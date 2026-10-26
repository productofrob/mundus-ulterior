# Rights validation — rulings and findings. **RULING 95 and FINDING 118**,
# declared 2026-09-14, before any rights target was opened.

*Numbers read from `RULINGS.md` at the time, per `RIGHTS_VALIDATION_START.md` §5:
the register's own line said "The next free ruling number is 95. The next free
finding is 118." That line is updated in the same commit as this file.*

---

# FINDING 118, 2026-09-14, in the first ten minutes of the rights block.

**A worklist that buckets by host will silently drop the records whose host is
not a source.**

`RIGHTS_VALIDATION_START.md` §2 sorts the 38 unread records into four buckets —
3 + 21 + 9 + 3. **That is 36.** Recomputed from `data/corpus_rights.json` and the
54 seed records before any page was opened, the two records in no bucket are:

```
scandinavia-03-vimose    web.archive.org/web/20151122163034/
                         http://www.runenprojekt.uni-kiel.de/...
southasia-04-pattanam    web.archive.org/web/20160304031410/
                         http://www.keralahistory.ac.in/...
```

**Both are Wayback Machine captures, and that is why they fell out.** Every other
bucket is defined by a host that is a publisher — a museum, a library, a
repository, an aggregator. `web.archive.org` is a host that is not a source, and
a rule written by grouping hostnames has nowhere to put it. The start document's
own §1 figures are exact — 38 unread, 18 hosts — and `web.archive.org` is one of
the 18 it counted and none of the four it bucketed.

**This is FINDING 115's shape once more, and the start document warned about it
in its own §7.** A figure can be right while the prose built on it is short: §1
counted 38 and §2 worked 36, and nothing in either document could see the gap
because no instrument reads a worklist. The gap was found by recomputing the
buckets rather than by reading them, which is exactly what §6.1 told this thread
to do and the only reason it was found before the block closed instead of after.

**What it costs:** two records that would have stayed `unread` with no name
against them, in a block whose entire purpose is to make the residue nameable.

---

# RULING 95 — **AN ARCHIVED CAPTURE IS THE PAGE AS CAPTURED. THE ARCHIVE'S OWN
# TERMS ARE NOT THE SOURCE'S POSITION.**

Where a record's rights target is a `web.archive.org` capture, the object is the
**original page at the moment of capture**, and the rights position is read off
the captured page.

```
THE OBJECT        the archived page, as rendered inside the capture

READ_OFF          the full Wayback URL, timestamp included. The timestamp is
                  part of the reading: it says WHICH state of the source was
                  read, and a live site may state something else today

EXCLUDED          everything archive.org injects -- the toolbar, the banner,
                  the "About this capture" panel, any archive.org footer.
                  None of it is the source speaking, and none of it may be
                  quoted into a cell

NOT THE POSITION  archive.org's own terms of use. They govern the archive,
                  not the archived. A cell quoting them is a reading of the
                  wrong object -- FINDING 87, one layer up

STATES_NO_TERMS   available only if the capture RENDERED and the captured page
                  states nothing. A capture that will not load, or that loads
                  without the region of the page where terms would sit, is
                  `unread` -- section 4 of the start document, unchanged
```

**Why this and not the alternative.** The obvious competing rule is that a
capture states two positions — the archived site's and archive.org's — to be
quoted in the order they appear under the parsigdatabase precedent. **It is
wrong, and it is worth saying why, because it looks rigorous.** Two positions
means one source contradicting itself. The archive is not the source; it is the
delivery. Recording archive.org's terms beside the captured page's would make
every archived record in this corpus `two_positions_stated` by construction,
which is a fact about how the text was fetched and not about who holds rights in
it — **the reachability-for-licence substitution FINDING 69 exists to forbid,
committed in a new place.**

**What this ruling does not settle**, recorded so nobody reads it as settled: it
says nothing about whether the archived page's terms are still in force, and
nothing about whether the capture is a faithful rendering of what the page said.
It fixes which object is read. The freshness question belongs to whoever next
argues about `read_on`.

**Neither of the two records in FINDING 118 is read in this session.** Rob's
scope for the block is bucket A and bucket B. The ruling exists so that when they
are read, the rule was written before the reading and not around it.

---
---

# DECLARED AT THE CLOSE OF THE CONFIRMATION PASS, 2026-09-14

*The four below were produced by the pass itself rather than by the plan for it.
Numbers read from `RULINGS.md` at the time: ruling 96, findings 120 to 122.
Rob's instruction for this block was to limit what gets carried over — a defect
found here is written up here, not handed to a later thread as an open item.*

---

# RULING 96 — **THE CELL RECORDS THE POSITION ON THE MATERIAL THE RECORD'S
# QUOTED TEXT COMES FROM. EVERYTHING ELSE GOES IN THE NOTE.**

Where a record touches more than one thing that has a rights position — a text
and an image, a source text and a translation, an object page and the site that
serves it — **the `position` field records the position on the material the
record's quoted text comes from.** Positions attaching to other components,
other locations or other formats are quoted verbatim in the `note` and never in
the `position`.

```
COMPONENTS    a catalogue description and a photograph of the same object are
              two components. The record quotes the description; the
              description's position is the cell

SOURCES       a Chinese source text and an English translation from different
              hosts are two components. eastasia-08-songshi-fulin's cell is for
              the translation, because that is what its English quotes

LOCATIONS     an object page and the site root that gates access to it are not
              two components -- they are two locations of one source. The cell
              records the position the SOURCE states, wherever on the source it
              is stated, and the note says where

FORMATS       a PDF and the repository page that serves it are two locations of
              one source. Where they DISAGREE the object's own statement is the
              position -- seasia-03-khao-sam-kaeo, where the article says CC
              BY-NC 4.0 and the repository's metadata says 3.0
```

**Declared because it had four instances and was about to get a fifth.**
`eastasia-08-songshi-fulin` named the problem in F6 and left it open: *"A record
whose two halves have two rights positions is a case this column cannot yet
express, and it is named here rather than resolved by picking the more flattering
one."* The confirmation pass then met it three more times in one day — the four
British Museum records, `africa-04`/`africa-05`, and `southasia-03-muziris-papyrus`.
**Four notes saying the column allows one position is three more than a
repository should tolerate**, and the rule below was already being applied
twenty-four times before it was written down.

**What it does not do.** It does not decide whether a quotation may stand — that
is RULING 74 — and it does not license ignoring the other component. The note is
mandatory: a cell that silently drops an open licence on an adjacent component is
worse than one that never found it, because it looks complete.

---

# FINDING 120, 2026-09-14. **AN OBJECT PAGE'S SILENCE DOES NOT ESTABLISH A
# SOURCE'S SILENCE, AND THE MODEL SEARCHED ONLY OBJECT PAGES.**

`states_no_terms` claims that a source states nothing. For every silence it
proposed, this session searched **the object page** — counts over the full HTML
for `copyright`, `©`, `licen[cs]e`, `creative commons`, `all rights reserved`,
`terms of use` and `creativecommons` anchors — and did not open the site root.

**Rob opened `epigraphy.packhum.org/` and found a licence gate:**

> *"I agree to use this website only for personal study and not to make copies
> except for my personal use under "Fair Use" principles of Copyright law."*
> *"Click here if you agree to this License"*

Two cells proposed as `states_no_terms` are now `all_rights_reserved`, and the
personal-use restriction is a term this project does not satisfy — the most
consequential single sentence the block turned up.

**The other three silences were then checked at their roots and held.**
`en.natmus.dk` (root, privacy policy, digital collections) and `wisdomlib.org`
(root, about, privacy policy) carry no rights statement anywhere and have no
terms page in their link sets. **So the gap cost exactly one host of four** — and
it would have cost nothing if the practice had been in the method from the start.

**The rule this leaves behind:** a `states_no_terms` cell must record what was
searched at the SITE as well as at the object, and name it in the note. FINDING
87 says read the object; it does not say read only the object.

---

# FINDING 121, 2026-09-14. **TWO LICENCE SIGNALS ON TWO HOSTS, BOTH FALSE, AND
# AN AUTOMATED MATCHER WOULD HAVE TAKEN BOTH.**

`RIGHTS_VALIDATION_START.md` §3 proposes a triage script that surfaces candidate
signals — `rel="license"`, `creativecommons` hrefs, badges, `dcterms.rights`,
footer text — and argues it does not break the never-derive rule because it
proposes a sentence to read and writes nothing. **This pass produced the
evidence for why that distinction has to hold.**

```
heritage.go.kr    `공공누리` (KOGL) appears exactly once on the object page:
                  as the LABEL OF A SEARCH-FILTER DROPDOWN (전체 / 제1유형 /
                  제2유형) for finding other records by licence type. The
                  object is all_rights_reserved. A matcher would have
                  proposed an open government licence off a <select>

en.natmus.dk      raw HTML returns `copyright` 2 and `licence` 1 on both
                  object pages, entirely from an invisible TYPO3 comment:
                  "TYPO3 is ... licensed under GNU/GPL. TYPO3 is copyright
                  1998-2019 of Kasper Skaarhoj." A matcher would have
                  proposed the GPL over a museum's prose
```

**Third instance in this corpus, and the first two are already recorded.**
`seasia-08-pong-tuk-lamp`'s cell names a Joomla template vendor's `© 2009-2014
by GPIUTMD` as the only copyright line on that site — a credit for the site's
design. The pattern is now: **the licence signal on a page is at least as likely
to belong to the software as to the source.**

**What it settles about the triage script:** build it, and let it print candidate
sentences beside the record for a person to accept or reject. **It may never
write a cell**, and the reason is now three measured cases rather than an
argument from principle.

---

# FINDING 122, 2026-09-14. **A SOURCE CAN STATE ITS RIGHTS IN A DOCUMENT AND
# RENDER THEM AT ZERO HEIGHT.**

All four British Museum object pages in this corpus carry
`© 2026 The Trustees of the British Museum` in their own HTML. Measured on
2026-09-14 on every one of them:

```
footer element    display: block · visibility: visible · opacity: 1
bounding rect     height 0px
document          scrollHeight == viewport height -- the page does not scroll
body innerText    2,468 characters, and the copyright line is not among them
```

**The collection application takes the whole viewport and the site footer
collapses behind it.** The line is in the document and is never painted. A
visitor cannot find it by scrolling, and the curator was asked to look for it
before this was disclosed — which was the wrong way round and is recorded as
such.

**Why it matters beyond the British Museum.** The reading stands: the sentence
is in the object's own document, served with it, and `southasia-07` set that
precedent in F6. But it means **"what the page states" and "what a reader of the
page can see" are different questions**, and a rights column that quotes the
first while a visitor experiences the second should say so. Every single-page
application serving catalogue records is a candidate for the same shape.
