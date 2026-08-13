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
    # `extent` was a bbox candidate until the dump was inspected on 2026-08-12.
    # It is not a bbox — it holds GeoJSON:
    #   {"type": "Point", "coordinates": [13.4119837, 42.082885]}
    # Parsed as four numbers it yields nothing, silently. Removed rather than
    # taught to read GeoJSON, because `bbox` is present and carries the value
    # directly; a second geometry parser would be a second thing to keep right.
    "bbox": ("bbox",),
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
    # Added after inspecting the 2026-08-10 dump, on the same argument as
    # authors/creators: capture in the one pass, or re-extract 6.5 MB later to
    # answer a question the row already contained.
    #
    # These four are not decoration. The dump's first row is "Borgo Medievale",
    # minDate 640 / maxDate 1453, timePeriods "M" — Pleiades is **not** confined
    # to antiquity, so an id can resolve perfectly and still denote a place
    # attested only centuries after the record citing it. Mundus Ulterior covers
    # 27 BC to AD 1204; a findspot whose gazetteer entry is mediaeval-only is a
    # misidentification that resolves cleanly, and nothing else in the pipeline
    # would notice.
    #
    # `locationPrecision` ("precise" in that row) is Pleiades' own statement of
    # how well it knows the location, which is a different axis from `ground` —
    # ours records how WE arrived at the placement, theirs how well THEY know
    # the point. A5 needs both to render honestly.
    "min_date": ("minDate",),
    "max_date": ("maxDate",),
    "time_period_keys": ("timePeriodsKeys",),
    "location_precision": ("locationPrecision",),
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
    gazetteer: str
    gazetteer_id: str
    title: str
    description: str | None
    repr_point: list[float] | None      # [lon, lat], GeoJSON order
    bbox: list[float] | None            # [min_lon, min_lat, max_lon, max_lat]
    time_periods: str | None
    feature_types: str | None
    authors: str | None
    creators: str | None
    min_date: str | None
    max_date: str | None
    time_period_keys: str | None
    location_precision: str | None
    dump_date: str
    retrieved: str

    @property
    def has_point(self) -> bool:
        return self.repr_point is not None

    @property
    def has_extent(self) -> bool:
        """Any bbox at all — enough to say the entry is not empty."""
        return self.bbox is not None

    @property
    def has_area(self) -> bool:
        """A bbox with actual area, which is a different question.

        Observed on the first real entry cached (Hoby, 98983): Pleiades writes a
        **degenerate** bbox for a point place — `[11.230919, 54.740603,
        11.230919, 54.740603]`, min equal to max. It is the representative point
        wearing a rectangle.

        This matters at A5 and would have been discovered there. `PHASE2_PLAN.md`
        says a `regional` placement renders as an extent and never as a pin; if
        `has_extent` were the test, a point place would render as a box of zero
        size and a regional place with only a degenerate bbox would render as
        nothing while claiming an extent. Two different things called by one
        name is the `translation_chunk` / `translation_chunk_id` trap that W2 is
        already scheduled to pay off.
        """
        if self.bbox is None:
            return False
        min_lon, min_lat, max_lon, max_lat = self.bbox
        return max_lon > min_lon and max_lat > min_lat


# --------------------------------------------------------------------------
# The cache on disk
# --------------------------------------------------------------------------

def empty_cache() -> dict[str, Any]:
    return {
        # One block per gazetteer. A single `source` block was correct while
        # there was one gazetteer and would have become a lie the moment there
        # were two — the same shape as the field name it accompanies.
        "sources": {},
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
    for key in ("sources", "licence", "places"):
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
    """Cached entries keyed `<gazetteer>:<id>`.

    Namespaced because ids collide across gazetteers: Pleiades 98983 is Hoby on
    Lolland and GeoNames 98983 is something else entirely. A cache keyed on the
    bare number would serve one for the other and nothing would raise.
    """
    out: dict[str, Entry] = {}
    for key, raw in cache["places"].items():
        out[key] = Entry(
            gazetteer=raw["gazetteer"],
            gazetteer_id=raw["gazetteer_id"],
            title=raw["title"],
            description=raw.get("description"),
            repr_point=raw.get("repr_point"),
            bbox=raw.get("bbox"),
            time_periods=raw.get("time_periods"),
            feature_types=raw.get("feature_types"),
            authors=raw.get("authors"),
            creators=raw.get("creators"),
            min_date=raw.get("min_date"),
            max_date=raw.get("max_date"),
            time_period_keys=raw.get("time_period_keys"),
            location_precision=raw.get("location_precision"),
            dump_date=raw["dump_date"],
            retrieved=raw["retrieved"],
        )
        expected = f"{out[key].gazetteer}:{out[key].gazetteer_id}"
        if expected != key:
            raise GazetteerError(
                f"cache key '{key}' does not match its entry, which says "
                f"'{expected}'"
            )
    return out


def resolve(cache_key: str, cache: dict[str, Any]) -> Entry:
    """The only way to get a coordinate. Raises rather than returning None.

    A caller that could receive None is a caller that could carry on with a
    missing point and render something anyway.
    """
    found = entries(cache).get(cache_key)
    if found is None:
        raise GazetteerError(
            f"'{cache_key}' is not in the gazetteer cache. Run "
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
            def opt(logical: str) -> str | None:
                if logical not in cmap:
                    return None
                return (row.get(cmap[logical]) or "").strip() or None

            found[pid] = {
                "gazetteer": "pleiades",
                "gazetteer_id": pid,
                "title": (row.get(cmap["title"]) or "").strip(),
                "description": opt("description"),
                "repr_point": [lon, lat] if lat is not None and lon is not None else None,
                "bbox": _bbox_from_row(row, cmap),
                "time_periods": opt("time_periods"),
                "feature_types": opt("feature_types"),
                "authors": opt("authors"),
                "creators": opt("creators"),
                "min_date": opt("min_date"),
                "max_date": opt("max_date"),
                "time_period_keys": opt("time_period_keys"),
                "location_precision": opt("location_precision"),
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
    return {
        p.gazetteer_id for p in iter_places(by_doc)
        if p.gazetteer == "pleiades" and p.gazetteer_id
    }


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


def cmd_find(dump: Path, needle: str, names_dump: Path | None = None) -> int:
    """Search the snapshot for a place name. Reports; never caches, never guesses.

    Deliberately searches **the dump**, not the website. The cache is built from
    a dated snapshot, so a name found on live Pleiades is not necessarily a name
    in the file the coordinates will come from — and *a result is comparable
    only within the thing that produced it* is the lesson this repository has
    recorded five times. Searching the artefact you will cache from is the whole
    point.

    The places table carries only Pleiades' own modern title. Ancient attested
    spellings live in the separate names table, so `--names-dump` is worth
    passing whenever a search comes back empty: the corpus asks about Adulis and
    Muziris, and it is the names table that knows Ἀδουλί.
    """
    needle_cf = needle.casefold()
    # A bare number is almost always an id being checked, not a name. Matching
    # it against titles only would answer a question nobody asked.
    needle_id = needle.strip() if needle.strip().isdigit() else None
    hits: list[dict[str, str]] = []

    with _open_dump(dump) as handle:
        reader = csv.DictReader(handle)
        cmap = map_columns(list(reader.fieldnames or []))
        for row in reader:
            title = (row.get(cmap["title"]) or "")
            desc = (row.get(cmap.get("description", "")) or "")
            row_id = (row.get(cmap["id"]) or "").strip()
            where = "ID" if needle_id and row_id == needle_id else (
                "title" if needle_cf in title.casefold() else (
                    "description" if needle_cf in desc.casefold() else None
                )
            )
            if where:
                lat = _float(row.get(cmap["lat"])) if "lat" in cmap else None
                lon = _float(row.get(cmap["lon"])) if "lon" in cmap else None
                hits.append({
                    "id": (row.get(cmap["id"]) or "").strip(),
                    "title": title.strip(),
                    "matched": where,
                    "precision": (row.get(cmap.get("location_precision", "")) or "").strip(),
                    "dates": f"{(row.get(cmap.get('min_date','')) or '').strip()}.."
                             f"{(row.get(cmap.get('max_date','')) or '').strip()}",
                    "periods": (row.get(cmap.get("time_period_keys", "")) or "").strip(),
                    # The coordinate is what tells one Hoby from another. Without
                    # it a name match is a proxy for identity — the same shape as
                    # the Part 4 probe that passed on `doc_id` while pointing at
                    # the wrong passage.
                    "where": f"{lat:.3f},{lon:.3f}" if lat is not None and lon is not None else "—",
                    "desc": desc.strip(),
                })

    name_hits: list[str] = []
    if names_dump is not None:
        with _open_dump(names_dump) as handle:
            reader = csv.DictReader(handle)
            fields = list(reader.fieldnames or [])
            pid_col = "pid" if "pid" in fields else None
            attested = "nameAttested" if "nameAttested" in fields else None
            title_col = "title" if "title" in fields else None
            if not pid_col:
                raise GazetteerError(
                    f"names dump has no 'pid' column. Observed header: {fields}"
                )
            for row in reader:
                blob = " ".join(
                    (row.get(c) or "") for c in (attested, title_col) if c
                )
                # The dumps README says pid "can be joined to the id column of a
                # places table". Observed 2026-08-12, it holds a PATH —
                # '/places/39271' — which joins to nothing. Normalised here, and
                # recorded because it is the third thing that README has been
                # wrong about.
                raw_pid = (row.get(pid_col) or "").strip()
                pid = raw_pid.rstrip("/").rsplit("/", 1)[-1]
                if needle_id and pid == needle_id:
                    name_hits.append(
                        f"  {pid}  {(row.get(attested or '') or '').strip()!r} "
                        f"({(row.get(title_col or '') or '').strip()})"
                    )
                elif needle_cf in blob.casefold():
                    name_hits.append(
                        f"  {pid}  {(row.get(attested or '') or '').strip()!r} "
                        f"({(row.get(title_col or '') or '').strip()})"
                    )

    print(f"searching {dump.name} for {needle!r}")
    if hits:
        for h in sorted(hits, key=lambda h: (h["matched"] != "title", h["title"]))[:25]:
            print(
                f"  {h['id']:>10}  {h['title'][:36]:<36} {h['where']:>17}  "
                f"[{h['matched']}] {h['precision'] or '?'} {h['dates']} {h['periods']}"
            )
            if h["desc"]:
                print(f"             {h['desc'][:150]}")
        print(
            "  A name match is not an identification. Open the URI and confirm "
            "the coordinate and description describe YOUR site before using an id."
        )
        if len(hits) > 25:
            print(f"  … and {len(hits) - 25} more")
    else:
        print("  no place title or description matches.")

    if names_dump is not None:
        print(f"attested names in {names_dump.name}: {len(name_hits)}")
        for line in name_hits[:25]:
            print(line)
    elif not hits:
        print(
            "  Try --names-dump with pleiades-names-<date>.csv.gz from the same "
            "index: the places table holds only Pleiades' modern title, and an "
            "ancient name may be recorded only as an attested spelling."
        )

    if not hits and not name_hits:
        print(
            "\n  Nothing found. That is a RESULT, not a failure: if this "
            "snapshot has no entry, the honest ground is 'regional' with a note "
            "saying so. Do not reach for a nearby place."
        )
    return 0


def load_survey(path: Path) -> list[tuple[str, list[str]]]:
    """Read a survey file: `@label` lines group the terms that follow.

    Blank lines and `#` comments are ignored. A term appearing under two labels
    is searched once and reported under both.
    """
    require_file(path, "survey file")
    groups: list[tuple[str, list[str]]] = []
    label = "(unlabelled)"
    terms: list[str] = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("@"):
            if terms:
                groups.append((label, terms))
            label, terms = line[1:].strip(), []
            continue
        terms.append(line)
    if terms:
        groups.append((label, terms))
    if not groups:
        raise GazetteerError(f"{path}: no search terms")
    return groups


def cmd_survey(
    survey_path: Path, dump: Path, names_dump: Path | None = None
) -> int:
    """Search many names in ONE pass over the dump.

    Sixteen `--find` calls would decompress and scan 6.5 MB sixteen times and
    produce sixteen outputs to read. One pass produces one report, grouped by
    the record each term belongs to, which is the unit the curator actually
    works in.

    Reports only. Nothing is cached, nothing is chosen, and a group with no hits
    is printed as an empty group rather than omitted — an absent name must be
    visibly absent, or the reader silently reads a shorter list as a complete one.
    """
    groups = load_survey(survey_path)
    all_terms = {t.casefold(): t for _, ts in groups for t in ts}
    found: dict[str, list[str]] = {t: [] for t in all_terms}

    with _open_dump(dump) as handle:
        reader = csv.DictReader(handle)
        cmap = map_columns(list(reader.fieldnames or []))
        for row in reader:
            title = (row.get(cmap["title"]) or "")
            desc = (row.get(cmap.get("description", "")) or "")
            title_cf, desc_cf = title.casefold(), desc.casefold()
            for term_cf in all_terms:
                where = "title" if term_cf in title_cf else (
                    "desc" if term_cf in desc_cf else None
                )
                if not where:
                    continue
                lat = _float(row.get(cmap["lat"])) if "lat" in cmap else None
                lon = _float(row.get(cmap["lon"])) if "lon" in cmap else None
                coord = (f"{lat:.3f},{lon:.3f}"
                         if lat is not None and lon is not None else "UNLOCATED")
                found[term_cf].append(
                    f"      {(row.get(cmap['id']) or '').strip():>10}  "
                    f"{title[:34]:<34} {coord:>17}  [{where}] "
                    f"{(row.get(cmap.get('location_precision','')) or '').strip() or '?'} "
                    f"{(row.get(cmap.get('min_date','')) or '').strip()}.."
                    f"{(row.get(cmap.get('max_date','')) or '').strip()}  "
                    f"{(row.get(cmap.get('feature_types','')) or '').strip()}"
                )

    name_hits: dict[str, list[str]] = {t: [] for t in all_terms}
    if names_dump is not None:
        with _open_dump(names_dump) as handle:
            reader = csv.DictReader(handle)
            fields = list(reader.fieldnames or [])
            if "pid" not in fields:
                raise GazetteerError(f"names dump has no 'pid'. Header: {fields}")
            for row in reader:
                blob = " ".join(
                    (row.get(c) or "") for c in ("nameAttested", "title") if c in fields
                ).casefold()
                if not blob.strip():
                    continue
                pid = (row.get("pid") or "").strip().rstrip("/").rsplit("/", 1)[-1]
                for term_cf in all_terms:
                    if term_cf in blob:
                        name_hits[term_cf].append(
                            f"      {pid:>10}  name: "
                            f"{(row.get('nameAttested') or '').strip() or (row.get('title') or '').strip()}"
                        )

    total = 0
    for label, terms in groups:
        print(f"\n@{label}")
        for term in terms:
            key = term.casefold()
            place_lines = found.get(key, [])
            name_lines = name_hits.get(key, [])
            total += len(place_lines)
            if not place_lines and not name_lines:
                print(f"  {term!r}: nothing")
                continue
            print(f"  {term!r}: {len(place_lines)} place(s), {len(name_lines)} name(s)")
            for line in place_lines[:6]:
                print(line)
            if len(place_lines) > 6:
                print(f"      … and {len(place_lines) - 6} more")
            for line in name_lines[:6]:
                print(line)
            if len(name_lines) > 6:
                print(f"      … and {len(name_lines) - 6} more")

    print(
        f"\n{total} place hits across {len(all_terms)} terms in {dump.name}. "
        f"Nothing cached, nothing chosen. A name match is not an "
        f"identification — the coordinate decides."
    )
    return 0


def cmd_refresh(dump: Path, corpus_dir: Path, path: Path) -> int:
    # Existence first, so a missing file is reported as a missing file rather
    # than as whatever the filename check happens to notice about its name.
    _open_dump(dump).close()
    wanted = wanted_ids(corpus_dir)
    if not wanted:
        print("no Pleiades id appears in the corpus yet — nothing to look up.")
        return 0

    dump_date = dump_date_from_name(dump)
    found, header, cmap = read_dump(dump, wanted)

    cache = load_cache(path)
    today = _today()
    for pid, row in found.items():
        cache["places"][f"pleiades:{pid}"] = {
            **row, "dump_date": dump_date, "retrieved": today
        }
    cache.setdefault("sources", {})["pleiades"] = (
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
        entry = known.get(p.cache_key or "")
        if entry is None:
            failures.append(f"{p.key}: '{p.cache_key}' is not cached")
            continue
        if not entry.has_point and not entry.has_extent:
            failures.append(
                f"{p.key}: '{p.cache_key}' ({entry.title}) resolves to no "
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

    sources = cache.get("sources", {})
    stale = sorted(
        {
            f"{e.gazetteer} {e.dump_date}"
            for e in known.values()
            if sources.get(e.gazetteer, {}).get("dump_date")
            and e.dump_date != sources[e.gazetteer]["dump_date"]
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
    for name, src in sorted(cache.get("sources", {}).items()):
        print(f"  source:   {name} — {src.get('dump_url')}")
        print(f"            snapshot {src.get('dump_date')} (retrieved {src.get('retrieved')})")
    if not cache.get("sources"):
        print("  source:   none yet")
    licence_text = cache.get("licence", {}).get("text", "")
    confirmed = bool(licence_text) and licence_text != LICENCE_UNCONFIRMED
    declared = bool((cache.get("licence", {}).get("declared_by") or {}).get("text"))
    print(f"  licence:  {'recorded' if confirmed else 'UNCONFIRMED'}"
          f" ({cache.get('licence', {}).get('source_url')})")
    print(f"  declared: {'recorded' if declared else 'NOT RECORDED'}"
          f" ({(cache.get('licence', {}).get('declared_by') or {}).get('source_url')})")
    print(f"  entries:  {len(known)}  (with point: {sum(1 for e in known.values() if e.has_point)},"
          f" with a bbox: {sum(1 for e in known.values() if e.has_extent)},"
          f" of which non-degenerate: {sum(1 for e in known.values() if e.has_area)})")
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
    ap.add_argument("--find", metavar="TEXT",
                    help="search the snapshot for a place name; never caches")
    ap.add_argument("--survey", type=Path, metavar="FILE",
                    help="search many names in one pass, grouped by record; "
                         "never caches")
    ap.add_argument("--names-dump", type=Path,
                    help="pleiades-names-<date>.csv.gz, to also search attested "
                         "ancient spellings")
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
        if args.find:
            if not args.dump:
                ap.error("--find needs --dump")
            return cmd_find(args.dump, args.find, args.names_dump)
        if args.survey:
            if not args.dump:
                ap.error("--survey needs --dump")
            return cmd_survey(args.survey, args.dump, args.names_dump)
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
