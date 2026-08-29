# F2 runbook — the commands, in order, on the host

*Everything below runs in PowerShell in the repo root with the venv active.
Nothing here needs the database or the gateway except the two that say so.*

## 0. The skip that is not a pass — DONE 2026-08-29

`pip install -r requirements-dev.txt` installed sqlglot 30.17.0 and
`answer.test_answer` ran clean with no skip line. F1's owed item 2 is closed.

The skip guarded **exactly one assertion** — *schema and queries parse as
PostgreSQL* — which parses the whole Part 7 schema, every query in `queries`,
and both `UPSERT_ANSWER` and `UPSERT_CITATION`. The parameter-cast and
`ON CONFLICT` guards around it are regex-based and had always run.

**Two suites now print their own count.** `ui\test_build_ui_data.py` had the
same defect -- a verdict and no number -- and now reads `14 passed, 0 failed`.
Seven suites, seven counts.

On `answer.test_answer` specifically: It printed nothing but
`all Part 7 offline checks passed`, which is why `GREEN, with ONE SKIP` could
stand in a state block with no way to tell one skipped assertion from thirty.
It now reads `150 passed, 0 failed`, and a future absence of sqlglot reads
`149 passed, 0 failed, 1 SKIPPED` with the assertion named beneath it.

**Still owed from the same install, and not done:** `ingest/test_sql.py` gains
sqlglot checks too and needs the database, so it has not been run with sqlglot
present. Run it once with the Postgres container up:

```powershell
python -m ingest.test_sql
python -m ingest.test_embed
```

Guards that have never run are guards nobody knows work.

## 1. The seven suites

`ingest.verify` is FIRST, and it is a suite. FINDING 31: it was red for a week
because no state block listed it.

```powershell
python -m ingest.verify
python -m ingest.test_fidelity
python -m ingest.test_cost
python -m eval.test_answer_eval
python -m eval.test_ranking_check
python -m answer.test_answer
python ui\test_build_ui_data.py
```

**Expected, and these numbers are printed by the suites themselves:**

```
ingest.verify            All integrity checks passed.
                         + a new note line: "curation cost: 0 record(s) timed,
                           24 excused. Comparator: within_tranche"
ingest.test_fidelity     30 passed, 0 failed
ingest.test_cost         46 passed, 0 failed        <- NEW
eval.test_answer_eval    343 passed, 0 failed       <- was 333; +10 for FINDING 32
eval.test_ranking_check  236 passed, 0 failed
answer.test_answer       150 passed, 0 failed     <- now prints its own count
ui\test_build_ui_data.py  14 passed, 0 failed    <- now prints its own count
```

## 2. The mutation harnesses

`mutate_cost.py` is new and shipped WITH the baseline check.
`mutate_part8.py` gained five mutations for FINDING 32 and is now 87.

**Run these on the host and not through the bridge.** `mutate_part8` is 87
mutations at roughly twelve seconds a suite run — around eighteen minutes — and
a harness killed between applying a mutation and restoring the sources leaves
the mutation on disk. That happened in this session to `eval/answer_eval.py`.

```powershell
python scripts\mutate_cost.py
python scripts\mutate_part8.py
python scripts\mutate_fidelity.py
python scripts\mutate_ranking.py
python scripts\mutate_part7b.py
python scripts\mutate_ui_places.py
```

**Expected:**

```
mutate_cost.py      all 37 mutations verified; sources restored     <- NEW
mutate_part8.py     all 87 mutations verified                       <- was 82
mutate_fidelity.py  all 24 mutations verified
mutate_ranking.py   all 100 mutations verified
mutate_part7b.py    all 18 mutations verified
mutate_ui_places.py all 4 mutations verified
```

**If a harness is interrupted**, check the tree before doing anything else:

```powershell
git status --porcelain
git diff
```

A mutation source left modified is a live mutation in your working tree. Do NOT
use `git checkout --` from the bridge — it cannot unlink and fails halfway.
From PowerShell `git checkout -- <path>` is fine.

## 3. The ledger — three READ-ONLY commands

**These three and nothing else.** None of them writes to the ledger.

```powershell
python -m ingest.cost_log status
python -m ingest.cost_log report
python -m ingest.cost_log check
```

`report` is the ONLY place a curation-cost number may be read from. Nothing in
`PROGRESS.md`, `F2_RESULT.md` or any later document may carry a cost figure
that was not printed by it — F1 put an assertion count into five files as 29
when the suite had 30, because the number was transcribed rather than read.

**Expected:**

```
status   no clock is running.
         0 record(s) timed, 24 excused from timing.
report   the comparator header, then NO RECORD HAS BEEN TIMED YET
check    curation cost ledger: all checks passed.
```

Do NOT run `cost_log start` before committing. It opens a clock, an open clock
fails `ingest.verify` by design, and step 4 would then commit a red tree. The
writing commands are in the reference section at the foot of this file, which
is F3's and has nothing to run today.

## 4. Commit

**Everything is already staged.** `git add -A` was run through the bridge and
the sixteen paths below are in the index. Re-running `git add -A` is harmless.

**One bridge artefact to know about.** Every `git` command run through the
bridge leaves a zero-byte `.git/index.lock` behind, because the bridge can
create the file and cannot unlink it. It was moved to
`_to_delete/git-locks-2026-08-29/` before this session stopped touching git, so
the tree you have is clean — but if a commit ever fails with
*"Unable to create '.git/index.lock': File exists"*, that is what it is, and
from PowerShell `del .git\index.lock` clears it. `_to_delete/` can be emptied
whenever you like.


```powershell
git add -A
git commit -F commit-f2.txt
git log --oneline -3
```

---

# Reference — the CLI F3 will use. NOTHING HERE IS RUN TODAY.

Kept out of the numbered steps deliberately: a runbook step should contain only
commands that are run when the step is reached, and this block sitting inside
step 3 was read as one on 2026-08-29.

**Per record, starting at record 25:**

```powershell
python -m ingest.cost_log start <record-id> source_hunting
# ... work ...
python -m ingest.cost_log stop
python -m ingest.cost_log start <record-id> text_capture
python -m ingest.cost_log stop

# a phase done away from the keyboard, or a clock that was left running:
python -m ingest.cost_log add <record-id> rights_and_licence --minutes 20 `
    --because "checked the licence in the browser before the clock existed"
```

The seven phases are `source_hunting`, `rights_and_licence`, `text_capture`,
`translation_and_fidelity`, `placement`, `authoring`, `rework`. **Every record
must carry all seven, and a phase that took no time records zero** — an absent
phase and an unrecorded phase are the same shape on disk.

**`ingest.verify` goes RED if a clock is left running, and RED if a record
reaches the corpus with no ledger row.** Both are deliberate and both are
ruling 47's point: nobody times a record twice.
