# Mundus Ulterior

A grounded cross-lingual sourcebook. An English question retrieves primary
sources in Koine Greek, Literary Chinese, Old Tamil, Parthian, Nabataean
Aramaic, Sabaic and Proto-Norse, and answers in English where **every quotation
resolves to an absolute character range in a named field of a named file.**

**Phase 1 is complete (2026-08-12). Exit-gate verdict: persevere.**
24 documents → 56 chunks → 54 embedded. Retrieval 11/11 probes at rank 1.
Translation 12/12 gold cases. 132 of 139 archived citations still resolve to
characters on disk.

### Where to start

| You want | Read |
| --- | --- |
| What happens next | **`PHASE2.md`** — the plan, four workstreams, gates |
| How to run anything | **`STARTUP.md`** — per-session setup, commands, costs |
| What was built and why | **`PROGRESS.md`** — closing summary at the foot; the rest is a searchable log, not required reading |
| To just look at it | `ui/index.html` — opens in a browser, no server |

`../mundus-ulterior-phase1-part1-setup.md` holds the full Part 1 environment
walkthrough including gotchas and fixes.

## Layout
- `ingest/` — fetch + chunk + embed the seed corpus
- `retrieve/` — vector search over pgvector
- `answer/` — translation, back-translation confidence, grounded answer assembly
- `eval/` — eval harness plus the declarative gold set in `eval/gold/` (retrieval
  probes, confidence profiles, translation cases — data, not code)
- `ui/` — thin front end
- `data/` — seed corpus (large blobs git-ignored)
- `gateway/` — LiteLLM proxy config
- `scripts/` — setup, schema SQL, mutation testing, baseline recovery

## Module map

41 Python files, ~13,000 lines. One line each, in the order data flows through
them. Test suites are listed with what they actually guard, because several
exist to hold a specific past defect down.

**Ingestion — `ingest/`**

| Module | Role |
| --- | --- |
| `loader.py` | Seed JSON → `Document` + `Chunk` records; assigns `parallel_group` at document level |
| `chunker.py` | Meaning-aware splitting (`§` → paragraph → line → sentence), never a fixed window; exact character spans |
| `fidelity.py` | Classifies how faithful a text is to its primary source; sets `eligible_for_retrieval` |
| `db.py` | Idempotent upsert + prune; clears all four embedding columns together when text changes |
| `embed.py` | Gateway-routed embeddings: batching, bounded retry, dimension validation, `input_type` document/query |
| `run_ingest.py` / `run_embed.py` | CLIs — `--dry-run`, `--stats`, `--limit`, `--force` |
| `verify.py` | Corpus integrity; asserts `source_text[start:end] == chunk.text`; audits W1 placements |
| `places.py` | Strict loader for `findspot_places` / `subject_places`; unknown keys, empty strings and empty blocks are load-time errors. Shape spec: `data/seed_corpus/PLACES.md` |
| `gazetteer.py` | The only module that turns a `pleiades_id` into a coordinate. Offline by default, reading a **dated** cached snapshot; `--inspect`, `--refresh`, `--check`, `--stats`, `--record-licence`, `--probe` |
| `test_chunker.py` | Splitting + offset round-trip |
| `test_sql.py` | SQL ↔ dataclass alignment, CHECK coverage |
| `test_embed.py` | 26 assertions; guards the missing `::text[]` cast and the doc-id-proxy probe bug. **Four function-scope imports remain** — the truncation defect's class is unfixed, W2 owns it |
| `test_places.py` | 46 assertions; every guard mutation-verified by `scripts/mutate_places.py` |

**Retrieval — `retrieve/`**

| Module | Role |
| --- | --- |
| `search.py` | Cosine KNN over the `retrievable_chunks` view, with language/region/role filters |
| `crosslingual_check.py` | Runs the 11 probes; probes themselves live in `eval/gold/`, not here |

**Answering — `answer/`**

| Module | Role |
| --- | --- |
| `translate.py` | Forward and back translation; the back prompt provably never sees the original |
| `confidence.py` | chrF + cosine, genre bands, blocking flags (`untranslated_echo`, `script_mismatch`) |
| `align.py` | Pairs an original with the right passage of its published translation, and states the evidence (`section` / `index` / `none`) |
| `evidence.py` | `Passage` — the unit shown to the model, with its English, band, flags and offsets |
| `assemble.py` | `fold_hits` (collapses translation hits into their originals), evidence block, prompt versions, the chat call |
| `cite.py` | **The core of the claim.** Resolves every quotation to characters on disk; 796 lines |
| `store.py` / `answer_store.py` | `chunk_translations` and `answers` tables, with provenance in the primary key |
| `run_answer.py` | The entrypoint — `--json`, `--dry-run`, `--repeat`, `--prompt-version` |
| `test_translate.py` | 104 assertions; guards prompt leakage, echo detection, chrF whitespace sensitivity |
| `test_answer.py` | 133 assertions; guards quote resolution and the grounding checks |

**Evaluation — `eval/`**

| Module | Role |
| --- | --- |
| `goldset.py` | Strict loader — **rejects unknown keys**, so a misspelled field cannot silently disable an assertion |
| `gold/*.json` | Retrieval probes, confidence profiles, translation cases, answer cases, floor — data, not code |
| `answer_eval.py` | Scores an answer against its case; separates *cited* from *quoted* |
| `run_answer_sweep.py` | Sweeps cases × prompt versions × repetitions; archives to `eval/sweeps/` |
| `rescore_sweep.py` | Re-scores archived runs with no API calls |
| `run_translation_check.py` | The Part 6 loop: translate → back-translate → score → record |
| `test_answer_eval.py` | 70 assertions on the scorer itself |

**UI — `ui/`**

| Module | Role |
| --- | --- |
| `build_ui_data.py` | Joins archived runs to the seed corpus, classifies every span (`resolved` / `case_only` / `moved` / `absent`), writes `data.js` |
| `index.html` | The whole UI — three views, no server, no build step, no CDN |
| `check_ui.mjs` | Runs the page's own render functions over all 61 archived runs in `node:vm` |

**Scripts — `scripts/`**

| Module | Role |
| --- | --- |
| `schema-part{3,4,6,7}.sql` | Idempotent schema, applied by the runners |
| `recover_answer_baseline.py` | Reconstructs archived answers from the database |
| `test_recover_baseline.py` | 45 assertions on that reconstruction |
| `check_db.py` / `hello.py` | Part 1 milestones — pgvector present, gateway answering |
| `mutate_part7b.py` / `mutate_part8.py` / `mutate_recover.py` | **Mutation testing** — 35 deliberate defects, each verified to break the guard meant to catch it |
| `mutate_places.py` | **Mutation testing, W1** — 14 deliberate defects; the first four are Gate G1 criterion 2 in code |

### Two names that are traps

- `translation_chunk_id` is the **retrieved member**; `translation_chunk` is the
  **merged section**. The citation arithmetic uses the record and is correct;
  the names are not. Renaming is a Phase 2 W2 item.
- `cite.py`'s `locate_in_text` falls back to a case-folded search and still
  records `match="exact"`. Six archived spans are affected. Also W2.

## Stack (as built)
- Python venv, `fastapi` pinned to `0.115.5` (LiteLLM proxy compatibility)
- Postgres 16 + pgvector via Docker (extension auto-enabled on first boot)
- LiteLLM gateway → Anthropic Claude (chat) + Voyage `voyage-3.5` (embeddings, 1024-dim)

## Quickstart (Windows / PowerShell)
```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"

# 1. venv + deps
python -m venv .venv
.venv\Scripts\Activate.ps1                 # if blocked: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
python -m pip install --upgrade pip
pip install -r requirements.txt

# 2. secrets — copy, then put REAL keys in .env (key lines: no inline comments / trailing spaces)
copy .env.example .env
notepad .env
# load .env into this window (PowerShell doesn't do it automatically):
Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}

# 3. database (Docker Desktop must be running; pgvector auto-enabled via scripts/init-db.sql)
docker compose up -d db
python scripts\check_db.py                  # expects: pgvector installed: True

# 4. gateway — leave running in its own window (reads keys from THIS window's env)
litellm --config gateway/config.yaml --port 4000

# 5. milestone — in a SECOND window (re-activate venv + reload .env there first)
python scripts\hello.py                     # prints a Claude chat reply + embedding dims = 1024
```

**Notes**
- The app DB variable is `APP_DATABASE_URL`, not `DATABASE_URL` (which LiteLLM reserves for its own Prisma DB).
- If you change a key in `.env`, **restart the gateway** — it only reads keys at startup.
- Activation + env loading are per-window; do both in every new PowerShell window.

**Part 1 is done when** `check_db.py` prints `pgvector installed: True` and
`hello.py` prints a chat reply plus an embedding vector length — both confirmed.

Part 2 (seed corpus, 24 docs across all 7 regions) is complete — see `data/seed_corpus/`.

## Part 3 — ingestion & chunking

Code complete and verified offline; the Postgres load is run on the host.

```powershell
python -m ingest.test_chunker    # splitting + exact-offset round-trip tests
python -m ingest.test_sql        # SQL <-> dataclass alignment, CHECK coverage
python -m ingest.test_places     # place-block + gazetteer assertions (Phase 2 W1)
python -m ingest.verify          # corpus integrity checks, incl. placement audit
python -m ingest.gazetteer --check   # every placement resolves to a dated snapshot
python -m ingest.run_ingest --dry-run
python -m ingest.run_ingest      # applies scripts/schema-part3.sql, loads Postgres
python -m ingest.run_ingest --stats
```

24 documents → 44 chunks. Original-language text and its translation are separate
rows sharing a `parallel_group`, each carrying region, language, citation, date and
exact character offsets into the source JSON. Every chunk also carries a
`text_fidelity` label; the 2 chunks that aren't genuine source wording are marked
`eligible_for_retrieval = false` rather than deleted. `chunks.embedding` is
`vector(1024)` and stays NULL until Part 4.

15 retrieval-eligible non-English chunks across 7 languages (Greek, Literary Chinese,
Parthian, Old Tamil, Nabataean, Sabaic, Proto-Norse) — see the Part 3b source-recovery
notes in `PROGRESS.md`.

Re-running is idempotent and preserves embeddings unless the chunk text changed.

**Part 3 complete** — 44 chunks loaded, verified 2026-08-09.

## Part 4 — embeddings & cross-lingual retrieval

Code complete; run against your gateway and Postgres.

```powershell
python -m ingest.test_embed              # offline tests, no API calls
python -m ingest.run_embed --dry-run
python -m ingest.run_embed               # applies scripts/schema-part4.sql, embeds
python -m ingest.run_embed --stats
python -m retrieve.crosslingual_check    # the Part 4 exit condition
```

**Parts 4 and 5 complete** — 45 chunks embedded, 11/11 cross-lingual probes at rank 1
(4/4 same-language, 5/5 cross-lingual, 2/2 paired). An English query retrieves Literary
Chinese and Parthian sources at rank 1 with English translations excluded from the pool.

Embeds with `voyage-3.5` through the existing gateway. BGE-M3 is deferred until there
is evidence it's needed — it is *not* a config-only swap (Voyage is an API you have a
key for; BGE-M3 needs a hosted endpoint or a local inference server). Both are 1024-dim,
so the schema is unaffected and switching costs only a re-embed.

`chunks.embedding_model` records the concrete model, so a partially migrated table is
never mistaken for a finished one.

## Part 6 — in-loop translation & back-translation confidence

**Complete, verified 2026-08-10** — 12/12 gold cases, prose profile calibrated from 24
observations, bands stable across five archived runs.

```powershell
python -m answer.test_translate                 # 60 offline assertions, no API, no DB
python -m ingest.run_ingest                     # 24 docs -> 50 chunks after the corpus edit
python -m ingest.run_embed                      # 4 chunks come back pending
python -m eval.run_translation_check --dry-run  # resolve chunks + references, no calls
python -m eval.run_translation_check            # translate, back-translate, score, store
python -m eval.run_translation_check --stats
```

A retrieved non-English chunk is translated to English, that English is translated back
**without the model seeing the original**, and the round trip is scored two ways: chrF
(character n-grams — wording) and voyage-3.5 cosine (meaning). Where a published
translation exists, the machine English is also compared against it directly.

Results land in `chunk_translations` with the model, the prompt version and a hash of the
source text, so a translation of superseded text is never served with a citation attached
(`current_translations` vs `stale_translations`).

Thresholds are **not in the code**: `eval/gold/confidence_profiles.json` holds four genre
profiles, all marked `calibrated: false` until the first live run gives a distribution to
set them from. Verse has its own profile because a low round-trip score on Sangam poetry
is the correct answer, not a defect.

Retrieval probes moved out of `retrieve/crosslingual_check.py` into
`eval/gold/retrieval_probes.json` — same eleven probes, now with their rationale attached
and a loader that rejects unknown keys, so a misspelled field can no longer silently
disable an assertion.

Two things worth knowing before reading a score:

- **Bands are genre-relative.** A `high` on verse and a `high` on prose do not describe
  the same strength of evidence. Do not rank across profiles on the band alone.
- **A blocking flag outranks the band.** `vimose-gmq-pro` is stored as `low` *with*
  `untranslated_echo`, and that flag is the instruction: show the source and the published
  gloss, never a machine translation. Six partly undeciphered runic sequences are material
  this pipeline should refuse, and the gold set asserts that it does.

## Part 7 — grounded answer assembly

**Complete, verified 2026-08-10.**

```powershell
python -m answer.test_answer                        # 133 offline assertions
python -m answer.run_answer --dry-run "..."         # retrieve only, 1 embedding, no chat call
python -m answer.run_answer "..."                   # 1 embedding + 1 chat call
python -m answer.run_answer --json "..." > out.json
python -m answer.run_answer --repeat 3 "..."        # temperature 0 is not determinism
```

Retrieval → fold → resolve English → prompt → grounding report. Exit codes: `0`
grounded, `1` answered but failed a check, `2` could not run. An ungrounded
answer is still printed and still stored — hiding it would remove the only
evidence the eval harness has to work from.

**`fold_hits` is the piece worth understanding.** A translation chunk that gets
retrieved is folded into its original, so a source appears once with both
languages attached rather than twice. `align.py` then supplies the right passage
of the published translation and says on what evidence — section numbers,
position, or nothing.

Every run is archived to `eval/answer_runs/` as well as stored in `answers`. The
table holds the *current* answer for a question; the archive holds *that*
answer. Three runs of one question can land on a single row with different text,
which is exactly why the directory exists.

**A blocking flag outranks the confidence band.** Filtering on band alone would
present a machine "translation" of undeciphered runes.

## Part 8 — groundedness eval harness

**Complete, verified 2026-08-10.** The floor is `calibrated: false` — a
within-session regression gate, not a definition of success.

```powershell
python -m eval.test_answer_eval                     # 70 offline assertions
python -m eval.answer_eval --archives --by-case     # score what's on disk, no API calls
python -m eval.rescore_sweep                        # re-score + floor, no API calls
python -m eval.run_answer_sweep --dry-run           # 5 embeddings, no chat calls
python -m eval.run_answer_sweep --prompt-version p7-answer-v2r --repeat 3   # ~15 chat calls
```

Two findings that shape how the numbers should be read:

- **Groundedness is not correctness**, measured rather than argued. Across 46
  archived answers the two disagree in both directions — one scored grounded
  while omitting what its own evidence printed in English; the Chinese answers
  score *not* grounded while being accurate and well quoted.
- **`expect_cited_docs` proves the model named a source. Only
  `expect_quoted_docs` proves it used one.**

## Part 9 — the UI

**Complete 2026-08-12.** Opens by double-clicking; no server, no build step, no
CDN, no framework.

```powershell
python ui\build_ui_data.py            # regenerate ui/data.js from runs + corpus
python ui\build_ui_data.py --verify   # audit every citation, exit 1 if any break
node ui\check_ui.mjs                  # render all 61 archived runs headlessly
start ui\index.html
```

Three views: **Questions** (answers with clickable quotations and a provenance
panel), **Regions & sources**, **What you are looking at** (the citation audit).

`build_ui_data.py` re-checks every archived citation against the seed corpus *as
it stands today* — a different question from whether it held when the answer was
made. Current state, **77 archived runs / 168 claimed spans: 158 resolved, 9
case-only, 0 moved, 1 absent** (re-measured 2026-08-12, Block 0; the earlier
figure of 132/6/0/1 was taken over 61 runs). The 9 case-only are **one** span —
`eastasia-02-hou-hanshu.reference_translation[391:516]` — recurring across nine
runs, not nine defects; the count grows with runs until `cite.py` gains its third
match state in Phase 2 W2.

The one absent span quoted the Adulis translation correctly before that record
was replaced, and is the evidence that **an answer does not record which corpus
version it quoted** — the outstanding item closed by Phase 2 W3.

Run the builder after any corpus edit. That is what would have caught the drift
on the day it happened.

## Phase 1 result

Exit gate 2026-08-12: **persevere**, with a framing correction — the product is a
cross-lingual sourcebook that has geography, not a map that has sources.

The argument is an asymmetry: the corpus, the provenance chain and the
cross-lingual index are the expensive, hard-to-rebuild assets and they work; the
failures are in ranking, question handling and scoring, which are the cheapest
layers to change. The proof is that the system refused a question whose answer it
was holding, and answered correctly when the question was reworded against
byte-identical evidence.

**The number that sets the Phase 2 order:** mean top-1 to rank-6 similarity
spread across 77 archived runs is **0.105**. Ranking is currently unmeasured, and
the corpus cannot be scaled until it isn't. See `PHASE2.md`.
