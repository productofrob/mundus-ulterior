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
from pathlib import Path

from .gazetteer import (
    Entry,
    GazetteerError,
    LICENCE_UNCONFIRMED,
    cmd_check,
    cmd_find,
    cmd_record_declaration,
    cmd_survey,
    cmd_record_licence,
    dump_date_from_name,
    empty_cache,
    entries,
    looks_deprecated,
    map_columns,
    read_dump,
    require_file,
    resolve,
    write_cache,
)
from .places import (
    GROUNDS,
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


def parse(raw, doc="africa-03-periplus-adulis", block="subject_places", i=0):
    return parse_place(raw, doc, block, i)


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
            Path("no-such-licence.txt"), "https://example.invalid", Path("g.json"))),
        ("declaration file", lambda: cmd_record_declaration(
            Path("no-such-decl.txt"), "https://example.invalid", Path("g.json"))),
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

        cache["licence"] = {"text": "…verbatim licence terms…",
                            "source_url": "https://example.invalid/licence",
                            "recorded": "2026-08-12"}
        write_cache(cache, gaz)
        expect(quiet_check(tmp / "seed_corpus", gaz) == 1,
               "the licence terms alone are not enough — the publisher's "
               "declaration that they apply is a second claim")

        cache["licence"]["declared_by"] = {
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
    test_gazetteer()
    test_check_exits_nonzero()

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
