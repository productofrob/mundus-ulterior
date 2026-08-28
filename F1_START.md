# F1 — starting point for the next thread

*Written 2026-08-28, at the close of the F0 decision block. `BLOCK_F_START.md`
is superseded by this file for the reading list and the state; it is still the
statement of what the four decisions WERE and why they were left open, and
`F0_RESULT.md` is what they were settled to. `PHASE2_PLAN.md` is still the
statement of what Block F is — W3, corpus 24 to 60, eight sessions, gate G3.*

## Read these, in this order

| # | file | why |
| :---- | :---- | :---- |
| 1 | **this file** | state, what F1 is, and the one deadline |
| 2 | `F0_RESULT.md` | the four decisions as settled, and three things BLOCK_F_START did not know |
| 3 | `F0_RULINGS.md` | rulings 36-42. Ruling 36 before archiving any sweep; 40 CARRIES A CORRECTION, read it |
| 4 | `PHASE2_PLAN.md`, the Block F section only | F1-F8 and the AMENDED G3 checklist |
| 5 | `eval/gold/floor.json` | read whole. Three states now, not two |
| 6 | `PROGRESS.md` **last two sections only** | ~659 KB. Do not read it whole. It is CURRENT as of 2026-08-28 |

`BLOCK_F_START.md`'s reading list points at a `PROGRESS.md` that ended at Block
D. That is fixed — the file now runs to `# State at the close of F0
(2026-08-28)` — and this list replaces it.

## State, as measured 2026-08-28

```
tree            clean, at the F0 block's last commit
                2091e03  the harnesses: mojibake, a discarded return code, and
                         an LF source converted in a commit
                3dfcae1  rulings 40-42
                bee344e  the stale stand-in, and the mutation that passed for
                         the wrong reason
                b42ba43  the four decisions, and the arm the archive never
                         recorded

corpus          24 records / 450 embedded / 0 pending
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                THE DENOMINATOR OF ALL 396 BLOCK E RUNS. F3 moves it.

ANSWER          eval.test_answer_eval       321   GREEN
mutations       scripts\mutate_part8.py      75   GREEN
                scripts\mutate_part7b.py     18   GREEN
                scripts\mutate_ui_places.py   4   GREEN
RANKING         eval.test_ranking_check     236   GREEN
mutations       scripts\mutate_ranking.py   100   GREEN
PART 7          answer.test_answer                GREEN
UI              ui\test_build_ui_data.py         GREEN

gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
floor           calibrated TRUE. per_case 132/132, per_session 31/33
required        antikythera-absent, chinese-da-qin, muziris-cargo
known-failing   aksum-exports, vimose-runes, skz-titulature
candidate       weilue-chinese-quotation      <- the third state, ruling 38
rulings         1 to 42, indexed in RULINGS.md
gates           G4 CLOSED. G3 is Block F's, AMENDED IN ADVANCE.
```

## THE ONE DEADLINE, and it is not F1's

**The sonnet arm has not run, and the frozen-corpus window closes the moment the
first sub-tranche lands.** `26e4a683` is the denominator of every Block E number.
F1 and F2 do not move the corpus; **F3 does**, and the arm has to be beside the
frozen archive or it is measuring something else.

```
33 cases x 5 repetitions, temperature 1, alias chat-strong, ONE session
--session-label required. Archives to eval/arms/, NEVER to eval/sweeps/
~165 chat calls. Its own gate, its own repetitions, its own numbers.
```

Five repetitions and not three because it cannot be greedy: ruling 22 records
that `claude-sonnet-5` refuses `temperature=0` with a bare 400. The question it
answers is the one runbook 3b posed and Block E ruled out of scope — **is the
answer path model-limited?** `aksum-exports` fails 0/3 under four prompts with
the answer sitting in published English in its own evidence block, and that has
been attributed to prompt and retrieval on no evidence either way.

**It is safe to run now and it was not safe a day ago.** Ruling 36 made the arm
part of a sweep's identity and part of the calibration scope; before that,
`floor.json`'s own anti-loophole would have INSISTED that a temperature-1 sonnet
sweep calibrate a floor set on greedy haiku. Read ruling 36 before running it.

## What F1 is

`PHASE2_PLAN.md` F1: **declare the tiering policy before curating anything**, and
set the target mix across the 36 new records so the tranche is not accidentally
all catalogue records.

```
verbatim_with_provenance   original text, published translation, both cited
published_translation_only no open original transcription available
catalogue_record           find/coin record, object description, no
                           source-language text
```

`ingest/fidelity.py`'s `text_fidelity` classifier already has the vocabulary.
F2 starts the minutes-per-record column from record 25; kill trigger 3 depends
on it.

**Two things F0 learned that belong in F1's curation style, not in its code.**

- **A case whose assertion asks for more than its question does is a case that
  will fail for a reason no reader can see.** That is ruling 42's weaker half:
  `skz-titulature` asks what titles Shapur claims and its assertion demands the
  filiation. Write the question to ask for what the assertion requires.
- **The gloss arm is starved and it is a fact about the corpus.** 3 gloss cases
  against 22 answerable, because this seed corpus holds very few texts whose
  READING is genuinely in dispute (ruling 28 keeps the arm narrow, and it stays
  narrow). If the 36 new records are chosen with that in mind, the balance can
  be met honestly for the first time.

## What does NOT move in Block F

**The model, on the default alias.** Ruling 22, and every archived number is
haiku at temperature 0. The sonnet arm is a SECOND alias and a separate archive,
never a replacement — that is the whole content of ruling 36.

**The prompt.** Changing rule 3 is what would close FINDING 13, and it
invalidates every archived number.

## Traps

Everything in `BLOCK_D_START.md`, `D4_START.md`, `BLOCK_E_START.md`,
`BLOCK_E_RUNBOOK.md` and `BLOCK_F_START.md` still applies. Four are worth
re-reading, and the last two are new as of 2026-08-28:

- **Never run a suite or a mutation harness through the Cowork bridge.** Each
  call is killed at 45 seconds and a killed harness leaves a live mutation in
  the tree. Host only, in PowerShell.
- **`git` through the bridge leaves `.git/index.lock` behind.** Use
  `--no-optional-locks` for anything read-only, or do not run git through the
  bridge at all.
- **Line endings are per file and must not be normalised.** `answer/*.py`,
  `eval/goldset.py` and `answer/align.py` are CRLF; everything else in `eval/`,
  `ui/` and `scripts/` is LF. `.gitattributes` says git must not rewrite a byte,
  and 168 archived citation spans point into the corpus by exact offset.
  **On 2026-08-28 a mutation harness converted `ui/build_ui_data.py` LF to CRLF
  and the conversion reached a commit.** All six harnesses now restore and
  compare BYTES. Check `git diff --stat` after any harness run: a file whose
  every line changed is this defect, not your edit.
- **A green mutation against a red suite proves nothing.** `mutate_part8`,
  `mutate_part7b` and `mutate_ui_places` now run their suite once unmutated and
  print `BASELINE:` plus `UNVERIFIED` lines when a mutation names a guard that
  was already failing. **If you see either word, fix the suite before believing
  any `ok` in that run.** The other three harnesses do not have this yet.
- **A mutation anchor that appears in more than one SOURCE resolves
  first-source-wins, in silence**, and an anchor on a PRECEDING line can be
  pushed away by an insertion. Both happened; the harness's ambiguity check
  catches the first and only a MISS catches the second. Do not disable either.

## What is NOT a finding

`aksum-exports` failing. `vimose-runes` failing. `skz-titulature` failing on the
Ardashir group. All three are tracked in `known_failing_cases` with evidence,
all three are out of `required_cases`, and none is ever subtracted from a floor
verdict. **A sweep that reports any of them passing is a finding, not a
success.**

`weilue-chinese-quotation` passing 12/12. It is a promotion candidate, not a
required case, and ruling 37's bar is 3/3 in each of three sessions on three
distinct UTC dates **at the corpus in force** — which means at 60, not at 24.

## The sentence that travels

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310.

**Four sessions read 0.727272… and one of them was different. The pass rate
cannot see change.**

**Nine archives, 396 runs, and not one of them recorded which model answered.**
