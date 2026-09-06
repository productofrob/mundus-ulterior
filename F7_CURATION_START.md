# F7 CURATION START — seven slots pointed at seven named candidates, one
# gloss declaration placed, five predictions pre-registered, and one instrument
# defect found before it could cost a record

**Written at `5b33934`, before any F7 record file exists**, after a browser and
search pass over candidates for all seven slots on 2026-09-06. Ruling 78 requires
the predictions to be written first; ruling 75 requires every miss to be recorded
as a searched failure with its reason named. Both are done here rather than in
`F7_RESULT.md`, where they would have an explanation available for them.

**`F7.closed` is `false` and this document does not move it.**

---

## THE OPENING STATE REPRODUCES

`python -m ingest.verify --state`, run on the bridge at `5b33934` on 2026-09-06,
reproduces the block pasted in `F7_START.md` line for line: **47 documents, 153
chunks, 33 parallel pairs, six loader warnings, all integrity checks passed.**
`python scripts/state_block.py` at the same tree prints the eleven instruments
**all green**. Neither block is restated here — `F7_START.md` carries them and
FINDING 76 is about restating a generated figure.

The bridge venv was rebuilt from scratch for this session
(`python3 -m venv ~/venv`, then `psycopg[binary]`, `sqlglot`, `python-dotenv`);
without it the table reads 424/1 and 149 and one RED, which is a fact about the
interpreter and not about the tree.

---

# THE SEVEN SLOTS AND WHAT EACH IS POINTED AT

```
#  region          tier                        candidate                          rights position expected
1  East Asia       published_translation_only  Jiu Tangshu 198, Fulin (Hirth K)    two_positions_stated
2  South Asia      published_translation_only  Cosmas, Christian Topography XI     public_domain
3  South Asia      catalogue_record            BM 1898,0803.11 chisel-cut aureus   all_rights_reserved
4  Arabia          catalogue_record            Walters 21.74, Maʾrib pediment      open_licence_stated
5  Persia          catalogue_record            Met 67.10a,b, Sasanian ewer  GLOSS  public_domain
6  Southeast Asia  catalogue_record            Bangkok NM, the Pong Tuk lamp       all_rights_reserved
7  Southeast Asia  catalogue_record            UNESCO WHC 6572, Óc Eo–Ba Thế       two_positions_stated
```

**No slot is on a tier that counts toward a source-language floor**, and
`Below the floor: none.` F7 cannot move a floor and is not trying to.

---

## 1 — East Asia, `published_translation_only`

**`eastasia-09-jiutangshu-fulin`.** 舊唐書 198, the Fulin account: Fulin bordering
Persia, window-bars of crystal and opaque glass, the gold-chased east gate, the
golden scale with twelve balls that marks the hours — and then the diplomatic
record, the embassy of Po-to-li in 643, tribute in gold and silk paid to the
Arabs, and further embassies in 667, 701 and 719.

**The translation is F. Hirth's**, `China and the Roman Orient` (Shanghai & Hong
Kong, 1885) — his lettered extract **K**. Capture is from the clean HTML at
`depts.washington.edu/silkroad/texts/romchin1.html`, **opened 2026-09-06, 102,048
characters**, carrying the heading `From the Chiu-t'ang-shu, ch. 198 (written
mid-10th Century C.E.), for 618-906 C.E.:` and the source line
`From: F. Hirth, China and the Roman Orient ... (Shanghai & Hong Kong, 1885), pp. 35-96.`

**The page states TWO rights positions and they are different in kind.** Both
read off that URL on 2026-09-06, verbatim:

```
"Unless otherwise indicated the specific electronic form of the document is
 copyright. Permission is granted for electronic copying, distribution in print
 form for educational purposes and personal use. If you do reduplicate the
 document, indicate the source. No permission is granted for commercial use of
 the Sourcebook."

"[Any modernization © 2000 Jerome S. Arkenberg.]"
```

`eastasia-08-songshi-fulin`'s cell records the first of these and not the second,
and **that omission matters here in a way it did not there**: on `eastasia-08` the
Sourcebook supplied one half of a bilingual record, and on this record it supplies
the whole of it. So the position is `two_positions_stated` and the second
statement is the one about the text this record actually carries.

**The translation-search boundary this tier owes** is therefore unusually
concrete: the record must say that the English is Hirth 1885 **as modernized by
Arkenberg in 2000**, and must state what was compared against Hirth's own 1885
text and what was not. Hirth's scan is public domain and reachable
(`archive.org/details/chinaandromanor00hirtgoog`, metadata
`possible-copyright-status: NOT_IN_COPYRIGHT`; the DLI copy
`in.ernet.dli.2015.24269` carries `Rights: In Public Domain`), and the extract
sits at printed **pp. 51–56**. Those page numbers were read off the scan's
page-text endpoint by the search pass **and have not yet been confirmed by me in
a browser** — that is owed before capture, and it is exactly the kind of figure
FINDING 76 says must be read rather than inherited.

## 2 — South Asia, `published_translation_only`

**`southasia-06-cosmas-taprobane`.** `Christian Topography` XI: **Sopatrus, a
Roman merchant, and a Persian, at the court of the king of Sielediba**, and the
king weighing the Roman gold `nomisma` against the Persian silver `miliarision`
and judging the Romans "clearly the more splendid people"; with the surrounding
survey of the island as the Indian Ocean's central entrepôt, receiving silk from
the east and passing it west, and the list of the five pepper marts of Male.

**McCrindle 1897, pp. 358–373**, at
`https://www.tertullian.org/fathers/cosmas_11_book11.htm` — **opened 2026-09-06,
32,224 characters**, heading `Cosmas Indicopleustes, Christian Topography (1897)
pp. 358-373.  Book 11`, and `Sopatrus`, `nomisma` and `miliarision` all present
in the transcription. Rights, verbatim from the foot of the page:

```
"This text was transcribed by Roger Pearse, 2003.  All material on this page is
 in the public domain - copy freely."
```

→ `public_domain`, the position `africa-07-cosmas-sasu` opened yesterday.

**TWO COSTS OF THIS CHOICE, DECLARED HERE RATHER THAN DISCOVERED IN THE RESULT.**

1. **It is the same author, the same translator, the same edition, the same
   transcriber and the same site as `africa-07-cosmas-sasu`**, curated in F6 one
   day earlier. Two of the tier's four members will come from one 1897 book.
2. **It makes the tier three-quarters "a region SPOKEN ABOUT".** `africa-01`,
   `africa-07` and this one are all Roman-world authors describing somewhere
   else; only slot 1 is a text of its own region. `published_translation_only`
   does not count toward the source-language floor and FINDING 68's provenance
   line will not move, so nothing in the repository will report this. It is
   reported here.

**What was examined and NOT taken instead**, and it is the better answer to cost 2:
the **Pañcasiddhāntikā** of Varāhamihira, tr. G. Thibaut and Sudhākara Dvivedī
(Benares, 1889) — a South Asian text whose second siddhānta is *named for Rome*
and whose ahargaṇa is reckoned from Yavanapura. The full text was fetched from
`archive.org` in the browser (**748,591 characters**) and Chapter I's translated
verses were read: *"There are the following Siddhantas : The Paulina, the Romaka,
the Vasishtha, the Saura and the Paitamaha"* … *"near to it stands the Siddhanta
proclaimed by Romaka"*. **Refused on capture quality, not on content.** The only
reachable text is OCR of an 1889 scan and the damage is in the verses themselves
— `1 am going to explain`, `con junctions`, `Vasishtha aro foremost`, `J'at her
and teacher`. A digest can prove the corpus copied a damaged text faithfully; it
cannot repair it, and a `published_translation_only` record is nothing but its
translation. The Roman content in Chapter I is also two stanzas. **Named for
Block G, findable in one step.**

## 3 — South Asia, `catalogue_record`

**`southasia-07-bm-claudius-aureus`.** British Museum **1898,0803.11**, opened in
the browser 2026-09-06. Gold aureus of Claudius I, minted at Rome 41–42 CE,
7.72 g, findspot `Excavated/Findspot: India (historic - pre-1947) (probably)`,
donated 1898 by the Raja of Pudukkottai — and the curator's comment is the whole
point of taking this coin rather than any of the other seventy-four in the same
bibliography term: **`Vertical chisel-cut on head.`** A Julio-Claudian gold coin
carried to South India by the Red Sea trade and then deliberately defaced there.

**The rights cell is the interesting one and it is NOT `open_licence_stated`.**
`britishmuseum.org/terms-use/copyright-and-permissions` says the Museum
*"increasingly intend[s] to release content on our website under a Creative
Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
licence"* and that *"The Creative Commons licence does not apply to everything on
our website. Content that is published under the Creative Commons licence will be
marked with the following logo"*. **The object page carries no such marking.**
Searched in the live DOM on 2026-09-06: zero occurrences of "Creative Commons",
zero links to `creativecommons.org`, and one copyright line, `© 2026 … Trustees of
the British Museum`. So for THIS record the licence does not apply and the honest
position is `all_rights_reserved`, with the site-level intent quoted beside it so
a later reader can see why the more flattering reading was refused.

## 4 — Arabia, `catalogue_record`

**`arabia-08-walters-marib-pediment`.** The Walters Art Museum **21.74**,
`https://art.thewalters.org/object/21.74/`. Fragment of a pediment with a
goddess, 2nd century CE, Sabaean, from **Maʾrib** — the same city as
`arabia-07-cih541`, which F6 curated yesterday and which refused
`pleiades:39379` on a name match. Calcite-alabaster, 52 × 54 × 13 cm, gift of
Giraud and Carolyn Foster, 2014.

The Roman connection is **stated by the museum in its own words**, which is the
hardest attribute to find in this tier:

```
"With the increasing influence of Greco-Roman culture during the 2nd and 3rd
 centuries CE, new artistic styles and motifs, such as this female deity, became
 part of ancient South Arabian culture."
```

**Rights: `open_licence_stated`.** Creative Commons Zero (CC0) on the object page,
with the institutional policy at `thewalters.org/about/policies/rights-reproductions/`.

*Note for the record's own notes, not for the rights cell:* the provenance chain is
market-derived (James Nash, London, 1963 → Foster, 1965 → Walters, 2014) and the
Walters publishes it openly. The record should carry it as the museum states it.

## 5 — Persia, `catalogue_record` — **AND IT CARRIES F7's ONE GLOSS DECLARATION**

**`persia-07-met-ewer-anahita`.** The Metropolitan Museum of Art **67.10a, b**,
`https://www.metmuseum.org/art/collection/search/325865`, opened in the browser
2026-09-06. Silver, mercury-gilded ewer, ca. 6th–7th century CE, Iran, Sasanian;
four dancing women under floral arcades, grape and leaf branches, a panther
drinking from a ewer. **Rights: `Public Domain` stated on the object page**, under
the Met's Open Access policy.

**THE GLOSS, AND EVERY WORD OF IT IS THE MUSEUM'S.** Quoted verbatim from the
object description, which on a find record is `original_text_excerpt` and is
retrieval-eligible — *inside a chunked field, which is where F3's two failed
declarations were not*:

```
"Both the females and their decorative motifs recall representations of the
 maenads, attendants of Dionysus. However, it has been suggested that these
 figures have been adapted to the cult of the Iranian goddess Anahita. No texts
 survive to explain the appearance or function of these female figures, but it
 seems likely that vessels decorated with motifs such as these would have been
 intended to hold wine for court celebrations or religious festivals."
```

That is (a) **a genuine alternative reading** — maenads of Dionysus, or the
Iranian Anahita — and (b) **a statement that the reading is uncertain**, twice
over: *"it has been suggested"* and *"No texts survive to explain"*. Neither is
this project's. FINDING 55 is satisfied, and `arabia-07-cih541` is the pattern it
copies.

**Kind: `hedged_identification`**, and it is the second in the corpus after
`eastasia-05-liangshu-qin-lun`. The gloss list will read 5 `contested_reading` and
2 `hedged_identification` at 7 of 7.

**One declaration, one record.** A second is over-delivery that `check_delivery`
fails on the day it happens, and the other six F7 records carry no declaration
however declarable their material looks.

**And the subject is the thesis.** The dispute is over whether a Sasanian court
silversmith was drawing a Greek maenad or an Iranian goddess. That is the whole
question this corpus exists to ask, argued by a museum about an object rather
than by this project about a text.

## 6 — Southeast Asia, `catalogue_record`

**`seasia-08-pongtuk-lamp`.** Bangkok National Museum, Fine Arts Department, at
`http://www.virtualmuseum.finearts.go.th/bangkoknationalmuseums/index.php/en/hilight/135-roman-lantern.html`
— **opened in the browser 2026-09-06**, in English, headed `ROMAN LANTERN`. The
bronze lamp found at Pong Tuk, Kanchanaburi, with a lid moulded as the head of
Silenus, a palm-leaf handle and two colliding dolphins. The museum's own text:

```
"This lamp may be wrought in Alexandria, Egypt when under Roman rule … and the
 Indian traders brought into the country. The district still located on the trade
 routes of the Indian traders once traveled by."
```

**Two defects to declare in the record, not to hide.** There is **no accession
number** on the page — `museum_number` will be absent, as it is on
`persia-03-coin`'s siblings — and the `ERA AGE` field is printed as `...`, so the
museum states no date at all and the record may not supply one. The page is
served over **HTTP**, not HTTPS. Rights are a bare footer, `© 2009-2014 by …`,
to be captured verbatim at curation → `all_rights_reserved`.

**This record could not be reached by a fetcher and was reached by a browser.**
The search pass hit an HTTPS-upgrade redirect loop and a `403 Host not in
allowlist` and recorded the URL as unverified. It opens in Chrome on the first
try. That asymmetry is worth keeping: a negative recorded by one instrument is
not a negative about the source.

## 7 — Southeast Asia, `catalogue_record`

**`seasia-09-oceo-unesco`.** UNESCO World Heritage Centre tentative list, ref
**6572**, `https://whc.unesco.org/en/tentativelists/6572` — *Oc Eo - Ba The
archaeological site*, State Party Viet Nam, submitted 04/01/2022. The
description names, in the State Party's own words:

```
"copper Roman gold coins and medals, Han bronze mirrors, Persian lamps; glass
 materials, precious metals imported from India and Mediterranean countries
 further clarify the capacity of sea exploitation."
```

**Rights: `two_positions_stated`.** `whc.unesco.org/en/disclaimer/` states both
that site elements *"cannot be copied or retransmitted by any means without
explicit authorisation"* and that **UNESCO-owned** content is under
**Creative Commons Attribution-ShareAlike 3.0 IGO** — and a tentative-list
description is text submitted by a State Party, which the disclaimer treats
separately from UNESCO-owned content. The record's cell must say which half it
believes covers the text it quotes, and say that the question is not settled by
the page. This is the shape `eastasia-08-songshi-fulin` named and could not
express; F7 now has two instances of it in one tranche.

**THE DUPLICATION IS DELIBERATE AND IS DECLARED.** `seasia-02-oc-eo-site` already
covers Óc Eo and cites **Wikipedia**. Nobody re-curates a record, so it stays.
What this adds is a different genre of witness for the same site — an
intergovernmental nomination record authored by the State Party — and, because it
is English prose about an object class the corpus already holds a record of, it
is the cleanest subject-crowding experiment F7 can run. See P2.

---

# FINDING 86 — `classify_original`'s non-Latin test is a closed allowlist of script names, so a script that is not on the list is silently treated as Latin, and on a find record that means DECLARED ENGLISH

`NON_LATIN_SCRIPTS` in `ingest/fidelity.py` is a 22-entry tuple of Unicode
script-name prefixes: GREEK, CJK, HANGUL, ARABIC, TAMIL, ETHIOPIC, RUNIC,
DEVANAGARI, SYRIAC, HEBREW, OLD SOUTH ARABIAN, OLD NORTH ARABIAN, IMPERIAL
ARAMAIC, INSCRIPTIONAL PARTHIAN, INSCRIPTIONAL PAHLAVI, PSALTER PAHLAVI,
CUNEIFORM, BRAHMI, KHAROSHTHI, COPTIC, HIRAGANA, KATAKANA. **THAI IS NOT ON IT.**

Run on the bridge at `5b33934`, on a Thai sentence and a French one:

```
FR  non_latin_ratio = 0.00   classify_original(..., 'find_record') -> ('object_description', 'en', True)
TH  non_latin_ratio = 0.00   classify_original(..., 'find_record') -> ('object_description', 'en', True)
```

The French result is expected — `fr` is in `LATIN_SCRIPT_LANGS`. **The Thai result
is not**, and it is not caused by the language list at all: `non_latin_ratio`
scores a page of Thai script at **zero**, because `unicodedata.name` of a Thai
character begins `THAI ` and nothing in the tuple matches it. On a find record
`classify_original` reads `nl >= 0.30` before it reads anything else, so the
transliteration branch that rescues `seasia-06-kedukan-bukit` and
`seasia-07-talang-tuo` is never reached.

**This is FINDING 82's twin in the ORIGINAL field, and it is broader.** FINDING 82
hard-codes one language for every translation chunk; this one mis-detects a whole
class of scripts and then declares them English. Khmer, Burmese, Sinhala, Tibetan,
Javanese, Georgian, Armenian and Cyrillic are all absent from the tuple too.

**WHAT IT COST F7, TODAY.** The two best Southeast Asian institutional records
this session's search found are both Thai and both were refused:

```
archaeology.sac.or.th/archaeology/120        Phu Khao Thong (SAC, Ministry of Culture)
suvarnabhumi.psu.ac.th/tudb/archaeologicalread/76   Khlong Thom / Khuan Lukpad (PSU)
```

The Khlong Thom record was opened in the browser and its own keyword line reads
`ก่อนประวัติศาสตร์ตอนต้น โรมัน ราชวงศ์ฮั่น … ตราประทับกรีก-โรมัน` — early
prehistory, **Roman**, Han dynasty, **Greco-Roman seals** — with Roman gold coins
and Roman mosaic beads in the body. **It is the most explicitly Roman Southeast
Asian institutional text found anywhere in this pass, and it would have entered
the index declared English.** Both are recorded as **searched failures under
ruling 75** and neither is curated, which is the decision F6 took on the Turfan
Manichaean vein for FINDING 82's sake. The precedent is followed rather than
argued with.

**NOT FIXED HERE, and adding `"THAI"` to the tuple is the wrong shape of fix.**
The defect is that the test is an allowlist at all; a one-line addition closes the
case that was noticed and leaves the class open, which is FINDING 82's argument
one field to the left. It also touches what every existing record's original chunk
declares, so it is a piece of work and not a patch.

**And it sharpens debt item 5.** No line in `ingest.verify --state` reports
language concentration within a region — and now there is a second reason the
count would mislead: a region could acquire a record in a local modern language
and have it reported as English.

---

# RULING 79 — F7's five predictions, written before the first record is curated

**In FINDING 83's unit.** F6's P4 named a record and then measured a region, and
was refuted by a run that confirmed the mechanism it was right about. So every
prediction below is denominated in **`beaten_by`, which records chunk ids**, and
not in a region. Each names its own refutation. **None of these is a gate**; a
prediction that fails is read, recorded, and does not stop the tranche.

Baseline: `20260906T103920+0000-retrievable_chunks_with_distractors.json`,
**544 chunks, 44 pairs, `recall@6` 0.6818 (30/44), MRR@10 0.5469; units 0.7561
(31/41)**. A prediction about a record that does not land is void, not refuted.

## P1 — 拂菻 crowds 拂菻, for the third time

`cefu-yuangui-fulin-glass` sits at **rank 4**, having fallen 2 → 4 in the F6 run,
beaten there by two translation chunks of `eastasia-08-songshi-fulin` — the Song
History's account of Fulin crowding the Cefu Yuangui's, four hundred years apart.
`eastasia-09-jiutangshu-fulin` is a **third** account of Fulin, in English, naming
the same 643 embassy.

**PREDICTED: `cefu-yuangui-fulin-glass` falls again, and at least one chunk of
`eastasia-09-jiutangshu-fulin` is in its `beaten_by`.**
**REFUTED BY:** it holds at 4 or improves; or it falls with no `eastasia-09` chunk
in its window, which would say the fall is index growth and not subject
resemblance.

## P2 — a rank-1 pair falls to English prose about its own object

This is the experiment F6's P4 could not run. `au-ezana-titles` held at rank 1
with an **empty** `beaten_by` against four new records, and the record that
resembled it least was the one P4 was about. `au-oc-eo-medallion` also sits at
**rank 1**, expecting `seasia-01-oc-eo-medallion`; and `seasia-09-oceo-unesco` is
English prose naming the same site, the same excavation and *"Roman gold coins and
medals"* — the target's own object class, in the target's own language.

**PREDICTED: `au-oc-eo-medallion` leaves rank 1, and chunks of
`seasia-09-oceo-unesco` are in its `beaten_by`.**
**REFUTED BY:** it holds at 1 with an empty `beaten_by`, exactly as
`au-ezana-titles` did — which would say a rank-1 pair is defended by something
other than the absence of a resembling record, and that FINDING 79's resemblance
mechanism does not reach the top of the list.

## P3 — the gloss record crowds one pair and only one, and it is cross-regional

`persia-07-met-ewer-anahita` is a museum description of a Greek god's imagery read
onto an Iranian cult. The corpus holds exactly one pair whose target is the same
argument about a different object: `bronze-heracles-verethragna-from-mesene`
(rank 104, `persia-04-bronze-heracles`) — a Greek Heracles identified with the
Iranian Verethragna.

**PREDICTED: no `beaten_by` list in the run contains a chunk of
`persia-07-met-ewer-anahita` except where the target is
`persia-04-bronze-heracles`.**
**REFUTED BY:** it appears against any other target, or against none at all. Both
refutations are informative and they are different: the first says resemblance is
looser than this, the second says a 100-word object description cannot crowd
anything.

## P4 — five object descriptions crowd almost nothing; two prose records do the crowding

In the F6 run the two records that crowded anything were **long English prose**
(`africa-07`, 2,777 characters) and a **full bilingual record**
(`eastasia-08`); the short one appeared in exactly one `beaten_by` list in the
whole run.

**PREDICTED: at most two of F7's five `catalogue_record` chunks appear in any
`beaten_by` list in the run, and both `published_translation_only` records appear
in at least one each.**
**REFUTED BY:** three or more of the five catalogue records appear, or either
prose record appears in none.

*Not a prediction, a sanity check with a stated band:* the two translations are
long and will chunk into several each; the five object descriptions are short and
should chunk into one each. **The index should land between 556 and 566 chunks.**
Outside that band, something is wrong with the loader and not with the
prediction.

## P5 — FINDING 84's frame, said before the run and not after it

Every record-adding run in Block F has been monotone worse: 0 better / 9, then
0 better / 14. The only run with improvements is the one where 393 distractors
left the index.

**PREDICTED: `ALL recall@6` falls from 0.6818, and NO gold pair improves.**
**REFUTED BY:** any pair improving — which would be the first improvement Block F
has ever seen from adding a record, and would be worth more than the seven
records that produced it.

---

# CANDIDATES FOUND AND NOT TAKEN — ruling 75's shape, recorded now rather than at the close

1. **BnF `camée.360`, Shapur I and Valerian** —
   `medaillesetantiques.bnf.fr/…/ark:/12148/c33gbqh22`, an ARK permalink that
   opens. Sardonyx cameo, after 260 CE, Shapur seizing the Roman emperor by the
   wrist at Edessa, with the BnF's own commentary arguing it was carved by a Roman
   hand. **The single best Rome↔Persia object in existence and F7 refuses it.**
   Its description is French, and by FINDING 86 a French object description on a
   find record enters the index declared English exactly as a Thai one does. Its
   rights are `two_positions_stated` at best — `© BnF` on the record, Licence
   Ouverte/Etalab on the catalogue metadata. **Refused for an instrument reason
   and not a source reason**, which is the most expensive sentence in this
   document.
2. **The two Thai institutional records** — FINDING 86 above.
3. **`collections.louvre.fr`** — a bot challenge to a real browser and HTTP 429 to
   a fetcher, on 2026-09-06. The Bishapur mosaics, Roman work in a Sasanian palace,
   are behind it. **The second negative recorded against a named institution**,
   after `betamasaheft.eu`'s 403.
4. **The Pañcasiddhāntikā** — §2 above. Content confirmed, capture quality refused.
5. **The British Museum holds no Roman-connected Southeast Asian object its own
   search surfaces.** `Ban Don Ta Phet` → 0 results. `Funan` → 1 result, and it is
   a Shang/Western Zhou finial found in China. Searched in the browser, where BM
   search works; it does not work through a fetcher, which returns a stale default
   set for every keyword.
6. **The Victorinus coin from U Thong (AD 269–271) has no institutional record.**
   The U Thong National Museum's virtual museum lists thirteen highlight objects
   and every one is Buddhist or terracotta. The coin is published in journals only.
7. **The Pompeii "Lakshmi" ivory, MANN inv. 149425** — no per-object institutional
   record found; the museum exposes it only through a paginated gallery URL that is
   not a stable identifier.
8. **UNESCO Pyu Ancient Cities, ref 1444** — opened. Its Outstanding Universal
   Value text names trade with *"Southeast Asia, China and India"* and carries **no
   Mediterranean or Roman link at all**. Refused on content, and Myanmar remains a
   region of Southeast Asia this corpus holds nothing from.
9. **Hirth's extracts L (Xin Tangshu 221b) and I (Wei shu 102)** — on the same
   page as the one that is being taken, both readable, both refused because there
   is one East Asia slot and extract K carries the embassies.

---

# WHAT IS VERIFIED AND WHAT IS NOT

**Opened in a browser on 2026-09-06 and read:** BM 1898,0803.11 and its live DOM
searched for a Creative Commons marking; Met 67.10 and its gloss sentences read
verbatim; the Bangkok National Museum Pong Tuk record and its highlight index; the
U Thong highlight index; Cosmas Book XI on tertullian.org with its rights line;
the Silk Road Seattle Hirth page with its two rights statements and its
Chiu-t'ang-shu heading; the Pañcasiddhāntikā full text; the Khlong Thom record;
the BM searches for `Ban Don Ta Phet` and `Funan`; `collections.louvre.fr`'s bot
challenge.

**Read through a fetcher and not yet in a browser:** Walters 21.74's description
and CC0 line; the BM copyright-and-permissions page; UNESCO 6572 and 1444 and the
WHC disclaimer; Hirth's printed page numbers 51–56.

**Not established:** the Pong Tuk lamp's accession number and date, which the
museum does not print; whether the Arkenberg modernization changed anything in
extract K; and the verbatim wording of the Fine Arts Department's footer.

**NOTHING HAS BEEN CAPTURED YET.** Every excerpt above is quoted here to justify a
candidate. **Each one is re-typed on the bridge, sliced independently from the
live page in the browser, SHA-256'd on both machines and compared** before it
enters a record — F6's practice, seven spans across four records, about a minute
each, and it earned its keep twice on the day it was invented.
