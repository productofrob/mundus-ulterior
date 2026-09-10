# UI MAP RESULT — **THE PREDICTIONS ARE SCORED AND NOT AMENDED, AND THE ONE
# CONSTRUCTED NOT TO FLATTER THE BLOCK WAS REFUTED BY THE FIRST COMMIT, ON ITS
# OWN REASONING, BEFORE ANY RESCOPING TOUCHED IT.**
#
# **AND THE FAILURE MODE THIS BLOCK NAMED IN ADVANCE — shipping a Map tab that
# measures better and reads worse — ACTUALLY HAPPENED. Rob caught it. The
# instrument said the map was bigger and said nothing about it being worse.**

*Written 2026-09-10 at the close. `UI_MAP_PREDICTIONS.md` was committed at
`a8d0e92` **before a line of `ui/` was edited** and is not amended here — it is
scored.*

---

## THE STATE BLOCK IS GENERATED. NOTHING BELOW IT IS RESTATED.

`python scripts/state_block.py`, at `9cb0196`:

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

**`node ui/check_ui.mjs`: 47 checks at the open, 53 at the close, 0 failures.**
Every guard added or moved was verified to FAIL on a broken version first.

**`ui/data.js` was not regenerated and appears in no diff** — checked with
`git diff a8d0e92^..HEAD -- ui/data.js`, which is empty. 54 records in, 54 out;
63 points drawn, 90 not; neither figure moved.

**Thirteen commits.** `RULINGS.md` reads next free ruling **91**, next free
finding **109**.

---

# 1. THE FIVE PREDICTIONS, READ

## P1 — WHICH CHECKS GO RED, AND THE COUNT. **THE HALVES THAT MATTER CONFIRMED; THE COUNT AND THE COMPOSITION REFUTED.**

**No check was red at any commit left standing. CONFIRMED.**

**Not one `data-*` check fired, for the fourth block running. CONFIRMED**, and
this block rewrote the Map tab's markup three times — into two columns, into a
full-width band, and back again.

**The count went 47 → 53, not the predicted 52, and only two of the five named
guards are among them.** That is refuted, and the refutation is the least
interesting kind: Rob redirected the block's scope four times after the
predictions were sealed, and three predicted guards went with the work they
belonged to.

```
GUARD 48   the panel is adjacent to the map     BUILT, and re-pointed TWICE
GUARD 49   every view has its own empty state   BUILT exactly as predicted
GUARD 50   the selected thing is marked         NOT BUILT — FINDING 106 is open
GUARD 51   the withheld failures counted        DEFERRED to the Methodology block
GUARD 52   the partial-archive substitution     DEFERRED to the Methodology block

and in their place, none of which the predictions could have anticipated:
GUARD 50   the map's label size is declared twice and the two agree
GUARD 51   every tab's name is declared once and the header agrees
GUARD 52   the Guide's trail steps back and forward and refuses both ends
GUARD 53   every figure in the geography ledger is re-derived, and only on
           Methodology
```

**The prediction named check 28 as the one genuinely at risk** — *all 54 records
are clickable from the Places tab* — and predicted it would not fire because
`regionCards()` would be relocated whole rather than rebuilt. **CONFIRMED.** It
was relocated whole three times and never fired.

## P2 — WHAT THE PAGE MEASURES AFTERWARDS. **TWO CONFIRMED, FIVE REFUTED, AND THE ANTI-FLATTERING ONE IS THE ONE WORTH READING.**

```
                              OPEN     PREDICTED        CLOSE
1600px  panel below fold      7306     0                 0      CONFIRMED
 390px  panel below fold     16464     0                 0      CONFIRMED
 390px  map y                  980     under 420        318     CONFIRMED
1600px  map y                  639     under 300        403     REFUTED
 390px  svg height             148     at least 300     148     REFUTED
 390px  page height          17557     down 2000+     16903     REFUTED (-654)
1600px  page height          10995     UP by 0..600   10240     REFUTED (-755)
```

**THE LAST LINE WAS THE PREDICTION BUILT NOT TO FLATTER THE BLOCK, AND IT IS
REFUTED FOR A REASON THAT HAS NOTHING TO DO WITH THE RESCOPING.** It was already
refuted by the FIRST commit: at `e705dd4`, before Rob had redirected anything,
the page measured 10531 — down 464, not up.

The reasoning was: *"the panel is tall, so the map's row is now as tall as the
taller of the two rather than as tall as the map."* **That is wrong about the
grid I then wrote.** The panel is placed `grid-row: 1 / span 2`, so its height is
absorbed by the second row — the row the map is in stays exactly as tall as the
map. I predicted about a layout and then built a different one, and did not go
back and re-read the prediction against it.

It is worth more than the two that held. A prediction refuted by a rescoping
teaches nothing; this one was refuted by my own mechanism being wrong, on the
first commit, and the instrument said so immediately.

**The two `svg height` and `page height` refusals on the phone are honest
failures of a different kind: the edit that would have moved them — the map's
own height at 390px — was never taken.** It is still the largest thing
outstanding on this tab and it is named in the start document that follows.

## P3 — WHAT I EXPECTED TO ABANDON. **CONFIRMED, ALL FOUR.**

```
1  THE GAP LISTS BEHIND A DISCLOSURE     ABANDONED, as predicted. Never attempted
2  A STICKY MAP ON DESKTOP               ABANDONED, as predicted. The Guide is
                                         the sticky column and two would fight
3  THE LEDGER MOVED BELOW THE MAP        KEPT — and then superseded: Rob moved it
                                         off the tab entirely, to Methodology,
                                         which is the same argument carried
                                         further than the prediction dared
4  DROPPING THE LEGEND ON THE PHONE      ABANDONED, as predicted. `ground` is
                                         told apart BY SHAPE and the legend is
                                         the only place the page says so
```

## P4 — THE TWO §9 DEBTS. **FIGURES CONFIRMED; THE WORK DEFERRED AND UNSCORED.**

```
PREDICTED   withheld failures                    2      DERIVED, 2
PREDICTED   partial-archive runs                16      DERIVED, 16 across 5
PREDICTED   the rail partition, unchanged   24 / 7 / 2  DERIVED, unchanged
```

Every figure was derived from the bundle before any code and every one held.
**The work itself is deferred**: Rob ruled that failures will be discussed at
length on Methodology and that the tab is edited after the map, so both debts
and the amendment RULING 86 owes travel to that block intact. The prediction
about the SHAPE of the line — that it says which kind each of the two failures
is — is unscored and carried forward.

## P5 — WHAT THIS BLOCK WOULD NOT DO. **CONFIRMED, ALL EIGHT.**

Chatbot, curation, coordinates, `data.js`, filtering to tidy a layout, relaxing
a guard, splitting the inline script, reading a rights position — none of them.

**And one it did better than promised.** *Not type a count into prose* was the
eighth, and this block found the same defect in words rather than digits: the
page typed its own tab names into five sentences and two tooltips, and had
already drifted — `viewAbout` said "the Places tab" twice about a tab labelled
"Map". Every mention is derived from `TABS` now.

---

# 2. THE FAILURE MODE THIS BLOCK NAMED IN ADVANCE, AND WHO CAUGHT IT

`UI_MAP_PREDICTIONS.md` §4 said the one thing that would make this block a
failure is **"shipping a Map tab that measures better and reads worse"**, and
that the check on it is not in `check_ui.mjs` and cannot be: it is rendering the
page and looking at it.

**It happened.** The map went full width at Rob's instruction, and by every
figure the instrument reports it was better: 1058 → 1480 rendered pixels, 24 →
33 labelled marks, the panel still in view at both widths. I reported those
figures, noted the panel's content stretching, and **did not say it read worse.**
Rob did, in one sentence, and reversed it.

That is the same shape as the design block's own closing note — *the sharpest
defect was found by Rob, not by me* — and it is the second time on this project.
**The instrument is very good at telling you a number moved and has no opinion
at all about whether the page is better.** Everything in §1's P2 was satisfied by
the version that got reversed.

---

# 3. WHAT LOOKING CAUGHT THAT NO CHECK WOULD HAVE

Six, and **four of them were in fixes rather than in the original code**, which
is the pattern worth carrying.

- **FINDING 106** — the map never shows what is selected. Four CSS rules style
  `.pin.hl`, `.extent.hl` and `.edge.hl`; `classList.add` is called twice in the
  file and both times with `"dragging"`. The screenshot before clicking a pin
  and the screenshot after are byte-for-byte the same file. **Still open.**
- **`block: "nearest"`** in my own §3A fix landed a phone reader at the BOTTOM
  of a 2,000px panel.
- **`#panel` rather than its wrapper** in the same fix put the eyebrow naming
  the panel 27px above the fold — a reader arriving at an answer with nothing on
  screen saying what they were looking at. Only reachable once the wrapped tab
  row pushed the layout down.
- **A label touching the pin it names**, at Roma, once the map was drawn at
  1.64×. The tight ratio had been there all along; the scale made it legible.
- **The two thumbnails**, which share `buildMap` and turned into smudges when the
  live map's dots were enlarged for clickability.
- **Three stale pointers** in the geography ledger the moment it moved tabs —
  "nothing HERE", "THIS map", "the lists BELOW", on a tab with no map and no
  lists below it. The same defect RULING 90 exists to have caught.

---

# 4. AND TWICE A RED TEST FOUND A HOLE IN THE GUARD RATHER THAN IN THE CODE

**This is the strongest thing this block has to say about its own practice.**

Guard 52 asserts the Guide's trail steps back and forward. Five ways to break the
trail were tried. Four went red. **The fifth — letting a forward step run off the
end of the list — stayed GREEN**, because the guard tested stepping past the
START and never past the END, in a guard written specifically to check both. No
amount of re-reading it had found that; breaking the code did, in one run.

**A check written and never seen red is a check nobody has any reason to trust,
and this block is why: the check itself is the thing being tested.**

---

# 5. WHAT THE BLOCK BUILT

```
SECTION 3A   FIXED. The box that answers a click on the map was 7,306 pixels
             below the fold at 1600px and 16,464 on a phone. It is the right-hand
             column, sticky over the whole tab, in view at both widths — checked
             at the far end of the tab as well as at the map

THE MARKS    A person can hit and read them. 12.9 -> 24.7 CSS px of dot, 11.8 ->
             16.5 of type, and 26 of 64 marks carry a name against 28 before,
             bought back by giving the collider eight candidate positions
             instead of four

RULING 90    The empty state belongs to the TAB. One string served two tabs and
             the Map tab was telling visitors to click things it does not have

THE TABS     'Map & Sources' and 'Methodology', and no prose types a tab name
             again — five sentences and two tooltips read TABS now, and the
             phone's tab row wraps so all four arrive on screen

THE GUIDE    Renamed, with Rob's sentence, and back / forward over everything a
             reader has opened. RULING 84 shaped it: state.selection stays the
             only source of truth and stepping WRITES it

THE LEDGER   Moved to Methodology, with the guard it never had

FINDING 106  the map never marks what is selected — OPEN
FINDING 107  "Claude outputs/" is where the desktop app delivers, not debris
FINDING 108  the map's mark sizes depend on the layout, and no guard can see it
```

---

# 6. FOR WHOEVER OPENS THE NEXT BLOCK

- **`ui/measure_map.mjs` is the instrument and it is committed.** Measure your own
  baseline before scoring anything against a figure in this document: it is
  headless Chromium on Linux, where the serif stack falls back, and it is NOT
  comparable with a host browser.
- **FINDING 108 is the trap.** A change to the Map tab's LAYOUT is a change to
  its MARK SIZES, silently, because the marks are authored in viewBox units and
  rendered at whatever scale the column gives them. It caught this block twice in
  one session, in both directions. Guard 50 cannot see it — the harness has no
  layout. Run the instrument after any layout change.
- **The harness needs `ui/data.manifest.json` beside `ui/data.js`.** A copy of
  `ui/` without it runs **44 of the 53** and still reports GREEN. The gate is the
  repository's 53.
- **FINDING 106 is the smallest useful thing left on this tab**, and it is half
  of "nothing appears to happen": the panel being far away was the other half and
  is fixed.
- **THE MAP'S HEIGHT AT 390px IS THE LARGEST.** It renders 0.38× into a
  148-pixel postage stamp, and no mark size rescues it. Two of P2's refutations
  are this and nothing else.
- **Owed to Methodology, and Rob has scheduled that tab next-but-one:** the two
  withheld failures with RULING 86's amendment, the partial-archive substitution,
  and the Home "the failures are kept" line Rob said will be slightly modified.
  The figures are derived and recorded in P4 above.
- **The gap lists are still on Map & Sources** — the contested-coordinate card,
  the focus-gaps card and the three placards — while the ledger that framed them
  is on Methodology. They point at each other correctly today. If more of that
  apparatus moves, they should travel together.
