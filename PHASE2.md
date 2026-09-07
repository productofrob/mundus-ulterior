# Mundus Ulterior — Phase 2 Plan

_Written 2026-08-12, immediately after the Phase 1 exit gate._

---

## Start here — reading order

`PROGRESS.md` is 3,300 lines. **Do not read it linearly.** It is a chronological
log whose value is that it records what was believed at the time and how that
turned out to be wrong — the Aksum entry reverses itself twice. That makes it
excellent evidence and a poor orientation document.

**Read in full (~700 lines, in this order):**

1. `README.md` — what the thing is, and the module map. 41 files, ~13,000 lines,
   one line each.
2. **`PROGRESS.md`, the closing summary only** — the final section, `# Phase 1 —
   closing summary`. What was built, what was proven, what was not, and the debt
   table pointing each open item at the workstream that owns it.
3. This file.
4. `STARTUP.md` — before running anything, every session.

**Then grep `PROGRESS.md` as needed.** The entries worth finding:

| Grep for | Why |
| --- | --- |
| `## Part 6 — RESULT` | How confidence bands were calibrated, and the stability rule for placing a threshold |
| `the finding that invalidated the floor` | Why the floor is `calibrated: false` — session variance, discovered hours after it was set |
| `## Part 9 — what's in place` | The span audit, and why an archived citation is only valid against the corpus version that made it |
| `Corrected 2026-08-12` | The Aksum diagnosis, including the two hypotheses that were wrong |
| `Standing lessons` | Appears several times; the consolidated list is at the foot of this file |

**Do not** reconstruct Phase 1's reasoning from scratch. If something looks like
an odd decision, it is probably in there with the defect that caused it.

---

## Ground rules carried in

- **Nothing is placed, quoted or claimed without a source.** This is the ethic
  the whole project runs on, and W1 extends it to geography.
- **Archive runs, not verdicts.** It has paid for itself three times, once in
  money.
- **Mutation-verify every guard.** A guard that has never been seen to fail is
  not known to work.
- **The gateway's free tier is 3 requests/minute.** Batch aggressively.

**Phase 2 in one sentence:** put the sourcebook on a map, make ranking something
that is measured before it is tuned, and only then grow the corpus — in tranches,
against a gold set large enough to tell a bad session from a bad case.

---

## Why this order, and not the one in the showcase brief

The brief (`Mundus_Ulterior_AI_Tech_Showcase_Rev.docx`) puts **GraphRAG** in
Phase 2, the **map** in Phase 3, and lists **reranking and hybrid search** in
Appendix B as optional. Phase 1 produced evidence that reorders all three.

**1. The graph has nothing to traverse yet.** The brief's own hero query is *"How
did Roman glassmaking connect to trade routes that reached Han China?"* The
corpus holds one Roman glass record (Hwangnam-daechong) and no workshop, route or
entrepôt records at all. A knowledge graph over 24 documents would have roughly
50 nodes, and its multi-hop queries would have to be hand-picked to work — which
is exactly the "passes for the wrong reason" failure Phase 1 caught four times.
**Phase 2 is not a replacement for the graph; it is the precondition for it.**

**2. Reranking is not optional.** Mean top-1 to rank-6 similarity spread across
77 archived runs is **0.105**; on the questions that matter, 0.045–0.094. The
Adulis export answer arrived at **rank 3, 0.012 below top-1**. At 200 documents
the eligible-chunk count goes from 54 to roughly 450 — about 8× the density
inside that same band — and that chunk lands near rank 20, outside a
`max_sources` of 6. **Scaling the corpus before hardening retrieval will make the
demo worse, not better.** Appendix B called this "an easy, measurable
groundedness win"; it is the load-bearing item of Phase 2.

**3. The map is cheap and the brief rates it "High — the Orbis parallel."**
17 of 24 records already carry named findspots; the 7 that do not are all
literary and carry the richest *subject* geography instead. Pleiades supplies
stable, cited, CC-BY place identifiers, and ToposText — already 3 of the 24
citations — is built on it. Deferring geography again would leave the reference
model unevidenced through two more phases, on a project named for it.

**What Phase 2 is therefore not:** GraphRAG, multimodal/HTR ingestion, and
multi-agent orchestration are all out of scope, and each has a named
precondition below. Refusing to start them is a decision, not an omission.

---

## The four workstreams

W1 and W2 run in parallel — they touch different code and W1 spends no API
calls. W3 is gated on W2. W4 runs alongside W2 and W3 and is what makes W3
legible.

```
W1 Geography        ────────────────►  (independent, no API cost)
W2 Retrieval        ──────────►  G2  ──►  W3 Corpus scaling  ──►  G3
W4 Gold set         ──────────────────────────────────────────►  G4
                                                                  │
                                                          Phase 2 exit gate
```

---

## W1 — Geography

**Goal:** every record placed, and every placement carrying its own provenance.

### Design decisions

- **Two place fields, not one.** `findspot_places` (where the object was found)
  and `subject_places` (where the text is *about*). They are strongest in
  opposite records: findspots exist for the 17 object records, subject geography
  for the 7 literary ones. A findspot map of 24 objects is a dot map; a
  subject-place map is a network, and the network is the ORBIS-shaped thing.
- **A place is a citation.** Each entry carries `{name, pleiades_id, uri,
  ground, note}`. Nothing is placed without a source, exactly as nothing is
  quoted without one.
- **`ground` records how the placement was arrived at**, and the UI shows it:
  - `stated` — the record itself names the place;
  - `identified` — a scholarly identification, with the citation that makes it
    (Adulis ≈ modern Zula; Muziris ≈ Pattanam is *contested* and must be
    labelled so);
  - `regional` — only the region is known, and the record says so rather than
    guessing a point.
- **Coordinates are never authored.** They are read from Pleiades via the
  `pleiades_id` and cached. A coordinate with no gazetteer id is a bug, and the
  build script fails on one.
- **Contested identifications stay contested.** Muziris/Pattanam is the live
  example. The UI must be able to render "probably here, and here is the
  argument" without flattening it to a pin.

### Deliverables

- `data/seed_corpus/**` — two new optional blocks per record.
- `data/gazetteer.json` — cached Pleiades lookups, so the build is offline and
  reproducible.
- `ui/` — region view becomes a place view; trade texts render as edges between
  subject places; every point clicks through to the record, the quotation and
  the characters on disk.
- Extend `ui/build_ui_data.py --verify` to audit placements the way it already
  audits quote spans.

### Gate G1

1. **24/24** records carry at least `regional` placement; **≥17** carry a named
   place with a resolving `pleiades_id`.
2. **Zero** coordinates in the bundle that do not derive from a gazetteer id —
   asserted by the build script, mutation-verified like the Phase 1 guards.
3. Every `identified` placement carries a citation; at least one contested
   identification renders as contested rather than as a pin.
4. The chain is unbroken end to end: **map point → record → quotation →
   characters on disk**, clickable, no dead link.

**Anti-goal:** a prettier map that asserts more than the evidence supports. If a
placement cannot be sourced, `regional` is the correct answer and the map should
look sparser for it.

---

## W2 — Retrieval hardening

**Goal:** ranking becomes measured, then improved — in that order.

Phase 1's standing lesson applies directly: instrument before you tune, or you
cannot tell a fix from a coincidence. Today there is **no ranking metric at all**;
the 11/11 probe result tests whether the right chunk is *in the corpus*, not
whether it is *ranked*.

### W2a — Measure first (no model changes)

- Build a ranking gold set: **≥20 question → known-good-chunk pairs** over the
  current 24 documents, drawn from cases where Phase 1 already established what
  the right passage is (the Adulis export chunk, the Muziris §56 pepper chunk,
  the Vimose transliteration chunk, and so on).
- Report **recall@6, MRR@10, and the score gap** between the known-good chunk and
  the highest-ranked irrelevant chunk. That gap, not the raw similarity, is what
  predicts survival at scale.
- **Record the baseline before touching anything.** It is the only number that
  can later show the hardening worked.

### W2b — The distractor experiment

The cheapest way to find out what happens at 200 documents is not to curate 200
documents.

Pad the index with **N known-irrelevant but plausibly-similar chunks** — further
public-domain Periplus sections, other classical geography, other museum
catalogue prose — and measure how the rank of each known-good chunk degrades as
N grows: 54 → 150 → 450 chunks. Distractors are flagged in the database and
excluded from every other metric.

**This predicts the 200-document behaviour before a single record is curated**,
and it turns the central Phase 2 assumption from an argument into a curve. If
degradation is milder than predicted, W3 can move faster; if it is worse, W3 does
not start.

### W2c — Then harden

- **Hybrid retrieval** — lexical (BM25 or `tsvector`) fused with dense. Justified
  by the Aksum finding: the model answered when the question shared wording with
  the passage. Lexical signal is exactly what dense-only retrieval discards.
  Needs care across scripts — a lexical index over Literary Chinese and Old Tamil
  is not the same problem as over English.
- **Cross-encoder reranking** over the fused candidate set.
- **Re-examine the fold.** `align._merge` presents a whole section when only one
  member was retrieved. Phase 1 proved this is *not* what breaks Aksum, so this
  is a ranking-quality question, not a bug fix: does surfacing the retrieved
  member score better than the merged section?

### Two carried defects, fixed here

- `cite.py`'s `locate_in_text` falls back to a case-folded search and still
  records `match="exact"`. Six archived spans affected. Add a third state.
- `translation_chunk_id` names the *retrieved member* while `translation_chunk`
  is the *merged section*. The arithmetic is right; the names are a trap. Rename.

### Gate G2

1. A ranking metric exists over ≥20 pairs, with a **baseline recorded before any
   change**.
2. The distractor curve is plotted to ≥450 chunks and its shape is stated in
   `PROGRESS.md`.
3. After hardening, the known-good chunk is in the **top 6 for ≥95%** of the
   ranking gold set **at 450 chunks including distractors** — that is the
   condition that matters, not performance at 54.
4. The score gap between known-good and best-irrelevant is **wider than
   baseline**, measured on the same pairs.
5. Measured across **≥2 sessions on different days**. A single-session ranking
   result is one sample, and Phase 1 established that the hard way.

**If G2 fails, W3 does not start.** That is kill trigger 1 from the exit gate.

---

## W3 — Corpus scaling, in tranches

**Goal:** 24 → 60 → 200 documents, with the degradation curve visible at each
step rather than discovered at the end.

### Required before the first tranche

**Record the corpus version in every answer.** A content hash of each seed record
at answer time, stored beside `prompt_version`. This is the fifth appearance of
the Phase 1 defect family and the only one still open: an archived citation
currently cannot be told from a stale one without re-checking the whole corpus.
The Adulis span found in Part 9 is the evidence, and the more the corpus is
edited — which is the whole of W3 — the more it bites.

### Design decisions

- **Depth, not breadth.** All seven regions already exist. The brief's advice was
  depth-first and Phase 1 went the other way; W3 corrects that by deepening
  regions rather than adding them. Target ~30 records per region at 200.
- **An explicit tiering policy.** Not every record can get the treatment the ŠKZ
  got. Declare the tiers up front — `verbatim_with_provenance`, `published_
  translation_only`, `catalogue_record` — and let `ingest/fidelity.py` enforce
  them. Phase 1's `text_fidelity` classifier already has the vocabulary.
- **Track curation cost per record.** Kill trigger 3 depends on it: if record 60
  costs what record 12 cost, 200 is a staffing question rather than an
  engineering one.
- **The machine-translation path will fire.** Local non-English sources mostly
  will not have published English, so `resolve_english` will start choosing
  `machine` and the Part 6 confidence machinery goes from dormant to
  load-bearing. Expect the `verse` and `documentary` profiles (n=1) to need real
  calibration the moment they carry weight.

### Candidate spike — HTR on the two held-back records

The Palmyrene Tariff and Ezana Stone have been `pointer` records since Part 3,
not for want of sources but for want of an open *transcription*. That is Pillar 4
work with a concrete, already-identified job. **Flagged as a spike, not
committed** — it is the one place multimodal earns its way into Phase 2, and only
if W3 has capacity.

### Gate G3

**CLOSED AND FAILED, 2026-09-07, Block G.** The amended checklist in
`PHASE2_PLAN.md` is the authority and carries the same banner;
`BLOCK_G_RESULT.md` §2 carries the box table. The five points below are the
gate as originally written and are kept verbatim.

1. **60 records** ingested, all seven regions, curation cost per record recorded
   and **trending down**.
2. Full sweep re-run at 60: content pass rate **not lower** than at 24, and the
   ranking gold set still **≥95% top-6**.
3. `ui/build_ui_data.py --verify` clean — **zero `moved` or `absent` spans** —
   which is now meaningful because corpus version is recorded.
4. Confidence profiles that fire on real machine translations are recalibrated,
   with `calibrated` set honestly.
5. Only then, 200.

---

## W4 — Gold-set expansion

**Goal:** be able to state, with evidence, **what fraction of the variance is the
session and what fraction is the case.** That number is the deliverable — not a
pass rate.

Phase 1 ended unable to steer: with five questions, one unstable case *is* 20% of
the pass rate, and three repetitions inside one session measure a mode rather
than a distribution.

### Design decisions

- **5 → 30 questions**, stratified: ≥3 per region, ≥6 source languages, and
  balanced across three expected behaviours — **answerable**, **correctly
  refusable** (the Antikythera pattern), and **refusable-with-gloss** (the Vimose
  pattern, where a machine translation would be the worst possible output).
- **Every case declares its expected behaviour explicitly.** Phase 1 established
  that `expect_untranslatable` must be set deliberately and never inherited from
  a default; the same applies to expected refusal.
- **Keep the known failures in.** `aksum-exports` stays required. Dropping a case
  because the model had a bad session is how a floor is quietly lowered to
  whatever currently passes.
- **Repetitions must span sessions.** Three runs on one day is one observation.
  The harness should refuse to mark a floor `calibrated` from single-session data.

### Gate G4

1. **≥30 cases**, meeting the stratification above, each with an explicit
   expected behaviour.
2. Run 3× on **≥3 separate days**, and report **per-case stability and
   per-session stability as separate numbers**.
3. A stated variance decomposition — how much is session, how much is case — with
   the data behind it archived.
4. The floor is recalibrated from cross-session data and `calibrated` returns to
   `true`, **or** the reason it cannot is written down.

**If G4 fails, Phase 2 cannot be steered** and every later improvement is
unfalsifiable. That is kill trigger 2.

---

## Phase 2 exit gate

Another honest kill / pivot / persevere, on the brief's own model. The three kill
triggers set at the Phase 1 gate, restated as the questions this phase must
answer:

1. **Does ranking survive scale?** Known-good chunks in the top 6 at 450 chunks
   (G2), and still there at 60 real documents (G3).
2. **Can improvement be distinguished from noise?** A stated variance
   decomposition over ≥30 cases across ≥3 days (G4).
3. **Does curation get cheaper?** Cost per record trending down across the first
   tranche (G3).

Passing all three unblocks the brief's Phase 2 — the knowledge graph — with a
corpus deep enough for multi-hop questions to be found rather than staged.
Failing 1 makes the product corpus-bound and the honest move is to polish the
sourcebook at 24–60 records rather than chase 200.

---

## Cost model

| activity | embeddings | chat calls |
| --- | --- | --- |
| W1 geography | 0 | 0 |
| W2a baseline + W2b distractors | ~10 batched | 0 |
| W2c reranking evaluation | ~10 batched | 0 (reranker is not a chat model) |
| W3 re-embed at 60 records | ~5 batched | 0 |
| W4 sweep, 30 cases × 3 reps × 3 days | ~30 batched | **~270** |

**Retrieval work is nearly free; evaluation is where the money goes.** Voyage's
free tier is 3 requests/minute, so batch aggressively — the constraint has not
changed since Part 4. Budget the W4 sweeps deliberately and do not re-run them
casually.

---

## Standing lessons carried from Phase 1

- **A result is comparable only within the thing that produced it, and that thing
  must be recorded.** Five instances in Phase 1. Corpus version is the one still
  open, and W3 closes it.
- **A test that passes for the wrong reason is worse than one that fails.**
  Assert on the specific thing, never a proxy.
- **Instrument before tuning.** W2a exists because of this and must not be
  skipped once a promising reranker is in hand.
- **Place a threshold where no observed case straddles it**, then confirm with
  repetitions spanning sessions.
- **Run the thing against what it will actually receive.** A scorer tested only
  against archived payloads cost 30 chat calls.
- **When two prompt versions in a row fail to fix a behaviour, the problem is not
  in the prompt.**
- **Prefer a cheap check to a confident hypothesis.** Two Phase 1 hypotheses were
  refuted by one call each; neither would have yielded to more reasoning.
- **Resist building measurement apparatus in place of the deliverable.** Part 8
  became the most instrumented part in the repository and shipped an
  uncalibrated floor.
