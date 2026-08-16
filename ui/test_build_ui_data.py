"""Tests for the three build-layer guards PHASE2_PLAN.md A6 assigns:

    - introduce a hand-authored coordinate with no `pleiades_id` -> build must fail
    - introduce an `identified` placement with no citation -> build must fail
    - point a `pleiades_id` at a non-resolving id -> build must fail

The first two are `check_placement_shape`, a re-check of the two G1-criterion-2
shape rules `ingest/places.py::parse_place` already enforces at load time — see
that function's docstring for why re-checking is not redundant work. Because
`parse_place` already refuses both shapes, the fixtures below build `Place`
objects directly rather than going through it, exactly as `ingest/test_places.py`
does when it needs to exercise a shape `parse_place` would never let through.

The third is `build_places`'s existing `uncached` list, which PROGRESS.md
records as implemented but never mutation-verified — that gap is what this file
and `scripts/mutate_ui_places.py` close.

No network, no database, no corpus edits.

Run: python ui/test_build_ui_data.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))         # repo root, for the `ingest` package

from ingest.places import Place, canonical_uri  # noqa: E402
from ingest import gazetteer as gz               # noqa: E402

import build_ui_data as bud  # noqa: E402  (ui/ is on the path — this script's own dir)

failures: list[str] = []


def expect(condition: bool, label: str) -> None:
    if condition:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


def _place(**over) -> Place:
    """A well-formed `Place`, so each test overrides only the field(s) under
    test — the same one-fixture-many-overrides shape as `ingest/test_places.py`'s
    `place()`. Built with the dataclass directly, not `parse_place`, because the
    two defects under test are exactly what `parse_place` already refuses.
    """
    base = dict(
        doc_id="test-doc", block="findspot_places", index=0,
        name="Adulis", ground="stated",
        gazetteer="pleiades", gazetteer_id="39271",
        uri=canonical_uri("pleiades", "39271"),
        ground_citation=None, contested=False, contested_citations=(),
        note=None, role=None,
    )
    base.update(over)
    return Place(**base)


def test_authored_coordinate() -> None:
    print("\ncheck_placement_shape: the authored-coordinate hole")

    ok = _place(ground="stated", gazetteer="pleiades", gazetteer_id="39271")
    expect(bud.check_placement_shape(ok) is None,
           "a stated placement carrying a gazetteer_id passes")

    regional_no_id = _place(ground="regional", gazetteer=None, gazetteer_id=None,
                             uri=None, note="region known, no more")
    expect(bud.check_placement_shape(regional_no_id) is None,
           "a regional placement with no id is not an authored coordinate — "
           "'we know the region and no more' is the honest case this rule "
           "must not catch")

    # `parse_place` refuses this shape outright; it is built directly here to
    # prove the BUILD refuses it too, independently. If this ever stops
    # failing, disabling ingest/places.py's own guard is enough on its own to
    # ship an authored point — see the docstring on check_placement_shape.
    authored = _place(ground="stated", gazetteer=None, gazetteer_id=None, uri=None)
    problem = bud.check_placement_shape(authored)
    expect(problem is not None and "authored coordinate" in problem,
           "a specific place with no gazetteer_id is reported as an "
           "authored coordinate")


def test_identified_without_citation() -> None:
    print("\ncheck_placement_shape: identified with no citation")

    cited = _place(ground="identified", ground_citation="Casson 1989, 52")
    expect(bud.check_placement_shape(cited) is None,
           "an identified placement carrying a citation passes")

    uncited = _place(ground="identified", ground_citation=None)
    problem = bud.check_placement_shape(uncited)
    expect(problem is not None and "identified" in problem
           and "ground_citation" in problem,
           "an identified placement with no ground_citation is reported")


def test_verify_placement_shape_aggregates() -> None:
    print("\nverify_placement_shape: aggregation across a corpus")

    by_doc = {
        "doc-a": [_place(doc_id="doc-a", ground="stated")],
        "doc-b": [
            _place(doc_id="doc-b", block="subject_places", index=0,
                   ground="identified", ground_citation=None, role="focus"),
            _place(doc_id="doc-b", block="subject_places", index=1,
                   ground="regional", gazetteer=None, gazetteer_id=None,
                   uri=None, note="region known, no more", role="mentioned"),
        ],
    }
    problems = bud.verify_placement_shape(by_doc)
    expect(len(problems) == 1 and "doc-b::subject_places[0]" in problems[0],
           "one bad placement among several good ones is named, and the "
           "others are not reported")


def _write_record(corpus: Path, doc_id: str, place: dict) -> None:
    sub = corpus / "test"
    sub.mkdir(parents=True, exist_ok=True)
    (sub / f"{doc_id}.json").write_text(
        json.dumps({"id": doc_id, "findspot_places": [place]}),
        encoding="utf-8",
    )


def test_uncached_id_fails_the_build() -> None:
    print("\nbuild_places: a pleiades_id that never resolves")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        corpus = tmp / "seed_corpus"
        gaz_path = tmp / "gazetteer.json"

        _write_record(corpus, "test-uncached", {
            "name": "Nowhere", "ground": "stated",
            "gazetteer": "pleiades", "gazetteer_id": "999999999",
            "uri": canonical_uri("pleiades", "999999999"),
        })
        gz.write_cache(gz.empty_cache(), gaz_path)

        places = bud.build_places(corpus, gaz_path)
        expect(places["uncached"] == ["pleiades:999999999"],
               "an id absent from the gazetteer cache is reported as uncached")
        expect(places["shape_problems"] == [],
               "a well-formed placement pointed at an uncached id is not also "
               "reported as a shape problem — the two guards are independent")

        # Caching the id (as `ingest.gazetteer --refresh` would) clears it.
        cache = gz.empty_cache()
        cache["places"]["pleiades:999999999"] = {
            "gazetteer": "pleiades", "gazetteer_id": "999999999",
            "title": "Nowhere", "description": None,
            "repr_point": [0.0, 0.0], "bbox": None, "time_periods": None,
            "feature_types": None, "authors": None, "creators": None,
            "dump_date": "2026-08-13", "retrieved": "2026-08-13",
        }
        gz.write_cache(cache, gaz_path)
        places = bud.build_places(corpus, gaz_path)
        expect(places["uncached"] == [],
               "once the id is cached, it is no longer reported as uncached")


def test_case_folded_is_told_from_the_labelling_defect() -> None:
    """C1a: `classify_span` must read the span's own `match`, not just the text.

    Two spans holding byte-identical characters and differing only in what
    `cite.py` claimed about them must classify differently. Before the third
    match state existed there was nothing to read: every case-folded match
    arrived labelled `exact`, so the build could only report the difference as a
    defect. It still must, for the runs archived that way — an archive quietly
    re-labelled is no longer evidence that the defect existed.
    """
    print("\nclassify_span: case_folded is not the same finding as case_only")

    text = "The tribute brought was neither precious nor rare"
    corpus = {"doc-1": {"fields": {"reference_translation": text}}}
    span = {
        "quote": "the tribute brought was neither precious nor rare",
        "doc_id": "doc-1", "source_field": "reference_translation",
        "abs_start": 0, "abs_end": len(text),
    }

    exact = bud.classify_span({**span, "match": "exact"}, corpus)
    expect(exact["state"] == "case_only",
           "a span claiming match='exact' over case-folded characters is still "
           "reported as a labelling defect")

    folded = bud.classify_span({**span, "match": "case_folded"}, corpus)
    # Not marked GUARD: this builds the span dict by hand, so no mutation of
    # cite.py can make it fail. The mutation-verified half of C1a is
    # "GUARD a case-folded match is not recorded as exact" in
    # answer/test_answer.py, exercised by scripts/mutate_part7b.py. This
    # assertion covers the other half — that the build reads the label at all.
    expect(folded["state"] == "case_folded",
           "a span recording match='case_folded' is not reported as a "
           "labelling defect")

    verbatim = bud.classify_span(
        {**span, "quote": text, "match": "exact"}, corpus)
    expect(verbatim["state"] == "resolved",
           "a span whose characters match verbatim is unaffected by either label")


def main() -> int:
    test_authored_coordinate()
    test_identified_without_citation()
    test_verify_placement_shape_aggregates()
    test_uncached_id_fails_the_build()
    test_case_folded_is_told_from_the_labelling_defect()

    print()
    if failures:
        print(f"FAILED ({len(failures)})")
        for f in failures:
            print(f"  x {f}")
        return 1
    print("All build-layer placement-shape assertions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
