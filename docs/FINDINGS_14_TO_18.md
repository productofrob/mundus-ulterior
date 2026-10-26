# Findings 14 to 18

*Written 2026-08-25, at the close of Block D's TASK 3. Findings 1–5 are in
`D_TASK0_RESULT.md`, 6–7 in `D1_RESULT.md`, 8 in `D2_RESULT.md`, 9–13 in
`FINDINGS_9_TO_13.md`. This document covers the two-day pilot and the three
defects found by running the instruments it was built to rehearse.*

**On the authority for 14, 15 and 16.** Each was written up in full, at the time
it was found, in the body of its own commit — `483be65`, `dce1ad1`, `fbabb93`.
Those bodies are the authoritative account and they are longer than what follows.
This file is the register entry: what the finding was, what it cost, and where to
read it. Nothing here is reconstructed, on the principle `RULINGS.md` sets out
about rulings 20 and 21.

**14, 15 and 16 were all found by RUNNING an instrument, not by reading one.**
That is the sentence Block D ends on. Three of the five findings in this file
were invisible to a suite that passes.

---

## Finding 14 — the sweep never recorded the corpus it was made against

`eval/run_answer_sweep.py` builds its own payload dict. It had no
`corpus_version` key and never set `answer.corpus_version` before calling
`assemble.store`, which reads `(answer.corpus_version or {}).get(...)` and
therefore wrote NULL to `seed_corpus_digest` and NULL to `cited_record_hashes`.

```
eval/answer_runs/*.json carrying sweep meta:   60
      ... of those carrying corpus_version:     0
```

D1 had made `run_answer` record the corpus version, and gave the reason: *"Block
E's whole claim is that the corpus did not move under the sweep."* **TASK 1
landed in the path that writes one of Block E's archives and not in the path
that writes the other 270.** Same shape as FINDING 10's half-fix: two harnesses,
one blind spot, and the second one is the one that matters.

The fix reads the corpus **twice** — before the first chat call and again after
the last — because a day of Block E is ~90 calls over well more than half an
hour, and the claim being made is precisely that nothing moved during it. What
changed is NAMED, never counted: *"the digest changed"* is a fact, *"eastasia-01-weilue
changed and persia-09-new appeared"* is something a person can act on.

Both D4 pilot sweeps carry `corpus_version`, `corpus_version_after` and
`corpus_moved: null`. Read `483be65`.

---

## Finding 15 — a mutation harness resolved an ambiguous target by taking the
## first source, silently

`scripts/mutate_part8.py` reported `MISS matching becomes punctuation-insensitive`.
The report was true and the diagnosis it invites — the guard is broken, or the
lists have drifted — was wrong. **The guard was fine. The mutation had moved.**

D4-B gave `eval/goldset.py` a `question_key()` byte-identical in body to
`eval/answer_eval.py`'s `normalise()`. The harness picks the first source in
`SOURCES`, which is `(GOLDSET, EVAL)`. So the mutation silently began patching
the loader's question key instead of the scorer's matcher, and
`GUARD matching is NOT punctuation-insensitive` was left **unwatched — not
broken, unwatched.**

Six ambiguous targets across the two harnesses. **One wrong, five correct by
the accident of ordering.** Pick-the-first-and-say-nothing, inside the instrument
this project built to catch pick-the-first-and-say-nothing — the same family as
FINDING 12 and `match_case`.

Both harnesses now refuse an ambiguous target by name. Ruling 34. Read `dce1ad1`.

---

## Finding 16 — CPython's bytecode cache validated a mutation away

Mutation 40 ran mutation 39's bytecode and reported 39's failures as its own.

A cached `.pyc` is keyed on its source's mtime **second** and its source's
**size**. Mutation 39 removes two bytes; mutation 40 removes two bytes; they are
written back to back. Same size, same second, same cache key. **They are the
only consecutive pair in that file with an identical size delta**, which is why
this had never been seen.

`scripts/mutate_ranking.py` had run its child with `-B` since 2026-08-16 under a
note describing this exact mechanism, explicitly *not credited with fixing
anything, because nothing here measured it.* It measured it on 2026-08-24.

**The note's model needed one correction and it makes the condition far more
likely:** the dangerous case is not a mutation that preserves the ORIGINAL's
size, it is **two consecutive mutations that produce the same size as each
other.** Removing two bytes is an ordinary thing for a mutation to do.

Which direction it fails in is luck. Here a working guard was reported as
unwatched — the harmless direction. The other direction — a guard that does not
fire, reported VERIFIED — is equally available and silent, and is what
2026-08-16 saw and attributed to a network mount.

Demonstrated at the boundary that failed rather than asserted:

```
without -B   [39] ok    [40] MISS, carrying 39's two failures
with -B      [39] ok    [40] ok, firing its own guard
```

Ruling 34. **Five other mutation harnesses remain non-compliant and are
deliberately unchanged.** Read `fbabb93`.

---

## Finding 17 — the aksum/adulis pair has never seen the same evidence

`BLOCK_D_START` and `D3_RESULT.md` both state the Phase 1 exit-gate claim as
*"reworded against **byte-identical evidence**"*. The archives do not support it.

```
2026-08-12  ADULIS  answered   [A000, P001, A002, M003, I000, X000]
2026-08-12  AKSUM   refused    [A002, P001, M003, I000, H000, hou-hanshu::000]

2026-08-24  ADULIS  answered   [A001, P001, A005, M003, A000, I000]
2026-08-24  AKSUM   refused    [A005, P001, M003, I000, A004, H000]

2026-08-25  ADULIS  answered   [A001, P001, A005, M003, A000, I000]
2026-08-25  AKSUM   refused    [A005, P001, M003, I000, A004, H000]
```

Four of six shared on every date. **The ASSERTION blocks are byte-identical and
ruling 31 enforces that at load. The EVIDENCE never has been.** The claim was
not true on the day it was made.

This does not weaken the discriminator — it sharpens it:

```
aksum-exports   [S1] africa-03-periplus-adulis::original::005  sim 0.559
                     ivory, tortoise-shell, rhinoceros ALL PRESENT
                [S5] africa-03-periplus-adulis::original::004  sim 0.455
                     ivory, tortoise-shell, rhinoceros ALL PRESENT
                -> refused, 3 of 3, on both days

adulis-exports  [S1] africa-03-periplus-adulis::original::001  sim 0.413
                -> answered, 3 of 3, on both days
```

**The question that refuses is shown the answer twice, at rank 1, at a higher
similarity than the question that answers it** — and the 24th and the 25th
returned the identical evidence set in the identical order, so this is now
observed across a date boundary rather than on one afternoon.

The sentence to correct is in `BLOCK_D_START.md` and `D3_RESULT.md`. No code
changes; `floor.json`'s own note never made the claim.

---

## Finding 18 — the verdicts held across a date boundary and not one answer
## text did

The D4 pilot ran the same six cases, three repetitions each, on 2026-08-24 and
2026-08-25 — same prompt version, same pinned model snapshot
`anthropic/claude-haiku-4-5-20251001`, temperature 0, corpus digest
`26e4a683…` identical at all four measurement points.

**Every verdict agreed.** `per-case 12/12 = 100%`, `per-session 6/6 = 100%`.

Every answer text, hashed:

```
case                 day 1 texts   day 2 texts   shared across the days
adulis-exports       2 distinct    1             NONE
aksum-exports        1             1             NONE
antikythera-absent   1             3 distinct    NONE
chinese-da-qin       3 distinct    1             NONE
muziris-cargo        1             1             BYTE-IDENTICAL, all six
vimose-runes         1             1             NONE
```

**Within-session determinism is not a property of the case.** `chinese-da-qin`
gave three texts then one; `antikythera-absent` gave one then three. An exact
swap.

**It is not a blanket claim about the model.** `muziris-cargo` returned the same
answer byte for byte in all six runs across both days. Text-level
reproducibility across a date boundary is achievable here. Five cases did not
achieve it.

**`vimose-runes` was deterministic on both days about a DIFFERENT answer.** One
text three times on the 24th, another three times on the 25th, differing enough
for the scorer to see it: the 24th quoted *"Several inscriptions remain only
partially deciphered"* and resolved one quotation, the 25th paraphrased the same
idea and resolved none. That is the 2026-08-10 phenomenon reproduced
deliberately. It did not cross a verdict boundary this time.

So a 100% per-session figure is a statement about **verdicts** and may not be
read as *"the system does the same thing on two days"*. **Ruling 35.**

### The corollary: the encoding fix cannot be proven on the answer path

`D4_PILOT_RUNBOOK.md`'s non-Latin check was vacuous, which
`claude/d4-day1-runbook-defects-and-day2.md` recorded on the 24th — and the
replacement it proposed, `eval.answer_eval --archives -v`, **is vacuous too.**
140,312 bytes captured on 2026-08-25; 70,155 characters; **zero above U+024F**
except em-dashes and ellipses.

That is not a bad choice of harness. It is the standing defect stating itself:

> **There is no non-Latin output because the system has never produced any.**
> 45 of 45 resolved spans came from the English while the Chinese chunk sat at
> `[S1]`. The failure detail prints `quoted: nothing`.

FINDING 10's guard is in all 44 entry points and mutation-verified. **It remains
unproven for the answer path, and cannot be proven there until the prompt asks
for a source text.** A proof must be taken from a harness that handles source
text by construction. Written down here so that no third attempt is made at
proving it on the path that has nothing to print.

---

*Block D ends here. The instruments can now tell a session from a repetition,
and the first thing they saw was that the verdicts hold while the words
underneath them do not.*
