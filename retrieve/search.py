"""Vector search over the chunk table.

Cosine distance (`<=>`) throughout, matching the HNSW operator class in
scripts/schema-part4.sql. Using a different operator silently bypasses the
index — correct results, wrong performance profile, and no error to tell you.

Only `retrievable_chunks` is queried: eligible chunks with a vector. Chunks the
Part 3 classifier held back are unreachable from here by construction, so an
answer in Part 7 cannot cite an editorial placeholder.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_DSN = "postgresql://mundus:mundus@localhost:5432/mundus"


@dataclass
class Hit:
    chunk_id: str
    doc_id: str
    lang: str
    role: str
    text_fidelity: str
    region: str
    citation: str
    text: str
    distance: float

    @property
    def similarity(self) -> float:
        return 1.0 - self.distance

    def preview(self, n: int = 80) -> str:
        return self.text[:n].replace("\n", " ")


def get_dsn() -> str:
    return os.environ.get("APP_DATABASE_URL", DEFAULT_DSN)


# Every filter parameter carries an explicit ::text[] cast, and the query vector
# an explicit ::vector. Without them Postgres cannot infer a type for a NULL
# parameter that appears as both `$n IS NULL` and `ANY($n)`, and raises
# AmbiguousParameter at execution time — not at parse time, so a syntax check
# will not find it.
SEARCH_SQL = """
SELECT chunk_id, doc_id, lang, role, text_fidelity, region, citation, text,
       embedding <=> %(query)s::vector AS distance
FROM retrievable_chunks
WHERE (%(langs)s::text[]   IS NULL OR lang   = ANY(%(langs)s::text[]))
  AND (%(regions)s::text[] IS NULL OR region = ANY(%(regions)s::text[]))
  AND (%(roles)s::text[]   IS NULL OR role   = ANY(%(roles)s::text[]))
ORDER BY embedding <=> %(query)s::vector
LIMIT %(k)s;
"""


def search(
    conn,
    query_vector: list[float],
    k: int = 10,
    langs: list[str] | None = None,
    regions: list[str] | None = None,
    roles: list[str] | None = None,
) -> list[Hit]:
    with conn.cursor() as cur:
        cur.execute(
            SEARCH_SQL,
            {
                "query": str(query_vector),
                "k": k,
                "langs": langs,
                "regions": regions,
                "roles": roles,
            },
        )
        return [Hit(*row[:8], distance=float(row[8])) for row in cur.fetchall()]


def search_text(conn, query: str, **kwargs) -> list[Hit]:
    """Embed a query string and search. Uses input_type='query'."""
    from ingest.embed import embed_query

    return search(conn, embed_query(query), **kwargs)
