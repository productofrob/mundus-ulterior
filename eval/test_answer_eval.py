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

import json
import tempfile
from pathlib import Path

from eval import answer_eval
from eval.goldset import (ANSWER_BEHAVIOURS, ANSWER_REGIONS, GoldSetError,
                          load_answer_cases, load_floor)

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
    archives = answer_eval.load_archives()
    expect(len(results) == len(archives),
           f"every archived run is scored ({len(results)} of {len(archives)})")
    expect(len(results) >= 16,
           f"the 16 recovered Part 7 answers are still among them "
           f"({len(results)})")
    expect(not unmatched, f"every archived question has a gold case {unmatched}")

    by_case: dict[str, list] = {}
    for result in results:
        by_case.setdefault(result.case_id, []).append(result)

    def runs(case_id: str, version: str) -> list:
        return [r for r in by_case[case_id] if r.prompt_version == version]

    expect(all(not r.ok for r in by_case["aksum-exports"]),
           "GUARD every archived Aksum answer fails — including those the "
           "Part 7 checks called grounded")

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
        summary({"vimose-runes": 2}, 3, 0.2), floor, 3)["v"]
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
    test_the_floor()
    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
