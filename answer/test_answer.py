"""Part 7 tests. No network, no database.

Run: python -m answer.test_answer

Every defect Part 6 shipped was found by running the thing, not by writing it.
These tests do not pretend to close that gap; what they do is make the *policy*
decisions executable, because those are the ones that would otherwise be true
only in a docstring:

  * a blocking flag outranks the confidence band (the Vimose rule);
  * a published translation is preferred to a machine one;
  * evidence order never depends on the band, because bands are genre-relative;
  * a quotation is verified against the source it cites, and resolved to
    absolute characters in the file on disk;
  * a sentence with no marker is not grounded;
  * a claim about an untranslated passage is rejected;
  * a machine translation never reaches a reader without its band.

Each of those has a regression guard below marked GUARD, and each guard was
verified by breaking the code it protects and watching the guard fail. A test
that has never failed is a test whose failure mode is unknown.

What these cannot catch is the standing Part 4/6 lesson, unchanged: the SQL in
answer_store.py is parsed here, never planned. `AmbiguousParameter` and its
relatives appear only against a real Postgres, and the first live run is the test
that counts.
"""

from __future__ import annotations

import re
from pathlib import Path

from answer import answer_store, assemble, cite, evidence
from answer.align import pair_chunks
from answer.confidence import Profile
from answer.evidence import (
    ChunkRecord,
    EnglishChoice,
    Passage,
    TranslationRecord,
    build_passages,
    caveat_for,
    resolve_english,
)

failures: list[str] = []


def expect(condition: bool, label: str) -> None:
    if condition:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


PROFILES = {
    "prose": Profile("prose", cos_high=0.95, cos_low=0.80, chrf_high=0.50,
                     chrf_low=0.20, calibrated=True),
    "verse": Profile("verse", cos_high=0.85, cos_low=0.65, chrf_high=0.35,
                     chrf_low=0.15, calibrated=False),
    "inscription": Profile("inscription", cos_high=0.90, cos_low=0.72,
                           chrf_high=0.40, chrf_low=0.20, calibrated=False),
}

GREEK = "56. καὶ φέρεται εἰς αὐτὰ πέπερι μονογενῶς ἐν ἑνὶ τόπῳ γεννώμενον"
RUNES = "harja\nwagnijo\nniþijo tawide\nmakija\nraunijaz\nhagiradaz"


def chunk(
    chunk_id="c1", doc_id="d1", lang="grc", text=GREEK, role="original", seq=0,
    char_start=1000, source_field="original_text_excerpt", **kwargs
) -> ChunkRecord:
    return ChunkRecord(
        chunk_id=chunk_id, doc_id=doc_id, role=role, seq=seq, lang=lang,
        text=text, citation=kwargs.pop("citation", "Periplus Maris Erythraei §56"),
        region=kwargs.pop("region", "south_asia"),
        source_type=kwargs.pop("source_type", "literary"),
        text_fidelity=kwargs.pop("text_fidelity", "verbatim_original"),
        source_field=source_field, char_start=char_start,
        char_end=char_start + len(text), **kwargs,
    )


def passage(
    marker="S1", english: EnglishChoice | None = None, similarity=0.6, **kwargs
) -> Passage:
    record = chunk(**kwargs)
    return Passage(
        marker=marker,
        chunk=record,
        english=english or EnglishChoice(kind="published", text="Pepper is brought "
                                        "to these places, grown in one region only",
                                        ground="section", attribution="Schoff 1912"),
        similarity=similarity,
        rank=1,
    )


# --------------------------------------------------------------------------
# 1. Which English a reader may see
# --------------------------------------------------------------------------

def test_english_policy() -> None:
    print("\nenglish resolution policy")

    english_chunk = chunk(lang="en", text="A bronze figurine of Roman workmanship.")
    expect(resolve_english(english_chunk).kind == "source",
           "an English chunk is its own English")

    machine = TranslationRecord(
        chunk_id="c1", translated_text="Pepper is carried thither",
        confidence_band="high", confidence_profile="prose", cos_back=0.963,
        chrf_back=0.554, translation_model="anthropic/claude-haiku-4-5-20251001",
    )

    # GUARD: published wins. Verified to fail when resolve_english consults
    # `machine` before `published_text`.
    both = resolve_english(
        chunk(), published_text="Pepper is brought to these places",
        published_ground="section", published_attribution="Schoff 1912",
        machine=machine, profiles=PROFILES,
    )
    expect(both.kind == "published",
           "GUARD a published translation is preferred to a machine one")
    expect(both.text == "Pepper is brought to these places",
           "the published text is the one shown")

    # A published translation that could not be aligned to the passage ranks
    # BELOW the machine translation, which is at least of the right passage.
    unaligned = resolve_english(
        chunk(), published_text="…the whole record…", published_ground="none",
        machine=machine, profiles=PROFILES,
    )
    expect(unaligned.kind == "machine",
           "an unaligned published translation does not outrank a passage-level "
           "machine translation")

    only_unaligned = resolve_english(
        chunk(), published_text="…the whole record…", published_ground="none",
    )
    expect(only_unaligned.kind == "published_document",
           "with no machine translation, an unaligned published one is offered "
           "as document-level")

    # GUARD: a blocking flag outranks the band. This is the Vimose rule, and the
    # row it protects is stored band='low' WITH the flag — filtering on band
    # alone would still have to decide what to do with 'low', and the point is
    # that no band is low enough. Verified to fail when resolve_english checks
    # `confidence_band` before `blocking_flags`.
    blocked = TranslationRecord(
        chunk_id="c9", translated_text="Harja. Wagnijo made this.",
        confidence_band="low", confidence_profile="inscription",
        flags=["untranslated_echo"],
    )
    result = resolve_english(chunk(lang="gmq-pro", text=RUNES), machine=blocked,
                            profiles=PROFILES)
    expect(result.kind == "none",
           "GUARD a blocked machine translation is not shown at any band")
    expect(result.text is None, "a blocked translation carries no text")
    expect("untranslated_echo" in (result.reason or ""),
           "the reason names the flag that blocked it")

    # ...and a blocked machine translation does not suppress a human one.
    with_published = resolve_english(
        chunk(lang="gmq-pro", text=RUNES), published_text="Harja (a name)",
        published_ground="document", machine=blocked, profiles=PROFILES,
    )
    expect(with_published.kind == "published_document",
           "a blocked machine translation does not hide the published gloss")

    nothing = resolve_english(chunk(lang="xpr", text="ANE mzdyzn ALHA"))
    expect(nothing.kind == "none" and nothing.text is None,
           "no published and no machine translation means no English")
    expect("translation made at answer time" in (nothing.reason or ""),
           "the reason says why nothing was translated on the spot")

    calibrated = resolve_english(chunk(), machine=machine, profiles=PROFILES)
    expect(calibrated.profile_calibrated is True,
           "the profile's calibration status travels with the choice")


# --------------------------------------------------------------------------
# 2. Bands are genre-relative
# --------------------------------------------------------------------------

def test_band_never_orders_evidence() -> None:
    print("\nbands do not order evidence")

    records = [
        (chunk(chunk_id=f"c{i}", doc_id=f"d{i}"), 0.9 - i * 0.1) for i in range(4)
    ]
    bands = ["low", "high", "medium", "high"]

    def english_map(band_list):
        return {
            record.chunk_id: EnglishChoice(
                kind="machine", text="…", band=band, profile="prose", cos_back=0.9
            )
            for (record, _), band in zip(records, band_list)
        }

    baseline = build_passages(records, english_by_chunk=english_map(bands))
    permuted = build_passages(records, english_by_chunk=english_map(bands[::-1]))

    # GUARD: verified to fail when build_passages sorts `ranked` by band.
    expect(
        [p.chunk_id for p in baseline] == [p.chunk_id for p in permuted]
        == ["c0", "c1", "c2", "c3"],
        "GUARD evidence order is retrieval order regardless of confidence band",
    )
    expect([p.marker for p in baseline] == ["S1", "S2", "S3", "S4"],
           "markers are assigned in retrieval order")

    capped = build_passages(records, english_by_chunk=english_map(bands),
                            max_sources=2)
    expect([p.marker for p in capped] == ["S1", "S2"], "max_sources truncates")


def test_caveats_are_specific() -> None:
    print("\ncaveats")

    medium = passage(english=EnglishChoice(
        kind="machine", text="…", band="medium", profile="prose",
        profile_calibrated=True, cos_back=0.937,
        attribution="anthropic/claude-haiku-4-5-20251001",
    ))
    text = caveat_for(medium, PROFILES)
    # Nine of twelve Part 6 cases banded medium. A caveat that says only
    # "medium confidence" would be attached to most of the corpus and read as
    # decoration, so it has to carry the numbers.
    expect("0.937" in text and "0.95" in text,
           "a medium caveat states the observed cosine and the threshold missed")
    expect(cite.MACHINE_LABEL in text, "a machine caveat says so in capitals")
    expect("self-consistency, not accuracy" in text,
           "the caveat repeats the Part 6 limit: the round trip is not accuracy")

    uncalibrated = passage(english=EnglishChoice(
        kind="machine", text="…", band="medium", profile="verse",
        profile_calibrated=False, cos_back=0.696,
    ))
    expect("provisional" in caveat_for(uncalibrated, PROFILES),
           "an uncalibrated profile says the band itself is provisional")

    published = passage()
    expect("Schoff 1912" in caveat_for(published, PROFILES),
           "a published translation is attributed")
    expect("section numbers" in caveat_for(published, PROFILES),
           "the alignment ground reaches the reader")

    index_ground = passage(english=EnglishChoice(
        kind="published", text="…", ground="index", attribution="Schoff 1912"))
    expect("weaker" in caveat_for(index_ground, PROFILES),
           "positional pairing is labelled weaker, as align.py labels it")

    tamil = Passage(
        marker="S1", chunk=chunk(lang="oty", text="…"),
        english=EnglishChoice(kind="machine", text="…", band="medium",
                              profile="verse", cos_back=0.696),
        similarity=0.37,
        lang_note=evidence.RETRIEVAL_LANG_NOTES["oty"],
    )
    expect("0.368" in (tamil.lang_note or ""),
           "the Old Tamil note carries the measurement it rests on")


# --------------------------------------------------------------------------
# 3. Quotations resolve to characters on disk
# --------------------------------------------------------------------------

def test_quote_location() -> None:
    print("\nquote location")

    p = passage()
    span = cite.locate_quote("πέπερι μονογενῶς", p)
    expect(span is not None, "a verbatim quote from the source is located")
    # GUARD: the whole Part 7 claim in one assertion. The chunk starts at
    # char_start in its source field, so the quote's absolute offset is
    # char_start + its offset within the chunk. Verified to fail when
    # locate_quote returns the chunk-relative offset instead.
    offset = GREEK.index("πέπερι μονογενῶς")
    expect(span.abs_start == 1000 + offset and span.abs_end == span.abs_start + len("πέπερι μονογενῶς"),
           "GUARD a quote resolves to absolute characters in the source file")
    expect(GREEK[span.abs_start - 1000: span.abs_end - 1000] == "πέπερι μονογενῶς",
           "the reported span round-trips back to the quoted characters")

    # Whitespace-insensitive, for the same reason chrF is: Literary Chinese has
    # no word spaces, so a whitespace-sensitive check would hold it and Greek to
    # different standards.
    chinese = passage(lang="lzh", text="大秦國一名犁鞬\n以在海西亦云海西國")
    expect(cite.locate_quote("大秦國一名犁鞬 以在海西", chinese) is not None,
           "quote matching survives whitespace differences")

    expect(cite.locate_quote("silk from Serica", p) is None,
           "text that is not in the passage is not located")

    english_only = passage(english=EnglishChoice(
        kind="published", text="Pepper is brought to these places",
        ground="section"))
    span_en = cite.locate_quote("brought to these places", english_only)
    expect(span_en is not None and span_en.within == "english",
           "a quote from the English is verified")
    expect(span_en.abs_start is None,
           "no on-disk character span is claimed for a translation")


# --------------------------------------------------------------------------
# 4. The grounding checks
# --------------------------------------------------------------------------

def _two_passages() -> list[Passage]:
    s1 = passage(marker="S1")
    s2 = Passage(
        marker="S2",
        chunk=chunk(chunk_id="c2", doc_id="d2", lang="lzh",
                    text="大秦國一名犁鞬", citation="Weilüe, tr. Hill",
                    region="east_asia", char_start=40),
        english=EnglishChoice(kind="machine", text="Da Qin is also called Lijian",
                              band="medium", profile="prose",
                              profile_calibrated=True, cos_back=0.899,
                              attribution="anthropic/claude-haiku-4-5-20251001"),
        similarity=0.47, rank=2,
    )
    return [s1, s2]


def test_grounding() -> None:
    print("\ngrounding checks")
    passages = _two_passages()
    sources = cite.render_sources(passages, None, PROFILES, cited_only=False)

    good = (
        "The Periplus records pepper being carried from a single growing region "
        "[S1]. Chinese sources call the Roman empire Da Qin [S2]."
    )
    report = cite.verify(good, passages, sources)
    expect(report.ok, "a fully cited answer verifies")
    expect(report.cited_markers == ["S1", "S2"], "both markers are recorded as cited")
    expect(report.coverage == 1.0, "coverage is 1.0 when every claim is cited")

    # GUARD: verified to fail when is_claim() returns False unconditionally.
    partly = (
        "The Periplus records pepper being carried from one region [S1]. "
        "Rome imported roughly fifty million sesterces of goods each year."
    )
    report = cite.verify(partly, passages, sources)
    expect(not report.ok and len(report.uncited_sentences) == 1,
           "GUARD an uncited factual sentence fails the answer")
    expect(report.coverage == 0.5, "coverage reports the proportion cited")

    expect(cite.verify("Pepper came from Limyrike [S9].", passages, sources)
           .unknown_markers == ["S9"],
           "a marker with no source behind it is caught")

    # GUARD: verified to fail when locate_quote is stubbed to return a span for
    # anything.
    invented = 'The text says "and much silk from the land of Seres" [S1].'
    report = cite.verify(invented, passages, sources)
    expect(len(report.unverified_quotes) == 1 and not report.ok,
           "GUARD a quotation absent from the evidence fails the answer")

    # A quote that exists, but not in the source it was hung on. Worse than an
    # invented one, because it survives a spot check of the corpus.
    misattributed = 'The Weilüe reads "πέπερι μονογενῶς" [S2].'
    report = cite.verify(misattributed, passages, sources)
    expect(len(report.misattributed_quotes) == 1,
           "GUARD a quote attributed to the wrong source is caught")
    expect(report.misattributed_quotes[0]["found_in"] == ["S1"],
           "the report says where the quote actually is")

    quoted = 'The passage reads "πέπερι μονογενῶς" [S1].'
    report = cite.verify(quoted, passages, sources)
    expect(report.ok and len(report.quote_spans) == 1,
           "a correctly attributed quote verifies")

    short = "In short:"
    expect(not cite.is_claim(short), "a fragment ending in a colon is not a claim")
    expect(cite.is_claim("Pepper was carried from Limyrike to Egypt"),
           "a full sentence is a claim")


def test_untranslated_sources() -> None:
    print("\nclaims on untranslated sources")

    runic = Passage(
        marker="S1",
        chunk=chunk(chunk_id="c9", doc_id="vimose", lang="gmq-pro", text=RUNES,
                    citation="Vimose finds, National Museum of Denmark",
                    region="scandinavia", char_start=0),
        english=EnglishChoice(
            kind="none", flags=["untranslated_echo"], band="low",
            reason="the machine translation of this passage is blocked by "
                   "untranslated_echo.",
        ),
        similarity=0.42, rank=1,
    )
    sources = cite.render_sources([runic], None, PROFILES, cited_only=False)

    # GUARD: this is the failure the whole part exists to prevent — a confident
    # English reading of undeciphered runes, arriving attached to a citation.
    # Verified to fail when the claims_on_untranslated block is removed.
    invented_reading = (
        "The Vimose comb bears an inscription meaning 'Harja made this comb' [S1]."
    )
    report = cite.verify(invented_reading, [runic], sources)
    expect(len(report.claims_on_untranslated) == 1 and not report.ok,
           "GUARD a claim about an untranslated passage fails the answer")

    # Quoting it verbatim is allowed: those characters are on disk.
    quoting = 'The Vimose comb carries the sequence "harja" [S1].'
    report = cite.verify(quoting, [runic], sources)
    expect(not report.claims_on_untranslated and report.ok,
           "quoting an untranslated source verbatim is allowed")
    expect(report.quote_spans[0].abs_start == RUNES.index("harja"),
           "the quotation still resolves to characters on disk")


def test_machine_translations_are_labelled() -> None:
    print("\nmachine translations reach the reader labelled")

    passages = _two_passages()
    answer = "Chinese sources call the Roman empire Da Qin [S2]."
    sources = cite.render_sources(passages, None, PROFILES, cited_only=False)

    expect(cite.MACHINE_LABEL in sources and "medium" in sources,
           "the rendered sources block names the label and the band")
    report = cite.verify(answer, passages, sources)
    expect(not report.unlabelled_machine, "a labelled machine translation passes")

    # GUARD: verified to fail when render_sources drops the band from the label.
    stripped = sources.replace(cite.MACHINE_LABEL, "English")
    report = cite.verify(answer, passages, stripped)
    expect(report.unlabelled_machine == ["S2"] and not report.ok,
           "GUARD an unlabelled machine translation fails the answer")

    evidence_block = cite.render_evidence(passages, PROFILES)
    expect(cite.MACHINE_LABEL in evidence_block,
           "the model is told which English is machine-made")
    expect("[S1]" in evidence_block and "[S2]" in evidence_block,
           "the evidence block is marker-addressed")

    no_english = Passage(
        marker="S1", chunk=chunk(lang="gmq-pro", text=RUNES),
        english=EnglishChoice(kind="none", reason="nothing available"),
    )
    block = cite.render_evidence([no_english], PROFILES)
    expect("ENGLISH: NONE AVAILABLE" in block,
           "a passage with no English says so, rather than leaving a gap to fill")


# --------------------------------------------------------------------------
# 5. Folding, prompt contract, identity
# --------------------------------------------------------------------------

def test_folding() -> None:
    print("\nfolding original and translation hits")

    original = chunk(chunk_id="grc-0", doc_id="periplus", role="original", seq=0,
                     text="56. καὶ φέρεται")
    english = chunk(chunk_id="en-0", doc_id="periplus", role="translation", seq=0,
                    lang="en", text="56. And there is brought")
    doc_passages = {"periplus": [original, english]}

    anchors, folded, published = assemble.fold_hits(
        [(english, 0.62), (original, 0.58)], doc_passages
    )
    expect(len(anchors) == 1 and anchors[0][0].chunk_id == "grc-0",
           "GUARD an original and its translation collapse into one source")
    expect(folded["grc-0"] == "en-0", "the folded translation chunk is recorded")
    expect(published["grc-0"][0] == english.text,
           "the English chunk becomes the published translation")
    expect(published["grc-0"][1] == "section",
           "the alignment ground is computed from the section markers")

    solo = chunk(chunk_id="en-only", doc_id="bm-coin", role="translation",
                 lang="en", text="A hoard of Roman denarii.")
    anchors, _, _ = assemble.fold_hits([(solo, 0.5)], {"bm-coin": [solo]})
    expect(len(anchors) == 1 and anchors[0][0].chunk_id == "en-only",
           "an English chunk with no original stands on its own")


def test_prompt_contract() -> None:
    print("\nanswer prompt contract")

    system = assemble.SYSTEM_ANSWER
    for requirement, label in (
        ("numbered sources", "the prompt restricts the model to the sources"),
        ("Use only the supplied sources", "the prompt says so again as a rule"),
        ("citation marker", "the prompt demands markers"),
        ("copy the characters exactly", "the prompt demands verbatim quotation"),
        ("Do not translate anything", "the prompt forbids answer-time translation"),
        ("NONE AVAILABLE", "the prompt names the no-English case"),
        ("machine translation", "the prompt requires machine English to be flagged in prose"),
    ):
        expect(requirement in system, label)

    expect(assemble.NO_ANSWER in system,
           "the refusal sentence is given verbatim, so `refused` can detect it")

    messages = assemble.build_messages("what came from Muziris?", "[S1] …")
    expect(len(messages) == 2 and messages[0]["role"] == "system",
           "the answer call is a fresh two-message request with no history")
    expect("[S1]" in messages[1]["content"],
           "the evidence block reaches the user turn")

    answer = assemble.AssembledAnswer(
        question="q", answer_text=assemble.NO_ANSWER, passages=[],
        grounding=cite.GroundingReport(ok=True), sources_block="", model="m",
    )
    expect(answer.refused, "a refusal is detected as one")

    expect(assemble._strip_preamble("Here is the answer: Pepper [S1].")
           == "Pepper [S1].",
           "a chat preamble is stripped rather than counted as an uncited claim")


def test_answer_identity() -> None:
    print("\nanswer identity")

    base = answer_store.answer_id("q", "haiku", "p7-answer-v1", ["a", "b"])
    expect(base == answer_store.answer_id("q", "haiku", "p7-answer-v1", ["a", "b"]),
           "the same question, model, prompt and evidence give the same id")
    # GUARD: the Part 6 lesson — a version stored but left out of the key lets a
    # new prompt destroy the evidence the old one produced. Verified to fail when
    # prompt_version is dropped from the hashed payload.
    expect(base != answer_store.answer_id("q", "haiku", "p7-answer-v2", ["a", "b"]),
           "GUARD a different prompt version is a different answer, not an overwrite")
    expect(base != answer_store.answer_id("q", "sonnet", "p7-answer-v1", ["a", "b"]),
           "a different model is a different answer")
    expect(base != answer_store.answer_id("q", "haiku", "p7-answer-v1", ["a", "c"]),
           "different evidence is a different answer")
    expect(base != answer_store.answer_id("q", "haiku", "p7-answer-v1", ["b", "a"]),
           "evidence order is part of the identity, because markers depend on it")


def test_citation_rows() -> None:
    print("\ncitation rows")

    passages = _two_passages()
    sources = cite.render_sources(passages, None, PROFILES, cited_only=False)
    report = cite.verify('Pepper appears here "πέπερι μονογενῶς" [S1].',
                         passages, sources)
    answer = assemble.AssembledAnswer(
        question="q", answer_text="…", passages=passages, grounding=report,
        sources_block=sources, model="haiku",
    )
    rows = {row["marker"]: row for row in assemble.citation_rows(answer)}

    expect(rows["S1"]["cited"] and rows["S1"]["quoted"],
           "a cited and quoted source is recorded as both")
    expect(not rows["S2"]["cited"],
           "a retrieved but uncited source is still stored, marked uncited")
    expect(rows["S1"]["char_start"] == 1000 and rows["S1"]["source_field"],
           "the citation row carries the chunk's span in its source file")
    expect(rows["S2"]["confidence_band"] == "medium",
           "a machine translation's band is stored with the citation")
    # Mirrors the answer_citations_machine_band CHECK constraint.
    expect(all(r["confidence_band"] is not None
               for r in rows.values() if r["english_kind"] == "machine"),
           "no machine citation row is written without a band")


def test_end_to_end_with_a_fake_model() -> None:
    """The whole assembly path with the chat call faked out.

    Worth having as a single test because the pieces are individually correct in
    ways that do not compose: verify() is called twice, the second time against
    the sources block that the first call's cited-marker list produced, and a
    mistake in that ordering would leave every machine translation looking
    unlabelled or every label unchecked.
    """
    print("\nend to end, fake model")

    class FakeMessage:
        def __init__(self, content): self.content = content

    class FakeChoice:
        def __init__(self, content): self.message = FakeMessage(content)

    class FakeCompletion:
        def __init__(self, content): self.choices = [FakeChoice(content)]

    class FakeClient:
        def __init__(self, reply):
            self.reply, self.calls = reply, []
            outer = self

            class Completions:
                def create(self, **kwargs):
                    outer.calls.append(kwargs)
                    return FakeCompletion(outer.reply)

            class Chat:
                completions = Completions()

            self.chat = Chat()

    passages = _two_passages()
    reply = (
        'Here is the answer: The Periplus names pepper as a cargo, "πέπερι '
        'μονογενῶς" [S1]. Chinese sources call the Roman empire Da Qin, on a '
        "machine translation of the Weilüe [S2]."
    )
    client = FakeClient(reply)
    answer = assemble.assemble("what came from Muziris?", passages,
                               client=client, profiles=PROFILES,
                               model_label="anthropic/claude-haiku-4-5-20251001")

    expect(len(client.calls) == 1, "one chat call per question")
    expect(client.calls[0]["temperature"] == 0,
           "the answer call is deterministic-as-possible, like the Part 6 calls")
    expect(not answer.answer_text.startswith("Here is"),
           "the preamble is stripped from the stored answer")
    expect(answer.ok, f"the assembled answer verifies ({answer.grounding.failures})")
    expect(cite.MACHINE_LABEL in answer.sources_block,
           "the rendered sources block labels the machine translation")
    expect("[S1]" in answer.render() and "Sources" in answer.render(),
           "render() puts the answer above its sources")
    expect(answer.grounding.quote_spans[0].abs_start == 1000 + GREEK.index("πέπερι"),
           "the end-to-end path still resolves the quote to disk")

    empty = assemble.assemble("q", [], client=client)
    expect(empty.answer_text == assemble.NO_ANSWER and len(client.calls) == 1,
           "no retrieval means no chat call and an explicit refusal")


# --------------------------------------------------------------------------
# 6. SQL — parsed, never planned
# --------------------------------------------------------------------------

def test_sql() -> None:
    print("\nSQL")

    sql = Path("scripts/schema-part7.sql").read_text(encoding="utf-8")

    expect("FROM retrievable_chunks" in sql,
           "citable_passages is built on retrievable_chunks, so held-back "
           "placeholder chunks stay uncitable by construction")
    expect(re.search(r"CREATE OR REPLACE VIEW citable_passages", sql) is not None,
           "the evidence view is idempotent")
    expect("english_kind <> 'machine' OR confidence_band IS NOT NULL" in sql,
           "the database refuses a machine citation with no band")

    # GUARD (Part 4/6, restated): a NULL-able parameter with no cast parses
    # cleanly and fails at execution with AmbiguousParameter. Verified to catch
    # the uncast form.
    queries = {
        "SELECT_BY_CHUNK_IDS": answer_store.SELECT_BY_CHUNK_IDS,
        "SELECT_DOC_PASSAGES": answer_store.SELECT_DOC_PASSAGES,
        "SELECT_CURRENT_TRANSLATIONS": answer_store.SELECT_CURRENT_TRANSLATIONS,
        "DELETE_STALE_CITATIONS": answer_store.DELETE_STALE_CITATIONS,
    }
    for name, query in queries.items():
        uncast = re.findall(r"%\((\w+)\)s(?!::)\s*IS NULL", query)
        expect(not uncast,
               f"GUARD {name}: every nullable parameter carries a cast "
               f"(uncast: {uncast})")
        arrays = re.findall(r"ANY\(%\((\w+)\)s\)", query)
        expect(not arrays,
               f"GUARD {name}: every ANY() parameter carries a ::text[] cast "
               f"(uncast: {arrays})")

    # GUARD: the primary key and the ON CONFLICT target must agree. Part 6 shipped
    # a key that omitted back_prompt_version while the upsert conflicted on the
    # narrower set, and one prompt's output silently overwrote another's. A drift
    # between the two raises only at execution time, which parsing cannot reach.
    for table, statement in (
        ("answer_citations", answer_store.UPSERT_CITATION),
        ("answers", answer_store.UPSERT_ANSWER),
    ):
        pk = _primary_key_columns(sql, table)
        conflict = _conflict_columns(statement)
        expect(pk and pk == conflict,
               f"GUARD {table}: ON CONFLICT {sorted(conflict)} matches the "
               f"primary key {sorted(pk)}")

    # Every optional upsert parameter must have a default in write_answer, or a
    # caller that omits one gets a psycopg KeyError at execution time only.
    supplied = set(re.findall(r"%\((\w+)\)s", answer_store.UPSERT_CITATION))
    defaulted = {
        "answer_id", "marker", "chunk_id", "doc_id", "english_kind",
        "source_field", "char_start", "char_end",
    }
    row_keys = set(assemble.citation_rows(
        assemble.AssembledAnswer(
            question="q", answer_text="", passages=_two_passages(),
            grounding=cite.GroundingReport(), sources_block="", model="m",
        )
    )[0]) | {"answer_id"}
    expect(supplied <= row_keys | defaulted,
           f"citation_rows supplies every upsert parameter "
           f"(missing: {sorted(supplied - row_keys - defaulted)})")

    try:
        import sqlglot

        for statement in sqlglot.parse(sql, read="postgres"):
            pass
        for name, query in queries.items():
            sqlglot.parse_one(query, read="postgres")
        sqlglot.parse_one(answer_store.UPSERT_ANSWER, read="postgres")
        sqlglot.parse_one(answer_store.UPSERT_CITATION, read="postgres")
        expect(True, "schema and queries parse as PostgreSQL")
    except ImportError:
        print("  skip sqlglot not installed (pip install -r requirements-dev.txt)")
    except Exception as exc:  # noqa: BLE001
        expect(False, f"schema and queries parse as PostgreSQL ({exc})")


def _primary_key_columns(sql: str, table: str) -> set[str]:
    body = re.search(
        rf"CREATE TABLE IF NOT EXISTS {table} \((.*?)\n\);", sql, re.S
    )
    if not body:
        return set()
    inline = re.search(r"(\w+)\s+text\s+PRIMARY KEY", body.group(1))
    if inline:
        return {inline.group(1)}
    declared = re.search(r"PRIMARY KEY \(([^)]*)\)", body.group(1), re.S)
    if not declared:
        return set()
    return {c.strip() for c in declared.group(1).split(",") if c.strip()}


def _conflict_columns(statement: str) -> set[str]:
    match = re.search(r"ON CONFLICT \(([^)]*)\)", statement, re.S)
    if not match:
        return set()
    return {c.strip() for c in match.group(1).split(",") if c.strip()}


# --------------------------------------------------------------------------
# 14. The first live run (2026-08-10)
#
# Five questions, five exit-1s, and four of the five failures were this file's
# fault rather than the model's. One root cause: sentences were split inside
# quotations, and quotations were then extracted per sentence, so each fragment
# held an odd number of quote marks and the regex paired the close of one
# quotation with the open of the next. The verbatim answer text is kept here —
# not a reduction of it — because a reduction is a guess about which detail
# mattered, and the first live run is the only evidence available of what a real
# answer looks like.
# --------------------------------------------------------------------------

# Split at the period in `c. 160-300 CE`, mid-quotation.
LIVE_VIMOSE = (
    'The sources retrieved do not answer this question. The sources do provide '
    'information about the Vimose inscriptions: they are "earliest datable '
    'Elder Futhark runic texts" from "c. 160-300 CE (Roman Iron Age in '
    'Scandinavia)," and "several inscriptions remain only partially '
    'deciphered," with some readings offered as "likely" or "possibly" rather '
    'than certain translations [S3].'
)

# Split at the ellipsis in `for the Berbers...`, also mid-quotation, which left
# the Greek quotation unpaired and fired claims_on_untranslated falsely.
LIVE_AKSUM = (
    'The sources do describe Roman trade with Aksum: "There are imported into '
    'these places, undressed cloth made in Egypt for the Berbers... wine of '
    'Laodicea and Italy, not much" [S1], and "Φέρεται δὲ ἀπὸ τῶν τόπων '
    'ἐλέφας" [S2].'
)

# `... toward Egypt. [S6]` orphaned the marker into a fragment of its own, so a
# correctly cited quotation was reported misattributed.
LIVE_MUZIRIS = (
    'A Tamil literary text describes Yavana vessels at Muciri "arriving with '
    'gold and departing with pepper." [S5] The Muziris Papyrus documents '
    'shipments of "Gangetic nard" toward Egypt. [S6]'
)


def test_live_run_defects() -> None:
    print("\nfirst live run: sentence splitting and quote extraction")

    expect(
        not any(s.rstrip().endswith('"c.') for s in cite.split_sentences(LIVE_VIMOSE)),
        "the live Vimose answer is no longer cut at `c. `",
    )

    # Two independent mechanisms stop that cut, so each needs a case only it
    # protects — otherwise a mutation disabling either one changes nothing and
    # the guard is untested. The mutation run found exactly this.
    #
    # GUARD: verified to fail when _in_quote_mask is stubbed to all-False. An
    # ellipsis inside a quotation is not an abbreviation, so only the
    # quotation-tracking stops it.
    ellipsis = 'The text reads "cloth for the Berbers... wine of Laodicea" [S1].'
    expect(
        len(cite.split_sentences(ellipsis)) == 1,
        "GUARD a quotation containing an ellipsis is not split in two",
    )
    # GUARD: verified to fail when the _is_abbreviation check is disabled. This
    # one is outside any quotation, so only the abbreviation list stops it.
    dated = "The comb is dated c. 160 CE by its excavators [S3]."
    expect(
        len(cite.split_sentences(dated)) == 1,
        "GUARD a sentence is not split after an abbreviation",
    )

    quotes = cite.extract_quotes(LIVE_VIMOSE)
    # GUARD: verified to fail against per-sentence extraction, which returned
    # 'with some readings offered as', 'and' and 'or' — the prose *between*
    # quotations — and missed the quotations themselves.
    expect(
        "likely" in quotes and "possibly" in quotes
        and "earliest datable Elder Futhark runic texts" in quotes,
        "GUARD every real quotation in the live answer is extracted",
    )
    # Not marked GUARD: no single mutation isolates it, because global
    # extraction makes the parity correct by construction. The falsifiable
    # version of this claim is the Aksum case below, which runs through verify().
    expect(
        not any(q in {"or", "and", "with some readings offered as"} for q in quotes),
        "the prose between two quotations is not taken as a quotation",
    )

    # GUARD: belt and braces on top of the splitter fix. Verified to fail when
    # the function-word floor is removed from _is_substantive.
    expect(
        cite.extract_quotes('the readings are given as "and" in the catalogue') == [],
        "GUARD a bare function word is never treated as a quotation",
    )
    expect(cite.extract_quotes('the notice names "大秦"') == ["大秦"],
           "the length floor is script-aware: two Han characters are a quotation")

    # The Aksum failure: the Greek was quoted verbatim, which is exactly what
    # citing an untranslated passage requires, and the check fired anyway
    # because the quotation was never extracted.
    greek = "Φέρεται δὲ ἀπὸ τῶν τόπων ἐλέφας"
    expect(greek in cite.extract_quotes(LIVE_AKSUM),
           "the Greek quotation survives an ellipsis earlier in the answer")

    untranslated = Passage(
        marker="S2",
        chunk=chunk(chunk_id="c2", text=greek, char_start=1170),
        english=EnglishChoice(kind="none", reason="no English exists"),
        similarity=0.5, rank=2,
    )
    english_side = passage(marker="S1", english=EnglishChoice(
        kind="published", ground="section",
        text='There are imported into these places, undressed cloth made in '
             'Egypt for the Berbers... wine of Laodicea and Italy, not much'))
    report = cite.verify(LIVE_AKSUM, [english_side, untranslated])
    # GUARD: verified to fail when extract_quotes is reverted to per-sentence.
    expect(
        not report.claims_on_untranslated,
        "GUARD quoting an untranslated passage verbatim satisfies the rule",
    )

    # GUARD: verified to fail against the old splitter, which cut `[S6]` off
    # into a fragment and left 'Gangetic nard' attributed to S5.
    sentences = cite.split_sentences(LIVE_MUZIRIS)
    holding = [s for s in sentences if "Gangetic nard" in s]
    expect(
        len(holding) == 1 and "[S6]" in holding[0],
        "GUARD a marker after the full stop stays with the sentence it cites",
    )

    # And the refusal, which failed itself in three answers out of five.
    refusal = cite.verify(cite.REFUSAL_SENTENCE, [])
    # GUARD: verified to fail when the exemption in is_claim() is removed.
    expect(refusal.ok and not refusal.uncited_sentences,
           "GUARD the refusal sentence is not an uncited claim")
    expect(
        cite.is_claim("Pepper was carried from Limyrike to Egypt every July"),
        "the exemption is for the refusal only, not for uncited claims at large",
    )

    # A quotation from a published translation resolves to disk, because the
    # translation is a chunk of the same seed record with its own field and
    # offsets. Across all five live answers, not one quotation resolved.
    english_text = "Pepper is brought to these places, grown in one region only"
    translation_record = chunk(
        chunk_id="en-1", lang="en", role="translation", text=english_text,
        char_start=2400, source_field="reference_translation",
    )
    with_disk = Passage(
        marker="S1", chunk=chunk(),
        english=EnglishChoice(kind="published", text=english_text,
                              ground="section"),
        translation_chunk=translation_record, similarity=0.6, rank=1,
    )
    span = cite.locate_quote("grown in one region only", with_disk)
    # GUARD: verified to fail when locate_quote drops the translation chunk and
    # returns abs_start=None for every English match.
    expect(
        span is not None and span.within == "english"
        and span.abs_start == 2400 + english_text.index("grown in one region only"),
        "GUARD a quote from a published translation resolves to characters on disk",
    )
    expect(span.source_field == "reference_translation",
           "the span names the translation's own field, not the original's")

    # ----------------------------------------------------------------
    # Second live run: four "fabrications" that were nothing of the kind.
    # Verbatim from the corpus, so the test fails if the seed text changes.
    # ----------------------------------------------------------------

    akananuru_en = (
        "...the city where the beautiful vessels, the masterpieces of the "
        "Yavanas [Ionians/Greeks-Romans], stir white foam on the Culli "
        "[Periyar], a river of the Chera, arriving with gold and departing "
        "with pepper—when that Muciri, brimming with prosperity, was besieged "
        "by the din of war."
    )
    tamil = Passage(
        marker="S1", chunk=chunk(lang="oty", text="யவனர் தந்த வினைமாண் நன்கலம்"),
        english=EnglishChoice(kind="published", text=akananuru_en, ground="index"),
        similarity=0.44, rank=1,
    )
    # GUARD: verified to fail when the edge-punctuation strip is removed. The
    # source reads `pepper—`; the model wrote `pepper."`, pulling the terminal
    # period inside the marks. That is a quoting convention, not a fabrication.
    # `match == "exact"` matters: the NFC fallback would also call this verified,
    # but it claims no character offset, and a quotation that is verified without
    # a span is a weaker result than this one deserves.
    span_punct = cite.locate_quote(
        "arriving with gold and departing with pepper.", tamil)
    expect(
        span_punct is not None and span_punct.match == "exact",
        "GUARD terminal punctuation added to a quotation does not fabricate it",
    )

    hou_hanshu_en = (
        "This was the very first time there was [direct] communication "
        "[between the two countries]. The tribute brought was neither precious "
        "nor rare, raising suspicion that the accounts [of the 'envoys'] might "
        "be exaggerated."
    )
    chinese = Passage(
        marker="S1", chunk=chunk(lang="lzh", text="大秦王安敦遣使自日南徼外獻象牙"),
        english=EnglishChoice(kind="published", text=hou_hanshu_en, ground="index"),
        translation_chunk=chunk(
            chunk_id="en-hh", lang="en", role="translation", text=hou_hanshu_en,
            char_start=2000, source_field="reference_translation",
        ),
        similarity=0.51, rank=1,
    )
    # GUARD: verified to fail when the case-folded fallback is removed. The
    # source reads `The tribute`; the model lowercased it to fit mid-sentence.
    span_case = cite.locate_quote(
        "the tribute brought was neither precious nor rare", chinese)
    expect(span_case is not None and span_case.match == "exact",
           "GUARD a quotation lowercased to fit a sentence is still verified")
    # A case-folded match must not shift the offsets: _fold is length-preserving
    # precisely so the index map stays truthful.
    expect(
        hou_hanshu_en[span_case.abs_start - 2000: span_case.abs_end - 2000]
        == "The tribute brought was neither precious nor rare",
        "the span round-trips to the source's own capitalisation",
    )

    # And the one real fabrication in the run, which must still fail.
    expect(
        cite.locate_quote("outer walls of the city made of stone", chinese) is None,
        "text absent from the source is still not located",
    )

    # Catalogue metadata is not evidence. The Vimose record's title was written
    # for this corpus; quoting it presents an editorial description as a source,
    # which is the Part 3 placeholder problem one layer up.
    titled = passage(
        marker="S1",
        title="The Vimose inscriptions — earliest datable Elder Futhark runic texts",
    )
    metadata_report = cite.verify(
        'They are "earliest datable Elder Futhark runic texts" [S1].', [titled]
    )
    # GUARD: verified to fail when the metadata branch is removed from verify().
    expect(
        len(metadata_report.quoted_metadata) == 1
        and not metadata_report.unverified_quotes,
        "GUARD quoting the record's title is named as metadata, not fabrication",
    )
    expect("title (S1)" in metadata_report.quoted_metadata[0]["found_in_metadata"],
           "the report names which metadata field was quoted")
    expect(not metadata_report.ok,
           "quoting metadata still fails the answer")

    # Was `endswith("v3")`, which pinned a version rather than the property that
    # matters and had to be edited every time the prompt moved. What must hold is
    # that the running prompt is a REGISTERED one: until Part 8 the version
    # string was bumped while the prose was edited in place, so the archive named
    # three prompts and the repository held one, and "run v2 again" was not a
    # reproducible instruction.
    expect(assemble.ANSWER_PROMPT_VERSION in assemble.ANSWER_PROMPTS,
           "the running prompt version is registered, so it can be re-run")
    expect(assemble.SYSTEM_ANSWER
           == assemble.ANSWER_PROMPTS[assemble.ANSWER_PROMPT_VERSION],
           "SYSTEM_ANSWER is the registered text, not a second copy of it")
    texts = list(assemble.ANSWER_PROMPTS.values())
    expect(len(set(texts)) == len(texts),
           "GUARD no two registered prompt versions share a text — identical "
           "texts under different names would make the version meaningless")

    # Rule 4 forbids saying what an untranslated passage MEANS, and it does so
    # in every registered version — that is the invariant, and it is where the
    # restriction belongs.
    for version, text in assemble.ANSWER_PROMPTS.items():
        expect("ENGLISH: NONE AVAILABLE" in text
               and "you may NOT say what it means" in text,
               f"{version}: rule 4 forbids reading an untranslated passage")

    # GUARD, and the Part 8 result. v3 and v4 added a rule 6 clause restricting
    # which sources the post-refusal sentence may name. It duplicated the
    # `claims_on_untranslated` CHECK, which already existed and costs nothing —
    # and it cost the Vimose question 3/3 under v3 and 3/3 under v4, because the
    # model read it as licence to retreat from any English it judged thin. The
    # running prompt must not carry it back.
    running = assemble.ANSWER_PROMPTS[assemble.ANSWER_PROMPT_VERSION]
    expect("Cite only sources you can read" not in running,
           "GUARD the running prompt does not ask the model to judge "
           "readability — four prompt versions broke on rules that did")
    expect("do not name a source whose English block reads" not in running,
           "GUARD the running prompt does not restrict the post-refusal "
           "sentence; the check does that job without costing an answer")
    expect(hasattr(cite.GroundingReport(), "claims_on_untranslated"),
           "the check the rule duplicated still exists, and is where the "
           "restriction is enforced")

    # Both losing versions are kept verbatim, so the comparison can be re-run
    # rather than reconstructed a second time.
    expect("Cite only sources you can read"
           in assemble.ANSWER_PROMPTS["p7-answer-v3"],
           "v3's text is kept verbatim")
    expect("however partial, hedged or uncertain"
           in assemble.ANSWER_PROMPTS["p7-answer-v4"],
           "v4's text is kept verbatim, including the narrowing that did not work")
    expect("were written by this corpus's editors" in assemble.SYSTEM_ANSWER,
           "the prompt tells the model the header line is not quotable")

    machine_only = Passage(
        marker="S1", chunk=chunk(),
        english=EnglishChoice(kind="machine", text=english_text, band="medium"),
        translation_chunk=translation_record, similarity=0.6, rank=1,
    )
    expect(
        cite.locate_quote("grown in one region only", machine_only).abs_start is None,
        "a machine translation still claims no span — it is not in any file",
    )


# --------------------------------------------------------------------------
# 15. Section alignment when one side splits further than the other
#
# Found by the fourth live run. `africa-03-periplus-adulis` holds Greek §4-§6
# against Schoff's English for the same three sections — but Schoff's §4 is
# twice the length of the Greek, so it becomes three chunks and only the first
# carries a marker. align.py required a marker on *every* chunk, so one long
# section disabled section alignment for the whole record, and §6 — the passage
# that says what Aksum traded — resolved as ENGLISH: NONE AVAILABLE.
# --------------------------------------------------------------------------

def test_section_alignment() -> None:
    print("\nsection alignment across a split translation")

    greek = [
        chunk(chunk_id="g4", seq=0, char_start=0, text="4. Μετὰ δὲ τὴν Πτολεμαΐδα"),
        chunk(chunk_id="g6", seq=1, char_start=400,
              text="6. Προχωρεῖ δὲ εἰς τοὺς τόπους τούτους ἱμάτια"),
    ]

    def english(chunk_id, seq, text, char_start):
        return chunk(chunk_id=chunk_id, seq=seq, role="translation", lang="en",
                     text=text, char_start=char_start,
                     source_field="reference_translation")

    first = english("e4a", 0, "§4 Below Ptolemais of the Hunts", 0)
    # Two characters of dropped whitespace between the chunks, as the chunker
    # leaves them.
    second = english("e4b", 1, "Opposite Mountain Island, twenty stadia from shore",
                     first.char_end + 2)
    third = english("e6", 2, "§6 There are imported into these places",
                    second.char_end + 2)

    pairs = pair_chunks(greek, [first, second, third])
    # GUARD: verified to fail when label inheritance is removed from
    # _inherited_labels, which is the pre-fix behaviour.
    expect(
        [p.ground for p in pairs] == ["section", "section"],
        "GUARD a section split into several chunks still aligns by section",
    )
    merged = pairs[0].translation
    expect(
        "Opposite Mountain Island" in merged.text,
        "the whole section is supplied, not merely its first chunk",
    )

    # The arithmetic that makes the merge safe: text taken from a later member
    # chunk must still resolve to its true offset in the field on disk.
    offset = cite.locate_in_text("Opposite Mountain Island", merged.text)
    # GUARD: verified to fail when the inter-chunk gap is filled with nothing
    # instead of the characters that were dropped.
    expect(
        merged.char_start + offset[0] == second.char_start,
        "GUARD a merged section keeps exact offsets for its later chunks",
    )
    # Found by the dry run after the merge landed: the merged section carries
    # only its first member's chunk_id, so fold_hits treated the later members
    # as orphans and showed them as separate sources repeating what the first
    # had already said — the double-counting fold_hits exists to prevent.
    expect(
        [m.chunk_id for m in pairs[0].members] == ["e4a", "e4b"],
        "the pair records every chunk its translation was merged from",
    )
    anchors, folded, published = assemble.fold_hits(
        [(greek[0], 0.56), (second, 0.49)],
        {"d1": greek + [first, second, third]},
    )
    # GUARD: verified to fail when fold_hits maps only the merged chunk's id.
    expect(
        len(anchors) == 1 and anchors[0][0].chunk_id == "g4",
        "GUARD a later chunk of a merged section folds into its original",
    )

    # Two texts numbered 1..n independently must not align by coincidence.
    unrelated = pair_chunks(
        [chunk(chunk_id="a", seq=0, text="1. πρῶτον")],
        [english("b", 0, "§9 something else entirely", 0)],
    )
    # It falls back to positional pairing, which align.py labels as weaker — but
    # it must not claim the sources stated the pairing themselves.
    expect(unrelated[0].ground == "index",
           "non-corresponding section numbers never claim section alignment")


# --------------------------------------------------------------------------

def main() -> int:
    print("Part 7 offline tests — no network, no database")
    test_english_policy()
    test_band_never_orders_evidence()
    test_caveats_are_specific()
    test_quote_location()
    test_grounding()
    test_untranslated_sources()
    test_machine_translations_are_labelled()
    test_folding()
    test_prompt_contract()
    test_answer_identity()
    test_citation_rows()
    test_end_to_end_with_a_fake_model()
    test_sql()
    test_live_run_defects()
    test_section_alignment()

    print()
    if failures:
        print(f"{len(failures)} failure(s):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("all Part 7 offline checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
