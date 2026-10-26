# F7 HOST RUNBOOK — the ranking run F7 owes, and it cannot be made from the bridge

**54 documents, working tree clean, all eleven instruments green.**
`eval.run_ranking_check` needs Postgres at
`postgresql://mundus:mundus@localhost:5432/mundus`, which the bridge cannot
reach, so the seven F7 records are **not in the index at all** and no ranking
number in this repository yet knows they exist.

> **CORRECTED 2026-09-06, FINDING 90.** This document first read *"Tree:
> `50c19fe`"* and its abort table said *"`HEAD` is not `50c19fe` → the tree
> moved under the measurement"*. **Committing the runbook moved `HEAD` to
> `327bd2c` and tripped the runbook's own abort condition**, which is what the
> first reader hit. The abort table below is now written against WHAT THE INDEX
> IS A FUNCTION OF rather than against a commit hash, because a document that
> pins its own commit is stale the moment it exists. The original sentence is
> quoted here rather than deleted.

---

## Step 1 — session ritual, in PowerShell

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
docker compose up -d db
python scripts\check_db.py
```

Expected: `pgvector installed: True`.

## Step 2 — verify the tree before anything writes to the index

```powershell
git status --porcelain
git diff --name-only 865a3d3..HEAD
```

**`git status` must print nothing.** A ranking run over a dirty tree produces a
number that looks like a pass.

**`git diff --name-only` may list only documentation.** `865a3d3` is record 54 —
the last commit that changed the corpus. Everything after it is prose. What the
run is a function of is:

```
data/seed_corpus/          the records
data/corpus_tiers.json     the declared tiers
data/gazetteer.json        the cached places
ingest/                    the loader and the classifier
eval/gold/ranking_pairs.json   the pairs being scored
```

**If the diff names anything under those, stop.** If it names only `*.md` at the
repository root — and, from `50c19fe`, `eval/gold/answer_cases.json`, which is
the gold ANSWER set and is not read by `run_ranking_check` — the tree has not
moved in any sense the measurement can see. Proceed.

## Step 3 — the run, in this order and no other

```powershell
python -m ingest.run_ingest
python -m ingest.run_embed
python -m eval.run_ranking_check --with-distractors
```

**`--with-distractors` is not optional.** FINDING 77 exists because it was
omitted once. No `--fuse` (ruling 65), no `--collapse`, no `--rerank`, no
`--skip-check` — the baseline this is read against is
`20260906T103920+0000-retrievable_chunks_with_distractors.json`, the plain
`--with-distractors` arm at 544 chunks, and an arm that differs from it in a flag
is not a comparison.

**Expected index size: 556–566 chunks.** That band is pre-registered in
`F7_CURATION_START.md` as a sanity check, not a prediction. Outside it, something
is wrong with the loader rather than with the corpus.

Roughly 8 seconds for the run itself; `run_embed` will make embedding requests
for the new chunks and is the slow step.

## Step 4 — the mutation harnesses, host-only (FINDING 59)

```powershell
python scripts\mutate_fidelity.py
python scripts\mutate_cost.py
```

Expected `70/70` and `58/58`, sources restored. **If either is interrupted, check
`git status --porcelain` before doing anything else** — a mutation source left
modified is a live mutation in the working tree. From PowerShell,
`git checkout -- <path>` is safe; from the bridge it is not.

## Step 5 — hand it back

The run archives itself to
`eval\ranking_runs\20260906T…-retrievable_chunks_with_distractors.json`. The
folder is connected, so **say "the run is done"** and I will read the JSON and
diff it against the baseline.

---

## What it is being read against — RULING 79, all five written before the records existed

```
P1  cefu-yuangui-fulin-glass (rank 4) falls again, with chunks of
    eastasia-09-jiutangshu-fulin in its beaten_by.
    REFUTED BY: it holds at 4 or improves; or it falls with no eastasia-09 chunk
    in the window.

P2  au-oc-eo-medallion (rank 1) LEAVES rank 1, with chunks of
    seasia-09-oc-eo-unesco in its beaten_by.
    REFUTED BY: it holds at 1 with an empty beaten_by, as au-ezana-titles did.

P3  no beaten_by list in the run contains a chunk of persia-07-met-ewer-anahita
    except where the target is persia-04-bronze-heracles.
    REFUTED BY: it appears against any other target, or against none.

P4  at most two of F7's five catalogue_record chunks appear in any beaten_by
    list, and both published_translation_only records appear in at least one.
    REFUTED BY: three or more catalogue records appear, or either prose record
    appears in none.

P5  ALL recall@6 falls from 0.6818 (30/44) and NO gold pair improves.
    REFUTED BY: any pair improving — the first improvement Block F has ever seen
    from adding a record.
```

**Expect the headline to fall.** FINDING 84: every record-adding run in Block F
has been monotone worse — 0 better / 9, then 0 better / 14 — and the only run
with improvements is the one where 393 distractors left the index. A falling
`recall@6` is the mechanical consequence of curating, and it is being said here
before the run rather than explained after it.

---

## ABORT — do not run if any of these is true

| observed | why it aborts |
| --- | --- |
| `HEAD` is not `50c19fe` | the tree moved under the measurement |
| `git status` shows any tracked file changed | same |
| `check_db.py` does not print `pgvector installed: True` | the index is not the index |
| the run errors partway | a half-run is not a run |
