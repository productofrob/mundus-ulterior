# Site text, thread 2: handoff (2026-10-20, updated 2026-10-23)

## Live

https://mundus-ulterior.pages.dev/ serves commit `d0d358f` byte for byte, apart from the 214-byte Cloudflare Pages Analytics block the host injects. Checked in the browser on 2026-10-23 after Rob deployed `Claude outputs/mundus-ulterior-site-2026-10-23` to Production: `index.html` with that block removed is SHA-256 `bc094a785e6c…`, and `data.js` is unchanged at `4acef54c7b58…`. The browser tab title reads "Mundus Ulterior — Rome and wider world: 27 BC – 1204 AD".

## State

- Committed: `d0d358f` "The masthead standards show on phones, and the Han banner clears the theme button", on top of `bd2e0de` "Site text, round 1: Rob's edits from the Site Text doc". The repo is clean apart from two untracked handoff files in its root, `site-feedback-thread1-handoff.md` and this one, `site-text-thread2-handoff.md`. Harness: 64 ok.
- Handoff documents are saved in the repo root (`C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior`) as well as in the claude.ai project, per Rob's standing instruction of 2026-10-23.

## Added 2026-10-23: the masthead standards at every width (`d0d358f`)

- The eagle and the Han banner had been hidden below 860px. They now have three placements, one shown at a time, chosen in CSS by class:
  - **1100px and up:** the approved E1 placement, unchanged (`.hz-em-desk`, `.hz-em-full`).
  - **760–1099px:** the Han banner moves left to x 2200, beside the sun (`.hz-em-tab`). At its full position the theme button covered its flag from about 880px to 1000px, a defect live since `ed3a7c3`.
  - **Under 760px:** a smaller pair on the nearer ridges (`.hz-em-phone`): the eagle on the third ridge at scale 0.6, the banner on the fourth at scale 0.55. Both take the near emblem color, so the eagle stays visible in the dark theme.
- **Under 360px** the title had been breaking onto two lines because the theme button shares its row. It steps down to `--t-xl` there and stays on one line.
- Verified by a width sweep from 320px to 1920px: every visible standard clears the title and subtitle lines by at least 9.7px and the theme button by at least 13.5px, and none is cut off. If the masthead text, the theme button, or the strip height changes, re-run that sweep. The script measures each shape's own box, not the group's, and lives in the session scratchpad (`tools/sweep.py`), so it would need recreating.

## What thread 2 did (2026-10-20)

- Built the Google Doc "Mundus Ulterior Site Text" (https://docs.google.com/document/d/17l2REQrEWaMsqKohRmyoq1zIXywGJojjW42IDbbh3Oc/edit) in the Mundus Drive folder: every piece of site text, one section per tab, captured by rendering the page. `{braces}` mark values computed from the data, gray italic notes are layout notes, and data-derived text (answers, excerpts, long data lists) is marked or condensed.
- Rob edited the doc. Changes were confined to the browser title, loading message, Home (all four cards), the Home map caption, and the Map legend. Questions and Methodology were untouched.
- Applied in `bd2e0de`, plus copy-edits on top of the doc: "travelled" → "traveled", "will cannot draw" → "cannot draw", "instead just" → "instead of just", an Oxford comma in the loading message, and straight quotes on Home. These remain in Rob's wording in the doc.
- Rob's decisions: the coastline legend line becomes its own sentence ("…retrieved 2026-08-13. It is a modern reference frame, not evidence, and does not show the ancient shoreline"), and the first legend item takes a colon like the rest.
- New `numWord()` beside `listOf()`: Home's "explores seven regions" is derived from the region list.
- Guard 58 now matches "as are the N questions" (seen to fail on the old phrasing first).

## For the next round of doc edits

- `claude/site-text-doc-baseline.txt` holds the doc's plain-text export as Rob left it after round 1. Export the doc again (Drive `download_file_content`, `text/plain`) and diff against it to find new edits.
- Harness phrases to watch: "The failures are kept"; "as are the N questions"; the "Sources are in …, and English." sentence; on the Map panel, "what is marked on the map", "Nothing on the map marks this edge", "the square where this map keeps the record", "declared, not derived", "No room at its anchor".

## Still open from thread 1

- Cloudflare Web Analytics beacon: Rob hasn't confirmed it was intended.
- Old banner PNGs still answer at `/banner/*.png`.
- Cleanup candidates left in place: `ui/build_banner.mjs`, `ui/banner/`, the header comment in `ui/measure_data.mjs`, the deploy folders under `Claude outputs/`, and the `commit-*.txt` message files from this round.
- Optional: split the §10 sentence "no content delivery network, and no server, and the page itself is not compiled".
- The older "Mundus Ulterior Portal Text" doc is superseded by the Site Text doc for site copy. It still holds Rob's "KEEP FOR PORTFOLIO SITE WRITEUP" notes.

## Deploy routine (unchanged)

Copy `ui/index.html` and `ui/data.js` into a fresh folder under `Claude outputs/`. In Cloudflare open Workers & Pages → mundus-ulterior → Create deployment → **Production**, and drag in the folder. Then check the live `index.html` digest (analytics block removed) against the commit.
