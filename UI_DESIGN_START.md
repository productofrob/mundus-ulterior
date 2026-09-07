# UI DESIGN START — **THE PAGE IS CORRECT AND IT IS NOT DESIGNED. THAT IS THE
# WHOLE BLOCK.**

*Written 2026-09-07 at the close of the UI block, for the thread that opens the
design block. **Nothing here was measured by the design block; it is a scope and
a set of constraints**, assembled from `UI_RESULT.md`, `UI_RULINGS.md` and the
state of `ui/` on disk at `6ddb5e6`. Every figure is transcribed from those or
measured at the close. The first thing the design session does is confirm the
state block still reproduces — if it does not, stop and find out what moved.*

---

# 1. WHERE THE PROJECT IS, IN FIVE LINES

**The UI block closed clean.** Ruling 83 decided the chatbot's shape and built
none of it. Click-through citation gained the axis it was actually missing.
FINDINGS 98 and 99 are closed. Debt row 7 is paid. `check_ui.mjs` went 25 checks
to 39, all green, and `build_ui_data.py --verify` is byte-identical on both axes.

**Read `UI_RESULT.md` before this document's §4.** Its §5 and §6 are the two
sections a design session will otherwise rediscover the hard way.

```
54 records          170 chunks          685 archived runs
33 questions        1289 citation spans 63 places drawn, 90 not
39 checks green     eleven instruments green
```

**The next free ruling is 84 and the next free finding is 100.** `RULINGS.md`
was corrected at the close and is now right; read it at the time anyway.

---

# 2. WHY THIS BLOCK EXISTS, STATED HONESTLY

**Every claim this page makes is now true, and none of it is designed.** The
typography is one serif stack and one system stack. The palette is six greys, a
brown and three status colours. The layout is a three-column grid that was
correct at 24 records and has since had four cards, a ledger and a cross-tab
added to it without anyone standing back.

**This is not a criticism of the page and the distinction matters.** Every
previous block bought correctness, and correctness was the right thing to buy —
a beautiful page that quietly dropped a citation would be worse than an ugly one
that cannot. **The design block is the first one that is allowed to care how it
looks, and it is allowed to care a lot.**

**What it is not allowed to do is make anything less true.** §4 is the whole of
how that is enforced, and the good news is that the enforcement was built with
this block in mind: **fourteen of the thirty-nine checks assert on `data-*`
attributes precisely so that prose, styling and layout can be rewritten freely.**

---

# 3. SCOPE — ALL FOUR, AND THEY ARE NOT EQUAL

```
IN   VISUAL / AESTHETIC        type, colour, spacing, density, the feel
     INFORMATION ARCHITECTURE  what is on which tab, what a first-time
                               visitor lands on
     INTERACTION / NAVIGATION  the panel, deep links, keyboard, the run picker
     MOBILE / RESPONSIVE       and there is a MEASURED DEFECT, §6

OUT  the chatbot and its question box -- ruling 83 specifies it and a
     SEPARATE block builds it. If the design block draws a search box it has
     designed the chatbot's front end before the chatbot block has decided
     anything, and that block will inherit a picture instead of a decision
OUT  curating a record, authoring a coordinate, touching p7-answer-v2r or
     chat-default, re-pointing floor.json's digest pin. Unchanged from
     UI_START.md section 10
```

**If only one of the four is taken, take VISUAL.** It is the lowest-risk against
the guards, it is almost entirely CSS, and it is the one whose absence a visitor
notices in the first two seconds.

**If two, take VISUAL and MOBILE**, for the reason in §6: the page currently
scrolls sideways on a phone, and this is a portfolio piece that people will open
from a link on a phone.

---

# 4. THE THIRTY-NINE GUARDS, AND WHICH ONES WILL FIGHT YOU

**This is the section that saves the design block a day.** `node ui/check_ui.mjs`
is the gate. It was extended in the UI block specifically so that a later
redesign would be cheap, and the extensions were written against
`data-*` attributes rather than against prose for exactly this reason.

## FREE — rewrite anything, these will not notice

```
Every check asserting on data-span-state, data-provenance, data-date-verdict,
data-place, data-group, data-edge, data-record, data-marker.
```

**You may change every sentence, every colour, every class name, every layout
and every font on this page without touching these**, as long as the elements
still carry those attributes. That is fourteen checks, including all of FINDING
98's, all of the second axis's, and all of A6's date verdicts. **They were
written this way on purpose. Use the freedom.**

## CAREFUL — these assert on structure, and a redesign can break them honestly

```
"index.html has exactly one inline script"
     -> splitting the script into modules FAILS this. It is not a style rule:
        check_ui.mjs extracts and runs that single script in a VM, and that is
        how every render check works at all. Changing it means changing the
        harness, deliberately, in the same commit

"every quotation appearing in an answer is highlighted (1289/1289)"
"all 1227 'resolved' spans hold their quoted characters"
     -> these are THE POINT OF THE PAGE. If a redesign moves them, the
        redesign dropped a citation. Never adjust these to fit a design

"no rendered answer emits a tag with a newline or a stray '<' inside it"
     -> FINDING 99's guard, and the one a redesign is MOST LIKELY to trip,
        because it fires the moment somebody wraps an emitted tag across two
        lines for readability. That is exactly how FINDING 99 happened. If it
        goes red, the fix is to put the tag back on one line, never to relax
        the check

"every cached point/extent (63) is drawn on the map"
"every drawable edge (19) is drawn on the map"
"all 54 records are clickable from the Places tab"
"every placement is listed on its own record's panel (169 checked)"
     -> a redesign that hides something behind a disclosure element still
        passes these, because they check the rendered STRING. A redesign that
        DROPS a card to tidy the page fails them, correctly

"the coastline renders land as land and sea as sea (9 control points)"
"zooming never distorts the projection's aspect ratio"
"reset returns exactly to the full extent"
     -> restyling the map is free. Reprojecting it is not
```

## THE ONE THAT IS ABOUT DESIGN ITSELF

```
"no view prints a record count that disagrees with the bundle (54 records)"
"every language code in the corpus has a name on screen"
```

**These exist because the page shipped `"All 24 records, by region"` and
`"a corpus of 24 primary sources"` while the corpus was 54.** Every count on
this page is now derived. **A redesign that types a number into new prose
re-creates the exact defect the UI block spent an hour removing** — and the
first guard only hunts the two sentences that were actually wrong, so it will
not catch a *new* typed number. **Derive every figure you print. There is no
figure on this page that cannot be derived; the helpers are already there
(`corpusLanguages()`, `listOf()`, `placeLedger()`).**

---

# 5. THE THINGS ON THIS PAGE THAT LOOK LIKE STYLE AND ARE ARGUMENTS

**Do not "clean these up". Each is load-bearing and each has a comment above it
saying so.**

- **`ground` is told apart by SHAPE, never by colour.** A `regional` claim draws
  as a shaded extent and never as a pin. Reusing `--good/--warn/--bad` for it
  would assert an ordering this project has explicitly refused — *"stated on a
  Greek port and regional on a Chinese polity are different kinds of claim, not
  different strengths of one"*. **A designer's instinct to unify the status
  colours across the page is the exact thing to resist here.**
- **D1's second axis is told apart by LABEL, never by colour**, for the same
  reason and by the same precedent. `changed` is not worse than `unchanged`, and
  `unrecorded` is not a failure.
- **The first axis IS an ordering and is allowed its colour ramp.** It says
  whether a claim still holds. It is the one axis on the page where a ramp is
  honest. `whitespace_only` is deliberately neither red nor amber — a dotted
  underline on the plain highlight — because FINDING 42 says it is neither a
  broken claim nor a labelling defect.
- **The confidence machinery is shown DORMANT rather than hidden.** Hiding it
  loses the work the moment Phase 2 adds material with no published English;
  showing it as if it were live would be a lie.
- **Labels are dropped on the map where they would collide**, in a deliberate
  order (most-referenced first, then extents, then alphabetical). Not
  incidental, and the order is stated so it cannot silently become "whichever
  sorted last".
- **`.gitattributes` is `* -text` and is load-bearing.** 168 archived citation
  spans point into the corpus by exact offset.

---

# 6. THE MEASURED STATE OF THE FOUR SCOPES

## MOBILE — **there is a real defect and here is its exact cause**

Rendered at 390×844 and 820×1180 at the close of the UI block:

```
390px  Questions tab   body 390 = viewport 390        no overflow
390px  PLACES tab      body 454 vs viewport 390       SCROLLS SIDEWAYS
820px  both tabs       no overflow
```

**The cause, found by walking the DOM rather than guessed:** `.rail-right.panel`
renders **426px wide inside a 390px viewport**. The Places tab's bottom `.cols`
carries an **inline** `style="grid-template-columns:minmax(0,1fr) 400px"`, and
an inline style beats the `@media (max-width: 860px) { .cols { grid-template-columns: 1fr } }`
rule that is supposed to collapse it. The Questions tab has no inline override
and collapses correctly. **One line, and it has probably been wrong since A5.**

**And the phone layout has a worse problem than the overflow.** On a 390px
screen the header's stat strip takes five stacked lines and consumes the entire
first screen; the tab labels wrap inside their own boxes; and a visitor then
scrolls past **33 question buttons** before reaching a single answer. **A phone
visitor currently sees a wall of statistics and a list of questions, and never
reaches the thing the page is for.**

## INTERACTION — **the page has no URL state at all**

**Nothing on this page can be linked to.** Not a question, not a run, not a
citation, not a place. For a page whose entire claim is *"click any highlighted
phrase and see the characters on disk"*, **you cannot send someone the
characters on disk.** `state` is a module-level object and never touches
`location.hash`.

**This is the single highest-value interaction change and it is not a large
one.** `state` already has exactly the four fields a hash would need
(`view`, `question`, `runIndex`, `selection`).

**The run picker is the other measured problem:**

```
33 questions, 685 runs
runs per question   max 42   median 17   min 17
questions with >20 runs   6
```

**Every question has at least 17 runs and the picker draws a chip for each**, so
the default question renders 41 chips in a six-row block above the answer.
`defaultRunIndex` picks a good one, and the reader has no idea why that one or
what the other 40 are for. **The variation between runs is real and this project
measured it — that is worth showing, and forty-one undifferentiated chips is not
showing it.**

## INFORMATION ARCHITECTURE — what a first-time visitor actually meets

```
answer length      min 0    median 354 chars    max 1609
passages per run   median 6, max 6
refused runs       242 of 685 -- more than a third
longest question   70 chars       longest record title  244 chars
```

**Two things worth deciding rather than inheriting.** First, a visitor lands on
the Questions tab, on a question they did not choose, on a run chosen by
`defaultRunIndex` — and the tab named *"What you are looking at"*, which explains
all of this, is third. **The page explains itself in the last place anyone
looks.** Second, that 244-character record title exists and will break any card
design that assumes titles are short.

## VISUAL — the honest inventory

One serif stack (`Iowan Old Style`/Palatino/Georgia) for prose, one system stack
for apparatus, one mono stack for identifiers. Six greys, one brown accent,
three status colours, one highlight yellow. A single `--radius: 8px`. No dark
mode, no motion, no scale beyond ad-hoc `font-size` values scattered through the
markup — **there are inline `style="font-family:system-ui,...;font-size:11px;..."`
attributes repeated on several `<h2>` elements, which is the clearest sign
nobody has yet built a type scale.**

---

# 7. FIRST FIVE MINUTES

1. **`pip install "psycopg[binary]" sqlglot` on the bridge first.** Without them
   `scripts/state_block.py` reads `scripts/test_recover_baseline.py` as **RED**
   and `answer.test_answer` as **149**, and neither is about the repository.
   FINDING 94, and the RED half is the dangerous one because 149 announces
   itself as a skip and RED does not.
2. `python -m ingest.verify --state` and `python scripts/state_block.py`.
   Confirm 54 documents, 170 chunks, `ingest.test_fidelity` 145, eleven
   instruments green, and `node ui/check_ui.mjs` **GREEN at 39 checks**. If not,
   stop.
3. **Read `ui/index.html` whole.** It is now ~108KB. This instruction is not
   ceremony: in the UI block it is what found both FINDING 98 and the
   architecture that a "rebuild" would have thrown away.
4. **RENDER THE PAGE AND LOOK AT IT, at 1600px AND at 390px, before changing
   anything.** This is not optional and `UI_RESULT.md` §2 is why. **Twice now —
   the inside-out coastline, and every citation marker on the page being broken
   HTML — the only instrument that worked was looking.** A design block that
   does not look at the page before redesigning it has no baseline.
5. **Write the predictions and commit them BEFORE any code**, ruling 78's
   practice. For a design block the useful predictions are: which of the 39
   checks you expect to go red and why, what the phone overflow is after the
   fix, and **which of your intended changes you expect to abandon once you see
   it rendered** — that last one is the prediction worth being wrong about.

---

# 8. WHAT THIS BLOCK MUST NOT DO

- **Not build the chatbot or its question box.** Ruling 83; a later block.
- **Not curate a record.** 54 in, 54 out.
- **Not author a coordinate.** Not one, ever.
- **Not type a count into prose.** Derive it. §4.
- **Not relax a check to fit a design.** If FINDING 99's guard goes red, the tag
  went back across two lines and the tag is what is wrong.
- **Not merge the two verify axes**, or render `unrecorded` as anything but its
  own third answer.
- **Not hand-edit `ui/data.js`.** `python ui/build_ui_data.py` is how it moves,
  and it writes `ui/data.manifest.json` beside it — **which is how you review
  your own change to a 9.5MB single-line file.** `git diff --stat` will only
  ever tell you it is `2 +-`.
- **Not split the inline script** without changing `check_ui.mjs`'s harness in
  the same commit, deliberately.
- **Not assign ruling or finding numbers from this document.** `RULINGS.md` is
  the authority and the next free number is read from it at the time. As of
  2026-09-07 the next free ruling is **84** and the next free finding is
  **100** — and `RULINGS.md`'s index still does not cover 53 to 79, for the
  reason written under its table.

---

# 9. ONE THING THE DESIGN BLOCK COULD EARN THAT NOBODY HAS ASKED FOR

**The page's best material is buried.** *One coordinate, taken 2 times and
refused 9* is the sharpest thing this corpus says about itself, and it is the
third card down on the second tab. *Every one of the eleven failing citations is
in the unknowable bucket* is a paragraph inside the third tab. **A visitor who
spends ninety seconds on this page currently leaves with "nice map".**

**That is an information-architecture problem wearing a visual-design costume**,
and it is the one place where design work would make the project *more*
convincing rather than merely better-looking. Worth naming as a goal in the
design block's predictions, so it can be scored rather than admired.
