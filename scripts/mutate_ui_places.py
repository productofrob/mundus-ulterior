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
    (
        # Ruling 40, 2026-08-28, RE-ANCHORED the same day. Without this branch
        # a quotation the writer fitted with an added article falls through to
        # the case-folding branch below and is reported as a LABELLING DEFECT
        # — `_same_characters` tests containment in either direction, so
        # `Half-length bust…` counts as "the same characters" as `a
        # half-length bust…`. The ruling document first said it fell through to
        # `absent`; that is what it would be under equality, and the
        # correction is recorded there.
        "a quotation fitted with an added article is reported as a case "
        "labelling defect instead",
        [("""    if (unarticled != quote
            and strip_added_article(found) == found
            and _same_characters(found.casefold(), unarticled.casefold())):""",
          """    if False:""")],
    ),
    (
        # FINDING 42, F3, fixed in F4. The whitespace category REMOVED, which is
        # the code as it stood when a correctly grounded Tamil quotation was
        # reported ABSENT because a newline had been rendered as a space. Both
        # branches go together: with only the first removed the second catches
        # the same span and the mutation would report MISS while the defect it
        # models was gone.
        "the verifier has no whitespace category, so a collapsed line break "
        "falls through to absent",
        [("""    if _same_characters(collapsed_found, collapsed_quote):""",
          """    if False:"""),
         ("""    if _same_characters(collapsed_found.casefold(), collapsed_quote.casefold()):""",
          """    if False:""")],
    ),
    (
        # The other direction, and the one that matters more. FINDING 42 says
        # the fix is a CATEGORY and not a TOLERANCE: a verifier that quietly
        # accepts anything it cannot classify reports nothing and fails nothing,
        # which is the state a reader cannot tell from a clean corpus.
        "the whitespace category swallows every span that reaches it, so a "
        "quotation that is genuinely absent is reported as a line break",
        [("""    if _same_characters(collapsed_found, collapsed_quote):""",
          """    if True:""")],
    ),
]

EXPECTED = [
    "a specific place with no gazetteer_id is reported as an authored "
    "coordinate",
    "an identified placement with no ground_citation is reported",
    "an id absent from the gazetteer cache is reported as uncached",

    # Ruling 40.
    "a span recording match='article_added' is classified as such, and not "
    "as the case labelling defect it fell into on the first run",

    # FINDING 42, F4.
    "GUARD a quotation differing from the record only by a collapsed line "
    "break is reported as whitespace_only, not as absent",
    "GUARD a quotation that is genuinely not in the field is still absent "
    "once the whitespace category exists",
]


def failures_from(output: str) -> set[str]:
    # The SPACE is load-bearing. FINDING 37, 2026-08-31, found in
    # scripts/mutate_places.py and fixed only there: `ui/test_build_ui_data.py`
    # ends a red run with a summary line reading `FAILED (1)`, so a bare
    # startswith("FAIL") harvests a phantom guard named `ED (1)` beside the real
    # ones -- and a harness that invents a failing guard reports a BASELINE
    # block against a suite that is green. Third harness, same defect, and it
    # survived here for the same reason it survived there: this one had not been
    # run since.
    return {
        line.split("FAIL ", 1)[1].strip()
        for line in output.splitlines()
        if line.strip().startswith("FAIL ")
    }


# 2026-08-28. FINDING 10's family, at the boundary answer/cite.py's own comment
# calls already guarded: a PARENT decoding a CHILD. This harness ran its suite
# with neither `encoding=` nor a child PYTHONIOENCODING, so on Windows it
# decoded stdout with the locale codec and every em-dash came back as `\xe2\x80\x94`
# mojibake. No guard label held a non-ASCII character until ruling 40 added
# one, and that guard could then never match its own failure line: the harness
# printed MISS on a mutation that had worked perfectly. Fixed the way
# scripts/mutate_part8.py already does it, which is where CHILD_ENV comes from.
CHILD_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8",
             "PYTHONDONTWRITEBYTECODE": "1"}


def run_tests() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", *TEST], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=CHILD_ENV,
    )


# 2026-08-28. PROGRESS.md named this at the close of Block D and predicted the
# exposure exactly: "A green mutation run is not evidence the tree was
# restored… All four harnesses compare text… Three of six are exposed, and
# only by the accident of which files are CRLF." It fired today. `write_text`
# translates "\n" to os.linesep, so on Windows every run of this harness
# rewrote an LF source as CRLF and its restore check, which compares TEXT,
# could not see it. The remedy PROGRESS.md gives is the one taken here: the
# harness compares and writes BYTES.
def _newline_of(raw: bytes) -> str:
    crlf = raw.count(b"\r\n")
    if crlf and raw.count(b"\n") - crlf:
        raise SystemExit(
            "a mutation source has MIXED line endings. Resolve that by hand "
            "before running this harness, which would otherwise pick one."
        )
    return "\r\n" if crlf else "\n"


def _write(path: pathlib.Path, text: str, newline: str) -> None:
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def main() -> int:
    if len(MUTATIONS) != len(EXPECTED):
        print(f"{len(MUTATIONS)} mutations against {len(EXPECTED)} expectations")
        return 1

    original_bytes = {f: f.read_bytes() for f in SOURCES}
    newlines = {f: _newline_of(original_bytes[f]) for f in SOURCES}
    originals = {
        f: original_bytes[f].decode("utf-8").replace("\r\n", "\n")
        for f in SOURCES
    }
    problems: list[str] = []
    try:
        # 2026-08-28. THE BASELINE — see scripts/mutate_part8.py. A green
        # mutation against a red suite is a vacuous proof.
        already_failing = failures_from(run_tests().stdout)
        if already_failing:
            print(f"  BASELINE: {len(already_failing)} check(s) already fail "
                  f"with NO mutation applied.")
            for name in sorted(already_failing):
                print(f"            - {name}")
            print()

        for (label, patches), guard in zip(MUTATIONS, EXPECTED):
            if guard in already_failing:
                problems.append(
                    f"{label}: UNVERIFIED — its guard {guard!r} was already "
                    f"failing before any mutation was applied."
                )
                print(f"  UNVERIFIED {label} (its guard was already red at "
                      f"baseline)")
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
                _write(f, edited[f], newlines[f])

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
            f.write_bytes(original_bytes[f])

    unrestored = [
        f.name for f in SOURCES
        # BYTES, not text. A restore check that normalises newlines is
        # constitutionally unable to see the damage a text-mode write does —
        # PROGRESS.md, at the close of Block D.
        if f.read_bytes() != original_bytes[f]
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
