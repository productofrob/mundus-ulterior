"""The Block F curation-cost ledger, as rules rather than as a spreadsheet.

Nothing here runs. `ingest/cost_log.py` is the CLI that writes the ledger and
`ingest/verify.py` check 13 is what refuses a corpus the ledger does not cover.
This module imports nothing from the package -- `ingest/fidelity.py`'s one
useful property, kept on purpose: the rules can be tested without a corpus, a
database or a network.

Three things this file exists to make impossible, all three of them named in
F2_START before a single minute was recorded:

1. **A single minutes figure per record.** It is gameable by re-labelling
   work: cost "trends down" the moment source-hunting or rights checking stops
   being counted as curation. Ruling 47 divides the minutes into seven phases
   and this module refuses a record entry that omits one. A phase that went to
   zero has to SAY zero, so the number falls in the phase that stopped rather
   than in the total that nobody can decompose.

2. **A cost claim read across a shifting mix.** Ruling 45, declared in F1
   before this column existed: cost is reported PER TIER and beside the
   declared target mix, because a mean over a mix that is moving cannot tell
   "the same kind of record got cheaper" from "we made more of the cheap kind".

3. **A comparator chosen after the numbers are in.** Ruling 46. Kill trigger 3
   as written compares record 60 against record 12 and NOTHING ANYWHERE
   RECORDS WHAT RECORD 12 COST. The comparator is declared in the ledger, it
   is within-tranche, and `check_comparator` refuses a comparator that claims
   a seed-record baseline.
"""

from __future__ import annotations

import re

# --------------------------------------------------------------------------
# Ruling 47: the phases, fixed before the first record was timed
# --------------------------------------------------------------------------

# The order is the order the work happens in, and the report prints them in it.
# `rework` is last because it is not a stage: it is what a failed verify sends
# back, and it is separated so that a tranche which got faster by getting
# sloppier shows up as rework rising rather than as the total falling.
PHASES = (
    "source_hunting",
    "rights_and_licence",
    "text_capture",
    "translation_and_fidelity",
    "placement",
    "authoring",
    "rework",
)

# Held here as well as in data/curation_cost.json for the reason ruling 43
# gives about the tier vocabulary: a definition that lives only in the data
# file is a definition the next curator gets to renegotiate, and the whole
# point of fixing the phases on day one is that record 25 and record 60 are
# divided the same way.
PHASE_DEFINITIONS = {
    "source_hunting": (
        "Finding a candidate source and deciding it is one. Searching "
        "institutional catalogues, corpora and scholarship; reading enough to "
        "know the text exists in a usable form; rejecting the ones that do not."
    ),
    "rights_and_licence": (
        "Establishing that the text and any translation can be quoted and "
        "cited, and recording where that permission comes from. Counted "
        "separately from source_hunting because it is the phase most easily "
        "dropped without anyone noticing it has been."
    ),
    "text_capture": (
        "Getting the source's own characters onto disk correctly: "
        "transcription or transfer, script and diacritics, normalisation, "
        "and checking the result against the page it came from."
    ),
    "translation_and_fidelity": (
        "The English side and its honesty: locating or commissioning a "
        "translation, citing it, deciding the text_fidelity labels, and "
        "settling the record's tier."
    ),
    "placement": (
        "W1 placement -- gazetteer lookup, ids, contested placements, or the "
        "written reason a record has none."
    ),
    "authoring": (
        "Writing the record JSON, chunking it, and writing whatever gold "
        "cases it carries. Gold-case writing is inside curation and not "
        "beside it: a record curated without the case that tests it is a "
        "record the sweep cannot see."
    ),
    "rework": (
        "Everything a failed check sent back: a red ingest.verify, a "
        "declared-vs-derived tier disagreement, a ranking regression traced "
        "to this record. Not a stage. It is the phase that tells you a "
        "tranche got faster by getting sloppier."
    ),
}

# `measured` is a clock this repository started and stopped. `estimated` is
# somebody remembering. Ruling 48, and it is ruling 36's shape one level down:
# recorded and reconstructed are two kinds of knowledge and must be REPORTED
# as two. The report prints the split, so a trend computed mostly out of
# recollection cannot be read as a measurement of anything.
PROVENANCES = ("measured", "estimated")

# FINDING 70, F5 Part 3 -- closed in F6, 2026-09-06, in the shape that finding
# asked for: "An `agent` field per phase, or per record, is the obvious shape
# and this session did not add one ... F6's, with the evidence already in the
# file." PER PHASE, because per record cannot say what records 37 to 40 are:
# one phase of seven is a human's self-reported minutes and five are a model's
# wall clock apportioned by judgement. A per-record field would have to pick
# one of those and would pick the flattering one.
#
# `unrecorded` IS A VALUE AND NOT AN ABSENCE, for LEDGER_REQUIRED's reason one
# level down: a missing field and a field that says nothing are the same shape
# on disk, and the first is how sixteen entries silently become whatever the
# reader assumes. Every entry written before 2026-09-06 reads as `unrecorded`
# unless F5 Part 3 wrote down who held the clock, and five of them did.
AGENTS = ("curator", "model", "curator_and_model", "unrecorded")

AGENT_DEFINITIONS = {
    "curator": "A person timed themselves. Records 25 to 35's assumption, and "
               "it is NOT backfilled onto them: nothing in the ledger states "
               "it, and writing it in now would be this module inventing the "
               "evidence it exists to check.",
    "model": "Model wall clock, apportioned across phases by judgement. It is "
             "smaller and smoother than a human timing themselves and it is "
             "not the same measurement.",
    "curator_and_model": "Both, inseparably, within one phase. Named rather "
                         "than split, because a split nobody measured is an "
                         "estimate wearing a measurement's shape.",
    "unrecorded": "The ledger did not carry this field when the entry was "
                  "written and no document says who held the clock. NEVER "
                  "read as `curator`.",
}

# Entries curated on or after this date must say. Before it, the field did not
# exist and `unrecorded` is the truth rather than an omission. A date and not a
# record count, because the ledger is in curation order and a count would move
# every time a row is retired.
AGENT_REQUIRED_FROM = "2026-09-06"

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_ISO_STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")

# The keys a ledger must declare. Required rather than optional-with-a-default
# for `load_floor`'s stated reason: a default is a threshold in Python by
# another route, and the one term here that is a threshold -- the n below
# which a per-tier mean is not a trend -- is exactly the term somebody would
# quietly lower at G3.
LEDGER_REQUIRED = {
    "phases",
    "comparator",
    "records",
    # Ruling 52, F3. A row whose record will never exist, kept rather than
    # deleted. Required, not optional: a ledger without the list is a ledger
    # where a retirement has nowhere to be recorded, and the first one would
    # then be a hand edit.
    "retired",
    "not_timed",
    "min_n_to_read_as_a_trend",
    "max_measured_span_minutes",
}


def check_phase_vocabulary(declared: "dict") -> "list[str]":
    """The ledger's declared phases are exactly PHASES, each with a definition."""
    problems: list[str] = []
    names = list(declared or {})
    if list(names) != list(PHASES):
        problems.append(
            f"declared phases {names} are not this module's PHASES {list(PHASES)}, "
            f"in order. The phases are fixed before the first record is timed "
            f"(ruling 47) and nobody times a record twice, so a phase added "
            f"later is a phase every earlier record is missing."
        )
    for name in names:
        if not str(declared.get(name, "") or "").strip():
            problems.append(
                f"phase {name!r} has no written definition. An undefined phase "
                f"is a phase two curators divide differently."
            )
    return problems


def check_comparator(comparator: "dict", seed_record_ids: "set[str]") -> "list[str]":
    """Ruling 46. What kill trigger 3 is evaluated against, declared in advance.

    The trigger as written -- *"if record 60 costs what record 12 cost, 200 is
    a staffing question rather than an engineering one"* -- cannot be
    evaluated, because no minutes figure exists for record 12 or for any other
    seed record and none can be reconstructed. The only trend Block F can
    measure is within records 25 to 60, per tier. That is a weaker claim, it
    is declared here BEFORE the first number, and this function refuses the
    two ways it could quietly become a stronger one:

      * a comparator naming a seed record, which would be a baseline nobody
        measured;
      * `evaluated_against` set to anything but `within_tranche`, which is the
        only thing there is evidence for.

    Ruling 39's argument for the third time in this block: a comparator chosen
    after the numbers are in is a comparator fitted to them.
    """
    problems: list[str] = []
    comparator = comparator or {}

    against = str(comparator.get("evaluated_against", "") or "").strip()
    if against != "within_tranche":
        problems.append(
            f"comparator.evaluated_against is {against!r}. Ruling 46 declares "
            f"'within_tranche' and there is evidence for nothing else: the "
            f"seed 24 were curated before any column existed."
        )

    if not str(comparator.get("why_not_record_12", "") or "").strip():
        problems.append(
            "comparator.why_not_record_12 is empty. The gap between the "
            "trigger as written and the trigger as evaluable is the single "
            "most important sentence in this file, and a gap recorded nowhere "
            "is a gap G3 rediscovers as a surprise."
        )

    named_seed = sorted(
        rid for rid in seed_record_ids
        if rid in str(comparator.get("baseline", "") or "")
    )
    if named_seed or comparator.get("baseline_record"):
        problems.append(
            f"the comparator names a seed record as a baseline "
            f"({named_seed or comparator.get('baseline_record')!r}). No seed "
            f"record has a minutes figure. A baseline reconstructed now would "
            f"be produced by the people who want the trend to be downward."
        )

    floor = comparator.get("n_per_tier_at_60")
    if not isinstance(floor, dict) or not floor:
        problems.append(
            "comparator.n_per_tier_at_60 is missing. The tranche is 14 / 10 / "
            "4 / 8 records per tier and a trend over eight is not a "
            "measurement anyone should stake 200 on. The n travels with the "
            "claim or the claim travels alone."
        )
    return problems


def _as_minutes(value) -> "float | None":
    """The value if it is a number, and None if it is not. `bool` is not.

    Split out so a mutation of the numeric guard cannot make the checker
    CRASH on a string instead of failing on it. A harness that reads a crash
    as a guard firing is a harness that would have passed while the guard did
    nothing -- test_embed.py spent two days crashing where it should have been
    asserting.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _check_record_entry(entry: "dict", where: str, max_span: float) -> "list[str]":
    problems: list[str] = []

    if not _ISO_DATE.match(str(entry.get("curated_on", "") or "")):
        problems.append(f"{where}: curated_on is not a YYYY-MM-DD date")

    phases = entry.get("phases")
    if not isinstance(phases, dict):
        problems.append(f"{where}: phases is not an object")
        return problems

    missing = [p for p in PHASES if p not in phases]
    if missing:
        problems.append(
            f"{where}: no entry for phase(s) {missing}. A phase that went to "
            f"zero has to SAY zero: an absent phase and an unrecorded phase "
            f"are the same shape on disk, and the second is how a total falls "
            f"without any work getting faster."
        )
    unknown = [p for p in phases if p not in PHASES]
    if unknown:
        problems.append(f"{where}: unknown phase(s) {sorted(unknown)}")

    for name in PHASES:
        cell = phases.get(name)
        if cell is None:
            continue
        if not isinstance(cell, dict):
            problems.append(f"{where}.{name}: not an object")
            continue
        minutes = _as_minutes(cell.get("minutes"))
        if minutes is None:
            problems.append(
                f"{where}.{name}: minutes {cell.get('minutes')!r} is not a number"
            )
            continue
        if minutes < 0:
            problems.append(f"{where}.{name}: minutes is negative")
        provenance = str(cell.get("provenance", "") or "")
        if provenance not in PROVENANCES:
            problems.append(
                f"{where}.{name}: provenance {provenance!r} is not one of "
                f"{list(PROVENANCES)}"
            )
            continue
        if provenance == "estimated" and not str(cell.get("because", "") or "").strip():
            problems.append(
                f"{where}.{name}: an estimated figure with no written reason. "
                f"An unexplained estimate is a measurement by tomorrow."
            )
        agent = str(cell.get("agent", "") or "")
        if not agent:
            if str(entry.get("curated_on", "") or "") >= AGENT_REQUIRED_FROM:
                problems.append(
                    f"{where}.{name}: no agent. FINDING 70 -- from "
                    f"{AGENT_REQUIRED_FROM} every phase says who was holding "
                    f"the clock, because a model apportioning its own wall "
                    f"clock and a person timing themselves are two "
                    f"measurements and the column carried one name for both."
                )
        elif agent not in AGENTS:
            problems.append(
                f"{where}.{name}: agent {agent!r} is not one of {list(AGENTS)}"
            )
        elif agent == "unrecorded" and str(
                entry.get("curated_on", "") or "") >= AGENT_REQUIRED_FROM:
            problems.append(
                f"{where}.{name}: agent is `unrecorded` on an entry curated on "
                f"or after {AGENT_REQUIRED_FROM}. That value is for entries "
                f"written before the field existed; on a new one it is a "
                f"question that was answerable and was not answered."
            )
        if provenance == "measured" and minutes > max_span:
            problems.append(
                f"{where}.{name}: {minutes} measured minutes is above the "
                f"{max_span}-minute span limit. A clock left running overnight "
                f"writes a working day into the one number kill trigger 3 "
                f"hangs off. Close it with an explicit estimate and a reason."
            )
    return problems


def check_ledger(
    ledger: "dict",
    derived_tiers: "dict[str, tuple[str, str]]",
) -> "list[str]":
    """Compare the ledger against the corpus on disk. Returns problems.

    The coverage rule is the one that matters and it is bidirectional, for
    `check_declared_tiers`'s stated reason: a list checked in one direction
    becomes a place to put things. EVERY record in the corpus is either timed
    or is in `not_timed` with a written reason, and never both. That is what
    makes "nobody times a record twice" enforceable rather than aspirational:
    a record F3 ingests without a cost entry turns ingest.verify red in the
    same run that loads it, which is the only moment its minutes still exist.
    """
    problems: list[str] = []
    ledger = ledger or {}

    missing_terms = LEDGER_REQUIRED - set(ledger)
    if missing_terms:
        problems.append(f"missing ledger term(s) {sorted(missing_terms)}")
        return problems

    try:
        max_span = float(ledger["max_measured_span_minutes"])
    except (TypeError, ValueError):
        problems.append("max_measured_span_minutes is not a number")
        return problems

    problems.extend(check_phase_vocabulary(ledger.get("phases") or {}))

    not_timed = ledger.get("not_timed") or {}
    if not isinstance(not_timed, dict):
        problems.append("not_timed is not an object of record_id -> reason")
        not_timed = {}
    for rid, reason in sorted(not_timed.items()):
        if not str(reason or "").strip():
            problems.append(
                f"not_timed[{rid}] has no reason. A record excused from the "
                f"column without one is the column's first exemption, and "
                f"exemptions accumulate."
            )

    problems.extend(
        check_comparator(ledger.get("comparator") or {}, set(not_timed))
    )

    records = ledger.get("records")
    if not isinstance(records, list):
        problems.append("records is not a list")
        return problems

    timed: dict[str, dict] = {}
    for i, entry in enumerate(records):
        where = f"records[{i}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: not an object")
            continue
        rid = str(entry.get("record_id", "") or "")
        if not rid:
            problems.append(f"{where}: no record_id")
            continue
        where = f"records[{rid}]"
        if rid in timed:
            problems.append(
                f"{where}: timed twice. Two entries for one record are two "
                f"answers to the question this column asks."
            )
            continue
        timed[rid] = entry
        problems.extend(_check_record_entry(entry, where, max_span))

        declared = str(entry.get("tier", "") or "")
        if rid in derived_tiers:
            got, reason = derived_tiers[rid]
            if declared != got:
                problems.append(
                    f"{where}: tier {declared!r} in the ledger, {got!r} derived "
                    f"from the record -- {reason}. Ruling 45 reports cost per "
                    f"tier, so a ledger row filed under the wrong tier moves "
                    f"two means at once."
                )

    # Ruling 52, F3, 2026-08-31. Source hunting is the phase that DECIDES
    # which record exists, so the clock cannot be started against the right id
    # until the phase it is timing is over. The first record in this project's
    # history proved it in under three minutes: the hunt eliminated the source
    # the clock was opened against, and the ledger had no way to say so.
    #
    # The anti-loophole is the whole design, and it is one clause: a row may be
    # retired ONLY if the record is not in the corpus. Without it, `retire`
    # becomes a way to delete the expensive records from the column kill
    # trigger 3 reads -- the same shape as a sweep excluded from a calibration
    # because somebody did not like its numbers, which floor.json refuses with
    # `a_named_sweep_must_actually_fail_the_rule`.
    #
    # Retired rows are KEPT and named, never deleted. Excluding by a recorded
    # rule is a diff; excluding by making a row vanish is not.
    retired = ledger.get("retired")
    retired_ids: dict[str, dict] = {}
    if not isinstance(retired, list):
        problems.append("retired is not a list")
        retired = []
    for i, entry in enumerate(retired):
        where = f"retired[{i}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: not an object")
            continue
        rid = str(entry.get("record_id", "") or "")
        if not rid:
            problems.append(f"{where}: no record_id")
            continue
        where = f"retired[{rid}]"
        if rid in retired_ids:
            problems.append(f"{where}: retired twice")
            continue
        retired_ids[rid] = entry
        if not str(entry.get("because", "") or "").strip():
            problems.append(
                f"{where}: retired with no written reason. An unexplained "
                f"retirement is a deletion with extra steps, and the minutes "
                f"it removes are the ones nobody can re-measure."
            )
        if not _ISO_DATE.match(str(entry.get("retired_on", "") or "")):
            problems.append(
                f"{where}: retired_on {entry.get('retired_on')!r} is not a date"
            )
        problems.extend(_check_record_entry(entry, where, max_span))

    # RULING 59, F4, 2026-08-31. Ruling 52 wrote its anti-loophole as a
    # PERMANENT property of the ledger -- a retired row's record must not be in
    # the corpus -- and retirement as an EVENT. The two disagree the moment a
    # record that did not exist comes to exist, which is not a hypothetical: it
    # happened to africa-04-silko-talmis, whose row was retired legitimately
    # when Adulis was curated first, and which was then curated four hours
    # later. A legal retirement became an illegal ledger, and ruling 52 gave
    # nobody a way back.
    #
    # A retired row may therefore be REINSTATED, and the anti-loophole is kept
    # exactly where it was: a reinstated row is exempt from both checks below
    # ONLY while an ACTIVE row for the same record exists. Reinstatement means
    # the minutes are back in a mean, not that a row escaped one. Retire it,
    # declare it reinstated, and file nothing, and the first check still fires.
    reinstated = {rid for rid, e in retired_ids.items()
                  if str(e.get("reinstated_on") or "").strip()}
    for rid in sorted(reinstated):
        entry = retired_ids[rid]
        if not _ISO_DATE.match(str(entry.get("reinstated_on", "") or "")):
            problems.append(
                f"retired[{rid}]: reinstated_on "
                f"{entry.get('reinstated_on')!r} is not a date")
        if not str(entry.get("reinstated_because") or "").strip():
            problems.append(
                f"retired[{rid}]: reinstated with no written reason. An "
                f"unexplained reinstatement is the retirement rule waived by "
                f"whoever was inconvenienced by it")
        if rid not in set(timed):
            problems.append(
                f"retired[{rid}]: reinstated, but no row in `records` carries "
                f"its minutes. Reinstatement means the minutes are back in a "
                f"mean; a reinstated row with nothing filed against it is a "
                f"retirement wearing a different word")

    in_corpus = sorted((set(retired_ids) - reinstated) & set(derived_tiers))
    if in_corpus:
        problems.append(
            f"{in_corpus} are RETIRED and are in the corpus. A row may be "
            f"retired only if its record does not exist: otherwise retirement "
            f"is a way to take the expensive records out of the column kill "
            f"trigger 3 reads."
        )
    clash = sorted((set(retired_ids) - reinstated) & (set(timed) | set(not_timed)))
    if clash:
        problems.append(
            f"{clash} are retired AND timed or excused. One record, one answer."
        )

    both = sorted(set(timed) & set(not_timed))
    if both:
        problems.append(
            f"{both} are both timed and excused from timing. One record, one "
            f"answer."
        )

    corpus = set(derived_tiers)
    uncovered = sorted(corpus - set(timed) - set(not_timed))
    if uncovered:
        problems.append(
            f"{uncovered} are in the corpus and in neither `records` nor "
            f"`not_timed`. Nobody times a record twice: the minutes exist on "
            f"the day the record is curated and never again."
        )
    stale = sorted((set(timed) | set(not_timed)) - corpus)
    if stale:
        problems.append(
            f"{stale} are in the ledger and not in the corpus. A stale row "
            f"makes a per-tier mean wrong in the direction nobody checks."
        )

    open_entry = ledger.get("open_entry")
    if open_entry:
        if not isinstance(open_entry, dict):
            problems.append("open_entry is not an object")
        else:
            rid = str(open_entry.get("record_id", "") or "")
            phase = str(open_entry.get("phase", "") or "")
            started = str(open_entry.get("started_at", "") or "")
            problems.append(
                f"a clock is still running: {rid or '?'} / {phase or '?'} "
                f"since {started or '?'}. Minutes nobody has attributed are "
                f"minutes that leave the column when the session ends. Run "
                f"`python -m ingest.cost_log stop`."
            )
            if phase and phase not in PHASES:
                problems.append(f"open_entry names unknown phase {phase!r}")
            if rid and derived_tiers and rid not in derived_tiers:
                problems.append(f"open_entry names unknown record {rid!r}")
            if started and not _ISO_STAMP.match(started):
                problems.append(
                    f"open_entry.started_at {started!r} is not an ISO UTC stamp"
                )
    return problems


# --------------------------------------------------------------------------
# The report. Ruling 45: PER TIER, beside the declared mix, and a cost claim
# only when the mix is met.
# --------------------------------------------------------------------------

def record_total(entry: "dict") -> float:
    """One record's minutes, over every phase it declares."""
    phases = entry.get("phases") or {}
    total = 0.0
    for name in PHASES:
        cell = phases.get(name) or {}
        minutes = _as_minutes(cell.get("minutes"))
        if minutes is not None:
            total += minutes
    return total


def summarise(ledger: "dict") -> "dict[str, dict]":
    """Per tier: the timed records in curation order, and what they cost.

    In CURATION ORDER and not in file order, because the only trend ruling 46
    admits is a trend across the tranche, and a trend is an order before it is
    an arithmetic. Ties break on record_id so two records curated on one day
    do not reorder between runs -- a report that reorders itself is a report
    whose diffs cannot be read.
    """
    by_tier: dict[str, dict] = {}
    for entry in ledger.get("records") or []:
        if not isinstance(entry, dict):
            continue
        tier = str(entry.get("tier", "") or "unknown")
        bucket = by_tier.setdefault(
            tier,
            {"rows": [], "by_phase": {p: 0.0 for p in PHASES},
             "measured": 0.0, "estimated": 0.0,
             "by_agent": {a: 0.0 for a in AGENTS}},
        )
        bucket["rows"].append(entry)
        phases = entry.get("phases") or {}
        for name in PHASES:
            cell = phases.get(name) or {}
            minutes = _as_minutes(cell.get("minutes"))
            if minutes is None:
                continue
            bucket["by_phase"][name] += minutes
            agent = str(cell.get("agent", "") or "unrecorded")
            if agent not in bucket["by_agent"]:
                agent = "unrecorded"
            bucket["by_agent"][agent] += minutes
            if str(cell.get("provenance", "")) == "measured":
                bucket["measured"] += minutes
            else:
                bucket["estimated"] += minutes

    for tier, bucket in by_tier.items():
        bucket["rows"].sort(
            key=lambda e: (str(e.get("curated_on", "")), str(e.get("record_id", "")))
        )
        bucket["n"] = len(bucket["rows"])
        bucket["total"] = sum(record_total(e) for e in bucket["rows"])
        bucket["mean"] = bucket["total"] / bucket["n"] if bucket["n"] else 0.0
    return by_tier


def trend_line(bucket: "dict", min_n: int) -> str:
    """First half against second half, or the reason it is not a trend.

    NOT MEASURED and says so -- ruling 39's amendment to G3 prints exactly
    that where per-session stability cannot be computed inside one sweep, and
    the same sentence is owed here. `published_translation_only` has four new
    records in the whole of Block F and `catalogue_record` has eight; below
    the declared floor a per-tier mean moves further on one hard record than
    on any change of method, and reporting one anyway would be a trend line
    over noise with kill trigger 3 hanging off it.
    """
    n = bucket["n"]
    if n < min_n:
        return (
            f"NOT A TREND (n={n}, floor {min_n}). Reported as a mean and "
            f"nothing more."
        )
    # FINDING 70's teeth, and the reason the field was worth adding. The risk
    # that finding names is not that the agent is unknown; it is that the tier
    # is "about to be read as a trend by somebody who does not know that four
    # of its timed entries measure a different agent." A trend across two
    # agents is a trend across two measurements, and n is the wrong guard for
    # it: this tier is comfortably above the floor and that is what makes it
    # dangerous. Refused rather than annotated -- ruling 36's shape, where an
    # arm that cannot be identified blocks rather than being read as a default.
    mixed = sorted(a for a, m in (bucket.get("by_agent") or {}).items() if m)
    if len(mixed) > 1:
        split = ", ".join(
            f"{a} {bucket['by_agent'][a]:.0f} min" for a in mixed)
        return (
            f"NOT A TREND (n={n}, above the floor {min_n}, but the minutes "
            f"come from {len(mixed)} agents: {split}). FINDING 70: a model "
            f"apportioning its own wall clock produces smaller, smoother "
            f"numbers than a person timing themselves, across every phase at "
            f"once. Reported as a mean and nothing more."
        )
    half = n // 2
    first = [record_total(e) for e in bucket["rows"][:half]]
    second = [record_total(e) for e in bucket["rows"][n - half:]]
    a = sum(first) / len(first)
    b = sum(second) / len(second)
    direction = "down" if b < a else ("up" if b > a else "flat")
    return (
        f"first {len(first)} mean {a:.1f} min -> last {len(second)} mean "
        f"{b:.1f} min ({direction})"
    )


def format_report(
    ledger: "dict",
    target_mix: "dict | None" = None,
) -> "list[str]":
    """The lines `ingest.cost_log report` prints, and the only source of any
    curation-cost number that reaches a document.

    F1 put an assertion count into five files as 29 when the suite had 30,
    because the number was transcribed rather than read. Every figure below is
    computed here at print time; nothing in PROGRESS.md or F2_RESULT.md may be
    a curation-cost number that was not.
    """
    target_mix = target_mix or {}
    at_60 = target_mix.get("by_tier_at_60") or {}
    min_n = int(ledger.get("min_n_to_read_as_a_trend", 0) or 0)
    by_tier = summarise(ledger)

    comparator = ledger.get("comparator") or {}
    lines = [
        "curation cost per record -- PER TIER (ruling 45), within-tranche "
        "(ruling 46)",
        "",
        f"evaluated against : {comparator.get('evaluated_against', '?')}",
        f"why not record 12 : {comparator.get('why_not_record_12', '?')}",
        "",
    ]

    # Ruling 52. NAMED, never merely subtracted -- the sentence
    # calibrate_floor already earns about an excluded sweep. A retired row that
    # no report mentions is a row that vanished, which is the thing retirement
    # was built NOT to be. Printed above the table because it is the one part
    # of this report that is about minutes NOT in it.
    retired = [e for e in (ledger.get("retired") or []) if isinstance(e, dict)]
    if retired:
        live = [e for e in retired if str(e.get("reinstated_on") or "").strip()]
        gone = [e for e in retired if e not in live]
        if gone:
            lines.append(f"retired rows: {len(gone)} -- minutes recorded "
                         f"against a record that will never exist, kept and "
                         f"named here, counted in NO mean below.")
            for entry in gone:
                lines.append(
                    f"  {entry.get('record_id', '?')}   "
                    f"{record_total(entry):.1f} min   "
                    f"retired {entry.get('retired_on', '?')}")
                lines.append(f"      {entry.get('because', '')}")
            lines.append("")
        # Ruling 59. Printed SEPARATELY and with the opposite sentence, because
        # these minutes ARE in a mean below -- re-filed on the record that
        # landed, as `estimated`. A reader who saw them under the heading above
        # would subtract them twice.
        if live:
            lines.append(f"reinstated rows: {len(live)} -- retired while the "
                         f"record did not exist, and reinstated when it did. "
                         f"Their minutes ARE counted below, re-filed on the "
                         f"record as `estimated`; the row here is the history.")
            for entry in live:
                lines.append(
                    f"  {entry.get('record_id', '?')}   "
                    f"retired {entry.get('retired_on', '?')}   "
                    f"reinstated {entry.get('reinstated_on', '?')}")
                lines.append(f"      {entry.get('reinstated_because', '')}")
            lines.append("")

    timed = sum(b["n"] for b in by_tier.values())
    excused = len(ledger.get("not_timed") or {})
    if not timed:
        lines.append(
            "NO RECORD HAS BEEN TIMED YET. The column starts at record 25 "
            f"(F3); {excused} seed records are excused from it with a written "
            "reason, and nothing else is."
        )
        return lines

    for tier in sorted(by_tier):
        bucket = by_tier[tier]
        target = at_60.get(tier, "?")
        lines.append(f"{tier}   n={bucket['n']}   target at 60: {target}")
        lines.append(
            f"    mean {bucket['mean']:.1f} min/record over "
            f"{bucket['total']:.1f} min"
        )
        lines.append(f"    {trend_line(bucket, min_n)}")
        measured = bucket["measured"]
        estimated = bucket["estimated"]
        total = measured + estimated
        share = (100.0 * estimated / total) if total else 0.0
        lines.append(
            f"    provenance: {measured:.1f} min measured, {estimated:.1f} min "
            f"estimated ({share:.0f}% remembered)"
        )
        agents = ", ".join(
            f"{a} {bucket['by_agent'][a]:.0f}"
            for a in AGENTS if bucket["by_agent"][a]
        )
        lines.append(f"    by agent: {agents or 'nothing recorded'}")
        phases = ", ".join(
            f"{name} {bucket['by_phase'][name]:.0f}"
            for name in PHASES
            if bucket["by_phase"][name]
        )
        lines.append(f"    by phase: {phases or 'nothing recorded'}")
        lines.append("")

    lines.append(mix_status_line(by_tier, at_60))
    return lines


def mix_status_line(by_tier: "dict[str, dict]", at_60: "dict") -> str:
    """Ruling 45's last clause, printed with the numbers it governs.

    *Read as a cost claim only when the mix is met.* A falling mean over a mix
    that has not been met is the exact reading the ruling exists to refuse, so
    the report says which of the two it is holding rather than leaving that to
    whoever quotes it.
    """
    if not at_60:
        return (
            "MIX NOT DECLARED IN THIS REPORT: no target mix was passed, so "
            "nothing above is a cost claim (ruling 45)."
        )
    short = {
        tier: (int(target) - by_tier.get(tier, {}).get("n", 0))
        for tier, target in at_60.items()
        if by_tier.get(tier, {}).get("n", 0) < int(target)
    }
    if short:
        return (
            "NOT YET A COST CLAIM (ruling 45): the declared mix is not met -- "
            f"still owed {dict(sorted(short.items()))}. Until it is, the means "
            "above describe the records that happen to have been curated, not "
            "the cost of curating a record."
        )
    return (
        "The declared mix is MET, so the per-tier means above are readable as "
        "a cost claim (ruling 45)."
    )
