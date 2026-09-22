# UI METHODOLOGY FINAL RESULT — **THE TAB IS BUILT FROM THE COPY, THE GUIDE LEFT IT,
# AND THE ONE MEASURE NOBODY REPORTED IS NOW ON THE PAGE.**
#
# **Scored against `UI_METHODOLOGY_DESIGN_PREDICTIONS.md`, unamended. Closed 2026-09-22.
# No ruling or finding numbers are assigned here.**

*Scope per `UI_METHODOLOGY_BUILD_START.md` as amended by `UI_LOOSE_ENDS_START_AMENDMENT_1.md`:
the Methodology tab's text and page design, A and B (hosting claims scoped to the reference
copy), F (the question box cut from the copy). Nothing here prepares the Lovable port.*

---

## 0. WHAT SHIPPED

```
ten sections, built from METHODOLOGY_COPY_FINAL.md      abf944b
the section 1 figure, four corrections                  d5002f2
the Guide off this tab, guard 61 rewritten              abf944b
retrieval by the language of the source, guard 62       this commit
zero-count citation outcomes suppressed                 this commit
the evidence panels rewritten to the copy rules         this commit
```

**113 flags were raised against the copy, the figures and the other tabs; Rob ruled on every
one.** The record is in `claude/methodology-final-flags.md` and
`claude/methodology-final-corrections.md`.

---

## 1. THE PREDICTIONS, SCORED

### P1 — LENGTH. **REFUTED, and the half that matters holds.**

```
                    predicted            measured
390px               13,000 – 16,000      15,931      inside
1600px               9,000 – 11,000      11,560      OUTSIDE, by 560
the floor claim     not below 12,000     15,931      holds
baseline                                 10,161 / 17,970
```

The phone figure landed inside its range and above the floor: the tab is a ninth shorter on a
phone than the cards were, which is not a fix and P1 said so before the work started. **The
desktop figure is outside its range in the direction nobody predicted — the rebuilt tab is
LONGER at 1600px than the cards it replaced.** The cause is a decision taken during the build
and not in the predictions: prose is set to a 68-character measure, because the column is
1,075px wide and a line of that length is unreadable. Narrower lines are taller. The
predictions were computed against a full-width render.

**The estimate in §1 of the predictions document (9,741 / 14,356) under-counted for a second
reason as well**, already recorded in the build start: it carried one figure, and the section
10 figure did not exist when it was made. That figure is now dropped, so the estimate's error
is the measure, not the figure.

### P2 — THE GUARDS. **REFUTED, by the clause the block triggered itself.**

```
2g   no count written down                NEVER RED        held
53   geography ledger re-derived          unmodified       held
49   panel empty state declares kinds     MOVED            refutes
61   every kind round-trips               REWRITTEN        refutes
58, 59, 60                                never went red   see below
harness ends at 61 checks or higher       62               held
```

P2 is refuted by "49 or 61 moving", and both moved — because Rob ruled on 2026-09-21 that the
Guide is for the other tabs. Guard 49 now skips a tab that renders no panel; guard 61 was
rewritten to assert the tab renders none, that every address handed out while it did still
opens the same thing on Map & Sources, and that the bare forms are unchanged. **That is RULING
88 applied, not relaxed: the guard moved with the thing it guards and gained a claim.**

**Guards 58, 59 and 60 never went red, and the prediction said they would.** The prediction
assumed the card prose would be rewritten and the derived figures re-homed by hand. What
happened instead is that the card functions were re-homed whole, inside collapsed evidence
panels, so the attributes those guards read never moved. Prediction wrong, and the reason is
worth keeping: a guard that reads a function's output does not care where the output is
rendered.

### P3 — NO COUNT BECOMES TYPED. **REFUTED, in letters, twice.**

Every figure in the evidence panels is computed. The prose is not clean:

```
§5   "Two kinds of written decision."            a count, in letters
§10  "Embeddings: voyage-3.5, at 1,024 dimensions."   a specification, and a typed figure
```

Guard 2g catches neither, and cannot: it hunts five literals it was told about, and a guard
that hunted every number word would be unenforceable. Rob ruled on 2026-09-16 to keep the
claim and remove the typed counts as they came up; four were removed (§4's "Two figures",
§8's "1 of 3", §10's "three requests a minute" and "Half of it"), and these two were judged
to be describing the system rather than counting the data. **The claim in §5 is stronger than
the page can keep, and it is recorded here rather than softened in the copy.**

### P4 — THE RIGHTS SLOTS. **WITHDRAWN BY RULING, NOT SCORED.**

Rob ruled on 2026-09-16 that §2 carries no rights figures. `ui/build_ui_data.py` was not
extended to read `data/corpus_rights.json`, so the prediction has nothing to score. The six
values were independently recomputed from the sidecar during the copy check and agreed with
the prediction (54 / 40 / 26 / 25 / 14 / 4), which is recorded here so the work is not lost.

### P5 — THE PORT SWEEP. **CONFIRMED.**

Beyond the three statements already named, the sweep found:

```
§5    "This portal is a port of that reference…"     false of the page TODAY, the reverse error
§7    "A separate instrument measures the page's layout"   measures the reference copy only
§10   "The page is a set of plain functions…"        true of what the checks execute
§10 figure  "Published site — static files, no server"     and its caption, "two static files"
Home  "every step below is read out of the archive when this page loads"
```

Five more, against a prediction of at least three. All were scoped to the reference copy per
Amendment 1 §3, in prose and in the figure, in one pass.

### P6 — A CLAIM WITH NO CHECK BEHIND IT. **CONFIRMED.**

At least one sentence ships that is true on build day, carries no check, and would not survive
the data moving. The clearest:

```
§8  "The exception is the record of a carved gemstone from Khao Sam Kaeo in Thailand,
     which has never been found."
§8  "Old Tamil performed worst at every stage run on the project's standard model"
§6  "Only the pass mark for prose has been set that way so far; the others are provisional."
```

The first is the sharpest instance, and it is new writing from this block: one ranking run
that finds that record makes it false, and nothing on the page would notice. Two of the three
candidates named in advance are in the shipped page. **The third named candidate — §4's
"English-language targets hold and non-English targets fall away" — is the one sentence of the
three that now DOES have a check behind it**, because guard 62 re-derives exactly that split.

---

## 2. THE RULINGS TAKEN IN THIS THREAD

```
2026-09-16  the six rights figures are not included                     P4 withdrawn
2026-09-21  the Guide box is for the other tabs; Methodology has none   guard 61 rewritten
2026-09-22  the section 10 figure does not ship                         built, never approved
2026-09-22  a citation outcome with no cases is not printed             R4
2026-09-22  the evidence panels are rewritten to the five copy rules    R7
2026-09-22  one evidence panel is wired, four bracket lines are cut     R6 as scoped
```

**The section 10 figure is dropped, and its files stay where they are.** `architecture-detail.html`
and `architecture-detail.build.py` are not deleted: cleanup in this repository has a recorded
history of costing more than it saves, and an unused generator costs nothing. Its content is in
§7 and §10 as prose. Two figures on one tab was the question; one figure is the answer.

---

## 3. GUARD 62, AND WHAT IT CAUGHT ON ITS FIRST RUN

The tab said, in two sections, that nothing reported retrieval by the language of the source.
It is reported now: `ui/build_ui_data.py` carries the archived ranking runs, split English from
everything else, and the page builds the table. Guard 62 builds the same table again from the
bundle's per-pair rows and compares them cell by cell, the separation `placeLedger` and guard
53 have.

**It failed on its first run, and the fault was in the page rather than in the check.** Two
runs in the archive searched the same number of passages and returned different figures, so a
row addressed by its size was a row the guard could read the wrong one of. The rows are
addressed by the run they came from now. **A second failure was in the check itself**: run
identifiers carry a `+0000` offset, and an unescaped `+` in the pattern made every row read as
missing. Both are the reason a new check is run before it is trusted.

```
what the table says, from the run of 2026-09-06 over 561 passages
  English        8 of 9
  everything else 21 of 35
  Old Tamil      1 of 3, and the question that fails it ranks 373rd
  17 comparable runs in the series; 17 more excluded for using the dropped experiments
```

---

## 4. WHAT THIS BLOCK LEAVES OPEN

**Handed to the next thread, in Rob's order:**

```
1  the Home tab's text                S1–S8. Home still says "You ask a question in English",
                                      and the citation figures cannot be reconciled across tabs
2  final layout edits                 minor, and after the text
3  the Lovable port                   LAST, held pending Rob's explicit order
```

**Also open, and not owned by any thread yet:**

- **The record-data pass, S9–S18.** The Safaitic inscription is labelled Nabataean Aramaic
  (and now appears that way in the retrieval table as well); the Songshi record says four
  hundred years where it is three; two records claim to be the first of something they are
  not. These change the records themselves, so they change fingerprints.
- **Four evidence panels were cut rather than built**: the passage table, the retrieval test
  set, the test suites and the rulings register, and the translation and place audits. The
  copy no longer advertises them.
- **§6 of the predictions document is unscored, and the block does not close without it.**
  Nothing in this document can score it. Rob has to use the tab at both widths.

---

## 5. THE FIGURES THIS DOCUMENT COMMITS TO

```
the tab, measured          11,560 at 1600px · 15,931 at 390px   measure_data.mjs, 2026-09-22
the baseline it replaced   10,161 / 17,970
the harness                62 checks, green
the copy                   ten sections, 3,938 words
the bundle                 gained a retrieval section; data.js 9,551 KB
```
