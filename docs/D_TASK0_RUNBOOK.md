# D TASK 0 — runbook

*Written 2026-08-21. Every command runs in PowerShell on the host, from the
repository root, with the venv active. Nothing here spends an API call except
where marked.*

## Before anything

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
docker compose up -d db
```

The LiteLLM gateway is **not** needed for anything in TASK 0. `docker compose up
-d db` is needed only by the two distractor steps, which are marked.

## Step 1 — the suite that was red

```powershell
python -m eval.test_answer_eval
```

**Observed 2026-08-21: 71 passed, 0 failed.** The prediction written here was
70 and was wrong by one. The delta is accounted for exactly:

```
68   passing before
 +2   the two failing on the missing gold case
 +1   test_answer_eval.py:217 — one assertion per NON-REFUSAL case
 ---
 71
```

`test_answer_eval.py:206` loops over every case and, for anything that is not a
refusal case, emits `GUARD <id>: a refusal cannot satisfy this case`.
`adulis-exports` is answerable, so it adds exactly one — and its passing is the
property the discriminator depends on. If a refusal could satisfy
`adulis-exports`, both halves of the pair would be satisfiable by the same
silence and the pair would discriminate nothing.

Three printed values, not the count alone:

```
every archived run is scored (77 of 77)          was 76 of 77
every archived question has a gold case []       the list must be EMPTY, not shorter
GUARD adulis-exports: a refusal cannot satisfy this case
```

## Step 2 — the seven suites nobody has watched this session

Run each on its own and record what it prints. **Assert the value, not the
heading** — a suite that prints its banner and no rows is not a pass.

```powershell
python -m answer.test_answer
python -m answer.test_translate
python ui\test_build_ui_data.py
node ui\check_ui.mjs
python -m ingest.test_distractors      # needs the db container
```

Then the ritual four, so the baseline for TASK 1 is measured and not assumed:

```powershell
python -m ingest.run_embed --stats     # expect 450 / 450 / 0 pending
python -m eval.test_ranking_check      # expect 218
python scripts\mutate_ranking.py       # expect 91
```

## Step 3 — the mutation harnesses, ONE AT A TIME

Never two over one working tree. Each captures the originals at start and
restores at exit, so a second running concurrently captures the first's mutation
as the original.

```powershell
python scripts\mutate_part8.py
```

then, only after it has finished and printed its restore line:

```powershell
python scripts\mutate_part7b.py
python scripts\mutate_distractors.py   # needs the db container
```

### What to watch for on `mutate_part8.py`

Two things, and they are different findings.

**(a) The tail line should have changed.** Before today, `eval.test_answer_eval`
failed on its own account, so the harness ended with:

> *sources restored, but `eval.test_answer_eval` fails on its own account — a
> finding about the suite, not about this harness*

That line should now be **gone**. If it is still there, step 1 did not do what
it said.

**(b) The cp1252 trap is UNFIXED in this harness, and this run is the test of
whether it fires.** `scripts/mutate_ranking.py:756` runs its child as

```python
capture_output=True, text=True, encoding="utf-8", errors="replace",
env={**os.environ, "PYTHONIOENCODING": "utf-8"},
```

`scripts/mutate_part8.py:153` and `scripts/mutate_part7b.py:223` run theirs as

```python
capture_output=True, text=True,
```

— no `encoding`, no `errors`, no `PYTHONIOENCODING`. On Windows that means the
parent decodes the child's stdout as cp1252 and the child's own `print` encodes
to cp1252. Answer cases carry Greek, Tamil and Chinese by construction, so a
mutation whose failure detail quotes a source can kill either end.

**Run it unfixed anyway.** The restore is in a `finally`, so a death here leaves
the tree clean, and there are only two outcomes and both are worth having:

| outcome | what it means |
| :---- | :---- |
| `MISS <label> (crash, not a guard failure)`, or a `UnicodeDecodeError` traceback | the trap **reproduces**. The fix then has a measured before and after. |
| all mutations verified, no crash | the trap is **latent, not active** — no current mutation produces non-Latin failure detail. The fix is then a precaution, and must be written down as one. |

The second outcome is the same shape as the `.git/index.lock` hazard recorded at
the close of C7: re-entered, not reproduced, precaution kept. Recording which of
the two happened is the deliverable here, not a green line.

## What changed on disk for TASK 0

One file, data only:

```
M  eval/gold/answer_cases.json     +33 -2
```

No loader change, no harness change, no schema change. That is deliberate: if
the instrument changed in the same commit that turned it green, the green would
not be evidence that the instrument was working. The schema change —
`expected_behaviour`, and the pairing promoted from prose to a loader-enforced
field — belongs to D2/D3 and lands there.
