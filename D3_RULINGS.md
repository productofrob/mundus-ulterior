# Rulings 27 to 31 — full text

*Declared 2026-08-21, during Block D's TASK 2 (D2, the schema) and TASK 2's case
work (D3). Indexed in `RULINGS.md`. Written here as declarations, and written
while the decisions were being made rather than reconstructed afterwards —
because rulings 20 and 21 have no full text anywhere, and that is what happens
when a ruling is left as a line in a summary list.*

**Do not renumber.** Twenty-six numbers were already quoted across `PROGRESS.md`
and seven session documents before these five existed.

---

## Ruling 27 — every case declares its expected behaviour, and the loader refuses to inherit it

`expected_behaviour` is a required key in `eval/gold/answer_cases.json`. A case
that omits it is a load error. It takes one of three values and nothing else:

```
answerable            the corpus holds it, so a red line is retrieval or assembly
correctly_refusable   the corpus does not hold it, so a red line means the model
                      invented something
refusable_with_gloss  the corpus holds it untranslatably, so a red line means a
                      machine translation appeared, attached to a citation
```

Those name three different pieces of news. Before this ruling a red line said
only *"this case failed"* and which of the three it was lived in a human's head.

**`expect_refusal` is KEPT, not derived from the label.** Two fields that must
agree are a guard; one field computed from the other is a guard deleted. The
loader refuses a disagreement in **both** directions, deliberately as two
clauses with two mutations: a `correctly_refusable` case that does not assert a
refusal, and a case asserting a refusal under any other label. Only the
assertion is scored, so where the two disagree it is the label that is wrong —
and the label is what a reader uses to decide what a red line means.

Two consequences worth stating because they are cheap to lose:

- **A case whose label says the answer should speak must require it to speak.**
  An exclusion alone is satisfied by silence: a refusal contains none of the
  strings a case excludes. `expect_answer_excludes` is a content assertion but
  not a positive one, and a non-refusal case built from exclusions alone is
  refused at load.
- **A `refusable_with_gloss` case must name the record whose published gloss the
  answer has to quote, and must declare its hedge in `expect_hedge_any`.** The
  hedge was previously one alternatives group among several, indistinguishable
  from content, and droppable by a later edit without anything noticing.

Mutation-verified: eight clauses, eight mutations, `scripts/mutate_part8.py`.

---

## Ruling 28 — the gloss arm is for a contested READING of a text, and nothing else

`refusable_with_gloss` means: the corpus holds the text, and what the text SAYS
is not settled. A red line on that arm means a machine translation appeared.

It does **not** cover uncertainty of other kinds. Contested attribution,
disputed dating, uncertain identification of a depicted figure and unresolved
provenance are all real uncertainties and none of them is this one. Where a case
needs the answer to preserve such a doubt, the doubt is required as **ordinary
content** — an `expect_answer_contains_any` group — on an `answerable` case.

Ruled at `sasanian-hunting-plate`, whose reign attribution is disputed between
Shapur I and Shapur II while nothing about its English description is. Applied
again at `khao-sam-kaeo-intaglio`, a carved gemstone with no text on it at all,
whose figure is "probably Mars". Applied a third time at
`hoby-silius-identification`: nothing about the letters SILIVS is contested; who
the man was is.

**Why the arm is kept narrow.** If it widens to any contested claim, a red line
on it stops naming one failure and starts naming several, and the specific
failure it was built to catch — *a machine translation, arriving attached to a
citation* — becomes one meaning among many. The count would improve and the
instrument would get worse.

There is also a mechanical reason, found at `sasanian-hunting-plate`: that
plate's attribution dispute lives on the source's **header line**, and the
prompt's rule 3 forbids quoting header lines so that an editorial description is
not presented as evidence. A case requiring the dispute would have required a
sentence the model cannot ground.

**The boundary case, recorded because it will be re-litigated:**
`hoby-cheirisophos-signature` quotes a Greek signature the corpus gives as
`[ΧEIPI]ΣΟΦΟΣ` — square brackets, an epigraphic restoration, sitting in a
retrieval-eligible chunk. It is `answerable`, not gloss. **Restored is not
contested.** The record supplies a confident published gloss and offers no
alternative reading, so a required hedge would be a hedge the evidence does not
argue for, and a case requiring it could never pass.

---

## Ruling 29 — a false premise the corpus can correct is ANSWERABLE

A question resting on something untrue, where the corpus holds the correction,
is an `answerable` case. Giving the correction is answering.

Ruled at `oc-eo-roman-coins`, which asks *"Were Roman coins found at Óc Eo?"*
They were not: the record calls them "costume jewelry rather than circulating
coinage" and "locally worn imitations/pendants of Roman coin types". Refusing
would be the wrong behaviour, not the safe one.

**The refusal arm means "the corpus cannot address this". It never means "the
question was badly posed."** Letting it mean the second turns refusal into the
reward for any awkwardly-worded question, and `floor.json` already names
citation hygiene bought with silence as a failure mode in its own right —
`max_refusal_rate` exists because a prompt that refuses more while erring no
less is a regression no metric built on grounding can see.

The question is phrased the way a reader would actually ask it, false premise
included. A case that asks the careful version of the question tests nothing.

---

## Ruling 30 — behaviour balance is held to the definitions, and the shortfall is recorded

`BLOCK_D_START.md` asks the 30 cases to be *"balanced across three expected
behaviours"*. The corpus holds roughly six records that can honestly carry a
`refusable_with_gloss` case. Balance at thirty is therefore not reachable
without widening what the label means.

**Ruled: write every gloss case the corpus can honestly support, fill the rest
with the other two arms, and record the shortfall in the result document with
the reason.** The stratification is the deliverable, not the count. A set
balanced by stretching a label is a set whose arms no longer name different
things, and the number would then be describing the labelling rather than the
corpus.

This is the same discipline as ruling 25, which accepted a sourcebook of 24–60
records rather than chase 200, and as `floor.json`'s refusal to drop
`vimose-runes` from `required_cases` after a bad session. **A criterion adjusted
until it is met has stopped being a criterion.**

The shortfall is a finding about the corpus and belongs in the write-up as one:
it says the seed corpus contains few texts whose reading is genuinely unsettled,
which is worth knowing before Block F decides what to add.

---

## Ruling 31 — a discriminator loads as one instrument, and `paired_with` means only that

`paired_with` is symmetric and enforced at load. The partner must exist, must
name this case back, and the two cases' **assertion blocks must be identical** —
everything in `_ASSERTION_KEYS`, which is every key that is part of the test.
`id`, `question`, `why`, `note`, `archived_status` and `paired_with` itself are
excluded, because **the question is the only thing the two halves are allowed to
differ on.**

That is the whole meaning of the Adulis discriminator. `aksum-exports` and
`adulis-exports` assert the same things about the same document; a run in which
the first fails and the second passes says the defect is in the
question-to-retrieval-to-answer path and not in the corpus. The reading survives
only while the two halves stay identical. Deleting one half is now a load error
rather than a silent halving; drift between the blocks is a load error rather
than a pair that has quietly stopped discriminating between two questions and
started discriminating between two tests.

**`paired_with` is NOT for two cases that happen to share a record.**
`skz-titulature` and `skz-roman-emperors` sit on `persia-01-skz` and are a
genuine pair in spirit — one question it can answer, one it cannot — but they
are not joined by the field, and must not be. They differ on every assertion.
The Adulis pair varies the QUESTION against one assertion block; the ŠKZ pair
varies what the record contains. Joining both under one field would make it mean
two things, and the loader could then enforce neither.
