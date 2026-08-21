"""Grounded answer assembly: retrieve, resolve, ask, verify.

The pipeline, and where each step's rules live:

    question
      -> embed (ingest.embed, input_type='query')
      -> search retrievable_chunks           retrieve/search.py
      -> hydrate to citable_passages         answer/answer_store.py
      -> fold each document's translation
         chunk into its original             answer/align.py
      -> decide which English may be shown   answer/evidence.py
      -> render the evidence block           answer/cite.py
      -> one chat call                       this module
      -> verify against the evidence         answer/cite.py
      -> store answer + citations            answer/answer_store.py

Two things this module refuses to do.

**It does not translate.** If a retrieved passage has no published translation
and no scored Part 6 machine translation, the evidence block says so and the
prompt forbids the model from supplying one. An inline translation made at answer
time would have no confidence band, no prompt version, no cache key and no
back-translation — and it would still arrive attached to a citation, which is the
one thing that makes a wrong translation dangerous rather than merely wrong.

**It does not rank on confidence band.** Bands are genre-relative: a `high` on
verse sits at cosine 0.70 and a `high` on prose at 0.96, and the Part 6 profiles
file records that in writing as `cross_profile_warning`. Evidence order is
retrieval order.

Prompt versioning follows Part 4's `embedding_model` and Part 6's
`prompt_version`: the version string is stored with every answer and forms part
of the answer's identity, so changing the contract writes new rows instead of
silently replacing the evidence the old contract produced.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

from answer import answer_store, cite
from answer.align import pair_chunks
from answer.evidence import (
    ChunkRecord,
    EnglishChoice,
    Passage,
    build_passages,
    resolve_english,
)
from answer.translate import DEFAULT_MODEL, TranslationError, _chat

# v2 after the first live run: rule 3 now says the header line is not quotable,
# and rule 6 makes the citation requirement on the post-refusal sentence
# unmissable. Bumped rather than edited in place, for the reason Part 6 learned
# the hard way — the version is part of `answer_id`, so v1's answers stay
# readable instead of being overwritten by output from a different prompt.
# v3 after the second live run, which exposed a conflict v2 created between its
# own rules 4 and 6: rule 6 told the model to cite the sources it was
# characterising, and on the Aksum question the set it was characterising
# included a passage with no English. Complying with rule 6 therefore breached
# rule 4. v3 resolves it in rule 4's favour — cite only what you can read.
#
# v4 narrowed v3's clause to a mechanical test. It did not work: Vimose failed
# 0/3 under v3 and 0/3 under v4, and passed 3/3 under v2 with byte-identical
# output. Measured over 30 runs in the Part 8 sweep, with refusal rate rising
# 40% -> 60%.
#
# So the default reverts to the reconstructed v2. The clause v3 and v4 shared
# duplicated the `claims_on_untranslated` check, which already existed and costs
# nothing — and the condition that motivated it (a retrieved passage with no
# English at all) can no longer arise from this corpus, since Part 7 gave all 18
# non-English passages an aligned published translation.
#
# The standing lesson, on its fourth occurrence: when two prompt versions in a
# row fail to fix a behaviour, the problem is not in the prompt. And: prefer a
# check to a rule. v3 and v4 are kept in the registry so the comparison can be
# re-run rather than reconstructed again.
ANSWER_PROMPT_VERSION = "p7-answer-v2r"

DEFAULT_K = 12               # retrieved before folding
DEFAULT_MAX_SOURCES = 6      # shown to the model after folding
DEFAULT_MAX_TOKENS = 1600

# Defined in `cite` because that is where it is enforced: the refusal is exempt
# from the uncited-claim check, and a second copy of the string here would let
# the two drift apart silently.
NO_ANSWER = cite.REFUSAL_SENTENCE


# --------------------------------------------------------------------------
# Prompt versions
# --------------------------------------------------------------------------
#
# Every version's TEXT lives here, not just its name. Until Part 8 only the
# name was kept: `ANSWER_PROMPT_VERSION` was bumped and the prose was edited in
# place, so the archive records that sixteen answers were produced under three
# prompts while the repository holds exactly one of those three. "Run v2 again"
# was not a reproducible instruction.
#
# That is the same defect Part 6 fixed for `back_prompt_version` and Part 4 for
# `embedding_model`, arriving a third time in a new disguise: a label was stored
# and the thing it labelled was not. A registry makes editing in place
# impossible — a changed contract has to be a new entry, because the old entry
# is still sitting beside it.
#
# `p7-answer-v2r` is RECONSTRUCTED from the v3 change note, not recovered: v2's
# exact wording is gone. The `r` is in the version string so its answers can
# never be pooled with the archived v2 rows as though they came from the same
# prompt. If the two agree, that is evidence the reconstruction is faithful; it
# is not a substitute for having kept the text.

_RULES_1_TO_5 = f"""You answer questions about contact between the Roman world \
and the regions beyond it, using ONLY the numbered sources supplied to you. You \
are writing for readers who will check you.

Rules, in order of importance:

1. Use only the supplied sources. You have no other knowledge for this task. Do \
not add background, context, dates, identifications or explanations that are not \
in the sources, however certain you are of them.

2. Every sentence that states a fact ends with a citation marker: [S1], or \
[S1][S3] where two sources support it. A sentence with no marker is a sentence \
that will be rejected.

3. Quote sparingly, and when you quote, copy the characters exactly from the \
source block — from the SOURCE TEXT or from the ENGLISH shown for that source. \
Put quotations in double quotation marks. Do not adjust spelling, accents, or \
punctuation. A quotation that cannot be found in the source it cites will be \
rejected. Quote only those two blocks: the title, date, region and citation on \
a source's header line were written by this corpus's editors, not by the source, \
and quoting them presents an editorial description as evidence.

4. Do not translate anything. Where a source shows ENGLISH, use it. Where a \
source says ENGLISH: NONE AVAILABLE, you may quote its source text verbatim and \
say what the record is, but you may NOT say what it means. Producing your own \
reading of an untranslated passage will be rejected.

5. Read the HOW TO USE THIS SOURCE line for each source and let it shape what \
you claim. Where English is a machine translation, say so in your own text the \
first time you rely on it, and prefer the sense over the exact wording. Where \
two sources disagree, say that they disagree and cite both.
"""

_CLOSING = """
Write plain prose, three to six sentences unless the question needs more. No \
headings, no bullet lists, no preamble, no closing summary."""

# v2, reconstructed. Rule 6 requires the post-refusal sentence to carry markers
# and says nothing about which sources may be named. On the Aksum question this
# collided with rule 4: the set being characterised included a passage with no
# English, so complying with 6 breached 4.
_RULE_6_V2R = f"""
6. If the sources do not answer the question, write exactly this sentence: \
"{NO_ANSWER}" After it you may write ONE further sentence saying what the \
sources do cover, and that sentence MUST end with citation markers naming the \
sources you are characterising, exactly as rule 2 requires — it is a sentence \
about the sources, so cite them.
"""

# v3. Resolves the 4/6 conflict in rule 4's favour — and overshoots. "Cite only
# sources you can read" asks the model to judge readability, and on the Vimose
# question it judged a published but hedged English gloss unreadable and
# retreated, three runs out of three, from the passage v2 answered best.
_RULE_6_V3 = f"""
6. If the sources do not answer the question, write exactly this sentence: \
"{NO_ANSWER}" After it you may write ONE further sentence saying what the \
sources do cover, and that sentence MUST end with citation markers naming the \
sources you are characterising, exactly as rule 2 requires — it is a sentence \
about the sources, so cite them. Cite only sources you can read: do not name a \
source shown as ENGLISH: NONE AVAILABLE in that sentence, and do not say what \
such a source is about, because saying what an untranslated passage covers is \
saying what it means. If you cannot cite the sentence under those terms, stop \
after the refusal and write nothing else. Do not fill the gap.
"""

# v4. The narrowing. v3's restriction is kept but its test stops being a
# judgement and becomes mechanical: the marker ENGLISH: NONE AVAILABLE, and
# nothing else. Three prompt versions in a row have been broken by a conflict
# between their own rules, and each time the rule that broke asked the model to
# decide something. A rule the model has to interpret is a rule that will be
# interpreted more broadly than written, and "sources you can read" was read as
# "sources whose English I consider adequate".
#
# The added sentence is not a new instruction; it is the same restriction stated
# from the other side, so that the boundary is unambiguous in both directions.
# Rules 1-5 are untouched, so rule 6 remains the only delta from v3 and the
# comparison stays clean.
_RULE_6_V4 = f"""
6. If the sources do not answer the question, write exactly this sentence: \
"{NO_ANSWER}" After it you may write ONE further sentence saying what the \
sources do cover, and that sentence MUST end with citation markers naming the \
sources you are characterising, exactly as rule 2 requires — it is a sentence \
about the sources, so cite them. In that sentence do not name a source whose \
English block reads exactly "ENGLISH: NONE AVAILABLE", and do not say what such \
a source is about, because saying what an untranslated passage covers is saying \
what it means. That restriction applies to those sources and to no others: a \
source that shows ENGLISH is usable in full, however partial, hedged or \
uncertain that English is. Report the hedges as hedges and cite it. Do not \
refuse a question the sources answer only cautiously, and do not treat a \
cautious translation as a missing one.
"""

ANSWER_PROMPTS: dict[str, str] = {
    "p7-answer-v2r": _RULES_1_TO_5 + _RULE_6_V2R + _CLOSING,
    "p7-answer-v3": _RULES_1_TO_5 + _RULE_6_V3 + _CLOSING,
    "p7-answer-v4": _RULES_1_TO_5 + _RULE_6_V4 + _CLOSING,
}

SYSTEM_ANSWER = ANSWER_PROMPTS[ANSWER_PROMPT_VERSION]


def system_prompt(version: str | None = None) -> str:
    version = version or ANSWER_PROMPT_VERSION
    if version not in ANSWER_PROMPTS:
        raise KeyError(
            f"unknown answer prompt version {version!r}. Known: "
            f"{sorted(ANSWER_PROMPTS)}. A version whose text was not kept "
            f"cannot be re-run — that is why the registry exists."
        )
    return ANSWER_PROMPTS[version]


@dataclass
class AssembledAnswer:
    question: str
    answer_text: str
    passages: list[Passage]
    grounding: cite.GroundingReport
    sources_block: str
    model: str
    prompt_version: str = ANSWER_PROMPT_VERSION
    embedding_model: str | None = None
    retrieval_k: int = DEFAULT_K
    notes: list[str] = field(default_factory=list)
    raw_response: str = ""

    @property
    def ok(self) -> bool:
        return self.grounding.ok

    @property
    def refused(self) -> bool:
        return NO_ANSWER.rstrip(".").lower() in self.answer_text.lower()

    def render(self) -> str:
        return f"{self.answer_text}\n\nSources\n-------\n{self.sources_block}"


# --------------------------------------------------------------------------
# Evidence
# --------------------------------------------------------------------------

def fold_hits(
    hits: list[tuple[ChunkRecord, float]],
    doc_passages: dict[str, list[ChunkRecord]],
) -> tuple[
    list[tuple[ChunkRecord, float]],
    dict[str, str],
    dict[str, tuple[str, str, ChunkRecord]],
]:
    """Collapse each document's original and translation hits into one passage.

    The retrieval index holds originals and translations as separate rows — that
    separation is what makes the Part 5 same-query-two-languages test possible,
    and it means an English question routinely retrieves both halves of the same
    record. Shown to the model as two sources they read as two witnesses, which
    is false: they are one passage and its translation.

    So the original is kept as the anchor and its English chunk is folded into it
    as the published translation. An English chunk whose original was not
    retrieved becomes an anchor in its own right, but is looked up in the
    document's originals so it can still show the source text it translates.

    Returns (anchors in retrieval order, **translation MEMBER chunk id** by
    anchor, published English by anchor as (text, alignment ground, the merged
    **SECTION** record)).

    The second and third are about different chunks and that is the whole point
    of C1b: `members` is the English chunk retrieval returned — or, when the
    original was the hit, the section's first chunk — while the record in
    `published` is every member of that section merged. They coincide except
    where a section split into several English chunks and a later one was the
    hit, which is exactly the case `align.py` was rewritten for.
    """
    anchors: list[tuple[ChunkRecord, float]] = []
    seen: set[str] = set()
    members: dict[str, str] = {}
    published: dict[str, tuple[str, str]] = {}

    # Pair each document once, so alignment ground is computed on the whole
    # document rather than on whichever passages happened to be retrieved.
    pairs_by_original: dict[str, tuple[ChunkRecord | None, str]] = {}
    original_by_translation: dict[str, ChunkRecord] = {}
    for doc_id, records in doc_passages.items():
        originals = [r for r in records if r.role == "original"]
        translations = [r for r in records if r.role == "translation"]
        originals.sort(key=lambda r: r.seq)
        translations.sort(key=lambda r: r.seq)
        for pair in pair_chunks(originals, translations):
            translation = pair.translation
            pairs_by_original[pair.original.chunk_id] = (translation, pair.ground)
            # Every member, not just the merged chunk's id: a section split into
            # several English chunks would otherwise surface its later chunks as
            # separate sources repeating what the first one already said.
            for member in (pair.members or ([translation] if translation else [])):
                original_by_translation[member.chunk_id] = pair.original

    for record, similarity in hits:
        if record.role == "translation":
            origin = original_by_translation.get(record.chunk_id)
            if origin is not None and origin.chunk_id in seen:
                members[origin.chunk_id] = record.chunk_id
                continue
            if origin is not None:
                anchors.append((origin, similarity))
                seen.add(origin.chunk_id)
                members[origin.chunk_id] = record.chunk_id
                translation, ground = pairs_by_original.get(origin.chunk_id, (None, "none"))
                if translation is not None:
                    published[origin.chunk_id] = (
                        translation.text, ground, translation
                    )
                continue
            # A translation chunk with no original — a record whose English
            # stands alone. It is its own anchor.
            if record.chunk_id not in seen:
                anchors.append((record, similarity))
                seen.add(record.chunk_id)
            continue

        if record.chunk_id in seen:
            continue
        anchors.append((record, similarity))
        seen.add(record.chunk_id)
        translation, ground = pairs_by_original.get(record.chunk_id, (None, "none"))
        if translation is not None:
            published[record.chunk_id] = (translation.text, ground, translation)
            members[record.chunk_id] = translation.chunk_id

    return anchors, members, published


def build_evidence(
    conn,
    query_vector: list[float],
    *,
    k: int = DEFAULT_K,
    max_sources: int = DEFAULT_MAX_SOURCES,
    langs: list[str] | None = None,
    regions: list[str] | None = None,
    profiles: dict | None = None,
) -> list[Passage]:
    hits = answer_store.search_passages(
        conn, query_vector, k=k, langs=langs, regions=regions
    )
    if not hits:
        return []

    doc_ids = list(dict.fromkeys(record.doc_id for record, _ in hits))
    doc_passages = answer_store.fetch_doc_passages(conn, doc_ids)
    anchors, members, published = fold_hits(hits, doc_passages)
    anchors = anchors[:max_sources]

    machine = answer_store.fetch_current_translations(
        conn, [record.chunk_id for record, _ in anchors]
    )

    english_by_chunk: dict[str, EnglishChoice] = {}
    translation_sections: dict[str, ChunkRecord] = {
        chunk_id: entry[2] for chunk_id, entry in published.items()
    }
    for record, _ in anchors:
        published_text, ground, _record = published.get(
            record.chunk_id, (None, None, None)
        )
        english_by_chunk[record.chunk_id] = resolve_english(
            record,
            published_text=published_text,
            published_ground=ground,
            published_attribution=record.translation_source,
            machine=machine.get(record.chunk_id),
            profiles=profiles,
        )

    return build_passages(
        anchors,
        english_by_chunk=english_by_chunk,
        max_sources=max_sources,
        translation_member_by_chunk=members,
        translation_section_by_chunk=translation_sections,
    )


# --------------------------------------------------------------------------
# The call
# --------------------------------------------------------------------------

def build_messages(question: str, evidence_block: str,
                   prompt_version: str | None = None) -> list[dict]:
    return [
        {"role": "system", "content": system_prompt(prompt_version)},
        {
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                f"Sources:\n\n{evidence_block}\n\n"
                f"Answer the question using only the sources above, citing every "
                f"factual sentence."
            ),
        },
    ]


def assemble(
    question: str,
    passages: list[Passage],
    *,
    model: str = DEFAULT_MODEL,
    model_label: str | None = None,
    profiles: dict | None = None,
    client=None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    sleep=time.sleep,
    prompt_version: str | None = None,
) -> AssembledAnswer:
    """One chat call, then verification. Never raises on a bad answer — an
    ungrounded answer is a result, and suppressing it would hide the failure that
    Part 8 needs to count."""
    notes: list[str] = []
    version = prompt_version or ANSWER_PROMPT_VERSION
    system_prompt(version)          # raise now, not after spending a chat call

    if not passages:
        return AssembledAnswer(
            question=question,
            answer_text=NO_ANSWER,
            passages=[],
            grounding=cite.verify(NO_ANSWER, [], ""),
            sources_block="",
            model=model_label or model,
            prompt_version=version,
            notes=["retrieval returned nothing; no chat call was made"],
        )

    evidence_block = cite.render_evidence(passages, profiles)
    # `_chat` returns THREE values: (text, retries, temperature_actually_used).
    # This call site unpacked two from bff0605 (ruling 22's temperature work,
    # which updated translate.py's three callers and missed this one) until
    # 2026-08-21, and every live answer call raised ValueError for those five
    # days. Nothing caught it because the answer suites were not run across
    # Block C, and no archived run is affected: the newest predates bff0605.
    #
    # The third value is CAPTURED and not discarded into `_`. Ruling 22 says
    # temperature is classified, recorded and opt-in, never dropped. This path
    # passes no temperature and no fallback, so the value is 0.0 today - which
    # is exactly why it is worth reading. It is a constant until someone changes
    # it, and a silent `_` is how that change would arrive unannounced.
    raw, retries, temperature_used = _chat(
        build_messages(question, evidence_block, version),
        model=model, client=client, max_tokens=max_tokens, sleep=sleep,
    )
    if retries:
        notes.append(f"{retries} retry/retries before the answer came back")
    if temperature_used != 0:
        notes.append(
            f"temperature {temperature_used} was used, not 0 - this answer is "
            f"NOT comparable with the greedy archive it will be filed beside"
        )

    answer_text = _strip_preamble(raw or "")
    if not answer_text.strip():
        notes.append("the model returned an empty answer")

    # Verified against the sources block that will actually be shown, so the
    # "no unlabelled machine translation" rule is checked on the artifact.
    provisional = cite.verify(answer_text, passages, None)
    sources_block = cite.render_sources(passages, provisional, profiles)
    grounding = cite.verify(answer_text, passages, sources_block)

    return AssembledAnswer(
        question=question,
        answer_text=answer_text,
        passages=passages,
        grounding=grounding,
        sources_block=sources_block,
        model=model_label or model,
        prompt_version=version,
        notes=notes,
        raw_response=raw or "",
    )


_PREAMBLE_RE = re.compile(
    r"^\s*(here(?:'s| is)[^\n:]{0,80}:|answer:|based on the sources[^\n:]{0,40}:)\s*",
    re.I,
)


def _strip_preamble(raw: str) -> str:
    """Same reasoning as parse_translation in Part 6: a preamble is not an
    answer, and keeping it would count as an uncited sentence and fail an answer
    for the model's manners rather than for its grounding."""
    return _PREAMBLE_RE.sub("", raw.strip()).strip()


# --------------------------------------------------------------------------
# Persistence
# --------------------------------------------------------------------------

def citation_rows(answer: AssembledAnswer) -> list[dict]:
    cited = set(answer.grounding.cited_markers)
    quoted = {span.marker for span in answer.grounding.quote_spans}
    rows: list[dict] = []
    for passage in answer.passages:
        english = passage.english
        rows.append(
            {
                "marker": passage.marker,
                "chunk_id": passage.chunk_id,
                "doc_id": passage.doc_id,
                "similarity": passage.similarity,
                "english_kind": english.kind,
                "english_ground": english.ground,
                "confidence_band": english.band,
                "confidence_profile": english.profile,
                "flags": list(english.flags),
                "cited": passage.marker in cited,
                "quoted": passage.marker in quoted,
                "source_field": passage.chunk.source_field,
                "char_start": passage.chunk.char_start,
                "char_end": passage.chunk.char_end,
            }
        )
    return rows


def store(conn, answer: AssembledAnswer, question_lang: str | None = None) -> str:
    chunk_ids = [p.chunk_id for p in answer.passages]
    aid = answer_store.answer_id(
        answer.question, answer.model, answer.prompt_version, chunk_ids
    )
    answer_store.write_answer(
        conn,
        {
            "answer_id": aid,
            "question": answer.question,
            "question_lang": question_lang,
            "answer_text": answer.answer_text,
            "answer_model": answer.model,
            "answer_prompt_version": answer.prompt_version,
            "embedding_model": answer.embedding_model,
            "retrieval_k": answer.retrieval_k,
            "grounded": answer.grounding.ok,
            "grounding": answer.grounding.to_dict(),
            "notes": " | ".join(answer.notes) or None,
        },
        citation_rows(answer),
    )
    return aid


__all__ = [
    "ANSWER_PROMPT_VERSION",
    "AssembledAnswer",
    "NO_ANSWER",
    "SYSTEM_ANSWER",
    "assemble",
    "build_evidence",
    "build_messages",
    "citation_rows",
    "fold_hits",
    "store",
    "TranslationError",
]
