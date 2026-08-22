"""Chunker tests.

No record in the current seed corpus is long enough to trigger splitting, so
the splitting paths are exercised here against synthetic input. They matter as
soon as the verbatim texts get pulled from the critical editions — the Palmyrene
Tariff alone runs to ~400 lines.

Run: python -m ingest.test_chunker
"""

from __future__ import annotations

from .chunker import DEFAULT_MAX_CHARS, chunk_field, estimate_tokens

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
# about where THIS process is writing, and until 2026-08-22 nothing guarded it.
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

failures: list[str] = []


def expect(condition: bool, label: str) -> None:
    if condition:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


def assert_roundtrip(source: str, label: str) -> list:
    """Every span must slice back out of the source byte-for-byte."""
    spans = chunk_field(source)
    ok = all(span.text_of(source) == source[span.start:span.end] for span in spans)
    covered = "".join(span.text_of(source) for span in spans)
    stripped_source = "".join(source.split())
    expect(ok, f"{label}: spans slice exactly")
    expect(
        "".join(covered.split()) == stripped_source,
        f"{label}: no content lost or duplicated",
    )
    ordered = all(
        spans[i].end <= spans[i + 1].start for i in range(len(spans) - 1)
    )
    expect(ordered, f"{label}: spans are ordered and non-overlapping")
    return spans


def main() -> int:
    print("short field stays whole")
    short = "harja — the oldest datable runic inscription, c. 160 CE."
    spans = assert_roundtrip(short, "short")
    expect(len(spans) == 1, "short: single chunk")
    expect(spans[0].text_of(short) == short, "short: chunk equals whole field")

    print("\nwhitespace is trimmed without breaking offsets")
    padded = "   \n  Muziris abounds in ships.  \n\n "
    spans = chunk_field(padded)
    expect(len(spans) == 1, "padded: single chunk")
    expect(
        spans[0].text_of(padded) == "Muziris abounds in ships.",
        "padded: leading/trailing whitespace excluded",
    )
    expect(
        padded[spans[0].start:spans[0].end] == "Muziris abounds in ships.",
        "padded: offsets still index the original string",
    )

    print("\nlong text splits on § section markers, not mid-sentence")
    section = " ".join(["Lorem ipsum dolor sit amet consectetur."] * 12)
    sectioned = f"§ 1 {section} § 2 {section} § 3 {section}"
    spans = assert_roundtrip(sectioned, "sectioned")
    expect(len(spans) > 1, "sectioned: did split")
    expect(
        all(len(s) <= DEFAULT_MAX_CHARS for s in spans),
        "sectioned: every chunk within budget",
    )
    starts = [s.text_of(sectioned).lstrip()[:3] for s in spans]
    expect(
        all(t.startswith("§") for t in starts),
        f"sectioned: each chunk begins at a § boundary (got {starts})",
    )

    print("\nlong text with no § falls through to line boundaries")
    lines = "\n".join(f"line {i} of an inscription face, reading left to right" for i in range(40))
    spans = assert_roundtrip(lines, "lines")
    expect(len(spans) > 1, "lines: did split")
    expect(
        all(len(s) <= DEFAULT_MAX_CHARS for s in spans),
        "lines: every chunk within budget",
    )
    expect(
        all(not s.text_of(lines).startswith("\n") for s in spans),
        "lines: no chunk starts mid-break",
    )

    print("\nlong single-paragraph prose falls through to sentence boundaries")
    prose = " ".join(
        f"Sentence number {i} describes a cargo of nard and ivory." for i in range(60)
    )
    spans = assert_roundtrip(prose, "prose")
    expect(len(spans) > 1, "prose: did split")
    expect(
        all(len(s) <= DEFAULT_MAX_CHARS for s in spans),
        "prose: every chunk within budget",
    )
    expect(
        all(s.text_of(prose).rstrip().endswith(".") for s in spans),
        "prose: chunks end at sentence boundaries",
    )

    print("\nCJK text with no whitespace or Latin punctuation")
    cjk = "大秦國一號犂靬，在安息、條支西大海之西。" * 40
    spans = assert_roundtrip(cjk, "cjk")
    expect(
        all(len(s) <= DEFAULT_MAX_CHARS for s in spans),
        "cjk: every chunk within budget (splits on 。)",
    )

    print("\npathological input: one unbroken token longer than the budget")
    blob = "x" * (DEFAULT_MAX_CHARS * 3)
    spans = assert_roundtrip(blob, "blob")
    expect(len(spans) == 1, "blob: returns one oversized chunk rather than cutting mid-token")

    print("\nedge cases")
    expect(chunk_field("") == [], "empty string yields no chunks")
    expect(chunk_field("   \n  ") == [], "whitespace-only yields no chunks")
    expect(chunk_field(None) == [], "None yields no chunks")
    expect(estimate_tokens("abcd") == 1, "token estimate floors at 1")

    if failures:
        print(f"\nFAILED ({len(failures)})")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("\nAll chunker tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
