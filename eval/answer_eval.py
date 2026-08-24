"""Part 8: score answers against the gold cases in eval/gold/answer_cases.json.

What this measures, and why it is not what Part 7 measured
----------------------------------------------------------

Part 7's seven checks answer "is this answer tidy about its citations?" — every
claim carries a marker, every quotation is really in the source it cites. They
cannot answer "does the claim follow from the passage?", and the gap is not
academic: the Aksum answer refuses, states the opposite of the English printed
in its own evidence block, and scores `Grounded` for it. Meanwhile the Chinese
answer is accurate, well quoted, and scores NOT GROUNDED on an uncited opening
sentence. One metric, two failures pointing opposite ways.

So this module scores **content**: does the answer say the thing the corpus can
support, does it cite the record that supports it, and did its quotations land
on characters that exist. Every assertion is a fact about strings — Part 8
decision 2. There is no judge. A judge would reproduce the back-translation's
problem one layer up, where the thing checking and the thing being checked can
be wrong in the same direction and agree.

Groundedness is still reported. It is never the pass condition.

Scoring archived runs vs. scoring live ones
-------------------------------------------

`score_payload` takes the payload shape `run_answer` writes and
`recover_answer_baseline` reconstructs, so the same scorer runs over a live
answer and over the 16 recovered archives. That matters because the archives are
the only comparison across prompt versions that exists, and re-scoring them is
free.

One caveat travels with the recovered ones, and `--archives` prints it: a
recovered payload has no passage text, so assertions about what the model was
*shown* cannot be checked from it. Nothing in the current case set needs that.

Usage:

    python -m eval.answer_eval --archives            # score every archived run
    python -m eval.answer_eval --archives --by-case  # grid: case x prompt version
    python -m eval.answer_eval --json run.json       # score one payload file
    python -m eval.answer_eval --list                # what the gold set asserts

Costs nothing: no gateway, no database, no embeddings. Reads files.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from eval.goldset import (AnswerCase, GoldSetError, load_answer_cases,
                          question_key)

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

RUNS_DIR = Path(__file__).resolve().parent / "answer_runs"

# cite.REFUSAL_SENTENCE, matched the way assemble.AssembledAnswer.refused does:
# trailing full stop stripped, case-insensitive. Imported rather than copied so
# the two cannot drift — a refusal the scorer fails to recognise would turn
# every refusal case into a silent failure.
try:
    from answer.cite import REFUSAL_SENTENCE
except ImportError:  # pragma: no cover - answer package always present in repo
    REFUSAL_SENTENCE = "The sources retrieved do not answer this question."


def normalise(text: str) -> str:
    """Casefolded, with runs of whitespace collapsed.

    The same tolerances cite.locate_in_text applies, and for the same reason: a
    writer fitting a phrase into a sentence changes spacing and case without
    changing what was said. Punctuation is NOT normalised — `tortoise-shell` and
    `tortoise shell` are different strings, and a case should say which it
    accepts rather than let the matcher decide on its behalf.
    """
    return re.sub(r"\s+", " ", text).strip().casefold()


def contains(haystack: str, needle: str) -> bool:
    return normalise(needle) in normalise(haystack)


def is_refusal(answer_text: str) -> bool:
    return REFUSAL_SENTENCE.rstrip(".").casefold() in answer_text.casefold()


@dataclass
class Assertion:
    label: str
    ok: bool
    detail: str = ""


@dataclass
class CaseResult:
    case_id: str
    question: str
    prompt_version: str
    source: str
    assertions: list[Assertion] = field(default_factory=list)
    grounded: bool | None = None
    refused: bool = False
    resolved_quotes: int = 0

    @property
    def ok(self) -> bool:
        return all(a.ok for a in self.assertions)

    @property
    def failures(self) -> list[Assertion]:
        return [a for a in self.assertions if not a.ok]

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "question": self.question,
            "prompt_version": self.prompt_version,
            "source": self.source,
            "ok": self.ok,
            "grounded": self.grounded,
            "refused": self.refused,
            "resolved_quotes": self.resolved_quotes,
            "assertions": [
                {"label": a.label, "ok": a.ok, "detail": a.detail}
                for a in self.assertions
            ],
        }


def _resolved_quote_count(payload: dict) -> int:
    spans = (payload.get("grounding") or {}).get("quote_spans") or []
    return sum(1 for span in spans if span.get("abs_start") is not None)


def _cited(payload: dict) -> list[dict]:
    """The passages the answer actually cited.

    Two payload shapes reach here and they do not agree, which cost 30 chat
    calls to discover. A RECOVERED payload carries `cited` per passage, because
    `answer_citations` stores that column. A LIVE payload is
    `Passage.to_dict()`, which carries marker, chunk_id, doc_id and the English
    choice — and no `cited` key, because whether a passage was cited is a
    property of the answer, not of the passage.

    Filtering on `p.get("cited")` therefore returned nothing for every live run,
    so `expect_cited_docs` failed on all four content cases while the answers
    were fine — Muziris and the Chinese sources scored 0/3 having quoted five and
    seven passages respectively. The scorer was written against the archives and
    never run against the thing it exists to score.

    So: use `cited` where the payload states it, and fall back to the grounding
    report's own `cited_markers`, which both shapes carry. The grounding report
    is the authority in either case — it is what `answer_citations.cited` was
    computed from in the first place.
    """
    passages = payload.get("passages", [])
    if any("cited" in p for p in passages):
        return [p for p in passages if p.get("cited")]
    markers = set((payload.get("grounding") or {}).get("cited_markers") or [])
    return [p for p in passages if p.get("marker") in markers]


def score_payload(case: AnswerCase, payload: dict, source: str = "") -> CaseResult:
    """Score one answer payload against one gold case. Pure; no I/O."""
    answer_text = payload.get("answer") or ""
    refused = is_refusal(answer_text)
    resolved = _resolved_quote_count(payload)
    cited = _cited(payload)
    cited_docs = {p.get("doc_id") for p in cited}
    cited_chunks = {p.get("chunk_id") for p in cited}

    result = CaseResult(
        case_id=case.id,
        question=case.question,
        prompt_version=payload.get("prompt_version") or "unknown",
        source=source,
        grounded=payload.get("grounded"),
        refused=refused,
        resolved_quotes=resolved,
    )
    add = result.assertions.append

    if case.expect_refusal:
        add(Assertion(
            "refuses, as the corpus cannot answer this",
            refused,
            "" if refused else "the answer did not refuse — if the corpus now "
                              "contains this material, the case is stale; if it "
                              "does not, the answer is invented",
        ))

    for needle in case.expect_answer_contains:
        add(Assertion(f"says {needle!r}", contains(answer_text, needle)))

    for group in case.expect_answer_contains_any:
        hit = next((item for item in group if contains(answer_text, item)), None)
        add(Assertion(
            f"says one of {group!r}",
            hit is not None,
            f"matched {hit!r}" if hit else "none of these wordings appears",
        ))

    for needle in case.expect_answer_excludes:
        absent = not contains(answer_text, needle)
        add(Assertion(
            f"does not say {needle!r}",
            absent,
            "" if absent else "present — for a refusal sentence this means the "
                              "answer declined a question the corpus can answer",
        ))

    for doc_id in case.expect_cited_docs:
        add(Assertion(
            f"cites {doc_id}",
            doc_id in cited_docs,
            f"cited: {sorted(d for d in cited_docs if d)}" if doc_id not in cited_docs else "",
        ))

    for chunk_id in case.expect_cited_chunks:
        add(Assertion(f"cites chunk {chunk_id}", chunk_id in cited_chunks))

    # Which documents were actually QUOTED, with the quotation resolving to
    # characters on disk. Citing a document says the model named it; quoting it
    # says the model used it. The Aksum evidence set is why this exists: three of
    # its six passages carry one or more of the gold terms, so every content
    # assertion is satisfiable from India and China while the Aksum passage is
    # cited for something else.
    doc_by_marker = {p.get("marker"): p.get("doc_id") for p in payload.get("passages", [])}
    quoted_docs = {
        doc_by_marker.get(span.get("marker"))
        for span in (payload.get("grounding") or {}).get("quote_spans") or []
        if span.get("abs_start") is not None
    }
    for doc_id in case.expect_quoted_docs:
        add(Assertion(
            f"quotes {doc_id}, resolving to characters on disk",
            doc_id in quoted_docs,
            f"quoted: {sorted(d for d in quoted_docs if d) or 'nothing'}"
            if doc_id not in quoted_docs else "",
        ))

    # FINDING 13, 2026-08-22. The check above passes on a quotation from EITHER
    # of a record's chunks. Across 16 archived runs of chinese-da-qin, 45 of 45
    # resolved spans came from reference_translation — while the Chinese chunk
    # was [S1], top of the block, at similarity 0.576. Prompt rule 3 permits the
    # SOURCE TEXT or the ENGLISH and requires neither, so the English wins every
    # time and nothing in the gold set could ever say otherwise.
    #
    # The span carries its own doc_id in both the archived and the live shape;
    # the marker map is kept as a fallback because Part 8 has already been caught
    # once assuming a key only the archives carry.
    quoted_from_original = {
        span.get("doc_id") or doc_by_marker.get(span.get("marker"))
        for span in (payload.get("grounding") or {}).get("quote_spans") or []
        if span.get("abs_start") is not None
        and span.get("source_field") == "original_text_excerpt"
    }
    for doc_id in case.expect_quoted_from_original:
        add(Assertion(
            f"quotes {doc_id} in its own language, not only in translation",
            doc_id in quoted_from_original,
            f"resolved quotations came from: "
            f"{sorted(d for d in quoted_from_original if d) or 'no source-text field'}"
            if doc_id not in quoted_from_original else "",
        ))

    if case.expect_min_resolved_quotes:
        add(Assertion(
            f"resolves at least {case.expect_min_resolved_quotes} quotation(s) "
            f"to characters on disk",
            resolved >= case.expect_min_resolved_quotes,
            f"resolved {resolved}",
        ))

    if case.expect_grounded is not None:
        add(Assertion(
            f"grounded is {case.expect_grounded}",
            bool(payload.get("grounded")) == case.expect_grounded,
        ))

    return result


# --------------------------------------------------------------------------
# Archives
# --------------------------------------------------------------------------

def load_archives(runs_dir: Path | None = None) -> list[tuple[dict, str]]:
    """Every archived run, as (payload, filename). Files with no `question`
    are not runs and are skipped — see eval/fixtures/README.md."""
    runs_dir = runs_dir or RUNS_DIR
    out: list[tuple[dict, str]] = []
    for path in sorted(runs_dir.glob("*.json")) if runs_dir.exists() else []:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(payload, dict) and "question" in payload:
            out.append((payload, path.name))
    return out


def match_case(cases: list[AnswerCase], payload: dict) -> AnswerCase | None:
    """The one gold case this archived run is scored against, or None.

    It used to return the FIRST case whose question matched, and that is the
    defect: a second case asking the same question would sit in the gold file
    looking like a test, counting toward every total, and never running
    against a single archive. Same family as FINDING 12 — a fault the harness
    was in a position to notice and reported as nothing at all — and quieter,
    because Finding 12 at least moved the numbers.

    Two guards, and they are not the same guard. `load_answer_cases` refuses a
    gold FILE that contains a collision, which is where the real set comes
    from. This refuses to CHOOSE when handed a colliding list by any other
    route — a hand-built list in a test, a filtered subset, a caller that
    concatenated two files. Either alone leaves the other door open.

    `question_key` is imported from the loader rather than reimplemented here,
    so the rule that admits a case and the rule that finds it are one rule.
    """
    question = question_key(payload.get("question") or "")
    hits = [case for case in cases if question_key(case.question) == question]
    if len(hits) > 1:
        raise GoldSetError(
            f"{len(hits)} gold cases ask this question — "
            f"{sorted(c.id for c in hits)}. Scoring cannot pick one, and "
            f"picking the first is how a case is never scored at all."
        )
    return hits[0] if hits else None


def score_archives(cases: list[AnswerCase],
                   runs_dir: Path | None = None) -> tuple[list[CaseResult], list[str]]:
    results, unmatched = [], []
    for payload, name in load_archives(runs_dir):
        case = match_case(cases, payload)
        if case is None:
            unmatched.append(f"{name}: {payload.get('question', '')[:60]}")
            continue
        results.append(score_payload(case, payload, source=name))
    return results, unmatched


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _print_result(result: CaseResult, verbose: bool) -> None:
    mark = "PASS" if result.ok else "FAIL"
    flags = []
    if result.grounded is not None:
        flags.append(f"grounded={result.grounded}")
    if result.refused:
        flags.append("refused")
    flags.append(f"quotes={result.resolved_quotes}")
    print(f"  {mark}  {result.case_id:<20} {result.prompt_version:<14} "
          f"{' '.join(flags)}")
    for assertion in (result.assertions if verbose else result.failures):
        tick = "ok  " if assertion.ok else "MISS"
        detail = f"  ({assertion.detail})" if assertion.detail else ""
        print(f"          {tick} {assertion.label}{detail}")


def _print_grid(results: list[CaseResult]) -> None:
    cases = sorted({r.case_id for r in results})
    versions = sorted({r.prompt_version for r in results})
    width = max((len(v) for v in versions), default=8)
    print("\ncase x prompt version — content PASS/FAIL, and (grounded)\n")
    print("  " + " " * 22 + "  ".join(v.ljust(width + 6) for v in versions))
    for case_id in cases:
        cells = []
        for version in versions:
            hits = [r for r in results
                    if r.case_id == case_id and r.prompt_version == version]
            if not hits:
                cells.append("-".ljust(width + 6))
                continue
            text = "/".join(
                f"{'PASS' if h.ok else 'FAIL'}({'G' if h.grounded else 'g'})"
                for h in hits
            )
            cells.append(text.ljust(width + 6))
        print(f"  {case_id:<22}" + "  ".join(cells))
    print("\n  G = the Part 7 checks called it grounded, g = they did not.")
    print("  PASS/FAIL is this harness: whether the answer says what the "
          "corpus supports.")

    # The disagreements are the entire point of building this.
    disagree = [r for r in results if r.ok is not bool(r.grounded)]
    if disagree:
        print(f"\n  {len(disagree)} answer(s) where the two metrics disagree:")
        for r in sorted(disagree, key=lambda r: (r.case_id, r.prompt_version)):
            direction = ("grounded but says nothing useful"
                         if r.grounded else "useful but scored not grounded")
            print(f"    {r.case_id:<20} {r.prompt_version:<14} {direction}")


# --------------------------------------------------------------------------
# D4 — session identity
# --------------------------------------------------------------------------
#
# `eval/run_answer_sweep.py` took --prompt-version --repeat --case --k
# --max-sources --pause --dry-run --no-write --json. There was no session flag
# and no archive carried a date. All three archived sweeps are within-session,
# and nothing in any of them says so.
#
# That is not a tidiness problem. floor.json records `calibration_invalidated:
# "2026-08-10, hours after being set."` — the vimose-runes evidence block was
# byte-identical (sha256, across all six archived runs) and one session
# produced 3/3 with seven resolved quotations while the next produced 0/3 with
# none. Same prompt version, same model, same evidence, temperature 0. Block
# E's ~270 calls are worth nothing if the archives cannot tell a SESSION from a
# REPETITION.
#
# TWO fields, not one, and the distinction is the whole point. TASK 3 specifies
# calibration on distinct DATES, and dates are what `eval/calibrate_floor.py`
# gates on. But the observation that invalidated the floor was two sweeps
# HOURS APART ON ONE DAY: the thing that moved was a session, not a date. A
# date-only archive cannot tell those two sweeps apart, which is the exact
# blindness this exists to remove — so the session id is recorded beside the
# date, and same-date-different-session pairs are reported as their own number.

SESSION_DATE_BASIS = "UTC"


def session_identity(label: str = "") -> dict:
    """One session, named once, at the moment it starts.

    The id is per INVOCATION. Two sweeps run an hour apart on one afternoon are
    two sessions and one date, and both facts are recorded rather than one
    being inferred from the other later.
    """
    now = _dt.datetime.now(_dt.timezone.utc)
    return {
        "id": uuid.uuid4().hex,
        "date": now.strftime("%Y-%m-%d"),
        "date_basis": SESSION_DATE_BASIS,
        "started_at": now.isoformat(timespec="seconds"),
        "label": label,
    }


def close_session(session: dict) -> dict:
    """The same session, with what happened to it while it ran.

    A day of Block E is ~90 chat calls, which is well over half an hour. A
    sweep begun at 23:50 UTC finishes on the next UTC date, and the session is
    still ONE session — `date` stays the date it STARTED, because that is what
    a session is denominated in and a session that changed its own date
    halfway through would be uncountable.

    `crossed_midnight_utc` records that it happened, so nobody has to work it
    out from two timestamps later, and so a three-day sweep whose day 2 and day
    3 are really one long day-2 cannot look like three dates.
    """
    now = _dt.datetime.now(_dt.timezone.utc)
    return {
        **session,
        "finished_at": now.isoformat(timespec="seconds"),
        "crossed_midnight_utc": now.strftime("%Y-%m-%d") != session["date"],
    }


# --------------------------------------------------------------------------
# D4 — per-case stability and per-session stability, as two numbers
# --------------------------------------------------------------------------
#
# One number cannot say which of the two is moving, and on 2026-08-10 they
# moved in opposite directions on the same case. `vimose-runes`, evidence block
# byte-identical across all six archived runs, temperature 0:
#
#     session A   3/3 pass, seven resolved quotations
#     session B   0/3 pass, none
#
# Read as ONE stability number that is 50% and looks like a flaky sampler. Read
# as two it is exact and says the opposite: PER-CASE stability 2 cells of 2,
# because each session was internally unanimous — the sampler is not the
# problem — and PER-SESSION stability 0 of 1, because the two sessions
# disagreed completely. `floor.json`'s session_caveat says it in prose:
# "repetitions within one session are correlated and are not independent
# samples". These are that sentence as arithmetic.

SESSION_VERDICTS = ("pass", "fail", "split")


def _cell_verdict(rows: list[dict]) -> str:
    """What one (case, prompt version, session) cell did, in one word.

    `split` is not a rounding of the other two and must never be collapsed into
    them: a cell that lands differently across its own repetitions is the
    condition floor.json refuses outright under max_unstable_content_cells,
    because the floor stops being MEASURABLE before it stops being met.
    """
    passed = sum(1 for r in rows if r["content_ok"])
    if passed == len(rows):
        return "pass"
    if passed == 0:
        return "fail"
    return "split"


def stability(rows: list[dict]) -> dict:
    """The two numbers, with their denominators, from any set of result rows.

    Pure. Takes rows from one sweep or from every sweep ever archived; the
    grouping is what makes them two numbers rather than one.

      per_case      within ONE session, across repetitions of one cell.
                    Measures the sampler.
      per_session   across SESSIONS, comparing each session's whole verdict for
                    one (case, prompt version). Measures the day.

    Rows carrying no `session_id` are counted in neither and are reported in
    `rows_without_session`. They are not folded into one anonymous session:
    doing that would put every pre-D4 archive into a single made-up session and
    return a per-session number computed over a session that never existed.
    """
    by_cell: dict[tuple, list[dict]] = {}
    without = 0
    for row in rows:
        session_id = row.get("session_id")
        if not session_id:
            without += 1
            continue
        by_cell.setdefault(
            (row["case"], row["prompt_version"], session_id), []).append(row)

    # Per case: only cells that were actually repeated. A cell of one
    # repetition is unanimous with itself, and counting it would raise the
    # stability figure by adding observations that cannot disagree.
    repeated = {k: v for k, v in by_cell.items() if len(v) > 1}
    stable_cells = sum(1 for rows_ in repeated.values()
                       if _cell_verdict(rows_) != "split")

    # Per session: only (case, prompt version) seen in more than one session.
    by_pair: dict[tuple, dict[str, str]] = {}
    for (case_id, version, session_id), rows_ in by_cell.items():
        by_pair.setdefault((case_id, version), {})[session_id] = \
            _cell_verdict(rows_)
    across = {k: v for k, v in by_pair.items() if len(v) > 1}
    agreeing = sum(1 for verdicts in across.values()
                   if len(set(verdicts.values())) == 1)

    return {
        "per_case": {
            "stable": stable_cells,
            "cells": len(repeated),
            "rate": (stable_cells / len(repeated)) if repeated else None,
            "measures": "the sampler, within one session",
        },
        "per_session": {
            "agreeing": agreeing,
            "pairs": len(across),
            "rate": (agreeing / len(across)) if across else None,
            "measures": "the day, across sessions",
        },
        # Named, not counted. "per-session stability 0.67" is a number; "this
        # case passed 3/3 in one session and 0/3 in the next" is something a
        # person can act on, and it is the only form in which the 2026-08-10
        # observation was ever legible.
        "disagreeing_across_sessions": [
            {"case": case_id, "prompt_version": version,
             "verdicts": dict(sorted(verdicts.items()))}
            for (case_id, version), verdicts in sorted(across.items())
            if len(set(verdicts.values())) > 1
        ],
        "sessions": sorted({row["session_id"] for row in rows
                            if row.get("session_id")}),
        "rows_without_session": without,
    }


def print_stability(numbers: dict) -> None:
    print("\n" + "=" * 72)
    print("stability — TWO numbers, because one cannot say which is moving")
    print("=" * 72)
    for key, label, nothing in (
        ("per_case", "per-case   ", "no cell was repeated"),
        ("per_session", "per-session", "no case was seen in two sessions"),
    ):
        block = numbers[key]
        n = block["cells"] if key == "per_case" else block["pairs"]
        got = block["stable"] if key == "per_case" else block["agreeing"]
        if not n:
            # NOT MEASURED, never 0% and never 100%. An empty denominator
            # printed as a rate is the vacuous pass this repository keeps
            # paying for.
            print(f"  {label}  NOT MEASURED — {nothing}")
            continue
        print(f"  {label}  {got}/{n} = {block['rate']:.0%}   "
              f"({block['measures']})")
    if numbers["rows_without_session"]:
        print(f"\n  {numbers['rows_without_session']} row(s) carry no session "
              f"identity and are counted in NEITHER number. They are pre-D4 "
              f"archives, not an anonymous session.")
    for row in numbers["disagreeing_across_sessions"]:
        print(f"\n  {row['case']} / {row['prompt_version']} disagreed across "
              f"sessions:")
        for session_id, verdict in row["verdicts"].items():
            print(f"    {session_id[:12]}  {verdict}")
    if numbers["per_session"]["pairs"]:
        print(
            "\n  A high per-case number beside a low per-session one is not "
            "noise: it is\n  every session being internally unanimous and the "
            "sessions disagreeing with\n  each other. That is the 2026-08-10 "
            "observation, and it is what invalidated\n  the floor."
        )
    else:
        print(
            "\n  Until a case has been seen in two sessions, the per-session "
            "number does not\n  exist and the per-case number is a "
            "within-session figure. That is the state\n  every archived sweep "
            "before D4 is in."
        )


# --------------------------------------------------------------------------
# D4 — calibration refuses to be written from too few days
# --------------------------------------------------------------------------

def calibration_eligibility(sweeps: list[dict], floor: dict) -> dict:
    """May `calibrated: true` be written from these sweeps? Pure; no I/O.

    TASK 3, item 2. `floor.json` has said `calibrated: false` since 2026-08-10,
    with `calibration_invalidated` recording that the stability which justified
    it was itself a single sample. The threshold lives in the floor FILE and
    not in this module, for the reason load_floor already gives about
    confidence_profiles: a threshold in Python invites the opposite move —
    quietly loosening it until the run passes — where in a data file loosening
    it is a diff.

    Dates, not sessions, per TASK 3 as written on 2026-08-20. Three sessions in
    one afternoon are three sessions and ONE date, and they cannot calibrate
    anything: that afternoon is exactly the shape of the 2026-08-10 pair of
    sweeps. Sessions are counted and reported beside the dates because they are
    the finer observation, and because a run with three dates and three
    sessions is a different thing from one with three dates and nine.
    """
    minimum = int(floor["min_distinct_dates"])
    reps_needed = int(floor["min_repetitions"])

    dated, undated = [], []
    for sweep in sweeps:
        session = sweep.get("session") or {}
        (dated if session.get("id") and session.get("date")
         else undated).append(sweep)

    dates = sorted({(s.get("session") or {})["date"] for s in dated})
    sessions = sorted({(s.get("session") or {})["id"] for s in dated})
    per_date: dict[str, int] = {}
    for sweep in dated:
        per_date[(sweep.get("session") or {})["date"]] = per_date.get(
            (sweep.get("session") or {})["date"], 0) + 1

    refusals: list[str] = []
    if len(dates) < minimum:
        refusals.append(
            f"{len(dates)} distinct date(s), and the floor requires "
            f"{minimum}. Repetitions within one session are correlated and "
            f"are not independent samples — a floor calibrated from fewer is "
            f"a within-session regression gate wearing the word 'calibrated'."
        )
    thin = [s for s in dated if int(s.get("repeat", 0)) < reps_needed]
    if thin:
        refusals.append(
            f"{len(thin)} sweep(s) ran fewer than {reps_needed} repetitions. "
            f"A single shot is one sample of a distribution nobody has looked "
            f"at."
        )
    if undated:
        refusals.append(
            f"{len(undated)} sweep(s) carry no session identity and count "
            f"toward no date. They were archived before D4 and cannot be "
            f"given one now: a date assigned after the fact is the "
            f"calibration this file already records as invalid."
        )

    return {
        "may_calibrate": not refusals,
        "refusals": refusals,
        "min_distinct_dates": minimum,
        "distinct_dates": len(dates),
        "dates": dates,
        "distinct_sessions": len(sessions),
        "sessions_per_date": dict(sorted(per_date.items())),
        # The finer observation, named because it is the one that broke the
        # floor: two sweeps, one day, opposite results.
        "dates_with_more_than_one_session": sorted(
            date for date, n in per_date.items() if n > 1),
        "sweeps_without_session": len(undated),
    }


def print_calibration(verdict: dict) -> None:
    print("\n" + "=" * 72)
    print("calibration eligibility")
    print("=" * 72)
    print(f"  distinct dates     {verdict['distinct_dates']} "
          f"(floor requires {verdict['min_distinct_dates']}): "
          f"{', '.join(verdict['dates']) or 'none'}")
    print(f"  distinct sessions  {verdict['distinct_sessions']}")
    for date, n in verdict["sessions_per_date"].items():
        print(f"    {date}  {n} session(s)")
    if verdict["dates_with_more_than_one_session"]:
        print(f"  more than one session on: "
              f"{', '.join(verdict['dates_with_more_than_one_session'])} — "
              f"counted as one date each, and worth reading beside the "
              f"per-session stability number")
    if verdict["may_calibrate"]:
        print("\n  ELIGIBLE. `calibrated: true` may be written from these "
              "sweeps.")
    else:
        print("\n  REFUSED. `calibrated: true` may NOT be written:")
        for refusal in verdict["refusals"]:
            print(f"    - {refusal}")


def check_floor(summary: dict, floor: dict, repetitions: int) -> dict:
    """Does a sweep summary meet the hard floor? Pure; no I/O.

    Returns one verdict per prompt version. A version meets the floor only if
    EVERY required case passed in EVERY repetition — not on average. An
    aggregate rate would let a total failure on one question be paid for by
    successes on others, and the questions are not interchangeable.
    """
    verdicts: dict[str, dict] = {}
    required = list(floor["required_cases"])
    known_failing = dict(floor.get("known_failing_cases") or {})

    for version, stats in summary["by_version"].items():
        cells = {c["case"]: c for c in summary["cells"]
                 if c["prompt_version"] == version}
        problems: list[str] = []

        if repetitions < floor["min_repetitions"]:
            problems.append(
                f"only {repetitions} repetition(s); the floor requires "
                f"{floor['min_repetitions']} — one shot is one sample of a "
                f"distribution nobody has looked at"
            )
        for case_id in required:
            cell = cells.get(case_id)
            if cell is None:
                problems.append(f"{case_id}: not run")
            elif cell["content_pass"] != cell["n"]:
                problems.append(
                    f"{case_id}: {cell['content_pass']}/{cell['n']} — a required "
                    f"case must pass every repetition"
                )
        if stats["refusal_rate"] > floor["max_refusal_rate"]:
            problems.append(
                f"refusal rate {stats['refusal_rate']:.0%} exceeds "
                f"{floor['max_refusal_rate']:.0%} — tidiness bought with silence"
            )
        if stats["unstable_content_cells"] > floor["max_unstable_content_cells"]:
            problems.append(
                f"{stats['unstable_content_cells']} content cell(s) unstable; "
                f"the floor stops being measurable before it stops being met"
            )

        verdicts[version] = {
            "meets_floor": not problems,
            "problems": problems,
            # Reported, never subtracted. An open defect is not an exemption.
            "known_failing": {
                case_id: {
                    "observed": (f"{cells[case_id]['content_pass']}"
                                 f"/{cells[case_id]['n']}"
                                 if case_id in cells else "not run"),
                    "reason": reason,
                }
                for case_id, reason in known_failing.items()
            },
        }
    return verdicts


def print_floor(verdicts: dict) -> None:
    print("\n" + "=" * 72)
    print("the hard floor")
    print("=" * 72)
    for version, verdict in verdicts.items():
        mark = "MEETS THE FLOOR" if verdict["meets_floor"] else "BELOW THE FLOOR"
        print(f"\n  {version}: {mark}")
        for problem in verdict["problems"]:
            print(f"    - {problem}")
        for case_id, detail in verdict["known_failing"].items():
            print(f"    known failure {case_id} ({detail['observed']}) — "
                  f"tracked, not exempted")
    print(
        "\n  The floor is a regression gate, not a definition of success: it "
        "says the\n  questions that work still work and that silence has not "
        "been mistaken for\n  rigour. Whether the corpus is big enough is a "
        "Part 10 question."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Part 8 — score answers on content, not citation hygiene"
    )
    parser.add_argument("--archives", action="store_true",
                        help="score every run in eval/answer_runs/")
    parser.add_argument("--json", metavar="PATH",
                        help="score a single run payload written by run_answer --json")
    parser.add_argument("--by-case", action="store_true",
                        help="print the case x prompt-version grid")
    parser.add_argument("--case", help="only this case id")
    parser.add_argument("--list", action="store_true",
                        help="print what each gold case asserts, and exit")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="show passing assertions too")
    args = parser.parse_args(argv)

    try:
        cases = load_answer_cases()
    except GoldSetError as exc:
        print(f"gold set will not load: {exc}", file=sys.stderr)
        return 2

    if args.case:
        cases = [c for c in cases if c.id == args.case]
        if not cases:
            print(f"no case with id {args.case!r}", file=sys.stderr)
            return 2

    if args.list:
        for case in cases:
            print(f"\n{case.id}  —  {case.question}")
            print(f"  why: {case.why}")
            if case.expect_refusal:
                print(f"  expects a REFUSAL: {case.refusal_is_correct_because}")
            for needle in case.expect_answer_contains:
                print(f"  says {needle!r}")
            for group in case.expect_answer_contains_any:
                print(f"  says one of {group!r}")
            for needle in case.expect_answer_excludes:
                print(f"  does not say {needle!r}")
            for doc_id in case.expect_cited_docs:
                print(f"  cites {doc_id}")
            if case.expect_min_resolved_quotes:
                print(f"  resolves >= {case.expect_min_resolved_quotes} quotation(s)")
            if case.archived_status:
                print(f"  archived: {case.archived_status}")
        return 0

    if args.json:
        payload = json.loads(Path(args.json).read_text(encoding="utf-8"))
        case = match_case(cases, payload)
        if case is None:
            print(f"no gold case for question {payload.get('question')!r}",
                  file=sys.stderr)
            return 2
        result = score_payload(case, payload, source=args.json)
        _print_result(result, args.verbose)
        return 0 if result.ok else 1

    if not args.archives:
        parser.print_help()
        return 2

    results, unmatched = score_archives(cases)
    if not results:
        print("no archived runs matched a gold case", file=sys.stderr)
        return 2

    print(f"scoring {len(results)} archived answer(s) against "
          f"{len(cases)} gold case(s)\n")
    for result in sorted(results, key=lambda r: (r.case_id, r.prompt_version,
                                                 r.source)):
        _print_result(result, args.verbose)

    if unmatched:
        print(f"\n{len(unmatched)} archived run(s) have no gold case:")
        for line in unmatched:
            print(f"  {line}")

    if args.by_case:
        _print_grid(results)

    passed = sum(1 for r in results if r.ok)
    print(f"\n{passed}/{len(results)} archived answers meet their case.")
    print(
        "Recovered archives carry no passage text, so assertions about what the "
        "model was shown cannot be checked from them. No current case needs it."
    )
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
