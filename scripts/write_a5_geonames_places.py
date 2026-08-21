"""Write the GeoNames placements into the five records Pleiades could not reach.

Generated rather than hand-edited, on the same argument as
`scripts/write_a4_places.py`: idempotent, rebuilds each block, writes only if
the result differs.

Every id below was accepted on its **coordinate and feature code**, never its
name, against the GeoNames country dumps searched on 2026-08-13. Two of the
four searches produced a plausible name match at the wrong place and both were
refused — those refusals are the most useful thing in this file and are
recorded in the notes that displace them.

    site                 result
    Gyeongju             1841603  P.PPL     accepted, 0.6 km from the tomb
    Óc Eo                13405688 P.PPLA2   accepted, the modern town
    Khao Sam Kaeo        8242723  T.HLL     REFUSED — 297 km from Chumphon
    Jabal Ḏabūb          7365997  P.PPL     REFUSED — 286 km from Ad Dali'
                         12118329 P.PPL     REFUSED — 152 km from Ad Dali'

Ground is `stated` for the three accepted placements, not `identified`.
`PLACES.md` says a GeoNames placement "will usually be identified rather than
stated", and that guidance is written for the Adulis ≈ Zula case, where a
scholar maps an ancient name onto a modern location. Nothing of the kind is
happening here: the records name Gyeongju and Óc Eo themselves, as modern
places, and GeoNames holds those same modern places. Marking them `identified`
would demand a `ground_citation` for the proposition that Gyeongju is Gyeongju.

What the coordinate DENOTES is the real risk, and it is carried in every note:
a city centre is not a tomb and a town is not an excavation trench.

Run: python scripts/write_a5_geonames_places.py [--check]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "data" / "seed_corpus"
sys.path.insert(0, str(ROOT))
from ingest.places import canonical_uri  # noqa: E402
from ingest.loader import iter_seed_records  # noqa: E402

CONFIRMED = (
    "Confirmed 2026-08-13 against the GeoNames country dump named below; the "
    "snapshot date is recorded in data/gazetteer.json under sources.geonames."
)


def P(name, ground, gid=None, note=None):
    e = {"name": name, "ground": ground}
    if gid:
        e["gazetteer"] = "geonames"
        e["gazetteer_id"] = gid
        e["uri"] = canonical_uri("geonames", gid)
    if note:
        e["note"] = note
    return e


PLACEMENTS: dict[str, list[dict]] = {
    # ---------------------------------------------------------------- Korea
    "eastasia-03-hwangnam-glass": [
        P(
            "Gyeongju", "stated", "1841603",
            CONFIRMED + " KR.zip. 1841603 'Gyeongju' 35.843/129.212, feature "
            "code P.PPL (populated place), North Gyeongsang — 0.6 km from the "
            "Daereungwon tumulus park that holds Hwangnam-daechong. **The "
            "coordinate denotes the modern city, not the tomb**: GeoNames has "
            "no entry for Tomb No. 98 or its south mound, and none was "
            "invented. Refused: 1833276 'Gyeongju' 35.833/129.250, which "
            "carries the same name and is A.ADM2 — the municipality, whose "
            "representative point sits 3.6 km east of the tumuli and which is "
            "a claim about an administrative area rather than about the "
            "settlement the record names. Also present and irrelevant: 44 "
            "hotels, schools, toll gates and country clubs whose names begin "
            "'Gyeongju'."
        ),
    ],
    # --------------------------------------------------------------- Vietnam
    "seasia-01-oc-eo-medallion": [
        P(
            "Óc Eo", "stated", "13405688",
            CONFIRMED + " VN.zip. 13405688 'Óc Eo' 10.242/105.155, feature "
            "code P.PPLA2 (populated place, seat of a second-order division), "
            "An Giang. **The coordinate denotes the modern town, not the "
            "excavated site**, which lies adjacent to it; GeoNames holds no "
            "entry for the excavation itself. Refused on feature type: "
            "8375917 'Thị Trấn Óc Eo' 10.251/105.145, A.ADM3 — the township "
            "boundary 1.5 km away, whose representative point is arbitrary "
            "within the polygon where the settlement's is not. The record's "
            "own note flags the identification of Óc Eo with Ptolemy's "
            "Cattigara as debated; that is an ancient-name question and is "
            "deliberately NOT encoded here, since no gazetteer entry for "
            "Cattigara was resolved and a contested identification needs both "
            "sides on the record."
        ),
    ],
    "seasia-02-oc-eo-site": [
        P(
            "Óc Eo", "stated", "13405688",
            CONFIRMED + " VN.zip. The same id `seasia-01-oc-eo-medallion` "
            "carries — one place, two records, which is what the UI's grouping "
            "by cached id exists to draw as a single marker. 13405688 'Óc Eo' "
            "10.242/105.155, P.PPLA2, An Giang. **The coordinate denotes the "
            "modern town**; this record's findspot is 'Óc Eo commune', for "
            "which GeoNames also holds 8375917 (A.ADM3, 1.5 km away) — refused "
            "for the same reason as in seasia-01, and so that both records "
            "resolve to one point rather than two 1.5 km apart."
        ),
    ],
    # -------------------------------------------------------------- Thailand
    "seasia-03-khao-sam-kaeo": [
        P(
            "Khao Sam Kaeo", "regional", None,
            "**GeoNames 8242723 'Khao Sam Kaeo' was examined and REFUSED on "
            "coordinate.** It is a T.HLL (hill) at 8.016/100.191 — 297 km "
            "south of Chumphon, in a different province from the site this "
            "record describes. *Khao Sam Kaeo* is a generic Thai toponym "
            "(roughly 'three-crystal hill') and the name matches a hill that "
            "is not this one; accepting it would have drawn the Thai-Malay "
            "peninsular trade site 300 km down the coast. Same class of error "
            "as Byzantion on the Konkan, and caught the same way — on the "
            "coordinate, not the name. The archaeological site at Khao Sam "
            "Kaeo, on the Tha Tapao river near Chumphon town, has no entry in "
            "the GeoNames TH dump under this name, and none in Pleiades. What "
            "is known is the region: the upper Thai-Malay peninsula, Chumphon "
            "Province. No point is drawn, which is correct."
        ),
    ],
    # ----------------------------------------------------------------- Yemen
    "arabia-04-jabal-dabub": [
        P(
            "Jabal Ḏabūb", "regional", None,
            "**Both GeoNames candidates were examined and REFUSED**, on "
            "feature type and on coordinate. 7365997 'Ad Dabūb' "
            "15.944/43.437 and 12118329 'Ad Dabūb' 14.519/43.601 are both "
            "P.PPL — *populated places*, where the record names a mountain "
            "(Arabic *jabal*), and GeoNames classes mountains T.MT. Both also "
            "sit far outside the region the record gives: 286 km and 152 km "
            "respectively from Ad Dali', in the Dhale region of southern "
            "Yemen. A settlement called Ad Dabūb is not Mount Ḏabūb, and "
            "neither is in the right place. Nothing resolves in either "
            "gazetteer; what is known is the region, Dhale, and no more."
        ),
    ],
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report what would change; write nothing")
    args = ap.parse_args()

    by_id = {}
    for path in iter_seed_records(SEED):
        by_id[json.loads(path.read_text(encoding="utf-8"))["id"]] = path

    changed, unchanged, missing = [], [], []
    for doc_id, block in PLACEMENTS.items():
        path = by_id.get(doc_id)
        if path is None:
            missing.append(doc_id)
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("findspot_places") == block:
            unchanged.append(doc_id)
            continue
        record["findspot_places"] = block
        # `no_places_reason` and a place block contradict each other and
        # ingest/places.py refuses both together. None of these five carries
        # one, but removing it here means this script stays correct if one is
        # ever added and then superseded by a real placement.
        record.pop("no_places_reason", None)
        if not args.check:
            path.write_text(
                json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        changed.append(doc_id)

    verb = "would change" if args.check else "wrote"
    for doc_id in changed:
        n = len(PLACEMENTS[doc_id])
        located = sum(1 for e in PLACEMENTS[doc_id] if e.get("gazetteer_id"))
        print(f"  {verb:12s} {doc_id:30s} {n} placement(s), {located} with an id")
    for doc_id in unchanged:
        print(f"  {'unchanged':12s} {doc_id}")
    if missing:
        print(f"\nNO SUCH RECORD: {missing}")
        return 1

    ids = sorted({e["gazetteer_id"] for b in PLACEMENTS.values()
                  for e in b if e.get("gazetteer_id")})
    print(f"\n{len(ids)} distinct GeoNames id(s) now cited: {ids}")
    print("These are NOT yet cached. Run, with the country dumps to hand:")
    print("  python -m ingest.gazetteer --geonames-dump <KR.zip> --refresh-geonames")
    print("  python -m ingest.gazetteer --geonames-dump <VN.zip> --refresh-geonames")
    print("`--check` will fail until then, naming each uncached id.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
