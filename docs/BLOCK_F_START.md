# Block F — starting point for the next thread

*Written 2026-08-28, after Block E closed and its eight corrections landed.
`PHASE2_PLAN.md` is still the statement of what Block F is — W3, corpus 24 to
60, eight sessions, gate G3. This is the state it inherits, the four decisions
that must be settled BEFORE F1, and the one window that closes the moment the
first sub-tranche lands.*

## Read these, in this order

| # | file | why |
| :---- | :---- | :---- |
| 1 | **this file** | state, the four open decisions, the window |
| 2 | `BLOCK_E_RESULT.md` | findings 25-27, and READ THE APPENDED CORRECTION |
| 3 | `PHASE2_PLAN.md`, the Block F section only | F1-F8 and the G3 checklist |
| 4 | `eval/gold/floor.json` | read whole. `calibrated: true` for the first time |
| 5 | `BLOCK_E_RUNBOOK.md` | the five decisions, the traps, why the model does not move |
| 6 | `PROGRESS.md` **last section only** | ~594 KB. Do not read it whole |

## State, as measured 2026-08-28

```
tree            1bdaf04, clean
                1bdaf04  Block E corrections: all eight applied, and two found
                         while applying them
                e3fed40  Block E day 3: the block stopped replicating, and the
                         pass rate did not move
                28e8c62  Block E: the day 3 handoff, and the fifth owed
                         correction

corpus          24 records / 450 embedded / 0 pending
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                asserted at BOTH ends of ALL FOUR Block E sessions.
                THIS IS THE BASELINE EVERY BLOCK E NUMBER IS DENOMINATED IN.

ANSWER          eval.test_answer_eval       292   GREEN   (was 283)
mutations       scripts/mutate_part8.py      66   GREEN   (was 61)
RANKING         eval.test_ranking_check     236   GREEN   (was 231)
mutations       scripts/mutate_ranking.py   100   GREEN   (was 97)

gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
sweeps          9 archived. 4 in scope, 5 excluded by the recorded rule.
decompositions  1   eval/decompositions/20260828T104000-decomposition.json

floor           calibrated: TRUE, 2026-08-28, first time in this project
                from 3 dates and 4 sessions
                per_case    132/132 = 1.000
                per_session  31/33  = 0.939   <- the two flips are IN the file
                required     antikythera-absent, chinese-da-qin, muziris-cargo
                known_failing  aksum-exports, weilue-chinese-quotation,
                               vimose-runes

serving stack   {id, model} only, and NEITHER identifies a stack. Confirmed
                2026-08-28 through the alias a sweep uses: model echoes back
                `chat-default`, identity is {}. Provider drift and sampling
                variance are NOT separable in these archives — stated limit,
                now measured on the right path.

gates           G4 CLOSED. G3 is Block F's.
```

## What Block E leaves Block F, in one paragraph

Four sessions over three dates returned `content_pass_rate` 0.727272… to every
digit printed. The fourth said different things about 55% of the corpus and
reversed two verdicts while doing it, and the two reversals cancelled exactly.
**The pass rate cannot see change.** That is FINDING 26, it is the reason the
variance decomposition exists, and it lands directly on Block F's gate.

## THE FOUR DECISIONS — settle these BEFORE F1, and write them down

`BLOCK_E_RUNBOOK` states the rule this project runs on: anything unsettled on
day 1 stays unsettled for the whole block or costs the whole sweep. Block F is
eight sessions and it moves the corpus. These four are open.

### 1. G3's checklist is blind where it matters most

As written it says:

```
[ ] full sweep re-run at 60: content pass rate not lower than at 24
```

Day 3 is the counter-example. A sweep at 60 records could return 0.727272…
having changed the system's behaviour completely, and that box would tick.
**Proposed:** keep it, and add beside it the two numbers that DID see day 3 —

```
[ ] per-session stability at 60, reported beside the pass rate
[ ] cross-session answer-text agreement at 60, against Block E's 74-77% and 45%
```

Both already exist, are archived, are mutation-verified, and cost nothing to
compute. This is a gate amendment and must be recorded as one, in advance, not
applied at the end.

### 2. The frozen-corpus window closes at the first sub-tranche

`26e4a683` is the denominator of all 396 Block E runs. F3-F7 move it. **Any
experiment that wants to be comparable to the Block E archive has to run
before the first sub-tranche lands, or it is measuring a different corpus.**

The one on the table is runbook 3b's: **a sonnet arm at temperature 1, run
BESIDE the frozen haiku archive and never folded into it.** Nobody has tested
whether the answer path is model-limited. `aksum-exports` fails 0/3 under four
prompts with the answer sitting in published English in its own evidence block,
and that is attributed to prompt and retrieval on no evidence either way. It
needs its own gate and its own repetitions because it cannot be greedy.

**Decide: run it in the window, or record that the window was allowed to close
and why.** Both are answers. Silently losing it is not.

### 3. The gold assertions may be too tight, and Block E could not ask

FINDING 22 and day 1's four unregistered failures: `skz-titulature` answered
well and never said "Ardashir"; `raqosh-epitaph` stated a disputed reading
without the hedge term; `oc-eo-cattigara` refused correctly without saying
"Ptolemy's Cattigara"; `aksumite-coin-imagery` quoted the record and the
quotation did not resolve to characters on disk. **Three of the four are the
answer being nearly right.** Whether that is the system or the assertions is
the first question Block F should ask, and it was not answerable from inside a
frozen block. Ask it before curating 36 new records against the same style of
assertion.

### 4. What promotes `weilue-chinese-quotation`, and what the bar now is

12/12 across four sessions and three dates, and still in `known_failing_cases`
— deliberately, because promoting a case while correcting a floor error is how
errors compound. But FINDING 26 also moved the standard:
`demotions.vimose-runes.reinstated_when` asks for two sessions on two dates,
and day 3 produced a case unanimous across THREE sessions that flipped on the
fourth. **Decide whether the reinstatement bar rises, and apply the same answer
to both cases.** Recorded in floor.json as Block F's decision, not settled.

## What does NOT move in Block F

The model. Runbook 3b settles it and nothing has changed: sonnet refuses
`temperature=0` (ruling 22), every archived number is haiku at temperature 0,
and repointing `chat-default` would make all of them incomparable. A sonnet arm
is a SECOND alias and a separate archive, never a replacement.

## Traps

Everything in `BLOCK_D_START.md`, `D4_START.md`, `BLOCK_E_START.md`,
`BLOCK_E_RUNBOOK.md`, `BLOCK_E_DAY2_START.md` and `BLOCK_E_DAY3_START.md` still
applies. Four are worth re-reading before touching anything:

- **Never run a mutation harness through the Cowork bridge.** Each call is
  killed at 45 seconds, the harness restores its sources in a `finally` that
  then never runs, and the tree is left with a live mutation in it. This is now
  MORE dangerous than it was: `eval/run_answer_sweep.py` joined
  `mutate_part8.py`'s SOURCES on 2026-08-28, so a killed run can leave the
  sweep runner itself mutated. Host only.
- **`git` through the bridge leaves `.git/index.lock` behind.** Use
  `--no-optional-locks` for anything read-only, or do not run git through the
  bridge at all.
- **`eval/goldset.py` and the two `answer/` modules are CRLF; everything else
  in `eval/` is LF.** Match the file, do not normalise the repository.
- **A mutation anchor appearing in more than one SOURCE resolves
  first-source-wins, in silence.** It has happened twice — 2026-08-24, and
  again on 2026-08-28 the moment a third source was added. The harness's own
  ambiguity check caught it both times. Do not disable it.

## What is NOT a finding

`aksum-exports` failing. 0/3 in all four Block E sessions. Tracked, out of
`required_cases`, and the case runbook 3b names as the reason to want a sonnet
arm.

`vimose-runes` failing. 0/3 in six sessions over five dates. Demoted with
evidence, a corrected diagnosis that names what was ruled out rather than
guessing a replacement, and a reinstatement condition no longer keyed to a
falsified mechanism. Reported beside the floor verdict for ever and never
subtracted from it.

`weilue-chinese-quotation` passing. 12/12. See decision 4.

## The sentence that travels

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT
was reachable. `muziris-cargo-akananuru` still sits at rank 310.

The clause that rode with those two since Part 7 was retired on 2026-08-26 by a
case that had never been run. Do not carry it forward.

And one more, from day 3, which travels with them now:

**Four sessions read 0.727272… and one of them was different. The pass rate
cannot see change.**
