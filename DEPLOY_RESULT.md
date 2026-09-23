# DEPLOY RESULT — **MUNDUS ULTERIOR IS LIVE AT https://mundus-ulterior.pages.dev/,
# AND THE DEPLOYED ARTIFACT IS THE CHECKED ARTIFACT, BYTE FOR BYTE.**
#
# **Every rights cell was read before the URL existed, every known-wrong record
# was fixed before it went up, and the site is 0.66 MB over the wire.**

*Closed 2026-09-23. Scored against `DEPLOY_PREDICTIONS.md`, which was committed
first (cbc9ed2) under RULING 78 and has **not been amended since**.*

---

# 1. WHAT IS LIVE

```
address        https://mundus-ulterior.pages.dev/   (Cloudflare Pages, direct upload,
                                                    no repository attached; D3, D4)
files          11: index.html, data.js, banner/*.png x9 -- nothing else is loaded
source         ui/ at the commit that carries this document
byte parity    11 of 11 identical to the committed files, SHA-256 of the decoded
               bytes, measured in the browser after each of the three deployments
over the wire  index.html 128,080 B · data.js 366,900 B (Brotli; 9,784,003 B
               decoded) · nine PNGs 163,474 B · total about 658 KB
harness        63 ok, run by Rob on the host after every change
```

**Redeploying.** Rebuild `ui/data.js` if the corpus changed, run the harness,
copy the 11 files into `Claude outputs/mundus-ulterior-site/` (gitignored), then
in Cloudflare open **Workers & Pages**, then **mundus-ulterior**, then **Create
deployment**, choose **Production**, and drag in that folder. Check the SHA-256
of the published files against the local ones afterwards, as in §4.

---

# 2. WHAT THE BLOCK DID, IN ORDER

```
1  predictions and RULING 98 committed before anything was edited      cbc9ed2
2  RULINGS.md indexes 97-98; its next-free line true again              6754900
3  five bounded rights readings, confirmed by Rob                        ce15efd
4  nine records' sources established -- all through Wikipedia -- and
   RULING 99 says whose words a cell describes                           e08c978
5  three clause-2 publications read                                      2da17c7
6  the last cell (Thurgood, via JSTOR): 54 of 54 read, no URL yet        dcb41e7
7  the record pass: OGIS collation, S9-S18, spellings, RULING 100        c2409ea
8  FIRST DEPLOY, from c2409ea. 11 of 11 identical
9  Methodology full width (Rob's ruling) and the icon fix                c253b51
10 SECOND DEPLOY. 11 of 11 identical, icon request gone
11 license notice on Methodology (Rob's ruling), this document
12 THIRD DEPLOY. 11 of 11 identical
```

**Decisions Rob took in this block, every one put to him with a recommendation:**
record pass before the deploy (D1); PHI records re-sourced from OGIS (D2, RULING
98); Cloudflare Pages (D3); the host's default address (D4, against the
recommendation); the Hill translations all rights reserved; the Wikipedia pair
read off Wikipedia; the three shapes of RULING 99; three clause-2 cells;
reworded "exact characters" claims; Illerup and JSNab 17 kept and declared;
"English translation" labels; RULING 100 kept; Methodology full width; and a
single license notice on Methodology rather than a row on every record panel
(against the recommendation).

---

# 3. SCORING THE PREDICTIONS

```
P1  the fourteen readings: 9 publishable / 2 forced / 3 unread    REFUTED, in the
                                                                  flattering direction
                                                                  it named: 14 / 0 / 0
P1  named calls: zh.wikisource open; academia ARR or silence;     1 of 3: academia
    captures one silent, one ARR                                  CONFIRMED (ARR)
P2  Brotli below 2 MB                                             CONFIRMED
P2  Brotli 1.3-1.9 MB                                             REFUTED: 0.37 MB
P2  gzip-only 1.9-2.4 MB                                          NOT MEASURED
P2  whole page under 2.3 MB                                       CONFIRMED: 0.66 MB
P3  pixel-identical                                               NOT MEASURED AS
                                                                  PIXELS; text identical
P3  relative paths, case, and MIME do not fire                    CONFIRMED
P3  the first difference is the address (/index.html -> /)        CONFIRMED
P3  zero requests outside the 11                                  REFUTED on the host
P4  no guard fails over HTTP                                      CONFIRMED
P4  at least one guard reads a file that is not deployed          CONFIRMED
P4  zero protocol branches in index.html                          CONFIRMED
P4  11 of 11 byte-identical                                       CONFIRMED, three times
P5  Silko: letters unchanged, at most punctuation or a diacritic  PARTLY CONFIRMED
P5  Adulis: at least 3 differences                                CONFIRMED: exactly 3
P5  africa-04 needs a second reading, and Satzinger is silent     CONFIRMED
P6  at least 10 record files change                               CONFIRMED: 32
P6  1227 moves by at most 3                                       CONFIRMED: by 0
P7  the deploy does not happen in this thread                     REFUTED
P7  a ruling on unread cells is asked for                         REFUTED: none left
```

**P1 failed exactly the way it said it would.** "If the nine records' text turns
out to have come from the English Wikipedia articles their citations point at...
That is the flattering direction, and it is the likeliest single way this
prediction is wrong." All nine did. Two of the five "bounded" records did too,
and none of the three hosts on record as refusing refused. **The named calls
failed for a different reason than the numbers:** RULING 96, applied properly,
moved the cell for four of the five off the host the prediction was about.

**P2 was right about the threshold and wrong by a factor of four to five about the
size.** 9.78 MB compressed to 367 KB, a ratio of 26.7. The bundle is 685 archived
runs of highly repetitive JSON, and nothing in the prediction's reasoning
accounted for that. The gzip-only figure could not be measured: the session
container and the device VM both have the host refused by their egress, and a
browser cannot force an encoding.

**P3's pixel test was not available, and what replaced it is stated rather than
passed off.** The live site was reachable only from Rob's Chrome, and the local
file only in the container's Chromium, which are different renderers. What was
measured instead: the rendered text of all four tabs, with every `<details>`
open, hashed deployed against local. It is identical. **The prediction "zero
requests outside the 11" failed on the host, and not because of the page.**
Cloudflare Pages answers any path it does not hold with `index.html` and status
200. The browser's own automatic request for `/favicon.ico` therefore downloaded
the whole page a second time on every visit, 126 KB. An empty inline icon in
c253b51 stopped it, and the next deployment measured no such request. It also
means a mistyped address shows the portal rather than a 404. That is noted and
left.

**P4, the guards that read what the site does not carry.** `check_ui.mjs` reads
`ui/banner/manifest.json` and `ui/data.manifest.json`, neither deployed, and
walks `eval/answer_runs` and `data/seed_corpus` for its freshness guard. So "the
deployed artifact is the checked artifact" is true of the 11 files. The harness
additionally checks provenance the site does not publish.

**P5's miss is small and specific.** It said Silko's "letters" would not change.
The letters did not, but the first one changed case (OGIS prints Ἐγὼ). A capital
is not a diacritic, and the prediction did not allow for it.

**P7 was written not to flatter the block, and the block beat it.** It predicted
at least two parts and a deploy in a later thread, needing a ruling on unread
cells. The site went live in this thread with no unread cell. The closest call
was Thurgood (1999), a printed book with no copyright page reachable online,
which Rob closed by finding JSTOR's record of it.

---

# 4. RULINGS AND FINDINGS DECLARED

```
RULING 98   a source whose stated terms restrict use to personal study is not the
            source of any text the public portal carries (PHI -> OGIS)
RULING 99   the cell describes whoever wrote the words the record quotes: an
            intermediary's own prose -> the intermediary; a third party it quotes
            -> the third party's publication; no author named -> the intermediary,
            with the gap stated
RULING 100  an archived language code is read through a correction only where one
            is declared, per record and per code (JSNab 17: xna shown as arc)
FINDING 123 635 of 1,227 "resolved" spans do not hold their quote exactly
            (numbered here; Home and Questions reworded; offsets unchanged)
FINDING 124 the American-spelling sweep missed page copy and could not reach
            record prose (both fixed in the record pass)
FINDING 125 JSNab 17's English is an adaptation of O'Connor's, declared rather
            than corrected
```

Full text in `DEPLOY_RULINGS.md`. The rights readings are in
`DEPLOY_READINGS.md`, and the OGIS collation is in `DEPLOY_COLLATION.md`.

---

# 5. WHAT THE BLOCK LEAVES, NAMED

- **FINDING 123's offsets.** The claims are now true: a click lands on "the
  passage it quotes". About half the highlights still stop one or two characters
  short, and archived spans are never re-resolved. A render-time fix is possible
  and was not chosen.
- **JSNab 17's tier.** `verbatim_with_provenance` over a transliteration its own
  note calls "a paraphrase reconstruction" (FINDING 125, left open).
- **The license notice is generated, not derived.** It was built from
  `data/corpus_rights.json` on 2026-09-23 and sits in `ui/index.html`. A comment
  there says to regenerate it if a rights cell changes, and nothing enforces
  that.
- **`data.js` publishes every record in full,** including curator notes the page
  only excerpts. Those notes keep their British spelling and internal language.
  Anyone who opens `data.js` can read them.
- **Not measured:** gzip-only size, pixel identity, and whether a stored theme
  choice carries across origins. `measure_data.mjs` still cannot run on the
  device VM.
- **The address.** A productofrob.com subdomain can be added later as a CNAME in
  Squarespace's DNS. Nothing needs redeploying.

---

# 6. STATE AT CLOSE

```
HEAD            the commit that carries this document
harness         63 ok
rights column   54 of 54 read: open 18 · all rights reserved 15 · states no terms 8 ·
                permission 6 · two positions 3 · public domain 4 · unread 0
spans           1289 claimed · 1227 resolved
next free       RULING 101 · FINDING 126
```

## Starting point for the next thread

The portal is published. What remains is what `areas/ancient-history-ai-project`
has named since Block G: **the portfolio case study on productofrob.com**, which
should cover the scaling limit, the solutions, and the directions forward, and
link to the live site; and **the public GitHub release**. That release is the
repo-visibility decision this block kept separate, and it now has a live site to
point at. If the portfolio wants the site under its own domain, the CNAME in §5
is one step.
