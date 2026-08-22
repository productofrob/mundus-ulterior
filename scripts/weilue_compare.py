"""Compare the two newest ranking archives on the numbers the Weilue fix moves.

Run once after step 0 to see the baseline, and again after step 4:

    python scripts\\weilue_compare.py              # newest vs the one before it
    python scripts\\weilue_compare.py --baseline   # newest only

It asserts VALUES, not headings. A check that greps a heading passes against a
report that prints the heading and no rows, and this repository has lost time to
that twice. The first draft of this script did exactly that: it read
units[].pairs as a list of dicts carrying expect_doc, when in the archive those
are pair IDS and expect_doc lives on the top-level `pairs` entries. It printed a
clean empty table and would have been read as "nothing to compare".

Every pair whose expect_doc is the Weilue record is discovered from the archive
rather than listed here, so a pair that is added later is picked up and a pair
that disappears is reported as VANISHED rather than silently omitted.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = "eastasia-01-weilue"
RANK_KEYS = ("rank", "rank_collapsed", "rank_reranked")


def rows(run: dict) -> dict[str, dict]:
    out = {}
    for pair in run.get("pairs", []):
        if pair.get("expect_doc") != DOC:
            continue
        out[pair["id"]] = {
            "lang": pair.get("query_lang"),
            "chunk": pair.get("resolved_chunk_id"),
            **{k: pair.get(k) for k in RANK_KEYS},
        }
    return out


def cell(row: dict | None) -> str:
    if row is None:
        return "VANISHED"
    return "/".join("-" if row[k] is None else str(row[k]) for k in RANK_KEYS)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    args = ap.parse_args()

    files = sorted(glob.glob(str(ROOT / "eval" / "ranking_runs" / "*.json")),
                   key=os.path.getmtime)
    if not files:
        print("no ranking archives found")
        return 1

    new = json.load(open(files[-1], encoding="utf-8"))
    new_r = rows(new)
    print(f"AFTER  {pathlib.Path(files[-1]).name}")
    if not new_r:
        print(f"  NO PAIR IN THIS ARCHIVE EXPECTS {DOC}. That is a finding, not "
              f"an empty result: the record was in the ranking gold set.")
        return 1

    if args.baseline or len(files) < 2:
        for pid, row in sorted(new_r.items()):
            print(f"  {pid:<30} lang={row['lang']:<4} "
                  f"rank/collapsed/reranked = {cell(row)}")
            print(f"  {'':<30} chunk={row['chunk']}")
        return 0

    old = json.load(open(files[-2], encoding="utf-8"))
    old_r = rows(old)
    print(f"BEFORE {pathlib.Path(files[-2]).name}\n")
    print(f"  {'pair':<30} {'lang':<5} {'before':>14}  {'after':>14}")

    moved = 0
    for pid in sorted(set(old_r) | set(new_r)):
        b, a = old_r.get(pid), new_r.get(pid)
        lang = (a or b).get("lang") or "?"
        mark = ""
        if b is None or a is None:
            mark, moved = "  <- APPEARED/VANISHED", moved + 1
        elif any(b[k] != a[k] for k in RANK_KEYS):
            better = all((a[k] or 10**6) <= (b[k] or 10**6) for k in RANK_KEYS)
            mark = "  <- IMPROVED" if better else "  <- MOVED"
            moved += 1
        print(f"  {pid:<30} {lang:<5} {cell(b):>14}  {cell(a):>14}{mark}")
    print("  (rank/collapsed/reranked; lower is better)")

    for pid in sorted(set(old_r) & set(new_r)):
        if old_r[pid]["chunk"] != new_r[pid]["chunk"]:
            print(f"\n  CHUNK ID MOVED for {pid}:")
            print(f"    {old_r[pid]['chunk']}  ->  {new_r[pid]['chunk']}")
            print("    Expected if the original re-chunked. Record it; do not "
                  "absorb it.")

    print(f"\n  {moved} pair(s) moved.")
    if moved == 0:
        print("  Zero movement after a corpus edit to this record is itself a\n"
              "  finding: either the edit never reached the index, or retrieval\n"
              "  never depended on the text that changed. Check run_embed --stats\n"
              "  before concluding the second.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
