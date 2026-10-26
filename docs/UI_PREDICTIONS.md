# UI PREDICTIONS — **WRITTEN AND COMMITTED BEFORE ANY CODE.** Ruling 78's
# practice. Every figure below was measured from the tree as it stands at the
# open of the UI block; every figure marked PREDICTED was not.

*Written 2026-09-07 at the open of the UI block, after `UI_START.md` §9 steps 1
to 4 and before a single line of `ui/` was edited. The state block reproduced,
`check_ui.mjs` was green on 25 checks, and `build_ui_data.py --verify` read
exactly what `UI_START.md` §7 transcribed. **Nothing in this file may be edited
after the first code commit lands.** A prediction amended once it is known to be
wrong is not a prediction; it is a summary.*

---

# 0. THE OPENING STATE, MEASURED

```
ingest.verify                        green, 54 documents, 170 chunks, 33 parallel pairs
                                     per-language line carries 'mul': 3 and no 'arc'
ingest.test_fidelity                 145   [green]
ingest.test_cost                     78    [green]
eval.test_answer_eval                425   [green]
eval.test_ranking_check              258   [green]
answer.test_answer                   150   [green]
ui/test_build_ui_data.py             19    [green]
scripts/test_recover_baseline.py     56    [green]
scripts/test_harnesses.py            43    [green]
python -m ingest.gazetteer --check   GREEN
node ui/check_ui.mjs                 GREEN, 25 checks, 0 failures
```

`build_ui_data.py --verify`, both axes:

```
FIRST AXIS    1289 claimed spans
              resolved 1227, case_folded 50, article_added 0, case_only 9,
              whitespace_only 1, moved 1, absent 1

SECOND AXIS   unchanged 0, changed 1121, unrecorded 168, not_in_version 0

places        73 pins, 6 extents, 90 gaps across 53 placed documents
              19/49 subject-place edges drawable
              0 unconsidered, 1 declared unplaceable (persia-03-coin)
              63 distinct cache keys drawn as markers
bundle        685 runs, 54 records, five prompt versions
              (p7-answer-v1, v2, v2r, v3, v4)
```

**`RULINGS.md` is one behind and this block does not fix it.** Its line reads
*"The next free ruling number is 83. The next free finding is 97."* W3 used 97
(`W3_RESULT.md` §5, the three `mutate_fidelity` mutations that reported MISS),
recorded in that document and never carried into this file's index or its
next-free line. **`UI_START.md` §10 says 98 and 98 is right.** This block takes
findings from 98 and rulings from 83, and says so here rather than quietly
picking the higher number.

---

# 1. WHAT THIS BLOCK IS, AFTER READING WHAT IT IS REBUILDING

`UI_START.md` §2 says the page is stale and that this is *"a rebuild, not a
build"*. **Having read all 1659 lines of `ui/index.html`, that is half right and
the wrong half is load-bearing.**

**The architecture is not stale.** Counts come from the data — the stat strip,
the region cards, the map extent, the audit badges are all computed. The map
already pans and zooms, re-solves label collisions per zoom level, culls the
coastline by bounding-box overlap rather than by vertex, and refuses to fall
back from a `regional` extent to a pin. `check_ui.mjs` already asserts the
coastline is not inside-out against nine control points. **A rewrite would throw
away the discipline that is the reason any of this is worth showing.**

**Three things are stale, and they are literals and one missing feature:**

```
LITERALS   "All 24 records, by region"            index.html:1394
           "a corpus of 24 primary sources"       the About tab
           "Five records (the GeoNames backlog) have not been geographically
             placed at all"                       -- it is now ZERO
           "two of the seven literary records"    -- seven was true at 24 records
           the LANGS table carries 12 codes; the corpus carries 20. pal, san,
             ocm, omy, non, arb, ko, vi and fr render on screen as raw codes

MISSING    `resolution.provenance` is written onto all 1289 spans by
           `build_ui_data.py` and READ BY NOTHING. D1's second axis is in the
           bundle and nowhere on the page

MISSING    the map lists 90 gaps and 30 undrawable edges in cards below itself,
           a proportion that was a footnote at 24 records and is the majority
           of the geography at 54
```

---

# 2. THE PREDICTIONS

## P1 — WHAT `node ui/check_ui.mjs` WILL READ AFTER THE REBUILD

**PREDICTED: green, with more checks than 25 and no failures.** Specifically:

- **the count rises to between 28 and 32.** New assertions are owed by the new
  surfaces: that every span's provenance state reaches the panel, that no
  `unrecorded` span is ever rendered as `unchanged`, and that the four states
  in `whitespace_only`/`case_only`/`moved`/`absent` each get their own on-screen
  treatment. Fewer than 28 means I added a surface and no guard for it.
- **`rendered all 685 runs (685)` is unchanged**, and so is
  `built a record panel for all 54 seed records`.
- **`every quotation appearing in an answer is highlighted (1289/1289)`
  is unchanged.** If this moves, the rebuild dropped a citation, which is the
  one failure this page exists to rule out.
- **`the headline audit matches the spans` prints the same six states**:
  `{"resolved":1227,"case_folded":50,"case_only":9,"moved":1,"absent":1,"whitespace_only":1}`.

**PREDICTED WRONG IF:** the check count lands at exactly 25. That would mean the
new surfaces shipped with no guard, which is this repository's oldest defect
(`check_ui.mjs`'s own §0 comment) in a new place.

## P2 — WHAT `build_ui_data.py --verify` WILL READ AFTER THE REBUILD

**PREDICTED: byte-identical on both axes.** resolved 1227, case_folded 50,
article_added 0, case_only 9, whitespace_only 1, moved 1, absent 1; unchanged 0,
changed 1121, unrecorded 168, not_in_version 0. Digest still
`0e7845055e440c7c…`.

**This is a prediction about scope, not about arithmetic.** The block edits
`ui/index.html`, `ui/check_ui.mjs` and adds a manifest. It adds no record,
touches no archived run, and does not re-point `floor.json`. **If either axis
moves, the block has done something it said it would not**, and the right
response is to stop and find out what, not to re-transcribe the new figure.

## P3 — WHICH OF THE 54 RECORDS RENDER WITH A BROKEN CITATION

`UI_START.md` §9 step 5: *"`africa-03-periplus-adulis` is the known one — a
prediction that names only it is a prediction worth being wrong about."*

**PREDICTED: EIGHT records render at least one citation that is not clean, and
africa-03 is only the worst of them.** Measured from the bundle, not guessed:

```
africa-03-periplus-adulis      4   absent 1, moved 1, case_only 1, case_folded 1
                                   -- the only record failing the FIRST axis at all,
                                      and G3 box 8 in one line
eastasia-02-hou-hanshu        31   case_only 8, case_folded 23
seasia-03-khao-sam-kaeo       13   case_folded 13
arabia-03-jsnab17              5   case_folded 5
eastasia-01-weilue             3   case_folded 3
arabia-01-periplus             3   case_folded 3
scandinavia-03-vimose          2   case_folded 2
southasia-01-akananuru-149     1   whitespace_only 1
```

**The eighth row is a DEFECT IN THE PAGE AS IT STANDS, found by reading it and
confirmed by rendering it — FINDING 98.** `southasia-01-akananuru-149`'s
`whitespace_only` span renders with `class="q"` and no modifier — visually
identical to a clean citation — while its `title` attribute reads *"this
quotation no longer resolves against the corpus"*, and `renderQuoteProvenance`
emits **no warnbox at all** for it. `classify_span` gained `whitespace_only` at
FINDING 42; neither renderer was extended, so the state falls through every
branch to the pessimistic default in one place and the optimistic default in
the other. **The picture says clean, the tooltip says broken, and the panel says
nothing.** All three cannot be right.

**PREDICTED: after the rebuild that is nine states rendered deliberately and
zero rendered by fall-through.**

## P4 — WHAT THE SECOND AXIS WILL SAY ONCE IT IS ON SCREEN

**This is the prediction I would most like to be wrong about, and it is
measured from the bundle rather than hoped for.** Cross-tabulating the two axes
over all 1289 spans:

```
resolved       / changed       1070
resolved       / unrecorded     157
case_folded    / changed         50
case_only      / unrecorded        9
whitespace_only/ changed           1
moved          / unrecorded        1
absent         / unrecorded        1
```

**EVERY span that fails the first axis has provenance `unrecorded`. All eleven
of them. Not one.** So the honest sentence the page will be able to make, and
cannot make today, is:

> This project cannot say, of a single one of its failing citations, whether the
> failure is a defect in the span or the record moving underneath it. Every one
> of them predates the corpus version.

And its mirror, which is the better half:

> The corpus moved under 1121 spans in one commit at W3, and not one of them
> broke. 1070 still resolve exactly, 50 differ only in case and say so, 1 differs
> only in a line break.

**PREDICTED: both sentences survive the build.** `unrecorded` is rendered as its
own third thing throughout and is **never** collapsed into `unchanged` or
`changed` — `corpus_provenance`'s docstring says why, and a UI that collapsed it
would report a span as a real defect on no evidence.

**PREDICTED: `unchanged` stays 0 and the page has to say so without reading as
broken.** There is no span in this archive whose record is known not to have
moved. That is a fact about W3's timing, not about the citations.

## P5 — WHAT THE MAP WILL AND WILL NOT DO

**PREDICTED: the marker count does not change.** 63 cache keys, 73 pin
placements, 6 extents, 19 drawable edges — before and after. **This block adds
no coordinate.** Debt row 9's Swedish and Thai GeoNames dumps are not in `data/`
(checked: only the two Pleiades snapshots and the licence files are there), so
the three coordinates a source handed over and this corpus refused stay refused,
and `seasia-08-pong-tuk-lamp` and both Scandinavian placements stay gaps.

**PREDICTED: the finding the rebuilt map surfaces is that Rome is not on it.**
Reading all 90 gap reasons: they are overwhelmingly *refusals*, not backlog.
`PLEIADES 423025 'Roma' IS NOT IMPORTED` recurs across records; so does
`A(u)xoume`. Every East Asian record's focus — 大秦, 拂菻, Fu-lin, Da Qin — is a
gap, because the texts mean an empire and the gazetteer offers a city. **The
reason only 19 of 49 edges draw is that the edges run to Rome and Rome has no
pin.** A page about Rome's connections to the wider world currently draws the
wider world and omits Rome, and does not say so anywhere.

**PREDICTED WRONG IF** the gap list turns out to be mostly backlog — records
waiting on a dump — rather than refusal. I have read the reasons and I do not
think it will be, but I have read them as strings and not as curation decisions.

---

# 3. WHAT THIS BLOCK WILL NOT DO, RESTATED SO IT CAN BE CHECKED AGAINST

- Not curate a record. 54 at the open and 54 at the close.
- Not touch `p7-answer-v2r` or `chat-default`.
- Not re-point `floor.json`'s digest pin. Ruling 82.
- Not build the chatbot. §4 is ruled on; a later block builds it.
- Not empty `MODERN_INSTITUTIONAL_PROSE_PENDING_RULING`.
- Not amend G3.
- Not author a coordinate.
- Not hand-edit `ui/data.js`.
