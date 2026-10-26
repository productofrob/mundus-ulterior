# Block D, TASK 2 — starting point for the next thread

*Written 2026-08-21 at the close of TASK 0 and TASK 1. Supersedes
`BLOCK_D_START.md`, whose TASK 0 and TASK 1 are done. Every number here was
measured on the host.*

## Read these, in this order

| # | file | why |
| :---- | :---- | :---- |
| 1 | **this file** | state, and the two tasks left |
| 2 | `D_TASK0_RESULT.md` | findings 1-5, including a five-day outage nobody saw |
| 3 | `D1_RESULT.md` | what D1 built, and the two spans it can and cannot explain |
| 4 | `RULINGS.md` | **new.** The index of rulings 1-26. Read it before quoting a number |
| 5 | `BLOCK_D_START.md` **TASK 2 and TASK 3 only** | still authoritative for those two |
| 6 | `PROGRESS.md` **last section only** | 594,356 bytes. Do not read it whole |

`BLOCK_D_START.md`'s TASK 0 and TASK 1 sections are **done**. Its "state as
measured 2026-08-20" block is **stale** — it names tree `ccca17e` and
`PROGRESS.md` at 580,817 bytes; both moved before that thread even started.

## State, as measured 2026-08-21

```
tree            f54c585, clean
                f54c585  D1 step 2: the corpus version travels with every answer
                73e3c80  D1 step 1: one definition of what a seed record is
                7c003a7  D TASK 0: adulis-exports, and the answer path had been dead

corpus          24 documents / 59 chunks / 57 retrieval-eligible
                digest 2e84436cb38a463b0110613d5662d0067b8d16cc9e28e1db4c8374882314ecfc
index           450 / 450 / 0 pending
archives        78 runs; ONE carries a corpus version
gold cases      6, need >= 30

ANSWER          eval.test_answer_eval        71   GREEN
RANKING         eval.test_ranking_check     218   GREEN
mutations       ranking 91 | part8 11 | part7b 15 | distractors 6
                | places 43 | ui_places 3
```

**No suite is red.** Every one was run on the host this session.

## What changed under TASK 2's feet

**The answer path was dead from `bff0605` until this morning** —
`assemble.py:449` unpacked two values from a three-value `_chat`. Block E's
270-call sweep would have died on call one. Fixed in `7c003a7`, and proven with
one live call. TASK 2 builds 30 cases that TASK 3 and Block E will run through
that path, so it is worth knowing it was only proven working once, on one
question, today.

**`adulis-exports` exists and passes live**, on evidence byte-identical to the
seven consecutive refusals of `aksum-exports`. The discriminator is a regression
test now. **Its assertion block is a byte-identical copy of `aksum-exports`'s** —
if the two ever drift apart the pair stops discriminating between two questions
and starts discriminating between two tests. TASK 2's schema change must not
break that.

**Every answer now records the corpus it was made against.** `--verify` reports
provenance on a second axis with three states. When TASK 2's cases are run,
their spans should come back `unchanged`; anything else is a real finding.

## TASK 2 — the schema change comes first, and it is the trap

`BLOCK_D_START.md`'s TASK 2 section is still authoritative. Two things it says
that are worth repeating because they are cheap to lose:

- **Every case declares its expected behaviour explicitly, and the loader
  REFUSES to inherit it from a default.** None of the current 6 carries such a
  field, so this is a schema change AND a loader change, and it needs a
  mutation.
- **Prefer `expect_quoted_docs` over `expect_cited_docs`.** Citing a document is
  a proxy; quoting it is the thing.

Note what the loader already refuses, so it is not rebuilt: a case making no
content assertion, an empty alternatives group, an empty required substring,
`expect_refusal` without a justification, a duplicate id, a misspelled key.
`eval/goldset.py::load_answer_cases` and its 11 mutations in
`scripts/mutate_part8.py`.

**The pairing between `aksum-exports` and `adulis-exports` is prose today.** The
plan is for it to become a loader-enforced field when `expected_behaviour`
lands, so deleting one of the pair is a load error rather than a silent halving
of the discriminator.

**Action item #5 stands:** the project owner writes the 30 cases, or at minimum
owns every expected-behaviour label. The agreed shape from this session is that
Claude drafts and the owner rules on each label explicitly before anything is
committed.

## TASK 3 — unchanged, and one addition

`BLOCK_D_START.md`'s TASK 3 is authoritative. One thing to add to the "change
nothing between days" list, found this session:

> **The schema file.** `run_answer.py:234` re-applies `scripts/schema-part7.sql`
> on EVERY call — ~90 a day in Block E. Any drift between file and database
> resolves silently, mid-sweep, in the direction of the file. The current list
> names the prompt, the corpus, retrieval and the gateway. It does not name this.

Also: `run_answer.py` takes the question as a **positional** argument. There is
no `--question` flag. A sweep script written against one would fail after the
gateway was up.

## Traps carried forward

Everything in `BLOCK_D_START.md`'s trap list still applies. Four to add:

- **A green mutation run is not evidence the tree was restored.** All four
  harnesses compare text after universal-newline normalisation, so a CRLF/LF
  rewrite passes as *"sources restored"*. `mutate_part8` did exactly this to
  `eval/answer_eval.py` on every one of its 11 mutations. The tree is **CRLF 13,
  LF 58** — LF is the majority — and three of six harnesses have LF sources.
- **Never `git checkout --` a file to clear line-ending churn.** It cannot tell
  your uncommitted work from the churn. This block's own step-2 runbook
  prescribed it and destroyed a completed task. **Commit before running any
  mutation harness**, or convert endings in place behind an assertion that the
  work is still in the file.
- **A migration cannot own a view that `schema-part7.sql` owns.** That file is
  re-applied on every run. Adding a column to one of its views from a migration
  fails loudly; REMOVING one would be silently restored.
- **A re-derivation that disagrees with the instrument by two orders of
  magnitude is a defect in the re-derivation.** A hand-written span check
  reported 115 broken spans against the harness's 2, because it used equality
  where `build_ui_data.py:475` uses containment in either direction.

## Open, and deliberately not closed

- **Nothing guards the `_chat` arity contract.** `mutate_part7b` verified 15 of
  15 and not one is about it. A signature is a contract with as many clauses as
  it has return values.
- **No mutation harness compares bytes on restore.**
- **`classify_span` asserts a cause it cannot know**, printed directly above a
  provenance line that now contradicts it. The wording should lose the claim.
- **Rulings 20 and 21 have no full text** — one line each in `C5_START.md`. The
  code is the authority; no prose is. Not reconstructed on purpose.
- **`aksum-exports` remains an open defect** in `floor.json.known_failing_cases`.
  Adding the passing half did not close it.

## The sentence that still travels with all of it

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310. The W2b distractor
curve still rests on English-only padding.

**Block D and Block E measure something different again: not whether the passage
can be found, but whether the answer built on it is stable enough to be improved
on purpose.** Nothing this session changed that, and D1 does not measure it — D1
only makes it possible to tell a moved corpus from a broken answer while
measuring it.
