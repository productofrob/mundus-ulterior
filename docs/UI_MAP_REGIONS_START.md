# UI MAP REGIONS START — **EVERY RECORD, FINDABLE ON THE MAP BY REGION, IN A
# WAY THAT IS USEFUL TO A VISITOR.**
#
# **THE MAP SHOWS 32 OF THE 54 RECORDS, AND THE 22 IT DOES NOT ARE NOT A
# BACKLOG: THEY ARE CONCENTRATED IN THE REGIONS WHOSE EVIDENCE IS TEXTUAL. East
# Asia is 3 of 9 and Southeast Asia is 3 of 9, because 大秦 and 拂菻 are Chinese
# names for the Roman world itself and this corpus refuses to pin them. A
# visitor reading the map concludes Rome's contact with East Asia was thin. The
# corpus says the opposite.**

*Written 2026-09-10 at the close of the Map block, for the thread that solves
regions. **Every figure here was measured at that close; none is inherited.**
The first thing the new thread does is confirm the state block still
reproduces — if it does not, stop and find out what moved.*

---

# 1. WHERE THE PROJECT IS

**The Map block closed clean over thirteen commits.** `UI_MAP_RESULT.md` scores
its predictions and is worth reading whole before this document's §4; its §2 in
particular, because the failure mode that block named in advance actually
happened and a person caught it, not the instrument.

```
54 records        169 placements      63 points and extents drawn, 90 not
7 regions         685 archived runs   53 checks green, eleven instruments green
```

**`RULINGS.md` is the authority: next free ruling 91, next free finding 109.**
Read it at the time anyway.

---

# 2. THE PROBLEM, MEASURED

## A. HOW MANY RECORDS REACH THE MAP AT ALL

```
records with at least one DRAWN placement   32
records whose placements are ALL gaps       21
records with no placements at all            1   (declared unplaceable)
                                            --
                                            54
```

## B. AND THE ASYMMETRY IS THE FINDING

```
region                total   on the map   gaps only   none
Arabia                    8            7           1      0
South Asia                7            6           1      0
Sub-Saharan Africa        7            6           1      0
Scandinavia               7            4           3      0
East Asia                 9            3           6      0
Southeast Asia            9            3           6      0
Persia                    7            3           3      1
```

**East Asia and Southeast Asia are the two largest regions in the corpus and the
two thinnest on the map.** Read the gap reasons and the cause is not a backlog:

```
eastasia-05-liangshu-qin-lun    大秦, the country the merchant comes FROM
eastasia-07-tang-huiyao         拂菻, the Tang name for Byzantium
eastasia-08-songshi-fulin       拂菻 is the Chinese name for the Byzantine…
eastasia-09-jiutangshu-fulin    `Fu-lin` and `Ta-ts'in` name a state and its people
eastasia-02-hou-hanshu          日南, the commandery on the Vietnamese coast
southasia-05-brihatsamhita      the Greek-speaking Mediterranean world as Sanskrit names it
```

**These are the corpus refusing to plot a polity as a town, which is correct and
is the project's own argument** — *"an office is not a city, a people is not a
place, and an empire is not the town on the Tiber."* The records are not
missing. The MAP'S UNIT IS THE PLACE AND THE CORPUS'S UNIT IS THE RECORD, and
where a record's geography is a whole civilisation seen from three thousand
miles away, the two do not meet.

**A second and different population is mixed in with them**, and telling the two
apart is the first real piece of work:

```
scandinavia-05-thorsberg-chape   seasia-03-khao-sam-kaeo   seasia-05-my-son-b6
scandinavia-06-tjurko-bracteate  seasia-06-kedukan-bukit   seasia-07-talang-tuo
scandinavia-07-rycksta-grikkium  seasia-04-dong-yen-chau   seasia-08-pong-tuk-lamp
```

Every one of these is a real, locatable findspot that no gazetteer entry could
be resolved for honestly. **That is a curation question and it is NOT this
thread's to answer** (§6), but a design that treats both populations the same
will be wrong about one of them.

## C. WHAT THE MAP CURRENTLY KNOWS ABOUT A REGION: NOTHING

**This is the constraint that shapes every option.**

```
regions on a RECORD          Arabia, East Asia, Persia, Scandinavia,
                             South Asia, Southeast Asia, Sub-Saharan Africa
regions on a PLACEMENT       NONE. A placement carries no region at all
region SHAPES in the bundle  NONE. `P` holds docs, edges, groups, unconsidered,
                             declared_unplaceable, uncached, shape_problems, stats
the only shapes drawn        six Pleiades extents — Italia, Limyrike, Pandion,
                             Indoskythia, Libanophoros Chora, Thamydenoi — and
                             not one of them is a project region
```

So the map draws placements; placements do not know their region; the region is
a property of the record one level up. **Any answer has to bridge that, and the
bridge is the design.**

---

# 3. THE RULES THAT CONSTRAIN THE ANSWER, AND THE ONE PRECEDENT

**Read these before designing anything. Three of them will kill an obvious idea.**

- **COORDINATES ARE NEVER AUTHORED.** A5's rule, and the reason every point on
  this map traces to a cached gazetteer id. Seven hand-drawn region blobs are
  the single most obvious answer to this brief and they are refused by it.
- **`ground` IS A CATEGORY, NOT A STRENGTH, AND IS TOLD APART BY SHAPE.** A
  `regional` claim draws as a shaded area and NEVER as a pin. Anything that makes
  a region look like a bigger version of a point re-creates the exact defect A5
  exists to refuse.
- **A RULE THAT HAS TO BE INTERPRETED IS A RULE THAT WILL BE BROKEN, AND INSIDE
  A MATCHER IT WILL BE BROKEN SILENTLY.** RULING 89, and RULING 74 before it.
  Classifying the 21 by reading their gap reasons with a regex is the shape both
  refuse. If the two populations in §2B need telling apart, **a person declares
  it and a guard re-derives the declaration** — the RULING 87 pattern, where
  seven refusal sentences each declare the claim they rest on and guard 46
  checks every one against the corpus.
- **AND THE ONE PRECEDENT THAT SAYS A SHAPE CAN BE HONEST.** The coastline. It
  was refused at first on the ground that "a traced coastline would be the one
  shape on the page that came from nowhere citable", and that was overturned for
  a reason recorded in `PROGRESS.md`'s A5 addendum: *coordinates are never
  authored* governs PLACEMENTS — claims about where a record's place is — while
  a coastline is the REFERENCE FRAME those claims are read against. It carries
  provenance like everything else here: Natural Earth 1:110m, its terms, and the
  date it was retrieved, all printed in the legend.
  **If a region layer is the answer, that is the argument it has to make and the
  standard it has to meet: a dated, citable, licence-checked source, shown as a
  frame and never as evidence.** Whether the project's own seven regions — which
  are its categories, not anyone's published boundaries — can meet it at all is
  the question, not a formality.

---

# 4. THE DESIGN SPACE, WITH WHAT EACH ONE COSTS

**Not a recommendation. The next thread decides with Rob, and should predict
before it builds.**

```
1  DO NOTHING ON THE MAP; THE REGION GRID IS ALREADY THE ANSWER
   All 54 records are listed by region under the map and every one is
   clickable — guard 28 has asserted that since A5. Costs nothing and
   changes nothing: the map still says East Asia is three records

2  REGION AS A FILTER, NOT A SHAPE
   Choosing a region highlights its drawn points and lists its off-map records
   beside them. NO NEW GEOMETRY, no authored coordinate, and it uses the `.hl`
   class FINDING 106 already says nothing applies. Cheapest honest answer;
   answers "where are this region's records" and not "where is this region"

3  A REGION LAYER, DRAWN FROM A CITABLE SOURCE
   The coastline's argument extended. Strongest visually and the only option
   that has to clear §3's last bullet: a published, dated, licence-read source
   whose boundaries are somebody's rather than this project's

4  EVERY RECORD GETS A VISIBLE HOME
   A per-region tray at the map's edge holding exactly what that region has and
   the map cannot draw, so a region's count is never silently 32-of-54.
   Composes with 2 and 3 rather than competing

5  THE PROJECT'S OWN ARGUMENT, DRAWN
   The map already refuses to plot 大秦. Say so ON the map: a region whose
   records name a polity rather than a place is the most interesting thing this
   geography has to say, and it is currently visible only as absence
```

**Whatever is chosen, the test is §2B: does a visitor who looks at East Asia
come away with 9 or with 3?**

---

# 5. THE GUARDS THAT WILL FIGHT YOU

`node ui/check_ui.mjs` is the gate, at **53**. The Map block's inventory is in
`UI_MAP_RESULT.md` §5 and is not restated. **These are the ones this brief
touches.**

```
FREE — every check asserting on data-place, data-group, data-edge, data-record,
data-marker, data-span. THREE full rewrites of the Map tab's markup in the last
block moved none of them. The freedom is real; use it.

CAREFUL
  28  all 54 records are clickable from the Places tab
      -> the region grid is the thing this brief is most likely to rebuild, and
         this check is why it must be relocated whole rather than re-authored
  48  the map, then the Guide, then the record grid
      -> re-pointed twice in the last block and relaxed neither time. If the
         layout changes again, re-point it; do not weaken it. The claim is that
         the box answering a click is ADJACENT to the map
  49  every tab with a panel has its own empty state, naming what it can select
      -> ADD A NEW CLICKABLE KIND AND THIS GOES RED until the Guide's sentence
         says so. That is the point of it
  53  every figure in the geography ledger is re-derived, on Methodology and
      only there
      -> `placeLedger()` is where the 90 comes from. A new way of counting what
         the map cannot draw has to agree with it or move it

AND THE TRAP THAT IS NOT A GUARD
  FINDING 108. The map's marks are authored in viewBox units and rendered at
  whatever scale the column gives them, so ANY LAYOUT CHANGE RESIZES THEM
  SILENTLY. It caught the last block twice in one session, in both directions,
  and guard 50 cannot see it because the harness has no layout. Run
  `node ui/measure_map.mjs <dir>` after any layout change.
```

---

# 6. WHAT THIS THREAD MUST NOT DO

- **Not curate a record. Not author a coordinate.** The nine locatable findspots
  in §2B are a curation question and answering it here would be this thread
  quietly changing the corpus to make its own design work.
- **Not classify the 21 with a matcher over their notes.** RULING 89. Declared by
  a person, re-derived by a guard.
- **Not hand-edit `ui/data.js`.** `python ui/build_ui_data.py` is how it moves,
  and FINDING 101 before running it on Windows.
- **Not relax a check to fit a design**, and not re-point one at a surface that
  carries a weaker claim — RULING 88's test.
- **Not type a count into prose**, and not type a tab name either: `TABS` is the
  authority and guard 51 enforces it.
- **Not build the chatbot.** Still RULING 83.
- **Not take the Methodology tab.** Rob has scheduled it, and it carries the two
  §9 debts, RULING 86's amendment and the Home "failures are kept" line.
- **Not assign ruling or finding numbers from this document.** `RULINGS.md` is
  the authority and the next free number is read from it at the time.

---

# 7. FIRST FIVE MINUTES

1. **`pip install "psycopg[binary]" sqlglot` on the bridge first**, with
   `--index-url https://pypi.org/simple` if plain `pip install` reports no
   matching distribution. FINDING 94: without them `state_block.py` reads
   `scripts/test_recover_baseline.py` as **RED** and `answer.test_answer` as
   **149**, and neither is about the repository. The RED half is the dangerous one.
2. **Enable file deletion for the repository folder at the start**, not in the
   middle. FINDING 103: git cannot commit from the Linux bridge without it, and a
   failed unlink leaves a lock that blocks every later attempt.
3. `python -m ingest.verify --state` and `python scripts/state_block.py`.
   Confirm 54 documents, eleven instruments green, `node ui/check_ui.mjs`
   **GREEN at 53**. If not, stop.
4. **Read `ui/index.html` whole.** It is ~247KB. Not ceremony: it found FINDING
   106 in the last block, and the block before that it found a false finding
   about to be written down.
5. **RENDER THE MAP TAB AND USE IT, at 1600px AND 390px**, and take your own
   baseline with `node ui/measure_map.mjs`. The figures in `UI_MAP_RESULT.md` are
   headless Chromium on Linux and are NOT comparable with a host browser.
6. **Write the predictions and commit them BEFORE any code.** Ruling 78. Include
   one built NOT to flatter the block — the last block's was refuted by its own
   first commit and was worth more than the two that held.

---

# 8. TWO THINGS THE LAST BLOCK LEARNED THAT ARE WORTH CARRYING

**A red test found a hole in a GUARD, twice, that re-reading never would have.**
Guard 52 was written specifically to check that stepping past both ends of the
Guide's trail is refused. Five ways to break the trail were tried; four went red
and the fifth stayed green, because the guard tested one end and not the other.
**The check itself is the thing being tested, and only breaking the code tests
it.**

**And the instrument has no opinion about whether the page is better.** The
full-width map satisfied every layout figure the last block predicted and was
reversed by Rob one message later. Every number said it improved. **Render it,
look at it, and put it in front of a person before believing a measurement.**
