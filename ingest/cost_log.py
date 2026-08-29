"""The only thing that writes data/curation_cost.json.

    python -m ingest.cost_log start  <record_id> <phase>
    python -m ingest.cost_log stop   [--note TEXT]
    python -m ingest.cost_log stop   --minutes N --because TEXT
    python -m ingest.cost_log add    <record_id> <phase> --minutes N --because TEXT
    python -m ingest.cost_log status
    python -m ingest.cost_log report
    python -m ingest.cost_log check

`start`/`stop` is a clock this repository ran, and what it writes is
`measured`. `add` is somebody remembering, and what it writes is `estimated`
with a written reason. Ruling 48 keeps them apart in the file and the report
prints the split, because a trend computed mostly out of recollection is not a
measurement of anything and the only moment anyone can tell is now.

The rules live in `ingest/cost.py`, which imports nothing from this package.
This module is the part that has to touch the corpus, and it touches it for
exactly one reason: to DERIVE each timed record's tier rather than let a
curator type it. Ruling 45 reports cost per tier, and a tier somebody typed is
a tier that can be typed wrong in the direction that flatters the mean.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from . import cost
from .loader import SEED_CORPUS_DIR, load_corpus

# FINDING 10: this process's own stdout. Through a pipe or a redirect on
# Windows it falls back to the locale codec, which cannot encode Greek, Tamil,
# Chinese, Ge'ez or runic, and it raises mid-output with the file half written
# and every number in it correct.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "curation_cost.json"
TIERS_PATH = Path(__file__).resolve().parent.parent / "data" / "corpus_tiers.json"

STAMP = "%Y-%m-%dT%H:%M:%SZ"


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def read_ledger(path: Path | None = None) -> dict:
    path = path or LEDGER_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def write_ledger(ledger: dict, path: Path | None = None) -> None:
    """LF, UTF-8, two-space indent, key order preserved.

    Bytes on the way out, for `mutate_ui_places`'s reason on 2026-08-28: a
    writer that goes through text mode picks a line ending, and the conversion
    reached a commit before a text-comparing check could see it. .gitattributes
    says git must not rewrite a byte of this repository; a writer inside it
    must not either.
    """
    path = path or LEDGER_PATH
    body = json.dumps(ledger, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
    path.write_bytes(body.encode("utf-8"))


def derived_tiers(corpus_dir: Path = SEED_CORPUS_DIR) -> "dict[str, tuple[str, str]]":
    """Every corpus record's tier, derived. Never declared, never typed."""
    from .fidelity import derive_record_tier

    result = load_corpus(corpus_dir)
    rows: dict[str, list] = defaultdict(list)
    for c in result.chunks:
        rows[c.doc_id].append(
            (c.role, c.text_fidelity, c.lang, c.eligible_for_retrieval)
        )
    return {
        d.doc_id: derive_record_tier(
            d.source_type, rows[d.doc_id], getattr(d, "translation_source", None)
        )
        for d in result.documents
    }


def _entry_for(ledger: dict, record_id: str, tiers: dict) -> dict:
    for entry in ledger["records"]:
        if entry.get("record_id") == record_id:
            break
    else:
        entry = {
            "record_id": record_id,
            "tier": "",
            "curated_on": _now().strftime("%Y-%m-%d"),
            "phases": {
                name: {"minutes": 0, "provenance": "measured"} for name in cost.PHASES
            },
            "note": "",
        }
        ledger["records"].append(entry)

    # Re-derived on every write, not stamped once. A record whose text lands
    # after its source-hunting was timed changes tier legitimately, and a tier
    # frozen at the first `start` would file the whole record under whatever it
    # looked like before it had a translation.
    if record_id in tiers:
        entry["tier"] = tiers[record_id][0]
    return entry


def _credit(entry: dict, phase: str, minutes: float, provenance: str,
            because: str) -> None:
    cell = entry["phases"].setdefault(
        phase, {"minutes": 0, "provenance": provenance}
    )
    cell["minutes"] = round(float(cell.get("minutes", 0) or 0) + float(minutes), 1)
    # Once any part of a phase is remembered rather than clocked, the phase is
    # remembered. The weaker provenance wins, because a cell labelled
    # `measured` that is half an estimate is the more flattering of the two
    # readings and the one nobody would check.
    if provenance == "estimated" or cell.get("provenance") == "estimated":
        cell["provenance"] = "estimated"
        reasons = [r for r in (cell.get("because", ""), because) if r.strip()]
        cell["because"] = " | ".join(dict.fromkeys(reasons))
    else:
        cell["provenance"] = "measured"


def cmd_start(args) -> int:
    ledger = read_ledger()
    if ledger.get("open_entry"):
        open_entry = ledger["open_entry"]
        print(
            f"a clock is ALREADY running: {open_entry['record_id']} / "
            f"{open_entry['phase']} since {open_entry['started_at']}.\n"
            f"Two clocks would double-count the overlap into a column that "
            f"cannot be re-measured. Stop that one first."
        )
        return 1
    if args.phase not in cost.PHASES:
        print(f"{args.phase!r} is not a phase. The seven are: "
              f"{', '.join(cost.PHASES)}")
        return 1
    ledger["open_entry"] = {
        "record_id": args.record_id,
        "phase": args.phase,
        "started_at": _now().strftime(STAMP),
    }
    write_ledger(ledger)
    print(f"started {args.record_id} / {args.phase} at "
          f"{ledger['open_entry']['started_at']}")
    return 0


def cmd_stop(args) -> int:
    ledger = read_ledger()
    open_entry = ledger.get("open_entry")
    if not open_entry:
        print("no clock is running.")
        return 1

    started = datetime.strptime(open_entry["started_at"], STAMP).replace(
        tzinfo=timezone.utc
    )
    span = round((_now() - started).total_seconds() / 60.0, 1)
    limit = float(ledger["max_measured_span_minutes"])

    if args.minutes is not None:
        if not args.because.strip():
            print("--minutes on `stop` overrides a clock, so it needs "
                  "--because. An unexplained override is a measurement by "
                  "tomorrow.")
            return 1
        minutes, provenance = float(args.minutes), "estimated"
        because = (f"{args.because} (clock read {span} min from "
                   f"{open_entry['started_at']})")
    elif span > limit:
        print(
            f"the clock has been running {span} minutes, above the "
            f"{limit:g}-minute span limit this ledger declares. A clock left "
            f"running overnight writes a working day of `measured` minutes "
            f"into the one number kill trigger 3 hangs off.\n"
            f"Close it deliberately:\n"
            f"  python -m ingest.cost_log stop --minutes N --because \"...\""
        )
        return 1
    else:
        minutes, provenance, because = span, "measured", ""

    tiers = derived_tiers()
    entry = _entry_for(ledger, open_entry["record_id"], tiers)
    _credit(entry, open_entry["phase"], minutes, provenance, because)
    if args.note:
        entry["note"] = (entry.get("note", "") + " " + args.note).strip()
    ledger["open_entry"] = None
    write_ledger(ledger)
    print(
        f"{open_entry['record_id']} / {open_entry['phase']}: +{minutes} min "
        f"({provenance}). Record total now "
        f"{cost.record_total(entry):.1f} min, tier "
        f"{entry['tier'] or 'NOT YET DERIVABLE -- the record is not in the corpus'}."
    )
    return 0


def cmd_add(args) -> int:
    if args.phase not in cost.PHASES:
        print(f"{args.phase!r} is not a phase. The seven are: "
              f"{', '.join(cost.PHASES)}")
        return 1
    if not args.because.strip():
        print("`add` writes an ESTIMATE, so it needs --because. Ruling 48: "
              "measured and remembered are two kinds of knowledge and the "
              "report prints the split.")
        return 1
    ledger = read_ledger()
    tiers = derived_tiers()
    entry = _entry_for(ledger, args.record_id, tiers)
    _credit(entry, args.phase, float(args.minutes), "estimated", args.because)
    write_ledger(ledger)
    print(
        f"{args.record_id} / {args.phase}: +{args.minutes} min (estimated). "
        f"Record total now {cost.record_total(entry):.1f} min."
    )
    return 0


def cmd_status(args) -> int:
    ledger = read_ledger()
    open_entry = ledger.get("open_entry")
    if not open_entry:
        print("no clock is running.")
    else:
        started = datetime.strptime(open_entry["started_at"], STAMP).replace(
            tzinfo=timezone.utc
        )
        span = (_now() - started).total_seconds() / 60.0
        print(f"running: {open_entry['record_id']} / {open_entry['phase']} "
              f"since {open_entry['started_at']} ({span:.1f} min)")
    timed = len(ledger.get("records") or [])
    excused = len(ledger.get("not_timed") or {})
    print(f"{timed} record(s) timed, {excused} excused from timing.")
    return 0


def cmd_report(args) -> int:
    ledger = read_ledger()
    mix = {}
    if TIERS_PATH.exists():
        mix = (json.loads(TIERS_PATH.read_text(encoding="utf-8"))
               .get("target_mix") or {})
    for line in cost.format_report(ledger, mix):
        print(line)
    return 0


def cmd_check(args) -> int:
    ledger = read_ledger()
    problems = cost.check_ledger(ledger, derived_tiers())
    if problems:
        print(f"FAILED ({len(problems)})")
        for p in problems:
            print(f"  x {p}")
        return 1
    print("curation cost ledger: all checks passed.")
    return 0


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m ingest.cost_log")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("start", help="start the clock on one record and phase")
    p.add_argument("record_id")
    p.add_argument("phase")
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("stop", help="stop the clock and credit the minutes")
    p.add_argument("--note", default="")
    p.add_argument("--minutes", type=float, default=None,
                   help="override the clock; writes an ESTIMATE and needs "
                        "--because")
    p.add_argument("--because", default="")
    p.set_defaults(func=cmd_stop)

    p = sub.add_parser("add", help="record remembered minutes as an estimate")
    p.add_argument("record_id")
    p.add_argument("phase")
    p.add_argument("--minutes", type=float, required=True)
    p.add_argument("--because", required=True)
    p.set_defaults(func=cmd_add)

    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("report").set_defaults(func=cmd_report)
    sub.add_parser("check").set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
