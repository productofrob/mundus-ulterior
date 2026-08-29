# F3 — starting point for the next thread

*Written 2026-08-29 at the close of F2, at commit `a74a307`. `PHASE2_PLAN.md`
is still the statement of what Block F is — W3, corpus 24 to 60, eight
sessions, gate G3, now amended THREE times in advance. This file is the state,
and the three things F3 has to settle before it curates a single record.*

**F3 is the first thread in this project that MOVES THE CORPUS.** Everything
before it declared, measured or built. `26e4a683` has been the denominator of
every archived number since Part 3, and F3 is what ends that.

## Read these, in this order

| # | file | why |
| :---- | :---- | :---- |
| 1 | **this file** | state, and the clause `floor.json` does not have |
| 2 | `F2_RESULT.md` | rulings 46-48, finding 32, and what F2 did NOT do |
| 3 | `F2_RULINGS.md` | **ruling 47 before timing anything.** The phases are fixed and a record that omits one is refused |
| 4 | `F2_RUNBOOK.md` | section 3, and the Reference at the foot: the CLI F3 lives in |
| 5 | `data/corpus_tiers.json` | the mix F3 is measured against |
| 6 | `data/curation_cost.json` | the ledger F3 writes into |
| 7 | `PHASE2_PLAN.md`, Block F section only | F3-F8 and the thrice-amended G3 |
| 8 | `PROGRESS.md` **last two sections only** | ~676 KB. Do not read it whole |

`F1_START.md`, `F1_HANDOFF.md` and `F2_START.md` are superseded for the
reading list and the state. They are still the statement of what F1 and F2
WERE. **`F2_START.md`'s state block says "FIVE SUITES" above a list of six;
there are seven. Do not copy a count out of it.**

## State, as measured 2026-08-29 at `a74a307`

*Every number below was printed by the thing it describes. None was
transcribed from an earlier document — which is F1's correction, F2's two
count corrections, and the reason the two uncounted suites now count.*

```
tree            clean, at F2's commit
                a74a307  F2: a column that cannot be gamed, and a comparator
                         that was never measured
                577a0e2  F1: five tiers, a target mix, and a suite that had
                         been red for a week

corpus          24 records / 59 chunks   RECOMPUTED at the close
                450 embedded / 0 pending  CARRIED from F2's block; needs the
                                          database to re-measure
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                RECOMPUTED and matched. CHECKED, not assumed.
                >>> F3 MOVES IT. <<<

SEVEN SUITES. Not five, not six. The list is the count, not a sentence
about the list.
INGEST          ingest.verify                    GREEN   <- FIRST, always
TIERS           ingest.test_fidelity         30   GREEN
COST            ingest.test_cost             46   GREEN
ANSWER          eval.test_answer_eval       343   GREEN
RANKING         eval.test_ranking_check     236   GREEN
PART 7          answer.test_answer          150   GREEN, no skip (sqlglot in)
UI              ui\test_build_ui_data.py     14   GREEN

mutations       270 verified on the host, six harnesses, no MISS, no
                UNVERIFIED, and no BASELINE warning in any of them
                scripts\mutate_ranking.py   100   GREEN
                scripts\mutate_part8.py      87   GREEN, restored byte for byte
                scripts\mutate_cost.py       37   GREEN, with BASELINE
                scripts\mutate_fidelity.py   24   GREEN, with BASELINE
                scripts\mutate_part7b.py     18   GREEN, with BASELINE
                scripts\mutate_ui_places.py   4   GREEN, with BASELINE

cost ledger     0 records timed / 24 excused with a written reason
                comparator within_tranche (ruling 46)
                7 phases fixed (ruling 47); min_n_to_read_as_a_trend 10

record tiers    11 verbatim_with_provenance / 0 verbatim_machine_english /
                1 published_translation_only / 11 catalogue_record /
                1 pointer_only
target at 60    25 / 10 / 5 / 19 / 1, regions levelled to 8-9, >= 4
                source-language records PER REGION, 8 gloss-capable,
                >= 6 expect_quoted_from_original cases

gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
                7 declare a floor_state, checked against floor.json (F32)
floor           calibrated TRUE. 4 sweeps, 3 dates.
                >>> ALL FOUR AT 24 RECORDS, digest 26e4a683. <<<
rulings         1 to 48.  findings 1 to 32.
gates           G4 CLOSED. G3 is Block F's, amended THREE times in advance
                (ruling 39, ruling 45, ruling 46).
```

## THE THING TO SETTLE ON DAY ONE, and it is not a record

**`floor.json`'s calibration scope has no corpus clause, and F3 is what makes
that matter.**

Measured, not argued:

```
floor.calibrated_from_sweeps names four archives.
  20260826T103006 / 20260826T115846 / 20260827T103048 / 20260828T103215
ALL FOUR carry, in their own corpus_version block:
  seed_record_count      24
  seed_corpus_digest     26e4a683...

floor.calibration_scope's clauses:
  session identity   |   min_cases_per_sweep 30   |   arm (ruling 36)
There is no clause about the corpus.

eval/calibrate_floor.py contains ZERO occurrences of the string "corpus".
```

**The data is already in every archive and the rule does not read it.**
FINDING 14 put `corpus_version` into every sweep precisely so that a corpus
that moved could not go unnoticed; `calibration_scope` was then written twice —
once on 2026-08-26, once by ruling 36 — without ever reaching for it.

**The moment F3 ingests record 25, a sweep at 33 records satisfies every clause
of the scope and calibrates a floor that was set at 24.** That is ruling 36's
own sentence, one dimension over:

> *"without it, `floor.json`'s own anti-loophole would have INSISTED that a
> temperature-1 sonnet sweep calibrate a floor set on greedy haiku."*

Substitute the corpus for the arm and the sentence is unchanged and unanswered.

**And this is not hypothetical, because two entries in the file already
anticipate the clause it does not have.** `promotion_candidates.weilue-chinese-
quotation.bar` reads *"3/3 in each of THREE sessions on THREE distinct UTC
dates, at 60 records"*, and `demotions.vimose-runes.reinstated_when` says the
same. Both entries know the corpus is part of a claim's identity. The rule that
decides what may calibrate does not.

**Decide, in writing, before record 25 is ingested:** is the floor in force
during the tranche, suspended for its duration, or re-calibrated at 60 — and
what is a mid-tranche sweep allowed to do to it? A rule written after the first
sub-tranche is a rule written by someone who has seen what the first
sub-tranche did to the numbers. Ruling 39's argument, for the fifth time in
this block, and the last block in which it can be made in advance.

## The second question: the mix is DECLARED but not ALLOCATED

Ruling 44 declares the mix at 60. **It does not say which sub-tranche carries
what**, and F3-F7 curate roughly nine records at a time.

Curated by convenience, F7 inherits every unmet constraint at once:

```
per tier            14 / 10 / 4 / 8 new records
per region          levelling to 8-9 each
per region          >= 4 records carrying SOURCE-LANGUAGE text
                    Southeast Asia has ZERO today and needs four
gloss-capable       8, and only three tiers can carry one
quoted-from-original >= 6 cases, against 1 today
```

Southeast Asia is the one to look at first: **zero** records carrying
retrieval-eligible source-language text, which is why all four of its gold
cases sit on find records. Every aggregate tier target above is satisfiable
inside Arabia and South Asia alone, and F1 declared the per-region floor for
exactly that reason.

An allocation decided at F7 is an allocation fitted to what was already
curated. **Allocate the 36 across the sub-tranches before the first one**, and
let the hard regions go first while there is still room to fail and retry.

## The third: what "re-running the sweep at each" actually costs

`PHASE2_PLAN` F3-F7 is headed *"Curate in sub-tranches of ~9, re-running the
sweep at each"*. The command block underneath it is:

```
python -m ingest.verify
python -m ingest.run_ingest
python -m ingest.run_embed
python -m eval.run_ranking_check
python ui\build_ui_data.py --verify
```

**That is the RANKING check, not the answer sweep.** Read the heading the other
way and it is ~198 chat calls per sub-tranche, four or five times over, on top
of the two sessions at 60 that ruling 39 already booked. Those two readings are
a cheap block and a block that runs out of days.

Settle which, in writing, in F3. G3 asks for *"full sweep re-run at 60"* —
one sweep at 60, plus the amendment's second date. Nothing in the gate asks for
a full sweep at 33, 42 or 51.

## What F2 decided that F3 inherits, and cannot renegotiate cheaply

- **`ingest.verify` goes RED if a record reaches the corpus with no ledger
  row**, and RED if a clock is left running. Both deliberate. The minutes exist
  on the day the record is made and never again.
- **The seven phases are fixed** and a record entry that omits one is refused.
  A phase that took no time records **zero** — an absent phase and an
  unrecorded phase are the same shape on disk.
- **`python -m ingest.cost_log report` is the only place a curation-cost number
  may be read from.** Nothing in any document may carry a cost figure the
  report did not print.
- **The comparator is `within_tranche`** and a seed record may not be named as
  a baseline. `min_n_to_read_as_a_trend` is 10, so `published_translation_only`
  (4 new) and `catalogue_record` (8 new) can NEVER be read as trends in Block
  F, whatever their numbers do.
- **A record cannot carry a new field.** Ruling 43, and there are now TWO
  sidecars for that one reason.
- **A case in a floor state declares it** in `floor_state`; absent means
  `none`; both directions are checked at load.

## What is owed, carried forward

```
1  `ingest/verify.py` check 9 asserts `len(docs) == 24`. THIS ONE IS F3'S.
   It is correct today and F3 breaks it on purpose, in the same commit as the
   records or not at all. Loosening it in advance is the floor lowered to
   what is currently passing.
2  the BASELINE check is in five harnesses of eight. mutate_ranking,
   mutate_places and mutate_recover lack it; mutate_distractors is the
   fourth and is a different shape (it mutates a live view).
3  ruling 40's article_added is STILL unverified against any live run.
4  muziris-cargo, REQUIRED, is 3/5 on the arm and 12/12 on the declared one.
5  `eval.answer_eval --archives` pools arms into one report (FINDING 29).
6  G3's amendment costs a SECOND session at 60, on a second UTC date, ~198
   chat calls. Ruling 39 booked the days. Do not discover this in F8.
7  `ingest/test_sql.py` gains sqlglot checks and needs the DATABASE. It has
   not been run with sqlglot present. Guards that have never run are guards
   nobody knows work.
8  the `verse` and `documentary` confidence profiles are at n=1 and go
   LOAD-BEARING the moment the first verbatim_machine_english record lands --
   which the mix says is ten of the thirty-six. PHASE2_PLAN says budget a
   session and set `calibrated` honestly. F3 is where that starts being true.
```

## Traps

Everything in `F1_START.md` and `F2_RESULT.md` still applies. The four that
cost time most recently:

- **Do NOT run a mutation harness through the device bridge.** It is killed at
  the call timeout, between applying a mutation and restoring the sources. F2
  lost `eval/answer_eval.py` to it — every quotation assertion in the scorer
  disabled, in the working tree, with the suites still green because none had
  been re-run. `git status` found it in one line.
- **`git checkout -- <path>` does not work through the bridge**, which cannot
  unlink. `git show HEAD:<path>` written back as bytes does. A `git add`
  through the bridge also leaves a stale `.git/index.lock`; from PowerShell,
  `del .git\index.lock`.
- **`ingest.verify` is a suite and is the FIRST line of the sub-tranche
  block.** FINDING 31: it was red for a week because no state block listed it.
- **A number transcribed into a document drifts from the thing it describes.**
  Three instances in two days: F1's assertion count, F2_START's suite count,
  and F1's harness count. Anything F3 writes into `PROGRESS.md` should be
  produced by something that can be re-run.

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
a suite that prints no count can carry a skip forever.**

**Kill trigger 3 compares record 60 against record 12, and nobody ever wrote
down what record 12 cost.**

**A check deferred WITH its implementation described is a check specified
before it was tried.**

And one from F3's own starting position:

**The floor is calibrated on four sweeps at 24 records, and the rule that
decides what is allowed to calibrate it cannot see the corpus.**
