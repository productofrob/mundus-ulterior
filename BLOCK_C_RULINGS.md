# Block C — the rulings, and what they cost

_Four on 2026-08-14; two more on 2026-08-16, both forced by the first working
measurement of the 450-chunk rung._

_Ruled 2026-08-14 by the project owner, against the per-pair evidence in
`eval/ranking_runs/20260814T084042+0000-retrievable_chunks.json` (57) and
`…T133556+0000-retrievable_chunks_with_distractors.json` (450). Every number
below was recomputed from those two files, not carried from a document._

These four were the critical path. `claude/phase2-block-c-plan.md` argued that
Block C's blocking work is decisions rather than engineering; this file is the
decisions. Nothing here is a recommendation — each is settled, and each says what
it costs, because three of the four make the gate easier to reach.

---

## Ruling 1 — a multi-target query is ONE unit with N acceptable targets

**Scored on its best acceptable target.** A ranking that finds one of three
targets and one that finds all three are no longer the same result only because
the metric happens to count rows.

### The correction that came with it

`claude/phase2-block-c-plan.md` states the post-ruling figure as **26/30**. That
collapsed the Muziris query and left the other shared query — *"How did Chinese
sources describe the Roman empire?"*, two pairs at ranks 4 and 5 — expanded.
Applied consistently to both, the arithmetic at 450 chunks is:

```
per pair, today                 26/32 = 0.812
collapse Muziris only           26/30 = 0.867     <- the plan's figure
collapse both, consistently     25/29 = 0.862     <- the ruling
```

Collapsing the China query removes a unit and a hit, so it lowers the ratio. The
ruling is still worth making — but it is worth making for the reason it was
argued, not for five thousandths of recall.

### What the gate now requires

At 29 units, **≥0.95 permits at most one miss** (28/29 = 0.966; 27/29 = 0.931).
Four units miss today:

```
unit                       rank   status
aksum-trade-adulis           35   in a top-50 rerank window
au-khao-sam-kaeo             17   in a top-50 rerank window
adulis-exports               15   in a top-50 rerank window
tc-frankincense-harvest      11   in a top-50 rerank window
```

**At least three of those four must be fixed for G2 to pass.** The ruling alone
does not reach the gate; it makes the gate reachable, which is a different claim
and the one to write down.

> **Amended 2026-08-14, later the same day.** The English→Tamil probe below was
> added, so the set is **33 pairs over 30 units** and the gate again permits at
> most one miss (29/30 = 0.967). The new pair is **unmeasured** — it was written
> after the last run. If it misses, which is what its own note expects, the
> requirement becomes **four of five fixed, not three of four**.
>
> That is the ruling's arithmetic getting *harder* because of an instrument
> added to watch the thing the ruling stopped counting. It is the correct
> direction and the reason to add the probe before C3 rather than after.

### What it costs, stated plainly

The two targets that stop being counted are `muziris-cargo-papyrus` (rank 109)
and `muziris-cargo-akananuru` (rank 309). The second is the corpus's **one
genuinely broken cross-lingual link** — an English query that cannot reach an Old
Tamil passage from three hundred ranks away. B1's own notes named "weakening what
the metric means" as the thing to refuse, and this ruling does some of that.

**Therefore, mandatory and non-negotiable:**

1. Every unit reports **coverage** alongside recall — how many of its acceptable
   targets sit in the top 6. It is reported, never gated. Today: Muziris **1/3**,
   China **2/2**.
2. The Old Tamil result is a **standing finding** that appears on the same page
   as any G2 number, in words, every time. A gate that passes while a known
   failure is uncounted is only honest if the failure is printed beside it.

---

## Ruling 2 — the four `translation_case` pairs accept the document's own published translation of the same section

An English query that retrieves the published English of Periplus §29 has done
something correct, not something wrong. The pair was written to test
cross-lingual reach; it was not written to declare a faithful translation of the
right section a miss.

**Still a miss** if retrieval lands on a *neighbouring* section of the same
document — §27–28 rather than §29. That was the discrimination
`tc-frankincense-harvest` was authored to make, and it survives.

### Why this does not weaken cross-lingual measurement

Cross-lingual reach is measured by the four `lang_pool: non_english` probes,
where an English translation is **excluded from the candidate pool by
construction** and cannot satisfy the pair. Those four (`probe-frankincense-kane`,
`probe-adulis-ivory`, `probe-roman-embassy`, `probe-roman-provinces`) all rank 1
at 450 chunks. The `translation_case` cohort measures something else — whether
retrieval reaches the right *section* — and after this ruling it measures that
and nothing else.

### The evidence gap this ruling exposed

The premise behind it — *"the chunk beating the target is always that document's
own English translation"* — is **not recoverable from either archived run**.
`run_ranking_check.py` recorded `sim_best_other_chunk` and never which chunk it
was. The claim had to be re-derived by hand in B5 and could afterwards only be
recalled.

Fixed on 2026-08-14: `PairResult` now carries `best_other_chunk_id` and
`best_other_doc_chunk_id`, asserted in `eval/test_ranking_check.py`. A chunk id
carries its own role and document, so the next run settles the question offline
and permanently.

**Consequence for planning: the effect of this ruling on recall is currently
unknown and must not be assumed.** `tc-frankincense-harvest` sits at rank 11 with
`gapAny −0.178` against `gapDoc −0.053`, so the chunk beating it is a sibling in
its own document — but whether that sibling is §29's English or §27–28's is
exactly what was never recorded. It may become a hit under this ruling. It may
not. **The next run answers it; nothing before then may claim it.**

---

## Ruling 3 — the gap is measured PRE-rerank, recall POST-rerank

G2's *"score gap wider than baseline, same pairs"* stays a statement about
embedding similarities, which is the quantity the baseline recorded and the
quantity the whole W2b distractor curve is denominated in. Reranking changes
ranks, not similarities; recomputing the gap on reranker scores would compare two
different quantities and call the comparison a gate.

- **gap** — computed on embedding similarities, before reranking, against the
  recorded baseline. Comparable by construction.
- **recall@6** — computed after reranking. That is the intervention's whole
  purpose.
- **reranker-score gap** — recorded under its own name, reported, and **never**
  compared to the baseline number.

Both halves are printed together, with one line saying which was measured where.
The failure this forecloses is G2 being assessed against two incompatible
readings of its own checklist.

---

## Ruling 4 — "wider than baseline" reads `gapDoc`

```
              57        151       450
gapDoc      +0.025    +0.023    +0.020
gapAny      -0.008    -0.009    -0.012
```

`gapDoc` — the target against the best chunk in any *other* document — is
positive at every rung, so "wider" is a claim that can be true or false.
`gapAny` is negative at every rung, **including at 57 chunks before any
distractor existed**; widening a negative number is satisfied by moving from
−0.012 to −0.005, which is not a gap and would let the gate pass on a
technicality.

`gapAny` is still recorded and still reported. It is a diagnostic, not the
criterion — and note that **ruling 2 changes it directly**, because the chunk
beating a `translation_case` target is the chunk that ruling now accepts.

---

---

## Ruling 5 — C2 returns to the critical path (2026-08-16)

**Ruling 3 has a consequence nobody stated when it was made.** It fixed the gap
to pre-rerank embedding similarities so the number stays comparable to B2's
baseline. That was right for comparability. It also means:

> A cross-encoder cannot move this number. Reranking reorders candidates; it does
> not alter cosine similarities. **C3 can satisfy G2's recall criterion and
> cannot touch its gap criterion, ever.**

Measured on the same 32 pairs that existed at B2:

```
B2 baseline,  57 chunks    gapDoc  +0.0249
today,        57 chunks    gapDoc  +0.0249     identical, two days later
today,       450 chunks    gapDoc  +0.0196
```

The gap at 450 is **narrower** than baseline. The criterion is not merely unmet;
it points the wrong way, and no amount of reranking will turn it round.

**Ruled: C2 comes back onto the critical path.** Hybrid lexical+dense is the only
planned intervention that changes what produces the score, so it is the only one
that can widen a pre-rerank gap. `claude/phase2-block-c-plan.md` demoted it to
*"optional, behind C3, only if still short"*; that demotion is withdrawn. Ruling
3 and G2 are otherwise unchanged.

**State the cost, as with ruling 1.** C2's own gotcha is unchanged and real:
`tsvector` will not tokenise Literary Chinese at all, so it needs character
n-grams and a per-script decision; and five of the six original misses were
English queries against non-English targets, where there is no shared vocabulary
for a lexical index to recover. **C2 may widen the gap while doing nothing for
recall.** That would still be a G2 criterion met — and it must be reported as
what it is, not as evidence that retrieval improved.

## Ruling 6 — the canary is a distractor, and the comment was wrong (2026-08-16)

`scripts/schema-b4-distractors.sql` said the containment canary *"carries NO
embedding … is invisible to both views … cannot perturb a ranking run. It is a
containment fixture, not a distractor."* It is inserted
`eligible_for_retrieval = true`, so `run_embed` embeds it; it has been one of the
450 since B4; and on 2026-08-16 it was the best competing document for
`tc-nabataean-epitaph`, moving that pair's gapDoc from +0.146 to +0.107.

**Ruled: it stays a distractor.** It is declared `is_distractor = true` and is one
of the 393 by design — a canary held back by eligibility would prove nothing
about the distractor flag, which is the whole reason it exists. The false comment
is struck in the schema and in `ingest/test_distractors.py`, whose docstring said
the same wrong thing while its own body recorded the truth.

No assertion was added, because the ones needed already existed: a vectorised
canary is INVISIBLE to `retrievable_chunks` and `citable_passages`, and VISIBLE
to `retrievable_chunks_with_distractors`. **Containment held throughout.** What
failed was the prose, and it failed in both directions at once —
`BLOCK_C_START.md` counted the canary among the 450 on the same day the schema
said it could not be there.

Effect on the gate: **none that changes a verdict.** Backing its influence out
entirely moves the 32-pair gapDoc from +0.0196 to roughly +0.0208, still short of
+0.0249, and `tc-nabataean-epitaph` is a hit at rank 2 either way. It is recorded
so it cannot be raised as an objection after the gate is assessed.

## The fifth item, which is a task and not a choice

**Add an English→Tamil cross-lingual probe** to `eval/gold/retrieval_probes.json`
with `lang_pool: non_english`. The four existing non-English-pool probes cover
Greek, Chinese and Parthian only. After ruling 1, the worst cross-lingual result
in the corpus — the Old Tamil link — rests entirely on an archived pair that no
longer counts toward the gate and was never designed to test cross-lingual reach
in the first place.

Cost: one query in the next batched embedding request. **Do it before C3**, so
the reranker is measured against a probe that exists rather than credited with
one that does not.

**Landed 2026-08-14** as `probe-tamil-akananuru-en` in both files — the probe in
`retrieval_probes.json` where cross-lingual probes live, and the pair in
`ranking_pairs.json` so it is actually measured. Query:

> *a Tamil poem describing Yavana ships arriving at Muciri with gold and
> departing with pepper*

Its partner `probe-tamil-akananuru` asks the same record in its own language and
ranks 1. This one asks in English against a pool with no English in it. It has
no rank yet; the next run gives it one, and the gate's arithmetic is restated
then rather than guessed at now.

---

## How the rulings are implemented, so the next reader does not have to infer it

- **The unit is declared, not inferred.** Each pair may carry `unit_id`; absent,
  a pair is its own unit. The loader asserts both directions — one unit means
  one query text, and pairs sharing a query text must share a unit. A unit
  inferred by grouping identical strings would change the gate's denominator the
  moment somebody edited a query by a character, with nothing to say so.
- **The alternate is computed, not copied.** A pair carrying
  `accept_aligned_translation` gets its alternate from `answer.align.pair_chunks`
  at scoring time, and only where that module reports the ground as `section`.
  Positional (`index`) alignment admits nothing: two texts numbered
  independently pair by coincidence of counting, and accepting on that would
  admit a *neighbouring* section, which this ruling says is still a miss. The
  ground is recorded per pair either way, because "none admitted" and "none
  asked for" are different facts about a run.
- **Nothing overwrites the baseline.** `rank`, both gaps and the cohort table
  keep their pre-Block-C meaning; `rank_accepted`, `recall_at_6_accepted` and
  the unit table sit beside them. Every run since B2 stays comparable, and the
  rulings can be re-argued against the same archive rather than only against
  runs made after them.

Seven mutations cover the above in `scripts/mutate_ranking.py` — 21 in total, up
from 14. Three of them break the gate's denominator specifically, because that
is the one quantity in the check that decides whether W3 starts, and the plan
itself already got that arithmetic wrong once.

---

## What travels with every G2 number, without exception

1. The curve was built on **English-only padding**. Seams 1 and 2 (Periplus,
   Strabo/Pliny/Ptolemy) were dropped on a time-box, so the twelve Greek-target
   pairs faced no competing Greek at any rung. A flat curve supports
   *"English-target retrieval survives an eightfold index of similar English
   competition"* and supports nothing about non-English retrieval at scale.
2. `gapAny` was negative before any padding existed. The quantity W2b was built
   to watch erode had no positive value to erode from.
3. The gate is reached over **29 units, not 32 pairs**, and the Old Tamil link at
   rank 309 is a standing failure the gate does not cover.
