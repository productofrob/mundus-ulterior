# UI METHODOLOGY PREDICTIONS — **THE PAGE ALREADY NAMES A FAILURE, AND IT IS
# THE WRONG ONE.**
#
# **`viewAbout`'s closing paragraph says "one question, on Aksumite trade, has
# failed to produce a grounded answer in every attempt under four different
# prompts". Measured against the archive as it stands: that question has 39 runs
# under FIVE prompt versions, 34 of them grounded and 2 of them showable — and it
# is NOT one of the two failures this tab owes a line about. The tab's only
# sentence about a failing question is about a third question, and it is stale in
# two places.**

*Written 2026-09-12, before a line of `ui/` was edited, and committed before any
of it. Ruling 78. Scored at the close in `UI_METHODOLOGY_RESULT.md` and **not
amended there**.*

---

# 0. THE STATE THIS IS PREDICTED AGAINST

`python scripts/state_block.py` and `python -m ingest.verify --state`, on the
host at `19cfba0`, confirmed reproducing before anything was edited:

```
ingest.verify                        green, 54 documents, 170 chunks
eight suites                         green
python -m ingest.gazetteer --check   GREEN
node ui/check_ui.mjs                 GREEN, 57 checks, 0 failures
RULINGS.md                           next free ruling 94, next free finding 115
                                     — 91-93 and 109-114 assigned this morning
```

**`ui/measure_map.mjs` in the session container**, Playwright and headless
Chromium 1194 on Linux, not comparable with a host browser — and it reproduces
`UI_MAP_REGIONS_RESULT.md`'s close figures to the pixel, so it is the same
instrument that block used:

```
width     page  notice     map    mapH    svgH   panel    grid   pins/ext
1600px    4175       —     403     954     618     403    1421     57/7
 390px    7098       —     318     790     201    1146    1386     57/7
```

**AND A SECOND INSTRUMENT, WRITTEN FOR THIS BLOCK, because `measure_map.mjs`
opens `#map` and this block is on `#data`.** Same widths, same browser. It reads
the tab's own layout and — the reason it exists — **what the address bar says
after a click**:

```
width     page   card1  notice   guide  guideH   rows (place/record/edge)
1600px    9031     403    1793     403     238   117 (65/22/30)
 390px   15896     578    3401     318     238   117 (65/22/30)

click a row, at BOTH widths, for ALL THREE kinds:
  the Guide is IN VIEW and FILLED          <- last block's phone fix holds
  the address bar says "#data"             <- and that is §4A, measured
```

**`UI_METHODOLOGY_START.md` §4A says "roughly seventy clickable rows". It is
117** — 65 placements, 22 records, 30 edges. Recorded here because the figure is
the argument for §4A and the start document under-counts it by two thirds.

---

# 1. P1 — THE TWO WITHHELD FAILURES. **WHICH TWO, AND WHICH KIND EACH IS.**

`railPartition()` returns them and nothing prints them. Measured from the
archive, before the line that will say so is written:

```
Where was the Roman glass from the Silla royal tomb made?
  hwangnam-glass-origin · East Asia · declared ANSWERABLE
  17 runs, 17 refused. Every run of it declined a question the project
  declared answerable.

What is shown on the gold coin of King Ezanas?
  aksumite-coin-imagery · Sub-Saharan Africa · declared ANSWERABLE
  17 runs, 0 refused, 5 grounded, and ZERO character spans claimed across
  all seventeen. It answers every time and quotes nothing, ever.
```

**PREDICTED: the line names both, and says which kind each is — one refused
throughout, one that never quotes — and does not merge them into "2 failures".**
This is the shape prediction carried forward unscored from the Map block, and it
is now scoreable.

**PREDICTED: the two kinds are more different than the count suggests, and the
second is the worse one.** A question that refuses seventeen times out of
seventeen is a system declining; a question that answers seventeen times and
claims no quotation is a system producing prose this project cannot check. The
first is RULING 87's territory wearing the wrong label. The second is the thing
the whole page exists to catch.

**PREDICTED: the line goes on the Methodology tab and NOT back on the Questions
rail.** RULING 86 owed a counted line at the foot of the rail; the Questions
block removed it and `viewQuestions`'s own comment records the debt. Putting it
back would re-open the argument that block settled — a visitor's first click
should not land on a question this corpus cannot answer — and the two failures
belong with the other two audits, not beside the questions they are not in.

---

# 2. P2 — THE THIRD QUESTION, AND IT IS A DEFECT RATHER THAN A DEBT

`viewAbout`'s closing paragraph, in force at `19cfba0`:

> *"And one question, on Aksumite trade, has failed to produce a grounded answer
> in every attempt under four different prompts, with the answer sitting in its
> own evidence in English. That is unexplained, and it is here rather than
> hidden."*

Measured on `What did Rome trade with the Kingdom of Aksum?`:

```
39 runs          five prompt versions: v1, v2, v3, v2r, v4
34 grounded      33 refused      22 spans claimed      2 showable runs
per version      v1 1/1 showable · v2 0/1 · v3 0/2 · v2r 1/32 · v4 0/3
```

**"Four different prompts" is five. "Failed to produce a grounded answer in
every attempt" is 34 of 39 grounded and 2 runs showable on the rail today.** The
sentence was presumably true when it was written and the archive grew underneath
it.

**PREDICTED: this is recorded as a FINDING and fixed in this block, and its
shape is FINDING 105's on a third surface** — a typed prose claim about the
archive, with no guard able to read a sentence. It is §4B's defect, found on the
closing paragraph rather than on the ledger, and found by reading the file whole
rather than by any check. That is the third and fourth stale sentence on this
tab and the third one a person found by reading.

**PREDICTED: the honest replacement is derived, not corrected.** Re-typing
"five" for "four" buys one archive growth. The figures come from the bundle, and
a guard re-derives them — RULING 87's pattern, guard 46's shape.

**AND THE UNCOMFORTABLE HALF: the page's only sentence about a failing question
is about a question that is IN THE RAIL, while the two it withholds go
unmentioned.** The debt and the defect are the same thing seen from two sides.

---

# 3. P3 — THE PARTIAL-ARCHIVE SUBSTITUTION

`renderPassageProvenance` shows a language and a region for runs reconstructed
from a partial archive, taken from the seed record rather than from the run, and
says nothing about it. The comment in the file records the debt and the figure.
Measured:

```
16 runs, across 5 questions, every passage of which carries no language
96 passages of 4,110 in the archive
What did ships carry from Muziris?                    3
How did Chinese sources describe the Roman empire?    3
What do the Vimose runes say?                         3
What did Rome trade with the Kingdom of Aksum?        4
When was the Antikythera mechanism built?             3
```

**PREDICTED: 16 across 5 is confirmed exactly, and the fifth question is the
Aksum trade question from §2.** Two of this block's three debts land on the same
question, and neither knew about the other before this document.

**PREDICTED: stating it on Methodology is NOT enough, and the block will find
that out by rendering.** The debt as written is *"the panel shows a language and
a region for those 16 runs without saying they came from the record"*. A
sentence on a different tab does not stop that panel making the substitution
silently. **PREDICTED: the panel gets a label too, and the Methodology line
carries the arithmetic.**

---

# 4. P4 — §4A, THE ADDRESS SPACE. **DECIDED IN WRITING FIRST, LIKE RULING 84.**

`hashOf` returns `#data` for this view and nothing more, for all 117 rows, at
both widths, measured above. **PREDICTED SCHEME**, declared in
`UI_METHODOLOGY_RULINGS.md` as RULING 94 rather than invented during the edit:

```
#data                          the tab
#data/place/<placement-key>    a placement, selected on Methodology
#data/record/<doc_id>          a record, selected on Methodology
#data/edge/<index>             an undrawn edge, selected on Methodology
```

**PREDICTED: the bare `#place/…`, `#record/…`, `#point/…` and `#edge/…` forms
are NOT touched, and still land on the Map tab.** Those are addresses this
project has handed out. RULING 84's whole argument is that a link must not
quietly mean something else later; changing which tab an existing address opens
is exactly that, and a new namespace costs nothing.

**PREDICTED: the kinds in the scheme are the kinds `PANEL_EMPTY.data.selects`
already declares — `place`, `record`, `edge` — and a guard asserts the two lists
agree.** That is the `--map-label` pattern on a third axis: the tab's selectable
kinds are declared once for guard 49 and once for the router, and something
checks they have not drifted.

**PREDICTED: `select()` is not where this goes.** `select()` calls
`repaintPanel()`, which calls `writeHash()`, which reads `hashOf(state)`. The
change is in `hashOf` and `applyHash` and nowhere else, and if it turns out to
need a third site that is a finding about the shape of the router.

---

# 5. P5 — THE GUARDS

```
PREDICTED   57 -> 61
```

```
NEW   the two withheld failures are named on Methodology, each with its kind,
      and both kinds are re-derived from the archive
NEW   the partial-archive line's two figures are re-derived (16 runs, 5
      questions), and the panel labels the substitution
NEW   every kind PANEL_EMPTY.data declares round-trips through hashOf and
      applyHash, and the bare forms still resolve to the map
NEW   every claim the closing paragraph makes about the near-failing question is
      re-derived from the archive
```

**PREDICTED: NO EXISTING GUARD GOES RED, and this one is written expecting to be
wrong.** Each of the last two blocks predicted specific guards red and was wrong
about which; guard 49 is the obvious candidate here and should not fire, because
the selectable kinds do not change. If 49 does fire it means the address work
changed what the markup emits, which would be a defect and not a success.

**PREDICTED: every new guard is seen RED first, by deliberately breaking the
code** — and at least one of the four is worthless until that happens. That has
been true in each of the last two blocks, twice in the regions block, and
FINDING 112 is the register entry for it.

---

# 6. P6 — **THE PREDICTION BUILT NOT TO FLATTER THIS BLOCK.**

**The first version of the address work will break something the harness cannot
see, and it will be found by rendering the page rather than by a check.**

The specific claim: **nothing in `check_ui.mjs` asserts that a hash ROUND-TRIPS.**
Guard 49 reads the markup, the trail guard reads a value after a sequence of
moves, and no guard has ever written a hash and read it back. So the failure
mode is a selection that writes an address the reader cannot paste back — or,
worse, one that resolves onto the Map tab because `applyHash`'s `record`,
`place` and `edge` branches all set `state.view = "map"` unconditionally and the
new branch forgets to. **That failure looks entirely correct in the source, is
green in the harness, and shows up the moment somebody copies a link.**

**And the second half, which is the unkind one: Rob will find at least one thing
on this tab that every figure in this document passed.** He found three in the
last block and two in the one before. The candidates, named in advance so the
prediction cannot be claimed afterwards: the Guide's 238-pixel height against a
panel that fills with a 20-row record list; the closing paragraph reading as an
apology once the two failures are stated properly above it; and the
`#data/place/<key>` addresses being long enough to be ugly when copied.

---

# 7. WHAT THIS BLOCK WILL NOT DO

- **Not touch the Questions rail.** The counted line goes on Methodology.
- **Not rewrite the two audits.** §4C is out of scope for this block and stays
  named as open.
- **Not build the ledger-prose guard as a general instrument.** §4B is answered
  for the closing paragraph specifically and the general hole stays open and
  recorded — a guard that can read any sentence is not a thing this block knows
  how to build.
- **Not relax a check to fit the design**, and not re-point one at a weaker
  claim. RULING 88.
- **Not type a count into prose, in digits or in letters.** FINDING 113.
- **Not author a coordinate.** Nothing in this block goes near a coordinate, and
  the promise is made flatly this time because it can be kept flatly.
- **Not hand-edit `ui/data.js`.** It is not regenerated either: nothing here
  changes the bundle.
- **Not build the chatbot.** RULING 83.
- **Not assign ruling or finding numbers from this document.** `RULINGS.md` is
  the authority; the numbers used here were read from it at 94 / 115 this
  morning and are declared in `UI_METHODOLOGY_RULINGS.md`.
