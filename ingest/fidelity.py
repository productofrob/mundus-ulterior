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

    gloss = sum(int(t.get("gloss_capable") or 0) for t in tranches)
    if gloss != int(mix.get("gloss_capable_records") or 0):
        problems.append(
            f"the allocation places {gloss} gloss-capable record(s); the mix "
            f"declares {mix.get('gloss_capable_records')!r}"
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

    quoted = sum(int(t.get("expect_quoted_from_original_cases") or 0)
                 for t in tranches)
    want_quoted = int(mix.get("min_expect_quoted_from_original_cases_at_60") or 0)
    if quoted < want_quoted:
        problems.append(
            f"the allocation writes {quoted} expect_quoted_from_original "
            f"case(s) and the mix requires {want_quoted}. One case is a "
            f"measurement of whether the answer path quotes THAT source text"
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
