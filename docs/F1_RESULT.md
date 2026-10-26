# F1 — result

*2026-08-29. F1 declares the tiering policy and the target mix before anything
is curated. It does not move the corpus: `26e4a683` is unchanged and is still
the denominator of all 396 Block E runs and of the sonnet arm's 165.*

```
tree            clean at a6442b6 on entry; F1 adds one commit
corpus          24 records / 450 embedded / 0 pending   UNMOVED
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                CHECKED, not assumed. See "the digest question" below.

rulings         43, 44, 45         findings  30, 31
new suite       ingest.test_fidelity        30   GREEN
new harness     scripts\mutate_fidelity.py  24   GREEN, and it has the BASELINE
                                                 check from the day it was built
ingest.verify   GREEN for the first time since 2026-08-22   <- FINDING 31
```

## What F1 declared

**Five tiers, not three** (ruling 43). `PHASE2_PLAN`'s table could not hold the
corpus that already exists: `arabia-02-palmyrene-tariff` fell in no tier at all,
and the tier F3–F7 *predicts becomes the common case* — source-language text
with no published translation, where `resolve_english` starts choosing
`machine` — had no name, so the mix could not have had a target for it. Ruling
38 one level over: a table with three states will keep producing the
contradiction that a third state was invented to end.

**The target mix** (ruling 44), declared before the first new record exists:

```
                             at 24    new    at 60
verbatim_with_provenance        11    +14       25
verbatim_machine_english         0    +10       10
published_translation_only       1     +4        5
catalogue_record                11     +8       19
pointer_only                     1     +0        1   <- a ceiling
                                --    ---       --
                                24    +36       60

region levelling      3 -> 9 (Africa, East Asia, Persia, SE Asia)
                      4 -> 8 (Arabia, Scandinavia, South Asia)
per region            >= 4 records carrying SOURCE-LANGUAGE text
gloss-capable         8 of the 36
quoted-from-original  >= 6 cases at 60, against 1 today
```

**And one number that made the per-region floor necessary.** Southeast Asia has
**zero** records carrying retrieval-eligible source-language text — which is why
all four of its gold cases sit on find records — and Africa, Persia and
Scandinavia have one each. Every aggregate target above is satisfiable inside
Arabia and South Asia alone.

## The headline, and it is a gate that can tick itself

**G3's box "curation cost per record recorded and trending down" is satisfiable
by curating cheaper records.** A museum object record is the cheapest thing in
this corpus to produce and a cited bilingual inscription is the dearest, and
nothing in the box distinguishes *the same kind of record got cheaper* from *we
made more of the cheap kind*. Kill trigger 3 hangs off that number: *"if record
60 costs what record 12 cost, 200 is a staffing question rather than an
engineering one."* A mean over a shifting mix cannot answer it.

Ruling 45 amends the box in advance — cost reported PER TIER, against the
declared mix — for ruling 39's reason, and because **F2 starts the
minutes-per-record column at record 25 and nobody times a record twice.** A
column that does not carry the tier cannot be decomposed by it afterwards.

This is FINDING 26's shape: an aggregate that moves for two unrelated reasons
reports one number and hides which one moved it.

## The digest question, asked before the file was written

A `tier` key on a seed record **would have moved the corpus digest.**
`canonical_record_text` hashes the whole parsed record with sorted keys, so any
new key changes that record's `content_hash` and therefore `corpus_digest` —
the denominator of 396 archived runs plus 165. The declaration is therefore a
sidecar.

And the sidecar is not under `data/seed_corpus/`, because `iter_seed_records`
**refuses** a `.json` at that depth: `glob("*/*.json")` would not see it and
`rglob("*.json")` would. **The layout guard fired on the first file anyone has
tried to add since it was written**, which is the only evidence a guard of that
kind can produce short of a defect.

## FINDING 31 — the suite nobody lists had been red for a week

`python -m ingest.verify` failed on `manifest-flagged record 'weilue' is
labelled verbatim_original`. On 2026-08-22 FINDING 11 lifted that flag in
`ingest/fidelity.py` with the reason written down; `ingest/verify.py` held a
second copy of the list and was never told. Red through D4, Block E's four
sessions and 396 runs, F0, and the sonnet arm.

**Nothing caught it because no state block in this repository lists
`ingest.verify` among the suites** — `F1_START` and `F1_HANDOFF` both name four
suites and six harnesses, and this is not one of them — while `PHASE2_PLAN`
F3–F7 makes it the **first line** of the block run after every sub-tranche.
F3 would have curated nine records and met a red suite that had nothing to do
with them: a true report inviting a false diagnosis, on the day the corpus first
moved.

Fixed by removing the second **opinion** rather than the check. The transcription
of the manifest's prose stays in `verify.py`; the never-`verbatim_original`
assertion now runs over `fidelity.PARAPHRASE_ID_HINTS`; a lift is a written
entry with a reason; and `check_paraphrase_flags` refuses a manifest flag that
is neither honoured nor lifted. Four guards, four mutations.

**There are five suites.** Every handoff from here on has to say so.

## FINDING 30 — a case asserted another file's state and kept asserting it

`weilue-chinese-quotation.archived_status` said the case was tracked in
`floor.json.known_failing_cases` as an open defect and that no archived answer
has quoted this record's Chinese. Ruling 38 moved it into
`promotion_candidates` on 2026-08-28, and `floor.json`'s own evidence for the
candidacy reads *"3/3 in each of four sessions… Chinese source text resolved in
the answer."* Two files stating opposite facts about one case.

`archived_status` is prose, deliberately outside `_ASSERTION_KEYS`, read by
nothing. Corrected in place with the correction recorded beside it; the missing
load-time check is deferred to F2 **in writing**, on FINDING 29's precedent.

## What F1 did NOT do

- **It did not move the corpus.** No seed record was edited. `corpus_digest` is
  `26e4a683`, checked.
- **It did not curate a record.** That is F3. F2 starts the cost column.
- **It did not touch a scored assertion.** The only edit to
  `eval/gold/answer_cases.json` is to `archived_status`, which is prose and is
  not in `_ASSERTION_KEYS`, so no archived run is re-scored.
- **It did not build the `archived_status` check.** FINDING 30, deferred with
  its reason.

## What is owed, carried forward

```
1  ruling 40's article_added is STILL unverified against any live run.
2  muziris-cargo, REQUIRED, is 3/5 on the arm and 12/12 on the declared one.
3  `eval.answer_eval --archives` pools arms into one report (FINDING 29).
4  the BASELINE check is in four harnesses of seven now — part8, part7b,
   ui_places and the new mutate_fidelity. Three still lack it: mutate_ranking,
   mutate_places, mutate_recover.
5  G3's amendment costs a SECOND session at 60, on a second UTC date, ~198
   chat calls. Ruling 39 booked the days. Do not discover this in F8.
6  FINDING 30's load-time check, deferred to F2 in writing.
7  `ingest/verify.py` check 9 asserts `len(docs) == 24`. It is CORRECT today
   and F3 breaks it on purpose. Left as written: loosening a count check in
   advance of the records is the floor lowered to what is currently passing.
   F3 changes it in the same commit as the records, or not at all.
```

## Traps, for the thread that curates

Everything in `F1_START`'s list still applies — the bridge, `git` locks,
per-file line endings, `BASELINE:`/`UNVERIFIED`, ambiguous mutation anchors.
Three more:

- **`ingest.verify` is a suite and belongs in the green check.** FINDING 31.
- **A record cannot carry a `tier` field.** Ruling 43. The digest is the reason
  and the reason does not expire.
- **A gloss case needs the dispute inside a retrieval-eligible chunk.** Not in
  `notes`, which is not chunked. `raqosh-epitaph` was nearly written the wrong
  way and its note says so.

## The sentences that travel

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310.

**Four sessions read 0.727272… and one of them was different. The pass rate
cannot see change.**

**Nine archives, 396 runs, and not one of them recorded which model answered.**

**36% and 27% are not two refusal rates. They are two rates of uttering one
sentence.**

And two from today:

**Cost per record trending down is not a fact about efficiency until the mix is
held. The cheapest record in this corpus is the one that teaches a reader the
least.**

**A suite that no state block lists is a suite that can be red for a week, and
this one was the first line of the runbook that would have found it.**

---

## A correction, made before the commit landed

**The assertion count went into five documents as 29 and the suite has 30.**
Written down once, before the last four `check_paraphrase_flags` assertions were
added, and never recounted — the number was transcribed rather than read.

Nothing about the work was wrong and that is the point: the count was the one
claim in F1 that no instrument produced. Corrected in all five, and
`ingest.test_fidelity` now prints `30 passed, 0 failed` in the house style, so
the next reader compares a document against a suite instead of against an
earlier document.

It is FINDING 31's family in miniature. One claim, held in more than one place,
and only one copy maintained.
