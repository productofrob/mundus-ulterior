# W3 — DECLARE, DON'T INFER

## FINDINGS 82 and 86, as ONE item. The session after Block G, before the UI.

*Written 2026-09-07, before Block G. **Nothing here was measured; it is a
design and a scope, assembled from `F7_RESULT.md`, `F7_RANKING.md` and
`BLOCK_G_START.md`.** Every figure quoted is transcribed from those, not
re-derived. The first thing this session does is confirm the state block still
reproduces — if it does not, stop and find out what moved.*

---

# 1. WHAT THIS IS, AND WHY IT IS ONE ITEM AND NOT TWO

```
FINDING 82   classify_translation hard-codes lang = "en" for every non-pointer
             translation chunk.
             Cost F6 its East Asia slot: the Turfan Manichaean vein, whose
             parsigdatabase translations are Persian.

FINDING 86   classify_original's non-Latin test is a closed allowlist of script
             names. Thai, Khmer, Burmese, Sinhala, Tibetan, Javanese, Georgian
             and Cyrillic are absent, non_latin_ratio scores a page of Thai at
             0.00, and the Latin-script branch that rescues transliterations is
             never reached on a find record.
             Cost F7 three records in one session.
```

**They are the same defect: a language is being INFERRED where it should be
DECLARED.** Filed as two rows in a debt table, one gets fixed and the other stays
open; filed as one, the fix is one ruling and one shape.

## The rule that produced the refusals is CORRECT and does not get relaxed

Block F refused those records because the instrument classified them wrongly.
That was right. Had they been curated anyway they would have entered as
`('object_description', 'en', True)` and every tier count, every per-region floor
and the whole speaking/spoken-about table would have been quietly wrong.

**This item fixes the classifier. It does not lower the standard.** If at any
point the work starts to look like "admit the record and accept the label", stop:
that is the failure this project has spent six blocks learning to refuse.

## Why it is worth doing at all

- **It is the only route to `verbatim_machine_english` that does not depend on
  another hunt finding nothing.** Two hunts already have — `seasia-vme-hunt-unresolved`
  at 9 minutes and `persia-vme-hunt-unresolved` at 20, both retired in the ledger
  so the cost of the missing tier is visible rather than absent.
- **Four already-found records are unblocked**, and their search cost is sunk:
  the BnF cameo of Shapur I seizing Valerian (86, *"reachable the day it is
  fixed"*), Phu Khao Thong and Khlong Thom (86, both Thai, the latter naming
  Roman gold coins and Greco-Roman intaglios in its own keyword line), and the
  Turfan pair `M2 I` and `M 5794 I` (82, plus a reachable English translation).
- **It removes a contradiction a reviewer will find.** The project description's
  stated interest is *"relevant local, non-English sources from the regions
  above."* The current honest sentence is that this interest is refused by a
  classifier bug.

## What it does NOT do, stated so nobody expects it

- **It closes no G3 box.** G3 is failed and stays failed.
- **It does not help the UI.**
- **Its success will show up as a WORSE headline number.** Six more records means
  a fall the size FINDING 91 describes. Block G's amendment 1 §4 asks for the
  prediction that makes this legible in advance; read it before running anything.

---

# 2. THE DESIGN

## 2.1 The declaration

Every text-bearing field on a record carries an explicit language code:
`original_text_excerpt` and `reference_translation`, each with its own.

**The loader refuses a record that omits one.** No default, no fallback, no
lenient flag. That is ruling 27's shape — *every case declares its expected
behaviour, and the loader REFUSES to inherit it from a default* — reused rather
than reinvented, and it is reused because the argument is identical: a value
inferred by code is a value nobody ruled on.

## 2.2 The classifiers are demoted from determination to cross-check

`non_latin_ratio` and the script test **stay**. They stop being the authority and
become a check that can disagree with the declaration and raise.

This is deliberate and it is ruling 27's other half: **two fields that must agree
are a guard; one field computed from the other is a guard deleted.** A record
declaring `tha` whose text is Latin script is now a load error rather than a
silent mislabel. Delete the ratio test and you have swapped one blind spot for
another.

## 2.3 The obvious objection, answered in advance

*"You are replacing an allowlist of scripts with an allowlist of language
codes — same defect."*

No, and the distinction matters enough to be a ruling clause. The script
allowlist was a **proxy for a general property** — "is this text non-Latin" — and
a proxy that omits Thai answers the general question wrongly. A list of language
codes the corpus contains is **a fact about the corpus**, it is already in use
(the state block's per-language chunk line runs `xsa arc grc lzh pal xpr non
gmq-pro oty san ocm omy gez`), and it grows deliberately, by a curator adding a
code for a record they are placing. The first is a rule stated as a list and gets
it wrong; the second is a list that is honestly a list.

FINDING 10's lesson applies to the first and not the second: assert the rule and
enumerate at check time.

## 2.4 The rejected alternative, recorded so it is not re-proposed

**A sidecar of language declarations, beside the manifest, leaving records
untouched and the digest unmoved.** Rejected: that is the shape of the paraphrase
flag, and FINDING 11 is what happened to it — *the flag marked SUSPICION and
nothing in the pipeline ever turned suspicion into a determination.* The fact
belongs on the record.

The cost of rejecting it is real and is accepted: see §4.

---

# 3. THE BACKFILL, AND THE TAUTOLOGY IN IT

54 records need declarations they do not have. **The obvious method is a
tautology and must not be used unmarked:** run the current classifier, write its
output as the declaration, then assert declaration == classifier. That check
passes by construction and proves nothing, and this repository has caught at
least four tautologies by mutation already.

Two honest routes. **The recommendation is to use both, split by cost:**

```
route A  declare from the record's own language_note and citation prose, and
         treat any classifier disagreement as a FINDING.
         USE FOR: the eight records carrying loader warnings, plus every
         record whose original or translation field is not English. These
         are where a disagreement is possible and therefore where reading
         costs something and buys something.

route B  backfill from the classifier, and state in the ruling that the guard
         has NO FORCE over those records and begins working at record 55.
         USE FOR: the remainder.
```

**Route B is defensible only if the ruling says it out loud.** A guard described
as protecting 54 records when it protects none of them is worse than no guard,
because the next reader believes it.

---

# 4. WHAT IT COSTS

- **The corpus digest moves.** Every record gains a field, so
  `26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28` — the
  denominator of all 396 Block E runs — is superseded. **This is why the item is
  scheduled after Block G**: once the closing summary has recorded that digest as
  the Phase 2 state, moving it is free.
- **A re-ingest.** Expect no re-embed: the chunk text is untouched and only
  metadata is added. **Verify this rather than assuming it** — if a declaration
  reaches chunk text or a chunk id, that assumption is wrong and 561 chunks of
  embeddings are in play.
- **`floor.json` is pinned to the old digest by ruling 49's corpus clause.**
  Decide what the pin means once the corpus it names no longer exists. Do not
  quietly re-point it.
- **The eight loader warnings are the working set** — the records with an empty
  `reference_translation` or an empty `original_text_excerpt`. A declaration on a
  field that holds nothing needs a ruled answer before the loader clause is
  written, or the clause refuses eight existing records on its first run.

---

# 5. SCOPE — INSTRUMENT ONLY. STOP AT THE PROOF.

**This session fixes the classifier and curates nothing.**

Curating six records is Block-F-shaped work: five sub-tranches, weeks, and a
ledger. It goes after the UI if it goes at all. The temptation here is severe,
because the moment the fix lands there will be three named sources sitting there
that the previous block had to refuse.

The stopping point, and it is a proof rather than a feeling:

```
DONE WHEN   the BnF cameo's French description, Phu Khao Thong's Thai and
            Khlong Thom's Thai each classify CORRECTLY when run through the
            fixed classifier, recorded as three worked examples --
            and none of the three is curated.
```

That is the whole deliverable: two debt items closed, three named sources
demonstrably unblocked, no corpus-growth commitment made, and the vein left open
for a later decision that has more information than this one.

---

# 6. VERIFICATION

Every new refusal clause gets its own mutation. **A predicate with two clauses
needs two mutations** — the rule this repository wrote for predicates and then
had to re-learn for signatures.

```
ingest.test_fidelity        115 today; rises
ingest.verify               green, 54 documents, and the state block reproduces
scripts\mutate_fidelity.py   70/70 today; rises
scripts\mutate_cost.py       58/58; should not move
eval.test_answer_eval       425; should not move
eval.test_ranking_check     258; should not move
```

**The new clauses must not join `UNMUTATED_AND_OWED`.** `mutate_fidelity` already
carries three refusal guards there and adding more is how an owed list becomes
the place refusals go to be forgotten.

**Mutation harnesses are HOST ONLY** (FINDING 59), in PowerShell, never through
the bridge — a call killed at 45 seconds leaves a live mutation in the tree, and
`eval/run_answer_sweep.py` is now in `mutate_part8`'s SOURCES.

**Check `git diff --stat` after any harness run.** A file whose every line changed
is the line-ending defect, not your edit. `answer/*.py`, `eval/goldset.py` and
`answer/align.py` are CRLF; everything else in `eval/`, `ui/` and `scripts/` is
LF, and 168 archived citation spans point into the corpus by exact offset.

---

# 7. THE PREDICTION TO WRITE BEFORE ANY CODE

Ruling 78's practice, and the cheapest thing in this session. Write these into the
session's opening document, at a commit, **before the fix exists**, each naming
its own refutation:

1. **Which of the 54 records the fixed classifier relabels.** The expectation is
   *none* — every existing record is either an ancient non-English text the
   allowlist already covers or an English translation. **Refuted by any relabel**,
   and a relabel is the more interesting outcome, because it means a tier count
   somewhere in Block F was wrong.
2. **What the three worked examples classify as.** Name the expected tuple for
   each before running it.
3. **Whether the digest is the only thing that moves.** Refuted by any change to
   a chunk id, a chunk count, or an embedding.

Prediction 1 is the one worth caring about. Block F's own conclusion was that its
refuted predictions were worth more than its confirmed ones.

---

# 8. WHAT THIS FIX FORCES A RULING ON, AND IT IS NOT OPTIONAL

**A modern Thai museum description of a Roman lamp is not an ancient
source-language text, and nothing in the corpus currently distinguishes the
two.**

Once the classifier accepts modern non-English institutional prose, these lines
become ambiguous the moment such a record is curated:

- `source-language records by region`, and its floor of 4;
- ruling 58's **speaking vs spoken about** table — is Thailand *speaking* because
  a Thai curator wrote in Thai in 2019, or is that a region being *spoken about*
  by its own modern institutions? Both readings are arguable and the table
  currently cannot express the question;
- the hero claim itself. **An English query retrieving modern Thai prose is a
  much easier problem than an English query retrieving Literary Chinese.** If both
  land in one bucket, cross-lingual recall improves for a reason that is not the
  hero capability — which is the W2b English-only-padding defect in new clothes,
  and ruling 56's own warning that a total climbing by construction is not
  evidence.

**Rule on this before curating any such record, not after.** The likely shape is
a distinct tier or a declared `source_era` on the record, so modern institutional
prose is counted, visible and never silently added to a count that means
something else. **It is not this session's ruling to make** — this session only
has to make sure the next one cannot avoid it.

## Also raised and deferred

**Rights.** Ancient texts are largely public domain; modern institutional prose is
not, and FINDING 87 is the warning — eleven CC0 badges over text actually released
under the GNU FDL. 38 of 54 records already carry an `unread` rights position.
Admitting this category without a rights read per record makes the worst column
in the state block worse. **Counted, not gated, and never derived** stays the
rule.

---

# 9. WHAT THIS SESSION MUST NOT DO

- **Not curate a record.** §5. Three worked examples, zero records.
- **Not add `"THAI"` to the tuple.** `F7_RESULT.md` says it is the wrong shape and
  it is right: the next language breaks it again, and French breaks it today
  regardless of any script name.
- **Not re-point `floor.json`'s digest pin quietly.** Ruling 49 is a ruling.
- **Not fix anything else in `§5` of `BLOCK_G_START.md`.** FINDING 89's shape, the
  diffable manifest, the GeoNames dumps and the owed investigations are all `after
  the UI`. This session closes two items and stops.
- **Not assign ruling or finding numbers from this document.** `RULINGS.md` is the
  authority and the next free number is read from it at the time. Rulings 20 and 21
  have no full text because somebody left them as lines in a list written
  elsewhere.

---

# 10. FIRST FIVE MINUTES

1. `python -m ingest.verify --state` and `python scripts/state_block.py` on the
   bridge. **Confirm they reproduce what `BLOCK_G_RESULT.md` recorded.** If not,
   stop.
2. Read `BLOCK_G_RESULT.md` — specifically the freeze decision and the debt
   table's `when` column, both of which this item was scheduled by.
3. Read `F7_RESULT.md`'s *"What Block G inherits"*, items 1 and 2, and F7's
   *"What F7 searched and did not take"*, items 1 and 2 — the three refused
   sources in their own words.
4. Read `ingest/fidelity.py` whole. It is the file.
5. **Write the §7 predictions and commit them before writing any code.**
