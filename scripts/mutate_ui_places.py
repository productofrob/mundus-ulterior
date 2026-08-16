"""Mutation-verify the three build-layer guards PHASE2_PLAN.md assigns to A6:

    - introduce a hand-authored coordinate with no `pleiades_id` -> build must fail
    - introduce an `identified` placement with no citation -> build must fail
    - point a `pleiades_id` at a non-resolving id -> build must fail

Same standard as `scripts/mutate_places.py`: each mutation breaks exactly one
rule in `ui/build_ui_data.py` and asserts that the guard protecting *that* rule
reports FAIL in `ui/test_build_ui_data.py` — not merely that something failed.

These three are deliberately redundant with guards `mutate_places.py` already
proves for `ingest/places.py` and `ingest/gazetteer.py`. The redundancy is the
point: PROGRESS.md records that `build_places()` has reported an uncached id as
a build failure since A4, and re-checked the other two shapes since A6, but
neither had ever been seen to fail on its own account before this file existed.
A guard never seen to fail is not known to work.

Run: python scripts/mutate_ui_places.py
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD_UI_DATA = ROOT / "ui" / "build_ui_data.py"
SOURCES = (BUILD_UI_DATA,)
TEST = ["ui/test_build_ui_data.py"]

MUTATIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "an authored coordinate (no gazetteer_id, ground not regional) is not "
        "reported by the build's own shape audit",
        [("""    if p.ground != "regional" and p.gazetteer_id is None:""",
          """    if False:""")],
    ),
    (
        "an identified placement with no ground_citation is not reported by "
        "the build's own shape audit",
        [("""    if p.ground == "identified" and p.ground_citation is None:""",
          """    if False:""")],
    ),
    (
        "an id that never resolves is no longer reported as uncached",
        [("""            if gap_reason and kind == "gap" and resolved is None and p.cache_key and p.locatable:""",
          """            if False:""")],
    ),
]

EXPECTED = [
    "a specific place with no gazetteer_id is reported as an authored "
    "coordinate",
    "an identified placement with no ground_citation is reported",
    "an id absent from the gazetteer cache is reported as uncached",
]


def failures_from(output: str) -> set[str]:
    return {
        line.split("FAIL", 1)[1].strip()
        for line in output.splitlines()
        if line.strip().startswith("FAIL")
    }


def run_tests() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *TEST], cwd=ROOT, capture_output=True, text=True,
    )


def main() -> int:
    if len(MUTATIONS) != len(EXPECTED):
        print(f"{len(MUTATIONS)} mutations against {len(EXPECTED)} expectations")
        return 1

    originals = {f: f.read_text(encoding="utf-8") for f in SOURCES}
    problems: list[str] = []
    try:
        for (label, patches), guard in zip(MUTATIONS, EXPECTED):
            edited = {f: originals[f] for f in SOURCES}
            missing = [
                old for old, _ in patches
                if not any(old in originals[f] for f in SOURCES)
            ]
            if missing:
                problems.append(f"{label}: mutation target not found")
                print(f"  MISS {label} (target not found)")
                continue
            for old, new in patches:
                target = next(f for f in SOURCES if old in edited[f])
                edited[target] = edited[target].replace(old, new, 1)
            for f in SOURCES:
                f.write_text(edited[f], encoding="utf-8")

            result = run_tests()
            failed = failures_from(result.stdout)
            if guard in failed:
                print(f"  ok   {label}")
                print(f"       -> {guard}")
            elif result.returncode != 0 and not failed:
                # A crash is not a guard firing — the same distinction
                # mutate_places.py keeps explicit, for the same reason.
                problems.append(
                    f"{label}: the suite crashed rather than failing the guard"
                )
                print(f"  MISS {label} (crash, not a guard failure)")
                print(result.stdout)
                print(result.stderr)
            else:
                problems.append(
                    f"{label}: expected {guard!r} to fail, got "
                    f"{sorted(failed) or 'no failures'}"
                )
                print(f"  MISS {label}")
    finally:
        for f in SOURCES:
            f.write_text(originals[f], encoding="utf-8")

    unrestored = [
        f.name for f in SOURCES
        if f.read_text(encoding="utf-8") != originals[f]
    ]
    if unrestored:
        problems.append(
            "sources were NOT restored cleanly: " + ", ".join(unrestored)
            + " — restore from version control before running anything else"
        )

    check = run_tests()
    if check.returncode != 0:
        problems.append(
            "sources restored, but `ui/test_build_ui_data.py` fails on its "
            "own account — a finding about the suite, not about this harness"
        )
        print("\n--- ui/test_build_ui_data.py output, so it is not lost ---")
        print((check.stdout or "") + (check.stderr or ""), end="")
        print("--- end ---")

    print()
    if problems:
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"all {len(MUTATIONS)} mutations verified; sources restored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
