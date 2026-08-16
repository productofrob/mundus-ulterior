# Block B3 — distractor seams, RULED 2026-08-14

`PHASE2_PLAN.md` action #3: *"You choose these. Anything that could actually
answer a gold-set question is not a distractor, and a curve built on
secretly-relevant padding will wave W3 through."*

**The three decisions are made** — see "Rulings" at the foot. Nothing has been
fetched yet. The seam arguments below are kept as written, including the two the
ruling went against, because a proposal edited to agree with the decision is not
a record of the decision.

**Target:** ~400 distractor chunks, so the index reaches ~450 alongside the real
corpus. The real corpus is **57 eligible chunks, not 54** — the 54 in
`PHASE2_PLAN.md` Action #1 is stale on the page. The rungs are **57 → 150 → 450**,
and the 57-chunk rung is already recorded
(`eval/ranking_runs/20260814T082748+0000`).

**Ranking depth is settled and must not change between rungs:** every pair is
ranked against the whole view, so no pair is ever out of reach and the gap means
are complete at 57, 150 and 450 alike. A fixed depth cannot be right at more than
one rung.

## What the B2 baseline changed about this document

Written before the baseline existed. Three results now bear on it, and none of
them changes the three decisions — they change what is at stake in each.

**1. The mean gap is already zero at 57 chunks.** `gapAny` across the gold set is
**0.000** and `gapDoc` is +0.035. The known-good passage, averaged over 32 pairs,
scores no better than the best competing passage in an index of fifty-seven. The
W2b curve is therefore not measuring *whether* a gap erodes — it is measuring how
far below zero it goes, from a start that is already at zero.

**2. Competing documents already outrank the archived targets.** `archived_answer`
sits at `gapDoc -0.111`: for the Phase 1 questions, some *other document* beats
the right one by a tenth of a similarity point before a single distractor exists.
Seam 2's risk is therefore not hypothetical. Strabo on the Indian Ocean would not
merely be "plausibly similar" — it would be competing in a race the corpus is
already losing.

**3. The cohort seam 3 attacks is the strongest one.** `authored` scores 0.889
with `gapDoc +0.057`, and all nine of its targets are English object
descriptions. Museum catalogue prose is the only candidate seam that competes
with them. That makes seam 3 **the highest-value distractor in the list, not the
safest** — it is the only one that can tell you whether the English-to-English
result is real or an artefact of having no English competition. The reverse of
how the seam was framed below.

**4. One target is already unreachable.** `muziris-cargo-akananuru` — Old Tamil —
does not appear in the top 50 of 57. It cannot degrade further, and it will read
as flat across all three rungs. Do not read that flatness as robustness.

---

## The test each candidate has to pass

A distractor must be **plausibly similar and known-irrelevant**. Those pull in
opposite directions, and the failure mode is asymmetric:

- Too dissimilar (modern news, software docs) and the curve is flat for a reason
  that has nothing to do with the corpus. W2c then looks unnecessary and W3 gets
  a green light it did not earn.
- Secretly relevant and the "irrelevant" chunk outranking the target is
  **correct** retrieval scored as failure. The curve then looks like a cliff and
  W2c spends six sessions hardening against a phantom.

The concrete danger for this corpus: **the gold set is 32 pairs over 20
documents, 12 of them Greek, and the obvious distractor seam is more Greek
geography about the same ports.** Strabo on Muziris is not a distractor. Ptolemy
on Adulis is not a distractor.

## Seam 1 — Periplus sections not in the corpus

`§1–3, §7–26, §30–52, §57–66` (Greek Wikisource, ed. Müller, *GGM* I — the route
Part 3b already used).

| | |
| --- | --- |
| **For** | Identical author, register, vocabulary and edition. This is the strongest similarity available anywhere, and the fetch route is already built and licensed. |
| **Against** | **§30–52 and §57–66 are the ones to worry about.** §41–48 cover Barygaza and the Indian west coast; §51–52 run down toward Limyrike. Several gold pairs are about ships, cargoes, pepper and Indian ports. A §51 chunk outranking the §56 pepper chunk may be the index doing the right thing. |
| **Proposal** | Take **§1–3, §7–26 and §57–66** — Egypt to the Horn, the Somali coast, and the far side past Limyrike. **Exclude §30–52 entirely.** ~55 sections, ~90 chunks. |
| **Needs your ruling on** | Whether §7–26 is safe. It is the Berber/Azanian coast, and `africa-03-periplus-adulis` (§4–6) plus `arabia-01-periplus` (§27–29) sit on either side of it. §16–18 mention ivory and tortoise-shell — the exact commodities in the `adulis-exports` pair. **My reading: exclude §14–26 as well**, leaving §1–3 and §7–13 (~15 sections, ~25 chunks). Cheap to be strict here; the section count is easy to make up elsewhere. |

## Seam 2 — other classical geography

Strabo, Ptolemy's *Geography*, Pliny *NH* VI.

| | |
| --- | --- |
| **For** | Same genre, same centuries, same Greek and Latin registers. Large and openly available. |
| **Against** | These are the *most* dangerous candidates in the list. Strabo XV and Pliny VI 26 are the standard companion sources for Muziris and the pepper trade; Ptolemy VII names Muziris directly; Pliny VI 34 covers the Red Sea ports. Any of them could answer a gold-set question better than the corpus does. |
| **Proposal** | Take these only from **regions the corpus has no pair in**: Strabo IV–VII (Gaul, Italy, the Alps, the Balkans), Pliny *NH* III–IV (Italy, Spain, the western provinces). Roman geographical prose about the Mediterranean interior — same author, same genre, same date, and nothing in the corpus asks about Gaul. ~200 chunks available easily. |
| **Needs your ruling on** | Whether *any* Strabo/Pliny/Ptolemy passage on the Indian Ocean, Arabia, Aksum or the Silk Road is admitted. **My reading: none of it.** The gain in similarity is small and the risk is exactly the failure mode action #3 warns about. |

## Seam 3 — museum catalogue prose

Object descriptions from open-data collections, chosen for stylistic similarity
to the corpus's find records.

| | |
| --- | --- |
| **For** | Nine corpus documents are catalogue prose in English (Hoby, Gudme, Illerup, Óc Eo ×2, Khao Sam Kaeo, Pattanam, Hwangnam glass, the two BM Sasanian objects), and nine gold pairs target them. Nothing else in the candidate list resembles that register at all, and without it the English half of the curve is untested. |
| **Against** | Easy to pick badly. "Roman glass" or "Sasanian silver" queries against a collection search will return the same object families the corpus holds. |
| **Proposal** | Draw from a **single named collection with clear open licensing**, restricted to material with no contact-with-Rome dimension: Egyptian dynastic, Mesopotamian, pre-Columbian, East Asian ceramics, European medieval. Same catalogue voice, same length, no overlap with any gold pair. ~100–150 chunks. |
| **Needs your ruling on** | The collection, and its licence. The Met and the Rijksmuseum publish open-licensed object data; the BM's terms are more restrictive and the corpus already cites BM records, which would blur the line between corpus and distractor. **My reading: one collection only** — mixing three makes "where did this come from" a per-chunk question. |

## What this adds up to

| seam | proposed | chunks |
| --- | --- | --- |
| 1 | Periplus §1–3, §7–13 | ~25 |
| 2 | Strabo IV–VII, Pliny *NH* III–IV | ~200 |
| 3 | one open collection, non-Roman-contact material | ~150 |
| | **total** | **~375** |

375 + 57 = **432**, close enough to the 450 rung. If you take the stricter
reading on seam 1, seam 2 makes up the difference easily.

## Rulings — Rob Padilla, 2026-08-14

| # | decision | outcome |
| --- | --- | --- |
| 1 | Periplus scope | **§1–3 and §7–13 only** (~25 chunks). §14–26, §30–52 and §57–66 all excluded. |
| 2 | Indian Ocean / Arabian classical geography | **Admitted freely.** Strabo XV, Pliny *NH* VI, Ptolemy VII are all in scope. |
| 3 | Museum collection | **The Met Open Access**, single collection, non-Roman-contact material only. |

Decision 1 took the strict reading, including the §57–66 exclusion added after I
noticed that range sits on the Southeast and East Asia records' geography.

### Decision 2 changes what the curve means, and that is the thing to hold on to

I recommended against it. The ruling stands and the reasoning is worth stating
plainly rather than repeating the objection:

Admitting Strabo on Muziris and Pliny on the Red Sea ports means some distractors
**can genuinely answer a gold-set question**. When one of them outranks a gold
target, that is not obviously an error — a user asking what ships carried from
Muziris is arguably well served by Strabo XV. So the curve stops measuring *"does
the right passage survive noise"* and starts measuring *"does the designated
passage survive competition"*.

That is a defensible and arguably more realistic question. It is **not the
question `PHASE2_PLAN.md`'s B5 decision point was written against**:

> degradation **milder** than predicted → W3 can move faster, and say so
> degradation **as or worse than** predicted → W2c is load-bearing and W3 stays shut

Read against a curve containing semantically relevant competitors, "worse than
predicted" no longer implies W2c is load-bearing — it may mean the corpus is
small and the world is large, which no amount of reranking fixes. **The decision
point has to be restated before B5 runs**, or the block will produce a verdict
about hardening from evidence about coverage.

### What is being built instead of the objection

B5 will report, for every pair whose rank worsens between rungs, **the text of
whatever outranked it** and whether that thing is a distractor. Roughly twenty
lines of adjudication per rung, and it converts the risk from an assumption into
a thing you can look at and rule on case by case.

Without it, a distractor-driven collapse and a noise-driven collapse are the same
number. With it, decision 2's cost is visible and bounded.

## Chunk budget under the rulings

| seam | scope | chunks |
| --- | --- | --- |
| 1 | Periplus §1–3, §7–13 | ~25 |
| 2 | Strabo IV–VII and XV, Pliny *NH* III–IV and VI, Ptolemy VII | ~225 |
| 3 | The Met, non-Roman-contact material | ~150 |
| | **total** | **~400** |

400 + 57 = **457**, against the 450 rung. Decision 2 makes seam 2 large and easy
to fill, which is exactly why the adjudication step above matters: the loosest
seam is now also the biggest.

## Before anything is fetched

1. **Verify the Met's current licence terms** and write
   `data/met-licence-declaration.txt`, matching the practice already established
   by `data/pleiades-licence.txt` and `data/geonames-licence.txt`. My
   recollection is CC0 for Open Access object data; recollection is not a licence
   check, and this project's standing rule is that nothing enters the corpus on a
   remembered provenance.
2. **Restate the B5 decision point** in light of decision 2, above.
3. B4's containment work, unchanged by any of this: `is_distractor` column,
   `retrievable_chunks` stays distractor-free, a separate
   `retrievable_chunks_with_distractors` view, and a mutation-verified test that a
   distractor is unreachable from the answer path.
