# D4 pilot — five gold cases across two real days

*Written 2026-08-24. TASK 3 item 4: "pilot on 5 cases across 2 days, ~30 chat
calls, so the three-day sweep is not the first time this code runs across a date
boundary." This is that pilot, and it is insurance on a 270-call artefact.*

**Do not start this until D4-A, D4-B, D4-C and D4-D are committed and all four
suites are green.** The pilot is Block E's dress rehearsal. Rehearsing against
an uncommitted tree, or against a harness whose own guards have not been
watched failing, is how a floor gets calibrated to a fiction — and this
repository has done that twice.

---

## Preconditions, checked before anything is spent

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1

# Both, always. PYTHONIOENCODING makes Python emit UTF-8; [Console]::OutputEncoding
# decides how PowerShell decodes it. Set only the first and you get a capture
# whose numbers are all correct and whose every Greek quotation is mojibake,
# with zero replacement characters, so nothing looks wrong.
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
docker compose up -d db
litellm --config gateway/config.yaml --port 4000     # separate window
```

```powershell
git status                              # MUST be clean
python -m ingest.run_embed --stats      # 450 / 450 / 0 pending
python -m eval.test_answer_eval         # 248
python -m eval.test_ranking_check       # 226
python scripts\mutate_part8.py          # 48
python scripts\mutate_ranking.py        # 95
```

A red suite here stops the pilot. So does an unclean tree.

---

## The six cases, and why these six

TASK 3 says five. This is six, and the sixth is `adulis-exports`.

| case | behaviour | what a cross-session observation buys |
| :---- | :---- | :---- |
| `antikythera-absent` | correctly_refusable | a required case; the refusal arm across a date boundary |
| `chinese-da-qin` | answerable | a required case; 16 archived runs to compare against |
| `muziris-cargo` | answerable | a required case |
| `vimose-runes` | refusable_with_gloss | **the case that flipped.** 3/3 then 0/3 on 2026-08-10 against a byte-identical evidence block. The per-session number exists because of this case |
| `aksum-exports` | answerable, known-failing | seven consecutive failures under four prompts, every one of them within-session or a single shot. The failure is **unexplained**, so cross-session data can actually move it |
| `adulis-exports` | answerable | the other half of the pair. Enforced at LOAD, not at run — so running `aksum-exports` alone is mechanically fine and evidentially half a measurement |

`weilue-chinese-quotation` is deliberately **out**. It fails for a fully
explained structural reason — prompt rule 3 permits either text and requires
neither — and nothing in the pilot changes the prompt, so six more observations
would reproduce what `floor.json` already states. An explained failure cannot
move; an unexplained one can.

`adulis-exports` is in because the aksum/adulis pair is the entire argument for
the persevere verdict at the Phase 1 exit gate: *the system refused a question
whose answer it was holding, and answered it correctly when the question was
reworded against byte-identical evidence.* That claim has never been observed
across a date boundary. If aksum fails both days and adulis passes both days,
the founding claim of this phase stops being an anecdote about one afternoon.
If adulis starts failing, that is a large finding bought for six chat calls.

**Cost: 6 cases x 3 repetitions x 1 prompt version = 18 chat calls per day, 36
in total.** Drop `--case adulis-exports` from both days for the literal 30.

The prompt version is not passed, so it defaults to
`assemble.ANSWER_PROMPT_VERSION`, which is `p7-answer-v2r` — the same version
`floor.json.calibrated_from` was measured under, and the same one Block E will
default to. **Run the pilot the way Block E will be run**, or it is not
insurance on that path.

---

## Day 1

```powershell
python -m eval.run_answer_sweep --dry-run `
  --case antikythera-absent --case chinese-da-qin --case muziris-cargo `
  --case vimose-runes --case aksum-exports --case adulis-exports
```

Six embedding requests, no chat call. Read three things before spending
anything:

1. **the session line** — `session: <12 hex>  2026-08-24 (UTC)`. If this is
   missing, D4-C is not in the tree.
2. **the corpus line** — `corpus: 24 seed record(s), digest 26e4a68301…
   (database)`. If this is missing, D4-D is not in the tree. **Write the digest
   down.** It is the number day 2 must reproduce.
3. **`aksum-exports`'s evidence block.** The dry run prints, per passage,
   whether each gold term is present in that passage's English. Three of the six
   Aksum passages carry gold terms. If the Aksum record is not in the set, the
   pilot is measuring a retrieval failure and not the defect.

Then:

```powershell
python -m eval.run_answer_sweep --repeat 3 --session-label "D4 pilot day 1" `
  --case antikythera-absent --case chinese-da-qin --case muziris-cargo `
  --case vimose-runes --case aksum-exports --case adulis-exports `
  *> eval\d4-pilot-day1.txt
```

18 chat calls. Redirected on purpose: this is the first sweep ever run under the
FINDING 10 stdout guard, and answers quoting Greek, Tamil and Chinese are
exactly what would have killed it before 2026-08-22. **A run that completes
under a redirect is itself a result** — check the file has non-Latin characters
in it and no traceback:

```powershell
Select-String -Path eval\d4-pilot-day1.txt -Pattern 'Traceback|UnicodeEncodeError'
(Get-Content eval\d4-pilot-day1.txt -Raw) -match '[^\u0000-\u024F]'
```

The second must be `True`. A green run that printed only `ok` lines in English
proves nothing about non-Latin output — that is the vacuous proof from
FINDING 10, and it cost an hour once already.

Expected in the report:

```
per-case     6/6 = 100%   (or fewer, and that is data)
per-session  NOT MEASURED — no case was seen in two sessions
```

`NOT MEASURED` is the correct answer on day 1 and the whole reason the number is
printed rather than a rate. One sweep is one session.

---

## Between the days: change NOTHING

Not a prompt, not the corpus, not retrieval, not the gateway, not
`gateway/config.yaml`, and not `scripts/schema-part7.sql`. Do not commit code
between day 1 and day 2. A change on day 2 turns two observations into one.

Writing `D4_RESULT.md` is fine — it is prose and touches no path a sweep runs
through.

---

## Day 2 — a different calendar date, not merely a different hour

```powershell
python -m eval.run_answer_sweep --repeat 3 --session-label "D4 pilot day 2" `
  --case antikythera-absent --case chinese-da-qin --case muziris-cargo `
  --case vimose-runes --case aksum-exports --case adulis-exports `
  *> eval\d4-pilot-day2.txt
```

The corpus digest printed at the top must be the same one you wrote down on day
1. If it is not, the pilot has found a moving corpus and that is the finding —
stop and record it rather than proceeding.

---

## After day 2 — the number the pilot exists to produce

```powershell
python -m eval.calibrate_floor
```

Expect it to **refuse**, and to be right about why:

```
distinct dates     2 (floor requires 3): 2026-08-24, 2026-08-25
distinct sessions  2

REFUSED. `calibrated: true` may NOT be written:
  - 2 distinct date(s), and the floor requires 3. ...
  - 3 sweep(s) carry no session identity and count toward no date. ...
```

Those three pre-D4 sweeps blocking calibration is correct behaviour, not a
nuisance: a date assigned to them after the fact is exactly the calibration
`floor.json` already records as invalid.

And **per-session stability is now a real number** for the first time in this
project's life:

```
per-case     n/n
per-session  n/n   <- the number that did not exist before today
```

---

## What would be a finding

- **`vimose-runes` disagrees across the two days.** That is the 2026-08-10
  observation reproduced deliberately, on a harness that can now name it. It
  would make the per-session number the headline of Block E rather than a
  footnote.
- **`aksum-exports` passes.** Seven consecutive archived failures and then a
  pass across a date boundary would mean the defect is session-shaped and not a
  property of the question. Record it; do not record it as closed.
- **`adulis-exports` fails.** The half that has always worked, against evidence
  byte-identical to the half that never has.
- **The corpus digest differs between the days.** The sweep now says so and
  exits 2.
- **Either known-failing case is reported as passing by the floor check.** A
  sweep that reports them passing is a finding, not a success.

## What is NOT a finding

`aksum-exports` and `weilue-chinese-quotation` failing. Both are tracked in
`floor.json.known_failing_cases` as **open defects**, both are out of
`required_cases`, and neither is closed by D4. They are reported beside the
floor verdict and never subtracted from it.

---

## The sentence that travels with all of it

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310, and the answer path
has still never quoted a non-English source text — 45 of 45 resolved spans came
from the English while the Chinese chunk sat at `[S1]`.

The pilot measures none of those. It measures whether this harness can tell a
session from a repetition, which is the one thing Block E's 270 calls cannot be
believed without.
