"""Apply a .sql file to the app database.

    python scripts/apply_sql.py scripts/schema-b4-distractors.sql

Exists because the B4 run instructions said `python scripts\\schema-b4-....sql`,
which hands a SQL file to the Python interpreter and fails on the first em-dash.
A one-line applier is cheaper than remembering to have psql on PATH, and it uses
the same DSN resolution as everything else in the repository.

The whole file is sent as ONE statement, so it is one implicit transaction:
either every statement applies or none does. That is what you want for a schema
migration, and it is why the failed first attempt left the database untouched
rather than half-migrated.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(__doc__)
        return 2
    path = Path(args[0])
    if not path.exists():
        print(f"not found: {path}", file=sys.stderr)
        return 2

    from ingest import db

    problem = db.check_connection()
    if problem:
        print(problem, file=sys.stderr)
        return 2

    import psycopg

    with psycopg.connect(db.get_dsn()) as conn:
        conn.execute(path.read_text(encoding="utf-8"))
        conn.commit()
    print(f"applied {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
