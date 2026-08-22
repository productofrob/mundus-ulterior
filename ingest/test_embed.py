"""Embedding-layer tests. No network, no database.

The failure modes worth catching before spending API calls are: silently
dropping or reordering vectors so text and embedding get mismatched, accepting
a wrong-dimension vector the column cannot hold, and retrying forever on a
permanent error.

Run: python -m ingest.test_embed
"""

from __future__ import annotations

import re
from pathlib import Path

from eval.goldset import Probe, load_probes
from retrieve.crosslingual_check import rank_of

from .embed import (
    EXPECTED_DIM,
    EmbeddingError,
    embed_texts,
    resolve_model_label,
)

import sys

# FINDING 10: this process's own stdout. On Windows `print` writes through a
# stream whose encoding comes from the console code page, and through a PIPE or
# a REDIRECT it falls back to the locale codec — cp1252, which cannot encode
# Greek, Tamil, Chinese, Ge'ez or runic. It does not degrade: it raises
# UnicodeEncodeError mid-output, with the file half written and every number in
# it correct. Found 2026-08-22 at build_ui_data.py:730, printing the Greek behind
# a `case_only` span into a redirect.
#
# Two neighbouring boundaries were already guarded and are NOT this one: a CHILD
# process's stdout (PYTHONIOENCODING in its env) and a PARENT decoding that child
# (subprocess encoding=). Both are about a pipe between two processes. This is
# about where THIS process is writing, and until 2026-08-22 nothing guarded it.
#
# errors="replace" is deliberate. A harness that cannot encode one character
# should print a replacement character and finish; it should never lose a run to
# a formatting problem. A mangled character is cosmetic. A three-day sweep that
# dies on day one is ninety chat calls.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

# These three were imported from `retrieve.crosslingual_check` inside main(),
# where `PROBES` had lived until Part 6 moved the probes into
# `eval/gold/retrieval_probes.json`. The name went away; the import did not.
#
# Because it sat two-thirds of the way down main(), the ImportError did not
# announce a broken dependency — it TRUNCATED the suite. Everything below it
# stopped running on 2026-08-10 and nobody saw a failure, including both guards
# this file is credited with in README.md: the doc-id-proxy probe bug and the
# missing ::text[] cast.
#
# Imports belong at module scope for exactly this reason. A missing dependency
# should fail at load, loudly, not silently shorten the test run.
# Found 2026-08-12, Block 0.

failures: list[str] = []


def expect(condition: bool, label: str) -> None:
    if condition:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


class FakeItem:
    def __init__(self, index: int, embedding: list[float]):
        self.index = index
        self.embedding = embedding


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeClient:
    """Records calls and returns deterministic vectors."""

    def __init__(self, dim=EXPECTED_DIM, fail_times=0, error=None,
                 shuffle=False, drop_one=False, reject_input_type=False):
        self.dim = dim
        self.fail_times = fail_times
        self.error = error or RuntimeError("transient upstream error")
        self.shuffle = shuffle
        self.drop_one = drop_one
        self.reject_input_type = reject_input_type
        self.calls: list[dict] = []
        self.embeddings = self

    def create(self, **kwargs):
        self.calls.append(kwargs)

        if self.reject_input_type and "extra_body" in kwargs:
            raise RuntimeError("Unrecognized request argument supplied: input_type")

        if self.fail_times > 0:
            self.fail_times -= 1
            raise self.error

        batch = kwargs["input"]
        # Vector encodes its text so mismatches are detectable.
        items = [
            FakeItem(i, [float(len(t))] + [0.0] * (self.dim - 1))
            for i, t in enumerate(batch)
        ]
        if self.drop_one:
            items = items[:-1]
        if self.shuffle:
            items = list(reversed(items))
        return FakeResponse(items)


def main() -> int:
    no_sleep = lambda _s: None  # noqa: E731

    print("batching splits inputs and preserves order")
    texts = [f"text-{'x' * i}" for i in range(1, 71)]  # 70 distinct lengths
    client = FakeClient()
    result = embed_texts(texts, batch_size=32, client=client, sleep=no_sleep)
    expect(len(result.vectors) == 70, "one vector per input")
    expect(result.batches == 3, f"70 inputs / batch 32 = 3 batches (got {result.batches})")
    expect(
        all(v[0] == float(len(t)) for v, t in zip(result.vectors, texts)),
        "each vector lines up with its own text",
    )

    print("\nout-of-order provider responses are re-sorted by index")
    client = FakeClient(shuffle=True)
    result = embed_texts(texts[:5], batch_size=32, client=client, sleep=no_sleep)
    expect(
        [v[0] for v in result.vectors] == [float(len(t)) for t in texts[:5]],
        "reversed response is restored to input order",
    )

    print("\na short response is an error, not a silent misalignment")
    client = FakeClient(drop_one=True)
    try:
        embed_texts(texts[:5], batch_size=32, client=client, sleep=no_sleep)
        expect(False, "raises when the provider returns fewer vectors than inputs")
    except EmbeddingError as exc:
        expect("4 vectors for 5 inputs" in str(exc), f"clear error message: {exc}")

    print("\nwrong dimensions are rejected before they reach the database")
    client = FakeClient(dim=512)
    try:
        embed_texts(["a"], client=client, sleep=no_sleep)
        expect(False, "raises on dimension mismatch")
    except EmbeddingError as exc:
        expect("512" in str(exc) and "1024" in str(exc), f"names both dims: {exc}")

    print("\ntransient failures retry, then succeed")
    client = FakeClient(fail_times=2)
    result = embed_texts(["a", "b"], client=client, sleep=no_sleep)
    expect(len(result.vectors) == 2, "recovers after 2 transient failures")
    expect(result.retries == 2, f"counts retries (got {result.retries})")

    print("\npermanent failures give up instead of looping")
    client = FakeClient(fail_times=99)
    try:
        embed_texts(["a"], client=client, sleep=no_sleep)
        expect(False, "raises after max retries")
    except EmbeddingError as exc:
        expect("after 4 attempts" in str(exc), f"bounded retries: {exc}")

    print("\ninput_type is sent, and falls back loudly if rejected")
    client = FakeClient()
    result = embed_texts(["a"], client=client, sleep=no_sleep)
    expect(
        client.calls[0].get("extra_body") == {"input_type": "document"},
        "input_type='document' is passed through the gateway",
    )
    client = FakeClient(reject_input_type=True)
    result = embed_texts(["a"], client=client, sleep=no_sleep)
    expect(len(result.vectors) == 1, "still returns vectors when input_type is rejected")
    expect(result.input_type_used is None, "records that input_type was dropped")
    expect(
        any("falling back" in n for n in result.notes),
        "warns rather than silently degrading",
    )

    print("\nempty input is a no-op, not an API call")
    client = FakeClient()
    result = embed_texts([], client=client, sleep=no_sleep)
    expect(result.vectors == [] and not client.calls, "no request made for zero texts")

    print("\nmodel label resolves the gateway alias to a concrete model")
    label = resolve_model_label(config_path="gateway/config.yaml")
    expect(
        "voyage" in label.lower(),
        f"embed-default resolves to the configured model (got {label!r})",
    )
    expect(
        label != "embed-default",
        "does not record the alias, which would be ambiguous after a BGE-M3 swap",
    )

    print("\nSQL and schema agree")
    from . import run_embed

    schema = Path("scripts/schema-part4.sql").read_text(encoding="utf-8")
    for col in ("embedding_model", "embedding_dim", "embedded_at"):
        expect(col in schema, f"schema adds {col}")
        expect(col in run_embed.UPDATE_EMBEDDING, f"update writes {col}")
    expect(
        "vector_cosine_ops" in schema,
        "HNSW index uses cosine ops",
    )
    from retrieve import search as search_mod

    expect(
        "<=>" in search_mod.SEARCH_SQL,
        "search uses the cosine operator that matches the index",
    )
    expect(
        "retrievable_chunks" in search_mod.SEARCH_SQL
        and "CREATE OR REPLACE VIEW retrievable_chunks" in schema,
        "search reads the view, so held-back chunks are unreachable",
    )
    expect(
        "eligible_for_retrieval" in run_embed.SELECT_PENDING,
        "backfill never embeds a chunk the classifier held back",
    )

    placeholders = set(re.findall(r"%\((\w+)\)s", run_embed.UPDATE_EMBEDDING))
    expect(
        placeholders == {"embedding", "model", "dim", "chunk_id"},
        f"update placeholders are exactly what the writer supplies ({placeholders})",
    )

    print("\nrequest timeout and retry policy are pinned")
    from . import embed as embed_mod

    expect(
        embed_mod.REQUEST_TIMEOUT_SECONDS <= 120,
        f"per-request timeout is bounded ({embed_mod.REQUEST_TIMEOUT_SECONDS}s), "
        "not the SDK's 600s default",
    )
    source = Path(embed_mod.__file__).read_text(encoding="utf-8")
    expect(
        "max_retries=0" in source,
        "SDK retries disabled so this module's retry loop isn't multiplied",
    )

    print("\nprogress is reported per batch")
    seen: list[tuple] = []
    client = FakeClient()
    embed_texts(
        [f"t{i}" for i in range(70)],
        batch_size=32,
        client=client,
        sleep=no_sleep,
        progress=lambda i, total, n, s: seen.append((i, total, n)),
    )
    expect(
        [s[:2] for s in seen] == [(1, 3), (2, 3), (3, 3)],
        f"callback fires once per batch with a total ({seen})",
    )
    expect(sum(s[2] for s in seen) == 70, "reported counts sum to the input size")

    print("\nembedding fields are cleared as a group by the Part 3 upsert")
    # Regression guard. Part 4 added a CHECK requiring embedding and
    # embedding_model to be null-or-present together. Part 3's upsert cleared
    # only `embedding` when a chunk's text changed, leaving the model label set
    # — so re-ingesting an edited record aborted the entire load with a
    # CheckViolation. Every column named in the constraint must be cleared by
    # the same condition.
    from . import db as db_mod

    upsert = db_mod.UPSERT_CHUNK
    schema3 = Path("scripts/schema-part3.sql").read_text(encoding="utf-8")
    constrained = set(
        re.findall(r"(embedding\w*)\s+IS\s+(?:NOT\s+)?NULL", schema3)
    ) | {"embedding"}
    guard = "WHEN chunks.text IS DISTINCT FROM EXCLUDED.text THEN NULL"
    for col in sorted(constrained):
        cleared = re.search(
            rf"{col}\s*=\s*CASE\s*\n?\s*{re.escape(guard)}", upsert
        )
        expect(bool(cleared), f"upsert clears {col} when the chunk text changes")
    expect(
        upsert.count(guard) >= len(constrained),
        f"all {len(constrained)} constrained columns share one clearing condition",
    )
    expect(
        "embedded_at" in upsert and "embedding_dim" in upsert,
        "stale embedded_at / embedding_dim are cleared too",
    )

    print("\nprobe assertions can be passage-level, not just document-level")
    PROBES = load_probes()

    class _H:
        def __init__(self, doc_id, text):
            self.doc_id, self.text = doc_id, text

    p = Probe("t", "q", "en", "doc-a", "cross_lingual", expect_text_contains="πέπερι")
    wrong_passage = [_H("doc-a", "53. Μετὰ δὲ Καλλίεναν")]
    right_passage = [_H("doc-a", "56. ... τοῦ πεπέρεως ... πέπερι ...")]
    expect(
        rank_of(wrong_passage, p) is None,
        "right document but wrong passage does not count as a hit",
    )
    expect(rank_of(right_passage, p) == 1, "the passage carrying the term does")
    expect(
        any(pr.expect_text_contains for pr in PROBES),
        "at least one probe asserts on passage content",
    )

    print("\noptional filter parameters are explicitly cast")
    # Regression guard. `%(langs)s IS NULL OR lang = ANY(%(langs)s)` parses fine
    # and fails at execution with AmbiguousParameter, because Postgres cannot
    # infer a type for a NULL parameter from that context. sqlglot will never
    # catch it; only an explicit cast or a live database will.
    sql = search_mod.SEARCH_SQL
    uncast = []
    for name in set(re.findall(r"%\((\w+)\)s", sql)):
        occurrences = re.findall(rf"%\({name}\)s(::\w+(?:\[\])?)?", sql)
        used_in_is_null = re.search(rf"%\({name}\)s(::\w+(?:\[\])?)?\s+IS NULL", sql)
        if used_in_is_null and any(cast is None or cast == "" for cast in occurrences):
            uncast.append(name)
    expect(
        not uncast,
        f"every nullable filter param is cast at every use ({uncast or 'all cast'})",
    )
    expect(
        sql.count("%(query)s::vector") == 2,
        "the query vector is cast in both the SELECT and the ORDER BY",
    )

    print("\nSQL parses under the postgres dialect")
    try:
        import sqlglot
    except ImportError:
        # Dev-only dependency. Not having it should not fail the suite the way
        # it did on first run — the assertions above are the ones that matter.
        print("  skip sqlglot not installed (pip install sqlglot to enable)")
    else:
        ok = True
        for stmt in (run_embed.UPDATE_EMBEDDING, search_mod.SEARCH_SQL, run_embed.EMBED_STATS):
            try:
                sqlglot.parse(stmt, read="postgres")
            except Exception as exc:  # noqa: BLE001
                ok = False
                print(f"    parse error: {exc}")
        expect(ok, "queries parse")

    if failures:
        print(f"\nFAILED ({len(failures)})")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("\nAll embedding tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
