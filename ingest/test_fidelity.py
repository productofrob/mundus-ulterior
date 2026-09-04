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
    SOURCE_LANGUAGE_TIERS,
    source_language_provenance,
    check_allocation,
    check_delivery,
    PARAPHRASE_FLAG_LIFTED,
    PARAPHRASE_ID_HINTS,
    RECORD_TIERS,
    UNCLASSIFIABLE,
    check_declared_tiers,
    check_paraphrase_flags,
    check_target_mix,
    split_quotation_cases,
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


def test_allocation():
    """Ruling 51, F3. The mix at 60 says WHAT; the allocation says WHEN.

    Every aggregate target in corpus_tiers.json is satisfiable inside Arabia
    and South Asia alone, and F3-F7 curate roughly seven records at a time. An
    allocation decided at F7 is an allocation fitted to what was already
    curated, so it is declared before the first new record and checked here.

    Guard labels are ASCII, like every label in this file.
    """
    print("check_allocation")
    doc = json.loads(TIERS_FILE.read_text(encoding="utf-8"))
    mix = doc["target_mix"]
    at24 = mix["records_by_region_at_24"]
    sl24 = mix["source_language_records_by_region_at_24"]

    expect(
        not check_allocation(mix, at24, sl24),
        "GUARD the declared allocation delivers the declared mix",
    )

    broken = json.loads(json.dumps(mix))
    broken["allocation"]["sub_tranches"] = []
    expect(
        any("declares no sub_tranches" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD an allocation with no sub-tranches is refused",
    )

    broken = json.loads(json.dumps(mix))
    broken["allocation"]["sub_tranches"][0]["slots"][0]["n"] -= 1
    expect(
        any("by_tier_new adds" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD an allocation that does not place every record in the tranche is refused",
    )

    # One slot relabelled. The count is untouched, so only the tier totals move.
    broken = json.loads(json.dumps(mix))
    broken["allocation"]["sub_tranches"][0]["slots"][0]["tier"] = "catalogue_record"
    expect(
        any("by_tier_new declares" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD an allocation whose tier totals differ from by_tier_new is refused",
    )

    # Two slots swap regions. Tier totals hold; the per-region ones do not.
    broken = json.loads(json.dumps(mix))
    broken["allocation"]["sub_tranches"][0]["slots"][0]["region"] = "Arabia"
    expect(
        any("the target at 60 is" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD an allocation whose per-region totals miss the target at 60 is refused",
    )

    # Southeast Asia's four source-language records become catalogue records
    # somewhere else: the aggregate still adds up and the region is left where
    # it started, which is the failure the per-region floor exists to catch.
    broken = json.loads(json.dumps(mix))
    for tranche in broken["allocation"]["sub_tranches"]:
        for slot in tranche["slots"]:
            if slot["region"] == "Southeast Asia":
                slot["tier"] = "catalogue_record"
    expect(
        any("source-language record(s) and the floor is" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD a region left below the source-language floor is refused",
    )

    # The cheap tier jumps the queue: the same 36 records, curated in the order
    # a block short of days drifts toward.
    # Ruling 62, F5. ingest.cost's precedent: a phase with no written definition
    # is refused. A gloss kind the code accepts and the file does not explain is
    # the same defect, and FINDING 56 is the reason it is checked from the DATA
    # side rather than by inventing a stricter rule in the checker.
    broken = json.loads(json.dumps(mix))
    broken["what_the_two_gloss_KINDS_are"].pop("hedged_identification")
    expect(
        any("no written definition" in p
            for p in check_target_mix(broken, doc["measured_at_24"])),
        "GUARD a gloss kind the code accepts and the file does not explain is refused",
    )

    broken = json.loads(json.dumps(mix))
    broken["allocation"]["sub_tranches"].reverse()
    expect(
        any("is curated before every catalogue record" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD an allocation that curates a catalogue record before a source-language record is refused",
    )

    broken = json.loads(json.dumps(mix))
    broken["allocation"]["sub_tranches"][0]["gloss_capable"] = 0
    expect(
        any("gloss-capable record(s); the mix" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD an allocation that drops a gloss-capable record is refused",
    )

    # Ruling 68, F5. This clause was an EQUALITY, and an equality is a plan with
    # no tolerance for a sub-tranche closing short. Two have. The direction that
    # can never be recovered is still guarded above; the direction that costs
    # nothing is now allowed, because the ceiling is enforced at DELIVERY where
    # it can actually be observed.
    slack = json.loads(json.dumps(mix))
    slack["allocation"]["sub_tranches"][3]["gloss_capable"] += 1
    expect(
        not any("gloss-capable record(s); the mix" in p
                for p in check_allocation(slack, at24, sl24)),
        "GUARD an allocation placing MORE gloss-capable records than the target "
        "is accepted, because a plan with no slack fails on the first miss",
    )

    broken = json.loads(json.dumps(mix))
    broken["allocation"]["sub_tranches"][0]["slots"] = [
        {"region": "Southeast Asia", "tier": "verbatim_machine_english", "n": 8}
    ]
    expect(
        any("on a tier that can carry a gloss case" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD gloss-capable records allocated to a sub-tranche that cannot carry one are refused",
    )

    broken = json.loads(json.dumps(mix))
    for tranche in broken["allocation"]["sub_tranches"]:
        tranche["expect_quoted_from_original_cases"] = 0
    expect(
        any("expect_quoted_from_original" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD an allocation writing fewer quoted-from-original cases than the mix requires is refused",
    )

    # RULING 56, F4. The quotation quota is two questions under one name, and
    # the four assertions below are the four ways the split can be undone: by
    # writing choice cases where nothing competes, by never declaring the second
    # line, by writing more of it than there are records to carry it, and by
    # classifying a case from the plan instead of from the record it names.
    broken = json.loads(json.dumps(mix))
    broken["allocation"]["sub_tranches"][0]["slots"] = [
        {"region": "Southeast Asia", "tier": "verbatim_machine_english", "n": 8}
    ]
    broken["allocation"]["sub_tranches"][0]["expect_quoted_from_original_cases"] = 2
    expect(
        any("for it to be preferred over" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD quoted-from-original cases allocated to a sub-tranche with no "
        "record holding both an original and a published English are refused",
    )

    broken = json.loads(json.dumps(mix))
    del broken["allocation"]["sub_tranches"][1]["vme_quotation_cases"]
    expect(
        any("declares no vme_quotation_cases" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD a sub-tranche that declares no vme_quotation_cases is refused, "
        "because a zero it was given by default is a decision nobody made",
    )

    broken = json.loads(json.dumps(mix))
    broken["allocation"]["sub_tranches"][3]["vme_quotation_cases"] = 3
    expect(
        any("verbatim_machine_english slot(s)" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD vme quotation cases allocated over a sub-tranche's "
        "verbatim_machine_english slots are refused",
    )

    # The reading, not the plan. FINDING 40: a quota counts cases and assumes
    # the cases are the same case.
    split = split_quotation_cases(
        [("choice-case", ["a-vwp"]),
         ("resolved-only", ["b-vme"]),
         ("both", ["b-vme", "a-vwp"]),
         ("nowhere", ["c-gone"])],
        {"a-vwp": "verbatim_with_provenance",
         "b-vme": "verbatim_machine_english",
         "d-cat": "catalogue_record"},
    )
    expect(
        split["choice"] == ["choice-case", "both"]
        and split["whether_resolved"] == ["resolved-only"],
        "GUARD a quotation case is classified by the TIER OF THE RECORD it "
        "names, and one naming any record that holds a competing English asks "
        "the which-chunk question",
    )
    expect(
        split["untiered"] == [("nowhere", ["c-gone"])],
        "GUARD a quotation case naming a record this corpus does not hold is "
        "counted in neither line rather than in the flattering one",
    )

    broken = json.loads(json.dumps(mix))
    broken["allocation"]["sub_tranches"][1]["name"] = \
        broken["allocation"]["sub_tranches"][0]["name"]
    expect(
        any("each must be present and distinct" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD two sub-tranches with the same name are refused",
    )

    # Ruling 73, F5. A slot may REQUIRE a provenance of the record that fills it,
    # and the declaration has to be coherent before delivery can be judged
    # against it.
    def _slot(m, name, region, tier):
        tranche = [t for t in m["allocation"]["sub_tranches"] if t["name"] == name][0]
        return [s for s in tranche["slots"]
                if s["region"] == region and s["tier"] == tier][0]

    broken = json.loads(json.dumps(mix))
    _slot(broken, "F6", "Sub-Saharan Africa",
          "verbatim_with_provenance")["requires_provenance"] = "interesting"
    expect(
        any("not one of" in p for p in check_allocation(broken, at24, sl24)),
        "GUARD a slot requiring a provenance outside the vocabulary is refused",
    )

    broken = json.loads(json.dumps(mix))
    _slot(broken, "F7", "Southeast Asia",
          "catalogue_record")["requires_provenance"] = "local_language"
    expect(
        any("carries no source-language text" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD a provenance requirement on a tier with no source-language text is "
        "refused, because it names a field the record does not have",
    )

    broken = json.loads(json.dumps(mix))
    broken["allocation"]["sub_tranches"][0]["slots"][0]["region"] = "Antarctica"
    expect(
        any("has no target at 60" in p
            for p in check_allocation(broken, at24, sl24)),
        "GUARD a slot naming a region with no target at 60 is refused",
    )


def test_delivery():
    """F3. check_allocation guards the PLAN; this guards what was CURATED.

    The gap it closes was found by two records rather than by a check: the
    gloss-capable quota was already missed at record 26 and nothing said so,
    because the only question anyone had asked was whether the plan added up.

    OVER-DELIVERY fails, SHORTFALL is progress, and UNREACHABILITY fails --
    that last one is the whole point. A shortfall that can still be made up is
    progress; a shortfall bigger than the slots remaining is a target that has
    already failed, and the difference is what nobody would notice until F7.
    """
    print("check_delivery")
    doc = json.loads(TIERS_FILE.read_text(encoding="utf-8"))
    mix = doc["target_mix"]

    # F5. The fixtures below say "nothing has been curated yet", and the live
    # file says F3 and F4 are CLOSED with three declarations already made. Those
    # are two different states of the world, and asserting both at once is how
    # the old slot-based ceiling passed a fixture it could not have passed if
    # the two had agreed. `open_mix` is the state the labels actually describe.
    open_mix = json.loads(json.dumps(mix))
    for _t in open_mix["allocation"]["sub_tranches"]:
        _t["closed"] = False
    open_mix["gloss_capable_declared"] = []

    expect(
        not check_delivery(open_mix, {}, set()),
        "GUARD a tranche that has curated nothing yet reports no problem",
    )

    good = {"seasia-04-x": ("Southeast Asia", "verbatim_with_provenance"),
            "seasia-05-y": ("Southeast Asia", "verbatim_machine_english")}
    expect(
        not check_delivery(open_mix, good, set()),
        "GUARD records curated into cells the allocation places report nothing",
    )

    expect(
        any("places nowhere" in p for p in check_delivery(
            mix, {"x": ("Persia", "pointer_only")}, set())),
        "GUARD a record curated into a cell the allocation does not place is refused",
    )

    # Southeast Asia is allocated two verbatim_with_provenance. A third is a
    # slot taken from a cell that still expects to be filled.
    over = {f"x{i}": ("Southeast Asia", "verbatim_with_provenance")
            for i in range(3)}
    expect(
        any("Over-delivering a cell" in p for p in check_delivery(mix, over, set())),
        "GUARD a cell curated past its planned count is refused",
    )

    expect(
        any("not a record this tranche curated" in p for p in check_delivery(
            mix, good, {"nobody"})),
        "GUARD a gloss-capable declaration naming a record the tranche did not curate is refused",
    )
    expect(
        any("cannot carry a gloss case" in p for p in check_delivery(
            mix, good, {"seasia-05-y"})),
        "GUARD a gloss-capable declaration on a tier whose only English is machine is refused",
    )
    expect(
        not check_delivery(open_mix, good, {"seasia-04-x"}),
        "GUARD a gloss-capable declaration on a tier that CAN carry one reports nothing",
    )

    # The quota lowered to one, so that TWO legitimate declarations exceed it.
    # Nine real ones cannot be built against the live mix without over-
    # delivering a cell first, and a fixture that trips two rules at once
    # cannot say which of them fired.
    small = json.loads(json.dumps(mix))
    small["gloss_capable_records"] = 1
    pair = {"seasia-04-x": ("Southeast Asia", "verbatim_with_provenance"),
            "seasia-06-z": ("Southeast Asia", "verbatim_with_provenance")}
    expect(
        any("the mix asks for" in p for p in check_delivery(
            small, pair, set(pair))),
        "GUARD more gloss-capable records than the mix asks for is refused",
    )

    # The reachability clause. Every gloss-capable slot in the plan is spent on
    # records that were NOT declared gloss-capable, so the quota can no longer
    # be met however the rest of the tranche is curated.
    spent: dict = {}
    n = 0
    for tranche in mix["allocation"]["sub_tranches"]:
        for slot in tranche["slots"]:
            if slot["tier"] in GLOSS_CAPABLE_TIERS:
                for _ in range(int(slot["n"])):
                    spent[f"spent-{n}"] = (slot["region"], slot["tier"])
                    n += 1
    problems = check_delivery(mix, spent, set())
    expect(
        any("UNREACHABLE" in p for p in problems),
        "GUARD a gloss quota the remaining slots cannot carry is refused, "
        "rather than reported as a shortfall nobody acts on",
    )
    expect(
        not any("UNREACHABLE" in p for p in check_delivery(open_mix, {}, set())),
        "GUARD an empty tranche is not called unreachable — every slot is still there",
    )

    # FINDING 51's OTHER half, and the half nothing could see. Above, the slots
    # ran out. Here every slot is still there and no sub-tranche is left that
    # can declare one -- which is the state the live file was actually in while
    # three checks reported it as progress, because slots and declarations are
    # both counts of records and the sentence read correctly either way.
    starved = json.loads(json.dumps(mix))
    for _t in starved["allocation"]["sub_tranches"]:
        _t["closed"] = True
    starved["gloss_capable_declared"] = []
    expect(
        any("UNREACHABLE" in p and "declaration count is what binds" in p
            for p in check_delivery(starved, {}, set())),
        "GUARD a gloss quota no OPEN sub-tranche can still declare is refused, "
        "with the slots plentiful and the DECLARATION named as what binds",
    )

    # The shape FINDING 51 needed and did not have. A bare id names no
    # sub-tranche, so nothing can compare a sub-tranche's delivery against its
    # own declaration -- which is the blocker and the loophole in one field.
    bare = json.loads(json.dumps(mix))
    bare["gloss_capable_declared"] = ["eastasia-04-jingjiao-stele"]
    expect(
        any("bare id" in p for p in check_delivery(bare, {}, set())),
        "GUARD a gloss-capable declaration that is a bare id, naming no "
        "sub-tranche, is refused",
    )

    astray = json.loads(json.dumps(mix))
    astray["gloss_capable_declared"][0]["sub_tranche"] = "F9"
    expect(
        any("which the allocation does not place" in p
            for p in check_delivery(astray, {}, set())),
        "GUARD a declaration attributed to a sub-tranche the allocation does "
        "not place is refused",
    )

    # Ruling 62. A kind outside the vocabulary is a distinction nobody agreed
    # to, and the whole point of holding the kind in data is that the discount
    # travels with the number.
    badkind = json.loads(json.dumps(mix))
    badkind["gloss_capable_declared"][0]["kind"] = "interesting"
    expect(
        any("declares gloss kind" in p
            for p in check_delivery(badkind, {}, set())),
        "GUARD a gloss kind outside the declared vocabulary is refused",
    )

    # Ruling 73's requirement, delivered against. Sub-Saharan Africa's
    # verbatim_with_provenance cell plans three records and one of them must be
    # in a language of the region. It fails on the UNREACHABILITY shape, not the
    # shortfall one -- the distinction this whole function turns on.
    AF = ("Sub-Saharan Africa", "verbatim_with_provenance")
    two_greek = {f"af-{i}": AF for i in range(2)}
    three_greek = {f"af-{i}": AF for i in range(3)}
    greek = {f"af-{i}": "empire_language_from_the_region" for i in range(3)}

    expect(
        not any("provenance" in p for p in
                check_delivery(mix, two_greek, set(), greek)),
        "GUARD a provenance requirement with a slot still left in the cell is "
        "progress, not a failure",
    )
    expect(
        any("can no longer be met" in p for p in
            check_delivery(mix, three_greek, set(), greek)),
        "GUARD a provenance requirement is refused once the cell is FULL and no "
        "record in it satisfies the requirement",
    )
    met = dict(greek, **{"af-0": "local_language"})
    expect(
        not any("provenance" in p for p in
                check_delivery(mix, three_greek, set(), met)),
        "GUARD a full cell holding a record of the required provenance reports "
        "nothing",
    )
    expect(
        any("could not be checked" in p for p in
            check_delivery(mix, three_greek, set(), {})),
        "GUARD a record whose provenance was not supplied is REPORTED rather "
        "than counted as satisfying the requirement",
    )

    # THE CHECK THAT DID NOT EXIST. F4 planned two gloss-capable records and
    # declared two; a third attributed to it is a tranche exceeding its own
    # declaration, which is exactly how FINDING 51 says the aggregate could be
    # met one tranche at a time with every check green.
    overdeclared = json.loads(json.dumps(mix))
    overdeclared["gloss_capable_declared"].append(
        {"record": "eastasia-06-cefu-yuangui", "sub_tranche": "F4",
         "kind": "contested_reading"})
    expect(
        any("declared against 2 the sub-tranche planned" in p
            for p in check_delivery(overdeclared, {}, set())),
        "GUARD a sub-tranche declaring more gloss-capable records than it "
        "planned is refused",
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
    # CORRECTED 2026-08-31, by record 25 turning it red. This counted the LIVE
    # corpus and compared it to `measured_at_24`, which made "the corpus is 24
    # records" an invariant when it is a SNAPSHOT -- taken at digest 26e4a683
    # on the day F1 declared the policy, and the thing every target in the file
    # is arithmetic over. The first record of Block F is precisely the event
    # that was always going to break it, and nothing named it in advance the
    # way `ingest/verify.py` check 9 was named.
    #
    # The seed set is the ledger's `not_timed`: F2 defined it as the 24 records
    # excused from the column with a written reason, and check_ledger refuses a
    # record that is both timed and excused. So the histogram is counted over
    # exactly those, and it stays a fact about the corpus the policy was
    # declared over however far the corpus moves past it.
    ledger = json.loads(
        (TIERS_FILE.parent / "curation_cost.json").read_text(encoding="utf-8"))
    seed = set(ledger.get("not_timed") or {})
    actual: dict[str, int] = {t: 0 for t in RECORD_TIERS}
    for doc_id, (t, _reason) in derived.items():
        if doc_id in seed:
            actual[t] = actual.get(t, 0) + 1
    expect(
        actual == {k: int(v) for k, v in doc["measured_at_24"].items()},
        "GUARD the measured histogram the target mix is arithmetic over still holds",
    )
    expect(
        len(seed) == sum(int(v) for v in doc["measured_at_24"].values()),
        "GUARD the seed set the histogram is counted over is the 24 the "
        "declaration names, and has not grown",
    )


def test_source_language_provenance():
    """Ruling 58's owed per-region rule, in the shape FINDING 62 gave it.

    Ruling 58 asked for a rule refusing a floor met entirely in Greek or Latin.
    That rule cannot tell africa-04-silko-talmis from africa-03-periplus-adulis,
    because both are `grc` -- so it would refuse the two records ruling 58
    argued hardest to keep and admit the one it should refuse. What separates
    them is not the language but whether the region is SPEAKING or being SPOKEN
    ABOUT, and `findspot` already held it.
    """
    print("source-language provenance (ruling 58 / FINDING 62)")

    # persia-01-skz's shape: a trilingual a Persian king cut. One Greek column
    # does not make it a Roman text.
    expect(
        source_language_provenance(["xpr", "pal", "grc"], "Naqsh-e Rostam")
        == "local_language",
        "GUARD any language outside Greek and Latin makes a record LOCAL, so a "
        "trilingual is not read as an empire text for its Greek column",
    )

    # africa-04-silko-talmis: Greek, cut on a wall in the region. Ruling 58's
    # sentence -- an African using the empire's language about himself.
    expect(
        source_language_provenance(["grc"], "Temple of Mandulis, Talmis")
        == "empire_language_from_the_region",
        "GUARD Greek WITH a findspot in the region is the region speaking",
    )

    # africa-03-periplus-adulis: Greek, source_type literary_text, findspot
    # None. An Alexandrian merchant's handbook, counted as one of Sub-Saharan
    # Africa's three source-language records.
    expect(
        source_language_provenance(["grc"], None)
        == "empire_language_about_the_region",
        "GUARD Greek with NO findspot is a Roman-world text ABOUT the region, "
        "not a source from it",
    )

    # The flattering direction is the one a missing field must never take.
    expect(
        source_language_provenance([], None) != "local_language"
        and source_language_provenance(["  "], None) != "local_language",
        "GUARD an empty language list is not read as LOCAL, because a missing "
        "field must never take the flattering branch",
    )

    result = load_corpus(SEED_CORPUS_DIR)
    doc = json.loads(TIERS_FILE.read_text(encoding="utf-8"))
    declared = doc["tiers"]
    source_docs = [d for d in result.documents
                   if declared.get(d.doc_id) in SOURCE_LANGUAGE_TIERS]
    expect(
        len(source_docs) > 0,
        "the source-language records are found and counted -- a collapsed list "
        "would make the guard below vacuous",
    )
    expect(
        all([c for c in (d.language_codes or []) if str(c).strip()]
            for d in source_docs),
        "GUARD every source-language record in the corpus carries a language "
        "code, so none of them reaches the classifier's empty branch",
    )

    kinds: dict = {}
    for d in source_docs:
        k = source_language_provenance(d.language_codes, d.findspot)
        kinds[k] = kinds.get(k, 0) + 1
    by_text: dict = {}
    for d in source_docs:
        key = (d.citation_original or "").strip()
        if key:
            by_text.setdefault(key, set()).add(d.region)
    multi = sorted(len(v) for v in by_text.values() if len(v) > 1)
    print(f"  note: {len(source_docs)} source-language record(s) by provenance: "
          f"{dict(sorted(kinds.items()))}. Texts counted in more than one "
          f"region, by region count: {multi}. Counted, not gated -- ruling 73 "
          f"put the gate on the one SLOT it can close on, Sub-Saharan Africa's "
          f"verbatim_with_provenance slot in F6, rather than on a per-region "
          f"floor that would claim six other regions nobody has evidence for.")


def main() -> int:
    test_derivation()
    test_declaration_checking()
    test_paraphrase_flags()
    test_target_mix()
    test_allocation()
    test_delivery()
    test_source_language_provenance()
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
