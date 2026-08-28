"""Part 8: run every gold question under several prompt versions, repeatedly.

Why a sweep and not thirty invocations
--------------------------------------

Three things this does that a shell loop over `run_answer` would not:

1. **Each question is embedded once**, and the vector is reused across every
   prompt version and every repetition. Voyage's free tier is 3 requests/minute
   and the embedding depends on the question alone, so a 5 x 2 x 3 sweep costs 5
   embedding requests rather than 30. The chat calls cannot be shared — each is a
   different prompt or a different sample — so 30 remain 30.

2. **The evidence is built once per question.** Retrieval, folding and English
   resolution do not depend on the prompt, and rebuilding them per run would let
   an unrelated change move underneath the comparison. Holding them fixed is what
   makes prompt version the only variable.

3. **Questions come from the gold set**, so the sweep cannot drift from the
   harness that scores it. Adding a case adds it here.

What it is for
--------------

Part 8 owes two things: a prompt decision, and a floor. The archived grid says
v2 beat v3 on content, but every cell is a single shot, and Part 6 measured a
0.317 chrF spread within one case at temperature 0 while Part 7 watched a
rewording flip an exit code. A threshold set from single shots is one sample of a
distribution nobody has looked at.

So this prints the distribution, per case and per prompt version, and marks
UNSTABLE anything that lands differently across its own repetitions. A floor goes
where no observed case straddles it — the Part 6 rule — and this is what shows
where that is.

Usage (repo root, venv active, .env loaded, gateway up on :4000, db up):

    python -m eval.run_answer_sweep --dry-run
    python -m eval.run_answer_sweep --prompt-version p7-answer-v4 --repeat 1
    python -m eval.run_answer_sweep \
        --prompt-version p7-answer-v2r --prompt-version p7-answer-v4 --repeat 3

Cost: one embedding per question, one chat call per (question, prompt, repeat).
`--dry-run` spends the embeddings only and makes no chat call, which is the
cheapest way to find out that something is wrong before spending 30 of them.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import statistics
import sys
import time
from pathlib import Path

from answer import answer_store, assemble, translate
from answer.run_answer import _archive
from eval import answer_eval
from eval.answer_eval import (SESSION_DATE_BASIS, close_session,
                              session_identity)
from eval.goldset import (GoldSetError, load_answer_cases,
                          load_floor, load_profiles)

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

SWEEP_DIR = Path(__file__).resolve().parent / "sweeps"

# D4's session identity lives in eval/answer_eval.py, not here. It is pure, it
# is what eval/calibrate_floor.py counts dates from, and this module imports
# `answer` and `ingest` — so a check on it that lived here could not run in the
# offline suite that has no database and no gateway.


def _resolved(answer) -> int:
    return sum(1 for s in answer.grounding.quote_spans if s.abs_start is not None)


def run_sweep(conn, cases, prompt_versions: list[str], repeat: int,
              k: int, max_sources: int, profiles: dict, pause: float,
              dry_run: bool, write: bool, session: dict,
              progress: bool = False) -> dict:
    from ingest.embed import EmbeddingError, embed_query, resolve_model_label

    model_label = translate.resolve_model_label()
    embed_model = resolve_model_label()
    results: list[dict] = []
    evidence_report: list[dict] = []

    # Block E correction 5, 2026-08-28. A 99-call sweep took ten minutes and
    # showed the operator NOTHING until it exited: `*>` redirects every stream
    # and Python buffers stdout when it is not a terminal, so the console is
    # dead either way. Days 1, 2 and 3 were all watched by counting archives
    # from a second window, which works and should not have been necessary.
    #
    # stderr, and flush=True, both on purpose. `*>` still captures everything,
    # so a redirected run loses nothing; an ordinary run becomes watchable; and
    # a run piped somewhere keeps its progress out of the data on stdout.
    #
    # NOT applied before day 3: the redirect was itself under observation as
    # FINDING 10's guard on the answer path, and changing the invocation on the
    # one day whose purpose was to replicate the other two would have made its
    # capture the only one produced a different way.
    total_cells = len(cases) * len(prompt_versions) * repeat
    done = 0

    def _tick(case_id: str, version: str, attempt: int, outcome: str) -> None:
        nonlocal done
        done += 1
        if not progress:
            return
        print(f"[{done:>4}/{total_cells}] {outcome:<6} {case_id} "
              f"{version} run {attempt}/{repeat}", file=sys.stderr, flush=True)

    # FINDING 14, 2026-08-24. D1 made run_answer record the corpus version in
    # the answers row and the per-run archive, and this file was never given
    # the same treatment: it builds its own payload, never set
    # answer.corpus_version, and so wrote NULL into seed_corpus_digest and no
    # key into the archive. Zero of the sixty sweep runs on disk carry one.
    #
    # That is the whole of TASK 1 missing from the harness TASK 1 was for:
    # "Block E's whole claim is that the corpus did not move under the sweep,
    # and right now nothing in an archive would say if it had." Block E is
    # ~270 calls and every one of them comes through here.
    #
    # Read once before the loop, exactly as run_answer does, so that every run
    # in this sweep is made against one corpus BY CONSTRUCTION rather than by
    # hope. It is read again after the last call — see below.
    corpus_version = answer_store.corpus_version(conn)

    # Block E, 2026-08-26. Extracted so that ONE call can fail without taking
    # the day with it.
    #
    # `run_sweep` caught EmbeddingError and returned cleanly, and left the chat
    # call unguarded. `_chat` gives up after MAX_RETRIES=3 — for an
    # unclassified provider error that is 2s + 4s, so six seconds of trouble is
    # enough — and TranslationError then propagated out of main(). It died
    # AFTER writing N per-run archives and BEFORE writing the sweep archive
    # that ties them together: exactly the orphan state this runbook warns
    # about from Ctrl-C, reachable without touching Ctrl-C.
    #
    # D4's 18-call pilot never went near it. A Block E day is 99 calls over
    # half an hour of continuous calling, and PHASE2_PLAN item 4 says the days
    # are the scarce resource, not the calls.
    def _one_run(case, passages, version, attempt) -> dict:
        answer = assemble.assemble(
            case.question, passages,
            model_label=model_label, profiles=profiles,
            prompt_version=version,
        )
        answer.embedding_model = embed_model
        answer.retrieval_k = k
        # FINDING 14. Without this line assemble.store writes NULL to
        # seed_corpus_digest and to cited_record_hashes, because it
        # reads `(answer.corpus_version or {})`.
        answer.corpus_version = corpus_version

        stored_id = assemble.store(conn, answer) if write else None
        payload = {
            "timestamp": _dt.datetime.now(_dt.timezone.utc)
                            .isoformat(timespec="seconds"),
            "question": answer.question,
            "answer": answer.answer_text,
            "grounded": answer.grounding.ok,
            "refused": answer.refused,
            "model": answer.model,
            # Block E decision 3. `model` is the alias this repository
            # SENT and cannot move; this is what the gateway said it
            # served. Absent keys are omitted rather than written null,
            # so an empty dict here is itself the finding.
            "serving_stack": answer.serving_stack,
            "prompt_version": answer.prompt_version,
            "embedding_model": answer.embedding_model,
            "answer_id": stored_id,
            "grounding": answer.grounding.to_dict(),
            "passages": [p.to_dict() for p in answer.passages],
            "sources_block": answer.sources_block,
            "sweep": {"case": case.id, "repetition": attempt,
                      "of": repeat},
            # D4. In the PER-RUN archive as well as the sweep file,
            # because eval/answer_runs/ is the durable evidence — the
            # sweep summary is rebuilt from it by rescore_sweep, and a
            # run whose session lived only in the summary would lose it
            # the first time a sweep was re-scored from the archives.
            "session": session,
            # FINDING 14. The same key run_answer writes, so that a
            # sweep run and a single run can be read by one reader —
            # ui/build_ui_data.py already does `run.get(
            # "corpus_version")` and until now got None for every
            # sweep-archived answer there has ever been.
            "corpus_version": corpus_version,
        }
        archived = _archive(payload) if write else None

        scored = answer_eval.score_payload(
            case, payload, source=archived or f"{case.id}/{version}/{attempt}"
        )
        row = {
            "case": case.id,
            "prompt_version": version,
            "repetition": attempt,
            # Denormalised onto the row on purpose: `summarise` groups
            # by it, and a summary that had to look the session up
            # elsewhere could be built over rows from two sessions
            # without noticing.
            "session_id": session["id"],
            "session_date": session["date"],
            "content_ok": scored.ok,
            "grounded": answer.grounding.ok,
            "refused": answer.refused,
            "resolved_quotes": _resolved(answer),
            # On the ROW as well as in the per-run archive, because the
            # variance decomposition reads rows. A stack that changed
            # between day 1 and day 3 is the difference between "the
            # session term is the day" and "the session term is a
            # deployment", and only a per-row value can say which.
            "serving_stack": answer.serving_stack,
            "answer": answer.answer_text,
            "failures": [a.label for a in scored.failures],
            "archived": archived,
        }
        mark = "PASS" if scored.ok else "FAIL"
        print(f"  {mark}  {version:<14} run {attempt}/{repeat}  "
              f"grounded={answer.grounding.ok!s:<5} "
              f"quotes={_resolved(answer)}")
        return row

    # Named, never counted. A cell that failed is a hole in the grid, and
    # eval/answer_eval.decompose_verdicts REFUSES an incomplete grid rather
    # than apportioning the hole to whichever term absorbs it.
    failed: list[dict] = []
    retried: list[dict] = []
    evidence_by_case: dict[str, list] = {}
    case_by_id = {c.id: c for c in cases}

    for case in cases:
        try:
            query_vector = embed_query(case.question)
        except EmbeddingError as exc:
            print(f"could not embed {case.id!r}: {exc}", file=sys.stderr)
            return {"error": str(exc)}

        passages = assemble.build_evidence(
            conn, query_vector, k=k, max_sources=max_sources, profiles=profiles,
        )
        evidence_report.append({
            "case": case.id,
            "passages": len(passages),
            "markers": [p.marker for p in passages],
            "chunks": [p.chunk_id for p in passages],
            "english_kinds": sorted({p.english.kind for p in passages}),
        })
        print(f"\n{case.id}: {len(passages)} source(s) — "
              f"{', '.join(sorted({p.english.kind for p in passages}))}")

        if dry_run:
            # Which passages, not merely how many. The Aksum question is the
            # reason: four archived answers refuse, and the only way to know
            # whether that is a retrieval failure or a reasoning one is to see
            # whether the passage carrying the answer is in the set and what
            # English is attached to it. A count cannot tell you that, and three
            # of Part 7's defects were found by looking at a dry run.
            for passage in passages:
                english = passage.english
                marker = f"[{passage.marker}]"
                print(f"    {marker:<5} {passage.chunk_id}")
                print(f"          sim {passage.similarity:.3f} | "
                      f"english={english.kind}"
                      + (f" ground={english.ground}" if english.ground else "")
                      + (f" band={english.band}" if english.band else ""))
                # The expectation the gold case makes of this question, checked
                # against the evidence before any chat call is paid for.
                for needle in (case.expect_answer_contains
                               + [w for group in case.expect_answer_contains_any
                                  for w in group]):
                    if english.text and needle.casefold() in english.text.casefold():
                        print(f"          gold term {needle!r} IS PRESENT in "
                              f"this passage's English")
            continue

        if not passages:
            continue

        evidence_by_case[case.id] = passages
        for version in prompt_versions:
            for attempt in range(1, repeat + 1):
                try:
                    results.append(
                        _one_run(case, passages, version, attempt))
                    _tick(case.id, version, attempt, "ok")
                except Exception as exc:  # noqa: BLE001 — provider errors are untyped
                    # Not re-raised, and not swallowed. The remaining cases are
                    # still worth measuring, and abandoning here would GUARANTEE
                    # the loss the retry below usually prevents.
                    failed.append({
                        "case": case.id, "prompt_version": version,
                        "repetition": attempt,
                        "error": f"{type(exc).__name__}: {exc}"[:300],
                    })
                    # The provider's own words, truncated. "RuntimeError"
                    # alone sends a reader to debug the harness, which is the
                    # same misdirection FINDING 15's true-but-wrong report made.
                    _tick(case.id, version, attempt, "FAILED")
                    print(f"  FAILED {version:<14} run {attempt}/{repeat}  "
                          f"{type(exc).__name__}: {str(exc)[:120]}"
                          f" — will retry once at the end")
                if pause:
                    time.sleep(pause)

    # One retry each, at the end, over the SAME evidence block — retrieval and
    # folding do not depend on the prompt and were built once per case, so a
    # retry is the same measurement and not a new one. It is recorded as a
    # retry on the row either way: a run that had to be asked twice must never
    # be indistinguishable from one that did not.
    #
    # At the end rather than in place, because whatever made the call fail is
    # likelier to have passed in ten minutes than in six seconds.
    if failed and not dry_run:
        print(f"\n{len(failed)} call(s) failed. Retrying each ONCE, over the "
              f"same evidence.")
        if progress:
            print(f"[retry] {len(failed)} cell(s), over the same evidence",
                  file=sys.stderr, flush=True)
        still: list[dict] = []
        for item in failed:
            case = case_by_id[item["case"]]
            try:
                row = _one_run(case, evidence_by_case[case.id],
                               item["prompt_version"], item["repetition"])
            except Exception as exc:  # noqa: BLE001
                item["retry_error"] = f"{type(exc).__name__}: {exc}"[:300]
                still.append(item)
                print(f"  STILL FAILED {case.id} run {item['repetition']}")
                continue
            row["retried_after_failure"] = item["error"]
            results.append(row)
            retried.append(item)
        failed = still

    # FINDING 14, the second half. A version captured only at the start records
    # what the sweep BEGAN against, which is a different sentence from the one
    # Block E needs to be able to say. Re-read after the last chat call, and
    # compared: a corpus that moved under a half-hour sweep splits it into two
    # measurements of two different corpora, and on 2026-08-22 the digest moved
    # three times in one day.
    #
    # Cheap: one query over the seed record hashes, twice, against ~90 chat
    # calls.
    corpus_version_after = answer_store.corpus_version(conn) if not dry_run \
        else corpus_version
    # Distinct, sorted, and named — the same treatment corpus_version gets at
    # both ends of the sweep, and for the same reason: the claim Block E makes
    # is that nothing moved underneath it.
    # Block E corrections 3 and 4, 2026-08-28. Counted over the stack
    # IDENTITY, not the recorded stack: `id` is unique per call and `model` is
    # the echo of the string sent, so counting the raw dicts reported one
    # distinct stack per call — 99 on a 99-call day — under a heading that
    # reads like a provider changing mid-run. Both are still on every row and
    # in every per-run archive. An EMPTY identity is dropped rather than
    # counted as one stack: on this gateway every identity is empty, and
    # "nothing distinguishing" is decision 3a's answer, not "one, unchanged".
    stacks = sorted({json.dumps(identity, sort_keys=True, ensure_ascii=False)
                     for identity in (
                         translate.serving_stack_identity(row.get("serving_stack"))
                         for row in results)
                     if identity})
    return {
        "results": results,
        "serving_stacks": [json.loads(s) for s in stacks],
        # A sweep with a hole in it is not a shorter sweep. Both are NAMED so
        # that the archive states which cells never returned rather than a
        # reader inferring it from a row count.
        "incomplete": failed,
        "retried": retried,
        "evidence": evidence_report,
        "corpus_version": corpus_version,
        "corpus_version_after": corpus_version_after,
        "corpus_moved": answer_eval.corpus_moved(corpus_version,
                                                 corpus_version_after),
    }


# --------------------------------------------------------------------------
# Reading the distribution
# --------------------------------------------------------------------------

def summarise(results: list[dict]) -> dict:
    by_key: dict[tuple[str, str], list[dict]] = {}
    for row in results:
        by_key.setdefault((row["case"], row["prompt_version"]), []).append(row)

    cells = []
    for (case_id, version), rows in sorted(by_key.items()):
        content = {r["content_ok"] for r in rows}
        grounded = {r["grounded"] for r in rows}
        texts = {r["answer"].strip() for r in rows}
        quotes = [r["resolved_quotes"] for r in rows]
        cells.append({
            "case": case_id,
            "prompt_version": version,
            "n": len(rows),
            "content_pass": sum(1 for r in rows if r["content_ok"]),
            "content_stable": len(content) == 1,
            "grounded_pass": sum(1 for r in rows if r["grounded"]),
            "grounded_stable": len(grounded) == 1,
            "distinct_texts": len(texts),
            "quotes_min": min(quotes) if quotes else 0,
            "quotes_max": max(quotes) if quotes else 0,
            "refusal_rate": sum(1 for r in rows if r["refused"]) / len(rows),
        })

    by_version: dict[str, dict] = {}
    for version in sorted({c["prompt_version"] for c in cells}):
        mine = [c for c in cells if c["prompt_version"] == version]
        runs = [r for r in results if r["prompt_version"] == version]
        by_version[version] = {
            "cases": len(mine),
            "runs": len(runs),
            "content_pass_rate": sum(r["content_ok"] for r in runs) / len(runs),
            "grounded_rate": sum(r["grounded"] for r in runs) / len(runs),
            "refusal_rate": sum(r["refused"] for r in runs) / len(runs),
            "unstable_content_cells": sum(1 for c in mine if not c["content_stable"]),
            "unstable_grounded_cells": sum(1 for c in mine
                                           if not c["grounded_stable"]),
            "mean_resolved_quotes": statistics.mean(
                [r["resolved_quotes"] for r in runs]) if runs else 0.0,
        }
    return {"cells": cells, "by_version": by_version}


def print_summary(summary: dict) -> None:
    print("\n" + "=" * 72)
    print("per cell — case x prompt version, across repetitions")
    print("=" * 72)
    print(f"  {'case':<20} {'prompt':<15} {'content':<10} {'grounded':<10} "
          f"{'quotes':<9} texts")
    for cell in summary["cells"]:
        content = f"{cell['content_pass']}/{cell['n']}"
        if not cell["content_stable"]:
            content += " !"
        grounded = f"{cell['grounded_pass']}/{cell['n']}"
        if not cell["grounded_stable"]:
            grounded += " !"
        quotes = (f"{cell['quotes_min']}" if cell["quotes_min"] == cell["quotes_max"]
                  else f"{cell['quotes_min']}-{cell['quotes_max']}")
        print(f"  {cell['case']:<20} {cell['prompt_version']:<15} "
              f"{content:<10} {grounded:<10} {quotes:<9} {cell['distinct_texts']}")
    print("\n  ! = the metric landed differently across repetitions of an "
          "identical run.\n  A floor must not sit where a case straddles it "
          "(the Part 6 threshold rule).")

    print("\n" + "=" * 72)
    print("per prompt version")
    print("=" * 72)
    for version, stats in summary["by_version"].items():
        print(f"\n  {version}  ({stats['runs']} runs over {stats['cases']} cases)")
        print(f"    content pass rate  {stats['content_pass_rate']:.0%}")
        print(f"    grounded rate      {stats['grounded_rate']:.0%}")
        print(f"    refusal rate       {stats['refusal_rate']:.0%}")
        print(f"    mean resolved quotations  {stats['mean_resolved_quotes']:.1f}")
        print(f"    unstable cells: content {stats['unstable_content_cells']}, "
              f"grounded {stats['unstable_grounded_cells']}")

    versions = list(summary["by_version"])
    if len(versions) > 1:
        print("\n" + "=" * 72)
        print("the comparison")
        print("=" * 72)
        best = max(versions,
                   key=lambda v: summary["by_version"][v]["content_pass_rate"])
        for version in versions:
            stats = summary["by_version"][version]
            print(f"  {version:<15} content {stats['content_pass_rate']:.0%}  "
                  f"refusals {stats['refusal_rate']:.0%}  "
                  f"grounded {stats['grounded_rate']:.0%}")
        print(f"\n  Highest content pass rate: {best}.")
        print(
            "  Read refusal rate beside it, not after it. A prompt that refuses "
            "more\n  while erring no less is a regression, however tidy its "
            "citations — that\n  is the failure mode Part 8 was built to see, "
            "and the exit code cannot."
        )

    unstable = [c for c in summary["cells"]
                if not c["content_stable"] or not c["grounded_stable"]]
    print("\n" + "=" * 72)
    if unstable:
        print(f"{len(unstable)} unstable cell(s) — a floor placed on these "
              f"measures the sampler")
        for cell in unstable:
            print(f"  {cell['case']} / {cell['prompt_version']}: "
                  f"content {cell['content_pass']}/{cell['n']}, "
                  f"grounded {cell['grounded_pass']}/{cell['n']}")
    else:
        print("No unstable cells: every case landed the same way in every "
              "repetition.\nA floor set here is measuring the pipeline, not the "
              "sampler.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Part 8 — sweep gold questions across prompt versions"
    )
    parser.add_argument("--prompt-version", action="append", dest="prompt_versions",
                        choices=sorted(assemble.ANSWER_PROMPTS),
                        help="repeatable; defaults to the current version")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--case", action="append", help="only these case ids")
    parser.add_argument("--k", type=int, default=assemble.DEFAULT_K)
    parser.add_argument("--max-sources", type=int,
                        default=assemble.DEFAULT_MAX_SOURCES)
    parser.add_argument("--pause", type=float, default=0.0,
                        help="seconds between chat calls, if the account needs it")
    parser.add_argument("--dry-run", action="store_true",
                        help="embed and retrieve, make no chat call")
    parser.add_argument("--no-write", action="store_true",
                        help="do not store answers or archive runs")
    parser.add_argument("--session-label", default="",
                        help="a note attached to this session's identity, e.g. "
                             "'D4 pilot day 1'. The session id and UTC date "
                             "are recorded whether or not this is given.")
    parser.add_argument("--progress", action="store_true",
                        help="one line per completed cell to stderr, flushed. "
                             "A redirected run still captures everything; a "
                             "plain run becomes watchable. Block E correction "
                             "5.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.repeat < 1:
        parser.error("--repeat must be at least 1")
    versions = args.prompt_versions or [assemble.ANSWER_PROMPT_VERSION]

    try:
        cases = load_answer_cases()
        profiles = load_profiles()
    except GoldSetError as exc:
        print(f"gold set will not load: {exc}", file=sys.stderr)
        return 2
    if args.case:
        cases = [c for c in cases if c.id in set(args.case)]
        if not cases:
            print("no matching case ids", file=sys.stderr)
            return 2

    session = session_identity(args.session_label)

    chat_calls = 0 if args.dry_run else len(cases) * len(versions) * args.repeat
    print(f"{len(cases)} question(s) x {len(versions)} prompt version(s) x "
          f"{args.repeat} repetition(s)")
    print(f"cost: {len(cases)} embedding request(s), {chat_calls} chat call(s)")
    if versions:
        print(f"prompts: {', '.join(versions)}")
    print(f"session: {session['id'][:12]}  {session['date']} "
          f"({SESSION_DATE_BASIS})"
          + (f"  {session['label']}" if session["label"] else ""))

    import psycopg

    try:
        from ingest.db import check_connection
        problem = check_connection(answer_store.get_dsn())
    except Exception:  # noqa: BLE001
        problem = None
    if problem:
        print(problem, file=sys.stderr)
        return 2

    with psycopg.connect(answer_store.get_dsn()) as conn:
        answer_store.apply_schema(conn)
        outcome = run_sweep(
            conn, cases, versions, args.repeat, args.k, args.max_sources,
            profiles, args.pause, args.dry_run, write=not args.no_write,
            session=session, progress=args.progress,
        )

    if "error" in outcome:
        return 2
    version = outcome.get("corpus_version") or {}
    print(f"\ncorpus: {version.get('seed_record_count', '?')} seed record(s), "
          f"digest {(version.get('seed_corpus_digest') or '?')[:16]}… "
          f"({version.get('source', '?')})")

    stacks = outcome.get("serving_stacks") or []
    if not args.dry_run:
        if not stacks:
            print("serving stack: the gateway returned nothing distinguishing "
                  "beside the model alias.\n  Recorded as absent. Provider "
                  "drift and sampling variance remain indistinguishable\n  in "
                  "these archives, and that is a stated limit rather than an "
                  "oversight.")
        elif len(stacks) == 1:
            print(f"serving stack: one, unchanged across the sweep - "
                  f"{json.dumps(stacks[0], ensure_ascii=False)}")
        else:
            # Not an error, and not silently averaged. A sweep served by two
            # stacks is two measurements, and the reader has to be told.
            print(f"serving stack: {len(stacks)} DISTINCT stacks served this "
                  f"sweep:")
            for stack in stacks:
                print(f"    {json.dumps(stack, ensure_ascii=False)}")

    if args.dry_run:
        print("\ndry run — no chat call made, nothing written")
        if args.json:
            print(json.dumps(outcome["evidence"], indent=2, ensure_ascii=False))
        return 0

    results = outcome["results"]
    if not results:
        print("no runs completed", file=sys.stderr)
        return 2

    summary = summarise(results)
    # Block E. A floor verdict on an incomplete sweep would be a floor met on a
    # DIFFERENT DENOMINATOR from the one it was set on, printed in the same
    # words. So it is not computed at all — `None` in the archive, and a named
    # refusal in the report. `max_unstable_content_cells` already refuses a
    # floor that has stopped being measurable; this is the same rule one level
    # up.
    incomplete = outcome.get("incomplete") or []
    verdicts = ({} if incomplete
                else answer_eval.check_floor(summary, load_floor(), args.repeat))

    session = close_session(session)
    if session["crossed_midnight_utc"]:
        print(f"\n  NOTE: this session began on {session['date']} "
              f"{SESSION_DATE_BASIS} and finished on the next date. It is one "
              f"session and is counted under the date it began — recorded so "
              f"that a sweep spanning midnight cannot be read as two days.")

    if not args.no_write:
        SWEEP_DIR.mkdir(parents=True, exist_ok=True)
        stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
        path = SWEEP_DIR / f"{stamp}-{'_'.join(versions)}-r{args.repeat}.json"
        path.write_text(json.dumps(
            {"prompt_versions": versions, "repeat": args.repeat,
             "session": session,
             # FINDING 14. Both ends, and the verdict, in the sweep file as
             # well as in every per-run archive — so that "the corpus did not
             # move under this sweep" is a fact the archive states rather than
             # one a reader reconstructs from ninety files.
             "serving_stacks": outcome.get("serving_stacks"),
             "corpus_version": outcome.get("corpus_version"),
             "corpus_version_after": outcome.get("corpus_version_after"),
             "corpus_moved": outcome.get("corpus_moved"),
             "results": results, "summary": summary,
             # Named, never counted, and never absent. A later reader must be
             # able to tell a sweep that ran clean from one that lost four
             # calls, without recounting rows.
             "incomplete": incomplete,
             "retried": outcome.get("retried") or [],
             "floor": verdicts or None},
            indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nsweep archived: {path}")

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print_summary(summary)
        # One sweep is one session, so the per-session number here is always
        # NOT MEASURED and says so rather than printing 100%. It becomes a
        # number under `python -m eval.calibrate_floor`, which reads every
        # archive. Printed anyway, because a sweep that showed only a
        # within-session figure with nothing naming it as such is how three
        # archived sweeps came to be read as a calibrated floor.
        answer_eval.print_stability(answer_eval.stability(results))
        retried = outcome.get("retried") or []
        if retried:
            print(f"\n  {len(retried)} call(s) failed once and succeeded on "
                  f"the retry. Each carries\n  `retried_after_failure` on its "
                  f"row — a run that had to be asked twice is\n  never "
                  f"indistinguishable from one that did not.")
            for item in retried:
                print(f"    {item['case']} run {item['repetition']}: "
                      f"{item['error'][:80]}")
        if incomplete:
            print("\n" + "=" * 72)
            print(f"INCOMPLETE — {len(incomplete)} cell(s) never returned, "
                  f"after one retry each")
            print("=" * 72)
            for item in incomplete:
                print(f"  {item['case']} / {item['prompt_version']} run "
                      f"{item['repetition']}")
                print(f"      first  {item['error'][:100]}")
                print(f"      retry  {item.get('retry_error', '')[:100]}")
            print(
                "\n  No floor verdict is printed and none is archived. The "
                "runs that DID\n  complete are real and are archived; they are "
                "not a shorter sweep.\n  eval.decompose will refuse this day's "
                "grid by name for the same reason."
            )
        else:
            answer_eval.print_floor(verdicts)

    # FINDING 14. AFTER the archive is written and after the report is printed,
    # for the reason run_ranking_check archives before printing: on 2026-08-16 a
    # KeyError in a printer destroyed a twenty-six-minute run. The archived run
    # IS the evidence. So this returns non-zero on a sweep whose corpus moved
    # rather than raising — the runs are real, they are archived, they say so,
    # and they are not comparable to each other.
    # Ordered after the archive and after the report, for the reason the
    # comment above gives. An incomplete sweep exits 2 like a moved corpus:
    # the runs are real, they are archived, they say so, and they do not make
    # a measurement.
    if incomplete:
        return 2

    moved = outcome.get("corpus_moved")
    if moved:
        print("\n" + "=" * 72)
        print(moved)
        print("=" * 72)
        return 2

    return 0 if all(v["meets_floor"] for v in verdicts.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
