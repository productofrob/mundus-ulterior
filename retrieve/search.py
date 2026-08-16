"""Vector search over the chunk table.

Cosine distance (`<=>`) throughout, matching the HNSW operator class in
scripts/schema-part4.sql. Using a different operator silently bypasses the
index — correct results, wrong performance profile, and no error to tell you.

`retrievable_chunks` is the DEFAULT and is what the answer path gets: eligible
chunks with a vector, no distractors. Chunks the Part 3 classifier held back are
unreachable from here by construction, so an answer in Part 7 cannot cite an
editorial placeholder, and a caller that says nothing about views still gets
containment.

The view became a parameter on 2026-08-14, and the reason is worth keeping.
Until then it was hardcoded, while `eval/run_ranking_check.py --with-distractors`
counted `retrievable_chunks_with_distractors` for its header and ranked against
`retrievable_chunks` — one view in the denominator, another in the numerator,
both counts individually correct. The B5 distractor curve was therefore
measurable only while the B4 containment guard was reverted and
`retrievable_chunks` itself held the padding; restoring the guard silently ended
the ability to measure that rung, and nothing said so. `schema-b4-distractors.sql`
had described the distractor view as *"read by eval/run_ranking_check.py
--with-distractors and by nothing else, ever"* — a design that was never wired.
"""

from __future__ import annotations

import json
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


# The only view names that may reach the SQL below. A view name cannot be a
# bound parameter — it is interpolated — so it is checked against this set
# rather than trusted. It is a constant at every call site today, and it stops
# being one the moment somebody adds a flag.
DEFAULT_VIEW = "retrievable_chunks"
SEARCHABLE_VIEWS = frozenset({
    DEFAULT_VIEW,
    # The only surface from which a distractor is visible, per
    # scripts/schema-b4-distractors.sql. Read by
    # eval/run_ranking_check.py --with-distractors, and now actually read.
    "retrievable_chunks_with_distractors",
})

# Every filter parameter carries an explicit ::text[] cast, and the query vector
# an explicit ::vector. Without them Postgres cannot infer a type for a NULL
# parameter that appears as both `$n IS NULL` and `ANY($n)`, and raises
# AmbiguousParameter at execution time — not at parse time, so a syntax check
# will not find it.
_SEARCH_SQL_TEMPLATE = """
SELECT chunk_id, doc_id, lang, role, text_fidelity, region, citation, text,
       embedding <=> %(query)s::vector AS distance
FROM {view}
WHERE (%(langs)s::text[]   IS NULL OR lang   = ANY(%(langs)s::text[]))
  AND (%(regions)s::text[] IS NULL OR region = ANY(%(regions)s::text[]))
  AND (%(roles)s::text[]   IS NULL OR role   = ANY(%(roles)s::text[]))
ORDER BY embedding <=> %(query)s::vector
LIMIT %(k)s;
"""


def search_sql(view: str = DEFAULT_VIEW) -> str:
    if view not in SEARCHABLE_VIEWS:
        raise ValueError(
            f"{view!r} is not a searchable view. Known: "
            f"{sorted(SEARCHABLE_VIEWS)}. The name is interpolated into SQL, so "
            f"an unknown one is refused rather than executed."
        )
    return _SEARCH_SQL_TEMPLATE.format(view=view)


# The default-view statement as a module constant, because ingest/test_embed.py
# asserts against it: the cosine operator matches the HNSW index, every nullable
# filter parameter is cast at every use, and the query vector is cast in both
# the SELECT and the ORDER BY.
SEARCH_SQL = search_sql(DEFAULT_VIEW)


def search(
    conn,
    query_vector: list[float],
    k: int = 10,
    langs: list[str] | None = None,
    regions: list[str] | None = None,
    roles: list[str] | None = None,
    view: str = DEFAULT_VIEW,
) -> list[Hit]:
    with conn.cursor() as cur:
        cur.execute(
            search_sql(view),
            {
                "query": str(query_vector),
                "k": k,
                "langs": langs,
                "regions": regions,
                "roles": roles,
            },
        )
        return [Hit(*row[:8], distance=float(row[8])) for row in cur.fetchall()]


def sample_vector(conn, view: str = DEFAULT_VIEW) -> list[float] | None:
    """One embedding already in the view, for probing reachability without spend.

    A caller that wants to know whether it can reach a whole view needs a query
    vector and has not embedded one yet. Borrowing a vector the view already
    holds costs a single row and no API call, and — unlike a synthetic vector —
    it is guaranteed to be the right dimension.
    """
    if view not in SEARCHABLE_VIEWS:
        raise ValueError(f"{view!r} is not a searchable view")
    with conn.cursor() as cur:
        cur.execute(f"SELECT embedding FROM {view} LIMIT 1;")
        row = cur.fetchone()
    if not row or row[0] is None:
        return None
    value = row[0]
    return list(value) if not isinstance(value, str) else json.loads(value)


def search_text(conn, query: str, **kwargs) -> list[Hit]:
    """Embed a query string and search. Uses input_type='query'."""
    from ingest.embed import embed_query

    return search(conn, embed_query(query), **kwargs)
