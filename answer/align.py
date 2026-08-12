"""Pairing original chunks with their published-translation chunks.

Part 3 set `parallel_group` at document level and said so plainly: passage-level
alignment was not something the pipeline could honestly claim, because the two
sides of a record do not always split into the same number of pieces.

Part 6 needs a pair — machine English against published English — for the same
passage, not the same document. So alignment is computed here, from evidence in
the text, and reports which of three grounds it used:

    "section"   both sides carry the same section markers (§56 / "56.").
                Strongest: the pairing is stated by the sources themselves.
    "index"     no markers, but both sides split into the same number of
                chunks in the same order. Plausible, and labelled as weaker.
    "none"      counts differ and no markers. No pairing is claimed.

The ground travels with the pair so a downstream score can never be read as
better-evidenced than it is.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, is_dataclass, replace
from typing import Sequence

# "53." / "§ 56" / "56)" at the very start of a chunk. Anchored deliberately:
# a number in the middle of a sentence ("five hundred stadia") is not a marker.
_SECTION_RE = re.compile(r"^\s*(?:§\s*)?(\d{1,4})\s*[.)\]]?\s")


def section_label(text: str) -> str | None:
    match = _SECTION_RE.match(text or "")
    return match.group(1) if match else None


@dataclass
class Pair:
    original: object          # anything with .text; a Hit or a row wrapper
    translation: object | None
    ground: str               # section | index | none
    label: str | None = None
    # Every chunk the translation was built from. A merged section carries only
    # its first member's chunk_id, so a caller mapping translation chunks back
    # to their original — `fold_hits` does — would treat the other members as
    # orphans and show them as separate sources saying the same thing.
    members: list = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.members and self.translation is not None:
            self.members = [self.translation]


def _labels(items: Sequence) -> list[str | None]:
    return [section_label(getattr(i, "text", "")) for i in items]


def _inherited_labels(items: Sequence) -> list[str | None]:
    """Section label per chunk, carried forward across continuation chunks.

    A section longer than the chunker's limit becomes several chunks and only
    the first carries the marker. Requiring a marker on every chunk — as this
    module did until 2026-08-10 — meant that one long section anywhere in a
    translation silently disabled section alignment for the whole record.
    """
    labels: list[str | None] = []
    current: str | None = None
    for item in items:
        found = section_label(getattr(item, "text", ""))
        if found is not None:
            current = found
        labels.append(current)
    return labels


def _merge(chunks: list) -> object:
    """Several chunks of one section, presented as the section.

    The gap between two adjacent chunks is filled with as many spaces as the
    characters that were dropped between them, so `char_start + offset` still
    lands on the right character for text taken from any member. Quote matching
    is whitespace-insensitive, so substituting spaces for the original newlines
    costs nothing and keeps the arithmetic exact.
    """
    if len(chunks) == 1:
        return chunks[0]
    first, last = chunks[0], chunks[-1]
    if not is_dataclass(first):
        return first
    parts = [first.text]
    for previous, following in zip(chunks, chunks[1:]):
        gap = getattr(following, "char_start", 0) - getattr(previous, "char_end", 0)
        parts.append(" " * max(0, gap) + following.text)
    return replace(first, text="".join(parts), char_end=last.char_end)


def _section_groups(items: Sequence) -> list[tuple[str | None, list]]:
    groups: list[tuple[str | None, list]] = []
    for item, label in zip(items, _inherited_labels(items)):
        if groups and groups[-1][0] == label:
            groups[-1][1].append(item)
        else:
            groups.append((label, [item]))
    return groups


def pair_chunks(originals: Sequence, translations: Sequence) -> list[Pair]:
    """Pair two ordered lists of chunks from the same document.

    Originals are returned unmerged — `fold_hits` keys on the retrieved chunk's
    own id, so merging them would break the lookup. Translations are merged per
    section, because a section is the unit the two sides agree on and a chunk is
    an artefact of how long the prose happens to be. Where an original section
    is itself split, every one of its chunks is paired with the whole English
    section: the ground is still the section number, which is what the caveat
    tells the reader.
    """
    if not originals:
        return []
    if not translations:
        return [Pair(o, None, "none") for o in originals]

    o_labels = _inherited_labels(originals)
    t_groups = _section_groups(translations)

    if all(l is not None for l in o_labels) and all(
        label is not None for label, _ in t_groups
    ):
        by_label = {label: _merge(chunks) for label, chunks in t_groups}
        members_by_label = {label: list(chunks) for label, chunks in t_groups}
        # Only claim section alignment if the markers actually correspond;
        # two texts numbered 1..n independently would otherwise "align" by
        # coincidence of counting.
        if set(o_labels) & set(by_label):
            return [
                Pair(
                    o, by_label.get(l),
                    "section" if by_label.get(l) else "none", l,
                    members_by_label.get(l, []),
                )
                for o, l in zip(originals, o_labels)
            ]

    if len(originals) == len(translations):
        return [Pair(o, t, "index") for o, t in zip(originals, translations)]

    return [Pair(o, None, "none") for o in originals]
