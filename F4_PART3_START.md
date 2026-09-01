# F4 PART 3 START — the close, and two predictions nobody has read yet

F4 Part 2 closed at `4f95db2`, working tree clean. The corpus is **35 records**,
digest `9728581d164b0a4b...`, 82 chunks, 23 parallel pairs.

```
ingest.verify              green -- 35 documents
ingest.test_fidelity        58      eval.test_ranking_check    253
eval.test_answer_eval      410      scripts/test_recover_baseline.py  STILL RED
mutate_ranking 108 (verified at a5c0ae6)   mutate_fidelity 46   mutate_ui_places 6
mutate_part8 94   mutate_cost 51    -- NONE re-run since a5c0ae6
```

Read `F4_RULINGS.md` first. Part 2 added **rulings 60, 61 and 62** and **FINDINGS
51 to 56**, and most of them were declared before the records they govern. This
document is only what has to be **decided or known** before Part 3 closes F4.

---

## THE TWO THINGS PART 3 MUST NOT READ UNTIL THE RANKING CHECK HAS RUN

**Ruling 55**, registered before any East Asian candidate was examined:
`china-describes-rome-houhanshu` (rank 4) and `china-describes-rome-weilue`
(rank 5) both move DOWN when F4's Literary Chinese records about Rome enter the
index, and `weilue` is the likelier to leave the top 6. Falsified if both hold —
which narrows FINDING 43 from same-subject texts to near-duplicate objects.

**Ruling 61**, registered before the debt pairs were ranked: for
`kedukan-bukit-saka-605` and `talang-tuo-sriksetra-park`,
`best_other_doc_chunk_id` names the other Srivijayan record; for
`thorsberg-chape-niwajemariz`, it names `scandinavia-03-vimose`. This is a
WITHIN-RUN comparison, so ruling 54's exclusion does not bar it.

**Three Literary Chinese records about Rome entered the index in Part 2 and the
prediction was written before any of them existed.** Do not open
`eval/ranking_runs/` until the run is archived. These are the only two
pre-registered predictions this project has ever made and both are now cheap to
spoil.

---

## What Part 2 delivered, against what F4 was allocated

```
ALLOCATED 7   Africa 2 vwp + 2 vme          East Asia 2 vwp + 1 vme
DELIVERED 5   record 31 africa-05-adulis-throne      vwp  (Part 1)
              record 32 africa-04-silko-talmis       vwp  (Part 1)
              record 33 eastasia-04-jingjiao-stele   vwp  gloss
              record 34 eastasia-05-liangshu-qin-lun vwp  gloss (weak, ruling 62)
              record 35 eastasia-06-cefu-yuangui     vme  + the vme_quotation_case
SHORTFALL 2   Africa's two verbatim_machine_english slots -- ruling 53's THIRD
              outcome, pre-declared, and step 1 below is writing it down.
```

**East Asia met its source-language floor** — 5 records against 4 — and is the
second region to do so. Gloss is **3 of 8 declared**, and FINDING 51 says why
that is not the same as 3 of 8 delivered against a reachable target.

---

## The four steps, in the order they should be taken

### 1. Africa's vme shortfall, under ruling 53's third outcome

Not a binary. Ruling 53 wrote three outcomes before the hunt and ruling 58
established which one fired: **Ge'ez fails on the ROME criterion, not the
translation criterion.** Every Rome-touching Ge'ez text in the open Littmann
volume is Ezana (held) or Sembrouthes (disqualified because a Wikipedia editor
attributed his English). That is FINDING 38's supply problem, not FINDING 41's
search problem. Write it as the NEITHER outcome and say so in those words.

### 2. `scripts/test_recover_baseline.py`, red since Block E

On `corpus_version` and `serving_stack`. F3 named it, F4 Parts 1 and 2 listed it
without touching it. Four threads. Every record Part 2 added moved
`corpus_version` again.

### 3. The two deferred rulings

- **The FINDING 41 ruling**, deferred by ruling 53 to F4's close, now with
  FINDING 45's genre seam AND record 35 in hand — the first record in this
  corpus curated by aiming at genre rather than at obscurity.
- **`vimose-runes` at rank 7**, owed since the opening decision. F4 added no
  Scandinavian records, so the neighbourhood will never be quieter — except that
  ruling 54's debt pair `thorsberg-chape-niwajemariz` is now in the index beside
  it, which ruling 61 predicts something about.

### 4. The ranking run, then F4_RESULT

**A DECISION BEFORE THE RUN.** `eval/gold/query_renderings.json` has no entries
for the eight pairs added in Part 2, and *"a query with no renderings raises
rather than degrading silently"* is a guard. The BASELINE arm is unaffected and
is the arm both predictions are denominated in. The C2 FUSED arm will refuse to
run until renderings are rebuilt, which costs chat calls. **Decide whether F4's
close needs the fused arm at all before spending them.**

F4_RESULT must carry, per ruling 62, the gloss count **with its composition** —
3 of 8, of which one is a hedged identification rather than a disputed reading —
and never as three equivalent cases.

---

## THE WORKFLOW CHANGED AGAIN IN PART 2, and these are not in F4_PART2_START

**FINDING 53 — `archive.org/_djvu.txt` is not the page.** It is somebody else's
OCR of it. Measured twice on one record: a dropped circumflex in `Tâ Ts'in`, and
a garbled MARGINAL NOTE spliced into the middle of a sentence. archive.org is
still excellent for FINDING a passage and establishing a book contains one —
ruling 57's whole evidence base is built from it. **It is not a capture source.
Characters come off the page images, read by a person.**

**And a locating fetch must not reveal the characters it located.** The moment
it does, the curator's capture stops being an independent second reading and
becomes agreement with a model. This is not theoretical: a fetch reported that
no critical apparatus existed near the stele's Da Qin passage, the curator's
BLIND paste contained exactly that apparatus, and the record's statement of
uncertainty came out of it. A false negative about the presence of evidence is
worse than a dropped character, because nothing falsifies it unless somebody
looks.

**FINDING 52 — write BYTES.** `.gitattributes` stops git rewriting line endings
and nothing stops the editor. A text-mode read-modify-write converted seven
files from CRLF to LF in one session, five of which had no intended change.
The convention here is PER FILE: `eval/goldset.py` and
`eval/run_ranking_check.py` are CRLF; `eval/test_answer_eval.py`,
`scripts/mutate_ranking.py` and the gold JSON are LF. **Read `git diff --stat`
before every commit** — a three-line change with a four-thousand-line diff is
the signal, and it is free.

**FINDING 54 — the ledger clock does not know whether anybody is at the
keyboard.** `max_measured_span_minutes: 240` was written against a clock left
running overnight. A two-hour break sails under it and writes eight times the
real figure under the label the file calls its most trustworthy. Close a span
that crossed a break with `stop --minutes N --because "..."`.

**FINDING 50, three measurements now.** Record 32: five divergences in ten
typed lines. Record 33: the machine dropped a diacritic and so did the curator,
in the same direction, on four words. Record 34: six divergences in one
paragraph, including the merchant's own NAME wrong twice in two different ways.
**Every record is right because the two paths were checked against each other,
and none would have been right on either path alone.**

---

## Still owed, and it is now five instrument changes and one coverage gap

All for F5, and deliberately as ONE re-cut with two tranches of evidence rather
than five re-cuts with one each:

1. ruling 53's deferred **vme allocation ruling** — whether the tier is
   allocated at all, and whether `by_tier_new`'s ten becomes a discovered floor.
2. ruling 58's **per-region language rule** — three of Sub-Saharan Africa's four
   source-language records are Greek and no check can see it.
3. FINDING 51's **per-sub-tranche gloss delivery check** — `gloss_capable` is
   declared per tranche and checked only in aggregate, so it can be missed one
   tranche at a time with every check green.
4. FINDING 55's **translation-search boundary on the vwp tier** — ruling 57
   makes a vme record state where its English search stopped, and a vwp record
   states only what it cited.
5. ruling 62's **distinction between a contested READING and a translator's
   hedged IDENTIFICATION** — both are "a hedged reading and a statement that the
   reading is uncertain" to any checker, and they are different evidence.

And the coverage gap, which is a different kind: **`scripts/mutate_part8.py`
does not mutate `eval/test_answer_eval.py`**, so three data-driven guards there
— the refusal-falsification check, the quoted-from-original quota, and Part 2's
new gloss-hedge check — have no mutation proving they can fail.

Carried from F2 and F3, untouched: `mutate_ranking`/`places`/`recover` BASELINE
blocks present but unexercised; ruling 40's `article_added` still reads 0;
`ingest/test_sql.py` has never run with sqlglot AND the database.

---

## What NOT to re-derive

**Do not re-hunt East Asia or Sub-Saharan Africa.** `F4_CANDIDATES.md` holds
both hunts in full, including every route that failed and why.

**Do not treat `[Siam, Cambodja?]` as an ordinary gloss.** Ruling 62 took it
WITH A DISCOUNT and the discount travels in three places. F4_RESULT is the
third.

**Do not read the aggregate cost per record.** Ruling 46 forbids it and the
allocation biases it downward by construction.

---

## The sentences that travel, from Part 2

**A quota declared per tranche and checked only in aggregate is a quota that can
be missed one tranche at a time with every check green.**

**The guard asked whether enough slots remained when the scarce thing was
declarations, and both are counts of records, so the sentence read correctly for
two sub-tranches.**

**The repository forbade git from rewriting a single byte, and then seven files
were rewritten by the tool that was reading them.**

**A fetch that tells you what it found has spent the evidence you were going to
check it against.**

**The guard was written against the clock left running overnight, and the clock
left running over lunch writes the same kind of lie under the same trusted
label.**

**The tier that admits it could not find an English translation is the only one
that writes down where it looked, and the tier that found one writes down
nothing at all.**

**Writing the checker for a rule is an invitation to write a stricter rule by
accident, and what caught it was a record curated before this session by
somebody who explained themselves in a note.**

**The definition could not tell a disputed text from an uncertain translator,
and the quota could not tell a strong case from a weak one, so the ruling had to
carry both distinctions in prose.**
