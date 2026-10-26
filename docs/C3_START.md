# C3 — starting point for the next thread

_Written 2026-08-16 at the close of the C1 sessions. Every number here was
produced by a run on the host, not recalled. Where something is inferred rather
than measured, it says so._

## Read these, in this order

| # | file | why |
| --- | --- | --- |
| 1 | **this file** | state, the six rulings, what C3 must clear, the traps |
| 2 | `BLOCK_C_RULINGS.md` | the six rulings in full, each with its arithmetic and its cost |
| 3 | `PHASE2_PLAN.md` § *Block C* | C3's brief and the **G2 checklist** |
| 4 | `PROGRESS.md` — **the last ~10 sections only** | the C1 sessions. ~500 KB; do not read it whole |
| 5 | `eval/ranking_runs/20260816T073652+0000-retrievable_chunks_with_distractors.json` | **the baseline C3 is measured against** |
| 6 | `eval/gold/ranking_pairs.json` | 33 pairs / 30 units; every `note` says why that pair exists |

**`BLOCK_C_START.md` is now partly stale** — its four open rulings are settled,
and its statement that the canary "cannot perturb a ranking run" was wrong. It is
kept for its traps, not its state. Read counts from the database and metrics from
an archived run, never from a document. This block proved that costs a day.

## State, as measured 2026-08-16

```
corpus        24 documents / 59 chunks / 57 retrieval-eligible
index         450 in retrievable_chunks_with_distractors
              = 57 corpus + 393 distractors, ONE OF WHICH IS THE CANARY
              retrievable_chunks sees 57 — distractors excluded, containment verified
gold set      33 pairs over 30 SCORED UNITS, 7 regions
spend to date across all of Block C: 6 batched embedding requests. No chat calls.
```

Green suites:

```
python -m eval.test_ranking_check      67 assertions
python scripts\mutate_ranking.py       23 mutations
python -m ingest.test_distractors      16 assertions
python scripts\mutate_distractors.py    6 mutations
python -m answer.test_answer           all
python -m answer.test_translate        all
python scripts\mutate_part7b.py        15 mutations
python ui\test_build_ui_data.py        all
python ui\build_ui_data.py --verify    157 resolved / 0 case_folded / 9 case_only / 1 moved / 1 absent
node ui\check_ui.mjs                   all
```

`--verify` exits non-zero on `moved 1` + `absent 1`. Both are the known Adulis
case from A4's Wikisource recovery. Unchanged, expected, and the standing
argument for D1.

## The measurement C3 is judged against

```
                       57 chunks    450 chunks
unit recall@6          27/30        27/30      = 0.900
gapDoc, same 32 pairs  +0.0249      +0.0196
```

Not one pair changed its recall@6 status between the rungs. 393 distractors
moved four pairs' gaps and zero outcomes.

The three misses, all inside a top-50 window:

```
aksum-trade-adulis     35    English -> Greek
au-khao-sam-kaeo       17    English -> English (ordinary relevance failure)
adulis-exports         15    English -> Greek
```

**G2 needs 29/30. So C3 must fix two of those three.** Two are cross-lingual,
which is the case a multilingual cross-encoder has a mechanism for.

Also on the board and NOT counted, by ruling 1: `muziris-cargo-papyrus` at 109
and `muziris-cargo-akananuru` at 309. The second is the corpus's one genuinely
broken cross-lingual link and belongs on the same page as any G2 number.

## The six rulings, one line each

1. A multi-target query is **one unit** scored on its best acceptable target;
   per-unit **coverage** is reported and never gated. 33 pairs → 30 units.
2. Four `translation_case` pairs also accept their document's own published
   translation **of the same section**, computed by `align.pair_chunks` and
   admitted only on `ground=section`. This is what took
   `tc-frankincense-harvest` from 11 to 1.
3. The gap is measured **pre-rerank**, recall **post-rerank**. Reranker-score gap
   may be recorded under its own name and never compared to the baseline.
4. *"Wider than baseline"* reads **gapDoc**, which is positive at every rung, not
   gapAny, which is negative at every rung.
5. **C2 is back on the critical path.** Ruling 3 means no reranker can move the
   gap; C2 is the only planned intervention that changes what produces the score.
6. The containment canary **is** a distractor and competes in ranking runs. The
   schema comment saying otherwise was struck.

## What C3 is, and what it is not

**It is a recall intervention only.** Under ruling 3 the gap criterion is
measured on embedding similarities, and reranking does not alter them. Do not
design C3 to move the gap; it cannot. That is C2's job.

**Path, already settled — hosted, no local model.** LiteLLM supports Voyage
rerank through the gateway already in place:

```yaml
model_list:
  - model_name: rerank-2.5
    litellm_params:
      model: voyage/rerank-2.5
      api_key: os.environ/VOYAGE_API_KEY
```

`rerank-2.5` is multilingual, 32K context, and carries **200M free tokens**
(the legacy `rerank-2` is also multilingual but has none). A full run over the
gold set at a top-50 window is on the order of 330K tokens — about 0.17% of the
allowance. **C3 costs effectively nothing.**

Local was checked and rejected on cost-benefit, not feasibility: CPU-only torch
wheels for cp314 do exist (2.9.1+cpu, plain pip, Windows), but the
`sentence-transformers` / `transformers` / `tokenizers` chain on cp314 is
unverified and buys nothing over a free hosted call.

**First action, before designing anything:** one `litellm.rerank()` call with a
throwaway query and three documents, to confirm the key reaches the endpoint.
Discovering that halfway through a design is the expensive version.

## Three design constraints, known now rather than found later

1. **Rerank the `lang_pool`-FILTERED candidate set.** Five pairs restrict
   candidates to non-English before ranking, and that filter is the only thing
   making them cross-lingual tests rather than same-language tests wearing the
   label. Reranking a raw top-50 silently restores English translations to pools
   built to exclude them.
2. **Do not overwrite `rank`.** Every gap and the whole B2-comparable aggregate
   are denominated in it. Ruling 2's precedent is the pattern to follow:
   `rank_accepted` sits beside `rank`, and the post-rerank rank should sit beside
   both. Rewriting `rank` restates every number Block B recorded as though the
   intervention had always been in force.
3. **Single-vendor blind spot.** Embeddings and reranking would both be Voyage.
   A cross-encoder scores query and passage jointly rather than comparing two
   independent vectors, so it *can* differ from the bi-encoder — but shared
   training data is a real unknown. **If C3 moves nothing, that is the first
   hypothesis, not a mystery.**

## Traps this block paid for

- **A report can count one view and rank another, with both numbers correct.**
  `index_state()` read `retrievable_chunks_with_distractors` and reported 450;
  `search()` hardcoded `retrievable_chunks` and ranked 57. The header said
  `index=450 depth=450` over a table of 57-chunk ranks. Fixed: `search()` takes
  an explicit view against an allowlist, and a pre-flight probe asserts an
  unfiltered search to depth N returns N hits. **If you add a stage that changes
  the candidate set, assert what it actually read.**
- **B5's curve was only measurable while containment was broken.** Restoring the
  guard silently removed the ability to measure the 450 rung, and nothing said
  so. The curve is real and is now reproducible on demand — verified by
  reproducing 309/109/35/17 exactly.
- **Prose asserting behaviour nobody measured.** The canary comment; `not_in_top_20`
  measured at k=50; `index.html` saying "six case-only spans" while the audit
  printed nine. Three instances in one block. **A sentence describing runtime
  behaviour needs an assertion or it is decoration.**
- **`mutate_*.py` restore is a claim about text, not bytes.** `f.write_text()` on
  Windows rewrites LF as CRLF, and the harness's own check uses `read_text()`,
  which translates it back. Files are semantically restored and byte-changed.
  Harmless with `.gitattributes`, unfixed, and **the one piece of known debt this
  thread leaves behind** — the fix is to keep the original bytes and restore
  those.

## Session ritual

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
docker compose up -d db
litellm --config gateway/config.yaml --port 4000     # separate window, C3 needs it
```

Verify before changing anything:

```powershell
python -m ingest.run_embed --stats        # 450 eligible / 450 embedded / 0 pending
python -m eval.test_ranking_check         # 67
python scripts\mutate_ranking.py          # 23
python -m ingest.test_distractors         # 16
python -m eval.run_ranking_check --dry-run   # 33 of 33 resolved, free
```

## G2, as it stands

```
[x] ranking metric over >=20 pairs, baseline recorded before any change
[x] distractor curve to >=450, shape stated — and reproducible
[ ] top 6 for >=95% at 450        27/30 = 0.900; C3 must fix 2 of 3
[ ] score gap wider than baseline +0.0196 vs +0.0249 — narrower; C2's job, not C3's
[ ] measured across >=2 days      one clean day banked, 2026-08-16
[x] cite.py third match state, mutation-verified
[x] translation_chunk* rename
```

## The one thing the next thread must not inherit uncritically

**That 0.900 is close to 0.95.** It is three misses against a budget of one, on a
30-unit denominator where every unit is worth 0.033 — and it was reached partly
by no longer counting the two hardest targets in the corpus. The gate is
reachable. It is not nearly passed.

And the flat curve still rests on **English-only padding**: seams 1 and 2 were
dropped on a time-box, so the twelve Greek-target pairs faced no competing Greek
at any rung. The 2026-08-16 run made that concrete rather than theoretical —
only four pairs saw any gap change at all, and every one of them lost to an
English museum-catalogue distractor. *"Flat over an eightfold index"* means
*"English-target retrieval survives English competition"* and still says nothing
about non-English retrieval at scale.
