# F4 candidates — the hunt, written down before any record is curated

*Two hunts, Sub-Saharan Africa and East Asia, run 2026-08-31 before record 31.
Recorded in full — including every disqualification and every source that
refused to load — because F3 established that a candidate discarded silently is
a hunt paid for twice, and because ruling 53 makes the SEARCH the evidence.*

*Ruling 53 required that a `verbatim_machine_english` record carry the failed
English search in its own notes, naming the sources consulted. This document is
where those searches live before they are copied onto records.*

---

# The headline: ruling 53's test returned a third answer

Ruling 53 pre-declared three outcomes. **The hunt produced a fourth, and it is
more useful than any of them.**

FINDING 41 said the tier cannot be targeted because a text worth curating is a
text somebody already translated. The East Asia hunt found the seam that claim
misses, and it is a structural one:

> **The nineteenth-century sinologists translated the DYNASTIC HISTORIES,
> because those were the prestige texts. The `huiyao`, the `leishu` and the
> geographical compendia — the Song-era compilations that preserve the
> administrative detail — were left alone.**

Hirth 1885 translates the Shiji, Hanshu, Hou Hanshu, Weilüe, Jinshu, Songshu,
Liangshu, Weishu, both Tang histories, the Songshi, the Mingshi, the Zhufan Zhi
and the Wenxian Tongkao. It does not translate the Tang Huiyao, the Cefu
Yuangui, the Taiping Huanyuji or the Lingwai Daida, and it never mentions the
last two. Checked against the book itself, not against a bibliography.

So `verbatim_machine_english` is not fed by obscurity, which is what FINDING 41
concluded and what makes the tier hopeless. **It is fed by GENRE.** That is a
property a curator can aim at, which is exactly what FINDING 41 said the tier
did not have — and it means the answer to ruling 53 is neither NARROWS nor
STANDS as those were written.

**The correction runs the other way too, and it is the part to be honest
about.** Two of the five East Asia candidates turned out to have English after
all: one in a 2020 monograph from an Italian academic press, one in a 1984
UNESCO series. And *The Roman Empire in Chinese Sources* (Leslie & Gardiner,
Rome 1996) is the standard translation-corpus of exactly this material, print
only, no digital copy — and nothing establishes whether it covers the three
strongest candidates. **The honest name for the tier is not "no published
English translation". It is "no English translation a curator can reach."**
That is decision 3 below, and it is FINDING 41's own sentence arriving from the
other side: the tier's real definition is not its written one.

---

# SUB-SAHARAN AFRICA

## The region's problem, stated first because it governs everything below

Africa is at **one** source-language record of four. Every strong candidate the
hunt produced is in **GREEK**.

```
Silko at Talmis                   Greek     LIST A
Monumentum Adulitanum II          Greek     LIST A
Sembrouthes at Daqqi Mahari       Greek     LIST A / disputed
the Dongola Creed                 Greek     LIST A, access-blocked
Qasr Ibrim epitaphs 43 and 56     Greek     LIST A, font-blocked
the Hamadab stela                 Meroitic  LIST B, and see below
```

`ingest.fidelity` counts a Greek record toward the per-region source-language
floor, and `africa-03-periplus-adulis` already is one. So four Greek records
would satisfy every check in this repository and leave Sub-Saharan Africa with
a source-language corpus written **entirely in the language of the empire the
project is measuring distance from.** No check can see that, and the project
instructions ask for *"relevant local, non-English sources from the regions
above."*

**The two local-language routes both fail, and they fail differently:**

**Ge'ez fails on the ROME criterion, not on translation.** Littmann's *Deutsche
Aksum-Expedition* IV (1913) is public domain, fully downloadable, prints the
inscriptions in original script with transliteration and **German translation
only** — the exact `verbatim_machine_english` profile. But its contents were
read through, and every text in it that touches Rome is either Ezana (which
this corpus already holds) or Sembrouthes. The Kaleb (RIÉ 191) and Wa'zeb
(RIÉ 192) inscriptions are not in Littmann; they are in the RIÉ, which is not
open, and the 2019 Drewes/Kropp edition is French and print-only. **This is
FINDING 38's supply problem, and it is ruling 53's third outcome — NEITHER —
arriving exactly where the third outcome was written to catch it.**

**Meroitic fails in a way nobody anticipated.** See decision 1.

## LIST A — source text and a reachable English translation

**A1. Silko, king of the Nobades, at Talmis (Kalabsha), c. 450 CE, Greek.**
Silko records victories over the Blemmyes in what had been the Roman
Dodecaschoenus, writing Greek in a Roman-period temple of Mandulis and styling
himself `βασιλίσκος` — the Greco-Roman diminutive used of client kings on the
empire's edge — and saying that God gave him the victory.
- Source text: PHI `epigraphy.packhum.org/text/219058` (OGIS 201). Clean,
  copyable Unicode Greek. PHI fetches without difficulty and is the best
  automated source in this region by a distance.
- English: *Fontes Historiae Nubiorum* III, entry 317, pp. 1147-1153, free PDF
  from the University of Bergen. **CAVEAT: the FHN III PDF is 54 MB and the
  hunt could only read its front matter. The entry number, page range and the
  presence of a Greek text plus English translation come from the table of
  contents, not from p. 1147.** A human opening the PDF settles it in a minute.

**A2. Monumentum Adulitanum II, the Adulis throne inscription, 3rd c. CE,
Greek.** An Aksumite king lists his conquests, records crossing the Red Sea
into Arabia, states that he made the trade roads safe by land and sea, and
dedicates the throne to **Ares**. Survives only because Cosmas Indicopleustes
copied it c. 520.
- Source text: PHI `epigraphy.packhum.org/text/219054` (OGIS 199), findspot
  given as Adoulis. This was the hunt's most useful single discovery: the Greek
  is otherwise only in Migne PG 88, whose host fails on an SSL error.
- English: McCrindle 1897, `tertullian.org/fathers/cosmas_02_book2.htm`,
  verified to carry the throne inscriptions.
- **Curatorial flag: the corpus already holds `africa-03-periplus-adulis`.**
  Different text, different author, different genre, same place.

**A3. Sembrouthes at Daqqi Mahari, Eritrea, Greek.** An Aksumite king calls
himself `βασιλεὺς ἐκ βασιλέων Ἀξουμειτῶν` in Greek and — on PHI's reading —
dates the act by `ιʹ ἰνδικτίονος`, the tenth **indiction**: the Roman and
Byzantine fiscal cycle on an African monument.
- Source text: PHI `epigraphy.packhum.org/text/223431` (SEG 24:1247), eight
  lines, clean.
- English: **this is the FINDING 41 case in its purest form.** Every scholarly
  edition is German (Littmann 1907, *Klio* 1961) or French (RIÉ 275) and none
  is open. The only freely reachable English is **on English Wikipedia**, after
  Munro-Hay. Searched and empty: Google Scholar, JSTOR open content,
  archive.org full-text search, *Aethiopica*, the ItyoPis survey of Aksumite
  epigraphy, Beta maṣāḥǝft.
- **Read this beside F3's two Old Malay records.** They qualified as
  `verbatim_machine_english` because a Wikipedia editor did not say whose
  English he was printing. Sembrouthes is disqualified from that same tier
  because a Wikipedia editor did say. **The tier turned on the same website
  twice, in opposite directions, and neither time on a fact about the text.**

**A4. The Constantinopolitan Creed at Old Dongola, 11th-12th c., Greek.** The
creed of an imperial council held at Constantinople in 381, inscribed in Greek
on a Nubian monastery wall — religion arriving from the empire in the most
literal available form. Łajtar in *Dongola 2015-2016*, with diplomatic
transcript and English translation.
- **Access: academia.edu, login wall for the PDF.** No open PCMA copy found.

**A5. Qasr Ibrim Greek epitaphs 43 and 56, 10th-12th c.** Nubian Christians
commemorated with Byzantine court titles carried into the Nubian state — no. 43
a `hypatos`, the title descended from the Roman consulate. Łajtar & van der
Vliet 2010, free PDF, Greek and English side by side.
- **Access: the Greek in that PDF does not extract as Unicode.** The font is a
  non-Unicode Greek encoding and the text comes back as mojibake. A verbatim
  capture needs OCR or a manual transcription — which is a cost, and under
  ruling 46 a cost that has to be timed rather than absorbed.

## LIST B — and the reason it is one item long

**B1. The Hamadab stela of Amanirenas and Akinidad, late 1st c. BC, Meroitic.**
BM EA1650, excavated at Hamadab south of Meroe in 1914; 42-45 lines of Meroitic
cursive; shows the queen and prince of the Roman war of 25-21 BC with a relief
of bound prisoners. **The British Museum's own record states that the word
`Areme` is thought to represent Rome**, and that the inscription may document
the Kushite raid on Roman Egypt of 24 BC.
- Source text: transliteration in *Fontes Historiae Nubiorum* II, entry 176,
  p. 719 (same caveat as A1: front matter only was readable). Also REM, on
  Persée, which **disallows automated fetching and holds page images rather
  than text**.
- English: **none exists, and four independent authorities say so on the
  record** — the British Museum object record ("remains undeciphered"), the FHN
  editors ("no consecutive translations can be provided"), Rilly in the UCLA
  Encyclopedia of Egyptology ("no more than a hundred words can be translated
  with some certainty"), and a 2025 ACL decipherment paper.
- **This is the strongest provenance story for an untranslated text that this
  project has ever found, and it is probably unusable. See decision 1.**

Also examined and not recommended: the Dakka inscription of Teriteqas,
Amanirenas and Akinidad (FHN II 173 — same untranslatability, weaker Rome
hook); the Kharamadoye inscription at Kalabsha, REM 0094 (Millet published an
English attempt in the *Meroitic Newsletter* 1973, and the Newsletter's own
open archive is unreachable by automation — an HTTPS-to-HTTP redirect loop —
so the disqualification could not be confirmed either way).

**The Polish Nubiological route, which F4_START did not name but which looked
obvious, is a dead end for this tier for a reason worth recording: Polish
Nubiology publishes in ENGLISH.** Łajtar, van der Vliet, Ochała and van Gerven
Oei all edit Nubian texts with English translations, and most of it is open
access. Everything found on that route belongs in LIST A.

---

# EAST ASIA

## LIST A — source text and a reachable English translation

**A1. Xin Tangshu 新唐書 221下, the Fulin entry, 1060 CE, `lzh`.** Opens by
identifying Byzantium with Rome outright — 拂菻，古大秦也 — then describes
Constantinople's walls, a water-clock with twelve balls, the twelve nobles who
govern jointly, deposition of the king after natural disasters, surgeons who
open the skull, and three dated embassies including King Boduoli's of 643 with
red glass.
- Source text: `zh.wikisource.org/wiki/新唐書/卷221下`, read in full.
- English: Hirth 1885 p. 56.
- **Access: `zh.wikisource.org` refused about fifteen other pages in the same
  session** ("cache-only and cannot be fetched") and served exactly two. Mirror
  anything taken from it at ingest rather than relying on a second fetch.

**A2. Liangshu 梁書 54, the Da Qin merchant Qin Lun 秦論, 635 CE, `lzh`,
recording 226 CE.** The most concrete Roman-person-in-East-Asia record in the
Chinese corpus: a merchant from Da Qin reaches Jiaozhi, is sent on to Sun Quan,
is questioned about the customs of his country, is shown captured short-statured
people from Danyang and says 大秦希見此人 — "Da Qin rarely sees such people" —
and is sent home with an escort who dies on the road.
- Source text: Kanripo, `raw.githubusercontent.com/kanripo/KR2a0018/master/
  KR2a0018_054.txt`, CC BY-SA 4.0, read in full.
- English: Hirth 1885, Liangshu section at p. 46; the episode is summarised in
  his introduction at p. 16. **The body of p. 46 was not read — the archive.org
  fetch truncated. Verify the wording before publishing.**

**A3. Weishu 魏書 102, the Da Qin entry, 554 CE, `lzh`.** Da Qin's capital at
Antu (Antioch), the royal city divided into five walled quarters, eight
ministers to each, and a conciliar procedure: when business cannot be decided,
the ministers of the four cities assemble at the king's, he hears it himself,
and only then is it carried out.
- Source text: Kanripo `KR2a0020_102.txt`, read in full.
- English: Hirth 1885, in the sequence between the Songshu and the Tang
  histories, roughly pp. 47-50; the page was not individually confirmed.

**A4. The Da Qin Jingjiao stele 大秦景教流行中國碑, Xi'an, 781 CE.** Banked in
F3 for F4, and the hunt improves the sourcing considerably. **James Legge, *The
Nestorian Monument of Hsî-an Fû* (1888), public domain on archive.org, prints
the Chinese text alongside the English translation and notes** — one open
volume for both halves of the record, which removes F3's assumption that this
one would cost a human pass at parsigdatabase.
- `archive.org/stream/nestorianmonumen00legg/nestorianmonumen00legg_djvu.txt`,
  read: Alopen 阿羅本 arrives from 大秦國 in the ninth year of Zhenguan (635).
- **Note against F3's banked entry:** F3 recorded this as a Middle Persian and
  Syriac record to be taken from parsigdatabase, region assigned by findspot.
  Legge gives the Chinese face and its English in a single open citation. The
  Syriac colophon is a separate question and a separate cost.
- **Access: `zh.wikisource.org/wiki/大秦景教流行中國碑` and the English
  Wikisource page both failed. ctext.org returns 403 on every text page.**

**A5. Tongdian 通典 193, including the surviving fragments of Du Huan's
Jingxingji 經行記, 801 CE, `lzh`.** Du Huan was taken prisoner at Talas, lived
in the Abbasid Caliphate and wrote up his return in 762; his book survives only
as quotations here. The juan also records murals at He 何國 showing the kings of
Persia and Fulin: 西壁則畫波斯拂菻諸國王.
- Source text: Kanripo `KR2m0001_198.txt` — **note the file-number offset, file
  `_198` is juan 193.** Read in full.
- English: Yule, *Cathay and the Way Thither* I (1866), Preliminary Essay §II
  "Chinese Knowledge of the Roman Empire". **The section was confirmed from the
  table of contents; Yule's actual rendering was not read.**
- **This was a LIST B candidate until Yule surfaced. Recorded as a
  disqualification, per ruling 53.**

## LIST B — the genre seam

**B1. Tang Huiyao 唐會要 99, 拂菻國, 961 CE, `lzh`.** An institutional
compendium built from Tang court archives, textually independent of the two
Tang histories at points: Fulin lies north of the Western Sea, ten thousand li,
four hundred walled cities, palace pillars of rock-crystal and glass; the
twelve joint ministers; election and deposition by merit and after portents;
the water-driven palace cooling and the mechanical timepiece; and the 643
embassy of King Boduoli with red glass.
- Source text: `zh.wikisource.org/wiki/唐會要/卷099`, read in full.
- English: **none found.** Not in Hirth 1885 (checked against the book's own
  contents). Not on Fordham's Internet East Asian History Sourcebook, Silk Road
  Seattle, silkroadfoundation.org or silk-road.com. Empty on archive.org
  full-text search, HathiTrust, Cambridge Core, ScienceDirect, DOAJ,
  eScholarship, academia.edu, ResearchGate, Google Books. chinaknowledge.de's
  page for the text lists no translation.

**B2. Cefu Yuangui 冊府元龜 970, 外臣部・朝貢, 1013 CE, `lzh`.** A
thousand-juan imperial compendium built directly from Tang court records — its
embassy notices are the closest thing to an archival register this project can
reach. Two dated Byzantine entries, and the first names the gift:
拂菻王波多力遣使獻赤頗黎、綠頗黎、石綠、金精等物 — the Fulin king Boduoli sent
envoys presenting red glass, green glass, malachite and gold-essence, in
Zhenguan 17 (643).
- **This is the strongest East Asia candidate in either list.** The corpus
  already holds Roman and Byzantine glass as archaeology
  (`eastasia-03-hwangnam-glass`, `scandinavia-*`, the Oc Eo material). This is
  the same substance arriving as a dated diplomatic gift, named in a Chinese
  archival register. Text and object, in two records, about one thing.
- Source text: Kanripo `KR3k0013_970.txt`, read in full.
- English: **none found**, same battery as B1.
- **Access note against F4_START's suggested route: `zh.wikisource.org/wiki/
  冊府元龜` is an EMPTY SHELL** — a table of the 31 部 headings and the notice
  此文档未完成，一部分的原作内容还未录入. Kanripo is the only reachable full text.

**B3. Taiping Huanyuji 太平寰宇記 184, 大秦國, c. 980 CE, `lzh`.** Northern Song
imperial geography, notable for welding the Han-era name 大秦/犁靬 to the
Tang-era 拂菻 in one lemma — a compact statement of the Chinese identification
of Rome with Byzantium.
- Source text: Kanripo `KR2k0004_184.txt`, read in full.
- English: **none found**, same battery.
- **Curatorial warning: much of the entry is a recension of the Hou Hanshu Da
  Qin account, which this corpus already holds** as
  `eastasia-02-hou-hanshu`. Its value is as a Song reworking with the Fulin
  equation added, not as new testimony. A weak add on content grounds even
  though it is a clean add on tier grounds — which is worth noticing, because
  the tier is what is short.

**B4. Lingwai Daida 嶺外代答 3, 大秦國, 1178 CE, `lzh` — a documented partial
disqualification.** Not the antiquarian Da Qin of the dynastic histories but a
live twelfth-century merchant report: a walled capital whose ruler wears a
gold-lettered turban, is rarely seen by his people, goes out every seventh day
through a mile-long underground passage to worship, sends annual tribute to the
素丹 (sultan) of the Arabs and calls on Arab troops in emergencies; products
include glass, coral, native gold, brocade, red carnelian and pearls; and there
is holy water that stills a storm at sea when sprinkled from a glass bottle.
- Source text: Kanripo `KR2k0116_003.txt`, read in full.
- **English EXISTS and is not reachable:** Victoria Almonte, *The Historical
  Value of the Work Lingwai Daida by Zhou Qufei* (Aracne, 2020), whose contents
  list includes "Section 39. Daqin guo. The country of Daqin. The Eastern Roman
  or Byzantine Empire." The publisher's preview PDF confirms the heading and
  stops before the chapter. Not open access. The older scholarly translation is
  German (Netolitzky 1977).
- **And a subtler problem:** the near-identical entry in the Zhufan Zhi IS in
  free English (Hirth & Rockhill 1911, ch. 20 "Baghdad (Ta-ts'in)"), so a
  reader can already get most of this content in English under another text's
  name.
- **This is decision 3 in one record.**

**B5. Hyecho 慧超, 往五天竺國傳, on 大拂臨國, composed 727 CE — the Korea
record.** The earliest overseas travelogue by a Korean, by a monk of Silla,
surviving in one Dunhuang manuscript (Pelliot chinois 3532). A Korean
eyewitness report of Byzantium resisting the Arabs: 此王兵馬強多，不屬餘國。
大寔數迴討擊不得 — "this king's troops and horses are strong and numerous; he is
subject to no other country; the Arabs have attacked repeatedly and could not
take it."
- Source text: CBETA TEI-P5, `raw.githubusercontent.com/cbeta-org/xml-p5/
  master/T/T51/T51n2089.xml`, read. The human-facing CBETA reader is
  JavaScript-only and returns nothing to a fetcher; `tripitaka.cbeta.org`
  404s, and the Wikipedia article still cites that dead URL.
- **English exists; reachability unresolved.** Yang Han-sung et al., *The Hye
  Ch'o Diary*, UNESCO Collection of Representative Works, 1984. There is a
  UNESDOC record at `unesdoc.unesco.org/ark:/48223/pf0000220391`, which would
  normally mean open access, but the page is JavaScript-rendered and the
  conventional direct-PDF path returned nothing. **One click in a browser
  settles whether Korea gets a LIST A record or a LIST B one.**

## Disqualifications, recorded so they are not re-hunted

- **Tongdian / Du Huan** — Yule 1866 translates it. Moved to LIST A.
- **Zhufan Zhi 諸蕃志** — Hirth & Rockhill 1911, free. **Also fails the window:**
  c. 1225, twenty years past 1204.
- **Songshi 宋史 490** — Hirth 1885 p. 62. **Also fails the window as a TEXT:**
  compiled 1345, though its content (the 1081 and 1091 embassies of Michael VII
  Doukas) is inside it. Whichever way that ambiguity is resolved, it is a
  LIST A record and not a LIST B one.
- **Jiu Tangshu 舊唐書 198** — English confirmed at Hirth p. 51; the source text
  was unreachable from every route tried, including a truncated Kanripo
  repository whose `_198` 404s. Trivial for a human on ctext or Wikisource.
- **Japanese Roman-glass excavation reports** — the strongest untapped seam for
  Japan and genuinely Japanese-only. The Utsukushi No. 1 tumulus at Nagaokakyō
  yielded layered glass beads identified as Roman manufacture, and its report
  is a Japanese-only PDF — behind an HTTPS-to-HTTP redirect loop that no
  fetcher gets through. `sitereports.nabunken.go.jp` holds 41,490 open PDFs and
  its record pages load, but its search endpoint is robots-disallowed. **A hand
  route, and a real one for F6.**

---

# Sources that refuse automation, for the cost column

Ruling 46 wants curation cost per tier. This is where it comes from.

```
CLEAN, no difficulty
  epigraphy.packhum.org        Greek from Nubia, Aksum, Adulis. The best
                               automated source in the Africa region by far.
  raw.githubusercontent.com/kanripo/     ~9,350 classical Chinese texts, UTF-8,
                               CC BY-SA 4.0. The breakthrough of the East Asia
                               hunt: kanripo.org itself returns 525.
  raw.githubusercontent.com/cbeta-org/   the Taisho canon as TEI-P5 XML.
  archive.org _djvu.txt        public-domain translations, but LONG BOOKS
                               TRUNCATE — front matter and TOC arrive, body
                               text deep in the volume often does not.

REFUSES OR DEGRADES
  ctext.org                    403 on every text page; api robots-disallowed
  zh.wikisource.org            "cache-only"; 2 of ~17 pages served
  db.history.go.kr             robots-disallowed (the Korean NIKH databases)
  persee.fr                    robots-disallowed; REM is page images anyway
  betamasaheft, dasi.cnr.it, trismegistos, shidianguji   robots or bot-challenge
  meroiticnewsletter.org, ityopis.org, nagaokakyo-maibun.or.jp
                               HTTPS->HTTP redirect loops
  documentacatholicaomnia.eu   SSL certificate failure (Migne PG 88)
  academia.edu                 login wall
  digitalt.uib.no FHN PDFs     40-54 MB, front matter only
  taubenschlagfoundation.pl    non-Unicode Greek font, extracts as mojibake
  daizhige GitHub mirror       GB2312, returns as binary
```

**A note that belongs in the cost column rather than here: two of the
strongest LIST A candidates need a human transcription pass** — Qasr Ibrim for
the font, and anything from the Bergen FHN PDFs for the size. That is the same
budget line F3 opened for parsigdatabase, and it is now two regions wide.

---

# What has to be decided before curation

**1. Meroitic.** The Hamadab stela has the best "no English exists" evidence
this project will ever see, and the reason is that **Meroitic is read but not
understood** — no continuous translation exists in ANY language. A
`verbatim_machine_english` record is one where the pipeline machine-translates
the source. No machine translates Meroitic. The tier exists to turn on the
machine-translation path; this record would turn it on and produce fluent
nonsense, attached to a citation, which is precisely the output the gloss arm
exists to catch.

**2. Greek.** Every reachable Africa candidate is Greek. Four Greek records
would satisfy the per-region source-language floor and every other check, and
leave the region's source-language corpus written entirely in the language of
the empire.

**3. "No published English" versus "no English a curator can reach."** B4 has
an English translation in a 2020 monograph from an Italian academic press. B5
has one in a 1984 UNESCO series whose open-access status could not be
established. B1-B3 may or may not be in Leslie & Gardiner 1996, print only, and
**nothing available to this project can establish which** — which is FINDING
41's own argument, arriving from the other side.
