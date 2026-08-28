"""Loader for the declarative gold set in eval/gold/.

Validation is strict on purpose, and in particular it rejects *unknown keys*.
A silently ignored key is how a probe passes for the wrong reason: write
`expect_contains` where the field is `expect_text_contains` and the assertion
disappears, leaving a probe that checks only the document id — which is the
exact failure this gold set was created in response to. A typo should be a
loud error at load time, not a weaker test at run time.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

GOLD_DIR = Path(__file__).parent / "gold"  # data files; this module is goldset.py so it cannot be shadowed by the directory

PROBE_KINDS = {"same_language", "cross_lingual", "paired"}
BANDS = ("unscored", "low", "medium", "high")
BAND_ORDER = {b: i for i, b in enumerate(BANDS)}


class GoldSetError(ValueError):
    pass


def _check_keys(obj: dict, required: set, optional: set, where: str) -> None:
    keys = set(obj)
    missing = required - keys
    if missing:
        raise GoldSetError(f"{where}: missing required key(s): {sorted(missing)}")
    unknown = keys - required - optional
    if unknown:
        raise GoldSetError(
            f"{where}: unknown key(s) {sorted(unknown)}. Known keys are "
            f"{sorted(required | optional)}. A misspelled key would otherwise be "
            f"ignored, weakening the check without failing it."
        )


# --------------------------------------------------------------------------
# Retrieval probes
# --------------------------------------------------------------------------

@dataclass
class Probe:
    name: str
    query: str
    query_lang: str
    expect_doc: str
    kind: str
    langs: list[str] | None = None
    roles: list[str] | None = None
    expect_text_contains: str | None = None
    pair: str | None = None
    note: str = ""


_PROBE_REQUIRED = {"name", "kind", "query", "query_lang", "expect_doc"}
_PROBE_OPTIONAL = {"langs", "lang_pool", "roles", "expect_text_contains", "pair", "note"}


def load_probes(path: Path | None = None) -> list[Probe]:
    path = path or GOLD_DIR / "retrieval_probes.json"
    data = _read(path)
    pools = data.get("pools", {})
    probes: list[Probe] = []
    seen: set[str] = set()

    for i, raw in enumerate(data.get("probes", [])):
        where = f"{path.name} probe[{i}]"
        _check_keys(raw, _PROBE_REQUIRED, _PROBE_OPTIONAL, where)

        if raw["kind"] not in PROBE_KINDS:
            raise GoldSetError(
                f"{where}: kind '{raw['kind']}' is not one of {sorted(PROBE_KINDS)}"
            )
        if raw["name"] in seen:
            raise GoldSetError(f"{where}: duplicate probe name {raw['name']!r}")
        seen.add(raw["name"])

        if "langs" in raw and "lang_pool" in raw:
            raise GoldSetError(
                f"{where}: set either 'langs' or 'lang_pool', not both — two "
                f"candidate pools for one probe is ambiguous."
            )
        langs = raw.get("langs")
        if "lang_pool" in raw:
            pool = pools.get(raw["lang_pool"])
            if pool is None:
                raise GoldSetError(
                    f"{where}: lang_pool '{raw['lang_pool']}' is not defined in "
                    f"'pools' ({sorted(pools)})"
                )
            langs = list(pool["langs"])

        probes.append(
            Probe(
                name=raw["name"],
                query=raw["query"],
                query_lang=raw["query_lang"],
                expect_doc=raw["expect_doc"],
                kind=raw["kind"],
                langs=langs,
                roles=raw.get("roles"),
                expect_text_contains=raw.get("expect_text_contains"),
                pair=raw.get("pair"),
                note=raw.get("note", ""),
            )
        )

    if not probes:
        raise GoldSetError(f"{path}: no probes defined")

    # A paired probe is only meaningful against its partner.
    pairs: dict[str, int] = {}
    for p in probes:
        if p.kind == "paired":
            if not p.pair:
                raise GoldSetError(
                    f"{path.name}: probe {p.name!r} is kind 'paired' but has no "
                    f"'pair' key naming its partner"
                )
            pairs[p.pair] = pairs.get(p.pair, 0) + 1
    for name, count in pairs.items():
        if count != 2:
            raise GoldSetError(
                f"{path.name}: pair {name!r} has {count} member(s); a paired "
                f"probe compares exactly two askings of the same question"
            )
    return probes


# --------------------------------------------------------------------------
# Confidence profiles
# --------------------------------------------------------------------------

_PROFILE_REQUIRED = {"cos_high", "cos_low", "chrf_high", "chrf_low"}
_PROFILE_OPTIONAL = {"calibrated", "note"}


def load_profiles(path: Path | None = None) -> dict:
    """Returns {name: answer.confidence.Profile}."""
    from answer.confidence import Profile

    path = path or GOLD_DIR / "confidence_profiles.json"
    data = _read(path)
    out: dict[str, Profile] = {}

    for name, raw in data.get("profiles", {}).items():
        where = f"{path.name} profile[{name}]"
        _check_keys(raw, _PROFILE_REQUIRED, _PROFILE_OPTIONAL, where)
        for key in _PROFILE_REQUIRED:
            value = raw[key]
            if not isinstance(value, (int, float)) or not 0.0 <= value <= 1.0:
                raise GoldSetError(f"{where}: {key} must be a number in 0.0-1.0")
        if raw["cos_low"] > raw["cos_high"] or raw["chrf_low"] > raw["chrf_high"]:
            raise GoldSetError(
                f"{where}: a 'low' threshold is above its 'high' counterpart, "
                f"which would make the medium band empty and every result either "
                f"high or low."
            )
        out[name] = Profile(
            name=name,
            cos_high=float(raw["cos_high"]),
            cos_low=float(raw["cos_low"]),
            chrf_high=float(raw["chrf_high"]),
            chrf_low=float(raw["chrf_low"]),
            calibrated=bool(raw.get("calibrated", False)),
            note=raw.get("note", ""),
        )

    if not out:
        raise GoldSetError(f"{path}: no profiles defined")
    return out


# --------------------------------------------------------------------------
# Translation cases
# --------------------------------------------------------------------------

@dataclass
class TranslationCase:
    id: str
    doc_id: str
    source_lang: str
    profile: str
    section: str | None = None
    seq: int | None = None
    expect_min_band: str = "low"
    expect_no_blocking_flags: bool = True
    allow_flags: list[str] = field(default_factory=list)
    reference_ground_expected: str | None = None
    # Some material cannot be translated by this pipeline and should not be.
    # The Vimose runes are six short, partly undeciphered sequences — the
    # published translation itself says "likely", "possibly", "remain only
    # partially deciphered" — and the model returns them verbatim rather than
    # inventing a reading. That is correct behaviour. A case marked here PASSES
    # when the round trip is BLOCKED, and fails if a clean translation appears:
    # if a future model does translate them, this stops being a known limit and
    # someone has to look at whether the reading is real or invented.
    expect_untranslatable: bool = False
    note: str = ""


_CASE_REQUIRED = {"id", "doc_id", "source_lang", "profile"}
_CASE_OPTIONAL = {
    "section", "seq", "expect_min_band", "expect_no_blocking_flags",
    "allow_flags", "reference_ground_expected", "expect_untranslatable", "note",
}


def load_translation_cases(
    path: Path | None = None, profiles: dict | None = None
) -> list[TranslationCase]:
    path = path or GOLD_DIR / "translation_cases.json"
    data = _read(path)
    profiles = profiles if profiles is not None else load_profiles()

    cases: list[TranslationCase] = []
    seen: set[str] = set()
    for i, raw in enumerate(data.get("cases", [])):
        where = f"{path.name} case[{i}]"
        _check_keys(raw, _CASE_REQUIRED, _CASE_OPTIONAL, where)

        if raw["id"] in seen:
            raise GoldSetError(f"{where}: duplicate case id {raw['id']!r}")
        seen.add(raw["id"])

        if raw["profile"] not in profiles:
            raise GoldSetError(
                f"{where}: profile '{raw['profile']}' is not defined in "
                f"confidence_profiles.json ({sorted(profiles)})"
            )
        band = raw.get("expect_min_band", "low")
        if band not in BAND_ORDER:
            raise GoldSetError(f"{where}: expect_min_band '{band}' not in {list(BANDS)}")
        if "section" in raw and "seq" in raw:
            raise GoldSetError(
                f"{where}: set either 'section' or 'seq', not both — they can "
                f"select different chunks, and then the case is about neither."
            )
        if raw.get("expect_untranslatable") and raw.get("expect_no_blocking_flags", True):
            raise GoldSetError(
                f"{where}: expect_untranslatable is true, so the case passes "
                f"only when the round trip is blocked. Set "
                f"expect_no_blocking_flags to false explicitly — declaring a "
                f"source untranslatable is a claim about the material and "
                f"should be made deliberately, not inherited from a default."
            )

        cases.append(
            TranslationCase(
                id=raw["id"],
                doc_id=raw["doc_id"],
                source_lang=raw["source_lang"],
                profile=raw["profile"],
                section=str(raw["section"]) if "section" in raw else None,
                seq=int(raw["seq"]) if "seq" in raw else None,
                expect_min_band=band,
                expect_no_blocking_flags=bool(raw.get("expect_no_blocking_flags", True)),
                allow_flags=list(raw.get("allow_flags", [])),
                reference_ground_expected=raw.get("reference_ground_expected"),
                expect_untranslatable=bool(raw.get("expect_untranslatable", False)),
                note=raw.get("note", ""),
            )
        )

    if not cases:
        raise GoldSetError(f"{path}: no translation cases defined")
    return cases


# --------------------------------------------------------------------------
# Answer cases (Part 8)
# --------------------------------------------------------------------------

@dataclass
class AnswerCase:
    id: str
    question: str
    why: str
    # What this case exists to observe, declared per case and never inherited
    # from a default. Three behaviours, and they name three different failures:
    #   answerable            the corpus holds it, so a red line is a retrieval
    #                         or assembly failure
    #   correctly_refusable   the corpus does not hold it, so a red line means
    #                         the model invented something
    #   refusable_with_gloss  the corpus holds it but not in a form that can be
    #                         translated, so a red line means a machine
    #                         translation appeared -- attached to a citation,
    #                         which is the worst output this system can produce
    # Without the label a red line says only "this case failed", and those three
    # are not the same piece of news.
    expected_behaviour: str
    expect_cited_docs: list[str] = field(default_factory=list)
    expect_cited_chunks: list[str] = field(default_factory=list)
    # Documents from which at least one quotation must resolve to characters on
    # disk. Stronger than expect_cited_docs, and added because a dry run showed
    # the weaker form was satisfiable by the wrong source: the Aksum evidence set
    # also carries `ivory` and `tortoise-shell` in the Muziris passage and
    # `rhinoceros` in the Hou Hanshu, so an answer could satisfy every content
    # term from India and China, cite the Aksum record once for something else,
    # and pass. Citing a document is a proxy; quoting it is the thing.
    expect_quoted_docs: list[str] = field(default_factory=list)
    # Documents from which a quotation must resolve into ORIGINAL_TEXT_EXCERPT
    # specifically — the record's own language, not its published English.
    # expect_quoted_docs cannot express this: it is satisfied by either chunk,
    # and FINDING 13 is that the English is always the one chosen. Prompt rule 3
    # permits either and nothing requires the source text, so a case that wants
    # the source text has to say so.
    expect_quoted_from_original: list[str] = field(default_factory=list)
    expect_answer_contains: list[str] = field(default_factory=list)
    # Each inner list is a set of acceptable wordings, one of which must appear.
    # `[["tortoise-shell", "tortoise shell"]]` accepts either spelling; two
    # separate entries would demand both.
    expect_answer_contains_any: list[list[str]] = field(default_factory=list)
    # The hedge a refusable_with_gloss case must find in the answer, declared
    # apart from ordinary content so the loader can REQUIRE it rather than hope
    # one of the alternatives groups happens to be hedges. It is merged into
    # expect_answer_contains_any at construction, so the scorer sees one more
    # alternatives group and nothing about scoring changes. The separation
    # exists at the only place the rule is enforced, which is load time.
    expect_hedge_any: list[list[str]] = field(default_factory=list)
    expect_answer_excludes: list[str] = field(default_factory=list)
    expect_min_resolved_quotes: int = 0
    # Recorded, never sufficient. See _has_content_assertion.
    expect_grounded: bool | None = None
    # Some questions the corpus genuinely cannot answer, and refusing is right.
    # Same shape as TranslationCase.expect_untranslatable: asserting it is a
    # claim about the corpus and must be justified in the file, not inherited.
    expect_refusal: bool = False
    refusal_is_correct_because: str = ""
    # The other half of a discriminator. Symmetric and enforced at load rather
    # than described in a note: see _check_pairs.
    paired_with: str = ""
    # Which of the corpus's seven regions this case exercises. Optional where a
    # doc id makes it derivable, required where nothing does -- see
    # load_answer_cases. G4 asks for ">=30 cases meeting the stratification" and
    # the stratification is per-region, so it has to be a number anyone can
    # compute from this file rather than a mapping someone reconstructs by hand.
    region: str = ""
    archived_status: str = ""
    note: str = ""


# The seven regions the corpus covers, spelled as the seed records spell them,
# plus one value for a case that is deliberately outside all of them. The
# Antikythera control is outside on purpose: it is a Mediterranean wreck, and
# that is the entire reason it is the right question to refuse.
ANSWER_REGIONS = (
    "Arabia",
    "East Asia",
    "Persia",
    "Scandinavia",
    "South Asia",
    "Southeast Asia",
    "Sub-Saharan Africa",
    "outside",
)

BEHAVIOUR_ANSWERABLE = "answerable"
BEHAVIOUR_REFUSABLE = "correctly_refusable"
BEHAVIOUR_GLOSS = "refusable_with_gloss"
ANSWER_BEHAVIOURS = (BEHAVIOUR_ANSWERABLE, BEHAVIOUR_REFUSABLE, BEHAVIOUR_GLOSS)

_ANSWER_REQUIRED = {"id", "question", "why", "expected_behaviour"}
_ANSWER_OPTIONAL = {
    "expect_cited_docs", "expect_cited_chunks", "expect_quoted_docs",
    "expect_quoted_from_original",
    "expect_answer_contains",
    "expect_answer_contains_any", "expect_hedge_any", "expect_answer_excludes",
    "expect_min_resolved_quotes", "expect_grounded", "expect_refusal",
    "refusal_is_correct_because", "paired_with", "region",
    "archived_status", "note",
    # Ruling 41, 2026-08-28. Why an exclusion list was changed, beside the
    # list. A correction recorded only in a commit message is a correction the
    # next reader of this file does not have.
    "excludes_corrected_on",
}

# Ruling 41. A correct refusal RESTATES the question it is refusing, so an
# exclusion assembled from that question's own vocabulary fires on the very
# answer the case exists to accept. Split out so the rule below reads as one
# sentence; the words themselves live in answer_cases.json.
def _content_words(text: str, stopwords: set) -> set:
    return {w for w in re.findall(r"[^\W\d_]+", text.casefold())} - stopwords

# The assertions that say something about what the answer SAYS, as opposed to
# whether it was tidy about citing. A case built only from the latter cannot
# fail a refusal, and a refusal is trivially grounded.
_CONTENT_KEYS = (
    "expect_quoted_from_original",
    "expect_answer_contains",
    "expect_answer_contains_any",
    "expect_hedge_any",
    "expect_answer_excludes",
    "expect_cited_docs",
    "expect_cited_chunks",
    "expect_quoted_docs",
)

# The assertions that require the answer to SAY something. An exclusion is not
# among them: a refusal contains none of the strings a case excludes, so a case
# built from exclusions alone is passed by silence. That is only tolerable when
# silence is the declared expected behaviour.
_POSITIVE_KEYS = (
    "expect_answer_contains",
    "expect_answer_contains_any",
    "expect_hedge_any",
)

# The keys that ARE the test, as written in the file. Two halves of a
# discriminator must agree on every one of them; id, question, why, note,
# archived_status and paired_with are deliberately not here, because the
# QUESTION is the only thing the two halves are allowed to differ on.
_ASSERTION_KEYS = (
    "expected_behaviour",
    "expect_cited_docs",
    "expect_cited_chunks",
    "expect_quoted_docs",
    "expect_quoted_from_original",
    "expect_answer_contains",
    "expect_answer_contains_any",
    "expect_hedge_any",
    "expect_answer_excludes",
    "expect_min_resolved_quotes",
    "expect_grounded",
    "expect_refusal",
)


def question_key(text: str) -> str:
    """The string under which two cases are THE SAME QUESTION.

    Defined here, and imported by `eval/answer_eval.py:match_case`, so that the
    rule the loader enforces and the rule the matcher applies cannot be two
    rules. The same argument as `answer_eval` importing `REFUSAL_SENTENCE`
    rather than copying it: a matcher that recognised a duplicate the loader
    did not would put the shadowed case back, and nothing would say so.

    Whitespace and case, and deliberately not punctuation — the same tolerances
    `answer_eval.normalise` applies, because an archived question and a gold
    question differ by the spacing a writer used, never by a comma.
    """
    return re.sub(r"\s+", " ", text).strip().casefold()


def _has_content_assertion(raw: dict) -> bool:
    if any(raw.get(key) for key in _CONTENT_KEYS):
        return True
    return int(raw.get("expect_min_resolved_quotes", 0) or 0) > 0


def _assertion_block(raw: dict) -> dict:
    """The part of a case that IS the test, exactly as written in the file."""
    return {key: raw[key] for key in _ASSERTION_KEYS if key in raw}


def _check_pairs(raws: dict[str, dict], path: Path) -> None:
    """A discriminator is one instrument in two halves, and it loads as one.

    `aksum-exports` and `adulis-exports` assert the same things about the same
    document and differ only in the wording of the question. A run in which the
    first fails and the second passes says the defect is in the
    question-to-retrieval-to-answer path and not in the corpus. That reading
    survives only while the two halves stay identical, so both facts are
    enforced here instead of being described in a note that nothing reads:

    * the partner exists and names this case back, so deleting one half is a
      load error rather than a silent halving of the discriminator;
    * the two assertion blocks are the same, so the pair never quietly stops
      discriminating between two QUESTIONS and starts discriminating between
      two tests.
    """
    for case_id, raw in raws.items():
        partner_id = str(raw.get("paired_with", "") or "").strip()
        if not partner_id:
            continue
        where = f"{path.name} case {case_id!r}"

        if partner_id == case_id:
            raise GoldSetError(
                f"{where}: paired_with names the case itself. A discriminator "
                f"is two questions against one assertion block; one question "
                f"discriminates nothing."
            )

        partner = raws.get(partner_id)
        if partner is None:
            raise GoldSetError(
                f"{where}: paired_with names {partner_id!r}, which is not in "
                f"this file. Half a discriminator measures nothing and reads "
                f"exactly like a whole one."
            )

        back = str(partner.get("paired_with", "") or "").strip()
        if back != case_id:
            raise GoldSetError(
                f"{where}: the pairing is not symmetric - {case_id!r} names "
                f"{partner_id!r}, which names {back or 'nothing'}. Enforced "
                f"from both ends, because otherwise deleting the half that "
                f"does not point back is silent."
            )

        mine, theirs = _assertion_block(raw), _assertion_block(partner)
        if mine != theirs:
            differing = sorted(
                key for key in set(mine) | set(theirs)
                if mine.get(key) != theirs.get(key)
            )
            raise GoldSetError(
                f"{where}: the assertion blocks of {case_id!r} and "
                f"{partner_id!r} differ on {differing}. The pair exists to "
                f"discriminate between two questions against identical "
                f"assertions; the moment the assertions differ it discriminates "
                f"between two tests instead, and its result stops meaning what "
                f"it is read as meaning."
            )


def load_answer_cases(path: Path | None = None) -> list[AnswerCase]:
    """Strict loader for eval/gold/answer_cases.json.

    Two rules here do not exist in the other loaders, and both are answers to
    Part 8 decision 1 — that the easy version of this harness, `assert
    grounding.ok`, is the one that measures nothing:

    1. **A case must make at least one content assertion.** Groundedness alone
       is unfailable by a refusal, and the corpus's own Aksum answer refuses
       while its cited evidence, printed in English in the same block, contains
       the answer. A case that could not fail that answer is not a test of it.

    2. **`expect_refusal` must justify itself.** Declaring that the corpus
       cannot answer a question is a claim about the corpus. It gets written
       out in `refusal_is_correct_because`, or it does not get made — the same
       rule `expect_untranslatable` follows, for the same reason.

    3. **`expected_behaviour` is declared per case and never inherited.** It is
       a required key, so a case that omits it is a load error rather than a
       case quietly filed under whatever the majority happens to be. The label
       must also agree with `expect_refusal` in BOTH directions: only the
       assertion is scored, so a label that disagrees with it files the case
       under a behaviour it does not test.

    4. **A discriminator loads as one instrument or not at all.** Cases joined
       by `paired_with` must name each other and must assert the same things.
       See `_check_pairs`.
    """
    path = path or GOLD_DIR / "answer_cases.json"
    data = _read(path)

    # Ruling 41. Read once, outside the loop. An absent rule means the clause
    # is not declared and nothing is checked, which is the pre-ruling
    # behaviour exactly — a gold file written before it existed does not
    # silently acquire it.
    exclusion_rule = data.get("refusal_exclusion_rule") or {}

    cases: list[AnswerCase] = []
    seen: set[str] = set()
    asked: dict[str, str] = {}
    raws: dict[str, dict] = {}
    for i, raw in enumerate(data.get("cases", [])):
        where = f"{path.name} case[{i}]"
        _check_keys(raw, _ANSWER_REQUIRED, _ANSWER_OPTIONAL, where)

        if raw["id"] in seen:
            raise GoldSetError(f"{where}: duplicate case id {raw['id']!r}")
        seen.add(raw["id"])
        raws[raw["id"]] = raw

        # Same family as FINDING 12, and quieter. `answer_eval.match_case`
        # returns the FIRST case whose question matches, so a second case
        # asking the same question is never scored against any archive — it
        # sits in the gold file looking exactly like a test, is counted in
        # every total and every per-region tally, and runs never. Avoided by
        # hand in `weilue-chinese-quotation` on 2026-08-22, unguarded until
        # now.
        #
        # Keyed with `question_key`, which is the matcher's own rule: two
        # questions differing only in spacing or letter case shadow each other
        # exactly as a byte-identical pair does, and refusing only the
        # byte-identical ones would be a guard that looks complete.
        key = question_key(raw["question"])
        if key in asked:
            raise GoldSetError(
                f"{where}: {raw['id']!r} asks the same question as "
                f"{asked[key]!r}. Scoring matches an archived run to the FIRST "
                f"case whose question matches, so the second would never be "
                f"scored against anything while still counting toward the "
                f"total and the per-region stratification. Two cases against "
                f"one record differ in the WORDING of the question — that is "
                f"what `paired_with` is for."
            )
        asked[key] = raw["id"]

        if not str(raw["why"]).strip():
            raise GoldSetError(
                f"{where}: 'why' is empty. A case that cannot say why it exists "
                f"will be deleted by whoever it inconveniences."
            )

        if not _has_content_assertion(raw):
            raise GoldSetError(
                f"{where}: makes no assertion about what the answer says. "
                f"Groundedness alone cannot fail a refusal, and a refusal is "
                f"trivially grounded — the Aksum answer refuses, states the "
                f"opposite of its own cited evidence, and is scored grounded. "
                f"Add at least one of {list(_CONTENT_KEYS)}, or "
                f"expect_min_resolved_quotes > 0."
            )

        # An empty alternatives list passes vacuously — the silent-weakening
        # failure this gold set exists to prevent, one level deeper than a
        # misspelled key.
        alternatives = [
            (key, j, group)
            for key in ("expect_answer_contains_any", "expect_hedge_any")
            for j, group in enumerate(raw.get(key, []))
        ]
        for key, j, group in alternatives:
            if not isinstance(group, list) or not group:
                raise GoldSetError(
                    f"{where}: {key}[{j}] must be a "
                    f"non-empty list of acceptable wordings. An empty group "
                    f"would be satisfied by any answer at all."
                )
            if any(not str(item).strip() for item in group):
                raise GoldSetError(
                    f"{where}: {key}[{j}] contains an "
                    f"empty string, which every answer contains."
                )
        for key in ("expect_answer_contains", "expect_answer_excludes"):
            for j, item in enumerate(raw.get(key, [])):
                if not str(item).strip():
                    raise GoldSetError(
                        f"{where}: {key}[{j}] is empty; every answer contains "
                        f"the empty string, so the assertion is vacuous."
                    )

        minimum = int(raw.get("expect_min_resolved_quotes", 0) or 0)
        if minimum < 0:
            raise GoldSetError(
                f"{where}: expect_min_resolved_quotes must be zero or positive"
            )

        refusal = bool(raw.get("expect_refusal", False))
        if refusal:
            if not str(raw.get("refusal_is_correct_because", "")).strip():
                raise GoldSetError(
                    f"{where}: expect_refusal is true, so the case passes only "
                    f"when the pipeline declines to answer. Say why the corpus "
                    f"cannot answer it in 'refusal_is_correct_because' — "
                    f"declaring a question unanswerable is a claim about the "
                    f"corpus and should be made deliberately, not inherited "
                    f"from a default."
                )
            contradictory = [
                key for key in
                ("expect_answer_contains", "expect_answer_contains_any",
                 "expect_hedge_any",
                 "expect_cited_chunks", "expect_quoted_docs",
                 "expect_quoted_from_original")
                if raw.get(key)
            ]
            if contradictory or minimum > 0:
                raise GoldSetError(
                    f"{where}: expect_refusal is true but the case also demands "
                    f"content the refusal cannot contain "
                    f"({contradictory + (['expect_min_resolved_quotes'] if minimum else [])}). "
                    f"A case cannot require an answer to both refuse and speak."
                )
        elif raw.get("refusal_is_correct_because"):
            raise GoldSetError(
                f"{where}: 'refusal_is_correct_because' is set but "
                f"expect_refusal is not true. The justification would sit in "
                f"the file explaining a rule that is not in force."
            )

        behaviour = str(raw["expected_behaviour"]).strip()
        if behaviour not in ANSWER_BEHAVIOURS:
            raise GoldSetError(
                f"{where}: expected_behaviour {behaviour!r} is not one of "
                f"{list(ANSWER_BEHAVIOURS)}. An unrecognised label would be "
                f"carried around as a string nothing acts on, which is a case "
                f"declaring an expectation no part of the harness reads."
            )

        # Two clauses, written as two on purpose. The first catches a case
        # labelled refusable that does not assert a refusal; the second catches
        # a case that asserts a refusal under some other label. Either clause
        # alone leaves half the contradiction expressible, and only the
        # assertion is scored - so the label is the half that would be wrong.
        if behaviour == BEHAVIOUR_REFUSABLE and not refusal:
            raise GoldSetError(
                f"{where}: expected_behaviour is {BEHAVIOUR_REFUSABLE!r} but "
                f"expect_refusal is not true. The label says the corpus cannot "
                f"answer this and the assertion says nothing of the kind."
            )
        if refusal and behaviour != BEHAVIOUR_REFUSABLE:
            raise GoldSetError(
                f"{where}: expect_refusal is true but expected_behaviour is "
                f"{behaviour!r}. A case that passes only when the pipeline "
                f"declines to answer is a {BEHAVIOUR_REFUSABLE!r} case whatever "
                f"the label says."
            )

        # RULING 41, 2026-08-28. `expect_answer_excludes` is a bare substring
        # test and cannot tell a claim from a refusal to make it. On a
        # correctly_refusable case that is not a corner: a correct refusal
        # NAMES what it is declining to say, and the more precisely it names
        # it the more certainly it trips an exclusion built out of the
        # question.
        #
        # oc-eo-cattigara failed 0/12 across four sessions and three dates on
        # exactly this, refusing correctly every time. Writing the guard then
        # turned up antikythera-absent — a REQUIRED case, passing 12/12, one
        # refusal phrasing away from the same failure, with nothing anywhere
        # that would have said why. That second case is the argument for a rule
        # rather than a correction.
        #
        # NOT a negation detector. The prompt notes already record that a rule
        # which has to be interpreted is a rule that will be broken, and inside
        # a matcher it would be broken in silence. This is a rule about how a
        # CASE is written: exclude fabrication markers — a name, a date, a
        # technical term the corpus does not hold — as the other seven
        # correctly_refusable cases already do.
        if behaviour == BEHAVIOUR_REFUSABLE:
            stopwords = {w.casefold() for w in
                         (exclusion_rule.get("stopwords") or [])}
            question_words = _content_words(raw["question"], stopwords)
            for phrase in raw.get("expect_answer_excludes") or []:
                phrase_words = _content_words(str(phrase), stopwords)
                if phrase_words and phrase_words <= question_words:
                    raise GoldSetError(
                        f"{where}: expect_answer_excludes {phrase!r} is built "
                        f"entirely from this case's own question "
                        f"({raw['question']!r}). A correct refusal restates "
                        f"the question it is refusing, so this exclusion fires "
                        f"on the answer the case exists to accept — and "
                        f"expect_answer_excludes is a substring test that "
                        f"cannot tell a claim from a refusal to make one. "
                        f"Exclude something a fabricating answer would ADD: a "
                        f"name, a date, a term the corpus does not contain. "
                        f"See answer_cases.json.refusal_exclusion_rule."
                    )

        positive = any(raw.get(key) for key in _POSITIVE_KEYS) or minimum > 0
        speaks = not refusal and behaviour != BEHAVIOUR_REFUSABLE
        if speaks and not positive:
            raise GoldSetError(
                f"{where}: expected_behaviour is {behaviour!r}, so the answer "
                f"is meant to speak - but this case only says what the answer "
                f"must NOT contain, and a refusal contains none of it. Add one "
                f"of {list(_POSITIVE_KEYS)}, or expect_min_resolved_quotes > 0."
            )

        region = str(raw.get("region", "") or "").strip()
        if region and region not in ANSWER_REGIONS:
            raise GoldSetError(
                f"{where}: region {region!r} is not one of "
                f"{list(ANSWER_REGIONS)}. The stratification is counted by "
                f"these names, so a near-miss spelling would drop the case out "
                f"of the count without dropping it out of the file."
            )
        # Derivable or declared, never absent. A case naming a document can be
        # attributed by looking that document up; a refusal names none, because
        # expect_quoted_docs is refused on a refusal case, so there is nothing
        # to look up and the case must say.
        if not region and not (raw.get("expect_cited_docs")
                               or raw.get("expect_quoted_docs")):
            raise GoldSetError(
                f"{where}: this case names no document, so its region cannot be "
                f"derived, so it must declare one. Without it the case is "
                f"invisible to the per-region stratification G4 is checked "
                f"against while still counting toward the total, which is the "
                f"shape of error that passes a gate on arithmetic nobody redid."
            )

        hedge = list(raw.get("expect_hedge_any", []))
        if behaviour == BEHAVIOUR_GLOSS:
            if not raw.get("expect_quoted_docs"):
                raise GoldSetError(
                    f"{where}: expected_behaviour is {BEHAVIOUR_GLOSS!r}, so "
                    f"the answer has to show the source's own published gloss. "
                    f"Name the record it must quote in expect_quoted_docs - "
                    f"citing a document is a proxy, quoting it is the thing."
                )
            if not hedge:
                raise GoldSetError(
                    f"{where}: expected_behaviour is {BEHAVIOUR_GLOSS!r} and no "
                    f"expect_hedge_any is declared. The hedge IS the assertion "
                    f"here: a confident English rendering of a partly "
                    f"undeciphered text is the worst output this system can "
                    f"produce, because it arrives attached to a citation."
                )
        elif hedge:
            raise GoldSetError(
                f"{where}: expect_hedge_any is set but expected_behaviour is "
                f"{behaviour!r}. The hedge requirement belongs to "
                f"{BEHAVIOUR_GLOSS!r}; anywhere else it sits in the file "
                f"looking like a rule that is in force."
            )

        cases.append(
            AnswerCase(
                id=raw["id"],
                question=raw["question"],
                why=raw["why"],
                expected_behaviour=behaviour,
                expect_cited_docs=list(raw.get("expect_cited_docs", [])),
                expect_cited_chunks=list(raw.get("expect_cited_chunks", [])),
                expect_quoted_docs=list(raw.get("expect_quoted_docs", [])),
                expect_quoted_from_original=list(
                    raw.get("expect_quoted_from_original", [])),
                expect_answer_contains=list(raw.get("expect_answer_contains", [])),
                expect_answer_contains_any=[
                    list(group) for group in raw.get("expect_answer_contains_any", [])
                ] + [list(group) for group in hedge],
                expect_hedge_any=[list(group) for group in hedge],
                expect_answer_excludes=list(raw.get("expect_answer_excludes", [])),
                expect_min_resolved_quotes=minimum,
                expect_grounded=raw.get("expect_grounded"),
                expect_refusal=refusal,
                refusal_is_correct_because=raw.get("refusal_is_correct_because", ""),
                paired_with=str(raw.get("paired_with", "") or "").strip(),
                region=region,
                archived_status=raw.get("archived_status", ""),
                note=raw.get("note", ""),
            )
        )

    _check_pairs(raws, path)

    if not cases:
        raise GoldSetError(f"{path}: no answer cases defined")
    return cases


# --------------------------------------------------------------------------
# Ranking pairs (W2a)
# --------------------------------------------------------------------------

@dataclass
class RankingPair:
    id: str
    query: str
    query_lang: str
    expect_doc: str
    # The assertion is the characters, not the id. Chunk ids move under a
    # re-ingest: africa-03-periplus-adulis was re-chunked on 2026-08-13 and the
    # Greek exports sentence the archived answers name as `original::002` now
    # lives in `original::005`. A pair keyed on the id would keep passing while
    # measuring ranking against the wrong passage — which is the doc-id-proxy
    # failure eval/gold/retrieval_probes.json was created in response to.
    expect_text_contains: str
    provenance: str
    region: str
    # Block C ruling 1 (BLOCK_C_RULINGS.md): a query with several acceptable
    # targets is ONE scored unit, not N. The unit is DECLARED here rather than
    # inferred by grouping identical query strings, because a unit inferred from
    # text nobody declared changes the gate's denominator the moment somebody
    # edits a query by a character. Absent, a pair is its own unit.
    unit_id: str | None = None
    # Block C ruling 2: this pair also accepts its document's own published
    # translation of the SAME section — computed at scoring time by
    # answer.align.pair_chunks, never hand-copied here, and only where that
    # module reports the alignment ground as "section". Declared per pair, so
    # extending the ruling beyond the four `translation_case` pairs it was made
    # for is a deliberate edit to this file and not a silent consequence.
    accept_aligned_translation: bool = False
    expect_lang: str | None = None
    langs: list[str] | None = None
    roles: list[str] | None = None
    pair: str | None = None
    source_ref: str = ""
    # Provenance only. Never asserted on, and never used to select a chunk. The
    # ranking check reports how many of these still name a chunk that exists, so
    # that re-chunking drift is a printed number rather than a silent pass.
    observed_chunk_id: str | None = None
    note: str = ""

    @property
    def unit(self) -> str:
        """The scored unit this pair belongs to. Its own id, if it declares none."""
        return self.unit_id or self.id


PROVENANCES = {"archived_answer", "retrieval_probe", "translation_case", "authored"}

_PAIR_REQUIRED = {"id", "query", "query_lang", "expect_doc",
                  "expect_text_contains", "provenance", "region"}
_PAIR_OPTIONAL = {"expect_lang", "langs", "lang_pool", "roles", "pair",
                  "source_ref", "observed_chunk_id", "note",
                  "unit_id", "accept_aligned_translation"}


def load_ranking_pairs(path: Path | None = None) -> list[RankingPair]:
    """The W2a ranking gold set.

    Same strictness as every other loader here, and one rule of its own: a pair
    must carry `expect_text_contains`. It is required rather than optional
    because the whole file exists to measure ranking, and a pair that asserts
    only `expect_doc` passes when the retriever returns the wrong passage of the
    right document — which for a five-chunk document is most of the ways it can
    be wrong.
    """
    path = path or GOLD_DIR / "ranking_pairs.json"
    data = _read(path)
    pools = data.get("pools", {})
    pairs: list[RankingPair] = []
    seen: set[str] = set()

    for i, raw in enumerate(data.get("pairs", [])):
        where = f"{path.name} pair[{i}]"
        _check_keys(raw, _PAIR_REQUIRED, _PAIR_OPTIONAL, where)

        if raw["id"] in seen:
            raise GoldSetError(f"{where}: duplicate pair id {raw['id']!r}")
        seen.add(raw["id"])

        if raw["provenance"] not in PROVENANCES:
            raise GoldSetError(
                f"{where}: provenance '{raw['provenance']}' is not one of "
                f"{sorted(PROVENANCES)}. The cohort is reported separately in "
                f"every ranking run, so an unrecognised one would drop a pair "
                f"out of the per-cohort table while leaving it in the total."
            )
        if not str(raw["expect_text_contains"]).strip():
            raise GoldSetError(
                f"{where}: expect_text_contains is empty. An empty substring is "
                f"in every chunk, so the pair would assert only expect_doc "
                f"while looking like it asserted more."
            )
        if "langs" in raw and "lang_pool" in raw:
            raise GoldSetError(
                f"{where}: set either 'langs' or 'lang_pool', not both — two "
                f"candidate pools for one pair is ambiguous."
            )
        langs = raw.get("langs")
        if "lang_pool" in raw:
            pool = pools.get(raw["lang_pool"])
            if pool is None:
                raise GoldSetError(
                    f"{where}: lang_pool '{raw['lang_pool']}' is not defined in "
                    f"'pools' ({sorted(pools)})"
                )
            langs = list(pool["langs"])

        if langs is not None and raw.get("expect_lang") and raw["expect_lang"] not in langs:
            raise GoldSetError(
                f"{where}: expect_lang '{raw['expect_lang']}' is excluded by "
                f"this pair's own candidate pool {sorted(langs)}, so the pair "
                f"can never be satisfied. This is how a cross-lingual pair gets "
                f"written against an English translation and then filtered out "
                f"of its own answer."
            )

        if "accept_aligned_translation" in raw:
            if not isinstance(raw["accept_aligned_translation"], bool):
                raise GoldSetError(
                    f"{where}: accept_aligned_translation must be true or false, "
                    f"not {raw['accept_aligned_translation']!r}. A truthy string "
                    f"would turn the ruling on for a pair that never declared it."
                )
            if raw["accept_aligned_translation"] and raw.get("expect_lang") == "en":
                raise GoldSetError(
                    f"{where}: accept_aligned_translation on an English target. "
                    f"The alternate this admits is the document's own English "
                    f"translation, so on an English target it either accepts the "
                    f"target twice or accepts an unrelated chunk. Ruling 2 is "
                    f"about reaching the right SECTION across a language "
                    f"boundary; there is no boundary here."
                )

        pairs.append(
            RankingPair(
                id=raw["id"],
                query=raw["query"],
                query_lang=raw["query_lang"],
                expect_doc=raw["expect_doc"],
                expect_text_contains=raw["expect_text_contains"],
                provenance=raw["provenance"],
                region=raw["region"],
                unit_id=raw.get("unit_id"),
                accept_aligned_translation=raw.get(
                    "accept_aligned_translation", False),
                expect_lang=raw.get("expect_lang"),
                langs=langs,
                roles=raw.get("roles"),
                pair=raw.get("pair"),
                source_ref=raw.get("source_ref", ""),
                observed_chunk_id=raw.get("observed_chunk_id"),
                note=raw.get("note", ""),
            )
        )

    if not pairs:
        raise GoldSetError(f"{path}: no ranking pairs defined")

    # PHASE2_PLAN.md B1: "Aim for >=20, spread across regions and languages — a
    # gold set that is 15 Greek pairs measures Greek." Both halves are enforced,
    # because the count alone is the easier half to satisfy dishonestly.
    if len(pairs) < 20:
        raise GoldSetError(
            f"{path.name}: {len(pairs)} pairs; W2a's floor is 20 (PHASE2_PLAN.md B1)."
        )
    regions = {p.region for p in pairs}
    if len(regions) < 7:
        raise GoldSetError(
            f"{path.name}: pairs cover {len(regions)} region(s) {sorted(regions)}; "
            f"the corpus spans 7 and a baseline over a subset is not a baseline "
            f"for the corpus."
        )

    # ----------------------------------------------------------------------
    # Block C ruling 1: the declared unit and the actual query text must agree,
    # in BOTH directions. Either direction failing silently moves the gate's
    # denominator, and 29 units against 32 pairs is the difference between a
    # G2 that needs three fixes and one that cannot pass at all.
    # ----------------------------------------------------------------------
    by_unit: dict[str, list[RankingPair]] = {}
    for p in pairs:
        by_unit.setdefault(p.unit, []).append(p)

    for unit, members in by_unit.items():
        queries = {m.query for m in members}
        if len(queries) > 1:
            raise GoldSetError(
                f"{path.name}: unit {unit!r} groups pairs with different query "
                f"text: {sorted(queries)}. A unit is one asking of one question "
                f"scored once; grouping two questions under it would score the "
                f"harder one away."
            )

    by_query: dict[str, list[RankingPair]] = {}
    for p in pairs:
        by_query.setdefault(p.query, []).append(p)
    for query, members in by_query.items():
        units = {m.unit for m in members}
        if len(members) > 1 and len(units) > 1:
            raise GoldSetError(
                f"{path.name}: {len(members)} pairs share the query {query!r} "
                f"but declare {len(units)} units {sorted(units)}. Under Block C "
                f"ruling 1 one query is one scored unit; leaving a new pair "
                f"undeclared would add a unit to the denominator without anyone "
                f"deciding to. Give them all the same unit_id."
            )

    # A paired pair is only meaningful against its partner — same rule as probes.
    partners: dict[str, int] = {}
    for p in pairs:
        if p.pair:
            partners[p.pair] = partners.get(p.pair, 0) + 1
    for name, count in partners.items():
        if count != 2:
            raise GoldSetError(
                f"{path.name}: pair group {name!r} has {count} member(s); a "
                f"paired pair compares exactly two askings of the same question"
            )
    return pairs


# --------------------------------------------------------------------------
# The Part 8 floor
# --------------------------------------------------------------------------

_FLOOR_REQUIRED = {"required_cases", "max_refusal_rate",
                   "max_unstable_content_cells", "min_repetitions",
                   # D4. Required rather than optional-with-a-default: a floor
                   # file that omitted it would calibrate from one day and the
                   # default would be the only thing saying otherwise, which
                   # is a threshold in Python by another route.
                   "min_distinct_dates"}


def load_floor(path: Path | None = None) -> dict:
    """The hard floor, as data.

    Same argument as confidence_profiles.json: thresholds in Python invite the
    opposite move — quietly loosening the metric until the run passes. In a data
    file, loosening it is a diff.

    `known_failing_cases` is deliberately NOT subtracted from anything. A case
    listed there is an open defect with a written reason, not an exemption, and
    the checker reports it separately so a floor pass can never be read as "the
    system answers these questions".
    """
    path = path or GOLD_DIR / "floor.json"
    data = _read(path)
    missing = _FLOOR_REQUIRED - set(data)
    if missing:
        raise GoldSetError(f"{path.name}: missing floor term(s) {sorted(missing)}")
    if not data["required_cases"]:
        raise GoldSetError(
            f"{path.name}: required_cases is empty, so the floor is met by a "
            f"pipeline that answers nothing."
        )
    overlap = set(data["required_cases"]) & set(data.get("known_failing_cases", {}))
    if overlap:
        raise GoldSetError(
            f"{path.name}: {sorted(overlap)} listed as both required and known "
            f"failing. A case cannot be a floor term and an exemption."
        )
    if int(data["min_distinct_dates"]) < 2:
        raise GoldSetError(
            f"{path.name}: min_distinct_dates is "
            f"{data['min_distinct_dates']}. Below two, a floor can be "
            f"calibrated from a single day — which is what "
            f"calibration_invalidated in this same file records happening on "
            f"2026-08-10, and the reason the term exists."
        )
    for case_id, reason in (data.get("known_failing_cases") or {}).items():
        if not str(reason).strip():
            raise GoldSetError(
                f"{path.name}: known_failing_cases[{case_id}] has no reason. "
                f"An unexplained known failure is an exemption, and exemptions "
                f"accumulate."
            )
    # Block E, 2026-08-26. A demotion is admissible in this file only with
    # evidence from more than one date, a diagnosis, and a written condition
    # for return. required_cases_note says removing a case because the model
    # had a bad session is how a floor is quietly lowered to whatever is
    # currently passing; this is that sentence with teeth. The three fields
    # are what separate the two acts, and nothing else does.
    for case_id, record in (data.get("demotions") or {}).items():
        if case_id in set(data["required_cases"]):
            raise GoldSetError(
                f"{path.name}: {case_id} is listed as demoted and is still in "
                f"required_cases."
            )
        if case_id not in (data.get("known_failing_cases") or {}):
            raise GoldSetError(
                f"{path.name}: {case_id} is demoted but is not tracked in "
                f"known_failing_cases. A demotion that stops being REPORTED "
                f"is a deletion, and a floor pass would then read as 'the "
                f"system answers this question'."
            )
        if not isinstance(record, dict):
            raise GoldSetError(
                f"{path.name}: demotions[{case_id}] is not a record.")
        thin = [key for key in ("evidence", "diagnosis", "reinstated_when")
                if not str(record.get(key, "")).strip()]
        if thin:
            raise GoldSetError(
                f"{path.name}: demotions[{case_id}] omits {sorted(thin)}. A "
                f"demotion without evidence, a diagnosis and a written "
                f"condition for return is not a demotion — it is the floor "
                f"lowered to whatever is currently passing, which is the move "
                f"required_cases_note forbids."
            )

    # Block F decision 4, 2026-08-28. The THIRD state, and the two ways it can
    # be abused. A promotion candidate is a case that is not failing and has
    # not met the bar; it is reported beside the floor verdict and counts
    # toward neither side of it. The checks below exist because the entry that
    # created this state was a case sitting in known_failing_cases recording,
    # in its own text, that it passed 12/12 — a file asserting the opposite of
    # what it had measured, for two days, because no state fitted.
    for case_id, record in (data.get("promotion_candidates") or {}).items():
        if case_id in set(data["required_cases"]):
            raise GoldSetError(
                f"{path.name}: {case_id} is a promotion candidate and is "
                f"already in required_cases. A case cannot be both waiting for "
                f"the bar and counted as having met it."
            )
        if case_id in (data.get("known_failing_cases") or {}):
            raise GoldSetError(
                f"{path.name}: {case_id} is listed as a promotion candidate "
                f"AND as known-failing. That contradiction is exactly the one "
                f"this state was added to end, on 2026-08-28: an entry saying "
                f"a case fails while recording that it passes."
            )
        if not isinstance(record, dict):
            raise GoldSetError(
                f"{path.name}: promotion_candidates[{case_id}] is not a "
                f"record.")
        thin = [key for key in ("evidence", "bar")
                if not str(record.get(key, "")).strip()]
        if thin:
            raise GoldSetError(
                f"{path.name}: promotion_candidates[{case_id}] omits "
                f"{sorted(thin)}. A candidate with no written bar is a case "
                f"that gets promoted whenever someone next looks at it, which "
                f"is the demotion rule's failure mode pointing upward."
            )

    # The scope rule that decides which archived sweeps may calibrate. An
    # exclusion with no reason beside it is a file moved out of the way.
    scope = data.get("calibration_scope") or {}
    if scope:
        if int(scope.get("min_cases_per_sweep") or 0) < 1:
            raise GoldSetError(
                f"{path.name}: calibration_scope.min_cases_per_sweep is "
                f"{scope.get('min_cases_per_sweep')!r}. A scope that admits a "
                f"sweep of no cases is not a scope."
            )
        for name, reason in (scope.get("excluded_by_rule") or {}).items():
            if not str(reason).strip():
                raise GoldSetError(
                    f"{path.name}: calibration_scope.excluded_by_rule[{name}] "
                    f"has no reason. An unexplained exclusion is a file moved "
                    f"out of the way with extra steps."
                )
        # Block F decision 2, 2026-08-28. The arm clause is optional — a floor
        # file written before it existed does not silently acquire one — but a
        # HALF-declared arm is worse than none, because calibration_eligibility
        # would compare against a None alias and pass everything that also
        # recorded None.
        arm = scope.get("arm")
        if arm is not None:
            if not isinstance(arm, dict) or not str(
                    arm.get("model_alias", "")).strip():
                raise GoldSetError(
                    f"{path.name}: calibration_scope.arm names no "
                    f"model_alias. An arm clause that cannot say which alias "
                    f"it means admits every sweep that also says nothing."
                )
            try:
                float(arm.get("temperature"))
            except (TypeError, ValueError):
                raise GoldSetError(
                    f"{path.name}: calibration_scope.arm.temperature is "
                    f"{arm.get('temperature')!r}. Ruling 22 makes temperature "
                    f"a recorded quantity; an arm that does not state one is "
                    f"half a pair, and the pair is the whole point."
                ) from None
    return data


def band_at_least(observed: str, floor: str) -> bool:
    return BAND_ORDER.get(observed, -1) >= BAND_ORDER[floor]


def _read(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise GoldSetError(f"gold file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GoldSetError(f"{path}: invalid JSON — {exc}") from exc
