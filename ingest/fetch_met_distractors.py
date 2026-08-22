"""Block B4, seam 3 — fetch Met Open Access object records as distractors.

    python -m ingest.fetch_met_distractors --probe          # no selection, no output corpus
    python -m ingest.fetch_met_distractors --fetch --limit 160

Runs on the host, like every other data acquisition in this project (the
Pleiades dump, the GeoNames dump, the Wikisource recovery). Writes JSON to
`data/distractors/`; loading into Postgres is a separate step, so the fetched
material is a reviewable artefact on disk before anything is embedded.

THE API'S SHAPE IS DISCOVERED, NOT ASSUMED
------------------------------------------
`--probe` records the live field names to `data/distractors/met-api-shape.json`
and `--fetch` asserts every field it depends on is present, naming any that are
missing. This project has now paid three times in one week for asserting
something about a system without measuring it — a gazetteer id from memory, an
index state from a dated line, an INSERT against unread DDL. An API schema from
recollection is the same move, and the API can change under us besides.

SELECTION: A DATE RULE AND AN ALLOWLIST
---------------------------------------
Block B3 ruled: a single collection, "non-Roman-contact material only".

The load-bearing filter is the **period**: an object whose date range does not
overlap 27 BC – 1204 AD cannot be evidence of Roman contact in this project's
window, whatever it is or wherever it is from. An object with unknown dates is
treated as overlapping and rejected — an unproven negative is not a negative.

The second filter is a department **allowlist** of six, chosen for material
culture comparable to the corpus's own find records. It replaced a denylist of
six-out-of-nineteen after the probe showed that denylist naming "Ancient Near
Eastern Art", a department the Met has renamed **Ancient West Asian Art** — so
the exclusion matched nothing, and the department holding Sasanian silver was
silently admitted. A denylist requires being right about all nineteen; an
allowlist requires being right about the six you name, and `assert_departments`
refuses to run if any of the six is absent from the live list.

WHAT THE TEXT IS
----------------
The Met API returns structured metadata, not narrative prose, so the distractor
text is a **rendered catalogue record** assembled from title, culture, period,
medium, dimensions, classification and credit line. That is stated plainly
because it is a claim about what the padding is: it is the same shape as the
corpus's own object descriptions ("Gold coin. Half-length bust of Ezanas right,
crowned, holding spear...", 279 characters), which are themselves rendered
catalogue records. It is not scraped prose and does not pretend to be.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# The era rule, the seed, the fetch and the output shape are SHARED with every
# other distractor source. Two implementations of one rule is the defect this
# repository keeps paying for, and an era rule that drifted between two fetchers
# would put in-period material in the padding on one side only, silently.
from ingest.distractors_common import (  # noqa: E402
    ERA_END,
    ERA_START,
    MIN_CHARS,
    OUT_DIR,
    PROGRESS_EVERY,
    SEED,
    Throttled,
    cap,
    get,
    report,
    write_records,
)
from ingest.distractors_common import overlaps_era as _overlaps_era  # noqa: E402

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
# about where THIS process is writing, and until 2026-08-22 nothing guarded it.
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

API = "https://collectionapi.metmuseum.org/public/collection/v1"
SHAPE_FILE = OUT_DIR / "met-api-shape.json"

# An ALLOWLIST, not a denylist. The first draft denied six departments out of
# nineteen, which requires being right about all nineteen — and it was not: it
# named "Ancient Near Eastern Art", which the Met has renamed **Ancient West
# Asian Art**, so the exclusion matched nothing and the department holding
# Sasanian silver (which is in the seed corpus) was silently admitted. The probe
# printed the live names beside the EXCLUDED marks and the gap was visible.
#
# An allowlist requires being right about the six you name. `assert_departments`
# then refuses to run if any named department is absent from the live list, so
# a rename can never again quietly widen or empty the selection.
#
# These six are chosen for material culture comparable to the corpus's own find
# records — metalwork, ceramics, glass, arms, instruments. The probe's first two
# samples were an 1843 cut-paper silhouette and a 1940s New York interior
# photograph: both pass the era rule trivially and are useless as distractors,
# because BLOCK_B3_DISTRACTORS.md's own warning is that material too dissimilar
# makes the curve flat for a reason that has nothing to do with the corpus.
INCLUDED_DEPARTMENTS = {
    "American Decorative Arts",
    "Arms and Armor",
    "Arts of Africa, Oceania, and the Americas",
    "Asian Art",
    "European Sculpture and Decorative Arts",
    "Musical Instruments",
}

# THE TWO ENDPOINTS DO NOT SHARE A VOCABULARY.
#
# /departments calls id 1 "American Decorative Arts". Every object record
# returned for id 1 reports `department: "The American Wing"`. So a record-level
# re-check against INCLUDED_DEPARTMENTS rejects ALL of them, and --fetch would
# have returned almost nothing while reporting the losses as `wrong_department`.
# Found by --preview, which does not apply that check; the preview and the fetch
# disagreed and the fetch was the one that was wrong.
#
# Selection is therefore keyed on departmentId, which is stable across both
# endpoints. The record's own `department` string is recorded, checked for
# consistency within its id, and tested against the list below — a DENYLIST is
# correct here, because this is a safety net on the record rather than the
# selection itself, and it must fail closed on a name it does not recognise.
FORBIDDEN_DEPARTMENT_NAMES = {
    "Greek and Roman Art",
    "Ancient West Asian Art",
    "Ancient Near Eastern Art",   # the former name, kept so a revert cannot slip through
    "Egyptian Art",
    "Islamic Art",
    "Medieval Art",
    "The Cloisters",
}

# ...AND THAT DENYLIST IS WRITTEN IN THE WRONG VOCABULARY, WHICH IS THE POINT.
#
# The --preview 12 run showed two of six allowlisted departments reporting a
# different name on their records:
#
#     'American Decorative Arts'                  -> 'The American Wing'
#     'Arts of Africa, Oceania, and the Americas' -> 'The Michael C. Rockefeller Wing'
#
# Those names come from /departments; records report wing names. So a record
# from a FORBIDDEN department, arriving under a stray id, might report a wing
# name that is not in the list above — and the denylist would fail open, exactly
# as the "Ancient Near Eastern Art" entry already did.
#
# A denylist of names cannot be completed against a vocabulary we do not hold.
# The real guard is therefore vocabulary-agnostic and fails CLOSED on novelty:
# the first record seen for a departmentId establishes the name that id reports,
# and any later record reporting a different name is rejected. A stray record
# from another department cannot pass, whatever either endpoint calls it.
def department_guard(dept_id: int, reported: str | None,
                     expected: dict[int, str]) -> str | None:
    """Rejection reason, or None. Fails closed on an unrecognised name."""
    if reported in FORBIDDEN_DEPARTMENT_NAMES:
        return "forbidden_department"
    known = expected.get(dept_id)
    if known is None:
        expected[dept_id] = reported
        return None
    if reported != known:
        return "unexpected_department_name"
    return None

# Fields the selection and rendering depend on. --fetch refuses to run if the
# live API does not supply them.
REQUIRED_FIELDS = (
    "objectID", "isPublicDomain", "department", "title",
    "objectBeginDate", "objectEndDate", "objectDate", "objectURL",
)
RENDER_FIELDS = (
    "title", "culture", "period", "dynasty", "medium", "dimensions",
    "classification", "artistDisplayName", "creditLine", "country", "region",
)


def probe(sample: int = 5) -> dict:
    departments = get(f"{API}/departments") or {}
    dept_list = departments.get("departments", [])
    ids = (get(f"{API}/objects") or {}).get("objectIDs", [])

    rng = random.Random(SEED)
    picks = rng.sample(ids, min(sample, len(ids))) if ids else []
    samples = [o for o in (get(f"{API}/objects/{i}") for i in picks) if o]

    keys: set[str] = set()
    for obj in samples:
        keys |= set(obj)

    shape = {
        "checked": date.today().isoformat(),
        "api": API,
        "departments": dept_list,
        "total_object_ids": len(ids),
        "sampled_object_ids": picks,
        "observed_fields": sorted(keys),
        "missing_required": sorted(set(REQUIRED_FIELDS) - keys),
        "sample_records": samples,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SHAPE_FILE.write_text(json.dumps(shape, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    return shape


def assert_departments(shape: dict) -> dict:
    """Resolve the allowlist against the live department list, or refuse.

    This is the guard for the defect the probe found: a department name that
    matches nothing silently changes the selection and reports nothing. A
    hardcoded name is a claim about a remote system, and this project's rule is
    that such a claim is checked rather than recalled.
    """
    live = {d["displayName"]: d["departmentId"] for d in shape["departments"]}
    absent = sorted(INCLUDED_DEPARTMENTS - set(live))
    if absent:
        raise SystemExit(
            f"these departments are not in the live list and would select "
            f"nothing: {absent}\n"
            f"Live names are:\n  " + "\n  ".join(sorted(live)) + "\n"
            f"Re-run --probe and reconcile INCLUDED_DEPARTMENTS before fetching.")
    return {name: live[name] for name in sorted(INCLUDED_DEPARTMENTS)}


def overlaps_era(obj: dict) -> bool:
    """Met field names, shared rule."""
    return _overlaps_era(obj.get("objectBeginDate"), obj.get("objectEndDate"))


def render(obj: dict) -> str:
    """A catalogue record as prose. Empty fields are omitted, not rendered blank."""
    bits = []
    title = (obj.get("title") or "").strip()
    name = (obj.get("objectName") or "").strip()
    if title:
        bits.append(title + ".")
    # The corpus's own object descriptions lead with the object type — "Gold
    # coin.", "Gilded silver plate" — so carry objectName when it says something
    # the title does not.
    if name and name.lower() not in title.lower():
        bits.append(name + ".")
    who = " ".join(x for x in (obj.get("culture"), obj.get("period"),
                               obj.get("dynasty")) if x)
    if who.strip():
        bits.append(who.strip() + ".")
    if obj.get("artistDisplayName"):
        bits.append(f"{obj['artistDisplayName']}.")
    if obj.get("objectDate"):
        bits.append(f"Dated {obj['objectDate']}.")
    if obj.get("medium"):
        bits.append(f"{obj['medium']}.")
    if obj.get("dimensions"):
        bits.append(f"{obj['dimensions']}.")
    if obj.get("classification"):
        bits.append(f"Classified as {obj['classification']}.")
    where = ", ".join(x for x in (obj.get("country"), obj.get("region")) if x)
    if where:
        bits.append(f"From {where}.")
    if obj.get("creditLine"):
        bits.append(f"{obj['creditLine']}.")
    return " ".join(bits)


def fetch(limit: int, min_chars: int = MIN_CHARS) -> dict:
    shape = json.loads(SHAPE_FILE.read_text(encoding="utf-8")) if SHAPE_FILE.exists() else probe()
    missing = shape.get("missing_required")
    if missing:
        raise SystemExit(
            f"the live API does not supply {missing}, which selection depends "
            f"on. Re-run --probe and read data/distractors/met-api-shape.json "
            f"before changing anything: the schema moved, or the sample was "
            f"unrepresentative.")

    wanted_depts = assert_departments(shape)

    rejected = {"not_public_domain": 0, "overlaps_era": 0, "forbidden_department": 0,
                "unexpected_department_name": 0, "too_short": 0, "no_title": 0,
                "unfetchable": 0}
    kept: list[dict] = []
    observed_names: dict[int, set] = {}
    expected_name: dict[int, str] = {}
    rng = random.Random(SEED)

    # Deterministic order across the whole allowlist, so a tranche is
    # reproducible and its composition can be recorded in the archived run.
    pool: list[tuple[str, int, int]] = []
    for name, dept_id in sorted(wanted_depts.items()):
        print(f"  listing {name}...", flush=True)
        ids = (get(f"{API}/objects?departmentIds={dept_id}") or {}).get("objectIDs") or []
        print(f"    {len(ids)} object ids", flush=True)
        pool.extend((name, dept_id, i) for i in sorted(ids))
    rng.shuffle(pool)
    print(f"  pool: {len(pool)} candidate objects; keeping up to {limit}",
          flush=True)

    throttled = None
    examined = 0
    for name, dept_id, object_id in pool:
        if len(kept) >= limit:
            break
        examined += 1
        if examined % PROGRESS_EVERY == 0:
            print(f"    examined {examined}, kept {len(kept)}", flush=True)
        try:
            obj = get(f"{API}/objects/{object_id}")
        except KeyboardInterrupt:
            # Ctrl-C used to discard everything gathered, because the file is
            # written only at the end. An interrupt is a reason to stop, not a
            # reason to lose work — the same rule already applied to a 403.
            throttled = "interrupted by the operator"
            break
        except Throttled as exc:
            # Keep what was gathered. The first 300-record run died on a 403
            # and lost every record it had, because the exception escaped to
            # the top. A refused API is a reason to stop, not a reason to
            # discard work.
            throttled = str(exc)
            break
        if not obj:
            rejected["unfetchable"] += 1
            continue
        if not obj.get("isPublicDomain"):
            rejected["not_public_domain"] += 1
            continue
        # Record-level safety net, not the selection. Selection is by
        # departmentId; this catches an object reporting a department the ruling
        # forbids, or one that does not report the name its id has been
        # reporting all along.
        observed_names.setdefault(dept_id, set()).add(obj.get("department"))
        reason = department_guard(dept_id, obj.get("department"), expected_name)
        if reason:
            rejected[reason] += 1
            continue
        if overlaps_era(obj):
            rejected["overlaps_era"] += 1
            continue
        if not (obj.get("title") or "").strip():
            rejected["no_title"] += 1
            continue
        text = cap(render(obj))
        if len(text) < min_chars:
            rejected["too_short"] += 1
            continue
        kept.append({
            "object_id": obj["objectID"],
            "department": obj.get("department"),
            "department_id": dept_id,
            "department_listed_as": name,
            "title": obj.get("title"),
            "object_date": obj.get("objectDate"),
            "object_begin_date": obj.get("objectBeginDate"),
            "object_end_date": obj.get("objectEndDate"),
            "is_public_domain": obj.get("isPublicDomain"),
            "object_url": obj.get("objectURL"),
            "text": text,
        })

    if throttled:
        rejected["stopped_early_throttled"] = 1
    return write_records("met", kept, rejected, {
        "licence": "CC0 — see data/met-licence-declaration.txt",
        "throttled": throttled,
        "included_departments": sorted(INCLUDED_DEPARTMENTS),
        "forbidden_department_names": sorted(FORBIDDEN_DEPARTMENT_NAMES),
        # /departments and /objects/{id} disagree on names. Recorded so the
        # mapping is an artefact rather than a thing someone rediscovers.
        "department_id_to_record_name": {
            str(k): sorted(x for x in v if x)
            for k, v in sorted(observed_names.items())},
    })


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--probe", action="store_true",
                    help="record the live API shape; select nothing")
    ap.add_argument("--fetch", action="store_true", help="select and write records")
    ap.add_argument("--preview", type=int, metavar="N",
                    help="render N allowlisted, public-domain, out-of-era "
                         "records and stop. Look at the padding before "
                         "committing an embedding request to it.")
    ap.add_argument("--pause", type=float, default=None,
                    help="seconds between requests. The Met returned 403 at the "
                         "default 0.12; try 1.0 to fetch more slowly.")
    ap.add_argument("--limit", type=int, default=160,
                    help="how many records to keep (default 160)")
    args = ap.parse_args(argv)

    if args.pause:
        import functools

        import ingest.distractors_common as _c
        _c.get = functools.partial(_c.get, pause=args.pause)
        globals()["get"] = _c.get

    if args.probe:
        shape = probe()
        print(f"departments ({len(shape['departments'])}):")
        for d in shape["departments"]:
            mark = "  <- INCLUDED" if d["displayName"] in INCLUDED_DEPARTMENTS else ""
            print(f"  {d['departmentId']:>3}  {d['displayName']}{mark}")
        print(f"\ntotal object ids: {shape['total_object_ids']}")
        print(f"observed fields ({len(shape['observed_fields'])}): "
              f"{', '.join(shape['observed_fields'])}")
        print(f"\nmissing required: {shape['missing_required'] or 'none'}")
        unmatched = sorted(INCLUDED_DEPARTMENTS -
                           {d["displayName"] for d in shape["departments"]})
        print(f"allowlist entries not present live: {unmatched or 'none'}")
        for rec in shape["sample_records"][:2]:
            print(f"\n--- {rec.get('objectID')} {rec.get('department')} "
                  f"[{rec.get('objectBeginDate')}..{rec.get('objectEndDate')}] "
                  f"public_domain={rec.get('isPublicDomain')}")
            print(f"    rendered: {render(rec)[:300]}")
        print(f"\nwrote {SHAPE_FILE}")
        return 0

    if args.preview:
        shape = json.loads(SHAPE_FILE.read_text(encoding="utf-8"))
        depts = assert_departments(shape)
        rng = random.Random(SEED)
        # Round-robin, not fill-from-the-first. The first version broke out of
        # the loop once it had enough and so only ever showed department 1 —
        # a preview of one sixth of the seam, read as a preview of the seam.
        candidates: dict[str, list] = {}
        for name, dept_id in sorted(depts.items()):
            ids = (get(f"{API}/objects?departmentIds={dept_id}") or {}).get("objectIDs") or []
            candidates[name] = rng.sample(sorted(ids), min(60, len(ids)))

        shown, per_dept = 0, max(1, args.preview // max(1, len(candidates)))
        names_seen: dict[str, set] = {}
        for name, ids in candidates.items():
            got = 0
            for object_id in ids:
                if got >= per_dept or shown >= args.preview:
                    break
                obj = get(f"{API}/objects/{object_id}")
                if not obj or not obj.get("isPublicDomain") or overlaps_era(obj):
                    continue
                text = render(obj)
                if len(text) < 120:
                    continue
                names_seen.setdefault(name, set()).add(obj.get("department"))
                got += 1
                shown += 1
                print(f"\n--- {obj['objectID']}  listed as {name!r}  "
                      f"reports {obj.get('department')!r}  "
                      f"[{obj.get('objectBeginDate')}..{obj.get('objectEndDate')}]  "
                      f"{len(text)} chars")
                print(f"    {text}")

        print(f"\nshown {shown}. Corpus object_description chunks are 110-409 chars.")
        print("\ndepartment name as listed -> as reported on the record:")
        for name, reported in sorted(names_seen.items()):
            flag = "" if reported == {name} else "   <- DIFFERENT"
            print(f"  {name!r} -> {sorted(reported)}{flag}")
        return 0

    if args.fetch:
        out = fetch(args.limit)
        report(out)
        if out.get("throttled"):
            print(f"\nSTOPPED EARLY: {out['throttled']}")
            print("The records above are written and safe. Re-run --fetch later "
                  "to top up;\nalready-written ids are skipped by the loader, "
                  "not re-fetched here.")
        depts: dict = {}
        for r in out["records"]:
            depts[r["department"]] = depts.get(r["department"], 0) + 1
        print("\nby department:")
        for d, n in sorted(depts.items(), key=lambda kv: -kv[1]):
            print(f"  {n:4d}  {d}")
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
