"""Cross-lingual sanity check — the Part 4 exit condition.

Run:  python -m retrieve.crosslingual_check

This is a sanity check, not the Part 8 eval harness. It answers one question:
does the embedding model actually place a query and a source in the same
semantic space when they are written in different scripts?

Three probe families, in increasing order of difficulty:

  1. SAME-LANGUAGE  — a Greek query should find the Greek text. If this fails,
     the model doesn't handle the script at all and nothing else matters.
  2. CROSS-LINGUAL  — an English query should find the NON-ENGLISH source, with
     English translations excluded from the candidate pool so the model cannot
     cheat by matching English to English. This is the actual claim the project
     rests on.
  3. PAIRED QUERY   — the same question asked in two languages should return the
     same document. This is the "same query, two languages" test named in the
     Phase 1 plan.

A failure here is informative, not fatal: it is the evidence that would justify
swapping voyage-3.5 for BGE-M3. Record which probes failed before switching.

The probes themselves moved to eval/gold/retrieval_probes.json in Part 6. They
were eleven hardcoded objects in this file, and one of them passed for the wrong
reason for a whole afternoon; expectations belong somewhere they can be read and
argued with without reading a runner.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict

from eval.goldset import Probe, load_probes

from .search import get_dsn, search


def rank_of(hits, probe: Probe) -> int | None:
    """Rank of the first hit that satisfies the probe.

    Satisfying means the right document AND, where the probe demands it, the
    right passage within that document. Matching on doc_id alone once let the
    pepper probe report PASS against Periplus §53 while §56 — the passage that
    actually mentions pepper — was not even loaded.
    """
    for i, hit in enumerate(hits, start=1):
        if hit.doc_id != probe.expect_doc:
            continue
        if probe.expect_text_contains and probe.expect_text_contains not in hit.text:
            continue
        return i
    return None


def main(argv: list[str] | None = None) -> int:
    import psycopg

    from ingest.embed import EmbeddingError, embed_texts

    k = 5
    results: list[dict] = []
    ranking_failures = 0
    probes = load_probes()

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM retrievable_chunks;")
            available = cur.fetchone()[0]
        if available == 0:
            print(
                "no embedded chunks — run `python -m ingest.run_embed` first.",
                file=sys.stderr,
            )
            return 2
        print(f"searching {available} embedded chunks with {len(probes)} probes")

        # Every probe query goes in ONE request. Embedding them one at a time
        # made 10 calls and tripped Voyage's free-tier limit of 3 requests per
        # minute — an infrastructure failure that looked exactly like a model
        # failure in the output. Ten short queries are far inside the 10K
        # tokens/minute ceiling, so one batch costs one request.
        try:
            embedded = embed_texts(
                [p.query for p in probes],
                input_type="query",
                batch_size=len(probes),
            )
        except EmbeddingError as exc:
            print(f"\ncould not embed the probe queries:\n{exc}", file=sys.stderr)
            return 2
        for note in embedded.notes:
            print(f"  note: {note}")
        print(f"embedded {len(probes)} probe queries in {embedded.batches} request(s)\n")

        for probe, vector in zip(probes, embedded.vectors):
            hits = search(conn, vector, k=k, langs=probe.langs, roles=probe.roles)
            rank = rank_of(hits, probe)
            passed = rank == 1
            top = hits[0] if hits else None

            status = "PASS" if passed else ("NEAR" if rank else "FAIL")
            if not passed:
                ranking_failures += 1

            print(f"[{status}] {probe.name}")
            print(f"        expected {probe.expect_doc} -> rank {rank or f'>{k}'}")
            if top:
                print(
                    f"        top hit: {top.doc_id} ({top.lang}, {top.role}, "
                    f"sim {top.similarity:.3f}) {top.preview(60)}"
                )
            results.append(
                {
                    "probe": probe.name,
                    "kind": probe.kind,
                    "pair": probe.pair,
                    "expected": probe.expect_doc,
                    "rank": rank,
                    "status": status,
                    "top_doc": top.doc_id if top else None,
                    "top_similarity": round(top.similarity, 4) if top else None,
                }
            )

    # Paired probes must agree with each other, not merely both rank first.
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        if r["kind"] == "paired" and r["pair"]:
            groups[r["pair"]].append(r)
    for name, members in sorted(groups.items()):
        tops = {m["top_doc"] for m in members}
        agree = len(tops) == 1
        print(
            f"\n[{'PASS' if agree else 'FAIL'}] paired '{name}' agree: "
            f"{' vs '.join(str(m['top_doc']) for m in members)}"
        )
        if not agree:
            ranking_failures += 1

    by_kind: dict[str, list[str]] = {}
    for r in results:
        by_kind.setdefault(r["kind"], []).append(r["status"])
    print("\nsummary by probe family")
    for kind, statuses in by_kind.items():
        passed = sum(1 for s in statuses if s == "PASS")
        print(f"  {kind:15} {passed}/{len(statuses)} at rank 1")

    with open("eval/crosslingual_check_last_run.json", "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    print("\nwrote eval/crosslingual_check_last_run.json")

    if ranking_failures:
        kinds_failed = {r["kind"] for r in results if r["status"] != "PASS"}
        print(f"\n{ranking_failures} probe(s) did not rank the expected source first.")
        if "same_language" in kinds_failed:
            print(
                "  same_language failed — the model cannot handle that script at all. "
                "This is the strongest case for BGE-M3."
            )
        if "cross_lingual" in kinds_failed:
            print(
                "  cross_lingual failed — each language is seen, but the shared space "
                "is weak. Also a case for BGE-M3."
            )
        if kinds_failed == {"paired"}:
            print(
                "  only paired probes failed, and same_language/cross_lingual passed. "
                "That is a probe-design issue or a near-miss within the same work, not "
                "a model failure — inspect the top hit before concluding anything about "
                "the embedding model."
            )
        return 1

    print("\nAll cross-lingual probes passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
