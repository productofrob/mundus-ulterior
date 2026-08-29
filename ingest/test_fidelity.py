"""Record-tier tests. No network, no database, no corpus edits.

Run: python -m ingest.test_fidelity

Every import sits at module scope, deliberately, for the reason
`ingest/test_places.py` gives: a name that goes away must fail at load rather
than truncating the run two-thirds of the way down.

The guards below are the F1 tiering policy in code. `data/corpus_tiers.json`
is the DECLARATION -- what a curator says each record is -- and
`derive_record_tier` is the reading. A tier that were only derived could never
be wrong and could never be checked either, so both exist and
`check_declared_tiers` is where they have to agree.

Guard labels are ASCII on purpose. FINDING 10's family: a label carrying an
em-dash could not be matched against its own failure line once a harness
decoded the child's stdout with the locale codec, and two harnesses printed
MISS on mutations that had worked perfectly.

`scripts/mutate_fidelity.py` breaks each rule in turn and confirms the guard
protecting THAT rule fires.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from .fidelity import (
    GLOSS_CAPABLE_TIERS,
    PARAPHRASE_FLAG_LIFTED,
    PARAPHRASE_ID_HINTS,
    RECORD_TIERS,
    UNCLASSIFIABLE,
    check_declared_tiers,
    check_paraphrase_flags,
    check_target_mix,
    derive_record_tier,
)
from .loader import SEED_CORPUS_DIR, load_corpus
from .verify import MANIFEST_FLAGGED

# FINDING 10: this process's own stdout. Through a pipe or a redirect on
# Windows it falls back to the locale codec, which cannot encode Greek, Tamil,
# Chinese, Ge'ez or runic, and it raises mid-output with the file half written
# and every number in it correct.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

TIERS_FILE = Path(__file__).resolve().parent.parent / "data" / "corpus_tiers.json"

failures: list[str] = []
# Counted rather than transcribed. On 2026-08-29 the assertion count went into
# five documents as 29 and the suite had 30 -- written down once, before the
# last four assertions were added, and never recounted. The suite is the only
# thing that knows how many assertions it has, so it is what says so.
passes: list[str] = []


def expect(condition: bool, label: str) -> None:
    if condition:
        print(f"  ok   {label}")
        passes.append(label)
    else:
        print(f"  FAIL {label}")
        failures.append(label)


# --------------------------------------------------------------------------
# Fixtures. (role, text_fidelity, lang, eligible_for_retrieval)
# --------------------------------------------------------------------------

GREEK = ("original", "verbatim_original", "grc", True)
CHINESE_PARTIAL = ("original", "partial_verbatim", "lzh", True)
PARTHIAN_TRANSLIT = ("original", "transliteration", "xpr", True)
ENGLISH_ORIGINAL = ("original", "verbatim_original", "en", True)
POINTER = ("original", "pointer", "en", False)
PARAPHRASE = ("original", "paraphrase", "en", False)
TRANSLATION = ("translation", "translation", "en", True)
OBJECT_DESC = ("original", "object_description", "en", True)

CITED = "Wilfred H. Schoff translation (1912)"


def tier(rows, source_type="literary_text", translation_source=CITED):
    return derive_record_tier(source_type, rows, translation_source)[0]


def test_derivation():
    print("derive_record_tier")

    # A catalogue record is decided by source_type and by nothing else. The
    # classifier already forces object_description on these, so letting the
    # shape of the fields vote would let a Korean catalogue description be read
    # as Korean source text.
    expect(
        all(
            tier([GREEK, TRANSLATION], source_type=st) == "catalogue_record"
            for st in ("find_record", "coin_record", "object_record", "artefact_record")
        ),
        "GUARD a find record tiers as catalogue_record whatever its text fields contain",
    )

    expect(
        tier([POINTER]) == "pointer_only"
        and tier([PARAPHRASE]) == "pointer_only",
        "GUARD a record with nothing retrieval-eligible in either role tiers as pointer_only",
    )

    expect(
        tier([GREEK, TRANSLATION]) == "verbatim_with_provenance",
        "GUARD source-language text with a cited published translation tiers as verbatim_with_provenance",
    )

    # The tier F3-F7 predicts becomes the common case, and the reason the
    # vocabulary was amended before curation rather than after.
    expect(
        tier([GREEK]) == "verbatim_machine_english",
        "GUARD source-language text with no published translation tiers as verbatim_machine_english",
    )

    # partial_verbatim means "flagged and unchecked", not "not there". Three of
    # the eleven verbatim records at 24 carry it.
    expect(
        tier([CHINESE_PARTIAL, TRANSLATION]) == "verbatim_with_provenance",
        "GUARD a partial_verbatim original counts as source-language text",
    )

    # Four more of the eleven are transliterations. Excluding either class
    # would tier seven of eleven as holding no source text at all.
    expect(
        tier([PARTHIAN_TRANSLIT, TRANSLATION]) == "verbatim_with_provenance",
        "GUARD a transliteration original counts as source-language text",
    )

    expect(
        tier([GREEK, TRANSLATION], translation_source="") == UNCLASSIFIABLE
        and tier([GREEK, TRANSLATION], translation_source=None) == UNCLASSIFIABLE,
        "GUARD a translation with an empty translation_source is refused, because both cited is the clause",
    )

    # Not published_translation_only: that tier asserts no original
    # transcription is available, and here the field on disk IS the original.
    expect(
        tier([ENGLISH_ORIGINAL, TRANSLATION]) == UNCLASSIFIABLE,
        "GUARD a retrieval-eligible English original on a non-find record is refused rather than read as published_translation_only",
    )

    expect(
        tier([POINTER, TRANSLATION]) == "published_translation_only",
        "GUARD no source-language original and a cited translation tiers as published_translation_only",
    )

    # A record nobody can tier is a record somebody has to look at.
    expect(
        tier([]) == UNCLASSIFIABLE and tier([OBJECT_DESC]) == UNCLASSIFIABLE,
        "GUARD a record no tier holds returns unclassifiable rather than a default",
    )

    expect(
        all(t in RECORD_TIERS for t in (
            tier([GREEK, TRANSLATION]),
            tier([GREEK]),
            tier([POINTER, TRANSLATION]),
            tier([GREEK, TRANSLATION], source_type="coin_record"),
            tier([POINTER]),
        )),
        "GUARD every tier the derivation returns is in the declared vocabulary",
    )


def test_declaration_checking():
    print("check_declared_tiers")

    derived = {
        "a": ("verbatim_with_provenance", "reason"),
        "b": ("catalogue_record", "reason"),
    }

    expect(
        not check_declared_tiers(
            {"a": "verbatim_with_provenance", "b": "catalogue_record"}, derived
        ),
        "GUARD a declaration that matches the derivation reports no problem",
    )

    expect(
        any("no declared tier" in p for p in check_declared_tiers(
            {"a": "verbatim_with_provenance"}, derived
        )),
        "GUARD a record with no declared tier is refused",
    )

    # The other drift direction, and it is the one nobody checks: a stale entry
    # silently makes the count wrong.
    expect(
        any("not in the corpus" in p for p in check_declared_tiers(
            {"a": "verbatim_with_provenance", "b": "catalogue_record",
             "gone": "catalogue_record"},
            derived,
        )),
        "GUARD a declared tier naming a record that is not in the corpus is refused",
    )

    expect(
        any("declared 'catalogue_record'" in p for p in check_declared_tiers(
            {"a": "catalogue_record", "b": "catalogue_record"}, derived
        )),
        "GUARD a declared tier that disagrees with the derived one is refused",
    )

    expect(
        any("not a declarable tier" in p for p in check_declared_tiers(
            {"a": UNCLASSIFIABLE, "b": "catalogue_record"}, derived
        )),
        "GUARD unclassifiable is refused as a declared tier",
    )

    expect(
        any("not one of" in p for p in check_declared_tiers(
            {"a": "verbatim_with_pedigree", "b": "catalogue_record"}, derived
        )),
        "GUARD a declared tier outside the vocabulary is refused",
    )


def test_paraphrase_flags():
    """FINDING 31. The manifest's flags and the code's, which drifted for a week."""
    print("check_paraphrase_flags")

    expect(
        not check_paraphrase_flags(set(MANIFEST_FLAGGED)),
        "GUARD every record the manifest flags is either honoured in code or carries a written lift",
    )

    expect(
        any("neither honours" in p for p in check_paraphrase_flags(
            set(MANIFEST_FLAGGED) | {"a-record-nobody-told-the-code-about"}
        )),
        "GUARD a manifest flag the code neither honours nor lifts is refused",
    )

    saved = dict(PARAPHRASE_FLAG_LIFTED)
    try:
        PARAPHRASE_FLAG_LIFTED[next(iter(saved))] = "   "
        expect(
            any("no written reason" in p
                for p in check_paraphrase_flags(set(MANIFEST_FLAGGED))),
            "GUARD a lift with no written reason is refused",
        )
        PARAPHRASE_FLAG_LIFTED.clear()
        PARAPHRASE_FLAG_LIFTED.update(saved)
        PARAPHRASE_FLAG_LIFTED[PARAPHRASE_ID_HINTS[0]] = "lifted as well as honoured"
        expect(
            any("in force and withdrawn" in p
                for p in check_paraphrase_flags(set(MANIFEST_FLAGGED))),
            "GUARD a flag cannot be honoured and lifted at once",
        )
        PARAPHRASE_FLAG_LIFTED.clear()
        PARAPHRASE_FLAG_LIFTED.update(saved)
        expect(
            any("does not flag" in p for p in check_paraphrase_flags(
                set(MANIFEST_FLAGGED) - set(saved)
            )),
            "GUARD a lift naming a flag the manifest does not carry is refused",
        )
    finally:
        PARAPHRASE_FLAG_LIFTED.clear()
        PARAPHRASE_FLAG_LIFTED.update(saved)


def test_target_mix():
    print("check_target_mix")
    doc = json.loads(TIERS_FILE.read_text(encoding="utf-8"))
    mix, at24 = doc["target_mix"], doc["measured_at_24"]

    expect(
        not check_target_mix(mix, at24),
        "GUARD the declared target mix is internally coherent",
    )

    broken = json.loads(json.dumps(mix))
    broken["by_tier_new"]["catalogue_record"] += 1
    expect(
        any("by_tier_new sums to" in p for p in check_target_mix(broken, at24)),
        "GUARD a target mix whose tier targets do not sum to the tranche is refused",
    )

    broken = json.loads(json.dumps(mix))
    broken["by_tier_new"]["pointer_only"] = 1
    broken["by_tier_new"]["catalogue_record"] -= 1
    broken["by_tier_at_60"]["pointer_only"] = at24.get("pointer_only", 0) + 1
    broken["by_tier_at_60"]["catalogue_record"] -= 1
    expect(
        any("pointer_only" in p for p in check_target_mix(broken, at24)),
        "GUARD a target mix that allows a new pointer_only record is refused",
    )

    broken = json.loads(json.dumps(mix))
    broken["min_source_language_records_per_region"] = 6
    expect(
        any("source-language records" in p for p in check_target_mix(broken, at24)),
        "GUARD a per-region minimum the aggregate targets cannot reach is refused",
    )

    broken = json.loads(json.dumps(mix))
    broken["which_tiers_can_carry_a_gloss_case"] = [
        "verbatim_with_provenance", "verbatim_machine_english"
    ]
    expect(
        any("gloss" in p for p in check_target_mix(broken, at24)),
        "GUARD a gloss case may not be declared possible on verbatim_machine_english",
    )

    expect(
        "verbatim_machine_english" not in GLOSS_CAPABLE_TIERS,
        "GUARD the gloss-capable tier set excludes the tier whose only English is machine",
    )


def test_against_the_live_corpus():
    print("the 24 seed records")
    doc = json.loads(TIERS_FILE.read_text(encoding="utf-8"))
    result = load_corpus(SEED_CORPUS_DIR)

    rows: dict[str, list] = defaultdict(list)
    for c in result.chunks:
        rows[c.doc_id].append(
            (c.role, c.text_fidelity, c.lang, c.eligible_for_retrieval)
        )

    derived = {
        d.doc_id: derive_record_tier(
            d.source_type, rows[d.doc_id], getattr(d, "translation_source", None)
        )
        for d in result.documents
    }

    problems = check_declared_tiers(doc["tiers"], derived)
    if problems:
        for p in problems:
            print(f"       {p}")
    expect(
        not problems,
        "GUARD every seed record derives the tier data/corpus_tiers.json declares",
    )

    # The measured histogram is a fact about the corpus at the moment the
    # policy was declared, and it is what the target mix is arithmetic over.
    # If it drifts, every target above it is denominated in a corpus that is
    # not the one on disk -- FINDING 14's shape, one level up.
    actual: dict[str, int] = {t: 0 for t in RECORD_TIERS}
    for t, _reason in derived.values():
        actual[t] = actual.get(t, 0) + 1
    expect(
        actual == {k: int(v) for k, v in doc["measured_at_24"].items()},
        "GUARD the measured histogram the target mix is arithmetic over still holds",
    )


def main() -> int:
    test_derivation()
    test_declaration_checking()
    test_paraphrase_flags()
    test_target_mix()
    test_against_the_live_corpus()

    print()
    if failures:
        print(f"FAILED ({len(failures)})")
        for f in failures:
            print(f"  x {f}")
        print(f"\n{len(passes)} passed, {len(failures)} failed")
        return 1
    print(f"{len(passes)} passed, 0 failed")
    print("All record-tier assertions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
