"""C2a — a section is ONE retrievable record, canonically the original.

Block C ruling 8. The index holds each passage twice, as `::original::` and as
`::translation::`, and until now the two competed for the same six slots. On
2026-08-16 that cost two units at the gate: `muziris-cargo-periplus` was beaten
by the English of its own section, and `china-describes-rome-weilue` and
`-houhanshu` were beaten at ranks 1 and 2 by their own documents' translations.

What this module does NOT do, and the distinction is the whole reason it is
allowed to exist:

  * It does not change what the metric COUNTS. Ruling 7 refused that. After a
    collapse the top 6 literally CONTAINS the original chunk the pair names, so
    `rank` still means what it has meant since B2 — where this pair's chunk sat
    in what retrieval returned. Nothing is accepted that was not returned.
  * It does not touch the gaps. Ruling 4 reads `gapDoc`, the target against the
    best chunk in any OTHER document, and collapsing within a document cannot
    move it. Gaps stay computed on the uncollapsed hits, exactly as ruling 3
    keeps them pre-rerank. C2a is a recall intervention only.

Two costs travel with it, per ruling 8:

  * **"Top 6" becomes six RECORDS, not six chunks**, and therefore covers more
    underlying text than an uncollapsed six.
  * **Canonicalising to the original was chosen after seeing that it turns
    misses into hits.** The defence is not the score: a sourcebook about the
    world beyond Rome in its own sources presents the Greek, Chinese or Tamil
    record as the record, and the alternative — canonical = whichever member
    ranked higher — would make the citable text depend on retrieval noise.

Everything here is pure. The alignment itself comes from
`answer.align.pair_chunks` and is read from the database by the caller, so the
rule that decides whether a G2 number means anything is testable and mutatable
without a database.
"""

from __future__ import annotations


def section_maps(groups, primary_by_doc: dict | None = None
                 ) -> tuple[dict[str, str], dict[str, str]]:
    """[(canonical_chunk_id, [member_chunk_ids], ground)] -> two lookups.

    Returns `(section_of, canonical)`:
      section_of   chunk_id -> the section key it belongs to
      canonical    section key -> the chunk that REPRESENTS that section

    The section key is the canonical chunk's own id, so a section carries its
    own name and nothing has to invent one.

    **Only `ground == "section"` builds a section.** Positional (`index`)
    alignment pairs two texts by coincidence of counting, and collapsing on it
    would merge a passage with a NEIGHBOURING section's translation — silently
    removing a genuinely different passage from the ranking. That is the same
    line ruling 2 drew for the same reason, and it is drawn here again rather
    than inherited by assumption.
    """
    section_of: dict[str, str] = {}
    canonical: dict[str, str] = {}
    for canon, members, ground in groups:
        if ground not in COLLAPSIBLE_GROUNDS:
            continue
        # Ruling 11: the row is the record's PRIMARY text, not always the
        # original. The section KEY stays the original's id so a section keeps a
        # stable name across runs whichever way this falls; only the chunk
        # emitted changes. A primary-is-translation section with more than one
        # member falls back to the original rather than guessing which member,
        # because "which of three" is a question this rule does not answer.
        doc = canon.split("::")[0]
        wants = (primary_by_doc or {}).get(doc, "original")
        canonical[canon] = (members[0] if (wants == "translation"
                                           and len(members) == 1) else canon)
        section_of[canon] = canon
        for member in members:
            if member == canon:
                continue
            section_of[member] = canon
    return section_of, canonical


def primary_role(source_type: str) -> str:
    """Which of a record's two texts IS the record. Ruling 11.

    Imported from `ingest.fidelity`, never redefined: `FIND_TYPES` has carried
    the distinction since Part 3 — "source types where the record describes an
    object rather than carrying text" — and `classify_translation` already says
    that for a find record the translation field "is a curatorial description,
    not a translation". Two definitions of one idea agree until they do not.

    literary_text, inscription -> "original"     the source text IS the record
    find_record, coin_record   -> "translation"  the object is the record, and
                                                 both text fields are curatorial
    """
    from ingest.fidelity import FIND_TYPES

    return "translation" if source_type in FIND_TYPES else "original"


SOLE = "sole"
COLLAPSIBLE_GROUNDS = frozenset({"section", SOLE})


def promote_sole(groups) -> list:
    """Relabel the unambiguous 1:1 case from `index` to `sole`. Ruling 9.

    `index` at n=1 is a mislabelled ground. The reason to distrust `index` —
    two texts numbered independently pair by coincidence of counting — is
    VACUOUS when the count is one: there is no neighbouring section to confuse
    and exactly one possible pairing. Twelve of this corpus's fifteen
    translated documents are that case.

    Qualifying is deliberately strict and computed from the groups alone: the
    document contributes exactly ONE group, that group has exactly ONE member,
    and its ground is `index`. A document with two `index` groups is the
    coincidence-of-counting case the ruling still refuses.

    Done HERE and not in `answer.align`, so ruling 2's alternates and the answer
    path are provably untouched: they test for `section` and will never see this
    name.
    """
    per_doc: dict[str, int] = {}
    for canon, _members, _ground in groups:
        per_doc[canon.split("::")[0]] = per_doc.get(canon.split("::")[0], 0) + 1
    out = []
    for canon, members, ground in groups:
        if (ground == "index" and len(members) == 1
                and per_doc[canon.split("::")[0]] == 1):
            ground = SOLE
        out.append((canon, members, ground))
    return out


def collapse(hits, section_of: dict[str, str], canonical: dict[str, str]) -> list:
    """The ranked list with each section appearing once, as its original.

    Order-preserving: a section takes the position of its BEST-RANKED member,
    which is what makes this a change to presentation rather than to ranking. A
    translation at rank 1 whose original sat at rank 7 yields the ORIGINAL at
    rank 1 — the record was found first, and the record is the original.

    A chunk belonging to no section passes through untouched, so a document
    whose alignment ground was not `section` is unaffected. The result is never
    longer than the input and never contains a chunk the search did not return:
    if a section's canonical chunk is somehow absent from `hits`, the
    first-ranked member is emitted in its place rather than a chunk nobody
    ranked.
    """
    by_id = {h.chunk_id: h for h in hits}
    out, seen = [], set()
    for hit in hits:
        key = section_of.get(hit.chunk_id)
        if key is None:
            out.append(hit)
            continue
        if key in seen:
            continue
        seen.add(key)
        canon_id = canonical.get(key, hit.chunk_id)
        out.append(by_id.get(canon_id, hit))
    return out


def entry_roles(hits, section_of: dict[str, str]) -> dict[str, str]:
    """section key -> the ROLE of the member that got there first.

    The honesty instrument for ruling 8, and it is not optional. A collapse
    emits the ORIGINAL at the position its best-ranked member reached — so when
    that member was the translation, the run reports the original as found on
    the strength of its English. That is correct behaviour for a product whose
    result is a record, and it is NOT evidence that the non-English text is
    reachable.

    The case that proves it matters: `muziris-cargo-akananuru`, the corpus's one
    genuinely broken cross-lingual link, sits at rank 309 while the English of
    the same poem ranks near the top. Collapsing would report it as found.
    Ruling 1 requires that failure printed beside any G2 number; without this
    map, the collapse would quietly erase it.
    """
    entry: dict[str, str] = {}
    for hit in hits:
        key = section_of.get(hit.chunk_id)
        if key is None or key in entry:
            continue
        entry[key] = hit.role
    return entry


def collapse_report(hits, collapsed) -> dict:
    """What the collapse actually did, for the archived run.

    A step that silently changes a candidate list is the defect this repository
    has paid for twice — a view counted in one place and ranked in another, and
    a canary described as invisible while it competed. So the numbers are
    recorded rather than described.
    """
    kept = {h.chunk_id for h in collapsed}
    return {
        "in": len(hits),
        "out": len(collapsed),
        "removed": len(hits) - len(collapsed),
        "promoted": sum(1 for a, b in zip(hits, collapsed) if a.chunk_id != b.chunk_id),
        "roles_removed": sorted({h.role for h in hits if h.chunk_id not in kept}),
    }
