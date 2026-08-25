# Block D — starting point for the next thread

*Written 2026-08-20 at the close of C7. Supersedes `C7_START.md`, whose three tasks are all done. Block C is closed and committed. Every number here was measured on the host or read out of a file on it.*

## Read these, in this order

| # | file | why |
| :---- | :---- | :---- |
| 1 | **this file** | state, the four tasks, and the one suite that is currently RED |
| 2 | `C7_RESULT.md` | what Block C ended at: ruling 26, 22/30, G2 at six of seven |
| 3 | `PHASE2_PLAN.md` **Block D, Block E, gate G4** | lines 399–503. The plan for this thread, written before any of it was measured |
| 4 | `eval/gold/floor.json` | read it whole. It is 900 words and four of them — `"calibration_invalidated"` — are the reason Block E exists |
| 5 | `PROGRESS.md` **on the host, last five sections only** | 580,817 bytes / 11,086 lines / 60 sections. Do not read it whole |

**`C7_START.md`, `C5_START.md` and `BLOCK_C_START.md` are done and are not needed.** Their traps are folded into this file.

**The copy of `PROGRESS.md` in the Claude project is STALE by ten days and 523 KB.** Read `…\mundus-ulterior\PROGRESS.md` on disk, tail-first.

## State, as measured 2026-08-20

```
tree          ccca17e, clean
              ccca17e  C7: the via-original sequencing fix, ruling 26, Block C closes
              744e57c  Block C: C5 and C6 run archives, ruling 25 documents
              bff0605  Block C: C2 measured and rejected; frozen config for C5-C6

corpus        24 documents / 59 chunks / 57 retrieval-eligible
index         450 in retrievable_chunks_with_distractors, 450 / 450 / 0 pending

RANKING       eval.test_ranking_check      218   GREEN
              scripts\mutate_ranking.py     91   GREEN

ANSWER        eval.test_answer_eval    68 passed, 2 FAILED   <- see TASK 0
              eval/gold/answer_cases.json          5 cases, need >=30
              eval/answer_runs/                   77 archived, 76 scored
              eval/sweeps/                         3 archived, all within-session
              eval/gold/floor.json          calibrated: false
```

Suites NOT run this session: `ingest.test_distractors`, `mutate_distractors`, `answer.test_answer`, `answer.test_translate`, `mutate_part7b`, `mutate_part8`, `ui\test_build_ui_data.py`, `ui\check_ui.mjs`. **Run them in TASK 0 before trusting any of them.**

## Where G2 landed, and why this thread is Block D and not Block F

G2 is **six of seven**. The gap criterion failed — `+0.019535` against a `+0.024927` baseline — and **ruling 25 pulled kill trigger 1, so W3 does not start** and the corpus is not chased to 200.

Ruling 25 named the follow-on work as *"the sourcebook at 24–60 records"*, which is Block F. **This thread takes Block D and then Block E instead, and the reason is a window that closes.** `PHASE2_PLAN` puts Block E *"in the window after G2 passes and before Block F touches the corpus"* — retrieval frozen, corpus frozen, corpus hash recorded. That window is open **right now** and it is the only stable thing this project will ever have to measure answer quality against. Growing the corpus first destroys it, and G4 would afterwards be measured against a moving target.

**Block F is not cancelled. It is second.**

---

# TASK 0 — the suite is red, and it is red about the right thing

```
eval.test_answer_eval    68 passed, 2 FAILED

FAIL  every archived run is scored (76 of 77)
FAIL  every archived question has a gold case
      ['20260812T133627+0000-53afe41c.json: What was exported from Adulis?']
```

**Both failures are one missing gold case, and it is the Adulis discriminator.**

`eval/gold/answer_cases.json` holds `aksum-exports` — *"What did Rome trade with the Kingdom of Aksum?"* — the question the system **refused**, seven consecutive times under four prompts. It does not hold *"What was exported from Adulis?"*, the rewording that **worked**, which sits unscored in `eval/answer_runs/20260812T133627+0000-53afe41c.json` with `grounded: true` and a verbatim Periplus quotation.

Those two questions are the entire argument for the persevere verdict at the Phase 1 exit gate: *the system refused a question whose answer it was holding, and answered it correctly when the question was reworded against the same evidence.* **CORRECTED 2026-08-25, FINDING 17: the evidence was never byte-identical, and the true claim is stronger — the refusing question is shown the answer twice, at rank 1, at a higher similarity than the question that answers it. See `FINDINGS_14_TO_18.md`.** **Only the failing half is in the gold set, so the founding claim of this phase is an anecdote and not a regression test.**

Add `adulis-exports`, expected behaviour **answerable**, paired explicitly with `aksum-exports` so a reader cannot get one without the other. Then run the suites listed above and record what they say. **Do not start TASK 2 against a red suite** — a case set built on an instrument nobody has watched pass is how a floor gets calibrated to a fiction, and this repository has done that twice.

Note `floor.json`'s `known_failing_cases`: `aksum-exports` is tracked as an **open defect, not a tolerated one**, so that a floor pass can never be read as *"the system answers these questions"*. Adding `adulis-exports` does not close it and must not be recorded as closing it.

---

# TASK 1 — D1, the corpus version in every answer

Cheap, offline, zero API calls, and it is debt that makes everything after it legible.

- hash each seed record on load; store the per-record hashes for the records actually cited in the `answers` row **and** in the `eval/answer_runs/` archive, beside `prompt_version`;
- `ui/build_ui_data.py --verify` then reports spans **against the corpus version that made them**;
- the Part 9 `1 absent` span becomes *explicable* rather than merely absent — *"this span broke"* and *"this span was made against a different corpus"* stop being the same observation.

This must land **before** Block E, because Block E's whole claim is that the corpus did not move under the sweep, and right now nothing in an archive would say if it had.

---

# TASK 2 — D2/D3, five cases to thirty

**Stratified, and the stratification is the deliverable, not the count:** ≥3 per region across seven regions (21 minimum), ≥6 source languages, balanced across three expected behaviours.

| Expected behaviour | Pattern | What a failure means |
| :---- | :---- | :---- |
| **answerable** | the corpus holds it and the model should find it | retrieval or assembly failure |
| **correctly refusable** | the Antikythera pattern — not in the corpus | the model invented something |
| **refusable-with-gloss** | the Vimose pattern — present but untranslatable; show source plus published gloss | a machine translation appeared, which is the **worst possible output**, because it arrives attached to a citation |

Rules, carried from Phase 1 and non-negotiable:

- **Every case declares its expected behaviour explicitly, and the loader REFUSES to inherit it from a default.** No case in the current five carries such a field, so this is a schema change and a loader change, and it needs a mutation.
- **Keep the known failures in.** `aksum-exports` stays required. Dropping a case because the model had a bad session is how a floor gets quietly lowered to whatever currently passes.
- **Prefer `expect_quoted_docs` over `expect_cited_docs`.** The first proves the model *used* a source; the second only proves it *named* one. `answer_cases.json`'s own note records why: on `aksum-exports`, three of six retrieved passages carry gold terms, so an answer could satisfy every content term from India and China, cite the Aksum record once for something else, and pass while never using it.
- **Every assertion is a fact about strings** — a substring, a doc id in a citation row, a count of quotations that resolved to characters on disk. No judge, nothing that has to be trusted. That is Part 8 decision 2 and it does not get relaxed at 30 cases.

---

# TASK 3 — D4, teach the harness about sessions, then pilot

`eval/run_answer_sweep.py` takes `--prompt-version --repeat --case --k --max-sources --pause --dry-run --no-write --json`. **There is no session or date flag, and no archive records one.** That is the gap.

1. Record a **session identity** — run date at minimum — in every sweep archive.
2. Make floor calibration **refuse to set `calibrated: true`** when distinct dates < 3, and **mutation-verify that refusal**.
3. Report **per-case stability and per-session stability as two separate numbers.** One number cannot say which of the two is moving.
4. **Pilot on 5 cases across 2 days, ~30 chat calls**, so the three-day sweep is not the first time this code runs across a date boundary.

That pilot is cheap insurance on a 270-call artefact, and this repository has already lost a 26-minute reranked run to a printer that had never been called on a shape it would meet.

---

# Then Block E — the sweep, and gate G4

Per day: **30 cases × 3 repetitions ≈ 90 chat calls**, plus ~10 batched embeddings. Three days: **~270 chat calls.**

```powershell
python -m eval.run_answer_sweep --dry-run      # embeddings only, no chat
python -m eval.run_answer_sweep --repeat 3     # ~90 chat calls
python -m eval.rescore_sweep                   # no API calls
```

**Between days, change nothing.** Not a prompt, not the corpus, not retrieval, not the gateway. A prompt tweak on day two turns three observations into one — this is exactly the discipline C5–C6 held to, and it held because the tree was committed first.

**Gate G4 checklist:**

```
[ ] >=30 cases meeting the stratification, each with an explicit expected behaviour
[ ] run 3x on >=3 separate days
[ ] per-case stability and per-session stability reported as SEPARATE numbers
[ ] a stated variance decomposition - how much is session, how much is case -
    with the data archived
[ ] the floor recalibrated from cross-session data and `calibrated: true`,
    OR the reason it cannot be written down
```

**The deliverable is the variance decomposition, not the pass rate.** If G4 fails, Phase 2 cannot be steered and every later improvement is unfalsifiable. That is **kill trigger 2**, and with kill trigger 1 already pulled it is the one that decides whether this project has an instrument at all.

---

## The single most important thing in `floor.json`, and why G4 is not optional

```
calibrated: false
calibration_invalidated: "2026-08-10, hours after being set."
```

The floor was calibrated on the observation that CONTENT was stable in 10 of 10 cells across three repetitions each. Then a second sweep, with the `vimose-runes` evidence block **byte-identical (sha256 verified across all six archived runs)**, produced the opposite result: **3/3 pass with seven resolved quotations in the first session, 0/3 with none in the second.** Same prompt version, same model, same evidence, temperature 0.

`session_caveat` states the consequence and it is the thesis of Block E:

> *"Repetitions within one session are correlated and are not independent samples. Part 6's lesson was 'one shot is one sample of a distribution nobody has looked at'. This is the same lesson one level up: three shots in one session may also be one sample. Until repetitions span sessions, this floor is a WITHIN-SESSION regression gate and nothing more."*

**All three archived sweeps are within-session.** The floor has never been measured the way it is written, in exactly the way the gap criterion had never been measured the way it was written — and that one took a session to find. Do not let a green sweep read as a calibrated floor.

## The one thing that must not move

**The ranking configuration is frozen and Block E depends on it staying frozen.**

```powershell
python -m eval.run_ranking_check --with-distractors --collapse --rerank --rerank-tpm 2000000
```

No `--fuse`. No `--skip-check`. `gateway/config.yaml` holds two chat aliases: `chat-default` (haiku-4-5, greedy) and `chat-strong` (sonnet-5, temperature 1 only). **Part 6 and Part 7 must keep using `chat-default`** — repointing it makes every archived number incomparable, and the whole sweep is denominated in it.

Ruling 22: a retry at temperature 0 is the same call, `claude-sonnet-5` refuses `temperature=0` outright, and LiteLLM's gateway-wide `drop_params` fix was refused. Temperature is classified, recorded and opt-in, never dropped.

## Traps carried forward

- **A test whose failure detail is non-Latin DIED instead of failing.** Through a pipe on Windows the child's stdout falls back to cp1252 and `print` raises. Both ends are fixed in the ranking harness; `mutate_part8.py` and `eval.test_answer_eval` are **a different harness pair and have not been checked against this.** Answer cases carry Greek, Tamil and Chinese by construction. Check it before trusting a green mutation run.
- **Delete and edit by NAME, never by line offset.** `write_atomically` vanished that way and surfaced as a `NameError` at the moment of writing.
- **A check that greps a heading passes against a report that prints the heading and no rows.** Assert the value.
- **A fixture where the max is the last value tests the word "max".** And a fixture where two figures agree cannot tell a report printing both from a report printing one twice.
- **A predicate with two clauses needs two mutations.** C7 found one of its own guards unwatched because the mutation written for it broke a different guard. A MISS that says *"detected by another guard — list drift?"* may not be drift; check what the mutation actually does before re-ordering the lists.
- **`--limit N` caps a plan; it does not create one.** A run asked to do something that plans nothing must say so.
- **Never run two mutation harnesses over one working tree at once**, and run them on the host against a local filesystem. Both capture originals at start and restore at exit, so the second captures the first's mutation as the original.

## Session ritual

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
docker compose up -d db
litellm --config gateway/config.yaml --port 4000     # separate window

python -m ingest.run_embed --stats        # 450 / 450 / 0 pending
python -m eval.test_answer_eval           # 68 + 2 FAILED until TASK 0 lands
python -m eval.test_ranking_check         # 218
python scripts\mutate_ranking.py          # 91
```

**Run `git` in PowerShell on the host, never through a mounted filesystem.** A `git status` issued from the Linux side of the device bridge left a stale `.git/index.lock` that had to be cleared by hand. `git rev-parse` and `git hash-object` are lock-free and safe; `git status` is not.

## The one thing the next thread must not inherit uncritically

Block C ended with two numbers and the temptation is to carry only the first.

**29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was reachable** — and the second moved from 21/30 only because C7 corrected which column the harness read, not because retrieval improved. `muziris-cargo-akananuru` still sits at rank 310, the corpus's one genuinely broken cross-lingual link, and is not counted toward the gate. The W2b distractor curve still rests on **English-only padding**, so *"flat over an eightfold index"* still means *"English-target retrieval survives English competition"*.

Block D and Block E measure something different again: not whether the passage can be found, but whether the answer built on it is **stable enough to be improved on purpose**. Those are three questions and they have three answers.

**C5 and C6 measured a stable pipeline. They did not measure a solved problem, and nothing since has changed that.**
