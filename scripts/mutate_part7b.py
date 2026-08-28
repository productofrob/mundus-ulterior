"""Mutation-verify the guards added after the first live run.

Each mutation breaks exactly one fix and asserts that the guard protecting that
fix — and specifically that guard, not merely *a* guard — reports FAIL. A test
that has never failed is a test whose failure mode is unknown.

Run: python scripts/mutate_part7b.py
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
CITE = ROOT / "answer" / "cite.py"
ALIGN = ROOT / "answer" / "align.py"
ASSEMBLE = ROOT / "answer" / "assemble.py"
SOURCES = (CITE, ALIGN, ASSEMBLE)

PRE_FIX_SPLITTER = (
    """    mask = _in_quote_mask(text)
    n = len(text)""",
    """    mask = [False] * len(text)
    n = len(text)""",
)

MUTATIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "quotation tracking disabled in the splitter",
        [PRE_FIX_SPLITTER],
    ),
    (
        "abbreviation check disabled in the splitter",
        [(
            """            if _is_abbreviation(text, i):
                i += 1
                continue""",
            """            if False:
                i += 1
                continue""",
        )],
    ),
    (
        # The bug as shipped: split anywhere, then extract per fragment. Neither
        # half reproduces it alone, which is why it needs its own mutation —
        # fixing the splitter alone already restores correct parity.
        "the pre-fix combination: crude splitting plus per-sentence extraction",
        [
            PRE_FIX_SPLITTER,
            (
                """            if _is_abbreviation(text, i):
                i += 1
                continue""",
                """            if False:
                i += 1
                continue""",
            ),
            (
                """        quotes = [
            quote for quote, start, _ in all_quotes
            if span_start <= start < span_end
        ]""",
                """        quotes = extract_quotes(sentence)""",
            ),
        ],
    ),
    (
        "trailing markers orphaned from their sentence",
        [(
            """            marker = _LEADING_MARKERS_RE.match(text, j)
            if marker:
                j = marker.end()""",
            """            marker = None""",
        )],
    ),
    (
        "refusal exemption removed",
        [(
            """    if collapse(stripped).rstrip(".").lower() == REFUSAL_SENTENCE.rstrip(".").lower():
        return False""",
            """    if False:
        return False""",
        )],
    ),
    (
        "function-word floor removed from quote extraction",
        [(
            """    words = re.findall(r"\\w+", quote.lower())
    if words and all(w in _FUNCTION_WORDS for w in words):
        return False""",
            """    pass""",
        )],
    ),
    (
        "edge-punctuation strip removed from quote matching",
        [(
            """    norm_quote = collapse(quote).strip(_EDGE_PUNCTUATION)""",
            """    norm_quote = collapse(quote)""",
        )],
    ),
    (
        "case-folded fallback removed from quote matching",
        [(
            """    if position < 0:
        position = _fold(norm_hay).find(_fold(norm_quote))""",
            """    if position < 0:
        pass""",
        )],
    ),
    (
        # C1a, 2026-08-14. The fallback below was never wrong; the LABEL was.
        # Removing the one line that records which branch found the quote puts
        # back the state this repository shipped for four days and reported to
        # itself as nine `case_only` spans in `build_ui_data.py --verify`.
        "case-folded match recorded as exact again",
        [(
            """        position = _fold(norm_hay).find(_fold(norm_quote))
        match = "case_folded\"""",
            """        position = _fold(norm_hay).find(_fold(norm_quote))""",
        )],
    ),
    (
        "metadata quotations reported as fabrications again",
        [(
            """            metadata = _in_metadata(quote, known or list(by_marker), by_marker)""",
            """            metadata = None""",
        )],
    ),
    (
        "section-label inheritance removed from align.py",
        [(
            """        if found is not None:
            current = found
        labels.append(current)""",
            """        labels.append(found)""",
        )],
    ),
    (
        "merged section gap filled with nothing",
        [(
            # Was `getattr(following, "char_start", 0) - getattr(previous,
            # "char_end", 0)` until 2026-08-13. Those defaults were what turned
            # "this type has no offsets" into `gap = 0` — a silently wrong merge
            # — for every caller whose rows lack the columns. The mutation is
            # unchanged in what it does; the line it does it to now fails loudly
            # rather than defaulting.
            """        gap = following.char_start - previous.char_end""",
            """        gap = 0""",
        )],
    ),
    (
        "fold_hits maps only the merged chunk's id",
        [(
            """            for member in (pair.members or ([translation] if translation else [])):
                original_by_translation[member.chunk_id] = pair.original""",
            """            if translation is not None:
                original_by_translation[translation.chunk_id] = pair.original""",
        )],
    ),
    (
        "published translation loses its on-disk span",
        [(
            """            translation = passage.translation_section
            if translation is not None and passage.english.kind in (""",
            """            translation = None
            if translation is not None and passage.english.kind in (""",
        )],
    ),
    # ---- Ruling 40, 2026-08-28 ------------------------------------------
    (
        "the added-article branch is removed, and the quotation is absent again",
        [("""        stripped = strip_added_article(norm_quote).strip(_EDGE_PUNCTUATION)""",
          """        stripped = norm_quote""")],
    ),
    (
        # The C1a argument, one class along: a span whose label overstates what
        # it found is the defect, not the match.
        "an added article is recorded as an exact match",
        [("""                norm_quote = stripped
                match = "article_added\"""",
          """                norm_quote = stripped
                match = "exact\"""")],
    ),
    (
        # The span is measured one character short of what was found, so the
        # offset stops round-tripping to the characters the answer quoted.
        #
        # The first version of this mutation set `stripped = norm_quote`, which
        # runs the end index two characters PAST the field and raises
        # IndexError. It killed the suite instead of failing the guard, and the
        # harness — which discarded the child's return code until today —
        # reported it as "expected <guard> to fail, got no failures". A
        # mutation that crashes proves nothing about the guard it names, and
        # both halves of that are now fixed: the harness says CRASH, and this
        # mutation no longer causes one.
        "the span is measured one character short of what was found",
        [("""            if position >= 0:
                norm_quote = stripped""",
          """            if position >= 0:
                norm_quote = stripped[1:]""")],
    ),
    (
        # The A4 defect restored: _merge assumes every chunk type carries
        # offsets. Part 7's does, Part 6's does not, and this is the branch that
        # tells them apart. Removing it puts the AttributeError back.
        "_merge assumes offsets on a chunk type that has none",
        [("""    if not has_offsets(first):
        return replace(first, text=" ".join(c.text for c in chunks))""",
          """    if False:
        return replace(first, text=" ".join(c.text for c in chunks))""")],
    ),
]

EXPECTED = [
    "GUARD a quotation containing an ellipsis is not split in two",
    "GUARD a sentence is not split after an abbreviation",
    # The live-run symptom that mattered: the Greek was quoted verbatim, the
    # broken parity meant it was never extracted, and the check that exists to
    # stop confident readings of untranslated text fired on a correct answer.
    "GUARD quoting an untranslated passage verbatim satisfies the rule",
    "GUARD a marker after the full stop stays with the sentence it cites",
    "GUARD the refusal sentence is not an uncited claim",
    "GUARD a bare function word is never treated as a quotation",
    "GUARD terminal punctuation added to a quotation does not fabricate it",
    "GUARD a quotation lowercased to fit a sentence is still verified",
    "GUARD a case-folded match is not recorded as exact",
    "GUARD quoting the record's title is named as metadata, not fabrication",
    "GUARD a section split into several chunks still aligns by section",
    "GUARD a merged section keeps exact offsets for its later chunks",
    "GUARD a later chunk of a merged section folds into its original",
    "GUARD a quote from a published translation resolves to characters on disk",

    # Ruling 40, in the order above.
    "GUARD a quotation the writer fitted with an added article resolves, and "
    "is NAMED as such",
    "GUARD an added article is not laundered into 'exact' — a viewer printing "
    "exact beside two visibly different strings discredits itself, which is "
    "C1a's own argument",
    "GUARD the span covers the record's characters, not the article the writer "
    "put in front of them",
    # Lives in answer.test_translate, which is why both suites now run.
    "without offsets, the pieces are joined with a single space",
]


# `align.py` is imported by BOTH Part 6 and Part 7, and until 2026-08-13 this
# harness verified it against Part 7's suite alone. That was not a gap in the
# testing so much as the bug itself, written down: `_merge` was covered — the
# guard "a merged section keeps exact offsets for its later chunks" exercises it
# thoroughly — but only ever with a chunk type that HAS offsets. Part 6's
# `ChunkRow` has none, and the first time a translation section split into two
# chunks the live run died on `last.char_end`.
#
# One module, two callers, one suite. Both suites now run for every mutation and
# the failures are pooled, so a guard may live wherever the defect actually
# shows up rather than wherever the mutation harness happens to look.
SUITES = ("answer.test_answer", "answer.test_translate")


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


def run_suites() -> tuple[set[str], bool]:
    """Failures across both suites, and whether either DIED rather than failed.

    2026-08-28. The return code used to be discarded, so a mutation that
    CRASHES a suite produced an empty failure set and was reported as
    "expected <guard> to fail, got no failures" — which reads as a broken
    guard and is the opposite of the truth. mutate_part8 has kept the two
    apart since 2026-08-12; the distinction arrives here because a mutation
    that raised IndexError inside locate_in_text was mis-reported by it.
    """
    failed: set[str] = set()
    crashed = False
    for suite in SUITES:
        result = subprocess.run(
            [sys.executable, "-B", "-m", suite], cwd=ROOT, capture_output=True,
            text=True, encoding="utf-8", errors="replace", env=CHILD_ENV,
        )
        found = failures_from(result.stdout)
        failed |= found
        crashed = crashed or (result.returncode != 0 and not found)
    return failed, crashed


def failures_from(output: str) -> set[str]:
    return {
        line.split("FAIL", 1)[1].strip()
        for line in output.splitlines()
        if line.strip().startswith("FAIL")
    }


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
    original_bytes = {f: f.read_bytes() for f in SOURCES}
    newlines = {f: _newline_of(original_bytes[f]) for f in SOURCES}
    originals = {
        f: original_bytes[f].decode("utf-8").replace("\r\n", "\n")
        for f in SOURCES
    }
    problems: list[str] = []
    try:
        # 2026-08-28. THE BASELINE — see scripts/mutate_part8.py for the
        # argument at length. A mutation is evidence only if the guard it
        # names was PASSING before the code was broken.
        already_failing, baseline_crashed = run_suites()
        if already_failing or baseline_crashed:
            print(f"  BASELINE: {len(already_failing)} check(s) already fail "
                  f"with NO mutation applied"
                  + (" (and a suite exited non-zero)" if baseline_crashed
                     else "") + ".")
            for name in sorted(already_failing):
                print(f"            - {name}")
            print()

        for (label, patches), guard in zip(MUTATIONS, EXPECTED):
            if guard in already_failing:
                problems.append(
                    f"{label}: UNVERIFIED — its guard {guard!r} was already "
                    f"failing before any mutation was applied, so this "
                    f"mutation proves nothing. Fix the suite, then re-run."
                )
                print(f"  UNVERIFIED {label} (its guard was already red at "
                      f"baseline)")
                continue
            edited: dict = {f: originals[f] for f in SOURCES}
            missing = [
                old for old, _ in patches
                if not any(old in originals[f] for f in SOURCES)
            ]
            if missing:
                problems.append(f"{label}: mutation target not found")
                continue
            for old, new in patches:
                target = next(f for f in SOURCES if old in edited[f])
                edited[target] = edited[target].replace(old, new, 1)
            for f in SOURCES:
                _write(f, edited[f], newlines[f])
            failed, crashed = run_suites()
            if guard in failed:
                print(f"  ok   {label}")
                print(f"       -> {guard}")
            elif crashed:
                problems.append(
                    f"{label}: the suite CRASHED rather than failing the "
                    f"guard. A mutation that kills a suite proves nothing "
                    f"about the guard it names."
                )
                print(f"  MISS {label} (crash, not a guard failure)")
            else:
                problems.append(
                    f"{label}: expected {guard!r} to fail, got {sorted(failed) or 'no failures'}"
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

    check = subprocess.run(
        [sys.executable, "-m", "answer.test_answer"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if check.returncode != 0:
        problems.append(
            "sources restored, but `answer.test_answer` fails on its own "
            "account — a finding about the suite, not about this harness"
        )
        print("\n--- answer.test_answer output, so it is not lost ---")
        print((check.stdout or "") + (check.stderr or ""), end="")
        print("--- end ---")

    print()
    if problems:
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"all {len(MUTATIONS)} mutations verified; sources restored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
