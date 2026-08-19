"""C2 — the query, rendered into every language the index holds.

Block C ruling 10 established what C2 is: **query translation, not hybrid
lexical+dense.** Every non-English target in the gold set ranks 1 when queried in
its own language and 5-309 from English. The index is not the bottleneck, the
passage embeddings are not the bottleneck, the reranker is not the bottleneck.
The language of the QUERY is.

Everything in this module is pure. The chat call that produces a rendering lives
in `answer.translate.render_query`, and the file it writes is produced once by
`scripts/build_query_renderings.py` and read from disk thereafter (ruling 19), so
the rule that decides whether a C2 number means anything is testable and
mutatable without a database, a gateway or a single API call.

The four rulings this file implements
-------------------------------------

**Ruling 12 — the language set is derived from the INDEX, never from the pair.**
`target_langs()` takes the languages present in the searched view and the
query's own language. It takes nothing else, and the signature is the assertion:
there is no parameter through which `expect_lang`, `expect_doc`, `lang_pool` or
`region` could reach it. Choosing a target language by reading the pair's
`expect_lang` is using the answer to find the answer, and a run built that way
measures nothing.

The same guarantee is built into the FILE. `query_renderings.json` is keyed on
query TEXT and holds no pair id at all, so it is structurally incapable of
recording a per-pair language choice. A future edit cannot introduce leakage
here without first changing the schema, which is a visible act.

**Ruling 15b — the rule is uniform.** A query is rendered into every non-English
language in the view except its own; its own text is always one of the variants.
The five native-language queries are therefore exercised like everything else,
and the assertion that replaces invariance is `native_query_problems()`: for a
native-language query the winning variant must be its own language, and its rank
must not get worse. A rendering beating the native text on a native query is a
finding to be printed, not a pass.

**Ruling 17(a) — the script check.** `answer/translate.py` carries this failure
in its own comment: v1 back-translated Old Tamil into Latin romanisation and
scored chrF 0.004, *"measuring alphabets"*. The same failure in a query rendering
would be invisible — a romanised Tamil query simply retrieves badly, which is the
thing C2 is trying to fix, and no number would say which had happened. So a
rendering that is not in the writing system its language uses is REFUSED: not
embedded, not fused, and recorded as a rejection.

**Ruling 19 — the renderings are frozen data.** `digest()` is recorded in every
archived run. `chat-default` is an alias that will be repointed, and C5-C6's
"two days, frozen configuration" is only true if the queries are byte-identical
on both days.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

# v2, 2026-08-16. A row gained `attempts`, because v1 let a retry DESTROY the
# rendering it replaced and the ruling-20 retry pass then did exactly that:
# seven of ten Old Tamil rows came back worse than the text they overwrote, one
# of them going from a single stray letter to thirty-six, and the better strings
# were gone. A file that cannot lose evidence is worth a schema bump.
SCHEMA = "mundus-ulterior/query-renderings/v2"
SUPERSEDED_SCHEMAS = frozenset({"mundus-ulterior/query-renderings/v1"})
DEFAULT_PATH = Path("eval/gold/query_renderings.json")


class RenderingError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# Ruling 12 — the language rule, and the signature IS the assertion
# --------------------------------------------------------------------------

def target_langs(index_langs, query_lang: str) -> list[str]:
    """Which languages this query is rendered into.

    Two arguments, both of them facts about the index and the query. There is
    deliberately no third: a pair cannot reach this function, so no target
    language can ever be chosen by reading the answer.

    English is excluded because the index's English is what an English query
    already reaches — rendering an English query into English is the arm ruling
    14 calls the single-variant arm, and it is the query's own text, not a
    rendering. The query's own language is excluded because rendering Greek into
    Greek is a no-op that would spend a call to produce a second copy of the
    input, and a model asked to do it does not reliably return one.
    """
    return sorted({
        lang for lang in index_langs
        if lang and lang != "en" and lang != query_lang
    })


def expected_rendering_count(index_langs, query_langs) -> int:
    """Total renderings the file must hold. The cost, computed not estimated."""
    return sum(len(target_langs(index_langs, q)) for q in query_langs)


# --------------------------------------------------------------------------
# Ruling 17(a) — the script check
# --------------------------------------------------------------------------

# Unicode ranges per writing system. Named ranges rather than a `str.isascii()`
# heuristic because the two failure directions are different: a Tamil rendering
# that came back romanised is all-Latin, and a Parthian rendering that came back
# in Greek characters is all-Greek. One test cannot see both.
SCRIPT_RANGES: dict[str, tuple[tuple[int, int], ...]] = {
    "greek": ((0x0370, 0x03FF), (0x1F00, 0x1FFF)),
    "han": ((0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF)),
    "tamil": ((0x0B80, 0x0BFF),),
    "ethiopic": ((0x1200, 0x137F), (0x1380, 0x139F)),
    "aramaic": ((0x0700, 0x074F), (0x10840, 0x1085F), (0x05D0, 0x05EA)),
    # U+02B0-02FF is Spacing Modifier Letters, and it is here because scholarly
    # transliteration of Semitic languages needs it: ʾ (alef) and ʿ (ayin) are
    # letters by Unicode category and are NOT in any Latin block. Without this
    # range, 118 admitted Sabaic and Nabataean renderings read as impure and a
    # whole-language guard would refuse the corpus's own convention. Added
    # 2026-08-16 with ruling 20, measured: it moves 117 of 118 Latin renderings
    # from "impure" to "wholly Latin", and the one that remains is a genuine
    # stray Greek gamma.
    "latin": ((0x0041, 0x005A), (0x0061, 0x007A), (0x00C0, 0x024F),
              (0x02B0, 0x02FF), (0x1E00, 0x1EFF)),
}

# Which script each language's rendering must be in. Derived from
# `answer.translate`'s two sets rather than restated, so there is one definition
# of "this language is stored romanised" in the repository. Built at import so a
# language added to translate.py and not here fails loudly at `required_script`.
_NATIVE_SCRIPT_OF = {
    "grc": "greek",
    "lzh": "han",
    "oty": "tamil",
    "gez": "ethiopic",
    "arc": "aramaic",
}

# The floor, and it is a ratio rather than "contains one character of the right
# script". A rendering reading "大秦 is the country the query asks about" would
# pass an any-character test while being English.
#
# **Set at 0.6 on 2026-08-16 and raised to 1.0 the same day, by measurement.**
# The argument for 0.6 was that a faithful rendering may keep a Latin proper
# name or a section number, and that a WHOLE rendering in the wrong script sits
# at 0.0, nowhere near the threshold. The first run over the real gold set
# showed the band between those two is not empty. It admitted, among others:
#
#     கேரளக் கரையில்발掘된 지중해 amphora sherds        66% Tamil
#     — Tamil, Hangul, Han, Malayalam and Latin in one string
#     அடுலிस் நगரம் மற்றும் அக்सுமीत राजधानीக்கு …    78% Tamil, rest Devanagari
#     乳香國及阿拉伯之Kane港                             69% Han
#
# Ten of 205 renderings sat in that band. A rendering a third of which is in
# another writing system is not a rendering, and no rank it produced would say
# so. At 1.0 the rule is also easier to state and to argue with: **a rendering
# contains no letter outside its own writing system.** The cost is ten
# re-renderings; the ratio is still reported, because "0% Tamil" and "78% Tamil
# with Devanagari" are different diagnoses and the run should print which.
SCRIPT_FLOOR = 1.0


def required_script(lang: str) -> str:
    """The writing system a rendering into `lang` must use. Ruling 17(a)."""
    from answer.translate import LANG_NAMES, TRANSLITERATED_LANGS

    if lang in _NATIVE_SCRIPT_OF:
        return _NATIVE_SCRIPT_OF[lang]
    if lang in TRANSLITERATED_LANGS:
        return "latin"
    if lang in ("en", "la"):
        return "latin"
    raise RenderingError(
        f"no writing system is declared for {lang!r} "
        f"({LANG_NAMES.get(lang, 'unknown to translate.py')}). A rendering "
        f"cannot be script-checked, so it cannot be admitted. Add it to "
        f"retrieve.render._NATIVE_SCRIPT_RANGES or to "
        f"answer.translate.TRANSLITERATED_LANGS — whichever is true — rather "
        f"than letting an unchecked rendering into a run."
    )


# Combining diacritics that belong to NO script: U+0300-036F is shared by Greek,
# by scholarly Latin transliteration and by much else. Excluded from both sides
# of the ratio, because requiring them to sit inside a script's own block would
# refuse correct Greek and correct transliteration alike.
_NEUTRAL_MARKS = (0x0300, 0x036F)


def counted_characters(text: str) -> list[str]:
    """The characters the script check judges: letters AND script-specific marks.

    Ruling 23. Letters alone was the rule until 2026-08-16, and it had a hole
    the size of an Indic script: vowel signs are Unicode category Mn/Mc, not L,
    so this passed at "100% Tamil" —

        அடுலിசிலிருந்து என்ன ஏற்றுமதி செய்யப்பட்டது?
              ^ MALAYALAM VOWEL SIGN I, inside the place name

    and that is the query for `adulis-exports`, the pair C2a's collapse moved
    from 15 to 3. In an Indic script the vowel signs carry much of the
    phonology; a foreign one is exactly the failure the guard exists to catch.

    Digits, punctuation and whitespace stay out: they are shared between writing
    systems and counting them would let a rendering pass on its section numbers.
    A script's OWN marks need no special case — Tamil's live inside the Tamil
    block already, and Greek's are neutral.
    """
    out = []
    for char in text or "":
        category = unicodedata.category(char)
        if category.startswith("L"):
            out.append(char)
        elif category in ("Mn", "Mc", "Me") and not (
                _NEUTRAL_MARKS[0] <= ord(char) <= _NEUTRAL_MARKS[1]):
            out.append(char)
    return out


def script_ratio(text: str, script: str) -> float:
    """Share of the text's judged characters that belong to `script`."""
    ranges = SCRIPT_RANGES[script]
    counted = counted_characters(text)
    if not counted:
        return 0.0
    hits = sum(
        1 for c in counted
        if any(lo <= ord(c) <= hi for lo, hi in ranges)
    )
    return hits / len(counted)


def foreign_characters(text: str, script: str) -> dict[str, int]:
    """The characters that do NOT belong to `script`, and how many of each.

    Named, not counted. The 2026-08-16 review of 205 renderings was only
    possible because the offending characters could be read: `發`, `된`,
    Devanagari `स`, Malayalam `ൽ`. A refusal that says "78%" sends you back to
    the file; a refusal that says "8 Devanagari letters" is the diagnosis.
    """
    ranges = SCRIPT_RANGES[script]
    out: dict[str, int] = {}
    for char in counted_characters(text):
        if any(lo <= ord(char) <= hi for lo, hi in ranges):
            continue
        out[char] = out.get(char, 0) + 1
    return out


def rendering_problems(text: str, lang: str, source_text: str = "") -> list[str]:
    """Why this rendering may not be admitted. Empty means it may.

    Three refusals, and each is a failure mode with a name:

      empty       the model returned nothing usable; `parse_translation` already
                  records the broken output contract, and an empty query would
                  otherwise be embedded and would retrieve noise.
      script      the alphabet failure — the Part 4 chrF-0.004 incident, in the
                  one place where it produces a bad number instead of a bad row.
      echo        the model returned the input. A rendering identical to the
                  English query is not a rendering; fused by max it is a second
                  copy of the single-variant arm and would make C2 look free.
    """
    problems: list[str] = []
    if not (text or "").strip():
        problems.append("empty: the model returned no usable rendering")
        return problems

    script = required_script(lang)
    ratio = script_ratio(text, script)
    if ratio < SCRIPT_FLOOR:
        strays = foreign_characters(text, script)
        named = "".join(
            sorted(strays, key=lambda c: -strays[c])
        )[:18]
        problems.append(
            f"script: {ratio:.0%} of the judged characters are {script}, "
            f"floor is "
            f"{SCRIPT_FLOOR:.0%}; {sum(strays.values())} stray character(s) "
            f"[{named}]. A rendering in the wrong writing system retrieves "
            f"badly for a reason no rank can report."
        )

    if source_text and text.strip() == source_text.strip():
        problems.append(
            "echo: the rendering is identical to the query it was made from"
        )
    return problems


# --------------------------------------------------------------------------
# The file — ruling 19, and ruling 12's structural half
# --------------------------------------------------------------------------

@dataclass
class Variant:
    """One query text that will be embedded and searched.

    `source` is "query" for the pair's own text and "rendering" for a produced
    one. The fused score records which variant won, and a run in which the
    winner is "query" for every pair is a run in which C2 did nothing — which is
    a result, and one the header must be able to state.
    """
    lang: str
    text: str
    source: str


@dataclass
class Renderings:
    path: Path
    prompt_version: str
    chat_model: str
    view: str
    index_langs: list[str]
    by_query: dict[str, dict[str, dict]] = field(default_factory=dict)
    digest: str = ""
    # Rows whose verdict on disk disagrees with the current guard. Ruling 24:
    # reported by every run, because a file judged under an older rule and a
    # file judged under this one are different configurations, and the content
    # hash alone cannot tell them apart.
    stale: list = field(default_factory=list)

    def variants_for(self, query: str, query_lang: str) -> list[Variant]:
        """The query's own text first, then every admitted rendering.

        Keyed on the query TEXT. Nothing about the pair is consulted, and the
        file holds no pair id to consult.
        """
        out = [Variant(query_lang, query, "query")]
        entry = self.by_query.get(query)
        if entry is None:
            raise RenderingError(
                f"no renderings for a query the run is about to embed:\n"
                f"  {query[:90]!r}\n"
                f"The gold set and {self.path} disagree. Re-run "
                f"`python scripts/build_query_renderings.py` — a run that "
                f"silently fell back to the English-only arm for some pairs and "
                f"not others would report a C2 number about a configuration "
                f"nobody chose."
            )
        for lang in sorted(entry):
            row = entry[lang]
            if row.get("ok"):
                out.append(Variant(lang, row["text"], "rendering"))
        return out

    def rejected(self) -> list[tuple[str, str, list[str]]]:
        """(query, lang, problems) for every rendering the guard refused."""
        out = []
        for query, entry in self.by_query.items():
            for lang, row in sorted(entry.items()):
                if not row.get("ok"):
                    out.append((query, lang, row.get("problems", [])))
        return out


def best_attempt(attempts: list[dict]) -> dict | None:
    """Which attempt IS the rendering. Never simply the most recent one.

    The ruling-20 retry pass is the argument. It was written on the reasoning
    that a corrective prompt naming the writing system would do better than the
    prompt that had just failed; measured, it did worse on seven of ten Old
    Tamil rows and better on one. A pipeline that takes the latest attempt would
    have replaced a rendering at 98% Tamil with one at 5% and called it a fix.

    Order: an admitted attempt beats a held one; among equals the higher script
    ratio wins; a tie keeps the EARLIER attempt, so a re-run that changes
    nothing changes nothing.
    """
    if not attempts:
        return None
    def key(pair):
        position, attempt = pair
        return (0 if attempt.get("ok") else 1,
                -float(attempt.get("script_ratio") or 0.0),
                position)
    return min(enumerate(attempts), key=key)[1]


def settle_row(row: dict, lang: str, query: str) -> dict:
    """Re-judge every attempt and promote the best to the row's own fields.

    THE VERDICT IS DERIVED, NEVER TRUSTED FROM DISK. Ruling 24, and it was
    written after the reader trusted a stored one: the file said `ok: true` for
    an Old Tamil rendering carrying a Malayalam vowel sign, because it had been
    judged under the pre-ruling-23b guard, and `load()` handed that string to
    the fusion without a word. A stored verdict is a claim about a rule that
    may since have changed; the TEXT is the evidence, and the verdict is
    recomputed from it every time the file is opened.

    Lives here, beside the guard, and is imported by
    `scripts/build_query_renderings.py` rather than copied into it. Two
    definitions of "which attempt is this row" agree until they do not, and the
    writer and the reader disagreeing is the worst place for that.
    """
    attempts = row.get("attempts")
    if not attempts:
        attempts = [{
            "text": row.get("text", ""),
            "notes": row.get("notes", []),
            "prompt_version": row.get("prompt_version"),
            "chat_model": row.get("chat_model"),
            "temperature": row.get("temperature"),
        }]
        row["attempts"] = attempts
    for attempt in attempts:
        if attempt.get("call_failed"):
            # Keep the provider's reason. Re-judging it would replace "the model
            # refuses temperature=0" with "empty", which is true and useless.
            attempt["ok"] = False
            attempt.setdefault("script_ratio", 0.0)
            continue
        problems = rendering_problems(attempt.get("text", ""), lang,
                                      source_text=query)
        attempt["ok"] = not problems
        attempt["problems"] = problems
        attempt["script_ratio"] = round(
            script_ratio(attempt.get("text", ""), required_script(lang)), 4)
    best = best_attempt(attempts) or {}
    row["text"] = best.get("text", "")
    row["ok"] = bool(best.get("ok"))
    row["problems"] = best.get("problems", [])
    row["notes"] = best.get("notes", [])
    row["prompt_version"] = best.get("prompt_version")
    row["chat_model"] = best.get("chat_model")
    row["temperature"] = best.get("temperature")
    row["script_ratio"] = best.get("script_ratio")
    row["attempt_count"] = len(attempts)
    return row


def digest(path: Path) -> str:
    """Content hash of the rendering file, recorded in every archived run.

    Ruling 19. Two runs on different days are the same configuration only if
    this string is the same in both.
    """
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def load(path: Path | str = DEFAULT_PATH) -> Renderings:
    path = Path(path)
    if not path.exists():
        raise RenderingError(
            f"{path} does not exist. C2 reads its renderings from disk rather "
            f"than producing them per run (ruling 19), so build them first:\n"
            f"    python scripts/build_query_renderings.py"
        )
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema") in SUPERSEDED_SCHEMAS:
        raise RenderingError(
            f"{path} declares schema {doc.get('schema')!r}, which is superseded "
            f"by {SCHEMA!r}. A v1 row holds one text and no attempt history, so "
            f"a run reading it could not say whether a rendering had been "
            f"retried or what the retry replaced. Re-run "
            f"`python scripts/build_query_renderings.py` — it upgrades the file "
            f"in place without spending a call."
        )
    if doc.get("schema") != SCHEMA:
        raise RenderingError(
            f"{path} declares schema {doc.get('schema')!r}, expected {SCHEMA!r}."
        )
    if "pair_ids" in json.dumps(doc):
        raise RenderingError(
            f"{path} mentions pair ids. Ruling 12: the file is keyed on query "
            f"text and holds nothing about a pair, so that a per-pair language "
            f"choice cannot be recorded here even by accident."
        )
    # Ruling 24. Every row is re-judged against the CURRENT guard as it is
    # read, and how many disagreed with the file is recorded. A reader that
    # trusts a stored `ok` is a reader that will embed whatever the last guard
    # happened to permit.
    by_query: dict[str, dict] = {}
    stale: list[tuple[str, str, bool]] = []
    for entry in doc.get("queries", []):
        rows = entry.get("renderings", {})
        for lang, row in rows.items():
            was_ok, was_text = row.get("ok"), row.get("text")
            settle_row(row, lang, entry["query"])
            if was_ok is not None and was_ok != row["ok"]:
                stale.append((entry["query"], lang, row["ok"]))
            elif was_text is not None and was_text != row["text"]:
                stale.append((entry["query"], lang, row["ok"]))
        by_query[entry["query"]] = rows

    return Renderings(
        path=path,
        prompt_version=doc.get("prompt_version", ""),
        chat_model=doc.get("chat_model") or doc.get("chat_model_this_run", ""),
        view=doc.get("view", ""),
        index_langs=list(doc.get("index_langs", [])),
        by_query=by_query,
        digest=digest(path),
        stale=stale,
    )


def coverage_problems(renderings: Renderings, queries: dict[str, str],
                      index_langs) -> list[str]:
    """Why this rendering file may not be used for this run. Empty means it may.

    `queries` is {query text -> query_lang} from the gold set. The check is
    two-directional on purpose: a file missing a query silently degrades that
    pair to the single-variant arm, and a file built against a different index
    silently measures a language set nobody chose.
    """
    problems: list[str] = []

    if sorted(set(index_langs)) != sorted(set(renderings.index_langs)):
        problems.append(
            f"the file was built against index languages "
            f"{sorted(set(renderings.index_langs))} and this run's view holds "
            f"{sorted(set(index_langs))}. Ruling 12 derives the language set "
            f"from the index, so a different index is a different rule."
        )

    for query, query_lang in sorted(queries.items()):
        entry = renderings.by_query.get(query)
        if entry is None:
            problems.append(f"no renderings for query: {query[:70]!r}")
            continue
        wanted = set(target_langs(index_langs, query_lang))
        have = set(entry)
        if wanted - have:
            problems.append(
                f"{query[:50]!r} is missing renderings for "
                f"{sorted(wanted - have)}"
            )
        if have - wanted:
            problems.append(
                f"{query[:50]!r} has renderings for {sorted(have - wanted)}, "
                f"which ruling 12's rule does not ask for"
            )
    return problems


# --------------------------------------------------------------------------
# Ruling 15b — the assertion that replaces invariance
# --------------------------------------------------------------------------

def native_query_problems(query_lang: str, winning_lang: str | None,
                          rank_single: int | None, rank_fused: int | None
                          ) -> list[str]:
    """Ruling 15b's control, for one pair whose query is not English.

    Not a gate and not an exception: a violation is a FINDING, printed beside
    the number. The four native-language probes rank 1 in their own language,
    so a rendering winning over the native text, or a native pair getting worse
    under fusion, means the harness is doing something other than what it says
    — and saying so is the whole reason ruling 15b was preferred to an
    exemption that could never have found out.
    """
    if query_lang == "en":
        return []
    problems: list[str] = []
    if winning_lang is not None and winning_lang != query_lang:
        problems.append(
            f"a {winning_lang} rendering beat the query's own {query_lang} "
            f"text on a query already written in the target language"
        )
    if (rank_single is not None and rank_fused is not None
            and rank_fused > rank_single):
        problems.append(
            f"fusion moved a native-language query from rank {rank_single} to "
            f"{rank_fused}"
        )
    if rank_single is not None and rank_fused is None:
        problems.append(
            f"fusion lost a native-language query that ranked {rank_single}"
        )
    return problems
