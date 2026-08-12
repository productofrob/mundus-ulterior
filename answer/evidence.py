"""What may be shown to a reader, and with what qualification.

This module answers one question per retrieved passage: *which English, if any,
is this reader allowed to see, and what has to be said about it?* It is pure —
no database, no network — so the policy can be tested exhaustively offline, which
is the only kind of test this sandbox can run.

The four decisions Part 6 left for Part 7, and where each one lives:

1. **A blocking flag outranks the band.** `vimose-gmq-pro` is stored with band
   `low` AND the flag `untranslated_echo`. Filtering on band alone would present
   a machine "translation" of six partly undeciphered runic sequences — the worst
   output this system could produce, because it would arrive attached to a
   citation. `resolve_english` checks flags before it looks at the band, and a
   blocked translation yields `kind="none"` with the reason attached.

2. **Bands are genre-relative and must not be compared across profiles.** A
   `high` on verse (cos 0.70) and a `high` on prose (cos 0.96) are not the same
   evidence. So nothing here sorts, ranks or filters on band. Passage order is
   retrieval order and only retrieval order; `caveat_for` always names the
   profile and prints the raw cosine beside its threshold, so the band is never
   read on its own. There is a test that asserts ordering is unchanged when every
   band is permuted.

3. **What `medium` looks like to a reader.** Nine of twelve Part 6 cases banded
   medium: it is the common case, not the exception, and boilerplate would train
   the reader to skip it. So the caveat is specific — the profile, the observed
   cosine, the threshold it fell short of, and, where the profile is
   uncalibrated, the fact that the threshold itself is an analogy.

4. **Published wins; machine is the fallback.** 16 of 24 records carry a human
   translation. Preference order is set out in `resolve_english`.

One thing this module deliberately does NOT do: translate. If no English exists
for a passage, the answer says so. An inline translation made at answer time
would be unscored, uncached, unversioned and uncitable — everything Part 6 was
built to avoid.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict

from answer.confidence import BLOCKING_FLAGS

# How the English attached to a passage was obtained. Ordered best to worst.
ENGLISH_KINDS = ("source", "published", "published_document", "machine", "none")

# Part 4 measured the retrieval model's grip on each script. Old Tamil ranked
# first in its probe and did so at cosine 0.368, against 0.607-0.676 for Greek,
# Literary Chinese and Parthian — and there is exactly one Tamil chunk in the
# corpus, so it had nothing to be confused with. Part 6 then produced a valid
# Tamil round trip in one attempt out of three; the other two came back in the
# wrong script.
#
# Both facts are about the stack, not about the source, and neither is visible in
# the band. A reader told that a Tamil passage is `medium` on a verse profile has
# not been told that the pipeline handles Tamil worse than anything else it
# handles. Kept as data with the numbers in it, so the note can be checked rather
# than believed.
RETRIEVAL_LANG_NOTES: dict[str, str] = {
    "oty": (
        "Old Tamil is the weakest language in this pipeline. It matched its own "
        "probe at cosine 0.368 where Greek, Literary Chinese and Parthian ran "
        "0.61-0.68, and one machine round trip in three came back in the wrong "
        "script. Claims resting on this passage are weaker than claims resting "
        "on the Greek."
    ),
}


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------

@dataclass
class ChunkRecord:
    """One row of `citable_passages`. Everything needed to quote and to cite."""
    chunk_id: str
    doc_id: str
    role: str                 # original | translation
    seq: int
    lang: str
    text: str
    citation: str
    region: str
    source_type: str
    text_fidelity: str
    source_field: str
    char_start: int
    char_end: int
    date_text: str | None = None
    title: str | None = None
    translation_source: str | None = None
    citation_original: str | None = None
    language_note: str | None = None
    parallel_group: str | None = None

    @property
    def is_english(self) -> bool:
        return self.lang == "en"


@dataclass
class TranslationRecord:
    """One row of `current_translations` — a Part 6 machine translation whose
    source text has not changed since it was made. The view enforces that; this
    dataclass never has to check it."""
    chunk_id: str
    translated_text: str
    confidence_band: str
    confidence_profile: str | None = None
    flags: list[str] = field(default_factory=list)
    chrf_back: float | None = None
    cos_back: float | None = None
    chrf_ref: float | None = None
    cos_ref: float | None = None
    translation_model: str | None = None
    prompt_version: str | None = None
    back_prompt_version: str | None = None

    @property
    def blocking_flags(self) -> list[str]:
        return [f for f in self.flags if f in BLOCKING_FLAGS]


# --------------------------------------------------------------------------
# The choice
# --------------------------------------------------------------------------

@dataclass
class EnglishChoice:
    kind: str                       # one of ENGLISH_KINDS
    text: str | None = None
    ground: str | None = None       # section | index | document | none
    attribution: str | None = None  # translator, for a published translation
    band: str | None = None
    profile: str | None = None
    profile_calibrated: bool | None = None
    flags: list[str] = field(default_factory=list)
    cos_back: float | None = None
    chrf_back: float | None = None
    reason: str | None = None       # why kind == 'none', or why a fallback was taken


def resolve_english(
    chunk: ChunkRecord,
    *,
    published_text: str | None = None,
    published_ground: str | None = None,
    published_attribution: str | None = None,
    machine: TranslationRecord | None = None,
    profiles: dict | None = None,
) -> EnglishChoice:
    """Decide which English a reader may see for one passage.

    Preference order, and the argument for it:

      1. the chunk is already English         -> kind 'source'
      2. a published translation ALIGNED to
         this passage (section or index)      -> kind 'published'
      3. a Part 6 machine translation with no
         blocking flag                        -> kind 'machine'
      4. a published translation of the
         DOCUMENT that could not be aligned
         to this passage                      -> kind 'published_document'
      5. nothing                              -> kind 'none'

    Steps 3 and 4 are in that order and it is the one non-obvious choice here.
    A human translation is better evidence of *accuracy* than a machine one; a
    passage-aligned translation is better evidence of *what this passage says*.
    When the human translation covers the document but cannot be pinned to the
    passage, quoting it beside a §-numbered citation would attribute words to a
    passage that may not contain them — a mis-citation, which is the specific
    thing Part 7 exists to prevent. The machine translation is at least of the
    right passage by construction, and it arrives labelled with a confidence
    band. So it goes first, and the document-level human translation is offered
    below it, labelled as covering the document.

    `published_ground` comes from `answer.align.Pair.ground` and travels all the
    way to the reader. 'index' pairing is positional and align.py labels it
    weaker; that word reaches the caveat.
    """
    if chunk.is_english:
        return EnglishChoice(kind="source", text=chunk.text, ground="self")

    aligned = published_ground in ("section", "index")
    if published_text and aligned:
        return EnglishChoice(
            kind="published",
            text=published_text,
            ground=published_ground,
            attribution=published_attribution,
        )

    if machine is not None:
        blocking = machine.blocking_flags
        if blocking:
            choice = EnglishChoice(
                kind="none",
                flags=list(machine.flags),
                band=machine.confidence_band,
                profile=machine.confidence_profile,
                reason=(
                    f"the machine translation of this passage is blocked by "
                    f"{', '.join(blocking)}. A blocking flag means the round trip "
                    f"did not measure translation quality, so the English it "
                    f"produced cannot be shown at all — no band is low enough to "
                    f"make it safe to quote."
                ),
            )
            # A blocked machine translation does not cancel a human one.
            if published_text:
                return EnglishChoice(
                    kind="published_document",
                    text=published_text,
                    ground=published_ground or "document",
                    attribution=published_attribution,
                    flags=list(machine.flags),
                    reason=(
                        f"{choice.reason} The published translation below covers "
                        f"the document rather than this passage specifically."
                    ),
                )
            return choice

        profile_calibrated = None
        if profiles and machine.confidence_profile in profiles:
            profile_calibrated = bool(profiles[machine.confidence_profile].calibrated)

        return EnglishChoice(
            kind="machine",
            text=machine.translated_text,
            ground="passage",
            attribution=machine.translation_model,
            band=machine.confidence_band,
            profile=machine.confidence_profile,
            profile_calibrated=profile_calibrated,
            flags=list(machine.flags),
            cos_back=machine.cos_back,
            chrf_back=machine.chrf_back,
        )

    if published_text:
        return EnglishChoice(
            kind="published_document",
            text=published_text,
            ground=published_ground or "document",
            attribution=published_attribution,
            reason=(
                "this published translation could not be aligned to the passage, "
                "so it is offered as covering the document, not these lines."
            ),
        )

    return EnglishChoice(
        kind="none",
        reason=(
            "no English exists for this passage: the record carries no published "
            "translation, and no Part 6 machine translation has been made and "
            "scored for it. It has NOT been translated here — an untracked "
            "translation made at answer time would carry no confidence score and "
            "no provenance, and would still arrive attached to a citation."
        ),
    )


# --------------------------------------------------------------------------
# The passage a reader sees
# --------------------------------------------------------------------------

@dataclass
class Passage:
    """One numbered source in an answer's evidence block."""
    marker: str                     # 'S1'
    chunk: ChunkRecord
    english: EnglishChoice
    similarity: float | None = None
    rank: int | None = None
    lang_note: str | None = None
    # The English-translation chunk folded into this passage, if one was
    # retrieved separately. Kept so the citation record can say the answer stood
    # on two chunks, not one.
    translation_chunk_id: str | None = None
    # The same chunk as a record rather than an id. A published translation is
    # not a floating string: it is a chunk of the seed JSON with its own field
    # and its own character span, exactly like the original. Carrying the record
    # is what lets a quotation from the English resolve to characters on disk
    # instead of being verified and then dropped — which is what happened to
    # every quotation in the first live run.
    translation_chunk: ChunkRecord | None = None

    @property
    def chunk_id(self) -> str:
        return self.chunk.chunk_id

    @property
    def doc_id(self) -> str:
        return self.chunk.doc_id

    @property
    def has_english(self) -> bool:
        return bool(self.english.text)

    @property
    def quotable_texts(self) -> list[str]:
        """Every string a claim citing this passage is allowed to quote.

        The source text is always quotable — it is characters on disk. English is
        quotable only when `resolve_english` produced some; when it did not, the
        absence is the point, and a quotation that cannot be found here is the
        signal that the model wrote English of its own.
        """
        texts = [self.chunk.text]
        if self.english.text:
            texts.append(self.english.text)
        return texts

    def to_dict(self) -> dict:
        return {
            "marker": self.marker,
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "rank": self.rank,
            "similarity": self.similarity,
            "lang": self.chunk.lang,
            "region": self.chunk.region,
            "citation": self.chunk.citation,
            "source_field": self.chunk.source_field,
            "char_start": self.chunk.char_start,
            "char_end": self.chunk.char_end,
            "english": asdict(self.english),
            "lang_note": self.lang_note,
            "translation_chunk_id": self.translation_chunk_id,
        }


def caveat_for(passage: Passage, profiles: dict | None = None) -> str:
    """The sentence a reader needs in order to weigh this passage correctly.

    Never boilerplate. Nine of twelve Part 6 cases banded `medium`, so a generic
    "medium confidence" line would be attached to most of the corpus and read as
    noise within a page. Each branch below names what is actually known.
    """
    english = passage.english
    kind = english.kind

    if kind == "source":
        return "This source is in English; nothing has been translated."

    if kind == "published":
        ground = (
            "aligned to this passage by the section numbers both texts carry"
            if english.ground == "section"
            else "paired with this passage by position — both sides split into "
                 "the same number of passages in the same order, which is weaker "
                 "evidence than matching section numbers"
        )
        who = f" ({english.attribution})" if english.attribution else ""
        return f"English from the published translation{who}, {ground}."

    if kind == "published_document":
        who = f" ({english.attribution})" if english.attribution else ""
        return (
            f"English from the published translation{who}, which covers the whole "
            f"record rather than this passage specifically. It may not contain "
            f"these particular lines, so do not read it as a rendering of them."
        )

    if kind == "none":
        return english.reason or "No English is available for this passage."

    # machine
    profile_name = english.profile or "unprofiled"
    profile = (profiles or {}).get(profile_name)
    parts: list[str] = [
        f"English by MACHINE TRANSLATION ({english.attribution or 'model unrecorded'}), "
        f"confidence {english.band or 'unscored'} on the {profile_name} profile."
    ]

    if english.cos_back is not None and profile is not None:
        if english.band == "high":
            parts.append(
                f"It round-trips at cosine {english.cos_back:.3f}, at or above "
                f"the {profile_name} threshold of {profile.cos_high:.2f}."
            )
        elif english.band == "medium":
            parts.append(
                f"It round-trips at cosine {english.cos_back:.3f}, below the "
                f"{profile_name} threshold of {profile.cos_high:.2f} for high and "
                f"above {profile.cos_low:.2f} for low. The sense survived a round "
                f"trip; the exact wording is not evidence."
            )
        else:
            parts.append(
                f"It round-trips at cosine {english.cos_back:.3f}, below the "
                f"{profile_name} floor of {profile.cos_low:.2f}. Treat it as an "
                f"indication of subject matter, not of what the passage says."
            )
    elif english.cos_back is not None:
        parts.append(f"It round-trips at cosine {english.cos_back:.3f}.")

    if english.profile_calibrated is False:
        parts.append(
            f"The {profile_name} threshold is set by analogy rather than "
            f"measurement — the corpus does not yet hold enough of this genre to "
            f"calibrate it — so the band itself is provisional."
        )

    non_blocking = [f for f in english.flags if f not in BLOCKING_FLAGS]
    if "semantic_ok_lexical_low" in non_blocking:
        parts.append(
            "Meaning survived the round trip but wording did not: this is a "
            "paraphrase, so quote the source text rather than this English."
        )
    if "short_source_chrf_noisy" in non_blocking:
        parts.append(
            "The passage is short enough that its wording score is noisy; the "
            "cosine above is the number to read."
        )
    if "disagrees_with_published_translation" in non_blocking:
        parts.append(
            "It is self-consistent but differs from the published translation of "
            "this record. Self-consistency is not accuracy."
        )

    parts.append(
        "Round-trip confidence measures self-consistency, not accuracy: a model "
        "can mistranslate a passage and mistranslate it back the same way."
    )
    return " ".join(parts)


def build_passages(
    ranked: list[tuple[ChunkRecord, float]],
    *,
    english_by_chunk: dict[str, EnglishChoice],
    max_sources: int | None = None,
    translation_chunk_by_chunk: dict[str, str] | None = None,
    translation_record_by_chunk: dict[str, ChunkRecord] | None = None,
) -> list[Passage]:
    """Number the evidence.

    Order is retrieval order, full stop. Not band, not language, not whether a
    published translation exists. Ranking by band would compare a `high` on verse
    against a `medium` on prose, which the Part 6 profiles file warns in writing
    is a false comparison; ranking by translation availability would put the
    best-served sources first and quietly bury the ones the corpus handles worst,
    which is the opposite of what this project is for.
    """
    passages: list[Passage] = []
    for rank, (chunk, similarity) in enumerate(ranked, start=1):
        if max_sources is not None and len(passages) >= max_sources:
            break
        passages.append(
            Passage(
                marker=f"S{len(passages) + 1}",
                chunk=chunk,
                english=english_by_chunk.get(
                    chunk.chunk_id, EnglishChoice(kind="none", reason="not resolved")
                ),
                similarity=similarity,
                rank=rank,
                lang_note=RETRIEVAL_LANG_NOTES.get(chunk.lang),
                translation_chunk_id=(translation_chunk_by_chunk or {}).get(
                    chunk.chunk_id
                ),
                translation_chunk=(translation_record_by_chunk or {}).get(
                    chunk.chunk_id
                ),
            )
        )
    return passages
