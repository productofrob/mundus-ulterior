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

from .places import GAZETTEERS, UNLOCATED_KEY, load_places, iter_places

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
    # attested only centuries after the record citing it, and nothing else in
    # the pipeline would notice.
    #
    # CORRECTED 2026-08-13, when A6 built the check this comment was arguing
    # for. The original went on: "Mundus Ulterior covers 27 BC to AD 1204; a
    # findspot whose gazetteer entry is mediaeval-only is a misidentification."
    # The first clause is right and the second does not follow from it — this
    # project runs to the Fourth Crusade, so Borgo Medievale's 640..1453
    # **overlaps the window by 564 years** and is not out of scope at all. The
    # example chosen to motivate the guard would have passed it. Caught by
    # `ingest/test_places.py::test_dates`, which used these very numbers as its
    # out-of-era fixture and found them in era.
    #
    # The real shape is subtler and is what `date_audit` implements: minDate and
    # maxDate are a HULL over the attested periods, so an entry attesting only
    # Achaemenid and modern reports -540..2100 and looks in scope while
    # attesting nothing between. See PROJECT_MIN_YEAR below.
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
# Dates: the window this project covers, and what a gazetteer entry attests
# --------------------------------------------------------------------------
#
# Mundus Ulterior covers **27 BC to AD 1204** — the founding of the Roman
# Empire to the Fourth Crusade's sack of Constantinople. That window is a
# property of the project, not of any record, and it is the only date this
# module compares against.
#
# It is NOT compared against the seed records' own `date` fields, and the
# reason is worth keeping. Those are free prose, written for a reader:
# "compiled 5th century CE; records an event of 166 CE", "deposited soon after
# 205 CE (dendrochronology of shield boards)". Parsing them into numeric ranges
# would be guessing, dressed as a check — and *a check that matches too broadly
# names the wrong cause* is the defect this repository has now paid for five
# times. The project's window needs no parsing and is the comparison the
# motivating case actually calls for.
PROJECT_MIN_YEAR = -27
PROJECT_MAX_YEAR = 1204


def _year(value: str | None) -> float | None:
    """Pleiades writes minDate/maxDate as strings; negative years are BC."""
    if value is None:
        return None
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def ranges_overlap(a: tuple[float, float], b: tuple[float, float]) -> bool:
    """Closed-interval overlap. Touching at a single year counts."""
    return a[0] <= b[1] and b[0] <= a[1]


def in_project_window(span: tuple[float, float]) -> bool:
    return ranges_overlap(span, (PROJECT_MIN_YEAR, PROJECT_MAX_YEAR))


def entry_hull(entry: Entry) -> tuple[float, float] | None:
    """The entry's `minDate..maxDate`, which is a HULL and not an attestation.

    Pleiades derives these two numbers from the entry's time periods, so for an
    entry attested in several *disjoint* periods the pair spans the gaps as
    well. The Ka'ba-ye Zartosht is the case that matters here: its periods are
    `achaemenid-central-asia` and `modern`, and the hull is -540..2100 — which
    covers the 3rd century AD without anything being attested there at all.

    So the hull answers only "could this entry possibly be in scope"; it takes
    `period_spans` to answer "is it".
    """
    lo, hi = _year(entry.min_date), _year(entry.max_date)
    if lo is None or hi is None:
        return None
    return (min(lo, hi), max(lo, hi))


def period_keys(entry: Entry) -> list[str]:
    raw = entry.time_period_keys or ""
    return [k.strip() for k in raw.split(",") if k.strip()]


# Verdicts from `date_audit`. Kept as a closed set for the same reason `ROLES`
# and `GROUNDS` are: the caller renders each one differently, and a verdict it
# cannot read would drop a placement out of the report without failing.
DATE_OK = "ok"                 # an attested period lies inside the window
DATE_OUTSIDE = "outside"       # the hull itself misses the window — a failure
DATE_HOLE = "hole"             # the hull covers, no attested period does — a note
DATE_UNKNOWN = "unknown"       # no period ranges cached, or keys never derived
DATE_NO_DATES = "no_dates"     # the entry carries none. Correct for GeoNames.


def date_audit(
    entry: Entry, ranges: dict[str, dict[str, Any]]
) -> tuple[str, str | None]:
    """Does this entry attest anything inside the project's window?

    Returns a verdict from the set above and, when there is something to say, a
    sentence naming what was found. The three interesting outcomes are kept
    apart deliberately — they have different causes and different severities:

    - `outside` is unambiguous. The entry's whole hull sits before 27 BC or
      after AD 1204, so nothing it attests can be what a record of this corpus
      is citing. This is the case `COLUMN_CANDIDATES` warns about above:
      "Borgo Medievale", minDate 640 / maxDate 1453 — a mediaeval-only entry
      that resolves perfectly and is a misidentification.
    - `hole` is the Ka'ba-ye Zartosht shape: the hull covers the era, but every
      period the gazetteer actually attests falls outside it. A NOTE and not a
      failure, because the placement can be perfectly correct — the ŠKZ really
      is carved on that monument — and what it means is that Pleiades attests
      the building narrowly, which is a prompt to look rather than a defect to
      fix. Same severity reasoning as the unrenderable-regional report below.
      Requires EVERY period to have a derived range; see below.
    - `unknown` is the honest answer when the period vocabulary has not been
      derived (`--refresh-periods`), when a key was ambiguous in the dump, or
      when a key simply never appears alone in it and so was never given a
      range. It is never silently treated as `ok`: a check that cannot tell
      must say so.

    **On the boundary between `hole` and `unknown`**, which the first real run
    got wrong. A `hole` is a positive claim — *nothing this entry attests is in
    era* — and it may only be made when every period is accounted for. If some
    period has no derived range, that period could be the one in era, and the
    verdict is `unknown` no matter how many of its siblings are known to be
    out. The first version returned `hole` as soon as no KNOWN period matched,
    which read as a finding about the gazetteer when it was really a gap in the
    vocabulary; it fired that way on the ŠKZ, whose `achaemenid-central-asia`
    appears in no single-period row of the 2026-08-10 dump and therefore has no
    derived range. Same shape as every other over-broad check here: it named a
    cause it had not established.
    """
    hull = entry_hull(entry)
    if hull is None:
        return DATE_NO_DATES, None

    if not in_project_window(hull):
        return DATE_OUTSIDE, (
            f"attested {hull[0]:.0f}..{hull[1]:.0f}, which lies entirely "
            f"outside this project's {PROJECT_MIN_YEAR}..{PROJECT_MAX_YEAR}. "
            f"The id resolves and the coordinate is real; the place is attested "
            f"only in periods no record here can be citing."
        )

    keys = period_keys(entry)
    if not keys or not ranges:
        return DATE_UNKNOWN, (
            "no attested periods to check"
            if not keys else
            "the Pleiades period vocabulary has not been derived — run "
            "`--refresh-periods --dump <dump>`"
        )

    known = [(k, ranges[k]) for k in keys if k in ranges]
    unknown = [k for k in keys if k not in ranges]
    if not known:
        return DATE_UNKNOWN, (
            f"none of its periods has a derived range ({', '.join(unknown)}) — "
            f"they were ambiguous in the dump or the vocabulary predates them"
        )

    for key, span in known:
        if in_project_window((span["min"], span["max"])):
            return DATE_OK, None

    outside_list = ", ".join(
        f"{k} ({r['min']:.0f}..{r['max']:.0f})" for k, r in known
    )

    # Every known period is out of era — but a period with no derived range
    # could be the one in era, so the `hole` claim cannot be made yet. Reported
    # as unknown, naming both halves so the reader can see how close it is.
    if unknown:
        return DATE_UNKNOWN, (
            f"its hull {hull[0]:.0f}..{hull[1]:.0f} covers this project's "
            f"window and every period with a derived range falls outside it "
            f"({outside_list}) — but {len(unknown)} period(s) have no derived "
            f"range ({', '.join(unknown)}), and one of those could be the one "
            f"in era. Not reported as out-of-era on that account."
        )

    return DATE_HOLE, (
        f"its hull {hull[0]:.0f}..{hull[1]:.0f} covers this project's window, "
        f"but every period it actually attests falls outside it: {outside_list}. "
        f"The hull spans the gap between them, so the entry looks in-scope and "
        f"attests nothing here."
    )


# --------------------------------------------------------------------------
# The cache on disk
# --------------------------------------------------------------------------

def empty_cache() -> dict[str, Any]:
    return {
        # One block per gazetteer. A single `source` block was correct while
        # there was one gazetteer and would have become a lie the moment there
        # were two — the same shape as the field name it accompanies.
        "sources": {},
        # Likewise, and this one WAS written flat and had to be migrated. See
        # `load_cache`: Pleiades is CC BY 3.0 US and GeoNames is CC BY 4.0, and
        # a single `licence` block would have recorded the second over the
        # first with nothing anywhere noticing that half the points on the map
        # were now attributed to the wrong terms.
        "licences": {},
        "places": {},
    }


def _blank_licence() -> dict[str, Any]:
    return {"text": LICENCE_UNCONFIRMED, "source_url": None, "recorded": None}


def load_cache(path: Path = GAZETTEER_PATH) -> dict[str, Any]:
    if not path.exists():
        return empty_cache()
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("sources", "places"):
        if key not in data:
            raise GazetteerError(f"{path}: cache is missing the '{key}' block")

    # Migration, 2026-08-13: `licence` (flat, implicitly Pleiades) -> `licences`
    # keyed by gazetteer. Done on read rather than by a one-off script so a
    # cache written before the GeoNames reader existed still loads, and so the
    # old shape can never be silently reinterpreted as covering both sources.
    if "licences" not in data:
        legacy = data.pop("licence", None)
        data["licences"] = {"pleiades": legacy} if legacy else {}
    elif "licence" in data:
        raise GazetteerError(
            f"{path}: the cache carries BOTH 'licence' and 'licences'. One of "
            f"them is stale and there is no way to tell which. Delete the flat "
            f"'licence' block if 'licences' already holds it."
        )
    return data


def licence_for(cache: dict[str, Any], gazetteer: str) -> dict[str, Any]:
    return (cache.get("licences") or {}).get(gazetteer) or _blank_licence()


def licence_is_recorded(licence: dict[str, Any]) -> bool:
    text = licence.get("text")
    return bool(text) and text != LICENCE_UNCONFIRMED


def gazetteers_in_use(by_doc: dict[str, list]) -> set[str]:
    """Which gazetteers the corpus actually cites.

    The licence check is driven by this rather than by `GAZETTEERS`, so that
    declaring a gazetteer in the vocabulary does not oblige anyone to record a
    licence for a source no placement uses — and so that the day a placement
    DOES use it, the check starts failing on its own.
    """
    return {p.gazetteer for p in iter_places(by_doc) if p.gazetteer}


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


# --------------------------------------------------------------------------
# GeoNames
# --------------------------------------------------------------------------
#
# A second reader rather than a second parameter on the first, because the two
# dumps agree on almost nothing: Pleiades ships a CSV with a header row, one
# row per ancient place, carrying a bbox and attested date range. GeoNames
# ships headerless TSV, one row per modern feature, with no bbox, no dates and
# no per-record authorship. Threading both through `read_dump` would have meant
# a function whose every line asked which gazetteer it was serving.
#
# The columns are POSITIONAL and documented, so unlike Pleiades there is no
# header to discover them from. That removes the discovery step and does NOT
# remove the obligation behind it: the standing rule here is that a parser is
# written against data, not against documentation, and the Pleiades README was
# wrong three times. So the shape is VERIFIED on the first data row instead —
# field count, a numeric id, parseable coordinates, and a feature class from
# the documented set. A file that fails those is reported with the row that
# failed, rather than quietly yielding 19 fields of nonsense.
GEONAMES_FIELDS = (
    "geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude",
    "feature_class", "feature_code", "country_code", "cc2",
    "admin1", "admin2", "admin3", "admin4",
    "population", "elevation", "dem", "timezone", "modification_date",
)
GEONAMES_FEATURE_CLASSES = set("AHLPRSTUV")


def _geonames_rows(path: Path):
    """Yield (line_number, [fields]) from a GeoNames dump, .zip or .txt.

    The country dumps are distributed only as zip, and unzipping them by hand
    to feed this a .txt is a step at which the file's provenance is quietly
    lost — so the zip is read directly and its internal timestamp becomes the
    snapshot date (see `geonames_dump_date`).
    """
    require_file(
        path,
        "GeoNames dump",
        "Download a country file from https://download.geonames.org/export/dump/ "
        "— e.g. KR.zip for South Korea. Pass the .zip; it is read directly.",
    )
    if path.suffix.lower() == ".zip":
        import zipfile
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.lower().endswith(".txt")
                     and not n.lower().startswith("readme")]
            if not names:
                raise GazetteerError(
                    f"{path.name} holds no .txt member; it contains {zf.namelist()}"
                )
            with zf.open(names[0]) as handle:
                for i, raw in enumerate(io.TextIOWrapper(handle, encoding="utf-8"), 1):
                    yield i, raw.rstrip("\n").split("\t")
    else:
        with path.open(encoding="utf-8") as handle:
            for i, raw in enumerate(handle, 1):
                yield i, raw.rstrip("\n").split("\t")


def verify_geonames_shape(fields: list[str], line_no: int, path: Path) -> None:
    n = len(GEONAMES_FIELDS)
    if len(fields) != n:
        raise GazetteerError(
            f"{path.name}:{line_no}: expected {n} tab-separated fields, got "
            f"{len(fields)}. GeoNames' documented 'geoname' table has {n} "
            f"columns; this file does not match it. First fields seen: "
            f"{fields[:6]}"
        )
    if not fields[0].strip().isdigit():
        raise GazetteerError(
            f"{path.name}:{line_no}: first field '{fields[0][:40]}' is not a "
            f"numeric geonameid. If this file has a header row, GeoNames "
            f"dumps do not — check you have the right file."
        )
    if _float(fields[4]) is None or _float(fields[5]) is None:
        raise GazetteerError(
            f"{path.name}:{line_no}: latitude/longitude do not parse "
            f"({fields[4]!r}, {fields[5]!r})."
        )
    if fields[6].strip() and fields[6].strip() not in GEONAMES_FEATURE_CLASSES:
        raise GazetteerError(
            f"{path.name}:{line_no}: feature class {fields[6]!r} is not one of "
            f"{sorted(GEONAMES_FEATURE_CLASSES)}."
        )


def geonames_dump_date(path: Path) -> str:
    """The snapshot date for a GeoNames dump.

    GeoNames filenames carry no date — `KR.zip` is always "whatever is current
    today" — so `dump_date_from_name`'s rule cannot be applied, and its reason
    still can: a snapshot that cannot say when it was taken cannot say what it
    is comparable with.

    The zip's internal member timestamp is the publisher's own build time and
    is used. A bare .txt has only its filesystem mtime, which records when the
    CURATOR unzipped it and not when GeoNames built it, so that path requires
    an explicit `--geonames-date` rather than being guessed from the file.
    """
    if path.suffix.lower() != ".zip":
        raise GazetteerError(
            f"'{path.name}' is not a .zip, so it carries no publisher "
            f"timestamp. Pass the .zip as downloaded, or state the snapshot "
            f"date explicitly with --geonames-date YYYY-MM-DD. A file's mtime "
            f"is when you unzipped it, not when GeoNames built it."
        )
    import zipfile
    try:
        with zipfile.ZipFile(path) as zf:
            members = [i for i in zf.infolist() if i.filename.lower().endswith(".txt")
                       and not i.filename.lower().startswith("readme")]
            if not members:
                raise GazetteerError(f"{path.name} holds no .txt member")
            y, m, d = members[0].date_time[:3]
    except zipfile.BadZipFile as exc:
        # A raw BadZipFile traceback names the zip module and not the thing the
        # reader needs to know: that the file they downloaded is not the file
        # this expects. Same argument as `require_file`.
        raise GazetteerError(
            f"'{path.name}' is named like a zip but cannot be read as one "
            f"({exc}). Re-download it from "
            f"https://download.geonames.org/export/dump/ — a partial download "
            f"is the usual cause."
        ) from exc
    return f"{y:04d}-{m:02d}-{d:02d}"


def read_geonames_dump(
    path: Path, wanted: set[str] | None = None
) -> dict[str, dict[str, Any]]:
    """Extract `wanted` geonameids (or everything) from a GeoNames dump."""
    found: dict[str, dict[str, Any]] = {}
    checked = False
    for line_no, fields in _geonames_rows(path):
        if not fields or not fields[0].strip():
            continue
        if not checked:
            verify_geonames_shape(fields, line_no, path)
            checked = True
        gid = fields[0].strip()
        if wanted is not None and gid not in wanted:
            continue
        lat, lon = _float(fields[4]), _float(fields[5])
        row = dict(zip(GEONAMES_FIELDS, (f.strip() for f in fields)))
        found[gid] = {
            "gazetteer": "geonames",
            "gazetteer_id": gid,
            "title": row["name"],
            # GeoNames has no prose description. The feature code plus the
            # country is what actually distinguishes one 'Óc Eo' from another,
            # so that is what gets stored where a reader will look for it.
            "description": (
                f"{row['feature_class']}.{row['feature_code']} in "
                f"{row['country_code']}"
                + (f", admin1 {row['admin1']}" if row["admin1"] else "")
                + (f", population {row['population']}" if row["population"] not in ("", "0") else "")
            ),
            "repr_point": [lon, lat] if lat is not None and lon is not None else None,
            # GeoNames features are points. No bbox means `has_area` is false,
            # so a `regional` GeoNames placement can never draw an extent —
            # which `--check` already reports, and which is the honest result:
            # GeoNames does not publish the extent it would need.
            "bbox": None,
            "time_periods": None,
            "feature_types": f"{row['feature_class']}.{row['feature_code']}",
            # CC BY 4.0 credits the GeoNames project, not per-record
            # contributors, so there is no author here to record and its
            # absence is not the gap it would be in a Pleiades entry.
            "authors": None,
            "creators": None,
            # GeoNames records modern places and states no attestation range.
            # Left null rather than filled with the record's edit date, which
            # would read as "this place existed from 2019" on the map.
            "min_date": None,
            "max_date": None,
            "time_period_keys": None,
            "location_precision": None,
            "country_code": row["country_code"],
            "population": row["population"] or None,
            "modification_date": row["modification_date"] or None,
        }
        if wanted is not None and len(found) == len(wanted):
            break
    if not checked:
        raise GazetteerError(f"{path.name}: no data rows")
    return found


def cmd_geonames_find(dump: Path, needle: str, limit: int = 30) -> int:
    """Search a GeoNames dump by name or id. Reports; never caches, never guesses."""
    needle_cf = needle.casefold()
    needle_id = as_needle_id(needle)
    hits: list[tuple[int, dict[str, str]]] = []
    checked = False

    for line_no, fields in _geonames_rows(dump):
        if not fields or not fields[0].strip():
            continue
        if not checked:
            verify_geonames_shape(fields, line_no, dump)
            checked = True
        row = dict(zip(GEONAMES_FIELDS, (f.strip() for f in fields)))
        where = None
        if needle_id and row["geonameid"] == needle_id:
            where = "ID"
        elif needle_cf in row["name"].casefold():
            where = "name"
        elif needle_cf in row["asciiname"].casefold():
            where = "ascii"
        elif needle_cf in row["alternatenames"].casefold():
            where = "alt"
        if not where:
            continue
        # Rank an exact name match above an incidental substring of a
        # 10,000-character alternatenames field.
        exact = row["name"].casefold() == needle_cf or row["asciiname"].casefold() == needle_cf
        hits.append((
            (0 if where == "ID" else 1 if exact else 2 if where in ("name", "ascii") else 3),
            {**row, "matched": where},
        ))

    print(f"searching {dump.name} for {needle!r}")
    for _, h in sorted(hits, key=lambda t: (t[0], t[1]["name"]))[:limit]:
        lat, lon = _float(h["latitude"]), _float(h["longitude"])
        print(
            f"  {h['geonameid']:>10}  {h['name'][:30]:<30} "
            f"{lat:8.3f},{lon:9.3f}  {h['feature_class']}.{h['feature_code']:<6} "
            f"{h['country_code']} adm1={h['admin1'] or '-':<4} pop={h['population'] or '0':>9} "
            f"[{h['matched']}]"
        )
    if not hits:
        print(
            "  nothing matches. That is a RESULT, not a failure: if this "
            "snapshot has no entry, the honest ground is 'regional' with a "
            "note saying so. Do not reach for a nearby place."
        )
    else:
        print(
            f"  {len(hits)} hit(s). A name match is not an identification — "
            f"check the coordinate and the feature code before using an id. "
            f"A GeoNames point is a MODERN place; say in the note what it "
            f"denotes (a commune centroid is not an excavation trench)."
        )
    return 0


def cmd_refresh_geonames(
    dump: Path, corpus_dir: Path, path: Path, dump_date: str | None
) -> int:
    by_doc = load_places(corpus_dir)
    wanted = {
        p.gazetteer_id for p in iter_places(by_doc)
        if p.gazetteer == "geonames" and p.gazetteer_id
    }
    if not wanted:
        print("no GeoNames id appears in the corpus yet — nothing to look up.")
        return 0

    date = dump_date or geonames_dump_date(dump)
    found = read_geonames_dump(dump, wanted)

    cache = load_cache(path)
    today = _today()
    url = f"https://download.geonames.org/export/dump/{dump.name}"
    for gid, row in found.items():
        cache["places"][f"geonames:{gid}"] = {
            **row, "dump_date": date, "retrieved": today,
            # Which country file this row came from. Pleiades needs no
            # equivalent: it has one global dump, so `sources.pleiades` answers
            # the question for every Pleiades entry. GeoNames is one file per
            # country, and a single `sources.geonames.dump_url` would name
            # whichever file was refreshed LAST — so after KR then VN, the cache
            # would claim Gyeongju came from VN.zip. Third instance in this
            # repository of one container holding what is really N things:
            # `sources` (fixed at A2), `licence` (fixed today), and this.
            "source_file": dump.name,
        }
    source = cache.setdefault("sources", {}).setdefault("geonames", {})
    source.update({
        "name": "GeoNames",
        "dump_date": date,
        "retrieved": today,
        "columns_observed": list(GEONAMES_FIELDS),
        "column_map": {f: i for i, f in enumerate(GEONAMES_FIELDS)},
    })
    # Accumulated, not replaced. Every country file that has contributed a
    # cached entry stays on the record with its own snapshot date.
    source.setdefault("files", {})[dump.name] = {
        "dump_url": url, "dump_date": date, "retrieved": today,
    }
    write_cache(cache, path)

    # A GeoNames country file holds one country. The corpus cites places in
    # Korea, Vietnam, Thailand and Yemen, so EVERY per-country refresh will
    # necessarily fail to find the other countries' ids — and the first version
    # of this reported that as `UNRESOLVED` with "check you have the right
    # country file", to a curator who had exactly the right country file.
    #
    # *A check that matches too broadly names the wrong cause.* Fifth recorded
    # instance, and the first one written after the lesson was written down.
    #
    # The Pleiades path is right to fail here: `pleiades-places-<date>.csv.gz`
    # is a single global dump, so an id it does not hold is an id that does not
    # exist. The GeoNames path cannot make that inference from one file, so it
    # reports what it did, and completeness is left to `--check`, which is the
    # command that already asserts every cited id is cached and is the only
    # place with the whole picture.
    still_uncached = sorted(
        gid for gid in wanted
        if f"geonames:{gid}" not in cache["places"]
    )
    print(f"looked up {len(found)} of {len(wanted)} GeoNames ids from {dump.name} ({date})")
    elsewhere = sorted(wanted - set(found))
    if elsewhere:
        print(
            f"  {len(elsewhere)} cited id(s) are not in this country file: "
            f"{elsewhere}. Expected when the corpus spans several countries — "
            f"each needs its own dump."
        )
    if still_uncached:
        print(
            f"\n  {len(still_uncached)} cited id(s) are still not cached from "
            f"any dump: {still_uncached}"
        )
        print("  Run --refresh-geonames with the country file that holds them.")
    else:
        print("  every GeoNames id cited by the corpus is now cached.")
    # Never non-zero for "not in THIS file". `--check` fails on an uncached id
    # and names each one; two commands reporting the same fact differently is
    # how they come to disagree.
    return 0


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


# Pleiades retains deprecated records in the dump, titled so a reader can see
# what they are: "Erroneous Duplicate: Al-Hijr (Madâ'in Sâlih)", id 427224440,
# sitting at Hegra's own coordinate. Such a record resolves perfectly, carries a
# plausible point, and is exactly what Pleiades is telling you not to cite.
#
# Found 2026-08-13 while confirming Hegra, and only because the title was read.
# Nothing about an id says it is deprecated.
DEPRECATED_TITLE_MARKERS = ("erroneous duplicate", "deprecated", "do not use")


def looks_deprecated(title: str) -> bool:
    lowered = (title or "").casefold()
    return any(marker in lowered for marker in DEPRECATED_TITLE_MARKERS)


def match_row(
    row: dict[str, str],
    cmap: dict[str, str],
    needle_cf: str,
    needle_id: str | None,
) -> str | None:
    """Where, if anywhere, a term matches a dump row: 'ID', 'title' or 'desc'.

    ONE matcher, used by both `--find` and `--survey`.

    They had two, and they disagreed: `--find` matched a bare number against the
    id column and `--survey` did not, so a survey of ids reported `nothing` for
    ids that plainly exist — and worse, reported a *hit* where the number
    happened to appear inside another record's description. Plausible output,
    silently wrong, from the command recommended for exactly that job.

    Two implementations of one question is the `translation_chunk` trap and the
    `check_ui.mjs` / `build_ui_data.py` disagreement over again. The fix is not
    to correct the second copy; it is to stop having two.
    """
    if needle_id and (row.get(cmap["id"]) or "").strip() == needle_id:
        return "ID"
    if needle_cf in (row.get(cmap["title"]) or "").casefold():
        return "title"
    if "description" in cmap and needle_cf in (row.get(cmap["description"]) or "").casefold():
        return "desc"
    return None


def as_needle_id(term: str) -> str | None:
    """A bare number is an id being checked, not a name being searched."""
    term = term.strip()
    return term if term.isdigit() else None


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
    needle_id = as_needle_id(needle)
    hits: list[dict[str, str]] = []

    with _open_dump(dump) as handle:
        reader = csv.DictReader(handle)
        cmap = map_columns(list(reader.fieldnames or []))
        for row in reader:
            title = (row.get(cmap["title"]) or "")
            desc = (row.get(cmap.get("description", "")) or "")
            where = match_row(row, cmap, needle_cf, needle_id)
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
    # Same matcher as --find, so a numeric term is an id here too. It was not,
    # and a survey of ten real ids reported "nothing" for every one of them.
    needle_ids = {cf: as_needle_id(orig) for cf, orig in all_terms.items()}
    found: dict[str, list[str]] = {t: [] for t in all_terms}

    with _open_dump(dump) as handle:
        reader = csv.DictReader(handle)
        cmap = map_columns(list(reader.fieldnames or []))
        for row in reader:
            title = (row.get(cmap["title"]) or "")
            for term_cf in all_terms:
                where = match_row(row, cmap, term_cf, needle_ids[term_cf])
                if not where:
                    continue
                lat = _float(row.get(cmap["lat"])) if "lat" in cmap else None
                lon = _float(row.get(cmap["lon"])) if "lon" in cmap else None
                coord = (f"{lat:.3f},{lon:.3f}"
                         if lat is not None and lon is not None else "UNLOCATED")
                found[term_cf].append(
                    f"      {(row.get(cmap['id']) or '').strip():>10}  "
                    f"{'!DEPRECATED! ' if looks_deprecated(title) else ''}"
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


def derive_period_ranges(
    path: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, list], int, int]:
    """Derive each Pleiades period's date range FROM THE DUMP, not from docs.

    Returns (ranges, ambiguous, rows_read, single_period_rows).

    The method, and why it is sound: Pleiades computes each place's
    `minDate`/`maxDate` from the time periods it attests. So a row attesting
    **exactly one** period states that period's range outright — `Adouli`,
    periods `roman`, minDate -30 maxDate 300, says `roman = -30..300`. Reading
    thousands of such rows gives the vocabulary with no documentation involved.

    This is the same discipline as `map_columns`: *the parser is written
    against data, not against documentation.* The alternative was a hand-listed
    set of "periods that count as in-scope", which is a vocabulary written from
    memory against a publisher's open-ended list — the exact thing this module
    refuses for place ids, one level up.

    **Disagreement is never resolved by picking a winner.** If two single-period
    rows give different ranges for the same key, the key is recorded as
    ambiguous and given NO range, so every entry using it audits as `unknown`
    rather than being silently judged against a guess. A most-common-value rule
    would have been easy here and would have made the check assert something
    the dump does not say.
    """
    seen: dict[str, dict[tuple[float, float], int]] = {}
    rows_read = 0
    single = 0

    with _open_dump(path) as handle:
        reader = csv.DictReader(handle)
        header = list(reader.fieldnames or [])
        if not header:
            raise GazetteerError(f"{path}: no header row")
        cmap = map_columns(header)
        for logical in ("time_period_keys", "min_date", "max_date"):
            if logical not in cmap:
                raise GazetteerError(
                    f"{path}: the dump has no '{logical}' column, so period "
                    f"ranges cannot be derived from it. Observed header: "
                    f"{header}"
                )

        for row in reader:
            rows_read += 1
            raw = (row.get(cmap["time_period_keys"]) or "").strip()
            keys = [k.strip() for k in raw.split(",") if k.strip()]
            if len(keys) != 1:
                continue
            lo = _year((row.get(cmap["min_date"]) or "").strip() or None)
            hi = _year((row.get(cmap["max_date"]) or "").strip() or None)
            if lo is None or hi is None:
                continue
            single += 1
            span = (min(lo, hi), max(lo, hi))
            seen.setdefault(keys[0], {}).setdefault(span, 0)
            seen[keys[0]][span] += 1

    ranges: dict[str, dict[str, Any]] = {}
    ambiguous: dict[str, list] = {}
    for key, spans in sorted(seen.items()):
        if len(spans) == 1:
            (lo, hi), count = next(iter(spans.items()))
            ranges[key] = {"min": lo, "max": hi, "rows": count}
        else:
            ambiguous[key] = sorted(
                ({"min": lo, "max": hi, "rows": n} for (lo, hi), n in spans.items()),
                key=lambda s: -s["rows"],
            )
    return ranges, ambiguous, rows_read, single


def period_ranges_from_cache(cache: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return ((cache.get("periods") or {}).get("ranges")) or {}


def cmd_refresh_periods(dump: Path, path: Path) -> int:
    """Derive the period vocabulary from --dump and cache it, dated.

    Separate from `--refresh` because the two read the dump for different
    things and at different times: `--refresh` extracts the handful of ids the
    corpus cites and is run whenever a record gains a placement, while this
    reads every row to build a vocabulary that only changes when Pleiades
    changes it. Folding them together would have meant a full-dump scan on
    every id added.
    """
    _open_dump(dump).close()
    dump_date = dump_date_from_name(dump)
    ranges, ambiguous, rows_read, single = derive_period_ranges(dump)

    if not ranges:
        print(
            f"no period ranges could be derived from {dump.name}. Every row "
            f"attesting exactly one period is what this reads, and none was "
            f"found — the dump's shape has changed."
        )
        return 1

    cache = load_cache(path)
    cache["periods"] = {
        "ranges": ranges,
        # Recorded, not dropped. A key with no range makes every entry using it
        # audit as `unknown`, and the reason it has no range belongs next to it.
        "ambiguous": ambiguous,
        "derived_from": {
            "dump_file": dump.name,
            "dump_date": dump_date,
            "retrieved": _today(),
            "method": (
                "each period's range is taken from dump rows attesting exactly "
                "one period; a key whose rows disagree is recorded as ambiguous "
                "and given no range"
            ),
            "rows_read": rows_read,
            "single_period_rows": single,
        },
    }
    write_cache(cache, path)

    print(
        f"derived {len(ranges)} period range(s) from {dump.name} ({dump_date})\n"
        f"  {rows_read} rows read, {single} attesting exactly one period"
    )
    in_scope = sum(
        1 for r in ranges.values() if in_project_window((r["min"], r["max"]))
    )
    print(
        f"  {in_scope} of {len(ranges)} overlap this project's "
        f"{PROJECT_MIN_YEAR}..{PROJECT_MAX_YEAR}"
    )
    if ambiguous:
        print(
            f"\nnote: {len(ambiguous)} period key(s) had disagreeing rows and "
            f"were given NO range rather than a guessed one. Entries using them "
            f"audit as 'unknown':"
        )
        for key, spans in list(ambiguous.items())[:5]:
            shown = ", ".join(
                f"{s['min']:.0f}..{s['max']:.0f} ({s['rows']} rows)" for s in spans[:3]
            )
            print(f"  ~ {key}: {shown}")
    return 0


def _require_known_gazetteer(gazetteer: str) -> str:
    if gazetteer not in GAZETTEERS:
        raise GazetteerError(
            f"unknown gazetteer '{gazetteer}'; known: {sorted(GAZETTEERS)}. "
            f"A licence recorded against a name no placement can cite would "
            f"sit in the cache looking satisfied and cover nothing."
        )
    return gazetteer


def cmd_record_licence(
    gazetteer: str, licence_file: Path, source_url: str, path: Path
) -> int:
    _require_known_gazetteer(gazetteer)
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
    cache.setdefault("licences", {})[gazetteer] = {
        "text": text,
        "source_url": source_url,
        "recorded": _today(),
    }
    write_cache(cache, path)
    print(f"{gazetteer} licence recorded verbatim from {source_url} ({len(text)} chars)")
    return 0


def cmd_record_declaration(
    gazetteer: str, decl_file: Path, source_url: str, path: Path
) -> int:
    """Record the publisher's own statement that this licence applies.

    Two different claims, deliberately stored apart:

      licences[g].text        — what CC BY says (from creativecommons.org)
      licences[g].declared_by — that the publisher says it governs their content

    Collapsing them would put the publisher's URL on the licensor's words, which
    is the one field whose entire purpose is to say where something came from.
    """
    _require_known_gazetteer(gazetteer)
    require_file(decl_file, "declaration file",
                 "Save the publisher's statement verbatim to that path.")
    text = decl_file.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise GazetteerError(f"{decl_file} is empty")
    cache = load_cache(path)
    existing = (cache.get("licences") or {}).get(gazetteer)
    if not existing or not licence_is_recorded(existing):
        raise GazetteerError(
            f"record the {gazetteer} licence itself before its declaration"
        )
    existing["declared_by"] = {
        "publisher": GAZETTEERS[gazetteer]["publisher"],
        "text": text,
        "source_url": source_url,
        "recorded": _today(),
    }
    write_cache(cache, path)
    print(f"{gazetteer} declaration recorded verbatim from {source_url} ({len(text)} chars)")
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
    unrenderable: list[str] = []
    date_holes: list[str] = []
    date_unknown: list[str] = []
    period_ranges = period_ranges_from_cache(cache)

    for p in locatable:
        entry = known.get(p.cache_key or "")
        if entry is None:
            failures.append(f"{p.key}: '{p.cache_key}' is not cached")
            continue

        # A6, the date-overlap check. An id can resolve perfectly, carry a real
        # coordinate, and denote a place attested only centuries away from
        # anything this corpus is about — see `date_audit`.
        verdict, detail = date_audit(entry, period_ranges)
        if verdict == DATE_OUTSIDE:
            failures.append(f"{p.key}: '{p.cache_key}' ({entry.title}) {detail}")
            continue
        if verdict == DATE_HOLE:
            date_holes.append(f"{p.key}: '{p.cache_key}' ({entry.title}) {detail}")
        elif verdict == DATE_UNKNOWN:
            date_unknown.append(f"{p.key}: '{p.cache_key}' ({entry.title}) {detail}")
        if looks_deprecated(entry.title):
            # A resolving id pointing at a record the publisher has marked as
            # wrong. It has a plausible coordinate — 427224440 sits at Hegra's
            # own point — so nothing downstream would ever query it.
            failures.append(
                f"{p.key}: '{p.cache_key}' is titled {entry.title!r}, which the "
                f"gazetteer marks as deprecated. It resolves, and it is still "
                f"not the place to cite. Find the record it duplicates."
            )
            continue
        if p.unlocated:
            # The placement CLAIMS the gazetteer cannot locate this place.
            # Verified, not trusted — the whole value of moving this out of a
            # free-text note is that it can now be checked against the entry.
            if entry.has_point or entry.has_extent:
                failures.append(
                    f"{p.key}: '{p.cache_key}' ({entry.title}) is marked "
                    f"'{UNLOCATED_KEY}', but the cached entry DOES carry a "
                    f"location. Either the gazetteer has placed it since the "
                    f"note was written — in which case drop the key and let it "
                    f"draw — or the key is on the wrong placement."
                )
            continue
        if not entry.has_point and not entry.has_extent:
            failures.append(
                f"{p.key}: '{p.cache_key}' ({entry.title}) resolves to no "
                f"point and no extent — nothing to draw, and nothing may be "
                f"invented to replace it. If the gazetteer genuinely holds "
                f"this place without a location, say so with "
                f"'{UNLOCATED_KEY}': true rather than dropping the id."
            )
        elif p.ground == "regional" and not entry.has_area:
            # PLACES.md: a regional placement renders as an EXTENT and never as
            # a pin. So a regional id whose bbox is degenerate draws nothing at
            # all — while resolving, caching, and passing every other check in
            # this function. The placement is not wrong; it is invisible, which
            # is the worse of the two because nothing reports it.
            #
            # Found 2026-08-13 on `pleiades:766 Aegyptus`, whose representative
            # point is Alexandria's own coordinate and whose bbox has zero area.
            # Egypt is the `source` in three of the seven literary records — the
            # single most connected node in the corpus — and it would have
            # rendered as blank space on the first map that drew it.
            #
            # A report and not a failure: the entry is honest, the id is right,
            # and what to do about it is a decision for A5 (draw the extent of
            # something else, accept the gap, or drop the id and say so in a
            # note). A failure here would demand a fix before the decision.
            unrenderable.append(
                f"{p.key}: '{p.cache_key}' ({entry.title}) is regional and its "
                f"bbox has no area, so it resolves to a representative point "
                f"and nothing an extent-only renderer can draw"
            )

    # A licence per gazetteer the corpus actually cites — not one licence for
    # the cache. Pleiades is CC BY 3.0 US and GeoNames is CC BY 4.0; a single
    # block would have asserted one publisher's terms over the other's points.
    # Driven by what is cited, so adding a gazetteer to the vocabulary obliges
    # nothing until a placement uses it, and obliges this the moment one does.
    for gaz in sorted(gazetteers_in_use(by_doc)):
        licence = licence_for(cache, gaz)
        publisher = GAZETTEERS.get(gaz, {}).get("publisher", gaz)
        if not licence_is_recorded(licence):
            failures.append(
                f"the {gaz} licence is unconfirmed. Read the licence and "
                f"attribution statement published by {publisher}, save it to a "
                f"file, and run `--record-licence <file> --licence-for {gaz} "
                f"--licence-source-url <url>`. It is recorded verbatim or not "
                f"at all — the same rule that forbids writing a place id from "
                f"memory."
            )
        elif not (licence.get("declared_by") or {}).get("text"):
            # Knowing what CC BY says is not knowing that this publisher chose
            # it. A cache holding only the first asserts a licence on the
            # strength of somebody's recollection that it applies.
            failures.append(
                f"the {gaz} licence text is recorded but {publisher}'s own "
                f"declaration that it governs their content is not. Save that "
                f"statement and run `--record-declaration <file> --licence-for "
                f"{gaz} --declaration-source-url <url>`."
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

    unlocated = [p for p in locatable if p.unlocated]
    print(f"placements: {len(places)}   locatable: {len(locatable)}   cached ids: {len(known)}")
    if unlocated:
        # Counted separately from the gaps, which is the entire point of the
        # key: these cite a real entry in a real gazetteer that records no
        # location, and they are not the same thing as a place no gazetteer
        # has heard of.
        print(
            f"gazetteer holds the place but not its location: {len(unlocated)} "
            f"({', '.join(sorted(p.name for p in unlocated))})"
        )
    print(f"documents with a placement: {sum(1 for v in by_doc.values() if v)} of {len(by_doc)}")

    # A note rather than a failure. CC BY asks for appropriate credit and
    # Pleiades credits per place, so an entry with neither authors nor creators
    # is a point the UI cannot attribute — but whether that is a defect in the
    # dump or a genuinely uncredited place is not something this check can tell,
    # and a guard that cannot tell those apart would name the wrong cause.
    # Pleiades only. GeoNames' CC BY 4.0 credits the project, not per-record
    # contributors, so a GeoNames entry with no author is not missing anything
    # — and listing 5 of them here every run would train the reader to ignore
    # the line that exists to catch a real Pleiades gap.
    unattributed = sorted(
        pid for pid, e in known.items()
        if e.gazetteer == "pleiades" and not e.authors and not e.creators
    )
    if unattributed:
        print(
            f"note: {len(unattributed)} cached Pleiades entries carry no authors "
            f"or creators, so they cannot be attributed per place: {unattributed[:5]}"
        )
    if stale:
        print(f"note: entries from earlier dump dates are present: {stale}")
    if unrenderable:
        print(
            f"\nnote: {len(unrenderable)} regional placement(s) resolve but "
            f"cannot be drawn as an extent. Not a failure — see A5."
        )
        for u in unrenderable:
            print(f"  ~ {u}")

    # A note and not a failure: the placement may be exactly right and the
    # gazetteer merely attests the place narrowly. What it costs is that the
    # entry's date range cannot be used as corroboration, which is worth
    # knowing and is not worth blocking a build over. See `date_audit`.
    if date_holes:
        print(
            f"\nnote: {len(date_holes)} placement(s) resolve to an entry whose "
            f"attested periods all fall outside {PROJECT_MIN_YEAR}.."
            f"{PROJECT_MAX_YEAR}, though its overall range spans it:"
        )
        for d in date_holes:
            print(f"  ~ {d}")
    if date_unknown:
        print(
            f"\nnote: {len(date_unknown)} placement(s) could not be date-checked:"
        )
        for d in date_unknown[:5]:
            print(f"  ? {d}")
        if not period_ranges:
            print(
                "  Run `python -m ingest.gazetteer --refresh-periods --dump "
                "<dump>` to derive the period vocabulary."
            )

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
        files = src.get("files")
        if files:
            # One line per country file, because "the GeoNames source" is not
            # one file and printing it as one would name the wrong provenance.
            print(f"  source:   {name} — {len(files)} country file(s)")
            for fname, meta in sorted(files.items()):
                print(f"            {fname:<10} snapshot {meta.get('dump_date')} "
                      f"(retrieved {meta.get('retrieved')})")
        else:
            print(f"  source:   {name} — {src.get('dump_url')}")
            print(f"            snapshot {src.get('dump_date')} (retrieved {src.get('retrieved')})")
    if not cache.get("sources"):
        print("  source:   none yet")
    in_use = gazetteers_in_use(by_doc)
    for gaz in sorted(set(cache.get("licences") or {}) | in_use):
        licence = licence_for(cache, gaz)
        declared = bool((licence.get("declared_by") or {}).get("text"))
        print(f"  licence:  {gaz} — "
              f"{'recorded' if licence_is_recorded(licence) else 'UNCONFIRMED'}"
              f", declaration {'recorded' if declared else 'NOT RECORDED'}"
              f"{'' if gaz in in_use else '  (not cited by any placement)'}")
        print(f"            {licence.get('source_url')}")
    if not in_use and not cache.get("licences"):
        print("  licence:  none recorded")
    by_gaz: dict[str, int] = {}
    for e in known.values():
        by_gaz[e.gazetteer] = by_gaz.get(e.gazetteer, 0) + 1
    print(f"  entries:  {len(known)} {dict(sorted(by_gaz.items()))} "
          f"(with point: {sum(1 for e in known.values() if e.has_point)},"
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
    ap.add_argument("--refresh-periods", action="store_true",
                    help="derive each Pleiades period's date range from --dump "
                         "and cache it, so --check can tell an entry that "
                         "attests this project's era from one whose range "
                         "merely spans it")
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
    # GeoNames. A separate dump flag rather than a mode switch on --dump,
    # because passing a GeoNames zip to the Pleiades CSV reader should be an
    # error the argument parser catches, not a parse failure 6 MB in.
    ap.add_argument("--geonames-dump", type=Path, metavar="FILE",
                    help="a GeoNames country dump (e.g. KR.zip) from "
                         "https://download.geonames.org/export/dump/")
    ap.add_argument("--geonames-find", metavar="TEXT",
                    help="search --geonames-dump by name, ascii name, alternate "
                         "name or id; never caches")
    ap.add_argument("--refresh-geonames", action="store_true",
                    help="extract the corpus's GeoNames ids from --geonames-dump")
    ap.add_argument("--geonames-date", default=None, metavar="YYYY-MM-DD",
                    help="snapshot date, required only when --geonames-dump is "
                         "an unzipped .txt whose publisher timestamp is lost")
    ap.add_argument("--record-licence", type=Path, metavar="FILE",
                    help="file holding the licence terms, verbatim")
    ap.add_argument("--licence-source-url", default=None)
    ap.add_argument("--record-declaration", type=Path, metavar="FILE",
                    help="file holding the publisher's statement that this "
                         "licence governs their content, verbatim")
    ap.add_argument("--declaration-source-url", default=None)
    # NOT --gazetteer: that is already the path to the cache file. Two meanings
    # on one flag is the defect this repository keeps paying for.
    ap.add_argument("--licence-for", default="pleiades", choices=sorted(GAZETTEERS),
                    help="which gazetteer a recorded licence or declaration "
                         "belongs to (default: pleiades)")
    args = ap.parse_args(argv)

    try:
        if args.probe:
            return cmd_probe(args.probe)
        if args.inspect:
            if not args.dump:
                ap.error("--inspect needs --dump")
            return cmd_inspect(args.dump)
        if args.geonames_find:
            if not args.geonames_dump:
                ap.error("--geonames-find needs --geonames-dump")
            return cmd_geonames_find(args.geonames_dump, args.geonames_find)
        if args.refresh_geonames:
            if not args.geonames_dump:
                ap.error(
                    "--refresh-geonames needs --geonames-dump. Download the "
                    "country file from https://download.geonames.org/export/dump/"
                )
            return cmd_refresh_geonames(
                args.geonames_dump, args.corpus, args.gazetteer, args.geonames_date
            )
        if args.find:
            if not args.dump:
                ap.error("--find needs --dump")
            return cmd_find(args.dump, args.find, args.names_dump)
        if args.survey:
            if not args.dump:
                ap.error("--survey needs --dump")
            return cmd_survey(args.survey, args.dump, args.names_dump)
        if args.refresh_periods:
            if not args.dump:
                ap.error(
                    "--refresh-periods needs --dump. Download a DATED dump "
                    "from " + DUMP_BASE
                )
            return cmd_refresh_periods(args.dump, args.gazetteer)
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
                args.licence_for, args.record_licence,
                args.licence_source_url, args.gazetteer,
            )
        if args.record_declaration:
            if not args.declaration_source_url:
                ap.error("--record-declaration needs --declaration-source-url")
            return cmd_record_declaration(
                args.licence_for, args.record_declaration,
                args.declaration_source_url, args.gazetteer,
            )
        if args.stats:
            return cmd_stats(args.gazetteer, args.corpus)
        return cmd_check(args.corpus, args.gazetteer)
    except GazetteerError as exc:
        print(f"gazetteer error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
