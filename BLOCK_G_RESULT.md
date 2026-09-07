# BLOCK G RESULT — **PHASE 2 EXITS ON A PIVOT.** Q1 no, Q2 yes about a corpus
# that no longer exists, Q3 no. **G3 IS CLOSED AND FAILED ON NINE BOXES.**

**The shape of this verdict was written and committed before this document
existed** — `BLOCK_G_VERDICT_SHAPE.md` at `526af18`, per `BLOCK_G_START.md` §8
step 5. That file records, against interest, that three pieces of evidence were
assembled before it was written. **Nothing in this document amends a gate,
rewords a box, lowers a target, curates a record or runs a sweep.**

---

## THE STATE BLOCKS ARE GENERATED. NOTHING BELOW THEM IS RESTATED.

Run by `python -m ingest.verify --state` on 2026-09-07. PASTE THIS BLOCK. Do not restate it.

```
documents: 54   chunks: 170   parallel pairs: 33
note: paraphrase flag LIFTED on 'weilue': LIFTED 2026-08-22, FINDING 11. eastasia-01-weilue's original_text_excerpt is 221 verbatim characters from zh.wikisource 三國志/卷30 and classifies as verbatim_original on its own merits. The manifest's flag marked SUSPICION and nothing in the pipeline ever turned suspicion into a determination; when two of its entries were finally checked they came back opposite ways. Leaving the flag on would have the corpus report a sourced text as paraphrased.
note: retrieval-eligible non-English chunks by language: {'xsa': 2, 'xna': 2, 'arc': 3, 'grc': 16, 'lzh': 7, 'pal': 6, 'xpr': 2, 'non': 1, 'gmq-pro': 3, 'oty': 1, 'san': 2, 'ocm': 1, 'omy': 2, 'gez': 1}
note: W1 placements: 53 placed + 1 declared unplaceable = 54/54 considered (G1's target was 24, met), 32 with a named place (G1 wanted 17), 66 distinct gazetteer ids, 1 contested (G1 criteria 1 and 3). Grounds: {'identified': 3, 'regional': 96, 'stated': 70}. Resolution is not checked here — run `python -m ingest.gazetteer --check`, which is the only thing that turns an id into a coordinate.
note: rights positions (ruling 74, column built in F6): {'open_licence_stated': 5, 'permission_stated_no_licence': 3, 'public_domain': 2, 'all_rights_reserved': 2, 'states_no_terms': 1, 'two_positions_stated': 3, 'unread': 38}. 38 of 54 record(s) are UNREAD -- nobody has read that source's rights position since FINDING 69, which was produced by two licence claims that were wrong in opposite directions in a single session. `unread` is a state of this project's knowledge and not of the source. COUNTED, NOT GATED, and never derived: citation_original is prose, and a matcher over it would read the word `open` in a sentence about reachability, which is FINDING 69 with a regular expression in front of it.
note: quotation cases: 9 ask WHICH chunk was quoted (target 6 at 60) and 4 ask only WHETHER anything resolved. Ruling 56: they are two questions under one name. The second line rises by construction with every verbatim_machine_english record, so a total that is climbing is not evidence that this system quotes sources rather than translations.
note: record tiers: verbatim_with_provenance 29/29, verbatim_machine_english 4/10, published_translation_only 4/4, catalogue_record 16/16, pointer_only 1/1 (F1 target at 60 records). Progress, not a threshold: the mix is a target for the end of Block F and a suite that failed on it throughout would be ignored throughout.
note: source-language records by region (F1 floor 4 each at 60): {'Arabia': 6, 'East Asia': 7, 'Persia': 4, 'Scandinavia': 4, 'South Asia': 4, 'Southeast Asia': 4, 'Sub-Saharan Africa': 4}. Below the floor: none. An aggregate tier target met entirely inside two regions leaves the other five exactly as unable to answer a source-text question as they are now.
note: allocation (ruling 51): F3 8, F4 7, F5 7, F6 7, F7 7 = 36 record(s), every source-language record before every catalogue record. The sub-tranche a record was curated in is NOT a field on the record and is not derivable from one: this line reports the PLAN, and data/curation_cost.json in curation order reports what happened.
note: delivery against the allocation: 30 of 36 tranche record(s) curated. Gloss-capable declared 7/7 (5 contested_reading, 2 hedged_identification), with 0 declaration(s) left in sub-tranches still open and 0 slot(s) left on a tier that can carry one. The DECLARATIONS are the scarce number: slots are plentiful by construction, and a guard that read them reported an unreachable quota as progress for two sub-tranches (FINDING 51). A SHORTFALL is progress and is reported here; an UNREACHABLE quota is a failure above, because a target that can no longer be reached has already been missed and nobody re-curates a record.
note: source-language records by PROVENANCE rather than by language (ruling 58, in the shape FINDING 62 gave it): is the region SPEAKING, or being SPOKEN ABOUT? Arabia 6 = 5 local + 0 empire-language from the region + 1 about it, so 5 SPEAKING and 1 spoken about; East Asia 7 = 7 local + 0 empire-language from the region + 0 about it, so 7 SPEAKING and 0 spoken about; Persia 4 = 4 local + 0 empire-language from the region + 0 about it, so 4 SPEAKING and 0 spoken about; Scandinavia 4 = 4 local + 0 empire-language from the region + 0 about it, so 4 SPEAKING and 0 spoken about; South Asia 4 = 2 local + 0 empire-language from the region + 2 about it, so 2 SPEAKING and 2 spoken about; Southeast Asia 4 = 4 local + 0 empire-language from the region + 0 about it, so 4 SPEAKING and 0 spoken about; Sub-Saharan Africa 4 = 1 local + 2 empire-language from the region + 1 about it, so 3 SPEAKING and 1 spoken about. Regions with no source-language record in a language of the region: []. Regions with NO RECORD SPEAKING AT ALL -- neither in a language of the region nor in an empire language from it: []. FINDING 68, closed in F6: those two lists are different questions and only the first was ever printed, so a region whose own rulers wrote in Greek was reported in the same words as a region that is only ever written about. One text counted as a source-language record in more than one region: [[('Arabia', 'arabia-01-periplus'), ('South Asia', 'southasia-02-periplus-muziris'), ('Sub-Saharan Africa', 'africa-03-periplus-adulis')]]. COUNTED, NOT GATED. A language-only rule -- the one ruling 58 proposed -- cannot tell a record whose findspot is in the region from a Roman-world text about it, because both are grc, so it would refuse the two records ruling 58 argued to keep and admit the one it should refuse.
note: curation cost: 30 record(s) timed, 24 excused, 6 RETIRED (ruling 52: kept and named, counted in no mean). Comparator: within_tranche (ruling 46 -- nothing records what record 12 cost). Run `python -m ingest.cost_log report` for the per-tier table; it is the only place a curation-cost number may be read from.
loader warnings: 8
  ! arabia-02-palmyrene-tariff: empty reference_translation, no translation chunk emitted
  ! eastasia-06-cefu-yuangui: empty reference_translation, no translation chunk emitted
  ! eastasia-09-jiutangshu-fulin: empty original_text_excerpt, no original chunk emitted
  ! eastasia-07-tang-huiyao: empty reference_translation, no translation chunk emitted
  ! southasia-06-cosmas-taprobane: empty original_text_excerpt, no original chunk emitted
  ! seasia-06-kedukan-bukit: empty reference_translation, no translation chunk emitted
  ! seasia-07-talang-tuo: empty reference_translation, no translation chunk emitted
  ! africa-07-cosmas-sasu: empty original_text_excerpt, no original chunk emitted

All integrity checks passed.
```

Run by `python scripts/state_block.py` at 526af18 on 2026-09-07. PASTE THIS BLOCK. Do not restate it, and do not compute a figure in it from another figure -- FINDING 76.

```
ingest.verify                        green, 54 documents
ingest.test_fidelity                 115   [green]
ingest.test_cost                     78   [green]
eval.test_answer_eval                425   [green]
eval.test_ranking_check              258   [green]
answer.test_answer                   150   [green]
ui/test_build_ui_data.py             19   [green]
scripts/test_recover_baseline.py     56   [green]
scripts/test_harnesses.py            43   [green]
python -m ingest.gazetteer --check   GREEN
node ui/check_ui.mjs                 GREEN
```

*The same table was produced at `b12ed34` at this block's open, before anything
else was read, and again at `526af18` after the verdict shape was committed.
Identical both times.*

**Both blocks reproduce `BLOCK_G_START.md`'s, note for note and row for row.**
That was §8 step 1's condition for reading anything else and it was met before
anything else was read. The tree moved from `20793e6` to `b12ed34` by two
document commits and nothing else; `git status` was clean at the block's open.

*The mutation harnesses are HOST ONLY (FINDING 59). Block G did not re-run them
and does not report a figure for them: F7's readings —* `mutate_fidelity`
**70/70**, `mutate_cost` **58/58** *— stand as F7 recorded them, and no record,
guard or source has moved since.*

---

# 1. THE VERDICT

```
PHASE 2 EXITS ON A PIVOT.

Q1  Does ranking survive scale?              NO
Q2  Can improvement be distinguished
    from noise?                              YES as asked, and the pass does
                                             not transfer to this corpus
Q3  Does curation get cheaper?               NO

G3                                           CLOSED AND FAILED, nine boxes
G4                                           CLOSED, five boxes, unchanged
```

**PIVOT and not KILL.** The corpus is real and it is green: 54 records across
seven regions, every per-region source-language floor met, four of five tiers on
their target, every integrity check passing, eleven suites green, and the only
answer-path observation taken above 24 records meeting the floor. Nothing here
says stop.

**PIVOT and not PERSEVERE.** `PHASE2_PLAN.md` conditions persevere on *passing
all three*. None of the three passes.

**The plan's own consequence for a failed Q1 is adopted and not softened.**
*"Failing 1 makes the product corpus-bound, and the honest move is the one the
plan names: polish the sourcebook at 24–60 records rather than chase 200."*
**200 is off the table.** It is not deferred, not staged behind a fix, and not
conditional on the next tranche. A later session that wants 200 back is
re-opening this verdict and should say so.

## THE SEQUENCING AFTER PHASE 2 WAS DECIDED INDEPENDENTLY OF THIS VERDICT

`PHASE2_PLAN.md` reads *"passing all three unblocks the knowledge graph."* **The
knowledge graph was deprioritised on separate grounds before this block ran, and
the UI — chatbot, map, click-through citation — is next regardless of what this
document concluded.** A pivot verdict did not choose the UI and a persevere
verdict would not have chosen the graph. A later reader who finds the UI work
immediately after this verdict will otherwise infer a causal link that was not
there. Amendment 1 §5, and it was written before this block ran.

---

# 2. G3 IS CLOSED AND FAILED, BOX BY BOX

**Every box below was re-verified in this session rather than copied from
`BLOCK_G_START.md`.** The command that produced each reading is named beside it,
because a box whose state is inherited from the document that predicted it is a
box nobody checked.

```
box                                                       state    read from
1  60 records, all seven regions, ALLOCATION delivered     NOT MET  ingest.verify --state
       54 records; seven regions present, every per-region floor met;
       allocation delivered 30 of 36
2  three sessions at 60 on three distinct UTC dates,       NOT MET  ls eval/sweeps
   calibrated:true re-written at 60, weilue-chinese-
   quotation and vimose-runes resolved
       ZERO sessions at 60. The last full sweep archived is 2026-08-28, at
       the 24-record corpus. The only later answer-path run is one 3-case
       probe on 2026-08-31 at 30 records, which archives to eval/probes and
       never to eval/sweeps, by design. The floor is still calibrated at 24
       and pinned there by digest 26e4a683… (ruling 49)
3  curation cost per record recorded and TRENDING DOWN     NOT MET  ingest.cost_log report
       recorded, yes: 30 timed, 24 excused, 6 retired. Trending: every tier
       prints NOT A TREND and the report closes NOT YET A COST CLAIM
4  full sweep re-run at 60, content pass rate not lower    NOT MET  ls eval/sweeps
5  per-session stability at 60                             NOT MET  ls eval/sweeps
6  cross-session answer-text agreement at 60               NOT MET  ls eval/sweeps
7  ranking gold set still ≥95% top-6                       NOT MET  20260906T170622 archive
       0.6591 by pair, 0.7317 by unit. AND SEE §4: the number the word
       "still" refers to was taken in a configuration no run since
       2026-08-31 has used, so on that denomination the box is also
       UNMEASURED. Both readings leave it NOT MET
8  ui/build_ui_data.py --verify clean, ZERO moved/absent   NOT MET  build_ui_data.py --verify
       moved 1, absent 1 — and BOTH are africa-03-periplus-adulis, the same
       record as debt row 8. One record fails this box
9  confidence profiles recalibrated, calibrated set        NOT MET  confidence_profiles.json
   honestly
       prose calibrated:true; documentary, inscription and verse all
       calibrated:false, still at the n=1 and n=2 observations of 2026-08-10
10 only then, 200                                          MOOT
```

**Nine boxes, none met, and box 10 moot.** Box 9 remains the only one that could
have been closed by work rather than by records, and it needs machine
translations to observe — which is the tier that ended 4 of 10.

## FOUR OF THE NINE WERE UNREACHABLE, NOT MERELY UNDONE

Boxes 2, 4, 5 and 6 all read *"at 60"*. There is no 60-record corpus and there
was not going to be one. **A gate box that cannot be reached is a box that has
already been missed** — FINDING 51's distinction between a shortfall and an
unreachable quota, applied to a gate rather than to a declaration.

## G3 IS NOT AMENDED, AND HERE IS WHAT WAS OFFERED AND REFUSED

This block found two things that would each have made a comfortable argument for
softening a box. **Both were refused, and both are recorded here so that the
refusal is visible rather than assumed:**

- **FINDINGS 82 and 86 together mean the corpus cannot currently accept a modern
  non-English institutional source at all.** That is part of the explanation for
  why `verbatim_machine_english` ended 4 of 10 and therefore why the corpus
  ended at 54. **It is not a reason to reword box 1.** Amendment 1 §0 said so
  before this block ran, and ruling 56 refused the same move when F3 delivered
  six of eight.
- **Box 7's ≥95% was measured in a configuration no Block F run uses** (§4).
  That does not lower the box, does not make 0.6591 acceptable, and does not
  make the box passable. It makes it fail in two ways instead of one.

**`total_at_60` stays 60. Ruling 69 is undisturbed. No box text was changed.**
The Gate G3 checklist in `PHASE2_PLAN.md` now carries a dated banner recording
that it is closed and failed and pointing at this document; every box beneath it
is verbatim as it was written, unticked.

**There is no `G3.closed` flag in the repository.** Gates in this project are
markdown checklists, and no JSON or Python file carries gate state — checked by
listing every tracked `.py`, `.json`, `.mjs` and `.yaml` file that mentions G3
and reading each hit. The banner is therefore what "closed and failed" is, and
it says both words.

---

# 3. THE THREE QUESTIONS

## Q1 — DOES RANKING SURVIVE SCALE? **NO.**

`BLOCK_G_START.md` §2 put two readings on the table and required an explicit
choice between them. **The answer is "No", and the second reading is recorded as
true about the measure and refused as the answer.**

### What was already known

```
run                                    records  chunks   recall@6 (pairs)  (units)
20260906T091154  before F6                  43     524     0.7273 (32/44)   0.8049 (33/41)
20260906T103920  after F6                   47     544     0.6818 (30/44)   0.7561 (31/41)
20260906T170622  after F7                   54     561     0.6591 (29/44)   0.7317 (30/41)
```

0 better / 36 worse across three record-adding runs (FINDING 84's series), and
the only run in which pairs improved is `FINDING 77`'s, where 393 distractors
LEFT the index. FINDING 91 then showed that eight of F7's thirteen falls had no
new chunk in the pair's window at all, and that
`bronze-heracles-verethragna-from-mesene` fell nine ranks with a `beaten_by`
identical entry for entry and a similarity gap identical to four decimal places.

### Why the second reading is refused as the answer

Reading 2 — *`recall@6` over a fixed gold set is partly a measure of index size
with the sign flipped* — **is true, and this document says so.** FINDING 91 is
the proof and FINDING 77's shrinking-index run is the natural experiment.

It is refused as the ANSWER for the reason §2 stated in advance: taking it
obliges Block G to deliver a replacement measure **and** the sentence that would
have falsified it, and **a measure chosen by a session that has already seen the
run is FINDING 83 at gate scale.** The defect is recorded as instrument debt
owned by W2, and its one binding condition is a timing one: **the replacement
measure is declared BEFORE the next record-adding run, never after.** That is
the only moment at which declaring it is legitimate, and it is why the debt
carries `open` rather than a date.

### THE FINDING THAT CHANGES WHAT Q1 IS ABOUT

**FINDING 92 — the degradation is entirely on non-English targets. Not one
English-target pair has moved.**

`recall@6` split by the pair's `expect_lang`, over the comparable archived runs:

```
run                chunks   expect_lang = en   expect_lang ≠ en
20260816T073652       450        8 / 9              19 / 24
20260904T081155       473        8 / 9              24 / 35
20260906T170622       561        8 / 9              21 / 35
```

**Eight of nine, three times, across a 3.7× growth in the index — and eight of
nine in ALL TWENTY-SEVEN archived distractor runs**, at every index size from
151 chunks to 561, under every configuration the project has ever run, collapsed
and reranked ones included. **No English-target pair has changed state in any
archived run, ever.** The non-English denominator moved from 24 to 35 when the
gold set expanded, so that column mixes composition with degradation; the English
column has a fixed denominator of nine and is the clean reading. Every pair Block
F lost, and every pair the gold set's expansion added and failed, is a
non-English target.

The `archived_answer` cohort is the same statement at its sharpest. All eight of
its pairs are non-English targets, and their targets were taken from what
retrieval itself returned in archived answer runs — **so the cohort's
construction is biased toward passing, and it passes one in eight:**

```
pair                              450 chunks / 24 records   561 chunks / 54 records
muziris-cargo-periplus                  5                        5     ok
muziris-cargo-papyrus                 109                      139
muziris-cargo-akananuru               309                      373
china-describes-rome-weilue             5   ok                  13
china-describes-rome-houhanshu          4   ok                  11
vimose-runes                            3   ok                  20
aksum-trade-adulis                     35                       53
adulis-exports                         15                       15
                                     ----                     ----
                                    4 of 8                    1 of 8
```

**`vimose-runes` went from rank 3 to rank 20.** It is also the case demoted from
`required_cases` in `floor.json`, whose reinstatement bar is 3/3 in three
sessions on three distinct dates. Its retrieval rank fell by seventeen places
while the corpus more than doubled.

**So Q1's answer is "No", and it is narrower and worse than "retrieval degrades
with scale".** Retrieval of English targets did not degrade at all. What degraded
is the cross-lingual link — which is the thing this project exists to do, and the
thing the brief names in its own words: *"Particular interest in relevant local,
non-English sources from the regions above."*

### THE PREDICTION FOR THE NEXT RECORD-ADDING RUN — Amendment 1 §4

**Written before that run exists, and before the six records it will add exist.**
Four predictions, each naming its own refutation, in the shape Block F used.

The next work re-opens the vein FINDINGS 82 and 86 blocked and points at roughly
six more records, all `verbatim_machine_english`. F7's seven records added 17
chunks, so six records is on the order of fifteen chunks against 561 — call it
2.7% index growth, against FINDING 91's rate of roughly three ranks per hundred
per three per cent.

```
PG1  recall@6 (ALL, pairs) falls from 0.6591 or holds, and NO gold pair improves.
     REFUTED BY: any gold pair improving its rank.

PG2  Pairs ranked above 100 fall by roughly 3% of their current rank —
     muziris-cargo-akananuru 373 -> about 384, muziris-cargo-papyrus 139 ->
     about 143, bronze-heracles 113 -> about 116 — and every pair at rank 1
     or 2 loses nothing.
     REFUTED BY: a pair at rank 1 or 2 losing its place, OR any pair above
     rank 100 moving by less than 1 rank or by more than 10% of its rank.

PG3  expect_lang = en stays 8 of 9.
     REFUTED BY: it moving in either direction, including upward.

PG4  The six new records enter beaten_by lists through their TRANSLATION
     chunks and not their ORIGINAL chunks — F7's P4, restated for a tier
     whose originals are non-English and whose English is machine-made.
     REFUTED BY: any `::original::` chunk of a new record appearing in any
     beaten_by list in the run.
```

**A verdict about whether ranking survives scale, written immediately before six
more records land and not accompanied by a prediction, is a verdict that will be
read afterwards with an explanation available for whatever happened.** These four
cost one paragraph and they are the cheapest thing in the block.

## Q2 — CAN IMPROVEMENT BE DISTINGUISHED FROM NOISE? **YES, AND THE PASS DOES NOT TRANSFER.**

**G4 is closed on all five boxes and stays closed.** Its deliverable was the
variance decomposition and not the pass rate, and the decomposition exists:
`floor.json` records per-case stability 132 of 132 cells and per-session
agreement 31 of 33 pairs, calibrated from four sessions on 2026-08-28.

**That answers the question the phase asked.** Session variance is small relative
to case variance at that corpus; improvement is distinguishable from noise there.

**And it is about a corpus of 24 records.** Ruling 49's corpus clause pinned it
there by digest, deliberately and in advance, so nothing since can recalibrate
it — and Block E's 74–77% and 45% cross-session figures are context and not
thresholds, because a gate comparing across the two corpora would be measuring
the corpus move it was meant to survive.

**Does it count for a 54-record corpus? No, and the honest form of that sentence
is that nobody has looked.** The only observation above 24 records is F3's floor
probe of 2026-08-31 — three cases, nine runs, one session, at 30 records: content
1.0, grounded 1.0, `meets_floor: true`. It is below `min_cases_per_sweep` and on
one date, so it is inadmissible as calibration by a rule declared before it ran,
and it archived to `eval/probes` exactly as designed. **It is one green light on
three of thirty-three cases and it is the whole of what is known.**

## Q3 — DOES CURATION GET CHEAPER? **NO.**

`python -m ingest.cost_log report` is the only place a curation-cost number may
be read from (FINDING 75), and this section names what it says rather than
restating a figure from it.

The box reads *"curation cost per record recorded and TRENDING DOWN"*. **Recorded
is met. Trending is not, and cannot now be.** Every tier prints `NOT A TREND`:
three are below the n=10 floor, and `verbatim_with_provenance` is above the floor
and is refused a trend anyway by FINDING 70, because its minutes come from four
agents and a model apportioning its own wall clock produces smaller, smoother
numbers than a person timing themselves. The report's own closing line is
`NOT YET A COST CLAIM`, and the declared mix it waits on is now permanently unmet.

**Whether that counts as a pass was Block G's call and the call is no.** A box
that asks for a trend and gets a refusal has not been met.

**What is worth more than the number, and is the reason this is a failed box
rather than a failed instrument:** the ledger was built, kept for thirty records
across five sub-tranches, and it **refuses to answer the question it was built
for, for reasons it states itself, in its own output, unprompted.** An instrument
that declines to produce a figure it cannot support is the opposite of the
failure mode this project has spent Phase 2 guarding against. The retired rows
are the part to read — `seasia-vme-hunt-unresolved` at nine minutes and
`persia-vme-hunt-unresolved` at twenty are hunts that produced no record at all,
kept and named so that the cost of the missing tier is visible rather than
absent.

---

# 4. FINDING 93 — THE ADOPTED RANKING CONFIGURATION WAS DROPPED, AND NOTHING RECORDS THE DECISION

**Block C adopted `--with-distractors --collapse --rerank` on 2026-08-16, wrote
the words *"the configuration is now declared, because C5-C6 must measure a fixed
one"*, and restated it as frozen at Block C's close on 2026-08-20.** The 29/30 =
0.967 that closed G2's `top 6 for >=95% at 450` box was measured under it, and
`PROGRESS.md` records the reading twice with the words `collapse + rerank` beside
it.

**Every ranking run archived since 2026-08-31 was taken without `--collapse` and
without `--rerank`.** The runs record it themselves — `collapsed: false`,
`reranked: false` — F3's runbook prescribes bare `python -m eval.run_ranking_check`,
and `PROGRESS.md`'s last mention of either flag is at Block C's close. **No
ruling, no result document and no finding records the change.** Ruling 65 is
about the FUSED arm and says nothing about collapse or rerank; FINDING 77 later
restored `--with-distractors` and did not restore the other two.

## What this does and does not do to box 7

G3 box 7 reads *"ranking gold set **still** ≥95% top-6"*. The word *still* points
at 29/30 under collapse + rerank at 450 chunks and 24 records. **The 0.6591 it is
being read against is a different measurement of a different configuration.**

**It does not rescue the box.**

- 0.6591 fails ≥95%. That reading stands exactly as it stood.
- On the configuration the ≥95% was adopted under, **there is no reading at 54
  records at all**, so the box is additionally UNMEASURED in its own denomination.
- **0.8182 is the highest `recall@6` in any of the 34 archived ranking runs, in
  any configuration, at any index size** — checked across every archived run with
  an aggregate, collapsed and reranked ones included.

Box 7 fails in both readings and is recorded as NOT MET on the number that was
taken. **A defect found after a gate failed does not soften the gate. It is
recorded, it is booked, and the gate stays where it fell.**

## THE PREDICTION FOR THE COLLAPSE+RERANK RUN — written before the run exists

The cheapest measurement that would answer Q1 in the denomination the gate used
is one run of the adopted configuration at 561 chunks: ~90 seconds and ~30 rerank
requests on the host. **It is booked, not taken here**, and this prediction is
written first so that the run cannot be fitted to a verdict already known.

```
PG5  recall@6 under --with-distractors --collapse --rerank at 561 chunks lands
     ABOVE the bare 0.6591 and BELOW 0.95, and box 7 fails on it too.
     MECHANISM: collapse removes same-document competitors from the window —
     muziris-cargo-periplus is beaten in part by another chunk of its own
     record — and rerank reorders the top 50, so both help most exactly where
     Block F's falls are.
     REFUTED BY, in either direction, and both refutations are informative:
       (a) it reaches >=0.95, which would mean the whole Q1 fall is a
           configuration artefact and box 7 was measurable all along; or
       (b) it lands at or below 0.6591, which would mean the adopted
           configuration buys nothing at this corpus and G2's 29/30 was
           itself an artefact of 450 chunks and 24 records.
```

**And the guard that matters:** if PG5 is refuted by (a), **G3 still stands
FAILED.** A gate is not re-opened by a run taken after it closed, by a session
that knew the result. Refutation (a) would be a finding for the block that takes
the run and an argument for how the NEXT gate should be denominated — never a
retroactive pass.

---

# 5. THE ONE NUMBER THAT SHOULD WORRY THE READER

## **`archived_answer` recall@6 is 0.125 — one pair of eight — and it was four of eight at 450 chunks.**

Not `muziris-cargo-akananuru` at rank 373. That pair is the obvious choice, has
been the obvious choice since Block C, and `BLOCK_G_START.md` §3 item 3 said in
advance that its obviousness was a reason to check the others. It was checked. It
is one pair, it is named, it is diagnosed, and it already travels with its own
sentence.

**Why this one instead.**

- **All eight of its pairs are non-English targets.** It is not a cohort that
  happens to score badly; it is the cross-lingual link measured directly, and the
  cross-lingual link is the product.
- **Its construction is biased toward passing.** These pairs name chunks
  retrieval itself returned in archived answer runs. The system is being asked to
  find, again, what it already found once — **and it finds one in eight.**
- **It halved and halved again while no headline moved.** 4 of 8 at 450 chunks,
  3 of 8 at 460, 1 of 8 from 473 chunks onward. The whole of that collapse
  happened inside Block F and none of it appears in a Block F result document,
  because every result document read the aggregate.
- **`BLOCK_G_START.md` §5 item 18 records 0.125 and does not record that it used
  to be 0.500.** A standing number recorded without its history reads as a
  property of the corpus. It is a trend, and it points down.

The sentence that travels with it is the one `BLOCK_G_START.md` §5 item 14
already wrote, and it turns out to have been about the whole system rather than
about one pair:
***29/30 is whether the RECORD was found; 22/30 is whether the NON-ENGLISH TEXT
was reachable.***

---

# 6. THE FREEZE, DECIDED AS A DECISION

Four things are frozen. **The closing summary is what preserves the meaning of
the numbers the freeze protected, so a freeze released in the same document that
records the numbers is released safely and a freeze released quietly three weeks
later is not.** Each is named, and each gets a verdict.

```
frozen thing                     survives the close of Phase 2?
1  the prompt, p7-answer-v2r      YES — and the UI work is what releases it
2  chat-default (haiku-4-5, t=0)  YES — and it stays frozen indefinitely
3  the corpus digest 26e4a683…    YES as a PIN, released only by a completed
                                  recalibration at 54 records
4  scripts/schema-part7.sql       YES — additive only
```

**1 — `p7-answer-v2r`. Survives, and the UI work is what releases it.** Rule 3
permits a quotation from the source text *or* from the English shown for that
source and requires neither, which is FINDING 13 and is why the answer path
quotes translations. Click-through citation will want that changed. **Three
things must travel with that change and are recorded here because the session
that makes it will not otherwise know them:** every archived answer number
becomes historical; `p7-answer-v2r` stays in `ANSWER_PROMPTS` beside v3 and v4
rather than being edited in place, which is already this file's pattern; and
**the floor is denominated per prompt version by construction** — `floor.json`
keys its verdicts on the prompt version — so a new version starts with **no
calibrated floor at all**, and earning one costs the same three sessions on three
distinct UTC dates and ~270 chat calls as the corpus recalibration does.
**Therefore: if the prompt and the corpus are both to move, move them together
and recalibrate once.** Two separate recalibrations is the same money twice.

**2 — `chat-default`, haiku-4-5 at temperature 0, ruling 22. Survives, and there
is no schedule for releasing it.** `gateway/config.yaml` already carries the
argument in its own comments: Part 6's translations and Part 7's answers were
measured on haiku, and repointing the alias would silently make every archived
number incomparable. The second alias exists for exactly this and is the route
for anything stronger. **A model swap on this alias is a re-baseline of the whole
archive, not a configuration change.**

**3 — the corpus digest `26e4a683…`. Survives as a pin, and the booking it
protects stands.** `F7_RESULT.md` handed Block G one open question — recalibration
was booked for 60 records, three distinct dates and ~270 chat calls, and the
corpus ended at 54. **The booking stands and the corpus reads 54.**
`floor.json`'s `recalibration_corpus` rule already says *"the corpus in force at
Block F's close"*; FINDING 64 corrected that wording in F5, before the corpus
landed, by a session that could not know what the number would be. So 54 is what
the rule names, and the price is unchanged. **The digest itself is not written
here:** `answer_store.corpus_version` reads it from the database and this block
ran on the bridge, so `recalibration_corpus.record_count` and
`seed_corpus_digest` are written by the session that takes the sweep, on the
host, from the corpus it actually ran against. A digest transcribed by a session
that could not compute it is a digest nobody verified.

**4 — `scripts/schema-part7.sql`. Survives, additive only.** `answer_store`
re-applies it on every call and the file is idempotent by design. **Adding a
column is safe; changing how a stored span is written is not** — `answer_citations`
holds the exact character span each marker occupies in its source file, which is
what makes *"every claim traces to a chunk, and every chunk traces to characters
on disk"* a query rather than an aspiration, and it is what
`ui/build_ui_data.py --verify` reads to produce its `moved` / `absent` / `168
UNKNOWN` counts. **Any change that moves a stored span is a re-baseline of that
verify output and must say so.**

---

# 7. THE DEBT TABLE

**Block G sorts. It closes nothing.** Three columns, and `when` takes exactly
three values — `next`, `after the UI`, `open` — from the sequencing Amendment 1
§2 recorded before this block ran:

```
next, before the UI     FINDINGS 82 and 86, as ONE item. Instrument only;
                        no record is curated
then                    the UI: chatbot, map, click-through citation
after the UI            everything else below, and pillars 2-4 as open questions
```

| # | item | owning workstream | when |
| --- | --- | --- | --- |
| 1 | **FINDINGS 82 and 86 — inference where a declaration belongs.** `classify_translation` hard-codes `lang = "en"`; `classify_original`'s non-Latin test is a closed allowlist missing Thai, Khmer, Burmese, Sinhala, Tibetan, Javanese, Georgian and Cyrillic. Together the corpus cannot accept a modern non-English institutional source at all. Cost F6 one record and F7 three. See `W3_DECLARE_DONT_INFER.md` | W3 | **next** |
| 2 | **Q1's replacement measure** — a retrieval measure that is not a proxy for index size with the sign flipped. **Declared BEFORE the next record-adding run, never after** | W2 | open |
| 3 | **FINDING 93 — the collapse+rerank run at 561 chunks**, and a ruling on which configuration the project reads ranking from. PG5 is written above and must be read before the run | W2 | after the UI |
| 4 | **FINDING 92's follow-up** — no instrument reports `recall@6` split by target language, so the one thing that moved was invisible in every figure the project printed | W2 | after the UI |
| 5 | **FINDING 89's shape — no check reads prose.** A gold case's justification can go false while the assertion it justifies still passes, and one did, for two sub-tranches | W4 | after the UI |
| 6 | **No line reports language concentration within a region.** East Asia's seven source-language records are seven Literary Chinese records | W3 | after the UI |
| 7 | **A diffable manifest beside `ui/data.js`** (FINDING 74) | UI | after the UI |
| 8 | **`UNMUTATED_AND_OWED`** — `GUARD a reinstated_on that is not a date is refused` in `mutate_cost`, and three refusal guards in `mutate_fidelity` | W3 | after the UI |
| 9 | **A Swedish GeoNames dump and a Thai one.** Closes both Scandinavian placements and `seasia-08-pong-tuk-lamp`'s. Three coordinates a source handed over and this corpus refused | W1 | after the UI |
| 10 | **`git log --follow` on `africa-03-periplus-adulis`** — two chunk-ids that still do not name their passage, in every run of Block F. **This one record is the whole of G3 box 8's failure**, moved 1 and absent 1 | W1 | after the UI |
| 11 | **Investigations owed, unchanged since F5** — a ranking pair targeting `eastasia-07-tang-huiyao`; `southasia-05-brihatsamhita` appearing nowhere in the ranking run; re-reading `arabia-04-jabal-dabub` and `eastasia-07-tang-huiyao` against ruling 74; the unlocated "two ṭ" sentence in Petrantoni; Dvivedī's mūla Bṛhatsaṃhitā 2.14; a GeoNames search for al-Ruwāfa | W3 | after the UI |
| 12 | **Candidates found and banked** — `U 431 Åshusby`; `M2 I` and `M 5794 I`, both Turfan, both blocked on row 1; the Maḥrem / Ares pair in `africa-06-ezana-rie189`'s notes; the BnF cameo of Shapur I seizing Valerian, blocked on row 1 and reachable the day it lands | W3 | after the UI |
| 13 | **38 of 54 records carry an `unread` rights position.** A state of this project's knowledge, not of the sources. Never derived — FINDING 69 with a regular expression in front of it is not a fix | W3 | after the UI |
| 14 | **`verbatim_machine_english` 4 of 10**, and `total_at_60` recorded as missed by six. Unblocked by row 1; **not re-opened by it** — nobody re-curates a record and the shortfall stays recorded as a miss | W3 | after the UI |
| 15 | **The floor recalibration at 54 records** — three sessions on three distinct UTC dates, ~270 chat calls, and it writes `recalibration_corpus.record_count` and `seed_corpus_digest` from the host. See §6 item 3: **if the prompt moves too, move both and recalibrate once** | W4 | after the UI |
| 16 | **`muziris-cargo-akananuru` at rank 373.** The corpus's one genuinely broken cross-lingual link, unmoved since Block C and now worse | W2 | after the UI |
| 17 | **`africa-01-ezana-stone`, a placeholder with a newspaper citation, holds rank 1 on `au-ezana-titles`** and has defended it against eleven new records with an empty `beaten_by` twice running | W2 | after the UI |
| 18 | **Pillars 2–4**, and the knowledge graph, deprioritised on separate grounds | — | open |

**Two rows are one defect and are written as one row, on purpose.** Amendment 1
§2: FINDINGS 82 and 86 split across two rows is how one gets fixed and the other
stays open.

**Row 2 is the only row this block created that has no date, and that is
deliberate.** Its condition is a moment, not a position in a queue.

---

# 8. WHAT BLOCK G DID NOT DO

Recorded because a prohibition that was honoured silently reads the same as one
that was forgotten.

- **Did not amend G3.** No box reworded, no target lowered, `total_at_60` still
  60, ruling 69 undisturbed. Two arguments for softening a box were found and are
  written up in §2 with their refusals.
- **Did not lower `total_at_60`.**
- **Did not curate or re-curate a record.** The corpus is 54 records at the gate
  and 54 records after it.
- **Did not fix FINDINGS 82 or 86.** They are cheap, offline, and this block read
  about them for an hour while sorting §5 into a table, which is exactly when a
  one-session block starts doing a two-session job. The fix adds a declared field
  to every record and **moves the corpus digest**, and this is the block that
  records what the corpus was at the gate. Amendment 1 §3, written in advance.
- **Did not run a sweep.** No W4 sweep, no ranking run. PG5's run is booked and
  its prediction is written; the run itself belongs to the block that takes it.
- **Did not read a cost figure from anywhere but `cost_log report`.** FINDING 75.
- **Did not compute a figure in a generated block from another figure in it.**
  FINDING 76. Every figure in §3 and §4 that is not inside a pasted block was
  read from an archived run file or from a command named beside it.
- **Did not name its own commit hash in an abort condition.** FINDING 90, and
  this document has no abort condition at all.
- **Did not fold Amendment 1 into `BLOCK_G_START.md`.** The amendment asked for
  it, and the reason it asked — one operating document, so that nobody reads the
  amendment second or not at all — was a reason that expired when this block
  read both in the order the amendment specified. **Folding an operating
  document after the block it operates is the shape of the thing this project
  forbids**, done to a document rather than to a gate, and it would leave
  `BLOCK_G_START.md` saying things it did not say while Block G ran. Both files
  stand as written. Recorded here so that the omission is a decision rather than
  an oversight.

---

# 9. WHAT PHASE 2 PROVED AND WHAT IT DID NOT

**Proven.** That a corpus of this shape can be built and kept honest. Fifty-four
records across seven regions, every per-region source-language floor met, four of
five tiers on target, integrity green, eleven suites green, and a set of
instruments that refuse to produce numbers they cannot support — the cost ledger
saying `NOT YET A COST CLAIM` about itself, the floor refusing to calibrate from
one date, the allocation guard distinguishing a shortfall from an unreachable
quota. **The findings that cost the most were the ones where an instrument was
believed rather than read.**

**Proven.** That improvement can be distinguished from noise — at 24 records, on
four sessions, with the decomposition archived.

**Not proven.** That ranking survives scale. It does not, and the failure is
specific: **the English-target pairs did not move at all and every loss is a
non-English target.**

**Not proven.** That curation gets cheaper. The instrument exists, the ledger was
kept for thirty records, and it declines to answer.

**Not proven, and not attempted.** Anything at 60 records, because there is no
60-record corpus. Four of G3's nine boxes were unreachable rather than undone.

**The one number that should worry the reader is in §5**, and it is not the one
that has been the obvious answer since Block C.

**Phase 2 exits on a PIVOT.** Next: FINDINGS 82 and 86 as one instrument fix,
then the UI — chatbot, map, click-through citation — and that sequencing was
settled before this verdict was written.
