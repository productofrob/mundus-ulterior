# F6_RANKING_2 — the run F6 owed, made AFTER F6 closed. P1 CONFIRMED, P2
# CONFIRMED, **P4 REFUTED** — and the aggregate moved for the first time since F4

*Run on the host, 2026-09-06, archived at
`eval/ranking_runs/20260906T103920+0000-retrievable_chunks_with_distractors.json`.
Baseline: `20260906T091154+0000-retrievable_chunks_with_distractors.json`. Same
view, same flag, same models. **524 chunks against 544** — the four F6 records
added 20 chunks and nothing else changed.*

**`F6.closed` stays `true`.** This document reads a run F6 owed and could not make
from the bridge; it does not reopen the sub-tranche, curate anything, or move a
flag.

---

# THE HEADLINE MOVED, AND IT MOVED DOWN

```
                          20260906T091154        20260906T103920
                          43 records, 524        47 records, 544
recall@6  (pairs)         0.7272727272727273     0.6818181818181818
                          32 / 44                30 / 44
MRR@10    (pairs)         0.5577651515151515     0.5469336219336219
recall@6  (units)         0.8048780487804879     0.7560975609756098
                          33 / 41                31 / 41
MRR@10    (units)         0.6205284552845528     0.6113433991482773
```

**`ALL recall@6` has read 0.727 since F4 and it does not any more.** P1 predicted
that it would move and named the pair that would move it. It moved because that
pair, and one other, left the window.

## Fourteen pairs moved. Every one of them moved WORSE. None improved.

```
pair                                       old   new  delta
muziris-cargo-akananuru                    341   356   +15
muziris-cargo-papyrus                      115   127   +12
adulis-throne-leuke-kome                    31    42   +11
aksum-trade-adulis                          39    45    +6
bronze-heracles-verethragna-from-mesene     98   104    +6
tc-frankincense-harvest                     13    18    +5
tc-jabal-dabub                               6     9    +3   <- LEAVES the window
thorsberg-chape-niwajemariz                 29    32    +3
vimose-runes                                18    20    +2
cefu-yuangui-fulin-glass                     2     4    +2
china-describes-rome-weilue                 10    11    +1
china-describes-rome-houhanshu               8     9    +1
probe-tamil-akananuru-en                     6     7    +1   <- LEAVES the window
dong-yen-chau-naga-of-the-king               5     6    +1
   ...30 pairs unchanged
```

Two pairs crossed the recall@6 boundary and both crossed outward. `dong-yen-chau`
and `cefu-yuangui` moved inside the window and stayed in it.

---

# P1 — CONFIRMED, and the crowder is named. But not only the crowder it named.

**Predicted at `a20214e`, before any F6 record existed:** `tc-jabal-dabub` sat at
rank 6 with zero slack, having fallen 3 → 6, with three chunks of
`arabia-06-syllaeus` inside its window; a FOURTH Arabia source-language record
would push it out of the top 6, and `ALL recall@6` would move off 0.727 for the
first time since F4.

**Observed: 6 → 9. Both halves happened.** And the new record IS in the window
that beat it:

```
tc-jabal-dabub  beaten_by, new records only:
    arabia-07-cih541::original::000              <- predicted
    africa-06-ezana-rie189::translation::001     <- NOT predicted by anyone
```

**The unpredicted half is the interesting half.** P1's stated mechanism was
"Arabia crowding Arabia". What actually sits in that window is one Arabia chunk
and one **Africa** chunk — the English of a Ge'ez inscription — against a query
about a South Arabian monumental inscription naming Rome. A same-region reading
of this run gets the right answer for a reason that is only half right.

---

# P2 — CONFIRMED, and its crowder is cross-regional exactly as the prediction said it would be

**Predicted:** `probe-tamil-akananuru-en`, also rank 6 with zero slack, falls —
and **falls to a cross-regional crowder**, because F6 places one East Asia record
and no South Asia record at all. "If it falls, it falls to a cross-regional
crowder, which is ruling 70's mechanism and not ruling 73's."

**Observed: 6 → 7, and the crowder is `eastasia-08-songshi-fulin::original::000`
— 295 characters of Literary Chinese, beating a South Asian target on an English
query.** This is the cleanest confirmation in the run: the prediction named the
mechanism, not just the direction, and the mechanism is what happened.

---

# P4 — REFUTED. And the reading underneath it is not.

**Predicted at `2991e04`, after the Africa candidate was located and before the
record file existed:** `au-ezana-titles` falls, and the five Greek-target Africa
pairs do not move. FINDING 79's reading — the crowder is the record that
RESEMBLES the target, and a Ge'ez transliteration resembles nothing in an Africa
cohort of Greek chunks.

**Observed:**

```
au-ezana-titles              1 ->  1     HELD. beaten_by is EMPTY: nothing beats it.
probe-adulis-ivory           1 ->  1     held
silko-basiliskos             1 ->  1     held
adulis-exports              15 -> 15     held, and no new record is in its window
aksum-trade-adulis          39 -> 45     MOVED
adulis-throne-leuke-kome    31 -> 42     MOVED
```

**That is refutation shape 1, named in ruling 78 before the run:** *"The Adulis
or Silko pairs fall while `au-ezana-titles` holds — FINDING 73 is right, the
region is the crowder, and resemblance was a coincidence of the Elder Futhark
pair."* Two Adulis pairs fell and the resembling pair held. **P4 is refuted on
its own terms and the refutation was pre-written.**

## And now the part that only `beaten_by` can see

**The record P4 was ABOUT appears in exactly one `beaten_by` list in the entire
run, and it is not an Africa pair.**

```
africa-06-ezana-rie189  crowds:  tc-jabal-dabub          (Arabia, Sabaic)
                        crowds:  NOTHING in Africa
```

The Africa damage came from the OTHER record F6 placed in Africa the same day:

```
aksum-trade-adulis        beaten_by:  africa-07-cosmas-sasu::translation::000
adulis-throne-leuke-kome  beaten_by:  africa-07-cosmas-sasu::translation::003
                                      africa-07-cosmas-sasu::translation::000
                                      arabia-07-cih541::translation::000
                                      eastasia-08-songshi-fulin::original::000
```

`africa-07-cosmas-sasu` is 2,777 characters of **English prose about Adulis,
Aksum and the gold trade**, and the two pairs it crowds are the two Adulis trade
pairs. `africa-06-ezana-rie189` is a Ge'ez transliteration and an English
translation of a victory inscription, and it crowds a **Sabaic transliteration**
of a South Arabian inscription. **Both records crowded what they RESEMBLE.
Neither crowded its region.**

And one more, unpredicted and just as clean:

```
cefu-yuangui-fulin-glass  2 -> 4   beaten_by: eastasia-08-songshi-fulin::translation::003
                                              eastasia-08-songshi-fulin::translation::001
```

The Song History's account of 拂菻 crowds the Cefu Yuangui's account of 拂菻. Same
name, same subject, four hundred years apart, and the older record loses two
ranks to the newer one.

---

# FINDING 83 — a pre-registered prediction can be refuted by a mechanism it was right about, if it is denominated in the wrong unit

**P4 was denominated in "Africa's six ranking pairs".** F6 placed **two** Africa
records on the day P4 was written, with completely different chunk profiles: a
Ge'ez transliteration plus a short English translation, and 2,777 characters of
English prose on the region's best-known trade route. **The prediction named
`africa-06` as its candidate and then measured a region.**

So the run answers a question P4 did not mean to ask. Read at pair level, the
region moved and the resembling pair held, and FINDING 73 wins. Read at chunk
level, `africa-06` crowded nothing in its own region and `africa-07` crowded
exactly the two pairs about the subject it discusses, and FINDING 79 wins.

**Both readings are of the same run and they disagree**, and the only reason the
second one is available at all is that `beaten_by` records chunk ids rather than
counts.

## What follows, and it is a rule about predictions and not about crowding

**A prediction that names a record must be denominated in what that record could
crowd, not in the region it belongs to.** The unit P4 should have used is: *"no
`beaten_by` list in the run contains a chunk of `africa-06-ezana-rie189` except
where the target is itself a transliterated South-Semitic inscription."* That is
a sentence the archive can answer without ambiguity, and it would have been
CONFIRMED.

**P4 stands as refuted.** It is not rewritten to the sentence it should have
been — ruling 78's whole point is that a prediction read afterwards has an
explanation available for it, and rewriting the unit afterwards is the same
defect wearing arithmetic. **The refutation is the result, and the better unit is
what F7 uses.**

---

# FINDING 84 — every run in Block F that ADDED records has been monotone worse, and the one that got better was the one where the index shrank

```
run                         what changed                    better   worse
FINDING 73's run            F5's records entered                 0       9
FINDING 77's run            393 distractors LEFT                 8       2
this run                    F6's four records entered            0      14
```

**Not one gold pair in Block F has ever improved when a record was added.**
Twenty-three pairs have moved across the two record-adding runs and all
twenty-three moved down. The single run with improvements is the run where
three-quarters of the index was removed.

**Rank in this index is a function of index SIZE**, and `recall@6` — the number
G2's gate is denominated in — cannot tell that apart from index quality. FINDING
77 said "stop reading recall@6 as though it were a measure of index quality" on
the evidence of a headline that did not move. **This run is the same finding from
the other side: the headline moved, and it moved because the corpus got bigger.**

That is not an argument for curating less. It is an argument that **a gate which
falls every time the project does the thing it exists to do is measuring the
wrong quantity**, and Block G should know that before it reads a number off it.

---

# What did NOT move, and it is worth as much as what did

- **`au-ezana-titles` holds at rank 1 with an empty `beaten_by`.** The record it
  expects — `africa-01-ezana-stone`, a placeholder with a newspaper citation — is
  the weakest thing in the Africa cohort and it defended rank 1 against four new
  records. FINDING 80's warning that a weak chunk might be holding a rank it
  could not defend is answered: it defended it.
- **`adulis-exports` holds at 15 with no new record in its window.** Two Adulis
  pairs fell and the third did not, which is why "the region is the crowder" is
  too coarse even as the refuting reading.
- **`vimose-runes` 18 → 20 with no F6 record in its `beaten_by`.** P3 was
  confirmed in the earlier run and this drift is not more evidence for it.
- **`silko-basiliskos` and `probe-adulis-ivory` hold at 1.**

---

# The two archived chunk-ids that no longer name their passage

```
aksum-trade-adulis: africa-03-periplus-adulis::original::000 -> ::001
adulis-exports:     africa-03-periplus-adulis::original::002 -> ::005
```

**Unchanged, in every run, and still owed** — `git log --follow` on that record
is debt item 4. Both drifting pairs are Africa pairs and both are in the P4
analysis above; the drift is not new and is not what moved them, but a reader of
this document should know that the two pairs P4 turns on are the two pairs whose
ids drift.

---

# THE MUTATION HARNESSES, RUN THE SAME DAY ON THE HOST

`mutate_fidelity` **70/70**, `mutate_cost` **58/58**, sources restored. The owed
list is unchanged: three refusal guards in `mutate_fidelity` and
`GUARD a reinstated_on that is not a date is refused` in `mutate_cost`.
