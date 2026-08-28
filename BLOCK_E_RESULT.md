# Block E — result

*2026-08-28. Four sessions, three dates, 396 chat calls, one corpus digest.
Written at the close of day 3, which is the day the block stopped replicating.*

`BLOCK_E_START.md` is still the statement of what Block E is and
`BLOCK_E_RUNBOOK.md` is still how it was run. This is what it measured.

## What ran

```
S1  37f79c93b79a  2026-08-26  10:20:15-10:30:06 UTC  "Block E day 1"   99 runs
S2  0c74d52b2c25  2026-08-26  11:48:17-11:58:46 UTC  "Block E day 1"   99 runs
D2  6715f2a3ab6b  2026-08-27  10:20:44-10:30:48 UTC  "Block E day 2"   99 runs
D3  6a382f4f9ac7  2026-08-28  10:23:00-10:32:15 UTC  "Block E day 3"   99 runs

    33 cases x 3 repetitions, p7-answer-v2r, temperature 0, haiku-4-5
    corpus 26e4a683014bdf8a asserted at BOTH ends of ALL FOUR sessions
    corpus_moved None in all four. 24 records, 450 embeddings, 0 pending.
    0 incomplete, 0 retried, 0 unstable content cells in any session
    crossed_midnight_utc false in all four
    FLOOR MET in all four
```

Day 3 was held to the morning slot on purpose. It began 24h 02m 16s after
day 2 and 48h 02m 45s after day 1 S1 — the closest thing this design can
produce to a pure 24-hour and a pure 48-hour date crossing, measured at the
same hour of the same kind of weekday morning.

Its own summary, read alone, is the cleanest of the block:

```
content 72.7%   grounded 78.8%   refusal 36.4%   mean resolved quotes 1.55
per-case stability 33/33 = 100%   unstable content 0   unstable grounded 0
```

**That summary is wrong about what happened, and the rest of this document is
why.**

## FINDING 25 — the answer text moved wholesale between 2026-08-27 and 2026-08-28. It is a step, not a gradient.

Every pair is scored against the within-session agreement of the two sessions
it actually contains, so no pair borrows a baseline from a session it does not
include. The first three rows are `BLOCK_E_DAY2_RESULT.md`'s committed table,
recomputed here from the archives and reproducing it to the decimal — the
instrument agrees with the published numbers before it is pointed at the new
pairs.

```
pair       separation            within         across          lost
S1 vs S2   same date,  1.5h    169/198  85%   222/297  75%    +10.6
S1 vs D2   ACROSS,    24.0h    163/198  82%   221/297  74%    + 7.9
S2 vs D2   ACROSS,    22.5h    174/198  88%   228/297  77%    +11.1
D2 vs D3   ACROSS,    24.0h    173/198  87%   134/297  45%    +42.3
S1 vs D3   ACROSS,    48.0h    168/198  85%   135/297  45%    +39.4
S2 vs D3   ACROSS,    46.6h    179/198  90%   135/297  45%    +44.9
```

The three sessions before day 3 agree with each other at 74-77%. All three
agree with day 3 at 45%.

**The separation does nothing.** The 48-hour pairs lose +39.4 and +44.9; the
24-hour pair loses +42.3. Doubling the elapsed time changes the loss by less
than the difference between the two 48-hour pairs themselves. Whatever
happened is not a function of how long you wait.

**Day 3 was not internally noisy.** Its within-session agreement is 87-90%,
the highest of the four sessions, and its per-case stability is 33/33 with
zero unstable cells. It was internally more unanimous than the sessions it
disagrees with.

The 27 cases D4 never ran say it without the pilot sample in the way:

```
the 27 cases    same date,  1.5h    +6.8        ACROSS, 24.0h (D2/D3)   +41.4
                ACROSS,    24.0h    +6.0        ACROSS, 48.0h (S1/D3)   +40.7
                ACROSS,    22.5h    +6.2        ACROSS, 46.6h (S2/D3)   +45.1
```

Three measurements spread over 0.8 of a point, then three more spread over 4.4
points, six times higher, with no ordering by distance.

`eval.decompose`, pooling all four sessions:

```
ANSWER TEXT, 33 cases, 4 sessions, 396 runs, THREE DATES
  within a session   342/396    = 86%
  across sessions   1075/1782   = 60%
  different case       0/76032  =  0%
  agreement lost at the session boundary: +26 pts
```

Day 2's pooled figure over three sessions was +10 pts. Adding one session
moved it to +26. The three new pairs contribute 404 of 891 agreements — 45%
— against 671 of 891, 75%, among the first three.

### What this does to FINDING 23

FINDING 23 was written yesterday and said: *"there is no date effect. The
boundary is the session, and nothing is added by crossing a date."* It named
its own failure condition — *"wrong if either across-date figure exceeds about
+20 pts"* — and both new across-date figures are at twice that.

**FINDING 23 is withdrawn.** But note carefully what replaces it and what does
not:

- **Its negative half survives and is strengthened.** Distance across dates
  still buys nothing. Six pairs now span 1.5 to 48 hours and the loss does not
  order by separation at any point. `BLOCK_E_DAY2_START` recorded that this
  block could not properly answer whether separation grows with distance; it
  still cannot, and nothing here suggests it does.
- **Its positive half is dead.** "Nothing is added by crossing a date" is
  refuted by a crossing that added 42 points. What day 3 shows is not a date
  effect but a **discontinuity located at day 3**, and the difference matters:
  a date effect would predict the 48-hour pairs lose most, and they do not.

Yesterday's second prediction was the one to watch — *"a 48-hour pair inside
the same band makes FINDING 23 harder to dislodge without settling it."* The
48-hour pair landed outside the band along with everything else touching day 3,
which dislodges FINDING 23 and settles nothing.

## FINDING 26 — the verdict layer is NOT invariant. Two cases flipped, they cancelled exactly, and the pass rate did not move.

FINDING 24 said no verdict moved across a session or a date. Two moved on day
3, and both moved only on day 3:

```
oc-eo-roman-coins       S1 fail   S2 fail   D2 fail   D3 PASS
pattanam-dna-evidence   S1 pass   S2 pass   D2 pass   D3 FAIL

per-session stability   33/33 = 100%  (three sessions)
                        31/33 =  94%  (four sessions)

VERDICTS (content_ok), 33 x 4 x 3 = 396, balanced
  mean 0.727
  case             92.4%   var +0.18892
  session           0.0%   var -0.00047   negative, reported then clamped
  case_x_session    7.6%   var +0.01562
  residual          0.0%   var +0.00000
```

**FINDING 24 is withdrawn.** The prediction committed against day 3 — *"case
100%"* — failed.

**The important part is the shape of the failure.** One case gained a pass and
one lost a pass, so `content_pass_rate` reads 0.727272… in every one of the
four sessions, to every digit printed. The session *main* term therefore
estimates negative and clamps to zero, and the entire effect lands on the
interaction. The aggregate is byte-identical across four sessions and three
dates while the set of cases behind it is not.

This is FINDING 18's lesson one level up. Part 8 built the two-number stability
report because a single flakiness figure hid a session boundary; day 3 shows
that a single *pass rate* hides one too. A report carrying only 72.7% would
have called day 3 the cleanest replication of the block. The decomposition and
the per-session number are what caught it, which is what they were built for
and the first time either has had to earn its keep on live data.

The two flipped cases are not required cases. The floor's three —
`antikythera-absent`, `chinese-da-qin`, `muziris-cargo` — went 12/12 across
all four sessions.

## FINDING 27 — it is generation-side. Retrieval held.

The evidence blocks were hashed across all four sessions:

```
30 of 33 evidence blocks BYTE-IDENTICAL in every session
 3 moved: akananuru-yavana-ships-tamil, pattanam-dna-evidence,
          weilue-ruler-selection
```

So 91% of cases were handed the same prompt and the same evidence in every
session, at temperature 0, and 55% of the answer text changed anyway.

The two verdict flips split cleanly on this:

- `pattanam-dna-evidence` is one of the three whose evidence moved. **That flip
  has a retrieval explanation available.**
- `oc-eo-roman-coins` is one of the thirty that did not. Identical question,
  identical evidence block, identical prompt version, temperature 0, and the
  verdict changed. **That flip has no explanation in this archive at all.**

The text differences are real prose, not formatting. 14 of 33 first-repetition
answers are byte-identical D2 to D3, and normalising whitespace and case moves
that count by exactly nothing. `oc-eo-roman-coins` rewrote a quotation as
reported speech and back; `weilue-chinese-quotation` was rewritten almost
entirely, at 0.16 character similarity.

## The serving stack, and the limit that was stated before day 1

The probe was run once before day 1 and once after day 3. Both readings:

```
{"id": "chatcmpl-…", "model": "anthropic/claude-haiku-4-5-20251001"}
```

No `system_fingerprint`, no `service_tier`, no LiteLLM `model_id` or
`custom_llm_provider`, either time.

**The second reading confirms nothing, and this was known before the first
call of the block.** Runbook decision 3a records it: `id` is unique per call
and traces one archive to one request, but says nothing about what served it;
`model` is the alias echoed back byte-identical to what was sent, so it
*cannot* move and therefore cannot report drift. The conclusion drawn on
2026-08-26 was that *"nothing in the Block E archives can distinguish
provider-side drift from sampling variance, and FINDING 18's question cannot
be answered by this block."*

Day 3 is exactly the shape provider-side drift would take, and that stated
limit is now the operative one. Findings 25, 26 and 27 describe a
discontinuity that this archive can locate to a date and cannot attribute to
a cause. Recording the limit before day 1 rather than discovering it after day
3 is the difference between a boundary and an excuse, and it is the reason
this result can be stated plainly instead of guessed at.

One thing still cuts the other way and belongs beside it: `chat-default`
points at a **dated** model id, not a floating alias, which is a stronger
guarantee against a silent model swap than a fingerprint on an undated alias
would be. It does not rule out serving-stack changes underneath a fixed model
id, and nothing available here does.

## The predictions, scored against what was committed at 4860711

Written into `BLOCK_E_DAY2_RESULT.md` and committed **before day 3 ran**, for
the reason `BLOCK_E_DAY1_DRYRUN` gives: a prediction made before the run is
evidence, and the same observation made afterwards is a story. They are scored
here and were not revised.

```
                                        predicted     actual        verdict
2026-08-27 vs 2026-08-28  ~24h        +6 to +12      +42.3         FAILED
2026-08-26 vs 2026-08-28  ~48h        +6 to +12      +39.4 / +44.9 FAILED
the 27 cases, either pair             +5 to +8       +40.7 … +45.1 FAILED
the verdict decomposition, 396 runs   case 100%      case 92.4%    FAILED
```

Four for four, all in the same direction, all by a wide margin. A day booked
to replicate two previous days replicated neither, and the design that made
that legible is the deliverable.

## The three things day 3 was told to watch

- **`weilue-chinese-quotation`: 3/3 for the fourth time — on TWO distinct
  texts.** Twelve runs, twelve passes, across four sessions and three dates.
  The nine-run byte-identical streak that made this case remarkable ended
  today: its day-2 and day-3 answers share 0.16 of their characters. The
  verdict held and the text did not, which is FINDING 25 inside the one case
  that had been immune to it. Its `floor.json` defect entry — inferred from 16
  runs of a sibling case that is not this one — is now falsified on three
  dates. It survives in the file to this commit because of the freeze and for
  no other reason.
- **`vimose-runes`: 0/3 for the fourth time, on ONE distinct text** (3 in S1,
  2 in S2, 2 in D2, 1 today). Stable verdict, and today the text stopped
  moving — the opposite of every other case. Demoted on two dates of evidence,
  now 0/3 in six sessions over five dates.
- **Non-Latin characters in the capture: the watch item was miscast, and day 2
  failed it.** See correction 6.

`unstable_grounded_cells` read 1, 1, 0, 0 across the four sessions. Groundedness
only; `unstable_content_cells` is 0 in all four, so no floor verdict and no
decomposition input is affected. Recorded, not acted on.

## The floor, now calibrated

`calibrate_floor` reported ELIGIBLE for the first time in this project and the
write was taken:

```
calibrated              true          (was false since 2026-08-10)
calibrated_at           2026-08-28T10:51:56+00:00
calibrated_from_dates   2026-08-26, 2026-08-27, 2026-08-28
calibrated_from_sessions 4
calibrated_from_sweeps  the four 33-case Block E archives
calibration_excluded_sweeps  five, each with the reason it fails the rule
calibrated_stability    per_case    132/132 = 1.000
                        per_session  31/33  = 0.939
```

**The 94% is in the file.** The two flipped cases are recorded in the artefact
the floor was calibrated from, not buried under the pass rate that did not
move — which is the only condition on which this write was defensible at all.

It was taken rather than declined on the ground `calibration_scope` already
states in its own anti-loophole: *"a sweep that SATISFIES the rule cannot be
excluded by name"*, because otherwise the list is *"a place to put a sweep
whose numbers nobody liked."* Declining a gate that passes, on the strength of
a finding made the same morning, is that move wearing the other hat. The gate's
three required cases went 12/12 through the very session that changed 55% of
the answer text, which is precisely what a regression gate is for.

The floor remains what it always was, and FINDING 25 does not change it: a
regression gate, not a definition of success.

## Gate G4 — closed

```
[x] >=30 cases, each with an explicit expected behaviour
       33: 22 answerable / 3 gloss / 8 correctly_refusable, >=3 per region
[x] run 3x on >=3 separate days
       2026-08-26 (two sessions), 2026-08-27, 2026-08-28
[x] per-case and per-session stability as separate numbers
       132/132 = 100%   and   31/33 = 94%
[x] a stated VARIANCE DECOMPOSITION, with the data archived
       eval/decompositions/20260828T104000-decomposition.json
[x] the floor recalibrated, OR the reason it cannot be
       calibrated: true, over four sweeps and three dates
```

**The deliverable was the decomposition, not the pass rate — and on the last
day of the block that stopped being a slogan and became the finding.**

## THE FREEZE — SEVEN corrections are now owed, and it LIFTS with this commit

Five were carried into day 3. Two were found today and, per the freeze, were
written down rather than fixed.

```
1  floor.json   weilue-chinese-quotation's defect entry is FALSIFIED. 12/12
                across four sessions and three dates. The entry was inferred
                from 16 runs of chinese-da-qin; this case had never been run
                when it was written.
2  floor.json   demotions.vimose-runes: the diagnosis "retrieval margin, not
                generation" is contradicted by 33 cases, and reinstated_when is
                keyed to a fix the evidence says is neither necessary nor
                sufficient. The DEMOTION stands — 0/3 in six sessions over five
                dates now. The
                recorded reasoning does not.
3  code         _serving_stack includes the per-call `id`, so each sweep
                archives 99 "distinct stacks" and prints an alarming
                meaningless line. The id belongs on the row, not the identity.
4  code         serving_stack.model reads the alias `chat-default` in the sweep
                path. The row's own `model` field is correct.
5  code         run_answer_sweep has no --progress and never flushes, so a
                ten-minute 99-call sweep shows nothing until it exits. Fix:
                --progress writing one line per completed cell to stderr with
                flush=True, so `*>` still captures everything while a plain run
                is watchable. Held back from day 3 on purpose: changing the
                invocation would have made day 3's capture the only one
                produced a different way, on the one day meant to replicate the
                other two.
6  process      DAY 2'S CAPTURE IS MOJIBAKE, and day 2's result document says
                the opposite. eval/block-e-day2.txt contains Γ x40, Ç x40,
                ö x39, ª x1 — UTF-8 em-dashes and one ellipsis read back
                through CP850. Days 1 and 3 hold the same characters intact.
                No UnicodeEncodeError was raised on any of the three, which is
                the failure mode FINDING 10 exists for: it did not throw, it
                corrupted silently. The watch item was also miscast from the
                start — no character beyond ASCII punctuation appears in ANY of
                the three captures, because the sweep prints case ids,
                PASS/FAIL rows and serving-stack JSON and nothing else. What
                was being confirmed on days 1 and 2 was em-dashes. NO
                MEASUREMENT IS AFFECTED: the per-run and sweep archives are
                JSON written to disk by Python with an explicit encoding and
                never pass through the console, and every digest matches at
                both ends.
7  floor.json   calibrated_from still names the invalidated 2026-08-10 sweep
                while calibrated_from_sweeps names the four Block E archives.
                A stale provenance pointer beside a fresh one. Found on
                inspecting the write, not fixed, because the write is the
                artefact this block is judged on.
```

**With this commit the freeze is over.** All seven are the first work of the
next step, and none of them is Block F.

## What is NOT a finding

`aksum-exports` failing. 0/3 in all four sessions, tracked, out of
`required_cases`, not closed by Block E.

`vimose-runes` failing. Demoted on two dates of evidence, now 0/3 in all four
Block E sessions and both D4 pilots — six sessions, five distinct dates.
Reported beside the floor verdict for ever and never subtracted from it.

`weilue-chinese-quotation` passing. 12/12 and its defect entry survives to this
commit because of the freeze, not because anyone believes it.

**The 99 "distinct serving stacks" line.** Owed correction 3. It is the
per-call `id` in the identity, not a provider changing under the run — and
note that it would have looked identical on a day when a provider *had*
changed, which is correction 3's real cost.

## What Block E measured, and what it did not

It set out to ask whether the answers this system gives can be improved on
purpose. It answered a narrower question and answered it well: **you cannot
tell, from a pass rate, whether anything moved.** Four sessions returned
0.727272… and the fourth said different things about 55% of the corpus and
reversed two verdicts while doing it.

It could not answer why. That was known on 2026-08-26 and written down before
the first call.

The experiment that could is the one runbook 3b already names and rules out of
this block: a sonnet arm at temperature 1, run **beside** the frozen haiku
archive and never folded into it, with its own gate and its own repetitions.
`aksum-exports` failing 0/3 under four prompts with the answer sitting in
published English in its own evidence block is still attributed to prompt and
retrieval, and nobody has tested whether the answer path is model-limited.

## The sentence that travels

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT
was reachable. `muziris-cargo-akananuru` still sits at rank 310.

The clause that rode with those two since Part 7 was retired on 2026-08-26 by
a case that had never been run. Do not carry it forward.
