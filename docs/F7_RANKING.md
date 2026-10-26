# F7 RANKING — P1 and P4 and P5 confirmed, **P2 and P3 refuted**, and the
# clearest evidence Block F has produced that rank is a function of index size

*Run on the host, 2026-09-06, archived at
`eval/ranking_runs/20260906T170622+0000-retrievable_chunks_with_distractors.json`.
Baseline: `20260906T103920+0000-retrievable_chunks_with_distractors.json`. Same
view, same flag, same models, no `--collapse`, no `--rerank`, no `--fuse`.
**561 chunks against 544** — F7's seven records added 17 chunks and nothing else
changed.*

All five predictions were written in `F7_CURATION_START.md` at `d2868fc`, before
any F7 record file existed, and each named its own refutation.

---

# THE HEADLINE, AND IT FELL AGAIN

```
                          20260906T103920        20260906T170622
                          47 records, 544        54 records, 561
recall@6  (pairs)         0.6818181818181818     0.6590909090909091
                          30 / 44                29 / 44
MRR@10    (pairs)         0.5469336219336219     0.5401154401154401
recall@6  (units)         0.7560975609756098     0.7317073170731707
                          31 / 41                30 / 41
MRR@10    (units)         0.6113433991482773     0.6040263259775455
```

**Thirteen pairs moved. Every one of them moved worse. None improved.** Thirty-one
were unchanged. One pair crossed the recall@6 boundary and it crossed outward:
`dong-yen-chau-naga-of-the-king`, 6 → 9.

```
pair                                       old   new  delta
muziris-cargo-akananuru                    356 -> 373  +17
muziris-cargo-papyrus                      127 -> 139  +12
bronze-heracles-verethragna-from-mesene    104 -> 113   +9
aksum-trade-adulis                          45 ->  53   +8
adulis-throne-leuke-kome                    42 ->  49   +7
dong-yen-chau-naga-of-the-king               6 ->   9   +3   <- LEAVES the window
china-describes-rome-weilue                 11 ->  13   +2
china-describes-rome-houhanshu               9 ->  11   +2
au-khao-sam-kaeo                            17 ->  19   +2
thorsberg-chape-niwajemariz                 32 ->  34   +2
tc-frankincense-harvest                     18 ->  19   +1
kedukan-bukit-saka-605                       3 ->   4   +1
cefu-yuangui-fulin-glass                     4 ->   5   +1
   ...31 pairs unchanged
```

---

# P1 — CONFIRMED, and 拂菻 has now crowded 拂菻 twice in two sub-tranches

**Predicted at `d2868fc`:** `cefu-yuangui-fulin-glass`, at rank 4 having fallen
2 → 4 in the F6 run to two translation chunks of `eastasia-08-songshi-fulin`,
falls again, and at least one chunk of `eastasia-09-jiutangshu-fulin` is in its
`beaten_by`.

**Observed: 4 → 5, and the chunk is there.**

```
cefu-yuangui-fulin-glass  beaten_by, new records only:
    eastasia-09-jiutangshu-fulin::translation::006
```

Three accounts of Fu-lin now sit in this corpus — the Cefu Yuangui's, the Song
History's four hundred years later, and the Jiu Tangshu's in English — and the
newest one has beaten the oldest one twice running, from two different records.
**The mechanism is not in doubt any more.** What P1 adds to F6's observation is
that it works from an ENGLISH chunk against a Literary Chinese target: the
crowder here is McCrindle-style prose, not 拂菻 in characters.

## And the unpredicted half, which is where the interest is

```
dong-yen-chau-naga-of-the-king  6 -> 9   beaten_by:  eastasia-09-jiutangshu-fulin::translation::001
```

A Tang history's account of Byzantium crowded **a fourth-century Cham inscription
from Vietnam** out of the recall@6 window. That is the single pair F7 cost the
corpus, and it was cost by the record furthest in subject from it. F6's P1 had
exactly this shape — a Ge'ez translation chunk turning up in an Arabian pair's
window that no mechanism predicted — and it is now twice that the *unpredicted*
entry in a `beaten_by` list has been the informative one.

---

# P2 — REFUTED, and more completely than F6's P4 was

**Predicted:** `au-oc-eo-medallion`, at rank 1 expecting `seasia-01-oc-eo-medallion`,
**leaves rank 1**, with chunks of `seasia-09-oc-eo-unesco` in its `beaten_by`.
This was written as the experiment F6's P4 could not run: there `au-ezana-titles`
held rank 1 against a record that resembled it only regionally, and P2 put a
record against it that names the same site, the same excavation and the same
class of object, in the same language as the target's own description.

**Observed:**

```
au-oc-eo-medallion       1 -> 1     beaten_by EMPTY, in both runs
                                    gapAny  0.0071 -> 0.0071, unchanged to four places
                                    best_other_chunk: seasia-01-oc-eo-medallion::original::000
seasia-09-oc-eo-unesco   appears in NO beaten_by list anywhere in the run
```

**This is not "the pair defended itself".** The crowder never arrived. 1,103
characters of English prose naming Óc Eo, the excavation and Roman gold coins did
not enter the top six of a query about the Óc Eo medallion — and the nearest
competitor to the target chunk is **another chunk of the target's own record**,
at a gap that did not move at all.

`au-ezana-titles` also held at 1 with an empty `beaten_by` and an unchanged gap,
for the second run running. **Two rank-1 pairs have now been shot at deliberately
and neither moved a place.** Whatever defends rank 1 in this index, it is not the
absence of a resembling record, and FINDING 79's resemblance mechanism — which
explains the middle of the list well — does not reach the top of it.

---

# P3 — REFUTED, in the second of the two directions the prediction named

**Predicted:** no `beaten_by` list in the run contains a chunk of
`persia-07-met-ewer-anahita` **except** where the target is
`persia-04-bronze-heracles` — the corpus's one other record about a Greek god
identified with an Iranian one. **Refuted by:** it appears against any other
target, **or against none at all.**

**Observed: against none at all.** `persia-07-met-ewer-anahita` appears in no
`beaten_by` list in the run. And the pair it was aimed at fell nine ranks anyway:

```
bronze-heracles-verethragna-from-mesene   104 -> 113
  beaten_by OLD:  persia-04-bronze-heracles::translation::000
                  persia-05-abnun::translation::000
                  persia-06-shahrestaniha::translation::001
                  persia-01-skz::original::000
                  persia-01-skz::translation::000
                  persia-03-coin::original::000
  beaten_by NEW:  identical, entry for entry, in the same order
  gapAny:         -0.4224 -> -0.4224
```

**The pair lost nine ranks with a byte-identical window and an identical
similarity gap.** Nothing that beat it before beats it any harder; nothing new
beat it at all. Nine chunks of the seventeen added simply sorted above it
somewhere below the sixth place, where `beaten_by` cannot see.

That is the second refutation direction stated in advance — *"a short object
description cannot crowd anything"* — and three of F7's five catalogue records
confirm it by appearing nowhere.

---

# P4 — CONFIRMED, on both halves

**Predicted:** at most two of F7's five `catalogue_record` chunks appear in any
`beaten_by` list, and both `published_translation_only` records appear in at
least one each.

```
record                              tier                        appears against
persia-07-met-ewer-anahita          catalogue_record            —
arabia-08-walters-marib-pediment    catalogue_record            —
southasia-07-bm-claudius-aureus     catalogue_record            —
seasia-09-oc-eo-unesco              catalogue_record            —
seasia-08-pong-tuk-lamp             catalogue_record            au-khao-sam-kaeo
                                                                kedukan-bukit-saka-605
eastasia-09-jiutangshu-fulin        published_translation_only  cefu-yuangui-fulin-glass
                                                                dong-yen-chau-naga-of-the-king
southasia-06-cosmas-taprobane       published_translation_only  adulis-throne-leuke-kome
```

**One of five, not two; both prose records present.** Confirmed with room to
spare, and the shape is F6's exactly: the records that crowd anything are the
long English ones, and the short object descriptions are invisible.

## The one catalogue record that did crowd, and why it is not a counter-example

`seasia-08-pong-tuk-lamp` is 495 characters — the second-shortest excerpt F7
placed — and it crowded two Southeast Asian pairs. It is also the only F7 record
whose region, subject class and object class all coincide with its targets: a
Mediterranean object found in Thailand, against a query about a Mediterranean
intaglio found in Thailand. **Both mechanisms point the same way on it**, which is
precisely the case F6's P1 could not separate and this run does not separate
either.

## And `southasia-06-cosmas-taprobane` crowded AFRICA, not South Asia

```
adulis-throne-leuke-kome  42 -> 49   beaten_by: southasia-06-cosmas-taprobane::translation::001
```

The record's own notes said, before the run: *"If the resemblance mechanism
holds, its chunks should appear against Indian Ocean trade targets ACROSS regions
rather than in South Asia alone."* It appears against one pair in the whole run
and that pair is an **Aksumite throne inscription**. The passage names `Adulé`
twice.

**And `africa-07-cosmas-sasu` — the same author, the same translator, the same
1897 edition, curated in F6 — crowded the two Adulis pairs and nothing else.**
Cosmas has now crowded Adulis from two different books of the Christian Topography
in two consecutive sub-tranches, once filed under Africa and once under South
Asia. The region on the record did not predict anything; the word in the text did.

---

# P5 — CONFIRMED, both halves, and said before the run

**Predicted:** `ALL recall@6` falls from 0.6818, and NO gold pair improves.
**Observed:** 0.6818 → 0.6591, and thirteen pairs moved, all thirteen worse.

```
run                         what changed                    better   worse
FINDING 73's run            F5's records entered                 0       9
FINDING 77's run            393 distractors LEFT                 8       2
F6's run                    F6's four records entered            0      14
THIS RUN                    F7's seven records entered           0      13
```

**Thirty-six pair movements across three record-adding runs in Block F, and not
one of them upward.** The only run with improvements remains the one where
three-quarters of the index was removed.

---

# FINDING 91 — a fall is predicted by the pair's DEPTH, not by what was added

**Eight of the thirteen falls have no F7 chunk in the pair's window at all.**

```
pair                                       old   new  delta   F7 chunk in beaten_by?
muziris-cargo-akananuru                    356 -> 373  +17     no
muziris-cargo-papyrus                      127 -> 139  +12     no
bronze-heracles-verethragna-from-mesene    104 -> 113   +9     no
aksum-trade-adulis                          45 ->  53   +8     no
adulis-throne-leuke-kome                    42 ->  49   +7     YES
thorsberg-chape-niwajemariz                 32 ->  34   +2     no
au-khao-sam-kaeo                            17 ->  19   +2     YES
tc-frankincense-harvest                     18 ->  19   +1     no
china-describes-rome-weilue                 11 ->  13   +2     no
china-describes-rome-houhanshu               9 ->  11   +2     no
dong-yen-chau-naga-of-the-king               6 ->   9   +3     YES
cefu-yuangui-fulin-glass                     4 ->   5   +1     YES
kedukan-bukit-saka-605                       3 ->   4   +1     YES
```

**Read down the delta column and then down the old-rank column.** The order is
almost the same. Seventeen chunks entered a 544-chunk index — 3.1% growth — and
the pairs ranked in the hundreds lost eight to seventeen places while the pairs
ranked in the top six lost one to three. **Every pair at rank 1 or 2 lost
nothing**, and thirty-one pairs did not move at all.

`bronze-heracles-verethragna-from-mesene` is the clean case and it is worth
stating on its own: **nine ranks lost, `beaten_by` identical entry for entry,
`gap_vs_other_chunk` identical to four decimal places.** No new competitor
entered its window and its distance from the old ones did not change. The rank
moved because the index got bigger.

**FINDING 84 said `recall@6` cannot tell index growth from corpus quality. This
run says something narrower and harder: for most of the pairs that moved, index
growth is the ONLY thing that happened.** A gate reading a number that behaves
this way is reading a proxy for corpus size with the sign flipped, and Block G
should know the size of the effect — roughly **three ranks per hundred, per three
per cent of index growth** — before it reads a recall figure off a bigger corpus.

---

# WHAT THIS RUN SAYS ABOUT PREDICTIONS, WHICH IS RULING 78's WHOLE POINT

**Five predictions, three confirmed and two refuted, and the two refutations are
worth more than the three confirmations.**

- **P1 confirmed** what F6 already showed, from a new direction: English prose
  crowding a Literary Chinese target on the same subject.
- **P4 confirmed** what F6 already showed, with a count: long records crowd,
  short ones do not.
- **P5 confirmed** what FINDING 84 already said, for the third run running.
- **P2 refuted**, and it killed a mechanism's reach rather than the mechanism:
  resemblance explains the middle of the list and has now failed twice at the
  top of it.
- **P3 refuted**, and it produced the run's best single piece of evidence — the
  pair it was aimed at fell nine places with an unchanged window, which is
  FINDING 91.

**Both refutations came from predictions that named their own refutation
conditions in advance**, and in P3's case named *which* refutation would mean
what. That is the difference between a prediction and a reading, and it is the
thing ruling 78 exists to buy.

---

# THE TWO ARCHIVED CHUNK-IDS THAT STILL DO NOT NAME THEIR PASSAGE

```
aksum-trade-adulis: africa-03-periplus-adulis::original::000 -> ::001
adulis-exports:     africa-03-periplus-adulis::original::002 -> ::005
```

Unchanged, in every run of Block F, and still owed. `git log --follow` on that
record is the debt item, and both drifting pairs are Africa pairs — one of which,
`aksum-trade-adulis`, is in this run's fall list with no F7 chunk in its window.

# AND RULING 54's CAVEAT APPLIES TO TWO OF THE FIVE CROWDED PAIRS

`dong-yen-chau-naga-of-the-king` and `kedukan-bukit-saka-605` were both written
AFTER their records were already in the index, so they may not be cited as
evidence that a tranche IMPROVED retrieval. They are cited here as evidence of
degradation, which is the opposite claim and is not what ruling 54 guards
against — but the caveat travels with the pairs and is recorded rather than
omitted.
