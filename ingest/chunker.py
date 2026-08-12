"""Meaning-aware chunking.

Per the Getting-Started Guide §3: chunk on meaning, not bytes. An inscription
line, a poem stanza, or a numbered section of the Periplus stays whole. A field
is only split when it exceeds the size budget, and then only at the strongest
natural boundary available.

Every span returned is an exact (start, end) offset pair into the source string,
so `source_text[start:end] == chunk_text` always holds. That property is what
lets a citation in Part 7 be traced back to characters on disk.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ~4 chars per token is a reasonable cross-lingual rule of thumb for budgeting;
# CJK runs denser, which only makes us conservative.
CHARS_PER_TOKEN = 4
DEFAULT_MAX_CHARS = 1200   # ≈300 tokens
DEFAULT_MIN_CHARS = 200    # below this, merge with the neighbouring piece

# Boundary tiers, strongest first. Each pattern matches the point AFTER which a
# split may occur, so the delimiter stays attached to the preceding piece.
_BOUNDARY_TIERS: list[re.Pattern[str]] = [
    re.compile(r"(?=§\s*\d)"),                    # § 1, § 20 — Periplus/ŠKZ sections
    re.compile(r"\n\s*\n"),                        # paragraph break
    re.compile(r"\n"),                             # line break (inscription lines)
    re.compile(r"(?<=[.!?。！？；;])\s+"),          # sentence end
]


@dataclass(frozen=True)
class Span:
    """An exact character range within a source field."""
    start: int
    end: int

    def text_of(self, source: str) -> str:
        return source[self.start:self.end]

    def __len__(self) -> int:
        return self.end - self.start


def estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / CHARS_PER_TOKEN))


def _trim_span(source: str, start: int, end: int) -> Span | None:
    """Shrink a span past leading/trailing whitespace, preserving exactness."""
    while start < end and source[start].isspace():
        start += 1
    while end > start and source[end - 1].isspace():
        end -= 1
    return Span(start, end) if end > start else None


def _split_at_tier(
    source: str, start: int, end: int, pattern: re.Pattern[str]
) -> list[tuple[int, int]]:
    """Cut [start, end) at every match of `pattern`. Returns raw ranges."""
    cuts: list[int] = []
    for m in pattern.finditer(source, start, end):
        # Zero-width lookahead patterns split before the match; delimiter
        # patterns split after the matched separator.
        point = m.start() if m.start() == m.end() else m.end()
        if start < point < end:
            cuts.append(point)
    if not cuts:
        return [(start, end)]

    ranges: list[tuple[int, int]] = []
    prev = start
    for c in cuts:
        ranges.append((prev, c))
        prev = c
    ranges.append((prev, end))
    return [r for r in ranges if r[1] > r[0]]


def _merge_small(
    ranges: list[tuple[int, int]], max_chars: int, min_chars: int
) -> list[tuple[int, int]]:
    """Greedily glue adjacent ranges back together while they fit the budget.

    Prevents a long text from shattering into one-clause fragments just because
    a fine-grained boundary tier happened to match.
    """
    merged: list[tuple[int, int]] = []
    for rng in ranges:
        if not merged:
            merged.append(rng)
            continue
        prev_start, prev_end = merged[-1]
        combined = rng[1] - prev_start
        prev_len = prev_end - prev_start
        if combined <= max_chars and (prev_len < min_chars or (rng[1] - rng[0]) < min_chars):
            merged[-1] = (prev_start, rng[1])
        else:
            merged.append(rng)
    return merged


def _split_range(
    source: str,
    start: int,
    end: int,
    max_chars: int,
    min_chars: int,
    tier: int = 0,
) -> list[tuple[int, int]]:
    """Recursively split [start, end) until every piece fits, or tiers run out."""
    if end - start <= max_chars or tier >= len(_BOUNDARY_TIERS):
        return [(start, end)]

    pieces = _split_at_tier(source, start, end, _BOUNDARY_TIERS[tier])
    if len(pieces) == 1:
        # This tier found nothing; try the next one on the same range.
        return _split_range(source, start, end, max_chars, min_chars, tier + 1)

    pieces = _merge_small(pieces, max_chars, min_chars)

    out: list[tuple[int, int]] = []
    for p_start, p_end in pieces:
        if p_end - p_start > max_chars:
            out.extend(_split_range(source, p_start, p_end, max_chars, min_chars, tier + 1))
        else:
            out.append((p_start, p_end))
    return out


def chunk_field(
    source: str,
    max_chars: int = DEFAULT_MAX_CHARS,
    min_chars: int = DEFAULT_MIN_CHARS,
) -> list[Span]:
    """Split one text field into meaning-preserving spans.

    Short fields — which is most of this corpus — come back as a single span
    covering the whole field. Nothing is split that doesn't need to be.
    """
    if source is None:
        return []
    whole = _trim_span(source, 0, len(source))
    if whole is None:
        return []

    if len(whole) <= max_chars:
        return [whole]

    spans: list[Span] = []
    for s, e in _split_range(source, whole.start, whole.end, max_chars, min_chars):
        trimmed = _trim_span(source, s, e)
        if trimmed is not None:
            spans.append(trimmed)
    return spans or [whole]
