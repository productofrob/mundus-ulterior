-- Mundus Ulterior — Phase 1 Part 7: grounded answer assembly.
--
-- Two things live here.
--
-- 1. `citable_passages` — the single surface Part 7 reads evidence from.
--    It is built ON TOP OF `retrievable_chunks`, not on `chunks`, and that is
--    the whole point: Part 3 held back two records as `pointer` (editorial
--    placeholders standing in for text), Part 4 made the retrieval view exclude
--    them, and an answer layer that queried `chunks` directly would quietly undo
--    both. Everything Part 7 can cite is, by construction, a chunk that was
--    eligible for retrieval AND carries a vector.
--
--    What it adds is metadata the answer needs and the retrieval view has no
--    reason to carry: `seq` (so original and translation chunks can be paired in
--    document order by answer/align.py), and the document-level `title`,
--    `translation_source` and `citation_original`. A published translation must
--    be attributed to its translator, and that attribution lives on `documents`.
--
--    `embedding` is deliberately NOT selected. It is 1024 doubles per row and no
--    consumer of this view wants it; search.py reads `retrievable_chunks` for
--    that and always will.
--
-- 2. `answers` + `answer_citations` — what was answered, from what, and whether
--    it verified. An answer that is not stored cannot be re-checked, and Part 8
--    exists to re-check answers. The citation table records one row per marker
--    with the exact character span the passage occupies in its source file, so
--    "every claim traces to a chunk, and every chunk traces to characters on
--    disk" is a query rather than an aspiration.
--
-- Idempotent: safe to re-run.

-- --------------------------------------------------------------------------
-- The evidence surface
-- --------------------------------------------------------------------------

CREATE OR REPLACE VIEW citable_passages AS
SELECT r.chunk_id,
       r.doc_id,
       r.parallel_group,
       r.role,
       r.lang,
       r.declared_lang,
       r.text,
       r.text_fidelity,
       r.region,
       r.source_type,
       r.citation,
       r.date_text,
       r.source_field,
       r.char_start,
       r.char_end,
       c.seq,
       d.title,
       d.translation_source,
       d.citation_original,
       d.language_note,
       -- D1. The seed record's content hash, so an answer can record the corpus
       -- version it was made against.
       --
       -- THIS COLUMN MUST BE DEFINED HERE AND NOT IN A MIGRATION. `apply_schema`
       -- re-applies this file on EVERY run of answer/run_answer.py, and
       -- CREATE OR REPLACE VIEW is authoritative: a migration that adds a
       -- column to this view is undone the next time anyone answers a
       -- question. scripts/schema-d1.sql tried exactly that on 2026-08-21 and
       -- the next run died with `cannot drop columns from view`.
       --
       -- It died loudly only because the migration ADDED a column. Had it
       -- removed one, this file would have silently put it back and nothing
       -- would have reported it. Any future change to this view belongs here.
       d.content_hash
FROM retrievable_chunks r
JOIN chunks    c ON c.chunk_id = r.chunk_id
JOIN documents d ON d.doc_id   = r.doc_id;

-- --------------------------------------------------------------------------
-- Stored answers
-- --------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS answers (
    -- sha256 over (question, answer model, prompt version, ordered chunk ids).
    -- Deterministic on purpose: re-asking the same question of the same evidence
    -- with the same prompt updates one row instead of accumulating near
    -- duplicates, and a changed prompt version writes a new row rather than
    -- overwriting the evidence the old prompt produced. That is the Part 6
    -- lesson — a v2 back-prompt silently destroyed v1's rows because the version
    -- was stored but left out of the key.
    answer_id             text        PRIMARY KEY,

    question              text        NOT NULL,
    question_lang         text,
    answer_text           text        NOT NULL,

    answer_model          text        NOT NULL,
    answer_prompt_version text        NOT NULL,
    embedding_model       text,
    retrieval_k           integer     NOT NULL,

    -- Did the answer pass every grounding check? The detail is in `grounding`;
    -- this column exists so the failures can be found without parsing jsonb.
    grounded              boolean     NOT NULL,
    grounding             jsonb       NOT NULL DEFAULT '{}'::jsonb,

    notes                 text,

    -- D1. Present here so a FRESH database gets them, and repeated as ALTERs in
    -- scripts/schema-d1.sql because CREATE TABLE IF NOT EXISTS does nothing to
    -- an existing table. Both are idempotent and both are needed; neither alone
    -- covers both cases.
    corpus_digest_algorithm text,
    seed_corpus_digest      text,
    cited_record_hashes     jsonb NOT NULL DEFAULT '{}'::jsonb,

    created_at            timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS answer_citations (
    answer_id       text    NOT NULL REFERENCES answers (answer_id) ON DELETE CASCADE,
    marker          text    NOT NULL,          -- 'S1', 'S2', ...
    chunk_id        text    NOT NULL REFERENCES chunks (chunk_id) ON DELETE CASCADE,
    doc_id          text    NOT NULL,
    similarity      double precision,

    -- Which English the reader was shown for this passage, and on what evidence
    -- it was paired with the passage. 'published' means a human translation
    -- aligned to this passage; 'published_document' means a human translation of
    -- the document that could not be aligned to this passage; 'machine' means
    -- Part 6 output; 'none' means no English may be shown at all.
    english_kind    text    NOT NULL CHECK (english_kind IN (
        'source', 'published', 'published_document', 'machine', 'none'
    )),
    english_ground  text,

    confidence_band    text,
    confidence_profile text,
    flags              text[] NOT NULL DEFAULT '{}',

    -- Did the answer actually cite this passage, and did it quote it verbatim?
    -- Retrieved-but-uncited rows are kept: what the model was shown and did not
    -- use is evidence about the retrieval, and deleting it makes every answer
    -- look perfectly targeted in hindsight.
    cited           boolean NOT NULL DEFAULT false,
    quoted          boolean NOT NULL DEFAULT false,

    -- The chunk's span in its source file. char_start + the offset of a quote
    -- within the chunk gives the absolute characters on disk.
    source_field    text    NOT NULL,
    char_start      integer NOT NULL,
    char_end        integer NOT NULL,

    PRIMARY KEY (answer_id, marker)
);

-- Same lockstep rule as chunks_embedding_provenance and
-- chunk_translations_back_provenance: a machine translation shown to a reader
-- without the band that qualifies it is the failure mode Part 6 was built to
-- prevent, so the database refuses to record one.
ALTER TABLE answer_citations DROP CONSTRAINT IF EXISTS answer_citations_machine_band;
ALTER TABLE answer_citations ADD CONSTRAINT answer_citations_machine_band
    CHECK (english_kind <> 'machine' OR confidence_band IS NOT NULL);

-- A published translation must say what pairing it rests on. align.py can report
-- 'section', 'index', 'none' or 'document', and a chrf_ref or a quotation read
-- without that ground is read as better-evidenced than it is.
ALTER TABLE answer_citations DROP CONSTRAINT IF EXISTS answer_citations_published_ground;
ALTER TABLE answer_citations ADD CONSTRAINT answer_citations_published_ground
    CHECK (
        english_kind NOT IN ('published', 'published_document')
        OR english_ground IS NOT NULL
    );

CREATE INDEX IF NOT EXISTS answer_citations_chunk_idx  ON answer_citations (chunk_id);
CREATE INDEX IF NOT EXISTS answer_citations_answer_idx ON answer_citations (answer_id);
CREATE INDEX IF NOT EXISTS answers_grounded_idx        ON answers (grounded);

-- Every citation in every answer, resolved to the characters it stands on.
-- This is the Part 7 claim, expressed as something you can SELECT.
CREATE OR REPLACE VIEW answer_provenance AS
SELECT a.answer_id,
       a.question,
       a.grounded,
       a.answer_model,
       a.answer_prompt_version,
       a.created_at,
       ac.marker,
       ac.chunk_id,
       ac.doc_id,
       ac.cited,
       ac.quoted,
       ac.english_kind,
       ac.english_ground,
       ac.confidence_band,
       ac.flags,
       ac.source_field,
       ac.char_start,
       ac.char_end,
       d.source_path,
       d.citation,
       d.translation_source
FROM answers a
JOIN answer_citations ac ON ac.answer_id = a.answer_id
JOIN documents d        ON d.doc_id      = ac.doc_id;

-- The operator's question: which answers cited a machine translation that the
-- confidence check flagged? Empty is the expected state; a non-empty result is
-- a citation that should not have been made.
CREATE OR REPLACE VIEW answers_citing_flagged_translations AS
SELECT a.answer_id, a.question, a.created_at,
       ac.marker, ac.chunk_id, ac.confidence_band, ac.flags
FROM answers a
JOIN answer_citations ac ON ac.answer_id = a.answer_id
WHERE ac.cited
  AND ac.english_kind = 'machine'
  AND cardinality(ac.flags) > 0;
