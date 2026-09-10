# UI MAP REGIONS PREDICTIONS — **THE RESCOPE DOES NOT TOUCH THE REGION THE
# START DOCUMENT LEADS WITH, AND THAT IS THE FIRST THING TO WRITE DOWN.**
#
# **`UI_MAP_REGIONS_START.md` opens on East Asia: 3 of 9, and the corpus says
# the opposite. Rob has rescoped this block to cache GeoNames and place the
# nine locatable findspots. NONE OF THE NINE IS AN EAST ASIA RECORD. They are
# six Southeast Asia and three Scandinavia. After the whole curation half
# lands, East Asia is still 3 of 9 on the map, and the band is the only thing
# in this block that moves it.**

*Written 2026-09-10, before a line of `ui/` or `data/` was edited, and
committed before any of it. Ruling 78. Scored at the close in
`UI_MAP_REGIONS_RESULT.md` and **not amended there.***

---

# 0. THE STATE THIS IS PREDICTED AGAINST

`python scripts/state_block.py`, at `c5fd73e`, confirmed reproducing at the
open of this block:

```
ingest.verify                        green, 54 documents
node ui/check_ui.mjs                 GREEN, 53 checks, 0 failures
python -m ingest.gazetteer --check   GREEN
```

**AND MY OWN BASELINE ON `ui/measure_map.mjs`**, taken before anything moved.
Headless Chromium 1194 on Linux, and NOT comparable with a host browser — but
it reproduces `UI_MAP_RESULT.md` §1 P2's close figures to the pixel, so it is
the same instrument that block used:

```
width     page  notice     map    mapH    svgH   panel    grid   pins/ext
1600px   10240       —     403     652     456     403    7451     57/7
 390px   16903       —     318     464     148     820   11121     57/7

click the first marker: panel IN VIEW at both widths, filled,
0 thing(s) marked on the map      <- FINDING 106, still open, still true
```

**`pins/ext` reads 57/7 and there are 57 pins and SIX extents.** The
instrument's `.mapsvg .extent` selector also matches `text.lbl.extent`, so one
extent LABEL is counted as an extent. Recorded here rather than fixed, because
the instrument's worth is being the same instrument at the open and the close,
and this block did not write it.

**`RULINGS.md` reads next free ruling 91, next free finding 109**, read at the
open. Numbers are taken from the file at the time they are used, not from here.

---

# 1. P1 — THE CURATION HALF, AND WHAT IT DOES **NOT** FIX

**PREDICTED: the nine place 8 of 9, and the ninth is refused again.**

```
seasia-04-dong-yen-chau      VN    PLACES
seasia-05-my-son-b6          VN    PLACES
seasia-06-kedukan-bukit      ID    PLACES
seasia-07-talang-tuo         ID    PLACES
seasia-08-pong-tuk-lamp      TH    PLACES
scandinavia-05-thorsberg     DE    PLACES
scandinavia-06-tjurko        SE    PLACES
scandinavia-07-rycksta       SE    PLACES
seasia-03-khao-sam-kaeo      TH    REFUSED AGAIN, and predicted so in advance
```

**The ninth is `seasia-03-khao-sam-kaeo` and the prediction is that a dump does
not save it.** Its note already records GeoNames 8242723 examined and refused
on coordinate — a `T.HLL` at 8.016/100.1, which is not the excavated site.
Nothing about caching TH.zip changes that reasoning, and the failure mode here
is the block taking the id the second time round *because it wants nine*. If it
is placed, the reason will be a NEW candidate with its own evidence, and it
goes to Rob before it goes in the corpus.

**PREDICTED, and this is the one the start document's headline depends on:**

```
region              BEFORE            AFTER the curation half
East Asia           3 of 9  on map    3 of 9      UNCHANGED
Southeast Asia      3 of 9  on map    8 of 9      +5
Scandinavia         4 of 7  on map    7 of 7      +3
everything else     unchanged         unchanged
                    --------          --------
                    32 of 54          40 of 54
```

**`records whose placements are ALL gaps` goes 21 -> 13. `declared unplaceable`
stays 1.** The 90 undrawn placements fall by the number of gap placements those
eight records carry, which is 11 by my count and is the figure to check.

## AND THE MAP'S OWN EXTENT MOVES, WHICH IS THE TRAP

`mapBase()` fits the window to the cached coordinates with 3 degrees of pad.
**Two of the eight sit outside today's window**: Palembang at roughly 3 degrees
SOUTH, against a current `latMin` near 5 north, and Södermanland near 59 north
against a current `latMax` near 59. So:

```
                          NOW              PREDICTED
viewBox H                 388              487        (+25%)
1600px svgH               456              570..580
1600px page height      10240              10400..10900
 390px svgH               148              180..190
```

**H is `900 * latSpan / lonSpan` and I have predicted it from the coordinates I
expect, so if the coordinates land where I think and H does not, the arithmetic
is wrong and not the corpus.** FINDING 108 says a layout change resizes the
marks silently; **this is the reverse and is worse — the DATA changes the
layout**, with no layout edit anywhere to prompt anyone to run the instrument.

---

# 2. P2 — THE BAND, AND WHAT IT IS

**A band is not a boundary, not a placement, and not a coordinate this project
authored.** It is the region's home on the map: the space the map reserves for
the records this corpus files under that region and cannot draw as points.

```
POSITION  derived — the centroid of that region's own cached FINDSPOT ids.
          Never subject places. A record's subject places are mostly OUTSIDE
          its region: East Asia's reach Mesene at 47E, Sub-Saharan Africa's
          reach Rome. THAT IS THE PROJECT'S WHOLE ARGUMENT and it is exactly
          why a region's area cannot be derived from where its records point.
SIZE      a constant in viewBox units, declared in MARK beside the dot sizes,
          and it is FURNITURE. It asserts no extent and the legend says so.
SHAPE     a third visual language. Hatched strip, square chips, region name in
          the eyebrow treatment. Never a circle, never the extent's dashed
          accent rectangle. `ground` is told apart by shape and a band is not a
          `ground` at all.
```

**PREDICTED: no published source draws this project's seven regions, and the
block will not find one.** Checked before predicting: the UN M49 geoscheme puts
IRAN IN SOUTHERN ASIA WITH INDIA, and Arabia and the rest of Persia together in
Western Asia; Scandinavia is not an M49 unit at all. So M49 gives four of the
seven and collides two of the others. **§3's last bullet asked whether the seven
can meet the coastline's standard. The answer is no, and that is a finding, not
a formality.** The band exists because of it.

**PREDICTED: at least two of the seven bands cannot sit at their anchor.**
Arabia's findspot centroid and Sub-Saharan Africa's are about 8 degrees apart,
which is roughly 40 viewBox units at this scale, and a band holding six chips
is wider than that. A placement rule is needed and it must be DECLARED and
deterministic — the label collider's discipline, not a nudge someone tuned.

---

# 3. P3 — THE GUARDS. **WHICH GO RED, AND THE COUNT.**

**PREDICTED: 53 -> 57, and three existing checks go red on the way.**

```
GOES RED, BY DESIGN
  30  every tab with a panel has its own empty state, naming what it can select
      -> `region` is a new clickable kind. This goes red the moment a band is
         clickable and stays red until PANEL_EMPTY.map.selects carries it AND
         the sentence a visitor reads names it. That is the point of it.
  34  every figure in the geography ledger is re-derived
      -> the ledger's prose says "placements the corpus names and the map
         cannot draw". With bands the map SHOWS them, and the sentence becomes
         false. RE-POINTED, NOT RELAXED — RULING 88's test, and the re-pointed
         claim must be at least as strong.
  18  every cached point/extent (63) is drawn on the map
      -> moves to 63 + whatever the eight records add. It goes red on the data
         change, not on a UI change, which is the FINDING 108 shape again.

PREDICTED NOT TO FIRE
  28  all 54 records are clickable from the Places tab
      -> `regionCards()` is relocated whole, as it was three times last block.
  19  every drawable edge (19) is drawn on the map
      -> `drawable` keeps meaning BOTH ENDS HAVE A CACHED COORDINATE. A band
         edge is a different claim and gets its own guard rather than widening
         this one. If 19 moves it will be because the eight records made real
         edges drawable, which is a data change and correct.

THE FOUR NEW ONES
  54  every region has exactly one band, and its anchor is derived from that
      region's own cached findspot ids
  55  every record with no drawable placement appears exactly once, in its own
      region's band, and no record appears in two
  56  every edge drawn to a band ends at a band or a cached point, never at
      nothing, and is never drawn in the cached-coordinate edge's own style
  57  the band's size is declared once and the page draws that size
```

**EVERY ONE OF THE FOUR IS SEEN RED ON A BROKEN VERSION BEFORE IT IS BELIEVED.**
`UI_MAP_RESULT.md` §4 is why: guard 52 was written to check both ends of the
trail, four ways of breaking it went red, and the fifth stayed green. **A check
written and never seen red is a check nobody has any reason to trust.**

---

# 4. P4 — WHAT I EXPECT TO ABANDON

```
1  A REGION LAYER FROM A PUBLISHED SOURCE      abandoned. §2 says why, and the
                                               reason is a finding worth keeping
2  ANY HAND-DRAWN REGION SHAPE                 abandoned. A5's rule, untouched
3  RECLASSIFYING THE 21 BY READING GAP NOTES   abandoned. RULING 89
4  THE `not yet placed` BOX                    REMOVED, as Rob asked, and it is
                                               already empty: `P.unconsidered`
                                               is `[]`, so the box has been
                                               printing "none" at full width
```

---

# 5. P5 — THE PREDICTION BUILT NOT TO FLATTER THE BLOCK

**The bands will make the Map tab read WORSE at 1600px on their first render,
and Rob will reverse something about them in one message.**

The reasoning, so it can be scored on its mechanism and not on its mood: the
map's eastern half is empty and its western half is already dense. **The band
that is most needed is East Asia's, and East Asia is where the room is. The
bands that have nowhere to go are Arabia's, Persia's, South Asia's and
Sub-Saharan Africa's** — whose anchors all fall in the Red Sea and Gulf
corridor, which is the single most crowded part of this map and already drops
four labels to the collider. Adding four hatched strips and their chips there
will collide with the pins, the extents, the edges and each other.

`UI_MAP_RESULT.md` §2: the full-width map satisfied every figure that block
predicted and Rob reversed it one message later, and **the instrument said the
map was bigger and said nothing about it being worse.** The same instrument
will say seven more marks are on screen. It will not say the corridor is
unreadable.

**This is scored on the render and on Rob's first reply, not on a number.**

---

# 6. P6 — WHAT THIS BLOCK WILL NOT DO

- **Not author a coordinate.** The eight place from cached GeoNames ids or they
  do not place.
- **Not take a refused id to make a number.** `seasia-03-khao-sam-kaeo` above.
- **Not classify the 21 with a matcher over their notes.** RULING 89.
- **Not hand-edit `ui/data.js`.** `python ui/build_ui_data.py`, and FINDING 101
  before running it on Windows.
- **Not relax a check to fit a design**, and not re-point one at a weaker claim.
- **Not type a count into prose**, and not type a tab name.
- **Not build the chatbot.** RULING 83.
- **Not take the Methodology tab**, beyond re-pointing the ledger sentence that
  this block's own change makes false.
- **Not assign ruling or finding numbers from this document.**
