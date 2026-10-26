# D4 RESULT — the harness can tell a session from a repetition

*Written 2026-08-25, at the close of the two-day pilot. This closes Block D.
Every number here was read out of the archives, not out of a report.*

## What D4 was for

`floor.json` records `calibration_invalidated: "2026-08-10, hours after being
set."` The floor had been calibrated on CONTENT being stable in 10 of 10 cells
across three repetitions each. A second sweep, against a `vimose-runes` evidence
block byte-identical across all six archived runs, produced 3/3 with seven
resolved quotations in the first session and 0/3 with none in the second — same
prompt version, same model, same evidence, temperature 0.

All three sweeps archived before D4 are within-session, and none of them carries
a date. **Block E's 270 calls are worth nothing if the archives cannot tell a
session from a repetition.** D4 is the block that made them able to.

## TASK 3, item by item

```
1  session identity in every sweep archive        DONE, on two live runs
2  calibration refuses under 3 distinct dates      DONE, mutation-verified, and
                                                   REFUSED FOR REAL on 2026-08-25
3  per-case and per-session as two numbers         DONE, both printed with their
                                                   own denominators
4  pilot on 5 cases across 2 days                  DONE. 6 cases, 36 chat calls
```

## The two sessions

```
                day 1                          day 2
session         792202e7ac58                   8ee2273defd6
date            2026-08-24 (UTC)               2026-08-25 (UTC)
window          12:21:08 - 12:23:10            19:14:21 - 19:21:21
label           D4 pilot day 1                 D4 pilot day 2
crossed midnight  false                        false
corpus          26e4a683014bdf8a...            26e4a683014bdf8a...
corpus_after    26e4a683014bdf8a...            26e4a683014bdf8a...
corpus_moved    null                           null
model           anthropic/claude-haiku-4-5-20251001, both days
prompt          p7-answer-v2r, both days
```

The gap is 31 hours, not 24. That is deliberate: midday to evening on
consecutive dates is a stronger observation than a few hours either side of
midnight UTC, and it keeps `crossed_midnight_utc` false on both runs so neither
session's date is contestable.

## The result — every verdict agreed

```
case                 24th   25th   behaviour
adulis-exports       3/3    3/3    answerable
aksum-exports        0/3    0/3    answerable, KNOWN-FAILING, still failing
antikythera-absent   3/3    3/3    correctly_refusable
chinese-da-qin       3/3    3/3    answerable
muziris-cargo        3/3    3/3    answerable
vimose-runes         0/3    0/3    refusable_with_gloss, REQUIRED, below floor

content 67%   grounded 83%   refusal 50%   unstable cells 0    BOTH DAYS
mean resolved quotes   2.22 (24th)   2.33 (25th)
```

```
per-case      12/12 = 100%    the sampler, within one session
per-session    6/6  = 100%    the day, across sessions
60 rows carry no session identity and are counted in NEITHER number
```

**Both numbers are 100% and that is a real result, not a null one.** It says the
verdicts this instrument produces are reproducible across a date boundary. It is
the first time this project has been able to say that about anything.

## And not one answer text agreed

Every answer in both sweeps, hashed:

```
case                 day 1 texts    day 2 texts    shared between the days
adulis-exports       2 distinct     1             NONE
aksum-exports        1             1              NONE
antikythera-absent   1             3 distinct     NONE
chinese-da-qin       3 distinct     1             NONE
muziris-cargo        1             1              BYTE-IDENTICAL, all six runs
vimose-runes         1             1              NONE
```

Five of six cases share not a single answer text between the two days, at
temperature 0, against a corpus whose digest is identical at all four
measurement points, on a pinned dated model snapshot.

Three things follow, and the third is the one that matters.

**Within-session determinism is not a property of the case.**
`chinese-da-qin` produced three distinct texts on day 1 and one text three times
on day 2. `antikythera-absent` did the exact reverse. Whatever produces
byte-identical repetitions is not stable across days either.

**It is not a blanket claim about the model.** `muziris-cargo` returned the same
answer, byte for byte, in all six runs across both days. Text-level
reproducibility across a date boundary is achievable on this stack. Five cases
did not achieve it.

**`vimose-runes` was internally deterministic on both days and deterministic
about a DIFFERENT answer on each.** One text three times on the 24th; another
text three times on the 25th. That is the 2026-08-10 phenomenon, reproduced
deliberately — the session-level substrate does move between days. It simply did
not cross a verdict boundary this time, for these six cases.

The two `vimose-runes` texts differ in a way the scorer can see:

```
24th   "...the English translation provided states only that 'Several
        inscriptions remain only partially deciphered' and offers only
        tentative interpretations..."            1 resolved quotation
25th   "...the English translation provided consists only of partial and
        uncertain interpretations rather than complete readings..."
                                                 0 resolved quotations
```

Same verdict, same failure list but for one entry, and one fewer quotation
resolved to characters on disk. A gate that watched quotations rather than
content would have called these two days a regression.

## What per-session stability measures — read this before quoting the number

`per-session 6/6 = 100%` is a statement about **verdicts**. It is not a
statement about behaviour, and the table above is the proof: the number reads
100% in a sweep where five of six cases changed their answer completely.

This is not a defect in the instrument. It is the correct scope for a gate — a
gate that failed on any text change would fail every day and measure nothing.
But it means the sentence *"the system does the same thing on two days"* is NOT
supported by a per-session pass, and D4 declines to let that reading stand.
Ruling 35.

## The floor — refused, and right about why

```
5 archived sweep(s), 96 run(s)

distinct dates     2 (floor requires 3): 2026-08-24, 2026-08-25
distinct sessions  2

REFUSED. `calibrated: true` may NOT be written:
  - 2 distinct date(s), and the floor requires 3.
  - 3 sweep(s) carry no session identity and count toward no date.
```

The three pre-D4 sweeps blocking calibration is **correct behaviour and not a
nuisance.** A date assigned to them after the fact is precisely the calibration
`floor.json` already records as invalid. They cannot be rescued and should not
be.

Neither sweep met the floor, both days, on one problem and the same one:

```
vimose-runes: 0/3 — a required case must pass every repetition
```

## `vimose-runes` — the recommendation is to demote it, not to defend it

`D4_DAY1_STATE.md` set out two outcomes for day 2 and both were worth having.
The one that arrived was the second: two sessions agreeing at 0/3. That points
at a standing defect rather than session variance.

The case is `refusable_with_gloss` and sits in `floor.json.required_cases`. It
has now failed 0/3 in both D4 sessions, and the failure is the same one each
time — the answer opens with the refusal sentence and then glosses, where the
case demands the gloss content (`harja`, `mariha`/`makija`, `awgns`) and three
resolved quotations, and forbids the refusal sentence.

The dry run shows the likely mechanism, and it is retrieval-shaped rather than
generation-shaped: **the Vimose record is at rank 3**, at similarity 0.384,
behind two Arabian inscriptions at 0.433 and 0.401 that have nothing to do with
the question. Three near-tied similarities with the gold content third is a far
thinner margin than any other case in this set.

**This is not closed by D4 and must not be closed by Block E in passing.** The
recommendation carried forward: either the case comes out of `required_cases`
with the reason recorded, or the retrieval margin is fixed and it stays. What is
not acceptable is a Block E floor that is met because the case was quietly
dropped.

## A defect in `calibrate_floor`'s own report

The refusal block says `calibrated: true` may NOT be written. The last line of
the same output says:

```
nothing written — re-run with --write to set calibrated: true
```

Those two sentences contradict each other, and a reader who skims to the last
line is invited to do the thing the report just refused. The trailing line is
printed unconditionally. On a refused run it should say that `--write` would
refuse too. **Filed as an open defect, not fixed here** — the tree is frozen
between the pilot and its commit, and this is a message, not a gate.

## The encoding fix cannot be proven on the answer path, and that is the
## standing defect stating itself

`D4_PILOT_RUNBOOK.md`'s non-Latin check was vacuous — the sweep prints PASS/FAIL
lines and summary tables and never prints an answer. That was recorded on the
24th, along with a replacement: `eval.answer_eval --archives -v`, described as
*"the real proof... on a harness that emits non-Latin text"*.

**The replacement is vacuous too.** Run on 2026-08-25: 140,312 bytes, 70,155
characters, UTF-16LE with a BOM, zero replacement characters, no traceback,
`76/115 archived answers meet their case` — and **zero characters above U+024F**
except em-dashes and ellipses.

Three attempts, three vacuous proofs, the third written by someone who had just
finished writing down why the second was wrong. The reason is not a bad choice
of flag:

> **There is no non-Latin output because the system has never produced any.**
> 45 of 45 resolved spans came from the English while the Chinese chunk sat at
> `[S1]`. The failure detail prints `quoted: nothing`.

FINDING 10's guard is in all 44 entry points and is mutation-verified. It is
**unproven for the answer path and unprovable there** until the prompt asks for
a source text. A proof has to come from a harness that handles source text by
construction — `scripts/weilue_compare.py` compares the Weilüe record's
Classical Chinese against the Sanguozhi text and is the obvious candidate.

Written down as FINDING 18's corollary so that no fourth attempt is made on the
path that has nothing to print.

## What Block E inherits

```
corpus digest       26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
sweeps archived     5, of which 2 carry session identity
distinct dates      2. Block E's first sweep is the third, and the floor
                    becomes calibratable on that day and not before
per-case            12/12 = 100%
per-session          6/6  = 100%, on VERDICTS. See ruling 35
floor               NOT MET both days, on vimose-runes alone
known-failing       aksum-exports 0/3 observed; weilue-chinese-quotation not run
```

**One addition Block E should make before it spends 270 calls.** The archive
records `model` but no `system_fingerprint` or serving-stack identifier. Nothing
in it can distinguish provider-side drift from sampling variance, and the text
table above is exactly the observation that needs the distinction. If the
gateway returns any such field, record it beside `model`. It costs one line.

## The sentence that still travels with all of it

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310, and the answer path
has still never quoted a non-English source text.

D4 measured none of those. It measured whether this harness can tell a session
from a repetition. It can, it did, and the first thing it saw was that the
verdicts hold while the words underneath them do not.
