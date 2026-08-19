"""Ruling 17(b) — how far each rendering sits from the query it was made from.

The script check (ruling 17a) verifies a WRITING SYSTEM. It cannot verify a
LANGUAGE, and the 2026-08-16 review showed what that leaves open: `latin` is the
required script for four of the seven targets, so any Latin string passes, and
the run admitted Old Norse for Proto-Norse, romanised Tamil for Parthian, and a
Chinese phonetic transcription of Parthian sounds that is 100% Han and means
nothing. None of those is visible to a rank and none is visible to the script
check.

This is the second instrument, and it is FREE: `cos(query, rendering)` uses only
vectors the ranking run computes anyway. It costs one batched embedding pass and
no chat calls.

WHAT IT SEES
    semantic drift from the source query. A transcription of the SOUNDS of a
    query, a rendering that answers the query instead of restating it, a
    rendering that dropped half the query — all sit far from the source.

WHAT IT DOES NOT SEE, and this must be said in the same breath
    the identity of a language. A competent Old Norse rendering and a competent
    Proto-Norse rendering of the same query will both sit close to it. This
    check cannot settle "is this Proto-Norse"; it can only say whether a
    language's renderings are, as a group, further from their queries than
    another language's are. That comparison is evidence, not proof, and the
    report prints it as a per-language distribution rather than a verdict.

REPORTED, NEVER GATED (ruling 17b). There is no baseline for this quantity, and
gating on a number with no baseline is the thing this project refuses. Nothing
here changes `ok` on any rendering; the script writes a report and returns 0
even when every row is an outlier.

    python scripts/check_renderings.py
    python scripts/check_renderings.py --mad 3.0
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from retrieve.render import DEFAULT_PATH, RenderingError, load  # noqa: E402

REPORT_DIR = pathlib.Path("eval/rendering_checks")


def cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    if not n:
        return 0.0
    mid = n // 2
    return ordered[mid] if n % 2 else (ordered[mid - 1] + ordered[mid]) / 2


def mad(values: list[float]) -> float:
    """Median absolute deviation. Robust where a standard deviation is not.

    Seven of thirty renderings in a language being wrong would drag a mean and
    a standard deviation with them, and the outlier test would then be tuned by
    the very rows it is meant to find.
    """
    med = median(values)
    return median([abs(v - med) for v in values])


def run(path: pathlib.Path, mad_multiple: float) -> int:
    renderings = load(path)

    texts: list[str] = []
    index: dict[tuple[str, str], int] = {}     # (query, lang) -> position
    for query, entry in renderings.by_query.items():
        index[(query, "__source__")] = len(texts)
        texts.append(query)
        for lang, row in sorted(entry.items()):
            if not row.get("ok"):
                continue
            index[(query, lang)] = len(texts)
            texts.append(row["text"])

    print(f"file       {path}")
    print(f"digest     {renderings.digest}")
    print(f"embedding  {len(texts)} texts "
          f"({len(renderings.by_query)} queries + "
          f"{len(texts) - len(renderings.by_query)} admitted renderings)")

    from ingest.embed import embed_texts, resolve_model_label

    embedded = embed_texts(texts, input_type="query")
    model = resolve_model_label()
    print(f"model      {model} in {embedded.batches} request(s)\n")

    rows: list[dict] = []
    for (query, lang), position in index.items():
        if lang == "__source__":
            continue
        source = embedded.vectors[index[(query, "__source__")]]
        rows.append({
            "query": query,
            "lang": lang,
            "cos": cosine(source, embedded.vectors[position]),
            "text": renderings.by_query[query][lang]["text"],
        })

    by_lang: dict[str, list[dict]] = {}
    for row in rows:
        by_lang.setdefault(row["lang"], []).append(row)

    outliers: list[dict] = []
    for lang, group in by_lang.items():
        values = [r["cos"] for r in group]
        floor = median(values) - mad_multiple * mad(values)
        for row in group:
            row["lang_median"] = median(values)
            row["outlier"] = row["cos"] < floor
            if row["outlier"]:
                outliers.append(row)

    report = {
        "schema": "mundus-ulterior/rendering-similarity/v1",
        "measured": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S+0000"),
        "renderings_file": str(path),
        "renderings_digest": renderings.digest,
        "embedding_model": model,
        "mad_multiple": mad_multiple,
        "about": (
            "Ruling 17(b). cos(source query, rendering), pre-rerank, from the "
            "same vectors a ranking run computes. Measures semantic drift from "
            "the query; does NOT identify a language. Reported, never gated."
        ),
        "by_language": {
            lang: {
                "n": len(group),
                "median": median([r["cos"] for r in group]),
                "mad": mad([r["cos"] for r in group]),
                "min": min(r["cos"] for r in group),
                "max": max(r["cos"] for r in group),
            }
            for lang, group in sorted(by_lang.items())
        },
        "rows": sorted(rows, key=lambda r: r["cos"]),
    }

    # Archive first. A KeyError in a report has already destroyed a run in this
    # repository; the file is the evidence and the table below is a rendering
    # of it.
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"{report['measured']}-query_similarity.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    print("per language — cos(source query, rendering)")
    print(f"  {'lang':9.9s} {'n':>3s}  {'median':>7s} {'mad':>6s} "
          f"{'min':>7s} {'max':>7s}")
    for lang, stats in report["by_language"].items():
        print(f"  {lang:9.9s} {stats['n']:3d}  {stats['median']:7.3f} "
              f"{stats['mad']:6.3f} {stats['min']:7.3f} {stats['max']:7.3f}")

    print(f"\n{len(outliers)} row(s) below their language's median "
          f"- {mad_multiple}x MAD:")
    for row in sorted(outliers, key=lambda r: r["cos"]):
        print(f"  {row['lang']:9.9s} {row['cos']:.3f} "
              f"(lang median {row['lang_median']:.3f})")
        print(f"            query      {row['query'][:64]}")
        print(f"            rendering  {row['text'][:64]}")

    print(f"\nwrote {out}")
    print(
        "\nReported, never gated. This measures distance from the query, not "
        "the identity of a language: two languages can both render a query "
        "faithfully and neither this number nor the script check can tell you "
        "which one you got."
    )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renderings", default=str(DEFAULT_PATH))
    parser.add_argument("--mad", type=float, default=2.0, dest="mad_multiple",
                        help="how many median absolute deviations below a "
                             "language's median counts as an outlier. A "
                             "parameter, archived with the numbers it produced.")
    args = parser.parse_args(argv)
    try:
        return run(pathlib.Path(args.renderings), args.mad_multiple)
    except RenderingError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
