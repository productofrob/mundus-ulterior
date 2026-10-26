# UI RESULT — **P5 IS REFUTED AND FINDING 99 IS THE REASON THE BLOCK WAS WORTH
# RUNNING.** Ruling 83 is decided, click-through citation gained the axis it was
# missing rather than the feature it already had, and **every citation marker on
# this page had been broken HTML for the whole life of the page.**

*Written 2026-09-07 at the close of the UI block. `UI_PREDICTIONS.md` and
`UI_RULINGS.md` were committed at `7c6d5f6` **before a line of `ui/` was
edited** and are not amended here — they are scored.*

---

## THE STATE BLOCKS ARE GENERATED. NOTHING BELOW THEM IS RESTATED.

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

`node ui/check_ui.mjs`: **25 checks at the open, 39 at the close, 0 failures.**

---

# 1. THE FIVE PREDICTIONS, READ

## P1 — WHAT `check_ui.mjs` WOULD READ. **PARTLY REFUTED. The mechanism held and the number was wrong on the high side.**

Predicted *"between 28 and 32"*. **It is 39.** Every other clause held exactly:
685 runs rendered, a record panel for all 54, `1289/1289` highlighted, and the
same six states in the headline audit.

**The range was written before three of the five guard sets existed.** I sized
it against the surfaces I had planned, then FINDING 98 turned out to need four
checks rather than one, the manifest needed three, and FINDING 99 did not exist
at all when the prediction was written. **The prediction's own failure clause —
*"predicted wrong if the count lands at exactly 25"* — was the one that
mattered, and it did not fire.**

## P2 — WHAT `build_ui_data.py --verify` WOULD READ. **CONFIRMED, byte for byte.**

```
FIRST AXIS   resolved 1227, case_folded 50, article_added 0, case_only 9,
             whitespace_only 1, moved 1, absent 1
SECOND AXIS  unchanged 0, changed 1121, unrecorded 168, not_in_version 0
DIGEST       0e7845055e440c7c...   unmoved
```

Identical to the opening measurement in `UI_PREDICTIONS.md` §0. **The block
edited `ui/index.html`, `ui/check_ui.mjs` and `ui/build_ui_data.py`, regenerated
`ui/data.js` twice, and moved neither axis** — which is what P2 was a prediction
about.

## P3 — WHICH RECORDS RENDER A CITATION THAT IS NOT CLEAN. **CONFIRMED on the eight. One clause refuted.**

The eight named records are the eight, with the counts predicted.
`africa-03-periplus-adulis` is the only record failing the first axis, and
`southasia-01-akananuru-149`'s `whitespace_only` span was the eighth row — the
defect the prediction went looking for.

**REFUTED:** *"after the rebuild that is nine states rendered deliberately."*
**`SPAN_STATES` covers eight** — `resolved`, `case_folded`, `case_only`,
`article_added`, `whitespace_only`, `moved`, `absent`, `unclaimed`. I counted
nine before writing the table and never re-counted. **The substantive half held:
zero states render by fall-through**, and `check_ui.mjs` now fails if a state in
the archive has no entry in the table.

## P4 — WHAT THE SECOND AXIS WOULD SAY. **CONFIRMED, and it is the prediction I would most have liked to be wrong about.**

```
resolved       / changed       1070        case_only      / unrecorded     9
resolved       / unrecorded     157        moved          / unrecorded     1
case_folded    / changed         50        absent         / unrecorded     1
whitespace_only/ changed          1
```

**All eleven citations that fail the first axis have provenance
`unrecorded`.** Both sentences P4 predicted are now on the About tab, and both
are derived rather than typed, so they change by themselves when the archive
does. `unchanged` is 0 and the page says why without reading as broken.

## P5 — WHAT THE MAP WOULD DO. **THE SCOPE HALF CONFIRMED. THE HEADLINE REFUTED, AND THE REFUTATION IS WORTH MORE THAN THE CONFIRMATION WOULD HAVE BEEN.**

Confirmed: no coordinate added, no marker moved. 63 groups, 19 of 49 edges,
before and after. Debt row 9's dumps are not in `data/` and the three refused
coordinates stay refused. All 90 gaps are `regional` — **asked of the data, not
asserted, so the sentence changes itself if that stops being true** — and 85 of
90 took no gazetteer id at all, which is the refusal-not-backlog half of the
`PREDICTED WRONG IF` clause holding.

**Refuted: *"the finding the rebuilt map surfaces is that Rome is not on
it."*** Rome is on it. `pleiades:423025` is drawn as a marker with two members.

**And the truth is sharper than the prediction:**

```
pleiades:423025 "Roma"

TAKEN 2x     arabia-06-syllaeus            Rome (rm) -- a Safaitic memorial
             southasia-07-bm-claudius-aureus  Rome, THE MINT, as the BM states it

REFUSED 9x   arabia-07-cih541              Rmn, the king of Rome
             eastasia-09-jiutangshu-fulin  Fu-lin (Ta-ts'in)
             eastasia-01-weilue            Da Qin
             persia-05-abnun               the Romans (Hromay)
             persia-06-shahrestaniha       kesar, the Caesar
             scandinavia-07-rycksta        Grikkium, among the Greeks
             scandinavia-06-tjurko         walhakurne, 'the foreign grain'
             southasia-06-cosmas-taprobane The Roman world
             seasia-09-oc-eo-unesco        Mediterranean countries
```

**The dot on the map is a mint and a journey. The empire is named nine more
times and refused a coordinate every time** — because a people is not a place,
an office is not a city, and an empire is not the town on the Tiber. That is a
better sentence than the one predicted, and **the corpus was already saying it;
the map just had no way to.** It does now, in a card that is derived rather than
hardcoded: it finds whichever id the notes argue about most, and goes away by
itself if the corpus stops arguing.

**Why the prediction was wrong is the useful part.** I read all 90 `gap_reason`
strings and never rendered the map. Reading the refusals told me Rome was
refused; only looking told me it was also taken.

---

# 2. FINDING 99, AND IT IS NOT IN ANY PREDICTION

**Every citation marker on this page — all 1945 of them, on 683 of 685 runs —
was emitted as broken HTML for the whole life of the page.**

`renderAnswerText` ends by turning every newline in the assembled markup into a
`<br>`. The marker button was written across two lines for readability, so the
newline **inside its opening tag** became a `<br>`:

```
<button class="marker" data-marker="S1"<br>                title="source S1 — click to inspect">[S1]</button>
```

The browser parses `<button class="marker" data-marker="S1"<br` as the element
and renders the rest — `title="source S1 — click to inspect">` — **as visible
text beside the answer.** The marker was also not clickable. On a page whose
entire claim is click-through provenance, the most obvious click target on the
screen had never worked.

**Not one check in `check_ui.mjs` caught it, and the one that looks closest is
the reason why.** *"citation markers all resolve to a source card"* compares
markers in the answer **prose** against the grounding report's
`unknown_markers`. Both sides were correct. Nothing rendered the markup and
looked at it.

**This is the second time that looking at the page was the only instrument that
worked** — check 2c exists because the first coastline snapshot drew the Indian
Ocean as a continent while every check passed. The cure is the same: assert the
property. `check_ui.mjs` now fails if any tag the page emits contains a newline
or a stray `<`, and if an answer whose prose carries a marker renders none as a
button. **Run against the pre-fix page the guard reports 683 of 685 runs
malformed**, so it fails on the code it was written against rather than being
decoration.

---

# 3. WHAT THE BLOCK BUILT

```
IN, AND IT IS THE FEATURE CLICK-THROUGH CITATION WAS ACTUALLY MISSING
    D1's SECOND AXIS. `build_ui_data.py` has written `resolution.provenance`
    onto all 1289 spans since D1 and this page read NONE of it. It is now on
    every citation panel and in aggregate on the About tab, and it stays a
    separate axis: `unrecorded` is its own third answer, and check_ui.mjs
    fails if a span whose data says `unrecorded` is ever rendered as
    `unchanged` or `changed`. Deliberately NOT coloured -- the axis has no
    ordering, so it is told apart by LABEL exactly as `ground` is told apart
    by SHAPE on the Places tab

FINDING 98, CLOSED, with a guard that would have caught it
FINDING 99, CLOSED, with a guard that fails on the pre-fix page

STALE LITERALS  four sentences, and a guard that hunts for those four
LANGS           12 codes against a corpus of 20. pal, san, ocm, omy, non, arb,
                ko, vi, fr rendered as raw ISO codes; each added name confirmed
                against the record that carries it, never read off the code.
                `mul` added, FINDING 95

THE MAP         no coordinate added and no marker moved. The 90 undrawable
                placements stop being a footer card: a counted ledger, the
                taken-2-refused-9 card, the ten `focus` gaps quoting each
                record's OWN note rather than naming the places, and
                twenty-one one-record cards collapsed into one list with
                nothing dropped

DEBT ROW 7      ui/data.manifest.json, FINDING 74. Written beside data.js by
                the same command; both axes kept separate; per-section
                digests. A DESCRIPTION and never a second source of truth --
                check_ui.mjs re-derives every figure in it from data.js and
                fails on disagreement, which is what stops a manifest from
                becoming a file that says whatever it last said

RULING 83       decided in UI_RULINGS.md BEFORE the build, so it cannot have
                been fitted to it. The chatbot REPLAYS and takes a question
                box anyway. NOTHING OF IT IS BUILT

NOT DONE, and stated so nobody expects it
    the question box. Ruling 83 specifies it; a later block builds it
    debt row 9. No Swedish or Thai GeoNames dump is in `data/` -- only the two
      Pleiades snapshots and the licence files -- so three coordinates a
      source handed over stay refused and both Scandinavian placements and
      seasia-08-pong-tuk-lamp stay gaps
    debt row 10's OTHER half. `git log --follow` on the Adulis record was read
      (three commits: 9470506, bb3bef5, f8eaa19) and the broken citation's
      state is designed around it. The two chunk ids are NOT reconciled --
      the ABSENT span claims `::translation::000` while the passage supplied
      under its marker is `::original::000`. That is a defect in a recovered
      2026-08-10 archive, and repairing an archive is not this block's business
    the 16 documents that are PARTLY gaps reach their gaps only through the
      record panel, not the Places tab's lists. True before this block too;
      check_ui.mjs asserts the record-panel path and that assertion still holds
```

---

# 4. WHAT THIS BLOCK DID NOT DO

- **Did not curate a record.** 54 at the open, 54 at the close.
- **Did not author a coordinate.** Not one.
- **Did not touch `p7-answer-v2r` or `chat-default`.**
- **Did not re-point `floor.json`'s digest pin.** Ruling 82.
- **Did not build the chatbot.** Ruling 83 decides its shape; a later block
  builds it.
- **Did not empty `MODERN_INSTITUTIONAL_PROSE_PENDING_RULING`.**
- **Did not amend G3.** Still closed, still failed on nine boxes.
- **Did not hand-edit `ui/data.js`.**
- **Did not fill in `RULINGS.md`'s missing 53 to 79.** The gap and the trap stay
  where W3 left them.

---

# 5. THE FINDINGS, AND ONE CORRECTION TO A DOCUMENT

```
FINDING 98  UI_RULINGS.md  the whitespace_only span renders clean, reads
                           broken via its title, and its panel explains
                           nothing. Three answers on one citation
FINDING 99  here           every citation marker on the page emitted as broken
                           HTML. 1945 markers, 683 of 685 runs, the life of the
                           page. Caught by looking
RULING 83   UI_RULINGS.md  the chatbot REPLAYS, and takes a question box anyway
```

**`RULINGS.md`'s next-free line was one behind and is corrected in place**, with
the original sentence quoted rather than deleted. It read *"the next free
finding is 97"* while W3 had already used 97 and recorded it only in
`W3_RESULT.md` §5. **A number used in a RESULT document and not carried back is
invisible to the next session that needs one** — which is the same class of
defect as the manifest this block just built. It now reads 84 and 100.

**One correction to `UI_START.md`, recorded rather than fixed.** §9 step 2 says
*"Read `W3_RESULT.md` §7 — the two verify axes"*. `W3_RESULT.md` has six
sections. The two-axes material is `UI_START.md`'s **own** §7, and `W3_RESULT`
§1's P3. Nothing was lost — this session read both — but the next reader hunting
for a §7 that does not exist will lose ten minutes.

**And one thing `UI_START.md` §2 got half wrong, which mattered more than the
citation.** It says the page is stale and *"this block is a rebuild, not a
build"*. **The architecture was not stale**: every count on the page was already
derived, the map already re-solved label collisions per zoom level and culled
the coastline by bounding box rather than by vertex, and `check_ui.mjs` already
asserted the coastline was not inside-out against nine control points. What was
stale was four literals, a language table, and a field nothing read. **A rebuild
taken at its word would have thrown away the discipline that is the reason any
of this is worth showing** — and §9 step 3, *"read `ui/index.html` whole"*, is
the instruction that stopped it. It is also what found both findings.

---

# 6. WHAT IS OWED, AND IT IS ONE COMMAND ON THE HOST

**`ui/build_ui_data.py` gained a function** (`build_manifest`), and
`scripts/mutate_ui_places.py` mutation-verifies that file's placement guards.
Nothing this block added is inside `check_placement_shape`, so no mutation is
expected to move — **which is exactly why it should be run rather than
assumed.**

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
python scripts\mutate_ui_places.py
git diff --stat
```

```
EXPECTED   mutate_ui_places   unmoved from its last recorded figure
           git diff --stat    no file whose every line changed
```

**Nothing else is owed.** This block needed no Postgres, took no ranking run,
and re-embedded nothing. `git diff --stat` was read after every commit from the
bridge and no file's every line changed; `.gitattributes` is `* -text` and the
168 archived spans that point into the corpus by exact offset all still resolve,
which `--verify` confirms above.

---

# 7. FOR WHOEVER OPENS THE CHATBOT BLOCK

Read `UI_RULINGS.md` first — ruling 83 is what you are building and its
`OUT` list is the part that matters. **The failure mode of a question box over
an archive is that it starts composing**, and the moment the page assembles a
new answer out of old ones it has produced an unscored answer by another route.

Two things this block leaves you that you would otherwise have to find:

- **`ui/data.manifest.json` is how you review your own change to `data.js`.**
  `git diff --stat` will tell you the 9.5MB bundle is `2 +-`. The manifest is
  the diff that can be read, and `check_ui.mjs` will fail if it drifts.
- **`data.js` carries `runs[].question` for 33 distinct questions**, and the
  manifest lists them sorted. That is the matchable set a question box answers
  from, and it is already in the bundle — no new build step is needed to have
  the visitor type something.
