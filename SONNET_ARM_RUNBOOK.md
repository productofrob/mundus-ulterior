# The sonnet arm — runbook

*Written 2026-08-28, in the F1 thread, before F1 curates anything. `F1_START.md`
names this as THE ONE DEADLINE and says it is not F1's. It is not: F1 and F2 do
not move the corpus, **F3 does**, and the arm has to be measured beside the
frozen archive `26e4a683` or it is measuring something else.*

## The question it answers

**Is the answer path model-limited?** Runbook 3b posed it and Block E ruled it
out of scope. `aksum-exports` fails 0/3 under four prompts with the answer
sitting in published English in its own evidence block, and that has been
attributed to prompt and retrieval on no evidence either way.

```
33 cases x 5 repetitions, temperature 1, alias chat-strong, ONE session
~165 chat calls + 33 embedding requests. Archives to eval/arms/, never sweeps/
Its own gate, its own repetitions, its own numbers.
```

Five repetitions and not three because it cannot be greedy: ruling 22 records
that `claude-sonnet-5` refuses `temperature=0` with a bare 400. Full case set
and not a targeted subset, because a targeted arm answers "is THIS CASE
model-limited" and cannot answer the question above.

## What changed today, before the first call

Ruling 36 had not reached the runner. `main` computed `check_floor` for whatever
arm had just run, printed MEETS / BELOW THE FLOOR in the words of a real
verdict, archived it under `floor`, and returned it in the **exit code** — so
this run was one command away from exiting 1 for failing a floor calibrated on
greedy haiku, and `eval/arms/` would have kept that verdict permanently.

Closed in `commit-f14.txt`: three pure functions (`floor_scope_arm`,
`floor_applies`, `exit_code`), seven checks, four mutations. A foreign arm now
gets no verdict at all, the archive says which arm and why in
`floor_not_applicable`, and the exit code carries no floor claim.

## Pre-flight — window 2, offline, before anything is spent

Paste the `STARTUP.md` block first. The tree is NOT clean: three files are
modified and `commit-f14.txt` is written and unstaged.

```powershell
python -m eval.test_answer_eval          # 328 passed, 0 failed   (was 321)
python scripts\mutate_part8.py           # all 79 mutations verified (was 75)
python -m eval.test_ranking_check        # 236
python -m answer.test_answer             # Part 7
python ui\test_build_ui_data.py          # UI
python scripts\mutate_part7b.py          # 18
python scripts\mutate_ui_places.py       # 4
python scripts\mutate_ranking.py         # 100
```

**Watch for the words `BASELINE:` and `UNVERIFIED` in the three harnesses that
now print them.** Either word means a mutation named a guard that was already
red — fix the suite before believing any `ok` in that run.

**Check `git diff --stat` after any harness run.** A file whose every line
changed is the LF-to-CRLF conversion defect of 2026-08-28, not your edit.

Then commit, so the arm runs from a clean tree:

```powershell
git add -A
git commit -F commit-f14.txt
git status          # clean
```

## The gateway — window 1

```powershell
docker compose up -d db
python scripts\check_db.py                        # pgvector installed: True
litellm --config gateway/config.yaml --port 4000  # leave running
```

`chat-strong` is already in `gateway/config.yaml` as `anthropic/claude-sonnet-5`.
If LiteLLM rejects that string, paste the dated model id in its place — the
provenance column records what actually answered either way.

## The smoke test — one chat call, nothing archived

Do not skip this. It proves the alias resolves, that temperature 1 is accepted,
and that the new no-verdict path prints, for the cost of one call rather than
forty minutes.

```powershell
python -m eval.run_answer_sweep --case chinese-da-qin --repeat 1 `
  --model chat-strong --temperature 1 --session-label "sonnet arm smoke" --no-write
```

It must print, in this order:

```
arm: chat-strong at temperature 1.0   NOT THE DEFAULT ARM
  archives to ...\eval\arms and NOT to ...\eval\sweeps.
corpus: 24 seed record(s), digest 26e4a683014bdf8a...
NO FLOOR VERDICT - this sweep is on another arm
  this floor calibrates from  chat-default at temperature 0   (declared)
  this sweep ran on           chat-strong at temperature 1
```

**If it prints MEETS THE FLOOR or BELOW THE FLOOR, stop.** The fix did not take
and the run would archive a verdict it must not.

## The run

```powershell
python -m eval.run_answer_sweep --repeat 5 `
  --model chat-strong --temperature 1 `
  --session-label "Block F sonnet arm" --progress `
  *> eval\sonnet-arm.txt
```

**Budget 45 to 90 minutes.** 33 embedding requests at Voyage's free 3/min is
~11 minutes before a single chat call is made; 165 sonnet calls then take
between 20 and 70 minutes at Block E's two observed rates.

Watch it from a THIRD window — `*>` redirects every stream, so the console
looks dead for the whole run:

```powershell
Get-Content eval\sonnet-arm.txt -Wait -Tail 5
```

Or count the archives. **99 runs are already dated 20260828** (the fourth haiku
session ran this morning), so the number to watch is 99 -> 264:

```powershell
(Get-ChildItem eval\answer_runs\20260828*.json).Count
```

## What stops the run, and what is merely a result

**STOPS IT.** The corpus line reading anything but `26e4a683014bdf8a...`. The
sweep says so and exits 2, and it stops the block — not just the arm.

**STOPS IT.** `INCOMPLETE — N cell(s) never returned`. Exit 2, no verdict, no
decomposition. The completed runs are real and are archived; they are not a
shorter sweep.

**NOT a defect.** `aksum-exports`, `vimose-runes` or `skz-titulature` passing.
On the greedy archive that is a finding rather than a success. **On this arm it
is the RESULT** — it is the whole question the arm was run to answer, and it
does not move the floor, which is calibrated on another arm and says so.

**Expected, not a fault.** Rate-limit failures retried once and named; a
`retried_after_failure` row is never indistinguishable from a clean one.

## After

1. `eval\arms\<stamp>-p7-answer-v2r-r5-chat-strong-t1.json` exists, and
   `eval\sweeps\` has gained nothing.
2. `python -m eval.calibrate_floor` still reports ELIGIBLE, four sweeps, three
   dates. **The arm must not have changed it.** If it did, something is reading
   `eval/arms/`, and that is a finding about the guard rather than about the arm.
3. The numbers to read beside the haiku archive: content pass rate against
   `0.727272...`, the per-case cells for the three known-failing cases, refusal
   rate, and the two stability figures — which read NOT MEASURED per session,
   because one sweep is one session.
4. Then F1, which does not move the corpus.
