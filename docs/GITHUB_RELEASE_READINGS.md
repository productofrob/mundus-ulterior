# GITHUB RELEASE READINGS — **FIVE CELLS OWE MORE, NONE LEAVES THE TREE, AND
# FOUR OF THE FIVE ARE PERMISSIONS.**
#
# **The redistribution pass, step 2 of `GITHUB_RELEASE_PREDICTIONS.md`. Proposed
# 2026-10-26 by the model and CONFIRMED BY ROB THE SAME DAY: all 54 readings, and
# the Tamil title in R-3 against the page. Every reading is signed
# `curator_and_model`.**

`data/corpus_rights.json` is not edited by this pass. The portal's cells stand
as they are, and these readings sit beside them, so `ui/data.js` and the live
site do not move.

---

# 0. THE QUESTION, AND WHAT THE REPOSITORY ADDS

The portal's readings asked whether **the portal** may carry each text. This
pass asks whether **the repository** may: a copy that anyone can download whole,
from a page that invites them to build on it.

**Measured first: the repository carries no source text that the portal does
not.** For all 54 records, `original_text_excerpt` and `reference_translation`
appear verbatim in `ui/data.js` (under each record's `fields`). The record files
add only citation and rights prose that `data.js` leaves out:

```
citation_original      37 records   citations and rights statements, not source text
citation_pdf            1           arabia-02
museum_number           1           persia-02
no_places_reason        1           persia-03
secondary_citation      1           persia-01
tertiary_citation       1           persia-01
```

The archived answers under `eval/` quote record text, and `data.js` already
carries all 685 of them. **What the repository adds is form, not text:** the
whole corpus in one download, with an invitation to reuse it. So each cell's
question is whether its terms say anything about that form.

```
SAME          the repository carries the text on exactly the portal's reading
OWES MORE     it carries the text, but owes something the record does not
              already supply: a license text shipped with it, a notice outside
              the record, or a restriction DATA_RIGHTS.md must state
CANNOT CARRY  stated terms that a public repository does not satisfy
```

---

# 1. THE FIVE THAT OWE MORE

## R-1. `arabia-08-walters-marib-pediment` — GNU Free Documentation License

> "The longer text descriptions about the artworks on this website are released
> under the GNU Free Documentation License."
> — https://thewalters.org/about/policies/rights-reproductions/, read 2026-09-06

**The record is a copy of the whole licensed document.** Its
`original_text_note` says the excerpt is the Walters' own object description,
"VERBATIM AND ENTIRE", 700 characters. The GFDL's verbatim-copying clause (§2)
asks that "this License, the copyright notices, and the license notice saying
this License applies to the Document are reproduced in all copies." No version
is named, and §10 says that where none is, "you may choose any version ever
published."

**Proposed: OWES MORE.** The repository ships the GFDL 1.3 text at
`LICENSES/GFDL-1.3.txt`, and `DATA_RIGHTS.md` names the record against it.

**The same clause reaches the portal, which links the license rather than
reproducing it** (Methodology §2's license list: "GNU Free Documentation License
(no version stated)", linked to gnu.org). **Declared as FINDING 126** in
`GITHUB_RELEASE_RULINGS.md`, and not fixed: Rob's order of 2026-10-26 holds every
change to the Mundus Ulterior page until he gives it.

## R-2. `eastasia-04-jingjiao-stele` — CBETA

> "Available for non-commercial use when distributed with this header intact."
> — CBETA's TEI header, `<publicationStmt><availability>`, in
> https://raw.githubusercontent.com/cbeta-org/xml-p5/master/T/T54/T54n2144.xml

**The condition attaches to distribution, and a repository is distribution.**
The record carries a 93-character excerpt, not the file, so the condition can be
read as written for the file alone. Shipping the header costs nothing and
removes the question.

**Proposed: OWES MORE.** The header ships verbatim at
`data/rights/cbeta-T54n2144-teiHeader.xml`. It is 3,650 characters, cut byte for
byte from the file as fetched on 2026-10-26. The file is 17,749 bytes, sha256
`4ee81fefd61bf42c94a0aea16da517961e00fa556553c99f2588609ac5aea18c`; the header
alone is sha256
`58f29df6154e3dcbed87ac184cb6f71962a3a5e804cc5cd674513dccd04a2cb7`. The
availability sentence is identical to the one the cell read on 2026-09-14. The
header's own `<date>` reads 2025-01-30.

## R-3. `southasia-01-akananuru-149` — Project Madurai

> "You are welcome to freely distribute this file, provided this header page is
> kept intact."
> — https://www.projectmadurai.org/pm_etexts/utf8/pmuni0229.html

**The cell quotes the header's last six lines, and the header page is longer.**
It begins with the work's title (அகநானுறு, akanAnURu) and the
acknowledgements: the University of Köln's romanized etext (Dr. Thomas Malten
and colleagues), the TSCII proofreaders, and the HTML and PDF preparation.
"Kept intact" means all of it. The record carries a 632-character excerpt,
which is the same question as R-2, with the same answer.

**Proposed: OWES MORE.** The header page ships at
`data/rights/project-madurai-pm0229-header.txt`. It was captured on 2026-10-26
from the page's own text in Chrome: 880 characters, 897 bytes, sha256
`e143322807df78dca0d06c863b1775a939c8aaaee1e761660ca29b51816c3009`. The first
eight bytes of that hash were computed in the page and matched the file built
here. **The Tamil title is eight characters, and Rob confirmed them against the
page on 2026-10-26**, as he does for every non-English string.

## R-4 and R-5. `scandinavia-06-tjurko-bracteate`, `scandinavia-07-rycksta-grikkium` — Riksantikvarieämbetet

> "Information om databasen får gärna återanvändas på webbsidor, men vi är
> tacksamma om källan alltid anges med en hänvisning till Samnordisk
> runtextdatabas och en länk till objektets stabila URI på kulturarvsdata.se …"
> — https://www.raa.se/hitta-information/runor/vanliga-fragor-runor/att-citera-innehall-ur-runtextdatabasen/

In English: *information from the database is welcome to be reused on web
pages, but we are grateful if the source is always given, with a reference to
the Samnordisk runtextdatabas and a link to the object's stable URI on
kulturarvsdata.se.*

**The permission names a medium.** It welcomes reuse "on web pages". It does
not restrict reuse to them, and it is citation guidance rather than a license.
Both records already give the attribution in the source's own form, with the
stable URIs (`…/srdb/d3844f66-…` and `…/srdb/16595786-…`).

**Proposed: OWES MORE, not CANNOT CARRY.** `DATA_RIGHTS.md` states the
permission's scope as RAÄ words it, and says that it is RAÄ's permission and
does not pass to anyone who takes these records from the repository.

---

# 2. THE FORTY-NINE THAT ARE SAME, BY THE REASON EACH GROUP SHARES

```
public_domain             4   africa-04, africa-05 (OGIS, RULING 98), africa-07,
                              southasia-06. Nothing to owe
CC0                       1   persia-07. Nothing to owe
CC BY                     4   arabia-05, arabia-07 (4.0); seasia-05,
                              southasia-03 (3.0). Attribution and the license
                              are in each record
CC BY-NC                  2   africa-06, seasia-03. The non-commercial term is
                              stated verbatim in each record, and the repository
                              grants nothing over it
CC BY-SA                 10   three el.wikisource excerpts, copied verbatim; seven
                              records read off Wikipedia under RULING 99. The
                              portal already says, in Methodology §2, "Text
                              adapted from a ShareAlike source is shared under
                              that same license."
                              DATA_RIGHTS.md repeats that sentence, so that
                              RULING 101's "no license from this project" over
                              the corpus does not contradict it. That is owed by
                              the portal's own reading, not added by the
                              repository
permission                2   eastasia-08: the Sourcebook grants electronic
                              copying for educational purposes, asks for the
                              source, and refuses commercial use; the record does
                              all three. seasia-07: SEAlang's "freely available
                              for re-use"
two_positions_stated      3   eastasia-09, persia-06, seasia-09. Neither position
                              is adjudicated, for the portal or here. seasia-09
                              stays the weakest cell in the corpus, because
                              UNESCO's blanket "may not be copied or retransmitted
                              by any means" reaches a repository and a portal
                              alike. The repository changes nothing about it
all_rights_reserved      15   RULING 74's four conditions hold identically: the
                              same short quotation, fully cited, with the position
                              verbatim in the record and the use non-commercial
states_no_terms           8   RULING 74: each record says so, in those words
```

---

# 3. CANNOT CARRY — NONE

No cell states terms that a public repository fails and the portal meets. The
two places where it could have happened are the "header intact" conditions,
which a shipped header satisfies (R-2 and R-3), and RAÄ's "on web pages", which
welcomes reuse rather than limiting it (R-4 and R-5).

---

# 4. THIRD-PARTY DATA IN THE REPOSITORY (not cells)

```
Pleiades           CC BY 3.0 US, quoted in data/pleiades-licence-declaration.txt.
                   data/gazetteer.json is derived from it: credit, link, and
                   say it was changed
GeoNames           CC BY 4.0, quoted in data/geonames-licence-declaration.txt.
                   The same three obligations
Natural Earth      public domain. Read 2026-10-26 off
                   https://www.naturalearthdata.com/about/terms-of-use/ :
                   "All versions of Natural Earth raster + vector map data found
                   on this website are in the public domain." and "No permission
                   is needed to use Natural Earth. Crediting the authors is
                   unnecessary." Credited anyway
The Met            CC0, quoted in data/met-licence-declaration.txt (2026-08-14)
Cleveland Museum   CC0. data/cma-licence-declaration.txt rested on Rob's own
of Art             check and asked to be re-read "if this material is ever
                   relied on outside the project." A public repository is that
                   case. Read 2026-10-26 off
                   https://www.clevelandart.org/open-access-api :
                   "To the extent possible under law, the Cleveland Museum of
                   Art has waived all copyright and related or neighboring
                   rights to this dataset using Creative Commons Zero."
                   The wording goes into the declaration in the front-door
                   commit
```

---

# 5. WHAT THIS PASS DID NOT COVER

**The process documents.** A document can quote a source that no record carries:
a candidate considered and not taken, or a longer passage pasted during
curation. That is history-and-tree work, and it is added to step 3's scan, which
looks for source text in the documents that no record carries, alongside the
withdrawn PHI Greek.
