# Block E day 3 — starting point for the next thread

*Written 2026-08-27 at the close of day 2. Supersedes nothing: `BLOCK_E_START.md`
is still the statement of what Block E is, `BLOCK_E_RUNBOOK.md` is still how to
run it, and `BLOCK_E_DAY2_START.md` is still where the schedule argument lives.
This is the state, the freeze, and the one day that closes the block.*

## Read these, in this order

| # | file | why |
| :---- | :---- | :---- |
| 1 | **this file** | state, the freeze, and what day 3 is |
| 2 | `BLOCK_E_DAY2_RESULT.md` | findings 23-24, the FIVE owed corrections, and day 3's committed predictions |
| 3 | `BLOCK_E_RUNBOOK.md` | the commands, the traps, the five decisions, and the DAY 3 closing sequence |
| 4 | `BLOCK_E_DAY1_RESULT.md` | findings 19-22 — and note that 19's date claim was withdrawn on day 2 |
| 5 | `eval/gold/floor.json` | read whole. `calibrated: false` is still true, and today is the day that can change it |
| 6 | `PROGRESS.md` **last section only** | ~594 KB. Do not read it whole |

## State, as measured 2026-08-27

```
tree            4860711, clean
                4860711  Block E day 2: the date effect was measured, and it is
                         not there
                325a82b  Block E day 1: result, findings 19-22, day 2 handoff,
                         dates amended to 27/28
                4d746d9  Block E day 1: result, findings 19-22, and the day 2
                         handoff

                NOTE: `BLOCK_E_DAY2_START.md` records day 1's tree as a1850fd.
                That commit was amended into 325a82b when the dates were
                amended at the close of day 1. Same content, different SHA.
                Do not go looking for a1850fd.

corpus          24 records / 450 embedded / 0 pending
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                asserted at BOTH ends of ALL THREE sessions. corpus_moved None.

ANSWER          eval.test_answer_eval       283   GREEN
mutations       scripts/mutate_part8.py      61   GREEN
RANKING         eval.test_ranking_check     231   GREEN
mutations       scripts/mutate_ranking.py    97   GREEN

gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
sweeps          8 archived. 3 carry no session identity and never will.
                5 do: 2026-08-24, 2026-08-25, TWO on 2026-08-26, 2026-08-27.
in scope        3 sweeps, 297 runs, 33 cases, one denominator
distinct dates  IN SCOPE: 2  (2026-08-26, 2026-08-27). The floor requires 3.
floor           calibrated: false. MET on all three Block E sessions.
serving stack   {id, model} only. No fingerprint. Provider drift and sampling
                variance are NOT separable in these archives — stated limit.
```

## What day 3 is

**The same one command, and then the closing sequence that ends the block.**

```powershell
python -m eval.run_answer_sweep --repeat 3 --session-label "Block E day 3" `
  *> eval\block-e-day3.txt
```

33 cases x 3 repetitions = **99 chat calls**, about 10 minutes. Days 1 and 2
each ran 10:20-10:30 UTC. **Start in the same morning slot if you can**: day 2
began 24 hours and 29 seconds after day 1 S1, and holding that pattern makes
day 3 a genuine replication rather than a third condition.

The pre-flight in `BLOCK_E_RUNBOOK.md` still applies: **the four suites green
on a clean tree before the first call.** A dry run remains optional and is not
recommended — retrieval is frozen, two dry runs are committed, and a third
costs 33 embedding requests to reprint a known page. The sweep asserts the
corpus digest at both ends regardless.

Then, and this part is different from days 1 and 2 — this is the sequence that
closes the block:

```powershell
python -m eval.decompose --write        # G4: "with the data archived"
python scripts\probe_serving_stack.py   # ONE chat call. compare to day 1.
python -m eval.calibrate_floor          # read the report. it should be ELIGIBLE.
python -m eval.calibrate_floor --write  # ONLY if the report above is ELIGIBLE
git add -A ; git commit -F commit-blocke-day3.txt
```

Day 1's probe returned `{"id": …, "model": "anthropic/claude-haiku-4-5-20251001"}`
and nothing else. A second reading at the far end of the block either confirms
that the serving stack did not move under 297 calls, or is a finding. Either
way it is one call and it belongs in the block result.

## THE FREEZE — five corrections are owed, and it LIFTS when day 3 is archived

All five are recorded in `BLOCK_E_DAY2_RESULT.md`. **None may be applied before
day 3's sweep and its closing sequence are committed.** After that commit, the
freeze is over and they are the first work of the next step.

```
1  floor.json   weilue-chinese-quotation's defect entry is FALSIFIED. 9/9 across
                three sessions and two dates, one distinct text throughout. The
                entry was inferred from 16 runs of chinese-da-qin; this case had
                never been run when it was written.
2  floor.json   demotions.vimose-runes: the diagnosis "retrieval margin, not
                generation" is contradicted by 33 cases, and reinstated_when is
                keyed to a fix the evidence says is neither necessary nor
                sufficient. The DEMOTION stands — 0/3 on four dates now. The
                recorded reasoning does not.
3  code         _serving_stack includes the per-call `id`, so each sweep archives
                99 "distinct stacks" and prints an alarming meaningless line.
                Ignore that line. The id belongs on the row, not the identity.
4  code         serving_stack.model reads the alias `chat-default` in the sweep
                path. The row's own `model` field is correct.
5  code         run_answer_sweep has no --progress and never flushes, so a
                ten-minute 99-call sweep shows nothing until it exits. Fix:
                --progress writing one line per completed cell to stderr with
                flush=True, so `*>` still captures everything while a plain run
                is watchable.
```

**5 must not be applied before day 3's run.** Days 1 and 2 both went through
`*>` on PowerShell 5.1, and that redirect is itself under observation — it is
how FINDING 10's stdout guard is being exercised on the answer path. Changing
the invocation would make day 3's capture the only one produced a different
way, on the one day whose entire purpose is to replicate the other two. Watch
the run from a second window instead; the script is at the bottom of this file.

**If anything else is found on day 3, it is written down and not fixed** — at
least until the closing sequence is committed. The block is 297 calls of
evidence that only exists because nothing moved, and the last day is not the
day to spend that.

## What day 3 decides, and the predictions already committed against it

Day 2 measured the date boundary and found it is not a boundary. Day 3 is the
**replication** — two independent measurements of the smallest possible date
crossing — plus one 48-hour pair that comes free.

These were written into `BLOCK_E_DAY2_RESULT.md` and committed at 4860711,
**before day 3 ran**. Do not revise them; score against them.

```
2026-08-27 vs 2026-08-28   ~24h, the REPLICATION   predicted +6 to +12 pts
2026-08-26 vs 2026-08-28   ~48h, derived for free  predicted +6 to +12 pts
the 27 cases, either pair                          predicted +5 to +8 pts
the verdict decomposition, 33 x 4 x 3 = 396 runs   predicted case 100%
```

**FINDING 23 is wrong if either across-date figure exceeds about +20 pts, or if
the 48-hour pair loses materially more than the 24-hour pairs.** The second is
the one to watch: it is the only thing in this design that can speak at all to
separation growing with distance, and `BLOCK_E_DAY2_START` already recorded
that this block cannot properly answer that question. A 48-hour pair inside the
same band makes FINDING 23 harder to dislodge without settling it.

For reference, what day 2 measured:

```
S1 vs S2   same date, 88 min     within 85%   across 75%   +10.6 pts
S1 vs D2   ACROSS DATE, 24h00m   within 82%   across 74%   + 7.9 pts
S2 vs D2   ACROSS DATE, 22h32m   within 88%   across 77%   +11.1 pts
the 27 cases D4 never ran        +6.8 / +6.0 / +6.2
the 6 D4 cases                   +27.8 / +16.7 / +33.3
```

Three specific things to watch:

- **`weilue-chinese-quotation`.** 3/3 three times, one distinct text, nine runs.
  A fourth pass ends the argument. A failure on day 3 is more interesting still.
- **Non-Latin characters in the capture.** Held on both dates through `*>` on
  PowerShell 5.1 with no UnicodeEncodeError. Confirm it holds a third time; do
  not build anything to prove it.
- **`vimose-runes` text count.** 3 / 2 / 2 distinct texts, verdict 0/3 in all
  three. Stable verdict, moving text, within a day and across one.

## Gate G4, and what closing it needs

```
[x] >=30 cases, each with an explicit expected behaviour     33
[ ] run 3x on >=3 separate days                              2 of 3 dates
[x] per-case and per-session stability as separate numbers   99/99, 33/33
[x] a stated VARIANCE DECOMPOSITION                          297 runs, 2 dates
                                                             --write still owed
[ ] the floor recalibrated, OR the reason it cannot be       REFUSED, 2 dates
```

Day 3's sweep answers box 2. `decompose --write` answers the archiving half of
box 4. `calibrate_floor --write` answers box 5, **and it is the first time in
this project that it can succeed** — the scope rule made the floor writable
from three homogeneous 33-case dates with one denominator, and day 3 supplies
the third.

**If it still refuses, read the refusal block and write down the reason. That
is a valid answer to box 5 and it must not be worked around.**

## The dates

```
day 1   Wednesday 2026-08-26  DONE — two sessions, 198 runs
day 2   Thursday  2026-08-27  DONE — one session, 99 runs
day 3   Friday    2026-08-28
```

Amended twice, at 10:00 on 2026-08-26 and at the close of day 1. `BLOCK_E_DAY2_START`
records why that should have been the last amendment, and it was.

Each session must sit wholly inside its own UTC date. You are UTC+1: start
after 01:00 BST, finish before 01:00 BST the next morning.

## Traps

Everything in `BLOCK_D_START.md`, `D4_START.md`, `BLOCK_E_START.md`,
`BLOCK_E_RUNBOOK.md` and `BLOCK_E_DAY2_START.md` still applies. The four added
on 2026-08-26 are worth re-reading in particular: separate the dry run from the
sweep, give every run its own capture filename, count archives rather than
console output, and do not run `git` through the Cowork bridge without
`--no-optional-locks`.

Two notes from day 2, neither a trap so much as a thing that will look wrong:

- **`commit-*.txt` is gitignored** (`.gitignore:37`), by construction — the
  message file is consumed by the commit it describes. Day 2's commit therefore
  reported **102** files, not 103, and that is correct.
- **The sweep prints "99 distinct serving stacks".** It is owed correction 3.
  Ignore it. It is not a provider changing under the run.

## Watching the run — a second window, changing nothing

Paste this into a third window (leave litellm alone in the second) **before**
starting the sweep. It writes no file, touches nothing in the tree, and there
is nothing to commit.

```powershell
$repo   = "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
$target = 99
$date   = (Get-Date).ToUniversalTime().ToString("yyyyMMdd")
$start  = Get-Date

while ($true) {
  $n  = @(Get-ChildItem "$repo\eval\answer_runs\$date*.json" -EA SilentlyContinue).Count
  $el = (Get-Date) - $start
  $eta = if ($n -gt 0 -and $n -lt $target) {
           [TimeSpan]::FromSeconds(($el.TotalSeconds / $n) * ($target - $n)).ToString("mm\:ss")
         } else { "--:--" }
  $bar = ("#" * [math]::Floor($n * 40 / $target)).PadRight(40, ".")
  Write-Host ("`r[{0}] {1,3}/{2}  elapsed {3}  eta {4}   " -f `
              $bar, $n, $target, $el.ToString("mm\:ss"), $eta) -NoNewline
  if ($n -gt $target) {
    Write-Host "`n!! $n ARCHIVES — ABOVE $target. A SECOND SWEEP IS RUNNING. STOP." -Foreground Red
    break
  }
  if ($n -eq $target) {
    Write-Host "`n$target runs. Waiting for the sweep archive…"
    while (-not (Get-ChildItem "$repo\eval\sweeps\$($date)T*.json" -EA SilentlyContinue)) {
      Start-Sleep -Seconds 3
    }
    Write-Host "Sweep archive written. Done." -Foreground Green
    break
  }
  Start-Sleep -Seconds 5
}
```

A count **above** 99 means a second sweep, not a retry. That is what cost day 1
its first capture.

## What is NOT a finding

`aksum-exports` failing. Tracked, out of `required_cases`, not closed by Block E.

`vimose-runes` failing. Demoted on two dates of evidence, now failing on four.
Reported beside the floor verdict for ever and never subtracted from it.

`weilue-chinese-quotation` passing. Its entry survives to the end of the block
because of the freeze, not because anyone believes it.

## The sentence that travels

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT
was reachable. `muziris-cargo-akananuru` still sits at rank 310.

The clause that rode with those two since Part 7 — *"and the answer path has
still never quoted a non-English source text"* — was retired on 2026-08-26 by a
case that had never been run. Do not carry it forward.
