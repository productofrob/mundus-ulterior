-- Mundus Ulterior — Phase 2 Block B4: distractor containment.
--
-- PHASE2_PLAN.md B4: "The containment requirement is as strong as the Part 3
-- `eligible_for_retrieval` one — build it the same way, BY CONSTRUCTION rather
-- than by filter."
--
-- A distractor is padding for the W2b degradation curve. It must be reachable
-- from exactly one place — the ranking check at elevated N — and from nowhere
-- else. Not from the answer path, not from the translator, not from the map,
-- not from any count that describes the corpus.
--
-- The mechanism is that `retrievable_chunks` excludes distractors, and every
-- consumer that matters is built on top of it. `citable_passages` is built on
-- `retrievable_chunks`, so Part 7 inherits the exclusion without knowing this
-- file exists — the same way it inherited the `pointer` exclusion in Part 3.
--
-- Idempotent: safe to re-run.

-- --------------------------------------------------------------------------
-- 1. The flag
-- --------------------------------------------------------------------------

-- On BOTH tables. Chunks need it because that is what retrieval reads;
-- documents need it because the prune in ingest/db.py operates on documents,
-- and because a distractor document must be identifiable without joining.
ALTER TABLE documents ADD COLUMN IF NOT EXISTS
    is_distractor boolean NOT NULL DEFAULT false;
ALTER TABLE chunks    ADD COLUMN IF NOT EXISTS
    is_distractor boolean NOT NULL DEFAULT false;

-- Provenance for the Met material. NULL for everything that did not come from
-- there. `met_is_public_domain` is recorded rather than assumed: the CC0 grant
-- is a property of the individual object record and not of the API, so the
-- claim has to travel with the row (see data/met-licence-declaration.txt).
ALTER TABLE documents ADD COLUMN IF NOT EXISTS distractor_source text;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS met_is_public_domain boolean;

-- A distractor document and a seed document are different kinds of thing and
-- must not drift into each other by accident.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'documents_distractor_source') THEN
        ALTER TABLE documents ADD CONSTRAINT documents_distractor_source
            CHECK (
                (is_distractor AND distractor_source IS NOT NULL)
                OR (NOT is_distractor AND distractor_source IS NULL
                    AND met_is_public_domain IS NULL)
            );
    END IF;
END $$;

-- A chunk's distractor status must match its document's. Without this a
-- distractor document could hold a chunk flagged as corpus and it would be
-- citable — which is the entire failure this file exists to prevent, arriving
-- through the back door.
CREATE OR REPLACE FUNCTION assert_chunk_matches_document_distractor()
RETURNS trigger AS $$
DECLARE doc_flag boolean;
BEGIN
    SELECT is_distractor INTO doc_flag FROM documents WHERE doc_id = NEW.doc_id;
    IF doc_flag IS DISTINCT FROM NEW.is_distractor THEN
        RAISE EXCEPTION
            'chunk % has is_distractor=% but its document % has is_distractor=%',
            NEW.chunk_id, NEW.is_distractor, NEW.doc_id, doc_flag;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS chunks_distractor_matches_document ON chunks;
CREATE TRIGGER chunks_distractor_matches_document
    BEFORE INSERT OR UPDATE ON chunks
    FOR EACH ROW EXECUTE FUNCTION assert_chunk_matches_document_distractor();

-- --------------------------------------------------------------------------
-- 2. The two views
-- --------------------------------------------------------------------------

-- Unchanged in every column; one new clause. Everything downstream —
-- retrieve/search.py, citable_passages, and therefore the whole answer path —
-- becomes distractor-free without being edited.
CREATE OR REPLACE VIEW retrievable_chunks AS
SELECT chunk_id, doc_id, parallel_group, role, lang, declared_lang, text,
       text_fidelity, region, source_type, citation, date_text,
       char_start, char_end, source_field, embedding, embedding_model
FROM chunks
WHERE eligible_for_retrieval
  AND embedding IS NOT NULL
  AND NOT is_distractor;

-- The ONLY surface from which a distractor is visible. Read by
-- eval/run_ranking_check.py --with-distractors and by nothing else, ever.
-- `is_distractor` is selected so the B5 adjudication step can say whether the
-- thing that outranked a gold target was padding or corpus.
CREATE OR REPLACE VIEW retrievable_chunks_with_distractors AS
SELECT chunk_id, doc_id, parallel_group, role, lang, declared_lang, text,
       text_fidelity, region, source_type, citation, date_text,
       char_start, char_end, source_field, embedding, embedding_model,
       is_distractor
FROM chunks
WHERE eligible_for_retrieval
  AND embedding IS NOT NULL;

-- --------------------------------------------------------------------------
-- 3. The canary
-- --------------------------------------------------------------------------
--
-- A permanent synthetic distractor, loaded by this file rather than by any
-- fetch. It exists so the containment assertions can run and fail on an index
-- holding no real distractors at all.
--
-- Without it the containment test would be vacuous until the day 400 chunks
-- land — and a test written after the data is a test that can pass because the
-- data happens to be absent. That is the tautology this repository has now paid
-- for nine times. The canary makes containment falsifiable from today.
--
-- Its text is a sentinel string that appears nowhere in the corpus, so any
-- assertion can search for it directly.
--
-- CORRECTED 2026-08-16. This comment used to end: "It carries NO embedding,
-- which means it is invisible to both views (they require `embedding IS NOT
-- NULL`) and cannot perturb a ranking run. It is a containment fixture, not a
-- distractor." Every clause of that was false one command later. The row is
-- inserted `eligible_for_retrieval = true` — deliberately, because a canary
-- held back by eligibility would prove nothing about the distractor flag — so
-- the next `python -m ingest.run_embed` embeds it like any other eligible
-- chunk. It has been one of the 450 since B4, and `BLOCK_C_START.md` said so
-- ("393 distractors, one of which is the canary") while this comment said the
-- opposite. Two documents, two days, nothing comparing them.
--
-- It IS a distractor and it competes. On 2026-08-16 it was the best competing
-- document for the gold pair `tc-nabataean-epitaph`, moving that pair's gapDoc
-- from +0.146 to +0.107. Visible only because the ranking run now records
-- `best_other_doc_chunk_id`; until 2026-08-14 it recorded the similarity and
-- not the chunk, and this would have stayed invisible.
--
-- What pins it is `ingest/test_distractors.py`, which already asserted the
-- truth while this comment asserted the opposite: a vectorised canary is
-- INVISIBLE to `retrievable_chunks` and to `citable_passages`, and VISIBLE to
-- `retrievable_chunks_with_distractors`. Containment held throughout. The prose
-- describing it did not.

INSERT INTO documents (
    doc_id, region, title, source_type, language_codes, citation,
    source_path, content_hash, is_distractor, distractor_source
) VALUES (
    '__canary__', 'Distractor', 'Containment canary', 'synthetic',
    ARRAY['en'],
    'Synthetic row created by scripts/schema-b4-distractors.sql. Not a source.',
    'synthetic://canary', 'synthetic',
    true, 'canary'
)
ON CONFLICT (doc_id) DO NOTHING;

-- Every NOT NULL column of `chunks` is named here, including
-- `parallel_group`, which has no meaning for a synthetic row and is set to the
-- doc id rather than left out. The first draft of this INSERT omitted it and
-- failed on the NOT NULL constraint — an INSERT written against a table whose
-- DDL had not been read. `ingest/test_distractors.py` now derives the NOT NULL
-- set from schema-part3.sql and asserts this statement covers it, so the next
-- omission is a test failure rather than a stack trace on the host.
INSERT INTO chunks (
    chunk_id, doc_id, parallel_group, role, seq, lang, text,
    char_start, char_end, source_field, text_fidelity, is_pointer,
    eligible_for_retrieval, region, source_type, citation,
    char_count, token_estimate, is_distractor
) VALUES (
    '__canary__::distractor::000', '__canary__', '__canary__', 'original', 0, 'en',
    'MUNDUS-ULTERIOR-CANARY-DISTRACTOR-DO-NOT-CITE',
    0, 45, 'synthetic', 'object_description', false,
    true, 'Distractor', 'synthetic',
    'Synthetic row. If this text reaches a user, containment has failed.',
    45, 11, true
)
ON CONFLICT (chunk_id) DO NOTHING;

-- --------------------------------------------------------------------------
-- 4. What this file does NOT fix, recorded here because it is load-bearing
-- --------------------------------------------------------------------------
--
-- Two hazards were found by auditing every reader of `chunks` and `documents`
-- before any distractor was fetched. Neither is a schema problem and neither is
-- solved by the views above. Both are fixed in Python, and both have a
-- regression test:
--
-- (a) ingest/db.py's prune runs
--         DELETE FROM documents WHERE NOT (doc_id = ANY(seed_doc_ids))
--     and chunks.doc_id REFERENCES documents(doc_id) ON DELETE CASCADE. Every
--     distractor document is absent from the seed list, so ONE ROUTINE
--     `python -m ingest.run_ingest` WOULD CASCADE-DELETE THE ENTIRE DISTRACTOR
--     CORPUS — 400 chunks and the embedding requests that produced them —
--     silently, from the command that opens every session.
--
-- (b) answer/store.py reads `FROM chunks` directly in three places, filtering
--     only on `eligible_for_retrieval`, which distractors must be. The worst is
--     SELECT_TRANSLATABLE: it would feed non-English distractors to the
--     translation pipeline and spend money translating Strabo. TRANSLATION_STATS
--     would report an inflated `translatable` count from the same defect.
--
-- PHASE2_PLAN.md B4 names `ingest/verify`, `answer/run_answer` and
-- `ui/build_ui_data.py` as the readers to make blind. `answer/store.py` is on
-- none of those lists and is the one that spends money.
