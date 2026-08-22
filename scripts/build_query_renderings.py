"""Produce `eval/gold/query_renderings.json` — C2's frozen query renderings.

Ruling 19: the renderings are DATA, not a pipeline step. `chat-default` is a
gateway alias that will be repointed, and C5-C6's "two runs on different days
against a frozen configuration" is only true if the queries are byte-identical
on both days. So this script runs ONCE, its output is reviewed and committed,
and every ranking run reads it from disk and records its content hash.

Ruling 12: the target languages come from the INDEX. This script reads
`SELECT DISTINCT lang FROM {view}` and the gold set's query TEXTS and query
LANGUAGES, and it reads nothing else about a pair. `expect_lang`, `expect_doc`
and `lang_pool` are never loaded, and the file it writes is keyed on query text
with no pair id in it, so a per-pair language choice cannot be recorded here
even by a later edit that forgets why.

Ruling 17(a): every rendering is script-checked before it is admitted. A
rendering in the wrong writing system is kept in the file, marked `ok: false`
with its reason, and never embedded — kept because "the model returned Latin
for Tamil" is evidence, and deleting it would leave only a gap.

Resumable by design. A rendering already in the file is not re-made, so a run
interrupted at call 140 of 205 costs 65 calls to finish rather than 205.

    python scripts/build_query_renderings.py --dry-run     # plan and cost, no spend
    python scripts/build_query_renderings.py
    python scripts/build_query_renderings.py --pace 0.5 --limit 20
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from retrieve.render import (  # noqa: E402
    DEFAULT_PATH,
    SCHEMA,
    SUPERSEDED_SCHEMAS,
    RenderingError,
    best_attempt,
    settle_row as settle,
    expected_rendering_count,
    rendering_problems,
    required_script,
    script_ratio,
    target_langs,
)

DEFAULT_VIEW = "retrievable_chunks_with_distractors"

from answer.translate import DEFAULT_MODEL as DEFAULT_CHAT_MODEL  # noqa: E402

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


def index_languages(view: str) -> list[str]:
    """Every language present in the searched view. Ruling 12's whole input."""
    from ingest import db

    reason = db.check_connection()
    if reason:
        raise SystemExit(reason)

    import psycopg

    from retrieve.search import SEARCHABLE_VIEWS

    if view not in SEARCHABLE_VIEWS:
        raise SystemExit(
            f"{view!r} is not a searchable view. Known: {sorted(SEARCHABLE_VIEWS)}. "
            f"The renderings are built for the view the RUN searches; building "
            f"them against another one produces a language set the run's own "
            f"index does not justify."
        )

    with psycopg.connect(db.get_dsn()) as conn, conn.cursor() as cur:
        cur.execute(f"SELECT DISTINCT lang FROM {view} WHERE lang IS NOT NULL;")
        return sorted(r[0] for r in cur.fetchall())


def gold_queries() -> dict[str, str]:
    """query text -> query language. NOTHING else about a pair is read.

    Returned as a dict rather than a list of pairs so that the pair objects do
    not survive this function. A caller cannot reach `expect_lang` through a
    string.
    """
    from eval.goldset import load_ranking_pairs

    out: dict[str, str] = {}
    for pair in load_ranking_pairs():
        existing = out.setdefault(pair.query, pair.query_lang)
        if existing != pair.query_lang:
            raise SystemExit(
                f"one query text carries two query languages "
                f"({existing!r} and {pair.query_lang!r}):\n  {pair.query[:80]!r}\n"
                f"The rendering file is keyed on text, so this is not "
                f"representable and would silently render one of them wrongly."
            )
    return out


def load_existing(path: pathlib.Path) -> tuple[dict, str]:
    """Read a v1 or v2 file. A v1 row becomes a v2 row with one attempt.

    Upgrading here rather than refusing: v1's whole defect is that it holds one
    text per row, and the text it holds is still evidence. Refusing to read it
    would throw away the 186 renderings that are fine to punish the format.
    """
    if not path.exists():
        return {}, SCHEMA
    doc = json.loads(path.read_text(encoding="utf-8"))
    schema = doc.get("schema")
    if schema not in SUPERSEDED_SCHEMAS and schema != SCHEMA:
        raise SystemExit(
            f"{path} declares schema {schema!r}, which this script does not "
            f"know how to read. Known: {SCHEMA!r} and {sorted(SUPERSEDED_SCHEMAS)}."
        )
    # v1 recorded the model ONCE, at file level, and the v1->v2 migration
    # originally dropped it. The consequence was worse than a gap: after a
    # partial re-render the top line named the new model while 189 of the rows
    # under it came from the old one, and nothing in any row said so. Backfilled
    # here, so a converted row carries the model that actually produced it.
    file_model = doc.get("chat_model")
    file_prompt = doc.get("prompt_version")
    out: dict[str, dict] = {}
    for entry in doc.get("queries", []):
        rows: dict[str, dict] = {}
        for lang, row in entry.get("renderings", {}).items():
            attempts = row.get("attempts")
            if not attempts:
                attempts = [{
                    "text": row.get("text", ""),
                    "ok": row.get("ok", False),
                    "problems": row.get("problems", []),
                    "notes": row.get("notes", []),
                    "prompt_version": row.get("prompt_version") or file_prompt,
                    "chat_model": row.get("chat_model") or file_model,
                    "temperature": row.get("temperature"),
                }]
            # `text` and `ok` are carried through so the caller can tell what
            # CHANGED when the row is re-judged. Dropping them made the
            # promotion counter permanently blind: every comparison was against
            # None, so a run that corrected a rendering reported "nothing to do"
            # and returned without writing it.
            rows[lang] = {
                "attempts": attempts,
                "text": row.get("text"),
                "ok": row.get("ok"),
            }
        out[entry["query"]] = rows
    return out, schema


def write_atomically(path: pathlib.Path, doc: dict) -> None:
    """Write, then move. Ruling: archive before you print.

    A `KeyError` in a report has already destroyed a twenty-six-minute run in
    this repository. The file is the evidence; the summary printed afterwards is
    a rendering of it, and nothing that happens after this call can cost a
    single one of the calls it just paid for.

    Deleted by accident on 2026-08-16 and restored the same day. A patch that
    removed `settle` by slicing between two line offsets took this function with
    it, because it sat between them — and the failure surfaced as a NameError
    at the moment of writing, AFTER a promotion had been detected and reported.
    The run said "promoted 1 row(s)" and then wrote nothing. Delete by name, not
    by offset.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    tmp.replace(path)


def build(view: str, path: pathlib.Path, *, dry_run: bool, limit: int | None,
          pace: float, refresh: bool, redo_held: bool,
          attempt_all: bool, model: str, only_lang: str | None) -> int:
    langs = index_languages(view)
    queries = gold_queries()

    # Fail before spending, not after. `required_script` raises for a language
    # with no declared writing system, and finding that out on call 140 would
    # cost 140 calls to learn something a dictionary lookup knows.
    for lang in langs:
        if lang != "en":
            required_script(lang)

    existing, on_disk_schema = ({}, SCHEMA) if refresh else load_existing(path)
    # A file written under a superseded schema must be rewritten even when no
    # verdict changed and nothing is re-rendered: the run-time reader refuses
    # v1 outright, so "nothing to do" would leave the ranking unable to read
    # its own renderings.
    needs_upgrade = on_disk_schema != SCHEMA

    # Re-judge every stored rendering against the CURRENT guard, not the guard
    # that was in force when it was written. Ruling 20 raised SCRIPT_FLOOR from
    # 0.6 to 1.0 after a run had already been made at 0.6, and a file that kept
    # its old verdicts would have carried ten renderings the project has since
    # decided are not renderings — under an `ok: true` that no longer means what
    # it says. The text is evidence; the verdict is derived, and it is re-derived
    # here every time.
    # Two kinds of change, and the second was invisible until 2026-08-16.
    # Ruling 23b's mark-aware guard held a haiku rendering that carried a
    # Malayalam vowel sign; `best_attempt` promoted the sonnet draw sitting
    # beside it, so the ROW stayed `ok` while the text under it changed. A
    # counter watching only the ok flag saw nothing, the run reported "nothing
    # to do" and returned WITHOUT WRITING — a correction computed and thrown
    # away. Promotions are changes.
    rejudged: list[tuple[str, str, bool]] = []
    promoted: list[tuple[str, str]] = []
    for query, entry in existing.items():
        for target, row in entry.items():
            was_ok, was_text = row.get("ok"), row.get("text")
            settle(row, target, query)
            if was_ok is not None and was_ok != row["ok"]:
                rejudged.append((query, target, row["ok"]))
            elif was_text is not None and was_text != row["text"]:
                promoted.append((query, target))

    if only_lang and only_lang not in target_langs(langs, "en"):
        raise SystemExit(
            f"--only-lang {only_lang!r} is not one of this index's render "
            f"targets {target_langs(langs, 'en')}. It filters the LANGUAGE "
            f"SET, which ruling 12 derives from the index; it is not a way to "
            f"reach a language the index does not hold."
        )

    plan: list[tuple[str, str, str]] = []          # (query, query_lang, target)
    for query, query_lang in sorted(queries.items()):
        for target in target_langs(langs, query_lang):
            if only_lang and target != only_lang:
                continue
            row = existing.get(query, {}).get(target)
            if row is not None and not attempt_all and (
                    row.get("ok") or not redo_held):
                continue
            plan.append((query, query_lang, target))

    total = expected_rendering_count(langs, queries.values())
    print(f"view              {view}")
    print(f"index languages   {langs}")
    print(f"render targets    {target_langs(langs, 'en')}")
    print(f"gold queries      {len(queries)} distinct "
          f"({sum(1 for v in queries.values() if v != 'en')} not English)")
    print(f"renderings wanted {total}")
    print(f"already on disk   {total - len(plan)}")
    print(f"calls this run    {len(plan)}"
          + (f", capped at {limit}" if limit else "")
          + ("" if (redo_held or attempt_all)
             else "   (--redo-held re-renders the held ones)"))
    if promoted:
        print(f"promoted          {len(promoted)} row(s) now read from a "
              f"different attempt under the current guard, with no change to "
              f"their verdict")
    if rejudged:
        print(f"re-judged         {len(rejudged)} stored rendering(s) changed "
              f"verdict under the CURRENT guard "
              f"({sum(1 for _, _, ok in rejudged if not ok)} admitted -> held, "
              f"{sum(1 for _, _, ok in rejudged if ok)} held -> admitted)")

    if dry_run:
        print("\n--dry-run: nothing was called and nothing was written."
              + ("\n  Re-run without --dry-run to persist the promotion(s) "
                 "above." if promoted or rejudged else ""))
        return 0
    # A run that was ASKED to do something and plans nothing must say so. The
    # 2026-08-16 probe passed `--model chat-strong --limit 3`, planned zero
    # calls because every row already existed, and printed a clean report that
    # looked like a successful model test. Nothing was wrong and nothing had
    # been measured — which is the shape of failure this repository keeps
    # paying for, in its cheapest form.
    if not plan and (model != DEFAULT_CHAT_MODEL or only_lang):
        # Built from the flags actually passed. The first version of this
        # message hardcoded "neither --attempt-all nor --redo-held was passed"
        # and printed it at a run that HAD passed --redo-held — the second
        # message in two days to state something the run knew to be false.
        if redo_held:
            why = ("--redo-held was passed and nothing is currently held, so "
                   "there was nothing to re-render.")
        elif attempt_all:
            why = ("--attempt-all was passed and no rendering matched the "
                   "filter, so there was nothing to attempt.")
        else:
            why = ("every wanted rendering is already on disk, and neither "
                   "--attempt-all nor --redo-held was passed:\n"
                   "    --attempt-all  one more attempt at every row, holding "
                   "the PROMPT fixed. Pair with --model.\n"
                   "    --redo-held    re-render only the held rows with the "
                   "RETRY prompt, holding the model fixed.\n"
                   "  One variable at a time: passing both makes an "
                   "improvement unattributable.")
        print(
            f"\nNOTHING WAS PLANNED, and something was asked for.\n"
            + (f"  --model {model} was given, but a model only applies to "
               f"renderings this run MAKES.\n" if model != DEFAULT_CHAT_MODEL
               else "")
            + (f"  --only-lang {only_lang} was given.\n" if only_lang else "")
            + f"  {why}"
        )

    if needs_upgrade:
        print(f"schema            {on_disk_schema} -> {SCHEMA}, rewritten "
              f"without spending a call")
    if not plan and not rejudged and not promoted and not needs_upgrade:
        print("\nnothing to do; the file is complete for this index.")
        return 0

    from answer.translate import (
        QUERY_PROMPT_VERSION,
        QUERY_RETRY_PROMPT_VERSION,
        TranslationError,
        render_query,
        resolve_model_label,
    )

    model_label = resolve_model_label(model)
    print(f"chat model        {model} -> {model_label}\n")
    renderings: dict[str, dict] = {q: dict(r) for q, r in existing.items()}
    done = 0
    failures = 0
    last_call = 0.0
    # Ruling 22's fail-fast. The first `--model chat-strong` run met a 400 the
    # model returns for EVERY call — temperature=0 is not supported — and would
    # have spent 205 renderings x 3 retries = 615 requests discovering it once.
    # It was stopped by hand at call 5. A systematic refusal is not a flaky
    # call, and the difference is whether the last few failures share a cause.
    ABORT_AFTER = 3
    consecutive: list[str] = []
    aborted = ""

    for query, query_lang, target in plan:
        if limit is not None and done >= limit:
            break
        if aborted:
            break
        if pace:
            waited = pace - (time.monotonic() - last_call)
            if waited > 0:
                time.sleep(waited)
        last_call = time.monotonic()
        done += 1

        try:
            # Ruling 20: a re-render is a RETRY prompt, not the same prompt
            # again. `_chat` is at temperature=0, so re-issuing the original
            # would return the same wrong-script string while reading like a
            # second attempt.
            # ONE VARIABLE AT A TIME. `--redo-held` changes the PROMPT and
            # holds the model; `--attempt-all` changes the MODEL and holds the
            # prompt. Doing both at once would produce a file whose Old Tamil
            # improvement could not be attributed to either, and the retry
            # prompt has already been measured making Tamil worse.
            result = render_query(query, query_lang, target, model=model,
                                  retry=redo_held and not attempt_all)
        except TranslationError as exc:
            # Recorded, not raised. 204 good renderings and one refusal is a
            # file worth keeping; losing them to an exception on the last call
            # is the failure this repository has already paid for twice.
            failures += 1
            cause = str(exc)[:160]
            row = renderings.setdefault(query, {}).setdefault(
                target, {"attempts": []})
            # One failure attempt per row, not one per run. A call that never
            # produced text is evidence that it was tried; five copies of it
            # are noise, and `best_attempt` would have to sort past them.
            if not any(a.get("call_failed") for a in row["attempts"]):
                row["attempts"].append({
                    "text": "",
                    "ok": False,
                    "call_failed": True,
                    "problems": [f"call failed: {cause}"],
                    "notes": [],
                    "prompt_version": (QUERY_RETRY_PROMPT_VERSION if redo_held
                                       else QUERY_PROMPT_VERSION),
                    "chat_model": model_label,
                })
            settle(row, target, query)
            consecutive.append(cause)
            if (len(consecutive) >= ABORT_AFTER
                    and len(set(consecutive[-ABORT_AFTER:])) == 1):
                aborted = cause
            print(f"  {done:3d}/{len(plan)}  {target:8.8s}  CALL FAILED  {exc}",
                  flush=True)
            continue

        # APPENDED, never assigned. The ruling-20 retry pass overwrote seven Old
        # Tamil renderings with worse ones and the better strings were gone; a
        # row keeps every attempt and `settle` promotes the best, so a retry can
        # only ever improve the file.
        row = renderings.setdefault(query, {}).setdefault(target, {"attempts": []})
        before = row.get("text")
        row["attempts"].append({
            "text": result.text,
            "notes": result.notes,
            # Per row, not only per file: after a retry or a model swap the file
            # holds more than one provenance and "which rows came from which" is
            # the first question anybody asks of it.
            "prompt_version": result.prompt_version,
            "chat_model": model_label,
            # Ruling 22. A rendering sampled at 1.0 and one decoded at 0.0 are
            # not the same measurement, and only this column says which it was.
            "temperature": result.temperature,
        })
        consecutive.clear()
        settle(row, target, query)
        flag = "ok  " if row["ok"] else "HELD"
        # INVERTED until 2026-08-16, and it inverted the reading of a whole run:
        # the condition fires when the text CHANGED, which is when the new
        # attempt WON. Sixteen rows that Sonnet fixed printed "kept the earlier
        # attempt, this one was worse". The promotion itself was correct and
        # mutation-verified; only the sentence about it was wrong, which is the
        # cheapest kind of lie and the easiest to believe.
        if before is None:
            kept = ""
        elif before == row["text"]:
            kept = "  <- kept the earlier attempt; this one was no better"
        else:
            kept = "  <- PROMOTED over the earlier attempt"
        print(f"  {done:3d}/{len(plan)}  {target:8.8s}  {flag}  "
              f"{row['text'][:56]}{kept}", flush=True)

    doc = {
        "schema": SCHEMA,
        "built": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+0000"),
        "prompt_version": QUERY_PROMPT_VERSION,
        # THIS RUN's model, and it speaks only for the renderings this run
        # made. `chat_models_in_file` is derived from the rows and is the
        # honest statement about the file as a whole.
        "chat_model_this_run": model_label,
        "chat_models_in_file": sorted({
            str(r.get("chat_model")) for rows in renderings.values()
            for r in rows.values()
        }),
        "view": view,
        "index_langs": langs,
        "about": (
            "C2 query renderings, Block C rulings 12/15b/17a/19. Keyed on query "
            "TEXT and holding no pair id, so a per-pair target language cannot "
            "be recorded here: the language set comes from index_langs and the "
            "query's own language, and from nothing about the answer. Every "
            "rendering is script-checked; ok:false rows are kept as evidence "
            "and are never embedded. Read from disk by every ranking run, whose "
            "archived report records this file's content hash — two runs on "
            "different days are the same configuration only if that hash is. "
            "RULING 23a, and it travels with any per-language number taken from "
            "this file: the selection regime is NOT uniform. Old Tamil rows were "
            "drawn twice (haiku, then chat-strong) and promoted by the "
            "gold-blind script guard; every other language was drawn once. "
            "`attempt_count` per row is the record of that, and a per-language "
            "comparison must say so."
        ),
        "queries": [
            {"query": q, "query_lang": queries[q], "renderings": renderings[q]}
            for q in sorted(renderings)
            if q in queries
        ],
    }
    write_atomically(path, doc)

    held = [(q, lang, row["problems"])
            for q, entry in renderings.items()
            for lang, row in entry.items() if not row["ok"]]

    if aborted:
        print(f"\nSTOPPED after {ABORT_AFTER} consecutive failures with one "
              f"cause. {done} of {len(plan)} attempted; everything that "
              f"succeeded is in the file below.\n  {aborted}")

    print(f"\nwrote {path}")
    print(f"{sum(len(e) for e in renderings.values())} renderings, "
          f"{len(held)} held back, {failures} call failure(s)")
    if held:
        print("\nHELD BACK — review these before committing:")
        for q, lang, problems in sorted(held)[:40]:
            print(f"  {lang:8.8s} {q[:44]!r}")
            for problem in problems:
                print(f"           {problem}")
    print(
        "\nReview the renderings before committing. Ruling 17(d): a translated "
        "query that succeeds proves the pipeline works, not that the retriever "
        "is cross-lingual."
    )
    return 1 if aborted else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--view", default=DEFAULT_VIEW)
    parser.add_argument("--out", default=str(DEFAULT_PATH), type=str)
    parser.add_argument("--dry-run", action="store_true",
                        help="print the plan and the cost; call nothing")
    parser.add_argument("--limit", type=int, default=None,
                        help="stop after N calls; the file is still written")
    parser.add_argument("--pace", type=float, default=0.0,
                        help="minimum seconds between calls")
    parser.add_argument("--model", default=None,
                        help="gateway alias for the chat model. The default is "
                             "`chat-default`, which gateway/config.yaml points "
                             "at claude-haiku-4-5 and its own comment calls "
                             "'cheap for the hello test'. Every rendering so far "
                             "was made by it, so a language it renders badly has "
                             "not been tested on anything else.")
    parser.add_argument("--only-lang", default=None,
                        help="restrict this run to one target language. A "
                             "filter on the language SET, never on pairs — "
                             "ruling 12 is untouched. `--only-lang oty "
                             "--attempt-all --model chat-strong` is the "
                             "sharpest available test of whether Old Tamil is "
                             "a model-tier problem, for 29 calls.")
    parser.add_argument("--attempt-all", action="store_true",
                        help="make one more attempt at EVERY rendering, held or "
                             "not, keeping all of them. Safe by construction "
                             "since ruling 21: an attempt that comes back worse "
                             "is stored as evidence and never promoted. This is "
                             "the model-comparison path — pair it with --model "
                             "and it holds the prompt fixed.")
    parser.add_argument("--redo-held", action="store_true",
                        help="re-render the rows the guard held back, keeping "
                             "every admitted one. This is the ruling-20 path: a "
                             "raised floor re-judges the file on load, and this "
                             "flag pays only for what it newly refused.")
    parser.add_argument("--refresh", action="store_true",
                        help="re-render everything, discarding what is on disk. "
                             "This invalidates comparability with any run made "
                             "against the old file — bump QUERY_PROMPT_VERSION "
                             "rather than refreshing silently.")
    args = parser.parse_args(argv)

    try:
        return build(args.view, pathlib.Path(args.out), dry_run=args.dry_run,
                     limit=args.limit, pace=args.pace, refresh=args.refresh,
                     redo_held=args.redo_held, attempt_all=args.attempt_all,
                     model=args.model or DEFAULT_CHAT_MODEL,
                     only_lang=args.only_lang)
    except RenderingError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
