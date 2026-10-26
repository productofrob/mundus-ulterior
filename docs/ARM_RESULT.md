# The sonnet arm — result

*2026-08-28, session `86a10af37a9f`, run in the F1 thread before F1 curated
anything. Decision 2's window closed as it was meant to: the arm is measured
beside the frozen archive `26e4a683`, and F3 has not moved it yet.*

```
165/165 complete    0 incomplete, 0 retried
corpus              26e4a683014bdf8a…  unmoved at both ends
archive             eval/arms/20260828T155443-p7-answer-v2r-r5-chat-strong-t1.json
arm block           chat-strong / anthropic/claude-sonnet-5 / temperature 1.0
                    quote_resolution 2026-08-28-article-added
floor               null, with floor_not_applicable naming both arms
calibrate_floor     ELIGIBLE, 4 sweeps, 3 dates — UNCHANGED by the arm
```

## The headline, and it is not the pass rate

```
haiku,  chat-default at 0, 396 runs   0.727272…
sonnet, chat-strong  at 1, 165 runs   0.763636…
```

Three points apart. **Eleven of thirty-three cases moved between them, five up
and five down.**

```
case                          haiku/12   sonnet/5
skz-titulature                    0/12       5/5    <- the Ardashir filiation
vimose-runes                      0/12       5/5
raqosh-epitaph                    0/12       5/5
oc-eo-cattigara                   0/12       4/5    <- CONFOUNDED, see below
aksum-exports                     0/12       1/5
oc-eo-roman-coins                 3/12       4/5
pattanam-dna-evidence             9/12       5/5

ezana-stone-geez                 12/12       0/5
illerup-roman-coins              12/12       0/5
shapur-drachm-imagery            12/12       2/5
khao-sam-kaeo-intaglio           12/12       2/5
muziris-cargo                    12/12       3/5    <- REQUIRED case
```

*Four sessions read 0.727272… and one of them was different. The pass rate
cannot see change.* That sentence was written about four haiku sessions. This is
its strongest demonstration: **two arms three points apart, and a third of the
gold set moved underneath.**

## Two of the eleven are not the arm

`eval/gold/answer_cases.json` was edited once today, at 15:32, in ruling
40-42's commit — **after all four haiku sweeps and before this run**. It touched
exactly two cases.

- **`oc-eo-cattigara` 0/12 → 4/5 is CONFOUNDED and must not be read as the arm.**
  Ruling 41 replaced the exclusions built from its own question. The move is
  the correction, not the model. What the arm adds is that it still fails 1 in
  5 — one run did not refuse.
- **`antikythera-absent`** lost one exclusion and did not move: 12/12 → 5/5.

The other nine movers have byte-identical case definitions on both arms.

**Ruling 40 aimed at `aksumite-coin-imagery` and did not reach it.** The
`article_added` match class was written from the archive to make that case's two
quotations resolve. On this arm it is 0/5 with **zero** resolved quotations in
every run — a different failure from haiku's, on a model that quotes differently.
Ruling 40 said the next sweep might score it differently. It scored it the same,
and the fix remains unverified against any live run.

## The mechanism is refusal, and it is two mechanisms wearing one number

```
refusal rate   haiku 144/396 = 36%     sonnet 44/165 = 27%
```

Four cases carry the entire difference, and reading the answers separates them
into two unrelated stories.

**Genuinely refuses less.**

- `vimose-runes` — haiku refused 12/12. Sonnet answers 5/5 with a real hedged
  gloss: *"harja" is "likely a personal name or 'comb'/'warrior'"*, *"possibly
  'Mari (the famous one) is the sword of Alla'"*. The gloss arm finally gets a
  gloss. This is behaviour, not detection.
- `aksum-exports` — still refuses 3/5, and names why: *"no source names Aksum;
  the closest material concerns trade goods exchanged at Adulis"*. One of the
  two non-refusing runs answered fully, with 16 resolved quotations.

**Does not utter the sentence.**

- `ezana-stone-geez` 12/12 → 0/5 is **not a fabrication and not a regression in
  behaviour.** Sonnet refuses correctly, in its own words, cited: *"the
  available source does not specify which of the inscription's three language
  versions the quoted text comes from… No transliteration or original-script
  rendering of the Ge'ez wording is provided in this source, only this
  English-language text"*. `expect_refusal` is a bare substring test for one
  canonical sentence, and it cannot tell a paraphrased refusal from an answer.

**So: 36% and 27% are not two refusal rates. They are two rates of uttering one
sentence.** How much of the nine-point gap is behaviour and how much is
detection cannot be separated from this archive without reading answers, and
that is a stated limit of this run.

This is **ruling 41's defect in the other direction.** Ruling 41 closed an
`expect_answer_excludes` that could not tell a claim from a refusal to make one.
`expect_refusal` cannot tell a refusal from an answer unless the refusal is
word-perfect — and the prompt hands the model that sentence verbatim precisely
so the detector can find it. Under the declared arm haiku honours the contract
100% of the time. Under this arm it does not.

---

## FINDING 28 — `expect_refusal` is a fixed-string test, and it is model-specific

**A correct, cited, precisely-worded refusal that does not utter the canonical
sentence is scored as an answer. The refusal rate is therefore not a measure of
refusal across arms; it is a measure of how often a model emits one sentence.**

`ezana-stone-geez` is the case that shows it. Twelve of twelve under haiku,
zero of five here, and the answer is right:

> "The available source on the Ezana Stone does not specify which of the
> inscription's three language versions the quoted text comes from… No
> transliteration or original-script rendering of the Ge'ez wording is provided
> in this source, only this English-language text [S5]."

That is what `refusal_is_correct_because` says the case exists to elicit —
`africa-01-ezana-stone` has one retrieval-eligible chunk and it is English.
The case scored it 0/5.

**This is ruling 41's defect in the other direction, and the symmetry is exact.**
Ruling 41 closed an `expect_answer_excludes` that could not tell a claim from a
refusal to make one, and the more precisely a refusal named what it declined to
assert, the more certainly it failed. `expect_refusal` cannot tell a refusal from
an answer unless the refusal is word-perfect, and the more fluently a model
refuses in its own words, the more certainly it fails.

**RECORDED, AND NOTHING IS CHANGED. That is the ruling.** Three things decided
it, on 2026-08-28, before F1 curated a single new case:

1. **The prompt hands the model that sentence verbatim, precisely so
   `assemble.refused` can detect it.** `answer/test_answer.py` asserts it: *"the
   refusal sentence is given verbatim, so `refused` can detect it."* It is a
   contract between the prompt and the detector, and under the declared arm
   haiku honours it in 144 refusals out of 144. A contract one arm does not
   honour is a fact about that arm.
2. **Widening the matcher means teaching it to interpret negation, which ruling
   41 explicitly rejected one level down** — *"a rule which has to be
   interpreted is a rule that will be broken, and inside a matcher it would be
   broken in silence."* That argument does not weaken because the defect is now
   pointing the other way.
3. **Tightening the CASES instead would re-score the frozen archive.**
   `answer_eval --archives` scores 396 archived runs against the definitions in
   force, so an assertion added to the eight `correctly_refusable` cases changes
   what the Block E archive says about runs nobody can repeat. That is the
   hazard ruling 40 named about `_resolved_quote_count`, and it is why ruling 41
   was written as a LOAD-TIME refusal rather than as a re-scoring.

**What it costs, stated rather than fixed.** The refusal rate is not comparable
across arms, and this run cannot say how much of 36% → 27% is behaviour and how
much is detection. `vimose-runes` is behaviour — the gloss is real and hedged.
`ezana-stone-geez` is detection. The other two were not separated, and reading
165 answers to separate them was not spent.

**What it does NOT touch.** Every archived number, because they are all on the
arm that honours the contract. Every gold case, because they are scored on that
arm. F1's curation, which writes cases against the declared arm and is
unaffected — but F1 now writes refusal cases knowing that `expect_refusal` tests
a sentence and not a behaviour, which is what a case author needs to know and
what this finding exists to tell them.

**And FINDING 26 has cross-arm evidence now.** *"The pass rate cannot see
change"* was established over four haiku sessions where two cases flipped and
cancelled. Here two arms sit three points apart with eleven of thirty-three
cases moved between them. The pass rate could not see that either.

---

## FINDING 29 — `eval/answer_runs/` pools arms, and a universal quantifier over it was a claim about one model that never had to say so

**Ruling 36 split the SWEEP file — `eval/arms/` against `eval/sweeps/` — and
left the per-run archive as one directory. The moment the arm landed, 165 runs
on chat-strong sat beside 511 greedy ones, and every assertion of the form
`every archived X fails` became a claim about two models.**

Found the way the Block D findings were found: by running an instrument, not by
reading one. `eval.test_answer_eval` went red on

```
FAIL GUARD every archived Aksum answer fails — including those the
     Part 7 checks called grounded
```

`aksum-exports` passed once in five on the arm. **The suite reported the arm's
RESULT as a broken guard** — the exact misreading `BLOCK_D_START` warns about,
where a true report invites a false diagnosis. Nobody had written anything
wrong; the assertion was written when the directory held one arm and did not
have to name it.

**Why the directory was not split, and why that stays.** `rescore_sweep`
rebuilds a summary from these files, and a per-arm directory would have to be
searched twice. The arm belongs on the ROW, where it already is —
`model_alias` and `temperature` have been on every payload since 2026-08-28 —
so the fix is a filter and not a move.

```
eval/answer_eval.payload_arm        the arm of ONE archived run, and how it is
                                    known: recorded / reconstructed / assumed
eval/answer_eval.archives_on_arm    splits the directory, and returns BOTH
                                    halves so a caller can assert that the
                                    filter excluded something
score_archives(archives=…)          scores a caller-supplied subset. Omitted,
                                    it reads the whole directory as before.
```

**Three states, not two, and the third is the honest one.** 396 legacy runs
carry no `model_alias` and are reconstructed from `serving_stack.model`, the
echo Block E correction 4 established cannot move. 115 older runs carry nothing
at all and fall back on the CODE argument ruling 36 already accepted — before
2026-08-28 `assemble` had no model parameter and the answer path could not send
another arm. Both land on the greedy default; they are not reported as the same
kind of knowledge.

**Guarded, and the guards are about the FILTER rather than about the cases.**
A filter matching everything makes the universals span two models; a filter
matching nothing makes them vacuously true, and vacuous truths are green. Both
are named and both are mutation-verified, along with a third that ignores a
recorded arm and reads today's runs as legacy greedy ones.

**A MISS, and it is the best thing in this finding.** Three mutations were
written against the filter and the third — *a recorded arm is ignored and every
run is read as greedy* — reported `MISS`: it broke the code and no guard
noticed. The reason is that ignoring a recorded `model_alias` falls through to
the serving-stack echo, and for the arm's 165 runs **that echo says
`chat-strong` too.** The filter still excluded them, every universal still held,
and a genuinely broken reading looked like a working one.

That is ruling 36's own argument arriving one level down and uninvited: *a
reconstruction that agrees is still not a reading*, and the difference has to be
ASSERTABLE or it has not been recorded. The guard that was missing asserts the
basis rather than the outcome — the 165 runs must be read from the row, and the
511 must be known two ways, both named. `eval.test_answer_eval` 331 → 333.

**The harness earned its keep here.** A MISS is not a failure of the mutation;
it is the harness saying a line of code has no witness. Nothing in the suite
would ever have gone red for this, and the echo would have gone on agreeing
until the day it did not.

**Three checks stay over the whole directory on purpose**: every run must be
scorable, and every archived question must have a gold case, whatever arm made
it. Only the per-case universals are filtered.

**What is still owed from this.** `python -m eval.answer_eval --archives` pools
arms in exactly the same way and now prints one report over two models. It is a
reporting path rather than a guard, nothing is denominated in it, and it is
recorded here rather than fixed in the same hour as the thing that found it.

## What the arm answers

**Is the answer path model-limited?** Partly — and not where the arm was
pointed.

```
MODEL-LIMITED       skz-titulature      0/12 -> 5/5   (ruling 42 refused to
                                                       touch this case, so the
                                                       move is entirely the arm)
                    vimose-runes        0/12 -> 5/5
                    raqosh-epitaph      0/12 -> 5/5   (F0: "this one looks like
                                                       the system". It was the model.)

NOT                 aksum-exports       0/12 -> 1/5   <- the case the arm was RUN FOR
                    aksumite-coin       0/12 -> 0/5
                    hoby-silius         0/12 -> 0/5
```

`aksum-exports` was the case that motivated the whole arm — 0/3 under four
prompts with the answer in published English in its own evidence block. A
stronger model at temperature 1 passes it **once in five**, and refuses three
times out of five while correctly naming what it cannot find. The attribution
to prompt and retrieval survives.

**The Adulis discriminator held on this arm**: `adulis-exports` 5/5 against
`aksum-exports` 1/5. The defect is still in the question-to-retrieval-to-answer
path and not in the corpus, measured on a second model.

## What it costs, and one number that refuses an easy reading

Four of the five regressions are ONE failure — `resolves at least 1 quotation to
characters on disk` — on `illerup-roman-coins`, `khao-sam-kaeo-intaglio`,
`shapur-drachm-imagery` and `aksumite-coin-imagery`. `muziris-cargo` is the
exception and fails on content: it omits `Cottonara`/`Kottanarike` in 2 of 5.

```
mean resolved quotations   haiku 1.58    sonnet 2.27
runs resolving ZERO        haiku 35%     sonnet 35%
```

**Identical.** The mean rose because sonnet quotes more copiously when it quotes
at all, not because it quotes more often. "The stronger model grounds better" is
not what this archive says.

## Stability

```
per-case      27/33 = 82%      (haiku, greedy: 0 unstable cells on all four days)
unstable      content 6, grounded 12
per-session   NOT MEASURED — one session, which is what the arm was scoped to
```

Six unstable content cells against greedy haiku's zero is temperature 1 doing
what temperature 1 does. It is not a finding. It is the reason the arm was run
at five repetitions rather than three.

## What this does NOT do

- **It does not move the floor.** Ruling 36, enforced in the archive: `floor` is
  `null` and `floor_not_applicable` names both arms. `calibrate_floor` reports
  ELIGIBLE on the same four sweeps and three dates it did before the run.
- **It does not move the default alias.** Every archived number stays haiku at 0.
- **It does not count toward any bar.** Ruling 37 measures promotion and
  reinstatement at the corpus in force and on the declared arm. `vimose-runes`
  passing 5/5 here is not a step toward reinstatement, and must never be read as
  one.
- **`muziris-cargo` at 3/5 is not a floor event.** It is a required case
  behaving badly on an arm the floor does not govern.

## What is owed

```
1  CLOSED as FINDING 28, above, on the day it was found and before F1 curated
   anything: recorded, and nothing changed. Read it before writing a
   correctly_refusable case.
2  floor.json's known_failing_cases evidence is now incomplete: two of the
   three (vimose-runes, skz-titulature) pass 5/5 on another arm, and the file
   attributes their failure without saying so.
3  ruling 40's article_added is still unverified against any live run.
4  muziris-cargo, REQUIRED, is 3/5 on this arm and stable on the other.
5  `eval.answer_eval --archives` pools arms into one report. FINDING 29 fixed
   the GUARDS and left the CLI, deliberately and in writing.
```

**Discharged in this thread, and both are recorded above rather than in a commit
message**: FINDING 28 and FINDING 29. `floor.json` now carries the cross-arm
observation beside all three `known_failing_cases` entries — two of the three
pass on chat-strong, and the file said nothing about it while attributing their
failure. Ruling 36 keeps every one of those numbers outside the floor, and
ruling 37 keeps `vimose-runes` passing 5/5 from being read as a step toward
reinstatement.

## The sentences that travel

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310.

**Four sessions read 0.727272… and one of them was different. The pass rate
cannot see change.**

**Nine archives, 396 runs, and not one of them recorded which model answered.**

And two from today:

**0.7273 and 0.7636 are three points apart, and eleven of thirty-three cases
moved between them.**

**36% and 27% are not two refusal rates. They are two rates of uttering one
sentence.**
