# UI METHODOLOGY RESULT — **THE PREDICTIONS ARE SCORED AND NOT AMENDED. NINE OF
# NINE PROMISES HELD, AND THE PREDICTION BUILT NOT TO FLATTER THE BLOCK IS
# REFUTED BY ITS OWN USEFULNESS.**
#
# **It named the exact way the router would break. Naming it is what made the
# round-trip guard get written alongside the router instead of after it, so the
# break never happened. That is a worse outcome for the prediction and a better
# one for the page, and it is scored as a refutation.**

*Written 2026-09-12 at the close. `UI_METHODOLOGY_PREDICTIONS.md` was committed
at `4e7bd9b` **before a line of `ui/` was edited** and is not amended here — it is
scored. One prediction is left UNSCORED on purpose, and §6 says why.*

---

## THE STATE AT THE CLOSE

```
node ui/check_ui.mjs      GREEN, 61 checks, 0 failures   (57 at the open)
ui/data.js                NOT REGENERATED and in no diff
RULINGS.md                rulings 91-94 and findings 109-116 assigned this block
five commits on top of 19cfba0, plus one that belonged to the last one
```

**`ui/measure_map.mjs`, the same instrument at both ends — and the Map tab did
not move, which is the point of running it:**

```
width     page  notice     map    mapH    svgH   panel    grid   pins/ext
OPEN and CLOSE, identical
1600px    4175       —     403     954     618     403    1421     57/7
 390px    7098       —     318     790     201    1146    1386     57/7
```

**The Methodology instrument, written for this block:**

```
width     page   card1  notice   guide  guideH   rows (place/record/edge)
OPEN
1600px    9031     403    1793     403     238   117 (65/22/30)
 390px   15896     578    3401     318     238   117 (65/22/30)
CLOSE
1600px   10161     403    2862     403     238   117 (65/22/30)
 390px   17970     578    5368     318     238   117 (65/22/30)

click a row, both widths, all three kinds:
  OPEN    the address bar says "#data"
  CLOSE   "#data/place/…", "#data/record/…", "#data/edge/0"
```

**THE TAB IS 12% LONGER AT 1600px AND 13% LONGER ON A PHONE, and at 390px it is
now 17,970 pixels.** That is the cost of paying §3 and it is recorded here rather
than argued away: two cards were added to a tab that was already the longest on
the page. It is the first thing in the next block's start document.

---

# 1. P1 — THE TWO WITHHELD FAILURES. **CONFIRMED, AND THE AMENDMENT IS NARROWER
# THAN THE PREDICTION CLAIMED.**

**CONFIRMED: both are named, each says which kind it is, and neither is merged
into a count.** Guard 58 re-derives which question, which kind and every figure
beside it from the archive rather than from the page's classifier, and was seen
red three ways. The shape prediction **carried forward unscored from the Map
block** is scored here and is CONFIRMED.

**CONFIRMED: the line went on Methodology and not back on the Questions rail.**

**AND THE CORRECTION THE BLOCK OWES ITSELF: the amendment adds less than the
prediction said it would.** RULING 86's own text already required the line to say
*"how many and what kind"*. The prediction was written as though naming the kinds
were new; it was not. What AMENDMENT 1 actually settles is **where** the
obligation lives and that **a count was never compliant with the ruling in the
first place** — which is a smaller claim, honestly a more embarrassing one, and
the reason the debt survived three blocks: everyone who read it read a number.

**Scoreable and not scored as a measurement: "the second kind is the worse one".**
That is an argument the page now makes, not a fact this block tested. It is
recorded as an argument.

---

# 2. P2 — FINDING 115. **CONFIRMED IN ALL FOUR PARTS.**

```
recorded as a finding and fixed in this block     CONFIRMED  (115, guard 60)
its shape is FINDING 105's on a third surface     CONFIRMED
the replacement is DERIVED, not corrected         CONFIRMED
the only failing question the tab named was one
  that IS in the rail, while the two it withholds
  went unmentioned anywhere                       CONFIRMED, measured
```

The closing paragraph now names whichever question in the rail has the smallest
share of showable runs — the `contestedCoordinate()` pattern — and today that is
still the Aksum trade question at 2 showable of 39 under 5 prompt versions. Guard
60 re-derives it independently and hunts the two literals that were there.

---

# 3. P3 — THE PARTIAL ARCHIVE. **THE FIGURES CONFIRMED. THE MECHANISM REFUTED.**

**CONFIRMED to the number: 16 runs across 5 questions, and the fifth is the Aksum
trade question from §2.** Two of the three debts landed on one question and
neither knew about the other before the predictions were written.

**REFUTED: "the block will find that out by rendering."** The prediction said
stating the arithmetic on Methodology would not be enough and that the block
would discover it by looking. It did not. The debt's own wording in
`renderPassageProvenance` says the panel makes the substitution, so the label was
in the first version, before anything was rendered. **Right conclusion, wrong
route, and the route is what the prediction claimed.**

**UNPREDICTED, and better than what was predicted: the archive DECLARES it.**
`partial_passages` is a flag on the run. The prediction assumed the page would
have to infer the condition from the absence of a language; it does not, and the
declared flag is what guard 59 reads. The inferred symptom was checked against
the declared flag and is the same 16 runs — which is corroboration, not the
source.

---

# 4. P4 — §4A. **CONFIRMED IN EVERY PART, INCLUDING THE ONE ABOUT WHERE THE CODE
# GOES.**

```
the scheme, as declared in RULING 94 before it was built      CONFIRMED
the bare #place/ #record/ #point/ #edge/ forms untouched      CONFIRMED
the kinds are PANEL_EMPTY.data.selects, and a guard agrees    CONFIRMED
"select() is not where this goes — hashOf and applyHash and
 nowhere else, and a third site would be a finding"           CONFIRMED exactly
```

Two sites, no third. **Guard 61 closes a hole open since RULING 84: nothing in
this harness had ever asserted that a hash round-trips.**

---

# 5. P5 — THE GUARDS. **57 → 61, CONFIRMED TO THE NUMBER, AND THE COMPOSITION IS
# RIGHT TOO.**

All four new guards are the four that were predicted, in the predicted order.
**That is a better result than the regions block's identical count with a wrong
composition, and it is also the least interesting kind of correct** — the four
were predicted from a scope that had already been settled.

**CONFIRMED: no existing guard went red.** Guard 49 was the candidate named and
did not fire, which is the right outcome: the selectable kinds did not change.

**CONFIRMED, and by a different route than predicted: a new guard read its own
assumption rather than the page.** Guard 58's assertion that Home carries the
withheld count matched a single space, and this page's template strings wrap. It
was caught by the guard failing on its FIRST RUN rather than by a deliberate
break — which is luckier than the practice deserves. **This is the fifth time on
this project.** `\s+` now, with the note beside it.

**Every new guard was seen RED first**, twelve ways across the four: kind
branches swapped, a failure dropped from the card, Home's count removed,
`isPartialRun` forced false and forced true, the old sentence restored verbatim,
the derivation inverted to name the best-answered question, the data branch
inheriting the map view, `hashOf` dropping the selection, the bare `#place` form
re-pointed, the router gaining an undeclared kind, and an unresolvable address
resolving in silence.

---

# 6. P6 — **THE PREDICTION BUILT NOT TO FLATTER. THE FIRST HALF IS REFUTED BY ITS
# OWN USEFULNESS. THE SECOND HALF IS UNSCORED AND THE BLOCK DOES NOT CLOSE
# WITHOUT IT.**

> *"The first version of the address work will break something the harness cannot
> see … `applyHash`'s `record`, `place` and `edge` branches all set
> `state.view = "map"` unconditionally and the new branch forgets to."*

**It did not break.** The router worked on its first run and the round-trip guard
was green the first time it was asked.

**And the reason is the prediction.** Naming that specific failure in writing,
before any code, is what made guard 61 get written ALONGSIDE the router rather
than after it — the one ordering in which the failure cannot ship. The break was
then demonstrated deliberately, as break 61a, and it goes red exactly as
described.

**Scored REFUTED, and the refutation is the most useful line in the document.**
A prediction specific enough to be designed around stops being a forecast and
becomes an instruction. That is not a reason to write vaguer ones; it is a reason
to notice that **the value of this practice is not in being right**. This is the
third block running in which the prediction written to be unkind to the block was
the one worth having, and the first in which it was worth having by being wrong.

**UNSCORED: "Rob will find at least one thing on this tab that every figure in
this document passed."** He found three in the regions block and two before it.
Nothing in this document can score it, and **the block does not close until he
has used the tab at both widths** — the instrument still has no opinion about
whether the page is better. The three candidates named in advance, so they cannot
be claimed afterwards: the Guide's 238-pixel height against a panel that fills
with a twenty-row record list; the closing paragraph reading as an apology now
that the failures are stated properly above it; and `#data/place/<key>` addresses
being ugly when copied — `#data/place/arabia-06-syllaeus%3A%3Asubject_places%5B0%5D`
is the real thing, and it is as ugly as predicted.

---

# 7. WHAT THIS BLOCK SAID IT WOULD NOT DO. **NINE OF NINE HELD.**

```
not touch the Questions rail            HELD — one comment inside viewQuestions
                                        was updated to say the debt is paid; no
                                        behaviour and no markup changed
not rewrite the two audits              HELD — §4C untouched and still open
not build a general ledger-prose guard  HELD — guard 60 is specific to one
                                        paragraph; the general hole stays open
not relax a check to fit a design       HELD — no check weakened or re-pointed
not type a count into prose             HELD, and it caught the block TWICE in
                                        its own new prose: "the worse of the
                                        two" and "a rail that drops two of them"
                                        were both written and both removed after
                                        reading the rendered page
not author a coordinate                 HELD — nothing here went near one
not hand-edit ui/data.js                HELD — in no diff, not regenerated
not build the chatbot                   HELD — RULING 83 intact
not assign numbers from the predictions RULINGS.md was the authority throughout
```

**Nine of nine, against the regions block's six of eight.** The difference is not
virtue: this block's promises were about a scope that had already been settled,
and the regions block's were broken by a mid-block rescope.

---

# 8. WHAT THE BLOCK FOUND THAT NOTHING PREDICTED

**FINDING 116, and it is the most valuable thing here.** `git status --short`,
read after two commits of its own, showed two files the block had not touched:
the Guide's home button, 92 lines across `ui/index.html` and `ui/check_ui.mjs`,
with `commit-ui-guide-home.txt` written and complete in the repository root and
**the commit never made**. RULING 93 was satisfied and was not enough — it covers
how a message is written, not the step after it, and while the bridge shell is
down a commit is an instruction a person carries out with nothing on either side
checking that they did.

**Two documents already described that work as shipped.**
`UI_MAP_REGIONS_RESULT.md` §3 counts guard 52's extension among the guards that
block strengthened, and `UI_METHODOLOGY_START.md` §2 told this thread the tab has
home / back / forward. Both true of the working tree and of no commit. **The
harness cannot catch it, because the harness reads the working tree**: 57 checks
were green against those files all morning, and so were both baselines in this
block's own predictions, which are recorded as taken that way and not amended.

**And the start document's own figure was wrong.** §4A said "roughly seventy
clickable rows". It is **117** — 65 placements, 22 records, 30 edges. Measured
before anything was built, and the figure is the whole argument for §4A.

---

# 9. FOR WHOEVER OPENS THE NEXT BLOCK

`UI_METHODOLOGY_DESIGN_START.md` scopes it and carries the measurements. The
short version:

- **The tab is 17,970 pixels on a phone and 10,161 at 1600px**, and two of the
  eleven cards are 2,578px of a single grid row at desktop width. That is the
  largest open thing on it and this block made it 13% worse.
- **§4B is still open**, and is now open with a second instance recorded against
  it: a guard that asserts a figure is present cannot see that the sentence
  around it is wrong, on the ledger and on the closing paragraph both.
- **§4C is untouched.** The two audits are the strongest material on the tab and
  nobody has read them with a visitor in mind.
- **After handing a commit to the host, read `git status --short`.** FINDING 116.
  `git log` says what was committed; only `git status` says what was not.
