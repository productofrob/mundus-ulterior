"""Generate the dated coastline snapshot the Places map draws as its backdrop.

    python scripts/build_coastline.py                     # from geopandas' bundled Natural Earth
    python scripts/build_coastline.py --source ne.geojson # from a downloaded Natural Earth file

Why this file exists at all
---------------------------
`ui/index.html`'s Places map originally drew no coastline. The argument recorded
in the code was that "a traced coastline would be the one shape on the page that
came from nowhere citable" — and that argument was **wrong**, in a specific and
instructive way. It conflated two different rules:

* *Coordinates are never authored* governs **placements** — a claim about where a
  record's place is. That rule is absolute and `ingest/places.py` enforces it.
* A coastline is not a claim about the corpus. It is the reference frame the
  claims are read against, and it can carry provenance exactly like any other
  source in this repository.

The cost of the mistake was that the map was unreadable: points spanning 10-84°E
and 9-56°N with no way to tell the Red Sea from the Bay of Bengal. The ORBIS
parallel that `PHASE2.md` rates "High" is mostly the reader recognising the
Indian Ocean, and dots on a graticule do not deliver it.

So the coastline is sourced under the same discipline as everything else here:
a **dated snapshot**, with its origin, retrieval date and terms recorded inside
the file it produces. Same shape as `data/gazetteer.json`'s `sources` block, and
for the same reason — *a result is comparable only within the thing that produced
it, and that thing must be recorded*.

Why Natural Earth
-----------------
Public domain, explicitly and unusually clearly: "no permission is needed to use
Natural Earth. Crediting the authors is unnecessary." That removes the licence
question a basemap would otherwise raise, which matters on a page that already
has to carry Pleiades' CC-BY attribution per place.

The 1:110m scale is deliberate. This map spans a third of the globe in a
viewBox 900 pixels wide; 1:10m detail would be tens of thousands of coordinates
rendering as the same handful of pixels, and `ui/data.js` is already ~1 MB.

Why the coastline is derived from country polygons
---------------------------------------------------
`unary_union` over the country polygons dissolves every internal land border,
so the boundary of the union is coast — not a political map. Drawing borders
would put a 21st-century nation-state outline under a map of the first-century
Indian Ocean, which is a claim this project should not make by accident.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

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

REPO = Path(__file__).resolve().parent.parent

# Generous on purpose: wide enough for every region the corpus covers, including
# the five records still in the GeoNames backlog (Óc Eo ~105°E, Khao Sam Kaeo
# ~99°E, Gyeongju ~129°E) which will need coastline the day they are placed.
# Clipping tightly to today's cached points would silently need regenerating the
# first time a placement moved outside it.
CLIP = {"min_lon": -25.0, "min_lat": -40.0, "max_lon": 150.0, "max_lat": 75.0}

# ~0.05° is about 5 km at the equator. At this map's scale (roughly 175° of
# longitude across 900 px, so ~0.19°/px) that is well under one pixel, so the
# simplification is invisible and the coordinate count drops by roughly half.
SIMPLIFY_TOLERANCE = 0.05

# 3 decimal places is ~110 m. Far finer than one pixel here, and it removes the
# float noise that would otherwise make every coordinate 17 characters long.
PRECISION = 3

SOURCE_NOTE = (
    "Natural Earth 1:110m Admin 0 Countries, dissolved to a single land "
    "geometry whose boundary is the coastline. Natural Earth is in the public "
    "domain: 'no permission is needed to use Natural Earth. Crediting the "
    "authors is unnecessary.' (naturalearthdata.com/about/terms-of-use)"
)


def load_land(source: Path | None):
    try:
        import geopandas  # noqa: PLC0415
        from shapely.ops import unary_union  # noqa: PLC0415
    except ImportError as exc:
        print(
            f"error: {exc}. This is a one-off generator, not part of the build "
            f"or test path — install its dependencies only when regenerating "
            f"the snapshot:\n    pip install 'geopandas<1.0'",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc

    import warnings
    warnings.filterwarnings("ignore")

    if source is not None:
        if not source.exists():
            raise SystemExit(f"error: no Natural Earth source at '{source}'")
        frame = geopandas.read_file(source)
        origin = str(source.name)
    else:
        # geopandas <1.0 ships the 1:110m countries file. Recorded by path so
        # the snapshot says which copy of Natural Earth it actually came from.
        path = geopandas.datasets.get_path("naturalearth_lowres")
        frame = geopandas.read_file(path)
        origin = f"geopandas {geopandas.__version__} bundled naturalearth_lowres"

    return unary_union(list(frame.geometry)), origin


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", type=Path, default=None,
                    help="a Natural Earth countries file; omit to use geopandas' bundled copy")
    ap.add_argument("--out-dir", type=Path, default=REPO / "data")
    args = ap.parse_args(argv)

    from shapely.geometry import box  # noqa: PLC0415

    land, origin = load_land(args.source)

    clipped = land.intersection(
        box(CLIP["min_lon"], CLIP["min_lat"], CLIP["max_lon"], CLIP["max_lat"])
    )
    simplified = clipped.simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)

    # POLYGONS, each as [exterior, hole, hole, ...] — not a flat list of
    # boundary rings.
    #
    # The first version of this emitted `.boundary`, which is every ring with
    # no record of which is an outer coast and which is an inland sea. Drawn as
    # one filled SVG path, the winding rule then guessed: the Mediterranean and
    # the Black Sea came out as water (they are holes, and happened to wind the
    # right way) while the Indian Ocean and the Atlantic came out as LAND,
    # because open ocean is not a ring at all — it is simply outside every ring,
    # and a fill cannot represent "outside" without knowing which side is which.
    #
    # Caught by rendering the map to an image and looking at it. Every automated
    # check passed on the broken version: `check_ui.mjs` asserts that each cached
    # point and edge appears in the SVG, and all of them did — on top of an
    # inside-out world. *An assertion about presence says nothing about
    # correctness*, which this repository has now paid for in a new medium.
    polygons: list[list[list[list[float]]]] = []
    geoms = getattr(simplified, "geoms", [simplified])

    def ring(coords) -> list[list[float]]:
        return [[round(x, PRECISION), round(y, PRECISION)] for x, y in coords]

    for geom in geoms:
        if geom.geom_type != "Polygon":
            continue
        exterior = ring(geom.exterior.coords)
        # A 2-point stub is a rounding artefact at this tolerance, not a coast.
        if len(exterior) <= 2:
            continue
        rings = [exterior]
        for interior in geom.interiors:
            hole = ring(interior.coords)
            if len(hole) > 2:
                rings.append(hole)
        polygons.append(rings)

    today = datetime.now(timezone.utc).date().isoformat()
    payload = {
        "source": "Natural Earth",
        "source_url": "https://www.naturalearthdata.com/downloads/110m-cultural-vectors/",
        "source_detail": origin,
        "scale": "1:110m",
        "terms": "public domain",
        "note": SOURCE_NOTE,
        "retrieved": today,
        "clip": CLIP,
        "simplify_tolerance": SIMPLIFY_TOLERANCE,
        "precision": PRECISION,
        "polygon_count": len(polygons),
        "ring_count": sum(len(rings) for rings in polygons),
        "point_count": sum(len(r) for rings in polygons for r in rings),
        # [[exterior, hole, ...], ...] — see the comment above `polygons`.
        "polygons": polygons,
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / f"coastline-ne110m-{today.replace('-', '')}.json"
    out.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    size = out.stat().st_size / 1024
    print(
        f"wrote {out.relative_to(REPO)} ({size:.0f} KB): "
        f"{payload['polygon_count']} polygon(s), {payload['ring_count']} ring(s), "
        f"{payload['point_count']} points, clipped to "
        f"{CLIP['min_lon']}..{CLIP['max_lon']}°E / {CLIP['min_lat']}..{CLIP['max_lat']}°N"
    )
    print(f"source: {origin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
