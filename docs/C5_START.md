# C5 — starting point for the next thread

_Written 2026-08-17 at the close of the C2 session. Every number here came from a
run on the host and is in `eval/ranking_runs/`. Supersedes `C2_START.md`, which
is kept only for its traps._

## Read these, in this order

| # | file | why |
| --- | --- | --- |
| 1 | **this file** | state, the frozen configuration, what C5 must do, the one open decision |
| 2 | `C2_RESULT.md` | C2 measured and rejected; the gap arithmetic; decision 3 |
| 3 | `C2_RULINGS.md` | rulings 12–24, each with its cost |
| 4 | `BLOCK_C_RULINGS.md` | rulings 1–11 |
| 5 | `eval/ranking_runs/20260817T080300+0000-…-collapsed-reranked50.json` | the run C5 must reproduce |
| 6 | `PROGRESS.md` — **the last few sections only** | ~550 KB; do not read it whole |

## State, as measured 2026-08-17

```
corpus        24 documents / 59 chunks / 57 retrieval-eligible
index         450 in retrievable_chunks_with_distractors
gold set      33 pairs over 30 SCORED UNITS, 7 regions
renderings    eval/gold/query_renderings.json, 205 admitted, 0 held,
              digest af427581d957d0ba   — NOT read by the frozen configuration
suites        python -m eval.test_ranking_check     209 assertions
              python scripts\\mutate_ranking.py       86 mutations
```

Suites NOT re-run this session: `ingest.test_distractors`, `mutate_distractors`,
`answer.test_answer`, `answer.test_translate`, `mutate_part7b`,
`ui\\test_build_ui_data.py`, `ui\\check_ui.mjs`. Run them before trusting them.

## G2, and what C5–C6 can and cannot do

```
[x] ranking metric over >=20 pairs, baseline recorded before any change
[x] distractor curve to >=450, shape stated and reproducible
[x] top 6 for >=95% at 450                 29/30 = 0.967
[ ] score gap wider than baseline          +0.0160 vs +0.0249      UNMET
[ ] measured across >=2 days               <- ALL C5-C6 CAN COMPLETE
[x] cite.py third match state, mutation-verified
[x] translation_chunk* rename
```

**C5–C6 takes G2 from five of seven to six of seven and does not change the
verdict.** The gap is the sole remaining failure and **there is no intervention
left for it**: ruling 5 settled that no reranker can move it, and C2 — the only
candidate — was measured on 2026-08-17 and rejected.

Do it anyway. It isolates the failure to exactly one criterion, and if decision 3
later shifts the gap's reading you would otherwise need two more days before you
could act.

## The frozen configuration

```powershell
python -m eval.run_ranking_check --with-distractors --collapse --rerank --rerank-tpm 2000000
```

```
view            retrievable_chunks_with_distractors   450 chunks
embedding       voyage/voyage-3.5
rerank          rerank-2.5, window 50, route /v1/rerank
NOT --fuse      C2 is rejected; the renderings file is not read at all
NOT --skip-check
```

**C5 is that command run today. C6 is the same command on a different calendar
day.** Nothing between them may move:

- the index, its contents and its embedding model
- `eval/gold/ranking_pairs.json`
- the rerank window and model
- **any code on the ranking path** — see the sequencing trap below

### The numbers C5 must reproduce

From the 08:03 run's single-variant arm:

```
recall@6 per unit    pre 27/30 0.900  ->  collapsed 28/30 0.933  ->  reranked 29/30 0.967
MRR@10 per unit          0.726        ->      0.831              ->      0.842
via the original text                     21/30 = 0.700
gapDoc / gapAny (33 pairs, pre-rerank)    +0.0160 / -0.0151
coverage                                  28/33 targets, 29 post-rerank
cohort recall   archived_answer 4/8   authored 8/9   retrieval_probe 12/12   translation_case 3/4
rerank                                    ~30 requests, ~310K tokens
```

A material disagreement between the two days IS the finding, and is more
interesting than agreement. Record it; do not re-run until it goes away.

## THE SEQUENCING TRAP — read before touching anything

**`recall@6 via the original text` is still computed PRE-rerank while the
adopted configuration reranks.** Flagged in `C2_START.md`, still true, still
unfixed, and it must be fixed before that figure leaves `PROGRESS.md`.

Fixing it changes code on the ranking path. So it happens **before C5 or after
C6, never between them.** Doing it between the days silently makes the two runs
two configurations and destroys the criterion they exist to satisfy.

Same rule for the "same pairs" gap in decision 3b: compute it **offline from the
archived runs**, not by changing the harness.

## The one open decision — G2's gap criterion

C2 is rejected and the frozen configuration is settled. What remains is the
project owner's, and `C2_RESULT.md` lays out the arithmetic:

- **3a. Declare the gap criterion failed and pull kill trigger 1.**
  `PHASE2_PLAN` pre-declared it: W3 does not start; polish the sourcebook at
  24–60 records rather than chase 200.
- **3b. Recompute the gap on the 32 pairs B2 actually measured, first.** Free,
  offline, and it is the criterion's own wording — *same pairs*. Reconstructed
  from the printed table it is **+0.0196**, against **+0.0161** over all 33; the
  slide from W2b's recorded +0.020 is `probe-tamil-akananuru-en` entering the
  denominator at −0.098 after the baseline was set, not retrieval degrading.
  Does not clear +0.0249.
- **3c. Rule the criterion unmeetable as written and replace it.** The gap
  narrows as the index grows — that is what W2b measured — so asking a
  450-chunk gap to exceed a 57-chunk baseline can only be satisfied by shrinking
  the index. **Changing a gate after seeing the number it failed is the most
  dangerous move available.** Defensible only from the curve's shape, which was
  recorded before any of this, and only with the old reading kept permanently
  beside the new one.

**Recommended: 3b, then 3a or 3c on the corrected number. Do not skip to 3c.**

## Rulings 12–24, one line each

12. The render language set comes from the **INDEX**, never from the pair. The
    file is keyed on query text and holds no pair id, so leakage is not
    representable.
13. Fusion is **max per candidate**, declared before any call. Exact only
    because `SEARCH_K is None`; `fuse` asserts that and refuses otherwise.
14. Every C2 run reports **both arms**, same index, same day. A fused gap below
    the same-run single-variant arm is not a C2 win.
15b. The rule is **uniform** — every query rendered into every index language
    but its own. The control is an assertion the pipeline can fail. **It fired.**
16. The reranker keeps receiving the pair's **own query text**; the cache keys on
    the arm and the candidate ids.
17. Mistranslation guards: script check, query-to-query cosine (reported, never
    gated), renderings archived, and the sentence that travels with every number.
18. **C4 is closed** as a ranking item — `_merge` is inert in the harness. What
    remains is a W4 question about which of two recorded arms is cited.
19. Renderings are **frozen data**; the file's content hash is in every run.
20. Script floor **1.0**; a retry is a different prompt under its own version.
21. Attempts are **additive**; `best_attempt` promotes, a retry can only improve.
22. Temperature is **classified, recorded and opt-in** — never dropped.
23. Uneven sampling recorded (23a); marks judged, not just letters (23b).
24. The verdict is **derived on read**, never trusted from disk.

## Traps this session paid for

- **A test whose failure detail is non-Latin DIED instead of failing.** Through
  a pipe on Windows the child's stdout falls back to cp1252 and `print` raises.
  Invisible at baseline — the detail only prints on failure — so the mutation
  harness saw a crash where there was a caught failure and called a working
  mutation unwatched. Both ends now fixed. **Every guard in this repository
  whose message carries Greek, Tamil or Chinese was affected.**
- **Deleting code by line offset took a neighbouring function with it.**
  `write_atomically` vanished, and the failure surfaced as a `NameError` at the
  moment of writing, after a correction had been detected and announced. Delete
  by name.
- **An inverted log line** printed "kept the earlier attempt" on exactly the
  sixteen rows where the new attempt won.
- **A loader that dropped `text`/`ok` made the promotion counter blind**, so a
  computed correction was reported as "nothing to do" and thrown away.
- **A retry at temperature 0 is the same call.** A corrective prompt naming the
  writing system made Old Tamil *worse* on seven of ten rows.
- **`claude-sonnet-5` refuses `temperature=0`.** LiteLLM's suggested
  `drop_params` fix is a gateway-wide setting and was refused.
- **A fixture where the max is the last value tests the word "max"**, not the
  behaviour. Two fusion mutations passed until the fixture was rebuilt so that
  neither first-wins nor last-wins reproduces the answer.
- **A check that greps a heading passes against a report that prints the heading
  and no rows.**
- **`--limit N` caps a plan; it does not create one.** A run asked to do
  something that plans nothing must say so, and now does.

## Session ritual

```powershell
cd "C:\\Users\\chemi\\Documents\\Claude\\Museums Project Number 1\\mundus-ulterior"
.venv\\Scripts\\Activate.ps1
Get-Content .env | Where-Object { $_ -notmatch '^\\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
docker compose up -d db
litellm --config gateway/config.yaml --port 4000     # separate window
```

Verify before changing anything:

```powershell
python -m ingest.run_embed --stats        # 450 eligible / 450 embedded / 0 pending
python -m eval.test_ranking_check         # 209
python scripts\\mutate_ranking.py          # 86
```

`gateway/config.yaml` now holds **two** chat aliases: `chat-default`
(haiku-4-5, greedy) and `chat-strong` (sonnet-5, temperature 1 only). Part 6 and
Part 7 still use `chat-default` and must keep doing so — repointing it would make
every archived number incomparable.

## The one thing the next thread must not inherit uncritically

**29/30 is whether the RECORD was found. 21/30 is whether the NON-ENGLISH TEXT
was reachable.** C2 was the only remaining intervention aimed at the second, and
it moved that number *down*, 21/30 to 20/30. `muziris-cargo-akananuru` still sits
at rank 308 and is not counted toward the gate.

And the W2b curve still rests on **English-only padding** — seams 1 and 2 were
dropped on a time-box, so the twelve Greek-target pairs faced no competing Greek
at any rung. *"Flat over an eightfold index"* still means *"English-target
retrieval survives English competition"*.
