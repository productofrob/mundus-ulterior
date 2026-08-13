"""Strict loader for the two place blocks a seed record may carry.

`findspot_places` — where the object was found.
`subject_places`  — where the text is *about*.

They are strongest in opposite records: findspots exist for the 17 object
records, subject geography for the 7 literary ones. A findspot map of 24 objects
is a dot map; a subject-place map is a network, and the network is the
ORBIS-shaped thing.

Validation is strict on purpose, and in three specific ways.

**Unknown keys are a load-time error.** Same argument as `eval/goldset.py`: write
`ground_cite` where the field is `ground_citation` and the requirement silently
disappears, leaving a placement that asserts a scholarly identification with no
scholar attached. A typo must be loud at load, not weaker at run time.

**Nothing is inherited from a default.** `PROGRESS.md` established this for
`expect_untranslatable`: a claim about the material may never arrive by omission.
The same holds here. `ground` says how a placement was arrived at and it is
always required; `ground_citation` is required exactly when `ground` is
`identified`, because that ground *is* the claim that a named scholar made an
identification. There is no default that could be honest.

**An empty value is not a value.** `""` and `[]` are load-time errors, not
"unspecified". The Palmyrene Tariff's `reference_translation` — empty rather than
null, a third state reading "a translation exists, and it is nothing" — is the
standing example in this repository of what one empty string costs later. A key
is written with content or it is omitted.

The same rule governs `contested`, which may appear **only** as `true`. Absent
means not contested. Permitting an explicit `false` would create exactly the
third state this module exists to refuse.

Coordinates appear nowhere in this module. A placement carries a `gazetteer`
and a `gazetteer_id`; `ingest/gazetteer.py` turns ids into points, and nothing
else may.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

PLACE_BLOCKS = ("findspot_places", "subject_places")

GROUNDS = {
    # The record's own text names the place.
    "stated",
    # A scholar identifies the ancient place with a modern location
    # (Adulis ~ Zula). Requires the citation that makes the identification.
    "identified",
    # Only the region is known. The map is sparser, and that is correct.
    "regional",
}

# Two gazetteers, because one is not enough and the reason is the project's own
# premise. Pleiades is a Greco-Roman gazetteer; this corpus was deliberately
# built outside the Roman world. The 2026-08-12 survey found no Pleiades entry
# for Gyeongju, Óc Eo, Khao Sam Kaeo or Jabal Ḏabūb — roughly half the findspot
# records — which is the premise of Mundus Ulterior showing up in its own gate.
#
# The field was `pleiades_id` until the survey. A field name that hard-codes one
# source is the `translation_chunk_id` trap — a name that will be wrong for half
# its values — and it was renamed while exactly ONE record carried a placement.
GAZETTEERS: dict[str, dict[str, str]] = {
    "pleiades": {
        "uri_prefix": "https://pleiades.stoa.org/places/",
        "uri_suffix": "",
        "scope": "Greco-Roman world; ancient places",
    },
    "geonames": {
        # The human-readable page, not the sws.geonames.org linked-data URI,
        # because PHASE2_PLAN A5 requires every point to click through to
        # something a reader can read.
        "uri_prefix": "https://www.geonames.org/",
        "uri_suffix": "",
        "scope": "modern places worldwide; used where no ancient gazetteer covers the site",
    },
}

_REQUIRED = {"name", "ground"}
_OPTIONAL = {
    "gazetteer",
    "gazetteer_id",
    "uri",
    "ground_citation",
    "contested",
    "contested_citations",
    "note",
}

_STRING_KEYS = (
    "name", "ground", "gazetteer", "gazetteer_id", "uri", "ground_citation", "note",
)


class PlaceError(ValueError):
    """Raised at load time. Never downgraded to a warning.

    A placement that cannot be validated is a placement that would put an
    unsourced point on a map, and the whole of W1 is the claim that no such
    point exists.
    """


@dataclass(frozen=True)
class Place:
    doc_id: str
    block: str
    index: int
    name: str
    ground: str
    gazetteer: str | None
    gazetteer_id: str | None
    uri: str | None
    ground_citation: str | None
    contested: bool
    contested_citations: tuple[str, ...]
    note: str | None

    @property
    def key(self) -> str:
        return f"{self.doc_id}::{self.block}[{self.index}]"

    @property
    def locatable(self) -> bool:
        """True when this placement licenses a lookup in a gazetteer.

        False only for a `regional` placement carrying no id — the honest
        'we know the region and no more' case, which renders as nothing on
        the map rather than as a guessed point.
        """
        return self.gazetteer_id is not None

    @property
    def cache_key(self) -> str | None:
        """How the gazetteer cache addresses this place.

        Namespaced by gazetteer, because ids collide: GeoNames 98983 and
        Pleiades 98983 are different places, and a cache keyed on the bare
        number would serve one for the other with no error anywhere.
        """
        if self.gazetteer is None or self.gazetteer_id is None:
            return None
        return f"{self.gazetteer}:{self.gazetteer_id}"


def canonical_uri(gazetteer: str, gazetteer_id: str) -> str:
    spec = GAZETTEERS.get(gazetteer)
    if spec is None:
        raise PlaceError(
            f"unknown gazetteer '{gazetteer}'; known: {sorted(GAZETTEERS)}"
        )
    return f"{spec['uri_prefix']}{gazetteer_id}{spec['uri_suffix']}"


def _reject_empty(raw: dict[str, Any], where: str) -> None:
    for key in _STRING_KEYS:
        if key not in raw:
            continue
        value = raw[key]
        if not isinstance(value, str):
            raise PlaceError(f"{where}: '{key}' must be a string, got {type(value).__name__}")
        if not value.strip():
            raise PlaceError(
                f"{where}: '{key}' is empty. Omit the key instead. An empty "
                f"string is a third state that reads as 'a value exists, and it "
                f"is nothing' — the defect already logged against "
                f"arabia-02-palmyrene-tariff's reference_translation."
            )


def _check_keys(raw: dict[str, Any], where: str) -> None:
    keys = set(raw)
    missing = _REQUIRED - keys
    if missing:
        raise PlaceError(f"{where}: missing required key(s): {sorted(missing)}")
    unknown = keys - _REQUIRED - _OPTIONAL
    if unknown:
        raise PlaceError(
            f"{where}: unknown key(s) {sorted(unknown)}. Known keys are "
            f"{sorted(_REQUIRED | _OPTIONAL)}. A misspelled key would otherwise "
            f"be ignored, dropping a requirement without failing anything."
        )


def _parse_contested(raw: dict[str, Any], ground: str, where: str) -> tuple[bool, tuple[str, ...]]:
    has_flag = "contested" in raw
    has_cites = "contested_citations" in raw

    if not has_flag:
        if has_cites:
            raise PlaceError(
                f"{where}: 'contested_citations' without 'contested': true. "
                f"Citations for an argument nobody has said is contested."
            )
        return False, ()

    if raw["contested"] is not True:
        raise PlaceError(
            f"{where}: 'contested' may only be written as true. Absence means "
            f"not contested; an explicit false is a third state saying the same "
            f"thing a second way."
        )

    if ground != "identified":
        raise PlaceError(
            f"{where}: contested is only meaningful on ground 'identified', not "
            f"'{ground}'. What is contested is the identification of an ancient "
            f"place with a modern location, not the fact that a text names it."
        )

    cites = raw.get("contested_citations")
    if not isinstance(cites, list) or not all(isinstance(c, str) and c.strip() for c in cites):
        raise PlaceError(
            f"{where}: 'contested_citations' must be a list of non-empty strings."
        )
    if len(cites) < 2:
        raise PlaceError(
            f"{where}: a contested identification needs at least two citations, "
            f"got {len(cites)}. One citation is a position; the requirement is "
            f"that both sides of the argument are on the record, so the UI can "
            f"render 'probably here, and here is the argument' rather than a pin."
        )
    return True, tuple(c.strip() for c in cites)


def parse_place(raw: Any, doc_id: str, block: str, index: int) -> Place:
    where = f"{doc_id}::{block}[{index}]"
    if not isinstance(raw, dict):
        raise PlaceError(f"{where}: expected an object, got {type(raw).__name__}")

    _check_keys(raw, where)
    _reject_empty(raw, where)

    ground = raw["ground"].strip()
    if ground not in GROUNDS:
        raise PlaceError(
            f"{where}: ground '{ground}' is not one of {sorted(GROUNDS)}."
        )

    gazetteer = raw.get("gazetteer")
    gazetteer = gazetteer.strip() if gazetteer else None
    gazetteer_id = raw.get("gazetteer_id")
    gazetteer_id = gazetteer_id.strip() if gazetteer_id else None

    if (gazetteer is None) != (gazetteer_id is None):
        raise PlaceError(
            f"{where}: 'gazetteer' and 'gazetteer_id' are written together or "
            f"not at all. An id with no source names nothing; a source with no "
            f"id identifies nothing."
        )
    if gazetteer is not None and gazetteer not in GAZETTEERS:
        raise PlaceError(
            f"{where}: gazetteer '{gazetteer}' is not one of "
            f"{sorted(GAZETTEERS)}. Adding one is a decision about sourcing and "
            f"licensing, not a spelling."
        )
    if gazetteer_id is not None and not gazetteer_id.isdigit():
        raise PlaceError(
            f"{where}: gazetteer_id '{gazetteer_id}' is not a bare numeric id. "
            f"Write the id, not the URL."
        )

    # A `stated` or `identified` placement asserts a specific place, and a
    # specific place is a point on the map. It must resolve to a gazetteer id
    # or the point would be authored, which G1 criterion 2 forbids outright.
    if gazetteer_id is None and ground != "regional":
        raise PlaceError(
            f"{where}: ground '{ground}' names a specific place and so requires "
            f"a gazetteer and gazetteer_id. If no id can be found in any "
            f"gazetteer, the honest ground is 'regional'."
        )

    uri = raw.get("uri")
    uri = uri.strip() if uri else None
    if gazetteer_id is None and uri is not None:
        raise PlaceError(f"{where}: 'uri' without a 'gazetteer_id'.")
    if gazetteer_id is not None:
        expected = canonical_uri(gazetteer, gazetteer_id)  # type: ignore[arg-type]
        if uri is None:
            raise PlaceError(f"{where}: gazetteer_id without its 'uri' ({expected}).")
        if uri != expected:
            # Two fields, one fact. If they can disagree they eventually will,
            # and the reader has no way to know which one the map used.
            raise PlaceError(
                f"{where}: uri '{uri}' does not match {gazetteer} id "
                f"'{gazetteer_id}' (expected '{expected}')."
            )

    ground_citation = raw.get("ground_citation")
    ground_citation = ground_citation.strip() if ground_citation else None
    if ground == "identified" and ground_citation is None:
        raise PlaceError(
            f"{where}: ground 'identified' requires a ground_citation. The "
            f"ground is the claim that a scholar identified this ancient place "
            f"with a modern location; without the citation it is an assertion "
            f"wearing the word 'identified'."
        )

    note = raw.get("note")
    note = note.strip() if note else None

    # The sparse case has to say why it is sparse, or 24/24 'at least regional'
    # is satisfied by a field that asserts nothing.
    if ground == "regional" and gazetteer_id is None and note is None:
        raise PlaceError(
            f"{where}: a regional placement with no gazetteer_id must carry a "
            f"note saying what is known and why no place could be resolved."
        )

    contested, contested_citations = _parse_contested(raw, ground, where)

    return Place(
        doc_id=doc_id,
        block=block,
        index=index,
        name=raw["name"].strip(),
        ground=ground,
        gazetteer=gazetteer,
        gazetteer_id=gazetteer_id,
        uri=uri,
        ground_citation=ground_citation,
        contested=contested,
        contested_citations=contested_citations,
        note=note,
    )


# G1 criterion 2 is "zero coordinates in the bundle that do not derive from a
# gazetteer id". The cheapest way for one to appear is for a curator — or a model
# helping a curator — to add a lat/lon pair to a seed record because it was to
# hand. The place blocks already refuse unknown keys; this closes the rest of the
# record.
#
# The list is EXACT key names, not a substring rule. A substring rule for "lat"
# would fire on `translation_source`, and *a check that matches too broadly names
# the wrong cause* has cost this project an afternoon once already.
FORBIDDEN_COORDINATE_KEYS = {
    "lat", "latitude", "lon", "long", "longitude", "lng",
    "coord", "coords", "coordinate", "coordinates",
    "geometry", "geojson", "wkt", "point", "bbox", "extent",
    "repr_lat", "reprlat", "repr_long", "reprlong", "x", "y",
}


def assert_no_authored_coordinates(record: dict[str, Any], doc_id: str | None = None) -> None:
    """A seed record may name a place. It may never state where the place is."""
    doc_id = doc_id or record.get("id") or "<unknown>"
    offending = sorted(k for k in record if k.lower() in FORBIDDEN_COORDINATE_KEYS)
    if offending:
        raise PlaceError(
            f"{doc_id}: seed record carries coordinate key(s) {offending}. "
            f"Coordinates are never authored — a record carries a gazetteer id "
            f"and ingest/gazetteer.py supplies the point from a dated snapshot. "
            f"A hand-written coordinate is the one thing G1 asserts cannot exist."
        )


def parse_record_places(record: dict[str, Any], doc_id: str | None = None) -> list[Place]:
    """Both place blocks of one seed record, validated.

    A record with neither block returns []. That is the pre-W1 state of every
    record in the corpus and is not an error here — it is `ingest/verify.py`
    that counts placed records against the G1 threshold.
    """
    doc_id = doc_id or record.get("id") or "<unknown>"
    places: list[Place] = []

    for block in PLACE_BLOCKS:
        if block not in record:
            continue
        raw_block = record[block]
        if not isinstance(raw_block, list):
            raise PlaceError(
                f"{doc_id}::{block}: expected a list, got {type(raw_block).__name__}"
            )
        if not raw_block:
            raise PlaceError(
                f"{doc_id}::{block}: present but empty. Omit the key rather "
                f"than write an empty list — the same third state an empty "
                f"string creates."
            )
        for index, raw in enumerate(raw_block):
            places.append(parse_place(raw, doc_id, block, index))

        keys = [p.cache_key for p in places if p.block == block and p.cache_key]
        dupes = sorted({k for k in keys if keys.count(k) > 1})
        if dupes:
            raise PlaceError(
                f"{doc_id}::{block}: gazetteer id repeated within one block: "
                f"{dupes}. One place, one entry."
            )

    return places


def load_places(corpus_dir: Path) -> dict[str, list[Place]]:
    """Every placement in the corpus, keyed by doc_id. Raises on the first bad one."""
    out: dict[str, list[Place]] = {}
    for path in sorted(corpus_dir.glob("*/*.json")):
        if path.name == "manifest.json":
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        assert_no_authored_coordinates(record)
        out[record["id"]] = parse_record_places(record)
    return out


def iter_places(by_doc: dict[str, list[Place]]) -> Iterator[Place]:
    for places in by_doc.values():
        yield from places
