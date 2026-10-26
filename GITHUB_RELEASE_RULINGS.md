# GitHub release: rulings and findings. **RULING 101**, declared 2026-10-26,
# before any rights target was opened or any file edited.

*On the numbers: `RULINGS.md` gives the next free ruling as 101 and the next free
finding as 126, and nothing written since `DEPLOY_RESULT.md` has used either. The
register is updated in the redistribution pass's commit, so that this commit
stays a predictions commit.*

---

# RULING 101 — **THE REPOSITORY IS NOT UNDER ONE LICENSE, AND NOTHING AT ITS
# ROOT MAY SAY IT IS.**

Taken by Rob on 2026-10-26, on R3 of `github-release-start.md`. The
recommendation was an MIT `LICENSE` at the root, so that GitHub would detect it,
with the scope stated in the README and `DATA_RIGHTS.md`. It named the cost:
GitHub's sidebar would then say "MIT" for the whole repository. Rob:

> *"I don't want the whole repo to say 'MIT' because it's not true."*

**This applies the rights column's rule to the repository's own label.** The
column exists so that no record says less than its source states, or says
something different (RULING 74, condition 3). A one-word label over 54 records
the project does not own would be the same substitution in the other direction:
the project stating terms that are not its to state.

```
CODE                     MIT. Program, page, and configuration files, by what a
                         file is rather than where it sits; ui/data.js is not
                         code. The verbatim text is in LICENSES/MIT.txt
ROB'S DOCUMENTS          CC BY 4.0: docs/, the README, and the page copy in
                         ui/index.html. Anything they quote from a source is
                         excepted and keeps that source's terms. The verbatim
                         text is in LICENSES/CC-BY-4.0.txt
THE CORPUS, AND          no license from this project: data/seed_corpus/, the
EVERYTHING THAT          archived runs under eval/, and ui/data.js. Each
QUOTES IT                record's own terms govern, as data/corpus_rights.json
                         states them per record
THIRD-PARTY DATA         under its own terms, credited in DATA_RIGHTS.md:
                         Pleiades, GeoNames, the Natural Earth coastline, the
                         Cleveland Museum of Art and Metropolitan Museum of Art
                         open-access records, and anything else the
                         declarations in data/ name
THE ROOT FILE            LICENSE.md states the scope and is not itself a
                         license text, so no detector reads it as one license
                         over the repository. The license texts live in
                         LICENSES/
```

## The disclaimer, as Rob gave it

Rob asked for three things to be said:

1. every effort has been made to verify that each source is used in line with
   its rights;
2. Mundus Ulterior makes no copyright claim of its own to any of the source
   material it uses;
3. anyone with a copyright concern should contact Rob.

They are carried in `LICENSE.md`, `DATA_RIGHTS.md`, and the README's license
section, in the same words in all three. The contact is not the address that D2
removes from the history.

## What it changes

- **`github-release-start.md` step 6:** "GitHub detects the license" becomes
  "GitHub's sidebar names no single license for the repository, and links
  `LICENSE.md`."
- **RULING 74's fourth condition** ("the use is non-commercial research and the
  corpus stays so") is stated in `DATA_RIGHTS.md` as a condition on the corpus,
  because the repository invites others to build on it.

## What it does not do

**It is not a legal opinion,** as RULING 74 says of itself. It licenses nothing
that is not Rob's to license, and it decides no cell. The redistribution pass
does that, one cell at a time.
