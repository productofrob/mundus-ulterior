# F2 — starting point for the next thread

*Written 2026-08-29 at the close of F1, at commit `577a0e2`. `PHASE2_PLAN.md`
is still the statement of what Block F is — W3, corpus 24 to 60, eight
sessions, gate G3, amended twice in advance. This file is the state and what F2
has to settle before it writes a single number.*

## Read these, in this order

| # | file | why |
| :---- | :---- | :---- |
| 1 | **this file** | state, what F2 is, and the comparator that does not exist |
| 2 | `F1_RESULT.md` | rulings 43-45, findings 30-31, and the correction at its foot |
| 3 | `F1_RULINGS.md` | **ruling 45 before designing the column.** It already decided the shape |
| 4 | `data/corpus_tiers.json` | the tier vocabulary and the target mix the column is reported against |
| 5 | `PHASE2_PLAN.md`, Block F section only | F1-F8 and the twice-amended G3 checklist |
| 6 | `PROGRESS.md` **last two sections only** | ~650 KB. Do not read it whole |

`F1_HANDOFF.md` and `F1_START.md` are superseded for the reading list and the
state. They are still the statement of what F1 WAS.

## State, as measured 2026-08-29

```
tree            clean, at F1's commit
                577a0e2  F1: five tiers, a target mix, and a suite that had
                         been red for a week
                a6442b6  F1_HANDOFF names the commit it was written at
                13a417d  FINDING 29's third mutation reported MISS, and the
                         MISS was right

corpus          24 records / 450 embedded / 0 pending
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                STILL THE DENOMINATOR. F3 moves it. F1 did not and F2 does not.

FIVE SUITES, not four. FINDING 31 is what that sentence cost.
INGEST          ingest.verify                    GREEN  (red 2026-08-22 to -29)
TIERS           ingest.test_fidelity         30   GREEN
ANSWER          eval.test_answer_eval       333   GREEN
RANKING         eval.test_ranking_check     236   GREEN
PART 7          answer.test_answer                GREEN, with ONE SKIP
UI              ui\test_build_ui_data.py         GREEN

mutations       scripts\mutate_part8.py      82   GREEN
                scripts\mutate_ranking.py   100   GREEN
                scripts\mutate_fidelity.py   24   GREEN, with BASELINE
                scripts\mutate_part7b.py     18   GREEN, with BASELINE
                scripts\mutate_ui_places.py   4   GREEN, with BASELINE

record tiers    11 verbatim_with_provenance / 0 verbatim_machine_english /
                1 published_translation_only / 11 catalogue_record /
                1 pointer_only
target at 60    25 / 10 / 5 / 19 / 1, regions levelled to 8-9, >= 4
                source-language records PER REGION, 8 gloss-capable,
                >= 6 expect_quoted_from_original cases

gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
floor           calibrated TRUE. ELIGIBLE, 4 sweeps, 3 dates — UNMOVED by F1
required        antikythera-absent, chinese-da-qin, muziris-cargo
known-failing   aksum-exports, vimose-runes, skz-titulature
candidate       weilue-chinese-quotation
rulings         1 to 45.  findings 1 to 31.
gates           G4 CLOSED. G3 is Block F's, amended twice in advance
                (ruling 39, ruling 45).
```

## What F2 is

`PHASE2_PLAN` F2: **minutes per record, in a column, from record 25.** No
curation. F3 is what moves the corpus.

Ruling 45 already settled the column's shape, in advance and for the reason
ruling 39 gives: **cost is reported PER TIER and against the declared mix**,
because "trending down" is otherwise satisfiable by curating cheaper records and
kill trigger 3 hangs off the number. Read it before designing anything.

## THE THING TO SETTLE ON DAY ONE, and it is not the schema

**Kill trigger 3's comparator does not exist.**

> *"if record 60 costs what record 12 cost, 200 is a staffing question rather
> than an engineering one"* — `PHASE2.md`, and `PHASE2_PLAN` F2 repeats it.

**Nothing anywhere records what record 12 cost.** The seed 24 were curated
before any column existed; there is no minutes figure for any of them, and none
can be reconstructed. So the trigger as written cannot be evaluated, and the
only trend Block F can actually measure is **within records 25 to 60**.

That is a different claim and a weaker one, and it has to be **declared before
the first number is written**, not discovered at G3. A comparator chosen after
the numbers are in is a comparator fitted to them — ruling 39's argument, for
the third time in this block. Say what kill trigger 3 is evaluated against, in
writing, in F2.

**And note what within-tranche does to n.** Per tier the tranche is 14 / 10 / 4
/ 8 records. A trend over eight catalogue records is not a measurement anyone
should stake 200 on, and saying so in F2 is cheaper than saying it in Block G.

## The second question, and it is ruling 45 one level down

**A single minutes number is gameable by re-labelling work.** If the column is
one figure per record, cost "trends down" as soon as source-hunting, rights
checking, placement or case-writing stops being counted as curation. That is
exactly the defect ruling 45 closed one level up — an aggregate satisfied by
changing what goes into it — and the fix is the same shape: **declare the phases
the minutes are divided into, before the first record is timed.**

Nobody times a record twice. Whatever the column does not carry on day one, it
never carries.

## What F1 already decided that F2 inherits

- **The cost ledger is a SIDECAR, not a record field.** Ruling 43's reason
  applies unchanged and does not expire: `canonical_record_text` hashes the
  whole parsed record, so a `minutes` key moves `corpus_digest` — the
  denominator of 396 Block E runs and 165 arm runs. This is the second file that
  would have done it.
- **And not under `data/seed_corpus/`.** `iter_seed_records` refuses a `.json`
  at that depth. `data/corpus_tiers.json` is the precedent; put the ledger
  beside it.
- **The tier is derived, so the column gets it free.** `derive_record_tier`
  reads it from the record's chunks. The column carries the tier as data, and
  the derivation is what checks it.

## What is owed, carried forward

```
1  FINDING 30's load-time check, DEFERRED TO F2 IN WRITING: goldset refuses a
   case whose archived_status names a floor.json state that floor.json
   contradicts. One token against one file, not prose interpretation.
2  `answer.test_answer` prints `skip sqlglot not installed`. A skip is not a
   pass, and the SQL-parse guards have not run on the host. It is one
   `pip install -r requirements-dev.txt`. Do it in F2, not in F3.
3  the BASELINE check is in four harnesses of seven. mutate_ranking,
   mutate_places and mutate_recover still lack it.
4  ruling 40's article_added is STILL unverified against any live run.
5  muziris-cargo, REQUIRED, is 3/5 on the arm and 12/12 on the declared one.
6  `eval.answer_eval --archives` pools arms into one report (FINDING 29).
7  G3's amendment costs a SECOND session at 60, on a second UTC date, ~198
   chat calls. Ruling 39 booked the days. Do not discover this in F8.
8  `ingest/verify.py` check 9 asserts `len(docs) == 24`. F3's, not F2's: it
   is correct today and F3 breaks it on purpose, in the same commit as the
   records or not at all.
```

## Traps

Everything in `F1_START.md`'s list still applies — the bridge, `git` locks,
per-file line endings, `BASELINE:`/`UNVERIFIED`, ambiguous mutation anchors.
Three from F1:

- **`ingest.verify` is a suite and belongs in every green check.** FINDING 31:
  it was red for a week because no state block listed it, and it is the first
  line of the runbook F3 runs after every sub-tranche.
- **A record cannot carry a new field.** Ruling 43. The digest is the reason and
  the reason does not expire.
- **A number transcribed into a document drifts from the thing it describes.**
  F1 put the assertion count into five files as 29 when the suite had 30, and
  the fix was to make the suite print its own count. Anything F2 writes into
  `PROGRESS.md` should be produced by something that can be re-run.

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

And one from F2's own starting position:

**Kill trigger 3 compares record 60 against record 12, and nobody ever wrote
down what record 12 cost.**
