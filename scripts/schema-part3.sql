-- Mundus Ulterior — Phase 1 Part 3 schema: documents + chunks with provenance.
--
-- Design notes:
--   * One row in `documents` per seed-corpus JSON record.
--   * One row in `chunks` per language-separated passage. Original-language text
--     and its reference translation are SEPARATE chunks sharing a `parallel_group`,
--     so Part 5's same-query-two-languages test can retrieve each independently.
--   * Provenance is denormalised onto `chunks` (region, citation, date_text,
--     source_type) so retrieval can filter and cite without a join.
--   * `char_start`/`char_end` are exact offsets into the named `source_field` of
--     the source JSON, so any chunk can be traced back to its bytes on disk.
--   * `embedding` stays NULL until Part 4 populates it. 1024 dims covers both
--     voyage-3.5 (current) and BGE-M3 (planned), so no migration is needed.
--
-- Idempotent: safe to re-run.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    doc_id            text PRIMARY KEY,
    region            text NOT NULL,
    title             text NOT NULL,
    source_type       text NOT NULL,
    language_codes    text[] NOT NULL,
    language_note     text,
    date_text         text,
    findspot          text,
    citation          text NOT NULL,
    citation_original text,
    extra_citations   jsonb NOT NULL DEFAULT '{}'::jsonb,
    translation_source text,
    notes             text,
    source_path       text NOT NULL,
    content_hash      text NOT NULL,
    ingested_at       timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id       text PRIMARY KEY,
    doc_id         text NOT NULL REFERENCES documents(doc_id) ON DELETE CASCADE,

    -- Links the original-language chunks of a source to its translation
    -- chunks. Document-level, not passage-level: the two sides do not
    -- necessarily split into the same number of pieces, so per-passage
    -- alignment is not claimed here.
    parallel_group text NOT NULL,

    role           text NOT NULL CHECK (role IN ('original', 'translation')),
    seq            integer NOT NULL,

    -- lang = the language the chunk text is ACTUALLY in (script-detected).
    -- declared_lang = what the record claims the source language is.
    -- These differ when e.g. a Middle Persian inscription is stored as an
    -- English rendering — the difference is the whole point of text_fidelity.
    lang           text NOT NULL,
    declared_lang  text,

    text           text NOT NULL,
    char_start     integer NOT NULL,
    char_end       integer NOT NULL,
    source_field   text NOT NULL,

    -- How faithful this text is to the actual primary source. Anything other
    -- than verbatim_original / transliteration must be EXCLUDED from the
    -- Part 5 cross-lingual retrieval test or the result is meaningless.
    text_fidelity  text NOT NULL CHECK (text_fidelity IN (
        'verbatim_original',   -- original-script primary source text
        'partial_verbatim',    -- source's own wording, but abridged/elided
        'transliteration',     -- romanised original, still the source wording
        'paraphrase',          -- summarised, not the source's own words
        'english_rendering',   -- English standing in for a non-English original
        'object_description',  -- catalogue/find description, no text-bearing source
        'translation',         -- a genuine translation of the original
        'pointer'              -- a reference to text held elsewhere, not text itself
    )),
    is_pointer     boolean NOT NULL DEFAULT false,
    eligible_for_retrieval boolean NOT NULL DEFAULT true,

    -- denormalised provenance
    region         text NOT NULL,
    source_type    text NOT NULL,
    citation       text NOT NULL,
    date_text      text,

    char_count     integer NOT NULL,
    token_estimate integer NOT NULL,

    -- Embedding + its provenance. Populated in Part 4; declared here so a fresh
    -- database has the same shape as a migrated one, and so the upsert in db.py
    -- can always reference these columns.
    embedding       vector(1024),
    embedding_model text,
    embedding_dim   integer,
    embedded_at     timestamptz,
    CONSTRAINT chunks_embedding_provenance CHECK (
        (embedding IS NULL AND embedding_model IS NULL)
        OR (embedding IS NOT NULL AND embedding_model IS NOT NULL)
    ),

    created_at     timestamptz NOT NULL DEFAULT now(),

    UNIQUE (doc_id, role, seq)
);

CREATE INDEX IF NOT EXISTS chunks_doc_id_idx         ON chunks (doc_id);
CREATE INDEX IF NOT EXISTS chunks_region_idx         ON chunks (region);
CREATE INDEX IF NOT EXISTS chunks_lang_idx           ON chunks (lang);
CREATE INDEX IF NOT EXISTS chunks_role_idx           ON chunks (role);
CREATE INDEX IF NOT EXISTS chunks_fidelity_idx       ON chunks (text_fidelity);
CREATE INDEX IF NOT EXISTS chunks_parallel_group_idx ON chunks (parallel_group);
CREATE INDEX IF NOT EXISTS chunks_eligible_idx       ON chunks (eligible_for_retrieval);

-- Vector index is deliberately NOT created here: HNSW should be built in Part 4
-- once embeddings exist, and once the distance operator class is settled.
