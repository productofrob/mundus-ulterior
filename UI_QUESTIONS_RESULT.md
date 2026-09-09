# UI QUESTIONS RESULT — **PART ONE SCORES THE PREDICTIONS. PART TWO CARRIES THE
# NINETEEN COMMITS THAT FOLLOWED AND IS WHERE THE HARNESS COUNT LIVES.**
#
# **THE RULE ROB ASKED FOR WOULD HAVE DELETED THE SEVEN QUESTIONS THIS CORPUS
# REFUSES CORRECTLY, AND THAT WAS FOUND BY MEASURING IT BEFORE BUILDING IT.**
# The rail is grouped by region, the run apparatus is gone, and one prediction is
# refuted for a reason worth more than the four that held.

*Written 2026-09-08 at the close of the Questions block.
`UI_QUESTIONS_PREDICTIONS.md` was committed at `ea87767` **before a line of
`ui/` was edited** and is not amended here — it is scored.*

---

## THE STATE BLOCK IS GENERATED. NOTHING BELOW IT IS RESTATED.

`python scripts/state_block.py`, after the block:

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

**`node ui/check_ui.mjs`: 43 checks at the open, 45 at the close, 0 failures.**
Both new guards were verified to FAIL on a broken version before being believed.

**`ui/data.js` was not regenerated and does not appear in any diff.** Five
commits:

```
ea87767  the predictions, before a line of ui/ was edited
b50bcf4  FINDING 100 fixed -- the harness, in its own commit
9d7f701  FINDING 101 fixed -- write BYTES, and a CR guard over the seed corpus
d32aa79  the rail grouped by region, the run apparatus gone, 43 -> 45
(this)   the rulings, the register, and this document
```

---

# 1. THE FIVE PREDICTIONS, READ

## P1 — WHICH CHECKS GO RED. **CONFIRMED, INCLUDING THE STRUCTURAL HALF.**

No check was red at any commit left standing. The count went **43 → 45**, the two
guards named in advance and no others.

**The prediction that was worth making is the one about check 5.** It named
`rendered all 685 runs` as the check genuinely at risk, because the obvious way
to build a filtered rail is to filter `QUESTIONS` — and `QUESTIONS` is also the
default question, `questionBySlug`, and the Home chain figure's example. It was
built the predicted way instead: `QUESTIONS` is untouched at all 33 in archive
order and the rail is a derived view (`railPartition`).

```
check 5    rendered all 685 runs        685, never fired
check 43   the chain figure             the same quotation, byte for byte:
                                        periplus-muziris.json:reference_translation[1967:2071]
data-*     fourteen checks              not one fired
```

**Not one `data-*` check fired for the third block running**, and this block
rewrote the rail's markup completely, deleted seven CSS classes and a click
handler, and merged two cards into one. The freedom the design block claimed was
built is still real.

## P2 — THE NUMBERS THE EXCLUSION RULE PRODUCES. **CONFIRMED, EXACTLY.**

```
PREDICTED   24 in the region rail   7 refusals   2 withheld
BUILT       24                      7            2

PREDICTED   South Asia 4  Scandinavia 4  Sub-Saharan Africa 4
            East Asia 3   Arabia 3       Persia 3   Southeast Asia 3
BUILT       identical, and printed by the page's own railPartition()
```

**And the predicate is insensitive to its spelling, as predicted.** Whether "the
run claims a character span" is read as `abs_start != null` or as
`resolution.state === "resolved"`, the same nine questions drop — measured both
ways before a line was written. A filter whose result moves when you rephrase it
is a filter about the phrasing.

**The substantive finding of this block was made here, before any code.** Rob's
rule — *exclude questions with no grounding, no citation, or refused* — was
measured against the archive before it was implemented, and **seven of the nine
questions it excludes are cases `gold.answer_cases` declares
`correctly_refusable`.** The system refused them because refusing was right:
Antikythera, planted from outside the empire; a tax rate, a DNA result, a list of
emperors and a runic reading the corpus does not contain. Applied literally, a
rule written to keep a visitor away from an empty answer would have deleted the
strongest evidence on the page — that this system declines rather than
confabulates — and left a portal on which the machine always answers.

Rob took the measurement and ruled: the seven are grouped and labelled, the two
genuine failures are withheld and counted. **That is RULING 86, and it exists
because the rule was measured before it was believed.**

## P3 — WHAT THE PAGE MEASURES AFTERWARDS. **THREE CONFIRMED, ONE REFUTED, AND THE REFUTATION IS THE USEFUL ONE.**

```
                              OPEN     PREDICTED       CLOSE
1600px  first answer line     1184     under 1120      1050    CONFIRMED
1600px  page height           4113     under 4050      3512    CONFIRMED
 390px  page height           5817     -400 or more    5120    CONFIRMED (-697)
 390px  first answer line     1604     within 40px     1344    REFUTED (-260)
```

**REFUTED, and the cause is a plain error of reasoning rather than a surprise in
the data.** The prediction argued that at 390px the rail is ordered *after* the
answer, so removing 33 meta lines could not move the answer — which is true of
the rail and says nothing about the picker, and **the picker sat directly above
the answer at every width.** Three of its four lines were on the phone too. I
predicted about the change I was thinking hardest about and forgot the other one
was in the same column.

It is worth recording rather than waving through, because the prediction was
constructed to be the one that did NOT improve — *"a prediction that everything
improves is not a prediction"* — and the discipline failed in the direction that
flatters the block.

## P4 — WHAT I EXPECTED TO ABANDON. **CONFIRMED, ALL FOUR.**

```
1  REGION GROUPS AS collapsed <details>     ABANDONED, as predicted. Seven
                                            closed discs hide a rail's whole
                                            content to save scroll it does not
                                            cost
2  A DERIVED LINE counting the withheld     KEPT. It reads "2 further questions
   failures                                 are archived and not listed: their
                                            runs never produced a grounded
                                            answer that quotes anything, and
                                            they are a failure rather than a
                                            refusal"
3  REMOVING the rail's "every run is        KEPT (removed). With no picker on
   kept; none is hidden" note               screen it was a promise the page
                                            had stopped keeping
4  MAKING the two withheld questions        ABANDONED, as predicted. Both still
   unresolvable by URL                      resolve; they are unlisted, never
                                            unreachable
```

## P5 — THE TWO FINDINGS THIS BLOCK CLEARS. **REFUTED ON THE SHAPE OF THE FINDING 100 FIX. CONFIRMED ON EVERYTHING ELSE.**

**FINDING 100 — REFUTED: it is not one line, and it should not have been.**

The prediction assumed the fix was the lookahead — teach `(?![^>]*\bsrc=)` to
exclude a bare `<script src>` as well. Writing it exposed that the lookahead was
never the defect. **The defect is that the harness matches script tags inside
HTML comments at all**, and a `<script>` written out in full inside a comment
would still have been miscounted by the "fixed" one-line version. The finding's
own headline says so and the prediction did not read it closely enough.

The next attempt — strip comments from `html` before matching — was written and
then abandoned on inspection: **`scripts[0]` is what gets EXECUTED in the VM**,
one of the page's own template strings contains an HTML comment, and a harness
that runs a lightly-edited copy of the file asserts about something that does not
ship. What is committed computes the comment ranges once and drops matches that
START inside one, so every captured body is still byte-for-byte what is in the
file.

**Verified three ways before being believed:** green at 43 on the file as it
stands; **RED** on a genuine second inline script inserted above the `data.js`
tag; and green on FINDING 100's own trigger — a comment writing the tag out —
which **the original harness still fails**, reproducing the finding on demand.

**FINDING 101 — CONFIRMED, including the half that was an open question.**
`build_ui_data.py` writes BYTES now, which is FINDING 52's rule for this
repository reaching the one file it had not. `ingest.verify` asserts that no seed
record holds a CR, reading **bytes** — reading those files as text is exactly the
operation that hides the defect, since universal newlines turn `\r\n` back into
`\n` on the way in. **The guard finds zero on the corpus as it stands**, which
was the prediction and the thing worth knowing: the hazard has not landed on the
168 archived citation spans that point into those records by exact offset. It was
verified RED first, on a copy of `data/seed_corpus/` with three CRs injected into
one record, and it names the file.

**§3E, the owed mutation run — CONFIRMED, with one figure to correct.**
`python scripts/mutate_ui_places.py` ran on the bridge: **all 6 mutations
verified, sources restored, `git status --porcelain` clean.** Nothing moved, as
predicted. **`UI_RESULT.md` §6's last recorded figure was `4 GREEN` and it is 6
now** — two guards were added to that harness after that line was written. The
figure was stale, not wrong, and this is the sentence that stops the next thread
reading `4` as the expected count.

---

# 2. FINDING 102 — **CLICKING A QUESTION FROM THE FOOT OF THE RAIL PUT THE
# ANSWER OFF THE TOP OF THE SCREEN.**

Measured while using the rebuilt page: scrolled to the bottom of the rail and
clicking a question left the answer **1,461px above the viewport at 1600px, and
2,505px above it on a 390px phone.** A visitor clicks a question and nothing
appears to happen.

**It has been true since the rail existed** — 33 buttons have always been taller
than one answer — and this block made it easier to reach, because the refusals
group is deliberately at the bottom and is the part worth clicking.

Fixed in the same commit, and narrowly: the answer column is brought into view
**only when it is not already in view**, so a reader who was already looking at
the right thing does not have the page taken from under them. After the fix, a
click from the foot of the rail lands the question 23px into the viewport at
1600px and 17px at 390px.

**No check would have caught it, and no check was added for it.** Every guard
here asserts that a view RENDERS and that its content is reachable, and all of
that was true throughout. It is a fact about scroll position after a click, which
the harness's DOM does not have and should not grow one to hold.

---

# 3. WHAT LOOKING CAUGHT THAT NO CHECK WOULD HAVE

Two, and the count on this project is now eight.

- **FINDING 102**, above.
- **The question sat alone in a card the height of three lines.** With the picker
  gone, its card held one sentence and a copy-link button in a box built to hold
  four lines of apparatus — which reads as something missing rather than as room.
  The question moved into the answer card. Nothing measured this; it was visible
  in the first screenshot after the picker came out.

---

# 4. WHAT THE BLOCK BUILT

```
THE RAIL     Seven region groups from gold.answer_cases -- where a person
             declared the region, not counted from which records a retriever
             happened to return -- then a labelled refusals group, then one
             derived line counting the withheld failures. 33 questions in,
             33 accounted for, guard 44

RULING 85    The run picker retired. A run keeps its ADDRESS and loses its
             CONTROL: #q/<slug>/r/<stamp> resolves exactly as ruling 84
             defined it, and nothing on the page offers the other runs. The
             chosen-run line, the five-figure spread, the 41-chip disclosure,
             the per-question meta line on 33 buttons, the fourth badge
             printing the prompt version, the .runchip handler, shortTime()
             and seven CSS classes went with it

RULING 86    What the rail lists, why the seven refusals are grouped rather
             than deleted, why the two failures are counted rather than
             dropped silently, and that QUESTIONS itself stays unfiltered

GUARD 44     the rail is a PARTITION of the archive -- every question in
             exactly one group. Verified red by dropping one question, which
             the guard then named
GUARD 45     the two groups hold what they claim -- no region question without
             a showable run, no refusal gold does not declare
             correctly_refusable. Verified red by sending every excluded
             question to the refusals group, which the guard then named,
             correctly, as the two failures

FINDING 100  fixed, in its own commit, in the harness
FINDING 101  fixed, and the seed corpus proved clean
FINDING 102  found by using the page, fixed in the same commit
```

---

# 5. WHAT THIS BLOCK DID NOT DO

- **Did not build the chatbot or a question box.** Still ruling 83, still a
  later block.
- **Did not curate a record or author a coordinate.** 54 in, 54 out.
- **Did not regenerate or hand-edit `ui/data.js`.** It is in no diff.
- **Did not filter `QUESTIONS`.** The rail is a derived view; every archived
  question is still addressable, including the two the rail does not list.
- **Did not relax a check**, and did not weaken the one it fixed: the repaired
  FINDING 100 check was shown red on a real second inline script before it was
  believed.
- **Did not split the inline script.** Still one.
- **Did not take `UI_QUESTIONS_START.md` §3A**, the Map tab's panel 7,500 pixels
  below its map. Decided with Rob rather than inherited by silence: it is a
  different tab, a different layout and a different set of predictions, and it is
  still the largest known defect on the page.
- **Did not read a rights position.** The 38 unread still gate a public URL.

---

# 6. FOR WHOEVER OPENS THE NEXT BLOCK

- **`railPartition()` is the contract, not the markup.** It returns data —
  regions, refusals, withheld — and `check_ui.mjs` asserts the partition against
  `QUESTIONS` without matching a word of prose. A redesign of the rail that keeps
  that function keeps both guards.
- **A fifth view still needs adding to `check_ui.mjs` by name** the day it exists.
  That was the design block's warning and it is unchanged.
- **The two withheld questions are unlisted and resolvable.** If a later block
  wants them reachable from the page, they are one derived line away; if it wants
  them gone, that is reversing RULING 86 and needs its own number.
- **The layout figures in §1's P3 are measured headless on Linux**, where the
  serif stack falls back. They are internally consistent — same instrument at the
  open and the close — and they are NOT comparable with `UI_QUESTIONS_START.md`
  §2's host figures. Measure your own baseline before scoring against them.
- **FINDING 103, and it is about the bridge rather than the repository.** Git
  cannot commit from the Linux bridge unless file deletion is enabled for the
  folder: it creates and removes `.git/index.lock` and `HEAD.lock` on every
  commit, and an unlink that fails leaves a lock behind that blocks every
  subsequent attempt. This session found a stale `index.lock` already sitting
  there, dated before it started — the fossil of an earlier attempt that hit the
  same wall. Enable deletion for the repository folder at the start of a block,
  not in the middle of one.

---
---

# PART TWO — **NINETEEN COMMITS OF ROB'S OWN EDITS FOLLOWED THE CLOSE, AND ONE
# OF THEM UNCOVERED A DEFECT THAT HAD BEEN ON THE DATA & SOURCES TAB THE WHOLE
# TIME.**

*Appended 2026-09-09. Everything above this line is the block as originally
scoped, scored against `UI_QUESTIONS_PREDICTIONS.md`, and is **not edited** — the
five predictions stand as they were read. The design block left its own result
document saying 39 checks while the harness said 43, and recorded that **a result
document that has gone stale is worse than no result document**. This is that
lesson applied to this one.*

---

## THE STATE BLOCK IS GENERATED. NOTHING BELOW IT IS RESTATED.

`python scripts/state_block.py`, at `c78ebab`:

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

**`node ui/check_ui.mjs`: 45 checks at Part One's close, 47 now.** Guard 46
(RULING 87) and guard 47 (RULING 89). Every guard added or moved in this half was
verified to FAIL on a broken version first, and the two that MOVED were verified
red on both of the failures they inherited.

**`ui/data.js` was not regenerated and appears in no diff.**

---

# 7. WHAT THE NINETEEN COMMITS DID

Rob directed all of it, after seeing the page rendered. Grouped by surface
rather than by commit:

```
THE HEADER      'on disk' out of the citation line, and the strip now on EVERY
                tab -- it used to stand down on the Questions landing, which
                made it a thing that appears and disappears as you move around

THE FRONT       A new headline and claim. Two captions reworded. THE TWO FINDING
SECTION         CARDS REMOVED -- the contested coordinate and 'what the failures
                say' -- both of which survive as full cards on the tabs they
                came from

THE RAIL        The refusals note moved ABOVE its questions, the group renamed
                'Not fully answerable', and the withheld-failures line removed

THE REFUSALS    RULING 87. Each of the seven now says WHICH KIND of refusal it
                is, in one sentence, and guard 46 re-derives every claim those
                sentences make -- 7 reasons, 24 claims

THE SOURCE      The cosine bar and its value off the cards; similarity, file and
CARDS           rank off the panel behind them

THE PANEL       1,276px -> 844px. Out: file, characters, chunk, the partial-
                archive box, and the whole 'has the record moved' section
                (RULING 88). In: region, language, date, findspot. 'the
                characters on disk' and 'the passage, as it sits in the file'
                are both 'Source Characters' now

THE NOTES       RULING 89. 54 curator's notes read; the page shows a declared
                VERBATIM EXCERPT of each, sliced by ui/build_public_notes.py and
                re-derived by guard 47

THE BAND        Ge'ez and Korean swapped, so the opening view carries Africa
                rather than a second East Asian script
```

---

# 8. THE TWO RULINGS THAT ARE ABOUT GUARDS RATHER THAN ABOUT DESIGN

**RULING 88 is the one worth reading before touching a guard on this project.**
Rob asked twice for the second axis to come off the quotation panel, and ruled
out both relaxing a guard and losing the information. Checks 30 and 31 asserted
against the panel's own HTML, so the honest move was neither to delete them nor
to point them at something weaker: **the axis moved to the Data & Sources
cross-tabulation, and the guards moved with it and got stronger.** The old pair
could say only that a state APPEARED in a panel; the new pair re-derives the
whole cross-tabulation and asserts every cell is on screen **with its own count**.

**And on its first run it found FINDING 105**, which had been live on the Data &
Sources tab for as long as that tab existed: `spanCrossTab()` keyed its map with
a **literal NUL byte** typed into `index.html` — which is why `grep` had been
reporting that file as binary — while `viewAbout` split those keys on a space, as
its own comment said it could. Every row of the cross-tabulation was rendering as
`resolved<?>changed — 1070 spans —` with **no provenance label and an empty tag**,
and the `cross["resolved unchanged"]` lookup beside it read 0 whatever the
archive held. It printed correctly by luck: `unchanged` is genuinely 0.

**No check caught it, because the guard in force asserted an attribute on a
panel, and the attribute was there.** The lesson is the one the design block kept
finding from the other direction: a guard that asserts PRESENCE cannot see a
value that is wrong.

---

# 9. WHAT IS OWED, AND ALL OF IT IS OWED TO ONE TAB

Three claims left the Questions tab in this half and **have not yet landed
anywhere else.** They are recorded in the source at the point of each removal,
and they are listed here because a commit message is not where the next thread
looks.

```
1  THE TWO WITHHELD FAILURES         Ruling 86 says they are COUNTED rather
   (ruling 86 owes an amendment)     than dropped silently, because Home says
                                     'the failures are kept'. The line came off
                                     the rail. Until the count is stated on Data
                                     & Sources the page is one claim short of
                                     what Home promises, and ruling 86 should be
                                     amended in the commit that lands it

2  THE PARTIAL-ARCHIVE SUBSTITUTION  16 of the 685 runs, across 5 questions, were
                                     reconstructed from a partial archive, and
                                     their panels show a language and a region
                                     taken from the seed record rather than from
                                     the run. The box that said so is gone and
                                     the substitution still happens

3  THE SECOND AXIS                   Already there, already guarded (ruling 88).
                                     Listed so the next thread does not think it
                                     owes it twice
```

**And one thing the Map tab is owed:** `renderPanel`'s empty state is ONE STRING
SERVING TWO TABS, and the clause it lost — *"or, on the Places tab, a point, a
shaded region or a line"* — was the Map tab's only instruction. That tab now
opens with a panel describing things it does not have.

---

# 10. WHAT LOOKING CAUGHT, AND ONE THING IT DID NOT

**FINDING 102**, in Part One, and the question card that was left holding one
sentence in a box built for four lines — both found by rendering the page.

**And the counter-example, which is the more useful half.** The `rank` row was
left on the source panel in `bb25cb2` on the stated ground that "no passage in
this archive carries one, so it prints for nothing today". **That was asserted
without measuring, and it is false**: 4,014 of the 4,110 passages carry a rank
and it rendered on nearly every source panel. It was caught by looking at a
screenshot two commits later, corrected in the log rather than fixed quietly, put
to Rob, and the row came off in `c78ebab`.

**A sentence written into a commit message is as capable of being wrong as a
sentence written onto the page, and nothing checks the commit message.**

---

# 11. WHAT THIS HALF DID NOT DO

- **Did not build the chatbot or a question box.** Still ruling 83.
- **Did not curate a record or author a coordinate.** RULING 89 reads all 54
  notes and edits none of them; the excerpts are a view of the corpus, not a
  change to it.
- **Did not regenerate or hand-edit `ui/data.js`.**
- **Did not relax or delete a guard.** Two moved surfaces, both to a place that
  carries the same claim, both verified red on the failures they inherited.
- **Did not touch the Map tab**, which is a thread of its own and now carries the
  §9 debt above.
- **Did not amend the predictions.** They are scored in Part One and stand.

**`RULINGS.md` reads next free ruling 90, next free finding 106.**
