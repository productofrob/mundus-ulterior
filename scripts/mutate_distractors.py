"""Mutation-verify Block B4's distractor containment.

Unlike the other mutation scripts here, containment does not live only in Python
— two of the five guards are enforced by a VIEW, and rewriting the .sql file on
disk would change nothing about the running database. So this harness mutates the
live schema object: it replaces a view with a version missing its guard clause,
runs the suite, and restores the view from `scripts/schema-b4-distractors.sql`.

That distinction matters. A text mutation of a .sql file would have "passed"
against an unmodified database and proved nothing at all — the presence assertion
this repository keeps paying for, wearing a mutation harness as a disguise.

Needs the database, and needs `scripts/schema-b4-distractors.sql` applied first:

    python scripts/apply_sql.py scripts/schema-b4-distractors.sql
    python -m ingest.test_distractors
    python scripts/mutate_distractors.py
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

# FINDING 10: this process's own stdout. On Windows `print` writes through a
# stream whose encoding comes from the console code page, and through a PIPE or
# a REDIRECT it falls back to the locale codec — cp1252, which cannot encode
# Greek, Tamil, Chinese, Ge'ez or runic. It does not degrade: it raises
# UnicodeEncodeError mid-output, with the file half written and every number in
# it correct. Found 2026-08-22 at build_ui_data.py:730, printing the Greek behind
# a `case_only` span into a redirect.
#
# Two neighbouring boundaries were already guarded and are NOT this one: a CHILD
# process's stdout (PYTHONIOENCODING in its env) and a PARENT decoding that child
# (subprocess encoding=). Both are about a pipe between two processes. This is
# about where THIS process is writing, and until 2026-08-22 nothing anywhere
# guarded it.
#
# errors="replace" is deliberate. A harness that cannot encode one character
# should print a replacement character and finish; it should never lose a run to
# a formatting problem. A mangled character is cosmetic. A three-day sweep that
# dies on day one is ninety chat calls.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SCHEMA = ROOT / "scripts" / "schema-b4-distractors.sql"
STORE = ROOT / "answer" / "store.py"
DB = ROOT / "ingest" / "db.py"
PY_SOURCES = (STORE, DB)

SUITE = "ingest.test_distractors"

# --------------------------------------------------------------------------
# Mutations applied to the live database
# --------------------------------------------------------------------------

VIEW_WITHOUT_GUARD = """
CREATE OR REPLACE VIEW retrievable_chunks AS
SELECT chunk_id, doc_id, parallel_group, role, lang, declared_lang, text,
       text_fidelity, region, source_type, citation, date_text,
       char_start, char_end, source_field, embedding, embedding_model
FROM chunks
WHERE eligible_for_retrieval
  AND embedding IS NOT NULL;
"""

CURVE_VIEW_WITH_GUARD = """
CREATE OR REPLACE VIEW retrievable_chunks_with_distractors AS
SELECT chunk_id, doc_id, parallel_group, role, lang, declared_lang, text,
       text_fidelity, region, source_type, citation, date_text,
       char_start, char_end, source_field, embedding, embedding_model,
       is_distractor
FROM chunks
WHERE eligible_for_retrieval
  AND embedding IS NOT NULL
  AND NOT is_distractor;
"""

DROP_TRIGGER = "DROP TRIGGER IF EXISTS chunks_distractor_matches_document ON chunks;"

SQL_MUTATIONS: list[tuple[str, str, str]] = [
    ("retrievable_chunks loses its distractor guard",
     VIEW_WITHOUT_GUARD,
     "a vectorised distractor is INVISIBLE to retrievable_chunks"),
    # The same mutation, caught by the assertion that reads the view DEFINITION
    # rather than counting rows through it. Both are kept: the count assertion
    # can be satisfied by an empty table, and the definition assertion can be
    # satisfied by a guard that is present but wrong.
    ("retrievable_chunks loses its guard (definition assertion)",
     VIEW_WITHOUT_GUARD,
     "retrievable_chunks still carries its distractor guard"),
    # The inverse mutation. Without it, the assertion that the curve view CAN
    # see a distractor is unfalsifiable, and the assertion above could be
    # passing because nothing is visible anywhere.
    ("retrievable_chunks_with_distractors gains a guard it must not have",
     CURVE_VIEW_WITH_GUARD,
     "a vectorised distractor is VISIBLE to retrievable_chunks_with_distractors"),
    ("the chunk/document agreement trigger is dropped",
     DROP_TRIGGER,
     "a chunk cannot disagree with its document about being a distractor"),
]

# --------------------------------------------------------------------------
# Mutations applied to Python sources
# --------------------------------------------------------------------------

PY_MUTATIONS: list[tuple[str, list[tuple[str, str]], str]] = [
    ("the translator's distractor guard removed",
     [("""FROM chunks
WHERE eligible_for_retrieval
  AND NOT is_distractor
  AND lang <> 'en'""",
       """FROM chunks
WHERE eligible_for_retrieval
  AND lang <> 'en'""")],
     "a non-English distractor is NOT offered to the translator"),
    ("the translatable count's distractor guard removed",
     [("""    (SELECT count(*) FROM chunks
      WHERE eligible_for_retrieval AND NOT is_distractor
        AND lang <> 'en' AND role = 'original') AS translatable;""",
       """    (SELECT count(*) FROM chunks
      WHERE eligible_for_retrieval
        AND lang <> 'en' AND role = 'original') AS translatable;""")],
     "a distractor does not inflate the translatable count"),
]

# The prune guard is exercised by the suite running the real DELETE statements
# rather than by importing them, so its mutation is a text edit to the same
# statements the suite executes. Kept honest by asserting the suite's own copy
# matches db.py — see check_prune_statements_match().
PRUNE_GUARD = "AND NOT is_distractor"


def run_suite() -> set[str]:
    result = subprocess.run(
        [sys.executable, "-m", SUITE], cwd=ROOT, capture_output=True, text=True
    )
    return {
        line.split("FAIL", 1)[1].strip()
        for line in result.stdout.splitlines()
        if line.strip().startswith("FAIL")
    }


def apply_sql(statement: str) -> None:
    import psycopg

    from ingest import db

    with psycopg.connect(db.get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(statement)
        conn.commit()


def restore_schema() -> str | None:
    """Re-apply the schema file. Returns a reason on failure, never raises.

    A restore that raises inside `finally` kills the harness mid-recovery and
    can leave a MUTATED VIEW in the live database — the worst possible outcome,
    because the next ranking run would then read a view with no distractor
    guard and report a clean number. Block 0 found all three existing mutation
    scripts conflating a restore failure with a suite failure; this is the same
    lesson one layer out, where the thing being restored is a schema object
    rather than a file.
    """
    try:
        apply_sql(SCHEMA.read_text(encoding="utf-8"))
        return None
    except Exception as exc:  # noqa: BLE001
        return (f"SCHEMA RESTORE FAILED: {exc}\n"
                f"    The live database may hold a MUTATED view. Recover with:\n"
                f"      python scripts/apply_sql.py {SCHEMA.relative_to(ROOT)}\n"
                f"    and do not run any ranking check until it succeeds.")


def check_prune_statements_match() -> str | None:
    """The suite runs its own copy of the prune DELETEs. If db.py's copy drifts,
    the suite would be proving containment for a statement nobody runs."""
    suite = (ROOT / "ingest" / "test_distractors.py").read_text(encoding="utf-8")
    dbtext = DB.read_text(encoding="utf-8")
    if suite.count(PRUNE_GUARD) < 2:
        return "the suite's prune statements no longer carry the guard"
    if dbtext.count(PRUNE_GUARD) < 2:
        return ("ingest/db.py's prune no longer carries the guard on both "
                "DELETE statements — the suite would pass on a copy")
    return None


def main() -> int:
    from ingest import db

    problem = db.check_connection()
    if problem:
        print(problem, file=sys.stderr)
        return 2

    problems: list[str] = []
    # 2026-08-28. Bytes on the way out — see the note in
    # scripts/mutate_places.py. mutate_ui_places converted an LF source to CRLF
    # on a live run and its text-comparing restore check could not see it.
    original_bytes = {f: f.read_bytes() for f in PY_SOURCES}
    originals = {f: f.read_text(encoding="utf-8") for f in PY_SOURCES}

    drift = check_prune_statements_match()
    if drift:
        problems.append(drift)
        print(f"  MISS prune statements: {drift}")
    else:
        print("  ok   the suite's prune statements match ingest/db.py's")

    try:
        for label, statement, guard in SQL_MUTATIONS:
            apply_sql(statement)
            failed = run_suite()
            restore_failure = restore_schema()
            if restore_failure:
                problems.append(restore_failure)
                print(f"  !!!! {restore_failure}")
                break
            if guard in failed:
                print(f"  ok   {label}\n       -> {guard}")
            else:
                problems.append(
                    f"{label}: expected {guard!r} to fail, got "
                    f"{sorted(failed) or 'no failures'}")
                print(f"  MISS {label}")

        for label, patches, guard in PY_MUTATIONS:
            edited = dict(originals)
            if not any(old in originals[f] for old, _ in patches for f in PY_SOURCES):
                problems.append(f"{label}: mutation target not found")
                print(f"  MISS {label} (target not found)")
                continue
            for old, new in patches:
                target = next(f for f in PY_SOURCES if old in edited[f])
                edited[target] = edited[target].replace(old, new, 1)
            for f in PY_SOURCES:
                f.write_text(edited[f], encoding="utf-8")
            failed = run_suite()
            for f in PY_SOURCES:
                f.write_bytes(original_bytes[f])
            if guard in failed:
                print(f"  ok   {label}\n       -> {guard}")
            else:
                problems.append(
                    f"{label}: expected {guard!r} to fail, got "
                    f"{sorted(failed) or 'no failures'}")
                print(f"  MISS {label}")
    finally:
        for f in PY_SOURCES:
            f.write_bytes(original_bytes[f])
        final_restore = restore_schema()
        if final_restore:
            problems.append(final_restore)
            print(f"  !!!! {final_restore}")

    unrestored = [f.name for f in PY_SOURCES
                  if f.read_bytes() != original_bytes[f]]
    if unrestored:
        problems.append("sources were NOT restored cleanly: " + ", ".join(unrestored))

    check = subprocess.run([sys.executable, "-m", SUITE], cwd=ROOT,
                           capture_output=True, text=True)
    if check.returncode != 0:
        problems.append(
            f"schema and sources restored, but `{SUITE}` fails on its own "
            f"account — a finding about the suite, not about this harness")
        print(f"\n--- {SUITE} output, so it is not lost ---")
        print((check.stdout or "") + (check.stderr or ""), end="")
        print("--- end ---")

    print()
    if problems:
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"all {len(SQL_MUTATIONS) + len(PY_MUTATIONS)} mutations verified; "
          f"schema and sources restored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
