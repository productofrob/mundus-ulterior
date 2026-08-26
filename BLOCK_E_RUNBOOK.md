# Block E — runbook

*Written 2026-08-26, before day 1. Sits under `BLOCK_E_START.md`, which is still
the statement of what Block E is. This is what to DO, in order, and what was
decided before any of it was run.*

---

## The four decisions, settled 2026-08-26

All four were settled before day 1 for the reason `BLOCK_E_START` gives: the
rule between days is *change nothing*, so anything unsettled on day 1 stays
unsettled for all three days or costs the whole sweep.

| # | decision | where it now lives |
| :---- | :---- | :---- |
| 1 | `vimose-runes` **demoted**, on two dates of evidence | `floor.json` `demotions` + `known_failing_cases` |
| 2 | **Two** decompositions — verdicts and answer text | `eval/answer_eval.py`, `eval/decompose.py` |
| 3 | Serving stack: **probe first, record what is real** | `answer/translate.py` `_serving_stack`, `scripts/probe_serving_stack.py` |
| 4 | Calibration scope: **exclude by a recorded rule**, keyed on the case set | `floor.json` `calibration_scope` |

### 1. vimose-runes

Out of `required_cases`, into `known_failing_cases`, with a `demotions` record
carrying the evidence (0/3 on 2026-08-24 **and** 0/3 on 2026-08-25), the
diagnosis (retrieval margin: its own gold record third at 0.384, behind two
unrelated Arabian inscriptions at 0.433 and 0.401), and what would put it back.

It is **reported for ever and never subtracted**, exactly like `aksum-exports`
and `weilue-chinese-quotation`. A sweep that reports it passing is a finding,
not a success.

`eval/goldset.py` now **refuses** a demotion that omits evidence, a diagnosis,
or a written condition for return. That is what stops the next demotion being
a floor quietly lowered to whatever is currently passing — the three fields are
the only thing separating the two acts, and now they cost something to skip.

### 2. The variance decomposition — G4's deliverable

Two response variables, printed together, because **the pair is the finding**:

```
decompose_verdicts   components of variance on content_ok, case x session
                     crossed, balanced two-way random effects with interaction.
                     "When the VERDICT moves, what moved it."

decompose_texts      a partition of pairwise agreement over the answer TEXT:
                     within-session, across-session, and a cross-case baseline.
                     "When the OUTPUT moves, what moved it."
```

Run against the two D4 pilot archives **before** any Block E call, it reproduces
FINDING 18 as arithmetic:

```
VERDICTS      case 100.0%   session 0.0%   case_x_session 0.0%   residual 0.0%
ANSWER TEXT   within a session  28/36 = 78%
              across sessions    9/54 = 17%
              different case     0/540 = 0%      <- no shared refusal template
              agreement lost at the session boundary: +61%

              byte-identical in every session: muziris-cargo
              shared NOTHING across sessions:  the other five
```

Both stability rates read 100%. The verdict decomposition puts **nothing** on
the session term. The text decomposition says agreement collapses at the
session boundary. A report carrying only the first would have called this
stable, which is precisely what FINDING 18 exists to refuse.

Three refusals worth knowing about, because they are what make the number
mean something:

- it **refuses to pool two prompt versions** (that would charge the difference
  between two prompts to the residual and report it as sampling noise — and
  Part 8's two-version grid is on disk);
- it **refuses an unbalanced or incomplete grid** (the balanced estimators are
  not those expressions on one, so a day that lost a case to a rate limit is
  refused rather than quietly apportioned);
- it **reports a negative component estimate rather than clamping it in
  silence**, and prints NOT MEASURED — never 0% — when total variance is zero.

### 3. Serving stack

`BLOCK_E_START` called this "one line". It is not: `_chat` returns a
three-tuple and has six call sites plus two in the suites, and the last time
its arity moved one call site was missed and every live answer call raised
`ValueError` for five days.

So it went in as an **out-parameter**, which touches one other call site and
leaves the other five untouched. `_serving_stack` records `id`, `model`,
`system_fingerprint`, `service_tier` and LiteLLM's `model_id` /
`custom_llm_provider` — **omitting any key the gateway did not populate**,
rather than writing null.

`system_fingerprint` is an OpenAI field and this gateway fronts Anthropic, so
it may be absent on every call. A column reading null 270 times would be the
fourth vacuous proof in five days. `scripts/probe_serving_stack.py` costs one
chat call and says which — **run it before day 1**, and again after day 3.

The sweep now prints, per day, whether one stack served the whole sweep or
several, and archives the distinct stacks beside `corpus_version` — the same
treatment, for the same reason.

### 4. Calibration scope

The thing `BLOCK_E_START` did not know: `calibrate_floor` refused on **any**
undated sweep, and three undated sweeps are on disk permanently. So
`calibrated: true` was unreachable at **any** number of dates, not merely
blocked until three. D4's report never showed it, because it refused on the
date count first and stopped reading.

`floor.json.calibration_scope` now states one rule that handles both that and
the pilots:

> A sweep contributes to calibration only if it carries a session identity AND
> ran at least 30 cases. A sweep that fails the rule blocks calibration
> outright UNLESS it is named in `excluded_by_rule`, with the reason written
> beside it.

All five archived sweeps are named. **And a sweep that SATISFIES the rule
cannot be excluded by name** — that refusal is the anti-loophole, and without
it the list is a place to put a sweep whose numbers nobody liked.

The two pilots are excluded from **calibration only**. They keep their session
identity, they count toward both stability numbers, and they are the archives
the decomposition was built and mutation-verified against.

**The floor therefore becomes writable on day 3, from three homogeneous
33-case dates with one denominator — not on day 1.**

Today, `python -m eval.calibrate_floor` reports:

```
  distinct dates     0 (floor requires 3): none
  eligible sweeps    0
    excluded by rule  <all five, each with the reason it fails>
  REFUSED. calibrated: true may NOT be written:
    - 0 distinct date(s), and the floor requires 3.
```

---

## The three dates, booked in advance

```
day 1   Thursday  2026-08-27  (UTC)
day 2   Saturday  2026-08-29  (UTC)
day 3   Monday    2026-08-31  (UTC)
```

You are UTC+1. **A session must sit wholly inside its own UTC date**: start
after 01:00 BST and finish before 01:00 BST the following morning. An ordinary
evening run is fine. A run started at half past midnight is on the *previous*
UTC date, and `crossed_midnight_utc` will say so.

D4's gap was 31 hours, midday to evening, and that was enough. Midday-to-midday
is not required.

---

## What changed in the tree today

```
answer/translate.py      _serving_stack(); _chat gains a `provenance` out-param
answer/assemble.py       captures it; AssembledAnswer.serving_stack
answer/run_answer.py     serving_stack into the per-run archive
eval/run_answer_sweep.py serving_stack on the row AND in the archive; the sweep
                         reports whether one stack or several served it
eval/answer_eval.py      decompose_verdicts, decompose_texts,
                         print_decomposition; calibration_eligibility gains the
                         scope rule and takes archive names
eval/calibrate_floor.py  passes the names; writes calibrated_stability from the
                         sweeps the scope ALLOWED; its last line no longer
                         contradicts its own refusal   <- open defect, closed
eval/decompose.py        NEW. the decomposition, from the archives
eval/goldset.py          refuses a demotion missing evidence / diagnosis /
                         condition for return; refuses an unexplained exclusion
eval/gold/floor.json     vimose-runes demoted; demotions; calibration_scope
scripts/probe_serving_stack.py  NEW. one chat call (+ the sys.path line every
                         script under scripts/ needs to import a package)
eval/test_answer_eval.py       248 -> 274
eval/test_ranking_check.py     226 -> 231
scripts/mutate_part8.py         48 -> 60
scripts/mutate_ranking.py       95 -> 97
```

---

## Before day 1 — on the host, in PowerShell

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1

$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
docker compose up -d db
litellm --config gateway/config.yaml --port 4000     # separate window
```

Then, in this order. **Nothing after this point changes until day 3 is
archived.**

```powershell
python -m eval.test_answer_eval          # expect 274 passed, 0 failed
python -m eval.test_ranking_check        # expect 231 passed, 0 failed
python scripts\mutate_part8.py           # expect all 60 mutations verified
python scripts\mutate_ranking.py         # expect all 97 mutations verified

python -m eval.decompose                 # FINDING 18, reproduced from the archives
python -m eval.calibrate_floor           # expect REFUSED, 0 eligible dates

python scripts\probe_serving_stack.py    # ONE chat call. read what it prints.
python -m ingest.run_embed --stats       # 450 / 450 / 0

git add -A
git commit -F commit-blocke-prep.txt
git status                               # MUST be clean before day 1
```

`probe_serving_stack.py` decides nothing that changes the code — the recording
already omits absent keys either way. It decides what goes in the **result
document**, and "the gateway returns nothing distinguishing beside the model
alias" is a finding worth stating, not a gap to leave unexplained.

---

## Each day — exactly as D4 rehearsed it

```powershell
python -m eval.run_answer_sweep --dry-run          # embeddings only, no chat call

python -m eval.run_answer_sweep --repeat 3 --session-label "Block E day N" `
  *> eval\block-e-dayN.txt
```

The corpus line must read `26e4a683014bdf8a…` on all three days. If it does not,
the sweep says so and exits 2 — that is the finding, and it stops the block.

**Watch progress from a SECOND window.** `*>` redirects every stream, so the
console looks dead for the whole run:

```powershell
(Get-ChildItem eval\answer_runs\20260827*.json).Count
```

33 cases x 3 repetitions = **99 chat calls per day**, about 297 across the
block. Do not Ctrl-C: a half-finished sweep leaves orphan per-run archives and
no sweep archive tying them together.

After each day:

```powershell
python -m eval.decompose                 # the block so far
python -m eval.calibrate_floor           # still REFUSED until day 3
git add -A ; git commit -F commit-blocke-dayN.txt
```

---

## Day 3 — closing the block

```powershell
python -m eval.decompose --write          # G4: "with the data archived"
python scripts\probe_serving_stack.py     # compare against the day-1 reading
python -m eval.calibrate_floor            # read the refusal block, if any
python -m eval.calibrate_floor --write    # only if the report above is ELIGIBLE
```

Gate G4, and where each box is answered:

```
[x] >=30 cases, each with an explicit expected behaviour
       33 cases: 22 answerable / 3 gloss / 8 correctly_refusable
[ ] run 3x on >=3 separate days
       2026-08-27, 2026-08-29, 2026-08-31
[ ] per-case and per-session stability as separate numbers
       eval/answer_eval.py stability(), printed by every sweep
[ ] a stated VARIANCE DECOMPOSITION, with the data archived
       eval/decompose.py --write  ->  eval/decompositions/
[ ] the floor recalibrated and calibrated: true, OR the reason it cannot be
       eval/calibrate_floor.py --write, over three in-scope dates
```

**The deliverable is the decomposition, not the pass rate.**

---

## Traps

Everything in `BLOCK_D_START.md`, `D4_START.md` and `BLOCK_E_START.md` still
applies. Two to add, both learned on 2026-08-26:

- **Never run a mutation harness through the Linux device bridge.** Each
  `device_bash` call is killed at 45 seconds, the harness restores its sources
  in a `finally` that then never runs, and the tree is left with a live
  mutation in it. It happened today: `eval/goldset.py` was left with
  `if False:` in place of the refusable-label guard, and the suite reported
  262 -> 258 passing with no obvious cause. Restore with
  `git cat-file blob HEAD:<path>`, not `git checkout` — the bridge cannot
  delete `.git/index.lock`. Run these on the host, or on a copy.
- **A `git` command run through the bridge can leave `.git/index.lock` behind.**
  The bridge cannot delete files, so the lock survives and every later
  `git add` / `git commit` fails with *"Another git process seems to be
  running"* — with no git process running. Delete it on the host:
  `Remove-Item .git\index.lock`. Read the working tree first, and do not run
  git through the bridge at all where a write lock is possible.
- **A script under `scripts/` that imports a repository package needs
  `sys.path.insert(0, ...)` on the root.** `python scripts\x.py` puts
  `scripts/` on the path and not the root. Every other script here carries the
  line (`scripts/probe_rerank.py:22`); `probe_serving_stack.py` shipped without
  it and raised `ModuleNotFoundError` before spending its one chat call. The
  offline suites import the packages directly and never exercise this path, so
  nothing green would have caught it.
- **`eval/goldset.py` and the two `answer/` modules are CRLF; everything else
  in `eval/` is LF.** An edit that writes LF into a CRLF file leaves it mixed,
  and `scripts/mutate_part8.py` refuses to run at all on a mixed source rather
  than picking one — which is the right behaviour and cost twenty minutes to
  read. Match the file, do not normalise the repository.

## What is NOT a finding

`aksum-exports` and `weilue-chinese-quotation` failing. Both are open defects,
both are out of `required_cases`, and neither is closed by Block E. As of today
`vimose-runes` joins them under the same rule. All three are reported beside
the floor verdict and never subtracted from it.

## The sentence that still travels with all of it

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT
was reachable. `muziris-cargo-akananuru` still sits at rank 310, and the answer
path has still never quoted a non-English source text.

Block E measures none of those. It measures whether the answers this system
gives can be improved on purpose.
