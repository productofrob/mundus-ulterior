# Rulings 36 to 39 — declared 2026-08-28, before F1

*Written in the session that made them, for the reason `RULINGS.md` records
about rulings 20 and 21: a ruling that exists only as a line in a summary list
is a ruling nobody can quote, check, or argue with later. All four settle
questions `BLOCK_F_START.md` left open ON PURPOSE, and all four are settled
BEFORE the first sub-tranche moves the corpus, because `BLOCK_E_RUNBOOK` states
the rule this project runs on: anything unsettled on day 1 stays unsettled for
the whole block or costs the whole sweep.*

---

## Ruling 36 — the ARM is part of a sweep's identity, and part of the calibration scope

**A sweep's arm is the pair `(model alias, temperature)`. It is recorded in the
sweep archive and on every row. A sweep whose arm differs from the one
`floor.json.calibration_scope.arm` declares cannot calibrate the floor, and two
arms cannot be pooled into one variance decomposition.**

### The defect this closes is not the one it looks like

The obvious risk is that a sonnet arm might calibrate the floor by accident.
That is not what was found. What was found is that **`floor.json`'s own
anti-loophole would have insisted on it.**

`calibration_scope.a_named_sweep_must_actually_fail_the_rule` refuses an
exclusion that names a sweep which SATISFIES the rule — declared on 2026-08-26
because otherwise `excluded_by_rule` is *"a place to put a sweep whose numbers
nobody liked."* That guard is right and stays. But the rule it enforces had two
clauses: a session identity, and at least 30 cases. A sonnet arm at temperature
1 carries a session identity, runs the full 33 cases and archives complete.
**It satisfies the rule.** So the guard built to stop inconvenient numbers being
hidden would have made a temperature-1 sonnet sweep impossible to exclude from
a floor calibrated on greedy haiku.

The arm had to enter the rule, or the anti-loophole becomes the loophole.

### What the nine archived sweeps say about their arm: nothing

Not one of the nine records a model or a temperature. Every number Block E
published is denominated in an arm that was a fact about the code on the day
rather than about the file. That is FINDING 14 one layer up — a corpus version
that lived in the runner instead of in the run — and it went unnoticed for the
same reason: while only one arm has ever run, the field is invisible.

`eval.answer_eval.sweep_arm` reconstructs the arm for those nine, from evidence
on disk, and **says which half is read and which is assumed**:

- the **alias** is read from `serving_stack.model` on the rows. Block E
  correction 4 established that this field is the echo of the string SENT and
  cannot move — useless as a drift detector, and for exactly that reason a
  faithful record of what the sweep asked for.
- the **temperature** is not in the archive at all. It is assumed to be 0
  because `answer.assemble.assemble` had no temperature parameter until
  2026-08-28 and the answer path could not send another value. **That is a
  claim about the code, not a reading of the file**, it is labelled
  `reconstructed` rather than `recorded` in every report, and it is available
  only to sweeps that predate the change.

A sweep archived after 2026-08-28 must state its arm or fail. Reconstruction is
not a free pass: a legacy sweep whose rows echo a different alias fails the
clause too, and a sweep with no arm block and no alias anywhere is
`unidentifiable` and blocks rather than being read as the default.

### What it does NOT do

It does not make the sonnet arm inadmissible evidence. It makes the sonnet arm
inadmissible **as a calibration input to a floor set on a different model**. The
arm archives to `eval/arms/`, reports its own numbers, and is read beside this
floor and never inside it.

**Guarded:** `GUARD a sweep on another arm cannot calibrate, even when it
satisfies every other clause of the rule`; `GUARD a sweep whose arm cannot be
identified at all blocks, rather than being read as the default`; `GUARD
reconstruction is not a free pass…`; `GUARD a decomposition refuses to pool two
arms`; `GUARD a half-declared arm clause is refused…`. Five mutations in
`scripts/mutate_part8.py`.

**Not guarded, and said so:** `run_answer_sweep` archives a non-default arm to
`eval/arms/` rather than `eval/sweeps/`. That is a convenience, not the
guarantee. The guarantee is the scope rule, which refuses a foreign arm even if
someone moves the file across by hand — which is what a guard should protect
against and a directory cannot.

---

## Ruling 37 — one bar governs promotion and reinstatement: 3/3 in each of three sessions on three distinct UTC dates, at the corpus in force

**A case may not enter `required_cases`, by promotion or by reinstatement, on
less than three sessions of unanimous passes across three distinct UTC dates,
measured at the corpus the floor will be defending.**

Raised from two sessions on two dates. The evidence for raising it is direct
and is FINDING 26: on 2026-08-28 a case unanimous across THREE sessions flipped
on the fourth. Two dates of agreement is a bar this project has watched fail.

**Three is not a new number.** It is `min_distinct_dates`, which `floor.json`
already imposes on its own calibration. Reusing it is deliberate: a bar invented
for one case is a bar chosen for that case.

**Decided once, for both directions.** `demotions.vimose-runes.reinstated_when`
and `promotion_candidates.weilue-chinese-quotation.bar` carry the same sentence,
settled on the same day, rather than each being settled on the day its case
happened to be in front of someone. `promotion_and_reinstatement_bar` states it
at the top level of the file as well, because a standard that exists only inside
the record of the case it was applied to is a standard the next case gets to
renegotiate.

**"At the corpus in force" is the clause that does the work here.** All twelve
of `weilue-chinese-quotation`'s passes are denominated in `26e4a683`, 24
records, and Block F replaces it. Promoting a case into `required_cases` on
evidence from a corpus that is about to be replaced is how a regression gate
comes to be guaranteed by an archive nobody can re-run.

---

## Ruling 38 — the promotion-candidate state

**`floor.json` has a third state for a case: not required, not known-failing.
It is reported beside the floor verdict and counts toward neither side of it.**

It exists because the file spent two days asserting the opposite of what it had
measured. `known_failing_cases.weilue-chinese-quotation` said the case fails,
and its own corrected text recorded that it passes 12/12 across four sessions
and three dates. Block E kept it there deliberately — promoting a case while
correcting a floor error is how errors compound — but the reason it had nowhere
better to go is that **no state fitted**, and a file with two states will keep
producing that contradiction.

`eval/goldset.py` refuses a candidate that is also in `required_cases`
(waiting for the bar and counted as having met it), a candidate that is also in
`known_failing_cases` (the exact contradiction this ends), and a candidate with
no written `evidence` and `bar` — which is the demotion rule pointing upward. A
candidate with no written bar is a case that gets promoted whenever someone next
looks at it.

**Guarded:** three guards in `eval/test_answer_eval.py`, two mutations.

---

## Ruling 39 — G3 is amended in advance, and the amendment is costed with it

**The G3 checklist gains two boxes: per-session stability at 60, and
cross-session answer-text agreement at 60. Both are reported beside the content
pass rate. The pass-rate box stays.**

Day 3 is the counter-example the original checklist cannot see: a sweep at 60
records could return `0.727272…` having changed the system's behaviour
completely, and that box would tick. Both new numbers already exist, are
archived, and are mutation-verified; computing them costs nothing.

**Two clauses were added to the proposal in `BLOCK_F_START`, and both matter.**

1. **The agreement number is gated on Block F's OWN sessions at 60.** Block E's
   74–77% and 45% are reported beside it as context and are not a threshold.
   Those figures were generated over 24 records; at 60 the evidence blocks
   differ by construction, so the answer text differs by construction, and a
   gate comparing across the two corpora would be measuring the corpus move it
   was written to survive.

2. **The amendment costs a second session at 60, and the days are booked now.**
   Cross-session agreement has no meaning inside one sweep, and per-session
   stability inside one sweep reads NOT MEASURED. G3 as written needed one
   sweep at 60; amended it needs two sessions on two distinct UTC dates, ~198
   chat calls. Item 4 of *Before anything else* says the days are the scarce
   resource — a block that discovers on its last afternoon that it owes a
   second date has already failed the gate it was trying to pass.

**Recorded before F1 and not at the end.** A gate amended after its numbers are
in is a gate fitted to its result, which is the same move
`calibration_scope.declared_on` refuses one level down.

---

# Rulings 40 to 42 — declared 2026-08-28, before F1 curates anything

*The three questions `F0_RESULT.md` left open. Each decides what a whole family
of the 36 new records will be scored against, which is why they are settled
before the records are written rather than after.*

---

## Ruling 40 — an article the writer added to a quotation is a NAMED match class, and it resolves

**`answer/cite.locate_in_text` gains a fourth match class, `article_added`,
tried last. The span covers the characters found in the record and not the
article in front of them, so it still round-trips. It counts as resolved. It is
never reported as `exact`.**

`locate_in_text` already forgives whitespace, case and edge punctuation, on the
stated ground that these are *"the three things a writer alters when fitting a
quotation into a sentence of their own"*. An added article is the fourth, from
the same cause: `The gold coin shows "a half-length bust of Ezanas…"` against a
record opening `Half-length bust of Ezanas…`. Refusing it while forgiving the
case-fold that arrives with it is incoherent — both edits are one act.

Found from the ARCHIVE, by `scripts/assertion_audit.py`, not from a live run:
`aksumite-coin-imagery` failed 0/12 across four sessions and three dates, every
content assertion passing, on `resolves at least 1 quotation to characters on
disk`, with both quotations sitting in
`africa-02-aksumite-coin.original_text_excerpt` one word away.

**The serious argument against, and why it lost.** `expect_min_resolved_quotes`
is the floor the product's central claim rests on, and this project's instinct
is to record rather than forgive — `mutate_part8.py` already says of a matcher
that punctuation tolerance *"sounds like kindness and is not"*. The answer is
the same one C1a gave for case folding: the span is exact over the record's own
characters, and it is the RENDERING that differs. The alternative is scoring a
verbatim, correctly-cited quotation as a fabrication.

**Leading articles only.** A stripped trailing article would let a quotation end
short of what it claims to quote, and nothing observed asks for it.

**What this does NOT do.** `_resolved_quote_count` reads the spans an answer
archived, so nothing is re-scored: `aksumite-coin-imagery` stays 0/12 in the
Block E archive and the next sweep may score it differently. That is the arm's
defect in another costume — a fact about the code on the day rather than about
the file — and it is closed the same way. `cite.QUOTE_RESOLUTION_CONTRACT`
carries a dated string, the sweep archive records it beside the arm, and a
comparison across two contracts has to say so.

**Guarded** in `answer/test_answer.py` (three mutations in
`scripts/mutate_part7b.py`) and in `ui/test_build_ui_data.py` (one in
`scripts/mutate_ui_places.py`).

**CORRECTED the same day, before this document had been read twice.** The
sentence here first said the UI path put such a span in `absent`, the state
`--verify` fails on. It does not. `classify_span._same_characters` tests
containment in EITHER direction, so `Half-length bust…` counts as "the same
characters" as `a half-length bust…` and the span landed in `case_only` — a
labelling defect, reported and not fatal. `absent` is what it would be under
equality, which is the more obvious reading of that function and not the one it
implements. The branch had to move ABOVE the case-folding test rather than
below it, and the guard's own wording was corrected with it. The claim was
written from reading the code and not from running it; the first run of the
suite is what caught it.

---

## Ruling 41 — on a `correctly_refusable` case, an exclusion may not be built from the case's own question

**`eval/goldset.py` refuses, at load time, an `expect_answer_excludes` entry on
a `correctly_refusable` case whose content words all appear in that case's own
question. The stopword list lives in `answer_cases.json`, where widening it is
a diff.**

A correct refusal restates the question it is refusing. `expect_answer_excludes`
is a bare substring test and cannot tell a claim from a refusal to make it — so
the more precisely a refusal names what it declines to assert, the more
certainly it fails. `oc-eo-cattigara` refused correctly twelve times out of
twelve and said *"…they do not address whether Óc Eo was identified as
Ptolemy's Cattigara…"*, which trips `"Ptolemy's Cattigara"`.

**Writing the guard turned up a second case, and that is the argument for a rule
rather than a correction.** `antikythera-absent` — REQUIRED, passing 12/12 —
excluded `"Antikythera mechanism was built"` against its own question *"When was
the Antikythera mechanism built?"*. It was one refusal phrasing away from the
same failure, and nothing anywhere would have said why.

**Not a negation detector.** The prompt notes already record that a rule which
has to be interpreted is a rule that will be broken; inside a matcher it would
be broken in silence. This is a rule about how a CASE is written.

**What a refusal case should exclude instead:** fabrication markers — a name, a
date, a technical term the corpus does not hold. Seven of the eight
`correctly_refusable` cases already do exactly that (`"Valerian"`,
`"West Eurasian"`, `"laukaz"`, `"87 BC"`). `oc-eo-cattigara` now excludes
`identified as Cattigara`, `Golden Chersonese`, `Geographia`, `Sinae`, all four
verified absent from the seed corpus. `expect_refusal: true` is what carries the
case, and it passed 12/12 throughout.

Both corrections are recorded in `excludes_corrected_on`, beside the lists they
changed, because a correction that lives only in a commit message is one the
next reader of the file does not have.

---

## Ruling 42 — `skz-titulature` is tracked as an open defect, not corrected away

**It stays as written, the Ardashir group stays asserted, and the case enters
`known_failing_cases` with its evidence.**

0/12 across four sessions and three dates, on one assertion, while satisfying
every other assertion it makes and resolving four quotations. The evidence was
in front of it: `persia-01-skz` §1 is a single titulature formula — *"I, the
Mazda-worshipping god Shapur, king of kings of Iran and Not-Iran, whose race is
of the gods, son of the Mazda-worshipping god Ardashir, king of kings of Iran,
whose race is of the gods, grandson of the god King Pabag, am lord of Iran"* —
and the answer quoted from that sentence and stopped at Shapur's own epithets,
dropping both genealogical clauses.

**Rejected: dropping the Ardashir group.** That is the floor lowered to what is
currently passing, on the strength of a case that has never passed — the move
`required_cases_note` forbids.

**Rejected: amending the question to ask for the filiation.** `match_case` joins
archived runs on question text, so it would orphan the twelve archived runs and
the case would stop being comparable with anything in the Block E archive.

**The weaker half of this is the QUESTION.** *"What titles does Shapur I claim"*
does not plainly ask for the filiation. That is a note for how the 36 new
records are written — a case whose assertion asks for more than its question
does is a case that will fail for a reason no reader can see — and it is not a
licence to rewrite this one.
