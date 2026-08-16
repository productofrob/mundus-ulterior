"""Shared machinery for Block B4 distractor fetchers.

Two collections now feed seam 3 (see BLOCK_B3_DISTRACTORS.md, decision 3 as
amended 2026-08-14). Everything they share lives here rather than being copied,
because **two implementations of one rule is the defect this repository keeps
paying for** — `--find` vs `--survey` disagreeing on numeric ids,
`translation_chunk` vs `translation_chunk_id`, and a JS port of `date_audit`
that was rejected for the same reason. An era rule that drifts between two
fetchers would put era-overlapping material in the padding on one side only,
and nothing would report it.

What is NOT shared: the field names and the rendering. Those are genuinely
per-API, and pretending otherwise would be the opposite error.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

OUT_DIR = Path("data/distractors")

# The project's window, from the brief: 27 BC to 1204 AD. A distractor must sit
# entirely outside it.
ERA_START, ERA_END = -27, 1204

# Fixed, so a tranche is reproducible and its composition can be recorded in the
# archived ranking run. Shared across sources so "the same seed" means one thing.
SEED = 20260814

# Below this, a rendered record is too thin to compete with anything and would
# pad the index without testing it. The corpus's own object_description chunks
# run 110-409 characters.
MIN_CHARS = 120

# No distractor may be longer than the longest chunk the project's own chunker
# would ever emit. Cleveland's descriptions run to 1422 characters against a
# corpus whose chunks are 36-1158 (median 416); left uncapped, the padding would
# differ from the corpus in LENGTH as well as in content, and a curve that moved
# could be reporting either. Capped at a sentence boundary, and the pre- and
# post-cap length distributions are both recorded.
MAX_CHARS = 1200

# Longest a single retry may sleep. See get().
MAX_BACKOFF = 20.0

# How often a long fetch reports. PROGRESS.md, Part 4: "the backfill prints a
# line per batch, so a slow gateway reports instead of looking dead." That
# lesson was recorded on 2026-08-09 and not applied here until a --pause 1.0 run
# went silent for minutes and had to be asked whether it had frozen.
PROGRESS_EVERY = 25


def cap(text: str, limit: int = MAX_CHARS) -> str:
    """Trim to the last sentence end at or before `limit`. Never mid-word."""
    if len(text) <= limit:
        return text
    window = text[:limit]
    for mark in (". ", "; ", ", "):
        cut = window.rfind(mark)
        if cut > limit // 2:
            return window[:cut + 1].strip()
    return window.rsplit(" ", 1)[0].strip()


def strip_markup(text: str) -> str:
    """Cleveland's `description` carries HTML — `<br><br>`, `<em>...</em>`.

    Left in, the padding would be the only material in the index containing
    markup, which is a signal about provenance rather than about content and is
    exactly the kind of artefact that makes a distractor distinguishable for the
    wrong reason.
    """
    import html
    import re

    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


class Throttled(RuntimeError):
    """The API refused repeatedly. Not a bug — a signal to stop and keep what
    was gathered."""


def get(url: str, pause: float = 0.12, attempts: int = 5) -> dict | None:
    """One GET. Returns None on 404, which collection APIs use freely.

    Retries 403/429/5xx with exponential backoff. The Met returned **HTTP 403**
    partway through a 300-record fetch and the exception killed the run,
    discarding every record gathered up to that point — the fetch had no way to
    tell "this API is refusing" from "this code is broken", and neither did the
    person reading the traceback.

    A 403 from a public open-access API at eight requests a second is almost
    certainly throttling or a bot rule, not a permission problem. It is retried
    politely and then raised as `Throttled`, which callers catch to write what
    they have instead of losing it.
    """
    delay = pause
    for attempt in range(attempts):
        time.sleep(delay)
        req = urllib.request.Request(url, headers={
            "User-Agent": "mundus-ulterior/phase2-b4 (research; distractor corpus)",
            "Accept": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            if exc.code in (403, 429, 500, 502, 503, 504) and attempt < attempts - 1:
                # Capped. Uncapped tripling from a --pause of 1.0 gives
                # 1+3+9+27+81 = 121 seconds on a single refused object, during
                # which a loop with no progress output is indistinguishable
                # from a hang. Backoff should be polite, not invisible.
                delay = min(MAX_BACKOFF, max(pause, delay * 3))
                continue
            if exc.code in (403, 429):
                raise Throttled(
                    f"HTTP {exc.code} from {url} after {attempts} attempts. "
                    f"The API is refusing; this is not a code defect. Keep what "
                    f"has been gathered and resume later.") from exc
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < attempts - 1:
                delay = min(MAX_BACKOFF, max(pause, delay * 3))
                continue
            raise


def overlaps_era(begin, end) -> bool:
    """True if [begin, end] touches the project's window, or is unknown.

    Unknown dates count as overlapping. A distractor whose period cannot be
    established is exactly the one that might be about the corpus's subject, and
    an unproven negative is not a negative.
    """
    if begin is None or end is None:
        return True
    try:
        begin, end = int(begin), int(end)
    except (TypeError, ValueError):
        return True
    return not (end < ERA_START or begin > ERA_END)


def sentence(*parts: str) -> str:
    """Join non-empty fragments into a rendered catalogue record."""
    out = []
    for part in parts:
        part = (part or "").strip().rstrip(".")
        if part:
            out.append(part + ".")
    return " ".join(out)


def write_records(source: str, records: list[dict], rejected: dict,
                  extra: dict | None = None) -> dict:
    """One output shape for every source, so the loader has one reader.

    MERGES with an existing file for the same source instead of overwriting it.
    The Met throttles: a 300-record run stopped at 47, and the honest fix for
    that is to re-run and top up. Overwriting would mean a second run that died
    EARLIER silently destroyed the first run's records — the same "discard the
    work" defect the Throttled handling was added to fix, one level up, and
    worse because it would look like success.

    Existing records win on a tie: they were fetched under whatever rules were
    live then, and re-deriving them is not the point of a top-up.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{source}-{date.today().isoformat()}.json"

    existing: list[dict] = []
    if path.exists():
        prior = json.loads(path.read_text(encoding="utf-8"))
        if prior.get("source") == source:
            existing = prior.get("records", [])
    seen = {str(r["object_id"]) for r in existing}
    added = [r for r in records if str(r["object_id"]) not in seen]
    merged = existing + added

    payload = {
        "schema": "mundus-ulterior/distractors/v1",
        "source": source,
        "fetched": date.today().isoformat(),
        "seed": SEED,
        "era_excluded": [ERA_START, ERA_END],
        "min_chars": MIN_CHARS,
        "max_chars": MAX_CHARS,
        "kept": len(merged),
        "added_this_run": len(added),
        "carried_from_earlier_run": len(existing),
        "rejected": rejected,
        **(extra or {}),
        "records": merged,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                    encoding="utf-8")
    payload["path"] = str(path)
    return payload


def report(payload: dict) -> None:
    print(f"kept {payload['kept']} records -> {payload['path']}")
    if payload.get("carried_from_earlier_run"):
        print(f"  {payload['added_this_run']} added this run, "
              f"{payload['carried_from_earlier_run']} carried from an earlier one")
    print("rejected, by named reason:")
    for reason, n in sorted(payload["rejected"].items(), key=lambda kv: -kv[1]):
        print(f"  {n:6d}  {reason}")
    lens = [len(r["text"]) for r in payload["records"]]
    if lens:
        lens.sort()
        print(f"\ntext length: min={lens[0]} median={lens[len(lens)//2]} "
              f"max={lens[-1]}")
        print("corpus object_description chunks for comparison: 110-409 chars")


def skeleton_report(payloads: list[dict]) -> None:
    """How uniform is the padding?

    The reason a second collection was added at all. A rendered catalogue record
    has a fixed skeleton, and several hundred chunks sharing one skeleton may
    cluster in embedding space and either all compete or none do — which would
    make the W2b curve a measurement of the renderer rather than of the index.

    This reports the crudest available proxy: how many distinct leading
    three-word shapes the padding has, and the share held by the commonest.
    Not a gate. A number to look at before spending an embedding request.
    """
    from collections import Counter

    shapes: Counter = Counter()
    per_source: dict[str, Counter] = {}
    for payload in payloads:
        c = per_source.setdefault(payload["source"], Counter())
        for rec in payload["records"]:
            words = rec["text"].split()
            shape = " ".join(words[:3])
            shapes[shape] += 1
            c[shape] += 1

    total = sum(shapes.values())
    if not total:
        print("no records to profile")
        return
    print(f"\nskeleton profile over {total} records from "
          f"{len(per_source)} source(s):")
    print(f"  distinct leading shapes : {len(shapes)}")
    top, n = shapes.most_common(1)[0]
    print(f"  commonest shape         : {n} ({n / total:.0%})  {top!r}")
    for source, c in sorted(per_source.items()):
        st = sum(c.values())
        print(f"  {source:12s} {len(c):5d} shapes over {st} records")
