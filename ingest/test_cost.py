"""Curation-cost ledger tests. No network, no database, no corpus edits.

Run: python -m ingest.test_cost

The suite counts its own assertions and prints the count, for the reason F1
learned on 2026-08-29: the assertion count went into five documents as 29 when
the suite had 30, because it was transcribed once and never recounted. The
suite is the only thing that knows how many assertions it has.

Guard labels are ASCII on purpose (FINDING 10's family): a label carrying an
em-dash could not be matched against its own failure line once a harness
decoded the child's stdout with the locale codec, and two harnesses printed
MISS on mutations that had worked perfectly.

`scripts/mutate_cost.py` breaks each rule in turn and confirms the guard
protecting THAT rule fires.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from .cost import (
    LEDGER_REQUIRED,
    PHASE_DEFINITIONS,
    PHASES,
    check_comparator,
    check_ledger,
    check_phase_vocabulary,
    format_report,
    record_total,
    summarise,
)
from .fidelity import derive_record_tier
from .loader import SEED_CORPUS_DIR, load_corpus

# FINDING 10: this process's own stdout. Through a pipe or a redirect on
# Windows it falls back to the locale codec, which cannot encode Greek, Tamil,
# Chinese, Ge'ez or runic, and it raises mid-output with the file half written
# and every number in it correct.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

LEDGER_FILE = Path(__file__).resolve().parent.parent / "data" / "curation_cost.json"

failures: list[str] = []
passes: list[str] = []


def expect(condition: bool, label: str) -> None:
    if condition:
        print(f"  ok   {label}")
        passes.append(label)
    else:
        print(f"  FAIL {label}")
        failures.append(label)


def fired(problems: "list[str]", *needles: str) -> bool:
    """A guard fired for the reason it exists, not merely for some reason.

    Matching on the message is deliberate. `expect_rejected` in
    eval/test_answer_eval.py takes the same care and records why: a check that
    only asserts SOMETHING failed passes when the fixture is malformed in a way
    the test did not intend, which is a green suite over a rule nobody has
    exercised.
    """
    blob = " || ".join(problems).casefold()
    return all(n.casefold() in blob for n in needles)


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

TIERS = {
    "a-01": ("verbatim_with_provenance", "cited both ways"),
    "a-02": ("catalogue_record", "a find record"),
}


def phases(**overrides) -> dict:
    out = {n: {"minutes": 10, "provenance": "measured"} for n in PHASES}
    for name, cell in overrides.items():
        if cell is None:
            out.pop(name, None)
        else:
            out[name] = cell
    return out


def entry(record_id="a-01", tier="verbatim_with_provenance",
          curated_on="2026-09-01", **overrides) -> dict:
    out = {
        "record_id": record_id,
        "tier": tier,
        "curated_on": curated_on,
        "phases": phases(),
        "note": "",
    }
    out.update(overrides)
    return out


def ledger(**overrides) -> dict:
    out = {
        "phases": dict(PHASE_DEFINITIONS),
        "comparator": {
            "evaluated_against": "within_tranche",
            "why_not_record_12": "nothing anywhere records what record 12 cost",
            "n_per_tier_at_60": {"verbatim_with_provenance": 14},
        },
        "records": [entry(), entry(record_id="a-02", tier="catalogue_record")],
        # Ruling 52. Present and empty in the fixture for the same reason it is
        # present and empty on disk: a ledger with nowhere to record a
        # retirement makes the first one a hand edit.
        "retired": [],
        "not_timed": {},
        "min_n_to_read_as_a_trend": 10,
        "max_measured_span_minutes": 240,
        "open_entry": None,
    }
    out.update(overrides)
    return out


# --------------------------------------------------------------------------
# The phase vocabulary (ruling 47)
# --------------------------------------------------------------------------

def test_phase_vocabulary():
    print("check_phase_vocabulary")

    expect(
        not check_phase_vocabulary(dict(PHASE_DEFINITIONS)),
        "GUARD the declared phase vocabulary on disk is accepted",
    )

    dropped = {k: v for k, v in PHASE_DEFINITIONS.items() if k != "rework"}
    expect(
        fired(check_phase_vocabulary(dropped), "are not this module's PHASES"),
        "GUARD a declared phase list missing a phase is refused",
    )

    reordered = {k: PHASE_DEFINITIONS[k] for k in reversed(list(PHASES))}
    expect(
        fired(check_phase_vocabulary(reordered), "in order"),
        "GUARD a declared phase list in the wrong order is refused",
    )

    blank = dict(PHASE_DEFINITIONS)
    blank["rework"] = "   "
    expect(
        fired(check_phase_vocabulary(blank), "no written definition"),
        "GUARD a phase with no written definition is refused",
    )


# --------------------------------------------------------------------------
# The comparator (ruling 46)
# --------------------------------------------------------------------------

def test_comparator():
    print("check_comparator")

    good = ledger()["comparator"]
    expect(not check_comparator(good, set()),
           "GUARD a within-tranche comparator with its n and its reason is accepted")

    bad = dict(good, evaluated_against="record_12")
    expect(
        fired(check_comparator(bad, set()), "evaluated_against", "within_tranche"),
        "GUARD a comparator evaluated against anything but within_tranche is refused",
    )

    bad = dict(good, why_not_record_12="")
    expect(
        fired(check_comparator(bad, set()), "why_not_record_12"),
        "GUARD a comparator that does not say why record 12 is unavailable is refused",
    )

    bad = dict(good, baseline="measured against southasia-01-akananuru-149")
    expect(
        fired(check_comparator(bad, {"southasia-01-akananuru-149"}),
              "names a seed record"),
        "GUARD a comparator naming a seed record as a baseline is refused",
    )

    bad = dict(good)
    bad.pop("n_per_tier_at_60")
    expect(
        fired(check_comparator(bad, set()), "n_per_tier_at_60"),
        "GUARD a comparator that does not carry the n per tier is refused",
    )


# --------------------------------------------------------------------------
# The record entries (ruling 47, ruling 48)
# --------------------------------------------------------------------------

def test_record_entries():
    print("check_ledger, record entries")

    expect(not check_ledger(ledger(), TIERS),
           "GUARD a well-formed ledger over a covered corpus reports no problem")

    bad = ledger(records=[entry(phases=phases(rework=None))])
    expect(
        fired(check_ledger(bad, {"a-01": TIERS["a-01"]}), "no entry for phase"),
        "GUARD a record entry that omits a phase is refused",
    )

    cells = phases()
    cells["reading_around"] = {"minutes": 5, "provenance": "measured"}
    bad = ledger(records=[entry(phases=cells)])
    expect(
        fired(check_ledger(bad, {"a-01": TIERS["a-01"]}), "unknown phase"),
        "GUARD a record entry with a phase outside the vocabulary is refused",
    )

    bad = ledger(records=[entry(phases=phases(
        placement={"minutes": "twenty", "provenance": "measured"}))])
    expect(
        fired(check_ledger(bad, {"a-01": TIERS["a-01"]}), "is not a number"),
        "GUARD minutes that are not a number are refused",
    )

    bad = ledger(records=[entry(phases=phases(
        placement={"minutes": -5, "provenance": "measured"}))])
    expect(
        fired(check_ledger(bad, {"a-01": TIERS["a-01"]}), "negative"),
        "GUARD negative minutes are refused",
    )

    bad = ledger(records=[entry(phases=phases(
        placement={"minutes": 5, "provenance": "guessed"}))])
    expect(
        fired(check_ledger(bad, {"a-01": TIERS["a-01"]}), "provenance"),
        "GUARD a provenance outside measured and estimated is refused",
    )

    bad = ledger(records=[entry(phases=phases(
        placement={"minutes": 5, "provenance": "estimated"}))])
    expect(
        fired(check_ledger(bad, {"a-01": TIERS["a-01"]}),
              "estimated figure with no written reason"),
        "GUARD an estimated figure with no written reason is refused",
    )

    ok = ledger(records=[entry(phases=phases(
        placement={"minutes": 5, "provenance": "estimated",
                   "because": "done in a browser away from the clock"}))])
    expect(
        not check_ledger(ok, {"a-01": TIERS["a-01"]}),
        "GUARD an estimated figure WITH a written reason is accepted",
    )

    bad = ledger(records=[entry(phases=phases(
        source_hunting={"minutes": 900, "provenance": "measured"}))])
    expect(
        fired(check_ledger(bad, {"a-01": TIERS["a-01"]}), "span limit"),
        "GUARD a measured span above the declared limit is refused",
    )

    bad = ledger(records=[entry(curated_on="September 2026")])
    expect(
        fired(check_ledger(bad, {"a-01": TIERS["a-01"]}), "curated_on"),
        "GUARD a curated_on that is not a date is refused",
    )

    bad = ledger(records=[entry(), entry()])
    expect(
        fired(check_ledger(bad, {"a-01": TIERS["a-01"]}), "timed twice"),
        "GUARD a record timed twice is refused",
    )

    bad = ledger(records=[entry(tier="catalogue_record"),
                          entry(record_id="a-02", tier="catalogue_record")])
    expect(
        fired(check_ledger(bad, TIERS), "in the ledger", "derived"),
        "GUARD a ledger tier that disagrees with the derived tier is refused",
    )


# --------------------------------------------------------------------------
# Coverage, in both directions
# --------------------------------------------------------------------------

def test_coverage():
    print("check_ledger, coverage")

    bad = ledger(records=[entry()])
    expect(
        fired(check_ledger(bad, TIERS), "neither"),
        "GUARD a corpus record that is neither timed nor excused is refused",
    )

    bad = ledger(records=[entry(), entry(record_id="a-02", tier="catalogue_record"),
                          entry(record_id="a-03", tier="catalogue_record")])
    expect(
        fired(check_ledger(bad, TIERS), "not in the corpus"),
        "GUARD a ledger row naming a record that is not in the corpus is refused",
    )

    bad = ledger(not_timed={"a-01": "curated before the column existed"})
    expect(
        fired(check_ledger(bad, TIERS), "both timed and excused"),
        "GUARD a record that is both timed and excused is refused",
    )

    bad = ledger(records=[entry(record_id="a-02", tier="catalogue_record")],
                 not_timed={"a-01": "   "})
    expect(
        fired(check_ledger(bad, TIERS), "no reason"),
        "GUARD a record excused from timing with no written reason is refused",
    )

    ok = ledger(records=[entry(record_id="a-02", tier="catalogue_record")],
                not_timed={"a-01": "curated before this column existed"})
    expect(
        not check_ledger(ok, TIERS),
        "GUARD a corpus covered by timing and excusing together is accepted",
    )

    # Found by ruling 52's own mutation, 2026-08-31. The loop below iterates
    # LEDGER_REQUIRED, so it tests the MECHANISM -- a missing term is refused --
    # and can never see a term LEAVE the set: delete one and the loop simply
    # stops testing it. That was true of all six original terms and nobody
    # could have noticed, because no mutation had ever removed one. The
    # membership is therefore declared here as well, independently, in ruling
    # 43's shape: declared in the module, declared again in the suite, and a
    # disagreement fails. It is the same lesson as "a check that greps a
    # heading passes against a report that prints the heading and no rows".
    expect(
        LEDGER_REQUIRED == {
            "phases", "comparator", "records", "retired", "not_timed",
            "min_n_to_read_as_a_trend", "max_measured_span_minutes",
        },
        "GUARD the required ledger terms are exactly the seven declared here, "
        "and a term removed from the set is refused rather than untested",
    )

    for term in sorted(LEDGER_REQUIRED):
        short = ledger()
        short.pop(term)
        if not fired(check_ledger(short, TIERS), "missing ledger term"):
            expect(False, "GUARD a ledger missing a required term is refused")
            break
    else:
        expect(True, "GUARD a ledger missing a required term is refused")


def test_the_open_clock():
    print("check_ledger, the open clock")

    bad = ledger(open_entry={"record_id": "a-01", "phase": "authoring",
                             "started_at": "2026-09-01T09:00:00Z"})
    expect(
        fired(check_ledger(bad, TIERS), "a clock is still running"),
        "GUARD a clock left running is refused, because unattributed minutes leave the column",
    )

    bad = ledger(open_entry={"record_id": "a-01", "phase": "thinking",
                             "started_at": "2026-09-01T09:00:00Z"})
    expect(
        fired(check_ledger(bad, TIERS), "unknown phase"),
        "GUARD an open clock on a phase outside the vocabulary is refused",
    )

    bad = ledger(open_entry={"record_id": "a-01", "phase": "authoring",
                             "started_at": "this morning"})
    expect(
        fired(check_ledger(bad, TIERS), "iso utc stamp"),
        "GUARD an open clock whose start is not an ISO UTC stamp is refused",
    )


# --------------------------------------------------------------------------
# The report (ruling 45, ruling 46, ruling 48)
# --------------------------------------------------------------------------

def _tranche(n: int, tier="verbatim_with_provenance", start=40, step=-2):
    """n records in the given tier, curated on consecutive days, getting
    cheaper by `step` minutes each. The trend is planted so the report can be
    asked whether it can see one."""
    rows = []
    for i in range(n):
        minutes = start + step * i
        cells = {name: {"minutes": 0, "provenance": "measured"} for name in PHASES}
        cells["authoring"] = {"minutes": minutes, "provenance": "measured"}
        rows.append({
            "record_id": f"r-{i:02d}",
            "tier": tier,
            "curated_on": f"2026-09-{i + 1:02d}",
            "phases": cells,
            "note": "",
        })
    return rows


def test_the_report():
    print("format_report")

    mix = {"by_tier_at_60": {"verbatim_with_provenance": 25}}

    small = ledger(records=_tranche(4), not_timed={})
    text = "\n".join(format_report(small, mix))
    expect("NOT A TREND (n=4, floor 10)" in text,
           "GUARD a tier below the declared floor is reported as NOT A TREND")

    big = ledger(records=_tranche(12), not_timed={})
    text = "\n".join(format_report(big, mix))
    expect("first 6 mean" in text and "last 6 mean" in text,
           "GUARD a tier at or above the floor is reported as first half against last half")
    expect("(down)" in text,
           "GUARD a planted downward trend is reported as down")

    expect(
        "NOT YET A COST CLAIM" in text and "still owed" in text,
        "GUARD per-tier means are not a cost claim while the declared mix is unmet",
    )

    met = ledger(records=_tranche(25), not_timed={})
    text = "\n".join(format_report(met, mix))
    expect(
        "declared mix is MET" in text,
        "GUARD the report says the mix is met when the tranche has met it",
    )

    text = "\n".join(format_report(ledger(records=[], not_timed={}), mix))
    expect("NO RECORD HAS BEEN TIMED YET" in text,
           "GUARD an empty column says so rather than printing a mean of nothing")

    text = "\n".join(format_report(ledger(records=_tranche(4)), {}))
    expect("MIX NOT DECLARED" in text,
           "GUARD a report handed no target mix refuses to call anything a cost claim")

    rows = _tranche(4)
    rows[0]["phases"]["rework"] = {"minutes": 30, "provenance": "estimated",
                                   "because": "remembered the next morning"}
    text = "\n".join(format_report(ledger(records=rows), mix))
    expect("estimated (" in text and "% remembered)" in text,
           "GUARD the report prints the measured/estimated split beside every mean")

    expect("by phase:" in text and "rework 30" in text,
           "GUARD the report decomposes a tier's minutes by phase")


def test_the_arithmetic():
    print("record_total and summarise")

    expect(record_total(entry()) == 10.0 * len(PHASES),
           "GUARD a record's total is the sum of every phase it declares")

    scrambled = list(reversed(_tranche(6)))
    buckets = summarise(ledger(records=scrambled))
    order = [
        r["record_id"]
        for r in buckets.get("verbatim_with_provenance", {}).get("rows", [])
    ]
    expect(bool(order) and order == sorted(order),
           "GUARD a tier's records are summarised in curation order, not file order")

    mixed = _tranche(3) + _tranche(2, tier="catalogue_record")
    buckets = summarise(ledger(records=mixed))
    expect(
        buckets.get("verbatim_with_provenance", {}).get("n") == 3
        and buckets.get("catalogue_record", {}).get("n") == 2,
        "GUARD records are counted under their own tier and not pooled",
    )


# --------------------------------------------------------------------------
# Against the file and the corpus on disk
# --------------------------------------------------------------------------

def test_against_the_live_ledger():
    print("data/curation_cost.json, against the corpus on disk")

    doc = json.loads(LEDGER_FILE.read_text(encoding="utf-8"))

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

    problems = check_ledger(doc, derived)
    if problems:
        for p in problems:
            print(f"       {p}")
    expect(not problems,
           "GUARD the ledger on disk covers every record in the corpus on disk")

    expect(
        not check_phase_vocabulary(doc.get("phases") or {}),
        "GUARD the phases declared on disk are this module's PHASES, in order",
    )

    expect(
        (doc.get("comparator") or {}).get("evaluated_against") == "within_tranche",
        "GUARD the comparator on disk is the within-tranche one ruling 46 declared",
    )

    # The column starts at record 25 and the seed 24 are excused, every one of
    # them with a written reason. If a seed record ever acquires a minutes
    # figure it was reconstructed, and a reconstructed baseline is exactly what
    # ruling 46 refuses.
    expect(
        not doc.get("records") and len(doc.get("not_timed") or {}) == len(derived),
        "GUARD every seed record is excused from the column and none is timed",
    )


def test_the_report_names_retired_rows():
    """Ruling 52. A retired row that no report mentions is a row that
    vanished, which is precisely what retirement was built not to be."""
    print("format_report, retirement")

    entry_retired = entry(record_id="z-99", tier="")
    entry_retired.update({"retired_on": "2026-08-31",
                          "because": "the hunt these minutes measured is what "
                                     "ruled the source out"})
    doc = ledger(retired=[entry_retired])
    text = "\n".join(format_report(doc, {"by_tier_at_60": {}}))
    expect("z-99" in text,
           "GUARD the report NAMES a retired row rather than subtracting it")
    expect("ruled the source out" in text,
           "GUARD the report prints the retirement's written reason")
    expect("counted in NO mean" in text,
           "GUARD the report says a retired row is in no mean, so a reader "
           "cannot take it for a timed record")

    quiet = "\n".join(format_report(ledger(), {"by_tier_at_60": {}}))
    expect("retired rows" not in quiet,
           "GUARD a ledger with nothing retired prints no retirement block")


def test_retirement():
    """Ruling 52, F3. A row whose record will never exist.

    Source hunting is the phase that DECIDES which record exists, so the clock
    cannot be started against the right id until the phase it is timing is
    over. The first record this project ever timed proved it in under three
    minutes.

    The guard that matters is the anti-loophole: a row may be retired only if
    its record is NOT in the corpus. Without it, retirement is a way to take
    the expensive records out of the column kill trigger 3 reads -- which is
    floor.json's a_named_sweep_must_actually_fail_the_rule, one file over.
    """
    print("check_ledger, retirement")

    def retired(record_id="z-99", **overrides):
        out = entry(record_id=record_id, tier="")
        out.update({"retired_on": "2026-08-31",
                    "because": "the hunt these minutes measured is what ruled "
                               "the source out"})
        out.update(overrides)
        return out

    ok = ledger(retired=[retired()])
    expect(
        not check_ledger(ok, TIERS),
        "GUARD a retired row naming a record that is not in the corpus is "
        "accepted, and is NOT counted as a stale row",
    )

    # The anti-loophole, and the only guard here that protects a number.
    bad = ledger(records=[entry(record_id="a-02", tier="catalogue_record")],
                 retired=[retired(record_id="a-01",
                                  tier="verbatim_with_provenance")])
    expect(
        fired(check_ledger(bad, TIERS), "may be retired only if"),
        "GUARD retiring a row whose record IS in the corpus is refused -- "
        "otherwise retirement takes the expensive records out of the column",
    )

    bad = ledger(retired=[retired(because="   ")])
    expect(
        fired(check_ledger(bad, TIERS), "no written reason"),
        "GUARD a retirement with no written reason is refused",
    )

    bad = ledger(retired=[retired(retired_on="last Tuesday")])
    expect(
        fired(check_ledger(bad, TIERS), "is not a date"),
        "GUARD a retired_on that is not a date is refused",
    )

    bad = ledger(retired=[retired(), retired()])
    expect(
        fired(check_ledger(bad, TIERS), "retired twice"),
        "GUARD a record retired twice is refused",
    )

    bad = ledger(retired=[retired(record_id="z-99")],
                 not_timed={"z-99": "excused"})
    expect(
        fired(check_ledger(bad, TIERS), "retired AND timed or excused"),
        "GUARD a record that is retired and also excused is refused -- one "
        "record, one answer",
    )

    # A retired row is still a row: its phases are checked, so minutes cannot
    # be laundered by retiring the entry that holds them.
    bad = ledger(retired=[retired(phases=phases(source_hunting={
        "minutes": -5, "provenance": "measured"}))])
    expect(
        fired(check_ledger(bad, TIERS), "negative"),
        "GUARD a retired row's phases are checked like any other row's",
    )

    bad = ledger(retired="not a list")
    expect(
        fired(check_ledger(bad, TIERS), "retired is not a list"),
        "GUARD a retired term that is not a list is refused",
    )


def main() -> int:
    test_phase_vocabulary()
    test_comparator()
    test_record_entries()
    test_coverage()
    test_retirement()
    test_the_report_names_retired_rows()
    test_the_open_clock()
    test_the_report()
    test_the_arithmetic()
    test_against_the_live_ledger()

    print()
    if failures:
        print(f"FAILED ({len(failures)})")
        for f in failures:
            print(f"  x {f}")
        print(f"\n{len(passes)} passed, {len(failures)} failed")
        return 1
    print(f"{len(passes)} passed, 0 failed")
    print("All curation-cost assertions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
