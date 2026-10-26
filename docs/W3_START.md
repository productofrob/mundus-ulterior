# W3 START — DECLARE, DON'T INFER. **The predictions, the four decisions, and
# FINDING 94, all written BEFORE a line of the fix exists.**

*Session opened 2026-09-07, on the bridge, at `e8e92f3`. This document is
committed BEFORE any change to `ingest/fidelity.py`, `ingest/loader.py` or any
seed record — `W3_DECLARE_DONT_INFER.md` §7 and §10 step 5, which are ruling
78's practice. **Every number quoted here was read from the command named beside
it in this session.** Ruling and finding numbers are read from `RULINGS.md` and
the finding series at the time of writing, not from `W3_DECLARE_DONT_INFER.md`,
which §9 forbids as a source of numbers.*

---

# 1. §10 STEP 1 — THE STATE BLOCKS REPRODUCE, AND THE FIRST READING WAS A LIE THE ENVIRONMENT TOLD

`python -m ingest.verify --state` reproduces `BLOCK_G_RESULT.md`'s block **note
for note**: 54 documents, 170 chunks, 33 parallel pairs, the same per-language
chunk line, the same tier line, the same eight loader warnings in the same order,
`All integrity checks passed.`

`python scripts/state_block.py` reproduces `BLOCK_G_RESULT.md`'s table **row for
row** — eleven instruments, all green, `answer.test_answer` at 150 and
`scripts/test_recover_baseline.py` at 56.

The tree is clean. `git log 526af18..HEAD` is **one commit**, the Block G result
itself, and `git diff --stat` over it is `BLOCK_G_RESULT.md`, `PHASE2.md`,
`PHASE2_PLAN.md`, `PROGRESS.md` — 834 insertions, no deletions, and not one path
the corpus, the classifier or the index is a function of.

**So §10 step 1's condition is met and this session may read on.** It was met
before anything else was read.

## FINDING 94 — `state_block.py`'s first reading on a fresh bridge is an ENVIRONMENT gap, and §10 step 1 would have stopped for it

The first run of `state_block.py` in this session printed:

```
answer.test_answer                   149   [green]
scripts/test_recover_baseline.py     RED (exit 1)
NOT ALL GREEN: ['scripts/test_recover_baseline.py']
```

Neither reading was about this repository. The bridge VM is rebuilt for every
session and its interpreter is not the host venv; it had neither `sqlglot` nor
`psycopg`. `test_recover_baseline.py` imports `recover_answer_baseline`, which
imports `psycopg` at module scope, so the suite dies in the import and reports
RED rather than reporting a skip. `pip install "psycopg[binary]" sqlglot` in the
bridge VM restored **56** and **150** exactly, on the same tree, with no file
touched.

**Half of this was already known and half was not.** `F3_RUNBOOK.md` documents
the `sqlglot` half in terms — *"`answer.test_answer` reads `149 passed, 0 failed,
1 SKIPPED` through the bridge"* — and says a host reading of 149 would be a
finding rather than a pass. Nothing documents the `psycopg` half, and it is the
worse one: **149 announces itself as a skip and RED does not.** A session
following §10 step 1 literally would have stopped at its first command, on a
document that tells it to stop and find out what moved, and gone looking in a
tree where nothing had.

**What this costs, stated rather than fixed:** `state_block.py` reports an import
failure and a genuine test failure in the same word. This session does not fix
it — that is not W3's item and §9 forbids fixing anything else — but the
requirement is now written down: **a bridge session runs
`pip install "psycopg[binary]" sqlglot` before `state_block.py`, or reads two of
its eleven rows as environment noise.**

---

# 2. THE FOUR DECISIONS, TAKEN BEFORE THE CODE

`W3_DECLARE_DONT_INFER.md` leaves four things open and asks for each to be ruled
before the clause that depends on it is written. All four were decided at the
open of this session. **They become rulings 80, 81 and 82** — the next free
number read from `RULINGS.md` and the ruling files it indexes, whose highest
declared ruling is 79 (`F7_CURATION_START.md`).

```
D1  SHAPE           flat sibling keys on the record:
                    `original_text_lang` beside `original_text_excerpt`,
                    `reference_translation_lang` beside `reference_translation`.
                    `language_code` KEEPS its current meaning and its current
                    type, because the region lines, `source_language_provenance`
                    and the state block all read it.

D2  EMPTY FIELDS    the key is REQUIRED on every record; `null` is a positive
                    declaration that the field holds no text. The loader raises
                    BOTH ways -- a `null` declaration over a field with text, and
                    a language declaration over a field with none.

D3  BACKFILL        route A over the 8 loader-warning records, the 12 records
                    carrying two or three language codes, and every record whose
                    original or translation field is not English; route B over
                    the remainder, WITH the no-force clause written out loud.

D4  floor.json      the pin KEEPS naming 26e4a683... -- that is the corpus the
                    floor was calibrated on -- and gains a dated `superseded_by`
                    line naming the new digest and stating that the floor is
                    UNCALIBRATED for the current corpus. The pin is not
                    re-pointed. Ruling 49 is undisturbed.
```

**D2 is the one that costs something and is worth it.** The cheaper reading — a
declaration is required only where there is text — makes an absent key mean two
different things at once: *nobody declared* and *there is nothing to declare*.
That ambiguity is the defect this whole item exists to remove, one level up.

**D3's 12 multi-code records are named here because they are where a relabel is
possible.** `language_code[0]` is a fact about the record and not about which
language sits in `original_text_excerpt`, and on these twelve the two can
differ:

```
arabia-02-palmyrene-tariff  (arc grc)   arabia-03-jsnab17       (xna arb)
arabia-05-ruwafa            (arc grc)   eastasia-03-hwangnam-glass (ko en)
persia-01-skz           (xpr pal grc)   scandinavia-01-hoby-treasure (en grc)
scandinavia-02-gudme-hoard   (en da)    scandinavia-04-illerup-adal  (en da)
southasia-07-bm-claudius-aureus (en la) seasia-01-oc-eo-medallion    (en la)
seasia-02-oc-eo-site      (en vi fr)    africa-01-ezana-stone  (gez xsa grc)
```

---

# 3. THE §8 QUESTION IS NOT RULED HERE, AND IT IS MADE MECHANICALLY UNAVOIDABLE

`W3_DECLARE_DONT_INFER.md` §8: **a modern Thai museum description of a Roman
lamp is not an ancient source-language text, and nothing in the corpus
distinguishes the two.** It says the ruling is not this session's to make and
that this session must make sure the next one cannot avoid it.

**A debt row is not "cannot avoid".** The mechanism is a loader refusal:

```
MODERN_INSTITUTIONAL_PROSE_PENDING_RULING = frozenset({"tha", "fra"})

A record declaring one of these codes on original_text_lang is REFUSED at load,
naming the owed ruling. The two codes are the ones the three blocked candidates
use and nothing more; the set is emptied by the session that makes the ruling.
```

**This is not the script allowlist in new clothes and the distinction is §2.3's.**
The script allowlist was a proxy for a general property and answered the general
question wrongly for every script it omitted. This set asserts a rule — *no
ruling exists for modern non-English institutional prose, and no record of that
kind may be curated until one does* — and enumerates the codes it currently
touches at check time. FINDING 10's lesson, on the right side of it.

**And it is exactly what §5 asks for.** The classifier is fixed and provably
fixed; the three named sources classify correctly; and the loader still refuses
to admit them, so the fix makes no corpus-growth commitment and the vein is left
open for a session with more information. The worked examples call the
classifier, not the loader, which is why both statements are true at once.

---

# 4. THE PREDICTIONS — written before the fix exists, each naming its own refutation

## P1 — WHICH OF THE 54 RECORDS THE FIXED CLASSIFIER RELABELS. **The expectation is NONE.**

After the backfill, every chunk in the corpus carries the same
`(text_fidelity, lang, eligible_for_retrieval)` it carries today, and every note
line in `ingest.verify --state` that is a function of them is unchanged: the
per-language chunk line, the tier line, the source-language-by-region line, the
provenance line, the quotation-cases line, and the eight loader warnings.

```
REFUTED BY   any relabel at all -- any chunk whose fidelity, lang or eligibility
             changes, or any state-block note line that moves by one count.
```

**A refutation is the more interesting outcome and the twelve records in §2 are
where it would come from**, because on them the declaration is being read from
the record's own prose and today's `lang` is `language_code[0]`. A relabel means
a tier count somewhere in Block F was wrong. This prediction is the one worth
caring about; Block F's own conclusion was that its refuted predictions were
worth more than its confirmed ones.

## P2 — WHAT THE THREE WORKED EXAMPLES CLASSIFY AS. **The tuples are named before the text is run.**

```
BnF camee.360, Shapur I seizing Valerian -- the BnF's French description
  today                ('object_description', 'en',  True)
  after the fix        ('object_description', 'fra', True)

Phu Khao Thong, archaeology.sac.or.th/archaeology/120 -- Thai
  today                ('object_description', 'en',  True)
  after the fix        ('object_description', 'tha', True)

Khlong Thom, suvarnabhumi.psu.ac.th/tudb/archaeologicalread/76 -- Thai
  today                ('object_description', 'en',  True)
  after the fix        ('object_description', 'tha', True)

REFUTED BY   any of the six tuples above being wrong, in either column.
```

**`object_description` is the correct first slot for all three and that is not a
concession.** They are find records and their text fields are catalogue
description; FINDING 86's defect was never in that slot. **The whole visible
effect of the fix on these three is the SECOND slot, `en` becoming the declared
language** — which is what FINDING 86 said in its own words, and which is the
reason `non_latin_ratio` scoring a page of Thai at 0.00 mattered.

**A FOURTH worked example, beyond §5's minimum, because FINDING 82 does not live
in `classify_original` at all:**

```
Turfan, M2 I / M 5794 I -- a parsigdatabase translation in Persian
  today                ('translation', 'en',  True)   -- hard-coded, FINDING 82
  after the fix        ('translation', 'pes', True)

REFUTED BY   either tuple being wrong.
```

Three worked examples close FINDING 86 and leave FINDING 82 asserted rather than
shown. §5's stopping point is a floor, not a ceiling, and the two findings are
filed as one item precisely so that one of them is not proved and the other
assumed.

## P3 — WHETHER THE DIGEST IS THE ONLY THING THAT MOVES. **No, and the second thing is predicted here so nobody reads it as a defect.**

```
MOVES, and is expected to
  the corpus digest 26e4a683...       every record gains two keys
  every record's content_hash         canonical_record_text hashes the PARSED
                                      record with sorted keys, so a new key
                                      moves it -- all 54 of them

DOES NOT MOVE
  chunk ids            `{doc_id}::{role}::{seq:03d}` reads none of the new keys
  chunk count          170 in `ingest.verify --state`
  chunk text           the declaration never reaches a text field
  char_start/char_end  offsets are into the FIELD's string, not the file's bytes
  embeddings           561 chunks in the index; expect NO re-embed

AND THE CONSEQUENCE THAT LOOKS LIKE A DEFECT AND IS NOT
  `ui/build_ui_data.py --verify` resolves an archived span by
  (doc_id, source_field, offset) and reports a SECOND axis: whether the record's
  content_hash still equals the one recorded with the span. That axis re-reads
  as "the record moved" for ALL 168 archived spans, at once, in one commit.
  The FIRST axis -- the one G3 box 8 failed on -- must stay `moved 1, absent 1`,
  both of them africa-03-periplus-adulis.

REFUTED BY   any change to a chunk id, a chunk count, a chunk text, an offset or
             an embedding; or by the first axis leaving `moved 1, absent 1`.
```

**§4 of `W3_DECLARE_DONT_INFER.md` says to verify the no-re-embed assumption
rather than assume it, and this is where that is done.** If a declaration reaches
a chunk id or a chunk text, 561 chunks of embeddings are in play and this
prediction is refuted before the ruling is written.

---

# 5. WHAT THIS SESSION WILL NOT DO

Restated from §5 and §9 so that a prohibition honoured silently does not read
like one forgotten.

- **Not curate a record.** Three worked examples, zero records. The corpus is 54
  records at this document and 54 records at the result.
- **Not add `"THAI"` to the script tuple.**
- **Not re-point `floor.json`'s digest pin.** D4.
- **Not fix anything else in `BLOCK_G_START.md` §5**, FINDING 94 included: it is
  recorded above and left where it is.
- **Not run a sweep, a ranking run, or PG5.**
- **Not let a new refusal clause join `UNMUTATED_AND_OWED`.** Every clause gets
  its own mutation, and a predicate with two clauses gets two.
