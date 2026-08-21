-- D1 — the corpus version travels with every answer.
--
--     python scripts/apply_sql.py scripts/schema-d1.sql
--
-- Applied as one implicit transaction, like every other migration here.
--
-- WHY THIS EXISTS
--
-- `build_ui_data.py --verify` classifies every archived character span against
-- the seed corpus as it stands TODAY, and when a span no longer holds it must
-- say which of two things happened:
--
--     this span broke
--     this span was made against a different corpus
--
-- Until now those were the same observation. `classify_span` even ASSERTS the
-- second - "the seed record was edited after this run was archived" - on
-- evidence it does not have. Recording the corpus version at answer time turns
-- that inference into a fact.
--
-- WHAT IS RECORDED, AND WHY IT IS TWO THINGS
--
--   cited_record_hashes   the content hash of each record the answer cited.
--                         Answers "did the record this span quotes move?"
--   seed_corpus_digest    one hash over the whole seed corpus.
--                         Answers "is this the corpus that made this answer?"
--
-- Neither is recoverable from the other. A corpus can move somewhere else
-- entirely while every cited record is untouched - which is exactly the state
-- Block E must be able to assert did NOT happen between day one and day three.
--
-- WHAT IS NOT IN THE KEY
--
-- `answer_id` is UNCHANGED. It stays sha256 over (question, model, prompt
-- version, ordered chunk ids). Putting corpus state into it would rewrite the
-- identity of all 77 archived answers and make the Part 7-8 archive
-- incomparable with itself. New fields, new names, additive - the same
-- discipline ruling 26 held to when `rank_reranked` never overwrote `rank`.

ALTER TABLE answers ADD COLUMN IF NOT EXISTS
    corpus_digest_algorithm text;

ALTER TABLE answers ADD COLUMN IF NOT EXISTS
    seed_corpus_digest      text;

-- Defaulted to an EMPTY OBJECT, never to NULL-as-unknown, so that "this answer
-- recorded no hashes" and "this answer cited nothing" stay distinguishable from
-- each other and from a row written before this migration. Rows that predate
-- the migration keep NULL in the two text columns above, and NULL is the
-- signal `--verify` reads as UNKNOWN. It must never be read as "unchanged".
ALTER TABLE answers ADD COLUMN IF NOT EXISTS
    cited_record_hashes     jsonb NOT NULL DEFAULT '{}'::jsonb;

-- THE VIEW IS NOT REDEFINED HERE, AND THAT IS THE POINT.
--
-- The first version of this file carried a CREATE OR REPLACE VIEW for
-- `citable_passages`. It applied cleanly, and the very next run of
-- answer/run_answer.py died:
--
--     psycopg.errors.InvalidTableDefinition: cannot drop columns from view
--
-- `run_answer.py:234` calls `answer_store.apply_schema(conn)` on EVERY run,
-- which re-applies scripts/schema-part7.sql. That file owns `citable_passages`,
-- and CREATE OR REPLACE VIEW is authoritative: a migration that adds a column
-- to a view defined there is undone the next time anyone answers a question.
--
-- It failed loudly only because this migration ADDED a column. Had it removed
-- one, schema-part7.sql would have silently restored it and nothing would have
-- said so. The loudness was luck, not design.
--
-- `d.content_hash` therefore lives in scripts/schema-part7.sql, beside the rest
-- of the view. What stays here is only what CREATE TABLE IF NOT EXISTS cannot
-- do to a table that already exists: the three ALTERs above.
--
-- A distractor note, kept here beside the code that could get it wrong:
-- `documents.content_hash` is NOT one quantity. ingest/loader.py stores a
-- sha256 of the canonicalised record for the 24 seed documents;
-- ingest/load_distractors.py stores the literal string f"{source}-{object_id}"
-- for the other 426. A roll-up over both would hash a mixture of a digest and
-- an identifier, and would be completely STABLE under any edit to a
-- distractor's text. Scope every roll-up to `NOT is_distractor`.
