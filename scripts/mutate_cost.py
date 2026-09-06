"""Mutation-verify the F2 curation-cost guards.

Same standard as `mutate_part8.py`, `mutate_part7b.py`, `mutate_places.py`,
`mutate_recover.py` and `mutate_fidelity.py`: each mutation breaks exactly one
rule and asserts that the guard protecting THAT rule reports FAIL -- not merely
that something failed. A guard that has never been seen to fail is not known to
work, and this ledger is the only instrument Block F has for the number kill
trigger 3 hangs off.

Built WITH the BASELINE check, like `mutate_fidelity.py` and unlike the three
that still lack it. F1's owed list records the count each time: the check is in
four harnesses of seven, and shipping an eighth without it would have made that
five.

Run: python scripts/mutate_cost.py
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys

# FINDING 10: this process's own stdout. Through a pipe or a redirect on
# Windows it falls back to the locale codec, which cannot encode Greek, Tamil,
# Chinese, Ge'ez or runic, and it raises mid-output with the file half written
# and every number in it correct. errors="replace" is deliberate: a mangled
# character is cosmetic, a lost run is not.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
# FINDING 16, and FINDING 10's other two boundaries: the CHILD's stdout encoding,
# and no bytecode cache for the child to read a stale mutation out of.
CHILD_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8",
             "PYTHONDONTWRITEBYTECODE": "1"}
COST = ROOT / "ingest" / "cost.py"
SOURCES = (COST,)
SUITE = ["-B", "-m", "ingest.test_cost"]


def _purge_bytecode() -> None:
    """FINDING 16. `-B` stops the child WRITING a cache; it does not stop it
    reading one an ordinary run left behind. Both, always."""
    for source in SOURCES:
        shutil.rmtree(source.parent / "__pycache__", ignore_errors=True)


# Ruling 52's retired-row phase check, which is two statements and cannot be
# anchored on one line: the same _check_record_entry call appears in the
# `records` loop above it, and a target occurring twice resolves
# first-occurrence-wins in silence.
# RE-ANCHORED IN F4. This anchor is SOURCE TEXT, so it moves whenever the source
# does: ruling 59 inserted its reinstatement block between the phase check and
# `in_corpus`, and this mutation reported `MISS ... (target not found)` on the
# next run. That is the harness working -- an anchor that no longer matches is
# reported, never silently skipped -- and it is the standing cost of a harness
# that patches text rather than behaviour. The line it removes is unchanged;
# only the context that makes it unique has moved.
PHASE_CHECK = (
    "        problems.extend(_check_record_entry(entry, where, max_span))\n"
    "\n"
    "    # RULING 59, F4, 2026-08-31."
)

MUTATIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        'the declared phase list is compared as a SET, so order stops mattering',
        [
            ('    if list(names) != list(PHASES):',
             '    if set(names) != set(PHASES):'),
        ],
    ),
    (
        'the declared phase list is not compared to PHASES at all',
        [
            ('    if list(names) != list(PHASES):',
             '    if False:'),
        ],
    ),
    (
        'a phase may be declared with no definition',
        [
            ('        if not str(declared.get(name, "") or "").strip():',
             '        if False:'),
        ],
    ),
    (
        'the comparator may be evaluated against anything',
        [
            ('    if against != "within_tranche":',
             '    if False:'),
        ],
    ),
    (
        'the comparator need not say why record 12 is unavailable',
        [
            ('    if not str(comparator.get("why_not_record_12", "") or "").strip():',
             '    if False:'),
        ],
    ),
    (
        'a seed record may be named as a cost baseline',
        [
            ('    if named_seed or comparator.get("baseline_record"):',
             '    if False:'),
        ],
    ),
    (
        'the comparator need not carry the n per tier',
        [
            ('    if not isinstance(floor, dict) or not floor:',
             '    if False:'),
        ],
    ),
    (
        'a record entry may omit a phase',
        [
            ('    missing = [p for p in PHASES if p not in phases]',
             '    missing = []'),
        ],
    ),
    (
        'a record entry may invent a phase',
        [
            ('    unknown = [p for p in phases if p not in PHASES]',
             '    unknown = []'),
        ],
    ),
    (
        'a non-numeric minutes value is read as zero instead of refused',
        [
            ('        return None\n    return float(value)',
             '        return 0.0\n    return float(value)'),
        ],
    ),
    (
        'negative minutes are allowed',
        [
            ('        if minutes < 0:',
             '        if False:'),
        ],
    ),
    (
        'provenance stops being a closed vocabulary',
        [
            ('        if provenance not in PROVENANCES:',
             '        if False:'),
        ],
    ),
    (
        'an estimate may be recorded with no written reason',
        [
            ('        if provenance == "estimated" and not str(cell.get("because", "") or "").strip():',
             '        if False:'),
        ],
    ),
    (
        'a measured span of any length is accepted',
        [
            ('        if provenance == "measured" and minutes > max_span:',
             '        if False:'),
        ],
    ),
    (
        'curated_on stops having to be a date',
        [
            ('    if not _ISO_DATE.match(str(entry.get("curated_on", "") or "")):',
             '    if False:'),
        ],
    ),
    (
        'a record may be timed twice',
        [
            ('        if rid in timed:',
             '        if False:'),
        ],
    ),
    (
        'the ledger tier is no longer checked against the derived one',
        [
            ('            if declared != got:',
             '            if False:'),
        ],
    ),
    (
        'a corpus record may be in neither records nor not_timed',
        [
            ('    uncovered = sorted(corpus - set(timed) - set(not_timed))',
             '    uncovered = []'),
        ],
    ),
    (
        'a ledger row may name a record that is not in the corpus',
        [
            ('    stale = sorted((set(timed) | set(not_timed)) - corpus)',
             '    stale = []'),
        ],
    ),
    (
        'a record may be both timed and excused',
        [
            ('    both = sorted(set(timed) & set(not_timed))',
             '    both = []'),
        ],
    ),
    (
        'a record may be excused from timing with no reason',
        [
            ('        if not str(reason or "").strip():',
             '        if False:'),
        ],
    ),
    (
        'a ledger may omit a required term',
        [
            ('    missing_terms = LEDGER_REQUIRED - set(ledger)',
             '    missing_terms = set()'),
        ],
    ),
    (
        'a clock left running is no longer reported',
        [
            ('    open_entry = ledger.get("open_entry")\n    if open_entry:',
             '    open_entry = ledger.get("open_entry")\n    if False:'),
        ],
    ),
    (
        'an open clock may name a phase that does not exist',
        [
            ('            if phase and phase not in PHASES:',
             '            if False:'),
        ],
    ),
    (
        'an open clock may start at a time that is not a stamp',
        [
            ('            if started and not _ISO_STAMP.match(started):',
             '            if False:'),
        ],
    ),
    (
        'a trend is drawn through a tier below the declared floor',
        [
            ('    if n < min_n:',
             '    if False:'),
        ],
    ),
    (
        'the halves stop being halves',
        [
            ('    half = n // 2',
             '    half = 1'),
        ],
    ),
    (
        'the direction of the trend stops being computed',
        [
            ('    direction = "down" if b < a else ("up" if b > a else "flat")',
             '    direction = "flat"'),
        ],
    ),
    (
        'an unmet mix no longer blocks the cost claim',
        [
            ('    if short:\n        return (\n            "NOT YET A COST CLAIM',
             '    if False:\n        return (\n            "NOT YET A COST CLAIM'),
        ],
    ),
    (
        'a met mix is read as unmet',
        [
            ('        if by_tier.get(tier, {}).get("n", 0) < int(target)',
             '        if by_tier.get(tier, {}).get("n", 0) <= int(target)'),
        ],
    ),
    (
        'an empty column prints a table instead of saying it is empty',
        [
            ('    if not timed:',
             '    if False:'),
        ],
    ),
    (
        'a report with no declared mix claims the mix is met',
        [
            ('    if not at_60:',
             '    if False:'),
        ],
    ),
    (
        'the measured/estimated split stops being printed',
        [
            ('            f"estimated ({share:.0f}% remembered)"',
             '            f"estimated"'),
        ],
    ),
    (
        'the per-phase decomposition loses its minutes',
        [
            ('            f"{name} {bucket[\'by_phase\'][name]:.0f}"',
             '            f"{name}"'),
        ],
    ),
    (
        'a record total stops summing every phase',
        [
            ('    total = 0.0\n    for name in PHASES:',
             '    total = 0.0\n    for name in PHASES[:1]:'),
        ],
    ),
    (
        "a tier's records stop being ordered by curation date",
        [
            ('        bucket["rows"].sort(\n            key=lambda e: (str(e.get("curated_on", "")), str(e.get("record_id", "")))\n        )',
             '        bucket["rows"].sort(key=lambda e: 0)'),
        ],
    ),
    (
        'every record is pooled into one tier',
        [
            ('        tier = str(entry.get("tier", "") or "unknown")',
             '        tier = "unknown"'),
        ],
    ),
    # Ruling 52, F3. Retirement, one branch at a time.
    (
        "a row may be retired even though its record is in the corpus",
        [("    if in_corpus:", "    if False:")],
    ),
    (
        "a retirement no longer needs a written reason",
        [('        if not str(entry.get("because", "") or "").strip():',
          "        if False:")],
    ),
    (
        "retired_on stops having to be a date",
        [('        if not _ISO_DATE.match(str(entry.get("retired_on", "") or "")):',
          "        if False:")],
    ),
    (
        "a record may be retired twice",
        [("        if rid in retired_ids:", "        if False:")],
    ),
    (
        "a record may be retired and excused at once",
        [("    if clash:", "    if False:")],
    ),
    (
        "a retired row's phases stop being checked",
        [(PHASE_CHECK, "\n    # RULING 59, F4, 2026-08-31.")],
    ),
    (
        "a retired term that is not a list is iterated anyway",
        [("    if not isinstance(retired, list):", "    if False:")],
    ),
    (
        "a retired row is subtracted rather than named",
        [("    if retired:", "    if False:")],
    ),
    (
        "the retirement's written reason stops being printed",
        [("""            lines.append(f"      {entry.get('because', '')}")""",
          """            pass""")],
    ),
    (
        "the report stops saying a retired row is in no mean",
        # RE-ANCHORED IN F4: ruling 59 split the retirement block in the
        # report into retired rows and reinstated rows, and the sentence moved
        # onto a different line.
        [('f"named here, counted in NO mean below.")', 'f"named here.")')],
    ),
    (
        "the ledger no longer has to carry a retired list",
        [('    "retired",\n    "not_timed",', '    "not_timed",')],
    ),
    (
        # RULING 59, F4. The exemption removed: a reinstated row is refused
        # again the moment its record exists, which is the state that made the
        # ledger permanently red and gave nobody a way back.
        "a reinstated row is not exempt from the retirement checks",
        [("""    reinstated = {rid for rid, e in retired_ids.items()
                  if str(e.get("reinstated_on") or "").strip()}""",
          """    reinstated = set()""")],
    ),
    (
        # The anti-loophole itself. Without this clause, retire an expensive
        # record, declare it reinstated, file nothing, and the minutes are out
        # of every mean with every check green.
        "a reinstated row no longer has to have its minutes filed anywhere",
        [("""        if rid not in set(timed):""", """        if False:""")],
    ),
    (
        "a reinstatement no longer needs a written reason",
        [("""        if not str(entry.get("reinstated_because") or "").strip():""",
          """        if False:""")],
    ),
    # --------------------------------------------------------------------
    # The agent field (FINDING 70, closed in F6). Added 2026-09-06, in the
    # session AFTER the one that closed the finding -- which shipped the field,
    # its date rule and trend_line's refusal with no assertion in this suite and
    # no mutation here, and all 51 existing mutations passed straight through
    # the new branch because their fixtures carry no agents at all.
    # --------------------------------------------------------------------
    (
        'an agent outside the vocabulary is admitted',
        [
            ('        elif agent not in AGENTS:',
             '        elif False:'),
        ],
    ),
    (
        'a new entry may omit the agent entirely',
        [
            ('            if str(entry.get("curated_on", "") or "") >= AGENT_REQUIRED_FROM:',
             '            if False:'),
        ],
    ),
    (
        'a new entry may answer `unrecorded` to a question it could answer',
        [
            ('        elif agent == "unrecorded" and str(\n'
             '                entry.get("curated_on", "") or "") >= AGENT_REQUIRED_FROM:',
             '        elif False:'),
        ],
    ),
    (
        'a trend is drawn straight through two agents',
        [
            ('    if len(mixed) > 1:',
             '    if len(mixed) > 99:'),
        ],
    ),
    (
        "a phase's minutes stop being attributed to the agent that phase names",
        [
            ('            bucket["by_agent"][agent] += minutes',
             '            bucket["by_agent"][agent] += 0'),
        ],
    ),
    (
        # CORRECTED 2026-09-06, after this mutation MISSED on its first run.
        # It patched the `not in AGENTS` fallback, which a phase with NO agent
        # never reaches: `str(cell.get("agent", "") or "unrecorded")` has
        # already made it `unrecorded`, and `unrecorded` IS in by_agent. The
        # mutation was pointing at the branch that catches an agent value the
        # ledger check would have refused upstream, so nothing it broke was
        # load-bearing. THE HARNESS WAS RIGHT AND THE MUTATION WAS WRONG, which
        # is the failure mode a MISS exists to report -- and it reported it on
        # a mutation written the same day as the guard.
        'minutes on a phase with no agent are dropped rather than counted unrecorded',
        [
            ('            bucket["by_agent"][agent] += minutes',
             '            if cell.get("agent"):\n'
             '                bucket["by_agent"][agent] += minutes'),
        ],
    ),
    (
        'the report stops printing the by-agent split',
        [
            ("""        lines.append(f"    by agent: {agents or 'nothing recorded'}")""",
             '        lines.append("")'),
        ],
    ),
]
EXPECTED = [
    'GUARD a declared phase list in the wrong order is refused',
    'GUARD a declared phase list missing a phase is refused',
    'GUARD a phase with no written definition is refused',
    'GUARD a comparator evaluated against anything but within_tranche is refused',
    'GUARD a comparator that does not say why record 12 is unavailable is refused',
    'GUARD a comparator naming a seed record as a baseline is refused',
    'GUARD a comparator that does not carry the n per tier is refused',
    'GUARD a record entry that omits a phase is refused',
    'GUARD a record entry with a phase outside the vocabulary is refused',
    'GUARD minutes that are not a number are refused',
    'GUARD negative minutes are refused',
    'GUARD a provenance outside measured and estimated is refused',
    'GUARD an estimated figure with no written reason is refused',
    'GUARD a measured span above the declared limit is refused',
    'GUARD a curated_on that is not a date is refused',
    'GUARD a record timed twice is refused',
    'GUARD a ledger tier that disagrees with the derived tier is refused',
    'GUARD a corpus record that is neither timed nor excused is refused',
    'GUARD a ledger row naming a record that is not in the corpus is refused',
    'GUARD a record that is both timed and excused is refused',
    'GUARD a record excused from timing with no written reason is refused',
    'GUARD a ledger missing a required term is refused',
    'GUARD a clock left running is refused, because unattributed minutes leave the column',
    'GUARD an open clock on a phase outside the vocabulary is refused',
    'GUARD an open clock whose start is not an ISO UTC stamp is refused',
    'GUARD a tier below the declared floor is reported as NOT A TREND',
    'GUARD a tier at or above the floor is reported as first half against last half',
    'GUARD a planted downward trend is reported as down',
    'GUARD per-tier means are not a cost claim while the declared mix is unmet',
    'GUARD the report says the mix is met when the tranche has met it',
    'GUARD an empty column says so rather than printing a mean of nothing',
    'GUARD a report handed no target mix refuses to call anything a cost claim',
    'GUARD the report prints the measured/estimated split beside every mean',
    "GUARD the report decomposes a tier's minutes by phase",
    "GUARD a record's total is the sum of every phase it declares",
    "GUARD a tier's records are summarised in curation order, not file order",
    'GUARD records are counted under their own tier and not pooled',
    "GUARD retiring a row whose record IS in the corpus is refused -- otherwise retirement takes the expensive records out of the column",
    "GUARD a retirement with no written reason is refused",
    "GUARD a retired_on that is not a date is refused",
    "GUARD a record retired twice is refused",
    "GUARD a record that is retired and also excused is refused -- one record, one answer",
    "GUARD a retired row's phases are checked like any other row's",
    "GUARD a retired term that is not a list is refused",
    "GUARD the report NAMES a retired row rather than subtracting it",
    "GUARD the report prints the retirement's written reason",
    "GUARD the report says a retired row is in no mean, so a reader cannot take it for a timed record",
    "GUARD the required ledger terms are exactly the seven declared here, and a term removed from the set is refused rather than untested",
    # RULING 59, F4 -- in the order above.
    "GUARD a REINSTATED row whose record is in the corpus and whose minutes "
    "are filed against it reports nothing",
    "GUARD a reinstated row with nothing filed against it is refused -- "
    "otherwise reinstatement is retirement wearing a different word",
    "GUARD a reinstatement with no written reason is refused",
    # The agent field, F6. In the order of the mutations above.
    'GUARD an agent outside the vocabulary is refused',
    'GUARD a phase with no agent on an entry curated on or after 2026-09-06 is '
    'refused, because a model apportioning its own wall clock and a person '
    'timing themselves are two measurements',
    'GUARD `unrecorded` on a NEW entry is refused: that value is for entries '
    'written before the field existed, and on a new one it is a question that '
    'was answerable and was not answered',
    'GUARD a tier ABOVE the floor whose minutes come from more than one agent '
    'is refused a trend, not annotated with one -- FINDING 70',
    "GUARD summarise attributes each phase's minutes to the agent that phase "
    'names',
    'GUARD minutes on a phase with no agent are counted as `unrecorded` rather '
    'than dropped, because a total that quietly shrinks is worse than one that '
    'says it does not know',
    'GUARD the report prints the by-agent split beside the measured/estimated '
    'one, so the two kinds of doubt are two lines',
]

# NOT mutation-verified from this source, and said so rather than left to be
# noticed. These are the POSITIVE controls -- the assertions that a well-formed
# ledger, a well-formed comparator and the file on disk are ACCEPTED. A
# mutation here makes a check laxer, and a laxer check does not fail an
# acceptance; what would break them is a check made stricter, which is a
# different harness and a different day. They are listed because a guard with
# no mutation beside it is otherwise indistinguishable from one whose mutation
# was forgotten.
UNMUTATED_BY_DESIGN = (
    'GUARD a corpus covered by timing and excusing together is accepted',
    'GUARD a well-formed ledger over a covered corpus reports no problem',
    'GUARD a within-tranche comparator with its n and its reason is '
    'accepted',
    'GUARD an estimated figure WITH a written reason is accepted',
    'GUARD the comparator on disk is the within-tranche one ruling 46 '
    'declared',
    'GUARD the declared phase vocabulary on disk is accepted',
    'GUARD the ledger on disk covers every record in the corpus on disk',
    "GUARD the phases declared on disk are this module's PHASES, in order",
    'GUARD `unrecorded` on an OLD entry is the truth rather than an '
    'omission, and is accepted',
    'GUARD a complete entry with an agent on every phase passes',
    'GUARD a ledger with nothing retired prints no retirement block',
    'GUARD a retired row naming a record that is not in the corpus is '
    'accepted, and is NOT counted as a stale row',
    'GUARD an entry curated BEFORE the field existed is not refused '
    'for lacking it -- the debt is dated, not retrospective',
    'GUARD every agent this module accepts is DEFINED, and no agent '
    'is defined that the code would refuse',
    'GUARD no seed record ever acquires a minutes figure, because a '
    'reconstructed baseline is what ruling 46 refuses',
    'GUARD one agent above the floor still gets its trend, and the '
    'planted downward trend is still read as down -- the refusal is '
    'about MIXING agents and not about having one',
    'GUARD the excused list is FROZEN at the seed records the tier '
    'declaration counts -- a record excused after the column opened '
    'is the column being routed around',
    'GUARD the refusal names the agents and their minutes, because a '
    'refusal that does not say what it saw is a number withheld',
    'GUARD the refusal says the tier is above the floor, so a reader '
    'cannot mistake it for the small-n refusal',
)

# UNMUTATED AND OWED, which is a different thing and is kept in a different
# list. These are REFUSAL guards -- checks that reject a malformed input --
# and a refusal guard with no mutation beside it has never been seen to fail.
# They are printed as a debt on every run rather than absorbed into the list
# above, because `by design` is a claim and these are simply not done yet.
UNMUTATED_AND_OWED = (
    'GUARD a reinstated_on that is not a date is refused',
)

def failures_from(output: str) -> set[str]:
    # THE SPACE, and this harness is LIVE, not latent. FINDING 37 found the
    # defect in scripts/mutate_places.py; FINDING 46 went looking for its
    # siblings and enumerated four harnesses by name. This is the fifth, it was
    # not on that list, and `ingest/test_cost.py` ends a red run with
    # `FAILED (n)` -- so a bare startswith("FAIL") harvested a phantom guard
    # named `ED (n)` into this harness's BASELINE block, which would report the
    # ledger suite as partly red while it was green. FINDING 58.
    return {
        line.split("FAIL ", 1)[1].strip()
        for line in output.splitlines()
        if line.strip().startswith("FAIL ")
    }



def ok_labels_from(output: str) -> set:
    """Every guard the suite REPORTED PASSING, harvested the same way
    `failures_from` harvests the failing ones and with the same space."""
    return {
        line.split("ok   ", 1)[1].strip()
        for line in output.splitlines()
        if line.strip().startswith("ok   ")
    }


def coverage_problems(guard_labels: set) -> "list[str]":
    """Is every guard in this suite accounted for? Added F6, 2026-09-06.

    THIS EXISTS BECAUSE THE LISTS WENT WRONG THE FIRST TIME ANYBODY CHECKED
    THEM. UNMUTATED_BY_DESIGN's own comment says the names are listed "because a
    guard with no mutation beside it is otherwise indistinguishable from one
    whose mutation was forgotten" -- and nothing compared the list to the suite,
    so a guard added later was exactly indistinguishable. On 2026-09-06 the two
    harnesses between them held 12 guards in NEITHER list and one name that the
    suite no longer printed at all.

    FINDING 10's lesson, one harness over: a hand-written enumeration of things
    to check was wrong four times in one afternoon, and the fix was to assert
    the RULE instead of maintaining the list. The rule here is that every guard
    is either mutated, listed as an acceptance that a laxer check cannot fail,
    or listed as owed -- and that no list names a guard the suite does not
    print.
    """
    problems: list[str] = []
    covered = set(EXPECTED) | set(UNMUTATED_BY_DESIGN) | set(UNMUTATED_AND_OWED)
    unwatched = sorted(guard_labels - covered)
    if unwatched:
        problems.append(
            f"{len(unwatched)} guard(s) are in NO list -- neither mutated, nor "
            f"declared an acceptance, nor declared owed. A guard nothing has "
            f"been seen to fail is not known to work: "
            + "; ".join(g[:70] for g in unwatched)
        )
    stale = sorted(covered - guard_labels)
    if stale:
        problems.append(
            f"{len(stale)} listed name(s) are not printed by the suite at all, "
            f"so the list is describing a guard that no longer exists: "
            + "; ".join(g[:70] for g in stale)
        )
    return problems

def _newline_of(raw: bytes) -> str:
    """The file's own line ending, so a mutation run does not change it."""
    crlf = raw.count(b"\r\n")
    if crlf and raw.count(b"\n") - crlf:
        raise SystemExit(
            "a mutation source has MIXED line endings. Resolve that by hand "
            "before running this harness, which would otherwise pick one."
        )
    return "\r\n" if crlf else "\n"


def _write(path: pathlib.Path, text: str, newline: str) -> None:
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def main() -> int:
    if len(MUTATIONS) != len(EXPECTED):
        print(f"{len(MUTATIONS)} mutations against {len(EXPECTED)} expectations")
        return 1

    # BYTES on the way out, whatever the harness did on the way in. On
    # 2026-08-28 mutate_ui_places converted ui/build_ui_data.py from LF to CRLF
    # on a live run, its text-comparing restore check could not see it, and the
    # conversion reached a commit. 168 archived citation spans point into the
    # corpus by exact offset.
    original_bytes = {f: f.read_bytes() for f in SOURCES}
    newlines = {f: _newline_of(original_bytes[f]) for f in SOURCES}
    originals = {
        f: original_bytes[f].decode("utf-8").replace("\r\n", "\n")
        for f in SOURCES
    }
    problems: list[str] = []
    try:
        # THE BASELINE. A mutation is verified by naming a guard and checking
        # the guard FAILS once the code is broken -- which is only evidence if
        # the guard was PASSING beforehand. A green mutation against a red
        # baseline is a vacuous proof, and on 2026-08-28 one happened inside
        # the instrument built to catch vacuous proofs.
        _purge_bytecode()
        _baseline = subprocess.run(
            [sys.executable, *SUITE], cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=CHILD_ENV,
        )
        already_failing = failures_from(_baseline.stdout)
        if already_failing:
            print(f"  BASELINE: {len(already_failing)} check(s) already fail "
                  f"with NO mutation applied. Any mutation naming one of\n"
                  f"            them cannot be verified by this run.")
            for name in sorted(already_failing):
                print(f"            - {name}")
            print()


        # Coverage, before any mutation is applied. F6.
        for problem in coverage_problems(ok_labels_from(_baseline.stdout)):
            problems.append(problem)
            print(f"  COVERAGE {problem[:100]}")
        if UNMUTATED_AND_OWED:
            print(f"  {len(UNMUTATED_AND_OWED)} refusal guard(s) are UNMUTATED "
                  f"AND OWED, listed in UNMUTATED_AND_OWED:")
            for name in UNMUTATED_AND_OWED:
                print(f"            - {name[:100]}")
            print()
        for (label, patches), guard in zip(MUTATIONS, EXPECTED):
            if guard in already_failing:
                problems.append(
                    f"{label}: UNVERIFIED - its guard {guard!r} was already "
                    f"failing before any mutation was applied, so this "
                    f"mutation proves nothing. Fix the suite, then re-run."
                )
                print(f"  UNVERIFIED {label} (its guard was already red at baseline)")
                continue

            edited = {f: originals[f] for f in SOURCES}
            missing = [
                old for old, _ in patches
                if not any(old in originals[f] for f in SOURCES)
            ]
            if missing:
                problems.append(f"{label}: mutation target not found")
                print(f"  MISS {label} (target not found)")
                continue

            # A target occurring more than once resolves first-source-wins and
            # then first-occurrence-wins, both in silence. It bit on the day the
            # check was written, in this repository, and left a guard unwatched
            # while the harness reported only that it had not failed.
            ambiguous = [
                (old, sum(originals[f].count(old) for f in SOURCES))
                for old, _ in patches
            ]
            ambiguous = [(old, n) for old, n in ambiguous if n > 1]
            if ambiguous:
                problems.append(
                    f"{label}: mutation target is AMBIGUOUS - "
                    + "; ".join(
                        f"{n} occurrences of "
                        f"{old.splitlines()[0].strip()[:60]!r}"
                        for old, n in ambiguous
                    )
                    + ". The first is chosen silently, so this mutation may be "
                      "pointing at code it was not written for. Anchor it with "
                      "surrounding lines until it is unique."
                )
                print(f"  MISS {label} (ambiguous target)")
                continue

            for old, new in patches:
                target = next(f for f in SOURCES if old in edited[f])
                edited[target] = edited[target].replace(old, new, 1)
            for f in SOURCES:
                _write(f, edited[f], newlines[f])

            _purge_bytecode()
            result = subprocess.run(
                [sys.executable, *SUITE], cwd=ROOT, capture_output=True, text=True,
                encoding="utf-8", errors="replace", env=CHILD_ENV,
            )
            failed = failures_from(result.stdout)
            if guard in failed:
                print(f"  ok   {label}")
                print(f"       -> {guard}")
            elif result.returncode != 0 and not failed:
                # A crash is not a guard firing. test_embed.py spent two days
                # crashing where it should have been asserting.
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
            f.write_bytes(original_bytes[f])

    unrestored = [f.name for f in SOURCES if f.read_bytes() != original_bytes[f]]
    if unrestored:
        problems.append(
            "sources were NOT restored cleanly: " + ", ".join(unrestored)
            + " - restore from version control before running anything else"
        )

    _purge_bytecode()
    check = subprocess.run(
        [sys.executable, *SUITE], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=CHILD_ENV,
    )
    if check.returncode != 0:
        problems.append(
            "sources restored, but `ingest.test_fidelity` fails on its own "
            "account - a finding about the suite, not about this harness"
        )
        print("\n--- ingest.test_fidelity output, so it is not lost ---")
        print((check.stdout or "") + (check.stderr or ""), end="")
        print("--- end ---")

    print()
    print(f"  {len(UNMUTATED_BY_DESIGN)} guard(s) are not mutated from this "
          f"source, by design and listed in UNMUTATED_BY_DESIGN.")
    if problems:
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"all {len(MUTATIONS)} mutations verified; sources restored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
