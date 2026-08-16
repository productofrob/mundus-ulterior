# Block C — the rulings, and what they cost

_Four on 2026-08-14; two more on 2026-08-16, both forced by the first working
measurement of the 450-chunk rung._

_Ruled 2026-08-14 by the project owner, against the per-pair evidence in
`eval/ranking_runs/20260814T084042+0000-retrievable_chunks.json` (57) and
`…T133556+0000-retrievable_chunks_with_distractors.json` (450). Every number
below was recomputed from those two files, not carried from a document._

These four were the critical path. `claude/phase2-block-c-plan.md` argued that
Block C's blocking work is decisions rather than engineering; this file is the
decisions. Nothing here is a recommendation — each is settled, and each says what
it costs, because three of the four make the gate easier to reach.

---

## Ruling 1 — a multi-target query is ONE unit with N acceptable targets

**Scored on its best acceptable target.** A ranking that finds one of three
targets and one that finds all three are no longer the same result only because
the metric happens to count rows.

### The correction that came with it

`claude/phase2-block-c-plan.md` states the post-ruling figure as **26/30**. That
collapsed the Muziris query and left the other shared query — *"How did Chinese
sources describe the Roman empire?"*, two pairs at ranks 4 and 5 — expanded.
Applied consistently to both, the arithmetic at 450 chunks is:

```
per pair, today                 26/32 = 0.812
collapse Muziris only           26/30 = 0.867     <- the plan's figure
collapse both, consistently     25/29 = 0.862     <- the ruling
```

Collapsing the China query removes a unit and a hit, so it lowers the ratio. The
ruling is still worth making — but it is worth making for the reason it was
argued, not for five thousandths of recall.

### What the gate now requires

At 29 units, **≥0.95 permits at most one miss** (28/29 = 0.966; 27/29 = 0.931).
Four units miss today:

```
unit                       rank   status
aksum-trade-adulis           35   in a top-50 rerank window
au-khao-sam-kaeo             17   in a top-50 rerank window
adulis-exports               15   in a top-50 rerank window
tc-frankincense-harvest      11   in a top-50 rerank window
```

**At least three of those four must be fixed for G2 to pass.** The ruling alone
does not reach the gate; it makes the gate reachable, which is a different claim
and the one to write down.

> **Amended 2026-08-14, later the same day.** The English→Tamil probe below was
> added, so the set is **33 pairs over 30 units** and the gate again permits at
> most one miss (29/30 = 0.967). The new pair is **unmeasured** — it was written
> after the last run. If it misses, which is what its own note expects, the
> requirement becomes **four of five fixed, not three of four**.
>
> That is the ruling's arithmetic getting *harder* because of an instrument
> added to watch the thing the ruling stopped counting. It is the correct
> direction and the reason to add the probe before C3 rather than after.

### What it costs, stated plainly

The two targets that stop being counted are `muziris-cargo-papyrus` (rank 109)
and `muziris-cargo-akananuru` (rank 309). The second is the corpus's **one
genuinely broken cross-lingual link** — an English query that cannot reach an Old
Tamil passage from three hundred ranks away. B1's own notes named "weakening what
the metric means" as the thing to refuse, and this ruling does some of that.

**Therefore, mandatory and non-negotiable:**

1. Every unit reports **coverage** alongside recall — how many of its acceptable
   targets sit in the top 6. It is reported, never gated. Today: Muziris **1/3**,
   China **2/2**.
2. The Old Tamil result is a **standing finding** that appears on the same page
   as any G2 number, in words, every time. A gate that passes while a known
   failure is uncounted is only honest if the failure is printed beside it.

---

## Ruling 2 — the four `translation_case` pairs accept the document's own published translation of the same section

An English query that retrieves the published English of Periplus §29 has done
something correct, not something wrong. The pair was written to test
cross-lingual reach; it was not written to declare a faithful translation of the
right section a miss.

**Still a miss** if retrieval lands on a *neighbouring* section of the same
document — §27–28 rather than §29. That was the discrimination
`tc-frankincense-harvest` was authored to make, and it survives.

### Why this does not weaken cross-lingual measurement

Cross-lingual reach is measured by the four `lang_pool: non_english` probes,
where an English translation is **excluded from the candidate pool by
construction** and cannot satisfy the pair. Those four (`probe-frankincense-kane`,
`probe-adulis-ivory`, `probe-roman-embassy`, `probe-roman-provinces`) all rank 1
at 450 chunks. The `translation_case` cohort measures something else — whether
retrieval reaches the right *section* — and after this ruling it measures that
and nothing else.

### The evidence gap this ruling exposed

The premise behind it — *"the chunk beating the target is always that document's
own English translation"* — is **not recoverable from either archived run**.
`run_ranking_check.py` recorded `sim_best_other_chunk` and never which chunk it
was. The claim had to be re-derived by hand in B5 and could afterwards only be
recalled.

Fixed on 2026-08-14: `PairResult` now carries `best_other_chunk_id` and
`best_other_doc_chunk_id`, asserted in `eval/test_ranking_check.py`. A chunk id
carries its own role and document, so the next run settles the question offline
and permanently.

**Consequence for planning: the effect of this ruling on recall is currently
unknown and must not be assumed.** `tc-frankincense-harvest` sits at rank 11 with
`gapAny −0.178` against `gapDoc −0.053`, so the chunk beating it is a sibling in
its own document — but whether that sibling is §29's English or §27–28's is
exactly what was never recorded. It may become a hit under this ruling. It may
not. **The next run answers it; nothing before then may claim it.**

---

## Ruling 3 — the gap is measured PRE-rerank, recall POST-rerank

G2's *"score gap wider than baseline, same pairs"* stays a statement about
embedding similarities, which is the quantity the baseline recorded and the
quantity the whole W2b distractor curve is denominated in. Reranking changes
ranks, not similarities; recomputing the gap on reranker scores would compare two
different quantities and call the comparison a gate.

- **gap** — computed on embedding similarities, before reranking, against the
  recorded baseline. Comparable by construction.
- **recall@6** — computed after reranking. That is the intervention's whole
  purpose.
- **reranker-score gap** — recorded under its own name, reported, and **never**
  compared to the baseline number.

Both halves are printed together, with one line saying which was measured where.
The failure this forecloses is G2 being assessed against two incompatible
readings of its own checklist.

---

## Ruling 4 — "wider than baseline" reads `gapDoc`

```
              57        151       450
gapDoc      +0.025    +0.023    +0.020
gapAny      -0.008    -0.009    -0.012
```

`gapDoc` — the target against the best chunk in any *other* document — is
positive at every rung, so "wider" is a claim that can be true or false.
`gapAny` is negative at every rung, **including at 57 chunks before any
distractor existed**; widening a negative number is satisfied by moving from
−0.012 to −0.005, which is not a gap and would let the gate pass on a
technicality.

`gapAny` is still recorded and still reported. It is a diagnostic, not the
criterion — and note that **ruling 2 changes it directly**, because the chunk
beating a `translation_case` target is the chunk that ruling now accepts.

---

---

## Ruling 5 — C2 returns to the critical path (2026-08-16)

**Ruling 3 has a consequence nobody stated when it was made.** It fixed the gap
to pre-rerank embedding similarities so the number stays comparable to B2's
baseline. That was right for comparability. It also means:

> A cross-encoder cannot move this number. Reranking reorders candidates; it does
> not alter cosine similarities. **C3 can satisfy G2's recall criterion and
> cannot touch its gap criterion, ever.**

Measured on the same 32 pairs that existed at B2:

```
B2 baseline,  57 chunks    gapDoc  +0.0249
today,        57 chunks    gapDoc  +0.0249     identical, two days later
today,       450 chunks    gapDoc  +0.0196
```

The gap at 450 is **narrower** than baseline. The criterion is not merely unmet;
it points the wrong way, and no amount of reranking will turn it round.

**Ruled: C2 comes back onto the critical path.** Hybrid lexical+dense is the only
planned intervention that changes what produces the score, so it is the only one
that can widen a pre-rerank gap. `claude/phase2-block-c-plan.md` demoted it to
*"optional, behind C3, only if still short"*; that demotion is withdrawn. Ruling
3 and G2 are otherwise unchanged.

**State the cost, as with ruling 1.** C2's own gotcha is unchanged and real:
`tsvector` will not tokenise Literary Chinese at all, so it needs character
n-grams and a per-script decision; and five of the six original misses were
English queries against non-English targets, where there is no shared vocabulary
for a lexical index to recover. **C2 may widen the gap while doing nothing for
recall.** That would still be a G2 criterion met — and it must be reported as
what it is, not as evidence that retrieval improved.

## Ruling 6 — the canary is a distractor, and the comment was wrong (2026-08-16)

`scripts/schema-b4-distractors.sql` said the containment canary *"carries NO
embedding … is invisible to both views … cannot perturb a ranking run. It is a
containment fixture, not a distractor."* It is inserted
`eligible_for_retrieval = true`, so `run_embed` embeds it; it has been one of the
450 since B4; and on 2026-08-16 it was the best competing document for
`tc-nabataean-epitaph`, moving that pair's gapDoc from +0.146 to +0.107.

**Ruled: it stays a distractor.** It is declared `is_distractor = true` and is one
of the 393 by design — a canary held back by eligibility would prove nothing
about the distractor flag, which is the whole reason it exists. The false comment
is struck in the schema and in `ingest/test_distractors.py`, whose docstring said
the same wrong thing while its own body recorded the truth.

No assertion was added, because the ones needed already existed: a vectorised
canary is INVISIBLE to `retrievable_chunks` and `citable_passages`, and VISIBLE
to `retrievable_chunks_with_distractors`. **Containment held throughout.** What
failed was the prose, and it failed in both directions at once —
`BLOCK_C_START.md` counted the canary among the 450 on the same day the schema
said it could not be there.

Effect on the gate: **none that changes a verdict.** Backing its influence out
entirely moves the 32-pair gapDoc from +0.0196 to roughly +0.0208, still short of
+0.0249, and `tc-nabataean-epitaph` is a hit at rank 2 either way. It is recorded
so it cannot be raised as an objection after the gate is assessed.

## The fifth item, which is a task and not a choice

**Add an English→Tamil cross-lingual probe** to `eval/gold/retrieval_probes.json`
with `lang_pool: non_english`. The four existing non-English-pool probes cover
Greek, Chinese and Parthian only. After ruling 1, the worst cross-lingual result
in the corpus — the Old Tamil link — rests entirely on an archived pair that no
longer counts toward the gate and was never designed to test cross-lingual reach
in the first place.

Cost: one query in the next batched embedding request. **Do it before C3**, so
the reranker is measured against a probe that exists rather than credited with
one that does not.

**Landed 2026-08-14** as `probe-tamil-akananuru-en` in both files — the probe in
`retrieval_probes.json` where cross-lingual probes live, and the pair in
`ranking_pairs.json` so it is actually measured. Query:

> *a Tamil poem describing Yavana ships arriving at Muciri with gold and
> departing with pepper*

Its partner `probe-tamil-akananuru` asks the same record in its own language and
ranks 1. This one asks in English against a pool with no English in it. It has
no rank yet; the next run gives it one, and the gate's arithmetic is restated
then rather than guessed at now.

---

## How the rulings are implemented, so the next reader does not have to infer it

- **The unit is declared, not inferred.** Each pair may carry `unit_id`; absent,
  a pair is its own unit. The loader asserts both directions — one unit means
  one query text, and pairs sharing a query text must share a unit. A unit
  inferred by grouping identical strings would change the gate's denominator the
  moment somebody edited a query by a character, with nothing to say so.
- **The alternate is computed, not copied.** A pair carrying
  `accept_aligned_translation` gets its alternate from `answer.align.pair_chunks`
  at scoring time, and only where that module reports the ground as `section`.
  Positional (`index`) alignment admits nothing: two texts numbered
  independently pair by coincidence of counting, and accepting on that would
  admit a *neighbouring* section, which this ruling says is still a miss. The
  ground is recorded per pair either way, because "none admitted" and "none
  asked for" are different facts about a run.
- **Nothing overwrites the baseline.** `rank`, both gaps and the cohort table
  keep their pre-Block-C meaning; `rank_accepted`, `recall_at_6_accepted` and
  the unit table sit beside them. Every run since B2 stays comparable, and the
  rulings can be re-argued against the same archive rather than only against
  runs made after them.

Seven mutations cover the above in `scripts/mutate_ranking.py` — 21 in total, up
from 14. Three of them break the gate's denominator specifically, because that
is the one quantity in the check that decides whether W3 starts, and the plan
itself already got that arithmetic wrong once.

---

## What travels with every G2 number, without exception

1. The curve was built on **English-only padding**. Seams 1 and 2 (Periplus,
   Strabo/Pliny/Ptolemy) were dropped on a time-box, so the twelve Greek-target
   pairs faced no competing Greek at any rung. A flat curve supports
   *"English-target retrieval survives an eightfold index of similar English
   competition"* and supports nothing about non-English retrieval at scale.
2. `gapAny` was negative before any padding existed. The quantity W2b was built
   to watch erode had no positive value to erode from.
3. The gate is reached over **29 units, not 32 pairs**, and the Old Tamil link at
   rank 309 is a standing failure the gate does not cover.

---

## Ruling 7 — ruling 2 does NOT extend to the pairs C3 displaced (2026-08-16)

The 2026-08-16 rerank runs displaced `muziris-cargo-periplus`,
`china-describes-rome-weilue`, `china-describes-rome-houhanshu` and
`aksum-trade-adulis`, and in every case **the chunk that beat the target is that
same document's own published English translation** — for the Muziris pair, the
same section index. Across the run, of the chunks outranking a target inside the
top 6: 38 translations, 12 originals, 3 distractors.

That is ruling 2's premise, arriving in a cohort ruling 2 does not cover. The
obvious move is to let those pairs declare `accept_aligned_translation` too.

**Ruled: no.**

**Not because the argument is bad.** On ruling 2's own reasoning it is decent:
cross-lingual reach is measured by the four `lang_pool: non_english` probes,
where English is excluded from the candidate pool by construction, and all four
rank 1 both pre- and post-rerank. Extending would not touch that instrument.

**Because of what it would cost and when it was proposed.** Extending would very
likely take post-rerank recall from 26/30 to 29 or 30 of 30 — G2's recall
criterion met. The extension is available precisely because it rescues a failing
gate, and a ruling made on that basis is fitting to the gold set rather than
measuring against it. Worse, the resulting gate would barely test the thing this
corpus exists for: if an English translation satisfies an English query, every
English query can be answered by an English chunk, and **4 units of 30 would be
the entire cross-lingual test.** Ruling 1 already reached the gate partly by no
longer counting the two hardest targets. This would be the second narrowing in
one block, and B1's refusal — *"weakening what the metric means"* — governs.

**The conditions under which it could be revisited**, so this is a ruling and not
a veto: it is argued from the pairs' purpose rather than from a score; it is
applied to the unreranked configuration as well; every affected number is
re-measured; and it is reported as a ruling change with its cost, never as an
intervention succeeding.

## Ruling 8 — a section is ONE retrievable record, canonically the original (C2a)

The index holds each passage twice, as `::original::` and as `::translation::`,
and the two compete for the same six slots. Three of the six chunks above
`muziris-cargo-periplus` are Periplus translations; one is the translation of
the target's own section.

**Ruled: retrieval collapses aligned siblings into one result.** One row per
document-section, admitted only where `answer.align.pair_chunks` reports
`ground=section` — the same standard ruling 2 set — and the row's chunk is
**the ORIGINAL**, with its translation carried alongside for display.

### Why this is not ruling 7 wearing a different hat

Ruling 7 refuses a change to **what the metric COUNTS**. This is a change to
**what the SYSTEM RETURNS**, measured by an unchanged metric: after it, the top
6 literally contains `southasia-02-periplus-muziris::original::003`, and `rank`
still means what it has meant since B2 — the position of this pair's chunk in
what retrieval returned. Nothing is accepted that was not returned.

### The objection, stated because it is real

**Canonicalising to the original is the choice that turns these misses into
hits, and it was made after seeing that.** The defence must therefore not be the
score, and is not: a sourcebook whose stated purpose is the world beyond Rome
*in its own sources* presents the Greek, Chinese or Tamil record as the record.
The alternative — canonical = whichever member happened to rank higher — would
make the citable text language-dependent on retrieval noise, which is plainly
wrong for this product whatever it did to the number.

### What it costs, stated plainly

1. **"Top 6" changes meaning: six RECORDS, not six chunks.** A collapsed top 6
   covers more underlying text than an uncollapsed one. That is a real change in
   what the gate proves and travels with every number produced under it.
2. **It cannot move the gap criterion.** Ruling 4 reads `gapDoc`, the target
   against the best chunk in any *other* document; collapsing within a document
   does not touch it. Gaps are computed on the UNCOLLAPSED hits, exactly as
   ruling 3 keeps them pre-rerank. C2a is a recall intervention only, and the
   gap remains C2's.
3. **Recorded beside, never over**, following rulings 2 and 3: `rank_collapsed`
   and `recall_at_6_accepted_collapsed` sit next to `rank` and `rank_accepted`.

## Ruling 9 — `sole` is a ground, and it collapses (2026-08-16)

`scripts/probe_sections.py` measured what C2a can reach: of fifteen documents
holding a translation, **three align on `section` and twelve are one original
and one translation on `index`**.

`index` at n=1 is a **mislabelled ground**. The stated reason to distrust it —
*"two texts numbered independently pair by coincidence of counting"* — is vacuous
when the count is one: there is no neighbouring section to confuse, and exactly
one possible pairing. It is the same defect this repository has paid for before
in `not_in_top_20` measured at k=50: a name that describes something other than
what it names.

**Ruled: the unambiguous 1:1 case gets its own ground, `sole`, and ruling 8's
collapse admits it.** A document contributing exactly one aligned group, with
exactly one member, under `index`, is `sole`. It is relabelled in
`retrieve/collapse.py` and NOT in `answer/align.py`, so ruling 2 and the answer
path are provably untouched by it.

**Ruling 2 does not admit `sole`.** Collapsing is a change to what the system
returns; accepting an alternate is a change to what the metric counts, and
ruling 7 refused that. The line stays where it was drawn.

### What it costs, and the condition it is ruled in under

It is likely to take the gate from 28/30 to 29/30, and **it is available because
it does.** It would also fold `southasia-01-akananuru-149`, so the Old Tamil link
at rank 309 — the corpus's one genuinely broken cross-lingual link, which ruling
1 requires printed beside every G2 number — would be reported as **found at rank
1**, on the strength of its English.

**Therefore, mandatory and non-negotiable, as with ruling 1's coverage:**

**`recall@6 via the original text` is computed and reported beside every G2
recall number.** A unit counts only if one of its acceptable targets reached the
top 6 through its ORIGINAL rather than through its translation. No
translation-mediated intervention — ruling 2's alternates, C2a's collapse,
`sole`, or a reranker preferring English — can inflate it. The gate's number
says whether the record was found; this one says whether the non-English text
was reachable, which is what this corpus exists to demonstrate. Both travel
together, always.

## Ruling 10 — C2 is QUERY TRANSLATION, not hybrid lexical+dense (2026-08-16)

The gold set already held the controlled comparison, and the 2026-08-16 runs made
it legible:

```
target                              native-language query    English query
eastasia-01-weilue::original::000   probe-chinese-weilue   1  china-…-weilue      5
southasia-01-akananuru-149::…::000  probe-tamil-akananuru  1  muziris-…-akananuru 309
southasia-02-periplus-muziris       probe-greek-muziris    1  muziris-…-periplus  5
persia-01-skz                       probe-parthian-skz     1
```

**Every non-English target ranks 1 when the query is in its own language.** The
index is not the problem, the passage embeddings are not the problem, and the
reranker is not the problem. **The bottleneck is the language of the QUERY.**

C2's original justification has been undermined twice: a lexical index over an
English query boosts the document's English sibling — the chunk already beating
the target (C3's evidence) — and the misses are not vocabulary-mismatch failures
at all (this run's evidence).

**Ruled: C2 becomes query translation.** The English query is translated into the
target languages and searched with both. It is supported by four probes rather
than argued from first principles; `answer/translate.py` already exists; machine
translation is named in the project's own scope; and — unlike C2a and C3 — **it
changes what produces the score, so it is capable of widening `gapDoc`**, which
is the entire reason ruling 5 put C2 back on the critical path.

**Stated risks, before anything is built:** a mistranslated query is a new
failure mode with no baseline and no guard; translating into eight target
languages multiplies queries per pair and needs a fusion rule that is declared
in advance, not chosen from results; and a translated query that succeeds proves
the pipeline works, not that the retriever is cross-lingual — which must be said
in the same breath as any number it produces.

**To be designed and ruled on before implementation.**

## Ruling 11 — the record declares which text is primary, and it already does (2026-08-16)

`sole` took the collapse from 13 sections to 24 and recall from 28/30 to
**25/30**. Three units that were hits at rank 1 vanished entirely:

```
au-hoby-silver      1 -> None    expect_lang en   "Roman silver table service"
au-silla-glass      1 -> None    expect_lang en   "Syrian workshop origin"
au-oc-eo-medallion  1 -> None    expect_lang en   "imitating a Roman aureus…"
```

All three name the ENGLISH chunk. Ruling 8 canonicalises to the original, so
their targets were folded away while the record was returned at rank 1 as a
chunk the pair does not name.

**The unstated consequence: `original` and `translation` do not mean the same
thing in every record.** For the Periplus the original is the substantive Greek.
For a Danish silver hoard the original is a 110-character findspot caption and
the English description is the record.

**Ruled: the collapse canonicalises to the record's PRIMARY text, and which text
is primary is derived from `source_type`.**

```
literary_text, inscription   primary = original      the source text IS the record
find_record, coin_record     primary = translation   the object is the record; both
                                                     text fields are curatorial
```

### Why this is a derivation and not a hand-assignment

**No seed record is edited. Nothing is authored. Nothing is labelled after the
fact.** `source_type` was written at ingest, and the distinction it draws here
is already stated in `ingest/fidelity.py`, which has carried `FIND_TYPES` —
*"source types where the record describes an object rather than carrying text"* —
since Part 3, with `classify_translation` saying in as many words that for a
find record this field *"is a curatorial description, not a translation"*.

The rule is therefore imported from `ingest.fidelity`, never redefined here: one
definition in this repository rather than two that agree until they do not. It
predicts all three failures without having been fitted to them, and it was
available to be written before the run that exposed them.

### Consequence for ruling 9's companion

`recall@6 via the original text` asks whether a genuine SOURCE TEXT was reached
without going through its rendering. A find record has no source text, so
reaching it through its curatorial description is not a shortcut and is not
counted as one. The companion counts a unit as bypassed only when the record's
primary IS the original and the entry was the translation.
