"""Part 7 database layer: read the evidence, write the answer.

Kept separate from evidence.py and cite.py for the same reason store.py is kept
separate from confidence.py — those modules are pure and can be tested offline,
and this one cannot be tested here at all. No Postgres exists in the dev sandbox,
so every statement below is *parsed* and never *planned*. Part 4 lost an
afternoon to that distinction (`AmbiguousParameter` on an uncast NULL parameter,
which parses perfectly), so every nullable parameter carries an explicit cast and
`test_answer.py` re-runs the Part 4/6 regression guard over this file's SQL.

The reading surface is `citable_passages`, which is built on `retrievable_chunks`
and therefore inherits its guarantee: a chunk the Part 3 fidelity classifier held
back cannot be selected here, so an answer cannot cite an editorial placeholder.
Nothing in this module queries `chunks` directly for evidence.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from answer.evidence import ChunkRecord, TranslationRecord

DEFAULT_DSN = "postgresql://mundus:mundus@localhost:5432/mundus"
SCHEMA_PATH = Path("scripts/schema-part7.sql")


def get_dsn() -> str:
    # APP_DATABASE_URL, not DATABASE_URL — LiteLLM reserves the latter for Prisma.
    return os.environ.get("APP_DATABASE_URL", DEFAULT_DSN)


def apply_schema(conn, schema_path: Path = SCHEMA_PATH) -> None:
    conn.execute(schema_path.read_text(encoding="utf-8"))
    conn.commit()


PASSAGE_COLUMNS = (
    "chunk_id, doc_id, role, seq, lang, text, citation, region, source_type, "
    "text_fidelity, source_field, char_start, char_end, date_text, title, "
    "translation_source, citation_original, language_note, parallel_group"
)


def _record(row) -> ChunkRecord:
    (
        chunk_id, doc_id, role, seq, lang, text, citation, region, source_type,
        text_fidelity, source_field, char_start, char_end, date_text, title,
        translation_source, citation_original, language_note, parallel_group,
    ) = row
    return ChunkRecord(
        chunk_id=chunk_id, doc_id=doc_id, role=role, seq=seq, lang=lang,
        text=text, citation=citation, region=region, source_type=source_type,
        text_fidelity=text_fidelity, source_field=source_field,
        char_start=char_start, char_end=char_end, date_text=date_text,
        title=title, translation_source=translation_source,
        citation_original=citation_original, language_note=language_note,
        parallel_group=parallel_group,
    )


# Hydration, not retrieval. The vector search itself stays in retrieve/search.py
# and runs against `retrievable_chunks`, which is where the HNSW index lives —
# an ORDER BY over a view that reaches the embedding through a subquery would
# produce identical results with the index bypassed, and there would be no error
# to tell you (the Part 4 note on `<=>` and operator classes, one layer up).
#
# So: search there, then fetch the citation metadata for the winning chunk ids
# here. Two queries, both able to use their indexes, and one definition of the
# distance operator in the codebase instead of two that can drift.
SELECT_BY_CHUNK_IDS = f"""
SELECT {PASSAGE_COLUMNS}
FROM citable_passages
WHERE chunk_id = ANY(%(chunk_ids)s::text[]);
"""

SELECT_DOC_PASSAGES = f"""
SELECT {PASSAGE_COLUMNS}
FROM citable_passages
WHERE doc_id = ANY(%(doc_ids)s::text[])
ORDER BY doc_id, role, seq;
"""

# One row per (chunk, prompt pair). A chunk can hold several — Part 6 widened the
# key to include back_prompt_version precisely so a v2 back prompt would stop
# overwriting v1's evidence. Newest first; the caller takes the first per chunk.
SELECT_CURRENT_TRANSLATIONS = """
SELECT chunk_id, translated_text, confidence_band, confidence_profile, flags,
       chrf_back, cos_back, chrf_ref, cos_ref,
       translation_model, prompt_version, back_prompt_version
FROM current_translations
WHERE target_lang = %(target_lang)s
  AND chunk_id = ANY(%(chunk_ids)s::text[])
ORDER BY chunk_id, created_at DESC;
"""

UPSERT_ANSWER = """
INSERT INTO answers (
    answer_id, question, question_lang, answer_text,
    answer_model, answer_prompt_version, embedding_model, retrieval_k,
    grounded, grounding, notes
) VALUES (
    %(answer_id)s, %(question)s, %(question_lang)s, %(answer_text)s,
    %(answer_model)s, %(answer_prompt_version)s, %(embedding_model)s,
    %(retrieval_k)s, %(grounded)s, %(grounding)s::jsonb, %(notes)s
)
ON CONFLICT (answer_id)
DO UPDATE SET
    answer_text = EXCLUDED.answer_text,
    answer_model = EXCLUDED.answer_model,
    answer_prompt_version = EXCLUDED.answer_prompt_version,
    embedding_model = EXCLUDED.embedding_model,
    retrieval_k = EXCLUDED.retrieval_k,
    grounded = EXCLUDED.grounded,
    grounding = EXCLUDED.grounding,
    notes = EXCLUDED.notes,
    created_at = now();
"""

UPSERT_CITATION = """
INSERT INTO answer_citations (
    answer_id, marker, chunk_id, doc_id, similarity,
    english_kind, english_ground, confidence_band, confidence_profile, flags,
    cited, quoted, source_field, char_start, char_end
) VALUES (
    %(answer_id)s, %(marker)s, %(chunk_id)s, %(doc_id)s, %(similarity)s,
    %(english_kind)s, %(english_ground)s, %(confidence_band)s,
    %(confidence_profile)s, %(flags)s::text[],
    %(cited)s, %(quoted)s, %(source_field)s, %(char_start)s, %(char_end)s
)
ON CONFLICT (answer_id, marker)
DO UPDATE SET
    chunk_id = EXCLUDED.chunk_id,
    doc_id = EXCLUDED.doc_id,
    similarity = EXCLUDED.similarity,
    english_kind = EXCLUDED.english_kind,
    english_ground = EXCLUDED.english_ground,
    confidence_band = EXCLUDED.confidence_band,
    confidence_profile = EXCLUDED.confidence_profile,
    flags = EXCLUDED.flags,
    cited = EXCLUDED.cited,
    quoted = EXCLUDED.quoted,
    source_field = EXCLUDED.source_field,
    char_start = EXCLUDED.char_start,
    char_end = EXCLUDED.char_end;
"""

DELETE_STALE_CITATIONS = """
DELETE FROM answer_citations
WHERE answer_id = %(answer_id)s
  AND NOT (marker = ANY(%(markers)s::text[]));
"""

ANSWER_STATS = """
SELECT
    (SELECT count(*) FROM answers)                                  AS answers,
    (SELECT count(*) FROM answers WHERE grounded)                   AS grounded,
    (SELECT count(*) FROM answer_citations WHERE cited)             AS citations_used,
    (SELECT count(*) FROM answer_citations WHERE cited AND quoted)  AS citations_quoted,
    (SELECT count(*) FROM answers_citing_flagged_translations)      AS flagged_citations,
    (SELECT count(*) FROM citable_passages)                         AS citable_passages;
"""


# --------------------------------------------------------------------------
# Reads
# --------------------------------------------------------------------------

def search_passages(
    conn,
    query_vector: list[float],
    k: int = 12,
    langs: list[str] | None = None,
    regions: list[str] | None = None,
    roles: list[str] | None = None,
) -> list[tuple[ChunkRecord, float]]:
    """Nearest passages, as (record, cosine similarity), in rank order.

    The ranking is done by retrieve.search over `retrievable_chunks`; this adds
    the document metadata a citation needs. Hits whose chunk is not in
    `citable_passages` are dropped rather than cited without provenance — the two
    views cannot currently disagree, but a citation with no title or translator is
    not a citation, so the code says so instead of assuming.
    """
    from retrieve.search import search

    hits = search(conn, query_vector, k=k, langs=langs, regions=regions, roles=roles)
    if not hits:
        return []

    with conn.cursor() as cur:
        cur.execute(SELECT_BY_CHUNK_IDS, {"chunk_ids": [h.chunk_id for h in hits]})
        by_id = {row[0]: _record(row) for row in cur.fetchall()}

    return [
        (by_id[hit.chunk_id], hit.similarity)
        for hit in hits
        if hit.chunk_id in by_id
    ]


def fetch_doc_passages(conn, doc_ids: list[str]) -> dict[str, list[ChunkRecord]]:
    """Every citable chunk of the named documents, grouped by doc_id and ordered
    by (role, seq) — the order answer.align.pair_chunks expects."""
    if not doc_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(SELECT_DOC_PASSAGES, {"doc_ids": doc_ids})
        rows = cur.fetchall()
    out: dict[str, list[ChunkRecord]] = {}
    for row in rows:
        record = _record(row)
        out.setdefault(record.doc_id, []).append(record)
    return out


def fetch_current_translations(
    conn, chunk_ids: list[str], target_lang: str = "en"
) -> dict[str, TranslationRecord]:
    """The newest current translation per chunk.

    'Current' is the view's word, not this function's: `current_translations`
    serves only rows whose stored source hash still matches the chunk text, so a
    translation of superseded text cannot be returned here and therefore cannot
    be cited.
    """
    if not chunk_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            SELECT_CURRENT_TRANSLATIONS,
            {"chunk_ids": chunk_ids, "target_lang": target_lang},
        )
        rows = cur.fetchall()

    out: dict[str, TranslationRecord] = {}
    for row in rows:
        (
            chunk_id, translated_text, band, profile, flags, chrf_back, cos_back,
            chrf_ref, cos_ref, model, prompt_version, back_prompt_version,
        ) = row
        if chunk_id in out:        # ORDER BY created_at DESC — first wins
            continue
        out[chunk_id] = TranslationRecord(
            chunk_id=chunk_id,
            translated_text=translated_text,
            confidence_band=band,
            confidence_profile=profile,
            flags=list(flags or []),
            chrf_back=chrf_back,
            cos_back=cos_back,
            chrf_ref=chrf_ref,
            cos_ref=cos_ref,
            translation_model=model,
            prompt_version=prompt_version,
            back_prompt_version=back_prompt_version,
        )
    return out


# --------------------------------------------------------------------------
# Writes
# --------------------------------------------------------------------------

def answer_id(
    question: str, model: str, prompt_version: str, chunk_ids: list[str]
) -> str:
    """Deterministic id over everything that makes the answer what it is.

    Same argument as chunk_translations' primary key. An answer is the output of
    (question, model, prompt, evidence); if any of the four changes, the row is
    about something else and must not overwrite its predecessor. Re-asking the
    identical question of identical evidence updates in place, which is what makes
    a re-run cheap to compare.
    """
    payload = "\x1f".join([question, model, prompt_version, *chunk_ids])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def write_answer(conn, record: dict, citations: list[dict]) -> str:
    """Store one answer and its citation rows. Returns the answer_id."""
    aid = record["answer_id"]
    grounding = record.get("grounding")
    params = dict(record)
    params["grounding"] = json.dumps(
        grounding if grounding is not None else {}, ensure_ascii=False
    )
    params.setdefault("question_lang", None)
    params.setdefault("embedding_model", None)
    params.setdefault("notes", None)

    with conn.cursor() as cur:
        cur.execute(UPSERT_ANSWER, params)
        for citation in citations:
            row = dict(citation)
            row["answer_id"] = aid
            row.setdefault("similarity", None)
            row.setdefault("english_ground", None)
            row.setdefault("confidence_band", None)
            row.setdefault("confidence_profile", None)
            row.setdefault("flags", [])
            row.setdefault("cited", False)
            row.setdefault("quoted", False)
            cur.execute(UPSERT_CITATION, row)
        # A re-run with fewer sources must not leave the old ones behind, or the
        # stored evidence set stops matching the answer that stands on it.
        cur.execute(
            DELETE_STALE_CITATIONS,
            {"answer_id": aid, "markers": [c["marker"] for c in citations]},
        )
    conn.commit()
    return aid


def stats(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute(ANSWER_STATS)
        (
            answers, grounded, citations_used, citations_quoted,
            flagged, citable,
        ) = cur.fetchone()
        cur.execute(
            "SELECT english_kind, count(*) FROM answer_citations "
            "WHERE cited GROUP BY english_kind ORDER BY english_kind;"
        )
        by_kind = dict(cur.fetchall())
    return {
        "answers": answers,
        "grounded": grounded,
        "ungrounded": answers - grounded,
        "citations_used": citations_used,
        "citations_quoted": citations_quoted,
        "flagged_translation_citations": flagged,
        "citable_passages": citable,
        "cited_by_english_kind": by_kind,
    }
