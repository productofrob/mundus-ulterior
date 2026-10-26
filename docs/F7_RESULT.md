# F7 RESULT — seven of seven placed, four of five tiers on target, and
# **BLOCK F IS CLOSED SIX RECORDS SHORT, AS RULING 69 DECIDED IT WOULD BE**

**`F7.closed` is `true` as of this document, and not before it.** It was set by
locating the sub-tranche named `F7` in
`data/corpus_tiers.json → target_mix → allocation → sub_tranches` **by name and
not by line number** — the file's sub-tranches are `['F3','F4','F5','F6','F7']`
and F7 is the fifth, which is exactly the fact F5 Part 3's first attempt at this
edit got wrong. **Every sub-tranche in Block F is now closed.**

---

## THE STATE BLOCK IS GENERATED. NOTHING BELOW IT IS RESTATED.

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

Run by `python scripts/state_block.py` at a731889 on 2026-09-06. PASTE THIS BLOCK. Do not restate it, and do not compute a figure in it from another figure -- FINDING 76.

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

**The mutation harnesses were run on the host on 2026-09-06 AFTER all seven
records:** `mutate_fidelity` **70/70**, `mutate_cost` **58/58**, sources
restored. The owed lists are unchanged and are still owed — three refusal guards
in `mutate_fidelity`'s `UNMUTATED_AND_OWED` and
`GUARD a reinstated_on that is not a date is refused` in `mutate_cost`'s.

---

# THE SEVEN RECORDS

```
48  persia-07-met-ewer-anahita        catalogue_record            Persia          GLOSS
49  arabia-08-walters-marib-pediment  catalogue_record            Arabia
50  southasia-07-bm-claudius-aureus   catalogue_record            South Asia
51  seasia-08-pong-tuk-lamp           catalogue_record            Southeast Asia
52  seasia-09-oc-eo-unesco            catalogue_record            Southeast Asia
53  eastasia-09-jiutangshu-fulin      published_translation_only  East Asia
54  southasia-06-cosmas-taprobane     published_translation_only  South Asia
```

**Five catalogue records and two published translations, exactly the slot list
ruling 77 left.** F7 placed no source-language record and could not move a
per-region floor, which was true of no other sub-tranche in Block F.

## What each is, in one sentence

- **48 — Met 67.10a, b.** A late Sasanian silver-gilt ewer whose dancing women
  the Metropolitan Museum reads as *either* maenads of Dionysus *or* the Iranian
  Anahita, and says in its own catalogue that no text survives to decide.
  **Carries Block F's last `gloss_capable` declaration.**
- **49 — Walters 21.74.** A pediment fragment from Maʾrib with a nude fertility
  goddess in vine leaves, and a museum sentence that is an argument:
  Greco-Roman motifs entering South Arabian culture in the 2nd and 3rd centuries.
- **50 — BM 1898,0803.11.** An aureus of Claudius minted at Rome in 41–42,
  found in India, **with a vertical chisel-cut through the emperor's head.**
- **51 — the Pong Tuk lamp.** Twenty-seven centimetres of cast bronze with a
  Silenus-head lid and two dolphins, made in Roman Alexandria and — the Bangkok
  National Museum's own account — *"the Indian traders brought into the country."*
- **52 — UNESCO WHC 6572.** The State Party of Viet Nam's own description of
  Óc Eo, naming *"copper Roman gold coins and medals, Han bronze mirrors,
  Persian lamps"* in one clause.
- **53 — 舊唐書 198.** Byzantium described from the Tang court: the golden
  hour-scale, the water-cooled roofs, and four embassies between 643 and 719.
  **The largest excerpt in the corpus at 5,833 characters.**
- **54 — Cosmas, Christian Topography XI.** A Roman merchant and a Persian argue
  before the king of Sri Lanka and he decides it by weighing their two coins.

---

# WHAT CLOSED

```
FOUR OF FIVE TIERS ARE ON TARGET, AND THREE OF THEM CLOSED IN F7
  verbatim_with_provenance   29/29   met in F6, thirteen records early
  published_translation_only  4/4    CLOSED BY RECORD 54
  catalogue_record           16/16   CLOSED BY RECORD 52
  pointer_only                1/1    ceiling, zero new, never moved
  verbatim_machine_english    4/10   SIX SHORT, and no F6 or F7 slot could carry one

BLOCK F'S LAST GLOSS DECLARATION IS MADE
  gloss_capable 7/7 — five contested_reading, two hedged_identification.
  persia-07-met-ewer-anahita, hedged_identification, and it is the only gloss
  case in the corpus about what an IMAGE means rather than what a TEXT says.
  THREE MORE F7 RECORDS CARRIED DECLARABLE MATERIAL AND NONE WAS DECLARED —
  49 ("might be the complement to this vignette"), 51 ("may be wrought in
  Alexandria", plus two datings centuries apart) and 53. One declaration, one
  record; a second is over-delivery check_delivery fails on.

ALL SEVEN RIGHTS POSITIONS ARE NOW GENUINELY EXERCISED
  states_no_terms was used for the first time, on record 51 — see FINDING 88,
  because F7_START said all seven had been.

THE PER-REGION FLOORS ARE UNMOVED AND WERE NEVER AT RISK
  Below the floor: none. No F7 slot counts toward one.
```

---

# THE FIVE FINDINGS

**FINDING 86 — `classify_original`'s non-Latin test is a closed allowlist of
script names, and Thai is not on it.** `non_latin_ratio` scores a page of Thai at
0.00, so a Thai museum description on a find record classifies
`('object_description', 'en', True)`. It is FINDING 82's twin in the ORIGINAL
field and broader: Khmer, Burmese, Sinhala, Tibetan, Javanese, Georgian and
Cyrillic are absent from the tuple too, and the Latin-script branch that rescues
transliterations is never reached on a find record. **It cost F7 the two best
Southeast Asian institutional records the search found** — Phu Khao Thong (SAC)
and Khlong Thom (PSU), the latter naming Roman gold coins and Greco-Roman seals
in its own words — **and the BnF cameo of Shapur I seizing Valerian**, whose
description is French. All recorded as searched failures under ruling 75 and none
curated, which is the decision F6 took on the Turfan vein for FINDING 82's sake.
**Not fixed here**, and adding `"THAI"` to the tuple is the wrong shape of fix.

**FINDING 87 — the licence a museum advertises on an object page is not
necessarily the licence covering the text on it.** `art.thewalters.org/object/21.74/`
carries eleven `Creative Commons License` badges, every one beside a
`Download Image` control and every one linking to CC0; a search pass had already
reported the cell as CC0. The policy page says the CC0 grant covers *images and
metadata* and that **"The longer text descriptions about the artworks on this
website are released under the GNU Free Documentation License."** What record 49
quotes is a longer text description.

**FINDING 88 — `F7_START.md` said all seven rights positions had been exercised.
Six had.** `states_no_terms` had never been used. The claim came from F6_RESULT
reporting *"TWO RIGHTS POSITIONS EXERCISED FOR THE FIRST TIME"* when one of the
two, `open_licence_stated`, was not new — a count computed in prose rather than
read from the file, which is FINDING 76's defect in a sentence instead of a table.

**FINDING 89 — the fabrication-marker guard fired for the second time, and the
sentence that had already gone false two sub-tranches ago is the one nothing was
checking.** `eval.test_answer_eval` went 425 → 424/1 the moment record 53 landed:
`weilue-ruler-selection` excludes `deposed`, and the Jiu Tangshu's English says a
Fu-lin king *"is deposed and another man is put in his stead."* The case survives
and one marker dies, which is FINDING 81's resolution. **The finding is the part
the guard did not catch:** the case's own `why` and `refusal_is_correct_because`
claim four words are absent from the entire corpus, and `chosen` has been in
`persia-05-abnun`'s published English **since F5** — because the guard reads
`expect_answer_excludes` and no check reads prose. Both sentences are kept as
written and the note records that they are false.

**FINDING 90 — the runbook named its own commit hash, was committed, and
falsified its own abort condition before anybody could read it.**
`F7_HOST_RUNBOOK.md` opened *"Tree: `50c19fe`"* and aborted on `HEAD ≠ 50c19fe`;
committing it moved `HEAD` to `327bd2c`, which is what the first reader hit.
`git diff --name-status 50c19fe..327bd2c` is one line and it adds the runbook.
Step 2 and the abort table are now denominated in **what the run is a function
of** — five paths — rather than in a commit, because an abort condition
denominated in a hash is a condition about history and the one that matters is
about content.

**And FINDING 91 is in `F7_RANKING.md`**, where the run that produced it is read.

---

# THE PREDICTIONS — RULING 79, FIVE OF THEM, WRITTEN BEFORE ANY RECORD EXISTED

Written in `F7_CURATION_START.md` at `d2868fc`, each denominated in `beaten_by`
chunk ids rather than in regions (FINDING 83), each naming its own refutation.
**Read in full in `F7_RANKING.md`.**

```
P1  CONFIRMED   cefu-yuangui-fulin-glass 4 -> 5, with eastasia-09's chunk in its
                beaten_by. 拂菻 crowds 拂菻 for the second sub-tranche running, and
                this time an ENGLISH chunk beats a Literary Chinese target.
P2  REFUTED     au-oc-eo-medallion held at rank 1 with an EMPTY beaten_by and an
                unchanged gap, and seasia-09 appears in no window in the run.
                The crowder never arrived.
P3  REFUTED     persia-07 appears in no beaten_by list at all — the second of the
                two refutation directions the prediction named in advance.
P4  CONFIRMED   one of five catalogue records crowds anything (predicted at most
                two); both published translations do.
P5  CONFIRMED   recall@6 0.6818 -> 0.6591; thirteen pairs moved, all worse, none
                improved. Block F is now 0 better / 36 across three
                record-adding runs.
```

**Three confirmed, two refuted, and the refutations are worth more.** P2 killed a
mechanism's reach — resemblance explains the middle of the list and has now
failed twice at the top of it. P3's refutation produced the run's best evidence:
`bronze-heracles-verethragna-from-mesene` fell nine ranks with a `beaten_by`
identical entry for entry and a similarity gap identical to four decimal places.

---

# WHERE BLOCK F ACTUALLY ENDED

This is the statement `F7_START.md` said F7 owed when it closed, and ruling 69
governs it.

```
                              at F0 open   now     target at 60
records                           24        54          60      SIX SHORT
verbatim_with_provenance          11        29          29      met
verbatim_machine_english           0         4          10      SIX SHORT
published_translation_only         1         4           4      met
catalogue_record                  11        16          16      met
pointer_only                       1         1           1      met (ceiling)

tranche delivery                            30 of 36 allocated
```

**Four of five tiers land exactly on their target and the corpus still ends six
records short, because all six missing records are one tier.** That is FINDING 85,
predicted before F7 began and confirmed by F7's close. The gap is
`verbatim_machine_english` — the tier `F3-F7` predicted would become the common
case, on the argument that local non-English sources mostly have no published
English.

**RULING 69 IS UNTOUCHED AND STILL GOVERNS: the shortfall is accepted, recorded
as MISSED, and `total_at_60` is not lowered.** Nothing in this document adjusts a
target to match what happened. The alternative — restating 60 as 54 — is the move
ruling 56 refused and FINDING 47 is about.

## Why the missing tier is missing, in the words of the sub-tranches that tried

`verbatim_machine_english` needed source-language text with **no reachable
English translation**, which sounds like the easy case and was the hardest one in
the block:

- **F3's Southeast Asia hunt** produced zero vme records across six candidates
  and 9 minutes are retired in the ledger under `seasia-vme-hunt-unresolved`,
  kept and named so the cost of the missing tier is visible rather than absent.
- **F4's Persia hunt** produced zero and 20 minutes are retired under
  `persia-vme-hunt-unresolved`.
- **F6's East Asia slot** was pointed at the Turfan Manichaean vein and could not
  take it, because `classify_translation` hard-codes `lang = "en"` (FINDING 82)
  and parsigdatabase's Manichaean translations are Persian.
- **F6 and F7 hold no vme slot at all**, by ruling 51's ordering: every
  source-language record before every catalogue record, and the cheap tiers last.

**So the tier is not short because nobody tried. It is short because two hunts
found nothing, one vein was blocked by an instrument defect that is still open,
and the allocation had spent its vme slots before the defect was found.**

---

# WHAT F7 SEARCHED AND DID NOT TAKE — ruling 75's shape

All recorded in `F7_CURATION_START.md` before curation, and none of them changed:

1. **BnF `camée.360`, Shapur I seizing Valerian** — an ARK permalink that opens,
   the best Rome↔Persia object in existence, with the BnF's own argument that a
   Roman hand carved it. **Refused for an instrument reason and not a source
   reason**: FINDING 86.
2. **`archaeology.sac.or.th/archaeology/120`** (Phu Khao Thong) and
   **`suvarnabhumi.psu.ac.th/tudb/archaeologicalread/76`** (Khlong Thom) — both
   opened, both Thai, both refused on FINDING 86. Khlong Thom names Roman gold
   coins, Greco-Roman intaglios and Roman mosaic beads in its own keyword line.
3. **`collections.louvre.fr`** — a bot challenge to a real browser and HTTP 429
   to a fetcher, on 2026-09-06. The Bishapur mosaics are behind it. **The second
   negative recorded against a named institution**, after `betamasaheft.eu`'s 403.
4. **Varāhamihira's Pañcasiddhāntikā**, whose second siddhānta is named for Rome.
   Content confirmed by reading Chapter I's translated verses; refused on capture
   quality, because the only reachable English is OCR of an 1889 scan with damage
   inside the verses themselves.
5. **The British Museum holds no Roman-connected Southeast Asian object its own
   search surfaces.** `Ban Don Ta Phet` → 0 results; `Funan` → 1, a Shang finial
   found in China.
6. **The Victorinus coin from U Thong has no institutional record.** The U Thong
   National Museum's virtual museum lists thirteen highlight objects and every
   one is Buddhist or terracotta.
7. **The Pompeii "Lakshmi" ivory (MANN 149425)** — no per-object institutional
   record found.
8. **UNESCO Pyu Ancient Cities (ref 1444)** — opened; its Outstanding Universal
   Value text names trade with Southeast Asia, China and India and no
   Mediterranean link at all. **Myanmar remains a part of Southeast Asia this
   corpus holds nothing from.**
9. **Hirth's extracts L (Xin Tangshu 221b) and I (Wei shu 102)** — readable on the
   same page as the one taken, refused because there is one East Asia slot.

---

# THE PRACTICE, AND WHAT IT CAUGHT THIS TIME

**Every capture was verified by SHA-256 across two machines**, as F6 established.
Seven spans, seven agreements.

```
record  field                    chars   digest (first 24)
48      original_text_excerpt     1023   e424b363437e2831ca5af334
49      original_text_excerpt      700   a40436d0948ed2d5a79c54db
50      original_text_excerpt      183   0740202da25683267f16e041
51      original_text_excerpt      495   9593d792b77de010a267b422
52      original_text_excerpt     1103   8d483080bf9860694d4abf67
53      reference_translation     5833   b54df5cf398d440182f99519
54      reference_translation     2720   d2ad0f03b4ae58d4015eff09
```

**AND FOR THE FIRST TIME IT CAUGHT A CURATOR RATHER THAN A PAGE.** Record 51's
span holds exactly one non-ASCII character — a non-breaking space at index 99,
between `dolphins` and the ordinary space before `were`. The first transcription
on the bridge put the two in the opposite order. **Invisible in every rendering
of the text, and a completely different digest.** It was found by comparing the
two machines, corrected from a code-point dump, and re-hashed. On
`arabia-07-cih541` the practice found a property of the page; on `eastasia-08` it
verified an edit; here it found the curator's own hands.

**Two other things the practice made possible:**

- **Record 50's excerpt is an ASSEMBLY of four British Museum fields** in a
  declared order, and the digest is taken over the RESULT, which is
  `eastasia-08`'s treatment of an edit applied to a join.
- **Record 53's translation-search boundary is a COMPARISON**, not a list of
  places looked at. Hirth's 1885 scan was opened and read against the electronic
  text: the modernization deletes his numbered sentences, respells `Po-ssu` as
  `Po-si`, and adds bracketed identifications where he has none. Four of them —
  `Theodosian`, `Pogonatus`, `Khazarstan`, `clepsydra` — occur nowhere in Hirth's
  translation. **This corpus had cited that page before without knowing it.**

**The page served over HTTP cost a step:** `crypto.subtle` is unavailable outside
a secure context, so SHA-256 was implemented in the page and checked against the
known digest of `abc` before being used on anything.

---

# COST

`python -m ingest.cost_log report` is the only place a curation-cost number may be
read from, and this section names what its rows cover rather than restating them.

**`catalogue_record` n=5 is exactly F7's five catalogue records** — no earlier
catalogue record in this corpus was ever timed. **`published_translation_only`
n=3 is F6's `africa-07-cosmas-sasu` plus F7's two.** Both rows carry
`NOT A TREND` against the floor of 10, and the report's closing line still reads
`NOT YET A COST CLAIM`, because the declared mix is not met and now never will be.

**The cheapest sub-tranche was designed to be cheap and was not.** Ruling 77's
`why_these` called F7 *"the cheapest tier, deliberately last"*. What actually cost
time was **rights**: three of the seven cells required reading a policy page
against an object page, and two of those readings came out the opposite way from
what the object page advertised (FINDING 87, and record 50's refusal of a
site-level CC BY-NC-SA that its own terms page says applies only to marked
content).

---

# WHAT BLOCK G INHERITS

## Instrument debt, and the first two are now load-bearing

1. **FINDING 82 — `classify_translation` hard-codes `lang = "en"`.** Cost F6 its
   East Asia candidate and is one of the four reasons `verbatim_machine_english`
   ended six short.
2. **FINDING 86 — `classify_original`'s script allowlist.** Cost F7 three records
   in one session. **Together these two mean the corpus cannot currently accept a
   modern non-English institutional source at all**, which is the project
   description's stated interest in *"relevant local, non-English sources from
   the regions above"*.
3. **FINDING 89's shape — no check reads prose.** A gold case's justification can
   go false while the assertion it justifies still passes, and one did, for two
   sub-tranches.
4. **No line in `ingest.verify --state` reports language concentration within a
   region.** East Asia's seven source-language records are seven Literary Chinese
   records.
5. **A diffable manifest beside `ui/data.js`** (FINDING 74).
6. **`GUARD a reinstated_on that is not a date is refused`** and three refusal
   guards in `mutate_fidelity` are still in `UNMUTATED_AND_OWED`.

## Cheap and unclaimed

7. **A Swedish GeoNames dump** closes both Scandinavian placements. **A Thai one
   closes `seasia-08-pong-tuk-lamp`'s**, which is stated to three administrative
   levels and recorded `regional` because no gazetteer this corpus holds reaches
   central Thailand. **Three coordinates a source handed over and this corpus
   refused.**
8. **`git log --follow` on `africa-03-periplus-adulis`** — its two chunk-ids still
   do not name their passage, in every run of Block F, and one of the two
   drifting pairs is in F7's fall list.

## Investigations owed, unchanged

9. A ranking pair targeting `eastasia-07-tang-huiyao`; `southasia-05-brihatsamhita`
   appearing nowhere in the ranking run; re-reading `arabia-04-jabal-dabub` and
   `eastasia-07-tang-huiyao` against ruling 74; the unlocated "two ṭ" sentence in
   Petrantoni; Dvivedī's mūla Bṛhatsaṃhitā 2.14; a GeoNames search for al-Ruwāfa.

## Candidates found and banked

10. **`U 431 Åshusby`** — *"and he died abroad among the Greeks"*, Scandinavia,
    found in F6 and not taken by either sub-tranche.
11. **`M2 I`, Mani dispatching Mār Addā into the Roman Empire**, and the banked
    `M 5794 I`. Both Turfan finds, both East Asia candidates under the findspot
    rule, **and both blocked on FINDING 82** plus a reachable English translation.
12. **The Maḥrem / Ares pair** in `africa-06-ezana-rie189`'s notes — an Aksumite
    chancery performing *interpretatio graeca* on its own dynastic god.
13. **The BnF cameo**, blocked on FINDING 86 and reachable the day it is fixed.

## Standing

14. **`africa-01-ezana-stone` is a placeholder with a newspaper citation** and it
    is one of the four members of a tier that is now closed. The tier's four
    members are that placeholder, a public-domain scholarly translation of Cosmas
    on the Aksumite gold trade, Hirth's Jiu Tangshu, and Cosmas on Sopatrus.
    **Three of the four are a region SPOKEN ABOUT and one is a region speaking**,
    which was declared in `F7_CURATION_START.md` before either F7 record existed
    and is reported here because nothing in the repository reports it.
15. **The answer floor is still calibrated at the 24-record corpus** by ruling
    49's corpus clause, and **re-calibration was booked for 60 records** — three
    distinct dates and roughly 270 chat calls. The corpus ended at 54. Whether the
    booking survives a target that was missed is Block G's first question about
    it and this document does not answer it.
