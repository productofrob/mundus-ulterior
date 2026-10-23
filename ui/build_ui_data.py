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
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO / "eval" / "answer_runs"
CORPUS_DIR = REPO / "data" / "seed_corpus"
GOLD_DIR = REPO / "eval" / "gold"
RANKING_DIR = REPO / "eval" / "ranking_runs"
GAZETTEER_PATH = REPO / "data" / "gazetteer.json"
OUT = Path(__file__).resolve().parent / "data.js"
# DEBT ROW 7, FINDING 74. `data.js` is one line of ~9.5MB, so every rebuild is
# `2 +-` in `git diff --stat` and no reviewer -- human or otherwise -- can tell
# a corpus rebuild from a coastline swap from a corruption. This is the diff
# that can be read: pretty-printed, sorted, one fact per line, written by the
# same command in the same breath so it cannot drift from what it describes.
# It is a DESCRIPTION and never a second source of truth: `check_ui.mjs`
# re-derives every figure in it from `data.js` and fails on any disagreement,
# which is what stops it from becoming a file that says whatever it last said.
MANIFEST = Path(__file__).resolve().parent / "data.manifest.json"

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
# The Methodology figures, 2026-10-23. `load_corpus` is taken under another name
# because this file already has a `load_corpus` of its own, which reads the seed
# records for display; the loader's is the one that cuts them into passages.
from ingest.loader import load_corpus as cut_corpus_into_passages  # noqa: E402
from ingest.fidelity import (                 # noqa: E402
    check_declared_tiers, declared_script_disagreement, derive_record_tier,
    script_mix,
)

TIERS_PATH = REPO / "data" / "corpus_tiers.json"

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


def attach_passages_and_tiers(corpus: dict[str, dict]) -> list[str]:
    """Give every record its passages and its tier, for the Methodology figures.

    Added 2026-10-23, when the Methodology tab gained figures that draw one
    record's passages (§3) and the tier of every record (§2). Neither was in the
    bundle: passages exist only in the database and in archived runs, and an
    archived run records the passages AS THEY WERE CUT THEN - the Periplus §56
    passage sits at 1301-2220 in one run and 1511-2430 in a later one. A figure
    drawn from the archive would draw a record that no longer exists.

    So the passages are cut here, by the loader that ingestion uses, from the
    records on disk today. Each one carries what the figure says about it: its
    positions, its declared language, the script its characters are in, and
    whether the loader's own cross-check finds the two in agreement.

    The tier is the DECLARED one, from data/corpus_tiers.json, and it is only
    attached once `derive_record_tier` agrees with it - the check ingest.verify
    makes (ruling 43). A figure that counted declarations nothing had checked
    would be counting what a curator believed rather than what the records are.

    Returns the problems found. An empty list means every record has both.
    """
    problems: list[str] = []
    cut = cut_corpus_into_passages(CORPUS_DIR)

    by_doc: dict[str, list[dict]] = {}
    for c in cut.chunks:
        field_text = (corpus.get(c.doc_id) or {}).get("fields", {}).get(c.source_field)
        # The chunker's one promise, checked where it is relied on: the
        # characters at the positions are the passage. A figure that prints the
        # positions is claiming exactly this.
        if field_text is None or field_text[c.char_start:c.char_end] != c.text:
            problems.append(f"{c.chunk_id}: the record's characters at "
                            f"{c.char_start}-{c.char_end} are not the passage")
            continue
        mix = script_mix(c.text)
        # The dominant script by share; ties go to the name that sorts first so
        # a rebuild cannot flip it.
        script = (sorted(mix.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
                  if mix else None)
        by_doc.setdefault(c.doc_id, []).append({
            "id": c.chunk_id,
            "role": c.role,
            "field": c.source_field,
            "start": c.char_start,
            "end": c.char_end,
            "declared": c.declared_lang,
            "script": script,
            "script_agrees": (declared_script_disagreement(c.text, c.declared_lang) is None
                              if c.declared_lang else None),
            "eligible": c.eligible_for_retrieval,
        })

    declared = json.loads(TIERS_PATH.read_text(encoding="utf-8")).get("tiers") or {}
    rows: dict[str, list[tuple]] = {}
    for c in cut.chunks:
        rows.setdefault(c.doc_id, []).append(
            (c.role, c.text_fidelity, c.lang, c.eligible_for_retrieval))
    derived = {
        d.doc_id: derive_record_tier(d.source_type, rows.get(d.doc_id, []),
                                     getattr(d, "translation_source", None))
        for d in cut.documents
    }
    problems.extend(f"record tier: {p}" for p in check_declared_tiers(declared, derived))

    for doc_id, entry in corpus.items():
        entry["passages"] = by_doc.get(doc_id, [])
        if not entry["passages"]:
            problems.append(f"{doc_id}: the loader cut no passages from it")
        if doc_id in declared:
            entry["tier"] = declared[doc_id]
        else:
            problems.append(f"{doc_id}: no declared tier")
    return problems


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
    - `whitespace_only` — the characters at the offset are the quoted
      characters once runs of whitespace are collapsed, and nothing else
      differs. FINDING 42, F3. `cite.locate_in_text` matches on
      whitespace-collapsed text BY DESIGN and says so in its own header, so
      `match="exact"` beside a collapsed match is not an overstatement the way
      `case_only` is: the offset is right, the label is right, and what differs
      is the ARCHIVE'S RENDERING of a line break the record still holds. It is
      reported rather than smoothed away, because an edit that changed only
      spacing must stay visible — and it is not a defect, so it does not fail
      the check. Before this category existed such a span fell all the way
      through to `absent`, which is what a fabricated citation looks like, and
      it did so on a correctly grounded Tamil quotation.
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
                    "why": "differs from the quotation only in letter case, and the "
                           "answer recorded it as such — the character positions are "
                           "right and so is the label"}
        return {"state": "case_only", "found": found,
                "why": f"differs from the quotation only in letter case; the checker "
                       f"matched it without regard to case but recorded the match as "
                       f"{recorded!r} — a labeling fault, shown as it was claimed"}

    # FINDING 42. The verifier was stricter than the matcher it verifies, and
    # it failed into the loudest category it has. `collapse` is IMPORTED from
    # the matcher rather than re-implemented here: a second whitespace rule
    # written beside the first is a rule that disagrees once, which is the
    # argument SOURCE_LANGUAGE_TIERS already makes in ingest/fidelity.py.
    #
    # Placed BELOW the case branches and ABOVE `moved`: the offset is right, and
    # "the offset is right" is the stronger statement about a span than "the
    # quotation is elsewhere in the field".
    from answer.cite import collapse
    collapsed_found, collapsed_quote = collapse(found), collapse(quote)
    if _same_characters(collapsed_found, collapsed_quote):
        return {"state": "whitespace_only", "found": found,
                "why": "the characters at these positions are the quoted characters "
                       "once repeated spaces and line breaks are treated as one - the "
                       "stored answer and the record disagree about a line break, which "
                       "the checker allows by design, so the positions and the label "
                       "are both right"}
    if _same_characters(collapsed_found.casefold(), collapsed_quote.casefold()):
        return {"state": "whitespace_only", "found": found,
                "why": f"the characters at these positions are the quoted characters "
                       f"once spacing and letter case are both set aside; the answer "
                       f"recorded the match as {recorded!r}. The positions are right; "
                       f"read the label alongside the letter-case rows above"}

    at = text.find(quote)
    if at < 0 and quote:
        at = text.casefold().find(quote.casefold())
    if at >= 0:
        return {"state": "moved", "found": found, "now_at": [at, at + len(quote)],
                "why": "the record was edited after this answer was stored; the "
                       "quotation is still in the same field, at a different position"}
    return {"state": "absent", "found": found,
            "why": "the quotation is not in this field of the record as it stands "
                   "today"}


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
                                "whitespace_only": [],
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


def _digest(obj: Any) -> str:
    """Stable sha256 of any bundle section, over canonical JSON."""
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build_manifest(bundle: dict, data_js: bytes, buckets: dict,
                   today_digest: str) -> dict:
    """A reviewable description of `data.js`, small enough to read in a diff.

    Every count here is derived from the bundle that was just written, in this
    process, from the same objects. A manifest assembled from a second pass
    over the corpus could disagree with the file it names and be the more
    convincing of the two.
    """
    runs = bundle["runs"]
    spans = [s for r in runs
             for s in r.get("grounding", {}).get("quote_spans", [])
             if s.get("resolution")]
    prov = Counter(s["resolution"]["provenance"]["state"] for s in spans)
    states = Counter(s["resolution"]["state"] for s in spans)
    places = bundle.get("places") or {}
    coast = bundle.get("coastline") or {}
    corpus = bundle["corpus"]

    return {
        "_": "Generated beside ui/data.js by ui/build_ui_data.py. Never edited "
             "by hand, and never read as truth: check_ui.mjs re-derives every "
             "figure below from data.js itself and fails on disagreement. It "
             "exists so a change to a 9.5MB single-line file can be reviewed "
             "(debt row 7, FINDING 74).",
        "generated": bundle["generated"],
        "data_js": {
            "bytes": len(data_js),
            "sha256": hashlib.sha256(data_js).hexdigest(),
        },
        "corpus": {
            "records": len(corpus),
            "digest": today_digest,
            "digest_algorithm": CORPUS_DIGEST_ALGORITHM,
            "languages": sorted({c for rec in corpus.values()
                                 for c in rec.get("language_code") or []}),
            "regions": dict(sorted(Counter(
                rec.get("region") or "(none)" for rec in corpus.values()).items())),
            # The Methodology figures, 2026-10-23: the declared tier of every
            # record (§2) and the passages the loader cuts today (§3).
            "tiers": dict(sorted(Counter(
                rec.get("tier") or "(none)" for rec in corpus.values()).items())),
            "passages": sum(len(rec.get("passages") or []) for rec in corpus.values()),
            "sha256": _digest(corpus),
        },
        "runs": {
            "count": len(runs),
            "questions": sorted({r["question"] for r in runs}),
            "prompt_versions": dict(sorted(Counter(
                r.get("prompt_version") or "(none)" for r in runs).items())),
            "with_corpus_version": sum(1 for r in runs if r.get("corpus_version")),
            "sha256": _digest(runs),
        },
        "spans": {
            "claimed": sum(len(v) for v in buckets.values()),
            # FIRST AXIS: does the archived quote still sit at its offset.
            "audit": dict(sorted(states.items())),
            # SECOND AXIS (D1): has the record moved underneath the span. Kept
            # as its own key because the two are different questions and a
            # manifest that merged them would make the merge look official.
            "corpus_provenance": dict(sorted(prov.items())),
            "sha256": _digest([s["resolution"] for s in spans]),
        },
        "places": {
            "stats": dict(sorted((places.get("stats") or {}).items())),
            "groups": len(places.get("groups") or []),
            "edges": len(places.get("edges") or []),
            "declared_unplaceable": sorted(places.get("declared_unplaceable") or {}),
            "unconsidered": sorted(places.get("unconsidered") or []),
            "sha256": _digest(places),
        },
        "coastline": {
            "source": coast.get("source"),
            "scale": coast.get("scale"),
            "retrieved": coast.get("retrieved"),
            "terms": coast.get("terms"),
            "polygon_count": coast.get("polygon_count"),
            "point_count": coast.get("point_count"),
            "simplify_tolerance": coast.get("simplify_tolerance"),
            "sha256": _digest(coast),
        } if coast else None,
        "gold": {name: _digest(obj)
                 for name, obj in sorted((bundle.get("gold") or {}).items())},
        "retrieval": ({
            "run": (bundle.get("retrieval") or {}).get("run"),
            "pairs": len((bundle.get("retrieval") or {}).get("pairs") or []),
            "series": len((bundle.get("retrieval") or {}).get("series") or []),
            "runs_excluded": (bundle.get("retrieval") or {}).get("runs_excluded"),
            "sha256": _digest(bundle.get("retrieval")),
        } if bundle.get("retrieval") else None),
    }


def load_retrieval(ranking_dir: Path) -> dict[str, Any] | None:
    """The retrieval check, split by the language of the source it looks for.

    THE PAGE SAID NOBODY REPORTED THIS, AND NOBODY DID. `run_ranking_check.py`
    prints one total and a cohort breakdown; the decline that mattered was in
    neither, and it took a split by language to see it at all. Every figure
    here is re-derived from the archived runs rather than copied out of a
    result document.

    ONLY COMPARABLE RUNS GO IN THE SERIES. A run with `collapsed` or
    `reranked` set used the two search improvements that were built, used and
    then dropped (FINDING 93). Its numbers cannot sit in the same series as the
    runs the archived answers were produced under, so they are EXCLUDED AND
    COUNTED rather than quietly averaged in.

    The language table comes from the newest comparable run that searched the
    padded index, because that is the hardest condition this project has
    measured and the one the page's claims are about.
    """
    if not ranking_dir.is_dir():
        return None
    runs = []
    for path in sorted(ranking_dir.glob("*.json")):
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(run, dict) or not run.get("pairs"):
            continue
        run["_file"] = path.name
        runs.append(run)
    if not runs:
        return None

    def comparable(run: dict) -> bool:
        return not run.get("collapsed") and not run.get("reranked")

    usable = [r for r in runs if comparable(r)]
    excluded = len(runs) - len(usable)
    if not usable:
        return None

    padded = [r for r in usable if "distractor" in str(r.get("view", ""))]
    latest = max(padded or usable, key=lambda r: str(r.get("timestamp", "")))

    def found(pair: dict) -> bool:
        return bool(pair.get("recall_at_6"))

    # The series: one row per comparable run, English and non-English kept
    # apart, because the total moved far less than either half did.
    series = []
    for run in sorted(usable, key=lambda r: str(r.get("timestamp", ""))):
        pairs = run.get("pairs") or []
        eng = [p for p in pairs if (p.get("expect_lang") or "") == "en"]
        oth = [p for p in pairs if (p.get("expect_lang") or "") != "en"]
        series.append({
            "timestamp": run.get("timestamp"),
            "view": run.get("view"),
            "index_chunks": run.get("index_chunks"),
            "pairs": len(pairs),
            "english": {"pairs": len(eng), "found": sum(1 for p in eng if found(p))},
            "other": {"pairs": len(oth), "found": sum(1 for p in oth if found(p))},
        })

    # The rows the page aggregates by language. Kept per pair, not per language,
    # so the page and its guard can derive the same table from the same rows
    # without either of them being the other's source.
    rows = []
    for pair in latest.get("pairs") or []:
        rows.append({
            "id": pair.get("id"),
            "region": pair.get("region"),
            "expect_lang": pair.get("expect_lang"),
            "expect_doc": pair.get("expect_doc"),
            "query_lang": pair.get("query_lang"),
            "rank": pair.get("rank"),
            "found_at_6": found(pair),
            "gap_vs_other_doc": pair.get("gap_vs_other_doc"),
        })

    return {
        "note": "Derived from the archived ranking runs by ui/build_ui_data.py. "
                "Runs that used the collapse or rerank experiments are excluded "
                "from the series and counted separately.",
        "run": {
            "file": latest.get("_file"),
            "timestamp": latest.get("timestamp"),
            "view": latest.get("view"),
            "index_chunks": latest.get("index_chunks"),
            "search_k": latest.get("search_k"),
            "query_embedding_model": latest.get("query_embedding_model"),
        },
        "pairs": rows,
        "series": series,
        "runs_excluded": excluded,
    }


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

    cut_problems = attach_passages_and_tiers(corpus)
    if cut_problems:
        print(f"\nFAILED: {len(cut_problems)} record(s) cannot give the Methodology "
              f"figures their passages or their tier:")
        for problem in cut_problems[:8]:
            print(f"  x {problem}")
        return 2
    print(f"passages: {sum(len(e['passages']) for e in corpus.values())} cut by the "
          f"loader; tiers: " + ", ".join(
              f"{t} {n}" for t, n in sorted(Counter(e['tier'] for e in corpus.values()).items())))

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
    retrieval = load_retrieval(RANKING_DIR)
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
                  "whitespace_only", "moved", "absent"):
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

    for state in ("moved", "absent", "case_only", "whitespace_only"):
        for item in buckets[state][:6]:
            print(f"\n  {state.upper()}  {item['doc_id']}.{item['field']}"
                  f"{item['at']}  ({item['run']})")
            print(f"    quote: {item['quote']!r}")
            print(f"    {item.get('why', '')}")
            print(f"    corpus provenance: {item['provenance']}")
        if len(buckets[state]) > 6:
            print(f"  ... and {len(buckets[state]) - 6} more {state}")

    # `moved` and `absent` mean an archived citation no longer points at what it
    # claimed. `whitespace_only` means the archive and the record disagree about
    # a line break: FINDING 42, and it is neither a broken claim nor a labelling
    # defect, because cite.py matches on whitespace-collapsed text by design. It
    # is COUNTED and PRINTED rather than tolerated silently - a verifier made
    # whitespace-insensitive would hide an edit that changed only spacing, which
    # is a real edit to a record whose offsets other runs depend on.
    # `case_only` is a labelling defect in cite.py, not a broken claim,
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
        # The retrieval check split by the language of the source, which is the
        # one measure that was moving while nothing reported it.
        "retrieval": retrieval,
    }

    # FINDING 101, and FINDING 52's rule applied where it had not reached:
    # WRITE BYTES. `Path.write_text` is text mode, so on Windows every \n
    # became \r\n, and `.gitattributes` is `* -text`, so git stored the CR
    # bytes exactly as they arrived. It surfaced here — two CR bytes and a
    # different sha256 for a reason unrelated to content — on the one file in
    # this repository where it could do no damage. `ingest.verify` now asserts
    # the same property of `data/seed_corpus/`, where it would shift 168
    # archived citation spans by one byte per line.
    OUT.write_bytes(
        (
            "// Generated by ui/build_ui_data.py — do not edit by hand.\n"
            "window.MU_DATA = "
            + json.dumps(bundle, ensure_ascii=False, separators=(",", ":"))
            + ";\n"
        ).encode("utf-8")
    )
    size = OUT.stat().st_size / 1024
    print(f"wrote {OUT.relative_to(REPO)} ({size:.0f} KB)")

    # Debt row 7. Written from the bundle in hand, in the same run, so it can
    # never describe a data.js that is not the one on disk beside it.
    manifest = build_manifest(bundle, OUT.read_bytes(), buckets, today_digest)
    MANIFEST.write_bytes(
        (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=False) + "\n")
        .encode("utf-8"))
    print(f"wrote {MANIFEST.relative_to(REPO)} "
          f"({MANIFEST.stat().st_size / 1024:.1f} KB) — the diffable one")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
