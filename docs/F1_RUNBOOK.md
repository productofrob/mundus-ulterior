# F1 — what to run on the host, in order

*PowerShell, in the repo root, venv active. Nothing here calls the API and
nothing here touches the corpus. Never run a suite or a harness through the
Cowork bridge: each call is killed at 45 seconds and a killed harness leaves a
live mutation in the tree.*

## 1. The new suite and its harness

```powershell
python -m ingest.test_fidelity
python scripts\mutate_fidelity.py
```

Expect `30 passed, 0 failed`, then `all 24 mutations verified; sources
restored`. **If the harness prints `BASELINE:` or any `UNVERIFIED` line, stop
and fix the suite** — a green mutation against a red baseline is a vacuous
proof, and this harness carries the check from the day it was built.

## 2. The suite that was red, and the four that were not

```powershell
python -m ingest.verify
python -m eval.test_answer_eval
python -m answer.test_answer
python -m eval.test_ranking_check
python ui\test_build_ui_data.py
```

`ingest.verify` is the one to watch. **It has been failing since 2026-08-22** on
`manifest-flagged record 'weilue' is labelled verbatim_original` — FINDING 31 —
and it should now end `All integrity checks passed.` with two new notes: the
record-tier histogram against the F1 target, and the source-language count by
region.

**`ingest.verify` is a suite. It belongs in this list from now on, and it was in
no state block in the repository.** That is why it was red for a week while the
four below it were green.

## 3. The line-ending check, every time a harness has run

```powershell
git --no-optional-locks diff --stat
```

Expect four modified files and no file whose every line has changed. A file with
a change count equal to its line count is the LF/CRLF defect that reached a
commit on 2026-08-28, not your edit.

## 4. The digest, which F1 must not have moved

```powershell
python -c "from ingest.loader import seed_record_hashes, corpus_digest; print(corpus_digest(seed_record_hashes()))"
```

Must print `26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28`.
It is the denominator of all 396 Block E runs and of the sonnet arm's 165, and
F3 is what moves it. Anything else means a seed record was edited and the F1
commit must not land.

## 5. Commit

```powershell
git add -A
git commit -F commit-f1.txt
```
