# UI METHODOLOGY START — **THIS TAB HAS BEEN HALF-REBUILT BY A BLOCK THAT
# PROMISED NOT TO TOUCH IT, AND IT STILL OWES EVERYTHING IT OWED BEFORE.**
#
# **Methodology now carries eight cards and a Guide of its own. The two §9 debts
# — the two withheld failures with RULING 86's amendment, and the partial-archive
# substitution — have been "owed to Methodology, next-but-one" since the Map
# block and are still owed. Pay them before adding anything.**

*Written 2026-09-11 at the close of the regions block, for the thread that edits
Methodology. **Every figure here was measured at that close; none is inherited.**
The first thing the new thread does is confirm the state block still reproduces —
if it does not, stop and find out what moved.*

---

# 1. WHERE THE PROJECT IS

`UI_MAP_REGIONS_RESULT.md` scores the regions block and is worth reading whole
before this document's §4 — its §6 in particular, because two of the eight things
that block promised not to do, it did, and one of them was taking this tab.

```
54 records        169 placements     63 points and extents drawn, 90 not
7 regions         685 archived runs  57 checks green, eleven instruments green
```

**`RULINGS.md` is the authority: next free ruling 91, next free finding 109.**
Read it at the time anyway. **Nothing was assigned in the regions block**, and
`UI_MAP_REGIONS_RESULT.md` §8 lists three rulings and six findings that block
owes the register. **Assigning them is the first act of this one.**

---

# 2. WHAT IS ON THIS TAB NOW

```
Citations checked against the corpus, just now        the first audit
And has the corpus moved underneath them?             the second audit
What the map draws, and what it will not              the geography ledger
one gazetteer id, named 11 times and used 2           \
the place the passage is organised around…             |
considered — nothing resolves to a drawable point      |  moved here 2026-09-11
edges named in the text, not drawn on the map          |
declared unplaceable — considered, and kept anyway    /
What this page does not show                          the closing prose
```

**AND IT HAS ITS OWN GUIDE.** `.cols-panel`, a sticky right-hand panel, `panelNav`
with home / back / forward, and `PANEL_EMPTY.data` — its own empty-state
sentence, because guard 49 requires a view that renders a panel to declare one
AND to advertise exactly the kinds its markup can select. This tab selects
`place`, `record` and `edge`. It has no map, so it does not offer `group`,
`region` or a point.

---

# 3. THE DEBTS THIS TAB HAS BEEN OWED SINCE THE MAP BLOCK

**These are not new work. They were derived, recorded, and deferred to this tab,
and `UI_MAP_RESULT.md` §1 P4 holds the figures:**

```
withheld failures               2       and RULING 86 owes an AMENDMENT about them
partial-archive substitution   16 runs across 5
the rail partition             24 / 7 / 2      derived, unchanged
```

- **The two withheld failures.** The Questions rail lists questions with a
  showable run, groups the seven `correctly_refusable` refusals, and COUNTS two
  failures it does not list — one `answerable` question every run of which
  refused, one whose runs never quote anything. Home promises that *"the failures
  are kept … a system that only displays its successes is not evidence of
  anything"*, and this tab is where that promise is kept or is not.
  **The prediction about the SHAPE of that line — that it says which KIND each of
  the two failures is — is unscored and carried forward from the Map block.**
- **RULING 86 owes an amendment** about those two, and it has been owed for two
  blocks.
- **The partial-archive substitution**, 16 runs across 5.
- **The Home "the failures are kept" line**, which Rob said will be slightly
  modified — and which cannot be modified honestly until the line above it exists.

---

# 4. WHAT IS OPEN ON THIS TAB, MEASURED

## A. A SELECTION MADE HERE IS NOT IN THE ADDRESS BAR

`hashOf` returns `#data` for this view and nothing more. The tab now has roughly
**seventy clickable rows** and a Guide to answer them, so a reader who opens a
refused placement and copies the link hands over a link to the tab and not to the
thing. The placement is still addressable as `#place/…`, which resolves onto the
**Map** tab.

**This is RULING 84's territory and it is the largest open item here.** The ruling
exists because "a shared link that quietly lands on a different question is a
viewer that would look entirely convincing and be wrong". Giving this tab its own
address space is a change to that machinery and was deliberately not folded into
a move.

## B. THE LEDGER'S PROSE IS NOT GUARDED, AND WENT STALE TWICE

Guard 53 re-derives **every figure** in the geography ledger and **cannot read a
sentence**. Twice in the last block the ledger's prose became false while the
guard stayed green — once when the bands were drawn and the last cell still said
these records appear "only in the lists on the Map & Sources tab", and once when
the legend flatly asserted that every band's position is derived. Both were
caught by a person reading the page.

**This is FINDING 105's shape on a different surface**: a guard asserting that a
value is present, unable to see that the words around it are wrong.

## C. THE TWO AUDITS PRE-DATE EVERY UI BLOCK

`Citations checked against the corpus, just now` and `And has the corpus moved
underneath them?` have not been touched since they were written. They are the
strongest material on this tab and nobody has read them with a visitor in mind.

---

# 5. THE GUARDS THAT WILL FIGHT YOU

`node ui/check_ui.mjs` is the gate, at **57**.

```
FREE — every check asserting on data-place, data-record, data-edge. FIVE rewrites
of this tab's markup have moved none of them.

CAREFUL
  49  every tab with a panel has its own empty state, naming what it can select
      -> reads `questions: 2, map: 4, data: 3`. ADD A CLICKABLE KIND TO THIS TAB
         AND THIS GOES RED until `PANEL_EMPTY.data.selects` says so. That is the
         point of it. It also refuses two tabs printing the same sentence.
  52  the Guide's trail steps back and forward, refuses both ends, and home puts
      the selection down without throwing the trail away
      -> the home button is new. Five claims, all about a VALUE after a sequence
         of moves. Four ways of breaking it go red.
  53  every figure in the geography ledger is re-derived, on Methodology and only
      there
      -> `placeLedger()` and `bandLedger()` are where the figures come from. The
         guard cannot see prose; §4B is the standing hole.
  19  every drawable edge is drawn, presents a target, and is listed on the panel
      of both points it joins; every undrawn edge names both ends and says what
      the map marks
      -> the undrawn-edge half renders on THIS tab now.
  54-57  the region bands. They assert against `buildMap()`, which this tab does
      not render — but `geographyCards()` and `placeNotice()` both print figures
      that 54 and 57 re-derive.

AND THE TRAP THAT IS NOT A GUARD
  A RE-POINTED SENTENCE. RULING 90. Five cards moved to this tab and every one of
  them pointed at "the map above". They were re-pointed by hand and nothing
  checks that they stay right. The next thing that moves will do it again.
```

---

# 6. WHAT THIS THREAD MUST NOT DO

- **Not leave the register unwritten.** `UI_MAP_REGIONS_RESULT.md` §8 lists three
  rulings and six findings the last block owes. Assign them from `RULINGS.md`
  first, before any code.
- **Not add to this tab before paying §3.** It has been owed two debts for two
  blocks and has just gained five cards.
- **Not relax a check to fit a design**, and not re-point one at a weaker claim —
  RULING 88's test.
- **Not type a count into prose**, in digits OR in letters. 2g hunts specific
  literals and the last block found one that had survived four blocks as the word
  "two".
- **Not author a coordinate.** Two were authored in the last block, at Rob's
  instruction, labelled on screen and guarded — and it was still scored refuted.
  If a third is needed, it is a ruling, not a diff.
- **Not hand-edit `ui/data.js`.** `python ui/build_ui_data.py`, and FINDING 101
  before running it on Windows.
- **Not build the chatbot.** Still RULING 83.
- **Not assign ruling or finding numbers from this document.** `RULINGS.md` is
  the authority and the next free number is read from it at the time.

---

# 7. FIRST FIVE MINUTES — **AND THE ENVIRONMENT HAS CHANGED**

**THE BRIDGE SHELL IS GONE.** A Windows update released **2026-09-08** stops
Claude's isolated Linux workspace reaching the repository; `device_bash` reports
`Workspace unavailable` and it is not a permissions problem, not transient, and
not fixed by reconnecting the folder. **Do not spend a turn diagnosing it.**

```
WORKS         device_list_dir / device_stage_files / device_commit_files
              — reading and writing the repository's files, with an mtime guard
DOES NOT      any shell on the host. No git, no pytest, no build_ui_data.py
NOT A WAY     computer-use. Terminals resolve at `click` tier: it can see a
ROUND IT      terminal and left-click in it, and cannot type
```

**So the division of labour is:**

1. **Stage the files you need** into the session container, edit them there, run
   `node ui/check_ui.mjs` there, and write them back with the mtime guard.
   Staging `ui/index.html`, `ui/check_ui.mjs`, `ui/data.js`, `ui/data.manifest.json`
   and `ui/banner/` gives a complete, runnable harness.
2. **`ui/measure_map.mjs` needs Playwright and a headless Chromium**, which the
   session container has and the host does not. Its figures are NOT comparable
   with a host browser's — measure your own baseline before scoring anything.
3. **Everything corpus-wide goes to the host**: `python -m ingest.verify --state`,
   `python scripts/state_block.py`, `python ui/build_ui_data.py`, the test suite,
   and `git`. Rebuilding `data.js` reads all 685 archived runs; do not ship those.
4. **Commit messages: `commit-<topic>.txt`, one per commit.** The repository's
   `.gitignore` covers `commit-*.txt` at line 33 and the root holds two hundred of
   them. **The last block used one reusable filename and each round overwrote the
   previous description before it had been committed — three rounds of work
   collapsed into one commit wearing the last round's words, and one commit
   shipped describing a change it did not contain.** Every instruction handed to
   the host names EVERY file the commit touches.
5. **Read `ui/index.html` whole.** It is ~300KB. Not ceremony: it has found a
   real defect in each of the last four blocks.
6. **Render the Methodology tab and use it, at 1600px AND 390px.** The phone is
   where the last block's worst defect was — the Guide landed 15,615 pixels down
   this tab because a grid item inherited an `order` from a rule written for a
   different layout.
7. **Write the predictions and commit them BEFORE any code.** Ruling 78. Include
   one built NOT to flatter the block: it has been the most valuable line in each
   of the last two result documents, and in both it was confirmed.

---

# 8. THREE THINGS THE LAST BLOCK LEARNED THAT ARE WORTH CARRYING

**A GUARD THAT RECOMPUTES FROM THE CONSTANT IT IS CHECKING AGREES WITH ITSELF.**
Guard 56 was written to assert that a band's plate is the size its contents
declare, and it derived the expected width from the same constant the page draws
with. Putting back the exact defect that had shipped left it GREEN. The fix was
the `--map-label` pattern: declare the value twice, in the stylesheet and in the
script, and check the two agree.

**AND A CHECK CAN READ ITS OWN ASSUMPTION RATHER THAN THE PAGE.** Twice. A
pattern built inside a template literal lost its `[\s\S]` to the escape rules and
compiled as `[sS]`; another matched a single space where the page's template
strings wrap. Both reported cleanly and both were testing nothing. **Four times
now on this project a red test has found the hole in the guard rather than in the
code, and every one of them was found by deliberately breaking the code.**

**THE INSTRUMENT STILL HAS NO OPINION ABOUT WHETHER THE PAGE IS BETTER.** Rob
found three defects in the last block that every figure passed: bands pinned to
the canvas edge under zoom, an edge too thin to click, and a card whose
explanation could not be followed. **Render it, look at it, and put it in front
of a person before believing a measurement.**
