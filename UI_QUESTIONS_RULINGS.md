# UI QUESTIONS RULINGS — **85 AND 86, DECLARED IN THE SESSION THAT MADE THEM.**

*Written 2026-09-08, during the Questions block, before the result document and
in the same sitting as the commit that built them. `RULINGS.md` read at the
time: **next free ruling 85, next free finding 102.** Both are used here, and
`RULINGS.md` is updated in the same sitting — the practice its own correction
note exists to enforce, because a number used in a result document and not
carried back is invisible to the next session that needs one.*

---

# RULING 85 — **A RUN KEEPS ITS ADDRESS AND LOSES ITS CONTROL.**

The run picker is retired. Nothing on the page offers the other runs of a
question, and every one of them is still archived, still counted, still replayed
by the harness, and **still addressable**: `#q/<slug>/r/<stamp>` resolves exactly
as RULING 84 defined it, `applyHash` still sets `state.runIndex` from it, and the
chain figure on Home still travels to the exact run it drew.

**This narrows RULING 84. It does not reverse it.** 84 rules how a run is NAMED —
by its timestamp, never by its index in a growing array — and that a link which
does not resolve says so. All of that stands. What 85 removes is a *control*, not
an *address*, and the distinction is the whole ruling: a URL is a promise this
project made to whoever holds one, and a picker is a piece of furniture it can
take back.

## Why

The picker was built in the design block and was, on its own terms, good: one
line naming the chosen run and why, the spread counted rather than asserted, and
every chip one click away grouped by the axis the variation is actually along. It
replaced forty-one undifferentiated pills and it was a clear improvement on them.

**It was also, all of it, apparatus about the archive rather than evidence about
the answer.** A visitor arrives to find out whether a quotation resolves to
characters on disk. Before reaching a word of the answer they were asked to take
on: that there are forty-one archived attempts at this question, that forty were
grounded and none refused, that one failed a grounding check, that five prompt
versions exist, and that a rule chose this run because it quotes the most. Every
figure true, every figure derived, and none of it about the sentence underneath
it.

The same distinction is what kept three badges and dropped a fourth. *Every claim
carries a citation*, *5 quotations traced to disk* and *6 sources consulted* are
properties of the answer on screen. *`p7-answer-v2`* names the machinery that
produced it, and went with the picker.

## What this does not license

- **It does not license removing a figure because it is unflattering.** The
  refusal note stays, the failed-grounding badge stays, and the two audits on the
  Data & Sources tab are untouched. What went is apparatus, and the test is
  whether a figure describes the answer being read or the archive around it.
- **It does not license breaking a link.** A block that renumbers runs, drops the
  `/r/` segment, or makes an archived run unreachable is reversing 84, not
  applying 85.
- **It does not license leaving the dead wiring behind.** The `.runchip` handler,
  `shortTime`, and the seven classes the picker needed were removed with it. A
  handler for an element that can no longer exist is a handler nobody can test.

---

# RULING 86 — **THE RAIL LISTS WHAT THE CORPUS CAN ANSWER, GROUPS WHAT IT
# CORRECTLY REFUSES, AND COUNTS WHAT IT FAILED.**

A question is listed under its region if it has at least one **showable** run: a
run that was not refused, passed the grounding check, and claims at least one
character span. Twenty-four of thirty-three do.

Of the nine that do not, **seven are cases `gold.answer_cases` declares
`correctly_refusable`** — declared by a person, before the runs were made. Those
seven are grouped under a heading that says so. **The remaining two are
failures**, and they are not listed and **are counted** in one derived line at the
foot of the rail.

## The three parts are a PARTITION, and that is guard 44

Every archived question is in exactly one of the three. The failure this rules
against is not a mislabelled question; it is a question that belongs to none of
the filters and silently stops being anywhere the day the archive grows a case
the partition did not anticipate. A question with no declared case falls into a
group whose heading says it has none, rather than vanishing.

## Why the seven are grouped and not dropped

**A retrieval system that declines is the strongest thing this page has to
show.** One of those seven is the Antikythera mechanism, planted from outside the
empire to be refused; the others ask the corpus for a rate, a DNA result, a list
of emperors and a runic reading that its records do not contain. Deleting them
would leave a page on which the system always answers — which is the failure mode
the whole project exists to argue against, achieved by editing the rail.

## Why the two are counted and not dropped silently

The Home tab says: *"The failures are kept. Refusals, citations that no longer
resolve and places the map will not draw are counted and shown, because a system
that only displays its successes is not evidence of anything."* A rail that drops
two failures in silence makes that sentence false one tab away. **One line, at the
foot of the rail, derived** — it says how many and what kind, and it goes away by
itself if they ever answer.

## What the region is read from

`gold.answer_cases[].region`, where a person declared it. **Not** counted from
which region's records a run happened to retrieve, which would make the rail's
groupings an artefact of the retriever it is meant to be evidence about. Every
region name in that file is one the corpus already uses, so the rail's vocabulary
is the Map tab's and the source cards'.

## And what stays unfiltered

**`QUESTIONS` is every archived question, in archive order, and nothing filters
it.** The rail is a derived view of it. The default question, `questionBySlug`,
the Home chain figure and the harness's run count all read that array, and the
two withheld questions remain resolvable by URL — unlisted, never unreachable.
Making a live archived run unreachable to tidy a rail is deleting evidence.

---

# FINDING 102 — **A QUESTION CLICKED FROM THE FOOT OF THE RAIL PUT THE ANSWER
# OFF THE TOP OF THE SCREEN, AND NO CHECK COULD HAVE SEEN IT.**

Measured, after the region groups were built and while using the page: scrolled
to the bottom of the rail and clicking a question left the answer **1,461 pixels
above the viewport at 1600px, and 2,505 above it on a 390px phone.** The visitor
clicks and nothing appears to happen; what happened is off the top of the screen.

**It has been true since the rail existed** — 33 buttons have always been taller
than one answer — and this block made it easier to reach, because the refusals
group is deliberately at the bottom and is worth clicking.

Fixed in the same commit: the answer column is brought into view **only when it is
not already in view**, so a reader already looking at the right thing does not
have the page taken from under them. **Found by rendering the page and using it,
which is now the sixth defect on this project found that way and the sixth no
guard would have caught.**
