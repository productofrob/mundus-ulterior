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
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from eval.goldset import AnswerCase, GoldSetError, load_answer_cases

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
    question = normalise(payload.get("question") or "")
    for case in cases:
        if normalise(case.question) == question:
            return case
    return None


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
