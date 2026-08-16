"""Place-block and gazetteer tests. No network, no database, no corpus edits.

Run: python -m ingest.test_places

Every import in this file sits at module scope, deliberately. `ingest/test_embed.py`
carried one import two-thirds of the way down `main()`, the name it referenced
went away in Part 6, and the resulting `ImportError` did not announce a broken
dependency — it **truncated the test run**, silently disabling five assertions
for two days. A missing dependency must fail at load, loudly.

The guards below each exist for a specific defect the W1 design anticipates.
`scripts/mutate_places.py` breaks each one in turn and confirms it fires; a guard
that has never been seen to fail is not known to work.
"""

from __future__ import annotations

import contextlib
import csv
import gzip
import io
import json
import tempfile
import zipfile
from pathlib import Path

from .gazetteer import (
    DATE_HOLE,
    DATE_NO_DATES,
    DATE_OK,
    DATE_OUTSIDE,
    DATE_UNKNOWN,
    Entry,
    GazetteerError,
    LICENCE_UNCONFIRMED,
    cmd_check,
    cmd_find,
    cmd_record_declaration,
    cmd_refresh_geonames,
    cmd_refresh_periods,
    cmd_survey,
    cmd_record_licence,
    date_audit,
    derive_period_ranges,
    dump_date_from_name,
    empty_cache,
    entries,
    entry_hull,
    in_project_window,
    period_ranges_from_cache,
    ranges_overlap,
    geonames_dump_date,
    licence_for,
    licence_is_recorded,
    load_cache,
    looks_deprecated,
    map_columns,
    read_dump,
    read_geonames_dump,
    verify_geonames_shape,
    require_file,
    resolve,
    write_cache,
)
from .places import (
    DIRECTIONAL_ROLES,
    GROUNDS,
    ROLES,
    Place,
    PlaceError,
    NO_PLACES_KEY,
    PLACE_BLOCKS,
    assert_no_authored_coordinates,
    canonical_uri,
    read_no_places_reason,
    parse_place,
    parse_record_places,
)

failures: list[str] = []


def expect(condition: bool, label: str) -> None:
    if condition:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


def expect_raises(fn, label: str, contains: str | None = None) -> None:
    try:
        fn()
    except (PlaceError, GazetteerError) as exc:
        if contains and contains.lower() not in str(exc).lower():
            # The label goes on the FAIL line alone and the reason on the next,
            # so scripts/mutate_places.py can read which guard fired. The
            # existing mutation harnesses parse `FAIL <label>` and a trailing
            # explanation on the same line would rename the guard.
            print(f"  FAIL {label}")
            print(f"       raised, but the message lacks {contains!r}: {exc}")
            failures.append(label)
        else:
            print(f"  ok   {label}")
        return
    print(f"  FAIL {label}")
    print("       no error raised")
    failures.append(label)


def place(**over):
    # 39271 is the real Adulis — title "Adouli", 15.262/39.659, "port on the
    # west coast of the Red Sea near modern Zula in Eritrea", confirmed against
    # the 2026-08-10 snapshot on 2026-08-12.
    #
    # This fixture previously carried 39274195, copied from the worked example
    # in PHASE2_PLAN.md — which is wrong, and wrong in the section that forbids
    # writing an id from memory. It was harmless here, being synthetic, and it
    # is corrected anyway: a fixture that is merely well-formed teaches the
    # shape, and one that is also true teaches the shape and the value.
    base = {
        "name": "Adulis",
        "ground": "stated",
        "gazetteer": "pleiades",
        "gazetteer_id": "39271",
        "uri": canonical_uri("pleiades", "39271"),
    }
    base.update(over)
    return {k: v for k, v in base.items() if v is not _OMIT}


class _Omit:
    pass


_OMIT = _Omit()


def parse(raw, doc="africa-03-periplus-adulis", block="findspot_places", i=0):
    """Parse one entry. Defaults to a block that takes no `role`.

    The default was `subject_places` until A4 made `role` mandatory there. The
    assertions below are about grounds, ids and uris, and none of them is about
    roles — so they run against the block where a role is not a parameter of the
    question. `test_roles` covers subject_places on its own.
    """
    return parse_place(raw, doc, block, i)


def subject(**over):
    """A well-formed subject_places entry: the fixture above, plus a role."""
    over.setdefault("role", "focus")
    return place(**over)


def parse_subject(raw, doc="africa-03-periplus-adulis", i=0):
    return parse_place(raw, doc, "subject_places", i)


# --------------------------------------------------------------------------
# The happy paths, so the strictness below is known to be strictness and not
# a module that rejects everything.
# --------------------------------------------------------------------------

def test_valid_shapes() -> None:
    print("\nvalid shapes")

    p = parse(place())
    expect(isinstance(p, Place) and p.ground == "stated", "a stated placement parses")
    expect(p.locatable, "a placement with an id is locatable")
    expect(p.contested is False and p.contested_citations == (),
           "contested defaults to absent, not to a written false")

    p = parse(place(ground="identified", ground_citation="Casson 1989, 102."))
    expect(p.ground_citation == "Casson 1989, 102.", "identified + citation parses")

    p = parse(
        place(
            ground="identified",
            ground_citation="Cherian et al. 2009.",
            contested=True,
            contested_citations=[
                "Cherian et al. 2009 — Pattanam finds argue the Muziris site.",
                "Gurukkal 2016 — the identification is not established.",
            ],
        )
    )
    expect(p.contested and len(p.contested_citations) == 2,
           "a contested identification carries both sides")

    p = parse(place(gazetteer=_OMIT, gazetteer_id=_OMIT, uri=_OMIT, ground="regional",
                    note="Region only; no Pleiades feature covers it."))
    expect(not p.locatable and p.note, "regional without an id parses, carrying its note")

    p = parse(place(ground="regional"))
    expect(p.locatable, "regional WITH an id parses and stays locatable")

    expect(GROUNDS == {"stated", "identified", "regional"},
           "the ground vocabulary is exactly the three the UI can render")

    expect(parse_record_places({"id": "x"}) == [],
           "a record with no place blocks is not an error")


# --------------------------------------------------------------------------
# Guards
# --------------------------------------------------------------------------

def test_guards() -> None:
    print("\nguards — each is mutation-verified by scripts/mutate_places.py")

    # G1: an unknown key must not be ignored. This is the goldset.py defect
    #     family: a misspelled key drops a requirement without failing anything.
    expect_raises(
        lambda: parse(place(ground="identified", ground_cite="Casson 1989.")),
        "unknown key is a load-time error",
        contains="unknown key",
    )

    # G2: the single most important rule in W1 — a specific place needs an id,
    #     because otherwise its coordinate would be authored.
    expect_raises(
        lambda: parse(place(gazetteer=_OMIT, gazetteer_id=_OMIT, uri=_OMIT)),
        "stated placement without a gazetteer id is refused",
        contains="gazetteer",
    )
    expect_raises(
        lambda: parse(place(gazetteer=_OMIT, gazetteer_id=_OMIT, uri=_OMIT, ground="identified",
                            ground_citation="Casson 1989.")),
        "identified placement without a gazetteer id is refused",
        contains="gazetteer",
    )

    # G2b: the gazetteer names the source of the id. Half the corpus's findspots
    #      have no Pleiades entry, so a placement has to say WHICH gazetteer —
    #      and adding one is a sourcing and licensing decision, not a spelling.
    expect_raises(
        lambda: parse(place(gazetteer="wikidata")),
        "an unlisted gazetteer is refused",
        contains="not one of",
    )
    expect_raises(
        lambda: parse(place(gazetteer_id=_OMIT, uri=_OMIT)),
        "a gazetteer with no id is refused",
        contains="together or not at all",
    )
    expect_raises(
        lambda: parse(place(gazetteer=_OMIT, uri=_OMIT)),
        "an id with no gazetteer is refused",
        contains="together or not at all",
    )
    p_geo = parse(place(gazetteer="geonames", gazetteer_id="1835235",
                        uri="https://www.geonames.org/1835235"))
    expect(p_geo.cache_key == "geonames:1835235",
           "a geonames placement keys separately from a pleiades one")
    expect(parse(place()).cache_key == "pleiades:39271",
           "cache keys are namespaced, so id 98983 in two gazetteers cannot collide")

    # G3: `identified` IS the claim that a scholar made an identification.
    expect_raises(
        lambda: parse(place(ground="identified")),
        "identified without a ground_citation is refused",
        contains="ground_citation",
    )

    # G4: two fields, one fact. If a uri and an id can disagree they eventually
    #     will, and the reader cannot tell which one the map used.
    expect_raises(
        lambda: parse(place(uri="https://pleiades.stoa.org/places/999999")),
        "uri that disagrees with the gazetteer id is refused",
        contains="does not match",
    )
    expect_raises(
        lambda: parse(place(uri=_OMIT)),
        "a gazetteer id without its uri is refused",
    )
    expect_raises(
        lambda: parse(place(gazetteer_id="https://pleiades.stoa.org/places/39271")),
        "a URL written into gazetteer_id is refused",
        contains="bare numeric",
    )

    # G5: empty is not a value. One empty string has already cost this project
    #     a third state it now has to live with.
    expect_raises(
        lambda: parse(place(note="")),
        "an empty string is refused rather than stored",
        contains="empty",
    )
    expect_raises(
        lambda: parse_record_places({"id": "x", "subject_places": []}),
        "an empty place block is refused",
        contains="empty",
    )

    # G6: contested may only be written as true, must sit on `identified`, and
    #     must carry both sides.
    expect_raises(
        lambda: parse(place(contested=False)),
        "contested written as false is refused",
        contains="only be written as true",
    )
    expect_raises(
        lambda: parse(place(ground="identified", ground_citation="Cherian 2009.",
                            contested=True, contested_citations=["one side only"])),
        "a contested identification with one citation is refused",
        contains="at least two",
    )
    expect_raises(
        lambda: parse(place(contested=True, contested_citations=["a", "b"])),
        "contested on ground 'stated' is refused",
        contains="only meaningful",
    )
    expect_raises(
        lambda: parse(place(contested_citations=["a", "b"])),
        "contested_citations without contested is refused",
    )

    # G7: the sparse case must say why it is sparse.
    expect_raises(
        lambda: parse(place(gazetteer=_OMIT, gazetteer_id=_OMIT, uri=_OMIT, ground="regional")),
        "regional with no id and no note is refused",
        contains="note",
    )

    # G8: vocabulary is closed.
    expect_raises(
        lambda: parse(place(ground="probable")),
        "an invented ground is refused",
        contains="not one of",
    )

    # G9: no coordinate is ever authored into a seed record. This is G1
    #     criterion 2 at its cheapest point of failure.
    expect_raises(
        lambda: assert_no_authored_coordinates(
            {"id": "x", "lat": 15.26, "lon": 39.66}
        ),
        "a hand-written coordinate in a seed record is refused",
        contains="never authored",
    )
    expect(
        assert_no_authored_coordinates(
            {"id": "x", "translation_source": "Schoff 1912.", "language_note": "…"}
        ) is None,
        "the coordinate rule matches exact keys, not the 'lat' inside "
        "'translation_source'",
    )

    # G9b: a record declares places OR a reason it has none, never both. Without
    #      this, an absent block means "not curated yet" AND "curated, nothing to
    #      place", and at A6 nobody can tell them apart — the third state this
    #      schema refuses everywhere else, one level up.
    expect(read_no_places_reason({"id": "x"}) is None,
           "a record with no places and no reason returns None, not an error")
    expect(read_no_places_reason({"id": "x", NO_PLACES_KEY: "findspot not recorded"})
           == "findspot not recorded",
           "a declared reason is read back")
    expect_raises(
        lambda: read_no_places_reason(
            {"id": "x", NO_PLACES_KEY: "none", "findspot_places": [place()]}),
        "a record cannot both declare places and declare it has none",
        contains="either has places",
    )
    expect_raises(
        lambda: read_no_places_reason({"id": "x", NO_PLACES_KEY: "  "}),
        "an empty no_places_reason is refused",
        contains="non-empty",
    )
    expect("origin_places" in PLACE_BLOCKS,
           "origin_places is a block: a mint is not a findspot, and origin to "
           "findspot is an object moving")
    expect(parse_record_places({"id": "x", "origin_places": [place()]})[0].block
           == "origin_places",
           "a placement records which block it came from")

    # G10: one place, one entry.
    expect_raises(
        lambda: parse_record_places(
            {"id": "x", "findspot_places": [place(), place(name="Adulis again")]}
        ),
        "a gazetteer id repeated inside one block is refused",
        contains="repeated",
    )


# --------------------------------------------------------------------------
# Roles — A4, and the shape A5's edges are derived from
#
# Decided 2026-08-13 with the seven literary records in hand and before any
# subject_places block was written, which is the whole reason A1 left it open.
# The rules below are what makes `source -> focus -> destination` a derivation
# rather than a convention someone has to remember.
# --------------------------------------------------------------------------

def test_roles() -> None:
    print("\nroles")

    expect(ROLES == {"focus", "source", "destination", "waypoint", "mentioned"},
           "the role vocabulary is exactly the five A5 can draw")
    expect(DIRECTIONAL_ROLES < ROLES and "mentioned" not in DIRECTIONAL_ROLES
           and "focus" not in DIRECTIONAL_ROLES,
           "the directional roles are the proper subset that draws an edge")

    p = parse_subject(subject(role="source"))
    expect(p.role == "source" and p.draws_edge, "a source draws an edge")
    expect(not parse_subject(subject(role="mentioned")).draws_edge,
           "a mentioned place draws no edge — naming Laodicean wine is not a "
           "route to Laodicea")
    expect(not parse_subject(subject(role="focus")).draws_edge,
           "the focus is an edge's endpoint, not an edge")

    # R1: no default. `mentioned` is a claim about the passage, and the standing
    #     rule since expect_untranslatable is that a claim never arrives by
    #     omission. This is the guard that makes the other four mean anything.
    expect_raises(
        lambda: parse_subject(place()),
        "a subject place with no role is refused",
        contains="no default",
    )
    expect_raises(
        lambda: parse_subject(subject(role="origin")),
        "a role outside the closed vocabulary is refused",
        contains="not one of",
    )

    # R2: the other two blocks name their relation already. A role there would
    #     be a second name for one fact — free to disagree with the first.
    expect_raises(
        lambda: parse(place(role="focus"), block="findspot_places"),
        "a role on findspot_places is refused",
        contains="subject_places only",
    )
    expect_raises(
        lambda: parse(place(role="source"), block="origin_places"),
        "a role on origin_places is refused",
        contains="subject_places only",
    )
    expect(parse(place()).role is None,
           "a findspot placement carries no role at all, rather than a blank one")

    # R3: at most one focus, or `source -> focus` does not say which focus.
    expect_raises(
        lambda: parse_record_places({"id": "x", "subject_places": [
            subject(name="Adulis"),
            subject(name="Aksum", gazetteer_id="39303",
                    uri=canonical_uri("pleiades", "39303")),
        ]}),
        "two foci in one block are refused",
        contains="ambiguous",
    )

    # R4: a directional role with nothing to be directional about. This is the
    #     rule that will fire on a half-edited record, which is exactly when it
    #     is worth having.
    expect_raises(
        lambda: parse_record_places({"id": "x", "subject_places": [
            subject(name="Egypt", role="source"),
            subject(name="Aksum", role="destination", gazetteer_id="39303",
                    uri=canonical_uri("pleiades", "39303")),
        ]}),
        "directional roles with no focus are refused",
        contains="no place carries 'focus'",
    )

    # ...and the honest version of the same block: a passage that names places
    # and describes nothing moving needs no focus, and must not be forced to
    # invent one.
    ok = parse_record_places({"id": "x", "subject_places": [
        subject(name="Egypt", role="mentioned"),
        subject(name="Aksum", role="mentioned", gazetteer_id="39303",
                uri=canonical_uri("pleiades", "39303")),
    ]})
    expect(len(ok) == 2 and not any(p.draws_edge for p in ok),
           "an all-mentioned block needs no focus and draws nothing")

    # R5: roles do not loosen the placement rules. A `mentioned` place is still
    #     a place, and still may not carry an authored point.
    expect_raises(
        lambda: parse_subject(subject(role="mentioned", gazetteer=_OMIT,
                                      gazetteer_id=_OMIT, uri=_OMIT)),
        "a mentioned place still needs an id or the regional ground",
        contains="gazetteer",
    )
    p = parse_subject(subject(role="waypoint", ground="regional", gazetteer=_OMIT,
                              gazetteer_id=_OMIT, uri=_OMIT,
                              note="Named as a stage of the voyage; no feature "
                                   "in either gazetteer covers it."))
    expect(p.draws_edge and not p.locatable,
           "a regional waypoint draws an edge it has no coordinate for — which "
           "A5 must render as a relation, not a line to a guessed point")


# --------------------------------------------------------------------------
# Gazetteer
# --------------------------------------------------------------------------

# The header of pleiades-places-20260810.csv.gz, as observed with --inspect on
# 2026-08-12 — not a header written from the dumps README, which is dated
# 2022-11-07 and documents six columns of the twenty-six that are actually
# there, none of them a coordinate. An earlier version of this list was
# guesswork and had `geometry` where the file has `geoContext`.
REAL_DUMP_HEADER = [
    "authors", "bbox", "connectsWith", "created", "creators", "currentVersion",
    "description", "extent", "featureTypes", "geoContext", "hasConnectionsWith",
    "id", "locationPrecision", "maxDate", "minDate", "modified", "path",
    "reprLat", "reprLatLong", "reprLong", "tags", "timePeriods",
    "timePeriodsKeys", "timePeriodsRange", "title", "uid",
]


def test_gazetteer() -> None:
    print("\ngazetteer")

    cmap = map_columns(REAL_DUMP_HEADER)
    expect(cmap["id"] == "id" and cmap["title"] == "title",
           "columns are discovered from the header, not assumed")
    expect(cmap.get("lat") == "reprLat" and cmap.get("lon") == "reprLong",
           "a representative point is found when the header offers one")

    # The dumps README (2022) documents no coordinate columns at all. A parser
    # written from documentation rather than data must fail loudly and print
    # what it saw, not silently cache points it never found.
    expect_raises(
        lambda: map_columns(["id", "title", "description", "path", "timePeriods"]),
        "a header with no geometry fails loudly",
        contains="no geometry",
    )
    expect_raises(
        lambda: map_columns(["pid", "label", "reprLat", "reprLong"]),
        "a header missing the id column fails loudly, printing the header",
        contains="observed header",
    )

    # A missing file is the likeliest failure in this module — every command
    # takes a path to something just saved or downloaded elsewhere. It must
    # never reach the user as a pathlib traceback. Written as one helper and
    # asserted at every call site, because the first version of this fix was
    # applied to --record-licence alone and --inspect produced the identical
    # traceback the same evening.
    for label, call in (
        ("dump", lambda: read_dump(Path("no-such-dump-20260812.csv.gz"), set())),
        ("licence file", lambda: cmd_record_licence(
            "pleiades", Path("no-such-licence.txt"),
            "https://example.invalid", Path("g.json"))),
        ("declaration file", lambda: cmd_record_declaration(
            "pleiades", Path("no-such-decl.txt"),
            "https://example.invalid", Path("g.json"))),
    ):
        expect_raises(
            call,
            f"a missing {label} raises with its resolved path, not a traceback",
            contains="resolved to",
        )

    # An absolute path must NOT be told it is relative to the working directory.
    # The first version of this message said so unconditionally, and said it to
    # a fully-qualified Windows path — a message naming a cause that cannot
    # apply, produced by the very helper written to stop that happening.
    with tempfile.TemporaryDirectory() as tmp:
        absent = Path(tmp).resolve() / "no-such-dump-20260810.csv.gz"
        try:
            require_file(absent, "Pleiades dump", "hint text")
        except GazetteerError as exc:
            msg = str(exc)
            expect("relative to" not in msg,
                   "an absolute missing path is not told it is relative")
            expect("holds no" in msg or "holds:" in msg,
                   "an absolute missing path reports what its directory does hold")
            expect("hint text" in msg, "the hint survives either branch")

    # A snapshot with no date is the defect family this repository has recorded
    # five times: a result comparable only within the thing that produced it.
    expect(dump_date_from_name(Path("pleiades-places-20260812.csv.gz")) == "2026-08-12",
           "a dated dump filename yields its date")
    expect_raises(
        lambda: dump_date_from_name(Path("pleiades-places-latest.csv.gz")),
        "an undated 'latest' dump is refused",
        contains="date",
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        dump = tmp / "pleiades-places-20260812.csv.gz"
        rows = [
            ",".join(REAL_DUMP_HEADER),
            # Shaped on the real first row of the 2026-08-10 dump: a bbox
            # written comma-separated, and a GeoJSON `extent` that is NOT a bbox.
            _row({"id": "39271", "title": "Adulis", "description": "Red Sea port",
                  "reprLat": "15.262", "reprLong": "39.659",
                  "bbox": "39.659, 15.262, 39.659, 15.262",
                  "extent": '{"type": "Point", "coordinates": [39.659, 15.262]}',
                  "timePeriods": "RL", "timePeriodsKeys": "roman, late-antique",
                  "featureTypes": "settlement", "locationPrecision": "precise",
                  "minDate": "-30", "maxDate": "640",
                  "authors": "R. Talbert", "creators": "S. Gillies"}),
            _row({"id": "981523", "title": "Limyrike", "description": "coastal region",
                  "bbox": "75.0, 8.0, 77.0, 12.0"}),
            _row({"id": "000000", "title": "Nowhere"}),
        ]
        dump.write_bytes(gzip.compress(("\n".join(rows) + "\n").encode("utf-8")))

        found, header, _ = read_dump(dump, {"39271", "981523"})
        expect(set(found) == {"39271", "981523"}, "only the wanted ids are extracted")
        expect(found["39271"]["repr_point"] == [39.659, 15.262],
               "the representative point is stored in GeoJSON [lon, lat] order")
        expect(found["981523"]["bbox"] == [75.0, 8.0, 77.0, 12.0],
               "a comma-separated bbox parses as [min_lon, min_lat, max_lon, max_lat]")
        expect(found["39271"]["bbox"] == [39.659, 15.262, 39.659, 15.262],
               "bbox and repr_point agree on lon-then-lat, as the real dump has them")
        expect(found["39271"]["min_date"] == "-30"
               and found["39271"]["max_date"] == "640"
               and found["39271"]["location_precision"] == "precise",
               "attested dates and Pleiades' own location precision are captured — "
               "an id can resolve cleanly and still denote a mediaeval place")
        expect("extent" not in map_columns(REAL_DUMP_HEADER).values(),
               "the GeoJSON `extent` column is never read as a bbox")

        # Pleiades writes a degenerate bbox (min == max) for a point place —
        # observed on Hoby/98983, the first entry ever cached. `has_extent` and
        # `has_area` must not be the same question, or A5 renders a point as a
        # zero-size box and a region as nothing.
        point_like = Entry(
            gazetteer="pleiades", gazetteer_id="98983", title="Hoby", description=None,
            repr_point=[11.230919, 54.740603],
            bbox=[11.230919, 54.740603, 11.230919, 54.740603],
            time_periods="R", feature_types="cemetery", authors="…", creators="…",
            min_date="-30", max_date="300", time_period_keys="roman",
            location_precision="precise", dump_date="2026-08-10",
            retrieved="2026-08-12",
        )
        expect(point_like.has_extent and not point_like.has_area,
               "a degenerate bbox counts as a bbox but NOT as an area")
        region_like = Entry(**{**vars(point_like), "bbox": [75.0, 8.0, 77.0, 12.0]})
        expect(region_like.has_area, "a real bbox has area")
        expect(header == REAL_DUMP_HEADER, "the observed header is reported back")
        expect(found["39271"]["authors"] == "R. Talbert"
               and found["39271"]["creators"] == "S. Gillies",
               "per-place attribution is captured in the same pass as the "
               "coordinates — CC BY credits places, not projects")
        expect(found["981523"]["authors"] is None,
               "a place with no credited authors records none rather than ''")

        # --find reports and never caches. Searching the snapshot rather than
        # the website is the point: the cache is built from this file, so a name
        # that exists on live Pleiades but not here would be a coordinate
        # sourced from something other than what was searched.
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            code = cmd_find(dump, "adul")
        out = buf.getvalue()
        expect(code == 0 and "39271" in out and "Adulis" in out,
               "--find matches a title case-insensitively and reports the id")
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            cmd_find(dump, "Lolland")
        miss = buf.getvalue()
        expect("no place title or description matches" in miss
               and "regional" in miss,
               "--find on an absent name says so, and names 'regional' as the "
               "honest answer rather than inviting a nearby place")

        # --survey: one pass, many terms, grouped by record. A group with no
        # hits must still be PRINTED — an absent name has to be visibly absent,
        # or a shorter list reads as a complete one.
        survey = tmp / "survey.txt"
        survey.write_text("@rec-a\nAdulis\n\n@rec-b\nLolland\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            code = cmd_survey(survey, dump)
        s_out = buf.getvalue()
        expect(code == 0 and "@rec-a" in s_out and "@rec-b" in s_out,
               "--survey groups its output by record label")
        expect("'Lolland': nothing" in s_out,
               "--survey prints a term with no hits rather than omitting it")
        expect("39271" in s_out, "--survey reports the id of a hit")

        # --find and --survey must answer the SAME question. They did not: only
        # --find matched a bare number against the id column, so a survey of ten
        # real ids reported 'nothing' for every one — and reported a false hit
        # where the number appeared inside another record's description.
        id_survey = tmp / "ids.txt"
        id_survey.write_text("@ids\n39271\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            cmd_survey(id_survey, dump)
        id_out = buf.getvalue()
        expect("[ID]" in id_out and "Adulis" in id_out,
               "--survey matches a bare numeric term against the id column, "
               "exactly as --find does")

        found_none, _, _ = read_dump(dump, {"000000"})
        expect(found_none["000000"]["repr_point"] is None
               and found_none["000000"]["bbox"] is None,
               "a place with no geometry is stored as having none, not as [0, 0]")

        # resolve() raises rather than returning None: a caller that could get
        # None is a caller that could render something anyway.
        cache = empty_cache()
        expect_raises(
            lambda: resolve("pleiades:39271", cache),
            "an uncached id raises rather than returning None",
            contains="not been guessed",
        )

        cache["places"]["pleiades:39271"] = {
            **found["39271"], "dump_date": "2026-08-12", "retrieved": "2026-08-12",
        }
        entry = resolve("pleiades:39271", cache)
        expect(isinstance(entry, Entry) and entry.has_point and entry.dump_date == "2026-08-12",
               "a cached entry resolves and carries its snapshot date")

        cache["places"]["pleiades:39271"]["gazetteer_id"] = "999"
        expect_raises(
            lambda: entries(cache),
            "a cache key that disagrees with its entry's id is refused",
            contains="does not match",
        )


def test_unlocated() -> None:
    """A6: 'no entry at all' and 'an entry with no location' are two states."""
    print("\nunlocated — the gazetteer holds the place and not its location")

    p = parse_place(place(ground="regional", note="n", unlocated=True),
                    "d", "findspot_places", 0)
    expect(p.unlocated and p.locatable and not p.drawable,
           "an unlocated placement is locatable — its id must resolve — but "
           "is never drawable")

    ordinary = parse_place(place(), "d", "findspot_places", 0)
    expect(not ordinary.unlocated and ordinary.drawable,
           "an ordinary placement is drawable and not unlocated")

    no_id = parse_place(
        place(ground="regional", gazetteer=_OMIT, gazetteer_id=_OMIT,
              uri=_OMIT, note="no gazetteer has this place"),
        "d", "findspot_places", 0)
    expect(not no_id.locatable and not no_id.drawable and not no_id.unlocated,
           "a place no gazetteer holds is neither locatable nor unlocated — "
           "the two states this key exists to separate")

    # `unlocated` is a claim ABOUT an entry, so it needs an entry to be about.
    expect_raises(
        lambda: parse_place(
            place(ground="regional", gazetteer=_OMIT, gazetteer_id=_OMIT,
                  uri=_OMIT, note="n", unlocated=True),
            "d", "findspot_places", 0),
        "unlocated without a gazetteer_id is refused",
        contains="no entry to make the claim about",
    )
    # Same rule as `contested`: an explicit false re-creates the third state.
    expect_raises(
        lambda: parse_place(place(unlocated=False), "d", "findspot_places", 0),
        "unlocated written as false is refused",
        contains="only be written as true",
    )


def test_check_verifies_unlocated() -> None:
    """The claim is checked against the gazetteer, never trusted."""
    print("\ncheck() and the unlocated claim")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        corpus = tmp / "seed_corpus" / "africa"
        corpus.mkdir(parents=True)
        seed = corpus / "r.json"
        gaz = tmp / "gazetteer.json"

        cache = empty_cache()
        cache["places"]["pleiades:39271"] = {
            "gazetteer": "pleiades", "gazetteer_id": "39271",
            "title": "Kyeneion", "description": None,
            "repr_point": None, "bbox": None,
            "time_periods": "R", "feature_types": "region",
            "authors": "R. Talbert", "creators": None,
            "min_date": "-30", "max_date": "300", "time_period_keys": "roman",
            "location_precision": "unlocated",
            "dump_date": "2026-08-10", "retrieved": "2026-08-13",
        }
        cache["sources"]["pleiades"] = {"dump_date": "2026-08-10"}
        cache["licences"]["pleiades"] = {
            "text": "…verbatim…", "source_url": "https://example.invalid/l",
            "recorded": "2026-08-13",
            "declared_by": {"publisher": "Pleiades", "text": "…verbatim…",
                            "source_url": "https://example.invalid/c",
                            "recorded": "2026-08-13"},
        }
        write_cache(cache, gaz)

        # Without the key, an entry with no geometry fails — and the failure
        # now names the key as the honest way to say so.
        seed.write_text(json.dumps({
            "id": "africa-03",
            "findspot_places": [place(ground="regional", note="n")],
        }), encoding="utf-8")
        code, out = check_with_output(tmp / "seed_corpus", gaz)
        expect(code == 1 and "unlocated" in out,
               "an entry with neither point nor extent still fails, and the "
               "failure names `unlocated` as the way to record it honestly")

        # With the key, the same entry passes and is counted separately.
        seed.write_text(json.dumps({
            "id": "africa-03",
            "findspot_places": [
                place(ground="regional", note="n", unlocated=True)],
        }), encoding="utf-8")
        code, out = check_with_output(tmp / "seed_corpus", gaz)
        expect(code == 0 and "holds the place but not its location" in out,
               "a declared-unlocated placement passes and is reported apart "
               "from the ordinary gaps")

        # The claim is VERIFIED. The day Pleiades locates Kyeneion, a stale
        # `unlocated` must fail rather than quietly keep drawing nothing.
        cache["places"]["pleiades:39271"]["repr_point"] = [39.659, 15.262]
        write_cache(cache, gaz)
        code, out = check_with_output(tmp / "seed_corpus", gaz)
        expect(code == 1 and "DOES carry a location" in out,
               "an unlocated claim against an entry that HAS a location fails "
               "— the claim is checked against the gazetteer, not trusted")


def _dated_entry(**over) -> Entry:
    """An Entry fixture whose dates are the thing under test."""
    base = dict(
        gazetteer="pleiades", gazetteer_id="39271", title="Adouli",
        description=None, repr_point=[39.659, 15.262], bbox=None,
        time_periods="R", feature_types="settlement", authors="R. Talbert",
        creators=None, min_date="-30", max_date="300",
        time_period_keys="roman", location_precision="precise",
        dump_date="2026-08-10", retrieved="2026-08-13",
    )
    base.update(over)
    return Entry(**base)


def test_dates() -> None:
    """A6: an id can resolve, carry a real point, and attest the wrong era."""
    print("\ndates — the project's window, and what an entry actually attests")

    # Derived ranges, as --refresh-periods would cache them.
    ranges = {
        "roman": {"min": -30.0, "max": 300.0, "rows": 9000},
        "late-antique": {"min": 300.0, "max": 640.0, "rows": 3000},
        "achaemenid-central-asia": {"min": -540.0, "max": -330.0, "rows": 40},
        "modern": {"min": 1700.0, "max": 2100.0, "rows": 800},
        "mediaeval": {"min": 640.0, "max": 1453.0, "rows": 500},
        "sixteenth-ce": {"min": 1500.0, "max": 1600.0, "rows": 300},
        "archaic": {"min": -750.0, "max": -550.0, "rows": 200},
    }

    expect(ranges_overlap((-30, 300), (-27, 1204))
           and not ranges_overlap((1500, 1600), (-27, 1204)),
           "overlap is closed-interval and symmetric")
    expect(ranges_overlap((1204, 1500), (-27, 1204)),
           "touching the window at a single year counts as overlap")

    ok = _dated_entry()
    expect(date_audit(ok, ranges)[0] == DATE_OK,
           "a Roman-era entry passes")

    # Pleiades is not confined to antiquity, so an id can resolve perfectly and
    # denote a place attested only centuries after this corpus.
    #
    # NOT the "Borgo Medievale" numbers, and that is a finding rather than a
    # fixture choice. `gazetteer.py`'s COLUMN_CANDIDATES comment offered that
    # row (640..1453) as the motivating out-of-era case; written as a test it
    # PASSES, because this project runs to AD 1204 and the two ranges overlap
    # by 564 years. The comment has been corrected in place. An entry has to be
    # genuinely post-mediaeval to be out of this project's era.
    outside = _dated_entry(title="Palazzo Reale", min_date="1500",
                           max_date="1600", time_periods="S",
                           time_period_keys="sixteenth-ce")
    verdict, detail = date_audit(outside, ranges)
    expect(verdict == DATE_OUTSIDE and "entirely outside" in (detail or ""),
           "an entry attested only after the project's window is refused, and "
           "the failure names the range it actually has")
    expect(date_audit(_dated_entry(title="Borgo Medievale", min_date="640",
                                   max_date="1453",
                                   time_period_keys="mediaeval"),
                      ranges)[0] == DATE_OK,
           "a mediaeval entry is IN era — this project runs to the Fourth "
           "Crusade, and the guard must not fire on the centuries it covers")

    early = _dated_entry(min_date="-1200", max_date="-400",
                         time_period_keys="archaic")
    expect(date_audit(early, ranges)[0] == DATE_OUTSIDE,
           "and likewise one attested only before it")

    # THE MOTIVATING CASE, on real values. The Ka'ba-ye Zartosht attests
    # `achaemenid-central-asia` and `modern`; Pleiades derives minDate/maxDate
    # from those, so the hull is -540..2100 and spans the 2,240-year gap
    # between them. The SKZ inscription it carries is 3rd-century — which sits
    # squarely in that gap. The hull says in-scope; nothing attested is.
    kaba = _dated_entry(
        gazetteer_id="616346030", title="Ka'ba-ye Zartosht",
        time_periods="AM", time_period_keys="achaemenid-central-asia,modern",
        min_date="-540", max_date="2100", feature_types="monument",
    )
    hull = entry_hull(kaba)
    expect(hull == (-540.0, 2100.0) and in_project_window(hull),
           "the Ka'ba's HULL covers the project window — which is why the "
           "hull alone cannot answer this")
    verdict, detail = date_audit(kaba, ranges)
    expect(verdict == DATE_HOLE,
           "an entry whose hull spans the window but whose every attested "
           "period falls outside it is reported as a hole, NOT as a failure — "
           "the placement can be correct and the gazetteer merely narrow")
    expect("achaemenid-central-asia" in (detail or "")
           and "modern" in (detail or ""),
           "and the note names the periods it does attest, with their ranges")

    # THE BOUNDARY BETWEEN `hole` AND `unknown`, got wrong on the first real
    # run against the 2026-08-10 dump. `achaemenid-central-asia` appears in no
    # single-period row, so it has no derived range — and the first version
    # called this a hole because no KNOWN period was in era. A hole is the
    # positive claim that NOTHING attested is in era, and it cannot be made
    # while a period is unaccounted for: that period could be the one in era.
    partial = {k: v for k, v in ranges.items() if k != "achaemenid-central-asia"}
    verdict, detail = date_audit(kaba, partial)
    expect(verdict == DATE_UNKNOWN,
           "a period with NO derived range makes the verdict unknown, not a "
           "hole — the missing period could be the one in era")
    expect("achaemenid-central-asia" in (detail or "")
           and "modern" in (detail or ""),
           "and the message names both what is known to be out of era and "
           "what could not be checked, so the reader sees how close it is")

    # `unknown` is never quietly folded into `ok`. A check that cannot tell
    # must say so — the same rule that makes an uncached id raise.
    expect(date_audit(kaba, {})[0] == DATE_UNKNOWN,
           "with no derived vocabulary, the verdict is unknown rather than ok")
    expect(date_audit(_dated_entry(time_period_keys="never-derived"),
                      ranges)[0] == DATE_UNKNOWN,
           "a period key with no derived range is unknown, not ok")
    expect(date_audit(_dated_entry(min_date=None, max_date=None,
                                   time_period_keys=None),
                      ranges)[0] == DATE_NO_DATES,
           "an entry with no dates at all is 'no_dates' — correct for "
           "GeoNames, which is a gazetteer of modern places")

    # A hole must not be reported when ONE attested period is in scope, even
    # if others are not — Adane attests fifteen periods spanning 3,200 years.
    mixed = _dated_entry(time_period_keys="achaemenid-central-asia,roman,modern",
                         min_date="-540", max_date="2100")
    expect(date_audit(mixed, ranges)[0] == DATE_OK,
           "one in-scope attested period is enough; the others are not a defect")


def test_derive_period_ranges() -> None:
    """The vocabulary is derived FROM THE DUMP, never written from memory."""
    print("\nderiving the period vocabulary from the dump")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        dump = tmp / "pleiades-places-20260810.csv.gz"
        rows = [
            ",".join(REAL_DUMP_HEADER),
            # Single-period rows. Each states its period's range outright.
            _row({"id": "1", "title": "A", "timePeriodsKeys": "roman",
                  "minDate": "-30", "maxDate": "300"}),
            _row({"id": "2", "title": "B", "timePeriodsKeys": "roman",
                  "minDate": "-30", "maxDate": "300"}),
            _row({"id": "3", "title": "C", "timePeriodsKeys": "modern",
                  "minDate": "1700", "maxDate": "2100"}),
            # Multi-period: says nothing about any single period, and must be
            # skipped rather than attributed to the first key. `only-paired`
            # appears here and nowhere else, so it ends with no range at all —
            # the real `achaemenid-central-asia` case in miniature.
            _row({"id": "4", "title": "D",
                  "timePeriodsKeys": "roman,only-paired",
                  "minDate": "-30", "maxDate": "2100"}),
            # Two single-period rows that DISAGREE. The key must be recorded
            # as ambiguous and given no range — never resolved by majority.
            _row({"id": "5", "title": "E", "timePeriodsKeys": "disputed",
                  "minDate": "100", "maxDate": "200"}),
            _row({"id": "6", "title": "F", "timePeriodsKeys": "disputed",
                  "minDate": "100", "maxDate": "200"}),
            _row({"id": "7", "title": "G", "timePeriodsKeys": "disputed",
                  "minDate": "900", "maxDate": "1000"}),
        ]
        dump.write_bytes(gzip.compress(("\n".join(rows) + "\n").encode("utf-8")))

        derived, ambiguous, rows_read, single = derive_period_ranges(dump)
        expect(rows_read == 7 and single == 6,
               "every row is read; the multi-period one is not counted as "
               "stating a single period's range")
        expect(derived["roman"] == {"min": -30.0, "max": 300.0, "rows": 2},
               "a period's range is taken from rows attesting exactly it, and "
               "the supporting row count is kept")
        expect(derived["modern"]["min"] == 1700.0,
               "a second period is derived independently")
        expect("disputed" not in derived and "disputed" in ambiguous,
               "a key whose rows disagree is given NO range — a majority rule "
               "would make the check assert what the dump does not say")
        # A period appearing ONLY alongside others gets no range and is NOT
        # ambiguous — it is simply absent, which is a third cause of "no range"
        # and has to stay distinguishable from the other two or the report
        # names the wrong one. Observed on the real dump: of 42,389 rows,
        # `achaemenid-central-asia` is in no single-period row, so 99 keys were
        # derived and it was not among them.
        expect("only-paired" not in derived and "only-paired" not in ambiguous,
               "a period appearing only alongside others is neither derived "
               "nor ambiguous — it is absent, and that is a third cause")
        expect(ambiguous["disputed"][0]["rows"] == 2,
               "and the disagreement is recorded, most-supported first, so the "
               "reason it has no range sits beside it")

        # An entry using an ambiguous key audits as unknown, not as ok.
        expect(date_audit(_dated_entry(time_period_keys="disputed"),
                          derived)[0] == DATE_UNKNOWN,
               "an ambiguous key propagates as 'unknown' to every entry using it")

        # End to end: --refresh-periods caches the vocabulary with provenance.
        gaz = tmp / "gazetteer.json"
        write_cache(empty_cache(), gaz)
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            code = cmd_refresh_periods(dump, gaz)
        out = buf.getvalue()
        expect(code == 0, "--refresh-periods succeeds on a well-formed dump")
        cached = load_cache(gaz)
        expect(period_ranges_from_cache(cached)["roman"]["max"] == 300.0,
               "the derived vocabulary is cached where --check reads it")
        prov = cached["periods"]["derived_from"]
        expect(prov["dump_date"] == "2026-08-10"
               and prov["dump_file"] == dump.name
               and prov["rows_read"] == 7,
               "the vocabulary records which dated dump it came from — the "
               "same discipline every cached coordinate is held to")
        expect("ambiguous" in out.lower() or "disputed" in out,
               "the ambiguous key is reported rather than silently dropped")

        # A dump with no period columns cannot yield a vocabulary, and must
        # say which column was missing rather than derive an empty one.
        # It carries geometry, so the failure is about the PERIOD columns and
        # not about `map_columns`' own geometry gate firing first — a check
        # that names the wrong cause is the defect this repository keeps
        # paying for, and it applies to test fixtures too.
        thin = tmp / "pleiades-places-20260811.csv.gz"
        thin.write_bytes(gzip.compress(
            b"id,title,reprLat,reprLong\n1,A,15.0,39.0\n"
        ))
        expect_raises(lambda: derive_period_ranges(thin),
                      "a dump with no period columns is refused, naming the "
                      "column it wanted",
                      contains="time_period_keys")


def test_check_reports_dates() -> None:
    """cmd_check: `outside` fails the build, `hole` is only a note."""
    print("\ncheck() and the date audit")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        corpus = tmp / "seed_corpus" / "africa"
        corpus.mkdir(parents=True)
        (corpus / "r.json").write_text(
            json.dumps({"id": "africa-03", "findspot_places": [place()]}),
            encoding="utf-8",
        )
        gaz = tmp / "gazetteer.json"

        cache = empty_cache()
        cache["places"]["pleiades:39271"] = {
            "gazetteer": "pleiades", "gazetteer_id": "39271",
            "title": "Adouli", "description": None,
            "repr_point": [39.659, 15.262], "bbox": None,
            "time_periods": "R", "feature_types": "settlement",
            "authors": "R. Talbert", "creators": None,
            "min_date": "-30", "max_date": "300", "time_period_keys": "roman",
            "location_precision": "precise",
            "dump_date": "2026-08-10", "retrieved": "2026-08-13",
        }
        cache["sources"]["pleiades"] = {"dump_date": "2026-08-10"}
        cache["licences"]["pleiades"] = {
            "text": "…verbatim…", "source_url": "https://example.invalid/l",
            "recorded": "2026-08-13",
            "declared_by": {"publisher": "Pleiades", "text": "…verbatim…",
                            "source_url": "https://example.invalid/c",
                            "recorded": "2026-08-13"},
        }
        cache["periods"] = {
            "ranges": {
                "roman": {"min": -30.0, "max": 300.0, "rows": 9000},
                "sixteenth-ce": {"min": 1500.0, "max": 1600.0, "rows": 300},
                "achaemenid-central-asia": {"min": -540.0, "max": -330.0, "rows": 40},
                "modern": {"min": 1700.0, "max": 2100.0, "rows": 800},
            },
            "ambiguous": {},
            "derived_from": {"dump_date": "2026-08-10", "dump_file": "d.csv.gz",
                             "retrieved": "2026-08-13", "method": "…",
                             "rows_read": 1, "single_period_rows": 1},
        }
        write_cache(cache, gaz)
        expect(quiet_check(tmp / "seed_corpus", gaz) == 0,
               "an in-era placement passes the check")

        # The hole: a note, and the build still succeeds.
        cache["places"]["pleiades:39271"].update(
            title="Ka'ba-ye Zartosht", min_date="-540", max_date="2100",
            time_periods="AM",
            time_period_keys="achaemenid-central-asia,modern",
        )
        write_cache(cache, gaz)
        code, out = check_with_output(tmp / "seed_corpus", gaz)
        expect(code == 0 and "attested periods all fall outside" in out,
               "a placement whose every attested period is out of era is "
               "REPORTED and does not fail the check")

        # Outside: a failure, because nothing it attests can be what is cited.
        # Post-mediaeval, not mediaeval — this project runs to AD 1204, so a
        # 640..1453 entry is in era. See test_dates.
        cache["places"]["pleiades:39271"].update(
            title="Palazzo Reale", min_date="1500", max_date="1600",
            time_periods="S", time_period_keys="sixteenth-ce",
        )
        write_cache(cache, gaz)
        code, out = check_with_output(tmp / "seed_corpus", gaz)
        expect(code == 1 and "entirely outside" in out,
               "a placement resolving to an entry attested only outside the "
               "project's window FAILS the check, and the failure says why")


def quiet_check(corpus: Path, gaz: Path) -> int:
    """cmd_check prints its own FAILED block. Swallow it.

    Otherwise a passing run of this suite scrolls several genuine-looking
    "FAILED" lines past the reader — and a message that points at something
    healthy is a defect this repository has already paid for twice.
    """
    return check_with_output(corpus, gaz)[0]


def check_with_output(corpus: Path, gaz: Path) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = cmd_check(corpus, gaz)
    return code, buf.getvalue()


def test_check_exits_nonzero() -> None:
    print("\ncheck() exits non-zero rather than warning")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        corpus = tmp / "seed_corpus" / "africa"
        corpus.mkdir(parents=True)
        (corpus / "r.json").write_text(
            json.dumps({"id": "africa-03", "findspot_places": [place()]}),
            encoding="utf-8",
        )
        gaz = tmp / "gazetteer.json"

        cache = empty_cache()
        write_cache(cache, gaz)
        expect(quiet_check(tmp / "seed_corpus", gaz) == 1,
               "an unresolved placement fails the check")

        cache["places"]["pleiades:39271"] = {
            "gazetteer": "pleiades", "gazetteer_id": "39271",
            "title": "Adulis", "description": None,
            "repr_point": [39.659, 15.262], "bbox": None, "time_periods": "RL",
            "feature_types": "settlement", "authors": "R. Talbert", "creators": None,
            "dump_date": "2026-08-12",
            "retrieved": "2026-08-12",
        }
        cache["sources"]["pleiades"] = {"dump_date": "2026-08-12"}
        write_cache(cache, gaz)
        code, out = check_with_output(tmp / "seed_corpus", gaz)
        expect(code == 1,
               "a resolving placement STILL fails while the licence is unconfirmed")
        # The exit code alone cannot pin this. Two licence rules run in
        # sequence, so disabling the first lets the second fail the run and the
        # exit code never moves — the over-determination `mutate_part8.py`
        # records twice, where the guard that did the work was always the check
        # on what the failure NAMES. Third instance; same answer.
        expect("unconfirmed" in out.lower(),
               "the unconfirmed-licence failure names it as unconfirmed")

        cache["licences"]["pleiades"] = {"text": "…verbatim licence terms…",
                                         "source_url": "https://example.invalid/licence",
                                         "recorded": "2026-08-12"}
        write_cache(cache, gaz)
        expect(quiet_check(tmp / "seed_corpus", gaz) == 1,
               "the licence terms alone are not enough — the publisher's "
               "declaration that they apply is a second claim")

        cache["licences"]["pleiades"]["declared_by"] = {
            "publisher": "Pleiades", "text": "…verbatim publisher statement…",
            "source_url": "https://example.invalid/credits",
            "recorded": "2026-08-12",
        }
        write_cache(cache, gaz)
        expect(quiet_check(tmp / "seed_corpus", gaz) == 0,
               "with the id cached, the licence recorded and its declaration "
               "recorded, the check passes")

        cache["places"]["pleiades:39271"]["repr_point"] = None
        write_cache(cache, gaz)
        expect(quiet_check(tmp / "seed_corpus", gaz) == 1,
               "an entry resolving to neither point nor extent fails")

        # A regional placement renders as an EXTENT and never as a pin
        # (PLACES.md). So a regional id whose bbox is degenerate resolves,
        # caches, passes every other check here — and draws nothing at all.
        #
        # Not hypothetical: `pleiades:766 Aegyptus` is exactly this, and Egypt
        # is the `source` in three of the seven literary records. The most
        # connected node in the corpus would have been blank space on the first
        # map that drew it, with nothing anywhere saying so.
        #
        # Reported, not failed. The entry is honest and the id is right; what to
        # do about it is A5's decision, and a failure would demand a fix before
        # the decision could be taken.
        cache["places"]["pleiades:39271"]["repr_point"] = [39.659, 15.262]
        cache["places"]["pleiades:39271"]["bbox"] = [39.659, 15.262, 39.659, 15.262]
        seed = corpus / "r.json"
        original = seed.read_text(encoding="utf-8")
        seed.write_text(
            json.dumps({"id": "africa-03",
                        "findspot_places": [place(ground="regional")]}),
            encoding="utf-8",
        )
        write_cache(cache, gaz)
        code, out = check_with_output(tmp / "seed_corpus", gaz)
        expect(code == 0 and "cannot be drawn as an extent" in out,
               "a regional placement whose bbox has no area is reported as "
               "unrenderable, and does not fail the check")

        # ...and the same entry with a real bbox says nothing, so the report is
        # about area and not about being regional.
        cache["places"]["pleiades:39271"]["bbox"] = [39.0, 15.0, 40.0, 16.0]
        write_cache(cache, gaz)
        code, out = check_with_output(tmp / "seed_corpus", gaz)
        expect(code == 0 and "cannot be drawn as an extent" not in out,
               "a regional placement with a real extent is not reported")

        seed.write_text(original, encoding="utf-8")
        cache["places"]["pleiades:39271"]["bbox"] = None
        write_cache(cache, gaz)

        # Pleiades keeps deprecated records in the dump, with a plausible
        # coordinate. 427224440 is "Erroneous Duplicate: Al-Hijr (Madâ'in
        # Sâlih)" and sits at Hegra's own point — it resolves, and citing it
        # would cite a record the publisher marks as wrong.
        cache["places"]["pleiades:39271"]["repr_point"] = [39.659, 15.262]
        cache["places"]["pleiades:39271"]["title"] = "Erroneous Duplicate: Adulis"
        write_cache(cache, gaz)
        code, out = check_with_output(tmp / "seed_corpus", gaz)
        expect(code == 1 and "deprecated" in out.lower(),
               "a resolving id whose title marks it deprecated is refused, and "
               "the failure says so")
        expect(looks_deprecated("Erroneous Duplicate: Al-Hijr")
               and not looks_deprecated("Hoby"),
               "the deprecation test reads the title and does not fire on "
               "ordinary places")

        expect(LICENCE_UNCONFIRMED.startswith("UNCONFIRMED"),
               "the unconfirmed licence sentinel is unmistakable on sight")


def _geonames_zip(path: Path, rows: list[list[str]],
                  when: tuple = (2026, 8, 11, 3, 0, 0)) -> Path:
    """A GeoNames country dump, built the way GeoNames builds one.

    Written as a zip with an explicit member timestamp because that timestamp
    IS the snapshot date — see `geonames_dump_date`. A fixture that used a
    bare .txt would exercise a path the real workflow never takes.
    """
    text = "\n".join("\t".join(r) for r in rows) + "\n"
    info = zipfile.ZipInfo(path.name.replace(".zip", ".txt"), date_time=when)
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(info, text)
    return path


def _gn_row(gid: str, name: str, lat: str, lon: str,
            fclass: str = "P", fcode: str = "PPL", cc: str = "KR") -> list[str]:
    return [gid, name, name, "", lat, lon, fclass, fcode, cc, "",
            "13", "", "", "", "0", "", "", "Asia/Seoul", "2019-09-06"]


def test_geonames() -> None:
    print("\ngeonames")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        good = _geonames_zip(tmp / "KR.zip", [_gn_row("1835235", "Gyeongju", "35.84278", "129.21167")])
        rows = read_geonames_dump(good, {"1835235"})
        entry = rows["1835235"]
        expect(entry["repr_point"] == [129.21167, 35.84278],
               "a GeoNames row yields [lon, lat] in GeoJSON order, not [lat, lon]")
        expect(entry["bbox"] is None,
               "a GeoNames entry carries no bbox, so it can never draw an extent")
        expect(entry["min_date"] is None and entry["max_date"] is None,
               "a GeoNames entry states no attestation range rather than "
               "borrowing its record-edit date")

        # The columns are positional and there is no header to discover them
        # from, so the obligation behind the discovery rule is met by verifying
        # the SHAPE instead. Both of these produced 19 fields of nonsense in the
        # first draft, silently.
        # Asserted against `verify_geonames_shape` directly rather than through
        # `read_geonames_dump`. Removing the guard and going through the reader
        # produces a KeyError three lines later, and `mutate_places.py` counts a
        # crash as a MISS — correctly, since a crash is not a guard firing. The
        # guard is a pure function, so it is tested as one and its mutation
        # then reports "no error raised", which is the guard not working.
        # A row with EXTRA fields, not a truncated one. Both are refused, but a
        # short row makes the guard's own later lines raise IndexError when the
        # guard is disabled, and `mutate_places.py` counts a crash as a MISS —
        # so the mutation could never be shown to work. A long row exercises the
        # identical check and, with it removed, silently truncates to 19 columns
        # instead of crashing: which is the real defect anyway, since a stray tab
        # inside a name misaligns every column after it.
        expect_raises(lambda: verify_geonames_shape(
                          _gn_row("1", "a", "1.0", "2.0") + ["extra", "tabs", "here"],
                          1, Path("LONG.zip")),
                      "a dump with the wrong field count is refused, naming the count",
                      contains="19 tab-separated fields")
        expect_raises(lambda: verify_geonames_shape(["geonameid"] + ["x"] * 18, 1,
                                                    Path("HEAD.zip")),
                      "a header row is refused — GeoNames dumps have none",
                      contains="not a numeric geonameid")
        expect_raises(lambda: verify_geonames_shape(
                          _gn_row("1", "a", "1.0", "2.0", fclass="Z"), 1, Path("CLS.zip")),
                      "an undocumented feature class is refused",
                      contains="feature class")
        expect_raises(lambda: verify_geonames_shape(
                          _gn_row("1", "a", "north", "2.0"), 1, Path("LAT.zip")),
                      "a coordinate that does not parse is refused",
                      contains="do not parse")

        # ...and the same check, reached the way the reader reaches it, so the
        # guard is known to be wired in and not merely to exist.
        long_row = _geonames_zip(
            tmp / "LONG.zip",
            [_gn_row("1", "a", "1.0", "2.0") + ["extra", "tabs", "here"]])
        expect_raises(lambda: read_geonames_dump(long_row, None),
                      "the reader applies the shape check to the first data row",
                      contains="19 tab-separated fields")

        # A truncated row is refused too — asserted through the reader, where a
        # short row cannot reach the guard's later lines.
        short = _geonames_zip(tmp / "SHORT.zip", [["1", "x", "y"]])
        expect_raises(lambda: read_geonames_dump(short, None),
                      "a truncated row is refused as well as an over-long one",
                      contains="19 tab-separated fields")

        # The snapshot date comes from the publisher's own zip timestamp. A
        # bare .txt has only an mtime, which records when the CURATOR unzipped
        # it — the undated-snapshot defect this repository has logged five times.
        expect(geonames_dump_date(good) == "2026-08-11",
               "the snapshot date is read from the zip's publisher timestamp")
        loose = tmp / "KR.txt"
        loose.write_text("\t".join(_gn_row("1", "a", "1.0", "2.0")) + "\n",
                         encoding="utf-8")
        expect_raises(lambda: geonames_dump_date(loose),
                      "an unzipped .txt is refused a guessed date, and says why",
                      contains="--geonames-date")

        # A second gazetteer means a second licence. One flat `licence` block
        # would have recorded GeoNames' CC BY 4.0 over Pleiades' CC BY 3.0 US,
        # with nothing noticing that half the points were attributed wrongly.
        corpus = tmp / "seed_corpus" / "east_asia"
        corpus.mkdir(parents=True)
        (corpus / "r.json").write_text(json.dumps({
            "id": "eastasia-03",
            "findspot_places": [{
                "name": "Gyeongju", "ground": "stated", "gazetteer": "geonames",
                "gazetteer_id": "1835235",
                "uri": "https://www.geonames.org/1835235", "note": "n",
            }],
        }), encoding="utf-8")

        gaz = tmp / "g.json"
        cache = empty_cache()
        cache["places"]["geonames:1835235"] = {
            **read_geonames_dump(good, {"1835235"})["1835235"],
            "dump_date": "2026-08-11", "retrieved": "2026-08-11",
        }
        cache["sources"]["geonames"] = {"dump_date": "2026-08-11"}
        licence = {"text": "…terms…", "source_url": "https://example.invalid",
                   "recorded": "2026-08-11",
                   "declared_by": {"publisher": "Pleiades", "text": "…",
                                   "source_url": "https://example.invalid",
                                   "recorded": "2026-08-11"}}
        cache["licences"]["pleiades"] = licence
        write_cache(cache, gaz)
        code, out = check_with_output(tmp / "seed_corpus", gaz)
        expect(code == 1 and "geonames licence is unconfirmed" in out,
               "a GeoNames placement is not covered by the Pleiades licence, "
               "and the failure names the gazetteer that is missing one")

        cache["licences"]["geonames"] = dict(licence,
                                             declared_by=dict(licence["declared_by"],
                                                              publisher="GeoNames"))
        write_cache(cache, gaz)
        expect(quiet_check(tmp / "seed_corpus", gaz) == 0,
               "with a licence recorded per gazetteer, the check passes")

        # Migration: a cache written before the GeoNames reader existed holds a
        # flat `licence` that meant Pleiades. It must keep working, and must
        # never be silently read as covering both sources.
        legacy = tmp / "legacy.json"
        legacy.write_text(json.dumps({
            "sources": {}, "places": {},
            "licence": {"text": "…terms…", "source_url": "u", "recorded": "2026-08-12"},
        }), encoding="utf-8")
        migrated = load_cache(legacy)
        expect("licence" not in migrated
               and licence_is_recorded(licence_for(migrated, "pleiades")),
               "a legacy flat licence block migrates to licences['pleiades']")
        expect(not licence_is_recorded(licence_for(migrated, "geonames")),
               "the migrated licence covers Pleiades only — it does not become "
               "a licence for a gazetteer nobody recorded one for")

        both = tmp / "both.json"
        both.write_text(json.dumps({
            "sources": {}, "places": {},
            "licence": {"text": "old"}, "licences": {"pleiades": {"text": "new"}},
        }), encoding="utf-8")
        expect_raises(lambda: load_cache(both),
                      "a cache holding BOTH licence shapes is refused rather "
                      "than one being guessed as current",
                      contains="BOTH")

        # A GeoNames country file holds one country, and this corpus spans
        # four. Every per-country refresh therefore misses the other countries'
        # ids, and the first version of this reported that as UNRESOLVED with
        # "check you have the right country file" — to a curator holding
        # exactly the right file, and with a non-zero exit. A check that
        # matches too broadly names the wrong cause.
        multi = tmp / "multi"
        (multi / "a").mkdir(parents=True)
        (multi / "b").mkdir(parents=True)
        for sub, doc, gid in (("a", "kr", "1841603"), ("b", "vn", "13405688")):
            (multi / sub / f"{doc}.json").write_text(json.dumps({
                "id": doc,
                "findspot_places": [{
                    "name": doc, "ground": "stated", "gazetteer": "geonames",
                    "gazetteer_id": gid,
                    "uri": f"https://www.geonames.org/{gid}", "note": "n",
                }],
            }), encoding="utf-8")

        kr = _geonames_zip(tmp / "KR2.zip",
                           [_gn_row("1841603", "Gyeongju", "35.84278", "129.21167")])
        vn = _geonames_zip(tmp / "VN2.zip",
                           [_gn_row("13405688", "Óc Eo", "10.242", "105.155", cc="VN")])
        multi_cache = tmp / "multi.json"
        write_cache(empty_cache(), multi_cache)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cmd_refresh_geonames(kr, multi, multi_cache, None)
        out = buf.getvalue()
        expect(code == 0,
               "a country file that lacks another country's ids is not a failure")
        expect("right country file" not in out and "UNRESOLVED" not in out,
               "and it does not tell the curator to check a file that is already correct")
        expect("13405688" in out and "still not cached" in out,
               "it names what is still missing, which is the actionable part")

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cmd_refresh_geonames(vn, multi, multi_cache, None)
        expect("every GeoNames id cited by the corpus is now cached"
               in buf.getvalue(),
               "once every country file has been read, it says so")


def _row(values: dict[str, str]) -> str:
    """Build a CSV row with the csv module, not by hand.

    The hand-rolled version quoted any field containing a comma or a space and
    was wrong the moment a real row was used as the fixture: Pleiades' `extent`
    column holds GeoJSON, so the value contains double quotes, which need
    doubling rather than wrapping. It produced a fixture the parser could not
    read, and the failure surfaced as a missing id — a fault in the test
    harness reported as a fault in the code under test.
    """
    buf = io.StringIO()
    csv.writer(buf, lineterminator="").writerow(
        [values.get(col, "") for col in REAL_DUMP_HEADER]
    )
    return buf.getvalue()


def main() -> int:
    test_valid_shapes()
    test_guards()
    test_roles()
    test_gazetteer()
    test_check_exits_nonzero()
    test_geonames()
    test_dates()
    test_derive_period_ranges()
    test_check_reports_dates()
    test_unlocated()
    test_check_verifies_unlocated()

    print()
    if failures:
        print(f"FAILED ({len(failures)})")
        for f in failures:
            print(f"  x {f}")
        return 1
    print("All place and gazetteer assertions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
