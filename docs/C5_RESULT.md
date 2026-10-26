# C5 — run, and the verdict against the pre-declared thresholds

_2026-08-19. `eval/ranking_runs/20260819T102211+0000-retrievable_chunks_with_distractors-collapsed-reranked50.json`,
tree `bff0605`, working tree clean but for the run's own output. Judged against
the thresholds written in `C5_3B_AND_PROTOCOL.md` §2 **before the run existed**._

---

## C5 PASSES. Every gated figure held.

```
                                     08-17 08:03      C5 08-19 10:22    threshold      verdict
recall@6 per unit, pre-rerank        27/30 0.900      27/30 0.900       any change     HELD
recall@6 per unit, collapsed         28/30 0.933      28/30 0.933       any change     HELD
recall@6 per unit, reranked          29/30 0.967      29/30 0.967       any change     HELD
recall@6 via the original text       21/30 0.700      21/30 0.700       any change     HELD
coverage  pre / collapsed / reranked 28 / 30 / 29     28 / 30 / 29      any change     HELD
per-pair recall@6 flips, any stage   -                none              any            HELD

gapDoc, 33 pairs                     +0.016047        +0.015947         |d| > 0.0005   HELD  d=-0.000100
gapDoc, B2's 32 pairs                +0.019622        +0.019535         |d| > 0.0005   HELD  d=-0.000087
gapAny, 33 pairs                     -0.015056        -0.015152         |d| > 0.0005   HELD  d=-0.000096
max per-pair |d gapDoc|              -                0.001683          > 0.003        HELD  probe-chinese-weilue
pairs over 0.003                     -                0                 any            HELD

MRR@10 per unit, reranked            0.841984         0.841984          reported       0.000000
```

Configuration identity, field by field: `view`, `index_chunks` 450, `search_k`
450, `embedding_models`, `query_embedding_model`, `rerank_model` rerank-2.5,
`rerank_window` 50, `rerank_route` `/v1/rerank`, `collapse_stats`
`{in 450, out 426, removed 24, promoted 425}`, and both `chunk_id_drift` entries
— **all identical.** `fused` False, `renderings_digest` null: C2 is not read, as
the frozen configuration requires.

---

## Everything that moved, and it closes exactly

Three units moved a rank, none of them across a gate:

```
unit                        pre-rerank   collapsed   effect on a gated figure
probe-tamil-akananuru-en      4 ->  5      4 ->  5   none - still recall@6
aksum-trade-adulis           34 -> 35     11 -> 10   none - a miss either way
au-khao-sam-kaeo             17 -> 16     16 -> 15   none - a miss either way
muziris-cargo-papyrus       108 ->106       (unit best is rank 5, unmoved)
muziris-cargo-akananuru     308 ->310       (unit best is rank 5, unmoved)
```

All within the declared tolerance of two places for anything outside the top 6.
`probe-tamil-akananuru-en` moved inside the top 6 and stayed a hit.

**The whole MRR delta is those moves and nothing else:**

```
MRR@10 per unit, pre-rerank    0.726111 -> 0.724444   d = -0.001667
  probe-tamil-akananuru-en  RR 0.25 -> 0.20  =  -0.05 / 30  =  -0.001667      exact

MRR@10 per unit, collapsed     0.830556 -> 0.832222   d = +0.001667
  probe-tamil-akananuru-en  RR 0.25 -> 0.20  =  -0.05 / 30  =  -0.001667
  aksum-trade-adulis        RR 0.00 -> 0.10  =  +0.10 / 30  =  +0.003333
                                                    net     =  +0.001667      exact

MRR@10 per unit, reranked      0.841984 -> 0.841984   d =  0.000000
```

Both deltas are accounted for to the last decimal with no residual. `aksum-trade-adulis`
crossing the rank-10 boundary in the collapsed ranking is why the collapsed MRR
rose while the pre-rerank MRR fell — one unit entering the MRR@10 window is
worth more than one unit slipping a place inside it.

**The reranked stage — the one G2's recall criterion reads — did not move at
all, in any figure, to six decimal places.**

---

## CORRECTION — why C5 moved at all

**§2 of `C5_3B_AND_PROTOCOL.md` said `voyage-3.5` is not bit-reproducible for
identical text across calls. That was inferred from two runs and it is wrong.**
Traced across every archived run, on `probe-greek-muziris` — a native Greek
query at rank 1 throughout, whose target is in the seed corpus:

```
run              idx    sim_target             sim_best_other_doc
20260814T084042   57    0.63747713789207683    0.54501903057098389
20260814T144005   57    0.63747713789207683    0.54501903057098389
20260814T133556  450    0.63747713789207683    0.54501903057098389
20260816T073642   57    0.63747713789207683    0.54501903057098389
20260816T073652  450    0.63747713789207683    0.54501903057098389
20260816T152136  450    0.63747713789207683    0.54501903057098389
20260816T162515  450    0.63747713789207683    0.54501903057098389
------------------------------------------------------------------ boundary
20260817T080300  450    0.63969614269161401    0.54493742645533161
20260819T102211  450    0.63903526300402180    0.54501479864120483
```

**Seven runs, five sessions, three calendar days, two index sizes and two
different gold-set sizes — byte-identical to seventeen decimal places.** Then it
breaks between 2026-08-16 16:25 and 2026-08-17 08:03, and every run since has
been different.

There is no query-vector cache to explain the identity: `vector_of` is built
per-run in `run_ranking_check.run()` and `rerank_cache` is per-run too, so all
nine runs embedded their queries by a fresh API call. Nor does the repository
explain the break:

```
gateway/config.yaml   the only edit is ADDITIVE - the chat-strong alias.
                      embed-default is untouched and no caching is configured.
the index             450 / 450 / 0 pending; embedding_models identical in
                      every run; collapse_stats and chunk_id_drift identical
the query text        ranking_pairs.json unmodified since 2026-08-14
```

What is left is provider-side: `voyage/voyage-3.5` is a vendor-versioned model
behind an alias, and something about it changed at that boundary. **This is
stated as the remaining explanation, not as a measurement.** It is unresolved,
it is recorded here, and it does not threaten C5 — the drift is 1e-4 against a
threshold of 5e-4 declared before the run, and no gated integer moved.

**The prediction in the earlier draft is withdrawn.** It rested on batch
composition, and batch composition is refuted by the table above: the 08-14 run
embedded 32 queries and the 08-16 run embedded 33, in a different number of
requests, and both returned the same vector. C6 has no prediction attached to
it. The declared materiality threshold stays at **0.0005**, unchanged and not
retuned after seeing C5.

**C6 is now also the experiment that settles this**, at no extra cost and with
no code change: `sim_target` is already archived on every pair. If C6 reproduces
C5 to seventeen decimals, the break was a one-off and determinism has returned.
If C6 differs from C5 as C5 differed from 08-17, the query embedding has become
non-deterministic run-to-run and every future comparison in this repository
carries a 1e-4 floor that has to be written down.

**This is the criterion earning its keep.** A second run of C5 an hour later
could not have surfaced any of it.

Rerank spend halved as expected — 60 requests / 626,634 tokens for two arms on
08-17, 30 requests / 310,185 tokens for one arm in C5.

---

## Why C6 waits for a different day — the criterion's own words

`C5_START.md` abbreviates the criterion to `measured across >=2 days`. The full
wording is in `PROGRESS.md` line 9229:

```
[ ] measured across >=2 SESSIONS on DIFFERENT DAYS    zero days so far under this metric
```

Two sessions **and** two days — the abbreviation dropped a word and the dropped
word is the stricter one. The rationale is recorded too, at line 9199, written
on 2026-08-14 before any of this was measured:

> *"The re-measure that gives the new pair its first rank should be its own
> session, on its own day, because G2 wants two measurements on different days
> and a run made in the same session as the code that changed the metric is a
> weak first day."*

So the criterion is not testing arithmetic stability, which a second run an hour
later would test. It is testing whether the number survives the environment
changing underneath it — a gateway restart, a vendor repointing an alias, a
machine rebooted, an operator returning cold. The correction above is that
failure caught in miniature.

There is a precedent, and it held: the 57-chunk gap on B2's 32 pairs reads
**+0.024927** in the 2026-08-14 08:40 baseline, **+0.024927** in the 08-14 14:40
session, and **+0.024927** in the 2026-08-16 07:36 session — three sessions, two
days, byte-identical. That is what a passing C5–C6 looks like.

Run stamps are UTC, so the earliest technically-valid C6 is after 00:00 UTC on
2026-08-20 — 01:00 London. **Do not do that.** The criterion says *sessions*,
and a run fired at five past midnight to tick a box is the letter of the gate
against its purpose, which is the thing this project has refused everywhere
else. Run it as a normal session tomorrow.

---

## C6 — the whole instruction

**On a different calendar day, 2026-08-20 or later:**

```powershell
python -m eval.run_ranking_check --with-distractors --collapse --rerank --rerank-tpm 2000000
```

**Between now and then, the repository is not touched.** Not a commit, not an
edit, not a re-embed, not a gateway change, not a gold-set change. Do not commit
the C5 run JSON — it is an output, it is safe where it is, and the simplest rule
that cannot be got wrong is *nothing*.

Verify immediately before C6, and record both lines beside the run:

```powershell
git rev-parse --short HEAD          # must read bff0605
git status --porcelain              # must show ONLY the untracked run JSONs
python -m ingest.run_embed --stats  # 450 / 450 / 0 pending
```

The suites do not need re-running before C6 — re-running them changes nothing,
but neither does skipping them, and the tree hash is the stronger evidence.

---

## After C6

1. **G2 goes to six of seven.** Criterion 5, *measured across ≥2 days*, is met.
   The gap is then the sole remaining failure, isolated, with ruling 25 already
   recording it as failed and kill trigger 1 pulled.
2. **The sequencing-trap fix.** `recall@6 via the original text` is still
   computed pre-rerank while the adopted configuration reranks. Ruled: **after
   C6.** It is safe the moment C6 is archived, and it must land before 21/30
   leaves `PROGRESS.md`.
3. **Block C closes.** `PROGRESS.md`, and the sourcebook at 24–60 records.
