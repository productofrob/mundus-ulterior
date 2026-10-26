# BLOCK G START — the Phase 2 exit gate. One session, a decision and not a
# build, and it opens with **G3 FAILED** rather than pending

**Read this before `F7_RESULT.md`, `F7_RANKING.md` or the tail of
`PROGRESS.md`.** Those are what Block F delivered and measured. This is the
operating document for Block G.

`PHASE2_PLAN.md` defines Block G in one line: *"Phase 2 exit gate (1 session) →
kill / pivot / persevere."* **It is not a curation block and it is not an
instrument block.** Nothing in this document asks for a record to be written.

---

## THE STATE BLOCK IS GENERATED. DO NOT RESTATE IT AND DO NOT COMPUTE A FIGURE IN IT.

```
python -m ingest.verify --state       the corpus state block
python scripts\state_block.py         RUNS the eleven and prints the table
python -m ingest.cost_log report      the ONLY place a cost number may be read
```

Run by `python -m ingest.verify --state` on 2026-09-06. PASTE THIS BLOCK. Do not restate it.

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

Run by `python scripts/state_block.py` at 20793e6 on 2026-09-06. PASTE THIS BLOCK. Do not restate it, and do not compute a figure in it from another figure -- FINDING 76.

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

*Mutation harnesses are HOST ONLY (FINDING 59) and are not in that table. Both
were run on the host on 2026-09-06 after F7's seven records:* `mutate_fidelity`
**70/70**, `mutate_cost` **58/58**, sources restored, owed lists unchanged.

**Tree at Block G's open: `20793e6`, working tree clean, 54 documents, every
sub-tranche in Block F closed.**

---

# 1. G3 IS FAILED, BOX BY BOX, AND THAT IS BLOCK G's INPUT RATHER THAN ITS PROBLEM

G3 is Block F's gate. `PHASE2_PLAN.md` carries the checklist as amended **four
times, every one of them in advance** — rulings 39, 45, 46, and 50 and 51
together — for the reason the plan states in the margin: *"a gate amended at the
end is a gate fitted to its result."*

```
box                                                        state
1  60 records, all seven regions, ALLOCATION delivered      NOT MET  54 records; seven regions
                                                                     present; allocation 30 of 36
2  three sessions at 60 on three distinct UTC dates,        NOT MET  zero sessions at 60, because
   with calibrated:true re-written at 60, and                        there is no 60-record corpus.
   weilue-chinese-quotation and vimose-runes resolved                The floor is still calibrated
                                                                     at the 24-record corpus, pinned
                                                                     by digest 26e4a683… (ruling 49)
3  curation cost per record recorded and TRENDING DOWN      NOT MET  recorded: 30 timed, 24 excused,
                                                                     6 retired. Trending: the report
                                                                     prints NOT A TREND for every
                                                                     tier and closes with NOT YET A
                                                                     COST CLAIM
4  full sweep re-run at 60, content pass rate not lower     NOT MET  no sweep at 60
5  per-session stability at 60                              NOT MET  no sessions at 60
6  cross-session answer-text agreement at 60                NOT MET  no sessions at 60
7  ranking gold set still ≥95% top-6                        NOT MET  0.659 by pair, 0.732 by unit
8  ui/build_ui_data.py --verify clean, ZERO moved/absent    NOT MET  moved 1, absent 1
9  confidence profiles recalibrated, calibrated set         NOT MET  1 of 4 profiles calibrated;
   honestly                                                          documentary, inscription and
                                                                     verse still sit at the n=1 and
                                                                     n=2 observations of 2026-08-10
10 only then, 200                                           MOOT
```

**Nine boxes, none of them met.** Box 9 is the only one that could be closed by
work rather than by records, and it needs machine translations to observe.

## THE ONE THING BLOCK G MAY NOT DO ABOUT THIS

**Do not amend G3.** The four amendments this gate has taken were all made
*before* the block that would be measured by them. A fifth, made now, with the
result in hand, is precisely the move the plan forbids and the move ruling 56
refused when F3 delivered six of eight. **G3 is recorded as FAILED. Its target is
not lowered, its boxes are not reworded, and `total_at_60` stays 60** — ruling 69,
undisturbed since F5.

## AND FOUR OF THE NINE ARE UNREACHABLE RATHER THAN UNDONE

Boxes 2, 4, 5 and 6 all read *"at 60"*. There is no 60-record corpus and there
will not be one without curating six more `verbatim_machine_english` records —
the tier that is six short **because two hunts found nothing and one vein is
blocked on an instrument defect that is still open**. `F7_RESULT.md` sets out
why, in the words of the sub-tranches that tried. A gate box that cannot be
reached is a box that has already been missed, which is the distinction
FINDING 51 drew between a shortfall and an unreachable quota, and it applies to
gates as well as to declarations.

---

# 2. THE THREE QUESTIONS BLOCK G EXISTS TO ANSWER, AND WHAT IS ALREADY ON THE TABLE

`PHASE2_PLAN.md`, Block G, verbatim: *"Another honest kill / pivot / persevere,
answering the three questions the phase was built to answer."*

## Q1 — Does ranking survive scale?

**The plan's evidence for this was Top-6 at 450 chunks (G2), still there at 60
real documents (G3). Neither half arrives clean.**

```
run                                    records  chunks   recall@6 (pairs)  (units)
20260906T091154  before F6                  43     524     0.7273 (32/44)   0.8049 (33/41)
20260906T103920  after F6                   47     544     0.6818 (30/44)   0.7561 (31/41)
20260906T170622  after F7                   54     561     0.6591 (29/44)   0.7317 (30/41)
```

**And FINDING 91, from F7's run, is the most important thing Block F produced
about this question.** Eight of the thirteen pairs that fell had **no new chunk
in their window at all**, and the size of a fall tracks the pair's existing depth
rather than anything about the records added. The clean case:
`bronze-heracles-verethragna-from-mesene` lost nine ranks with a `beaten_by`
identical entry for entry and a similarity gap identical to four decimal places.

**Read with FINDING 84 — 0 better / 36 across three record-adding runs, and the
only run with improvements is the one where 393 distractors LEFT the index — Q1
has two possible answers and Block G must choose between them explicitly:**

- **"No."** Retrieval degrades as the corpus grows, the product is corpus-bound,
  and the honest move is the one the plan names: polish the sourcebook at 24–60
  records rather than chase 200.
- **"The question is malformed."** `recall@6` over a fixed gold set is partly a
  measure of index size with the sign flipped, so a falling number is what a
  working system does while it grows, and G3's ≥95% box was denominated in a
  quantity that cannot hold still. **This reading is not a way out.** If it is
  taken, Block G owes a replacement measure and must say what would have
  falsified it — otherwise it is FINDING 83's defect at gate scale: a criterion
  re-denominated after the run, by someone who knows the result.

**Whichever is chosen, `F7_RANKING.md` is the document to read first**, and
`FINDING 77`'s run — the one where the index shrank and eight pairs improved — is
the natural experiment that separates the two readings and has already been made.

## Q2 — Can improvement be distinguished from noise?

**G4 is CLOSED**, all five boxes, and its deliverable was the variance
decomposition rather than the pass rate. **The caveat that travels with it:** it
was closed at the 24-record corpus, and ruling 49's corpus clause deliberately
pinned the answer floor there by digest, so nothing since can recalibrate it.
Block E's cross-session agreement figures — 74–77% and 45% — are **context and
not thresholds** and G3's own amendment says a gate comparing across the two
corpora would be measuring the corpus move it was meant to survive.

So Q2's evidence exists, is good, and is **about a corpus that is now 54 records
rather than 24**. Block G should say plainly whether it counts.

## Q3 — Does curation get cheaper?

**Read `python -m ingest.cost_log report` and read nothing else.** Its own
closing line is `NOT YET A COST CLAIM`, because the declared mix is unmet — and
now permanently unmet. Every tier prints `NOT A TREND`: three are below the n=10
floor, and `verbatim_with_provenance` is above the floor and is refused a trend
anyway by **FINDING 70**, because its minutes come from four agents and a model
apportioning its own wall clock produces smaller, smoother numbers than a person
timing themselves.

**Q3's honest answer is available and it is not a number.** It is that the
instrument was built, the ledger was kept for thirty records across five
sub-tranches, and the ledger **refuses to answer the question it was built for**,
for reasons it states itself. Whether that counts as a pass is Block G's call.
The retired rows are the part worth reading: `seasia-vme-hunt-unresolved` at 9
minutes and `persia-vme-hunt-unresolved` at 20 are hunts that produced no record
at all, kept and named so the cost of the missing tier is visible rather than
absent.

---

# 3. WHAT BLOCK G OWES WHEN IT CLOSES

From `PHASE2_PLAN.md`, verbatim: *"Write the closing summary at the foot of
`PROGRESS.md` in the Phase 1 style: what was proven, what was **not** proven, the
one number that should worry the reader, and the debt table pointing each open
item at the workstream that owns it."*

So, concretely:

1. **A verdict — kill, pivot or persevere — with the three questions answered
   separately.** Passing all three unblocks the knowledge graph. The plan says
   what failing Q1 means and Block G should not soften it.
2. **G3 recorded as FAILED, with the box table**, and `G3.closed` — if the
   repository carries such a flag — set to whatever "closed and failed" is, never
   to "still open". A gate left open is a gate somebody amends later.
3. **The one number that should worry the reader.** Do not pick it from this
   document; the candidates are named in §5 below and one of them is the obvious
   choice, which is a reason to check the others first.
4. **The debt table, each item pointed at the workstream that owns it.** §5 is
   the raw list and it is not yet a table.
5. **The closing summary at the foot of `PROGRESS.md`**, in the Phase 1 style.
6. **`BLOCK_G_RESULT.md`**, and nothing in the repository claims Phase 2 is
   concluded before it exists.

---

# 4. WHAT BLOCK G MUST NOT DO

- **Not amend G3**, for the reason in §1.
- **Not lower `total_at_60`.** Ruling 69.
- **Not curate a record.** If a record would change the verdict, the verdict is
  the wrong shape.
- **Not re-curate a record.** Nobody re-curates a record — the standing rule that
  keeps `africa-01-ezana-stone`'s newspaper citation and the two Wikipedia-cited
  Scandinavian records in the corpus, visible, as evidence about how far the
  project's standards moved.
- **Not run a sweep it has not booked days for.** ~270 chat calls for a full W4
  sweep, and **the days are the scarce resource, not the calls** — item 4 of the
  plan's *Before anything else*, and the thing Phase 1 failed on.
- **Not read a cost figure from anywhere but `cost_log report`.** FINDING 75.
- **Not compute a figure in a generated block from another figure in it.**
  FINDING 76.
- **Not name its own commit hash in an abort condition.** FINDING 90, and it is
  four hours old.

---

# 5. THE DEBT BLOCK G INHERITS, UNSORTED

`F7_RESULT.md` carries these with their reasons. Block G's job is to sort them
into the table, not to close them.

**Instrument debt, and the first two are now load-bearing together:**

1. **FINDING 82** — `classify_translation` hard-codes `lang = "en"` for every
   non-pointer translation chunk.
2. **FINDING 86** — `classify_original`'s non-Latin test is a closed allowlist of
   script names; Thai, Khmer, Burmese, Sinhala, Tibetan, Javanese, Georgian and
   Cyrillic are all absent. **Together these mean the corpus cannot currently
   accept a modern non-English institutional source at all**, which is the
   project description's own stated interest in *"relevant local, non-English
   sources from the regions above"*. Between them they cost F6 one record and F7
   three.
3. **FINDING 89's shape — no check reads prose.** A gold case's justification can
   go false while the assertion it justifies still passes, and one did, for two
   sub-tranches, unnoticed.
4. **No line reports language concentration within a region.** East Asia's seven
   source-language records are seven Literary Chinese records.
5. **A diffable manifest beside `ui/data.js`** (FINDING 74).
6. **`GUARD a reinstated_on that is not a date is refused`** and three refusal
   guards in `mutate_fidelity` remain in `UNMUTATED_AND_OWED`.

**Cheap and unclaimed:**

7. **A Swedish GeoNames dump** closes both Scandinavian placements; **a Thai one**
   closes `seasia-08-pong-tuk-lamp`'s. **Three coordinates a source handed over
   and this corpus refused.**
8. **`git log --follow` on `africa-03-periplus-adulis`** — two chunk-ids that
   still do not name their passage, in every run of Block F.

**Investigations owed, unchanged since F5:**

9. A ranking pair targeting `eastasia-07-tang-huiyao`;
   `southasia-05-brihatsamhita` appearing nowhere in the ranking run; re-reading
   `arabia-04-jabal-dabub` and `eastasia-07-tang-huiyao` against ruling 74; the
   unlocated "two ṭ" sentence in Petrantoni; Dvivedī's mūla Bṛhatsaṃhitā 2.14; a
   GeoNames search for al-Ruwāfa.

**Candidates found and banked, for whatever follows Phase 2:**

10. **`U 431 Åshusby`** — *"and he died abroad among the Greeks"*, Scandinavia.
11. **`M2 I`, Mani dispatching Mār Addā into the Roman Empire**, and `M 5794 I`.
    Both Turfan finds, both blocked on FINDING 82.
12. **The Maḥrem / Ares pair** in `africa-06-ezana-rie189`'s notes.
13. **The BnF cameo of Shapur I seizing Valerian**, blocked on FINDING 86 and
    reachable the day it is fixed.

**Standing, and each is a candidate for the one number that should worry the
reader:**

14. **`muziris-cargo-akananuru` sits at rank 373.** The corpus's one genuinely
    broken cross-lingual link, unmoved since Block C and now worse. The sentence
    that travels with every aggregate: *29/30 is whether the RECORD was found;
    22/30 is whether the NON-ENGLISH TEXT was reachable.*
15. **38 of 54 records have an `unread` rights position.**
16. **`verbatim_machine_english` 4 of 10** — the tier the whole
    machine-translation path exists to exercise, and the reason the corpus ends
    six short.
17. **The answer floor is calibrated at 24 records** and pinned there by digest.
18. **`archived_answer` recall@6 is 0.125 (1 of 8)** — and those pairs name chunks
    retrieval itself returned, so their recall is partly true by construction.
19. **`africa-01-ezana-stone`, a placeholder with a newspaper citation, holds
    rank 1 on `au-ezana-titles` and has defended it against eleven new records.**

---

# 6. THE ENVIRONMENT

**The bridge** — a Linux VM with the repo mounted — runs everything in the
instrument table, `ingest.gazetteer`, `ui/build_ui_data.py` and `check_ui.mjs`.
It needs its own venv and the repo's `.venv` is a Windows venv and is not usable
there:

```
python3 -m venv ~/venv
~/venv/bin/pip install "psycopg[binary]" sqlglot python-dotenv
```

Without `psycopg` and `sqlglot` the table reads 424/1 and 149 and one RED, which
is a fact about the interpreter and not about the tree.

**The host** runs what the bridge cannot — anything needing Postgres, and the
mutation harnesses. `STARTUP.md` is the daily ritual and has not changed.

```
docker compose up -d db
python scripts\check_db.py
python -m ingest.run_ingest
python -m ingest.run_embed
python -m eval.run_ranking_check --with-distractors
python scripts\mutate_fidelity.py
python scripts\mutate_cost.py
```

**`--with-distractors` is not optional** (FINDING 77), and **RULING 65 — no
`--fuse`.** The baseline any new ranking figure is read against is
`20260906T170622+0000-retrievable_chunks_with_distractors.json`, **561 chunks**.

**Git from the bridge:** `git --no-optional-locks`, `-c user.name -c user.email`
per commit, and `device_request_delete_permission` on the repo root or git cannot
remove its own `.git/objects/tmp_obj_*` and `.git/*.lock`. Commit messages go in
`commit-*.txt` and are gitignored — **do not `git add` them.**

---

# 7. THE TRAPS, AND THE ONES BLOCK F ADDED LAST

**A GATE AMENDED AT THE END IS A GATE FITTED TO ITS RESULT.** G3's four
amendments were all made in advance. §1.

**A CRITERION RE-DENOMINATED AFTER THE RUN IS THE SAME DEFECT ONE LEVEL UP.**
FINDING 83 refused to rewrite a prediction's unit after seeing the run, on the
grounds that a prediction read afterwards has an explanation available for it.
Q1's second reading is exactly that move at gate scale, and if Block G takes it,
it owes a replacement measure **and** the sentence that would have falsified it.

**A JUSTIFICATION CAN ROT WHILE THE ASSERTION IT JUSTIFIES STILL PASSES.**
FINDING 89. Block G is a document made almost entirely of prose about numbers,
and nothing in the repository checks prose.

**DO NOT PIN A DOCUMENT TO ITS OWN COMMIT.** FINDING 90.

**READ WHAT THE GREP RETURNS.** FINDING 66's guard — `grep -rn "== <n>" ingest
eval scripts ui` finds exactly one line — held at 48, 50, 52 and 54 and collided
once at 45. It is a substring search over a repository full of numbers and Block
G moves no document count, so it should not fire at all; if it does, read what
came back before assuming it is the defect the guard is for.

**ARCHIVE RUNS, NOT VERDICTS.** The plan's own closing lesson, and it has paid
for itself three times, once in money. Block G is the block most tempted to
record a verdict and drop the run behind it.

---

# 8. THE FIRST FIVE MINUTES OF THE NEW THREAD

1. `python -m ingest.verify --state` and `python scripts/state_block.py` on the
   bridge. **Confirm they reproduce the blocks pasted above**, and if they do not,
   stop and find out what moved before reading anything else.
2. `python -m ingest.cost_log report`, and read its closing line before reading
   its numbers.
3. Read `F7_RESULT.md` and then `F7_RANKING.md`. **In that order** — the result
   says where Block F ended and the ranking says what the last run means, and the
   ranking document is the one that bears on Q1.
4. Read `PHASE2_PLAN.md`'s Block G section and the G3 checklist above it, and
   `PHASE2.md`'s Gate G3 and Gate G4 sections.
5. **Then decide the shape of the verdict before assembling evidence for it**,
   and write that decision down first — because a verdict assembled from evidence
   already chosen is the same defect as a prediction written after the run.
