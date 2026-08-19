# C2 — query translation: the rulings, and what each costs

_Drafted 2026-08-16 against the repository at `695a06b`. Every count below was
computed from `eval/gold/ranking_pairs.json` and from the code named beside it,
not carried from a document. Rulings 12–14 and 16–19 are settled by the evidence
cited under each. **Ruling 15 was the one genuine choice; it was ruled 15b by
the project owner on 2026-08-16 and the harness is built to it.**_

Numbering continues `BLOCK_C_RULINGS.md`, which ends at 11.

---

## Three corrections to `C2_START.md`, before anything is designed on it

**A. The control is misnamed, and it has five members, not four.**

`C2_START.md` design constraint 3 reads: *"The four `lang_pool: non_english`
probes are the CONTROL and must not improve. They already query in the target
language and rank 1."* Two separate things are conflated:

```
queries already IN the target language   query_lang != en   lang_pool: None
  probe-greek-muziris            grc
  probe-chinese-weilue           lzh
  probe-tamil-akananuru          oty
  probe-parthian-skz             xpr
  probe-muziris-ports-grc        grc     <- absent from C2_START's table

pairs carrying lang_pool: non_english    query_lang == en   all six
  probe-frankincense-kane        -> grc
  probe-adulis-ivory             -> grc
  probe-roman-embassy            -> lzh
  probe-roman-provinces          -> xpr
  probe-pepper-cargo             -> grc
  probe-tamil-akananuru-en       -> oty
```

These are disjoint sets. The `lang_pool: non_english` pairs are **English
queries with English excluded from the candidate pool by construction** — they
are not a control, they are the six pairs C2 is most directly aimed at. The
control, if there is one, is the five native-language queries.

**B. `probe-muziris-ports-grc` is missing from the evidence table.** The table in
`C2_START.md` shows four native-language targets at rank 1. There is a fifth
Greek query against the same document, and it belongs in any statement of the
form *"every non-English target ranks 1 when queried in its own language"*.

**C. A fourth design constraint was not named: what the reranker receives.**
`run()` passes `p.query` to `rerank_documents` and keys `rerank_cache` on
`(p.query, langs, roles)`. C2 introduces a second candidate query text per pair,
and nothing in `C2_START.md` says which one the cross-encoder sees. Ruling 16
settles it.

---

## Ruling 12 — the language set is derived from the INDEX, never from the pair

Every query is rendered into **every non-English language present in the searched
view**, obtained at run time from `SELECT DISTINCT lang FROM {view}`. The
query's own text is always one of the variants.

No pair attribute may be read when choosing what to render into — not
`expect_lang`, not `expect_doc`, not `lang_pool`, not `region`, not
`expect_text_contains`. This is the leakage trap and it is the one that would
invalidate every number in the run.

```
non-English languages in the corpus   grc lzh oty xpr xna xsa gmq-pro   = 7
distinct queries in the gold set                                        = 30
renderings, uniform rule                25 en x 7  +  5 non-en x 6       = 205
```

### Two alternatives, refused, and why

**Per-pair selection from `expect_lang`.** Using the answer to find the answer. A
run built that way measures nothing and cannot be repaired afterwards.

**Two-stage selection: retrieve in English, then render into the languages of the
top-k.** Gold-blind, and roughly a third of the cost. Refused because it makes
the language set a function of the English retrieval that C2 exists to repair:
the pairs it fails worst are exactly the pairs whose target language is least
likely to appear in an English top-k. `muziris-cargo-akananuru` sits at rank 309;
a rule seeded from the top-25 would never have proposed Old Tamil for it.

### What it costs

205 chat calls, once. Nine of the 33 pairs — the whole `authored` cohort, every
one a find record with `expect_lang: en` — will be searched with seven renderings
that cannot help them. That is not waste to be optimised away; it is the price of
a rule that cannot see the answer, and the `authored` cohort's recall under C2 is
the measurement of what that price is.

---

## Ruling 13 — the fusion rule is MAX per candidate, declared before any run

For a candidate chunk `c` and variants `v`:

```
score(c) = max over v of cosine(q_v, c)
```

The fused ordering sorts on that score. `gapDoc` and `gapAny` are computed from
it, in cosine units, pre-rerank — ruling 3 unchanged. The variant that produced
the winning score is recorded per pair as `fused_from_lang`, reported and never
gated.

**The max is exact here, and that is not a general property.** `SEARCH_K is
None`, so `_search_depth()` returns `n_index` and every variant's search returns
the entire filtered view. There is no truncated list, so no chunk is missing from
a variant's results with an unknown similarity, and the max is a true max rather
than a max over survivors. If `SEARCH_K` ever becomes a number, this ruling
silently becomes biased — the harness must assert `SEARCH_K is None` at the point
of fusion and refuse to fuse otherwise.

### Two alternatives, refused

**Mean.** A target in one of eight languages scores well on one variant and
poorly on seven. Averaging penalises precisely the case C2 exists to fix, and it
would make the intervention look worst where it works best.

**Best-query-wins.** Requires a criterion for picking one variant's whole
ranking. Every gold-blind criterion available — top-1 similarity, score spread —
is itself a retrieval decision that would need its own baseline and its own
measurement. It is a second intervention wearing the first one's name.

### The comparability question, stated rather than assumed

The B2 baseline gap is a max over one variant; the C2 gap is a max over eight.
Both are cosine similarities between a query embedding and a chunk embedding —
the same quantity on the same scale, which is what ruling 3 was protecting. But
they are different order statistics, and a max over more samples is larger in
expectation for **every** chunk, target and distractor alike. The gap is a
difference of two such maxima, so it is not inflated by construction — but that
argument is a claim about the arithmetic, not a measurement. Ruling 14 is how it
gets measured.

---

## Ruling 14 — every C2 run reports both arms, and the C2 claim is made against the same-run English-only arm

A C2 run computes, on the same index, the same day, the same pairs:

- the **single-variant** arm — the query's own text alone, which is the
  configuration adopted on 2026-08-16;
- the **fused** arm — ruling 13.

G2's criterion is *"score gap wider than baseline"* and the baseline is B2's
`gapDoc +0.0249`, so that comparison is made and reported. But B2 was recorded at
**57 chunks** and the run is at **450**, where the same configuration reads
`+0.016`. A fused gap that beats `+0.0249` while sitting below the same-run
single-variant arm is not evidence that C2 widened anything, and must not be
printed as if it were.

Both numbers, on the same line, every time. Cost: nothing — the single-variant
arm is the run that already exists.

---

## Ruling 15 — RULED 15b. What the five native-language queries are for

Under ruling 12 a Greek query is rendered into the six other non-English
languages. So the five native-language pairs are no longer untouched, and
`C2_START.md`'s *"if those four move, the harness is doing something other than
what it says"* is no longer available for free. Two ways to have a control, and
they are not the same instrument.

### 15a — invariance by construction

Translation applies only where `query_lang == "en"`. The rule reads the query,
never the target, so it is gold-blind. The five native-language pairs are then
identical between the two arms **by construction**, and the harness asserts it:
any difference at all is a bug in the harness, full stop.

```
renderings   25 x 7 = 175        (30 fewer calls)
control      hard: byte-identical rankings, asserted
cost         C2 is never exercised on a non-English query, and the exemption is
             an asymmetry someone will later have to justify
```

### 15b — uniform rule, weaker assertion

Every query is rendered into every index language but its own. The five native
pairs are exercised like everything else. The assertion becomes: **for a
native-language query, the winning variant must be its own language, and its rank
must not get worse.** A rendering beating the native text on a native query is a
finding to be printed, not a pass.

```
renderings   205
control      soft: an assertion about which variant won, not about invariance
cost         a real failure mode has no hard tripwire; on the other hand the
             pipeline is actually tested rather than exempted
```

**Ruled: 15b, 2026-08-16.** 15a's exemption is a rule about the query that
exists only because we already expect the answer — the leakage trap at one
remove — and 15b's assertion is a test the pipeline can fail, which 15a cannot
run at all. The cost accepted with it is that the native-language control has no
hard tripwire, on a harness that twice this month produced a green result about
a fiction. `retrieve.render.native_query_problems` is the mitigation and it is
mutation-verified; it is not the same instrument as an invariance assertion and
must not be described as one.

---

## Ruling 16 — the reranker keeps receiving the pair's own query text

C3 was adopted on a measurement made with `p.query`, and `--collapse --rerank` is
the configuration C5–C6 must measure frozen. If C2 changes what the cross-encoder
sees, then the frozen configuration is not the one measured on 2026-08-16, C2 and
C3 confound, and the difference between 28/30 and 29/30 stops being attributable
to anything.

So: **C2 changes what is retrieved and how it is scored; the reranker's input
query is unchanged.** `rerank_cache`'s key stays valid and the rerank spend does
not move.

The objection worth recording: a multilingual cross-encoder handed the
target-language query might do better than one handed the English. That is a
third intervention. It needs its own baseline and its own name, and it is not
this one.

---

## Ruling 17 — two mechanical guards on mistranslation, both free, and one sentence that travels with every number

`answer/translate.py` already carries the failure this guards against, in its own
comment: v1 back-translated Old Tamil into Latin romanisation and scored chrF
0.004, *"measuring alphabets"*. The same class of failure in a query rendering
would be invisible — a romanised Tamil query would simply retrieve badly, which
is what C2 is trying to fix, and nothing would say which had happened.

**(a) Script check, deterministic, no calls.** Each rendering is checked against
`translate.NATIVE_SCRIPT_LANGS` and `TRANSLITERATED_LANGS`. A `grc` rendering
with no Greek characters, an `oty` rendering with no Tamil characters, is
**refused** — recorded as `rendering_rejected`, not embedded, and not silently
fused. A refused rendering is a run-level note, not a pair-level miss.

**(b) Query-to-query cosine, from vectors the run already computes.**
`cos(q_en, q_lang)` per rendering. A rendering that drifted semantically shows up
as an outlier against the other six for the same query. Recorded and reported,
**never gated** — there is no baseline for it, and gating on a quantity with no
baseline is the thing this project refuses.

**(c) The renderings are archived verbatim** in the run JSON with
`prompt_version` and the resolved chat model, for the same reason
`embedding_model` sits beside every vector: a later run must be able to tell *the
retriever changed* from *the translation changed*.

**(d) The sentence, printed on the same page as every C2 number:** *a translated
query that succeeds proves the pipeline works, not that the retriever is
cross-lingual.* `recall@6 via the original text` — 21/30 today — is the number
that speaks to the second, and a C2 run that does not report it is reporting half
a result.

---

## Ruling 18 — C2a does not subsume C4, and the ranking harness cannot measure C4 at all

The C4 item asks: *"`align._merge` presents a whole section when only one member
was retrieved. Measure both arms on the gold set: does surfacing the retrieved
member score better than the merged section?"*

Four facts from the code:

1. `retrieve.collapse.collapse()` emits a chunk **that was already in `hits`**,
   text unchanged. It decides WHICH chunk represents a section. `align._merge`
   decides WHAT TEXT a section's translation is. Different objects, different
   layers.
2. `_merge` merges **translations only**. `pair_chunks` returns originals
   unmerged by design — *"`fold_hits` keys on the retrieved chunk's own id"*.
   Ruling 11 canonicalises a collapsed section to the record's **primary** text,
   which for `literary_text` and `inscription` is the original. So for every
   collapsing literary document, the merged object never enters the ranking.
3. In the ranking harness `_merge`'s output is **functionally inert**.
   `resolve_alternates` reads `aligned.members` — every member's chunk id — and
   `resolve_sections` reads the same. Neither reads the merged `.text`, and
   neither uses the merged object's id. **No rank, no gap and no recall in any
   archived run has ever depended on `_merge`.**
4. Both arms already exist on the answer path and are already recorded
   separately: `evidence.py` carries `translation_member_chunk_id` (the retrieved
   member) beside `translation_section` (the merged section). That separation is
   what C1b's `translation_chunk*` rename produced.

**Ruling: C4 is closed as a Block C ranking item.** The instrument that was to
produce its number cannot see the thing it is about. What remains is one question
on the answer path — which of two already-recorded arms is presented and cited —
and it belongs to W4, against the answer gold set, not to Block C.

Cost: none, and it closes the item the runbook flags as *"most likely to absorb a
week for a null result"* — for a better reason than a null result.

---

## Ruling 19 — the renderings are frozen data, not a pipeline step

C5–C6 require two runs on different days against a frozen configuration.
`chat-default` is a gateway alias that will be repointed, and `translate.py` runs
at `temperature=0` for reproducibility that the alias does not guarantee across
days. If day 2 re-renders, the two runs used different queries and the two-day
criterion is satisfied by two different configurations.

So the renderings are produced **once**, written to
`eval/gold/query_renderings.json`, reviewed, and committed. Every run reads them
from disk and records the file's content hash in the archived report.
`--refresh-renderings` is a separate, explicit action that bumps a version and
invalidates comparability, exactly as `PROMPT_VERSION` does.

This is also what makes C2 cheap: 205 chat calls once, and every run after that
is embeddings and local search.

---

## Ruling 22 — a stronger model refuses greedy decoding, and that is recorded rather than dropped

`claude-sonnet-5` returns a bare 400 for `temperature=0`: *"Only temperature=1
is supported."* `_chat` has sent 0 since Part 6 on the argument that *a
translation harness must be reproducible*, so a stronger model is not a drop-in
for this pipeline — it costs determinism, and the first `--model chat-strong`
run spent 615 requests discovering that before it was stopped by hand.

**LiteLLM's own suggested fix is refused.** `drop_params = True` is a gateway
setting: it would silently discard unsupported parameters from *every* call the
proxy makes, embeddings included, and produce rows that look decoded and were
sampled. Silently dropping a parameter an archived measurement depended on is
the failure this repository keeps paying for.

Instead, three things:

1. **`_is_unsupported_temperature`** joins `_is_rate_limit_error` and
   `_is_connection_error`. Unclassified, this arrives as a generic error, is
   retried three times, and is reported as *"translation failed"* — which sends
   you to debug a prompt.
2. **The fallback is opt-in and defaults to off.** `render_query` is the only
   caller that opts in. Part 6's translations and Part 7's answers keep sending
   0 and keep failing loudly, so no archived number quietly changes meaning
   because an alias moved.
3. **`temperature` is recorded on every `Translation` and every rendering row**,
   with a note on the row. A rendering sampled at 1.0 and one decoded at 0.0 are
   not the same measurement and nothing else in the row says which it was.

### Why the loss is smaller than it looks, and where it is real

Ruling 19 already put reproducibility in the FILE, not the sampler: renderings
are produced once, committed, read from disk, and their content hash is recorded
in every run. What makes two runs on two days comparable is the frozen file. So
temperature=1 does not touch C5-C6.

What it does cost: **a re-render is no longer the same call twice.** Ruling 20's
retry argument — *"at temperature=0 re-issuing the same prompt is the same
call"* — stops holding on a sampling model. Above zero, a second attempt at the
same prompt is a genuinely independent draw.

### The opportunity that falls out of it, stated so it is not mistaken for cherry-picking

Since ruling 21 attempts are additive and `best_attempt` promotes by a
**gold-blind** criterion — the script guard — drawing N samples and keeping the
best is rejection sampling against a mechanical rule that cannot see any pair's
target. It is not selection against the gold set and must never become that.
Old Tamil fails 16 of 29 on one greedy draw from the cheapest model; N draws
from a stronger one is a legitimate and cheap thing to try, and it needs no new
flag — `--attempt-all` run twice is two samples.

**What must travel with it:** the number of attempts per row is recorded, and a
rendering that took four draws to pass the guard is weaker evidence about the
pipeline than one that passed first time. Report the distribution, never only
the survivors.

### Also fixed, from the same run

A systematic failure now **stops the run after three consecutive failures with
one cause**, writes what succeeded, and prints the shared reason. 205 renderings
x 3 retries against a 400 that will never succeed is not a retry policy. And a
row records at most one failed-call attempt, so a bad alias cannot stack 205
empty attempts the promotion rule then has to sort past.

---

## Ruling 23 — what the first real rendering run changed about the guard

**23a — the selection regime is uneven, and it is recorded rather than evened
out.** Old Tamil rows were drawn twice (haiku, then `chat-strong`) and promoted
by the gold-blind script guard; every other language was drawn once. Evening it
up would have cost 176 calls and another review cycle to buy nothing the gap
criterion can see. `attempt_count` per row is the record, the caveat sits in the
file's own `about`, and **any per-language number taken from this file has to
say so** — which matters, because the plan's own C2 instruction is that an
aggregate win which loses Chinese is a loss.

**23b — the script check judges letters AND script-specific marks.** Letters
alone was the rule until this passed at "100% Tamil":

```
அடுலിசிலிருந்து என்ன ஏற்றுமதி செய்யப்பட்டது?
      ^ MALAYALAM VOWEL SIGN I, inside the place name
```

Vowel signs are Unicode category `Mn`/`Mc`, not `L`, and in an Indic script they
carry much of the phonology. That row is the query for `adulis-exports`, the
pair C2a's collapse moved from 15 to 3 — not an inert row. `U+0300-036F` is
excluded from both sides of the ratio because it belongs to no script and is
used by Greek and by scholarly transliteration alike; refusing it would refuse
correct renderings. Cost: one row of 205.

## Ruling 24 — the verdict is derived on read, never trusted from disk

`eval/gold/query_renderings.json` said `ok: true, problems: []` for that same
Adulis rendering, because it had been judged under the pre-23b guard. **The
reader trusted it, and the fusion would have embedded a rendering the current
guard refuses with nothing in the run to say so.** The guard was right, the
writer was right, and the reader quietly undid both.

So `settle_row` moved into `retrieve/render.py` beside the guard, is imported by
the build script rather than copied, and `load()` re-judges every row as it
opens the file. Rows whose stored verdict disagrees are counted and reported.

**This is what the content hash cannot do.** Ruling 19's digest says the bytes
are the same on both days; `stale` says whether the rules that judged them are.
Two runs against one digest can still be two configurations.

The Adulis row proved the whole chain in one step: the mark-aware guard held the
haiku text, `best_attempt` promoted the sonnet draw already sitting beside it
from ruling 21, and the correction cost nothing because it had already been
bought.

---

## What is settled and what is not

```
12  language set from the index          settled by the leakage argument
13  fusion = max per candidate           settled; exact because SEARCH_K is None
14  both arms, same run                  settled
15  the control                          RULED 15b - uniform, soft assertion
16  reranker sees the original query     settled by C3's frozen configuration
17  script check + q-q cosine + archive  settled
18  C4 closed as a ranking item          settled by four facts in the code
19  renderings are committed data        settled by the two-day criterion
```

All eight are ruled. What is built against them, and what is not:

```
built, offline-verified          retrieve/render.py          the language rule,
                                                             the script check,
                                                             the file, the control
                                 answer/translate.py         render_query + prompt,
                                                             QUERY_PROMPT_VERSION
                                 scripts/build_query_renderings.py
                                 eval/test_ranking_check.py  +33 assertions
                                 scripts/mutate_ranking.py   +14 mutations, 50 -> 64

NOT built yet                    ruling 13's fusion in eval/run_ranking_check.py
                                 ruling 14's two-arm reporting
                                 ruling 17(b)'s query-to-query cosine
```

The fusion is deliberately second. Ruling 19 makes the renderings reviewable
data, and a fusion written against a file nobody has read would be measured on
205 strings whose quality is unknown.
