# Block C — starting point for the next thread

_Written 2026-08-14 at the close of Block B. Everything here was measured, not
recalled; where a number is inherited from a document rather than a run, it says
so._

## Read these, in this order

| # | file | why |
| --- | --- | --- |
| 1 | **this file** | state, open rulings, traps |
| 2 | `PHASE2_PLAN.md` § *Block C* | the runbook's C1–C6 and the **G2 checklist** |
| 3 | project doc `claude/phase2-block-c-plan.md` | Block C planned against B5's evidence — including why a perfect reranker cannot reach G2 |
| 4 | `PROGRESS.md` — **the last ~8 sections only** | Block B's findings. The file is ~400 KB; do not read it whole |
| 5 | `eval/gold/ranking_pairs.json` | the 32 gold pairs; every `note` explains why that pair exists |
| 6 | `eval/ranking_runs/20260814T084042+0000-*.json` | the 57-chunk baseline, full depth. **This is the baseline G2 compares against** |

**Do not trust `PHASE2_PLAN.md`'s numbers.** Its Action #1 says the corpus is 54
chunks; it is 57, and has been since A4. `STARTUP.md` has been wrong before too.
Read counts from the database, never from a document.

## State, as measured 2026-08-14

```
corpus        24 documents / 59 chunks / 57 retrieval-eligible
index         450 chunks in retrievable_chunks_with_distractors
              = 57 corpus + 393 distractors (one of which is the canary)
              retrievable_chunks itself sees 57 — distractors are excluded
distractors   600 fetched on disk, 393 loaded; Met 200 + Cleveland 400
gold set      32 ranking pairs, 7 regions, 8 target languages
```

Green suites:

```
python -m eval.test_ranking_check     35 assertions
python scripts\mutate_ranking.py      14 mutations
python -m ingest.test_distractors     16 assertions
python scripts\mutate_distractors.py   6 mutations
```

## The W2b curve — Block B's deliverable

```
index          57        151       450
recall@6      0.812     0.812     0.812
MRR@10        0.651     0.648     0.648
gapDoc       +0.025    +0.023    +0.020
gapAny       -0.008    -0.009    -0.012
spread        0.146     0.141     0.136
```

**Flat.** No degradation over an eightfold index. Two caveats that must travel
with that sentence:

1. The padding is **English catalogue prose only** — seams 1 and 2 (Periplus,
   Strabo/Pliny/Ptolemy) were dropped on a time-box. The twelve Greek-target
   pairs faced no competing Greek at any rung, so their stability is **not**
   evidence of robustness.
2. `gapAny` is **negative at every rung**. Averaged over the gold set, the
   known-good passage scores slightly worse than the best competing passage —
   and it did so at 57 chunks, before any padding existed.

## Four rulings, all free, all blocking

These are decisions, not code. Block C's critical path runs through them.

1. **Is a multi-target query N pairs or one pair with N acceptable targets?**
   *"What did ships carry from Muziris?"* is three pairs; two of its targets sit
   at ranks 109 and 309 and cannot be reached by any reranker. Scoring it once
   takes recall from 26/32 to 26/30, and to 30/30 once the four in-window misses
   are fixed. **G2 is unreachable without this ruling.** It also reaches the gate
   partly by no longer counting the Old Tamil pair, which is the corpus's one
   broken cross-lingual link — say so on the same page as any G2 number.

2. **Do the four `translation_case` pairs expect the right thing?** They show
   `gapDoc +0.012` against `gapAny −0.142`: the chunk beating the target is
   always that document's own **English translation**, answering an English
   query. That is arguably correct retrieval. Settle it before hardening against
   it.

3. **Post-rerank, what is "score gap"?** G2 wants *"score gap wider than
   baseline, same pairs"*. Reranking changes ranks, not embedding similarities.
   Either recompute the gap on reranker scores — a different quantity from the
   recorded baseline — or measure gap pre-rerank and recall post-rerank. Decide
   and write it down, or G2 gets assessed against two incompatible readings of
   its own checklist.

4. **Add an English→Tamil cross-lingual probe.** The four `lang_pool:
   non_english` probes cover Greek, Chinese and Parthian only. The worst
   cross-lingual result in the corpus rests on one archived pair never designed
   to test it.

## Traps this block has already paid for

- **`CREATE OR REPLACE VIEW` in an early migration undoes a later one.**
  `schema-part4.sql` defines `retrievable_chunks` without B4's distractor guard,
  and both `run_ingest` and `run_embed` re-applied it — silently reverting
  containment mid-session. Fixed by `db.MIGRATIONS`, which applies part3 → part4
  → b4 in order. **If you add a migration that redefines a view, append it to
  `MIGRATIONS`.**
- **A count-based check can read a contaminated view and report OK.**
  `load_distractors` printed *"corpus chunks unchanged: 151 → 151 OK"* while the
  guard was gone. `ingest/test_distractors.py` now asserts the guard by reading
  `pg_get_viewdef`, not by counting rows through it.
- **A hardcoded remote name that matches nothing is invisible at the point of
  use.** Four separate instances in one seam — a renamed Met department, two Met
  vocabularies for one department, a combined Cleveland department, an
  unverified allowlist. Only a probe printing the live vocabulary beside the
  configured one catches these.
- **The answer path was exposed for several hours** while the guard was reverted.
  Nothing ran it, so no answer is contaminated — but if you replay archived
  answers, confirm none cites a `distractor-*` doc_id.

## Session ritual

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
docker compose up -d db
litellm --config gateway/config.yaml --port 4000     # separate window, C3 only
```

Verify state before changing anything:

```powershell
python -m ingest.run_embed --stats          # 450 eligible / 450 embedded / 0 pending
python -m ingest.test_distractors           # 16
python -m eval.test_ranking_check           # 35
python scripts\mutate_ranking.py            # 14
python scripts\mutate_distractors.py        # 6
```

## First session's work

C1a and C1b from the runbook — `cite.py`'s third match state and the
`translation_chunk*` rename. Both are cheap, both are on the G2 checklist, and
neither needs the gateway or a single API call. Do the four rulings in the same
session; they cost reading, not spend.

**Close by writing to `PROGRESS.md`, even a bad session.** Its value is that it
records what was believed at the time and how it turned out to be wrong.
