"""Part 6 tests. No network, no database.

Run: python -m answer.test_translate

What is worth catching before spending model calls:

  * the back-translation seeing the original (the score would then measure
    leakage, and it would look like success);
  * a chat preamble being kept as if it were translation output;
  * chrF being wrong, or being quietly whitespace-dependent — which would put
    Literary Chinese and Greek on different footings;
  * a model handing back the source untranslated and scoring a perfect round
    trip for it;
  * a gold-set typo silently disabling an assertion;
  * the Part 6 SQL drifting from the dict the upsert is called with.

What these tests cannot catch is the Part 4 lesson, restated: SQL here is only
parsed, never planned. Anything with a NULL-able parameter needs one execution
against the real database before it counts as working.
"""

from __future__ import annotations

from dataclasses import dataclass

import json
import re
import tempfile
from pathlib import Path

from answer import align, confidence, store, translate

failures: list[str] = []


def expect(condition: bool, label: str) -> None:
    if condition:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


# --------------------------------------------------------------------------
# Fake chat client
# --------------------------------------------------------------------------

class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeCompletion:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


class FakeChat:
    def __init__(self, outer):
        self.completions = outer


class FakeClient:
    """Returns canned responses and records every request."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls: list[dict] = []
        self.chat = FakeChat(self)

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if not self.responses:
            raise AssertionError("FakeClient ran out of responses")
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return FakeCompletion(item)


GREEK = "56. Πλεῖ δὲ εἰς τὰ ἐμπόρια ταῦτα μεγάλα πλοῖα διὰ τὸ πλῆθος τοῦ πεπέρεως."


def test_prompt_contract() -> None:
    print("\nprompt construction")

    forward = translate.build_forward_messages(GREEK, "grc")
    expect(len(forward) == 2 and forward[0]["role"] == "system",
           "forward messages are a system + user pair")
    expect("Ancient Greek" in forward[1]["content"],
           "forward prompt names the source language, not just its code")
    expect(GREEK in forward[1]["content"], "forward prompt carries the passage")
    expect("<translation>" in forward[0]["content"],
           "forward prompt states the output contract")

    # THE contamination guard. If the original can reach the back-translation,
    # the round trip stops being evidence about the forward translation.
    english = "Large ships sail to these markets because of the quantity of pepper."
    back = translate.build_back_messages(english, "grc")
    payload = json.dumps(back, ensure_ascii=False)
    expect(GREEK not in payload, "back-translation prompt does not contain the original")
    expect("πέπερι" not in payload and "Πλεῖ" not in payload,
           "no fragment of the Greek leaks into the back-translation prompt")
    expect(english in payload, "back-translation prompt carries the English")

    parthian = translate.build_back_messages(english, "xpr")
    expect("transliteration" in parthian[0]["content"].lower(),
           "back-translating into a romanised language asks for transliteration")

    # The v1 bug: nothing told the model which script to answer in for a
    # language stored in its own characters, and on Old Tamil it chose
    # romanisation. chrF then compared two alphabets and returned 0.004.
    for code, script in (("oty", "tamil"), ("grc", "greek"), ("lzh", "chinese")):
        system = translate.build_back_messages(english, code)[0]["content"].lower()
        expect(script in system and "do not romanise" in system,
               f"back-translating into {code} demands its own script, not romanisation")
    expect("transliteration" not in translate.build_back_messages(
        english, "grc")[0]["content"].lower(),
        "Greek is not asked for in transliteration — it has its own script here")
    expect(translate.BACK_PROMPT_VERSION != translate.PROMPT_VERSION
           and translate.BACK_PROMPT_VERSION.endswith("v2"),
           "the back prompt version was bumped, so v1 rows stay distinguishable")

    unknown = translate.build_forward_messages(GREEK, "zzz")
    expect("zzz" in unknown[1]["content"],
           "an unknown language code is passed through rather than guessed at")


def test_response_parsing() -> None:
    print("\nresponse parsing")

    text, notes = translate.parse_translation(
        "<translation>Large ships sail here.</translation>"
    )
    expect(text == "Large ships sail here." and not notes, "clean tagged response")

    text, notes = translate.parse_translation(
        "Here is the translation:\n\nLarge ships sail here."
    )
    expect(text == "Large ships sail here.", "preamble stripped when tags are missing")
    expect(any("no <translation> tags" in n for n in notes),
           "a broken output contract is reported, not hidden")

    text, _ = translate.parse_translation(
        "<translation>53. A</translation>\n<translation>54. B</translation>"
    )
    expect(text == "53. A\n\n54. B", "multiple blocks are joined in order")

    text, notes = translate.parse_translation("<translation>truncated here")
    expect(text == "truncated here" and any("truncated" in n for n in notes),
           "an unclosed tag is recovered and flagged as possibly truncated")

    text, notes = translate.parse_translation("")
    expect(text == "", "empty response yields empty text")


def test_chat_calls() -> None:
    print("\nchat calls")

    client = FakeClient(["<translation>Large ships sail here.</translation>"])
    result = translate.translate_to_english(GREEK, "grc", client=client)
    expect(result.text == "Large ships sail here.", "forward translation returned")
    expect(result.target_lang == "en" and result.source_lang == "grc",
           "direction recorded on the result")
    expect(result.prompt_version == translate.PROMPT_VERSION,
           "prompt version travels with the translation")
    expect(client.calls[0]["temperature"] == 0,
           "temperature is 0 — a translation harness must be reproducible")

    client = FakeClient([
        RuntimeError("rate limit exceeded (429)"),
        "<translation>ok</translation>",
    ])
    slept: list[float] = []
    result = translate.translate_to_english(
        GREEK, "grc", client=client, sleep=slept.append
    )
    expect(result.text == "ok" and result.retries == 1, "rate limit is retried")
    expect(slept and slept[0] >= 20,
           "rate-limit backoff waits out a full window, not 2 seconds")

    client = FakeClient([RuntimeError("Connection refused")])
    try:
        translate.translate_to_english(GREEK, "grc", client=client, sleep=lambda s: None)
        expect(False, "a dead gateway raises TranslationError")
    except translate.TranslationError as exc:
        expect("gateway" in str(exc).lower(),
               "a dead gateway raises TranslationError naming the gateway")

    try:
        translate.translate_to_english("   ", "grc", client=FakeClient([]))
        expect(False, "empty input is rejected before an API call")
    except translate.TranslationError:
        expect(True, "empty input is rejected before an API call")


# --------------------------------------------------------------------------
# chrF
# --------------------------------------------------------------------------

def test_chrf() -> None:
    print("\nchrF")

    expect(confidence.chrf("abcdef", "abcdef") == 1.0, "identical strings score 1.0")
    expect(confidence.chrf("abcdef", "uvwxyz") == 0.0, "disjoint strings score 0.0")
    expect(confidence.chrf("", "abc") == 0.0, "empty hypothesis scores 0.0")
    expect(confidence.chrf("abc", "") == 0.0, "empty reference scores 0.0")

    partial = confidence.chrf("the quick brown fox", "the quick brown cat")
    expect(0.5 < partial < 1.0, f"partial overlap scores between (got {partial:.3f})")

    # Hand-computed: hyp "abc", ref "abd". Whitespace removed, n=1..3.
    #   n=1 matches {a,b} of 3 -> p=r=2/3
    #   n=2 matches {ab} of 2   -> p=r=1/2
    #   n=3 matches {} of 1     -> p=r=0
    #   avg p = avg r = (2/3 + 1/2 + 0)/3 = 0.38888...
    #   F(beta) with p == r is just p.
    manual = confidence.chrf("abc", "abd", max_n=3)
    expect(abs(manual - 0.3888888) < 1e-6,
           f"chrF matches a hand-computed value (got {manual:.6f})")

    # Whitespace independence matters here more than in ordinary MT: Literary
    # Chinese has no word spaces, so a whitespace-sensitive metric would score
    # scripts on different footings.
    spaced = confidence.chrf("大秦 國 一號 犂靬", "大秦國一號犂靬")
    expect(spaced > 0.99, f"whitespace does not change the score (got {spaced:.3f})")

    # beta=2 weights recall: dropping half the source should hurt more than
    # padding the output with extra words.
    short = confidence.chrf("the quick", "the quick brown fox")
    long = confidence.chrf("the quick brown fox jumps over", "the quick brown fox")
    expect(short < long, "beta=2 punishes omission more than addition")

    expect(confidence.chrf("ab", "ab", max_n=6) == 1.0,
           "strings shorter than max_n still score, using the orders that exist")


def test_cosine() -> None:
    print("\ncosine")
    expect(abs(confidence.cosine([1, 0], [1, 0]) - 1.0) < 1e-9, "identical vectors")
    expect(abs(confidence.cosine([1, 0], [0, 1])) < 1e-9, "orthogonal vectors")
    expect(abs(confidence.cosine([2, 0], [5, 0]) - 1.0) < 1e-9, "magnitude ignored")
    expect(confidence.cosine([0, 0], [1, 1]) == 0.0, "zero vector is 0, not an error")
    try:
        confidence.cosine([1, 0], [1, 0, 0])
        expect(False, "mismatched dimensions raise")
    except ValueError:
        expect(True, "mismatched dimensions raise")


# --------------------------------------------------------------------------
# Scoring and bands
# --------------------------------------------------------------------------

PROSE = confidence.Profile("prose", cos_high=0.75, cos_low=0.55,
                           chrf_high=0.45, chrf_low=0.25)


def test_scoring() -> None:
    print("\nconfidence scoring")

    good = confidence.score(
        original="Μουζιρὶς καὶ Νέλκυνδα",
        forward_en="Muziris and Nelkynda",
        back_translated="Μουζιρὶς καὶ Νέλκυνδα",
        profile=PROSE, cos_back=0.9,
    )
    expect(good.band == "high", "high cosine and high chrF -> high band")
    expect(good.trustworthy, "a high band with no blocking flags is trustworthy")

    paraphrase = confidence.score(
        original="Μουζιρὶς καὶ Νέλκυνδα ἐμπόρια",
        forward_en="Muziris and Nelkynda, the markets",
        back_translated="τὰ ἐμπορεῖα Μουζειρὶ",
        profile=PROSE, cos_back=0.88,
    )
    expect(paraphrase.band == "medium",
           "high meaning with low wording is capped at medium, not called high")
    expect("semantic_ok_lexical_low" in paraphrase.flags,
           "the paraphrase pattern is flagged by name")

    # The failure that would otherwise look like a perfect result: the model
    # returns the source unchanged, so the round trip is trivially exact.
    echo = confidence.score(
        original=GREEK, forward_en=GREEK, back_translated=GREEK,
        profile=PROSE, cos_back=1.0,
    )
    expect("untranslated_echo" in echo.flags,
           "a source handed back untranslated is flagged")
    expect(echo.band == "low", "an echo scores low however perfect its round trip")
    expect(not echo.trustworthy, "an echo is never trustworthy")

    refusal = confidence.score(
        original=GREEK,
        forward_en="I'm sorry, I cannot read this inscription.",
        back_translated="…", profile=PROSE, cos_back=0.9,
    )
    expect("refusal_suspected" in refusal.flags, "a refusal is flagged, not scored")
    expect(refusal.band == "low", "a refusal cannot reach a passing band")

    # The false pass from the first live run, verbatim: Tamil-script source,
    # romanised back-translation, chrF 0.004, cosine 0.573 — which is neither
    # high enough to trip semantic_ok_lexical_low nor low enough to fail a
    # floor, so it was reported as a quiet 'medium' with no flags at all.
    tamil = "சிறுபுன் சிதலை சேண்முயன்று எடுத்த நெடுஞ்செம் புற்றத்து"
    romanised = "Cīriya kalam āṟṟiya teṟkkaḷ tōḷ-k-koṇṭu nīḷiya vēḷḷai cempoṉ"
    mismatch = confidence.score(
        original=tamil, forward_en="Small fragments of broken pottery were picked up",
        back_translated=romanised, profile=PROSE, cos_back=0.573,
    )
    expect("script_mismatch" in mismatch.flags,
           "a romanised back-translation of a native-script source is flagged")

    # Run 2's version of the same failure: the back-translation came back in
    # DEVANAGARI against a Tamil source. A latin/non-latin test sees "non-Latin
    # on both sides" and says nothing, so the check has to compare scripts.
    devanagari = "सिऱिय पॊडिन्द कुवळै टुकडे एडुत्तु कळ नीळ वेळि मुरै मुडि अवळि तिरि"
    wrong_script = confidence.score(
        original=tamil, forward_en="Small fragments of broken pottery",
        back_translated=devanagari, profile=PROSE, cos_back=0.660,
    )
    expect("script_mismatch" in wrong_script.flags,
           "Devanagari answering a Tamil source is flagged, not just romanisation")
    expect(confidence.dominant_script(tamil) == "TAMIL"
           and confidence.dominant_script(devanagari) == "DEVANAGARI"
           and confidence.dominant_script(GREEK) == "GREEK"
           and confidence.dominant_script("大秦國一號犂靬") == "CJK"
           and confidence.dominant_script("az man Mazdēsn") == "LATIN",
           "dominant_script identifies each script family in the corpus")
    expect(confidence.dominant_script("123 — ,.") is None,
           "text with no letters has no dominant script, and is not a mismatch")
    expect(mismatch.band == "low",
           "a script mismatch cannot report a passing band — the score is not "
           "measuring translation quality")
    expect(not mismatch.trustworthy, "a script mismatch is never trustworthy")

    # ...and the mirror image must NOT fire, or every transliterated source in
    # the corpus (ŠKZ, Sabaic, the runes) would be blocked wrongly.
    both_latin = confidence.score(
        original="ANE mzdyzn ALHA šhypwhr MLKYN MLKA",
        forward_en="I, the Mazda-worshipping lord Shapur, king of kings",
        back_translated="az man Mazdēsn bay Šābuhr šāhān šāh",
        profile=PROSE, cos_back=0.897,
    )
    expect("script_mismatch" not in both_latin.flags,
           "a romanised source with a romanised back-translation is not a mismatch")

    greek_pair = confidence.score(
        original=GREEK, forward_en="Large ships sail to these markets",
        back_translated="Πλοῖα μεγάλα πλεῖ εἰς τὰ ἐμπόρια",
        profile=PROSE, cos_back=0.9,
    )
    expect("script_mismatch" not in greek_pair.flags,
           "Greek against Greek is not a mismatch")

    # Measured on 2026-08-10: three runs of a 52-character Chinese source gave
    # chrF 0.213-0.306, while 476-919 character sources moved by 0.012 or less.
    short = confidence.score(
        original="至桓帝延熹九年，大秦王安敦遣使自日南徼外獻象牙",
        forward_en="In the ninth year of Yanxi, the king of Da Qin sent an envoy",
        back_translated="桓帝延熹九年，大秦王遣使獻象牙",
        profile=PROSE, cos_back=0.88,
    )
    expect("short_source_chrf_noisy" in short.flags,
           "a short source is flagged as having a noisy chrF")
    expect("short_source_chrf_noisy" not in confidence.BLOCKING_FLAGS,
           "the short-source flag is a reading instruction, not a failure")

    # Control: the same texts repeated past the length threshold, so chrF and
    # cosine are held roughly constant and length is the only thing that moves.
    control = confidence.score(
        original="\n".join(["至桓帝延熹九年，大秦王安敦遣使自日南徼外獻象牙"] * 8),
        forward_en="In the ninth year of Yanxi, the king of Da Qin sent an envoy",
        back_translated="\n".join(["桓帝延熹九年，大秦王遣使獻象牙"] * 8),
        profile=PROSE, cos_back=0.88,
    )
    expect("short_source_chrf_noisy" not in control.flags,
           "a source past the length threshold is not flagged")
    expect(short.band == control.band,
           f"the short-source flag does not by itself change the band "
           f"(short {short.band} vs control {control.band})")

    empty = confidence.score(GREEK, "", "", profile=PROSE)
    expect(empty.band == "unscored" and "empty_translation" in empty.flags,
           "an empty translation is unscored, not zero")

    no_cos = confidence.score(
        original="abcdef", forward_en="x", back_translated="abcdef", profile=PROSE
    )
    expect(no_cos.band in {"medium", "low"},
           "without cosine the band falls back to chrF and cannot reach high")
    expect(any("chrF alone" in n for n in no_cos.notes),
           "the fallback to chrF alone is stated in the notes")

    # A profile with looser thresholds must actually change the verdict, or
    # genre-awareness is decoration.
    verse = confidence.Profile("verse", cos_high=0.65, cos_low=0.45,
                               chrf_high=0.35, chrf_low=0.15)
    args = dict(original="அ ஆ இ ஈ உ", forward_en="a b c d e",
                back_translated="அ ஆ இ ஈ உ", cos_back=0.70)
    expect(confidence.score(profile=PROSE, **args).band == "medium"
           and confidence.score(profile=verse, **args).band == "high",
           "the same round trip bands differently under prose and verse profiles")


def test_alignment() -> None:
    print("\nchunk alignment")

    class C:
        def __init__(self, chunk_id, text):
            self.chunk_id = chunk_id
            self.text = text

    originals = [C("o1", "53. Μετὰ δὲ"), C("o2", "54. Βασιλείας"),
                 C("o3", "55. Ἑτέρα"), C("o4", "56. Πλεῖ")]
    translations = [C("t1", "53. Beyond"), C("t2", "54. Tyndis"),
                    C("t3", "55. There is"), C("t4", "56. They send")]

    pairs = align.pair_chunks(originals, translations)
    expect(all(p.ground == "section" for p in pairs),
           "matching section markers give section-level alignment")
    expect(pairs[3].translation.chunk_id == "t4", "sections pair by label, not position")

    shuffled = [translations[2], translations[0], translations[3], translations[1]]
    pairs = align.pair_chunks(originals, shuffled)
    expect(pairs[0].translation.chunk_id == "t1",
           "section pairing survives the translation chunks arriving out of order")

    # The Part 3 case: three Greek chunks against one English summary.
    pairs = align.pair_chunks(
        [C("o1", "27. Ἀπὸ δὲ"), C("o2", "28. Εἰσάγεται"), C("o3", "29. Μετὰ δὲ")],
        [C("t1", "From Eudaemon Arabia there follows...")],
    )
    expect(all(p.translation is None and p.ground == "none" for p in pairs),
           "unequal counts with no markers claim no pairing at all")

    pairs = align.pair_chunks([C("o1", "no marker here")], [C("t1", "none here either")])
    expect(pairs[0].ground == "index",
           "equal counts without markers fall back to index pairing, labelled as such")

    expect(align.section_label("56. Πλεῖ δὲ") == "56", "leading number is a marker")
    expect(align.section_label("§ 20 ANE") == "20", "§ form is a marker")
    expect(align.section_label("five hundred stadia, 56 of them") is None,
           "a number mid-sentence is not a section marker")

    # ------------------------------------------------------------------
    # _merge, against BOTH chunk types this module is called with.
    #
    # It had never run. `C` above is a plain class, so `is_dataclass` sent
    # every call down the single-chunk return, and no translation section had
    # ever split into two chunks in the corpus. The A4 Greek recovery split one,
    # and Part 6 crashed on `last.char_end` — because `answer/store.py`'s
    # ChunkRow has no offsets while `answer/answer_store.py`'s row does, and
    # this function was written for the second and reached from both.
    # ------------------------------------------------------------------

    @dataclass(frozen=True)
    class WithOffsets:
        chunk_id: str
        text: str
        char_start: int
        char_end: int

    @dataclass(frozen=True)
    class NoOffsets:          # the shape of answer/store.py's ChunkRow
        chunk_id: str
        text: str

    expect(align.has_offsets(WithOffsets("a", "x", 0, 1))
           and not align.has_offsets(NoOffsets("a", "x")),
           "the two chunk types are distinguished by whether they carry offsets")

    # With offsets: the gap between chunks is filled so that char_start + n
    # still lands on the right character, which is what cite.py depends on.
    merged = align._merge([
        WithOffsets("a", "53. Beyond Calliena", 100, 119),
        WithOffsets("b", "there are other towns", 124, 145),
    ])
    expect(merged.text == "53. Beyond Calliena     there are other towns",
           "with offsets, the dropped characters are replaced space for space")
    expect(merged.char_end == 145, "the merged span ends where the last chunk ends")
    expect(merged.text.index("there") == 124 - 100,
           "an offset into the merged text still resolves to the right character")

    # Without offsets: merging must not crash, and must not invent a span.
    #
    # The exception is caught rather than allowed to propagate because the
    # defect being guarded IS an AttributeError, and an uncaught one would abort
    # the suite instead of failing this line. `scripts/mutate_part7b.py` reads
    # `FAIL <label>`, and a crash is explicitly not a guard firing — the
    # distinction test_embed.py cost two days to establish.
    try:
        merged = align._merge([NoOffsets("a", "53. Beyond Calliena"),
                               NoOffsets("b", "there are other towns")])
        joined = merged.text == "53. Beyond Calliena there are other towns"
        no_span = not hasattr(merged, "char_end")
    except Exception as exc:                      # noqa: BLE001 — see above
        print(f"       _merge raised on a chunk type with no offsets: {exc!r}")
        joined = no_span = False
    expect(joined, "without offsets, the pieces are joined with a single space")
    expect(no_span, "a chunk type with no span does not acquire one by being merged")

    # The regression proper: the exact call Part 6 makes, which crashed.
    try:
        pairs = align.pair_chunks(
            [NoOffsets("o1", "4. Μετὰ δὲ τὴν Πτολεμαΐδα")],
            [NoOffsets("t1", "4. Below Ptolemais of the Hunts"),
             NoOffsets("t2", "and about eight hundred stadia beyond")],
        )
        ok = pairs[0].ground == "section" and "eight hundred" in pairs[0].translation.text
    except Exception as exc:                      # noqa: BLE001
        print(f"       pair_chunks raised: {exc!r}")
        ok = False
    expect(ok, "a split translation section merges for a chunk type with no offsets")


# --------------------------------------------------------------------------
# Gold set
# --------------------------------------------------------------------------

def test_gold_set() -> None:
    print("\ngold set")

    from eval import goldset

    probes = goldset.load_probes()
    expect(len(probes) >= 11, f"all probes load ({len(probes)} found)")
    expect(any(p.expect_text_contains for p in probes),
           "at least one probe asserts passage content, not just a document id")
    pepper = [p for p in probes if "pepper" in p.name]
    expect(pepper and pepper[0].expect_text_contains == "πέπερι",
           "the pepper probe still carries its passage-level assertion")
    cross = [p for p in probes if p.kind == "cross_lingual"]
    expect(all(p.langs and "en" not in p.langs for p in cross),
           "no cross-lingual probe can be satisfied by an English chunk")
    expect(all(len(p.langs) == len(cross[0].langs) for p in cross),
           "every cross-lingual probe uses the same pool — no silent drift")

    profiles = goldset.load_profiles()
    expect({"prose", "verse", "inscription", "documentary"} <= set(profiles),
           "the four genre profiles are defined")
    expect(all(p.cos_low <= p.cos_high and p.chrf_low <= p.chrf_high
               for p in profiles.values()),
           "no profile has an inverted threshold pair")

    cases = goldset.load_translation_cases(profiles=profiles)
    expect(len(cases) >= 8, f"translation cases load ({len(cases)} found)")
    expect(all(c.profile in profiles for c in cases),
           "every case names a profile that exists")
    langs = {c.source_lang for c in cases}
    expect(len(langs) >= 4, f"cases span several source languages ({sorted(langs)})")
    expect(any(c.id == "skz-xpr" for c in cases),
           "the hardest case (Parthian ŠKZ) is in the gold set")

    untranslatable = [c for c in cases if c.expect_untranslatable]
    expect(len(untranslatable) == 1 and untranslatable[0].id == "vimose-gmq-pro",
           "the untranslatable case is declared as such")
    expect(all(not c.expect_no_blocking_flags for c in untranslatable),
           "an untranslatable case does not also demand clean flags")

    # Declaring a source untranslatable is a claim about the material. It has
    # to be made deliberately, not inherited from the default.
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                     encoding="utf-8") as fh:
        json.dump({"cases": [{
            "id": "sloppy", "doc_id": "d", "source_lang": "grc",
            "profile": "prose", "expect_untranslatable": True,
        }]}, fh)
        sloppy = Path(fh.name)
    try:
        goldset.load_translation_cases(sloppy, profiles=profiles)
        expect(False, "expect_untranslatable without an explicit flag waiver raises")
    except goldset.GoldSetError as exc:
        expect("expect_no_blocking_flags" in str(exc),
               "expect_untranslatable without an explicit flag waiver raises")
    finally:
        sloppy.unlink(missing_ok=True)

    # A misspelled key must fail loudly. This is the shape of the bug the gold
    # set exists to prevent: a silently ignored key leaves a weaker assertion.

    bad = {
        "probes": [{
            "name": "typo", "kind": "same_language", "query": "x",
            "query_lang": "grc", "expect_doc": "d",
            "expect_contains": "πέπερι",     # <- should be expect_text_contains
        }]
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                     encoding="utf-8") as fh:
        json.dump(bad, fh)
        bad_path = Path(fh.name)
    try:
        goldset.load_probes(bad_path)
        expect(False, "an unknown key in a probe raises GoldSetError")
    except goldset.GoldSetError as exc:
        expect("expect_contains" in str(exc),
               "an unknown key in a probe raises GoldSetError naming the key")
    finally:
        bad_path.unlink(missing_ok=True)

    expect(goldset.band_at_least("high", "medium") and
           not goldset.band_at_least("low", "medium") and
           goldset.band_at_least("medium", "medium"),
           "band comparison orders unscored < low < medium < high")


# --------------------------------------------------------------------------
# SQL
# --------------------------------------------------------------------------

def test_sql() -> None:
    print("\nPart 6 SQL")

    sql = Path("scripts/schema-part6.sql").read_text(encoding="utf-8")

    expect("CREATE TABLE IF NOT EXISTS chunk_translations" in sql,
           "schema is idempotent (IF NOT EXISTS)")
    expect(sql.count("DROP CONSTRAINT IF EXISTS") == 3,
           "every constraint is dropped before being added, so re-running works")
    expect("REFERENCES chunks (chunk_id) ON DELETE CASCADE" in sql,
           "a pruned chunk takes its translations with it")
    # BOTH prompt versions belong in the key. Leaving back_prompt_version out
    # of it is not theoretical: on 2026-08-10 a v2 back-translation overwrote
    # the v1 row for the same chunk, row count stayed at 9, and a band flipped
    # medium -> high with no trace of what it had been.
    pk = sql.split("PRIMARY KEY (", 1)[1].split(")", 1)[0]
    pk_cols = {c.strip() for c in pk.replace("\n", " ").split(",")}
    expect(pk_cols == {"chunk_id", "target_lang", "translation_model",
                       "prompt_version", "back_prompt_version"},
           f"both prompt versions are in the primary key (got {sorted(pk_cols)})")
    expect("back_prompt_version     text        NOT NULL DEFAULT 'none'" in sql,
           "back_prompt_version is NOT NULL — a primary key column has to be")

    # ON CONFLICT must name exactly the primary key, or the upsert raises at
    # execution time. Parse-level checking cannot catch that; comparing the two
    # column lists can.
    conflict = store.UPSERT_TRANSLATION.split("ON CONFLICT (", 1)[1].split(")", 1)[0]
    conflict_cols = {c.strip() for c in conflict.replace("\n", " ").split(",")}
    expect(conflict_cols == pk_cols,
           f"ON CONFLICT matches the primary key exactly "
           f"(key {sorted(pk_cols)} vs conflict {sorted(conflict_cols)})")
    expect("DO $$" in sql and "chunk_translations_pkey" in sql,
           "an existing table is migrated to the wider key, not left behind")

    # The staleness rule has to agree on both sides or a translation of
    # superseded text keeps being served with a citation attached.
    expect("encode(sha256(convert_to(c.text, 'UTF8')), 'hex')" in sql,
           "the view computes the source hash in SQL")
    expect(store.text_sha256("abc") ==
           "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
           "the Python hash is plain sha256 hex of the UTF-8 bytes")

    # Every column named in the upsert must exist in the table, and every
    # parameter must be supplied by write_translation's defaults.
    columns = set()
    body = sql.split("CREATE TABLE IF NOT EXISTS chunk_translations (", 1)[1]
    body = body.split("PRIMARY KEY", 1)[0]
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("--"):
            continue
        columns.add(line.split()[0].strip(","))

    _re = re

    insert_cols = {
        c.strip() for c in
        store.UPSERT_TRANSLATION.split("INSERT INTO chunk_translations (", 1)[1]
        .split(")", 1)[0].replace("\n", " ").split(",")
    }
    expect(insert_cols <= columns,
           f"every inserted column exists in the table (extra: {insert_cols - columns})")

    params = set(_re.findall(r"%\((\w+)\)s", store.UPSERT_TRANSLATION))
    supplied = set()
    src = Path("answer/store.py").read_text(encoding="utf-8")
    defaults_block = src.split("full = {", 1)[1].split("}", 1)[0]
    supplied.update(_re.findall(r'"(\w+)":', defaults_block))
    required_from_caller = {"chunk_id", "translation_model", "prompt_version",
                            "translated_text", "source_text_sha256"}
    expect(params - supplied <= required_from_caller,
           f"every optional upsert parameter has a default "
           f"(missing: {sorted(params - supplied - required_from_caller)})")

    # Same regression guard as Part 4: a NULL-able parameter with no cast
    # parses cleanly and then fails at execution with AmbiguousParameter.
    for name, query in (("SELECT_TRANSLATABLE", store.SELECT_TRANSLATABLE),):
        offenders = [
            m for m in _re.findall(r"%\((\w+)\)s(?!::)\s*IS NULL", query)
        ]
        expect(not offenders,
               f"{name}: every nullable parameter carries a cast "
               f"(uncast: {offenders})")

    try:
        import sqlglot

        # sqlglot does not model PL/pgSQL, so the DO $$ ... $$ migration block
        # parses as an opaque Command and prints a warning. It is excluded here
        # and checked by the string assertions above instead; parsing the rest
        # is still worth doing.
        parseable = re.sub(r"DO \$\$.*?\$\$;", "", sql, flags=re.S)
        for statement in sqlglot.parse(parseable, read="postgres"):
            pass
        sqlglot.parse_one(store.UPSERT_TRANSLATION, read="postgres")
        sqlglot.parse_one(
            store.SELECT_TRANSLATABLE.format(limit_clause=""), read="postgres"
        )
        expect(True, "schema and queries parse as PostgreSQL")
    except ImportError:
        print("  skip sqlglot not installed (pip install -r requirements-dev.txt)")
    except Exception as exc:  # noqa: BLE001
        expect(False, f"schema and queries parse as PostgreSQL ({exc})")


def main() -> int:
    print("Part 6 offline tests — no network, no database")
    test_prompt_contract()
    test_response_parsing()
    test_chat_calls()
    test_chrf()
    test_cosine()
    test_scoring()
    test_alignment()
    test_gold_set()
    test_sql()

    print()
    if failures:
        print(f"{len(failures)} failure(s):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("all Part 6 offline checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
