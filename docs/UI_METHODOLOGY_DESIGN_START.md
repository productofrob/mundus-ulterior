# UI METHODOLOGY DESIGN START — **THE TAB IS EIGHTEEN THOUSAND PIXELS LONG ON A
# PHONE, AND THE LAST TWO BLOCKS BOTH MADE IT LONGER.**
#
# **Everything on it is true, guarded and derived. Nobody has asked whether a
# visitor can read it. That is this block.**

*Written 2026-09-12 at the close of the Methodology block, for the thread that
redesigns this tab. **Every figure here was measured at that close on the
instruments named below; none is inherited.** The first thing the new thread does
is confirm the state block still reproduces and re-measure its own baseline — if
either does not reproduce, stop and find out what moved.*

---

# 1. WHERE THE PROJECT IS

```
54 records        169 placements     63 points and extents drawn, 90 not
7 regions         685 archived runs  61 checks green, eleven instruments green
```

**`RULINGS.md` is the authority: next free ruling 95, next free finding 118.**
Read it at the time anyway. **The register is CLEAN** — rulings 91-94 and
findings 109-117 were all assigned and carried back in the block that used them,
which is the first time in three blocks that has been true. `UI_METHODOLOGY_RESULT.md`
scores the last block and owes the register nothing.

**Read `UI_METHODOLOGY_RESULT.md` §6 before writing this block's predictions.** A
prediction specific enough to be designed around prevented the failure it named
and was scored refuted for it (FINDING 117). That is not a reason to write vaguer
ones.

---

# 2. WHAT IS ON THIS TAB NOW, AND HOW BIG EACH PIECE OF IT IS

Measured on a Methodology-tab layout probe at the close, headless Chromium 1194,
not comparable with a host browser and comparable with itself:

```
                                                       1600px        390px
page                                                    10161        17970
 1  Citations checked against the corpus, just now         591         1298
 2  And has the corpus moved underneath them?              635         1261
 3  The questions this page will not put in front of you   589         1191
 4  The runs this archive had to rebuild                   449          743
 5  What the map draws, and what it will not               550         1247
 6  one gazetteer id, named 11 times and used 2           1119         2037
 7  the place the passage is organised around             1083         2117
 8  considered — nothing resolves to a drawable point     1616         2774
 9  edges named in the text, not drawn on the map     ]   2578         3481
10  declared unplaceable — considered, and kept     ]  one grid row     323
11  What this page does not show                           309          668
```

**Cards 9 and 10 are `.placards`, a two-column grid at desktop width**, so they
report the height of the row they share — 2,578px of it, the tallest thing on the
tab. On a phone they stack and card 9 alone is 3,481px.

**AND IT HAS A GUIDE AND ITS OWN ADDRESS SPACE.** `.cols-panel`, a sticky
right-hand panel, `panelNav` with home / back / forward, `PANEL_EMPTY.data`, and
**117 clickable rows** — 65 placements, 22 records, 30 edges. Every one of them
now writes `#data/place/…`, `#data/record/…` or `#data/edge/…` to the address bar
(RULING 94, guard 61).

**The Guide is 238 pixels tall in its empty state** and fills with panels that run
to twenty rows. Nobody has looked at that.

---

# 3. THE THREE THINGS THIS BLOCK IS FOR

## A. **THE LENGTH, AND IT IS THE WHOLE PROBLEM**

Eleven cards. At 1600px the closing card — the one that says no answer on this
page is generated when you read it — sits at 9,772 pixels, which no visitor
reaches. On a phone the tab is **17,970 pixels**: about forty-five screens.

**The last two blocks both made it worse and both were right to.** The regions
block moved five cards here because they are about how the map is MADE rather
than about what it shows. The Methodology block added two because §3's debts had
been owed for two blocks. Neither was wrong and the result is unreadable.

**This is an information-architecture problem wearing a visual-design costume**,
which is the sentence `UI_DESIGN_START.md` §9 used about the front section, and
that block's answer — move the best material to the first screen — is available
here and is not obviously right, because on this tab everything claims to be the
best material.

**What is NOT allowed as an answer: deleting a count.** Home promises the failures
are kept. Every card here is one of the things that promise names.

## B. **§4B, THE LEDGER'S PROSE, AND IT NOW HAS TWO INSTANCES**

Guard 53 re-derives every figure in the geography ledger and **cannot read a
sentence**. Twice in the regions block the ledger's prose became false while the
guard stayed green, and both were caught by a person reading the page. **FINDING
115 is the third instance, on the closing paragraph**, and it was fixed only for
that paragraph: guard 60 re-derives those four claims and nothing else.

**The general hole is open and this is the block that could close it.** The shape
of an answer is already on the page twice — RULING 87's refusal sentences declare
the claim they rest on and guard 46 re-derives it; `data-cell` attributes make the
ledger's figures machine-readable. What does not exist is a rule that a sentence
on this tab MUST declare what it rests on.

## C. **§4C, THE TWO AUDITS, NEVER READ WITH A VISITOR IN MIND**

`Citations checked against the corpus, just now` and `And has the corpus moved
underneath them?` have not been touched since they were written. **They are the
strongest material on this tab** — 1,226 pixels of it at 1600px, at the top,
where a visitor actually arrives — and they were written for a reader who already
knew what a span was.

---

# 4. THE GUARDS THAT WILL FIGHT YOU

`node ui/check_ui.mjs` is the gate, at **61**.

```
FREE — every check asserting on data-place, data-record, data-edge. Six rewrites
of this tab's markup have moved none of them.

CAREFUL
  49  every tab with a panel has its own empty state, naming what it can select
      -> reads `questions: 2, map: 4, data: 3`. ADD A CLICKABLE KIND AND THIS
         GOES RED until PANEL_EMPTY.data.selects says so — AND SO DOES 61, which
         reads the same list from the router's side.
  61  every kind this tab can select round-trips through the address bar, and
      the bare #place/ #record/ #point/ #edge/ forms still open the MAP
      -> the two declarations are DATA_ROUTE and PANEL_EMPTY.data.selects. They
         must agree. The bare forms are links this project has handed out and
         RULING 94 forbids re-pointing them.
  58  the two withheld failures are named, with the KIND re-derived, and Home
      carries the same count from the same derivation
      -> it reads `data-withheld`, `data-runs`, `data-refused`, `data-spans` off
         the markup and Home's own sentence. Reword either and read this first.
  59  the partial-archive figures are re-derived AND the panel labels the
      substitution — and does not label a run that is not partial
  60  the closing paragraph names whichever question the archive answers worst,
      every figure derived, and the old literals are hunted
  53  every figure in the geography ledger is re-derived, on Methodology and
      only there
  2g  no count on this page is written down. It hunts specific literals, in
      digits AND in letters, and it cannot see a new one.

AND THE TRAP THAT IS NOT A GUARD
  A RE-POINTED SENTENCE. RULING 90. Cards on this tab point at "the ${TABS.map}
  tab" in four places and each was re-pointed by hand when the cards moved.
  Nothing checks that they stay right. A redesign that moves a card moves a
  pointer.
```

---

# 5. WHAT THIS THREAD MUST NOT DO

- **Not delete a count to shorten the tab.** Home promises the failures are kept;
  every card here is one of the things that promise names. Length is solved by
  arrangement, disclosure or hierarchy, not by dropping evidence.
- **Not re-point a link that has been handed out.** RULING 94. `#place/…`,
  `#record/…`, `#point/…` and `#edge/…` open the Map tab and keep doing so
  whatever moves.
- **Not relax a check to fit a design**, and not re-point one at a weaker claim.
  RULING 88.
- **Not type a count into prose**, in digits OR in letters. It caught the last
  block twice in its own new writing, both times by reading the rendered page.
- **Not author a coordinate.** RULING 91 if one is ever needed; it is a ruling,
  not a diff.
- **Not hand-edit `ui/data.js`.** `python ui/build_ui_data.py`, and FINDING 101
  before running it on Windows.
- **Not build the chatbot.** Still RULING 83.
- **Not assign ruling or finding numbers from this document.** `RULINGS.md` is
  the authority and the next free number is read from it at the time.

---

# 6. FIRST FIVE MINUTES — **AND THE ENVIRONMENT HAS NOT IMPROVED**

**THE BRIDGE SHELL IS STILL GONE.** A Windows update released 2026-09-08 stops
Claude's isolated Linux workspace reaching the repository; `device_bash` reports
that no drive shares are mounted. Confirmed still broken on 2026-09-12. **Do not
spend a turn diagnosing it.**

```
WORKS         device_list_dir / device_stage_files / device_commit_files
              — reading and writing the repository's files, with an mtime guard
DOES NOT      any shell on the host. No git, no pytest, no build_ui_data.py
NOT A WAY     computer-use. Terminals resolve at `click` tier
ROUND IT
```

1. **Confirm the state block on the host** before editing: `git status --short`,
   `python scripts/state_block.py`, `python -m ingest.verify --state`,
   `node ui/check_ui.mjs`. **Read the `git status` output** — FINDING 116 is
   exactly what it is for, and it cost the last block a commit it did not know it
   was carrying.
2. **Stage `ui/index.html`, `ui/check_ui.mjs`, `ui/data.js`,
   `ui/data.manifest.json` and `ui/banner/`** into the session container. That is
   a complete runnable harness. Edit there, run there, write back with the mtime
   guard, and CHECK THE BYTE COUNT after every write — FINDING 104.
3. **Playwright needs a symlink in this container.** `/opt/pw-browsers` holds
   build 1194 and a freshly installed `playwright` wants 1243; link
   `chromium_headless_shell-1243/chrome-headless-shell-linux64` at 1194's
   `chrome-linux`, and `headless_shell` as `chrome-headless-shell`. Two commands,
   and without them `ui/measure_map.mjs` cannot run at all.
4. **`ui/measure_map.mjs` measures the MAP tab (`#map`).** There is no committed
   instrument for this one. The last block wrote a throwaway probe; **write a real
   `ui/measure_data.mjs` and commit it**, because this block is a layout block and
   a layout block without an instrument is a matter of opinion.
5. **Commit messages: `commit-<topic>.txt`, one per commit** — RULING 93 — and
   the instruction handed to the host names EVERY file the commit touches.
6. **Read `ui/index.html` whole.** It is ~330KB. Not ceremony: it has found a real
   defect in each of the last five blocks, and the last one was FINDING 115.
7. **Render the tab and use it, at 1600px AND 390px, before deciding anything.**
   The phone is where this tab's problem lives: 17,970 pixels of it.
8. **Write the predictions and commit them BEFORE any code.** Ruling 78. Include
   one built NOT to flatter the block — and read `UI_METHODOLOGY_RESULT.md` §6
   first, because the last one was refuted by being useful.

---

# 7. THREE THINGS THE LAST BLOCK LEARNED THAT ARE WORTH CARRYING

**A COMMIT MESSAGE WRITTEN TO ITS OWN CORRECTLY-NAMED FILE IS NOT A COMMIT.**
FINDING 116. Ninety-two lines of the previous block's work sat in the working
tree for a day while two documents described it as shipped, and the harness could
not see it because the harness reads the working tree. `git log` says what was
committed; only `git status` says what was not.

**A DEBT RECORDED IN A COMMENT IS A DEBT NOBODY CAN SEE.** The two withheld
failures were recorded in `viewQuestions`, the partial-archive substitution in
`renderPassageProvenance`, and both survived three blocks being deferred by
documents that faithfully repeated them. What discharged them was a card on a
page and a guard that re-derives it.

**AND THE INSTRUMENT STILL HAS NO OPINION ABOUT WHETHER THE PAGE IS BETTER.**
Every figure in the last block passed, twelve deliberate breaks went red, and the
tab got 13% longer on a phone. **Render it, look at it, and put it in front of a
person before believing a measurement.**
