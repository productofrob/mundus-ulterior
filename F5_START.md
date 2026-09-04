# F5 START — three targets that cannot be reached, and the one instrument that would have said so

F4 closed at `5497a2b`, working tree clean. The corpus is **35 records**, digest
`9728581d164b0a4b…`, 82 chunks, 23 parallel pairs.

```
ingest.verify              green -- 35 documents
ingest.test_fidelity        58      ingest.test_cost             64
eval.test_answer_eval      410      eval.test_ranking_check     253
answer.test_answer         150      ui/test_build_ui_data.py     19
scripts/test_recover_baseline.py 56 scripts/test_harnesses.py    33   <- NEW, ninth
mutate: ranking 108  part8 94  cost 51  fidelity 46  places 43
        part7b 18  recover 17  distractors 6  ui_places 6  = 389, all verified
```

Read `F4_RULINGS.md` first — it carries rulings 63 to 66 and FINDINGS 57 to 61,
and the readings of the two pre-registered predictions. This document is only
what has to be **decided or known** before F5 curates anything.

---

## THE THING F5 MUST DECIDE BEFORE IT CURATES A RECORD

**Three targets are already unreachable, all by the same mechanism, and every
check in this repository reports all three as fine.** None of this is a new
defect. It is arithmetic nobody has done, on numbers that have been on file
since F1.

### 1. The corpus lands at 56, not 60

```
seed 24  +  delivered 11  +  still allocated F5 7 + F6 7 + F7 7 = 21   =  56
```

The gap is **4** — F3's two unfilled slots and F4's two. Neither was absorbed,
both for reasons stated at the time (ruling 63 declined to re-cut for F4's).

### 2. Two regions cannot reach the source-language floor of 4

**And the allocation was RIGHT when it was written.** As planned, every region
clears it:

```
region              at 24   planned +   planned final      ACTUAL final
Arabia                  3           3             6              6
East Asia               2           4             6              6
Persia                  1           4             5              4
South Asia              3           2             5              5
Southeast Asia          0           4             4              4
Scandinavia             1           3             4              3   <-- BELOW
Sub-Saharan Africa      1           4             5              3   <-- BELOW
```

`check_allocation` verified the plan and the plan was sound. What happened is
that **F3's two missing records and F4's two landed in the two regions with the
least headroom.** Persia lost one and the plan had a record of slack, so it
recovers to exactly 4. Scandinavia lost one and had none. Africa lost two and
had one.

**Sub-Saharan Africa therefore ends Block F with three source-language records,
below the floor — and ruling 58 has already established that all three are
Greek.** The region ends the block with zero records carrying a local-language
source text, which is the thing the project instructions ask for by name.

### 3. The gloss target of 8 lands at 7

FINDING 51, on file since F4 Part 2 and unfixed on purpose.

### The mechanism is one mechanism, and this is its third registry

FINDING 51's sentence: *"the guard asked whether enough slots remained when the
scarce thing was declarations, and both are counts of records, so the sentence
read correctly."*

Here the scarce thing is **allocated slots** and the guards count **curated
records**. `check_allocation` reads the PLAN, which still sums to 36 and always
will. `check_delivery` compares curation against the cells the plan places and
correctly calls a shortfall progress. `ingest.verify` prints *"11 of 36 tranche
records curated"*, which reads as *25 to go*, and *"Below the floor: {…}"*,
which reads as *work in progress*. **Nothing compares cumulative delivery, plus
what is still allocated, against any target.**

Every one of those checks is doing its job. The check that would have caught
this does not exist.

### What F5 must not do

**Keep curating and discover at F7's close that none of the three was
reachable.** That is the failure FINDING 51 named and deliberately did not fix,
because a quota changed in the session that noticed it is a quota fitted to the
session. **F5 is the session with two tranches of evidence and no quota riding
on the answer**, which is exactly the position ruling 53 said the re-cut should
be taken from.

And **not** by letting a later tranche quietly over-deliver: nothing compares a
tranche's delivery to its declaration, so that route is available and it is the
loophole. Whatever F5 decides, it is a diff.

---

## The mechanical first act

**Run the nine suites on the host at `5497a2b`.** Seven of the nine numbers above
were printed on the host at `4d3ebe2`, and nothing since feeds them — but
`scripts/test_harnesses.py` has never run on the host at all, and
`eval.test_answer_eval`'s 410 was measured against 52 entry points where there
are now 53. FINDING 57's rule is that a suite number names the commit **and** the
interpreter, and the state block above is currently a stitch of two trees.

---

## What F5 is allocated

```
Persia       verbatim_with_provenance 1   verbatim_machine_english 1
Arabia       verbatim_with_provenance 2   verbatim_machine_english 1
South Asia   verbatim_with_provenance 1   verbatim_machine_english 1
                                                            7 records
gloss_capable 2      expect_quoted_from_original_cases 3     vme_quotation_cases 1
```

`why_these`, from the allocation: *"the last source-language records for the
three regions that already clear the per-region floor, and the sub-tranche that
completes the quoted-from-original quota at seven cases across seven regions."*

**Three of the seven are `verbatim_machine_english`, and one of them is in
Persia.** That is the region whose four disqualifications produced FINDING 41 —
Kartir, the Pahlavi corpus, M 5794 I, the Istanbul epitaph, all Englished — and
ruling 53's whole complaint was that the tier had been *"tested where the tier is
hardest to fill and reported as a property of the tier."*

**So ruling 53's deferred vme ruling has to be taken BEFORE F5 curates, not at
its close.** Taken after, F5 will have spent its vme hunting time in the same
tradition that produced the finding, and the ruling will again be made by
somebody who has just seen what that tradition does to the numbers.

---

## The four decisions, in the order they should be taken

### 1. The three unreachable targets, above. Before anything is curated.

Three routes, and they are not equivalent: raise F5–F7's allocation to absorb
the four; lower `total_at_60` and the per-region floor, which is a re-cut and
belongs with the five instrument changes already owed; or accept 56 and re-read
every figure denominated *"at 60"* against it — the floor's re-calibration
clause, `min_source_language_records_per_region`,
`min_expect_quoted_from_original_cases_at_60`, `gloss_capable_records`.

### 2. FINDING 60's interval recording. Cheap, and it unblocks a finding.

The ranking run should record, per pair, **the documents ranked between the
target and `best_other_doc_chunk_id`**. That field records the CEILING, which is
stable precisely because it is the best; crowding happens in the interval
underneath it, and the interval is what is not stored.

Four attributions in `F4_RESULT.md` are written as *unavailable* because of this
one missing field, and FINDING 43 has never been testable. The ranking is
already computed to full depth and `rerank_top_chunk_ids` already does exactly
this for the rerank arm.

**Do this before F5's records enter the index**, or F5's tranche is the fifth to
have its crowding claims made against an instrument that cannot see a crowder.

### 3. The one re-cut of `data/corpus_tiers.json`, carrying five instrument changes

F4 declined to re-cut that file four separate times so these could be taken
together, with two tranches of evidence instead of one:

1. ruling 53's deferred **vme allocation ruling** — and ruling 63 records that
   it inherits an experiment that was NOT PERFORMED, not a null result.
2. ruling 58's **per-region language rule** — which decision 1 above has just
   made urgent rather than tidy.
3. FINDING 51's **per-sub-tranche gloss delivery check**.
4. FINDING 55's **translation-search boundary on the vwp tier**.
5. ruling 62's **contested READING vs hedged IDENTIFICATION**.

### 4. Register F5's predictions before curating

F4's two pre-registered predictions are the only two this project has ever made.
**Both came back usable and neither came back the way its mechanism argued** —
ruling 55 right about direction with its cause unavailable, ruling 61 right once
in three with its most useful result the asymmetry it did not predict. Both were
worth more than any post-hoc reading of the same run, and both were only
possible because they were written before the records existed.

Decision 2 is what will let the next one be checked properly.

---

## The workflow rules that carry, and they are not optional

**The capture path.** Source text and published translations are **pasted by the
curator from the cited page**, every record. `WebFetch` silently drops lacuna
markers and substitutes U+0027 for U+2019 (FINDING 48, measured twice).
`archive.org/_djvu.txt` is **not the page** — it is somebody else's OCR, and it
splices marginal notes into sentences (FINDING 53). Characters come off the page
images, read by a person.

**A locating fetch must not reveal what it located.** The moment it does, the
curator's capture stops being an independent second reading and becomes
agreement with a model. A fetch reported no critical apparatus existed near the
stele's Da Qin passage; the curator's BLIND paste contained exactly that
apparatus, and the record's statement of uncertainty came out of it.

**And a model CAN be the diff.** FINDING 50: the automated path was wrong once in
431 characters and the human path five times in ten lines. Neither would have
been right alone. Propose the diff; never apply it.

**Write BYTES.** Per-file newline conventions, and `git diff --stat` before every
commit — a three-line change with a four-thousand-line diff is the signal
(FINDING 52). All nine harnesses now hold `_newline_of` and
`scripts/test_harnesses.py` asserts it (FINDING 61).

**Never run a mutation harness anywhere it can be interrupted.** The restore
lives inside the harness's own process, so the 45-second limit the older runbooks
cite was never the exposure. A disconnect mid-run left a live mutation in
`ingest/cost.py` on 2026-09-04 (FINDING 59). Host only, in a window somebody is
watching.

**Close a span that crossed a break** with `stop --minutes N --because "…"`. The
ledger clock does not know whether anybody is at the keyboard, and
`max_measured_span_minutes: 240` sails over a two-hour lunch (FINDING 54).

---

## What NOT to re-derive

**Do not re-hunt East Asia or Sub-Saharan Africa.** `F4_CANDIDATES.md` holds both
hunts in full, including every route that failed and why. Ruling 63 has read
Africa's zero.

**Do not read the aggregate cost per record.** Ruling 46 forbids it and the
allocation biases it downward by construction. The per-tier means are `vwp` n=8
at 10.7 min and `vme` n=3 at 4.0, both below the n=10 floor and reported as NOT
A TREND.

**Do not treat `[Siam, Cambodja?]` as an ordinary gloss.** Ruling 62 took it with
a discount and the discount travels in three places.

**Do not re-take the F4 ranking run.** A second archive at one tree makes *which
run is F4's* a question nobody needs.

---

## Still owed, beyond the four decisions

- **ruling 65's renderings debt** — the eight Part 2 pairs, before any fused arm
  can include them. The C2 fused arm has now gone two tranches without a reading.
- **FINDING 58's shared matcher** — nine copies of one three-line rule.
  `scripts/test_harnesses.py` stops them drifting; it does not make them one.
- **`scripts/mutate_part8.py` does not mutate `eval/test_answer_eval.py`**, so
  three data-driven guards there have no mutation proving they can fail.
- **`scripts/mutate_distractors.py` has no BASELINE block**, and it is the one
  that mutates the SCHEMA. Counted rather than asserted by the new check.
- **The floor is calibrated at the 24-record corpus**, pinned there by ruling
  49's clause, and re-calibration at 60 costs three more distinct dates and
  ~270 chat calls. That is a scheduled cost, not a formality — and decision 1
  may change the number it is denominated in.
- Carried untouched: `verse` and `documentary` profiles at n=1 and load-bearing;
  ruling 40's `article_added` still 0; `ingest/test_sql.py` never run with
  sqlglot AND the database; `muziris-cargo-akananuru` at rank 319.

---

# The sentences that travel, into F5

**The allocation was right when it was written, and the two tranches that missed
their records missed them in the two regions with no headroom.**

**Sub-Saharan Africa ends Block F below the source-language floor with three
records, and ruling 58 has already established that all three are Greek.**

**Every check reads the plan or the tranche, and the plan still sums to 36, so
three unreachable targets have been reported as progress for two sub-tranches.**

**A prediction confirmed in direction and unattributable in cause is two
results, and writing it as one is how a mechanism becomes folklore.**

**The field records the one competitor that never moves, so four tranches of
crowding claims were made against an instrument that cannot see a crowder.**
