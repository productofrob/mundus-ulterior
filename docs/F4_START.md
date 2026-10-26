# F4 START — read this before curating a single record

F3 closed at `3010abd`, working tree clean. The corpus is **30 records**,
digest `34b3e4cbdd77109e...`, 69 chunks, 19 parallel pairs. Suites at close:
`eval.test_answer_eval` 383, `ingest.test_fidelity` 53, `ingest.test_cost` 60,
`ingest.verify` green.

Read `F3_RESULT.md` first. It is the handoff. This document is only the part
that has to be DECIDED before F4 curates anything, in the shape F3_START used:
decisions first, because every one of them is cheap now and expensive after
the records exist.

---

## What the allocation currently says F4 is

From `data/corpus_tiers.json`, ruling 51:

```
F4   7 records
     Sub-Saharan Africa   2 verbatim_with_provenance + 2 verbatim_machine_english
     East Asia            2 verbatim_with_provenance + 1 verbatim_machine_english
     gloss_capable: 2     expect_quoted_from_original_cases: 2
```

Its stated reason: *"Africa is at one source-language record of four and
Ge'ez has no published translation for most of what is open, so it is the
second-hardest region and the second-largest verbatim_machine_english draw."*

**Three of seven are `verbatim_machine_english`, and FINDING 41 says that tier
cannot be targeted.** That collision is decision 1 and it blocks everything
else, because `check_allocation` refuses an allocation whose tier totals
differ from `by_tier_new`.

Carried in from F3: the gloss-capable quota is at **1 of 8 declared** with 22
slots left — F3 was allocated 2 and delivered 1
(`scandinavia-05-thorsberg-chape`).

---

## DECISION 1 — what to do about the vme allocation. Blocking.

FINDING 41's claim is that a curator can only establish *"I did not find an
English translation"*, which is a property of the search rather than of the
text, so the tier is an outcome and F3 wrote it into a plan as a quota. Three
strong candidates were disqualified in one session because each had already
been translated well and posted free.

**But F4 is the fairest available test of that claim, and the ruling is better
made after it than before.** F3 hunted Persian and Scandinavian material —
two of the most thoroughly Englished epigraphic traditions in existence.
Ge'ez is not. The allocation's own sentence anticipated this. If Sub-Saharan
Africa yields 2 vme records honestly, FINDING 41 narrows from *"vme cannot be
targeted"* to *"vme cannot be targeted outside under-documented traditions"*,
which is a much more useful rule and a much smaller change to the mix. If it
does not, the ruling writes itself and F5 re-cuts with two tranches of
evidence instead of one.

Three ways to go, and the choice is the F4 thread's to make:

1. **Run F4 on the allocation as written**, treat any missed vme slot as a
   SHORTFALL (which `check_delivery` already reports as progress), and make
   the ruling at F4's close with Ge'ez evidence in hand. Nothing in the code
   changes. **Recommended.**
2. **Re-cut now**: vme becomes a FLOOR ("at least N, discovered") rather than
   a target. Changes `by_tier_new` in `corpus_tiers.json` and
   `check_allocation` together, in one commit, with the guard that currently
   refuses a mismatch rewritten to refuse something else.
3. **Allocate by region and source-language coverage only**, dropping tier
   from the allocation entirely. The largest change, and it discards a guard
   that has caught real errors.

Whichever is chosen, write it as a ruling before the first record, not as a
note after the seventh.

---

## DECISION 2 — pre-register the East Asia prediction BEFORE curating

FINDING 43 found that `scandinavia-05-thorsberg-chape`, curated for the gloss
arm, pushed `vimose-runes` from rank 3 to rank 7 and out of recall@6 — a near
neighbour in language, script, period, object type and country.

**F4's other region is East Asia, and East Asia's two pairs sit at the edge:**

```
china-describes-rome-houhanshu   rank 4   r@6 yes
china-describes-rome-weilue      rank 5   r@6 yes
```

Two ranks and one rank from falling out. F4 plans 2 vwp + 1 vme East Asian
records, which will be Literary Chinese `lzh` source-language texts about the
same subject as both pairs.

So the prediction is available NOW, before any record exists: **if FINDING
43's mechanism is real, these two pairs move down when F4's East Asian records
enter the index, and `china-describes-rome-weilue` is the more likely of the
two to leave the top 6.** Record that in F4's rulings before curating. A
prediction written afterwards is an explanation, and this project already has
a sentence about the difference.

This also gives F4 something F3 could not have: a way for its records to
produce a POSITIVE reading. If pairs are written for the new records in the
same commit (decision 3), F4 measures both what it added and what it cost,
instead of only the second.

---

## DECISION 3 — adopt "pairs in the same commit as the records"

FINDING 43: there is not one ranking pair for any of F3's six records, and
their four gold cases have never been run. The only measured effect of F3 on
retrieval is that two older pairs moved down. That is structural — every
tranche adds competition to queries written before it and adds no query of its
own — so it repeats in F4 unless the rule changes.

The precedent already exists in this repository: `ingest/verify.py` check 9 is
raised in the same commit as the records it counts, never in advance and never
later. Apply the same discipline to ranking pairs. **A pair written after the
run is a pair written knowing the rank.**

---

## Step 0 — two small fixes, deliberately deferred out of F3

Both were left for F4 for the same reason: they touch code that mutation
harnesses cover, so the fix is minutes and re-establishing *"every guard is
exercised"* is a host run. Do them together, once, before curating.

1. **`whitespace_only` in `build_ui_data --verify`** (FINDING 42). A correctly
   grounded Tamil quotation was reported ABSENT because a newline had been
   rendered as a space. Add a CATEGORY beside `case_only` — do not make the
   verifier whitespace-insensitive, because an edit that changed only spacing
   must stay visible. Re-run `mutate_ui_places`.
2. **The hardcoded rank at `eval/run_ranking_check.py:1695`.** It prints "at
   rank 309" under every view and every corpus; it said 309 while its own
   table said 313, and 309 while the table said 54. Either derive it or delete
   it. Line 471 records that this confusion has bitten before.

And one to decide rather than fix: **`run_ranking_check`'s default view is not
the historical one.** `--with-distractors` reads 460 chunks, the default reads
67, and every run before F3 used the flag. F3's first run omitted it and
produced a table that looked like a large improvement and was a different
measurement. Either change the default or make the report refuse to print
cross-view prose.

---

## Still owed, not F4-blocking

- **`vimose-runes` at rank 7 needs a decision, not a note.** It is
  `known_failing` so no gate broke, but it is the gloss arm's only
  demonstrated success. F4 adds no Scandinavian records, so the pressure is
  off for one tranche — which makes this the cheapest moment to decide.
- **`verse` and `documentary` confidence profiles at n=1**, load-bearing since
  the first vme records landed. `PHASE2_PLAN` wants a budgeted session with
  `calibrated` set honestly.
- **`answer/translate.py` language declarations are uncovered by mutation.**
  F4 will add `gez` and more `lzh`; a missing declaration makes
  `run_ranking_check` refuse, which is a real guard but an expensive one.
- **The corpus clause has still never fired.** Ruling 49 declares 24 records
  against a corpus of 30, but a probe never reaches the eligibility check. Its
  first real test is the 30-case sweep at 60 records.
- Carried from F2: `mutate_ranking`/`places`/`recover` BASELINE checks present
  but unexercised; ruling 40's `article_added` still reads 0 and is unverified
  rather than confirmed; `ingest/test_sql.py` has never run with sqlglot AND
  the database; a third distinct UTC date at 60 is owed by three rules.

---

## Banked candidates — do not hunt cold

Full reasons in `F3_RULINGS.md` under "Candidates banked". For F4
specifically:

- **The Xi'an stele (781 CE)** — Middle Persian and Syriac in the Tang
  capital, in `parsigdatabase.com`'s private-inscriptions corpus. Region is
  assigned by FINDSPOT here, so it is an **East Asia** record, not a Persian
  one.

For F5, already found and not to be re-hunted: the Istanbul epitaph of
Khurdad son of Ohrmazd-afrid (Persia, vwp, de Blois 1990); M 5794 I (Persia,
vwp, Skjaervo); the Quilon copper plates and the Kanheri graffiti (South
Asia).

**A source rather than a candidate:** `parsigdatabase.com` carries four
corpora with Persian translations, free on attribution, and refuses automated
fetching — every record from it costs a human pass at the keyboard. Budget it
as such.

---

## What not to re-derive

`source_hunting` cannot be measured under the current rules, because the clock
takes a record id and the hunt is what chooses one. Do not treat that as a
discipline failure again. What CAN be measured is everything after the id is
settled — `text_capture`, `placement`, `authoring` — in SEPARATE cost_log
calls. F3's `verbatim_machine_english` column reads 83% remembered and part of
that was avoidable.

`retire`'s output always tells you to re-file the minutes onto "the record
that landed". When the retirement is a failed hunt there is no such record and
the instruction is a no-op.
