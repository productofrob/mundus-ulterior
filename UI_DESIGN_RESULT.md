# UI DESIGN RESULT — **THE CHECK THAT WENT RED WAS NOT ONE OF THE TWO I NAMED,
# AND THE REASON IS FINDING 100.** Ruling 84 is decided and built, the phone
# overflow is gone and its cause was exactly where §6 said, and the front
# section prints no figure it did not derive.

*Written 2026-09-07 at the close of the design block. `UI_DESIGN_PREDICTIONS.md`
and `UI_DESIGN_RULINGS.md` were committed at `64fb3e7` **before a line of `ui/`
was edited** and are not amended here — they are scored. The work is one commit,
`e86582e`, and it touches one file.*

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

`node ui/check_ui.mjs`: **39 checks at the open, 39 at the close, 0 failures.**
This block added no guard, which was P1's own condition on itself.

`git diff --stat` for the whole block: `ui/index.html | 1120 insertions, 281
deletions`. **One file.** `ui/data.js` is not in the diff and
`ui/data.manifest.json` still names `4c32f724d3af8c4b…`.

---

# 1. THE FIVE PREDICTIONS, READ

## P1 — WHICH CHECKS GO RED. **THE SHAPE HELD AND THE NAMES WERE WRONG, AND THAT IS THE FINDING.**

**CONFIRMED:** no check is red at any commit left standing, and **not one of the
fourteen `data-*` checks fired at any point.** That was the substantive half —
§4 says the guards were written against `data-*` attributes precisely so a later
redesign would be cheap, and this block rewrote every view's markup, retired
seven inline `style=` attributes, restructured the run picker and added a whole
front section **without touching a single `data-span-state`, `data-provenance`,
`data-date-verdict`, `data-place`, `data-group`, `data-edge`, `data-record` or
`data-marker`.** The freedom §4 claimed was built is real and this block spent
it.

**REFUTED:** *"exactly two go red at least once, both from the same cause"* —
naming FINDING 99's tag guard and its marker-button partner. **Neither ever
fired.** The tag stayed on one line because the comment above it says to, which
is the comment doing its job.

**What went red instead was `index.html has exactly one inline script (found
2)`, and the cause is worth a number.** See FINDING 100 below. It went red once,
was diagnosed in the same sitting, and the second red line — *"the page's script
threw: Unexpected token '.'"* — was not an independent failure but the same one
one layer down: the harness had cut the page's script in half at a boundary that
does not exist.

**So the count was right (two red lines, once) and the causal claim was wrong,
which is the worse half to be wrong about.**

## P2 — THE PHONE OVERFLOW. **CONFIRMED ON THE CAUSE AND THE NUMBERS. ONE CLAUSE REFUTED.**

```
                     BEFORE            AFTER
390px  Questions     390 = 390         390 = 390
390px  PLACES        454 vs 390        390 = 390
390px  About         390 = 390         390 = 390
820px  all three     no overflow       no overflow
```

**The cause was exactly where §6 said it was.** Two inline
`grid-template-columns` declarations — one around the Places tab's record grid,
one inside the contested-coordinate card — beat the `@media (max-width: 860px)`
rule that was supposed to collapse them. Both are classes now
(`.cols-main-panel`, `.cols-half`), and the overflow went away with them.

**REFUTED: *"the 860px media query is NOT edited to achieve this."*** It had to
be. `.cols.cols-main-panel` is a two-class selector and outranks the media
query's `.cols`, so the new classes had to be named inside it. The prediction
was written as though moving a declaration from an attribute to a class were
specificity-neutral, and it is not. **The fix is still one line of cause and no
new breakpoint**, which was the substantive claim.

**Second prediction, CONFIRMED and by more than predicted:** the first line of
answer prose at 390px.

```
BEFORE   3871px down the page — past the fifth screen
AFTER    1538px on the front section, 590px once you have clicked anything
```

The stat strip is one horizontally-scrolling line instead of five stacked ones,
the tab labels no longer wrap inside their boxes, and the 33-question list is
ordered **after** the answer on a phone rather than before it. Nothing was
dropped to do it; the list is still there and the guards that count it still
pass.

## P3 — WHAT I EXPECTED TO ABANDON. **CONFIRMED, ALL FOUR.**

```
1  A DARK THEME              KEPT. Tokens only: the dark palette redefines
                             ~30 custom properties and NOT ONE RULE in the
                             stylesheet is written twice for it. The map's
                             sea, land, coastline and graticule are tokens
                             now, which is what made that possible
2  MOTION on the panel,      ABANDONED, for the reason predicted. The only
   the picker and the tabs   animation in the file is the loading bar
3  A NARROWER MEASURE for    ABANDONED. The answer column's size and leading
   the answer                are untouched
4  A FRONT SECTION           KEPT, and it is the change worth the most
```

**One thing to record against P3 rather than let it pass as a fifth
abandonment:** the About tab's prose was running the full 1500px of the window,
which is not a column, and it is capped at 104 characters now. That is a measure
being **fixed**, not the answer column being narrowed, and it is a different
change from the one P3 named. Saying so is the point of having written P3 down.

## P4 — THE TWO AXES. **CONFIRMED, BYTE FOR BYTE.**

```
FIRST AXIS   resolved 1227, case_folded 50, article_added 0, case_only 9,
             whitespace_only 1, moved 1, absent 1
SECOND AXIS  unchanged 0, changed 1121, unrecorded 168, not_in_version 0
DIGEST       0e7845055e440c7c...   unmoved
```

Identical to `UI_RESULT.md` §1's P2 and to this block's own opening measurement.
**`ui/data.js` was never regenerated and never appears in the diff**, and every
figure the design wanted was already in the bundle — which was the actual claim
P4 was making.

## P5 — THE §9 GOAL. **CONFIRMED, AND IT FOUND A TYPED FIGURE THAT WAS ALREADY THERE.**

Both sentences are on the first screen, and **not one figure in the front
section is typed.** `grep` for a literal in the new prose returns two digits,
both of them `0` inside `reduce((n, v) => n + (v || 0), 0)`.

The mechanism is the part worth keeping: `contestedCoordinate()` and
`spanCrossTab()` were **lifted out of `viewPlaces` and `viewAbout`** rather than
copied, so the front section and the tab it summarises cannot come apart. A
second derivation of one figure is how a page starts disagreeing with itself,
and this page has been down that road once already.

**And the prediction found something it was not looking for.** The About tab
said *"drawn from seven regions Rome traded with or heard about"*. Seven is
correct today and is the same class of literal as the two the UI block removed —
a number that looks constant and is not. It is derived now. §4's guard would
never have caught it: that guard hunts the two specific sentences that were
actually wrong.

---

# 2. FINDING 100 — **`check_ui.mjs` COUNTS INLINE SCRIPTS INSIDE HTML COMMENTS, AND A COMMENT DESCRIBING THE CHECK IS WHAT TRIPPED IT.**

The loading state is introduced by an HTML comment explaining why it is pure
HTML and CSS. That comment contained the words `<script src>` — describing the
tag it sits above.

`check_ui.mjs`'s first check is:

```js
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)]
```

The negative lookahead excludes `src=`. **`<script src>`, with no `=`, is not
excluded** — so the regex matched inside the comment, counted a second inline
script, and captured everything from the middle of a comment to the first real
`</script>`. The count check went red, and the "runs to completion" check went
red immediately after it because the string it was handed began mid-sentence.

**It fails in the safe direction and that is the only reason this is a finding
and not an incident.** A comment can turn the harness RED; nothing here can turn
it green. But the failure mode is a bad one to leave lying around, because the
red it produces points at the page rather than at the harness, and the next
person to write a comment about a script tag will spend the time I spent.

**Not fixed here, deliberately.** §8 says a design block does not relax a check
to fit a design, and the neighbouring temptation — a design block quietly
editing the guard file it is being judged by — is worse. **It is recorded, with
its cause, for whoever opens the harness next.** The workaround in place is the
one a comment can always take: the comment no longer writes the tag out.

---

# 3. WHAT THE BLOCK BUILT

```
TOKENS      A type scale, a spacing scale, radii, two elevations, the whole
            colour system and the MAP'S OWN reference frame (sea, land,
            coastline, graticule) live in :root and have names. The dark
            theme is ~30 token redefinitions and nothing else -- no rule in
            the stylesheet exists twice. That is the test of whether a token
            layer is real, and it is the reason the amendment asked for one:
            a value in :root ports as a stylesheet, a value in a template
            string ports by hand

INLINE      Seven repeated `style="font-family:system-ui;font-size:11px;
STYLES      text-transform:uppercase;letter-spacing:.11em;..."` attributes on
            <h2> and <h3> are ONE class, `.eyebrow`. The only style=
            attribute left in the markup is `width:${...}%` on the
            similarity bar, which is a computed value and belongs there

PHONE       The overflow, and the layout the overflow was hiding

FRONT       Section 9's two sentences, on the first screen, derived
SECTION

RUN PICKER  One line saying which run and why, the spread counted, and all
            41 chips one click away grouped by prompt version -- the axis
            the variation is actually along

DEEP LINKS  RULING 84, built. Every question, run, quotation, source,
            record, placement, coordinate and edge has an address, and an
            address that does not resolve says what it was looking for and
            leaves the address bar holding what was pasted

LOADING     A page whose claim is that every quotation resolves to characters
STATE       on disk can say WHY its download is large. Pure HTML and CSS
            above the bundle, so the file still has exactly one inline script

THEME       A three-state button (auto / light / dark). Guarded: localStorage
BUTTON      throws in some contexts and the page works with no memory at all
```

**And one thing that is not in the list because it turned out not to exist.**
Halfway through the token pass I wrote a comment asserting that the map legend's
five swatches were rendering black, because they are drawn with
`fill="var(--accent)"` as SVG *presentation attributes* and those, I was
confident, do not resolve custom properties. **Then I rendered the legend and
read the computed styles, and they resolve.** The swatches have always been
right. The comment was corrected before it was committed and no finding was
opened. **That is the third time on this project that looking at the page was
the instrument that worked**, and the first time it worked by stopping something
being written down rather than by catching something already wrong.

---

# 4. WHAT THIS BLOCK DID NOT DO

- **Did not build the chatbot or a question box.** Ruling 83, and it is step 3.
- **Did not curate a record.** 54 in, 54 out.
- **Did not author a coordinate.** Not one.
- **Did not regenerate or hand-edit `ui/data.js`.**
- **Did not split the inline script.** Still one.
- **Did not relax a check**, and did not touch `check_ui.mjs` at all.
- **Did not merge the two verify axes**, and `unrecorded` is still its own third
  answer in both themes.
- **Did not unify the status colours**, which is the thing §5 said a designer
  would want to do and a dark theme would want most: `ground` is still told
  apart by SHAPE, D1's second axis still by LABEL, and the only colour ramp on
  the page is still the first axis, which is the one axis that is an ordering.

---

# 5. FOR WHOEVER OPENS THE PORT BLOCK

The amendment's §3 inheritance list still holds and is not restated. Three
things this block adds to it:

- **The design is in `:root` and in class rules, and that was the whole point.**
  Copy the custom properties and the stylesheet across; the only thing in the
  markup that carries a value is one computed percentage width.
- **RULING 84 is the URL contract, not a suggestion.** A router that renumbers
  runs does not satisfy it. `hashOf()` and `applyHash()` are forty lines and
  they are the specification.
- **The browser-only wiring is gated behind one flag, `HAS_DOM`.** `check_ui.mjs`
  runs the page's script in a VM with a DOM thin enough to prove the top-level
  code completes, and `location`, `history` and `localStorage` are not in it.
  **Gate the wiring, do not widen the harness** — the harness is thin on purpose
  and a wider one asserts less.

**And the thing the port block should not inherit quietly: FINDING 100.** If the
port carries `check_ui.mjs`'s structural check across in any form, it should
carry the fix the design block declined to make.
