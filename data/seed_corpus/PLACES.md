# Place fields — the spec 24 records are edited against

Phase 2, Block A (W1 Geography). Approved 2026-08-12 before any record was
edited, because a shape agreed after the fact is a shape the records have
already bent.

Enforced by `ingest/places.py`. Every rule below is a load-time error, not a
warning: a placement that cannot be validated is a placement that would put an
unsourced point on a map, and W1 is the claim that no such point exists.

---

## The two blocks

Both are optional, both are lists, and a record may carry either, both or
neither.

| block | means |
| --- | --- |
| `findspot_places` | where the object was **found** |
| `origin_places` | where the object was **made** |
| `subject_places` | where the text is **about** |

`origin_places` was added 2026-08-13 for the Aksumite coin — minted at Aksum,
found in Yemen. A mint is not a findspot, and a coin has no text, so neither
other block could hold it without damaging its own definition. The general case
is manufacture, not minting, and it recurs across this corpus: the Hoby cups
were made in Italy, the Hwangnam glass is Roman, the Óc Eo medallion is an
Antoninus. **Origin to findspot is an object moving** — the connection the
project exists to show, and the edge A5 should draw.

They are strongest in opposite records. Findspots exist for the 17 object
records; subject geography for the 7 literary ones. A findspot map of 24 objects
is a dot map; a subject-place map is a network, and the network is the
ORBIS-shaped thing.

**A block that is present must be non-empty.** Omit the key rather than write
`[]`.

## A record with no geography at all

A record carries place blocks **or** a record-level `no_places_reason`, never
both and — at G1 — never neither.

```json
"no_places_reason": "Considered 2026-08-13 and no placement is possible. The findspot is 'Not recorded (acquired via Robertson sale, 1843)' — absent rather than vague …"
```

Without it, an absent block means two different things: *not curated yet* and
*curated, and there is nothing to place*. At A6 nobody could tell them apart —
the same third state this schema refuses at every other level.

It also makes G1 criterion 1 checkable. "24/24 records carry at least
`regional`" is **unreachable** when a record's findspot is genuinely unrecorded;
"24/24 records have been considered" is both reachable and the thing worth
asserting. `verify` reports `N placed + M declared unplaceable = N+M/24
considered`.

---

## One entry

```json
{
  "name": "Adulis",
  "ground": "identified",
  "gazetteer": "pleiades",
  "gazetteer_id": "39271",
  "uri": "https://pleiades.stoa.org/places/39271",
  "ground_citation": "…the scholarly identification that makes the claim…",
  "role": "focus",
  "note": "…"
}
```

> `role` appears on `subject_places` entries only, and is required there. See
> the `role` section below.

> The id above is **real**: Pleiades 39271, title "Adouli", 15.262/39.659.
> `PHASE2_PLAN.md`'s draft of this example carried `39274195`, which is not
> Adulis and was written from memory in the section that forbids exactly that.
> Do not copy an id out of a worked example without resolving it.

Keys not listed here are a **load-time error**. Write `ground_cite` for
`ground_citation` and the requirement would silently disappear, leaving a
placement that asserts a scholarly identification with no scholar attached. Same
argument as `eval/goldset.py`'s unknown-key check, which exists because a typo
once turned a passage assertion into a document-id assertion and the probe
passed for the wrong reason.

| key | required | notes |
| --- | --- | --- |
| `name` | always | the place as this record refers to it |
| `ground` | always | one of `stated`, `identified`, `regional` |
| `gazetteer` | with `gazetteer_id`, or neither | `pleiades` or `geonames` |
| `gazetteer_id` | unless `ground` is `regional` | bare numeric id, not a URL |
| `uri` | whenever `gazetteer_id` is present | the canonical form for that gazetteer |
| `ground_citation` | when `ground` is `identified` | the citation that makes the identification |
| `contested` | never, except as `true` | see below |
| `contested_citations` | when `contested` | **two or more** |
| `role` | **always on `subject_places`**, never elsewhere | see below |
| `unlocated` | never, except as `true` | the gazetteer holds this place and records no coordinate. Requires `gazetteer_id`. See below |
| `note` | when `regional` with no id | otherwise optional, and by standing decision of 2026-08-12 every placement records how its id was confirmed |

---

## `unlocated` — the gazetteer has the place and not its location

Added **2026-08-13** (A6). Three states, not two, and the middle one had
nowhere to live:

| state | how it is written |
| --- | --- |
| the gazetteer locates this place | `gazetteer_id` + `uri` |
| **the gazetteer holds it and records no coordinate** | `gazetteer_id` + `uri` + `unlocated: true` |
| no gazetteer has heard of this place | `ground: "regional"`, no id, with a `note` |

Pleiades 40186 Kyeneion, 906027 Sabbatha and 60485/50630 Chryse all **resolve**
and carry no coordinate at all. Until this key existed such a placement had to
be written with *no id*, because `--check` fails an entry with neither point
nor extent and citing the id would have failed the build. The id therefore
survived only in a free-text `note` — where no check can read it, and where
Kyeneion looked exactly like Ariake, a place no gazetteer has ever heard of.

Rules, and each is mutation-verified:

- **`true` or omitted.** An explicit `false` re-creates the third state the key
  exists to remove — the same rule as `contested`.
- **Requires a `gazetteer_id`.** The key is a claim *about an entry*; with no
  id there is no entry to make it about.
- **The claim is checked, not trusted.** `--check` requires the cached entry to
  really carry neither point nor extent. The day Pleiades locates Kyeneion, a
  stale `unlocated` fails loudly rather than quietly drawing nothing.

An unlocated placement is `locatable` (its id must resolve and cache) and never
`drawable`. Those are two questions, and this key is why they now have two
names.

**Use it only when one id is settled.** Chryse has two unlocated candidates and
deliberately does not use the key: recording either would settle by keystroke a
question nobody has settled by argument.

---

## `role` — how a subject place stands to the passage

Decided **2026-08-13**, at the start of A4 and before a single `subject_places`
block existed. A1 left it open on purpose: A5 renders trade texts as *edges
between subject places*, an edge needs to know one end from the other, and a
vocabulary written at A1 would have been a guess. Written with the seven
literary records in front of us it is a decision with evidence.

| `role` | means | edge? |
| --- | --- | --- |
| `focus` | the place the passage is organised around | endpoint |
| `source` | goods, people or knowledge reach the focus **from** here | yes |
| `destination` | they leave the focus **for** here | yes |
| `waypoint` | on the way, and named as such | yes |
| `mentioned` | named, and nothing moves | **no** |

A5 derives every edge as **`source → focus → destination`**.

**`role` is required on every `subject_places` entry and forbidden on the other
two blocks.** Forbidden there because `findspot_places` and `origin_places`
already name their relation, and a role beside them would be a second name for
one fact — free to disagree with the first, with nothing to say which the map
used. Required here, with no default, for the reason `expect_untranslatable`
has no default: `mentioned` is a **claim** — that the text names this place and
describes nothing moving through it — and a claim may never arrive by omission.
A default of `mentioned` would let a half-edited record quietly drop edges.

Two rules hold across the block rather than within one entry:

- **At most one `focus`.** Two, and `source → focus` does not say which focus.
  If a passage genuinely turns on two places, one of them is a source, a
  destination or a waypoint of the other.
- **A directional role requires a `focus`.** Without one it names one end of an
  edge and no other. A block of nothing but `mentioned` needs no focus and must
  not be made to invent one.

### Named `focus`, not `anchor`

This corpus is largely sailing manuals, and Periplus §4 discusses in so many
words where ships anchor. `"role": "anchor"` would have been readable as a claim
about the passage's own subject matter — the *two questions under one name*
defect this repository has now paid for four times (`has_extent` vs `has_area`,
`translation_chunk` vs `translation_chunk_id`, `--find` vs `--survey`, and the
field once called `pleiades_id`).

### The known limit: no ordering

Roles are relations to the focus, so a multi-leg route flattens. The Muziris
papyrus runs Muziris → Berenike → Coptos → Alexandria; that records as one
focus, one destination and two waypoints, and **the order of the two waypoints
is not recoverable**. Accepted deliberately: the alternative was a separate
`subject_routes` block with explicit `{from, to, what_moved}` relations, which is
more expressive and is the right answer if ordering ever has to be drawn. The
papyrus is the record that will show whether this is a real loss — read it first
if the question is reopened.

### Every named place is placed

The Periplus names far more places than it is *about*. §4-6 alone names
Ptolemais, Adulis, Mountain Island, Diodorus, Coloe, the Auxumites, the Nile,
Cyeneum, the Alalaei, Egypt, Arsinoe, Diospolis, Laodicea and Italy. **All of
them are placed, each carrying its role**, rather than the trade-bearing ones
only.

`mentioned` is what makes this affordable: the weak ones are on the record, so
the entry is a complete index of the passage's geography and no omission is
invisible. The same argument as `no_places_reason` and as the three recorded
id rejections — "we considered this and decided against it" is worth nothing if
it is not written down.

Placement rules do not loosen for a `mentioned` place. It is still a place: a
`stated` or `identified` ground still needs a gazetteer id, and where none
resolves the honest ground is still `regional` with a note.

---

## `ground` — how the placement was arrived at

The UI **shows** this. A `regional` placement must not look like a `stated` one.

| situation | `ground` |
| --- | --- |
| the record's own text names the place | `stated` |
| a scholar identifies ancient with modern (Adulis ≈ Zula) | `identified` + `ground_citation` |
| only the region is known | `regional` |
| Muziris ≈ Pattanam | `identified` + `contested: true` + both sides |

`stated` and `identified` both name a specific place, and a specific place is a
point on the map — so both **require** a `gazetteer` and `gazetteer_id`. If no
id can be found in any listed gazetteer, the honest ground is `regional`. That is not a workaround; it is the
answer, and the map is sparser for it, which is correct.

---

## `regional`, and the decision left open per record

A `regional` placement takes one of two forms, chosen record by record
(decision taken 2026-08-12):

**With an id** — Pleiades holds region-scale places carrying an extent. Name
one, and the UI draws its extent, never a pin. Note that a Pleiades *point*
place carries a **degenerate** bbox (min equal to max), which is not an extent;
`gazetteer.py` distinguishes `has_extent` from `has_area` for this reason.

```json
{ "name": "Limyrike", "ground": "regional", "gazetteer": "pleiades",
  "gazetteer_id": "…", "uri": "…" }
```

**Without an id** — nothing resolves, nothing is drawn, and the entry must
carry a `note` saying what is known and why no place could be resolved.

```json
{ "name": "somewhere on the Malabar coast", "ground": "regional",
  "note": "The record fixes the region and no more; no Pleiades feature covers it." }
```

The `note` is required in the second form so that "24/24 records carry at least
`regional`" is not satisfied by a field asserting nothing.

---

## Contested identifications

`contested` may appear **only** as `true`. Absent means not contested. An
explicit `false` would be a third state saying the same thing a second way —
and this repository already carries the cost of one third state
(`arabia-02-palmyrene-tariff`'s `reference_translation`, empty rather than null,
reading as "a translation exists, and it is nothing").

Two further rules:

- `contested` is only meaningful on `ground: "identified"`. What is contested is
  the identification of an ancient place with a modern location, not the fact
  that a text names it.
- **Two citations minimum.** One citation is a position. The requirement is that
  both sides are on the record, so the UI can render *"probably here, and here is
  the argument"* rather than flattening it to a pin.

---

## Empty is not a value

`""` and `[]` are load-time errors. A key is written with content or it is
omitted. The plan's draft shape carried `"note": ""` and `"contested": false`;
both are gone for this reason.

---

## Coordinates

There are none in this file, and none in any seed record. A placement carries a
`gazetteer` and a `gazetteer_id`; `ingest/gazetteer.py` is the only thing in the
repository that turns an id into a point, and it reads a dated, cached snapshot.

## Two gazetteers

| `gazetteer` | covers | licence |
| --- | --- | --- |
| `pleiades` | the Greco-Roman world; ancient places | CC BY 3.0 US |
| `geonames` | modern places worldwide, where no ancient gazetteer reaches | CC BY 4.0 |

`geonames` exists because the 2026-08-12 survey found **no Pleiades entry** for
Gyeongju, Óc Eo, Khao Sam Kaeo or Jabal Ḏabūb — roughly half the findspot
records. Pleiades is a Greco-Roman gazetteer and this corpus was deliberately
built outside the Roman world, so the shortfall is the project's premise
appearing in its own gate.

A GeoNames placement is a **modern** administrative place, so it will usually be
`identified` rather than `stated`, and the note should say what the coordinate
actually denotes — a district centroid is not an excavation trench.

Search the snapshot before concluding a place is absent:

```powershell
python -m ingest.gazetteer --find "<name>" --dump <dump> --names-dump <names>
python -m ingest.gazetteer --survey data/place_survey.txt --dump <dump>
```

### Using GeoNames

Download the **country file** for the site from
<https://download.geonames.org/export/dump/> — `KR.zip`, `VN.zip`, `TH.zip`,
`YE.zip`. Pass the `.zip` as downloaded; it is read directly, and the zip's
internal timestamp becomes the snapshot date. Unzipping first loses that date,
and an undated snapshot cannot say what it is comparable with — so a bare
`.txt` is refused unless you state `--geonames-date` yourself.

```powershell
$kr = "$env:USERPROFILE\Downloads\KR.zip"
python -m ingest.gazetteer --geonames-dump $kr --geonames-find "Gyeongju"
# paste the id into the record, then:
python -m ingest.gazetteer --geonames-dump $kr --refresh-geonames
python -m ingest.gazetteer --check
```

`--geonames-find` searches the name, the ASCII name, the alternate names and
the id, and ranks an exact name match above an incidental substring of a
10,000-character alternate-names field. It reports; it never caches and never
chooses.

**Read the feature code before accepting an id.** `P.PPL` is a populated place,
`A.ADM2` a second-level administrative division, `T.MT` a mountain, `S.*` a
spot or building. Gyeongju exists as both `P.PPLA2` (the city) and `A.ADM2`
(the municipality) at slightly different coordinates; they are different claims
and the note must say which one the placement means.

**Two things are true of every GeoNames entry and of no Pleiades entry:**

- **It has no bbox.** GeoNames publishes points, so `has_area` is always false
  and a `regional` GeoNames placement can never draw an extent. If a region is
  what you mean, either accept that it draws nothing or find an ancient
  gazetteer entry that carries a real extent.
- **It is a modern place, and states no attestation range.** `min_date` and
  `max_date` are null rather than borrowed from the record's edit date. This is
  why a GeoNames placement is usually `identified` rather than `stated`, and
  why the note must say **what the coordinate actually denotes** — a commune
  centroid is not an excavation trench, and a municipality is not a tomb.

Licences are recorded **per gazetteer**: Pleiades is CC BY 3.0 US and GeoNames
is CC BY 4.0. `--check` demands a recorded licence and a publisher declaration
for every gazetteer the corpus actually cites, and starts demanding one the
moment the first placement cites a new source.

```powershell
python -m ingest.gazetteer --record-licence <file> --licence-for geonames `
    --licence-source-url https://creativecommons.org/licenses/by/4.0/
```

Title search alone is unreliable: Pleiades titles Adulis **"Adouli"**, and three
separate searches on the corpus's own vocabulary missed it.

**No id is written from memory** — not by the curator, not by a model. A
remembered id is an authored coordinate wearing a citation.

To check the corpus after editing a record:

```powershell
python -m ingest.verify
python -m ingest.gazetteer --check
```
