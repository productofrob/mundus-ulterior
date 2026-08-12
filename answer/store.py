"""Reading chunks for translation, and writing translations back.

Kept separate from translate.py and confidence.py so both of those stay free of
the database and can be tested offline — which is the only kind of test this
sandbox can run, and, per the Part 4 lesson, the only kind that cannot catch a
type-inference error. Every parameter that can be NULL carries an explicit cast.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DSN = "postgresql://mundus:mundus@localhost:5432/mundus"
SCHEMA_PATH = Path("scripts/schema-part6.sql")


def get_dsn() -> str:
    # APP_DATABASE_URL, not DATABASE_URL — LiteLLM reserves the latter for Prisma.
    return os.environ.get("APP_DATABASE_URL", DEFAULT_DSN)


def text_sha256(text: str) -> str:
    """Must match the SQL in the current_translations view exactly:
    encode(sha256(convert_to(text, 'UTF8')), 'hex')."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def apply_schema(conn, schema_path: Path = SCHEMA_PATH) -> None:
    conn.execute(schema_path.read_text(encoding="utf-8"))
    conn.commit()


@dataclass
class ChunkRow:
    chunk_id: str
    doc_id: str
    role: str
    seq: int
    lang: str
    text: str
    citation: str
    region: str
    source_type: str
    text_fidelity: str

    def preview(self, n: int = 60) -> str:
        return self.text[:n].replace("\n", " ")


CHUNK_COLUMNS = (
    "chunk_id, doc_id, role, seq, lang, text, citation, region, source_type, "
    "text_fidelity"
)

SELECT_BY_DOC = f"""
SELECT {CHUNK_COLUMNS}
FROM chunks
WHERE doc_id = %(doc_id)s
  AND role = %(role)s
  AND eligible_for_retrieval
ORDER BY seq;
"""

SELECT_TRANSLATABLE = f"""
SELECT {CHUNK_COLUMNS}
FROM chunks
WHERE eligible_for_retrieval
  AND lang <> 'en'
  AND role = 'original'
  AND (%(doc_ids)s::text[] IS NULL OR doc_id = ANY(%(doc_ids)s::text[]))
  AND (%(langs)s::text[]   IS NULL OR lang   = ANY(%(langs)s::text[]))
ORDER BY lang, doc_id, seq
{{limit_clause}};
"""

UPSERT_TRANSLATION = """
INSERT INTO chunk_translations (
    chunk_id, target_lang, translation_model, prompt_version,
    translated_text, source_text_sha256,
    back_translated_text, back_translation_model, back_prompt_version,
    chrf_back, cos_back, chrf_ref, cos_ref, chrf_echo,
    confidence_band, confidence_profile, flags, scoring_embedding_model, notes
) VALUES (
    %(chunk_id)s, %(target_lang)s, %(translation_model)s, %(prompt_version)s,
    %(translated_text)s, %(source_text_sha256)s,
    %(back_translated_text)s, %(back_translation_model)s, %(back_prompt_version)s,
    %(chrf_back)s, %(cos_back)s, %(chrf_ref)s, %(cos_ref)s, %(chrf_echo)s,
    %(confidence_band)s, %(confidence_profile)s, %(flags)s::text[],
    %(scoring_embedding_model)s, %(notes)s
)
ON CONFLICT (chunk_id, target_lang, translation_model, prompt_version,
             back_prompt_version)
DO UPDATE SET
    translated_text = EXCLUDED.translated_text,
    source_text_sha256 = EXCLUDED.source_text_sha256,
    back_translated_text = EXCLUDED.back_translated_text,
    back_translation_model = EXCLUDED.back_translation_model,
    back_prompt_version = EXCLUDED.back_prompt_version,
    chrf_back = EXCLUDED.chrf_back,
    cos_back = EXCLUDED.cos_back,
    chrf_ref = EXCLUDED.chrf_ref,
    cos_ref = EXCLUDED.cos_ref,
    chrf_echo = EXCLUDED.chrf_echo,
    confidence_band = EXCLUDED.confidence_band,
    confidence_profile = EXCLUDED.confidence_profile,
    flags = EXCLUDED.flags,
    scoring_embedding_model = EXCLUDED.scoring_embedding_model,
    notes = EXCLUDED.notes,
    created_at = now();
"""

TRANSLATION_STATS = """
SELECT
    (SELECT count(*) FROM chunk_translations)                        AS rows,
    (SELECT count(*) FROM current_translations)                      AS current,
    (SELECT count(*) FROM stale_translations)                        AS stale,
    (SELECT count(*) FROM chunks
      WHERE eligible_for_retrieval AND lang <> 'en' AND role = 'original') AS translatable;
"""


def fetch_by_doc(conn, doc_id: str, role: str = "original") -> list[ChunkRow]:
    with conn.cursor() as cur:
        cur.execute(SELECT_BY_DOC, {"doc_id": doc_id, "role": role})
        return [ChunkRow(*row) for row in cur.fetchall()]


def fetch_translatable(
    conn,
    doc_ids: list[str] | None = None,
    langs: list[str] | None = None,
    limit: int | None = None,
) -> list[ChunkRow]:
    sql = SELECT_TRANSLATABLE.format(
        limit_clause=f"LIMIT {int(limit)}" if limit else ""
    )
    with conn.cursor() as cur:
        cur.execute(sql, {"doc_ids": doc_ids, "langs": langs})
        return [ChunkRow(*row) for row in cur.fetchall()]


def write_translation(conn, params: dict) -> None:
    """Insert or replace one translation row. `params` keys must match
    UPSERT_TRANSLATION; missing optional keys default to None."""
    full = {
        "back_translated_text": None,
        "back_translation_model": None,
        # 'none', not NULL: this column is in the primary key now, so it cannot
        # be null. See the migration note in scripts/schema-part6.sql.
        "back_prompt_version": "none",
        "chrf_back": None,
        "cos_back": None,
        "chrf_ref": None,
        "cos_ref": None,
        "chrf_echo": None,
        "confidence_band": "unscored",
        "confidence_profile": None,
        "flags": [],
        "scoring_embedding_model": None,
        "notes": None,
        "target_lang": "en",
    }
    full.update(params)
    with conn.cursor() as cur:
        cur.execute(UPSERT_TRANSLATION, full)
    conn.commit()


def stats(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute(TRANSLATION_STATS)
        rows, current, stale, translatable = cur.fetchone()
        cur.execute(
            "SELECT confidence_band, count(*) FROM current_translations "
            "GROUP BY confidence_band ORDER BY confidence_band;"
        )
        by_band = dict(cur.fetchall())
    return {
        "rows": rows,
        "current": current,
        "stale": stale,
        "translatable_chunks": translatable,
        "by_band": by_band,
    }
