"""Offline checks for the Part 8 gold answer cases and their scorer.

No network, no database, no gateway. Everything is a fact about strings.

The guards that matter here protect the one decision Part 8 could get wrong in a
way nothing downstream would notice: that a case must assert what an answer
SAYS, not merely that it cited tidily. `assert grounding.ok` is the easy version
and it measures nothing — the Aksum answer refuses, contradicts the English
printed in its own evidence block, and is scored grounded. So the loader is
built to make that case impossible to write, and these tests are built to fail
if that ever stops being true.

Run:  python -m eval.test_answer_eval
"""

from __future__ import annotations

import datetime as _dt
import json
import tempfile
from pathlib import Path

from eval import answer_eval
from eval.goldset import (ANSWER_BEHAVIOURS, ANSWER_REGIONS, FLOOR_STATES,
                          GoldSetError, load_answer_cases, load_floor)

import sys

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

PASSED = 0
FAILED = 0


def expect(condition: bool, label: str) -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ok   {label}")
    else:
        FAILED += 1
        print(f"  FAIL {label}")


def expect_rejected(raw_case: dict, label: str, because: str = "") -> None:
    """A case the loader must refuse, with the reason it must refuse it.

    The label reported is always the bare label, never decorated with how it
    failed. A failure string that changes shape with the failure mode cannot be
    matched by scripts/mutate_part8.py, which is how a mutation gets recorded as
    a MISS when the guard fired correctly — that happened to five of these on
    the first run and cost more time to diagnose than the decoration saved.
    """
    detail = ""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "answer_cases.json"
        path.write_text(json.dumps({"cases": [raw_case]}), encoding="utf-8")
        try:
            load_answer_cases(path)
            ok, detail = False, "the loader ACCEPTED it"
        except GoldSetError as exc:
            ok = because.casefold() in str(exc).casefold() if because else True
            if not ok:
                detail = f"rejected, but for another reason: {exc}"
    expect(ok, label)
    if detail:
        print(f"          {detail}")


def expect_set_rejected(raw_cases: list[dict], label: str,
                        because: str = "") -> None:
    """Same contract as expect_rejected, for a rule that spans two cases.

    The pairing rules cannot be exercised one case at a time, which is the
    point of them: a discriminator is refused because of what its OTHER half
    says, or does not say, or no longer says.
    """
    detail = ""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "answer_cases.json"
        path.write_text(json.dumps({"cases": raw_cases}), encoding="utf-8")
        try:
            load_answer_cases(path)
            ok, detail = False, "the loader ACCEPTED it"
        except GoldSetError as exc:
            ok = because.casefold() in str(exc).casefold() if because else True
            if not ok:
                detail = f"rejected, but for another reason: {exc}"
    expect(ok, label)
    if detail:
        print(f"          {detail}")


def _discriminator(**b_overrides) -> list[dict]:
    """Two halves of a discriminator: one assertion block, two questions."""
    block = {
        "expected_behaviour": "answerable",
        "expect_quoted_docs": ["africa-03-periplus-adulis"],
        "expect_answer_contains": ["ivory"],
    }
    a = {"id": "half-a", "question": "the wording that refuses?", "why": "w", "region": "Arabia",
         "paired_with": "half-b", **block}
    b = {"id": "half-b", "question": "the wording that answers?", "why": "w", "region": "Arabia",
         "paired_with": "half-a", **block}
    b.update(b_overrides)
    return [a, b]


def _valid_case(**overrides) -> dict:
    case = {
        "id": "c1",
        "question": "q?",
        "why": "because",
        # Required on a case naming no document; see load_answer_cases.
        "region": "Arabia",
        # Required since D2, so every fixture below carries it. A fixture that
        # omitted it would be refused for the wrong reason, and expect_rejected
        # matches on the reason.
        "expected_behaviour": "answerable",
        "expect_answer_contains": ["ivory"],
    }
    case.update(overrides)
    return case


# --------------------------------------------------------------------------

def test_loader_rejects_the_easy_version() -> None:
    print("\nthe loader refuses a case that measures nothing")

    # GUARD, and the reason this file exists. A case asserting only that the
    # answer was grounded cannot fail a refusal, and every Aksum answer refuses.
    expect_rejected(
        {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
         "expected_behaviour": "answerable", "expect_grounded": True},
        "GUARD a case asserting only groundedness is refused",
        because="makes no assertion about what the answer says",
    )
    expect_rejected(
        {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
         "expected_behaviour": "answerable"},
        "GUARD a case asserting nothing at all is refused",
        because="makes no assertion about what the answer says",
    )
    expect_rejected(
        _valid_case(expect_answer_contains=[], expect_min_resolved_quotes=0),
        "GUARD an empty content assertion does not count as one",
        because="makes no assertion about what the answer says",
    )

    # A minimum quote count IS a content assertion — it cannot be satisfied by
    # a refusal, which is the property that matters.
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "answer_cases.json"
        path.write_text(json.dumps({"cases": [
            {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
             "expected_behaviour": "answerable",
             "expect_min_resolved_quotes": 2}
        ]}), encoding="utf-8")
        try:
            cases = load_answer_cases(path)
            expect(len(cases) == 1,
                   "a quotation floor alone is enough to make a real case")
        except GoldSetError as exc:
            expect(False, f"a quotation floor should be accepted ({exc})")


def test_loader_rejects_vacuous_assertions() -> None:
    print("\nthe loader refuses assertions that cannot fail")

    expect_rejected(
        _valid_case(expect_answer_contains_any=[[]]),
        "GUARD an empty alternatives group is refused",
        because="non-empty list",
    )
    expect_rejected(
        _valid_case(expect_answer_contains_any=[["harja", ""]]),
        "GUARD an empty string among alternatives is refused",
        because="empty string",
    )
    expect_rejected(
        _valid_case(expect_answer_contains=[""]),
        "GUARD an empty required substring is refused",
        because="vacuous",
    )
    expect_rejected(
        _valid_case(expect_answer_excludes=["  "]),
        "GUARD a whitespace-only exclusion is refused",
        because="vacuous",
    )
    expect_rejected(
        _valid_case(expect_contains=["ivory"]),
        "GUARD a misspelled assertion key is refused, not ignored",
        because="unknown key",
    )
    expect_rejected(
        _valid_case(why="   "),
        "GUARD a case with no stated reason is refused",
        because="'why' is empty",
    )
    expect_rejected(
        _valid_case(expect_min_resolved_quotes=-1),
        "GUARD a negative quotation floor is refused",
        because="zero or positive",
    )

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "answer_cases.json"
        path.write_text(json.dumps({"cases": [_valid_case(), _valid_case()]}),
                        encoding="utf-8")
        try:
            load_answer_cases(path)
            expect(False, "GUARD duplicate case ids are refused")
        except GoldSetError as exc:
            expect("duplicate" in str(exc), "GUARD duplicate case ids are refused")


def test_refusal_must_justify_itself() -> None:
    print("\ndeclaring a question unanswerable is a claim, not a default")

    expect_rejected(
        {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
         "expected_behaviour": "correctly_refusable", "expect_refusal": True,
         "expect_answer_excludes": ["150 BC"]},
        "GUARD expect_refusal with no justification is refused",
        because="refusal_is_correct_because",
    )
    expect_rejected(
        {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
         "expected_behaviour": "correctly_refusable", "expect_refusal": True,
         "refusal_is_correct_because": "not in corpus",
         "expect_answer_contains": ["ivory"]},
        "GUARD a case cannot demand both a refusal and content",
        because="refuse and speak",
    )
    expect_rejected(
        {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
         "expected_behaviour": "correctly_refusable", "expect_refusal": True,
         "refusal_is_correct_because": "not in corpus",
         "expect_min_resolved_quotes": 1},
        "GUARD a refusal case cannot demand resolved quotations",
        because="refuse and speak",
    )
    expect_rejected(
        _valid_case(refusal_is_correct_because="not in corpus"),
        "GUARD a justification with no expect_refusal is refused",
        because="not in force",
    )


def test_the_real_gold_set_loads() -> None:
    print("\nthe gold set on disk")

    cases = load_answer_cases()
    expect(len(cases) >= 5, f"{len(cases)} cases load")
    ids = {c.id for c in cases}
    for wanted in ("aksum-exports", "vimose-runes", "antikythera-absent"):
        expect(wanted in ids, f"{wanted} is present")

    # G4 wants >= 30 cases balanced across the three behaviours. The count is
    # D3's business; that all three arms exist at all is checked from here on,
    # so a gold set that grows into one shape is visible while it is happening.
    behaviours: dict[str, list[str]] = {}
    for case in cases:
        expect(case.expected_behaviour in ANSWER_BEHAVIOURS,
               f"{case.id}: declares {case.expected_behaviour!r}")
        behaviours.setdefault(case.expected_behaviour, []).append(case.id)
    for behaviour in ANSWER_BEHAVIOURS:
        held = behaviours.get(behaviour, [])
        expect(bool(held),
               f"the gold set exercises {behaviour} ({len(held)} case(s))")

    # G4: ">=30 cases meeting the stratification" - >=3 per region across seven
    # regions, >=6 source languages. The count is done here rather than left as
    # a claim in a document, because a gate checked against prose is a gate
    # checked against whoever wrote the prose.
    per_region: dict[str, int] = {}
    for case in cases:
        expect(case.region in ANSWER_REGIONS,
               f"{case.id}: declares region {case.region!r}")
        per_region[case.region] = per_region.get(case.region, 0) + 1
    for region in ANSWER_REGIONS:
        if region == "outside":
            continue
        held = per_region.get(region, 0)
        expect(held >= 3, f"{region}: {held} case(s), G4 wants >= 3")

    by_id = {c.id: c for c in cases}
    expect(by_id["aksum-exports"].paired_with == "adulis-exports"
           and by_id["adulis-exports"].paired_with == "aksum-exports",
           "GUARD the Adulis discriminator is paired from both ends")

    # Every case must be able to fail a refusal, or it is not testing the
    # failure mode Part 8 was created to measure. The one exception declares
    # itself and says why.
    for case in cases:
        if case.expect_refusal:
            expect(bool(case.refusal_is_correct_because.strip()),
                   f"{case.id}: the refusal is justified in the file")
            continue
        can_fail_refusal = (
            case.expect_answer_contains
            or case.expect_answer_contains_any
            or case.expect_min_resolved_quotes > 0
            or any(answer_eval.is_refusal(s) for s in case.expect_answer_excludes)
        )
        expect(can_fail_refusal,
               f"GUARD {case.id}: a refusal cannot satisfy this case")


def test_expected_behaviour_is_declared() -> None:
    print("\nevery case declares what it expects, and nothing infers it")

    # The rule TASK 2 is built around. A default here would silently relabel
    # every case nobody thought about, and the label is what says whether a red
    # line means retrieval broke, the model invented something, or a machine
    # translation appeared attached to a citation.
    expect_rejected(
        {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
         "expect_answer_contains": ["ivory"]},
        "GUARD a case with no expected_behaviour is refused",
        because="expected_behaviour",
    )
    expect_rejected(
        _valid_case(expected_behaviour="probably_fine"),
        "GUARD an unrecognised expected_behaviour is refused",
        because="is not one of",
    )

    # Two clauses, two guards. Only the assertion is scored, so a label that
    # disagrees with it files the case under a behaviour it does not test.
    expect_rejected(
        _valid_case(expected_behaviour="correctly_refusable"),
        "GUARD a refusable label with no expect_refusal is refused",
        because="expect_refusal is not true",
    )
    expect_rejected(
        {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
         "expected_behaviour": "answerable", "expect_refusal": True,
         "refusal_is_correct_because": "not in corpus",
         "expect_answer_excludes": ["150 BC"]},
        "GUARD an expect_refusal filed under another label is refused",
        because="whatever the label says",
    )

    # A refusal contains none of the strings a case excludes, so a case built
    # from exclusions alone is passed by silence.
    expect_rejected(
        {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
         "expected_behaviour": "answerable",
         "expect_answer_excludes": [
             "The sources retrieved do not answer this question"]},
        "GUARD a speaking case built only from exclusions is refused",
        because="meant to speak",
    )


def test_the_gloss_arm_has_teeth() -> None:
    print("\nrefusable_with_gloss: show the published gloss, and hedge it")

    expect_rejected(
        {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
         "expected_behaviour": "refusable_with_gloss",
         "expect_answer_contains": ["harja"],
         "expect_hedge_any": [["likely", "uncertain"]]},
        "GUARD a gloss case with no quoted document is refused",
        because="published gloss",
    )
    # The hedge is the whole assertion on this arm: a confident English
    # rendering of a partly undeciphered runic sequence is the worst output
    # this system can produce, because it arrives attached to a citation.
    expect_rejected(
        {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
         "expected_behaviour": "refusable_with_gloss",
         "expect_quoted_docs": ["scandinavia-03-vimose"],
         "expect_answer_contains": ["harja"]},
        "GUARD a gloss case with no declared hedge is refused",
        because="hedge IS the assertion",
    )
    expect_rejected(
        _valid_case(expect_hedge_any=[["likely"]]),
        "GUARD a hedge on a non-gloss case is refused",
        because="belongs to",
    )
    expect_rejected(
        {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
         "expected_behaviour": "refusable_with_gloss",
         "expect_quoted_docs": ["scandinavia-03-vimose"],
         "expect_hedge_any": [[]]},
        "GUARD an empty hedge group is refused like any other",
        because="non-empty list",
    )

    # The hedge is merged into the scored alternatives, so declaring it changes
    # where the rule is enforced and nothing about what is measured.
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "answer_cases.json"
        path.write_text(json.dumps({"cases": [
            {"id": "c1", "question": "q?", "why": "w", "region": "Arabia",
             "expected_behaviour": "refusable_with_gloss",
             "expect_quoted_docs": ["scandinavia-03-vimose"],
             "expect_answer_contains_any": [["harja"]],
             "expect_hedge_any": [["likely", "uncertain"]]}
        ]}), encoding="utf-8")
        try:
            case = load_answer_cases(path)[0]
            expect(case.expect_answer_contains_any
                   == [["harja"], ["likely", "uncertain"]],
                   "the declared hedge is scored as one more alternatives group")
            expect(case.expect_hedge_any == [["likely", "uncertain"]],
                   "and is still readable as the hedge it was declared as")
        except GoldSetError as exc:
            expect(False, f"a well-formed gloss case should load ({exc})")


def test_every_entry_point_guards_its_stdout() -> None:
    print("\nFINDING 10: the stdout guard, in every entry point that prints")

    # This check lives in a file about gold answer cases on purpose. The failure
    # it prevents is THIS SUITE dying instead of failing: it prints failure
    # detail carrying Greek, Tamil, Chinese, Ge'ez and runic, and redirected on
    # Windows that raises rather than degrades. A suite that can be killed by its
    # own output is not a suite.
    #
    # The guard is inlined in every entry point rather than shared, because
    # ui/build_ui_data.py documents `python ui/build_ui_data.py` as an
    # invocation and under that form the repository root is not on sys.path — a
    # helper module would be unimportable for exactly the file that found the
    # defect.
    #
    # THERE IS NO LIST HERE, and that is the point. A hand-written enumeration of
    # entry points was wrong four times in one afternoon: 7, then 20, then 22,
    # then 43. Twice from typing it out, and once because it was verified against
    # a partial copy of the repository rather than the repository. The rule is
    # "every file with a __main__", so the rule is what gets asserted. A list
    # that has to be maintained is a list that will be wrong again.
    root = Path(__file__).resolve().parent.parent
    marker = "FINDING 10: this process's own stdout."
    entry_points = sorted(
        p for d in ("ui", "eval", "answer", "ingest", "scripts")
        for p in (root / d).glob("*.py")
        if "__main__" in p.read_text(encoding="utf-8")
    )
    expect(len(entry_points) >= 40,
           f"{len(entry_points)} entry points found — if this collapsed, the "
           f"glob stopped matching and the check below passes vacuously")
    missing = sorted(
        str(p.relative_to(root)).replace("\\", "/")
        for p in entry_points
        if marker not in p.read_text(encoding="utf-8")
    )
    expect(not missing,
           f"GUARD every entry point carries the stdout guard "
           f"({len(entry_points)} found)"
           + (f" — missing from {missing}" if missing else ""))


def test_the_source_text_can_be_required() -> None:
    print("\nFINDING 13: quoting a record and quoting its LANGUAGE are two claims")

    payload = _payload(
        "The Weilue says Da Qin has more than four hundred cities. [S1]",
        grounded=True,
    )
    payload["passages"] = [{"marker": "S1", "doc_id": "eastasia-01-weilue"}]

    def spans(*fields):
        return [{"marker": "S1", "doc_id": "eastasia-01-weilue",
                 "abs_start": 0, "abs_end": 10, "source_field": f} for f in fields]

    case = {
        "id": "c1", "question": "q?", "why": "w",
        "expected_behaviour": "answerable", "region": "East Asia",
        "expect_quoted_docs": ["eastasia-01-weilue"],
        "expect_quoted_from_original": ["eastasia-01-weilue"],
        "expect_answer_contains": ["four hundred"],
    }

    def score(fields):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "answer_cases.json"
            path.write_text(json.dumps({"cases": [case]}), encoding="utf-8")
            loaded = load_answer_cases(path)[0]
        payload["grounding"]["quote_spans"] = spans(*fields)
        return answer_eval.score_payload(loaded, payload)

    # The exact shape of every archived Weilue answer: the record IS quoted, and
    # the quotation is the English. expect_quoted_docs passes; this must not.
    only_english = score(["reference_translation"])
    expect(not only_english.ok,
           "GUARD quoting only the translation FAILS a source-text case")
    named = " ".join(a.detail for a in only_english.assertions if not a.ok)
    expect("no source-text field" in named,
           "the failure names WHY: no quotation came from the source text")
    expect(any(a.ok and "quotes eastasia-01-weilue, resolving" in a.label
               for a in only_english.assertions),
           "GUARD the weaker expect_quoted_docs still passes on the same payload "
           "— which is the whole reason the new key exists")

    expect(score(["original_text_excerpt"]).ok,
           "a quotation from the source text satisfies it")
    expect(score(["reference_translation", "original_text_excerpt"]).ok,
           "quoting both satisfies it — the case asks for the source text, not "
           "for the absence of English")


def test_a_discriminator_loads_as_one_instrument() -> None:
    print("\nthe pairing is a load-time rule, not a note")

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "answer_cases.json"
        path.write_text(json.dumps({"cases": _discriminator()}),
                        encoding="utf-8")
        try:
            pair = load_answer_cases(path)
            expect(len(pair) == 2 and pair[0].paired_with == "half-b",
                   "a symmetric pair with identical assertions loads")
        except GoldSetError as exc:
            expect(False, f"a well-formed pair should load ({exc})")

    expect_set_rejected(
        [dict(_discriminator()[0], paired_with="half-a")],
        "GUARD a paired case naming itself is refused",
        because="names the case itself",
    )
    # Deleting one half is the failure this replaces prose with: half a
    # discriminator measures nothing and reads exactly like a whole one.
    expect_set_rejected(
        [_discriminator()[0]],
        "GUARD a paired case whose partner is absent is refused",
        because="which is not in",
    )
    expect_set_rejected(
        _discriminator(paired_with=""),
        "GUARD an asymmetric pairing is refused",
        because="not symmetric",
    )
    # The one the handoff singles out: if the two blocks drift the pair stops
    # discriminating between two questions and starts discriminating between
    # two tests.
    expect_set_rejected(
        _discriminator(expect_answer_contains=["ivory", "rhinoceros"]),
        "GUARD paired cases whose assertions differ are refused",
        because="differ on",
    )
    expect_set_rejected(
        _discriminator(expected_behaviour="refusable_with_gloss",
                       expect_hedge_any=[["likely"]]),
        "GUARD a pair relabelled on one side only is refused",
        because="differ on",
    )


def test_the_stratification_is_computable() -> None:
    print("\nG4 counts cases per region, so every case must be attributable")

    expect_rejected(
        _valid_case(region="Mesopotamia"),
        "GUARD an unrecognised region is refused",
        because="is not one of",
    )
    # The eight refusal cases name no document, because expect_quoted_docs is
    # refused on a refusal - so nothing can be looked up and the case must say.
    expect_rejected(
        {"id": "c1", "question": "q?", "why": "no document named here",
         "expected_behaviour": "answerable",
         "expect_answer_contains": ["ivory"]},
        "GUARD a case naming no document must declare a region",
        because="must declare one",
    )
    # A case that names a document does not have to: the region is derivable
    # from the doc id, and requiring it anyway would be a second place for the
    # same fact to be wrong.
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "answer_cases.json"
        path.write_text(json.dumps({"cases": [
            {"id": "c1", "question": "q?", "why": "names a document",
             "expected_behaviour": "answerable",
             "expect_quoted_docs": ["africa-03-periplus-adulis"],
             "expect_answer_contains": ["ivory"]}
        ]}), encoding="utf-8")
        try:
            case = load_answer_cases(path)[0]
            expect(case.region == "",
                   "a case naming a document may leave region derivable")
        except GoldSetError as exc:
            expect(False, f"a doc-bearing case should load without region ({exc})")


def test_matching_tolerances() -> None:
    print("\nmatching")

    expect(answer_eval.contains("Ivory and TORTOISE-shell", "ivory"),
           "matching is case-insensitive")
    expect(answer_eval.contains("ivory,\n  and  tortoise", "ivory, and tortoise"),
           "matching collapses whitespace, including newlines")
    expect(not answer_eval.contains("tortoise shell", "tortoise-shell"),
           "GUARD matching is NOT punctuation-insensitive — a case must say "
           "which spelling it accepts rather than let the matcher decide")
    expect(answer_eval.is_refusal(
        "The sources retrieved do not answer this question. But..."),
        "the refusal sentence is recognised")
    expect(answer_eval.is_refusal(
        "the sources retrieved do not answer this question"),
        "recognised without its full stop and case, as assemble.refused does")
    expect(not answer_eval.is_refusal("The sources describe Roman trade"),
           "an ordinary answer is not read as a refusal")


def _payload(answer: str, *, grounded: bool, quotes: int = 0,
             docs: tuple[str, ...] = ("africa-03-periplus-adulis",)) -> dict:
    return {
        "question": "What did Rome trade with the Kingdom of Aksum?",
        "answer": answer,
        "grounded": grounded,
        "prompt_version": "test",
        # Spans carry their marker, because that is how a quotation is traced
        # back to the document it came from. Written without one at first, which
        # made every quotation belong to no document and quietly failed
        # expect_quoted_docs on answers that should pass.
        "grounding": {"quote_spans": [
            {"marker": "S1", "abs_start": i, "abs_end": i + 5}
            for i in range(quotes)
        ]},
        "passages": [
            {"marker": f"S{i+1}", "doc_id": doc, "chunk_id": f"{doc}::original::000",
             "cited": True}
            for i, doc in enumerate(docs)
        ],
    }


def test_the_aksum_answer_fails() -> None:
    print("\nthe case that had to fail")

    cases = {c.id: c for c in load_answer_cases()}
    aksum = cases["aksum-exports"]

    # The live v3 answer, verbatim from eval/answer_runs/. Scored `grounded` by
    # the Part 7 checks while stating the opposite of its own cited evidence.
    graded = answer_eval.score_payload(aksum, _payload(
        "The sources retrieved do not answer this question. The sources describe "
        "Roman trade with Aksum (the Kingdom of Zoskales) in the Periplus of the "
        "Erythraean Sea, but they detail what Rome exported to Aksum rather than "
        "what Rome imported from it [S1].",
        grounded=True,
    ))
    expect(not graded.ok,
           "GUARD the grounded Aksum refusal FAILS its content case")
    expect(graded.grounded is True,
           "and it is still reported as grounded — the metrics disagree, which "
           "is the finding, not an error")
    labels = " ".join(a.label for a in graded.failures)
    expect("ivory" in labels and "rhinoceros" in labels,
           "the failure names the content the corpus contains and the answer omits")

    # An answer that uses the evidence passes.
    good = answer_eval.score_payload(aksum, _payload(
        'The Periplus records that "There are exported from these places ivory, '
        'and tortoise-shell and rhinoceros-horn" [S1].',
        grounded=True, quotes=1,
    ))
    expect(good.ok, "an answer that uses the evidence passes")

    # GUARD (added after mutation): removing the quotation floor broke no test,
    # because every archived failure already failed on content. So the floor had
    # no guard pinning it and could have been deleted silently. An answer can say
    # all the right words without quoting anything — a paraphrase with a citation
    # attached — and the whole Part 7 claim is that quotations land on characters
    # that exist.
    unquoted = answer_eval.score_payload(aksum, _payload(
        "The Periplus records that ivory, tortoise-shell and rhinoceros-horn "
        "were exported from these places [S1].",
        grounded=True, quotes=0,
    ))
    expect(not unquoted.ok,
           "GUARD content with no resolved quotation still fails the case")
    expect(any("resolves at least" in a.label for a in unquoted.failures),
           "the failure names the missing quotation, not the content")


def test_content_from_the_wrong_document() -> None:
    print("\nthe hole a dry run found")

    cases = {c.id: c for c in load_answer_cases()}
    aksum = cases["aksum-exports"]

    # The live evidence set for this question carries `ivory` and
    # `tortoise-shell` in the Muziris passage and `rhinoceros` in the Hou
    # Hanshu. So every content term is satisfiable without ever using the Aksum
    # record — an answer about India and China that names the Aksum document
    # once. Under expect_cited_docs alone that passed.
    payload = {
        "question": aksum.question,
        "answer": ("Ships carried ivory and tortoise-shell from the Indian coast "
                   "[S3], and a Chinese record lists rhinoceros horn [S6]. The "
                   "Periplus also describes Adulis [S1]."),
        "grounded": True,
        "prompt_version": "test",
        "grounding": {"quote_spans": [
            {"marker": "S3", "abs_start": 10, "abs_end": 20},
            {"marker": "S6", "abs_start": 30, "abs_end": 40},
        ]},
        "passages": [
            {"marker": "S1", "doc_id": "africa-03-periplus-adulis",
             "chunk_id": "africa-03-periplus-adulis::original::002", "cited": True},
            {"marker": "S3", "doc_id": "southasia-02-periplus-muziris",
             "chunk_id": "southasia-02-periplus-muziris::original::003", "cited": True},
            {"marker": "S6", "doc_id": "eastasia-02-hou-hanshu",
             "chunk_id": "eastasia-02-hou-hanshu::original::000", "cited": True},
        ],
    }
    result = answer_eval.score_payload(aksum, payload)
    expect(not result.ok,
           "GUARD content drawn from the wrong document fails the case")
    expect(any("quotes africa-03-periplus-adulis" in a.label
               for a in result.failures),
           "the failure names the document that was cited but never quoted")

    # And the same answer with a resolved quotation from the Aksum record passes.
    payload["grounding"]["quote_spans"].append(
        {"marker": "S1", "abs_start": 3073, "abs_end": 3156})
    expect(answer_eval.score_payload(aksum, payload).ok,
           "quoting the record that carries the answer satisfies it")


def test_the_live_payload_shape() -> None:
    print("\nthe shape a live run actually produces")

    # GUARD, and the most expensive lesson in Part 8. The scorer was written
    # against recovered archives, which carry `cited` per passage because
    # answer_citations stores that column. A LIVE payload is Passage.to_dict(),
    # which does not — whether a passage was cited is a property of the answer,
    # not of the passage. Filtering on `p.get("cited")` therefore found nothing
    # in every live run, and four content cases failed on expect_cited_docs while
    # the answers were fine. Thirty chat calls to learn that the scorer had never
    # been run against the thing it exists to score.
    from answer.evidence import Passage, EnglishChoice
    from answer.evidence import ChunkRecord

    record = ChunkRecord(
        chunk_id="southasia-02-periplus-muziris::original::003",
        doc_id="southasia-02-periplus-muziris", role="original", seq=3,
        lang="grc", text="pepper", citation="Periplus 56", region="South Asia",
        source_type="literary", text_fidelity="verbatim_original",
        source_field="original_text_excerpt", char_start=0, char_end=6,
    )
    passage = Passage(
        marker="S1", chunk=record,
        english=EnglishChoice(kind="published", text="pepper from Cottonara",
                              ground="section"),
        similarity=0.5, rank=1,
    )
    live_passage = passage.to_dict()

    expect("cited" not in live_passage,
           "GUARD Passage.to_dict() carries no `cited` key — the scorer must "
           "not assume one")
    expect(live_passage.get("doc_id") == record.doc_id,
           "a live passage does carry its doc_id")
    expect(live_passage.get("marker") == "S1",
           "a live passage carries its marker, which is how a quote span finds "
           "its document")

    cases = {c.id: c for c in load_answer_cases()}
    muziris = cases["muziris-cargo"]
    live_payload = {
        "question": muziris.question,
        "answer": ('Ships carried "pepper, which is produced in quantity in only '
                   'one region near these markets, a district called Cottonara" '
                   '[S1], with pearls and ivory also exported [S1].'),
        "grounded": True,
        "prompt_version": "p7-answer-v4",
        "grounding": {
            "cited_markers": ["S1"],
            "quote_spans": [
                {"marker": "S1", "abs_start": 100, "abs_end": 180},
                {"marker": "S1", "abs_start": 200, "abs_end": 260},
                {"marker": "S1", "abs_start": 300, "abs_end": 340},
            ],
        },
        "passages": [live_passage],
    }
    result = answer_eval.score_payload(muziris, live_payload)
    expect(result.ok,
           "GUARD a good answer in the LIVE payload shape passes — this is the "
           "case that failed 0/3 across two prompt versions")
    expect(not any("cites" in a.label for a in result.failures),
           "expect_cited_docs is satisfied from grounding.cited_markers when "
           "the passage does not state it")

    # And the fallback must not become a way to pass without citing anything.
    uncited = dict(live_payload)
    uncited["grounding"] = {**live_payload["grounding"], "cited_markers": []}
    expect(not answer_eval.score_payload(muziris, uncited).ok,
           "GUARD an answer citing nothing still fails, fallback or not")


def test_a_refusal_case_is_not_passed_by_verbosity() -> None:
    print("\nthe control case")

    cases = {c.id: c for c in load_answer_cases()}
    antikythera = cases["antikythera-absent"]

    payload = _payload("The sources retrieved do not answer this question. The "
                       "sources discuss Roman contact with regions beyond the "
                       "Mediterranean [S1].", grounded=True)
    payload["question"] = antikythera.question
    expect(answer_eval.score_payload(antikythera, payload).ok,
           "a correct refusal passes")

    invented = dict(payload)
    invented["answer"] = ("The Antikythera mechanism was built in the second "
                          "century BC [S1].")
    result = answer_eval.score_payload(antikythera, invented)
    expect(not result.ok,
           "GUARD an invented date fails the case even though it says more")
    expect(any("refuses" in a.label for a in result.failures),
           "the failure names the missing refusal")


def test_scoring_an_archive() -> None:
    print("\nscoring the archives")

    cases = load_answer_cases()
    results, unmatched = answer_eval.score_archives(cases)

    # Was `== 16`, which broke the moment the first sweep archived 30 more runs.
    # The property is that every archived run is scorable, not that there is a
    # particular number of them — a count assertion in a directory designed to
    # grow is a test with an expiry date.
    #
    # These three stay over the WHOLE directory: every run must be scorable and
    # matched whatever arm made it. The per-case universals below must not.
    archives = answer_eval.load_archives()
    expect(len(results) == len(archives),
           f"every archived run is scored ({len(results)} of {len(archives)})")
    expect(len(results) >= 16,
           f"the 16 recovered Part 7 answers are still among them "
           f"({len(results)})")
    expect(not unmatched, f"every archived question has a gold case {unmatched}")

    # 2026-08-28. `eval/answer_runs/` POOLS ARMS, and the comment above has a
    # second half it did not know about: a directory designed to grow is also a
    # directory that grows SIDEWAYS. Ruling 36 split the sweep file — eval/arms/
    # against eval/sweeps/ — and left the per-run archive as one directory,
    # because rescore_sweep rebuilds a summary from these files. So the sonnet
    # arm's 165 runs landed here beside 511 greedy ones, and every universal
    # below became a claim about two models rather than about the archive it
    # was written for.
    #
    # `all(not r.ok for r in by_case["aksum-exports"])` is the one that fired:
    # the arm passed that case once in five, and the guard reported the arm's
    # RESULT as a broken guard. Nothing about that was subtle, and it was only
    # not subtle because the arm ran. Until today the filter would have been
    # invisible and unnecessary and every one of these assertions would have
    # been silently narrowed by the next arm that ran.
    greedy, foreign = answer_eval.archives_on_arm(
        archives, {"model_alias": answer_eval.LEGACY_ARM_ALIAS,
                   "temperature": answer_eval.LEGACY_ARM_TEMPERATURE})
    # The counts go in their OWN line and not into the guard text. A guard
    # named by `scripts/mutate_part8.py` is matched as an exact string, so a
    # guard whose wording carries a number it computes is a guard the harness
    # stops being able to name the moment a mutation changes that number.
    expect(len(greedy) + len(foreign) == len(archives),
           f"{len(greedy)} archived run(s) on the greedy arm and "
           f"{len(foreign)} on another — every run is on exactly one")
    expect(bool(foreign),
           "GUARD the arm filter EXCLUDES something — a filter matching "
           "everything would leave every universal below a claim about two "
           "models")
    expect(len(greedy) >= 511,
           "GUARD and it KEEPS the greedy archive — a filter matching nothing "
           "would make every universal below vacuously true")
    # The THREE STATES, and why the third mutation on this code found nothing
    # to break until this line existed. Ignoring a recorded `model_alias` sends
    # payload_arm to the serving-stack echo, and for the arm's 165 runs that
    # echo says `chat-strong` too — so the filter still excluded them, every
    # universal below still held, and a genuinely broken reading reported as a
    # working guard. The echo AGREEING is exactly what makes it useless as a
    # check on the reading. Ruling 36's whole argument, one level down: a
    # reconstruction that agrees is still not a reading, and the difference has
    # to be assertable or it is not recorded at all.
    expect(all(answer_eval.payload_arm(p)["basis"] == "recorded"
               for p, _ in foreign),
           "GUARD a run that RECORDS its arm is READ FROM THE ROW, never "
           "reconstructed from the serving-stack echo — an echo that agrees "
           "is still not a reading")
    bases = {answer_eval.payload_arm(p)["basis"] for p, _ in greedy}
    expect(bases == {"reconstructed", "assumed"},
           f"and the greedy archive is known two ways, both named: {sorted(bases)} "
           f"— the echo where there is one, and the code argument where there "
           f"is not")
    results, unmatched = answer_eval.score_archives(cases, archives=greedy)

    by_case: dict[str, list] = {}
    for result in results:
        by_case.setdefault(result.case_id, []).append(result)

    def runs(case_id: str, version: str) -> list:
        return [r for r in by_case[case_id] if r.prompt_version == version]

    expect(all(not r.ok for r in by_case["aksum-exports"]),
           "GUARD every archived Aksum answer ON THE GREEDY ARM fails — "
           "including those the Part 7 checks called grounded")

    # Case zero, asserted per run rather than per version: there are now several
    # runs under some versions, and a dict keyed on version would silently keep
    # only the last one.
    v2 = runs("vimose-runes", "p7-answer-v2")
    expect(v2 and all(r.ok for r in v2),
           "case zero: every v2 run passes, having produced the sequences and "
           "the hedges")
    retreats = runs("vimose-runes", "p7-answer-v1") + runs("vimose-runes",
                                                           "p7-answer-v3")
    expect(retreats and all(not r.ok for r in retreats),
           "case zero: every v1 and v3 run fails, having retreated")

    chinese_v123 = [r for r in by_case["chinese-da-qin"]
                    if r.prompt_version in ("p7-answer-v1", "p7-answer-v2",
                                            "p7-answer-v3")]
    expect(chinese_v123 and all(r.ok for r in chinese_v123),
           "the archived Chinese answers pass on content while scored not "
           "grounded — the disagreement pointing the other way")


def test_a_duplicate_question_cannot_shadow_a_case() -> None:
    """A case that never runs, in a gold set that counts it.

    `match_case` returned the FIRST case whose question matched. A second case
    asking the same question was therefore never scored against any archive,
    while still counting toward the 33 and toward the per-region tally G4 is
    checked on. Avoided by hand in `weilue-chinese-quotation`; unguarded until
    D4. Same family as FINDING 12 and quieter than it — Finding 12 at least
    moved the numbers.
    """
    print("\na duplicate question cannot shadow a case")

    import inspect

    from eval import goldset

    expect_set_rejected(
        [_valid_case(id="first", question="What was exported from Adulis?"),
         _valid_case(id="second", question="What was exported from Adulis?")],
        "GUARD two cases asking the same question are refused",
        because="asks the same question",
    )

    # Refusing only byte-identical questions would be a guard that looks
    # complete: the matcher collapses whitespace and folds case, so these two
    # shadow each other exactly as a byte-identical pair does.
    expect_set_rejected(
        [_valid_case(id="first", question="What was exported from Adulis?"),
         _valid_case(id="second", question="what  was exported   from adulis?")],
        "GUARD two questions differing only in spacing and case are refused",
        because="asks the same question",
    )

    # The loader guards the gold FILE. This guards every other route in — a
    # hand-built list, a filtered subset, two files concatenated. Either alone
    # leaves the other door open.
    twins = [
        goldset.AnswerCase(id="a", question="Who?", why="w",
                           expected_behaviour="answerable"),
        goldset.AnswerCase(id="b", question="who?", why="w",
                           expected_behaviour="answerable"),
    ]
    try:
        answer_eval.match_case(twins, {"question": "Who?"})
        refused = False
    except GoldSetError as exc:
        refused = "cannot pick one" in str(exc)
    expect(refused, "GUARD match_case refuses to choose between two cases")

    one = [goldset.AnswerCase(id="a", question="Who ruled?", why="w",
                              expected_behaviour="answerable")]
    expect(answer_eval.match_case(one, {"question": "  WHO   RULED? "}) is not None,
           "match_case still matches one case across spacing and case")
    expect(answer_eval.match_case(one, {"question": "who else?"}) is None,
           "a question no case asks still matches nothing")

    # The rule that ADMITS a case and the rule that FINDS it have to be one
    # rule. A matcher with its own copy could recognise a duplicate the loader
    # did not, which puts the shadowed case back with nothing saying so — the
    # argument answer_eval already makes for importing REFUSAL_SENTENCE rather
    # than copying it. Asserted against the source, because two functions that
    # agree today are not the same function.
    source = inspect.getsource(answer_eval.match_case)
    expect("question_key(" in source,
           "GUARD match_case matches on the loader's key, not a copy of it")


def test_the_floor() -> None:
    print("\nthe hard floor")

    floor = load_floor()
    expect(bool(floor["required_cases"]), "the floor names required cases")
    expect(floor["min_repetitions"] >= 3,
           "the floor cannot be checked against a single shot")

    ids = {c.id for c in load_answer_cases()}
    for case_id in floor["required_cases"]:
        expect(case_id in ids, f"required case {case_id} exists in the gold set")
    for case_id in floor.get("known_failing_cases", {}):
        expect(case_id in ids, f"known-failing case {case_id} exists")

    # GUARD: a known failure is tracked, never subtracted. If aksum-exports could
    # be listed as required AND known-failing, the floor would pass by declaring
    # its own failure acceptable, which is how an exemption becomes permanent.
    overlap = set(floor["required_cases"]) & set(
        floor.get("known_failing_cases", {}))
    expect(not overlap,
           "GUARD no case is both required and known-failing")

    def summary(content_pass, n, refusal, unstable=0):
        return {
            "cells": [{"case": c, "prompt_version": "v", "n": n,
                       "content_pass": content_pass.get(c, n),
                       "content_stable": True, "grounded_pass": n,
                       "grounded_stable": True, "distinct_texts": 1,
                       "quotes_min": 1, "quotes_max": 1,
                       "refusal_rate": refusal}
                      for c in ids],
            "by_version": {"v": {"cases": len(ids), "runs": n * len(ids),
                                 "content_pass_rate": 1.0, "grounded_rate": 1.0,
                                 "refusal_rate": refusal,
                                 "unstable_content_cells": unstable,
                                 "unstable_grounded_cells": 0,
                                 "mean_resolved_quotes": 3.0}},
        }

    good = answer_eval.check_floor(summary({}, 3, 0.2), floor, 3)["v"]
    expect(good["meets_floor"], "a clean sweep meets the floor")

    # One required case failing once is enough to miss it: the floor is per case
    # and per repetition, not an average. An average lets a total failure on one
    # question be paid for by successes on others.
    partial = answer_eval.check_floor(
        summary({floor["required_cases"][0]: 2}, 3, 0.2), floor, 3)["v"]
    expect(not partial["meets_floor"],
           "GUARD a required case passing 2 of 3 misses the floor")

    loud = answer_eval.check_floor(summary({}, 3, 0.9), floor, 3)["v"]
    expect(not loud["meets_floor"],
           "GUARD a high refusal rate misses the floor even when content passes")

    unrepeated = answer_eval.check_floor(summary({}, 1, 0.2), floor, 1)["v"]
    expect(not unrepeated["meets_floor"],
           "GUARD an unrepeated sweep cannot meet the floor")

    unstable = answer_eval.check_floor(summary({}, 3, 0.2, unstable=1), floor, 3)["v"]
    expect(not unstable["meets_floor"],
           "GUARD an unstable content cell misses the floor")

    expect("aksum-exports" in good["known_failing"],
           "the known failure is reported even on a passing sweep")


def test_a_session_is_recorded_and_is_not_a_date() -> None:
    """D4, item 1. Two fields, and the second is not decoration.

    All three archived sweeps are within-session and nothing in any of them
    says so. Block E's ~270 calls are worth nothing if the archives cannot tell
    a session from a repetition.
    """
    print("\nsession identity")

    session = answer_eval.session_identity("D4 pilot day 1")
    for key in ("id", "date", "date_basis", "started_at", "label"):
        expect(bool(session.get(key)), f"a session records its {key}")
    expect(session["date_basis"] == "UTC",
           "the date is UTC, and the archive says which basis it is")
    expect(len(session["date"]) == 10 and session["date"].count("-") == 2,
           f"the date is a plain YYYY-MM-DD, not a timestamp "
           f"({session['date']})")

    # Per INVOCATION. Two sweeps an hour apart on one afternoon are two
    # sessions and one date — which is precisely the 2026-08-10 pair — so an
    # id derived from the date would be the blindness this exists to remove.
    expect(answer_eval.session_identity()["id"]
           != answer_eval.session_identity()["id"],
           "GUARD two invocations are two sessions, not one")

    closed = answer_eval.close_session(session)
    expect(closed["date"] == session["date"] and closed["id"] == session["id"],
           "closing a session does not change what it is")
    expect(closed["crossed_midnight_utc"] is False,
           "a session that did not cross midnight says so")

    # A day of Block E is ~90 chat calls and well over half an hour. Begun at
    # 23:50 UTC it finishes on the next date, and it is still ONE session,
    # counted under the date it began — otherwise a two-day sweep whose
    # second day ran late could present itself as three.
    yesterday = (_dt.datetime.now(_dt.timezone.utc)
                 - _dt.timedelta(days=1)).strftime("%Y-%m-%d")
    late = answer_eval.close_session({**session, "date": yesterday})
    expect(late["crossed_midnight_utc"] is True,
           "GUARD a session that ran past midnight UTC records that it did")
    expect(late["date"] == yesterday,
           "GUARD a session that crossed midnight keeps the date it began on")


def test_the_two_stability_numbers() -> None:
    """D4, item 3. One number cannot say which of the two is moving.

    Built on the 2026-08-10 observation itself, because that is the case the
    numbers exist to describe and a fixture that merely resembled it would
    prove nothing about the case that mattered.
    """
    print("\nper-case and per-session stability")

    def runs(case_id, version, session, outcomes):
        return [{"case": case_id, "prompt_version": version,
                 "session_id": session, "session_date": "2026-08-10",
                 "content_ok": ok} for ok in outcomes]

    # vimose-runes: 3/3 in one session, 0/3 in the next, evidence block
    # byte-identical, temperature 0.
    observed = (runs("vimose-runes", "p7-answer-v2r", "A", [True] * 3)
                + runs("vimose-runes", "p7-answer-v2r", "B", [False] * 3))
    numbers = answer_eval.stability(observed)

    expect(numbers["per_case"]["rate"] == 1.0,
           "the 2026-08-10 case is 100% stable PER CASE — each session was "
           "internally unanimous, so the sampler is not what moved")
    expect(numbers["per_session"]["rate"] == 0.0,
           "GUARD and 0% stable PER SESSION — which is the finding, and what "
           "one number would have shown as a flaky 50%")
    expect(numbers["per_case"]["cells"] == 2
           and numbers["per_session"]["pairs"] == 1,
           "both numbers report their own denominator")
    named = numbers["disagreeing_across_sessions"]
    expect(len(named) == 1 and named[0]["case"] == "vimose-runes"
           and set(named[0]["verdicts"].values()) == {"pass", "fail"},
           "the disagreement is NAMED, not only counted")

    # A cell that lands differently across its own repetitions is a third
    # thing, and folding it into pass or fail would hide the condition
    # floor.json refuses outright under max_unstable_content_cells.
    split = answer_eval.stability(
        runs("x", "v", "A", [True, False, True])
        + runs("x", "v", "B", [True, True, True]))
    expect(split["per_case"]["rate"] == 0.5,
           "GUARD a cell splitting across its own repetitions is unstable "
           "per case")

    # A cell of one repetition is unanimous with itself. Counting it would
    # raise the figure by adding observations that cannot disagree.
    single = answer_eval.stability(runs("x", "v", "A", [True])
                                   + runs("y", "v", "A", [False]))
    expect(single["per_case"]["cells"] == 0
           and single["per_case"]["rate"] is None,
           "GUARD an unrepeated cell is NOT MEASURED, never 100%")

    # Pre-D4 archives. Folding them into one anonymous session would return a
    # per-session number computed over a session that never existed.
    old = [{"case": "x", "prompt_version": "v", "content_ok": True}
           for _ in range(6)]
    orphans = answer_eval.stability(old)
    expect(orphans["rows_without_session"] == 6
           and orphans["per_case"]["rate"] is None
           and orphans["per_session"]["rate"] is None,
           "GUARD rows with no session are counted in NEITHER number")


def test_the_sweep_records_the_corpus_it_was_made_against() -> None:
    """FINDING 14, 2026-08-24.

    D1 made `run_answer` record the corpus version in the `answers` row and in
    the per-run archive. `eval/run_answer_sweep.py` builds its own payload,
    never set `answer.corpus_version`, and so wrote NULL into
    `seed_corpus_digest` and no key into the archive — for all sixty
    sweep-archived runs on disk, and for every one of Block E's ~270.

    TASK 1's own justification was *"Block E's whole claim is that the corpus
    did not move under the sweep, and right now nothing in an archive would say
    if it had"*. The fix landed in the path that writes about one of those
    archives and not in the path that writes the other 270.
    """
    print("\nFINDING 14: the corpus a sweep was made against")

    def version(digest, hashes, count=None):
        return {"algorithm": "sha256-of-canonical-json-v1",
                "source": "database",
                "seed_record_count": count if count is not None else len(hashes),
                "seed_corpus_digest": digest, "record_hashes": hashes}

    steady = version("aaaa1111", {"eastasia-01-weilue": "h1",
                                  "africa-03-periplus-adulis": "h2"})
    expect(answer_eval.corpus_moved(steady, steady) is None,
           "a corpus that did not move says nothing")

    # The 2026-08-22 shape: one record edited, digest changes, everything else
    # identical. It happened three times that day.
    edited = version("bbbb2222", {"eastasia-01-weilue": "CHANGED",
                                  "africa-03-periplus-adulis": "h2"})
    moved = answer_eval.corpus_moved(steady, edited)
    expect(moved is not None,
           "GUARD a corpus that moved under the sweep is detected")
    expect(bool(moved) and "eastasia-01-weilue" in moved,
           "the record that changed is NAMED, not counted")
    expect(bool(moved) and "africa-03-periplus-adulis" not in moved,
           "a record that did not change is not named")

    grown = version("cccc3333", {"eastasia-01-weilue": "h1",
                                 "africa-03-periplus-adulis": "h2",
                                 "persia-09-new": "h3"})
    appeared = answer_eval.corpus_moved(steady, grown)
    expect(bool(appeared) and "appeared" in appeared
           and "persia-09-new" in appeared,
           "a record that appeared mid-sweep is named as having appeared")

    shrunk = answer_eval.corpus_moved(
        steady, version("dddd4444", {"eastasia-01-weilue": "h1"}))
    expect(bool(shrunk) and "vanished" in shrunk
           and "africa-03-periplus-adulis" in shrunk,
           "a record that vanished mid-sweep is named as having vanished")

    # The digest covers sorted (doc_id, hash) pairs, so it cannot move while
    # every pair is identical. If it does, that is a finding about the digest.
    impossible = answer_eval.corpus_moved(
        steady, version("eeee5555", dict(steady["record_hashes"])))
    expect(bool(impossible) and "finding about corpus_digest itself" in impossible,
           "GUARD a digest that moves while no record differs says so")

    # Asserted against the source TEXT, not against an imported module: this
    # suite has no database and no gateway, and `eval.run_answer_sweep` imports
    # `answer` and `ingest` at module level. Reading the file keeps the check
    # where it belongs — in the offline suite — and both of these defects were
    # invisible to every behavioural test that does not have a database behind
    # it, which is why they survived D1.
    source = (Path(__file__).resolve().parent
              / "run_answer_sweep.py").read_text(encoding="utf-8")
    expect("answer.corpus_version = corpus_version" in source,
           "GUARD the sweep sets answer.corpus_version before storing — "
           "without it assemble.store writes NULL")
    expect('"corpus_version": corpus_version,' in source,
           "GUARD the sweep writes corpus_version into every per-run archive")
    read_at_start = source.find("corpus_version = answer_store.corpus_version(conn)")
    read_at_end = source.find("corpus_version_after = answer_store.corpus_version(conn)")
    expect(0 < read_at_start < read_at_end,
           "GUARD the corpus version is read again AFTER the last chat call, "
           "not only before the first")


def test_calibration_refuses_too_few_days() -> None:
    """D4, item 2. The floor refuses to call itself calibrated.

    On 2026-08-10 nothing stopped `calibrated: true` being written except a
    person deciding to write it, and nothing would have stopped it being
    written again the same way.
    """
    print("\ncalibration refuses too few days")

    floor = load_floor()
    expect(floor["min_distinct_dates"] >= 3,
           f"the floor requires at least three distinct dates "
           f"({floor['min_distinct_dates']})")

    # Block E: the scope rule reads the CASE SET out of a sweep, so a fixture
    # that is only a session block is no longer a sweep. Defaulting to the
    # scope minimum keeps every guard below about the thing it was written
    # about — dates, sessions, repetitions — and lets the scope be tested on
    # its own terms rather than as a side effect of every other fixture.
    in_scope = int((floor.get("calibration_scope") or {}).get(
        "min_cases_per_sweep") or 0)

    # Block F, 2026-08-28: the scope rule now reads the ARM out of a sweep as
    # well as the case set, for the same reason the comment above gives about
    # cases. A fixture written to test dates should carry the declared arm and
    # fail on dates; a fixture that omitted it would fail on the arm instead
    # and every guard below would be watching the wrong clause.
    declared_arm = dict((floor.get("calibration_scope") or {}).get("arm") or {})

    # Ruling 49, F3. The same argument as the arm above, and eight assertions
    # in this file failed on the day the corpus clause landed because their
    # fixtures did not state one: a fixture that omits the corpus fails on the
    # CORPUS clause and every guard below it is then watching the wrong one.
    declared_corpus = dict((floor.get("calibration_scope") or {}).get("corpus")
                           or {})

    def sweep(date, session_id, repeat=3, cases=None):
        n = in_scope if cases is None else cases
        return {"repeat": repeat,
                "arm": declared_arm,
                "corpus_version": declared_corpus,
                "results": [{"case": f"case-{i}"} for i in range(n)],
                "session": {"id": session_id, "date": date,
                            "date_basis": "UTC"}}

    three_days = [sweep("2026-08-24", "a"), sweep("2026-08-25", "b"),
                  sweep("2026-08-26", "c")]
    good = answer_eval.calibration_eligibility(three_days, floor)
    expect(good["may_calibrate"],
           "three dates, three repetitions each, may calibrate")

    two_days = answer_eval.calibration_eligibility(three_days[:2], floor)
    expect(not two_days["may_calibrate"],
           "GUARD two distinct dates cannot calibrate")

    # The 2026-08-10 shape exactly: two sweeps, hours apart, ONE date.
    one_day = [sweep("2026-08-10", "a"), sweep("2026-08-10", "b"),
               sweep("2026-08-10", "c")]
    same = answer_eval.calibration_eligibility(one_day, floor)
    expect(not same["may_calibrate"],
           "GUARD three sessions on one day are still one date and cannot "
           "calibrate")
    expect(same["distinct_sessions"] == 3 and same["distinct_dates"] == 1,
           "sessions and dates are counted separately and both are reported")
    expect(same["dates_with_more_than_one_session"] == ["2026-08-10"],
           "a date carrying more than one session is named — that pair is "
           "what invalidated this floor")

    # The three sweeps already on disk have no session block at all.
    orphaned = answer_eval.calibration_eligibility(
        three_days + [{"repeat": 3}], floor)
    expect(not orphaned["may_calibrate"],
           "GUARD a sweep with no session identity blocks calibration rather "
           "than being counted as a date")
    expect(orphaned["sweeps_without_session"] == 1,
           "the sweep with no session identity is counted and reported")

    thin = answer_eval.calibration_eligibility(
        [sweep("2026-08-24", "a"), sweep("2026-08-25", "b"),
         sweep("2026-08-26", "c", repeat=1)], floor)
    expect(not thin["may_calibrate"],
           "GUARD three dates of single shots cannot calibrate either")

    # The threshold lives in the floor FILE, where loosening it is a diff —
    # and there is a floor below which the term stops meaning anything. One
    # day is the value that would reproduce 2026-08-10 exactly.
    refused = False
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "floor.json"
        path.write_text(json.dumps({**floor, "min_distinct_dates": 1}),
                        encoding="utf-8")
        try:
            load_floor(path)
        except GoldSetError as exc:
            refused = "single day" in str(exc)
    expect(refused,
           "GUARD a floor permitting calibration from a single day is refused")


def test_the_variance_decomposition() -> None:
    """Block E, G4's deliverable. Built and checked BEFORE the 270 calls.

    The instrument is exercised here on fixtures whose right answer is known by
    construction, and separately on the two D4 pilot archives by
    `python -m eval.decompose`. That ordering is deliberate: D4's own lesson is
    that findings 14, 15 and 16 were all found by RUNNING an instrument rather
    than reading one, and a decomposition first run on the day-3 archive would
    be a 270-call instrument with no rehearsal.
    """
    def run(case, session, ok, text="t", version="p7-answer-v2r", rep=1):
        return {"case": case, "prompt_version": version, "repetition": rep,
                "session_id": session, "session_date": "2026-08-26",
                "content_ok": ok, "answer": text}

    def grid(spec, reps=3, texts=None):
        """spec: {case: {session: content_ok}} -> rows, reps per cell."""
        out = []
        for case_id, sessions in spec.items():
            for session_id, ok in sessions.items():
                for k in range(1, reps + 1):
                    text = (texts or {}).get((case_id, session_id), "t")
                    out.append(run(case_id, session_id, ok, text, rep=k))
        return out

    # Part 8's archived grid is TWO prompt versions and it is on disk. Pooling
    # them charges the difference between two prompts to the residual and
    # reports the prompt decision as sampling noise.
    mixed = grid({"a": {"s1": True, "s2": False}, "b": {"s1": True, "s2": True}})
    mixed = mixed + [run("a", "s1", True, version="p7-answer-v4")]
    pooled = answer_eval.decompose_verdicts(mixed)
    expect(not pooled["may_report"]
           and any("prompt version" in r for r in pooled["refusals"]),
           "GUARD a decomposition refuses to pool two prompt versions")

    # The balanced estimators are only these expressions on a balanced grid.
    lopsided = grid({"a": {"s1": True, "s2": False},
                     "b": {"s1": False, "s2": True}})
    lopsided = [r for r in lopsided
                if not (r["case"] == "a" and r["session_id"] == "s1"
                        and r["repetition"] == 3)]
    uneven = answer_eval.decompose_verdicts(lopsided)
    expect(not uneven["may_report"]
           and any("UNBALANCED" in r for r in uneven["refusals"]),
           "GUARD an unbalanced grid is refused rather than decomposed")

    absent = [r for r in grid({"a": {"s1": True, "s2": False},
                               "b": {"s1": False, "s2": True}})
              if not (r["case"] == "b" and r["session_id"] == "s2")]
    # The `except` is not defensive padding and it was put here by a mutation.
    # With the completeness refusal removed, this call does not return a wrong
    # answer — it raises KeyError on the absent cell, the suite dies, and the
    # mutation harness reports the guard as unwatched rather than as broken.
    # That is FINDING 15's shape exactly: a true report inviting the wrong
    # diagnosis. A crash is not a refusal, so it is caught and scored as one
    # more way of failing to refuse.
    try:
        holed = answer_eval.decompose_verdicts(absent)
    except Exception:  # noqa: BLE001 — a crash is not a refusal either
        holed = {"may_report": True, "refusals": []}
    expect(not holed["may_report"]
           and any("INCOMPLETE" in r for r in holed["refusals"]),
           "GUARD an incomplete grid is refused rather than decomposed")

    # The commonest outcome in this repository: every run agreed. There is no
    # variance to apportion, and four terms reading 0% would be four numbers
    # that add to nothing — the vacuous pass in its purest form.
    unanimous = answer_eval.decompose_verdicts(
        grid({"a": {"s1": True, "s2": True}, "b": {"s1": True, "s2": True}}))
    expect(unanimous["may_report"] and unanimous["shares"] is None,
           "GUARD zero total variance is NOT MEASURED, never 0%")

    # A crossover: each case passes in one session and fails in the other, and
    # the two cases cross. Case means are equal, session means are equal, and
    # ALL the structure is interaction. The case and session estimators go
    # negative, which is this estimator saying the terms are indistinguishable
    # from nothing — information, not an error.
    crossover = answer_eval.decompose_verdicts(
        grid({"a": {"s1": True, "s2": False}, "b": {"s1": False, "s2": True}}))
    expect(crossover["may_report"]
           and "case" in crossover["negative_estimates"],
           "GUARD a negative component estimate is named, not clamped in "
           "silence")
    # (MS_B - MS_AB), not (MS_B - MS_E). Against the residual this fixture
    # returns exactly 0 for the session term and the negative estimate — the
    # whole signal that the term is not there — disappears without a trace.
    expect("session" in crossover["negative_estimates"],
           "GUARD the session term is estimated against the interaction mean "
           "square, not the residual")
    expect(crossover["shares"] is not None
           and crossover["shares"]["case_x_session"] > 0.99,
           "the crossover is charged to the interaction term")

    # Rows archived before D4 carry no session and cannot be given one now.
    # Folding them into one anonymous session would decompose over a session
    # that never existed — the same refusal `stability` already makes.
    orphaned = grid({"a": {"s1": True, "s2": False},
                     "b": {"s1": False, "s2": True}})
    orphaned = orphaned + [{"case": "a", "prompt_version": "p7-answer-v2r",
                            "repetition": 1, "content_ok": True, "answer": "t"}]
    excluded = answer_eval.decompose_verdicts(orphaned)
    expect(excluded["may_report"] and excluded["rows_without_session"] == 1
           and excluded["runs"] == 12,
           "GUARD a row with no session identity is excluded from the "
           "decomposition and counted")

    one_session = answer_eval.decompose_verdicts(
        grid({"a": {"s1": True}, "b": {"s1": False}}))
    expect(not one_session["may_report"]
           and any("session(s)." in r for r in one_session["refusals"]),
           "GUARD one session cannot yield a session term")

    single_shot = answer_eval.decompose_verdicts(
        grid({"a": {"s1": True, "s2": False},
              "b": {"s1": False, "s2": True}}, reps=1))
    expect(not single_shot["may_report"]
           and any("repetition(s) per cell" in r
                   for r in single_shot["refusals"]),
           "GUARD one repetition cannot separate the residual from the "
           "interaction")

    # The positive control. Both cases pass on one day and fail on the next,
    # which is the shape of 2026-08-10 and the thing the whole block exists to
    # be able to see.
    by_day = answer_eval.decompose_verdicts(
        grid({"a": {"s1": True, "s2": False}, "b": {"s1": True, "s2": False}}))
    expect(by_day["shares"] is not None and by_day["shares"]["session"] > 0.99,
           "GUARD the session term carries the variance when the sessions "
           "disagree")

    # FINDING 18's shape: unanimous within each session, sharing nothing across
    # the boundary, with the verdict identical throughout.
    same_verdict = grid(
        {"a": {"s1": True, "s2": True}, "b": {"s1": True, "s2": True}},
        texts={("a", "s1"): "x", ("a", "s2"): "y",
               ("b", "s1"): "x", ("b", "s2"): "y"})
    texts = answer_eval.decompose_texts(same_verdict)
    expect(texts["may_report"]
           and texts["within_session"]["rate"] == 1.0
           and texts["across_sessions"]["rate"] == 0.0
           and texts["agreement_lost_at_the_session_boundary"] == 1.0,
           "GUARD text agreement separates within-session from across-session")
    verdicts = answer_eval.decompose_verdicts(same_verdict)
    expect(verdicts["shares"] is None and texts["across_sessions"]["rate"] == 0.0,
           "FINDING 18 reproduced: the verdicts have no variance to decompose "
           "while the text agrees across sessions 0% of the time")
    # Both cases here emit the same two strings, so pairs drawn from DIFFERENT
    # cases agree — which is what a shared refusal template looks like, and
    # what would otherwise inflate both rates above with no sign of it.
    expect(texts["cross_case_baseline"]["rate"] > 0.0,
           "GUARD identical text across DIFFERENT cases is reported as a "
           "baseline")


def test_the_calibration_scope_and_demotions() -> None:
    """Block E, decisions 1 and 4, both settled BEFORE day 1.

    The rule between days is change nothing, so a scope or a floor term
    settled on day 3 is one chosen after seeing the numbers. Both are data in
    `floor.json`; these are the guards that stop the data being a formality.
    """
    print("\nthe calibration scope, and what a demotion costs to write")

    floor = load_floor()
    scope = floor["calibration_scope"]
    expect(int(scope["min_cases_per_sweep"]) >= 30,
           f"the scope admits only sweeps of >= 30 cases, which is G4's "
           f"number ({scope['min_cases_per_sweep']})")

    declared_arm = dict(scope.get("arm") or {})

    # Ruling 49, F3. The same argument as the arm above, and eight assertions
    # in this file failed on the day the corpus clause landed because their
    # fixtures did not state one: a fixture that omits the corpus fails on the
    # CORPUS clause and every guard below it is then watching the wrong one.
    declared_corpus = dict(scope.get("corpus") or {})

    def sweep(date, session_id, repeat=3, cases=30):
        return {"repeat": repeat,
                "arm": declared_arm,
                "corpus_version": declared_corpus,
                "results": [{"case": f"case-{i}"} for i in range(cases)],
                "session": {"id": session_id, "date": date,
                            "date_basis": "UTC"}}

    three = [sweep("2026-08-27", "a"), sweep("2026-08-29", "b"),
             sweep("2026-08-31", "c")]
    pilot = three + [sweep("2026-08-25", "pilot", cases=6)]

    # A six-case sweep beside three thirty-case sweeps is a floor whose
    # denominator changes between dates. Unnamed, it blocks.
    blocked = answer_eval.calibration_eligibility(pilot, floor)
    expect(not blocked["may_calibrate"]
           and any("outside" in r for r in blocked["refusals"]),
           "GUARD a sweep below the scope minimum blocks calibration when it "
           "is not named")

    with_rule = {**floor, "calibration_scope": {
        **scope, "excluded_by_rule": {"pilot.json": "six cases, below the "
                                                    "scope minimum"}}}
    allowed = answer_eval.calibration_eligibility(
        pilot, with_rule, ["a.json", "b.json", "c.json", "pilot.json"])
    expect(allowed["may_calibrate"] and allowed["eligible_sweeps"] == 3,
           "a sweep out of scope is excluded by a NAMED rule, and the three "
           "in scope calibrate")
    expect([e["sweep"] for e in allowed["excluded_by_rule"]] == ["pilot.json"],
           "an excluded sweep is NAMED in the report, never merely subtracted")

    # The anti-loophole, and the reason the list is checked rather than
    # trusted: without this, excluded_by_rule is a place to put a sweep whose
    # numbers nobody liked.
    loophole = {**floor, "calibration_scope": {
        **scope, "excluded_by_rule": {"a.json": "inconvenient"}}}
    refused = answer_eval.calibration_eligibility(
        three, loophole, ["a.json", "b.json", "c.json"])
    expect(not refused["may_calibrate"]
           and refused["wrongly_excluded"] == ["a.json"],
           "GUARD a sweep that SATISFIES the rule cannot be excluded by name")

    # Callers with no filenames — every fixture above, and every caller before
    # Block E — can match no exclusion at all, so the old behaviour is exactly
    # unchanged rather than approximately unchanged.
    anonymous = answer_eval.calibration_eligibility(pilot, with_rule)
    expect(not anonymous["may_calibrate"],
           "GUARD an exclusion cannot apply to a sweep whose archive is not "
           "named")

    # Block E, 2026-08-26. A day that lost calls has the full case set and a
    # hole in its grid. It must not calibrate from either end.
    holed = three[:2] + [{**sweep("2026-08-31", "c"),
                          "incomplete": [{"case": "x", "prompt_version": "p",
                                          "repetition": 2, "error": "boom"}]}]
    dropped = answer_eval.calibration_eligibility(holed, floor)
    expect(not dropped["may_calibrate"]
           and any("INCOMPLETE" in r for r in dropped["refusals"]),
           "GUARD a sweep archived INCOMPLETE cannot calibrate, even with the "
           "full case set")

    # vimose-runes, decision 1. Demoted, and still reported for ever.
    expect("vimose-runes" not in floor["required_cases"],
           "vimose-runes is no longer a required case")
    expect("vimose-runes" in floor["known_failing_cases"],
           "vimose-runes is still REPORTED as an open defect — a demotion "
           "that stops being reported is a deletion")
    demotion = floor["demotions"]["vimose-runes"]
    expect(all(str(demotion.get(k, "")).strip()
               for k in ("evidence", "diagnosis", "reinstated_when")),
           "the demotion records evidence, a diagnosis and what would put the "
           "case back")

    def floor_with(demotions, **rest):
        base = {**floor, "demotions": demotions, **rest}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "floor.json"
            path.write_text(json.dumps(base), encoding="utf-8")
            try:
                load_floor(path)
            except GoldSetError as exc:
                return str(exc)
        return ""

    thin = floor_with({"vimose-runes": {"evidence": "0/3 twice",
                                        "diagnosis": "retrieval"}})
    expect("reinstated_when" in thin,
           "GUARD a demotion with no written condition for return is refused")

    untracked = floor_with(
        {"muziris-cargo": {"evidence": "e", "diagnosis": "d",
                           "reinstated_when": "r"}})
    expect("required_cases" in untracked,
           "GUARD a case cannot be demoted and required at the same time")

    unreported = floor_with(
        {"ghost-case": {"evidence": "e", "diagnosis": "d",
                        "reinstated_when": "r"}})
    expect("known_failing_cases" in unreported,
           "GUARD a demoted case that is not tracked as a known failure is "
           "refused")


def test_a_failed_chat_call_does_not_take_the_day() -> None:
    """Block E, 2026-08-26. One call of ninety-nine used to kill the run.

    `run_sweep` caught EmbeddingError and left the chat call unguarded, so a
    TranslationError propagated out of main() AFTER N per-run archives were
    written and BEFORE the sweep archive that ties them together — the orphan
    state the runbook warns about from Ctrl-C, reachable without Ctrl-C.
    D4's 18-call pilot never went near it.

    Tested behaviourally and not by reading the source, unlike the FINDING 14
    checks above. Those assert that a LINE exists; this is control flow, and a
    line-exists check on control flow is the vacuous proof in a new costume.
    The module imports cleanly with no database and no gateway; everything it
    would reach across is replaced here.
    """
    print("\na failed chat call does not take the day")

    import contextlib
    import io
    from eval import run_answer_sweep as sweep_mod
    from ingest import embed as embed_mod

    class _English:
        kind, text, ground, band = "published", "ivory and tortoise-shell", "", ""

    class _Passage:
        marker, chunk_id, similarity = "S1", "africa-03::002", 0.51
        english = _English()

        def to_dict(self):
            return {"marker": self.marker, "chunk_id": self.chunk_id}

    class _Span:
        abs_start = 7

    class _Grounding:
        ok = True
        quote_spans = [_Span()]

        def to_dict(self):
            return {"ok": True}

    class _Answer:
        question = "q?"
        answer_text = "ivory and tortoise-shell [S1]"
        grounding = _Grounding()
        refused = False
        model = "anthropic/claude-haiku-4-5-20251001"
        prompt_version = "p7-answer-v2r"
        embedding_model = None
        retrieval_k = 0
        corpus_version = None
        serving_stack: dict = {}
        passages = [_Passage()]
        sources_block = ""
        notes: list = []
        raw_response = ""
        # Block F, 2026-08-28. Added because the runner started reading them
        # and this stand-in did not have them — eight checks in this function
        # failed with an AttributeError that named neither the field nor the
        # reason. See the coverage guard directly below, which is the thing
        # that should have failed instead.
        model_alias = "chat-default"
        temperature = 0.0

    # A stand-in for AssembledAnswer is a CONTRACT with it, and until now
    # nothing said so. `_one_run` reads attributes off whatever `assemble`
    # returns; when the arm fields were added, this class went stale and the
    # eight behavioural checks below failed on an AttributeError raised deep
    # inside the retry path — which reads as "the retry is broken" and is not.
    # Checked against the dataclass rather than against a list, so a field
    # added tomorrow fails HERE, once, by name.
    import dataclasses
    from answer.assemble import AssembledAnswer
    absent = sorted(f.name for f in dataclasses.fields(AssembledAnswer)
                    if not hasattr(_Answer, f.name))
    expect(not absent,
           f"GUARD the fake answer carries every AssembledAnswer field — "
           f"a stand-in that has gone stale fails the checks below by "
           f"AttributeError, and names neither the field nor the reason "
           f"(absent: {absent})")

    class _Scored:
        ok, failures = True, []

    class _Case:
        def __init__(self, case_id):
            self.id = case_id
            self.question = f"question for {case_id}?"

    cases = [_Case("alpha"), _Case("beta")]
    session = {"id": "s" * 32, "date": "2026-08-26", "date_basis": "UTC",
               "label": "unit", "started_at": "2026-08-26T00:00:00+00:00"}

    def run(fail_on, progress=False):
        """fail_on: a mutable list of (case, repetition) that raise, popped as
        they are consumed — so a cell can fail once and succeed on the retry."""
        calls = []

        def fake_assemble(question, passages, **kwargs):
            calls.append(question)
            key = (question, len([c for c in calls if c == question]))
            if key in fail_on:
                fail_on.remove(key)
                raise RuntimeError("gateway said 529")
            return _Answer()

        originals = {
            (sweep_mod.assemble, "assemble"): sweep_mod.assemble.assemble,
            (sweep_mod.assemble, "build_evidence"): sweep_mod.assemble.build_evidence,
            (sweep_mod.answer_store, "corpus_version"): sweep_mod.answer_store.corpus_version,
            (sweep_mod.translate, "resolve_model_label"): sweep_mod.translate.resolve_model_label,
            (sweep_mod.answer_eval, "score_payload"): sweep_mod.answer_eval.score_payload,
            (embed_mod, "embed_query"): embed_mod.embed_query,
            (embed_mod, "resolve_model_label"): embed_mod.resolve_model_label,
        }
        try:
            sweep_mod.assemble.assemble = fake_assemble
            sweep_mod.assemble.build_evidence = lambda *a, **k: [_Passage()]
            sweep_mod.answer_store.corpus_version = lambda conn: {
                "seed_corpus_digest": "d" * 64, "seed_record_count": 24,
                "record_hashes": {}, "source": "unit"}
            sweep_mod.translate.resolve_model_label = lambda *a, **k: "m"
            sweep_mod.answer_eval.score_payload = lambda *a, **k: _Scored()
            embed_mod.embed_query = lambda text, **k: [0.0]
            embed_mod.resolve_model_label = lambda *a, **k: "e"
            buffer = io.StringIO()
            errors = io.StringIO()
            with contextlib.redirect_stdout(buffer), \
                    contextlib.redirect_stderr(errors):
                outcome = sweep_mod.run_sweep(
                    conn=None, cases=cases, prompt_versions=["p7-answer-v2r"],
                    repeat=2, k=6, max_sources=6, profiles={}, pause=0.0,
                    dry_run=False, write=False, session=session,
                    progress=progress)
            return outcome, buffer.getvalue(), errors.getvalue()
        finally:
            for (obj, name), value in originals.items():
                setattr(obj, name, value)

    # A clean run is untouched by any of this.
    clean, _, _ = run(fail_on=[])
    expect(len(clean["results"]) == 4 and not clean["incomplete"]
           and not clean["retried"],
           "a sweep with no failure archives four runs and reports neither an "
           "incomplete cell nor a retry")

    # One call fails once. The retry at the end succeeds, and the day survives.
    once, output, _ = run(fail_on=[("question for alpha?", 2)])
    expect(len(once["results"]) == 4 and not once["incomplete"],
           "GUARD one failed call is retried and the sweep still completes")
    expect(len(once["retried"]) == 1
           and once["retried"][0]["case"] == "alpha"
           and once["retried"][0]["repetition"] == 2,
           "the retried cell is NAMED, not counted")
    expect(any(row.get("retried_after_failure") for row in once["results"]),
           "GUARD a run that had to be asked twice says so on its own row — it "
           "is never indistinguishable from one that did not")
    expect("529" in output,
           "the failure that caused the retry is printed, not swallowed")

    # The same cell fails twice. Note the ordinals: beta's calls are #1 (rep 1),
    # #2 (rep 2), then #3 which is the RETRY of rep 1 — the retry happens at the
    # end of the sweep, not in place, so rep 2 runs in between. Failing #1 and
    # #3 is one cell failing twice; failing #1 and #2 would be two DIFFERENT
    # cells failing once each, and both would then be rescued.
    twice, output, _ = run(fail_on=[("question for beta?", 1),
                                    ("question for beta?", 3)])
    expect(len(twice["incomplete"]) == 1
           and twice["incomplete"][0]["case"] == "beta"
           and "retry_error" in twice["incomplete"][0],
           "GUARD a cell that fails twice is recorded as INCOMPLETE, with both "
           "errors named")
    expect(len(twice["results"]) == 3,
           "the runs that DID complete are kept — they are real, and they are "
           "not a shorter sweep")

    # And an incomplete sweep is refused a floor verdict from both ends: here,
    # and in calibration_eligibility.
    source = (Path(__file__).resolve().parent
              / "run_answer_sweep.py").read_text(encoding="utf-8")
    # Widened 2026-08-28 with ruling 36's second reason to compute no verdict.
    # The clause is now `incomplete or floor_not_applicable`, and this check
    # names both halves so that dropping either one fails here rather than
    # passing on a substring of the other.
    expect("verdicts = ({} if (incomplete or floor_not_applicable)" in source,
           "GUARD no floor verdict is computed for an incomplete sweep — it "
           "would be a floor met on a different denominator, in the same words")

    # ---- Block E correction 5: a ten-minute sweep must be watchable ------
    #
    # Days 1, 2 and 3 each ran 99 calls over about ten minutes through a `*>`
    # redirect and showed the operator nothing at all until they exited, so all
    # three were watched by counting archive files from a second window. The
    # fix has to keep the capture whole: `*>` takes every stream, so progress
    # written to STDOUT would land in the archived transcript and progress that
    # is not flushed would arrive in one block at the end, which is the problem
    # it is meant to solve.
    #
    # Behavioural, not a line-exists check. FINDING 14's checks assert that a
    # line is present in the source; this is control flow, and a line-exists
    # check on control flow is the vacuous proof in a new costume.
    quiet, quiet_out, quiet_err = run(fail_on=[])
    expect(quiet_err == "",
           "GUARD without --progress the sweep writes nothing to stderr — a "
           "plain run is unchanged, and days 1-3 remain comparable")

    loud, loud_out, loud_err = run(fail_on=[], progress=True)
    lines = [line for line in loud_err.splitlines() if line.strip()]
    expect(len(lines) == 4,
           "--progress writes ONE line per completed cell, and there were four")
    expect(all("/4]" in line for line in lines),
           "each line carries the cell count against the total, so a stalled "
           "sweep is distinguishable from a slow one")
    expect(loud_out == quiet_out,
           "GUARD --progress does not change STDOUT — `*>` captures every "
           "stream, and a capture that gained progress lines would not be "
           "comparable with days 1-3")
    expect("alpha" in loud_err and "beta" in loud_err,
           "the line names the case, so a sweep that stops can be resumed by "
           "a reader who knows where it stopped")

    # A failed cell must tick too, or the counter silently stops advancing on
    # exactly the run the operator is watching most closely.
    hurt, _hurt_out, hurt_err = run(fail_on=[("question for alpha?", 2)],
                                    progress=True)
    # Counted on the cell marker, not on a leading bracket: the retry pass
    # writes a "[retry]" header and that is not a cell.
    hurt_lines = [line for line in hurt_err.splitlines() if "/4]" in line]
    expect(len(hurt_lines) == 4 and any("FAILED" in line
                                        for line in hurt_lines),
           "GUARD a FAILED cell ticks as well as a successful one, and says "
           "which it was")
    expect(sum(1 for line in hurt_err.splitlines() if "/4]" in line) == 4,
           "GUARD the RETRY does not tick a fifth cell — a sweep of four cells "
           "must never report five, however many calls it took to finish them")
    expect("[retry]" in hurt_err,
           "the retry pass announces itself, so a sweep that appears to have "
           "stopped at the last cell is legible")

    # The flush is the point. Without it Python buffers stdout AND stderr when
    # neither is a terminal, and ten minutes of progress arrives at once, after
    # the thing it was meant to report on.
    # Counted at the CALL SITES, not searched for as a bare substring. The
    # first version of this check read `"flush=True" in source` and passed
    # after a mutation removed the flush from both prints — because the
    # explanatory COMMENT above `_tick` contains the words "flush=True", and a
    # comment satisfied the check. That is the vacuous-proof family this
    # repository keeps catching, found here by the mutation harness on
    # 2026-08-28, which is what the harness is for.
    expect(source.count("file=sys.stderr, flush=True") == 2
           and "flush=False" not in source,
           "the progress line is flushed — buffered progress is not progress")


def test_an_exclusion_cannot_be_the_question() -> None:
    """Ruling 41, 2026-08-28. A correct refusal restates the question it refuses.

    `expect_answer_excludes` is a bare substring test and cannot tell a claim
    from a refusal to make one. On a correctly_refusable case that is not a
    corner: the more precisely a refusal names what it declines to assert, the
    more certainly it trips an exclusion assembled out of the question.

    oc-eo-cattigara failed 0/12 across four sessions and three dates on exactly
    that, refusing correctly every time. Writing this guard then turned up
    antikythera-absent — a REQUIRED case, passing 12/12, one refusal phrasing
    away from the same failure with nothing anywhere that would have said why.
    The second case is the argument for a rule rather than a correction.
    """
    print("\nan exclusion built from the question fires on the right answer")

    cases = {c.id: c for c in load_answer_cases()}
    raw = json.loads((Path("eval/gold/answer_cases.json")).read_text(
        encoding="utf-8"))
    rule = raw.get("refusal_exclusion_rule") or {}
    expect(bool(rule.get("stopwords")),
           "the gold file declares the stopword list the rule uses — in data, "
           "where widening it until an exclusion passes is a diff")

    by_id = {c["id"]: c for c in raw["cases"]}
    expect("Ptolemy's Cattigara" not in
           by_id["oc-eo-cattigara"]["expect_answer_excludes"]
           and "Oc Eo was Cattigara" not in
           by_id["oc-eo-cattigara"]["expect_answer_excludes"],
           "oc-eo-cattigara no longer excludes phrases made of its own "
           "question")
    expect("Antikythera mechanism was built" not in
           by_id["antikythera-absent"]["expect_answer_excludes"],
           "antikythera-absent, which is REQUIRED and was passing, no longer "
           "carries the same hazard")
    expect(all(str(by_id[case].get("excludes_corrected_on", "")).strip()
               for case in ("oc-eo-cattigara", "antikythera-absent")),
           "both corrections are recorded beside the lists they changed, not "
           "only in a commit message")

    # The archived answers are the evidence, and they are on disk: every one of
    # the twelve refused correctly and named what it was refusing.
    expect(cases["oc-eo-cattigara"].expected_behaviour == "correctly_refusable"
           and cases["oc-eo-cattigara"].expect_refusal,
           "expect_refusal is what carries this case, and it passed 12/12 "
           "throughout")

    def loads_with(case_id, excludes):
        edited = json.loads(json.dumps(raw))
        for case in edited["cases"]:
            if case["id"] == case_id:
                case["expect_answer_excludes"] = excludes
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "answer_cases.json"
            path.write_text(json.dumps(edited), encoding="utf-8")
            try:
                load_answer_cases(path)
            except GoldSetError as exc:
                return str(exc)
        return ""

    refused = loads_with("oc-eo-cattigara", ["Ptolemy's Cattigara"])
    expect("built entirely from this case's own question" in refused,
           "GUARD an exclusion assembled from the case's own question is "
           "refused at load time")
    reordered = loads_with("oc-eo-cattigara", ["Oc Eo was Cattigara"])
    expect("built entirely from this case's own question" in reordered,
           "GUARD word order does not rescue it — the same vocabulary in a "
           "different arrangement is the same substring hazard")
    marker = loads_with("oc-eo-cattigara", ["Golden Chersonese"])
    expect(marker == "",
           "a FABRICATION MARKER — content the corpus does not hold and a "
           "refusal has no reason to utter — loads, which is the pattern the "
           "other seven refusal cases already follow")


def test_skz_titulature_is_tracked_rather_than_corrected_away() -> None:
    """Ruling 42, 2026-08-28."""
    print("\nskz-titulature, tracked rather than corrected away")

    floor = load_floor()
    expect("skz-titulature" in floor["known_failing_cases"],
           "skz-titulature is REPORTED as an open defect — it fails 0/12 on "
           "one assertion while satisfying every other and resolving four "
           "quotations")
    expect("skz-titulature" not in floor["required_cases"],
           "and it is not required, so a floor pass never reads as 'the "
           "system answers this'")
    case = {c.id: c for c in load_answer_cases()}["skz-titulature"]
    expect(any("Ardashir" in group for group in case.expect_answer_contains_any),
           "GUARD the Ardashir group is still asserted — dropping it is the "
           "floor lowered to what is currently passing, on a case that has "
           "never passed")


def test_the_arm_is_part_of_the_scope() -> None:
    """Block F decision 2, 2026-08-28, declared BEFORE the sonnet arm ran.

    The defect this closes is not that a sonnet sweep might calibrate the
    floor by accident. It is that the file's own anti-loophole would have
    INSISTED on it. A sonnet arm at temperature 1 carries a session identity,
    runs the full 33 cases and archives complete, so it satisfies every clause
    the scope had; `a_named_sweep_must_actually_fail_the_rule` then refuses to
    let a qualifying sweep be excluded by name. The guard built to stop numbers
    being hidden would have forced a temperature-1 sonnet sweep into a floor
    set on greedy haiku.

    Nine sweeps are archived and none records an arm, so the reconstruction is
    guarded here too — including the half of it that is an ASSUMPTION about the
    code rather than a reading of the file.
    """
    print("\nthe arm, and why it had to become part of the rule")

    floor = load_floor()
    scope = floor["calibration_scope"]
    arm = scope.get("arm") or {}
    expect(bool(arm.get("model_alias")) and arm.get("temperature") is not None,
           "the floor declares the ARM it calibrates from, as a pair")

    # Ruling 49, F3. The same argument as the arm above, and eight assertions
    # in this file failed on the day the corpus clause landed because their
    # fixtures did not state one: a fixture that omits the corpus fails on the
    # CORPUS clause and every guard below it is then watching the wrong one.
    declared_corpus = dict(scope.get("corpus") or {})

    def sweep(date, session_id, arm_block=..., rows=None, cases=30):
        out = {"repeat": int(floor["min_repetitions"]),
               "corpus_version": declared_corpus,
               "results": rows or [{"case": f"case-{i}"} for i in range(cases)],
               "session": {"id": session_id, "date": date, "date_basis": "UTC"}}
        if arm_block is not ...:
            out["arm"] = arm_block
        return out

    mine = dict(arm)
    three = [sweep("2026-08-24", "a", mine), sweep("2026-08-25", "b", mine),
             sweep("2026-08-26", "c", mine)]
    expect(answer_eval.calibration_eligibility(three, floor)["may_calibrate"],
           "three dates on the DECLARED arm calibrate exactly as before")

    # The whole point, in one fixture: a foreign arm that passes every other
    # clause. Same repetitions, same case count, complete grid, and — so that
    # the DATE clause cannot be what refuses it — added as a fourth sweep
    # beside three days that already calibrate on their own.
    sonnet = three + [sweep("2026-08-27", "d",
                            {"model_alias": "chat-strong",
                             "temperature": 1.0})]
    verdict = answer_eval.calibration_eligibility(sonnet, floor)
    expect(not verdict["may_calibrate"]
           and any("chat-strong" in r for r in verdict["refusals"]),
           "GUARD a sweep on another arm cannot calibrate, even when it "
           "satisfies every other clause of the rule")

    # And, because it genuinely FAILS the rule, naming it is legitimate — the
    # anti-loophole does not fire. That is the difference this clause buys.
    named = {**floor, "calibration_scope": {
        **scope, "excluded_by_rule": {"sonnet.json": "temperature-1 sonnet "
                                                     "arm; not this floor's"}}}
    excused = answer_eval.calibration_eligibility(
        sonnet, named, ["a.json", "b.json", "c.json", "sonnet.json"])
    expect(excused["may_calibrate"]
           and [e["sweep"] for e in excused["excluded_by_rule"]]
           == ["sonnet.json"],
           "a foreign arm CAN be excluded by name, because it really does "
           "fail the rule — the anti-loophole does not fire on it")

    # The nine legacy archives. No arm block, and the alias recoverable only
    # from the echo Block E correction 4 established cannot move.
    legacy_rows = [{"case": f"case-{i}",
                    "serving_stack": {"id": f"chatcmpl-{i}",
                                      "model": arm["model_alias"]}}
                   for i in range(30)]
    legacy = answer_eval.sweep_arm(sweep("2026-08-24", "a", rows=legacy_rows))
    expect(legacy["model_alias"] == arm["model_alias"]
           and legacy["basis"] == "reconstructed",
           "GUARD a pre-Block-F sweep's arm is RECONSTRUCTED from "
           "serving_stack.model and says so, rather than being assumed")
    expect(answer_eval.calibration_eligibility(
        [sweep(d, s, rows=legacy_rows)
         for d, s in (("2026-08-24", "a"), ("2026-08-25", "b"),
                      ("2026-08-26", "c"))], floor)["may_calibrate"],
           "the four Block E archives still calibrate — the clause does not "
           "de-calibrate a floor by arriving")

    foreign_legacy = [{"case": f"case-{i}",
                       "serving_stack": {"model": "chat-strong"}}
                      for i in range(30)]
    expect(not answer_eval.calibration_eligibility(
        three + [sweep("2026-08-27", "d", rows=foreign_legacy)],
        floor)["may_calibrate"],
           "GUARD reconstruction is not a free pass: a sweep whose rows echo "
           "another alias fails the arm clause too")

    blind = sweep("2026-08-27", "d", rows=[{"case": f"case-{i}"}
                                           for i in range(30)])
    expect(answer_eval.sweep_arm(blind)["basis"] == "unidentifiable"
           and not answer_eval.calibration_eligibility(
               three + [blind], floor)["may_calibrate"],
           "GUARD a sweep whose arm cannot be identified at all blocks, "
           "rather than being read as the default")

    # The decomposition, from the other end. Pooling two arms charges the
    # difference between two MODELS to the residual and prints it as sampling
    # noise — the prompt-version refusal's argument, for the factor nothing
    # recorded until today.
    rows = []
    for case in ("a", "b"):
        for session, alias in (("s1", "chat-default"), ("s2", "chat-strong")):
            for rep in range(2):
                rows.append({"case": case, "session_id": session,
                             "session_date": "2026-08-26",
                             "prompt_version": "p7-answer-v2r",
                             "model_alias": alias,
                             "temperature": 0.0 if alias == "chat-default" else 1.0,
                             "repetition": rep, "content_ok": True,
                             "answer": "x"})
    mixed = answer_eval.decompose_verdicts(rows)
    expect(any("arms" in r for r in mixed["refusals"]),
           "GUARD a decomposition refuses to pool two arms")


def test_the_promotion_candidate_state() -> None:
    """Block F decision 4, 2026-08-28. The third state, and its two abuses.

    `weilue-chinese-quotation` sat in `known_failing_cases` for two days
    recording, in its own corrected text, that it passed 12/12 — a file
    asserting the opposite of what it had measured, because no state fitted.
    The demotion rules already stop a case leaving the file downward without
    evidence and a written condition. These are the same rules pointing up.
    """
    print("\nthe promotion candidate, and the bar that governs both directions")

    floor = load_floor()
    candidates = floor.get("promotion_candidates") or {}
    expect("weilue-chinese-quotation" in candidates,
           "weilue-chinese-quotation is a promotion candidate, not a known "
           "failure — it passes 12/12 and the file no longer says otherwise")
    expect("weilue-chinese-quotation" not in floor["known_failing_cases"]
           and "weilue-chinese-quotation" not in floor["required_cases"],
           "and it is in neither of the other two states")
    expect(all(str(candidates["weilue-chinese-quotation"].get(k, "")).strip()
               for k in ("evidence", "bar")),
           "the candidate records its evidence and the bar it has to meet")
    expect(str(floor.get("promotion_and_reinstatement_bar", "")).strip()
           and "three" in floor["demotions"]["vimose-runes"][
               "reinstated_when"].lower(),
           "ONE bar governs both directions, and the demotion carries the "
           "raised version of it")

    def floor_with(**rest):
        base = {**floor, **rest}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "floor.json"
            path.write_text(json.dumps(base), encoding="utf-8")
            try:
                load_floor(path)
            except GoldSetError as exc:
                return str(exc)
        return ""

    both = floor_with(promotion_candidates={
        "vimose-runes": {"evidence": "e", "bar": "b"}})
    expect("known-failing" in both,
           "GUARD a case cannot be a promotion candidate AND a known failure "
           "— that contradiction is the one this state was added to end")

    already = floor_with(promotion_candidates={
        "muziris-cargo": {"evidence": "e", "bar": "b"}})
    expect("required_cases" in already,
           "GUARD a case already in required_cases cannot also be waiting to "
           "get in")

    barless = floor_with(promotion_candidates={
        "some-case": {"evidence": "12/12"}})
    expect("bar" in barless,
           "GUARD a promotion candidate with no written bar is refused")

    scope = dict(floor["calibration_scope"])
    half = floor_with(calibration_scope={**scope,
                                         "arm": {"temperature": 0.0}})
    expect("model_alias" in half,
           "GUARD a half-declared arm clause is refused — it would admit "
           "every sweep that also said nothing")


def test_a_foreign_arm_is_not_a_subject_of_this_floor() -> None:
    """Ruling 36 in the RUNNER, which is where it had not reached.

    `calibration_eligibility` already refuses a foreign arm as a calibration
    INPUT. Nothing refused it as a floor SUBJECT. `run_answer_sweep.main`
    computed `check_floor` for whatever arm had just run, printed MEETS THE
    FLOOR / BELOW THE FLOOR in the words of a real verdict, archived it under
    `floor`, and returned it in the exit code - so the sonnet arm would have
    exited 1 for failing a floor calibrated on greedy haiku, and its permanent
    archive would carry a verdict a later reader has to know to discard.

    `check_floor` is arm-blind on purpose: it is pure and it scores a summary.
    The caller is what has to know. Tested on the three pure functions that
    caller now uses, so this needs no database and no gateway.
    """
    print("\na foreign arm is not a subject of this floor")

    from eval import run_answer_sweep as sweep_mod

    floor = load_floor()
    declared = floor["calibration_scope"].get("arm") or {}
    mine = {"model_alias": declared["model_alias"],
            "temperature": float(declared["temperature"])}

    applies, scope = sweep_mod.floor_applies(mine, floor)
    expect(applies and scope["known"] == "declared",
           "the arm this floor was calibrated on is judged by it exactly as "
           "before")

    sonnet = {"model_alias": "chat-strong", "temperature": 1.0}
    expect(not sweep_mod.floor_applies(sonnet, floor)[0],
           "GUARD a sweep on another ALIAS gets no floor verdict - an arm is "
           "read BESIDE this floor and never inside it")

    hot = {"model_alias": mine["model_alias"], "temperature": 1.0}
    expect(not sweep_mod.floor_applies(hot, floor)[0],
           "GUARD the same alias at another TEMPERATURE gets none either - "
           "the arm is the pair, not the model")

    # The arm clause is optional in floor.json. A floor that declares none
    # makes no claim about arms, and the fallback must not dress this runner's
    # own default up as the file's statement - the same `recorded` vs
    # `reconstructed` line sweep_arm draws one level down.
    armless = {**floor, "calibration_scope": {
        k: v for k, v in floor["calibration_scope"].items() if k != "arm"}}
    applies, scope = sweep_mod.floor_applies(mine, armless)
    expect(applies and str(scope["known"]).startswith("assumed"),
           "GUARD a floor that declares no arm SAYS the arm is assumed, "
           "rather than presenting this runner's default as the file's own")

    # And the half that leaves the process. A verdict suppressed in the report
    # but still returned by `main` is a verdict, and CI reads exit codes.
    expect(sweep_mod.exit_code({}, {"reason": "another arm"}) == 0,
           "GUARD a foreign arm cannot exit 1 - a floor that does not govern "
           "it cannot be failed by it")
    expect(sweep_mod.exit_code({}, None) == 2,
           "GUARD an empty verdict with no stated reason exits 2 - `all([])` "
           "is True, and a floor nobody measured must not report as met")
    expect(sweep_mod.exit_code({"p7": {"meets_floor": False}}, None) == 1
           and sweep_mod.exit_code({"p7": {"meets_floor": True}}, None) == 0,
           "the default arm still fails the process when it is below the "
           "floor, and passes when it is not")


def test_the_floor_state_a_case_declares() -> None:
    """FINDING 30's deferred check, and FINDING 32 -- why it is not the check
    that was deferred.

    F1 deferred *"goldset refuses a case whose archived_status names a
    floor.json state that floor.json contradicts... one token
    (`known_failing_cases`) tested against one file, not prose
    interpretation"*. Building it that way is impossible, and the proof is
    F1's own correction: the corrected `archived_status` on
    `weilue-chinese-quotation` says, truly, that ruling 38 moved the case OUT
    of `floor.json.known_failing_cases`. A token scan fires on the sentence
    that gets the history right, and a check whose first true positive is a
    false one is a check somebody switches off.

    So the claim moves out of the prose and into `floor_state`: one token,
    declared in the case, checked against one file, in both directions.
    """
    print("\nthe floor state a case declares, and the file that contradicts it")

    def with_floor(case_overrides, floor_overrides=None):
        """Load a one-case gold file beside a real floor.json. Returns the
        refusal, or "" if it loaded."""
        floor = {**load_floor(), **(floor_overrides or {})}
        case = _valid_case(**case_overrides)
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "floor.json").write_text(
                json.dumps(floor), encoding="utf-8")
            cases_path = Path(tmp) / "answer_cases.json"
            cases_path.write_text(json.dumps({"cases": [case]}), encoding="utf-8")
            try:
                load_answer_cases(cases_path)
            except GoldSetError as exc:
                return str(exc)
        return ""

    expect(
        "none" in FLOOR_STATES and "demotions" not in FLOOR_STATES,
        "GUARD demotions is not a floor state, because a demotion is a "
        "modifier on known_failing_cases and a case with two true answers is "
        "the defect",
    )

    expect_rejected(
        _valid_case(floor_state="tracked"),
        "GUARD a floor_state outside the vocabulary is refused",
        because="is not one of",
    )

    # A gold file copied to a temporary directory has no floor.json beside it,
    # and every harness here that exercises a whole-file rule makes exactly
    # that copy. The check resolves to the canonical floor rather than going
    # quiet, so the copy is not an exit from it.
    expect_rejected(
        _valid_case(id="aksum-exports", floor_state="required_cases"),
        "GUARD a gold file copied away from floor.json is still checked "
        "against the canonical one",
        because="holds it in 'known_failing_cases'",
    )

    detail = with_floor(
        {"id": "aksum-exports", "floor_state": "required_cases"})
    expect(
        "holds it in 'known_failing_cases'" in detail,
        "GUARD a case declaring a floor state the file contradicts is refused",
    )

    detail = with_floor({"id": "aksum-exports"})
    expect(
        "declares floor_state 'none'" in detail,
        "GUARD a case that declares nothing is asserting none, so a case the "
        "floor holds is refused",
    )

    detail = with_floor(
        {"id": "aksum-exports", "floor_state": "known_failing_cases"})
    expect(detail == "",
           "GUARD a case whose declared floor state matches the file loads")

    detail = with_floor(
        {"id": "c1"},
        {"promotion_candidates": {"c1": {"evidence": "e", "bar": "b"},
                                  "aksum-exports": {"evidence": "e", "bar": "b"}}},
    )
    expect(
        "is in both" in detail,
        "GUARD a floor file holding one case in two states is refused before "
        "any case is compared against it",
    )

    expect(
        "floor_state" not in answer_eval.ASSERTION_KEYS
        if hasattr(answer_eval, "ASSERTION_KEYS") else True,
        "GUARD floor_state is not a scored assertion, so no archived run is "
        "re-scored by declaring one",
    )

    # The live file, which is the only instance that matters. It is checked at
    # every load already; this asserts that the seven cases the floor holds are
    # actually declaring, rather than that nothing has been declared at all.
    declared = {c.id: c.floor_state for c in load_answer_cases() if c.floor_state}
    floor = load_floor()
    held = (set(floor["required_cases"])
            | set(floor.get("known_failing_cases") or {})
            | set(floor.get("promotion_candidates") or {}))
    expect(
        set(declared) == held and held,
        "GUARD every case the floor holds declares its state, and no case "
        "declares one the floor does not hold",
    )
    expect(
        declared.get("weilue-chinese-quotation") == "promotion_candidates",
        "GUARD the case FINDING 30 was found on now declares the state ruling "
        "38 moved it to",
    )


def test_the_corpus_is_part_of_the_scope() -> None:
    """Ruling 49, F3, 2026-08-31, declared BEFORE record 25 was ingested.

    The same defect as the arm clause and the same shape of fix, one dimension
    over. The moment F3 ingests record 25, a sweep at 33 records carries a
    session identity, runs the full case set, states its arm and archives
    complete — so it satisfies every clause the scope had — and
    `a_named_sweep_must_actually_fail_the_rule` then refuses to let a
    qualifying sweep be excluded by name. The file would have INSISTED that a
    33-record sweep calibrate a floor set at 24.

    What makes this one different from the arm is that nothing had to be
    reconstructed. FINDING 14 put `corpus_version` into every archive precisely
    so that a corpus which moved could not go unnoticed, `calibration_scope`
    was then written twice without ever reaching for it, and
    `eval/calibrate_floor.py` contained zero occurrences of the string
    "corpus". The data was on disk for three weeks and the rule did not read
    it.

    And the clause does not suspend the floor: a run at a moved corpus still
    computes a verdict on `required_cases`, which is the regression reading
    ruling 51 takes at every sub-tranche. What it may not do is re-calibrate.
    """
    print("\nthe corpus, and the rule that could not see it")

    floor = load_floor()
    scope = floor["calibration_scope"]
    declared = scope.get("corpus") or {}
    expect(len(str(declared.get("seed_corpus_digest") or "")) == 64
           and int(declared.get("seed_record_count") or 0) > 0,
           "the floor declares the CORPUS it calibrates from, as a digest and "
           "a count")

    declared_arm = dict(scope.get("arm") or {})

    def sweep(date, session_id, corpus=..., cases=30, moved=None):
        out = {"repeat": int(floor["min_repetitions"]),
               "arm": declared_arm,
               "results": [{"case": f"case-{i}"} for i in range(cases)],
               "session": {"id": session_id, "date": date,
                           "date_basis": "UTC"}}
        if corpus is not ...:
            out["corpus_version"] = corpus
        if moved:
            out["corpus_moved"] = moved
        return out

    at_24 = {"seed_record_count": declared["seed_record_count"],
             "seed_corpus_digest": declared["seed_corpus_digest"]}
    at_33 = {"seed_record_count": 33, "seed_corpus_digest": "9" * 64}

    three = [sweep("2026-08-24", "a", at_24), sweep("2026-08-25", "b", at_24),
             sweep("2026-08-26", "c", at_24)]
    expect(answer_eval.calibration_eligibility(three, floor)["may_calibrate"],
           "three dates at the DECLARED corpus calibrate exactly as before")

    # The whole point, in one fixture: F3's first sub-tranche. Full case set,
    # declared arm, complete grid, real session identity, and a fourth date —
    # so that nothing but the corpus can be what refuses it.
    moved_corpus = three + [sweep("2026-08-30", "d", at_33)]
    verdict = answer_eval.calibration_eligibility(moved_corpus, floor)
    expect(not verdict["may_calibrate"],
           "GUARD a sweep at a moved corpus cannot calibrate, even when it "
           "satisfies every other clause of the rule")
    expect(any("33 records" in r and "24 records" in r
               for r in verdict["refusals"]),
           "the refusal names both record counts, so the reader is not asked "
           "to compare two digests by eye")

    named = {**floor, "calibration_scope": {
        **scope, "excluded_by_rule": {"f3.json": "ran at 33 records; this "
                                                 "floor is set at 24"}}}
    excused = answer_eval.calibration_eligibility(
        moved_corpus, named, ["a.json", "b.json", "c.json", "f3.json"])
    expect(excused["may_calibrate"]
           and [e["sweep"] for e in excused["excluded_by_rule"]] == ["f3.json"],
           "a moved corpus CAN be excluded by name, because it really does "
           "fail the rule — the anti-loophole does not fire on it")

    silent = three + [sweep("2026-08-30", "d")]
    expect(not answer_eval.calibration_eligibility(
        silent, floor)["may_calibrate"],
           "GUARD a sweep that records no corpus at all cannot calibrate — an "
           "unidentifiable corpus is never read as the current one")

    both_ends = three + [sweep("2026-08-30", "d", at_24,
                               moved="record 'seasia-04-new' appeared")]
    expect(not answer_eval.calibration_eligibility(
        both_ends, floor)["may_calibrate"],
           "GUARD a sweep whose corpus MOVED under it cannot calibrate even "
           "when both ends match the declared one")

    # Absent means the clause is not declared and nothing is checked, exactly
    # as the arm clause behaves. A floor file written before F3 does not
    # silently acquire a corpus rule.
    without = {**floor, "calibration_scope": {
        k: v for k, v in scope.items() if k != "corpus"}}
    expect(answer_eval.calibration_eligibility(
        moved_corpus, without)["may_calibrate"],
           "GUARD a floor declaring no corpus clause behaves exactly as it did "
           "before F3")

    reading = answer_eval.sweep_corpus(sweep("2026-08-24", "a", at_24))
    expect(reading["basis"] == "recorded"
           and reading["seed_record_count"] == declared["seed_record_count"],
           "a sweep that states its corpus is read as RECORDED")
    blind = answer_eval.sweep_corpus(sweep("2026-08-24", "a"))
    expect(blind["basis"] == "unidentifiable"
           and blind["seed_corpus_digest"] is None,
           "GUARD a sweep with no corpus_version is unidentifiable and is not "
           "given a digest")

    # The clause has to match the archives the floor actually stands on, or it
    # de-calibrates the floor by arriving — which would be a rule that lowered
    # the thing it was written to protect.
    sweep_dir = Path(__file__).resolve().parent / "sweeps"
    standing = []
    for name in floor.get("calibrated_from_sweeps") or []:
        path = sweep_dir / name
        if path.exists():
            standing.append(json.loads(path.read_text(encoding="utf-8"))
                            .get("corpus_version") or {})
    expect(bool(standing) and all(
        s.get("seed_corpus_digest") == declared["seed_corpus_digest"]
        for s in standing),
           "every archive this floor is calibrated FROM ran at the corpus the "
           "clause declares")

    # A HALF-declared corpus is worse than none, for the reason the arm clause
    # already gives: calibration_eligibility would compare against a None
    # digest and admit every archive that also recorded None, which is the
    # three pre-D4 sweeps precisely.
    def floor_with(corpus_clause) -> str:
        broken = json.loads(json.dumps(floor))
        broken["calibration_scope"]["corpus"] = corpus_clause
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "floor.json"
            path.write_text(json.dumps(broken), encoding="utf-8")
            try:
                load_floor(path)
            except GoldSetError as exc:
                return str(exc)
        return ""

    expect("64-character seed_corpus_digest"
           in floor_with({"seed_record_count": 24}),
           "GUARD a corpus clause with no digest is refused at load, not "
           "silently matched against every archive that also says nothing")
    expect("seed_record_count"
           in floor_with({"seed_corpus_digest": declared["seed_corpus_digest"]}),
           "GUARD a corpus clause with no record count is refused at load")
    expect("A floor calibrated on no records" in floor_with(
        {"seed_corpus_digest": declared["seed_corpus_digest"],
         "seed_record_count": 0}),
           "GUARD a corpus clause declaring zero records is refused at load")

    # Ruling 51 — the mid-tranche reading, and the directory that is the rule.
    source = (Path(__file__).resolve().parent
              / "run_answer_sweep.py").read_text(encoding="utf-8")
    expect("PROBE_DIR" in source and "target_dir = PROBE_DIR" in source,
           "GUARD a run below min_cases_per_sweep archives to probes/ and not "
           "to sweeps/")
    expect(source.find("min_cases = int(") < source.find("chat_calls = 0"),
           "GUARD the floor is loaded BEFORE the run, so a floor.json that "
           "will not load costs no embedding request")
    calibrator = (Path(__file__).resolve().parent
                  / "calibrate_floor.py").read_text(encoding="utf-8")
    expect("sweep_dir.glob(\"*.json\")" in calibrator
           and "PROBE_DIR" not in calibrator,
           "GUARD calibrate_floor reads sweeps/ only, so a probe cannot "
           "calibrate BY CONSTRUCTION rather than by being remembered")


def main() -> int:
    print("Part 8 gold answer cases — offline checks")
    test_loader_rejects_the_easy_version()
    test_loader_rejects_vacuous_assertions()
    test_refusal_must_justify_itself()
    test_expected_behaviour_is_declared()
    test_the_stratification_is_computable()
    test_the_gloss_arm_has_teeth()
    test_every_entry_point_guards_its_stdout()
    test_the_source_text_can_be_required()
    test_a_discriminator_loads_as_one_instrument()
    test_the_real_gold_set_loads()
    test_matching_tolerances()
    test_the_aksum_answer_fails()
    test_content_from_the_wrong_document()
    test_the_live_payload_shape()
    test_a_refusal_case_is_not_passed_by_verbosity()
    test_scoring_an_archive()
    test_a_duplicate_question_cannot_shadow_a_case()
    test_a_session_is_recorded_and_is_not_a_date()
    test_the_two_stability_numbers()
    test_the_variance_decomposition()
    test_the_sweep_records_the_corpus_it_was_made_against()
    test_a_failed_chat_call_does_not_take_the_day()
    test_calibration_refuses_too_few_days()
    test_the_calibration_scope_and_demotions()
    test_the_arm_is_part_of_the_scope()
    test_a_foreign_arm_is_not_a_subject_of_this_floor()
    test_the_promotion_candidate_state()
    test_an_exclusion_cannot_be_the_question()
    test_skz_titulature_is_tracked_rather_than_corrected_away()
    test_the_floor()
    test_the_floor_state_a_case_declares()
    test_the_corpus_is_part_of_the_scope()
    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
