# UI QUESTIONS RULINGS — **85 TO 89, EACH DECLARED IN THE SESSION THAT
# MADE IT.** 87 was declared after the block's first close, and says so.

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

## AMENDMENT 1, 2026-09-12 — **THE LINE IS NOT ON THE RAIL, AND IT WAS NEVER A
## LINE. THE DEBT IS DISCHARGED ON THE METHODOLOGY TAB.**

**This ruling was declared and then not kept, for two blocks.** The counted line
existed when the ruling was written; the Questions block rebuilt the rail and
removed it — correctly for that tab — and recorded the obligation in a comment in
`viewQuestions` rather than discharging it. A debt recorded in a comment is a debt
no reader of the page can see, and the Map and regions blocks both deferred it
again. For two blocks this page withheld two failures and said so nowhere.

**WHERE.** On the Methodology tab, in `questionAudit()`, and not back on the rail.
The rail's own rule stands and is the reason: a visitor's first click should not
land on a question this corpus cannot answer. The two failures belong beside the
other things this project counts against itself — the citation audits and the
geography ledger — and not beside the questions they are not in.

**WHAT — AND THIS IS THE PART THE ORIGINAL RULING ALREADY REQUIRED.** The clause
above says the line *"says how many and what kind"*. **A count alone was never
compliant with this ruling**, and reading it as "two failures, counted" is how the
obligation came to look dischargeable by a single number. So the amendment states
plainly what the ruling implied:

```
NAMED        each withheld question appears, in its own words
CLASSIFIED   each says which KIND of failure it is, and the kind is DERIVED
             from the archive rather than declared beside the question
NO FALL-THROUGH   a question that is neither known shape renders as
             `unclassified` and says the page has no description for it — the
             SPAN_STATES discipline, not a nearest-match
REACHABLE    each carries a control that opens it on the Questions tab, because
             "still resolvable by URL" is only true for a reader who knows the
             slug
```

**The two kinds are not two of a thing.** One is a question declared ANSWERABLE
that every archived run refused — a system declining where the project expected
an answer. The other is a question the system answered every time and never
quoted a source for. The second is the worse shape, and a page that prints
*"2 failures"* has told a reader neither of those things. That is the same
collapse this project refuses in `unrecorded` folded into `unchanged`, in a
`regional` claim falling back to a pin, and in a span state borrowing the nearest
branch that has a colour.

**Guard 58 re-derives every part of it** — which question, which kind, and every
figure printed beside it — from the archive rather than from the page's own
classifier, and asserts Home's promise carries the same count from the same
derivation. Verified red three ways: the kind branches swapped, one of the two
failures dropped from the card, and Home's count removed.

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

---

# RULING 87 — **A REFUSAL SAYS WHICH KIND OF REFUSAL IT IS, AND EVERY CLAIM
# THAT SENTENCE MAKES IS RE-DERIVED.**

*Declared 2026-09-08, after the block's first close, when Rob asked why the
seven refusals are refused. `RULINGS.md` read at the time: next free ruling 87.*

Each of the seven questions in the **Not fully answerable** group now carries one
sentence, shown when the question is opened, saying why the refusal is correct.
The group's heading was *"and what it refuses"* and is now *"Not fully
answerable"*.

## Why one sentence per case and not one sentence for the group

*"The evidence here does not answer this"* is true of all seven and useful about
none of them, because they are not the same thing. The corpus's own gold cases
distinguish four species and say so in their reasoning, written before the runs
were made:

```
OUTSIDE THE CORPUS       Antikythera. A Mediterranean find, outside the seven
                         regions. The control: a system never asked something it
                         should decline is never shown declining

IN, AND UNREACHABLE      The Palmyrene tax tariff. The record is one of the 54;
                         its text is a bracketed editorial pointer and it carries
                         no translation, so no part of it can be retrieved. An
                         answer would have been written from a title

THE NOTES ADVERTISE      The Res Gestae Divi Saporis, Oc Eo / Cattigara, the
WHAT THE TEXT DOES       Pattanam DNA evidence. Title and notes name exactly what
NOT HOLD                 is asked; the text does not contain it. THE MOST
                         DANGEROUS SHAPE IN THIS CORPUS -- a model can supply the
                         true answer from its own weights and hang a citation on
                         it, and it will look careful

ADJACENCY                The Gudme bracteates, the Weilue's ruler-selection.
                         Everything near the record says the answer should be
                         there: bracteates usually carry runes, another record
                         here is full of real runic readings, and the Weilue is
                         famous for the passage this corpus does not hold
```

**Naming the species is the argument.** A visitor who reads "no sources" learns
that the corpus is small. A visitor who reads that a record's notes advertise
what its text does not contain learns what this project is actually for.

## The gold paragraphs are NOT what is printed

`gold.answer_cases` carries a paragraph of reasoning for each case. They are
written for the harness — they open by comparing one case to another — so the
page prints one sentence per case, written from them, and the paragraph stays
where it is.

## And the sentences are checked, because a typed sentence goes stale

**A sentence typed about the corpus is the prose form of a typed count**, which
is the defect the UI block spent an hour removing in its numeric form. So each
sentence declares the claim it rests on and `check_ui.mjs` re-derives it (guard
46, 7 reasons and 24 claims):

```
absent        these strings appear in NO field of that record -- or, with no
              record named, in no record in the corpus
pointerOnly   the record carries no reference_translation and its excerpt is a
              bracketed editorial pointer rather than source text
```

**The Palmyrene case is why this is not ceremony, and it asked for this itself.**
Its gold note calls it *"a tripwire on that follow-up as much as a gold case"*:
`manifest.json` lists that record for a transcription pass, and the day someone
does it the record gains reachable text, the sentence becomes false, and the case
becomes wrong rather than stale. Guard 46 is the tripwire. Verified red three
ways before being believed: a refusal whose sentence is missing, a claim that a
word is absent when it is in the record, and the Palmyrene claim pointed at a
record that does carry a translation — which is the state that record enters the
day the pass happens.

## What this does not license

- **It does not license explaining a refusal from the model's answer text.** The
  sentence is about what the CORPUS holds, checked against the corpus. A run's
  own account of why it refused is the run's claim, not the project's.
- **It does not license a sentence with no re-derivable claim.** Guard 46 fails
  a reason that declares none, rather than printing it unchecked.

---

# RULING 88 — **THE SECOND AXIS IS RENDERED WHERE IT CAN BE READ, AND THE GUARD
# MOVES WITH IT AND GETS STRONGER.**

*Declared 2026-09-08, when Rob asked a second time for "record moved?" to come
off the Provenance box, having ruled out both relaxing a guard and losing the
information. `RULINGS.md` read at the time: next free ruling 88, next free
finding 105.*

D1's second axis — has the record moved underneath this citation? — is no longer
on the Questions tab. It is on **Data & Sources**, cell by cell, beside the first
axis it has to be read against.

## Why it is not on the quotation panel

**It is a question about the archive's own bookkeeping, asked of a reader who
came to see whether a quotation matches its source.** For every failing citation
on this page the answer is *not knowable from the archive* — which, read beside a
quotation, lands as a doubt about that quotation. It is not one: it says the
project cannot tell whether a failure is a defect in the span or the record
moving under it, because nothing recorded a corpus version at the time. That is
worth stating once, in a place where the two axes sit together and the sentence
explaining them is on screen. It is not worth stating 1,289 times next to
individual quotations that are fine.

## What makes this different from hiding it

**The guard moved to the new surface and asserts MORE than it did.** The old pair
called `renderQuoteProvenance` for every span and checked that the panel's HTML
contained the right `data-provenance`. It could only say a state APPEARED.

The new pair re-derives the whole cross-tabulation from the archive and asserts
**every cell of it is on screen with its own count**, both states machine-readable
on the row. Folding `unrecorded` into a neighbour now fails on arithmetic rather
than on a missing attribute; a cell that quietly disappears fails too. Verified
red both ways before being believed: stripping the attributes reports every cell
as not on screen, and rendering `unrecorded` as `changed` reports 0 of 168 still
their own third answer.

**`unrecorded` is still its own third answer and is still never rounded into
either neighbour.** What changed is where the page says so, not whether it does.

## What this does not license

- **It does not license moving a guard to a surface that does not carry the
  claim.** The move was only available because the cross-tabulation states the
  same fact per cell. A guard re-pointed at something weaker is a relaxed guard
  wearing a move.
- **It does not license removing the axis from the bundle.** `build_ui_data.py`
  still writes `resolution.provenance` onto all 1,289 spans; a field that reaches
  the bundle and no screen is the A6 defect, and the cross-tab is the screen.

---

# FINDING 105 — **THE CROSS-TABULATION HAS BEEN PRINTING A MANGLED STATE AND A
# BLANK LABEL ON THE DATA & SOURCES TAB, AND THE GUARD FOUND IT THE MOMENT IT
# STARTED COUNTING.**

`spanCrossTab()` returned a map keyed by `state + SEPARATOR + provenance`, and
**the separator was a literal NUL BYTE typed into `ui/index.html`** — which is
why `grep` has been reporting that file as binary. Every test inside the function
used the same byte and was therefore right: 11, 1121 and `allUnrec` were all
correct.

**`viewAbout` split those keys on a SPACE**, as its own comment said it could.
So it got back one mangled string and an `undefined` provenance, and every row of
the cross-tabulation rendered as `resolved<?>changed — 1070 spans —` with **no
provenance label and an empty tag**. The `cross["resolved unchanged"]` lookup
beside it read 0 whatever the archive held; it printed correctly by luck, because
`unchanged` is genuinely 0.

```
BEFORE   resolved<?>changed     1070 spans —            (blank tag)
AFTER    resolved               1070 spans — the record moved after this run  CHANGED
```

**No check caught it for as long as it existed**, because the guard in force
asserted that a `data-provenance` attribute appeared on a *panel*, and it did.
The check that found it is the one RULING 88 moved to this surface, on its first
run: it asked whether the archive's cells were on screen with their counts, and
they were not there at all.

**Fixed in the same commit.** There are no string keys now — `spanCrossTab()`
returns cells, `{state, provenance, n}`, so nothing downstream parses anything,
and `cellN(state, provenance)` answers the one lookup that wanted a key. The five
NUL bytes are gone from the file with them.

---

# RULING 89 — **A RECORD'S NOTE SHOWS THE CURATOR'S WORDS ABOUT THE SOURCE, AND
# NOTHING ABOUT THE PROJECT.**

*Declared 2026-09-09, at the close of the session, when Rob asked for the record
notes to stop carrying project-internal references. `RULINGS.md` read at the
time: next free ruling 89.*

Every one of the 54 records carries a curator's note, and those notes are
working documents. They open with which tranche placed the record, which ruling
bought its slot, which prediction it tests and which tier it counts toward — and
then, usually, they say what the source is and why it matters, which is the best
writing in this project. **The page was printing the whole of one.** A visitor to
a showcase was reading the scaffolding.

The panel now shows a declared excerpt. Measured before it was built: 731
sentences across the 54 notes, of which roughly 29% mention project machinery,
mixed sentence by sentence — 5 notes clean throughout, 5 machinery end to end,
44 mixed.

## The excerpts are SLICED, never retyped

`ui/build_public_notes.py` holds a start and end marker for each fragment, chosen
by a person, and cuts the text out of the record's own note. **A marker that is
missing or that appears twice is a hard error**, because an ambiguous boundary is
how an excerpt silently becomes a different sentence. 67 fragments, 20,430
characters, 53 of 54 records with something public to show.

## And guard 47 re-derives it at run time

Every fragment must still be a substring of the note it came from, whitespace
aside. A note edited underneath an excerpt goes **red** rather than the page
attributing to a curator a sentence they no longer hold.

**A record with NO entry is a failure, not a blank.** The defect this exists to
catch is a record curated later whose entire note reaches the screen because
nobody looked at it. An entry declared empty is fine — that is somebody having
looked, and `eastasia-01-weilue` is the one record declared so.

## Why not a rule over the prose

A filter that drops any sentence mentioning a ruling, a tier or a gold case was
considered and refused. **RULING 74 already refuses a matcher over
`citation_original`, and `gold.answer_cases`' own refusal rule says a rule that
has to be interpreted is a rule that will be broken, and inside a matcher it
would be broken silently.** At a 29% hit rate it would cut real content and keep
real machinery, and both failures would look fine on screen.

## What this does not license

- **It does not license editing the records.** Not one note changed; the corpus
  is untouched and the excerpts are a view of it.
- **It does not license the page writing a summary.** Every character shown is
  the curator's, and guard 47 is what keeps that true rather than a comment
  asking the next person to be careful.

---

# THE CORRECTION THIS SESSION OWES ITS OWN LOG

`bb25cb2` removed `similarity` and `file` from the source panel and said of the
`rank` row that it "prints for nothing today — no passage in this archive carries
one". **That is false.** 4,014 of the 4,110 passages carry a rank, across 669 of
the 685 runs, and it rendered as `#1 of what was retrieved` on nearly every
source panel. The claim was asserted without measuring and the measurement takes
one line.

It was corrected in `bc58c1a`'s message rather than fixed quietly, put to Rob as
his call, and `rank` came off in `c78ebab` for the same reason the cosine did.
