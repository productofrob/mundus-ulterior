# Block E day 2 — starting point for the next thread

*Written 2026-08-26 at the close of day 1. Supersedes nothing: `BLOCK_E_START.md`
is still the statement of what Block E is, and `BLOCK_E_RUNBOOK.md` is still how
to run it. This is the state, and the four things that must not change.*

## Read these, in this order

| # | file | why |
| :---- | :---- | :---- |
| 1 | **this file** | state, the freeze, and what day 2 is |
| 2 | `BLOCK_E_DAY1_RESULT.md` | findings 19-22, and the four corrections owed |
| 3 | `BLOCK_E_RUNBOOK.md` | the commands, the traps, the five decisions |
| 4 | `BLOCK_E_DAY1_DRYRUN.md` | the predictions, committed before the runs |
| 5 | `eval/gold/floor.json` | read whole. `calibrated: false` is still true |
| 6 | `PROGRESS.md` **last section only** | ~594 KB. Do not read it whole |

## State, as measured 2026-08-26

```
tree            a1850fd, clean
                a1850fd  Block E day 1: two sessions, 198 runs, floor met in both
                2a4077d  Block E prep: the variance decomposition, the calibration
                         scope, and a demotion that costs something to write
                fceec7a  Block E: the probe's null result, and why haiku

corpus          24 records / 450 embedded / 0 pending
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                asserted at BOTH ends of BOTH day-1 sweeps. corpus_moved None.

ANSWER          eval.test_answer_eval       283   GREEN
mutations       scripts/mutate_part8.py      61   GREEN
RANKING         eval.test_ranking_check     231   GREEN
mutations       scripts/mutate_ranking.py    97   GREEN

gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
sweeps          7 archived. 3 carry no session identity and never will.
                4 do: 2026-08-24, 2026-08-25, and TWO on 2026-08-26.
distinct dates  IN SCOPE: 1  (2026-08-26). The floor requires 3.
floor           calibrated: false. MET on both day-1 sessions.
serving stack   {id, model} only. No fingerprint. Provider drift and sampling
                variance are NOT separable in these archives — stated limit.
```

## What day 2 is

**One command, and nothing else.**

```powershell
python -m eval.run_answer_sweep --repeat 3 --session-label "Block E day 2" `
  *> eval\block-e-day2.txt
```

33 cases x 3 repetitions = **99 chat calls**, about 10 minutes. Day 1 ran
10:20-10:30 and 11:48-11:58; the sweep is faster than `BLOCK_E_RUNBOOK`
predicted because the embedding pass is not the bottleneck it looked like.

The pre-flight in `BLOCK_E_RUNBOOK.md` still applies: the four suites green on a
clean tree before the first call. **A dry run is optional on day 2** — retrieval
is frozen, day 1's dry run is committed, and a second one costs 33 embedding
requests to re-print an identical page. Run it if you want the corpus digest
asserted before spending calls; the sweep asserts it at both ends regardless.

Then:

```powershell
python -m eval.decompose
python -m eval.calibrate_floor       # will still REFUSE: 2 dates, needs 3
git add -A ; git commit -F commit-blocke-day2.txt
```

## THE FREEZE — four corrections are owed and NONE may be made before day 3

All four are recorded in `BLOCK_E_DAY1_RESULT.md`. All four wait. The precedent
is `calibrate_floor`'s self-contradicting last line, carried as a recorded
defect through the whole of D4 and fixed between blocks.

```
1  floor.json   weilue-chinese-quotation's defect entry is FALSIFIED. It passed
                3/3 in both day-1 sessions, quoting Classical Chinese. The entry
                was inferred from 16 runs of chinese-da-qin; the case itself had
                never been run.
2  floor.json   demotions.vimose-runes: the diagnosis "retrieval margin, not
                generation" is contradicted by 33 cases, and reinstated_when is
                keyed to a fix the evidence says is neither necessary nor
                sufficient.
3  code         _serving_stack includes the per-call `id`, so each sweep archives
                99 "distinct stacks" and prints an alarming meaningless line.
                Ignore that line. The id belongs on the row, not the identity.
4  code         serving_stack.model reads the alias `chat-default` in the sweep
                path. The row's own `model` field is correct.
```

**If anything else is found on day 2, it is written down and not fixed.** A
correction applied between days turns three observations into one, and the whole
block is 297 calls of evidence that only exists because nothing moved.

## The dates

```
day 1   Wednesday 2026-08-26  DONE — two sessions, 198 runs
day 2   Thursday  2026-08-27
day 3   Friday    2026-08-28
```

**Amended 2026-08-26, at the close of day 1, from 29 / 31.** Nothing requires
the days to be far apart: `min_distinct_dates` is 3 and its note only rules out
compressing runs into one day. The original 29 / 31 came from a recommendation
made before any date effect had been measured, on the guess that wider gaps
sample more of it. Day 1 measured one, so the guess is no longer the best
available reasoning, and three consecutive dates replicate the SMALLEST date
crossing twice — the condition nothing has ever measured.

**The trade-off, stated rather than discovered later:** with two ~24h gaps and
no long one, this design cannot tell whether the loss keeps growing with
separation. D4's 31-hour, +61% observation sits OUTSIDE the range being
sampled, and day 3 will not be able to speak to it. That is accepted.

**This is the second amendment and it should be the last.** A booking that moves
twice is a schedule; one that moves three times is not a booking. Neither
amendment was made after seeing a number that either one selects for, and both
are recorded — but the argument only holds while that stays true.

Each session must sit wholly inside its own UTC date. You are UTC+1: start after
01:00 BST, finish before 01:00 BST the next morning. An evening run is fine.

## What day 2 will decide

Day 1 measured a date effect for the first time, by accident, because two
sessions shared a date:

```
the six D4 cases, two sessions, TWO DATES (31h)      text agreement lost +61%
the six D4 cases, two sessions, ONE DATE  (90min)    text agreement lost +28%
```

Day 2 is the first **planned** second date on the full 33-case set. It turns
that one comparison into a design:

```
2026-08-26 S1 vs S2     within-day, 90 minutes      MEASURED: +11% over 33 cases
2026-08-26 vs 08-27     across-day, ~24 hours       day 2 measures this
2026-08-27 vs 08-28     across-day, ~24 hours       day 3 REPLICATES it
2026-08-26 vs 08-28     across-day, ~48 hours       derived, for free
```

If the across-day loss on 33 cases lands near +11%, the date boundary is not
the thing and D4's +61% was its case sample. If it lands well above, the date
boundary is real at scale and day 1's within-day figure is the floor of it.
**Either answer is worth the 99 calls, and neither is available any other way.**

Because the two gaps are the same size, day 3 is a genuine REPLICATION rather
than a second point on a curve: two independent measurements of the smallest
possible date crossing. That is the stronger design for deciding *whether* a
date boundary matters, and the weaker one for deciding *how much it grows*.

Three specific things to watch:

- **`weilue-chinese-quotation`.** 3/3 twice on one date. A third pass on a
  second date makes the falsification of its defect entry unarguable. A failure
  on day 2 is more interesting still.
- **Non-Latin characters in the capture.** Seven cases produced them on day 1
  through a `*>` redirect on PowerShell 5.1 with no UnicodeEncodeError. That is
  FINDING 10's guard being exercised on the answer path for the first time.
  Confirm it holds; do not build anything to prove it.
- **`vimose-runes` text count.** 3 distinct texts in S1, 2 in S2, verdict 0/3 in
  both. Stable verdict, moving text, within one day.

## Traps added on 2026-08-26

Everything in `BLOCK_D_START.md`, `D4_START.md`, `BLOCK_E_START.md` and
`BLOCK_E_RUNBOOK.md` still applies. Four to add:

- **Do not paste the dry run and the real sweep as one block.** That is how day 1
  ran twice: the dry run printed to the console, the real sweep ran silently into
  the capture, and it looked like nothing had happened. Run them separately and
  check `eval/sweeps/` before starting anything.
- **`*>` truncates on open.** The second day-1 run overwrote the first's capture
  before writing a byte, and it stayed 0 bytes with a stale timestamp until the
  process exited. **Give every run its own capture filename.** The sweep archive
  is the evidence; the capture is a convenience that can be destroyed by the next
  command.
- **A running sweep looks identical to a finished one.** Count archives, not
  console output: `(Get-ChildItem eval\answer_runs\<date>*.json).Count`, and check
  `eval/sweeps/` for the file that only appears at the end. A count ABOVE the
  expected total means a second run, not a retry.
- **`git` through the Cowork bridge leaves `.git/index.lock` behind** — even a
  read-only-looking `git status`, and the bridge cannot delete it. Happened twice
  on 2026-08-26, the second time after the trap was written down. Use
  `git --no-optional-locks status`, or do not run git through the bridge.

## What is NOT a finding

`aksum-exports` failing. Tracked, out of `required_cases`, not closed by Block E.

`vimose-runes` failing. Demoted 2026-08-26 on two dates of evidence, now three.
Reported beside the floor verdict for ever and never subtracted from it.

**`weilue-chinese-quotation` is no longer in this list.** It passes. Its entry
survives to day 3 only because of the freeze, not because anyone believes it.

## The sentence that travels

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310.

The clause that rode with those two since Part 7 — *"and the answer path has
still never quoted a non-English source text"* — was retired on 2026-08-26 by a
case that had never been run. Do not carry it forward.
