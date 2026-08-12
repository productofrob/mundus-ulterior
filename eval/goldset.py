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
    expect_answer_contains: list[str] = field(default_factory=list)
    # Each inner list is a set of acceptable wordings, one of which must appear.
    # `[["tortoise-shell", "tortoise shell"]]` accepts either spelling; two
    # separate entries would demand both.
    expect_answer_contains_any: list[list[str]] = field(default_factory=list)
    expect_answer_excludes: list[str] = field(default_factory=list)
    expect_min_resolved_quotes: int = 0
    # Recorded, never sufficient. See _has_content_assertion.
    expect_grounded: bool | None = None
    # Some questions the corpus genuinely cannot answer, and refusing is right.
    # Same shape as TranslationCase.expect_untranslatable: asserting it is a
    # claim about the corpus and must be justified in the file, not inherited.
    expect_refusal: bool = False
    refusal_is_correct_because: str = ""
    archived_status: str = ""
    note: str = ""


_ANSWER_REQUIRED = {"id", "question", "why"}
_ANSWER_OPTIONAL = {
    "expect_cited_docs", "expect_cited_chunks", "expect_quoted_docs",
    "expect_answer_contains",
    "expect_answer_contains_any", "expect_answer_excludes",
    "expect_min_resolved_quotes", "expect_grounded", "expect_refusal",
    "refusal_is_correct_because", "archived_status", "note",
}

# The assertions that say something about what the answer SAYS, as opposed to
# whether it was tidy about citing. A case built only from the latter cannot
# fail a refusal, and a refusal is trivially grounded.
_CONTENT_KEYS = (
    "expect_answer_contains",
    "expect_answer_contains_any",
    "expect_answer_excludes",
    "expect_cited_docs",
    "expect_cited_chunks",
    "expect_quoted_docs",
)


def _has_content_assertion(raw: dict) -> bool:
    if any(raw.get(key) for key in _CONTENT_KEYS):
        return True
    return int(raw.get("expect_min_resolved_quotes", 0) or 0) > 0


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
    """
    path = path or GOLD_DIR / "answer_cases.json"
    data = _read(path)

    cases: list[AnswerCase] = []
    seen: set[str] = set()
    for i, raw in enumerate(data.get("cases", [])):
        where = f"{path.name} case[{i}]"
        _check_keys(raw, _ANSWER_REQUIRED, _ANSWER_OPTIONAL, where)

        if raw["id"] in seen:
            raise GoldSetError(f"{where}: duplicate case id {raw['id']!r}")
        seen.add(raw["id"])

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
        for j, group in enumerate(raw.get("expect_answer_contains_any", [])):
            if not isinstance(group, list) or not group:
                raise GoldSetError(
                    f"{where}: expect_answer_contains_any[{j}] must be a "
                    f"non-empty list of acceptable wordings. An empty group "
                    f"would be satisfied by any answer at all."
                )
            if any(not str(item).strip() for item in group):
                raise GoldSetError(
                    f"{where}: expect_answer_contains_any[{j}] contains an "
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
                 "expect_cited_chunks", "expect_quoted_docs")
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

        cases.append(
            AnswerCase(
                id=raw["id"],
                question=raw["question"],
                why=raw["why"],
                expect_cited_docs=list(raw.get("expect_cited_docs", [])),
                expect_cited_chunks=list(raw.get("expect_cited_chunks", [])),
                expect_quoted_docs=list(raw.get("expect_quoted_docs", [])),
                expect_answer_contains=list(raw.get("expect_answer_contains", [])),
                expect_answer_contains_any=[
                    list(group) for group in raw.get("expect_answer_contains_any", [])
                ],
                expect_answer_excludes=list(raw.get("expect_answer_excludes", [])),
                expect_min_resolved_quotes=minimum,
                expect_grounded=raw.get("expect_grounded"),
                expect_refusal=refusal,
                refusal_is_correct_because=raw.get("refusal_is_correct_because", ""),
                archived_status=raw.get("archived_status", ""),
                note=raw.get("note", ""),
            )
        )

    if not cases:
        raise GoldSetError(f"{path}: no answer cases defined")
    return cases


# --------------------------------------------------------------------------
# The Part 8 floor
# --------------------------------------------------------------------------

_FLOOR_REQUIRED = {"required_cases", "max_refusal_rate",
                   "max_unstable_content_cells", "min_repetitions"}


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
    for case_id, reason in (data.get("known_failing_cases") or {}).items():
        if not str(reason).strip():
            raise GoldSetError(
                f"{path.name}: known_failing_cases[{case_id}] has no reason. "
                f"An unexplained known failure is an exemption, and exemptions "
                f"accumulate."
            )
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
