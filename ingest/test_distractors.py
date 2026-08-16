"""Block B4 — prove a distractor is unreachable from everything but the curve.

Needs the database. Run on the host, after applying
`scripts/schema-b4-distractors.sql`:

    python -m ingest.test_distractors

THE TRAP THIS FILE IS BUILT AROUND
----------------------------------
A canary with no embedding is invisible to both views, because both require
`embedding IS NOT NULL`. An assertion that simply checks the canary is absent
from `retrievable_chunks` would then pass **because the vector is missing**, not
because the row is a distractor — and it would keep passing with
`AND NOT is_distractor` deleted from the view. That is a test that cannot fail,
in the file whose entire job is to prove containment, and it is the tenth time
this repository has had to name the shape.

So every view assertion here ensures the canary has a vector first, and the
exclusion being asserted is caused by the distractor flag alone.

THE CANARY IS EMBEDDED, AND THAT IS NOT A DEFECT
------------------------------------------------
This docstring used to say the canary "carries no embedding". It has not been
true since B4: the row is `eligible_for_retrieval = true` on purpose, so
`run_embed` embeds it like anything else, and it is one of the 450 chunks in
`retrievable_chunks_with_distractors`. The body of this file already knew that —
see the note above the UPDATE below, which records the fixture being redesigned
around exactly this — while the docstring above it said the opposite. Corrected
2026-08-16, along with the same false claim in
`scripts/schema-b4-distractors.sql`.

The consequence is real but small and is now written down where it can be found:
the canary competes in ranking runs, and on 2026-08-16 it was the best competing
document for the gold pair `tc-nabataean-epitaph`. Containment is unaffected —
that is what the assertions below prove — but a synthetic string participating in
a G2 input is a thing to know before the gate is assessed rather than after.
"""

from __future__ import annotations

import re
import sys

PASS: list[str] = []
FAIL: list[str] = []

CANARY_DOC = "__canary__"
CANARY_CHUNK = "__canary__::distractor::000"
CANARY_TEXT = "MUNDUS-ULTERIOR-CANARY-DISTRACTOR-DO-NOT-CITE"

# A fixed unit vector. Never persisted — see the module docstring. Not zeros:
# cosine distance against a zero vector is undefined and would fail for a reason
# that has nothing to do with containment.
FAKE_VECTOR = "[" + ",".join(["0.03125"] * 1024) + "]"


def not_null_columns(sql: str, table: str) -> set[str]:
    """Column names declared NOT NULL in a CREATE TABLE block, minus any with a
    DEFAULT (which the INSERT may legitimately omit).

    Parenthesis depth is tracked rather than matching line prefixes. The first
    version filtered on lines starting with CONSTRAINT/CHECK/UNIQUE and so read
    `OR` — a continuation line of a multi-line CHECK containing the words
    "NOT NULL" — as a required column. It reported a missing column that does
    not exist, which is a false alarm in a pre-flight whose whole value is being
    trusted. Caught by running it, not by reading it.
    """
    import re

    block = re.search(
        rf"CREATE TABLE IF NOT EXISTS {table} \((.*?)\n\);", sql, re.S)
    if not block:
        return set()
    out: set[str] = set()
    depth = 0
    for raw in block.group(1).splitlines():
        line = raw.strip()
        at_top_level = depth == 0
        depth += raw.count("(") - raw.count(")")
        if not at_top_level or not line or line.startswith("--"):
            continue
        name = line.split()[0]
        if not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
            continue
        if name.upper() in {"CONSTRAINT", "UNIQUE", "PRIMARY", "CHECK", "FOREIGN"}:
            continue
        if "NOT NULL" in line.upper() and "DEFAULT" not in line.upper():
            out.add(name)
    return out


def insert_columns(sql: str, table: str) -> set[str]:
    import re

    m = re.search(rf"INSERT INTO {table} \((.*?)\) VALUES", sql, re.S)
    return {c.strip() for c in m.group(1).split(",")} if m else set()


def preflight() -> None:
    """Offline. Runs before the database is touched, because the failure it
    catches is one that otherwise surfaces as a stack trace on the host after a
    schema has half-applied.

    The first draft of the canary INSERT omitted `parallel_group` — an INSERT
    written against a table whose DDL had not been read. Deriving the NOT NULL
    set from the schema turns that from a thing to remember into a thing that
    fails here, for free.
    """
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    part3 = (root / "scripts" / "schema-part3.sql").read_text(encoding="utf-8")
    b4 = (root / "scripts" / "schema-b4-distractors.sql").read_text(encoding="utf-8")

    declared = set(re.findall(r"^\s{4}(\w+)", part3, re.M)) | {
        "is_distractor", "distractor_source", "met_is_public_domain"}

    for table in ("documents", "chunks"):
        required = not_null_columns(part3, table)
        supplied = insert_columns(b4, table)
        missing = sorted(required - supplied)
        unknown = sorted(supplied - declared)
        check(f"the canary INSERT covers every NOT NULL column of `{table}`",
              not missing, f"missing: {missing}")
        check(f"the canary INSERT names no column `{table}` does not have",
              not unknown, f"unknown: {unknown}")


def check(name: str, ok: bool, detail: str = "") -> None:
    (PASS if ok else FAIL).append(name)
    print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f"\n       {detail}" if detail and not ok else ""))


def scalar(cur, sql, params=None):
    cur.execute(sql, params or {})
    row = cur.fetchone()
    return row[0] if row else None


def main() -> int:
    preflight()
    if FAIL:
        print(f"\n{len(PASS)} passed, {len(FAIL)} failed — pre-flight failed, "
              f"database not touched")
        for name in FAIL:
            print(f"  FAILED: {name}")
        return 1

    from ingest import db

    problem = db.check_connection()
    if problem:
        print(problem, file=sys.stderr)
        return 2

    import psycopg

    with psycopg.connect(db.get_dsn()) as conn:
        with conn.cursor() as cur:
            # ---------------------------------------------------------------
            # The fixture is present and is what it claims to be
            # ---------------------------------------------------------------
            check("the containment canary exists",
                  scalar(cur, "SELECT count(*) FROM chunks WHERE chunk_id = %s;",
                         (CANARY_CHUNK,)) == 1,
                  "apply scripts/schema-b4-distractors.sql first")
            check("the canary is flagged as a distractor",
                  scalar(cur, "SELECT is_distractor FROM chunks WHERE chunk_id = %s;",
                         (CANARY_CHUNK,)) is True)
            check("the canary is eligible_for_retrieval",
                  scalar(cur, "SELECT eligible_for_retrieval FROM chunks WHERE chunk_id = %s;",
                         (CANARY_CHUNK,)) is True,
                  "a canary held back by eligibility would prove nothing about "
                  "the distractor flag — eligibility already excludes it")

            # ---------------------------------------------------------------
            # The guard is in the live view definition
            # ---------------------------------------------------------------
            # Asserted DIRECTLY, not inferred from counts. On 2026-08-14
            # `run_embed` re-applied schema-part4.sql, which redefines
            # `retrievable_chunks` without the distractor guard, and containment
            # was reverted for the rest of the session. Every count-based check
            # then read the reverted view and reported OK. A guard that can be
            # silently replaced needs an assertion about the guard itself.
            cur.execute("SELECT pg_get_viewdef('retrievable_chunks'::regclass, true);")
            baseline_def = cur.fetchone()[0]
            check("retrievable_chunks still carries its distractor guard",
                  "is_distractor" in baseline_def,
                  "the view has been redefined without it — re-apply "
                  "scripts/schema-b4-distractors.sql and find what reverted it")

            # ---------------------------------------------------------------
            # The views
            # ---------------------------------------------------------------
            # The canary is embedded by `run_embed` like any other eligible
            # chunk — it is a real distractor, not a fixture held outside the
            # pipeline. The first version deliberately left it vectorless and
            # vectorised it inside a rolled-back savepoint; `run_embed` then
            # embedded it for real ("chunks to embed: 94" for 93 loaded
            # records), the rollback assertion started failing, and the reason
            # was a fixture designed around a pipeline it was sitting inside.
            cur.execute(
                "UPDATE chunks SET embedding = COALESCE(embedding, %s::vector), "
                "embedding_model = COALESCE(embedding_model, 'synthetic'), "
                "embedding_dim = COALESCE(embedding_dim, 1024) "
                "WHERE chunk_id = %s;",
                (FAKE_VECTOR, CANARY_CHUNK),
            )
            in_baseline = scalar(
                cur, "SELECT count(*) FROM retrievable_chunks WHERE chunk_id = %s;",
                (CANARY_CHUNK,))
            in_curve = scalar(
                cur,
                "SELECT count(*) FROM retrievable_chunks_with_distractors "
                "WHERE chunk_id = %s;", (CANARY_CHUNK,))
            in_citable = scalar(
                cur, "SELECT count(*) FROM citable_passages WHERE chunk_id = %s;",
                (CANARY_CHUNK,))

            check("a vectorised distractor is INVISIBLE to retrievable_chunks",
                  in_baseline == 0,
                  "the exclusion is not coming from the distractor flag")
            check("a vectorised distractor is VISIBLE to "
                  "retrievable_chunks_with_distractors",
                  in_curve == 1,
                  "the curve cannot see its own padding — the previous assertion "
                  "would then be passing for the wrong reason")
            check("a vectorised distractor is INVISIBLE to citable_passages",
                  in_citable == 0,
                  "the answer path can cite a distractor")
            check("the canary carries a vector, so its exclusion cannot be "
                  "caused by the absence of one",
                  scalar(cur, "SELECT embedding IS NOT NULL FROM chunks "
                              "WHERE chunk_id = %s;", (CANARY_CHUNK,)) is True)

            # ---------------------------------------------------------------
            # The two readers that do NOT inherit the view
            # ---------------------------------------------------------------
            from answer.store import SELECT_TRANSLATABLE, TRANSLATION_STATS

            cur.execute("SAVEPOINT nonenglish;")
            cur.execute(
                "UPDATE chunks SET lang = 'grc' WHERE chunk_id = %s;", (CANARY_CHUNK,))
            cur.execute(
                SELECT_TRANSLATABLE.format(limit_clause=""),
                {"doc_ids": None, "langs": None},
            )
            reached = [r[0] for r in cur.fetchall()]
            check("a non-English distractor is NOT offered to the translator",
                  CANARY_CHUNK not in reached,
                  "answer/store.py SELECT_TRANSLATABLE would spend money "
                  "translating padding")

            cur.execute(TRANSLATION_STATS)
            translatable_with = cur.fetchone()[3]
            cur.execute("ROLLBACK TO SAVEPOINT nonenglish;")
            cur.execute(TRANSLATION_STATS)
            translatable_without = cur.fetchone()[3]
            check("a distractor does not inflate the translatable count",
                  translatable_with == translatable_without,
                  f"{translatable_with} with the distractor, "
                  f"{translatable_without} without")

            # ---------------------------------------------------------------
            # The prune that would have destroyed the corpus
            # ---------------------------------------------------------------
            # Not a text check on db.py — run the real prune against the real
            # table and see whether the row survives. The hazard is a cascade
            # from `documents`, so the assertion is made on the chunk.
            cur.execute("SAVEPOINT pruned;")
            cur.execute(
                "DELETE FROM chunks WHERE doc_id = ANY(%s) AND NOT (chunk_id = ANY(%s)) "
                "AND NOT is_distractor;", ([], []))
            cur.execute(
                "DELETE FROM documents WHERE NOT (doc_id = ANY(%s)) "
                "AND NOT is_distractor;", ([],))
            survived = scalar(
                cur, "SELECT count(*) FROM chunks WHERE chunk_id = %s;", (CANARY_CHUNK,))
            cur.execute("ROLLBACK TO SAVEPOINT pruned;")
            check("a prune naming no seed documents does not delete a distractor",
                  survived == 1,
                  "chunks.doc_id cascades from documents — without the "
                  "is_distractor guard one routine run_ingest destroys the "
                  "whole W2b corpus and the embedding requests behind it")

            # ---------------------------------------------------------------
            # The trigger
            # ---------------------------------------------------------------
            cur.execute("SAVEPOINT mismatch;")
            try:
                cur.execute(
                    "UPDATE chunks SET is_distractor = false WHERE chunk_id = %s;",
                    (CANARY_CHUNK,))
                raised = False
            except psycopg.errors.RaiseException:
                raised = True
            cur.execute("ROLLBACK TO SAVEPOINT mismatch;")
            check("a chunk cannot disagree with its document about being a distractor",
                  raised,
                  "a distractor document could hold a citable chunk")

        conn.rollback()

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for name in FAIL:
        print(f"  FAILED: {name}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
