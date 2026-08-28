"""Block F decision 3: are the gold assertions too tight? Asked of the archive,
at a cost of zero chat calls.

Why this exists
---------------

`BLOCK_F_START` names four cases where *"three of the four are the answer being
nearly right"* and says the first question Block F should ask is whether that is
the SYSTEM or the ASSERTIONS — before curating 36 new records against the same
style of assertion.

The question is answerable from what is already on disk. The four Block E
sweeps carry every answer's text and the named failures beside it, and the seed
corpus carries the characters a quotation is supposed to resolve to. Nothing
here makes a chat call, touches the database, or needs the gateway.

    python scripts/assertion_audit.py                 # the four named cases
    python scripts/assertion_audit.py --all-failing   # every case that failed
    python scripts/assertion_audit.py --case skz-titulature
    python scripts/assertion_audit.py --json

What it will and will not tell you
----------------------------------

It reports, per case: which assertion failed, in how many of the archived runs,
and — for the two failure families that can be checked mechanically — what the
near miss actually was.

  * an `expect_answer_excludes` failure prints the phrase IN ITS SENTENCE. A
    bare substring test cannot tell an assertion from its negation, and a
    refusal that names the thing it is refusing to claim reads as a violation
    to a matcher and as a correct answer to a person.

  * an unresolved-quotation failure walks each quoted span down a ladder of
    normalisations against the fields of every cited record, and NAMES the rung
    it lands on. `answer/cite.locate_in_text` already tolerates whitespace,
    case and edge punctuation — *"the three things a writer alters when fitting
    a quotation into a sentence of their own"*. The ladder here adds the rungs
    it does NOT tolerate, so that "the quotation is not in the corpus" and "the
    quotation is in the corpus with an article in front of it" stop being the
    same report.

It does NOT decide anything. A rung is a measurement, not a verdict: adding a
tolerance to the resolver is a change to what this project claims a quotation
IS, and `scripts/mutate_part8.py` already records why that is not a kindness —
*"punctuation tolerance sounds like kindness and is not: it decides on the case
author's behalf that `tortoise shell` and `tortoise-shell` are the same claim
about a source's wording."* The same sentence applies to an article. This
prints the evidence; the ruling is a ruling.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from pathlib import Path

# scripts/ is on sys.path when this is run as `python scripts\assertion_audit.py`
# and the repository root is not. Every script here that imports a repository
# package does exactly this line; see scripts/probe_serving_stack.py.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# FINDING 10: this process's own stdout. Through a pipe or a redirect on Windows
# `print` falls back to the locale codec — cp1252, which cannot encode Greek,
# Tamil, Chinese, Ge'ez or runic, and this report prints answer text and source
# text verbatim. It does not degrade; it raises UnicodeEncodeError mid-output.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = Path(__file__).resolve().parent.parent
SWEEP_DIR = ROOT / "eval" / "sweeps"

# The four `BLOCK_F_START` names, in the order it names them.
NAMED = ["skz-titulature", "raqosh-epitaph", "oc-eo-cattigara",
         "aksumite-coin-imagery"]

# The failure label a missing-quotation assertion produces, and the one an
# exclusion produces. Matched on the label text because that is what the sweep
# archives carry — the CaseResult objects were not archived, only their labels.
_EXCLUDES = re.compile(r'^does not say "(.+)"$')
_QUOTE_DOC = re.compile(r"^quotes (\S+), resolving to characters on disk$")
_QUOTE_MIN = re.compile(r"^resolves at least \d+ quotation\(s\) to characters "
                        r"on disk$")


def _records() -> dict[str, dict]:
    """Every seed record by id, read through the ONE walk D1 left standing.

    `iter_seed_records` yields PATHS, not parsed records — D1 collapsed five
    disagreeing walks of the corpus into this one and it hands back the files
    it found. Reading the JSON here rather than reimplementing the walk is the
    whole point of that consolidation.
    """
    from ingest.loader import iter_seed_records
    out: dict[str, dict] = {}
    for path in iter_seed_records():
        raw = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        if isinstance(raw, dict) and raw.get("id"):
            out[raw["id"]] = raw
    return out


def _fields(record: dict) -> list[tuple[str, str]]:
    """The fields a quotation is allowed to resolve into, longest first."""
    named = ("original_text_excerpt", "reference_translation")
    return [(k, record[k]) for k in named
            if isinstance(record.get(k), str) and record[k].strip()]


# The ladder. Each rung is a transformation applied to the QUOTE only; the
# haystack is never rewritten, because a report that rewrites the corpus to make
# a quotation fit is not a report about the corpus.
#
# Rung 0 is `answer.cite.locate_in_text` itself — whitespace, case and edge
# punctuation — so that "exact" and "case_folded" here mean exactly what they
# mean everywhere else in this repository, and this file adds no fourth
# definition of what a resolved quotation is.
_LEADING_ARTICLE = re.compile(r"^(a|an|the)\s+", re.IGNORECASE)
_TRAILING_ARTICLE = re.compile(r"\s+(a|an|the)$", re.IGNORECASE)


def _rungs(quote: str):
    yield "as written", quote
    stripped = _LEADING_ARTICLE.sub("", quote, count=1)
    if stripped != quote:
        yield "a leading article was added to the quotation", stripped
    trimmed = _TRAILING_ARTICLE.sub("", quote, count=1)
    if trimmed != quote:
        yield "a trailing article was added to the quotation", trimmed
    # Both ends, for a quotation lifted out of the middle of a clause.
    both = _TRAILING_ARTICLE.sub("", stripped, count=1)
    if both not in (quote, stripped, trimmed):
        yield "articles were added at both ends", both


def locate_on_ladder(quote: str, records: dict[str, dict]) -> dict | None:
    """Where a quotation lands, and what had to be forgiven to land it there."""
    from answer import cite
    for rung, candidate in _rungs(quote):
        for doc_id, record in records.items():
            for field, text in _fields(record):
                found = cite.locate_in_text(candidate, text)
                if found:
                    return {"rung": rung, "match": found.match, "doc": doc_id,
                            "field": field, "span": [found.start, found.end],
                            "as_written_in_the_record":
                                text[found.start:found.end]}
    return None


def _sentence_with(answer: str, phrase: str) -> str:
    from answer import cite
    for sentence in cite.split_sentences(answer):
        if phrase.casefold() in sentence.casefold():
            return sentence.strip()
    return ""


def audit(case_ids: list[str], sweeps: list[Path]) -> list[dict]:
    from answer import cite
    records = _records()
    rows: dict[str, list[dict]] = {}
    for path in sweeps:
        data = json.loads(path.read_text(encoding="utf-8"))
        for row in data.get("results", []):
            if not case_ids or row.get("case") in case_ids:
                rows.setdefault(row["case"], []).append(row)

    out: list[dict] = []
    for case_id in sorted(rows):
        runs = rows[case_id]
        passes = sum(1 for r in runs if r.get("content_ok"))
        labels: dict[str, int] = {}
        for run in runs:
            for label in run.get("failures", []):
                labels[label] = labels.get(label, 0) + 1
        findings: list[dict] = []
        for label, count in sorted(labels.items(), key=lambda kv: -kv[1]):
            entry = {"assertion": label, "failed_in": count, "of": len(runs)}
            excluded = _EXCLUDES.match(label)
            if excluded:
                phrase = excluded.group(1)
                entry["family"] = "exclusion"
                entry["phrase"] = phrase
                entry["in_context"] = sorted({
                    _sentence_with(r.get("answer", ""), phrase)
                    for r in runs if phrase.casefold()
                    in (r.get("answer") or "").casefold()} - {""})
            elif _QUOTE_DOC.match(label) or _QUOTE_MIN.match(label):
                entry["family"] = "quotation"
                seen: dict[str, dict | None] = {}
                for run in runs:
                    for quote in cite.extract_quotes(run.get("answer") or ""):
                        if quote not in seen:
                            seen[quote] = locate_on_ladder(quote, records)
                entry["quotations"] = [
                    {"quoted": q, **(found or {"rung": None})}
                    for q, found in seen.items()]
            else:
                entry["family"] = "content"
            findings.append(entry)
        out.append({"case": case_id, "runs": len(runs), "passes": passes,
                    "deterministic": passes in (0, len(runs)),
                    "findings": findings})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Block F decision 3 — re-read the archived answers against "
                    "the assertions that failed them. No chat calls.")
    parser.add_argument("--case", action="append", dest="cases")
    parser.add_argument("--all-failing", action="store_true",
                        help="every case that failed at least once, not only "
                             "the four BLOCK_F_START names")
    parser.add_argument("--sweep", action="append", dest="sweeps",
                        help="archive filenames; defaults to the four Block E "
                             "sweeps, which are the only ones with 33 cases")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.sweeps:
        sweeps = [SWEEP_DIR / name for name in args.sweeps]
    else:
        sweeps = sorted(SWEEP_DIR.glob("2026082[678]T*.json"))
    missing = [p.name for p in sweeps if not p.exists()]
    if missing:
        print(f"no such sweep archive: {', '.join(missing)}", file=sys.stderr)
        return 2
    if not sweeps:
        print("no sweep archives matched", file=sys.stderr)
        return 2

    wanted = args.cases or ([] if args.all_failing else NAMED)
    report = audit(wanted, sweeps)
    if args.all_failing:
        report = [r for r in report if r["passes"] < r["runs"]]

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    print(f"{len(sweeps)} archive(s): {', '.join(p.name for p in sweeps)}")
    print("no chat call is made by this script\n")
    for case in report:
        print("=" * 72)
        head = (f"{case['case']}   {case['passes']}/{case['runs']}")
        if case["deterministic"]:
            head += "   deterministic across every archived run"
        print(head)
        for finding in case["findings"]:
            print(f"\n  FAILED {finding['failed_in']}/{finding['of']}  "
                  f"{finding['assertion']}")
            if finding["family"] == "exclusion":
                print("    an exclusion is a bare substring test. It cannot "
                      "tell a claim from a\n    refusal to make it. Every "
                      "sentence the phrase appears in:")
                for sentence in finding["in_context"] or ["(not found)"]:
                    print(f"      - {sentence}")
            elif finding["family"] == "quotation":
                for quoted in finding["quotations"]:
                    if quoted.get("rung") is None:
                        print(f"    NOT IN THE CORPUS on any rung: "
                              f"{quoted['quoted'][:90]!r}")
                    elif quoted["rung"] == "as written":
                        print(f"    resolves ({quoted['match']}) in "
                              f"{quoted['doc']}.{quoted['field']}: "
                              f"{quoted['quoted'][:70]!r}")
                    else:
                        print(f"    NEAR MISS — {quoted['rung']}")
                        print(f"      answer: {quoted['quoted'][:100]!r}")
                        print(f"      record: "
                              f"{quoted['as_written_in_the_record'][:100]!r}")
                        print(f"      in {quoted['doc']}.{quoted['field']}, "
                              f"match {quoted['match']}")
    print("\n" + "=" * 72)
    print("A rung is a measurement, not a verdict. Adding a tolerance to the\n"
          "resolver changes what this project claims a quotation IS, and that\n"
          "is a ruling — see the punctuation-tolerance note in\n"
          "scripts/mutate_part8.py for why loosening a matcher is not kindness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
