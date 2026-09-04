# F5 PART 2 START — seven records, three predictions waiting on them, and the reason this is not F6

**Read this before `F5_RULINGS.md` or `F5_RESULT.md`.** Those two are the record
of a session that decided things. This is the operating document for the session
that curates.

---

## THIS IS NOT F6, AND THE DOCUMENTS WILL TELL YOU IT IS

`F5_RESULT.md` is titled **F5 CLOSED**. That is true of the SESSION and false of
the SUB-TRANCHE, and the file knows the difference even though the document does
not:

```
sub-tranche  closed  slots  gloss  quoted  vme_q          delivered
  F3         True       8      2       2      2            6 of 8
  F4         True       7      2       2      1            5 of 7
  F5         False      7      2       3      1            0 of 7   <-- HERE
  F6         False      7      1       0      0
  F7         False      7      1       0      0
```

**F5 has delivered nothing and is open.** A session that read the two closing
documents and opened F6 would strand seven allocated slots and all three
registered predictions, and the corpus would land at 49 rather than 56. Nothing
would go red: `check_delivery` reports a shortfall as progress, which is the
behaviour ruling 51 built and FINDING 51 measured the cost of.

**Set `F5.closed` to `true` only when its seven cells are filled or its shortfall
is written down.** That flag is what `check_delivery`'s reachability arithmetic
reads to decide which declarations are still available.

---

## The state

```
HEAD                4c97f8f          corpus 35 records, digest 9728581d164b0a4b…
                                     82 chunks, 23 parallel pairs, unmoved since F4

nine suites, host, at 6c7b7cd -- one commit, one interpreter
ingest.verify        green            ingest.test_fidelity          77
ingest.test_cost        64            eval.test_answer_eval        413
eval.test_ranking_check 258           answer.test_answer           150
ui/test_build_ui_data    19           scripts/test_recover_baseline 56
scripts/test_harnesses   43

mutation harnesses   mutate_ranking 111 at bf85a4f, mutate_fidelity 60 at fedb2c9
```

Everything between `6c7b7cd` and `4c97f8f` is documents. Documents do not feed
suites, so those numbers describe HEAD — **and that sentence is the one FINDING
47 is about, so check it rather than inherit it.** `git diff --stat 6c7b7cd..HEAD`
is the whole of the evidence.

---

## What F5 Part 2 is allocated

```
2 x Arabia              verbatim_with_provenance
1 x Persia              verbatim_with_provenance
1 x South Asia          verbatim_with_provenance
1 x East Asia           verbatim_machine_english
1 x Persia              verbatim_machine_english
1 x South Asia          verbatim_machine_english
                                                    7 records
gloss_capable 2    expect_quoted_from_original_cases 3    vme_quotation_cases 1
```

**East Asia's `verbatim_machine_english` slot is ruling 67's**, moved there from
Arabia this session, and it is the whole of the tier's remaining evidence: F6 and
F7 place no vme slot, so **F5 is the last sub-tranche that can add one.** Aim it
at FINDING 45's seam — the Tang Huiyao, the Taiping Huanyuji and the Lingwai
Daida are named, untranslated and still open; the Cefu Yuangui was spent in F4.

**Persia's and South Asia's vme slots are the ones ruling 72 predicts will fail**,
and the prediction is only worth anything if the search is real. Ruling 57's rule
is load-bearing here: every vme record carries the named sources consulted and
the boundary where the search stopped, and **a slot that goes unfilled with no
recorded search is not evidence for ruling 72 and may not be counted as such.**

---

## The three registered predictions, and none has been read

They were written before any candidate was examined and are denominated in
`eval/ranking_runs/20260904T081155+0000-retrievable_chunks_with_distractors.json`.
**They are checkable only once F5's records are in the index**, which is why they
are still open.

```
pair                             rank   best_other_doc_chunk_id
china-describes-rome-houhanshu      8   eastasia-01-weilue::translation::000
china-describes-rome-weilue         9   seasia-02-oc-eo-site::original::000
vimose-runes                        7   arabia-04-jabal-dabub::original::000
muziris-cargo-akananuru           319   arabia-01-periplus::translation::001
```

**Ruling 70.** At least one of F5's two Arabian records appears in
`vimose-runes`'s `beaten_by`. It sits at rank 7, so its interval names all six
chunks in front of it, and two of those six are already Arabian inscriptions.

**Ruling 71.** F5's East Asia record appears in `beaten_by` for at least one
`china-describes-rome` pair — **and the blind spot is named in advance**: both
pairs are outside the recall window, so a crowder landing at rank 7 would operate
invisibly. Report `beaten_by` AND `rank` for both, and if the ranks fall while
the record is absent from both intervals, that is the cap and not evidence
against FINDING 43.

**Ruling 72.** East Asia's vme slot fills and at least one of Persia's and South
Asia's does not, failing because English was FOUND rather than because material
is missing.

`beaten_by` landed in F5 and no archived run carries it. **Take the ranking run
after the records enter the index, not before**, and the archive it produces is
the first that can see a crowder.

---

## What has already been decided — do not re-open these

- **56, not 60**, recorded as missed (ruling 69, amended by 73). `total_at_60`
  and `by_tier_at_60` are not lowered.
- **The gloss target is 7**, reached twice from two directions, and reachable
  with **zero slack**: 3 declared + F5 2 + F6 1 + F7 1. If F5 declares fewer than
  2, `check_delivery` fails the tree that day rather than at F7's close.
- **Every region clears the source-language floor** under the plan. Two did not
  this morning; ruling 73 re-pointed two catalogue slots rather than adding
  records.
- **Sub-Saharan Africa's F6 slot requires `local_language`** and cannot be filled
  with a third Greek record. That is F6's, not this session's.
- **FINDING 41 narrows** rather than standing: the tier is fed by a nameable
  structural gap in English-language scholarship, and the evidence is delivery,
  not the experiment ruling 53 designed.

---

## The workflow rules that carry, and F5 Part 1 never had to obey them

**F5 curated nothing, so none of the capture discipline was exercised this
session.** All of it applies from the first record.

**The capture path.** Source text and published translations are **pasted by the
curator from the cited page**, every record. `WebFetch` silently drops lacuna
markers and substitutes U+0027 for U+2019 — measured twice (FINDING 48, 50).
`archive.org/_djvu.txt` is **not the page**: it is somebody else's OCR, it
splices marginal notes into sentences, and it agrees with itself about its own
errors (FINDING 53).

**A locating fetch must not reveal what it located.** The moment it does, the
curator's capture stops being an independent second reading and becomes agreement
with a model. A fetch reported that no critical apparatus existed near the
stele's Da Qin passage; the curator's BLIND paste contained exactly that
apparatus, and the record's statement of uncertainty came out of it.

**A model CAN be the diff.** The automated path was wrong once in 431 characters
and the human path five times in ten lines. Propose the diff; never apply it.

**Write BYTES**, under each file's own newline convention, and read
`git diff --stat` BEFORE every commit — a three-line change with a
four-thousand-line diff is the signal (FINDING 52, 61).

**Never run a mutation harness where it can be interrupted.** The restore lives
inside the harness's own process. Host only, in a window somebody is watching
(FINDING 59). And `git status` from the bridge takes a lock it cannot release —
use `git --no-optional-locks` there, or the host.

**Close a span that crossed a break** with `stop --minutes N --because "…"`
(FINDING 54).

**The bridge is a different PLATFORM, not a host missing sqlglot.** Different
path separator, different default encoding, `psycopg` absent as well as
`sqlglot`. A green bridge run is evidence about Linux. F5 lost a guard to that
and the remedy already existed twice in this repository.

---

## What NOT to re-derive

- **`F4_CANDIDATES.md` holds the East Asia and Sub-Saharan Africa hunts in full**,
  including every route that failed and why. Ge'ez is closed on the ROME
  criterion; Meroitic is closed as a class and rightly.
- **Do not read the aggregate cost per record.** Ruling 46 forbids it and the
  allocation biases it downward by construction.
- **Do not re-take the F4 ranking run.** A second archive at one tree makes
  *which run is F4's* a question nobody needs.
- **Do not treat `[Siam, Cambodja?]` as an ordinary gloss.** Ruling 62 took it
  with a discount, and the discount is now DATA — `gloss_capable_declared` carries
  `kind`, so it travels with the count.

---

## Still owed

- **`scripts/mutate_part8.py` does not mutate `eval/test_answer_eval.py`.** Six
  data-driven guards with no mutation proving they can fail; F5 took that from
  three to six.
- **`scripts/test_harnesses.py` is mutated by nothing**, and F5 added ten guards
  to it.
- **`mutate_distractors.py`** has no BASELINE block, no `MUTATIONS` list and no
  target verification — three instruments blind to the one harness that mutates
  the SCHEMA.
- **Six mutation targets across three harnesses match more than one line.**
  Counted, not gated; the condition for asserting it is written in FINDING 66.
- **FINDING 58's shared matcher** — nine copies of one three-line rule.
- **Ruling 65's renderings debt** — the eight Part 2 pairs. The C2 fused arm has
  now gone three tranches without a reading.
- **FINDING 67** — `total_at_60` is the size of the plan and the file calls it a
  target.
- **FINDING 68** — the SPEAKING subtotal is reported nowhere. The project's stated
  purpose has no number, and two regions sit below the floor on that reading.
  F6's cheapest worthwhile change.
- **The floor is calibrated at 24 records** and re-calibration is booked at the
  corpus in force at Block F's close — three sessions on three distinct dates,
  ~270 chat calls. `recalibration_corpus` is a pair with both halves null until
  that corpus exists.

---

# The sentences that travel, into F5 Part 2

**F5 is open with nothing delivered, and the document that closes the session is
titled as though it closed the sub-tranche.**

**F5 is the last sub-tranche allocated any machine-English record, so the tier's
whole remaining evidence is three slots and one of them is on a named seam.**

**Three predictions are registered and none can be read until the records exist,
which is the only reason they are worth anything.**

**A slot that goes unfilled without a recorded search is not evidence for the
prediction that said it would fail.**

**The corpus check asserts that a quotation resolves to the characters on disk,
and nothing at all asserts that the characters on disk are the ones on the page.**
