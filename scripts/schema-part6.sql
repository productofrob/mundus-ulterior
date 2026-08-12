-- Mundus Ulterior — Phase 1 Part 6: machine translations + confidence scores.
--
-- Why store translations at all: Part 7 assembles answers with inline citations
-- and must not re-translate a passage every time it is cited — both because it
-- costs two model calls per chunk and because an answer that quotes a slightly
-- different English each time is not auditable.
--
-- Why the provenance columns: the same argument as Part 4's embedding_model.
-- A translation is the output of (model, prompt) applied to a specific text. If
-- any of those three changes, the cached row is about something else. So all
-- three are recorded, the first two in the primary key and the third as a hash
-- of the source text, and a stale row is visible rather than silently served.
--
-- Idempotent: safe to re-run.

CREATE TABLE IF NOT EXISTS chunk_translations (
    chunk_id                text        NOT NULL
        REFERENCES chunks (chunk_id) ON DELETE CASCADE,
    target_lang             text        NOT NULL,
    translation_model       text        NOT NULL,
    prompt_version          text        NOT NULL,

    translated_text         text        NOT NULL,
    -- The source text this translation was made FROM, as a hash. Part 3's
    -- upsert rewrites chunks.text whenever a record is corrected on disk; that
    -- must invalidate the translation, exactly as it already nulls the vector.
    source_text_sha256      text        NOT NULL,

    back_translated_text    text,
    back_translation_model  text,
    -- NOT NULL with a sentinel because this is part of the primary key, and PK
    -- columns cannot be null. 'none' means no back-translation was attempted.
    back_prompt_version     text        NOT NULL DEFAULT 'none',

    chrf_back               double precision,
    cos_back                double precision,
    chrf_ref                double precision,
    cos_ref                 double precision,
    chrf_echo               double precision,

    confidence_band         text        NOT NULL DEFAULT 'unscored',
    confidence_profile      text,
    flags                   text[]      NOT NULL DEFAULT '{}',
    scoring_embedding_model text,

    notes                   text,
    created_at              timestamptz NOT NULL DEFAULT now(),

    PRIMARY KEY (chunk_id, target_lang, translation_model, prompt_version,
                 back_prompt_version)
);

-- Migration for tables created before 2026-08-10, when the key did not include
-- back_prompt_version.
--
-- Why this changed: the first live run bumped the back prompt from v1 to v2 to
-- fix a script bug, re-ran one case, and the v2 row *overwrote* the v1 row —
-- row count stayed at 9 while a band flipped from medium to high. The whole
-- argument for storing a prompt version is that output from two prompts is not
-- comparable; leaving one of the two versions out of the key meant the newer
-- prompt silently destroyed the evidence the older one produced. The version
-- column was right; the key was incomplete.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chunk_translations_pkey'
          AND pg_get_constraintdef(oid) NOT LIKE '%back_prompt_version%'
    ) THEN
        UPDATE chunk_translations
           SET back_prompt_version = 'none'
         WHERE back_prompt_version IS NULL;
        ALTER TABLE chunk_translations
            ALTER COLUMN back_prompt_version SET DEFAULT 'none';
        ALTER TABLE chunk_translations
            ALTER COLUMN back_prompt_version SET NOT NULL;
        ALTER TABLE chunk_translations DROP CONSTRAINT chunk_translations_pkey;
        ALTER TABLE chunk_translations ADD PRIMARY KEY (
            chunk_id, target_lang, translation_model, prompt_version,
            back_prompt_version
        );
        RAISE NOTICE 'chunk_translations: primary key widened to include back_prompt_version';
    END IF;
END $$;

ALTER TABLE chunk_translations DROP CONSTRAINT IF EXISTS chunk_translations_band_check;
ALTER TABLE chunk_translations ADD CONSTRAINT chunk_translations_band_check
    CHECK (confidence_band IN ('high', 'medium', 'low', 'unscored'));

-- Same lockstep rule as chunks_embedding_provenance: a back-translation with no
-- model label is unusable, and a model label with no back-translation is a lie.
-- Part 4 shipped an upsert that violated its own constraint by clearing one
-- column of a group; keeping the groups small and explicit is the fix.
ALTER TABLE chunk_translations DROP CONSTRAINT IF EXISTS chunk_translations_back_provenance;
ALTER TABLE chunk_translations ADD CONSTRAINT chunk_translations_back_provenance
    CHECK (
        (back_translated_text IS NULL AND back_translation_model IS NULL)
        OR (back_translated_text IS NOT NULL AND back_translation_model IS NOT NULL)
    );

-- A cosine score without the model that produced it cannot be compared with
-- anything, for the same reason a vector cannot.
ALTER TABLE chunk_translations DROP CONSTRAINT IF EXISTS chunk_translations_cos_provenance;
ALTER TABLE chunk_translations ADD CONSTRAINT chunk_translations_cos_provenance
    CHECK (
        (cos_back IS NULL AND cos_ref IS NULL)
        OR scoring_embedding_model IS NOT NULL
    );

CREATE INDEX IF NOT EXISTS chunk_translations_band_idx
    ON chunk_translations (confidence_band);
CREATE INDEX IF NOT EXISTS chunk_translations_chunk_idx
    ON chunk_translations (chunk_id);

-- What Part 7 is allowed to read: translations whose source text has not
-- changed since they were made. A translation of superseded text is worse than
-- no translation, because it still carries a citation.
CREATE OR REPLACE VIEW current_translations AS
SELECT t.*,
       c.doc_id,
       c.lang        AS source_lang,
       c.region,
       c.citation,
       c.text        AS source_text
FROM chunk_translations t
JOIN chunks c ON c.chunk_id = t.chunk_id
WHERE t.source_text_sha256 = encode(sha256(convert_to(c.text, 'UTF8')), 'hex');

-- The complement, for the operator: rows that need re-translating.
CREATE OR REPLACE VIEW stale_translations AS
SELECT t.chunk_id, t.target_lang, t.translation_model, t.prompt_version,
       t.created_at, c.doc_id
FROM chunk_translations t
JOIN chunks c ON c.chunk_id = t.chunk_id
WHERE t.source_text_sha256 <> encode(sha256(convert_to(c.text, 'UTF8')), 'hex');
