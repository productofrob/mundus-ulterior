"""Part 9: bundle the archived answer runs and the seed corpus into `ui/data.js`.

Why this script exists at all
----------------------------
An archived run in `eval/answer_runs/` records that a quotation lives at
`reference_translation[7:48]` of `scandinavia-03-vimose`. It does **not** record
what those characters are. The payload carries `english.text` — the passage the
model was shown — but a quote span is an offset into the *seed field*, and for a
non-English passage those are different strings entirely.

So a UI built from the payloads alone can print the numbers `[7:48]` and cannot
show what sits there. That is the difference between claiming provenance and
demonstrating it, and demonstrating it is the whole point of Part 9. This script
does the join: runs on one side, `data/seed_corpus/**/*.json` on the other,
matched on `doc_id` and `source_field`.

Why a `.js` file and not `.json`
--------------------------------
`ui/index.html` is meant to open by double-clicking it. Browsers refuse
`fetch("data.json")` from a `file://` page — it is a cross-origin request to a
null origin, and no header can be set on a local file to permit it. A `<script
src="data.js">` tag has no such restriction. The cost is one assignment line;
the benefit is that the UI needs no server, which matters because the point of
this part is that somebody can look at the thing.

Usage
-----
    python ui/build_ui_data.py
    python ui/build_ui_data.py --verify     # check spans, write nothing

A6 — the build's own placement audit
-------------------------------------
`build_places` calls `verify_placement_shape` on every load, in both modes
above. This is deliberately redundant with `ingest/places.py`'s own load-time
guards (an authored coordinate, an `identified` placement with no citation) and
with `ingest/gazetteer.py --check`'s cache lookup (a `pleiades_id` that never
resolves, surfaced here as `uncached`): PHASE2_PLAN A6 asks for the build to
refuse these on its own account, not merely inherit a refusal from a tool a
curator might not have run before bundling. See `check_placement_shape` and
`scripts/mutate_ui_places.py`, which mutation-verifies all three.
"""

from __future__ import annotations

import argparse
from collections import Counter
import datetime as _dt
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO / "eval" / "answer_runs"
CORPUS_DIR = REPO / "data" / "seed_corpus"
GOLD_DIR = REPO / "eval" / "gold"
GAZETTEER_PATH = REPO / "data" / "gazetteer.json"
OUT = Path(__file__).resolve().parent / "data.js"

# `ingest` is a sibling package, not a subpackage of `ui`. This script is run
# as `python ui/build_ui_data.py`, not `python -m ui.build_ui_data`, so the
# repo root is not on `sys.path` by default — the same fix already applied in
# `scripts/write_a4_places.py`.
sys.path.insert(0, str(REPO))
from ingest.places import (            # noqa: E402
    Place, SUBJECT_BLOCK, load_places, read_no_places_reason,
)
from ingest.loader import (                   # noqa: E402
    iter_seed_records, seed_record_hashes, corpus_digest,
    CORPUS_DIGEST_ALGORITHM,
)
from ingest import gazetteer as gz     # noqa: E402

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

# The seed fields a chunk can be cut from. `source_field` in a run payload
# names one of these; anything else is a shape we have not seen and should be
# reported rather than silently dropped.
TEXT_FIELDS = ("original_text_excerpt", "reference_translation")

# Carried into the UI so a source card can show what the record claims about
# itself without the UI hardcoding the seed schema.
META_FIELDS = (
    "id", "region", "title", "source_type", "language_code", "language_note",
    "date", "findspot", "citation", "citation_original_language",
    "translation_source", "original_text_note", "reference_translation_note",
    "notes",
)


def load_corpus() -> dict[str, dict]:
    """Read every seed record, keyed by document id.

    The document id in a run payload (`doc_id`) is the seed record's `id`, not
    its filename, so the mapping has to be built by reading the files rather
    than by guessing paths.
    """
    corpus: dict[str, dict] = {}
    # Was `CORPUS_DIR.rglob("*.json")`, the one walk in the tree that disagreed
    # with the other four - and with build_places() forty lines below it. See
    # ingest.loader.iter_seed_records for why that mattered to D1.
    for path in iter_seed_records(CORPUS_DIR):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  skipped unreadable seed record {path.name}: {exc}",
                  file=sys.stderr)
            continue
        doc_id = record.get("id")
        if not doc_id:
            print(f"  seed record without an id: {path.name}", file=sys.stderr)
            continue

        entry = {k: record.get(k) for k in META_FIELDS if record.get(k) is not None}
        entry["file"] = str(path.relative_to(REPO)).replace("\\", "/")
        entry["fields"] = {
            field: record[field]
            for field in TEXT_FIELDS
            if isinstance(record.get(field), str)
        }
        corpus[doc_id] = entry
    return corpus


def load_runs() -> list[dict]:
    """Read every archived run.

    Two payload shapes exist on disk and both are kept. The `-recovered` files
    were reconstructed in Part 8 and carry a thinner passage record — no `lang`,
    `region` or `citation`. Normalising them into the richer shape by inventing
    those fields would put fabricated provenance into a provenance viewer, so
    they are marked instead and the UI renders what is actually there.
    """
    runs: list[dict] = []
    for path in sorted(RUNS_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        # `--repeat N --json` writes a list; single runs write an object.
        items = payload if isinstance(payload, list) else [payload]
        for index, item in enumerate(items):
            item["file"] = path.name
            item["run_key"] = f"{path.stem}#{index}" if len(items) > 1 else path.stem
            passages = item.get("passages") or []
            item["partial_passages"] = bool(passages) and "lang" not in passages[0]
            runs.append(item)
    return runs


def _resolved_geometry(
    entry: gz.Entry, ranges: dict[str, dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Everything the page needs to draw or attribute one cached gazetteer entry.

    Deliberately a superset of what any one view uses today — `location_precision`
    is not read yet by any map marker, but PHASE2_PLAN A5 says the page needs it
    alongside `ground` to render honestly (they are different axes: `ground` is
    how WE arrived at a placement, `location_precision` is how well PLEIADES
    knows the point), and re-deriving it from `data/gazetteer.json` a second time
    later is the `translation_chunk`/`translation_chunk_id` mistake again — the
    two names that meant the merged section and the retrieved member, renamed at
    C1b (2026-08-14) to `translation_section` and `translation_member_chunk_id`.

    A6 left `date_verdict` out and PROGRESS.md recorded the consequence: the
    `hole` and `unknown` verdicts were computed and reported by
    `ingest.gazetteer --check` and never reached the bundle, so **the page could
    not show that a point's dates do not corroborate the record citing it**. On
    screen a marker whose gazetteer entry attests nothing in this era looked
    exactly like one that attests the right century.

    Computed here from `gz.date_audit` rather than re-implemented, for the same
    reason the geometry above is copied rather than re-derived: two
    implementations of one rule is the defect this file keeps paying for. When
    `ranges` is absent the verdict is `None` — honestly "not checked", never a
    silent `ok`.
    """
    verdict, detail = (gz.date_audit(entry, ranges) if ranges is not None
                       else (None, None))
    return {
        "date_verdict": verdict,
        "date_detail": detail,
        "title": entry.title,
        "point": entry.repr_point,          # [lon, lat] or None
        "bbox": entry.bbox,                 # [min_lon, min_lat, max_lon, max_lat] or None
        "has_point": entry.has_point,
        "has_extent": entry.has_extent,
        "has_area": entry.has_area,
        "location_precision": entry.location_precision,
        "min_date": entry.min_date,
        "max_date": entry.max_date,
        "time_period_keys": entry.time_period_keys,
        "dump_date": entry.dump_date,
        "authors": entry.authors,
        "creators": entry.creators,
    }


def _place_geometry(
    p: Place, known: dict[str, gz.Entry],
    ranges: dict[str, dict[str, Any]] | None = None,
) -> tuple[str, dict[str, Any] | None, str | None]:
    """Classify one placement as `pin`, `extent` or `gap` — never a fourth thing.

    A `stated` or `identified` ground names a specific place, so it renders as a
    PIN at the gazetteer's cached representative point. `identified` with
    `contested: true` still returns `"pin"` here — Pleiades has a coordinate for
    it — but carries `p.contested`, which the page reads to draw it as disputed
    rather than settled. "Renders as contested, not as a pin" (PHASE2_PLAN A5)
    is a statement about the marker's *style*, not about whether it has a
    position.

    A `regional` ground renders as an EXTENT only when its cached bbox has real
    area (`has_area`). It never falls back to a representative point — that
    fallback is the one thing this whole `ground` vocabulary exists to prevent
    (see A5's Egypt decision in PROGRESS.md).

    Everything else is a GAP, with a reason a person can read: no id was ever
    findable (most `regional` placements), or an id resolves and is cached but
    has no drawable geometry for its ground (`pleiades:766` Aegyptus — a real
    id, cached, `has_area` false), or — should `ingest.gazetteer --check` not
    have been run since the corpus changed — an id this join cannot find in the
    cache at all. A gap is reported, never silently dropped: for two of the
    seven literary records (the Weilüe, the Hou Hanshu) *every single place* is
    a gap, and a renderer that only draws pins and extents would delete Rome's
    only two Chinese sources from the page without printing a word about it.
    """
    if not p.locatable:
        return "gap", None, (
            f"no gazetteer entry at all — "
            f"{p.note or 'the region is known and no more'}"
        )

    entry = known.get(p.cache_key or "")

    # A6: the gazetteer HOLDS this place and records no location for it. A
    # different state from the one above, and the page must not render them
    # with the same sentence: Ariake is a place no gazetteer has heard of,
    # while Kyeneion is a Pleiades entry with an id, a title, a date range and
    # no coordinate. Both draw nothing; only one of them is a gap in the
    # gazetteer's coverage rather than in its geometry.
    #
    # `resolved` is returned even though nothing can be drawn from it: the
    # entry has a title, a date range and provenance, all of which the record
    # panel should show. Returning None here would also have made this look
    # like an uncached id to `build_places`, which is a different failure.
    if p.unlocated and entry is not None:
        return "gap", _resolved_geometry(entry, ranges), (
            f"'{p.cache_key}' is in the gazetteer and the gazetteer does not "
            f"record where it is — it is catalogued as {entry.title!r} with no "
            f"coordinate. Not an absent entry: the place is known, its "
            f"location is not."
        )
    if entry is None:
        return "gap", None, (
            f"'{p.cache_key}' has not been looked up (run "
            f"`python -m ingest.gazetteer --refresh`) — this should not happen "
            f"once `--check` passes; treat it as a build defect, not a real gap"
        )

    resolved = _resolved_geometry(entry, ranges)

    if p.ground == "regional":
        if entry.has_area:
            return "extent", resolved, None
        return "gap", resolved, (
            f"'{p.cache_key}' ({entry.title}) resolves and is cached, but its "
            f"bbox has no area — a regional placement never falls back to a "
            f"representative point, so nothing here can be drawn"
        )

    if entry.has_point:
        return "pin", resolved, None
    return "gap", resolved, (
        f"'{p.cache_key}' ({entry.title}) is cached but carries no "
        f"representative point, only an extent — '{p.ground}' names a "
        f"specific place and requires a point"
    )


def check_placement_shape(p: Place) -> str | None:
    """One placement against the two G1-criterion-2 shape rules, re-checked.

    `ingest/places.py::parse_place` already refuses both of these at load
    time, so nothing in today's corpus can trigger this — the same relation
    `verify_spans` has to `cite.py`'s own span-matching. The point of asking
    again here, on the `Place` objects `load_places` already returned, is
    PHASE2_PLAN A6: a rule enforced in exactly one place is a rule one edit
    away from being silently weakened, and `scripts/mutate_places.py` proves
    `parse_place` refuses each of these — not that the BUILD does. Without
    this, disabling the ingest-side guard alone would be enough to ship an
    authored point; with it, the ingest guard and this one must both fail.
    """
    if p.ground != "regional" and p.gazetteer_id is None:
        return (
            f"{p.key}: ground '{p.ground}' names a specific place but carries "
            f"no gazetteer_id — an authored coordinate. ingest/places.py "
            f"should already refuse this at load time; if you are seeing it "
            f"here, that guard has been weakened."
        )
    if p.ground == "identified" and p.ground_citation is None:
        return (
            f"{p.key}: ground 'identified' with no ground_citation — an "
            f"identification with nobody identifying it. ingest/places.py "
            f"should already refuse this at load time; if you are seeing it "
            f"here, that guard has been weakened."
        )
    return None


def verify_placement_shape(by_doc: dict[str, list[Place]]) -> list[str]:
    """Every placement in the corpus, against `check_placement_shape`."""
    return [
        problem
        for places in by_doc.values()
        for p in places
        if (problem := check_placement_shape(p)) is not None
    ]


def build_places(corpus_dir: Path, gazetteer_path: Path) -> dict[str, Any]:
    """Join `ingest/places.py` and `ingest/gazetteer.py` into what A5 draws.

    Three things fall out of one pass over the corpus, because they were built
    in that order and each depends on the one before:

    - `docs`      — every placement, classified pin/extent/gap (see
                    `_place_geometry`), keyed by the document that carries it.
    - `groups`    — the same placements re-keyed by cached gazetteer id, so
                    that four records naming the same coordinate (Muziris,
                    claimed `stated` three times and `identified` + contested
                    once) become one map marker carrying four references,
                    rather than three confident pins and a contested one
                    stacked on the same point.
    - `edges`     — `subject_places` blocks only, derived exactly as
                    `PLACES.md` specifies: `source -> focus`, `focus ->
                    destination`, `waypoint -> focus` with no ordering claimed
                    among waypoints (the vocabulary's known limit). An edge is
                    `drawable` only when BOTH ends resolved to a pin or an
                    extent; otherwise it is reported with the reason, never
                    dropped — this is where Ariake (source for Muziris, no id
                    at all) and Sabbatha (source for Cana, resolves and is
                    UNLOCATED) show up.

    Records with neither a place block nor `no_places_reason` (still open —
    the GeoNames backlog PROGRESS.md tracks) and records that declared
    themselves unplaceable are both counted and named, so "not on the map" is
    never confused with "not yet considered".
    """
    by_doc = load_places(corpus_dir)
    cache = gz.load_cache(gazetteer_path)
    known = gz.entries(cache)
    # The same ranges `--check` audits against, read from the same cache, so
    # the page and the checker cannot disagree about what is in era.
    ranges = gz.period_ranges_from_cache(cache)

    docs: dict[str, list[dict[str, Any]]] = {}
    edges: list[dict[str, Any]] = []
    groups: dict[str, dict[str, Any]] = {}
    uncached: list[str] = []
    unconsidered: list[str] = []
    declared_unplaceable: dict[str, str] = {}
    counts = {"pin": 0, "extent": 0, "gap": 0}

    for path in iter_seed_records(corpus_dir):
        record = json.loads(path.read_text(encoding="utf-8"))
        doc_id = record["id"]
        reason = read_no_places_reason(record, doc_id)
        places = by_doc.get(doc_id, [])

        if reason:
            declared_unplaceable[doc_id] = reason
            continue
        if not places:
            unconsidered.append(doc_id)
            continue

        entries_out: list[dict[str, Any]] = []
        for p in places:
            kind, resolved, gap_reason = _place_geometry(p, known, ranges)
            counts[kind] += 1
            if gap_reason and kind == "gap" and resolved is None and p.cache_key and p.locatable:
                uncached.append(p.cache_key)

            entries_out.append({
                "key": p.key, "doc_id": doc_id, "block": p.block, "index": p.index,
                "name": p.name, "ground": p.ground, "role": p.role,
                "gazetteer": p.gazetteer, "gazetteer_id": p.gazetteer_id,
                "cache_key": p.cache_key, "uri": p.uri,
                "ground_citation": p.ground_citation,
                "contested": p.contested,
                "contested_citations": list(p.contested_citations),
                "note": p.note, "draws_edge": p.draws_edge,
                "kind": kind, "resolved": resolved, "gap_reason": gap_reason,
            })

            if kind in ("pin", "extent") and p.cache_key:
                group = groups.setdefault(p.cache_key, {
                    "cache_key": p.cache_key, "kind": kind,
                    "resolved": resolved, "members": [],
                })
                group["members"].append({
                    "doc_id": doc_id, "key": p.key, "block": p.block,
                    "name": p.name, "ground": p.ground, "role": p.role,
                    "contested": p.contested,
                })

        docs[doc_id] = entries_out

        subject = [p for p in places if p.block == SUBJECT_BLOCK]
        focus = next((p for p in subject if p.role == "focus"), None)
        for p in subject:
            if not p.draws_edge:
                continue
            # source/waypoint reach the focus FROM p; destination leaves the
            # focus FOR p. Waypoints are drawn like sources (a line to the
            # focus) but the page must not draw an arrowhead that implies an
            # order PLACES.md says is not recoverable.
            a, b = (p, focus) if p.role in ("source", "waypoint") else (focus, p)
            a_kind, _, a_gap = _place_geometry(a, known)
            b_kind, _, b_gap = _place_geometry(b, known)
            drawable = a_kind in ("pin", "extent") and b_kind in ("pin", "extent")
            reasons = []
            if a_kind == "gap":
                reasons.append(f"{a.name}: {a_gap}")
            if b_kind == "gap" and b is not a:
                reasons.append(f"{b.name}: {b_gap}")
            edges.append({
                "doc_id": doc_id, "role": p.role,
                "from_key": a.key, "to_key": b.key,
                "from_name": a.name, "to_name": b.name,
                "drawable": drawable,
                "gap_reason": "; ".join(reasons) or None,
            })

    return {
        "docs": docs,
        "edges": edges,
        "groups": sorted(groups.values(), key=lambda g: g["cache_key"]),
        "unconsidered": unconsidered,
        "declared_unplaceable": declared_unplaceable,
        "uncached": sorted(set(uncached)),
        # A6: the build-layer re-check of G1 criterion 2, independent of
        # ingest/places.py's own load-time guards. See `verify_placement_shape`.
        "shape_problems": verify_placement_shape(by_doc),
        "stats": {
            "pins": counts["pin"], "extents": counts["extent"], "gaps": counts["gap"],
            "documents_placed": len(docs),
            "documents_unconsidered": len(unconsidered),
            "documents_declared_unplaceable": len(declared_unplaceable),
            "edges_total": len(edges),
            "edges_drawable": sum(1 for e in edges if e["drawable"]),
        },
    }


def load_coastline(data_dir: Path) -> dict[str, Any] | None:
    """The dated Natural Earth snapshot the map draws as its backdrop.

    Generated by `scripts/build_coastline.py`; see that file for why a basemap
    is sourced rather than omitted, and why omitting it was a mistake.

    Missing is a NOTE, not a build failure, and the difference is deliberate.
    An absent coastline costs legibility — the map still draws every point,
    extent and edge it would otherwise, and every one of them still traces to a
    cached gazetteer id. An absent *placement* would be a false claim about the
    corpus, which is why `build_places` exits non-zero on an uncached id and
    this does not. Different severities for different kinds of wrong.

    The newest dated file wins, and the date is read from the filename for the
    same reason `gazetteer.dump_date_from_name` refuses a file called
    'latest': a snapshot that cannot say when it was taken cannot say what it
    is comparable with.
    """
    candidates = sorted(data_dir.glob("coastline-ne110m-*.json"))
    if not candidates:
        return None
    path = candidates[-1]
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["file"] = str(path.relative_to(REPO)).replace("\\", "/")
    return payload


def _same_characters(found: str, quote: str) -> bool:
    """Is `found` the same run of characters the model quoted?

    Containment in either direction, not equality: `cite.py` trims edge
    punctuation before recording a span, so a quotation ending in a comma the
    source does not have is a quoting convention, not a corruption.
    """
    return bool(found) and (found in quote or quote in found)


def classify_span(span: dict, corpus: dict[str, dict]) -> dict:
    """Decide what a claimed character span actually holds, today.

    Until now this assertion has only been checked at answer time, against the
    live database that produced the answer. Checking it here — archive against
    seed files — asks a different and more useful question: *does the claim
    still hold?* The Part 8 corpus edits happened after most of these runs were
    archived, so some of these offsets now point at text that has moved.

    Five outcomes, and the distinction between the middle three is the reason
    this function exists rather than a boolean:

    - `resolved`     — the characters at the offset are the quoted characters.
    - `case_folded`  — they differ only in letter case, **and the span says so**:
      `cite.py` recorded `match="case_folded"`. The span is right and its label
      is right. Not a defect, and reported separately from one.
    - `case_only`    — they differ only in letter case and the span claims
      `match="exact"`, so the payload overstates what it found. The span is
      right; the label is not. Worth showing rather than smoothing over, because
      a viewer that prints "exact" beside two visibly different strings
      discredits itself. **Every archived run made before C1a (2026-08-14) lands
      here by construction** — they were produced by the labeller that had only
      two states. They are not re-labelled retroactively: the archive records
      what was claimed at the time, and rewriting it would destroy the only
      evidence that the defect existed.
    - `article_added` — they are the quoted characters with an article the
      writer added at the front removed, and the span says so: `cite.py`
      recorded `match="article_added"`. Ruling 40, 2026-08-28. The span is
      right and its label is right, exactly as for `case_folded`; the
      quotation as rendered is one word longer than the record. A span in
      this shape whose label says otherwise is reported here with the label it
      actually carries, on the `case_only` precedent — the archive records what
      was claimed at the time and is never re-labelled retroactively.
    - `moved`        — the quote is still in the field, at a different offset.
      The record was edited after this answer was archived. **This is the failure
      a naive viewer would render silently and convincingly**, showing whatever
      now sits at those coordinates as though the answer had quoted it.
    - `absent`       — the quote is not in the field at all.
    """
    start, end = span.get("abs_start"), span.get("abs_end")
    quote = (span.get("quote") or "").strip()
    doc = corpus.get(span.get("doc_id"))
    field = span.get("source_field")
    recorded = span.get("match")

    if doc is None:
        return {"state": "absent", "why": "no seed record with this doc_id"}
    text = doc["fields"].get(field)
    if text is None:
        return {"state": "absent", "why": f"seed record has no field {field!r}"}

    found = text[start:end]
    if _same_characters(found, quote):
        return {"state": "resolved", "found": found}

    # Ruling 40, and CORRECTED the same day. This must sit ABOVE the
    # case-folding branch, not below it: `_same_characters` tests containment
    # in EITHER direction, so `Half-length bust…` is "the same characters" as
    # `a half-length bust…` and an article span placed after that branch is
    # reported as a case labelling defect. It was, on the first run.
    #
    # What the ruling document first said about this — that such a span landed
    # in `absent` — was wrong, and is corrected there. Containment made it
    # `case_only`. `absent` is what it would have been under equality, which is
    # the more obvious reading of this function and not the one it implements.
    #
    # The test is precise rather than "does stripping help": the QUOTE has a
    # leading article and what is on disk does NOT, so the writer added one.
    # A pair that both carry `The` differs only in case and must keep falling
    # through to the branch below.
    from answer.cite import strip_added_article
    unarticled = strip_added_article(quote)
    if (unarticled != quote
            and strip_added_article(found) == found
            and _same_characters(found.casefold(), unarticled.casefold())):
        agrees = recorded == "article_added"
        return {"state": "article_added", "found": found,
                "why": ("differs from the quotation by an article the writer "
                        "added at the front, and the span records "
                        "match='article_added' — the offset is right and so is "
                        "its label")
                       if agrees else
                       (f"differs from the quotation by an article the writer "
                        f"added at the front; cite.py matched it but recorded "
                        f"match={recorded!r}"),
                "label_agrees": agrees}

    if _same_characters(found.casefold(), quote.casefold()):
        if recorded == "case_folded":
            return {"state": "case_folded", "found": found,
                    "why": "differs from the quotation only in letter case, and "
                           "the span records match='case_folded' — the offset is "
                           "right and so is its label"}
        return {"state": "case_only", "found": found,
                "why": f"differs from the quotation only in letter case; "
                       f"cite.py matched case-insensitively but recorded "
                       f"match={recorded!r}"}

    at = text.find(quote)
    if at < 0 and quote:
        at = text.casefold().find(quote.casefold())
    if at >= 0:
        return {"state": "moved", "found": found, "now_at": [at, at + len(quote)],
                "why": "the seed record was edited after this run was archived; "
                       "the quotation is still in the field, at a different offset"}
    return {"state": "absent", "found": found,
            "why": "the quotation is not in this field of the seed record as it "
                   "stands today"}


# D1. THREE states, and the third is the point. `moved` and `absent` say a
# claim no longer holds; these say whether the corpus it was made against has
# moved underneath it. They are different axes and are kept as different axes -
# `classify_span`'s five states are not touched, exactly as `rank_reranked`
# never overwrote `rank`.
PROVENANCE_STATES = ("unchanged", "changed", "unrecorded", "not_in_version")


def corpus_provenance(run: dict, span: dict, today: dict[str, str]) -> dict:
    """Was the record this span quotes the same record it is being checked against?

    | recorded and EQUAL to today's | the record did not move - an `absent` or
    |                               | `moved` span is a real defect in the span
    | recorded and DIFFERENT        | the record moved - the span is explained
    | NOT recorded                  | UNKNOWN, and reported on its own line

    Every archive written before D1 is in the third bucket by construction, and
    it must never be silently counted as either of the first two. Collapsing
    "unknown" into "unchanged" would report a span as a real defect on no
    evidence; collapsing it into "changed" would explain away every real defect
    the archive holds. This file already sets that precedent for the pre-C1a
    runs in `classify_span`, and for the same reason.
    """
    version = run.get("corpus_version")
    doc_id = span.get("doc_id")
    if not version:
        return {"state": "unrecorded",
                "why": "this run was archived before the corpus version was "
                       "recorded; whether the record has moved since is not "
                       "knowable from the archive, and is not assumed either way"}
    algorithm = version.get("algorithm")
    if algorithm != CORPUS_DIGEST_ALGORITHM:
        return {"state": "unrecorded",
                "why": f"recorded under {algorithm!r}, and this build hashes "
                       f"records as {CORPUS_DIGEST_ALGORITHM!r}. Two hashes of "
                       f"different things cannot be compared, and a mismatch "
                       f"between them would say nothing about the corpus"}
    recorded = (version.get("record_hashes") or {}).get(doc_id)
    if recorded is None:
        return {"state": "not_in_version",
                "why": f"the run recorded a corpus version, but {doc_id!r} is "
                       f"not in it - the answer cited a document the corpus "
                       f"version does not cover"}
    now = today.get(doc_id)
    if now is None:
        return {"state": "changed", "recorded": recorded, "now": None,
                "why": f"{doc_id!r} carried a hash when this run was made and "
                       f"is not a seed record today"}
    if recorded == now:
        return {"state": "unchanged", "recorded": recorded, "now": now,
                "why": "the seed record is byte-for-byte the one that made this "
                       "answer, so a failing span here is a defect in the span"}
    return {"state": "changed", "recorded": recorded, "now": now,
            "why": "the seed record was edited after this run was archived - "
                   "measured, not inferred"}


def verify_spans(runs: list[dict], corpus: dict[str, dict]) -> dict[str, list]:
    """Classify every claimed span, annotating the runs in place.

    The classification is written back onto each span as `resolution`, so the UI
    never has to re-derive it and can never disagree with this script about what
    a span holds.
    """
    buckets: dict[str, list] = {"resolved": [], "case_folded": [],
                                "article_added": [], "case_only": [],
                                "moved": [], "absent": []}
    today_hashes = seed_record_hashes(CORPUS_DIR)
    for run in runs:
        for span in run.get("grounding", {}).get("quote_spans", []):
            if span.get("abs_start") is None or span.get("abs_end") is None:
                continue                      # no span was claimed; not a defect
            resolution = classify_span(span, corpus)
            resolution["provenance"] = corpus_provenance(run, span, today_hashes)
            span["resolution"] = resolution
            buckets[resolution["state"]].append({
                "run": run["run_key"], "doc_id": span.get("doc_id"),
                "field": span.get("source_field"),
                "at": f"[{span['abs_start']}:{span['abs_end']}]",
                "quote": (span.get("quote") or "")[:70],
                "provenance": resolution["provenance"]["state"],
                **{k: v for k, v in resolution.items()
                   if k not in ("found", "provenance")},
            })
    return buckets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="bundle archived runs for ui/index.html")
    parser.add_argument("--verify", action="store_true",
                        help="check every span against the seed corpus, write nothing")
    args = parser.parse_args(argv)

    if not RUNS_DIR.exists():
        print(f"no archived runs at {RUNS_DIR}", file=sys.stderr)
        return 2

    corpus = load_corpus()
    runs = load_runs()
    print(f"{len(runs)} archived run(s), {len(corpus)} seed record(s)")

    places = build_places(CORPUS_DIR, GAZETTEER_PATH)
    ps = places["stats"]
    print(
        f"\nplaces (A5): {ps['pins']} pin(s), {ps['extents']} extent(s), "
        f"{ps['gaps']} gap(s) across {ps['documents_placed']} placed "
        f"document(s); {ps['edges_drawable']}/{ps['edges_total']} "
        f"subject-place edges drawable; {ps['documents_unconsidered']} "
        f"document(s) not yet considered, "
        f"{ps['documents_declared_unplaceable']} declared unplaceable"
    )
    coastline = load_coastline(REPO / "data")
    if coastline is None:
        print(
            "\nnote: no coastline snapshot in data/ — the Places map will draw "
            "its graticule, points and edges with no landmass behind them, "
            "which is legible only if you already know the region. Generate "
            "one with `python scripts/build_coastline.py`."
        )
    else:
        print(
            f"coastline: {coastline['file']} — {coastline['source']} "
            f"{coastline['scale']}, {coastline['point_count']} points, "
            f"retrieved {coastline['retrieved']} ({coastline['terms']})"
        )

    if places["shape_problems"]:
        print(
            f"\nFAILED: {len(places['shape_problems'])} placement(s) fail the "
            f"build's own shape audit (PHASE2_PLAN A6) — a rule "
            f"ingest/places.py should already enforce at load time:"
        )
        for problem in places["shape_problems"][:5]:
            print(f"  x {problem}")
        return 2

    if places["uncached"]:
        print(
            f"\nFAILED: {len(places['uncached'])} placement(s) resolve to an id "
            f"with no cached gazetteer entry: {places['uncached'][:5]}. Run "
            f"`python -m ingest.gazetteer --refresh --dump <dump>` — "
            f"`ingest.gazetteer --check` should have caught this before the UI "
            f"bundle ever did."
        )
        return 2

    buckets = verify_spans(runs, corpus)
    total = sum(len(v) for v in buckets.values())
    print(f"\n{total} claimed character span(s) checked against the seed corpus:")
    for state in ("resolved", "case_folded", "article_added", "case_only",
                  "moved", "absent"):
        print(f"  {state:<14} {len(buckets[state])}")

    # D1. The SECOND axis. `moved`/`absent` say a claim no longer holds; this
    # says whether the corpus it was made against has moved underneath it.
    # Reported separately because they are separate questions, and because
    # collapsing them is the conflation D1 exists to end.
    provenance = Counter(item["provenance"]
                         for items in buckets.values() for item in items)
    today_digest = corpus_digest(seed_record_hashes(CORPUS_DIR))
    print(f"\nseed corpus on disk: {len(corpus)} record(s), "
          f"digest {today_digest[:16]}... ({CORPUS_DIGEST_ALGORITHM})")
    print("corpus provenance of those spans:")
    for state in PROVENANCE_STATES:
        print(f"  {state:<15} {provenance.get(state, 0)}")
    if provenance.get("unrecorded"):
        print(f"  note: {provenance['unrecorded']} span(s) are UNKNOWN, not "
              f"unchanged. Their runs predate the corpus version, so whether "
              f"the record moved is not knowable from the archive.")

    for state in ("moved", "absent", "case_only"):
        for item in buckets[state][:6]:
            print(f"\n  {state.upper()}  {item['doc_id']}.{item['field']}"
                  f"{item['at']}  ({item['run']})")
            print(f"    quote: {item['quote']!r}")
            print(f"    {item.get('why', '')}")
            print(f"    corpus provenance: {item['provenance']}")
        if len(buckets[state]) > 6:
            print(f"  ... and {len(buckets[state]) - 6} more {state}")

    # `moved` and `absent` mean an archived citation no longer points at what it
    # claimed. `case_only` is a labelling defect in cite.py, not a broken claim,
    # so it is reported but does not fail the check — and since C1a it can only
    # be produced by a run archived before the third match state existed. A
    # `case_only` span on a run archived after 2026-08-14 would mean the label
    # regressed; `case_folded` is the state a new run should reach.
    # D1 changes what is REPORTED, not what fails. A `moved` span whose record
    # provenance is `changed` is explained rather than defective, and it is
    # tempting to stop failing on it - but that is a policy change to the gate
    # and it would silently weaken the check the day it was made. The
    # decomposition is printed; the gate stays where it was until someone
    # decides to move it on purpose, in writing.
    broken = len(buckets["moved"]) + len(buckets["absent"])
    if args.verify:
        return 1 if broken else 0

    gold = {}
    for name in ("answer_cases.json", "confidence_profiles.json", "floor.json"):
        path = GOLD_DIR / name
        if path.exists():
            gold[name.removesuffix(".json")] = json.loads(
                path.read_text(encoding="utf-8"))

    bundle = {
        "generated": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "runs": runs,
        "corpus": corpus,
        "gold": gold,
        # Recorded so the UI can say, honestly, whether the archive it is
        # displaying still matches the corpus on disk.
        "span_audit": {k: len(v) for k, v in buckets.items()},
        "span_problems": buckets["moved"] + buckets["absent"] + buckets["case_only"],
        # Phase 2 A5: the place/gazetteer join `viewPlaces` draws.
        "places": places,
        # A5 addendum: the map's backdrop. None if the snapshot is absent, and
        # the page degrades to a graticule rather than failing.
        "coastline": coastline,
    }

    OUT.write_text(
        "// Generated by ui/build_ui_data.py — do not edit by hand.\n"
        "window.MU_DATA = "
        + json.dumps(bundle, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    size = OUT.stat().st_size / 1024
    print(f"wrote {OUT.relative_to(REPO)} ({size:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
