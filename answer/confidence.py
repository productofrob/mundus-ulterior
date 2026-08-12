"""Back-translation confidence scoring.

The question this answers: *how much should Part 7 trust a machine translation
of a source it is about to cite?*

Two independent signals, deliberately not one:

  chrF   character n-gram F-score between the original and its back-translation.
         Character-level, so it works on Greek, Chinese, Tamil and romanised
         Parthian without a tokenizer per script. Measures wording.

  cosine voyage-3.5 similarity between the same two texts. Measures meaning.

One number would be easier to read and worse to trust. The pair is informative
precisely where they disagree: high cosine with low chrF is a paraphrase (normal
for verse); high chrF with low cosine is close to impossible in an honest round
trip and usually means one side is not what it claims to be.

Where a published translation exists — 16 records in this corpus have one — the
machine English is also scored against it directly. That is a stronger signal
than the round trip, because it compares against a human who read the original.

Nothing here calls the network or the database. Vectors are passed in already
computed, so a caller can embed every text for a whole run in a single request
(the Voyage free tier is 3 requests/minute, and Part 4 learned that lesson the
expensive way).

Thresholds live in eval/gold/confidence_profiles.json, not in this module. They
are provisional until the first live run produces a distribution to calibrate
against, and a number that lives in data can be recalibrated without a code
change — or argued with.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field, asdict

MAX_NGRAM = 6
CHRF_BETA = 2.0

# An "untranslated echo" is the forward call returning the source unchanged.
# It scores a perfect round trip and means nothing at all, so it is checked
# before anything else.
ECHO_CHRF_THRESHOLD = 0.90

_REFUSAL_CUES = (
    re.compile(r"\bI (?:cannot|can't|am unable to)\b", re.I),
    re.compile(r"\bI'm sorry\b", re.I),
    re.compile(r"\bas an AI\b", re.I),
    re.compile(r"\bno (?:readable |legible )?text\b", re.I),
    re.compile(r"\bunable to (?:translate|read)\b", re.I),
)

_WHITESPACE_RE = re.compile(r"\s+")

# Below this many characters, chrF is too noisy to read closely. Measured, not
# guessed: three repetitions of each case on 2026-08-10 gave a chrF spread of
# 0.009-0.012 on sources of 476-919 characters, and 0.093 on the 52-character
# Weilüe notice — with cosine varying by 0.003 or less on all of them. A short
# text has few character n-grams, so a single word choice moves the score. The
# flag is a reading instruction, not a failure.
SHORT_SOURCE_CHARS = 150


# --------------------------------------------------------------------------
# chrF
# --------------------------------------------------------------------------

def _char_ngrams(text: str, n: int) -> Counter:
    return Counter(text[i:i + n] for i in range(len(text) - n + 1))


def chrf(
    hypothesis: str,
    reference: str,
    max_n: int = MAX_NGRAM,
    beta: float = CHRF_BETA,
    remove_whitespace: bool = True,
) -> float:
    """Character n-gram F-score, following Popović (2015). Range 0.0-1.0.

    Whitespace is removed by default, as in the reference implementation. That
    matters more here than in a normal MT setting: Literary Chinese has no word
    spaces at all, so a whitespace-sensitive metric would score Chinese and
    Greek on different footings.
    """
    if not hypothesis or not reference:
        return 0.0

    hyp = _WHITESPACE_RE.sub("", hypothesis) if remove_whitespace else hypothesis
    ref = _WHITESPACE_RE.sub("", reference) if remove_whitespace else reference
    if not hyp or not ref:
        return 0.0

    precisions: list[float] = []
    recalls: list[float] = []

    for n in range(1, max_n + 1):
        hyp_grams = _char_ngrams(hyp, n)
        ref_grams = _char_ngrams(ref, n)
        hyp_total = sum(hyp_grams.values())
        ref_total = sum(ref_grams.values())
        if hyp_total == 0 and ref_total == 0:
            # Both texts are shorter than n characters; the order says nothing.
            continue
        matched = sum((hyp_grams & ref_grams).values())
        precisions.append(matched / hyp_total if hyp_total else 0.0)
        recalls.append(matched / ref_total if ref_total else 0.0)

    if not precisions:
        return 0.0

    avg_p = sum(precisions) / len(precisions)
    avg_r = sum(recalls) / len(recalls)
    if avg_p + avg_r == 0:
        return 0.0
    b2 = beta * beta
    return (1 + b2) * avg_p * avg_r / (b2 * avg_p + avg_r)


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity. Vectors from voyage-3.5 are already L2-normalised, but
    normalising again costs nothing and makes this safe for any provider."""
    if not a or not b or len(a) != len(b):
        raise ValueError(f"cannot compare vectors of length {len(a)} and {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# --------------------------------------------------------------------------
# Profiles and bands
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Profile:
    """Thresholds for one genre of source text.

    Genre-aware by design. Verse does not round-trip like a sailing manual, and
    a single threshold would mark Akanāṉūṟu 149 as a failure for being poetry —
    then someone would "fix" the metric, which was right, by loosening it for
    everything. Naming the genre keeps the disagreement visible.
    """
    name: str
    cos_high: float
    cos_low: float
    chrf_high: float
    chrf_low: float
    calibrated: bool = False
    note: str = ""


@dataclass
class ConfidenceReport:
    profile: str
    band: str                       # high | medium | low | unscored
    chrf_back: float | None = None
    cos_back: float | None = None
    chrf_ref: float | None = None
    cos_ref: float | None = None
    chrf_echo: float | None = None  # forward output vs the original
    flags: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def trustworthy(self) -> bool:
        """Whether Part 7 may present this translation without a caveat."""
        return self.band == "high" and not self.blocking_flags

    @property
    def blocking_flags(self) -> list[str]:
        return [f for f in self.flags if f in BLOCKING_FLAGS]


# Flags that invalidate the round trip rather than merely colouring it. A
# blocking flag means the score is not measuring translation quality at all.
BLOCKING_FLAGS = {
    "untranslated_echo",
    "refusal_suspected",
    "empty_translation",
    "empty_back_translation",
    "script_mismatch",
}

def dominant_script(text: str) -> str | None:
    """The Unicode script family most of this text's letters belong to.

    Unicode character names begin with their script ("TAMIL LETTER A",
    "DEVANAGARI LETTER KA", "GREEK SMALL LETTER ALPHA", "CJK UNIFIED
    IDEOGRAPH-5927"), so the first token identifies the family without needing a
    table. Returns None for text with no letters at all.
    """
    import unicodedata
    from collections import Counter as _Counter

    counts: _Counter = _Counter()
    for ch in text:
        if not ch.isalpha():
            continue
        try:
            counts[unicodedata.name(ch).split()[0]] += 1
        except ValueError:      # unnamed character
            continue
    return counts.most_common(1)[0][0] if counts else None


def script_mismatch(original: str, back_translated: str) -> bool:
    """True if the two texts are not written in the same script.

    Two live runs, two versions of this check, and the second version exists
    because the first was too coarse:

      run 1  Akanāṉūṟu 149 (Tamil script) came back in Latin romanisation.
             chrF 0.004 — comparing two alphabets. Caught by a latin/non-latin
             test, which is what this function used to be.
      run 2  the same case came back 95% DEVANAGARI with a few Tamil letters.
             chrF 0.016 — and the latin/non-latin test saw "non-Latin on both
             sides" and said nothing. Devanagari answering a Tamil source is
             exactly as wrong as romanisation; the check was measuring the
             wrong distinction.

    Comparing the dominant script family catches both, and does not fire for the
    corpus's romanised records (ŠKZ, Sabaic, Nabataean, the runes), where both
    sides are legitimately LATIN.
    """
    a = dominant_script(original)
    b = dominant_script(back_translated)
    if a is None or b is None:
        return False        # nothing to compare; other flags cover empty output
    return a != b


def looks_like_refusal(text: str) -> bool:
    return any(p.search(text) for p in _REFUSAL_CUES)


def score(
    original: str,
    forward_en: str,
    back_translated: str,
    *,
    profile: Profile,
    cos_back: float | None = None,
    reference_en: str | None = None,
    cos_ref: float | None = None,
    source_is_english: bool = False,
) -> ConfidenceReport:
    """Score one round trip.

    `cos_back` is cosine(original, back_translated); `cos_ref` is
    cosine(forward_en, reference_en). Both are optional — the report degrades to
    chrF only and says so, rather than failing.
    """
    report = ConfidenceReport(profile=profile.name, band="unscored")

    if not forward_en.strip():
        report.flags.append("empty_translation")
        report.notes.append("the forward translation came back empty")
        return report
    if looks_like_refusal(forward_en):
        report.flags.append("refusal_suspected")
        report.notes.append(
            "the forward translation reads as a refusal or an apology, not a "
            "translation — inspect the raw response before trusting any score"
        )

    # Echo check first: if the model handed back the source, everything
    # downstream is a perfect score for no work.
    if not source_is_english:
        report.chrf_echo = chrf(forward_en, original)
        if report.chrf_echo >= ECHO_CHRF_THRESHOLD:
            report.flags.append("untranslated_echo")
            report.notes.append(
                f"the 'translation' is {report.chrf_echo:.2f} chrF identical to "
                f"the source — the model echoed the passage instead of "
                f"translating it. The round-trip score below is meaningless."
            )

    if not back_translated.strip():
        report.flags.append("empty_back_translation")
        report.notes.append("the back-translation came back empty")
    else:
        report.chrf_back = chrf(back_translated, original)
        report.cos_back = cos_back
        if script_mismatch(original, back_translated):
            report.flags.append("script_mismatch")
            report.notes.append(
                "the back-translation is not in the same script as the source "
                "(most likely romanised where the source is not). chrF across "
                "two writing systems is near zero whatever the translation is "
                "worth, so neither score below can be read as quality."
            )

    if reference_en:
        report.chrf_ref = chrf(forward_en, reference_en)
        report.cos_ref = cos_ref

    if len(original) < SHORT_SOURCE_CHARS and report.chrf_back is not None:
        report.flags.append("short_source_chrf_noisy")
        report.notes.append(
            f"the source is {len(original)} characters; below "
            f"{SHORT_SOURCE_CHARS} the chrF of repeated runs varies by around "
            f"0.09, against 0.01 on longer passages. Read cos_back here and "
            f"treat chrF as indicative only."
        )

    report.band = _band(report, profile)
    _add_divergence_flags(report, profile)
    return report


def _band(report: ConfidenceReport, profile: Profile) -> str:
    """Meaning leads, wording corroborates.

    Cosine carries the band because a good translation may share little wording
    with its source's back-translation, while a bad one rarely shares meaning.
    chrF can only pull a result down from 'high' to 'medium' — never up — so a
    string coincidence cannot manufacture confidence.
    """
    if report.blocking_flags:
        return "low"
    if report.cos_back is None:
        if report.chrf_back is None:
            return "unscored"
        # chrF alone: usable, but held to the stricter of the two thresholds.
        return "medium" if report.chrf_back >= profile.chrf_high else "low"

    if report.cos_back >= profile.cos_high:
        if report.chrf_back is not None and report.chrf_back < profile.chrf_low:
            return "medium"
        return "high"
    if report.cos_back >= profile.cos_low:
        return "medium"
    return "low"


def _add_divergence_flags(report: ConfidenceReport, profile: Profile) -> None:
    if report.cos_back is None or report.chrf_back is None:
        if report.cos_back is None and report.chrf_back is not None:
            report.notes.append(
                "no embedding similarity available; band set from chrF alone"
            )
        return

    if report.cos_back >= profile.cos_high and report.chrf_back < profile.chrf_low:
        report.flags.append("semantic_ok_lexical_low")
        report.notes.append(
            "meaning survives the round trip but wording does not — a "
            "paraphrase. Expected for verse and for heavily formulaic "
            "inscriptions; worth a look in plain prose."
        )

    if report.chrf_back >= profile.chrf_high and report.cos_back < profile.cos_low:
        report.flags.append("lexical_high_semantic_low")
        report.notes.append(
            "wording matches closely while meaning does not, which an honest "
            "round trip does not produce. Check whether the two texts are in "
            "the language they claim to be, and whether the embedding model "
            "handles this script at all."
        )

    if report.chrf_ref is not None and report.chrf_back is not None:
        if report.chrf_ref < profile.chrf_low and report.chrf_back >= profile.chrf_high:
            report.flags.append("disagrees_with_published_translation")
            report.notes.append(
                "the round trip is self-consistent but the English differs from "
                "the published translation. Self-consistency is not accuracy: a "
                "model can mistranslate a passage and mistranslate it back the "
                "same way."
            )
