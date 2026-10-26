# Block D, TASK 3 (D4) — starting point for the next thread

*Written 2026-08-22 at the close of TASK 2. Supersedes `BLOCK_D_TASK2_START.md`,
whose TASK 2 is done. Every number here was measured on the host.*

## Read these, in this order

| # | file | why |
| :---- | :---- | :---- |
| 1 | **this file** | state, and the one task left in Block D |
| 2 | `D3_RESULT.md` | the 33-case gold set and what Block E inherits |
| 3 | `FINDINGS_9_TO_13.md` | five findings, four of them in the instruments |
| 4 | `RULINGS.md` | index of rulings 1–31. Read before quoting a number |
| 5 | `BLOCK_D_START.md` **TASK 3 only** | still authoritative for D4 |
| 6 | `eval/gold/floor.json` | read it whole. `calibration_invalidated` is why D4 exists |
| 7 | `PROGRESS.md` **last section only** | ~594 KB. Do not read it whole |

`BLOCK_D_START.md`'s TASK 0, TASK 1 and TASK 2 sections are **done**. Its "state
as measured 2026-08-20" block is **stale** by two days and three corpus digests.

## State, as measured 2026-08-22

```
tree            b1e11ab, clean
                b1e11ab  FINDING 11: the paraphrase flag marked suspicion
                2c8f20e  the Finding 10 demonstration
                5a3bd7b  D3 and the Weilue investigation, two documents
                846d5b9  FINDING 10: stdout guard, 43 entry points
                5b9aed2  the runs behind the Weilue fix
                d0ef3bc  FINDING 13: expect_quoted_from_original
                5289f55  Weilue: invented excerpt -> sourced Sanguozhi text

corpus          24 records / 59 chunks / 57 retrieval-eligible
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
index           450 / 450 / 0 pending
archives        79 answer runs, 26 ranking runs, 3 sweeps (ALL within-session)
gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
                Arabia 4  East Asia 5  Persia 4  Scandinavia 5
                South Asia 5  Southeast Asia 4  Sub-Saharan Africa 5  outside 1
floor           calibrated: false, 4 required, 2 known-failing

ANSWER          eval.test_answer_eval       203   GREEN
mutations       mutate_part8                 27   GREEN
```

**THE DIGEST CHANGED THREE TIMES TODAY.** `2e84436c` → `bcfa0211` → `26e4a683`,
from two real corpus edits (the Weilüe text, then the Hou Hanshu note). Only
`26e4a683…` is current, and it is the number Block E records on day one and
re-asserts on day three. Any document still naming `2e84436c` is stale.

## TASK 3 — the only thing left in Block D

`BLOCK_D_START.md`'s TASK 3 is still authoritative. Restated, because it is now
the last thing between here and a Block E that can be believed:

1. Record a **session identity** — run date at minimum — in every sweep archive.
2. Make floor calibration **refuse to set `calibrated: true`** when distinct
   dates < 3, and **mutation-verify that refusal**.
3. Report **per-case stability and per-session stability as two separate
   numbers.** One number cannot say which of the two is moving.
4. **Pilot on 5 cases across 2 days, ~30 chat calls**, so the three-day sweep is
   not the first time this code runs across a date boundary.

**The gap is confirmed, not assumed.** `eval/run_answer_sweep.py` takes
`--prompt-version --repeat --case --k --max-sources --pause --dry-run --no-write
--json`. There is no session flag and no date field in any archive. Checked
2026-08-22.

**Why it is not optional.** `floor.json` says `calibration_invalidated:
"2026-08-10, hours after being set."` The floor was calibrated on CONTENT being
stable in 10 of 10 cells across three repetitions each. A second sweep, with the
`vimose-runes` evidence block byte-identical across all six archived runs,
produced 3/3 with seven resolved quotations in the first session and 0/3 with
none in the second. Same prompt version, same model, same evidence, temperature 0.

All three archived sweeps are within-session. **Block E's 270 calls are worth
nothing if the archives cannot tell a session from a repetition**, and today they
cannot.

## Carried into D4 from TASK 2 — three things, and one is unfinished work

**FINDING 12 is unguarded and it is the first thing to do.** `run_ranking_check.py`
drops a gold pair that stops resolving and reports it only as a count line. On
2026-08-22 two pairs left a run and every aggregate moved because the DENOMINATOR
shrank — via-original reranked read `22/30 -> 21/29`, which looks like a
regression and is a lost pair. The invalid archive
`eval/ranking_runs/20260822T160349…` is committed deliberately as the exhibit.
The fix is a pair-count check against the gold file, failing loudly and naming
what did not resolve. `scripts/weilue_compare.py` already does this for the
Weilüe pairs; the harness itself does not.

**`match_case` returns the FIRST case whose question matches.** Two cases sharing
a question would leave the second silently unscored against every archive —
sitting in the gold set looking like a test and never running. Avoided by hand in
`weilue-chinese-quotation`; unguarded in the loader. Same family as Finding 12.

**Two gold cases are expected to fail and must stay failing.** `aksum-exports`
and `weilue-chinese-quotation`, both tracked in `floor.json.known_failing_cases`
as OPEN defects, both out of `required_cases`. Neither is closed by D4. A sweep
that reports them passing is a finding, not a success.

## Traps carried forward

Everything in `BLOCK_D_START.md` and `BLOCK_D_TASK2_START.md` still applies.
Four to add, all learned the hard way on 2026-08-22:

- **A green result from a partial copy of the repository is not a result.** The
  stdout-guard count was reported as "22 of 22" from a sandbox that did not
  contain twenty-one of the entry points. Verify against the tree that ships.
- **An enumeration maintained by hand will be wrong.** That same count was wrong
  four times — 7, 20, 22, 43. The check that finally held asserts the RULE and
  globs at check time, and additionally asserts the glob found at least forty
  files, because an enumeration that collapses to zero passes vacuously.
- **A passing suite proves nothing about non-Latin output.** The first proof of
  the encoding fix was `test_answer_eval > file` returning 0. A green run prints
  only `ok` lines in English; the non-Latin lives in failure detail it never
  emits. Zero non-Latin characters reached the file.
- **Encoding has TWO ends on Windows and both must be named.**
  `PYTHONIOENCODING=utf-8` makes Python emit UTF-8;
  `[Console]::OutputEncoding` decides how PowerShell decodes it. Set only the
  first and you get a capture whose numbers are all correct and whose every Greek
  quotation is mojibake, with zero replacement characters, so nothing looks wrong.

## Session ritual

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1

# Both, always. See the traps above.
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
docker compose up -d db
litellm --config gateway/config.yaml --port 4000     # separate window

python -m ingest.run_embed --stats        # 450 / 450 / 0 pending
python -m eval.test_answer_eval           # 203
python scripts\mutate_part8.py            # 27
```

**Run `git` in PowerShell on the host, never through a mounted filesystem.**
`git rev-parse` and `git hash-object` are lock-free and safe; `git status` is not.

**Commit before running any mutation harness.** This block already lost a
completed task to a restore command that could not tell uncommitted work from
line-ending churn.

## Housekeeping left undone

`_to_delete/` holds three staging tarballs from the 2026-08-22 session —
`f10.tgz`, `f10-guarded.tgz`, `mu-sub.tgz` — alongside three older files. The
directory is gitignored; nothing depends on any of it.

## The sentence that still travels with all of it

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310. The W2b distractor
curve still rests on English-only padding.

**And one more, earned today: the answer path has never quoted a non-English
source text.** 45 of 45 resolved spans across 16 runs came from the English,
while the Chinese chunk sat at `[S1]`. That is not retrieval and it is not the
corpus — the corpus was corrected and nothing moved. Nothing in the prompt ever
asks for the source text, and rule 3 permits either. Block E will measure a
system that reads its sources in translation.
