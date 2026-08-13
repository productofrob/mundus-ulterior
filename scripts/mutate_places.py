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
        [("""    if not licence.get("text") or licence["text"] == LICENCE_UNCONFIRMED:""",
          """    if False:""")],
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
