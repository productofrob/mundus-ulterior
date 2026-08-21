"""Part 7 entrypoint: ask a question, get a grounded answer.

Usage (repo root, venv active, .env loaded, gateway on :4000, db up):

    python -m answer.run_answer --dry-run "what did ships carry from Muziris?"
    python -m answer.run_answer "what did ships carry from Muziris?"
    python -m answer.run_answer --k 16 --max-sources 8 --region south_asia "..."
    python -m answer.run_answer --json "..." > answer.json
    python -m answer.run_answer --stats

Cost: one embedding request and one chat call per question. The embedding is the
constrained one — Voyage's free tier allows three requests a minute — so a
question costs one, and --dry-run costs one too, because the retrieval is the
part worth inspecting before spending a chat call.

Exit codes: 0 grounded, 1 answered but failed a grounding check, 2 could not run.
An ungrounded answer exits 1 and is still printed and still stored. Hiding it
would remove the only evidence Part 8 has to work from.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path as _Path

from answer import answer_store, assemble, cite, translate
from eval.goldset import load_profiles


def _print_evidence(passages, profiles) -> None:
    print(f"{len(passages)} source(s) after folding:\n")
    for passage in passages:
        chunk = passage.chunk
        english = passage.english
        print(
            f"  [{passage.marker}] {chunk.chunk_id}\n"
            f"       {chunk.citation}\n"
            f"       {chunk.region} | {chunk.lang} | "
            f"similarity {passage.similarity:.3f} | "
            f"english={english.kind}"
            + (f" band={english.band}" if english.band else "")
            + (f" ground={english.ground}" if english.ground else "")
        )
        if english.flags:
            print(f"       flags: {', '.join(english.flags)}")
        if english.kind == "none":
            print(f"       NO ENGLISH: {english.reason}")
        if passage.lang_note:
            print(f"       language note: {passage.lang_note}")
    print()


RUNS_DIR = _Path(__file__).resolve().parent.parent / "eval" / "answer_runs"


def _archive(payload: dict) -> str:
    """Write one run to `eval/answer_runs/`, never overwriting.

    `answers` is keyed on (question, model, prompt version, evidence), so asking
    the identical question twice updates the row in place. That is right for the
    table — it is a store of current answers — and wrong as the only record,
    because it silently destroys exactly the evidence Part 8 needs: three runs of
    the Vimose question under p7-answer-v3 produced three answers, two identical
    and one reworded, and all three landed on answer_id 3b4489a4. Part 6 learned
    this with `--repeat` and answered it with `eval/runs/`; this is the same
    answer for the same reason.
    """
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = payload["timestamp"].replace(":", "").replace("-", "")
    name = f"{stamp}-{(payload.get('answer_id') or 'unstored')[:8]}.json"
    path = RUNS_DIR / name
    counter = 2
    while path.exists():                      # same second, same answer
        path = RUNS_DIR / f"{name[:-5]}-{counter}.json"
        counter += 1
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return str(path)


def _print_grounding(report: cite.GroundingReport) -> None:
    print("grounding")
    print(
        f"  claim sentences {report.claim_sentences}, cited "
        f"{report.cited_sentences} (coverage {report.coverage:.0%})"
    )
    print(f"  markers cited: {', '.join(report.cited_markers) or 'none'}")
    print(
        f"  quotations verified: {len(report.quote_spans)}"
        + (
            f" ({sum(1 for s in report.quote_spans if s.abs_start is not None)} "
            f"resolved to characters on disk)"
            if report.quote_spans
            else ""
        )
    )
    for span in report.quote_spans:
        location = (
            f"{span.source_field}[{span.abs_start}:{span.abs_end}]"
            if span.abs_start is not None
            else f"{span.within}, no character span claimed ({span.match} match)"
        )
        print(f"    {span.marker} {span.quote[:52]!r} -> {location}")

    for label, items in (
        ("UNKNOWN MARKER", report.unknown_markers),
        ("UNCITED CLAIM", report.uncited_sentences),
        ("UNLABELLED MACHINE TRANSLATION", report.unlabelled_machine),
    ):
        for item in items:
            print(f"  {label}: {item}")
    for entry in report.unverified_quotes:
        print(f"  UNVERIFIED QUOTE cited {entry['cited']}: {entry['quote'][:80]!r}")
        print(f"      {entry['reason']}")
    for entry in report.quoted_metadata:
        print(
            f"  QUOTED METADATA cited {entry['cited']}: {entry['quote'][:80]!r}"
        )
        print(f"      {entry['reason']}")
    for entry in report.misattributed_quotes:
        print(
            f"  MISATTRIBUTED QUOTE: {entry['quote'][:60]!r} cited "
            f"{entry['cited']} but found in {entry['found_in']}"
        )
    for entry in report.claims_on_untranslated:
        print(f"  CLAIM ON UNTRANSLATED SOURCE {entry['marker']}: {entry['sentence']}")
        print(f"      {entry['reason']}")
    for note in report.notes:
        print(f"  note: {note}")


def _print_repetitions(runs: list[tuple], archived_paths: list[str]) -> None:
    """Report what moved across repetitions, and what did not.

    Part 6's `--repeat` found that a spread within one case can exceed the gap
    between two thresholds, and Part 7 found three runs of one question landing
    on a single answer_id with different text. So the two things worth printing
    are whether the VERDICT moved and whether the TEXT moved — a stable verdict
    over varying text is a usable metric; a verdict that flips on a rewording is
    not, and the Vimose triple flipped one on exactly that.
    """
    print(f"\n{len(runs)} repetition(s), same question, same evidence, "
          f"same prompt version\n")
    verdicts = {a.grounding.ok for a, _ in runs}
    texts = {a.answer_text.strip() for a, _ in runs}
    quote_counts = [
        sum(1 for s in a.grounding.quote_spans if s.abs_start is not None)
        for a, _ in runs
    ]

    for i, ((answer, stored_id), path) in enumerate(zip(runs, archived_paths or
                                                        [None] * len(runs)), 1):
        print(f"  {i}. {'grounded' if answer.grounding.ok else 'NOT grounded':<13}"
              f" quotes={quote_counts[i - 1]:<3} "
              f"{'refused' if answer.refused else ''}")
        print(f"     {answer.answer_text.strip()[:100]}")
        if path:
            print(f"     {path}")

    print()
    if len(verdicts) > 1:
        print("  VERDICT UNSTABLE — the same question, evidence and prompt "
              "produced different grounding verdicts. A floor set on this "
              "metric would be measuring the sampler.")
    else:
        print(f"  verdict stable across all {len(runs)} "
              f"({'grounded' if verdicts.pop() else 'not grounded'})")
    if len(texts) > 1:
        print(f"  {len(texts)} distinct answer text(s) — temperature 0 is not "
              f"determinism.")
    else:
        print("  answer text byte-identical across all repetitions")
    if len(set(quote_counts)) > 1:
        print(f"  resolved quotations vary: {min(quote_counts)}-{max(quote_counts)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Mundus Ulterior Part 7 — grounded answer with inline citations"
    )
    parser.add_argument("question", nargs="?", help="the question to answer")
    parser.add_argument("--k", type=int, default=assemble.DEFAULT_K,
                        help="passages retrieved before folding")
    parser.add_argument("--max-sources", type=int, default=assemble.DEFAULT_MAX_SOURCES,
                        help="passages shown to the model after folding")
    parser.add_argument("--lang", action="append", help="restrict to these chunk languages")
    parser.add_argument("--region", action="append", help="restrict to these regions")
    parser.add_argument("--dry-run", action="store_true",
                        help="retrieve and resolve English, make no chat call")
    parser.add_argument("--no-write", action="store_true",
                        help="answer but do not store it in Postgres")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument(
        "--prompt-version", default=assemble.ANSWER_PROMPT_VERSION,
        choices=sorted(assemble.ANSWER_PROMPTS),
        help="which answer prompt to use (default: %(default)s)",
    )
    parser.add_argument(
        "--repeat", type=int, default=1, metavar="N",
        help="ask the same question N times. Temperature 0 is not determinism: "
             "Part 6 measured a 0.317 chrF spread within one case, and Part 7 "
             "saw a rewording flip an exit code. One shot is one sample of a "
             "distribution nobody has looked at. The embedding is spent once; "
             "each repetition costs one further chat call.",
    )
    args = parser.parse_args(argv)

    if args.repeat < 1:
        parser.error("--repeat must be at least 1")

    if not args.question and not args.stats:
        parser.error("a question is required (or --stats)")

    import psycopg

    try:
        from ingest.db import check_connection

        problem = check_connection(answer_store.get_dsn())
    except Exception:  # noqa: BLE001 — ingest.db is optional to this module
        problem = None
    if problem:
        print(problem, file=sys.stderr)
        return 2

    profiles = load_profiles()

    with psycopg.connect(answer_store.get_dsn()) as conn:
        answer_store.apply_schema(conn)

        if args.stats:
            print(json.dumps(answer_store.stats(conn), indent=2, ensure_ascii=False))
            return 0

        from ingest.embed import EmbeddingError, embed_query, resolve_model_label

        try:
            query_vector = embed_query(args.question)
        except EmbeddingError as exc:
            print(f"could not embed the question: {exc}", file=sys.stderr)
            return 2
        embed_model = resolve_model_label()

        passages = assemble.build_evidence(
            conn,
            query_vector,
            k=args.k,
            max_sources=args.max_sources,
            langs=args.lang,
            regions=args.region,
            profiles=profiles,
        )

        if not args.json:
            print(f"question: {args.question}\n")
            _print_evidence(passages, profiles)

        if args.dry_run:
            if args.json:
                print(json.dumps(
                    {"question": args.question,
                     "passages": [p.to_dict() for p in passages]},
                    indent=2, ensure_ascii=False,
                ))
            else:
                print(cite.render_evidence(passages, profiles))
                print("\ndry run — no chat call made, nothing written")
            return 0

        if not passages:
            print(assemble.NO_ANSWER)
            return 1

        model_label = translate.resolve_model_label()

        # D1. Read ONCE, before the repetition loop: every repetition in this
        # invocation is made against the same corpus by construction, and
        # re-reading it per repetition would invite a run whose repetitions
        # disagree about what they were measured against.
        corpus_version = answer_store.corpus_version(conn)

        # The retrieval and its embedding are spent once; each repetition costs
        # one chat call. `answers` is keyed on (question, model, prompt, evidence)
        # and so holds one row however many times this loop runs — the run-to-run
        # evidence lives in eval/answer_runs/, which is the whole reason that
        # directory exists.
        runs: list[tuple] = []
        for attempt in range(args.repeat):
            try:
                answer = assemble.assemble(
                    args.question,
                    passages,
                    model_label=model_label,
                    profiles=profiles,
                    prompt_version=args.prompt_version,
                )
            except translate.TranslationError as exc:
                print(f"the answer call failed: {exc}", file=sys.stderr)
                return 2

            answer.embedding_model = embed_model
            answer.retrieval_k = args.k
            answer.corpus_version = corpus_version

            stored_id = None
            if not args.no_write:
                stored_id = assemble.store(conn, answer)
            runs.append((answer, stored_id))

            if args.repeat > 1 and not args.json:
                print(f"--- repetition {attempt + 1} of {args.repeat} "
                      f"({'grounded' if answer.grounding.ok else 'NOT grounded'})")

    payloads = []
    for answer, stored_id in runs:
        payloads.append({
            "timestamp": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "question": answer.question,
            "answer": answer.answer_text,
            "grounded": answer.grounding.ok,
            "refused": answer.refused,
            "model": answer.model,
            "prompt_version": answer.prompt_version,
            # D1. Beside prompt_version, because it answers the same kind of
            # question about the answer: what was it made from. An archive
            # WITHOUT this key predates D1 and is UNKNOWN, never "unchanged".
            "corpus_version": answer.corpus_version,
            "embedding_model": answer.embedding_model,
            "answer_id": stored_id,
            "grounding": answer.grounding.to_dict(),
            "passages": [p.to_dict() for p in answer.passages],
            "sources_block": answer.sources_block,
        })

    archived_paths = []
    if not args.no_write:
        archived_paths = [_archive(p) for p in payloads]

    all_grounded = all(a.grounding.ok for a, _ in runs)

    if args.json:
        print(json.dumps(payloads if args.repeat > 1 else payloads[0],
                         indent=2, ensure_ascii=False))
        return 0 if all_grounded else 1

    if args.repeat > 1:
        _print_repetitions(runs, archived_paths)
        return 0 if all_grounded else 1

    answer, stored_id = runs[0]
    archived = archived_paths[0] if archived_paths else None

    print(answer.render())
    print()
    _print_grounding(answer.grounding)
    for note in answer.notes:
        print(f"  note: {note}")
    if stored_id:
        print(f"\nstored as answer {stored_id}")
    if archived:
        # The table holds the current answer; this file holds *this* answer.
        print(f"archived run: {archived}")

    if answer.grounding.ok:
        print("\nGrounded: every claim carries a citation and every quotation was "
              "found in the source it cites.")
        return 0

    print(
        "\nNOT GROUNDED. Before changing the prompt, read which check failed: an "
        "uncited sentence is a prompt problem, an unverified quotation is the "
        "model writing text of its own, and a claim on an untranslated source is "
        "the failure this part exists to prevent."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
