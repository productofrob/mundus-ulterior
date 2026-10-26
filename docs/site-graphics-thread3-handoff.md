# Site graphics, thread 3: handoff (2026-10-23)

## What this thread did

Feedback found the Methodology tab text-heavy. Rob chose six sections for graphics, approved drafts on the review canvas "Methodology Graphics Drafts" (claude.ai artifact BYkRNXJeqTwqvv4LFuT3sQ), and ordered all six added. They are built into `ui/index.html`, in the site's own tokens, with every number computed from `data.js`:

| § | Figure | Placement |
|---|---|---|
| 2 | The five tiers: what each holds, and how many records declare it | after the tier list |
| 3 | One record (Periplus §53–56) cut into passages, with positions, the script check, original kept apart from translation, and the place it stores | after the intro paragraph |
| 4 | The withheld-translation test, two panels | after "How that claim is tested" |
| 6 | Every quotation by what the re-check found, the 62 redrawn larger | after the six-outcome list |
| 8 | The retrieval series run by run, with question-set bands | inside the first paragraph, which is now two (break after "…results got worse as the collection grew.") |
| 9 | The span covered, and the two proposed windows dashed | after "A longer span" |

## State

**Update, later on 2026-10-23: committed as `14300d2` and deployed to Production by Rob.** Checked in the browser: the live `index.html` with the 214-byte analytics block removed is `574484ac9af9…` (424,055 bytes) and `data.js` is `bd24c61cf5fd…`, both matching the commit; all six figures render on the live Methodology tab with no console errors. The notes below on committing and deploying are kept as written before that.

- **Uncommitted** in the repo, on top of `d0d358f`: `ui/build_ui_data.py`, `ui/check_ui.mjs`, `ui/data.js`, `ui/data.manifest.json`, `ui/index.html`, `ui/test_build_ui_data.py`. Commit message is in `commit-methodology-figures.txt` (repo root, gitignored like the others).
- To commit:
  ```
  cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
  git add ui/build_ui_data.py ui/check_ui.mjs ui/data.js ui/data.manifest.json ui/index.html ui/test_build_ui_data.py
  git commit -F commit-methodology-figures.txt
  ```
- **Not yet deployed.** The deploy folder is `Claude outputs/mundus-ulterior-site-2026-10-23b` (repo-level `Claude outputs`), byte-identical to the working tree: `index.html` SHA-256 `574484ac9af9…`, `data.js` `bd24c61cf5fd…`. Live is still `d0d358f` until Rob deploys.
- Checks: harness 65 ok (was 64); `test_build_ui_data.py` 23 passed (was 19); `check_chain.mjs` intact.

## What changed underneath

- `build_ui_data.py` → `attach_passages_and_tiers`: every record gets its `passages` (cut by `ingest.loader` from today's records, with positions, declared language, dominant script, script agreement, eligibility) and its declared `tier` (only once `derive_record_tier` agrees). The build refuses on any disagreement. 170 passages; tiers 29/4/4/16/1. Only the corpus section of `data.js` moved; the manifest now reports passages and tiers.
- `index.html`: six functions (`figTiers`, `figPassages`, `figWithheld`, `figCitations`, `figRetrieval`, `figSpan`), a CSS block under `.mfig`, and `SPAN_OUTCOMES` lifted to the top level so the §6 figure and the evidence badges share one table. Example records are named constants: `PASSAGE_EXAMPLE`, `WITHHELD_EXAMPLE`.
- Guard 64 re-derives every figure number; seen red seven ways. Section 2h checks the manifest's new fields.
- The §8 annotations ("Padding added: no change", "As real sources were added, other languages fell") and the caption's "grew twice" are derived and print only when the series bears them out.
- Gotcha recorded in the CSS: never class anything `src` on this page. `.src` is a source card and the click handler opens it.
- Layout (measure_data.mjs): the tab grows from 7612px to 10366px at 1600px and from 17473px to 21662px at 390px.

## Open

- **Site Text doc — done 2026-10-23.** Each figure's labels, notes, screen-reader description where it has one, and caption are in "Mundus Ulterior Site Text" (https://docs.google.com/document/d/17l2REQrEWaMsqKohRmyoq1zIXywGJojjW42IDbbh3Oc/edit), placed where the figure sits, in the doc's conventions ({braces} for computed values, gray italic for layout notes). The §8 entry follows the first §8 paragraph, which was not split or changed in the doc; a note says where the chart sits on the page. The doc changed by those six insertions only (checked against the export taken before). `claude/site-text-doc-baseline.txt` is refreshed to the doc as it now stands, so the next diff shows only Rob's edits.
- **§8 text vs data (flagged, untouched on Rob's order of 2026-10-23):** the prose says Old Tamil "performed worst at every stage"; on the latest run Proto-Norse (0 of 2), Old Cham (0 of 1) and Sabaic (0 of 1) are found less often than Old Tamil (1 of 3), though Old Tamil has the deepest miss (position 373). The evidence drawer's "the same questions as the collection grew" is not strictly true: the set grew 32 → 33 → 44.
- Carried from thread 2, unchanged: the Cloudflare analytics beacon question; old banner PNGs at `/banner/*.png`; the cleanup candidates; the optional §10 sentence split.

## Two design fixes after the figures (2026-10-23)

On Rob's orders, CSS and the section-nav click handler only, in `ui/index.html`:

- **Section buttons:** 14.5px medium ink on the accent wash, 35px tall, solid accent on hover and focus. The nav wraps from 860px and sticks only from 1100px (two rows, 105px; three rows and 149px below about 1060px). A click lands the section just below the stuck nav, measuring its height.
- **Section titles:** `.mth > h2.eyebrow` is 27px bold serif ink; `.mth-head` is 18.5px regular `--ink-soft`. `.eyebrow` on other tabs is unchanged.
- The Site Text doc's layout note on Methodology now says each section opens with its name as a large title, above a smaller heading; the baseline is refreshed to match (that sentence was the only change).
- Commit message: `commit-methodology-nav-headings.txt`. Deploy folder: `Claude outputs/mundus-ulterior-site-2026-10-23c` (`index.html` `45a70753ce83…`, `data.js` unchanged at `bd24c61cf5fd…`). Harness 65 ok.
- **Committed as `e14f17e` and deployed by Rob, 2026-10-23.** Checked in the browser: live `index.html` (analytics block removed) is `45a70753ce83…`, `data.js` `bd24c61cf5fd…`, both matching the commit. Rob approved the result live.

## Starting point for the next thread

Everything from this thread is committed (`14300d2`, `e14f17e`) and live. Nothing is pending from it except the open items above. Rob's next edits to the Site Text doc are found by exporting it and diffing against the refreshed baseline.
