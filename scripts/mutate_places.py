"""Mutation-verify the W1 place and gazetteer guards.

Same standard as `mutate_part7b.py`, `mutate_part8.py` and `mutate_recover.py`:
each mutation breaks exactly one rule and asserts that the guard protecting
*that* rule reports FAIL — not merely that something failed. A guard that has
never been seen to fail is not known to work, and Block A ships eleven new ones
before a single record is edited against them.

The mutations worth reading are the first three. They remove, in turn: the rule
that a specific place needs a gazetteer id, the rule that `identified` needs its
citation, and the rule that a coordinate cannot be resolved from an uncached id.
Those three are G1 criterion 2 in code. If they ever stop breaking their guards,
W1 has quietly become a map that draws whatever it is handed.

Run: python scripts/mutate_places.py
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

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

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLACES = ROOT / "ingest" / "places.py"
GAZETTEER = ROOT / "ingest" / "gazetteer.py"
SOURCES = (PLACES, GAZETTEER)

MUTATIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "a specific place no longer needs a gazetteer id — the authored-coordinate hole",
        [("""    if gazetteer_id is None and ground != "regional":""",
          """    if False:""")],
    ),
    (
        "any string is accepted as a gazetteer name",
        [("""    if gazetteer is not None and gazetteer not in GAZETTEERS:""",
          """    if False:""")],
    ),
    (
        "a gazetteer and its id no longer have to appear together",
        [("""    if (gazetteer is None) != (gazetteer_id is None):""",
          """    if False:""")],
    ),
    (
        "`identified` no longer needs the citation that makes the identification",
        [("""    if ground == "identified" and ground_citation is None:""",
          """    if False:""")],
    ),
    (
        "an uncached id resolves to None instead of raising",
        [("""    found = entries(cache).get(cache_key)
    if found is None:""",
          """    found = entries(cache).get(cache_key)
    if False:""")],
    ),
    (
        "unknown keys are ignored, as they were before eval/goldset.py",
        [("""    unknown = keys - _REQUIRED - _OPTIONAL
    if unknown:""",
          """    unknown = keys - _REQUIRED - _OPTIONAL
    if False:""")],
    ),
    (
        "an empty string is accepted as a value",
        [("""        if not value.strip():""", """        if False:""")],
    ),
    (
        "a uri may disagree with the id beside it",
        [("""        if uri != expected:""", """        if False:""")],
    ),
    (
        "a contested identification needs only one side of the argument",
        [("""    if len(cites) < 2:""", """    if False:""")],
    ),
    (
        "`contested: false` is accepted, re-creating the third state",
        [("""    if raw["contested"] is not True:""", """    if False:""")],
    ),
    (
        "a regional placement with no id no longer has to say why",
        [("""    if ground == "regional" and gazetteer_id is None and note is None:""",
          """    if False:""")],
    ),
    (
        "a record may both declare places and declare it has none",
        [("""    present = [b for b in PLACE_BLOCKS if b in record]
    if present:""",
          """    present = [b for b in PLACE_BLOCKS if b in record]
    if False:""")],
    ),
    (
        "an empty no_places_reason is accepted",
        [("""    if not isinstance(reason, str) or not reason.strip():""",
          """    if False:""")],
    ),
    (
        "a hand-written lat/lon in a seed record is accepted",
        [("""    offending = sorted(k for k in record if k.lower() in FORBIDDEN_COORDINATE_KEYS)""",
          """    offending = []""")],
    ),
    (
        "a dump header with no geometry column is accepted",
        [("""    if not has_point and "bbox" not in mapping and not has_corners:""",
          """    if False:""")],
    ),
    (
        "an undated 'latest' dump is stamped with today instead of refused",
        [("""    raise GazetteerError(
        f"cannot read a dump date from '{path.name}'.""",
          """    return "1970-01-01"
    raise GazetteerError(
        f"cannot read a dump date from '{path.name}'.""")],
    ),
    (
        "the unconfirmed-licence gate is removed",
        [("""        if not licence_is_recorded(licence):""", """        if False:""")],
    ),
    (
        "the licence may be asserted without the publisher declaring it",
        [("""    elif not (licence.get("declared_by") or {}).get("text"):""",
          """    elif False:""")],
    ),
    (
        "--survey stops matching ids, as it silently did until 2026-08-13",
        [("""    if needle_id and (row.get(cmap["id"]) or "").strip() == needle_id:""",
          """    if False:""")],
    ),
    (
        "a record the gazetteer marks as an erroneous duplicate is accepted",
        [("""        if looks_deprecated(entry.title):""", """        if False:""")],
    ),
    (
        "a cached entry with neither point nor extent passes the check",
        [("""        if not entry.has_point and not entry.has_extent:""",
          """        if False:""")],
    ),
    # A4 — the five rules that make `source -> focus -> destination` derivable.
    #
    # The first is the one to read. It does not delete the requirement, it gives
    # it a DEFAULT — which is how this defect would actually arrive, and why the
    # guard is worded around "no default" rather than around a missing key. A
    # half-edited record would then quietly assert that every place it had not
    # got to yet is merely mentioned, and the network would be short of edges
    # with nothing anywhere saying so.
    (
        "a missing role defaults to `mentioned` instead of being refused",
        [("""    if role is None:
        raise PlaceError(""",
          """    if role is None:
        return "mentioned"
    if role is None:
        raise PlaceError(""")],
    ),
    (
        "any string is accepted as a role",
        [("""    if role not in ROLES:""", """    if False:""")],
    ),
    (
        "a role is accepted on findspot_places and origin_places, where the "
        "block name already says the relation",
        [("""    if block != SUBJECT_BLOCK:
        if role is not None:""",
          """    if block != SUBJECT_BLOCK:
        if False:""")],
    ),
    (
        "two places may both be the focus, leaving every edge ambiguous about "
        "which end it has",
        [("""    if len(foci) > 1:""", """    if False:""")],
    ),
    (
        "a directional role is accepted with no focus to be directional about",
        [("""    if directional and not foci:""", """    if False:""")],
    ),
    (
        # A regional id whose bbox has no area resolves, caches and passes every
        # other check — and draws nothing, because a regional placement renders
        # as an extent and never as a pin. `pleiades:766 Aegyptus` is exactly
        # this, and Egypt is the source in three of the seven literary records.
        "a regional placement that can never be drawn is not reported",
        [("""        elif p.ground == "regional" and not entry.has_area:""",
          """        elif False:""")],
    ),
    # --- GeoNames, added 2026-08-13 with the second gazetteer ----------------
    #
    # The Pleiades reader discovers its columns from a header row. GeoNames has
    # no header and documented positional columns, so the discovery step does
    # not apply — but the obligation behind it does, and these four are what
    # replaced it. Each one, disabled, turns a malformed file into 19 fields of
    # plausible nonsense.
    (
        "the GeoNames field count is not checked, so a truncated row is accepted",
        [("""    if len(fields) != n:""", """    if False:""")],
    ),
    (
        "a GeoNames header row is accepted as data",
        [("""    if not fields[0].strip().isdigit():""", """    if False:""")],
    ),
    (
        "an undocumented GeoNames feature class is accepted",
        [("""    if fields[6].strip() and fields[6].strip() not in GEONAMES_FEATURE_CLASSES:""",
          """    if False:""")],
    ),
    (
        "an unzipped GeoNames .txt is given a guessed snapshot date",
        [("""    if path.suffix.lower() != ".zip":""", """    if False:""")],
    ),
    # The licence split. Pleiades is CC BY 3.0 US and GeoNames is CC BY 4.0;
    # each of these three restores a way for one publisher's terms to be
    # recorded over the other's points with nothing noticing.
    (
        "one licence is assumed to cover every gazetteer, as it did before GeoNames",
        [("""    for gaz in sorted(gazetteers_in_use(by_doc)):""",
          """    for gaz in sorted(set()):""")],
    ),
    (
        "a legacy flat licence block is read as covering every gazetteer",
        [("""        data["licences"] = {"pleiades": legacy} if legacy else {}""",
          """        data["licences"] = {g: legacy for g in GAZETTEERS} if legacy else {}""")],
    ),
    (
        "a cache holding both licence shapes picks one silently",
        [('''    elif "licence" in data:''', """    elif False:""")],
    ),
    (
        # A GeoNames country file holds one country and this corpus spans four,
        # so every per-country refresh misses the others' ids. Reporting that
        # as UNRESOLVED told a curator with exactly the right file to go and
        # check they had the right file.
        "a country file that lacks another country's ids is reported as the "
        "curator having the wrong file",
        [("""    still_uncached = sorted(""",
          """    print("UNRESOLVED — check you have the right country file")
    still_uncached = sorted(""")],
    ),
    # --- A6, the date-overlap check ------------------------------------------
    #
    # An id can resolve, cache, carry a real coordinate and pass every guard
    # above while denoting a place attested nowhere near this project's era.
    # These four restore, in turn: the out-of-era failure, the hull/attestation
    # distinction the Ka'ba-ye Zartosht turns on, the refusal to guess a range
    # for a period the dump disagrees about, and the rule that an unanswerable
    # check says so rather than passing.
    (
        "an entry attested entirely outside 27 BC - AD 1204 is accepted",
        [("""    if not in_project_window(hull):""", """    if False:""")],
    ),
    (
        # The motivating case. Pleiades derives minDate/maxDate from the
        # attested periods, so for an entry attesting only Achaemenid and
        # modern the pair spans the 2,240-year gap between them. Trusting the
        # hull is precisely the defect: it reports in-scope and attests nothing.
        "the hull is trusted as an attestation, so a period-shaped hole reads "
        "as coverage",
        [("""    for key, span in known:
        if in_project_window((span["min"], span["max"])):
            return DATE_OK, None""",
          """    return DATE_OK, None""")],
    ),
    (
        "a period whose dump rows disagree is given a guessed range instead of "
        "none",
        [("""        if len(spans) == 1:""", """        if True:""")],
    ),
    (
        "a multi-period row is read as stating its first period's range",
        [("""            if len(keys) != 1:""", """            if len(keys) < 1:""")],
    ),
    (
        # The defect the first real run against the 2026-08-10 dump exposed.
        # A `hole` is the positive claim that NOTHING attested is in era; with
        # a period unaccounted for, that period could be the one in era. This
        # restores the version that claimed a hole as soon as no *known*
        # period matched — a finding about the gazetteer that was really a gap
        # in the derived vocabulary.
        "a hole is claimed while a period has no derived range, so a gap in "
        "the vocabulary reads as a finding about the gazetteer",
        [("""    if unknown:
        return DATE_UNKNOWN, (
            f"its hull {hull[0]:.0f}..{hull[1]:.0f} covers this project's \"""",
          """    if False:
        return DATE_UNKNOWN, (
            f"its hull {hull[0]:.0f}..{hull[1]:.0f} covers this project's \"""")],
    ),
    # --- A6, UNLOCATED vs no entry at all ------------------------------------
    #
    # Two states that looked identical until this block: a place no gazetteer
    # has heard of, and a gazetteer entry that records no coordinate. These
    # three restore, in turn: the requirement that the claim names an entry,
    # the third state an explicit `false` re-creates, and — the one that
    # matters — the check that the claim is TRUE of the cached entry rather
    # than merely asserted by the record.
    (
        "`unlocated` no longer needs the gazetteer id it is a claim about",
        [("""    if gazetteer_id is None:
        raise PlaceError(
            f"{where}: '{UNLOCATED_KEY}' without a gazetteer_id.""",
          """    if False:
        raise PlaceError(
            f"{where}: '{UNLOCATED_KEY}' without a gazetteer_id.""")],
    ),
    (
        "`unlocated: false` is accepted, re-creating the third state",
        [("""    if raw[UNLOCATED_KEY] is not True:""", """    if False:""")],
    ),
    (
        # The claim is only worth moving out of a free-text note if something
        # checks it. Trusting it would leave a stale `unlocated` drawing
        # nothing on a place the gazetteer has since located.
        "an `unlocated` claim is trusted instead of checked against the entry",
        [("""            if entry.has_point or entry.has_extent:""",
          """            if False:""")],
    ),
]

EXPECTED = [
    "stated placement without a gazetteer id is refused",
    "an unlisted gazetteer is refused",
    "a gazetteer with no id is refused",
    "identified without a ground_citation is refused",
    "an uncached id raises rather than returning None",
    "unknown key is a load-time error",
    "an empty string is refused rather than stored",
    "uri that disagrees with the gazetteer id is refused",
    "a contested identification with one citation is refused",
    "contested written as false is refused",
    "regional with no id and no note is refused",
    "a record cannot both declare places and declare it has none",
    "an empty no_places_reason is refused",
    "a hand-written coordinate in a seed record is refused",
    "a header with no geometry fails loudly",
    "an undated 'latest' dump is refused",
    # NOT the exit-code assertion: two licence rules run in sequence, so
    # disabling the first lets the second fail the run and the code never moves.
    # Over-determined exactly as the Aksum and floor cases were in
    # mutate_part8.py, and as there, the guard that pins it is what the failure
    # NAMES. Third occurrence of this shape in the repository.
    "the unconfirmed-licence failure names it as unconfirmed",
    "the licence terms alone are not enough — the publisher's declaration that "
    "they apply is a second claim",
    "--survey matches a bare numeric term against the id column, exactly as "
    "--find does",
    "a resolving id whose title marks it deprecated is refused, and the failure "
    "says so",
    "an entry resolving to neither point nor extent fails",
    "a subject place with no role is refused",
    "a role outside the closed vocabulary is refused",
    # Over-determined with "a role on origin_places is refused" — one rule
    # covers both blocks, so both guards fire. Pinned to the findspot one
    # because findspot_places is the block 17 of 24 records carry, and so the
    # one a stray role would actually appear in. Fourth occurrence of this
    # shape; see the licence note above.
    "a role on findspot_places is refused",
    "two foci in one block are refused",
    "directional roles with no focus are refused",
    "a regional placement whose bbox has no area is reported as unrenderable, "
    "and does not fail the check",
    # Over-determined with "the reader applies the shape check to the first
    # data row", which asserts the same guard end-to-end. Pinned to the pure
    # function, because removing the guard makes the end-to-end path CRASH
    # three lines later and this harness counts a crash as a MISS. Fifth
    # occurrence of the over-determination shape; see the licence note above.
    "a dump with the wrong field count is refused, naming the count",
    "a header row is refused — GeoNames dumps have none",
    "an undocumented feature class is refused",
    "an unzipped .txt is refused a guessed date, and says why",
    "a GeoNames placement is not covered by the Pleiades licence, and the "
    "failure names the gazetteer that is missing one",
    "the migrated licence covers Pleiades only — it does not become a licence "
    "for a gazetteer nobody recorded one for",
    "a cache holding BOTH licence shapes is refused rather than one being "
    "guessed as current",
    "and it does not tell the curator to check a file that is already correct",
    # A6. The first is pinned to the pure function rather than to cmd_check's
    # exit code: `date_audit` runs before the licence gate in the same loop, so
    # asserting on the exit code alone would be over-determined by whichever
    # failure the fixture happened to reach first. Sixth occurrence of this
    # shape in the repository; same answer as the licence and role cases above.
    "an entry attested only after the project's window is refused, and the "
    "failure names the range it actually has",
    "an entry whose hull spans the window but whose every attested period "
    "falls outside it is reported as a hole, NOT as a failure — the placement "
    "can be correct and the gazetteer merely narrow",
    "a key whose rows disagree is given NO range — a majority rule would make "
    "the check assert what the dump does not say",
    "every row is read; the multi-period one is not counted as stating a "
    "single period's range",
    "a period with NO derived range makes the verdict unknown, not a hole — "
    "the missing period could be the one in era",
    "unlocated without a gazetteer_id is refused",
    "unlocated written as false is refused",
    "an unlocated claim against an entry that HAS a location fails — the claim "
    "is checked against the gazetteer, not trusted",
]


def failures_from(output: str) -> set[str]:
    return {
        line.split("FAIL", 1)[1].strip()
        for line in output.splitlines()
        if line.strip().startswith("FAIL")
    }


def main() -> int:
    if len(MUTATIONS) != len(EXPECTED):
        print(f"{len(MUTATIONS)} mutations against {len(EXPECTED)} expectations")
        return 1

    originals = {f: f.read_text(encoding="utf-8") for f in SOURCES}
    problems: list[str] = []
    try:
        for (label, patches), guard in zip(MUTATIONS, EXPECTED):
            edited = {f: originals[f] for f in SOURCES}
            missing = [
                old for old, _ in patches
                if not any(old in originals[f] for f in SOURCES)
            ]
            if missing:
                problems.append(f"{label}: mutation target not found")
                print(f"  MISS {label} (target not found)")
                continue
            for old, new in patches:
                target = next(f for f in SOURCES if old in edited[f])
                edited[target] = edited[target].replace(old, new, 1)
            for f in SOURCES:
                f.write_text(edited[f], encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "ingest.test_places"],
                cwd=ROOT, capture_output=True, text=True,
            )
            failed = failures_from(result.stdout)
            if guard in failed:
                print(f"  ok   {label}")
                print(f"       -> {guard}")
            elif result.returncode != 0 and not failed:
                # A crash is not a guard firing. `test_embed.py` spent two days
                # crashing where it should have been asserting, and nothing said
                # so; the distinction is kept explicit here for that reason.
                problems.append(
                    f"{label}: the suite crashed rather than failing the guard"
                )
                print(f"  MISS {label} (crash, not a guard failure)")
            else:
                problems.append(
                    f"{label}: expected {guard!r} to fail, got "
                    f"{sorted(failed) or 'no failures'}"
                )
                print(f"  MISS {label}")
    finally:
        for f in SOURCES:
            f.write_text(originals[f], encoding="utf-8")

    # Two different failures, kept apart — the correction made to all three
    # existing mutation scripts on 2026-08-12, after "sources were not restored
    # cleanly" was printed over a perfect restore and hid a real finding through
    # an exit gate.
    unrestored = [
        f.name for f in SOURCES
        if f.read_text(encoding="utf-8") != originals[f]
    ]
    if unrestored:
        problems.append(
            "sources were NOT restored cleanly: " + ", ".join(unrestored)
            + " — restore from version control before running anything else"
        )

    check = subprocess.run(
        [sys.executable, "-m", "ingest.test_places"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if check.returncode != 0:
        problems.append(
            "sources restored, but `ingest.test_places` fails on its own "
            "account — a finding about the suite, not about this harness"
        )
        print("\n--- ingest.test_places output, so it is not lost ---")
        print((check.stdout or "") + (check.stderr or ""), end="")
        print("--- end ---")

    print()
    if problems:
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"all {len(MUTATIONS)} mutations verified; sources restored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
