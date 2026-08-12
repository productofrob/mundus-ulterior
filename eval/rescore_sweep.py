"""Re-score an archived sweep without spending a single API call.

The first live sweep was scored by a version of `answer_eval` that filtered
passages on a `cited` key which live payloads do not carry — so every content
case failed for a reason that had nothing to do with the answers. Thirty chat
calls, and the numbers were about the scorer.

They were not wasted, and that is the argument for archiving every run rather
than only the verdict: the answers, their grounding reports and their passages
are all on disk, so the fix is re-read rather than re-run. Part 6 learned this
with `eval/runs/` and Part 7 with `eval/answer_runs/`; this is the same
principle applied to the thing those directories were built for.

Usage:

    python -m eval.rescore_sweep                       # newest sweep
    python -m eval.rescore_sweep eval/sweeps/NAME.json
    python -m eval.rescore_sweep --write               # update the archive too

`--write` rewrites the sweep's `results` and `summary` in place and records what
scored them, so a re-scored file cannot be mistaken for the original run's
verdicts. The answers themselves are never touched.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

from eval import answer_eval
from eval.goldset import GoldSetError, load_answer_cases, load_floor
from eval.run_answer_sweep import SWEEP_DIR, print_summary, summarise


def newest_sweep() -> Path | None:
    files = sorted(SWEEP_DIR.glob("*.json")) if SWEEP_DIR.exists() else []
    return files[-1] if files else None


def rescore(sweep: dict, cases_by_id: dict) -> list[dict]:
    """Re-run the current scorer over the archived answers.

    The sweep archive stores each result's answer text but not the full payload,
    so the payload is rebuilt from the matching archived run in
    eval/answer_runs/ where one exists — that file holds the passages and the
    grounding report. Where it does not, the result is carried through unscored
    and marked, rather than silently kept at its old verdict.
    """
    runs_by_key: dict[tuple[str, str, str], dict] = {}
    for payload, name in answer_eval.load_archives():
        sweep_meta = payload.get("sweep") or {}
        if not sweep_meta:
            continue
        key = (
            sweep_meta.get("case"),
            payload.get("prompt_version"),
            str(sweep_meta.get("repetition")),
        )
        runs_by_key[key] = payload

    rescored: list[dict] = []
    for row in sweep["results"]:
        key = (row["case"], row["prompt_version"], str(row["repetition"]))
        payload = runs_by_key.get(key)
        case = cases_by_id.get(row["case"])
        if payload is None or case is None:
            row = dict(row)
            row["rescored"] = False
            row["rescore_note"] = (
                "no archived run found for this cell; verdict is the original "
                "run's and was produced by the scorer that had the cited-key bug"
            )
            rescored.append(row)
            continue

        result = answer_eval.score_payload(case, payload, source=row.get("archived") or "")
        rescored.append({
            **row,
            "content_ok": result.ok,
            "failures": [a.label for a in result.failures],
            "rescored": True,
        })
    return rescored


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Re-score an archived sweep")
    parser.add_argument("path", nargs="?", help="sweep file (default: newest)")
    parser.add_argument("--write", action="store_true",
                        help="rewrite the sweep archive with the new verdicts")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    path = Path(args.path) if args.path else newest_sweep()
    if path is None or not path.exists():
        print("no sweep archive found", file=sys.stderr)
        return 2

    try:
        cases_by_id = {c.id: c for c in load_answer_cases()}
    except GoldSetError as exc:
        print(f"gold set will not load: {exc}", file=sys.stderr)
        return 2

    sweep = json.loads(path.read_text(encoding="utf-8"))
    before = sum(1 for r in sweep["results"] if r["content_ok"])
    results = rescore(sweep, cases_by_id)
    after = sum(1 for r in results if r["content_ok"])
    missing = [r for r in results if not r.get("rescored")]

    print(f"re-scored {path.name}")
    print(f"  {len(results)} run(s), {len(results) - len(missing)} re-scored, "
          f"{len(missing)} carried through unscored")
    print(f"  content pass: {before} -> {after}")
    if missing:
        print("  cells with no archived run (verdict unchanged, treat as stale):")
        for row in missing:
            print(f"    {row['case']} / {row['prompt_version']} "
                  f"run {row['repetition']}")

    summary = summarise(results)
    verdicts = answer_eval.check_floor(summary, load_floor(), sweep.get("repeat", 1))
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print_summary(summary)
        answer_eval.print_floor(verdicts)

    if args.write:
        sweep["results"] = results
        sweep["summary"] = summary
        sweep["floor"] = verdicts
        sweep["rescored_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(
            timespec="seconds")
        sweep["rescore_note"] = (
            "Verdicts re-computed offline from the archived runs. The original "
            "verdicts were produced by a scorer that filtered passages on a "
            "`cited` key absent from live payloads, so every content case failed "
            "on expect_cited_docs regardless of the answer. The answers "
            "themselves are unchanged."
        )
        path.write_text(json.dumps(sweep, indent=2, ensure_ascii=False),
                        encoding="utf-8")
        print(f"\nsweep archive updated: {path}")
    else:
        print("\nnothing written — re-run with --write to update the archive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
