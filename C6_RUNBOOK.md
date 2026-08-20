# C6 — runbook for 2026-08-20

_The last run of Block C. Same command as C5, different calendar day. Nothing in
the repository has moved since C5 and nothing may move before C6 fires._

---

## Step 1 — session ritual

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
docker compose up -d db
```

Then, **in a separate window**:

```powershell
litellm --config gateway/config.yaml --port 4000
```

## Step 2 — verify, immediately before the run

```powershell
git rev-parse --short HEAD
git status --porcelain
python -m ingest.run_embed --stats
```

Expected, exactly:

```
bff0605

?? eval/ranking_runs/20260819T102211+0000-retrievable_chunks_with_distractors-collapsed-reranked50.json

{ "eligible": 450, "embedded": 450, "pending": 0, "embedded_but_ineligible": 0,
  "by_model": { "voyage/voyage-3.5": 450 } }
```

**The suites are optional and can be skipped for speed.** `test_ranking_check`
(209) and `mutate_ranking.py` (86) passed at C5 against this exact tree, and the
commit hash is stronger evidence of code identity than re-running them. Run them
only if step 2 surprises you.

## Step 3 — C6

```powershell
python -m eval.run_ranking_check --with-distractors --collapse --rerank --rerank-tpm 2000000
```

No `--fuse`. No `--skip-check`. Nothing else. ~30 rerank requests, ~310K tokens.

**Expect ~90 seconds.** Measured, not estimated — wall clock from each run's own
`timestamp` to the moment it wrote its archive:

```
20260816 16:02   --collapse --rerank   30 req   89.8s
20260816 16:12   --collapse --rerank   30 req   92.8s
20260816 16:25   --collapse --rerank   30 req   92.4s
20260819 10:22   C5                    30 req   90.2s
```

For scale: the same run without `--rerank` is ~8s, so the cross-encoder is
essentially all of it, at ~2.7s per request. The 08-17 fused run took 205s
because it reranked both arms.

**If it is still going after five minutes, you left off `--rerank-tpm 2000000`.**
Two archived runs took **27 minutes** — 1,643s and 1,641s — of which 1,553s was
rate-limit pacing against the default token budget. That is what the flag is for.

**Do not kill it if that happens.** The tpm budget is pacing only; it cannot move
a rank or a score, it is not in the abort list, and the run is fully valid when
it finishes. A half-run is not a day. Let it finish and note the wall clock.

## Step 4 — hand it over

The run archives itself to `eval\ranking_runs\20260820T…-collapsed-reranked50.json`.
The folder is connected, so **you can simply say "C6 is done"** and I will read
the JSON and diff it. Pasting the console output also works but is not needed.

---

## ABORT — do not run C6 if any of these is true

| observed | why it aborts |
| --- | --- |
| `HEAD` is not `bff0605` | the tree moved; C5 and C6 are two configurations |
| `git status` shows anything but the untracked run JSON | a tracked file changed |
| embed stats is not `450 / 450 / 0 pending` | the index moved under the measurement |
| litellm will not start, or the run errors partway | a half-run is not a day |

In any of those cases stop and tell me what you saw. A C6 fired over a changed
tree is worse than no C6 at all — it produces a number that looks like a pass.

---

## What C6 is judged against

All of this was declared **before C5 ran** and is not retuned.

```
GATED - any change at all is material, and none is expected
  recall@6 per unit    pre 27/30    collapsed 28/30    reranked 29/30
  recall@6 via the original text    21/30
  coverage             pre 28   collapsed 30   reranked 29
  per-pair recall@6 flips at any stage                  none

TOLERANCED
  gapDoc, 33 pairs        C5 = +0.015947      material if |d| > 0.0005
  gapDoc, B2's 32 pairs   C5 = +0.019535      material if |d| > 0.0005
  gapAny, 33 pairs        C5 = -0.015152      material if |d| > 0.0005
  max per-pair |d gapDoc|                     material if > 0.003
  rank movement <=2 places outside the top 6  NOT material, do not re-run

ABORT, not a disagreement
  any change in index_chunks, collapse_stats, chunk_id_drift,
  embedding model, rerank model / window / route
```

### The free experiment C6 also settles

`probe-greek-muziris` `sim_target` was byte-identical across seven runs and three
days, then changed at 2026-08-17 and again at C5. C6 needs no code change to
answer it — the value is already archived on the pair:

```
C5 08-19    0.63903526300402180
C6          reproduces it exactly  ->  the 08-17 break was a one-off
            differs again          ->  the query embedding is now non-deterministic,
                                       and every future comparison in this repo
                                       carries a 1e-4 floor that must be written down
```

Either answer is a result. Neither changes C6's verdict, which rests on the
table above.

---

## After C6 passes

1. **G2 goes to six of seven.** Criterion 5 — *≥2 sessions on different days* —
   is met. The gap is the sole remaining failure, already ruled failed by
   ruling 25 with kill trigger 1 pulled.
2. **Then, and only then, the sequencing-trap fix**: `recall@6 via the original
   text` is computed pre-rerank while the adopted configuration reranks. Safe
   the moment C6 is archived; must land before 21/30 leaves `PROGRESS.md`.
3. **Commit both run JSONs**, write up `PROGRESS.md`, close Block C, and move to
   the sourcebook at 24–60 records.
