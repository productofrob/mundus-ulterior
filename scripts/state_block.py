"""Run the eleven instruments and PRINT the table. FINDING 76, F6, 2026-09-06.

FINDING 75 was three tier counts copied from the document before. The answer to
it was `ingest.verify --state`, and it covers ONE command.

FINDING 76 is the other ten. `F6_START.md` opened by refusing to hand-copy its
predecessor's numbers, printed eleven instrument counts under that heading, and
one of them was wrong: `eval.test_answer_eval` was reported as 422 against an
actual 425, having been COMPUTED -- 416 measured at the open, plus an assumed
per-case assertion rate -- rather than read off the instrument that had already
printed 425 into the same session. Arithmetic is the form a number takes when
somebody already knows not to copy.

So: no argument, no options, no way to pass a figure in. Every number below is
read out of the process that produced it, in this run, or the row says the
instrument did not run. A row this script cannot fill is a row an opening
document may not fill either.

MUTATION HARNESSES ARE NOT HERE. FINDING 59: they must never run where they can
be interrupted, and this script is exactly the thing somebody runs casually.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# FINDING 10: this process's own stdout. On Windows `print` writes through a
# stream whose encoding comes from the console code page, and through a PIPE or
# a REDIRECT it falls back to the locale codec -- cp1252, which cannot encode
# Greek, Tamil, Chinese, Ge'ez or runic. It does not degrade: it raises
# UnicodeEncodeError mid-output, with the file half written and every number in
# it correct. This file is the one most likely to be redirected into a document,
# which is the exact shape the guard was written for.
#
# errors="replace" is deliberate. A table that cannot encode one character
# should print a replacement character and finish.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = Path(__file__).resolve().parent.parent

# (label, argv). Order is the one Block F's documents print, so a reader can
# lay this table beside the last one and diff it by eye.
INSTRUMENTS = [
    ("ingest.verify", [sys.executable, "-m", "ingest.verify"]),
    ("ingest.test_fidelity", [sys.executable, "-m", "ingest.test_fidelity"]),
    ("ingest.test_cost", [sys.executable, "-m", "ingest.test_cost"]),
    ("eval.test_answer_eval", [sys.executable, "-m", "eval.test_answer_eval"]),
    ("eval.test_ranking_check", [sys.executable, "-m", "eval.test_ranking_check"]),
    ("answer.test_answer", [sys.executable, "-m", "answer.test_answer"]),
    ("ui/test_build_ui_data.py", [sys.executable, "ui/test_build_ui_data.py"]),
    ("scripts/test_recover_baseline.py",
     [sys.executable, "scripts/test_recover_baseline.py"]),
    ("scripts/test_harnesses.py", [sys.executable, "scripts/test_harnesses.py"]),
    ("python -m ingest.gazetteer --check",
     [sys.executable, "-m", "ingest.gazetteer", "--check"]),
    ("node ui/check_ui.mjs", ["node", "ui/check_ui.mjs"]),
]

_PASSED = re.compile(r"^\s*(\d+)\s+passed,\s+(\d+)\s+failed", re.M)
_DOCUMENTS = re.compile(r"^documents:\s+(\d+)", re.M)


def _run(argv: "list[str]") -> "tuple[int, str]":
    if shutil.which(argv[0]) is None and not Path(argv[0]).exists():
        return (127, f"{argv[0]}: not on PATH in this environment")
    # The two NEIGHBOURING boundaries FINDING 10's comment names and separates:
    # the CHILD's own stdout (PYTHONIOENCODING in its environment) and this
    # process DECODING that child (encoding= on subprocess). Both are needed
    # here and neither is the guard above. Without the first, a suite printing
    # Ge'ez into this pipe dies on Windows and its row reads RED for a reason
    # that is not about the suite.
    env = dict(os.environ, PYTHONIOENCODING="utf-8:replace")
    proc = subprocess.run(
        argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=env,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def read_one(label: str, argv: "list[str]") -> str:
    """One row. The FIGURE, or why there is not one -- never a blank."""
    code, out = _run(argv)
    if code == 127:
        return f"DID NOT RUN -- {out}"

    counts = _PASSED.findall(out)
    if counts:
        # The LAST match: a suite that prints per-section subtotals ends with
        # its own total, and the first match would be a section.
        passed, failed = counts[-1]
        state = "green" if (code == 0 and failed == "0") else "RED"
        tail = "" if failed == "0" else f", {failed} FAILED"
        return f"{passed}{tail}   [{state}]"

    if label == "ingest.verify":
        docs = _DOCUMENTS.search(out)
        n = docs.group(1) if docs else "?"
        state = "green" if code == 0 else "RED"
        return f"{state}, {n} documents"

    if code == 0:
        return "GREEN"
    return f"RED (exit {code})"


def main() -> int:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    head = subprocess.run(
        ["git", "--no-optional-locks", "rev-parse", "--short", "HEAD"],
        cwd=ROOT, capture_output=True, text=True)
    tree = (head.stdout or "").strip() or "unknown tree"

    rows = [(label, read_one(label, argv)) for label, argv in INSTRUMENTS]
    width = max(len(label) for label, _ in rows)

    print(f"Run by `python scripts/state_block.py` at {tree} on {stamp}. "
          f"PASTE THIS BLOCK. Do not restate it, and do not compute a figure "
          f"in it from another figure -- FINDING 76.")
    print()
    print("```")
    for label, value in rows:
        print(f"{label.ljust(width)}   {value}")
    print("```")

    red = [label for label, value in rows if "RED" in value or "DID NOT RUN" in value]
    if red:
        print()
        print(f"NOT ALL GREEN: {red}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
