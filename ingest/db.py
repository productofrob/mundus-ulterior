"""Postgres persistence for documents and chunks.

Idempotent by design: re-running ingestion upserts on primary key, so the
pipeline can be run repeatedly while the corpus is still being corrected.
Embeddings already computed in Part 4 are preserved unless the chunk text
itself changed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

from .loader import Chunk, Document

DEFAULT_DSN = "postgresql://mundus:mundus@localhost:5432/mundus"
SCHEMA_PATH = Path("scripts/schema-part3.sql")


def get_dsn() -> str:
    # APP_DATABASE_URL, not DATABASE_URL — LiteLLM reserves the latter for Prisma.
    return os.environ.get("APP_DATABASE_URL", DEFAULT_DSN)


# Every migration that touches a view, in the order it must be applied. LATER
# ENTRIES MUST FOLLOW EARLIER ONES, because a `CREATE OR REPLACE VIEW` in an
# early file silently undoes a redefinition in a later one.
#
# That is not hypothetical. `schema-part4.sql` defines `retrievable_chunks`
# WITHOUT Block B4's `AND NOT is_distractor`, and both `run_ingest` and
# `run_embed` re-applied part4 on every invocation. So two commands in the
# standing session ritual silently reverted distractor containment — and on
# 2026-08-14 `run_embed` did exactly that, between a containment suite that
# passed 15/15 and one that failed three assertions.
#
# Nothing detected it. `load_distractors` printed "corpus chunks unchanged:
# 151 -> 151  OK" while reading the reverted view, so the check that existed to
# catch containment failure was itself reading contaminated data.
MIGRATIONS = (
    "scripts/schema-part3.sql",
    "scripts/schema-part4.sql",
    "scripts/schema-b4-distractors.sql",
)


def apply_schema(conn: psycopg.Connection, schema_path: Path = SCHEMA_PATH) -> None:
    """Apply every migration, in order, skipping any that is absent.

    `schema_path` is honoured for the Part 3 file so existing callers and tests
    keep working; everything after it comes from MIGRATIONS.
    """
    conn.execute(schema_path.read_text(encoding="utf-8"))
    for name in MIGRATIONS[1:]:
        path = Path(name)
        if path.exists():
            conn.execute(path.read_text(encoding="utf-8"))


def check_connection(dsn: str | None = None) -> str | None:
    """Return None if Postgres is reachable, else a human-readable reason.

    Called before the ingest report prints, so a stopped container fails in one
    line instead of after forty lines of output that look like success.
    """
    try:
        with psycopg.connect(dsn or get_dsn(), connect_timeout=5) as conn:
            conn.execute("SELECT 1;")
        return None
    except Exception as exc:  # noqa: BLE001
        return (
            f"cannot reach Postgres at {dsn or get_dsn()}\n"
            f"  {exc}\n"
            f"Is the container up?  docker compose up -d db\n"
            f"Then confirm with:    python scripts/check_db.py"
        )


UPSERT_DOC = """
INSERT INTO documents (
    doc_id, region, title, source_type, language_codes, language_note,
    date_text, findspot, citation, citation_original, extra_citations,
    translation_source, notes, source_path, content_hash
) VALUES (
    %(doc_id)s, %(region)s, %(title)s, %(source_type)s, %(language_codes)s,
    %(language_note)s, %(date_text)s, %(findspot)s, %(citation)s,
    %(citation_original)s, %(extra_citations)s, %(translation_source)s,
    %(notes)s, %(source_path)s, %(content_hash)s
)
ON CONFLICT (doc_id) DO UPDATE SET
    region = EXCLUDED.region,
    title = EXCLUDED.title,
    source_type = EXCLUDED.source_type,
    language_codes = EXCLUDED.language_codes,
    language_note = EXCLUDED.language_note,
    date_text = EXCLUDED.date_text,
    findspot = EXCLUDED.findspot,
    citation = EXCLUDED.citation,
    citation_original = EXCLUDED.citation_original,
    extra_citations = EXCLUDED.extra_citations,
    translation_source = EXCLUDED.translation_source,
    notes = EXCLUDED.notes,
    source_path = EXCLUDED.source_path,
    content_hash = EXCLUDED.content_hash,
    ingested_at = now();
"""

# Note the embedding clause: an existing vector survives a re-ingest unless the
# chunk's text actually changed, so Part 4 work isn't thrown away by a re-run.
UPSERT_CHUNK = """
INSERT INTO chunks (
    chunk_id, doc_id, parallel_group, role, seq, lang, declared_lang, text,
    char_start, char_end, source_field, text_fidelity, is_pointer,
    eligible_for_retrieval, region, source_type, citation, date_text,
    char_count, token_estimate
) VALUES (
    %(chunk_id)s, %(doc_id)s, %(parallel_group)s, %(role)s, %(seq)s, %(lang)s,
    %(declared_lang)s, %(text)s, %(char_start)s, %(char_end)s, %(source_field)s,
    %(text_fidelity)s, %(is_pointer)s, %(eligible_for_retrieval)s, %(region)s,
    %(source_type)s, %(citation)s, %(date_text)s, %(char_count)s,
    %(token_estimate)s
)
ON CONFLICT (chunk_id) DO UPDATE SET
    parallel_group = EXCLUDED.parallel_group,
    role = EXCLUDED.role,
    seq = EXCLUDED.seq,
    lang = EXCLUDED.lang,
    declared_lang = EXCLUDED.declared_lang,
    text = EXCLUDED.text,
    char_start = EXCLUDED.char_start,
    char_end = EXCLUDED.char_end,
    source_field = EXCLUDED.source_field,
    text_fidelity = EXCLUDED.text_fidelity,
    is_pointer = EXCLUDED.is_pointer,
    eligible_for_retrieval = EXCLUDED.eligible_for_retrieval,
    region = EXCLUDED.region,
    source_type = EXCLUDED.source_type,
    citation = EXCLUDED.citation,
    date_text = EXCLUDED.date_text,
    char_count = EXCLUDED.char_count,
    token_estimate = EXCLUDED.token_estimate,
    -- All four embedding fields move together. Clearing `embedding` alone left
    -- `embedding_model` populated, which violates the chunks_embedding_provenance
    -- CHECK added in Part 4 — so re-ingesting any record whose text had changed
    -- aborted the whole load. The constraint was right; this upsert predated it.
    embedding = CASE
        WHEN chunks.text IS DISTINCT FROM EXCLUDED.text THEN NULL
        ELSE chunks.embedding
    END,
    embedding_model = CASE
        WHEN chunks.text IS DISTINCT FROM EXCLUDED.text THEN NULL
        ELSE chunks.embedding_model
    END,
    embedding_dim = CASE
        WHEN chunks.text IS DISTINCT FROM EXCLUDED.text THEN NULL
        ELSE chunks.embedding_dim
    END,
    embedded_at = CASE
        WHEN chunks.text IS DISTINCT FROM EXCLUDED.text THEN NULL
        ELSE chunks.embedded_at
    END;
"""


def write(
    conn: psycopg.Connection,
    documents: list[Document],
    chunks: list[Chunk],
    prune: bool = True,
) -> dict[str, int]:
    """Upsert documents and chunks. Returns counts."""
    with conn.cursor() as cur:
        for doc in documents:
            params = doc.__dict__.copy()
            params["extra_citations"] = Jsonb(params["extra_citations"])
            cur.execute(UPSERT_DOC, params)

        for chunk in chunks:
            cur.execute(UPSERT_CHUNK, chunk.__dict__)

        pruned_chunks = pruned_docs = 0
        if prune:
            # Drop rows for records that have since been removed from disk, so
            # the table never serves a citation to a source we no longer hold.
            doc_ids = [d.doc_id for d in documents]
            chunk_ids = [c.chunk_id for c in chunks]
            cur.execute(
                "DELETE FROM chunks WHERE doc_id = ANY(%s) AND NOT (chunk_id = ANY(%s)) "
                "AND NOT is_distractor;",
                (doc_ids, chunk_ids),
            )
            pruned_chunks = cur.rowcount
            # `AND NOT is_distractor` is load-bearing, not defensive. Distractor
            # documents are by definition absent from the seed corpus, and
            # chunks.doc_id REFERENCES documents(doc_id) ON DELETE CASCADE — so
            # without this clause one routine `python -m ingest.run_ingest`
            # would cascade-delete the entire W2b distractor corpus and the
            # batched embedding requests that produced it. Silently, from the
            # command that opens every session.
            cur.execute(
                "DELETE FROM documents WHERE NOT (doc_id = ANY(%s)) "
                "AND NOT is_distractor;",
                (doc_ids,),
            )
            pruned_docs = cur.rowcount

    conn.commit()
    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "pruned_chunks": pruned_chunks,
        "pruned_documents": pruned_docs,
    }


def summary(conn: psycopg.Connection) -> dict:
    """Post-load counts, for the milestone check."""
    out: dict = {}
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM documents;")
        out["documents"] = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM chunks;")
        out["chunks"] = cur.fetchone()[0]
        cur.execute(
            "SELECT region, count(*) FROM chunks GROUP BY region ORDER BY region;"
        )
        out["by_region"] = dict(cur.fetchall())
        cur.execute(
            "SELECT text_fidelity, count(*) FROM chunks "
            "GROUP BY text_fidelity ORDER BY count(*) DESC;"
        )
        out["by_fidelity"] = dict(cur.fetchall())
        cur.execute(
            "SELECT lang, count(*) FROM chunks GROUP BY lang ORDER BY count(*) DESC;"
        )
        out["by_lang"] = dict(cur.fetchall())
        cur.execute(
            "SELECT count(*) FROM chunks WHERE eligible_for_retrieval AND embedding IS NULL;"
        )
        out["awaiting_embedding"] = cur.fetchone()[0]
    return out
