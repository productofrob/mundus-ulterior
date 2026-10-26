# D3 — result: the gold set goes from 6 cases to 33

*Written 2026-08-22. Every number here was measured on the host. Companion
documents: `D3_RULINGS.md` (rulings 27–31, full text) and `FINDINGS_9_TO_13.md`,
which covers the corpus and harness investigation that started after D3 had
closed and is deliberately kept out of this one.*

```
gold set               6  ->  33 cases
eval.test_answer_eval 98  ->  203
scripts/mutate_part8  23  ->  27
seed corpus digest    bcfa0211dcbe999a...   (changed by the Weilue fix; see the
                                             findings document)
```

## G4's stratification, computed by the suite rather than claimed here

```
cases                 33      wants >= 30
behaviours            22 answerable / 3 gloss / 8 correctly_refusable
Arabia 4   East Asia 5   Persia 4   Scandinavia 5
South Asia 5   Southeast Asia 4   Sub-Saharan Africa 5   outside 1
regions at >= 3       7 of 7
source languages      14      wants >= 6
loader-enforced pairs 2
```

`eval.test_answer_eval` computes the per-region tally itself and fails if any
region falls below three. **A gate checked against prose is a gate checked
against whoever wrote the prose**, and until the `region` field landed, eight
cases were invisible to that count while still contributing to the total — the
loader forbids `expect_quoted_docs` on a refusal case, so a refusal names no
document and nothing tied it to a region.

## What the three behaviours are for

Not three flavours of one thing. Three different pieces of news:

| label | the corpus | a red line means |
| :---- | :---- | :---- |
| `answerable` | holds it | retrieval or assembly failed |
| `correctly_refusable` | does not hold it | the model invented something |
| `refusable_with_gloss` | holds it untranslatably | a machine translation appeared, attached to a citation |

Before D2 a red line said only *"this case failed"*, and which of the three it
was lived in a human's head.

## Four species of correct refusal, and they were built deliberately

The eight `correctly_refusable` cases are not eight instances of one thing:

```
not in the corpus at all         antikythera-absent
in the corpus, no reachable      palmyrene-tariff-rates, ezana-stone-geez
text                             (both are `pointer` chunks, ineligible — the
                                  corpus's only two)
reachable, but the excerpt does  skz-roman-emperors, oc-eo-cattigara,
not hold what the record's own   pattanam-dna-evidence, weilue-ruler-selection
title and notes advertise
adjacency                        gudme-bracteate-runes
```

**The third species is the one a model is most likely to fail**, and the fourth
is the one a reader is least likely to catch. `skz-roman-emperors` asks which
Roman emperors the Res Gestae Divi Saporis names; the record's own notes say it
"directly documents Roman emperors (Gordian III, Philip the Arab, Valerian)" and
the excerpt on disk contains none of *Valerian*, *Gordian*, *Philip*, *emperor*,
*Rome* or *Roman*. A model retrieves it with high confidence, sees a Sasanian
royal *res gestae*, and can supply Valerian from its own weights.

`gudme-bracteate-runes` refuses by **adjacency**: the record does say "nine gold
bracteates", gold bracteates often carry Elder Futhark runes, and the corpus
holds `vimose-runes` as a template for what such an answer looks like. Its
excluded strings, `alu` and `laukaz`, are the formulaic legends that actually
recur on Scandinavian bracteates — exactly what a model would supply.

In every case the excluded strings are **wrong about this corpus, not about
history**, which is why none of them may ever be softened on the grounds that the
answer is correct.

## Two loader-enforced pairs, discriminating on different axes

```
aksum-exports / adulis-exports          varies the WORDING of an English question
akananuru-yavana-ships / -tamil          varies the LANGUAGE it is asked in
```

Both carry byte-identical assertion blocks against one record, enforced at load
under ruling 31. The Tamil pair is the set's first non-English question, and a
run where the Tamil half passes and the English half fails puts the defect in
cross-lingual retrieval and nowhere else — not the corpus, which holds the poem,
and not the answer path, which just answered the same question about the same
record.

**The Tamil question is a verbatim phrase from the poem, not an interrogative
sentence.** It is the already-ranked `probe-tamil-akananuru` string, which buys a
known-good retrieval half and invents no Old Tamil that nobody on this project
can check. If someone who reads Tamil supplies a real interrogative, replace the
question string and **nothing else** — the loader will refuse a drifted pair.

## The behaviour balance is NOT met, and was not negotiated

**3 gloss cases against 22 answerable.** Ruling 30 governs this: write every
gloss case the corpus can honestly carry, fill the rest with the other two arms,
and record the shortfall rather than widen a label to meet a number.

The arm needs a text whose **reading** is unsettled. The seed corpus holds three:
`vimose-runes` (partly undeciphered Elder Futhark), `raqosh-epitaph` (two
competing scholarly readings, stated inside the retrieval-eligible chunk), and
`oc-eo-medallion-legend` (a corrupt Latin coin legend with an alternative reading
and a curator's note that it is corrupt).

**That shortfall is a finding about the corpus, not about the case set**, and it
is worth knowing before Block F decides what to add: this seed corpus contains
very few texts whose reading is genuinely in dispute.

Ruling 28 was applied three times to keep the arm narrow — `sasanian-hunting-plate`
(contested attribution), `khao-sam-kaeo-intaglio` (contested identification of a
carved figure), `hoby-silius-identification` (contested identification of a
person). Each required its uncertainty as ordinary content instead. Widening the
arm would have hit the balance target and cost the arm its meaning.

## The boundary case, recorded so it is not re-litigated

`hoby-cheirisophos-signature` quotes a Greek signature the corpus gives as
`[ΧEIPI]ΣΟΦΟΣ` — square brackets, an epigraphic restoration, in a
retrieval-eligible chunk. It is `answerable`, not gloss. **Restored is not
contested**: the record supplies a confident published gloss and offers no
alternative, so a required hedge would be a hedge the evidence does not argue
for, and the case could never pass.

## Deliberate known failures

Two cases are expected to fail and say so in the file before they were ever run.
Both are tracked in `floor.json.known_failing_cases` as **open defects, never
tolerated ones**, and both are kept out of `required_cases` so that a floor pass
can never be read as *"the system does this"*.

- **`aksum-exports`** — unchanged from Phase 1. Seven consecutive refusals under
  four prompts, against evidence overlapping that of the passing `adulis-exports` in four of six passages. **CORRECTED 2026-08-25, FINDING 17 — the phrase here was "byte-identical" and the archives never supported it; the ASSERTION blocks are byte-identical, the EVIDENCE is not. See `FINDINGS_14_TO_18.md`.**
- **`weilue-chinese-quotation`** — added 2026-08-22. Fails because nothing in the
  answer path ever asks for a non-English source text to be quoted. See
  `FINDINGS_9_TO_13.md`, finding 13.

Two more are expected to be hard but are not yet classified as known failures,
because they have never been run: both halves of the Akanāṉūṟu pair. Part 4
scored Old Tamil at 0.368 against 0.6–0.7 for other scripts. **Neither goes into
`required_cases` until both are seen passing across sessions.**

## What Block E inherits

```
33 cases, stratification met and machine-checkable
2 loader-enforced pairs
2 known-failing cases, both open defects
floor.json          calibrated: false, four required cases, unchanged
corpus digest       bcfa0211dcbe999a...   record on day one, re-assert on day three
```

Three things Block E must not do, carried from `BLOCK_D_START` and reinforced by
this session:

1. **Change nothing between days** — and that list must name `scripts/schema-part7.sql`,
   which `run_answer.py:234` re-applies on every one of ~90 calls a day.
2. **Do not read a green sweep as a calibrated floor.** All three archived sweeps
   are within-session; `calibration_invalidated` still stands.
3. **`run_answer.py` takes the question as a positional argument.** There is no
   `--question` flag, and a sweep script written against one fails after the
   gateway is up.

## Open, and deliberately not closed

- **Behaviour balance unmet**, 3 gloss against 22 answerable, under ruling 30.
- **`match_case` returns the FIRST case whose question matches.** Two cases
  sharing a question would leave the second silently unscored against every
  archive — sitting in the gold set looking like a test and never running. Avoided
  by hand in `weilue-chinese-quotation`; unguarded in the loader.
- **The Akanāṉūṟu Tamil question is a phrase, not a sentence**, pending someone
  who reads Tamil.
- **`aksum-exports` remains an open defect.** Nothing in D3 closed it and nothing
  should be recorded as closing it.
- **Rulings 20 and 21 still have no full text.** Unchanged by this session; the
  code remains the authority and no prose is.
