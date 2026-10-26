# UI RULINGS — **RULING 83 IS THE ONE `UI_START.md` §4 SAYS THIS BLOCK OWES AND
# MUST NOT BUILD PAST. IT IS DECIDED HERE, BEFORE ANY CODE, AND NOTHING IN THIS
# BLOCK BUILDS IT.**

*Written 2026-09-07 at the open of the UI block, alongside `UI_PREDICTIONS.md`
and before a line of `ui/` was edited. Numbers taken from `RULINGS.md`'s
next-free line as corrected in `UI_PREDICTIONS.md` §0: rulings from 83, findings
from 98.*

---

# RULING 83 — THE CHATBOT REPLAYS. **AND IT TAKES A QUESTION BOX ANYWAY.**

## The question, as §4 put it

> Does the chatbot answer LIVE at request time, or REPLAY the archived runs?

## The ruling

**REPLAY. A visitor may type their own question; the page answers it from the
685 archived runs, or says plainly that no archived run asked it. No answer is
generated at request time, now or by the block that builds this.**

## Why, and it is not cost

**§4 named REPLAY's one real weakness and it is a good objection:** *"Reads as a
demo rather than a system to anyone who types a question of their own."* That
objection is about the **input**, not about the answers. It is satisfied by
giving the visitor somewhere to type — which costs nothing, needs no backend,
and puts no unscored text on the screen.

**The decisive argument against LIVE is the project's own claim.** Every
quotation on this page resolves to a named range of characters in a named field
of a named file, and 1289 of them have been checked against the corpus as it
stands today. **A live answer would be the one artefact on the page that has not
been checked at the moment it is read** — and it would sit in the same type, in
the same layout, beside 1289 that have. A visitor cannot tell those apart, and
the page would have no honest way to tell them.

§4 anticipated exactly this and set the bar: *"If LIVE wins, the ruling has to
say what is shown to a visitor about an answer nobody has evaluated — and
'nothing' is an answer that would not survive being written down."* **I could
not write that sentence.** Every version of it either understates the gap
("this answer has not yet been scored", which reads as a formality beside a
badge saying *1227 resolving to characters on disk*) or overstates it into
uselessness. That failure is the ruling.

**Three more reasons, and the third is the expensive one:**

- **`p7-answer-v2r` is frozen and its successor is already planned.**
  `UI_START.md` §5: click-through citation will want rule 3 changed, and when it
  is, *every archived answer number becomes historical*. A live box would be
  serving answers under a prompt version this project has already decided to
  move off.
- **The floor is denominated per prompt version.** `floor.json` keys its
  verdicts on the prompt version, so a live answer under v3 would be served with
  **no calibrated floor at all** until three sessions on three distinct UTC dates
  and ~270 chat calls have earned one. A live box would therefore ship
  uncalibrated by construction, not by oversight.
- **A key on a public page is a key on a public page.** Hosted backend, key
  handling, rate limiting, and a cost per visitor — a tail this project has
  never carried and would be carrying for the one feature it cannot score.

## What REPLAY-with-a-question-box means, precisely, so the later block cannot
## soften it

```
IN    a text input. The visitor types a question in their own words
IN    matching that question against the archived question set, and showing
      the archived runs for the closest match
IN    SAYING SO WHEN NOTHING MATCHES. "No archived run asked this" is a
      first-class answer of this page and is not styled as an error
IN    every answer shown carries the badges it already carries -- its prompt
      version, its grounding verdict, its span audit, and (after this block)
      its corpus provenance

OUT   generating any text at request time
OUT   any API call from the visitor's browser
OUT   paraphrasing, stitching or summarising across archived runs to
      manufacture an answer to a question nobody asked
```

**That last line is the one that matters.** The failure mode of a question box
over an archive is that it starts *composing*. The moment the page assembles a
new answer out of old ones it has produced an unscored answer by another route,
and every argument above applies to it. **An archived run is shown whole, under
the question it was actually asked, or it is not shown.**

## What would re-open this

**A LIVE box becomes arguable the day a live answer can be scored before it is
displayed** — that is, when the span audit and the floor can run in-loop on a
fresh answer and refuse to display one that fails. That is a real engineering
target and not a rhetorical one. Until then the honest demonstration of the
capability is 685 answers whose every quotation has been checked, not one that
has not.

**This ruling does not depend on anything the UI block builds**, and it was
written before the build so it cannot have been fitted to it.

---

# FINDING 98 — **THE `whitespace_only` SPAN RENDERS CLEAN, READS BROKEN, AND
# EXPLAINS NOTHING. THREE ANSWERS, ALL DIFFERENT, ON ONE CITATION.**

Found by reading `ui/index.html` whole as `UI_START.md` §9 step 3 requires, and
confirmed by rendering it rather than by reading the code twice.

`classify_span` gained `whitespace_only` at FINDING 42 — the archive and the
record disagree about a line break, `cite.py` matches on collapsed text by
design, and the state is *"neither a broken claim nor a labelling defect"*.
**Neither renderer was extended for it.** In `renderAnswerText`:

```
cls    resolved -> ""   case_only/case_folded -> " caseonly"
       moved/absent -> " unresolved"
       whitespace_only -> falls through to ""            OPTIMISTIC DEFAULT
title  ...
       whitespace_only -> falls through to the final else,
                          "this quotation no longer resolves
                           against the corpus"           PESSIMISTIC DEFAULT
```

and `renderQuoteProvenance` has no branch for it, so the panel opens with the
quotation and the chain and **no warnbox of any kind**.

Rendered, `20260828T154621+0000-eff84b08` span 0
(`southasia-01-akananuru-149`, the Akananuru 149 Tamil line):

```
the mark      <mark class="q" data-span="0"
                title="this quotation no longer resolves against the corpus — click for detail">
the panel     warnbox: false
```

**The picture says clean, the tooltip says broken, and the panel says nothing.**
All three cannot be right, and the state they are describing is in fact the
mildest of the six.

**Why it survived:** every guard in `check_ui.mjs` asserts that a span is
*present and highlighted*, and this one is. The audit assertion accumulates
states from the data on both sides, so a state the renderers ignore still
tallies correctly. **Nothing in this repository asserts that a state reaches the
screen as itself** — which is the same shape as the A6 defect `check_ui.mjs`'s
own `data-date-verdict` guard was written to close, one layer over.

**Closed in this block**, and the guard is the point: the fix without a check
that each state renders deliberately would leave the next state added to
`classify_span` in exactly this position.
