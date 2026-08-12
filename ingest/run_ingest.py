"""Part 3 entrypoint: chunk the seed corpus and load it into Postgres.

Usage (from the repo root, venv active, .env loaded):

    python -m ingest.run_ingest --dry-run          # chunk + report, touch nothing
    python -m ingest.run_ingest --dry-run --json out.json
    python -m ingest.run_ingest                    # apply schema + load Postgres
    python -m ingest.run_ingest --stats            # report what's in the DB now
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from .loader import SEED_CORPUS_DIR, load_corpus, to_jsonable


def report(result, verbose: bool = False) -> None:
    docs, chunks = result.documents, result.chunks
    print(f"documents : {len(docs)}")
    print(f"chunks    : {len(chunks)}")

    print("\nchunks by region")
    for region, n in sorted(Counter(c.region for c in chunks).items()):
        print(f"  {region:20} {n:4}")

    print("\nchunks by role")
    for role, n in sorted(Counter(c.role for c in chunks).items()):
        print(f"  {role:20} {n:4}")

    print("\nchunks by language (as detected)")
    for lang, n in Counter(c.lang for c in chunks).most_common():
        print(f"  {lang:20} {n:4}")

    print("\nchunks by text fidelity")
    for fid, n in Counter(c.text_fidelity for c in chunks).most_common():
        eligible = sum(
            1 for c in chunks if c.text_fidelity == fid and c.eligible_for_retrieval
        )
        print(f"  {fid:20} {n:4}   (retrieval-eligible: {eligible})")

    ineligible = [c for c in chunks if not c.eligible_for_retrieval]
    if ineligible:
        print(f"\nheld back from retrieval ({len(ineligible)}) — needs source work")
        for c in ineligible:
            print(f"  {c.chunk_id:52} {c.text_fidelity}")

    sizes = [c.char_count for c in chunks]
    if sizes:
        print(
            f"\nchunk size chars: min={min(sizes)} "
            f"median={sorted(sizes)[len(sizes)//2]} max={max(sizes)}"
        )
    split = [d for d in docs if sum(1 for c in chunks if c.doc_id == d.doc_id) > 2]
    print(f"records that required splitting: {len(split)}")

    if result.warnings:
        print(f"\nwarnings ({len(result.warnings)})")
        for w in result.warnings:
            print(f"  ! {w}")

    if verbose:
        print("\nchunk detail")
        for c in chunks:
            preview = c.text[:70].replace("\n", " ")
            print(f"  {c.chunk_id:52} {c.lang:5} {c.text_fidelity:20} {preview}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mundus Ulterior Part 3 ingestion")
    parser.add_argument("--corpus", type=Path, default=SEED_CORPUS_DIR)
    parser.add_argument("--dry-run", action="store_true", help="chunk only, no DB writes")
    parser.add_argument("--stats", action="store_true", help="report DB contents and exit")
    parser.add_argument("--json", type=Path, help="write chunk output to a JSON file")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--no-prune",
        action="store_true",
        help="keep DB rows for records no longer on disk",
    )
    args = parser.parse_args(argv)

    if args.stats:
        import psycopg
        from . import db

        with psycopg.connect(db.get_dsn()) as conn:
            print(json.dumps(db.summary(conn), indent=2, ensure_ascii=False))
        return 0

    if not args.corpus.exists():
        print(f"corpus directory not found: {args.corpus}", file=sys.stderr)
        print("run this from the repo root.", file=sys.stderr)
        return 2

    # Fail fast on a dead database, before printing a full report that looks
    # like the run succeeded.
    if not args.dry_run:
        from . import db as _db

        problem = _db.check_connection()
        if problem:
            print(problem, file=sys.stderr)
            return 2

    result = load_corpus(args.corpus)
    report(result, verbose=args.verbose)

    if args.json:
        args.json.write_text(
            json.dumps(to_jsonable(result), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nwrote {args.json}")

    if args.dry_run:
        print("\ndry run — nothing written to Postgres")
        return 0

    import psycopg
    from . import db

    with psycopg.connect(db.get_dsn()) as conn:
        db.apply_schema(conn)
        conn.commit()
        counts = db.write(conn, result.documents, result.chunks, prune=not args.no_prune)
        print(f"\nloaded into Postgres: {counts}")
        print(json.dumps(db.summary(conn), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
