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
    "arc": "Aramaic",
    "gez": "Ge'ez (Classical Ethiopic)",
    "la": "Latin",
    "en": "English",
}

# Scripts that are romanised in this corpus rather than stored in their own
# characters. Back-translating into these means producing a transliteration, and
# the prompt has to say so or the model will answer in Arabic or Devanagari
# script and every character-level score will read as a total failure.
TRANSLITERATED_LANGS = {"xpr", "xna", "xsa", "gmq-pro"}

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

def _chat(
    messages: list[dict],
    *,
    model: str,
    client=None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    sleep=time.sleep,
) -> tuple[str, int]:
    """One chat completion, with the Part 4 retry policy. Returns (text, retries)."""
    client = client or _make_client()
    retries = 0
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,      # a translation harness must be reproducible
                max_tokens=max_tokens,
            )
            return (response.choices[0].message.content or ""), retries

        except Exception as exc:  # noqa: BLE001 — provider errors are untyped
            message = str(exc)
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

    raw, retries = _chat(
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

    raw, retries = _chat(
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
