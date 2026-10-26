# GITHUB RELEASE PREDICTIONS — **THE WITHDRAWN GREEK IS PREDICTED IN THE CURRENT
# TREE, NOT ONLY IN ITS HISTORY, AND THE REPOSITORY WILL NOT SAY "MIT".**
#
# **Written 2026-10-26, before any rights target was opened, any history was
# searched, or any file was edited. RULING 78: committed first, scored at the
# close in `GITHUB_RELEASE_RESULT.md`, and not amended there.**

---

# 0. THE STATE THIS IS PREDICTED AGAINST

Read over the bridge on 2026-10-26, with read-only git and no optional locks.

```
HEAD                 e14f17e on master, 275 commits from 9470506 (2026-08-12)
remote               none
tree                 clean, apart from five untracked handoff and start documents
tracked files        1,115, of which 148 are Markdown documents at the root
ui/data.js           9,819,314 B   sha256 bd24c61cf5fd…8f0c89784628dcb6dd3
ui/index.html        426,323 B     sha256 45a70753ce83…1f6f876031ebab
eval/answer_runs/    685 files
harness              65 ok at e14f17e (node ui/check_ui.mjs, run by Rob on
                     2026-10-23); check_chain.mjs: chain intact;
                     test_build_ui_data.py: 23 passed
next free            RULING 101 · FINDING 126
```

**`github-release-start.md`'s "Where things stand" reproduces.** HEAD, the commit
count, the tracked-file count, the 148 root documents, the absent remote, and
the five untracked files all match. Nothing moved between 2026-10-23 and today.

**The rights column, recomputed from `data/corpus_rights.json`:**

```
open_licence_stated           18   CC BY-SA 4.0 x10 (three stated in Greek),
                                   CC BY 4.0 x2, CC BY 3.0 x2, CC BY-NC x2,
                                   CC0 x1, GFDL with no version named x1
all_rights_reserved           15
states_no_terms                8
permission_stated_no_licence   6   eastasia-04, eastasia-08, scandinavia-06,
                                   scandinavia-07, seasia-07, southasia-01
public_domain                  4   africa-04 and africa-05 (OGIS, RULING 98),
                                   africa-07, southasia-06
two_positions_stated           3   eastasia-09, persia-06, seasia-09 (UNESCO:
                                   CC BY-SA 3.0 IGO, stated for "© UNESCO"
                                   content)
                              --
                              54   read_by: curator_and_model 39, model 10,
                                   curator 5
```

## What was NOT looked at before writing, so that what follows is a forecast

- the verbatim wording of any of the six permissions, or of any rights target
- the content of any commit or blob, and any `packhum` hit. Nothing in the
  history was searched
- `check_ui.mjs` at lines 385 and 886, and which files any harness script reads
- `.env.example`, and any search for keys, for Rob's email address, or for
  `C:\Users\chemi`
- `DEPLOY_COLLATION.md`, `F4_CANDIDATES.md`, `F4_RESULT.md`, and the archived
  answers

---

# 1. DECISIONS TAKEN 2026-10-26, BEFORE THIS WAS WRITTEN

```
D1  history: rewritten in a separate sibling clone with       recommended, taken.
    git filter-repo, with an old-to-new commit map in docs/.   Provisional: Rob
    The working repo is never rewritten in place               confirms it again
                                                               against step 3
D2  Rob's commit email mapped to his GitHub noreply address    recommended, taken
    in the same rewrite, and the new working repo commits
    as that address from then on
D3  licenses: MIT for code, CC BY 4.0 for Rob's documents,     recommended, taken
    no license over the corpus or anything that quotes it      WITH ROB'S
                                                               AMENDMENT:
                                                               RULING 101
D4  the root's process documents move to docs/ as pure         recommended, taken
    renames in one commit, with docs/README.md as the index
D5  docs/origins/: the brief (_Rev.docx is the final           recommended, taken
    version), the Part 1 setup walkthrough, and the Phase 1
    Getting-Started Guide (read first for anything
    personal). docs/: the three site-thread handoffs and
    github-release-start.md. case-study-start.md stays out:
    it is portfolio positioning, and the case study is
    unpublished
D6  curator notes in data.js left as they are, with one        recommended, taken
    README line saying so
D7  ui/build_banner.mjs and ui/banner/ removed in their own    recommended, taken
    commit, only if check_ui.mjs:886 does not need them
D8  the four "project repository" mentions in Methodology      recommended, taken
    §10 become links, after the push
    the repository: productofrob/mundus-ulterior, public,      recommended, taken
    issues on, default branch master
```

**D3's amendment is a ruling, not a preference.** Rob: *"I don't want the whole
repo to say 'MIT' because it's not true."* The recommendation had accepted
GitHub's sidebar reading "MIT" as the price of license detection. **RULING 101**
(`GITHUB_RELEASE_RULINGS.md`) holds the repository's own label to the same
standard as the rights column: it states what is true of each part, and no
one-word label may say otherwise. It also carries Rob's disclaimer and a contact
for rights holders. **It changes one line of the start document's done-when:**
"GitHub detects the license" becomes "GitHub's sidebar names no single license
for the repository, and links `LICENSE.md`."

**Open at writing:** where rights holders contact Rob, and the noreply address
D2 maps to.

## The order of work these decisions produce

```
1  this document and GITHUB_RELEASE_RULINGS.md, committed
2  the redistribution pass over 54 cells, readings proposed and confirmed by
   Rob, recorded in GITHUB_RELEASE_READINGS.md beside the portal's cells.
   data/corpus_rights.json is not edited. RULINGS.md indexes 101 in the
   same commit
3  the history scan from 9470506, and Rob confirms D1 against it
4  the rewrite, in a new sibling folder, run by Rob on the host
5  in the new clone, each its own commit: the docs/ move, the D5 documents,
   RULING 101's files, the README, DATA_RIGHTS.md, CITATION.cff, then D7
6  checks on the new clone: secrets, personal data, harness, fresh clone
7  push, repository settings, and the browser check
8  D8, its deploy, and the result document
```

---

# 2. THE PREDICTIONS

## P1 — the redistribution pass

The repository is a different publication from the portal: a copy anyone can
download whole, from a page that invites them to build on it. Each cell is read
for the repository as one of three:

```
SAME          the repository carries the text on exactly the portal's reading
OWES MORE     it carries the text, but owes something the record does not
              already supply: a license text shipped with it, a notice outside
              the record, or a restriction DATA_RIGHTS.md must state
CANNOT CARRY  stated terms that a public repository does not satisfy
```

**Predicted:**

```
                         cells    SAME   OWES MORE   CANNOT CARRY
open_licence_stated        18      15        3             0
all_rights_reserved        15      15        0             0
states_no_terms             8       8        0             0
permission_stated           6       4        2             0
public_domain               4       4        0             0
two_positions_stated        3       3        0             0
                          ---     ---       ---           ---
                           54      49        5             0
```

**Named calls.**

- **The GFDL cell OWES MORE.** The GFDL requires its license text to travel with
  every copy, which is something a repository can ship and the portal's reading
  did not ask for.
- **The two non-commercial cells OWE MORE.** A portal reader cannot take the
  text away, so nothing needed to say "not for commercial reuse." A repository
  reader can, so `DATA_RIGHTS.md` must say it.
- **The ten share-alike cells are SAME.** Each record already states its license
  verbatim, and the repository adds no license over it.
- **Two of the six permissions are worded for display, or for the granting
  site's own content,** and owe a statement that the permission is the source's
  and does not pass to anyone who clones the repository.

**The aggregate claim, which is the one the start document hopes for:** for
every cell, the repository's exposure in the current tree is the portal's,
because `ui/data.js` already publishes every record's text. **Predicted true. The
pass moves 5 cells, all to OWES MORE, and none out of the tree.**

## P2 — the history scan

**The withdrawn text is predicted in the current tree, not only in its
history.** RULING 98 says the restricted source "stays in the note as a
cross-reference … and nothing is quoted from it." The documents that did the
work quote it:

```
DEPLOY_COLLATION.md       carries PHI's africa-05 Greek, at least the characters
                          where it differs from OGIS (Wolska-Conus's readings)
the F4 documents of       at least one of F4_CANDIDATES.md and F4_RESULT.md
2026-08-31                carries the Greek as first pasted
eval/answer_runs/         at least one archived quotation lands on africa-05's
                          PHI Greek in characters OGIS does not print. ui/data.js
                          carries the archived answers, so the live site
                          carries it too
```

**In the history, between `03e430f` (2026-08-31) and `c2409ea` (2026-09-23):**

```
record blobs (africa-04, africa-05)        4 - 10
ui/data.js blobs                          15 - 35
archived-answer files                      1 - 15
Markdown documents                         2 - 6
commits touching any of the above         25 - 60
```

**africa-04 (Silko) contributes withdrawn text only in its citation and notes.**
OGIS 201 and PHI print the same letters (`DEPLOY_PREDICTIONS.md` P5), so its
Greek is OGIS's whichever page it was copied from. **africa-05 is the case that
matters.**

**The `packhum` hits in `9470506` are URLs, not text.** Predicted: no record in
the original 24 took its source-language text from PHI.

## P3 — the rewrite

```
commits in = commits out         no commit pruned. Every author and committer
                                 date is preserved
Rob's address                    remapped on every commit that carries it, as
                                 author or committer. Claude's 56 commits keep
                                 noreply@anthropic.com
hashes in commit messages        rewritten by filter-repo to the new hashes
hashes in file contents          left as they are. At least 100 distinct hashes
                                 are cited in the tree, and every one resolves
                                 through the commit map in docs/
check_chain.mjs                  still "chain intact". It checks the evidence
                                 chain, not git
```

## P4 — the move, the banner, and the harness

```
the docs/ move                  148 renames, every one at 100% similarity, and no
                                other change. Harness 65 ok before and after
root entries on GitHub          25 or fewer before the README
D7: check_ui.mjs:886            a mention of a retired check, not a read of
                                build_banner.mjs. The removal goes ahead and the
                                harness stays at 65
ui/data.js                      the same bytes at the close as today
                                (bd24c61cf5fd…). Nothing in this thread rebuilds
                                it
```

## P5 — the checks

```
secrets, full history           0 live keys. At least one placeholder that
                                matches a key pattern, in .env.example
Rob's email in tracked files    0 in the current tree. It lives in commit
                                metadata, and in github-release-start.md, which
                                is redacted as it is added to docs/
C:\Users\chemi                  in 25 - 60 tracked files, all of them runbooks,
                                start documents, and results with cd lines.
                                0 in ui/data.js
fresh clone, no ignored files   ui/index.html opens from file:// with 0 console
                                errors, and node ui/check_ui.mjs reports 65 ok
```

## P6 — GitHub

```
sidebar license                 "View license", linking LICENSE.md. Not "MIT",
                                and not a list of licenses
README                          renders, and every relative link in it resolves
tracked files                   GitHub's count equals git ls-files at the pushed
                                commit
```

## P7 — WRITTEN NOT TO FLATTER THE BLOCK

**The rewrite is not a history-only fix.** If P2 holds, removing the withdrawn
text changes current documents and at least one archived answer, and `ui/data.js`
on the live site carries the same characters. **Predicted: this thread finds a
live-site defect under RULING 98, declares it as a finding here, and needs a
ruling from Rob on what an archived quotation of withdrawn text becomes.** The
deploy block did not take that ruling, because it re-sourced the records and did
not look at what had already quoted them. Neither option is free. Editing an
archived answer changes a scoring denominator, and leaving it breaks RULING 98.
Any change to the live site that follows is listed for Rob and not made here,
since D8 is this thread's only site change.

**And this thread runs to at least two parts.** Fifty-four readings that Rob
confirms one by one, a history scan, a rewrite he runs on the host, a front door,
four checks, and a push do not fit in one.

---

# 3. WHAT WOULD MAKE THIS DOCUMENT WRONG IN A WAY WORTH KNOWING

- **P2 fails in the flattering direction** if the collation and the F4 documents
  quote only OGIS, and no archived answer touched africa-05's Greek. The start
  document was then right that only the history needs the rewrite.
- **P2 fails interestingly** if `packhum` in the first commit is text and not a
  link. A third record would then have carried PHI text through the deploy, and
  RULING 98's sweep would have gone by record name rather than by source.
- **P3 or P4 fails interestingly** if any guard reads git, such as a commit hash
  in `data.manifest.json` checked against HEAD. The rewrite would then break the
  harness on a clean tree.
- **P6 fails** if GitHub's detector reads `LICENSES/MIT.txt` and labels the
  repository "MIT" anyway. RULING 101 would then need the license texts somewhere
  the detector does not look.
