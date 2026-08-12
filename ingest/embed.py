"""Embedding client, routed through the LiteLLM gateway.

Everything goes through the gateway on :4000, so switching voyage-3.5 → BGE-M3
later is a change to gateway/config.yaml plus a re-embed, not a code change here.

Two things this deliberately does NOT do:
  * silently accept a wrong-dimension vector — the column is vector(1024) and a
    mismatch means the gateway is pointed at a different model than we think;
  * embed queries and documents identically. Voyage distinguishes input_type
    "document" from "query", and using the right one measurably improves
    retrieval. If the gateway rejects the parameter we fall back and say so,
    rather than quietly degrading.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field

EXPECTED_DIM = 1024
DEFAULT_MODEL = "embed-default"          # gateway alias, see gateway/config.yaml
DEFAULT_BASE_URL = "http://localhost:4000"

# voyage-3.5 accepts larger batches, but the gateway sits in the middle and
# 32 keeps any single failure cheap to retry.
DEFAULT_BATCH_SIZE = 32
MAX_RETRIES = 4
BACKOFF_SECONDS = 2.0

# The OpenAI SDK defaults to a 600-second timeout and its own 2 internal
# retries. Combined with the retry loop below that is 4 x 3 = 12 attempts at up
# to ten minutes each — a run that looks like a hang with no output for the best
# part of an hour. Both are pinned here so this module's retry policy is the
# only one in play and a stalled gateway fails fast.
REQUEST_TIMEOUT_SECONDS = 60.0

# Voyage's free tier is 3 requests/minute. On a rate-limit response, waiting a
# little over a full window is the only backoff that helps — doubling from 2s
# just spends every remaining attempt inside the same throttled minute.
RATE_LIMIT_BACKOFF_SECONDS = 21.0


class EmbeddingError(RuntimeError):
    pass


@dataclass
class EmbeddingResult:
    vectors: list[list[float]]
    model: str
    dim: int
    input_type_used: str | None
    batches: int = 0
    retries: int = 0
    notes: list[str] = field(default_factory=list)


def _make_client(base_url: str | None = None):
    from openai import OpenAI  # LiteLLM proxy is OpenAI-compatible

    return OpenAI(
        base_url=base_url or os.environ.get("LITELLM_BASE_URL", DEFAULT_BASE_URL),
        api_key=os.environ.get("LITELLM_MASTER_KEY", "sk-local-dev"),
        timeout=float(os.environ.get("EMBED_TIMEOUT", REQUEST_TIMEOUT_SECONDS)),
        max_retries=0,   # this module retries; don't let the SDK multiply it
    )


def _chunked(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def embed_texts(
    texts: list[str],
    *,
    input_type: str = "document",
    model: str = DEFAULT_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    client=None,
    expected_dim: int = EXPECTED_DIM,
    sleep=time.sleep,
    progress=None,
) -> EmbeddingResult:
    """Embed `texts` in order. Returns one vector per input text.

    `client` is injectable so the tests can exercise batching, retry and
    dimension validation without touching the network. `progress` is called as
    progress(batch_index, total_batches, batch_len, elapsed_seconds) after each
    batch, so a long run reports rather than sitting silent.
    """
    if not texts:
        return EmbeddingResult([], model, expected_dim, None)

    client = client or _make_client()
    vectors: list[list[float]] = []
    result = EmbeddingResult([], model, expected_dim, input_type)
    total_batches = (len(texts) + batch_size - 1) // batch_size

    for batch in _chunked(texts, batch_size):
        result.batches += 1
        started = time.monotonic()
        batch_vectors = _embed_one_batch(
            client, batch, model, input_type, result, sleep
        )

        if len(batch_vectors) != len(batch):
            raise EmbeddingError(
                f"gateway returned {len(batch_vectors)} vectors for {len(batch)} inputs"
            )
        for vec in batch_vectors:
            if len(vec) != expected_dim:
                raise EmbeddingError(
                    f"expected {expected_dim}-dim vectors, got {len(vec)}. "
                    f"The gateway's '{model}' alias is probably pointed at a "
                    f"different model than the schema was built for."
                )
        vectors.extend(batch_vectors)
        if progress:
            progress(result.batches, total_batches, len(batch), time.monotonic() - started)

    result.vectors = vectors
    return result


def _embed_one_batch(client, batch, model, input_type, result, sleep) -> list[list[float]]:
    """One batch, with retry, and graceful fallback if input_type is rejected."""
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            kwargs: dict = {"model": model, "input": batch}
            if result.input_type_used:
                # LiteLLM forwards unknown kwargs to the provider.
                kwargs["extra_body"] = {"input_type": result.input_type_used}
            response = client.embeddings.create(**kwargs)
            # Providers may return items out of order; index is authoritative.
            items = sorted(response.data, key=lambda d: getattr(d, "index", 0))
            return [item.embedding for item in items]

        except Exception as exc:  # noqa: BLE001 - provider errors are untyped
            message = str(exc)
            if result.input_type_used and _is_bad_parameter(message):
                # Drop input_type once, note it loudly, and retry without it.
                result.notes.append(
                    f"gateway rejected input_type='{result.input_type_used}' "
                    f"({message[:120]}); falling back to untyped embeddings. "
                    f"Retrieval quality will be slightly worse than it could be."
                )
                result.input_type_used = None
                continue

            if _is_rate_limit_error(message):
                # Free-tier Voyage allows 3 requests/minute. Backing off for a
                # full window is the only thing that helps; exponential-from-2s
                # just burns attempts inside the same minute.
                result.retries += 1
                if attempt == MAX_RETRIES - 1:
                    raise EmbeddingError(
                        f"rate limited by the embedding provider after "
                        f"{MAX_RETRIES} attempts.\n"
                        f"The Voyage free tier allows 3 requests/minute and 10K "
                        f"tokens/minute. Reduce request count (batch more per "
                        f"call), wait, or add a payment method at "
                        f"https://dashboard.voyageai.com/.\n"
                        f"Provider said: {message[:300]}"
                    ) from exc
                wait = RATE_LIMIT_BACKOFF_SECONDS
                result.notes.append(
                    f"rate limited; waiting {wait:.0f}s before retry "
                    f"{attempt + 2}/{MAX_RETRIES}"
                )
                sleep(wait)
                continue

            if _is_connection_error(message):
                # Not transient in any useful sense: nothing is listening. Four
                # attempts with backoff just delays the same answer.
                raise EmbeddingError(
                    f"cannot reach the LiteLLM gateway at "
                    f"{os.environ.get('LITELLM_BASE_URL', DEFAULT_BASE_URL)} ({message}).\n"
                    f"Start it in its own window, with .env loaded in THAT window:\n"
                    f"    litellm --config gateway/config.yaml --port 4000\n"
                    f"Then confirm with:  python scripts/hello.py"
                ) from exc

            last_error = exc
            result.retries += 1
            if attempt == MAX_RETRIES - 1:
                break
            sleep(BACKOFF_SECONDS * (2 ** attempt))

    raise EmbeddingError(f"embedding failed after {MAX_RETRIES} attempts: {last_error}")


def _is_rate_limit_error(message: str) -> bool:
    """Upstream throttling — worth waiting out, unlike a dead socket.

    The Voyage free tier is 3 requests/minute and 10K tokens/minute, so this is
    the single most likely failure on a fresh key.
    """
    lowered = message.lower()
    return any(
        s in lowered
        for s in ("rate limit", "ratelimit", "rate_limit", "429",
                  "too many requests", " rpm", " tpm", "quota")
    )


def _is_connection_error(message: str) -> bool:
    """A genuinely dead endpoint — nothing is listening, so don't retry.

    Deliberately narrow. LiteLLM wraps *upstream provider* errors as
    `litellm.APIConnectionError` too, so matching that class name would report
    "cannot reach the gateway" for a Voyage rate-limit response — sending you to
    debug a healthy gateway. Rate limits are checked first, and the substrings
    below describe socket-level failure only.
    """
    lowered = message.lower()
    if _is_rate_limit_error(lowered):
        return False
    return any(
        s in lowered
        for s in ("connection refused", "failed to establish", "actively refused",
                  "name or service not known", "max retries exceeded",
                  "connection error.")
    )


def _is_bad_parameter(message: str) -> bool:
    lowered = message.lower()
    return "input_type" in lowered or "unexpected keyword" in lowered or (
        "unrecognized" in lowered and "parameter" in lowered
    )


def embed_query(text: str, **kwargs) -> list[float]:
    """Embed a single search query (input_type='query')."""
    result = embed_texts([text], input_type="query", **kwargs)
    return result.vectors[0]


def resolve_model_label(
    model: str = DEFAULT_MODEL,
    config_path: str = "gateway/config.yaml",
) -> str:
    """What to record in chunks.embedding_model.

    The gateway alias ('embed-default') is not a model identity — it is a
    pointer that gets repointed at BGE-M3 later. Storing the alias would make
    voyage vectors and BGE-M3 vectors indistinguishable in the table, which is
    exactly the confusion the provenance columns exist to prevent. So resolve
    the alias to the concrete model by reading the gateway config.
    """
    override = os.environ.get("EMBED_MODEL_LABEL")
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
        # pyyaml ships with litellm, but don't hard-fail the backfill over it.
        import re

        match = re.search(
            rf"model_name:\s*{re.escape(model)}\s*\n\s*litellm_params:\s*\n\s*model:\s*(\S+)",
            text,
        )
        if match:
            return match.group(1)

    return f"{model}(unresolved in {config_path})"
