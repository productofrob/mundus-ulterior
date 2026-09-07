# W3 RESULT — **FINDINGS 82 AND 86 ARE CLOSED AS ONE ITEM.** The classifier is
# fixed, three refused sources classify correctly, **NO RECORD IS CURATED**, and
# **PREDICTION P1 IS REFUTED BY ONE RECORD** — which is the most valuable thing
# in the session.

*Written 2026-09-07, on the bridge. The three predictions this document is read
against were committed at `59dcd1e` in `W3_START.md` **before a line of the fix
existed** — ruling 78's practice, `W3_DECLARE_DONT_INFER.md` §7. Rulings 80 to 82
and FINDINGS 95 and 96 are in `W3_RULINGS.md`; FINDING 94 is in `W3_START.md`.
Numbers were read from the command named beside them and no figure in a generated
block is computed from another figure in it — FINDING 76.*

**ONE HONESTY NOTE ABOUT ORDER, because nothing else proves it.** `W3_START.md`
was written and saved before route A's read, and committed after it, because the
commit is host-only and the session kept working while it waited. **P1 was not
edited in that interval and is refuted as written.** A later reader has the
file's mtime and this sentence and nothing stronger; FINDING 90 was a document
whose provenance claim could not be checked, and this is that shape declared
rather than left implicit.

---

## THE STATE BLOCKS ARE GENERATED. NOTHING BELOW THEM IS RESTATED.

Run by `python -m ingest.verify --state` on 2026-09-07. PASTE THIS BLOCK. Do not restate it.

```
documents: 54   chunks: 170   parallel pairs: 33
note: paraphrase flag LIFTED on 'weilue': LIFTED 2026-08-22, FINDING 11. eastasia-01-weilue's original_text_excerpt is 221 verbatim characters from zh.wikisource 三國志/卷30 and classifies as verbatim_original on its own merits. The manifest's flag marked SUSPICION and nothing in the pipeline ever turned suspicion into a determination; when two of its entries were finally checked they came back opposite ways. Leaving the flag on would have the corpus report a sourced text as paraphrased.
note: retrieval-eligible non-English chunks by language: {'xsa': 2, 'xna': 2, 'mul': 3, 'grc': 16, 'lzh': 7, 'pal': 6, 'xpr': 2, 'non': 1, 'gmq-pro': 3, 'oty': 1, 'san': 2, 'ocm': 1, 'omy': 2, 'gez': 1}
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

Run by `python scripts/state_block.py` at 59dcd1e on 2026-09-07. PASTE THIS BLOCK. Do not restate it, and do not compute a figure in it from another figure -- FINDING 76.

```
ingest.verify                        green, 54 documents
ingest.test_fidelity                 145   [green]
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


**`ingest.test_fidelity` is 115 → 145 and `mutate_fidelity` is owed to the
host.** Every other instrument reads exactly what `BLOCK_G_RESULT.md` recorded.
`ui/data.js` was rebuilt because every record's mtime moved; `check_ui` was RED
until it was, which is the staleness guard doing its job.

---

# 1. THE THREE PREDICTIONS, READ

## P1 — WHICH RECORDS THE FIXED CLASSIFIER RELABELS. **REFUTED. One record, three chunks.**

The prediction was *none*, refuted by any relabel. **Three chunks moved and all
three are `arabia-05-ruwafa`:**

```
ruwafa::original::000   verbatim_original   arc -> mul
ruwafa::original::001   transliteration     arc -> mul
ruwafa::original::002   partial_verbatim    arc -> mul
```

Nothing else in the corpus moved. Chunk count 170, loader warnings 8, every tier
count, every per-region count, the provenance table and the quotation-case split
are identical.

**The refutation is worth more than the confirmation would have been, and
FINDING 95 is what it found:** two of those three chunks are Greek, and the
corpus reported `'arc': 3` throughout Block F while its retrieval index held no
Aramaic chunk at all. The line now reads `'mul': 3` and `arc` is gone from it.

**The eleven other records that could have refuted P1 did not**, and the reason
is ruling 81: each was settled by its own `language_note`, not by judgement.
`persia-01-skz` is declared `xpr` unchanged with its doubt recorded as an owed
investigation rather than resolved by a session that is not qualified to resolve
it.

## P2 — WHAT THE WORKED EXAMPLES CLASSIFY AS. **CONFIRMED. Eight tuples of eight.**

**And the BEFORE column is MEASURED, not transcribed from FINDING 86.** Each
example was run through `ingest/fidelity.py` as it stood at `59dcd1e`:

```
                          old non_latin_ratio      old classification
bnf-camee-360                     0.000            ('object_description', 'en', True)
phu-khao-thong                    0.000            ('object_description', 'en', True)
khlong-thom                       0.000            ('object_description', 'en', True)
parsigdatabase-persian            1.000            ('translation',        'en', True)
```

**`non_latin_ratio` scored a page of Thai at exactly 0.000.** FINDING 86 said so
and this is the first time it was run against the actual source text.

**And the fourth line is FINDING 82 in one row:** the old code could see the
Persian perfectly well — `non_latin_ratio` 1.000 — and returned the constant
`"en"` anyway, because `classify_translation` never looked.

## P3 — WHETHER THE DIGEST IS THE ONLY THING THAT MOVES. **CONFIRMED, and its one number was wrong.**

```
MOVED     corpus digest   26e4a683... -> 0e7845055e440c7c46535f1aa2e5ea55e5116ed733d77bbb616404e8bdc2c839
          content_hash    all 54, every record gained two keys

DID NOT   chunk ids, chunk count (170), chunk text, char_start/char_end
          -- verified by diffing every record against HEAD: not one field VALUE
             changed, two keys added, none lost

OWED      the embeddings. The bridge cannot reach Postgres; W3_HOST_RUNBOOK.md
          step 2 is where `run_embed --stats` before and after settles it, and
          P3 is refuted if it reports pending work.
```

**The consequence P3 predicted so it would not read as a defect happened, and
the number in the prediction was wrong.** `build_ui_data.py --verify`'s second
axis now reads `unchanged 0, changed 1121` — every span whose corpus provenance
was recorded, in one commit. P3 said *"all 168 archived spans"*; the 168 are
precisely the spans that CANNOT say, because their runs predate the corpus
version. **The mechanism was right and the figure was borrowed from a sentence
in another document rather than measured**, which is FINDING 76's defect in a
prediction instead of a table. Recorded rather than quietly corrected.

**The first axis is unchanged: `moved 1, absent 1`, both `africa-03-periplus-adulis`.**
G3 box 8 fails exactly as it failed, on exactly the same record.

---

# 2. §5's STOPPING POINT, AND IT IS A PROOF RATHER THAN A FEELING

```
DONE WHEN   the BnF cameo's French description, Phu Khao Thong's Thai and
            Khlong Thom's Thai each classify CORRECTLY when run through the
            fixed classifier, recorded as three worked examples --
            and none of the three is curated.
```

`python scripts/w3_worked_examples.py`:

```
bnf-camee-360  --  https://medaillesetantiques.bnf.fr/ark:/12148/c33gbqh22
  refused by   F7, FINDING 86 (F7_CURATION_START.md, candidates found and not taken, item 1)
  declared     'fra'   non_latin_ratio 0.000
  declaration  ACCEPTED by the cross-check
  before W3    ('object_description', 'en', True)
  predicted    ('object_description', 'fra', True)
  classifies   ('object_description', 'fra', True)   MATCH
  as a RECORD  REFUSED at load, pending the section 8 ruling

phu-khao-thong  --  https://archaeology.sac.or.th/archaeology/120
  refused by   F7, FINDING 86 (F7_RESULT.md, what F7 searched and did not take, item 2)
  declared     'tha'   non_latin_ratio 1.000
  declaration  ACCEPTED by the cross-check
  before W3    ('object_description', 'en', True)
  predicted    ('object_description', 'tha', True)
  classifies   ('object_description', 'tha', True)   MATCH
  as a RECORD  REFUSED at load, pending the section 8 ruling

khlong-thom  --  https://suvarnabhumi.psu.ac.th/tudb/archaeologicalread/76
  refused by   F7, FINDING 86 (F7_RESULT.md, what F7 searched and did not take, item 2)
  declared     'tha'   non_latin_ratio 1.000
  declaration  ACCEPTED by the cross-check
  before W3    ('object_description', 'en', True)
  predicted    ('object_description', 'tha', True)
  classifies   ('object_description', 'tha', True)   MATCH
  as a RECORD  REFUSED at load, pending the section 8 ruling

parsigdatabase-persian  --  https://parsigdatabase.com/
  refused by   F6, FINDING 82 (F6_RULINGS.md)
  declared     'pes'   non_latin_ratio 1.000
  declaration  ACCEPTED by the cross-check
  before W3    ('translation', 'en', True)
  predicted    ('translation', 'pes', True)
  classifies   ('translation', 'pes', True)   MATCH
  as a RECORD  not gated -- a modern scholarly translation is a translation, not the category section 8 is about

All four worked examples classify as W3_START.md predicted, and none of them is curated.
```

**A fourth example beyond the three §5 asks for**, because FINDING 82 does not
live in `classify_original` at all and three examples would have closed FINDING
86 and left its twin asserted.

**None of the four is curated, and three of them CANNOT BE.** `tha` and `fra`
are in `MODERN_INSTITUTIONAL_PROSE_PENDING_RULING`, so a record declaring either
is refused at load, naming the ruling `W3_DECLARE_DONT_INFER.md` §8 says is not
this session's to make. The classifier handles them correctly and the loader
refuses them anyway — **both sentences are true at once, and that is the whole
design.** A debt row would have been a note; this is a refusal a curator walks
into. The set is emptied by the session that makes the ruling, and emptying it is
one edit.

---

# 3. WHAT CLOSED, AND WHAT IT DID NOT CLOSE

```
CLOSED    debt row 1 of BLOCK_G_RESULT.md -- FINDINGS 82 and 86, as ONE item
          the contradiction between the brief's stated interest in "relevant
          local, non-English sources" and a classifier that refused them

NOT CLOSED, and stated so nobody expects it
          G3 stays failed on nine boxes. No box reworded, total_at_60 still 60
          the UI is not helped
          `verbatim_machine_english` is still 4 of 10 and is NOT re-opened by
          this -- debt row 14 says nobody re-curates a record and the shortfall
          stays recorded as a miss
          the four unblocked candidates (the BnF cameo, the two Thai records,
          the Turfan pair) are BANKED, not taken. Debt row 12, after the UI
```

**Its success did not show up as a worse headline number, and the reason is that
it added no records.** `W3_DECLARE_DONT_INFER.md` §1 expected a fall the size
FINDING 91 describes; that expectation was about the six records this session was
forbidden to curate. **No ranking run was taken and none is owed by this item.**

---

# 4. THE FINDINGS

```
FINDING 94   W3_START.md    `state_block.py` on a fresh bridge reads RED for an
                            import error and 149 for a skip, and §10 step 1
                            would have stopped for neither reason. Extended
                            here: a bridge `git status` leaves a lock the
                            bridge CANNOT DELETE
FINDING 95   W3_RULINGS.md  the declaration is per FIELD, the language is
                            carried per CHUNK, and ruwafa's three chunks are
                            not all in one language. Two of three were labelled
                            wrong for the whole of Block F
FINDING 96   W3_RULINGS.md  a Cyrillic Є inside the Greek signature on
                            scandinavia-01-hoby-treasure. Invisible to every
                            instrument here until the script allowlist was
                            deleted. NOT corrected -- that is curation
```

---

# 5. WHAT IS OWED, AND IT IS TWO COMMANDS ON THE HOST

**`W3_HOST_RUNBOOK.md`.** This document reports no figure for either.

```
mutate_fidelity   84/84 expected, was 70/70. FOURTEEN new mutations, and NOT ONE
                  of them is in UNMUTATED_AND_OWED, which stays at 3
mutate_cost       58/58, must not move
run_ingest        and `run_embed --stats` before and after: P3's open half
```

Verified from the bridge without running them: MUTATIONS and EXPECTED are both
84, every mutation target occurs exactly once in `ingest/fidelity.py`, and every
guard the suite prints is in one of the three coverage lists.

---

# 6. WHAT W3 DID NOT DO

- **Did not curate a record.** 54 records at `W3_START.md` and 54 records here.
- **Did not add `"THAI"` to the script tuple.** It deleted the tuple.
- **Did not re-point `floor.json`'s digest pin.** Ruling 82.
- **Did not rule on §8.** It made the question unavoidable in code instead.
- **Did not correct `scandinavia-01-hoby-treasure`'s Cyrillic character**, or
  resolve `persia-01-skz`'s language. Both are recorded; both are curation.
- **Did not fix `state_block.py`'s conflation of an import failure with a test
  failure**, though FINDING 94 is about it. Not this item.
- **Did not fill in `RULINGS.md`'s missing 53-79**, having got three of
  twenty-seven wrong on the first attempt. The gap and the trap are recorded
  where the next session will stand.
- **Did not run a sweep, a ranking run, or PG5.**
