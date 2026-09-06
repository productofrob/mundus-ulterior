# F6 rulings — 2026-09-06

*Block F's sixth distinct date. `date -u +%F` on the machine of record gives
`2026-09-06`; F5 Part 3 and the F6 opening document both ran on `2026-09-05`.*

*THIS SESSION HAS A SHELL. It is the bridge and not the host: a Linux VM on the
user's machine with the repository mounted, `git --no-optional-locks`, no git
identity of its own, and no mutation harness (FINDING 59). Every number below
was produced by running the command named beside it, in that shell, at the tree
named beside it. Where a number was read from a file rather than run, it says
so.*

---

# FINDING 76 — the document that discovered FINDING 75 committed FINDING 75, in the table that reports the instruments

## The observation

`F6_START.md` opens by refusing to hand-copy its predecessor's numbers, states
the rule — **"If you need a figure, run the command"** — and prints eleven
instrument counts. **One of them is wrong.**

Run on the bridge at `a20214e`, the tree `F6_START.md` describes:

```
python -m eval.test_answer_eval        425 passed, 0 failed
```

The document says **422**. `F5_PART3_RESULT.md:560` says where the 422 came
from, and it is the whole finding:

```
eval.test_answer_eval            422    (416 at open; +6 for three gold cases)
```

## The 416 is right and it is the only measured half

Measured, not inherited. `git archive 0f5bfe0^ | tar -x` into a scratch tree
outside the mount, then the suite:

```
0f5bfe0^   416 passed, 0 failed
a20214e    425 passed, 0 failed
```

**416 is correct. The delta is +9, not +6.** Commit `0f5bfe0` changes
`eval/gold/answer_cases.json` from 45 to 48 cases and does not touch
`eval/test_answer_eval.py` at all — `git diff` over that path across the commit
is empty. The suite is data-driven, so three cases carried **three** assertions
each, and the "+6" is a **per-case assertion rate that was assumed and never
counted**.

## Why this is not the same mistake as FINDING 75, and is worse

FINDING 75 was three counts **copied** from the document before. This one was
**computed** — 416 measured, plus an arithmetic step — and arithmetic is the
form a number takes when someone knows not to copy. **The instrument was
available and printed 425 into that same session; what it was asked for was the
opening figure, and the closing figure was worked out instead.**

`F6_START.md` then quotes the 422 under a heading saying the block is verbatim
`ingest.verify` output. **It is not — `eval.test_answer_eval` is not
`ingest.verify`, and the eleven-instrument table below the state block was never
covered by the rule the document had just written.** The rule was scoped to one
command, and eleven were printed.

## What follows

- **The count is 425.** `F6_START.md`'s table and `F5_PART3_RESULT.md:560` are
  corrected in place, each with a dated line saying what it read and why it was
  wrong, in FINDING 75's own form.
- **Debt item 8 grows a second half.** `ingest.verify --state` prints one
  command's output. The instrument table needs the same treatment or it will
  drift again: a script that RUNS the eleven and prints the block is the only
  version of this that cannot be restated. Deferred to the instrument work
  below, and named here so that the deferral is a decision.
- **No number in this repository derived by arithmetic from a measured number
  may be reported as an instrument count.** Either the instrument was run or the
  figure is an estimate and says so.

---

# RULING 76 — Persia's `published_translation_only` slot re-points to `verbatim_with_provenance`

**Accepted by the project owner, 2026-09-06, against the recommendation
`F6_START.md` made and on the evidence browser pass 2 was run to get.**

## What was decided

F6's allocation entry `{Persia, published_translation_only, 1}` becomes
`{Persia, verbatim_with_provenance, 1}`. Nothing else about Persia moves.

## Why now and not in F7

FINDING 71. Persia stands at **3** source-language records against a floor of
**4**. Both of its F6 slots were tiers that do not count toward the floor and
**F7 places no Persia slot at all**, so Persia ended Block F at 3 by
construction — while `check_allocation` reported `All integrity checks passed`,
because it reads the PLAN and the plan assumes its slots fill.

**F6 is the last sub-tranche that can change this.** That is not a preference,
it is the same argument ruling 73 used to put its two re-pointed slots here.

## Why the objection F5's hunt raised no longer holds

F5 refused this vein on a supply argument: `parsigdatabase.com` and
`noorlib.ir` "have refused every automated request since F3". **Browser pass 2,
run this morning, is `F6_BROWSER_PASS2.md`, and both sites open completely.**
Parsīg Database carries 120 texts, 93,518 words, transcription and translation
in adjacent tabs, stable numeric per-record URLs, five texts with an English
translation on the record, and — for `šahrīhā ī ērān` — an **edited text from
Jamasp-Asana 1897–1913, which is public domain**, with a printed bibliography
that lets the translation search state its own boundary.

**The supply was never thin. It was unexamined**, and four documents recorded
the refusal of a fetcher as a property of the site.

## What this costs if it is wrong

One `published_translation_only` record, on a tier that stands at **1 of 5**.
F7 places one `published_translation_only` slot for East Asia and one for South
Asia and can absorb a third. **The cost of not deciding is a floor that can
never be reached**, which is a different kind of number.

---

# RULING 77 — Persia's `catalogue_record` slot is exchanged with F7 and re-points to an Arabia `verbatim_with_provenance`, for CIH 541

**Accepted by the project owner, 2026-09-06.**

## What was decided

Two edits, and they are one exchange:

```
F6   {Persia, catalogue_record, 1}      ->  {Arabia, verbatim_with_provenance, 1}
F7   {Arabia, catalogue_record, 1}      ->  {Persia, catalogue_record, 1}
```

**The exchange is what keeps `records_by_region_target_at_60` still.** Persia
gives up a record in F6 and takes one back in F7; Arabia takes one in F6 and
gives one back in F7. Persia ends at 9 and Arabia at 8, exactly as ruling 44
declared. This is the shape rulings 67 and 73 both used, for the reason they
both gave: a re-point that moves a region's total is a re-target wearing a
re-point's clothes.

The tier totals DO move, and they are meant to:

```
by_tier_new         verbatim_with_provenance  16 -> 18
                    published_translation_only 4 ->  3   (ruling 76)
                    catalogue_record           6 ->  5   (this ruling)
by_tier_at_60       verbatim_with_provenance  27 -> 29
                    published_translation_only 5 ->  4
                    catalogue_record          17 -> 16
new_records         36, unchanged
```

## Why `catalogue_record` is the slot to spend

It is the tier with the most slack anywhere in the plan — **11 of 17 already
standing at 40 records**, with five more slots after this ruling and every one
of them in F7, the sub-tranche whose whole design is that it is cheap. It is
also the tier `PHASE2_PLAN` named as the failure mode: *"so the tranche is not
accidentally all catalogue records."* **Spending a catalogue slot on a
source-language record is that sentence being obeyed, not bent.**

## What is bought

CIH 541 Sadd Ma'rib 5, at `dasi.cnr.it/project/1/epigraphs/2382`, DOI
`10.82194/dasi-epi-2382`, read by a person in browser pass 3 and recorded in
`F5_PART3_BROWSER_PASSES.md`: a **CC BY 4.0 Late Sabaic source text** and a **CC
BY 4.0 English translation on the same record**, a DOI, a stable per-record URL,
a linked site record so placements resolve, and **three named-editor variant
readings printed in an apparatus on the page**.

**It carries F6's one `gloss_capable` declaration**, on the standard
`arabia-05-ruwafa` was declared on and subject to the mechanical requirement in
full: the hedge and the statement that the reading is uncertain both sit inside
`original_text_excerpt` or `reference_translation`, and **not** in `notes`,
which the loader does not chunk. `eastasia-05-liangshu-qin-lun` is the pattern.

## What is knowingly given up, declared rather than discovered

- **It buys no floor.** Arabia stands at 5 against a floor of 4 and this makes
  it 6. The record is taken for its provenance, not for a count.
- **F5's session is no longer an independent check on the capture.** Browser
  pass 3 read CIH 541's Sabaic text and the opening of its English translation
  into a session's transcript. A capture made now is still a curator's blind
  paste, but it is checked against a document rather than against a second
  independent reading. **Declared in the record, the same way browser pass 1's
  reading and `southasia-05` are.** FINDING 55 is why this is stated and not
  argued away: an alternative this project supplied itself is worth nothing, and
  the same is true of a check.
- **It puts a fourth Arabia record into an index where the third already cost
  something.** That is ruling 78.

---

# RULING 78 — F6's predictions are written before the first record is curated

**Accepted by the project owner, 2026-09-06.** F6 places seven records on an
index where FINDING 73 measured **nine gold pairs falling, none improving, and
the headline not moving**. Read afterwards, any number that moves has an
explanation available for it. So the predictions are written first, here, at
`a20214e`, before a record exists.

## P1 — `tc-jabal-dabub` leaves recall@6, and the aggregate finally moves

FINDING 73 put it at **rank 6 with zero slack**, having fallen 3 → 6, with
**three chunks of `arabia-06-syllaeus` inside its window** — Arabia crowding
Arabia. Ruling 77 adds a **fourth** Arabia source-language record, CIH 541,
whose Sabaic text and English translation are both retrieval-eligible and both
about a South Arabian monumental inscription naming Rome.

**Predicted: `tc-jabal-dabub` falls out of the top 6.** If it does, `ALL
recall@6` moves off `0.727` for the first time since F4, and pair-level moves
off 32/44.

**What would refute it:** `tc-jabal-dabub` holds at 6, or improves. Either means
same-region crowding is weaker than FINDING 73 read it, and that the two chunks
of `arabia-06-syllaeus` did something a third Arabia record does not.

## P2 — `probe-tamil-akananuru-en` falls too, and NOT for a same-region reason

Also at **rank 6 with zero slack**, 5 → 6, with `eastasia-07-tang-huiyao`
inside it. F6 places **one East Asia** `verbatim_with_provenance` record and
**no South Asia record at all**. If it falls, it falls to a cross-regional
crowder, which is ruling 70's mechanism and not ruling 73's.

**Predicted: it falls.** **What would refute it:** it holds while
`tc-jabal-dabub` falls — which would say the two rank-6 cases are at rank 6 for
different reasons and that only the same-region one is fragile.

## P3 — Scandinavia is F6's largest draw and `vimose-runes` keeps falling

`vimose-runes` has already gone **7 → 16**. F6 places **two** Scandinavian
source-language records. **Predicted: it falls further and does not recover.**
**What would refute it:** it improves, or holds within one rank — which would
mean the 7 → 16 fall was caused by something other than Scandinavian material
entering the index, and that FINDING 73 named the wrong cause.

## The rule this ruling does not make

**None of these is a gate.** `F6_START.md` is explicit and it is right: a
threshold on these margins is a threshold nobody has evidence for. A prediction
that fails is read, recorded, and does not stop the tranche. Ruling 71 was not
confirmed and F5 closed anyway.

---

# What F6's allocation is, after rulings 76 and 77

```
region              tier                        n   note
Sub-Saharan Africa  verbatim_with_provenance    1   requires_provenance:
                                                    LOCAL_LANGUAGE
Sub-Saharan Africa  published_translation_only  1
East Asia           verbatim_with_provenance    1
Scandinavia         verbatim_with_provenance    2   re-pointed by ruling 73
Persia              verbatim_with_provenance    1   re-pointed by RULING 76
Arabia              verbatim_with_provenance    1   re-pointed by RULING 77

gloss_capable 1     expect_quoted_from_original_cases 0     vme_quotation_cases 0
```

**Six of seven are source-language records** and F6 places **no catalogue
record at all**, which makes it the first sub-tranche in Block F whose slots
are entirely the tiers the product's central claim depends on. Two of the six
move a per-region floor from missed to met — Scandinavia's pair — and a third,
Persia's, moves one from **unreachable** to met, which no other slot in the
remaining allocation could do.

**No `verbatim_machine_english` slot is placed in F6 or F7.** The tier ends at
**4 of 10** and F5's two recorded failures are what fix it there. Nothing in
these rulings moves it and nothing should try.
---

# FINDING 80 — the handoff document mis-describes the record it points the Africa hunt at, in the sentence that justifies the slot

## The observation

`F6_CURATION_START.md` and `F6_PROGRESS.md` both close their Africa section with
the same sentence:

> `africa-01-ezana-stone` is already the GREEK of a stone that also carries Ge'ez.

**It is not.** Read on the bridge at `b8a4cd3`, before anything was curated:

```
data/corpus_tiers.json      africa-01-ezana-stone -> published_translation_only
original_text_excerpt       "[Ge'ez, Sabaean, and Greek texts of the Ezana Stone are
                             not transcribed in this pass; pull from Encyclopaedia
                             Aethiopica or the DAE ... corpus during ingestion.]"
citation                    https://en.protothema.gr/the-ezana-stone-of-aksum-...
classify_original(...)      ('pointer', 'en', False)
```

**The record holds no Greek text and no Ge'ez text and no Sabaean text.** Its
`original_text_excerpt` is a bracketed instruction to a later session; its
`reference_translation` is an English rendering of the Greek titulature quoted
from a **news website**; and the classifier returns `pointer`, not retrieval
eligible, which is why it is `published_translation_only` and why it is NOT one
of Africa's three source-language records. Those three are
`africa-03-periplus-adulis`, `africa-04-silko-talmis` and
`africa-05-adulis-throne`, all `verbatim_original` `grc` — and the two the
provenance line calls "empire-language from the region" are 04 and 05.

## Why this is not pedantry

**It changes what the slot is.** The sentence reads as though the Africa Ge'ez
capture would be adding a second register to a text the corpus already holds in
the first. It would not. The corpus holds **no register of the Ezana Stone's own
words in any language**, and the only thing it holds about that stone is a
translated titulature from a newspaper. A curator who believed the sentence
would go looking for the Ge'ez of one specific stone, find it hard, and not know
that any Aksumite royal text in Ge'ez would do.

**And it leaves a gold case looking closer than it is.** `ezana-stone-geez` —
"What does the Ge'ez text of the Ezana Stone say?" — is a known-failing answer
case written against exactly this gap. **The record placed today does not close
it**, because RIE 189 is a different inscription from the trilingual stone, and
the record says so in its own notes rather than leaving the next session to
discover it.

**It is FINDING 75's species again**: a sentence written once, inherited by a
second document, and never checked against the file it describes. The check cost
one `python3 -c` and was not run in either document.

## What follows

- The sentence is corrected in place in `F6_CURATION_START.md` and
  `F6_PROGRESS.md`, each with a dated line saying what it said and why it was
  wrong, in FINDING 75's form.
- `africa-01-ezana-stone` is **not re-curated**. Nobody re-curates a record. What
  it is, is now written down where the next session reads.

---

# RULING 78, P4 — the Africa prediction, written before the record was curated

**Written 2026-09-06 at `b8a4cd3`, after the candidate was located and before any
file was written.** Ruling 78's own sequencing: the candidate for P1 was named in
the ruling before CIH 541 was curated, and P3 was confirmed because it was
written first.

## The candidate this prediction is about

**RIE 189, lines 39-52** — ‘Ēzānā's vocalized Ge‘ez throne inscription from
Aksum, in Latin-script transliteration, with a published English translation by a
named scholar on the same page: George Hatke, *Aksum and Nubia*, ISAW/NYU 2013,
open access, CC BY-NC, quoting Bernand, Drewes & Schneider, *RIÉ* I (1991)
264-5. `classify_original` returns `('transliteration', 'gez', True)`;
`english_marker_ratio` is **0.0792**, measured, against a threshold of 0.18.

## Africa's six ranking pairs, which are what the prediction is denominated in

```
pair                       expect_doc                  expect_lang   last rank
aksum-trade-adulis         africa-03-periplus-adulis   grc           33
adulis-exports             africa-03-periplus-adulis   grc           unchanged
probe-adulis-ivory         africa-03-periplus-adulis   grc           unchanged
adulis-throne-leuke-kome   africa-05-adulis-throne     grc           unchanged
silko-basiliskos           africa-04-silko-talmis      grc           unchanged
au-ezana-titles            africa-01-ezana-stone       en            unchanged
```

## The two readings disagree, and they disagree in a shape that can be read off one run

```
FINDING 73 says   curating a region damages that region's own gold cases
                  -> Africa's six pairs degrade as a group, the three Adulis
                     ones included

FINDING 79 says   the crowder is the record that RESEMBLES the target
                  -> five of the six are GREEK chunks of Greek texts and the new
                     record contains no Greek at all, so they should not move.
                     The sixth, au-ezana-titles, resembles it in every dimension
                     that matters: same king, same genre, first person, royal
                     titulature and kingship -- AND its expected chunk is
                     ENGLISH, which is what the new record's reference_translation
                     also is.
```

**PREDICTED (P4): `au-ezana-titles` falls, and the five Greek-target pairs do
not move.** That is FINDING 79's reading and it is the one this project's own
last experiment supports.

**What would refute it, in three distinguishable ways:**

1. **The Adulis or Silko pairs fall while `au-ezana-titles` holds** — FINDING 73
   is right, the region is the crowder, and resemblance was a coincidence of the
   Elder Futhark pair.
2. **`au-ezana-titles` holds and nothing else moves either** — neither mechanism
   fires, and the honest reading is that a record whose two chunks are a
   transliteration and an English translation is too unlike anything in the index
   to crowd it. That is a *weaker* claim than FINDING 79 and would need saying.
3. **Everything falls.** Then what is being measured is the index growing, not
   either mechanism, and both findings are under-determined by 44 pairs.

**This is not a gate.** Ruling 78's closing paragraph governs: a prediction that
fails is read, recorded, and does not stop the tranche.

## The one asymmetry that has to be declared now rather than after the run

`au-ezana-titles` expects `africa-01-ezana-stone`, the record FINDING 80 has just
shown to be a placeholder with a newspaper citation. **If it falls, the honest
reading is not automatically "the new record crowded it"** — it may be that a
weak chunk was holding a rank it could not defend against any new Africa material
whatsoever. That alternative is written down here, before the run, because after
the run it would be available as an excuse for either outcome.
