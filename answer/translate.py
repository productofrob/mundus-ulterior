"""In-loop translation, routed through the LiteLLM gateway.

Two calls, deliberately isolated from each other:

  forward   source-language chunk  ->  English
  backward  that English           ->  source language

The backward call must not see the original. If it does, the model can copy
wording it was never given by the translation, and the confidence score stops
measuring anything — it measures leakage. So each direction is a fresh request
with no conversation history, and `build_back_messages` is covered by a test
that asserts the original text does not appear anywhere in the payload.

Output contract
---------------
Chat models like to introduce themselves ("Here is the translation:"). A
preamble is not a translation, and silently keeping it would inflate length and
depress every similarity score. So the prompt demands the translation inside
<translation></translation> tags and `parse_translation` extracts it. If the
tags are missing we fall back to stripping known preamble shapes and record a
note rather than pretending the response was clean.

Provenance
----------
`prompt_version` is stored beside every translation for the same reason
`embedding_model` is stored beside every vector (Part 4): a prompt change makes
old and new output incomparable, and a cache with no version column cannot tell
you which is which. Bump PROMPT_VERSION whenever the prompt text changes.
"""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field

# Reused rather than re-implemented. These classifiers were the fix for a real
# incident in Part 4 — LiteLLM reports upstream provider rate limits as
# `APIConnectionError`, so a naive connection check sends you to debug a healthy
# gateway. Importing them keeps one definition; a second copy would drift.
from ingest.embed import (
    RATE_LIMIT_BACKOFF_SECONDS,
    _is_connection_error,
    _is_rate_limit_error,
    _make_client,
)

DEFAULT_MODEL = "chat-default"          # gateway alias, see gateway/config.yaml
PROMPT_VERSION = "p6-translate-v1"
# v2 (2026-08-10): the first live run back-translated Old Tamil into Latin
# romanisation, because the prompt asked for transliteration where the corpus
# stores transliteration and said nothing at all in the other direction. The
# resulting chrF of 0.004 was measuring alphabets. Bumped rather than edited in
# place: prompt_version is part of the primary key, so v1 rows stay readable and
# distinguishable instead of being silently overwritten by v2 output.
BACK_PROMPT_VERSION = "p6-backtranslate-v2"
# C2 (Block C ruling 12). A THIRD direction, and a third version, because a
# query is not a passage: it is short, it is usually interrogative, and the
# thing it has to survive is retrieval rather than a chrF score. Sharing
# BACK_PROMPT_VERSION would put two different jobs under one provenance string
# and make a rendering indistinguishable from a back-translation afterwards —
# the exact confusion `prompt_version` exists to prevent.
#
# v1 renders the query in its OWN grammatical form: a question stays a question.
# Changing form and language at once would confound two interventions, and the
# gold set's English queries are questions. If C2 falls short, "the rendering
# style was a variable nobody varied" is the first thing to check, and it is
# checked by bumping this string rather than by editing the prompt in place.
QUERY_PROMPT_VERSION = "c2-render-v1"
# Ruling 20's retry, and it needs its own version for a reason worth stating.
# `_chat` runs at temperature=0 so the harness is reproducible; re-issuing the
# SAME prompt to the same model is therefore not a retry at all, it is the same
# call, and it would return the same wrong-script rendering while looking like a
# second attempt. A retry has to be a different prompt, and a different prompt
# has to be a different version — otherwise the file would hold two prompts'
# output under one provenance string.
QUERY_RETRY_PROMPT_VERSION = "c2-render-retry-v1"

MAX_RETRIES = 3
BACKOFF_SECONDS = 2.0
DEFAULT_MAX_TOKENS = 2048

# Language names for the prompt. Codes are the ones the corpus actually uses
# (see `chunks.lang`); an unknown code degrades to the bare code plus a note
# rather than guessing, because a wrong language name in the prompt is a silent
# translation error.
LANG_NAMES: dict[str, str] = {
    "grc": "Ancient Greek (Koine)",
    "lzh": "Literary Chinese (Classical Chinese)",
    "oty": "Old Tamil",
    "xpr": "Parthian, in scholarly Latin transliteration",
    "xna": "Ancient North Arabian (Nabataean Aramaic), in scholarly Latin transliteration",
    "xsa": "Ancient South Arabian (Sabaic), in scholarly Latin transliteration",
    "gmq-pro": "Proto-Norse, in runic transliteration",
    "ocm": "Old Cham, in scholarly Latin transliteration",
    "arc": "Aramaic",
    "gez": "Ge'ez (Classical Ethiopic)",
    "la": "Latin",
    "en": "English",
}

# Scripts that are romanised in this corpus rather than stored in their own
# characters. Back-translating into these means producing a transliteration, and
# the prompt has to say so or the model will answer in Arabic or Devanagari
# script and every character-level score will read as a total failure.
TRANSLITERATED_LANGS = {"xpr", "xna", "xsa", "gmq-pro", "ocm"}

# The other half of the same rule, and the half that was missing in v1. These
# languages are stored in their own characters, so a back-translation must come
# back in those characters. Saying nothing left the choice to the model, and on
# Old Tamil it chose romanisation — producing a chrF of 0.004 that looked like a
# translation failure and was a writing-system mismatch.
NATIVE_SCRIPT_LANGS = {
    "grc": "the Greek alphabet, polytonic",
    "lzh": "Chinese characters",
    "oty": "the Tamil script",
    "gez": "the Ethiopic (Ge'ez) script",
    "arc": "the Aramaic script",
}


class TranslationError(RuntimeError):
    pass


# A third classifier, beside `_is_rate_limit_error` and `_is_connection_error`
# and for the same reason: the provider reports this as a bare 400, which a
# naive handler retries three times and then reports as "translation failed",
# sending you to debug a prompt. Block C ruling 22 — the first `--model
# chat-strong` run spent 615 requests on it before it was stopped by hand.
def _is_unsupported_temperature(message: str) -> bool:
    lowered = (message or "").lower()
    return ("temperature" in lowered
            and ("does not support" in lowered
                 or "unsupportedparams" in lowered
                 or "only temperature=1" in lowered))


@dataclass
class Translation:
    """One direction of one round trip."""
    text: str
    source_lang: str
    target_lang: str
    model: str
    prompt_version: str
    raw_response: str = ""
    notes: list[str] = field(default_factory=list)
    retries: int = 0
    # WHAT SAMPLER PRODUCED THIS. Block C ruling 22: claude-sonnet-5 refuses
    # temperature=0 outright, so a stronger model cannot be a drop-in for a
    # harness whose reproducibility argument was "temperature=0". Recorded
    # rather than assumed, because a rendering sampled at 1.0 and one decoded
    # at 0.0 are not the same measurement and nothing else in the row says so.
    temperature: float = 0.0

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()


def language_name(code: str) -> str:
    return LANG_NAMES.get(code, code)


# --------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------

SYSTEM_FORWARD = (
    "You are a philological translator working on ancient and medieval sources "
    "for a scholarly database. You translate the supplied passage and do "
    "nothing else.\n"
    "Rules:\n"
    "1. Translate the whole passage, omitting nothing and adding nothing.\n"
    "2. Do not explain, comment, annotate, or supply historical background.\n"
    "3. Keep section numbers, line numbers and paragraph breaks exactly where "
    "they are in the source.\n"
    "4. Transliterate proper names; do not substitute modern equivalents.\n"
    "5. If a stretch is genuinely unreadable, write [illegible] in its place. "
    "Never invent content to fill a gap.\n"
    "6. Reply with the translation only, wrapped in "
    "<translation></translation> tags, and nothing outside those tags."
)

SYSTEM_BACK = (
    "You are a philological translator working on ancient and medieval sources. "
    "You will be given an English passage. Render it into {target_name}, as a "
    "translator working into that language would.\n"
    "Rules:\n"
    "1. Translate the whole passage, omitting nothing and adding nothing.\n"
    "2. Do not explain, comment, or annotate.\n"
    "3. Keep section numbers, line numbers and paragraph breaks where they are.\n"
    "{script_rule}"
    "4. Reply with the translation only, wrapped in "
    "<translation></translation> tags, and nothing outside those tags."
)

_TRANSLITERATION_RULE = (
    "3a. Write in the standard scholarly Latin transliteration for that "
    "language, with its usual diacritics — not in its historical script.\n"
)

_NATIVE_SCRIPT_RULE = (
    "3a. Write in {script}. Do NOT romanise or transliterate: the text this "
    "will be compared against is in that script, and a romanised answer cannot "
    "be compared with it at all.\n"
)


def build_forward_messages(text: str, source_lang: str) -> list[dict]:
    """Messages for source-language -> English."""
    return [
        {"role": "system", "content": SYSTEM_FORWARD},
        {
            "role": "user",
            "content": (
                f"Source language: {language_name(source_lang)}\n"
                f"Target language: English\n\n"
                f"Passage:\n{text}"
            ),
        },
    ]


def build_back_messages(english_text: str, target_lang: str) -> list[dict]:
    """Messages for English -> source language.

    Takes the English only. The original passage is not a parameter of this
    function, which is the point: a back-translation that has seen the original
    proves nothing about the forward translation.
    """
    if target_lang in TRANSLITERATED_LANGS:
        script_rule = _TRANSLITERATION_RULE
    elif target_lang in NATIVE_SCRIPT_LANGS:
        script_rule = _NATIVE_SCRIPT_RULE.format(script=NATIVE_SCRIPT_LANGS[target_lang])
    else:
        script_rule = ""

    system = SYSTEM_BACK.format(
        target_name=language_name(target_lang), script_rule=script_rule
    )
    return [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": (
                f"Source language: English\n"
                f"Target language: {language_name(target_lang)}\n\n"
                f"Passage:\n{english_text}"
            ),
        },
    ]


SYSTEM_RENDER = (
    "You are a philological translator working on ancient and medieval sources "
    "for a scholarly database. You will be given a SEARCH QUERY. Render it into "
    "{target_name} so that it could be used to search texts written in that "
    "language.\n"
    "Rules:\n"
    "1. Render the query itself. Do not answer it, do not explain it, and do "
    "not add background, context or commentary of any kind.\n"
    "2. Keep the query's grammatical form. A question stays a question; a "
    "phrase stays a phrase.\n"
    "3. For a place, people or title that the sources in that language have "
    "their own name for, use that name. Otherwise transliterate.\n"
    "{script_rule}"
    "4. Render the whole query, omitting nothing and adding nothing.\n"
    "5. Reply with the rendering only, wrapped in "
    "<translation></translation> tags, and nothing outside those tags."
)


_RETRY_RULE = (
    "0. A previous attempt at this returned text in the WRONG WRITING SYSTEM. "
    "Before answering, check that every letter you write belongs to the script "
    "named below. Do not mix scripts. If you cannot render a word in that "
    "script, transliterate it into that script rather than leaving it in "
    "another.\n"
)


def build_render_messages(query: str, source_lang: str, target_lang: str,
                          *, retry: bool = False) -> list[dict]:
    """Messages for one query rendering. C2, Block C ruling 12.

    The script rule is the SAME rule the back-translation uses, read from the
    same two sets, because "this language is stored romanised in this corpus" is
    one fact and a second copy of it would drift. Getting it wrong here is the
    Part 4 incident in a new place: a romanised Tamil query retrieves badly, and
    a bad rank says nothing about which of the two went wrong.

    `retrieve.render.rendering_problems` checks the output against the same
    distinction afterwards, so the rule is both asked for and verified.
    """
    if target_lang in TRANSLITERATED_LANGS:
        script_rule = _TRANSLITERATION_RULE
    elif target_lang in NATIVE_SCRIPT_LANGS:
        script_rule = _NATIVE_SCRIPT_RULE.format(script=NATIVE_SCRIPT_LANGS[target_lang])
    else:
        script_rule = ""

    system = SYSTEM_RENDER.format(
        target_name=language_name(target_lang), script_rule=script_rule
    )
    if retry:
        system = system.replace("Rules:\n", "Rules:\n" + _RETRY_RULE, 1)
    return [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": (
                f"Source language: {language_name(source_lang)}\n"
                f"Target language: {language_name(target_lang)}\n\n"
                f"Search query:\n{query}"
            ),
        },
    ]


# --------------------------------------------------------------------------
# Response parsing
# --------------------------------------------------------------------------

_TAG_RE = re.compile(r"<translation>(.*?)</translation>", re.S | re.I)

# Preamble shapes seen in practice. Only stripped when the tags are missing.
_PREAMBLE_RE = re.compile(
    r"^\s*(here(?:'s| is)[^\n:]{0,60}:|translation:|english translation:|"
    r"sure[^\n:]{0,40}:)\s*",
    re.I,
)
_TRAILER_RE = re.compile(
    r"\n\s*(note[s]?:|\(note[s]?:|this translation|the passage above)\b.*$",
    re.I | re.S,
)


def parse_translation(raw: str) -> tuple[str, list[str]]:
    """Extract the translation from a chat response.

    Returns (text, notes). A note is recorded whenever the model broke the
    output contract, so a run that quietly degraded is visible in the report
    instead of only in the scores.
    """
    notes: list[str] = []
    if raw is None:
        return "", ["empty response from the gateway"]

    matches = _TAG_RE.findall(raw)
    if matches:
        if len(matches) > 1:
            notes.append(
                f"response contained {len(matches)} <translation> blocks; "
                f"joined them in order"
            )
        return "\n\n".join(m.strip() for m in matches), notes

    notes.append(
        "response had no <translation> tags; fell back to preamble stripping. "
        "Treat the score for this row as approximate."
    )
    text = _PREAMBLE_RE.sub("", raw.strip())
    text = _TRAILER_RE.sub("", text).strip()
    # A dangling opening tag means the model was cut off mid-answer.
    if "<translation>" in text.lower():
        text = re.sub(r"</?translation>", "", text, flags=re.I).strip()
        notes.append("unclosed <translation> tag — the response may be truncated")
    return text, notes


# --------------------------------------------------------------------------
# The calls
# --------------------------------------------------------------------------

def _serving_stack(response) -> dict:
    """What the gateway says about WHICH stack served this call.

    Block E decision 3, 2026-08-26. FINDING 18 asks a question the archive
    cannot answer: five of six cases changed their answer text completely
    between two dates at temperature 0, and nothing recorded could distinguish
    provider-side drift from sampling variance. The archive carried `model` -
    which is the alias this repository SENT, and therefore cannot move.

    Keys whose value is None are OMITTED rather than written as null.
    `system_fingerprint` is an OpenAI field and this gateway fronts Anthropic,
    so it may be absent on every call; a column reading null 270 times is the
    vacuous proof BLOCK_E_START carries as trap 4, after three of them in four
    days. What is real is recorded; what is absent is recorded ONCE, in the
    result document, rather than two hundred and seventy times in the
    archives. `python scripts/probe_serving_stack.py` is what says which, and
    it costs one chat call.

    `model` is kept, but CORRECTION 4 (2026-08-28) records what it is not. It is
    the string this repository SENT, echoed back, in every path. The sweep calls
    assemble with no `model=`, so `_chat` gets DEFAULT_MODEL and all 396 Block E
    archives carry `"model": "chat-default"`. `scripts/probe_serving_stack.py`
    sent `resolve_model_label()` instead - the concrete name it had just read out
    of gateway/config.yaml - and the gateway echoed THAT. Neither reading came
    from the provider, and neither can move unless the caller moves it. It is
    recorded because it states which string this call was made with; it is NOT
    provenance, and `serving_stack_identity` excludes it for that reason.
    """
    out: dict = {}
    for key in ("id", "model", "system_fingerprint", "service_tier"):
        value = getattr(response, key, None)
        if value is not None:
            out[key] = value
    hidden = getattr(response, "_hidden_params", None)
    if isinstance(hidden, dict):
        for key in ("model_id", "custom_llm_provider"):
            if hidden.get(key) is not None:
                out[key] = hidden[key]
    return out


# Keys unique to a CALL rather than to the stack that served it, and therefore
# excluded from the stack IDENTITY. Block E corrections 3 and 4, 2026-08-28.
#
# `id` is a fresh uuid on every response. Including it in the identity made
# every sweep report one distinct stack per call - 99 of them on a 99-call day
# - under a heading that reads like a provider changing mid-run. It stays on
# the row and in the per-run archive, where it traces one archived answer back
# to one request, which is the only thing it is good for.
#
# `model` is the echo of the string sent; see `_serving_stack` above. A key
# that cannot vary independently of the request is not provenance. Leaving it
# in the identity is worse than useless: it would make two genuinely different
# stacks look identical whenever the caller sent the same alias, which is
# always.
CALL_SCOPED_STACK_KEYS = ("id", "model")


def serving_stack_identity(stack: dict | None) -> dict:
    """The part of a recorded serving stack that could identify a STACK.

    Applied when counting distinct stacks, so the count answers "did the thing
    serving this sweep change" rather than "how many calls were made".

    Applied at READ time and not at record time, deliberately: the 396 runs
    already archived by Block E are then re-read under the same rule as
    anything recorded after it, and no archive has to be rewritten to be
    counted correctly.

    On this gateway the result is EMPTY, and that is decision 3a's null result
    expressed in code instead of in a sentence - nothing the gateway returns
    distinguishes provider drift from sampling variance. An empty identity is
    reported as "nothing distinguishing", never as one stack: a sweep served by
    two stacks that both return nothing would otherwise read as one.
    """
    return {key: value for key, value in (stack or {}).items()
            if key not in CALL_SCOPED_STACK_KEYS}


def _chat(
    messages: list[dict],
    *,
    model: str,
    client=None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    sleep=time.sleep,
    temperature: float = 0,
    temperature_fallback: float | None = None,
    provenance: dict | None = None,
) -> tuple[str, int, float]:
    """One chat completion, with the Part 4 retry policy.

    Returns (text, retries, temperature_actually_used).

    `provenance` is an OUT-parameter and not a fourth return value, which is a
    choice and not laziness. `assemble.py` carries a comment about what
    happened the last time this function's arity moved: ruling 22's
    temperature work updated three of its four call sites, the fourth
    unpacked two values from a three-tuple, and every live answer call raised
    ValueError for five days with nothing catching it. There are now six call
    sites and two test call sites, and Block E freezes this code for three
    days across 270 chat calls. A caller that wants the serving stack passes a
    dict; the five that do not are not touched at all.

    `temperature_fallback` is OPT-IN and defaults to None, so Part 6's
    translations and Part 7's answers keep sending temperature=0 and keep
    failing loudly if a model refuses it. Silently sampling where an archived
    measurement assumed greedy decoding would make old and new rows
    incomparable with nothing in either to say which was which — and LiteLLM's
    own suggested fix, `drop_params = True`, does exactly that, globally, to
    every call including the embeddings. Refused for that reason.

    Where a caller DOES opt in, the fallback temperature is returned so it can
    be written into the row's provenance.
    """
    client = client or _make_client()
    retries = 0
    last_error: Exception | None = None
    used = temperature

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=used,   # a translation harness must be reproducible
                max_tokens=max_tokens,
            )
            if provenance is not None:
                provenance.clear()
                provenance.update(_serving_stack(response))
            return (response.choices[0].message.content or ""), retries, used

        except Exception as exc:  # noqa: BLE001 — provider errors are untyped
            message = str(exc)
            if _is_unsupported_temperature(message):
                if temperature_fallback is None or used == temperature_fallback:
                    raise TranslationError(
                        f"model {model!r} refuses temperature={used}. This "
                        f"harness sends 0 because a translation that cannot be "
                        f"reproduced cannot be compared, and it will not drop "
                        f"the parameter silently — LiteLLM's `drop_params` "
                        f"would do that to every call in the gateway, "
                        f"embeddings included.\nEither point the alias at a "
                        f"model that supports greedy decoding, or use a caller "
                        f"that opts into a recorded temperature fallback.\n"
                        f"Provider said: {message[:300]}"
                    ) from exc
                used = temperature_fallback
                retries += 1
                continue

            if _is_rate_limit_error(message):
                retries += 1
                if attempt == MAX_RETRIES - 1:
                    raise TranslationError(
                        f"rate limited by the chat provider after {MAX_RETRIES} "
                        f"attempts. Translation costs 2 calls per chunk, so a "
                        f"large run trips limits that the embedding pass does "
                        f"not — use --limit.\nProvider said: {message[:300]}"
                    ) from exc
                sleep(RATE_LIMIT_BACKOFF_SECONDS)
                continue

            if _is_connection_error(message):
                raise TranslationError(
                    f"cannot reach the LiteLLM gateway at "
                    f"{os.environ.get('LITELLM_BASE_URL', 'http://localhost:4000')} "
                    f"({message}).\nStart it in its own window, with .env loaded "
                    f"in THAT window:\n"
                    f"    litellm --config gateway/config.yaml --port 4000"
                ) from exc

            last_error = exc
            retries += 1
            if attempt == MAX_RETRIES - 1:
                break
            sleep(BACKOFF_SECONDS * (2 ** attempt))

    raise TranslationError(f"translation failed after {MAX_RETRIES} attempts: {last_error}")


def translate_to_english(
    text: str,
    source_lang: str,
    *,
    model: str = DEFAULT_MODEL,
    client=None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    sleep=time.sleep,
) -> Translation:
    if not text or not text.strip():
        raise TranslationError("nothing to translate: the passage is empty")

    raw, retries, temperature = _chat(
        build_forward_messages(text, source_lang),
        model=model, client=client, max_tokens=max_tokens, sleep=sleep,
    )
    parsed, notes = parse_translation(raw)
    if source_lang not in LANG_NAMES:
        notes.append(
            f"language code '{source_lang}' is not in LANG_NAMES; the prompt "
            f"named it by code only, which weakens the translation"
        )
    return Translation(
        text=parsed,
        source_lang=source_lang,
        target_lang="en",
        model=model,
        prompt_version=PROMPT_VERSION,
        raw_response=raw,
        notes=notes,
        retries=retries,
        temperature=temperature,
    )


def back_translate(
    english_text: str,
    target_lang: str,
    *,
    model: str = DEFAULT_MODEL,
    client=None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    sleep=time.sleep,
) -> Translation:
    """English -> source language. Never give this function the original."""
    if not english_text or not english_text.strip():
        raise TranslationError(
            "nothing to back-translate: the forward translation was empty"
        )

    raw, retries, temperature = _chat(
        build_back_messages(english_text, target_lang),
        model=model, client=client, max_tokens=max_tokens, sleep=sleep,
    )
    parsed, notes = parse_translation(raw)
    return Translation(
        text=parsed,
        source_lang="en",
        target_lang=target_lang,
        model=model,
        prompt_version=BACK_PROMPT_VERSION,
        raw_response=raw,
        notes=notes,
        retries=retries,
        temperature=temperature,
    )


def render_query(
    query: str,
    source_lang: str,
    target_lang: str,
    *,
    model: str = DEFAULT_MODEL,
    client=None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    sleep=time.sleep,
    retry: bool = False,
) -> Translation:
    """One query, rendered into one target language. C2, Block C ruling 12.

    Deliberately takes three strings and knows nothing about a gold pair. Which
    target languages are asked for is decided by `retrieve.render.target_langs`
    from the INDEX, and this function is not a place that decision could leak
    into: it renders what it is told to render.

    `max_tokens` is left at the module default rather than lowered to something
    query-sized. A truncated rendering is a silently shortened query, which
    retrieves plausibly and wrongly; the spend saved would be a rounding error
    against the 205 calls this costs once.
    """
    if not query or not query.strip():
        raise TranslationError("nothing to render: the query is empty")
    if target_lang == source_lang:
        raise TranslationError(
            f"asked to render a {source_lang} query into {target_lang}. "
            f"retrieve.render.target_langs excludes a query's own language, so "
            f"reaching here means the language rule was bypassed — and a "
            f"self-rendering fused by max is a second copy of the "
            f"single-variant arm, which would make C2 look free."
        )

    # Ruling 22. The renderer is the ONE caller that opts into a temperature
    # fallback, because it is the one whose reproducibility does not rest on the
    # sampler: ruling 19 already freezes the renderings to disk and every run
    # reads that file and records its hash. What a re-render would produce is
    # not what makes two runs comparable — the committed file is.
    raw, retries, temperature = _chat(
        build_render_messages(query, source_lang, target_lang, retry=retry),
        model=model, client=client, max_tokens=max_tokens, sleep=sleep,
        temperature_fallback=1.0,
    )
    parsed, notes = parse_translation(raw)
    if temperature != 0:
        notes.append(
            f"sampled at temperature={temperature}: this model refuses greedy "
            f"decoding, so the rendering is one draw and not a reproducible one"
        )
    if target_lang not in LANG_NAMES:
        notes.append(
            f"language code '{target_lang}' is not in LANG_NAMES; the prompt "
            f"named it by code only, which weakens the rendering"
        )
    return Translation(
        text=parsed,
        source_lang=source_lang,
        target_lang=target_lang,
        model=model,
        prompt_version=(QUERY_RETRY_PROMPT_VERSION if retry
                        else QUERY_PROMPT_VERSION),
        raw_response=raw,
        notes=notes,
        retries=retries,
        temperature=temperature,
    )


def resolve_model_label(
    model: str = DEFAULT_MODEL,
    config_path: str = "gateway/config.yaml",
) -> str:
    """Concrete chat model behind the alias, for the provenance column.

    Same argument as Part 4's embedding label: 'chat-default' is a pointer that
    will be repointed (haiku today, sonnet tomorrow), and two models' output
    stored under one label cannot be told apart afterwards.

    Resolved here rather than by calling ingest.embed.resolve_model_label, which
    honours the EMBED_MODEL_LABEL override — that override would then relabel
    chat output with an embedding model's name.
    """
    override = os.environ.get("TRANSLATE_MODEL_LABEL")
    if override:
        return override

    from pathlib import Path

    path = Path(config_path)
    if not path.exists():
        return f"{model}(unresolved: {config_path} not found)"

    text = path.read_text(encoding="utf-8")
    try:
        import yaml

        config = yaml.safe_load(text) or {}
        for entry in config.get("model_list", []):
            if entry.get("model_name") == model:
                concrete = (entry.get("litellm_params") or {}).get("model")
                if concrete:
                    return concrete
    except ImportError:
        match = re.search(
            rf"model_name:\s*{re.escape(model)}\s*\n\s*litellm_params:\s*\n\s*model:\s*(\S+)",
            text,
        )
        if match:
            return match.group(1)

    return f"{model}(unresolved in {config_path})"
