"""Block B4 — load fetched distractors into Postgres, in stratified tranches.

    python -m ingest.load_distractors --plan               # what would load, no writes
    python -m ingest.load_distractors --target-index 150
    python -m ingest.load_distractors --target-index 450

Reads every `data/distractors/*.json` written by a fetcher, in the shared shape
from `ingest/distractors_common.write_records`.

WHY --target-index AND NOT --limit
----------------------------------
The W2b rungs are **57 → 150 → 450**, and those are INDEX SIZES, not distractor
counts. `PHASE2_PLAN.md` gives the rungs and `BLOCK_B3_DISTRACTORS.md` gives a
~400 total, and it is easy to read the pair as one load of 400 — which skips the
middle rung entirely. So the loader is told the index size it must reach and
works out the rest against the live count.

WHY STRATIFIED
--------------
If tranche 1 were all Met and tranche 2 all Cleveland, the 150 and 450 rungs
would differ in **composition as well as size**, and the curve would report as
degradation-with-scale something that is really a change in what the padding is
made of. The curve must vary one thing. Each tranche therefore takes the same
proportion from each source, sampled deterministically from `SEED`, and the
composition is written into the run so it can be checked rather than assumed.

WHAT IT REFUSES TO DO
---------------------
Write a distractor row with `is_distractor = false`. The database would stop it
anyway — `scripts/schema-b4-distractors.sql` installs a trigger asserting a
chunk agrees with its document — but a loader that depends on a trigger to be
correct is a loader that is wrong and lucky.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingest.distractors_common import MAX_CHARS, OUT_DIR, SEED  # noqa: E402

# Distractor rows carry values that must never collide with the seed corpus's
# own vocabulary, so a distractor is visible as one in any report that groups by
# region or source type — even a report written before this block existed.
DISTRACTOR_REGION = "Distractor"
DISTRACTOR_SOURCE_TYPE = "distractor"
TEXT_FIDELITY = "object_description"


def load_files() -> list[dict]:
    payloads = []
    for path in sorted(OUT_DIR.glob("*.json")):
        if path.name.endswith("-api-shape.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema", "").startswith("mundus-ulterior/distractors/"):
            data["_path"] = str(path)
            payloads.append(data)
    return payloads


def plan(payloads: list[dict], have: int, target: int, already: set[str]) -> dict:
    """Which records to add, proportionally across sources, to reach `target`."""
    need = max(0, target - have)
    pools = {}
    for p in payloads:
        fresh = [r for r in p["records"]
                 if doc_id_for(p["source"], r) not in already]
        if fresh:
            pools[p["source"]] = fresh
    total_available = sum(len(v) for v in pools.values())

    chosen: dict[str, list] = {}
    if not pools or need == 0:
        return {"need": need, "available": total_available, "chosen": chosen,
                "shortfall": need}

    rng = random.Random(SEED)
    # Proportional to what each source actually has, so one small source cannot
    # starve the tranche and one large source cannot dominate it.
    for source, records in sorted(pools.items()):
        share = len(records) / total_available
        want = min(len(records), round(need * share))
        chosen[source] = rng.sample(sorted(records, key=lambda r: str(r["object_id"])),
                                    want)

    # Rounding can leave the tranche a record or two short of `need`; top up
    # from whichever source still has the most left, deterministically.
    picked = sum(len(v) for v in chosen.values())
    while picked < need:
        room = {s: len(pools[s]) - len(chosen.get(s, [])) for s in pools}
        best = max(sorted(room), key=lambda s: room[s])
        if room[best] <= 0:
            break
        remaining = [r for r in pools[best] if r not in chosen.get(best, [])]
        chosen.setdefault(best, []).append(remaining[0])
        picked += 1

    return {"need": need, "available": total_available, "chosen": chosen,
            "shortfall": max(0, need - picked)}


def doc_id_for(source: str, record: dict) -> str:
    return f"distractor-{source}-{record['object_id']}"


def rows_for(source: str, record: dict, licence: str) -> tuple[dict, dict]:
    doc_id = doc_id_for(source, record)
    text = record["text"]
    citation = (f"{record.get('title') or 'Untitled'} — {source.upper()} "
                f"{record['object_id']}. {record.get('object_url') or ''} "
                f"({licence})").strip()
    doc = {
        "doc_id": doc_id,
        "region": DISTRACTOR_REGION,
        "title": record.get("title") or f"{source} {record['object_id']}",
        "source_type": DISTRACTOR_SOURCE_TYPE,
        "language_codes": ["en"],
        "citation": citation,
        "source_path": record.get("object_url") or f"{source}:{record['object_id']}",
        "content_hash": f"{source}-{record['object_id']}",
        "is_distractor": True,
        "distractor_source": source,
        "met_is_public_domain": record.get("is_public_domain") if source == "met" else None,
    }
    chunk = {
        "chunk_id": f"{doc_id}::distractor::000",
        "doc_id": doc_id,
        "parallel_group": doc_id,
        "role": "original",
        "seq": 0,
        "lang": "en",
        "text": text,
        "char_start": 0,
        "char_end": len(text),
        "source_field": "rendered_catalogue_record",
        "text_fidelity": TEXT_FIDELITY,
        "is_pointer": False,
        "eligible_for_retrieval": True,
        "region": DISTRACTOR_REGION,
        "source_type": DISTRACTOR_SOURCE_TYPE,
        "citation": citation,
        "char_count": len(text),
        "token_estimate": max(1, len(text) // 4),
        "is_distractor": True,
    }
    # One chunk per record, deliberately: every distractor is capped at
    # MAX_CHARS = 1200 by the fetcher, which is the chunker's own splitting
    # threshold, so the chunker would emit exactly this one chunk anyway.
    #
    # The first version of this comment claimed "these texts are 120-400
    # characters". That was false the moment Cleveland arrived: its
    # descriptions ran to 1422. The claim was written from the Met's preview
    # and never rechecked — the same shape of error as the rest of this block,
    # in a justification rather than in a guard. The cap now makes the claim
    # true by construction rather than by assertion.
    if len(text) > MAX_CHARS:
        raise SystemExit(
            f"{chunk['chunk_id']} is {len(text)} characters, over MAX_CHARS "
            f"({MAX_CHARS}). The fetcher should have capped it; loading it "
            f"would put a chunk in the padding longer than any the chunker "
            f"would emit for the corpus.")
    return doc, chunk


INSERT_DOC = """
INSERT INTO documents (doc_id, region, title, source_type, language_codes,
                       citation, source_path, content_hash,
                       is_distractor, distractor_source, met_is_public_domain)
VALUES (%(doc_id)s, %(region)s, %(title)s, %(source_type)s, %(language_codes)s,
        %(citation)s, %(source_path)s, %(content_hash)s,
        %(is_distractor)s, %(distractor_source)s, %(met_is_public_domain)s)
ON CONFLICT (doc_id) DO NOTHING;
"""

INSERT_CHUNK = """
INSERT INTO chunks (chunk_id, doc_id, parallel_group, role, seq, lang, text,
                    char_start, char_end, source_field, text_fidelity,
                    is_pointer, eligible_for_retrieval, region, source_type,
                    citation, char_count, token_estimate, is_distractor)
VALUES (%(chunk_id)s, %(doc_id)s, %(parallel_group)s, %(role)s, %(seq)s,
        %(lang)s, %(text)s, %(char_start)s, %(char_end)s, %(source_field)s,
        %(text_fidelity)s, %(is_pointer)s, %(eligible_for_retrieval)s,
        %(region)s, %(source_type)s, %(citation)s, %(char_count)s,
        %(token_estimate)s, %(is_distractor)s)
ON CONFLICT (chunk_id) DO NOTHING;
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--target-index", type=int,
                    help="total retrievable chunks INCLUDING distractors to "
                         "reach (the W2b rungs are 150 and 450)")
    ap.add_argument("--plan", action="store_true",
                    help="report what would load and write nothing")
    args = ap.parse_args(argv)

    payloads = load_files()
    if not payloads:
        raise SystemExit(
            f"no distractor files in {OUT_DIR}. Run a fetcher first.")
    licences = {p["source"]: p.get("licence", "unstated") for p in payloads}
    print("distractor files:")
    for p in payloads:
        print(f"  {p['source']:8s} {len(p['records']):5d} records  "
              f"{Path(p['_path']).name}")

    from ingest import db

    problem = db.check_connection()
    if problem:
        raise SystemExit(problem)

    import psycopg

    with psycopg.connect(db.get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM retrievable_chunks_with_distractors;")
            have = int(cur.fetchone()[0])
            cur.execute("SELECT count(*) FROM retrievable_chunks;")
            corpus = int(cur.fetchone()[0])
            cur.execute("SELECT doc_id FROM documents WHERE is_distractor;")
            already = {r[0] for r in cur.fetchall()}

        print(f"\nindex now: {corpus} corpus chunks, "
              f"{have} including distractors ({len(already)} distractor docs)")

        if not args.target_index:
            print("\nno --target-index given; nothing to plan. "
                  "The W2b rungs are 150 and 450.")
            return 0

        result = plan(payloads, have, args.target_index, already)
        print(f"\nto reach an index of {args.target_index}: need {result['need']}, "
              f"{result['available']} unloaded records available")
        for source, recs in sorted(result["chosen"].items()):
            print(f"  {source:8s} {len(recs):5d}")
        if result["shortfall"]:
            print(f"  SHORTFALL {result['shortfall']} — the rung will be "
                  f"{args.target_index - result['shortfall']}, not "
                  f"{args.target_index}. Recorded, not silently absorbed: a curve "
                  f"whose rungs are not where they claim to be is not a curve.")

        if args.plan:
            print("\n--plan: nothing written")
            return 0

        written = 0
        with conn.cursor() as cur:
            for source, recs in sorted(result["chosen"].items()):
                for rec in recs:
                    doc, chunk = rows_for(source, rec, licences.get(source, "unstated"))
                    if not (doc["is_distractor"] and chunk["is_distractor"]):
                        raise SystemExit(
                            "refusing to write a distractor row with "
                            "is_distractor false")
                    cur.execute(INSERT_DOC, doc)
                    cur.execute(INSERT_CHUNK, chunk)
                    written += 1
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM retrievable_chunks;")
            corpus_after = int(cur.fetchone()[0])
            cur.execute("SELECT count(*) FROM chunks WHERE is_distractor;")
            distractors = int(cur.fetchone()[0])

    print(f"\nwrote {written} distractor documents + chunks")
    print(f"corpus chunks unchanged: {corpus} -> {corpus_after}"
          f"{'  OK' if corpus == corpus_after else '   <- CONTAINMENT FAILURE'}")
    print(f"distractor chunks in table: {distractors}")
    print("\nthey carry no vector yet. Next:")
    print("  python -m ingest.run_embed        # embeds distractors too")
    print("  python -m ingest.test_distractors # containment, with real rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
