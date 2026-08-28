# Mundus Ulterior — Phase 2 execution runbook

_Written 2026-08-12, from `PHASE2.md`, `PROGRESS.md` (closing summary), `README.md`
and `STARTUP.md`._

`PHASE2.md` is the **argument** — why these four workstreams, in this order, and
what each gate must prove. This file is the **runbook**: what to open on a given
evening, which command to type, what number to look at, and what to write down
before closing the window. It does not restate the reasoning; where a decision
here departs from `PHASE2.md`, the departure is named and justified.

**Planning assumption:** roughly three working sessions a week, one to three
hours each. W1 and W2 are therefore **serialised, not parallel** — see Deviation 1.
Calendar estimate: **9–11 weeks**, ~30 sessions.

---

## Before anything else — five actions that are yours alone

These are the items no amount of code can do for you. Everything else in this
file follows from them.

| # | Action | Why it blocks | Session |
| --- | --- | --- | --- |
| 1 | ~~**Reconcile the corpus counts.**~~ **DONE 2026-08-12.** Truth is **24 docs / 56 chunks / 54 eligible / 54 embedded**. `README.md` and `PHASE2.md` were right; **`STARTUP.md` was wrong** (57/55) and has been corrected. The W2b denominator of 54 stands. | The W2b distractor curve is *denominated in chunk counts* (54 → 150 → 450). A baseline recorded against an uncertain denominator is not a baseline. | 0 ✅ |
| 2 | **Decide the Pleiades sourcing rule and hold it.** Every `pleiades_id` is looked up and its JSON cached. **No id, from me or any model, is written from memory.** A remembered id is an authored coordinate wearing a citation. | W1's entire ethic, and gate G1.2. | Before A1 |
| 3 | **Choose the distractor sources yourself.** They must be *plausibly similar and known-irrelevant* — further public-domain Periplus sections, other classical geography, other museum catalogue prose. Candidate list in Block B; the judgement of "irrelevant" is a scholarly call, not a mechanical one. | If distractors are secretly relevant, the degradation curve is measuring the wrong thing and W3 gets a green light it did not earn. | Before B3 |
| 4 | **Book three separate calendar days for the W4 sweep, in advance.** ~270 chat calls, and the *days* are the scarce resource, not the calls. Three runs in one week is fine; three runs in one day is one observation. | G4.2, and kill trigger 2. Phase 1 failed exactly here. | Block E |
| 5 | **Write the 30 W4 cases yourself, or at least their expected behaviour.** The `answerable` / `correctly-refusable` / `refusable-with-gloss` label is a claim about the *material*, and `PROGRESS.md` established it must never be inherited from a default. | G4.1. A gold set someone else's judgement wrote is not a gold set you can be surprised by. | Block D |

---

## Two deviations from `PHASE2.md`, and the reasons

**Deviation 1 — W1 and W2 are serialised, W1 first.**
`PHASE2.md` runs them in parallel because they touch different code. At three
sessions a week, "parallel" means context-switching every session and finishing
neither. W1 goes first for three reasons: it needs **no gateway, no database and
no API spend**, so a session can start in thirty seconds; it is the workstream
whose scope is fully known today; and it produces the visible artefact (the map)
that makes the rest of the phase legible to anyone you show it to. W2's gate is
the one that blocks W3, but W3 is nine weeks out regardless.

**Deviation 2 — corpus-version recording moves from W3 to before the W4 sweep.**
`PHASE2.md` lists "record the corpus version in every answer" as *required before
the first tranche* of W3. Move it earlier. The W4 sweep is the single most
expensive artefact in the phase (~270 chat calls, three days, and the variance
decomposition that everything after it is steered by). If it runs without a
corpus hash in each answer, those 270 calls produce evidence with **the exact
defect that made the Adulis span unreadable in Part 9** — the fifth appearance of
the Phase 1 defect family, spent on the phase's most costly measurement. Cost of
moving it: one small schema change and one code change, done in Block D. Do not
skip this because it feels like W3's problem.

---

## The schedule at a glance

```
Block 0  reconcile state                  1 session   → true baseline numbers
Block A  W1 geography                     6 sessions  → G1
Block B  W2a baseline + W2b distractors   5 sessions  → the degradation curve
Block C  W2c hardening                    6 sessions  → G2   ◄── W3 gated here
Block D  W4 authoring + corpus version    4 sessions  (interleaved with B/C)
Block E  W4 sweep, 3 separate days        3 sessions  → G4
Block F  W3 tranche 24 → 60               8 sessions  → G3
Block G  Phase 2 exit gate                1 session   → kill / pivot / persevere
```

**The one hard ordering constraint:** Block E runs in the window *after* G2
passes and *before* Block F edits the corpus. That window is the only point in
the phase where retrieval and corpus are both frozen — which is what makes the
G4 numbers comparable against the G3 re-run at 60 records, per Gate G3.2.

---

## Standing session ritual

Paste at the top of every window (from `STARTUP.md`), twice — the gateway window
and the work window:

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
```

**Sessions in Block A need none of this** — no venv activation beyond the Python
call, no `.env`, no Docker, no gateway. That is the point of putting W1 first.

**Close every session by writing to `PROGRESS.md`**, even a bad session. Phase 1's
value is that it records what was believed at the time and how it turned out to
be wrong; a session that only records the outcome throws away the half that
mattered.

---

# Block 0 — Reconcile the state (1 session, no spend)

Nothing in Phase 2 is measured against a number you have not personally
confirmed.

```powershell
docker compose up -d db
python scripts\check_db.py              # pgvector installed: True

python -m ingest.run_ingest --stats     # docs / chunks / awaiting_embedding
python -m ingest.run_embed --stats      # embedded / pending / by_model
python -m answer.run_answer --stats

python -m answer.test_answer            # 133 assertions
python -m answer.test_translate         # 104 assertions
python -m ingest.test_embed
python -m ingest.test_chunker
python scripts\test_recover_baseline.py

python scripts\mutate_part7b.py         # 13 mutations, restores sources
python scripts\mutate_part8.py
python scripts\mutate_recover.py        # 11 mutations, restores sources

python ui\build_ui_data.py --verify     # 77 runs / 168 spans: 158 resolved, 9 case_only, 0 moved, 1 absent
node ui\check_ui.mjs
```

**Block 0 ran 2026-08-12 and found four defects. Recorded in `PROGRESS.md`; three
are fixed, one is yours.** Summary:

| Found | Status |
| --- | --- |
| **The repo was not under version control** — `.gitignore` but no `.git`, while three mutation scripts rewrite source files in place | `.gitignore` corrected (it would have excluded the entire 140K seed corpus); **`git init` is yours to run on the host** |
| `ingest/test_embed.py` crashed on a Part 6 import, **truncating the suite since 2026-08-10** and silently disabling both guards it is credited with | Fixed — import moved to module scope; 5 dead assertions now run and pass |
| All three `mutate_*.py` reported any suite failure as "sources were not restored cleanly" | Fixed — restore is now verified by content comparison, suite failure reported separately with its output |
| **An archived answer has no gold case:** `20260812T133627+0000-53afe41c` / *"What was exported from Adulis?"* — grounded, and the successful half of the discriminator the whole persevere verdict rests on | Open — **yours**, see Block D |

**Exit:** one line in `PROGRESS.md` stating the confirmed corpus state, the date,
and that all offline suites and all 35 mutation checks pass. ✅

---

# Block A — W1 Geography (6 sessions, zero spend)

**Goal:** every record placed, every placement carrying its own provenance.
**Gate:** G1 (all four criteria in `PHASE2.md`).

### A1 — Schema and the gazetteer client

Add two optional blocks per seed record. Proposed shape, matching the existing
citation style:

```json
"findspot_places": [
  {
    "name": "Adulis",
    "pleiades_id": "39274195",
    "uri": "https://pleiades.stoa.org/places/39274195",
    "ground": "identified",
    "ground_citation": "…the scholarly identification that makes the claim…",
    "contested": false,
    "note": ""
  }
],
"subject_places": [ … same shape … ]
```

Build `ingest/gazetteer.py`:

- reads `data/gazetteer.json`; on a miss, fetches
  `https://pleiades.stoa.org/places/<id>/json` **once**, caches name,
  representative point, bbox, licence and retrieval date, and never fetches again;
- exposes an offline-only mode so the build is reproducible with no network;
- **fails loudly on a coordinate with no id.** Not a warning — a non-zero exit.

**Your actions:** approve the field shape before 24 records are edited against it;
confirm the Pleiades licence line you want recorded (CC-BY, attribution string in
the bundle).

### A2–A4 — Place the records

Three sessions, roughly eight records each. Order them **17 findspot records
first** (mechanical: the record names the place, `ground: "stated"` or
`"identified"`), **7 literary records last** (the interesting ones: subject
geography, and the Periplus records will each carry many places).

Per record: resolve the id on Pleiades, paste the id and URI, choose the `ground`
honestly, and where `identified`, paste the citation that makes the identification.

**The list to keep in front of you:**

| Situation | Correct `ground` |
| --- | --- |
| The record's own text names the place | `stated` |
| A scholar identifies ancient with modern (Adulis ≈ Zula) | `identified` + citation |
| Only the region is known | `regional` — and the map is sparser, which is correct |
| **Muziris ≈ Pattanam** | `identified` + `contested: true` + both sides of the argument |

**Your actions:** this block is almost entirely yours. Two judgements recur —
whether an identification is settled or contested, and whether a literary text is
*about* a place or merely mentions it. Neither is delegable. Run
`python -m ingest.verify` after every record edited.

### A5 — UI: region view becomes place view

- points render from cached gazetteer coordinates only;
- `ground` is **shown**, not hidden — a `regional` placement must look different
  from a `stated` one;
- a contested identification renders as contested, not as a pin;
- trade texts render as **edges between subject places** — this is the
  ORBIS-shaped thing and the reason `subject_places` exists;
- every point clicks through: **map point → record → quotation → characters on disk**.

### A6 — Verification and G1

Extend `ui/build_ui_data.py --verify` to audit placements the way it audits quote
spans, then **mutation-verify it** the way Phase 1's guards were:

- introduce a hand-authored coordinate with no `pleiades_id` → build must fail;
- introduce an `identified` placement with no citation → build must fail;
- point a `pleiades_id` at a non-resolving id → build must fail.

Each verified to fail against the defect it guards. A guard never seen to fail is
not known to work.

**Gate G1 checklist:**

- [ ] 24/24 records carry at least `regional`; **≥17** carry a named place with a resolving `pleiades_id`
- [ ] **zero** coordinates not derived from a gazetteer id — asserted, and the assertion mutation-verified
- [ ] every `identified` placement carries a citation; ≥1 contested identification renders as contested
- [ ] map point → record → quotation → characters on disk, clickable, no dead link
- [ ] `node ui\check_ui.mjs` clean over all archived runs

**Spend for the whole of Block A: nothing.**

---

# Block B — W2a baseline and W2b distractors (5 sessions, ~10 batched embeddings)

**The rule that governs this block: record the baseline before touching
anything.** It is the only number that can later show the hardening worked.

### B1 — Build the ranking gold set (≥20 pairs)

Do **not** author these from scratch. Mine what Phase 1 already proved:

| Source | What to take |
| --- | --- |
| `eval/answer_runs/` (61 archived answers, 139 citations) | question → the chunk a citation *resolved to on disk*. Already verified by `cite.py`. The richest seam. |
| `eval/gold/retrieval_probes.json` (11 probes) | probe query → expected passage, with rationale attached |
| `eval/gold/translation_cases.json` (12 cases) | the chunk is known; write the question that should retrieve it |
| Named in `PHASE2.md` | the Adulis export chunk, the Muziris §56 pepper chunk, the Vimose transliteration chunk |

Store as `eval/gold/ranking_pairs.json`, loaded through the **existing strict
loader** (`eval/goldset.py`) so an unknown key is a load-time error. Do not write
a second loader.

Aim for ≥20, spread across regions and languages — a gold set that is 15 Greek
pairs measures Greek.

### B2 — Record the baseline

Build `eval/run_ranking_check.py` reporting, per pair and in aggregate:

- **recall@6** — is the known-good chunk in the top 6
- **MRR@10**
- **score gap** — known-good chunk minus *highest-ranked irrelevant* chunk

**The gap, not the raw similarity, is what predicts survival at scale.** Phase 1's
number to beat: mean top-1 to rank-6 spread of 0.105, and 0.045–0.094 on the
questions that matter.

All 20+ queries embed in **one batched request** (Voyage free tier: 3 req/min).
Archive to `eval/ranking_runs/<timestamp>.json`, never to a `_last_run.json` — a
one-case run once replaced a nine-case baseline and calibration was done from it.

**Your action:** paste the baseline table into `PROGRESS.md` *this session*,
before any hardening idea gets tried. Once a promising reranker is in hand the
temptation to skip backwards is real, and `PHASE2.md` names it.

### B3 — Curate distractors

Target ~400 chunks so the index reaches ~450 including the real corpus. Candidate
seams, all public domain or openly licensed:

- **further Periplus sections not in the corpus** — §1–3, §7–26, §30–52, §57–66
  (Greek Wikisource, ed. Müller, *GGM* I; the route Part 3b already used)
- **other classical geography** — Strabo, Ptolemy's *Geography*, Pliny *NH* VI
- **other museum catalogue prose** — object descriptions from collections with
  open data, chosen for stylistic similarity to the corpus's find records

**Your action (#3 above): you choose these.** Anything that could actually answer
a gold-set question is not a distractor, and a curve built on secretly-relevant
padding will wave W3 through.

### B4 — Load distractors, safely

The containment requirement is as strong as the Part 3 `eligible_for_retrieval`
one — build it the same way, **by construction rather than by filter**:

- a `is_distractor boolean NOT NULL DEFAULT false` column;
- `retrievable_chunks` stays distractor-free; a separate
  `retrievable_chunks_with_distractors` view is what the ranking check reads at
  elevated N;
- `ingest/verify`, `answer/run_answer`, `ui/build_ui_data.py` and every existing
  metric **cannot see them**;
- a test asserting a distractor chunk is unreachable from the answer path,
  mutation-verified.

Embed in **two or three large batched requests**, not four hundred small ones.

### B5 — Plot the curve

Re-run the ranking check at **54 → 150 → 450** chunks and record, per gold pair,
how rank and score gap move. State the **shape** of the curve in `PROGRESS.md` —
linear, cliff-edged, or flat — not just the endpoints.

This is the block's actual deliverable: it turns the central Phase 2 assumption
from an argument into a curve, before a single new record is curated.

**Decision point:**

- degradation **milder** than predicted → W3 can move faster, and say so
- degradation **as or worse than** predicted → W2c is load-bearing and W3 stays shut

---

# Block C — W2c hardening (6 sessions, ~10 batched embeddings) → **G2**

Do these in order; each is separately measurable against the B2 baseline.

### C1 — The two carried defects (do these first; they are cheap and they are debt)

1. **`cite.py`'s `locate_in_text`** records `match="exact"` after a case-folded
   fallback. Add a third state (`case_folded`), re-run `build_ui_data.py --verify`,
   and confirm the **six affected archived spans** re-classify. Regression guard,
   mutation-verified.
2. **Rename the trap.** `translation_chunk_id` is the *retrieved member*;
   `translation_chunk` is the *merged section*. The arithmetic is right, the names
   are a trap. Rename both, in the schema and every reader.

### C2 — Hybrid retrieval (lexical + dense)

Justified by the Aksum finding: the model answered when the question shared
wording with the passage, and lexical signal is exactly what dense-only retrieval
discards.

**The gotcha to plan for, not discover:** a lexical index over Literary Chinese
and Old Tamil is not the same problem as over English. Postgres `tsvector` with
an English configuration will stem Greek badly and will not tokenise Literary
Chinese at all — Chinese has no whitespace, and the corpus's two Chinese chunks
are 52 and 36 characters. Expect to need the `simple` configuration plus
**character n-grams for CJK**, and to decide per-script rather than globally.
Measure per-language recall, not just aggregate; an aggregate win that loses
Chinese is a loss.

Fuse with a stated method (RRF is the cheap default) and **re-measure against B2's
baseline on the same pairs.**

### C3 — Cross-encoder reranking

Over the fused candidate set. Two paths — establish which before designing around
it:

- a **hosted reranker through the existing gateway** (your Voyage key may already
  cover a rerank endpoint; confirm LiteLLM support and free-tier terms before
  assuming it);
- a **local cross-encoder**, remembering this venv is **Python 3.14 (cp314)** and
  `torch`/`sentence-transformers` wheels lag new CPython releases — the same
  dependency trap that cost a day in Part 4.

Reranking is not a chat model, so this costs no chat calls.

### C4 — Re-examine the fold

`align._merge` presents a whole section when only one member was retrieved. Phase
1 **proved this is not what breaks Aksum**, so this is a ranking-quality question
and not a bug fix. Measure both arms on the gold set: does surfacing the retrieved
member score better than the merged section? Answer with the number, then move on
— this is the item most likely to absorb a week for a null result.

### C5–C6 — Measure across two sessions on different days

**Gate G2 checklist:**

- [ ] ranking metric exists over ≥20 pairs, **baseline recorded before any change**
- [ ] distractor curve plotted to ≥450 chunks, its **shape stated** in `PROGRESS.md`
- [ ] known-good chunk in **top 6 for ≥95%** of pairs **at 450 chunks including distractors** — not at 54
- [ ] score gap **wider than baseline**, same pairs
- [ ] measured across **≥2 sessions on different days**
- [ ] `cite.py` third match state landed and mutation-verified
- [ ] `translation_chunk*` rename landed

**If G2 fails, W3 does not start.** That is kill trigger 1, and the honest move is
to polish the sourcebook at 24–60 records rather than chase 200.

---

# Block D — W4 authoring and corpus version (4 sessions, interleaved with B and C)

Offline work that fills the gaps between B and C sessions. None of it spends an
API call.

### D1 — Corpus version in every answer (Deviation 2)

A content hash of each seed record at answer time, stored beside `prompt_version`.
Then: an archived citation can be told from a stale one without re-checking the
whole corpus, and `build_ui_data.py --verify` can distinguish *"this span broke"*
from *"this span was made against a different corpus"*.

- hash each seed record on load; store the set (or a Merkle-ish roll-up plus the
  per-record hashes for the records actually cited) in the `answers` row and in
  the `eval/answer_runs/` archive;
- `build_ui_data.py` reports spans against **the corpus version that made them**;
- the Part 9 `1 absent` span should become explicable rather than merely absent.

### D2–D3 — Write the 30 W4 cases

**5 → 30, stratified:** ≥3 per region (7 regions = 21 minimum), ≥6 source
languages, and balanced across three expected behaviours:

| Expected behaviour | Pattern | What a failure means |
| --- | --- | --- |
| **answerable** | the corpus holds it and the model should find it | retrieval or assembly failure |
| **correctly refusable** | the Antikythera pattern — not in the corpus | the model invented something |
| **refusable-with-gloss** | the Vimose pattern — present but untranslatable; show source + published gloss | a machine translation appeared, which is the **worst possible output**, because it arrives attached to a citation |

Rules, carried from Phase 1 and non-negotiable:

- **every case declares its expected behaviour explicitly.** The loader must
  refuse to inherit it from a default, exactly as `expect_untranslatable` already
  works.
- **keep the known failures in.** `aksum-exports` stays required. Dropping a case
  because the model had a bad session is how a floor gets quietly lowered to
  whatever currently passes.
- prefer `expect_quoted_docs` over `expect_cited_docs`. The first proves the model
  *used* a source; the second only proves it *named* one.

**Start with the case Block 0 found missing.** `eval/gold/answer_cases.json` holds
`aksum-exports` — *"What did Rome trade with the Kingdom of Aksum?"* — the
question the system **refused**. It does not hold *"What was exported from
Adulis?"*, the rewording that **worked**, which sits unscored in
`eval/answer_runs/20260812T133627+0000-53afe41c.json` with `grounded: true` and a
verbatim Periplus quotation.

Those two questions are the Adulis discriminator, and the discriminator is the
entire argument for the persevere verdict: *the system refused a question whose
answer it was holding, and answered correctly when the question was reworded
against byte-identical evidence.* **Only the failing half is in the gold set.**
`eval.test_answer_eval` has been failing two assertions about this since the exit
gate, and the message was routed through a mutation script that mislabelled it.

Add the case as `adulis-exports`, expected behaviour **answerable**, paired
explicitly with `aksum-exports` so the two are read together. Until it exists,
the phase's founding claim is an anecdote rather than a regression test.

**Your action (#5): write these, or at minimum own every expected-behaviour label.**

### D4 — Teach the harness about sessions, then pilot

- record a **session identity** (run date at minimum) in every sweep archive;
- make floor calibration **refuse to set `calibrated: true`** when distinct dates
  < 3 — and mutation-verify that refusal;
- report **per-case stability and per-session stability as separate numbers**;
- **pilot on 5 cases across 2 days (~30 chat calls)** so the real 3-day sweep is
  not the first time this code runs across a date boundary.

That pilot is cheap insurance on a 270-call artefact.

---

# Block E — The W4 sweep (3 sessions, 3 separate days) → **G4**

Runs in the window after G2 passes and before Block F touches the corpus.
Retrieval frozen, corpus frozen, corpus hash recorded. Nothing else in the phase
gives you a system this stable to measure.

Per day: **30 cases × 3 repetitions ≈ 90 chat calls**, plus ~10 batched
embeddings. Three days: **~270 chat calls.**

```powershell
python -m eval.run_answer_sweep --dry-run                        # embeddings only, no chat
python -m eval.run_answer_sweep --repeat 3                       # ~90 chat calls
python -m eval.rescore_sweep                                     # no API calls
```

Between days: **change nothing.** A prompt tweak on day two turns three
observations into one.

**Gate G4 checklist:**

- [ ] ≥30 cases meeting the stratification, each with an explicit expected behaviour
- [ ] run 3× on **≥3 separate days**
- [ ] **per-case stability and per-session stability reported as separate numbers**
- [ ] a stated **variance decomposition** — how much is session, how much is case — with the data archived
- [ ] the floor recalibrated from cross-session data and `calibrated: true`, **or** the reason it cannot be written down

**The deliverable is the variance decomposition, not the pass rate.** If G4 fails,
Phase 2 cannot be steered and every later improvement is unfalsifiable — kill
trigger 2.

---

# Block F — W3, corpus 24 → 60 (8 sessions) → **G3**

Only after G2 and G4. **Depth, not breadth** — all seven regions already exist;
deepen them rather than add. Target ~30 records per region at 200, so 60 is
roughly 8–9 per region.

### F1 — Declare the tiering policy before curating anything

Not every record can get the treatment the ŠKZ got. Write the tiers down first
and let `ingest/fidelity.py` enforce them — the `text_fidelity` classifier already
has the vocabulary:

| Tier | What it means | Roughly |
| --- | --- | --- |
| `verbatim_with_provenance` | original text, published translation, both cited | the ŠKZ / Periplus treatment |
| `published_translation_only` | no open original transcription available | |
| `catalogue_record` | find/coin record, object description, no source-language text | the 8 records with `reference_translation: null` |

**Your action:** set the target mix across the 36 new records now, so the tranche
is not accidentally all catalogue records.

### F2 — Track curation cost per record from record 25

Minutes per record, in a column, from the first new record. **Kill trigger 3
depends on it:** if record 60 costs what record 12 cost, 200 is a staffing
question rather than an engineering one, and that is a finding worth having.

### F3–F7 — Curate in sub-tranches of ~9, re-running the sweep at each

After each sub-tranche:

```powershell
python -m ingest.verify
python -m ingest.run_ingest
python -m ingest.run_embed              # only the new/changed chunks
python -m eval.run_ranking_check        # must hold ≥95% top-6
python ui\build_ui_data.py --verify     # zero moved, zero absent
```

**Expect the machine-translation path to fire.** Local non-English sources mostly
will not have published English, so `resolve_english` starts choosing `machine`
and the Part 6 confidence machinery goes from dormant to load-bearing. The
`verse` and `documentary` profiles are at **n=1** and will need real calibration
the moment they carry weight — budget a session for it and set `calibrated`
honestly.

### F8 — Candidate spike: HTR on the two held-back records

Palmyrene Tariff and Ezana Stone have been `pointer` records since Part 3, not for
want of sources but for want of an open **transcription**. **Flagged as a spike,
not committed** — attempt it only if F1–F7 came in under budget. The classifier
will promote them automatically if the text ever lands, with no code changes.

**Gate G3 checklist:**

*AMENDED 2026-08-28, before F1, as Block F decision 1 — recorded in advance
because a gate amended at the end is a gate fitted to its result. Ruling 39
carries the full text; `F0_RULINGS.md` is the authority. The two new boxes are
the two numbers that SAW day 3, and the box they sit beside is the one that
did not.*

- [ ] **60 records** ingested, all seven regions
- [ ] curation cost per record recorded and **trending down**
- [ ] full sweep re-run at 60: content pass rate **not lower** than at 24
- [ ] **per-session stability at 60, reported beside the pass rate** — not as a
      threshold, as the number the pass rate cannot see. FINDING 26: four
      sessions returned `content_pass_rate` 0.727272… to every digit printed
      while two cases reversed and cancelled. A pass rate that reads the same
      on a day the system behaved differently is a box that ticks itself.
- [ ] **cross-session answer-text agreement at 60**, computed over **Block F's
      own sessions at 60** and reported beside Block E's 74–77% / 45%, which are
      **context and not a threshold**. The Block E figures were generated over
      24 records: at 60 the evidence blocks differ by construction, so the text
      differs by construction, and a gate comparing across the two corpora
      would be measuring the corpus move it was meant to survive.
- [ ] ranking gold set still **≥95% top-6**
- [ ] `ui/build_ui_data.py --verify` clean — **zero `moved` or `absent`** (now meaningful, because corpus version is recorded)
- [ ] confidence profiles that fire on real machine translations recalibrated, `calibrated` set honestly
- [ ] only then, 200

**What the amendment COSTS, stated with it.** Both new boxes need at least
**two sessions at 60 records on two distinct UTC dates** — cross-session
agreement has no meaning inside a single sweep, and per-session stability
inside one sweep reads NOT MEASURED and says so. G3 as originally written
needed one sweep at 60. It now needs two, ~198 chat calls, and **two booked
days at the end of Block F**. Booked in advance for the reason item 4 of
*Before anything else* gives: the days are the scarce resource, and a block
that discovers on its last afternoon that it owes a second date has already
failed the gate it was trying to pass.

---

# Block G — Phase 2 exit gate (1 session)

Another honest kill / pivot / persevere, answering the three questions the phase
was built to answer:

1. **Does ranking survive scale?** Top-6 at 450 chunks (G2), still there at 60 real documents (G3).
2. **Can improvement be distinguished from noise?** A stated variance decomposition over ≥30 cases across ≥3 days (G4).
3. **Does curation get cheaper?** Cost per record trending down across the first tranche (G3).

Passing all three unblocks the brief's Phase 2 — the **knowledge graph** — with a
corpus deep enough for multi-hop questions to be *found* rather than staged.
Failing 1 makes the product corpus-bound, and the honest move is to polish the
sourcebook at 24–60 records rather than chase 200.

Write the closing summary at the foot of `PROGRESS.md` in the Phase 1 style: what
was proven, what was **not** proven, the one number that should worry the reader,
and the debt table pointing each open item at the workstream that owns it.

---

## Cost ledger

| Block | Embeddings | Chat calls |
| --- | --- | --- |
| 0 reconcile | 0 | 0 |
| A geography | **0** | **0** |
| B baseline + distractors | ~10 batched | 0 |
| C hardening | ~10 batched | 0 (a reranker is not a chat model) |
| D authoring + pilot | ~2 batched | ~30 (pilot only) |
| E W4 sweep | ~30 batched | **~270** |
| F corpus to 60 | ~5 batched | sweep re-run at 60 |
| **Retrieval work is nearly free; evaluation is where the money goes.** | | |

Voyage free tier is **3 requests/minute** — batch aggressively; the full embedding
pass is 2 requests. Anthropic chat is a different tier and does not compete.
**Budget the W4 sweeps deliberately and do not re-run them casually.**

---

## The standing lessons, kept where you will see them

- A result is comparable only within the thing that produced it, **and that thing
  must be recorded.** Five instances in Phase 1; corpus version is the one still
  open, and Block D closes it.
- **A test that passes for the wrong reason is worse than one that fails.** Assert
  on the specific thing, never a proxy.
- **Instrument before tuning.** Block B exists because of this and must not be
  skipped once a promising reranker is in hand.
- **Place a threshold where no observed case straddles it**, then confirm with
  repetitions spanning sessions.
- **Run the thing against what it will actually receive.** A scorer tested only
  against archived payloads cost 30 chat calls.
- When **two prompt versions in a row** fail to fix a behaviour, the problem is
  not in the prompt.
- **Prefer a cheap check to a confident hypothesis.** Two Phase 1 hypotheses were
  refuted by one call each; neither would have yielded to more reasoning.
- **Resist building measurement apparatus in place of the deliverable.** Part 8
  became the most instrumented part in the repository and shipped an uncalibrated
  floor. Block A is the antidote: ship the map.
- **Mutation-verify every guard.** A guard that has never been seen to fail is not
  known to work.
- **Archive runs, not verdicts.** It has paid for itself three times, once in money.
