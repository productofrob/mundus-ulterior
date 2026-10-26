# UI QUESTIONS PREDICTIONS — **WRITTEN AND COMMITTED BEFORE A LINE OF `ui/` IS
# EDITED.** Ruling 78's practice.

*Written 2026-09-08 at the open of the Questions block, from `UI_QUESTIONS_START.md`,
`UI_DESIGN_RESULT.md` read whole, `ui/index.html` read whole at `fa01756`, and the
archive measured directly. Scored at the close and **not amended**.*

---

## THE STATE AT THE OPEN, REPRODUCED

`python scripts/state_block.py` at `fa01756`, on the bridge with
`psycopg[binary]` and `sqlglot` installed (FINDING 94):

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

`node ui/check_ui.mjs`: **43 checks, 0 failures.**

**THE LAYOUT BASELINE IS THIS THREAD'S OWN AND IS NOT `UI_QUESTIONS_START.md`
§2's.** That document measured on the host; this thread renders headless
Chromium on Linux, where the serif stack falls back and every figure lands
40–120px longer. Scoring a change against a baseline measured on other font
metrics would be measuring the fonts. Mine, at `fa01756`:

```
1600px  #questions   page 4113   first answer line at 1184   panel at 954
 390px  #questions   page 5817   first answer line at 1604   panel at 2952
```

---

## WHAT THIS BLOCK WAS ASKED FOR

Rob, in four rulings taken in conversation before any of this was written:

1. **Organise the question rail by region.**
2. **Do not land a visitor on a question the corpus cannot answer** — but the
   seven the project DECLARES correctly refusable go in their own labelled
   group rather than being deleted, because a retrieval system that declines is
   the strongest evidence on the page.
3. **Remove the run apparatus.** The per-question meta line in the rail
   (`41 archived runs · 40 grounded · 0 refused`) and the whole run-picker block
   above the answer — the timestamp, the prompt version, the "chosen because"
   sentence, the five-figure spread line, and the disclosure holding 41 chips.
4. **Runs stay addressable by URL and get no UI.** RULING 84 narrows; it is not
   reversed. `#q/<slug>/r/<stamp>` keeps resolving.

Everything below is a prediction about what happens when that is built.

---

## P1 — WHICH CHECKS GO RED, AND THE ONE THAT IS ACTUALLY AT RISK

**Predicted: no check is red at any commit left standing, and the count goes
43 → 45.**

**The check at risk is number 5, `rendered all 685 runs`, and it is at risk for
a reason worth writing down.** It iterates `QUESTIONS` — the module-level array
— and counts renders against `D.runs.length`. **The obvious way to build a
filtered rail is to filter `QUESTIONS`, and that would take the count to 24
questions' worth of runs and fire check 5 immediately.** It would also silently
change three other things that read `QUESTIONS[0]`: the default question, the
Home tab's chain figure, and therefore check 43.

So the prediction is structural, not just "it will be green": **`QUESTIONS` stays
all 33 in archive order, and the rail is built from a separate derived
ordering.** Nothing that resolves a hash, defaults a question or draws the chain
figure changes at all.

```
PREDICTED   43 -> 45 checks, 0 red at any commit left standing
            check 5 renders 685 and never fires
            check 43 draws the same quotation it draws today
            not one data-* check fires
```

**PREDICTED WRONG IF** `QUESTIONS` is filtered; if check 5 or check 43 goes red
at any point; if the count lands anywhere but 45; or if any `data-*` check
fires, which would mean the rail was rebuilt by moving attributes the guards
hold rather than by changing what is listed.

**The two new guards are named in advance:**

```
44  every archived question is accounted for in the rail exactly once
    -- listed under a region, in the refusals group, or inside the withheld
    count. The failure this exists to catch is a question that belongs to
    neither set and vanishes: a rail built by two filters that do not
    partition is a rail that silently loses a question the day the archive
    changes

45  the two groups are what they claim to be
    -- no question in the region rail has zero showable runs, and no question
    in the refusals group is one `gold.answer_cases` does not declare
    `correctly_refusable`
```

Both will be verified to FAIL on a broken version before they are believed —
the practice `UI_QUESTIONS_START.md` §8 says is the one worth carrying.

---

## P2 — THE NUMBERS THE EXCLUSION RULE PRODUCES

Measured directly off `ui/data.js` before writing this, and predicted to survive
being rewritten in the page's own vocabulary:

```
PREDICTED   33 questions  ->  24 in the region rail
                               7 in the refusals group
                               2 withheld and counted

REGION RAIL   South Asia 4   Scandinavia 4   Sub-Saharan Africa 4
              East Asia 3    Arabia 3        Persia 3   Southeast Asia 3
```

**The predicate is predicted to be insensitive to which of its two honest
spellings is used.** A run is showable if it is not refused, passed the
grounding check, and claims at least one character span. Whether "claims a
span" is read as `abs_start != null` or as `resolution.state === "resolved"`,
**the same nine questions drop** — measured, both ways, before this was
written. That is the reason to trust the rule at all: a filter whose result
moves when you rephrase it is a filter about the phrasing.

**And the sharp fact this block found before building anything: seven of the
nine excluded questions are `correctly_refusable` in `gold.answer_cases`.** The
system refused them because refusing was right. Only two are failures — one
`answerable` question whose every run refused (the Silla glass), and one whose
runs never quote anything (the gold coin of King Ezanas).

**PREDICTED WRONG IF** the built page lists any other count; if the region tally
differs; or if the two spellings of the predicate disagree once written against
the page's own helpers.

---

## P3 — WHAT THE PAGE MEASURES AFTERWARDS

The picker is three stacked lines and a disclosure summary between the question
and the answer; the rail's meta line is a second line on each of 33 buttons.

```
PREDICTED   1600px   first answer line   1184  ->  under 1120
            1600px   page height         4113  ->  under 4050
             390px   page height         5817  ->  at least 400px shorter
             390px   first answer line   1604  ->  within 40px of today
```

The phone answer line is predicted **not** to move much, and that is the point
of stating it: at 390px the rail is ordered *after* the answer already, so
removing 33 meta lines shortens the page without moving the thing a visitor
reads first. A prediction that everything improves is not a prediction.

**PREDICTED WRONG IF** the 1600px answer line does not clear 1120; if the phone
page does not lose 400px; or if the phone answer line moves more than 40px,
which would mean something above the answer changed that I did not intend to
change.

---

## P4 — WHAT I EXPECT TO ABANDON ONCE I SEE IT RENDERED

Four intentions. **I predict I abandon two, and I am naming which.**

```
1  REGION GROUPS AS <details>, collapsed    ABANDONED. Predicted: seven
   except the region of the current                closed discs hide the
   question                                        rail's whole content to
                                                   save scroll a rail does
                                                   not cost

2  A ONE-LINE DERIVED FOOTNOTE counting     KEPT. The Home tab says "the
   the questions withheld as failures            failures are kept ... a
                                                 system that only displays
                                                 its successes is not
                                                 evidence of anything", and
                                                 dropping two failures in
                                                 silence would make that
                                                 sentence false one tab away

3  REMOVING the rail's "runs of this        KEPT. With no picker on screen
   question / every run is kept; none is         "none is hidden" is a claim
   hidden" note                                  the page stops honouring

4  MAKING the two withheld questions        ABANDONED. Predicted: they stay
   unresolvable by URL                           resolvable and merely
                                                 unlisted. Nothing links to
                                                 them; making a live archived
                                                 run unreachable is deleting
                                                 evidence to tidy a rail
```

**PREDICTED WRONG IF** I abandon a different two, keep all four, or abandon one
of the two named KEPT. As in the design block, 1 and 2 are predictions about my
own judgement and I am the one scoring them; that is weaker evidence than P1 or
P2 and is written down as such.

---

## P5 — THE TWO FINDINGS THIS BLOCK CLEARS

**FINDING 100.** Predicted: **one line**, in its own commit, before any design
work. The lookahead `(?![^>]*\bsrc=)` becomes one that also excludes a bare
`<script src>`; the fixed harness is predicted to still report **exactly one
inline script**, and to still go **red** when a genuine second inline script is
added — verified by adding one and watching it fail before the fix is believed.

**FINDING 101.** Predicted: `newline=""` in `build_ui_data.py`, plus a guard
that no tracked file under `data/seed_corpus/` holds a CR byte. **Predicted:
that guard finds zero today.** If it finds any, the hazard has already landed on
the 168 archived citation spans that point into those records by byte offset,
and this stops being a cheap fix.

**§3E, the owed mutation run.** `python scripts/mutate_ui_places.py` on the
host. **Predicted: nothing moves** — neither block since has touched
`check_placement_shape` — and the point is that it is run rather than assumed.

**PREDICTED WRONG IF** FINDING 100 takes more than one line; if the fixed regex
cannot be shown red on a real second script; if any seed-corpus file already
holds a CR; or if the mutation run reports anything but what `UI_RESULT.md` §6
last recorded.

---

## WHAT THIS BLOCK WILL NOT DO

Unchanged from `UI_QUESTIONS_START.md` §7 and restated only as a scoring
boundary: no chatbot, no question box, no curation, no authored coordinate, no
hand-edit of `ui/data.js`, no typed count in prose, no relaxed check, no second
inline script, no merged verify axes, and no ruling or finding number assigned
from this document — `RULINGS.md` is read at the time.

**And one thing this block will not take, deliberately:** `UI_QUESTIONS_START.md`
§3A, the Map tab's panel 7,500 pixels below its map. It is the largest known
defect on the page and it is a different tab, a different layout and a different
set of predictions. Decided rather than inherited by silence.
