# SOURCE MATERIAL FOR THE METHODOLOGY PAGE, SECTION 2: DATA SOURCING
#
# **Every figure below was computed on 2026-09-14 from a clean tree at
# `219c8a5`, with `python -m ingest.verify` green. None is inherited from a
# document. Each has its provenance named in §6 so the Methodology thread can
# recompute it rather than quote it on trust.**

*Written by the rights validation block for the thread that owns `ui/`. §5 of
`RIGHTS_VALIDATION_START.md` put the Methodology copy out of this block's scope
and it stays out: **nothing here is committed to `ui/` and none of it is copy.**
§3 of the same document said the result must state the position accurately
"because the Methodology copy will quote it" — this is that, assembled in one
place so Section 2 can be written without reading six documents.*

---

# 1. THE CORPUS IN FIGURES

```
records                     54
chunks                     170
parallel pairs              33

non-English retrieval-eligible chunks    49, in 14 language codes
    grc 16 · lzh 7 · pal 6 · gmq-pro 3 · mul 3 · xsa 2 · xna 2 · xpr 2 ·
    san 2 · omy 2 · non 1 · oty 1 · ocm 1 · gez 1

tiers        verbatim_with_provenance     29
             catalogue_record             16
             verbatim_machine_english      4
             published_translation_only    4
             pointer_only                  1

placement    53 placed + 1 declared unplaceable = 54 of 54 considered
             32 with a named place · 66 distinct gazetteer ids · 1 contested
             grounds: stated 70 · regional 96 · identified 3
```

**Source-language records by region**, and the distinction that matters more than
the count — is the region *speaking*, or being *spoken about*:

```
                      records   speaking   spoken about
Arabia                   6          5           1
East Asia                7          7           0
Persia                   4          4           0
Scandinavia              4          4           0
South Asia               4          2           2
Southeast Asia           4          4           0
Sub-Saharan Africa       4          3           1
```

**No region is silent.** There is no region with no source-language record in a
language of the region, and none with no record speaking at all. Sub-Saharan
Africa's three "speaking" includes two records in an empire language written
*from* the region — a distinction FINDING 68 exists because an earlier count
could not make it, and reported a region whose own rulers wrote in Greek in the
same words as a region only ever written about.

**One text counts as a source-language record in three regions** — the *Periplus
of the Erythraean Sea*, as `arabia-01-periplus`, `southasia-02-periplus-muziris`
and `africa-03-periplus-adulis`. Section 2 should say so if it prints regional
counts, because 33 source-language records are not 33 distinct texts.

---

# 2. RIGHTS: WHAT THE COLUMN NOW HOLDS

```
all_rights_reserved              12
open_licence_stated              11
states_no_terms                   7
permission_stated_no_licence      5
two_positions_stated              3
public_domain                     2
unread                           14
                                 --
                                 54

40 of 54 read, off 26 distinct hosts
```

**Every non-`unread` cell is signed.** `read_by` across the 40:

```
curator_and_model    25     read by the model and again by Rob, host by host
model                10     read by the model alone, F6 and F7
curator               5     read by Rob alone, F5 Part 3 and F6
```

**The eleven named licences, as printed by their sources** — the column records
what each page printed, not a tidied version:

```
CC BY-SA 4.0 (in Greek)                      x3   el.wikisource.org
CC BY 4.0                                    x2   dasi.cnr.it, edizionicafoscari
CC BY 3.0                                     1   papyri.info
CC BY 3.0 Unported                            1   isaw.nyu.edu
CC BY-NC 4.0                                  1   real.mtak.hu
CC0 1.0 Universal                             1   metmuseum.org
CC BY-NC (no version printed)                 1   dlib.nyu.edu
GNU Free Documentation License (no version)   1   thewalters.org
CC BY-SA 3.0 IGO                              1   whc.unesco.org — and whether it
                                                   reaches the text quoted is the
                                                   unsettled question in that cell
```

**Two of them print a licence without a version.** The column records the string
as printed rather than supplying one, which is why `open_licence_stated` is not
the same as "we know which licence applies".

---

# 3. THE PART SECTION 2 SHOULD LEAD WITH

**Four records carried licence claims their own sources do not make**, and they
were found by opening the sources rather than by reading the records.

```
eastasia-05-liangshu-qin-lun  |  citation_original: "Licence: CC BY-SA 4.0."
eastasia-06-cefu-yuangui      |  The Kanripo files state NOTHING. Searched over
eastasia-07-tang-huiyao       |  the whole of each: creative 0, licen 0, CC BY 0,
                              |  copyright 0, © 0, 版權/著作權/授權 0

eastasia-04-jingjiao-stele    |  citation_original: "Licence: CBETA, CC BY-NC-SA."
                              |  The CBETA file names no licence anywhere and
                              |  states, in its own TEI header: "Available for
                              |  non-commercial use when distributed with this
                              |  header intact."
```

**The licences are not false about Kanripo or CBETA. They are absent from the
objects** — they live in repository `LICENSE` files, and the records quote the
files. That is the distinction the whole column exists to hold, and it is the
most concrete thing this project can show a reader about its own discipline.

**Two further corrections, smaller and the same species.**
`southasia-05-brihatsamhita`'s record quotes wisdomlib as saying it is *"free to
read online"*; that string returns zero on the object page, the site root, the
about page and the privacy policy. `persia-05-abnun`'s record asserted its source
states nothing; there is a copyright line on the object page, and it is a
hyperlink to the terms.

**And one line that was the wrong shape rather than wrong.** The three *Periplus*
records carry *"(ed. C. Müller … Paris 1855; public domain)"* — true about the
1855 edition, and not the position the page states, which is CC BY-SA 4.0 over
the transcription. A rights column and an edition's copyright status are
different facts and the record was carrying one in the other's place.

---

# 4. WHAT SECTION 2 MAY CLAIM, AND WHAT IT MAY NOT

**These are true and checkable:**

- Forty of the fifty-four sources have had their rights position read off the
  object and quoted verbatim, each signed by a named reader on a named date.
- Twenty-five of those forty were read twice, by two different readers.
- Fourteen have not been read, and each is named with the reason.
- Four records were found to carry licence claims their sources do not make.
- Positions are **counted, never gated**: `all_rights_reserved` is a statement
  about what a source said, not a verdict on whether a quotation may stand.
- No position was derived — not from the record's own prose, not from a matcher,
  not from a sibling record on the same host.

**These are false, or true of something else, and are the tempting ones:**

```
"all sources are cleared"            No. Twelve are all-rights-reserved and
                                     RULING 74 governs whether each quotation
                                     stands. The column does not clear anything

"most sources have not been checked" No, and this was the sentence that started
                                     the block. Rights were investigated during
                                     curation — the cost ledger tracks
                                     `rights_and_licence` as its own phase and
                                     twenty of thirty timed records carry minutes
                                     against it. What was missing was the looking
                                     WRITTEN DOWN in a form a check can see

"the British Museum publishes        No. Four object pages carry a reserved-rights
 under CC BY-NC-SA"                  line; four IMAGE pages carry CC BY-NC-SA 4.0;
                                     the corpus quotes catalogue text, not images.
                                     The Museum's own policy says the licence
                                     applies only to content carrying the mark

"seven sources state no terms"       Say instead: seven objects were REACHED and
                                     state no terms. A source that could not be
                                     opened is `unread`, and the difference is the
                                     single most likely way this page ships a lie
```

---

# 5. THE FOURTEEN UNREAD, DESCRIBED WITHOUT APOLOGISING OR HIDING

```
9   no citation_original, so the rights target computes to the English Wikipedia
    article the record cites. At least three situations underneath, and the slow
    one is a CITATION defect rather than a rights defect: a text taken from a
    named edition that the record does not cite

3   hosts documented as refusing or degrading — zh.wikisource.org (cache-only) x2,
    academia.edu (behind a login) x1

2   web.archive.org captures. RULING 95 now says how to read them — the object is
    the page as captured, the archive's own terms are not the source's — and
    nobody has yet
```

**Not one of the fourteen is unread because a page was hard to open.** Every
target the block attempted was reached, including one behind a bot interstitial
that resolved on its own and two on hosts one browser refused and another opened.
The fourteen are unread because they were out of scope, because their source is
not yet established, or because the host is on record as refusing.

---

# 6. DRAFT SENTENCES — **FOR THE METHODOLOGY THREAD TO TAKE, REWRITE OR REFUSE**

*Not copy. Not committed. The tone is this document's, not the page's.*

> **Where the texts come from.** Fifty-four records, drawn from twenty-six
> distinct hosts — national museums, university libraries, epigraphic databases,
> digital text repositories and a handful of scholarly editions. Forty-nine of
> the chunks the retrieval system can reach are in a language other than English,
> across fourteen language codes, from Ancient Greek and Literary Chinese to
> Ge'ez, Old Tamil, Old Cham and Proto-Norse.

> **What we checked, and what we found.** For each source we opened the object
> itself and read what it says about reuse, then quoted that sentence verbatim
> into the record. Forty of the fifty-four now carry such a reading, signed by
> the person who made it and dated; twenty-five were read twice by two readers.
> Four records turned out to claim a licence their source does not state — in
> each case because the licence belonged to the repository holding the file
> rather than to the file the record quotes.

> **What we have not checked.** Fourteen sources have no reading. Nine are
> records whose underlying edition we have not yet established well enough to
> know what to read; three are hosts that refuse automated and human access
> alike; two are archived captures of sites that no longer serve the page. We
> would rather show you that number than round it away.

> **A note on what this column is not.** Recording that a source reserves its
> rights is not a judgement that we may quote it, and recording an open licence
> is not a claim that everything on the page carries it. Twelve of our sources
> reserve their rights; we quote them at quotation length, with attribution,
> and say so.

---

# 7. WHERE EVERY FIGURE COMES FROM

```
54 records · 170 chunks · 33 parallel pairs   python -m ingest.verify, 2026-09-14
49 non-English chunks in 14 codes             same run, "retrieval-eligible" line
tiers, regions, provenance, placements        same run
rights distribution                           same run, and data/corpus_rights.json
26 distinct hosts · read_by counts            computed over corpus_rights.json's
                                              40 non-unread cells at 219c8a5
the four contradictions                       RIGHTS_VALIDATION_RESULT.md §2, and
                                              each record's own cell note
the cost-ledger claim in §4                   data/curation_cost.json, via
                                              python -m ingest.cost_log report --
                                              the only place a curation-cost
                                              number may be read from
```

**If Section 2 prints a number, it should be one of these, and the page should be
rebuilt from the data rather than from this document.** `ui/data.js` is generated
by `python ui/build_ui_data.py` — FINDING 101 before running it on Windows — and
`data/corpus_rights.json` is a sidecar no corpus walk reaches, so if the page is
to show rights counts, that build is the other thread's decision and its own
commit.
