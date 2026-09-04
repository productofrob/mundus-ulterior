# F5 — closed 2026-09-04 at `6c7b7cd`, and it curated nothing

**That is the headline and it is not an apology.** F5 was allocated seven
records and examined no candidate. What it did instead was discover that three
of the block's targets were already unreachable, that all three were one
shortfall counted three times, and that two of the three could be met by moving
slots the plan already had rather than by finding records nobody has.

The seven records are still allocated. Every one of them is now findable in a
place somebody has argued for.

---

## The state, at one commit and one interpreter

**Nine suites, on the host, at `6c7b7cd`.** F4's handover state block was a
stitch of three trees and two interpreters, and FINDING 57 — arrived at in that
same block — is the rule it broke. This one is a single measurement.

```
ingest.verify                    green -- 35 documents, 82 chunks, 23 parallel pairs
ingest.test_fidelity              77      ingest.test_cost              64
eval.test_answer_eval            413      eval.test_ranking_check      258
answer.test_answer               150      ui/test_build_ui_data.py      19
scripts/test_recover_baseline.py  56      scripts/test_harnesses.py     43
```

**Mutation harnesses: `mutate_ranking` 111 verified at `bf85a4f`,
`mutate_fidelity` 60 verified at `fedb2c9`.** Neither is re-run at `6c7b7cd`,
and the reason is stated rather than assumed: the only commit between them and
HEAD changes two comments, no guard, no number and no assertion. That is a
claim about a diff, and it is the kind of claim FINDING 47 says to write down
rather than leave implied.

```
suite                        F4 close    F5 close
ingest.test_fidelity              58          77
eval.test_answer_eval            410         413
eval.test_ranking_check          253         258
scripts/test_harnesses.py         33          43
mutation harnesses           389 total   397 total   (ranking 108->111, fidelity 46->60)
```

## The corpus, unchanged, and the plan around it, changed

```
corpus                        35 records, digest unchanged, nothing curated
reachable at F7's close       56 against a target of 60
verbatim_machine_english       6 of 10 -- the whole of the shortfall
every other tier              lands exactly on its target

source-language records per region at the block's close, floor of 4:
   Arabia 5   East Asia 7   Persia 4   Scandinavia 4   South Asia 5
   Southeast Asia 4   Sub-Saharan Africa 4        SEVEN OF SEVEN
```

**Two regions were below that floor this morning and none is now**, and no
record was added to do it.

---

## What was decided — rulings 67 to 73

**67. The deferred `verbatim_machine_english` ruling.** FINDING 41 NARROWS to a
rule about where a hunt looks. Taken on the DELIVERY record and not on the
experiment ruling 53 designed, which ruling 63 records as never having run —
and F5 says so rather than letting the two wear the same clothes. Every vme
record that landed came from a region where a structural gap in English
scholarship had been named before the hunt; every slot that failed was in a
tradition FINDING 41 itself named, or failed on supply. Three of three against
zero of four. Arabia's F5 slot moved to East Asia, onto FINDING 45's seam.

**68. The gloss target, re-denominated to 7**, by two independent routes that
agree. `check_allocation`'s gloss clause relaxed from an equality, because a
plan with no slack against a target fails on the first miss and Block F has
closed two sub-tranches short. FINDING 51's guard now counts DECLARATIONS as
well as slots and **names which one binds**.

**69. The corpus lands at 56, recorded as missed.** `total_at_60` not lowered.
Amended the same day by ruling 73 — in place, with what it said kept.

**70, 71, 72. Three predictions**, registered before any candidate was examined
and denominated in the F4 archive rather than in any document. Two of them are
checkable only because FINDING 60 landed first, and ruling 71 names its own
blind spot in advance: both `china-describes-rome` pairs sit outside the recall
window, so a crowder arriving at rank 7 would operate invisibly.

**73. Two slots re-pointed rather than added**, and Sub-Saharan Africa's carries
`requires_provenance: "local_language"`, enforced by `check_delivery` on the
unreachability shape. Ruling 58's owed gate, scoped to the one place it can
close.

## What was found — FINDINGS 62 to 67

**62.** One Greek text is counted as three regions' source-language records. The
Periplus supplies one to Arabia, one to South Asia and one to Sub-Saharan
Africa, from one edition and one page. **And the rule ruling 58 asked for would
have refused the wrong records** — it cannot tell Silko from the Periplus,
because both are `grc`.

**63.** F5 is the last sub-tranche allocated any vme record at all.

**64.** One standard written in three places against the risk of being
renegotiated, and the copy a reader of that case actually meets carried a
forecast. *An earlier draft of this finding said three gates and named a fourth
clause that was written correctly; the correction is in the document.*

**65.** All four missing records are one tier.

**66.** A mutation whose target has moved proves nothing, and the only detector
was a host run. **Continued:** the check written to catch that asked the weaker
of two questions and let the next one through within the hour.

**67.** `total_at_60` is the size of the plan and the file calls it a target.
Measured, not argued: no configuration places 38 records and reads 60.

---

## What F5 got wrong

Four defects, and **three of the four were caught by a host run rather than by
anything the session did.** Recorded here because a result document that lists
only what worked is the document FINDINGS 47 and 57 are about.

```
stale mutation targets     ruling 68 and FINDING 51 moved source that two
                           mutations still named. Caught: mutate_fidelity, MISS.
a Windows path key         str(PurePath) in an anti-vacuity assertion. Green on
                           the bridge, red on the host, and the remedy already
                           existed twice in this repository.
the weaker question        the target check asked EXISTS where it should have
                           asked EXACTLY ONCE. Caught by its own next use.
the +2 framing             ruling 69 asked how many MORE records when the
                           question was which DIFFERENT ones. Caught by the
                           project owner asking whether African languages would
                           actually be included.
```

**The fourth is the one worth keeping.** It was not a coding error and no
instrument would ever have caught it. A question framed on an assumption is
answered inside that assumption, and the only thing that breaks it is somebody
asking what the answer would actually contain.

---

## What F6 inherits

**Seven records to curate, all of them findable.** Three vme slots, one of them
on FINDING 45's named seam. Four vwp. F6 additionally holds the two re-pointed
source-language slots and the Africa requirement.

**The Africa slot is a hunt, not a plan.** The supply is established —
`F4_CANDIDATES` records that Polish Nubiology publishes in English, which made
the route a dead end for the tier F4 was filling and puts everything on it in
LIST A, the profile this tier wants. Ge'ez is closed on the Rome criterion,
Meroitic is closed as a class and rightly, and the two Nubian candidates F4
named are Greek, which the requirement refuses. **Whether an Old Nubian text
inside the window touches Rome or Byzantium well enough is what F6 settles.**
Three outcomes are declared in advance so that it cannot be settled by choosing.

**Owed, and none of it discharged here:** `mutate_part8` still does not mutate
`eval/test_answer_eval.py`, and F5 took that debt from three guards to six.
`scripts/test_harnesses.py` is mutated by nothing and F5 added ten guards to it.
`mutate_distractors` has no BASELINE block, no `MUTATIONS` list and no target
verification — three instruments blind to the one harness that mutates the
schema. Six mutation targets across three harnesses match more than one line.
FINDING 58's shared matcher. Ruling 65's renderings debt, now three tranches
without a reading of the C2 fused arm. And FINDING 67.

---

# The sentences that travel, out of F5

**All four records the block is short are one tier, and the corpus lands at 56
because the machine-English tier lands at 6.**

**One Greek text supplies a source-language record to three different regions,
and the rule written to stop an aggregate being met inside two regions cannot
see a text counted in three.**

**What makes a tradition bad for the machine-English tier makes it good for the
provenance tier — which moved a slot at noon and filled a floor at five.**

**The guard asked whether enough slots remained when the scarce thing was
declarations, so the new one counts both and says which binds.**

**A number that must equal the sum of the plan cannot be missed by the plan.**

**The check written to catch a mutation that proves nothing was, within the
hour, the check that let one through — by asking the weaker of two questions it
could have asked.**

**Clearing a floor did not need more records. It needed different ones, and the
question that hid that was asked by the session, not by the file.**
