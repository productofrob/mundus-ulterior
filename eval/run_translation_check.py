"""Part 6 entrypoint: translate, back-translate, score, record.

Usage (repo root, venv active, .env loaded, gateway on :4000, db up):

    python -m eval.run_translation_check --dry-run    # pick the chunks, no API calls
    python -m eval.run_translation_check --case muziris-54-grc
    python -m eval.run_translation_check              # the whole gold set
    python -m eval.run_translation_check --stats

Cost model, which drives the shape of this file:
  * translation is TWO chat calls per case, and they cannot be batched;
  * embedding is ONE request for the whole run, because Voyage's free tier
    allows three per minute and Part 4 lost an afternoon to learning that.

So every chat call happens first, all the text is collected, and the embeddings
are taken in a single batched call at the end.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field

from answer import confidence, store, translate
from answer.align import pair_chunks, section_label
from eval.goldset import (
    TranslationCase,
    band_at_least,
    load_profiles,
    load_translation_cases,
)

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

OUTPUT_PATH = "eval/translation_check_last_run.json"

# Every run is also archived. `last_run.json` is overwritten by whatever ran
# most recently, and a one-case `--case akananuru-149-oty` invocation replaced a
# nine-case baseline on 2026-08-10 — the file said "last run" and meant it, but
# the only copy of the previous results was in a terminal scrollback. Archived
# runs are what calibration is done from, so they cannot live in a file whose
# contract is "most recent invocation".
RUNS_DIR = "eval/runs"

# Half of embed.py's default. All the texts for a full run fit in one request
# by count, but the free tier also caps tokens per minute, and two smaller
# requests are still well inside three per minute.
EMBED_BATCH_SIZE = 16


@dataclass
class Attempt:
    """One case, carried through the chat phase into the scoring phase."""
    case: TranslationCase
    chunk: store.ChunkRow
    reference_text: str | None
    reference_ground: str
    forward: translate.Translation | None = None
    back: translate.Translation | None = None
    error: str | None = None
    report: confidence.ConfidenceReport | None = None
    cos_back: float | None = None
    cos_ref: float | None = None
    notes: list[str] = field(default_factory=list)


def select_chunk(chunks: list[store.ChunkRow], case: TranslationCase):
    """Find the chunk a case names, or explain why it can't be found."""
    if not chunks:
        return None, (
            f"no retrieval-eligible original chunks for {case.doc_id}. Either the "
            f"record is held back by the Part 3 fidelity classifier, or ingestion "
            f"has not been re-run since the corpus changed."
        )
    if case.section is not None:
        for c in chunks:
            if section_label(c.text) == case.section:
                return c, None
        found = sorted({section_label(c.text) or "-" for c in chunks})
        return None, (
            f"{case.doc_id} has no chunk labelled section {case.section!r} "
            f"(found: {found}). The section markers come from the source text, so "
            f"this usually means the record was edited without updating the case."
        )
    if case.seq is not None:
        for c in chunks:
            if c.seq == case.seq:
                return c, None
        return None, f"{case.doc_id} has no chunk with seq {case.seq}"
    return chunks[0], None


def build_attempt(conn, case: TranslationCase) -> Attempt:
    originals = store.fetch_by_doc(conn, case.doc_id, role="original")
    chunk, problem = select_chunk(originals, case)
    if chunk is None:
        return Attempt(case, None, None, "none", error=problem)  # type: ignore[arg-type]

    if chunk.lang != case.source_lang:
        note = (
            f"case declares source_lang '{case.source_lang}' but the chunk's "
            f"script-detected lang is '{chunk.lang}'. The database wins; the "
            f"prompt will name '{chunk.lang}'."
        )
    else:
        note = None

    translations = store.fetch_by_doc(conn, case.doc_id, role="translation")
    reference_text, ground = None, "none"
    if translations:
        for pair in pair_chunks(originals, translations):
            if pair.original.chunk_id == chunk.chunk_id and pair.translation:
                reference_text, ground = pair.translation.text, pair.ground
                break
        if reference_text is None:
            # No passage-level pairing available. The published translation is
            # still evidence, but only about the document — say which it is,
            # because a low chrf_ref against a document-level reference is not
            # a translation error.
            reference_text = "\n\n".join(t.text for t in translations)
            ground = "document"

    attempt = Attempt(case, chunk, reference_text, ground)
    if note:
        attempt.notes.append(note)
    return attempt


def run_chat_phase(attempts: list[Attempt], model: str, pause: float) -> None:
    for i, attempt in enumerate(attempts, start=1):
        if attempt.error:
            continue
        chunk = attempt.chunk
        print(
            f"[{i}/{len(attempts)}] {attempt.case.id}: translating "
            f"{chunk.chunk_id} ({chunk.lang}, {len(chunk.text)} chars)",
            flush=True,
        )
        try:
            attempt.forward = translate.translate_to_english(
                chunk.text, chunk.lang, model=model
            )
            if attempt.forward.is_empty:
                attempt.error = "forward translation was empty"
                continue
            # The back-translation is given the English only — see the
            # contamination guard in answer/test_translate.py.
            attempt.back = translate.back_translate(
                attempt.forward.text, chunk.lang, model=model
            )
        except translate.TranslationError as exc:
            attempt.error = str(exc)
            print(f"        failed: {exc}", file=sys.stderr)
        if pause:
            time.sleep(pause)


def run_embedding_phase(attempts: list[Attempt]) -> tuple[str | None, list[str]]:
    """One batched embedding request for the whole run."""
    from ingest.embed import EmbeddingError, embed_texts, resolve_model_label

    texts: list[str] = []
    index: list[tuple[int, str]] = []   # (attempt position, slot name)

    for pos, attempt in enumerate(attempts):
        if attempt.error or not attempt.forward or not attempt.back:
            continue
        if attempt.back.text.strip():
            index.append((pos, "original")); texts.append(attempt.chunk.text)
            index.append((pos, "back")); texts.append(attempt.back.text)
        if attempt.reference_text:
            index.append((pos, "forward")); texts.append(attempt.forward.text)
            index.append((pos, "reference")); texts.append(attempt.reference_text)

    if not texts:
        return None, ["nothing to embed — no case produced a usable round trip"]

    try:
        result = embed_texts(texts, input_type="document", batch_size=EMBED_BATCH_SIZE)
    except EmbeddingError as exc:
        return None, [
            f"embedding failed, so cosine scores are unavailable and bands fall "
            f"back to chrF alone: {exc}"
        ]

    slots: dict[int, dict[str, list[float]]] = {}
    for (pos, name), vector in zip(index, result.vectors):
        slots.setdefault(pos, {})[name] = vector

    for pos, vectors in slots.items():
        attempt = attempts[pos]
        if "original" in vectors and "back" in vectors:
            attempt.cos_back = confidence.cosine(vectors["original"], vectors["back"])
        if "forward" in vectors and "reference" in vectors:
            attempt.cos_ref = confidence.cosine(vectors["forward"], vectors["reference"])

    return resolve_model_label(), list(result.notes)


def score_attempts(attempts: list[Attempt], profiles: dict) -> None:
    for attempt in attempts:
        if attempt.error or not attempt.forward:
            continue
        profile = profiles[attempt.case.profile]
        attempt.report = confidence.score(
            original=attempt.chunk.text,
            forward_en=attempt.forward.text,
            back_translated=attempt.back.text if attempt.back else "",
            profile=profile,
            cos_back=attempt.cos_back,
            reference_en=attempt.reference_text,
            cos_ref=attempt.cos_ref,
        )


def judge(attempt: Attempt) -> tuple[str, list[str]]:
    """PASS / FAIL / ERROR for one case, with the reasons."""
    if attempt.error:
        return "ERROR", [attempt.error]
    report = attempt.report
    if report is None:
        return "ERROR", ["no score produced"]

    reasons: list[str] = []
    case = attempt.case
    blocking = [f for f in report.blocking_flags if f not in case.allow_flags]

    # A case declared untranslatable passes when the pipeline refuses. The
    # assertion is about the detector, not the translation: the Vimose runes are
    # six partly undeciphered sequences and the honest output is no output.
    if case.expect_untranslatable:
        if blocking:
            return "PASS", []
        return "FAIL", [
            "expected this source to be detected as untranslatable, but a "
            "clean translation came back. Either the model has improved, or it "
            "has produced a confident reading of undeciphered text. Read the "
            "translation before relaxing anything."
        ]

    if case.expect_no_blocking_flags and blocking:
        reasons.append(f"blocking flag(s): {blocking}")
    if not band_at_least(report.band, case.expect_min_band):
        reasons.append(f"band {report.band} below floor {case.expect_min_band}")
    return ("FAIL" if reasons else "PASS"), reasons


def fmt(value: float | None) -> str:
    return f"{value:.3f}" if value is not None else "  -  "


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mundus Ulterior Part 6 translation check")
    parser.add_argument("--case", action="append", help="run only these case ids")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true",
                        help="resolve chunks and references, make no API calls")
    parser.add_argument("--no-write", action="store_true",
                        help="score but don't store translations in Postgres")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--pause", type=float, default=0.0,
                        help="seconds to wait between cases (chat rate limits)")
    parser.add_argument(
        "--repeat", type=int, default=1,
        help="run each case N times and report the spread. Costs N x 2 chat "
             "calls per case. Temperature is 0, but that is not determinism: "
             "the same Tamil case scored chrF 0.333 and then 0.016 on two "
             "identical runs. A threshold set from a single shot is not a "
             "threshold.",
    )
    args = parser.parse_args(argv)

    import psycopg

    profiles = load_profiles()
    cases = load_translation_cases(profiles=profiles)
    if args.case:
        wanted = set(args.case)
        unknown = wanted - {c.id for c in cases}
        if unknown:
            print(f"unknown case id(s): {sorted(unknown)}", file=sys.stderr)
            return 2
        cases = [c for c in cases if c.id in wanted]
    if args.limit:
        cases = cases[: args.limit]

    problem = None
    try:
        from ingest.db import check_connection

        problem = check_connection(store.get_dsn())
    except Exception:  # noqa: BLE001 — ingest.db is optional to this module
        pass
    if problem:
        print(problem, file=sys.stderr)
        return 2

    with psycopg.connect(store.get_dsn()) as conn:
        store.apply_schema(conn)

        if args.stats:
            print(json.dumps(store.stats(conn), indent=2, ensure_ascii=False))
            return 0

        attempts = [build_attempt(conn, case) for case in cases]
        if args.repeat > 1:
            # Rebuild rather than copy: each repetition is an independent
            # attempt at the same case, so nothing is shared between them.
            attempts = [
                build_attempt(conn, case)
                for _ in range(args.repeat)
                for case in cases
            ]
            print(f"--repeat {args.repeat}: {len(attempts)} attempts "
                  f"({len(cases)} cases x {args.repeat})\n")

        print(f"{len(attempts)} case(s) resolved\n")
        for attempt in attempts:
            if attempt.error:
                print(f"  [ERROR] {attempt.case.id}: {attempt.error}")
                continue
            print(
                f"  {attempt.case.id:22} {attempt.chunk.chunk_id:46} "
                f"{attempt.chunk.lang:8} profile={attempt.case.profile:12} "
                f"reference={attempt.reference_ground}"
            )
            for note in attempt.notes:
                print(f"        note: {note}")

        if args.dry_run:
            print("\ndry run — no API calls made, nothing written")
            return 0

        model_label = translate.resolve_model_label()
        print(f"\ntranslating via gateway; recording model as: {model_label}")
        print(f"2 chat calls per case = {2 * sum(1 for a in attempts if not a.error)} calls\n")

        run_chat_phase(attempts, translate.DEFAULT_MODEL, args.pause)
        embed_model, embed_notes = run_embedding_phase(attempts)
        for note in embed_notes:
            print(f"  note: {note}")
        score_attempts(attempts, profiles)

        # ------------------------------------------------------------------
        # Report
        # ------------------------------------------------------------------
        print(
            f"\n{'case':22} {'status':7} {'band':8} {'chrF↺':7} {'cos↺':7} "
            f"{'chrF·ref':9} {'cos·ref':8} flags"
        )
        failures = 0
        results: list[dict] = []
        for attempt in attempts:
            status, reasons = judge(attempt)
            if status != "PASS":
                failures += 1
            report = attempt.report
            print(
                f"{attempt.case.id:22} {status:7} "
                f"{(report.band if report else '-'):8} "
                f"{fmt(report.chrf_back if report else None):7} "
                f"{fmt(report.cos_back if report else None):7} "
                f"{fmt(report.chrf_ref if report else None):9} "
                f"{fmt(report.cos_ref if report else None):8} "
                f"{','.join(report.flags) if report and report.flags else ''}"
            )
            for reason in reasons:
                print(f"    -> {reason}")
            if report:
                for note in report.notes:
                    print(f"       {note}")

            results.append(
                {
                    "case": attempt.case.id,
                    "status": status,
                    "reasons": reasons,
                    "doc_id": attempt.case.doc_id,
                    "chunk_id": attempt.chunk.chunk_id if attempt.chunk else None,
                    "lang": attempt.chunk.lang if attempt.chunk else None,
                    "profile": attempt.case.profile,
                    "reference_ground": attempt.reference_ground,
                    "score": report.to_dict() if report else None,
                    "translation": attempt.forward.text if attempt.forward else None,
                    "back_translation": attempt.back.text if attempt.back else None,
                    "translation_notes": (attempt.forward.notes if attempt.forward else [])
                    + (attempt.back.notes if attempt.back else []),
                }
            )

        # Calibration aid: the thresholds are provisional, so print the spread
        # they are being applied to. Set thresholds from this, not from taste.
        #
        # Cases carrying a blocking flag are EXCLUDED. The Vimose runes echoed
        # their source on 2026-08-10 and contributed chrF 0.981 / cos 0.997 to
        # the inscription range — a failure, feeding the numbers used to decide
        # what success looks like. A blocked case is not a measurement.
        print("\nobserved by profile (for calibrating eval/gold/confidence_profiles.json)")
        by_profile: dict[str, list[Attempt]] = {}
        excluded = 0
        for attempt in attempts:
            if not attempt.report:
                continue
            if attempt.report.blocking_flags:
                excluded += 1
                continue
            by_profile.setdefault(attempt.case.profile, []).append(attempt)
        if excluded:
            print(f"  ({excluded} case(s) excluded: blocked, so not a measurement)")
        for name, group in sorted(by_profile.items()):
            cos = [a.report.cos_back for a in group if a.report.cos_back is not None]
            ch = [a.report.chrf_back for a in group if a.report.chrf_back is not None]
            calibrated = "calibrated" if profiles[name].calibrated else "PROVISIONAL"
            print(
                f"  {name:12} n={len(group)}  "
                f"cos↺ {fmt(min(cos) if cos else None)}-{fmt(max(cos) if cos else None)}  "
                f"chrF↺ {fmt(min(ch) if ch else None)}-{fmt(max(ch) if ch else None)}  "
                f"[{calibrated}]"
            )

        # Variance across repetitions of the same case. This is the number that
        # says whether any threshold below is meaningful: if the spread within
        # one case approaches the distance between two profiles, the profiles
        # are not measuring genre, they are measuring noise.
        if args.repeat > 1:
            print(f"\nspread across {args.repeat} runs of each case")
            print(f"{'case':22} {'chrF↺ min-max':>16} {'range':>7} "
                  f"{'cos↺ min-max':>16} {'range':>7}  bands")
            grouped: dict[str, list[Attempt]] = {}
            for attempt in attempts:
                if attempt.report and not attempt.report.blocking_flags:
                    grouped.setdefault(attempt.case.id, []).append(attempt)
            worst = 0.0
            for case_id, group in sorted(grouped.items()):
                ch = [a.report.chrf_back for a in group if a.report.chrf_back is not None]
                co = [a.report.cos_back for a in group if a.report.cos_back is not None]
                bands = {a.report.band for a in group}
                if ch:
                    worst = max(worst, max(ch) - min(ch))
                print(
                    f"{case_id:22} "
                    f"{fmt(min(ch) if ch else None)}-{fmt(max(ch) if ch else None):>7} "
                    f"{(max(ch) - min(ch)) if ch else 0:7.3f} "
                    f"{fmt(min(co) if co else None)}-{fmt(max(co) if co else None):>7} "
                    f"{(max(co) - min(co)) if co else 0:7.3f}  "
                    f"{'/'.join(sorted(bands))}"
                    f"{'  <- BAND UNSTABLE' if len(bands) > 1 else ''}"
                )
            print(
                f"\nwidest chrF spread within a single case: {worst:.3f}. "
                f"Compare that against the gaps between profile thresholds "
                f"before trusting any of them."
            )

        if not args.no_write:
            written = 0
            for attempt in attempts:
                if attempt.error or not attempt.forward or not attempt.report:
                    continue
                store.write_translation(
                    conn,
                    {
                        "chunk_id": attempt.chunk.chunk_id,
                        "target_lang": "en",
                        "translation_model": model_label,
                        "prompt_version": attempt.forward.prompt_version,
                        "translated_text": attempt.forward.text,
                        "source_text_sha256": store.text_sha256(attempt.chunk.text),
                        "back_translated_text": attempt.back.text if attempt.back else None,
                        "back_translation_model": model_label if attempt.back else None,
                        "back_prompt_version": (
                            attempt.back.prompt_version if attempt.back else "none"
                        ),
                        "chrf_back": attempt.report.chrf_back,
                        "cos_back": attempt.report.cos_back,
                        "chrf_ref": attempt.report.chrf_ref,
                        "cos_ref": attempt.report.cos_ref,
                        "chrf_echo": attempt.report.chrf_echo,
                        "confidence_band": attempt.report.band,
                        "confidence_profile": attempt.report.profile,
                        "flags": attempt.report.flags,
                        "scoring_embedding_model": embed_model,
                        "notes": " | ".join(attempt.report.notes) or None,
                    },
                )
                written += 1
            print(f"\nstored {written} translation(s) in chunk_translations")
            print(json.dumps(store.stats(conn), indent=2, ensure_ascii=False))

    import os
    from datetime import datetime, timezone

    payload = {
        "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cases_requested": args.case or "all",
        "translation_model": model_label,
        "embedding_model": embed_model,
        "back_prompt_version": translate.BACK_PROMPT_VERSION,
        "prompt_version": translate.PROMPT_VERSION,
        "results": results,
    }
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    os.makedirs(RUNS_DIR, exist_ok=True)
    stamp = payload["ran_at"].replace(":", "").replace("-", "")
    scope = "all" if not args.case else f"{len(results)}case"
    archive = f"{RUNS_DIR}/{stamp}-{scope}.json"
    with open(archive, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print(f"wrote {OUTPUT_PATH} and archived to {archive}")

    if failures:
        print(f"\n{failures} case(s) did not meet their expectation.")
        print(
            "Before changing a threshold, check which signal moved: a blocking "
            "flag means the round trip did not happen and no threshold can fix "
            "it; a band below floor with clean flags may mean the floor is wrong "
            "for that genre."
        )
        return 1

    print("\nAll translation cases met their expectations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
