# GITHUB RELEASE RESULT — **THE REPOSITORY IS PUBLIC, AND WHAT IT WITHDREW WAS
# SIX CHARACTERS FROM A PUBLIC-DOMAIN EDITION. THE HEADLINE PREDICTION WAS HALF
# RIGHT, AND THE HALF IT GOT WRONG IS THE LIVE SITE.**
#
# **Written 2026-10-26, at the close. Scored against
# `GITHUB_RELEASE_PREDICTIONS.md` as committed in `7388bb9` (old `3bc8994`),
# NOT AMENDED (RULING 78).**

---

# 0. WHAT IS TRUE AT THE CLOSE

```
repository          https://github.com/productofrob/mundus-ulterior, public
                    pushed by Rob, master at 4d849af; 284 commits; 1,126 files
                    on GitHub and in git ls-files, equal. About: the
                    description, https://mundus-ulterior.pages.dev/, and eight
                    topics; issues on
working repository  the rewritten clone, now at the old path
                    ...\Museums Project Number 1\mundus-ulterior; git
                    user.email is Rob's noreply address. The original is kept,
                    unrewritten, as mundus-ulterior-prerelease
history             rewritten once (D1, D2, RULING 102): 278 commits in, 278
                    out, every date and name unchanged; Rob's address now
                    10733157+productofrob@users.noreply.github.com on every
                    one of his commits; the full copies of the withdrawn Greek replaced by
                    notices in 23 blobs. docs/COMMIT_MAP.md maps old to new
licenses            RULING 101: no single license. GitHub reads LICENSE.md,
                    finds none (NOASSERTION), and labels the sidebar "License"
                    and not "MIT". "Cite this repository" reads CITATION.cff
harness             65 ok, chain intact, test_build_ui_data.py 23 passed, at
                    every step of this thread, on the host and on a fresh
                    clone with no ignored file present
ui/data.js          bd24c61cf5fd…dcb6dd3, byte for byte the same as this
                    morning. Nothing in this thread moved the live site
```

## The commits

```
old       new       what
3bc8994   7388bb9   predictions and RULING 101, before anything changed
f7331a0   8a8509c   the redistribution pass: 54 cells read, 5 owe more
1730a2a   3985ea9   the history scan, and RULING 102
          ---------- the rewrite, the folder swap (above here, old hashes)
          50cb345   151 documents to docs/, every one a 100% rename
          bbf3724   docs/ index, commit map, origins, post-launch handoffs
          715fe70   LICENSE.md, LICENSES/, DATA_RIGHTS.md, CITATION.cff
          253214e   the August README to docs/PHASE1_README.md, 100% rename
          a957912   the release README
          4d849af   the retired banner builder and images leave the tree (R7)
```

## Rob's decisions, in the order taken

```
D1-D8                  all as recommended, except R3, amended into RULING 101;
                       D1 confirmed against the scan as RULING 102 (full copies
                       out, phrases stay)
noreply address        10733157+productofrob@users.noreply.github.com, read off
                       his GitHub email settings
rights contact         rob@productofrob.com (productofrob.com has no contact
                       page)
D8 HELD                "Do not do anything else on the Mundus Ulterior page
                       until I tell you." The site will get a new banner after
                       the release, linking the repository, the case study, and
                       the contact address
the 54 readings        all confirmed, and the Tamil title of the Madurai header
                       checked against the page
C:\Users\chemi paths   kept as they are: 42 files (30 documents with cd lines,
                       12 archived runs that record each answer file's path),
                       none of them in data.js
the README             approved as written
```

---

# 1. THE PREDICTIONS, SCORED

## P1 — the redistribution pass. **TOTALS RIGHT, COMPOSITION WRONG.**

```
                         predicted SAME / MORE / CANNOT    actual
open_licence_stated          15 / 3 / 0                   17 / 1 / 0
all_rights_reserved          15 / 0 / 0                   15 / 0 / 0
states_no_terms               8 / 0 / 0                    8 / 0 / 0
permission_stated             4 / 2 / 0                    2 / 4 / 0
public_domain                 4 / 0 / 0                    4 / 0 / 0
two_positions_stated          3 / 0 / 0                    3 / 0 / 0
                             49 / 5 / 0                   49 / 5 / 0
```

**The 49/5/0 is right by two errors that cancel.** The two non-commercial
cells were predicted to OWE MORE, and they are SAME: each record states its
non-commercial term verbatim, and the repository grants nothing over it. The
two "header intact" permissions (CBETA, Project Madurai) were not foreseen,
and they OWE MORE. **The named calls:** GFDL owes more, RIGHT; the ten
share-alike cells are SAME, RIGHT; two permissions worded for display owe more,
RIGHT (the Swedish Heritage Board's "on web pages", both records). **The
aggregate claim**, that the repository's exposure in the current tree is the
portal's, is RIGHT, and it was measured rather than assumed: all 54 records'
quoted fields are in `ui/data.js` verbatim, and the record files add only
citation and rights prose.

## P2 — the history scan. **THE HEADLINE IS HALF RIGHT.**

- **"The withdrawn text is in the current tree, not only in its history":**
  RIGHT. `DEPLOY_COLLATION.md` printed both PHI texts in full, one word per line,
  which is more than the predicted "at least the characters where it differs."
- **The F4 documents:** PARTLY. `F4_RULINGS.md` holds seven words of Adulis as
  copied from PHI's page, and `F4_CANDIDATES.md` holds five words of a different
  inscription on PHI's reading. Neither holds "the Greek as first pasted."
- **"At least one archived quotation lands on africa-05's PHI Greek… so the live
  site carries it too":** WRONG. No archived answer ever quoted a PHI-specific
  character. Today's `data.js` and the live site carry none.

```
                          predicted     actual
record blobs              4 - 10          4      RIGHT
ui/data.js blobs          15 - 35        17      RIGHT
archived-answer files     1 - 15          0      WRONG
Markdown documents        2 - 6           5      RIGHT
commits touching them     25 - 60        24      WRONG, by one
```

**"africa-04 contributes withdrawn text only in its citation and notes":**
WRONG in its conclusion. Its letters are OGIS's, as predicted, but its excerpt
still differed by a capital, a comma, and an accent, and both of its record
versions were full copies. **"africa-05 is the case that matters":** WRONG in
scale. RULING 98 expected Wolska-Conus's text to differ from OGIS, and in this
excerpt it differs by two commas and one ρ. **The two cases are the same size:
three characters each.** **`packhum` in the first commit is a URL, not text:**
RIGHT. It is `persia-01-skz`'s tertiary citation.

## P3 — the rewrite. **RIGHT.**

Commits in equal commits out, with every date preserved; Rob's address remapped
on every commit and Claude's 56 unchanged; abbreviated hashes in commit messages
rewritten (`c2409ea`: two mentions before, none after); `check_chain.mjs` still
"chain intact". **At least 100 distinct old hashes cited in the tree, every one
resolving through the map:** RIGHT, 138, none unresolved.

## P4 — the move, the banner, and the harness. **RIGHT, WITH ONE COUNT OFF.**

The `docs/` move was 151 renames, not 148, every one at 100% and nothing else.
The 148 counted at the start included `README.md`, which stayed at the root, and
this thread added its own four documents before the move. Harness 65 ok before
and after. **Root entries on GitHub: 20** (predicted 25 or fewer). **D7:** line
886 is a comment naming the banner's two-place declaration as a pattern, not a
read. The removal went ahead, and the harness stayed at 65. **`ui/data.js`
unchanged at the close:** RIGHT.

## P5 — the checks. **RIGHT, WITH ONE CLASS WRONG.**

**Secrets:** no live key in any of the 284 commits, and `.env` never committed.
The placeholders are where expected: `.env.example`, the Part 1 walkthrough,
and the `sk-local-dev` gateway default in three scripts. **Rob's address:** none
in the tree, and after D2 none in the commit metadata either. The two mentions
in `github-release-start.md` were redacted as it entered `docs/`.
**`C:\Users\chemi`:** 42 files, inside the predicted 25 to 60, and none in
`data.js`. **"All of them runbooks, start documents, and results with cd
lines":** WRONG. Twelve are archived evaluation runs whose `archived` field
records each answer file's absolute path. **Fresh clone, no ignored files:**
`git status --ignored` printed nothing, the harness gave 65 ok, the chain was
intact, the test script gave 23 passed with plain Python and no virtual
environment, and the page opened and worked (Rob's check). Console errors were
not measured on the host.

## P6 — GitHub. **RIGHT IN SUBSTANCE, WRONG IN ONE WORD.**

GitHub's license API returns `NOASSERTION` for `LICENSE.md`. The sidebar names no
license and links `LICENSE.md`, but it reads **"License"**, not the predicted
"View license". It is not "MIT", and it is not a list. **The README renders,
and every relative link resolves:** 198 relative links checked across the
README, `LICENSE.md`, `DATA_RIGHTS.md`, and the `docs/` index. **The file count
matches:** 1,126.

## P7 — WRITTEN NOT TO FLATTER THE BLOCK. **BOTH WRONG.**

**"This thread finds a live-site defect under RULING 98":** WRONG. No archived
answer quoted the withdrawn characters, so nothing on the live site carries
them. The thread did find a live-site gap, FINDING 126 (the GFDL text the site
links and does not reproduce), and did need a new ruling, RULING 102. Neither
was the one predicted, and the prediction takes no credit for them. **"At least
two parts":** WRONG. The thread closed in one, in a single day.

## Section 3's named failure modes

- **P2 failing in the flattering direction** happened in half: no answer
  touched the Greek, but the collation sheet carried it in the current tree.
- **`packhum` turning out to be text,** a guard reading git, and GitHub labelling
  the repository "MIT" all did not happen.

---

# 2. WHAT THE THREAD LEARNED

**A rights position says what may be done with a text, and a license can also
say what every copy must carry.** The column was built to answer the first
question. The GFDL, CBETA's "with this header intact", and Project Madurai's
"header page kept intact" are the second kind, and only a repository, which is
copied whole, made them visible. FINDING 126 is the one that also reaches the
site.

**Measure the size of the thing before ruling on how to remove it.** RULING 98
was written expecting the restricted edition to differ materially from the
public-domain one. Measured, the difference was six characters in two excerpts.
RULING 102 still removed the full copies, because the terms are the terms, but
it was decided knowing that, and it left the phrases.

**A prediction can land on the right total for the wrong reasons.** P1's 49/5/0
is exact, and two of its cell-level calls are wrong in opposite directions. The
scoring above keeps the two apart.

---

# 3. OPEN, AND WHERE EACH ONE GOES

```
the new site banner       Rob's, after this release: links to the repository,
                          the case study, and rob@productofrob.com
D8                        the four "project repository" mentions in Methodology
                          §10 become links. HELD, with the banner
FINDING 126, site half    reproduce or attach the GFDL text for arabia-08 on the
                          site. HELD, with the banner
the case study            its own thread, from case-study-start.md, which stays
                          out of the repository (excluded locally). The repo URL
                          it waited for is now real
release_rewrite.py        in the folder above the repository. NEVER COMMIT IT:
                          it holds the withdrawn strings as byte escapes
github-release-start.original.md
                          the unredacted start document, in the folder above
mundus-ulterior-prerelease  the original repository, kept and never rewritten.
                          Its hashes are the "old" column of COMMIT_MAP.md
mu-fresh                  the fresh-clone test copy in Rob's temp folder, safe
                          to delete
Docker                    mundus-db restarts on its own when Docker Desktop
                          next runs. Its folder path is unchanged
```
