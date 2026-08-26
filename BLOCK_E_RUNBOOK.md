# Block E — runbook

*Written 2026-08-26, before day 1. Sits under `BLOCK_E_START.md`, which is still
the statement of what Block E is. This is what to DO, in order, and what was
decided before any of it was run.*

---

## The decisions, settled 2026-08-26

All settled before day 1 for the reason `BLOCK_E_START` gives: the rule
between days is *change nothing*, so anything unsettled on day 1 stays
unsettled for all three days or costs the whole sweep. Four were the decisions
`BLOCK_E_START` named; the fifth was found by reading the sweep path against a
99-call day.

| # | decision | where it now lives |
| :---- | :---- | :---- |
| 1 | `vimose-runes` **demoted**, on two dates of evidence | `floor.json` `demotions` + `known_failing_cases` |
| 2 | **Two** decompositions — verdicts and answer text | `eval/answer_eval.py`, `eval/decompose.py` |
| 3 | Serving stack: **probe first, record what is real** | `answer/translate.py` `_serving_stack`, `scripts/probe_serving_stack.py` |
| 4 | Calibration scope: **exclude by a recorded rule**, keyed on the case set | `floor.json` `calibration_scope` |
| 5 | One failed call is **retried once, then named** — it must not take the day | `eval/run_answer_sweep.py` |

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

### 3a. What the probe actually returned, 2026-08-26

Run once before day 1, one chat call, against the gateway:

```
{
  "id":    "chatcmpl-069dc421-2111-449c-ae1f-c40719f19cf1",
  "model": "anthropic/claude-haiku-4-5-20251001"
}
```

No `system_fingerprint`, no `service_tier`, no LiteLLM `model_id` or
`custom_llm_provider`. **This is a null result and it is decision 3's answer.**

Read what the two keys are worth, because it is less than it looks:

- `id` is unique per call. It traces one archived answer back to one request.
  It is **not** provenance: it says nothing about what served it.
- `model` is the alias echoed back, byte-identical to what was sent. It
  **cannot move**, so it cannot report drift.

**So nothing in the Block E archives can distinguish provider-side drift from
sampling variance, and FINDING 18's question cannot be answered by this block.**
That has to be stated in the result document as a limit that was measured
before day 1, not discovered after day 3.

One thing does cut the other way and belongs beside it: `chat-default` points
at `anthropic/claude-haiku-4-5-20251001`, a **dated** model id, not a floating
alias. A dated id is a stronger guarantee against a silent model swap than a
fingerprint on an undated alias would be. It does not rule out serving-stack
changes underneath a fixed model id, and nothing available here does.

### 3b. Why the answer path runs haiku and not sonnet

Asked on 2026-08-26 and worth writing down, because it will be asked again.

**Sonnet has never been measured on the answer path.** All 115 archived answer
runs are `anthropic/claude-haiku-4-5-20251001`; there is no sonnet arm to
compare against, and no such comparison exists anywhere in this repository.

What *was* measured on sonnet is **Block C2's query renderings** — the
retrieval-side translation of a query into a target language, not answer
generation. `chat-strong` was added to `gateway/config.yaml` on 2026-08-16
because all sixteen script-guard refusals under haiku were Old Tamil. Even
there it is not a clean win: **ruling 23a** records the selection regime as
uneven — Old Tamil rows were drawn twice, haiku then `chat-strong`, every other
language once — so *"any per-language number taken from this file has to say
so"*, and one Adulis row is the case where the sonnet draw was promoted. C2 as
a whole moved the non-English-reachability number **down**, 21/30 to 20/30.

Three reasons the alias does not move for Block E:

1. **Ruling 22: `claude-sonnet-5` refuses `temperature=0`** — a bare 400,
   *"Only temperature=1 is supported"*, found after 615 spent requests. The
   answer path sends 0 because a measurement that cannot be reproduced cannot
   be compared. Running Block E on sonnet means sampling at temperature 1,
   which puts the sampler **into** the variance this block exists to
   decompose — and 3a has just established that nothing in the archive could
   separate it back out again.
2. **Every archived number would become incomparable.** The floor,
   `calibration_invalidated`, the 2026-08-10 pair, both D4 pilots and all 115
   archived runs are haiku at temperature 0. `gateway/config.yaml` says it in
   its own comment: repointing `chat-default` would silently make every
   archived number incomparable, which is why `chat-strong` is a second alias
   and not a replacement.
3. **The corpus and retrieval are frozen for this block.** The model is part of
   that freeze whether or not the plan spells it out.

**The real question this exposes is a good one, and it is Block F's or later.**
Nobody has asked whether the answer path is *model-limited*. `aksum-exports`
fails 0/3 across four prompts and seven archived runs with the answer sitting
in published English in its own evidence block, and
`weilue-chinese-quotation` has never once quoted a source text. Both are
attributed to prompt and retrieval. A sonnet arm at temperature 1, run
**beside** the frozen haiku archive and never folded into it, is the experiment
that would test that attribution. It needs its own gate and its own repetitions
because it cannot be greedy, and it must not touch Block E.

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

### 5. One failed call must not take the day — added 2026-08-26, before day 1

Found by reading the sweep path against a 99-call day rather than an 18-call
one. `run_sweep` caught `EmbeddingError` and returned cleanly, and left the
chat call **unguarded**. `_chat` gives up after `MAX_RETRIES = 3`; for an
unclassified provider error the backoff is 2s then 4s, so **six seconds of
trouble is enough**, and `TranslationError` then propagated out of `main()`.
It died AFTER writing N per-run archives and BEFORE writing the sweep archive
that ties them together — the orphan state this document already warns about
from Ctrl-C, reachable without touching Ctrl-C. D4's two 18-call sweeps never
went near it.

`PHASE2_PLAN` item 4 decides it: *the days are the scarce resource, not the
calls.* A guard costing forty-five minutes against a failure costing a booked
day is not a close call.

What it does now:

```
a call fails        NAMED, the sweep continues — abandoning would GUARANTEE
                    the loss the retry usually prevents
at the end          each failed cell is retried ONCE, over the SAME evidence
                    block (retrieval was built once per case, so a retry is
                    the same measurement), and at the end rather than in place
                    because whatever failed is likelier to have passed in ten
                    minutes than in six seconds
it succeeds         the row carries `retried_after_failure`. A run that had to
                    be asked twice is never indistinguishable from one that
                    did not
it fails again      the sweep is INCOMPLETE. Everything that completed is
                    archived, the cells that never returned are NAMED with
                    both errors, NO floor verdict is computed or archived, and
                    it exits 2
```

Refused from both ends, because an incomplete day has the full case set and a
hole in its grid:

- `run_answer_sweep` computes no floor verdict — one would be a floor met on a
  different denominator, printed in the same words;
- `calibration_eligibility` refuses an incomplete sweep by name;
- `decompose_verdicts` already refuses an incomplete grid and names the cells.

Tested **behaviourally**, not by reading the source like the FINDING 14 checks
above it. Those assert that a line exists; this is control flow, and a
line-exists check on control flow is the vacuous proof in a new costume.

---

## The three dates, booked in advance

```
day 1   Wednesday 2026-08-26  (UTC)   <- amended
day 2   Saturday  2026-08-29  (UTC)
day 3   Monday    2026-08-31  (UTC)
```

**Amended 2026-08-26 at 10:00 UTC, before day 1 and before any Block E call.**
Booked earlier the same morning as 27 / 29 / 31. Moving day 1 forward gives
gaps of three days then two — *wider* spacing than the booking it replaces —
and no Block E number existed when it was changed, so this is a decision taken
in advance and not a date chosen after seeing a result. Recorded here rather
than silently edited, because a booking that can be moved without a note is
not a booking.

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
eval/run_answer_sweep.py one failed call is retried once and then NAMED;
                         an incomplete sweep gets no floor verdict, exits 2
eval/test_answer_eval.py       248 -> 283
eval/test_ranking_check.py     226 -> 231
scripts/mutate_part8.py         48 -> 61
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
python -m eval.test_answer_eval          # expect 283 passed, 0 failed
python -m eval.test_ranking_check        # expect 231 passed, 0 failed
python scripts\mutate_part8.py           # expect all 61 mutations verified
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

**Budget 35 to 65 minutes.** The sweep makes one embedding request per case
and Voyage's free tier is 3 per minute, so 33 cases is about **11 minutes of
embeddings alone** — and the dry run spends the same 33 again. D4's six cases
took two minutes, which is why this was invisible until now. The 99 chat calls
then took between 7 and 39 minutes at D4's two observed rates.

The corpus line must read `26e4a683014bdf8a…` on all three days. If it does not,
the sweep says so and exits 2 — that is the finding, and it stops the block.

**Watch progress from a SECOND window.** `*>` redirects every stream, so the
console looks dead for the whole run:

```powershell
(Get-ChildItem eval\answer_runs\20260826*.json).Count      # 99 when done
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
       2026-08-26, 2026-08-29, 2026-08-31
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
- **A `git` command run through the bridge leaves `.git/index.lock` behind.**
  Even a read-only-looking `git status` takes the index lock to refresh it,
  the bridge cannot delete files, so the lock survives, and every later
  `git add` / `git commit` fails with *"Another git process seems to be
  running"* — with no git process running. Delete it on the host:
  `Remove-Item .git\index.lock`. **This happened twice on 2026-08-26, the
  second time after the trap had already been written down**, which is the
  argument for the flag rather than the discipline: `git --no-optional-locks
  status` exists precisely for a read-only caller and takes no lock. Use it,
  or do not run git through the bridge at all.
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
