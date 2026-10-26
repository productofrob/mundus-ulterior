# UI DESIGN RULINGS — **decided before the build, so they cannot have been
# fitted to it.**

*Written 2026-09-07 alongside `UI_DESIGN_PREDICTIONS.md` and committed with it,
before a line of `ui/index.html` was edited. `RULINGS.md` was read at the time:
**the next free ruling number is 84 and the next free finding is 100.***

---

# RULING 84 — **THE HASH SCHEME. A URL NAMES THE THING, NOT ITS POSITION, AND AN
# UNRESOLVABLE URL SAYS SO RATHER THAN LANDING SOMEWHERE ELSE.**

`UI_DESIGN_START.md` §6 records that nothing on this page can be linked to — on a
page whose entire claim is *"click any highlighted phrase and see the characters
on disk"*, **you cannot send someone the characters on disk.**
`UI_DESIGN_START_AMENDMENT_1.md` §2 rules that this is built now rather than
during the port, because *"a router invented during the port produces URLs nobody
chose, and they are permanent the moment one is shared."*

**Permanence is the whole reason this is a ruling and not an implementation
detail.** A hash scheme is the one thing in this block that other people's
bookmarks will hold, so it is decided in writing first.

## THE SCHEME

```
#                                    the default view
#places                              a tab
#about
#q/<question-slug>                   a question, at its default run
#q/<slug>/r/<timestamp>              a question at ONE archived run
#q/<slug>/r/<ts>/quote/<i>           ... with a quotation selected
#q/<slug>/r/<ts>/source/<marker>     ... with a retrieved source selected
#record/<doc_id>                     a seed record's panel
#place/<placement-key>               one placement, drawn or gap
#point/<cache_key>                   one gazetteer id, and everything on it
#edge/<index>                        one edge
```

## THE THREE DECISIONS INSIDE IT, EACH WITH ITS REASON

**1. A run is named by its TIMESTAMP, never by its index in the picker.**
`state.runIndex` is an offset into an array that is sorted at load time, and the
archive grows. An index-shaped URL is a promise that the array never changes
length or order, which this project cannot make and should not imply. A
timestamp is what identifies a run in `eval/answer_runs/` and it is what the URL
should carry.

**2. A question is named by a slug of its own text, never by its index.** Same
argument. The slug is derived from the question and is therefore stable exactly
as long as the question text is, which is the correct dependency: if someone
edits a question, the old link should stop resolving rather than silently point
at a different question.

**3. A quotation IS named by its index within its run, and this is the one
positional handle in the scheme.** It is admitted rather than hidden. An archived
run is immutable — that is the point of an archive — so `quote_spans[3]` of a
named run is a stable address in a way that `runs[3]` of a growing archive is
not. There is no other handle: a span carries no id of its own.

## AND THE PART THAT MAKES IT A RULING RATHER THAN A FORMAT

**A hash that does not resolve must SAY SO. It must never fall back to the
default view as though the visitor had typed nothing.**

This is the same failure this project has ruled against three times in other
clothes: `unrecorded` collapsed into `unchanged`, a `regional` claim falling back
to a pin, a state falling through to the nearest branch that happens to have a
colour. **A shared link that quietly lands on a different question is a viewer
that "would look entirely convincing and be wrong"** — `UI_RESULT.md`'s own
sentence about the `absent` span, and it applies here unchanged.

So: an unresolvable hash renders the default view **with a notice naming what was
asked for and what could not be found**, and the notice is dismissible. Not an
alert, not a silent redirect, not a 404 page — this is a single file with no
server and it should behave like one.

## WHAT RULING 84 DOES NOT DECIDE

- **It does not decide the port's router.** It decides what the URLs mean. A
  React router that produces the same addresses satisfies it; one that renumbers
  runs does not.
- **It does not make the hash the source of truth.** `state` remains the source
  of truth and the hash is written from it and read into it. Two sources of truth
  for the selected run is how a back button starts fighting a click handler.
- **It says nothing about the chatbot's URL surface.** Ruling 83's question box
  is step 3 and will want an address of its own; it can have one that does not
  contradict this scheme.
