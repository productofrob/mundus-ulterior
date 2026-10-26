# The working documents

Mundus Ulterior was built in blocks. Each block ran as its own working session,
and each one left its documents behind. This folder holds all of them,
unchanged except for moving here from the repository root on 2026-10-26. They
are the project's notebook: what was decided, what was predicted, and what
happened, written at the time.

## Where to start

1. **The live site's Methodology tab,** https://mundus-ulterior.pages.dev/ ,
   gives the public account of what was built and what was found.
2. **[`origins/`](origins/)** shows what was planned.
3. **[`BLOCK_G_RESULT.md`](BLOCK_G_RESULT.md)** is the turning point: Phase 2's
   exit verdict, and why the corpus stopped at 54 records.
4. **[`DEPLOY_RESULT.md`](DEPLOY_RESULT.md)** gives the state at launch.
5. **[`RULINGS.md`](RULINGS.md)** says where each numbered ruling is declared.

## How a block's documents fit together

```
*_START          written when the previous block closed, so that the next
                 session can pick up the work: what is done, what is next,
                 and what to decide first
*_PREDICTIONS    written and committed BEFORE any code or data changed, then
                 scored at the close without amendment (RULING 78)
*_RULINGS        decisions taken during the block. RULING n and FINDING n are
                 numbered across the whole project
*_RUNBOOK        the exact commands Rob ran on his own machine, in order
*_RESULT         what the block did, scored against its predictions
```

## Reading notes

- **The commit hashes cited are the pre-release ones.** The history was
  rewritten once before publication. [`COMMIT_MAP.md`](COMMIT_MAP.md) gives each
  old hash's new one.
- **"The host" and "the bridge."** Every git command, test, and pipeline run was
  executed by Rob on his Windows machine, "the host". Claude, the AI assistant
  the project was built with, read and wrote files over a link to it, "the
  bridge", and handed over the commands.
- **Spelling.** The earlier documents use British spelling, and the site and the
  later documents American. Each is kept as written.

## Origins: what was planned

July and August 2026, before the repository's first commit. Kept as written.

- [`origins/AI_TECH_SHOWCASE_BRIEF.md`](origins/AI_TECH_SHOWCASE_BRIEF.md): The brief, in its revision of 2026-07-18: six pillars, a reference stack, and a four-phase build order. Converted from the Word original.
- [`origins/PHASE1_GETTING_STARTED_GUIDE.md`](origins/PHASE1_GETTING_STARTED_GUIDE.md): The Phase 1 plan: a thin slice of three to five sources in every one of the seven regions. Exported from the Google Doc.
- [`origins/PHASE1_PART1_SETUP.md`](origins/PHASE1_PART1_SETUP.md): The environment as first built on Windows, with the fixes it needed (2026-08-09).

## The running documents

Used across every phase.

- [`PROGRESS.md`](PROGRESS.md): Begun as the Phase 1 progress tracker, and kept as the project's running log, with the standing lessons.
- [`STARTUP.md`](STARTUP.md): What to start, in what order, at the beginning of every working session.
- [`RULINGS.md`](RULINGS.md): The register of rulings: which document declares each one. It says plainly where it is incomplete.

## Phase 2 plan

2026-08-12.

- [`PHASE2.md`](PHASE2.md): The Phase 2 plan.
- [`PHASE2_PLAN.md`](PHASE2_PLAN.md): Its execution runbook.

## Block B3: distractors

2026-08-14 to 2026-08-16. Off-topic museum records added to the index, so that retrieval has something to get wrong.

- [`BLOCK_B3_DISTRACTORS.md`](BLOCK_B3_DISTRACTORS.md)

## Block C: query translation and the first measured runs

2026-08-16 to 2026-08-20.

- [`BLOCK_C_START.md`](BLOCK_C_START.md)
- [`BLOCK_C_RULINGS.md`](BLOCK_C_RULINGS.md)
- [`C2_START.md`](C2_START.md)
- [`C2_RULINGS.md`](C2_RULINGS.md)
- [`C2_RENDERING_REVIEW.md`](C2_RENDERING_REVIEW.md)
- [`C2_RESULT.md`](C2_RESULT.md)
- [`C3_START.md`](C3_START.md)
- [`C5_START.md`](C5_START.md)
- [`C5_3B_AND_PROTOCOL.md`](C5_3B_AND_PROTOCOL.md)
- [`C5_RESULT.md`](C5_RESULT.md)
- [`C6_RUNBOOK.md`](C6_RUNBOOK.md)
- [`C6_RESULT.md`](C6_RESULT.md)
- [`C7_START.md`](C7_START.md)
- [`C7_RESULT.md`](C7_RESULT.md)

## Block D: the corpus version in every answer, the gold set, and a harness that can tell a session from a repetition

2026-08-20 to 2026-08-25.

- [`BLOCK_D_START.md`](BLOCK_D_START.md)
- [`D_TASK0_RUNBOOK.md`](D_TASK0_RUNBOOK.md)
- [`D_TASK0_RESULT.md`](D_TASK0_RESULT.md)
- [`BLOCK_D_TASK2_START.md`](BLOCK_D_TASK2_START.md)
- [`D1_DESIGN.md`](D1_DESIGN.md)
- [`D1_STEP1_RUNBOOK.md`](D1_STEP1_RUNBOOK.md)
- [`D1_STEP2_RUNBOOK.md`](D1_STEP2_RUNBOOK.md)
- [`D1_RESULT.md`](D1_RESULT.md)
- [`D2_RESULT.md`](D2_RESULT.md)
- [`D3_RULINGS.md`](D3_RULINGS.md)
- [`D3_RESULT.md`](D3_RESULT.md)
- [`WEILUE_FIX_RUNBOOK.md`](WEILUE_FIX_RUNBOOK.md)
- [`FINDINGS_9_TO_13.md`](FINDINGS_9_TO_13.md)
- [`D4_START.md`](D4_START.md)
- [`D4_PILOT_RUNBOOK.md`](D4_PILOT_RUNBOOK.md)
- [`D4_DAY1_STATE.md`](D4_DAY1_STATE.md)
- [`D4_RULINGS.md`](D4_RULINGS.md)
- [`D4_RESULT.md`](D4_RESULT.md)
- [`FINDINGS_14_TO_18.md`](FINDINGS_14_TO_18.md)

## Block E: the measured runs, and the Sonnet arm

2026-08-25 to 2026-08-28.

- [`BLOCK_E_START.md`](BLOCK_E_START.md)
- [`BLOCK_E_RUNBOOK.md`](BLOCK_E_RUNBOOK.md)
- [`BLOCK_E_DAY1_DRYRUN.md`](BLOCK_E_DAY1_DRYRUN.md)
- [`BLOCK_E_DAY1_RESULT.md`](BLOCK_E_DAY1_RESULT.md)
- [`BLOCK_E_DAY2_START.md`](BLOCK_E_DAY2_START.md)
- [`BLOCK_E_DAY2_RESULT.md`](BLOCK_E_DAY2_RESULT.md)
- [`BLOCK_E_DAY3_START.md`](BLOCK_E_DAY3_START.md)
- [`BLOCK_E_RESULT.md`](BLOCK_E_RESULT.md)
- [`SONNET_ARM_RUNBOOK.md`](SONNET_ARM_RUNBOOK.md)
- [`ARM_RESULT.md`](ARM_RESULT.md)

## Block F: the corpus from 24 records to 54, region by region

2026-08-28 to 2026-09-06, in tranches F0 to F7. F4 to F7 are the curation tranches, and their CANDIDATES documents record the hunts before any record was written.

- [`BLOCK_F_START.md`](BLOCK_F_START.md)
- [`F0_RESULT.md`](F0_RESULT.md)
- [`F0_RULINGS.md`](F0_RULINGS.md)
- [`F1_START.md`](F1_START.md)
- [`F1_HANDOFF.md`](F1_HANDOFF.md)
- [`F1_RUNBOOK.md`](F1_RUNBOOK.md)
- [`F1_RULINGS.md`](F1_RULINGS.md)
- [`F1_RESULT.md`](F1_RESULT.md)
- [`F2_START.md`](F2_START.md)
- [`F2_RUNBOOK.md`](F2_RUNBOOK.md)
- [`F2_RULINGS.md`](F2_RULINGS.md)
- [`F2_RESULT.md`](F2_RESULT.md)
- [`F3_START.md`](F3_START.md)
- [`F3_RUNBOOK.md`](F3_RUNBOOK.md)
- [`F3_RULINGS.md`](F3_RULINGS.md)
- [`F3_RESULT.md`](F3_RESULT.md)
- [`F4_START.md`](F4_START.md)
- [`F4_CANDIDATES.md`](F4_CANDIDATES.md)
- [`F4_RULINGS.md`](F4_RULINGS.md)
- [`F4_PART2_START.md`](F4_PART2_START.md)
- [`F4_PART3_START.md`](F4_PART3_START.md)
- [`F4_PART3_RUNBOOK.md`](F4_PART3_RUNBOOK.md)
- [`F4_RESULT.md`](F4_RESULT.md)
- [`F5_START.md`](F5_START.md)
- [`F5_CANDIDATES.md`](F5_CANDIDATES.md)
- [`F5_RULINGS.md`](F5_RULINGS.md)
- [`F5_RESULT.md`](F5_RESULT.md)
- [`F5_PART2_START.md`](F5_PART2_START.md)
- [`F5_PART3_START.md`](F5_PART3_START.md)
- [`F5_PART3_BROWSER_PASSES.md`](F5_PART3_BROWSER_PASSES.md)
- [`F5_PART3_RULINGS.md`](F5_PART3_RULINGS.md)
- [`F5_PART3_RESULT.md`](F5_PART3_RESULT.md)
- [`F6_START.md`](F6_START.md)
- [`F6_CURATION_START.md`](F6_CURATION_START.md)
- [`F6_PROGRESS.md`](F6_PROGRESS.md)
- [`F6_BROWSER_PASS2.md`](F6_BROWSER_PASS2.md)
- [`F6_RULINGS.md`](F6_RULINGS.md)
- [`F6_RANKING.md`](F6_RANKING.md)
- [`F6_RANKING_2.md`](F6_RANKING_2.md)
- [`F6_RESULT.md`](F6_RESULT.md)
- [`F7_START.md`](F7_START.md)
- [`F7_CURATION_START.md`](F7_CURATION_START.md)
- [`F7_HOST_RUNBOOK.md`](F7_HOST_RUNBOOK.md)
- [`F7_RANKING.md`](F7_RANKING.md)
- [`F7_RESULT.md`](F7_RESULT.md)

## Block G: the Phase 2 exit gate

2026-09-06 to 2026-09-07. **Phase 2 exits on a pivot:** the corpus stops at 54 records, and the work turns to the portal. If you read one result document, read this one.

- [`BLOCK_G_START.md`](BLOCK_G_START.md)
- [`BLOCK_G_START_AMENDMENT_1.md`](BLOCK_G_START_AMENDMENT_1.md)
- [`BLOCK_G_VERDICT_SHAPE.md`](BLOCK_G_VERDICT_SHAPE.md)
- [`BLOCK_G_RESULT.md`](BLOCK_G_RESULT.md)

## W3: declare, don't infer

2026-09-07. Every text-bearing field declares its own language, and the loader refuses to guess one.

- [`W3_START.md`](W3_START.md)
- [`W3_DECLARE_DONT_INFER.md`](W3_DECLARE_DONT_INFER.md)
- [`W3_HOST_RUNBOOK.md`](W3_HOST_RUNBOOK.md)
- [`W3_RULINGS.md`](W3_RULINGS.md)
- [`W3_RESULT.md`](W3_RESULT.md)

## The portal: click-through citation and the map

2026-09-07.

- [`UI_START.md`](UI_START.md)
- [`UI_PREDICTIONS.md`](UI_PREDICTIONS.md)
- [`UI_RULINGS.md`](UI_RULINGS.md)
- [`UI_RESULT.md`](UI_RESULT.md)

## The portal: design

2026-09-07.

- [`UI_DESIGN_START.md`](UI_DESIGN_START.md)
- [`UI_DESIGN_START_AMENDMENT_1.md`](UI_DESIGN_START_AMENDMENT_1.md)
- [`UI_DESIGN_PREDICTIONS.md`](UI_DESIGN_PREDICTIONS.md)
- [`UI_DESIGN_RULINGS.md`](UI_DESIGN_RULINGS.md)
- [`UI_DESIGN_RESULT.md`](UI_DESIGN_RESULT.md)

## The portal: the Questions tab

2026-09-08.

- [`UI_QUESTIONS_START.md`](UI_QUESTIONS_START.md)
- [`UI_QUESTIONS_PREDICTIONS.md`](UI_QUESTIONS_PREDICTIONS.md)
- [`UI_QUESTIONS_RULINGS.md`](UI_QUESTIONS_RULINGS.md)
- [`UI_QUESTIONS_RESULT.md`](UI_QUESTIONS_RESULT.md)

## The portal: the map, and every record on it by region

2026-09-10 to 2026-09-12.

- [`UI_MAP_PREDICTIONS.md`](UI_MAP_PREDICTIONS.md)
- [`UI_MAP_RESULT.md`](UI_MAP_RESULT.md)
- [`UI_MAP_REGIONS_START.md`](UI_MAP_REGIONS_START.md)
- [`UI_MAP_REGIONS_PREDICTIONS.md`](UI_MAP_REGIONS_PREDICTIONS.md)
- [`UI_MAP_REGIONS_RULINGS.md`](UI_MAP_REGIONS_RULINGS.md)
- [`UI_MAP_REGIONS_RESULT.md`](UI_MAP_REGIONS_RESULT.md)

## The portal: the Methodology tab

2026-09-11 to 2026-09-22.

- [`UI_METHODOLOGY_START.md`](UI_METHODOLOGY_START.md)
- [`UI_METHODOLOGY_PREDICTIONS.md`](UI_METHODOLOGY_PREDICTIONS.md)
- [`UI_METHODOLOGY_RULINGS.md`](UI_METHODOLOGY_RULINGS.md)
- [`UI_METHODOLOGY_RESULT.md`](UI_METHODOLOGY_RESULT.md)
- [`UI_METHODOLOGY_DESIGN_START.md`](UI_METHODOLOGY_DESIGN_START.md)
- [`UI_METHODOLOGY_DESIGN_PREDICTIONS.md`](UI_METHODOLOGY_DESIGN_PREDICTIONS.md)
- [`UI_METHODOLOGY_BUILD_START.md`](UI_METHODOLOGY_BUILD_START.md)
- [`METHODOLOGY_COPY_FINAL.md`](METHODOLOGY_COPY_FINAL.md)
- [`UI_METHODOLOGY_FINAL_RESULT.md`](UI_METHODOLOGY_FINAL_RESULT.md)

## Rights validation

2026-09-14. Each record's rights position read off its own source and quoted.

- [`RIGHTS_VALIDATION_START.md`](RIGHTS_VALIDATION_START.md)
- [`RIGHTS_VALIDATION_PREDICTIONS.md`](RIGHTS_VALIDATION_PREDICTIONS.md)
- [`RIGHTS_VALIDATION_RUNBOOK.md`](RIGHTS_VALIDATION_RUNBOOK.md)
- [`RIGHTS_VALIDATION_READINGS.md`](RIGHTS_VALIDATION_READINGS.md)
- [`RIGHTS_VALIDATION_RULINGS.md`](RIGHTS_VALIDATION_RULINGS.md)
- [`RIGHTS_VALIDATION_RESULT.md`](RIGHTS_VALIDATION_RESULT.md)
- [`RIGHTS_FOR_METHODOLOGY_SECTION2.md`](RIGHTS_FOR_METHODOLOGY_SECTION2.md)

## The portal: loose ends

2026-09-15 to 2026-09-16.

- [`UI_LOOSE_ENDS_START.md`](UI_LOOSE_ENDS_START.md)
- [`UI_LOOSE_ENDS_START_AMENDMENT_1.md`](UI_LOOSE_ENDS_START_AMENDMENT_1.md)
- [`UI_LOOSE_ENDS_RESULT.md`](UI_LOOSE_ENDS_RESULT.md)

## Deploy

2026-09-22 to 2026-09-23. The last rights readings, the re-sourcing of two Greek inscriptions from a public-domain edition, and the launch at https://mundus-ulterior.pages.dev/.

- [`DEPLOY_START.md`](DEPLOY_START.md)
- [`DEPLOY_PREDICTIONS.md`](DEPLOY_PREDICTIONS.md)
- [`DEPLOY_RULINGS.md`](DEPLOY_RULINGS.md)
- [`DEPLOY_READINGS.md`](DEPLOY_READINGS.md)
- [`DEPLOY_COLLATION.md`](DEPLOY_COLLATION.md)
- [`DEPLOY_RESULT.md`](DEPLOY_RESULT.md)

## After launch

2026-09-23 to 2026-10-23. Feedback from trusted readers, and the changes it led to. These threads closed with handoffs rather than result documents.

- [`site-feedback-thread1-handoff.md`](site-feedback-thread1-handoff.md): The masthead redrawn, and site fixes from the feedback.
- [`site-text-thread2-handoff.md`](site-text-thread2-handoff.md): The site text revised from Rob's edits.
- [`site-graphics-thread3-handoff.md`](site-graphics-thread3-handoff.md): Six figures added to the Methodology tab, every number drawn from the data.

## The public release

From 2026-10-23: preparing this repository, including what was withdrawn from its history and why.

- [`github-release-start.md`](github-release-start.md): The start document for the release.
- [`GITHUB_RELEASE_PREDICTIONS.md`](GITHUB_RELEASE_PREDICTIONS.md): The release's predictions, committed before anything changed.
- [`GITHUB_RELEASE_RULINGS.md`](GITHUB_RELEASE_RULINGS.md): RULINGS 101 and 102, and FINDING 126.
- [`GITHUB_RELEASE_READINGS.md`](GITHUB_RELEASE_READINGS.md): Each of the 54 rights cells read again, for a repository rather than the site.
- [`GITHUB_RELEASE_HISTORY_SCAN.md`](GITHUB_RELEASE_HISTORY_SCAN.md): What the history held of the withdrawn text, and the rewrite that removed it.
- [`COMMIT_MAP.md`](COMMIT_MAP.md): Old commit hashes to new.
