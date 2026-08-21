# D TASK 0 — result (2026-08-21)

*Every number below was measured on the host, in PowerShell, against a venv and
a live db container. Nothing here was run over the device bridge.*

## The suite is green, and so are the seven nobody had watched

```
eval.test_answer_eval           71 passed, 0 failed      was 68 + 2 FAILED
answer.test_answer              all Part 7 offline checks passed   was a CRASH
answer.test_translate           all Part 6 offline checks passed   1 skip, sqlglot
ui\test_build_ui_data.py        all build-layer assertions passed
ui\check_ui.mjs                 all checks passed
ingest.test_distractors         16 passed, 0 failed

ingest.run_embed --stats        450 / 450 / 0 pending
eval.test_ranking_check         218 passed, 0 failed
scripts\mutate_ranking.py       91 mutations verified
scripts\mutate_part8.py         11 mutations verified
scripts\mutate_part7b.py        15 mutations verified
scripts\mutate_distractors.py    6 mutations verified
                                --
                                123 mutations across four harnesses
```

`check_ui.mjs` also reprinted the span audit that D1 is aimed at, over 77 runs
and 24 seed records:

```
{"resolved":157,"case_folded":0,"case_only":9,"moved":1,"absent":1}
```

**There is a `moved` span as well as the known `absent` one.** `BLOCK_D_START`
names only "the Part 9 `1 absent` span". Both are unexplainable today and both
are D1's business.

## 71 and not 70

The prediction written before the run was 70 and was wrong by one.

```
68   passing before
 +2   the two failing on the missing gold case
 +1   test_answer_eval.py:217 — one assertion per NON-REFUSAL case
```

`test_answer_eval.py:206` loops over every case and, for anything that is not a
refusal case, emits `GUARD <id>: a refusal cannot satisfy this case`.
`adulis-exports` is answerable, so it adds exactly one — and **that assertion
passing is the property the discriminator depends on.** If a refusal could
satisfy `adulis-exports`, both halves of the pair would be satisfiable by the
same silence and the pair would discriminate nothing.

---

# FINDING 1 — the answer path had been dead for five days

This is what TASK 0 was for, and it is worse than the missing gold case it was
sent to fix.

```
answer/translate.py:377   def _chat(...) -> tuple[str, int, float]
                          "Returns (text, retries, temperature_actually_used)"
answer/translate.py:478   raw, retries, temperature = _chat(     updated
answer/translate.py:516   raw, retries, temperature = _chat(     updated
answer/translate.py:573   raw, retries, temperature = _chat(     updated
answer/assemble.py:449    raw, retries = _chat(                  NOT updated
```

`assemble.py:449` was the only `_chat` caller outside `translate.py`, and it was
the one missed. `git log -S` dates both ends:

```
_chat gained the third value      bff0605   "Block C: ... rulings 12-25"
assemble.py:449 last touched      9470506   "Phase 1 baseline ... 2026-08-12"
```

This is **ruling 22's own temperature work**. It has been on `master` through
`bff0605 → 744e57c → ccca17e → 77d51fa`, across the whole of C5, C6 and C7,
invisible because Block C ran only the ranking suites.

**Every live answer call raised `ValueError: too many values to unpack (expected
2, got 3)` the instant the model returned.** So did `eval.run_answer_sweep`.
Block E's 270-call sweep would have died on call one, and so would the D4 pilot
that exists to stop precisely that.

**No archived number is contaminated.** The newest archive is
`20260812T133627`, five days before `bff0605`.

### The fix captures the third value rather than discarding it

Ruling 22: temperature is *classified, recorded and opt-in, never dropped*. A
`_` would have worked and would also have dropped it. This path passes no
temperature and no fallback, so the value is `0.0` today — which is exactly why
it is worth reading. It is a constant until someone changes it, and a silent `_`
is how that change would arrive unannounced.

```python
raw, retries, temperature_used = _chat(...)
if temperature_used != 0:
    notes.append(f"temperature {temperature_used} was used, not 0 - this answer "
                 f"is NOT comparable with the greedy archive it will be filed beside")
```

# FINDING 2 — nothing guards the `_chat` arity contract, and this is the gap that matters

`mutate_part7b.py` mutates `answer/assemble.py` and verified **15 of 15**
mutations. **Not one of them is about the contract that broke.**

The suite did not *fail* on this defect — it **died**, at
`test_answer.py:607`, because the only thing exercising the contract is an
end-to-end test that calls straight through into the real `assemble()`. A defect
that kills the suite rather than failing an assertion has no guard by
definition, and a harness whose suite dies reports every subsequent mutation as
`MISS (crash)` rather than as a finding.

**A signature is a contract with as many clauses as it has return values, and a
predicate with two clauses needs two mutations.** The rule the repository
already wrote for predicates was never applied to signatures.

# FINDING 3 — the cp1252 trap did NOT reproduce. It is latent, not active

`BLOCK_D_START` required this be checked before any green mutation run was
trusted. Checked, by inspection and then by running:

```
scripts/mutate_ranking.py:756   encoding="utf-8", errors="replace",
                                PYTHONIOENCODING=utf-8          BOTH ENDS FIXED
scripts/mutate_part8.py:153     capture_output=True, text=True  NEITHER END
scripts/mutate_part7b.py:223    capture_output=True, text=True  NEITHER END
```

Both harnesses nevertheless ran clean — 11 and 15 mutations, no crash, no
`UnicodeDecodeError`. **No current mutation produces non-Latin failure detail**,
so the exposure is real and unexercised.

This is the same shape as the `.git/index.lock` hazard recorded at the close of
C7: re-entered, not reproduced, precaution kept. **The fix is a precaution and
must be written down as one, not as a repair.** An intermittent hazard is the
kind this repository has been worst at, because the run that does not reproduce
it is the one that gets believed.

# FINDING 4 — a text-mode round trip rewrites whole files, on BOTH sides

The first write of the `assemble.py` patch produced a diff of **577 insertions,
560 deletions** — the whole file. `answer/assemble.py` is CRLF on disk; a
`read_text`/`write_text` round trip performed **on the Linux side of the device
bridge** normalised all 560 line endings to LF, and `.gitattributes:16` sets
`* -text`, so git does not paper over it. Caught by reading the diffstat,
restored, and the real diff is 18 and 1.

The sharp form of the trap is not "Python text mode rewrites line endings":

> **`mutate_part7b.py` round-trips `assemble.py` through that same call pair on
> every one of its 15 mutations and has never damaged it, because on Windows
> `write_text` translates `\n` back to `\r\n` on the way out. The identical code
> loses CRLF only when the writer is on Linux.**

That much was written down as a bridge hazard. **It was half the finding, and
the direction was backwards.**

## FINDING 5 — `mutate_part8.py` rewrote one of its own sources on the host, and reported "sources restored"

Caught minutes later, in the commit editor, as an unexplained
`modified: eval/answer_eval.py` that neither the session nor the author had
touched. Measured:

```
                       HEAD                    DISK after mutate_part8.py
eval/answer_eval.py    crlf=0   bare_lf=527    crlf=527  bare_lf=0    REWRITTEN
eval/goldset.py        crlf=754 bare_lf=0      unchanged
answer/cite.py         crlf=839 bare_lf=0      unchanged
answer/align.py        crlf=184 bare_lf=0      unchanged
answer/store.py        crlf=201 bare_lf=0      unchanged
ingest/db.py           crlf=244 bare_lf=0      unchanged
```

Content identical ignoring line endings, in every case.

**`eval/answer_eval.py` is the only mutation-harness source in the repository
that was LF at HEAD.** `mutate_part8.py` round-trips it through
`read_text`/`write_text` on each of its 11 mutations; on Windows `write_text`
emits `\r\n`, so all 527 endings were converted on the first write and never
converted back. `mutate_part8.py:185` then compared the restored text **after
universal-newline normalisation**, found it equal, and printed
*"all 11 mutations verified; sources restored"*.

**The harness rewrote a source file and its own restore check was
constitutionally unable to see it.** The same blind comparison sits at
`mutate_part7b.py:274` and in `mutate_distractors.py`.

The other three harnesses escaped **only because every one of their sources
happens to be CRLF.** That is file history, not design. The moment any harness
gains an LF source — or any existing source is normalised — it silently rewrites
it on every run.

Three consequences, and the third is the one that costs an afternoon:

- **CORRECTED 2026-08-21, after the claim above was committed.** The line
  originally written here said *".py in this repo is CRLF except
  eval/answer_eval.py"*. That was a generalisation from the seven files this
  session happened to look at, and it is wrong. Surveyed over every tracked
  `.py` at HEAD:

  ```
  CRLF 13    LF 58    mixed 0
  ```

  **LF is the majority by four to one.** `eval/answer_eval.py` is not an
  anomaly in the tree — it is an anomaly *among the eight mutation-harness
  sources*, seven of which happen to fall in the CRLF 13. That is luck, not
  design, and it inverts the remedy: **normalising the tree to CRLF would be
  normalising the minority.** The fix belongs in the harnesses, which must
  read and write bytes rather than text.
- **A restore check must compare BYTES, not normalised text.** Every one of the
  four harnesses compares text. This is the same defect family as *"a check that
  greps a heading passes against a report that prints the heading and no rows"* —
  the comparison is too tolerant to fail on the thing it exists to detect.
- **A green mutation run is not evidence the tree was restored.** All 123
  mutations reported clean restores today and one of them was not clean. Any
  future finding that rests on *"sources restored"* rests on a check that has now
  been shown to pass while wrong.

---

## What landed on disk

```
M  eval/gold/answer_cases.json    +33  -2     adulis-exports, data only
M  answer/assemble.py             +18  -1     the dead answer path
A  D_TASK0_RUNBOOK.md
A  D1_DESIGN.md
A  D_TASK0_RESULT.md
```

The gold-case change is **data only** — no loader change, no harness change, no
schema change. If the instrument had changed in the commit that turned it green,
the green would not have been evidence that the instrument works.

## Carried into TASK 1

- Two unexplainable spans, not one: `1 moved` and `1 absent`.
- The five decisions in `D1_DESIGN.md`, unchanged.
- The temperature value is captured but not yet archived. It belongs in D1's
  provenance block beside `corpus_version` and `prompt_version`, so there is one
  schema migration rather than two.

## Open, and deliberately not closed here

- **Rulings 25 and 26 are still not in the rulings register.** `BLOCK_C_RULINGS.md`
  carries 1–11; `C2_RULINGS.md` stops at 24. Ruling 26 is quoted by this block's
  own start document.
- **The `_chat` arity guard does not exist** (Finding 2).
- **The cp1252 precaution is not applied** to `mutate_part8.py` or
  `mutate_part7b.py` (Finding 3).
- **No mutation harness compares bytes on restore** (Finding 5). Four harnesses,
  one blind check each.
- `aksum-exports` remains an **open defect** in `floor.json.known_failing_cases`.
  Adding the passing half did not close it and was not recorded as closing it.
