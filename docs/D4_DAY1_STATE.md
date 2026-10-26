# D4 — state at the close of pilot day 1

*Written 2026-08-24. Committed 2026-08-25, because day 2's precondition was a
clean tree. This is the single undivided copy of three documents that were
written into the project store during day 1, which rejects a document above
about five kilobytes: `claude/d4-day1-state.md`, `claude/d4-finding-17.md` and
`claude/d4-day1-runbook-defects-and-day2.md`.*

**Superseded on the outcome by `D4_RESULT.md`.** Kept because it is the record
of what was known and predicted BEFORE day 2 ran, and because the two outcomes
it sets out for `vimose-runes` are the reason day 2's result can be read at all.
FINDING 17 is now in `FINDINGS_14_TO_18.md`; the runbook defects are corrected
in `D4_PILOT_RUNBOOK.md` itself.

## State, as measured 2026-08-24

```
tree            483be65, clean
                483be65  FINDING 14: the sweep never recorded the corpus it was made against
                fbabb93  FINDING 16: CPython's bytecode cache validated a mutation away
                dce1ad1  FINDING 15: a mutation harness resolved an ambiguous target
                5c238c4  D4-B/C: a duplicate question cannot shadow a case, and the
                         sweep learns what a session is
                424fef1  D4-A / FINDING 12: a gold pair that stops resolving kills the run
                bdc79ba  Block D TASK 3: the handoff document this thread opened from

corpus          24 records / 450 embedded / 0 pending
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                unchanged since 2026-08-22, and now asserted at BOTH ends of a sweep

ANSWER          eval.test_answer_eval       248   GREEN   (was 203)
mutations       scripts/mutate_part8.py      48   GREEN   (was 27)
RANKING         eval.test_ranking_check     226   GREEN   (was 218)
mutations       scripts/mutate_ranking.py    95   GREEN   (was 91)

sweeps          4 archived. THREE carry no session identity and never will.
                One does.
```

## TASK 3, item by item, as of day 1

```
1  session identity in every sweep archive          DONE, demonstrated on a live run
2  calibration refuses under 3 distinct dates        DONE, mutation-verified
3  per-case and per-session as two numbers           DONE, both printed
4  pilot on 5 cases across 2 days                    DAY 1 DONE. Day 2 outstanding.
```

Item 4 was the whole of what remained, and it could not be brought forward: it
needed a second UTC date.

## Day 1, measured

Six cases, three repetitions, `p7-answer-v2r`, 18 chat calls, session
`792202e7ac58`, 12:21:08 to 12:23:10 UTC.

```
case                 content  grounded  quotes  texts
adulis-exports         3/3      3/3      3-4      2
aksum-exports          0/3      3/3      0        1
antikythera-absent     3/3      3/3      0        1
chinese-da-qin         3/3      3/3      3-8      3
muziris-cargo          3/3      3/3      4        1
vimose-runes           0/3      0/3      1        1

content pass 67%   grounded 83%   refusal 50%   unstable cells 0
per-case      6/6 = 100%
per-session   NOT MEASURED — no case was seen in two sessions
floor         BELOW THE FLOOR: vimose-runes 0/3, a required case
```

**`vimose-runes` at 0/3 is the result day 2 turns into a number.** Two outcomes
were set out, and both were worth having:

- **3/3** — per-session stability 0% on a required case. The 2026-08-10
  phenomenon reproduced deliberately, on an instrument that can name which of
  the two numbers moved.
- **0/3 again** — two sessions agreeing. That points at a regression rather than
  session variance, and `vimose-runes`' place in `required_cases` needs
  re-examining rather than defending.

**Day 2 returned the second.** See `D4_RESULT.md`.

`per-case 6/6 = 100%` sits beside a floor failure and is not a contradiction:
every cell was internally unanimous, so the sampler is steady and something else
is not. That split is the entire argument for reporting two numbers.

## What day 1 proved about the instruments

The archive states it rather than a reader reconstructing it:

```
session               id, date, date_basis, started_at, finished_at, label,
                      crossed_midnight_utc     all present
corpus_version        26e4a683…  at the start
corpus_version_after  26e4a683…  after the last chat call
corpus_moved          null
every results row     carries session_id and session_date
```

FINDING 14's second read is not decoration: it is the difference between *"the
corpus this sweep BEGAN against"* and *"the corpus did not move under this
sweep"*, and only the second is the sentence Block E needs.

## What day 1 said to change between the days: NOTHING

Not a prompt, not the corpus, not retrieval, not the gateway, not
`gateway/config.yaml`, not `scripts/schema-part7.sql`, and not
`D4_PILOT_RUNBOOK.md` — it was committed, and day 2's precondition was a clean
tree. Honoured: `git status` on 2026-08-25 showed no tracked file modified, only
day 1's own untracked outputs.
