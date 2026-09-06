# Startup — every session

The README's quickstart is *first-time setup* (create the venv, copy `.env`).
This is the daily ritual. Nothing here installs anything.

**Two PowerShell windows.** Both need `cd` + venv activate + `.env` load. This is
not optional and not cached: PowerShell does not read `.env`, and the gateway
reads keys **only at startup** — so if you change a key, restart the gateway.

Project root:

```
C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior
```

---

## The block to paste into every new window

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
```

Check it took:

```powershell
$env:APP_DATABASE_URL          # postgresql://mundus:mundus@localhost:5432/mundus
$env:ANTHROPIC_API_KEY.Length  # non-zero
```

`APP_DATABASE_URL`, **not** `DATABASE_URL` — LiteLLM reserves the latter for its
own Prisma database, and setting it sends the gateway looking for a schema that
isn't there.

---

## Window 1 — database + gateway

```powershell
# Docker Desktop must be running first.
docker compose up -d db
python scripts\check_db.py          # expects: pgvector installed: True

litellm --config gateway/config.yaml --port 4000   # leave this running
```

The container has `restart: unless-stopped`, so it usually comes back on its own
after a reboot. `check_db.py` is the cheapest way to find out whether it did —
run it before anything else, because a dead database produces a full successful-
looking report followed by a traceback.

Gateway routes: chat → `anthropic/claude-haiku-4-5-20251001`, embed →
`voyage/voyage-3.5` (1024-dim). Health check from window 2:

```powershell
curl http://localhost:4000/health/readiness
```

---

## Window 2 — work

Paste the startup block again (new window, new environment), then:

```powershell
# offline — no network, no database, costs nothing
python scripts\state_block.py                # RUNS the eleven and prints the table
python -m ingest.verify --state              # prints the corpus state block
python -m answer.test_translate              # prints per-check lines, NO total
python scripts\mutate_part7b.py              # 13 mutations, restores sources
python scripts\mutate_recover.py             # 11 mutations, restores sources

# state of the corpus — database only, no API calls
python -m ingest.run_ingest --stats
python -m ingest.run_embed --stats
python -m answer.run_answer --stats
```

**THE EXPECTED NUMBERS ARE NOT WRITTEN HERE ANY MORE, AND THAT IS THE POINT.**
`scripts\state_block.py` runs the eleven instruments and prints their counts;
`ingest.verify --state` prints the corpus state block. Read the numbers off
those, and compare them with the last result document's pasted block. **Do not
add a figure to this file.**

`answer.test_translate` is the one suite that prints no total of its own, so
`state_block.py` does not carry it. It passes or it says so.

**Then compare `run_ingest --stats` and `run_embed --stats` against
`ingest.verify`, which counts the corpus ON DISK.** The database is a copy of
the corpus and the two drift whenever records are curated on a machine that is
not running the database. **A difference here is the ingest you have not run
yet, not a defect** — which is the opposite of what this section used to say.

*CORRECTED 2026-09-06, F6, and this is the fourth instance of FINDING 75 in one
day. This section read:*

> *`python -m answer.test_answer  # 133 assertions`,
> `python -m answer.test_translate  # 104 assertions`,
> `python scripts\test_recover_baseline.py  # 44 assertions`,
> `python -m ingest.run_ingest --stats  # expect 24 docs, 56 chunks`,
> `python -m ingest.run_embed --stats  # expect eligible 54, embedded 54,
> pending 0`* — *and then:* **Expected state, confirmed on the host 2026-08-12
> (Phase 2 Block 0): 24 documents → 56 chunks → 54 eligible → 54 embedded with
> `voyage/voyage-3.5`. If those numbers differ, stop and find out why before
> running anything that writes.**

*Every one of those five figures was stale. Measured on the bridge on
2026-09-06: `answer.test_answer` **150**, `scripts\test_recover_baseline.py`
**56**, and the corpus **43 documents → 133 chunks**. `answer.test_translate`
prints no total at all, so its 104 could never have been checked by reading its
output.*

***AND THE STALE FIGURES CARRIED AN INSTRUCTION TO STOP.*** *A session
following this file after Block D would run `run_ingest --stats`, see a number
other than 24, and be told by this document to halt before running anything
that writes — for the ordinary and expected reason that F3 to F6 added
nineteen records. The daily ritual is the one document a new session actually
follows, and it had been telling them to stop since Block D.*

> *An older correction, kept: this file previously said 57 chunks / 55 embedded.
> It was wrong — written at a corpus state that no longer existed and never
> revised, while `README.md` and `PHASE2.md` both carried the correct figure.
> Corrected in Block 0. The distractor curve in W2b is denominated in chunk
> counts, so this mattered.* **Corrected in Block 0 by writing a different
> frozen number, which went stale in eighteen days. F6 removes the number
> instead.**

---

## Where Phase 2 picks up

Phase 1 closed 2026-08-12 with **persevere**. The plan is `PHASE2.md`; the
argument behind it is the closing summary at the foot of `PROGRESS.md`.

**Two workstreams start in parallel, and neither spends an API call.**

### W1 — Geography (no network, no database)

Add `findspot_places` and `subject_places` to the seed records, each entry
carrying a Pleiades id and a `ground` of `stated` / `identified` / `regional`.
17 of 24 records already have a named findspot; the 7 that do not are literary
and carry the richer *subject* geography instead.

```powershell
python -m ingest.verify               # after any seed edit, always
python ui\build_ui_data.py            # regenerate the bundle
node ui\check_ui.mjs                  # 11 checks over all archived runs
```

**Never author a coordinate.** Coordinates are read from Pleiades via the id and
cached in `data/gazetteer.json`. A coordinate without an id is a bug and the
build script should fail on one.

### W2a — Measure ranking before changing it

There is currently **no ranking metric at all**. The 11/11 probe result tests
whether the right chunk is in the corpus, not whether it is ranked — with 54
chunks nearly everything relevant is retrieved.

Build ≥20 question → known-good-chunk pairs, record recall@6, MRR@10 and the
score gap between the known-good chunk and the best irrelevant one, **and record
the baseline before touching anything.** Then the distractor experiment: pad the
index to 150 and 450 chunks with flagged, known-irrelevant material and plot how
rank degrades. That predicts the 200-document behaviour without curating 200
documents.

**Do not skip W2a once a promising reranker is in hand.** That is the whole
reason it is written down as a separate step.

### The number that set this order

Mean top-1 to rank-6 similarity spread across 77 archived runs: **0.105**. The
Adulis export answer arrived at **rank 3, 0.012 below top-1**. At 450 chunks it
lands near rank 20 and never reaches the model. **W3 does not start until W2's
gate passes.**

---

## Costs, so a run is never a surprise

| Action | Spend |
| --- | --- |
| Every offline suite above | nothing |
| Every `--stats` | nothing (database only) |
| `recover_answer_baseline.py` | nothing (database only) |
| `ui\build_ui_data.py` and `check_ui.mjs` | nothing (files only) |
| All of W1 geography | nothing |
| `run_answer --dry-run "..."` | 1 embedding request |
| `run_answer "..."` | 1 embedding + 1 chat call |
| `run_translation_check` per case | 2 chat calls, **cannot be batched** |
| `run_answer_sweep --repeat 3` (5 cases) | 5 embeddings + 15 chat calls |
| W4 sweep at 30 cases × 3 reps × 3 days | ~30 embeddings + **~270 chat calls** |

**Voyage free tier is 3 requests/minute.** Batch aggressively — the full
embedding pass is 2 requests and the cross-lingual check is 1. Anthropic chat is
a different tier, so translation and answer calls do not compete with embeddings.

---

## When something looks wrong

- **"cannot reach the LiteLLM gateway"** — check it is actually a socket
  failure. LiteLLM wraps upstream provider errors as `APIConnectionError`, and a
  Voyage rate limit once got reported as a dead gateway while the gateway was
  fine. Rate limits are now tested first, but read the message.
- **A run that appears to hang** — `EMBED_TIMEOUT` defaults to 60s and the
  backfill prints a line per batch. Silence means the gateway, not the model.
- **`AmbiguousParameter` on a NULL parameter** — a cast is missing. Parse-level
  checks cannot catch it; only execution against real Postgres can.
- **Numbers that moved with no change** — check `eval/runs/` and
  `eval/answer_runs/`, not the `_last_run.json` files. Those hold the most recent
  invocation only, which is how a one-case run once replaced a nine-case
  baseline.

---

## Ground truth lives in

- `PHASE2.md` — what to do next, and the gate each workstream must pass.
- `PROGRESS.md` — every defect and why it mattered. **Do not read it linearly**
  (3,300 lines); read the closing summary at the foot and grep for the rest.
  `PHASE2.md` opens with the greps that matter.
- `README.md` — the module map, if you need to find where something lives.
- `eval/gold/` — probes, confidence profiles, translation and answer cases, floor.
- `eval/runs/`, `eval/answer_runs/`, `eval/sweeps/` — archived runs, never
  overwritten. **Calibrate from these, never from a `_last_run.json`.**
