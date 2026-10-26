# Rulings 32 to 35 — declared in Block D, TASK 3

*Written 2026-08-25, in the session that made them. `RULINGS.md` records why
that matters: rulings 20 and 21 exist only as one-line entries in a summary
list, nobody can quote them, and the code is the only authority for what was
decided. These four are written at the time, with the reasoning, so that is not
true of them.*

**Do not renumber.** 1–31 are quoted across `PROGRESS.md` and a dozen session
documents.

---

## Ruling 32 — a lost gold pair kills the run, and the only way past it is to
## name the pair

FINDING 12: `run_ranking_check.py` dropped a gold pair that stopped resolving
and reported it as a count line. On 2026-08-22 two pairs left a run and every
aggregate moved because the DENOMINATOR shrank — via-original reranked read
`22/30 -> 21/29`, which reads as a regression and is a lost pair. The invalid
archive `eval/ranking_runs/20260822T160349...` is committed deliberately as the
exhibit.

**Ruled.** The harness counts the pairs it resolved against the gold file, not
against what resolved. A shortfall is fatal, before anything is embedded, and
the message names each pair and why it did not resolve.

**The opt-out is a named list, never a flag.** `--allow-unresolvable` takes pair
ids. A pair missing from that list still kills the run. And an allowance that
names a pair which DOES resolve is itself refused — a stale allowance is a
silent re-opening of the hole this ruling closed, so it is made loud the moment
it stops being true.

*Why not a `--force`.* A boolean opt-out is a permission to stop reading. A list
of pair ids cannot be carried forward without someone re-reading it, and it goes
stale in a way the harness can detect. That asymmetry is the whole ruling.

Built and mutation-verified: `eval/test_ranking_check.py`, section *"FINDING 12:
a gold pair that stops resolving"*, eight checks; mutations in
`scripts/mutate_ranking.py`, four of them.

---

## Ruling 33 — DATES gate calibration; sessions are recorded beside them and
## gate nothing

The floor was calibrated on 2026-08-10 from repetitions inside one session and
was invalid within hours. Repetitions inside a session are correlated. They are
not independent samples, and a floor built from them is a within-session
regression gate wearing the word `calibrated`.

**Ruled.** `calibrated: true` may not be written from fewer than **three
distinct UTC dates**. Sessions are counted, reported, and named beside the
dates — a date carrying more than one session is printed, because that pair is
what invalidated this floor — but the session count gates nothing on its own.
Three sessions on one day are one date and cannot calibrate. Three dates of
single shots cannot calibrate either: the repetition requirement stands beside
the date requirement, not instead of it.

**A sweep with no session identity blocks calibration rather than counting as a
date.** The three pre-D4 sweeps cannot be given a date now. Assigning one after
the fact is exactly the calibration `floor.json` already records as invalid, and
they will block calibration permanently. That is accepted as the cost of having
run them before the instrument existed.

**And a floor file that permits calibration from a single day is itself
refused** — the threshold is not a tunable that a future session can quietly
lower to make a red gate green.

Exercised for real on 2026-08-25: refused at 2 distinct dates, and named both
grounds.

Built and mutation-verified: `eval/test_answer_eval.py`, section *"calibration
refuses too few days"*, ten checks; five mutations in `scripts/mutate_part8.py`.

---

## Ruling 34 — a mutation target must be unique across the SOURCES it is applied
## to, and the child must not read a stale bytecode cache

Two defects found by running the harness on 2026-08-24. One ruling, because
either alone silently converts a mutation harness into a machine that reports
successes it did not perform.

**FINDING 15 — the harness picked the first source and said nothing.**
`mutate_part8.py` locates a target with `next(f for f in SOURCES if old in
edited[f])` and applies it with `.replace(old, new, 1)`: the first source, then
the first occurrence, neither announced. D4-B had given `eval/goldset.py` a
`question_key()` whose body is byte-identical to `eval/answer_eval.py`'s
`normalise()`, and `SOURCES` is `(GOLDSET, EVAL)`. The punctuation mutation
therefore stopped mutating the scorer's matcher and started mutating the
loader's question key. `normalise()` was never touched and
*"GUARD matching is NOT punctuation-insensitive"* was left **unwatched — not
broken, unwatched**, which is the condition this block exists to find.

Six targets were ambiguous across the two harnesses. **One was wrong; five were
correct by the accident of `SOURCES` ordering.** Undocumented luck is worse than
a defect, because nothing says when it runs out — and in the sibling harness it
ran out the same day.

**Ruled:** a mutation target is resolved against every source it may appear in.
An ambiguous target is refused, by name, reporting the occurrence count and
telling the reader to anchor it — never resolved by position. Anchoring is done
with surrounding lines until the target is unique.

**FINDING 16 — the interpreter served the previous mutation's bytecode.**
A cached `.pyc` is keyed on its source's mtime **second** and its source's
**size**. Mutation 39 rewrote `["date"]` as `["id"]` and mutation 40 rewrote
`undated` as `False`: both remove exactly two bytes, written back to back. Same
size, same second, same cache key. Mutation 40 ran mutation 39's bytecode and
reported 39's failures attached to 40.

**The note in `mutate_ranking.py` had described this mechanism since 2026-08-16
and its `-B` was uncredited because nothing had measured it.** It is credited
now — and its model needs one correction, which makes the condition far more
likely than the note implied: **the dangerous case is not a mutation that
preserves the ORIGINAL's size, it is two CONSECUTIVE mutations that produce the
same size as each other.** Removing two bytes is an ordinary thing for a
mutation to do.

Which direction it fails in is luck. Here a working guard was reported
unwatched, which is the harmless direction. The other — a guard that genuinely
does not fire, reported VERIFIED because the previous mutation's failures
arrived attached to it — is equally available and is silent. 2026-08-16 saw it,
could not explain it, and attributed it to a network mount.

**Ruled:** a mutation harness runs every child with `-B`, sets
`PYTHONDONTWRITEBYTECODE` in the child environment, **and purges the bytecode
cache before every child run** — because `-B` stops a child WRITING a `.pyc` and
does nothing to stop it READING one an ordinary `python -m ...` left behind.
Both halves, or neither is a fix.

**Five other harnesses are known not to comply and are deliberately unchanged.**
`mutate_distractors`, `mutate_part7b`, `mutate_places`, `mutate_recover`,
`mutate_ui_places` — one flag and one call each. None of the five was run in
Block D, and a harness changed without being watched pass is the exact failure
this block exists to stop shipping. **Recorded as open work: any block that runs
one of the five fixes it first.**

## Ruling 35 — per-session stability is a statement about VERDICTS, and the
## number may not be read as a statement about behaviour

On 2026-08-25 the pilot returned `per-session 6/6 = 100%` for a pair of sessions
in which **five of six cases shared not one answer text**, at temperature 0,
against an identical corpus digest and a pinned dated model snapshot.
`vimose-runes` was internally deterministic on both days and deterministic about
a different answer on each.

**Ruled.** Both stability numbers are computed over the scored verdict —
content, groundedness, refusal — and neither is computed over the answer text.
That is the correct scope for a gate: a gate that failed on any text change
would fail every day and measure nothing.

**What follows is a prohibition on how the number is quoted.** A per-session
pass supports *"the verdicts this instrument produces are reproducible across a
date boundary."* It does NOT support *"the system does the same thing on two
days"*, and no document may use it that way. Where behaviour is the claim, the
evidence is `distinct_texts` per cell and the answer hashes, and those are
reported separately.

*Why this is a ruling and not a footnote.* The 2026-08-10 observation was a
verdict-level flip, so a verdict-level number is what caught it and what Block E
needs. But the same afternoon's mistake — a stable measurement read as a stable
system — is available again in a subtler form the moment someone quotes 100%
without its denominator's meaning. The scope goes in the register rather than in
one result document, because result documents are read once.

`distinct_texts` was already recorded per cell before this ruling. The ruling
adds no code. It constrains the prose.
