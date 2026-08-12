"""The gazetteer: Pleiades ids in, coordinates out, and nothing else.

The rule this module exists to enforce, from `PHASE2_PLAN.md` action #2:

    Every pleiades_id is looked up and its JSON cached. No id, from me or any
    model, is written from memory. A remembered id is an authored coordinate
    wearing a citation.

So: `ingest/places.py` validates that a placement carries an id, and this module
is the only thing in the repository that turns an id into a point. Read the two
together and there is no path from a seed record to a map pin that does not pass
through a cached lookup with a dated source.

Why a dated bulk dump rather than per-id fetches
------------------------------------------------
`PHASE2_PLAN.md` A1 specifies fetching `pleiades.stoa.org/places/<id>/json` once
per id. On 2026-08-12 that endpoint was found to sit behind **Anubis**, a
proof-of-work anti-bot challenge: the JSON URL returns an empty body and the
HTML page returns a JavaScript challenge. A `urllib` call from the host would
meet the same wall, and would meet it as an ambiguous failure that reads like
"this id does not exist" — the project's recurring *a check that matches too
broadly names the wrong cause*, which has already cost an afternoon chasing a
healthy gateway.

Pleiades publishes complete dumps at `atlantides.org`, regenerated each morning
and named by date. Taking a **dated snapshot** is also the better fit for this
repository's standing lesson that *a result is comparable only within the thing
that produced it, and that thing must be recorded*: every cached entry carries
the dump date it came from, so a coordinate can be told from a coordinate that
was correct under an earlier snapshot.

The per-id route is not deleted — it is `--probe`, which reports what it found
rather than guessing, so the day Anubis is reconfigured this is one flag away.

What is deliberately absent
---------------------------
No fallback that invents a point. No nearest-name matching. No "if the id does
not resolve, use the region centroid". Every failure path here exits non-zero.
An empty map is a correct map; a plausible one is not.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .places import load_places, iter_places

GAZETTEER_PATH = Path("data/gazetteer.json")
SEED_CORPUS_DIR = Path("data/seed_corpus")

DUMP_BASE = "https://atlantides.org/downloads/pleiades/dumps/"
DUMP_LATEST = DUMP_BASE + "pleiades-places-latest.csv.gz"
PLEIADES_JSON = "https://pleiades.stoa.org/places/{pid}/json"

# The licence is recorded verbatim from the publisher or it is not recorded.
# This sentinel is what an unfilled cache holds, and `check` fails on it — the
# same discipline as `calibrated: false` in the confidence profiles, which is
# there so a guess can never be mistaken for a measurement.
LICENCE_UNCONFIRMED = "UNCONFIRMED — record the licence text verbatim from the publisher"

# Column names are DISCOVERED from the dump's header row, never assumed. The
# dumps README (last modified 2022-11-07) documents `id`, `title`,
# `description`, `path`, `timePeriods` and `featureTypes` for the places table
# and does not mention coordinate columns at all, while the file itself is
# regenerated daily. A parser written from that README would be a parser written
# against documentation rather than against data. These are candidates, in
# preference order; a logical field that matches nothing is a loud failure that
# prints the header it actually saw.
COLUMN_CANDIDATES: dict[str, tuple[str, ...]] = {
    "id": ("id",),
    "title": ("title",),
    "description": ("description",),
    "lat": ("reprLat", "repr_lat", "representative_latitude", "y"),
    "lon": ("reprLong", "reprLon", "repr_long", "representative_longitude", "x"),
    "bbox": ("bbox", "extent"),
    "min_lon": ("minLong", "minLon", "min_long"),
    "min_lat": ("minLat", "min_lat"),
    "max_lon": ("maxLong", "maxLon", "max_long"),
    "max_lat": ("maxLat", "max_lat"),
    "time_periods": ("timePeriods", "time_periods"),
    "feature_types": ("featureTypes", "feature_types"),
    "path": ("path",),
    # CC BY requires appropriate credit, and Pleiades credits the individual
    # authors and contributors of each place rather than the project as a whole.
    # Captured in the same pass as the coordinates because the alternative is
    # re-extracting the whole dump later to attribute one point.
    "authors": ("authors",),
    "creators": ("creators",),
}

# Without these the dump is not usable and the run stops before writing anything.
REQUIRED_LOGICAL = ("id", "title")


class GazetteerError(RuntimeError):
    pass


def require_file(path: Path, what: str, hint: str = "") -> Path:
    """Every path this module is handed goes through here.

    A `FileNotFoundError` traceback names the failing library call and not the
    thing the reader needs: which path was tried, what it resolved to, and where
    the file was supposed to come from. Every command here takes a path to
    something the user has just saved or downloaded somewhere else, so this is
    the single most likely failure in the module.

    Written once as a helper rather than three times as a check, because the
    first version of this fix was applied to `--record-licence` alone and
    `--inspect` produced the identical traceback the same evening. Fixing an
    instance is not fixing the class — the standing lesson from Part 4's
    `AmbiguousParameter`, arriving here in its most ordinary form.
    """
    if not path.exists():
        message = f"no {what} at '{path}'."
        # Both of these are only true of a RELATIVE path. Printed against an
        # absolute one, "resolved to <the same string>" is noise and "the path
        # is relative to where you ran this" is false — a message naming a cause
        # that does not apply, which is the defect family this repository has
        # recorded three times and which this very message walked into.
        if not path.is_absolute():
            message += (
                f" It resolved to '{path.resolve()}'; the path is relative to "
                f"the directory you ran this from."
            )
        elif path.parent.exists():
            # The directory is there and the file is not, so the likeliest
            # cause is the filename, not the location. Say what IS there.
            siblings = sorted(p.name for p in path.parent.glob(f"*{path.suffix}"))[:8]
            if siblings:
                message += f" That directory holds: {siblings}."
            else:
                message += f" '{path.parent}' exists but holds no {path.suffix} files."
        else:
            message += f" The directory '{path.parent}' does not exist either."
        if hint:
            message += f" {hint}"
        raise GazetteerError(message)
    return path


@dataclass(frozen=True)
class Entry:
    pleiades_id: str
    title: str
    description: str | None
    repr_point: list[float] | None      # [lon, lat], GeoJSON order
    bbox: list[float] | None            # [min_lon, min_lat, max_lon, max_lat]
    time_periods: str | None
    feature_types: str | None
    authors: str | None
    creators: str | None
    dump_date: str
    retrieved: str

    @property
    def has_point(self) -> bool:
        return self.repr_point is not None

    @property
    def has_extent(self) -> bool:
        return self.bbox is not None


# --------------------------------------------------------------------------
# The cache on disk
# --------------------------------------------------------------------------

def empty_cache() -> dict[str, Any]:
    return {
        "source": {
            "name": "Pleiades",
            "dump_url": None,
            "dump_date": None,
            "retrieved": None,
            "columns_observed": [],
            "column_map": {},
        },
        "licence": {
            "text": LICENCE_UNCONFIRMED,
            "source_url": None,
            "recorded": None,
        },
        "places": {},
    }


def load_cache(path: Path = GAZETTEER_PATH) -> dict[str, Any]:
    if not path.exists():
        return empty_cache()
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("source", "licence", "places"):
        if key not in data:
            raise GazetteerError(f"{path}: cache is missing the '{key}' block")
    return data


def write_cache(cache: dict[str, Any], path: Path = GAZETTEER_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def entries(cache: dict[str, Any]) -> dict[str, Entry]:
    out: dict[str, Entry] = {}
    for pid, raw in cache["places"].items():
        out[pid] = Entry(
            pleiades_id=raw["pleiades_id"],
            title=raw["title"],
            description=raw.get("description"),
            repr_point=raw.get("repr_point"),
            bbox=raw.get("bbox"),
            time_periods=raw.get("time_periods"),
            feature_types=raw.get("feature_types"),
            authors=raw.get("authors"),
            creators=raw.get("creators"),
            dump_date=raw["dump_date"],
            retrieved=raw["retrieved"],
        )
        if out[pid].pleiades_id != pid:
            raise GazetteerError(
                f"cache key '{pid}' does not match its entry's pleiades_id "
                f"'{out[pid].pleiades_id}'"
            )
    return out


def resolve(pleiades_id: str, cache: dict[str, Any]) -> Entry:
    """The only way to get a coordinate. Raises rather than returning None.

    A caller that could receive None is a caller that could carry on with a
    missing point and render something anyway.
    """
    found = entries(cache).get(pleiades_id)
    if found is None:
        raise GazetteerError(
            f"pleiades_id '{pleiades_id}' is not in the gazetteer cache. Run "
            f"`python -m ingest.gazetteer --refresh` to look it up. It has NOT "
            f"been guessed."
        )
    return found


# --------------------------------------------------------------------------
# Reading a dump
# --------------------------------------------------------------------------

def map_columns(header: Iterable[str]) -> dict[str, str]:
    header = list(header)
    lowered = {h.lower(): h for h in header}
    mapping: dict[str, str] = {}
    for logical, candidates in COLUMN_CANDIDATES.items():
        for cand in candidates:
            if cand in header:
                mapping[logical] = cand
                break
            if cand.lower() in lowered:
                mapping[logical] = lowered[cand.lower()]
                break

    missing = [k for k in REQUIRED_LOGICAL if k not in mapping]
    if missing:
        raise GazetteerError(
            f"dump header lacks column(s) for {missing}. Observed header: "
            f"{header}. Candidates tried: "
            f"{ {k: COLUMN_CANDIDATES[k] for k in missing} }. Fix "
            f"COLUMN_CANDIDATES against the header above rather than guessing."
        )

    has_point = "lat" in mapping and "lon" in mapping
    has_corners = all(k in mapping for k in ("min_lon", "min_lat", "max_lon", "max_lat"))
    if not has_point and "bbox" not in mapping and not has_corners:
        raise GazetteerError(
            f"dump header carries no geometry: no representative point, no "
            f"bbox, no corner columns. Observed header: {header}. A gazetteer "
            f"that cannot supply a coordinate is not a gazetteer, and the "
            f"alternative — authoring one — is what W1 forbids."
        )
    return mapping


def _float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _bbox_from_row(row: dict[str, str], cmap: dict[str, str]) -> list[float] | None:
    if "bbox" in cmap:
        raw = (row.get(cmap["bbox"]) or "").strip()
        if raw:
            parts = [p for p in raw.replace(",", " ").split() if p]
            nums = [_float(p) for p in parts]
            if len(nums) == 4 and all(n is not None for n in nums):
                return [float(n) for n in nums]  # type: ignore[arg-type]
    corners = ("min_lon", "min_lat", "max_lon", "max_lat")
    if all(k in cmap for k in corners):
        nums = [_float(row.get(cmap[k])) for k in corners]
        if all(n is not None for n in nums):
            return [float(n) for n in nums]  # type: ignore[arg-type]
    return None


def _open_dump(path: Path) -> io.TextIOWrapper:
    require_file(
        path,
        "Pleiades dump",
        f"Download a DATED places dump from {DUMP_BASE} — open that index and "
        f"take the most recent 'pleiades-places-<YYYYMMDD>.csv.gz' (~6.5 MB) "
        f"that is actually listed there. Do not construct the filename from a "
        f"date: the places CSVs and the JSON dumps are regenerated on different "
        f"schedules and sit in different directories, so a plausible-looking "
        f"name can 404.",
    )
    raw = gzip.open(path, "rb") if path.suffix == ".gz" else path.open("rb")
    return io.TextIOWrapper(raw, encoding="utf-8", newline="")


def read_dump(
    path: Path,
    wanted: set[str] | None = None,
) -> tuple[dict[str, dict[str, Any]], list[str], dict[str, str]]:
    """Extract `wanted` ids from a Pleiades places dump.

    Returns (rows by id, observed header, column map). Nothing is written and
    nothing is dated here — that is `refresh`'s job, so this function can be
    used by `--inspect` without touching the cache.
    """
    with _open_dump(path) as handle:
        reader = csv.DictReader(handle)
        header = list(reader.fieldnames or [])
        if not header:
            raise GazetteerError(f"{path}: no header row")
        cmap = map_columns(header)

        found: dict[str, dict[str, Any]] = {}
        for row in reader:
            pid = (row.get(cmap["id"]) or "").strip()
            if not pid:
                continue
            if wanted is not None and pid not in wanted:
                continue
            lat = _float(row.get(cmap["lat"])) if "lat" in cmap else None
            lon = _float(row.get(cmap["lon"])) if "lon" in cmap else None
            found[pid] = {
                "pleiades_id": pid,
                "title": (row.get(cmap["title"]) or "").strip(),
                "description": (row.get(cmap["description"]) or "").strip() or None
                if "description" in cmap else None,
                "repr_point": [lon, lat] if lat is not None and lon is not None else None,
                "bbox": _bbox_from_row(row, cmap),
                "time_periods": (row.get(cmap["time_periods"]) or "").strip() or None
                if "time_periods" in cmap else None,
                "feature_types": (row.get(cmap["feature_types"]) or "").strip() or None
                if "feature_types" in cmap else None,
                "authors": (row.get(cmap["authors"]) or "").strip() or None
                if "authors" in cmap else None,
                "creators": (row.get(cmap["creators"]) or "").strip() or None
                if "creators" in cmap else None,
            }
            if wanted is not None and len(found) == len(wanted):
                break
    return found, header, cmap


def dump_date_from_name(path: Path) -> str:
    """`pleiades-places-20260812.csv.gz` -> `2026-08-12`.

    A dump named `latest` has no date in it, and a snapshot with no date is the
    exact defect this repository has recorded five times. Fail rather than
    stamp today's date on a file that may be weeks old.
    """
    stem = path.name
    for token in stem.replace(".", "-").replace("_", "-").split("-"):
        if len(token) == 8 and token.isdigit():
            return f"{token[0:4]}-{token[4:6]}-{token[6:8]}"
    raise GazetteerError(
        f"cannot read a dump date from '{path.name}'. Download the dated file "
        f"(e.g. pleiades-places-20260812.csv.gz), not '...-latest...': a cache "
        f"whose snapshot date is unknown cannot say what it is comparable with."
    )


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def wanted_ids(corpus_dir: Path = SEED_CORPUS_DIR) -> set[str]:
    by_doc = load_places(corpus_dir)
    return {p.pleiades_id for p in iter_places(by_doc) if p.pleiades_id}


def cmd_inspect(dump: Path) -> int:
    with _open_dump(dump) as handle:
        reader = csv.DictReader(handle)
        header = list(reader.fieldnames or [])
        first = next(reader, None)
    print(f"dump: {dump}")
    print(f"columns ({len(header)}): {header}")
    try:
        cmap = map_columns(header)
    except GazetteerError as exc:
        print(f"\nCOLUMN MAPPING FAILED\n  {exc}")
        return 1
    print(f"column map: {json.dumps(cmap, indent=2, sort_keys=True)}")
    if first:
        print(f"first row: {json.dumps(first, ensure_ascii=False, indent=2)[:1500]}")
    return 0


def cmd_refresh(dump: Path, corpus_dir: Path, path: Path) -> int:
    # Existence first, so a missing file is reported as a missing file rather
    # than as whatever the filename check happens to notice about its name.
    _open_dump(dump).close()
    wanted = wanted_ids(corpus_dir)
    if not wanted:
        print("no pleiades_id appears in the corpus yet — nothing to look up.")
        return 0

    dump_date = dump_date_from_name(dump)
    found, header, cmap = read_dump(dump, wanted)

    cache = load_cache(path)
    today = _today()
    for pid, row in found.items():
        cache["places"][pid] = {**row, "dump_date": dump_date, "retrieved": today}
    cache["source"].update(
        {
            "name": "Pleiades",
            "dump_url": DUMP_BASE + dump.name,
            "dump_date": dump_date,
            "retrieved": today,
            "columns_observed": header,
            "column_map": cmap,
        }
    )
    write_cache(cache, path)

    missing = sorted(wanted - set(found))
    print(f"looked up {len(found)} of {len(wanted)} ids from {dump.name} ({dump_date})")
    no_geometry = [p for p, r in found.items() if not r["repr_point"] and not r["bbox"]]
    if no_geometry:
        print(f"  entries with neither point nor extent: {sorted(no_geometry)}")
    if missing:
        print(f"\nUNRESOLVED ({len(missing)}): {missing}")
        print("  These ids are not in the dump. They have not been guessed.")
        return 1
    return 0


def cmd_record_licence(licence_file: Path, source_url: str, path: Path) -> int:
    require_file(licence_file, "licence file",
                 "Save the licence terms verbatim to that path.")
    # utf-8-sig, not utf-8: this text is pasted out of a browser and saved on
    # Windows, where a BOM is the default rather than the exception. It is
    # stripped if present and changes nothing if absent — but recorded verbatim,
    # a leading U+FEFF would sit invisibly at the front of the licence forever.
    text = licence_file.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise GazetteerError(f"{licence_file} is empty")
    cache = load_cache(path)
    cache["licence"] = {
        "text": text,
        "source_url": source_url,
        "recorded": _today(),
    }
    write_cache(cache, path)
    print(f"licence recorded verbatim from {source_url} ({len(text)} chars)")
    return 0


def cmd_record_declaration(decl_file: Path, source_url: str, path: Path) -> int:
    """Record the publisher's own statement that this licence applies.

    Two different claims, deliberately stored apart:

      licence.text            — what CC BY 3.0 US says (from creativecommons.org)
      licence.declared_by     — that Pleiades says it governs their content

    Collapsing them would put the publisher's URL on the licensor's words, which
    is the one field whose entire purpose is to say where something came from.
    """
    require_file(decl_file, "declaration file",
                 "Save the publisher's statement verbatim to that path.")
    text = decl_file.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise GazetteerError(f"{decl_file} is empty")
    cache = load_cache(path)
    if "licence" not in cache or not cache["licence"].get("text"):
        raise GazetteerError("record the licence itself before its declaration")
    cache["licence"]["declared_by"] = {
        "publisher": "Pleiades",
        "text": text,
        "source_url": source_url,
        "recorded": _today(),
    }
    write_cache(cache, path)
    print(f"declaration recorded verbatim from {source_url} ({len(text)} chars)")
    return 0


def cmd_check(corpus_dir: Path, path: Path) -> int:
    """Every locatable placement resolves, and the licence is real.

    This is the assertion G1 criterion 2 is measured against, and it exits
    non-zero rather than warning. A warning would let a build with an unsourced
    point succeed, which is the only thing W1 is trying to make impossible.
    """
    failures: list[str] = []
    by_doc = load_places(corpus_dir)
    cache = load_cache(path)
    known = entries(cache)

    places = list(iter_places(by_doc))
    locatable = [p for p in places if p.locatable]

    for p in locatable:
        entry = known.get(p.pleiades_id or "")
        if entry is None:
            failures.append(f"{p.key}: pleiades_id '{p.pleiades_id}' is not cached")
            continue
        if not entry.has_point and not entry.has_extent:
            failures.append(
                f"{p.key}: '{p.pleiades_id}' ({entry.title}) resolves to no "
                f"point and no extent — nothing to draw, and nothing may be "
                f"invented to replace it"
            )

    licence = cache.get("licence", {})
    if not licence.get("text") or licence["text"] == LICENCE_UNCONFIRMED:
        failures.append(
            "licence is unconfirmed. Read the licence and attribution statement "
            "on the Pleiades site, save it to a file, and run "
            "`--record-licence <file> --licence-source-url <url>`. It is "
            "recorded verbatim or not at all — the same rule that forbids "
            "writing a place id from memory."
        )
    elif not (licence.get("declared_by") or {}).get("text"):
        # Knowing what CC BY says is not knowing that Pleiades chose it. A cache
        # holding only the first is a cache asserting a licence on the strength
        # of somebody's recollection that it applies.
        failures.append(
            "the licence text is recorded but the publisher's declaration is "
            "not. Save the statement from https://pleiades.stoa.org/credits and "
            "run `--record-declaration <file> --declaration-source-url <url>`."
        )

    stale = sorted(
        {
            e.dump_date
            for e in known.values()
            if cache["source"].get("dump_date")
            and e.dump_date != cache["source"]["dump_date"]
        }
    )

    print(f"placements: {len(places)}   locatable: {len(locatable)}   cached ids: {len(known)}")
    print(f"documents with a placement: {sum(1 for v in by_doc.values() if v)} of {len(by_doc)}")

    # A note rather than a failure. CC BY asks for appropriate credit and
    # Pleiades credits per place, so an entry with neither authors nor creators
    # is a point the UI cannot attribute — but whether that is a defect in the
    # dump or a genuinely uncredited place is not something this check can tell,
    # and a guard that cannot tell those apart would name the wrong cause.
    unattributed = sorted(
        pid for pid, e in known.items() if not e.authors and not e.creators
    )
    if unattributed:
        print(
            f"note: {len(unattributed)} cached entries carry no authors or "
            f"creators, so they cannot be attributed per place: {unattributed[:5]}"
        )
    if stale:
        print(f"note: entries from earlier dump dates are present: {stale}")

    if failures:
        print(f"\nFAILED ({len(failures)})")
        for f in failures:
            print(f"  x {f}")
        return 1
    print("\nEvery placement resolves to a cached, dated gazetteer entry.")
    return 0


def cmd_probe(pleiades_id: str) -> int:
    """The per-id route from PHASE2_PLAN A1, kept as a reporter, not a fallback.

    It never writes to the cache. Its job is to say what the endpoint actually
    returned, so that "Pleiades is behind a bot wall" and "this id does not
    exist" can never again be the same message.
    """
    url = PLEIADES_JSON.format(pid=pleiades_id)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "mundus-ulterior/0.1 (research prototype; contact via repository)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            body = resp.read()
    except urllib.error.HTTPError as exc:
        print(f"probe {url}\n  HTTP {exc.code} {exc.reason}")
        return 1
    except Exception as exc:  # noqa: BLE001 — the point is to report, not classify
        print(f"probe {url}\n  transport failure: {type(exc).__name__}: {exc}")
        return 1

    print(f"probe {url}\n  HTTP {status}, {len(body)} bytes")
    if not body:
        print(
            "  empty body. This is the Anubis signature observed 2026-08-12: "
            "the endpoint answers, and answers with nothing. NOT evidence that "
            "the id is wrong."
        )
        return 1
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        head = body[:200].decode("utf-8", "replace")
        print(f"  body is not JSON. First 200 bytes: {head!r}")
        if b"Anubis" in body or b"not a bot" in body:
            print("  -> anti-bot challenge page. The bulk dump route is the answer.")
        return 1
    print(f"  JSON keys: {sorted(data)[:20]}")
    return 0


def cmd_stats(path: Path, corpus_dir: Path) -> int:
    cache = load_cache(path)
    known = entries(cache)
    by_doc = load_places(corpus_dir)
    places = list(iter_places(by_doc))

    grounds: dict[str, int] = {}
    for p in places:
        grounds[p.ground] = grounds.get(p.ground, 0) + 1

    print(f"gazetteer:  {path}")
    print(f"  source:   {cache['source'].get('dump_url')}")
    print(f"  snapshot: {cache['source'].get('dump_date')} (retrieved {cache['source'].get('retrieved')})")
    licence_text = cache.get("licence", {}).get("text", "")
    confirmed = bool(licence_text) and licence_text != LICENCE_UNCONFIRMED
    declared = bool((cache.get("licence", {}).get("declared_by") or {}).get("text"))
    print(f"  licence:  {'recorded' if confirmed else 'UNCONFIRMED'}"
          f" ({cache.get('licence', {}).get('source_url')})")
    print(f"  declared: {'recorded' if declared else 'NOT RECORDED'}"
          f" ({(cache.get('licence', {}).get('declared_by') or {}).get('source_url')})")
    print(f"  entries:  {len(known)}  (with point: {sum(1 for e in known.values() if e.has_point)},"
          f" with extent: {sum(1 for e in known.values() if e.has_extent)})")
    print(f"corpus:     {len(by_doc)} records, {sum(1 for v in by_doc.values() if v)} placed")
    print(f"  placements by ground: {dict(sorted(grounds.items()))}")
    print(f"  contested: {sum(1 for p in places if p.contested)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--gazetteer", type=Path, default=GAZETTEER_PATH)
    ap.add_argument("--corpus", type=Path, default=SEED_CORPUS_DIR)
    ap.add_argument("--dump", type=Path, help="local Pleiades places dump (.csv or .csv.gz)")
    ap.add_argument("--inspect", action="store_true",
                    help="print the dump's header and first row; write nothing")
    ap.add_argument("--refresh", action="store_true",
                    help="extract the corpus's ids from --dump into the cache")
    ap.add_argument("--check", action="store_true",
                    help="every placement resolves, and the licence is recorded")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--probe", metavar="PLEIADES_ID",
                    help="report what the per-id endpoint returns; never caches")
    ap.add_argument("--record-licence", type=Path, metavar="FILE",
                    help="file holding the licence terms, verbatim")
    ap.add_argument("--licence-source-url", default=None)
    ap.add_argument("--record-declaration", type=Path, metavar="FILE",
                    help="file holding the publisher's statement that this "
                         "licence governs their content, verbatim")
    ap.add_argument("--declaration-source-url", default=None)
    args = ap.parse_args(argv)

    try:
        if args.probe:
            return cmd_probe(args.probe)
        if args.inspect:
            if not args.dump:
                ap.error("--inspect needs --dump")
            return cmd_inspect(args.dump)
        if args.refresh:
            if not args.dump:
                ap.error(
                    "--refresh needs --dump. Download a DATED dump from "
                    + DUMP_BASE
                )
            return cmd_refresh(args.dump, args.corpus, args.gazetteer)
        if args.record_licence:
            if not args.licence_source_url:
                ap.error("--record-licence needs --licence-source-url")
            return cmd_record_licence(
                args.record_licence, args.licence_source_url, args.gazetteer
            )
        if args.record_declaration:
            if not args.declaration_source_url:
                ap.error("--record-declaration needs --declaration-source-url")
            return cmd_record_declaration(
                args.record_declaration, args.declaration_source_url, args.gazetteer
            )
        if args.stats:
            return cmd_stats(args.gazetteer, args.corpus)
        return cmd_check(args.corpus, args.gazetteer)
    except GazetteerError as exc:
        print(f"gazetteer error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
