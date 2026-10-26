# F1 — starting point, after the sonnet arm

*Written 2026-08-28 at the close of the arm thread. `F1_START.md` is still the
statement of WHAT F1 IS and its two curation notes are unchanged — read it. This
file replaces its reading list and its state block, both of which predate the
arm.*

## Read these, in this order

| # | file | why |
| :---- | :---- | :---- |
| 1 | **this file** | state, and what the arm changed for F1 |
| 2 | `ARM_RESULT.md` | the arm, FINDING 28 and FINDING 29. **Read 28 before writing a refusal case** |
| 3 | `F1_START.md`, from *"What F1 is"* onward | the tiering policy, the target mix, and the two curation notes. Its state block and reading list are superseded by this file |
| 4 | `F0_RULINGS.md` | rulings 36-42. 40 carries a correction |
| 5 | `PHASE2_PLAN.md`, Block F section only | F1-F8 and the AMENDED G3 checklist |
| 6 | `eval/gold/floor.json` | three states, and three `known_failing_cases` entries that now carry a cross-arm note |
| 7 | `PROGRESS.md` **last two sections only** | ~659 KB. Do not read it whole |

## State, as measured 2026-08-28

```
tree            clean, at the arm thread's last commit
                13a417d  the MISS: a recorded arm with no witness
                7d34272  the sonnet arm: 165 runs, two findings, and a floor
                         that did not move
                dcc285a  PROGRESS.md catches up two blocks, and F1 gets a
                         starting point

corpus          24 records / 450 embedded / 0 pending
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                STILL THE DENOMINATOR. F3 moves it. F1 and F2 do not.

ANSWER          eval.test_answer_eval       333   GREEN   (was 321)
mutations       scripts\mutate_part8.py      82   GREEN   (was 75)
                scripts\mutate_part7b.py     18   GREEN
                scripts\mutate_ui_places.py   4   GREEN
RANKING         eval.test_ranking_check     236   GREEN
mutations       scripts\mutate_ranking.py   100   GREEN
PART 7          answer.test_answer                GREEN
UI              ui\test_build_ui_data.py         GREEN

gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
floor           calibrated TRUE. ELIGIBLE, 4 sweeps, 3 dates — UNMOVED by the arm
required        antikythera-absent, chinese-da-qin, muziris-cargo
known-failing   aksum-exports, vimose-runes, skz-titulature
                all three now carry a CROSS-ARM note. Two of them pass on
                chat-strong and the file used to say nothing about it.
candidate       weilue-chinese-quotation
archives        eval/sweeps/  9 haiku sweeps, 396 runs in scope
                eval/arms/    1 sonnet arm, 165 runs, its own gate
rulings         1 to 42.  findings 1 to 29.
gates           G4 CLOSED. G3 is Block F's, AMENDED IN ADVANCE.
```

**The deadline that governed the last thread is discharged.** The arm ran inside
the frozen-corpus window and is archived beside `26e4a683`. Nothing now blocks
F1, and F1 does not move the corpus.

## What the arm changed for F1's curation

`F1_START.md`'s two curation notes stand. The arm adds three.

- **`expect_refusal` tests a SENTENCE, not a behaviour.** FINDING 28. A correct,
  cited, precisely-worded refusal that does not utter the canonical sentence
  scores as an answer. Under the declared arm haiku emits it 144 times out of
  144, so nothing archived is affected — but a case author writing eight more
  refusal cases needs to know that `expect_refusal: true` is a substring test
  and that `refusal_is_correct_because` is where the actual claim lives.
- **The gloss arm is starved, and the arm proved the arm has teeth.**
  `F1_START.md` says 3 gloss cases against 22 answerable is a fact about the
  corpus. `vimose-runes` went 0/12 to 5/5 on the second model with a real hedged
  gloss, so the gloss assertions are discriminating rather than impossible. Choose
  the 36 new records so the balance can be met honestly.
- **Any new universal over `eval/answer_runs/` must filter by arm.** FINDING 29.
  That directory now holds two arms and will hold more. `every archived X` is a
  claim about a model, and `eval.answer_eval.archives_on_arm` is how a check says
  which one.

## What is owed, carried forward

```
1  ruling 40's article_added is unverified against any live run.
   aksumite-coin-imagery is 0/5 with ZERO resolved quotations on the arm.
2  muziris-cargo, REQUIRED, is 3/5 on the arm and 12/12 on the declared one.
3  `eval.answer_eval --archives` pools arms into one report. FINDING 29 fixed
   the guards and left the CLI, deliberately and in writing.
4  the baseline check that mutate_part8 gained on 2026-08-28 is still not in
   the other five harnesses.
5  G3's amendment costs a SECOND session at 60, on a second UTC date, ~198
   chat calls. Ruling 39 booked the days. Do not discover this in F8.
```

## Traps

Everything in `BLOCK_D_START.md`, `D4_START.md`, `BLOCK_E_START.md`,
`BLOCK_E_RUNBOOK.md`, `BLOCK_F_START.md` and `F1_START.md` still applies. The
five worth re-reading are in `F1_START.md`'s own list — the bridge, `git`
locks, per-file line endings, `BASELINE:`/`UNVERIFIED`, and ambiguous mutation
anchors. Two more from this thread:

- **A MISS is not a pass and is not noise.** Mutation 80 broke `payload_arm` and
  no guard noticed, because the serving-stack echo agreed with the field it had
  just been told to ignore. The harness was reporting that a line of code has no
  witness. Fixing the guard is the response; re-pointing the mutation at a guard
  that already fails is not.
- **A red guard after a live run may be the RUN's result, not a defect.**
  `GUARD every archived Aksum answer fails` went red because the arm passed that
  case once in five. `BLOCK_D_START` warns about the misreading in the other
  direction; this is the same warning and it cost twenty minutes.

## The sentences that travel

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310.

**Four sessions read 0.727272… and one of them was different. The pass rate
cannot see change.**

**Nine archives, 396 runs, and not one of them recorded which model answered.**

**0.7273 and 0.7636 are three points apart, and eleven of thirty-three cases
moved between them.**

**36% and 27% are not two refusal rates. They are two rates of uttering one
sentence.**
