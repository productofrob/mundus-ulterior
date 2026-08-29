# Rulings 46 to 48, and finding 32 — declared 2026-08-29, in F2

*Written in the session that made them, for the reason `RULINGS.md` records
about rulings 20 and 21: a ruling that exists only as a line in a summary list
is a ruling nobody can quote, check, or argue with later.*

*All three rulings are recorded BEFORE a single record is timed. That is not a
preference. `PHASE2_PLAN` F2 starts the minutes column at record 25, **nobody
times a record twice**, and whatever the column does not carry on the day a
record is curated it never carries. F2 is the last moment any of these can be
decided in advance, and ruling 39's sentence — a gate amended at the end is a
gate fitted to its result — applies to a comparator and to a phase list exactly
as it applies to a gate.*

---

## Ruling 46 — kill trigger 3 is evaluated WITHIN THE TRANCHE, records 25 to 60, per tier, and against nothing else

**Kill trigger 3 as written cannot be evaluated. It is amended, in advance, to
a within-tranche trend: cost per record in tier T across records 25 to 60, in
curation order, with n stated beside it. The comparator is declared in
`data/curation_cost.json` and `ingest.cost.check_comparator` refuses a
comparator that names a seed record as a baseline.**

### The comparator does not exist, and nothing said so

> *"if record 60 costs what record 12 cost, 200 is a staffing question rather
> than an engineering one"* — `PHASE2.md`, repeated verbatim by `PHASE2_PLAN`
> F2.

**Nothing anywhere records what record 12 cost.** The seed 24 were curated
across Parts 3 to 7, before any column existed; there is no minutes figure for
any of them, in any file, and none can be reconstructed. The trigger names a
comparison one of whose two terms has never been measured.

This is not a small gap. Kill trigger 3 is one of the three questions Phase 2
was built to answer, and the number it hangs off is the one G3 asks for. A
block that reached G3 and discovered its comparator was missing would have
spent eight sessions producing a figure with nothing to compare it to.

### Why the weaker claim, declared now, and not a manufactured baseline

Two alternatives were considered and both refused.

**Re-timing three or four seed records to manufacture a record-12 equivalent.**
Refused because it measures the wrong thing. Re-curating a solved record is
re-doing it: the source is already found, the rights are already cleared, the
placement is already decided, the tier is already settled. It is systematically
cheaper than curation, in the phases that dominate curation, and a baseline
built that way would bias the trigger toward *costs have not fallen* — the
answer that keeps the project going. A comparator whose error has a direction
is worse than no comparator, because the number it produces looks like
evidence.

**Reconstructing estimates for the seed 24 from `PROGRESS.md` and the commit
history.** Refused for ruling 39's reason, in its purest form: the estimate
would be produced by the people who want the trend to be downward, after the
new numbers are in.

So the claim available to Block F is the within-tranche one, and **it is a
different and weaker claim than the trigger as written.** It cannot say whether
the machine got cheaper than it was at record 12. It can say whether it got
cheaper across the 36 records that came after record 24. G3 reports that, or
G3 reports nothing.

### And the n travels with it

Per tier the tranche is **14 / 10 / 4 / 8** records. `min_n_to_read_as_a_trend`
is declared at **10**, now, with the consequence stated rather than discovered:
**`published_translation_only` (4 new) and `catalogue_record` (8 new) can never
be read as trends inside Block F, whatever their numbers do.** Two of the four
moving tiers can carry the claim. Below ten, a per-tier mean moves further on
one unusually hard record than on any change of method, and
`ingest.cost.trend_line` prints `NOT A TREND (n=4, floor 10)` rather than a
direction — the same sentence ruling 39's amendment already prints where
per-session stability cannot be computed inside one sweep.

**A trend over eight catalogue records is not a measurement anyone should stake
200 on, and saying so here costs one paragraph. Saying it in Block G costs the
block.**

---

## Ruling 47 — the minutes are divided into SEVEN PHASES, fixed before the first record is timed, and a phase that went to zero must say zero

**Curation minutes are recorded per record AND per phase:
`source_hunting`, `rights_and_licence`, `text_capture`,
`translation_and_fidelity`, `placement`, `authoring`, `rework`. The vocabulary
is held in `ingest.cost.PHASES`, declared with a written definition apiece in
`data/curation_cost.json`, and `ingest.cost.check_ledger` REFUSES a record
entry that omits a phase.**

### A single minutes figure is gameable by re-labelling work

This is ruling 45 one level down and it is the same defect. Ruling 45 closed
*an aggregate satisfied by curating cheaper records*; a single figure per record
is *an aggregate satisfied by counting less of the record*. Cost "trends down"
the moment source-hunting is called research rather than curation, or rights
checking stops being timed, or gold-case writing moves out of curation and into
"eval work". Nothing in one number can tell that from the work getting faster,
and kill trigger 3 hangs off it.

Seven phases make the same move visible as its own line. **A phase that went to
zero has to SAY zero** — an absent phase and an unrecorded phase are the same
shape on disk, so the checker refuses the absence, and the fall lands in the
phase that stopped rather than in a total nobody can decompose.

### Why these seven, and why `rework` is one of them

`rights_and_licence` is separate from `source_hunting` because it is the phase
most easily dropped without anybody noticing it has been. `authoring` includes
gold-case writing on purpose: a record curated without the case that tests it
is a record the sweep cannot see, and putting case-writing outside curation
would make the corpus look cheaper by making it less measurable.

`rework` is not a stage. It is what a failed check sends back — a red
`ingest.verify`, a declared-vs-derived tier disagreement, a ranking regression
traced to one record. It exists so that **a tranche that got faster by getting
sloppier reports rework rising rather than a total falling.** Without it the
cheapest possible curation strategy is the one that fails verification, and the
column would applaud it.

### Fixed on day one, and that is the whole point

Nobody times a record twice. A phase added at record 40 is a phase records 25
to 39 are missing, and there is no way to go back and fill it in. So the
vocabulary is closed, `check_phase_vocabulary` compares the declared list
against the module's in order, and adding a phase later is a deliberate edit
that turns the ledger red until every earlier record is reconciled — which is
the correct outcome and not an inconvenience.

---

## Ruling 48 — a measured minute and a remembered minute are two kinds of knowledge, and the ledger reports them as two

**Every phase cell carries `provenance`: `measured` if a clock in
`ingest.cost_log` produced it, `estimated` if a person remembered it. An
`estimated` cell REQUIRES a written reason. A cell that is part clocked and
part remembered is `estimated`. The report prints the split per tier.**

This is ruling 36's shape one level down, and `data/corpus_tiers.json` already
names it: *recorded and reconstructed are two kinds of knowledge and must be
reported as two*.

Without the distinction, a trend computed mostly out of recollection is
indistinguishable from a measurement, and the only moment anyone can tell is
the moment the figure is written. `python -m ingest.cost_log stop` writes
`measured`. `add --minutes N --because "..."` writes `estimated`, and refuses
to write at all without the reason, because **an unexplained estimate is a
measurement by tomorrow.**

**The weaker provenance wins.** A cell that was clocked for twenty minutes and
then credited ten remembered ones is `estimated` in full — the more flattering
of the two readings is the one nobody would check.

**And a clock has a ceiling.** `max_measured_span_minutes` is 240. A clock
started and left running overnight writes a working day of `measured` minutes
into the one number kill trigger 3 depends on, and it arrives wearing the label
of the most trustworthy figure in the file. Above four hours, `stop` refuses
and the span must be closed as an explicit estimate with a reason — which is a
diff. Four hours rather than one, because a hard `verbatim_with_provenance`
record genuinely can take an afternoon, and a limit that fires on real work is
a limit people route around.

**An open clock fails `ingest.verify`.** Unattributed minutes are minutes that
leave the column when the session ends, and the ledger is the only place they
ever existed.

---

# FINDING 32 — the check FINDING 30 deferred could not be built as deferred, and F1's own correction is the counterexample

**F1 deferred a check to F2 in writing and specified it:**

> *"`eval/goldset.py` refusing a case whose `archived_status` names a
> `floor.json` state that `floor.json` contradicts... It is one token
> (`known_failing_cases`) tested against one file, not prose interpretation,
> so it is a small F2 item and not a research question."*

**Built as specified, it fires on the sentence that gets the history right.**

F1's corrected `archived_status` on `weilue-chinese-quotation` says, truly:

> *"ruling 38 moved it OUT of `floor.json.known_failing_cases` on 2026-08-28
> into the `promotion_candidates` state that ruling created"*

That sentence contains the token. It is not a stale claim; it is the
correction. A scan for `known_failing_cases` in that field refuses the one case
in the corpus whose prose is now exactly right, and **a check whose first true
positive is a false one is a check somebody switches off in a week.**

The specification was not careless. It was written in the hour the defect was
found, about a field that had just been corrected, and the correction is what
made it impossible. **Prose cannot carry a machine-checkable claim about
another file, however few tokens it is scanned for** — which is the same
sentence `archived_status` already earns by being deliberately outside
`_ASSERTION_KEYS`.

## What was built instead, and why it is still one token against one file

The claim moves out of the prose and into a field: **`floor_state`**, one of
`required_cases`, `known_failing_cases`, `promotion_candidates`, `none`.

It is ruling 43's shape exactly. The tier is DECLARED in the case and DERIVED
from the record, and `ingest.verify` fails when they disagree. The floor state
is DECLARED in the case and HELD in `floor.json`, and `load_answer_cases` fails
when they disagree. Both exist for the same reason: *a state that is only read
from one place could never be wrong, and could never be checked either.*

`archived_status` is untouched. It stays prose, stays outside
`_ASSERTION_KEYS`, stays read by nothing, and `floor_state` is outside
`_ASSERTION_KEYS` too — **no archived run is re-scored by any of this.**

## Three decisions inside it, each with a reason

**Absent means `none`.** A case that declares nothing is asserting it is in NO
floor state. That is what makes the check bidirectional without editing 33
cases: when ruling 38 next moves a case, the case's implicit `none` contradicts
`floor.json` and the gold set refuses to load. FINDING 30's exact failure mode
was a file changing and *nothing having to notice*; a one-directional check
would still let it through.

**`demotions` is not a state.** `load_floor` already refuses a demotion that is
not tracked in `known_failing_cases`, so a demoted case is in that state and
admitting `demotions` as a fourth would give one case two true answers — the
defect this check exists to catch, reintroduced by the check itself.

**The floor resolves to the canonical file when none sits beside the gold
file.** Every harness in this repository that exercises a whole-file rule
writes a copy of `answer_cases.json` to a temporary directory. A check that ran
only next to `floor.json` would be a check any copy walks out of, and two
existing tests found that within a minute of the first version being written.

## What it caught on the first run

Seven cases: three in `required_cases`, three in `known_failing_cases`, one in
`promotion_candidates`. All seven now declare, and the suite refused the gold
set until they did.

**The suite went from 333 assertions to 343 and stayed green, and it stayed
green because it was run.** Which is the other half of FINDING 31's lesson,
and it is why the F2 state block below lists six suites.

---

# The trap this session walked into, recorded because it is a repeat

`scripts/mutate_part8.py` is 87 mutations at roughly twelve seconds a suite
run. Started through the device bridge, it was killed by the bridge's own call
timeout **between applying a mutation and reaching the `finally` that restores
the sources**, and `eval/answer_eval.py` was left on disk with
`for doc_id in case.expect_quoted_docs:` mutated to `for doc_id in []:`. Every
quotation assertion in the scorer, silently disabled, in the working tree.

`git status` found it in one line and `git show HEAD:` restored it — **not
`git checkout --`, which the bridge refuses because it cannot unlink.** That is
worth its own sentence in the traps list.

**A mutation harness must be run where it can finish.** F2 verified its five
new `mutate_part8` mutations by importing the module and slicing `MUTATIONS`
and `EXPECTED` to the last five — six suite runs instead of eighty-eight — and
the full harness belongs in the PowerShell run on the host, where nothing kills
it at two minutes.
