# UI START — **CLICK-THROUGH CITATION AND THE MAP. NOT THE CHATBOT, AND NOT THE
# PROMPT.**

*Written 2026-09-07 at the close of W3, for the thread that opens the UI block.
**Nothing here was measured by the UI block; it is a scope and a set of
constraints**, assembled from `BLOCK_G_RESULT.md`, `W3_RESULT.md` and the state
of `ui/` on disk. Every figure is transcribed from those. The first thing the UI
session does is confirm the state block still reproduces — if it does not, stop
and find out what moved.*

---

# 1. WHERE THE PROJECT IS

**Phase 2 exited on a PIVOT.** Q1 no, Q2 yes about a corpus that no longer
exists, Q3 no. G3 is closed and failed on nine boxes. **200 records is off the
table** and a session that wants it back is re-opening that verdict.

**W3 closed debt row 1** — FINDINGS 82 and 86, the inference-where-a-declaration-
belongs defect — and moved the corpus digest doing it:

```
26e4a683...  24 records   the digest floor.json is still pinned to, deliberately
0e784505...  54 records   what is on disk now
```

**The sequencing was decided before the Block G verdict was written and the UI
did not win it by argument.** `PHASE2_PLAN.md` conditioned the knowledge graph on
passing all three questions; the graph was deprioritised on separate grounds
beforehand, and the UI is next regardless of what Block G concluded. A reader who
finds the UI immediately after a pivot verdict will otherwise infer a causal link
that was not there.

---

# 2. WHAT ALREADY EXISTS, AND IT IS MORE THAN "NOTHING"

**`ui/index.html` is 82KB of static page, last touched 2026-08-14.** It has an
inline SVG map — no Leaflet, no tile server, no network at all — and sections for
questions asked, the sources an answer was given, provenance, and place.

**It is stale in a way that matters:** its own heading reads *"All 24 records, by
region"* and the corpus is 54. **This block is a rebuild, not a build**, and the
first honest act is to read what is there before replacing it.

**`ui/data.js` is 9.5MB and CURRENT** — regenerated 2026-09-07, after W3. It
already carries everything this block needs:

```
runs          685    with passages, grounding, sources_block, prompt_version,
                     corpus_version and the per-span citations
corpus         54    every record
places               docs, edges, groups, stats, declared_unplaceable, uncached
coastline            polygons, with its source, scale and simplify tolerance
gold                 answer_cases, confidence_profiles, floor
span_audit           resolved 1227, case_folded 50, case_only 9,
                     whitespace_only 1, moved 1, absent 1
```

**`build_ui_data.py --verify` is the instrument this block reads**, and
`node ui/check_ui.mjs` is its gate. `check_ui` refuses to report a single count
while `data.js` is behind the corpus — it went RED during W3 for exactly that
reason and the fix was `python ui/build_ui_data.py`, not an argument.

---

# 3. SCOPE — DECIDED AT W3's CLOSE, AND NARROWER THAN THE SEQUENCING SENTENCE

`BLOCK_G_RESULT.md` names three things: chatbot, map, click-through citation.
**This block takes two.**

```
IN     click-through citation
       the map rebuild, at 54 records

OUT    the chatbot -- a later block, and see section 4
OUT    any change to p7-answer-v2r -- section 5
```

**Why the split, and it is not timidity.** Both things that are IN run entirely
off `ui/data.js`: no prompt, no gateway, no server, no keys, no cost per visitor.
The block is offline and reversible. And it settles **what a citation has to LOOK
like before the prompt is rewritten to produce it** — which is the only order in
which the prompt gets written once.

---

# 4. THE ONE RULING THIS BLOCK OWES AND MUST NOT BUILD PAST

**Does the chatbot answer LIVE at request time, or REPLAY the archived runs?**

**Decide it in this block. Build neither.** It is a product decision with a
security and cost tail, and it must not be made by whoever is halfway through a
build with a deadline in front of them.

```
LIVE     the honest demonstration of the capability, and what "functional web
         portal" most naturally means. Needs a hosted backend, key handling,
         rate limiting, and it puts an answer in front of a visitor that no
         instrument in this repository has scored -- at the moment they read it

REPLAY   static, free, deployable anywhere, and every answer shown has already
         passed the floor and the span audit. Reads as a demo rather than a
         system to anyone who types a question of their own
```

**What makes this hard is not the engineering.** This project's whole claim is
that every quotation resolves to characters on disk. A live answer is the one
artefact on the page that has not been checked when it is displayed. **If LIVE
wins, the ruling has to say what is shown to a visitor about an answer nobody has
evaluated** — and "nothing" is an answer that would not survive being written
down.

---

# 5. THE FREEZE, AND WHY THE PROMPT IS OUT OF SCOPE

**`p7-answer-v2r` is frozen and stays frozen through this block.** Its rule 3
permits a quotation from the source text *or* from the English shown for that
source, and requires neither — FINDING 13, and the reason the answer path quotes
translations. **Click-through citation will want that changed. Not here.**

Three things travel with that change whenever it is made, and they are recorded
here because the session that makes it will not otherwise know them:

- **every archived answer number becomes historical;**
- **`p7-answer-v2r` stays in `ANSWER_PROMPTS` beside v3**, rather than being
  edited in place — already this file's pattern;
- **the floor is denominated PER PROMPT VERSION by construction.** `floor.json`
  keys its verdicts on the prompt version, so **v3 starts with no calibrated
  floor at all**, and earning one costs three sessions on three distinct UTC
  dates and ~270 chat calls.

**And the corpus has ALREADY moved.** W3 superseded the digest, so a corpus
recalibration is owed regardless. `BLOCK_G_RESULT.md` §6: **if the prompt and the
corpus are both to move, move them together and recalibrate ONCE.** Two separate
recalibrations is the same money twice, and after W3 that is no longer
hypothetical.

**`chat-default` (haiku-4-5, temperature 0, ruling 22) stays frozen indefinitely.**
A model swap on that alias is a re-baseline of the whole archive, not a
configuration change.

---

# 6. THE DEBT ROWS THIS BLOCK MAKES DUE

From `BLOCK_G_RESULT.md` §7. **Three rows stop being "after the UI" the moment
the UI is the thing being built:**

```
row 7   A DIFFABLE MANIFEST BESIDE ui/data.js (FINDING 74). data.js is 9.5MB of
        generated JSON on one line. Nothing can review a change to it, and this
        block regenerates it repeatedly. OWNED BY THIS BLOCK

row 10  git log --follow on africa-03-periplus-adulis -- two chunk ids that
        still do not name their passage. THIS ONE RECORD IS THE WHOLE OF G3
        BOX 8's FAILURE, moved 1 and absent 1, and it is the record whose
        citation the UI will render BROKEN. Read it before designing the
        broken-citation state, not after

row 9   a Swedish GeoNames dump and a Thai one. Closes both Scandinavian
        placements and seasia-08-pong-tuk-lamp's -- THREE COORDINATES A SOURCE
        HANDED OVER AND THIS CORPUS REFUSED. The map is the reason they matter
```

**Row 2 is not due and must not be touched.** Q1's replacement retrieval measure
is owed **before the next record-adding run, never after**. This block adds no
records, so it stays open with no date — and if anything later makes it due, it
is paid before the run and not chosen after seeing one.

---

# 7. WHAT THE UI SESSION WILL SEE AND MUST NOT READ AS BREAKAGE

**`build_ui_data.py --verify` reports on TWO AXES and W3 moved the second one for
every span at once.**

```
FIRST AXIS   does the archived quote still sit at its recorded offset
             resolved 1227, case_folded 50, case_only 9, whitespace_only 1,
             moved 1, absent 1
             -- moved 1 / absent 1 are BOTH africa-03-periplus-adulis, and that
                is G3 box 8, failing exactly as it failed

SECOND AXIS  has the record moved underneath the span
             unchanged 0, changed 1121, UNKNOWN 168
             -- EVERY recorded span reads "changed" because W3 added two keys to
                all 54 records, so every content_hash moved in one commit. This
                was PREDICTED in W3_START.md before the fix existed, precisely
                so a later reader would not meet it cold. IT IS NOT A DEFECT
             -- the 168 UNKNOWN predate the corpus version and CANNOT say
```

**A UI session that reads `changed 1121` as corpus drift will go looking for a
break that is not there.** That is what this section exists to prevent.

---

# 8. THE OPERATING CONSTRAINTS, ALL OF WHICH BIT SOMEBODY

- **Git runs in PowerShell ON THE HOST, never through the bridge.** A bridge
  `git status` leaves a `.git/index.lock` **the bridge cannot delete** —
  `rm` on a mounted file returns `Operation not permitted` — so a bridge session
  that trips it has to interrupt the user. FINDING 94. `git rev-parse` and
  `git log` are lock-free and safe.
- **A fresh bridge VM has neither `psycopg` nor `sqlglot`**, and without them
  `scripts/state_block.py` reads `scripts/test_recover_baseline.py` as **RED**
  and `answer.test_answer` as **149**. Neither is about the repository. Run
  `pip install "psycopg[binary]" sqlglot` first. FINDING 94, and the RED half is
  the dangerous one because 149 announces itself as a skip and RED does not.
- **Mutation harnesses are HOST ONLY** (FINDING 59), in PowerShell. A call killed
  at 45 seconds leaves a live mutation in the tree. Never two over one working
  tree at once.
- **Check `git diff --stat` after any harness run.** A file whose every line
  changed is the line-ending defect, not your edit. `.gitattributes` is `* -text`
  and it is load-bearing: 168 archived citation spans point into the corpus by
  exact offset.
- **The bridge cannot reach Postgres.** `postgresql://mundus:mundus@localhost:5432/mundus`
  is host-only, so anything touching the index is a host runbook.
- **`ui/data.js` is generated.** Never hand-edit it; `python ui/build_ui_data.py`
  is how it moves, and `check_ui.mjs` refuses to count anything while it is stale.

---

# 9. FIRST FIVE MINUTES

1. `pip install "psycopg[binary]" sqlglot` on the bridge, then
   `python -m ingest.verify --state` and `python scripts/state_block.py`.
   **Confirm they reproduce what `W3_RESULT.md` recorded** — 54 documents, 170
   chunks, `ingest.test_fidelity` at 145, eleven instruments green, and
   `'mul': 3` with no `'arc'` in the per-language line. If not, stop.
2. Read `W3_RESULT.md` §7 — the two verify axes — before running
   `build_ui_data.py --verify`, or `changed 1121` will look like a fire.
3. **Read `ui/index.html` whole.** It is 82KB and it is the thing being replaced.
   A rebuild that has not read what it is rebuilding is a rewrite.
4. Read `BLOCK_G_RESULT.md` §6 (the freeze) and §7 rows 7, 9 and 10.
5. **Write the predictions and commit them BEFORE any code**, ruling 78's
   practice. At minimum: what `check_ui.mjs` and `build_ui_data.py --verify`
   will read after the rebuild, and which of the 54 records will render with a
   broken citation. **`africa-03-periplus-adulis` is the known one — a prediction
   that names only it is a prediction worth being wrong about.**

---

# 10. WHAT THIS BLOCK MUST NOT DO

- **Not curate a record.** The corpus is 54 and stays 54.
- **Not touch `p7-answer-v2r`, or `chat-default`.** §5.
- **Not re-point `floor.json`'s digest pin.** Ruling 82. The pin names
  `26e4a683…` on purpose and `superseded_by` records why.
- **Not build the chatbot.** §4 rules on it; a later block builds it.
- **Not empty `MODERN_INSTITUTIONAL_PROSE_PENDING_RULING`.** The §8 question —
  modern non-English institutional prose against ancient source-language text —
  is ruled on AFTER the UI, and the loader refusal is what makes sure the next
  session cannot skip it. The UI curates nothing, so it cannot trip it.
- **Not amend G3.** It is closed and failed. A gate is not re-opened by a run
  taken after it closed, by a session that knows the result.
- **Not assign ruling or finding numbers from this document.** `RULINGS.md` is
  the authority and the next free number is read from it at the time. **As of
  2026-09-07 the next free ruling is 83 and the next free finding is 98** — and
  `RULINGS.md`'s index does not cover 53 to 79, for the reason written under its
  table.
