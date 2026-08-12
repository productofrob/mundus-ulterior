"""Part 9: bundle the archived answer runs and the seed corpus into `ui/data.js`.

Why this script exists at all
----------------------------
An archived run in `eval/answer_runs/` records that a quotation lives at
`reference_translation[7:48]` of `scandinavia-03-vimose`. It does **not** record
what those characters are. The payload carries `english.text` — the passage the
model was shown — but a quote span is an offset into the *seed field*, and for a
non-English passage those are different strings entirely.

So a UI built from the payloads alone can print the numbers `[7:48]` and cannot
show what sits there. That is the difference between claiming provenance and
demonstrating it, and demonstrating it is the whole point of Part 9. This script
does the join: runs on one side, `data/seed_corpus/**/*.json` on the other,
matched on `doc_id` and `source_field`.

Why a `.js` file and not `.json`
--------------------------------
`ui/index.html` is meant to open by double-clicking it. Browsers refuse
`fetch("data.json")` from a `file://` page — it is a cross-origin request to a
null origin, and no header can be set on a local file to permit it. A `<script
src="data.js">` tag has no such restriction. The cost is one assignment line;
the benefit is that the UI needs no server, which matters because the point of
this part is that somebody can look at the thing.

Usage
-----
    python ui/build_ui_data.py
    python ui/build_ui_data.py --verify     # check spans, write nothing
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO / "eval" / "answer_runs"
CORPUS_DIR = REPO / "data" / "seed_corpus"
GOLD_DIR = REPO / "eval" / "gold"
OUT = Path(__file__).resolve().parent / "data.js"

# The seed fields a chunk can be cut from. `source_field` in a run payload
# names one of these; anything else is a shape we have not seen and should be
# reported rather than silently dropped.
TEXT_FIELDS = ("original_text_excerpt", "reference_translation")

# Carried into the UI so a source card can show what the record claims about
# itself without the UI hardcoding the seed schema.
META_FIELDS = (
    "id", "region", "title", "source_type", "language_code", "language_note",
    "date", "findspot", "citation", "citation_original_language",
    "translation_source", "original_text_note", "reference_translation_note",
    "notes",
)


def load_corpus() -> dict[str, dict]:
    """Read every seed record, keyed by document id.

    The document id in a run payload (`doc_id`) is the seed record's `id`, not
    its filename, so the mapping has to be built by reading the files rather
    than by guessing paths.
    """
    corpus: dict[str, dict] = {}
    for path in sorted(CORPUS_DIR.rglob("*.json")):
        if path.name in {"manifest.json"}:
            continue
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  skipped unreadable seed record {path.name}: {exc}",
                  file=sys.stderr)
            continue
        doc_id = record.get("id")
        if not doc_id:
            print(f"  seed record without an id: {path.name}", file=sys.stderr)
            continue

        entry = {k: record.get(k) for k in META_FIELDS if record.get(k) is not None}
        entry["file"] = str(path.relative_to(REPO)).replace("\\", "/")
        entry["fields"] = {
            field: record[field]
            for field in TEXT_FIELDS
            if isinstance(record.get(field), str)
        }
        corpus[doc_id] = entry
    return corpus


def load_runs() -> list[dict]:
    """Read every archived run.

    Two payload shapes exist on disk and both are kept. The `-recovered` files
    were reconstructed in Part 8 and carry a thinner passage record — no `lang`,
    `region` or `citation`. Normalising them into the richer shape by inventing
    those fields would put fabricated provenance into a provenance viewer, so
    they are marked instead and the UI renders what is actually there.
    """
    runs: list[dict] = []
    for path in sorted(RUNS_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        # `--repeat N --json` writes a list; single runs write an object.
        items = payload if isinstance(payload, list) else [payload]
        for index, item in enumerate(items):
            item["file"] = path.name
            item["run_key"] = f"{path.stem}#{index}" if len(items) > 1 else path.stem
            passages = item.get("passages") or []
            item["partial_passages"] = bool(passages) and "lang" not in passages[0]
            runs.append(item)
    return runs


def _same_characters(found: str, quote: str) -> bool:
    """Is `found` the same run of characters the model quoted?

    Containment in either direction, not equality: `cite.py` trims edge
    punctuation before recording a span, so a quotation ending in a comma the
    source does not have is a quoting convention, not a corruption.
    """
    return bool(found) and (found in quote or quote in found)


def classify_span(span: dict, corpus: dict[str, dict]) -> dict:
    """Decide what a claimed character span actually holds, today.

    Until now this assertion has only been checked at answer time, against the
    live database that produced the answer. Checking it here — archive against
    seed files — asks a different and more useful question: *does the claim
    still hold?* The Part 8 corpus edits happened after most of these runs were
    archived, so some of these offsets now point at text that has moved.

    Four outcomes, and the distinction between the middle two is the reason this
    function exists rather than a boolean:

    - `resolved`   — the characters at the offset are the quoted characters.
    - `case_only`  — they differ only in letter case. `cite.py`'s
      `locate_in_text` falls back to a case-folded search and still labels the
      result `match="exact"`, so the payload overstates what it found. The span
      is right; the label is not. Worth showing rather than smoothing over,
      because a viewer that prints "exact" beside two visibly different strings
      discredits itself.
    - `moved`      — the quote is still in the field, at a different offset. The
      record was edited after this answer was archived. **This is the failure a
      naive viewer would render silently and convincingly**, showing whatever
      now sits at those coordinates as though the answer had quoted it.
    - `absent`     — the quote is not in the field at all.
    """
    start, end = span.get("abs_start"), span.get("abs_end")
    quote = (span.get("quote") or "").strip()
    doc = corpus.get(span.get("doc_id"))
    field = span.get("source_field")

    if doc is None:
        return {"state": "absent", "why": "no seed record with this doc_id"}
    text = doc["fields"].get(field)
    if text is None:
        return {"state": "absent", "why": f"seed record has no field {field!r}"}

    found = text[start:end]
    if _same_characters(found, quote):
        return {"state": "resolved", "found": found}
    if _same_characters(found.casefold(), quote.casefold()):
        return {"state": "case_only", "found": found,
                "why": "differs from the quotation only in letter case; "
                       "cite.py matched case-insensitively but recorded "
                       "match='exact'"}

    at = text.find(quote)
    if at < 0 and quote:
        at = text.casefold().find(quote.casefold())
    if at >= 0:
        return {"state": "moved", "found": found, "now_at": [at, at + len(quote)],
                "why": "the seed record was edited after this run was archived; "
                       "the quotation is still in the field, at a different offset"}
    return {"state": "absent", "found": found,
            "why": "the quotation is not in this field of the seed record as it "
                   "stands today"}


def verify_spans(runs: list[dict], corpus: dict[str, dict]) -> dict[str, list]:
    """Classify every claimed span, annotating the runs in place.

    The classification is written back onto each span as `resolution`, so the UI
    never has to re-derive it and can never disagree with this script about what
    a span holds.
    """
    buckets: dict[str, list] = {"resolved": [], "case_only": [], "moved": [],
                                "absent": []}
    for run in runs:
        for span in run.get("grounding", {}).get("quote_spans", []):
            if span.get("abs_start") is None or span.get("abs_end") is None:
                continue                      # no span was claimed; not a defect
            resolution = classify_span(span, corpus)
            span["resolution"] = resolution
            buckets[resolution["state"]].append({
                "run": run["run_key"], "doc_id": span.get("doc_id"),
                "field": span.get("source_field"),
                "at": f"[{span['abs_start']}:{span['abs_end']}]",
                "quote": (span.get("quote") or "")[:70],
                **{k: v for k, v in resolution.items() if k != "found"},
            })
    return buckets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="bundle archived runs for ui/index.html")
    parser.add_argument("--verify", action="store_true",
                        help="check every span against the seed corpus, write nothing")
    args = parser.parse_args(argv)

    if not RUNS_DIR.exists():
        print(f"no archived runs at {RUNS_DIR}", file=sys.stderr)
        return 2

    corpus = load_corpus()
    runs = load_runs()
    print(f"{len(runs)} archived run(s), {len(corpus)} seed record(s)")

    buckets = verify_spans(runs, corpus)
    total = sum(len(v) for v in buckets.values())
    print(f"\n{total} claimed character span(s) checked against the seed corpus:")
    for state in ("resolved", "case_only", "moved", "absent"):
        print(f"  {state:<10} {len(buckets[state])}")

    for state in ("moved", "absent", "case_only"):
        for item in buckets[state][:6]:
            print(f"\n  {state.upper()}  {item['doc_id']}.{item['field']}"
                  f"{item['at']}  ({item['run']})")
            print(f"    quote: {item['quote']!r}")
            print(f"    {item.get('why', '')}")
        if len(buckets[state]) > 6:
            print(f"  ... and {len(buckets[state]) - 6} more {state}")

    # `moved` and `absent` mean an archived citation no longer points at what it
    # claimed. `case_only` is a labelling defect in cite.py, not a broken claim,
    # so it is reported but does not fail the check.
    broken = len(buckets["moved"]) + len(buckets["absent"])
    if args.verify:
        return 1 if broken else 0

    gold = {}
    for name in ("answer_cases.json", "confidence_profiles.json", "floor.json"):
        path = GOLD_DIR / name
        if path.exists():
            gold[name.removesuffix(".json")] = json.loads(
                path.read_text(encoding="utf-8"))

    bundle = {
        "generated": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "runs": runs,
        "corpus": corpus,
        "gold": gold,
        # Recorded so the UI can say, honestly, whether the archive it is
        # displaying still matches the corpus on disk.
        "span_audit": {k: len(v) for k, v in buckets.items()},
        "span_problems": buckets["moved"] + buckets["absent"] + buckets["case_only"],
    }

    OUT.write_text(
        "// Generated by ui/build_ui_data.py — do not edit by hand.\n"
        "window.MU_DATA = "
        + json.dumps(bundle, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    size = OUT.stat().st_size / 1024
    print(f"wrote {OUT.relative_to(REPO)} ({size:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
