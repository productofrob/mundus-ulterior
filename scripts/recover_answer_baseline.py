"""Part 8 step zero: get the Part 7 baseline out of Postgres and onto disk.

Why this exists
---------------

`eval/answer_runs/` was added at the end of Part 7, *after* the four live runs it
was meant to capture. The directory currently holds five files of 90-130 bytes —
the same-second collision fixtures (`{"answer": "answer B reworded"}`) — and not
one real run. So the archive that Part 8's decisions rest on does not exist.

That matters most for the case Part 8 names as case zero: the Vimose question
under `p7-answer-v2` produced seven quotations, all seven resolved to characters
on disk, hedges intact; under `p7-answer-v3` it refuses, three times out of
three. Both score `Grounded`. A harness that cannot separate those two is not
measuring anything — and right now the v2 side of that comparison exists only as
prose in PROGRESS.md.

The good news is the Part 6 lesson paying off a second time. `answer_id` is a
sha256 over (question, model, **prompt version**, ordered chunk ids), so a v3 run
of the same question against the same evidence wrote a *new* row rather than
overwriting v2's. If the database has not been rebuilt, the v2 answers are still
there. This script finds out, and then writes them out.

What a recovered archive is, and is not
---------------------------------------

A native archive is `run_answer`'s payload: question, answer, grounding, and
`passages` as `Passage.to_dict()` — including the passage text and the English
actually shown to the model — plus the rendered `sources_block`.

The database stores the answer, the full grounding report (jsonb, quote spans
included), and one `answer_citations` row per marker. It does **not** store the
passage text or the sources block. Those were never persisted, and no query
brings them back.

So a recovered archive is a reconstruction, and it says so: `recovered: true`,
with `recovered_absent` naming every field that could not be rebuilt and
`recovered_from` naming the query it came from. This is the same argument as
`calibrated: false` in the confidence profiles and `english_ground` on a
citation — a record that cannot distinguish a witness from a reconstruction will
eventually be read as though everything in it were a witness.

The timestamp is likewise qualified. `UPSERT_ANSWER` sets `created_at = now()`
on conflict, so the column records the *last write* of that answer_id, not the
first run of that answer. Two runs of the same question, same prompt, same
evidence leave one row bearing the second run's time. `timestamp_meaning` says
so in every file.

Usage (repo root, venv active, .env loaded, db up)
--------------------------------------------------

    python scripts/recover_answer_baseline.py                 # census, writes nothing
    python scripts/recover_answer_baseline.py --json          # census as json
    python scripts/recover_answer_baseline.py --write         # dump every answer
    python scripts/recover_answer_baseline.py --write --prompt-version p7-answer-v2
    python scripts/recover_answer_baseline.py --write --question-contains Vimose

Costs nothing: no gateway calls, no embeddings, database reads only. Run the
census first and read it before writing anything.

Exit codes: 0 census printed or files written, 1 nothing found to recover,
2 could not run (no database, missing table).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg  # noqa: E402

from answer import answer_store  # noqa: E402
from answer.run_answer import RUNS_DIR  # noqa: E402


# What the reconstruction cannot contain, named in every file it writes rather
# than left for a reader of Part 8 to discover by finding a key missing.
ABSENT = [
    "passages[].text — the passage text shown to the model was never persisted",
    "passages[].english.text — likewise",
    "sources_block — the rendered evidence block was never persisted",
    "refused — not a stored column; infer from the answer text if needed",
]

SELECT_CENSUS = """
SELECT answer_prompt_version,
       answer_model,
       count(*)                    AS answers,
       count(*) FILTER (WHERE grounded) AS grounded,
       min(created_at)             AS earliest,
       max(created_at)             AS latest
FROM answers
GROUP BY answer_prompt_version, answer_model
ORDER BY answer_prompt_version, answer_model;
"""

SELECT_QUESTIONS = """
SELECT answer_prompt_version, question, count(*) AS rows
FROM answers
GROUP BY answer_prompt_version, question
ORDER BY question, answer_prompt_version;
"""

SELECT_ANSWERS = """
SELECT answer_id, question, question_lang, answer_text,
       answer_model, answer_prompt_version, embedding_model, retrieval_k,
       grounded, grounding, notes, created_at
FROM answers
WHERE (%(prompt_version)s::text IS NULL
       OR answer_prompt_version = %(prompt_version)s::text)
  AND (%(question_contains)s::text IS NULL
       OR question ILIKE '%%' || %(question_contains)s::text || '%%')
ORDER BY created_at, answer_id;
"""

SELECT_CITATIONS = """
SELECT answer_id, marker, chunk_id, doc_id, similarity,
       english_kind, english_ground, confidence_band, confidence_profile,
       flags, cited, quoted, source_field, char_start, char_end
FROM answer_citations
WHERE answer_id = ANY(%(answer_ids)s::text[])
ORDER BY answer_id, marker;
"""


# --------------------------------------------------------------------------
# Census
# --------------------------------------------------------------------------

def census(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute(SELECT_CENSUS)
        versions = [
            {
                "prompt_version": row[0],
                "model": row[1],
                "answers": row[2],
                "grounded": row[3],
                "earliest": row[4].isoformat() if row[4] else None,
                "latest": row[5].isoformat() if row[5] else None,
            }
            for row in cur.fetchall()
        ]
        cur.execute(SELECT_QUESTIONS)
        questions: dict[str, dict[str, int]] = {}
        for prompt_version, question, rows in cur.fetchall():
            questions.setdefault(question, {})[prompt_version] = rows

    return {"by_prompt_version": versions, "by_question": questions}


def print_census(report: dict) -> None:
    versions = report["by_prompt_version"]
    if not versions:
        print("No rows in `answers`. Nothing to recover.\n")
        print(
            "That is the bad case: the Part 7 baseline exists only as prose in\n"
            "PROGRESS.md. Re-run the five questions under both prompt versions\n"
            "before building the harness, or Part 8 has nothing to adjudicate."
        )
        return

    print("answers by prompt version\n")
    for row in versions:
        print(
            f"  {row['prompt_version']:<20} {row['model']}\n"
            f"      {row['answers']} answer(s), {row['grounded']} grounded\n"
            f"      created_at {row['earliest']} .. {row['latest']}"
        )
    print()

    versions_seen = sorted({row["prompt_version"] for row in versions})
    print(f"questions x prompt version  ({len(report['by_question'])} question(s))\n")
    width = max(len(v) for v in versions_seen)
    print("      " + "  ".join(v.ljust(width) for v in versions_seen))
    for question, counts in report["by_question"].items():
        cells = "  ".join(
            str(counts.get(v, "-")).ljust(width) for v in versions_seen
        )
        print(f"      {cells}  {question[:60]}")
    print()

    # The comparison Part 8 exists to make. Say plainly whether it is available.
    both = [
        q for q, counts in report["by_question"].items() if len(counts) > 1
    ]
    if both:
        print(
            f"{len(both)} question(s) have answers under more than one prompt "
            "version.\nThose are the adjudicable pairs — case zero material:"
        )
        for question in both:
            print(f"  - {question[:72]}")
    else:
        print(
            "No question has answers under more than one prompt version.\n"
            "There is no prompt-to-prompt comparison in this database, which is\n"
            "the pair Part 8 decision 5 is built around. Re-run before building."
        )
    print()

    print(
        "created_at is the row's LAST WRITE, not the first run: UPSERT_ANSWER\n"
        "sets created_at = now() on conflict. Two runs of the same question,\n"
        "prompt and evidence leave one row bearing the second run's time."
    )


# --------------------------------------------------------------------------
# Recovery
# --------------------------------------------------------------------------

def _citation_payload(row) -> dict:
    (
        _answer_id, marker, chunk_id, doc_id, similarity, english_kind,
        english_ground, confidence_band, confidence_profile, flags, cited,
        quoted, source_field, char_start, char_end,
    ) = row
    return {
        "marker": marker,
        "chunk_id": chunk_id,
        "doc_id": doc_id,
        "similarity": similarity,
        "cited": cited,
        "quoted": quoted,
        "source_field": source_field,
        "char_start": char_start,
        "char_end": char_end,
        "english": {
            "kind": english_kind,
            "ground": english_ground,
            "band": confidence_band,
            "profile": confidence_profile,
            "flags": list(flags or []),
        },
    }


def build_payloads(conn, prompt_version: str | None,
                   question_contains: str | None) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            SELECT_ANSWERS,
            {
                "prompt_version": prompt_version,
                "question_contains": question_contains,
            },
        )
        rows = cur.fetchall()
        if not rows:
            return []

        answer_ids = [row[0] for row in rows]
        cur.execute(SELECT_CITATIONS, {"answer_ids": answer_ids})
        citations: dict[str, list[dict]] = {}
        for citation in cur.fetchall():
            citations.setdefault(citation[0], []).append(
                _citation_payload(citation)
            )

    payloads = []
    for row in rows:
        (
            answer_id, question, question_lang, answer_text, answer_model,
            answer_prompt_version, embedding_model, retrieval_k, grounded,
            grounding, notes, created_at,
        ) = row
        payloads.append({
            "timestamp": created_at.isoformat(timespec="seconds"),
            "timestamp_meaning": (
                "answers.created_at — the row's last write, not necessarily the "
                "first run of this answer (UPSERT_ANSWER sets created_at = now() "
                "on conflict)"
            ),
            "recovered": True,
            "recovered_from": "answers + answer_citations",
            "recovered_absent": ABSENT,
            "question": question,
            "question_lang": question_lang,
            "answer": answer_text,
            "grounded": grounded,
            "model": answer_model,
            "prompt_version": answer_prompt_version,
            "embedding_model": embedding_model,
            "retrieval_k": retrieval_k,
            "answer_id": answer_id,
            "grounding": grounding or {},
            "passages": citations.get(answer_id, []),
            "notes": notes,
        })
    return payloads


def archive_path(payload: dict) -> Path:
    """Same naming rule as run_answer._archive, plus a `-recovered` marker.

    The marker is in the filename as well as the payload so a reconstruction can
    be spotted from a directory listing, without opening it. Never overwrites:
    two payloads sharing a second and an answer_id get -2, -3, as upstream.
    """
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = payload["timestamp"].replace(":", "").replace("-", "")
    stem = f"{stamp}-{payload['answer_id'][:8]}-recovered"
    path = RUNS_DIR / f"{stem}.json"
    counter = 2
    while path.exists():
        path = RUNS_DIR / f"{stem}-{counter}.json"
        counter += 1
    return path


def inspect_existing() -> dict:
    """What is already in eval/answer_runs/, split into runs and not-runs.

    A file with no `question` key is not a run. The five currently there are
    collision fixtures from the Part 7 test suite; they are reported, never
    deleted — deciding what to do with them is a separate call.
    """
    runs, fixtures, unreadable = [], [], []
    for path in sorted(RUNS_DIR.glob("*.json")) if RUNS_DIR.exists() else []:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            unreadable.append((path.name, str(exc)))
            continue
        (runs if isinstance(data, dict) and "question" in data
         else fixtures).append(path.name)
    return {"runs": runs, "not_runs": fixtures, "unreadable": unreadable}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Recover the Part 7 answer baseline from Postgres into "
                    "eval/answer_runs/"
    )
    parser.add_argument(
        "--write", action="store_true",
        help="write recovered archives (default is a census that writes nothing)",
    )
    parser.add_argument(
        "--prompt-version",
        help="only this answer_prompt_version, e.g. p7-answer-v2",
    )
    parser.add_argument(
        "--question-contains",
        help="only questions matching this substring, case-insensitive",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    existing = inspect_existing()
    if not args.json:
        print(f"eval/answer_runs/ holds {len(existing['runs'])} run(s) and "
              f"{len(existing['not_runs'])} file(s) that are not runs.")
        for name in existing["not_runs"]:
            print(f"      not a run: {name}")
        for name, why in existing["unreadable"]:
            print(f"      UNREADABLE: {name} — {why}")
        print()

    try:
        with psycopg.connect(answer_store.get_dsn(), connect_timeout=5) as conn:
            report = census(conn)
            if args.write:
                payloads = build_payloads(
                    conn, args.prompt_version, args.question_contains
                )
            else:
                payloads = None
    except psycopg.OperationalError as exc:
        print(f"cannot reach the database: {exc}", file=sys.stderr)
        print("is the container up?  docker compose up -d db", file=sys.stderr)
        return 2
    except psycopg.errors.UndefinedTable as exc:
        print(f"no answers table: {exc}", file=sys.stderr)
        print("Part 7 schema was never applied to this database.", file=sys.stderr)
        return 2

    if not args.write:
        if args.json:
            print(json.dumps({"existing": existing, "census": report},
                             indent=2, ensure_ascii=False))
        else:
            print_census(report)
            print("\ncensus only — nothing written. Re-run with --write.")
        return 0 if report["by_prompt_version"] else 1

    if not payloads:
        print("no answers matched — nothing written", file=sys.stderr)
        return 1

    written = []
    for payload in payloads:
        path = archive_path(payload)
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        written.append(str(path))

    if args.json:
        print(json.dumps({"written": written}, indent=2, ensure_ascii=False))
    else:
        print(f"recovered {len(written)} answer(s):\n")
        for payload, path in zip(payloads, written):
            print(f"  {Path(path).name}")
            print(f"      {payload['prompt_version']} | "
                  f"grounded={payload['grounded']} | "
                  f"{len(payload['passages'])} citation row(s)")
            print(f"      {payload['question'][:66]}")
        print(
            "\nEvery file is marked `recovered: true` with `recovered_absent`.\n"
            "The passage text and the rendered sources block were never stored\n"
            "and are not in these files. Do not read a reconstruction as a run."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
