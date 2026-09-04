"""Text-fidelity classification.

The seed corpus is honest about its own imperfections: some records store a
paraphrase or an English rendering in the `original_text_excerpt` field rather
than the source's own words. If those are embedded and retrieved as if they
were primary text, the Part 5 cross-lingual test silently measures nothing, and
Part 7's citations point at wording no source ever contained.

So every chunk is classified and, where it isn't genuine source text, marked
ineligible for retrieval. Nothing is discarded — it stays queryable and can be
promoted once the verbatim text is pulled from the critical editions.
"""

from __future__ import annotations

import re
import unicodedata

# ---------------------------------------------------------------------------
# Manual overrides
# ---------------------------------------------------------------------------
# Called out in data/seed_corpus/manifest.json under
# `follow_up_before_ingestion`: their original_text_excerpt is paraphrased or
# partial rather than a verbatim transliteration. Fixing them is a separate
# source-research pass; until then they are flagged, not trusted.
#
# THIS LIST MARKS SUSPICION. Nothing in the pipeline ever turned suspicion into
# a determination, and on 2026-08-22 two of its entries were checked against
# their sources for the first time and came back opposite ways: eastasia-01-weilue
# was INVENTED (0 of 3 fragments present in the Sanguozhi text) and
# eastasia-02-hou-hanshu is GENUINE (34 of 36 characters identical, one
# traditional/simplified pair and one variant character for the same word). The
# flag never distinguished them. FINDING 11.
#
# eastasia-01-weilue was REMOVED from this list on 2026-08-22 because its
# original_text_excerpt is now 221 verbatim characters from zh.wikisource
# 三國志/卷30 and classifies as verbatim_original on its own merits. Leaving it
# here would have the corpus report a sourced text as paraphrased.
PARAPHRASED_ORIGINALS: dict[str, str] = {
    "arabia-02-palmyrene-tariff": "manifest: paraphrased, not verbatim CIS II 3913 text",
    "eastasia-02-hou-hanshu": "manifest: paraphrased, not verbatim 後漢書 text — but VERIFIED genuine 2026-08-22, see original_text_note; the flag is now stale in the other direction",
    "southasia-03-akananuru": "manifest: paraphrased, not verbatim Akanāṉūṟu 149 text",
    "subsaharan-01-ezana-stone": "manifest: paraphrased, not verbatim Ezana Stone text",
}

# Matched against document ids loosely, because ids in the corpus vary in shape.
PARAPHRASE_ID_HINTS = (
    "palmyrene-tariff",
    # "weilue" removed 2026-08-22: the record now holds verbatim Sanguozhi text.
    "hou-hanshu",
    "akananuru",
    "ezana-stone",
)

# ---------------------------------------------------------------------------
# Script detection
# ---------------------------------------------------------------------------
# Unicode block prefixes for the non-Latin scripts this corpus actually uses.
NON_LATIN_SCRIPTS = (
    "GREEK",
    "CJK",
    "HANGUL",
    "ARABIC",
    "TAMIL",
    "ETHIOPIC",
    "RUNIC",
    "DEVANAGARI",
    "SYRIAC",
    "HEBREW",
    "OLD SOUTH ARABIAN",
    "OLD NORTH ARABIAN",
    "IMPERIAL ARAMAIC",
    "INSCRIPTIONAL PARTHIAN",
    "INSCRIPTIONAL PAHLAVI",
    "PSALTER PAHLAVI",
    "CUNEIFORM",
    "BRAHMI",
    "KHAROSHTHI",
    "COPTIC",
    "HIRAGANA",
    "KATAKANA",
)

LATIN_SCRIPT_LANGS = {"en", "la", "da", "de", "fr", "it", "sv", "no"}

# Frequent English function words. A high ratio of these in a Latin-script
# passage means we're looking at English prose, not a romanised original.
ENGLISH_MARKERS = {
    "the", "of", "and", "to", "in", "a", "is", "was", "were", "that", "this",
    "for", "with", "from", "by", "as", "on", "at", "which", "their", "they",
    "we", "our", "his", "her", "it", "are", "be", "been", "has", "have", "had",
    "who", "whom", "not", "but", "or", "an", "into", "than", "then", "there",
}

_WORD_RE = re.compile(r"[A-Za-z']+")

# Source types where the record describes an object rather than carrying text.
FIND_TYPES = {"find_record", "coin_record", "object_record", "artefact_record"}

# Phrases that mean "the real text lives somewhere else" rather than being text.
_POINTER_PATTERNS = (
    re.compile(r"available at the citation", re.I),
    re.compile(r"see the citation", re.I),
    re.compile(r"\bat the citation URL\b", re.I),
    re.compile(r"\bhosted separately\b", re.I),
    re.compile(r"full (english )?(translation|text)[^.]{0,60}\bavailable\b", re.I),
    re.compile(r"\bsee\b[^.]{0,40}\bfor the full\b", re.I),
)

# Editorial placeholders: a bracketed note standing in for text that was never
# transcribed. Six records in the seed corpus are of this shape, e.g.
#   "[Greek text of §53-54 ... — pull full section from the Greek Wikisource]"
# Embedding these would put the corpus editor's own prose into the retrieval
# index and let Part 7 cite it as if it were a primary source.
_PLACEHOLDER_CUES = (
    re.compile(r"\bnot transcribed\b", re.I),
    re.compile(r"\bpull (verbatim |the full |full )?(text |section )?from\b", re.I),
    re.compile(r"\bnot reproduced\b", re.I),
    re.compile(r"\bsee\b[^\]]{0,80}\b(wikisource|papyri\.info|encyclopaedia|wikipedia)\b", re.I),
    re.compile(r"\bfull critical transcription\b", re.I),
    re.compile(r"\btext spans\b", re.I),
)

# Marks an excerpt that is genuine source wording but elided or partial.
_ELISION_RE = re.compile(r"(\.\.\.|…|\[\.{3}\]|\blines? \d+[-–]\d+\b)")

# Diacritics used in scholarly romanisation of Semitic, Iranian, Indic and
# runic material. Their presence in quantity means the field contains an actual
# transliteration, even if it is wrapped in an editorial bracket — as in
# arabia-03-jsnab17, "[Nabataean script, transliterated: dnh qbrʾ dy ʿbd ...]".
_TRANSLIT_MARKS = set("ʾʿḥṣṭḍẓġḫšṯḏṛṇṉṟḷḻāīūēōṃṅñśẖḳǧčžəḤṢṬḌẒĠḪŠṮḎṚṆŚṀṞṺ¹²³")
_TRANSLIT_MIN_MARKS = 3


def translit_mark_count(text: str) -> int:
    return sum(1 for ch in text if ch in _TRANSLIT_MARKS)


def has_transliteration(text: str) -> bool:
    return translit_mark_count(text) >= _TRANSLIT_MIN_MARKS


def looks_like_placeholder(text: str) -> bool:
    """True if the field is an editorial note about text, not the text itself."""
    stripped = text.strip()
    # A field carrying a real transliteration is content, whatever else it says.
    if has_transliteration(stripped) or non_latin_ratio(stripped) >= 0.30:
        return False
    bracketed = stripped.startswith("[")
    cues = sum(1 for p in _PLACEHOLDER_CUES if p.search(stripped))
    # A bracketed opening plus one cue, or two cues on their own, is decisive.
    return (bracketed and cues >= 1) or cues >= 2


def non_latin_ratio(text: str) -> float:
    """Fraction of alphabetic characters that belong to a non-Latin script."""
    alpha = [c for c in text if c.isalpha()]
    if not alpha:
        return 0.0
    hits = 0
    for ch in alpha:
        try:
            name = unicodedata.name(ch)
        except ValueError:
            continue
        if name.startswith(NON_LATIN_SCRIPTS):
            hits += 1
    return hits / len(alpha)


def english_marker_ratio(text: str) -> float:
    """Fraction of Latin-script words that are common English function words."""
    words = [w.lower() for w in _WORD_RE.findall(text)]
    if len(words) < 8:
        return 0.0
    return sum(1 for w in words if w in ENGLISH_MARKERS) / len(words)


def looks_like_pointer(text: str) -> bool:
    """True if the field describes where text lives rather than containing it."""
    return any(p.search(text) for p in _POINTER_PATTERNS)


def is_flagged_paraphrase(doc_id: str) -> bool:
    if doc_id in PARAPHRASED_ORIGINALS:
        return True
    lowered = doc_id.lower()
    return any(hint in lowered for hint in PARAPHRASE_ID_HINTS)


def classify_original(
    text: str,
    doc_id: str,
    declared_langs: list[str],
    source_type: str,
) -> tuple[str, str, bool]:
    """Classify an `original_text_excerpt`.

    Returns (text_fidelity, actual_lang, eligible_for_retrieval).
    """
    primary = (declared_langs[0] if declared_langs else "und").lower()
    nl = non_latin_ratio(text)

    # 1. Editorial placeholders and cross-references are not source text.
    if looks_like_placeholder(text) or looks_like_pointer(text):
        return "pointer", "en", False

    # 2. Find and coin records describe an object. Their "original text" field is
    #    a catalogue description — legitimately useful for retrieval, but it must
    #    never be mistaken for the wording of a primary text.
    if source_type in FIND_TYPES:
        lang = primary if (nl >= 0.30 and primary not in LATIN_SCRIPT_LANGS) else "en"
        return "object_description", lang, True

    # 3. Original-script text present: the source's own characters.
    if nl >= 0.30:
        if is_flagged_paraphrase(doc_id) or _ELISION_RE.search(text):
            # The manifest flags these as "paraphrased or partial".
            #
            # THIS COMMENT USED TO SAY "the wording is the source's own — it is
            # abridged, not invented". That was an assumption, and on 2026-08-22
            # it was disproved on the first record anyone checked:
            # eastasia-01-weilue's 52 characters occurred nowhere in the Weilue.
            # Not abridged. Invented. This branch cannot tell the difference —
            # it sees non-Latin script and a flag, and neither is evidence about
            # wording. FINDING 11.
            #
            # Still retrieval-eligible, and the reason is unchanged and still
            # good: excluding flagged records would remove every Chinese text
            # from the corpus and leave the Part 5 cross-lingual test with
            # nothing for East Asia. But `partial_verbatim` means "flagged and
            # unchecked", not "abridged", and the only thing that resolves it is
            # someone reading the source.
            return "partial_verbatim", primary, True
        return "verbatim_original", primary, True

    # 4. Latin script from here down.
    if primary in LATIN_SCRIPT_LANGS:
        return "verbatim_original", primary, True

    if is_flagged_paraphrase(doc_id):
        return "paraphrase", "en", False

    # Declared as a non-Latin-script language but stored in Latin characters:
    # either a romanised transliteration or an English stand-in.
    if english_marker_ratio(text) >= 0.18:
        return "english_rendering", "en", False
    return "transliteration", primary, True


def classify_translation(text: str, source_type: str) -> tuple[str, str, bool]:
    """Classify a `reference_translation`. Returns (fidelity, lang, eligible)."""
    if looks_like_pointer(text) or looks_like_placeholder(text):
        return "pointer", "en", False
    if source_type in FIND_TYPES:
        # For find records this field is a curatorial description, not a
        # translation. Still useful for retrieval; labelled honestly.
        return "object_description", "en", True
    return "translation", "en", True


# ---------------------------------------------------------------------------
# Record tiers (F1, 2026-08-29)
# ---------------------------------------------------------------------------
# The classifier above answers a question about a CHUNK: is this field the
# source's own wording, and may it be retrieved? A tier answers a question
# about a RECORD: what kind of evidence is this, and what did curating it cost?
# F1 needs the second question because PHASE2_PLAN sets a target mix over the
# 36 new records, and a mix can only be set over something that is counted.
#
# PHASE2_PLAN wrote three tiers. The corpus on disk has five states and the
# pipeline already distinguishes them:
#
#   verbatim_with_provenance      11 records
#   verbatim_machine_english       0 records   <- the tier F3-F7 predicts
#   published_translation_only     1 record    africa-01-ezana-stone
#   catalogue_record              11 records
#   pointer_only                   1 record    arabia-02-palmyrene-tariff
#
# `verbatim_machine_english` is the one worth the amendment. F3-F7 says in
# terms: "Local non-English sources mostly will not have published English, so
# `resolve_english` starts choosing `machine` and the Part 6 confidence
# machinery goes from dormant to load-bearing." A record with original text and
# no published translation is not verbatim_with_provenance -- there is no
# published translation to cite -- and it is not published_translation_only,
# because there IS an original. The tier the tranche is predicted to fill had
# no name, and a mix cannot have a target for a tier that cannot be written
# down. `pointer_only` is the smaller half of the same defect: the Palmyrene
# Tariff has been in this corpus since Part 3 and none of the three tiers held
# it.
#
# This is ruling 38 one level over. floor.json spent two days asserting the
# opposite of what it had measured because no state fitted, and the answer was
# a third state rather than a better argument about the two.
#
# WHAT A TIER IS DELIBERATELY NOT. It is not a fact about the aligner.
# `answer.align.Pair.ground` is section | index | document | none, and an
# unalignable published translation lands a reader on `published_document`
# rather than `published`. That is a real distinction and it is reported beside
# the tier, never inside it: a tier that moved when align.py changed would stop
# being a property of the record, and the whole point of counting records is
# that the count means the same thing in F3 as it does in F7.

RECORD_TIERS = (
    "verbatim_with_provenance",
    "verbatim_machine_english",
    "published_translation_only",
    "catalogue_record",
    "pointer_only",
)

# Not a tier. Returned when no tier holds the record, and REFUSED as a
# declaration -- ruling 36's shape, where an arm that cannot be identified
# blocks rather than being read as the default. A record nobody can tier is a
# record somebody has to look at, and a sixth tier invented at curation time to
# hold it is a tier chosen to fit one record.
UNCLASSIFIABLE = "unclassifiable"

# The original-role fidelities that mean "the source's own characters are
# here". `partial_verbatim` is included and that is not an oversight: it means
# "flagged and unchecked", not "not there", and three of the eleven verbatim
# records (hou-hanshu, akananuru, muziris-papyrus) carry it. `transliteration`
# is included for the same reason and covers four more (jsnab17, jabal-dabub,
# skz, vimose). Excluding either would tier seven of eleven records as though
# they held no source text at all.
ELIGIBLE_ORIGINAL_FIDELITIES = frozenset(
    {"verbatim_original", "partial_verbatim", "transliteration"}
)


def derive_record_tier(
    source_type: str,
    chunk_rows: "list[tuple[str, str, str, bool]]",
    translation_source: str | None = None,
) -> tuple[str, str]:
    """Derive one record's tier from its chunks. Returns (tier, reason).

    `chunk_rows` is (role, text_fidelity, lang, eligible_for_retrieval) per
    chunk -- plain tuples rather than Chunk objects, so this module keeps its
    one useful property: it imports nothing from the package and can be tested
    without a corpus, a database or a network.

    The reason travels with the tier and is printed by `ingest.verify`, because
    a derivation that says only what it concluded is a derivation nobody can
    argue with when it is wrong.
    """
    rows = [(str(r), str(f), str(lang), bool(e)) for r, f, lang, e in chunk_rows]
    if not rows:
        return UNCLASSIFIABLE, "the record produced no chunks at all"

    # 1. A find record first, and unconditionally. `classify_original` already
    #    forces `object_description` on these whatever the field contains, so a
    #    Korean object description is still a catalogue description and not
    #    Korean source text. Testing anything else first would let the shape of
    #    a catalogue entry decide the tier.
    if source_type in FIND_TYPES:
        return "catalogue_record", (
            f"source_type {source_type!r} is a find/coin/object record, so both "
            f"text fields are catalogue description whatever they contain"
        )

    eligible = [r for r in rows if r[3]]
    if not eligible:
        return "pointer_only", (
            "no chunk in either role is retrieval-eligible: the record says "
            "where its text lives rather than carrying it"
        )

    source_language = [
        r for r in eligible
        if r[0] == "original"
        and r[1] in ELIGIBLE_ORIGINAL_FIDELITIES
        and r[2] != "en"
    ]
    published = [r for r in eligible if r[0] == "translation" and r[1] == "translation"]

    if source_language:
        langs = sorted({r[2] for r in source_language})
        if not published:
            return "verbatim_machine_english", (
                f"retrieval-eligible source-language text in {langs} and no "
                f"published translation, so `resolve_english` reaches this "
                f"passage with `machine` or with nothing"
            )
        if not (translation_source or "").strip():
            return UNCLASSIFIABLE, (
                f"source-language text in {langs} and a translation chunk, but "
                f"`translation_source` is empty. 'both cited' is the clause that "
                f"makes this tier verbatim_with_provenance rather than a claim, "
                f"and an unattributed translation is a curation defect and not a "
                f"sixth tier"
            )
        return "verbatim_with_provenance", (
            f"retrieval-eligible source-language text in {langs}, a published "
            f"translation, and both cited"
        )

    english_original = [
        r for r in eligible
        if r[0] == "original"
        and r[1] in ELIGIBLE_ORIGINAL_FIDELITIES
        and r[2] == "en"
    ]
    if english_original:
        return UNCLASSIFIABLE, (
            "the original_text_excerpt classifies as retrieval-eligible ENGLISH "
            "source text on a record that is not a find record. No tier holds "
            "it: there is no source-language text to be verbatim about, and "
            "calling it published_translation_only would assert that no original "
            "transcription is available when the field on disk IS the original"
        )

    if published:
        return "published_translation_only", (
            "no retrieval-eligible source-language text, and a published "
            "translation that is cited"
        )

    return UNCLASSIFIABLE, (
        "a retrieval-eligible chunk exists but it is neither source-language "
        f"original nor published translation: {sorted({(r[0], r[1]) for r in eligible})}"
    )


def check_declared_tiers(
    declared: "dict[str, str]",
    derived: "dict[str, tuple[str, str]]",
) -> "list[str]":
    """Compare a declared tier map against the derived one. Returns problems.

    Three failures and they are three different defects, which is why they are
    not one message:

      * a record with no declared tier -- the curator added a record and did not
        tier it, and a tier that is optional is a tier that gets forgotten;
      * a declaration naming a record that is not in the corpus -- the sidecar
        has drifted, and a stale entry silently makes the count wrong in the
        direction nobody checks;
      * declared != derived -- the curator believes the record is one kind of
        evidence and the classifier reads it as another. That one is the whole
        reason a DECLARATION exists beside a derivation. A tier that is only
        derived cannot be wrong, and cannot be checked either.

    Both drift directions are named on purpose. `calibration_scope`'s
    `a_named_sweep_must_actually_fail_the_rule` is the same argument in
    floor.json: a list that is only checked in one direction becomes a place to
    put things.
    """
    problems: list[str] = []

    for doc_id in sorted(set(derived) - set(declared)):
        problems.append(
            f"{doc_id}: no declared tier. Derived {derived[doc_id][0]!r} -- "
            f"{derived[doc_id][1]}"
        )

    for doc_id in sorted(set(declared) - set(derived)):
        problems.append(
            f"{doc_id}: declared tier {declared[doc_id]!r} names a record that "
            f"is not in the corpus"
        )

    for doc_id in sorted(set(declared) & set(derived)):
        want = declared[doc_id]
        got, reason = derived[doc_id]
        if want == UNCLASSIFIABLE:
            problems.append(
                f"{doc_id}: {UNCLASSIFIABLE!r} is not a declarable tier. It is "
                f"what the derivation returns when no tier holds a record"
            )
            continue
        if want not in RECORD_TIERS:
            problems.append(
                f"{doc_id}: declared tier {want!r} is not one of {RECORD_TIERS}"
            )
            continue
        if want != got:
            problems.append(
                f"{doc_id}: declared {want!r}, derived {got!r} -- {reason}"
            )

    return problems


# The tiers that can carry a `refusable_with_gloss` case. Held here rather than
# only in data/corpus_tiers.json because it is a rule and not a number: a gloss
# case requires the answer to quote a PUBLISHED hedged reading, and on
# verbatim_machine_english the only English is machine. Quoting a machine
# translation of a disputed reading, attached to a citation, is the exact output
# the gloss arm exists to catch, so a gloss case on that tier would be testing
# for the defect by requiring it.
GLOSS_CAPABLE_TIERS = frozenset(
    {"verbatim_with_provenance", "published_translation_only", "catalogue_record"}
)

# Ruling 56, F4, 2026-08-31. The tiers on which an `expect_quoted_from_original`
# case asks WHICH CHUNK was quoted, rather than WHETHER anything resolved.
#
# The assertion is built from resolved quote spans whose `source_field` is
# `original_text_excerpt`. That is a CHOICE only where a second retrieval-
# eligible chunk is competing for the quotation, and exactly one tier holds
# both an original and its published English: `verbatim_with_provenance`.
# `published_translation_only` has no original to prefer, `catalogue_record` has
# neither, and on `verbatim_machine_english` the only English lives in
# `current_translations`, which is not a corpus field, so a quotation of it
# cannot resolve to characters on disk at all and the assertion is satisfied by
# any resolved quotation whatsoever.
#
# FINDING 40 measured the difference the name hides: across 16 archived runs of
# chinese-da-qin, 45 of 45 resolved quotations came from the English while the
# source chunk sat at [S1]. That is the defect the assertion was invented to
# see, and it is unobservable on a record with one chunk.
#
# Held in code beside GLOSS_CAPABLE_TIERS, and for its reason: it is a rule and
# not a number, and a mutation has to be able to break it.
QUOTATION_CHOICE_TIERS = frozenset({"verbatim_with_provenance"})

# Ruling 62's owed distinction, F5. A `refusable_with_gloss` case can sit on two
# quite different things and the definition could not tell them apart:
#
#   contested_reading        the SOURCE TEXT is disputed -- undeciphered runes, a
#                            corrupt legend, two scholarly readings of one
#                            epitaph. This is what the gloss arm was built to
#                            see: whether a model renders a disputed text
#                            confidently.
#   hedged_identification    the source text is not in doubt and the TRANSLATOR
#                            is unsure what it refers to. Hirth's
#                            "Fu-nan [Siam, Cambodja?]" on record 35.
#
# Mechanically both satisfy what_gloss_capable_MEANS_mechanically -- a hedged
# reading and a statement that the reading is uncertain, inside a retrieval-
# eligible chunk -- and there is no reading of that sentence on which either
# does not. Ruling 62 therefore had to carry the distinction in three separate
# places of PROSE, and its own closing sentence was that the count is the only
# thing anyone reads.
#
# Held in code beside GLOSS_CAPABLE_TIERS and QUOTATION_CHOICE_TIERS, for their
# stated reason: it is a rule and not a number, and a mutation has to be able to
# break it. Each member must also carry a written definition in
# `what_the_two_gloss_KINDS_are` -- check_target_mix refuses one that does not,
# on ingest.cost's precedent that a phase with no written definition is refused.
GLOSS_KINDS = frozenset({"contested_reading", "hedged_identification"})

REGION_COUNT = 7


def check_target_mix(
    mix: "dict", measured_at_24: "dict[str, int]"
) -> "list[str]":
    """Is the declared target mix internally coherent? Returns problems.

    The mix is data and this is the rule it has to satisfy. Kept in code so a
    mutation can break it: a target mix that does not add up is a target nobody
    can miss, and the arithmetic is exactly the kind of thing that stays wrong
    for five sessions because every individual number looks reasonable.
    """
    problems: list[str] = []

    new = mix.get("by_tier_new") or {}
    at60 = mix.get("by_tier_at_60") or {}
    by_region = mix.get("records_by_region_target_at_60") or {}

    unknown = sorted(set(new) - set(RECORD_TIERS))
    if unknown:
        problems.append(f"by_tier_new names tiers outside the vocabulary: {unknown}")

    want_new = mix.get("new_records")
    if sum(new.values()) != want_new:
        problems.append(
            f"by_tier_new sums to {sum(new.values())}, not the {want_new} records "
            f"Block F adds"
        )

    want_total = mix.get("total_at_60")
    if sum(by_region.values()) != want_total:
        problems.append(
            f"records_by_region_target_at_60 sums to {sum(by_region.values())}, "
            f"not {want_total}"
        )
    if len(by_region) != REGION_COUNT:
        problems.append(
            f"records_by_region_target_at_60 covers {len(by_region)} regions, not "
            f"{REGION_COUNT}. A region with no target is a region the mix cannot "
            f"be missed in"
        )

    for tier in sorted(set(new) | set(at60)):
        expect = measured_at_24.get(tier, 0) + new.get(tier, 0)
        if at60.get(tier) != expect:
            problems.append(
                f"by_tier_at_60[{tier}] is {at60.get(tier)!r}; measured_at_24 "
                f"{measured_at_24.get(tier, 0)} plus by_tier_new {new.get(tier, 0)} "
                f"is {expect}"
            )

    if new.get("pointer_only", 0) != 0:
        problems.append(
            "by_tier_new allows a new pointer_only record. The ceiling is zero: a "
            "record whose text lives somewhere else grows the record count without "
            "growing the corpus"
        )

    # The per-region minimum has to be reachable from the aggregate, or it is a
    # target that fails in F7 for a reason set in F1.
    per_region = mix.get("min_source_language_records_per_region") or 0
    source_language_at_60 = sum(
        at60.get(t, 0) for t in ("verbatim_with_provenance", "verbatim_machine_english")
    )
    if per_region * REGION_COUNT > source_language_at_60:
        problems.append(
            f"min_source_language_records_per_region {per_region} x {REGION_COUNT} "
            f"regions needs {per_region * REGION_COUNT} source-language records, and "
            f"the tier targets provide {source_language_at_60}"
        )

    gloss_tiers = set(mix.get("which_tiers_can_carry_a_gloss_case") or ())
    if not gloss_tiers or not gloss_tiers <= GLOSS_CAPABLE_TIERS:
        problems.append(
            f"which_tiers_can_carry_a_gloss_case is {sorted(gloss_tiers)}; a gloss "
            f"case may only sit on {sorted(GLOSS_CAPABLE_TIERS)}"
        )

    kinds_doc = mix.get("what_the_two_gloss_KINDS_are") or {}
    undefined = sorted(k for k in GLOSS_KINDS
                       if not str(kinds_doc.get(k) or "").strip())
    if undefined:
        problems.append(
            f"gloss kind(s) {undefined} carry no written definition in "
            f"what_the_two_gloss_KINDS_are. A kind the code accepts and the file "
            f"does not explain is a distinction nobody agreed to"
        )

    gloss = mix.get("gloss_capable_records") or 0
    if not 0 < gloss <= (want_new or 0):
        problems.append(
            f"gloss_capable_records is {gloss}, which is not a quota over the "
            f"{want_new} new records"
        )

    return problems


# The tiers that carry retrieval-eligible source-language text, and therefore
# the ones the per-region floor is counted over. Named here rather than written
# out at each use, because it is the same pair in check_target_mix's
# reachability arithmetic and in check_allocation's per-region one, and a pair
# that is spelled out twice is a pair that disagrees once.
SOURCE_LANGUAGE_TIERS = ("verbatim_with_provenance", "verbatim_machine_english")


# Ruling 58 owed a per-region language rule to F5. FINDING 62 changed its shape
# before it could be written, and the change matters more than the rule.
#
# Ruling 58 read Sub-Saharan Africa's floor as MET IN GREEK and defended
# africa-04-silko-talmis and africa-05-adulis-throne as Africans using the
# empire's language to say something about themselves -- "a sharper statement
# about influence than a local language would have made". That defence is right
# and this does not disturb it.
#
# What it did not see is the third record beside them. FOUR of the corpus's
# twenty-two source-language records are Greek with NO FINDSPOT AT ALL, and
# three of those four are THE SAME TEXT: the Periplus of the Erythraean Sea
# supplies one source-language record to Arabia, one to South Asia and one to
# Sub-Saharan Africa, from one edition, one page and one citation_original. The
# floor counts RECORDS, and the Periplus is one text wearing three.
#
# So the rule ruling 58 proposed -- refuse a floor met entirely in Greek or
# Latin -- gets exactly the wrong records. It cannot tell Silko from the
# Periplus, because both are `grc`: it would refuse the two records ruling 58
# argued hardest to keep and admit the one it should refuse. The distinction
# that does the work is not the LANGUAGE of the text but whether the region is
# SPEAKING or being SPOKEN ABOUT, and the corpus already holds it, in `findspot`
# and in W1's findspot_places / subject_places split. The tier layer read
# neither field.
#
# COUNTED, NOT GATED -- and the REASON changed four hours after it was written,
# which is why the old one is kept here rather than replaced. It read:
#
#   "Sub-Saharan Africa has ZERO source-language records in a language of the
#    region and no source-language slot left in any sub-tranche, so a gate would
#    fail the tree on a condition no allocation Block F still has can satisfy."
#
# RULING 73 GAVE THE REGION THAT SLOT. The second half of that sentence stopped
# being true in the same commit as the ruling that made it false, which is the
# defect this block keeps finding: a rule's stated reason outliving the reason.
#
# It stays counted for a better reason. The gate now EXISTS and it is narrower
# than a per-region floor: `requires_provenance` sits on the one slot created to
# meet it, check_delivery enforces it, and it fails only when that cell is full
# with no local-language record in it. A blanket minimum would still be a claim
# about six other regions nobody has evidence for. Ruling 56's shape either way
# -- the teeth are the presence of the number and the fact that it is printed,
# and now, on one slot, a requirement that can actually close.
EMPIRE_LANGUAGES = frozenset({"grc", "lat"})

SOURCE_LANGUAGE_PROVENANCE = (
    "local_language",
    "empire_language_from_the_region",
    "empire_language_about_the_region",
)


def source_language_provenance(language_codes, findspot) -> str:
    """Is the region SPEAKING in this record, or being SPOKEN ABOUT?

    ANY language outside EMPIRE_LANGUAGES makes a record local. persia-01-skz is
    Parthian, Middle Persian AND Greek, and a trilingual a Persian king cut is
    not a Roman text because one of its three columns is Greek.

    An EMPTY language list is not read as local. The flattering direction is the
    one a missing field must never take -- `a_named_sweep_must_actually_fail_the_rule`
    one file over -- and ingest.verify reports any source-language record that
    has no language code rather than letting this function absorb it.
    """
    codes = {str(c).strip().lower() for c in (language_codes or []) if str(c).strip()}
    if codes and not codes <= EMPIRE_LANGUAGES:
        return "local_language"
    if str(findspot or "").strip():
        return "empire_language_from_the_region"
    return "empire_language_about_the_region"


def check_allocation(
    mix: "dict", records_by_region_at_24: "dict[str, int]",
    source_language_by_region_at_24: "dict[str, int]",
) -> "list[str]":
    """Does the sub-tranche allocation deliver the declared mix? Problems.

    Ruling 51, F3, 2026-08-31. Ruling 44 declared the mix AT 60 and said
    nothing about which sub-tranche carries what. Curated by convenience, F7
    inherits every unmet constraint at once, and every aggregate tier target in
    corpus_tiers.json is satisfiable inside Arabia and South Asia alone - which
    is the failure the per-region floor already exists to catch, one level up.

    The allocation is a table of SLOTS, each a (region, tier, n). Nothing here
    is a count declared beside a list: the counts ARE the list, summed, which
    is F1's own correction and the reason two suite counts and a harness count
    drifted in two days. A sub-tranche's `records` is not a field.

    The ordering rule is the one that has teeth. EVERY source-language slot
    precedes EVERY catalogue_record slot, so an allocation that puts the cheap
    tier first - which is what a block short of days will drift toward - is
    refused rather than noticed. A tranche curated cheap-first also reports a
    RISING aggregate cost per record, which is the flattering direction for
    kill trigger 3 and the one nobody would check.
    """
    problems: list[str] = []

    allocation = mix.get("allocation") or {}
    tranches = allocation.get("sub_tranches") or []
    if not tranches:
        return ["target_mix.allocation declares no sub_tranches. The mix at 60 "
                "is then a target with no plan, and F7 inherits every unmet "
                "constraint at once"]

    names = [str(t.get("name") or "") for t in tranches]
    if not all(names) or len(set(names)) != len(names):
        problems.append(
            f"sub_tranche names are {names}; each must be present and distinct"
        )

    new = mix.get("by_tier_new") or {}
    by_region_at_60 = mix.get("records_by_region_target_at_60") or {}

    per_tier: dict[str, int] = {}
    per_region: dict[str, int] = {}
    per_region_source: dict[str, int] = {}
    first_catalogue: int | None = None
    last_source_language: int | None = None
    total = 0

    for index, tranche in enumerate(tranches):
        slots = tranche.get("slots") or []
        if not slots:
            problems.append(f"{names[index] or index}: no slots. A sub-tranche "
                            f"that curates nothing is not one")
        for slot in slots:
            region = str(slot.get("region") or "")
            tier = str(slot.get("tier") or "")
            try:
                n = int(slot.get("n"))
            except (TypeError, ValueError):
                n = -1
            if n < 1:
                problems.append(f"{names[index] or index}: slot "
                                f"{region}/{tier} has n {slot.get('n')!r}")
                continue
            if tier not in RECORD_TIERS:
                problems.append(f"{names[index] or index}: slot names tier "
                                f"{tier!r}, which is outside the vocabulary")
            if region not in by_region_at_60:
                problems.append(f"{names[index] or index}: slot names region "
                                f"{region!r}, which has no target at 60")
            total += n
            per_tier[tier] = per_tier.get(tier, 0) + n
            per_region[region] = per_region.get(region, 0) + n
            if tier in SOURCE_LANGUAGE_TIERS:
                per_region_source[region] = per_region_source.get(region, 0) + n
                last_source_language = index
            if tier == "catalogue_record" and first_catalogue is None:
                first_catalogue = index

    want_new = mix.get("new_records")
    if total != want_new:
        problems.append(
            f"the allocation places {total} record(s); by_tier_new adds "
            f"{want_new}"
        )

    for tier in sorted(set(per_tier) | set(new)):
        if per_tier.get(tier, 0) != new.get(tier, 0):
            problems.append(
                f"the allocation places {per_tier.get(tier, 0)} {tier} "
                f"record(s); by_tier_new declares {new.get(tier, 0)}"
            )

    for region in sorted(set(per_region) | set(by_region_at_60)):
        want = by_region_at_60.get(region, 0) - records_by_region_at_24.get(region, 0)
        if per_region.get(region, 0) != want:
            problems.append(
                f"the allocation places {per_region.get(region, 0)} record(s) "
                f"in {region}; the target at 60 is {by_region_at_60.get(region)} "
                f"against {records_by_region_at_24.get(region, 0)} today, so it "
                f"needs {want}"
            )

    per_region_floor = int(mix.get("min_source_language_records_per_region") or 0)
    for region in sorted(by_region_at_60):
        at_60 = (source_language_by_region_at_24.get(region, 0)
                 + per_region_source.get(region, 0))
        if at_60 < per_region_floor:
            problems.append(
                f"{region} ends the tranche with {at_60} source-language "
                f"record(s) and the floor is {per_region_floor}. An aggregate "
                f"met inside two regions leaves the other five exactly as "
                f"unable to answer a source-text question as they are now"
            )

    # The ordering rule. Equality is allowed - one sub-tranche may hold the
    # last source-language record and the first catalogue record - and anything
    # earlier is the cheap tier jumping the queue.
    if (first_catalogue is not None and last_source_language is not None
            and first_catalogue < last_source_language):
        problems.append(
            f"the first catalogue_record slot is in "
            f"{names[first_catalogue] or first_catalogue} and the last "
            f"source-language slot is in "
            f"{names[last_source_language] or last_source_language}. Every "
            f"source-language record is curated before every catalogue record: "
            f"the cheap tier last, so that a block which runs out of days is "
            f"missing the records this corpus already has eleven of"
        )

    # Ruling 68, F5. This was an EQUALITY, and an equality is a plan with no
    # tolerance for a sub-tranche closing short. Block F has now closed two
    # short -- F3 6 of 8, F4 5 of 7 -- and all four missing records fell in one
    # tier, in the two regions that had no headroom. A plan with no slack
    # against a target is a target that fails on the first miss.
    #
    # Relaxing it costs nothing, because the ceiling is enforced where it can
    # actually be observed: check_delivery refuses more DECLARATIONS than the
    # mix asks for. Under-placing is the failure that can never be recovered,
    # since nobody re-curates a record, and that is the direction still guarded.
    # Ruling 73, F5. A slot may REQUIRE a provenance of the record that fills it.
    # Checked here for coherence and in check_delivery for delivery: a value
    # outside the vocabulary is a requirement nobody can satisfy, and one on a
    # tier with no source-language text is a requirement about a field the
    # record does not have.
    for index, tranche in enumerate(tranches):
        for slot in (tranche.get("slots") or []):
            want = slot.get("requires_provenance")
            if want is None:
                continue
            if want not in SOURCE_LANGUAGE_PROVENANCE:
                problems.append(
                    f"{names[index] or index}: slot {slot.get('region')!r}/"
                    f"{slot.get('tier')!r} requires provenance {want!r}, which is "
                    f"not one of {sorted(SOURCE_LANGUAGE_PROVENANCE)}"
                )
            if str(slot.get("tier")) not in SOURCE_LANGUAGE_TIERS:
                problems.append(
                    f"{names[index] or index}: slot {slot.get('region')!r}/"
                    f"{slot.get('tier')!r} requires a provenance, and that tier "
                    f"carries no source-language text for one to be read from"
                )

    gloss = sum(int(t.get("gloss_capable") or 0) for t in tranches)
    if gloss < int(mix.get("gloss_capable_records") or 0):
        problems.append(
            f"the allocation places {gloss} gloss-capable record(s); the mix "
            f"declares {mix.get('gloss_capable_records')!r}, and a plan that "
            f"places fewer than the target has already missed it"
        )
    for index, tranche in enumerate(tranches):
        capacity = sum(
            int(slot.get("n") or 0) for slot in (tranche.get("slots") or [])
            if str(slot.get("tier")) in GLOSS_CAPABLE_TIERS)
        if int(tranche.get("gloss_capable") or 0) > capacity:
            problems.append(
                f"{names[index] or index}: {tranche.get('gloss_capable')} "
                f"gloss-capable record(s) allocated over {capacity} slot(s) on "
                f"a tier that can carry a gloss case"
            )

    # Ruling 56. Two lines, because they are two questions. The first counts
    # cases that ask WHICH chunk was quoted and may only be written where a
    # second chunk competes; the second counts cases on records where nothing
    # competes, and is capacity-capped and REPORTED rather than floored.
    quoted = sum(int(t.get("expect_quoted_from_original_cases") or 0)
                 for t in tranches)
    want_quoted = int(mix.get("min_expect_quoted_from_original_cases_at_60") or 0)
    if quoted < want_quoted:
        problems.append(
            f"the allocation writes {quoted} expect_quoted_from_original "
            f"case(s) on records that hold a reference_translation and the mix "
            f"requires {want_quoted}. One such case is a measurement of "
            f"WHICH chunk the answer path quoted; the same words on a "
            f"verbatim_machine_english record ask only whether anything "
            f"resolved, and are counted on their own line"
        )

    for index, tranche in enumerate(tranches):
        capacity = sum(
            int(slot.get("n") or 0) for slot in (tranche.get("slots") or [])
            if str(slot.get("tier")) in QUOTATION_CHOICE_TIERS)
        if int(tranche.get("expect_quoted_from_original_cases") or 0) > capacity:
            problems.append(
                f"{names[index] or index}: "
                f"{tranche.get('expect_quoted_from_original_cases')} "
                f"quoted-from-original case(s) allocated over {capacity} slot(s) "
                f"on a tier that carries both an original and a published "
                f"English for it to be preferred over"
            )

        # PRESENCE, not a value. An absent field is a sub-tranche that never
        # decided, and a zero it was given by `or 0` is a decision nobody made.
        # This is the guard with teeth on this line: the aggregate below is a
        # declared zero, for the reason ruling 56 gives.
        vme_cases = tranche.get("vme_quotation_cases")
        if vme_cases is None:
            problems.append(
                f"{names[index] or index}: declares no vme_quotation_cases. "
                f"Ruling 56 splits the quotation quota in two and a sub-tranche "
                f"that names only one of them is a sub-tranche whose cases land "
                f"in whichever line reads better afterwards"
            )
            continue
        vme_capacity = sum(
            int(slot.get("n") or 0) for slot in (tranche.get("slots") or [])
            if str(slot.get("tier")) == "verbatim_machine_english")
        if int(vme_cases or 0) > vme_capacity:
            problems.append(
                f"{names[index] or index}: {vme_cases} vme quotation case(s) "
                f"allocated over {vme_capacity} verbatim_machine_english slot(s)"
            )

    vme_total = sum(int(t.get("vme_quotation_cases") or 0) for t in tranches)
    want_vme = int(mix.get("min_vme_quotation_cases_at_60") or 0)
    if vme_total < want_vme:
        problems.append(
            f"the allocation writes {vme_total} vme quotation case(s) and the "
            f"mix requires {want_vme}"
        )

    return problems


def split_quotation_cases(
    cases: "list[tuple[str, list[str]]]", tiers: "dict[str, str]",
) -> "dict[str, list]":
    """Read the gold set's quotation cases as the two questions they ask.

    Ruling 56, F4. Until today the six lived only in the allocation PLAN and
    nothing counted the cases that actually exist -- so the number a reader
    takes to G3 was a number nobody had classified. FINDING 40's correction is
    a reading, and a reading nothing computes is a reading that decays.

    `cases` is (case id, the doc_ids its expect_quoted_from_original names).
    A case naming several records is counted as `choice` if ANY of them can
    carry the choice, because one competing pair of chunks is enough to make
    the assertion discriminate.

    The direction is why this is worth computing every run: the plan predicts
    verbatim_machine_english becomes the common tier, and every vme record
    supplies a case that passes by construction. The count therefore gets
    EASIER to satisfy as the thing it measures gets harder to observe, and it
    drifts silently, because the count is the only thing anyone reads.
    """
    split: dict[str, list] = {"choice": [], "whether_resolved": [], "untiered": []}
    for case_id, doc_ids in cases:
        known = [d for d in doc_ids if d in tiers]
        unknown = [d for d in doc_ids if d not in tiers]
        if unknown:
            split["untiered"].append((case_id, sorted(unknown)))
            continue
        if any(tiers[d] in QUOTATION_CHOICE_TIERS for d in known):
            split["choice"].append(case_id)
        else:
            split["whether_resolved"].append(case_id)
    return split


def check_delivery(
    mix: "dict", delivered: "dict[str, tuple[str, str]]",
    gloss_declared: "set[str] | None" = None,
    provenance_of: "dict[str, str] | None" = None,
) -> "list[str]":
    """Do the records actually CURATED deliver the allocation? Returns problems.

    F3, 2026-08-31, and it exists because `check_allocation` above does not do
    this. That function guards the PLAN -- eleven branches of arithmetic over a
    table of slots -- and nothing guarded DELIVERY. Two records into Block F the
    gloss-capable count was already missed and no check said so, because the
    only thing anyone had asked was whether the plan added up.

    `delivered` is {record_id: (region, tier)} for the TRANCHE'S records only.
    The seed 24 are excluded by their own definition: they are the ledger's
    `not_timed`, and this check is about the 36 the allocation places.

    What fails, and what is only reported
    -------------------------------------

    OVER-DELIVERY FAILS. A record curated into a (region, tier) cell the
    allocation does not place, or a cell curated past its planned count, is a
    slot taken from somewhere else -- and since nobody re-curates a record, the
    place it was taken from can never be refilled. That is detectable on the day
    it happens and it fails on the day it happens.

    A SHORTFALL IS A NOTE, for `ingest.verify`'s own reason about the tier
    histogram: the mix is a target for the END of Block F, and a suite that
    failed on it from F3 to F7 would be ignored from F3 to F7.

    UNREACHABILITY FAILS, and it is the point of the whole function. A shortfall
    that can still be made up is progress; a shortfall larger than the slots
    remaining is a target that has already failed, and the difference between
    those two is exactly what nobody would notice until F7. This is
    `check_target_mix`'s reachability clause one level down: there, a per-region
    minimum the aggregate cannot reach is refused at declaration; here, a quota
    the remaining sub-tranches cannot carry is refused the moment curation makes
    it so.
    """
    problems: list[str] = []
    gloss_declared = set(gloss_declared or ())

    allocation = mix.get("allocation") or {}
    tranches = allocation.get("sub_tranches") or []
    if not tranches:
        return problems

    planned: dict[tuple[str, str], int] = {}
    for tranche in tranches:
        for slot in tranche.get("slots") or []:
            key = (str(slot.get("region")), str(slot.get("tier")))
            planned[key] = planned.get(key, 0) + int(slot.get("n") or 0)

    done: dict[tuple[str, str], int] = {}
    for record_id, (region, tier) in sorted(delivered.items()):
        key = (region, tier)
        if key not in planned:
            problems.append(
                f"{record_id} is curated as {tier} in {region}, which the "
                f"allocation places nowhere. A record outside the plan spends a "
                f"slot the plan still expects to fill"
            )
            continue
        done[key] = done.get(key, 0) + 1

    # `planned.get(key, 0)` rather than `planned[key]`: with the membership
    # test above removed, an unplanned cell reaches here and a subscript would
    # RAISE. A checker that crashes when its own guard is removed cannot be
    # mutation-verified -- scripts/mutate_fidelity.py reports "crash, not a
    # guard failure" and says nothing about whether the guard works. Degrading
    # into a wrong answer is what makes a guard observable.
    for key, count in sorted(done.items()):
        if count > planned.get(key, 0):
            problems.append(
                f"{key[0]} / {key[1]}: {count} curated against "
                f"{planned.get(key, 0)} "
                f"planned. Over-delivering a cell takes the slot from another, "
                f"and nobody re-curates a record"
            )

    remaining = {k: planned[k] - done.get(k, 0) for k in planned}

    # The gloss quota, and the only part of this that is DECLARED rather than
    # derived. corpus_tiers.json defines gloss-capable mechanically -- a hedged
    # reading AND a statement that the reading is uncertain, both inside a
    # RETRIEVAL-ELIGIBLE chunk -- and that is a judgement about prose, not
    # something a classifier here can read. So it is declared in the sidecar,
    # beside the tiers, and what IS checked is everything mechanical about the
    # declaration.
    for record_id in sorted(gloss_declared):
        # Same reason as the `.get` above: with the membership test removed,
        # the tier lookup must still return something rather than raise.
        tier_of = (delivered.get(record_id) or ("", ""))[1]
        if record_id not in delivered:
            problems.append(
                f"{record_id} is declared gloss-capable and is not a record "
                f"this tranche curated"
            )
        elif tier_of not in GLOSS_CAPABLE_TIERS:
            problems.append(
                f"{record_id} is declared gloss-capable on tier "
                f"{tier_of}, which cannot carry a gloss case. "
                f"A refusable_with_gloss case requires the answer to quote a "
                f"PUBLISHED hedged reading"
            )

    # FINDING 51 and ruling 62, F5. The declarations are a LIST OF OBJECTS. A
    # bare id cannot say which sub-tranche made it, and without that nothing in
    # this repository could compare a sub-tranche's DELIVERY against its own
    # DECLARATION -- which is both the blocker FINDING 51 named and the loophole
    # it named, in one missing field. `kind` is ruling 62's owed distinction.
    #
    # These read the DOCUMENT's declarations. `gloss_declared` above is the set
    # of ids, which ingest.verify derives from this same list so that production
    # has one source; the unit tests pass the two apart on purpose, because the
    # per-record guards above and the shape guards here are different rules.
    tranche_names = {str(t.get("name")) for t in tranches}
    declared_by_tranche: dict[str, int] = {}
    for entry in (mix.get("gloss_capable_declared") or []):
        if not isinstance(entry, dict):
            problems.append(
                f"gloss-capable declaration {entry!r} is a bare id and names no "
                f"sub-tranche. An unattributed declaration is what kept "
                f"FINDING 51 invisible for two sub-tranches"
            )
            continue
        name = str(entry.get("sub_tranche") or "")
        if name not in tranche_names:
            problems.append(
                f"{entry.get('record')!r} is declared gloss-capable in "
                f"sub-tranche {name!r}, which the allocation does not place"
            )
        else:
            declared_by_tranche[name] = declared_by_tranche.get(name, 0) + 1
        kind = str(entry.get("kind") or "")
        if kind not in GLOSS_KINDS:
            problems.append(
                f"{entry.get('record')!r} declares gloss kind {kind!r}, which is "
                f"not one of {sorted(GLOSS_KINDS)}. Ruling 62: a contested "
                f"READING and a translator's hedged IDENTIFICATION are different "
                f"evidence about different failure modes"
            )

    for tranche in tranches:
        name = str(tranche.get("name"))
        planned_gloss = int(tranche.get("gloss_capable") or 0)
        if declared_by_tranche.get(name, 0) > planned_gloss:
            problems.append(
                f"{name}: {declared_by_tranche[name]} gloss-capable record(s) "
                f"declared against {planned_gloss} the sub-tranche planned. "
                f"Nothing else here compares a tranche's delivery to its own "
                f"declaration, which is how an aggregate gets met one tranche at "
                f"a time with every check green"
            )

    # Ruling 73, F5. A cell whose slots declare `requires_provenance` must end up
    # holding at least that many records of that provenance.
    #
    # Cell granularity, because that is all this function has: a record's
    # sub-tranche is not derivable from it, so a delivered Sub-Saharan Africa
    # verbatim_with_provenance record could be F4's or F6's. Requiring the COUNT
    # in the cell is the same claim without needing to know which slot it filled.
    #
    # And it fails on the UNREACHABILITY shape, not on the shortfall one: while
    # the cell still has slots left, an unmet requirement is progress, exactly as
    # this function treats every other target. Africa's cell holds two Greek
    # records today against three planned, so the requirement is still reachable
    # through the slot ruling 73 created, and it is not a failure until the cell
    # is full and no local-language record is in it.
    required: dict[tuple[str, str], int] = {}
    for tranche in tranches:
        for slot in (tranche.get("slots") or []):
            want = slot.get("requires_provenance")
            if want is None:
                continue
            key = (str(slot.get("region")), str(slot.get("tier")), str(want))
            required[key] = required.get(key, 0) + int(slot.get("n") or 0)

    provenance_of = provenance_of or {}
    for (region, tier, want), n in sorted(required.items()):
        in_cell = [r for r, (rg, ti) in delivered.items()
                   if rg == region and ti == tier]
        if not in_cell:
            continue
        unknown = sorted(r for r in in_cell if r not in provenance_of)
        if unknown:
            problems.append(
                f"{region} / {tier}: the slot requires provenance {want!r} and the "
                f"provenance of {unknown} was not supplied, so the requirement "
                f"could not be checked rather than being met"
            )
            continue
        have = sum(1 for r in in_cell if provenance_of.get(r) == want)
        left = planned.get((region, tier), 0) - len(in_cell)
        if have < n and left < n - have:
            problems.append(
                f"{region} / {tier}: {n} record(s) of provenance {want!r} are "
                f"required, {have} delivered, and {left} slot(s) remain in the "
                f"cell. The requirement can no longer be met, which is a target "
                f"already missed rather than one still open"
            )

    want_gloss = int(mix.get("gloss_capable_records") or 0)
    if len(gloss_declared) > want_gloss:
        problems.append(
            f"{len(gloss_declared)} records are declared gloss-capable and the "
            f"mix asks for {want_gloss}"
        )

    # FINDING 51, and this clause is the finding. It asked whether enough SLOTS
    # remained when the scarce thing was DECLARATIONS -- and both are counts of
    # records, so the sentence read correctly for two sub-tranches while
    # answering a question nobody was asking, in the reassuring direction. Slots
    # are plentiful by construction: every gloss-capable-tier slot in every
    # remaining sub-tranche counts, including twelve nobody intends to spend on
    # a gloss case.
    #
    # The ceiling is now BOTH, because both bind: a declaration cannot be made
    # without a slot on a tier that can carry one, and a slot cannot carry a
    # declaration its sub-tranche never planned. WHICH ONE BINDS IS NAMED --
    # reporting one number was how this went unnoticed.
    capacity = sum(n for (region, tier), n in remaining.items()
                   if tier in GLOSS_CAPABLE_TIERS)
    still_declarable = sum(int(t.get("gloss_capable") or 0)
                           for t in tranches if not t.get("closed"))
    ceiling = len(gloss_declared) + min(still_declarable, capacity)
    if ceiling < want_gloss:
        binds = "declaration" if still_declarable <= capacity else "slot"
        problems.append(
            f"the gloss quota is UNREACHABLE: {len(gloss_declared)} declared, "
            f"{still_declarable} declaration(s) left in sub-tranches still open "
            f"and {capacity} slot(s) left on a tier that can carry one, so at "
            f"most {ceiling} against {want_gloss} required. The {binds} count is "
            f"what binds"
        )

    return problems


# ---------------------------------------------------------------------------
# Flags the MANIFEST names that this module deliberately no longer honours
# ---------------------------------------------------------------------------
# FINDING 31, 2026-08-29, found by running `python -m ingest.verify` in F1.
#
# `data/seed_corpus/manifest.json.follow_up_before_ingestion` names five
# records as "paraphrased or partial": Palmyrene Tariff, Weilue, Hou Hanshu,
# Akananuru 149, Ezana Stone. That claim was held in THREE places -- the
# manifest's prose, `PARAPHRASE_ID_HINTS` above, and `MANIFEST_FLAGGED` in
# `ingest/verify.py`. On 2026-08-22 FINDING 11 corrected ONE of the three:
# eastasia-01-weilue's excerpt is now 221 verbatim characters from
# zh.wikisource and the hint was removed, with the reason written down.
#
# `verify.py` kept its copy, and its check that no manifest-flagged record is
# ever labelled `verbatim_original` has been RED ever since -- through D4,
# through Block E's four sessions and 396 runs, through F0 and the sonnet arm.
# Nothing caught it because no state block lists `ingest.verify` among the
# suites, and it is the FIRST line of the sub-tranche runbook that F3 runs.
#
# Two ends of a comparison must not hold two definitions of the thing being
# compared -- `iter_seed_records`'s own lesson, and this is it between two
# modules rather than between two walks. A lift is now a WRITTEN entry with a
# reason, and `check_paraphrase_flags` refuses a manifest flag that is neither
# honoured nor lifted. The divergence cannot recur in silence.
PARAPHRASE_FLAG_LIFTED: dict[str, str] = {
    "weilue": (
        "LIFTED 2026-08-22, FINDING 11. eastasia-01-weilue's "
        "original_text_excerpt is 221 verbatim characters from zh.wikisource "
        "三國志/卷30 and classifies as verbatim_original on its own merits. The "
        "manifest's flag marked SUSPICION and nothing in the pipeline ever "
        "turned suspicion into a determination; when two of its entries were "
        "finally checked they came back opposite ways. Leaving the flag on "
        "would have the corpus report a sourced text as paraphrased."
    ),
}


def check_paraphrase_flags(manifest_flagged: "set[str]") -> "list[str]":
    """Do the manifest's flags and this module's agree? Returns problems.

    `manifest_flagged` is the hand-transcription of the manifest's prose that
    `ingest/verify.py` holds. Transcribing prose by hand is fine; holding a
    SECOND opinion about what the code does with it is not, and that is the
    divergence FINDING 31 records.
    """
    problems: list[str] = []

    both = sorted(set(PARAPHRASE_ID_HINTS) & set(PARAPHRASE_FLAG_LIFTED))
    if both:
        problems.append(
            f"{both} are both honoured as paraphrase hints and recorded as "
            f"lifted. A flag cannot be in force and withdrawn at once"
        )

    for record_id, reason in PARAPHRASE_FLAG_LIFTED.items():
        if not (reason or "").strip():
            problems.append(
                f"the lift on {record_id!r} has no written reason. A lift with "
                f"no reason is a flag deleted by whoever last found it "
                f"inconvenient"
            )

    unaccounted = sorted(
        manifest_flagged - set(PARAPHRASE_ID_HINTS) - set(PARAPHRASE_FLAG_LIFTED)
    )
    if unaccounted:
        problems.append(
            f"the manifest flags {unaccounted} and this module neither honours "
            f"nor lifts them. That is FINDING 31 recurring: two modules holding "
            f"two opinions about one claim, with nothing that has to agree"
        )

    stray = sorted(set(PARAPHRASE_FLAG_LIFTED) - manifest_flagged)
    if stray:
        problems.append(
            f"{stray} are recorded as lifted but the manifest does not flag "
            f"them. A lift on a flag that does not exist is a note nobody can "
            f"check"
        )

    return problems
