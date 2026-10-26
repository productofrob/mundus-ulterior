# F2 — result

*2026-08-29. F2 builds the instrument and declares what it is allowed to mean.
It times no record: the column starts at record 25, which is F3's. The corpus
is unmoved and `26e4a683` is still the denominator of all 396 Block E runs and
of the sonnet arm's 165.*

```
tree            clean at 577a0e2 on entry; F2 adds one commit
corpus          24 records / 450 embedded / 0 pending   UNMOVED
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                UNMOVED. F3 moves it.

rulings         46, 47, 48         findings  32
new sidecar     data/curation_cost.json     the ledger, empty on purpose
new module      ingest/cost.py              the rules; imports nothing from
                                            the package, like fidelity.py
new CLI         ingest/cost_log.py          the only thing that writes it
new suite       ingest.test_cost        46  GREEN
new harness     scripts\mutate_cost.py  37  GREEN, with the BASELINE check
                                            from the day it was built
sqlglot         INSTALLED on the host. answer.test_answer 150/150, no skip
counts          answer.test_answer and ui\test_build_ui_data.py were the two
                suites printing a verdict and NO NUMBER. Both now count: 150
                and 14. Seven suites, seven counts.
```

## The headline, and it is a comparator that was never measured

**Kill trigger 3 compares record 60 against record 12, and nobody ever wrote
down what record 12 cost.**

`PHASE2.md` and `PHASE2_PLAN` F2 both carry the sentence — *"if record 60 costs
what record 12 cost, 200 is a staffing question rather than an engineering
one"* — and one of its two terms has never existed. The seed 24 were curated
across Parts 3 to 7, before any column existed; there is no minutes figure for
any of them in any file, and none can be reconstructed.

Ruling 46 amends it in advance, **before the first number**, to the only claim
Block F can actually make: a trend across records 25 to 60, per tier, in
curation order, with n printed beside it. That is **a different and weaker
claim** and it is written down as one. A comparator chosen after the numbers
are in is a comparator fitted to them — ruling 39's argument for the fourth
time in this block, and the reason the amendment is here rather than at G3.

**Two ways of manufacturing the missing term were considered and refused.**
Re-timing three or four seed records measures re-doing a solved record — source
already found, rights already cleared, placement already decided — so it is
systematically cheap in exactly the phases that dominate curation, and would
bias the trigger toward *costs have not fallen*, which is the answer that keeps
the project going. A comparator whose error has a direction is worse than none,
because the number it produces looks like evidence. Reconstructing estimates
from `PROGRESS.md` was refused for ruling 39's reason in its purest form.

## And the n, stated now rather than discovered at G3

Per tier the tranche is **14 / 10 / 4 / 8**. `min_n_to_read_as_a_trend` is
declared at **10**, with the consequence spelled out in the file:
**`published_translation_only` and `catalogue_record` can never be read as
trends inside Block F, whatever their numbers do.** Two of the four moving
tiers can carry the claim. Below ten, a per-tier mean moves further on one hard
record than on any change of method, and `trend_line` prints
`NOT A TREND (n=4, floor 10)` rather than a direction — the sentence ruling
39's amendment already prints where per-session stability cannot be computed
inside one sweep.

## The second defect, and it is ruling 45 one level down

**A single minutes figure per record is gameable by re-labelling work.** Cost
"trends down" the moment source-hunting becomes research rather than curation,
or rights checking stops being timed, or gold-case writing moves out into "eval
work". Ruling 45 closed *an aggregate satisfied by curating cheaper records*;
this is *an aggregate satisfied by counting less of the record*, and one number
cannot tell either from the work getting faster.

Ruling 47 divides the minutes into seven phases — `source_hunting`,
`rights_and_licence`, `text_capture`, `translation_and_fidelity`, `placement`,
`authoring`, `rework` — fixed before the first record is timed, and
`check_ledger` **refuses a record entry that omits one**. A phase that went to
zero has to say zero, so the fall lands in the phase that stopped.

`rework` is in the list because without it the cheapest possible curation
strategy is the one that fails verification, and the column would applaud it.
`authoring` includes gold-case writing because a record curated without the
case that tests it is a record the sweep cannot see.

## FINDING 32 — the deferred check could not be built as deferred

F1 deferred FINDING 30's check to F2 **and specified it**: *"one token
(`known_failing_cases`) tested against one file, not prose interpretation"*.

Built that way, it fires on F1's own correction. The corrected
`archived_status` on `weilue-chinese-quotation` says, truly, *"ruling 38 moved
it OUT of `floor.json.known_failing_cases`"*. **A check whose first true
positive is a false one is a check somebody switches off in a week.**

So the claim moved out of the prose and into `floor_state` — one token, four
values, declared in the case and held in `floor.json`, refused when they
disagree. Ruling 43's shape exactly: declared here, derived there, and a state
read from only one place could never be wrong and could never be checked
either. `archived_status` is untouched, stays prose, stays outside
`_ASSERTION_KEYS`; `floor_state` is outside them too, so **no archived run is
re-scored.**

Three decisions inside it, each recorded with its reason in `F2_RULINGS.md`:
absent means `none` (which is what makes it bidirectional without editing 33
cases, and FINDING 30's failure was a file changing while nothing had to
notice); `demotions` is not a state (it is a modifier on `known_failing_cases`,
and admitting it would give one case two true answers); and the floor resolves
to the canonical file when none sits beside the gold file, because every
harness here that exercises a whole-file rule writes a copy to a temp
directory, and a check any copy walks out of is a check with an exit.

Seven cases now declare. The suite went 333 -> 343 and stayed green.

## The skip that was not a pass, and the number nobody could have checked

F1 carried it as owed item 2 and F2 closed it: `pip install -r
requirements-dev.txt`, and `answer.test_answer` now runs the guard it had been
printing `skip sqlglot not installed` in place of. **It is exactly one
assertion** — *"schema and queries parse as PostgreSQL"* — but it is not a
small one: it parses the whole Part 7 schema, every query in `queries`, and
both `UPSERT_ANSWER` and `UPSERT_CITATION`. It passes. The regex guards around
it (the parameter casts, the `ON CONFLICT`-matches-the-primary-key pairs) had
always run and were never behind the skip.

**And the reason it stood for weeks is the same reason "FIVE SUITES" stood.**
`answer.test_answer` printed only `all Part 7 offline checks passed` and no
count, so the PART 7 line in every state block in this repository carried no
number. `GREEN, with ONE SKIP` was therefore uncheckable in both directions:
nobody could see how much the suite covered, or how little was missing. A
reader had no way to tell one skipped assertion from thirty.

**And it was two suites, not one.** `ui\test_build_ui_data.py` printed only
`All build-layer placement-shape assertions passed.` for the same reason and
with the same consequence: **two of the seven suites in this repository were
reporting a verdict and no number.** Both now count, 150 and 14.

Fixed the way F1 fixed the assertion count: **the suite counts and prints its
own.** `answer.test_answer` now reads `150 passed, 0 failed` — and if sqlglot is ever absent
again it reads `149 passed, 0 failed, 1 SKIPPED` with the skipped assertion
named beneath it, in the summary line rather than a hundred and fifty lines
above it. The `except ImportError` branch stays, because
`requirements-dev.txt` is deliberate that every suite degrades gracefully
without it; what it no longer does is degrade quietly.

## What F2 did NOT do

- **It did not time a record.** The column starts at record 25. `records` is
  `[]` and all 24 seed records are in `not_timed` with a written reason.
- **It did not move the corpus.** No seed record was edited. `corpus_digest` is
  unchanged.
- **It did not touch a scored assertion.** `floor_state` is outside
  `_ASSERTION_KEYS`, like `archived_status`, so no archived run is re-scored.
- **It did not loosen `ingest/verify.py` check 9.** `len(docs) == 24` is
  correct today and F3 breaks it on purpose, in the same commit as the records
  or not at all.

## Two corrections, both of them counts, both of them transcribed

**F2_START's state block says "FIVE SUITES, not four" above a list of six.**
The sentence is F1's, and it was true when written — four listed plus
`ingest.verify`. `ingest.test_fidelity` then made six, and the sentence
travelled into the next document unchanged with the list it contradicts
directly beneath it. **With `ingest.test_cost` there are SEVEN.** This is
exactly F1's own closing correction — one claim held in more than one place and
only one copy maintained — reappearing in the document that recorded it, eight
hours later.

**F1's owed item 4 says the BASELINE check is in "four harnesses of seven".**
It is now in five: `mutate_part8`, `mutate_part7b`, `mutate_ui_places`,
`mutate_fidelity`, `mutate_cost`. The denominator of seven excludes
`scripts/mutate_distractors.py`, which is a real harness but a different
shape — it mutates a live database view rather than a source file — so the
count is defensible and is recorded here so the next reader does not have to
re-derive it.

## The trap, and it is a repeat with a new mechanism

`scripts/mutate_part8.py` was started through the device bridge and **killed by
the bridge's own call timeout between applying a mutation and reaching the
`finally` that restores the sources.** `eval/answer_eval.py` was left on disk
with `for doc_id in case.expect_quoted_docs:` mutated to `for doc_id in []:` —
every quotation assertion in the scorer silently disabled, in the working tree,
with the suites still reporting green because they had not been re-run.

Found by `git status` in one line. Restored with `git show HEAD:` writing the
bytes back, **not with `git checkout --`, which the bridge refuses because it
cannot unlink.**

F2's five new `mutate_part8` mutations were then verified by importing the
module and slicing `MUTATIONS` and `EXPECTED` to the last five — six suite runs
instead of eighty-eight. **The full harness belongs in the PowerShell run on
the host**, and `F2_RUNBOOK.md` says so with the reason attached.

## What is owed, carried forward

```
1  the BASELINE check is in five harnesses of eight. mutate_ranking,
   mutate_places and mutate_recover still lack it; mutate_distractors is the
   fourth and is a different shape.
2  ruling 40's article_added is STILL unverified against any live run.
3  muziris-cargo, REQUIRED, is 3/5 on the arm and 12/12 on the declared one.
4  `eval.answer_eval --archives` pools arms into one report (FINDING 29).
5  G3's amendment costs a SECOND session at 60, on a second UTC date, ~198
   chat calls. Ruling 39 booked the days. Do not discover this in F8.
6  `ingest/verify.py` check 9 asserts `len(docs) == 24`. F3's, not F2's: it is
   correct today and F3 breaks it on purpose, in the same commit as the
   records or not at all.
7  sqlglot also adds checks to `ingest/test_sql.py` and `ingest/test_embed.py`.
   test_embed passes with it. test_sql needs the DATABASE and has not been run
   on the host with sqlglot present -- guards that have never run are guards
   nobody knows work.
8  the FIRST record F3 curates is the first test of the CLI under real
   conditions. If `start`/`stop` turns out to be friction the curator routes
   around, the failure mode is estimates with reasons rather than silence —
   which is why `add` exists and why the report prints the split.
```

## Traps, for the thread that curates

Everything in `F1_START`'s list still applies — the bridge, `git` locks,
per-file line endings, `BASELINE:`/`UNVERIFIED`, ambiguous mutation anchors.
Four from today:

- **`ingest.verify` is a suite and belongs in every green check.** FINDING 31,
  and it now carries the cost ledger's coverage check as well as the tiers'.
- **A record cannot carry a new field.** Ruling 43. The cost ledger is the
  SECOND file that would have moved the digest.
- **Do not run a mutation harness through the bridge.** It will be killed
  mid-mutation and the mutation stays on disk.
- **`git checkout --` does not work through the bridge.** It cannot unlink.
  `git show HEAD:<path>` written back as bytes does.

## The sentences that travel

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310.

**Four sessions read 0.727272… and one of them was different. The pass rate
cannot see change.**

**Nine archives, 396 runs, and not one of them recorded which model answered.**

**36% and 27% are not two refusal rates. They are two rates of uttering one
sentence.**

**Cost per record trending down is not a fact about efficiency until the mix is
held. The cheapest record in this corpus is the one that teaches a reader the
least.**

**A suite that no state block lists is a suite that can be red for a week, and
this one was the first line of the runbook that would have found it.**

And three from F2:

**Kill trigger 3 compares record 60 against record 12, and nobody ever wrote
down what record 12 cost. The comparator was missing for eight sessions and the
gate would have found out last.**

**A number is only safe from re-labelling if the thing underneath it is
recorded too — the tier, and then the phase, and there is no third level
because nobody times a record twice.**

**A check deferred WITH its implementation described is a check specified
before it was tried, and F1's own correction is what it would have fired on.**

**A suite that prints no count can carry a skip forever, because nobody can
tell one skipped assertion from thirty. Two of the seven were printing none.**
