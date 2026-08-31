"""Mutation-verify the guards in scripts/test_recover_baseline.py.

Same standard as scripts/mutate_part7b.py: each mutation breaks exactly one fix
and asserts that the guard protecting *that* fix reports FAIL — not merely that
something failed. A guard that has never failed is a guard whose failure mode is
unknown, and Part 7 found six of thirteen mutations initially failing to break
their guard, each miss a finding.

The guards worth mutating here are the ones protecting a distinction rather than
a behaviour: that a reconstruction announces itself, that a nullable parameter
carries a cast, and that the absent list tracks run_answer's payload instead of
being a copy of it that drifts.

Run: python scripts/mutate_recover.py
"""

from __future__ import annotations

import os
import pathlib
import subprocess
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
RECOVER = ROOT / "scripts" / "recover_answer_baseline.py"
RUN_ANSWER = ROOT / "answer" / "run_answer.py"
SOURCES = (RECOVER, RUN_ANSWER)

MUTATIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "a recovered payload no longer announces itself",
        [('            "recovered": True,\n', "")],
    ),
    (
        # First attempt at this mutation was `ABSENT = [] or [...]`, which
        # Python evaluates to the second list — the mutation did not mutate, and
        # the guard was blamed for it. Left recorded because a mutation that
        # quietly fails to mutate reads exactly like a guard that does not work.
        "the absent list is emptied — nothing names what was not rebuilt",
        [("ABSENT = [", "ABSENT: list[str] = []\n_ABSENT_UNUSED = [")],
    ),
    (
        # The failure this whole file exists to prevent: a reconstruction that
        # supplies the field it cannot know. An empty sources block is not the
        # sources block that was shown; it is a claim that none was.
        "the reconstruction invents an empty sources block",
        [('            "notes": notes,',
          '            "notes": notes,\n            "sources_block": "",')],
    ),
    (
        "a nullable filter loses its cast",
        [("WHERE (%(prompt_version)s::text IS NULL",
          "WHERE (%(prompt_version)s IS NULL")],
    ),
    (
        "the chunk id array loses its ::text[] cast",
        [("WHERE answer_id = ANY(%(answer_ids)s::text[])",
          "WHERE answer_id = ANY(%(answer_ids)s)")],
    ),
    (
        "the archive can overwrite an existing file",
        [("""    counter = 2
    while path.exists():
        path = RUNS_DIR / f"{stem}-{counter}.json"
        counter += 1
    return path""", "    return path")],
    ),
    (
        "the -recovered marker is dropped from the filename",
        [('stem = f"{stamp}-{payload[\'answer_id\'][:8]}-recovered"',
          'stem = f"{stamp}-{payload[\'answer_id\'][:8]}"')],
    ),
    (
        "the runs directory is re-derived instead of imported",
        [("from answer.run_answer import RUNS_DIR  # noqa: E402",
          "RUNS_DIR = Path(__file__).resolve().parent.parent / 'eval' / 'runs'")],
    ),
    (
        "the timestamp stops saying what it means",
        [('''            "timestamp_meaning": (
                "answers.created_at — the row's last write, not necessarily the "
                "first run of this answer (UPSERT_ANSWER sets created_at = now() "
                "on conflict)"
            ),
''', '            "timestamp_meaning": "answers.created_at",\n')],
    ),
    (
        "a file with no question is counted as a run",
        [("""        (runs if isinstance(data, dict) and "question" in data
         else fixtures).append(path.name)""", "        runs.append(path.name)")],
    ),
    (
        # Drift, simulated at the source: run_answer grows a payload key this
        # script cannot rebuild and ABSENT does not name it. The guard reads
        # run_answer.py rather than a copy, so it must notice.
        "run_answer's payload grows a key ABSENT does not name",
        [('        "sources_block": answer.sources_block,',
          '        "sources_block": answer.sources_block,\n'
          '        "evidence_digest": None,')],
    ),
]

EXPECTED = [
    "GUARD every recovered payload is marked recovered: true",
    "GUARD recovered_absent names what could not be rebuilt",
    "a recovered payload does not invent a sources block",
    "GUARD SELECT_ANSWERS: every nullable parameter carries a cast (uncast: "
    "['prompt_version'])",
    "GUARD SELECT_CITATIONS: every ANY() parameter carries a ::text[] cast "
    "(uncast: ['answer_ids'])",
    "GUARD identical timestamp and answer_id never collide",
    "GUARD a reconstruction is visible in a directory listing",
    "GUARD the runs directory is imported from run_answer, not re-derived",
    "the qualification is specific, not decorative",
    "GUARD a fixture with no question is not counted as a run",
    "GUARD every native payload key is either recoverable or named in ABSENT "
    "(unaccounted: ['evidence_digest'])",
]


def failures_from(output: str) -> set[str]:
    return {
        line.split("FAIL", 1)[1].strip()
        for line in output.splitlines()
        if line.strip().startswith("FAIL")
    }


def main() -> int:
    # 2026-08-28. BYTES on the way out, whatever the harness did on the way in.
    # PROGRESS.md named this at the close of Block D and predicted the exposure
    # exactly — "a green mutation run is not evidence the tree was restored…
    # three of six are exposed, and only by the accident of which files are
    # CRLF." On 2026-08-28 mutate_ui_places converted ui/build_ui_data.py from
    # LF to CRLF on a live run and its text-comparing restore check could not
    # see it; the conversion reached a commit. `write_text` translates "\n" to
    # os.linesep. The restore below writes the ORIGINAL BYTES and the check
    # compares BYTES, so this harness can no longer do that to its own sources.
    original_bytes = {f: f.read_bytes() for f in SOURCES}
    originals = {f: f.read_text(encoding="utf-8") for f in SOURCES}
    problems: list[str] = []
    try:
        # THE BASELINE, added 2026-08-31 in F3. Carried as owed since F1 and
        # closed BEFORE the corpus moves, which is the whole reason it stopped
        # being cheap to defer.
        #
        # A mutation is verified by naming a guard and checking that the guard
        # FAILS once the code is broken. That is only evidence if the guard was
        # PASSING beforehand. A green mutation against a red baseline is a
        # vacuous proof, and on 2026-08-28 one happened inside the instrument
        # built to catch vacuous proofs.
        #
        # F3 takes the corpus from 24 records to 60. A guard that goes red
        # because of a NEW RECORD, in a harness with no baseline, turns every
        # mutation naming it into a green line that proves nothing.
        _baseline = subprocess.run(
            [sys.executable, "-B", "scripts/test_recover_baseline.py"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            errors="replace",
            env={**os.environ, "PYTHONIOENCODING": "utf-8",
                 "PYTHONDONTWRITEBYTECODE": "1"},
        )
        already_failing = failures_from(_baseline.stdout)
        if _baseline.returncode != 0 and not already_failing:
            print("  BASELINE: the suite CRASHED with NO mutation applied. "
                  "Nothing below can be verified.")
            print(_baseline.stderr.rstrip()[-2000:])
            return 1
        if already_failing:
            print(f"  BASELINE: {len(already_failing)} check(s) already fail "
                  f"with NO mutation applied. Any mutation naming one of\n"
                  f"            them cannot be verified by this run.")
            for name in sorted(already_failing):
                print(f"            - {name}")
            print()

        for (label, patches), guard in zip(MUTATIONS, EXPECTED):
            if guard in already_failing:
                problems.append(
                    f"{label}: UNVERIFIED - its guard {guard!r} was already "
                    f"failing before any mutation was applied, so this "
                    f"mutation proves nothing. Fix the suite, then re-run."
                )
                print(f"  UNVERIFIED {label} "
                      f"(its guard was already red at baseline)")
                continue
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

            result = subprocess.run(
                [sys.executable, "scripts/test_recover_baseline.py"],
                cwd=ROOT, capture_output=True, text=True,
            )
            failed = failures_from(result.stdout)
            # An import-time break is not a guard firing. Say so rather than
            # counting a crash as a pass — Part 7's mutation misses were mostly
            # of this shape: something failed, but not the thing under test.
            if guard in failed:
                print(f"  ok   {label}")
                print(f"       -> {guard}")
            elif result.returncode != 0 and not failed:
                problems.append(
                    f"{label}: the suite crashed rather than failing the guard "
                    f"({result.stderr.strip().splitlines()[-1:] or ['no stderr']})"
                )
                print(f"  MISS {label} (crash, not a guard failure)")
            else:
                problems.append(
                    f"{label}: expected {guard!r} to fail, got "
                    f"{sorted(failed) or 'no failures'}"
                )
                print(f"  MISS {label}")
    finally:
        for f in SOURCES:
            f.write_bytes(original_bytes[f])

    # Two different failures, kept apart — see the note in mutate_part8.py.
    # A restore failure is checked by comparing content; a suite failure is a
    # finding about the suite and must not be reported as a corrupted tree.
    unrestored = [
        f.name for f in SOURCES
        if f.read_bytes() != original_bytes[f]
    ]
    if unrestored:
        problems.append(
            "sources were NOT restored cleanly: " + ", ".join(unrestored)
            + " — restore from version control before running anything else"
        )

    check = subprocess.run(
        [sys.executable, "scripts/test_recover_baseline.py"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if check.returncode != 0:
        problems.append(
            "sources restored, but `scripts/test_recover_baseline.py` fails on "
            "its own account — a finding about the suite, not about this harness"
        )
        print("\n--- test_recover_baseline.py output, so it is not lost ---")
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
