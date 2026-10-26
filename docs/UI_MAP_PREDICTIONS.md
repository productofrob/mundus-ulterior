# UI MAP PREDICTIONS — **WRITTEN AND COMMITTED BEFORE A LINE OF `ui/` WAS
# EDITED.** Ruling 78's practice. Scored, never amended.

*Written 2026-09-10, at `88d56c6`, after reading `ui/index.html` whole and after
rendering and using the Map tab at 1600px and at 390px. Every figure below is
measured on my own instrument at the open — **the figures in
`UI_QUESTIONS_START.md` §3A are the design block's instrument and are NOT
comparable with these.** Rob took the widest scope on both questions put to him:
a full Map tab layout pass, and both §9 debts landed in this block.*

*`RULINGS.md` read at the time: **next free ruling 90, next free finding 106.***

---

## THE STATE BLOCK IS GENERATED. NOTHING BELOW IT IS RESTATED.

`python scripts/state_block.py`, at `88d56c6`:

```
ingest.verify                        green, 54 documents
ingest.test_fidelity                 145   [green]
ingest.test_cost                     78   [green]
eval.test_answer_eval                425   [green]
eval.test_ranking_check              258   [green]
answer.test_answer                   150   [green]
ui/test_build_ui_data.py             19   [green]
scripts/test_recover_baseline.py     56   [green]
scripts/test_harnesses.py            43   [green]
python -m ingest.gazetteer --check   GREEN
node ui/check_ui.mjs                 GREEN
```

**`node ui/check_ui.mjs`: 47 checks, 0 failures, at the open.** FINDING 94's
pre-flight was done first and it mattered: without `psycopg` and `sqlglot` on the
bridge this block would have opened reading `scripts/test_recover_baseline.py` as
RED and `answer.test_answer` as 149, and neither is about the repository.

**One thing the next thread should not rediscover.** The harness needs
`ui/data.manifest.json` beside `ui/data.js`; a copy of `ui/` without it runs
**44 of the 47** and reports GREEN, silently skipping the three manifest checks.
The gate is the repository's 47, not a copy's 44.

---

# 1. THE INSTRUMENT, AND THE BASELINE IT READ

`ui/measure_map.mjs` — headless Chromium on Linux, where the serif stack falls
back. Its only job is to be the SAME instrument at the open and at the close.
Absolute document offsets, read out of the rendered page, never computed from
one another.

```
                    page   notice     map    mapH    svgH   panel    grid
1600px             10995      403     639     799     638    8206    8206
 390px             17557      274     980     464     148   17308   11547
```

And the defect, made concrete — click the first pin, then ask where the thing
that answers you is:

```
1600px   panel 8206px down a  900px viewport —  7306px BELOW THE FOLD, panel filled
 390px   panel 17308px down an 844px viewport — 16464px BELOW THE FOLD, panel filled
```

**§3A is confirmed on my own instrument and is worse than it was recorded.** The
panel fills correctly and is seven thousand pixels away from the person who
filled it.

---

# 2. FINDING 106 — **THE MAP NEVER SHOWS WHAT IS SELECTED, AND FOUR CSS RULES
# HAVE BEEN DRESSING A CLASS NOTHING APPLIES.**

Found by using the page, and then measured rather than asserted — the correction
in `UI_QUESTIONS_RULINGS.md` is about exactly this failure mode.

`ui/index.html` styles `.mapsvg .pin.hl`, `.mapsvg .pin.contested.hl`,
`.mapsvg .extent.hl` and `.mapsvg .edge.hl` in four rules. **`classList.add` is
called twice in the whole file and both times with `"dragging"`.** Nothing ever
adds `hl`.

So the screenshot of the Map tab before clicking a pin and the screenshot after
clicking it are **byte-for-byte the same file** (`md5 f1a6f70d…`, both). A
visitor clicks a marker; the page fills a panel seven thousand pixels below and
gives no sign on the map that anything was selected.

**This is RULING 85's argument in reverse.** 85 removed a handler for an element
that could no longer exist, because a handler nobody can test is dead wiring.
This is dead *styling* for a feature that was never wired — and unlike a dead
handler it is invisible, because CSS for a class that never arrives fails
silently.

**No check would have caught it and none should be asked to**, on the FINDING 102
principle: this is a fact about what changes on screen after a click. But a guard
CAN assert the class is applied to the right element once the class exists, and
P1 predicts one.

---

# 3. THE PREDICTIONS

## P1 — WHICH CHECKS GO RED, AND THE COUNT

**No check will be red at any commit left standing. The count goes 47 → 52.**

The five, named in advance:

```
GUARD 48   THE PANEL IS RENDERED BEFORE THE RECORD GRID, not after it. Asserted
           on the ORDERING of the two in viewPlaces' own markup — a relation,
           not a presence — so a later block that puts the panel back at the
           bottom fails on this rather than on a reader noticing

GUARD 49   EVERY VIEW THAT RENDERS A PANEL HAS ITS OWN EMPTY STATE, and no view
           falls back to another view's sentence. The SPAN_STATES / PROVENANCE
           pattern (checks 32 and 35): a table, and a guard that says the table
           covers everything the page can produce

GUARD 50   THE SELECTED THING IS MARKED ON THE MAP — after selecting a group,
           exactly one element in the SVG carries `hl` and it is that group's
           cache_key. FINDING 106's guard

GUARD 51   THE WITHHELD FAILURES ARE COUNTED ON DATA & SOURCES, and the count
           and the kind of each are re-derived from railPartition().withheld

GUARD 52   THE PARTIAL-ARCHIVE SUBSTITUTION IS STATED ON DATA & SOURCES, and
           its two figures are re-derived from runs.filter(r =>
           r.partial_passages)
```

**The prediction worth making is about check 28.** *"All 54 records are clickable
from the Places tab"* is the check genuinely at risk, because the region grid is
the largest thing on the tab and moving it is the largest thing I want to do —
and the obvious way to make room for the panel beside the map is to put the grid
somewhere it can be collapsed. **I predict it does not fire**, because
`regionCards()` will be relocated whole rather than rebuilt, exactly as
`QUESTIONS` was left unfiltered and the rail derived from it.

**And the standing claim, tested for the fourth block running:** not one
`data-*` check fires, though this block rewrites the Map tab's markup completely.
Checks 16–28 are the Map tab's own guards and they are all attribute-and-count
checks. If the freedom the design block claimed is real, this is where it is
proved; if it is not real, this is the block that finds out.

## P2 — WHAT THE PAGE MEASURES AFTERWARDS

```
                              OPEN      PREDICTED
1600px  panel below fold      7306      0 — in view without scrolling
 390px  panel below fold     16464      0
1600px  map y                  639      under 300
 390px  map y                  980      under 420
 390px  svg height             148      at least 300
 390px  page height          17557      down by 2000 or more
1600px  page height          10995      UP, by between 0 and 600
```

**The last line is the prediction constructed not to flatter, and it is the one
worth reading.** Every other line above says something improves. The Questions
block's P3 was built the same way, was the one prediction refuted, and the
refutation was worth more than the four that held — so this block owes one.

The reasoning: the panel is tall (`max-height: calc(100vh - 60px)`, and its
content routinely fills it), and putting it beside the map means the map's row is
now as tall as the taller of the two rather than as tall as the map. Nothing is
deleted by this block — the ledger, the cards and the grid all still exist and
still take their pixels. **A layout pass that moves things and deletes nothing
should get LONGER on a wide screen, not shorter, and a block that predicted every
figure improves has not predicted anything.**

The 390px case is different and is predicted down, because there the columns
already stack and the ledger's four cells are the whole first screen.

## P3 — WHAT I EXPECT TO ABANDON

Written now so it cannot be written afterwards as though it had been the plan.

```
1  THE GAP LISTS BEHIND A DISCLOSURE      EXPECT TO ABANDON. Same argument the
   (three placards + the all-gap card)    design block used against collapsed
                                          <details> for the region rail: hiding
                                          a list's whole content to save scroll
                                          it does not cost. These lists ARE the
                                          tab's argument — 90 placements the
                                          corpus names and will not draw

2  A STICKY MAP ON DESKTOP                EXPECT TO ABANDON. The panel is
                                          already sticky; two sticky columns
                                          fight for the same viewport and the
                                          loser is whichever the reader wanted

3  THE LEDGER MOVED BELOW THE MAP         EXPECT TO KEEP. 236px of apparatus
                                          about what the map cannot draw,
                                          standing above the map. RULING 85's
                                          test applied to this tab: does the
                                          figure describe the evidence on
                                          screen, or the archive around it

4  DROPPING THE LEGEND ON THE PHONE       EXPECT TO ABANDON. `ground` is told
                                          apart BY SHAPE and never by colour,
                                          and the legend is the only place the
                                          page says so. Dropping it to save
                                          250px would make a ruling unreadable
                                          to save scroll
```

## P4 — THE TWO §9 DEBTS, AND THE FIGURES THEY WILL PRINT

Derived from the bundle before any code, so the prediction is falsifiable:

```
PREDICTED   withheld failures                    2
PREDICTED   partial-archive runs                16   across  5 questions
PREDICTED   the rail partition, unchanged   24 / 7 / 2  of 33
```

**And the shape they land in.** The two withheld failures are not the same kind
of failure, and RULING 87's argument applies to them exactly as it applied to the
seven refusals: *"the evidence here does not answer this" is true of both and
useful about neither.* Measured:

```
Silla royal tomb glass    17 runs, ALL 17 REFUSED, gold declares it `answerable`
Ezanas gold coin          17 runs, NONE refused, not one quoting span in any of them
```

One is a system declining a question a person said it should be able to answer.
The other is a system answering and never once quoting. **I predict the line says
which is which**, and that saying so costs two clauses and is the whole value of
the line.

**RULING 86 is amended in the commit that lands this**, per §9 — it says the
count sits at the foot of the rail and it will not.

## P5 — WHAT THIS BLOCK WILL NOT DO

- **Not build the chatbot or a question box.** Still RULING 83.
- **Not curate a record. Not author a coordinate.** 54 in, 54 out; 63 drawn,
  90 not.
- **Not regenerate or hand-edit `ui/data.js`.** It will appear in no diff.
- **Not filter anything to tidy a layout.** The rail is a derived view of
  `QUESTIONS`; the region grid will be a relocated view of `regionCards()`.
- **Not relax or delete a guard.** Every new guard verified RED on a broken
  version before it is believed, and any guard that has to MOVE moves only to a
  surface carrying the same claim — RULING 88's test.
- **Not split the inline script.** Still one.
- **Not read a rights position.** The 38 unread still gate a public URL.
- **Not type a count into prose.** Every figure the two §9 debts print is
  derived, including the two that look like constants.

---

# 4. THE ONE THING THAT WOULD MAKE THIS BLOCK A FAILURE

Not a red check, and not a refuted prediction — a refuted prediction is the
instrument working.

**It is shipping a Map tab that measures better and reads worse.** Every figure
in P2 can be satisfied by making the map smaller and the panel narrower, and the
result would be a tab that scores well on an instrument I wrote and is worse to
use. The check on that is not in `check_ui.mjs` and cannot be: it is rendering
the page at both widths at the close and looking at it, which is how both of this
project's last two blocks found every defect the harness missed.
