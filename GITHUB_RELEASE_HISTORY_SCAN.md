# GITHUB RELEASE HISTORY SCAN — **THE WITHDRAWN GREEK IS SIX CHARACTERS AWAY
# FROM THE PUBLIC-DOMAIN EDITION. IT IS IN 26 BLOBS, AND NOT IN ANY ANSWER.**
#
# **Step 3 of `GITHUB_RELEASE_PREDICTIONS.md`, run 2026-10-26 on a bare clone
# outside Rob's folders, read-only, at `f7331a0`: 277 commits and 1,996 blobs.
# Rob confirmed D1 against it the same day, choosing RULING 102.**

This document quotes none of the withdrawn text. Where it describes a
difference, it names the character and its place, as the collation sheet does.

---

# 1. WHAT WAS LOOKED FOR

```
THE PHI-COPIED GREEK    the africa-04 (Silko) and africa-05 (Adulis) excerpts as
                        committed from 2026-08-31 until c2409ea replaced them on
                        2026-09-23. The probes were the windows 10 characters
                        either side of each place where PHI's text differs from
                        OGIS's, so a hit means PHI's copy and not the ancient
                        text. Each probe was searched as raw UTF-8, NFC, NFD, and
                        \u-escaped JSON, in every blob in the history
packhum                 every occurrence, in every blob
SOURCE TEXT THAT NO     in every tracked .md file: runs of 12 or more non-Latin
RECORD CARRIES          letters not found in any version of any record, and
                        quoted passages of 220 characters or more that do not
                        match record text
```

# 2. HOW FAR PHI'S TEXT IS FROM OGIS

```
africa-05  Adulis   PHI 479 characters, OGIS 478. PHI has two commas OGIS does
                    not print, and lacks one ρ that OGIS prints. Every other
                    character is the same
africa-04  Silko    PHI 150 characters, OGIS 151. PHI starts with a lower-case
                    epsilon where OGIS has a capital, has no comma after the
                    eighth word where OGIS has one, and has one ε unaccented
                    where OGIS accents it. Letters identical
```

**Six characters in all.** PHI prints Adulis from Wolska-Conus's edition, and
RULING 98 expected it to differ from OGIS by more. In this excerpt it does not.

# 3. WHERE IT IS

**Full copies, 23 blobs:**

```
data/seed_corpus/subsaharan_africa/adulis-throne.json   2 versions   03e430f (2026-08-31), f8eaa19
data/seed_corpus/subsaharan_africa/silko-talmis.json    2 versions   58c6b77 (2026-08-31), f8eaa19
ui/data.js                                             17 versions   every bundle built before c2409ea
DEPLOY_COLLATION.md                                     2 versions   c2409ea and dcb41e7 (2026-09-23),
                                                                     and so the CURRENT file. Both
                                                                     texts in full, one word per line,
                                                                     laid out for Rob to check against
                                                                     the printed page
```

**Short phrases, 3 to 7 words:**

```
F5_RESULT.md, F5_RULINGS.md   Silko's opening words, in FINDING 68
ui/banner/manifest.json       the old banner's Greek specimen, 4 words
F4_RULINGS.md                 7 words of Adulis as copied from PHI's page, with its
                              lacuna mark, in a finding about fetch corruption whose
                              subject is those characters
F4_CANDIDATES.md              5 words of the Sembrouthes inscription "on PHI's
                              reading", a candidate that was never taken
commit 4c97f8f's message      Silko's first seven words (FINDING 68's addendum)
```

The probes found the first three. The last three hold words where PHI and OGIS
do not differ, so the windows could not see them, and they were found by
reading every non-Latin run in the documents (§5).

**24 commits add, change, or remove a blob above, all between 2026-08-31 and
2026-09-23.**

**NOT FOUND in any archived answer under `eval/`, in today's `ui/data.js`, or on
the live site.** No answer ever quoted the PHI-specific characters. The live
site has served OGIS's text since the deploy.

# 4. `packhum`

**Every occurrence is a URL, a reference, or rights prose,** such as the
readings that quote PHI's site gate. The first commit's occurrence is
`persia-01-skz`'s `tertiary_citation`, a link to PHI's Greek version of the
inscription. That record's text is the Middle Persian and Parthian, and the
three Greek-block characters in it are the γ of Middle Persian transcription.
**No record took text from PHI apart from africa-04 and africa-05.**

# 5. SOURCE TEXT IN THE DOCUMENTS THAT NO RECORD CARRIES

```
non-Latin runs of 12+ letters in the 148 tracked .md files    62
  not found in any version of any record                      42, in 15 files
quoted passages of 220+ characters not matching record text  112
```

**Every one of the 42 runs is 60 characters or fewer.** They are terms-of-use
wording (the el.wikisource, parsigdatabase, and zh.wikipedia footers), site
interface text (Thai museum labels, a Wikisource notice), rendering-test strings,
and lines of public-domain ancient texts: the Periplus, the Hou Hanshu, the
Weilüe, the Jiu Tangshu, and the Akananuru. **Every one of the 112 passages is
the project quoting itself,** a source's terms of use, a model's answer, or
Rob's words. **No document carries a substantial passage of an in-copyright
work.**

# 6. THE RULING, AND THE DRY RUN

**Rob chose to remove the full copies and keep the phrases: RULING 102**
(`GITHUB_RELEASE_RULINGS.md`). The rewrite and D2's address mapping run as one
`git filter-repo` pass in the public clone, by `release_rewrite.py`. **That
script lives in the folder above the repository and is never committed,**
because it holds the withdrawn strings as byte escapes in order to find them.

**Dry run, 2026-10-26, on a scratch clone at `f7331a0`:**

```
commits                    277 in, 277 out. Every author date, committer date, and
                           name identical, commit for commit
identities                 Rob's 221 author and 221 committer entries now
                           10733157+productofrob@users.noreply.github.com;
                           Claude's 56 unchanged
replacements               42 in 23 distinct blobs: each Greek excerpt in 19
                           blobs (its 2 record versions and the 17 data.js
                           versions), each collation word list in 2
today's tree               ONE file differs: DEPLOY_COLLATION.md, whose two word
                           lists are now notices
PHI-specific text left     only the three short-phrase blobs in §3, as the ruling
                           says
hashes in commit messages  rewritten by filter-repo: "c2409ea" appears twice in the
                           old messages and 0 times in the new ones
commit map                 one line per commit, old and new, in
                           .git/filter-repo/commit-map
```

**What it costs, named:** the 23 rewritten blobs no longer reproduce what was
committed, so the public history between 2026-08-31 and 2026-09-23 cannot rebuild
those bundles byte for byte. The working repository, which is kept and never
rewritten, still can.
