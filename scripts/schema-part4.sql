-- Mundus Ulterior — Phase 1 Part 4: embedding provenance + vector index.
--
-- Why the provenance columns: the plan is to embed with voyage-3.5 now and
-- revisit BGE-M3 only if Voyage measurably fails on the hard languages. That
-- decision is only reversible if the table records WHICH model produced each
-- vector. Without it, a half-migrated table is indistinguishable from a
-- finished one, and cosine distances across two models are meaningless.
--
-- Idempotent: safe to re-run.

ALTER TABLE chunks ADD COLUMN IF NOT EXISTS embedding_model text;
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS embedding_dim  integer;
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS embedded_at    timestamptz;

-- An embedding without a model label is unusable; a model label without an
-- embedding is a lie. Keep them in lockstep.
ALTER TABLE chunks DROP CONSTRAINT IF EXISTS chunks_embedding_provenance;
ALTER TABLE chunks ADD CONSTRAINT chunks_embedding_provenance CHECK (
    (embedding IS NULL AND embedding_model IS NULL)
    OR (embedding IS NOT NULL AND embedding_model IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS chunks_embedding_model_idx ON chunks (embedding_model);

-- Vector index. Cosine, because voyage-3.5 returns L2-normalised vectors and
-- BGE-M3 dense output is normalised too — so the same operator class survives a
-- model swap. Query with the matching operator (<=>) or the index is ignored.
--
-- m/ef_construction are left at pgvector defaults (16/64): at 42 vectors the
-- index is irrelevant to latency and exists to keep the query path identical to
-- what it will be at corpus scale. Revisit when the corpus passes ~10k chunks.
CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);

-- Convenience view: what retrieval is actually allowed to see.
CREATE OR REPLACE VIEW retrievable_chunks AS
SELECT chunk_id, doc_id, parallel_group, role, lang, declared_lang, text,
       text_fidelity, region, source_type, citation, date_text,
       char_start, char_end, source_field, embedding, embedding_model
FROM chunks
WHERE eligible_for_retrieval
  AND embedding IS NOT NULL;
