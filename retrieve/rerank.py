"""Cross-encoder reranking, routed through the LiteLLM gateway (Block C3).

A bi-encoder compares two independently produced vectors; a cross-encoder reads
query and passage together. That is the whole mechanism C3 is betting on, and it
is why C3 can move a rank that `voyage-3.5` alone could not.

What this module is NOT allowed to do, each for a reason already written down:

1. **It cannot move the gap.** Ruling 3 fixes G2's gap criterion to PRE-rerank
   embedding similarities, because that is the quantity B2's baseline recorded
   and the quantity the whole W2b distractor curve is denominated in. Reranking
   reorders candidates; it does not alter cosine similarities. A reranker-score
   gap may be recorded under its own name — `rerank_gap_*` — and is never
   compared to the baseline number. C3 is a recall intervention only.
2. **It cannot widen the candidate pool.** Five gold pairs restrict candidates
   to non-English before ranking, and that filter is the only thing making them
   cross-lingual tests rather than same-language tests wearing the label.
   Reranking a raw top-50 would quietly restore English translations to pools
   built to exclude them. `pool_problems()` asserts the submitted set still
   satisfies the pair's own filters, because this repository has already paid a
   day for a stage that read a different surface than the one it named.
3. **It cannot overwrite `rank`.** Nothing here writes anything; the caller
   records the post-rerank position beside `rank` and `rank_accepted`, following
   ruling 2's precedent. Rewriting `rank` would restate every number Block B
   recorded as though the intervention had always been in force.

The network call and the reordering are separate on purpose. `reorder()`,
`parse_rerank_payload()` and `pool_problems()` are pure, so the invariants that
decide whether a G2 number means anything are testable and mutatable without a
gateway, a key, or a database.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field

# Gateway alias, see gateway/config.yaml. The alias — not `voyage/rerank-2.5` —
# so swapping the reranker stays a config change, as with embed-default.
DEFAULT_MODEL = "rerank-2.5"
DEFAULT_BASE_URL = "http://localhost:4000"

# How many pre-rerank candidates are handed to the cross-encoder. 50 is chosen
# because the three misses C3 must fix sit at 35, 17 and 15, so all three are
# inside it — and because it is a PARAMETER: it is recorded in the archived run,
# and a different window is a different measurement, not a better one.
DEFAULT_WINDOW = 50

# LiteLLM's proxy has exposed the rerank route at both of these. Which one
# answers is discovered once by scripts/probe_rerank.py and recorded in the run,
# rather than asserted from documentation that does not quote its own response.
RERANK_PATHS = ("/v1/rerank", "/rerank")

MAX_RETRIES = 4
BACKOFF_SECONDS = 2.0
REQUEST_TIMEOUT_SECONDS = 60.0

# Voyage's published table gives rerank-2.5 2000 RPM / 2M TPM. That table is
# what an account WITH A PAYMENT METHOD gets. Measured on this project's account
# on 2026-08-16, before one was added, the provider answered:
#
#   "You have not yet added your payment method ... and will have reduced rate
#    limits of 3 RPM and 10K TPM"
#
# A payment method WAS added later on 2026-08-16, which should move the account
# to the published table. **That is a claim from a document, and this file has
# already been wrong three times today taking those at face value** — it is
# recorded as unverified until a run without pacing completes. `--rerank-tpm`
# stays regardless: it paces on what each call actually cost, so it is correct
# under any ceiling and costs nothing under a generous one.
#
# — the same throttle that governs embeddings, and the reason `embed_texts`
# batches every query into one request. Reranking CANNOT batch queries: one
# query is one call, so the only lever is spacing. Hence `min_interval`, and
# hence this module no longer asserts a rate limit it read in a table.
#
# The arithmetic, and the second mistake of the same kind, recorded because it
# is the one this repository keeps paying for. The first estimate said "mean
# chunk ~375 characters ~= 94 tokens, so a 50-document window is ~4.7K tokens,
# and ~30s between calls satisfies 10K TPM". It was measured off the seed-corpus
# JSON ON DISK — not off the 450 chunks in the index, 393 of which are museum
# catalogue prose this project never wrote. Paced at 30s the provider still
# refused, which means a single 50-document window does not fit inside 10K TPM
# at all, and no spacing can make it fit.
#
# THE WINDOW'S REAL TOKEN COST HAS NOT BEEN MEASURED AGAINST THE INDEX. Until it
# is, nothing here may state one. What is known is only what the provider said.
RATE_LIMIT_BACKOFF_SECONDS = 21.0

# Seconds to leave between rerank calls. 0 means "the account is not throttled";
# a run sets it explicitly and the value is archived, because a paced run and an
# unpaced one are the same measurement and it should be possible to prove that.
DEFAULT_MIN_INTERVAL_SECONDS = 0.0

# A tokens-per-minute ceiling to pace against, or 0 for none. This exists so the
# spacing stops being a guess: every response carries the tokens it cost, so the
# NEXT call can be spaced by what the LAST one actually consumed rather than by
# an estimate of what a window is worth. The estimate has now been wrong twice
# — once from a docs table, once from the seed corpus on disk — and a number the
# provider hands back is not an estimate.
DEFAULT_TPM_BUDGET = 0.0


class RerankError(RuntimeError):
    pass


@dataclass
class RerankResponse:
    """`scored` is (index into the submitted documents, relevance score), best first."""
    scored: list[tuple[int, float]]
    model: str
    path: str | None = None
    total_tokens: int | None = None
    retries: int = 0
    waited: float = 0.0
    notes: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# Pure — the parts that decide whether the number means anything
# --------------------------------------------------------------------------

def parse_rerank_payload(payload: dict, n_documents: int) -> list[tuple[int, float]]:
    """Provider JSON -> [(document index, score)], best first.

    Strict about three things, because each one silently produces a plausible
    ranking that is about the wrong documents:

      * an index outside the submitted set means the response is not about this
        request;
      * a repeated index means one document was scored twice and another not at
        all, and the reorder below would drop a candidate;
      * a missing `relevance_score` scored as 0.0 would sort a whole cohort of
        candidates to the bottom while looking like a successful call.

    Ties break on the ORIGINAL index, so an unreranked pool and a pool the
    reranker scored flat come out in the same order rather than an arbitrary one.
    """
    results = payload.get("results")
    if not isinstance(results, list):
        raise RerankError(
            f"the rerank response has no 'results' list. Keys present: "
            f"{sorted(payload)}. This is the shape check that stops a provider "
            f"or gateway change from being read as a ranking."
        )
    scored: list[tuple[int, float]] = []
    seen: set[int] = set()
    for item in results:
        if not isinstance(item, dict) or "index" not in item:
            raise RerankError(f"rerank result without an 'index': {item!r}")
        if "relevance_score" not in item:
            raise RerankError(
                f"rerank result for index {item['index']} carries no "
                f"'relevance_score'; keys are {sorted(item)}"
            )
        idx = int(item["index"])
        if not 0 <= idx < n_documents:
            raise RerankError(
                f"rerank returned index {idx} for a request of {n_documents} "
                f"documents. The response is not about this request."
            )
        if idx in seen:
            raise RerankError(f"rerank returned index {idx} more than once")
        seen.add(idx)
        scored.append((idx, float(item["relevance_score"])))
    scored.sort(key=lambda pair: (-pair[1], pair[0]))
    return scored


def pool_problems(hits, langs=None, roles=None) -> list[str]:
    """Does the set about to be reranked still satisfy the pair's own filters?

    Design constraint 1 in C3_START.md, made into an assertion. `search()`
    applies `langs` and `roles` in SQL today, so this is expected to be silent —
    which is the point. The failure it forecloses is a later refactor that
    reranks a raw top-50 and quietly restores English translations to pools built
    by construction to exclude them, turning five cross-lingual tests into
    same-language tests still wearing the label. Nothing in a rank would say so.
    """
    problems: list[str] = []
    if langs:
        wrong = sorted({h.lang for h in hits if h.lang not in set(langs)})
        if wrong:
            problems.append(
                f"the candidate pool restricted to langs={sorted(langs)} contains "
                f"{wrong}; reranking it would score passages the pair excludes"
            )
    if roles:
        wrong = sorted({h.role for h in hits if h.role not in set(roles)})
        if wrong:
            problems.append(
                f"the candidate pool restricted to roles={sorted(roles)} contains "
                f"{wrong}"
            )
    return problems


def reorder(hits: list, scored: list[tuple[int, float]], window: int) -> list:
    """The reranked candidate ordering. A permutation of `hits`, never a subset.

    The first `window` candidates are reordered by the cross-encoder; everything
    below the window keeps its pre-rerank order and follows them. A target the
    window never reached therefore keeps a rank it can be recognised by —
    `muziris-cargo-akananuru` stays at 309 rather than becoming `none`, and a
    reranked run remains comparable to the run that produced 309.

    Coverage is required, not tolerated: `scored` must name every member of the
    window exactly once. A provider that returns `top_n` fewer results than it
    was asked for would otherwise have its silence rendered as a ranking, which
    is the same defect as a metric whose name is wrong.
    """
    if window < 0:
        raise RerankError(f"window must be non-negative, got {window}")
    head, tail = hits[:window], hits[window:]
    named = sorted(i for i, _ in scored)
    if named != list(range(len(head))):
        raise RerankError(
            f"the rerank response covers {len(named)} of {len(head)} candidates "
            f"in the window. A partial response reordered as though it were "
            f"complete would silently drop candidates from the ranking."
        )
    return [head[i] for i, _ in scored] + tail


def rank_of(ordering: list, chunk_ids) -> int | None:
    """1-based position of the first chunk in `chunk_ids`, or None.

    Takes a collection so ruling 2's accepted alternates and ruling 1's
    per-unit best are computed the same way here as they are pre-rerank.
    """
    wanted = set(chunk_ids)
    for i, hit in enumerate(ordering, start=1):
        if hit.chunk_id in wanted:
            return i
    return None


def scores_by_chunk(hits: list, scored: list[tuple[int, float]],
                    window: int) -> dict[str, float]:
    """chunk_id -> reranker score, for the window only.

    Recorded so the reranker-score gap can be reported under its own name.
    Ruling 3: this quantity is NEVER compared to the baseline gap, which is
    denominated in embedding similarities.
    """
    head = hits[:window]
    return {head[i].chunk_id: score for i, score in scored}


# --------------------------------------------------------------------------
# The network call
# --------------------------------------------------------------------------

def _post(url: str, api_key: str, body: dict, timeout: float):
    """POST JSON, returning (status_code, parsed body or raw text)."""
    try:
        import httpx
    except ModuleNotFoundError as exc:  # pragma: no cover - environment
        raise RerankError(
            f"{exc}. This call goes through the gateway over HTTP, so it needs "
            f"the host's venv:\n  .venv\\Scripts\\Activate.ps1"
        ) from exc

    response = httpx.post(
        url,
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"},
        content=json.dumps(body),
        timeout=timeout,
    )
    try:
        return response.status_code, response.json()
    except Exception:  # noqa: BLE001 - a non-JSON body is itself the diagnosis
        return response.status_code, response.text


def rerank_documents(
    query: str,
    documents: list[str],
    *,
    model: str = DEFAULT_MODEL,
    base_url: str | None = None,
    api_key: str | None = None,
    paths: tuple[str, ...] = RERANK_PATHS,
    post=_post,
    sleep=time.sleep,
    timeout: float = REQUEST_TIMEOUT_SECONDS,
    min_interval: float = DEFAULT_MIN_INTERVAL_SECONDS,
    tpm_budget: float = DEFAULT_TPM_BUDGET,
    clock=time.monotonic,
) -> RerankResponse:
    """One query against `documents`, through the gateway. `post` is injectable.

    `top_n` is set to the full document count deliberately. Asking for fewer
    would make the reorder's coverage check unsatisfiable and would hand the
    decision about how deep the window really is to a default nobody recorded.
    """
    if not documents:
        return RerankResponse(scored=[], model=model, notes=["no documents to rerank"])

    base = (base_url or os.environ.get("LITELLM_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
    key = api_key or os.environ.get("LITELLM_MASTER_KEY", "sk-local-dev")
    body = {"model": model, "query": query, "documents": documents,
            "top_n": len(documents)}

    result = RerankResponse(scored=[], model=model)
    last_error: str | None = None
    tried: list[str] = []

    # Pacing happens BEFORE the call, not as a reaction to a 429. Waiting only
    # once refused means every run spends its retry budget discovering a limit
    # it already knew about, which is what happened on the first C3 run.
    waited = pace(clock(), min_interval, _LAST_TOKENS[0], tpm_budget)
    if waited:
        sleep(waited)
        result.notes.append(f"paced {waited:.1f}s to stay inside the account's limits")
    result.waited = waited
    _LAST_CALL_AT[0] = clock()

    for path in paths:
        url = base + path
        for attempt in range(MAX_RETRIES):
            try:
                status, payload = post(url, key, body, timeout)
            except Exception as exc:  # noqa: BLE001 - transport errors are untyped
                message = str(exc)
                if _is_connection_error(message):
                    raise RerankError(
                        f"cannot reach the LiteLLM gateway at {base} ({message}).\n"
                        f"Start it in its own window, with .env loaded in THAT "
                        f"window:\n"
                        f"    litellm --config gateway/config.yaml --port 4000\n"
                        f"Then confirm with:  python scripts/probe_rerank.py"
                    ) from exc
                last_error = message
                result.retries += 1
                if attempt == MAX_RETRIES - 1:
                    break
                sleep(BACKOFF_SECONDS * (2 ** attempt))
                continue

            if status == 404:
                tried.append(path)
                last_error = f"404 at {path}"
                break                      # try the next documented route
            if status == 429:
                result.retries += 1
                if attempt == MAX_RETRIES - 1:
                    raise RerankError(
                        f"rate limited by the rerank provider after "
                        f"{MAX_RETRIES} attempts, with min_interval="
                        f"{min_interval:.0f}s.\n"
                        f"An account with no payment method is held to 3 RPM and "
                        f"10K TPM. The last call the provider costed was "
                        f"{_LAST_TOKENS[0]} tokens; at that size, "
                        f"{60.0 * (_LAST_TOKENS[0] or 6000) / 10000:.0f}s between "
                        f"calls is the floor. Re-run with `--rerank-tpm 10000`, "
                        f"which paces on what each call ACTUALLY cost.\n"
                        f"Provider said: {str(payload)[:300]}"
                    )
                result.notes.append(
                    f"rate limited; waiting {RATE_LIMIT_BACKOFF_SECONDS:.0f}s "
                    f"before retry {attempt + 2}/{MAX_RETRIES}"
                )
                sleep(RATE_LIMIT_BACKOFF_SECONDS)
                continue
            if status >= 400:
                raise RerankError(
                    f"the gateway refused the rerank request ({status}) at "
                    f"{path}: {str(payload)[:400]}\n"
                    f"If this is an authentication or model error, the alias "
                    f"'{model}' may be missing from gateway/config.yaml, or "
                    f"VOYAGE_API_KEY may not be set in the window running the "
                    f"gateway."
                )

            if not isinstance(payload, dict):
                raise RerankError(f"rerank returned a non-JSON body: {str(payload)[:300]}")
            result.scored = parse_rerank_payload(payload, len(documents))
            result.path = path
            result.total_tokens = _total_tokens(payload)
            # Feeds the NEXT call's pacing. Left alone when the provider reports
            # nothing, so an unreported call paces on the last measured one
            # rather than on zero — which would space nothing at all.
            if result.total_tokens is not None:
                _LAST_TOKENS[0] = result.total_tokens
            return result

    raise RerankError(
        f"no rerank route answered at {base}. Tried {list(paths)}; "
        f"404 at {tried or 'none'}. Last error: {last_error}. "
        f"Check that gateway/config.yaml declares model_name '{model}' and that "
        f"the gateway was restarted after it was added."
    )


# Module state, deliberately: pacing is a property of the ACCOUNT, so two
# callers in one process share one limit and must share one clock.
_LAST_CALL_AT: list[float | None] = [None]
_LAST_TOKENS: list[int | None] = [None]


def pace(now: float, min_interval: float, last_tokens: int | None = None,
         tpm_budget: float = DEFAULT_TPM_BUDGET) -> float:
    """Seconds to wait before the next call. Pure, so the arithmetic is testable.

    Two constraints, and the wait is whichever is longer:

      * `min_interval` — a floor, for requests-per-minute;
      * `tpm_budget` — tokens per minute, satisfied by spacing the next call by
        `60 * last_tokens / budget`. MEASURED, not estimated: `last_tokens` is
        what the provider said the previous call cost.

    Returns 0 for the first call of a process and whenever the wait has already
    elapsed — pacing must not add latency it does not need, or it becomes a
    reason not to measure.
    """
    if _LAST_CALL_AT[0] is None:
        return 0.0
    needed = max(0.0, min_interval)
    if tpm_budget > 0 and last_tokens:
        needed = max(needed, 60.0 * last_tokens / tpm_budget)
    return max(0.0, needed - (now - _LAST_CALL_AT[0]))


def _total_tokens(payload: dict) -> int | None:
    """Token usage if the response carries it, and None if it does not.

    Recorded, never depended on. Providers move this between `meta.billed_units`,
    `meta.tokens` and `usage`, and a spend figure inferred from a key that is not
    there is worse than no spend figure.
    """
    meta = payload.get("meta") or {}
    for holder in (meta.get("tokens"), meta.get("billed_units"), payload.get("usage")):
        if isinstance(holder, dict):
            for key in ("total_tokens", "input_tokens", "search_units"):
                if isinstance(holder.get(key), (int, float)):
                    return int(holder[key])
    return None


def _is_connection_error(message: str) -> bool:
    lowered = message.lower()
    return any(s in lowered for s in (
        "connection refused", "connection error", "failed to establish",
        "max retries exceeded", "cannot connect", "connecterror",
        "name or service not known", "actively refused",
    ))
