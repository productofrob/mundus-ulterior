# F3 RESULT — the first thread that moved the corpus

Closed 2026-08-31. **6 of 8 records delivered.** The two unfilled slots are a
SHORTFALL, which `check_delivery` reports as progress; they are not an
unreachable quota, which it would fail.

F3 was the first tranche to add records since the seed 24. The corpus went
**24 -> 30**, and the seed digest moved from `26e4a683...` to
`34b3e4cbdd77109e...` for the first time in this project's life.

---

## What landed

| # | id | region | tier | language |
|---|---|---|---|---|
| 25 | `seasia-04-dong-yen-chau` | Southeast Asia | verbatim_with_provenance | Old Cham `ocm` |
| 26 | `seasia-05-my-son-b6` | Southeast Asia | verbatim_with_provenance | Sanskrit `san` |
| 27 | `scandinavia-05-thorsberg-chape` | Scandinavia | verbatim_with_provenance | Proto-Norse `gmq-pro` |
| 28 | `persia-04-bronze-heracles` | Persia | verbatim_with_provenance | Parthian `xpr` |
| 29 | `seasia-06-kedukan-bukit` | Southeast Asia | **verbatim_machine_english** | Old Malay `omy` |
| 30 | `seasia-07-talang-tuo` | Southeast Asia | **verbatim_machine_english** | Old Malay `omy` |

`verbatim_machine_english` moved **0/10 -> 2/10**. The tier that turns on the
machine-translation path has records under it for the first time.

Southeast Asia reached the F1 per-region source-language floor of 4. Every
other region is still below it: Arabia 3, South Asia 3, East Asia 2, Persia 2,
Scandinavia 2, Sub-Saharan Africa 1.

**Not delivered:** Persia `verbatim_machine_english`, Scandinavia
`verbatim_machine_english`. See FINDING 41 — they were not missed through
effort, they were unsourceable by construction.

---

## What F3 found

Four findings, all in `F3_RULINGS.md` with the evidence.

**FINDING 40 — a quota counts cases, and two of the six are not the same
case.** The `expect_quoted_from_original` quota reached 6 of 6. On a record
carrying a `reference_translation` the assertion records WHICH chunk was
quoted; across 16 archived runs of `chinese-da-qin`, 45 of 45 resolved
quotations came from the English. On a `verbatim_machine_english` record there
is no second chunk, so the assertion asks only WHETHER anything resolved. Six
of six is four of the first question and two of the second. The bar was not
lowered; the reading was corrected.

**FINDING 41 — `verbatim_machine_english` is a residue, not a target.** Three
strong candidates were disqualified in one session because somebody had
already translated each of them well and posted it free: Kartir on avesta.org,
M 5794 I in Skjaervo's open PDF, the Istanbul epitaph of Khurdad in de Blois
1990 via English Wikipedia. A curator can only establish "I did not find an
English translation", which is a property of the SEARCH. The tier cannot be
hunted, and F3 wrote four of it into a plan as a quota. **This blocks F4's
allocation.**

**FINDING 42 — the verifier is stricter than the matcher it verifies.**
`build_ui_data --verify` reported a correctly grounded Tamil quotation as
ABSENT. Same offsets, same length, one character: a newline the model rendered
as a space. `cite.locate_in_text` collapses whitespace and the gold suite
asserts that it does. The checker has `case_folded` and `case_only` but no
whitespace category, so the span falls through to the category that means a
citation was invented.

**FINDING 43 — F3's six records are measured only by what they broke.**
`vimose-runes` fell from rank 3 to rank 7 and out of recall@6, and the record
that displaced it is `scandinavia-05-thorsberg-chape` — curated in this
tranche FOR the gloss arm, whose one proven success is `vimose-runes`. There
is not a single ranking pair for any of the six new records, and their four
gold cases have never been run.

---

## The measurements

**Suites, on the host, at the committed tree**

```
eval.test_answer_eval    383 passed / 0 failed   (377 before F3)
ingest.test_fidelity      53 passed / 0 failed   (30 before F3)
ingest.test_cost          60 passed / 0 failed   (46 before F3)
ingest.verify            green -- 30 documents, 69 chunks, 19 parallel pairs
```

Three loader warnings, and all three are the empty-`reference_translation`
notice that the vme tier exists to produce.

**Ranking check** — `--with-distractors`, index 460 chunks, voyage-3.5.

```
recall@6 by unit   0.867 (26/30)      MRR@10  0.713
ALL pairs          0.788 (26/33)      MRR@10  0.624
archived_answer    0.375 ( 3/8)   authored 0.889   retrieval_probe 1.000
```

Exactly three pairs moved against every stable baseline since 19 August:
`muziris-cargo-akananuru` 310 -> 313, `tc-jabal-dabub` 2 -> 3, `vimose-runes`
3 -> 7. **Nothing improved.** See FINDING 43 for why that is structural rather
than a bad tranche.

**Floor probe** — 3 cases x 3 repetitions, archived to `eval/probes/`.

```
content 100%   grounded 100%   refusal 33%   mean resolved quotations 3.2
unstable cells: content 0, grounded 0
p7-answer-v2r: MEETS THE FLOOR
```

The probe routed to `probes/` and said in its own voice that it cannot
calibrate. **The corpus clause did NOT fire and was not tested.** Ruling 49's
`calibration_scope.corpus` declares 24 records against a corpus of 30, but a
probe never reaches the eligibility check. That clause remains a no-op. **Its
first real test is the next 30-case sweep**, which is at 60 records.

**Cost ledger** — 6 records timed, 24 excused, 5 retired.

```
verbatim_machine_english   n=2   mean 3.3 min   83% remembered
verbatim_with_provenance   n=4   mean 7.3 min   59% remembered
NOT YET A COST CLAIM (ruling 45): the declared mix is unmet.
```

Read 3.3 with care. The tier the mix is furthest short of is the one whose
cost is least measured, and the ~29 minutes of failed vme hunting sit in
retired rows that are in no mean. `source_hunting` cannot be measured under
the current rules at all, because the clock takes a record id and the hunt is
what chooses one.

---

## MUST be settled before F4 starts

**1. The allocation ruling (FINDING 41). Blocking.** `check_allocation`
refuses an allocation whose tier totals differ from `by_tier_new`, and the mix
at 60 declares 10 `verbatim_machine_english`. F4 cannot write an allocation
until it is decided whether vme is allocated at all. The recommendation on
file: allocate by REGION and by source-language coverage, and let the tier
fall out of what each record turns out to carry. That is a ruling and it
changes `corpus_tiers.json` and `check_allocation` together.

**2. `whitespace_only` in `build_ui_data --verify` (FINDING 42).** Cheap, and
it should land before F4 adds spans. Do NOT make the verifier
whitespace-insensitive silently -- add the category so the disagreement is
counted and visible.

**3. Ranking pairs written in the same commit as the records (FINDING 43).**
The precedent already exists: `verify` check 9 is raised in the same commit as
the records it counts. A pair written after the run is a pair written knowing
the rank.

**4. `vimose-runes` at rank 7 needs a decision, not a note.** It is
`known_failing` so the floor is not breached, but it is the gloss arm's only
demonstrated success and F4 may add more Scandinavian records. Either its
recall is defended or the gloss arm's evidence quietly decays.

**5. The hardcoded rank in the ranking report.**
`eval/run_ranking_check.py:1695` prints "at rank 309" under every view and
every corpus. It said 309 while the table said 313, and 309 while the table
said 54. One number, no check.

**6. The ranking check's DEFAULT view is not the historical one.**
`--with-distractors` reads the 460-chunk index; the default reads 67. Every
run before F3 used the flag and F3's first run did not, producing a table that
looked like a dramatic improvement and was a different measurement. Either the
default changes or the report refuses to print cross-view prose.

**7. `answer/translate.py`'s language declarations are load-bearing and
uncovered.** A missing declaration makes `run_ranking_check` refuse, which is
a real guard but an integration-level one needing the whole stack. No mutation
harness reaches it, so nothing cheap catches a bad declaration before an
expensive run.

**8. The `verse` and `documentary` confidence profiles are at n=1 and are now
load-bearing**, because the first `verbatim_machine_english` records landed.
`PHASE2_PLAN` wants a budgeted session with `calibrated` set honestly.

---

## Carried forward

Five candidates are banked with their reasons in `F3_RULINGS.md`, so F4 and F5
do not hunt cold. The strongest is **the Istanbul epitaph of Khurdad son of
Ohrmazd-afrid** — a Middle Persian Christian gravestone from a Byzantine
cemetery in Capa, dated 8th-10th century, for a named private man from the
village of Xist who went to Rom `pad ummed xwastarih-kardan i bar-xwada i
masih` and was buried there. Every other Persia record is a king on a
monument. It is `verbatim_with_provenance` (de Blois 1990) and belongs in F5's
Persia slot.

Also carried, unchanged from F2: `mutate_ranking`/`places`/`recover` have the
BASELINE check present but not yet exercised; ruling 40's `article_added` read
0 again and remains unverified rather than confirmed; `ingest/test_sql.py` has
still never run with sqlglot AND the database; and the third distinct UTC date
at 60 records is still owed by three separate rules.

---

## The sentences that travel, from F3

**A quota counts cases and assumes the cases are the same case.**

**You cannot search for the absence of a translation. You can only fail to
find one, and then call the failure a tier.**

**The two vme records this corpus holds qualified because one Wikipedia editor
did not say whose English he was printing.**

**A verifier that reports its most serious finding on a newline teaches its
reader to disbelieve it.**

**Six records entered the corpus and the only thing any instrument here can
say about them is that two older pairs moved down.**
