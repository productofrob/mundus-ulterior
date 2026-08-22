"""Offline checks for scripts/recover_answer_baseline.py.

No network, no database. Everything here is a fact about strings, paths and
dict shapes — the same standard Part 7's checks hold to, and the standard Part 8
decision 2 commits to for the eval harness itself.

The guards worth their keep are the two that protect a distinction rather than a
behaviour:

  * a recovered archive must never be mistakable for a native run, because the
    passage text and sources block it lacks are exactly what a reader would
    assume were present; and
  * a nullable SQL parameter must carry a cast, because `AmbiguousParameter`
    parses perfectly and only fails against a real Postgres — the Part 4 lesson,
    restated here because this file introduces two new nullable filters.

Run:  python scripts/test_recover_baseline.py
"""

from __future__ import annotations

import ast
import datetime as dt
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import recover_answer_baseline as rb  # noqa: E402  (scripts/ is on the path)
from answer import run_answer  # noqa: E402

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
# about where THIS process is writing, and until 2026-08-22 nothing guarded it.
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

PASSED = 0
FAILED = 0


def expect(condition: bool, label: str) -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ok   {label}")
    else:
        FAILED += 1
        print(f"  FAIL {label}")


# --------------------------------------------------------------------------
# A fake database, so the payload builder can be exercised offline
# --------------------------------------------------------------------------

_WHEN = dt.datetime(2026, 8, 10, 12, 0, 0, tzinfo=dt.timezone.utc)

_ANSWER_ROW = (
    "3b4489a4f7657729e397a3506eec3bf1",          # answer_id
    "What do the Vimose runes say?",              # question
    "en",                                         # question_lang
    "The corpus does not contain a full rendering [S1].",
    "anthropic/claude-haiku-4-5-20251001",        # answer_model
    "p7-answer-v2",                               # answer_prompt_version
    "voyage/voyage-3.5",                          # embedding_model
    12,                                           # retrieval_k
    True,                                         # grounded
    {"claim_sentences": 1, "cited_sentences": 1, "quote_spans": []},
    None,                                         # notes
    _WHEN,                                        # created_at
)

_CITATION_ROW = (
    "3b4489a4f7657729e397a3506eec3bf1", "S1", "scandinavia-02-vimose:0",
    "scandinavia-02-vimose", 0.5123, "published", "section", None, None,
    [], True, True, "original_text_excerpt", 0, 118,
)


class _FakeCursor:
    def __init__(self, script: dict[str, list]) -> None:
        self._script = script
        self._rows: list = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, query, params=None):
        for marker, rows in self._script.items():
            if marker in query:
                self._rows = rows
                return
        self._rows = []

    def fetchall(self):
        return self._rows


class _FakeConn:
    def __init__(self, script: dict[str, list]) -> None:
        self._script = script

    def cursor(self):
        return _FakeCursor(self._script)


# --------------------------------------------------------------------------

def test_sql_casts() -> None:
    print("\nSQL")

    queries = {
        "SELECT_CENSUS": rb.SELECT_CENSUS,
        "SELECT_QUESTIONS": rb.SELECT_QUESTIONS,
        "SELECT_ANSWERS": rb.SELECT_ANSWERS,
        "SELECT_CITATIONS": rb.SELECT_CITATIONS,
    }

    # GUARD (Part 4, restated): `%(x)s IS NULL` with no cast parses cleanly and
    # fails at execution with AmbiguousParameter. This file adds two new nullable
    # filters, which is precisely the shape that bug had.
    for name, query in queries.items():
        uncast = re.findall(r"%\((\w+)\)s(?!::)\s*IS NULL", query)
        expect(not uncast,
               f"GUARD {name}: every nullable parameter carries a cast "
               f"(uncast: {uncast})")
        arrays = re.findall(r"ANY\(%\((\w+)\)s\)", query)
        expect(not arrays,
               f"GUARD {name}: every ANY() parameter carries a ::text[] cast "
               f"(uncast: {arrays})")

    # The ILIKE filter concatenates a cast parameter rather than interpolating,
    # so a question containing % or _ cannot become a wildcard by accident.
    expect("ILIKE '%%' || %(question_contains)s::text || '%%'" in rb.SELECT_ANSWERS,
           "the substring filter is a bound parameter, not string interpolation")

    # Reads only. This script must not be able to change the baseline it recovers.
    for name, query in queries.items():
        upper = query.upper()
        expect(
            not any(word in upper for word in
                    ("INSERT ", "UPDATE ", "DELETE ", "DROP ", "ALTER ")),
            f"GUARD {name}: read-only — recovery cannot mutate the evidence",
        )

    try:
        import sqlglot

        for name, query in queries.items():
            sqlglot.parse_one(query, read="postgres")
        expect(True, "every query parses as PostgreSQL")
    except ImportError:
        print("  skip sqlglot not installed (pip install -r requirements-dev.txt)")
    except Exception as exc:  # noqa: BLE001
        expect(False, f"every query parses as PostgreSQL ({exc})")


def test_recovered_payload() -> None:
    print("\nrecovered payloads")

    conn = _FakeConn({
        "FROM answers\nWHERE": [_ANSWER_ROW],
        "FROM answer_citations": [_CITATION_ROW],
    })
    payloads = rb.build_payloads(conn, None, None)
    expect(len(payloads) == 1, "one answer row becomes one payload")
    payload = payloads[0]

    # GUARD: a reconstruction must announce itself. The passage text and the
    # rendered sources block were never persisted, and a file that looks like a
    # native run while missing them will be read as though they were absent from
    # the run rather than absent from the record.
    expect(payload.get("recovered") is True,
           "GUARD every recovered payload is marked recovered: true")
    expect(bool(payload.get("recovered_absent")),
           "GUARD recovered_absent names what could not be rebuilt")
    expect(any("sources_block" in item for item in payload["recovered_absent"]),
           "GUARD the missing sources block is named, not merely missing")
    expect(any("text" in item for item in payload["recovered_absent"]),
           "GUARD the missing passage text is named, not merely missing")

    # And it must not silently supply the fields it cannot know.
    expect("sources_block" not in payload,
           "a recovered payload does not invent a sources block")
    for passage in payload["passages"]:
        expect("text" not in passage,
               "a recovered passage does not invent its text")

    # What it can carry, it must: this is the material Part 8 adjudicates on.
    for key in ("question", "answer", "grounded", "model", "prompt_version",
                "answer_id", "grounding", "passages"):
        expect(key in payload, f"payload carries {key}")

    expect(payload["prompt_version"] == "p7-answer-v2",
           "the prompt version survives — the axis case zero compares on")
    expect(payload["passages"][0]["english"]["kind"] == "published",
           "english kind survives per citation")
    expect(payload["passages"][0]["char_start"] == 0
           and payload["passages"][0]["char_end"] == 118,
           "the character span survives — the Part 7 claim, still checkable")

    # The timestamp is qualified, because created_at is the last write.
    expect("timestamp_meaning" in payload,
           "GUARD the timestamp says what it means (created_at is last write)")
    expect("last write" in payload["timestamp_meaning"],
           "the qualification is specific, not decorative")

    # A native run payload and a recovered one must not share a shape that hides
    # the difference. Keys the native writer emits and this one cannot: named.
    native_only = {"sources_block", "refused"}
    expect(not (native_only & set(payload)),
           f"recovered payloads omit native-only keys {sorted(native_only)}")


def test_archive_never_overwrites() -> None:
    print("\narchiving")

    with tempfile.TemporaryDirectory() as tmp:
        original = rb.RUNS_DIR
        rb.RUNS_DIR = Path(tmp)
        try:
            payload = {
                "timestamp": "2026-08-10T12:00:00+00:00",
                "answer_id": "3b4489a4f7657729e397a3506eec3bf1",
            }
            first = rb.archive_path(payload)
            first.write_text("{}", encoding="utf-8")
            second = rb.archive_path(payload)
            second.write_text("{}", encoding="utf-8")
            third = rb.archive_path(payload)

            expect(first != second != third,
                   "GUARD identical timestamp and answer_id never collide")
            expect(second.name.endswith("-2.json")
                   and third.name.endswith("-3.json"),
                   "collisions are suffixed -2, -3, as run_answer._archive does")
            expect("-recovered" in first.name,
                   "GUARD a reconstruction is visible in a directory listing")
            expect(first.name.startswith("20260810T120000"),
                   "the timestamp prefix matches run_answer's naming, so a "
                   "directory listing still sorts chronologically")
        finally:
            rb.RUNS_DIR = original

    # The directory is defined once, upstream. Two definitions drift.
    expect(rb.RUNS_DIR == run_answer.RUNS_DIR,
           "GUARD the runs directory is imported from run_answer, not re-derived")


def test_inspect_existing() -> None:
    print("\ninspecting what is already there")

    with tempfile.TemporaryDirectory() as tmp:
        original = rb.RUNS_DIR
        rb.RUNS_DIR = Path(tmp)
        try:
            # The five files actually in eval/answer_runs/ look like this.
            (rb.RUNS_DIR / "20260810T120000+0000-3b4489a4.json").write_text(
                json.dumps({"timestamp": "2026-08-10T12:00:00+00:00",
                            "answer": "answer B reworded",
                            "answer_id": "3b4489a4"}),
                encoding="utf-8",
            )
            (rb.RUNS_DIR / "20260810T130000+0000-aaaaaaaa-recovered.json").write_text(
                json.dumps({"question": "real", "answer": "real",
                            "recovered": True}),
                encoding="utf-8",
            )
            (rb.RUNS_DIR / "broken.json").write_text("{not json", encoding="utf-8")

            report = rb.inspect_existing()
            expect(len(report["not_runs"]) == 1,
                   "GUARD a fixture with no question is not counted as a run")
            expect(len(report["runs"]) == 1, "a real run is counted as one")
            expect(len(report["unreadable"]) == 1,
                   "an unparseable file is reported, not skipped in silence")
        finally:
            rb.RUNS_DIR = original


def test_absent_list_is_honest() -> None:
    print("\nthe absent list")

    # GUARD: if run_answer's payload grows a key this script cannot rebuild, the
    # absent list must grow with it. Checked against the source rather than a
    # copy of it, so the two cannot drift silently.
    #
    # Found by parsing, not by slicing on `payload = {`. The first version did
    # slice, and when run_answer grew --repeat the assignment became
    # `payloads.append({` — the guard raised IndexError instead of failing, which
    # a mutation run reported as a crash rather than a finding. A guard that
    # breaks when the code is merely rearranged trains people to ignore it.
    source = Path("answer/run_answer.py").read_text(encoding="utf-8")
    native_keys: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Dict):
            continue
        keys = {k.value for k in node.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)}
        # The archived payload, identified by what it is rather than where it
        # sits: no other dict in this module carries both of these.
        if {"grounding", "answer_id"} <= keys:
            native_keys |= keys
    expect(bool(native_keys),
           "the archived payload dict was located in run_answer.py")
    recoverable = {
        "timestamp", "question", "answer", "grounded", "model",
        "prompt_version", "embedding_model", "answer_id", "grounding",
        "passages",
    }
    unaccounted = native_keys - recoverable
    named = " ".join(rb.ABSENT)
    missing = [key for key in unaccounted if key not in named]
    expect(not missing,
           f"GUARD every native payload key is either recoverable or named in "
           f"ABSENT (unaccounted: {missing})")


def main() -> int:
    print("recover_answer_baseline — offline checks")
    test_sql_casts()
    test_recovered_payload()
    test_archive_never_overwrites()
    test_inspect_existing()
    test_absent_list_is_honest()
    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
