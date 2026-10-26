# UI MAP REGIONS RULINGS — **the register debt of a block that closed without
# paying it.**

*Written 2026-09-12, at the open of the Methodology block, from
`UI_MAP_REGIONS_RESULT.md` §8, which listed these nine as candidates "in the
order they were found, for whoever opens the next block". `RULINGS.md` was read
at the time: **the next free ruling number is 91 and the next free finding is
109.***

**THESE ARE NOT NEW DECISIONS.** Every one of them was made, built and guarded
in the regions block; what did not happen is the writing-down.
`UI_MAP_REGIONS_START.md` §6 forbade assigning numbers from a start document,
nothing since had done it, and the result document says so in its own §8. The
wording below is written from that document and from the code in force at
`19cfba0` — not reconstructed from memory, which is the practice `RULINGS.md`
refuses in its own note on rulings 20 and 21.

**Scoring note.** The regions block was scored REFUTED on two of the eight things
it promised not to do (`UI_MAP_REGIONS_RESULT.md` §6). Neither refutation is
softened here. Ruling 91 is the ruling that governs the authored coordinates, and
it is written as the rule they now live under rather than as a retrospective
permission for having authored them.

---

# RULING 91 — **A BAND'S POSITION DERIVES FROM ITS REGION'S OWN CACHED FINDSPOTS
# AND FROM NOTHING ELSE. A DECLARED ANCHOR IS PERMITTED, AND MUST SAY SO ON
# SCREEN.**

A region band is the space this map reserves for the records the corpus files
under a region and cannot draw as points. It is not a `ground`, not a boundary,
not a placement, and not an authored coordinate: A5's rule governs PLACEMENTS —
claims about where a record's place is — and a band is the map SAYING WHERE IT
KEEPS SOMETHING, the way a legend or a scale bar does. Its width is the number of
records in it and its height the number of rows they wrap into; neither has any
relationship to territory.

**The one number that is derived is the POSITION, and it derives from FINDSPOTS
ONLY.** That is the load-bearing half. A record's SUBJECT places are mostly
outside its own region, because a corpus about contact between Rome and elsewhere
is a corpus of texts pointing away from home: East Asia's subject places reach
Mesene at 47°E and Sub-Saharan Africa's reach Rome. A findspot is where the
object or the stone actually is, and is inside the region by construction. So a
band's anchor is the centre of the box holding that region's own cached
findspots, counted as DISTINCT SITES, and every corner of that box traces to an
id in `data/gazetteer.json`.

**A DECLARED ANCHOR IS PERMITTED**, and the conditions are the whole of the
ruling, because a declared anchor that looked like a derived one would be the
single worst thing this page could contain — the reader has no way to tell them
apart. A declaration must:

```
say "declared, not derived" in those words, in the band's own panel
print the derivation it overrules, so a reader can see what the corpus would
    have said
name its reason, written by the person who declared it
be named in the legend
sit inside the map's window, and be DRAWN on the declared point — the placer
    does not get a vote, because a declaration that gets nudged is not one
```

Guard 55 enforces every clause. Two anchors are declared at the time of writing
— `South Asia` at 79.0, 22.0 and `Southeast Asia` at 107.5, −1.5 — and both exist
for the same reason: **three of the seven regions have exactly one distinct
cached findspot, and the box holding one point is that point**, so the derivation
cannot run rather than running wrong.

**AND THE REFUTATION STANDS.** `UI_MAP_REGIONS_PREDICTIONS.md` §6 said *not
author a coordinate*, flatly, and two coordinates were authored. This ruling is
the rule they live under; it does not convert the refutation into a pass. Both
declarations are expected to become unnecessary — five of the Southeast Asian
records a GeoNames pass would place are findspots, and once cached the derived
anchor moves south on its own. The day it does, the entry should be deleted and
the band left to derive.

---

# RULING 92 — **EDGES ARE NEVER DRAWN TO A REGION BAND.**

**Both ends of every edge in this corpus sit inside ONE record**, and a band is
keyed to the record's region rather than to the place. An edge drawn from a
cached point to its own record's band would therefore assert that the place at
its far end is in that region: for the Chinese histories, that is Rome in East
Asia — the mirror of the refusal those records make in their own notes, and the
map contradicting its own best sentence. Thirteen of the thirty undrawn edges
would also have collapsed to zero length inside a single plate.

**MARKING IS A WEAKER CLAIM THAN DRAWING, AND THAT IS WHY IT IS THE HONEST ONE.**
Selecting an undrawn edge marks the end that has a coordinate and the square
where the map keeps the record, and draws no line between them. It says *here is
the end that has a coordinate, and here is where the map keeps the record that
names the other one*, and asserts no route.

Four cases, and the panel distinguishes all four rather than printing one
sentence over them:

```
both ends resolve, record has a square      ends marked, and the square
one end resolves, record has a square       that end marked, and the square
one or both resolve, record has no square   the resolving end(s) only
neither resolves, record has no square      "nothing on the map marks this edge"
```

The fourth was got wrong first — the page described a square for a record that is
drawn as points elsewhere and therefore has none — and was found by clicking one.
Guard 19 asserts that every undrawn edge names both ends, says what the map
marks, carries the curator's own refusal verbatim, and **never promises a square
its record does not have**.

---

# RULING 93 — **ONE COMMIT MESSAGE PER COMMIT, IN ITS OWN `commit-<topic>.txt`,
# AND THE INSTRUCTION HANDED TO THE HOST NAMES EVERY FILE THE COMMIT TOUCHES.**

The repository's own convention: `.gitignore` covers `commit-*.txt` at line 33
and the root holds two hundred of them. This makes the convention a rule, because
departing from it cost real work.

**What happened.** The regions block wrote every round's message to one reusable
filename, and each round overwrote the previous description before it had been
committed. **Three rounds of work collapsed into one commit wearing the last
round's words, and one commit shipped describing a change it did not contain.**

```
one file per commit           commit-<topic>.txt, a topic per round
never reused                  a message is not overwritten before it is committed
names every file              the instruction handed to the host lists them all
```

The last clause is not bookkeeping. While the bridge shell is down
(`UI_METHODOLOGY_START.md` §7) the session cannot run `git`,
so a commit is a set of edits written through the file bridge plus an instruction
a person carries out. An instruction that does not name every file is an
instruction whose `git add` can silently miss one, and the session has no way to
see that it did.

---

# FINDING 109 — **an SVG `<pattern>`'s contents do not take their paint from this
# page's classes.**

The band hatch was an SVG `<pattern>`. `getComputedStyle` on the rect inside the
pattern reported `rgb(255,255,255)` from `var(--card)` and on the line
`rgb(138,133,124)` from `var(--ink-faint)`, **exactly as authored** — and the
paint filled every band SOLID BLACK, which is `fill`'s initial value. Injecting
`fill:#ff0000 !important` on the pattern's own child changed nothing on screen.

**The style system and the raster disagreed, and only the screenshot knew.** Same
family as the `mask-image` defect recorded on `.spec`: a technique that is correct
in the DOM and wrong in the paint. The hatch is ordinary clipped lines now —
elements the stylesheet actually reaches — and there is no paint server on this
map.

---

# FINDING 110 — **a band clamped to the canvas edge replaces its derivation with
# "wherever the edge is", and does so silently at every zoom level.**

The band placer clamped a band with nowhere clear to go back inside the canvas.
Zoom in twice and EVERY band's anchor leaves the window, so every band was pinned
to whichever border it had been pushed against — Scandinavia's in the corner of a
view of the Gulf, Sub-Saharan Africa's and Arabia's stacked on the left edge, each
sitting on geography it has no relation to.

**A band's position is the ONLY thing about it derived from the corpus**, and
clamping silently replaced that derivation. A pin outside the window is drawn
outside the window and clipped; a band is treated the same way now, because it is
making the same kind of claim about where it is. Off-screen and honest beats
on-screen and wrong, and nothing is lost — every record in a band is also in the
region grid below.

**Found by Rob, on a zoomed map.**

---

# FINDING 111 — **a stroke is hit-tested at the width it is DRAWN, and six edges
# in this corpus are shorter than the marks at their own ends.**

An edge is drawn at 1.4 viewBox units — about 1.7 CSS pixels at 1600px and half a
pixel on a phone, thinner than a cursor's own hotspot. Every edge on this map had
been clickable in principle and unhittable in practice since A5. **Found by Rob,
who could not select one.**

**And the obvious fix was half a fix.** An invisible `.hit` line at `--edge-hit`
units carries the click; measured afterwards, that reached **10 of 19**. Six edges
are shorter than the two dots they connect — `Coloe → Adulis` is 3.9 units between
radii of 8 and 10.5, so the line is entirely underneath its own endpoints — and
two are identical `Ganges → Muziris` edges from different records drawn on top of
each other, so one can never be the thing the pointer finds. Hence the endpoint
lists: every edge is listed on the panel of both places it joins.

---

# FINDING 112 — **a guard that recomputes from the constant it is checking agrees
# with itself.**

Guard 56 was written to assert that a band's plate is the size its contents
declare, and it derived the expected width from the same constant the page draws
with. **Putting back the exact defect that had shipped left it GREEN.**

The fix is the `--map-label` pattern one shape over: declare the value twice —
once in the stylesheet as `--band-label`, once in the script as `BAND.namePx` —
and check that the two agree. A guard has to have something to check other than a
number agreeing with itself.

**This is the third time on this project that a red test found the hole in the
guard rather than in the code, and every one was found by deliberately breaking
the code.**

---

# FINDING 113 — **a typed count in letters passes a guard that hunts digits.**

Guard 2g hunts specific literals in digits. The contested-coordinate card carried
*"right for TWO of these placements"*, beside a figure that was derived — a typed
count wearing letters, through four blocks, invisible to the guard that exists to
find exactly that defect. The rule that follows: **not a count in prose, in digits
OR in letters.**

---

# FINDING 114 — **three rounds of work collapsed into one commit because every
# message was written to one reusable filename and each round overwrote the
# last.**

The mechanism, recorded separately from RULING 93 because the ruling says what to
do and this says how it fails: a message file written before the commit and
overwritten before the commit is made leaves no trace of what it said. Three
rounds went in as one commit wearing the last round's words, and one commit
shipped describing a change it did not contain. Nothing in the tree shows this —
the evidence is a commit log that disagrees with its own diffs.
