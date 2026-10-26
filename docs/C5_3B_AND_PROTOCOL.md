# C5 — 3b measured, the noise floor, and two things to fix before the run

_2026-08-17. Every figure recomputed at full precision from the archived run JSON
in `eval/ranking_runs/`. No harness change, no calls, nothing on the ranking path
touched. Ruled 3b by the project owner on 2026-08-17; sequencing trap ruled
**after C6**._

---

## 1. Decision 3b — the gap on the pairs B2 actually measured

```
                                       run                            n   gapDoc      gapAny
B2 baseline, 57 chunks                 20260814T084042               32   +0.024927   -0.008360
W2b 450-chunk rung, same pairs         20260814T133556               32   +0.019586   -0.012406
frozen config, 450 chunks, same pairs  20260817T080300 single-arm    32   +0.019622   -0.012452
frozen config, 450 chunks, all pairs   20260817T080300 single-arm    33   +0.016047   -0.015056
```

The pair sets differ by exactly one member, and it is the one `C2_RESULT.md`
named:

```
in C2's 33 and not in B2's 32     probe-tamil-akananuru-en
in B2's 32 and not in C2's 33     none
its gapDoc                        -0.098380   (rank 4)
its effect on the mean            -0.003575   (+0.019622 -> +0.016047)
```

**`C2_RESULT.md`'s reconstruction was right to four decimals: +0.0196 is
+0.019622.** The slide from W2b's recorded +0.020 is the denominator changing,
confirmed rather than inferred — the 450-chunk rung on B2's own pair set reads
+0.019586, and W2b's `+0.020` is that number rounded.

### The criterion is still unmet, on its own wording

```
G2 asks     450-chunk gapDoc, same pairs   >   B2 baseline
measured                        +0.019622  <  +0.024927
short by                        0.005305      = 21.3% of the baseline
```

3b does not rescue G2 and was not expected to. What it changes is what gets
written down: the failure is now recorded against the arithmetic the criterion
specifies, not against a denominator that changed on 2026-08-14 after the
baseline was set. **That is the whole value of 3b and it has been collected.**

---

## 2. The noise floor — measured, and pre-declared before C5 fires

`C5_START.md` says *"a material disagreement between the two days IS the
finding"* and does not define material. Defining it after seeing C6 would be
decision 3c's error in miniature. It can be defined now, because the archive
already holds the frozen configuration run on two calendar days.

```
08-16 16:25  ->  08-17 08:03     same view, same 33 pairs, same everything below

gapDoc, 33 pairs           +0.016011 -> +0.016047      d = +0.000036
gapAny, 33 pairs           -0.015012 -> -0.015056      d = -0.000044
recall@6 per unit  pre/collapsed/reranked   27 / 28 / 29    unchanged
recall@6 via the original text              21             unchanged
MRR@10 per unit    pre 0.72611 -> 0.72611 ; reranked 0.84139 -> 0.84198
per-pair sim_target        all 33 moved ; max |d| = 0.00222
pre-rerank rank changes    4 pairs, each by exactly one place
post-rerank rank changes   1 pair   adulis-exports  8 -> 7
```

**These two runs are NOT a valid C5–C6 pair** and must never be presented as
one: `eval/run_ranking_check.py` was rewritten between them (3,557 lines against
HEAD). They bound the noise; they do not satisfy criterion 5.

### Where the drift comes from, since it is not float noise

The index is identical between the two runs — 450 chunks, `collapse_stats`
`{in 450, out 426, removed 24, promoted 425}`, the same `chunk_id_drift` entry,
`voyage/voyage-3.5` on both sides. Yet **all 33 `sim_target` and all 33
`sim_best_other_doc` moved.** Stored chunk vectors cannot have moved, and a
changed query vector moves both quantities at once.

**`voyage-3.5` does not return a bit-identical vector for identical text across
calls.** That is the mechanism, it is one query embedding per pair per run, and
it sets the floor for everything C5–C6 can claim.

### Declared now, for C5 vs C6

```
MATERIAL, stop and record         any change in a gated integer -
                                  recall@6 per unit at any stage, or
                                  recall@6 via the original text
                                  Expected: none.

MATERIAL                          |d gapDoc| over 33 pairs > 0.0005
                                  = 14x the observed day-to-day drift,
                                    and under 1/10 of the deficit to baseline
                                  Expected: < 0.0001.

NOT MATERIAL, do not re-run       per-pair rank movement of <=2 places for
                                  any pair ranked outside the top 6
                                  per-pair |d sim| up to 0.003

NOT A DISAGREEMENT - a
CONFIGURATION CHANGE, abort       any change in index_chunks, collapse_stats,
                                  chunk_id_drift, embedding model, rerank
                                  model / window / route
```

---

## 3. Hazard 1 — the ranking path C5 will run is uncommitted

```
HEAD                     695a06b  2026-08-16 17:26  "Block C: rulings 7-11, ..."

modified, tracked        eval/run_ranking_check.py    3557 lines vs HEAD
                         eval/test_ranking_check.py
                         answer/translate.py
                         scripts/mutate_ranking.py
                         gateway/config.yaml
                         PROGRESS.md
untracked, on the path   retrieve/render.py
                         retrieve/fuse.py
                         eval/gold/query_renderings.json
```

`C5_START.md` requires that **no code on the ranking path moves between the two
days**. The code that produced the 08:03 run exists only as uncommitted
working-tree state. Nothing can currently prove the two days ran the same tree,
and nothing would say so if they did not: an editor autosave, a stash, a partial
revert, a `git checkout` of one file between C5 and C6 destroys criterion 5
**silently**, on a repository that has twice this month produced a green result
about a fiction.

**Fix before C5: commit.** A commit changes no file content, so it is not a
change on the ranking path — it is the only thing that makes the two days
provably one configuration. Record the commit hash beside both run records, the
way the renderings digest is recorded. `C2_RESULT.md` already intends this:
*"the renderings, the guard and the fusion stay in the repository as a measured
negative result."*

---

## 4. Hazard 2 — an archived run reports an index it did not search

```
20260814T144005   view retrievable_chunks                    index_chunks   57
20260814T144013   view retrievable_chunks_with_distractors   index_chunks  450

differences across 33 pairs on sim_target, sim_best_other_doc,
sim_best_other_chunk, rank and top_doc                                       0
```

Adding 393 distractors changed nothing whatsoever. It cannot have been searched.
The distractors were reachable earlier the same day — the 13:35 run on the same
view moved gapDoc from +0.024927 to +0.019586 and changed `sim_best_other_doc`
on 4 of 32 pairs.

`check_search_reaches_the_view`, which asserts `n_hits == n_index` and refuses
otherwise, landed in **bb3bef5 on 2026-08-16 — after this run.** So the guard
already covers C5 and C6, and this is an archival caveat rather than a live
defect. What travels with it:

- **`20260814T144013` must never be cited as a 450-chunk measurement.** Nothing
  in `C5_START.md` does; W2b's 450 rung is the 13:35 run, which is what 3b uses.
- **`index_chunks` records the view's row count, not what the search reached.**
  The number in a run header is not self-validating; the guard is what validates
  it, and it must stay on. `--skip-check` is already refused by the frozen
  configuration for exactly this reason.

---

## 5. The C5 protocol

### Before the run

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
# .env into the environment, docker compose up -d db, litellm in a separate window

git add -A ; git commit -m "Block C: C2 measured and rejected, rulings 12-24"
git rev-parse --short HEAD          # record this beside C5 and C6

python -m ingest.run_embed --stats  # 450 eligible / 450 embedded / 0 pending
python -m eval.test_ranking_check   # 209
python scripts\mutate_ranking.py    # 86
```

The embed check is not ceremony — hazard 2 is what a run looks like when it is
skipped.

### The run

```powershell
python -m eval.run_ranking_check --with-distractors --collapse --rerank --rerank-tpm 2000000
```

No `--fuse`. No `--skip-check`. Nothing else.

### What C5 must reproduce, from the 08:03 single-variant arm

```
recall@6 per unit    pre 27/30 0.900  ->  collapsed 28/30 0.933  ->  reranked 29/30 0.967
MRR@10 per unit          0.72611      ->      0.83056            ->      0.84198
recall@6 via the original text            21/30 = 0.700
gapDoc / gapAny (33 pairs, pre-rerank)    +0.016047 / -0.015056
gapDoc / gapAny (B2's 32 pairs)           +0.019622 / -0.012452
coverage                                  28/33 targets, 29 post-rerank
cohort recall   archived_answer 4/8   authored 8/9   retrieval_probe 12/12   translation_case 3/4
rerank                                    ~30 requests, ~310K tokens
```

Judge disagreement against section 2's thresholds, which were written before the
run.

### C6

The same command on a different calendar day. Between the two: no commit, no
edit, no re-embed, no gateway change, no gold-set change. The sequencing-trap fix
happens **after C6**, as ruled.

---

## 6. Ruling 25 — RULED 3a. G2's gap criterion has failed

**Ruled by the project owner, 2026-08-17, on the corrected number.** 3b was
collected first, as its own wording requires, and the criterion fails on it:

```
G2, gap criterion, on the pairs the baseline measured
    450-chunk gapDoc   +0.019622     B2 baseline   +0.024927     FAILED
    short by 0.005305 = 21.3% of the baseline
```

**Kill trigger 1 is pulled. W3 does not start.** The sourcebook is polished at
24–60 records rather than chased to 200, exactly as `PHASE2_PLAN` pre-declared
before any of this was measured.

What this ruling costs, stated so it is not discovered later: W3 does not
happen, and `recall@6 via the original text` stays at 21/30 with no intervention
left aimed at it — ruling 5 settled that no reranker moves the gap, and C2, the
only remaining candidate, was measured on 2026-08-17 and rejected.

**C5 and C6 still run.** They take G2 from five of seven to six of seven and
isolate the failure to exactly one criterion. That is worth having even though
the verdict is now settled: a criterion that failed with one other criterion
still unmeasured is a weaker record than one that failed alone.

### Both readings travel together, permanently

```
gapDoc, all 33 pairs, 450 chunks     +0.016047     the run prints this
gapDoc, B2's 32 pairs, 450 chunks    +0.019622     the criterion asks for this
B2 baseline, 32 pairs, 57 chunks     +0.024927
```

Neither number may be published without the other, and neither without the index
size beside it.

### 3c was not taken, and the argument for it is recorded rather than used

3b strengthened the *measurability* half of a 3c case: the 450-chunk rung on
B2's pairs read +0.019586 on 2026-08-14 and +0.019622 on 2026-08-17, agreeing to
four decimals across three days and a harness rewrite, so a like-for-like
criterion would be a stable quantity. It strengthened the *legitimacy* half not
at all. **Changing a gate after seeing the number it failed remains the most
dangerous move available, and it was not made.** Anyone reopening this must
argue from the W2b curve's shape, which was recorded before any of this, and
must keep the reading above beside the new one.

---

## 7. Superseded — the 3a / 3c question as it stood before the ruling

3b is collected. The corrected number is **+0.019622 against +0.024927** and it
fails.

- **3a — declare the gap criterion failed, pull kill trigger 1.** The recorded
  reading is now the one the criterion asks for. W3 does not start; the
  sourcebook is polished at 24–60 records.
- **3c — rule the criterion unmeetable and replace it with a like-for-like
  comparison.** 3b strengthened the *measurability* half of this argument: the
  450-chunk rung on B2's pairs read +0.019586 on 08-14 and +0.019622 on 08-17,
  agreeing to four decimals across three days and a harness rewrite, so a
  450-against-450 criterion would be a stable quantity. It does not strengthen
  the *legitimacy* half at all. Changing a gate after seeing the number it
  failed is still the most dangerous move available.

C5 and C6 do not depend on this decision and should not wait for it. Both
readings — +0.016047 over 33 pairs and +0.019622 over B2's 32 — are recorded
above and travel together permanently, whichever way it goes.
