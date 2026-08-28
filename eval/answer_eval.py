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


def payload_arm(payload: dict) -> dict:
    """The arm ONE archived run was made on. Pure.

    `sweep_arm` answers this for a sweep FILE. This is the same question one
    level down, and it had to exist because `eval/answer_runs/` is NOT split by
    arm: ruling 36 separated `eval/arms/` from `eval/sweeps/`, and the per-run
    archive stayed one directory, because `rescore_sweep` rebuilds a summary
    from these files and a split directory would have to be searched twice.

    A payload with no `model_alias` predates 2026-08-28, when `assemble` gained
    the field and the answer path could not send anything but the greedy
    default. That is the same reconstruction ruling 36 permits for the nine
    legacy sweeps, on the same evidence, and it is labelled rather than assumed
    in silence.
    """
    alias = payload.get("model_alias")
    if alias:
        return {"model_alias": str(alias),
                "temperature": float(payload.get("temperature") or 0.0),
                "basis": "recorded"}
    # No arm on the row. `serving_stack.model` is the echo of the alias SENT -
    # Block E correction 4 established that it cannot move, which makes it
    # useless as a drift detector and for that reason a faithful record of what
    # was asked for. 396 of the legacy runs carry it; 115 older ones carry
    # nothing, and those fall back on the CODE argument above rather than on a
    # reading of the file. Both land on the greedy default, and the two are not
    # reported as the same kind of knowledge.
    echoed = (payload.get("serving_stack") or {}).get("model")
    return {"model_alias": str(echoed) if echoed else LEGACY_ARM_ALIAS,
            "temperature": LEGACY_ARM_TEMPERATURE,
            "basis": "reconstructed" if echoed else "assumed"}


def archives_on_arm(archives: list[tuple[dict, str]],
                    arm: dict) -> tuple[list, list]:
    """Split archived runs into (on this arm, on any other). Pure.

    Ruling 36 in the per-run archive. Until 2026-08-28 every run in
    `eval/answer_runs/` was greedy haiku, so a universal quantifier over the
    directory - `every archived Aksum answer fails` - was a claim about one arm
    that did not have to say so. The sonnet arm put 165 runs on another arm in
    the same directory and that assertion became a claim about two models,
    which is not what anyone wrote.

    BOTH halves are returned, so a caller can assert that the filter excluded
    something. A filter that silently matches everything, or nothing, turns
    every universal built on it into a vacuous truth.
    """
    want = (str(arm["model_alias"]), float(arm["temperature"]))
    on, off = [], []
    for payload, name in archives:
        got = payload_arm(payload)
        target = on if (got["model_alias"], got["temperature"]) == want else off
        target.append((payload, name))
    return on, off


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
                   runs_dir: Path | None = None,
                   archives: list[tuple[dict, str]] | None = None
                   ) -> tuple[list[CaseResult], list[str]]:
    """`archives` scores a caller-supplied subset - see `archives_on_arm`.
    Omitted, it reads the whole directory exactly as before."""
    results, unmatched = [], []
    for payload, name in (archives if archives is not None
                          else load_archives(runs_dir)):
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
# Block E — the variance decomposition, which is G4's actual deliverable
# --------------------------------------------------------------------------
#
# D4 built two stability RATES, and ruling 35 constrains what they may be
# called: per-session stability is a statement about VERDICTS and may not be
# quoted as one about behaviour. G4 asks a different question — "how much is
# session, how much is case" — and a rate cannot answer it. On 2026-08-25 both
# rates read 100%, which is the sentence "nothing is moving", printed over six
# cases whose every answer text had changed between the two sessions
# (FINDING 18).
#
# So there are TWO decompositions here and not one, over two different response
# variables, and neither is a summary of the other:
#
#   decompose_verdicts   components of variance for content_ok, case x session
#                        crossed. Answers "when the VERDICT moves, what moved
#                        it".
#   decompose_texts      a partition of pairwise agreement over the answer
#                        TEXT. Answers "when the OUTPUT moves, what moved it".
#
# On the D4 archives the first puts ~all the variance on the case term and none
# on the session term, and the second reports agreement collapsing entirely at
# the session boundary. Both are correct. A report carrying only the first says
# the system is stable, and that is the claim FINDING 18 exists to refuse.
#
# Both are PURE and take rows in the shape run_answer_sweep archives them, so
# they run in the offline suite with no database, no gateway and no chat call,
# and they were built and mutation-verified against the two D4 pilot sweeps
# BEFORE Block E spent 270 calls. That ordering is the point: an instrument
# first run on the data it was built to measure has never been wrong in a way
# anyone could see.

DECOMPOSITION_TERMS = ("case", "session", "case_x_session", "residual")

# Components of variance are differences of mean squares and land on exact
# zeros constantly here — a binary response with unanimous cells makes SS_E
# exactly 0. Compare against a tolerance rather than 0.0 so that -4e-18 is not
# reported as a negative estimate.
_TINY = 1e-12


def _mean(values) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def _decomposition_rows(rows: list[dict], value_key: str) -> dict:
    """The checks both decompositions share, and their refusals.

    Refusals rather than exceptions, for the reason calibration_eligibility
    gives: the caller is a report, the report should print what is wrong with
    its own input, and an exception in a printer destroyed a twenty-six-minute
    run on 2026-08-16.
    """
    refusals: list[str] = []
    versions = sorted({r.get("prompt_version") for r in rows})
    dated = [r for r in rows if r.get("session_id")]
    without = len(rows) - len(dated)

    # Block F decision 2. The same argument as the prompt-version refusal
    # directly below, for the factor that was not recorded until Block F: rows
    # from two arms pooled into one decomposition charge the difference between
    # two MODELS to the residual and print it as sampling noise. Rows archived
    # before Block F carry no arm and are all one arm, so a set containing any
    # of them plus one labelled row is exactly the case this refuses.
    arms = sorted({(r.get("model_alias"), r.get("temperature"))
                   for r in rows if r.get("model_alias") is not None})
    if len(arms) > 1:
        refusals.append(
            f"{len(arms)} arms in one decomposition ("
            + "; ".join(f"{alias} at temperature {float(temp or 0.0):g}"
                        for alias, temp in arms)
            + "). Pooling them charges the difference between two models to "
              "the residual and reports it as sampling noise. Decompose each "
              "arm separately."
        )

    if len(versions) > 1:
        # Pooling two prompt versions puts PROMPT VERSION into the residual
        # term and reports it as sampling noise. Part 8's entire archived grid
        # is two prompt versions, so this is not a hypothetical input: it is
        # the shape of eval/sweeps/20260810T191414-*.json, which is on disk.
        refusals.append(
            f"{len(versions)} prompt versions in one decomposition "
            f"({', '.join(str(v) for v in versions)}). Pooling them charges the "
            f"difference between two prompts to the residual and reports it as "
            f"sampling noise. Decompose each version separately."
        )
    if not dated:
        refusals.append(
            "no row carries a session identity, so there is no session term to "
            "estimate. Rows archived before D4 cannot be given one after the "
            "fact."
        )
    return {"refusals": refusals, "dated": dated,
            "rows_without_session": without,
            "prompt_version": versions[0] if len(versions) == 1 else None}


def decompose_verdicts(rows: list[dict], value_key: str = "content_ok") -> dict:
    """Components of variance for a run outcome, case x session crossed.

    The model is the balanced two-way random-effects one, with interaction:

        y_ijk = mu + case_i + session_j + (case x session)_ij + e_ijk

    Both factors are random: the thirty cases are a sample of the questions
    this corpus could be asked, and the three days are a sample of the days the
    provider could serve. Expected mean squares for the balanced design give

        var(residual)       = MS_E
        var(case x session) = (MS_AB - MS_E) / n
        var(session)        = (MS_B  - MS_AB) / (n * a)
        var(case)           = (MS_A  - MS_AB) / (n * b)

    with a cases, b sessions, n repetitions per cell.

    Three things this refuses to do, each of which would produce a number that
    looks like an answer:

    1. It refuses an UNBALANCED grid. The estimators above are only these
       expressions when every (case, session) cell holds the same n. A sweep
       that lost a case to a rate limit on day 2 is unbalanced, and silently
       running the balanced arithmetic over it charges the missing runs to
       whichever term the imbalance happens to load. The refusal names the
       cells.

    2. It refuses to CLAMP a negative estimate without saying so. A negative
       variance estimate is not a bug and not an error: it is what this
       estimator does when the true component is near zero, and it is
       information — it says the term is not distinguishable from nothing.
       Clamping to 0 is right for reporting a share and wrong for reporting a
       finding, so both are returned and `negative_estimates` names any term
       that needed clamping.

    3. It refuses to print SHARES when total variance is zero. Every run
       agreeing is the commonest outcome here — five of six D4 cells were
       unanimous — and 0/0 rendered as a percentage is the vacuous pass this
       repository keeps paying for. `shares` is None and the printer says NOT
       MEASURED.
    """
    shared = _decomposition_rows(rows, value_key)
    refusals = list(shared["refusals"])
    dated = shared["dated"]

    cells: dict[tuple[str, str], list[float]] = {}
    for row in dated:
        cells.setdefault((row["case"], row["session_id"]), []).append(
            float(bool(row.get(value_key))))

    cases = sorted({case for case, _ in cells})
    sessions = sorted({session for _, session in cells})
    a, b = len(cases), len(sessions)

    sizes = sorted({len(v) for v in cells.values()})
    n = sizes[0] if sizes else 0
    missing = [(c, s) for c in cases for s in sessions if (c, s) not in cells]
    if dated:
        if a < 2:
            refusals.append(
                f"{a} case(s). A case term cannot be estimated from one case.")
        if b < 2:
            refusals.append(
                f"{b} session(s). A session term cannot be estimated from one "
                f"session — that is the state every sweep before D4 is in, and "
                f"it is why the per-session stability number printed NOT "
                f"MEASURED rather than 100%.")
        if n < 2:
            refusals.append(
                f"{n} repetition(s) per cell. With one run per cell the "
                f"residual and the interaction are the same quantity and "
                f"neither can be separated from the other.")
        if missing:
            refusals.append(
                f"the grid is INCOMPLETE: {len(missing)} of {a * b} "
                f"(case, session) cells are absent — "
                + ", ".join(f"{c}/{s[:8]}" for c, s in missing[:6])
                + ("…" if len(missing) > 6 else "")
                + ". The balanced estimators are not these expressions on an "
                  "incomplete grid.")
        elif len(sizes) > 1:
            uneven = sorted(
                (f"{c}/{s[:8]}", len(v)) for (c, s), v in cells.items()
                if len(v) != sizes[-1])
            refusals.append(
                f"the grid is UNBALANCED: cell sizes {sizes}. "
                + ", ".join(f"{name} has {k}" for name, k in uneven[:6])
                + ("…" if len(uneven) > 6 else "")
                + ". Charging an imbalance to whichever term absorbs it is not "
                  "a decomposition.")

    out = {
        "value": value_key,
        "prompt_version": shared["prompt_version"],
        "refusals": refusals,
        "may_report": False,
        "cases": a,
        "sessions": b,
        "repetitions": n,
        "runs": len(dated),
        "rows_without_session": shared["rows_without_session"],
        "mean": None,
        "mean_squares": None,
        "components_raw": None,
        "components": None,
        "shares": None,
        "negative_estimates": [],
        "total_variance": None,
    }
    if refusals:
        return out

    grand = _mean(v for values in cells.values() for v in values)
    case_mean = {c: _mean(v for s in sessions for v in cells[(c, s)])
                 for c in cases}
    session_mean = {s: _mean(v for c in cases for v in cells[(c, s)])
                    for s in sessions}
    cell_mean = {k: _mean(v) for k, v in cells.items()}

    ss_a = n * b * sum((case_mean[c] - grand) ** 2 for c in cases)
    ss_b = n * a * sum((session_mean[s] - grand) ** 2 for s in sessions)
    ss_ab = n * sum(
        (cell_mean[(c, s)] - case_mean[c] - session_mean[s] + grand) ** 2
        for c in cases for s in sessions)
    ss_e = sum((v - cell_mean[(c, s)]) ** 2
               for c in cases for s in sessions for v in cells[(c, s)])

    ms_a = ss_a / (a - 1)
    ms_b = ss_b / (b - 1)
    ms_ab = ss_ab / ((a - 1) * (b - 1))
    ms_e = ss_e / (a * b * (n - 1))

    raw = {
        "case": (ms_a - ms_ab) / (n * b),
        "session": (ms_b - ms_ab) / (n * a),
        "case_x_session": (ms_ab - ms_e) / n,
        "residual": ms_e,
    }
    negative = sorted(k for k, v in raw.items() if v < -_TINY)
    clamped = {k: (v if v > _TINY else 0.0) for k, v in raw.items()}
    total = sum(clamped.values())

    out.update({
        "may_report": True,
        "mean": grand,
        "mean_squares": {"case": ms_a, "session": ms_b,
                         "case_x_session": ms_ab, "residual": ms_e},
        "components_raw": raw,
        "components": clamped,
        "negative_estimates": negative,
        "total_variance": total,
        # None, not zeros. Every run agreeing is a real and common outcome and
        # it has no decomposition: there is no variance to apportion. Saying
        # "case 0%, session 0%" would be four numbers that add to nothing.
        "shares": ({k: clamped[k] / total for k in DECOMPOSITION_TERMS}
                   if total > _TINY else None),
    })
    return out


def decompose_texts(rows: list[dict], text_key: str = "answer") -> dict:
    """Where the ANSWER TEXT stops agreeing with itself: within a session, or
    across sessions.

    Not a components-of-variance model, deliberately. Answer text has no honest
    continuous scale — chrF against what? the modal text? which is chosen by
    the data — and inventing one to feed an ANOVA would put a modelling
    decision underneath G4's headline number. Pairwise agreement needs no such
    choice: two runs either produced the same text or they did not, and every
    figure below is a count over a named denominator.

    Three rates, and the third is the one that stops the other two being
    misread:

      within_session   P(same text | same case, same session)
      across_sessions  P(same text | same case, different session)
      cross_case       P(same text | DIFFERENT case) — the baseline. It should
                       be ~0. If it is not, identical refusal boilerplate is
                       being emitted for unrelated questions, and the other two
                       rates are measuring a template rather than an answer.
                       That is a finding, and nothing else here would show it.

    `agreement_lost_at_the_session_boundary` is within_session - across_sessions.
    It is the text-side answer to G4's question. On the D4 archives it is large:
    five of six cases were internally unanimous and shared NOTHING across the
    date boundary, while the verdict decomposition put nothing at all on the
    session term.
    """
    shared = _decomposition_rows(rows, text_key)
    refusals = list(shared["refusals"])
    dated = shared["dated"]

    by_case: dict[str, dict[str, list[str]]] = {}
    for row in dated:
        text = (row.get(text_key) or "").strip()
        by_case.setdefault(row["case"], {}).setdefault(
            row["session_id"], []).append(text)

    within_pairs = within_agree = 0
    cross_pairs = cross_agree = 0
    per_case = []
    for case_id in sorted(by_case):
        sessions = by_case[case_id]
        c_within = c_within_ok = c_cross = c_cross_ok = 0
        for texts in sessions.values():
            for i in range(len(texts)):
                for j in range(i + 1, len(texts)):
                    c_within += 1
                    c_within_ok += texts[i] == texts[j]
        ids = sorted(sessions)
        for x in range(len(ids)):
            for y in range(x + 1, len(ids)):
                for left in sessions[ids[x]]:
                    for right in sessions[ids[y]]:
                        c_cross += 1
                        c_cross_ok += left == right
        within_pairs += c_within
        within_agree += c_within_ok
        cross_pairs += c_cross
        cross_agree += c_cross_ok
        per_case.append({
            "case": case_id,
            "sessions": len(ids),
            "within_session": f"{c_within_ok}/{c_within}",
            "across_sessions": f"{c_cross_ok}/{c_cross}",
            "distinct_texts_overall": len({t for ts in sessions.values()
                                           for t in ts}),
            "distinct_texts_per_session": {s: len(set(ts))
                                           for s, ts in sorted(sessions.items())},
            # Named, not counted — the house rule. "agreement 0.33" is a
            # number; "this case was word for word identical on both days" and
            # "this case shared not one character across the boundary" are
            # things a person can act on, and FINDING 18 was only ever legible
            # in that form.
            "identical_across_every_session": c_cross > 0 and c_cross_ok == c_cross,
            "shared_nothing_across_sessions": c_cross > 0 and c_cross_ok == 0,
        })

    flat = [(case_id, text) for case_id, sessions in by_case.items()
            for texts in sessions.values() for text in texts]
    base_pairs = base_agree = 0
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i][0] != flat[j][0]:
                base_pairs += 1
                base_agree += flat[i][1] == flat[j][1]

    if dated and not cross_pairs:
        refusals.append(
            "no case was seen in two sessions, so there is no session boundary "
            "to measure agreement across.")

    within_rate = (within_agree / within_pairs) if within_pairs else None
    cross_rate = (cross_agree / cross_pairs) if cross_pairs else None
    return {
        "value": text_key,
        "prompt_version": shared["prompt_version"],
        "refusals": refusals,
        "may_report": not refusals,
        "rows_without_session": shared["rows_without_session"],
        "runs": len(dated),
        "within_session": {"agree": within_agree, "pairs": within_pairs,
                           "rate": within_rate},
        "across_sessions": {"agree": cross_agree, "pairs": cross_pairs,
                            "rate": cross_rate},
        "cross_case_baseline": {"agree": base_agree, "pairs": base_pairs,
                                "rate": (base_agree / base_pairs)
                                if base_pairs else None},
        "agreement_lost_at_the_session_boundary": (
            (within_rate - cross_rate)
            if within_rate is not None and cross_rate is not None else None),
        "per_case": per_case,
    }


def print_decomposition(verdicts: dict, texts: dict) -> None:
    """Both, always, and never one without the other.

    They are printed together because the pair is the finding. FINDING 18 is
    what it looks like when the first says 'nothing moved' and the second says
    'everything did', and a reader given only one of them would have written
    down the opposite of what happened.
    """
    print("\n" + "=" * 72)
    print("variance decomposition — G4's deliverable, over TWO response "
          "variables")
    print("=" * 72)

    label = verdicts.get("prompt_version") or "?"
    print(f"\n  VERDICTS ({verdicts['value']}), prompt {label}")
    if verdicts["refusals"]:
        print("    NOT COMPUTED:")
        for refusal in verdicts["refusals"]:
            print(f"      - {refusal}")
    else:
        print(f"    {verdicts['cases']} case(s) x {verdicts['sessions']} "
              f"session(s) x {verdicts['repetitions']} repetition(s) = "
              f"{verdicts['runs']} run(s), balanced")
        print(f"    mean {verdicts['mean']:.3f}")
        if verdicts["shares"] is None:
            print("    total variance is zero — every run agreed. NOT "
                  "MEASURED, and not 0%: there is no variance to apportion.")
        else:
            for term in DECOMPOSITION_TERMS:
                raw = verdicts["components_raw"][term]
                share = verdicts["shares"][term]
                flag = "  (negative estimate, clamped)" \
                    if term in verdicts["negative_estimates"] else ""
                print(f"      {term:<16} {share:6.1%}   var {raw:+.5f}{flag}")
        if verdicts["negative_estimates"]:
            print("    A negative estimate is not an error: it is this "
                  "estimator saying the\n    term is not distinguishable from "
                  "zero. Reported, then clamped for the\n    share — never "
                  "clamped silently.")

    print(f"\n  ANSWER TEXT ({texts['value']}), pairwise agreement")
    if texts["refusals"]:
        print("    NOT COMPUTED:")
        for refusal in texts["refusals"]:
            print(f"      - {refusal}")
    else:
        for key, name in (("within_session", "within a session "),
                          ("across_sessions", "across sessions  "),
                          ("cross_case_baseline", "different case   ")):
            block = texts[key]
            if not block["pairs"]:
                print(f"      {name} NOT MEASURED — no such pair")
                continue
            print(f"      {name} {block['agree']}/{block['pairs']} = "
                  f"{block['rate']:.0%}")
        lost = texts["agreement_lost_at_the_session_boundary"]
        if lost is not None:
            print(f"\n      agreement lost at the session boundary: "
                  f"{lost:+.0%}")
        base = texts["cross_case_baseline"]["rate"]
        if base is not None and base > 0.01:
            print(f"      NOTE: {base:.0%} of pairs from DIFFERENT cases are "
                  f"byte-identical. The two\n      rates above are partly "
                  f"measuring a shared refusal template, not an answer.")
        identical = [c["case"] for c in texts["per_case"]
                     if c["identical_across_every_session"]]
        nothing = [c["case"] for c in texts["per_case"]
                   if c["shared_nothing_across_sessions"]]
        if identical:
            print(f"\n      byte-identical in every session: "
                  f"{', '.join(identical)}")
        if nothing:
            print(f"      shared NOTHING across sessions: "
                  f"{', '.join(nothing)}")

    if verdicts.get("may_report") and texts.get("may_report"):
        v_session = (verdicts["shares"] or {}).get("session")
        lost = texts["agreement_lost_at_the_session_boundary"]
        if v_session is not None and lost is not None \
                and v_session < 0.05 and lost > 0.5:
            print(
                "\n  READ THESE TOGETHER. The verdict decomposition puts "
                f"{v_session:.0%} on the session\n  term and the text "
                f"agreement loses {lost:.0%} at the session boundary. The "
                "system\n  reached the same verdicts on different days by "
                "saying different things —\n  FINDING 18, reproduced. A report "
                "carrying only the verdict number would\n  have called this "
                "stable."
            )


# --------------------------------------------------------------------------
# FINDING 14 — did the corpus move underneath the sweep?
# --------------------------------------------------------------------------

def corpus_moved(before: dict, after: dict) -> str | None:
    """What changed in the corpus while a sweep was running, or None.

    Pure. `before` and `after` are `answer_store.corpus_version(conn)` dicts.

    FINDING 14, 2026-08-24. D1 made `run_answer` record the corpus version in
    the `answers` row and the per-run archive. `eval/run_answer_sweep.py`
    builds its own payload, never set `answer.corpus_version`, and therefore
    wrote NULL into `seed_corpus_digest` and no key into the archive — for
    every one of the 60 sweep runs on disk, and for every one of Block E's
    ~270. The fix landed in the path that writes about one archive and not in
    the path that writes the other 270. Same shape as FINDING 10's half fix.

    Reading it ONCE, as `run_answer` does before its repetition loop, is right
    for one question and not enough here. A day of Block E is ~90 chat calls
    and well over half an hour, and the claim being made is precisely that the
    corpus did not move during it. A version captured only at the start records
    what the sweep BEGAN against, which is a different sentence.

    So: named, never counted. "the digest changed" is a fact; "these two
    records changed and this one appeared" is something a person can act on,
    and on 2026-08-22 the digest changed three times in one day.
    """
    if not before or not after:
        return None
    if before.get("seed_corpus_digest") == after.get("seed_corpus_digest"):
        return None

    was = before.get("record_hashes") or {}
    now = after.get("record_hashes") or {}
    changed = sorted(d for d in set(was) & set(now) if was[d] != now[d])
    vanished = sorted(set(was) - set(now))
    appeared = sorted(set(now) - set(was))

    lines = [
        "THE CORPUS MOVED WHILE THIS SWEEP WAS RUNNING.",
        f"  digest {before.get('seed_corpus_digest', '?')[:16]}… -> "
        f"{after.get('seed_corpus_digest', '?')[:16]}…",
        f"  records {before.get('seed_record_count')} -> "
        f"{after.get('seed_record_count')}",
    ]
    for label, ids in (("changed", changed), ("vanished", vanished),
                       ("appeared", appeared)):
        if ids:
            lines.append(f"  {label}: {', '.join(ids)}")
    if not (changed or vanished or appeared):
        # The digest covers sorted (doc_id, hash) pairs, so it cannot move
        # while every pair is identical. Said out loud rather than reported as
        # an empty list, because an unexplained digest change is a finding
        # about the digest.
        lines.append("  no record differs, yet the digest moved — that is a "
                     "finding about corpus_digest itself, not about the corpus")
    lines.append(
        "  Every answer before the change and every answer after it were made "
        "against different corpora. The runs are archived and are not "
        "comparable to each other."
    )
    return "\n".join(lines)


# --------------------------------------------------------------------------
# D4 — calibration refuses to be written from too few days
# --------------------------------------------------------------------------

# Block F decision 2, 2026-08-28. What produced these numbers, expressed as
# the pair that decides comparability.
LEGACY_ARM_TEMPERATURE = 0.0
# The alias every answer archived before 2026-08-28 was made on. Not a default
# and not a guess: until that day `assemble.assemble` had no `model` of its own
# to pass and the answer path could not send anything else. It is the same
# argument ruling 36 accepted for the nine legacy sweeps' temperature, and it
# is labelled wherever it is used rather than presented as a reading.
LEGACY_ARM_ALIAS = "chat-default"


def sweep_arm(sweep: dict) -> dict:
    """The (model alias, temperature) a sweep was run on, and how that is known.

    Why this function is not `sweep["arm"]["model_alias"]`
    -----------------------------------------------------

    Nine sweeps are archived and not one of them records an arm. Every number
    Block E published is denominated in a model and a temperature that were
    facts about the code on the day, not about the archive — exactly the shape
    of FINDING 14 (a corpus version that lived in the runner rather than in the
    run) one layer up. The sonnet arm makes that gap load-bearing: two archives
    that differ only in the thing neither of them records.

    So the arm is RECONSTRUCTED for the nine, from evidence that is on disk,
    and only from evidence that is on disk:

      * the ALIAS comes from `serving_stack.model` on the rows. Block E
        correction 4 established that this field is the echo of the string
        SENT and cannot move — useless as a drift detector, which is precisely
        what makes it a faithful record of what the sweep asked for.
      * the TEMPERATURE cannot be read from the archive at all, because
        `assemble.assemble` had no temperature parameter until Block F: the
        answer path could not send anything but 0. That is a claim about the
        code and not about the file, so it is `assumed` rather than `read`,
        and it is stated in the return value rather than folded silently into
        an equality test.

    A sweep archived AFTER the runner learned to record an arm carries one, and
    a missing arm block then means the sweep came from somewhere else. Callers
    are told which of the two they have: `basis` is "recorded" or
    "reconstructed", and `reconstructed` is never treated as a positive
    identification of the arm — it is only ever enough to say "this is the
    legacy greedy arm, or it is not identifiable".
    """
    recorded = sweep.get("arm")
    if isinstance(recorded, dict) and recorded.get("model_alias"):
        return {"model_alias": recorded["model_alias"],
                "temperature": float(recorded.get("temperature") or 0.0),
                "basis": "recorded",
                "note": ""}

    rows = sweep.get("results") or []
    aliases = sorted({
        (row.get("model_alias")
         or ((row.get("serving_stack") or {}).get("model")))
        for row in rows
    } - {None})
    if len(aliases) == 1:
        return {"model_alias": aliases[0],
                "temperature": LEGACY_ARM_TEMPERATURE,
                "basis": "reconstructed",
                "note": "alias read from serving_stack.model on the rows; "
                        "temperature assumed 0 because the answer path could "
                        "not send another value before Block F"}
    if len(aliases) > 1:
        return {"model_alias": None, "temperature": None,
                "basis": "unidentifiable",
                "note": f"{len(aliases)} distinct aliases on the rows of one "
                        f"sweep: {', '.join(aliases)}"}
    return {"model_alias": None, "temperature": None,
            "basis": "unidentifiable",
            "note": "no arm block, and no row records an alias"}


def calibration_eligibility(sweeps: list[dict], floor: dict,
                            names: list[str] | None = None) -> dict:
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

    Block E, 2026-08-26 — the SCOPE, and why it is a rule and not a judgement
    ------------------------------------------------------------------------

    Until this was added, an undated sweep was an unconditional refusal. Three
    such sweeps are on disk and can never be given a session identity, so
    `calibrated: true` was unreachable at ANY number of dates — not merely
    blocked until three. D4's report never showed this, because it refused on
    the date count first and stopped reading.

    The second problem is the pilots. Both carry real session identity, and
    both ran SIX cases where Block E runs the full stratified set. A floor
    calibrated across a 6-case date and a 30-case date is a floor whose
    denominator changes between dates, which is the failure
    min_distinct_dates_note was written to prevent one level down.

    One rule handles both, and it lives in `floor.json.calibration_scope`: a
    sweep calibrates only if it carries a session identity AND ran at least
    `min_cases_per_sweep` cases. A sweep failing the rule blocks calibration
    outright UNLESS it is NAMED in `excluded_by_rule`.

    And the guard that stops the list being a loophole: a sweep named there
    which SATISFIES the rule is itself a refusal. Without that check, the list
    is a place to put a sweep whose numbers someone did not like — the exact
    move this whole file exists to make impossible. Excluding by a recorded
    rule is a diff. Excluding by moving files is not, and is why the rule names
    the archives rather than the archives being deleted.

    `names` is the archive filename for each sweep, positionally. Callers that
    do not have them — every unit fixture — pass none, no sweep can then be
    matched to the exclusion list, and the pre-Block-E behaviour is exactly
    unchanged.
    """
    minimum = int(floor["min_distinct_dates"])
    reps_needed = int(floor["min_repetitions"])
    scope = floor.get("calibration_scope") or {}
    min_cases = int(scope.get("min_cases_per_sweep") or 0)
    named = dict(scope.get("excluded_by_rule") or {})
    # Block F decision 2. The arm this floor calibrates from. Absent means the
    # clause is not declared and nothing is checked, which is the pre-Block-F
    # behaviour exactly — a floor file written before the clause existed does
    # not silently acquire it.
    declared_arm = scope.get("arm") or {}
    if names is None:
        names = [None] * len(sweeps)

    eligible: list[dict] = []
    eligible_indexes: list[int] = []
    excluded: list[dict] = []
    blocking: list[dict] = []
    wrongly_excluded: list[str] = []
    undated_total = 0

    for index, (sweep, name) in enumerate(zip(sweeps, names)):
        session = sweep.get("session") or {}
        cases = {row.get("case") for row in (sweep.get("results") or [])}
        fails: list[str] = []
        if not (session.get("id") and session.get("date")):
            fails.append("carries no session identity")
            undated_total += 1
        if min_cases and len(cases) < min_cases:
            fails.append(f"ran {len(cases)} case(s), below the {min_cases} "
                         f"this floor calibrates from")
        # Block E, 2026-08-26. A day that lost four of its ninety-nine calls
        # has 33 cases and would pass the case-set test above while carrying a
        # hole in its grid. The sweep itself already refuses to compute a floor
        # verdict on one; this stops the same sweep calibrating the floor from
        # the other end.
        if sweep.get("incomplete"):
            fails.append(f"archived INCOMPLETE: {len(sweep['incomplete'])} "
                         f"cell(s) never returned")
        # Block F decision 2, 2026-08-28, declared BEFORE the sonnet arm ran
        # and for that reason. Every archived number is haiku at temperature 0.
        # A sonnet arm at temperature 1 carries a session identity and runs the
        # full 33 cases, so it SATISFIES every other clause of this rule — and
        # `a_named_sweep_must_actually_fail_the_rule` then makes it impossible
        # to exclude by name. The arm has to be part of the rule, or the
        # anti-loophole becomes the loophole: the file's own guard would insist
        # that a temperature-1 sonnet sweep calibrate a floor set on greedy
        # haiku. Declared in advance because a scope settled after seeing the
        # sonnet numbers is a scope chosen to fit them.
        arm = sweep_arm(sweep)
        if declared_arm:
            want = (declared_arm.get("model_alias"),
                    float(declared_arm.get("temperature") or 0.0))
            if arm["basis"] == "unidentifiable":
                fails.append(f"records no identifiable arm ({arm['note']}), "
                             f"and this floor calibrates only from "
                             f"{want[0]} at temperature {want[1]:g}")
            elif (arm["model_alias"], arm["temperature"]) != want:
                fails.append(
                    f"ran {arm['model_alias']} at temperature "
                    f"{arm['temperature']:g}, not the {want[0]} at temperature "
                    f"{want[1]:g} this floor calibrates from")
        entry = {"sweep": name, "fails": fails, "arm": arm}
        if not fails:
            # A sweep that qualifies cannot be excluded. This is the whole
            # anti-loophole, and it is one line.
            if name is not None and name in named:
                wrongly_excluded.append(name)
            eligible.append(sweep)
            eligible_indexes.append(index)
        elif name is not None and name in named:
            excluded.append({**entry, "recorded_reason": named[name]})
        else:
            blocking.append(entry)

    dates = sorted({(s.get("session") or {})["date"] for s in eligible})
    sessions = sorted({(s.get("session") or {})["id"] for s in eligible})
    per_date: dict[str, int] = {}
    for sweep in eligible:
        date = (sweep.get("session") or {})["date"]
        per_date[date] = per_date.get(date, 0) + 1

    refusals: list[str] = []
    if wrongly_excluded:
        refusals.append(
            f"{len(wrongly_excluded)} sweep(s) named in "
            f"calibration_scope.excluded_by_rule SATISFY the rule and may not "
            f"be excluded by it: {', '.join(sorted(wrongly_excluded))}. A list "
            f"that can hold a qualifying sweep is a place to put numbers "
            f"nobody liked."
        )
    unnamed_undated = [b for b in blocking
                       if "carries no session identity" in b["fails"]]
    if unnamed_undated:
        refusals.append(
            f"{len(unnamed_undated)} sweep(s) carry no session identity and "
            f"count toward no date. They were archived before D4 and cannot be "
            f"given one now: a date assigned after the fact is the "
            f"calibration this file already records as invalid. Exclude them "
            f"by name in calibration_scope.excluded_by_rule, or they block."
        )
    out_of_scope = [b for b in blocking if b not in unnamed_undated]
    if out_of_scope:
        refusals.append(
            f"{len(out_of_scope)} sweep(s) fall outside "
            f"calibration_scope and are not named in excluded_by_rule: "
            + "; ".join(f"{b['sweep'] or 'unnamed'} ({', '.join(b['fails'])})"
                        for b in out_of_scope)
        )
    if len(dates) < minimum:
        refusals.append(
            f"{len(dates)} distinct date(s), and the floor requires "
            f"{minimum}. Repetitions within one session are correlated and "
            f"are not independent samples — a floor calibrated from fewer is "
            f"a within-session regression gate wearing the word 'calibrated'."
        )
    thin = [s for s in eligible if int(s.get("repeat", 0)) < reps_needed]
    if thin:
        refusals.append(
            f"{len(thin)} sweep(s) ran fewer than {reps_needed} repetitions. "
            f"A single shot is one sample of a distribution nobody has looked "
            f"at."
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
        "sweeps_without_session": undated_total,
        # Named, never merely subtracted. A sweep that left the calibration
        # silently is a sweep nobody can argue with later.
        "eligible_sweeps": len(eligible),
        # Positional, so a caller can recover the ROWS that calibrated the
        # floor without matching on filenames. What gets written into
        # floor.json must be computed over the sweeps that were allowed to
        # write it, or `calibrated_stability` reports numbers from archives
        # the calibration itself excluded.
        "eligible_indexes": eligible_indexes,
        "excluded_by_rule": excluded,
        "wrongly_excluded": sorted(wrongly_excluded),
        "min_cases_per_sweep": min_cases,
        "declared_arm": declared_arm or None,
        # Every arm seen, eligible or not, and how each was established. A
        # calibration standing on four sweeps whose arm was RECONSTRUCTED is a
        # different claim from one standing on four that recorded it, and the
        # difference should not have to be dug out of the code.
        "arms": [dict(sweep_arm(sweep), sweep=name)
                 for sweep, name in zip(sweeps, names)],
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
    print(f"  eligible sweeps    {verdict.get('eligible_sweeps', '?')}")
    if verdict.get("min_cases_per_sweep"):
        print(f"  scope: a sweep calibrates only if it carries a session "
              f"identity AND ran\n         at least "
              f"{verdict['min_cases_per_sweep']} cases "
              f"(floor.json calibration_scope)")
    for entry in verdict.get("excluded_by_rule") or []:
        # Named, never merely subtracted. A sweep that left the calibration
        # silently is a sweep nobody can argue with later.
        print(f"    excluded by rule  {entry['sweep']}")
        print(f"                      {'; '.join(entry['fails'])}")
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
