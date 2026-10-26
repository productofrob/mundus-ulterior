# F0 — the four decisions, settled before F1

*2026-08-28, from `e207e65`. `BLOCK_F_START.md` left four decisions open on
purpose and named the window that closes at the first sub-tranche. All four are
settled here, all four are recorded in the artefacts that enforce them, and
none of this is Block F. Rulings 36-39 carry the reasoning; `F0_RULINGS.md` is
the authority for their text.*

## What was found before anything was decided

The state `BLOCK_F_START` records is accurate — 24 records, 33 cases split
22/3/8, nine archived sweeps with five excluded by rule, one decomposition,
`calibrated: true` with the 31/33 in the file. Correction 8's owed follow-up is
discharged: `probe_serving_stack.py` sends `translate.DEFAULT_MODEL`.

Three things it does not record.

### 1. `PROGRESS.md` is two blocks stale, and its reading list points at it

`PROGRESS.md` ends at 2026-08-21, *"Block D — TASK 0 and TASK 1"*, at tree
`f54c585` and corpus digest `2e84436c`. D2, D3, D4 and all four Block E
sessions are absent. `BLOCK_F_START`'s reading list sends the next thread to
*"PROGRESS.md last section only"* — which today hands them Block D's state and
a digest that is not the one every Block E number is denominated in. **Open.
Not fixed here.**

### 2. THE ARM WAS NEVER RECORDED, AND THE ANTI-LOOPHOLE WOULD HAVE FORCED THE SONNET SWEEP INTO THE FLOOR

The reason decision 2 could not simply be answered "yes, run it".

Not one of the nine archived sweeps records which model or which temperature
produced it. Every Block E number is denominated in an arm that was a fact
about the code on the day rather than about the file — FINDING 14 one layer up.

That gap is not merely untidy. `calibration_scope`'s anti-loophole,
`a_named_sweep_must_actually_fail_the_rule`, refuses an exclusion naming a
sweep that SATISFIES the rule — declared 2026-08-26 so the exclusion list could
not become *"a place to put a sweep whose numbers nobody liked."* The rule had
two clauses: a session identity, and ≥30 cases. **A sonnet arm at temperature 1
satisfies both.** So `eval/calibrate_floor.py`, which globs `eval/sweeps/*.json`
and pools every row it finds, would have taken it — and the guard against
hiding numbers would have made it impossible to exclude by name.

Running the arm before closing this would have contaminated the one archive the
whole block is denominated in. Closed by ruling 36, before the arm runs.

### 3. All four of decision 3's cases fail 0/12, each on exactly ONE assertion

`BLOCK_F_START` calls them *"day 1's four unregistered failures"*. They are not
day 1's: each is 0/12 across four sessions and three dates, deterministically,
and each fails on a single assertion while satisfying every other. See below.

## Decision 1 — G3's checklist. AMENDED, in advance

Adopted with two clauses added. `PHASE2_PLAN.md`'s G3 checklist now carries
per-session stability at 60 and cross-session answer-text agreement at 60,
beside the pass rate rather than instead of it. Ruling 39.

- the agreement number is gated on **Block F's own sessions at 60**. Block E's
  74–77% and 45% are context, not a threshold: they were generated over 24
  records, so at 60 the evidence blocks differ by construction and a
  cross-corpus comparison would be measuring the corpus move it was written to
  survive.
- **the amendment costs a second session, and it is booked with it.**
  Cross-session agreement has no meaning inside one sweep. G3 needed one sweep
  at 60; it now needs two sessions on two distinct UTC dates, ~198 chat calls.
  *Before anything else* item 4 says the days are the scarce resource.

## Decision 2 — the sonnet arm. RUN IT, in the window, after ruling 36 lands

33 cases × 5 repetitions at temperature 1 through `chat-strong`, one session,
its own archive, its own gate, never folded into the haiku archive. ~165 calls.
Full case set rather than a targeted subset, so the arm produces a content pass
rate comparable in composition to the 0.727272… four haiku sessions returned —
a targeted arm answers "is this case model-limited" and cannot answer "is the
answer path model-limited", which is the question runbook 3b actually poses.

**It must run before the first sub-tranche.** `26e4a683` is the denominator of
all 396 Block E runs and F3 moves it.

What landed to make it safe, all of it before the arm runs:

```
answer/assemble.py        temperature and temperature_fallback, ruling 22's
                          contract unchanged: opt-in, recorded, never dropped.
                          AssembledAnswer carries model_alias and the
                          temperature ACTUALLY USED, not the one requested.
run_answer_sweep.py       --model, --temperature, --temperature-fallback.
                          The arm is on the sweep archive AND on every row.
                          A non-default arm archives to eval/arms/ and must
                          carry --session-label.
                          resolve_model_label now resolves the alias BEING
                          SENT — it resolved chat-default whatever was sent,
                          which is correction 4's defect in the other
                          direction.
answer_eval.sweep_arm     the arm, and how it is known: `recorded` for
                          anything archived from today, `reconstructed` for
                          the nine (alias read from serving_stack.model,
                          temperature assumed 0 and labelled as assumed),
                          `unidentifiable` otherwise — which BLOCKS.
calibration_eligibility   a foreign arm fails the rule. It can then be
                          excluded by name, legitimately, because it really
                          does fail it.
_decomposition_rows       refuses to pool two arms, on the prompt-version
                          refusal's argument.
floor.json                calibration_scope.arm = chat-default at 0,
                          declared_on 2026-08-28, BEFORE the arm ran.
```

The four Block E sweeps still calibrate: `python -m eval.calibrate_floor`
reports ELIGIBLE, four sweeps, three dates. **The clause does not de-calibrate
a floor by arriving**, and there is a guard that says so.

The directory split is a convenience and is **not** the guarantee. The
guarantee is the scope rule, which refuses a foreign arm even if the file is
moved into `eval/sweeps/` by hand.

## Decision 3 — the assertions. MEASURED, from the archive, at zero chat calls

`scripts/assertion_audit.py` re-reads the archived answers against the
assertions that failed them. It makes no chat call, touches no database and
needs no gateway. Run:

```powershell
python scripts\assertion_audit.py
python scripts\assertion_audit.py --all-failing
```

**All four cases fail 0/12, deterministically, each on exactly one assertion.**

### `oc-eo-cattigara` — the assertion is wrong, and it is not close

`BLOCK_F_START` records this as *"refused correctly without saying 'Ptolemy's
Cattigara'"*. **That is backwards.** It refused correctly and DID say it, in
the sentence saying the sources do not support it:

> "…but they do not address whether Óc Eo was identified as Ptolemy's
> Cattigara or discuss Ptolemy's geography at all."

`expect_answer_excludes` is a bare substring test. **It cannot tell a claim
from a refusal to make it**, and the more precisely a refusal names what it is
declining to assert, the more certainly it fails. This is a textbook correct
answer scored as a violation.

### `aksumite-coin-imagery` — the answer is right and the quotation is real

Every content assertion passes. It fails only on quotation resolution, 0
resolved quotes. The audit's ladder locates both quotations in
`africa-02-aksumite-coin.original_text_excerpt`, case-folded, under one
transformation:

```
answer  'a half-length bust of Ezanas right, crowned, holding stick or …'
record  'Half-length bust of Ezanas right, crowned, holding stick or …'
```

**The model prepended an article.** `answer/cite.locate_in_text` already
forgives whitespace, case and edge punctuation — *"the three things a writer
alters when fitting a quotation into a sentence of their own"* — and an added
article is the fourth thing sitting right beside them, and is not forgiven.

**This is not a decision the audit takes.** Tolerating it means the resolver
attributes to a source an article the source does not have, and
`mutate_part8.py` already records why loosening a matcher is not kindness. It
is a ruling, and it is open.

### `skz-titulature` — the assertion asks for something the question does not

The answer gives "king of kings of Iran and Not-Iran", "lord of Iran", "the
Mazda-worshipping god", four resolved quotations. It satisfies two of the three
`expect_answer_contains_any` groups and fails on `['Ardashir', 'Ardašīr']`.
The question is *"What titles does Shapur I claim"*. Ardashir is his father,
named in the genealogy. **Open, and it is a question about the case, not the
system.**

### `raqosh-epitaph` — this one looks like the system

`refusable_with_gloss`, and the required hedge is about competing readings. The
answer quotes the epitaph and the curse, resolves two quotations, and states one
reading flat with no hedge at all. The gloss arm has teeth and they are in the
right place. **Not an assertion defect on this evidence.**

**So: three of the four are the assertion or the resolver, and they are three
different defects, not one style of over-tightness.** That is the answer
decision 3 wanted before 36 new records are written against the same style, and
it was available for the cost of reading files.

## Decision 4 — the bar, and `weilue-chinese-quotation`. RAISED, and moved

One bar, both directions: **3/3 in each of three sessions on three distinct UTC
dates, at the corpus in force.** Raised from two-on-two by FINDING 26 — a case
unanimous across three sessions flipped on the fourth. Three is
`min_distinct_dates`, reused rather than invented. Rulings 37 and 38.

`weilue-chinese-quotation` leaves `known_failing_cases` — it does not fail —
and enters a new `promotion_candidates` state rather than `required_cases`. Its
twelve passes are all denominated in `26e4a683`, and Block F replaces that
corpus; a regression gate guaranteed by an archive nobody can re-run is not a
gate. `eval/goldset.py` refuses a candidate that is also required, a candidate
that is also known-failing, and a candidate with no written bar.

`demotions.vimose-runes.reinstated_when` carries the same raised bar, with the
superseded text kept beside it.

## What is owed, and is not fixed here

```
1  PROGRESS.md is two blocks stale and BLOCK_F_START points the next thread
   at its last section.
2  the sonnet arm has not run. The window closes at the first sub-tranche.
3  the baseline check that mutate_part8 gained on 2026-08-28 is not in the
   other five harnesses. Nothing is known to be wrong with any of them, which
   is the point.
```

CLOSED THE SAME DAY, as rulings 40, 41 and 42 â the three case-and-matcher
questions this list opened with. They belonged before curating 36 new records
against the same style of assertion, which is exactly what decision 3 said to
establish first. `F0_RULINGS.md` carries them. Ruling 41 turned up a second
case while it was being written: `antikythera-absent`, REQUIRED and passing
12/12, carried the same hazard and was one refusal phrasing from failing.

## The sentence that travels

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT
was reachable. `muziris-cargo-akananuru` still sits at rank 310.

**Four sessions read 0.727272… and one of them was different. The pass rate
cannot see change.**

And one from today, which travels with them now:

**Nine archives, 396 runs, and not one of them recorded which model answered.**
