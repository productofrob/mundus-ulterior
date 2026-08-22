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
