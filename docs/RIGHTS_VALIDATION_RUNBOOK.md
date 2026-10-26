# RIGHTS VALIDATION HOST RUNBOOK — **TWO PARTS. PART 1 IS TWO COMMITS OF PROSE
# AND ZERO CELLS; PART 2, APPENDED AT THE CLOSE, IS THE THREE COMMITS THAT
# FOLLOW THE CONFIRMATION PASS AND THE ONE THAT TOUCHES DATA.**
#
# **Part 1's steps 1 to 4 are done. Its step 5 — the confirmation pass — is done.
# Start at Part 2, step 7.**

*Written 2026-09-14. The bridge shell is still down — confirmed again this
morning — so `git` and `python -m ingest.verify` are Rob's, not the session's.
**FINDING 116: a commit message written to its own correctly-named file is not a
commit.** Step 4 is the step that finding exists for.*

---

## Step 0 — what has landed on disk already

Four files were written into the repository root by the session and are sitting
**uncommitted** in the working tree:

```
RIGHTS_VALIDATION_PREDICTIONS.md   NEW   12,965 bytes
RIGHTS_VALIDATION_RULINGS.md       NEW    4,842 bytes
RIGHTS_VALIDATION_READINGS.md      NEW   22,196 bytes
RIGHTS_VALIDATION_RUNBOOK.md       NEW   this file, committed in step 4
RULINGS.md                         EDIT  40,173 -> 41,186 bytes
commit-rights-predictions.txt      NEW   gitignored, not part of any commit
commit-rights-readings.txt         NEW   gitignored, not part of any commit
```

Byte counts were checked after every write — FINDING 104 — and are repeated here
so a short file is caught before it is committed.

## Step 1 — session ritual, in PowerShell

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
git status --short
```

**Expect exactly the four tracked paths above and nothing else.** If anything
under `data/`, `ingest/`, `ui/` or `eval/` appears, stop — this block wrote none
of them, and something else is in the tree.

## Step 2 — the shape gate, BEFORE the commits

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
python -m ingest.verify
```

**This must be green and it must be green for a boring reason.** No cell was
written, so `check_rights` is being asked the same question it was asked at the
close of F7 and must give the same answer: 54 records, 54 cells, bidirectional,
and every non-`unread` cell signed and quoted. **If it is red, the redness is not
this block's** and the two commits below should wait until it is explained.

## Step 3 — commit the predictions and the ruling, as one commit

RULING 78: the predictions are committed before any cell is filled. No cell is
filled, so this ordering is intact — but commit it first anyway, because the
readings document is scored against it.

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
git add RIGHTS_VALIDATION_PREDICTIONS.md RIGHTS_VALIDATION_RULINGS.md RULINGS.md
git commit -F commit-rights-predictions.txt
git status --short
```

**Three files. `git add -A` would sweep the readings document in with them** and
the two are scored against each other, so they do not belong in one commit.

## Step 4 — commit the readings

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
git add RIGHTS_VALIDATION_READINGS.md RIGHTS_VALIDATION_RUNBOOK.md
git commit -F commit-rights-readings.txt
git status --short
git log --oneline -3
```

**Read `git status --short` after each commit and not `git log`.** FINDING 116 was
found by doing exactly that: 92 lines of finished work sat in the tree for a day
behind a complete, correctly-named commit message.

## Step 5 — the confirmation pass, which is the actual gate

**Nothing writes a cell until this is done.** `RIGHTS_VALIDATION_READINGS.md` §2
carries all 24 proposed cells with the URL, the verbatim quotation and the search
counts behind each. §4 names the three that carry a judgement rather than a
transcription and are worth the most attention:

```
the bare © line as all_rights_reserved     5 cells turn on one precedent
seasia-03 read off the item page           the object cited is the PDF
southasia-01 as one position, not two      a © line beside a permission
```

For each of the 24: **confirm, amend, or refuse.** A refused cell stays `unread`
and that is a complete outcome, not a gap.

## Step 6 — after confirmation, and NOT before

The cells are then written into `data/corpus_rights.json` with
`read_by: "curator_and_model"` and `read_on: "2026-09-14"` — or the date of the
confirmation, which is the honest one if it is a different day. That edit is a
text edit on hand-maintained data: staged, edited, committed back, **byte count
checked after the write**, and `python -m ingest.verify` run again on the host
before the commit, because that edit is the first one in this block that
`check_rights` can actually fail.

**`ui/data.js` is NOT regenerated for a rights edit.** `data/corpus_rights.json`
is a sidecar that no corpus walk reaches; it does not touch a content hash or the
corpus digest. If the Methodology copy later wants to print the column's counts,
that is the other thread's build and its own decision — FINDING 101 before
running `ui/build_ui_data.py` on Windows.

---

## The abort conditions, written against what they are a function of

```
git status --short shows anything under data/    STOP. This block wrote no data.
python -m ingest.verify is red before step 3     STOP. Not this block's redness.
a file's byte count differs from step 0          STOP. FINDING 104.
a commit message file is committed               It is gitignored (commit-*.txt).
                                                 If git adds one, .gitignore moved.
```

---
---

# PART 2 — **AFTER THE CONFIRMATION PASS. THREE COMMITS, AND `ingest.verify` RUN
# TWICE ROUND THE ONE THAT TOUCHES DATA.**

*Appended 2026-09-14 at the close. Step 5 above is DONE: all twenty-four cells
were confirmed live, host by host, and three of them changed in the doing.*

## What is now sitting uncommitted in the working tree

```
data/corpus_rights.json         EDIT  30,990 -> 71,331 bytes   24 cells + 1 amended
RIGHTS_VALIDATION_RULINGS.md    EDIT   4,842 -> 12,540 bytes   RULING 96, FINDINGS 120-122
RULINGS.md                      EDIT  41,186 -> 42,497 bytes   next free 97 / 123
RIGHTS_VALIDATION_RESULT.md     NEW                            the close and the scoring
RIGHTS_VALIDATION_RUNBOOK.md    EDIT                           this Part 2
commit-rights-rulings.txt       NEW   gitignored
commit-rights-cells.txt         NEW   gitignored
commit-rights-result.txt        NEW   gitignored
```

**Byte counts were checked after every write — FINDING 104.** If any of the three
figures above disagrees with what is on disk, stop before committing.

## Step 7 — the rulings, first, so the numbers exist before the cells cite them

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
git add RIGHTS_VALIDATION_RULINGS.md RULINGS.md
git commit -F commit-rights-rulings.txt
git status --short
```

## Step 8 — verify BEFORE the data commit, so a red is attributable

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
python -m ingest.verify
```

**This is the first run in the block that `check_rights` can actually fail.**
Twenty-four cells moved off `unread`, and each now has to satisfy SIGNED (a
`read_off` URL, a `read_by` of `curator | model | curator_and_model`, an ISO
`read_on`) and QUOTED (five of the seven positions must carry a verbatim
quotation; `states_no_terms` must carry NONE). The expected line is:

```
rights positions ... {'all_rights_reserved': 12, 'open_licence_stated': 11,
'states_no_terms': 7, 'permission_stated_no_licence': 5, 'two_positions_stated': 3,
'public_domain': 2, 'unread': 14}
14 of 54 record(s) are UNREAD
```

**If it is red, do not commit.** The likeliest failures are a `states_no_terms`
cell carrying a quotation it may not have, or a missing signature field — both
are shape errors in this session's writing, not in your confirmations.

## Step 9 — the cells

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
git add data/corpus_rights.json
git commit -F commit-rights-cells.txt
git status --short
```

**One file.** `git add -A` would sweep the result document and this runbook in
with the data, and FINDING 114 is three rounds of work collapsed into one commit.

## Step 10 — the close

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
git add RIGHTS_VALIDATION_RESULT.md RIGHTS_VALIDATION_RUNBOOK.md
git commit -F commit-rights-result.txt
git status --short
git log --oneline -6
```

**`git status --short` must print nothing after this.** Five commits should stand
above `8e1f8f9`: the start document, the predictions, the readings, the rulings,
the cells, the close.

## Step 11 — verify again, and that is the block

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
python -m ingest.verify
```

Same green as step 8, on a clean tree. **`ui/data.js` is NOT regenerated for a
rights edit** — `data/corpus_rights.json` is a sidecar that no corpus walk
reaches, it moves no content hash and no corpus digest, and `node ui/check_ui.mjs`
is unaffected. If the Methodology tab later wants to print this column's counts,
that is the other thread's build and its own decision, with FINDING 101 before
running `ui/build_ui_data.py` on Windows.

## The abort conditions for Part 2

```
a byte count differs from the table above     STOP. FINDING 104.
ingest.verify red at step 8                   STOP. Shape error in the cells.
git status --short non-empty after step 10    A commit did not happen. FINDING 116.
a commit-*.txt appears in git add             .gitignore moved.
ui/data.js appears in any diff                Nothing in this block regenerates it.
```
