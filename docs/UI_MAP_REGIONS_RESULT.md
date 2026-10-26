# UI MAP REGIONS RESULT — **THE PREDICTIONS ARE SCORED AND NOT AMENDED, AND
# TWO OF THE EIGHT THINGS THIS BLOCK PROMISED NOT TO DO, IT DID.**
#
# **IT AUTHORED TWO COORDINATES, AND IT TOOK THE METHODOLOGY TAB. Both at Rob's
# instruction, both labelled on screen, both guarded — and both refuted on the
# wording of §6, which carved out no exception for either.**

*Written 2026-09-11 at the close. `UI_MAP_REGIONS_PREDICTIONS.md` was committed
at `3ceafdb` **before a line of `ui/` or `data/` was edited** and is not amended
here — it is scored.*

---

## THE STATE AT THE CLOSE

```
node ui/check_ui.mjs      GREEN, 57 checks, 0 failures   (53 at the open)
ui/data.js                NOT REGENERATED and in no diff. 54 records in, 54 out
RULINGS.md                next free ruling 91, next free finding 109 — UNCHANGED
```

**`ui/measure_map.mjs`, same instrument at both ends:**

```
width      page   notice    map    mapH   svgH   panel   grid   pins/ext
OPEN
1600px    10240        —    403     652    456     403   7451      57/7
 390px    16903        —    318     464    148     820  11121      57/7
CLOSE
1600px     4175        —    403     954    618     403   1421      57/7
 390px     7098        —    318     790    201    1146   1386      57/7
```

**The Map tab is 59% shorter at 1600px and 58% shorter on a phone**, and the
record grid moved from 7451 pixels down the page to 1421. Neither was predicted;
both are consequences of Rob moving five cards off the tab.

**`0 thing(s) marked on the map` at the open, `1` at the close, at both widths.**
FINDING 106, closed.

---

# 1. P1 — THE CURATION HALF. **ABANDONED, AND THE HALF THAT WAS SCORABLE IS THE
# HALF THAT MATTERED.**

**The curation never ran.** Rob rescoped this block to cache GeoNames and place
the nine locatable findspots on 2026-09-10, and dropped it on 2026-09-11 after
asking what it was for. So:

```
8 of 9 place                              UNSCORED — and now unscoreable here
seasia-03-khao-sam-kaeo refused again     UNSCORED
21 gaps-only records -> 13                UNSCORED. It is still 21
```

**Recorded as ABANDONED, not as passed.** A prediction that never got the chance
to be wrong is not a prediction that held.

## AND THE ONE THAT DID SCORE IS THE ONE THE BLOCK TURNED ON

> *"NONE OF THE NINE IS AN EAST ASIA RECORD. After the whole curation half lands,
> East Asia is still 3 of 9 on the map, and the band is the only thing in this
> block that moves it."*

**CONFIRMED, and it became the reason the curation was dropped.** When Rob asked
why the work was needed, that sentence — written before any of it — was the
answer: his goal was every source on the map, the bands had already met it, and
the curation would have moved **zero** records onto the map.

## THE MAP'S EXTENT MOVED. **RIGHT MECHANISM, WRONG CAUSE.**

The prediction was that placing the eight would push the window south and make
the viewBox 25% taller, because `mapBase()` fits the window to the cached
coordinates. The eight never placed. **The window moved anyway, and further**,
because `mapBase()` had to be taught to fit something the prediction had not
imagined: a declared band anchor three degrees south of anything this corpus has
cached.

```
1600px svgH    predicted 456 -> 570..580      actual 456 -> 618
 390px svgH    predicted 148 -> 180..190      actual 148 -> 201
```

Both figures land **outside** the predicted band, in the predicted direction, for
a cause the prediction did not name. Scored REFUTED on the numbers. The
underlying claim — *a change to the coordinates the map fits is a silent change
to its layout, with no layout edit anywhere to prompt anyone to measure* — held
exactly, and is FINDING 108 running in reverse.

---

# 2. P2 — WHAT A BAND IS. **BOTH HALVES CONFIRMED.**

**"No published source draws this project's seven regions, and the block will not
find one." CONFIRMED, and checked rather than assumed:** the UN M49 geoscheme
puts **Iran in Southern Asia with India**, Arabia with the rest of Western Asia,
and has no unit called Scandinavia. Four of the seven, two of them collided.
`UI_MAP_REGIONS_START.md` §3's last bullet asked whether the seven could meet the
coastline's standard. The answer is no, and it is why a band is not a boundary.

**"At least two of the seven bands cannot sit at their anchor." CONFIRMED on the
first render** — and the count moved three times as the placer was tuned: four
crowded, then one, then none once the window grew. The reasoning given in advance
was the right one: Arabia's findspot centroid and Sub-Saharan Africa's are about
eight degrees apart and a six-record band is wider than that.

---

# 3. P3 — THE GUARDS. **THE COUNT IS EXACTLY RIGHT AND THE COMPOSITION IS NOT.**

```
PREDICTED   53 -> 57        ACTUAL   53 -> 57     CONFIRMED, to the number
```

**And that is the least interesting kind of correct.** Three of the four new
guards are roughly what was predicted; what the prediction could not see is that
**four EXISTING guards were re-pointed and strengthened**, none of them named:

```
19   widened TWICE — a hit target, then reachability from both endpoints, then
     the four cases an undrawn edge's panel has to distinguish
52   extended to cover the Guide's home button
2g   gained the literal it had never been able to see
49   went red on `region`, as predicted, and again when `place` came off `map`
```

**Of the three predicted to go red:**

```
30/49  every tab's empty state names what it can select     RED, as predicted
34/53  every figure in the geography ledger is re-derived   DID NOT FIRE
18     every cached point/extent is drawn                   NEVER MOVED
```

**Guard 34 is the interesting miss.** It was predicted red because the ledger's
prose would become false — and it did become false, twice. The guard never saw
it, because **it checks the ledger's FIGURES and cannot read its sentences**. The
stale pointer was caught by a person reading the page, which is the same hole
FINDING 105 named on the cross-tabulation and the same one RULING 90 exists for.
Predicting it red was right about the defect and wrong about the instrument.

Guard 18 never moved because nothing was curated. UNSCORED.

**Predicted not to fire: 28 and 19.** Guard 28 CONFIRMED — `regionCards()` was
relocated whole, twice more, and never fired. Guard 19 did not fire either, but
only because it was rewritten by hand three times; scoring that as a pass would
be generous to the point of dishonesty.

**EVERY NEW GUARD WAS SEEN RED FIRST, and two were worthless until that happened.**
Guard 56's first version recomputed the plate width from the same constant
`buildMap` draws with, so the two moved together: putting back the exact defect
that had shipped left it GREEN. The 2g literal matched a single space while the
page's template strings wrap, so it read its own assumption rather than the page.
**That is the third and fourth time on this project that a red test found the
hole in the guard rather than in the code.**

---

# 4. P4 — WHAT THE BLOCK EXPECTED TO ABANDON. **ALL FOUR, AS PREDICTED.**

```
1  A REGION LAYER FROM A PUBLISHED SOURCE   abandoned, and §2 is the finding
2  ANY HAND-DRAWN REGION SHAPE              abandoned. No polygon was authored
3  RECLASSIFYING THE 21 BY THEIR NOTES      abandoned. RULING 89 untouched
4  THE `not yet placed` BOX                 removed, and it was already empty
```

---

# 5. P5 — THE PREDICTION BUILT NOT TO FLATTER THE BLOCK. **CONFIRMED ON ITS OWN
# STATED MECHANISM, ON THE FIRST RENDER.**

> *"The bands will make the Map tab read WORSE at 1600px on their first render,
> and Rob will reverse something about them in one message. The band that is most
> needed is East Asia's, and East Asia is where the room is. The bands that have
> nowhere to go are Arabia's, Persia's, South Asia's and Sub-Saharan Africa's,
> whose anchors all fall in the Red Sea and Gulf corridor."*

**Exactly those four, exactly there, on the first render.** PERSIA's name sat
across Ctesiphon and the Ka'ba, SOUTH ASIA's across Sri Lanka, SUB-SAHARAN
AFRICA's across A(u)xoume. And Rob did not reverse one thing in one message — he
corrected the design **three times**: Southeast Asia's position, South Asia's
position, and the clamp that pinned every band to a border under zoom.

**This is the second block running in which the prediction written to be unkind
to the block was the one worth having.**

---

# 6. P6 — THE EIGHT THINGS THIS BLOCK SAID IT WOULD NOT DO. **SIX HELD. TWO DID
# NOT, AND THEY ARE THE ONLY PART OF THIS DOCUMENT THAT MATTERS.**

```
HELD
  not take a refused id to make a number    khao-sam-kaeo was never touched
  not classify the 21 with a matcher        RULING 89 intact
  not hand-edit ui/data.js                  in no diff, at all
  not relax a check to fit a design         four were re-pointed, none weakened
  not build the chatbot                     RULING 83 intact
  not assign ruling or finding numbers      RULINGS.md still reads 91 / 109
```

## **REFUTED: "NOT AUTHOR A COORDINATE."**

`REGION_ANCHOR` holds two coordinates that were typed by hand:

```
"Southeast Asia"  [107.5, -1.5]   between Sumatra and Borneo
"South Asia"      [ 79.0, 22.0]   central India
```

**There is a defence and it is not a complete one.** A5's rule governs
PLACEMENTS — claims about where a record's place is — and a band anchor is not a
placement; the page says "declared, not derived" in those words, prints the
derivation it overrules, names the regions in the legend, and guard 55 enforces
all of it. Both were Rob's instruction, and both exist because three of the seven
regions have exactly one distinct cached findspot, so the derivation could not
run rather than running wrong.

**And §6 carved out no exception.** It said *not author a coordinate*, flatly, and
two coordinates were authored. **Scored REFUTED.** The honest reading is that the
prediction was written about the curation half and was allowed to stand as a
general promise it could not keep — which is a defect in the prediction, and the
right response is to score it rather than to explain it away.

## **REFUTED: "NOT TAKE THE METHODOLOGY TAB."**

The clause allowed exactly one thing: *re-pointing the ledger sentence that this
block's own change makes false*. What the block actually did to that tab:

```
moved five cards onto it        the contested id, the focus gaps, the gap lists,
                                the undrawn edges, the declared-unplaceable card
gave it its own Guide           `.cols-panel`, a sticky panel, `panelNav`
gave it its own empty state     `PANEL_EMPTY.data`, which guard 49 demanded
fixed its phone layout          the Guide had landed 15,615 pixels down
```

At Rob's explicit instruction, and the tab is better for it. **Refuted all the
same.** The two §9 debts that were "owed to Methodology, next-but-one" are still
owed, and now that tab has been half-rebuilt by a block that promised not to
touch it — which is precisely the mess §6 existed to prevent.

---

# 7. WHAT LOOKING CAUGHT THAT NO CHECK WOULD HAVE

**Five, and Rob found two of them.**

- **An SVG `<pattern>`'s contents do not take their paint from this page's
  stylesheet.** `getComputedStyle` on the rect inside the pattern reported
  `rgb(255,255,255)` from `var(--card)` and on the line `rgb(138,133,124)` from
  `var(--ink-faint)`, exactly as authored — and the paint filled every band
  SOLID BLACK, which is `fill`'s initial value. `fill:#ff0000 !important` on the
  pattern's own child changed nothing on screen. **The style system and the
  raster disagreed, and only the screenshot knew.**
- **The band placer clamped to the canvas edge.** Zoom in twice and every band's
  anchor leaves the window, so every band was pinned to whichever border it had
  been pushed against, sitting on geography it has no relation to. **Found by
  Rob, on a zoomed map.**
- **An edge is hit-tested at the width it is DRAWN** — 1.4 viewBox units, about
  1.7 CSS pixels, thinner than a cursor hotspot. Every edge had been clickable in
  principle and unhittable in practice since A5. **Found by Rob.** And the
  obvious fix was half a fix: measured afterwards, 10 of 19. Six edges are
  SHORTER THAN THE TWO DOTS THEY CONNECT.
- **`BAND.nameCharW` was measured for lower-case type** and `.bname` is uppercase
  and tracked, so the longest region name ran off its own plate.
- **A typed count wearing letters.** "right for TWO of these placements", beside
  a figure that was derived, through four blocks, invisible to a guard that hunts
  digits.

---

# 8. WHAT THIS BLOCK OWES THE REGISTER

**Nothing was assigned. `RULINGS.md` reads next free ruling 91, next free finding
109, unchanged since the open**, because `UI_MAP_REGIONS_START.md` §6 forbade
assigning numbers from a start document and nothing since has done it. These are
the candidates, in the order they were found, for whoever opens the next block:

```
RULINGS
  a band's position derives from its region's own cached FINDSPOTS and from
  nothing else; a DECLARED anchor is permitted, and must say "declared, not
  derived" on screen, print the derivation it overrules, and be named in the
  legend

  edges are never drawn to a region band: both ends of every edge in this corpus
  sit inside ONE record, and a band belongs to the record rather than to the
  place, so the line would assert that the place at its far end is in that region

  a commit message is written to `commit-<topic>.txt` — the repository's own
  gitignored convention — one file per commit, and the instruction handed to the
  host names EVERY file the commit touches

FINDINGS
  an SVG `<pattern>`'s contents do not take their paint from this page's classes
  a band clamped to the canvas edge replaces its derivation with "wherever the
    edge is", and does so silently at every zoom level
  a stroke is hit-tested at the width it is drawn, and six edges in this corpus
    are shorter than the marks at their own ends
  a guard that recomputes from the constant it is checking agrees with itself
  a typed count in letters passes a guard that hunts digits
  three rounds of work collapsed into one commit because every message was
    written to one reusable filename and each round overwrote the last
```

---

# 9. FOR WHOEVER OPENS THE NEXT BLOCK

- **The bridge shell is gone and it is not coming back on its own.** A Windows
  update released 2026-09-08 stops Claude's Linux workspace reaching the
  repository. The file bridge works; `git` and anything corpus-wide runs on the
  host. `UI_METHODOLOGY_START.md` §7 is the runbook.
- **`ui/measure_map.mjs` still needs Playwright and a headless Chromium**, which
  means the session container, which means staging `ui/` there. The figures in
  this document are that instrument and are NOT comparable with a host browser.
- **A selection made on Methodology is not in the address bar.** `hashOf` returns
  `#data` for that view. Now that the tab has a Guide and roughly seventy
  clickable rows, that is a real gap and it is the first thing on the next
  block's list.
- **The two §9 debts are still owed to Methodology**, untouched by this block:
  the two withheld failures with RULING 86's amendment, the partial-archive
  substitution, and the Home "the failures are kept" line.
- **The map at 390px is no longer the largest thing outstanding.** It was a
  148-pixel postage stamp; the taller window has taken it to 201, and the tab as
  a whole is 58% shorter. It is still small.
