# Commit map: old hashes to new

The public history was rewritten once, on 2026-10-26, before the repository was
first pushed (`docs/GITHUB_RELEASE_HISTORY_SCAN.md`, RULING 102). The rewrite
mapped the author address on Rob's commits to his GitHub noreply address, and
replaced the full copies of two withdrawn Greek excerpts with a notice. **Every
commit hash changed. No commit was added, dropped, or re-dated.**

The documents in `docs/` were written before the rewrite, so the hashes they
cite are the OLD ones. Find an old hash below, by its first seven characters, to
get the commit it now is. Hashes inside commit messages were rewritten to the
new ones by `git filter-repo` itself.

278 commits, oldest first. Commits made after the rewrite have only one
hash and are not listed.

## Short form: old, new, date, subject

```
old      new      date        subject
9470506  504a187  2026-08-12  Phase 1 baseline: 24 docs / 56 chunks / 54 embedded (confirmed 2026-08-12)
9d2865a  f3d885d  2026-08-12  Block 0: regenerate stale UI bundle (61->77 runs), add staleness guard to check_ui.mjs
bbca400  a1d3722  2026-08-12  Block A1: place-field shape, strict loader, dated-snapshot gazetteer
08ade9f  dedd835  2026-08-12  A1: licence + declaration recorded; require_file across all paths
3602d1b  7dcf6ec  2026-08-13  A2: pleiades_id -> gazetteer + gazetteer_id; namespaced cache; GeoNames declared
6ee866a  d89df92  2026-08-13  A2: seven records placed, nine Pleiades ids resolved (8/24)
013ae4a  8884d2f  2026-08-13  A2: three judgement records; no_places_reason and origin_places
bb3bef5  e17c2de  2026-08-16  Blocks A3-C3: ranking harness, distractors, W2b curve, six rulings, C3 rerank
695a06b  df5c4fc  2026-08-16  Block C: rulings 7-11, C2a section collapse, C3 rerank measured, via-original companion
bff0605  bd77c49  2026-08-19  Block C: C2 measured and rejected, rulings 12-25; frozen config for C5-C6
744e57c  c8ae5f6  2026-08-20  Block C: C5 and C6 run archives, ruling 25 documents, G2 at six of seven
ccca17e  89c0432  2026-08-20  C7: the via-original sequencing fix (21/30 pre-rerank, 22/30 post), ruling 26, Block C c
0518cf4  1814257  2026-08-20  C7: result and the Block D starting point
77d51fa  0553565  2026-08-21  PROGRESS: state at the close of C7 — tree 89c0432, the three archived runs, the unregist
7c003a7  b178eaf  2026-08-21  D TASK 0: adulis-exports, and the answer path had been dead since bd77c49
73e3c80  16946ce  2026-08-21  D1 step 1: one definition of what a seed record is
f54c585  f7d5ba6  2026-08-21  D1 step 2: the corpus version travels with every answer
d426b68  c4b14c2  2026-08-21  Block D: TASK 0 and TASK 1 closed, rulings registered, PROGRESS written
9ea1774  bf7e000  2026-08-22  D2: every case declares its expected behaviour, and the loader refuses a default
62b72cc  992a145  2026-08-22  D2: record the host run, and rule on the vimose-runes label
45f20d6  a5ce05f  2026-08-22  D3: the gold set goes from 6 cases to 32, written against the D2 loader
3a9abd6  ebf5d0e  2026-08-22  Weilue fix: the runbook, and gitignore the commit-message drafts
5289f55  bc147cb  2026-08-22  Weilue: replace an invented original_text_excerpt with the sourced Sanguozhi text
d0ef3bc  dd3f25b  2026-08-22  FINDING 13: make "quoted the record's own language" an assertable thing
5b9aed2  5f34ea1  2026-08-22  Archive the runs behind the Weilue fix, and the runbook as it ended up
846d5b9  7ef53c9  2026-08-22  FINDING 10: guard this process's own stdout, in all 43 entry points
5a3bd7b  bf5778a  2026-08-22  D3 and the Weilue investigation, written up as two documents
2c8f20e  39026e8  2026-08-22  Keep the Finding 10 demonstration: build_ui_data --verify completing under a redirect wi
b1e11ab  2a13c00  2026-08-22  FINDING 11: the paraphrase flag marked suspicion and nothing ever resolved it
bdc79ba  67fad44  2026-08-24  Block D TASK 3: the handoff document this thread opened from
424fef1  ce1eb70  2026-08-24  D4-A / FINDING 12: a gold pair that stops resolving kills the run
5c238c4  f88c886  2026-08-24  D4-B/C: a duplicate question cannot shadow a case, and the sweep learns what a session i
dce1ad1  28bc120  2026-08-24  FINDING 15: a mutation harness resolved an ambiguous target by taking the first source, 
fbabb93  2f1ffd8  2026-08-24  FINDING 16: CPython's bytecode cache validated a mutation away, and the flag that forecl
483be65  c0dbdb8  2026-08-24  FINDING 14: the sweep never recorded the corpus it was made against
ac96556  7e6780b  2026-08-25  D4 day 2: the pilot crossed a date boundary, and FINDING 18
a82f039  3f0ccef  2026-08-25  Block E: the handoff document the next thread opens from
2a4077d  830bc70  2026-08-26  Block E prep: the variance decomposition, the calibration scope, and a demotion that cos
fceec7a  97c8b9f  2026-08-26  Block E: the probe's null result, and why the answer path runs haiku
3a1fde8  21c9f5d  2026-08-26  Block E: one failed chat call no longer takes the day
98939c7  f40d0f6  2026-08-26  Block E day 1: what the dry run said, before the 99 calls
a1850fd  68a7a15  2026-08-26  Block E day 1: two sessions, 198 runs, floor met in both
4d746d9  be185c4  2026-08-26  Block E day 1: result, findings 19-22, and the day 2 handoff
325a82b  c5c96a6  2026-08-26  Block E day 1: result, findings 19-22, day 2 handoff, dates amended to 27/28
4860711  b490cd5  2026-08-27  Block E day 2: the date effect was measured, and it is not there
28e8c62  edeb45c  2026-08-27  Block E: the day 3 handoff, and the fifth owed correction
e3fed40  c948dd5  2026-08-28  Block E day 3: the block stopped replicating, and the pass rate did not move
1bdaf04  dab1575  2026-08-28  Block E corrections: all eight applied, and two found while applying them
e207e65  fc624d4  2026-08-28  Block F: the starting point, and four decisions left open on purpose
b42ba43  6d8399d  2026-08-28  Block F decision block: the four decisions, and the arm the archive never recorded
bee344e  17a7df8  2026-08-28  Block F: the stale stand-in, and the mutation that passed for the wrong reason
3dfcae1  e12280c  2026-08-28  Rulings 40-42: the article, the exclusion built from its own question, and Ardashir
2091e03  98dd62c  2026-08-28  The harnesses: mojibake, a discarded return code, and an LF source converted in a commit
54512b7  73f927b  2026-08-28  The rulings register catches up: 40-42 were declared and not indexed
dcc285a  e3dbe55  2026-08-28  PROGRESS.md catches up two blocks, and F1 gets a starting point
4ec42d1  d40a749  2026-08-28  Ruling 36 reaches the runner: a foreign arm is not a subject of this floor
7d34272  48d589b  2026-08-28  The sonnet arm: 165 runs, two findings, and a floor that did not move
13a417d  5ad5efc  2026-08-28  FINDING 29's third mutation reported MISS, and the MISS was right
a6442b6  e3b9300  2026-08-28  F1_HANDOFF names the commit it was written at
577a0e2  c354b11  2026-08-29  F1: five tiers, a target mix, and a suite that had been red for a week
a74a307  576bb22  2026-08-29  F2: a column that cannot be gamed, and a comparator that was never measured
51e0f21  534ddb9  2026-08-29  F3_START names the commit it was written at, and the clause floor.json lacks
a1af62d  dc5473b  2026-08-31  F3: the clause the floor did not have, and a date nobody had booked
445c6da  a46e06c  2026-08-31  F3 owed item 1 closed: 288 mutations on the host, no MISS
8df6e31  db172d4  2026-08-31  F3: the BASELINE check reaches eight harnesses of eight, and FINDING 35
e7d932e  ad17a79  2026-08-31  F3: the baseline check pays for itself in an hour -- FINDINGS 36 and 37
73c05f3  eeaf419  2026-08-31  F3 ruling 52: a ledger row may be retired, and only if its record does not exist
91c05c2  91b837a  2026-08-31  F3: RECORD 25. The corpus moves for the first time since Part 7.
31f43a9  0d4e45c  2026-08-31  F3: RECORD 26, and the first record in this corpus under an open licence
5ed5c9a  aeea290  2026-08-31  F3: the delivery check -- the plan was guarded, the delivery was not
50bd59d  9ae4620  2026-08-31  F3: FINDING 38, and RECORD 27 -- the first record curated to be gloss-capable
5b6c6cd  c716417  2026-08-31  F3: check 10 triaged record 27, and one sentence was removed rather than defended
8c954dc  a15e4c3  2026-08-31  F3: FINDING 39 -- a record can falsify a correctly_refusable case
d540549  7c8a42a  2026-08-31  F3: RECORD 28 -- a Greek Heracles that the Parthian calls Verethragna
b45995c  30761ef  2026-08-31  F3 records 29-30: the first verbatim_machine_english pair, and their cases
e0b77c4  6b6cd87  2026-08-31  F3: FINDING 41 -- verbatim_machine_english is a residue, not a target
3010abd  a24315e  2026-08-31  F3 CLOSED: the handoff, and two findings the sub-tranche run produced
ea1b9ae  eed00d3  2026-08-31  F4 START — the three decisions that have to precede the first record
bbd9324  df499be  2026-08-31  F4: rulings 53-58 and findings 44-46, all declared before record 31
8fadc20  c66e0bd  2026-08-31  F4 step 0: FINDING 42 -- a whitespace CATEGORY, not a whitespace tolerance
d1817a8  b1964bc  2026-08-31  F4 step 0: FINDING 43's hardcoded rank, derived -- and a rule for the next one
8754be6  e38f1db  2026-08-31  F4 step 0: RULING 56 -- the quotation quota splits, and the gold set is counted
fa8d18f  4a55231  2026-08-31  F4: FINDING 47, and a correction to ruling 56 made before it was acted on
03e430f  5a5ada2  2026-08-31  F4 RECORD 31 -- Monumentum Adulitanum II, and the first pair written under ruling 54
58c6b77  57ab884  2026-08-31  F4 RECORD 32 -- Silko at Talmis, ruling 59, and FINDING 50
179e975  0f7a10d  2026-08-31  F4: re-anchor two mutate_cost mutations that ruling 59 moved
f1bd391  9d23231  2026-08-31  F4 PART 2 START -- East Asia, and a workflow that changed under F4
c99aaa8  c989c0b  2026-09-01  F4 PART 2 opens with ruling 60 and FINDING 51, before any excerpt is chosen
a5c0ae6  c0122e0  2026-09-01  F4 PART 2: ruling 54's debt paid, and the stamp made a field rather than a note
585c72f  b4cb295  2026-09-01  F4 RECORD 33 -- the Jingjiao stele describes Rome, and FINDINGS 53 and 54
93916eb  c0afd60  2026-09-01  F4 RECORD 34 -- Qin Lun at the court of Sun Quan, ruling 62, and FINDING 55
4f95db2  1fdb740  2026-09-01  F4 RECORD 35 -- the Fulin embassy of 643 and its glass, and the tier aimed at
935c35a  c9f3fea  2026-09-01  F4 PART 2 CLOSED -- the handoff to Part 3
4d3ebe2  95f4a52  2026-09-04  F4 PART 3: the close's instrument work, before the ranking run
e6c2aff  34398da  2026-09-04  F4 CLOSED: two predictions read, the harnesses settled, and the directory nobody had enu
7d4b38b  af7bde5  2026-09-04  F4: 254 mutations verified, the newline repair measured, and the ninth harness
5497a2b  f2782e6  2026-09-04  F4: all nine harnesses green at one tree, 389 mutations
74c480c  3fc27a6  2026-09-04  F5 START: three targets that cannot be reached, and the arithmetic nobody had done
bf85a4f  b741792  2026-09-04  F5: the one re-cut, four owed instrument changes, and three targets decided
c1dfa1e  9607e50  2026-09-04  F5: the check written to catch a stale mutation had a platform bug the bridge could not 
fedb2c9  d1cc7f9  2026-09-04  F5: two slots re-pointed rather than added, every region's floor cleared, and the target
6c7b7cd  0ec2fc7  2026-09-04  F5: a rule's stated reason outlived the reason, in the same commit as the ruling that ki
c73e3a3  c02af0b  2026-09-04  F5 CLOSED: seven records allocated, none curated, and every one of them now findable
4c97f8f  e1c46fc  2026-09-04  F5 addendum: FINDING 68, asked by the project owner after the close
16ffe3f  dc6fb41  2026-09-04  F5 PART 2 START: the next session is not F6, and the closing documents say it is
9deb041  e0a7589  2026-09-04  F5 candidates: the seam is necessary and not sufficient, and two slots fail after findin
7e6c021  b22ec8c  2026-09-04  F5 RECORD 36 -- Tang Huiyao 99 on Fulin, the last machine-English record this project ca
cf4be19  9b860e1  2026-09-04  F5 PART 3 START: one record of seven, four candidates settled and waiting on a paste, an
f29517b  188b12b  2026-09-05  F5 Part 3: the rulings and the browser passes — FINDING 69, Ruling 74, FINDING 70, FINDI
c15317c  0d77007  2026-09-05  F5 Part 3: records 37-40 — Ruwafa, Syllaeus, Abnun, Brhatsamhita — with their tier, glos
0f5bfe0  d2d81ea  2026-09-05  F5 Part 3: the three expect_quoted_from_original gold cases the allocation declared — an
f80e2ab  49ad73e  2026-09-05  F5 Part 3: Ruling 75 and FINDING 72 — South Asia's vme slot fails, ruling 72's predictio
26561b3  32f2a93  2026-09-05  F5 Part 3: eastasia-04's Chang'an placement — an id that was never resolved, a ground th
a61ac62  51b149a  2026-09-05  F5 Part 3: the ranking run read against its two pre-registered predictions — ruling 70 c
29702f9  fc785a3  2026-09-05  F5 Part 3: record 40's transcription breach is retired — confirmed character for charact
960e7e5  69b614e  2026-09-05  F5 Part 3: rebuild ui/data.js — the eleventh instrument goes green after 622 files of st
d5fae4f  27abff6  2026-09-05  F5 Part 3: the result document, and F5.closed = true — the tranche closes at 5 of 7 with
6ccac91  7d1c5cb  2026-09-05  F5 Part 3: FINDING 75 — three tier counts in this session's own documents were wrong, an
a20214e  1918e67  2026-09-05  F6 START — the handoff document, with the first state block in Block F that is verify's 
eab5905  c567857  2026-09-06  F6: browser pass 2 overturns two more negatives, rulings 76-78 re-point Persia's floor i
082185e  2c4a00e  2026-09-06  F6: four instrument debts closed -- FINDING 68's subtotal, FINDING 70's agent field, rul
39bcc1f  415f487  2026-09-06  F6 RECORD 41 -- Sahrestaniha i Eransahr, the western quarter, and PERSIA'S FLOOR IS MET:
4c940f7  684f3a1  2026-09-06  F6 RECORD 42 -- the Tjurko 1 bracteate: a Proto-Norse inscription that calls gold `walha
7a819c4  13a3e1f  2026-09-06  F6 RECORD 43 -- the Rycksta stone: a man goes I GRIKKJUM and divides up gold, and SCANDI
61dd1d6  0cd060b  2026-09-06  F6 PROGRESS -- three of seven placed, two of three floors closed, and F6 STAYS OPEN. The
de43309  c3ef77a  2026-09-06  F6: STARTUP.md's daily ritual had five stale figures and an instruction to STOP on the e
c5810ca  1b03730  2026-09-06  F6: the ranking run read against ruling 78 -- P3 CONFIRMED with its crowder named, P1 an
0b73aa1  9f2e3aa  2026-09-06  F6: FINDING 78 -- 111 mutations verified this morning and NOT ONE of them touched either
c1e7909  f25c877  2026-09-06  F6: the like-for-like ranking run -- SIX pairs fell, NONE improved, and BOTH headline nu
7c50bba  f156aca  2026-09-06  F6: correct F6_PROGRESS.md's own ranking section, which went stale within hours of being
b8a4cd3  8e0b690  2026-09-06  F6 CURATION START -- the handoff for the four records that are left, with a state block 
2991e04  3e6b02a  2026-09-06  F6: FINDING 80 -- the handoff document mis-describes the record it points the Africa hun
8a24bee  4c91536  2026-09-06  F6 record 44: africa-06-ezana-rie189 -- the LAST per-region floor in Block F closes, and
c3a0869  966dd38  2026-09-06  F6 record 45: arabia-07-cih541 -- the ambassador of ROME at a South Arabian court in 548
e1f0d66  f279455  2026-09-06  F6 record 46: eastasia-08-songshi-fulin -- the East Asia slot, filled by the SECOND-CHOI
b24b8e9  41086be  2026-09-06  F6 record 47: africa-07-cosmas-sasu -- the seventh and last record of the tranche, the F
1a9d4ac  95258f0  2026-09-06  F6 FINDING 81: the guard that nobody had ever seen fire, fired -- a gold refusal case na
114ce15  f379333  2026-09-06  F6: FINDINGS 81 and 82 written up, and two corrections to F6_CURATION_START.md's own war
59d99bf  e31cbda  2026-09-06  F6 RESULT: seven of seven placed, the LAST per-region floor in Block F closed, and F6.cl
d34d3f1  2e73122  2026-09-06  F6_RANKING_2: the run F6 owed, made after F6 closed -- P1 CONFIRMED, P2 CONFIRMED, P4 RE
5b33934  fa3170d  2026-09-06  F7 START: the last sub-tranche of Block F -- seven slots, none of them a source-language
d2868fc  358b1c4  2026-09-06  F7 CURATION START: seven slots pointed at seven named candidates, the gloss declaration 
b029edd  6cc1bbe  2026-09-06  F7 record 48: persia-07-met-ewer-anahita -- maenads of Dionysus or the Iranian Anahita, 
8242629  7d00d7e  2026-09-06  F7 record 49: arabia-08-walters-marib-pediment -- a nude goddess in vine leaves on a ped
915cd9e  92250bb  2026-09-06  F7 record 50: southasia-07-bm-claudius-aureus -- minted at Rome in 41-42, found in India
f2ecfee  5cf01fc  2026-09-06  F7 record 51: seasia-08-pong-tuk-lamp -- a bronze lamp with a Silenus head and two dolph
4c10882  581720e  2026-09-06  F7 record 52: seasia-09-oc-eo-unesco -- Roman gold coins, Han bronze mirrors and Persian
163b009  0434d11  2026-09-06  F7 record 53: eastasia-09-jiutangshu-fulin -- Byzantium described from the Tang court, a
865a3d3  9a9b242  2026-09-06  F7 record 54: southasia-06-cosmas-taprobane -- a Roman and a Persian argue before the ki
50c19fe  78cd19a  2026-09-06  FINDING 89: the fabrication-marker guard fired a second time, and the sentence that had 
327bd2c  b912eb8  2026-09-06  F7 HOST RUNBOOK: the ranking run F7 owes, the five predictions it is read against, and t
5b23011  d287919  2026-09-06  FINDING 90: the runbook named its own commit hash, was committed, and falsified its own 
a731889  6156064  2026-09-06  F7_RANKING: P1, P4 and P5 confirmed, P2 and P3 REFUTED, and FINDING 91 -- a fall is pred
20793e6  3bd4aec  2026-09-06  F7 RESULT: seven of seven placed, four of five tiers on target, F7.closed = true -- and 
0adbc94  e989c13  2026-09-06  BLOCK G START: the Phase 2 exit gate, one session, and it opens with G3 FAILED box by bo
b12ed34  0fdbac0  2026-09-07  Block G amendment 1, and the W3 declare-don't-infer handoff
526af18  7db3f1e  2026-09-07  BLOCK G: the shape of the verdict, written and committed BEFORE the result
e8e92f3  06b8ca4  2026-09-07  BLOCK G RESULT: PHASE 2 EXITS ON A PIVOT, and G3 is CLOSED AND FAILED on nine boxes with
59dcd1e  6bc2b6c  2026-09-07  W3 START: the three predictions, the four decisions and FINDING 94, written before the f
f8eaa19  1a6960b  2026-09-07  W3: FINDINGS 82 and 86 closed as one item -- every text-bearing field declares its own l
d62c8d0  cb12087  2026-09-07  W3: FINDING 97 -- three refusal guards were watching the predicate and not their clause,
0f33547  4ad523c  2026-09-07  W3 closed: FINDING 97 and the 84/84 re-run. UI_START.md scopes the next block to click-t
7c6d5f6  c011d49  2026-09-07  UI block: predictions and ruling 83, written before any code
07cbd08  6cf94e3  2026-09-07  UI block: D1's second axis on screen, FINDING 98 closed, debt row 7 paid
610fe25  5aa252e  2026-09-07  UI block: FINDING 99 -- every citation marker on this page was broken HTML
6ddb5e6  e016529  2026-09-07  UI block: UI_RESULT.md, and RULINGS.md's next-free line corrected
67f30bc  5e7dbbf  2026-09-07  UI DESIGN block: the start document, written at the UI block's close
43ac562  cd9858b  2026-09-07  UI DESIGN START amendment 1: the sequence, and what a coming port changes
64fb3e7  9d14f3d  2026-09-07  UI DESIGN block: predictions and ruling 84, before a line of ui/ is edited
e86582e  3cca7e3  2026-09-07  UI DESIGN block: a design system in :root, the front section, deep links, and the phone
b640b01  59981b7  2026-09-07  UI DESIGN block: UI_DESIGN_RESULT.md, and RULINGS.md's next-free line carried forward
b6d4aaa  a5f8340  2026-09-07  UI DESIGN: the header line and the stat strip, cut to what a first-time reader needs
83b1b10  97b6aa2  2026-09-07  UI DESIGN: a Home tab, the tabs renamed, and the harness extended to cover the new view
439bd8b  beb0de3  2026-09-07  UI DESIGN: the masthead gets the corpus's own scripts and its own map
f53b6e9  882ddbb  2026-09-08  UI DESIGN: the script band is scrollable with a mouse, which it was not
a57f0ce  ba6438e  2026-09-08  UI DESIGN: the band's order, and a Greek specimen from outside the empire
a06ed0e  414638f  2026-09-08  ui/data.js and its manifest, regenerated on the host — and FINDING 101
db89c3e  70580e2  2026-09-08  UI DESIGN: the chain drawn on Home, and the map beside "What this portal does"
fa01756  25fbb2e  2026-09-08  UI DESIGN block closed: the result document brought up to date, and the Questions handof
ea87767  612cf4c  2026-09-08  UI QUESTIONS: the predictions, committed before a line of ui/ is edited
b50bcf4  7552c4b  2026-09-08  FINDING 100 fixed: the harness no longer counts script tags inside HTML comments
9d7f701  ad24092  2026-09-08  FINDING 101 fixed: build_ui_data.py writes BYTES, and ingest.verify asserts no seed reco
d32aa79  4e69bbf  2026-09-08  UI QUESTIONS: the rail grouped by region, the run apparatus gone, 43 -> 45 checks
2b247af  eca008b  2026-09-08  UI QUESTIONS block closed: rulings 85 and 86, findings 102 and 103, and the predictions 
5da1335  fe3a46b  2026-09-08  UI QUESTIONS: the cosine bar and its value off the source cards
d361ea4  0f77e45  2026-09-08  RULING 87: each refusal says which kind of refusal it is, and guard 46 re-derives every 
cf6a387  8d22b9c  2026-09-08  The header strip on every tab, and 'on disk' out of its citation line
1582411  12a4cdb  2026-09-08  The front section's third and fourth captions, reworded
f31debc  792e1a1  2026-09-08  The fourth front-section caption: 'failed citation checks'
59684ab  bd2b05a  2026-09-08  The front section's headline and claim, rewritten
595c601  475b772  2026-09-08  The two finding cards off the front section
6903cba  480ccb7  2026-09-08  The refusals note moves above its questions, and the withheld-failures line comes off th
68b5484  6b0d3ec  2026-09-08  The Provenance box's empty state, rewritten
ec58982  7c53b2e  2026-09-08  The quotation panel: three chain rows out, the characters heading renamed, the dormant n
77fdaed  51567d9  2026-09-08  'Has the record moved underneath this citation?' becomes one row in the chain
dd09dd7  f3e914c  2026-09-08  RULING 88: the second axis moves to Data and Sources with its guard, and FINDING 105 was
bb25cb2  ecec833  2026-09-09  The quotation panel gains region, language, date and findspot; the source panel loses si
42856ee  2273055  2026-09-09  The source panel's characters heading matches the quotation panel's
8e05a71  f522906  2026-09-09  The partial-archive box comes off the source panel
22f5376  c14afd9  2026-09-09  The masthead band: Ge'ez and Korean swap places
bc58c1a  f2437c4  2026-09-09  RULING 89: a record's note shows the curator's words about the source, and nothing about
c78ebab  44bc69c  2026-09-09  The rank row off the source panel
88d56c6  e85a222  2026-09-09  The session's documents brought up to date: ruling 89 declared, Part Two written, regist
a8d0e92  8b213ab  2026-09-10  The predictions, before a line of ui/ was edited
e705dd4  d67b502  2026-09-10  Section 3A: the Map tab's panel comes up beside the map
9fe18da  ca38889  2026-09-10  RULING 90: the empty state belongs to the tab, and no tab borrows another's
df2c564  8361dc5  2026-09-10  RULINGS.md: ruling 90 and finding 106 carried back, register at 91 / 107
82c8e7e  056e10e  2026-09-10  FINDING 107: "Claude outputs/" is not a leftover, it is where the app delivers
c2b0bda  996662a  2026-09-10  The map's marks and labels at a size a person can hit and read
5c2d640  3c8468c  2026-09-10  The Map tab is 'Map & Sources', and no prose types a tab name again
952f1f2  6b6b5af  2026-09-10  The phone's tab row wraps, so all four tabs arrive on screen
ae37fc0  dc0f232  2026-09-10  'Data & Sources' becomes 'Methodology'
a8309ed  c6cb1d3  2026-09-10  The map goes full width and the Guide band sits above it
8a6643e  db53869  2026-09-10  FINDING 108: the map's mark sizes depend on the layout, and no guard can see it
e45a066  9935a0e  2026-09-10  The map goes back to the left column and the Guide to the right
9041253  6890542  2026-09-10  The Guide box gets back and forward over the things you have opened
9cb0196  d90c768  2026-09-10  The geography ledger moves to Methodology
c5fd73e  cfd5dfe  2026-09-10  The Map block closes: predictions scored, and the regions thread scoped
3ceafdb  4e77a33  2026-09-10  The regions block predicts, and states in advance that the rescope does not touch East A
cb5ff9d  e42dc5d  2026-09-10  Every record reaches the map: the region band, and a third shape to draw it in
31b8475  d523f2f  2026-09-10  Four guards for the bands, and the third one was worthless until a red test said so
f2ede0c  a0b2cfa  2026-09-10  The band placer is measured rather than judged, and a band that cannot sit on its anchor
28fb66b  9aec5db  2026-09-10  Southeast Asia's band is placed between Sumatra and Borneo, and the page says a person p
101419b  66b7fe8  2026-09-10  A declared band is drawn where it was declared, and a band whose anchor is off screen is
2ad4c79  af2946e  2026-09-11  An edge is a hairline, and a hairline is not a click target
66a9673  50a333c  2026-09-11  The undrawn edges stay off the bands, and the page says why in the place a reader will a
4ac5f3c  e6620c8  2026-09-11  The five geography cards move to Methodology, the contested card is rewritten, and Metho
485ba64  1b2a85e  2026-09-11  The retrieval count comes off the record rows, and the guard that belongs with the card 
b038161  d193891  2026-09-11  The map key explains the numeral on a shared point, because a reader had to ask what it 
19cfba0  1488ffc  2026-09-11  The regions block closes: predictions scored, and the Methodology thread scoped
342868a  96f1dd9  2026-09-12  The regions block's register debt is paid, before this block writes any code
4e7bd9b  de87967  2026-09-12  Predictions and RULING 94, committed before a line of ui/ is edited
7df0755  91446e3  2026-09-12  The Guide gets a home button, and it puts the selection down rather than throwing the tr
fd53101  bc06775  2026-09-12  FINDING 116: a commit message written to its own file is not a commit
b499ac3  a532573  2026-09-12  §3 is paid: the two withheld failures are named, the substitution is labelled, and the c
8c3ad19  5a5796d  2026-09-12  §4A: Methodology gets its own address space, and the links already handed out are untouc
1a53df7  02a0cf5  2026-09-12  The Methodology block closes: predictions scored unamended, FINDING 117, and the design 
596d74c  de65421  2026-09-12  The Methodology tab gets a committed instrument, before the block that redesigns it writ
8e1f8f9  d7dfa93  2026-09-14  The rights backlog is scoped before it is worked: 38 unread records, bucketed, with the 
c839f54  94cc961  2026-09-14  Predictions written before a single rights target is opened, and the worklist is short b
7123b50  eec498f  2026-09-14  Twenty-four rights targets opened and read, four records contradicted by their own objec
41d175f  e582887  2026-09-14  RULING 96 and three findings, declared out of the confirmation pass rather than out of t
dba53ee  c5ed716  2026-09-14  Twenty-four rights cells written and one amended: the column goes from 16 read / 38 unre
219c8a5  ad04da2  2026-09-14  The rights block closes: 19 of 24 predictions correct, and the two that mattered most we
5e2a669  bd224c5  2026-09-14  Source material for Methodology Section 2, assembled so the copy can be written from dat
bab2efb  74169a5  2026-09-15  The rights column gains two declared fields, so the Methodology page can derive its figu
671e5c8  7cf134f  2026-09-15  Predictions for the Methodology design block, committed before a line of ui/ is edited
eccf722  7e5711a  2026-09-15  The design thread closes into two scoped threads, and the file bridge settles a question
90a5a5e  172e25f  2026-09-15  Amendment 1: the Lovable port becomes the final block, and three items could not run whe
f4ca8a3  4d39bdf  2026-09-16  Loose Ends C: unread_reason and contradicts_record_prose are guarded, not just declared
d90bed9  35b20cb  2026-09-16  Loose Ends closes: E already landed, D was already measured, C is the only code
abf944b  61d50bc  2026-09-21  The Methodology tab is built from the copy, and the Guide leaves it
d5002f2  9d7d632  2026-09-22  The section 1 figure says when the check runs, and stops claiming the files have not mov
3abe352  d1e8c3a  2026-09-22  Methodology closes: the one measure nobody reported is on the page, and the evidence pan
2725d56  d612954  2026-09-22  Methodology Final closes: the last prediction is scored, and the review found nothing
dfe3ab8  871d429  2026-09-22  Home says what the portal actually does, and the portal spells in American
5863383  b1a8850  2026-09-22  Home and Questions stop reading as narrow columns in a wide shell
e64d372  46d0e83  2026-09-22  The last block is a deploy, not a port, and the start document says why
cbc9ed2  3a504f6  2026-09-22  Deploy predictions and rulings, committed before anything is edited
6754900  fb172d4  2026-09-22  The register indexes 97 and 98, and its next-free line is true again
ce15efd  991c3b9  2026-09-22  Five rights cells read and confirmed; nine remain, all source_not_established
e08c978  94ba732  2026-09-22  Five more rights cells, all through Wikipedia, and RULING 99 says whose words a cell des
2da17c7  95b0fef  2026-09-23  Three clause-2 rights cells confirmed; one unread cell left, and Rob is finding the book
dcb41e7  58f71ac  2026-09-23  The rights column is closed: 54 of 54 read, before any public URL exists
c2409ea  086798b  2026-09-23  The record pass: S9-S18, the OGIS collation, and every known-wrong line fixed before the
c253b51  e273bfc  2026-09-23  Methodology prose runs full width, and the page stops downloading itself as its icon
ad2455c  909e7b9  2026-09-23  Deploy closes: Mundus Ulterior is live at mundus-ulterior.pages.dev, byte for byte
bc8f206  91668fb  2026-10-19  The masthead becomes a drawn landscape: the script band and map thumbnail go
048a697  aae3a0f  2026-10-19  Site fixes 2-6: the exactness claim, one language count, source records, the Questions h
ed3a7c3  f01a589  2026-10-20  The masthead gains two standards: a Roman eagle far off, a Han banner near
b2f019e  cf97aad  2026-10-20  The masthead wordmark grows, and the subtitle drops "source-based answers"
bd2e0de  b244e99  2026-10-20  Site text, round 1: Rob's edits from the Site Text doc
d0d358f  388d2b3  2026-10-23  The masthead standards show on phones, and the Han banner clears the theme button
14300d2  2346379  2026-10-23  The Methodology tab gains six figures, every number in them drawn from the data
e14f17e  4547ff9  2026-10-23  The Methodology section buttons grow, and each section title outranks its subheading
3bc8994  7388bb9  2026-10-26  GitHub release predictions and RULING 101, committed before anything is edited
f7331a0  8a8509c  2026-10-26  Redistribution pass: 54 cells read for the repository, 5 owe more, none leaves the tree
1730a2a  3985ea9  2026-10-26  History scan: the withdrawn Greek is six characters from OGIS, in 26 blobs, and in no an
```

## Full hashes: old, new

```
947050630efe840a8c8a88b86d447c2b190c9681  504a187dbebb38ad573edb0cc842f3bafd1d055d
9d2865a3b8651984ea3fafae78530900b6801861  f3d885d5d23ea11cb7ac66c7a2d4fa931d4f09ec
bbca400c3425d0f4e5df60c1570db1fd0c415b49  a1d3722e657755de1ab06598e01733924febefb9
08ade9fd29f02f695c79043d25632334a51085e9  dedd835bc25c685996f21cf7fb879aae7d3328f4
3602d1b0c2a3dcb593c4eda007db1a5f8c78bcca  7dcf6ec7a24f038c228449cf6f8b2e1754abb52f
6ee866a4bf6f61fad63553e77eb5dd68b85c80d6  d89df920d7fc845f408780e96c5c39d4678ee31a
013ae4a3787b6e872c9783cc89e84544bb672c20  8884d2f2683269230e1e3c3cc36b54311c536fa0
bb3bef58383cd52b3990ccf406c20157be6189a9  e17c2de1b9458a5655dae79526beebecdb1a7f6a
695a06b5c3c754dfe2753dfea0e86cf130e6a1d4  df5c4fcf8c2256ccba8f013614823fd4ce451ffb
bff0605b003c794cbc0739853360804114dafa81  bd77c49dbe6893198ddd3e142bbec0e4c20f197b
744e57c2f651a2f59754d19de18398dc886ab33c  c8ae5f6b6b178be5399105ddc3dc6943ad9b16d8
ccca17ed39575f34f4ff0e338c8f33ed516ce2df  89c0432fef7ea4d38cf60adef0461f953aabafb2
0518cf4292e373ca5d13222a8d09013b3f9b55dd  1814257471f2d88ab97b38bcfb2f664ff98708f0
77d51fa3ae019dd9274d61ee752acf32c9559549  05535658faeada4adb62a66298d8cc67b723ef56
7c003a7e7ba9a4c5030347f8963774788f9fd134  b178eaf893d700ef521d98e2de1e441dcf371ad2
73e3c800c33de112a746870889c0f6e580f1078b  16946ceb758982222821d978020954dc874e7e2d
f54c5850f73d7be754a1f1b59f84c50dccb83ae0  f7d5ba6ce0cb298bc7021ece6a6902a277857b3e
d426b680c9f0507e09960e0a1eaf0de16a1ba3a4  c4b14c2d13523da97e60ef5afa8c31190ec3b519
9ea177433a8ddc88b438a86faf910891d2d2dee6  bf7e0003460944e21dd3bc77d62ef2adbd7b06b4
62b72cc2d90f3a3526b566774c264cab23622548  992a145f8195ede678f7d9cab81f478da5fd9d35
45f20d63001740c6db13159a4fe4e2ca21291841  a5ce05f1a664df1d413ec58bc75691acd862f6d6
3a9abd6737e339333d1fc87876fc53e860a47afd  ebf5d0eb987dbb19114f623f22e72a863bb9aa5a
5289f55842231e660f980214dc260d0e3820ee69  bc147cbf3ceb33e3c90a8e25b8e1e36d14c9345b
d0ef3bcf717547519ae111d543cfab692e95c4fc  dd3f25b302f08b1aa23a4e6262346697aecd8e4e
5b9aed223aa365ae70426df80cb9e460ba84825b  5f34ea175470830d24ee0d1a355ed25a91261138
846d5b964100e57ec866135e71ae31f4e433a3ed  7ef53c9448b25f7047a28f516b00ad78bb7cc7b7
5a3bd7b3bb092262a6a5d8546c4e78cb555bf5a1  bf5778aeb9112b13204139a4170dc6e6b1b288b8
2c8f20e45e5423f9eff6186bbfe51a3465a2ecc0  39026e8efc44f85141c9507d0f9e4e1bf6b8b347
b1e11abde84e7d2978905000627100a11befd145  2a13c009f3095ba8c783edd80b18919765ea3692
bdc79bac1beb3df5482df3f26c3978de7c8cfbc0  67fad44892132238b29c707d8cf16a5b3736319b
424fef196800637e17380cb4193996566c84c8ec  ce1eb70d14cbb999e7027b544b4882749d41fb9d
5c238c4a6ac9f7a89adb7b9f6ce5d7a56d6e2732  f88c8860f76313eefb9bc5ceffe47632c4be7a14
dce1ad12caca7b12df3c820e12d9026fdbb1f23e  28bc120ebddd574ec9ca3d4a42d2f668e6c446e0
fbabb93fdc16422a9daaaf3fc5e78bd247f9a390  2f1ffd8a195ae224acd0bc79f49ea8e4c943c93e
483be65fe2a5cee65e9bb94fa66217cb4af2c24d  c0dbdb81b06f0f979d04abdb89259f8e61ac4619
ac96556d7418e3ee07772a4a3a6d3483fe58d0c9  7e6780b86f9cd2931782f9b2f44fc7fd02a95fce
a82f039e3d3e0f543c606d26333f1bd9718862be  3f0ccef0cb93cc4d39e584cee5787343bd768323
2a4077dd0b6cc4e86353985f833c285422190750  830bc7006e420be0f094d7a9322743a1738778e6
fceec7a219171d5e9587e9bdc0d9c16893263e00  97c8b9fe07d473d4024447e49c4da2058b0cc946
3a1fde8c8b244c1fd84de53b0f5d15145b61c7d1  21c9f5d50898533952e5c006447588362500a732
98939c7c2cff25199cebfc132ddc555b3bda2188  f40d0f6a1179f6ebf0ed04b88d2a9a8a9bd7f55b
a1850fd13da7e487f820405c75664d2a1336f448  68a7a15ed3222ae34dc2c3e399f9d7ae914b16c4
4d746d9695bebadc6e8680e482d20cac44892ba9  be185c433819486e21a24696ab962508b1e2b58b
325a82b40edae94a0ca628acfa63ed9e7765ce82  c5c96a64b1e959e6bcebee8d20c5b133ab31fc3b
4860711231c2e3120ffbc3d13ba61ce5e4ef6a46  b490cd5ddf2fa7877adcfd54fba470079cd7aef1
28e8c62171c8ec2ca4f16a57eefa1e39c93e2564  edeb45c19beacfa50040c7a4b91557aeed846b72
e3fed4034f84778644409e772d323a91a04b3121  c948dd58a6fcf9280d5ee4d5fb67c90814534800
1bdaf04e8d79c3488031acecdc891e7991943d19  dab1575414b5b633ac32f97384cba664c12de45f
e207e65d68c72ad8a496914c7f26454eacb9c7c4  fc624d476707108f26845c3e4592ceb3a31c4ed1
b42ba4366c4856bfd184862322fd65db4b541008  6d8399d8d28aa9d5b897add2c6120ce977af57b8
bee344ec249cc76a4dbda4712bd7a6ceac463f74  17a7df8b85e87a7f200222c31dd93d43a8c66d36
3dfcae151ac899901a87bc2f1aa30f95a583c288  e12280c43dc6040cacc62beb29f3e5530d58f055
2091e036acedcd870971e4f024f6e3722905794f  98dd62cf944b3d0bbd79f22404c5fabca7df30c9
54512b771313b2ec0210712c4a6c707c0809e5a3  73f927b4ca741a6130287513f928ddda1f9ad5f8
dcc285ad18ad2a8dcb6812619591221ac9e7c626  e3dbe550b300b5f788e95a4fedd7bcfb9da3f539
4ec42d1f11eeca21a75363ba08f3a7ddc62781bb  d40a7490c86389c62a5eff93429861d9ffd4d5cc
7d342723e0658f49cccacabc6d981efefb9ab19e  48d589b7a3a411c97f5edc674a9f185e729e1a5c
13a417d55e76275fa6d7a048226ec70505a66db3  5ad5efcb8b744e0869c80653b2fb216133567951
a6442b6d72361b4c0e8bf9b9f59a75ddb34c1e6e  e3b9300ef2fbc3754f27f1a9ca42a64be4fd8637
577a0e21419fc03ff9d951e4eb60866e3e515a52  c354b11ee2c0bd8fe42e928de834cb5d949ab689
a74a3071d9fce83bc92cbcb5f179607bd520ec62  576bb2276e0b2e34715920aa64f807c7713e851a
51e0f21de1dc2425600bed4468a08d30a79e32b2  534ddb956a71eabe69554f9d6e2c31b4a6093042
a1af62d350e317d2a57f31e625177cec35f60372  dc5473bfb2f0c1fce727a2e28ee1afb6b4ebd18a
445c6daec055b7f874bdc938c0f4c84c68972e06  a46e06c13259617badf8617146a426cc81305582
8df6e31106f6ca0ba3176e8964134b39c5a2e555  db172d43980d73fddf0b5e02d2171d35c5b7015f
e7d932e314d5a97f8e7d95f6f8553f7c7c2ffa77  ad17a7928c1b633f08403b525ac26a4273f72331
73c05f391dbbf7eb79b2459667930de9d3cc55a3  eeaf419c0244978c4c4337cf4f5006c2daaa7040
91c05c2b84c98ab59c8ab63f524eccce21f6526a  91b837a0fb91693cabe7c88f7532934618f8b10e
31f43a9f1d2bfebf8d94ff913f2afd680d1f4199  0d4e45caf29dd628c26de94758dd92507c4290a5
5ed5c9a2a97bf1c9eec74abf99f452ef7d0f5e09  aeea290fca76d942bf9508e1b531217827117151
50bd59d2a69a41d1572d66a7a41c86d642f57975  9ae46204b1ab4ffd27634d6e186cecd6630699ed
5b6c6cd6208b39f7fc64f78abc3e6c64f196bf52  c7164172099701077659c7303faf1e65ae4a43eb
8c954dcc6816aefc358b78c0d9f38959079bbd93  a15e4c34c6939577b333a7fdf00d5108628aa6b0
d5405496921734d57fc810a2240e133551e865b7  7c8a42ae8b08424d82696360600cf95046eb3d7b
b45995c34e016e230432fc8471b98f4c8bf0ba9a  30761effb90424b53e7e7d731990f52d08cb099b
e0b77c4999be509a93393c36e4d9a41c80059d39  6b6cd87889d871146fdabd90daff0303f5c1374d
3010abd07ddfa270784117168ca0508ff9a59f13  a24315e7df40a5f57e3cc4ff3c3df5d15f7ef5c1
ea1b9ae58d52ef2d1f66289b49235b0c5bf7b59f  eed00d37cc5702a80c5e0fe07a6ad122d7de7921
bbd932443247b01dc6bf87331523feceaf29d010  df499be20398d99528c7b5be5e0d9d64d2adea61
8fadc209d883312ef4a2b176384dd378b78b6a58  c66e0bd35e199e6ac3f70e309953ed24ab1ac059
d1817a88c850fe1c8174e5ae1e38e8fd2d4e33f8  b1964bc60948b31053d96a9abea4a67ca5763191
8754be647ae5fe6bf82312ceffdce872210eb0c1  e38f1dbc927bfd4bae326af5f1864d6be09f6c57
fa8d18f1562bc5ec7a0728909579c9ff0b93c974  4a552315a6f0a7f469bc5bbdd6c8966d3d63c0c6
03e430f329aaeaa0c2b792c32433ac90688cb114  5a5ada26e0f3ae1a59ef35061b68fb0ccf1128d3
58c6b771a3e3e8fab3e5a881c415df8ff37dec2e  57ab88422a7505bafcd3e1346a4501278ad6350d
179e975a8aa51cb6921427677e2f9cb25f2b1c1a  0f7a10dc5ada9147055390f06730654933049b17
f1bd391ff676b5826a3e8dfda7bb7e6eeb9d347a  9d23231bcaaf23a8429ed7f1ed76d88baa9d6a63
c99aaa8d82a110e33b4c2d2285d1daedb31486a9  c989c0bc45bd15d0706691dc51ddede7b6b08e47
a5c0ae6bbefd8bdfe531d1d7f549e55b6a9e5c30  c0122e0cd34f1727d7252eac39eb6c076cf81747
585c72f58f8aedb71a53690447a4a2cc1856c740  b4cb2951fe9b0a28776e6427e4af55de2c58e07b
93916eb63496cb0ce660584e97d99cdaf18d831f  c0afd6049528d4d781de8ee6449b49e5c84ce627
4f95db222675b26ade076188e4ee2f722c8d8701  1fdb740c9026c76b352230c47a0e32842296fe4a
935c35ad010bd993d6538c02a5069d1d5d162c8f  c9f3feab3a6a0ffa010fef1c07ae0c32417afeac
4d3ebe2e06c81a50d3c9ed9b92539ac3072ad33b  95f4a524f5175e9e399648500b52a37d2e544f89
e6c2aff5012389b739974e24072cc5ac29dccd07  34398da34f8822d19fb1e174098b994aa4511377
7d4b38b3f51baee43d5fc05962a3e157bc8aa980  af7bde529577af9d80a3f869afe05424b411318e
5497a2beccb22dbb0434cb34b25351e0674e1307  f2782e64c907d1337ee39f6b4683321f67cd4c3b
74c480c96443a7dddd5e5e4c7a9e06f873f68d35  3fc27a699ca1409528eaa12854c279cc1905c455
bf85a4fae7165acc4821699147be563c01f3fdef  b7417924a4eaf3c9bd782a9ba67785f40a07958c
c1dfa1eb3e9aa56a5b52a851e41cff2700ba43a3  9607e5096c36e6e40c9e7b67bf3eb189d4f5355d
fedb2c9ce7ba02516656ddd2a8e27322287adf7e  d1cc7f97ed832e39e728088148ed452692ce4292
6c7b7cd2bee897ccc36b1a7c8d180a32d6f92d1d  0ec2fc76a65146408fb19c2ee292852c95b79ae8
c73e3a37570c56a24e194b34f3e8424d2f49eb0c  c02af0b515c76184fed55a2099cc815f7b04d075
4c97f8f99a78588c3231d6423517070c88398982  e1c46fc6fa68480e129edc5407ed8890adaa6452
16ffe3f4c90a59f9098402f6d72b7bca30144dd4  dc6fb41f6d60ff6d07d39487e6b17ee36015f64b
9deb0419146571ea4386a407794bf4add6b6a714  e0a758921d5863cea5270f336667ea81634844b4
7e6c021fead2502a229a8dc853a5b53b5b067a11  b22ec8c23c691aec60af6a102802fb0fdd814293
cf4be19e38329c65d4cbbc363dbbf8aa1e97057a  9b860e10c992c7269b82ee77a5a6313d66c4ab72
f29517b6b2400891a7c26e17281fab31ac0f871e  188b12b36f09b38c392ec957f8016dfd2683c5ff
c15317c82651970aadfc0e486975803a296e736f  0d77007014230cf7ca052cad88ea83039d0fa7fa
0f5bfe0e92859654bd3d9ca2ac3b3a2abce02670  d2d81ea0e778eabe0d56c0c4f9705d97fbf91f0f
f80e2aba9d6ce8ccfff32cd62f56114bd87a4691  49ad73eeedc8621cb607bd09072e8e4c00367065
26561b3644278fe6f76fed725877d1d4861d8f5e  32f2a934e7035714a3f3229f03b50494ef996d30
a61ac62cddd34deb5c88dba219995e1d653beb07  51b149a4a11c8212d732c1a156ce0247bd3b1891
29702f9187679a119a15d9b40de5fac930d7b6c9  fc785a371192cb766e9dbeb1bf3d283e24cd990b
960e7e568ba17f973be86b6ebcb25e3ba6fd48a0  69b614e6c49d853c1fe5fee2d98e84d7301ba2d8
d5fae4fe144b13ee984bf03f9fe60385059bd6b6  27abff61d9735f562c528c9344963e9a8a594549
6ccac917103f33f9bd186e033f64d8f689e88ec9  7d1c5cb29ecb045c4d95d902fc91685d3bbcbcfd
a20214e8eff7685a860a9fd1728c2a146494ef7f  1918e6757f3344ef392438aac98546e1efcef6ca
eab5905b9765d3f10245e6def71ba274e829a608  c56785764e56acf63641b09c292849c9cfbf829e
082185edbf0322b29001ce99e5700a76f59787d8  2c4a00e088faead07127d8c94c7ff5020b155776
39bcc1fdefcfaa0e5289c192f72cd3b7d34bf40a  415f487443f58a08a8bd5352a0f6a81be483a9f8
4c940f76cda7c3fdb5f21b18f8c95e6c98bd232d  684f3a1b588b8aca49b204fc4f6627e7a0f50223
7a819c47915d8061b9536e6d93a7ace9128f686e  13a3e1f42773756c6aa52c828cc7cd344d6187a1
61dd1d6661e418a00817c9eb017f98a963ff7b4e  0cd060bb42d19d44c42c9330e316d39055346c4e
de43309ffd8c060d3371610f1cb466a1f7a55a1e  c3ef77a828432dd1174dad30bfe79973f8ddef83
c5810ca1d2f450d08dfb6985dc26d68f90cc4595  1b03730c785d4db4101e6bb86233303ec308e315
0b73aa13b532091ce79267cd04d087334e244a04  9f2e3aa7254b93581b33d2fe9b7d22fd243ce27c
c1e790923b4cc2cf9e9d5f1750c789304edcb6dd  f25c87747994d03e91adf29206ebea67593ec235
7c50bbae867c9d93df28e182843f7621b26bc0f1  f156aca3868633313db40a5ed4d2453429cebd5c
b8a4cd3bdf3ed5b1c241436d1280b85156ab82e0  8e0b690c1dd0f7361d0f2c05439ac7b55a7115a8
2991e04f9285c5c8c1f8f6e7b4b4390153e7cc1b  3e6b02a77bedf88c35c04b1d741eb21e9603c903
8a24beedceef170e272b242323d842e12ec523f4  4c91536e7d3922a8c5c0ac5a5fae7fa7a9093db4
c3a08693d3fc4fecc3407729525e216d89d9c76f  966dd38105a92da9a78dcefb70229dbabc47d147
e1f0d66feee0645501c34326f79922555826fefd  f279455d899b776a8643c268942e4f7c25a99dae
b24b8e9b9f5d0baa73c41a5f270b3175cbeacdd5  41086be75b467413e7633badbe37186b61a81053
1a9d4ac4a38ecce05f474d593201c5d30464af02  95258f020e54618dfe1704dfcb5d2ef6323bb4f9
114ce150e38e15e589e8b74c49eefbbe69556d13  f3793332ae3f902a1062c603cdb5af7b879de2df
59d99bf596de0b3819c138728c3950f35e342fd1  e31cbda57b521668c43471209871e57cdd48da55
d34d3f1015dff0d5883b17934d7f9b24ebaca16f  2e73122dcfc9515450edd2cb7db1f810289fe0b1
5b33934a004c640c838d7dd117412977e4a4ca5e  fa3170d8749c1aa215724b3a542950d084b8c84b
d2868fc75abec45dcba006c0debc068fa6d75182  358b1c46771cb9445884cfc0fff0acde46856e76
b029edd5a48e0c077d834d857c838cfe97f85201  6cc1bbe0926ec89e5c6176a3954a9e61faa10278
824262911461ad473ec9cd9e4d4d62b4699c1482  7d00d7e7d3250eb92923e44d87e004acbff65cd6
915cd9e966b16827a4180ab8a62a71b73bb43573  92250bbd5e6ec5d8b03615dea52b9d25a4229380
f2ecfee479d9c147b6a93eb8f2751b4eafda8786  5cf01fcf8db6397a46ddf2c689817ded9c935a21
4c108820c2462573cbe53e37425c1b401394a741  581720e94cf884f776725b7a2ab81a3038642344
163b009aacfcaf80df6eed118267e89ff1283779  0434d11ef2272c53c353d2b9b5ce7d59aed758e5
865a3d3a39ee5850ee96bcbe45b9611465d4a839  9a9b242bdd9e9ca04466cd95525b48728e9a07bc
50c19fe84fecce233d918e2a28ebf3d5861a1c0a  78cd19a6be550b8d165a700d1268422630c61f15
327bd2c57d669742585fa4eabaa405245ac03bf7  b912eb80e37906ffa787b7d67d9bdc3a134a05bc
5b23011bff2ca6734653b2bacbd97f5bd9d0a950  d287919ef588eaec69f92fae9f65ac1748abca5d
a7318893cb58cb81f2d6bdce2bc884710014b819  6156064bca1e2d216752a063663cf111c2e16d02
20793e6a649357bc97993227a665b280a991c111  3bd4aec393cc94778363c2d5e26c6764b5b4a1dc
0adbc9488e2b51187e58cc7affedff7dcf73eb11  e989c135dffd6ac858ae8bb622c597f2d49a4989
b12ed34526aff6f6f707098a1b2d7851106e4f60  0fdbac0eac7d78eef46b5f2535e0a46827ee0bc1
526af18bdb7dfcdf091824dd354957bef227916a  7db3f1e96aaa52c830fc75b955caccf8aa53efd2
e8e92f3e7e026d9d69dbe943212b02a24a514408  06b8ca4955a5c772f28ac1ef8dde09c62a510962
59dcd1e3d6dc69fd68077253b0a2857cca073baa  6bc2b6cd650b52c7cf19b7cdd5df5977a623d9be
f8eaa1901d736ae0689f2b350080b1b46423c20f  1a6960b6f3353052070c25a716ad5a213d60c1d7
d62c8d05ee335863cbe6997de46fa22c44110b66  cb120872f4622b1fe9f5f92afdf0ddbf6653ed0e
0f335473437d5c7e60d446aa660486aa539a90b1  4ad523c2830f7456343dac0b2f1df53052e6ebef
7c6d5f6e62ef4ddb1e62714d2e646bf74c1b30b8  c011d497766a5f0f7d1d4bc3d7c4e12824499078
07cbd08cf18bbd932ad2202b8bceccf88024c326  6cf94e3b7d47880da9f748178d939d1776209c7f
610fe25343d0c212140c7348ff625a6163306a0a  5aa252eed0f3f4f6e31f980ad122a15a91f1801d
6ddb5e639a01ff771ce77e293bb7e93ea2efe527  e0165292521c5b6c7c713b5ac7ea6a2b8e5ac2eb
67f30bcfceb75995fed99ab9bdc0b9ec63e692ac  5e7dbbfb83b81a869e1fb90ebbe562a79840ee50
43ac562a801d95c669c1bd92cb99b779a715d7bd  cd9858b7c71dd0803980e5040f93a724ad28b439
64fb3e71c82babf89a7fd4932af5450d2fc60327  9d14f3d81f52c76457ed628c7231d8c06d30c69b
e86582e21d9328de926979feb68e57f228e77d0b  3cca7e33685f82dd833dc86a7b4ae8fbddf24850
b640b01df01fa2580b89749a2fc231164caf2354  59981b7310cbd3658a8ec38cdbc6c7b7d0224ad6
b6d4aaa7a8654790b014f32d46f37516f1d498ff  a5f83400232da6bf8fa6010dc651dac38c7a9b36
83b1b10ebab23429f8cea398710b531fc3462d5e  97b6aa2517fc31c65b619be3a4236f0f4da8722f
439bd8b917725af1c8ea5daa78dff8554ac8b94e  beb0de32d7e36288cf5eb1a24371b1dc6fb604f4
f53b6e929c18a4b7a01ff3dc6c0dc68b2698a9e6  882ddbb14a1696a66713a756a0681d2264d12d3e
a57f0cef410894059036caec20dea9fbcd665057  ba6438ea81b1fb172b0d61aea3366f10189ecb0a
a06ed0e9b494a5d5f82df40cdc460299eeea214e  414638f922e011ab7db2e670b241710104b554a2
db89c3e23074e6da4a30881068d5beecf36bfac3  70580e2e7c23ab9e42b49a37038b794a0cba72b8
fa017565aff2f5d8f856d1291bc5c7eac3acf8f6  25fbb2e5c3adf892fd4dff765280f7ae60c2bc87
ea877675c8b106b5657f2286399d0444635efe81  612cf4c53b48737911d33430fd5b5318c802f0ef
b50bcf43a7b748c378ac20858557af4e970d19de  7552c4b86b1348fd64aad8448e74d6f3f197e39f
9d7f70157ae966d8b5fd55de91755fb038130d27  ad24092cb1066576ee8747852c58624438e9c4e6
d32aa796cd97ab15418f1dc53c5f95cb815aed2d  4e69bbfb78964f94c9f130b77d71d441f920da4e
2b247afc506c8ab1834729630567428457aa1d86  eca008b5231f49f1d9206581208ceed2af075196
5da1335516e808691281ee7201008d5d1f78d377  fe3a46b6a45f5dbcdf3b67c97666ee313aff02c8
d361ea44aa27ed43a90f3120bd6a1ceec4f62426  0f77e45db21ba0bc619763863c8800cf2cc99da7
cf6a387b4a2d4a8d9ff69709f8566485629609bc  8d22b9c2b047b4ada6e30daf0066e0411f4771b0
158241107f553ebbcb47015c003fc9b0752c8577  12a4cdb68180d6a859bb1a7b25a4396edc31bf3e
f31debc7ca81f442f668a382650ac6451a6f5217  792e1a1d89b24703191e79d0a4d1cbb23a575141
59684ab432ce52b09ebb4315e39b20484754ff03  bd2b05a841b320787dcb3f51de2af478a48fa3a3
595c601dc7b0a770553399d4f973bc1aea2ad21f  475b772bc2215359fa16746c6ee4f09228c99b49
6903cbabe4ca83bf27e29de63bdded469dd6f15f  480ccb7b0d9e4d0641827f5b270bc4c69e8bbc51
68b5484867e7e687f6a44371577aa5422fe2b443  6b0d3ecff7f2531b001394c1112e49cd3e5bcfb1
ec58982d01d5085d456fe5a2e2e4d887e7037dd6  7c53b2ede0919edee7c0ffc61d914e82efd66bf0
77fdaed173fd42e6a51d0132259f2c431ea96088  51567d9330213e84225ff0e53d32bed6e9f8e2da
dd09dd7d98c5ccb716ea9c3a140943e51002d577  f3e914cf6fe75b3e192894519d04d9c662a55446
bb25cb2c245ce625bae4dfe7286dd11c78349cc2  ecec8336586364818d918479461e5907cb16ace4
42856eeb74d04483910fc955d206d08761fbd037  2273055b736c2a7f1fbcc5cf3c827b1ce6dbbd26
8e05a7122889c9e89830516b50b8a455556bb21a  f5229060bf22186c511b9a12199a671aa32398f2
22f5376a7321d57ba35567afdb2d1b6587c88d88  c14afd967521bb52a46252df15df58222292410e
bc58c1a99c0a3255a5741e61f5457d6a685984f7  f2437c43a2dd0bdecfca62b968d2727d1a8c8fc9
c78ebab39da0bd0dfcad15b23525bfbc2b346b47  44bc69cb2527c92455ba43a1a9e90be3c176e776
88d56c65522261843c540fe60af2b359f9aba86c  e85a2228b9bb660c5ac7e1790ac4320f2411f334
a8d0e92b35796cb3ecb7ab9c977b0f907ac44a85  8b213ab9b77df68c0321f90db9ac4da9827f2ba8
e705dd4b18de834c402d9484d3e10cad378afe23  d67b5025b471064d5fcd6109ab193a2b6d757aa7
9fe18daf9a1b927096ed2c95fa24094a9c2f82cf  ca3888958b50a06b0b504fd9d434dd95f2cafb58
df2c564372e86af896bbe45867e7dbe2987d1dfa  8361dc5c45791659fe25e66feea761b8662676b3
82c8e7e3ab358f50ccb4799e741aee709af48af0  056e10e3f581473186d98189c431f6c7f4144e45
c2b0bdab5203389befcdc82d204accd79cef3fd6  996662a159947da6a17fce6372cb1f378a468f85
5c2d640910da4f08435196777dfb17152f885f27  3c8468cf5bbbc59ead02fecea1eeaabda5d818c8
952f1f2267844dce7e66ec1c7feb11e06bbf4fdd  6b6b5afea656d6181641c4d04bedb0713fa62df7
ae37fc06f558408fe7997a637c4db3394d70c13c  dc0f2322e1433c55c6efda6ed078a277739f9dfe
a8309ed1e9694c9efcc2cd2b81ee7fa23818f5f1  c6cb1d3b228c11ff61692d9c373213051473bbaf
8a6643eab02c511a475d33c9b1d0c7bfaa0d6aca  db5386950285b450e22a8d552bc01190e4aad0e3
e45a066ff40f87c01306b2f1d99804bdfa8775bb  9935a0ee70ff935c22ef40a6d1ed6481e7fd72e7
9041253e906a093c627c2d531d085db8599da6a3  68905426c24dbd7c5acbe3c1e886dd13602d3f8b
9cb01960729f806e8d55895d96ddacbdde5e828c  d90c76848912fb19f6166a941922e2a05424f243
c5fd73e0716ad67796cbf5f764d88058e52f24ee  cfd5dfef129589ea1646b619320172d3723830fc
3ceafdb43882c3e9ce73c4cfe8bcb14efc0fa97a  4e77a33eaa277750be5acfd500a31089c9df22fc
cb5ff9de392f1249fd75c69b08ef8025f820fbdd  e42dc5d030dc24f3ee751692b6ac2a7e62b64ddd
31b8475ebe7a53192926055b78817306cfe4d42d  d523f2f24ff2e2093970432a84ce67dd371c4f4c
f2ede0cada68158ecde1331efc5c4857fcaaba00  a0b2cfa40358eed396426cd54942d2c24fb4abec
28fb66b334a508a2408687c7ce1e774130dc00c7  9aec5db2d62dd4acbde4a2d7eaad11be000c038f
101419b6cef4a1db58c8e0d220225bccc9667caa  66b7fe87126d8db5556282b0c3ecf20e7cac6097
2ad4c794af565ff75fbdae77a5621c725fd7ca4f  af2946ec297e3b43201d0743dc9306601f76021f
66a96733e88ad5ee20735c4a5128f910f16d3e27  50a333c8885ea1c00c878da30ad21bbdb707c4e5
4ac5f3cd22e6ee3e6fc5f188a9ea7def520094e3  e6620c89c9cb216ef55c4360088da3a850b8c740
485ba64decfe25bff5b300b6d037002495258b2c  1b2a85e53d8d5afcf9a4ee239795ce6eb9cff942
b038161e6dfd534a4d96f6a018bd27993e8fc442  d19389149dbc3f6520e597888f0fe3d80182aaa0
19cfba09d39c2b9e374e65e5c8473cf93352bc31  1488ffc0b3eaaba6b75d1cf538a0fd216ed6d46c
342868ae9115713f95ac8b2360fc2936497c2c68  96f1dd9869f7ddf6fccd3d2f14c17ab029632ebb
4e7bd9bc0dc5ea23b02579a67272ec31f190fa42  de879675715a4577906b645369db0f18edd1ea1a
7df075540eca29968b88b33781b1ed9af185805b  91446e3ec2b0d3e8b3747f79bf98d6e53d597d1b
fd53101a487ba88434e2be11f3fc39b139d5e85c  bc067755dad95941c5ba37ad44465f7ea2a9fef1
b499ac35218c663c1926e6d5a4d210f00c7b5bcb  a53257347663d6af518aaa14f67e69698c0498da
8c3ad19d71129c014f34eb5fe5a064a0954a86fd  5a5796d5bebf59cc2cd76b661ecd4b5d85ef70e8
1a53df7a4ccc62df4a49ca44e6b788b651589811  02a0cf5188caf046f8289390701fe245655d2b49
596d74cf6d6e1b15bfac487881905b5d30af40f6  de65421a152637a0e4a575cd701ab772b58c0039
8e1f8f9eb0e899cda0b383e4c564626814df45a1  d7dfa93cc8af8fe0cfa0cf80697dc32007bc3b3e
c839f54523c14bda68b962c70f16753058b4da68  94cc961287c457c98c11e0ff945d1ae4f59a9ef3
7123b501be87eb9413d9c904d9cb921d7d1ce0b2  eec498f7446fc50b8a91aa85edbd83159d4e5f68
41d175f2cb447b91aabc60f5b75d944b661a7970  e5828877594f534b65cdb666ab1ab00ba847ca10
dba53eeea9e8b56637a47fdff9050dba4d03a1c7  c5ed716afd2ac577a4587c8efcc9031bfe7870e8
219c8a5fbe3339322b3f895c63e13dd95e3212ff  ad04da23b4c87f3e59beedd5e461dfd16533f0a2
5e2a669abf4f24f36719a1a1e52a00f0f531f735  bd224c54b76f0f8719480786748dff5d0489b3da
bab2efbec1dfce136c1f61247c3966b965850c40  74169a55b2e66a07c07186ba92454f3a8d295697
671e5c80fa8b8bf418673345702fde06edbc4006  7cf134f486792eb92fed6265180149ab5f843bc9
eccf722718bdf34df04b31336c14fc063b8e1716  7e5711a2325e2076a7fca9d7cf956b6a5b85d1ff
90a5a5eb66577b3a45a63582536c29542d75f724  172e25f03a984d4ecd45f0d26e1543925422abc7
f4ca8a35ccc6edf93eda18cd3f179333b8c43f92  4d39bdf383d589cc205d565cbc43a8b16eb01f2c
d90bed9d2d72856bbdffd065e27dfaa503aea6d2  35b20cb85a3b71db064ac7c724e5e4a8e2f9409d
abf944b01383c4935723fcdc382b9166a62a2bb6  61d50bc29fa25f8e74877f5e3dfe269e45474a16
d5002f2b9b676b80e0fa986b36132c29c2e434e4  9d7d632e058a4bd59bd546f4f4728921bcc39d5d
3abe3521da3cd24fb0e6c040e64bb4cc291fec0b  d1e8c3abac005e5f864af93e4844224567334f9a
2725d562c7c8e73c73dfa87150334d1f280fd03a  d6129540e9d75b7b797e0ecdf7df5bfe53dbdd18
dfe3ab8cee617ca99d1ffd8c5d8361edc9cc0026  871d4291598625f4685c1eae8f4f16dccc9d1119
586338324fc942a31d01b997dd8a86083d7143b1  b1a8850330aa32ff8c455a78fb96aaaec2bc1c52
e64d3728dea99d0e81f90439a81d6d26b8869df2  46d0e83c85e4934d43c07de3b28c46557aeb5238
cbc9ed26621ee0ade6b3cc4a77d7325743834d71  3a504f6c5be51b891861c880f280ff160e910711
67549008e50ae7894676b7f851cd65a3df347236  fb172d40252eb04ed62bf1c4e5455880e2d9b441
ce15efd9fa81151091ce0f7beafe2c2f55dc4a37  991c3b9c7e04512dbdaff48a773e68e5d75b5d92
e08c9780debbac40087c95a54295446133c6f5c8  94ba7324eb1855f966ff5be8a3e5a3a49f352da3
2da17c7dd8794bb8f06b69304519e123d9e12f7a  95b0fefc7e4d672d00ab84dac3f41e3a357c6278
dcb41e7f4988777fc1bde1cb1fbd6b4a511ea12a  58f71ac83d1c4d9bb7f4d0576e286584f82de625
c2409eacf99d4a37ca302d5a3809fabe12ddf782  086798bce3910acc318db845dea675271e2b3ae8
c253b51a63b0bebee856bcfb0711cd73b622e5a3  e273bfc627f833aefc325176872bab4a81877cf9
ad2455cb0925080e3b5a1d9c9c5b35ba8a215800  909e7b9399442a732b06d68b4558af927ed647e7
bc8f20658dbc3ad17043add5e246a1f32f13ae89  91668fba0fa0fe230358edf916fc5cc1639f7da8
048a69787a5e57883dd45416c1fd7342a382643c  aae3a0f8e99655c4b4cf042189e9369657a3a3e6
ed3a7c3706f0e24b777f8236d6f06b2769704aef  f01a5894660a6ddaf8cb341ff20647a82332031d
b2f019e3537b47dc1af7b46022d60b401770b17d  cf97aadc873687aa6c4a710abeeef9d4241e068b
bd2e0ded11911154bae27356d3d22073f56f4ff4  b244e99618bed037710b9e4b149e0ebb278a9dd5
d0d358fc8acac496fdcb6dd7751ec7cd0dc5dedc  388d2b3983fe12e95f30965b6591a2d6b665bcd7
14300d2efbdd512b41ab0132de4859a3e2a62b05  2346379be64aa0477febff1a9be892ae73705b83
e14f17e3e1bfa8c6e5b357b80f10d0ced51ace4b  4547ff980098b04b4e53d272bf3d9aaab4359dfc
3bc89948e0f69a604febe13752d5d89d5f060982  7388bb974c97f99d0de33f3244036e7c697b3afd
f7331a08f2e03aa6b52e5b8b99f18a5d11a4e181  8a8509c26df7b12a39d1a275619f93bfffac0475
1730a2a5afd69c393abf8f1f8c39c39f3ccf7648  3985ea9ce751521b07b1af10f38b7b64c0bafbf1
```
