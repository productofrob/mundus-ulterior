# UI METHODOLOGY DESIGN PREDICTIONS — **THE BLOCK WAS SCOPED AS A LENGTH PROBLEM AND
# THE MEASUREMENT SAYS IT IS NOT GOING TO SOLVE ONE.**
#
# **The rebuilt tab is predicted to come in around fourteen thousand pixels on a
# phone, against seventeen thousand nine hundred and seventy today. That is a fifth
# off, it is not a fix, and P1 says so before the work starts rather than after.**

*Written 2026-09-15, before a line of `ui/index.html` is edited. RULING 78. Scored in
`UI_METHODOLOGY_DESIGN_RESULT.md` and **not amended there — scored.** Every prediction
below names its own refutation clause. One is written not to flatter the block and is
marked. One is left UNSCORED on purpose and §6 says why.*

---

# 1. WHAT THIS IS PREDICTED AGAINST

**The baseline, measured with the committed instrument** — `node ui/measure_data.mjs`,
headless Chromium 1194 in the session container, the same instrument at both ends:

```
                    1600px     390px
page                 10161      17970
card 1 top             403        578
closing card top      9772      17242
guide (empty)          238        238
clickable rows      117 (65 place / 22 record / 30 edge)
```

**And an estimate, which is not a measurement and is labelled as one.** The approved
copy was rendered as plain styled prose — the figure at its drawn height, each evidence
panel as a single collapsed control, no evidence content, no section nav, body type
guessed at 16px/1.55 with a 72-character measure:

```
                    1600px     390px
new copy, estimated   9741      14356
```

**The estimate is generous.** It costs the section nav nothing, assumes ten collapsed
panels at roughly one control-height each, and guesses a type scale the page has not
been built with. Every one of those assumptions moves the real figure up, not down.

---

# 2. THE PREDICTIONS

## P1 — **LENGTH. THE BLOCK DOES NOT SOLVE THE PROBLEM IT WAS SCOPED FOR.**

The rebuilt tab measures **between 13,000 and 16,000 at 390px**, and **between 9,000
and 11,000 at 1600px**.

**REFUTED** if either falls outside its range.

And the claim that matters more than the range: **the phone tab does not drop below
12,000 pixels.** `UI_METHODOLOGY_DESIGN_START.md` §3A called the length "the whole
problem". It is not solved by this block. What improves is that a reader can reach a
named section without scrolling past nine cards to find it — which is navigability,
and the result document must not report it as length.

**REFUTED** by a phone figure below 12,000, which would mean the disclosure did more
than this predicts and the prediction was too pessimistic.

## P2 — **THE GUARDS. THREE GO RED ON THE FIRST RENDER AND 2g DOES NOT.**

Retiring the card prose moves the surfaces guards 53, 58, 59 and 60 read.

```
53  geography ledger figures re-derived     STAYS GREEN, unmodified. The ledger moves
                                            into a collapsed panel and is still on
                                            Methodology, which is all 53 asserts
58  withheld failures named, Home agrees    RED, and expected: the Home clause is
                                            deleted by ruling, the naming half stays
59  partial-archive figures + the label     RED on first render, green once the card's
                                            content is re-homed
60  closing paragraph derives its figures   RED on first render for the same reason
2g  no count written down                   NEVER RED. Every figure in the new copy is
                                            a derived slot and no count is typed
49  panel empty state declares its kinds    STAYS GREEN — the selectable kinds do not
61  every kind round-trips the address bar  change, so neither of these should move
```

**REFUTED** by 2g going red at any point, by 53 needing modification, or by 49 or 61
moving.

**And the count:** the harness ends at **61 or higher**, never lower. Guard 58 loses a
clause and is not deleted. **REFUTED** by a total below 61.

## P3 — **NO COUNT BECOMES TYPED.**

Every figure on the rebuilt tab is computed from the bundle at render time. **REFUTED**
by a single typed count in the shipped page, in digits or in letters — including in the
six rights slots, which are the most tempting because their values are now known.

## P4 — **THE RIGHTS SLOTS RESOLVE, IN ONE COMMIT, TO KNOWN VALUES.**

Extending `ui/build_ui_data.py` to read `data/corpus_rights.json` is one commit, adds
no guard failure, and the six slots resolve to **40 / 54 / 26 / 25 / 14 / 4**.

**REFUTED** by any of the six resolving to something else, by the extension requiring
more than one commit, or by it turning an existing check red. The values were computed
from the sidecar on 2026-09-15 and the prediction is that the page agrees with the file
rather than that the file is right.

## P5 — **THE PORT SWEEP FINDS MORE THAN THE THREE ALREADY NAMED.**

The copy was written describing `ui/index.html`, and the page ships on Lovable. Three
statements are already known false of the port — §5's "the checks run against the
site", §7's "one HTML file, openable from disk", §10's "no framework, no build step".
A sweep finds **at least three more.**

**REFUTED** by a sweep that finds two or fewer.

## P6 — **WRITTEN NOT TO FLATTER THE BLOCK: THE NEW PROSE SHIPS A CLAIM WITH NO GUARD
## BEHIND IT, AND §5 WILL BE THE SECTION THAT SAYS SO.**

The tab's own §5 documents this exact failure — a sentence goes false while the number
beside it stays right — and this block has already committed it once, in the draft, in
its own new writing: §8 said "most sources' reuse terms have not been re-read" and the
rights work made it false without touching a figure. That was caught by rewriting §2
beside it, not by anything systematic.

**So: at least one sentence ships on the rebuilt tab that is true of the data on build
day, has no check behind it, and would not survive the corpus moving.** The candidates,
named in advance so they cannot be claimed afterwards: §2's "the largest group are
records whose underlying edition has not been established"; §8's "Old Tamil performs
worst"; §4's "English-language targets hold and non-English targets fall away".

**REFUTED** if every such sentence in the shipped page either carries a check or is
generated from the data. That would be the best outcome available to this block and it
is not the one predicted.

---

# 3. WHAT THIS BLOCK WILL NOT DO

- **Not type a count into prose**, in digits or in letters.
- **Not relax a check to fit the design**, and not re-point one at a weaker claim.
- **Not delete evidence.** The card prose is retired; the derived figures behind it are
  not, and they move into the collapsed panels.
- **Not author a coordinate.**
- **Not hand-edit `ui/data.js`.**
- **Not build the chatbot or the question box.** RULING 83, and it is its own block.
- **Not assign ruling or finding numbers from this document.**

---

# 4. A DECLARED SCOPE EXCEPTION, SO IT IS NOT A SURPRISE AT THE CLOSE

**This block edits Home.** One sentence — the promise that the failures are kept — is
removed, and guard 58's clause that reads it is deleted with it. Ruled by Rob on
2026-09-15.

The regions block was scored REFUTED for taking a neighbouring tab at Rob's
instruction, and recorded that the instruction did not make the promise kept. This
document therefore does not promise to leave Home alone. It promises **exactly one
sentence and one guard clause**, and anything beyond that is a refutation of this
paragraph.

---

# 5. THE FIGURES THIS DOCUMENT COMMITS TO

```
baseline, measured        10161 / 17970, measure_data.mjs, 2026-09-15
estimate, computed         9741 / 14356, prose render, assumptions in §1
rights slots               40 / 54 / 26 / 25 / 14 / 4, corpus_rights.json
harness at the open        61 checks, green
```

---

# 6. UNSCORED, AND THE BLOCK DOES NOT CLOSE WITHOUT IT

**"Rob will find at least one thing on the rebuilt tab that every figure in the result
document passed."** He found three on this tab in the regions block, two before that,
and the Methodology block left the same prediction unscored for the same reason.
Nothing in the result document can score it.

The candidates, named in advance: that the collapsed evidence is never opened, and the
disclosure has solved the length by hiding the strongest material on the page; that ten
sections in a sticky nav is more navigation than a reader of a single tab wants; and
that the architecture figure, which reads well in isolation, says the same thing as the
first paragraph beneath it and one of the two should go.

**The block does not close until he has used the tab at both widths.**
