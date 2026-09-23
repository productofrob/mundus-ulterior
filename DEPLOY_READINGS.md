# DEPLOY READINGS — the five bounded cells. **CONFIRMED BY ROB AND WRITTEN,
# 2026-09-22. See §7 for what the confirmation changed.**

*Read by the model on 2026-09-22 in Claude in Chrome. Nothing here is in
`data/corpus_rights.json` until Rob confirms it, and each cell is then signed
`curator_and_model`. The method is the rights validation block's: counts over the
full HTML and the rendered text, the object AND the site (FINDING 120), and
archive.org's injections excluded (RULING 95).*

---

# 0. RULING 96 MOVES THE CELL FOR FOUR OF THE FIVE

The rights target for all five was computed from `citation_original`. RULING 96
says the cell is for **the material the record's quoted text comes from**, and
for four of these records that is somewhere else:

```
record                       where the quoted text comes from     citation_original
---------------------------  -----------------------------------  ----------------------
eastasia-01-weilue           Hill's English, Silk Road Seattle    zh.wikisource (Chinese)
eastasia-02-hou-hanshu       Hill's English, Silk Road Seattle    zh.wikisource (Chinese)
scandinavia-03-vimose        en.wikipedia "Vimose inscriptions"   Kiel capture, Wayback
southasia-04-pattanam        en.wikipedia "Muziris"               KCHR PDF capture, Wayback
seasia-01-oc-eo-medallion    Borell's paper, academia.edu         the same -- unchanged
```

The two Chinese records follow the eastasia-08-songshi-fulin precedent RULING 96
names: two components from two hosts, and the cell is for the translation
because that is what the English quotes. The other component is quoted in the
note, which RULING 96 makes mandatory.

**None of the three `host_refuses` hosts refused on 2026-09-22.** zh.wikisource
and academia.edu both rendered in Claude in Chrome.

---

# 1. eastasia-01-weilue — PROPOSED `all_rights_reserved`

```
read_off        https://depts.washington.edu/silkroad/texts/weilue/weilue.html
stated          "Draft English translation by John E. Hill © September, 2004"
object counts   copyright 0 · © 1 · licen[cs]e 0 · creative commons 0 ·
                all rights reserved 0 · terms of use 0 · creativecommons anchors 0
```

**The site states more, on its own copyright page** (linked "Copyright" from the
root, https://depts.washington.edu/silkroad/), https://depts.washington.edu/silkroad/copyright.html:

> "Materials on the Silk Road Seattle web site are copyrighted by Silk Road
> Seattle or by the individual authors, photographers or museums. Much of the
> material is freely available for non-profit educational use, but note in
> particular the restrictions imposed by museums on any copying of their images
> without permission. [...] If you wish to download or copy materials for
> re-distribution and in particular for any profit-generating enterprise, you
> must request permission."

**Why `all_rights_reserved` and not `permission_stated_no_licence`.** The
permission is hedged ("Much of the material") and does not name this
translation, whose copyright the object states as Hill's own, and the page sends
other holders' permissions to "contact them directly". The bare copyright line
is the object's own statement, and the precedent (southasia-07, africa-01) reads
it as all rights reserved. **RULING 74's conditions apply in full.** The
quotation is 130 words, attributed. The redistribution sentence is a copyright
notice, not an agreement a reader clicks through. That is the difference from
PHI, and why RULING 98 does not reach it.

**Second component, for the note:** the Chinese, from
https://zh.wikisource.org/wiki/%E4%B8%89%E5%9C%8B%E5%BF%97/%E5%8D%B730. The page
holds the record's excerpt (大秦國一號犁靬 found). Footer:

> "本站的全部文字在知识共享 署名-相同方式共享 4.0协议之条款下提供，附加条款亦可能应用。"

A creativecommons anchor points to by-sa/4.0. 公有領域/公有领域 appears 0 times,
so there is no public-domain template on the page.

# 2. eastasia-02-hou-hanshu — PROPOSED `all_rights_reserved`

```
read_off        https://depts.washington.edu/silkroad/texts/hhshu/hou_han_shu.html
stated          "Translated by John E. Hill © September 2003"
object counts   copyright 0 · © 1 · licen[cs]e 0 · creative commons 0 ·
                all rights reserved 0 · terms of use 0 · creativecommons anchors 0
site            the same copyright page as §1
```

The reasoning is §1's. The quotation is 81 words.

**Second component, for the note:** https://zh.wikisource.org/zh-hans/%E5%BE%8C%E6%BC%A2%E6%9B%B8/%E5%8D%B788.
The footer text is identical to §1's. There is no creativecommons anchor on this
page, and 公有领域 appears 0 times. **The `zh-hans` URL serves the SIMPLIFIED
conversion**: the page reads 献 and 玳瑁 where the record holds 獻 and 瑇瑁.
The record's `original_text_note` already accounts for this.

# 3. seasia-01-oc-eo-medallion — PROPOSED `states_no_terms`, **ON CONDITION**

```
read_off        https://www.academia.edu/12682533/The_Power_of_Images_Coin_Portraits_of_Roman_Emperors_on_Jewellery_Pendants_in_Early_Southeast_Asia
object counts   copyright 2 · © 3 · all rights reserved 1 · licen[cs]e 0 (text) ·
                creative commons 0 · creativecommons anchors 0
```

**Every hit belongs to something other than the paper.** "© 2026 Academia. All
rights reserved" is the platform's footer. By RULING 95's reasoning the delivery
is not the source, and it is FINDING 121's shape: a signal that belongs to the
host rather than the work. "© Ecole francaise d'Extrême-Orient, fonds Vietnam
EFEO-VIE01835", and the other credits, are IMAGE credits for the paper's figures,
a component the record does not quote (RULING 96). They go in the note.

**The source is established, and it is this paper.** The rendered text holds the
record's legend and measurements: "Slightly corrupted legend ANTONINVS AVG PIVS
NVRP (or NVAP) XV", "Diameter: 19 mm. Thickness of the gold sheet 0.3 mm. Weight
1.4135 g. Gold, fineness: 916".

**THE CONDITION.** The rendered page does not name the journal the paper
appeared in, and the PDF's own first page was not opened, because downloading
it goes through the site's sign-up flow. If the published PDF carries a
publisher's statement, that statement is the position, not silence. **Rob opens
the PDF and checks its first and last pages before this is confirmed.**

# 4. scandinavia-03-vimose — PROPOSED `open_licence_stated`, CC BY-SA 4.0

```
read_off        https://en.wikipedia.org/wiki/Vimose_inscriptions
stated          "Text is available under the Creative Commons
                Attribution-ShareAlike 4.0 License; additional terms may apply."
last edited     17 March 2026, 08:12 UTC
```

**Source established:** the article carries the record's readings and glosses,
for example 'possibly "Mari (the famous one) is the sword of Alla"', 'awgns;
possibly "son/descendant of Awa"', "[w]agni[ŋ]o". The record's own
`translation_source` says "as summarized on Wikipedia".

**Second component, for the note, read under RULING 95:**

```
object capture   https://web.archive.org/web/20151122163034/http://www.runenprojekt.uni-kiel.de/abfragen/standard/deutung2.asp?findno=20&ort=Vimose&objekt=Kamm
                 rendered; "copyright" 2 in the HTML, BOTH in archive.org's
                 injected comment ("JAVASCRIPT APPENDED BY WAYBACK MACHINE,
                 COPYRIGHT INTERNET ARCHIVE ..."), excluded. The captured page
                 states nothing
root capture     https://web.archive.org/web/20151219231222/http://www.runenprojekt.uni-kiel.de/
                 renders a hit counter and "Letzte Aktualisierung: 04.03.2012";
                 the link set is five image links (beschreibung, abfragen,
                 kontakt, links, English). No rights statement
contact capture  20160306044941, returned no text. Not read
```

# 5. southasia-04-pattanam — PROPOSED `open_licence_stated`, CC BY-SA 4.0

```
read_off        https://en.wikipedia.org/wiki/Muziris
stated          the same footer sentence as §4
last edited     10 August 2026, 14:48 UTC
```

**Source established, near-verbatim:** the article reads "Mediterranean objects:
(100 BC to 400 AD) Amphora and terra sigillata shards; fragments of Roman glass
pillar bowls; and gaming counters", and the record reads "Mediterranean objects
(100 BC to 400 AD): Amphora and terra sigillata shards; fragments of Roman glass
pillar bowls; and gaming counters." The record's own note says "Summary drawn
from Wikipedia's synthesis of KCHR season reports".

**Second component, for the note:** the KCHR handbook capture,
https://web.archive.org/web/20160304031410/http://www.keralahistory.ac.in/pdf2013/pattanam_7th_season_handbook1.pdf,
**did not render.** The Wayback toolbar loaded over a blank frame. **Unread**, and
under RULING 95 it cannot be `states_no_terms`. It is the note's component, not
the cell's.

**A citation defect, separate from the rights:** `citation_original` names a
document the text was never taken from. The note promises to "pull the primary
KCHR 'Pattanam Seventh Season Handbook' ... during ingestion", and that was never
done. It is the eastasia-01 shape the rights block already recorded: a promise in
a field that nobody kept.

---

# 6. WHAT CC BY-SA ASKS OF THE PORTAL, FOR §4 AND §5

Attribution, and the license named where the adapted text is shown. The record
panels show `citation` (the Wikipedia URL). **Whether they also name the license
is checked at step 8's look**, not assumed here.

---

# 7. THE CONFIRMATION, 2026-09-22

```
record                      proposed                 confirmed
--------------------------  -----------------------  ---------------------------
eastasia-01-weilue          all_rights_reserved      all_rights_reserved
eastasia-02-hou-hanshu      all_rights_reserved      all_rights_reserved
seasia-01-oc-eo-medallion   states_no_terms, IF      all_rights_reserved -- the
                            the PDF says nothing     PDF carries a publisher line
scandinavia-03-vimose       open_licence_stated      open_licence_stated
southasia-04-pattanam       open_licence_stated      open_licence_stated
```

**One of five changed, and it changed on the condition written for it.** Rob
opened Borell's PDF and found:

> "© Kommission für Archäologie Außereuropäischer Kulturen des Deutschen
> Archäologischen Instituts, Bonn, 2014"

The PDF breaks the line after "Kulturen", and the cell closes that break up. **This
is FINDING 120's shape a second time.** The page's silence did not establish the
source's silence. This time the gap was named before the reading and closed by
the curator, rather than being found afterwards.

**Rob ruled the Wikipedia pair on the question of which page the cell describes**,
not on the license, which was never in doubt. He chose Wikipedia, the page the
records' words came from, over the archived pages `citation_original` names.

**All five are signed `curator_and_model`.** `check_rights` returns no problems
when it is run in the device VM. `python -m ingest.verify` on the host is Rob's.

```
the column after the five     open_licence_stated 13 · all_rights_reserved 15 ·
                              states_no_terms 7 · permission_stated_no_licence 5 ·
                              two_positions_stated 3 · public_domain 2 · unread 9
```

**`ui/data.js` is not regenerated for this edit.** The rights sidecar reaches no
content hash. The Methodology figures that count the column are rebuilt at step 8
with everything else, and until then they read 40 / 14.

---
---

# 8. THE NINE — WHERE EACH RECORD'S WORDS CAME FROM. **INVESTIGATED 2026-09-22,
# NOTHING WRITTEN**

*All nine were `source_not_established`: no `citation_original`, and a `citation`
pointing at an English Wikipedia article. Each record's quoted fields were
matched against the article it names, and against its revision history where
they did not match, in Claude in Chrome on 2026-09-22. Every article's footer
reads "Text is available under the Creative Commons Attribution-ShareAlike 4.0
License; additional terms may apply."*

**All nine sources are now established, and P1 fails in the flattering direction
it named.** Every one routes through Wikipedia. They differ in whose words
Wikipedia is carrying:

```
SHAPE 1 -- WIKIPEDIA'S OWN PROSE. Rob's Vimose/Pattanam ruling applies as it stands

scandinavia-05-thorsberg-chape  Thorsberg_chape, edited 24 Aug 2026. Glosses and
                                apparatus verbatim ('Wolthuthewaz is
                                well-renowned', 'the servant of Ullr, the
                                renowned', 'alliterative long-line')
seasia-02-oc-eo-site            Óc_Eo, edited 1 Aug 2026. 'pottery, tools,
                                jewelry', 'casts for making jewelry', 'Antonine
                                period'
scandinavia-04-illerup-adal     THE FIRST SENTENCE is from Roman_Iron_Age_weapon_
                                deposits (edited 14 Sep 2025), NOT from the
                                Illerup_Ådal article the citation names. THE
                                SECOND SENTENCE is on neither page, in any of the
                                last 15 revisions of either -- see below
arabia-02-palmyrene-tariff      Palmyra_Tariff, edited 8 May 2026. The record
                                QUOTES NO SOURCE TEXT (pointer_only). Its
                                descriptive fields follow the article, and the
                                Matthews sentence kept in `notes` is on it

SHAPE 2 -- A NAMED THIRD PARTY'S TEXT, SET OFF AS A QUOTATION ON WIKIPEDIA

arabia-03-jsnab17               JSNab_17, edited 8 Apr 2026. O'Connor's 1986
                                translation, introduced "This yields:". The
                                record simplifies its diacritics (Raqash for
                                Raqāsh, Mare 'Alma for Marē ʿAlma)
arabia-04-jabal-dabub           Jabal_Dabub_inscription, edited 3 Sep 2026.
                                Al-Jallad's revised reading and "In English:",
                                both footnoted [2]
seasia-04-dong-yen-chau         Đông_Yên_Châu_inscription, edited 29 Apr 2026.
                                "Transliteration[1]" and "English
                                translation[1]", Thurgood
seasia-07-talang-tuo            Talang_Tuo_inscription, edited 20 Jun 2025.
                                "Original Script[2]", and note 2 is "Old Malay
                                Corpus". sealang.net. THE RECORD'S OWN NOTE SAYS
                                THE ARTICLE "does NOT state whose transliteration
                                it prints", and it does. The page carries a
                                maintenance banner saying the section is a copy
                                of source text

SHAPE 3 -- UNATTRIBUTED ON WIKIPEDIA

seasia-06-kedukan-bukit         Kedukan_Bukit_inscription, edited 5 Aug 2026. The
                                transliteration table has no footnote; the
                                references name Guy, de Casparis, Acri, and
                                Coedès in a gloss note, but none of them against
                                the transliteration. It writes v where Talang
                                Tuo writes w (svasti/swasti, vulan/wulan), so the
                                two are not from one corpus
```

## Illerup's second sentence has a source, and its wording is closest to a
## machine summary

The record reads: "The deposit contains 194 Roman denarii, four barbarous
imitations, and a sestertius." It is on no Wikipedia page. The fact is in the
abstract of the paper "Roman coins from Illerup Ådal (Denmark)" on academia.edu,
https://www.academia.edu/39904493/Roman_coins_from_Illerup_%C3%85dal_Denmark_:

> "There are 194 denarii, Nero to Commodus, four barbarous imitation denarii and
> a sestertius of Antoninus Pius."

**The closest wording on that page is not the author's.** It is the platform's
"Key takeaways AI" box: "The Illerup Ådal deposit contains 194 denarii, four
barbarous imitations, and a sestertius". The record matches that line more
closely than the abstract. Nothing establishes which the record was taken from,
or when. **For the record pass, and not for the rights cell.**

---

# 9. RULINGS ON §8, AND THE CLAUSE-2 PUBLICATIONS READ, 2026-09-22

**Rob ruled on all three shapes**, and they are now RULING 99 in
`DEPLOY_RULINGS.md`. Five cells are written: the four in shape 1 and Kedukan
Bukit (shape 3), all `open_licence_stated`, CC BY-SA 4.0, signed
`curator_and_model`. `check_rights` returns no problems when it is run in the
device VM. **The column is now 18 / 15 / 7 / 5 / 3 / 2, and 4 unread.**

**The four shape-2 records, read against the publication each one quotes:**

```
arabia-03-jsnab17        O'Connor, "The Arabic Loanwords in Nabatean Aramaic",
                         JNES 45.3 (1986) 213-229
  object                 https://www.journals.uchicago.edu/doi/10.1086/373188
  states                 "Copyright 1986 The University of Chicago."
  site footer            "© 2025 The University of Chicago and other publishing
                         partners. All rights reserved, including rights for text
                         and data mining and training of artificial intelligence
                         technologies or similar technologies."
  PROPOSED               all_rights_reserved

arabia-04-jabal-dabub    Al-Jallad, "A pre-Islamic basmala", JSAI 52 (2022) 1-28
  object                 https://www.academia.edu/43388891 -- the link Wikipedia's
                         footnote [2] gives
  rendered page          states nothing of the article's own. The only lines are
                         the platform's footer, and the translation is not in the
                         rendered text
  journal site           https://jsai.huji.ac.il/ -- "©The Hebrew University of
                         Jerusalem. All Rights Reserved"
  PROPOSED               all_rights_reserved, ON CONDITION that Rob checks the
                         PDF's first and last pages, as he did for Borell

seasia-07-talang-tuo     Suhadi (1983), as displayed in SEAlang's Old Malay Corpus
  object                 http://sealang.net/oldmalay/display.pl?id=OM17&author=Suhadi&year=1983
                         -- Wikipedia's footnote [2] links exactly this. It holds
                         the record's text (niparwuat, jayanāga, pranidhānānda,
                         "śakawarṣātīta 606" all found) and states nothing
  site root              http://sealang.net/ -- "All results are freely available
                         for re-use under the Creative Commons open license." It
                         names no specific license
  the publication        SEAlang hosts Suhadi 1983 as a PDF, linked from
                         http://sealang.net/oldmalay/ as archives/suhadi1983seven.pdf.
                         Not opened: it is a PDF
  PROPOSED               read the PDF's statement (Rob), and failing one,
                         permission_stated_no_licence off SEAlang's root sentence

seasia-04-dong-yen-chau  Thurgood, From Ancient Cham to Modern Dialects (University
                         of Hawai'i Press, 1999), p. 3
  object                 a printed book. Google Books shows snippet view only,
                         https://books.google.co.uk/books?id=K4NkAAAAMAAJ, and the
                         copyright page could not be opened. No other online copy
                         was found
  PROPOSED               see the question put to Rob
```

---

# 10. THREE OF THE FOUR CONFIRMED, 2026-09-23

```
arabia-03-jsnab17        all_rights_reserved            O'Connor, "Copyright 1986
                                                        The University of Chicago."
arabia-04-jabal-dabub    states_no_terms                the page and its PDF state
                                                        nothing (the PDF checked by Rob)
seasia-07-talang-tuo     permission_stated_no_licence   SEAlang's root sentence;
                                                        Suhadi's PDF states nothing
                                                        (checked by Rob)
seasia-04-dong-yen-chau  UNREAD                         Rob is finding a copy of
                                                        Thurgood (1999)
```

**One proposal was withdrawn before Rob ruled, and the withdrawal is recorded.**
§9 proposed `all_rights_reserved` for Jabal Dabub off the JSAI website's footer.
The africa-01-ezana-stone precedent does not read a different host into a cell:
the article is served from academia.edu, not from jsai.huji.ac.il. The proposal
became `states_no_terms`, with the footer quoted in the note.

**The column is now 18 open / 16 all rights reserved / 8 states no terms / 6
permission / 3 two positions / 2 public domain, and 1 unread.**

**The one unread cell's reason is now wrong, and that is known.** `seasia-04`
still says `source_not_established`. Its source IS established (RULING 99 clause
2, Thurgood 1999). What is missing is the publication's own statement. It stays
as it is until Rob reports what the copy says, because a new `unread_reason` is a
schema change and may not be needed.
