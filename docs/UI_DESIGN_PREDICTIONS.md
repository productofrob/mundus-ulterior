# UI DESIGN PREDICTIONS — **written before a line of `ui/index.html` was edited,
# and scored at the close.**

*Written 2026-09-07, after the opening state block reproduced and after the page
was rendered and looked at at 1600px and at 390px, and before any change.
Ruling 78's practice. `UI_DESIGN_START.md` §7 step 5 asks a design block for
three things specifically: which checks go red and why, what the phone overflow
is after the fix, and **which intended changes get abandoned once the page is
seen rendered** — that last one is the prediction worth being wrong about, and it
is P3.*

---

## §0 — THE OPENING MEASUREMENT, so the close has something to be identical to

`python scripts/state_block.py` at `43ac562`:

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

`node ui/check_ui.mjs`: **39 checks, 0 failures.** `ui/data.manifest.json` names
`data.js` at `4c32f724d3af8c4b…`, 9 768 352 bytes.

**The overflow reproduces exactly as `UI_DESIGN_START.md` §6 measured it**, which
is the thing that had to be true before this block was allowed to start:

```
390px  Questions tab   body 390  vs viewport 390     no overflow
390px  PLACES tab      body 454  vs viewport 390     SCROLLS SIDEWAYS
390px  About tab       body 390  vs viewport 390     no overflow
820px  all three       no overflow
```

**Rendered document height at 390px, which §6 did not measure and which is the
other half of the mobile defect:** Questions 5 669px, Places 19 485px, About
4 743px. The first screen of the Questions tab is 844px of stat strip and tab
bar; the first answer begins somewhere past 5 000px.

---

## P1 — WHICH OF THE 39 CHECKS GO RED, AND WHY

**Predicted: none of the 39 goes red at any commit that is left standing, and
exactly two go red at least once during the block, both from the same cause.**

The two are FINDING 99's guard — *"no rendered answer emits a tag with a newline
or a stray `<` inside it"* — and *"every answer whose prose carries a citation
marker renders it as a button"*. They are the pair that fires when a template
string is re-wrapped for readability, and this block rewrites more template
strings than any block since the page was written. §4 says this guard is the one
a redesign is most likely to trip; I am predicting it trips, is caught in the
same sitting, and that the fix is the tag going back onto one line.

**The fourteen `data-*` checks are predicted not to fire at all.** Not one
`data-span-state`, `data-provenance`, `data-date-verdict`, `data-place`,
`data-group`, `data-edge`, `data-record` or `data-marker` attribute is removed,
renamed or moved to a different element by this block. That is the freedom §4
says was built on purpose, and this prediction is the test of whether it was
actually built.

**PREDICTED WRONG IF** a check outside that pair goes red at any point — in
particular if *"every cached point/extent (63) is drawn on the map"* or *"all 54
records are clickable from the Places tab"* fires, which would mean the redesign
dropped a card rather than restyled one. **Also predicted wrong if the count
leaves 39**: this block adds no guard. It is a design block, and a design block
that finds itself writing checks has found a defect and should say so as a
finding rather than quietly growing the number.

---

## P2 — WHAT THE PHONE OVERFLOW IS AFTER THE FIX

**Predicted: `body 390 = viewport 390` on all three tabs at 390px, and the fix is
the removal of two inline `grid-template-columns` declarations, not a new media
query.**

The cause is measured, not guessed: `viewPlaces()` emits
`<div class="cols" style="grid-template-columns:minmax(0,1fr) 400px">` around the
record grid, and the contested-coordinate card emits a second inline
`.cols` override of its own. **An inline style beats
`@media (max-width: 860px) { .cols { grid-template-columns: 1fr } }`**, so the
Questions tab collapses and the Places tab does not. Both overrides become
classes; the media query already there then does its job.

```
PREDICTED   390px  Questions 390   Places 390   About 390
            820px  all three, no overflow
            the 860px media query is NOT edited to achieve this
```

**PREDICTED WRONG IF** the Places tab still overflows after both inline
declarations are gone — which would mean something other than `.rail-right.panel`
is 426px wide and §6 found the wrong cause. **Also predicted wrong if the fix
needs a new breakpoint**: a defect whose repair needs a new rule was not the
defect that was diagnosed.

**Second, separable prediction, and it is the one about design rather than about
a bug:** the Questions tab at 390px is predicted to reach its first line of
answer prose **within the first two screens**, against something past the sixth
today. The stat strip and the 33-question list are what stand in the way, and
both are being moved rather than deleted.

---

## P3 — WHICH INTENDED CHANGES I EXPECT TO ABANDON ONCE I SEE THEM RENDERED

**This is the prediction worth being wrong about, so it is specific and it is
written before the first token was defined. Four intentions; I predict I abandon
two of them, and I am naming which two.**

```
1  A DARK THEME                          KEPT, and it is the largest single
                                         piece of token work in the block
2  MOTION -- transitions on the panel,    ABANDONED. Predicted: the panel is a
   the run picker and tab changes         reference surface people read, and
                                         animating its arrival will read as
                                         slow rather than as considered
3  A DENSER, NARROWER MEASURE for the     ABANDONED. Predicted: the answer
   answer column                          column already sets the one thing on
                                         this page that is prose, and tightening
                                         it will make the quotations harder to
                                         scan, not easier
4  A FRONT SECTION above the tabs         KEPT, and it is the one change that
                                         makes the project more convincing
                                         rather than better-looking
```

**PREDICTED WRONG IF** I abandon a different two, or keep all four, or abandon
one of the two named as KEPT. The failure mode being guarded against is the one
where a design block scores itself on what it shipped and never records what it
tried; naming the abandonments in advance is what makes them countable.

**And the honest caveat:** predictions 2 and 3 are predictions about my own
judgement, and I am the one who scores them. That is weaker evidence than P1 or
P2 and is written down as such rather than presented as the same kind of claim.

---

## P4 — WHAT `build_ui_data.py --verify` READS AT THE CLOSE

**Predicted: byte-identical to `UI_RESULT.md` §1's P2, on both axes, and the
digest unmoved.**

```
FIRST AXIS   resolved 1227, case_folded 50, article_added 0, case_only 9,
             whitespace_only 1, moved 1, absent 1
SECOND AXIS  unchanged 0, changed 1121, unrecorded 168, not_in_version 0
DIGEST       0e7845055e440c7c...
```

**This block does not regenerate `ui/data.js`.** It does not need to: every
figure it wants to print is already in the bundle, and `corpusLanguages()`,
`listOf()` and `placeLedger()` are already there to derive them. So
`ui/data.manifest.json` should still name `4c32f724d3af8c4b…` at the close and
`git diff --stat` should not list `ui/data.js` at all.

**PREDICTED WRONG IF** `ui/data.js` appears in the diff. If the design needs a
field the bundle does not carry, that is a real finding and the honest response
is to say the design wanted something the data does not have — not to regenerate
a 9.5MB file inside a design block and hope the digests land.

---

## P5 — THE §9 GOAL, SCORED RATHER THAN ADMIRED

`UI_DESIGN_START.md` §9 says the page's best material is buried: *one coordinate,
taken 2 times and refused 9* is the third card on the second tab, and *every one
of the eleven failing citations is in the unknowable bucket* is a paragraph
inside the third. **A visitor who spends ninety seconds currently leaves with
"nice map".**

**Predicted: both sentences reach the first screen, and neither figure is typed.**
The Rome card already finds its own id — it is *whichever id the notes argue
about most* and goes away by itself if the corpus stops arguing — and the
eleven-failing line is already derived from the cross-tabulation. **Both are
already derived; the change is where they are, not what they say.** So the
prediction is that the front section adds **no new literal number to the prose**,
and that `grep` for a typed count in the diff comes back empty.

**PREDICTED WRONG IF** any figure in the new front section is written as a
literal — including "seven regions", which is the kind of number that looks
constant and is not. §4's guard only hunts the two sentences that were actually
wrong, so it will not catch a new one; this prediction is what stands in for a
check that does not exist.

---

## WHAT THIS BLOCK IS NOT DOING, restated so the close can be checked against it

- **No chatbot, and no search box.** Ruling 83 specifies it and it is step 3.
- **No record curated, no coordinate authored, no `data.js` hand-edited.**
- **The inline script stays one script.** The loading state is therefore pure
  HTML and CSS above the `data.js` tag, with no script of its own.
- **`ground` stays told apart by shape and D1's second axis by label.** The
  designer's instinct to unify the status colours is the exact thing §5 says to
  resist, and a dark theme is where that instinct will be loudest, because a dark
  theme wants every accent re-derived from one ramp.
- **No check relaxed to fit a design.**
