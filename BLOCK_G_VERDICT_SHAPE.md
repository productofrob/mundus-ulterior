# BLOCK G — THE SHAPE OF THE VERDICT, WRITTEN BEFORE THE RESULT DOCUMENT

*`BLOCK_G_START.md` §8 step 5: "decide the shape of the verdict before
assembling evidence for it, and write that decision down first — because a
verdict assembled from evidence already chosen is the same defect as a
prediction written after the run."*

**This file is that decision. It is committed before `BLOCK_G_RESULT.md`
exists.** If the shape below changes, the change is recorded as a change and
this text is kept, not rewritten.

---

## 1. THE ORDER THINGS ACTUALLY HAPPENED IN, STATED BECAUSE IT IS NOT CLEAN

§8's steps 1–4 require reading `cost_log report`, `F7_RESULT.md`,
`F7_RANKING.md` and the two gate documents before step 5. That was done. **Three
things were also assembled before this file was written, and they are not in
steps 1–4:**

1. `recall@6` decomposed **by cohort** across all ten comparable archived
   ranking runs.
2. `recall@6` decomposed **by `expect_lang` = en versus non-en**.
3. The configuration under which every archived ranking run was taken.

**That is more evidence than step 5 wanted in hand, and it went looking in a
direction nobody asked for.** It is recorded here rather than presented later as
though the shape came first. What it did *not* do is change a target, a box or a
denominator — see §4.

---

## 2. THE SHAPE

```
VERDICT                 PIVOT
Q1  ranking at scale    NO
Q2  signal from noise   YES, and the pass does not transfer to this corpus
Q3  curation cost       NO
G3                      FAILED, nine boxes, closed and failed
```

**PIVOT and not KILL** because the corpus is real and green: 54 records, seven
regions, four of five tiers on target, every integrity check passing, eleven
suites green, and the only answer-path observation above 24 records meeting the
floor.

**PIVOT and not PERSEVERE** because `PHASE2_PLAN.md` conditions persevere on
*passing all three*, and none of the three passes.

**The plan's own consequence for a failed Q1 is adopted and not softened:** the
product is corpus-bound, and the honest move is to polish the sourcebook at
24–60 records rather than chase 200. **200 is off the table.**

## Q1 — NO, and reading 2 is refused as an answer

`BLOCK_G_START.md` §2 offers two readings and requires an explicit choice. **The
answer is "No."**

Reading 2 — *the question is malformed* — is **true as a statement about the
measure** and is recorded as such. FINDING 91 proves rank movement is partly a
pure function of index size; FINDING 77's shrinking-index run is the natural
experiment. **It is refused as the ANSWER** because §2 says taking it obliges
Block G to deliver a replacement measure and the sentence that would have
falsified it, and a measure adopted by someone who has seen the run is
FINDING 83 at gate scale. The defect is booked as debt, to be **declared before**
the next record-adding run, which is the only timing at which declaring it is
legitimate.

## Q2 — YES as asked, and the pass is about a corpus that no longer exists

G4 closed on all five boxes and its deliverable was the variance decomposition.
That answers the question the phase asked. Ruling 49's corpus clause pinned it at
24 records by digest, deliberately, so nothing since can move it. **The pass is
recorded as a pass and as non-transferable in the same sentence.**

## Q3 — NO

The box reads *recorded and TRENDING DOWN*. Recorded: yes. Trending: the ledger
refuses, tier by tier, for reasons it states itself. **A ledger that refuses to
answer the question it was built for is a good instrument and a failed box, and
Block G calls it a failed box.**

---

## 3. THE ONE NUMBER THAT SHOULD WORRY THE READER

**`archived_answer` recall@6 = 0.125 — one pair of eight — down from four of
eight at 450 chunks.**

Not `muziris-cargo-akananuru` at rank 373. That pair is one pair, it has been the
obvious choice since Block C, and it is already named, diagnosed and travelling
with its own sentence.

---

## 4. WHAT THIS SHAPE DOES NOT DO

- **It does not amend G3.** Nine boxes, none met, target unchanged,
  `total_at_60` stays 60. Ruling 69 undisturbed.
- **It does not use a defect found after the gate failed as a reason to soften
  the gate.** Everything in §1 leaves every box exactly as failed as it was.
- **It does not curate, re-curate, or fix FINDINGS 82 or 86.**
- **It does not run a sweep.**
