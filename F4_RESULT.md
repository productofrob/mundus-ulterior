# F4 RESULT — five records, two predictions read, and an instrument that cannot see the thing three tranches have been claiming

*Closed 2026-09-04. Corpus **35 records**, digest
`9728581d164b0a4b68520ecc0ff3e8eea0d21d475c9895788c4fcc8c0344da69`, 82 chunks,
23 parallel pairs. Ranking run
`eval/ranking_runs/20260904T081155+0000-retrievable_chunks_with_distractors.json`,
index 473 chunks, BASELINE arm.*

*2026-09-04 is a **fourth distinct UTC date** in Block F. Three rules wanted a
third and ruling 50 booked a ninth session to buy one; Part 3 being its own day
paid for it and one more.*

---

## 1. Delivery against the allocation

```
ALLOCATED 7   Sub-Saharan Africa 2 vwp + 2 vme      East Asia 2 vwp + 1 vme
DELIVERED 5   31 africa-05-adulis-throne      vwp   (Part 1)
              32 africa-04-silko-talmis       vwp   (Part 1)
              33 eastasia-04-jingjiao-stele   vwp   gloss
              34 eastasia-05-liangshu-qin-lun vwp   gloss (weak — ruling 62)
              35 eastasia-06-cefu-yuangui     vme   + the vme_quotation_case
SHORTFALL 2   Sub-Saharan Africa's two verbatim_machine_english slots
```

**East Asia met its source-language floor** — 5 against 4 — and is the second
region to do so. Sub-Saharan Africa is at 3 against 4, and ruling 58 has already
said that three of those are Greek.

### The shortfall is ruling 53's NEITHER outcome (ruling 63)

Ge'ez fails on the **ROME criterion, not the translation criterion.** Littmann's
*Deutsche Aksum-Expedition* IV is public domain, downloadable, and prints
Aksumite inscriptions in original script with German translation only — the
`verbatim_machine_english` profile exactly, in the region ruling 53 named as its
test. Every text in it that touches Rome is Ezana, which this corpus holds, or
Sembrouthes, disqualified because a Wikipedia editor attributed his English.
FINDING 38's supply problem, not FINDING 41's search problem.

**Ruling 53 designed a test and the test did not run.** NEITHER is not a third
result on the same axis as the other two; it is the statement that this tranche
produced no evidence about the axis at all. **F5's deferred vme ruling inherits
an experiment that was not performed, not a null result**, and the two are read
very differently by anyone deciding whether to keep the tier.

FINDING 45's genre seam is likewise untested in Africa: the Ge'ez route closed
on Rome before genre could be aimed at anything.

Falsifiable in the direction that matters: **name a Ge'ez text that touches Rome,
sits inside 27 BC to 1204 AD, and is printed in an open volume without an
English translation.**

---

## 2. The gloss-capable count, with its composition (ruling 62)

**3 of 8 declared, of which ONE is a translator's hedged IDENTIFICATION rather
than a disputed READING.** Never three equivalent cases.

```
jingjiao-stele-da-qin       a contested reading, with a critical apparatus
liangshu-qin-lun-funan      Hirth's `Fu-nan [Siam, Cambodja?]` -- TAKEN WITH A
                            DISCOUNT: 扶南 is not in doubt at all; what is
                            hedged is which modern country it answers to
raqosh-epitaph / others     from earlier tranches
```

The discount travels in three places and this is the third: the record's own
`reference_translation` and `notes`, the gold case's `why`, and here. The gloss
arm exists to see whether a model will render a *disputed text* confidently, and
the Liangshu case cannot see that, because nothing about its text is disputed.

**And the target of 8 is already out of reach by declaration.** FINDING 51:
1 declared + F4's 2 + F5 2 + F6 1 + F7 1 = 7, against 8, and no check compares a
tranche's declaration to its delivery. `check_delivery` prints *"18 slot(s)
left"* and answers a question nobody is asking — slots are plentiful,
declarations are four.

---

## 3. The two pre-registered predictions

Full readings are in `F4_RULINGS.md`. In brief:

### Ruling 55 — CONFIRMED in direction; its mechanism is not in the evidence

```
china-describes-rome-houhanshu   rank 4 -> 8   r@6 True -> False   dSim -0.0004
china-describes-rome-weilue      rank 5 -> 9   r@6 True -> False   dSim -0.0005
```

Both moved down, both left the top 6, neither falsification condition fired. The
ordering clause — `weilue` named as the likelier to fall — got **no test**: both
fell by exactly four places, preserving the one-rank gap.

The two pairs ruling 55 named lost **four times what any other top-20 pair
lost** (every other one lost a single place), which is a real differential in
the predicted direction. But `sim_target` did not move, `gap_vs_other_doc` did
not move, and `best_other_doc_chunk_id` is the same pre-F4 document before and
after. **The direction is confirmed, the concentration is confirmed, and the
attribution is unavailable.**

The only pair in the run whose competitor actually changed is
`probe-roman-embassy`, crowded by record 34 — the one clean instance of an F4
record displacing something, in a pair no ruling named.

### Ruling 61 — ONE of three, which is toward falsified

```
talang-tuo-sriksetra-park    -> seasia-06-kedukan-bukit            CORRECT
kedukan-bukit-saka-605       -> distractor-met-74991               WRONG
thorsberg-chape-niwajemariz  -> scandinavia-02-gudme-hoard         WRONG
```

Reported as 1 of 3 rather than rounded to a verdict, as the ruling required.

**Near-duplication is not symmetric.** The ruling predicted both directions of
the Srivijayan pair because it treated the relation as a property of the pair.
For `talang-tuo`'s query the other Srivijayan record is nearest; for
`kedukan-bukit`'s query a Metropolitan Museum object description is nearer, and
**beats the target outright** — `top_doc` is the distractor.

And `thorsberg-chape-niwajemariz`'s nearest chunk of any kind is the English
translation **of the record it is looking for**, at 0.5341 against the source
text's 0.3506. *29/30 is whether the RECORD was found; 22/30 is whether the
NON-ENGLISH TEXT was reachable* — with a number on it.

---

## 4. Ruling 66 — `vimose-runes` at rank 7

**The rank is accepted, FINDING 43's diagnosis for this pair is superseded, and
the query is not rewritten.**

Twenty-three archived runs with distractors, and
`arabia-04-jabal-dabub::original::000` is the nearest other document in **every
one of them**, with a gap that has moved by 0.001 across the rank falling from
3 to 7. `scandinavia-05-thorsberg-chape` — the record FINDING 43 says caused the
fall — **has never been this pair's nearest competitor**, and is not sitting on
it from the other side either.

The diagnosis was inferred from timing. The field that could have tested it was
in every archive and was not read.

**RULED OUT:** near-duplicate crowding by `scandinavia-05-thorsberg-chape`.
**NOT ESTABLISHED:** what did displace it — a gap in the archive, not a fact
about the corpus.

The pair is stable rather than decaying (thirteen chunks and five records
entered in F4 and it did not move), it stays reported, and the query is not
rewritten: a query rewritten until its pair re-enters the top 6 is
`skz-titulature`'s refusal in reverse.

---

## 5. What F4 added, and what it cost — ruling 54's first payout

**F3 could measure only the second half of this. That was the whole argument for
ruling 54, and this is the first tranche where both halves exist.**

### What it added — five records, five pairs, written in the same commits

```
silko-basiliskos                rank  1   yes
liangshu-qin-lun-rarely-seen    rank  1   yes
jingjiao-stele-coral-sea        rank  2   yes
cefu-yuangui-fulin-glass        rank  2   yes
adulis-throne-leuke-kome        rank 28   NO
```

**Four of five inside recall@6, three of them at rank 1 or 2.** None carries
`written_after_the_records_entered_the_index`, and that absence is the claim.

`adulis-throne-leuke-kome` at 28 is the miss, and it is in a congested
neighbourhood: `adulis-exports` sits at 15 and `aksum-trade-adulis` at 38, all
three pointing into Adulis material. It is also where the run reports two
`chunk_id` drifts, both on `africa-03-periplus-adulis` — counted, not failed on,
which is why pairs assert characters and not ids.

### What it cost — measured on the 33 pairs that existed before F4

```
SHARED 33 pairs   recall@6   26/33 = 0.788   ->   24/33 = 0.727
FLIPS             china-describes-rome-houhanshu   True -> False
                  china-describes-rome-weilue      True -> False
```

**Two pairs lost recall@6 and they are exactly the two ruling 55 predicted.**
Every other pre-existing pair held. Nine of the 33 changed rank at all; eight of
those nine moved with nothing about them changing but the number.

### The aggregate, which must not be read as either

```
                 pairs  recall@6           MRR@10
ALL                 44  0.727 (32)         0.566
BY UNIT             41  0.805 (33/41)      0.629
  archived_answer    8  0.125 ( 1)
  authored          20  0.800 (16)
  retrieval_probe   12  1.000 (12)
  translation_case   4  0.750 ( 3)
```

The F3 run had 33 pairs and 30 units. **This one has 44 and 41, eleven of them
new, six of them ruling 54's stamped debt pairs.** The totals are not comparable
in either direction and are printed here so nobody reconstructs them into a
trend. The shared-33 line above is the only before/after this run supports, and
the six stamped pairs may not be cited as evidence that any tranche improved
retrieval.

`muziris-cargo-akananuru` is at **319**. It has been the corpus's one genuinely
broken cross-lingual link since Block C and nothing in F4 touched it.

---

## 6. The instrument work

### Ruling 64 — the `corpus_version` deferral, decided

FINDING 36 handed one question to F4 by name. A recovered payload now rebuilds
what the `answers` row proves under **`recovered_corpus_identity`**, whose
`basis` is the literal `"recovered"` — neither of ruling 49's two values — and
whose hash map is `cited_record_hashes` and never `record_hashes`.
`corpus_version` stays in `ABSENT`, its reason rewritten from a deferral to a
decision pointing at the replacement.

**The name is the ruling.** `record_hashes` means the whole corpus,
`cited_record_hashes` is a subset by construction, and `corpus_moved` diffs
those maps by key — so the subset under the whole-corpus name would report every
uncited record as `vanished`. A true measurement producing a false sentence.

Adding a third `basis` to `sweep_corpus` was refused as a mid-block re-cut of
the field ruling 49 made decide what may calibrate the floor: **the fifth such
refusal in this block and the first outside `corpus_tiers.json`.** The
discipline is about the timing, not the file.

### FINDING 57 — a suite fixed in the commit that found it broken, reported broken ever since

`scripts/test_recover_baseline.py` has been **green since `e7d932e`**, and the
three blobs its guard reads are byte-identical from there to `HEAD`. F4 Part 1
wrote `RED`, Part 2 copied it, Part 3 wrote `STILL RED`, and each part budgeted
a step for work already done.

FINDING 36's remedy was to list the suite. It was listed in the block that holds
**commands** and not the block that holds **numbers** — the only one of eight
whose expected output was prose, and prose gets transcribed rather than compared.

**And the remedy, applied, wrote a number that was one short**: 55 from the
bridge, 56 on the host, the difference being the sqlglot assertion the bridge
skips. The rule is therefore: *a suite number in a state block names the commit
it was printed at AND the interpreter that printed it.*

### FINDING 58 — an enumeration is not a search

FINDING 46 went looking for `startswith("FAIL")`'s siblings and named four
harnesses. `scripts/` holds **eight** files that harvest guard names from a
suite's stdout. `mutate_cost` was **LIVE** — `ingest/test_cost.py` ends a red run
with `FAILED (n)`, so its BASELINE block would have harvested a phantom guard
`ED (n)` against the ledger suite, the instrument ruling 46 names as the only
place a curation-cost number may be read from. `mutate_recover`, `mutate_part7b`
and `mutate_distractors` were latent; the last has no `failures_from` at all,
the same three lines inlined in `run_suite()`, so every search for the defect
looked for a function name while the defect was in the code.

All four fixed. One shared matcher is owed.

### FINDING 59 — the rule names a timeout; today it was a disconnect

`mutate_cost.py` was started through the bridge, the workspace disconnected
mid-run, and it left a live mutation in `ingest/cost.py` making `trend_line`
report every tier as flat. Recovered with `git cat-file blob` written back as
bytes. **A harness restores its sources from inside its own process**, so the
45-second limit the runbooks cite was never the exposure. No suite would have
caught it; `git status --porcelain` did.

### FINDING 61 — the newline remedy reached five harnesses of nine

`scripts/` holds nine mutation harnesses. Five carried `_newline_of`; four still
applied their mutations with `write_text`, which translates a newline to
`os.linesep`. **`mutate_ranking` is the only harness whose sources do not share
a convention** — seven CRLF and `answer/translate.py` at LF — so there is no
platform on which it leaves them alone, and it is the harness FINDING 52's
seven-file measurement was taken on. The byte-safe restore only runs if the
process finishes, which FINDING 59 says cannot be assumed.

All four fixed before `mutate_ranking` was run. Third instance in two days of
one mechanism: **there is no moment in this project's workflow at which a
directory is enumerated**, so every finding of this family has been closed by a
person noticing.

`scripts/test_harnesses.py` is the answer to that — the harnesses checked as a
population, asserting only what FINDINGS 37, 52 and 58 already state in prose.
Its first run went red on `mutate_places`, which was **correct**: the check was
stricter than any written rule, in the file whose docstring cites FINDING 56 by
number for exactly that hazard. Narrowed to the filter; the stricter idea is a
counted line. Its second run was caught by `eval.test_answer_eval`'s FINDING 10
guard — the repository's one pre-existing directory check, which has been making
this argument since Block D about entry points and was never pointed at anything
else.

### FINDING 60 — the field that records the competitor that never moves

Across the 33 shared pairs: 9 changed rank, and in **8 of the 9** the target's
similarity, the gap, and the identity of the nearest competitor are all
unchanged. Something arrived in between, and the archive records only the
ceiling.

`best_other_doc_chunk_id` was added because *"the run recorded the number and not
the thing it was measured against"* — and it records the **best** competitor,
which is stable precisely because it is the best. Crowding happens in the
interval between the target and that ceiling, and the interval is what is not
stored.

**So FINDING 43, ruling 55, ruling 61 and F4's opening decision have all
attributed rank movements to specific arriving records using an instrument that
cannot see a crowder.** Every one of those attributions was inferred from what
arrived in the same tranche. The remedy is cheap — record the documents ranked
between the target and `best_other_doc_chunk_id`, which `rerank_top_chunk_ids`
already does for the rerank arm — and it is the item that makes FINDING 43
testable for the first time.

---

## 7. The C2 FUSED arm — NOT RUN, deliberately (ruling 65)

```
BASELINE     RUN.  44 pairs, 41 units, index 473 chunks.
C2 FUSED     NOT RUN.
```

`eval/gold/query_renderings.json` has no entries for the eight pairs ruling 54
added in Part 2. The fused arm answers no question F4 asked — both predictions
are denominated in BASELINE — rebuilding the renderings costs chat calls, and it
would move `renderings_digest` inside the commit reporting the run, which is
FINDING 47 four days after FINDING 47.

**Named, never merely subtracted.** The eight pairs' missing renderings are a
debt on F5.

---

## 8. Suites and harnesses, on the host, at this tree

```
ingest.verify                     All integrity checks passed.  35 documents,
                                  82 chunks, 23 parallel pairs
ingest.test_fidelity               58 passed, 0 failed
ingest.test_cost                   64 passed, 0 failed
eval.test_answer_eval             410 passed, 0 failed
eval.test_ranking_check           253 passed, 0 failed
answer.test_answer                150 passed, 0 failed
ui/test_build_ui_data.py           19 passed, 0 failed
scripts/test_recover_baseline.py   56 passed, 0 failed   (44 before ruling 64;
                                   55 through the bridge, which skips sqlglot)
scripts/test_harnesses.py          33 passed, 0 failed   (new, FINDING 61)

scripts/mutate_recover.py          17 verified   (11 before ruling 64)
scripts/mutate_cost.py             51 verified
scripts/mutate_part7b.py           18 verified
scripts/mutate_distractors.py       6 verified   (schema and sources restored)
                                   -- 92 mutations, no BASELINE line, no
                                      UNVERIFIED, no phantom guard
```

`mutate_ranking` (108), `mutate_fidelity` (46), `mutate_part8` (94) and
`mutate_ui_places` (6) have still not been run since `a5c0ae6`. Their `EXPECTED`
labels were checked statically against what their suites actually print (254 of
254 still printed) and every mutation target still resolves, so no `MISS` from
FINDING 37's family is waiting. **`mutate_ranking` was repaired before being
run** — see FINDING 61.

The gold answer set is **44 cases**: 30 answerable, 8 correctly_refusable, 6
refusable_with_gloss, every region at or above G4's minimum of 3.

---

## 9. Cost, per tier, and the fence around it (ruling 46)

```
verbatim_machine_english   n=3   mean  4.0 min   NOT A TREND (floor 10)
verbatim_with_provenance   n=8   mean 10.7 min   NOT A TREND (floor 10)
```

**NOT YET A COST CLAIM.** The declared mix is unmet, both n are below the floor,
and the report says so itself. **The aggregate per record is not read** — ruling
46 forbids it and the allocation biases it downward by construction.

One line from the phase decomposition is worth carrying because it is a
measurement of a finding rather than of a budget: of
`verbatim_with_provenance`'s 85.5 minutes, **61 are `text_capture`.** FINDING 48
said the phase has a floor no tooling removes and FINDING 53 said the floor is a
person reading a page image. That is what the floor looks like in minutes.

Five retired rows are named and counted in no mean, and
`africa-04-silko-talmis` is the first **reinstated** row under ruling 59.

---

## 10. Still owed — F5's list

**One re-cut, with two tranches of evidence, carrying five instrument changes:**

1. **ruling 53's deferred vme allocation ruling** — inheriting an experiment
   that did not run (ruling 63), which is not the same inheritance ruling 53
   planned for.
2. **ruling 58's per-region language rule** — three of Sub-Saharan Africa's four
   source-language records are Greek and no check can see it.
3. **FINDING 51's per-sub-tranche gloss delivery check** — a quota declared per
   tranche and checked only in aggregate can be missed one tranche at a time
   with every check green.
4. **FINDING 55's translation-search boundary on the vwp tier** — the tier that
   admits it could not find an English translation is the only one that writes
   down where it looked.
5. **ruling 62's distinction between a contested READING and a hedged
   IDENTIFICATION** — both look identical to any checker and they are different
   evidence.

**Three more, new from Part 3:**

6. **FINDING 60's interval recording** in the ranking archive — the item that
   makes FINDING 43 testable at all, and the reason four attributions in this
   file are stated as unavailable rather than as findings.
7. **FINDING 58's shared matcher** — nine copies of one three-line rule is
   FINDING 14's shape inside the machinery built to catch FINDING 14's shape.
   `scripts/test_harnesses.py` now stops the copies drifting; it does not make
   them one copy.
9. **A BASELINE block for `scripts/mutate_distractors.py`** — the only harness
   without one, and the one that mutates the SCHEMA. Counted rather than
   asserted by the new check, because a BASELINE block has never been written
   down as a requirement: it was added to four harnesses across F1 to F3 and to
   this one never. Fourth instance of FINDING 61's family, not a new defect.
8. **ruling 65's renderings debt** — the eight Part 2 pairs, before any fused
   arm can include them.

**And the coverage gap, which is a different kind:**
`scripts/mutate_part8.py` does not mutate `eval/test_answer_eval.py`, so three
data-driven guards there — the refusal-falsification check, the
quoted-from-original quota, and the gloss-hedge check — have no mutation proving
they can fail.

**Carried, untouched:** `mutate_ranking`/`places` BASELINE blocks still
unexercised (`recover` and `cost` both ran clean today); ruling 40's
`article_added` still reads 0; `ingest/test_sql.py` has never run with sqlglot
AND the database; `verse` and `documentary` confidence profiles still at n=1.

**Discharged:** the third distinct UTC date three rules wanted. Block F now has
four.

---

# The sentences that travel, from F4

**Ruling 53 designed a test and the test did not run, so F5 inherits an
experiment that was not performed rather than a null result.**

**The field was added so the run would record what a number was measured
against, and it records the one competitor that never moves — so three tranches
of crowding claims were made against an instrument that cannot see a crowder.**

**Two Old Malay inscriptions a year apart from one polity see different
neighbourhoods, and only one of them sees the other.**

**The nearest chunk in the index to a query asking for Proto-Norse is the
English translation of the record it is asking about.**

**A green suite carried as red is a suite whose next real failure reads as the
old one.**

**The remedy for a defect nobody had searched for was a search, and the search
was performed by listing the files that were already open — which is why the
only live instance was the one that was not on the list.**

**The restore lives inside the process, so every argument about how long the
process is allowed to live is an argument about the wrong thing.**

**A prediction confirmed in direction and unattributable in cause is two
results, and writing it as one is how a mechanism becomes folklore.**
