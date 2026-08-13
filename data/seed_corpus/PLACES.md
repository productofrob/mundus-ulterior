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
| `findspot_places` | where the object was found |
| `subject_places` | where the text is *about* |

They are strongest in opposite records. Findspots exist for the 17 object
records; subject geography for the 7 literary ones. A findspot map of 24 objects
is a dot map; a subject-place map is a network, and the network is the
ORBIS-shaped thing.

**A block that is present must be non-empty.** Omit the key rather than write
`[]`.

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
  "note": "…"
}
```

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
| `note` | when `regional` with no id | otherwise optional, and by standing decision of 2026-08-12 every placement records how its id was confirmed |

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

Title search alone is unreliable: Pleiades titles Adulis **"Adouli"**, and three
separate searches on the corpus's own vocabulary missed it.

**No id is written from memory** — not by the curator, not by a model. A
remembered id is an authored coordinate wearing a citation.

To check the corpus after editing a record:

```powershell
python -m ingest.verify
python -m ingest.gazetteer --check
```
