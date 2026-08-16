"""Citations: how evidence is shown to the model, and how the answer is checked.

Part 7's claim is that every claim traces to a chunk and every chunk traces to
characters on disk. A prompt asking for that politely is not the claim; this
module is. Nothing here trusts the model, and everything it reports is a fact
about strings that can be recomputed from the database and the seed JSON.

Six checks, and what each one is for:

  unknown_markers          the answer cites [S7] when six sources were supplied.
                           A citation that resolves to nothing looks exactly like
                           a citation that resolves to something.

  uncited_sentences        a sentence making a claim with no marker at all. The
                           most common way an answer stops being grounded is not
                           a wrong citation, it is a fluent connecting sentence
                           that came from the model's own knowledge.

  unverified_quotes        quoted text that appears in none of the passages it
                           cites. This is the check that reaches disk: a verified
                           quote is resolved to an absolute character span in the
                           source file, via the chunk's char_start.

  misattributed_quotes     quoted text that exists in the corpus but not in the
                           source it was attributed to. Worse than an invented
                           quote, because it survives a spot check.

  claims_on_untranslated   a claim resting on a passage that has no English —
                           the Vimose case. Six partly undeciphered runic
                           sequences, whose published gloss says "likely",
                           "possibly", "remain only partially deciphered". A
                           confident English reading of those, arriving attached
                           to a citation, is the worst thing this system could
                           emit. Citing such a passage is allowed only with a
                           verbatim quotation of it in the same sentence.

  unlabelled_machine       a machine translation reaching the reader without the
                           band that qualifies it. Nine of twelve Part 6 cases
                           banded medium; an unlabelled medium translation is
                           worse than no confidence score, because the reader
                           assumes there was none to give.

Quote matching is done on whitespace-collapsed text. Whitespace is the one thing
a model reliably alters when copying, and Literary Chinese has no word spaces at
all, so a whitespace-sensitive check would hold Greek and Chinese to different
standards — the same argument that made chrF whitespace-insensitive in Part 6.
Where an exact match fails, a case-folded match is tried and recorded as
`case_folded` — the span is still exact, because `_fold` is length-preserving,
but the source renders those characters differently and a viewer that says
"exact" beside two visibly different strings discredits itself. Where that fails
too, a Unicode-NFC match is tried and the quote is marked verified-but-unresolved:
NFC can merge codepoints, so the character offset is no longer trustworthy, and
reporting a span that might be wrong is worse than reporting none.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import NamedTuple

from answer.evidence import Passage, caveat_for

MARKER_RE = re.compile(r"\[\s*(S\d+(?:\s*[,;]\s*S\d+)*)\s*\]")
_SINGLE_MARKER_RE = re.compile(r"S\d+")

# Both the ASCII and the guillemet forms, plus curly quotes, because a model
# told to use one will occasionally use another and a missed quotation is a
# missed check.
# The length floor lives in _is_substantive, not here: two gates on the same
# property drift apart, and the regex one silently rejected `"大秦"` for being
# under three characters while accepting `" or "` for being over.
_QUOTE_RE = re.compile(
    r"«([^»]+)»"
    r"|“([^”]+)”"
    r"|\"([^\"]+)\""
    r"|‘([^’]+)’",
    re.S,
)

_WS_RE = re.compile(r"\s+")

# A sentence shorter than this is a fragment, a heading or a transition, and
# demanding a citation for "In short:" produces noise that trains the reader to
# ignore the check.
MIN_CLAIM_WORDS = 5

MACHINE_LABEL = "MACHINE TRANSLATION"

# The refusal is the model doing as it was told. It carries no citation because
# there is nothing to cite, and the first live run failed it as an uncited claim
# in three answers out of five — including the out-of-corpus question, where
# refusing was the entire correct behaviour. Defined here rather than in
# `assemble` because `assemble` imports this module; `assemble.NO_ANSWER` is an
# alias for it.
REFUSAL_SENTENCE = "The sources retrieved do not answer this question."

# Terminal punctuation is often followed by a closing quote or bracket before
# the space that ends the sentence. The first live run required the punctuation
# to sit immediately before the space, so `Cottonara." [S1] The same source ...`
# was read as a single sentence and a four-sentence answer reported
# `claim sentences 1`.
_CLOSERS = "\"'»”’)]"
_TERMINALS = ".!?。？！"

# A marker following the boundary belongs to the sentence it cites. `... toward
# Egypt. [S6]` orphaned S6 into a fragment of its own, so a quotation the model
# had cited correctly was reported misattributed.
_LEADING_MARKERS_RE = re.compile(
    r"\s*(?:\[\s*S\d+(?:\s*[,;]\s*S\d+)*\s*\]\s*)+"
)

# Periods that do not end sentences. A corpus of classical citations is full of
# them: `c. 160-300 CE` split a sentence mid-quotation in the first live run,
# and `pp. 39-50`, `cf.`, `e.g.` and editors' initials are all one keystroke
# away. Single letters are treated as initials (`W. H. Schoff`).
_ABBREVIATIONS = frozenset("""
ca cf circ cent col cols dr ed eds esp et etc fig figs fl fr ibid inv ll
mr mrs ms mss no nos pp pl pls prof repr rev st trans viz vol vols vs
e.g i.e s.v op.cit
""".split())

# Words that cannot on their own constitute a quotation. Belt and braces: with
# the splitter fixed the parity bug that produced `'or'` and `'and'` as quoted
# text cannot recur, but a quotation check that can report a conjunction as a
# fabricated quote is one bad regex away from crying wolf again.
_FUNCTION_WORDS = frozenset("""
a an and as at be but by for from in into is it of on or that the this to was
were with
""".split())


# --------------------------------------------------------------------------
# Text utilities
# --------------------------------------------------------------------------

def _collapse_with_map(text: str) -> tuple[str, list[int]]:
    """Whitespace-collapsed text, plus normalised index -> original index.

    Built character by character so the map stays exact. Collapsing is the only
    transformation applied, precisely so that this map remains truthful.
    """
    out: list[str] = []
    index: list[int] = []
    previous_was_space = True          # leading whitespace is dropped
    for i, ch in enumerate(text):
        if ch.isspace():
            if not previous_was_space:
                out.append(" ")
                index.append(i)
                previous_was_space = True
            continue
        out.append(ch)
        index.append(i)
        previous_was_space = False
    while out and out[-1] == " ":
        out.pop()
        index.pop()
    return "".join(out), index


def collapse(text: str) -> str:
    return _WS_RE.sub(" ", text).strip()


def markers_in(text: str) -> list[str]:
    """Every source marker in `text`, in order of first appearance."""
    found: list[str] = []
    for group in MARKER_RE.findall(text):
        for marker in _SINGLE_MARKER_RE.findall(group):
            if marker not in found:
                found.append(marker)
    return found


def _in_quote_mask(text: str) -> list[bool]:
    """For each index, whether it sits inside an open quotation.

    Only the marks that can be tracked honestly are tracked: the ASCII `"` by
    parity, and the paired «» “” by depth. The curly single quote is excluded
    deliberately, because ’ is also an apostrophe and `Casson’s` would otherwise
    open a quotation that never closes.
    """
    mask = [False] * len(text)
    double = False
    depth = 0
    for i, ch in enumerate(text):
        if ch == '"':
            double = not double
            mask[i] = True
        elif ch in "«“":
            depth += 1
            mask[i] = True
        elif ch in "»”":
            depth = max(0, depth - 1)
            mask[i] = True
        else:
            mask[i] = double or depth > 0
    return mask


def _is_abbreviation(text: str, dot: int) -> bool:
    """Whether the period at `dot` closes an abbreviation rather than a
    sentence. `c. 160-300 CE` is the case that cost the first live run."""
    start = dot
    while start > 0 and (text[start - 1].isalpha() or text[start - 1] == "."):
        start -= 1
    token = text[start:dot].lower().strip(".")
    if not token:
        return False
    if len(token) == 1 and token.isalpha():
        return True                      # an initial: W. H. Schoff
    return token in _ABBREVIATIONS


def _trimmed(text: str, start: int, end: int) -> tuple[int, int] | None:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return (start, end) if end > start else None


def sentence_spans(text: str) -> list[tuple[int, int]]:
    """(start, end) of each sentence-ish unit, in `text`'s own coordinates.

    Offsets rather than strings, because quotations are extracted from the whole
    answer and attributed to the sentence containing them. Extracting quotes per
    sentence is what broke in the first live run: a split inside a quotation left
    an odd number of quote marks in each fragment, so the regex paired the close
    of one quotation with the open of the next and reported the prose between
    them — `'or'`, `'[S1], and'` — as quoted text the model had fabricated.

    Still deliberately crude about what counts as a sentence. What it now refuses
    to do is split inside a quotation, split after an abbreviation, or leave a
    trailing marker behind as a fragment of its own.
    """
    mask = _in_quote_mask(text)
    n = len(text)
    spans: list[tuple[int, int]] = []
    start = 0
    i = 0
    while i < n:
        ch = text[i]
        if ch == "\n":
            span = _trimmed(text, start, i)
            if span:
                spans.append(span)
            i += 1
            start = i
            continue

        if ch in _TERMINALS:
            j = i + 1
            while j < n and text[j] in _CLOSERS:
                j += 1
            closed_here = j > i + 1
            # A period inside a quotation ends a sentence only when the
            # quotation closes on it. `"...pepper." [S5] The next ...` is a
            # boundary; the period in `"c. 160-300 CE"` is not.
            if mask[i] and not closed_here:
                i += 1
                continue
            if not (j >= n or text[j].isspace()):
                i += 1
                continue
            if _is_abbreviation(text, i):
                i += 1
                continue
            marker = _LEADING_MARKERS_RE.match(text, j)
            if marker:
                j = marker.end()
            span = _trimmed(text, start, j)
            if span:
                spans.append(span)
            start = j
            i = j
            continue
        i += 1

    span = _trimmed(text, start, n)
    if span:
        spans.append(span)
    return spans


def split_sentences(text: str) -> list[str]:
    """Sentence-ish units. See `sentence_spans` for what counts as a boundary."""
    return [text[a:b] for a, b in sentence_spans(text)]


def is_claim(sentence: str) -> bool:
    """Whether this sentence has to carry a citation."""
    stripped = sentence.strip()
    if stripped.endswith(":"):
        return False
    # The refusal is the model obeying the prompt. There is nothing to cite.
    if collapse(stripped).rstrip(".").lower() == REFUSAL_SENTENCE.rstrip(".").lower():
        return False
    # A heading or a bare list label.
    body = re.sub(MARKER_RE, "", stripped)
    body = re.sub(r"^[-*•#>\s\d.)]+", "", body).strip()
    if not body:
        return False
    return len(body.split()) >= MIN_CLAIM_WORDS


def _is_substantive(quote: str) -> bool:
    """Whether a quoted string is long enough, and meaningful enough, to be
    treated as a quotation at all.

    The length floor is script-aware for the same reason chrF is: `大秦國` is a
    quotation and `the` is not, and a floor set in characters alone would either
    reject the Chinese or accept the conjunction.
    """
    if not quote:
        return False
    non_latin = any(ord(ch) > 0x24F for ch in quote)
    if len(quote) < (2 if non_latin else 3):
        return False
    words = re.findall(r"\w+", quote.lower())
    if words and all(w in _FUNCTION_WORDS for w in words):
        return False
    return True


def extract_quotes_with_spans(text: str) -> list[tuple[str, int, int]]:
    """Every quotation in `text`, with its offsets in `text`.

    Run over a whole answer, never over one sentence — see `sentence_spans` for
    why. The length and function-word floors are applied to the stripped quote,
    so ` or ` between two quotations cannot pass as a three-character one.
    """
    found: list[tuple[str, int, int]] = []
    for match in _QUOTE_RE.finditer(text):
        group = next(
            i for i, g in enumerate(match.groups(), start=1) if g is not None
        )
        raw = match.group(group)
        quote = raw.strip()
        if not _is_substantive(quote):
            continue
        offset = match.start(group) + (len(raw) - len(raw.lstrip()))
        found.append((quote, offset, offset + len(quote)))
    return found


def extract_quotes(text: str) -> list[str]:
    return [quote for quote, _, _ in extract_quotes_with_spans(text)]


# --------------------------------------------------------------------------
# Locating a quote on disk
# --------------------------------------------------------------------------

@dataclass
class QuoteSpan:
    quote: str
    marker: str
    chunk_id: str
    doc_id: str
    source_field: str
    # Absolute offsets into the named field of the seed JSON record. The chunk's
    # own span is char_start..char_end; the quote sits inside it.
    abs_start: int | None
    abs_end: int | None
    # 'exact'       the characters are there as written, allowing for whitespace
    #               and for punctuation at the edges of the quotation.
    # 'case_folded' they are there, but the letter case differs — the writer
    #               lowercased an opening letter to fit the quotation into a
    #               sentence of their own. The span is exact (`_fold` is
    #               length-preserving, so the index map stays truthful); it is
    #               the *rendering* that differs, and a viewer printing "exact"
    #               beside two visibly different strings discredits itself.
    # 'normalised'  found only after Unicode NFC, which can merge codepoints.
    #               No span is claimed, because a span that might be wrong is
    #               worse than none.
    match: str          # 'exact' | 'case_folded' | 'normalised'
    within: str         # 'source' | 'english'

    def to_dict(self) -> dict:
        return asdict(self)


# Punctuation a writer adds or drops at the edge of a quotation without
# altering what was quoted. The first live run produced four false fabrications
# from exactly this: `departing with pepper.` against a source reading
# `departing with pepper—`, and `Alla',` against `Alla'.`.
_EDGE_PUNCTUATION = " \t\n.,;:!?—–-…\"'“”‘’«»()[]"


def _fold(text: str) -> str:
    """Lowercased, and guaranteed the same length as the input.

    `str.lower()` is not length-preserving for every codepoint, and the index
    map built by `_collapse_with_map` is only truthful while length is. Any
    character whose lowercase form is not one character is left alone.
    """
    out: list[str] = []
    for ch in text:
        low = ch.lower()
        out.append(low if len(low) == 1 else ch)
    return "".join(out)


class Located(NamedTuple):
    """Where a quote sits, and *how* it had to be matched to be found there.

    A NamedTuple rather than a dataclass so that `span[0]` and `span[1]` keep
    meaning what they meant when this function returned a plain pair — the third
    field is additive, and no caller that only wants offsets has to change.

    `match` exists because until 2026-08-14 the case-folded fallback below was
    invisible at the point of use: `locate_quote` recorded `match="exact"`
    whichever branch found the quote, and `ui/build_ui_data.py --verify` had to
    re-derive the distinction from the characters and report it as a labelling
    defect. Nine archived spans sit in that bucket. The fallback was never
    wrong; the label was.
    """
    start: int
    end: int
    match: str          # 'exact' | 'case_folded'


def locate_in_text(quote: str, haystack: str) -> Located | None:
    """Offsets of `quote` within `haystack`, in `haystack`'s own coordinates.

    Insensitive to whitespace, to case, and to punctuation at the edges of the
    quotation — the three things a writer alters when fitting a quotation into a
    sentence of their own, none of which changes what was quoted. The first live
    run reported four fabricated quotations that were nothing of the kind: three
    had their opening letter lowercased to fit mid-sentence, and one had its
    terminal em-dash replaced by the period the quoting convention puts inside
    the marks.

    Returns None when the quote is genuinely not present. The span returned
    covers the trimmed quotation, so a reported offset always round-trips to the
    characters it names — including on the case-folded branch, which is why the
    span can be reported at all and only its *label* had to change.
    """
    norm_hay, index = _collapse_with_map(haystack)
    norm_quote = collapse(quote).strip(_EDGE_PUNCTUATION)
    if not norm_quote:
        return None
    match = "exact"
    position = norm_hay.find(norm_quote)
    if position < 0:
        position = _fold(norm_hay).find(_fold(norm_quote))
        match = "case_folded"
    if position < 0:
        return None
    start = index[position]
    end = index[position + len(norm_quote) - 1] + 1
    return Located(start, end, match)


def _nfc_contains(quote: str, haystack: str) -> bool:
    needle = unicodedata.normalize(
        "NFC", collapse(quote).strip(_EDGE_PUNCTUATION)
    )
    return bool(needle) and _fold(needle) in _fold(
        unicodedata.normalize("NFC", collapse(haystack))
    )


def locate_quote(quote: str, passage: Passage) -> QuoteSpan | None:
    """Resolve a quote against one passage, source text first.

    The source text is tried before the English because it is the thing that
    exists on disk with a character span. A quote found in the source gets
    absolute offsets; a quote found only in the English is verified but has no
    on-disk span, because a translation is not a file offset.
    """
    span = locate_in_text(quote, passage.chunk.text)
    if span is not None:
        return QuoteSpan(
            quote=quote, marker=passage.marker, chunk_id=passage.chunk_id,
            doc_id=passage.doc_id, source_field=passage.chunk.source_field,
            abs_start=passage.chunk.char_start + span[0],
            abs_end=passage.chunk.char_start + span[1],
            match=span.match, within="source",
        )

    english = passage.english.text
    if english:
        span = locate_in_text(quote, english)
        if span is not None:
            # A *published* translation is a chunk of the same seed record, with
            # its own field and offsets, so a quote from it resolves to disk just
            # as the original does. A *machine* translation does not: it lives in
            # `chunk_translations`, was made at Part 6 time, and has no character
            # span in any file. The distinction is the whole point — the reader
            # is told which of the two they are looking at.
            translation = passage.translation_section
            if translation is not None and passage.english.kind in (
                "published", "published_document"
            ):
                return QuoteSpan(
                    quote=quote, marker=passage.marker,
                    chunk_id=translation.chunk_id, doc_id=passage.doc_id,
                    source_field=translation.source_field,
                    abs_start=translation.char_start + span[0],
                    abs_end=translation.char_start + span[1],
                    match=span.match, within="english",
                )
            return QuoteSpan(
                quote=quote, marker=passage.marker, chunk_id=passage.chunk_id,
                doc_id=passage.doc_id, source_field=passage.chunk.source_field,
                abs_start=None, abs_end=None, match=span.match, within="english",
            )

    if _nfc_contains(quote, passage.chunk.text):
        return QuoteSpan(
            quote=quote, marker=passage.marker, chunk_id=passage.chunk_id,
            doc_id=passage.doc_id, source_field=passage.chunk.source_field,
            abs_start=None, abs_end=None, match="normalised", within="source",
        )
    if english and _nfc_contains(quote, english):
        return QuoteSpan(
            quote=quote, marker=passage.marker, chunk_id=passage.chunk_id,
            doc_id=passage.doc_id, source_field=passage.chunk.source_field,
            abs_start=None, abs_end=None, match="normalised", within="english",
        )
    return None


# --------------------------------------------------------------------------
# The report
# --------------------------------------------------------------------------

@dataclass
class GroundingReport:
    ok: bool = False
    cited_markers: list[str] = field(default_factory=list)
    unknown_markers: list[str] = field(default_factory=list)
    uncited_sentences: list[str] = field(default_factory=list)
    unverified_quotes: list[dict] = field(default_factory=list)
    quoted_metadata: list[dict] = field(default_factory=list)
    misattributed_quotes: list[dict] = field(default_factory=list)
    claims_on_untranslated: list[dict] = field(default_factory=list)
    unlabelled_machine: list[str] = field(default_factory=list)
    quote_spans: list[QuoteSpan] = field(default_factory=list)
    claim_sentences: int = 0
    cited_sentences: int = 0
    notes: list[str] = field(default_factory=list)

    @property
    def coverage(self) -> float:
        if not self.claim_sentences:
            return 1.0
        return self.cited_sentences / self.claim_sentences

    @property
    def failures(self) -> dict[str, int]:
        return {
            "unknown_markers": len(self.unknown_markers),
            "uncited_sentences": len(self.uncited_sentences),
            "unverified_quotes": len(self.unverified_quotes),
            "quoted_metadata": len(self.quoted_metadata),
            "misattributed_quotes": len(self.misattributed_quotes),
            "claims_on_untranslated": len(self.claims_on_untranslated),
            "unlabelled_machine": len(self.unlabelled_machine),
        }

    def to_dict(self) -> dict:
        data = {
            k: v for k, v in asdict(self).items() if k != "quote_spans"
        }
        data["quote_spans"] = [s.to_dict() for s in self.quote_spans]
        data["coverage"] = round(self.coverage, 4)
        data["failures"] = self.failures
        return data


def verify(
    answer_text: str,
    passages: list[Passage],
    rendered_sources: str | None = None,
) -> GroundingReport:
    """Check an assembled answer against the evidence it was given.

    `rendered_sources` is the sources block that will actually be shown beside
    the answer. It is checked, rather than assumed, because the rule that a
    machine translation is never presented without its band is a property of what
    reaches the reader — not of what this code intended to reach the reader.
    """
    report = GroundingReport()
    by_marker = {p.marker: p for p in passages}

    # Quotations are extracted once, from the whole answer, and attributed to
    # the sentence containing their opening character. Extracting them per
    # sentence made the check depend on the splitter agreeing with the model
    # about where sentences end, and it did not.
    all_quotes = extract_quotes_with_spans(answer_text)

    for span_start, span_end in sentence_spans(answer_text):
        sentence = answer_text[span_start:span_end]
        sentence_markers = markers_in(sentence)
        claim = is_claim(sentence)
        if claim:
            report.claim_sentences += 1

        for marker in sentence_markers:
            if marker not in by_marker:
                if marker not in report.unknown_markers:
                    report.unknown_markers.append(marker)
            elif marker not in report.cited_markers:
                report.cited_markers.append(marker)

        if claim:
            if sentence_markers:
                report.cited_sentences += 1
            else:
                report.uncited_sentences.append(sentence)

        known = [m for m in sentence_markers if m in by_marker]
        quotes = [
            quote for quote, start, _ in all_quotes
            if span_start <= start < span_end
        ]

        for quote in quotes:
            located = None
            for marker in known:
                located = locate_quote(quote, by_marker[marker])
                if located is not None:
                    break
            if located is not None:
                report.quote_spans.append(located)
                if located.match == "normalised":
                    report.notes.append(
                        f"quote {quote[:40]!r} matched only after Unicode "
                        f"normalisation, so no character offset is claimed for it"
                    )
                elif located.match == "case_folded":
                    report.notes.append(
                        f"quote {quote[:40]!r} matched only after case folding: "
                        f"the span is exact, but the source renders those "
                        f"characters with different capitalisation"
                    )
                continue

            elsewhere = [
                p.marker for p in passages
                if p.marker not in known and locate_quote(quote, p) is not None
            ]
            entry = {
                "quote": quote,
                "cited": known,
                "sentence": sentence,
            }
            metadata = _in_metadata(quote, known or list(by_marker), by_marker)
            if elsewhere:
                entry["found_in"] = elsewhere
                report.misattributed_quotes.append(entry)
            elif metadata:
                entry["found_in_metadata"] = metadata
                entry["reason"] = (
                    f"this text is the record's {metadata} — catalogue metadata "
                    f"written by the corpus editor, not words from the source or "
                    f"from any translation of it. Quoting it presents an "
                    f"editorial description as evidence, which is the Part 3 "
                    f"placeholder problem in miniature: the Vimose record's "
                    f"English title is not the Vimose inscription."
                )
                report.quoted_metadata.append(entry)
            else:
                entry["reason"] = (
                    "this text appears in no supplied passage, in either the "
                    "source language or the English. It was not copied from the "
                    "evidence."
                )
                report.unverified_quotes.append(entry)

        # A passage with no English may be cited only with a verbatim quotation
        # of its source text in the same sentence. Anything else is a claim about
        # what an untranslated passage means.
        for marker in known:
            passage = by_marker[marker]
            if passage.english.kind != "none" or not claim:
                continue
            quoted_here = any(
                locate_quote(q, passage) is not None for q in quotes
            )
            if not quoted_here:
                report.claims_on_untranslated.append(
                    {
                        "marker": marker,
                        "chunk_id": passage.chunk_id,
                        "sentence": sentence,
                        "reason": passage.english.reason,
                    }
                )

    if rendered_sources is not None:
        for marker in report.cited_markers:
            passage = by_marker[marker]
            if passage.english.kind != "machine":
                continue
            line = _block_for(rendered_sources, marker)
            if MACHINE_LABEL not in line or (passage.english.band or "") not in line:
                report.unlabelled_machine.append(marker)

    report.ok = not any(report.failures.values())
    return report


def _in_metadata(
    quote: str, markers: list[str], by_marker: dict[str, Passage]
) -> str | None:
    """Which piece of catalogue metadata a quotation came from, if any.

    The evidence block shows each passage's title and date so the model can
    frame an answer. In the first live run it quoted both — `earliest datable
    Elder Futhark runic texts` is the record's *title*, written for this corpus,
    and `c. 160-300 CE (Roman Iron Age in Scandinavia)` is its `date_text`.
    Neither is the source speaking, and neither should be reported as a
    fabrication either: the model copied them faithfully from what it was
    handed. This names the mistake it actually made.
    """
    fields = ("title", "date_text", "citation", "translation_source", "region")
    for marker in markers:
        passage = by_marker.get(marker)
        if passage is None:
            continue
        for name in fields:
            value = getattr(passage.chunk, name, None)
            if value and locate_in_text(quote, str(value)) is not None:
                return f"{name} ({marker})"
    return None


def _block_for(rendered: str, marker: str) -> str:
    """The chunk of a rendered sources block belonging to one marker."""
    pattern = re.compile(rf"^\[{re.escape(marker)}\]", re.M)
    match = pattern.search(rendered)
    if not match:
        return ""
    following = re.compile(r"^\[S\d+\]", re.M).search(rendered, match.end())
    return rendered[match.start(): following.start() if following else len(rendered)]


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render_evidence(passages: list[Passage], profiles: dict | None = None) -> str:
    """The evidence block handed to the model.

    Source text is always shown, English only where `resolve_english` allowed it.
    Where it did not, the block says so in words and says why — a model given a
    passage with a silent gap where the English should be will fill the gap.
    """
    blocks: list[str] = []
    for passage in passages:
        chunk = passage.chunk
        header = (
            f"[{passage.marker}] {chunk.title or chunk.doc_id} — {chunk.citation}"
        )
        meta = [
            f"region: {chunk.region}",
            f"language: {chunk.lang}",
            f"type: {chunk.source_type}",
        ]
        if chunk.date_text:
            meta.append(f"date: {chunk.date_text}")
        if passage.similarity is not None:
            meta.append(f"retrieval similarity: {passage.similarity:.3f}")

        lines = [header, "  " + " | ".join(meta)]
        lines.append(f"  SOURCE TEXT ({chunk.lang}):")
        lines.append(_indent(chunk.text, "    "))

        if passage.english.text:
            label = {
                "source": "ENGLISH (this source is in English)",
                "published": "ENGLISH (published translation)",
                "published_document": "ENGLISH (published translation, document-level)",
                "machine": f"ENGLISH ({MACHINE_LABEL}, "
                           f"confidence {passage.english.band})",
            }[passage.english.kind]
            lines.append(f"  {label}:")
            lines.append(_indent(passage.english.text, "    "))
        else:
            lines.append("  ENGLISH: NONE AVAILABLE.")

        lines.append(f"  HOW TO USE THIS SOURCE: {caveat_for(passage, profiles)}")
        if passage.lang_note:
            lines.append(f"  LANGUAGE NOTE: {passage.lang_note}")
        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)


def render_sources(
    passages: list[Passage],
    report: GroundingReport | None = None,
    profiles: dict | None = None,
    cited_only: bool = True,
) -> str:
    """The sources block shown beside the answer.

    Every machine translation carries the words MACHINE TRANSLATION and its band,
    here, where a reader will see them — not in a footnote and not by convention.
    `verify` reads this string back and fails the answer if either is missing, so
    the rule is enforced against the artifact rather than against the intention.
    """
    cited = set(report.cited_markers) if (report and cited_only) else None
    lines: list[str] = []
    for passage in passages:
        if cited is not None and passage.marker not in cited:
            continue
        chunk = passage.chunk
        lines.append(f"[{passage.marker}] {chunk.citation}")
        if chunk.title:
            lines.append(f"      {chunk.title} — {chunk.region}, {chunk.lang}")
        if chunk.translation_source and passage.english.kind in (
            "published", "published_document"
        ):
            lines.append(f"      translation: {chunk.translation_source}")
        if passage.english.kind == "machine":
            lines.append(
                f"      English: {MACHINE_LABEL} — confidence "
                f"{passage.english.band} ({passage.english.profile} profile)"
            )
        elif passage.english.kind == "none":
            lines.append("      English: none available; source text only")
        lines.append(f"      {caveat_for(passage, profiles)}")
        lines.append(
            f"      traceable to: {chunk.source_field} "
            f"[{chunk.char_start}:{chunk.char_end}] of {chunk.doc_id}"
        )
        lines.append("")
    return "\n".join(lines).rstrip()


def _indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line for line in text.splitlines())
