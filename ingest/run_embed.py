"""Part 4 entrypoint: embed retrieval-eligible chunks and store the vectors.

Usage (repo root, venv active, .env loaded, gateway running on :4000):

    python -m ingest.run_embed --dry-run     # show what would be embedded
    python -m ingest.run_embed --limit 4     # embed a few, check, then continue
    python -m ingest.run_embed               # embed everything outstanding
    python -m ingest.run_embed --stats
    python -m ingest.run_embed --force       # re-embed everything (model swap)

Resumable: it only picks up chunks whose embedding is NULL, so an interrupted
run costs you the current batch and nothing else. Chunks held back by the
Part 3 fidelity classifier are never embedded — a placeholder that isn't in the
index cannot be cited as a source.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from . import db
from .embed import DEFAULT_BATCH_SIZE, EmbeddingError, embed_texts, resolve_model_label

SELECT_PENDING = """
SELECT chunk_id, text, lang, text_fidelity, char_count
FROM chunks
WHERE eligible_for_retrieval
  AND ({force} OR embedding IS NULL)
ORDER BY lang <> 'en' DESC, char_count DESC, chunk_id
{limit_clause};
"""

UPDATE_EMBEDDING = """
UPDATE chunks
SET embedding = %(embedding)s,
    embedding_model = %(model)s,
    embedding_dim = %(dim)s,
    embedded_at = now()
WHERE chunk_id = %(chunk_id)s;
"""

EMBED_STATS = """
SELECT
    count(*) FILTER (WHERE eligible_for_retrieval)                              AS eligible,
    count(*) FILTER (WHERE eligible_for_retrieval AND embedding IS NOT NULL)    AS embedded,
    count(*) FILTER (WHERE eligible_for_retrieval AND embedding IS NULL)        AS pending,
    count(*) FILTER (WHERE NOT eligible_for_retrieval AND embedding IS NOT NULL) AS wrongly_embedded
FROM chunks;
"""


def fetch_pending(conn, force: bool, limit: int | None):
    sql = SELECT_PENDING.format(
        force="true" if force else "false",
        limit_clause=f"LIMIT {int(limit)}" if limit else "",
    )
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def report_stats(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute(EMBED_STATS)
        eligible, embedded, pending, wrongly = cur.fetchone()
        cur.execute(
            "SELECT embedding_model, count(*) FROM chunks "
            "WHERE embedding IS NOT NULL GROUP BY embedding_model;"
        )
        by_model = dict(cur.fetchall())
        cur.execute(
            "SELECT lang, count(*) FROM chunks "
            "WHERE embedding IS NOT NULL AND lang <> 'en' GROUP BY lang ORDER BY lang;"
        )
        non_english = dict(cur.fetchall())
    return {
        "eligible": eligible,
        "embedded": embedded,
        "pending": pending,
        "embedded_but_ineligible": wrongly,
        "by_model": by_model,
        "non_english_embedded": non_english,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mundus Ulterior Part 4 embedding pass")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true", help="re-embed even if present")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="don't apply scripts/schema-part4.sql (index + provenance columns)",
    )
    args = parser.parse_args(argv)

    import psycopg

    with psycopg.connect(db.get_dsn()) as conn:
        if args.stats:
            print(json.dumps(report_stats(conn), indent=2, ensure_ascii=False))
            return 0

        if not args.skip_index:
            from pathlib import Path

            conn.execute(Path("scripts/schema-part4.sql").read_text(encoding="utf-8"))
            conn.commit()

        rows = fetch_pending(conn, args.force, args.limit)
        if not rows:
            print("nothing to embed — every eligible chunk already has a vector")
            print(json.dumps(report_stats(conn), indent=2, ensure_ascii=False))
            return 0

        non_en = sum(1 for r in rows if r[2] != "en")
        print(f"chunks to embed: {len(rows)}  ({non_en} non-English)")
        for chunk_id, _text, lang, fidelity, chars in rows[:8]:
            print(f"  {chunk_id:52} {lang:8} {fidelity:18} {chars:5} chars")
        if len(rows) > 8:
            print(f"  ... and {len(rows) - 8} more")

        if args.dry_run:
            print("\ndry run — no API calls made, nothing written")
            return 0

        model_label = resolve_model_label()
        print(f"\nembedding via gateway; recording model as: {model_label}")
        print(
            f"timeout {os.environ.get('EMBED_TIMEOUT', '60')}s per request, "
            f"batch size {args.batch_size}",
            flush=True,
        )

        def on_batch(i, total, n, seconds):
            print(f"  batch {i}/{total}: {n} chunks in {seconds:.1f}s", flush=True)

        try:
            result = embed_texts(
                [r[1] for r in rows],
                input_type="document",
                batch_size=args.batch_size,
                progress=on_batch,
            )
        except EmbeddingError as exc:
            print(f"\nembedding failed: {exc}", file=sys.stderr)
            print(
                "Check the gateway is running (litellm --config gateway/config.yaml "
                "--port 4000) and that VOYAGE_API_KEY was set in the window that "
                "started it.",
                file=sys.stderr,
            )
            return 1

        for note in result.notes:
            print(f"  note: {note}")

        with conn.cursor() as cur:
            for (chunk_id, *_rest), vector in zip(rows, result.vectors):
                cur.execute(
                    UPDATE_EMBEDDING,
                    {
                        "embedding": str(vector),   # pgvector accepts '[1,2,...]'
                        "model": model_label,
                        "dim": result.dim,
                        "chunk_id": chunk_id,
                    },
                )
        conn.commit()

        print(
            f"\nembedded {len(result.vectors)} chunks in {result.batches} batches "
            f"({result.retries} retries)"
        )
        print(json.dumps(report_stats(conn), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
