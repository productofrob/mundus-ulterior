# Rulings 67 to 73 and FINDINGS 62 to 67 — declared 2026-09-04, in F5, before any record was curated

*Date taken from the host, not from another document: `date -u +%F` printed
`2026-09-04`. That is Block F's fourth distinct UTC date and the same date F4
closed on, which is stated rather than hidden: this is a second session on one
date, and three rules in this repository count DATES.*

*Everything below is recorded before F5's first candidate is examined. Ruling
39's discipline for the tenth time in this block — and this time it is
load-bearing rather than habitual, because ruling 67 decides the fate of a tier
that F5 has three slots on. A session that ruled on that tier after hunting for
it would be ruling on the tier with its own hunting time already spent, which is
ruling 53's complaint about F3 arriving in the session appointed to answer it.*

*Two things were established mechanically before anything was decided. The nine
suites were run **on the host at `74c480c`**, which is one commit past
`5497a2b` and differs from it by one document, `F5_START.md`, 281 insertions and
nothing else. FINDING 57's rule is that a number names the commit AND the
interpreter, and the F4 handover broke that rule in its second paragraph by
claiming a tree for numbers measured at another one. These name `74c480c`.*

```
ingest.verify                    green -- 35 documents, 82 chunks, 23 parallel pairs
ingest.test_fidelity              58      ingest.test_cost              64
eval.test_answer_eval            410      eval.test_ranking_check      253
answer.test_answer               150      ui/test_build_ui_data.py      19
scripts/test_recover_baseline.py  56      scripts/test_harnesses.py     33
```

*`test_harnesses.py` had never run on the host before. `test_answer_eval`
reports 53 entry points, so its 410 is now measured against the population it
describes rather than against 52 — the FINDING 47 shape the handover flagged is
closed.*

---

# FINDING 65 — the four records the block is short are all one tier, and every check counts them three times

*Found first in this session and numbered last. FINDINGS 62 to 64 were put to
the project owner under those numbers before this document existed, and a number
that has been communicated should not churn.*

`claude/f5-opening-debt.md` records the arithmetic and asks F5 to record it as
its own finding, on its own date, before curating. Recomputed from
`data/corpus_tiers.json` and the seed corpus rather than read back from the
prose, every figure it states holds:

```
seed 24 + delivered 11 (F3 6 of 8, F4 5 of 7) + still allocated 21 = 56    target 60
```

**What nobody had done is the same arithmetic by tier.**

```
tier                        at 24   now   +F5-F7   final   target
verbatim_with_provenance       11    19        6      25       25
verbatim_machine_english        0     3        3       6       10   <-- 4 SHORT
published_translation_only      1     1        4       5        5
catalogue_record               11    11        8      19       19
pointer_only                    1     1        0       1        1

F3 and F4, planned against delivered
  verbatim_with_provenance    planned  8    delivered  8    complete
  verbatim_machine_english    planned  7    delivered  3    MISSING 4
```

Every other tier lands exactly on its number. F3 and F4 hit **every one** of
their sixteen source-language-with-a-published-translation slots. What they
missed, they missed entirely inside `verbatim_machine_english`: Persia one,
Scandinavia one, Sub-Saharan Africa two.

So the three unreachable targets `F5_START.md` names are not three problems with
a shared cause. **They are one shortfall counted three times.** The corpus lands
at 56 because the vme tier lands at 6. Scandinavia and Africa are below the
source-language floor because the records they lost were vme records. And the
gloss target is short for a different reason entirely, which is FINDING 51 and
is settled by ruling 68 below.

`F5_START.md` frames this as *"F3's two unfilled slots and F4's two"* landing
*"in the two regions with the least headroom"*, which is true and is the second
sentence. The first is that all four were on one tier, and that is the sentence
which decides what the remedy can be.

---

# FINDING 62 — one Greek text is counted as three regions' source-language records, and ruling 58's proposed rule would have refused the wrong three

Ruling 58 read Sub-Saharan Africa's floor as **met in Greek** and defended
`africa-04-silko-talmis` and `africa-05-adulis-throne` as *"Africans using the
empire's language and the empire's gods to say something about themselves, which
is a sharper statement about influence than a local language would have made."*
That defence is right and nothing here disturbs it.

**What it did not see is the third record sitting beside them.** Of the corpus's
22 source-language records, four are Greek with **no findspot at all**:

```
Arabia              arabia-01-periplus             Periplus §27-29,  Cana and the Frankincense Country
South Asia          southasia-02-periplus-muziris  Periplus §53-56,  Muziris and the Limyrike coast
South Asia          southasia-03-muziris-papyrus   SB XVIII 13167,   a Greek loan contract found in Egypt
Sub-Saharan Africa  africa-03-periplus-adulis      Periplus §4-6,    Adulis and the kingdom of Zoskales
```

Three of those four are **the same text**. Same work, same edition, same
`citation_original` — Müller's *Geographi Graeci Minores* I, 1855, via one Greek
Wikisource page. **The Periplus of the Erythraean Sea supplies one
source-language record to Arabia, one to South Asia and one to Sub-Saharan
Africa.** The floor counts records; the Periplus is one text wearing three.

`why_per_region` states exactly what the floor was built to stop: *"A tier target
met entirely inside Arabia and South Asia would satisfy every aggregate above and
leave four regions exactly as unable to answer a source-text question as they are
now."* It stops an aggregate being met inside two regions. **It cannot stop three
regions being met inside one Alexandrian merchant's handbook.**

Split by whether the region is speaking or being spoken about:

```
region               total   local-lang   empire-lang    empire-lang
                                          in region      about region
East Asia                5            5             0              0
Southeast Asia           4            4             0              0
Arabia                   3            2             0              1
Persia                   2            2             0              0
Scandinavia              2            2             0              0
South Asia               3            1             0              2
Sub-Saharan Africa       3            0             2              1   <-- ZERO
```

**Sub-Saharan Africa holds no source-language record in a language of the
region.** Two Africans writing Greek, and one Greek writing about Africa. South
Asia is at one — the Akanānūru; its other two are the Periplus and an Egyptian
papyrus.

## Why this changes the rule ruling 58 asked for rather than confirming it

Ruling 58 proposed *"a per-region rule that refuses a floor met entirely in Greek
or Latin."* **That rule gets exactly the wrong records.** It cannot tell
`africa-04-silko-talmis` from `africa-03-periplus-adulis`, because both are
`grc`. It would refuse the two records ruling 58 argued hardest to keep and admit
the one it should refuse.

The distinction that does the work is not the LANGUAGE of the text but whether
the region is **speaking** or being **spoken about** — and the corpus already
holds it, in `findspot` and in W1's `findspot_places` / `subject_places` split.
The tier layer read neither field. FINDING 51's family again, and ruling 49's:
*the data was already there and the rule did not read it.*

## What is done, and what is deliberately not

`ingest.fidelity.source_language_provenance` classifies a source-language record
into `local_language`, `empire_language_from_the_region` or
`empire_language_about_the_region`, and `ingest.verify` prints the table above
plus any text counted in more than one region. Any language outside
`EMPIRE_LANGUAGES` makes a record local, so `persia-01-skz` — Parthian, Middle
Persian and Greek — is not read as a Roman text for its Greek column. An **empty
language list is not read as local**, because the flattering direction is the one
a missing field must never take.

**COUNTED, NOT GATED**, and not out of timidity. Sub-Saharan Africa has zero
local-language source records and **no source-language slot left in any
sub-tranche**, so a minimum here would fail the tree on a condition no allocation
Block F still has can satisfy — and a gate nobody can satisfy is a gate somebody
deletes. Ruling 56's shape: the teeth are the presence of the number and the fact
that it is printed, not a floor.

Nine assertions and three mutations. The mutations are the three ways the
classifier can lie in the flattering direction: every record read as local, a
Roman-world text read as a record from the region, and an empty language list
taking the local branch.

---

# FINDING 63 — F5 is the last sub-tranche allocated any `verbatim_machine_english` record at all

```
                    planned   delivered
F3  Southeast Asia        2           2     unattributed circulating English (ruling 57)
F3  Persia                1           0     FINDING 41's tradition
F3  Scandinavia           1           0     FINDING 41's other tradition
F4  Sub-Saharan Africa    2           0     supply, not translation (ruling 63)
F4  East Asia             1           1     the genre seam (FINDING 45)
F5  Persia 1, Arabia 1, South Asia 1  = 3 allocated
F6                        0
F7                        0
```

**F6 and F7 place no `verbatim_machine_english` slot.** The tier stands at 3
against a target of 10, F5 holds three slots, and nothing after F5 holds any.
Even a perfect F5 ends the block at 6 of 10 and there is no session left in which
to do better.

That is why ruling 53's deferred ruling cannot be deferred a third time, and the
reason is not that F5 was nominated for it. **It is that F5 is the last session
with anything to rule about.** A deferral to F6 would be a deferral to a session
that cannot act on the answer.

---

# Ruling 67 — the deferred `verbatim_machine_english` ruling: FINDING 41 NARROWS, on delivery evidence that is weaker than the experiment, and one slot is re-pointed

**FINDING 41 becomes a rule about where a hunt LOOKS and not a property of the
tier. `data/corpus_tiers.json`'s allocation moves F5's Arabia
`verbatim_machine_english` slot to East Asia, onto FINDING 45's named seam, and
Arabia takes a `catalogue_record` slot from F7 in exchange. No tier total moves,
no region's target at 60 moves, and no delivered plan is restated.**

## The evidence F5 actually has, and it is not the evidence ruling 53 designed

Ruling 63 is right and its sentence governs this ruling: *"ruling 53 designed a
test and the test did not run… F5's deferred vme ruling inherits an experiment
that was not performed rather than a null result."* Sub-Saharan Africa delivered
zero for FINDING 38's supply reason, not FINDING 41's search reason, so the
NARROWS / STANDS / NEITHER reading ruling 53 wrote conditions for has no input.

What exists instead is the delivery record above, and it has a shape:

**Every `verbatim_machine_english` record that landed came from a region where a
specific, nameable structural gap in English-language scholarship had been
identified BEFORE the hunt began** — an attribution gap in Old Malay (ruling 57:
the English that circulates for Kedukan Bukit and Talang Tuo is unattributed),
and a genre gap in the Chinese compilations (FINDING 45: the sinologists
translated the dynastic histories and left the *huiyao*, the *leishu* and the
geographies alone). **Every slot that failed was either in a tradition FINDING 41
itself named as among the most thoroughly Englished in existence, or failed on
supply rather than on search.**

Three of three where a seam was named. Zero of four where one was not.

**This is weaker than the experiment would have been and F5 says so rather than
letting delivery evidence wear the experiment's clothes.** It is four
observations, two of them retrospectively described — FINDING 45 was written in
F4, after F3's Old Malay records had already landed — and a pattern read off
deliveries is a pattern read off work somebody chose to do. It is enough to
re-point one slot. It is not enough to re-cut the tier's target, which is why
ruling 69 leaves `by_tier_at_60` alone.

## Why a slot had to move at all

F5's three vme slots stood at Persia, Arabia and South Asia: Middle Persian
epigraphy, Ancient North and South Arabian, and Old Tamil. Three traditions with
substantial English-language scholarship, and **no genre seam named in any of
them by anybody.** Persia is the region whose four disqualifications produced
FINDING 41 in the first place. Curating those three as written is ruling 53's
complaint for the third time — *"tested where the tier is hardest to fill and
reported as a property of the tier"* — in the last sub-tranche that can test it
at all.

## Which slot moved, and why only one

**Arabia's, and not South Asia's.** Under the allocation Arabia ends at five
source-language records and South Asia at four. Taking the slot from South Asia
would leave it sitting exactly on the per-region floor with nothing to spare, and
FINDING 65's whole lesson is that F3's and F4's misses landed in the two regions
that had no headroom. **The slack comes from the region that has some.**

**One slot and not three.** Moving all three would meet the tier inside a single
region, which is `why_per_region`'s own complaint one field over, and FINDING
45's seam holds three named untranslated texts — the Tang Huiyao, the Taiping
Huanyuji and the Lingwai Daida — not nine. A ruling that spent the whole tier on
one seam would be a ruling fitted to the one seam anybody has found.

## The anti-loophole, carried across intact and now doing double duty

Ruling 53's requirement and ruling 57's definition both stand unchanged: a
`verbatim_machine_english` record carries, in its own `notes`, the named sources
consulted and the boundary where the search stopped, and any English found is
cited with its URL beside the reason it was refused. **A record whose note says
only "no English translation found" is not evidence for anything.**

That rule now carries ruling 72's prediction as well, and the reason is stated
here rather than discovered later: a curator who has predicted that Persia and
South Asia will fail is a curator who can make them fail by not looking. **A vme
slot that goes unfilled without a recorded search is not evidence for ruling 72
and F5_RESULT may not count it as such.**

## What is NOT decided

`by_tier_new`'s ten does not become *"at least N, discovered"*. The tier keeps a
declared target and misses it visibly, which is ruling 69's shape one field down.
And FINDING 41's central claim — that what a curator establishes is a property of
the search — is not weakened; ruling 57 already made that the definition.

---

# Ruling 68 — the gloss target is re-denominated to 7, the allocation is allowed to carry slack, and FINDING 51's guard is made to count the scarce thing

**`gloss_capable_records` 8 → 7. `gloss_capable_declared` becomes a list of
objects carrying `record`, `sub_tranche` and `kind`. `check_allocation`'s gloss
clause relaxes from an equality to a minimum. `check_delivery`'s reachability
counts DECLARATIONS and slots, and names which one binds.**

## The number, reached twice from two directions

At 60 records, 8 gloss-capable records is one per 7.5. The same proportion of 56
is 7.47, and the reachable integer is 7. FINDING 51's arithmetic gives the same
number from the other side: 3 declared, plus F5 2 + F6 1 + F7 1 still to declare,
is 7 and cannot be 8 unless some sub-tranche quietly exceeds its own declaration
— which is the loophole that finding named. **Two independent routes to 7 is why
this is a re-denomination and not a quota fitted to the session that noticed it.**

`F5_START.md` names `gloss_capable_records` explicitly among the figures
denominated *"at 60"* that must be re-read against 56. This is that re-reading.

**F3's declared 2 stays 2 though it delivered 1.** Restating a delivered plan to
match what happened is the move ruling 56 refused, and the plan therefore places
8 against a target of 7.

## Why the plan may now place more than the target

`check_allocation` required the sub-tranches' `gloss_capable` to EQUAL
`gloss_capable_records`. **An equality is a plan with no tolerance for a
sub-tranche closing short**, and Block F has now closed two short. A plan with no
slack against a target is a target that fails on the first miss.

Relaxing it costs nothing, because the ceiling is enforced where it can be
observed: `check_delivery` already refuses more DECLARATIONS than the mix asks
for. Under-placing is the direction that can never be recovered — nobody
re-curates a record — and that direction is still guarded.

## FINDING 51's guard, which was aimed at the wrong quantity on the day it was written

```
before:  len(declared) + SLOTS-on-a-tier-that-can-carry-one  <  want
after:   len(declared) + min(declarations-left-in-OPEN-sub-tranches, slots)  <  want
         ...and the message names which of the two binds
```

Slots are plentiful by construction — 18 remain, including twelve
`catalogue_record` and `published_translation_only` slots no plan intends to
spend on a gloss case. Declarations are four. Both are counts of records, so the
old sentence read correctly for two sub-tranches while answering a question
nobody was asking, in the reassuring direction.

**Reporting one number is how this stayed invisible, so the new message reports
both and says which binds.** `ingest.verify`'s delivery note does the same.

Making the arithmetic possible required the data-structure change FINDING 51
named as its blocker. Each declaration now states its `sub_tranche`, and each
sub-tranche states whether it is `closed`. Both are DECLARED and not derived, for
the reason `ingest.verify` already prints: F3 and F5 both place a
Persia/`verbatim_with_provenance` slot, so a delivered record in that cell
belongs to either.

**And the check that did not exist now exists:** a sub-tranche declaring more
gloss-capable records than it planned is refused. Nothing else in this repository
compares a tranche's delivery to its own declaration, which is how an aggregate
gets met one tranche at a time with every check green.

## Ruling 62's owed distinction, paid as data

`kind` is `contested_reading` or `hedged_identification`, held in code as
`GLOSS_KINDS` beside `GLOSS_CAPABLE_TIERS` and `QUOTATION_CHOICE_TIERS` for their
stated reason — *it is a rule and not a number, and a mutation has to be able to
break it* — and every member must carry a written definition in the file, on
`ingest.cost`'s precedent that a phase with no written definition is refused.

`ingest.verify` now prints **"Gloss-capable declared 3/7 (2 contested_reading, 1
hedged_identification)"**. Ruling 62 had to carry the discount in three separate
places of prose because no field held it, and its own closing sentence was that
the count is the only thing anyone reads. The discount now travels with the
count.

## The thing this ruling does NOT fix, stated because it is one record wide

**7 is reachable with zero slack.** 3 declared plus 4 declarations left in open
sub-tranches is exactly 7. F5 did not inflate a later tranche's declaration to
create headroom, because a promise made by this session for F6 to keep is the
mirror image of a quota fitted to the session that noticed it. What is different
from before is that the guard now fires **the moment** slack goes negative
instead of at F7's close.

---

# FINDING 64 — the bar was written three times, twice correctly, and the copy a reader meets carries a forecast

Accepting 56 requires re-reading every figure denominated *"at 60"*.
`claude/f5-opening-debt.md` names four in `corpus_tiers.json` and one in
`floor.json`. In `floor.json` there are two, and the second is the interesting
one.

```
promotion_and_reinstatement_bar          "at the corpus in force when the claim is made"   CORRECT
demotions.vimose-runes.reinstated_when   "at the corpus in force when the reinstatement
                                          is claimed"                                      CORRECT
promotion_candidates.weilue-...bar       "at 60 records"                                   a forecast
calibration_scope.corpus.recalibration_at_60                                               a forecast
```

*An earlier draft of this finding said three gates and named
`vimose-runes.reinstated_when` among them, on the strength of
`recalibration_at_60`'s own sentence claiming the bar "already required — at 60 —
of weilue-chinese-quotation and vimose-runes". That sentence is wrong about
`vimose-runes`, and the draft repeated it instead of reading the string. The
correction is left here because it is the finding's own mechanism happening to
the finding.*

**One standard, decided once on 2026-08-28, written in three places. Two of them
name the corpus in force. One names a number.** And
`promotion_and_reinstatement_bar`'s own closing sentence is the diagnosis,
verbatim:

> *"Written here as well as in the two entries it governs, because a standard
> that exists only inside the record of the case it was applied to is a standard
> the next case gets to renegotiate."*

It was written twice against exactly that risk, and the second copy is the one a
reader of `weilue-chinese-quotation` actually meets. At 56 records that copy can
never be satisfied while the standard it restates can. **Nothing goes red: a gate
denominated in a forecast does not fail, it never fires.** A case passing 12/12
stays a candidate for ever, and `why_the_existing_evidence_does_not_promote_it`
carries the same forecast as a statement of fact — *"Block F moves the corpus to
60"* — which is now false.

## The mechanism is one field written twice, once as a measurement and once as a forecast

`calibration_scope.corpus` identifies the 24-record corpus by a MEASURED pair,
`seed_record_count: 24` and `seed_corpus_digest: 26e4a683…`, with a rule that a
sweep calibrates only if its corpus is *"BOTH identifiable AND equal to the pair
above."* That is exactly right. Its own successor clause identified the next
corpus by **60** — a number nobody had measured, because at the time nobody
could.

`why_the_corpus_had_to_become_part_of_the_rule` closes with *"The data was
already there and the rule did not read it."* **Here the rule read a number that
was never data.**

## What is done

`recalibration_at_60` becomes `recalibration_corpus`: a pair, `record_count` and
`seed_corpus_digest`, **both null**, because Block F has not closed and that pair
is a measurement that does not exist yet. Null blocks nothing that should happen
— there is nothing to re-calibrate at a corpus that does not exist — and the
superseded text is kept beside it. The promotion candidate's restatement is made
identical to the standard it restates, with what it used to say preserved.

Three guards in `eval.test_answer_eval`: every statement of the bar is
enumerated, none may carry a literal record count, and all must name the corpus
in force. **The first draft of those three guards broke FINDING 49** — a computed
list inside a guard label — and the counts moved onto their own note line before
the draft left the session. They join the class of data-driven guards in that
file which `scripts/mutate_part8.py` does not mutate, and that debt is now six
guards rather than three.

---

# Ruling 69 — the corpus lands at 56, recorded as missed

**`total_at_60` is not lowered and `by_tier_at_60` is not lowered. The corpus
ends Block F at 56 with `verbatim_machine_english` at 6 of 10, and both numbers
are reported against the targets they missed.**

*AMENDED by ruling 73, later the same day, and amended on a measurement rather
than an argument. What follows stands as the reading of the HEADLINE number
and is unchanged. What ruling 73 revises is the assumption underneath it —
that the four missing records were interchangeable, and that clearing a
per-region floor needed MORE records rather than DIFFERENT ones.*

A target the corpus missed, recorded as missed, is a result. **A target lowered
to what was delivered is bookkeeping**, and it is the move ruling 56 refused for
the quotation quota four days ago.

## What was refused, and it had the better argument on one axis

Raising F5–F7's allocation by four to reach 60 is **the only route that leaves
`floor.json`'s at-60 clauses untouched**, and neither `F5_START.md` nor
`claude/f5-opening-debt.md` makes that argument. It was refused anyway: four more
records reach 60 only as records. Unless all four were `verbatim_machine_english`
the tier still ends at 6 while the headline reads met — **a corpus that hit its
target and missed the thing the target was for**, which is ruling 56's decoration
arriving on the number the whole block is named for.

And the four would have to be found on a tier where the block has delivered 3 of
7, in a session with one seam named. Planning four more against that record is
planning against a rate this block has never achieved.

## What still has to be re-read against 56

`gloss_capable_records` is done (ruling 68). `floor.json`'s two clauses are done
(FINDING 64). `min_source_language_records_per_region` stays at **4** and is NOT
re-denominated: 4 × 7 = 28 source-language records and the plan provides 31 even
at 56, so the floor remains reachable in aggregate and lowering it would be
fitting the floor to Scandinavia's and Africa's shortfall.
`min_expect_quoted_from_original_cases_at_60` is 6, already delivered at 6 with
21 records still to come, and is left alone.

**Scandinavia and Sub-Saharan Africa end Block F at three source-language records
against a floor of four, and that is now a delivery fact rather than a
prediction.** `ingest.verify` reports it; `check_allocation` cannot, because it
reads the plan and the plan clears the floor in every region.

---

# The three pre-registered predictions

*F4's two were the only predictions this project has ever made. Both came back
usable and neither came back the way its mechanism argued. All three below are
registered before F5's first candidate is examined, and two of them are only
checkable because FINDING 60's `beaten_by` landed first.*

*The F4 baseline they are denominated in, read from
`eval/ranking_runs/20260904T081155+0000-retrievable_chunks_with_distractors.json`
rather than from any document:*

```
pair                             rank   best_other_doc_chunk_id
china-describes-rome-houhanshu      8   eastasia-01-weilue::translation::000
china-describes-rome-weilue         9   seasia-02-oc-eo-site::original::000
vimose-runes                        7   arabia-04-jabal-dabub::original::000
muziris-cargo-akananuru           319   arabia-01-periplus::translation::001
```

## Ruling 70 — `vimose-runes` and the two new Arabian records

**Prediction: after F5's two Arabia `verbatim_with_provenance` records enter the
index, at least one of them appears in `vimose-runes`'s `beaten_by`.**

This is the cleanest subject the corpus offers, and the reason is arithmetic:
`vimose-runes` sits at rank 7, so `beaten_by` names **all six** chunks in front
of it rather than a truncated prefix. A pair at rank 3 would give two.

The mechanism is already measured twice. `floor.json`'s `superseded_diagnosis`
records `scandinavia-03-vimose` at rank 3, sim 0.384, *"behind
arabia-04-jabal-dabub at 0.433 and arabia-03-jsnab17 at 0.401, a pair of
unrelated Arabian inscriptions"*, and the F4 archive has `jabal-dabub` as its
ceiling still. **Two of the six chunks in front of a Scandinavian runic pair are
already Arabian inscriptions, and F5 adds two more.**

**What falsifies it.** Neither new Arabian record reaches the six. Then the
crowding is by those two particular short Semitic inscriptions and not by
"Arabian inscription" as a class — a narrower and more useful statement than the
one on file, and available only because the prediction was written first.

**What it costs if it is right**, and this is why it is worth registering:
curating Arabia measurably damages a Scandinavian gold case that is already a
known failure, and nothing in the allocation accounts for a region's records
degrading another region's retrieval.

## Ruling 71 — the East Asia record and the two `china-describes-rome` pairs

**Prediction: F5's East Asia `verbatim_machine_english` record appears in
`beaten_by` for at least one of `china-describes-rome-houhanshu` and
`china-describes-rome-weilue`.**

Ruling 55 predicted both would fall when F4's East Asian records entered. Both
did — 4 → 8 and 5 → 9 — and F4 read it as *right about direction with its cause
unavailable*, because `best_other_doc_chunk_id` names the ceiling and a ceiling
does not move. **The cause is available for the first time in the F5 run.**

**The known way this can be wrong for a reason that is not about the mechanism,
stated in advance:** both pairs are outside the top 6, so their `beaten_by` lists
ranks 1–6 only. If the new record lands at rank 7 and pushes both pairs further
down, the mechanism will have operated and the interval will not show it.
**F5_RESULT reports both `beaten_by` and `rank` for these two pairs, and if the
ranks fall while the record is absent from both intervals, that is the recall
window and not evidence against FINDING 43.** A prediction whose instrument has a
blind spot has to name the blind spot before the run, not after it.

## Ruling 72 — ruling 67's own test, run for the first time

**Prediction: East Asia's `verbatim_machine_english` slot fills, and at least one
of Persia's and South Asia's does not — and the disqualifying reason in the ones
that fail is that English EXISTS AND WAS FOUND, not that the material is
missing.**

This is the experiment ruling 53 designed and ruling 63 records as never having
run. F5 has set it up so it can be read: one slot on a named seam, two on
traditions FINDING 41 identified, and the outcomes distinguished by REASON and
not only by count.

**What falsifies it, in three directions that mean three different things.** All
three fill: the seam is not necessary, FINDING 41 was over-read, and ruling 67
narrowed too far. East Asia fails too: the seam does not work either and FINDING
45 is weaker than it looks. Persia or South Asia fails on SUPPLY rather than on
found English: that is FINDING 38's problem again and evidence for neither, which
is ruling 53's third outcome and is reported as such rather than folded into a
binary.

**The anti-loophole is ruling 57's and it is load-bearing here.** A curator who
has predicted that Persia will fail can make Persia fail by not looking. Every
unfilled vme slot must carry the named sources consulted and the boundary where
the search stopped; a slot that fails with only *"no English translation found"*
is not evidence for this prediction and F5_RESULT may not count it as such.

---

# FINDING 67 — `total_at_60` is the size of the PLAN, and the file calls it a target

Measured by building the modified mix and running the guards, not by reading them:

```
A   add two slots, change nothing else                   4 problems
B   + new_records 38, by_tier_new vwp 16, at_60 vwp 27   2 problems
C   + region targets Scandinavia 9, Sub-Saharan Africa 10
    "records_by_region_target_at_60 sums to 62, not 60"  1 problem
D   + total_at_60 = 62                                   no problems
```

**There is no configuration of this file in which the allocation places 38 records
and `total_at_60` reads 60.** `check_target_mix` requires the region targets to sum
to it. `check_allocation` requires each region's slots to equal its target minus
its count at 24. The target is derived from the plan by construction.

**A number that must equal the sum of the plan cannot be missed by the plan.** It
can only be missed by delivery — and every figure denominated *"at 60"*, the
per-region floor and the quotation quota and the gloss target and until this
morning two clauses in `floor.json`, is denominated in a number that moves
whenever the allocation moves.

FINDING 51's family, and the deepest instance of it: the block is named for a
number that is structurally its own plan's size. **Nothing is done about it
today.** Separating the plan's total from the target is a re-cut of the field
ruling 44 declared, and it would be made by a session that has already made three
mistakes this afternoon. Named, measured, and owed — and ruling 73 is written so
that it does not have to be taken.

---

# Ruling 73 — two slots are RE-POINTED rather than added, and one of them carries a requirement

**The allocation moves Scandinavia's and Sub-Saharan Africa's `catalogue_record`
slots out of F7 and re-points them as `verbatim_with_provenance` slots in F6;
F6's two Southeast Asian catalogue records go to F7 in exchange. `total_at_60`
and `new_records` do not move. The Sub-Saharan Africa slot declares
`requires_provenance: "local_language"`, and `check_delivery` enforces it.**

```
                                          every guard green
F5   7 slots   vwp 4, vme 3
F6   7 slots   vwp 4, pto 2, cat 1
F7   7 slots   pto 2, cat 5

source-language records at the block's close, floor of 4:
   Arabia 5   East Asia 7   Persia 4   Scandinavia 4   South Asia 5
   Southeast Asia 4   Sub-Saharan Africa 4          ALL SEVEN CLEAR

by_tier_at_60   verbatim_with_provenance 25 -> 27   catalogue_record 19 -> 17
corpus at the close                                 56, unchanged
```

## Why re-pointing and not adding

The session first put a **+2** to the project owner and he took it. Implementing
it produced FINDING 67: two more slots force `total_at_60` to 62, so the number
the block is named for would read *raised* on the afternoon it was recorded as
missed. The re-point buys the same thing — **every region's floor, and Africa's
local-language slot** — for no extra record and no field moving.

**The question was framed badly and this ruling records whose fault that was.**
Ruling 69 asked *how many more records*, and the session inherited the assumption
that clearing a floor needs MORE records. It needs DIFFERENT ones. Ruling 67 had
broken exactly that assumption for the machine-English tier four hours earlier —
re-point, do not add — and the session did not carry it across. FINDING 46's
sentence, twice in one day, by the same party.

## What it costs, stated rather than buried

`catalogue_record` lands at **17 of 19**. That tier is the one F7's own
`why_these` calls *"the cheapest to curate and the one whose absence would cost
the corpus least, deliberately last."* So the trade is the least valuable thing in
the plan for the two most load-bearing records in it — and it is a trade, not a
saving. F5_RESULT and any G3 reading state both numbers.

## The requirement, and why a slot rather than a floor

Ruling 58 asked for a per-region rule refusing a floor met entirely in Greek or
Latin. FINDING 62 showed the rule had to be about PROVENANCE rather than
language, and also that **Sub-Saharan Africa cannot satisfy it**: zero
local-language source records and, before this ruling, no source-language slot in
which to acquire one. A floor nobody can meet is a floor somebody deletes, which
is why FINDING 62 left the distinction counted.

**A requirement on a slot created for that purpose is satisfiable by
construction.** It is declared in the slot, checked for coherence in
`check_allocation` — the value must be in `SOURCE_LANGUAGE_PROVENANCE` and the
tier must actually carry source-language text — and enforced in `check_delivery`
against `source_language_provenance`.

**And it fails on the UNREACHABILITY shape, not the shortfall one**, which is the
distinction that function turns on. Africa's `verbatim_with_provenance` cell holds
two Greek records today against three planned, so the requirement is still
reachable through the slot this ruling created. It becomes a failure only when the
cell is full and no record in it is local-language. **That is the anti-loophole:
the slot cannot be quietly filled with a third Greek record.**

## The supply, and the three outcomes declared before the hunt

`F4_CANDIDATES.md` establishes it, in a passage that ruled the route out for the
opposite reason:

> *"The Polish Nubiological route … is a dead end for this tier for a reason worth
> recording: Polish Nubiology publishes in ENGLISH. Łajtar, van der Vliet, Ochała
> and van Gerven Oei all edit Nubian texts with English translations, and most of
> it is open access. Everything found on that route belongs in LIST A."*

F4 was hunting `verbatim_machine_english`. Nubian was a dead end **because the
English exists and is open** — and LIST A, source text plus a reachable English
translation, is exactly this tier. **What makes a tradition bad for the
machine-English tier makes it good for the provenance tier**, which is the same
asymmetry that moved Arabia's vme slot to East Asia this morning.

Ge'ez is closed on the ROME criterion (ruling 63). Meroitic is closed as a class
(FINDING 44) and closed rightly: it is undeciphered, so the translation path
produces confident nonsense with a British Museum accession number. The two
Nubian candidates F4 named — the Constantinopolitan Creed at Old Dongola and the
Qasr Ibrim epitaphs — are **Greek**, and the requirement refuses both.

**MET.** A local-language record from the region, inside 27 BC to 1204 AD,
touching Rome or Byzantium. Africa's local-language count goes 0 → 1 and its
floor is met with a record the region actually speaks.

**FAILED ON SUPPLY.** No local-language African text inside the window touches
Rome or Byzantium well enough. FINDING 38's problem, ruling 53's third outcome,
and Africa's zero becomes a supply fact that was tested rather than an unexamined
consequence of an allocation nobody revisited. Reported as a SHORTFALL with the
search recorded — and NOT filled with Greek, because the requirement refuses it.

**FAILED ON REACH.** The material exists and sits behind print-only or closed
editions. Ruling 57's boundary, recorded in the same shape.

**The third outcome is written for ruling 53's reason: a close that can only say
MET or MISSED can satisfy itself by choosing.**

---

# FINDING 66 — a mutation whose target has moved proves nothing, and the only thing that noticed was a host run

**This session's own defect, found by the host and recorded here rather than
quietly repaired.**

Ruling 68 relaxed one clause in `ingest/fidelity.py` from `!=` to `<`, and
FINDING 51 replaced a whole reachability expression. Two mutations in
`scripts/mutate_fidelity.py` still named the old text:

```
MISS a gloss-capable record may be dropped from the allocation        (target not found)
MISS an unreachable gloss quota is reported as a shortfall instead
     of a failure                                                     (target not found)
```

**Nothing caught it.** `test_harnesses.py`'s positional-pair guard passed,
because 55 still equals 55 and a length says nothing about whether a target
exists. Every suite passed, because a suite is indifferent to what a harness
names. The mutation count read 55 in three places. The only detector in this
repository was running that one harness on the host, and the two guards those
mutations protect had spent the interval unproven while reading as covered.

## The generalisation, performed rather than scheduled

FINDING 46's sentence is that a defect is fixed in the file where it was found
and the search for its siblings is a separate act nobody schedules. So the search
was run across all nine harnesses: **eight were clean and the ninth was the one
already known.** That is what makes this worth an assertion rather than a note —
a rule that eight of nine already satisfy is a rule, and one that half satisfy is
a preference.

`test_harnesses.py` now checks it. 33 -> 43 assertions:

- every mutation target that is a string literal must still occur in the sources
  a harness could be pointed at — the harness files themselves excluded, because
  a target's text is a literal *inside* the harness and a search that included
  them would find every target exactly where it was written and prove nothing;
- the searchable corpus is counted, so a collapsed glob cannot pass every guard
  by finding nothing to contradict it;
- a target absent from every source really is reported absent, so a clean result
  is a reading and not an empty haystack;
- targets that are **not** string literals are COUNTED and named — seven of them
  — because a target this cannot read is not a target it has verified.

**It does not reuse `_literal`, and the reason is the finding again.**
`_literal` runs `ast.literal_eval` over the whole `MUTATIONS` list and returns
`None` the moment one entry interpolates a module constant. `mutate_fidelity.py`
does exactly that, which is why it reports `MUTATIONS=-` in the positional-pair
line — **so a check built on the existing reader would have skipped the one file
this defect was found in.** A new reader walks the AST entry by entry and counts
what it cannot evaluate.

## What this does not fix

`scripts/test_harnesses.py` is mutated by nothing. Its own guards — now
forty-three of them — have no mutation proving they can fail, which is the same
class as the six in `eval/test_answer_eval.py` and is not new here. And
`mutate_distractors.py` still inlines its mutations rather than declaring a
`MUTATIONS` list, so it is the one harness this check reports on and cannot
check: no BASELINE block, no positional pair, and now no target verification.
Three separate instruments cannot see the harness that mutates the SCHEMA.

**The sentence that travels: the length of a mutation list says nothing about
whether its targets exist, and a mutation that proves nothing reads exactly like
one that proves something until somebody runs it.**

---

# FINDING 66, continued — the check asked whether a target EXISTS, and the stricter question caught the next defect an hour later

The guard above asks whether a mutation's target still occurs in the sources it
names. Writing ruling 73's mutations produced one whose target — `if unknown:` —
matches **three** lines in `ingest/fidelity.py`, two of them at the same indent.
A harness applies its mutation with `str.replace`, which changes every
occurrence, so that mutation would have broken three rules while claiming one.

**The check passed it.** *Exists* and *occurs exactly once* are different
questions and the weaker one was asked. Strengthened to exactly-once, it went red
on **three harnesses that have been green for the whole block**:
`mutate_fidelity`'s `if both:` at three places and `if stray:` at two,
`mutate_ranking` at three targets, `mutate_recover` at one.

**None of them is false.** The named guard does fail in every case, because one
of the replacements broke it; the others are collateral. Widening six targets
across three working harnesses is a change nobody asked for, on the last
afternoon, by a session that has already made three mistakes.

**So it is COUNTED, and the demotion is FINDING 56's precedent applied to
itself:** *writing the checker for a rule is an invitation to write a stricter
rule by accident*, and the stricter idea survives as a counted line. Second time
today. What would make it assertable is what made the weaker line assertable — a
session that widens the six, finds the population clean, and asserts a rule the
population already satisfies.

The one target written today was widened rather than counted, because a target
written this afternoon has no claim on the exemption.

**The sentence that travels: the check written to catch a mutation that proves
nothing was, within the hour, the check that let one through — by asking the
weaker of two questions it could have asked.**

---

# What is NOT done, and is owed beyond this document

- **`scripts/mutate_part8.py` still does not mutate `eval/test_answer_eval.py`.**
  That file's data-driven guards with no mutation proving they can fail were
  three; FINDING 64 added three more, so the debt is **six** and F5 made it
  worse rather than better. Named here so nobody has to re-derive it.
- **FINDING 58's shared matcher.** Nine copies of one three-line rule.
  `scripts/test_harnesses.py` stops them drifting and does not make them one, and
  it reports that `mutate_places.py` still slices on `split("FAIL", 1)` where the
  other eight slice on `split("FAIL ", 1)`.
- **`scripts/mutate_distractors.py` has no BASELINE block**, it declares no
  `MUTATIONS` list, and its targets cannot be verified either — three
  instruments blind to the one harness that mutates the SCHEMA (FINDING 66).
- **`scripts/test_harnesses.py` is mutated by nothing.** Its guards have no
  mutation proving they can fail, and F5 added ten of them.
- **Six mutation targets across three harnesses match more than one line**
  (FINDING 66, continued). Counted, not gated, and the condition for
  asserting it is written there.
- **`total_at_60` is the size of the plan and the file calls it a target**
  (FINDING 67). Separating the two is a re-cut of the field ruling 44
  declared, and ruling 73 was written so it did not have to be taken today.
- **Ruling 65's renderings debt** — the eight Part 2 pairs. The C2 fused arm has
  now gone two tranches without a reading.
- **The per-region floor is still checked against the PLAN only.** Scandinavia
  and Africa end below it and `check_allocation` stays green, because the plan
  clears the floor in every region. FINDING 65's shape, one field over, and F5
  did not fix it: a delivery-side per-region floor check would fail the tree on
  two regions whose shortfall is already recorded and cannot be recovered.
- **`scripts/test_recover_baseline.py` could not be run in this session's bridge
  at all** — `psycopg` is absent there — which means the F4 handover's bridge
  column for that suite came from a different environment than this one. Not a
  defect in the repository; recorded so the next session does not read a bridge
  number as reproducible.

---

# The sentences that travel, out of F5

**All four records the block is short are one tier, and the corpus lands at 56
because the machine-English tier lands at 6.**

**One Greek text supplies a source-language record to three different regions,
and the rule written to stop an aggregate being met inside two regions cannot see
a text counted in three.**

**A language rule would have refused the two records ruling 58 argued to keep and
admitted the one it should refuse, because what separates them is not the
language but whether the region is speaking or being spoken about.**

**The guard asked whether enough slots remained when the scarce thing was
declarations, so the new one counts both and says which binds.**

**One standard was written in three places against the risk of being
renegotiated, and the copy that drifted is the one a reader of that case
actually meets.**

**A ruling taken on delivery evidence is not the experiment that was designed,
and a session that says so is worth more than one that lets the two wear the same
clothes.**
