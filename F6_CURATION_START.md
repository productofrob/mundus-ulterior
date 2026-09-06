# F6 CURATION START — three of seven placed, two floors closed, and the four
# records that are left

**Read this before `F6_PROGRESS.md`, `F6_RULINGS.md` or `F6_RANKING.md`.** Those
are what F6 decided, what it measured and what it found. This is the operating
document for the curation session.

**`F6.closed` is `false` and stays false until `F6_RESULT.md` exists.** Locate
that flag by reading the block, not by line number: F5 Part 3's first attempt at
that edit set the wrong sub-tranche's flag.

---

## THE STATE BLOCK IS GENERATED. DO NOT RESTATE IT AND DO NOT COMPUTE A FIGURE IN IT.

Both instruments were built on 2026-09-06, for FINDING 75 and FINDING 76. Run
them; do not copy from here if you can run them.

```
python -m ingest.verify --state       the corpus state block
python scripts\state_block.py         RUNS the eleven and prints the table
```

Run by `python -m ingest.verify --state` on 2026-09-06. PASTE THIS BLOCK. Do not restate it.

```
documents: 43   chunks: 133   parallel pairs: 30
note: paraphrase flag LIFTED on 'weilue': LIFTED 2026-08-22, FINDING 11. eastasia-01-weilue's original_text_excerpt is 221 verbatim characters from zh.wikisource 三國志/卷30 and classifies as verbatim_original on its own merits. The manifest's flag marked SUSPICION and nothing in the pipeline ever turned suspicion into a determination; when two of its entries were finally checked they came back opposite ways. Leaving the flag on would have the corpus report a sourced text as paraphrased.
note: retrieval-eligible non-English chunks by language: {'xna': 2, 'arc': 3, 'grc': 16, 'xsa': 1, 'lzh': 6, 'pal': 6, 'xpr': 2, 'non': 1, 'gmq-pro': 3, 'oty': 1, 'san': 2, 'ocm': 1, 'omy': 2}
note: W1 placements: 42 placed + 1 declared unplaceable = 43/43 considered (G1's target was 24, met), 26 with a named place (G1 wanted 17), 64 distinct gazetteer ids, 1 contested (G1 criteria 1 and 3). Grounds: {'identified': 3, 'regional': 69, 'stated': 61}. Resolution is not checked here — run `python -m ingest.gazetteer --check`, which is the only thing that turns an id into a coordinate.
note: rights positions (ruling 74, column built in F6): {'open_licence_stated': 1, 'permission_stated_no_licence': 2, 'all_rights_reserved': 1, 'two_positions_stated': 1, 'unread': 38}. 38 of 43 record(s) are UNREAD -- nobody has read that source's rights position since FINDING 69, which was produced by two licence claims that were wrong in opposite directions in a single session. `unread` is a state of this project's knowledge and not of the source. COUNTED, NOT GATED, and never derived: citation_original is prose, and a matcher over it would read the word `open` in a sentence about reachability, which is FINDING 69 with a regular expression in front of it.
note: quotation cases: 9 ask WHICH chunk was quoted (target 6 at 60) and 4 ask only WHETHER anything resolved. Ruling 56: they are two questions under one name. The second line rises by construction with every verbatim_machine_english record, so a total that is climbing is not evidence that this system quotes sources rather than translations.
note: record tiers: verbatim_with_provenance 26/29, verbatim_machine_english 4/10, published_translation_only 1/4, catalogue_record 11/16, pointer_only 1/1 (F1 target at 60 records). Progress, not a threshold: the mix is a target for the end of Block F and a suite that failed on it throughout would be ignored throughout.
note: source-language records by region (F1 floor 4 each at 60): {'Arabia': 5, 'East Asia': 6, 'Persia': 4, 'Scandinavia': 4, 'South Asia': 4, 'Southeast Asia': 4, 'Sub-Saharan Africa': 3}. Below the floor: {'Sub-Saharan Africa': 3}. An aggregate tier target met entirely inside two regions leaves the other five exactly as unable to answer a source-text question as they are now.
note: allocation (ruling 51): F3 8, F4 7, F5 7, F6 7, F7 7 = 36 record(s), every source-language record before every catalogue record. The sub-tranche a record was curated in is NOT a field on the record and is not derivable from one: this line reports the PLAN, and data/curation_cost.json in curation order reports what happened.
note: delivery against the allocation: 19 of 36 tranche record(s) curated. Gloss-capable declared 5/7 (4 contested_reading, 1 hedged_identification), with 2 declaration(s) left in sub-tranches still open and 11 slot(s) left on a tier that can carry one. The DECLARATIONS are the scarce number: slots are plentiful by construction, and a guard that read them reported an unreachable quota as progress for two sub-tranches (FINDING 51). A SHORTFALL is progress and is reported here; an UNREACHABLE quota is a failure above, because a target that can no longer be reached has already been missed and nobody re-curates a record.
note: source-language records by PROVENANCE rather than by language (ruling 58, in the shape FINDING 62 gave it): is the region SPEAKING, or being SPOKEN ABOUT? Arabia 5 = 4 local + 0 empire-language from the region + 1 about it, so 4 SPEAKING and 1 spoken about; East Asia 6 = 6 local + 0 empire-language from the region + 0 about it, so 6 SPEAKING and 0 spoken about; Persia 4 = 4 local + 0 empire-language from the region + 0 about it, so 4 SPEAKING and 0 spoken about; Scandinavia 4 = 4 local + 0 empire-language from the region + 0 about it, so 4 SPEAKING and 0 spoken about; South Asia 4 = 2 local + 0 empire-language from the region + 2 about it, so 2 SPEAKING and 2 spoken about; Southeast Asia 4 = 4 local + 0 empire-language from the region + 0 about it, so 4 SPEAKING and 0 spoken about; Sub-Saharan Africa 3 = 0 local + 2 empire-language from the region + 1 about it, so 2 SPEAKING and 1 spoken about. Regions with no source-language record in a language of the region: ['Sub-Saharan Africa']. Regions with NO RECORD SPEAKING AT ALL -- neither in a language of the region nor in an empire language from it: []. FINDING 68, closed in F6: those two lists are different questions and only the first was ever printed, so a region whose own rulers wrote in Greek was reported in the same words as a region that is only ever written about. One text counted as a source-language record in more than one region: [[('Arabia', 'arabia-01-periplus'), ('South Asia', 'southasia-02-periplus-muziris'), ('Sub-Saharan Africa', 'africa-03-periplus-adulis')]]. COUNTED, NOT GATED. A language-only rule -- the one ruling 58 proposed -- cannot tell a record whose findspot is in the region from a Roman-world text about it, because both are grc, so it would refuse the two records ruling 58 argued to keep and admit the one it should refuse.
note: curation cost: 19 record(s) timed, 24 excused, 6 RETIRED (ruling 52: kept and named, counted in no mean). Comparator: within_tranche (ruling 46 -- nothing records what record 12 cost). Run `python -m ingest.cost_log report` for the per-tier table; it is the only place a curation-cost number may be read from.
loader warnings: 5
  ! arabia-02-palmyrene-tariff: empty reference_translation, no translation chunk emitted
  ! eastasia-06-cefu-yuangui: empty reference_translation, no translation chunk emitted
  ! eastasia-07-tang-huiyao: empty reference_translation, no translation chunk emitted
  ! seasia-06-kedukan-bukit: empty reference_translation, no translation chunk emitted
  ! seasia-07-talang-tuo: empty reference_translation, no translation chunk emitted

All integrity checks passed.
```


```
ingest.verify                        green, 43 documents
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

*Run on the bridge under an interpreter with `psycopg[binary]` and `sqlglot`.
Without them the table reads 424/1 and 149 and one RED, which is a fact about the
interpreter and not about the tree. Mutation harnesses are HOST ONLY (FINDING
59) and are not in that table.*

**Both mutation harnesses were run on the host on 2026-09-06 and are green:**
`mutate_fidelity` **70/70**, `mutate_cost` **58/58**, sources restored.

---

# WHAT IS LEFT: FOUR SLOTS

```
region              tier                        n   note
Sub-Saharan Africa  verbatim_with_provenance    1   requires_provenance:
                                                    LOCAL_LANGUAGE  <- THE LAST FLOOR
Sub-Saharan Africa  published_translation_only  1
East Asia           verbatim_with_provenance    1
Arabia              verbatim_with_provenance    1   RULING 77 -- CIH 541, and
                                                    F6's ONE gloss declaration

delivered so far: 41 persia-06-shahrestaniha, 42 scandinavia-06-tjurko-bracteate,
                  43 scandinavia-07-rycksta-grikkium   (all verbatim_with_provenance)
gloss_capable 0 of 1 declared   expect_quoted_from_original_cases 0   vme_quotation_cases 0
```

`Below the floor: {'Sub-Saharan Africa': 3}`. **Persia's and Scandinavia's are
closed. Africa's is the only per-region floor left in the whole of Block F, and
the slot that closes it is the hardest capture in the tranche.**

---

# 1. THE AFRICA SLOT, AND ITS PREDICTION MUST BE WRITTEN BEFORE IT IS CURATED

Africa's three source-language records are **0 local + 2 empire-language from the
region + 1 about it** — `africa-01-ezana-stone` and `africa-04-silko-talmis` are
African rulers writing in Greek. The provenance line now prints that as **"2
SPEAKING and 1 spoken about"** rather than as a bare deficit (FINDING 68), and the
second list it prints — regions with NO record speaking at all — is empty. **Ge'ez
is what the slot is for.**

**NOTHING WAS HUNTED FOR THIS SLOT AND NO NEGATIVE IS RECORDED AGAINST IT.** That
sentence is here so a later session does not read silence as a failed search. Two
leads, neither opened: **Beta maṣāḥǝft** (`betamasaheft.eu`, Hamburg, Ge'ez with
translations) and the **RIÉ** corpus of Aksumite inscriptions (Bernand, Drewes,
Schneider — print, in copyright, so ruling 74's four conditions would govern).
**CORRECTED 2026-09-06, FINDING 80.** This sentence read: "`africa-01-ezana-stone`
is already the GREEK of a stone that also carries Ge'ez." IT IS NOT. That record is
`published_translation_only`; its `original_text_excerpt` is a bracketed instruction to
a later session and classifies as `pointer`, not retrieval eligible; its translation is
the Greek titulature quoted from a news website. **The corpus holds no register of the
Ezana Stone's own words in any language**, and Africa's two empire-language records are
`africa-04-silko-talmis` and `africa-05-adulis-throne`. The slot is therefore not a
second register of a text already held — any Aksumite royal text in Ge'ez serves it.

**THE OWED PRE-REGISTRATION.** FINDING 79 and FINDING 73 disagree about what this
record will do to the index, and the disagreement is testable:

```
FINDING 73 says   curating a region damages that region's own gold cases
                  -> a Ge'ez record should crowd Africa's cases
FINDING 79 says   the crowder is the record that RESEMBLES the target, not the
                  one from the same region -- F6 curated TWO Scandinavian records
                  and only the Elder Futhark one crowded the two Elder Futhark
                  cases
                  -> a Ge'ez record, against a corpus whose Africa records are
                     GREEK, should crowd almost nothing
```

**Write the prediction, in ruling 78's shape, with what would refute it, BEFORE
the record is curated.** Ruling 78's P3 is the only prediction this project has
confirmed on its own terms, and it was confirmed because it was written first.

---

# 2. THE GLOSS DECLARATION, WHICH IS STILL RULING 77's AND HAS TWO FALLBACKS

**CIH 541**, `dasi.cnr.it/project/1/epigraphs/2382`, DOI `10.82194/dasi-epi-2382`
— read in full by a person in `F5_PART3_BROWSER_PASSES.md`, CC BY 4.0 source text
AND CC BY 4.0 English translation on one record, three named-editor variants in a
printed apparatus. **Declare that F5's session read it, the way records 41-43
declare their own captures.**

**If it does not land, no new curation is needed.** Two records already in the
corpus carry published alternative readings inside chunks the loader chunks:

```
persia-06-shahrestaniha           §12 hrōmāyīg published as "the Greek";
                                  §28 wīst-ē published as "twenty-one";
                                  §29 two mountain-rulers left unread
scandinavia-07-rycksta-grikkium   Óleifr/Gulleifr, two readings of one name the
                                  edition prints with a slash in EVERY register
```

**Neither is declared, and a second declaration is over-delivery that
`check_delivery` fails on the day it happens.** One declaration, one record.

---

# 3. THE EAST ASIA SLOT HAS A LEAD NOBODY HAS FOLLOWED, AND IT SETTLES A MIS-REGIONING

`F6_START.md`'s debt list: **`M2 I` and the banked `M 5794 I` are Turfan finds and
are EAST ASIA records under this corpus's findspot rule, not Persia. Settling that
mis-regioning is F6's.**

**Browser pass 2 found the corpus they belong to and it is open.**
`parsigdatabase.com/surf/` carries **Manichaean Middle Persian, 59 texts from
Boyce 1975's reader**, transcribed, transliterated and translated, with **the
manuscript versions from the Turfanforschung Digital Turfan-Archive**. The rights
position is the two contradictory sentences record 41 quotes verbatim, and the
edition behind each text is named on the page.

**A Turfan Manichaean text is an EAST ASIA record by findspot and its language is
Middle Persian or Parthian.** That is the East Asia slot and the mis-regioning
settled in one record — but check the edition's date before taking it: Boyce 1975
is in copyright and ruling 74's four conditions would have to be met, where
`šahrīhā ī ērān` rested on Jamasp-Asana 1897–1913 and did not.

---

# 4. THE AFRICA `published_translation_only` SLOT

No source-language text, a cited published translation. The cheapest of the four
and deliberately last. `noorlib.ir` is open (browser pass 2) and states no
licence, so ruling 74's third condition applies in the form it prescribes: **the
record says the source states no terms, in those words.**

---

# THE FOUR REGISTRATIONS EVERY NEW RECORD NEEDS, AND THREE OF THEM ARE NEW

A record is not curated until all four exist. `ingest.verify` fails on any one of
them, and two of the four did not exist before 2026-09-06.

```
1  data/seed_corpus/<region>/<file>.json     the record
2  data/corpus_tiers.json  -> tiers          the DECLARED tier
3  data/corpus_rights.json -> records        NEW: the rights cell (ruling 74)
4  data/curation_cost.json -> records        the ledger entry, with an `agent`
                                             on EVERY phase (NEW: FINDING 70)
```

**And raise the document count.** `ingest/verify.py` holds
`check(len(docs) == 43, ...)`. It moves once per record, in that record's own
commit, and `grep -rn "== 43" ingest eval scripts ui` must find that line and
nothing else (FINDING 66).

## The rights cell, in full

Seven positions: `open_licence_stated`, `permission_stated_no_licence`,
`public_domain`, `all_rights_reserved`, `states_no_terms`,
`two_positions_stated`, `unread`. Every position except `unread` needs
`read_off`, `read_by` and an ISO `read_on`; every position that asserts what a
source SAID must quote it verbatim; `states_no_terms` must NOT carry a quotation;
`two_positions_stated` needs at least two. **`permission_stated_no_licence` was
added by a case** — a source that permits reuse in prose and names no licence is
neither `open_licence_stated` nor `states_no_terms`.

**38 of 43 records are `unread` and that is the honest number.** A new record is
not one of them.

## The agent field

`curator` | `model` | `curator_and_model` | `unrecorded`, on every phase.
**`unrecorded` is refused on any entry curated on or after 2026-09-06.** And
`ingest.cost.trend_line` now REFUSES a trend for any tier whose minutes come from
more than one agent, however far above the floor it sits.

---

# THE TRAPS THIS SESSION HIT, SO THE NEXT ONE DOES NOT

**TWENTY-SIX WORDS OF CURATORIAL ENGLISH TURNED A SOURCE-LANGUAGE CHUNK INTO AN
ENGLISH ONE.** Two bracketed headings in `original_text_excerpt` pushed
`english_marker_ratio` to 0.20 against a threshold of 0.18; the excerpt was
classified `english_rendering`, went not-retrieval-eligible, derived the record as
`published_translation_only` and **failed three checks at once** — tier, cost
ledger and delivery. **Keep every word of your own prose out of the excerpt.**
Register headings go in `original_text_note`.

**MEASURE THE RATIO, DO NOT COUNT IT.** The first draft of that note said
"2/14 = 0.14" by hand. It is 0.167. Call
`ingest.fidelity.english_marker_ratio(chunk)`.

**`findspot_places: []` IS REFUSED.** Omit the key; an empty list is the third
state an empty string creates.

**`ground: "stated"` ON A SPECIFIC PLACE REQUIRES A GAZETTEER ID.** Without one
the honest ground is `regional`. The schema refused this twice today and both
refusals turned out to be facts about the texts.

**A DIRECTIONAL ROLE NEEDS A `focus`.** `destination` with no place marked
`focus` is refused — and on the Rycksta stone the missing focus was real: a
memorial does not say where a man set out from.

**NEVER AUTHOR A COORDINATE.** Runor hands over WGS84 pairs and both Scandinavian
records refused them. A coordinate reaches this corpus through a gazetteer id or
not at all. To add a Pleiades id:

```
python -m ingest.gazetteer --dump data\pleiades-places-20260810.csv.gz --find "Nisibis"
python -m ingest.gazetteer --refresh --dump data\pleiades-places-20260810.csv.gz
python -m ingest.gazetteer --check
```

**Use the CSV dump, not the json.gz** — the json.gz OOMs on the bridge, the CSV
streams. **A name match is not an identification**: three near-miss ids were found
and refused today, including `Edessa (Macedonia)`, which is `precise`, attests
`roman`, and is the wrong Edessa.

**`--refresh` RE-STAMPS `retrieved` ON EVERY CACHED ENTRY.** Expect
`data/gazetteer.json` to show thousands of changed lines for three added ids.
Checked field by field on 2026-09-06: no coordinate, extent, title, period or
feature type moved.

---

# THE ENVIRONMENT

**The bridge** — a Linux VM with the repo mounted — runs everything in the
instrument table, `ingest.gazetteer`, `ui/build_ui_data.py` and `check_ui.mjs`.
It needs its own venv: `psycopg[binary]`, `sqlglot`, `python-dotenv`. The repo's
`.venv` is a Windows venv and is not usable there.

**The host** runs what the bridge cannot: `run_ingest`, `run_embed`,
`run_ranking_check`, and **every mutation harness** (FINDING 59).

**Git from the bridge:** `git --no-optional-locks`, `-c user.name -c user.email`
per commit (the bridge has no identity), and `device_request_delete_permission`
on the repo root or git cannot remove its own `.git/objects/tmp_obj_*` and a
commit dies half-done. Commit messages go in `commit-*.txt` and are gitignored —
**do not `git add` them.**

**READ `git diff --stat` BEFORE EVERY COMMIT AND KNOW WHAT IT CANNOT SHOW.** A
record is `Bin 0 -> N bytes` (FINDINGS 52, 61), a 9 MB `ui/data.js` rebuild is
`2 +-` (FINDING 74), and `data/gazetteer.json` shows thousands of lines for a
re-stamp. **Four instruments in this repository report a change they cannot
show.**

---

# THE RULES THAT CARRY, IN ONE LINE EACH

**THE CAPTURE PATH** — source text and published translations are pasted by the
curator from the cited page. `WebFetch` drops lacuna markers and substitutes
U+0027 for U+2019 (FINDINGS 48, 50); `archive.org/_djvu.txt` is not the page
(FINDING 53).

**A LOCATING FETCH MUST NOT REVEAL WHAT IT LOCATED — AND NEITHER MUST A PROGRESS
MESSAGE.** All three of F6's records declare that their capture was not blind,
because locating and capture happened in one session. **Declare it; do not
mitigate it.**

**AN ALTERNATIVE THIS PROJECT SUPPLIED ITSELF IS WORTH NOTHING** (FINDING 55).

**THE GLOSS MECHANICAL REQUIREMENT** — the hedge AND the statement that the
reading is uncertain both sit inside `original_text_excerpt` or
`reference_translation`, never in `notes`, which the loader does not chunk.
`eastasia-05-liangshu-qin-lun` is the pattern.

**RULING 74** — an in-copyright source may be cited and quoted under four
conditions, declared in the record: the quotation is short and bounded by the
source itself; the work is fully cited; the rights position is stated verbatim,
and where a source states no terms the record says THAT, in those words; and the
use is non-commercial research.

**EVERY TIER STATES THE BOUNDARY OF ITS TRANSLATION SEARCH** in its own words —
what was looked at and what was not. Record 41's says Daryaee 2002 is by its own
title an English translation of exactly that text and **was not opened**.

**RULING 65 — no `--fuse`.**

**WRITE BYTES.** `json.dumps(d, ensure_ascii=False, indent=2) + "\n"`, UTF-8, LF
only, no BOM. 168 archived citation spans point into the corpus by exact offset.

---

# THE DEBT LIST F6 WILL HAND ON

**Owed by F6 itself:**

1. The **Africa Ge'ez** slot and its written prediction.
2. The **gloss declaration**.
3. The **East Asia** and **Africa pto** slots.
4. `F6_RESULT.md`, and `F6.closed = true` only then.
5. A **ranking run after the Arabia record lands** — ruling 78's P1 predicted
   `tc-jabal-dabub` falling from a FOURTH Arabia record and there is still no
   Arabia record. P1 and P2 are untested, not refuted.

**Cheap and unclaimed:**

6. **A Swedish GeoNames dump** — closes both Scandinavian placements, which
   refused coordinates their source handed over. The cheapest work in the repo.
7. **`GUARD a reinstated_on that is not a date is refused`** and three guards in
   `mutate_fidelity` are in `UNMUTATED_AND_OWED` — refusal guards with no
   mutation, printed by name on every harness run.
8. **A diffable manifest beside `ui/data.js`** (FINDING 74).

**Investigations owed, unchanged from `F6_START.md`:** `git log --follow` on
`africa-03-periplus-adulis` (its chunk-id drift is in every ranking run and
unchanged); a ranking pair targeting `eastasia-07-tang-huiyao`;
`southasia-05-brihatsamhita` appearing nowhere in the ranking run; re-reading
`arabia-04-jabal-dabub` and `eastasia-07-tang-huiyao` against ruling 74; the
unlocated "two ṭ" sentence in Petrantoni; Dvivedī's mūla Bṛhatsaṃhitā 2.14; a
GeoNames search for al-Ruwāfa; and browser pass 1's ~20 minutes as
`source_hunting` on a Bhaṭṭotpala record if one is ever written.

**Found today and not taken:** `U 431 Åshusby` — *"and he died abroad among the
Greeks"* — a live F7 candidate, found by the search that produced record 43.

**Standing:** the two older Scandinavian source-language records cite Wikipedia.
Neither is re-curated — nobody re-curates a record — but Runor now exists in this
repository with signa, persistent URIs, a named edition and a stated reuse
permission.
