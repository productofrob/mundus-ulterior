# RIGHTS VALIDATION HOST RUNBOOK — **TWO COMMITS OF PROSE, AND ZERO CELLS.**
# `data/corpus_rights.json` is not in either commit and its byte count is
# unchanged at 30,990.

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
