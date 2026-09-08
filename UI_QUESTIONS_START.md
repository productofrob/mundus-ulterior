# UI QUESTIONS START — **THE PAGE IS DESIGNED NOW, AND THE QUESTIONS TAB IS THE
# ONE SURFACE THE DESIGN BLOCK BARELY TOUCHED.**

*Written 2026-09-08 at the close of the design block, for the thread that edits
the Questions tab. **Nothing here was measured by that thread; it is a scope and
a set of constraints**, assembled from `UI_DESIGN_RESULT.md`, `RULINGS.md` and
the state of `ui/` on disk at `db89c3e`. Every figure is transcribed from those
or measured at the close. **The first thing the new thread does is confirm the
state block still reproduces** — if it does not, stop and find out what moved.*

---

# 1. WHERE THE PROJECT IS, IN FIVE LINES

**The design block closed clean over ten commits.** The page has a token layer,
a dark theme, four tabs, deep links under RULING 84, a masthead script band and
map, and a figure on Home that draws the whole provenance chain from a real
answer. `check_ui.mjs` went 39 checks to 43, all green, and
`build_ui_data.py --verify` reads byte-identical on both axes.

```
54 records          170 chunks          685 archived runs
33 questions        1289 citation spans 63 places drawn, 90 not
43 checks green     eleven instruments green
```

**Read `UI_DESIGN_RESULT.md` whole before this document's §4.** Its Part Two is
what a thread will otherwise rediscover.

**The next free ruling is 85 and the next free finding is 102.** `RULINGS.md` is
the authority; read it at the time anyway.

---

# 2. WHAT THE QUESTIONS TAB IS NOW, MEASURED

Rendered at `db89c3e`. `#questions` is the tab's own landing (front section
showing); `#q/<slug>` is a visitor who has clicked something.

```
1600px  #questions   page 3923   first answer line at 1185   panel at  955
1600px  #q/...       page 3371   first answer line at  633   panel at  403
 390px  #questions   page 5700   first answer line at 1559   panel at 2875
 390px  #q/...       page 4767   first answer line at  626   panel at 1942
```

**The panel is BESIDE the answer here**, which is the thing the Map tab gets
wrong (§5). At 390px it is ordered after the answer and before the question
list, and the question list is last.

What the tab holds today:

```
LEFT RAIL     33 question buttons, each with its run counts
CENTRE        the question, a copy-link button, the RUN PICKER, the answer,
              then the sources that answer was given
RIGHT RAIL    the provenance panel, sticky
ABOVE ALL     the front section, when nothing has been clicked yet
```

**The run picker was rebuilt in the design block and is not obviously debt.**
One line naming the chosen run and why it was chosen, the spread counted, and
all the chips one click away behind a disclosure grouped by prompt version.

```
33 questions, 685 runs        runs per question   min 17  median 17  max 42
questions with >20 runs   6   refused runs        242 of 685
answer length   min 0   median 354 chars   max 1609
```

---

# 3. THE FOUR THINGS OWED, AND ONE IS NOT THIS THREAD'S TO DO

## A. THE MAP TAB'S PANEL IS 7,500 PIXELS BELOW THE MAP IT ANSWERS

**Measured, and it is the worst interaction defect left on the page.** The
Places/Map tab's provenance panel sits inside the tab's BOTTOM `.cols`, below
thirteen cards and the whole region grid, where it has been since A5.

```
desktop   map at y=442     panel at y=7964     page 10753
phone     map at y=956     panel at y=17242    page 17538   map only 148px tall
```

Click a pin and the thing that answers you is eight thousand pixels down. On a
phone the map is a postage stamp and the panel is sixteen thousand pixels away.
**No check catches this** — every guard asserts the panel RENDERS and that
placements are reachable from it, and all of that is true.

It is on the Map tab, not the Questions tab. **It is written here because it is
the largest known defect on the page and the next thread should decide
deliberately whether to take it, not inherit it by silence.**

## B. THE 38 UNREAD RIGHTS POSITIONS. **GATES A PUBLIC URL, NOT THIS THREAD.**

```
open_licence_stated 5, permission_stated_no_licence 3, public_domain 2,
all_rights_reserved 2, states_no_terms 1, two_positions_stated 3, UNREAD 38
```

`unread` is a state of this project's knowledge and not of the source, and
counting-not-gating it is honest for a file you open by double-clicking. **A
public URL showing source text and published translations is a different act.**
RULING 74 refuses a matcher over `citation_original`; FINDING 69 exists because
two licence claims were checked in one session and were wrong in opposite
directions. **Read by a person, off each source.**

This also blocks the strip of object images on Home: only two of the 54 records
are objects whose rights have been read, and both are held by institutions with
open-access image programmes — which is precisely the shape FINDING 69 warns
about.

## C. FINDING 100 — the harness counts script tags inside comments

`check_ui.mjs`'s first check matches `<script(?![^>]*\bsrc=)`. The lookahead
excludes `src=` but not `<script src>` with no equals sign, so **a comment
describing a script tag is counted as a second inline script** and the harness
goes red pointing at the page rather than at itself. Fails safe; recorded rather
than fixed, because a block quietly editing the guard file it is judged by is
worse than the defect. **One line to fix, deliberately, in its own commit.**

## D. FINDING 101 — a Windows write puts CRLF into files stored verbatim

`build_ui_data.py` writes with `Path.write_text`, which is text mode: on Windows
every `\n` becomes `\r\n`, and `.gitattributes` is `* -text`, so git stores them.
It surfaced on `ui/data.js` where it is harmless. **It would not be harmless on
`data/seed_corpus/`**, where 168 archived citation spans point into the records
by exact byte offset. The fix is `newline=""` or writing bytes, plus a check that
no tracked file under `data/seed_corpus/` contains a CR.

## E. STILL OWED FROM THE UI BLOCK, AND IT IS ONE COMMAND ON THE HOST

`UI_RESULT.md` §6 asked for a mutation run and **there is no record it ever
happened.** Its last recorded figure is `4 GREEN`.

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
python scripts\mutate_ui_places.py
git status --porcelain
```

Host-only, FINDING 59. Nothing either block added is inside
`check_placement_shape`, so nothing is expected to move — **which is exactly why
it should be run rather than assumed.**

---

# 4. THE FORTY-THREE GUARDS, AND WHICH ONES WILL FIGHT YOU

`node ui/check_ui.mjs` is the gate. `UI_DESIGN_START.md` §4's inventory still
holds for the original 39 and is not restated. **Four are new and three of them
are about surfaces this thread might touch.**

## FREE — rewrite anything, these will not notice

Every check asserting on `data-span-state`, `data-provenance`,
`data-date-verdict`, `data-place`, `data-group`, `data-edge`, `data-record`,
`data-marker`. **The design block rewrote every view's markup, retired seven
inline `style=` attributes, restructured the run picker and added two tabs
without moving one of them.** The freedom is real. Use it.

## CAREFUL — the four added since

```
"the home view renders"
     -> viewHome is exported BY NAME. A fifth view needs adding here the day
        it exists, or it ships unguarded

"every masthead specimen has its record, its characters and its image"
"native script and romanised transliteration are not confused"
     -> the specimen list is declared TWICE, in index.html and in
        ui/build_banner.mjs. Change one and this fails. That is the point:
        regenerating the images is `node ui/build_banner.mjs`, and the widths
        it prints must be carried into index.html's BANNER

"the chain figure draws a quotation that still resolves"
     -> the figure is chosen at RENDER TIME from the archive, so it can change
        without anyone editing a line. If the default question or its default
        run changes, this check is what tells you the figure still makes a true
        claim
```

## AND THE OLD ONES THAT STILL MATTER MOST

```
"index.html has exactly one inline script"
     -> still one. FINDING 100 lives here
"every quotation appearing in an answer is highlighted (1289/1289)"
"all 1227 'resolved' spans hold their quoted characters"
     -> THE POINT OF THE PAGE. Never adjust these to fit a design
"no rendered answer emits a tag with a newline or a stray '<' inside it"
     -> FINDING 99's guard. It did not fire once in the design block, because
        the comment above the tag says not to wrap it. Keep the comment
```

---

# 5. THINGS THAT LOOK LIKE STYLE AND ARE ARGUMENTS

`UI_DESIGN_START.md` §5 still holds in full and is not restated. **The design
block added two of its own:**

- **The glyph ink in the script band is the one colour on the page that is not a
  token.** It is baked black in the PNGs and the dark theme inverts it, because
  CSS masks — which would have taken their colour from `--ink` — do not load
  from `file://`. There is a comment saying so. Do not "tidy" it into a token
  without re-checking that mask loading still fails.
- **A specimen labelled `· romanised` is making a claim.** Five of the nine are
  the script the source is written in and four are transliteration the corpus
  actually holds. Dropping the label, or setting a transliteration in a script
  font, asserts something the corpus does not.

---

# 6. FIRST FIVE MINUTES

1. **`pip install "psycopg[binary]" sqlglot` on the bridge first.** Without them
   `scripts/state_block.py` reads `scripts/test_recover_baseline.py` as **RED**
   and `answer.test_answer` as **149**, and neither is about the repository.
   FINDING 94, and the RED half is the dangerous one.
2. `python -m ingest.verify --state` and `python scripts/state_block.py`.
   Confirm 54 documents, 170 chunks, eleven instruments green, and
   `node ui/check_ui.mjs` **GREEN at 43 checks**. If not, stop.
3. **Read `ui/index.html` whole.** It is ~170KB now. This instruction is not
   ceremony: in the UI block it found two findings, and in the design block it
   is what found the CSS-mask failure, the dropped last word of every specimen,
   and a false finding that was about to be written down.
4. **RENDER THE PAGE AND USE IT, at 1600px AND at 390px, before changing
   anything.** Not just look — *use*. The design block's clearest result is that
   **every defect in its second half was found by using the page and not one by
   the harness**, and the sharpest of them — a band that could not be scrolled
   with a mouse — was found by Rob, not by me.
5. **Write the predictions and commit them BEFORE any code**, ruling 78's
   practice.

---

# 7. WHAT THIS THREAD MUST NOT DO

- **Not build the chatbot or its question box.** RULING 83; it is step 3 of the
  sequence in `UI_DESIGN_START_AMENDMENT_1.md` and a separate block.
- **Not curate a record. Not author a coordinate.**
- **Not hand-edit `ui/data.js`.** `python ui/build_ui_data.py` is how it moves,
  and see FINDING 101 before running it on Windows.
- **Not type a count into prose.** Derive it. Every figure on this page is
  derived and the last typed one — "seven regions" on the About tab — was found
  and removed by the design block.
- **Not relax a check to fit a design.**
- **Not split the inline script** without changing the harness in the same
  commit, deliberately.
- **Not merge the two verify axes**, or render `unrecorded` as anything but its
  own third answer.
- **Not assign ruling or finding numbers from this document.** `RULINGS.md` is
  the authority and the next free number is read from it at the time.

---

# 8. ONE THING WORTH SAYING ABOUT HOW THIS BLOCK WENT

**Ten commits, four new guards, and every single guard was verified to FAIL on a
broken version of the thing it guards before it was believed.** That is the
practice worth carrying: a check written and never seen red is a check nobody
has any reason to trust. Twice in this block a guard was broken deliberately —
a moved specimen start, a chain read three characters late — and the red line it
produced named the right thing.

**And the counterweight, which is the more useful half:** not one of the five
defects in the block's second half was caught by a check. They were caught by
rendering the page and using it. **The harness is what stops a redesign breaking
what is already true; it is not what tells you the page works.**
