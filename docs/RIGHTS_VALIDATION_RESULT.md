# RIGHTS VALIDATION RESULT — **TWENTY-FOUR CELLS READ, CONFIRMED AND WRITTEN.
# THE COLUMN IS 40 READ / 14 UNREAD AND EVERY ONE OF THE FOURTEEN HAS A NAME.**
#
# **The curator's pass changed three cells and produced a ruling and three
# findings the plan did not anticipate. The most consequential sentence in the
# block was found by Rob on a page the model had not opened.**

*Closed 2026-09-14. Scored against `RIGHTS_VALIDATION_PREDICTIONS.md`, committed
before a single rights target was opened — RULING 78 — and **not amended since**.*

---

# 1. WHAT THE COLUMN NOW SAYS

```
                                before      after      of which written today
unread                            38          14
all_rights_reserved                2          12               10
open_licence_stated                5          11                6
states_no_terms                    1           7                6
permission_stated_no_licence       3           5                2
two_positions_stated               3           3                0
public_domain                      2           2                0
                                  --          --               --
                                  54          54               24
```

**All 24 are signed `curator_and_model`.** Every one was opened by the model and
then opened again by Rob, who confirmed, amended or overruled it. Four were also
searched by Rob for terms the model had not looked for, and two of those searches
changed the answer.

**`southasia-07-bm-claudius-aureus` was amended**, not re-read: its position and
its original note stand, and it gains the image-page capture the other three
British Museum cells carry, so that all four are written to one standard.

---

# 2. THE TWENTY-FOUR

```
record                          position                      read_off host
------------------------------  ----------------------------  -----------------
africa-02-aksumite-coin         all_rights_reserved           britishmuseum.org
persia-02-silver-plate          all_rights_reserved           britishmuseum.org
persia-03-coin                  all_rights_reserved           britishmuseum.org
africa-03-periplus-adulis       open_licence_stated           el.wikisource.org
arabia-01-periplus              open_licence_stated           el.wikisource.org
southasia-02-periplus-muziris   open_licence_stated           el.wikisource.org
eastasia-04-jingjiao-stele      permission_stated_no_licence  raw.githubusercontent
eastasia-05-liangshu-qin-lun    states_no_terms               raw.githubusercontent
eastasia-06-cefu-yuangui        states_no_terms               raw.githubusercontent
eastasia-07-tang-huiyao         states_no_terms               raw.githubusercontent
africa-04-silko-talmis          all_rights_reserved           epigraphy.packhum.org
africa-05-adulis-throne         all_rights_reserved           epigraphy.packhum.org
persia-01-skz                   all_rights_reserved           parthiansources.com
persia-04-bronze-heracles       all_rights_reserved           parthiansources.com
scandinavia-01-hoby-treasure    states_no_terms               en.natmus.dk
scandinavia-02-gudme-hoard      states_no_terms               en.natmus.dk
africa-01-ezana-stone           all_rights_reserved           en.protothema.gr
eastasia-03-hwangnam-glass      all_rights_reserved           heritage.go.kr
persia-05-abnun                 all_rights_reserved           sites.uci.edu
seasia-03-khao-sam-kaeo         open_licence_stated           real.mtak.hu
seasia-05-my-son-b6             open_licence_stated           isaw.nyu.edu
southasia-01-akananuru-149      permission_stated_no_licence  projectmadurai.org
southasia-03-muziris-papyrus    open_licence_stated           papyri.info
southasia-05-brihatsamhita      states_no_terms               wisdomlib.org
```

## What the objects said that their own records did not

**Four flat contradictions**, all four on `raw.githubusercontent.com`:

```
eastasia-05/06/07   citation_original: "Licence: CC BY-SA 4.0."
                    the files state NOTHING. creative 0, licen 0, CC BY 0,
                    copyright 0, © 0, 版權/著作權/授權 0 -- confirmed by Rob on
                    the untranslated files
eastasia-04         citation_original: "Licence: CBETA, CC BY-NC-SA."
                    the file names no licence anywhere and states, in its own
                    TEI <availability>: "Available for non-commercial use when
                    distributed with this header intact."
```

**Two corrections.** `southasia-05-brihatsamhita`'s prose quotes wisdomlib as
saying it is *"free to read online"*; `free to read` returns zero on the object
page, the site root, the about page and the privacy policy. `persia-05-abnun`'s
prose asserted the site states nothing; there is a copyright line on the object
page and it is a hyperlink to the terms.

**One line that was the wrong shape rather than wrong.** The three Periplus
records carry *"(ed. C. Müller … Paris 1855; public domain)"* — true about the
edition, and not the position the page states, which is CC BY-SA 4.0 over the
transcription. §2E called this exactly.

---

# 3. SCORING THE PREDICTIONS

```
P1  CBETA/Kanripo split                        PARTLY CONFIRMED
P2  per-record calls, 24 of them               19 CORRECT, 5 WRONG
P2  states_no_terms is the largest outcome     REFUTED
P2  two_positions_stated returns zero          CONFIRMED
P3  one object, three cells, not derivation    CONFIRMED
P4  persia-05's target is a policy page        CONFIRMED -> FINDING 119
P5  exactly two clean corroborations           CONFIRMED
P6  bucket A teaches nothing                   REFUTED
P7  2 to 4 unreadable this session             REFUTED -- all 24 were read
P7  the confirmation pass changes at least one CONFIRMED -- it changed three
P7  the block does not close the column        CONFIRMED -- 14 remain
```

**P1 was right about the mechanism and wrong about the position.** It predicted
the four `raw.githubusercontent.com` records would split CBETA against Kanripo,
that the Kanripo files would state nothing, and that CBETA would state its terms
in its own header. All true. It then called CBETA `open_licence_stated`, and the
header names no licence at all — `permission_stated_no_licence`. **Predicting
that a file states its terms is not the same as predicting what it says.**

**The five wrong calls:** `eastasia-04` (licence → permission), `eastasia-03`
(KOGL → all rights reserved), `seasia-03` (silence → CC BY-NC 4.0), and
`africa-04` / `africa-05`, which moved from silence to all-rights-reserved on a
sentence the model never looked for.

**P2's headline is refuted and the refutation is informative.** It predicted
`states_no_terms` would be the largest single outcome at 9 of 24, on the
reasoning that *"a text served by a scholar states its edition and not its
terms"*. The largest outcome is `all_rights_reserved` at 10, and silence came
second at 6. **Scholarly hosts state terms more often than predicted; what they
do not do is state a licence.** Of the 10 all-rights-reserved cells, exactly two
are a commercial publisher's — the rest are museums, universities and a research
institute asserting rights in prose.

**P2's named failure mode did not fire.** It said `el.wikisource.org` was the
likeliest way the call would break, because a Wikisource page reproducing an 1855
public-domain edition might carry both a PD banner and the site licence, making
the three Periplus records `two_positions_stated`. The page was searched: zero
matches for `public domain` or `κοινό κτήμα`. **The prediction named the right
risk and the risk was not there.**

**P6 is refuted and it is the refutation this document most wants read.** It
predicted the three British Museum readings would return identical quotations and
teach the block nothing, and it named its own refutation condition: *"any one of
the three carrying an image-licence line … that is `two_positions_stated`, and it
would mean the policy did not transfer on the third object anyone happened to
check."* **All four British Museum objects route to an image page carrying CC
BY-NC-SA 4.0**, at four distinct image ids. It did not become
`two_positions_stated` — Rob ruled the licence into the note and the position
onto the text, which is what became RULING 96 — but the prediction that the
readings would teach nothing produced, from those four objects alone: the image
captures, FINDING 122, RULING 96, and an amendment to a cell written five weeks
earlier.

**FINDING 117's lesson repeats.** That finding records that a prediction specific
enough to be designed around stops being a forecast. P6 was written to be unkind
to the block and was refuted by the block doing the work properly — and the
refutation is worth more than the four cells it was about.

---

# 4. WHAT THE PASS PRODUCED THAT THE PLAN DID NOT

**RULING 96** — the cell records the position on the material the record's quoted
text comes from; other components, locations and formats go in the note. Declared
because it had four instances and was about to get a fifth.

**FINDING 120** — an object page's silence does not establish a source's silence.
The model searched objects only; Rob opened `epigraphy.packhum.org/` and found a
licence gate that moved two cells and put a personal-use restriction in front of
this project. The other three silences were then checked at their roots and held,
so the gap cost exactly one host of four.

**FINDING 121** — two licence signals on two hosts, both false: a KOGL label on a
search-filter `<select>`, and a TYPO3 boilerplate comment about the CMS's own
GPL. Third instance in the corpus after `seasia-08-pong-tuk-lamp`'s Joomla
template credit. The triage script may propose a sentence and may never write a
cell, and that is now three measured cases rather than an argument.

**FINDING 122** — all four British Museum object pages state their copyright line
in a footer that renders at zero height on a page that does not scroll. What a
page states and what its reader can see are different questions.

**FINDING 119**, declared earlier in the block — `persia-05-abnun`'s rights target
computed to a university policy page, because `citation_original` is prose and its
prose contains a URL. A field that is both an argument and a machine-readable
address will do this again.

---

# 5. THE INSTRUMENTS, AND ONE OF THEM WAS CAUGHT MID-PASS

```
CLAUDE IN CHROME       20 of 24 readings
THE DESKTOP APP'S      4 -- epigraphy.packhum.org x2, en.natmus.dk x2, which
BROWSER PANE              Chrome refuses to the extension outright
THE CURATOR'S OWN      every confirmation, and the real.mtak.hu PDF, which the
BROWSER                   model could not render at all
MACHINE TRANSLATION    MANUAL AND ON DEMAND by the curator, never automatic
```

**The translation instrument was established two confirmations late.** Rob's
first check of `KR2a0018_054.txt` was run over a Google-translated view, and he
said so. A translated DOM is a different document from the one the record cites,
and a search for ABSENCE run over it proves less than it appears to — if that
file had carried `版權`, translation would have rendered it as "copyright" and a
search for *creative* and *license* would have sailed past it. The check was
redone on the untranslated file. **The two confirmations already given before the
question was asked are recorded as having been given first**, rather than the
practice being presented as having held from the start.

---

# 6. THE RESIDUE, NAMED

```
BUCKET C   9 records   no citation_original; the rights target computes to the
                       English Wikipedia article. At least three situations
                       underneath, and the slow one is a CITATION defect
BUCKET D   3 records   zh.wikisource.org x2, academia.edu x1 -- hosts documented
                       as refusing or degrading. Unread, and unread is correct
FINDING    2 records   scandinavia-03-vimose, southasia-04-pattanam --
118                    web.archive.org captures. RULING 95 now says how to read
                       them; nobody has
```

**Not one of the fourteen is unread because a page was hard to open.** Every
target this block attempted was reached. The fourteen are unread because they
were out of scope, because their source is not yet established, or because the
host has been documented as refusing — which is the distinction §4 said the block
was most likely to collapse, and did not.

---

# 7. WHAT DID NOT HAPPEN, WHICH IS THE OTHER HALF OF THE RESULT

**No cell was filled from prose already in the record.** The fifteen records
carrying licence-shaped prose were all treated as unread and the sources opened.
Four of them turned out to be wrong, which is the whole argument for the rule.

**No unreachable source was recorded as `states_no_terms`.** Every silence in
this block is a page that rendered, and each such cell's note records what was
searched at the object AND at the site.

**No record's text, tier, placements or citation offsets were changed**, and no
`citation_original` was edited — including `persia-05-abnun`'s, which needs it.
`ui/data.js` was not regenerated and `ui/` was not touched.

**Nothing here claims `python -m ingest.verify` is green.** It is host-only, the
bridge shell is still down, and the runbook hands it to Rob.

---

# 8. THE SENTENCE THE METHODOLOGY COPY CAN NOW USE

Not *"most sources have not been checked"*, and not *"all sources are cleared"*.

> **Forty of the fifty-four sources in this corpus have had their rights position
> read off the object and quoted verbatim, each signed by a named reader on a
> named date. Fourteen have not, and each of those fourteen is named with the
> reason. Four records were found to carry licence claims their own sources do
> not make.**

That last clause is the one a reader will believe the rest of the page for.
