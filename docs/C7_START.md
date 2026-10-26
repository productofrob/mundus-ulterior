# C7 — starting point for the next thread

*Written 2026-08-20 at the close of the C5–C6 session. Supersedes `C5_START.md`, which is kept for its traps and its session ritual. Every number here came from a run on the host and is in `eval/ranking_runs/`.*

## Read these, in this order

| \# | file | why |
| :---- | :---- | :---- |
| 1 | **this file** | state, the two tasks, the trap fix's spec and its target number |
| 2 | `C6_RESULT.md` | C6 passed byte-identical; G2 at six of seven; the embedding-régime note |
| 3 | `C5_3B_AND_PROTOCOL.md` | decision 3b measured, **ruling 25**, the thresholds, two archive hazards |
| 4 | `C5_RESULT.md` | C5's verdict and the correction about `voyage-3.5` determinism |
| 5 | `C2_RULINGS.md`, `BLOCK_C_RULINGS.md` | rulings 1–24 |
| 6 | `PROGRESS.md` **on the host, last few sections only** | 557,037 bytes / 10,615 lines / 56 sections; do not read it whole, and see the warning below |

**`C5_START.md` is not on this list and is not needed.** Its traps and its session ritual are folded into this file. Do not act on its *"one open decision"* — that is closed, ruling 25, 2026-08-17.

**`PROGRESS.md` in the Claude project is STALE and must not be used.** It was uploaded 2026-08-10; the host file has ten days of sections after that, ending at *"C2 is measured and REJECTED (2026-08-17)"*, and the whole project knowledge base is 57 KB against the host file's 557 KB. Read `…\mundus-ulterior\PROGRESS.md` on disk, tail-first. The C5–C6 sections do not exist anywhere yet — writing them is TASK 3\.

## State, as measured 2026-08-20

tree          bff0605, clean; every ranking-path file verified byte-identical

              to its committed blob after C6

corpus        24 documents / 59 chunks / 57 retrieval-eligible

index         450 in retrievable\_chunks\_with\_distractors, 450/450/0 pending

gold set      33 pairs over 30 SCORED UNITS, 7 regions

suites        eval.test\_ranking\_check  209   |   scripts\\mutate\_ranking.py  86

C5            eval/ranking\_runs/20260819T102211+0000-…-collapsed-reranked50.json

C6            eval/ranking\_runs/20260820T151200+0000-…-collapsed-reranked50.json

              byte-identical to C5 across all 33 pairs, both sims, every rank,

              every aggregate, and rerank tokens

Suites NOT re-run this session: `ingest.test_distractors`, `mutate_distractors`, `answer.test_answer`, `answer.test_translate`, `mutate_part7b`, `ui\test_build_ui_data.py`, `ui\check_ui.mjs`.

## G2 — six of seven, and the verdict is settled

\[x\] ranking metric over \>=20 pairs, baseline recorded before any change

\[x\] distractor curve to \>=450, shape stated and reproducible

\[x\] top 6 for \>=95% at 450                          29/30 \= 0.967

\[ \] score gap wider than baseline    \+0.019535 vs \+0.024927   FAILED, ruling 25

\[x\] measured across \>=2 sessions on different days   C5 08-19 / C6 08-20

\[x\] cite.py third match state, mutation-verified

\[x\] translation\_chunk\* rename

**Ruling 25 (2026-08-17) declared the gap criterion failed and pulled kill trigger 1\.** W3 does not start. Both gap readings travel together forever: **\+0.015947** over all 33 pairs, **\+0.019535** over the 32 pairs B2 measured, against **\+0.024927** at 57 chunks. Neither is published without the other or without its index size.

---

# TASK 1 — the commit

Untracked and uncommitted after C6:

eval/ranking\_runs/20260819T102211+0000-…-collapsed-reranked50.json     C5

eval/ranking\_runs/20260820T151200+0000-…-collapsed-reranked50.json     C6

These two files ARE the evidence for G2 criterion 5\. Committing is safe now — the two-day window is closed and nothing on the ranking path may be held frozen any longer.

Also write into the repository root, beside `C2_RESULT.md` and `C5_START.md`, the four documents this session produced. They currently live only in the Claude project: `C5_3B_AND_PROTOCOL.md`, `C5_RESULT.md`, `C6_RUNBOOK.md`, `C6_RESULT.md`.

**Run `git` in PowerShell on the host, never through a mounted filesystem.** A `git status` issued from the Linux side of the device bridge on 2026-08-19 left a stale `.git/index.lock` that could not be unlinked and had to be cleared by hand. `git rev-parse` and `git hash-object` are lock-free and safe; `git status` is not.

---

# TASK 2 — the sequencing trap

## What is wrong

`recall@6 via the original text` is computed **PRE-rerank** while the adopted configuration **reranks**. The report prints recall at 29/30 post-rerank and via-original at 21/30 pre-rerank on the same page, as though they shared a measurement point. They do not.

`eval/run_ranking_check.py` **line 791**, in the collapsed scoring path:

result.recall\_at\_6\_via\_original \= bool(

    result.recall\_at\_6\_accepted\_collapsed          \# \<- PRE-rerank recall

    and not (result.collapse\_entry\_role \== "translation"

             and result.collapse\_primary\_role \== "original")

)

Unit level, **line 929**: `via_original = any(m.recall_at_6_via_original ...)`, gated on `collapsed`. Aggregate at **lines 985–986**, report at **1612–1613**.

## The fact that makes the fix cheap

**Collapse runs BEFORE rerank and emits one row per section.** So `collapse_entry_role` is fixed at collapse time and the reranker cannot change which member of a section surfaced first — there is only one row per section left for it to reorder. The fix therefore needs **no new entry-role computation in `apply_rerank`**. It is the same predicate evaluated against the post-rerank recall column.

## The shape

1. **`PairResult.recall_at_6_via_original_reranked`** — a NEW field under a new name. It must never overwrite `recall_at_6_via_original`, exactly as `rank_reranked` never overwrites `rank`. Every archived run holds the pre-rerank figure and dropping it makes the archive incomparable.  
     
   bool(result.recall\_at\_6\_accepted\_reranked  
     
        and not (result.collapse\_entry\_role \== "translation"  
     
                 and result.collapse\_primary\_role \== "original"))  
     
2. **`UnitResult.recall_at_6_via_original_reranked`** \= `any(...)` over members, gated on `reranked` exactly as the existing one is gated on `collapsed`.  
     
3. **Aggregate** keys `recall_at_6_via_original_reranked` and `…_n`.  
     
4. **Report** prints BOTH lines, pre and post, side by side and labelled.

## The target — computed offline from C6's archive, so the fix is verified

via-original, PRE-rerank   (what the harness prints today)   21/30 \= 0.700

via-original, POST-rerank  (what the fix must print)         22/30 \= 0.733

**Exactly one unit changes, and the two near-misses are the whole test:**

unit                  entry role   primary role   coll rank   rr rank   changes?

au-khao-sam-kaeo      None         translation       15          1      NO \-\> YES

aksum-trade-adulis    translation  original          10          2      no, and must not

adulis-exports        translation  original           3          7      no, and must not

`aksum-trade-adulis` is rescued by the reranker from 35 to 2 and **must still not count as via-original**, because its entry was the translation and its record's primary is the original — that is a bypass whatever the reranker does. A fix that prints 23/30 has dropped the primary-role clause. A fix that prints 21/30 has not taken effect. **22/30 is the only correct answer.**

## Assertions this needs before it is believed

- a unit the reranker rescues, whose entry was the **translation** of a record whose primary is the **original**, does NOT become via-original  
- a unit the reranker rescues, whose record has **no source text**, DOES  
- a unit that **leaves** the top 6 post-rerank loses post-rerank via-original while keeping its pre-rerank value  
- the pre-rerank figure is unchanged and still printed  
- **an unreranked run prints no post-rerank via-original key at all** — mirroring the existing assertion *"an unreranked run reports no post-rerank keys at all"*

## Mutations it needs

- the post-rerank value silently overwrites the pre-rerank one  
- the predicate drops the `collapse_primary_role == "original"` clause  
- the unit gate reads `collapsed` instead of `reranked`  
- the report prints only one of the two lines

## Then

Re-run the suites (expect 209+ and 86+), re-run the frozen command once, and confirm **22/30**. That run is NOT a third day and is not needed for any criterion — C5 and C6 are complete and criterion 5 is met. It is the fix's verification and nothing else.

---

# TASK 3 — write up and close Block C

`PROGRESS.md` needs: ruling 25, C5 and C6, G2 at six of seven, the trap fix, and **the two hazards found in the archive**, both of which are recorded in `C5_3B_AND_PROTOCOL.md` §3–4:

- the ranking path was **uncommitted** for two days and unprovable until `bff0605`  
- **`20260814T144013` reports `index_chunks=450` and did not search it** — it is byte-identical to the 57-chunk run of the same minute on all 33 pairs. It predates `check_search_reaches_the_view` (bb3bef5). It must never be cited as a 450-chunk measurement; W2b's 450 rung is the 13:35 run.

Then Block C closes and the work is the sourcebook at 24–60 records.

---

## The embedding-régime note, which is new and must not be lost

`voyage/voyage-3.5` query vectors were **byte-identical across seven runs and three days**, changed at or before 2026-08-17, changed again at or before 08-19, and were then byte-identical again across C5 and C6. Batch composition is refuted as the cause: 32-queries-in-1-request and 33-in-2 return the same vector. No query cache exists, the config edit was additive, the index is unmoved and the query text is unchanged since 08-14. **The remaining explanation is provider-side, and it is an open observation, not a finding.**

within a régime   comparisons are EXACT             C5 \= C6, to the bit

across a régime   aggregate gapDoc floor  \~1e-4

                  per-pair gapDoc floor   \~2e-3

**B2's baseline was measured in the old régime and C5–C6 in the new one**, so the gap criterion's comparison spans a boundary. It does not disturb ruling 25 — the deficit is 0.005392 and the drift is \~1.6% of it — but it belongs beside any future comparison against a pre-08-17 figure.

## Traps, carried forward — these bite the work in TASK 2 specifically

Folded in from `C5_START.md` so that file is not needed. The first three have already cost this repository a session each, and all three are live for a thread that is about to edit `run_ranking_check.py` and add assertions to it.

- **A test whose failure detail is non-Latin DIED instead of failing.** Through a pipe on Windows the child's stdout falls back to cp1252 and `print` raises. Invisible at baseline, because the detail only prints on failure — so the mutation harness saw a crash where there was a caught failure and called a working mutation unwatched. Both ends are fixed, but **any new assertion whose message carries Greek, Tamil or Chinese re-enters this territory.**  
- **Deleting code by line offset took a neighbouring function with it.** `write_atomically` vanished and surfaced as a `NameError` at the moment of writing. **Delete by name.** The line numbers quoted in TASK 2 are for reading, not for editing against.  
- **A check that greps a heading passes against a report that prints the heading and no rows.** TASK 2 adds a report line; asserting the line exists is not asserting the number is right. Assert the value.  
- **A fixture where the max is the last value tests the word "max", not the behaviour.** Two fusion mutations passed until the fixture was rebuilt so that neither first-wins nor last-wins reproduces the answer.  
- **`--limit N` caps a plan; it does not create one.** A run asked to do something that plans nothing must say so.  
- **A retry at temperature 0 is the same call**, and `claude-sonnet-5` refuses `temperature=0` outright. LiteLLM's `drop_params` fix is gateway-wide and was refused — see ruling 22\.

## Session ritual

cd "C:\\Users\\chemi\\Documents\\Claude\\Museums Project Number 1\\mundus-ulterior"

.venv\\Scripts\\Activate.ps1

Get-Content .env | Where-Object { $\_ \-notmatch '^\\s\*\#' \-and $\_ \-match '=' } | ForEach-Object {

  $name, $value \= $\_ \-split '=', 2

  Set-Item \-Path "Env:$($name.Trim())" \-Value $value.Trim()

}

docker compose up \-d db

litellm \--config gateway/config.yaml \--port 4000     \# separate window

python \-m ingest.run\_embed \--stats        \# 450 / 450 / 0 pending

python \-m eval.test\_ranking\_check         \# 209

python scripts\\mutate\_ranking.py          \# 86

python \-m eval.run\_ranking\_check \--with-distractors \--collapse \--rerank \--rerank-tpm 2000000

The frozen command takes **\~90 seconds**. If it runs past five minutes, `--rerank-tpm 2000000` was omitted and it is pacing against the default budget — two archived runs took 27 minutes that way. Let it finish; the budget is pacing only and cannot move a number.

`gateway/config.yaml` holds two chat aliases: `chat-default` (haiku-4-5, greedy) and `chat-strong` (sonnet-5, temperature 1 only). Part 6 and Part 7 must keep using `chat-default` — repointing it makes every archived number incomparable.

## The one thing the next thread must not inherit uncritically

**29/30 is whether the RECORD was found. 21/30 — soon 22/30 — is whether the NON-ENGLISH TEXT was reachable.** C2 was the only remaining intervention aimed at the second and it moved that number *down*. `muziris-cargo-akananuru` sits at rank 310, the corpus's one genuinely broken cross-lingual link, and is not counted toward the gate.

And the W2b curve still rests on **English-only padding** — seams 1 and 2 were dropped on a time-box, so the twelve Greek-target pairs faced no competing Greek at any rung. *"Flat over an eightfold index"* still means *"English-target retrieval survives English competition"*.

**C5 and C6 measured a stable pipeline. They did not measure a solved problem.**  
