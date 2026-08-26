# Block E day 1 — result

*2026-08-26. Two sessions, 198 chat calls, one date. Commit `a1850fd`.
Predictions in `BLOCK_E_DAY1_DRYRUN.md` were committed before the runs.*

## What ran

```
S1  37f79c93b79a  10:20:15-10:30:06 UTC  "Block E day 1"  99 runs
S2  0c74d52b2c25  11:48:17-11:58:46 UTC  "Block E day 1"  99 runs

both   33 cases x 3 repetitions, p7-answer-v2r, temperature 0
       corpus 26e4a683014bdf8a at BOTH ends of BOTH sweeps, corpus_moved None
       0 unstable content cells, 0 incomplete, 0 retried
       FLOOR MET in both

S1  content 73%  grounded 77%  refusal 36%
S2  content 73%  grounded 80%  refusal 36%
```

**Two sessions on one date was an accident** — the real sweep and the dry run
were pasted as one block, and a second run was started later in the belief the
first had not happened. It is kept, and labelled, because it turned out to be
the most valuable observation of the day. It adds a **session, not a date**:
`calibrate_floor` counts 2026-08-26 once and still refuses, needing three.

## FINDING 19 — the date boundary is real, and the D4 pilot sampled the unstable end

D4 reported text agreement collapsing **+61%** at the session boundary and
called it the session. It is not only the session. Holding the instrument, the
corpus, the prompt and the case set fixed, and varying only what separates the
two sessions:

```
the SAME six D4 cases, two sessions, TWO DATES (31h apart)     lost +61%
the SAME six D4 cases, two sessions, ONE DATE   (90min apart)  lost +28%
```

Same six questions, same everything else. **Crossing a date roughly doubles the
loss.** That is the first direct measurement of a date effect in this project,
and it could not be made before today because no two sessions had ever shared a
date with a repeated case set.

The other half is the case set, and it is larger than anyone would have
guessed:

```
the six D4 cases,      one date      lost +28%
the 27 cases D4 never ran, one date  lost  +7%
all 33 cases,          one date      lost +11%
```

**The six cases D4 piloted on are about four times more text-unstable than the
twenty-seven it never ran.** D4's sample was not representative, and it was
drawn — reasonably, at the time — from the cases with the longest archived
history, which are the cases that had given trouble. Every text-stability
number in `D4_RESULT.md` is therefore an upper bound on the system's
instability, not an estimate of it.

Neither correction was available to D4 and neither is a criticism of it. Both
change what its numbers mean.

## The verdicts are inert. All four ways.

```
                                        case    session   interaction  residual
D4, six cases, two dates                100%      0%          0%          0%
day 1, six cases, one date              100%      0%          0%          0%
day 1, 27 cases, one date               100%      0%          0%          0%
day 1, all 33 cases, one date  n=198    100%      0%          0%          0%
                                        mean 0.727
```

Every slice puts **all** the variance on the case and **none** on the session,
the interaction or the sampler. Whether a case passes is a property of the case.
Nothing about the session, the day, or the draw moves it.

Which is why the deliverable is two decompositions and not one. Read alone,
this table says the system is perfectly stable. The text table says 25% of
cross-session answer pairs are different strings. Both are true, and ruling 35
already forbids quoting the first as a statement about behaviour.

```
ANSWER TEXT, 33 cases, 198 runs, one date
  within a session   169/198 = 85%
  across sessions    222/297 = 75%
  different case     0/19008 = 0%      <- no shared refusal template, at scale
```

The cross-case baseline at 0 over nineteen thousand pairs is worth keeping: it
says the two rates above are measuring answers and not a template.

## FINDING 20 — `weilue-chinese-quotation` passes, and the answer path quotes Chinese

```
weilue-chinese-quotation   S1 3/3   S2 3/3   6 resolved quotations   1 text
```

The answer contains, verbatim:

> 大秦國一號犁靬，在安息、條支西大海之西 … 以石爲城郭

`floor.json` tracks this case as an open defect on the ground that *"nothing in
the answer path ever asks for a non-English source text to be quoted"*, and
`BLOCK_E_RUNBOOK` states the rule: **a sweep that reports a tracked defect
passing is a finding, not a success.**

Here is why it is one. **Only 6 of the 33 cases had ever been run in any
archived sweep.** `weilue-chinese-quotation` had **zero** prior runs. Its
defect entry says so in its own words — the 45-of-45 measurement was taken
*"across 16 archived runs of `chinese-da-qin`"*, a different case. The entry
generalised from a sibling to a case nobody had executed, and the first
execution falsifies it, twice, ninety minutes apart.

Two register entries fall with it:

- `FINDING 18`'s corollary, *"there is nothing non-Latin to print"*, and
  `D4_RESULT`'s *"the answer path has never quoted a non-English source text"*.
  Both were true when written and are false as of 10:30 on 2026-08-26.
- `BLOCK_E_START`'s trap 4, *"do not attempt a fourth non-Latin proof on the
  answer path"*. No fourth proof was attempted. The characters arrived on their
  own, in an ordinary run, exactly where `BLOCK_E_DAY1_DRYRUN.md` said to look.

Non-Latin characters above U+024F appear in the answers of seven cases —
Chinese in `weilue-chinese-quotation`, Greek (ΕΙΟΠΣΦΧЄ) in
`hoby-cheirisophos-signature`, and Ḏ or an em-dash in five others. **The
FINDING 10 stdout guard has now been exercised on the answer path**, through a
`*>` redirect on PowerShell 5.1, without a UnicodeEncodeError. That is the
proof D4 declared unobtainable, obtained by not trying to obtain it.

## FINDING 21 — retrieval rank does not predict failure

`floor.json` `demotions.vimose-runes.diagnosis` reads *"Retrieval margin, not
generation."* Thirty-three cases contradict it.

```
case                     rank  sim    spread from [S1]   day 1
jabal-dabub-basmala        3   0.388      0.135          3/3  PASS
vimose-runes               3   0.384      0.049          0/3  FAIL
muziris-cargo  REQUIRED    2   0.463      0.040          3/3  PASS
illerup-roman-coins        3   0.496      0.028          3/3  PASS
ezana-titulature           2   0.427      0.023          3/3  PASS
khao-sam-kaeo-intaglio     2   0.524      0.014          3/3  PASS
```

The case with the **worst** displacement in the entire set passes 3/3 in both
sessions. A required case sits at rank 2 inside vimose's own margin and passes
3/3. Rank and margin predict nothing.

The demotion itself stands: it rests on 0/3 across two dates, now 0/3 across a
third. But **the recorded diagnosis is wrong, and the `reinstated_when`
condition keyed to "[S1]" names a fix the evidence says is neither necessary
nor sufficient.** Both need rewriting. Neither is rewritten today — see the
freeze, below.

`vimose-runes` produced **3 distinct texts in S1 and 2 in S2** while holding
0/3 in both. Stable verdict, moving text, *within a single day*. D4 only ever
saw that shape across a date boundary.

## FINDING 22 — the right document, the wrong English

Predicted in `BLOCK_E_DAY1_DRYRUN.md` and committed before the run:

```
hoby-silius-identification    0/3   refusal 100%
hoby-cheirisophos-signature   3/3
```

Both retrieve the **same chunk**, `scandinavia-01-hoby-treasure::original::000`,
resolved `english=source ground=self`. That English is the
`original_text_excerpt`, which carries `Cheirisophos`, `ΣΟΦΟΣ`, `ЄΠΟΙΕΙ` and
`SILIVS`. The identification the second case is about — *Silius, possibly Gaius
Silius, Roman commandant at Mainz* — lives in `reference_translation`, and
`reference_translation` is not in the evidence block.

A third failure family, and it should not be folded into the other two:

```
aksum-exports               content IS in the evidence; the answer refuses anyway
weilue-chinese-quotation    entry was inferred, not measured — now falsified
hoby-silius-identification  content is in the RECORD and not in the EVIDENCE
```

Not actionable in Block E: retrieval and the corpus are frozen for the block.

## Four failures in no register at all

Twenty-four of 33 passed. Nine failed, identically in both sessions. Two are
tracked (`aksum-exports`, `vimose-runes`); one is FINDING 22. The rest are new,
and every one of them is a *near miss* rather than a collapse:

```
skz-titulature          answered well, never said "Ardashir"      (a required term)
raqosh-epitaph          stated a disputed reading without hedging (no hedge term)
aksumite-coin-imagery   quoted the record; the quotation did not RESOLVE to
                        characters on disk
oc-eo-cattigara         refused correctly, but the refusal did not say
                        "Ptolemy's Cattigara" as the case demands
```

None is a retrieval failure and none is a refusal-when-it-should-answer. Three
of the four are the answer being *nearly* right. Whether that is the system or
the gold assertions being over-tight is the first question Block F should ask,
and it is not answerable from inside a frozen block.

## What is deliberately NOT fixed

The rule between days is *change nothing*. Four corrections are owed and all
four wait until day 3 is archived, on the `calibrate_floor` precedent — its
self-contradicting last line was carried as a recorded defect through the whole
of D4 and fixed between blocks.

```
1  floor.json  weilue-chinese-quotation's defect entry is falsified
2  floor.json  demotions.vimose-runes diagnosis and reinstated_when are wrong
3  code        _serving_stack includes the per-call `id`, so the sweep archived
                99 "distinct stacks" and printed an alarming, meaningless line.
                The id belongs on the row, not in the stack identity.
4  code        serving_stack.model reads the alias `chat-default` in the sweep
                path. The row's own `model` field is correct and unaffected.
```

3 and 4 are additive metadata: they touch no verdict, no text, no corpus
assertion and no decomposition. 1 and 2 are reported-but-never-subtracted
fields. Nothing here changes a number on days 2 or 3.

## Gate G4, after day 1

```
[x] >=30 cases, each with an explicit expected behaviour     33
[ ] run 3x on >=3 separate days                              1 of 3 dates
[x] per-case and per-session stability as separate numbers   66/66, 33/33
[x] a stated VARIANCE DECOMPOSITION                          computed, four ways
[ ] the floor recalibrated, OR the reason it cannot be       REFUSED, 1 date
```

Days 2 and 3 remain: **2026-08-29 and 2026-08-31.** Nothing else is outstanding.

## The sentence that travels, amended

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT
was reachable. `muziris-cargo-akananuru` still sits at rank 310.

But the clause that has ridden with those two since Part 7 — *"and the answer
path has still never quoted a non-English source text"* — was retired at 10:30
this morning by a case that had never been run.
