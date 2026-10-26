# GitHub release: rulings and findings. **RULING 101**, declared 2026-10-26,
# before any rights target was opened or any file edited; **FINDING 126**,
# declared the same day by the redistribution pass; and **RULING 102**, taken the
# same day on the history scan.

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
removes from the history: **it is rob@productofrob.com**, Rob's choice of
2026-10-26. productofrob.com no longer has a contact page.

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

---

# FINDING 126 — **THE PORTAL CARRIES ONE GFDL DOCUMENT ENTIRE, AND LINKS THE
# LICENSE INSTEAD OF REPRODUCING IT.**

Found on 2026-10-26 by the redistribution pass (`GITHUB_RELEASE_READINGS.md`,
R-1), and confirmed by Rob the same day.

`arabia-08-walters-marib-pediment`'s `original_text_excerpt` is the Walters Art
Museum's object description, "VERBATIM AND ENTIRE" in the words of its own
`original_text_note`: 700 characters. The Walters releases those descriptions
under the GNU Free Documentation License and names no version. The GFDL's
verbatim-copying clause (§2) requires that "this License, the copyright notices,
and the license notice saying this License applies to the Document are
reproduced in all copies."

**Methodology §2's license list names the GFDL and links gnu.org. It does not
reproduce the license.** The rights validation and deploy blocks read the
position correctly. Neither asked what a GFDL position obliges a copy to carry,
because the column records what a source states, not what a copy owes.

```
WHAT IS DONE HERE      the repository ships LICENSES/GFDL-1.3.txt and names the
                       record against it in DATA_RIGHTS.md. With no version
                       named, §10 lets any published version be chosen
WHAT IS NOT DONE       any change to the live site. Rob's order of 2026-10-26
                       holds every change to the Mundus Ulterior page until he
                       gives it. The site half is listed for him and carried as
                       open in the result document
```

**The general lesson:** a position says what may be done with a text, and a
license can also say what every copy must carry. Among the 54 cells, only the
GFDL requires its own full text in the copy. The Creative Commons licenses ask
for the license to be named with a link or URI, and Methodology §2 gives one.

---

# DECISIONS TAKEN AFTER THE PREDICTIONS COMMIT

```
2026-10-26  The rights contact is rob@productofrob.com (RULING 101)
2026-10-26  D2's address is 10733157+productofrob@users.noreply.github.com,
            read off Rob's GitHub email settings, where "Keep my email
            addresses private" is on
2026-10-26  D8 IS HELD. Rob: "Do not do anything else on the Mundus Ulterior
            page until I tell you." After the GitHub release, an updated banner
            on the site will link the repository, the case study, and the
            contact address. The four §10 links wait for that, and FINDING
            126's site half waits with them
2026-10-26  All 54 redistribution readings confirmed, together with the Tamil
            title of the Madurai header, checked against the page
2026-10-26  D1 confirmed against the history scan, as RULING 102
```

---

# RULING 102 — **A FULL COPY OF TEXT TAKEN FROM A RESTRICTED SOURCE LEAVES THE
# PUBLIC HISTORY. A PHRASE OF THE ANCIENT TEXT STAYS.**

Taken by Rob on 2026-10-26, on the history scan (`GITHUB_RELEASE_HISTORY_SCAN.md`),
from three options, with the recommendation.

PHI Greek Inscriptions' gate reads: *"I agree to use this website only for
personal study and not to make copies except for my personal use."* RULING 98
made that the rule for the portal. The scan found PHI's copies of the Silko and
Adulis excerpts in 23 blobs of the history, one of them the current
`DEPLOY_COLLATION.md`, and phrases of 3 to 7 words in five documents and one
commit message.

```
REMOVED    every full copy of text a restricted source supplied: each version
           of a record, of data.js, or of a document that carries the copied
           excerpt whole. Each is replaced in place by a bracketed notice
           saying what was withdrawn, under which rulings, and where the
           record's text comes from now
KEPT       a phrase of a few words, quoted in a document or a commit message,
           whose letters any public-domain edition prints. That is the
           ancient text, not the restricted source's copy of it. The
           collation sheet's list of single-word differences is kept on the
           same ground
WHERE      in the public clone only, in the same git filter-repo pass as D2's
           address mapping. The working repository is never rewritten
```

**Why not keep everything.** The scan measured PHI's text at six characters from
OGIS's public-domain edition, so what would be republished is almost all
public-domain text. It would still be copies made under terms that said not to
make them, and RULING 98 exists to keep those terms.

**Why not remove the phrases too.** That would edit the wording of five
documents and a commit message, including a finding whose subject is the
characters of one phrase, for words that are the inscription itself.

**What it costs.** The public history between 2026-08-31 and 2026-09-23 cannot
rebuild those records and bundles byte for byte. The working repository is kept,
and still can. No archived answer changes, because none quoted the withdrawn
text.
