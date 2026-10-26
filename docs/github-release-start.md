# GitHub release: start document (written 2026-10-23)

## What this thread is for

Publish the `mundus-ulterior` repository on GitHub so that others can pick the project up and build on it. The live site is https://mundus-ulterior.pages.dev/; the repo is the other half of what the portfolio case study will link to.

**Done when:** the repository is public; a reader landing on it understands in a minute what the project is, what was built, what was not, and how to run or extend it; no text sits in it, or in its history, that the project's own rights rulings say it may not carry; Rob has pushed it; and the published repo has been checked in the browser.

The case study is a separate thread (`case-study-start.md`) and runs after this one.

## Where things stand (measured 2026-10-23)

- **HEAD** `e14f17e` on `master`, 275 commits since `9470506` (2026-08-12). No remote is configured. The working tree is clean apart from untracked handoff files in the root: `site-feedback-thread1-handoff.md`, `site-text-thread2-handoff.md`, `site-graphics-thread3-handoff.md`, this file, and `case-study-start.md`.
- **Size:** 1,115 tracked files, about 33 MB; `.git` is 45 MB. The largest tracked file is `ui/data.js` at 9.8 MB, well under GitHub's 100 MB limit.
- **The root:** 148 tracked Markdown process documents plus six config files sit beside eight code and data folders. GitHub lists about 160 root entries before it shows the README. No code opens any root `.md` by path (checked with `git grep`); the references are in comments and prose only.
- **README** dates from 9 August and still describes the Part 1 skeleton, with a Windows/PowerShell quickstart and no live link. It points at `../mundus-ulterior-phase1-part1-setup.md`, which is outside the repo, as are the original brief (`Mundus_Ulterior_AI_Tech_Showcase.docx` and `_Rev.docx`, in the parent folder) and the Phase 1 Getting-Started Guide (a Google Doc).
- **No LICENSE file.**
- **Commit authors:** Rob Padilla `<his personal address, removed from this copy under D2>` on 219 commits; `Claude <noreply@anthropic.com>` on 56. Publishing the history publishes that address.
- **Secrets:** `.env` has never been committed and `.env.example` holds placeholders (checked 2026-09-23). Re-check over the full history before pushing.
- **Ignored, on disk, not pushed:** `_to_delete/` (158 MB), `Claude outputs/` (93 MB), 209 `commit-*.txt` files, `.env`, the Pleiades dumps, and `data/CN.zip`.
- **The site already says "the project repository"** four times in Methodology §10, with no link.
- **Cleanup candidates from the site threads:** `ui/build_banner.mjs` and `ui/banner/` are unreferenced since the drawn masthead (`check_ui.mjs:385` says so), but `check_ui.mjs:886` mentions a check that compares against `build_banner.mjs`. Verify before removing anything.
- **Harness:** 65 ok at `e14f17e`.

## Rights come first

Rob's standing lesson is that rights must be dealt with at the start, never discovered late. The rights review (54 of 54 cells read: open 18, all rights reserved 15, states no terms 8, permission 6, two positions 3, public domain 4) asked whether **the portal** may carry each text. A public repository raises three questions that review did not:

1. **The history holds text the portal withdrew.** PHI-sourced Greek text was committed in `03e430f` and `58c6b77` (2026-08-31: Monumentum Adulitanum II and Silko at Talmis) and re-sourced from OGIS in `c2409ea` (2026-09-23) under RULING 98, which says a source restricted to personal study is not the source of any public text. The string `packhum` also appears in the seed corpus from the first commit, `9470506`, so scope the scan from there. Publishing the full history as it stands republishes that text.
2. **A LICENSE file at the root reads as covering everything in the repo.** The corpus is not Rob's to license: 15 cells are all rights reserved, 6 rest on a permission (granted for what use?), and the nine records traced through Wikipedia carry either Wikipedia's own prose, which is CC BY-SA and requires attribution and share-alike, or scholars' readings passed through it (RULING 99).
3. **Archived answers quote the sources.** `eval/` and `ui/data.js` carry quotations, so they inherit the rights of what they quote.

`ui/data.js` already publishes every record's text on the live site, so for most cells the repo adds no new exposure. The work is to confirm that cell by cell, and to find the cells where it does.

## Decisions to put to Rob at the start, each with a recommendation

Put these in one round, before anything changes.

- **R1. History.** (a) Publish the full history as it stands; (b) a fresh single-commit export of today's tree, with the history kept private; (c) the full history rewritten in a **separate clone** with `git filter-repo` to remove the withdrawn text, publishing the old-to-new commit map in `docs/` so every hash cited in the documents still resolves. **Recommend (c).** It keeps the dates that prove predictions were committed before code, which (b) loses and the case study relies on, and it honors RULING 98, which (a) does not. The cost to name: the rewritten clone becomes the working repo from then on (Rob renames the folders; the old one is kept, not deleted), and ignored files the work needs (`.env`, the Pleiades dumps, `data/CN.zip`) are copied across. The working repo is never rewritten in place.
- **R2. Commit email.** If R1 is (c), mapping Rob's personal address to Rob's GitHub noreply address costs nothing extra. **Recommend mapping it.** Under (a) the address stays on 219 commits.
- **R3. Licenses.** **Recommend:** MIT for the code; CC BY 4.0 for Rob's own documentation; and no license over the corpus or anything that quotes it (`data/seed_corpus/`, `eval/`, `ui/data.js`). A `DATA_RIGHTS.md` at the root says so, points at `data/corpus_rights.json` per record, and credits the third-party datasets under their own terms (Pleiades, GeoNames, the Natural Earth coastline, the Cleveland Museum of Art distractors, and whatever else the declarations in `data/` name). Add a `CITATION.cff`.
- **R4. The root.** **Recommend** moving the process documents into `docs/` as pure renames in one standalone commit, with `docs/README.md` as an index by phase and block that says where to start. Leave only README, the license files, `DATA_RIGHTS.md`, `CITATION.cff`, and config at the root. Verify with `git diff --cached -M --stat` that every change is a 100% rename, and run the harness before and after.
- **R5. Documents from outside the repo.** **Recommend** adding the brief and the Part 1 setup walkthrough to `docs/origins/` as Markdown, and the three site-thread handoffs plus these two start documents to `docs/`. They are the only record of the post-launch work and of what was planned. Rob says which of the two brief versions is final.
- **R6. Curator notes in `data.js`.** These are published in full, in internal language and British spelling (DEPLOY_RESULT §5). **Recommend** leaving them as they are, with one README line saying so. They are already public on the live site, and editing them moves `data.js` and the deployed hashes.
- **R7. Banner leftovers.** **Recommend** removing `ui/build_banner.mjs` and `ui/banner/` in their own commit, only if the line-886 check proves not to need them, with the harness run before and after.
- **R8. Link the site to the repo.** **Recommend** turning the four "project repository" mentions in Methodology §10 into links, as one small site commit and deploy after the push. It is the only site change in this thread; anything else that turns up gets listed for Rob, not fixed.

Also settle the repo name (`mundus-ulterior` recommended), Rob's GitHub username, issues on (recommended, since specialist corrections are a named direction), and the default branch (keep `master`; renaming buys nothing here).

## Steps

0. **Predictions.** As every block has, commit a short `GITHUB_RELEASE_PREDICTIONS.md` before any change. For example: how many cells the redistribution pass moves, how many commits and blobs the history scan finds, whether the harness stays at 65 ok after the move, and whether a fresh clone runs without any ignored file.
1. **Redistribution pass, current tree.** For each of the 54 cells, can the repo carry the text? Start with the 32 that are not open or public domain, and with the permission cells: what exactly was granted? Readings are captured, quoted, and proposed; Rob confirms each before anything is written (`read_by: curator_and_model`). Record the result beside the portal's reading without changing the portal's cells, so `data.js` and the live site do not move.
2. **History scan.** List every commit and blob carrying text the current tree withdrew (the PHI-era records at minimum) or that step 1 rules out, across records, `data.js` versions, and archived runs. Rob then confirms R1 against what was found.
3. **Build the public tree** per R1, in a new sibling folder, never in the working repo.
4. **Front door.** A new README covering what the project is, the live link, what was built and what was not (link Methodology rather than restate it), and a map of the folders. It sets out three ways in: (1) open `ui/index.html` locally, no server or keys needed; (2) run the harness with Node, no keys; (3) the full pipeline with Docker, Postgres, and Anthropic and Voyage keys. It also covers where to start reading, directions for building on it (from Methodology §9–§10), licenses, credits, citation, and contact. State which platform the quickstart was tested on (Windows 11, PowerShell) rather than guessing at the others. Then the R3–R7 files and moves.
5. **Checks, on the public clone.** A secrets scan over the full history (`gitleaks` if it installs; otherwise `git log -p` searched for key patterns such as `sk-ant-` and `pa-`). A personal-data scan for the email and for `C:\Users\chemi` paths, with each hit listed and Rob ruling on it. The harness, run by Rob on the host. A fresh-clone test: clone the public tree into a temporary folder, open `ui/index.html`, and run the harness, which proves nothing depends on an ignored file.
6. **Push.** Rob creates the repository on GitHub, public, with no README or license generated by GitHub, then runs:
   ```
   cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\<public clone folder>"
   git remote add origin https://github.com/<username>/mundus-ulterior.git
   git push -u origin master
   ```
   Set the description, website (https://mundus-ulterior.pages.dev/), and topics. Then check the repo in the browser at its full URL: the README renders, every link resolves, GitHub detects the license, the file count matches, and there is no `.env`.
7. **R8,** then close with a result document scored against the predictions, unamended.

## Ways of working

- Rob runs every git command and the harness himself, in PowerShell on the host. Claude writes the code, the files, and exact commands, with the `cd` line at the top of every block.
- Commit messages go in `commit-<step>.txt` in the repo root, for `git commit -F`.
- Every option question carries a recommendation.
- Always give the full URL when asking Rob to check something.
- American spelling and Oxford commas in everything public.
- Deleting in the connected folder needs Rob's permission. Move, never delete, unless he grants it.
- A defect found here is written up here, not handed on to another thread.
- Save the closing handoff to the repo root and to the claude.ai project.

## Out of scope

The case study. Any site change other than R8. Removing `_to_delete/`, which is Rob's to do when he likes.
