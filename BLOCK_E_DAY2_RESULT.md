# Block E day 2 — result

*2026-08-27. One session, 99 chat calls, the first PLANNED second date.
Nothing in the tree moved between day 1 and this run: the freeze held.*

## What ran

```
D2  6715f2a3ab6b44d4  10:20:44-10:30:48 UTC  "Block E day 2"  99 runs

    33 cases x 3 repetitions, p7-answer-v2r, temperature 0
    corpus 26e4a683014bdf8a at BOTH ends, corpus_moved None, 24 records
    0 unstable content cells, 0 incomplete, 0 retried
    crossed_midnight_utc false
    FLOOR MET

    content 73%   grounded 79%   refusal 36%   mean resolved quotes 1.61
```

Day 1 S1 began at 10:20:15 and this began at 10:20:44. **The date crossing is
24 hours and 29 seconds.** That was not arranged; the morning slot was chosen
to match day 1's time of day and the clock did the rest. It means the
across-day comparison below is as close to a pure date crossing as this design
can produce — the same hour, the same weekday-morning conditions, one calendar
day apart.

## FINDING 23 — there is no date effect. The boundary is the session, and nothing is added by crossing a date.

This is what day 2 was booked to decide, and it decides it against the
hypothesis that motivated the booking.

Three session pairs now exist over the same 33 cases. One is within a date and
two cross one. Each is scored against the within-session agreement of the two
sessions it actually compares, so no pair borrows a baseline from a session it
does not contain:

```
pair            separation              within      across        lost
S1 vs S2        same date, 88 min     169/198 85%  222/297 75%   +10.6 pts
S1 vs D2        ACROSS DATE, 24h00m   163/198 82%  221/297 74%   + 7.9 pts
S2 vs D2        ACROSS DATE, 22h32m   174/198 88%  228/297 77%   +11.1 pts
```

**The two across-date losses bracket the within-date loss.** One is smaller,
one is larger, and the within-date figure sits between them. `S2 vs D2` crosses
a date boundary twenty-two hours wide and agrees BETTER (77%) than `S1 vs S2`
did ninety minutes apart on one morning (75%).

The 27 cases D4 never ran say it without any noise at all:

```
the 27 cases       same date, 88 min    +6.8 pts
                   ACROSS DATE, 24h     +6.0 pts
                   ACROSS DATE, 22.5h   +6.2 pts
```

Three measurements, two of them crossing a date, spread over 0.8 of a point.

`BLOCK_E_DAY2_START` set the decision rule in advance: *"if the across-day loss
on 33 cases lands near +11%, the date boundary is not the thing and D4's +61%
was its case sample."* It landed at +7.9 and +11.1 against a within-day +10.6.
**The date boundary is not the thing.**

`eval.decompose`, pooling all three sessions as it is written to, prints the
same conclusion as one number:

```
ANSWER TEXT, 33 cases, 3 sessions, 297 runs, TWO DATES
  within a session   253/297   = 85%
  across sessions    671/891   = 75%
  different case     0/42768   = 0%
  agreement lost at the session boundary: +10 pts
```

Day 1's within-date figure was +11 pts on this same case set. Adding a second
date moved it to +10. **A date is worth about minus one point**, which is to
say: nothing.

### What that does to FINDING 19

FINDING 19 was written yesterday off exactly one across-date comparison — D4's
six cases, 31 hours, +61 pts — set against the same six cases within one day at
+28 pts, and concluded *"crossing a date roughly doubles the loss."*

That conclusion does not survive today. The same six cases, now across a real
date boundary at the full three-session grid:

```
the 6 D4 cases     same date, 88 min    +27.8 pts
                   ACROSS DATE, 24h     +16.7 pts
                   ACROSS DATE, 22.5h   +33.3 pts
```

Crossing a date gives +16.7 and +33.3 against a same-date +27.8. **Not a
doubling. Not a direction.** And D4's +61 pts is not reproduced by either
across-date pair even on D4's own case set — it is above both.

So D4's +61 was two things stacked, and yesterday only caught one of them:

1. **a case sample four times more text-unstable than the rest of the set** —
   which FINDING 19 got right, and which today confirms on a third session
   (the six lose 17-33 pts where the twenty-seven lose 6);
2. **fifty-four pairs.** At that denominator a swing from +17 to +61 is a
   handful of cells. FINDING 19 read a difference between two small samples as
   a difference between two conditions.

FINDING 19's second half stands and is strengthened. **Its first half — the
date effect — is withdrawn by the measurement it asked for.** That is the
correct outcome for a claim built on one comparison, and it is why day 2 was
worth 99 calls whichever way it fell.

## FINDING 24 — the verdict layer is invariant across a date as well as across a session

```
VERDICTS (content_ok), 33 cases x 3 sessions x 3 repetitions = 297, balanced
  mean 0.727
  case             100.0%   var +0.20455
  session            0.0%   var +0.00000
  case_x_session     0.0%   var +0.00000
  residual           0.0%   var +0.00000
```

Not one verdict moved. All 33 cases returned the identical result in all three
sessions — the same 24 passes, the same 9 failures — and `content_pass_rate`
reads 0.727272… in each of the three to every digit printed.

Yesterday this table was four ways of measuring one date. It could not tell
whether "session 0%" meant sessions do not matter or merely that both sessions
shared a morning. **Today it spans two dates and says the same thing**, so the
reading is now: whether a case passes is a property of the case, and neither
the session, nor the day, nor the draw moves it.

Read it against FINDING 23 and the pair is still the deliverable, exactly as
ruling 35 requires. The verdicts are perfectly stable across a date. A quarter
of cross-session answer pairs are still different strings across that same
date. Both are true; neither may be quoted without the other.

## The three things day 2 was told to watch

- **`weilue-chinese-quotation`: 3/3 again, on a second date, 1 distinct text.**
  Three sessions, nine runs, nine passes, byte-identical throughout. Its
  `floor.json` defect entry — inferred from 16 runs of a sibling case that is
  not this one — is now falsified on two dates. It stays in the file until
  day 3 is archived, because of the freeze and for no other reason.
- **Non-Latin characters survived the capture again.** 42,316 bytes through a
  `*>` redirect on PowerShell 5.1, no `UnicodeEncodeError`. FINDING 10's guard
  has now been exercised on the answer path on two separate dates. Nothing was
  built to prove it, on either.
- **`vimose-runes`: 0/3, 2 distinct texts** (3 in S1, 2 in S2, 2 today).
  Stable verdict, moving text, now across a date as well as within a day.

## One new observation, written down and not acted on

`unstable_grounded_cells` read **1** in both day-1 sessions and **0** today.
Groundedness only — `unstable_content_cells` is 0 in all three, so no floor
verdict is affected and no decomposition input changes. Recorded here so that
day 3 has something to compare against rather than discovering it as a
surprise.

Both known metadata defects reproduced exactly as predicted: the sweep archived
**99 distinct serving stacks** (the per-call `id` is in the identity) and
`serving_stack.model` reads the alias `chat-default` on all 99 rows. Both lines
are meaningless and both were ignored.

## THE FREEZE — now FIVE corrections are owed, and none may be made before day 3

The four from `BLOCK_E_DAY1_RESULT.md` are unchanged and untouched. A fifth is
added today, and like the others it is written down rather than fixed.

```
1  floor.json   weilue-chinese-quotation's defect entry is FALSIFIED
2  floor.json   demotions.vimose-runes diagnosis and reinstated_when are wrong
3  code         _serving_stack includes the per-call `id`
4  code         serving_stack.model reads the alias in the sweep path
5  code         run_answer_sweep has no --progress and never flushes, so a
                10-minute 99-call sweep shows the operator nothing at all until
                it exits. `*>` redirects every stream and Python buffers stdout
                when it is not a terminal, so the console is dead either way.
                Fix: --progress writing one line per completed cell to stderr
                with flush=True, so `*>` still captures everything while a
                plain run is watchable.
```

**5 must not be applied before day 3.** Days 1 and 2 both ran through `*>` on
PowerShell 5.1, and that redirect is itself under observation — it is how
FINDING 10's guard is being exercised on the answer path. Changing the
invocation for day 3 would make day 3's capture the only one produced a
different way, on the one day whose whole purpose is to replicate the other
two. Day 3 is watched from a second window by counting archives, which is what
the trap in `BLOCK_E_DAY2_START` asks for and which touches nothing.

## Gate G4, after day 2

```
[x] >=30 cases, each with an explicit expected behaviour     33
[ ] run 3x on >=3 separate days                              2 of 3 dates
[x] per-case and per-session stability as separate numbers   99/99, 33/33
[x] a stated VARIANCE DECOMPOSITION                          computed, 297 runs
[ ] the floor recalibrated, OR the reason it cannot be       REFUSED, 2 dates
```

`calibrate_floor` refuses on the one remaining ground and names it:

```
distinct dates     2 (floor requires 3): 2026-08-26, 2026-08-27
distinct sessions  3        2026-08-26: 2 session(s)   2026-08-27: 1
eligible sweeps    3        five excluded by rule, each with its reason
REFUSED. `calibrated: true` may NOT be written.
```

One date outstanding. Nothing else.

## A prediction for day 3, committed before it runs

Recorded here for the reason `BLOCK_E_DAY1_DRYRUN` gives: a prediction made
before the run is evidence, and the same observation made afterwards is a
story.

```
2026-08-27 vs 2026-08-28   ~24h, the REPLICATION   predicted +6 to +12 pts
2026-08-26 vs 2026-08-28   ~48h, derived for free  predicted +6 to +12 pts
the 27 cases, either pair                          predicted +5 to +8 pts
the verdict decomposition, 33 x 4 x 3 = 396 runs   predicted case 100%
```

**FINDING 23 is wrong if either across-date figure exceeds about +20 pts, or
if the 48-hour pair loses materially more than the 24-hour pairs.** The second
is the one worth watching: it is the only thing in this design that could speak
to separation growing with distance, and `BLOCK_E_DAY2_START` already recorded
that this block cannot properly answer that question. A 48-hour pair inside the
same band would make FINDING 23 harder to dislodge without settling it.

## What is NOT a finding

`aksum-exports` failing. Tracked, out of `required_cases`, not closed by
Block E.

`vimose-runes` failing. Demoted on two dates, now failing on a third.
Reported beside the floor verdict for ever and never subtracted from it.

`weilue-chinese-quotation` passing. Its entry survives to day 3 because of the
freeze, not because anyone believes it.

## The sentence that travels

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT
was reachable. `muziris-cargo-akananuru` still sits at rank 310.

The clause that rode with those two since Part 7 was retired on 2026-08-26.
Do not carry it forward.

---

## CORRECTION, added 2026-08-28. The original text above is unaltered.

**The claim in "The three things day 2 was told to watch" that non-Latin
characters survived day 2's capture is wrong on both halves.** It reads:
*"Non-Latin characters survived the capture again. 42,316 bytes through a `*>`
redirect on PowerShell 5.1, no `UnicodeEncodeError`."*

```
capture         bytes    non-ASCII   beyond ASCII punctuation
day 1           42140      41   — x40, … x1                 0
day 2           42316     120   Γ x40  Ç x40  ö x39  ª x1
day 3           42156      40   — x39, … x1                 0
```

`ΓÇö` is UTF-8 `E2 80 94` read back as CP850 — a mangled em-dash — and `ΓÇª` is
a mangled ellipsis. **Day 2's capture is mojibake.** Days 1 and 3 hold the same
characters intact. No `UnicodeEncodeError` was raised on any of the three,
which is the failure mode FINDING 10 exists for: it did not throw, it corrupted
silently.

The watch item was also miscast from the start. **No character beyond ASCII
punctuation appears in ANY of the three captures**, because the sweep prints
case ids, PASS/FAIL rows and serving-stack JSON and nothing else. What days 1
and 2 confirmed was em-dashes, not Chinese, Tamil or runes. The Chinese in
`weilue-chinese-quotation` reached the ANSWER and the archives, which is
FINDING 20 and stands; it never reached the transcript.

**No measurement is affected.** The per-run and sweep archives are JSON written
to disk by Python with an explicit encoding and never pass through the console.
Every digest matches at both ends of every sweep.

Recorded here rather than by editing the text above, on the precedent set when
FINDING 19 was withdrawn without rewriting `BLOCK_E_DAY1_RESULT.md`. Carried as
owed correction 6 in `BLOCK_E_RESULT.md` and applied 2026-08-28.
