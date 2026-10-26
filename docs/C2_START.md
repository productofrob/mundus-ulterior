# C2 — starting point for the next thread

_Written 2026-08-16 at the close of the C2a/C3 session. Every number here was
produced by a run on the host and is in `eval/ranking_runs/`. Where something is
inferred rather than measured, it says so._

## Read these, in this order

| # | file | why |
| --- | --- | --- |
| 1 | **this file** | state, the eleven rulings, what C2 must clear, the traps |
| 2 | `BLOCK_C_RULINGS.md` | all eleven in full, each with its arithmetic and its cost |
| 3 | `PHASE2_PLAN.md` § *Block C* | C2/C4/C5–C6 and the **G2 checklist** |
| 4 | `PROGRESS.md` — **the last ~8 sections only** | this session. ~530 KB; do not read it whole |
| 5 | `eval/ranking_runs/20260816T162515+0000-…-collapsed-reranked50.json` | **the configuration C2 is measured against** |
| 6 | `eval/ranking_runs/20260814T084042+0000-retrievable_chunks.json` | the B2 baseline the GAP criterion compares to |

`C3_START.md` is superseded by this file. It is kept for its traps.

## State, as measured 2026-08-16, committed at `695a06b`

```
corpus        24 documents / 59 chunks / 57 retrieval-eligible
index         450 in retrievable_chunks_with_distractors  (57 corpus + 393 distractors,
              one of which is the containment canary — ruling 6)
gold set      33 pairs over 30 SCORED UNITS, 7 regions
git           committed for the first time since A2. eval/run_ranking_check.py
              had been UNTRACKED while every Block B and C number depended on it.
```

Green, verified this session:

```
python -m eval.test_ranking_check      131 assertions
python scripts\mutate_ranking.py        50 mutations
```

The other suites (`ingest.test_distractors`, `mutate_distractors`,
`answer.test_answer`, `answer.test_translate`, `mutate_part7b`,
`ui\test_build_ui_data.py`, `ui\check_ui.mjs`) were **not** re-run today. Run
them before trusting them.

## The measurement C2 is judged against

```
                                 recall@6      MRR@10   gapDoc (33 pairs)
uncollapsed, no rerank           27/30 0.900   0.726    +0.016
collapsed (C2a)                  28/30 0.933   0.834    +0.016
collapsed + reranked (ADOPTED)   29/30 0.967   0.841    +0.016
via the original text            21/30 0.700
B2 baseline, 57 chunks                                  +0.0249
```

**Adopted configuration: `--collapse --rerank`.** C3 alone is a net negative; in
combination it is the difference between 28/30 and 29/30. C5–C6 must measure
this configuration, frozen.

## G2, as it stands

```
[x] ranking metric over >=20 pairs, baseline recorded before any change
[x] distractor curve to >=450, shape stated and reproducible
[x] top 6 for >=95% at 450        29/30 = 0.967
[ ] score gap wider than baseline +0.016 vs +0.0249   <- C2's whole job
[ ] measured across >=2 days      one day, blocked on the gap
[x] cite.py third match state, mutation-verified
[x] translation_chunk* rename
```

**Five of seven. The recall half of Block C is done; the gap half has not
started.**

## The eleven rulings, one line each

1. A multi-target query is **one unit** scored on its best acceptable target;
   coverage is reported, never gated. 33 pairs → 30 units.
2. Four `translation_case` pairs also accept their document's own published
   translation **of the same section**, on `ground=section` only.
3. The gap is measured **pre-rerank**, recall **post-rerank**. Reranker-score
   gap is recorded under its own name and never compared to the baseline.
4. *"Wider than baseline"* reads **gapDoc**, positive at every rung, not gapAny.
5. C2 is on the critical path: no reranker can move the gap.
6. The containment canary **is** a distractor and competes in ranking runs.
7. Ruling 2 does **not** extend to the pairs C3 displaced — it would rescue a
   failing gate and leave 4 units of 30 as the whole cross-lingual test.
8. **C2a**: a section is ONE retrievable record. A change to what the system
   RETURNS, measured by an unchanged metric — which is why it is allowed where
   ruling 7 was refused.
9. **`sole`** is a ground and it collapses; `index` at n=1 is mislabelled. Ruled
   in only with its companion, **`recall@6 via the original text`**.
10. **C2 is QUERY TRANSLATION**, not hybrid lexical+dense.
11. The collapse canonicalises to the record's **primary** text, derived from
    `source_type` via `ingest.fidelity.FIND_TYPES`. No seed record was edited.

## Why C2 changed, and the evidence for it

The gold set holds the controlled comparison:

```
target                              native-language query    English query
eastasia-01-weilue::original::000   probe-chinese-weilue   1  china-…-weilue      5
southasia-01-akananuru-149::…::000  probe-tamil-akananuru  1  muziris-…-akananuru 309
southasia-02-periplus-muziris       probe-greek-muziris    1  muziris-…-periplus  5
persia-01-skz                       probe-parthian-skz     1
```

**Every non-English target ranks 1 when queried in its own language.** The index
is not the problem, the passage embeddings are not the problem, the reranker is
not the problem. The bottleneck is the language of the QUERY.

The original C2 — hybrid lexical+dense — was undermined twice: a lexical index
over an English query boosts that document's English sibling, which is the chunk
already beating the target; and the misses are not vocabulary-mismatch failures.

## Four design constraints, known now rather than found later

1. **THE LEAKAGE TRAP, and it is the one that would invalidate everything.**
   Choosing which language to translate a query into by reading the pair's
   `expect_lang` is **using the answer to find the answer**. A run built that
   way measures nothing. The query must be translated without reference to its
   target — into every candidate language, or into a set chosen by a rule that
   cannot see the gold set. Decide this first and write it down.
2. **The gap needs a single defined score per pair, or ruling 3 breaks.** Two
   queries produce two similarities; `gapDoc` is compared to a B2 baseline
   computed from one. The fusion rule — max, mean, or best-query-wins — must be
   **declared before any run**, and the gap must be denominated in whatever it
   produces, consistently. Choosing the fusion rule from results is the same
   error as choosing rank fusion after seeing the score.
3. **The four `lang_pool: non_english` probes are the CONTROL and must not
   improve.** They already query in the target language and rank 1. Translating
   a Greek query into Greek is a no-op; if those four move, the harness is doing
   something other than what it says.
4. **Mistranslation is a new failure mode with no baseline and no guard.**
   `answer/translate.py` exists — read it before designing. A translated query
   that succeeds proves the pipeline works, not that the retriever is
   cross-lingual, and that must be said in the same breath as any number.

## Also outstanding, both cheap

- **Does C2a subsume C4?** The runbook's C4 re-examines `align._merge`
  presenting a whole section when one member was retrieved — the same territory
  ruling 8 settled from the retrieval side. A ruling, not code, and it may close
  an item the plan flags as *"most likely to absorb a week for a null result"*.
- **`recall@6 via the original text` is computed PRE-rerank** while the adopted
  configuration includes reranking. A pre-rerank number on a post-rerank page is
  the mismatch ruling 3 exists to prevent, inside the instrument built to
  prevent it. It is conservative in the right direction and nothing depends on
  it yet. **Fix it before that figure leaves `PROGRESS.md`.**

## Traps this session paid for

- **A mutation harness killed mid-iteration leaves a silent one-word edit** with
  nothing to restore from, and the next run captures it as *originals*. Twice in
  one day. Run it on the host, on a local filesystem, one at a time.
- **A crashed suite reads as "no failures."** The harness reads FAIL lines from
  stdout, so an uncaught exception marked a mutation unwatched AND skipped every
  check after it. Now returns `SUITE_CRASHED`.
- **`MUTATIONS` and `EXPECTED` are zipped positionally.** An entry added to one
  and not the other at the same offset mispairs everything after it and prints a
  row of MISSes that read like real failures. Order is the contract.
- **Printing before archiving destroyed a 26-minute run.** A `KeyError` in
  `print_report` killed the process before `archive()`. **Archive first**; the
  archived run is the evidence, the terminal output is a rendering of it.
- **`extra = {...}` where `.update` was meant** discarded the collapse keys and
  was invisible unless BOTH interventions were on. Neither alone could catch it.
- **Three claims taken from documentation were wrong** — 2000 RPM (it is 3
  without a payment method), a 4.7K-token window (6.1K), "the window is too big"
  (the spacing was too tight). Measure, then write the sentence.
- **A stub that lies makes a green test about a fiction.** `ranking()` called
  every chunk an `original`, so `roles_removed == ["original"]` passed while the
  real collapse removes translations.
- **`git add -A` nearly committed a 129 MB gazetteer dump.** Verify a staged
  commit by NAME (`git diff --cached --name-only | Select-String "\.gz$"`),
  never by count.

## Session ritual

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
docker compose up -d db
litellm --config gateway/config.yaml --port 4000     # separate window
```

Verify before changing anything:

```powershell
python -m ingest.run_embed --stats        # 450 eligible / 450 embedded / 0 pending
python -m eval.test_ranking_check         # 131
python scripts\mutate_ranking.py          # 50
python scripts\probe_sections.py          # 15 with a translation, 3 primary=translation
python -m eval.run_ranking_check --with-distractors --collapse --rerank --rerank-tpm 2000000
                                          # 29/30 = 0.967, via-original 21/30
```

The Voyage account now has a payment method: **2000 RPM / 2M TPM, measured**
(`waiting=0s`). A full reranked run is seconds and ~310K tokens — 0.15% of the
200M free rerank allowance.

## The one thing the next thread must not inherit uncritically

**29/30 is whether the RECORD was found. 21/30 is whether the NON-ENGLISH TEXT
was reachable.** Nine pairs reached a source text through its English, including
`muziris-cargo-akananuru` at rank 309 finding its record at 5 on the strength of
a translation. G2 asks the first question. This project exists to answer the
second, and **C2 is the only remaining work aimed at it.**

And the flat W2b curve still rests on **English-only padding** — seams 1 and 2
were dropped on a time-box, so the twelve Greek-target pairs faced no competing
Greek at any rung. *"Flat over an eightfold index"* still means *"English-target
retrieval survives English competition"* and still says nothing about
non-English retrieval at scale.
