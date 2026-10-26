# Block E — starting point for the next thread

*Written 2026-08-25 at the close of Block D. Supersedes `D4_START.md`, whose
TASK 3 is done. Every number here was read off the host or out of an archive.*

## Read these, in this order

| # | file | why |
| :---- | :---- | :---- |
| 1 | **this file** | state, and the four decisions to make BEFORE spending a call |
| 2 | `D4_RESULT.md` | what the two-day pilot measured, and FINDING 18 |
| 3 | `FINDINGS_14_TO_18.md` | five findings; three were found by RUNNING an instrument |
| 4 | `RULINGS.md` | index of rulings 1–35. **Read 35 before quoting a stability number** |
| 5 | `PHASE2_PLAN.md` lines 472–503 | Block E and gate G4, written before any of it was measured |
| 6 | `eval/gold/floor.json` | read it whole. `calibrated: false` is still true |
| 7 | `D4_PILOT_RUNBOOK.md` | the shape of a multi-day sweep, with its two defects now corrected in place |
| 8 | `PROGRESS.md` **last section only** | ~594 KB. Do not read it whole |

## State, as measured 2026-08-25

```
tree            ac96556, clean
                ac96556  D4 day 2: the pilot crossed a date boundary, and FINDING 18
                483be65  FINDING 14: the sweep never recorded the corpus it was made against
                fbabb93  FINDING 16: CPython's bytecode cache validated a mutation away
                dce1ad1  FINDING 15: a mutation harness resolved an ambiguous target
                5c238c4  D4-B/C: a duplicate question cannot shadow a case, and the
                         sweep learns what a session is
                424fef1  D4-A / FINDING 12: a gold pair that stops resolving kills the run

corpus          24 records / 450 embedded / 0 pending
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                unchanged since 2026-08-22, asserted at BOTH ends of every D4 sweep

ANSWER          eval.test_answer_eval       248   GREEN
mutations       scripts/mutate_part8.py      48   GREEN
RANKING         eval.test_ranking_check     226   GREEN
mutations       scripts/mutate_ranking.py    95   GREEN

gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
sweeps          5 archived. THREE carry no session identity and never will.
                TWO do: 2026-08-24 and 2026-08-25.
distinct dates  2. The floor requires 3.
floor           calibrated: false. NOT MET on both D4 days, on vimose-runes alone
```

## What Block E is

`PHASE2_PLAN.md`: **30 cases × 3 repetitions ≈ 90 chat calls per day, three
separate calendar days, ~270 calls.** Runs in the window after G2 and before
Block F touches the corpus — retrieval frozen, corpus frozen, corpus hash
recorded. That window is open now and closes the moment the sourcebook grows.

Gate G4:

```
[ ] >=30 cases meeting the stratification, each with an explicit expected behaviour
[ ] run 3x on >=3 separate days
[ ] per-case stability and per-session stability reported as separate numbers
[ ] a stated VARIANCE DECOMPOSITION — how much is session, how much is case —
    with the data archived
[ ] the floor recalibrated from cross-session data and calibrated: true,
    OR the reason it cannot be written down
```

**The deliverable is the variance decomposition, not the pass rate.** If G4
fails, Phase 2 cannot be steered and every later improvement is unfalsifiable —
kill trigger 2.

## What D4 built that Block E now depends on

```
session block      id, date, date_basis, started_at, finished_at, label,
                   crossed_midnight_utc — in the sweep archive AND in every
                   per-run archive under eval/answer_runs/
corpus_version     read before the first chat call
corpus_version_after   read again after the last, and compared. Exits 2 if moved
two numbers        per-case and per-session, each with its own denominator
calibration        REFUSES to write calibrated: true under 3 distinct dates, and
                   a sweep with no session identity blocks it permanently
pair-count guard   a gold pair that stops resolving kills the run (ruling 32)
duplicate question a second case asking the same question is refused at load
```

All of it exercised on two live runs across a real date boundary. **The
instrument is not the risk in Block E. The four decisions below are.**

---

## FOUR DECISIONS, and all of them must be made BEFORE day 1

Because the rule between days is *change nothing*, anything unsettled on day 1
stays unsettled for all three days or costs the whole sweep.

### 1. `vimose-runes` — demote it, or fix the margin

It is in `floor.json.required_cases` and it has now failed **0/3 in two
consecutive sessions on two dates**. `floor.json`'s own note defends its
retention on the ground that *"the failure is not a regression in the
pipeline"* and that removing it would be *"how a floor is quietly lowered to
whatever is currently passing."* That note was written when the failure looked
like one bad session. It no longer does.

The dry run points at retrieval rather than generation:

```
vimose-runes   [S1] arabia-04-jabal-dabub    sim 0.433   unrelated
               [S2] arabia-03-jsnab17        sim 0.401   unrelated
               [S3] scandinavia-03-vimose    sim 0.384   ALL SEVEN gold terms
```

Its own gold record is third, behind two Arabian inscriptions, in a spread of
0.049. No other case in the pilot has a margin like it.

**If it stays required and keeps failing, `calibrated: true` cannot be written
on day 3 even with three dates**, and G4's last box is answered with a reason
rather than a number. That may be the honest outcome. It is not an outcome to
discover on day 3. Decide now, write the reason down, and if it is demoted say
in `floor.json` that it was demoted on evidence from two dates and what would
put it back.

### 2. The variance decomposition does not exist yet

G4's deliverable is *"how much is session, how much is case"*. D4 built two
stability **rates**. It did not build a decomposition, and nothing in the
harness computes one.

Build it and mutation-verify it **before** spending 270 calls, on the D4
archives, which are exactly two sessions of six cases and will exercise every
edge — including the one FINDING 18 found, where both rates read 100% and the
answers all changed.

**And decide what it is computed over.** FINDING 18 is the argument for two
decompositions rather than one: verdicts are stable across sessions and texts
are not, so a decomposition over verdicts alone will report near-zero session
variance for a system whose output changed completely. `distinct_texts` and the
answer hashes are already in every archive.

### 3. Record a serving-stack identifier

The archive records `model` (`anthropic/claude-haiku-4-5-20251001`) and nothing
else. Nothing in it can distinguish provider-side drift from sampling variance —
which is precisely the question FINDING 18 raises and cannot answer. If the
gateway returns a `system_fingerprint` or any equivalent, record it beside
`model`. One line, and it is worth far more before the 270 calls than after.

### 4. Do the two D4 pilot sweeps count toward calibration?

`calibrate_floor` currently reads **every** archived sweep. After Block E day 1
there will be three distinct dates — but two of them are six-case pilot sweeps
and one is a thirty-case sweep. **A floor calibrated across heterogeneous case
sets is a floor whose denominator changes between dates.**

This is not hypothetical: it decides whether the floor becomes writable on
Block E day 1 or day 3. Either is defensible. Neither is defensible discovered
by accident. Decide, and if the pilot sweeps are excluded, exclude them by a
recorded rule rather than by moving files.

---

## Booking the days

`PHASE2_PLAN.md` item 4: *"Book three separate calendar days for the W4 sweep,
in advance. The **days** are the scarce resource, not the calls. Three runs in
one week is fine; three runs in one day is one observation."*

D4 confirms it. Two dates cost two days of wall-clock and about four minutes of
compute. **Book the three dates before day 1 and put them in the result
document.** Midday-to-midday is not required — D4's gap was 31 hours, midday to
evening — but each session must sit wholly inside its own UTC date, or
`crossed_midnight_utc` records that it did not.

## Session ritual

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1

# Both, always. And see the FIVE boundaries in D4_PILOT_RUNBOOK.md.
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
docker compose up -d db
litellm --config gateway/config.yaml --port 4000     # separate window

git status                              # MUST be clean
python -m ingest.run_embed --stats      # 450 / 450 / 0
python -m eval.test_answer_eval         # 248
python -m eval.test_ranking_check       # 226
python scripts\mutate_part8.py          #  48
python scripts\mutate_ranking.py        #  95
```

Then per day, exactly as D4 rehearsed it:

```powershell
python -m eval.run_answer_sweep --dry-run          # embeddings only, no chat call
python -m eval.run_answer_sweep --repeat 3 --session-label "Block E day N" `
  *> eval\block-e-dayN.txt
```

The corpus line must read `26e4a683014bdf8a…` on all three days. If it does not,
the sweep says so and exits 2 — that is the finding, and it stops the block.

## Traps carried forward

Everything in `BLOCK_D_START.md` and `D4_START.md` still applies. Five to add,
all learned on 2026-08-24 and 2026-08-25:

- **`*>` makes the console look dead.** It redirects every stream, so a
  seven-minute sweep prints nothing at all. Watch progress from a SECOND window
  with `(Get-ChildItem eval\answer_runs\<date>*.json).Count`. Do not Ctrl-C: a
  half-finished sweep leaves orphan per-run archives and no sweep archive tying
  them together.
- **`git log` opens a pager and waits.** Press `q`. Use `git --no-pager`.
- **A capture's `.Length` is CHARACTERS, its size on disk is BYTES, and the
  captures are UTF-16.** `D4_DAY1_STATE.md` records *"~8700 on day 1"*, which is
  the byte count; `(Get-Content -Raw).Length` reads 4370. Both pilot captures are
  8742 bytes **and they are different files** — verified, 15 differing lines. A
  fixed-width report makes equal lengths ordinary, so length is a smoke test and
  never an identity check.
- **Three vacuous non-Latin proofs in four days.** Do not attempt a fourth on the
  answer path. See FINDING 18's corollary: there is nothing non-Latin to print.
- **`calibrate_floor`'s last line contradicts its own refusal.** It ends with
  `re-run with --write to set calibrated: true` even when it has just refused.
  Open defect. Read the refusal block, not the last line.

## What is NOT a finding

`aksum-exports` and `weilue-chinese-quotation` failing. Both are tracked in
`floor.json.known_failing_cases` as **open defects**, both are out of
`required_cases`, and neither is closed by Block E. They are reported beside the
floor verdict and never subtracted from it. **A sweep that reports them passing
is a finding, not a success.**

## The sentence that still travels with all of it

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310, and the answer path
has still never quoted a non-English source text.

Block E measures none of those. It measures whether the answers this system
gives can be improved on purpose — and it is the first block in this project
that will be able to say which of the session and the case is moving, because
D4 built the instrument that can tell them apart.
