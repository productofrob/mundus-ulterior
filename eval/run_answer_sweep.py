"""Part 8: run every gold question under several prompt versions, repeatedly.

Why a sweep and not thirty invocations
--------------------------------------

Three things this does that a shell loop over `run_answer` would not:

1. **Each question is embedded once**, and the vector is reused across every
   prompt version and every repetition. Voyage's free tier is 3 requests/minute
   and the embedding depends on the question alone, so a 5 x 2 x 3 sweep costs 5
   embedding requests rather than 30. The chat calls cannot be shared — each is a
   different prompt or a different sample — so 30 remain 30.

2. **The evidence is built once per question.** Retrieval, folding and English
   resolution do not depend on the prompt, and rebuilding them per run would let
   an unrelated change move underneath the comparison. Holding them fixed is what
   makes prompt version the only variable.

3. **Questions come from the gold set**, so the sweep cannot drift from the
   harness that scores it. Adding a case adds it here.

What it is for
--------------

Part 8 owes two things: a prompt decision, and a floor. The archived grid says
v2 beat v3 on content, but every cell is a single shot, and Part 6 measured a
0.317 chrF spread within one case at temperature 0 while Part 7 watched a
rewording flip an exit code. A threshold set from single shots is one sample of a
distribution nobody has looked at.

So this prints the distribution, per case and per prompt version, and marks
UNSTABLE anything that lands differently across its own repetitions. A floor goes
where no observed case straddles it — the Part 6 rule — and this is what shows
where that is.

Usage (repo root, venv active, .env loaded, gateway up on :4000, db up):

    python -m eval.run_answer_sweep --dry-run
    python -m eval.run_answer_sweep --prompt-version p7-answer-v4 --repeat 1
    python -m eval.run_answer_sweep \
        --prompt-version p7-answer-v2r --prompt-version p7-answer-v4 --repeat 3

Cost: one embedding per question, one chat call per (question, prompt, repeat).
`--dry-run` spends the embeddings only and makes no chat call, which is the
cheapest way to find out that something is wrong before spending 30 of them.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import statistics
import sys
import time
from pathlib import Path

from answer import answer_store, assemble, translate
from answer.run_answer import _archive
from eval import answer_eval
from eval.goldset import (GoldSetError, load_answer_cases,
                          load_floor, load_profiles)

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

SWEEP_DIR = Path(__file__).resolve().parent / "sweeps"


def _resolved(answer) -> int:
    return sum(1 for s in answer.grounding.quote_spans if s.abs_start is not None)


def run_sweep(conn, cases, prompt_versions: list[str], repeat: int,
              k: int, max_sources: int, profiles: dict, pause: float,
              dry_run: bool, write: bool) -> dict:
    from ingest.embed import EmbeddingError, embed_query, resolve_model_label

    model_label = translate.resolve_model_label()
    embed_model = resolve_model_label()
    results: list[dict] = []
    evidence_report: list[dict] = []

    for case in cases:
        try:
            query_vector = embed_query(case.question)
        except EmbeddingError as exc:
            print(f"could not embed {case.id!r}: {exc}", file=sys.stderr)
            return {"error": str(exc)}

        passages = assemble.build_evidence(
            conn, query_vector, k=k, max_sources=max_sources, profiles=profiles,
        )
        evidence_report.append({
            "case": case.id,
            "passages": len(passages),
            "markers": [p.marker for p in passages],
            "chunks": [p.chunk_id for p in passages],
            "english_kinds": sorted({p.english.kind for p in passages}),
        })
        print(f"\n{case.id}: {len(passages)} source(s) — "
              f"{', '.join(sorted({p.english.kind for p in passages}))}")

        if dry_run:
            # Which passages, not merely how many. The Aksum question is the
            # reason: four archived answers refuse, and the only way to know
            # whether that is a retrieval failure or a reasoning one is to see
            # whether the passage carrying the answer is in the set and what
            # English is attached to it. A count cannot tell you that, and three
            # of Part 7's defects were found by looking at a dry run.
            for passage in passages:
                english = passage.english
                marker = f"[{passage.marker}]"
                print(f"    {marker:<5} {passage.chunk_id}")
                print(f"          sim {passage.similarity:.3f} | "
                      f"english={english.kind}"
                      + (f" ground={english.ground}" if english.ground else "")
                      + (f" band={english.band}" if english.band else ""))
                # The expectation the gold case makes of this question, checked
                # against the evidence before any chat call is paid for.
                for needle in (case.expect_answer_contains
                               + [w for group in case.expect_answer_contains_any
                                  for w in group]):
                    if english.text and needle.casefold() in english.text.casefold():
                        print(f"          gold term {needle!r} IS PRESENT in "
                              f"this passage's English")
            continue

        if not passages:
            continue

        for version in prompt_versions:
            for attempt in range(1, repeat + 1):
                answer = assemble.assemble(
                    case.question, passages,
                    model_label=model_label, profiles=profiles,
                    prompt_version=version,
                )
                answer.embedding_model = embed_model
                answer.retrieval_k = k

                stored_id = assemble.store(conn, answer) if write else None
                payload = {
                    "timestamp": _dt.datetime.now(_dt.timezone.utc)
                                    .isoformat(timespec="seconds"),
                    "question": answer.question,
                    "answer": answer.answer_text,
                    "grounded": answer.grounding.ok,
                    "refused": answer.refused,
                    "model": answer.model,
                    "prompt_version": answer.prompt_version,
                    "embedding_model": answer.embedding_model,
                    "answer_id": stored_id,
                    "grounding": answer.grounding.to_dict(),
                    "passages": [p.to_dict() for p in answer.passages],
                    "sources_block": answer.sources_block,
                    "sweep": {"case": case.id, "repetition": attempt,
                              "of": repeat},
                }
                archived = _archive(payload) if write else None

                scored = answer_eval.score_payload(
                    case, payload, source=archived or f"{case.id}/{version}/{attempt}"
                )
                results.append({
                    "case": case.id,
                    "prompt_version": version,
                    "repetition": attempt,
                    "content_ok": scored.ok,
                    "grounded": answer.grounding.ok,
                    "refused": answer.refused,
                    "resolved_quotes": _resolved(answer),
                    "answer": answer.answer_text,
                    "failures": [a.label for a in scored.failures],
                    "archived": archived,
                })
                mark = "PASS" if scored.ok else "FAIL"
                print(f"  {mark}  {version:<14} run {attempt}/{repeat}  "
                      f"grounded={answer.grounding.ok!s:<5} "
                      f"quotes={_resolved(answer)}")
                if pause:
                    time.sleep(pause)

    return {"results": results, "evidence": evidence_report}


# --------------------------------------------------------------------------
# Reading the distribution
# --------------------------------------------------------------------------

def summarise(results: list[dict]) -> dict:
    by_key: dict[tuple[str, str], list[dict]] = {}
    for row in results:
        by_key.setdefault((row["case"], row["prompt_version"]), []).append(row)

    cells = []
    for (case_id, version), rows in sorted(by_key.items()):
        content = {r["content_ok"] for r in rows}
        grounded = {r["grounded"] for r in rows}
        texts = {r["answer"].strip() for r in rows}
        quotes = [r["resolved_quotes"] for r in rows]
        cells.append({
            "case": case_id,
            "prompt_version": version,
            "n": len(rows),
            "content_pass": sum(1 for r in rows if r["content_ok"]),
            "content_stable": len(content) == 1,
            "grounded_pass": sum(1 for r in rows if r["grounded"]),
            "grounded_stable": len(grounded) == 1,
            "distinct_texts": len(texts),
            "quotes_min": min(quotes) if quotes else 0,
            "quotes_max": max(quotes) if quotes else 0,
            "refusal_rate": sum(1 for r in rows if r["refused"]) / len(rows),
        })

    by_version: dict[str, dict] = {}
    for version in sorted({c["prompt_version"] for c in cells}):
        mine = [c for c in cells if c["prompt_version"] == version]
        runs = [r for r in results if r["prompt_version"] == version]
        by_version[version] = {
            "cases": len(mine),
            "runs": len(runs),
            "content_pass_rate": sum(r["content_ok"] for r in runs) / len(runs),
            "grounded_rate": sum(r["grounded"] for r in runs) / len(runs),
            "refusal_rate": sum(r["refused"] for r in runs) / len(runs),
            "unstable_content_cells": sum(1 for c in mine if not c["content_stable"]),
            "unstable_grounded_cells": sum(1 for c in mine
                                           if not c["grounded_stable"]),
            "mean_resolved_quotes": statistics.mean(
                [r["resolved_quotes"] for r in runs]) if runs else 0.0,
        }
    return {"cells": cells, "by_version": by_version}


def print_summary(summary: dict) -> None:
    print("\n" + "=" * 72)
    print("per cell — case x prompt version, across repetitions")
    print("=" * 72)
    print(f"  {'case':<20} {'prompt':<15} {'content':<10} {'grounded':<10} "
          f"{'quotes':<9} texts")
    for cell in summary["cells"]:
        content = f"{cell['content_pass']}/{cell['n']}"
        if not cell["content_stable"]:
            content += " !"
        grounded = f"{cell['grounded_pass']}/{cell['n']}"
        if not cell["grounded_stable"]:
            grounded += " !"
        quotes = (f"{cell['quotes_min']}" if cell["quotes_min"] == cell["quotes_max"]
                  else f"{cell['quotes_min']}-{cell['quotes_max']}")
        print(f"  {cell['case']:<20} {cell['prompt_version']:<15} "
              f"{content:<10} {grounded:<10} {quotes:<9} {cell['distinct_texts']}")
    print("\n  ! = the metric landed differently across repetitions of an "
          "identical run.\n  A floor must not sit where a case straddles it "
          "(the Part 6 threshold rule).")

    print("\n" + "=" * 72)
    print("per prompt version")
    print("=" * 72)
    for version, stats in summary["by_version"].items():
        print(f"\n  {version}  ({stats['runs']} runs over {stats['cases']} cases)")
        print(f"    content pass rate  {stats['content_pass_rate']:.0%}")
        print(f"    grounded rate      {stats['grounded_rate']:.0%}")
        print(f"    refusal rate       {stats['refusal_rate']:.0%}")
        print(f"    mean resolved quotations  {stats['mean_resolved_quotes']:.1f}")
        print(f"    unstable cells: content {stats['unstable_content_cells']}, "
              f"grounded {stats['unstable_grounded_cells']}")

    versions = list(summary["by_version"])
    if len(versions) > 1:
        print("\n" + "=" * 72)
        print("the comparison")
        print("=" * 72)
        best = max(versions,
                   key=lambda v: summary["by_version"][v]["content_pass_rate"])
        for version in versions:
            stats = summary["by_version"][version]
            print(f"  {version:<15} content {stats['content_pass_rate']:.0%}  "
                  f"refusals {stats['refusal_rate']:.0%}  "
                  f"grounded {stats['grounded_rate']:.0%}")
        print(f"\n  Highest content pass rate: {best}.")
        print(
            "  Read refusal rate beside it, not after it. A prompt that refuses "
            "more\n  while erring no less is a regression, however tidy its "
            "citations — that\n  is the failure mode Part 8 was built to see, "
            "and the exit code cannot."
        )

    unstable = [c for c in summary["cells"]
                if not c["content_stable"] or not c["grounded_stable"]]
    print("\n" + "=" * 72)
    if unstable:
        print(f"{len(unstable)} unstable cell(s) — a floor placed on these "
              f"measures the sampler")
        for cell in unstable:
            print(f"  {cell['case']} / {cell['prompt_version']}: "
                  f"content {cell['content_pass']}/{cell['n']}, "
                  f"grounded {cell['grounded_pass']}/{cell['n']}")
    else:
        print("No unstable cells: every case landed the same way in every "
              "repetition.\nA floor set here is measuring the pipeline, not the "
              "sampler.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Part 8 — sweep gold questions across prompt versions"
    )
    parser.add_argument("--prompt-version", action="append", dest="prompt_versions",
                        choices=sorted(assemble.ANSWER_PROMPTS),
                        help="repeatable; defaults to the current version")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--case", action="append", help="only these case ids")
    parser.add_argument("--k", type=int, default=assemble.DEFAULT_K)
    parser.add_argument("--max-sources", type=int,
                        default=assemble.DEFAULT_MAX_SOURCES)
    parser.add_argument("--pause", type=float, default=0.0,
                        help="seconds between chat calls, if the account needs it")
    parser.add_argument("--dry-run", action="store_true",
                        help="embed and retrieve, make no chat call")
    parser.add_argument("--no-write", action="store_true",
                        help="do not store answers or archive runs")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.repeat < 1:
        parser.error("--repeat must be at least 1")
    versions = args.prompt_versions or [assemble.ANSWER_PROMPT_VERSION]

    try:
        cases = load_answer_cases()
        profiles = load_profiles()
    except GoldSetError as exc:
        print(f"gold set will not load: {exc}", file=sys.stderr)
        return 2
    if args.case:
        cases = [c for c in cases if c.id in set(args.case)]
        if not cases:
            print("no matching case ids", file=sys.stderr)
            return 2

    chat_calls = 0 if args.dry_run else len(cases) * len(versions) * args.repeat
    print(f"{len(cases)} question(s) x {len(versions)} prompt version(s) x "
          f"{args.repeat} repetition(s)")
    print(f"cost: {len(cases)} embedding request(s), {chat_calls} chat call(s)")
    if versions:
        print(f"prompts: {', '.join(versions)}")

    import psycopg

    try:
        from ingest.db import check_connection
        problem = check_connection(answer_store.get_dsn())
    except Exception:  # noqa: BLE001
        problem = None
    if problem:
        print(problem, file=sys.stderr)
        return 2

    with psycopg.connect(answer_store.get_dsn()) as conn:
        answer_store.apply_schema(conn)
        outcome = run_sweep(
            conn, cases, versions, args.repeat, args.k, args.max_sources,
            profiles, args.pause, args.dry_run, write=not args.no_write,
        )

    if "error" in outcome:
        return 2
    if args.dry_run:
        print("\ndry run — no chat call made, nothing written")
        if args.json:
            print(json.dumps(outcome["evidence"], indent=2, ensure_ascii=False))
        return 0

    results = outcome["results"]
    if not results:
        print("no runs completed", file=sys.stderr)
        return 2

    summary = summarise(results)
    verdicts = answer_eval.check_floor(summary, load_floor(), args.repeat)

    if not args.no_write:
        SWEEP_DIR.mkdir(parents=True, exist_ok=True)
        stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
        path = SWEEP_DIR / f"{stamp}-{'_'.join(versions)}-r{args.repeat}.json"
        path.write_text(json.dumps(
            {"prompt_versions": versions, "repeat": args.repeat,
             "results": results, "summary": summary,
             "floor": verdicts},
            indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nsweep archived: {path}")

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print_summary(summary)
        answer_eval.print_floor(verdicts)

    return 0 if all(v["meets_floor"] for v in verdicts.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
