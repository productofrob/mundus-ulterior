# Block E day 1 — what the dry run said, BEFORE the 99 calls

*2026-08-26, session `255bac6abaf9`, written and committed before
`python -m eval.run_answer_sweep --repeat 3` was run. Recorded in advance
because a prediction made before the run is evidence and the same observation
made afterwards is a story.*

## The verdict: green

```
corpus     24 seed record(s), digest 26e4a683014bdf8a…   as required
cases      33 of 33 retrieved 6 sources each
records    EVERY case's expected document is present in its own evidence block
```

**No case will fail on day 1 for want of the record.** That is the one thing a
dry run is cheap enough to establish and expensive to discover afterwards.

## vimose-runes reproduces to the third decimal

```
                 D4, 2026-08-24/25          Block E day 1, 2026-08-26
[S1]  arabia-04-jabal-dabub    0.433        0.433
[S2]  arabia-03-jsnab17        0.401        0.401
[S3]  scandinavia-03-vimose    0.384        0.384   ALL SEVEN gold terms
```

Retrieval is frozen and it is reproducible. The demotion in `floor.json` rests
on 0/3 across two dates, and its diagnosis is now confirmed a third time.

## The pilot was not representative, and the demotion note says so by luck

`known_failing_cases.vimose-runes` reads *"a spread of 0.049, and no other case
**in the pilot** has a margin like it."* The qualifier is correct and it is
load-bearing: across the full 33 there are **worse** displacements.

Answerable cases whose expected document is NOT at [S1]:

```
jabal-dabub-basmala      rank 3   0.388  behind 0.523, 0.392   spread 0.135
vimose-runes  (gloss)    rank 3   0.384  behind 0.433, 0.401   spread 0.049
muziris-cargo  REQUIRED  rank 2   0.463  behind 0.503          spread 0.040
illerup-roman-coins      rank 3   0.496  behind 0.524, 0.509   spread 0.028
ezana-titulature         rank 2   0.427  behind 0.450          spread 0.023
khao-sam-kaeo-intaglio   rank 2   0.524  behind 0.538          spread 0.014
```

**`muziris-cargo` is a required case at rank 2 with a spread of 0.040** — inside
vimose's 0.049 — and it passed 3/3 on both D4 days with byte-identical text
across all six runs. So rank and margin alone do not predict failure, and
whatever is wrong with `vimose-runes` is not simply that its record sits third.
That weakens nothing in the demotion, which rests on the failures and not on
the margin, but it does retire "the margin is the explanation" as a hypothesis
nobody had tested against more than six cases.

`jabal-dabub-basmala` is the case to watch: the largest displacement in the set,
answerable, and never measured before Block E.

## A prediction, made before the run

**`hoby-silius-identification` will fail, for a reason that is neither of the
two known defects.**

Its expected document is at [S1], sim 0.436 — and the dry run flagged **not one
gold term present**. Its sibling `hoby-cheirisophos-signature` retrieves the
*same chunk*, `scandinavia-01-hoby-treasure::original::000`, and has every gold
term present.

The record explains it:

```
original_text_excerpt   "Signature on the silver cups: [ΧEIPI]ΣΟΦΟΣ ЄΠΟΙΕΙ
                        ('Cheirisophos made [this]'); engraved owner's name:
                        SILIVS."
                        -> carries Cheirisophos, ΣΟΦΟΣ, ЄΠΟΙΕΙ, 'made [this]',
                           'signature'.  SILIVS, not "Silius".

reference_translation   "...signed by the silversmith Cheirisophos and engraved
                        with the name Silius — possibly Gaius Silius, Roman
                        commandant at Mainz 14-21 CE — suggesting..."
                        -> carries Silius, possibly, Gaius Silius, Mainz,
                           commandant. EVERY term this case asks for.
```

The passage resolves `english=source ground=self`, so the English in the
evidence block is the excerpt. **The identification the case is about lives in
`reference_translation`, and `reference_translation` is not in the evidence.**

So this is a third failure family, and it should be named as one rather than
folded into the other two:

```
aksum-exports              content IS in the evidence; the answer refuses anyway
weilue-chinese-quotation   nothing in the prompt ever asks for source text
hoby-silius-identification content is in the RECORD and not in the EVIDENCE —
                           the right document, the wrong English attached to it
```

Same document, same chunk, opposite predicted outcomes, decided entirely by
which English got attached. That is FINDING 17's family — *the aksum/adulis pair
has never seen the same evidence* — arriving from the other direction.

**Not actionable in Block E.** Retrieval and the corpus are frozen for the whole
block. This is written down so that day 1 either confirms it or refutes it.

## The non-Latin opening, and why it matters

`D4_RESULT.md` closed the encoding question: the FINDING 10 guard is *"unproven
here and unprovable here until the prompt asks for source text"*, because
`eval.answer_eval --archives -v` produced 140,312 bytes and **zero** characters
above U+024F. `BLOCK_E_START` carries it as trap 4: three vacuous non-Latin
proofs in four days, do not attempt a fourth.

The dry run says the premise has a hole in it. Two answerable cases have
**non-Latin gold terms present in the retrieved English**:

```
hoby-cheirisophos-signature   ΣΟΦΟΣ, ЄΠΟΙΕΙ   present at [S1]
hwangnam-glass-origin         경주             present at [S1]
```

Neither is a source-text quotation — the Greek sits inside an English
description and the Korean inside a heritage designation — so `D4_RESULT`'s
sentence is not wrong. But it means characters above U+024F can now reach an
answer, an archive and a `*>` capture by an ordinary route nobody planned.

**This is not a fourth attempt at the proof.** Nothing is being built, asserted
or run for it. It is a thing to LOOK for in `eval\block-e-day1.txt`: if either
answer comes back carrying those characters, the guard has been exercised on the
answer path for the first time, by accident, and that is worth a line in the
result document. If neither does, that is worth a line too.

## What would stop the block

The corpus line reading anything other than `26e4a683014bdf8a…`. The sweep says
so and exits 2. Nothing else on this page stops it.
