"""Compare the two newest ranking archives on the numbers the Weilue fix moves.

Run it AFTER step 0 to record the baseline, and again AFTER step 4. It asserts
values rather than greping headings: a check that greps a heading passes against
a report that prints the heading and no rows, which this repository has been
caught by before.

    python scripts\\weilue_compare.py            # newest vs the one before it
    python scripts\\weilue_compare.py --baseline # print the newest only

The four Weilue-bearing units are named explicitly. If one stops appearing, that
is reported as a MISSING line rather than silently dropping out of the table --
a unit that vanishes is a louder result than a unit that moved.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import pathlib

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

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = "eastasia-01-weilue"
WATCH = (
    "china-describes-rome-weilue",
    "probe-chinese-weilue",
    "chinese query -> Weilue Da Qin",
)


def load(path: str) -> dict:
    return json.load(open(path, encoding="utf-8"))


def ranks(run: dict) -> dict[str, dict]:
    """Every unit whose expected document is the Weilue record, by unit id."""
    out: dict[str, dict] = {}
    for unit in run.get("units", []):
        pairs = unit.get("pairs") or []
        ids = [p.get("id") or p.get("name") for p in pairs if isinstance(p, dict)]
        docs = {p.get("expect_doc") for p in pairs if isinstance(p, dict)}
        if DOC not in docs:
            continue
        key = ids[0] if ids else (unit.get("query") or "?")[:48]
        out[key] = {
            "best_rank": unit.get("best_rank"),
            "collapsed": unit.get("best_rank_collapsed"),
            "reranked": unit.get("best_rank_reranked"),
            "coverage": unit.get("coverage_reranked", unit.get("coverage")),
        }
    return out


def headline(run: dict) -> dict:
    agg = run.get("aggregate_units") or run.get("aggregate") or {}
    return {k: v for k, v in agg.items() if isinstance(v, (int, float, str))}


def fmt(v) -> str:
    return "-" if v is None else str(v)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true",
                    help="print the newest archive only, no comparison")
    args = ap.parse_args()

    files = sorted(glob.glob(str(ROOT / "eval" / "ranking_runs" / "*.json")),
                   key=os.path.getmtime)
    if not files:
        print("no ranking archives found")
        return 1

    new = load(files[-1])
    print(f"AFTER  {pathlib.Path(files[-1]).name}")
    new_r = ranks(new)

    if args.baseline or len(files) < 2:
        for key in WATCH:
            row = new_r.get(key)
            print(f"  {key:<34} "
                  + ("MISSING" if row is None else
                     f"rank={fmt(row['best_rank'])} collapsed={fmt(row['collapsed'])} "
                     f"reranked={fmt(row['reranked'])}"))
        print("  aggregate:", json.dumps(headline(new), ensure_ascii=False))
        return 0

    old = load(files[-2])
    old_r = ranks(old)
    print(f"BEFORE {pathlib.Path(files[-2]).name}\n")

    print(f"  {'unit':<34} {'before':>22}  {'after':>22}")
    moved = 0
    for key in WATCH:
        b, a = old_r.get(key), new_r.get(key)
        def cell(row):
            if row is None:
                return "MISSING"
            return (f"{fmt(row['best_rank'])}/{fmt(row['collapsed'])}"
                    f"/{fmt(row['reranked'])}")
        mark = ""
        if b and a and (b["reranked"] != a["reranked"]
                        or b["best_rank"] != a["best_rank"]):
            mark = "  <- MOVED"
            moved += 1
        if (b is None) != (a is None):
            mark = "  <- APPEARED/VANISHED"
            moved += 1
        print(f"  {key:<34} {cell(b):>22}  {cell(a):>22}{mark}")
    print("  (cells are best_rank/collapsed/reranked; lower is better)")

    print("\n  aggregate before:", json.dumps(headline(old), ensure_ascii=False))
    print("  aggregate after: ", json.dumps(headline(new), ensure_ascii=False))

    extra = sorted((set(old_r) | set(new_r)) - set(WATCH))
    if extra:
        print(f"\n  NOT IN THE WATCH LIST but expects {DOC}: {extra}")
        print("  Add them to WATCH or explain why they are not watched.")

    print(f"\n  {moved} watched unit(s) moved.")
    if moved == 0:
        print("  Zero movement after a corpus edit to this record is itself a "
              "finding: either the edit did not reach the index, or retrieval "
              "never depended on the text that changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
