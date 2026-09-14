# RIGHTS VALIDATION — BROWSER PASS 4, AND TWENTY-FOUR PROPOSED CELLS AWAITING
# CONFIRMATION. **NOTHING IS WRITTEN. `data/corpus_rights.json` IS UNTOUCHED AND
# ALL THIRTY-EIGHT CELLS STILL READ `unread`.**
#
# **Four records say something in their own prose that the object flatly does not
# say, and two more say something the object does not contain. The largest single
# outcome of the pass is `states_no_terms` — eight objects reached, each of which
# states nothing at all.**

*Run 2026-09-14. Rob's scope for the block: all of bucket A and bucket B, and
nothing signed without him. Every cell below is a PROPOSAL. On his confirmation
each is written with `read_by: "curator_and_model"`; anything he does not confirm
stays `unread`.*

---

# 0. INSTRUMENTS, BECAUSE THE CLAIM IS ABOUT WHAT A BROWSER SEES

Two browsers were used and which one read which page is part of each reading.

```
CLAUDE IN CHROME        20 of the 24 readings
  the extension in Rob's own Chrome

THE DESKTOP APP'S       4 readings -- epigraphy.packhum.org x2,
BROWSER PANE              en.natmus.dk x2
  Chrome refused both domains outright ("Navigation to this domain is not
  allowed"), so they were opened in the app's own pane after Rob granted
  each site. Same practice as F6_BROWSER_PASS2, declared for the same reason.
```

**METHOD, DECLARED IN FULL because it is more than "a person looked at a page".**
Each rights target was opened, and the rendered document was then interrogated in
the page's own context for the signals `southasia-07-bm-claudius-aureus` set the
precedent for: occurrences of `Creative Commons`, `CC BY`, `CC0`, `copyright`,
`©` and `all rights reserved` **in the full HTML and not only the visible text**;
every `<a>` or `<link rel="license">`; every anchor whose href contains
`creativecommons`; `dcterms`/`rights` metadata; and the footer's text. Where a
count was non-zero the surrounding text was pulled and read. **Counts are
reported below for every `states_no_terms` cell, because that position is a claim
that nothing is there and a claim of absence has to show its search.**

**F6_RULINGS' consequence applies and is the reason for the shape of this
document.** The session that supplied these captures is not an independent check
on them. That is what Rob's confirmation pass is for, and it is why `read_by` is
proposed as `curator_and_model` and not `model`.

---

# 1. THE FOUR CONTRADICTIONS, FIRST, BECAUSE THEY ARE WHAT THE BLOCK IS FOR

## 1A. The three Kanripo records. **"Licence: CC BY-SA 4.0." The file says nothing.**

`eastasia-05-liangshu-qin-lun`, `eastasia-06-cefu-yuangui`,
`eastasia-07-tang-huiyao` each carry `Licence: CC BY-SA 4.0.` in
`citation_original`. Each cites a `raw.githubusercontent.com` path into a Kanripo
repository. **A raw path serves a file, not a page.** All three were opened and
searched:

```
KR2a0018_054.txt   19,300 chars   creative commons 0   CC BY 0   licen[cs]e 0
KR3k0013_970.txt    8,107 chars   creative commons 0   CC BY 0   licen[cs]e 0
KR2m0002_099.txt    9,718 chars   creative commons 0   CC BY 0   licen[cs]e 0
```

Every one begins with the same five-line mandoku header — mode line, title, date,
`ID`, `BASEEDITION`, `JUAN` — and then the text. **There is no rights sentence in
any of the three, anywhere in the file.**

**The licence is not false about Kanripo; it is absent from the object.** It lives
in a LICENSE file in the repository, which is a different object, and the record
quotes the file. That is FINDING 87 arriving through a door nobody had watched:
not a policy page standing in for an object page, but a *repository* standing in
for a *file*.

**PROPOSED: `states_no_terms` x3.** The objects were reached, they say nothing,
and under RULING 74 the record says THAT.

## 1B. `eastasia-04-jingjiao-stele`. **"Licence: CBETA, CC BY-NC-SA." It is not a licence.**

The CBETA TEI file was opened and searched: **`creative commons` 0, `CC BY` 0,
the word `licen[cs]e` 0.** What the file does carry, in its own `<publicationStmt>`,
is this:

> **"Available for non-commercial use when distributed with this header intact."**

**PROPOSED: `permission_stated_no_licence`.** The object states, in its own words,
what may be done with its content and names no licence — the seventh position,
exactly as the vocabulary defines it. The record's prose names a Creative Commons
licence that does not appear in the file at all.

**And the CBETA/Kanripo split the start document's own correction predicted is
real**, in a sharper form than expected: one of the four states terms in its
header and three state nothing, and the one that states terms does not state a
licence.

## 1C. `southasia-05-brihatsamhita`. **The quoted sentence is not on the object.**

`citation_original` records that wisdomlib "states that it is 'free to read
online' and offers nothing further." The object page was reached — after a
Cloudflare interstitial that resolved on its own, no challenge answered — and
searched:

```
htmlLen 45,700   copyright 0   © 0   licen[cs]e 0   creative commons 0
"free to read" 0   "terms of use" 0   "all rights reserved" 0
footer links: About | Contact | contact form | privacy policy
```

**PROPOSED: `states_no_terms`.** The record's characterisation of the site is
right in substance — no licence — and the sentence it quotes is not on the page
the record cites. That is a small thing and it is the exact species of small
thing that FINDING 69 was made of.

## 1D. `persia-05-abnun`. **The rights target is a policy page. The object has its own line.**

The record's `citation_original` contains `https://uci.edu/copyright/`, so the
computed rights target is the university's copyright page. Both were read.

```
uci.edu/copyright/
  "Copyright © 2005-2025 The Regents of the University of California.
   All rights reserved."

sites.uci.edu/sasanika/abnun-inscription/   <- THE OBJECT
  "Privacy Notice | © 2026 UC Regents"
  copyright 2   © 1   licen[cs]e 0   creative commons 0
```

**They agree, and the reading is still the object's and not the policy's.** The
proposed cell is read off the Sasanika page.

**AND THE CITATION DEFECT STANDS AND IS NOT FIXED HERE.** A record whose
`citation_original` resolves to a university copyright page rather than to the
text is a citation problem, §5 puts record edits out of this thread's scope, and
it is raised for its own decision.

---

# 2. THE TWENTY-FOUR PROPOSED CELLS

Every quotation below was read off the URL in the same row, on 2026-09-14.
`read_by` is proposed as `curator_and_model` throughout and is valid only on
Rob's confirmation.

## BUCKET A — britishmuseum.org, 3 records

**All three carry one line and nothing else.** Searched exactly as
`southasia-07-bm-claudius-aureus` was: `creative commons` 0, `CC BY` 0, `CC0` 0,
anchors containing `creativecommons` 0, in the full HTML of each.

```
africa-02-aksumite-coin   britishmuseum.org/collection/object/C_1915-0108-81
persia-02-silver-plate    britishmuseum.org/collection/object/W_1908-1118-1
persia-03-coin            britishmuseum.org/collection/object/C_1843-0620-5

  all three        position   all_rights_reserved
                   verbatim   "© 2026 The Trustees of the British Museum"
```

**AND THE ONE THING THE THREE READINGS DID TURN UP.** The object page's "Use this
image" control does not open a panel — it navigates to a DIFFERENT URL,
`britishmuseum.org/collection/image/597606001`, which states:

> *"© The Trustees of the British Museum. Shared under a Creative Commons
> Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
> licence."*

**That is a third object and it is not this record's.** The corpus quotes the
catalogue description, which sits on the object page under the reserved-rights
line. The image page is recorded here so that nobody finds it later and thinks
the cell was read carelessly — and because it is the Walters case inverted: an
adjacent page carrying an open licence over material the corpus does not take.

## BUCKET B — 21 records, 13 hosts

### el.wikisource.org — ONE OBJECT, THREE RECORDS

`africa-03-periplus-adulis`, `arabia-01-periplus`, `southasia-02-periplus-muziris`
all cite the same page.

```
read_off   el.wikisource.org/wiki/Περίπλους_της_Ερυθράς_Θαλάσσης
position   open_licence_stated
licence    Creative Commons Αναφορά Δημιουργού-Παρόμοια Διανομή 4.0 (CC BY-SA 4.0)
rel=license anchor  creativecommons.org/licenses/by-sa/4.0/deed.el
```

> **"Όλα τα κείμενα είναι διαθέσιμα υπό την Άδεια Creative Commons Αναφορά
> Δημιουργού-Παρόμοια Διανομή 4.0· μπορεί να ισχύουν πρόσθετοι όροι. Δείτε τους
> Όρους Χρήσης για λεπτομέρειες."**

**The page was searched for a public-domain banner and there is none** — zero
matches for `public domain`, `κοινό κτήμα` or any PD template on the rendered
page. **So the three records' own prose — "(ed. C. Müller … Paris 1855; public
domain)" — is a true statement about the EDITION and not the position the page
states.** §2E called this line the wrong shape for a rights cell and it is: the
object states a licence, and the 1855 edition's public-domain status is a separate
fact that belongs where it already is, in `citation_original`.

**Three cells, one reading, and that is stated rather than left to look like
three independent verifications** — the practice `scandinavia-07-rycksta-grikkium`
established.

### raw.githubusercontent.com — 4 records

Covered in §1A and §1B.

```
eastasia-04-jingjiao-stele     permission_stated_no_licence
   read_off  raw.githubusercontent.com/cbeta-org/xml-p5/master/T/T54/T54n2144.xml
   verbatim  "Available for non-commercial use when distributed with this
              header intact."
eastasia-05-liangshu-qin-lun   states_no_terms
   read_off  raw.githubusercontent.com/kanripo/KR2a0018/master/KR2a0018_054.txt
eastasia-06-cefu-yuangui       states_no_terms
   read_off  raw.githubusercontent.com/kanripo/KR3k0013/master/KR3k0013_970.txt
eastasia-07-tang-huiyao        states_no_terms
   read_off  raw.githubusercontent.com/kanripo/KR2m0002/master/KR2m0002_099.txt
```

### epigraphy.packhum.org — 2 records

```
africa-04-silko-talmis    epigraphy.packhum.org/text/219058   OGIS 201
africa-05-adulis-throne   epigraphy.packhum.org/text/219054   OGIS 199

  both      position   states_no_terms
            searched   copyright 0 · © 0 · licen[cs]e 0 · creative commons 0 ·
                       "all rights reserved" 0 · "terms of use" 0 ·
                       creativecommons anchors 0
            links on the page: Regions, OGIS, Search Help, Contact Us,
                       All Regions, By Reference, Bibliography — no terms page
```

**PHI Greek Inscriptions states nothing about rights anywhere reached.** Read in
the desktop app's browser pane; Chrome refused the domain.

### parthiansources.com — 2 records

```
persia-01-skz              parthiansources.com/texts/skz/
persia-04-bronze-heracles  parthiansources.com/texts/bhm/bhm-parthian-text/
                           (the record's http:// URL redirects to https://)

  both      position   all_rights_reserved
            verbatim   "Parthian Sources Online All rights reserved."
```

**Read on each page separately and not inherited from the first.** The sentence
is the site footer's, printed identically on both; **there is no `©` character on
either page**, and the string is quoted exactly as it renders.

### en.natmus.dk — 2 records

```
scandinavia-01-hoby-treasure  .../the-early-iron-age/the-chieftains-grave-from-hoby/
scandinavia-02-gudme-hoard    .../gudme-gold-gods-and-people/the-roman-connection/

  both      position   states_no_terms
            in the rendered document, EXCLUDING HTML COMMENTS:
                       copyright 0 · © 0 · licen[cs]e 0 · creative commons 0
            footer: address, phone, privacy policy, organisation, shop,
                       research links. No copyright line, no terms page.
```

**AND THE REASON THE COUNT IS GIVEN TWICE.** Counting the raw HTML returns
`copyright 2, licence 1` on both pages, from the TYPO3 boilerplate comment:
*"TYPO3 is a free open source Content Management Framework … licensed under
GNU/GPL. TYPO3 is copyright 1998-2019 of Kasper Skaarhoj."* **That is the content
management system's licence, not the museum's position on its text**, and it is
precisely the sentence an automated matcher would hand back as a finding. Read in
the desktop app's browser pane; Chrome refused the domain.

### en.protothema.gr — 1 record

```
africa-01-ezana-stone
  read_off   en.protothema.gr/2021/09/08/the-ezana-stone-of-aksum-a-trilingual-
             monument-similar-to-the-rosetta-stone/
             (the record's URL redirects to this dated path)
  position   all_rights_reserved
  verbatim   "Copyright © 2026 Πρώτο Θέμα"
  searched   creative commons 0 · creativecommons anchors 0 ·
             "all rights reserved" 0 · licen[cs]e 0
```

A bare copyright line with no reservation wording, taken as
`all_rights_reserved` on the precedent of `southasia-07`, which recorded
`"© 2026 The Trustees of the British Museum"` under that position. **If Rob reads
a bare © line as something short of all-rights-reserved, this cell and the four
British Museum cells move together and that is a vocabulary question, not a
reading question.**

### www.heritage.go.kr — 1 record, AND A PREDICTION REFUTED

```
eastasia-03-hwangnam-glass
  read_off   heritage.go.kr/heri/cul/culSelectDetail.do (VdkVgwKey 11,01930000,11)
  position   all_rights_reserved
  verbatim   "© 2025 Korea Heritage Service. All rights reserved"
  also on the page, in a meta tag:
             "COPYRIGHT(C) 2000~CULTURAL HERITAGE ADMINISTRATION.
              ALL RIGHTS RESERVED."
```

**The predictions said this would come back under a Korean Open Government
Licence and it does not.** `공공누리` — KOGL — does appear in the page's HTML,
**once, as the label of a search-filter dropdown** (`전체 / 제1유형 / 제2유형`) for
finding *other* records by their KOGL type. It is a facet, not a mark on this
object, and the object carries a reserved-rights line instead.

**This is the single most useful thing the pass found about the triage script
proposed in §3 of the start document.** A pass hunting licence signals would have
returned `공공누리` here and proposed an open licence, off a `<select>` element.

### uci.edu / sites.uci.edu — 1 record

```
persia-05-abnun
  read_off   sites.uci.edu/sasanika/abnun-inscription/    <- the object
  position   all_rights_reserved
  verbatim   "Privacy Notice | © 2026 UC Regents"
```

See §1D. The policy page at `uci.edu/copyright/` was also read and states
*"Copyright © 2005-2025 The Regents of the University of California. All rights
reserved."* — recorded in the note, not quoted into the cell, because it is not
the object.

### real.mtak.hu — 1 record, AND THE OTHER PREDICTION REFUTED

```
seasia-03-khao-sam-kaeo
  read_off   real.mtak.hu/141407/
  position   open_licence_stated
  licence    Creative Commons Attribution Non-commercial  (NO VERSION PRINTED;
             the anchor points at creativecommons.org/licenses/by-nc/3.0/)
  verbatim   "Text 11_HoppalK_DissArch_2021_v01.pdf
              Available under License Creative Commons Attribution
              Non-commercial."
```

**THE PDF ITSELF COULD NOT BE RENDERED** — it froze the browser tab and the
screenshot timed out — so the reading is off the repository item page, **and the
distinction matters enough to state rather than bury**: this is not a site-wide
policy standing in for an object. The sentence names *this file*, by filename, in
the same line. That is an item-level statement about the object.

**The predictions called this `states_no_terms` on the reasoning that a PDF
states nothing.** The PDF may well state nothing; the page that serves it states a
licence about it by name, and that is the reading.

**A versioned licence printed without its version**, exactly like
`africa-06-ezana-rie189`. The cell records the string as printed and puts the
anchor's `3.0` in the note.

### isaw.nyu.edu — 1 record. CORROBORATION.

```
seasia-05-my-son-b6
  read_off   isaw.nyu.edu/publications/inscriptions/campa/inscriptions/C0087.html
  position   open_licence_stated
  licence    Creative Commons Attribution 3.0 Unported License
  verbatim   "C. 87 Stela from Mỹ Sơn B6: Copyright (c) 2012 by Arlo Griffiths.
              Licensed under a Creative Commons Attribution 3.0 Unported
              License."
  rel=license anchor  creativecommons.org/licenses/by/3.0/deed.en_US
```

The record's `notes` announce it as *"THE FIRST RECORD IN THIS CORPUS UNDER AN
EXPLICIT OPEN LICENCE"* and **the object agrees**. First of two clean
corroborations.

### www.projectmadurai.org — 1 record

```
southasia-01-akananuru-149
  read_off   projectmadurai.org/pm_etexts/utf8/pmuni0229.html
  position   permission_stated_no_licence
  searched   creative commons 0 · creativecommons anchors 0
```

> **"© Project Madurai, 1998-2006 .
> Project Madurai is an open, voluntary, worldwide initiative devoted to
> preparation of electronic texts of tamil literary works and to distribute them
> free on the Internet.
> Details of Project Madurai are available at the website
> http://www.projectmadurai.org/
> You are welcome to freely distribute this file, provided this header page is
> kept intact."**

A copyright assertion and an explicit permission, in one block, naming no
licence. **They do not disagree** — one says who holds the rights, the other says
what may be done — so this is the seventh position and not
`two_positions_stated`. The parsigdatabase precedent is two sentences that
contradict; this is two sentences that compose.

**Note how close this is in substance to the CBETA header in §1B**: both grant
reuse on condition the header travels with the file, and neither names a licence.
Two of this block's 24 cells are that same shape, found on opposite sides of the
world.

### papyri.info — 1 record. CORROBORATION.

```
southasia-03-muziris-papyrus
  read_off   papyri.info/editions/sb/18/13167
             (the record's /ddbdp/sb;18;13167 URL redirects to this)
  position   open_licence_stated
  licence    Creative Commons Attribution 3.0 License
  verbatim   "© Duke Databank of Documentary Papyri. This work is licensed under
              a Creative Commons Attribution 3.0 License."
  rel=license anchor  creativecommons.org/licenses/by/3.0/
```

The record's prose says `(DDbDP, CC BY 3.0)` and **the object agrees**. Second and
last clean corroboration.

### www.wisdomlib.org — 1 record

`southasia-05-brihatsamhita`, `states_no_terms`. Covered in §1C.

---

# 3. WHAT THE TWENTY-FOUR COME TO

```
                                  proposed    predicted
states_no_terms                       8           9
all_rights_reserved                   8           7
open_licence_stated                   6           7
permission_stated_no_licence          2           1
two_positions_stated                  0           0
public_domain                         0           0
```

**Twenty-one of the twenty-four per-record calls were right and three were
wrong** — `eastasia-04` (predicted a licence, found a permission),
`eastasia-03-hwangnam-glass` (predicted KOGL, found all-rights-reserved),
`seasia-03-khao-sam-kaeo` (predicted silence, found a named licence).

**P7 is REFUTED and it is the refutation worth reading.** It predicted that 2 to 4
of the 24 would prove unreadable to standard and stay `unread`. **All 24 were
read.** Two put up resistance and neither survived it: Chrome refused two domains
and the desktop app's pane opened both; wisdomlib's bot interstitial resolved on
its own without a challenge being answered. The one genuine failure — the
`real.mtak.hu` PDF freezing the tab — did not cost the reading, because the
licence statement was on the page serving the file and names the file.

**On confirmation this column goes from 16 read / 38 unread to 40 read / 14
unread**, and the 14 have names: 9 in bucket C, 3 in bucket D, 2 in FINDING 118.

---

# 4. WHAT ROB IS BEING ASKED TO CONFIRM, AND THE THREE PLACES TO PUSH

Not all 24 are equally worth his time. **Three cells carry a judgement rather than
a transcription**, and they are where a confirmation pass earns its keep:

1. **The bare `©` line as `all_rights_reserved`** — five cells turn on it
   (`africa-02`, `persia-02`, `persia-03`, `africa-01`, `persia-05`), and the
   precedent for it is a single earlier cell. If the reading is wrong it is wrong
   five times at once.
2. **`seasia-03-khao-sam-kaeo` read off the item page rather than the PDF.** The
   sentence names the file, but the object cited is the file, and a stricter
   reading of RULING 74 leaves this `unread` until the PDF itself can be opened.
3. **`southasia-01-akananuru-149` as one position rather than two.** A © line and
   a permission sitting together — the call that they compose rather than
   contradict is a judgement, and `persia-06-shahrestaniha` is the precedent for
   the other way of seeing it.

**Everything else in this document is a sentence copied off a page**, and the
counts are given so that the absences can be checked as easily as the presences.

---

# 5. WHAT HAS NOT BEEN DONE, STATED PLAINLY

- **No cell is written.** `data/corpus_rights.json` has not been opened for
  editing and its byte count is unchanged at 30,990.
- **`python -m ingest.verify` has not been run.** It is host-only, the bridge
  shell is still down, and nothing here claims the shape gate is green. The
  runbook hands it to Rob.
- **Buckets C and D are untouched**, and so are the two records in FINDING 118.
- **No record's text, tier, placement, citation or offsets were changed**, and no
  `citation_original` was edited — including `persia-05-abnun`'s, which needs it.
- **`ui/` was not touched** and `ui/data.js` was not regenerated.
