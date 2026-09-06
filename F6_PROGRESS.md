# F6 PROGRESS — 2026-09-06. Three of seven placed, two of three floors closed,
# and F6 IS STILL OPEN

**`F6.closed` is `false` and must stay false.** This is a progress document, not
a result document. `F6_RESULT.md` does not exist yet and nothing here sets a
flag.

---

## THE STATE BLOCK IS `ingest.verify --state` OUTPUT, PASTED

FINDING 75 asked for this and FINDING 76 said why one command was not enough.
Both instruments now exist and this document uses both. Nothing below is
restated and nothing is computed from anything else.

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

And the eleven instruments, generated by `python scripts/state_block.py`,
run on the bridge under an interpreter with `psycopg[binary]` and `sqlglot`:

```
ingest.verify                        green, 43 documents
ingest.test_fidelity                 77   [green]
ingest.test_cost                     64   [green]
eval.test_answer_eval                425   [green]
eval.test_ranking_check              258   [green]
answer.test_answer                   150   [green]
ui/test_build_ui_data.py             19   [green]
scripts/test_recover_baseline.py     56   [green]
scripts/test_harnesses.py            43   [green]
python -m ingest.gazetteer --check   GREEN
node ui/check_ui.mjs                 GREEN
```

---

# What F6 has done

## Two of the three per-region floors are closed, and the third is F6's

```
region              at F6 open   now   floor   what closed it
Persia                       3     4       4   RULING 76 -- record 41
Scandinavia                  2     4       4   ruling 73 -- records 42 and 43
Sub-Saharan Africa           3     3       4   F6's REMAINING SLOT
```

**Persia's was the one that could not be reached at all.** FINDING 71 had it
ending Block F at 3 by construction, with both F6 slots on tiers that do not
count and no Persia slot in F7, while `check_allocation` reported all integrity
checks passed — because it reads the plan and the plan assumes its slots fill.
Ruling 76 re-pointed the slot and record 41 filled it.

## The records placed

```
41  persia-06-shahrestaniha           verbatim_with_provenance  Persia       pal
42  scandinavia-06-tjurko-bracteate   verbatim_with_provenance  Scandinavia  gmq-pro
43  scandinavia-07-rycksta-grikkium   verbatim_with_provenance  Scandinavia  non
```

**Three sentences, and they are why these three:**

- **§33 of Šahrestānīhā ī Ērānšahr** — `ast šāhān šāh ast kēsar`, "some by the
  king of kings and some by the Caesar." A Middle Persian geography divides the
  city-founding of the known world between two builders and puts no verb of
  conflict between them. Persia's other two records are a king's account of
  beating the Romans and a courtier's vow that he will; **this is Rome as a peer
  institution**, and the corpus held no Persian text that said so.
- **Tjurkö 1** — `wurte runoz an walhakurne`, runes cut on **`walhakurn`, the
  grain of the Romans**: a Proto-Norse kenning for gold built on the word behind
  *Welsh*, *Wallonia* and *walnut*, on a gold bracteate that is itself an
  imitation of a Roman imperial medallion.
- **Sö 163** — `fór Óleifr/Gulleifr í Grikkjum gulli skipti`, "travelled to
  Greece, divided up gold." **Five hundred years after Tjurkö and in the other
  direction**: the gold is there now and the Scandinavian is the one who moves.
  Gold is in both sentences and neither inscription was chosen to make the pair.

## The decisions, and they were the project owner's

Rulings 76, 77 and 78, in `F6_RULINGS.md`, all accepted 2026-09-06 with the
recommendation attached to each.

## The debts closed

```
FINDING 78   both guards F6 added are now asserted AND mutated, and the two
             harnesses gained the coverage check that would have said so
FINDING 68   the SPEAKING subtotal is printed, and a second list beside it
FINDING 70   an `agent` field per phase, and trend_line REFUSES a trend across
             two agents -- which turned "first 6 mean 5.9 -> last 6 mean 24.7
             (up)" into NOT A TREND. The "up" was the agent changing.
Ruling 74    data/corpus_rights.json, six positions and then seven
FINDING 75   `python -m ingest.verify --state`
FINDING 76   `python scripts/state_block.py` -- runs the other ten
Debt item 1  browser pass 2, F6_BROWSER_PASS2.md
Debt item 2  FINDING 73's fall table, read; the predictions are ruling 78
Debt item 3  Persia's floor, decided
```

---

# What F6 still owes, in the order the next session will want it

## 1. THE AFRICA SLOT, WHICH IS THE LAST FLOOR AND THE HARDEST CAPTURE

`{Sub-Saharan Africa, verbatim_with_provenance, 1, requires_provenance:
local_language}`. **Ge'ez is what that slot is for.** Africa is the only region
with no source-language record in a language of the region: its three are
`0 local + 2 empire-language from the region + 1 about it`, and the two are
African rulers writing in Greek, which the provenance line now prints as
**"2 SPEAKING and 1 spoken about"** rather than as a bare deficit.

**Nothing was hunted for this slot in this session and no negative is recorded
against it.** What is known from F4's own notes is only that Ge'ez has no
published translation for most of what is open. Two leads, neither opened:
**Beta maṣāḥǝft** (`betamasaheft.eu`, Hamburg, Ge'ez with translations) and the
**RIÉ** corpus of Aksumite inscriptions, which is print and in copyright.
`africa-01-ezana-stone` is already the GREEK of a stone that also carries Ge'ez.

## 2. F6's ONE GLOSS DECLARATION IS UNMADE, AND TWO RECORDS ALREADY CARRY THE
##    MATERIAL

Ruling 77 spends it on **CIH 541** at `dasi.cnr.it/project/1/epigraphs/2382`,
which is unclaimed and fully read in `F5_PART3_BROWSER_PASSES.md`. **That is
still the right record and the slot is still an Arabia
`verbatim_with_provenance`.**

But if it does not land, **no new curation is needed to make a declaration**:

- `persia-06-shahrestaniha` — §12's `hrōmāyīg` published as "the Greek", §28's
  `wīst-ē` published as "twenty-one", §29's two mountain-rulers the translator
  leaves unread. All three inside `reference_translation`.
- `scandinavia-07-rycksta-grikkium` — `Óleifr/Gulleifr`, two readings of one
  name the edition prints with a slash in every register, inside both chunks.

**Neither was declared, because a second declaration is over-delivery and
`check_delivery` fails on it the day it happens.**

## 3. THE RANKING RUN IS DONE, AND IT IS `F6_RANKING.md`

*CORRECTED 2026-09-06, later the same day. This section read "THE RANKING RUN IS
OWED AND CANNOT BE RUN FROM THE BRIDGE" and listed all three predictions as
untested. It was written before the host ran it. Kept as a heading rather than
deleted, because a progress document whose corrections are removed looks like one
that was never wrong -- and because this is the fourth stale figure this session
has had to correct in a document it wrote itself.*

**Two runs happened, and the first was made with the wrong view — the
instruction omitted `--with-distractors`.** Both are archived and both are read
in `F6_RANKING.md`.

```
P3   CONFIRMED, like-for-like, with the crowder named:
     vimose-runes 16 -> 18, beaten by BOTH chunks of tjurko-bracteate.
     AND thorsberg-chape-niwajemariz 24 -> 29, which nothing predicted.
P1   NOT TESTED. F6 has placed no Arabia record; tc-jabal-dabub held at 6 with
     no F6 record in its beaten_by list. Stands unmodified.
P2   NOT TESTED. F6 has placed no East Asia record; probe-tamil-akananuru-en
     held at 6, same. Stands unmodified.
```

**FINDING 79 came out of it and it bears on the slot F6 has left.** The crowder
is the record that RESEMBLES the target — script, language stage, genre — and not
the record from the same region: F6 curated two Scandinavian records and only the
Elder Futhark one crowds the two Elder Futhark gold cases. **On that reading a
Ge'ez Africa record should crowd almost nothing; on FINDING 73's reading it should
crowd Africa's cases. The Africa slot is the experiment, and the prediction should
be written before it is curated.**

And FINDING 77, restated because it happened twice: **six pairs fell, none
improved, and recall@6 AND MRR@10 are both identical to sixteen decimal places** —
recall@6 blind because no pair crossed rank 6, MRR@10 blind because all six were
already outside the top ten.

## 4. THE REST OF F6's SLOTS

```
Sub-Saharan Africa  published_translation_only  1
East Asia           verbatim_with_provenance    1
Arabia              verbatim_with_provenance    1   RULING 77, CIH 541, gloss
```

---

# What this session found that was not on anyone's list

**`eval.test_answer_eval` is 425 and `F6_START.md` said 422** — FINDING 76, and
the number had been computed from a measured one rather than read off the
instrument that had already printed it.

**A seventh rights position exists because a source needed it.**
`permission_stated_no_licence`: Riksantikvarieämbetet permits reuse in prose and
names no licence. FINDING 69 separated REACHABLE from LICENSED; this separates
LICENSED UNDER A NAMED LICENCE from PERMITTED IN PROSE.

**Thirty-eight of forty-three records have an `unread` rights position**, which
is the honest number and is now countable rather than recoverable only by
reading records by hand.

**Twenty-six words of curatorial English turned a source-language chunk into an
English one.** Two bracketed headings on record 42's excerpt pushed
`english_marker_ratio` to 0.20 against a threshold of 0.18 and failed three
checks at once. The margin without them is **0.167, measured** — a hand count in
the first draft said 0.14 and was wrong, which is FINDING 76 committed in
miniature in the session that recorded FINDING 76.

**The schema corrected the curator twice, on two records, and both corrections
were facts about the texts** — a `stated` ground with no id on Merv and Herat,
and a `destination` role with no `focus` on Grikkium, where the missing focus is
that a memorial does not say where a man set out from.

**A fourth instrument reports a change it cannot show.** `git diff --stat`
cannot see a record (FINDINGS 52, 61) or the UI bundle (FINDING 74), and
`data/gazetteer.json` showed **4,496 changed lines for three added entries**
because `--refresh` re-stamped `retrieved` on all 58 cached Pleiades entries.
Checked field by field against HEAD: nothing else moved.

**The cheapest unclaimed work in the repository is a Swedish GeoNames dump.**
Both Scandinavian records refused a placement that their source handed over as a
WGS84 coordinate, because W1 forbids authoring one and the repository's only
GeoNames dump is China.

**`U 431 Åshusby` is a live F7 candidate and was found and not taken** — "and he
died abroad among the Greeks."

**The two older Scandinavian source-language records cite Wikipedia.** Neither
is re-curated — nobody re-curates a record — but Runor now exists in this
repository with signa, persistent URIs, a named edition and a stated reuse
permission, and F7 or Block G should know that before writing anything else
Scandinavian.
