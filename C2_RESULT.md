# C2 — the result, and three decisions

_2026-08-17, from `eval/ranking_runs/20260817T080300+0000-…-collapsed-reranked50.json`.
Renderings digest `af427581d957d0ba`, 205 admitted, 0 held._

## The number

```
                    recall@6      MRR@10    gapDoc     gapAny
single-variant      27/33 pairs    0.636   +0.0160    -0.0151
fused               26/33 pairs    0.579   +0.0163    -0.0174

per unit            pre    collapsed  reranked   via original
single-variant      27/30    28/30      29/30       21/30
fused               25/30    26/30      29/30       20/30

GAP     B2 baseline +0.0249    single +0.0160    fused +0.0163
```

**C2 moved the gap by +0.0003.** That is the fourth decimal place, and it is
still below the baseline G2 names. On every other measure it did harm.

## C2 is rejected, and the evidence is not close

1. **The gap did not move.** +0.0160 → +0.0163 over 33 pairs. `gapAny`, the
   diagnostic, got **worse**: −0.0151 → −0.0174.
2. **Recall fell.** 27/30 → 25/30 pre-rerank; 28/30 → 26/30 collapsed. Both
   arms land at 29/30 only because the cross-encoder rescues the fused arm from
   further back.
3. **`recall@6 via the original text` fell, 21/30 → 20/30.** That is the number
   this project exists to raise, and C2 was the only intervention aimed at it.
4. **Old Tamil went 2/3 → 0/3.** The language C2 was built for, the language
   most of this session's rendering work went into, is the one language fusion
   destroyed. Every other language held or gained (`grc` 8/12 → 9/12).
5. **Ruling 15b's control fired.** `probe-tamil-akananuru` — a Tamil query
   against a Tamil target, rank 1 in the single-variant arm — **fell to rank 14
   under fusion.** The control was written on 2026-08-16 to catch exactly this
   and it caught it on the first run that could trip it.

### The mechanism, stated because it generalises

Max over eight variants raises the ceiling for **every** candidate. A target
gains only when its own language rendering is good; a distractor gains from all
eight draws. The winning-variant table shows renderings claimed the target's
score for 19 of 33 pairs — and recall still fell, because the same renderings
were lifting distractors faster.

That is not a defect in the renderings and not a defect in the fusion. It is
what max-fusion does to a 450-chunk index where seven of eight variants are, for
any given target, in the wrong language. **Ruling 13 was declared before the run
and it produced a clean negative. That is the instrument working.**

## The gap criterion has never been measured the way it is written

G2 says *"score gap wider than baseline, **same pairs**"*. The pairs changed:
Block C's fifth item added `probe-tamil-akananuru-en` on 2026-08-14, after the
baseline was recorded. It is the hardest pair in the set at gapDoc −0.098.

```
gapDoc, all 33 pairs                    +0.0161   (the run prints +0.0160)
gapDoc, the 32 pairs B2 measured        +0.0196
W2b's recorded 450-chunk rung           +0.020
```

**The apparent slide from +0.020 to +0.0160 is the denominator changing, not
retrieval degrading.** On the pairs the baseline actually covers, the 450-chunk
gap is +0.0196 — essentially exactly what W2b recorded.

This does not rescue G2. +0.0196 at 450 chunks is still below +0.0249 at 57.
But it means the criterion as applied has been comparing two different pair sets
**and** two different index sizes, and only one of those was ever intended.

*(Figures above are reconstructed from the printed table, which rounds to three
decimals. Recompute from the archived run before either number is published.)*

## Three decisions

**Decision 1 — reject C2. Settled by the evidence above.** It is not adopted
into the configuration. The renderings, the guard and the fusion stay in the
repository as a measured negative result with 209 assertions and 86 mutations
behind them; `--fuse` remains available and off by default.

**Decision 2 — the frozen configuration is `--collapse --rerank`, unchanged
since 2026-08-16.** This is the consequence of decision 1, and it is what
unblocks C5–C6: the second day was blocked on the adoption decision, and the
adoption decision is now made.

**Decision 3 — the gap criterion. This one is the project owner's.**

- **3a. Declare G2's gap criterion failed and pull kill trigger 1.**
  `PHASE2_PLAN` pre-declared the response: W3 does not start; polish the
  sourcebook at 24–60 records rather than chase 200. Honest, and it is what the
  plan says to do. Cost: W3 does not happen.
- **3b. Re-measure the gap on the B2 pair set first, then decide.** Free, no
  calls, recomputed from archived runs. It is the criterion's own words — *same
  pairs* — and it changes the number under discussion from +0.0160 to +0.0196.
  It does not clear +0.0249, so this is unlikely to change 3a's outcome; it
  changes whether the failure is recorded honestly or against an arithmetic
  nobody intended.
- **3c. Rule that the gap criterion is unmeetable as written and replace it.**
  The gap narrows as the index grows — that is what the W2b curve measured and
  stated. A criterion that asks a 450-chunk gap to exceed a 57-chunk baseline
  cannot be met by any retrieval improvement; it can only be met by shrinking
  the index. If the criterion is to survive, it must compare like with like: a
  450-chunk gap against the 450-chunk rung, on the same pairs. **This is a
  change to the gate, and changing a gate after seeing the number it failed is
  the most dangerous move available.** It is defensible only if the argument is
  made from the W2b curve's shape, which was recorded before any of this, and
  only if the old reading is recorded beside the new one permanently.

**Recommended: 3b, then 3a or 3c on the corrected number.** Do the free
recomputation before deciding, because the current number is measured against a
denominator that changed after the baseline was set. Do not skip to 3c.

## What travels with any of this

- 29/30 is whether the RECORD was found. **21/30 is whether the non-English text
  was reachable**, and it is unchanged by C2.
- `muziris-cargo-akananuru` sits at rank 308 and is not counted toward the gate.
- The W2b curve rests on **English-only padding**; seams 1 and 2 were dropped on
  a time-box, so the twelve Greek-target pairs faced no competing Greek at any
  rung.
- The renderings file is best-of-2 for Old Tamil and best-of-1 for every other
  language.
