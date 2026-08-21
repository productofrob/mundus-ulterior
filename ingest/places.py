"""Strict loader for the two place blocks a seed record may carry.

`findspot_places` — where the object was found.
`origin_places`   — where the object was made.
`subject_places`  — where the text is *about*.

`origin_places` was added 2026-08-13 for the Aksumite coin, minted at Aksum and
found in Yemen. A mint is not a findspot and a coin has no text, so neither
existing block could hold it without damaging its own definition. The general
case is not minting but **manufacture**, and it is everywhere in this corpus:
the Hoby cups were made in Italy, the Hwangnam glass is Roman, the Óc Eo
medallion is an Antoninus. **Origin to findspot is an object moving**, which is
the connection this whole project exists to show, so the block is named for the
general case rather than the instance that prompted it.

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

`role` was added 2026-08-13, at the start of A4 and before any `subject_places`
block existed, because A1 deliberately left the question open and A5 renders
trade texts as **edges between subject places** — and an edge needs to know one
end from the other. Deciding it at A1 would have been guessing; deciding it with
the seven literary records in front of us is a decision with evidence. See
`ROLES` below for the vocabulary and the two block-level rules that make an edge
derivable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from .loader import iter_seed_records

PLACE_BLOCKS = ("findspot_places", "origin_places", "subject_places")

# A record carries place blocks OR this, never both and (at G1) never neither.
#
# Without it, an absent block means two different things — "not curated yet" and
# "curated, and there is nothing to place" — and at A6 nobody can tell them
# apart. That is the third state this schema refuses everywhere else, arriving
# at the level above the entry. `persia-03-coin` is the case that forced it:
# its findspot is "Not recorded (acquired via Robertson sale, 1843)", which is
# not vague, it is absent, and no honest `regional` placement exists.
#
# It also makes G1 criterion 1 checkable. "24/24 records carry at least
# regional" is unreachable if two records have no geography; "24/24 records have
# been considered" is both reachable and the thing actually worth asserting.
NO_PLACES_KEY = "no_places_reason"

# How a subject place stands to the passage that names it. `subject_places`
# only; the other two blocks state their relation in the block name already,
# and a `role` there would be a second name for the same fact.
#
# The vocabulary is closed and it is what A5 derives edges from:
#
#     source --> focus --> destination
#
# `focus` is the place the passage centres on — the port whose imports and
# exports §28 lists, the polity the Weilüe describes. Every directional role is
# relative to it, which is why a block carrying one requires it.
#
# Named `focus` and not `anchor` on purpose. This corpus is largely sailing
# manuals; Periplus §4 discusses, in so many words, where ships anchor. A key
# whose value could be read as a claim about the text's own subject matter is
# the "two questions under one name" defect this repository has now paid for
# four times (`has_extent`/`has_area`, `translation_chunk`/`translation_chunk_id`,
# `--find`/`--survey`, and the field once called `pleiades_id`).
ROLES = {
    # The place the passage is organised around. At most one per block.
    "focus",
    # Goods, people or knowledge reach the focus FROM here.
    "source",
    # They leave the focus FOR here.
    "destination",
    # On the way, and named as such. Draws an edge; carries no ordering, which
    # is this vocabulary's known limit — see PLACES.md.
    "waypoint",
    # Named, and nothing moves. Draws no edge. This is not "we have not decided
    # yet"; it is the positive claim that the text merely names the place, which
    # is why there is no default and every entry must say which it is.
    "mentioned",
}

# Roles that assert a movement, and therefore require the other end of it.
DIRECTIONAL_ROLES = {"source", "destination", "waypoint"}

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
        "publisher": "Pleiades",
    },
    "geonames": {
        # The human-readable page, not the sws.geonames.org linked-data URI,
        # because PHASE2_PLAN A5 requires every point to click through to
        # something a reader can read.
        "uri_prefix": "https://www.geonames.org/",
        "uri_suffix": "",
        "scope": "modern places worldwide; used where no ancient gazetteer covers the site",
        "publisher": "GeoNames",
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
    # The gazetteer holds this place and does not record where it is. See
    # UNLOCATED_KEY below.
    "unlocated",
    # Required on subject_places, forbidden elsewhere — a conditional the key
    # set cannot express, so it is enforced in parse_place instead.
    "role",
}

_STRING_KEYS = (
    "name", "ground", "gazetteer", "gazetteer_id", "uri", "ground_citation", "note",
    "role",
)

SUBJECT_BLOCK = "subject_places"

# "The gazetteer holds this place and does not know where it is."
#
# A6, 2026-08-13. This is the third state again, one level down from
# `no_places_reason`, and it arrived the same way: by being written in prose
# because the schema had nowhere to put it. Pleiades 40186 Kyeneion, 906027
# Sabbatha and 60485/50630 Chryse all RESOLVE and carry no coordinate at all —
# the gazetteer records the place and not its location.
#
# Until now such a placement had to be written with **no id**, because
# `gazetteer --check` fails an entry resolving to neither point nor extent, so
# citing the id would have failed the build. The id therefore survived only in
# a free-text `note` — unreadable by any check, and at the data layer
# indistinguishable from Ariake, which no gazetteer has ever heard of. Two
# different states, one shape, exactly what `has_extent`/`has_area` and
# `no_places_reason` were each split to prevent.
#
# Written as `true` or omitted, on the same rule as `contested`: an explicit
# `false` would re-create the third state this key exists to remove. It
# requires an id, because "the gazetteer has it and cannot locate it" is a
# claim ABOUT an entry, and without the id there is no entry to make it about.
#
# It is a claim, so `--check` verifies it rather than trusting it: the cached
# entry must really carry neither point nor extent. A placement declaring
# `unlocated` against an entry that has a coordinate is a stale note, and the
# day Pleiades locates Kyeneion this fails instead of quietly drawing nothing.
UNLOCATED_KEY = "unlocated"


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
    # None on findspot_places and origin_places, where the block already says
    # the relation. Never None on subject_places.
    role: str | None
    # The gazetteer holds this place and records no location for it. See
    # UNLOCATED_KEY.
    unlocated: bool = False

    @property
    def key(self) -> str:
        return f"{self.doc_id}::{self.block}[{self.index}]"

    @property
    def draws_edge(self) -> bool:
        """Whether A5 should draw a line from this place to its block's focus.

        `mentioned` is the deliberate false: a text that names Laodicean wine
        is not a text about a route to Laodicea, and an edge there would make
        the network assert trade the passage does not describe.
        """
        return self.role in DIRECTIONAL_ROLES

    @property
    def locatable(self) -> bool:
        """True when this placement licenses a lookup in a gazetteer.

        False only for a `regional` placement carrying no id — the honest
        'we know the region and no more' case, which renders as nothing on
        the map rather than as a guessed point.

        An `unlocated` placement is still locatable in this sense and
        deliberately so: it cites an id, that id must resolve, and the entry
        behind it must be cached so the claim that the gazetteer cannot place
        it can be checked against the gazetteer. What it will not do is yield
        a coordinate — see `drawable`.
        """
        return self.gazetteer_id is not None

    @property
    def drawable(self) -> bool:
        """Whether a coordinate could ever come of this placement.

        Distinct from `locatable`, which asks whether there is an id to look
        up. The two were the same question until A6 and are not: an
        `unlocated` placement has an id, resolves, caches, and can never put
        anything on the map. Collapsing them is how "the gazetteer has never
        heard of this" and "the gazetteer has it and does not know where it
        is" came to look identical.
        """
        return self.gazetteer_id is not None and not self.unlocated

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


def _parse_unlocated(raw: dict[str, Any], gazetteer_id: str | None, where: str) -> bool:
    """`unlocated: true`, or the key is absent. See UNLOCATED_KEY."""
    if UNLOCATED_KEY not in raw:
        return False

    if raw[UNLOCATED_KEY] is not True:
        raise PlaceError(
            f"{where}: '{UNLOCATED_KEY}' may only be written as true. Absence "
            f"means the gazetteer locates this place normally; an explicit "
            f"false is a third state saying the same thing a second way."
        )
    if gazetteer_id is None:
        raise PlaceError(
            f"{where}: '{UNLOCATED_KEY}' without a gazetteer_id. The key is a "
            f"claim about a gazetteer entry — that it holds this place and "
            f"records no location for it — and with no id there is no entry "
            f"to make the claim about. A place no gazetteer has heard of is "
            f"'regional' with a note, which is a different state and the one "
            f"this key exists to be told apart from."
        )
    return True


def _parse_role(raw: dict[str, Any], block: str, where: str) -> str | None:
    """`role` is required on subject_places and refused on the other two blocks.

    Required, with no default, for the reason `expect_untranslatable` has no
    default in `eval/goldset.py`: `mentioned` is a **claim** — that the text
    names this place and describes nothing moving through it — and a claim may
    never arrive by omission. Defaulting to `mentioned` would let an
    uncurated entry silently assert the weakest reading, and defaulting to
    anything else would let it silently assert an edge.
    """
    role = raw.get("role")
    role = role.strip() if role else None

    if block != SUBJECT_BLOCK:
        if role is not None:
            raise PlaceError(
                f"{where}: 'role' belongs to {SUBJECT_BLOCK} only. "
                f"'{block}' already names the relation, and a role here would "
                f"be a second name for the same fact — free to disagree with "
                f"the first, and nothing would notice which the map used."
            )
        return None

    if role is None:
        raise PlaceError(
            f"{where}: {SUBJECT_BLOCK} requires a 'role', one of {sorted(ROLES)}. "
            f"There is no default: 'mentioned' is the positive claim that the "
            f"text merely names the place, and a directional role asserts that "
            f"something moved. Neither may arrive by omission."
        )
    if role not in ROLES:
        raise PlaceError(
            f"{where}: role '{role}' is not one of {sorted(ROLES)}. The "
            f"vocabulary is closed because A5 derives edges from it; a role it "
            f"cannot read would drop a place off the network without failing."
        )
    return role


def _check_block_roles(places: list[Place], doc_id: str, block: str) -> None:
    """The two rules that make an edge derivable, checked across the block.

    Neither can be seen from a single entry, which is why they are not in
    `parse_place`: both are statements about how the entries stand together.
    """
    if block != SUBJECT_BLOCK:
        return
    in_block = [p for p in places if p.block == block]

    foci = [p for p in in_block if p.role == "focus"]
    if len(foci) > 1:
        raise PlaceError(
            f"{doc_id}::{block}: {len(foci)} places carry role 'focus' "
            f"({', '.join(p.name for p in foci)}). A5 derives every edge as "
            f"source -> focus -> destination, so two foci make each edge "
            f"ambiguous about which end it has. If the passage genuinely turns "
            f"on two places, one of them is a source, a destination or a "
            f"waypoint of the other."
        )

    directional = [p for p in in_block if p.draws_edge]
    if directional and not foci:
        raise PlaceError(
            f"{doc_id}::{block}: {len(directional)} place(s) carry a "
            f"directional role ({', '.join(sorted(p.role for p in directional))}) "
            f"but no place carries 'focus'. A directional role is relative — a "
            f"source of goods reaching somewhere, a destination they leave for "
            f"— so without a focus it names one end of an edge and no other. "
            f"Either mark the place the passage centres on, or the roles are "
            f"'mentioned'."
        )


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
    role = _parse_role(raw, block, where)
    unlocated = _parse_unlocated(raw, gazetteer_id, where)

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
        role=role,
        unlocated=unlocated,
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


def read_no_places_reason(record: dict[str, Any], doc_id: str | None = None) -> str | None:
    """The record's declaration that it has been considered and cannot be placed."""
    doc_id = doc_id or record.get("id") or "<unknown>"
    if NO_PLACES_KEY not in record:
        return None
    reason = record[NO_PLACES_KEY]
    if not isinstance(reason, str) or not reason.strip():
        raise PlaceError(
            f"{doc_id}: '{NO_PLACES_KEY}' must be a non-empty string saying what "
            f"was looked for and why nothing could be placed."
        )
    present = [b for b in PLACE_BLOCKS if b in record]
    if present:
        raise PlaceError(
            f"{doc_id}: '{NO_PLACES_KEY}' alongside {present}. A record either "
            f"has places or has a reason it has none. Both is a record that "
            f"contradicts itself, and the reader cannot tell which is current."
        )
    return reason.strip()


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

        _check_block_roles(places, doc_id, block)

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
    for path in iter_seed_records(corpus_dir):
        record = json.loads(path.read_text(encoding="utf-8"))
        assert_no_authored_coordinates(record)
        read_no_places_reason(record)   # raises if it contradicts the blocks
        out[record["id"]] = parse_record_places(record)
    return out


def iter_places(by_doc: dict[str, list[Place]]) -> Iterator[Place]:
    for places in by_doc.values():
        yield from places
