# C7 — the commit, the sequencing fix, and Block C closed (2026-08-20)

_`C7_START.md`'s three tasks are done. Every number below came from a run on the
host or from a replay of an archived run through the patched code._

---

## TASK 1 — committed as `744e57c`

Seven files, `git add` by named path rather than `-A`:

```
eval/ranking_runs/20260819T102211+0000-…-collapsed-reranked50.json   C5
eval/ranking_runs/20260820T151200+0000-…-collapsed-reranked50.json   C6
C5_3B_AND_PROTOCOL.md  C5_RESULT.md  C6_RUNBOOK.md  C6_RESULT.md  C7_START.md
```

The two run JSONs are the evidence for G2 criterion 5. The four session
documents previously lived only in the Claude project and are now in the
repository beside `C2_RESULT.md`.

---

## TASK 2 — the sequencing trap is fixed, and the answer is 22/30

`recall@6 via the original text` was computed PRE-rerank, in `apply_collapse`,
while the adopted configuration reranks.

### The target was computed before the code was written

Replayed from C6's archive, so the fix had a number it had to hit:

```
via-original, PRE-rerank    21/30 = 0.700
via-original, POST-rerank   22/30 = 0.733

unit                  entry role   primary role   coll rank   rr rank   changes?
au-khao-sam-kaeo      None         translation       15          1      NO -> YES
aksum-trade-adulis    translation  original          10          2      no, and must not
adulis-exports        translation  original           3          7      no, and must not
```

`aksum-trade-adulis` is rescued from 35 to 2 and still does not count. **23/30
means the primary-role clause was dropped; 21/30 means the fix did not take
effect.**

### The shape

`PairResult.recall_at_6_via_original_reranked` is a NEW field under a NEW name,
exactly as `rank_reranked` never overwrote `rank`. Same predicate, post-rerank
recall column. `apply_rerank` gained no entry-role logic, because the collapse
runs BEFORE the rerank and emits one row per section — the reranker cannot
change which member surfaced first. `UnitResult` and the aggregate gained the
same field; the report prints both lines, labelled with their measurement point.

### Ruling 26 — the two via-original keys are emitted from the COLLAPSE block

The entry role the predicate reads is a fact the collapse produces. A run with
`--rerank` and no `--collapse` has no entry role for the bypass clause to fire
on, so the post-rerank figure would equal post-rerank recall — 29/30 published
under a name that says something else.

```
uncollapsed run              NEITHER figure is reported
collapsed, not reranked      the pre-rerank figure alone
collapsed and reranked       both, side by side and labelled
```

### The run confirms it, and the change is provably additive

`20260820T161457+0000-…-collapsed-reranked50.json`. **Not a third day and must
never be cited as one** — same calendar day as C6, changed tree. Diffed field by
field against C6:

```
config fields on the abort list                    0 differ
pairs differing on ANY pre-existing field          0 of 33
unit-aggregate fields moved                        NONE of the 24
keys added                recall_at_6_via_original_reranked, ..._n
keys removed              none
```

### The mutation harness caught a guard of C7's own that nothing was watching

The first C7 run reported one MISS as possible list drift. It was not drift.
**Dropping `and collapse_primary_role == "original"` makes the predicate
STRICTER**, removing ruling 11's exemption, so the guard that fails is *"a
rescued record with NO source text does count as via-original"* — not the
English-bypass guard it was filed under. Re-pointing it showed the English-bypass
guard had no mutation at all: a predicate with two clauses needs two mutations.
A fifth was added.

```
python -m eval.test_ranking_check      218 assertions   (209 at the start)
python scripts\mutate_ranking.py        91 mutations    (86 at the start)
```

All five C7 mutations were verified on a shadow copy of the tree before the host
run, because `mutate_ranking.py` writes to its sources and its own note forbids
running it over a network mount.

---

## TASK 3 — `PROGRESS.md` written, Block C closed

**557,037 → 580,817 bytes, 10,614 → 11,086 lines, 56 → 60 sections.** Four
sections appended:

1. Decision 3b and ruling 25, with the two archive hazards (the ranking path
   uncommitted for two days until `bff0605`; `20260814T144013` reporting
   `index_chunks=450` and not searching it).
2. C5 and C6 — byte-identical over one provably identical tree, the withdrawn
   determinism claim, and the embedding-régime note.
3. The sequencing trap, ruling 26, the additivity proof, the mutation finding.
4. Block C closes.

Committed as `ccca17e`, five paths: the three sources, `PROGRESS.md`, and the
verification run.

### G2 — six of seven

```
[x] ranking metric over >=20 pairs, baseline recorded before any change    B2
[x] distractor curve to >=450, shape stated and reproducible               W2b
[x] top 6 for >=95% at 450                       29/30 = 0.967
[ ] score gap wider than baseline                +0.019535 vs +0.024927    FAILED, ruling 25
[x] measured across >=2 sessions on different days    C5 08-19 / C6 08-20
[x] cite.py third match state, mutation-verified                           C1a
[x] translation_chunk* rename                                              C1b
```

Kill trigger 1 is pulled. W3 does not start.

---

## Carried forward

**The embedding-régime note.** Within a régime comparisons are EXACT; across a
régime the aggregate gapDoc floor is ~1e-4 and the per-pair floor ~2e-3. B2's
baseline is in the old régime and C5–C6 in the new one, so the gap comparison
spans a boundary — 1.6% of a 0.005392 deficit, too small to matter, but it
belongs beside any comparison against a pre-08-17 figure.

**Both gap readings travel together, always with the index size:** +0.015947
over all 33 pairs, +0.019535 over B2's 32, against +0.024927 at 57 chunks.

**The sentence that travels with all of it.** 29/30 is whether the RECORD was
found; 22/30 is whether the NON-ENGLISH TEXT was reachable. The second moved by
one unit because the measurement point was corrected, not because retrieval
improved — `au-khao-sam-kaeo` was always rescued and the harness was always
reading the wrong column. `muziris-cargo-akananuru` still sits at rank 310, the
corpus's one genuinely broken cross-lingual link, not counted toward the gate.
The W2b curve still rests on English-only padding.

**C5 and C6 measured a stable pipeline. They did not measure a solved problem.**

---

## Next

`BLOCK_D_START.md`. Block D then Block E — the W4 cases and the three-day sweep,
in the window while retrieval and the corpus are frozen. Block F, the sourcebook
at 24–60 records, is second and not cancelled.
