"""Block E: the variance decomposition, read off the archived sweeps.

Why this is a program and not a paragraph in the result document
----------------------------------------------------------------

G4's checklist asks for four things, and three of them D4 already built. The
fourth is:

    a stated VARIANCE DECOMPOSITION — how much is session, how much is case —
    with the data archived

and `PHASE2_PLAN.md` adds: **the deliverable is the variance decomposition, not
the pass rate.** D4 built two stability RATES. A rate cannot answer that
question: on 2026-08-25 both rates read 100% over six cases whose every answer
text had changed between sessions (FINDING 18). Read as rates the system was
perfectly stable. It was not.

So this reports two decompositions, over two response variables, and prints
them together because the PAIR is the finding. `eval/answer_eval.py` holds the
arithmetic — pure, no database, no gateway, mutation-verified in
`scripts/mutate_part8.py`, and exercised in the offline suite on fixtures whose
answer is known by construction.

What it decomposes over, and why it never pools
-----------------------------------------------

Sweeps are grouped by their CASE SET and their prompt versions, and each group
is decomposed on its own. Nothing is pooled across a group boundary, ever:

  * pooling two prompt versions charges the difference between two PROMPTS to
    the residual and reports it as sampling noise. Part 8's archived grid is
    two prompt versions and it is on disk.
  * pooling a six-case pilot with a thirty-case sweep gives an incomplete
    case x session grid, on which the balanced estimators are not the
    expressions they are written as.

This is the same rule `floor.json.calibration_scope` states for calibration,
applied to the report rather than to the floor — one rule, in one place,
deciding what may be compared with what.

    python -m eval.decompose                 # every group, oldest first
    python -m eval.decompose --json          # the numbers, for a document
    python -m eval.decompose --write         # archive it under eval/decompositions/

Costs nothing: no gateway, no database, no embeddings. Reads files.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

from eval import answer_eval
from eval.calibrate_floor import load_sweeps

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

OUT_DIR = Path(__file__).resolve().parent / "decompositions"


def group_sweeps(archived: list[tuple[dict, str]]) -> list[dict]:
    """Sweeps that may be compared with each other, and nothing else.

    The key is (case set, prompt versions). Two sweeps that ran different
    questions are two measurements of two different things, and a grid built
    across them has holes in it — which `decompose_verdicts` refuses, but by
    then the refusal is all the report says. Grouping first means every group
    that CAN be decomposed is.
    """
    groups: dict[tuple, dict] = {}
    for sweep, name in archived:
        rows = sweep.get("results") or []
        key = (frozenset(row.get("case") for row in rows),
               frozenset(row.get("prompt_version") for row in rows))
        group = groups.setdefault(key, {
            "cases": sorted(c for c in key[0] if c),
            "prompt_versions": sorted(v for v in key[1] if v),
            "sweeps": [], "rows": [], "sessions": [], "dates": [],
        })
        group["sweeps"].append(name)
        group["rows"].extend(rows)
        session = sweep.get("session") or {}
        group["sessions"].append(session.get("id"))
        group["dates"].append(session.get("date"))
    return list(groups.values())


def decompose_group(group: dict) -> dict:
    rows = group["rows"]
    return {
        "sweeps": group["sweeps"],
        "cases": len(group["cases"]),
        "prompt_versions": group["prompt_versions"],
        "dates": sorted({d for d in group["dates"] if d}),
        "sessions": sorted({s for s in group["sessions"] if s}),
        "runs": len(rows),
        "verdicts": answer_eval.decompose_verdicts(rows),
        "texts": answer_eval.decompose_texts(rows),
        # Printed beside the decomposition on purpose. Ruling 35 constrains
        # what a stability rate may be CALLED; the decomposition is what it
        # could never say. Side by side, neither can be quoted as the other.
        "stability": answer_eval.stability(rows),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Block E — the variance decomposition, from the archives")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", action="store_true",
                        help="archive the decomposition under "
                             "eval/decompositions/")
    args = parser.parse_args(argv)

    archived = load_sweeps()
    if not archived:
        print("no sweep archives found", file=sys.stderr)
        return 2

    groups = [decompose_group(g) for g in group_sweeps(archived)]
    stamp = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    report = {"generated_at": stamp, "groups": groups}

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"{len(archived)} archived sweep(s) in {len(groups)} "
              f"comparison group(s).")
        print("Sweeps are grouped by case set and prompt version. Nothing is "
              "pooled across a\ngroup: two sweeps that ran different questions "
              "are two measurements of two\ndifferent things.")
        for group in groups:
            print("\n" + "#" * 72)
            print(f"# {group['cases']} case(s), prompt "
                  f"{', '.join(group['prompt_versions']) or '?'}, "
                  f"{group['runs']} run(s)")
            dates = ", ".join(group["dates"]) or \
                "NONE — these archives carry no session identity"
            print(f"# dates    {dates}")
            for name in group["sweeps"]:
                print(f"#   {name}")
            print("#" * 72)
            answer_eval.print_stability(group["stability"])
            answer_eval.print_decomposition(group["verdicts"], group["texts"])

    if args.write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        name = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
        path = OUT_DIR / f"{name}-decomposition.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                        encoding="utf-8")
        print(f"\ndecomposition archived: {path}")
        print("G4 asks for the decomposition WITH THE DATA ARCHIVED. This is "
              "that file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
