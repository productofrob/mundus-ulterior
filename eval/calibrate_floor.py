"""D4: read every archived sweep, report both stability numbers, and decide
whether `calibrated: true` may be written to eval/gold/floor.json.

Why this is a program and not a judgement
-----------------------------------------

`floor.json` has read `calibrated: false` since 2026-08-10, with:

    calibration_invalidated: "2026-08-10, hours after being set."

The floor was set on the observation that CONTENT was stable in 10 of 10 cells
across three repetitions each. A second sweep, with the `vimose-runes` evidence
block byte-identical (sha256 verified across all six archived runs), produced
3/3 pass with seven resolved quotations in the first session and 0/3 with none
in the second. Same prompt version, same model, same evidence, temperature 0.

Nothing stopped `calibrated: true` being written that morning except a person
deciding to write it, and nothing would have stopped it being written again.
This refuses, from the sweep archives, on a threshold that lives in the floor
file where loosening it is a diff.

    python -m eval.calibrate_floor              # report; writes nothing
    python -m eval.calibrate_floor --write      # set calibrated: true, if eligible

Costs nothing: no gateway, no database, no embeddings. Reads files.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

from eval import answer_eval
from eval.goldset import GOLD_DIR, GoldSetError, load_floor

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


def load_sweeps(sweep_dir: Path | None = None) -> list[tuple[dict, str]]:
    """Every archived sweep, as (sweep, filename), oldest name first."""
    sweep_dir = sweep_dir or SWEEP_DIR
    out: list[tuple[dict, str]] = []
    for path in sorted(sweep_dir.glob("*.json")) if sweep_dir.exists() else []:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(data, dict) and "results" in data:
            out.append((data, path.name))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="D4 — the two stability numbers, and whether the floor "
                    "may be called calibrated")
    parser.add_argument("--write", action="store_true",
                        help="set calibrated: true in eval/gold/floor.json, "
                             "IF the archived sweeps make that legitimate")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        floor = load_floor()
    except GoldSetError as exc:
        print(f"floor will not load: {exc}", file=sys.stderr)
        return 2

    archived = load_sweeps()
    if not archived:
        print("no sweep archives found", file=sys.stderr)
        return 2

    sweeps = [sweep for sweep, _ in archived]
    rows = [row for sweep in sweeps for row in sweep.get("results", [])]

    numbers = answer_eval.stability(rows)
    verdict = answer_eval.calibration_eligibility(sweeps, floor)

    if args.json:
        print(json.dumps({"stability": numbers, "calibration": verdict},
                         indent=2, ensure_ascii=False))
    else:
        print(f"{len(archived)} archived sweep(s), {len(rows)} run(s)\n")
        for sweep, name in archived:
            session = sweep.get("session") or {}
            print(f"  {name}")
            print(f"      {session.get('date', 'NO SESSION IDENTITY'):<12} "
                  f"{session.get('id', '')[:12]:<14} "
                  f"repeat={sweep.get('repeat', '?')}"
                  + (f"  {session['label']}" if session.get("label") else "")
                  + ("  [began before midnight UTC and finished after]"
                     if session.get("crossed_midnight_utc") else ""))
        answer_eval.print_stability(numbers)
        answer_eval.print_calibration(verdict)

    if not args.write:
        print("\nnothing written — re-run with --write to set calibrated: true")
        return 0 if verdict["may_calibrate"] else 1

    if not verdict["may_calibrate"]:
        # The whole point. TASK 3, item 2: calibration REFUSES, rather than
        # a person deciding not to. Exit 2 and not 1: this is a refusal to
        # act, not a report of a state.
        print("\nREFUSED to write calibrated: true.", file=sys.stderr)
        for refusal in verdict["refusals"]:
            print(f"  - {refusal}", file=sys.stderr)
        return 2

    path = GOLD_DIR / "floor.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["calibrated"] = True
    data["calibrated_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(
        timespec="seconds")
    # What it was calibrated FROM, not merely that it was. `calibrated_from`
    # already names one file; this names the dates, because the claim being
    # made is about days and not about a run.
    data["calibrated_from_dates"] = verdict["dates"]
    data["calibrated_from_sessions"] = verdict["distinct_sessions"]
    data["calibrated_stability"] = {
        "per_case": numbers["per_case"],
        "per_session": numbers["per_session"],
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"\ncalibrated: true written to {path}")
    print(f"  from {verdict['distinct_dates']} dates "
          f"({', '.join(verdict['dates'])}) and "
          f"{verdict['distinct_sessions']} sessions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
