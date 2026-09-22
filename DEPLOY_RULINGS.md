# Deploy — rulings and findings. **RULING 98, FINDING 123, and FINDING 124**,
# declared 2026-09-22, before any rights target was opened or any file edited.

*On the numbers: `RULINGS.md`'s own line says the next free ruling is 97, and
that line is stale. RULING 97 was taken on 2026-09-22 (languages a record
references rather than holds) and recorded in `ui/index.html` beside
`LANG_REFERENCED_NOT_HELD` and in `commit-home-text.txt`, but not in the
register. `DEPLOY_START.md` §7 gives the next free numbers as ruling 98 and
finding 123. The register is corrected in the commit after this one, so that
this commit stays a predictions commit.*

---

# RULING 98 — **A SOURCE WHOSE STATED TERMS RESTRICT USE TO PERSONAL STUDY IS
# NOT THE SOURCE OF ANY TEXT THE PUBLIC PORTAL CARRIES.**

Taken by Rob on 2026-09-22, on the case the rights validation block flagged and
did not decide. `africa-04-silko-talmis` and `africa-05-adulis-throne` carry
Greek copied by hand from PHI Greek Inscriptions, behind a gate on the site root
that reads:

> *"I agree to use this website only for personal study and not to make copies
> except for my personal use under "Fair Use" principles of Copyright law."*

A public portfolio site is not personal study, and publishing the site publishes
every record's full text (`DEPLOY_START.md` §2).

```
WHERE A PUBLIC-DOMAIN     the text is re-sourced to it by collating the excerpt
EDITION EXISTS            against that edition's printed page, character by
                          character. The record then cites that edition, and
                          its rights cell is read off it

WHAT THE COLLATION        where the edition's characters differ from the
DECIDES                   record's, the edition's characters stand and the
                          difference is recorded in original_text_note.
                          Nothing is kept because it was already there

THE RESTRICTED SOURCE     stays in the note as a cross-reference: where the
                          text was first found, and which edition it prints.
                          It is not the citation, and nothing is quoted from it

WHERE NO PUBLIC-DOMAIN    the restricted source still may not supply the text.
EDITION EXISTS            What replaces it is NOT settled here; the next such
                          case gets its own ruling
```

**For these two records:**

```
africa-04  OGIS 201   W. Dittenberger, Orientis Graeci Inscriptiones Selectae I
                      (Leipzig, 1903). PHI itself files the text as OGIS 201
africa-05  OGIS 199   the same volume. PHI prints Kosmas from Wolska-Conus's
                      edition (1968-73), which is in copyright, so OGIS's text
                      is expected to differ. The collation says by how much
```

**Why this and not the alternatives.** All three were put to Rob with their
costs stated:

- **Withholding the Greek** keeps the records and removes the one thing they
  exist for, which is Sub-Saharan Africa's source-language text for retrieval.
  Archived quotations into that field would stop resolving.
- **Publishing unchanged** treats two to four lines of an ancient inscription as
  ordinary scholarly quotation, which is what they are. It also publishes under
  terms the project read, recorded, and found it does not satisfy, which is the
  thing the rights column exists to prevent.
- **Dropping both records** takes the corpus from 54 to 52 and changes every
  count on every tab.

**What it does not do.** It does not settle africa-04's English. That is
Satzinger's rendering on a personal university page, and nobody has read its
terms. Under RULING 96 the cell is for the material the record's quoted text
comes from, so that page is read in this block, separately
(`DEPLOY_PREDICTIONS.md` P5).

**How it relates to RULING 74.** Ruling 74 lets an in-copyright source be quoted
under four declared conditions. This ruling is narrower and different in kind:
it is about a source's stated terms of use rather than about copyright, and it
applies whatever the length of the quotation.

---

# FINDING 123 — **635 OF 1,227 "RESOLVED" SPANS DO NOT HOLD THEIR QUOTE
# EXACTLY.** Measured before this block and handed over without a number;
# numbered here so that the register does not carry an unnamed defect onto a
# public site.

The only write-up is `DEPLOY_START.md` §7, quoted:

> *"610 record an end offset one or two characters short, almost always a
> closing bracket or comma. The corpus-wide check compares with `includes` in
> either direction and cannot see it; the chain figure's guard compares exactly
> and found it the moment the example moved."*

The other 25 are not a simple 1–2 character shortfall, and their shape is
uncharacterized.

**It bears directly on Home's own claim**, that "almost every click lands on the
exact characters". Numbering it is the only action this document takes. **Whether
Home's sentence can go public while the finding stands is a question for Rob
before step 9** of the order of work in `DEPLOY_PREDICTIONS.md` §1.

---

# FINDING 124 — **THE 2026-09-22 AMERICAN-SPELLING SWEEP MISSED VISIBLE TEXT IN
# THE PAGE, AND COULD NOT HAVE REACHED THE REST.**

Rob asked for the whole portal to be swept into American spelling on
2026-09-22. On the first look in this block, a narrow pass over the RENDERED
text of all four tabs, with every `<details>` opened, found:

```
PAGE COPY      " · romanised"   index.html:5754, the banner-label template.
                                Built inside a template literal, so four
                                labels on every tab come from one string
               "romanised"      index.html:5663, Methodology: "some as
                                romanised transcriptions"
RECORD PROSE   "catalogue"      the Šahrestānīhā title
               "travelled"      the Rycksta stone title
               "organised"      place notes, "the passage is organised
                                around", rendered six times on Methodology
```

**Two different causes, and only one of them is a miss.** The page-copy strings
are sentences in `index.html` that a sweep of the page should have caught. One
of them is assembled in a template literal, which a sweep over prose can pass
over. The record-prose strings live in `data/seed_corpus/`, where changing a
word moves the record's `content_hash`. A sweep of the page could not reach
them, and doing so needed a record pass, which is where they now go.

**The pass that found these was sixteen patterns, not a sweep.** The fix step
runs a wider one over the rendered text, and it must exclude quotation fields:
a British spelling inside a quoted source or published translation is the
source's own, and it stays.
