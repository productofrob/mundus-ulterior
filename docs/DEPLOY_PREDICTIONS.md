# DEPLOY PREDICTIONS — **THE FOURTEEN ARE THREE JOBS, NOT ONE, AND NINE OF
# THEM ARE CITATION WORK BEFORE THEY ARE RIGHTS WORK.**
#
# **Written 2026-09-22, before any code, data, or copy was edited and before any
# rights target was opened. RULING 78: committed first, scored at the close in
# `DEPLOY_RESULT.md`, and not amended there.**

---

# 0. THE STATE THIS IS PREDICTED AGAINST

Read over the bridge and in the session container on 2026-09-22.

```
HEAD                 e64d372  the start document's own commit, on 5863383
tree                 clean
harness              run by Rob on the host: "runs without error". The start
                     document's count is 63; the count line was not pasted
the artifact         index.html 384,397 B · data.js 9,782,002 B ·
                     banner/*.png x9 163,474 B · 11 files, 10,329,873 B
next free            RULING 98 · FINDING 123
```

**The page was looked at before anything else, as §8 says.** From disk
(`file://`) in the session container's Chromium, on a Linux filesystem, at
1600×1000 and 390×844:

```
console errors, page errors      0 at both widths
failed requests on Home's load   0 at both widths -- all 11 files load from
                                 a CASE-SENSITIVE filesystem
horizontal page scroll           none at either width
at 390px                         the stat strip is its own scroller:
                                 overflow-x auto, 571px of content in 358px,
                                 so "63 locations" is off screen until swiped.
                                 Deliberate, and not touched by this block
```

**One thing the start document does not list was visible on the first look:
British spellings that the 2026-09-22 sweep missed.** Measured over the rendered
text of all four tabs with every `<details>` opened, on sixteen patterns
(-isation, -ised, -ising, colour, behaviour, catalogue, centre, licence,
practise, favour, honour, analyse, travelled, labelled, modelled, artefact).
That is a narrow pass, not a sweep:

```
PAGE COPY      " · romanised"   the banner-label template, index.html:5754.
                                Four labels, shown on every tab
               "romanised"      Methodology, "some as romanised
                                transcriptions", index.html:5663
RECORD PROSE   "catalogue"      the Šahrestānīhā title
               "travelled"      the Rycksta stone title
               "organised"      "the country the passage is organised
                                around" and its variants -- place notes,
                                rendered six times on Methodology
```

Declared as **FINDING 124** in `DEPLOY_RULINGS.md`. The page-copy half is a
correction to existing sentences, which §5 allows. The record-prose half moves
fingerprints and belongs to the record pass.

## What was NOT looked at before writing, so that what follows is a forecast

- the compressed size of anything
- what any tab other than Home requests when it is opened
- which files `ui/check_ui.mjs` reads
- any field of the fourteen unread records, or any of their rights targets
- the OGIS scans

## The fourteen, by the reason each is unread, from `data/corpus_rights.json`

```
source_not_established  9   arabia-02-palmyrene-tariff, arabia-03-jsnab17,
                            arabia-04-jabal-dabub, scandinavia-04-illerup-adal,
                            scandinavia-05-thorsberg-chape, seasia-02-oc-eo-site,
                            seasia-04-dong-yen-chau, seasia-06-kedukan-bukit,
                            seasia-07-talang-tuo
host_refuses            3   eastasia-01-weilue, eastasia-02-hou-hanshu
                            (zh.wikisource.org), seasia-01-oc-eo-medallion
                            (academia.edu)
archived_capture        2   scandinavia-03-vimose, southasia-04-pattanam
                            (web.archive.org, RULING 95)
```

**`DEPLOY_START.md` §2 calls fourteen "a bounded job". That is true of five.**
The other nine have no `citation_original`, so there is no object to read a
position off until the source of the record's text is established. The rights
result called this "a CITATION defect and not a rights one", and it is the slow
part of the block.

---

# 1. DECISIONS TAKEN 2026-09-22, BEFORE THIS WAS WRITTEN

```
D1  the record pass S9-S18 lands BEFORE the deploy         recommended, taken
D2  africa-04 and africa-05 are re-sourced from OGIS        recommended, taken
    -> RULING 98
D3  host: Cloudflare Pages, a direct upload of the 11       recommended, taken
    files, with no repository attached
D4  address: the host's default subdomain (*.pages.dev)    Rob's choice, over
                                                            the recommended
                                                            productofrob.com
                                                            subdomain
```

**D3 keeps repo visibility where the start document put it, as a side issue.**
GitHub Pages on a free plan would have required a public repository and pulled
that decision into this block. **D4 takes a DNS step out of the block.**
productofrob.com resolves to a Squarespace address, so a subdomain would have
been a CNAME there. One can still be added later without redeploying.

## The order of work these decisions produce

```
1  this document and DEPLOY_RULINGS.md, committed
2  RULINGS.md indexes 97 and 98, and its next-free line is corrected
3  the five bounded readings: 3 host_refuses, 2 archived_capture
4  the nine: establish each record's source, then read its terms
5  RULING 98: collate africa-04 and africa-05 against OGIS
6  the record pass: S9-S18, and the record-prose half of FINDING 124
7  the page-copy half of FINDING 124
8  rebuild data.js (and the banner if a label changed), run the harness, look
   again
9  deploy, check byte parity, and score these predictions
```

---

# 2. THE PREDICTIONS

## P1 — the fourteen readings

**Publishable unchanged** means the source states nothing, or it states terms
that a public, non-commercial portal quoting a short attributed excerpt
satisfies. That covers any open license, NC and SA included, and a bare
copyright line, which RULING 74 already governs for twelve cells. **Forces a
change** means a stated term the portal does not satisfy (personal or private
use only, no reproduction in any form, no quotation without permission), or a
source that cannot be established for text the record quotes.

```
                            publishable   forces a change   unread at close
host_refuses        3            3              0                 0
archived_capture    2            2              0                 0
source_not_est.     9            4              2                 3
                   --           --             --                --
                   14            9              2                 3
```

**Named calls.** Both zh.wikisource records read `open_licence_stated`: CC
BY-SA 4.0 off the site footer, over a classical text that is itself public
domain. The academia.edu record reads `all_rights_reserved` or
`states_no_terms`, because the paper names no license, and it is publishable
under RULING 74. The two archived captures read one `states_no_terms` and one
`all_rights_reserved`.

**How it breaks.** If the nine records' text turns out to have come from the
English Wikipedia articles their citations point at, all nine establish fast,
all nine read CC BY-SA 4.0, and the two right-hand columns are zero. That is
the flattering direction, and it is the likeliest single way this prediction
is wrong.

## P2 — `data.js` over the wire

```
Brotli (what a current browser negotiates)    1.3 - 1.9 MB     below 2 MB: YES
gzip only                                      1.9 - 2.4 MB     below 2 MB: NO
the whole page, 11 files, Brotli              under 2.3 MB
```

Measured as bytes transferred from the deployed URL with the encoding forced,
not from a local compressor run. Cloudflare compresses at the edge, at a level
this repository does not choose.

## P3 — the deployed site against the local file

**Predicted: pixel-identical on all four tabs at 1600px and 390px**, measured
by screenshot diff in the same container Chromium, `file://` against the
deployed URL.

The start document names three ways it might not be. **All three are predicted
not to fire.** Relative paths and case-sensitive filenames have already been
exercised for Home's load (§0: zero failures on a Linux filesystem), and
Cloudflare is predicted to serve `.js` as JavaScript. **Tabs other than Home
have not been exercised yet**, and the 11-file inventory is predicted to hold on
all four: zero requests outside the 11 on any tab.

**The predicted first difference is in the address, not the pixels.**
Cloudflare Pages serves the page at `/` and redirects `/index.html` to it, so
anything that names `index.html` as where the page lives reads differently on
the host. There is a second difference, though not in the rendering: a stored
theme choice does not carry across, because `file://` and `https://` are
different origins.

## P4 — the harness, and the difference between disk and HTTP

**Predicted: no guard fails because the page is served, because no guard
touches HTTP.** The harness executes the page's functions in Node over files it
reads from disk, and serving the page changes nothing the harness reads.

**The sharper claim is the one to measure:** a list of every path that
`check_ui.mjs`, and anything it imports, opens, with each path classified as
deployed or not. **Predicted: at least one guard reads a file that is not
deployed**, at minimum `ui/data.manifest.json` (G10 in
`METHODOLOGY_FINAL_FLAGS.md` says guard 2h checks it). That does not break "the
deployed artifact is the checked artifact". It means the harness also checks
provenance the site does not carry, and the result document should say which
guards do.

**Also predicted: zero places in `index.html` branch on `location.protocol` or
`file:`.**

**Parity is then proven by bytes rather than asserted:** the SHA-256 of each of
the 11 files as fetched from the deployed URL, compared with the local file.
**Predicted: 11 of 11 identical.** If one differs, it is `index.html`, through
something the host injects (an analytics beacon or email obfuscation), because
HTML is the one file type a CDN edits.

## P5 — the OGIS collation, under RULING 98

```
africa-04 Silko   OGIS 201   the excerpt's letters are identical to OGIS; at
                             most punctuation or a diacritic differs. The Greek
                             field changes by 0 letters
africa-05 Adulis  OGIS 199   at least 3 character differences in the §62
                             excerpt, because PHI prints Wolska-Conus (1968-73)
                             and OGIS is older. The field changes
```

**Re-sourcing the Greek does not finish africa-04, and this is written down
before anyone opens it.** Its English is Satzinger's rendering on a personal
University of Vienna page, and its rights cell was read off PHI. Under RULING 96
the cell is for the material the record's quoted text comes from, and the
answers on this portal quote the English. **Predicted: that page states no
terms, and africa-04 needs a second reading in this block** that the fourteen do
not count. africa-05's English is McCrindle (1897, public domain) and needs
nothing.

## P6 — the record pass moves fingerprints, not citations

```
record files that change        at least 10: S10-S15, S17, the record-prose
                                half of FINDING 124, and africa-04/05
"1227 resolving to characters"  moves by at most 3, and only through africa-05
```

Titles and notes are not quoted fields, so editing them moves `content_hash`
without moving a resolved span. The only edit predicted to touch a quoted field
is africa-05's Greek.

## P7 — WRITTEN NOT TO FLATTER THE BLOCK

**The first public deploy does not happen in this thread.** Nine sources to
establish, a collation that is curator work at a scanned page, the second rights
reading P5 found, and a record pass that rebuilds `data.js` all come before it.
**Predicted: this block runs to at least two parts.**

**And the ruling in §2 of the start document will not be satisfied by reading
alone.** P1 predicts three of the fourteen still unread when everything else is
ready. The deploy then needs a ruling it does not have yet: publish with those
cells named as unread, which Methodology §2 already discloses, or withhold or
remove those records. **Predicted: that ruling gets asked for, and neither
option is free.**

---

# 3. WHAT WOULD MAKE THIS DOCUMENT WRONG IN A WAY WORTH KNOWING

- **P1 fails in the flattering direction** if the nine are Wikipedia text. That
  would mean nine records carried their provenance in `citation` all along and
  only their `citation_original` was missing.
- **P3 fails interestingly** if a tab other than Home loads something outside
  the 11. The inventory in `DEPLOY_START.md` §1 and G11's "It is 11" would both
  then have been measured on first load only.
- **P4 fails interestingly** if the page branches on protocol anywhere. "Not two
  things" would then be true of the bytes and false of the behavior.
