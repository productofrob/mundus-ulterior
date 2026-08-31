# Rulings 49 to 51, and FINDING 33 — declared 2026-08-31, in F3

*Written in the session that made them, for the reason `RULINGS.md` records
about rulings 20 and 21: a ruling that exists only as a line in a summary list
is a ruling nobody can quote, check, or argue with later.*

*All three are recorded BEFORE record 25 is ingested. That is not a preference.
`F3_START.md` names F3 as the first thread in this project that MOVES THE
CORPUS, `26e4a683` has been the denominator of every archived number since Part
3, and a rule written after the first sub-tranche is a rule written by someone
who has seen what the first sub-tranche did to the numbers. Ruling 39's
argument, for the fifth time in this block, and the last block in which it can
be made in advance.*

---

## Ruling 49 — the CORPUS is part of the calibration scope, and the floor stays in force while it moves

**`floor.json.calibration_scope` gains a `corpus` clause: a seed record count
and a seed corpus digest. A sweep calibrates only if its `corpus_version` is
BOTH identifiable AND equal to the declared pair, and a sweep whose corpus
moved under it fails for a second reason. The clause is OPTIONAL — absent means
nothing is checked, which is the pre-F3 behaviour exactly — and
`eval/goldset.py` refuses a half-declared one.**

**The floor is NOT suspended for the tranche.** A run at 33 records still
computes a verdict on `required_cases`, and that verdict is the regression
reading. What the clause removes is that run's ability to RE-CALIBRATE.

### The rule could not see the data it was written to protect

Measured, not argued, on 2026-08-31 at `51e0f21`:

```
floor.calibrated_from_sweeps names four archives, and ALL FOUR carry, in
their own corpus_version block:   seed_record_count 24
                                  seed_corpus_digest 26e4a683...
floor.calibration_scope's clauses:  session identity | min_cases_per_sweep 30
                                    | arm (ruling 36)
                                    There is no clause about the corpus.
eval/calibrate_floor.py contains ZERO occurrences of the string "corpus".
```

FINDING 14 put `corpus_version` into every sweep **precisely so that a corpus
that moved could not go unnoticed.** `calibration_scope` was then written
twice — once on 2026-08-26, once by ruling 36 — without ever reaching for it.
The data was on disk for three weeks and the rule did not read it.

### It is ruling 36's own sentence, one dimension over

> *"without it, `floor.json`'s own anti-loophole would have INSISTED that a
> temperature-1 sonnet sweep calibrate a floor set on greedy haiku."*

Substitute the corpus for the arm. **The moment record 25 is ingested, a sweep
at 33 records carries a session identity, runs the full case set, states its arm
and archives complete — so it satisfies every clause the scope had — and
`a_named_sweep_must_actually_fail_the_rule` then REFUSES to let it be excluded
by name.** This file would have insisted that a 33-record sweep calibrate a
floor set at 24.

And it was not hypothetical: two entries in `floor.json` already anticipated
the clause. `promotion_candidates.weilue-chinese-quotation.bar` reads *"at 60
records"* and `demotions.vimose-runes.reinstated_when` reads *"at the corpus in
force when the reinstatement is claimed"*. Both knew the corpus is part of a
claim's identity. The rule that decides what may calibrate did not.

### In force, and not self-renewing, are two different properties

The three options were: the floor in force during the tranche, suspended for
its duration, or re-calibrated at 60. **Suspension was refused.** It would
leave the largest corpus move in this project's history — 24 records to 60,
five sub-tranches, five sessions — with no regression gate at all, and the
floor exists to say that the questions which worked still work. A new record
that displaces `muziris-cargo`'s evidence is exactly what it is for.

What suspension was reaching for is real, and the clause answers it directly: a
verdict taken at a corpus the floor was not set on may not become the floor.
`calibrated: true`, and the `calibrated_stability` numbers written beside it,
stay denominated in the four sweeps at 24 records until three sessions at 60
replace them.

### Nothing changes today, and that is checked rather than asserted

`python -m eval.calibrate_floor` still reports **ELIGIBLE** at `51e0f21`: the
four archives the floor stands on all ran at `26e4a683`, so the clause is a
no-op on the day it lands and bites on the day record 25 is ingested. A rule
that de-calibrated the floor by arriving would be a rule that lowered the thing
it was written to protect, and `eval/test_answer_eval.py` asserts the match
against the archives themselves rather than trusting the digest that was typed
into the clause.

### What it cost to land, and the shape of that cost

**Eight assertions in three existing tests failed the moment the clause was
declared, every one of them because a synthetic sweep fixture did not state a
corpus.** The suite already carried the answer, written for the arm clause on
2026-08-28:

> *"a fixture that omitted it would fail on the arm instead and every guard
> below would be watching the wrong clause."*

The fixtures now state a corpus for the same reason they state an arm. That is
the same defect as the one the ruling closes — a record of a run that does not
say what it ran against — inside the file that tests for it.

---

## Ruling 50 — the third UTC date at 60 records is BOOKED, as a ninth session in Block F

**Block F is nine sessions, not eight. G3's amendment booked two sessions at 60
on two distinct UTC dates; three separate rules in this repository require
three. The third is booked now, in advance, and the F8 spike is not sacrificed
for it.**

### Three rules needed it and the gate booked two

```
floor.json  min_distinct_dates                     3
            -> calibrate_floor REFUSES calibrated: true below three dates, and
               ruling 49 now requires those dates to be at the corpus in force.
floor.json  promotion_and_reinstatement_bar        3 sessions, 3 dates, AT 60
            -> weilue-chinese-quotation cannot be promoted on fewer.
floor.json  demotions.vimose-runes.reinstated_when 3 sessions, 3 dates, AT 60
            -> vimose-runes cannot be reinstated on fewer.

PHASE2_PLAN G3 amendment: "at least two sessions at 60 records on two
distinct UTC dates ... two booked days at the end of Block F."
```

**Two dates at 60 leave all three unresolvable.** The floor would arrive at G3
still calibrated from four sweeps at 24 records — which ruling 49 makes an
honest statement rather than a hidden one, but an honest statement of a claim
nobody can act on. `weilue-chinese-quotation` would stay a promotion candidate
having already satisfied every clause of its bar except the corpus.
`vimose-runes` would stay demoted for a ninth session.

One session buys all three, and it buys them only if it is booked before the
block is spent. **A block that discovers on its last afternoon that it owes a
third date has already failed the gate it was trying to pass** — which is
PHASE2_PLAN's own sentence about the second date, unchanged, one date later.

### Why a ninth session and not the F8 spike

The obvious trade was to spend F8 — the HTR spike on the Palmyrene Tariff and
the Ezana Stone, which PHASE2_PLAN already flags as *"not committed; attempt it
only if F1–F7 came in under budget"*. It was refused. The two records it would
promote are the corpus's only `pointer_only` record and its
`published_translation_only` companion, both standing since Part 3, and
`ruling 44` sets the new-`pointer_only` ceiling at zero precisely because a
record whose text lives elsewhere is invisible to retrieval. Turning the one we
have into a record the index can see is the highest-value single record in the
block, and trading it for a calibration date would be paying for a measurement
with the thing being measured.

**The cost is stated with the decision:** ~198 chat calls, one booked day, and
Block F reads nine sessions everywhere it is written down.

---

## Ruling 51 — a sub-tranche re-runs the RANKING check and a floor PROBE, and the answer sweep runs only at 60

**`PHASE2_PLAN` F3–F7 is headed *"Curate in sub-tranches of ~9, re-running the
sweep at each"* and the command block beneath it is the RANKING check. The
command block is what F3–F7 do. The full answer sweep runs at 60 and nowhere
else. The floor's mid-tranche reading is a PROBE: the three `required_cases` at
`min_repetitions`, archived to `eval/probes/` and never to `eval/sweeps/`.**

### Read the heading the other way and it is the block

~198 chat calls per full sweep, four or five times over, on top of the three
sessions at 60 that rulings 39 and 50 have now booked. Those two readings of
one heading are a cheap block and a block that runs out of days.

**And the number a mid-tranche sweep would produce is one no rule here may
read.** It cannot calibrate — ruling 49. It cannot promote or reinstate — the
bar says at 60. G3 asks for a full sweep at 60 and asks for nothing at 33, 42
or 51. What is left is the regression question, which is the floor's, and the
floor's three required cases at three repetitions cost about nine calls.

### The directory is the rule

`eval/run_answer_sweep.py` archives a run below the floor's own
`min_cases_per_sweep` to `eval/probes/`, exactly as a foreign arm archives to
`eval/arms/`. `eval/calibrate_floor.load_sweeps` globs `sweeps/*.json`, so **a
probe cannot calibrate by construction**, and `excluded_by_rule` does not grow
one entry per sub-tranche — which is what would have happened had probes landed
beside the stratified sweeps and been excused by name five times.

The scope clause is still the guard if a file is ever moved across by hand.
This is the ordinary path that means nobody has to rely on it. **A rule
enforced by the directory is a rule nobody has to remember**, and the two D4
pilot sweeps are on disk today as the record of what happens when a small run
lands in the same folder as a large one.

### The allocation, which is the other half of the same ruling

Ruling 44 declared the mix at 60 and did not say which sub-tranche carries
what. `data/corpus_tiers.json.target_mix.allocation` now places all 36 records
as **slots** — a region, a tier and a count — over F3 to F7, and
`ingest.fidelity.check_allocation` FAILS `ingest.verify` if they do not deliver
the declared mix. Eleven branches, each mutation-verified.

```
F3  8   Southeast Asia 2+2, Persia 1+1, Scandinavia 1+1   (all source-language)
F4  7   Sub-Saharan Africa 2+2, East Asia 2+1
F5  7   Persia 1+1, Arabia 2+1, South Asia 1+1
F6  7   East Asia 1, Scandinavia 1, then the first catalogue records
F7  7   catalogue records and published translations only
```

**Every source-language record is curated before every catalogue record, and
the check refuses an allocation where that is not true.** Southeast Asia goes
first because it has ZERO records carrying retrieval-eligible source-language
text and needs four, which is why all four of its gold cases sit on find
records. Its four `verbatim_machine_english` records are also what turn on the
machine-translation path: the `verse` and `documentary` confidence profiles are
at n=1 and go load-bearing the moment the first one lands, and discovering that
in F7 leaves no session to calibrate them in.

**What this does to the cost column is stated rather than discovered.** It
biases the AGGREGATE cost per record downward by construction, because the
expensive tiers are curated first and the cheap tier last. That is not a defect
to be corrected by re-ordering — it is the reason ruling 46 already reports per
tier and in curation order. Within a tier the ordering is untouched, and the
two tiers above `min_n_to_read_as_a_trend` are exactly the two spread across
four sub-tranches each. **The aggregate is unreadable under this allocation and
ruling 46 already forbids reading it.** Said here so that nobody at G3 reads a
falling total as efficiency.

---

# FINDING 33 — three rules required a third date at 60 and the gate booked two, and each of the three was written by someone looking at one of them

Ruling 50 is the decision. This is what it says about how the gap was made.

Each of the three rules is correct and each was declared in advance with its
reason attached:

* `min_distinct_dates: 3` — D4, 2026-08-24, because a floor set from one day's
  observation was contradicted the same day.
* `promotion_and_reinstatement_bar` — 2026-08-28, Block F decision 4, raised
  from two dates to three by FINDING 26, and deliberately made ONE bar in both
  directions so that a case coming up and a case going down face the same
  standard.
* G3's two booked days — 2026-08-28, Block F decision 1, booked in advance
  precisely because *"the days are the scarce resource."*

**All three were written within five days of each other, two of them on the
same day, and no document holds the sum.** The bar was raised to three dates in
the same session that booked two days at 60, in the same file, by the same
decision list. The conflict is not between a rule and a mistake; it is between
three rules that were each checked against the thing they were about.

The shape is FINDING 14's, one level up from data: **a quantity that has to
agree across three declarations, maintained in three places, and nothing
computing the sum.** F1 found it in an assertion count, F2 found it in two
suite counts, and here it is in a resource nobody can buy retroactively — a UTC
date at a corpus that only exists after 36 records are curated.

There is no code fix. `PHASE2_PLAN.md`'s Block F section now carries the
session count and the three rules that set it, in one place, which is the same
remedy F1 applied to the suite list: **the list is the count, not a sentence
about the list.**

---

# FINDING 34 — every date in this session was transcribed, in the repository where a UTC date is the scarce resource

**Rulings 49 to 51 were written on 2026-08-31 and stamped 2026-08-29, in seven
source files and five documents, including `floor.json`'s own
`calibration_scope.corpus.declared_on`.**

The date was taken from two places and neither of them is a clock: the device
information reported at the start of the session, and `F3_START.md`'s own
opening line, *"Written 2026-08-29 at the close of F2"* — which was true about
F2 and was never a claim about F3. Two days had passed between the two threads
and nothing in the working tree said so, because nothing had changed in it:
`51e0f21` on entry, clean.

**It was caught by the suite, on the host, printing a number about itself:**

```
ok   the date is a plain YYYY-MM-DD, not a timestamp (2026-08-31)
```

`session_identity` is the function this project dates every sweep with, running
on the machine that runs them. It printed the real date beside eleven documents
claiming another one.

## Why this is not a cosmetic correction

A wrong date in this repository is not a typo, it is a false provenance claim
in the file whose entire business is provenance:

* `min_distinct_dates` counts **distinct UTC dates** and refuses calibration
  below three. `demotions.vimose-runes` and `promotion_candidates` both spend
  dates. Ruling 50 has just booked a ninth session to buy one.
* `calibration_scope.declared_on` and `arm.declared_on` exist to establish that
  a rule was written BEFORE the numbers it governs — which is ruling 39's whole
  argument, and an argument that rests on a date being right.
* `min_distinct_dates_note` already says it in the file: *"A sweep carrying no
  session identity contributes no date and cannot be given one after the
  fact."*

**A date read off another document is a date given after the fact.** The clause
this very session added refuses a sweep that cannot say which corpus it ran at;
it was declared in a file that could not say which day it was written.

## The mechanism, stated so it does not recur

This is the transcription defect for the fourth time in three sessions — F1's
assertion count, F2's suite count, F1's harness count, and now a date — and the
remedy is the one already written down: **anything written into a document
should be produced by something that can be re-run.** For dates that is one
command, and it costs nothing:

```powershell
python -c "import datetime as d; print(d.datetime.now(d.timezone.utc).date())"
```

`F3_RUNBOOK.md` step 0 now runs it before anything else. **The host is the
authority**, because the host is what stamps a sweep.

---

# FINDING 35 — the sentence that travels undercounts its own evidence, and the correction makes it stronger

**"Nine archives, 396 runs, and not one of them recorded which model
answered."** That sentence has been copied into every block document since
Block E. `eval.calibrate_floor` printed the other number on 2026-08-31, on the
host, in its first line:

```
9 archived sweep(s), 492 run(s)
```

Counted per archive, from the files:

```
20260810T191414  30 runs   5 cases   NO SESSION IDENTITY
20260810T193907  15 runs   5 cases   NO SESSION IDENTITY
20260812T134030  15 runs   5 cases   NO SESSION IDENTITY
20260824T122310  18 runs   6 cases   D4 pilot day 1
20260825T192121  18 runs   6 cases   D4 pilot day 2
20260826T103006  99 runs  33 cases   Block E day 1
20260826T115846  99 runs  33 cases   Block E day 1
20260827T103048  99 runs  33 cases   Block E day 2
20260828T103215  99 runs  33 cases   Block E day 3
                492
```

**396 is 4 x 99 — the four Block E sweeps, and only those.** It is the right
number for the sentence it was born in, `F2_RESULT`'s *"the denominator of all
396 Block E runs"*, and the wrong number beside "nine archives". The pair is
mismatched: nine archives hold 492.

**And the claim the sentence makes is true of all nine.** Not one of the 492
records which model answered — the three pre-D4 archives least of all, since
they carry no session identity either. So the correction does not weaken the
finding, it strengthens it by a hundred runs, which is the opposite of how a
transcribed number usually fails.

Corrected in F3's documents. The earlier block documents keep the sentence as
they wrote it: they are the record of what was said at the time, and editing
them is the move `archived_status` and `superseded_diagnosis` already exist to
avoid.

---

# The trap this session walked into, recorded because it is a new mechanism

**A mutation harness cannot be run through the bridge because of what the SUITE
costs there, not only because of the harness.** `eval.test_answer_eval` takes
**21.7 seconds** through the bridge and 94 mutations is forty minutes; even ONE
mutation plus its baseline exceeds the 45-second call timeout. F2 lost
`eval/answer_eval.py` to a kill between applying a mutation and restoring the
sources, and the mechanism here is the same trap with the arithmetic done in
advance.

`ingest.test_fidelity` costs 3.9 seconds, so `scripts/mutate_fidelity.py` was
verified here in three slices of four, four and three — each under twenty
seconds, each restoring its sources, each checked with `git status` afterwards.
**All eleven new mutations verified.**

The seven new `mutate_part8` mutations were pre-verified against ONE test
function rather than the whole suite — 0.3 seconds instead of 21.7 — and **that
is not the same evidence.** It cannot see a mutation caught by a guard
elsewhere in the file, which is exactly what the full harness reports as
`MISS ... detected by another guard`, and which has happened twice in this
repository. All seven fire. **The full harness still owes a run on the host**,
and `F3_RUNBOOK.md` step 2 is where it is claimed.

**CLOSED 2026-08-31, at `a1af62d`, and the claim held.** All six harnesses ran
on the host against the committed tree: `mutate_part8` 94, `mutate_fidelity`
35, `mutate_cost` 37, `mutate_ranking` 100, `mutate_part7b` 18,
`mutate_ui_places` 4 — **288 mutations, no MISS, no UNVERIFIED, no BASELINE
block in any of them**, sources restored byte for byte, and `git status`
empty afterwards. Each of the seven new mutations was caught by the guard
written for it and by no other, which is the part the one-function
pre-verification could not have shown. **The pre-verification agreed with the
full harness this time and that is not a reason to trust it next time** — it
would have agreed just as loudly if a guard elsewhere had been doing the work,
because it never ran the guards that would have.

---

# The sentences that travel

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT
was reachable. `muziris-cargo-akananuru` still sits at rank 310.

**Four sessions read 0.727272… and one of them was different. The pass rate
cannot see change.**

**Nine archives, 492 runs, and not one of them recorded which model
answered.** (CORRECTED 2026-08-31, FINDING 35. The sentence has read 396
since Block E; that is the four Block E sweeps' runs, not the nine archives'.)

**36% and 27% are not two refusal rates. They are two rates of uttering one
sentence.**

**Cost per record trending down is not a fact about efficiency until the mix is
held. The cheapest record in this corpus is the one that teaches a reader the
least.**

**Kill trigger 3 compares record 60 against record 12, and nobody ever wrote
down what record 12 cost.**

And three from F3:

**The floor was calibrated on four sweeps at 24 records and the rule that
decides what is allowed to calibrate it could not see the corpus — on data that
had been in every archive for three weeks, put there so that a corpus which
moved could not go unnoticed.**

**Three rules required a third UTC date at 60 records, two of them written on
the same day as the gate that booked two, and no document held the sum.**

**An allocation decided at F7 is an allocation fitted to what was already
curated, and the cheap tier last is the only ordering under which running out
of days costs the corpus least.**

**Eleven documents said 2026-08-29 and the machine that stamps every sweep said
2026-08-31. The date was read off another document, in the repository where a
UTC date is the thing a ninth session was just booked to buy.**
