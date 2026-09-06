# The F6 ranking run — read against ruling 78's three pre-registered predictions

*Run on the host, 2026-09-06, archived at
`eval/ranking_runs/20260906T084832+0000-retrievable_chunks.json`.*

---

## FIRST, THE ERROR IN THE INSTRUCTION, BECAUSE IT GOVERNS EVERYTHING BELOW

**This run was made with the wrong view, and it was the instruction that was
wrong, not the tool.** `eval.run_ranking_check` takes `--with-distractors` as an
opt-in flag and defaults to `retrievable_chunks`. F5's closing run — the one
FINDING 73's fall table and ruling 78's three predictions are written against —
used the flag:

```
20260905T183224  view=retrievable_chunks_with_distractors  index=507 chunks
20260906T084832  view=retrievable_chunks                   index=131 chunks
```

**393 distractor chunks left the index between the two runs, and three records
entered it.** A rank comparison across that pair is not like-for-like, and
ruling 78 was written expecting a comparison that is. **The run that answers
ruling 78 on its own terms is `python -m eval.run_ranking_check
--with-distractors` and it is still owed.**

**Two of the three readings below survive it anyway, and one of them is
STRENGTHENED by the mistake.** Where that is so, it is said and the reason is
given.

---

# FINDING 77 — THE HEADLINE IS IDENTICAL TO SIXTEEN DECIMAL PLACES ACROSS TWO DIFFERENT EXPERIMENTS

Not similar. Identical.

```
                        05 Sep, 507 chunks      06 Sep, 131 chunks
                        with 393 distractors    no distractors, +3 records
recall@6  (pairs)       0.7272727272727273      0.7272727272727273
                        32 / 44                 32 / 44
recall@6  (units)       0.8048780487804879      0.8048780487804879
                        33 / 41                 33 / 41
mean_coverage           0.7886178861788619      0.7886178861788619
MRR@10    (pairs)       0.5577651515151515      0.5706439393939394
MRR@10    (units)       0.6205284552845528      0.6343495934959349
```

**Seventy-five per cent of the index was removed and the number a reader meets
did not move at all.** Only MRR moved, and it moved by about a fiftieth.

## The per-pair table, which is where everything actually happened

```
pair                              05Sep/507   06Sep/131   delta
muziris-cargo-akananuru                 333          83    -250   BETTER
muziris-cargo-papyrus                   113          47     -66   BETTER
bronze-heracles-verethragna-from-mes     86          78      -8   BETTER
au-khao-sam-kaeo                         17          10      -7   BETTER
aksum-trade-adulis                       39          33      -6   BETTER
dong-yen-chau-naga-of-the-king            5           2      -3   BETTER
kedukan-bukit-saka-605                    3           2      -1   BETTER
thorsberg-chape-niwajemariz              24          23      -1   BETTER
tc-frankincense-harvest                  12          13      +1   worse
vimose-runes                             16          18      +2   worse
   ...34 pairs unchanged
```

**Eight better, two worse, thirty-four unchanged — AND NOT ONE PAIR CROSSED THE
recall@6 BOUNDARY IN EITHER DIRECTION.** Every improvement above rank 6 was a
pair already outside the window; the two improvements inside it (5→2 and 3→2)
were already inside it. That is why 32/44 is 32/44.

**The improvements are the distractors leaving, and they are concentrated exactly
where the distractors were dense** — at depth. The corpus's one genuinely broken
cross-lingual link, `muziris-cargo-akananuru`, moves 333 → 83 and is still
nowhere near the window.

## Why this matters more than the individual ranks

`PHASE2.md`'s W2b built the distractor experiment to "pad the index to 150 and
450 chunks with flagged, known-irrelevant material and plot how rank degrades",
because degradation "predicts the 200-document behaviour without curating 200
documents." **This run is that experiment run backwards, at full scale, and the
answer is that padding the index to 4× degrades rank ONLY BELOW THE WINDOW THE
GATE READS.** The metric G2's recall criterion is denominated in is insensitive
to the manipulation W2b exists to measure.

**That is not a reason to distrust either number. It is a reason to stop reading
recall@6 as though it were a measure of index quality**, and to note that a
project which had curated 393 real records instead of 393 distractors would have
seen the same 0.727 and concluded nothing had happened.

---

# RULING 78's PREDICTIONS, READ

## P3 — CONFIRMED, AND THE MECHANISM IS NAMED RATHER THAN INFERRED

> *Predicted: `vimose-runes` falls further and does not recover.*

**It fell, 16 → 18.** And the run prints what beat it:

```
vimose-runes   rank 16 -> 18   beaten_by:
  scandinavia-06-tjurko-bracteate::original::000      <-- curated today
  arabia-05-ruwafa::translation::000
  arabia-05-ruwafa::translation::002
  arabia-05-ruwafa::original::002
  scandinavia-06-tjurko-bracteate::translation::000   <-- curated today
  arabia-04-jabal-dabub::original::000
```

**Two of the six chunks now beating Scandinavia's gold case are both halves of
the Scandinavian record this session curated.** Ruling 78 wrote the prediction
before the record existed; the record exists; it is in the list.

**THE WRONG VIEW MADE THIS HARDER TO CONFIRM, NOT EASIER.** Every other pair at
comparable depth IMPROVED when 393 distractors left the index — 86→78, 39→33,
24→23. `vimose-runes` got worse in an index that got four times smaller. It is
one of only two pairs in the whole set that did.

## P1 — NOT TESTED, AND THE RUN SAYS WHY IN ITS OWN DATA

> *Predicted: `tc-jabal-dabub` falls out of the top 6, because ruling 77 adds a
> fourth Arabia source-language record.*

**F6 has placed no Arabia record.** CIH 541 is unclaimed. `tc-jabal-dabub` held
at **rank 6**, and its crowders are unchanged from FINDING 73:

```
tc-jabal-dabub   rank 6 -> 6   beaten_by:
  arabia-04-jabal-dabub::translation::000
  arabia-06-syllaeus::original::000
  arabia-06-syllaeus::translation::000
  arabia-06-syllaeus::translation::002
  seasia-05-my-son-b6::translation::000
```

**No F6 record appears in that list.** The prediction's cause has not arrived, so
holding at 6 is not evidence against it. **The prediction stands, unmodified,
for the run that follows CIH 541.**

## P2 — NOT TESTED, FOR THE SAME REASON, AND ITS CAUSE IS ALSO UNFILLED

> *Predicted: `probe-tamil-akananuru-en` falls too, to a cross-regional crowder.*

**F6 has placed no East Asia record.** It held at **rank 6**, crowded by
`eastasia-07-tang-huiyao` and Periplus chunks — the same crowders as before, and
**no F6 record among them**.

## The second pair that got worse, and it is NOT read as a fourth result

`tc-frankincense-harvest` moved 12 → 13 and its `beaten_by` list is **empty**,
because that pair reaches its rank through ruling 2's aligned-translation accept
(13 → 1 on the alternate). **A one-rank move on a pair with no listed crowder,
across a view change, is not evidence of anything** and is recorded here so that
nobody later reads it as a fifth data point.

---

# What is owed after this run

1. **`python -m eval.run_ranking_check --with-distractors`** — the like-for-like
   comparison against the 2026-09-05 baseline. Cost: one embedding request for
   the 41 distinct query texts.
2. **P1 and P2 stay open and unmodified** until F6's Arabia and East Asia slots
   are filled. Reading them against this run would be reading a prediction
   against an experiment that does not contain its cause.
3. **The `africa-03-periplus-adulis` drift is in BOTH runs and is unchanged** —
   two archived chunk ids resolving to different ids while the originals still
   exist. That is debt item 9 and this run is not new evidence about it, only a
   second sighting.


---

# THE LIKE-FOR-LIKE RUN, 20260906T091154, `--with-distractors`, index 524

**This is the run ruling 78 was written against.** Same view as F5's closing run,
same gold set, 507 chunks then and 524 now — the difference is F6's three
records and nothing else.

## SIX PAIRS MOVED. ALL SIX WORSE. NONE BETTER. AND BOTH HEADLINE NUMBERS ARE IDENTICAL TO SIXTEEN DECIMAL PLACES

```
pair                                    05Sep    06Sep   delta
bronze-heracles-verethragna-from-mes       86      98     +12   worse
muziris-cargo-akananuru                   333     341      +8   worse
thorsberg-chape-niwajemariz                24      29      +5   worse
muziris-cargo-papyrus                     113     115      +2   worse
vimose-runes                               16      18      +2   worse
tc-frankincense-harvest                    12      13      +1   worse
   ...38 pairs unchanged

recall@6  (pairs)   0.7272727272727273  ->  0.7272727272727273   32/44
recall@6  (units)   0.8048780487804879  ->  0.8048780487804879   33/41
MRR@10    (pairs)   0.5577651515151515  ->  0.5577651515151515
MRR@10    (units)   0.6205284552845528  ->  0.6205284552845528
```

**Both numbers are blind, and they are blind for two different reasons.**
`recall@6` cannot see the moves because **not one pair crossed rank 6**.
`MRR@10` cannot see them because **every one of the six was already outside the
top ten** — 12, 16, 24, 86, 113, 333 — so all six moves happened where MRR@10
does not look.

**This is FINDING 73 happening again, in the same words.** That finding read:
*nine gold pairs fell, none improved, and the number a reader meets did not
move.* This one reads: **six gold pairs fell, none improved, and both numbers a
reader meets are identical to sixteen decimal places.** Twice in two tranches,
and the second time it was predicted.

---

# FINDING 79 — THE CROWDER IS THE RECORD THAT RESEMBLES THE TARGET, NOT THE RECORD FROM THE SAME REGION

Ruling 78's P3 predicted `vimose-runes` would fall. **It fell, and so did the
OTHER Scandinavian gold case, which nothing predicted.**

```
vimose-runes                 16 -> 18   beaten_by includes
    scandinavia-06-tjurko-bracteate::original::000
    scandinavia-06-tjurko-bracteate::translation::000

thorsberg-chape-niwajemariz  24 -> 29   beaten_by includes
    scandinavia-06-tjurko-bracteate::translation::000
```

**F6 curated TWO Scandinavian records and only ONE of them is in either list.**
`scandinavia-07-rycksta-grikkium` crowds neither case, and it is in the same
region, entered the index in the same hour, and is the longer of the two.

What separates them is not region. It is what the text LOOKS LIKE:

```
scandinavia-06-tjurko-bracteate   Elder Futhark, Proto-Norse, 5th-7th c., 95 chars
scandinavia-03-vimose             Elder Futhark, Proto-Norse   <- crowded
scandinavia-05-thorsberg-chape    Elder Futhark, Proto-Norse   <- crowded
scandinavia-07-rycksta-grikkium   younger futhark, Old Norse, 11th c.   <- crowds nothing
```

**Ruling 70 predicted cross-regional crowding; FINDING 73 amended it to
same-region crowding; this run amends it again, and the amendment is narrower
than either.** The region field is not what does the damage. A record crowds the
gold cases whose SOURCE TEXT IT RESEMBLES — same script, same language stage,
same genre — and a record from the same region five centuries later in a
different alphabet does not crowd them at all.

**COUNTED, NOT GATED, AND IT IS ONE OBSERVATION.** Two crowded cases and one
non-crowding record is not a law, and this finding names what would refute it:
an F7 record that crowds a gold case it does not resemble, or a resembling
record that crowds nothing. It is recorded now because **the next curation
decision it bears on is the Africa Ge'ez slot** — the corpus holds two Greek
Africa records and no Ge'ez, so on this reading a Ge'ez record should crowd
almost nothing, and on FINDING 73's reading it should crowd Africa's cases.
**Those two predictions differ, and F6's own last slot is the experiment.**

## What P1 and P2 did, and it is the same answer as before

`tc-jabal-dabub` held at 6 and `probe-tamil-akananuru-en` held at 6, with **no
F6 record in either `beaten_by` list**, because F6 has placed no Arabia and no
East Asia record. Both predictions stand unmodified.

## And the earlier run is now explained

The 2026-09-06 run without distractors showed *eight pairs better, two worse*.
Against this like-for-like run the truth is *none better, six worse*. **Every one
of those eight improvements was the 393 distractors leaving the index**, and
none of them was F6's doing.
