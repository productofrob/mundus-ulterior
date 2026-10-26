# F7 START — the last sub-tranche of Block F. Seven slots, none of them
# expensive, one gloss declaration, and a corpus that will close six short

**Read this before `F6_RESULT.md`, `F6_RANKING_2.md` or `F6_RULINGS.md`.** Those
are what F6 decided, delivered and measured. This is the operating document for
F7.

**`F7.closed` is `false` and stays false until `F7_RESULT.md` exists.** Locate
that flag by reading the block for the sub-tranche NAMED `F7` in
`data/corpus_tiers.json → target_mix → allocation → sub_tranches`, **not by line
number** — F5 Part 3's first attempt at that edit set the wrong sub-tranche's
flag.

---

## THE STATE BLOCK IS GENERATED. DO NOT RESTATE IT AND DO NOT COMPUTE A FIGURE IN IT.

Both instruments exist. Run them; do not copy from here if you can run them.

```
python -m ingest.verify --state       the corpus state block
python scripts\state_block.py         RUNS the eleven and prints the table
```

Run by `python -m ingest.verify --state` on 2026-09-06. PASTE THIS BLOCK. Do not restate it.

```
documents: 47   chunks: 153   parallel pairs: 33
note: paraphrase flag LIFTED on 'weilue': LIFTED 2026-08-22, FINDING 11. eastasia-01-weilue's original_text_excerpt is 221 verbatim characters from zh.wikisource 三國志/卷30 and classifies as verbatim_original on its own merits. The manifest's flag marked SUSPICION and nothing in the pipeline ever turned suspicion into a determination; when two of its entries were finally checked they came back opposite ways. Leaving the flag on would have the corpus report a sourced text as paraphrased.
note: retrieval-eligible non-English chunks by language: {'xsa': 2, 'xna': 2, 'arc': 3, 'grc': 16, 'lzh': 7, 'pal': 6, 'xpr': 2, 'non': 1, 'gmq-pro': 3, 'oty': 1, 'san': 2, 'ocm': 1, 'omy': 2, 'gez': 1}
note: W1 placements: 46 placed + 1 declared unplaceable = 47/47 considered (G1's target was 24, met), 28 with a named place (G1 wanted 17), 65 distinct gazetteer ids, 1 contested (G1 criteria 1 and 3). Grounds: {'identified': 3, 'regional': 81, 'stated': 64}. Resolution is not checked here — run `python -m ingest.gazetteer --check`, which is the only thing that turns an id into a coordinate.
note: rights positions (ruling 74, column built in F6): {'open_licence_stated': 3, 'permission_stated_no_licence': 3, 'public_domain': 1, 'all_rights_reserved': 1, 'two_positions_stated': 1, 'unread': 38}. 38 of 47 record(s) are UNREAD -- nobody has read that source's rights position since FINDING 69, which was produced by two licence claims that were wrong in opposite directions in a single session. `unread` is a state of this project's knowledge and not of the source. COUNTED, NOT GATED, and never derived: citation_original is prose, and a matcher over it would read the word `open` in a sentence about reachability, which is FINDING 69 with a regular expression in front of it.
note: quotation cases: 9 ask WHICH chunk was quoted (target 6 at 60) and 4 ask only WHETHER anything resolved. Ruling 56: they are two questions under one name. The second line rises by construction with every verbatim_machine_english record, so a total that is climbing is not evidence that this system quotes sources rather than translations.
note: record tiers: verbatim_with_provenance 29/29, verbatim_machine_english 4/10, published_translation_only 2/4, catalogue_record 11/16, pointer_only 1/1 (F1 target at 60 records). Progress, not a threshold: the mix is a target for the end of Block F and a suite that failed on it throughout would be ignored throughout.
note: source-language records by region (F1 floor 4 each at 60): {'Arabia': 6, 'East Asia': 7, 'Persia': 4, 'Scandinavia': 4, 'South Asia': 4, 'Southeast Asia': 4, 'Sub-Saharan Africa': 4}. Below the floor: none. An aggregate tier target met entirely inside two regions leaves the other five exactly as unable to answer a source-text question as they are now.
note: allocation (ruling 51): F3 8, F4 7, F5 7, F6 7, F7 7 = 36 record(s), every source-language record before every catalogue record. The sub-tranche a record was curated in is NOT a field on the record and is not derivable from one: this line reports the PLAN, and data/curation_cost.json in curation order reports what happened.
note: delivery against the allocation: 23 of 36 tranche record(s) curated. Gloss-capable declared 6/7 (5 contested_reading, 1 hedged_identification), with 1 declaration(s) left in sub-tranches still open and 7 slot(s) left on a tier that can carry one. The DECLARATIONS are the scarce number: slots are plentiful by construction, and a guard that read them reported an unreachable quota as progress for two sub-tranches (FINDING 51). A SHORTFALL is progress and is reported here; an UNREACHABLE quota is a failure above, because a target that can no longer be reached has already been missed and nobody re-curates a record.
note: source-language records by PROVENANCE rather than by language (ruling 58, in the shape FINDING 62 gave it): is the region SPEAKING, or being SPOKEN ABOUT? Arabia 6 = 5 local + 0 empire-language from the region + 1 about it, so 5 SPEAKING and 1 spoken about; East Asia 7 = 7 local + 0 empire-language from the region + 0 about it, so 7 SPEAKING and 0 spoken about; Persia 4 = 4 local + 0 empire-language from the region + 0 about it, so 4 SPEAKING and 0 spoken about; Scandinavia 4 = 4 local + 0 empire-language from the region + 0 about it, so 4 SPEAKING and 0 spoken about; South Asia 4 = 2 local + 0 empire-language from the region + 2 about it, so 2 SPEAKING and 2 spoken about; Southeast Asia 4 = 4 local + 0 empire-language from the region + 0 about it, so 4 SPEAKING and 0 spoken about; Sub-Saharan Africa 4 = 1 local + 2 empire-language from the region + 1 about it, so 3 SPEAKING and 1 spoken about. Regions with no source-language record in a language of the region: []. Regions with NO RECORD SPEAKING AT ALL -- neither in a language of the region nor in an empire language from it: []. FINDING 68, closed in F6: those two lists are different questions and only the first was ever printed, so a region whose own rulers wrote in Greek was reported in the same words as a region that is only ever written about. One text counted as a source-language record in more than one region: [[('Arabia', 'arabia-01-periplus'), ('South Asia', 'southasia-02-periplus-muziris'), ('Sub-Saharan Africa', 'africa-03-periplus-adulis')]]. COUNTED, NOT GATED. A language-only rule -- the one ruling 58 proposed -- cannot tell a record whose findspot is in the region from a Roman-world text about it, because both are grc, so it would refuse the two records ruling 58 argued to keep and admit the one it should refuse.
note: curation cost: 23 record(s) timed, 24 excused, 6 RETIRED (ruling 52: kept and named, counted in no mean). Comparator: within_tranche (ruling 46 -- nothing records what record 12 cost). Run `python -m ingest.cost_log report` for the per-tier table; it is the only place a curation-cost number may be read from.
loader warnings: 6
  ! arabia-02-palmyrene-tariff: empty reference_translation, no translation chunk emitted
  ! eastasia-06-cefu-yuangui: empty reference_translation, no translation chunk emitted
  ! eastasia-07-tang-huiyao: empty reference_translation, no translation chunk emitted
  ! seasia-06-kedukan-bukit: empty reference_translation, no translation chunk emitted
  ! seasia-07-talang-tuo: empty reference_translation, no translation chunk emitted
  ! africa-07-cosmas-sasu: empty original_text_excerpt, no original chunk emitted

All integrity checks passed.
```

And the eleven instruments, generated by `python scripts/state_block.py`, run on
the bridge under an interpreter with `psycopg[binary]`, `sqlglot` and
`python-dotenv`:

Run by `python scripts/state_block.py` at d34d3f1 on 2026-09-06. PASTE THIS BLOCK. Do not restate it, and do not compute a figure in it from another figure -- FINDING 76.

```
ingest.verify                        green, 47 documents
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
were run on the host on 2026-09-06 AFTER F6's four records:* `mutate_fidelity`
**70/70**, `mutate_cost` **58/58**, sources restored.

---

# WHAT IS LEFT: SEVEN SLOTS, AND NOT ONE OF THEM IS A SOURCE-LANGUAGE RECORD

```
region              tier                        n   note
East Asia           published_translation_only  1
South Asia          published_translation_only  1
South Asia          catalogue_record            1
Arabia              catalogue_record            1
Persia              catalogue_record            1   RULING 77's exchange half
Southeast Asia      catalogue_record            2

gloss_capable 1     expect_quoted_from_original_cases 0     vme_quotation_cases 0
```

**This is the cheap sub-tranche and it was designed to be.** Ruling 51 put every
source-language record before every catalogue record, and F6 spent the last of
them. F7 places **two published translations and five catalogue records**, and
the whole of the expensive work in Block F is behind it.

## What closes when F7 delivers

```
tier                          now      after F7   target at 60
verbatim_with_provenance      29        29          29   MET, and met at 47 records
verbatim_machine_english       4         4          10   SIX SHORT. No vme slot
                                                         exists in F6 or F7.
published_translation_only     2         4           4   MET
catalogue_record              11        16          16   MET
pointer_only                   1         1           1   MET

records                       47        54          60   SIX SHORT
```

**Four of five tiers land exactly on their target and the corpus still ends six
records short, because all six missing records are one tier.** That is FINDING 85
and it is the corrected form of a figure that had gone stale in
`data/corpus_tiers.json` itself: the field said `reachable_at_F7_close: 56` and
"the gap is 4", counting F5 as still allocated 7 when F5 closed at 5 of 7.
**54, and the gap is 6.** Ruling 69's decision — accept the shortfall, record it
as missed, do not lower `total_at_60` — is untouched and still governs.

## The per-region floors are ALL CLOSED and F7 cannot move them

`Below the floor: none.` F6 closed the last one. **No F7 slot is on a tier that
counts toward a source-language floor**, so nothing F7 does can raise or lower
one. This is the first sub-tranche in Block F for which that is true, and it
means F7's failure modes are about provenance and rights rather than about
counts.

---

# 1. F7's ONE GLOSS DECLARATION, AND THE TIERS IT MAY SIT ON

`gloss_capable_records` stands at **6 of 7**. F7 holds the seventh and it is the
last one Block F will ever make.

**All three of F7's tiers can carry it** —
`which_tiers_can_carry_a_gloss_case` is `["verbatim_with_provenance",
"published_translation_only", "catalogue_record"]` — so the declaration is not
constrained by the slot list. **What constrains it is the mechanical
requirement**, and it has failed twice in this repository:

**THE HEDGE AND THE STATEMENT THAT THE READING IS UNCERTAIN BOTH SIT INSIDE
`original_text_excerpt` OR `reference_translation`, NEVER IN `notes`**, which the
loader does not chunk. F3 declared two gloss-capable records at record 26 and
neither could ever pass, because both hedges were written into
`original_text_note`.

**`arabia-07-cih541` is the pattern to copy and it is F6's.** Every sentence of
its gloss is the SOURCE'S: the text prints `ḏ-(Ṯ)wlmn` with DASI's
uncertain-reading mark, the apparatus on the same page prints
`84  Glaser and CIH: (S²)wlmn.`, and DASI's editorial-criteria page defines both
marks in its own words. The record quotes all three inside
`reference_translation`. **An alternative this project supplied itself is worth
nothing** (FINDING 55), and that applies to the hedge as much as to the text.

**A second declaration is over-delivery that `check_delivery` fails on the day it
happens.** One declaration, one record.

---

# 2. THE TWO `published_translation_only` SLOTS, AND WHAT F6 LEARNED ABOUT THE TIER

The tier stands at **2 of 4** and its two members are a fair picture of how far
this project's standards moved:

```
africa-01-ezana-stone    seed 24.  original_text_excerpt is a bracketed
                         instruction to a later session; classify_original
                         returns ('pointer','en',False); the translation is a
                         titulature quoted from a NEWS WEBSITE. FINDING 80.
africa-07-cosmas-sasu    F6.  McCrindle 1897, named translator, named publisher,
                         page range, public-domain, digest-verified, with the
                         boundary of its translation search stated and the two
                         things it did NOT open named.
```

**Three things F6 established about this tier, and F7's two records should carry
all of them:**

1. **OMIT `original_text_excerpt` RATHER THAN FILLING IT WITH A PLACEHOLDER.**
   That raises a loader warning — `empty original_text_excerpt, no original chunk
   emitted` — and the warning is the honest artefact. A bracketed note saying the
   source text is "to be pulled during ingestion" classifies as a `pointer`,
   suppresses nothing, and reads to a later session as though the work were half
   done. `africa-01` is what that costs, six weeks later.
2. **`derive_tier` will refuse a retrieval-eligible ENGLISH original on a
   non-find record** as `unclassifiable`. There is no tier for a record whose
   "original" is English prose. The field is omitted or it is a pointer.
3. **The tier still owes a translation-search boundary**, in the record's own
   words, naming what was looked at and what was not. A `published_translation_only`
   record is nothing BUT its translation and its citation; the boundary is the
   only thing separating it from a link.

**Candidates named and not taken.** `F6_CURATION_START.md` sent the Africa slot to
`noorlib.ir`; it did not go there, because noorlib serves Arabic and Persian works
and this tier needs a published **English** translation. **noorlib remains open,
holds the Mojmal al-Tawārīkh, states no licence, and is a live candidate for the
EAST ASIA or SOUTH ASIA slot only if an English translation is what is being
cited.** Under ruling 74 a source that states no terms is usable and **the record
must say THAT, in those words.**

---

# 3. THE FIVE `catalogue_record` SLOTS, AND THE ONE TRAP IN THEM

`catalogue_record` is the tier `PHASE2_PLAN` named as the failure mode — *"so the
tranche is not accidentally all catalogue records"* — and F7 is where they all
land, by design, with every source-language record already curated.

**`classify_original` treats find and coin records specially.** For
`source_type in FIND_TYPES` the `original_text_excerpt` is classified
`object_description`, retrieval-eligible, and **the record tiers as
`catalogue_record` whatever its text fields contain** — there is a mutation guard
asserting exactly that. So a catalogue record's "original text" field is a
museum's object description and must never be mistaken for the wording of a
primary text. `africa-02-aksumite-coin` and `persia-03-coin-bm-1843-0620-5` are
the pattern.

**The rights column is where these will cost time.** Museum records have terms
and they are not all the same: this corpus already holds
`met-licence-declaration.txt`, `cma-licence-declaration.txt` and a British Museum
record. **38 of 47 records are still `unread`** and a new record is never one of
them.

---

# 4. WHAT F6 LEARNED ABOUT PREDICTIONS, AND WHAT F7 SHOULD DO DIFFERENTLY

**Ruling 78 required predictions to be written before the records exist. F6 wrote
four. P1 confirmed, P2 confirmed, P3 confirmed, P4 REFUTED** — and P4's
refutation is the useful one.

```
P4 said     a Ge'ez record should crowd almost nothing in Africa, because the
            crowder is the record that RESEMBLES the target (FINDING 79)
P4 measured "Africa's six ranking pairs"
what F6     TWO Africa records the same day, with completely different chunk
placed      profiles
result      the region moved; the resembling pair held; P4 refuted
diagnostic  africa-06 (Ge'ez) appears in exactly ONE beaten_by list in the run
            and it is tc-jabal-dabub -- an ARABIA target expecting a Sabaic
            transliteration. It crowded NOTHING in Africa.
            africa-07 (English prose about Adulis) crowded the two Adulis pairs.
```

**THE RULE F7 INHERITS: a prediction that names a record must be denominated in
what that record could crowd, not in the region it belongs to.** The unit is a
sentence the archive can answer — *"no `beaten_by` list contains a chunk of
`<record>` except where the target is `<kind>`"* — because `beaten_by` records
chunk ids and the pair-level rank does not.

**F7 places no source-language record, so its predictions are about a different
thing.** Two `published_translation_only` records put ENGLISH chunks into an index
where English is already 497 of 544 chunks, and five catalogue records put
`object_description` chunks in. **The interesting question F7 can pre-register is
whether an English-prose record crowds by SUBJECT across regions** — which is
what `africa-07-cosmas-sasu` did to the Adulis pairs and what
`eastasia-08-songshi-fulin` did to `cefu-yuangui-fulin-glass`, two records about
拂菻 four hundred years apart.

**And FINDING 84 is the frame for reading whatever comes back.** Not one gold pair
in Block F has ever improved when a record was added: 0 better / 9 worse, then
0 better / 14 worse. The only run with improvements is the one where 393
distractors LEFT the index. **A falling `recall@6` is the expected mechanical
consequence of curating**, and the gate G2 reads cannot tell that from a corpus
getting worse. Expect it to fall again. Say so before the run.

---

# THE FOUR REGISTRATIONS EVERY NEW RECORD NEEDS

A record is not curated until all four exist. `ingest.verify` fails on any one.

```
1  data/seed_corpus/<region>/<file>.json     the record
2  data/corpus_tiers.json  -> tiers          the DECLARED tier
3  data/corpus_rights.json -> records        the rights cell (ruling 74)
4  data/curation_cost.json -> records        the ledger entry, with an `agent`
                                             on EVERY phase (FINDING 70)
```

**And raise the document count.** `ingest/verify.py` holds
`check(len(docs) == 47, ...)`. It moves once per record, in that record's own
commit.

**FINDING 66's grep guard has started colliding and F7 will hit it.** The rule is
that `grep -rn "== <n>" ingest eval scripts ui` must find that line and nothing
else. At 45 it also matched `eval/test_ranking_check.py:1049`, a pacing assertion
reading `== 45.0`. **The collision is real, the guard is a substring search over a
repository full of numbers, and at 48 or 50 it may collide again.** Read what the
grep returns; do not assume a second hit is the defect the guard is for.

## The seven rights positions

`open_licence_stated`, `permission_stated_no_licence`, `public_domain`,
`all_rights_reserved`, `states_no_terms`, `two_positions_stated`, `unread`.
**All seven have now been exercised** — F6 spent the last two, `public_domain` on
`africa-07` and a second `open_licence_stated` on a licence that names no version.

Every position except `unread` needs `read_off`, `read_by` and an ISO `read_on`;
every position that asserts what a source SAID must quote it verbatim;
`states_no_terms` must NOT carry a quotation; `two_positions_stated` needs at
least two.

**And one shape the column cannot yet express**, found by
`eastasia-08-songshi-fulin`: a record whose SOURCE TEXT and TRANSLATION come from
two different sources with two different positions. That record's cell covers the
translation and says so. **F7 will hit this again on any catalogue record whose
object is in one museum and whose text is in another.**

---

# THE TRAPS, IN ONE LINE EACH, AND THE ONES F6 ADDED

**VERIFY EVERY CAPTURE BY DIGEST.** Type it on the bridge, slice the same span out
of the live page in the browser, SHA-256 both, compare. F6 did this on seven
spans across four records and it earned its keep twice: the DASI line-number
gutter is **non-breaking spaces, four per line, forty-four in the span**, which no
reader would have seen; and on `eastasia-08` it verified an **edit** — Kanripo's
`¶` and `<pb:...>` markers stripped by the same two rules on both machines — which
is the part a curator's eye is worst at checking. **About a minute a record.**

**KEEP EVERY WORD OF YOUR OWN PROSE OUT OF THE EXCERPT.** Twenty-six words of
curatorial English pushed record 42's `english_marker_ratio` to 0.20 against a
threshold of 0.18 and failed three checks at once.

**MEASURE THE RATIO, DO NOT COUNT IT.** Call
`ingest.fidelity.english_marker_ratio(chunk)`.

**`findspot_places: []` IS REFUSED.** Omit the key.

**`ground: "stated"` ON A SPECIFIC PLACE REQUIRES A GAZETTEER ID.** Without one
the honest ground is `regional`.

**A DIRECTIONAL ROLE NEEDS A `focus`.** `source`, `destination` and `waypoint`
all assert a movement and require the other end of it in the same block.
`arabia-07-cih541` extended its excerpt by two lines specifically so the arrivals
had a stated destination.

**NEVER AUTHOR A COORDINATE.** A coordinate reaches this corpus through a
gazetteer id or not at all. **And use `--names-dump`**: `Maʾrib` matches no place
TITLE in the pinned Pleiades snapshot, and `pleiades:39379` surfaced only as the
attested Greek name `Μαρίαβα`. A name match is not an identification — confirm on
description and coordinate before taking an id.

```
python -m ingest.gazetteer --dump data\pleiades-places-20260810.csv.gz --names-dump data\pleiades-names-20260810.csv.gz --find "Name"
python -m ingest.gazetteer --refresh --dump data\pleiades-places-20260810.csv.gz
python -m ingest.gazetteer --check
```

**`--refresh` may or may not re-stamp the cache, and the start document that
warned about thousands of changed lines was date-dependent.** F6's refresh added
26 lines and changed none, because the entries had already been stamped that
morning. Read `git diff --stat` and know what it cannot show: a record is
`Bin 0 -> N bytes`, a `ui/data.js` rebuild is `2 +-`.

**A PEOPLE, A STATE, AN OFFICE AND A TITLE ARE NOT SETTLEMENTS.** `kēsar`,
`Hrōmāy`, `walhakurn`, `mlk Rmn`, `mlk Frs¹`, `ngs²yn` and "the King of the
Axômites" have all been refused a gazetteer id on that rule. Do not import
Pleiades 423025 `Roma` for a text that names the Roman state.

**RULING 65 — no `--fuse`.**

**WRITE BYTES.** `json.dumps(d, ensure_ascii=False, indent=2) + "\n"`, UTF-8, LF
only, no BOM. Archived citation spans point into the corpus by exact offset.

---

# THE ENVIRONMENT

**The bridge** — a Linux VM with the repo mounted — runs everything in the
instrument table, `ingest.gazetteer`, `ui/build_ui_data.py` and `check_ui.mjs`.
**It needs its own venv and the repo's `.venv` is a Windows venv and is not
usable there:**

```
python3 -m venv ~/venv
~/venv/bin/pip install "psycopg[binary]" sqlglot python-dotenv
```

Without `psycopg` and `sqlglot` the table reads 424/1 and 149 and one RED, which
is a fact about the interpreter and not about the tree.

**The host** runs what the bridge cannot, and F6 proved it end to end:

```
docker compose up -d db
python scripts\check_db.py
python -m ingest.run_ingest
python -m ingest.run_embed
python -m eval.run_ranking_check --with-distractors
python scripts\mutate_fidelity.py
python scripts\mutate_cost.py
```

**`--with-distractors` is not optional.** FINDING 77 exists because it was
omitted once, and the baseline every prediction is written against is
`20260906T103920+0000-retrievable_chunks_with_distractors.json`, view
`retrievable_chunks_with_distractors`, **544 chunks**.

**Git from the bridge:** `git --no-optional-locks`, `-c user.name -c user.email`
per commit, and `device_request_delete_permission` on the repo root or git cannot
remove its own `.git/objects/tmp_obj_*`. Commit messages go in `commit-*.txt` and
are gitignored — **do not `git add` them.**

---

# THE DEBT LIST F7 INHERITS

**Cheap and unclaimed:**

1. **A Swedish GeoNames dump** — closes both Scandinavian placements, which
   refused coordinates their source handed over. Still the cheapest work here.
2. **`GUARD a reinstated_on that is not a date is refused`** and **three** refusal
   guards in `mutate_fidelity` are in `UNMUTATED_AND_OWED`, printed by name on
   every harness run.
3. **A diffable manifest beside `ui/data.js`** (FINDING 74).

**Instrument debt F6 raised and did not fix:**

4. **FINDING 82 — `classify_translation` hard-codes `lang = "en"`** for every
   non-pointer translation chunk. Nothing checks it. This is why F6's East Asia
   slot could not take the Turfan Manichaean text it was pointed at:
   parsigdatabase's Manichaean translations are **Persian** and would have entered
   the index declared English. **A fix changes what every existing record's
   translation chunk declares**, so it is a piece of work and not a patch.
5. **No line in `ingest.verify --state` reports LANGUAGE CONCENTRATION within a
   region.** East Asia's seven source-language records are seven Literary Chinese
   records; Africa gained its first local language in F6. A region that speaks in
   one language is a narrower witness than its count suggests and nothing prints
   it.

**Investigations owed, unchanged:**

6. `git log --follow` on `africa-03-periplus-adulis` — its chunk-id drift is in
   every ranking run and **both drifting pairs are the two Africa pairs P4 turns
   on**.
7. A ranking pair targeting `eastasia-07-tang-huiyao`;
   `southasia-05-brihatsamhita` appearing nowhere in the ranking run; re-reading
   `arabia-04-jabal-dabub` and `eastasia-07-tang-huiyao` against ruling 74; the
   unlocated "two ṭ" sentence in Petrantoni; Dvivedī's mūla Bṛhatsaṃhitā 2.14; a
   GeoNames search for al-Ruwāfa.

**Candidates found and NOT taken — these are F7's or Block G's:**

8. **`U 431 Åshusby`** — *"and he died abroad among the Greeks"* — found by the
   search that produced record 43. Scandinavia, and F7 places no Scandinavia slot,
   so this is Block G's unless a slot is re-pointed.
9. **`M2 I`, Mani dispatching Mār Addā INTO THE ROMAN EMPIRE**, and the banked
   `M 5794 I`. **Both are Turfan finds and are EAST ASIA candidates under the
   findspot rule** that makes `eastasia-04-jingjiao-stele` East Asia and not
   Persia — the mis-regioning F6 settled without curating. The vein is REACHABLE
   and blocked only on FINDING 82 plus an English translation: TITUS carries M 2
   under `Mir.Man., ii`, parsigdatabase carries 59 Middle Persian texts under
   Boyce 1975's sigla, and Boyce 1975, Asmussen 1975 and Andreas–Henning 1933 are
   all in copyright.
10. **The Maḥrem / Ares pair.** `africa-06-ezana-rie189`'s notes record that
    ‘Ēzānā's pre-Christian inscriptions call him `walda Maḥrǝm za-’ǝy-yǝtmawā’
    la-ḍar` in the Ge‘ez and `υἱὸς θεoῦ ἀνικήτoυ Ἄρεως` in the Greek — an Aksumite
    chancery performing *interpretatio graeca* on its own dynastic god for a
    Mediterranean readership. **Not taken** because the Ge‘ez is a four-word phrase
    inside the author's prose and an excerpt assembled from parentheticals is the
    curator's construction. Findable in one step if a later block wants it.

**Standing:**

11. **`betamasaheft.eu` returns 403 to a real browser**, at root and at
    `/inscriptions`, with its own page inviting an email for access. The first
    negative ever recorded against Ge'ez sourcing. **The printed RIÉ corpus was
    NOT opened and no negative is recorded against it.**
12. The two older Scandinavian source-language records cite Wikipedia. Neither is
    re-curated — nobody re-curates a record — but Runor now exists in this
    repository with signa, persistent URIs, a named edition and a stated reuse
    permission.
13. **`africa-01-ezana-stone` is a placeholder with a newspaper citation** and it
    is one of the two members of the `published_translation_only` tier. It holds
    rank 1 on `au-ezana-titles` and defended it against four new records.

---

# WHAT F7 OWES WHEN IT CLOSES

1. Seven records, or fewer with **every miss recorded as a searched failure with
   its reason named** — ruling 75's precedent, which F6 used for the Turfan vein.
2. **One gloss declaration**, the last in Block F.
3. A **pre-registered prediction** in ruling 78's shape, denominated in
   `beaten_by` and not in a region — FINDING 83.
4. A **ranking run on the host** after the records land, read against it.
5. **`F7_RESULT.md`, and `F7.closed = true` only then.**
6. **A statement of where Block F actually ended**: 54 records against a target of
   60, `verbatim_machine_english` at 4 of 10, and four of five tiers on target.
   Ruling 69 decided that is recorded as missed and not lowered.
