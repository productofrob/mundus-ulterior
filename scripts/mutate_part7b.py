"""Mutation-verify the guards added after the first live run.

Each mutation breaks exactly one fix and asserts that the guard protecting that
fix — and specifically that guard, not merely *a* guard — reports FAIL. A test
that has never failed is a test whose failure mode is unknown.

Run: python scripts/mutate_part7b.py
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

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


def run_suites() -> set[str]:
    failed: set[str] = set()
    for suite in SUITES:
        result = subprocess.run(
            [sys.executable, "-m", suite], cwd=ROOT, capture_output=True, text=True
        )
        failed |= failures_from(result.stdout)
    return failed


def failures_from(output: str) -> set[str]:
    return {
        line.split("FAIL", 1)[1].strip()
        for line in output.splitlines()
        if line.strip().startswith("FAIL")
    }


def main() -> int:
    originals = {f: f.read_text(encoding="utf-8") for f in SOURCES}
    problems: list[str] = []
    try:
        for (label, patches), guard in zip(MUTATIONS, EXPECTED):
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
                f.write_text(edited[f], encoding="utf-8")
            failed = run_suites()
            if guard in failed:
                print(f"  ok   {label}")
                print(f"       -> {guard}")
            else:
                problems.append(
                    f"{label}: expected {guard!r} to fail, got {sorted(failed) or 'no failures'}"
                )
                print(f"  MISS {label}")
    finally:
        for f in SOURCES:
            f.write_text(originals[f], encoding="utf-8")

    # Two different failures, kept apart — see the note in mutate_part8.py.
    # A restore failure is checked by comparing content; a suite failure is a
    # finding about the suite and must not be reported as a corrupted tree.
    unrestored = [
        f.name for f in SOURCES
        if f.read_text(encoding="utf-8") != originals[f]
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
