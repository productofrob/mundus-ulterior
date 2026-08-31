"""Integrity checks for the Part 3 chunking pass.

Run before trusting anything downstream:

    python -m ingest.verify

These are the invariants Parts 4-8 depend on. If any fail, the cross-lingual
test and the citation trail are unsound regardless of how good the retrieval is.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from .loader import SEED_CORPUS_DIR, iter_seed_records, load_corpus
from .places import (
    PlaceError,
    assert_no_authored_coordinates,
    parse_record_places,
    read_no_places_reason,
)

# FINDING 10: this process's own stdout. On Windows `print` writes through a
# stream whose encoding comes from the console code page, and through a PIPE or
# a REDIRECT it falls back to the locale codec — cp1252, which cannot encode
# Greek, Tamil, Chinese, Ge'ez or runic. It does not degrade: it raises
# UnicodeEncodeError mid-output, with the file half written and every number in
# it correct. Found 2026-08-22 at build_ui_data.py:730, printing the Greek behind
# a `case_only` span into a redirect.
#
# Two neighbouring boundaries were already guarded and are NOT this one: a CHILD
# process's stdout (PYTHONIOENCODING in its env) and a PARENT decoding that child
# (subprocess encoding=). Both are about a pipe between two processes. This is
# about where THIS process is writing, and until 2026-08-22 nothing anywhere
# guarded it.
#
# errors="replace" is deliberate. A harness that cannot encode one character
# should print a replacement character and finish; it should never lose a run to
# a formatting problem. A mangled character is cosmetic. A three-day sweep that
# dies on day one is ninety chat calls.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

# Gate G1, criterion 1: 24/24 records carry at least a `regional` placement, and
# at least 17 carry a named place with a resolving pleiades_id. Held here as
# numbers rather than prose so the progress line below cannot drift from the
# gate it reports against.
G1_PLACED_TARGET = 24
G1_NAMED_TARGET = 17

EXPECTED_REGIONS = {
    "Arabia", "East Asia", "Persia", "Scandinavia",
    "South Asia", "Southeast Asia", "Sub-Saharan Africa",
}

MANIFEST_FLAGGED = {
    "palmyrene-tariff", "weilue", "hou-hanshu", "akananuru", "ezana-stone",
}


def run(corpus_dir: Path = SEED_CORPUS_DIR) -> int:
    result = load_corpus(corpus_dir)
    docs, chunks = result.documents, result.chunks
    failures: list[str] = []
    notes: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    # 1. Every chunk round-trips exactly to characters on disk. This is the
    #    load-bearing claim for citations in Part 7.
    raw_fields: dict[str, dict] = {}
    for path in iter_seed_records(corpus_dir):
        rec = json.loads(path.read_text(encoding="utf-8"))
        raw_fields[rec["id"]] = rec

    bad_offsets = []
    for c in chunks:
        source = str(raw_fields[c.doc_id].get(c.source_field, ""))
        if source[c.char_start:c.char_end] != c.text:
            bad_offsets.append(c.chunk_id)
    check(not bad_offsets, f"offsets do not round-trip for: {bad_offsets[:5]}")

    # 2. Provenance is never null.
    required = ("doc_id", "region", "citation", "lang", "source_field", "text_fidelity")
    missing = [
        f"{c.chunk_id}.{fname}"
        for c in chunks
        for fname in required
        if not getattr(c, fname)
    ]
    check(not missing, f"missing provenance: {missing[:5]}")

    # 3. All seven regions survived ingestion.
    regions = {c.region for c in chunks}
    check(
        regions == EXPECTED_REGIONS,
        f"region mismatch — missing {EXPECTED_REGIONS - regions}, extra {regions - EXPECTED_REGIONS}",
    )

    # 4. chunk_id uniqueness.
    dupes = [k for k, v in Counter(c.chunk_id for c in chunks).items() if v > 1]
    check(not dupes, f"duplicate chunk_ids: {dupes[:5]}")

    # 5. Original and translation are separate rows sharing a parallel_group —
    #    the precondition for the Part 5 same-query-two-languages test.
    groups: dict[str, set[str]] = defaultdict(set)
    for c in chunks:
        groups[c.parallel_group].add(c.role)
    paired = sum(1 for roles in groups.values() if roles == {"original", "translation"})
    # Find and coin records legitimately have no translation, so the expected
    # pair count is derived from the records that actually carry both fields.
    expect_pairs = sum(
        1 for rec in raw_fields.values()
        if str(rec.get("original_text_excerpt") or "").strip()
        and str(rec.get("reference_translation") or "").strip()
    )
    check(
        paired == expect_pairs,
        f"{paired} parallel original/translation pairs, expected {expect_pairs}",
    )

    # 6. No manifest-flagged record is ever presented as fully verbatim. It may
    #    be held back (pointer/paraphrase) or admitted as partial_verbatim where
    #    the original script is genuinely present — but never as clean source text.
    #     CORRECTED 2026-08-29, FINDING 31. This loop ran over MANIFEST_FLAGGED,
    #     a second copy of a list `ingest/fidelity.py` also holds, and the two
    #     drifted on 2026-08-22: FINDING 11 lifted the Weilue's flag there with
    #     a written reason and this file was not told. The check has been RED
    #     ever since -- through D4, Block E's four sessions and 396 runs, F0 and
    #     the sonnet arm -- and nothing noticed, because no state block lists
    #     `ingest.verify` among the suites while it is the FIRST line of the
    #     sub-tranche runbook F3 runs. F3 would have curated nine records and
    #     then met a red suite that had nothing to do with them: a true report
    #     inviting a false diagnosis, which BLOCK_D_START warns about by name.
    #
    #     MANIFEST_FLAGGED stays: it is this file's transcription of the
    #     manifest's prose, and transcribing prose by hand is fine. What is not
    #     fine is holding a second OPINION about what the code does with it, so
    #     the never-verbatim assertion now runs over fidelity's own hints and
    #     `check_paraphrase_flags` refuses a manifest flag that is neither
    #     honoured nor lifted.
    from .fidelity import (
        PARAPHRASE_FLAG_LIFTED,
        PARAPHRASE_ID_HINTS,
        check_paraphrase_flags,
    )

    for problem in check_paraphrase_flags(set(MANIFEST_FLAGGED)):
        failures.append(f"paraphrase flags: {problem}")

    for hint in PARAPHRASE_ID_HINTS:
        flagged = [
            c for c in chunks
            if hint in c.doc_id.lower() and c.role == "original"
        ]
        check(bool(flagged), f"manifest-flagged record '{hint}' not found in chunks")
        check(
            all(c.text_fidelity != "verbatim_original" for c in flagged),
            f"manifest-flagged record '{hint}' is labelled verbatim_original",
        )

    for hint, reason in sorted(PARAPHRASE_FLAG_LIFTED.items()):
        lifted = [
            c for c in chunks
            if hint in c.doc_id.lower() and c.role == "original"
        ]
        check(bool(lifted), f"lifted record '{hint}' not found in chunks")
        notes.append(f"paraphrase flag LIFTED on '{hint}': {reason}")

    # 6b. No editorial placeholder reaches the retrieval index. If one did, an
    #     answer in Part 7 could cite the corpus editor's own note as a source.
    from .fidelity import looks_like_placeholder, looks_like_pointer

    leaked = [
        c.chunk_id for c in chunks
        if c.eligible_for_retrieval
        and (looks_like_placeholder(c.text) or looks_like_pointer(c.text))
    ]
    check(not leaked, f"placeholder text is retrieval-eligible: {leaked[:5]}")
    check(
        all(not c.eligible_for_retrieval for c in chunks if c.text_fidelity == "pointer"),
        "a chunk labelled 'pointer' is retrieval-eligible",
    )

    # 7. No chunk exceeds the size budget.
    from .chunker import DEFAULT_MAX_CHARS
    oversize = [c.chunk_id for c in chunks if c.char_count > DEFAULT_MAX_CHARS]
    check(not oversize, f"chunks over {DEFAULT_MAX_CHARS} chars: {oversize[:5]}")

    # 8. Cross-lingual capability sanity: the retrieval-eligible pool must
    #    contain genuine non-English text, or Part 5 has nothing to test.
    eligible_non_en = [c for c in chunks if c.eligible_for_retrieval and c.lang != "en"]
    check(
        len(eligible_non_en) >= 5,
        f"only {len(eligible_non_en)} retrieval-eligible non-English chunks",
    )
    langs = Counter(c.lang for c in eligible_non_en)
    notes.append(f"retrieval-eligible non-English chunks by language: {dict(langs)}")

    # 9. Docs and chunks line up.
    # F3, 2026-08-31. 24 -> 25 with the FIRST record of Block F, and raised in
    # the same commit as the record that makes it true. F2 wrote the rule this
    # obeys: "it is correct today and F3 breaks it on purpose, in the same
    # commit as the records or not at all. Loosening it in advance is the floor
    # lowered to what is currently passing."
    check(len(docs) == 26, f"expected 26 documents, got {len(docs)}")
    orphans = {c.doc_id for c in chunks} - {d.doc_id for d in docs}
    check(not orphans, f"chunks reference unknown docs: {orphans}")

    # 10. A record whose `translation_source` says the English was SUMMARIZED,
    #     while its translation chunk is classified `translation`, is a
    #     divergence between what the record declares and what the classifier
    #     concluded. Same shape as Part 3's `lang` vs `declared_lang`: the
    #     divergence is the signal, and it is a signal for review rather than a
    #     verdict.
    #
    #     It is NOT a failure, because the 2026-08-10 audit showed no mechanical
    #     rule separates the good cases from the bad. Two candidates were tried
    #     and both fired on the wrong records: "a pointer's translation is
    #     suspect" would have flagged the Ezana titulature, which is genuine, and
    #     missed the object records entirely; "summary-declared means not a
    #     translation" flags the Vimose gloss, which is a published hedged
    #     reading and a required floor case. The audit had to be done by reading
    #     24 records, and this check exists so it does not have to be done again
    #     from scratch — only for records not yet triaged.
    reviewed = {
        "scandinavia-03-vimose": (
            "KEPT. A hedged scholarly gloss of six partly undeciphered runic "
            "sequences — 'likely', 'possibly', 'remain only partially "
            "deciphered' — from the Kiel Runenprojekt. Not a running "
            "translation, but published readings presented with their "
            "uncertainty intact, which is what an answer quoting them "
            "reproduces. Excluding it would remove the only Scandinavian "
            "textual evidence in the corpus."
        ),
    }
    translation_fidelity = {
        c.doc_id for c in chunks
        if c.role == "translation" and c.text_fidelity == "translation"
    }
    untriaged = []
    for doc in docs:
        source = (getattr(doc, "translation_source", None) or "").lower()
        if "summar" not in source:
            continue
        if doc.doc_id not in translation_fidelity:
            continue          # e.g. classified object_description — honest label
        if doc.doc_id in reviewed:
            continue
        untriaged.append(doc.doc_id)
    if untriaged:
        notes.append(
            "REVIEW: translation_source declares a summary while the chunk is "
            f"classified `translation`: {untriaged}. Read the field and decide "
            "whether it renders source wording or describes it. Editorial prose "
            "in a quotable field is citable as source evidence — that is how a "
            "modern historian's judgement nearly reached a reader as Palmyrene "
            "testimony."
        )

    # 11. Placements (Phase 2 W1). Two different things are checked here and
    #     they are deliberately not the same severity.
    #
    #     A malformed placement is a FAILURE, from the first record edited: it
    #     would put an unsourced point on a map, which is the one thing G1
    #     asserts cannot happen.
    #
    #     Incomplete *coverage* is a NOTE, because Block A spends three sessions
    #     getting from 0 to 24 and a suite that fails throughout is a suite that
    #     gets ignored throughout. The progress line names the gate it is
    #     heading for so it cannot be mistaken for a pass.
    placed = 0
    declared_unplaceable = 0
    named = 0
    contested = 0
    by_ground: Counter = Counter()
    place_ids: set[str] = set()

    for doc_id, rec in sorted(raw_fields.items()):
        try:
            assert_no_authored_coordinates(rec, doc_id)
            reason = read_no_places_reason(rec, doc_id)
            record_places = parse_record_places(rec, doc_id)
        except PlaceError as exc:
            failures.append(str(exc))
            continue
        if reason:
            declared_unplaceable += 1
        if not record_places:
            continue
        placed += 1
        by_ground.update(p.ground for p in record_places)
        contested += sum(1 for p in record_places if p.contested)
        if any(p.locatable for p in record_places):
            named += 1
        place_ids.update(p.cache_key for p in record_places if p.cache_key)

    notes.append(
        # F3, 2026-08-31. This read "25/24 considered" the moment the corpus
        # grew past G1's target, because a moving quantity was printed over a
        # closed gate's constant. At 60 records it would have read "60/24".
        # The denominator is now the corpus, and G1's target is stated beside
        # it as the met target it is. Same defect as the sentence that read
        # "nine archives, 396 runs" while the archives held 492: a constant
        # paired with something that moves.
        f"W1 placements: {placed} placed + {declared_unplaceable} declared "
        f"unplaceable = {placed + declared_unplaceable}/{len(docs)} "
        f"considered (G1's target was {G1_PLACED_TARGET}, met), "
        f"{named} with a named place (G1 wanted {G1_NAMED_TARGET}), "
        f"{len(place_ids)} distinct gazetteer ids, {contested} contested "
        f"(G1 criteria 1 and 3). Grounds: {dict(sorted(by_ground.items()))}. "
        f"Resolution is not checked here — run `python -m ingest.gazetteer --check`, "
        f"which is the only thing that turns an id into a coordinate."
    )

    # 12. Record tiers (F1, ruling 43). data/corpus_tiers.json DECLARES what
    #     each record is; ingest.fidelity.derive_record_tier READS what it is
    #     from the chunks; they have to agree. A tier that were only derived
    #     could never be wrong and could never be checked either.
    #
    #     The declaration is a sidecar and not a field on the record, and that
    #     is not tidiness. `canonical_record_text` hashes the whole parsed
    #     record with sorted keys, so a `tier` key would change every
    #     content_hash and therefore corpus_digest -- the denominator of all
    #     396 Block E runs and of the sonnet arm's 165. It is not under
    #     data/seed_corpus/ either, because `iter_seed_records` refuses a .json
    #     at that depth: glob('*/*.json') would not see it and rglob would, and
    #     a file some walks see and others do not is the exact failure that
    #     function exists to prevent.
    #
    #     A FAILURE and not a note, from the first record curated. Coverage
    #     checks are notes here (see 11) because a suite that fails throughout
    #     a three-session block gets ignored throughout. This is not coverage:
    #     an untiered or mis-tiered record is a record the target mix cannot
    #     count, and the mix is the thing F1 exists to make countable.
    from .fidelity import (
        GLOSS_CAPABLE_TIERS,
        RECORD_TIERS,
        check_allocation,
        check_delivery,
        check_declared_tiers,
        check_target_mix,
        derive_record_tier,
    )

    tiers_path = Path(__file__).resolve().parent.parent / "data" / "corpus_tiers.json"
    if not tiers_path.exists():
        failures.append(f"{tiers_path.name} is missing: no record tier is declared")
    else:
        tier_doc = json.loads(tiers_path.read_text(encoding="utf-8"))
        chunk_rows: dict[str, list] = defaultdict(list)
        for c in chunks:
            chunk_rows[c.doc_id].append(
                (c.role, c.text_fidelity, c.lang, c.eligible_for_retrieval)
            )
        derived = {
            d.doc_id: derive_record_tier(
                d.source_type,
                chunk_rows[d.doc_id],
                getattr(d, "translation_source", None),
            )
            for d in docs
        }
        for problem in check_declared_tiers(tier_doc.get("tiers") or {}, derived):
            failures.append(f"record tier: {problem}")
        for problem in check_target_mix(
            tier_doc.get("target_mix") or {}, tier_doc.get("measured_at_24") or {}
        ):
            failures.append(f"target mix: {problem}")
        # Ruling 51, F3. The mix at 60 says WHAT and the allocation says WHEN,
        # and until F3 only the first existed. This FAILS the suite rather than
        # noting it: unlike the tier histogram below, which is progress against
        # a target for the END of the block, the allocation is arithmetic that
        # is either right today or wrong today.
        mix_doc = tier_doc.get("target_mix") or {}
        for problem in check_allocation(
            mix_doc,
            mix_doc.get("records_by_region_at_24") or {},
            mix_doc.get("source_language_records_by_region_at_24") or {},
        ):
            failures.append(f"allocation: {problem}")

        counts = Counter(t for t, _reason in derived.values())
        mix = tier_doc.get("target_mix") or {}
        at60 = mix.get("by_tier_at_60") or {}
        notes.append(
            "record tiers: "
            + ", ".join(
                f"{tier} {counts.get(tier, 0)}/{at60.get(tier, '?')}"
                for tier in RECORD_TIERS
            )
            + f" (F1 target at {mix.get('total_at_60', '?')} records). "
            + "Progress, not a threshold: the mix is a target for the end of "
            + "Block F and a suite that failed on it throughout would be "
            + "ignored throughout."
        )

        source_language = Counter(
            d.region for d in docs
            if derived[d.doc_id][0]
            in ("verbatim_with_provenance", "verbatim_machine_english")
        )
        floor_per_region = mix.get("min_source_language_records_per_region", 0)
        short = {
            region: source_language.get(region, 0)
            for region in sorted(EXPECTED_REGIONS)
            if source_language.get(region, 0) < floor_per_region
        }
        notes.append(
            f"source-language records by region (F1 floor {floor_per_region} each "
            f"at 60): {dict(sorted(source_language.items()))}. Below the floor: "
            f"{short or 'none'}. An aggregate tier target met entirely inside two "
            f"regions leaves the other five exactly as unable to answer a "
            f"source-text question as they are now."
        )

        allocation = mix_doc.get("allocation") or {}
        tranches = allocation.get("sub_tranches") or []
        placed = sum(
            int(slot.get("n") or 0)
            for tranche in tranches for slot in (tranche.get("slots") or [])
        )
        notes.append(
            "allocation (ruling 51): "
            + ", ".join(
                f"{tranche.get('name')} "
                f"{sum(int(s.get('n') or 0) for s in (tranche.get('slots') or []))}"
                for tranche in tranches
            )
            + f" = {placed} record(s), every source-language record before "
            + "every catalogue record. The sub-tranche a record was curated in "
            + "is NOT a field on the record and is not derivable from one: "
            + "this line reports the PLAN, and data/curation_cost.json in "
            + "curation order reports what happened."
        )

    # 13. The curation-cost ledger (F2, rulings 46-48). data/curation_cost.json
    #     carries minutes per record PER PHASE from record 25, and the check
    #     that matters is COVERAGE, in both directions: every record in the
    #     corpus is either timed or excused with a written reason, and never
    #     both.
    #
    #     A FAILURE, and from the first record F3 curates. Nobody times a
    #     record twice: the minutes exist on the day the record is made and
    #     never again, so a record that reaches the corpus without a ledger row
    #     has to turn this suite red in the same run that first loads it. A
    #     coverage NOTE here would be a column that quietly ends up with 30
    #     rows for 36 records, and kill trigger 3 hangs off the mean.
    #
    #     The ledger is a sidecar for ruling 43's reason, which does not
    #     expire: a `minutes` key on a record would move corpus_digest, the
    #     denominator of 396 Block E runs and 165 arm runs. This is the second
    #     file that would have done it.
    from .cost import check_ledger

    cost_path = Path(__file__).resolve().parent.parent / "data" / "curation_cost.json"
    if not cost_path.exists():
        failures.append(
            f"{cost_path.name} is missing: no record's curation cost is recorded"
        )
    else:
        ledger = json.loads(cost_path.read_text(encoding="utf-8"))
        for problem in check_ledger(ledger, derived if tiers_path.exists() else {}):
            failures.append(f"curation cost: {problem}")

        # F3, 2026-08-31. check_allocation guards the PLAN; this guards
        # DELIVERY. The tranche's records are the ledger's `records` by
        # definition -- the seed 24 are its `not_timed` -- so the two files that
        # have to agree are the allocation and the column, and neither of them
        # is the record.
        regions_by_doc = {d.doc_id: d.region for d in docs}
        derived_tiers = derived if tiers_path.exists() else {}
        tranche_records = {
            entry.get("record_id"): (
                regions_by_doc.get(entry.get("record_id"), ""),
                (derived_tiers.get(entry.get("record_id")) or ("", ""))[0],
            )
            for entry in (ledger.get("records") or [])
        }
        mix_for_delivery = (tier_doc.get("target_mix") or {}) if tiers_path.exists() else {}
        for problem in check_delivery(
            mix_for_delivery, tranche_records,
            set(mix_for_delivery.get("gloss_capable_declared") or ()),
        ):
            failures.append(f"delivery: {problem}")

        allocation_cells: dict = {}
        for tranche in (mix_for_delivery.get("allocation") or {}).get("sub_tranches") or []:
            for slot in tranche.get("slots") or []:
                key = (str(slot.get("region")), str(slot.get("tier")))
                allocation_cells[key] = allocation_cells.get(key, 0) + int(slot.get("n") or 0)
        done_cells: dict = {}
        for region, tier in tranche_records.values():
            done_cells[(region, tier)] = done_cells.get((region, tier), 0) + 1
        gloss_declared = mix_for_delivery.get("gloss_capable_declared") or []
        gloss_capacity = sum(
            n - done_cells.get(k, 0) for k, n in allocation_cells.items()
            if k[1] in GLOSS_CAPABLE_TIERS)
        notes.append(
            f"delivery against the allocation: {len(tranche_records)} of "
            f"{sum(allocation_cells.values())} tranche record(s) curated. "
            f"Gloss-capable declared {len(gloss_declared)}/"
            f"{mix_for_delivery.get('gloss_capable_records', '?')}, with "
            f"{gloss_capacity} slot(s) left on a tier that can carry one. A "
            f"SHORTFALL is progress and is reported here; an UNREACHABLE quota "
            f"is a failure above, because a target the remaining slots cannot "
            f"carry has already been missed and nobody re-curates a record."
        )

        timed = len(ledger.get("records") or [])
        retired = len(ledger.get("retired") or [])
        notes.append(
            f"curation cost: {timed} record(s) timed, "
            f"{len(ledger.get('not_timed') or {})} excused"
            + (f", {retired} RETIRED (ruling 52: kept and named, counted in "
               f"no mean)" if retired else "")
            + ". "
            f"Comparator: {(ledger.get('comparator') or {}).get('evaluated_against', '?')} "
            f"(ruling 46 -- nothing records what record 12 cost). "
            f"Run `python -m ingest.cost_log report` for the per-tier table; "
            f"it is the only place a curation-cost number may be read from."
        )

    print(f"documents: {len(docs)}   chunks: {len(chunks)}   parallel pairs: {paired}")
    for n in notes:
        print(f"note: {n}")
    if result.warnings:
        print(f"loader warnings: {len(result.warnings)}")
        for w in result.warnings:
            print(f"  ! {w}")

    if failures:
        print(f"\nFAILED ({len(failures)})")
        for f in failures:
            print(f"  ✗ {f}")
        return 1

    print("\nAll integrity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
