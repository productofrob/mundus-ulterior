"""Block B4, seam 3b — Cleveland Museum of Art open-access records as distractors.

    python -m ingest.fetch_cma_distractors --probe
    python -m ingest.fetch_cma_distractors --preview 12
    python -m ingest.fetch_cma_distractors --fetch --limit 80

WHY A SECOND COLLECTION
-----------------------
Block B3's decision 3 was "one collection only — mixing three makes 'where did
this come from' a per-chunk question". Amended 2026-08-14, and the reason is not
volume: the Met holds 502,238 objects and the era rule *excludes* material, so
there was never a shortage.

The reason is **skeleton uniformity**. A rendered catalogue record has a fixed
shape — *Title. Culture. Dated X. Medium. Dimensions. Credit line.* — and the
Met preview produced eight records with that identical shape. Several hundred
chunks sharing one skeleton may cluster in embedding space and either all
compete with a gold target or none do, which would make the W2b curve a
measurement of my renderer rather than of the index.

The per-chunk provenance objection is answered by `distractor_source`, which is
on the row and NOT NULL for every distractor (scripts/schema-b4-distractors.sql).
"where did this come from" is a column, not a question.

WHY CLEVELAND
-------------
It needs no API key, which the Rijksmuseum and Smithsonian both do — a key is a
credential to store, rotate and keep out of git, for padding. And its records
carry free-text `description` and `tombstone` fields alongside the structured
ones, so its rendering can differ in shape from the Met's rather than being the
same skeleton wearing a different accession number.

**That last sentence is an expectation, not a measurement.** `--probe` records
the live field names and prints which of them are present; if `description` is
absent or usually empty, the second source is not buying what it was added for
and the amendment should be revisited rather than quietly proceeded with.

LICENCE
-------
CC0, attested by the project owner 2026-08-14 and recorded in
`data/cma-licence-declaration.txt`. That file states plainly that — unlike the
Met's — the terms were NOT fetched and quoted in-session, because the fetch
needed an approval that was not given. A human reading the page is a legitimate
source; it is recorded as what it is rather than dressed up as a quotation.

CC0 is a property of the individual record, not of the API. Every record is
checked on its own `share_license_status` and the value is kept on the row.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingest.distractors_common import (  # noqa: E402
    MIN_CHARS,
    OUT_DIR,
    SEED,
    PROGRESS_EVERY,
    Throttled,
    cap,
    get,
    overlaps_era,
    report,
    sentence,
    strip_markup,
    write_records,
)

API = "https://openaccess-api.clevelandart.org/api/artworks"
SHAPE_FILE = OUT_DIR / "cma-api-shape.json"
LICENCE_FILE = Path("data/cma-licence-declaration.txt")

# Cleveland's department vocabulary. This API has no numeric department id, so
# the NAME is the identifier — which makes an unverified name exactly the defect
# the Met seam already produced twice.
#
# THESE NAMES ARE A GUESS UNTIL --probe CONFIRMS THEM. The Met's /departments
# endpoint gave an authoritative list; Cleveland has no such endpoint, so the
# probe samples widely and collects the department values it actually observes.
# `assert_departments()` then refuses to fetch if any allowlist entry was never
# seen — because a name that matches nothing silently selects nothing, and the
# first version of the Met fetcher failed exactly that way with a department the
# museum had renamed.
# CONFIRMED against 1200 sampled records, 2026-08-14. All six exist.
#
# "American Painting and Sculpture" (101 in sample) was swapped for "Art of the
# Americas" (46): the former is paintings, the latter is pre-Columbian material
# culture — a closer register match to the corpus's find records, and
# geographically disjoint from all seven regions rather than merely out of era.
INCLUDED_DEPARTMENTS = {
    "Art of the Americas",
    "Chinese Art",
    "Decorative Art and Design",
    "Japanese Art",
    "Korean Art",
    "Textiles",
}

# Belt-and-braces only: selection is a strict allowlist, so anything absent from
# INCLUDED_DEPARTMENTS is already rejected as `not_in_allowlist`. This list
# exists so that adding a department to the allowlist by mistake still fails.
#
# THE THIRD NAMING DEFECT OF THIS SEAM. The first draft listed "Egyptian Art"
# and "Ancient Near Eastern Art" as separate entries, copied from the Met's
# vocabulary. Cleveland combines them: **"Egyptian and Ancient Near Eastern
# Art"** (30 in sample). Both entries matched nothing.
#
# Three museums, three vocabularies, three silent no-ops — the Met's renamed
# West Asian department, the Met's /departments-vs-record wing names, and this.
# `--probe` now reports which forbidden names were never observed, so a no-op
# announces itself instead of reading like protection.
FORBIDDEN_DEPARTMENTS = {
    "Greek and Roman Art",
    "Egyptian and Ancient Near Eastern Art",   # Cleveland's actual name
    "Egyptian Art",                            # kept: harmless if a rename splits them
    "Ancient Near Eastern Art",                # kept: same reason
    "Islamic Art",
    "Medieval Art",
    "Indian and Southeast Asian Art",
    "African Art",   # Sub-Saharan Africa is a corpus region (44 in sample)
}

REQUIRED_FIELDS = ("id", "title", "department", "creation_date_earliest",
                   "creation_date_latest", "share_license_status")


def render(obj: dict) -> str:
    """Cleveland's records differ from the Met's in carrying free text.

    When `description` is present the rendering leads with it, so the chunk does
    not open with the same three words as every Met chunk. When it is absent the
    rendering falls back to the structured fields and IS Met-shaped — which is
    why --probe reports how often that happens.
    """
    desc = strip_markup(obj.get("description") or "")
    if desc:
        return cap(sentence(desc, obj.get("technique"), obj.get("creation_date")))
    return cap(sentence(
        obj.get("title"),
        obj.get("culture")[0] if isinstance(obj.get("culture"), list) and obj.get("culture") else None,
        f"Dated {obj['creation_date']}" if obj.get("creation_date") else None,
        obj.get("technique") or obj.get("type"),
        obj.get("measurements"),
        (obj.get("tombstone") or "").split(",")[-1] if obj.get("tombstone") else None,
    ))


def fetch_page(skip: int, limit: int = 100, department: str | None = None) -> list[dict]:
    url = f"{API}?limit={limit}&skip={skip}&has_image=0"
    if department:
        url += f"&department={urllib_quote(department)}"
    data = get(url) or {}
    return data.get("data") or []


def urllib_quote(s: str) -> str:
    from urllib.parse import quote

    return quote(s)


def probe(pages: int = 12, per_page: int = 100) -> dict:
    """Sample widely enough to enumerate the department vocabulary.

    The first version sampled 40 records and saw three departments, five of the
    six allowlist entries unconfirmed. A vocabulary cannot be checked against a
    sample that does not contain it, and "not seen in this sample" reads
    dangerously like "does not exist".
    """
    rows: list[dict] = []
    for page in range(pages):
        batch = fetch_page(page * per_page, per_page)
        if not batch:
            break
        rows.extend(batch)

    keys: set[str] = set()
    for row in rows:
        keys |= set(row)
    with_desc = sum(1 for r in rows if (r.get("description") or "").strip())
    counts: dict[str, int] = {}
    for r in rows:
        d = r.get("department")
        if d:
            counts[d] = counts.get(d, 0) + 1

    shape = {
        "checked": date.today().isoformat(),
        "api": API,
        "sampled": len(rows),
        "observed_fields": sorted(keys),
        "missing_required": sorted(set(REQUIRED_FIELDS) - keys),
        "departments_seen": dict(sorted(counts.items(), key=lambda kv: -kv[1])),
        "allowlist_unconfirmed": sorted(INCLUDED_DEPARTMENTS - set(counts)),
        # A forbidden name that matches nothing is not protection, it is a
        # no-op that reads like protection. Reported, not gated: a museum may
        # legitimately have no department by that name.
        "forbidden_never_observed": sorted(FORBIDDEN_DEPARTMENTS - set(counts)),
        "records_with_nonempty_description": with_desc,
        "sample_records": rows[:5],
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SHAPE_FILE.write_text(json.dumps(shape, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    return shape


def assert_departments(shape: dict) -> None:
    """Refuse to fetch on an allowlist entry the API has never been seen to use."""
    unconfirmed = shape.get("allowlist_unconfirmed")
    if unconfirmed:
        seen = shape.get("departments_seen", {})
        raise SystemExit(
            f"these allowlist departments were never observed and would select "
            f"nothing: {unconfirmed}\n"
            f"Departments actually seen, by frequency:\n  " +
            "\n  ".join(f"{n:5d}  {d}" for d, n in seen.items()) + "\n"
            f"Reconcile INCLUDED_DEPARTMENTS against that list, or widen the "
            f"probe, before fetching.")


def selectable(obj: dict) -> str | None:
    """Returns a rejection reason, or None if the record is admissible."""
    if obj.get("department") in FORBIDDEN_DEPARTMENTS:
        return "forbidden_department"
    if obj.get("department") not in INCLUDED_DEPARTMENTS:
        return "not_in_allowlist"
    if overlaps_era(obj.get("creation_date_earliest"), obj.get("creation_date_latest")):
        return "overlaps_era"
    if (obj.get("share_license_status") or "").upper() != "CC0":
        return "not_cc0"
    if not (obj.get("title") or "").strip():
        return "no_title"
    if len(render(obj)) < MIN_CHARS:
        return "too_short"
    return None


def fetch(limit: int) -> dict:
    if not LICENCE_FILE.exists():
        raise SystemExit(
            f"{LICENCE_FILE} does not exist. Confirm Cleveland's terms at\n"
            f"  https://www.clevelandart.org/open-access-api\n"
            f"and write the declaration first, as data/met-licence-declaration.txt\n"
            f"and data/pleiades-licence.txt were. Nothing enters this corpus on a\n"
            f"remembered provenance.")

    shape = json.loads(SHAPE_FILE.read_text(encoding="utf-8")) if SHAPE_FILE.exists() else probe()
    if shape.get("missing_required"):
        raise SystemExit(
            f"the live API does not supply {shape['missing_required']}. Re-run "
            f"--probe and read {SHAPE_FILE} before changing anything.")
    assert_departments(shape)

    rejected: dict[str, int] = {}
    kept: list[dict] = []
    rng = random.Random(SEED)
    skip = 0
    while len(kept) < limit and skip < 20000:
        try:
            rows = fetch_page(skip, 100)
        except (Throttled, KeyboardInterrupt):
            rejected["stopped_early"] = rejected.get("stopped_early", 0) + 1
            break
        if not rows:
            break
        skip += len(rows)
        if skip % (PROGRESS_EVERY * 4) == 0:
            print(f"    scanned {skip}, kept {len(kept)}", flush=True)
        for obj in rows:
            if len(kept) >= limit:
                break
            reason = selectable(obj)
            if reason:
                rejected[reason] = rejected.get(reason, 0) + 1
                continue
            kept.append({
                "object_id": obj.get("id"),
                "department": obj.get("department"),
                "title": obj.get("title"),
                "object_date": obj.get("creation_date"),
                "object_begin_date": obj.get("creation_date_earliest"),
                "object_end_date": obj.get("creation_date_latest"),
                "licence": obj.get("share_license_status"),
                "has_description": bool((obj.get("description") or "").strip()),
                "object_url": obj.get("url"),
                "text": render(obj),
            })
    rng.shuffle(kept)
    return write_records("cma", kept, rejected, {
        "included_departments": sorted(INCLUDED_DEPARTMENTS),
        "forbidden_departments": sorted(FORBIDDEN_DEPARTMENTS),
        "licence": "see data/cma-licence-declaration.txt",
    })


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--preview", type=int, metavar="N")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--pause", type=float, default=None,
                    help="seconds between requests. The Met returned 403 at the "
                         "default 0.12; try 1.0 to fetch more slowly.")
    ap.add_argument("--limit", type=int, default=80)
    args = ap.parse_args(argv)

    if args.pause:
        import functools

        import ingest.distractors_common as _c
        _c.get = functools.partial(_c.get, pause=args.pause)
        globals()["get"] = _c.get

    if args.probe:
        shape = probe()
        print(f"sampled {shape['sampled']} records")
        print(f"observed fields ({len(shape['observed_fields'])}): "
              f"{', '.join(shape['observed_fields'])}")
        print(f"\nmissing required: {shape['missing_required'] or 'none'}")
        print(f"records with a non-empty `description`: "
              f"{shape['records_with_nonempty_description']}/{shape['sampled']}")
        print("  ^ this is the number the second collection was added for. If it "
              "is near zero,\n    Cleveland renders Met-shaped and the amendment "
              "bought nothing — say so\n    rather than proceeding.")
        print(f"\ndepartments observed, by frequency:")
        for d, n in shape["departments_seen"].items():
            mark = "  <- ALLOWLISTED" if d in INCLUDED_DEPARTMENTS else (
                "  <- FORBIDDEN" if d in FORBIDDEN_DEPARTMENTS else "")
            print(f"  {n:5d}  {d}{mark}")
        print(f"\nallowlist entries never observed: "
              f"{shape['allowlist_unconfirmed'] or 'none'}")
        print(f"forbidden names that matched nothing (no-ops, not gated): "
              f"{shape.get('forbidden_never_observed') or 'none'}")
        if shape["allowlist_unconfirmed"]:
            print("  ^ --fetch will REFUSE until these are reconciled. A name "
                  "that matches\n    nothing selects nothing and reports nothing "
                  "— the Met seam failed\n    exactly this way with a renamed "
                  "department.")
        print(f"\nwrote {SHAPE_FILE}")
        return 0

    if args.preview:
        shown = 0
        skip = 0
        while shown < args.preview and skip < 4000:
            rows = fetch_page(skip, 100)
            if not rows:
                break
            skip += len(rows)
            for obj in rows:
                if shown >= args.preview:
                    break
                if selectable(obj):
                    continue
                text = render(obj)
                shown += 1
                print(f"\n--- {obj.get('id')}  {obj.get('department')}  "
                      f"[{obj.get('creation_date_earliest')}.."
                      f"{obj.get('creation_date_latest')}]  "
                      f"desc={bool((obj.get('description') or '').strip())}  "
                      f"{len(text)} chars")
                print(f"    {text[:400]}")
        print(f"\nshown {shown} of {args.preview} requested "
              f"(scanned {skip} records).")
        print("Corpus object_description chunks are 110-409 chars.")
        return 0

    if args.fetch:
        payload = fetch(args.limit)
        report(payload)
        with_desc = sum(1 for r in payload["records"] if r["has_description"])
        print(f"\nrecords rendered from free-text description: "
              f"{with_desc}/{payload['kept']}")
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
