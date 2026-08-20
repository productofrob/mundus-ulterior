# C6 — PASSED. G2 criterion 5 is met, and the two runs are byte-identical

_2026-08-20 15:12 UTC. `eval/ranking_runs/20260820T151200+0000-retrievable_chunks_with_distractors-collapsed-reranked50.json`
against C5's `20260819T102211+0000-…`. Judged on thresholds declared before C5
ran and not retuned since._

---

## The verdict

**Not "within tolerance" — identical.** Every threshold was written expecting
drift, and there is none to measure:

```
config fields on the abort list                    0 differ
unit-aggregate fields (all 24)                     0 moved
rank changes, pre / collapsed / reranked           NONE, at any stage
per-pair sim_target,  bit-for-bit                  0 of 33 differ
per-pair sim_best_other_doc, bit-for-bit           0 of 33 differ
rerank tokens                                      310185  =  310185

gapDoc, 33 pairs        +0.015946701  ->  +0.015946701   d = 0.000000000
gapAny, 33 pairs        -0.015152071  ->  -0.015152071   d = 0.000000000
gapDoc, B2's 32 pairs   +0.019534956  ->  +0.019534956   d = 0.000000000
```

The gated integers, restated because they are what the criterion reads:

```
recall@6 per unit    pre 27/30 0.900   collapsed 28/30 0.933   reranked 29/30 0.967
recall@6 via the original text         21/30 = 0.700
coverage             pre 28   collapsed 30   reranked 29   of 33 targets
```

### The tree was verified without touching it

Checked lock-free, blob hash against the committed blob, so no `git status` and
no index lock:

```
HEAD                          bff0605         unchanged since C5
eval/run_ranking_check.py     UNCHANGED
eval/gold/ranking_pairs.json  UNCHANGED
eval/gold/retrieval_probes.json, retrieve/search.py, retrieve/collapse.py,
retrieve/rerank.py, retrieve/fuse.py, retrieve/render.py, ingest/embed.py
                              UNCHANGED
```

Two runs, two calendar days, one provably identical tree, and one identical
number to seventeen decimal places. **That is the criterion satisfied at the
strongest level it can be.**

---

## G2 — six of seven

```
[x] ranking metric over >=20 pairs, baseline recorded before any change    B2
[x] distractor curve to >=450, shape stated and reproducible               W2b
[x] top 6 for >=95% at 450                       29/30 = 0.967
[ ] score gap wider than baseline                +0.019535 vs +0.024927    FAILED
[x] measured across >=2 sessions on different days    C5 2026-08-19 / C6 2026-08-20
[x] cite.py third match state, mutation-verified                           C1a
[x] translation_chunk* rename                                              C1b
```

**The gap is now the sole remaining failure, isolated, with nothing else
unmeasured beside it.** That was the entire purpose of running C5–C6 after
ruling 25 had already declared the gap failed: a criterion that fails alone is a
stronger record than one that fails with a second criterion still unknown.

---

## The determinism question — answered for the criterion, open as an observation

C6 reproduced C5 bit-for-bit, so **the query embedding is deterministic within a
régime** and the frozen configuration is exactly repeatable. Nothing about
C5–C6 rests on an unexplained quantity.

The wider history is still unexplained, and the batch-shape hypothesis is now
refuted:

```
run              pairs   embedding call                probe-greek-muziris sim_target
20260814 08:40    32     32 queries,  1 request        0.63747713789207683
20260814 13:35    32     32 queries,  1 request        0.63747713789207683
20260814 14:40    33     33 queries,  2 requests       0.63747713789207683   <- different shape, same vector
20260816 07:36    33     33 queries,  2 requests       0.63747713789207683
20260816 16:25    33     33 queries,  2 requests       0.63747713789207683
20260817 08:03    33    235 texts,    8 requests       0.63969614269161401
20260819 10:22    33     30 texts,    1 request        0.63903526300402180
20260820 15:12    33     30 texts,    1 request        0.63903526300402180   <- C6 reproduces C5 exactly
```

32-in-1 and 33-in-2 give the same vector, so **batch composition is not the
cause.** Two régime changes are visible — one at or before 08-17, one at or
before 08-19 — and neither is explained by anything in the repository: no query
cache exists, `gateway/config.yaml`'s only edit is the additive `chat-strong`
alias, the index is unmoved at 450/450/0, and the query text has not changed
since 08-14. The remaining explanation is provider-side, and it is recorded as
an open observation, not a finding.

### What must travel with future numbers

```
within a régime      comparisons are EXACT           C5 = C6, to the bit
across a régime      aggregate gapDoc floor  ~1e-4
                     per-pair gapDoc floor   ~2e-3
```

**B2's baseline `+0.024927` was measured in the old régime; C5–C6's `+0.019535`
is in the new one, so the gap criterion's comparison now spans a boundary.** It
does not rescue the gap and does not disturb ruling 25 — the deficit is
**0.005392**, and the régime drift is **~1.6% of it**, two orders of magnitude
too small to matter. But it belongs beside the number, because every future
comparison in this repository against a pre-08-17 figure carries that floor and
nothing else in the archive says so.

---

## What happens next, in order

1. **Commit the two run JSONs.** They are the evidence for criterion 5 and they
   are currently untracked. This is now safe — the two-day window is closed.
2. **The sequencing-trap fix.** `recall@6 via the original text` is computed
   PRE-rerank while the adopted configuration reranks. Ruled *after C6*, and C6
   is archived, so it is unblocked as of now. It changes code on the ranking
   path, which is exactly why it waited. **21/30 must not leave `PROGRESS.md`
   until this lands.**
3. **`PROGRESS.md` write-up and Block C closes** — ruling 25, C5–C6, G2 at six
   of seven, the régime note above, and the two hazards found in the archive
   (the uncommitted ranking path, and `20260814T144013` reporting an index size
   it did not search).
4. **Kill trigger 1 is already pulled.** W3 does not start. The work after Block
   C is the sourcebook at 24–60 records.

### The sentence that travels with all of it

**29/30 is whether the RECORD was found. 21/30 is whether the NON-ENGLISH TEXT
was reachable** — and `muziris-cargo-akananuru` still sits at rank 310, the
corpus's one genuinely broken cross-lingual link, not counted toward the gate.
C5 and C6 measured a stable pipeline. They did not measure a solved problem.
