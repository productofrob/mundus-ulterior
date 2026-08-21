# D1 step 1 — one seed-corpus walk. Runbook

*All commands are PowerShell on the host, from the repository root, venv active.
No API calls. The db container is needed only where marked.*

## Order matters here, and the reason is Finding 5

`scripts/mutate_places.py` rewrites `ingest/places.py` and
`ingest/gazetteer.py`; `scripts/mutate_ui_places.py` rewrites
`ui/build_ui_data.py`. All three are LF, so on Windows those harnesses will
convert them to CRLF and report *"sources restored"* anyway.

Clearing that churn afterwards means `git checkout -- <file>`, and
**`ingest/places.py` and `ui/build_ui_data.py` both carry uncommitted D1 edits
right now.** Running the harnesses before committing, then restoring, would
silently discard this step's work.

**So: commit first. Then run. Then restore.**

## 1. Commit

```powershell
git add ingest/loader.py ingest/places.py ingest/verify.py ui/build_ui_data.py scripts/write_a5_geonames_places.py D1_DESIGN.md D_TASK0_RESULT.md
git commit -F D1_STEP1_COMMIT_MSG.txt
Remove-Item D1_STEP1_COMMIT_MSG.txt
```

## 2. The suites that touch the five changed files

```powershell
python -m ingest.verify              # loader + places + verify, all three changed
python -m ingest.test_places
python -m ingest.test_sql            # needs the db container
python ui\test_build_ui_data.py
node ui\check_ui.mjs
```

## 3. The regression that actually matters

This change must alter **what the code does about a corpus that does not exist
yet** and **nothing whatsoever about the corpus that does.** That is the whole
claim, and it is checkable:

```powershell
python ui\build_ui_data.py --verify
```

```
24 seed record(s)                                       unchanged
77 archived run(s)                                      unchanged
{"resolved":157,"case_folded":0,"case_only":9,"moved":1,"absent":1}   IDENTICAL
```

**If any of those three move, the walk change altered which records are read and
the change is not additive.** Same standard C7 held its via-original fix to:
the target was computed before the code was written.

## 4. Mutation, ONE AT A TIME

```powershell
python scripts\mutate_places.py
```

then, only once it has printed its restore line:

```powershell
python scripts\mutate_ui_places.py
```

## 5. Clear the EOL churn these two will leave

```powershell
git diff --stat
```

Expect whole-file diffs on `ingest/places.py`, `ingest/gazetteer.py` and
`ui/build_ui_data.py` — hundreds of lines each, with no real content change.
Confirm that is all it is, then:

```powershell
git checkout -- ingest/places.py ingest/gazetteer.py ui/build_ui_data.py
git diff --stat
```

The second `git diff --stat` should print nothing.

**If any of those three files shows a diff that is NOT whole-file, stop.** That
would be a real content change left behind by a harness, which is a different
and much worse finding than line endings.

## 6. Confirm nothing else moved

```powershell
python -m eval.test_answer_eval      # 71 passed, 0 failed
python -m answer.test_answer         # all Part 7 offline checks passed
```

## What this step changed

```
ingest/loader.py                      iter_seed_records() — the one definition
                                      + CorpusLayoutError, MANIFEST_NAME
                                      iter_record_paths() delegates to it
ingest/places.py:669                  load_places
ingest/verify.py:56                   run
ui/build_ui_data.py:92                load_corpus      <- was the rglob outlier
ui/build_ui_data.py:354               build_places
scripts/write_a5_geonames_places.py   by_id
```

A `.json` anywhere other than `region/record.json` now raises
`CorpusLayoutError`. No flag, no lenient mode: a corpus two walks disagree about
is broken for everything, not only for D1.

## Still to come in D1

The digest itself and the plumbing — Decisions 1, 3, 4 and 5. Nothing of that is
written yet.
