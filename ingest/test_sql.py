"""Offline checks on the SQL layer — no database required.

These catch the failure mode that would otherwise only show up mid-load: a
named placeholder in an INSERT that has no matching dataclass field, or a
schema column the writer never populates. Both raise at runtime, after the
schema has already been applied.

Run: python -m ingest.test_sql
"""

from __future__ import annotations

import re
from dataclasses import fields
from pathlib import Path

from . import db
from .loader import Chunk, Document

failures: list[str] = []


def expect(condition: bool, label: str) -> None:
    if condition:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


PLACEHOLDER_RE = re.compile(r"%\((\w+)\)s")


def placeholders(sql: str) -> set[str]:
    return set(PLACEHOLDER_RE.findall(sql))


def insert_columns(sql: str) -> list[str]:
    """Column list from the INSERT INTO ... ( ... ) VALUES clause."""
    m = re.search(r"INSERT INTO \w+ \(([^)]*)\)\s*VALUES", sql, re.S | re.I)
    assert m, "could not parse INSERT column list"
    return [c.strip() for c in m.group(1).split(",") if c.strip()]


def schema_columns(sql: str, table: str) -> set[str]:
    """Real column names for `table`, via the SQL parser rather than by regex.

    Hand-rolled line scanning gets this wrong: the multi-line CHECK constraint
    on text_fidelity looks like a column definition to a naive parser.
    """
    try:
        import sqlglot
        from sqlglot import exp
    except ImportError:
        return _schema_columns_fallback(sql, table)

    for stmt in sqlglot.parse(sql, read="postgres"):
        if not isinstance(stmt, exp.Create):
            continue
        if stmt.this and stmt.this.this and stmt.this.this.name != table:
            continue
        return {c.alias_or_name for c in stmt.find_all(exp.ColumnDef)}
    raise AssertionError(f"could not find CREATE TABLE for {table}")


def _schema_columns_fallback(sql: str, table: str) -> set[str]:
    """Paren-depth-aware column scan, for when sqlglot isn't installed.

    Depth matters: a naive line scan treats the literals inside the multi-line
    `CHECK (text_fidelity IN (...))` constraint as column definitions.
    """
    m = re.search(rf"CREATE TABLE IF NOT EXISTS {table} \((.*?)\n\);", sql, re.S | re.I)
    assert m, f"could not find CREATE TABLE for {table}"

    cols: set[str] = set()
    depth = 0
    for raw in m.group(1).splitlines():
        line = raw.split("--")[0].strip()
        at_top_level = depth == 0
        depth += line.count("(") - line.count(")")
        if not line or not at_top_level:
            continue
        token = line.split()[0]
        if token.upper() in {"UNIQUE", "PRIMARY", "FOREIGN", "CHECK", "CONSTRAINT"}:
            continue
        if re.fullmatch(r"[a-z_][a-z0-9_]*", token):
            cols.add(token)
    return cols


def check_constraint_values(sql: str, column: str) -> set[str]:
    """The literal set allowed by a `CHECK (<column> IN (...))` constraint."""
    m = re.search(
        rf"{column}\s+text\s+NOT NULL\s+CHECK\s*\(\s*{column}\s+IN\s*\((.*?)\)\s*\)",
        sql,
        re.S | re.I,
    )
    assert m, f"could not find CHECK constraint for {column}"
    return set(re.findall(r"'(\w+)'", m.group(1)))


def check_pair(sql: str, dataclass_type, table: str, schema_sql: str, extra_ok: set[str]) -> None:
    name = dataclass_type.__name__
    ph = placeholders(sql)
    dc_fields = {f.name for f in fields(dataclass_type)}

    missing = ph - dc_fields
    expect(not missing, f"{name}: every SQL placeholder has a dataclass field ({missing or 'none missing'})")

    unused = dc_fields - ph
    expect(not unused, f"{name}: every dataclass field is written to SQL ({unused or 'none unused'})")

    cols = insert_columns(sql)
    expect(len(cols) == len(ph), f"{name}: column count {len(cols)} matches placeholder count {len(ph)}")
    expect(set(cols) == ph, f"{name}: column names match placeholder names")

    sch = schema_columns(schema_sql, table)
    not_in_schema = set(cols) - sch
    expect(not not_in_schema, f"{table}: all inserted columns exist in schema ({not_in_schema or 'ok'})")

    never_written = sch - set(cols) - extra_ok
    expect(
        not never_written,
        f"{table}: no unexpected column left unwritten ({never_written or 'ok'})",
    )


def main() -> int:
    schema_sql = Path("scripts/schema-part3.sql").read_text(encoding="utf-8")

    print("SQL parses as valid PostgreSQL")
    try:
        import sqlglot
    except ImportError:
        # Dev-only dependency (requirements-dev.txt). Skip rather than fail the
        # whole suite — the alignment checks below are the load-bearing ones.
        print("  skip sqlglot not installed (pip install -r requirements-dev.txt)")
    else:
        parsed_ok = True
        for stmt in (schema_sql, db.UPSERT_DOC, db.UPSERT_CHUNK):
            try:
                sqlglot.parse(stmt, read="postgres")
            except Exception as exc:  # noqa: BLE001
                parsed_ok = False
                print(f"    parse error: {exc}")
        expect(parsed_ok, "schema and upserts parse under the postgres dialect")

    print("\ndocuments: SQL <-> dataclass alignment")
    check_pair(
        db.UPSERT_DOC, Document, "documents", schema_sql,
        extra_ok={"ingested_at"},  # server default
    )

    print("\nchunks: SQL <-> dataclass alignment")
    check_pair(
        db.UPSERT_CHUNK, Chunk, "chunks", schema_sql,
        # Not written on INSERT: the embedding columns are populated by the
        # Part 4 backfill, and created_at has a server default. They ARE
        # referenced in the ON CONFLICT clause, which test_embed.py checks.
        extra_ok={
            "embedding", "embedding_model", "embedding_dim", "embedded_at",
            "created_at",
        },
    )

    print("\nfidelity labels in the classifier are all permitted by the CHECK constraint")
    allowed = check_constraint_values(schema_sql, "text_fidelity")
    from .loader import load_corpus

    corpus_chunks = load_corpus().chunks
    used = {c.text_fidelity for c in corpus_chunks}
    expect(
        bool(allowed) and used <= allowed,
        f"labels emitted {sorted(used)} are within CHECK set {sorted(allowed)}",
    )

    print("\nrole values are permitted by the CHECK constraint")
    allowed_roles = check_constraint_values(schema_sql, "role")
    roles = {c.role for c in corpus_chunks}
    expect(
        bool(allowed_roles) and roles <= allowed_roles,
        f"roles emitted {sorted(roles)} within CHECK set {sorted(allowed_roles)}",
    )

    print("\nembedding dimension matches the gateway's model")
    expect("vector(1024)" in schema_sql, "embedding column is vector(1024) — voyage-3.5 and BGE-M3")

    print("\nre-ingest preserves embeddings unless text changed")
    expect(
        "WHEN chunks.text IS DISTINCT FROM EXCLUDED.text THEN NULL" in db.UPSERT_CHUNK,
        "upsert nulls the embedding only when the chunk text changed",
    )

    if failures:
        print(f"\nFAILED ({len(failures)})")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("\nAll SQL checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
