# Mundus Ulterior — Phase 1 Progress Tracker

Broad thin slice: 3–5 sources from each of the seven regions. Exit gate is the
full cross-lingual → grounded-citation → eval loop working end to end.

_Last updated: 2026-08-12 — **Phase 1 complete. Verdict: persevere.**_
_Phase 2 plan: `PHASE2.md`. Closing summary at the foot of this file._

## Phase 1 parts

| Part | Description | Status |
| --- | --- | --- |
| 1 | Prerequisites & environment (gateway, Postgres/pgvector, layout) | ✅ Complete |
| 2 | Seed corpus — 3–5 sources per region (~25–30 docs) + provenance metadata | ✅ Complete (24 docs) |
| 3 | Ingestion & chunking with provenance baked in | ✅ Complete — 44 chunks loaded 2026-08-09 |
| 4 | Multilingual embeddings + cross-lingual index | ✅ Complete — voyage-3.5, 4/4 same-language, 4/4 cross-lingual |
| 5 | Cross-lingual retrieval + same-query-two-languages test | ✅ Satisfied by the Part 4 check — 11/11, paired queries agree |
| 6 | In-loop translation + back-translation confidence check | ✅ Complete 2026-08-10 — 12/12 cases, prose calibrated, bands stable across 5 runs |
| 7 | Grounded answer assembly with inline citations | ✅ Complete 2026-08-10 — 4/5 grounded, every quotation resolves to disk |
| 8 | Groundedness eval harness + hard floor (build alongside 5–7) | ✅ Complete 2026-08-10 — content gold set + floor built and running; floor `calibrated: false` after session variance invalidated it (see below) |
| 9 | Thin click-through UI | ✅ Complete 2026-08-12 — opens with no server; 132/139 archived citations re-verified against disk |
| 10 | Phase 1 exit gate — kill / pivot / persevere | ✅ Complete 2026-08-12 — **PERSEVERE**, with a framing correction and a reordered Phase 2 |

## Part 1 — what's in place (verified 2026-08-09)

- **Repo skeleton:** `ingest/ retrieve/ answer/ eval/ ui/ data/ gateway/ scripts/`
- **Python venv** with pinned deps (`requirements.txt`); FastAPI pinned `0.115.5`.
- **Postgres 16 + pgvector** via `docker-compose.yml`; extension auto-enabled by
  `scripts/init-db.sql`. Confirmed: `pgvector installed: True` (PostgreSQL 16.14).
- **LiteLLM gateway** on `:4000`, routing:
  - chat → `anthropic/claude-haiku-4-5-20251001`
  - embed → `voyage/voyage-3.5` (1024-dim)
- **Secrets** in `.env` (git-ignored): `ANTHROPIC_API_KEY`, `VOYAGE_API_KEY`,
  `LITELLM_MASTER_KEY`, `APP_DATABASE_URL`.
- **Milestone passed:** `scripts/hello.py` returns a Claude reply + a 1024-dim
  Voyage embedding; `scripts/check_db.py` returns `pgvector installed: True`.

Key decisions / fixes locked in (details in `../mundus-ulterior-phase1-part1-setup.md`):
`fastapi==0.115.5`; app DB var renamed `APP_DATABASE_URL` (avoids LiteLLM's Prisma
trigger); gateway must be restarted after any key change; `.env` key lines carry
no inline comments.

## Part 2 — what's in place (verified 2026-08-09)

- **24 documents** on disk at `data/seed_corpus/<region>/*.json`, spanning all seven
  regions (Persia 3, Arabia 4, East Asia 3, South Asia 4, Southeast Asia 3,
  Sub-Saharan Africa 3, Scandinavia 4) — just under the ~25-30 target, weighted toward
  quality/verification over hitting the top of the range.
- Each record captures: original text (or excerpt), reference translation, source
  language code(s), region, stable citation (+ a secondary "original-language" citation
  where the translation source differs from the text-critical edition), rough date,
  and findspot where applicable. Schema documented in `data/seed_corpus/manifest.json`.
- Mix of source types: inscriptions (trilingual ŠKZ, Ezana Stone, Palmyrene Tariff,
  Nabataean/Sabaic, Vimose runes), literary texts (Periplus ×4 sections, Weilüe, Hou
  Hanshu, Akananuru 149, Muziris papyrus), and find/coin records (British Museum,
  National Museum of Denmark, Gyeongju National Museum, Óc Eo, Khao Sam Kaeo, Pattanam).
- Index: `data/seed_corpus/MANIFEST.md` (human-readable) and `manifest.json`
  (machine-readable), including a `follow_up_before_ingestion` list.
- **Known gaps to close before/during Part 3 ingestion:** five records (Palmyrene
  Tariff, Weilüe, Hou Hanshu, Akananuru 149, Ezana Stone) have paraphrased rather than
  verbatim original-language text — pull exact transliterations from the cited critical
  editions before chunking. The Arabia Sabaic entry (Jabal Ḏabūb) is 6th-century and not
  directly Rome-linked; consider a denser Himyarite/Roman-contact replacement.

Milestone met: ~25 documents on disk, each with original text + provenance metadata,
spanning all seven regions. ✅

## Part 3 — what's in place (built 2026-08-09)

The ingestion pass is written and passes every offline check. **The Postgres load
itself has not been run** — Docker/Postgres lives on the Windows host, so the final
`python -m ingest.run_ingest` step is yours to execute (see below).

### Code

| File | Role |
| --- | --- |
| `scripts/schema-part3.sql` | `documents` + `chunks` tables, provenance columns, `vector(1024)` (NULL until Part 4). Idempotent. |
| `ingest/chunker.py` | Meaning-aware splitting; exact character spans. |
| `ingest/fidelity.py` | Classifies how faithful each text is to its primary source. |
| `ingest/loader.py` | Reads seed JSON → `Document` + `Chunk` records. |
| `ingest/db.py` | Idempotent upsert + prune; post-load summary. |
| `ingest/run_ingest.py` | CLI: `--dry-run`, `--stats`, `--json`, `--verbose`. |
| `ingest/verify.py` | Corpus integrity checks. |
| `ingest/test_chunker.py` | Splitting + offset round-trip tests. |
| `ingest/test_sql.py` | SQL ↔ dataclass alignment, CHECK-constraint coverage. |

### Design decisions

- **Chunk on meaning.** A field becomes one chunk unless it exceeds ~1200 chars,
  and then splits at the strongest available boundary: `§` markers → paragraph →
  line → sentence (incl. `。`). Never a fixed token window. No record in the
  current corpus needs splitting; the paths are covered by synthetic tests because
  the Palmyrene Tariff alone will run ~400 lines once its verbatim text is pulled.
- **Exact offsets.** `source_text[char_start:char_end] == chunk.text` always holds,
  so any Part 7 citation traces back to characters on disk. Asserted in `verify.py`.
- **Original and translation are separate rows** sharing a `parallel_group`. This
  is the precondition for the Part 5 same-query-two-languages test: a Greek query
  can retrieve the Greek without the English riding along.
- **`lang` is script-detected, not declared.** `declared_lang` keeps what the record
  claims. Where they diverge — a Middle Persian inscription stored as English prose —
  that divergence is the signal.
- **`text_fidelity` + `eligible_for_retrieval`.** Nothing is discarded; text that
  isn't genuine source wording is flagged and held out of the index.

### Result of the dry run (24 docs → 44 chunks, after source recovery)

- Regions: all seven present.
- Roles: 28 original, 16 translation, **16 parallel pairs**. The 8 records without
  a translation are all find/coin records with `reference_translation: null` — they
  have no source-language text to translate, so this is expected, not a gap.
- Chunk size: min 36 / median 363 / max 990 chars. Two records now require splitting
  (the Greek Periplus sections), exercising the `§`-boundary path.
- Fidelity: `object_description` 14, `translation` 13, `verbatim_original` 8,
  `transliteration` 4, `partial_verbatim` 3, `pointer` 2.
- **42 chunks retrieval-eligible, 2 held back.**
- **15 retrieval-eligible non-English chunks** across 7 languages: Greek 8,
  Literary Chinese 2, Nabataean 1, Sabaic 1, Parthian 1, Proto-Norse 1, Old Tamil 1.

### What the classifier found (matters more than the counts)

Two things the manifest's `follow_up_before_ingestion` note did not capture:

1. **Six `original_text_excerpt` fields are editorial placeholders, not text** — e.g.
   `"[Greek text of §53-54 … pull full section from the Greek Wikisource anchor]"`.
   Embedding these would have put the corpus editor's own prose into the retrieval
   index, where Part 7 could cite it as a primary source. Affected: Palmyrene Tariff,
   Akananuru 149, Muziris papyrus, Periplus §53-54, Ezana Stone, Periplus Adulis.
   All classified `pointer` and excluded. The ŠKZ *translation* field is also a
   pointer ("available at the citation URL"), and the ŠKZ *original* is an English
   rendering of the Greek recension — both excluded.
2. **Hou Hanshu and Weilüe are fine.** The manifest flagged both as paraphrased, but
   both hold genuine verbatim Chinese (100% Han script) — abridged, not invented.
   Classified `partial_verbatim` and kept eligible. Excluding them would have removed
   every Chinese text from the corpus and left East Asia with nothing to test in Part 5.

At first pass this left only **6 retrieval-eligible non-English chunks** — enough to
*run* the Part 5 cross-lingual test, but too thin for a passing result to mean much.
That gap has since been closed; see the next section.

## Part 3b — source recovery (2026-08-09)

Six of the eight held-back chunks were not missing sources, only missing transcription:
each record already cited an edition that turned out to be openly available. Text was
pulled and written into the seed JSON, with `original_text_note` recording exactly what
was taken, what was normalised, and under what licence.

| Record | Recovered | Source |
| --- | --- | --- |
| Periplus §4-6 (Adulis) | Koine Greek, 2,089 chars | Greek Wikisource, ed. C. Müller, *GGM* I (1855), public domain |
| Periplus §27-29 (Frankincense Country) | Koine Greek, 1,614 chars | same |
| Periplus §53-54 (Muziris) | Koine Greek, 990 chars | same |
| Muziris papyrus (SB 18 13167) | Greek recto + verso, 711 chars | DDbDP via papyri.info, CC BY 3.0 |
| Akanāṉūṟu 149 | Old Tamil, full 19-line poem | Project Madurai PM 0229 |
| ŠKZ | Parthian §1 + §20, transliteration *and* transcription | Parthian Sources Online, ed. Huyse 1999 |

Result: **non-English retrieval-eligible chunks 6 → 15**, languages 5 → 7, and the ŠKZ
record now carries real Parthian rather than an English rendering of the Greek recension.
The ŠKZ §20 province list (Thrace, Bithynia, Asia, Pamphylia, Isauria, Lycaonia, Galatia,
Lycia, Cilicia, Cappadocia, Phrygia, Syria) is direct Rome-contact evidence in Parthian.

**Still held back (2):**

- **Palmyrene Tariff** — the Aramaic/Greek text runs ~400 lines across four faces; the
  critical edition (Healey 2009/2014) is not openly available. Worth checking DASI, which
  holds Aramaic material from the region.
- **Ezana Stone** — Ge'ez/Sabaic/Greek. Needs DAE IV or RIÉ 185/270; Beta maṣāḥǝft is the
  most likely open route.

**A bug this shook out.** `parallel_group` was originally assigned per span, so passage N
of the original would pair with passage N of the translation. That only holds when both
sides split into the same number of pieces — and once the Greek Periplus started splitting
into three chunks against a one-chunk English summary, the original↔translation link broke
for exactly the records that matter most. Parallel grouping is now document-level, which is
all we can honestly claim; sentence-level cross-lingual alignment belongs in Part 6.

### To run the load (Windows / PowerShell, from the repo root)

```powershell
.venv\Scripts\Activate.ps1
# load .env into this window (see README step 2)
docker compose up -d db

python -m ingest.test_chunker      # synthetic splitting + offset tests
python -m ingest.test_sql          # SQL <-> dataclass alignment (needs sqlglot)
python -m ingest.verify            # corpus integrity checks
python -m ingest.run_ingest --dry-run     # report, writes nothing

python -m ingest.run_ingest        # applies schema, loads Postgres
python -m ingest.run_ingest --stats
```

Re-running is safe: upserts by primary key, prunes rows for records deleted from disk,
and preserves any Part 4 embedding unless the chunk text itself changed.

**Milestone met 2026-08-09.** ✅ Load confirmed on the host: 24 documents, 44 chunks,
all seven regions, `awaiting_embedding: 42`, `pruned: 0`. Seed corpus is chunked and in
Postgres with provenance intact.

## Part 4 — starting point (for the next thread)

1. ~~Close the non-English gap.~~ Done in Part 3b — 15 eligible non-English chunks
   across 7 languages. Two records remain held back (Palmyrene Tariff, Ezana Stone);
   neither blocks Part 4, and the classifier will promote them automatically if their
   text is ever pulled, with no code changes.
2. **Embed with `voyage-3.5` first — decision taken 2026-08-09.** Correcting an earlier
   note in this file: swapping to BGE-M3 is *not* config-only. Voyage is an API the
   gateway already holds a key for; BGE-M3 is an open model, so it needs either a
   provider that hosts it or a local inference server. Both are 1024-dim, so the schema
   is unaffected and a later swap costs only a re-embed. Voyage-3.5 is multilingual and
   already working, so it goes first; BGE-M3 gets revisited only if Voyage measurably
   fails on the hard cases — Parthian transliteration, Literary Chinese, Old Tamil.
3. Embed every chunk with `eligible_for_retrieval = true` (42 of 44), write to
   `chunks.embedding`.
4. Build the HNSW index (deliberately not created in Part 3, so the distance operator
   class can be chosen once embeddings exist).
5. Sanity check: a Greek query vector should sit closer to the Greek Periplus chunk
   than to its English translation chunk.

## Part 4 — what's in place (built 2026-08-09, not yet run)

| File | Role |
| --- | --- |
| `scripts/schema-part4.sql` | `embedding_model` / `embedding_dim` / `embedded_at` columns, provenance CHECK, HNSW cosine index, `retrievable_chunks` view. Idempotent. |
| `ingest/embed.py` | Gateway-routed embedding client: batching, bounded retry, dimension validation, `input_type` document/query. |
| `ingest/run_embed.py` | Backfill CLI — `--dry-run`, `--limit`, `--force`, `--stats`, `--skip-index`. Resumable. |
| `retrieve/search.py` | Cosine KNN over `retrievable_chunks`, with language/region/role filters. |
| `retrieve/crosslingual_check.py` | 10 probes across three families — the Part 4 exit condition. |
| `ingest/test_embed.py` | 26 offline assertions, no network, no DB. |

### Design decisions

- **Embedding provenance is stored, not assumed.** `embedding_model` records the
  *concrete* model (`voyage/voyage-3.5`), resolved by reading `gateway/config.yaml` —
  not the alias `embed-default`, which will be repointed at BGE-M3 later. Storing the
  alias would make voyage and BGE-M3 vectors indistinguishable in the same column,
  and cosine distance across two models is meaningless. A CHECK constraint keeps
  vector and label in lockstep.
- **Cosine everywhere.** voyage-3.5 returns L2-normalised vectors and BGE-M3 dense
  output is normalised too, so `vector_cosine_ops` survives a model swap. `search.py`
  uses `<=>` to match; a mismatched operator would silently bypass the index —
  correct results, wrong performance, no error.
- **The held-back chunks are unreachable by construction.** The backfill filters on
  `eligible_for_retrieval`, and search reads the `retrievable_chunks` view rather than
  the table. A Part 3 placeholder cannot be embedded, retrieved, or cited.
- **`input_type` document vs query.** Voyage distinguishes these and it measurably
  helps retrieval. If the gateway rejects the parameter, the client falls back and
  prints a warning rather than quietly degrading.
- **Non-English chunks are embedded first** (`ORDER BY lang <> 'en' DESC`), so a run
  interrupted partway still leaves the interesting material queryable.
- **Timeouts and retries are pinned** (fixed 2026-08-09 after the first run appeared to
  hang). The OpenAI SDK defaults to a 600-second timeout *and* two internal retries;
  layered under this module's own 4-attempt loop that is up to 12 attempts at ten
  minutes each — roughly an hour of silence with no output. The client now sets
  `timeout=60` (override with `EMBED_TIMEOUT`) and `max_retries=0`, and the backfill
  prints a line per batch, so a slow gateway reports instead of looking dead.

### The cross-lingual check (`python -m retrieve.crosslingual_check`)

Three probe families, increasing difficulty:

1. **same_language** (4 probes) — Greek query finds Greek text, Chinese finds Chinese,
   Tamil finds Tamil, Parthian finds Parthian. Failure here means the model cannot see
   the script at all.
2. **cross_lingual** (4 probes) — English query, with English translations *excluded
   from the candidate pool* so the model cannot cheat by matching English to English.
   This is the claim the project actually rests on.
3. **paired** (2 probes) — the same question in English and Greek must return the same
   document. This is the "same query, two languages" test from the Phase 1 plan.

A failure is informative, not fatal: it is precisely the evidence that would justify
swapping to BGE-M3. Which family fails matters — `same_language` failure means an
unsupported script, `cross_lingual` failure means a weak shared space.

### Dependency gotcha (hit 2026-08-09)

`litellm[proxy]` was unpinned. Adding one test-only package (`sqlglot`) made pip
re-resolve the whole tree, backtrack from the working 1.95.0 down to 1.93.0 — which
ships as an sdist with no cp314 wheel — and try to download a Rust toolchain to
compile it. On Python 3.14 that fails, and the install aborts.

Fixed two ways: `litellm[proxy]==1.95.0` is now pinned, and test-only deps moved to
`requirements-dev.txt` so installing them can never disturb runtime resolution. Both
test suites skip their sqlglot checks gracefully if it isn't present.

**Worth knowing:** this venv is Python 3.14 (cp314), which is new enough that wheels
are still patchy. That will matter again if BGE-M3 is ever run locally — torch and
sentence-transformers lag new CPython releases. A hosted BGE-M3 endpoint sidesteps it.

### The limit of offline SQL testing (learned 2026-08-09)

`search.py` shipped with `%(langs)s IS NULL OR lang = ANY(%(langs)s)`. That parses
cleanly and failed at execution with `AmbiguousParameter: could not determine data type
of parameter $2` — Postgres cannot infer a type for a NULL parameter used that way.

The offline suites could not have caught it: no Postgres is available in the dev
sandbox, so the SQL is only ever *parsed*, never *planned*. Fixed by casting every
nullable filter parameter (`::text[]`) and the query vector (`::vector`) at every use,
plus a regression guard in `test_embed.py` that flags any parameter appearing beside
`IS NULL` without a cast — verified to catch the original form.

Standing lesson for Parts 5-8: parse-level checks catch typos, not type inference.
Anything with optional/NULL parameters needs at least one execution against the real
database before it is called done.

### Rate limits, and an error that lied (2026-08-09)

First live run of the cross-lingual check reported 7 failures and advised swapping to
BGE-M3. All 7 were **Voyage free-tier rate limiting** — 3 requests/minute — because the
check embedded each probe query in its own request. No model quality signal at all.

Three fixes:

1. **One request, not ten.** All probe queries are embedded in a single batched call.
   Ten short queries sit far inside the 10K tokens/minute ceiling.
2. **Rate limits are recognised and waited out**, with a 21-second backoff (a full
   window) rather than exponential-from-2s, which would spend every attempt inside the
   same throttled minute.
3. **The error message no longer lies.** LiteLLM wraps upstream provider errors as
   `litellm.APIConnectionError`, and the connection-error check matched that class name
   — so a Voyage rate limit was reported as "cannot reach the LiteLLM gateway", pointing
   at a healthy gateway. Rate limits are now tested first, and the connection check
   matches socket-level failures only.

The harness also conflated "the embedding call errored" with "the model ranked the wrong
source", and emitted BGE-M3 advice off the back of an infrastructure fault. Ranking
failures and errors are now separate, and the BGE-M3 recommendation only fires when
same_language or cross_lingual probes genuinely rank wrong.

**Free-tier budgeting:** at 3 RPM, keep requests few and batches large. The full
embedding pass is 2 requests; the check is 1.

## Part 4 — RESULT (2026-08-09) ✅

Final verified run: **24 documents → 47 chunks, 45 retrieval-eligible, 45 embedded**
with `voyage/voyage-3.5`. 18 non-English: Greek 11, Literary Chinese 2, Old Tamil 1,
Nabataean 1, Parthian 1, Sabaic 1, Proto-Norse 1.

**11/11 probes at rank 1.**

| Family | Result | Similarities |
| --- | --- | --- |
| same_language | **4/4** | Chinese 0.676, Parthian 0.607, Greek 0.639, Old Tamil 0.368 |
| cross_lingual | **5/5** | EN→Parthian 0.520, EN→Greek 0.513 / 0.498 / 0.491, EN→Chinese 0.472 |
| paired | **2/2**, identical top hit | EN 0.539, GRC 0.747 — both §54 |

The pepper probe returns **§56** (`πέπερι` present) at 0.513, up from a meaningless 0.389
when it was matching §53 by document id alone.

**Decision: stay on voyage-3.5. BGE-M3 is not needed.** An English question retrieves a
Literary Chinese source and a Parthian transliteration at rank 1, with the English
translations excluded from the candidate pool so the match cannot be English-to-English.
That is the project's central claim, working.

Watch item: Old Tamil similarity is 0.370 against 0.6-0.7 for the other scripts. It still
ranks first, but there is exactly one Tamil chunk in the corpus, so this is a weak
measurement. Re-check when Tamil coverage grows.

### The paired probes, and a corpus gap they exposed

Both paired probes returned `arabia-01-periplus` §28 first with the Muziris text second —
and they *agreed with each other*, which is the "same query, two languages" test passing
in the sense that matters. The mismatch was my expected label, not the model: the probe
asked about **pepper**, which is Periplus **§56**, while the record held only §53-54.
The corpus did not contain the answer being asked for.

Resolved two ways, kept separate so neither contaminates the other:

1. **Probe corrected** to ask what §53-54 actually says (the Limyrike ports and their
   kingdoms). Fixing a bad test.
2. **Corpus extended** to §53-56, justified on its own merits: §56 is the cargo manifest
   — pepper from Kottanarike, Gangetic nard, ivory, Chinese silk cloth, pearls, diamonds,
   and the July sailing from Egypt. A record titled "Muziris and the Limyrike coast" that
   stops at §54 omits the passage that documents the trade. §55 included for contiguity.
   A separate new probe tests the pepper passage.

Corpus is now **24 documents → 47 chunks**, 18 non-English eligible (Greek 11).

**Known asymmetry:** this record's original now covers §53-56 while its reference
translation covers §53-54 only. Recorded in `original_text_note` and `notes`. It will
matter for the Part 6 back-translation check and should be closed by adding the Schoff
English for §55-56.

### Re-run needed after the corpus change

`run_ingest` nulls the embedding of any chunk whose text changed, so the three new/changed
Greek chunks come back as pending and get re-embedded automatically.

### Two bugs the §56 re-ingest exposed (2026-08-09)

**1. The Part 4 constraint contradicted the Part 3 upsert.** Part 4 added
`chunks_embedding_provenance`, requiring `embedding` and `embedding_model` to be
null-or-present together. Part 3's upsert cleared only `embedding` when a chunk's text
changed, leaving the model label behind — so the first re-ingest of an edited record
aborted the entire load with a `CheckViolation`. The constraint was right; the upsert
predated it and was never revisited. All four embedding columns now clear together.

Structural fix as well as a point fix: the provenance columns and the constraint moved
into `schema-part3.sql`'s `CREATE TABLE`, so a fresh database has the same shape as a
migrated one, and `apply_schema()` now applies Part 4 as well. Both remain idempotent.

**2. A probe passed against the wrong passage.** The new pepper probe reported PASS while
§56 was not even in the database — because ranking matched on `doc_id`, and §53 belongs
to the same document. Its similarity (0.389, the lowest of any cross-lingual probe) was
the only hint. Probes can now assert passage content (`expect_text_contains="πέπερι"`),
so the right document with the wrong passage no longer counts.

Both have regression guards in `test_embed.py`, each verified to fail against the
original form.

**Also fixed:** `run_ingest` now checks the database connection *before* printing its
report. A stopped container previously produced forty lines of apparently-successful
output followed by a traceback. And `docker-compose.yml` gained `restart: unless-stopped`.

## Part 6 — starting point (for the next thread)

**State:** Parts 1-5 complete and verified. 24 documents → 47 chunks → 45 embedded with
`voyage/voyage-3.5`. Cross-lingual retrieval works: 11/11 probes at rank 1.

Goal: in-loop translation with a back-translation confidence check. The pipeline
retrieves a non-English chunk, translates it for the answer, and needs a signal for how
much to trust that translation before Part 7 cites it.

### Do this first

**Close the Muziris asymmetry.** `south_asia/periplus-muziris.json` holds original §53-56
but reference translation §53-54 only. Add the Schoff English for §55-56 (already cited in
`translation_source`). This is the corpus's best back-translation test case: four Greek
chunks with known-good published English to score machine translation against.

### Parallel pairs available for back-translation testing

16 records have both an original and a reference translation. The strongest:

- **ŠKZ** (`persia-01-skz`) — Parthian transliteration + transcription, with Huyse's
  English. The hardest translation case in the corpus and the best test of the
  confidence check, because a low score here would be *correct*.
- **Periplus ×3** — Greek with Schoff's 1912 English. Public domain, well-studied.
- **Akanāṉūṟu 149** — Old Tamil with English. Poetry; expect low back-translation
  agreement that does not indicate failure. Worth deciding early whether the confidence
  metric should be genre-aware, or you will "fix" a metric that was right.

### Build the eval harness alongside (Part 8)

`retrieve/crosslingual_check.py` is 11 hand-written probes with hardcoded expectations.
It has already produced one false PASS (matching on `doc_id` instead of passage). Before
Part 6 adds translation-quality assertions, move to a declarative gold set in `eval/`
with probes as data, not code.

### Standing lessons from Parts 3-5

- Parse-level SQL checks miss type inference. Anything with optional/NULL parameters
  needs one execution against the real database.
- A test that passes for the wrong reason is worse than one that fails. Assert on the
  specific thing, not a proxy for it (`doc_id` was a proxy; passage content is the thing).
- The gateway's free tier is 3 requests/minute. Batch aggressively; one request for all
  probe queries, not one per probe.
- Two PowerShell windows, both needing `cd` + venv activate + `.env` load. The gateway
  reads keys only at startup.

### To run (Windows / PowerShell, repo root, gateway up on :4000)

```powershell
python -m ingest.test_embed                 # offline, no API calls
python -m ingest.run_embed --dry-run
python -m ingest.run_embed --limit 4        # spend 4 API calls, sanity-check
python -m ingest.run_embed                  # embed the remaining eligible chunks
python -m ingest.run_embed --stats          # expect embedded 42, pending 0
python -m retrieve.crosslingual_check
```

Expect `embedded: 42`, `pending: 0`, `embedded_but_ineligible: 0`, and
`by_model: {"voyage/voyage-3.5": 42}`.

## Part 6 — what's in place (built 2026-08-10, not yet run live)

Written and passing every offline check (60/60 assertions, no network, no database).
**The live run is yours to execute on the host** — Docker, Postgres and the gateway all
live on Windows. See "To run" at the end of this section.

### Code

| File | Role |
| --- | --- |
| `answer/translate.py` | Gateway-routed translation: forward (source → English) and back (English → source), strict output contract, rate-limit and dead-gateway handling. |
| `answer/confidence.py` | chrF + cosine scoring, bands, and the flags that say *why* a score is what it is. No network, no database. |
| `answer/align.py` | Pairs an original chunk with the right passage of its published translation, and records on what evidence. |
| `answer/store.py` | Reads chunks for translation; writes translations back with provenance. |
| `scripts/schema-part6.sql` | `chunk_translations` + `current_translations` / `stale_translations` views. Idempotent. |
| `eval/goldset.py` | Strict loader for the declarative gold set. |
| `eval/gold/*.json` | Retrieval probes, confidence profiles, translation cases — as data. |
| `eval/run_translation_check.py` | The Part 6 entrypoint: translate → back-translate → score → record. |
| `answer/test_translate.py` | 104 offline assertions, including regression guards for every defect found in the two live runs, each verified to fail against the bug it guards. |

### Design decisions

- **Two signals, not one.** chrF (character n-grams, so no per-script tokenizer) measures
  wording; voyage-3.5 cosine measures meaning. A single number would be easier to read
  and worse to trust. The pair earns its keep where the two disagree: high cosine with low
  chrF is a paraphrase, which is the *expected* result for verse; high chrF with low
  cosine is close to impossible in an honest round trip and points at something being not
  what it claims to be.
- **The back-translation never sees the original.** It is a separate request with no
  history, and `build_back_messages` does not take the original as a parameter — it
  cannot leak it. A test asserts the Greek appears nowhere in the payload, and was
  verified to fail when a leak is deliberately introduced. Without this the score
  measures contamination and looks like success.
- **Meaning leads, wording corroborates.** chrF can only pull a band down from high to
  medium, never up. A string coincidence must not be able to manufacture confidence.
- **The echo check runs first.** The likeliest silent failure is the model handing back
  the source untranslated — a perfect round trip for no work, and most tempting when the
  source is already in Latin script, which is exactly the ŠKZ case. Forward output is
  compared against the source before anything else, and a match blocks the result.
- **Thresholds are data, not code.** `eval/gold/confidence_profiles.json` holds four
  genre profiles (prose / documentary / inscription / verse), every number marked
  `calibrated: false`. They are guesses until the first live run produces a distribution.
  Putting them in Python would invite the opposite move: quietly loosening the metric
  until the corpus passes. Verse has its own profile so that a correct low score on
  Akanāṉūṟu 149 does not get "fixed" for everything else — the Part 6 note in this file
  warned about exactly that, and the profile is the answer to it.
- **Alignment states its own evidence.** Part 3 set `parallel_group` at document level and
  said passage alignment could not be honestly claimed. `align.py` claims it only where
  both sides carry the same section markers (`ground="section"`), falls back to positional
  pairing when the counts match (`"index"`, labelled as weaker), and otherwise claims
  nothing (`"none"`, and the comparison drops to document level). The ground travels into
  the run output, so a weak `chrf_ref` can be read for what it is.
- **Translations are cached with full provenance.** `(chunk_id, target_lang, model,
  prompt_version)` is the primary key, and the row also stores a SHA-256 of the source
  text it was made from. `current_translations` serves only rows whose hash still matches
  the chunk; the rest surface in `stale_translations`. Same argument as Part 4's
  `embedding_model`: a translation is the output of (model, prompt, text), and a cache
  that records one of the three cannot tell you what it is holding. Part 3's upsert
  already nulls a vector when chunk text changes; the hash extends that rule to text the
  ingest pass has no reason to know about.

### The gold set (Part 8, started here)

`retrieve/crosslingual_check.py` no longer contains its probes. All eleven moved verbatim
into `eval/gold/retrieval_probes.json`, along with the reason each exists — including the
note that the pepper probe once passed against the wrong passage. The candidate-language
pool is defined once and referenced by name, so four cross-lingual probes can no longer
drift apart.

The loader rejects **unknown keys**. Write `expect_contains` where the field is
`expect_text_contains` and the assertion silently disappears, leaving a probe that checks
only a document id — which is the precise bug the gold set exists to prevent. A typo is
now a load-time error.

`eval/gold/translation_cases.json` holds nine cases across five source languages. Band
floors are deliberately loose while the thresholds are uncalibrated; what every case does
assert is that a round trip *happened* — no echo, no refusal, no empty response. That
assertion is true or false independently of any threshold, so it is worth failing on
today.

### Corpus change: the Muziris asymmetry is closed

`south_asia/periplus-muziris.json` held Greek §53-56 against an elided English §53-54.
The reference translation now carries Schoff's §53-56 in full, from the Silk Road Seattle
digitisation (1912, public domain). Two mechanical changes, both recorded in a new
`reference_translation_note`: the modern editors' square-bracket glosses comparing
Casson's readings are dropped, and one hyphenation artefact is closed up. Schoff's own
spellings are left alone, including the odd ones — an editorial correction here would be
indistinguishable from source wording downstream.

Both sides now split into **four chunks each, section for section**, so this is the one
record in the corpus where machine English can be scored against published English for
the same passage rather than the same document. Corpus is now **24 documents → 50
chunks** (was 47); `ingest/verify` passes.

### What the offline tests cover — and what they cannot

Six regression guards, each verified to fail against the bug it guards (mutation-tested,
not assumed):

1. back-translation prompt leaking the original;
2. a chat preamble kept as if it were translation output;
3. the echo check disabled;
4. chrF made whitespace-sensitive — which would score Literary Chinese and Greek on
   different footings;
5. the gold loader's unknown-key check removed;
6. a NULL-able SQL parameter losing its `::text[]` cast.

**What they cannot catch is unchanged from Part 4:** the SQL here is parsed, never
planned. `AmbiguousParameter` and friends only appear against a real Postgres. The first
live run is the test that counts.

### Cost model

Translation is **two chat calls per case and they cannot be batched** — that is inherent,
since the back-translation must consume the forward output. Embeddings are taken in a
single batched call *after* all the chat work, because Voyage's free tier is 3
requests/minute. A full nine-case run is 18 chat calls (Anthropic, not Voyage) and 1-2
embedding requests. Chat rate limits are a different tier from embeddings, so `--pause`
exists if the account needs it.

### To run (Windows / PowerShell, repo root, gateway up on :4000, db up)

```powershell
python -m answer.test_translate              # offline, no API calls, no DB
python -m ingest.verify                      # corpus integrity after the Muziris edit
python -m ingest.run_ingest                  # re-load: 24 docs -> 50 chunks
python -m ingest.run_embed                   # 4 chunks come back pending; embed them
python -m retrieve.crosslingual_check        # probes now load from eval/gold/
python -m eval.run_translation_check --dry-run
python -m eval.run_translation_check --case muziris-54-grc    # 2 chat calls
python -m eval.run_translation_check         # the whole gold set
python -m eval.run_translation_check --stats
```

Expect after re-ingest: `chunks: 50`, `awaiting_embedding: 4`, `pruned: 0`. The three new
English chunks are §54-56 of the Schoff translation; the fourth is the old §53-54 chunk,
whose text changed and whose vector was therefore cleared — the Part 3 rule working as
intended.

## Part 6 — first live run (2026-08-10, 9 cases)

First live run: 24 documents → **50 chunks → 48 embedded**, 11/11 retrieval probes still at
rank 1 after the corpus change, and **9/9 translation cases reported PASS**.

| case | band | chrF↺ | cos↺ | chrF·ref | cos·ref |
| --- | --- | --- | --- | --- | --- |
| muziris-54-grc | high | 0.565 | 0.967 | 0.583 | 0.938 |
| muziris-56-grc | high | 0.560 | 0.961 | 0.495 | 0.924 |
| frankincense-28-grc | high | 0.555 | 0.936 | 0.275 | 0.756 |
| weilue-lzh | medium | 0.213 | 0.874 | 0.209 | 0.808 |
| hou-hanshu-lzh | high | 0.579 | 0.938 | 0.255 | 0.874 |
| akananuru-149-oty | medium | **0.004** | 0.573 | 0.297 | 0.704 |
| skz-xpr | medium | 0.194 | 0.897 | 0.653 | 0.960 |
| jabal-dabub-xsa | medium | 0.113 | 0.767 | 0.336 | 0.897 |
| muziris-papyrus-grc | high | 0.506 | 0.896 | 0.442 | 0.862 |

**9/9 PASS is the least interesting fact about this run.** The floors were deliberately
loose, so nothing *could* have failed. Three findings matter more.

### 1. One case passed and should not have — a false PASS, again

`akananuru-149-oty` scored chrF 0.004 and was reported `medium` with no flags. The cause
was not translation quality: the source is in **Tamil script** and the back-translation
came back in **Latin romanisation** ("Cīriya kalam āṟṟiya teṟkkaḷ…"), so chrF was
comparing two alphabets. Confirmed by measurement — non-Latin ratio 1.00 on the source,
0.00 on the back-translation, while every other case matched its source exactly.

It slipped through a gap between the flags: 0.004 is not a *high* chrF, so
`semantic_ok_lexical_low` never fired, and cos 0.573 was not low enough to breach a floor.

Two fixes, both regression-guarded and mutation-tested:

- **`script_mismatch`** is now a blocking flag in `answer/confidence.py`, comparing the
  non-Latin ratio of source and back-translation (reusing `ingest.fidelity`'s 0.30
  threshold — one definition, not two). Deliberately asymmetric: ŠKZ and the Sabaic
  inscription are *stored* romanised, so both sides are Latin and no mismatch exists.
- **The back prompt now names the script.** v1 told transliterated languages to romanise
  and said nothing to the others, leaving the choice to the model. `NATIVE_SCRIPT_LANGS`
  now demands Greek/Chinese/Tamil/Ge'ez/Aramaic characters explicitly.
  `BACK_PROMPT_VERSION` is bumped to `p6-backtranslate-v2` rather than edited in place —
  it is part of the primary key, so the v1 rows stay readable instead of being
  overwritten by output from a different prompt. That column earning its keep on day one
  is the strongest argument for having added it.

**The verse profile therefore has no usable measurement yet.** Re-run that case before
concluding anything about Sangam poetry or about Old Tamil.

### 2. Cosine is saturated, and the thresholds were far below the data

Eight of nine cases landed between **0.767 and 0.967**; the ninth was the script mismatch.
Two texts in the same language on the same subject sit close together in voyage space
more or less regardless of how good the translation is. Prose `cos_high` was 0.75 — below
the entire observed distribution, so it had no power to fail anything.

Recalibrated from the run: **prose is now `cos_high` 0.93 / `cos_low` 0.80** (n=5,
`calibrated: true`). `documentary` and `verse` stay uncalibrated at n=1 — one data point
is not a distribution, and marking it calibrated would be the lie the flag exists to
prevent.

`inscription` caught the same error twice: with `cos_high` at 0.70 the recalibration
promoted **ŠKZ to `high`** — precisely the outcome named in advance as the sign the metric
had stopped measuring anything. Raised to 0.90, so both inscription cases read `medium`,
which is the honest answer at n=2: not yet distinguishable from each other.

### 3. Two low scores have known causes that are not translation errors

- **ŠKZ (chrF↺ 0.194).** The record stores Huyse's *heterographic transliteration*
  (`ANE mzdyzn ALHA šhypwhr MLKYN MLKA`); the model back-translates into *phonemic
  transcription* (`az man Mazdēsn, yazd Šābuhr, šāh šāhān`). Same text, same meaning —
  cos 0.897 agrees — two scholarly conventions. The fix is to score against the
  transcription the record *already contains*, not to lower a threshold. Left as a Part 7
  task rather than papered over.
- **Literary Chinese chrF is structurally lower.** 0.213 (Weilüe) against 0.579 (Hou
  Hanshu) on comparable work: a 52-character passage has few character n-grams and each
  character carries far more meaning than a Greek one. **chrF is script-sensitive in a way
  the genre axis does not capture.** Open question: whether profiles need a second
  dimension, or whether chrF should be normalised by script. Do not resolve it by widening
  the prose band until it stops complaining.

**On ŠKZ's chrF·ref of 0.653** — the highest agreement with a published translation of any
case, higher than the Greek prose. Not evidence of a great translation, and not (on
inspection) recitation of Huyse: the machine renders `kē čihr az yazdān` as "whose form is
from the gods" where the scholarly reading is closer to seed/lineage. The number is
inflated by §20, a list of twelve province names where any two translations must agree.
A formulaic list flatters chrF; worth remembering before reading chrF·ref as accuracy.

### The re-run of the Tamil case — and two defects it exposed

Back-prompt v2 worked: `akananuru-149-oty` came back **in Tamil script**, chrF↺ 0.004 →
**0.333**, cos↺ 0.573 → **0.699**. The verse profile finally has a real measurement.

But the run output also said `rows: 9` and `by_band` moved from {high 5, medium 4} to
{high 6, medium 3}. Nine rows, and one of them had changed. Two defects:

**1. The v2 back-translation overwrote the v1 row.** The primary key was
`(chunk_id, target_lang, translation_model, prompt_version)` — where `prompt_version` is
the *forward* prompt. `back_prompt_version` was stored but left out of the key, so the
newer back prompt silently destroyed the evidence produced by the older one. The whole
argument for recording a prompt version is that output from two prompts is not
comparable; a key that omits one of the two versions concedes the argument. Widened to
include it, with an idempotent `DO $$` migration for the existing table, and a test that
compares the PK column set against the `ON CONFLICT` column set — a drift between those
two raises only at execution time, which parse-level checking cannot reach. Both
mutation-verified.

**2. A one-case run replaced the nine-case baseline.** `--case akananuru-149-oty`
rewrote `eval/translation_check_last_run.json` with a single result. The file did what it
says on the tin; the mistake was doing calibration from a file whose contract is "most
recent invocation". Runs are now also archived to `eval/runs/<timestamp>-<scope>.json`,
with the model and both prompt versions recorded in the payload.

### The thresholds were low for one traceable reason

Four profiles, four `cos_high` values below the observed distribution — the third and
fourth caught only because re-banding showed ŠKZ and then Akanāṉūṟu jumping to `high`.
The common cause: every provisional threshold was anchored on the **Part 4 retrieval**
numbers (English→Greek 0.49-0.52, same-language query-to-document 0.61-0.68). But this
check compares two renderings of the *same passage in the same language*, which is a much
easier problem and lands far higher. Recorded as `threshold_origin` in the profiles file.

Where a profile has enough cases to speak for itself (prose, n=5) the correction is
calibration. Where it does not (documentary and verse at n=1, inscription at n=2) it is
an analogy applied to a still-uncalibrated profile, and `calibrated` stays false. Current
bands under the corrected thresholds:

| | prose | inscription | documentary | verse |
| --- | --- | --- | --- | --- |
| high | muziris-54, muziris-56, frankincense-28, hou-hanshu | — | muziris-papyrus | — |
| medium | weilue | skz, jabal-dabub | — | akananuru-149 |

**Bands are genre-relative and not comparable across profiles.** A `high` on verse (cos
0.699) and a `high` on prose (cos 0.967) do not describe the same strength of evidence.
Part 7 must not rank or filter across genres on the band alone; noted in the profiles
file as `cross_profile_warning`.

### What changed since the run

`answer/confidence.py` (script_mismatch), `answer/translate.py` (native-script rule,
prompt v2), `eval/gold/confidence_profiles.json` (recalibrated, with the reasoning),
`eval/gold/translation_cases.json` (**9 → 12 cases**: Nabataean epitaph and Vimose runes
to give `inscription` n=4, Adulis §4 to give `prose` a sixth case and a second region).
Offline suite is 104 assertions, all passing, with mutation-verified guards on every fix above.

## Part 6 — full gold-set run (2026-08-10, 12 cases)

`rows: 20` — 9 old + 12 new − 1 overlap. The key migration fired and the v1 evidence
survived, as intended.

| case | band | chrF↺ | cos↺ | chrF·ref | cos·ref | |
| --- | --- | --- | --- | --- | --- | --- |
| muziris-54-grc | high | 0.572 | 0.969 | 0.583 | 0.938 | |
| muziris-56-grc | high | 0.552 | 0.964 | 0.490 | 0.924 | |
| frankincense-28-grc | high | 0.553 | 0.937 | 0.275 | 0.756 | |
| adulis-4-grc | high | 0.465 | 0.943 | 0.427 | 0.836 | |
| weilue-lzh | medium | 0.213 | 0.874 | 0.209 | 0.808 | |
| hou-hanshu-lzh | high | 0.631 | 0.968 | 0.255 | 0.874 | |
| akananuru-149-oty | medium | 0.016 | 0.660 | 0.335 | 0.682 | wrong script |
| skz-xpr | medium | 0.182 | 0.896 | 0.653 | 0.960 | |
| jabal-dabub-xsa | medium | 0.113 | 0.767 | 0.336 | 0.897 | |
| raqosh-xna | medium | 0.237 | 0.789 | 0.135 | 0.771 | |
| vimose-gmq-pro | **low** | 0.981 | 0.997 | 0.231 | 0.719 | **FAIL** untranslated_echo |
| muziris-papyrus-grc | high | 0.512 | 0.894 | 0.442 | 0.863 | |

**The harness produced its first genuine failure, and it was right.** Three further
defects came out of the same run.

### 1. The Vimose FAIL was a corpus defect, not a translation defect

The model was handed `original_text_excerpt` and returned it verbatim — chrF 0.981
against its own source. Correct behaviour, because the field was an **English catalogue
listing** with runic transliterations embedded in it: "Vimose Comb (c. 160 CE, oldest
known datable runic inscription): harja …".

That prose was in the retrieval index labelled `lang=gmq-pro`, retrieval-eligible and
embedded. A Part 7 citation could have quoted a museum label as if it were an
inscription — the precise failure the Part 3 fidelity classifier exists to prevent. It
passed because `english_marker_ratio` counts function words, and catalogue prose has
almost none. **Known blind spot, now documented**; the echo flag is the current backstop,
one layer downstream of where it should be caught.

Record restructured: the field holds the six transliterations only, one per line; object
identification, dates and the comb's runes moved to `notes` and a new `object_sequence`.
Verify passes, still `transliteration` / eligible / one chunk.

### 2. The script check was measuring the wrong distinction

Akanāṉūṟu came back **95% Devanagari with a scattering of Tamil letters** — and the
`script_mismatch` flag, added that morning for this exact case, said nothing, because it
tested Latin against non-Latin and both sides were non-Latin. Devanagari answering a
Tamil source is exactly as wrong as romanisation.

Now compares the **dominant Unicode script family** (first token of the character name:
TAMIL, DEVANAGARI, GREEK, CJK, LATIN). Re-checked against every case in the archived run:
flags Akanāṉūṟu, and nothing else — no false positives on the four romanised records where
both sides are legitimately LATIN.

Consequence: **the verse profile still has no valid measurement.** Two runs, two invalid
results (romanisation, then Devanagari). Both would now be blocked rather than reported as
`medium`.

### 3. Calibration statistics were being drawn from a failure

The `observed by profile` block reported `inscription n=4, chrF↺ 0.113-0.981` — where
0.981 *is the echoed Vimose case*. A blocked case is not a measurement, and it was
feeding the numbers used to decide what success looks like. Blocking-flagged cases are now
excluded from the summary, with a count of what was dropped.

### 4. Temperature 0 is not determinism — and the variance is large

Same case, same prompt version, same model, two runs:

| case | run A | run B | spread |
| --- | --- | --- | --- |
| akananuru-149-oty | chrF 0.333 | chrF 0.016 | **0.317** |
| hou-hanshu-lzh | chrF 0.579 | chrF 0.631 | 0.052 |
| muziris-54-grc | chrF 0.565 | chrF 0.572 | 0.007 |

A 0.317 spread within one case is larger than the gap between two profile thresholds.
**Any threshold set from a single shot is measuring one sample of a distribution nobody
has looked at.** Added `--repeat N`, which runs each case N times and prints the per-case
spread plus a `BAND UNSTABLE` marker where repetitions land in different bands.

Note the pattern in the table: the well-attested Greek prose is nearly deterministic, the
Chinese moves a little, and the Old Tamil — the language the model handles worst — moves
enormously. Variance looks like a proxy for competence, which if it holds up is a cheaper
confidence signal than the round trip itself. Worth testing properly in Part 8.

## Part 6 — variance run and the untranslatable case (2026-08-10, third session)

### Vimose echoes on a clean field — and that is the answer

The restructured record went in (50 chunks, 1 re-embedded) and the model **still returned
the runic text verbatim**, chrf_echo 1.00. With the English scaffolding gone, that is no
longer a corpus defect: six short, partly undeciphered sequences — the published gloss
itself reads "likely", "possibly", "remain only partially deciphered" — carry too little
context to translate, and returning them unchanged is the correct behaviour.

So the case was **reclassified rather than fixed**. The gold set now has
`expect_untranslatable`, and this case passes when the pipeline **refuses**, failing if a
clean translation ever appears. The inversion is the point: a confident English rendering
of an undeciphered runic sequence is the worst output this system could produce, because
it would arrive attached to a citation. If a future model produces one, this case fires
and someone has to decide whether the reading is real or invented.

Declaring a source untranslatable requires setting `expect_no_blocking_flags: false`
explicitly — it is a claim about the material, and the loader refuses to let it be
inherited from a default.

**Part 7 consequence:** filtering on `confidence_band` alone is not enough. This row is
stored with band `low` *and* a blocking flag, and the flag is what says "present the
source and the published gloss, never a machine translation".

### The variance run, which is the most useful data so far

Three repetitions of four cases, same prompt, same model, temperature 0:

| case | source chars | chrF↺ range | spread | cos↺ spread |
| --- | --- | --- | --- | --- |
| muziris-56-grc | 919 | 0.546-0.555 | 0.009 | 0.003 |
| muziris-54-grc | 572 | 0.563-0.575 | 0.012 | 0.003 |
| frankincense-28-grc | 476 | 0.545-0.557 | 0.012 | 0.003 |
| weilue-lzh | **52** | 0.213-0.306 | **0.093** | 0.001 |

No band changed across any repetition, which is the reassuring part. But chrF on the
52-character Chinese notice moves nearly eight times as much as on the Greek passages,
and **cosine barely moves at all anywhere** (≤0.003).

This corrects the earlier hypothesis in this file. After the first run I wrote that chrF
is *script*-sensitive, because Literary Chinese scored 0.213 against 0.579 on comparable
work. The variance data says the driver is **length**: both Chinese chunks are the
shortest in the corpus (52 and 36 characters), and a short text has few character n-grams,
so one word choice moves the score. The two long Greek passages and the long Chinese-free
prose are all stable. Script may still matter, but length dominates and was the
confounder.

Acted on: `short_source_chrf_noisy`, a **non-blocking** flag below 150 characters, with
the measured numbers in the note. It does not change the band — verified by a control that
holds chrF and cosine constant and varies only length.

**The division of labour between the two signals is now clear.** Cosine is stable and
compressed: reliable, weakly discriminative, and the right thing to band on. chrF is
discriminative but noisy, and its noise is a function of length. Reading chrF closely on a
40-character inscription was never going to work.

## Part 6 — RESULT ✅ (2026-08-10)

**12/12 cases meet their expectations**, including `vimose-gmq-pro` passing by being
correctly refused. Final run:

| case | band | chrF↺ | cos↺ | chrF·ref | cos·ref | flags |
| --- | --- | --- | --- | --- | --- | --- |
| muziris-54-grc | high | 0.563 | 0.965 | 0.564 | 0.938 | |
| muziris-56-grc | high | 0.554 | 0.963 | 0.490 | 0.924 | |
| hou-hanshu-lzh | high | 0.631 | 0.971 | 0.254 | 0.873 | short source |
| muziris-papyrus-grc | high | 0.478 | 0.905 | 0.440 | 0.859 | |
| frankincense-28-grc | medium | 0.553 | 0.937 | 0.275 | 0.756 | |
| adulis-4-grc | medium | 0.486 | 0.925 | 0.418 | 0.837 | |
| weilue-lzh | medium | 0.309 | 0.899 | 0.205 | 0.796 | short source |
| skz-xpr | medium | 0.193 | 0.902 | 0.653 | 0.960 | semantic_ok_lexical_low |
| raqosh-xna | medium | 0.237 | 0.789 | 0.135 | 0.771 | |
| jabal-dabub-xsa | medium | 0.113 | 0.768 | 0.336 | 0.896 | short source |
| akananuru-149-oty | medium | 0.328 | 0.696 | 0.309 | 0.711 | |
| vimose-gmq-pro | low | — | — | — | — | **untranslated_echo (expected)** |

### The last defect: a band that changed when nothing did

`adulis-4-grc` banded `high` (cos 0.943) in one run and `medium` (0.925) in the next on
identical input, against a threshold of 0.93. Pooling every prose observation on disk —
24 of them across five archived runs — showed why:

```
0.874 0.874 0.874 0.875 0.899 | 0.925 0.936 0.937 0.937 0.939 0.939 0.943 | 0.962 … 0.971
```

Three clusters, no natural binary split, and 0.93 landed in a narrow gap beside a case
that oscillates across it. Moved to **0.95**, where no observed case straddles: everything
at or above 0.962 is stably high, everything at or below 0.943 stably medium. Re-banding
all five archived runs under the new thresholds gives **zero unstable cases**.

**The stability criterion is the reusable lesson**: place a threshold where no observed
case crosses it, and confirm with `--repeat`. The cost is that two sound translations
(0.925-0.943) now read `medium`; that is a deliberate decision about what `high` should
mean — reserved for the top cluster so the band carries signal — not something the data
decides by itself.

### Part 6 milestone, honestly stated

The loop works: a non-English chunk is retrieved, translated, translated back without the
model seeing the original, scored on two independent signals, banded against a
genre-specific profile, and stored with the model, both prompt versions and a hash of the
source text. Ten languages' worth of behaviour is now characterised rather than assumed.

What it does **not** yet do: tell you whether a translation is *accurate*. The round trip
measures self-consistency, and a model can mistranslate a passage and mistranslate it back
the same way. `chrf_ref` against a published translation is the only accuracy signal here,
it exists for 16 of 24 records, and on ŠKZ it is inflated by a formulaic province list.
Part 8 owns that gap.

Six defects were found by running it, none by writing it: a false PASS on script mismatch,
a too-coarse fix for that false PASS, a primary key that let one prompt overwrite
another's evidence, calibration statistics drawn from a failure, a corpus record with
English prose indexed as Proto-Norse, and a band that moved on identical input. The
offline suite is 104 assertions with a mutation-verified guard for each.

### To re-run

```powershell
python -m answer.test_translate                              # 104 assertions
python -m eval.run_translation_check                         # all 12, ~24 calls
python -m eval.run_translation_check --repeat 3 --limit 4    # variance
```

Note that `--repeat` results are **not** all persisted: every repetition of a case shares a
primary key, so the last one wins in `chunk_translations`. The full set lives in
`eval/runs/<timestamp>-*.json`, which is what calibration should read.

## Part 7 — starting point (for the next thread)

**State:** Parts 1-6 complete and verified. 24 documents → 50 chunks → 48 embedded with
`voyage/voyage-3.5`. Retrieval: 11/11 probes at rank 1. Translation: 12/12 gold cases,
20 rows in `chunk_translations`, bands stable across five archived runs.

Goal: assemble a grounded answer with inline citations, where every claim traces to a
chunk, and every chunk traces to characters on disk.

### What Part 6 hands you

- `current_translations` — the view to read. It serves only translations whose source
  hash still matches the chunk, so a translation of superseded text can never be cited.
- Each row carries `confidence_band`, `flags`, `confidence_profile`, both prompt versions,
  the translation model, and the scoring embedding model.
- `retrievable_chunks` — the retrieval surface, already excluding the two held-back
  pointer chunks. A Part 3 placeholder cannot be retrieved or cited by construction.
- `answer/align.py` — pairs an original with the right passage of its published
  translation, and reports whether that pairing rests on section markers, position, or
  nothing.

### Decisions Part 7 has to make

1. **A blocking flag outranks the band.** `vimose-gmq-pro` is stored `low` *with*
   `untranslated_echo`. Filtering on band alone would present a machine "translation" of
   undeciphered runes. The rule needs to be: blocking flag → show source and published
   gloss only, never machine English.
2. **Bands are genre-relative and must not be compared across profiles.** A `high` on
   verse (cos 0.70) and a `high` on prose (cos 0.96) are not the same evidence. If the UI
   ranks or filters on band across genres, it is asserting something false.
3. **What a `medium` band looks like to a reader.** Nine of twelve cases are `medium`.
   This is the common case, not the exception, and a cited translation with unstated
   confidence is worse than no confidence score at all.
4. **Whether to cite a machine translation at all when a published one exists.** 16 of 24
   records have a human translation. The interesting question is what to do for the other
   8 — and `answer/store.py` already knows which is which.

### Known gaps, carried forward honestly

- **Self-consistency is not accuracy.** The round trip cannot catch a passage
  mistranslated the same way twice. `chrf_ref` is the only accuracy signal, exists for
  16 of 24 records, and is inflated by formulaic text (ŠKZ scores 0.653 largely on a list
  of twelve province names). **This is Part 8's central problem.**
- **ŠKZ is scored against the wrong rendering.** The record holds both a heterographic
  transliteration and a phonemic transcription; the model back-translates into the latter
  while chrF compares against the former, costing roughly 0.4 for no reason connected to
  translation quality. Needs a per-record "comparison target" the schema does not yet have.
- **Three profiles are uncalibrated** — `documentary` and `verse` at n=1, `inscription`
  at n=3 — because the corpus contains one papyrus and one poem. Their thresholds come
  from a systematic correction, not from measurement, and `calibrated: false` says so.
- **Old Tamil is the weakest language in the stack.** One attempt in three came back in
  the wrong script, and it scored lowest of any script in the Part 4 retrieval check
  (0.368). Whatever Part 7 claims about Tamil sources should be weaker than what it
  claims about Greek.
- **Two records still held back** (Palmyrene Tariff, Ezana Stone) as `pointer`. Neither
  blocks Part 7; both would be promoted automatically if their text is ever pulled.

### Standing lessons from Parts 3-6

- Parse-level SQL checks miss type inference. Anything with optional/NULL parameters needs
  one execution against the real database.
- A test that passes for the wrong reason is worse than one that fails. Assert on the
  specific thing, not a proxy for it.
- Every defect in Part 6 was found by running the thing, not by writing it. Six of them,
  each now carrying a mutation-verified guard.
- Place a threshold where no observed case straddles it, then confirm with `--repeat`.
  A band that moves when the input did not is worse than a coarse one.
- Provisional numbers get anchored on whatever is nearby. All four confidence profiles
  were set too low because they borrowed from Part 4's cross-lingual similarities, which
  measure a different and harder thing.
- The gateway's free tier is 3 requests/minute. Batch aggressively.
- Two PowerShell windows, both needing `cd` + venv activate + `.env` load. The gateway
  reads keys only at startup.

## Part 7 — what's in place (built 2026-08-10, not yet run live)

Written and passing every offline check (**101 assertions, no network, no database**),
with **13 regression guards, all mutation-verified** — each one was checked by breaking
the code it protects and confirming that guard, and not merely *some* guard, failed.
**The live run is yours to execute on the host.** See "To run" at the end.

### Code

| File | Role |
| --- | --- |
| `scripts/schema-part7.sql` | `citable_passages` view (built on `retrievable_chunks`), `answers` + `answer_citations`, `answer_provenance`, `answers_citing_flagged_translations`. Idempotent. |
| `answer/evidence.py` | Which English a reader may see, and what must be said about it. Pure — no DB, no network. |
| `answer/answer_store.py` | Part 7 database layer: hydrate hits to citable passages, read `current_translations`, write answers and citations. |
| `answer/cite.py` | Evidence-block and sources-block rendering, and the six grounding checks. Resolves quotations to absolute characters on disk. |
| `answer/assemble.py` | The pipeline, the versioned grounding prompt, and answer persistence. |
| `answer/run_answer.py` | CLI: `--dry-run`, `--k`, `--max-sources`, `--lang`, `--region`, `--no-write`, `--json`, `--stats`. |
| `answer/test_answer.py` | 101 offline assertions; 13 mutation-verified guards. |

### The four decisions Part 6 left open, and how they were taken

1. **A blocking flag outranks the band.** `resolve_english` reads `blocking_flags`
   before it reads `confidence_band`, and a blocked translation returns
   `kind="none"` carrying the flag name as its reason. No band is low enough to make
   a blocked translation quotable — the point of `vimose-gmq-pro` being stored `low`
   *with* `untranslated_echo` is that band-based filtering still has to decide what
   to do with `low`, and the honest answer is "nothing". A blocked machine
   translation does **not** suppress a published gloss, which is served instead.

2. **Nothing ranks or filters on band.** Evidence order is retrieval order, full
   stop. Ranking on band would compare a `high` on verse (cos 0.70) with a `medium`
   on prose (cos 0.94), which the profiles file already warns in writing is a false
   comparison. Guarded by a test that permutes every band and asserts the ordering
   is unchanged. Ranking by *translation availability* was also rejected: it would
   put the best-served sources first and quietly bury the ones the corpus handles
   worst, which is the opposite of what this project is for.

3. **`medium` is the common case, so its caveat carries numbers.** Nine of twelve
   Part 6 cases banded medium; boilerplate would be attached to most of the corpus
   and read as decoration within a page. Every machine translation reaches the
   reader as `MACHINE TRANSLATION — confidence medium (prose profile)` followed by
   the observed cosine, the threshold it fell short of, and — where the profile is
   uncalibrated — the fact that the threshold is an analogy rather than a
   measurement. The Part 6 limit is restated every time: self-consistency is not
   accuracy.

4. **Published wins; machine is the fallback.** Preference order is: the chunk is
   already English → a published translation *aligned to this passage* → a Part 6
   machine translation → a published translation of the *document* that could not be
   aligned → nothing. The one non-obvious step is the third above the fourth. A human
   translation is better evidence of accuracy; a passage-aligned translation is
   better evidence of *what this passage says*. Quoting a document-level human
   translation beside a §-numbered citation attributes words to a passage that may
   not contain them — a mis-citation, which is precisely what this part exists to
   prevent — whereas the machine translation is of the right passage by construction
   and arrives with a band attached.

### Design decisions

- **It does not translate, ever.** Where no English exists the evidence block says
  `ENGLISH: NONE AVAILABLE` in words, with the reason, and the prompt forbids the
  model from supplying one. An inline translation made at answer time would have no
  band, no prompt version, no cache key and no back-translation — and would still
  arrive attached to a citation, which is what makes a wrong translation dangerous
  rather than merely wrong. A silent gap where the English should be is worse than a
  loud one: a model handed a gap fills it.
- **`citable_passages` is built on `retrievable_chunks`, not on `chunks`.** Part 3
  held two records back as `pointer`; Part 4 made the retrieval view exclude them.
  An answer layer querying `chunks` directly would quietly undo both. Everything
  Part 7 can cite is, by construction, a chunk that was eligible *and* embedded.
- **The vector search stays in `retrieve/search.py`.** The first draft of
  `answer_store` reached the embedding through a correlated subquery over the new
  view, which returns identical results with the HNSW index bypassed and no error to
  say so — the Part 4 `<=>` lesson one layer up. Now: rank there, hydrate here. One
  definition of the distance operator in the codebase instead of two that can drift.
- **Original and translation chunks are folded into one source.** They are separate
  rows because Part 3 made them separate — which is what makes the Part 5
  same-query-two-languages test possible — so an English question routinely retrieves
  both halves of one record. Shown as two numbered sources they read as two
  witnesses, which is false. `fold_hits` keeps the original as the anchor and folds
  its English in as the published translation, reusing `align.py` so the alignment
  ground travels to the reader.
- **The answer's identity includes its prompt version and its evidence.**
  `answer_id` is a hash of (question, model, prompt version, ordered chunk ids), for
  the same reason `chunk_translations` widened its key in Part 6: a version that is
  stored but left out of the key lets a new prompt destroy the evidence the old one
  produced.
- **Verification runs twice, deliberately.** Once to learn which markers were cited,
  then the sources block is rendered, then again *against that rendered block* — so
  "a machine translation never reaches a reader without its band" is checked on the
  artifact rather than on the intention.

### The six grounding checks

Nothing here trusts the model. Every result is a fact about strings that can be
recomputed from the database and the seed JSON.

| Check | What it catches |
| --- | --- |
| `unknown_markers` | `[S7]` when six sources were supplied. A citation resolving to nothing looks exactly like one that resolves to something. |
| `uncited_sentences` | The most common way an answer stops being grounded: not a wrong citation, but a fluent connecting sentence out of the model's own knowledge. |
| `unverified_quotes` | Quoted text found in none of the passages it cites. **This is the check that reaches disk** — a verified quote is resolved to `char_start + offset`, an absolute span in the named source field. |
| `misattributed_quotes` | Text that exists in the corpus but not in the source it was hung on. Worse than an invented quote, because it survives a spot check. |
| `claims_on_untranslated` | A claim resting on a passage with no English. Citing one is allowed **only** with a verbatim quotation of it in the same sentence. |
| `unlabelled_machine` | A machine translation reaching the reader without its band. |

Quote matching is whitespace-insensitive, for the same reason chrF is: Literary
Chinese has no word spaces, so a whitespace-sensitive check would hold Greek and
Chinese to different standards. Where an exact match fails, a Unicode-NFC match is
tried and the quote is marked **verified but unresolved** — NFC can merge codepoints,
so the offset is no longer trustworthy, and a span that might be wrong is worse than
no span.

### What `claims_on_untranslated` is really for

The Vimose case, carried forward. Six short, partly undeciphered runic sequences whose
own published gloss reads "likely", "possibly", "remain only partially deciphered". A
confident English reading of those, arriving attached to a citation, is the worst
output this system could produce. So: quoting `"harja"` verbatim is allowed and still
resolves to characters on disk; writing *"an inscription meaning 'Harja made this
comb'"* fails the answer. Guarded, and mutation-verified.

### Known gaps, carried forward honestly

- **Self-consistency is still not accuracy.** Unchanged from Part 6 and still Part 8's
  central problem. Part 7 surfaces the limitation in every machine-translation caveat
  rather than closing it.
- **The claim-sentence rule is a heuristic.** A sentence is held to need a citation if
  it has five or more words and does not end in a colon. Deliberately crude — a
  cleverer splitter that merged two sentences would let the second ride on the first
  one's marker — but it will occasionally demand a citation for a transition. Watch
  the first live run for false positives before loosening it.
- **`answers_citing_flagged_translations` should be empty.** It is a view over answers
  that cited a machine translation carrying any flag. Non-empty means a citation was
  made that should not have been. Check it after every run.
- **ŠKZ is still scored against the wrong rendering** (heterographic transliteration vs
  phonemic transcription), so its band understates it. Part 7 shows the band as it is
  rather than correcting it here; the fix is a per-record comparison target the schema
  does not yet have.
- **Old Tamil weakness is now surfaced, not fixed.** `RETRIEVAL_LANG_NOTES` attaches
  the Part 4 measurement (0.368 against 0.61-0.68 for the other scripts) to any Tamil
  passage, because that fact is invisible in the band.

### To run (Windows / PowerShell, repo root, gateway up on :4000, db up)

```powershell
python -m answer.test_answer                 # 101 offline assertions, no API calls
python -m answer.run_answer --dry-run "What did ships carry from Muziris?"
python -m answer.run_answer "What did ships carry from Muziris?"
python -m answer.run_answer --json "How did Roman sources describe Da Qin?" > answer.json
python -m answer.run_answer --stats
```

Cost is **one embedding request and one chat call per question**. `--dry-run` spends
the embedding only, and is the one worth running first: it prints the resolved evidence
with each passage's English kind, band, flags and alignment ground before any chat call
is made.

Exit codes: `0` grounded, `1` answered but failed a check, `2` could not run. An
ungrounded answer is printed and stored anyway — hiding it would remove the only
evidence Part 8 has to work from.

### Questions worth asking first

Chosen to exercise different paths rather than to flatter the system:

- *What did ships carry from Muziris?* — the best-served case: Greek original, Schoff's
  published English, section-aligned, four chunks either side.
- *How did Chinese sources describe the Roman empire?* — machine translation on a short
  source, `short_source_chrf_noisy`, `medium` band. This is what most of the corpus
  looks like.
- *What do the Vimose runes say?* — should refuse, or quote and attribute without
  claiming a meaning. If it produces a confident reading, `claims_on_untranslated`
  fires and the answer exits 1.
- *What did Rome trade with the Kingdom of Aksum?* — the Ezana Stone is one of the two
  held-back `pointer` records, so this tests that the answer says the corpus does not
  cover it rather than reaching for something adjacent.
- *When was the Antikythera mechanism built?* — outside the corpus entirely. Should
  return the refusal sentence verbatim.

## Part 7 — first live run (2026-08-10, 5 questions)

All five exited `1`. **Four of the five failures were this file's fault, not the
model's**, and they share one root cause. The banner's own advice held: read which check
failed before touching the prompt.

### What worked, which is most of the part

Evidence resolution behaved exactly as designed on real retrieval. `english=published
ground=section` on the Muziris Greek; `english=machine band=high ground=passage` on
Periplus §27-29; `english=none` on Adulis §6 carrying the full refusal-to-translate
reason; the Old Tamil `RETRIEVAL_LANG_NOTES` line attached to Akanāṉūṟu wherever it
surfaced. `citable_passages` reported **48** against 50 chunks — the two `pointer`
records are unreachable through the view stack, and neither appeared in any of the 30
retrieved sources. Folding worked: no record was presented as two witnesses.

**The Vimose question did not produce a confident runic reading.** It hedged in the
published gloss's own terms. That was the failure mode this part exists to prevent.

### One root cause, four symptoms

`split_sentences` cut inside quotations. Everything else followed, because
`extract_quotes` then ran **per sentence**: each fragment held an odd number of quote
marks, so the regex paired the *close* of one quotation with the *open* of the next and
reported the prose between them as quoted text the model had fabricated.

| Symptom | Where it showed |
| --- | --- |
| split at `c. ` inside a quotation | Vimose: `UNCITED CLAIM: ... from "c.` |
| split at `Berbers... ` inside a quotation | Aksum |
| phantom quotations from the gaps | `'or'`, `'and'`, `'[S1], and'`, `'with some readings offered as'` |
| markers orphaned after the full stop | `... toward Egypt. [S6]` — so `'Gangetic nard'`, cited correctly to S6, was reported **misattributed** |
| under-splitting on `." [S1] ` | a visibly four-sentence Muziris answer reported `claim sentences 1` |

**The worst consequence was on the check that matters most.** In the Aksum answer the
model quoted S4's Greek verbatim — `Φέρεται δὲ ἀπὸ τῶν τόπων ἐλέφας καὶ χελώνη καὶ
ῥινόκερως` — which is precisely the case `claims_on_untranslated` permits. The quotation
was never extracted, so the check fired on a correct answer. A string bug defeating the
part's central safeguard.

### Three further defects

**1. The refusal sentence failed itself.** `The sources retrieved do not answer this
question.` was flagged `UNCITED CLAIM` in three of five answers. The Antikythera question
— out of corpus, refused, nothing cited — did the textbook-correct thing and scored 0%
coverage. `NO_ANSWER` now lives in `cite.py` as `REFUSAL_SENTENCE` and is exempt in
`is_claim`; `assemble.NO_ANSWER` is an alias, so the two cannot drift.

**2. Not one quotation resolved to characters on disk, in any of the five answers.**
`quotations verified: 2 (0 resolved)`. Every verified quote matched the *English*, and
`locate_quote` claimed no span for English on the grounds that "a translation is not a
file offset". True of a machine translation; **false of a published one**, which is a
chunk of the same seed record with its own `source_field` and `char_start`. `fold_hits`
had the record in hand and passed only its text forward. `Passage` now carries
`translation_chunk`, and a quote from a published translation resolves to
`reference_translation [start:end]`. Machine translations still claim no span — they are
in `chunk_translations`, not in any file, and that distinction is now the reason rather
than an oversight.

**3. Two floors on quote length, drifting apart.** `_QUOTE_RE` required three characters
*inside* the marks, which rejected `"大秦"` as too short while accepting `" or "` as long
enough. One floor now, in `_is_substantive`, script-aware: two characters if non-Latin,
three otherwise, and never a bare function word.

### What the mutation run found that writing the tests did not

Seven mutations, each expected to break one guard. **Three came back MISS**, and each
miss was informative:

- Disabling quotation-tracking, and disabling the abbreviation list, *each* left the
  `c. 160-300 CE` case passing — two independent mechanisms protect it, so neither
  mutation changed anything. Split into two cases that only one mechanism each protects:
  an ellipsis inside a quotation, and an abbreviation outside one.
- Reverting to per-sentence extraction alone changed nothing either, because fixing the
  splitter restores correct parity by itself. The bug **as shipped** needs all three
  reversions at once, and its falsifiable symptom is the Aksum false positive, not the
  phantom quotes.
- Removing the function-word floor changed nothing, because `"or"` is two characters and
  the length floor caught it anyway. Test string changed to `"and"`.

One assertion is deliberately **not** marked GUARD: no single mutation isolates it, and
labelling an unfalsifiable assertion as a guard is the same error as a test that passes
for the wrong reason.

`scripts/mutate_part7b.py` runs all seven and restores `cite.py` afterwards.

### Genuine model failures, correctly caught

Two survive the fixes and should:

- `'the tribute brought was neither precious nor rare...'` cited to the Hou Hanshu, whose
  chunk is **36 characters** of Literary Chinese. The model is reciting Hill's published
  translation from its own knowledge.
- `'arriving with gold and departing with pepper'` — the familiar Kulke rendering of
  Akanāṉūṟu 149, not present in the supplied passage.

`unverified_quotes` doing exactly its job: fluent, plausible, accurate-sounding, and not
from the evidence.

Replaying the live Muziris answer through the fixed verifier now yields four sentences
with markers S1, S1, S5, S6 and `'Gangetic nard'` attributed to S6.

### Offline state

**Part 7: 115 assertions**, up from 101. **Seven new guards**, each mutation-verified by
`scripts/mutate_part7b.py`, on top of the 13 from the build. Part 6's 104 still pass
unchanged.

### To re-run

```powershell
python -m answer.test_answer                 # 115 assertions
python scripts/mutate_part7b.py              # 7 mutations, restores cite.py
python -m answer.run_answer --dry-run "What did ships carry from Muziris?"
```

Then all five questions again. **Do not change the prompt yet** — four of five failures
were in the checker, so the model's real error rate is not yet known. Read
`answers_citing_flagged_translations` after each run; it was not checked after the first.

## Part 7 — second live run (2026-08-10, same five questions)

**Aksum exits 0** — the first grounded answer this project has produced. And
**quotations now resolve to characters on disk**: 4/4, 3/3, 1/1, 2/2, with real spans
(`reference_translation[1981:2072]`, `original_text_excerpt[1902:1958]`). That was the
one failure mode the offline tests could not rule out — a hand-built `Passage` passing
while the real `build_evidence` path never produced a `translation_chunk` — and the live
run settles it.

### Every unverified quotation, checked against the seed JSON

Seven across the run. **One was a fabrication.**

| Quotation | In the corpus? | Cause |
| --- | --- | --- |
| `arriving with gold and departing with pepper.` | yes, source ends `pepper—` | terminal period pulled inside the marks |
| `the tribute brought was neither precious nor rare…` | yes, source reads `The tribute` | lowercased to fit mid-sentence |
| `several inscriptions remain only partially deciphered.` | yes, source reads `Several` | lowercased |
| `mariha … makija: possibly 'Mari…Alla',` | yes, source ends `Alla'.` | comma for period |
| `earliest datable Elder Futhark runic texts` | the record's **title** | quoted the evidence header |
| `c. 160-300 CE (Roman Iron Age in Scandinavia),` | the record's **date_text** | quoted the evidence header |
| `outer walls of the city made of stone.` | **nowhere** | genuine fabrication |

**Four false fabrications from case and edge punctuation.** `locate_in_text` was
whitespace-insensitive and case- and punctuation-*sensitive*, which held a quotation to a
standard no writer meets: the three things a writer alters to fit a quotation into a
sentence of their own are exactly whitespace, opening capital, and terminal punctuation,
and none of them changes what was quoted. Matching now folds case and strips
`_EDGE_PUNCTUATION` from the quotation's edges. `_fold` is length-preserving by
construction — `str.lower()` is not, and the index map in `_collapse_with_map` is only
truthful while length is, so a naive `.lower()` would have silently shifted every offset.

**This corrects a claim made in this file after the first run.** The Akanāṉūṟu quotation
was recorded as the model reciting Kulke from memory. It was not: the text was in the
passage the whole time, one period away from matching. A checker that misreports a
correct quotation as a fabrication is worse than one that misses a fabrication, because
it is the kind of failure that gets "fixed" by loosening the model's instructions.

### Metadata is not evidence — `quoted_metadata`

Two quotations came from the evidence block's **header line**: the record's title and its
`date_text`. Reporting these as fabrications misdescribes what happened — the model
copied them faithfully from what it was handed.

They are now their own check, and they still fail the answer. The reason is the Vimose
lesson one layer up: `The Vimose inscriptions — earliest datable Elder Futhark runic
texts` is a title **written by this corpus's editors**. Quoting it presents an editorial
description as a source, which is precisely what the Part 3 fidelity classifier exists to
prevent and what Part 3b caught when English catalogue prose was sitting in the index
labelled `lang=gmq-pro`. Making the title quotable would have been the easy fix and the
wrong one. Rule 3 of the prompt now says the header line is not quotable.

### The one genuine prompt failure

Antikythera did **not** reach exit 0, and the prediction that it would was wrong. The
refusal exemption worked — claim sentences went 2 → 1 — but the model added a second
sentence characterising the corpus with no marker. Rule 6 already permitted one further
sentence "with citations"; it now says so unmissably, and says to stop after the refusal
if the sentence cannot be cited.

`ANSWER_PROMPT_VERSION` is bumped to **`p7-answer-v2`** rather than edited in place. It is
part of `answer_id`, so the v1 answers stay readable instead of being overwritten by
output from a different prompt — the same argument that widened the Part 6 translation
key. **Re-running now writes new rows rather than replacing the v1 ones.**

### What the mutation run found this time

Two of the three new mutations came back MISS, both for the same reason: the NFC fallback
in `locate_quote` also folds and strips, so it caught what the exact path had dropped and
the guards passed anyway. The guards now assert `match == "exact"`. That distinction is
worth asserting on its own account — an NFC match claims no character offset, so a
quotation verified that way is a weaker result than these deserve.

**Offline state: 124 assertions, 10 mutation-verified guards.** Part 6's 104 unchanged.

### To re-run

```powershell
python -m answer.test_answer                 # 124 assertions
python scripts\mutate_part7b.py              # 10 mutations, restores cite.py
```

Then the five questions again. What to expect, so the run can falsify the fixes:

- **Muziris, Chinese, Vimose** should lose their false fabrications. The Weilüe's `outer
  walls of the city made of stone` should **remain** unverified — if it passes, the
  matcher has been loosened too far.
- **Vimose** should now report `QUOTED METADATA`, not `UNVERIFIED QUOTE`, for the title
  and date — or, if rule 3 lands, not quote them at all.
- **Antikythera** should reach exit 0, or fail again in the same place, which would say
  the rule-6 wording is not the binding constraint.
- **Aksum** should stay at 0.

## Part 7 — third live run (2026-08-10) — 3/5 grounded

| Question | Exit | Verdict |
| --- | --- | --- |
| Muziris | **0** | 4 claims, 4 cited, **5 quotations, 5 resolved to disk** |
| Chinese sources | 1 | one fabricated quotation — genuine |
| Vimose | **0** | 3 claims, **7 quotations, 7 resolved to disk** |
| Aksum | 1 | `claims_on_untranslated` — correct, and caused by the v2 prompt |
| Antikythera | **0** | refusal + one cited coverage sentence |

Three of four predictions held. **The matcher was not loosened too far**: `outer walls of
the city made of stone` is still reported unverified, and it is still the only genuine
fabrication in three runs. The four false fabrications are gone; the real one remains.

**No `QUOTED METADATA` fired.** The check was written and the prompt rule was written in
the same pass, and the prompt rule was sufficient — the model stopped quoting the header
rather than being caught doing it. The check stays as the backstop, currently unexercised
in the wild.

### Vimose is the best result this project has produced

Seven quotations, every one resolved to characters on disk, and the answer presents the
hedges *as hedges*: `"harja," which is "likely a personal name or 'comb'/'warrior'"`. The
runic sequence resolves to `original_text_excerpt[0:5]` and the gloss to
`reference_translation[7:48]` — two different fields of the same record, correctly
distinguished. This is the record that failed Part 6 as an untranslatable echo, and the
answer layer now quotes it without ever claiming a reading of it.

### The Aksum regression, which was the prompt's fault and not the model's

Aksum went 0 → 1. The model did not quote S4 this time; it wrote a characterising
sentence — "they detail what Rome imported from Aksum" — and cited `[S1][S4]`. S4 has no
English. `claims_on_untranslated` fired, and **it was right**: describing what an
untranslated Greek passage covers is saying what it means, which is the one thing this
part exists to stop.

But the model was following instructions. **v2's rule 6 conflicted with v2's rule 4**:
rule 6 told it to cite the sources it was characterising, and the set it was
characterising contained a passage it could not read. Antikythera passed the same rule
only because none of its six sources was untranslated. A rule that is safe when the
corpus happens to be well-served is not safe.

Resolved in rule 4's favour at **`p7-answer-v3`**: cite only sources you can read, do not
name a `NONE AVAILABLE` source in the coverage sentence, and if that leaves nothing
citable, stop after the refusal. The alternative — relaxing `claims_on_untranslated` when
a sentence also cites a readable source — was rejected: a sentence citing `[S1][S4]` is
exactly where a mis-citation would hide, because the readable source lends the unreadable
one its credibility.

**Offline: 125 assertions, 10 mutation-verified guards.**

### Standing observation

Every prompt version has been broken by the run after it, and each break has been a
conflict between two rules rather than a rule being wrong on its own. Worth watching
whether v3 introduces a third one before adding any further rules.

## Part 7 — fourth live run: v3 did not work, and the reason is in the corpus

Antikythera holds at **0**. Aksum is **still 1**, citing `[S1][S4]` in defiance of v3's
new instruction. Two prompt versions have now tried to talk the model out of this and
neither worked, which is the signal to stop editing the prompt and look at the evidence.

**S1 and S4 are two chunks of the same record.** `africa-03-periplus-adulis` holds
original §4–§6 (2,089 chars) against a reference translation covering §4–§5 only (794
chars). Chunk 002 — §6, characters 1170–2089 — has no English partner, so it resolves
`english=none`. The model is characterising one document and citing both of its chunks,
which is reasonable behaviour, and one of those chunks is unreadable.

**This is the Muziris asymmetry again, unclosed.** Part 6 found `periplus-muziris.json`
holding Greek §53–56 against English §53–54 and fixed it by adding Schoff's §55–56. The
Adulis record has the identical defect and it was never caught, because nothing before
Part 7 asked for the English of a specific passage.

**And §6 is the passage that answers the question.** `Φέρεται δὲ ἀπὸ τῶν τόπων ἐλέφας καὶ
χελώνη καὶ ῥινόκερως` — ivory, tortoise-shell and rhinoceros horn exported from these
places — with the imports listed alongside. The corpus contains the answer to "what did
Rome trade with Aksum" and refuses to give it, because the translation stops one section
short.

So the honest verdict on this question is not that the answer layer failed. It is that
**a grounded system correctly refused to read a passage it had no translation for**, and
the fix is to close the gap in the data rather than to loosen the rule that caught it.
`translation_source` already cites Schoff 1912 via ToposText, which is where §55–56 came
from for Muziris — the same public-domain route.

v3 is kept. Its rule is right even though the model ignored it, and Antikythera's coverage
sentence is now stably cited. But **no further prompt rule should be written for the Aksum
case**: three of the last four changes to this system have been attempts to make a rule
cover a hole in the corpus.

## Part 7 — closing the Adulis gap (2026-08-10)

### The corpus defect was worse than a missing section

`africa-03-periplus-adulis` did not merely stop short of §6. Its reference translation
held **§4, §6, §5 — in that order** — each heavily elided with `...`, with an editorial
gloss (`[Aksumites]`) inserted, in 794 characters against 2,089 of Greek. The §6 fragment
it did carry stopped immediately before the exports clause, which is the half of §6 that
answers the question.

Replaced with **Schoff's 1912 translation of §4, §5 and §6 in full and in order**, from
the ToposText digitisation already named in `translation_source`. Two mechanical changes,
both recorded in a new `reference_translation_note`: ToposText's hyperlinks are reduced to
their link text, and runs of whitespace are collapsed. Schoff's spellings and section
numbering stand. Title corrected from `(§4, §6)` to `(§4-§6)`.

Corpus is now **24 documents → 55 chunks**; `ingest.verify` passes.

### Which exposed a real defect in `align.py`

With the full English in place, alignment got *worse* — all three sections dropped to
`ground="none"`. Schoff's §4 is roughly twice the length of the Greek §4, so it becomes
three chunks, and **only the first carries a section marker**. `pair_chunks` required a
marker on *every* translation chunk before it would attempt section alignment, so one long
section anywhere in a record silently disabled section alignment for the whole record.

This was latent from Part 6 and invisible until now: every other paired record in the
corpus is one chunk per side, and Muziris happened to split 4:4. It would have appeared
for any record whose translation is more verbose than its original — which is most
translations out of Greek.

Fixed by making the **section the unit of alignment and the chunk an artefact of length**:
labels are carried forward across continuation chunks, and a section's chunks are merged
before pairing. Originals are deliberately *not* merged — `fold_hits` keys on the retrieved
chunk's own id.

**The merge keeps offsets exact.** The gap between two adjacent chunks is filled with as
many spaces as the characters the chunker dropped between them, so `char_start + offset`
still lands on the right character for text taken from any member. Verified against the
seed JSON: `There are exported from these places ivory` resolves to
`reference_translation[3073:3115]` and round-trips. Quote matching is whitespace-insensitive
anyway, so substituting spaces for the original newlines costs nothing.

Alignment across the whole corpus after the change: Adulis 3×`section` (was 3×`none`),
Muziris 4×`section` (unchanged), every other record unchanged.

### A test that failed for the right reason

The new suite initially failed on `non-corresponding section numbers claim no alignment`.
The assertion was wrong, not the code: with equal counts `pair_chunks` falls back to
positional pairing, which it labels `index` and documents as weaker. The invariant worth
asserting is that it never claims **`section`** on numbers that do not correspond, and that
is what the test now says.

**Offline: 129 assertions, 12 mutation-verified guards.** Part 6's 104 unchanged.

### To run — this one needs a re-ingest and a re-embed

```powershell
python -m answer.test_answer                 # 129 assertions
python scripts\mutate_part7b.py              # 12 mutations
python -m ingest.verify                      # 24 docs, 55 chunks
python -m ingest.run_ingest                  # 50 -> 55 chunks
python -m ingest.run_embed                   # the new English chunks
python -m ingest.run_embed --stats           # expect pending 0
python -m answer.run_answer --dry-run "What did Rome trade with the Kingdom of Aksum?"
```

The dry run is the one that matters: **S4 should now read `english=published
ground=section` instead of `english=none`**. If it still says `none`, the re-ingest did not
pick up the new translation chunks.

Then the question itself. It should stop refusing — the corpus now contains the answer in
English, aligned to the passage, from a named human translator.

### The re-ingest worked, and the dry run caught what the tests could not

24 documents → **55 chunks**, 6 new English chunks embedded in one batch, `pending: 0`,
53 eligible and 53 embedded. And §6 did what closing the gap was meant to do: it is now
**S1 at similarity 0.559**, up from rank 4 at 0.498, with `english=published
ground=section` and the whole of Schoff's §6 attached — imports, exports and sailing
season.

But the same dry run showed **`africa-03-periplus-adulis::translation::005` standing as
its own source at S4**, printing text already inside S1's English. The merge introduced
it: `fold_hits` maps a translation chunk back to its original through the pair, and a
merged section carries only its *first* member's `chunk_id`, so every later member looked
like an orphaned English chunk and became an anchor in its own right. Two numbered
sources, one passage, saying the same thing — exactly the double-counting `fold_hits`
exists to prevent, reintroduced by the fix for a different problem.

`Pair` now carries `members`, the chunks its translation was merged from, and `fold_hits`
registers all of them. Guarded and mutation-verified.

**Worth recording as a method note.** Neither the offline suite nor `ingest.verify` could
have found this: it needs real retrieval to return a mid-section English chunk, which
depends on what the embedding ranks. `--dry-run` cost one embedding request and no chat
call, and it is the third defect it has caught before any answer was generated.

**Offline: 133 assertions, 13 mutation-verified guards.** The folding fix landed: Adulis
appears once, and the freed slot pulled in a sixth distinct record.

An aside worth keeping. That sixth record was **Hou Hanshu 88** — whose 166 CE embassy
offers 象牙、犀角、瑇瑁, elephant tusks, rhinoceros horn and turtle shell, the same three
commodities Adulis §6 exports as ἐλέφας καὶ χελώνη καὶ ῥινόκερως. A Greek merchant's
handbook and a Chinese dynastic history, retrieved together for one English question,
listing the same goods. Nothing asked for that; it is what the project is for, appearing
incidentally in a dry run.

## Part 7 — RESULT (2026-08-10): 4/5 grounded, and the metric is now the problem

| Question | Exit | |
| --- | --- | --- |
| Aksum | **0** | grounded, and **wrong about its own evidence** |
| Muziris | **0** | 3 claims, 3 quotations, 3 resolved to disk |
| Chinese sources | 1 | uncited opening sentence — a real catch |
| Vimose | **0** | grounded by refusing; the v2 run answered it better |
| Antikythera | **0** | refusal + one cited coverage sentence |

`answers_citing_flagged_translations`: **0 rows**. Checked for the first time, and clean —
no answer in any run has cited a machine translation carrying a flag.

### There has never been a fabricated fact

`outer walls of the city made of stone` was recorded in this file across two runs as the
one genuine fabrication in the corpus. **It was not.** Hill's translation reads *"The
outer walls of the city **are** made of stone."* The model dropped one word while
compressing the quotation to fit its sentence. The earlier check searched for the model's
wording, not Hill's, and concluded the text was absent.

So across four live runs: **zero invented facts.** Every failure was a checker defect, a
quoting convention, or — here — a misquotation.

That is not an argument for relaxing the check. Altering wording inside quotation marks
attributes to Hill something Hill did not write, and this run shows the check catching it
while the same model, quoting the same passage at greater length, produced a verbatim
span that verified at `reference_translation[416:692]`. But **`unverified_quotes` should
be understood as a misquotation check, not a hallucination check.** Its yield across four
runs is one real misquotation and roughly a dozen false alarms since fixed.

### Two of the four passes are worse answers than the failures they replaced

**Aksum exits 0 and says something false.** "They detail what Rome exported to Aksum
rather than what Rome imported from it [S1]" — while S1's own English, printed in the
evidence block, reads *"There are exported from these places ivory, and tortoise-shell and
rhinoceros-horn."* That is precisely what Rome imported from Aksum. The corpus now
contains the answer, in English, aligned to the passage, and the system refuses it and is
scored **grounded** for doing so, because the sentence carries a citation and contains no
quotation to check.

**Vimose exits 0 by retreating.** Under v2 it produced seven quotations, all seven
resolved to characters on disk, presenting the hedges as hedges — the best output this
project has produced. Under v3 it says the content "is only partially available" and
quotes nothing. Both are `Grounded`. Whether v3's extra caution caused this or it is
run-to-run variance is **unresolved**, and worth a `--repeat` before concluding anything.

### What that means

The six checks verify that a claim carries a citation and that quoted text appears in the
source it cites. They do not, and cannot, verify that the claim **follows from** the
passage. A refusal is trivially grounded. So the exit code now measures citation hygiene,
and citation hygiene is maximised by saying as little as possible.

This is the Part 6 limitation arriving one layer up. There it was "self-consistency is not
accuracy"; here it is **"groundedness is not correctness"**, and the failure mode has
flipped from the dangerous one to the useless one — from confident readings of untranslated
runes to a system that will not tell you what its own Greek says. The first was worth
building all this to prevent. The second is what Part 8 has to measure, and no floor built
on `exit 0` will see it.

### Closing the last asymmetry — and an unexpected consequence

A systematic check of every non-English record found **one more** of the Adulis class, and
only one. `arabia-01-periplus` (Cana and the Frankincense Country) held Greek §27–29
against a 734-character English abridgement that **omitted §28 entirely** and ran §27 and
§29 together as one block — so only §27 aligned, §29 had no reachable English despite
being partly present, and §28 reached readers only through a Part 6 machine translation.

Replaced with Schoff's §27, §28 and §29 in full and in order, from the same ToposText
digitisation, recorded in a `reference_translation_note`. Corpus is now **24 documents →
57 chunks**. All three Periplus records align section-for-section, and the corpus-wide
count of non-English passages lacking published English is **0**.

**The consequence is worth stating, because it is not obviously good.** Every one of the
18 retrieval-eligible non-English passages now has a published human translation aligned
to it. `resolve_english` prefers published over machine, so **a machine translation will
never again reach a reader from this corpus.** The Part 6 confidence machinery — the
bands, the `medium` caveat with its observed cosine, the blocking-flag rule that refuses
the Vimose echo, the `unlabelled_machine` check — is now exercised only by the offline
tests. It is dormant against live questions.

That is the right outcome for a reader and an awkward one for a test bed. Two things
follow for Part 8: any eval must keep at least one case that exercises machine English
deliberately, and the honest place to find such material is the corpus's own growth —
Phase 2 regions whose sources have no published English at all are where the confidence
bands will earn their keep. Building them was not wasted; it was early.

### The Vimose triple: not variance, and two defects it shook out

Three runs of the same question under `p7-answer-v3`, same evidence, temperature 0. All
three refused; two were byte-identical and the third reworded one clause. **So the v2 → v3
regression is not run-to-run variance** — v3 consistently retreats where v2 produced seven
quotations, all seven resolved to disk. The only delta is rule 6's "cite only sources you
can read", which was written for a passage with *no* English and appears to have made the
model cautious about a passage whose English it judged interpretive. That is the **third**
consecutive prompt version broken by a conflict between two of its own rules.

**1. `QUOTED METADATA` fired in the wild, 3/3.** Its first live firing. The model quoted
the record's title — `earliest datable Elder Futhark runic texts` — in all three runs,
despite rule 3 telling it in as many words that the header line is not quotable. The check
works; the prompt rule does not. Worth remembering the next time a rule looks like a fix.

**2. One `answer_id` for three different answers.** All three runs stored as
`3b4489a4f7657729e397a3506eec3bf1`, and the third's text differed from the first two. The
key is (question, model, prompt version, evidence) and deliberately excludes the answer
text, which is right for a table of *current* answers and wrong as the only record: it
destroys precisely the run-to-run evidence Part 8 needs. Part 6 hit this with `--repeat`
and answered it with `eval/runs/`; `run_answer` now archives every run to
**`eval/answer_runs/<timestamp>-<answer_id>.json`**, never overwriting, with same-second
collisions handled.

**3. The verdict moved without the answer moving.** The earlier v3 run of this question
exited **0**; these three exit **1**. The answers say the same thing — the corpus does not
contain a full rendering of the runes — but these three reached for the title to say it,
and that is a `QUOTED METADATA` failure. A rewording that leaves the answer's usefulness
untouched flips the exit code. The metric is sensitive to phrasing in a way that has
nothing to do with whether the reader is well served, which is one more reason a hard floor
built on `exit 0` would measure the wrong thing.

### Part 7 milestone, honestly stated

A question in English retrieves Greek, Literary Chinese, Old Tamil and Proto-Norse; the
right English is chosen per passage under a stated policy; machine translations arrive
banded and are never quoted unlabelled; and **every quotation in every grounded answer
resolves to an absolute character span in a named field of a named seed record** —
`reference_translation[1981:2071]`, `original_text_excerpt[1902:1958]`. That was the claim
Part 7 set out to make, and it holds.

What it does not yet do is tell you whether the answer is any good. Four defects in this
part were found by running it and none by writing it: a sentence splitter that cut inside
quotations, a quote matcher stricter than any writer, an alignment rule that one long
section could disable, and a merge that turned one passage into two witnesses. A fifth —
that the corpus itself was missing the passage under discussion — was found only because
the answer layer asked a question no earlier part had asked.

## Part 8 — starting point (for the next thread)

**State:** Parts 1–7 complete and verified. 24 documents → **57 chunks → 55 embedded**
with `voyage/voyage-3.5`. Retrieval 11/11 probes at rank 1. Translation 12/12 gold cases,
bands stable across five archived runs. Answers: 4/5 grounded, and **every quotation in
every grounded answer resolves to an absolute character span** in a named field of a named
seed record.

Goal as the plan states it: a groundedness eval harness and a hard floor. **What Part 7
learned changes what that has to mean.**

### The problem Part 8 actually has to solve

The six grounding checks verify that a claim carries a citation and that quoted text is
really in the source it cites. They cannot verify that the claim **follows from** the
passage. Two consequences, both observed live:

- **A refusal is trivially grounded.** The Aksum answer exits 0 while stating the opposite
  of what its own cited evidence says — Schoff's §6, printed in its evidence block, reads
  *"There are exported from these places ivory, and tortoise-shell and rhinoceros-horn"*,
  and the answer says the sources do not cover what Rome imported from Aksum.
- **Citation hygiene is maximised by saying as little as possible.** The Vimose question
  scored `Grounded` for a retreat, having scored `NOT GROUNDED` for the best answer this
  project has produced.

So a floor built on `exit 0` would reward the failure mode that remains and ignore the one
that matters. Part 6's limitation — self-consistency is not accuracy — arrives here as
**groundedness is not correctness**, and the danger has inverted: from confident readings
of undeciphered runes to a system that will not tell you what its own Greek says.

### What Part 7 hands you

- **`eval/answer_runs/<timestamp>-<answer_id>.json`** — every run archived, never
  overwritten. `answers` is keyed on (question, model, prompt version, evidence) and
  updates in place, so the table cannot hold repetitions; this directory can.
- **`answers`, `answer_citations`, `answers_citing_flagged_translations`** — the last has
  been **0 rows** in every run.
- **Seven checks**, not six: `unknown_markers`, `uncited_sentences`, `unverified_quotes`,
  `quoted_metadata`, `misattributed_quotes`, `claims_on_untranslated`, `unlabelled_machine`.
- **`run_answer --json`** — the full payload, including every passage's English kind, band,
  flags, alignment ground, and every resolved quote span.
- **`eval/goldset.py`** — the strict loader from Part 6. Rejects unknown keys at load time,
  which is what stops a mistyped assertion from silently disappearing.

### Decisions Part 8 has to make

1. **A gold answer case must assert content, not only groundedness.** The corpus contains
   the answer to the Aksum question; a case that does not say so cannot fail the refusal.
   Expected substrings, expected cited chunk ids, expected resolved spans — all are
   checkable without a human. Decide before writing the harness, because the easy version
   (assert `grounding.ok`) is the one that measures nothing.
2. **How to score "used the evidence" without a judge you cannot audit.** An LLM judge
   would carry the same unauditable-agreement problem the back-translation had. Prefer
   assertions that are facts about strings, as Part 7's checks are.
3. **Refusal rate is a metric, not an outcome.** Track it per question and per prompt
   version. A rise in refusals with no fall in errors is a regression.
4. **How many repetitions, and what is the unit.** Part 6 measured a 0.317 chrF spread on
   Old Tamil at temperature 0. Part 7 saw a rewording flip an exit code with the answer's
   usefulness unchanged. A single shot measures one sample of a distribution nobody has
   looked at.
5. **Case zero is already waiting.** The Vimose question under `p7-answer-v2` produced
   seven quotations, all resolved to disk, hedges intact; under `p7-answer-v3` it refuses,
   three times out of three. Both are "grounded". **A harness that cannot separate those
   two is not measuring anything**, and adjudicating prompt versions by hand on one
   question is exactly what Part 8 exists to replace.

### Known gaps, carried forward honestly

- **`p7-answer-v3` rule 6 is under suspicion.** Written for passages with no English, it
  appears to have made the model retreat from a passage whose English it judged
  interpretive. v2 is the comparison; do not revert by eye, adjudicate it.
- **Prompt rules are a weak instrument.** Rule 3 tells the model the header line is not
  quotable; it quoted the title in 3 of 3 runs anyway. The `quoted_metadata` check caught
  every one. Prefer checks to rules.
- **The machine-translation path is dormant.** All 18 retrieval-eligible non-English
  passages now have aligned published English, so `resolve_english` will never choose
  `machine` from this corpus. Bands, the `medium` caveat, the blocking-flag rule and
  `unlabelled_machine` are exercised only by the offline suite. Keep at least one eval case
  that exercises them deliberately; Phase 2 material with no published English is where
  they will matter again.
- **Self-consistency is still not accuracy.** `chrf_ref` remains the only accuracy signal,
  exists for 16 of 24 records, and is inflated by formulaic text.
- **ŠKZ is scored against the wrong rendering** — heterographic transliteration against
  phonemic transcription. Needs a per-record comparison target the schema does not have.
- **Three uncalibrated confidence profiles** — `documentary` n=1, `verse` n=1,
  `inscription` n=3.
- **Two records held back as `pointer`** — Palmyrene Tariff and **Ezana Stone**. The latter
  is Aksumite and would give the Aksum question a second witness in Ge'ez beside the Greek.
- **The claim-sentence rule is a heuristic** — five or more words, not ending in a colon.
  It has produced no false positive in four live runs, but it has never been stress-tested.

### Standing lessons from Parts 3–7

- Parse-level SQL checks miss type inference. Anything with optional/NULL parameters needs
  one execution against the real database.
- A test that passes for the wrong reason is worse than one that fails. Assert on the
  specific thing, not a proxy for it.
- **Mutation-verify every guard, and expect misses.** Six of the thirteen Part 7 mutations
  initially failed to break their guard — because two fixes protected the same case, or
  because a fallback path quietly satisfied the assertion. Each miss was a finding.
- **Every defect in Parts 6 and 7 was found by running the thing, not by writing it** — and
  three of Part 7's were found by `--dry-run` before any chat call was made. One embedding
  request is the cheapest test in the system.
- Place a threshold where no observed case straddles it, then confirm with repetition.
- Provisional numbers get anchored on whatever is nearby.
- **When two prompt versions in a row fail to fix a behaviour, the problem is not in the
  prompt.** The Aksum refusal survived v2 and v3 and turned out to be a corpus defect: the
  translation stopped one section short of the passage that answered the question.
- The gateway's free tier is 3 requests/minute. Batch aggressively.
- Two PowerShell windows, both needing `cd` + venv activate + `.env` load. The gateway
  reads keys only at startup.

### To run (Windows / PowerShell, repo root, gateway up on :4000, db up)

```powershell
python -m answer.test_answer                 # 133 assertions, offline
python -m answer.test_translate              # 104 assertions, offline
python scripts\mutate_part7b.py              # 13 mutations, restores sources
python -m ingest.run_ingest --stats          # 24 docs, 57 chunks
python -m ingest.run_embed --stats           # embedded 55, pending 0
python -m retrieve.crosslingual_check        # 11/11
python -m answer.run_answer --dry-run "..."  # one embedding, no chat call
```

Cost per answered question: one embedding request and one chat call. `--dry-run` spends
the embedding only.

## Part 8 — baseline recovery (2026-08-10)

**The archive Part 8 was to work from did not exist.** `eval/answer_runs/` was added at
the end of Part 7, *after* the runs it was meant to capture, and held five files of 90–130
bytes — collision fixtures from a manual check of `_archive`'s same-second loop, written
by hand and left there. Not one real run. So the v2 Vimose answer named as case zero —
seven quotations, all resolved to disk — existed only as prose in this file.

It was recoverable, and the reason is the Part 6 lesson paying off a second time.
`answer_id` is a sha256 over (question, model, **prompt version**, ordered chunk ids), so
a v3 run of the same question wrote a *new* row instead of overwriting v2's.

`scripts/recover_answer_baseline.py` (census by default, `--write` to dump; database reads
only, no gateway). Recovered **16 answers**: v1 ×5, v2 ×5, v3 ×6, all with their citation
rows intact — no loss to `answer_citations`' `ON DELETE CASCADE` despite two re-ingests.

### What the census found that the plan did not assume

- **Three prompt versions, not two.** `p7-answer-v1` survived for all five questions. The
  handoff named only v2 and v3. That is a 5 × 3 grid, not a single pair, and adjudicating
  prompt versions by hand on one question was exactly what Part 8 existed to replace.
- **Six v3 rows against five questions.** The duplicate is Aksum, and it is a *controlled
  corpus experiment nobody designed*: two rows mean the evidence changed while question,
  model and prompt stayed fixed — the Adulis translation fix landing between two runs.
  Nothing else in the archive isolates that variable.
- **The database no longer reproduces this file's 4/5 headline.** v3 reads 3 grounded of
  6, because the Vimose triple ran after the results table was written, exited 1 three
  times, and updated the same `answer_id` in place. The exit-0 run the 4/5 rests on is
  gone. Treat the recovered v3 Vimose row as the third of three, not as the run in the
  table.

### A recovered archive is not a run, and says so

The passage text and the rendered `sources_block` were never persisted and no query brings
them back. Every recovered file therefore carries `recovered: true`, a `recovered_absent`
list naming each missing field, `recovered_from`, and `-recovered` in the filename. Same
argument as `calibrated: false` and `english_ground`: a record that cannot distinguish a
witness from a reconstruction is eventually read as though everything in it were a witness.

`timestamp_meaning` travels too, because `UPSERT_ANSWER` sets `created_at = now()` on
conflict — the column is the row's **last write**, not the run.

A guard reads `run_answer.py`'s payload block directly and fails if it grows a key that is
neither recoverable nor named in `ABSENT`, so the two cannot drift.

The five fixtures moved to `eval/fixtures/` with a README. `eval/answer_runs/` now holds
16 files and all 16 are runs.

## Part 8 — the content gold set (2026-08-10)

`eval/gold/answer_cases.json` + `load_answer_cases` in `eval/goldset.py` +
`eval/answer_eval.py`. Five cases, one per archived question. Every assertion is a fact
about strings — a substring of the answer, a doc id among the citation rows, a count of
quotations that resolved to characters on disk. No judge: a judge would reproduce the
back-translation's problem one layer up, where the checker and the checked can be wrong in
the same direction and agree.

### The two rules that make it different from the exit code it replaces

Both are enforced at **load time**, not by discipline, because the easy version of this
harness is the one that gets written at six o'clock.

1. **A case that makes no content assertion will not load.** `assert grounding.ok` is
   unwritable; the loader's error names the Aksum answer. Groundedness cannot fail a
   refusal, and a refusal is trivially grounded.
2. **`expect_refusal` must justify itself** in `refusal_is_correct_because`. Declaring that
   the corpus cannot answer a question is a claim about the corpus. Same rule as
   `expect_untranslatable`, for the same reason, and the loader also refuses a case that
   demands both a refusal and the content a refusal cannot contain.

Matching is case-insensitive and whitespace-normalised, and **deliberately not**
punctuation-insensitive: `tortoise-shell` and `tortoise shell` are different claims about a
source's wording, and the case says which it accepts rather than letting the matcher decide.

### The grid

```
                        p7-answer-v1     p7-answer-v2     p7-answer-v3
  aksum-exports         FAIL(G)          FAIL(g)          FAIL(g)/FAIL(G)
  antikythera-absent    PASS(g)          PASS(G)          PASS(G)
  chinese-da-qin        PASS(g)          PASS(g)          PASS(g)
  muziris-cargo         PASS(g)          PASS(G)          PASS(G)
  vimose-runes          FAIL(g)          PASS(G)          FAIL(g)
```

`G` = the Part 7 checks called it grounded. **10/16 pass on content, and the two metrics
disagree on 7 of 16 — in both directions.**

- **Aksum is grounded twice while omitting ivory, tortoise-shell and rhinoceros-horn**,
  which its own evidence block prints in English.
- **Chinese passes all three times while scored NOT GROUNDED all three times** — an uncited
  opening sentence, a real catch, on three accurate well-quoted answers.
- **Case zero is now mechanical.** v2 passes; v1 and v3 fail. No hand adjudication.
- **Antikythera is the control** and it earns its place: it proves the harness does not
  simply reward saying more, and its excluded strings keep the dangerous failure — a
  fabricated date arriving attached to a citation — caught.

### The Aksum v1 row: four failures, not one failure repeated

The live run turned up a distinction the sandbox did not. **v1 resolved 2 quotations and
still failed**, with no quotation-floor miss. It retrieved the right passage, quoted the
Greek export sentence in full — `Φέρεται δὲ ἀπὸ τῶν τόπων ἐλέφας καὶ χελώνη καὶ ῥινόκερως`
— and said *"no English translation is available for the second passage."*

**That was true when it ran.** The Adulis gap was closed later in Part 7. v1's refusal was
correct behaviour under the corpus it saw; v3-after-fix refuses with the aligned English
present and contradicts it. The case scores both FAIL because it is written against
today's corpus.

**Do not weaken the case to accommodate v1.** The missing axis is *which corpus was this
answer made against*, and that is the fourth time this project has met the same shape —
after `embedding_model`, `prompt_version`, and `chunk_translations`' source hash. A result
is only comparable within the thing that produced it. Recorded in the case's
`archived_status`; the fix belongs in the re-check runner.

### What the mutation run found that writing the tests did not

Nine mutations (`scripts/mutate_part8.py`), and on the first pass **the quotation floor
broke no test at all** — every archived failure already failed on content, so the floor was
load-bearing for nothing and could have been deleted in silence. Wrote the missing guard:
an answer that says all the right words with zero resolved quotations must still fail.

The same run showed the **Aksum case is over-determined** — five failing assertions, so its
verdict cannot pin any single one. The guard that does pin the alternatives scoring is the
check on what the failure *names*, not on whether it fails.

Two of the mutations were themselves wrong, and both are recorded in place rather than
quietly fixed, because a mutation that fails to mutate reads exactly like a guard that does
not work:

- one deleted punctuation outright (`tortoise-shell` → `tortoiseshell`), which still fails
  to match `tortoise shell`. Replacing punctuation with a space is the tolerance a
  well-meaning author would actually add;
- one was defeated by a test label that changed shape with the failure mode, which made
  five correct guards read as MISS. `expect_rejected` now always reports the bare label.

Same lesson as Part 7's mutation run, from the other side: **expect misses, and read each
one before blaming the guard.**

### Offline state

- `eval/test_answer_eval.py` — 46 assertions, no network, no database.
- `scripts/test_recover_baseline.py` — 44 assertions, including the read-only guard that
  stops recovery mutating the evidence it recovers.
- `scripts/mutate_part8.py` — 9 mutations; `scripts/mutate_recover.py` — 11. Both restore
  sources and re-run the suite to prove it.
- Part 7's 133 and Part 6's 104 still pass unchanged.

## Part 8 — what is still open

1. **The re-check runner.** v1 was scored by a checker with six failure categories; v2 and
   v3 by one with seven (`quoted_metadata` did not exist when v1 ran), and v1's four
   `unverified_quotes` are the *same strings* v2 quoted successfully under a fixed matcher.
   **Pooling the stored `grounded` flag across the grid measures the checker as much as the
   prompt.** Re-run today's seven checks over the archives instead — `cite.verify()` is pure
   and costs nothing. It needs the passage text, reconstructible from `chunk_id`, and must
   flag any answer whose cited chunk has changed since: the `current_translations` /
   `stale_translations` pattern, one layer up.
2. **Corpus versioning on new answers.** Stamp a corpus digest into the payload so the
   Aksum v1 problem stops recurring for the 17th answer.
3. **Repetition.** No case has been run more than once through this harness. Part 6 measured
   a 0.317 chrF spread at temperature 0; Part 7 saw a rewording flip an exit code. A single
   shot is one sample of a distribution nobody has looked at.
4. **Refusal rate as a tracked metric**, per question and per prompt version. A rise in
   refusals with no fall in errors is a regression, and the grid already shows v3 refusing
   where v2 answered.
5. **The hard floor itself.** Not yet set, deliberately. Set it on content PASS plus refusal
   rate, never on `exit 0` — and place it where no observed case straddles it, then confirm
   with repetition, as the Part 6 threshold lesson requires.
6. **The machine-translation path is still dormant.** All 18 non-English passages have
   aligned published English, so no eval case currently exercises the confidence bands.

### To run (Windows / PowerShell, repo root; db up for the first two only)

```powershell
python scripts\recover_answer_baseline.py            # census, reads only
python scripts\recover_answer_baseline.py --write    # dump answers to eval/answer_runs/

python -m eval.test_answer_eval                      # 46 offline
python scripts\test_recover_baseline.py              # 44 offline
python scripts\mutate_part8.py                       # 9 mutations
python scripts\mutate_recover.py                     # 11 mutations

python -m eval.answer_eval --archives --by-case      # the grid
python -m eval.answer_eval --list                    # what each case asserts, and why
python -m eval.answer_eval --json run.json           # score one live run
```

Everything in this part costs nothing to run: no gateway, no embeddings, database reads
only where a database is needed at all.

## Part 8 — prompt v4 and the sweep (2026-08-10)

The archived grid said v2 beat v3 on content, with the gap entirely on Vimose —
the question rule 6 was suspected of breaking. That is a decision the harness was
built to make, so it was made rather than deferred.

### A third instance of the same defect: the prompt texts were never stored

Only the prompt *name* was kept. `ANSWER_PROMPT_VERSION` was bumped while the
prose was edited in place, so the archive records sixteen answers under three
prompts and the repository held exactly one of the three. **"Run v2 again" was not
a reproducible instruction.**

Same defect as Part 4's `embedding_model` and Part 6's `back_prompt_version`,
arriving a third time in a new disguise: a label was stored and the thing it
labelled was not. Fixed with `assemble.ANSWER_PROMPTS`, a registry holding every
version's full text. Editing in place is now impossible — a changed contract has
to be a new entry, because the old entry is sitting beside it.

**`p7-answer-v2r` is RECONSTRUCTED, not recovered.** v2's exact wording is gone;
this is v3's rule 6 with the "cite only sources you can read" paragraph removed,
per the v3 change note. The `r` is in the version string so its answers can never
be pooled with the archived v2 rows as though they came from the same prompt. If
the two agree that is evidence the reconstruction is faithful; it is not a
substitute for having kept the text.

### v4 — the narrowing

Rule 6 is the only delta from v3; rules 1-5 are byte-identical, so the comparison
stays clean.

v3 said *"Cite only sources you can read"*. That asks the model to **judge**
readability, and on Vimose it judged a published-but-hedged English gloss
unreadable and retreated in three runs out of three from the passage v2 answered
best. v4 keeps the restriction and makes its test **mechanical** — the literal
marker `ENGLISH: NONE AVAILABLE`, nothing else — and states the boundary from
both sides: *"That restriction applies to those sources and to no others: a
source that shows ENGLISH is usable in full, however partial, hedged or uncertain
that English is. Report the hedges as hedges and cite it."*

**The generalisable lesson, on the fourth occurrence:** three prompt versions in a
row broke on a rule that asked the model to decide something. A rule requiring
interpretation will be interpreted more broadly than written. Prefer a rule that
names a string.

Guards added: the running prompt must be registered and identical to its
registry entry; no two versions may share a text; the running prompt must not
contain "Cite only sources you can read"; v3's text is kept verbatim so the
comparison it lost can be re-run. The old test pinned `endswith("v3")` — a
version, not a property — and had to be edited every time the prompt moved; it
now asserts the property.

### `--repeat` on run_answer, and the sweep

`run_answer --repeat N` reuses one embedding and one evidence set across N chat
calls, and reports whether the **verdict** moved and whether the **text** moved.
A stable verdict over varying text is a usable metric; a verdict that flips on a
rewording is not, and the Part 7 Vimose triple flipped one on exactly that.

`eval/run_answer_sweep.py` runs every gold question under several prompt versions,
repeatedly:

- **each question is embedded once** and the vector reused across every prompt and
  repetition, so a 5 x 2 x 3 sweep costs **5 embedding requests, not 30** — the
  embedding depends on the question alone and Voyage's free tier is 3/minute;
- **the evidence is built once per question**, so prompt version is the only
  variable and nothing unrelated can move underneath the comparison;
- **questions come from the gold set**, so the sweep cannot drift from the harness
  that scores it.

It marks `!` on any cell whose metric landed differently across repetitions, and
prints refusal rate beside content pass rate rather than after it — a prompt that
refuses more while erring no less is a regression, however tidy its citations.

### A guard that broke on refactoring, which is its own finding

The `--repeat` change turned `payload = {` into `payloads.append({`, and the
ABSENT-drift guard in `test_recover_baseline.py` — which sliced the source on
that literal — raised `IndexError` instead of failing. The mutation run reported
a crash rather than a finding.

Now located by parsing: the payload dict is identified as the dict literal
carrying both `grounding` and `answer_id`, wherever it sits. **A guard that breaks
when code is merely rearranged trains people to ignore it.**

### Offline state

Part 6: 104. Part 7: 133 + 13 mutations. Part 8: 46 + 45 assertions, 9 + 11
mutations. All passing.

### To run the sweep (Windows / PowerShell, gateway up on :4000, db up)

```powershell
python -m eval.run_answer_sweep --dry-run          # 5 embeddings, no chat call

python -m eval.run_answer_sweep `
    --prompt-version p7-answer-v2r `
    --prompt-version p7-answer-v4 `
    --repeat 3
```

5 embedding requests, 30 chat calls. Chat is a different rate-limit tier from
embeddings, so the two do not compete; add `--pause 2` if the account needs it.
Every run is archived to `eval/answer_runs/` and the whole sweep to
`eval/sweeps/`.

**Read the dry run first.** It costs 5 embedding requests and shows the evidence
each question retrieves. Three of Part 7's defects were found by `--dry-run`
before any chat call was made; one embedding request remains the cheapest test in
the system.

### Setting the floor, once the sweep has run

1. Any cell marked `!` is unstable — **a floor must not sit where a case
   straddles it.** That is the Part 6 threshold rule, and it is why the sweep
   repeats rather than sampling once.
2. Set the floor on **content pass rate and refusal rate together**, never on
   `exit 0`. Groundedness is maximised by saying as little as possible.
3. Expect `aksum-exports` to fail under both prompts. It is a corpus/reasoning
   failure, not a prompt one — the English is present and aligned, and two prompt
   versions have already failed to fix it. **When two prompt versions in a row
   fail to fix a behaviour, the problem is not in the prompt** — the standing
   lesson from the Adulis defect, which is worth testing again here before
   anyone writes a v5.

## Part 8 — what the sweep's dry run found before any chat call was paid for

Three of Part 7's defects were found by `--dry-run`. This one found two more, and
one of them is a corpus defect of a class already seen once.

### 1. The gold case could be satisfied by the wrong document

`aksum-exports` asserted `expect_cited_docs: [africa-03-periplus-adulis]` plus the
content terms. The dry run printed the whole evidence set, and **three of its six
passages carry gold terms**: `ivory` and `tortoise-shell` in the Muziris passage
(S3), `rhinoceros` in the Hou Hanshu (S6).

So an answer about India and China — "ivory and tortoise-shell [S3] … rhinoceros
horn [S6]" — that named the Aksum record once for something else would have
satisfied every assertion **while never using the passage the case is about.**
Citing a document says the model named it; it does not say the model used it.

Same failure shape as the Part 4 pepper probe, which passed on `doc_id` while the
passage it claimed was not in the database. The lesson keeps arriving: assert on
the specific thing, not a proxy for it.

Added `expect_quoted_docs` — documents from which at least one quotation must
resolve to characters on disk — and applied it to the four non-refusal cases. The
archived verdicts are unchanged at **10/16**, so this closed a hole without
rewriting history.

Two further notes from wiring it up, both worth keeping:

- The test helper built quote spans with no `marker`, so every quotation belonged
  to no document and the new assertion failed on answers that should pass. A
  span without its marker cannot be traced to a source, which is the whole point
  of the span.
- The mutation removing the quotation floor left the verdict unchanged, because
  `expect_quoted_docs` also fails when nothing is quoted. **Second time a
  mutation has shown that a verdict cannot pin a single assertion**, and both
  times the guard doing the real work was the one checking what the failure
  NAMES, not whether it failed. Defence in depth is good; it just means the
  verdict is the wrong thing to mutation-test against.

### 2. A second editorial-prose-as-evidence defect, in the field nobody audited

`arabia-02-palmyrene-tariff::translation::000` is **not a translation**:

> "Regulates customs duties on goods entering/leaving Palmyra and on local trades
> (not long-distance caravan tolls specifically) — described by historian John
> Matthews as 'one of the most important single items of evidence for the
> economic life of any part of the Roman Empire.'"

It is an editorial summary carrying a quotation from a **modern historian**, and
it is classified `text_fidelity=translation`, `eligible_for_retrieval=True`. It
surfaced as S6 in the `chinese-da-qin` evidence set at similarity 0.375.

**Nothing in the pipeline catches it.** A quotation of Matthews resolves to real
characters in `reference_translation`, so `unverified_quotes` passes and a reader
receives a modern historian's judgement presented as Palmyrene evidence with a
citation attached. That is the failure this project was built to prevent.

The record's *original* is correctly held back as `pointer` — so the placeholder
is blocked while the editorial prose beside it is citable. Second instance of the
class after the Vimose comb catalogue, and the pattern is now visible:
**`text_fidelity` has been audited on the original field and never on the
translation field.**

Not fixed before the sweep, deliberately: changing the corpus now would break the
comparison against the 16 archived answers, and prompt version has to be the only
variable. Fix after, then re-run. **A systematic audit of every
`reference_translation` for editorial prose is owed** — the Vimose case was found
by an echo flag and this one by reading a dry run, neither by a check.

### 3. Retrieval ranking oddities, recorded not acted on

- `muziris-cargo`: the top hit is `arabia-01-periplus` (Frankincense Country) at
  0.503, **above** the actual Muziris passage at 0.463. The answers are right
  anyway, but the ranking is not.
- `vimose-runes`: the Vimose record ranks **third** at 0.384, below two Arabian
  inscriptions. The lowest-similarity evidence set of the five.
- `chinese-da-qin`: `seasia-02-oc-eo-site` contains the string `166`, which is one
  of that case's accepted alternatives. `expect_quoted_docs` now prevents an
  answer satisfying it from the wrong record.

## Part 8 — RESULT (2026-08-10): the sweep, a scorer bug, and the floor

### First, the scorer was wrong, and 30 chat calls said so

The first sweep reported **content 0/3 on Muziris and on the Chinese sources**,
under both prompt versions, while those same answers quoted five and seven
passages and had passed on all three archived prompts. Answers do not get worse
while quoting more.

`_cited()` filtered passages on a `cited` key. A **recovered** payload carries it,
because `answer_citations` stores that column. A **live** payload is
`Passage.to_dict()`, which does not — whether a passage was cited is a property of
the answer, not of the passage. So on every live run the filter found nothing and
`expect_cited_docs` failed regardless of the answer.

**The scorer had never been run against the thing it exists to score.** Every test
built its payloads in the archived shape, which is the shape that has the key.
Guarded now by a test that constructs a real `Passage.to_dict()` and asserts both
that it lacks `cited` and that a good answer in that shape passes.

The calls were not wasted, and that is the argument for archiving runs rather than
verdicts: `eval/rescore_sweep.py` re-scored all 30 offline, **content pass 6 → 21**.
Part 6 learned this with `eval/runs/`, Part 7 with `eval/answer_runs/`; this is
the third application of the same principle and the first time it paid for itself
in money.

### The prompt decision — and my prediction was wrong

| | content | refusals | grounded | mean quotes |
| --- | --- | --- | --- | --- |
| **p7-answer-v2r** | **80%** | **40%** | 93% | 3.1 |
| p7-answer-v4 | 60% | 60% | 87% | 2.3 |

Per cell, over three repetitions each:

```
  case                 v2r        v4
  aksum-exports        0/3        0/3
  antikythera-absent   3/3        3/3
  chinese-da-qin       3/3        3/3
  muziris-cargo        3/3        3/3
  vimose-runes         3/3        0/3
```

**v4's narrowing did not work.** It was predicted to fix Vimose and did not: 0/3,
same as v3, against v2r's 3/3 with byte-identical output on all three runs. So
rule 6's restriction has now broken the same question under **two** successive
attempts to fix it, which is the standing lesson arriving for the fourth time:
*when two prompt versions in a row fail to fix a behaviour, the problem is not in
the prompt.*

Two things settle it:

1. **The clause duplicated a check that already existed.** `claims_on_untranslated`
   has enforced exactly this since Part 7, at no cost. The prompt rule cost the
   Vimose question 6 runs out of 6 across v3 and v4. *Prefer checks to rules* —
   already written in this file, and here is what ignoring it costs.
2. **The condition it guarded can no longer arise.** v3's rule 6 was written for a
   retrieved passage with no English at all. Part 7 gave all 18 non-English
   passages an aligned published translation, so no passage in this corpus yields
   `ENGLISH: NONE AVAILABLE`. The guard is dormant; only its side effect is live.

**`ANSWER_PROMPT_VERSION` is now `p7-answer-v2r`.** v3 and v4 stay in the registry
so the comparison can be re-run rather than reconstructed a second time.

### The floor — `eval/gold/floor.json`, and why it is content-based

Set from 30 runs across 10 cells, every number in a gap no observed case
straddles.

**The choice of metric is measured, not argued.** Across ten cells of three
repetitions: **content was stable in 10 of 10** — every cell landed 0/3 or 3/3,
nothing in between. **`grounded` was unstable in 3 of 10**: same question, same
evidence, same prompt, temperature 0, different verdicts. A floor on `grounded`
would measure the sampler. That is the empirical version of the argument Part 8
opened with.

Terms: every **required case** (`antikythera-absent`, `chinese-da-qin`,
`muziris-cargo`, `vimose-runes`) must pass in **every repetition** — per case, not
on average, because an average lets total failure on one question be paid for by
another. **Refusal rate ≤ 0.5** (observed 0.40 v2r, 0.60 v4). **Zero unstable
content cells.** **At least 3 repetitions** — checking the floor against one shot
is not checking it.

`aksum-exports` is listed under `known_failing_cases` with a written reason, and
the loader **refuses to let a case be both required and known-failing**. It is
reported on every check, never subtracted: an unexplained exemption becomes
permanent, and a floor pass must never read as "the system answers these
questions".

Verdict on the sweep: **v2r MEETS THE FLOOR. v4 is BELOW it** (vimose 0/3, refusal
rate 60%).

### Aksum: seven consecutive failures under four prompts

0/3 under v2r, 0/3 under v4, 4/4 across the archived Part 7 runs. The dry run
confirmed the answer is in the evidence block in published English, aligned by
section (`original::002` ↔ `translation::004+005`, ground=`section`), with all
three gold terms present.

**This is not a prompt defect and not a retrieval defect.** The model is handed
Schoff's *"There are exported from these places ivory, and tortoise-shell and
rhinoceros-horn"* and reports that the sources do not say what Rome imported. The
question is bidirectional, the passage answers both directions, and the model
consistently reads one. That is the next thing to investigate, and no v5 should be
written before it is understood.

### A negative result worth recording

Part 6 observed that run-to-run variance looked like a proxy for competence and
asked for it to be tested properly in Part 8. **It does not replicate at the
answer layer.** Distinct-text counts against outcomes: vimose/v2r 1 text and
passes, vimose/v4 3 texts and fails — but aksum/v2r is 1 text and **fails**,
muziris/v2r is 3 texts and **passes**. No usable relationship. The hypothesis was
worth testing and is not worth carrying forward.

### Offline state

Part 6: 104. Part 7: 133 + 13 mutations. Part 8: 70 + 45 assertions, 11 + 11
mutations. All passing.

### To re-check the floor at any time (no API calls)

```powershell
python -m eval.rescore_sweep                 # newest sweep, re-scored + floor
python -m eval.answer_eval --archives --by-case
```

A fresh sweep re-checks it live and **exits 1 if any prompt version is below the
floor**:

```powershell
python -m eval.run_answer_sweep --prompt-version p7-answer-v2r --repeat 3
```

## Part 8 — the translation-field audit (2026-08-10)

Prompted by the Palmyrene record surfacing in a sweep dry run. All 24 records'
`reference_translation` fields read by hand. **Result: 1 real defect, 1 partial,
3 false alarms I had raised myself, 19 clean.**

### No mechanical rule separates the good from the bad

Two candidate rules were tried before reading, and **both fired on the wrong
records**:

- *"a pointer's original means its translation is suspect"* — would have flagged
  the **Ezana** titulature, which is genuine translated Greek, and missed the
  object records entirely.
- *"translation_source declaring a summary means the field is not a
  translation"* — flags four records, of which one is already honestly labelled
  `object_description` (Hwangnam glass), one is the real defect (Palmyrene), one
  is partial (Ezana), and one is **Vimose**, a published hedged gloss and a
  required floor case.

Length ratio was worse still: it flags Weilüe at 13.3x and Hou Hanshu at 14.4x,
which is simply what Literary Chinese does. That is the **same length/script
confound Part 6 already untangled for chrF**, and building on it would have been
repeating a documented mistake.

**The three object records I flagged on ratio were correctly classified all
along** — Hwangnam glass, Hoby, Óc Eo medallion all carry `object_description` on
both chunks, and Part 7 shows them as `english=source ground=self` with the
caveat "This source is in English; nothing has been translated." The label was
truthful, which is the thing that matters. Flagging them was my error, corrected
by reading rather than by a heuristic.

### The one real defect

**`arabia-02-palmyrene-tariff`** held, in a field classified
`text_fidelity='translation'` and retrieval-eligible:

> "Regulates customs duties on goods entering/leaving Palmyra ... — described by
> historian **John Matthews** as 'one of the most important single items of
> evidence for the economic life of any part of the Roman Empire.'"

A modern historian's judgement, quotable as Palmyrene evidence with a citation
attached. Its own `translation_source` began "Summarized from". Field nulled,
content moved to `notes`, `reference_translation_note` records what happened. The
record's original was already a `pointer`, so it now contributes nothing to
retrieval — which is the honest state until Healey 2009/2014 is transcribed.

**`africa-01-ezana-stone`** was partial: genuine translated Greek titulature
followed by a bracketed editorial sentence summarising the untranscribed
remainder. Titulature kept, bracket moved to `notes`, `translation_source`
corrected — after the edit it no longer summarises, so it no longer says it does.

**Corpus is now 24 documents → 56 chunks** (was 57).

### The check that was warranted, and the one that was not

`ingest/verify` now reports a **REVIEW note** — not a failure — listing records
whose `translation_source` declares a summary while the chunk is classified
`translation`, excluding those already triaged. Vimose is triaged in the code with
its verdict written out: kept, because a hedged published reading presented with
its uncertainty intact is what an answer quoting it reproduces, and excluding it
would remove the only Scandinavian textual evidence in the corpus.

Verified to fire on an untriaged record and stay silent on a triaged one. It
exists so the audit does not have to be redone from scratch — only for records
nobody has looked at yet. **Making it a failure, or making it reclassify, would
have been the mistake the two candidate rules demonstrate.**

### Consequence: the floor needs re-validating

The sweep that set the floor ran against the 57-chunk corpus. The Palmyrene
translation chunk was **S6 in the `chinese-da-qin` evidence set**, so that case's
evidence has changed. The floor's numbers stand as a method; its observations are
now one corpus behind.

This is the corpus-versioning gap arriving on schedule — the same one the Aksum v1
row exposed. Re-run after re-ingest:

```powershell
python -m ingest.verify
python -m ingest.run_ingest          # expect 24 docs, 56 chunks
python -m ingest.run_embed           # a few chunks come back pending
python -m eval.run_answer_sweep --dry-run
python -m eval.run_answer_sweep --prompt-version p7-answer-v2r --repeat 3
```

15 chat calls, 5 embedding requests. Exits 1 if v2r no longer meets the floor.

## Part 8 — the finding that invalidated the floor, hours after it was set

The post-audit re-run put **v2r BELOW the floor**: `vimose-runes` 0/3 and refusal
rate 60%. The obvious reading is that the corpus edit broke something. **It did
not, and checking rather than assuming is the whole of this entry.**

### The evidence block is byte-identical

Six archived v2r runs of the Vimose question, three from each sweep. The
`sources_block` sha256 is **`0e1e32d21d4018c6` in all six**, same 694 characters,
same six chunks in the same order. The Palmyrene and Ezana edits never touched
this question's evidence.

| session | result |
| --- | --- |
| 19:12 | 7 resolved quotations, the sequences and hedges, **3/3 pass**, three byte-identical answers |
| 19:37 | refusal, 0 quotations, **0/3 pass** |

Same prompt version, same model, same evidence, temperature 0.

### Stable within a session, flipped between sessions

That is the shape, and it is worse than ordinary variance. Each sweep was
*internally* consistent — 3/3 one way, then 3/3 the other. So **three repetitions
inside one session measure a mode, not a distribution.**

Part 6's lesson was "one shot is one sample of a distribution nobody has looked
at." This is the same lesson one level up: **three shots in one session may also
be one sample.** Repetition was supposed to be the defence against exactly this
and it was not enough, because the repetitions were not independent.

The cause is not determinable from here — a provider-side serving change is the
likeliest explanation, and nothing in this repository can confirm it. What *is*
determined is that the evidence, the prompt and the corpus are excluded.

### What this costs

- **`floor.json` is now `calibrated: false`**, with `calibration_invalidated` and
  `session_caveat` recorded in the file. It stands as a **within-session
  regression gate** and nothing more.
- **`vimose-runes` stays a required case despite failing.** The failure is not a
  pipeline regression — the evidence is bit-identical. Dropping a case because
  the model had a bad session is how a floor is quietly lowered to whatever
  currently passes.
- **The v2r-over-v4 decision is narrower than claimed.** Both prompts ran in
  session 1, so that comparison is controlled and stands *for session 1*: v2r 3/3
  against v4 0/3 on identical evidence. Whether it holds under session-2
  conditions is untested — v4 was not re-run. The prompt decision rests on a
  controlled comparison in one session, which is more than it rested on before
  and less than it sounded like.

### The methodological correction

A sweep must record **when** it ran and treat same-session repetitions as one
observation. Any future calibration needs repetitions spanning sessions before
`calibrated` goes back to true. This is the fourth appearance of the same family
of defect — `embedding_model`, `prompt_version`, corpus version, and now session —
and every one of them was a case of *a result being comparable only within
something that was not being recorded.*

### Corpus state after the audit

24 documents → **56 chunks → 54 embedded**, 1 chunk pruned, 1 re-embedded.
Held back: 2 pointers (Palmyrene, Ezana originals). Non-English eligible: 18
across 7 languages, unchanged.

### Cheapest next measurement, if it is wanted

Re-run vimose alone under both prompts in one session — 6 chat calls — to see
whether the current mode affects v2r and v4 equally. That tests whether the prompt
decision generalises, without another 30-call sweep:

```powershell
python -m eval.run_answer_sweep --case vimose-runes `
    --prompt-version p7-answer-v2r --prompt-version p7-answer-v4 --repeat 3
```

## Part 8 milestone, honestly stated

The harness works, and the strongest evidence for that is unflattering: **it
caught its own calibration being invalid within hours of the floor being set.**
An eval that only ever confirms what its author expected has not been tested.

What Part 8 established:

- **Groundedness is not correctness, measured rather than argued.** Across 46
  archived answers the two metrics disagree in both directions — Aksum scored
  grounded while omitting what its own evidence prints in English; the Chinese
  answers scored NOT grounded while being accurate and well quoted.
- **A prompt decision, made from data rather than by eye.** v2r over v4 on
  identical evidence in a controlled comparison, and the reason rule 6 kept
  breaking things: it duplicated the `claims_on_untranslated` check and its
  guard condition can no longer arise from this corpus.
- **A floor that is a regression gate, not a definition of success**, with a
  known failure tracked and never subtracted.

What Part 8 did **not** establish:

- **That any of these numbers are stable across sessions.** They are not.
- **That the system answers the questions.** 3 of 5 gold questions pass reliably;
  Aksum has failed 7 consecutive times under 4 prompts with the answer sitting in
  its evidence block in English.

Nine defects were found by running things and none by writing them. Two of the
nine were in my own test code, and one cost 30 chat calls.

## Part 9 — starting point (for the next thread)

**State:** Parts 1–8 complete. 24 documents → **56 chunks → 54 embedded** with
`voyage/voyage-3.5`. Retrieval 11/11 probes at rank 1. Translation 12/12 gold
cases. Answers: every quotation in every grounded answer resolves to an absolute
character span in a named field of a named seed record.

Goal: a thin click-through UI. `ui/` is empty except `.gitkeep`.

### The reason this part matters more than it looks

**Nobody has looked at this system's output in a form a reader would use.**
Every judgement so far — including every judgement in this file — has been made
by reading JSON and terminal tables. Part 10 is kill / pivot / persevere, and it
cannot be answered from an exit code. The UI is the instrument for the only
question left: *is this worth continuing?*

There is also a standing risk this project has demonstrated repeatedly. Four
parts running ended with a larger offline suite, and Part 8's own plan line said
"build alongside 5–7" — it became the most elaborately instrumented part in the
repository while its actual deliverable, the floor, is now `calibrated: false`.
**Resist building measurement apparatus for the UI.** Make it clickable.

### What Part 8 hands you

- **`answer/run_answer.py --json`** — one question in, a full payload out:
  answer text, every passage with its English kind, band, flags and alignment
  ground, every resolved quote span with absolute character offsets, and the
  rendered sources block. The UI needs no new backend logic; it needs a view.
- **`assemble.ANSWER_PROMPTS`** — every prompt version's text, so the UI can
  report which contract produced an answer.
- **`eval/answer_runs/`** — 46 archived answers, real output to design against
  without spending a single call.
- **`eval/gold/answer_cases.json`** and **`floor.json`** — five questions with
  known-good and known-bad behaviour, ready-made as demo material and as a
  smoke test.

### Decisions Part 9 has to make

1. **What a citation looks like when you click it.** The project's whole claim is
   that a quotation resolves to `reference_translation[3073:3156]` of a named seed
   file. If the UI does not show that, it is displaying a chatbot. If it does, it
   is displaying the thing that was built.
2. **How to show a refusal.** Three of five gold questions currently produce a
   refusal at least sometimes, and one of them (Antikythera) is *correct*. A UI
   that renders refusals as failure will misrepresent the system; one that hides
   them will misrepresent it worse.
3. **Whether to surface the confidence machinery at all.** Bands, flags and
   alignment ground are dormant — all 18 non-English passages have aligned
   published English, so `resolve_english` never chooses `machine` from this
   corpus. Showing controls for something that never fires is misleading.
   Showing nothing loses the Part 6 work the moment Phase 2 adds material with no
   published English.
4. **Map or no map.** The reference model is ORBIS, which is a map. Nothing in
   Phase 1 has produced geography — the corpus has findspots and regions but no
   coordinates. Deciding this is a scope decision, not a UI decision.
5. **Who it is for.** A researcher checking provenance and a curious reader want
   different surfaces. The citation-span view is the former's; it may be noise to
   the latter.

### Known gaps, carried forward honestly

- **Session-level variance is unmodelled and large.** Identical evidence, prompt
  and model produced 7 quotations three times in one session and a refusal three
  times in the next. **A demo can therefore look excellent or threadbare on the
  same question depending on the day.** Design for that; do not be surprised by it.
- **`aksum-exports` fails 7/7 under 4 prompts** with the answer present in its
  evidence in English. Not a prompt or retrieval defect. Unexplained.
- **The floor is `calibrated: false`** and is a within-session regression gate.
- **The machine-translation path is dormant**; the Part 6 confidence machinery is
  exercised only by offline tests.
- **Two records held back as `pointer`** — Palmyrene Tariff and Ezana Stone
  originals, both awaiting a transcription pass.
- **Retrieval ranking is imperfect**: the Muziris question's top hit is the wrong
  Periplus section, and the Vimose record ranks third for its own question.
- **`akananuru-149` translation is an excerpt**, not the full poem — noticed
  during the audit, not investigated.

### Standing lessons from Parts 3–8

- Parse-level SQL checks miss type inference; anything with optional/NULL
  parameters needs one execution against the real database.
- A test that passes for the wrong reason is worse than one that fails. Assert on
  the specific thing, not a proxy — `expect_cited_docs` said the model *named* a
  source, and only `expect_quoted_docs` says it used one.
- **Run the thing against what it will actually receive.** The Part 8 scorer was
  tested only against archived payloads and had never seen a live one; the shapes
  differ and it cost 30 chat calls.
- Mutation-verify every guard, and expect misses. Twice a mutation showed a
  verdict could not pin a single assertion, and both times the guard doing the
  work was the one checking what the failure *names*.
- **Prefer a check to a rule.** Rule 6 duplicated `claims_on_untranslated` and
  cost the Vimose question 6 runs out of 6 across two prompt versions.
- When two prompt versions in a row fail to fix a behaviour, the problem is not
  in the prompt.
- Place a threshold where no observed case straddles it — then confirm with
  repetitions **that span sessions**, because same-session repetitions are
  correlated.
- **A result is comparable only within the thing that produced it**, and that
  thing must be recorded: `embedding_model`, `prompt_version`, corpus version,
  session. Four instances, four defects.
- Archive runs, not verdicts. It has now paid for itself three times, once in
  money.
- The gateway's free tier is 3 requests/minute. Batch aggressively.
- Two PowerShell windows, both needing `cd` + venv activate + `.env` load. See
  `STARTUP.md`.

### To run (Windows / PowerShell, repo root, gateway up on :4000, db up)

```powershell
# offline, free
python -m answer.test_answer                 # Part 7, 133 assertions
python -m answer.test_translate              # Part 6, 104 assertions
python -m eval.test_answer_eval              # Part 8, 70 assertions
python scripts\test_recover_baseline.py      # 45 assertions
python scripts\mutate_part7b.py              # 13 mutations
python scripts\mutate_part8.py               # 11 mutations
python scripts\mutate_recover.py             # 11 mutations

# state, database only
python -m ingest.verify                      # 24 docs, 56 chunks
python -m ingest.run_ingest --stats
python -m ingest.run_embed --stats           # embedded 54, pending 0
python -m eval.answer_eval --archives --by-case
python -m eval.rescore_sweep                 # re-score + floor, no API calls

# spends calls
python -m answer.run_answer --json "..."     # 1 embedding + 1 chat call
python -m eval.run_answer_sweep --dry-run    # 5 embeddings, no chat call
```

**Design the UI against `eval/answer_runs/` first.** Forty-six real payloads are
on disk, including the best answer this project has produced and the worst, and
they cost nothing to read.

## Part 9 — what's in place (built 2026-08-12)

The UI opens by double-clicking `ui/index.html`. No server, no build step, no
CDN, no framework. It reads `ui/data.js`, which is generated from the 61
archived runs and the 24 seed records.

### Code

| File | Role |
| --- | --- |
| `ui/build_ui_data.py` | Joins `eval/answer_runs/*.json` to `data/seed_corpus/**/*.json`, classifies every claimed character span, writes `ui/data.js`. `--verify` checks and writes nothing. |
| `ui/index.html` | The whole UI. Three views: Questions, Regions & sources, What you are looking at. |
| `ui/check_ui.mjs` | Headless smoke test: runs the page's own render functions over every archived run in `node:vm` with a thin DOM shim. |
| `ui/data.js` | Generated, 657 KB. Not hand-edited. |

### Design decisions

- **The join was not optional.** A run payload records that a quotation lives at
  `reference_translation[7:48]` of a named record. It does **not** record what
  those characters are — `english.text` is the passage the model was shown, and
  for a non-English passage that is a different string from the seed field the
  offsets index. So a UI built from the payloads alone can print `[7:48]` and
  cannot show what sits there. That is the difference between claiming provenance
  and demonstrating it, and demonstrating it was the whole brief.
- **`data.js`, not `data.json`.** Browsers refuse `fetch()` from a `file://`
  page — a null-origin cross-origin request no header on a local file can
  permit. A `<script src>` has no such restriction. The cost is one assignment
  line; the benefit is that the page needs no server, which matters because the
  point of this part is that somebody can look at the thing.
- **Both archive shapes are kept as they are.** The 32 `-recovered` payloads
  carry a thinner passage record with no `lang`, `region` or `citation`.
  Normalising them into the richer shape would put invented provenance into a
  provenance viewer. They are marked `partial_passages` and the UI says so, then
  falls back to the seed record for those fields.
- **Every run of a question is shown, none is chosen.** The picker lists all of
  them with their prompt version and time, dotted by outcome. Part 8 established
  that the same question, prompt and evidence produced 7 quotations three times
  in one session and a refusal three times in the next; a UI that displayed one
  "best" answer would be hiding the single most important thing this project
  learned. The default selection prefers a run that quotes, because an empty
  first screen misrepresents the system just as badly as a curated one.
- **Refusals render as results, not failures.** No red, no error styling: a
  neutral badge, a sentence saying the sources did not contain the answer, and
  the evidence it consulted listed below so the reader can judge the refusal.
  The Antikythera refusal is correct behaviour and now looks like it.
- **The confidence machinery is shown and labelled dormant.** Every non-English
  passage in this corpus has aligned published English, so `resolve_english`
  never returns `machine` and every band is null. The panel says exactly that,
  including that the path exists and is exercised only by offline tests. Hiding
  it would lose the Part 6 work the moment Phase 2 adds material with no
  published translation; showing live-looking controls for something that never
  fires would be a lie.
- **Regions, not a map.** The corpus has findspots as prose and regions as
  labels, and no coordinates. The Regions view groups the 24 records by region
  and says in as many words why there is nothing honest to plot yet. ORBIS is a
  map; this is not one, and the decision is recorded on screen rather than left
  to be inferred from an absence.
- **No measurement apparatus.** The Part 9 brief warned that four parts running
  ended with a bigger offline suite than deliverable. `check_ui.mjs` checks three
  things and stops.

### The span audit, which is the finding

`build_ui_data.py` re-checks every archived citation against the seed corpus **as
it stands today** — a different question from the one Part 7 answered, which was
whether the span held at the moment the answer was produced.

| | spans |
| --- | --- |
| resolved — the characters at the offset are the quoted characters | **132** |
| case_only — differ from the quotation only in letter case | **6** |
| moved — quote still in the field, at a different offset | 0 |
| absent — quote not in the field at all | **1** |

**1. The `absent` one is corpus drift, and it is the failure a naive viewer would
render silently and convincingly.** `africa-03-periplus-adulis.reference_translation[409:628]`
was quoted correctly on 2026-08-10 at 12:46. Later that day the record's
abridged translation — the one with `...` elisions — was replaced with Schoff's
full §4-6. The archived answer quotes `"...Berbers... wine of Laodicea and
Italy..."`, which no longer exists in the file, and those coordinates now hold a
passage about anchoring at Diodorus island. A viewer that trusted the offsets
would have displayed that passage as though the answer had quoted it, and it
would have looked perfect.

This is the **fifth** appearance of the family of defect this file has been
tracking: `embedding_model`, `prompt_version`, corpus version, session, and now
corpus version again one layer out. *A result is comparable only within the thing
that produced it, and that thing must be recorded.* An archived answer records
its model, both prompt versions and its embedding model. It does not record which
version of the corpus it was quoting.

**2. The 6 `case_only` spans are a labelling defect in `cite.py`.**
`locate_in_text` tries an exact search, then falls back to `_fold()` — a
case-insensitive search — and returns the span with `match="exact"` either way.
The docstring says a fallback match is marked; the NFC path is, the case-folded
path is not. The span is correct; the label overstates what was found. Six runs
of the Hou Hanshu question quote `"the tribute brought was neither precious nor
rare…"` where the file has `"The tribute…"`. Low impact, but a viewer that prints
"exact" beside two visibly different strings discredits itself, so the UI shows
the state and the reason instead. **Not fixed here** — it is a Part 7 change and
Part 9 was told to stay out of the machinery.

### What `check_ui.mjs` checks

Runs the page's real render functions — not a reimplementation — over all 61
runs, 505 provenance panels and 24 record panels, then asserts four things about
what ends up on screen:

- every quotation that appears in an answer's prose is actually highlighted
  (139/139) — a quote silently dropped is precisely the failure this page exists
  to rule out;
- every `[Sn]` marker resolves to a source card, and the count agrees with the
  grounding report's own `unknown_markers`;
- every span classified `resolved` genuinely holds its quote, re-derived from
  `data.js` rather than trusting the Python that wrote it;
- the headline audit on the About tab matches the spans in the bundle.

All passing.

### To run

```powershell
python ui\build_ui_data.py            # regenerate ui/data.js
python ui\build_ui_data.py --verify   # audit spans only; exit 1 if any break
node ui\check_ui.mjs                  # headless render of all 61 runs
start ui\index.html                   # open it
```

`build_ui_data.py` needs no database, no gateway and no API calls. Neither does
the UI. Re-run the builder after any corpus edit — that is what would have caught
the Adulis drift the day it happened.

### Still open after Part 9

- **No live question box.** Decided: static first. The `/ask` endpoint wrapping
  `answer/run_answer.py` is the obvious next increment and was deliberately not
  built, because every design iteration against it costs a chat call and the view
  was not yet settled.
- **Corpus version is still not recorded in an answer.** The Adulis span is the
  evidence that it should be. A content hash of the seed record at answer time,
  stored beside `prompt_version`, would turn a silent wrong render into a
  detectable one at the point it happens rather than two days later.
- **`cite.py` reports case-folded matches as exact.** Six spans affected.
- **`aksum-exports` still fails**, and now fails visibly: the UI shows it failing
  with the answer sitting in its own evidence in English.

## Part 9 — first reading, and the Aksum diagnosis (2026-08-12)

The UI was read as a reader for the first time. Cross-lingual display (Old Tamil,
Literary Chinese) reads well; the "what you are looking at" framing of the broken
Adulis citation reads as honesty rather than alarm. One change made: the refusal
copy was too defensive and is now two sentences — *"These sources don't answer
this question. Rather than fill the gap, the system says so. Everything it
searched is listed below."* Badge reads `no answer in these sources`.

### `aksum-exports` is not unexplained any more

Reading the 13 archived Aksum runs together — free, no API calls — identifies the
failure precisely. **It is a reading failure, not a retrieval, prompt or corpus
failure.**

The model is shown, in S1, in English, inside a 1,419-character block:

> "There are exported from these places ivory, and tortoise-shell and
> rhinoceros-horn."

and then refuses on the ground that the sources *"detail what Rome exported to
Aksum rather than what Rome imported from it"* — a statement that is false about
the passage printed directly above it. Three measurements say why:

| | |
| --- | --- |
| position of the export sentence | 82% through the block, unit **17 of 19** |
| `imported` vs `exported` in the block | **3 : 1** |
| identical refusal text | **7 of 13 runs**, across two sessions and two prompt versions |

The third row is the important one. This is **not** the session variance that
flipped the Vimose question 3/3 → 0/3; it is stable across exactly the boundary
that broke everything else. A deterministic misreading is why prompts v2, v3 and
v4 all failed to move it, and the standing lesson already covers it: *when two
prompt versions in a row fail to fix a behaviour, the problem is not in the
prompt.*

### Corrected 2026-08-12: it is the fold, not the chunker

The first instinct was to split the Adulis English at the `§` boundary. **That
would have been a corpus edit fixing nothing**, and checking before spending the
calls is the whole of this entry. `chunk_field` already splits
`reference_translation` into six chunks, and chunk 5 — `[3073:3333]` — *is* the
export sentence, standing alone. It is already its own passage.

Reading `fold_hits` and `align._merge` together shows what really happens:

1. Retrieval **found the export chunk**. `folded[origin] = record.chunk_id`
   records the retrieved member, and the archived payload names
   `::translation::005` — the 260-character export passage. Retrieval got this
   question exactly right.
2. `fold_hits` folded that hit into its Greek original `::original::002`, and
   `align._merge` then presented the model with **the whole of §6** — chunks 004
   and 005 concatenated, 1,419 characters — rather than the 260 characters that
   actually matched.
3. So the winning passage arrived buried at 82% of a block dominated by the
   import list, and the model read the block, not the hit.

Merging was deliberate, and the reason is in the code comment: without it *"a
section split into several English chunks would otherwise surface its later
chunks as separate sources repeating what the first one already said."* That is a
sound de-duplication argument. **Its cost was never measured: the retrieved
passage loses its salience inside the section it belongs to.** This corpus has
exactly one record where an English section outsplits its original, and it is the
one question that has never worked.

**A latent trap found on the way.** `translation_chunk_id` and
`translation_chunk` are not the same object. The id is the *retrieved member*
(`::005`, char_start 3073); the record is the *merged section* (`::004`,
char_start 1914). `cite.py` uses the record, so the arithmetic is right — the
export sentence resolves to `[3073:3156]` as the gold case says. But anything
that read `translation_chunk_id` and assumed the offsets were relative to *that*
chunk would compute 4232 on a 3333-character field. Nothing does today. The UI
reads `quote_spans` and is unaffected. Worth renaming before something does.

**Corrected cheapest test — one chat call, no code and no corpus change:**

```powershell
python -m answer.run_answer "What was exported from Adulis?"
```

Same evidence, sharper question. If it answers with ivory, tortoise-shell and
rhinoceros-horn, the model *can* see the sentence and the failure is burial plus
question framing. If it still refuses, burial alone is decisive and the fold is
the thing to change.

### A convergence worth recording

The single broken citation in the whole archive — the one Adulis span that no
longer resolves — belongs to the **12:46 Aksum v1 run**. That is not a
coincidence. v1 refused because the aligned English genuinely was not there yet,
which was *correct under the corpus it saw*; the record was then replaced and its
citation now dangles. The gold case had already predicted this in
`archived_status` ("Do not weaken the case to accommodate v1 — record the corpus
version instead"), and the Part 9 span audit produced the evidence for it
independently, from the other direction. Two routes to the same missing field:
**an answer does not record which corpus version it quoted.**

## Part 10 — starting point (for the next thread)

**State:** Parts 1-9 complete. 24 documents → 56 chunks → 54 embedded. Retrieval
11/11. Translation 12/12. Answers: 132 of 139 archived citations still resolve to
characters on disk; 1 fails for a known and now-understood reason; 6 differ only
in letter case through a `cite.py` labelling defect. The UI exists, opens with no
server, and has been read.

Goal: kill / pivot / persevere.

### The one measurement Phase 1 never made

Part 8 ended with: *"What Part 8 did not establish: that any of these numbers are
stable across sessions. They are not."* The correction it prescribed was
repetitions **spanning sessions** before anything is called calibrated. Every
archived run is from 2026-08-10. Nothing has been run since.

So a sweep today is not a repeat — it is the **third session, two days later**,
and the first cross-session measurement this project has ever had. It bears
directly on the exit-gate question, because "persevere" partly means "this is
stable enough to build on", and that has not been tested. ~15 chat calls:

```powershell
python -m eval.run_answer_sweep --prompt-version p7-answer-v2r --repeat 3
```

Three outcomes and what each would mean:

- **Matches the 19:12 session** (Vimose 3/3, ~7 quotations) — the 19:37 collapse
  was a transient provider-side episode. The floor can be recalibrated across
  sessions and `calibrated` can go back to true.
- **Matches the 19:37 session** (Vimose 0/3, refusals) — the earlier session was
  the anomaly and the system is weaker than the best archived output suggests.
- **A third pattern** — session is a larger free variable than two samples
  showed, and that is itself the finding the exit gate needs.

Do this before deciding. A kill/pivot/persevere call made on two-day-old data
from a system with known session-level variance is a call made on one sample.

## Part 10 — the cross-session sweep and the discriminator (2026-08-12)

Two measurements, run on the host in one session two days after everything else
on disk. Recorded here as findings; the exit-gate verdict is not yet written.

### The discriminator settled it, and against the stated hypothesis

`python -m answer.run_answer "What was exported from Adulis?"` — **grounded, two
resolved quotations**, the first being *"there are exported from these places
ivory, and tortoise-shell and rhinoceros-horn"* at
`reference_translation[3073:3155]`.

The passage it quoted is **S3 = `africa-03-periplus-adulis::original::002`** —
the same chunk, carrying the same merged 1,419-character §6, that the Aksum
question is given as S1 and refuses on. Identical evidence, opposite outcome.

**So burial is not the cause and the fold is not the bug.** The hypothesis in the
previous entry was wrong, and one chat call was enough to say so. `align._merge`
should be left alone.

What differs is the question. `"What was exported from…"` shares its wording with
the sentence itself (*"There are exported from these places…"*); `"What did Rome
trade with the Kingdom of Aksum?"` shares its wording with the import list, which
is three times longer and comes first. The model anchors on the longer, earlier,
lexically-matching material, concludes the passage is about goods going *to*
Aksum, and stops — then explains itself with a statement that is false about the
text printed above it.

**The corrected diagnosis: the answers are in the corpus, and the failure is in
how a question's phrasing maps onto passage wording.** That is a retrieval and
prompting problem, not a data problem — which matters for the exit gate, because
the corpus is the expensive asset and it is sound.

### The cross-session sweep — the good session was the outlier

`--prompt-version p7-answer-v2r --repeat 3`, 5 embeddings + 15 chat calls.

| case | content | grounded | quotes | distinct texts |
| --- | --- | --- | --- | --- |
| muziris-cargo | **3/3** | 3/3 | 5 | 3 |
| chinese-da-qin | **3/3** | 0/3 | 3-4 | 3 |
| antikythera-absent | **3/3** | 3/3 | 0 | 3 |
| vimose-runes | 0/3 | 1/3 **!** | 0-1 | 2 |
| aksum-exports | 0/3 | 3/3 | 0 | 1 |

Content 60%, grounded 67%, refusal 60%. **BELOW THE FLOOR** — vimose 0/3 on a
required case, refusal rate over 50%.

Set against the two sessions of 2026-08-10:

| session | vimose-runes |
| --- | --- |
| 19:12 | 3/3, seven resolved quotations |
| 19:37 | 0/3, refusals |
| 2026-08-12 | 0/3 content, 1/3 grounded, unstable |

**Two of three sessions produce the degraded behaviour.** The 19:12 run — the
best output this project has ever produced, and the one that made it look most
convincing — is the outlier, not the norm. That is the answer to the question
Part 8 left open, and it is the unflattering one.

### What is stable, which the headline rate hides

Three of five cases behaved identically across all three sessions.
`muziris-cargo` returned exactly five resolved quotations every repetition of
every session. `antikythera-absent` refused correctly every time.
`chinese-da-qin` passed on content 3/3 while scoring `grounded` 0/3 — the Part 8
finding that groundedness is not correctness, reproduced a third time; that is a
scorer disagreement, not a wrong answer.

So the instability is concentrated in **`vimose-runes`**, and the two content
failures have known and different causes. The system is not uniformly 60%
reliable; it is near-deterministic on most cases and genuinely unstable on one.

## Part 10 — RESULT: PERSEVERE, with a framing correction (2026-08-12)

**Decision: persevere.** Not because the numbers are good — the sweep came in
below the floor — but because of *where* the failures sit. The expensive,
hard-to-rebuild parts work. The failing parts are the cheap, iterable ones.

### The evidence the decision rests on

**What is reproducible across three sessions spanning two days:**

- An English question retrieves a Literary Chinese, Parthian, Old Tamil or Greek
  source at rank 1, with English translations excluded from the candidate pool so
  the match cannot be English-to-English. 11/11 probes. This is the project's
  central claim and it has never failed.
- `muziris-cargo` returned **exactly five resolved quotations on every
  repetition of every session** — nine consecutive runs, no drift.
- `antikythera-absent` refused correctly every time. The system knows when its
  corpus does not contain an answer.
- **132 of 139 archived citations still resolve to exact characters on disk**,
  re-checked against the corpus as it stands today rather than as it stood when
  the answers were made.
- The provenance chain is end-to-end and visible: quotation → seed field →
  absolute offsets → the characters themselves, in a UI that opens with no
  server.

**What fails, and why each failure is survivable:**

| failure | cause | cheap to fix? |
| --- | --- | --- |
| `chinese-da-qin` grounded 0/3 while content 3/3 | scorer disagrees with a correct answer — the Part 8 "groundedness is not correctness" finding, reproduced a third time | yes — scorer, not system |
| `aksum-exports` 0/3 | question phrasing anchors on the longer, earlier import list; **the same evidence answers correctly under a reworded question** | yes — retrieval/prompt layer |
| `vimose-runes` unstable, 1/3 | genuine session-level nondeterminism | no — but isolated to one case |
| refusal rate 60% | tidiness bought with silence | tied to the two above |

**The decisive fact for the exit gate:** the Adulis discriminator proved the
answers *are in the corpus*. The system refused a question whose answer it was
holding, then answered correctly when the question was reworded against identical
evidence. **The corpus — the expensive asset, the one that took Parts 2, 3 and 3b
and still has two records held back — is sound. The failures are in the layer
above it, which is the layer that costs least to change.** That asymmetry is the
whole argument for persevering.

### The framing correction

Phase 1 did not build an ORBIS. It built something else, and the something else
is more defensible: **a cross-lingual, provenance-grounded sourcebook** in which
an English question reaches a Parthian inscription and every quotation resolves
to named characters in a named file.

The map was never built because the corpus has no coordinates and Phase 1
produced no reason to think they were coming cheaply. That has now been examined
rather than assumed, and the conclusion reverses: **geography is cheap and should
be built next.** 17 of 24 records carry named findspots; the 7 without are all
literary and carry the richest *subject* geography instead. Pleiades supplies
stable, cited, CC-BY place identifiers, and ToposText — already 3 of the 24
citations — is built on it. A place becomes a citation like everything else,
which is the ethic the whole project already runs on.

So the correction is not "abandon the map". It is: **the product is a sourcebook
that has geography, not a map that has sources.** Region-level placement has
value on its own — the UI groups by region today — and the ladder from region to
named place to Pleiades ID to coordinates has a usable rung at every step,
without ever claiming precision the evidence does not carry.

### The finding that sets the Phase 2 order

Retrieval margins across 77 archived runs: mean top-1 to rank-6 spread **0.105**,
and on the questions that matter 0.045–0.094. The Adulis export answer arrived at
**rank 3, 0.012 below top-1**.

At 200 documents the eligible-chunk count goes from 54 to roughly 450 — about 8×
the density inside that same narrow band. Today's rank-6 chunk lands near rank
40–50; the chunk that answered the Adulis question lands near rank 20 and, at
`max_sources` 6, never reaches the model.

**Scaling the corpus without first hardening retrieval will make the demo worse,
not better.** And the current 11/11 probe result cannot warn of this: with 54
chunks nearly everything relevant is retrieved, so the probes measure *is it in
the corpus*, not *is it ranked*. Same class as `expect_cited_docs` versus
`expect_quoted_docs` — a metric passing for a reason adjacent to the one that
matters. Ranking quality is, as of today, **unmeasured**.

### What would trigger a kill later

Recorded now, while the decision is fresh and before anyone is invested in the
outcome:

1. **Retrieval hardening fails to hold the answer in the top 6 at 60 documents.**
   That is the first tranche and the first honest test of ranking. If a
   cross-encoder reranker plus hybrid retrieval cannot keep known-good passages
   in the window at 2.5× scale, 200 is not reachable and the product is
   corpus-bound.
2. **Session variance stays unattributable at 30 gold questions.** The stated
   reason for scaling the gold set is to separate "bad session" from "bad case".
   If it does not separate, Phase 2 cannot be steered and every subsequent
   improvement is unfalsifiable.
3. **Curation cost per record does not fall.** 24 records consumed three parts
   and two remain held back. If record 60 costs what record 12 cost, 200 is a
   staffing question, not an engineering one.

None of these is a prediction of failure. They are the conditions under which
persevering would stop being the honest call.

---

# Phase 1 — closing summary

Nine working parts and an exit gate, 2026-08-04 to 2026-08-12. What follows is
the whole of Phase 1 as it would be told to someone who had not read the 2,900
lines above.

## What was built

A pipeline that takes an English question and returns an English answer in which
every claim carries a citation and every quotation resolves to an absolute
character range in a named field of a named file — where the file may be in
Koine Greek, Literary Chinese, Old Tamil, Parthian, Nabataean Aramaic, Sabaic or
Proto-Norse.

| | |
| --- | --- |
| corpus | 24 primary sources, 7 regions, 10 languages, 56 chunks |
| embedded | 54 chunks, `voyage/voyage-3.5`, 1024-dim, HNSW cosine |
| held back | 2 (`pointer` records: Palmyrene Tariff, Ezana Stone originals) |
| translations | 20 rows with model, both prompt versions and a source-text hash |
| archived answers | 61, spanning 5 prompt versions and 3 sessions |
| offline assertions | 307 across four suites, plus 35 mutation checks |
| UI | one HTML file, no server, no build step, no CDN |

## What was proven

1. **Cross-lingual retrieval works, and it is the project's central claim.** An
   English question retrieves a Literary Chinese or Parthian source at rank 1
   *with English translations excluded from the candidate pool*, so the match
   cannot be English-to-English. 11/11 probes. The same question asked in English
   and in Greek returns the same document.
2. **Provenance survives the language boundary.** A quotation in an English
   answer traces to characters on disk in the source language or in a named
   published translation, and the two are distinguished. 132 of 139 archived
   citations still resolve today.
3. **The system knows when it does not know.** `antikythera-absent` refused
   correctly in every repetition of every session.
4. **Translation confidence can be scored without a reference.** Forward
   translation, back-translation that provably never sees the original, two
   independent signals, genre-relative bands. 12/12 gold cases — including one
   that passes by being correctly refused as untranslatable.

## What was not proven

- **Stability across sessions.** Identical evidence, prompt and model produced
  seven quotations three times in one session and a refusal three times in the
  next. A third session two days later matched the worse one. **The best output
  this project has produced is the outlier, not the norm.**
- **That the corpus is big enough**, or that ranking survives it being bigger.
  Retrieval quality is, as of the end of Phase 1, *unmeasured* — with 54 chunks
  nearly everything relevant is retrieved, so the probes test presence, not rank.
- **That groundedness tracks correctness.** They disagree in both directions, and
  this was measured rather than argued.

## The one number that should worry you

Mean top-1 to rank-6 similarity spread across 77 archived runs: **0.105**. On the
questions that matter, 0.045–0.094. The Adulis answer arrived at rank 3, 0.012
below top-1. At 200 documents that chunk lands near rank 20 and never reaches the
model. **The corpus cannot be scaled before ranking is hardened**, and nothing in
Phase 1 could have told you that — it took the UI work to go looking.

## How the defects were found

**Roughly thirty defects across Phase 1. Almost none were found by writing code;
they were found by running it, and several by running it a second time.**

The recurring one, five times over: **a result is comparable only within the
thing that produced it, and that thing must be recorded.** It appeared as
`embedding_model` (cosine across two models is meaningless), `prompt_version`
(one prompt's output overwriting another's evidence), corpus version (an archived
citation pointing into a record that had since been replaced), session (three
repetitions inside one session measure a mode, not a distribution), and corpus
version again from the other direction. Four of the five were caught only because
something downstream contradicted itself.

The second recurring one: **a test that passes for the wrong reason is worse than
one that fails.** A probe matched on `doc_id` and passed against the wrong
passage. `expect_cited_docs` proved the model *named* a source; only
`expect_quoted_docs` proves it used one. A script-mismatch flag added in the
morning failed that afternoon because it compared Latin to non-Latin when the
real error was Devanagari answering Tamil.

## What Phase 1 got wrong, in order

- **Breadth over depth.** The showcase brief said start with Rome ↔ Persia. All
  seven regions were built at 3–4 records each. That bought a stronger
  cross-lingual result across ten languages, and it is why no region is deep
  enough to support a connection — which is the bill Phase 2 pays.
- **Thresholds anchored on the wrong distribution.** Four confidence profiles
  were set from Part 4 *retrieval* numbers, then found to sit below the entire
  observed range of a much easier comparison.
- **Measurement apparatus outgrowing the deliverable.** Part 8 became the most
  instrumented part in the repository while its actual output, the floor, ended
  `calibrated: false`. Part 9 was explicitly written to resist this.
- **Two hypotheses stated confidently and refuted by one cheap check each** — the
  Aksum "burial" theory, and the chunker being blamed for what `align._merge`
  was doing. Both cost one call to disprove. Neither would have been caught by
  reasoning harder.

## Carried into Phase 2 as known debt

| item | where |
| --- | --- |
| Ranking quality is unmeasured | PHASE2 W2 |
| Corpus version is not recorded in an answer | PHASE2 W3 |
| `cite.py` reports case-folded matches as `match="exact"` (6 spans) | PHASE2 W2 |
| `translation_chunk_id` names the retrieved member; `translation_chunk` is the merged section | PHASE2 W2 |
| Floor is `calibrated: false`; a within-session gate only | PHASE2 W4 |
| `verse` and `documentary` confidence profiles at n=1 | PHASE2 W3 |
| 2 records held back for want of an open transcription | PHASE2 W3, candidate HTR spike |
| `akananuru-149` reference translation is an excerpt, not the full poem | PHASE2 W3 |
| Machine-translation path dormant — exercised only by offline tests | PHASE2 W3 |
| No geography of any kind | PHASE2 W1 |

## The verdict, in one paragraph

Persevere. Not because the sweep passed — it came in below the floor — but
because of where the failures sit. The corpus, the provenance chain and the
cross-lingual index are the expensive, hard-to-rebuild assets, and they work. The
failures are in ranking, question handling and scoring, which are the cheapest
layers to change. The proof is the Adulis discriminator: the system refused a
question whose answer it was holding, and answered correctly when the question
was reworded against byte-identical evidence. That asymmetry — sound foundations,
fixable surface — is the whole argument, and it is the only argument being made.

---

# Phase 2 — Block 0: reconcile the state (2026-08-12)

The plan's first block was meant to be bookkeeping: confirm the corpus triple,
run every offline suite, and correct whichever document had drifted. It found
four defects instead, and the two that matter were both being reported through a
message that named the wrong cause.

## The corpus state, confirmed on the host

**24 documents → 56 chunks → 54 eligible → 54 embedded** with
`voyage/voyage-3.5`, `pending: 0`, all seven regions, 18 non-English chunks
across 7 languages. `answers`: 28 rows, 18 grounded, 68 citations used, 30
quoted.

`README.md` and `PHASE2.md` were right. **`STARTUP.md` was wrong** — it claimed
57 chunks / 55 embedded, written at a corpus state that no longer existed and
never revised. Corrected. This is the fifth appearance of *a result is comparable
only within the thing that produced it*, in its mildest form: the number was
recorded, then the thing it described moved.

It mattered because the W2b distractor curve is denominated in chunk counts
(54 → 150 → 450). A baseline against an uncertain denominator is not a baseline.

## 1. The repository was not under version control

There is a `.gitignore`. There was no `.git`. Thirteen thousand lines, thirty
documented defects, nine parts, and three mutation scripts — `mutate_part7b.py`,
`mutate_part8.py`, `mutate_recover.py` — whose entire method is to **rewrite
source files in place and restore them from an in-memory copy**. A crashed
interpreter between the write and the `finally` would have destroyed the file
with no way back.

Worse, the `.gitignore` that was waiting read `data/**`, with the comment in
`README.md` explaining it as "large blobs git-ignored". There are no large blobs.
`data/` is **28 files, 140K** — the seed corpus, which the Phase 1 closing summary
names as one of the expensive, hard-to-rebuild assets the whole persevere verdict
rests on. The first commit would have excluded it.

Rewritten to ignore large or derived artefacts by name, and to keep the corpus,
`eval/runs/`, `eval/answer_runs/` and `eval/sweeps/` tracked — *archive runs, not
verdicts*. `ui/data.js` is tracked deliberately despite being derived and 673K:
`--verify` is a criterion at G1 and G3, and having the bundle in history is what
lets a gate result be compared against the thing that produced it.

## 2. `ingest/test_embed.py` had been truncating itself since Part 6

The suite crashed at line 259 on
`from retrieve.crosslingual_check import PROBES, Probe, rank_of`. Part 6 moved
the probes out into `eval/gold/retrieval_probes.json`; `crosslingual_check.py`
now calls `load_probes()` internally and no longer exports `PROBES`. The name
went away. The import did not.

Because the import sat two-thirds of the way down `main()`, the `ImportError`
did not announce a broken dependency — **it truncated the test run**. Every
assertion below that line stopped executing on 2026-08-10 and nothing reported a
failure. That included both guards `README.md` credits this file with:

- the **doc-id-proxy probe bug** — the guard for the false PASS where a probe
  matched on `doc_id` and passed against the wrong passage;
- the **missing `::text[]` cast** — the guard for the `AmbiguousParameter` defect
  from Part 4, which parse-level checking cannot reach.

Five assertions, dead for two days, guarding two of the defects this project has
already paid for once.

Fixed by moving the import to module scope. **A missing dependency should fail at
load, loudly, not silently shorten the test run** — that is the reusable lesson,
and it is a new one. All five assertions now run and pass.

This is the sharpest instance yet of *a guard that has never been seen to fail is
not known to work*, because these guards were not merely unexercised — they were
**unreachable**, while the README went on advertising them.

## 3. Three mutation scripts reported the wrong cause

`mutate_part8.py` ended with `- sources were not restored cleanly`, which reads
as a corrupted working tree — the worst possible message on a repository that
turned out to have no version control.

The restore was perfect. The check was:

```python
check = subprocess.run([sys.executable, "-m", "eval.test_answer_eval"], ...)
if check.returncode != 0:
    problems.append("sources were not restored cleanly")
```

Any non-zero exit from the post-restore suite was attributed to the restore.
`mutate_part7b.py` and `mutate_recover.py` carried the identical pattern and
happened not to fire.

**Same defect family as Part 4's Voyage rate limit reported as a dead gateway.**
A check that matches too broadly produces a message pointing at something
healthy, and the real finding goes unread. That is now twice.

Fixed in all three: restore is verified by comparing file content against the
originals, suite failure is reported separately, and the suite's own output is
printed rather than discarded.

## 4. The evidence the persevere verdict rests on has no gold case

With the message corrected, the real failure surfaced — 2 of 70 assertions in
`eval.test_answer_eval`:

```
FAIL every archived run is scored (76 of 77)
FAIL every archived question has a gold case
      ['20260812T133627+0000-53afe41c.json: What was exported from Adulis?']
```

That run is from the exit-gate session. It is `grounded: true`, and it quotes the
Periplus verbatim: *"there are exported from these places ivory, and
tortoise-shell and rhinoceros-horn."*

`eval/gold/answer_cases.json` contains `aksum-exports` — "What did Rome trade
with the Kingdom of Aksum?" — the question that was **refused**, correctly kept
in as a known failure. It does not contain the rewording that **worked**.

The closing summary above states the argument for persevering: *the system
refused a question whose answer it was holding, and answered correctly when the
question was reworded against byte-identical evidence.* **Only the failing half
of that discriminator is in the gold set.** The successful half is an unscored
archived run. The harness noticed immediately and said so; the message was routed
through a mutation script that called it a restore failure, and it went unread
through the exit gate.

Nothing in the verdict changes — the run is on disk and it is sound. What changes
is that the claim is currently an anecdote rather than a regression test. Adding
`adulis-exports` as an **answerable** case, paired explicitly with
`aksum-exports`, is the first item of Phase 2 W4 (`PHASE2_PLAN.md`, Block D).

## Also found

- **`node` is not installed on the host**, so `ui/check_ui.mjs` could not run.
  Not urgent today; Block A's G1 needs it.
- **The `--verify` counts have drifted with the archive**, not with any defect:
  **77 runs / 168 spans / 158 resolved / 9 case_only / 0 moved / 1 absent**
  (was 132/6/0/1 over 61 runs). The 9 `case_only` are **one** span,
  `eastasia-02-hou-hanshu.reference_translation[391:516]`, recurring across nine
  runs — one defect, counted nine times, and the count will keep growing until
  `cite.py` gains its third match state in W2. Worth knowing before reading that
  number as nine problems.
- **`0 moved`** — so W1 is clear to begin editing seed records.

## Standing lessons added

- **A missing dependency should fail at load, not shorten the test run.** An
  import inside a function turns a broken reference into a partial pass.
- **A check that matches too broadly names the wrong cause**, and the real
  finding goes unread. Second occurrence; the first cost an afternoon chasing a
  healthy gateway, this one hid a defect in the gold set through an exit gate.
- **Version control is a guard too**, and it was the one guard this project never
  had while running scripts that deliberately damage source files.

## Block 0 exit

Corpus state confirmed and documented. All offline suites pass; all 35 mutation
checks verify. Three of four defects fixed. `git init` and the `adulis-exports`
gold case remain, both on the host.

## Block 0 addendum — the UI bundle was stale, and its checker said so was fine

Found while confirming the baseline commit. `ui/build_ui_data.py --verify` and
`ui/check_ui.mjs` were both passing, and reporting different worlds:

| | `build_ui_data.py --verify` | `check_ui.mjs` |
| --- | --- | --- |
| runs | 77 | 61 |
| spans | 168 | 139 |
| resolved / case_only | 158 / 9 | 132 / 6 |

`ui/data.js` was written at **09:02**. Sixteen archived runs are newer than it —
the whole of the exit-gate session, 13:36 to 13:40. `grep 53afe41c ui/data.js`
returned nothing: **the Adulis answer the persevere verdict rests on was not in
the UI at all**, alongside not being in the gold set. The one artefact you would
show somebody, and the one run the argument depends on, and they had not met.

Every assertion `check_ui.mjs` makes was true of the bundle. None was true of the
project. This is the fifth appearance of *a test that passes for the wrong
reason*, and the second in a single day — the first being `test_embed.py`
truncating itself.

The instruction already existed. `README.md`, Part 9: *"Run the builder after any
corpus edit. That is what would have caught the drift on the day it happened."*
It was not run after the exit gate. **An instruction in a README is not a guard**,
which is the lesson, and it is new.

Fixed by adding a staleness check as **check 0** in `check_ui.mjs`: if any file
under `eval/answer_runs/` or `data/seed_corpus/` is newer than `ui/data.js`, the
run hard-fails and exits before printing a single count, because every count
after it would describe a bundle behind the evidence. Verified against the real
defect rather than a synthetic one — it fired on the actual stale bundle and
named the Adulis run first.

Bundle regenerated: 673 KB → 827 KB, 61 → 77 runs, 139 → 168 spans, and the two
audits now agree at **158 resolved / 9 case_only / 0 moved / 1 absent**.

**This is the argument for tracking `ui/data.js` in git, made on day one.** The
bundle is derived, and it is also evidence; a gate result that cannot be compared
against the artefact that produced it is the Phase 1 defect family again.

## Block 0 addendum — a third state in `reference_translation`

`ingest.verify` reports `parallel pairs: 15` against Part 3's 16, with one loader
warning:

```
! arabia-02-palmyrene-tariff: empty reference_translation, no translation chunk emitted
```

Part 3's design says a record with no translation carries
`reference_translation: null`, and accounted for exactly 8 such records, all
find/coin. The Palmyrene Tariff is a ninth, and its field is **empty rather than
null** — a third state that reads as "a translation exists, and it is nothing."

Benign today: the record is held back as a `pointer` regardless. It matters at
Block F, where the HTR spike targets this very record. When a transcription
lands, the field must become either a real translation or an honest `null`.
Logged rather than fixed, because fixing it now would change a seed record for no
behavioural gain and invalidate spans for nothing.

---

# Phase 2 — Block A1: place-field shape and the gazetteer client (2026-08-12)

Zero API calls, zero corpus records edited. A1 is the session that decides what
24 records will be edited *against*, so the deliverable is a shape, a client and
fourteen mutation-verified guards — not a placement.

## The finding: Pleiades per-id JSON is behind an anti-bot wall

`PHASE2_PLAN.md` A1 specifies fetching `pleiades.stoa.org/places/<id>/json`
once per id and caching it. Checked before writing the client:

| request | result |
| --- | --- |
| `https://pleiades.stoa.org/places/39274195/json` | **empty body** |
| `https://pleiades.stoa.org/places/39274195` | **Anubis** challenge page — "Making sure you're not a bot", JavaScript proof-of-work |

A `urllib` call from the host meets the same wall, and meets it as an *empty
200* — which a naive client reports as "this id did not resolve". That is
**the third appearance of *a check that matches too broadly names the wrong
cause***: after Part 4's Voyage rate limit reported as a dead gateway, and Block
0's suite failure reported as a corrupted working tree. Caught this time before
it was written rather than after it cost an afternoon, which is the only
difference worth noting.

**Route taken (your decision):** the dated bulk dump. Pleiades publishes
complete places tables at `atlantides.org/downloads/pleiades/dumps/`,
regenerated each morning and named by date; `pleiades-places-20260812.csv.gz` is
6.5 MB. One network act, no per-id calls, and — the reason it is *better* than
the plan's design rather than merely a workaround — **every cached entry carries
the dump date it came from**. A coordinate can be told from a coordinate that
was correct under an earlier snapshot, which is the standing lesson this
repository has recorded five times.

The per-id route is not deleted. It is `--probe`, which **reports what it found
and never caches**: it distinguishes an HTTP error, a transport failure, an
empty body and a challenge page, and says so in four different sentences. The
day Anubis is reconfigured, this is one flag away.

## What was decided, and what was deliberately not

Four decisions, taken before any record was edited:

1. **Bulk dump, dated.** Above.
2. **No defaults; conditional requirements.** `ground_citation` is *required*
   when `ground` is `identified`, because that ground **is** the claim that a
   scholar made an identification. Nothing is inherited from a default — the
   `expect_untranslatable` rule, applied to geography.
3. **`regional` may or may not carry a Pleiades id, decided per record.** With
   an id it renders as an extent, never a pin. Without one it renders as
   nothing, and **must carry a note** saying what is known and why no place
   resolved — otherwise "24/24 carry at least `regional`" is satisfied by a
   field asserting nothing.
4. **The licence is recorded verbatim or not at all.** See the open item below.

**Two departures from the plan's draft shape**, both for the same reason:
`"note": ""` and `"contested": false` are now **load-time errors**. An empty
string is a third state reading "a value exists, and it is nothing" — this
repository already carries one, `arabia-02-palmyrene-tariff`'s
`reference_translation`, logged in Block 0 and due to be paid for at Block F.
`contested` may appear only as `true`; absent means not contested. One way to
say each thing.

**Not decided, and named so it is not decided by accident:** `subject_places`
carries no `role` or direction key. A5 renders trade texts as *edges* between
subject places, and an edge needs to know origin from destination. Adding a key
now that A5 might define differently is worse than re-editing the **7 literary
records** that will carry edges. Flagged for A5, not deferred silently.

## What was built

| file | role |
| --- | --- |
| `data/seed_corpus/PLACES.md` | the spec 24 records are edited against, with worked examples |
| `ingest/places.py` | strict loader for `findspot_places` / `subject_places`. Unknown keys, empty strings and empty blocks are load-time errors |
| `ingest/gazetteer.py` | the **only** thing in the repository that turns an id into a point. Offline by default; `--inspect`, `--refresh`, `--check`, `--stats`, `--record-licence`, `--probe` |
| `data/gazetteer.json` | the cache, empty, with an `UNCONFIRMED` licence that fails the check |
| `ingest/test_places.py` | 46 offline assertions, no network, no DB |
| `scripts/mutate_places.py` | **14 mutations, all verified** |
| `ingest/verify.py` | placement audit wired in — malformed is a failure, incomplete coverage is a progress note |

Read `places.py` and `gazetteer.py` together and there is no path from a seed
record to a map pin that does not pass through a cached lookup with a dated
source.

## The column-discovery decision, which is not fussiness

The dumps `README.txt` (last modified **2022-11-07**) documents the places table
as `id, title, description, path, timePeriods, featureTypes` and **mentions no
coordinate columns at all**, while the file itself is regenerated daily. A
parser written from that README is a parser written against documentation
rather than against data — and the dump could not be downloaded into the
development sandbox to check.

So `map_columns()` **discovers** columns from the header row against candidate
lists, and a logical field that matches nothing raises with **the header it
actually observed** printed in the message. `--inspect` prints the header, the
resolved column map and the first row while writing nothing, so the shape can be
confirmed on the host before a single entry is cached. The observed header is
then stored in `data/gazetteer.json` alongside the data it produced.

## Coverage now, against G1

```
documents: 24   chunks: 56   parallel pairs: 15
note: W1 placements: 0/24 records placed, 0/17 with a named place,
      0 distinct Pleiades ids, 0 contested (G1 criteria 1 and 3)
```

Zero is the correct number today. `verify` reports it as a **note**, not a
failure: Block A spends three sessions getting from 0 to 24, and a suite that
fails throughout is a suite that gets ignored throughout. A *malformed*
placement is a failure from the first record edited.

## The fourteen guards, and why each exists

Every one is broken in turn by `scripts/mutate_places.py` and confirmed to make
its own assertion fail — not merely to make something fail. The first four are
Gate G1 criterion 2 in code:

1. a specific place no longer needs a `pleiades_id` — **the authored-coordinate hole**
2. `identified` no longer needs the citation that makes the identification
3. an uncached id resolves to `None` instead of raising
4. a hand-written `lat`/`lon` in a seed record is accepted

…then: unknown keys ignored; empty strings accepted; a `uri` allowed to disagree
with the id beside it; a contested identification with one side; `contested:
false` re-creating the third state; a `regional` placement not having to say why
it is sparse; a dump header with no geometry accepted; an undated `latest` dump
stamped with today; the licence gate removed; a cached entry with neither point
nor extent passing.

**On guard 4 and a rule that nearly matched too broadly.** The forbidden-key
list is *exact key names*, not a substring rule. A substring rule for `lat`
fires on `translation_source`. Written as a substring rule first, caught by
asking what else contains those three letters — and there is an assertion
holding the answer in place, because the next person will reach for the
substring rule too.

**On the test output.** `cmd_check` prints its own `FAILED` block, and three of
the assertions are that it does. Un-suppressed, a *passing* run of
`test_places` scrolled four genuine-looking `FAILED` lines past the reader.
Redirected. A message pointing at something healthy is the defect family this
repository has paid for twice; there was no reason to manufacture a third
instance inside a test suite.

## Also found

- **`ingest/test_embed.py` still has four function-scope imports.** Block 0
  moved *one* to module scope and the file was called fixed. The remaining four
  gate the "SQL and schema agree" section behind `from . import db`, and in an
  environment without `psycopg` the suite still **truncates rather than
  reports** — exactly the two-day defect, one layer down. It passes on the host
  because the host has `psycopg`. **The class is unfixed; W2/Block C owns it.**
- `ingest/gazetteer.py` had one function-scope import (`urllib`) written out of
  habit. Moved to module scope on the same argument, before anyone had to find
  it.

## Open — yours, both small, both blocking

1. **The Pleiades licence text.** It is *not* in the dumps `README.txt` and the
   credits page is behind the same Anubis wall, so it could not be read here.
   `--check` **fails** while the cache holds `UNCONFIRMED` — the same discipline
   as `calibrated: false`, so a guess can never be mistaken for a record. Read
   it in a browser, save it to a file, and run:

   ```powershell
   python -m ingest.gazetteer --record-licence licence.txt `
       --licence-source-url https://pleiades.stoa.org/credits
   ```

2. **Download one dated dump** (not `...-latest...`, which `--refresh` refuses
   for want of a snapshot date), then confirm its shape before caching:

   ```powershell
   python -m ingest.gazetteer --inspect --dump pleiades-places-20260812.csv.gz
   python -m ingest.gazetteer --refresh --dump pleiades-places-20260812.csv.gz
   python -m ingest.gazetteer --check
   ```

   `--refresh` before any record carries an id is a no-op, so the natural order
   is A2's first record, then refresh, then check.

## A1 exit

Field shape approved and written down. `ingest/places.py` and
`ingest/gazetteer.py` built, 46 assertions and **14/14 mutations verified**,
`ingest/verify` wired and passing at 24 documents / 56 chunks. No record edited,
no coordinate anywhere in the corpus, no API call spent. **A2 is clear to begin
placing the 17 findspot records** once the licence is recorded and one dated
dump is on disk.

## Standing lesson added

- **When the plan names an endpoint, check it answers before designing around
  it.** One request would have been the cheapest possible check at any point in
  Phase 1, and the same one-request check is what refuted two confident
  hypotheses at the exit gate. *Prefer a cheap check to a confident hypothesis*
  now has a fourth instance, and it is the first where the hypothesis was in a
  written plan rather than in someone's head.

## A1 addendum — the licence, and an attribution gap it exposed (2026-08-12)

Recording the licence surfaced two things worth keeping.

**1. `--record-licence` raised a traceback on a missing file.** `FileNotFoundError`
pointing at `pathlib`, where what the reader needs is *which path was tried and
what it resolved to* — this command is nearly always run with a relative path
against a file just saved somewhere else. Now a `GazetteerError` naming both.
Reading is also `utf-8-sig` rather than `utf-8`: the text is pasted from a
browser and saved on Windows, where a BOM is the default, and recorded verbatim
a leading U+FEFF would sit invisibly at the front of the licence forever.

**2. The licence text is the Creative Commons deed, not a Pleiades page.**
`source_url` is therefore recorded as
`https://creativecommons.org/licenses/by/3.0/us/`, which is where the text
actually is. Writing `pleiades.stoa.org/credits` would have claimed the text was
read off the Pleiades page; it was not. Same rule as not writing a place id from
memory, applied to the one field whose whole purpose is to say where something
came from.

**Still unrecorded, and named so it is not forgotten:** *that Pleiades declares
this licence* is a separate claim from *what the licence says*, and only the
second is in the cache. The credits page is behind the same Anubis wall.

**The gap that mattered more.** CC BY 3.0 requires "appropriate credit", and
Pleiades credits **the authors and contributors of each place**, not the project
as a whole. The dump carries `authors` and `creators` columns; had `--refresh`
not captured them, attributing a single point later would have meant
re-extracting the entire dump. Added to `COLUMN_CANDIDATES` and stored per
entry, in the same pass as the coordinates, before the pass was ever run.

`cmd_check` reports entries with neither authors nor creators as a **note, not a
failure**. Whether an unattributed entry is a defect in the dump or a genuinely
uncredited place is not something this check can distinguish — and a guard that
cannot tell those apart would name the wrong cause, which is the mistake this
repository has now recorded three times.

`--check` passes at exit 0. 48 assertions, 14/14 mutations still verified.

## A1 addendum 2 — the declaration recorded, and a guard that could not pin itself

The Pleiades statement was read and is now on the record:

> Copyrights on software and content are held by the participating institutions
> and by the individual contributors listed below. Using, sharing, and remixing
> of the content is permitted under terms of the Creative Commons Attribution
> 3.0 License (cc-by).

Stored as `licence.declared_by`, **separately from `licence.text`**, because they
are two different claims:

| field | claim | source |
| --- | --- | --- |
| `licence.text` | what CC BY 3.0 US says | creativecommons.org |
| `licence.declared_by` | that Pleiades says it governs their content | pleiades.stoa.org/credits |

Collapsing them would put the publisher's URL on the licensor's words. Both are
verbatim, both dated, and `--check` now fails on either being absent —
`--record-declaration` is the new command. Verbatim text kept in the repository
at `data/pleiades-licence.txt` and `data/pleiades-licence-declaration.txt`, so
the cache can be rebuilt from tracked sources rather than from a browser tab.

**The statement also settles the attribution question the previous addendum
opened.** Copyright is held "by the participating institutions and by the
individual contributors" — per place, not per project. Capturing `authors` and
`creators` during `--refresh` was the right call, and is now sourced rather
than inferred.

### A guard that could not pin itself, for the third time

Adding the declaration rule as an `elif` beneath the licence rule **broke an
existing mutation**: disabling the first rule let the second fail the run, the
exit code never moved, and the assertion "a resolving placement STILL fails
while the licence is unconfirmed" went on passing. The mutation harness said so
immediately — `expected ... to fail, got no failures` — which is the harness
doing precisely the job it exists for.

This is the **third instance of the same shape** in the repository.
`mutate_part8.py` records the other two, both in Part 8: the Aksum case fails on
five assertions so removing one leaves the verdict unchanged, and the quotation
floor is shadowed by `expect_quoted_docs`. Both times the guard that actually
pinned the defect was **the check on what the failure NAMES**, not on whether
the run failed.

Same answer here: `check_with_output` returns the captured text alongside the
exit code, and the guard is now *"the unconfirmed-licence failure names it as
unconfirmed"*. Verified to fire.

**The generalisation, now that it has happened three times and is worth
stating:** *when two rules can fail the same run, an exit-code assertion pins
neither.* Assert on the message. Defence in depth is good, and it is exactly
what makes a verdict-level assertion worthless as a guard.

State: 50 assertions, **15/15 mutations verified**, `ingest.verify` and
`gazetteer --check` both at exit 0. Licence and declaration recorded. The only
thing standing between here and A2 is one dated dump.

## A1 addendum 3 — fixing the instance instead of the class, within one session

`--record-licence` raised a `FileNotFoundError` traceback on a missing file. It
was fixed. Two commands later, `--inspect` raised the identical traceback from
`_open_dump`, because the fix had been written into one function rather than
applied to the module.

That is **the same mistake in miniature that Part 4 recorded at scale**: a point
fix where a structural one was needed. There, `chunks_embedding_provenance`
cleared one column and left three, and the correction was to move the columns
and the constraint into the `CREATE TABLE` so a fresh database and a migrated
one have the same shape. Here the correction is a single `require_file(path,
what, hint)` used by all four paths the module accepts — dump, licence,
declaration, and the existence check now leading `cmd_refresh`.

Asserted at every call site rather than once, so the next command that takes a
path is caught by a failing test rather than by the user:

```
ok  a missing dump raises with its resolved path, not a traceback
ok  a missing licence file raises with its resolved path, not a traceback
ok  a missing declaration file raises with its resolved path, not a traceback
```

Each message now names the path, what it resolved to, that the path is relative
to the working directory, and — for the dump — where to download one and how
large it is. The traceback named `gzip.py` line 208.

**Standing lesson, restated because it recurred inside a single session:** *fix
the class, not the instance.* Two occurrences an hour apart, and the second was
avoidable by asking, at the moment of the first, which other call sites take a
path. 53 assertions, 15/15 mutations.

## A1 addendum 4 — a filename asserted from the wrong index, and a message that named the wrong cause twice

The `--inspect` step failed again, and both causes were mine.

**1. The dump filename did not exist.** `pleiades-places-20260812.csv.gz` was
put in the instructions and in the module's own hint text. The **places CSV
dumps run only to `20260810`**; `pleiades-places-latest.csv.gz` is dated
2026-08-10. The `20260812` files are in `downloads/pleiades/json/` — the 129 MB
JSON dumps — a **different directory on a different regeneration schedule**. The
date was carried across from the JSON index to the CSV one, and the download
404'd.

This is *a place id written from memory* in its purest form, committed by the
same session that built a module whose founding rule is that no such thing may
happen. The rule was applied to Pleiades ids and not to the filename that
delivers them. The hint text now says: open the index and take a name that is
**actually listed there**, and do not construct one from a date.

**2. The error message asserted something false.** It ended, unconditionally,
*"The path is relative to the directory you ran this from"* — printed against
`C:\Users\chemi\Downloads\pleiades-places-20260812.csv.gz`, a fully qualified
path to which that sentence cannot apply, alongside a redundant "resolved to"
repeating the same string back.

So the helper written **specifically to stop messages naming the wrong cause**
named the wrong cause on its second outing. Fourth occurrence of that family in
this repository, and the first inside the fix for the third.

Corrected to branch on the path:

| path | message |
| --- | --- |
| relative | where it resolved to, and that it is relative to the working directory |
| absolute, parent exists | **what that directory does contain** — because then the likeliest cause is the filename, not the location |
| absolute, parent missing | that the directory does not exist either |

Had the second branch existed an hour ago, the listing of `Downloads` would have
shown at a glance that nothing matching had ever arrived.

Three assertions added, including one that the string "relative to" **cannot**
appear in an absolute-path message.

**The lesson, and it is a new one:** *an error message is an assertion, and it
is subject to the same standard as any other.* This project asserts nothing
about a translation, a coordinate or a citation without a source, and then
prints diagnostic sentences that were never checked against the case they
appear in. Three of the roughly thirty-five Phase 1 defects were messages
pointing at healthy things; none of them had a test.

56 assertions, 15/15 mutations, `verify` and `--check` at exit 0.

## A1 addendum 5 — the dump inspected, and what the first row changed (2026-08-12)

`--inspect` ran against `pleiades-places-20260810.csv.gz`. This is the step the
command was built for: the parser was written blind, against a README dated
**2022-11-07** that documents six of the twenty-six columns actually present and
**names no coordinate column at all**. Four things the first row settled.

**Confirmed, unchanged:** `reprLat` / `reprLong` resolve, and `bbox` is
comma-separated `lon, lat, lon, lat` — the `[min_lon, min_lat, max_lon, max_lat]`
order already assumed. Both now asserted against a fixture shaped on the real
row rather than on the guess.

**1. `extent` is not a bbox.** It was second in the bbox candidate list. It holds
GeoJSON — `{"type": "Point", "coordinates": [13.41, 42.08]}` — which parsed as
four numbers yields nothing, silently, and would have done so on any place whose
`bbox` column was empty. Removed rather than taught to read GeoJSON: `bbox` is
present and direct, and a second geometry parser is a second thing to keep
right. Asserted that `extent` is never mapped.

**2. Pleiades is not confined to antiquity, and this matters.** The dump's first
row is **"Borgo Medievale", minDate 640, maxDate 1453, timePeriods "M"** — a
period code absent from the README's documented vocabulary
(`A`/`C`/`H`/`R`/`L`). Mundus Ulterior covers 27 BC to AD 1204. **An id can
resolve perfectly and still denote a place attested only centuries after the
record citing it** — a misidentification that passes every check now in
existence, because nothing compares the record's date to the gazetteer entry's.

`minDate`, `maxDate` and `timePeriodsKeys` are therefore captured, and
`locationPrecision` with them. The last is a **different axis from `ground`**:
ours records how *we* arrived at the placement, Pleiades' records how well *they*
know the point. A5 needs both to render honestly.

Captured now rather than checked now, deliberately. Seed-record dates are free
text — "c. 40-70 CE", "grave: 1st century CE" — and a date-overlap check built
on parsing them would be a guess wearing an assertion. **The data is on disk
from the first refresh; the check belongs at A6.** Logged as W1 debt.

**3. The test fixture was built with a hand-rolled CSV writer, and it was
wrong.** It quoted any field containing a comma or a space. The real `extent`
value contains double quotes, which need doubling rather than wrapping — so the
fixture was unparseable and the failure surfaced as `KeyError: '39274195'`, *a
missing id*. **A fault in the test harness reported as a fault in the code under
test**, which is the fifth appearance of a check naming the wrong cause and the
first one this session that wasted a run rather than a message. Replaced with
`csv.writer`.

**4. The guessed header was wrong in one column** — `geometry` where the file has
`geoContext`. Harmless, since neither is read, and it is the point: a header
written from documentation is a header that can differ from the file in ways
nothing notices.

**What this vindicates.** The single most useful decision in A1 was refusing to
write the parser from the README and building `--inspect` instead. Three of the
four findings above would have become silent wrong data in `data/gazetteer.json`
— the kind that is discovered when a map pin looks odd, six weeks later.

59 assertions, 15/15 mutations, `verify` and `--check` at exit 0. **Nothing has
been cached yet — `--refresh` is still a no-op until a record carries an id.**

## A1 addendum 6 — the coverage survey, and the plan's own id was wrong

Before editing any record, four searches against the 2026-08-10 snapshot —
using `--find`, which was built for this and searches **the artefact the cache
will be built from** rather than the live site.

| searched | result |
| --- | --- |
| `Lolland` | nothing |
| `Hoby` | **98983**, 54.741/11.231, precise, roman, BAtlas 10 H2 |
| `Adulis` | nothing by title; one description mention (Matara) |
| `Adule` | nothing — the only hit was "Padule di Raspollino" in a description |
| `39271` (by id) | **Adouli**, 15.262/39.659, "port on the west coast of the Red Sea near modern Zula in Eritrea" |

**1. `PHASE2_PLAN.md`'s worked example carries the wrong id.** It illustrates
the field shape with `"name": "Adulis", "pleiades_id": "39274195"`. Adulis is
**39271**. The wrong id sits in the section whose stated rule is that *no id,
from me or any model, is written from memory* — and it was written from memory,
in the document that forbids it, and then copied into this repository's test
fixture, where it survived until the snapshot was searched. Fixture corrected to
39271 with the real coordinates.

Nothing downstream was affected, because no record had been edited. That is
entirely down to sequencing: A1 built the machinery and placed nothing, so the
wrong id had no path into the corpus. Had A1 and A2 been one session it would be
in a seed record now.

**2. Title search is unreliable, and would have failed on the most important
record in the corpus.** Pleiades titles Adulis **"Adouli"** — a transliteration
of Ἀδουλί containing neither "Adulis" nor "Adule". Three separate title searches
missed it. The **names** dump found it immediately, holding both "Adouli" and
"Adule" against place 39271.

So the A2 method is: search the names dump, not just titles, and treat an empty
title search as *no information* rather than as absence. `--find` now also
matches a **bare numeric id**, which is what resolved this.

**3. My hypothesis about coverage was wrong, usefully.** I predicted a
Greco-Roman gazetteer would not cover Scandinavia, and that A2–A4 would need
reordering. Wrong: Pleiades has **the site and not the modern region**. "Lolland"
is a Danish administrative area and is absent; "Hoby" is an archaeological site
in Barrington Atlas 10 H2 and is present with a precise coordinate. The plan's
findspots-first ordering stands. Refuted by four searches costing about a
minute — *prefer a cheap check to a confident hypothesis*, and this time the
confident hypothesis was mine.

**4. A name match is not an identification.** Both ids were accepted only after
the **coordinate** was read: 54.741/11.231 is on Lolland, 15.262/39.659 is the
Eritrean Red Sea coast. Matching on the name alone is the Part 4 defect exactly —
a probe that passed on `doc_id` while pointing at the wrong passage. `--find`
now prints the coordinate and description on every hit and says so in as many
words.

**5. The dumps README is wrong on three counts**, all found by reading the file:
it documents six of twenty-six columns, names no coordinate column, and claims
the names table's `pid` joins to the places table's `id` when it actually holds
a path, `/places/39271`. Normalised in `--find`.

**The unlocated case is real, not theoretical.** "Adulas M." (194037) is in the
dump with no coordinate at all — precisely what `cmd_check` refuses.

63 assertions, 15/15 mutations. Still nothing cached: `--refresh` remains a
no-op until a record carries an id.

## A2 begins — first record placed, chain confirmed end to end (2026-08-12)

`scandinavia-01-hoby-treasure` carries a `findspot_places` block. Pleiades
**98983**, `stated`, confirmed by coordinate (54.741/11.231, Lolland) and
attested period (Roman, −30..300) rather than by title.

```
W1 placements: 1/24 records placed, 1/17 with a named place, 1 Pleiades id
looked up 1 of 1 ids from pleiades-places-20260810.csv.gz (2026-08-10)
Every placement resolves to a cached, dated gazetteer entry.
```

`verify` 0, `--check` 0. The cached entry carries the point, the attested date
range, `locationPrecision: precise`, `featureTypes: cemetery` — which
independently corroborates a chieftain's grave — and the attribution the CC BY
licence requires: *"Bloemers, J., DARMC, S. Gillies, R. Talbert, T. Elliott"*.
Capturing authors during `--refresh` has paid off on the first entry rather than
at A5.

### The first entry immediately showed a defect A5 would have inherited

Pleiades writes a **degenerate bbox** for a point place:
`[11.230919, 54.740603, 11.230919, 54.740603]` — min equal to max, the
representative point wearing a rectangle. `--stats` duly reported
`with extent: 1`, which is true and misleading.

It matters because `PHASE2_PLAN.md` A5 says a `regional` placement renders as an
extent and never as a pin. Had `has_extent` been the test, a point place would
have drawn a zero-size box and a regional place holding only a degenerate bbox
would have drawn nothing while claiming an extent. **Two different questions
under one name** — the same trap as `translation_chunk` vs
`translation_chunk_id`, which W2 is already scheduled to pay off.

Split into `has_extent` (any bbox) and `has_area` (a bbox with area), both
asserted. `--stats` now reads:

```
entries: 1  (with point: 1, with a bbox: 1, of which non-degenerate: 0)
```

Found by looking at the one real row cached, not by reasoning about the format.
That is the fourth thing this snapshot has corrected about a parser written
against documentation.

65 assertions, 15/15 mutations.

## A2 — a second gazetteer, and a field renamed while it cost one record

The survey forced two decisions, both taken 2026-08-12 with one placement on
disk.

### The G1 shortfall is the project's premise appearing in its own gate

Roughly **9 of 17** findspot records can carry a named Pleiades place. Seven have
no entry at all — Jabal Ḏabūb, Gyeongju, Khao Sam Kaeo, Óc Eo ×2, and two coin
records whose findspot is unrecorded or hearsay. With the 7 literary records that
is **16 records with a resolving id, against G1's ≥17**.

Pleiades is a Greco-Roman gazetteer; this corpus was deliberately built outside
the Roman world. The gate assumed 17 findspots would yield 17 named places, and
the assumption is exactly the thing Mundus Ulterior exists to test.

**Decision: add GeoNames** for the extra-Roman sites, rather than lower the
number or count region boxes toward it. GeoNames is CC BY 4.0, so the licence and
declaration machinery already built applies unchanged, and its per-country dumps
are small and dated — the same shape as the Pleiades path.

A GeoNames placement is a **modern administrative place**, so it will usually be
`identified` rather than `stated`, and its note must say what the coordinate
denotes. A district centroid is not an excavation trench, and the schema should
not let those read alike.

### `pleiades_id` → `gazetteer` + `gazetteer_id`

A field name that hard-codes one source is the `translation_chunk_id` trap: a
name that is wrong for half its values. **Seen coming this time**, and renamed
while exactly one record carried a placement — one record edit, a spec revision
and a test pass, against seventeen record edits had it waited until A4.

- `gazetteer` comes from a **closed vocabulary** (`pleiades`, `geonames`).
  Adding one is a decision about sourcing and licensing, not a spelling.
- `gazetteer` and `gazetteer_id` are written together or not at all. An id with
  no source names nothing; a source with no id identifies nothing.
- `uri` is checked against **that gazetteer's** canonical form.
- **Cache keys are namespaced `<gazetteer>:<id>`.** Ids collide: Pleiades 98983
  is Hoby on Lolland, GeoNames 98983 is something else. A cache keyed on the bare
  number would serve one for the other and nothing would raise.
- `sources` is a block **per gazetteer**. A single `source` was correct with one
  gazetteer and would have become a lie with two — the same defect as the field
  name it accompanied, one level up.

Three new mutation-verified guards: an unlisted gazetteer, a gazetteer with no
id, an id with no gazetteer. **71 assertions, 17/17 mutations.**

The cache was reset to the namespaced shape; the licence and declaration blocks
were preserved, so one `--refresh` restores it.

### GeoNames is declared but has no reader, deliberately

Its country files are **tab-separated with no header row**, so the
header-discovery design cannot apply and writing the parser now would mean
writing it from documentation — the mistake that has cost four corrections in
this session alone (a filename from the wrong index, `extent` as a bbox, a
guessed header column, and a hand-rolled CSV writer). The next step there is to
download one country file and look at it first.

## A2 — two searches that answered different questions (2026-08-13)

The id-confirmation survey came back reporting `nothing` for **ten ids that
plainly exist**, including 922685, 50146, 39303 and 98970 — all four already
confirmed by `--find` the day before. Two hits it did report were false.

**Cause: `--find` and `--survey` did not implement the same search.** `--find`
matches a bare numeric term against the `id` column; `--survey` was written
first and only ever matched title and description. So a survey of ids searched
for those digits *as text*, and:

- `'814675'` "found" place **427224440**, because the string 814675 appears in
  that record's **description**;
- `'427224440'` found nothing, because no description contains it;
- every id whose digits appear nowhere in prose reported `nothing`.

The output was **plausible** rather than empty or erroring, and it was produced
by the command recommended for exactly this job.

This is the same defect family as `check_ui.mjs` and `build_ui_data.py`
reporting different worlds while both passed, and as `translation_chunk` vs
`translation_chunk_id`: **two implementations of one question, which will
diverge, and whose divergence nothing checks.** Fixed by deleting one — `--find`
and `--survey` now share a single `match_row()`, and a guard asserts `--survey`
resolves a bare id. Mutation-verified.

### What the broken run found anyway

`427224440` is titled **"Erroneous Duplicate: Al-Hijr (Madâ'in Sâlih)"** and sits
at **26.792, 37.961** — Hegra's own coordinate, `precise`, −330..2100.

**Pleiades retains deprecated records in the dump.** Such an id resolves, carries
a plausible point, and is the publisher explicitly saying *do not cite this*.
Nothing in the pipeline would have noticed: it has a coordinate, a date range and
a feature type, and the only thing marking it is prose in the title.

`cmd_check` now **fails** on a cached entry whose title carries a deprecation
marker, naming it and saying to find the record it duplicates. Mutation-verified.
Found only because the title was read — the same reason the Muziris and Hoby
placements were accepted by coordinate rather than by name.

**19 mutations, 76 assertions.** The survey must be re-run; every id result from
the 2026-08-13 run before this fix is void.

### Standing lesson, sharpened

*A test that passes for the wrong reason is worse than one that fails* — and its
sibling, now seen three times: **two code paths answering one question will
diverge, and the divergence will look like data rather than a bug.** The fix is
never to correct the second copy. It is to stop having two.

## A2 — seven records placed, nine ids resolved (2026-08-13)

```
W1 placements: 8/24 records placed, 8/17 with a named place, 9 gazetteer ids
looked up 9 of 9 ids from pleiades-places-20260810.csv.gz (2026-08-10)
entries: 9  (with point: 9, with a bbox: 9, of which non-degenerate: 6)
Every placement resolves to a cached, dated gazetteer entry.
```

| record | id | title | ground |
| --- | --- | --- | --- |
| scandinavia-01-hoby | 98983 | Hoby | stated |
| arabia-02-palmyrene-tariff | 668331 | Palmyra | stated |
| arabia-03-jsnab17 | 814675 | Egra/Meda'in Salih | stated |
| scandinavia-02-gudme | 98970 | Gudme | stated |
| scandinavia-04-illerup | 20492 | Illerup Ådal | stated |
| scandinavia-03-vimose | 99059 | Vimose | stated |
| africa-01-ezana-stone | 39303 | A(u)xoume | stated |
| persia-01-skz | 922685 | Naqsh-i Rustam | stated |
| persia-01-skz | 616346030 | Ka'ba-ye Zartosht | **identified** |

Every id was accepted on its **coordinate and feature types**, never its name,
and each placement's note records what it was checked against.

### The ŠKZ carries two placements, and the pair is the point

Pleiades holds the **Ka'ba-ye Zartosht** (616346030, "A stone monument located in
the Naqsh-e Rustam compound") separately from the **necropolis** (922685) — about
100 m apart. The inscription is carved on the tower; the record's `findspot`
field says "Naqsh-e Rostam".

So both are placed, and the *difference in ground is the information*: `stated`
for what the record says, `identified` for the more precise truth, with the
citation that supports it. A single placement would have had to either lose the
precision or misreport where the claim came from.

### Three deliberate absences, each recorded in a note

- **Lundeborg** (99004) — Gudme's findspot field calls it an associated trading
  site *nearby*, not where the hoard was found.
- **The Hermitage Museum** — the Palmyrene Tariff's current location. A findspot
  is where it was found.
- **Skanderborg** — no separate Pleiades entry; the deposit site carries it.

Each is in the record rather than in anyone's memory, because "we considered this
and decided against it" is invisible otherwise, and the next curator would
otherwise re-open all three.

### The deprecation guard earned itself immediately

Hegra resolves to **814675 Egra/Meda'in Salih** (26.798/37.952). Pleiades also
holds **427224440**, "Erroneous Duplicate: Al-Hijr (Madâ'in Sâlih)", 700 m away,
`precise`, with the same feature types and date range. Both would have cached and
drawn identically. The note on the Hegra placement names the duplicate so the
question is not re-opened by someone reading a search result.

### Watch item for A6

The Ka'ba-ye Zartosht's `timePeriodsKeys` are `achaemenid-central-asia,modern` —
no Roman or late-antique key — while the ŠKZ is a **3rd-century** inscription.
The attested range (−540..2100) does cover it, so there is no contradiction, but
this is precisely the shape the deferred date-overlap check exists to catch, and
it appeared on the ninth entry cached. **A6 should build that check.**

### Left for judgement, not placed

`southasia-04-pattanam` (contested, needs two citations), `africa-02-aksumite-coin`
(found ~300 km north of Aden — Aden is not the findspot), `persia-02-silver-plate`
(hearsay, and Pleiades 837 "Asia Minor" is `related` precision, dated 1700..1799,
with a representative point near Ephesus — a poor record for a peninsula), and
`persia-03-coin` (no findspot recorded at all).

## A2 — the three judgement records, and two schema gaps they exposed (2026-08-13)

```
W1 placements: 11 placed + 1 declared unplaceable = 12/24 considered,
               10/17 with a named place, 10 gazetteer ids, 1 contested
Grounds: {identified: 2, regional: 2, stated: 9}
```

### `no_places_reason` — because "unplaced" and "unplaceable" were the same thing

`persia-03-coin`'s findspot is *"Not recorded (acquired via Robertson sale,
1843)"*. Not vague — **absent**. No honest `regional` placement exists, and the
record carries no mint either.

An omitted block therefore meant both *not curated yet* and *curated, nothing to
place*, which at A6 are indistinguishable. **The third state this schema refuses
at every other level, appearing one level up.** A record now carries place blocks
OR a record-level `no_places_reason`, never both, and `verify` reports
`placed + declared unplaceable = considered`.

This also makes **G1 criterion 1 achievable and honest at the same time.** "24/24
records carry at least `regional`" is unreachable when a findspot is genuinely
unrecorded; "24/24 have been considered" is reachable and is the claim actually
worth making.

### `origin_places` — a mint is not a findspot

The Aksumite coin was minted at Aksum and found in Yemen. `subject_places` means
"where the text is about" and a coin has no text; stretching it would have
damaged the definition A4 depends on. So a third block, named for the general
case — **manufacture** — rather than the instance that prompted it, because the
general case is everywhere here: Hoby's cups made in Italy, Roman glass at
Hwangnam-daechong, an Antoninus medallion at Óc Eo.

**Origin to findspot is an object moving**, which is the connection this project
exists to document and the edge A5 should draw. Added while 8 records were
placed; only the coin uses it so far, and the other records will not be
retro-fitted without a decision.

### The three judgements

**Pattanam** — `identified` + `contested`, on Pleiades **50146 Muziris**, whose
point (10.154/76.213) *is Pattanam* and which Pleiades marks `precise`. **The
gazetteer has already adopted the identification this record treats as open.**
Our entry now says something Pleiades does not, which is exactly what the
contested flag is for.

The second citation is **explicitly provisional and says so in its own text**:
the sceptical side currently rests on this record's `notes` summarising an ASI
caution, which is our own prose, not published scholarship. Recorded that way
rather than quietly satisfying the two-citation rule — a rule met by a citation
that is not really a citation is worse than a rule seen to be pending.

**Aksumite coin** — findspot `regional` with **no id**. Pleiades 39269 is Aden,
about 300 km from where the coin was found, and is deliberately unused: *a
resolving id at the wrong place is worse than no id*. Origin placed at Aksum
(39303) — the same id that is africa-01's **findspot**, which is precisely why
the two are separate blocks.

**Silver plate** — `regional`, no id. "Said to have been found in Anatolia" is a
reported attribution, not a findspot. **Pleiades 837 was examined and rejected**:
`related` precision, attested 1700..1799, representative point near Ephesus
rather than any centroid. The rejection is written into the note so the next
curator does not re-find 837 and silently reach the opposite conclusion.

**Recording the rejections is the point.** "We looked at this and decided against
it" is invisible otherwise, and three separate questions would have been
reopened from scratch.

**81 assertions, 21/21 mutations.**

---

# A4 — starting point (for the next thread)

**State at commit `013ae4a`, 2026-08-13.** Block A is roughly half done.

```
W1 placements: 11 placed + 1 declared unplaceable = 12/24 considered
               10/17 with a named place, 1 contested
placements: 13   locatable: 11   cached ids: 10
entries: 10  (with point: 10, with a bbox: 10, of which non-degenerate: 6)
Every placement resolves to a cached, dated gazetteer entry.
81 assertions, 21/21 mutations, ingest.verify and gazetteer --check both at 0.
```

13 placements across 11 documents; 11 are locatable and they resolve to **10**
distinct ids, because **Aksum (39303) is used twice** — as `africa-01`'s findspot
and as the Aksumite coin's `origin`. That is the two-block design working, and it
is the first edge on the map.

## What A4 is

`subject_places` for the **7 literary records**: Periplus ×3
(`arabia-01`, `southasia-02`, `africa-03`), `eastasia-01-weilue`,
`eastasia-02-hou-hanshu`, `southasia-01-akananuru-149`,
`southasia-03-muziris-papyrus`.

This is where the dot map becomes the network. The Periplus records will each
carry **many** places; that is the point, and it is why `subject_places` exists.

## The one design question A1 deliberately left open

**`subject_places` has no `role` or direction key.** A5 renders trade texts as
*edges between subject places*, and an edge needs to know origin from
destination. Adding a vocabulary at A1 would have been guessing; adding one at
A4, with the seven records in front of you, is a decision with evidence.

Decide it **before** editing the seven, not after. Candidate axis: whether the
text describes a place as a source of goods, a destination, a waypoint, or
merely mentions it. `origin_places` already establishes the precedent that a
distinct relation earns a distinct block rather than a free-text note.

## The method, which is now proven and should not be re-derived

1. **Search the snapshot, never the website.** `--find` and `--survey` read the
   dated dump the cache is built from.
2. **A name match is not an identification. The coordinate decides.** Every id
   so far was accepted on its coordinate and feature types.
3. **Title search alone is unreliable.** Pleiades titles Adulis **"Adouli"** and
   Aksum **"A(u)xoume"**; three searches on the corpus's own vocabulary missed
   both. Pass `--names-dump` and search ancient forms.
4. **A bare number searches the id column** in both commands.
5. **Deprecated records resolve.** `--check` fails on them and `--survey` prefixes
   them `!DEPRECATED!`.
6. **Every placement carries a note** recording what it was confirmed against —
   standing decision of 2026-08-12.
7. **Record the rejections too.** Three ids were examined and refused (Aden for
   the coin, 837 for the plate, 427224440 for Hegra); each refusal is written
   into a note so the question is not reopened from scratch.

## The trap A4 will meet immediately

**Pleiades has already adopted contested identifications.** `50146 Muziris` sits
at 10.154/76.213 — Pattanam — and is marked `precise`, with a *degenerate* bbox.
Its `subject_places` entry in `southasia-02-periplus-muziris` will therefore
assert a place whose location the corpus itself treats as open. Read
`southasia-04-pattanam`'s `findspot_places` note before writing it; the two must
not contradict each other.

## Commands

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
$d = "$env:USERPROFILE\Downloads\pleiades-places-20260810.csv.gz"
$n = "$env:USERPROFILE\Downloads\pleiades-names-20260810.csv.gz"

python -m ingest.gazetteer --survey data\place_survey_a4.txt --dump $d --names-dump $n
python -m ingest.verify
python -m ingest.gazetteer --refresh --dump $d
python -m ingest.gazetteer --check
```

No venv, no `.env`, no Docker, no gateway. Block A spends nothing.

## Still outstanding elsewhere in Block A

| item | note |
| --- | --- |
| GeoNames reader | blocks Gyeongju, Óc Eo ×2, Khao Sam Kaeo. **Start with `--inspect` on one country file** — they are tab-separated with no header row, so header discovery does not transfer |
| Pattanam's sceptical citation | currently provisional and says so in its own text; needs a published source |
| ŠKZ ground_citation | expand with the full title of Huyse 1999, which names the Ka'ba-ye Zartosht |
| A5 | region view becomes place view; `has_area` vs `has_extent` already distinguishes a point place from a real extent |
| A6 | date-overlap check. Motivating case on disk: the Ka'ba's `timePeriodsKeys` skip the Roman era while the ŠKZ is 3rd-century |
| `PHASE2_PLAN.md` | its worked example still carries the wrong Adulis id (`39274195`); worth correcting at source |

---

# A4 — the role vocabulary, and two findings from reading the sources (2026-08-13)

The open design question is closed and the survey is built. **No record is
edited yet**, because no id has been resolved yet and none may be written from
memory. The survey run is the next thing, and it is yours.

```
95 assertions (was 81), 26/26 mutations (was 21), ingest.verify clean.
Corpus unchanged: 24 documents, 56 chunks, 13 placements across 11 documents.
```

## The decision: `role`, a closed vocabulary on `subject_places`

`source → focus → destination`, from which A5 derives every edge. Five values:
`focus`, `source`, `destination`, `waypoint`, `mentioned`. Full reasoning in
`data/seed_corpus/PLACES.md`; the three rules worth repeating here:

- **Required on `subject_places`, forbidden on the other two blocks.** Forbidden
  because `findspot_places` and `origin_places` already name their relation, and
  a role beside them is a second name for one fact — free to disagree with the
  first. Required with **no default**, for the reason `expect_untranslatable`
  has none: `mentioned` is the positive claim that the text names a place and
  describes nothing moving through it, and a claim may not arrive by omission.
  A default of `mentioned` is precisely how a half-edited record would silently
  lose its edges, so that is the mutation that verifies the guard.
- **At most one `focus` per block**, or `source → focus` does not say which focus.
- **A directional role requires a `focus`**, or it names one end of an edge and
  no other. A block of nothing but `mentioned` needs none and must not be made
  to invent one.

Named `focus` and not `anchor`: this corpus is largely sailing manuals and
Periplus §4 discusses where ships anchor. That is the *two questions under one
name* defect, which this repository has now paid for four times, seen coming a
fifth.

**Known limit, accepted deliberately:** roles carry no ordering, so a multi-leg
route flattens. The alternative considered was a separate `subject_routes` block
of explicit `{from, to, what_moved}` relations — more expressive, and the right
answer if ordering ever has to be drawn. Recorded in `PLACES.md` rather than
left to be rediscovered.

**Inclusion rule: every named place is placed, each carrying its role**, not the
trade-bearing ones only. `mentioned` is what makes that affordable, and it keeps
the weak entries visible instead of turning them into invisible omissions —
the same argument as `no_places_reason` and the three recorded id rejections.

## Two findings, both from reading the sources rather than the titles

### 1. Schoff's English and the Greek name different places

§54 Greek reads `τοῖς ἀπὸ τῆς Ἀριακῆς … πλοίοις` — ships coming from **Ariake**,
the northern Konkan coast. Schoff 1912 prints "cargoes from **Arabia**". Two
more in the same sections: Greek `Λιμυρική` against Schoff's "Damirica", and
`Τοπαρόν / Τυραννοσβόας` against "Togarum / Aurannohoas".

Ariake and Arabia are a thousand miles apart and draw a different trade network.
**The placement follows the original, not the reference translation**, and the
divergence goes in the entry's note so the next reader does not correct it back.

This is a Part 6 lesson arriving in W1. `chrf_ref` treats a published
translation as ground truth; a published translation is itself an edition with
readings in it. Worth carrying to W2.

### 2. The Muziris papyrus does not name Muziris

The excerpted text (recto col. ii 2-8, verso col. ii) names **Koptos** twice,
**Alexandria** once, and the Ganges adjectivally. Muziris appears in our title,
our `notes`, and the papyrus's conventional name — that is, in editorial prose.

Placing Muziris as this record's focus would be the **Vimose defect exactly**: a
claim carried by our own scaffolding rather than by the text, arriving
downstream attached to a citation. Two honest options, and the choice is
curatorial:

- **(a)** focus `Koptos`, destination `Alexandria`, source `Ganges`. Correct
  today; the record contributes the Egyptian leg and no Indian endpoint.
- **(b)** extend the excerpt to a passage of SB 18 13167 that does name the
  Indian port, then place it. Better record; costs a source-recovery pass
  against papyri.info, the same shape as the Part 3b recoveries.

Written for (a) in the survey file, so nothing blocks. (b) supersedes it cleanly.

## What is on disk

| file | change |
| --- | --- |
| `ingest/places.py` | `ROLES`, `DIRECTIONAL_ROLES`, `Place.role`, `Place.draws_edge`, `_parse_role`, `_check_block_roles` |
| `ingest/test_places.py` | `test_roles` — 15 assertions; the shared fixture now defaults to a block that takes no role |
| `scripts/mutate_places.py` | 5 new mutations, each verified to fail the guard it targets |
| `data/seed_corpus/PLACES.md` | the `role` section, the naming argument, the ordering limit, the inclusion rule |
| `data/place_survey_a4.txt` | 238 terms in 7 groups, ancient and Greek forms first, each with its proposed role and both findings at the foot |

## Next, in order

1. Run the survey (below). It is 238 terms in one pass over the dump — slower
   than A2's 16, so expect a minute or two rather than seconds.
2. Settle Finding 2 — option (a) or (b) — before `southasia-03` is written.
3. Write the seven records from the survey output. Accept every id on its
   **coordinate and feature types**, never its name; record in each note what it
   was confirmed against, and record the rejections too.
4. `--refresh`, then `--check`, then `verify`.

Expect a large `regional` share among the results. `Da Qin`, the Chera and
Pandya kingdoms, Limyrike, Barbaria and the Yavanas are polities and peoples
rather than settlements, and several of the §53 market-towns have never been
located. A sparser map is the correct answer, and G1 criterion 1 counts records
considered, not pins drawn.

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
$d = "$env:USERPROFILE\Downloads\pleiades-places-20260810.csv.gz"
$n = "$env:USERPROFILE\Downloads\pleiades-names-20260810.csv.gz"

python -m ingest.test_places            # 95 assertions
python scripts\mutate_places.py         # 26 mutations
python -m ingest.gazetteer --survey data\place_survey_a4.txt --dump $d --names-dump $n
```

## A4 — the survey ran, and the corpus was the thing that was wrong (2026-08-13)

238 terms, 7,300 place hits, **no id written**. The survey did its job, but what
it mostly established is that three of the seven records did not contain the
text they claimed to.

### FINDING 3 — 20% of the Periplus Greek was missing, silently

Four places named in Schoff's English had no counterpart in the Greek. That was
not an edition difference. Measured against the same Greek Wikisource text of
Müller, *GGM* I (1855) that all three records name in `citation_original`:

| | §4 | §5 | §6 | §27 | §28 | §29 | §53 | §54 | §55 | §56 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| present | **58.9%** | 100% | **70.5%** | **84.5%** | **86.0%** | **75.1%** | 100% | 100% | **59.1%** | 100%* |

**1,479 characters of Koine Greek absent from the corpus**, in six sections,
four of them truncated at the end and two with internal sentences dropped.
(\*§56 is complete but had two characters altered — `πολύς` for Müller's
`πολὺς` — so "verbatim" was not quite true there either.)

Recovered by `scripts/recover_periplus_a4.py`, which rebuilds each excerpt from
the cited source and is idempotent. Greek retrieval-eligible chunks **11 → 14**.

**Why it stayed invisible for four days of work on these very records.** Three
things at once, and no one of them is the culprit:

1. `original_text_note` said "wording is otherwise unaltered" — true of every
   word present, and silent about the ones that were not. A note about
   *fidelity* was read as a note about *completeness*.
2. Part 6 replaced the reference translations with **complete** Schoff, so the
   two sides of each record drifted further apart at the exact moment they were
   being reconciled.
3. **Nothing in the pipeline compares an excerpt against its own cited source.**
   `ingest/verify` checks internal consistency, and internal consistency is
   precisely what a uniformly short excerpt has. This is the standing lesson
   about proxies, one level up: every check was on the record, none on the
   record's relationship to the thing it cites.

The rules that would have caught it were all there and all pointed inward. The
normalisation used to rebuild was validated by reproducing §5, §53 and §54 —
which survived intact — character for character; a rule set that cannot
reproduce the text already on disk is not safe to rebuild the rest with.

**Three consequences beyond A4**, worst first:

- **`align.py` reported `ground="section"` on these pairs.** A §4 Greek chunk
  58.9% the length of its §4 English is the *strong* pairing claim, made over
  materially different text. The ground was honest about its evidence; the
  evidence was wrong.
- **`chrf_ref` is confounded for exactly these records** — a machine translation
  of a short Greek chunk scored against a full published English section — and
  PROGRESS.md calls `chrf_ref` the only accuracy signal the project has. It does
  **not** explain the Part 6 numbers on its own (§28 was 86% present and scored
  0.275; §4 was 58.9% present and scored 0.427), but it is an uncontrolled
  variable that nobody knew was in the measurement. **Re-run Part 6 on the three
  Periplus records after re-ingest and compare.**
- A Part 7 citation of Schoff's Alalaei or Diodorus sentence had **no Greek to
  resolve to**. The two `pointer` records are unreachable by construction; this
  was reachable and wrong.

### FINDING 2, resolved — the Muziris papyrus now names Muziris

The excerpt ran to recto col. ii line 8. **Μουζεῖριν** is at line 12 — *"the
loan contracts made at Muziris"*. Extended to line 14 from the DDbDP
transcription already cited. Two lacunae of unstated length at line 12 are
marked `...` rather than closed up silently, and the note says so.

Until today this record named its port in its title, its `notes` and the
papyrus's conventional name, and **nowhere in its own text** — the Vimose defect
exactly, and it would have arrived attached to a citation.

Outstanding: `reference_translation` still covers the old excerpt only.

### FINDING 1, confirmed against the source

§54's Greek reads `ἀπὸ τῆς Ἀριακῆς` where Schoff prints "from Arabia". Also
`Λιμυρική` for "Damirica" and `Τοπαρόν / Τυραννοσβόας` for "Togarum /
Aurannohoas". Placements follow the original; Ariake has two candidate ids and
the choice is in the second survey.

### What the survey did settle

Confident, coordinate-checked, not yet written: Adulis 39271, Ptolemais Theron
39409, Oreine 39404, Koloe 39363, Aksum 39303 · Kane 39355, Eudaimon Arabia
39269, Orneon 39405, Mouza 39390, Sachalites 39419 · Muziris 50146, Kalliena
50023, Semylla 50261, Palaipatmai 50196, Byzantion 49929, Toparon 50308,
Tyrannosboas 50315, Sesekreienai 50264, Aigidion 49842, Kaineiton 50015, Naoura
50160, Tyndis 50312, Nelkynda 50165, Bakare 49890, Limyrike 50092, Cottonara
49953, Barygaza 59737 · Periyar 50234 (as `Pseudostomos`) · Coptos 786010.

**Five decoys a name match would have taken**, each to be recorded as a
rejection in the note that displaces it:

| decoy | what it actually is |
| --- | --- |
| 746710 "Arabia Eudaemon" | a peninsula label at 28.96/35.35 — north-west Arabia, not Aden |
| 471890 "Barbaria" | Barbagia, in **Sardinia** |
| 39295 "Arsinoe" | a Red Sea station at 12.71/43.25 — right region, wrong Arsinoe |
| 785982 "Bakare" | an Egyptian **mine** at 25.21/34.27 |
| 246333 "Chera" | a settlement in **Spain** |

And `49929 Byzantion` at 16.503/73.340 is a Konkan market-town, not
Constantinople — the case where the coordinate rule pays for itself outright.

**A class the schema cannot currently express.** `Kyeneion` (40186) and
`Sabbatha` (906027) both resolve in Pleiades and are marked **UNLOCATED**, so
they carry no coordinate and `--check` would fail on them. There is no way to
say *"the gazetteer holds this place and does not know where it is"* — it is
`regional` with no id and a note naming the id, which is honest but throws away
the fact that the gazetteer has an entry. **A6 should decide whether that
deserves a state.**

### Next

1. `python -m ingest.run_ingest` then `run_embed` — the recovery changed six
   chunks, so they come back pending. Then `retrieve.crosslingual_check`.
2. `--survey data\place_survey_a4b.txt` — the second round, covering the ids
   seen only as names, the five places the recovery just brought into scope,
   and the Ariake choice.
3. Re-run `eval.run_translation_check` on the three Periplus records and compare
   `chrf_ref` against the Part 6 table. This is the measurement Finding 3 makes
   available and it was not previously possible.
4. Then write the seven records.

## A4 — the re-ingest, and the bug the recovery exposed (2026-08-13)

Re-ingest and re-embed clean: **24 documents → 59 chunks → 57 embedded**, 12 chunks
re-embedded in one batched request, **11/11 retrieval probes still at rank 1**.
Greek eligible chunks 11 → 14. The Adulis cross-lingual probe now lands on the
recovered §4 sentence (`Καὶ κατ᾽ αὐτὴν τὴν ἐν τῇ Ὀρεινῇ ἤπειρον…`, sim 0.524),
which is text that was not in the corpus this morning.

### `align._merge` had never run, and was written for the wrong type

Step 2 crashed:

```
AttributeError: 'ChunkRow' object has no attribute 'char_end'
  answer/align.py:94 in _merge
```

`align.py` is imported by **both** Part 6 and Part 7, and they pass different
row types:

| caller | type | offsets |
| --- | --- | --- |
| `answer/answer_store.py` (Part 7) | has `char_start`/`char_end` — `cite.py` resolves quotations to characters on disk | yes |
| `answer/store.py` (Part 6) | `ChunkRow` | **no** |

`_merge` was written on 2026-08-10 against the first. It survived three months
because **no translation section had ever split into two chunks**; the A4
recovery lengthened §4 and §6 enough that one did, and Part 6 died on the first
live call.

**The coverage was real and one-sided.** `mutate_part7b.py` already carries
*"a merged section keeps exact offsets for its later chunks"*, which exercises
`_merge` thoroughly — with a dataclass that has offsets. And
`answer/test_translate.py`'s alignment fixture is a plain class, not a
dataclass, so `is_dataclass(first)` sent every Part 6 test call down the
single-chunk early return. One module, two callers, and every test on the side
that worked.

**The defensive defaults were the defect, not the crash.**

```python
gap = getattr(following, "char_start", 0) - getattr(previous, "char_end", 0)
```

turns *"this type has no offsets"* into `gap = 0` — a silently wrong merge, with
no error anywhere. The one line that had no default is the only reason this was
ever found. A default that makes a missing field look like a legitimate value is
worse than no handling at all; the crash was the lucky case.

Fixed by branching on `has_offsets()` explicitly: with offsets, the exact
space-for-space arithmetic as before; without, the pieces join with a single
space and the result **does not acquire a `char_end`**. chrF is
whitespace-insensitive by deliberate design, so the separator cannot move a Part
6 score, and nothing that needs to locate a quotation on disk uses the
offset-less type. If that changes, the type gains the columns — not this
function another default.

`mutate_part7b.py` now runs **both** suites and pools their failures, because
verifying a shared module against one of its two callers is the bug written
down. 14/14 mutations, `test_translate` 104 → 110 assertions.

**Standing lesson, fourth occurrence and sharpest yet.** The family is
"two things answering one question, and nothing checks they agree" —
`--find`/`--survey`, `has_extent`/`has_area`, `translation_chunk`/
`translation_chunk_id`. This is its inverse: **one implementation, two data
shapes, and a test suite for each shape that only ever met one of them.**

### Two suites fail on their own account — neither is A4's

- `eval.test_answer_eval`: *"every archived question has a gold case"* fails on
  `20260812T133627+0000-53afe41c` / *"What was exported from Adulis?"*. This is
  the **known open Block 0 item**, already recorded in `PHASE2_PLAN.md` as
  Block D work. 76 of 77 runs scored.
- `scripts/test_recover_baseline.py`: `ModuleNotFoundError: psycopg` in the dev
  sandbox only. It has the module on the host.

### Round-two ids — resolved, and the decoys refused

| place | id | coordinate | note |
| --- | --- | --- | --- |
| Alalaiou islands | 39281 | 15.729/40.003 | archipelago; §4, recovered today |
| Nilus (river) | 727172 | 9.904/30.657 | |
| Diospolis Magna/Thebai | **786017** | 25.665/32.632 | §6's murrine. Decoys: 727111/730107 Diospolis Kato in the Delta, and 216859 — which is **Kabyle, in Bulgaria** |
| Laodicea | **668290** | 35.519/35.777 | settlement + **port** = ad Mare, Latakia. Decoy 668291 "ad Libanum", inland |
| Italia | **1052** | 43.694/11.095 | `related`, **−30..300**. Decoy 452346 is `precise` and dated −750..−330 — the archaic Italia of the toe, four centuries too early |
| Arsinoite nome | 736893 | 29.286/30.735 | Ἀρσινοητικαί is the nome adjective. Decoy 39295, a Red Sea station |
| Libanophoros Chora | 39370 | 17.411/53.407 | region; Pleiades titles it *Libano-*, not *Libanoto-* |
| Mandagara | 50116 | 17.951/73.039 | |
| Leuke (island) | **50091** | 14.019/74.325 | Konkan. Found only on a description match; decoy 226677 is Leuke in the **Black Sea** |
| Pandion | 50201 | 9.654/78.194 | label, −330..640 |
| Ganges (river) | **59822** | 25.932/83.780 | decoy 49984 is *"Ganges (river in **Sri Lanka**)"* |
| Indoskythia | **59850** | 26.366/67.811 | §27's Σκυθία is Indo-Scythia (Sindh), not 1001892 Scythia Minor on the Black Sea |
| Mesene/Characene | 912905 | 31.468/47.344 | Tiaozhi |
| Parthyene/Parthia | **952097** | 38.500/57.500 | −900..300. Decoy 590282460 "Parthian empire" is `related` and dated **2000..2099** — a modern label |
| Roma | 423025 | 41.890/12.491 | |
| Alexandria | 727070 | 31.201/29.910 | settlement + port |
| Barygaza | 59737 | 21.701/72.983 | |

**Still unresolvable, and each is a `regional` with no id and a note saying so:**
Diodorou (759556, UNLOCATED), Kyeneion (40186, UNLOCATED), Sabbatha (906027,
UNLOCATED), Chryse (60485 and 50630, both UNLOCATED), Ommana, Chersonesos —
nothing Indian in 23 hits — Melizeigara, Moschophagoi, Barbaria (471890 is in
**Sardinia**), Trullas, Keprobotros/Chera (246333 is in **Spain**), the Yavanas,
Da Qin, Rinan, Angu, Haixi.

**Ariake is still yours.** 59700 *Ariake/Larike* 22.304/71.976 (Saurashtra,
`label`) against 49874 *Ariake Sadenon* 18.143/74.499 (inland Maharashtra,
`region, label`). §54 says ships come to Muziris **from** Ariake, so the coastal
region is wanted — and this is the edge Schoff prints as "Arabia".

## A4 — the seven records written (2026-08-13)

Decision taken: **stay regional** — the Weilüe's glosses (Da Qin ≈ Rome, Anxi ≈
Parthia, Tiaozhi ≈ Characene, Angu ≈ Gerrha, Haixi ≈ Egypt) are the translator's
identifications, the records carry no citation for any of them, and
`identified` without its `ground_citation` is an assertion wearing the word.
Read as covering Ariake too, where two ids resolve and neither covers §54's
usage; both are named in the note as examined and refused.

Written by `scripts/write_a4_places.py` — generated rather than hand-edited,
because seventy placements done by hand would differ from themselves. Idempotent.

```
W1 placements: 18 placed + 1 declared unplaceable = 19/24 considered
               50 distinct gazetteer ids (was 10), 1 contested
Grounds: {stated: 49, regional: 33, identified: 2}
95 assertions, 26/26 + 14/14 mutations, ingest.verify clean.
```

| record | places | with an id | roles |
| --- | --- | --- | --- |
| `africa-03-periplus-adulis` | 16 | 12 | focus 1, source 8, mentioned 6, waypoint 1 |
| `arabia-01-periplus` | 13 | 9 | focus 1, destination 4, source 3, mentioned 5 |
| `southasia-02-periplus-muziris` | 27 | 22 | focus 1, mentioned 18, source 5, waypoint 3 |
| `eastasia-01-weilue` | 5 | **0** | focus 1, mentioned 2, waypoint 1, destination 1 |
| `eastasia-02-hou-hanshu` | 2 | **0** | focus 1, source 1 |
| `southasia-01-akananuru-149` | 4 | 1 | focus 1, mentioned 2, source 1 |
| `southasia-03-muziris-papyrus` | 4 | 4 | focus 1, waypoint 1, destination 1, source 1 |

**33 of 84 placements are `regional`**, and that is the honest shape of the
result rather than a shortfall. Six places resolve in Pleiades and are UNLOCATED
(Diodorou, Kyeneion, Sabbatha, Chryse ×2, and Skythias); the rest are polities,
peoples and never-located market-towns. `eastasia-01` and `eastasia-02` carry no
id at all — a Greco-Roman gazetteer indexing a Chinese account of Rome, which is
the project's premise appearing in its own gate for the second time in Block A.

Nine ids were **examined and refused**, each named in the note that displaces
it, so none is re-found and silently accepted later: 746710 (Arabia Eudaemon in
north-west Arabia), 471890 (Barbaria in Sardinia), 39295 (a Red Sea Arsinoe),
785982 (a Bakare that is an Egyptian mine), 246333 (a Chera in Spain), 226677
(Leuke in the Black Sea), 49984 (a Ganges in Sri Lanka), 1001892 (Scythia Minor
on the Black Sea), 452346 (the archaic Italia, four centuries early). Plus
216859, which a Diospolis search returns and which is Kabyle, in Bulgaria.

The entry worth reading is `southasia-02`'s **Byzantion**: 49929, a market-town
at 16.503/73.340 on the Konkan, listed in §53 between Melizeigara and Toparon.
Accepting an id on its name would have put Constantinople in a coastal Indian
trade network.

### Still to do in Block A

1. `--refresh` then `--check` on the host — **40 new ids to cache**, and the one
   thing that turns an id into a coordinate. Watch for `has_area` on the three
   region-scale placements (766 Aegyptus, 1052 Italia, 39370 Libanophoros): each
   must render as an extent, and 766's representative point *is* Alexandria's
   coordinate, so a pin there would be actively misleading.
2. The five records still unconsidered — `arabia-04`, `eastasia-03`, `seasia-01`
   ×2 and `-03` — are all **blocked on the GeoNames reader**, which remains the
   largest open item in Block A. `eastasia-02`'s Rinan now joins them.
3. `southasia-01`'s Culli is `regional` for want of a citation, not for want of
   a place: Pleiades 50234 `Pseudostomos (river)` at 9.848/76.819 is the Periyar
   under its Greek name and is almost certainly the referent. One published
   source for Culli ≈ Periyar promotes it to `identified`.
4. `southasia-03`'s `reference_translation` still covers the pre-recovery
   excerpt and does not include the Muziris clause.

## A4 — RESULT ✅ (2026-08-13), and the placement that resolves to nothing

```
50 of 50 ids looked up from pleiades-places-20260810.csv.gz
placements: 84   locatable: 59   cached ids: 50
documents with a placement: 18 of 24
Every placement resolves to a cached, dated gazetteer entry.
27/27 + 14/14 mutations, ingest.verify clean.
```

**The subject-place network, which is what A4 was for:**

| record | focus | places | edges |
| --- | --- | --- | --- |
| `africa-03-periplus-adulis` | Adulis | 16 | 9 |
| `southasia-02-periplus-muziris` | Muziris | 27 | 8 |
| `arabia-01-periplus` | Cana | 13 | 7 |
| `southasia-03-muziris-papyrus` | Muziris | 4 | 3 |
| `eastasia-01-weilue` | Da Qin | 5 | 2 |
| `southasia-01-akananuru-149` | Muciri | 4 | 1 |
| `eastasia-02-hou-hanshu` | Rinan | 2 | 1 |

**31 edges over 71 subject places.** The dot map is a network. Forty of those
places are `mentioned` and draw nothing, which is the vocabulary earning its
keep: a text that names Laodicean wine is not a text about a route to Laodicea.

### `pleiades:766 Aegyptus` resolves, caches, passes — and draws nothing

The `has_area` watch item fired on the first real run. Of the six `regional`
placements carrying an id, five have a genuine extent — Indoskythia, Limyrike,
Pandion, Italia, Libanophoros Chora. **766 Aegyptus has a degenerate bbox**: its
representative point is Alexandria's own coordinate and its bounding box has
zero area.

`PLACES.md` says a regional placement renders as an extent and **never** as a
pin. So Egypt draws nothing at all — while resolving, caching, and passing every
check in `cmd_check`. Egypt is the `source` in **three of the seven** literary
records; it is the most connected node in the corpus, and it would have been
blank space on the first map that drew it, with nothing anywhere saying so.

This is exactly what the `has_extent` / `has_area` split was built for on
2026-08-12, arriving on real data ten days later. The split was made on the
argument that they are *two different questions under one name*; the value of
having asked the second one is that this was a line of output rather than a
silent hole.

`--check` now **reports** unrenderable regional placements — named, counted, and
explicitly not a failure:

```
note: 3 regional placement(s) resolve but cannot be drawn as an extent.
  ~ arabia-01-periplus::subject_places[9]: 'pleiades:766' (Aegyptus …)
  ~ southasia-02-periplus-muziris::subject_places[26]: 'pleiades:766' …
  ~ africa-03-periplus-adulis::subject_places[9]: 'pleiades:766' …
```

A report and not a failure because the entry is honest and the id is right. What
to do is **A5's decision, and it is a real one**: draw the extent of something
else, accept the gap, or drop the id and say so in a note. A failure here would
demand a fix before the decision could be taken. Mutation-verified, with a
control that a regional placement carrying a real extent is not reported.

### Block A after A4

| item | state |
| --- | --- |
| **GeoNames reader** | the largest open item. Blocks `arabia-04`, `eastasia-03`, `seasia-01/02/03` and now `eastasia-02`'s Rinan — 5 records unconsidered. Start with `--inspect` on one country file |
| A5 | region view → place view, **plus the 31 edges**, plus the Egypt decision above |
| A6 | date-overlap check; and whether "the gazetteer holds this place and does not know where it is" deserves a state — six UNLOCATED ids are currently indistinguishable from no entry at all |
| Pattanam's sceptical citation | still provisional |
| Culli ≈ Periyar | one published source promotes 50234 from `regional` to `identified` |
| `southasia-03` reference translation | pre-recovery, missing the Muziris clause |

---

# A5 — starting point (for the next thread)

**State: A4 complete, 2026-08-13.** Block A is roughly three-quarters done.

```
24 documents -> 59 chunks -> 57 embedded (voyage/voyage-3.5)
Retrieval 11/11 at rank 1.  Translation gold set 12 cases.
W1: 84 placements across 18 documents + 1 declared unplaceable = 19/24 considered
    59 locatable, 50 distinct cached ids, 1 contested
    Grounds: {stated 49, regional 33, identified 2}
    31 edges over 71 subject places
Suites: ingest.test_places 95 · answer.test_translate 110 · verify clean
Mutations: places 27/27 · part7b 14/14
```

## What A5 is

`PHASE2_PLAN.md`: region view becomes place view. Five requirements, and the
fourth is the new one:

- points render **from cached gazetteer coordinates only**;
- `ground` is **shown** — a `regional` placement must not look like a `stated` one;
- a contested identification renders as contested, not as a pin;
- **trade texts render as edges between subject places** — the ORBIS-shaped
  thing, and now buildable: `source → focus → destination`, with `mentioned`
  drawing nothing. `Place.draws_edge` is the predicate;
- every point clicks through: map point → record → quotation → characters on disk.

## The three decisions A5 has to make before it draws anything

1. **What to do about Egypt.** `pleiades:766 Aegyptus` resolves, caches, passes
   `--check`, and has a **zero-area bbox**. A regional placement renders as an
   extent and never as a pin, so Egypt draws nothing — and it is the `source` in
   three of the seven literary records, the most connected node in the corpus.
   `--check` reports it by name. Three options and none is obviously right:
   draw the extent of some other feature, accept the gap and show it as a gap,
   or drop the id and say so in a note. **Do not resolve this by letting a
   regional placement fall back to its representative point** — that is the pin
   the whole `ground` vocabulary exists to prevent.

2. **How an edge with an unlocatable end is drawn.** Several are: Ariake is
   `source` for Muziris with **no id at all**; Sabbatha is `source` for Cana and
   is UNLOCATED in Pleiades; all of `eastasia-01`'s and `eastasia-02`'s edges
   have no coordinate on either end. A line needs two points and these have one
   or none. Dropping them silently would delete the Weilüe and the Hou Hanshu
   from the network entirely — the two records that are most the point of the
   project. Whatever is chosen, the absence has to be visible.

3. **Bands and grounds are not comparable across profiles, and the UI must not
   imply they are.** Standing from Part 6: a `high` on verse (cos 0.70) and a
   `high` on prose (cos 0.96) are not the same evidence. The same now holds for
   `ground`: `stated` on a Greek port and `regional` on a Chinese polity are
   different kinds of claim, not different strengths of one.

## What A5 can rely on

- `Place.draws_edge` — true for `source`/`destination`/`waypoint`, false for
  `focus` and `mentioned`. The edge derivation is `source → focus → destination`
  and there is exactly one focus per block, enforced at load.
- `has_point` / `has_extent` / **`has_area`** — three questions, three answers.
  `has_extent` is "any bbox"; `has_area` is "a bbox that is not degenerate", and
  a Pleiades *point* place has a degenerate bbox. Use `has_area` for anything
  that draws a region.
- `locationPrecision` on every cached entry — Pleiades' own statement of how well
  **it** knows the point, which is a different axis from our `ground`. A5 needs
  both to render honestly, and several placements are `precise` on a coordinate
  our own corpus treats as contested (Muziris/Pattanam).
- `min_date` / `max_date` / `time_period_keys` — cached but **unused**. A6 owns
  the overlap check; A5 may want them for a time slider.
- Every placement carries a `note` saying what its id was confirmed against and,
  where one exists, which id was examined and refused. Ten refusals are on the
  record.

## Traps, in the order they will be met

- **Muziris is one id used by three records** (`southasia-01`, `-02`, `-03`) and
  a fourth as a findspot (`southasia-04`, `identified` + `contested`). Pleiades
  marks 10.154/76.213 `precise`; our own corpus treats that identification as
  open. The map must not render three confident pins and one contested one at
  the same coordinate.
- **Aksum 39303 is used three ways** — `africa-01` findspot, `africa-02` origin,
  `africa-03` subject `source`. That is the block design working and it is the
  first place a naive renderer will draw three overlapping markers.
- `arabia-02-palmyrene-tariff` and `africa-01-ezana-stone` are still `pointer`
  chunks, held out of retrieval by construction. They **do** carry findspots, so
  they appear on the map and have no quotable text behind them. The click-through
  has to survive that.

## Standing lessons this block added

- *One implementation, two data shapes, and a test suite for each that only ever
  met one of them.* `align._merge` was fully covered — against one of its two
  callers. Verify a shared module against **every** caller.
- *A defensive default that makes a missing field look like a legitimate value is
  worse than no handling at all.* `getattr(x, "char_end", 0)` turned a type error
  into silently wrong arithmetic; the one line without a default is why it was
  found.
- *Nothing in the pipeline compares an excerpt against its own cited source.* Every
  check pointed inward, and a uniformly short excerpt is internally consistent.
  20% of the Periplus Greek was missing for four days of work on those records.
- *A resolving id at the wrong place is worse than no id* — now with ten worked
  examples, of which Byzantion on the Konkan is the one to show people.

## To run

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
$d = "$env:USERPROFILE\Downloads\pleiades-places-20260810.csv.gz"

python -m ingest.test_places            # 95
python -m answer.test_translate         # 110
python scripts\mutate_places.py         # 27
python scripts\mutate_part7b.py         # 14
python -m ingest.verify
python -m ingest.gazetteer --check --dump $d
python ui\build_ui_data.py --verify
node ui\check_ui.mjs
```

Block A has spent one batched embedding request in total — for the twelve chunks
the Greek recovery invalidated. Everything else is offline.

---

# A5 — RESULT ✅ (2026-08-13): the join, the map, and the three decisions

```
places (A5): 51 pin(s), 5 extent(s), 28 gap(s) across 18 placed document(s);
18/31 subject-place edges drawable; 5 document(s) not yet considered,
1 declared unplaceable
27/27 + 14/14 mutations, ingest.verify clean, ingest.gazetteer --check clean.
check_ui.mjs: 18/18 checks passed, including 4 new to A5.
```

## What was built

`ui/build_ui_data.py` gained `build_places()` — the join `PHASE2_PLAN.md` A5
specifies: `ingest/places.py`'s validated placements against
`ingest/gazetteer.py`'s cached coordinates, classified into exactly three
outcomes (`_place_geometry`): **pin** (`stated`/`identified`, a cached
representative point), **extent** (`regional` with a real bbox), or **gap**
(everything else — named, reasoned, never dropped). Placements sharing a
cached id are merged into one `groups` entry rather than drawn as separate
overlapping markers; `subject_places` blocks are walked a second time to
derive the `source → focus → destination` / `waypoint → focus` edges, each
tagged `drawable` only when both ends resolved to a pin or an extent.

`ui/index.html`'s "Regions & sources" tab is now **Places**: a hand-rolled
equirectangular SVG projection (`buildMap()`), fit to whatever the corpus
actually cached — no basemap, no coastline, no CDN, consistent with the rest
of this build. Pins, shaded extents and edges are clickable through to a
`place`/`group`/`edge` provenance panel, and `renderRecordProvenance` now
lists every place a record carries, drawn or not, closing the loop the old
tab's record cards started. Coordinates are never authored here; they are
read from the same `data/gazetteer.json` `ingest.gazetteer --check` already
verifies, so the map cannot know something the CLI check does not.

**Click-through, honestly labelled.** `subject_places` and `findspot_places`
carry no character span the way Part 7's answer citations do — nothing in
Block A wrote an `abs_start`. `bestEffortLocate()` searches the record's own
fields for the place's name and shows what it finds, captioned as a text
search rather than a recorded citation — the same caution this page already
applies to `case_only` spans elsewhere, extended to a case where no span was
ever claimed in the first place.

## The three decisions

**1. Egypt.** `pleiades:766` resolves, is cached, and has a degenerate bbox —
a `regional` placement that can never be drawn as an extent, and the `source`
in three of the seven literary records. Resolved by treating it as one
instance of a general rule rather than a special case: **a gap is reported,
never guessed at.** Egypt does not draw a pin (that is the one thing `ground`
exists to prevent) and does not draw an extent (there is none to draw). It
appears instead in its three records' place lists and in the "considered —
nothing resolves to a drawable point" cards where it is the sole cause, each
clickable through to the full record. The absence is visible; nothing is
invented to hide it.

**2. An edge with an unlocatable end.** Ariake (no id at all), Sabbatha
(resolves, UNLOCATED), and every one of the Weilüe's and Hou Hanshu's edges
(no coordinate on either end) all use the same mechanism as Egypt: `drawable`
is computed per edge from both ends' geometry, and a non-drawable edge is
listed — with the reason, per end — in "edges named in the text, not drawn on
the map," never silently dropped from `P.edges`. The Weilüe and the Hou
Hanshu, whose every place is a gap, get their own cards ("considered —
nothing resolves to a drawable point here") so the two records most the point
of the project are not simply absent from the tab that is supposed to be
about geography.

**3. Grounds are not comparable across profiles.** The map tells `ground`
apart by **shape**, not colour: a pin (`stated`/`identified`) is a filled
circle, a `regional` extent is a dashed, translucent rectangle, and a
`contested` identification is a dashed, hollow ring — three categories, not a
gradient. None of `--good`/`--warn`/`--bad`, already used elsewhere on this
page for grounded/refused/ungrounded, is reused for `ground`: doing so would
assert an ordering PROGRESS.md explicitly refused ("stated on a Greek port
and regional on a Chinese polity are different kinds of claim, not different
strengths of one"). `location_precision` — Pleiades' own confidence, a
different axis — is carried into every place and group panel alongside
`ground` rather than folded into it.

## The Muziris trap, handled

`pleiades:50146` is claimed `stated` by three records and `identified` +
`contested` by a fourth (`southasia-04-pattanam`, Pattanam). `build_places()`
groups all four under one `cache_key`; the map draws **one** marker, styled
contested because at least one member is, with a member list in its panel
naming each record and its own ground rather than flattening four claims into
one pin. Aksum (`pleiades:39303`, used three ways — findspot, origin, subject
`source`) merges the same way and draws once.

## Verified

```
python -m ingest.test_places        95 assertions, ok
python -m answer.test_translate     110 assertions, ok
python scripts/mutate_places.py     27/27
python scripts/mutate_part7b.py     14/14
python -m ingest.verify             clean (pre-existing warning: arabia-02 empty reference_translation)
python -m ingest.gazetteer --check  clean (the 3 Aegyptus notes are expected, not failures)
python ui/build_ui_data.py          places (A5) line above; 980 KB
node ui/check_ui.mjs                18/18, including the 4 new checks below
```

`check_ui.mjs` gained four A5 assertions, each checking the data rather than
reading the HTML: every placement (84) is listed on its own record's panel,
so "not drawable" can never collapse into "not reachable"; every cached
point/extent (49) and every drawable edge (18) the data claims to plot
actually appears in the SVG `buildMap()` returns; and all 24 records are
clickable from the Places tab regardless of whether they carry a single
placement. A hand-rolled tag-balance check over `viewPlaces()`,
`viewQuestions()`, `viewAbout()` and a record panel found no unclosed
`<div>`/`<svg>`/`<g>`/`<rect>`/`<line>`/`<circle>`/`<span>`/`<button>`.

`build_ui_data.py --verify` exits 1 on one pre-existing `moved` and one
pre-existing `absent` span in `eastasia-02-hou-hanshu`/`africa-03` answer
archives — unrelated to A5, predating this session, and the exact
already-documented Part 9 phenomenon the About tab explains ("an archived
citation is only valid against the corpus version that produced it").

## Carried into A6

- The mutation-verified guards `PHASE2_PLAN.md` assigns to A6 ("a hand-authored
  coordinate with no `pleiades_id`", "an `identified` placement with no
  citation", "a `pleiades_id` at a non-resolving id") are `ingest`-side and
  distinct from what A5 built — `build_places()` reports an uncached id as a
  build failure (exit 2) but does not yet have a mutation test proving that
  failure path fires.
- `location_precision` and `min_date`/`max_date`/`time_period_keys` are now
  carried into every place/group panel but nothing renders a time slider —
  A6's stated option, still open.
- The "gazetteer holds this place and does not know where it is" state
  (UNLOCATED — Cyeneum, Sabbatha, Chryse) is still indistinguishable, at the
  data layer, from "no entry at all"; both surface identically as a gap with
  a `note`-derived reason on this page. A6 owns giving them separate states.

---

# A5 addendum — the basemap I argued my way out of, and the world drawn inside out (2026-08-13)

**Raised by the curator, immediately on opening the page: "there's no actual
map, it's just dots and lines."** Correct, and the reason it was correct is
worth more than the fix.

## The reasoning error

A5 shipped with no coastline, and the argument was written into `buildMap()`:

> This project cites gazetteer ids for every point it draws; a traced coastline
> would be the one shape on the page that came from nowhere citable, so the
> grid is the only backdrop.

That conflates two different rules. *Coordinates are never authored* governs
**placements** — claims about where a record's place is — and `ingest/places.py`
enforces it absolutely. A coastline is **not a claim about the corpus**; it is
the reference frame the claims are read against, and it can carry provenance
exactly like any other source here. Natural Earth is public domain, versioned
and datable, and sits under precisely the discipline `data/gazetteer.json`
already uses.

The failure mode is the interesting part: **a correct principle, applied one
category too wide, produced a worse artefact than having no principle.** The
map spanned 10–84°E and 9–56°N with no way to tell the Red Sea from the Bay of
Bengal, on a project whose reference model is ORBIS and whose own `PHASE2.md`
rates the ORBIS parallel "High". Rigour that removes the thing it was meant to
protect is not rigour.

Also worth recording: **nothing in `PHASE2_PLAN.md` deferred this.** W2 is
retrieval, W3 corpus scaling, W4 the gold set — there is no later block where a
basemap arrives. "It gets added later" would have been false; it would simply
never have been added.

## What was built

`scripts/build_coastline.py` → `data/coastline-ne110m-20260813.json` (33 KB,
46 polygons, 2,060 points). Natural Earth 1:110m Admin 0, dissolved with
`unary_union` so the boundary is **coast and not a political map** — drawing
21st-century borders under a first-century Indian Ocean is a claim this project
should not make by accident. Clipped to −25..150°E / −40..75°N, deliberately
wider than today's cached points so the five GeoNames-backlog records (Óc Eo,
Khao Sam Kaeo, Gyeongju) will not need a re-clip the day they are placed.
Simplified at 0.05° — under one pixel at this scale — and rounded to 3 dp.

The snapshot records its own source, scale, terms, retrieval date, clip window
and simplification tolerance, and the page prints the attribution in the map
legend. A missing snapshot is a **note, not a build failure**: the map still
draws every point, extent and edge, each still tracing to a cached gazetteer
id. An absent placement would be a false claim; an absent backdrop is only
harder to read. Different severities for different kinds of wrong.

## The defect that every passing check missed

The first snapshot emitted `.boundary` — every ring, with no record of which is
an outer coast and which is an inland sea. Drawn as one filled SVG path, the
winding rule guessed: **the Mediterranean and Black Sea rendered as water, and
the Indian Ocean and Atlantic rendered as land.** Open ocean is not a ring at
all; it is simply *outside* every ring, and a fill cannot represent "outside"
without knowing which side is which.

`check_ui.mjs` passed. All of it. Its A5 assertions check that each cached
point and each drawable edge is **present** in the SVG — and all 49 points and
18 edges were present, sitting on top of an inside-out world. The bug was found
by rendering the map to a PNG and looking at it.

> **Standing lesson added: an assertion about presence says nothing about
> correctness.** This repository has now paid for that four times — the Part 4
> probe that passed on `doc_id` while pointing at the wrong passage, the
> `--survey` that reported hits on substrings of unrelated descriptions, the
> stale `data.js` that certified 61 runs while the archive held 77, and now a
> map that plotted every point correctly onto an inverted planet.

Fixed by emitting real polygons as `[exterior, hole, ...]` and rendering with
`fill-rule="evenodd"`, which is what makes the Caspian and the Black Sea water.

**And then a second, opposite bug:** with marker positions seeded as label
obstacles, every label collided with *its own* marker and the map rendered with
no names whatsoever. Also invisible to every assertion, also caught by looking.
Obstacles now carry their owning `cache_key` and are skipped for their own
label.

## The guard, mutation-verified

`check_ui.mjs` gained a check that asserts a **property** rather than presence:
nine control points — Aksum, the Sahara, central Arabia, the Deccan; the
Mediterranean, Black Sea, Arabian Sea, Bay of Bengal, Red Sea — evaluated with
the same even-odd rule the SVG uses over the same rings. Land must be land and
sea must be sea.

Verified to fail against the defect it guards, per this repository's standing
rule. Injecting a world-spanning ring into the bundle (the parity flip the
boundary-rings bug caused) makes it fail and name all nine points; restoring
the bundle makes it pass. A second check asserts the snapshot carries the
provenance the legend prints.

## Labels

29 of 49 places are labelled. Placement order is deliberate and stated —
busiest nodes first, then extents, then alphabetical — so that when the Konkan
coast runs out of room it is Muziris and Barygaza that keep their names rather
than whichever market-town sorted last. Colliding labels are dropped, not
overlapped; the legend says so, and every point remains clickable with its full
Pleiades title in the panel. Pleiades' scholarly apparatus is trimmed for the
map only (`Mandagara?` → `Mandagara`, `Adane/Athenae/Eudaimon Arabia` → `Adane`).

## Verified

```
python scripts/build_coastline.py   46 polygons, 2060 points, 33 KB
python ui/build_ui_data.py          1016 KB, coastline attributed
node ui/check_ui.mjs                20/20, incl. the land/sea property check
  └─ mutation-verified: world-spanning ring injected -> FAILS, naming 9 points
python -m ingest.verify             clean
python -m ingest.gazetteer --check  clean
python -m ingest.test_places        ok    python -m answer.test_translate  ok
python scripts/mutate_places.py     27/27  python scripts/mutate_part7b.py  14/14
```

`scripts/build_coastline.py` needs `geopandas<1.0` and is a **one-off
generator**, not on the build or test path. Nothing in the normal build imports
it; `ui/build_ui_data.py` reads only the committed JSON snapshot.

---

# A5 addendum 2 — pan and zoom, and why East and Southeast Asia are not on the map (2026-08-13)

## Why the Chinese and Southeast Asian sources are absent

Asked by the curator on reading the map. It is **not a rendering gap** — it is
two different states, and the distinction is the one `no_places_reason` and the
gap lists were built to preserve.

**Curated, and nothing resolves (2 records, 7 placements).**

| record | places | drawable |
| --- | --- | --- |
| `eastasia-01-weilue` | Da Qin, Anxi, Tiaozhi, Angu, Haixi | 0 of 5 |
| `eastasia-02-hou-hanshu` | Rinan, Da Qin | 0 of 2 |

Every one is `regional` with no id, because **Pleiades is a Greco-Roman
gazetteer and holds no entry for any of them**. A4 went further and refused the
available shortcut: the translator's glosses (Da Qin ≈ Rome, Haixi ≈ Egypt) are
uncited identifications, so `pleiades:766` was deliberately **not** reused for
Haixi even though it is used for Egypt in three other records, and
`pleiades:423025 Roma` was examined and refused for Da Qin on the grounds that
the city is not the empire. Those refusals are why the two records that are
most the point of the project draw nothing — and they were the right calls.

**Not yet placed at all (4 records).** `eastasia-03-hwangnam-glass` (Gyeongju),
`seasia-01-oc-eo-medallion`, `seasia-02-oc-eo-site` (Óc Eo),
`seasia-03-khao-sam-kaeo` — plus `arabia-04-jabal-dabub`. These are the
**GeoNames backlog**, blocked on a reader that does not exist. `PLACES.md`
predicted exactly this set on 2026-08-12: "no Pleiades entry for Gyeongju, Óc
Eo, Khao Sam Kaeo or Jabal Ḏabūb — roughly half the findspot records … the
premise of Mundus Ulterior showing up in its own gate."

So the map is empty east of the Ganges because the gazetteer is, not because
the renderer dropped anything: all 7 curated placements appear in the "considered
— nothing resolves to a drawable point here" cards, and all 5 unplaced records
in "not yet placed". **The GeoNames reader remains the single highest-value
open item in Block A** — it alone would put Korea, Vietnam and Thailand on the
map, and it is what turns "Rome and the wider world" from a claim into a
picture. It is not scheduled in `PHASE2_PLAN.md` and needs an owner.

## Pan and zoom

Held as a **centre plus a zoom factor**, with the visible window derived on
every draw — not as an SVG transform on a group. A transform is cheaper per
frame but scales everything inside it: marker radii, stroke widths and type
size would all grow with the zoom, and the label collision solver, which works
in pixel space, would be solving against geometry that no longer matches what
is drawn.

Recomputing the window keeps `buildMap()` a pure function of (data, window) —
the thing `check_ui.mjs` already calls with no arguments — and buys a real
feature rather than only avoiding a problem: **label collisions are re-solved
at every zoom level**, so the Konkan market-towns that have no room at full
extent get their names back as you zoom into them. At the default view 29 of 49
places are labelled; at ×14 over Malabar, Tyndis, Bakare, Nelkynda and
Cottonara appear, with Limyrike and Pandion as shaded extents around them.

Wheel zooms about the cursor (the lon/lat under the pointer stays pinned),
drag pans, `+`/`−`/`Reset` for people who would rather click, and a live `N×`
readout. A drag that moved more than 3 px swallows the click that follows it,
so panning across the map cannot also select whatever marker the pointer was
released over. Only the SVG is rebuilt, inside `requestAnimationFrame` — never
the whole view, which would rebuild the record grid and destroy the provenance
panel's scroll position while the reader is using it.

### The bug zoom introduced, and the reason it was found

Coastline culling skipped any landmass with **no vertex inside the window**.
Correct at full extent, and wrong the instant zoom existed: zoomed into the
middle of the Sahara, every vertex of Africa is off-screen while Africa covers
the entire view, so **the map lost its land exactly when land was all there
was**. Replaced with a bounding-box overlap test.

This is the *same shape* as the inverted-world bug in the previous addendum,
and it is worth naming as a pattern rather than two incidents: **both were
correct-looking code whose assumption held only for the one view every test
exercised.** `check_ui.mjs` called `buildMap()` at the default window and
nowhere else.

## The guards, both mutation-verified

`check_ui.mjs` is now 20 checks. Three are new here, and they assert
**properties across views** rather than presence in one:

- the coastline still draws at four zoomed windows, including mid-ocean and
  inside a continent;
- zooming never distorts the aspect ratio (lon-span : lat-span must always
  match W : H, to 1e-9);
- reset returns *exactly* to the full extent, not merely near it.

Verified to fail against the defect they guard, per standing rule: restoring
the vertex-inside culling makes the first check fail and name the two views
that lose their land ("mid-ocean, x8", "inside the Sahara, x40"); restoring the
bbox test makes it pass.

## Verified

```
python ui/build_ui_data.py          1016 KB
node ui/check_ui.mjs                20/20
  └─ mutation-verified: vertex culling restored -> FAILS, naming 2 zoom views
python -m ingest.verify             clean    python -m ingest.gazetteer --check  clean
python -m ingest.test_places        ok       python -m answer.test_translate     ok
python scripts/mutate_places.py     27/27    python scripts/mutate_part7b.py     14/14
```

## Standing lesson added

> *A test that exercises one view of a rendered artefact tests the view, not
> the renderer.* Two bugs in one block — an inside-out world and a vanishing
> continent — were both invisible to a full suite that only ever drew the
> default window. Presence assertions compounded it: every point and edge was
> correctly present in both broken maps.

---

# A5 addendum 3 — the GeoNames reader (2026-08-13)

**Built to close the five unplaced records** — Gyeongju, Óc Eo ×2, Khao Sam
Kaeo and Jabal Ḏabūb — which is the whole of Southeast Asia and half of East
Asia. Taken before A6 deliberately: G1 criterion 1 asks for 24/24 considered,
and 19/24 cannot be argued up.

**Status: the code is complete and verified; the ids are not yet resolved.**
GeoNames distributes country data only as zip, and a binary fetch does not
survive this environment's web tooling, so the dumps have to be downloaded on
the host — exactly as the Pleiades dump already is. That is the established
pattern here, not a workaround: `--dump` has always pointed at a file the
curator downloaded.

## What was built

- **`--geonames-dump`, `--geonames-find`, `--refresh-geonames`** in
  `ingest/gazetteer.py`. A separate reader from the Pleiades one, because the
  two agree on almost nothing: Pleiades is a headed CSV of ancient places with
  bboxes and attested date ranges; GeoNames is headerless TSV of modern
  features with none of those. Threading both through `read_dump` would have
  produced a function whose every line asked which gazetteer it was serving.
- **Shape verification in place of column discovery.** The Pleiades reader
  discovers columns from a header row because that README was wrong three
  times. GeoNames has no header and documented positional columns, so there is
  nothing to discover — and the obligation behind the rule still holds. The
  first data row is instead checked for field count, a numeric id, parseable
  coordinates and a documented feature class, and a file that fails is
  reported with the row that failed.
- **Snapshot dating from the publisher's own timestamp.** GeoNames filenames
  carry no date — `KR.zip` is always "current" — so `dump_date_from_name`'s
  rule cannot apply and its reason still does. The zip's internal member
  timestamp is GeoNames' build time and is used; a bare `.txt` has only an
  mtime recording when the *curator* unzipped it, and is refused unless
  `--geonames-date` is stated. Sixth time this repository has refused an
  undated snapshot.

## The schema defect this uncovered

`data/gazetteer.json` held **one flat `licence` block**, written when there was
one gazetteer. Pleiades is CC BY 3.0 US; GeoNames is CC BY 4.0. Recording the
second would have overwritten the first, leaving every Pleiades point on the
map attributed to terms its publisher never chose — and nothing anywhere would
have noticed.

This is the *same shape* as the defect the file's own comment records for
`sources`: "a single `source` block was correct while there was one gazetteer
and would have become a lie the moment there were two." It was fixed for
`sources` and missed for `licence`, in the same file, by the same author.

> **Standing lesson added:** *when a container is split because a second case
> arrived, every sibling container holding the same assumption must be split
> with it.* `sources` was made per-gazetteer at A2 and `licence` beside it was
> not; the second gazetteer was six days away and already named in `GAZETTEERS`.

Migrated to `licences` keyed by gazetteer, on read rather than by a one-off
script, so a cache written before today still loads. A cache holding **both**
shapes is refused outright rather than one being guessed as current. `--check`
now demands a licence and a publisher declaration **per gazetteer the corpus
actually cites** — so declaring a gazetteer obliges nothing until a placement
uses it, and obliges it the moment one does.

Both GeoNames licence documents are already recorded verbatim: CC BY 4.0 from
creativecommons.org, and GeoNames' own declaration from the dump readme
("This work is licensed under a Creative Commons Attribution 4.0 License").

## Verified

```
python -m ingest.test_places        16 new GeoNames assertions, all pass
python scripts/mutate_places.py     34/34  (27 before, 7 new)
python -m ingest.verify             clean    ingest.gazetteer --check   clean
python -m answer.test_translate     ok       scripts/mutate_part7b.py   14/14
node ui/check_ui.mjs                20/20
```

The seven new mutations restore, in turn: an unchecked field count, an accepted
header row, an undocumented feature class, a guessed snapshot date, one licence
covering every gazetteer, a legacy flat licence read as covering all of them,
and a cache with both shapes picking one silently.

**Two of them had to be re-aimed, and the reason is worth keeping.** Disabling
the field-count guard makes the *reader* crash three lines later on a truncated
row, and this harness counts a crash as a MISS — correctly, since a crash is
not a guard firing. Re-aimed at `verify_geonames_shape` as a pure function and
at an **over-long** row rather than a short one, which exercises the identical
check and, with the guard removed, silently truncates to 19 columns instead of
crashing. That is the real defect anyway: a stray tab inside a place name
misaligns every column after it. Fifth occurrence of the over-determination
shape in this repository.

## The four searches, and the two that were refused

Dumps downloaded and searched on the host, 2026-08-13. Written by
`scripts/write_a5_geonames_places.py`.

| site | id | code | outcome |
| --- | --- | --- | --- |
| Gyeongju | `1841603` | `P.PPL` | **accepted** — 0.6 km from the Daereungwon tumuli |
| Óc Eo | `13405688` | `P.PPLA2` | **accepted** — the modern town, used by both Óc Eo records |
| Khao Sam Kaeo | `8242723` | `T.HLL` | **REFUSED** — 297 km from Chumphon |
| Jabal Ḏabūb | `7365997` | `P.PPL` | **REFUSED** — 286 km from Ad Dali', and a settlement not a mountain |
| Jabal Ḏabūb | `12118329` | `P.PPL` | **REFUSED** — 152 km from Ad Dali', same reason |

**Khao Sam Kaeo is Byzantion-on-the-Konkan again.** GeoNames holds a hill of
exactly that name, and it is 297 km south of Chumphon in a different province.
*Khao Sam Kaeo* is a generic Thai toponym — roughly "three-crystal hill" — so
the name matches a hill that is not this one. Accepting it would have drawn the
peninsular trade site 300 km down the coast, on a resolving id with a plausible
coordinate. Caught the same way as every other: **on the coordinate, not the
name.**

**Jabal Ḏabūb failed on feature code first.** Both candidates are `P.PPL`,
populated places called *Ad Dabūb*, where the record names a mountain — Arabic
*jabal*, which GeoNames classes `T.MT`. A settlement called Ad Dabūb is not
Mount Ḏabūb, and neither sits in the Dhale region the record gives. The feature
code did the work the coordinate then confirmed; this is the first refusal in
the corpus where the *type* was the discriminator.

Both refused sites are now `regional` with the refusal on the record. Two of
the five stay off the map, and that is the correct result rather than a
shortfall.

**Ground is `stated`, not `identified`, for the three accepted placements.**
`PLACES.md` says a GeoNames placement "will usually be `identified`", and that
guidance is written for Adulis ≈ Zula, where a scholar maps an ancient name to
a modern location. Nothing of the kind happens here: the records name Gyeongju
and Óc Eo themselves, as modern places, and GeoNames holds those same modern
places. `identified` would demand a `ground_citation` for the proposition that
Gyeongju is Gyeongju. What the coordinate **denotes** is the real exposure, and
it is carried in every note: a city centre is not a tomb, a town is not an
excavation trench.

## G1 criteria 1 and 3, now met

```
W1 placements: 23 placed + 1 declared unplaceable = 24/24 considered,
18/17 with a named place, 52 distinct gazetteer ids, 1 contested
Grounds: {identified 2, regional 35, stated 52}
```

Up from 19/24 and 15/17. Criterion 1 ("24/24 carry at least regional") and
criterion 3 (≥17 named, ≥1 contested rendering as contested) are satisfied;
criterion 2 (zero authored coordinates, mutation-verified) has held since A1
and is now 34 mutations. A6 owns the remaining two.

## Outstanding — one command

The two accepted ids are cited but **not yet cached**, so
`ingest.gazetteer --check` currently fails, naming all three placements that
use them. That is the guard working: an id in a record with nothing behind it
is precisely what it exists to catch.

```powershell
python -m ingest.gazetteer --geonames-dump "$env:USERPROFILE\Downloads\KR.zip" --refresh-geonames
python -m ingest.gazetteer --geonames-dump "$env:USERPROFILE\Downloads\VN.zip" --refresh-geonames
python -m ingest.gazetteer --check
python ui\build_ui_data.py
node ui\check_ui.mjs
```

After which Korea and Vietnam appear on the map for the first time, and the
default view's bounding box widens from 84°E to about 129°E — the first time
the map's extent has matched the project's stated scope.

## Done (2026-08-13). Two defects the refresh exposed, both mine

The dumps were downloaded and both ids cached. Final state:

```
placements: 89   locatable: 62   cached ids: 52  {geonames 2, pleiades 50}
documents with a placement: 23 of 24  (+1 declared unplaceable = 24/24)
Every placement resolves to a cached, dated gazetteer entry.
places (A5): 54 pins, 5 extents, 30 gaps; 0 documents not yet considered
```

### 1. A check that named the wrong cause, written after the lesson was written down

`--refresh-geonames` reported the ids it did not find as `UNRESOLVED`, told the
curator to "check you have the right country file", and exited non-zero. But a
GeoNames country file holds **one country** and this corpus spans four, so
`KR.zip` will *always* lack the Vietnamese id and `VN.zip` will *always* lack
the Korean one. Both runs printed a false alarm to a curator holding exactly
the right file, and both exited 1 on a successful refresh.

*A check that matches too broadly names the wrong cause* — fifth recorded
instance, and the first written **after** the lesson was recorded in this very
file. Knowing the rule did not prevent it; the rule was applied to the Pleiades
path, where it is correct (one global dump, so a missing id does not exist)
and carried unchanged to a path where the premise is false.

Now: not-in-this-file is a note, still-uncached-anywhere is the actionable
line, and completeness is left to `--check`, which is the only command with
the whole picture. Four new assertions, mutation-verified.

### 2. `sources.geonames` named whichever file was refreshed last

After `KR.zip` then `VN.zip`, the cache claimed the GeoNames source was
`VN.zip` — so the provenance of Gyeongju's coordinate, which came from
`KR.zip`, was recorded as a file that does not contain it.

**Third instance in this repository of one container holding what is really N
things**: `sources` was flat and became per-gazetteer at A2; `licence` was flat
and became per-gazetteer earlier today; and `sources.geonames` was one file and
is really one per country. Each was found only when the second case arrived.

Fixed by recording `source_file` on every cached GeoNames entry and
accumulating `sources.geonames.files` rather than replacing it. `--stats` now
prints one line per country file.

> **Standing lesson, restated with a third worked example:** *when a container
> is split because a second case arrived, check every sibling AND every child
> holding the same assumption.* Splitting `sources` per gazetteer at A2 did not
> prompt splitting `licence` beside it, and splitting `licence` today did not
> prompt splitting `sources.geonames` below it. The shape recurs downward as
> well as sideways.

**Re-run the two refresh commands** to pick up `source_file` on the two cached
entries; nothing else changes and `--check` passes either way.

### Verified

```
python -m ingest.verify             clean    ingest.gazetteer --check   clean
python -m ingest.test_places        ok       answer.test_translate      ok
python scripts/mutate_places.py     35/35    scripts/mutate_part7b.py   14/14
node ui/check_ui.mjs                20/20
```

Block A is complete. A6 inherits: the two mutation-verified guards
`PHASE2_PLAN.md` assigns it, the date-overlap check, and the UNLOCATED-versus-
no-entry distinction — Cyeneum, Sabbatha and Chryse still surface identically
to places no gazetteer has heard of.

## Why there is nothing from China on the map, and why that is correct

Asked on reading the finished map, 2026-08-13. The answer is **not** a
gazetteer gap: **no place in China is named anywhere in the corpus.**

| record | places named | where they are |
| --- | --- | --- |
| `eastasia-01-weilue` | Da Qin, Anxi, Tiaozhi, Angu, Haixi | all **west** of China — the section is titled "Peoples of the West" |
| `eastasia-02-hou-hanshu` | Da Qin, Rinan | Rinan is a Han commandery on the **central Vietnamese** coast |
| `eastasia-03-hwangnam-glass` | Gyeongju | Korea — now placed |

No record in the corpus has a Chinese findspot either. The two Chinese sources
are Chinese *texts about the west*, which is precisely why they are in this
corpus, and the map showing no point in China is the corpus being represented
accurately. A4 already refused the obvious way to manufacture one: *"Luoyang,
the court the tribute was offered to, is NOT named in this passage and is
deliberately not placed."*

Two genuine follow-ups are recorded here rather than done, by decision of
2026-08-13 — neither belongs to A6's actual job (the G1 gate and verification),
and both need judgement better taken deliberately than appended to a finished
block.

**1. Rinan — a TODO the record wrote for itself.** Its note reads: "this is
GeoNames territory, and the GeoNames reader is the outstanding Block A item.
Promote to a named place when it exists." It now exists. The complication is
that Rinan is an **ancient commandery**, not a modern place, so GeoNames may
hold nothing under that name and any placement is an ancient-to-modern claim
requiring `identified` + `ground_citation`, not `stated`. It would put a pin in
Vietnam, not China.

**2. The Da Qin identifications — the highest-value geography item left.**
`Da Qin ≈ Rome`, `Haixi ≈ Egypt`, `Anxi ≈ Parthia`, `Tiaozhi ≈ Characene`,
`Angu ≈ Gerrha` are all *the translator's glosses*, and A4 refused every one of
them for want of a citation — including declining `pleiades:766` for Haixi
while using it for Egypt three records away, because there the Greek names
Αἴγυπτος outright and here the Chinese names 海西. Those refusals are correct
and they are also why the Weilüe and the Hou Hanshu draw nothing.

Cite a scholar for them (Hill; Leslie & Gardiner) and both records join the
network with edges to Rome and Egypt — **the two records most the point of this
project, currently invisible on its map.** That is worth doing properly, with
sources, and it is corpus curation rather than verification. It is the first
thing to consider after G1.

---

# A6 — the build-layer mutation guards (2026-08-13)

**One of three items `PHASE2_PLAN.md` assigns A6**, chosen first because it was
the smallest and best-specified: extend `ui/build_ui_data.py --verify` to audit
placements the way it already audits quote spans, then mutation-verify it.

## What the gap actually was

All three guards `PHASE2_PLAN.md` names — an authored coordinate, an
`identified` placement with no citation, a `pleiades_id` that never resolves —
were already true of the corpus, because `ingest/places.py` and
`ingest/gazetteer.py` already refuse all three at load time, and
`scripts/mutate_places.py` has mutation-verified those refusals since A1. The
gap was narrower than the checklist reads: **the build had never been shown, on
its own account, to refuse them too.**

Two of the three turned out to be free rides that had never been exercised:
`build_places()` calls `ingest.places.load_places()`, which already raises on
an authored coordinate and on an uncited `identified` placement — but nothing
caught that exception, so a bad record would have **crashed** the build with a
traceback rather than failing it cleanly. A crash is not a guard firing, by this
repository's own standing rule (`mutate_places.py`'s docstring, and the
`test_embed.py` incident it exists to prevent). The third — an id that never
resolves — was already a clean, reported failure (`places["uncached"]`, exit 2,
present since A4) but had genuinely never been mutation-tested.

## What was built

- **`check_placement_shape(p: Place) -> str | None`** and
  **`verify_placement_shape(by_doc) -> list[str]`** in `ui/build_ui_data.py`.
  Deliberately redundant with `ingest/places.py::parse_place` — re-checking the
  same two shape rules on the `Place` objects the build already has, rather
  than trusting that `parse_place` validated them. The reasoning is the same
  one `verify_spans` is built on: a rule enforced in exactly one place is a
  rule one edit away from being silently weakened, and until today only
  `ingest/places.py`'s copy of these two rules had ever been shown to fail.
  Wired into `build_places()`'s return as `shape_problems` and into `main()` as
  a third failure path, alongside `uncached`, both exiting 2 with the specific
  placements named.
- **`ui/test_build_ui_data.py`** — fixture tests in the exact `expect`/`ok`/
  `FAIL` idiom `ingest/test_places.py` and `scripts/test_recover_baseline.py`
  use, so `scripts/mutate_ui_places.py` can parse its FAIL lines the same way
  `mutate_places.py` parses `ingest.test_places`'s. Fixtures build `Place`
  objects directly rather than through `parse_place`, for the same reason
  `ingest/test_places.py` does when it needs to exercise a shape `parse_place`
  would never let through: these two defects cannot arrive any other way.
- **`scripts/mutate_ui_places.py`** — same structure as `mutate_places.py`
  (patch source, run the test module as a subprocess, confirm the named FAIL
  line, restore, confirm restoration), sized to the three guards this block
  owns rather than folded into the existing script, because `ui/build_ui_data.py`
  is not one of `mutate_places.py`'s two `SOURCES`.

## Verified

```
python ui/test_build_ui_data.py     all build-layer placement-shape assertions passed
python scripts/mutate_ui_places.py  3/3, sources restored
python -m ingest.verify             clean    ingest.gazetteer --check   clean
python -m ingest.test_places        ok       answer.test_translate     ok
python scripts/mutate_places.py     35/35    scripts/mutate_part7b.py  14/14
node ui/check_ui.mjs                20/20
python ui/build_ui_data.py          wrote ui/data.js (1025 KB), 0 shape_problems, 0 uncached
```

`ui/data.js` was rebuilt against these changes; nothing in it moved except its
`generated` timestamp — the new checks pass silently against a corpus that was
already clean, which is what they are supposed to do.

## Left for A6

The other two items `PHASE2_PLAN.md`'s Block A closing notes and the two A5
watch items assign here, neither touched by this session:

- **the date-overlap check** — motivating case on disk: the Ka'ba-ye Zartosht's
  `timePeriodsKeys` (`achaemenid-central-asia, modern`) omit the Roman era
  while the ŠKZ inscription it is tied to is 3rd-century;
- **the UNLOCATED-versus-no-entry distinction** — six UNLOCATED gazetteer ids
  (Cyeneum, Sabbatha, Chryse among them) currently surface identically to a
  place no gazetteer has heard of.

Also still explicitly not A6's job, per the note at the end of the previous
entry: Rinan's placement and the Da Qin/Haixi/Anxi identifications — corpus
curation, first thing to consider after G1 closes, not part of it.

---

# A6 — the date-overlap check, and UNLOCATED given its own state (2026-08-13)

Both remaining A6 items, in one session, and **the dump refresh found a defect
in the first of them** — see "The refresh ran" below, which is the part of this
entry worth reading.

```
python -m ingest.test_places        all pass (+44 assertions)
python scripts/mutate_places.py     43/43  (35 before, 8 new)
python ui/test_build_ui_data.py     ok     scripts/mutate_ui_places.py  3/3
python -m ingest.verify             clean  ingest.gazetteer --check     clean
node ui/check_ui.mjs                23/23  scripts/mutate_part7b.py     14/14
```

## Part 1 — the date-overlap check

### The comparison the check could NOT be

`PROGRESS.md` framed this as the record's date against the gazetteer entry's
attested range. That is not available: the seed records' `date` fields are
free prose written for a reader — *"compiled 5th century CE; records an event
of 166 CE"*, *"deposited soon after 205 CE (dendrochronology of shield
boards)"*. Parsing those into numeric ranges is guessing with a check's face
on, and **a check that matches too broadly names the wrong cause** is the
defect this repository has paid for five times.

`gazetteer.py` had already written down the right comparison, in the
`COLUMN_CANDIDATES` comment that asked for this guard in the first place: the
**project's own window, 27 BC to AD 1204**, which is a constant and needs no
parsing.

### The comment that asked for the guard was itself wrong

That same comment offered its motivating case: *"Mundus Ulterior covers 27 BC
to AD 1204; a findspot whose gazetteer entry is mediaeval-only is a
misidentification that resolves cleanly."* Written as a test, **Borgo
Medievale passes** — 640..1453 against −27..1204 overlaps by 564 years,
because this project runs to the Fourth Crusade. The example chosen to justify
the check would not have tripped it.

Found by using those exact numbers as the out-of-era fixture and watching the
assertion fail. The comment is corrected in place, and
`ingest/test_places.py::test_dates` now asserts **both** directions: a
post-mediaeval entry is refused, and a mediaeval one is explicitly in era.

> **Standing lesson added:** *an example written to motivate a guard is not
> the same as a case the guard catches, and only writing it as a test tells
> them apart.* The comment had sat in the file since A1, read several times,
> and its worked example was wrong about the project's own dates.

### `minDate`/`maxDate` are a hull, not an attestation — which is the real defect

The sharper finding, and it makes the ŠKZ case a different shape from the one
recorded at A2. Pleiades **derives** an entry's `minDate`/`maxDate` from the
periods it attests, so for an entry attested in disjoint periods the pair
spans the gaps too. The Ka'ba-ye Zartosht attests `achaemenid-central-asia`
and `modern`; the hull is −540..2100 and there is a **2,240-year hole** in the
middle, with the 3rd-century ŠKZ sitting squarely in it. The entry looks in
scope and attests nothing there.

So the hull answers only *could this be in scope*. Answering *is it* needs each
period's own range — which the cache did not hold, and which is where the one
design decision of this block sat. **Deriving it from the dump**, rather than
hand-listing the in-scope period keys: a row attesting **exactly one** period
states that period's range outright (`Adouli`, periods `roman`, −30..300, says
`roman = −30..300`). Thousands of such rows give the vocabulary with no
documentation involved — the same discipline as `map_columns`, *the parser is
written against data, not against documentation*. The alternative was a
vocabulary written from memory against a publisher's open-ended list, which is
what this module refuses for place ids one level up.

`--refresh-periods` caches it with full provenance. **Disagreement is never
resolved by picking a winner**: if two single-period rows give different ranges
for one key, the key is recorded as `ambiguous` with **no** range, and every
entry using it audits as `unknown`. A most-common-value rule was easy here and
would have made the check assert what the dump does not say.

### Three severities, because there are three different wrongs

| verdict | meaning | severity |
| --- | --- | --- |
| `outside` | the hull itself misses −27..1204 | **failure** — nothing it attests can be what is cited |
| `hole` | hull covers, every attested period falls outside | **note** — the Ka'ba case |
| `unknown` | vocabulary not derived, or the key was ambiguous | **note**, never folded into `ok` |

`hole` is a note and not a failure because the placement can be perfectly
correct: the ŠKZ really is carved on that monument, and what the finding means
is that Pleiades attests the building narrowly. Same reasoning as the
unrenderable-regional report. `unknown` is kept distinct on the rule that made
`resolve()` raise: **a check that cannot tell must say so.**

## Part 2 — UNLOCATED given its own state

### Why the id was in a note instead of the record

The state was invisible for a mechanical reason worth recording. `--check`
fails an entry resolving to neither point nor extent, so citing Pleiades 40186
Kyeneion — which resolves and carries **no coordinate** — would have failed the
build. The curator's only option was to drop the id and write it in prose. The
id therefore survived somewhere no check can read, and at the data layer
Kyeneion was indistinguishable from Ariake, which no gazetteer has ever heard
of.

**The third state again, one level below `no_places_reason`**, and it arrived
the same way: written in prose because the schema had nowhere to put it.

### `unlocated: true`

Written as `true` or omitted, on the same rule as `contested`. It **requires an
id**, because "the gazetteer holds this and cannot place it" is a claim about
an entry and without an id there is no entry to make it about.

And it is **verified, not trusted** — the cached entry must really carry
neither point nor extent. That is the whole value of moving it out of a note:
the day Pleiades locates Kyeneion, a stale `unlocated` fails loudly instead of
quietly continuing to draw nothing. Mutation-verified.

`Place` also gained **`drawable`** beside `locatable`, because those had become
two questions under one name: an `unlocated` placement has an id, must resolve,
must cache — and can never yield a coordinate. Collapsing them is exactly how
the two states came to look alike.

### Two records updated, one deliberately not

Cyeneum (`pleiades:40186`) and Sabbatha (`pleiades:906027`) each had a single
candidate id already determined and recorded in prose by the curator; both now
cite it. **Chryse does not**, and that is a decision rather than an omission:
its note names *two* unlocated candidates, `60485 Chryse/Aurea` and `50630
Chrysei`, and which one this is has never been settled. `unlocated` takes one
id, and recording either would settle by keystroke a question nobody has
settled by argument. Its note now says so.

## The refresh ran, and the check was wrong on the case it was built for

```
derived 99 period range(s) from pleiades-places-20260810.csv.gz (2026-08-10)
  42389 rows read, 14861 attesting exactly one period
  36 of 99 overlap this project's -27..1204
  0 ambiguous
placements: 89   locatable: 64   cached ids: 54
gazetteer holds the place but not its location: 2 (Cyeneum, Sabbatha)
Every placement resolves to a cached, dated gazetteer entry.
```

**The derivation method is sound, and the dump says so.** 14,861 single-period
rows produced 99 ranges and **zero** disagreements — the ambiguity guard, built
because a majority rule would have been a guess, turns out to have nothing to
guard against in this snapshot. That is the right order: the guard exists
because the method could have been unsound, and the run is what established
that it is not.

### The defect: a `hole` claimed on a vocabulary gap

The first real run reported the ŠKZ as a `hole` — and the note gave it away:

> every period it actually attests falls outside it: modern (1700..2100);
> **1 further period(s) have no derived range**

`achaemenid-central-asia` appears in **no single-period row of 42,389**, so it
has no derived range. Some Pleiades periods only ever co-occur, and that is a
**third cause** of "no range" beside "not derived yet" and "ambiguous" — one I
had not anticipated.

A `hole` is the positive claim that *nothing this entry attests is in era*, and
it cannot be made while a period is unaccounted for: **the missing period could
be the one in era.** The first version claimed it as soon as no *known* period
matched, which reported a gap in the derived vocabulary as a finding about the
gazetteer.

> **The over-broad check again, and this time I wrote it after writing the
> lesson down twice in this same file.** Sixth instance. It is worth naming
> what made it slip through: every one of the fixture tests passed, because
> each supplied a *complete* vocabulary. The partial-vocabulary case — the one
> the real dump actually produces — was not among them. **A fixture that is
> always complete cannot test what happens when the data is not.**

Now `unknown`, naming both halves: what is known to be out of era, and what
could not be checked. Mutation-verified (43 mutations, up from 42), with the
mutation restoring precisely the version that shipped.

The corpus is down from 59 `unknown` verdicts to **1** — the ŠKZ — and it is
the honest one. Resolving it needs a range for `achaemenid-central-asia`, which
this method cannot supply from a dump where it never appears alone. Bounding it
from multi-period rows was considered and does not work either: the Ka'ba row
constrains it to start at −540 and says nothing about where it ends, which is
exactly the fact in question.

## Verified, everything green

```
python -m ingest.verify              clean    ingest.gazetteer --check    clean
python -m ingest.test_places         ok       answer.test_translate       ok
python ui/test_build_ui_data.py      ok       scripts/mutate_ui_places.py 3/3
python scripts/mutate_places.py      43/43    scripts/mutate_part7b.py    14/14
python ui/build_ui_data.py           wrote ui/data.js (1027 KB)
node ui/check_ui.mjs                 23/23
```

The two `unlocated` ids are cached and Cyeneum and Sabbatha now render with
their own gap reason — *the gazetteer holds this place and does not record
where it is* — distinct from Ariake's *no gazetteer entry at all*, which was
the point of the block.

## What A6 has left

- **G1 criterion 4** — the only checklist item never asserted end to end. Its
  own starting-point section follows.
- The `hole` and `unknown` verdicts are computed and reported by `--check` but
  are **not carried into `ui/data.js`**, so the page cannot yet show that a
  point's dates do not corroborate the record citing it.

---

# G1 criterion 4 — starting point (for the next thread)

**Everything else on the G1 checklist is met.** This is the last item, and the
gate closes when it is done.

| criterion | state |
| --- | --- |
| 1. 24/24 considered, ≥17 with a named resolving id | ✅ 24/24, 18 named |
| 2. zero authored coordinates, mutation-verified | ✅ 43 mutations |
| 3. every `identified` cited; ≥1 contested renders as contested | ✅ Pattanam |
| 4. **map point → record → quotation → characters on disk, no dead link** | ✅ 6/24 chains, 8 mutations |
| 5. `check_ui.mjs` clean over all archived runs | ✅ 23/23 |

## What criterion 4 is, and why the existing checks do not cover it

`check_ui.mjs` already asserts every hop **separately**: 51 cached points are
drawn, 24 record panels build, 89 placements appear on their own record's
panel, every quotation in an answer is highlighted, and all 157 `resolved`
spans hold their quoted characters. All of it passes.

None of it asserts the hops **connect**. This repository has paid for that
distinction four times (`PROGRESS.md`'s standing lesson: *an assertion about
presence says nothing about correctness*), and most expensively when a map
plotted all 49 points correctly onto an inverted planet with 20/20 green.

So the work is one traversal that starts at a map marker and ends at characters
in a seed file on disk, asserting at each hop that the next one is reachable —
not that it exists somewhere.

## The finding that shapes the whole block

**The chain is complete for 6 of 24 documents.** Measured against the current
`ui/data.js`:

```
docs with a drawable map point : 18
docs with a resolved quotation :  8
docs with BOTH (full chain)    :  6
```

`drawn but never quoted` (12): africa-01-ezana-stone, africa-02-aksumite-coin,
arabia-01-periplus, arabia-02-palmyrene-tariff, arabia-03-jsnab17,
eastasia-03-hwangnam-glass, persia-01-skz, scandinavia-01-hoby-treasure,
scandinavia-02-gudme-hoard, scandinavia-04-illerup-adal,
seasia-01-oc-eo-medallion, seasia-02-oc-eo-site.

`quoted but not drawn` (2): **eastasia-01-weilue, eastasia-02-hou-hanshu** —
the Da Qin records, which draw nothing because A4 refused the translator's
uncited glosses. The two records most the point of this project are, again,
the two that cannot complete the chain.

**Decide what the criterion asserts before writing it.** Two readings:

1. *every chain that exists is unbroken* — 6 documents, and the count is
   reported so a shrinking number is visible;
2. *every record completes the chain* — unreachable, and would be satisfiable
   only by weakening what "quotation" means.

Reading 1 is the honest one and is what the wording ("no dead link") says. But
**6/24 must be printed, not hidden inside a pass**: a green check over six
records reads exactly like a green check over twenty-four, and that is the
`--survey`-on-substrings failure again. The `unrenderable` and `date_holes`
reports are the house pattern for this — count it, name it, do not fail on it.

## What it can rely on

- `ui/check_ui.mjs` already loads `data.js` into a sandbox and holds the
  render API: `renderPlaceProvenance`, `renderGroupProvenance`,
  `renderRecordProvenance`, `renderQuoteProvenance`, `buildMap`, `viewPlaces`.
  Nothing new needs building to reach any hop.
- The join between the two graphs is **`doc_id`**: `places.groups[].members[]`
  carries it on the map side, `runs[].grounding.quote_spans[]` on the answer
  side, and `corpus[doc_id].fields[source_field]` holds the characters.
- `span.resolution.state` is already computed (`resolved` / `case_only` /
  `moved` / `absent`). Only `resolved` and `case_only` are live links; `moved`
  and `absent` are the two known-broken archived citations and must be
  **excluded by name, with the reason**, not filtered silently.

## Traps, in the order they will be met

1. **`moved` and `absent` are real and pre-existing.** One of each, both in
   `africa-03-periplus-adulis`, both predating A5 and explained on the About
   tab. A chain check that counts them as dead links fails on a phenomenon the
   page already documents; one that drops them without saying so hides the
   only two genuinely broken citations in the archive.
2. **A group panel is not a record panel.** A marker resolves to a
   `places.groups[]` entry with N members; the chain passes through a *chosen*
   member. Assert every member is reachable, or the check passes on the first
   one and says nothing about the other three.
3. **`unlocated` and gap placements have no marker at all.** Cyeneum, Sabbatha
   and the 30 gaps are reachable from the record panel but never from the map.
   They are not dead links; they are places with no point, and the chain does
   not start there.
4. **Do not assert on presence in HTML strings.** `renderRecordProvenance`
   returns markup; checking that it *contains* a doc_id is the presence
   assertion this whole block exists to stop trusting. Assert reachability
   through the data the renderer was given.

## To run

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
python ui\build_ui_data.py
node ui\check_ui.mjs
python -m ingest.gazetteer --check
```

Everything is green at the start of this block. No dump is needed: the
gazetteer cache, the period vocabulary and `data.js` are all current as of
2026-08-13.

## And when the gate closes

The queue from Block A's closing notes, in the order those notes put it:

1. **The Da Qin identifications** — cite Hill, or Leslie & Gardiner, for
   `Da Qin ≈ Rome` and `Haixi ≈ Egypt`. The Weilüe and the Hou Hanshu join the
   network, and the two records that cannot complete criterion 4's chain today
   would be the ones it most rewards.
2. **Rinan** — needs `identified` + a `ground_citation`; puts a pin in Vietnam.
3. Carry the `hole` / `unknown` date verdicts into `data.js`, so the page can
   show what `--check` already knows.

Then **Block B**, which is a different kind of work: the W2a retrieval
baseline, and the first thing in Phase 2 that spends money.

---

# G1 criterion 4 — done, and the gate closes

`ui/check_chain.mjs` and `scripts/mutate_chain.mjs` are new. One traversal from
a drawn map marker to characters in a seed file on disk, and eight mutations
proving it can fail on the right hop.

```
node ui/check_chain.mjs        chain intact — no dead link   (8 assertions)
node scripts/mutate_chain.mjs  8/8 mutations caught by the assertion that owns the hop
```

The chain is complete for **6 of 24** records, exactly the count the starting
notes predicted, and the traversal makes **956 marker-to-disk paths** over
**104 distinct quotations** — a record reachable from three markers has three
chains through it, and each is walked on its own account.

## Two tautologies, one of them caught only by mutation

**This block's real finding is that I wrote two assertions that could not fail,
inside the file whose entire purpose is to stop trusting assertions that cannot
fail.** Seventh and eighth instances of the standing lesson, and the first time
one was caught by machinery rather than by re-reading.

The first I caught by inspection. It asserted that the four cohorts sum to 24 —
but `fullChain`, `drawnNotQuoted`, `quotedNotDrawn` and `neither` are
*constructed* as a partition of the same array, so the sum is 24 by
construction. It now asserts that every record counted as a complete chain was
actually walked end to end, which is computed two independent ways: cohort
membership from set intersection, `traversed` from the walk arriving at disk.

**The second I did not catch, and would not have.** Hop 3 asserted that a
quotation's run is "reachable from a run the page can open" —
`byQuestion.get(run.question).includes(run)`. The mutation that was supposed to
break it moved a run to an unlisted question, and `check_chain.mjs` passed.
`byQuestion` is built from `D.runs` and `QUESTIONS` from `byQuestion`, so every
run is reachable by construction and no mutation could ever have failed it. It
read like a real check and asserted nothing.

> **Within one self-consistent bundle, most "reachability" is derived and
> therefore tautological.** This is the sharpest form the standing lesson has
> taken. `data.js` is generated from a single build; asking whether one part of
> it can reach another usually asks whether the builder ran, which it did. The
> only genuinely falsifiable links are the ones that cross between structures
> the builder wrote *independently*, or that leave the bundle altogether.

## What replaced it, and why it is the better hop anyway

Reading `renderQuoteProvenance` to design the replacement turned up something
the starting notes had missed. The panel prints `rec.file` on screen under a
heading that reads **"the characters on disk"** — the page tells the user which
file the quotation came from.

My first draft found the seed file by scanning `data/seed_corpus` for a
matching `id`. So the page could have named one file while the check validated
another, and both would have been green. The traversal now travels *through*
`D.corpus[doc_id].file`: it opens the path the page displays, checks that file
holds the record it claims, and indexes the characters there. That is what makes
this one chain rather than two true facts side by side.

Three of the eight mutations exercise it: point the record at a different seed
file, point it at a path that is not on disk, and — the load-bearing pair —
edit the characters in the seed file itself while leaving `data.js` internally
consistent. If the last hop had quietly read the bundle, those two would have
stayed green.

## The `case_only` trap, found before it cost anything

All 166 live spans land on their characters on disk. The 9 `case_only` spans
match only case-insensitively, which is precisely what `case_only` names — a
hop-4 check comparing case-sensitively would have reported nine dead links that
are not dead. The leniency is scoped to that state alone, and mutation 7 proves
it: upper-casing a **`resolved`** span's characters on disk still fails.

## What is counted, not hidden

`moved` and `absent` are excluded **by name with the reason** — one of each,
both in `africa-03-periplus-adulis`, which is also one of the six complete
chains, so trap 1 landed on a chain member rather than off to the side.

The shortfall prints as four named cohorts, in the `unrenderable` / `date_holes`
house pattern:

- **6 full chain** — africa-03-periplus-adulis, scandinavia-03-vimose,
  southasia-01-akananuru-149, southasia-02-periplus-muziris,
  southasia-03-muziris-papyrus, southasia-04-pattanam
- **12 drawn, never quoted** — chain ends at the record
- **2 quoted, never drawn** — eastasia-01-weilue, eastasia-02-hou-hanshu
- **4 neither** — arabia-04-jabal-dabub, persia-02-silver-plate, persia-03-coin,
  seasia-03-khao-sam-kaeo

**That last cohort was not in the starting notes.** Those notes accounted for
6 + 12 + 2 = 20 of 24 and never named the remaining four. The accounting is now
exhaustive on screen, because a cohort nobody lists is a cohort nobody checks.

The check hard-fails on exactly one thing beside a broken link: a chain count of
zero. A traversal with nothing to traverse prints green while asserting nothing,
which is the failure the file exists to rule out.

It lives in its own file rather than inside `check_ui.mjs` for the reason the
starting notes gave — a green check over six records reads exactly like a green
check over twenty-four, and as line 24 of a 23-line report that is what it would
read like. Here the 6/24 is the only number on the page.

## Everything green

```
python -m ingest.verify          clean   ingest.gazetteer --check     clean
python -m ingest.test_places     ok      answer.test_translate        ok
python ui/test_build_ui_data.py  ok      scripts/mutate_ui_places.py  3/3
python scripts/mutate_places.py  43/43   scripts/mutate_part7b.py     14/14
python ui/build_ui_data.py       wrote ui/data.js (1027 KB)
node ui/check_ui.mjs             23/23
node ui/check_chain.mjs          chain intact — no dead link
node scripts/mutate_chain.mjs    8/8
```

**G1 is closed.** All five criteria met.

## Next, in the order Block A's closing notes put it

1. **The Da Qin identifications** — cite Hill, or Leslie & Gardiner, for
   `Da Qin ≈ Rome` and `Haixi ≈ Egypt`. This is now worth more than it was this
   morning: the Weilüe and the Hou Hanshu are the whole of the `quoted, never
   drawn` cohort, so giving them a marker moves the chain count from 6 to 8 and
   empties a cohort.
2. **Rinan** — needs `identified` + a `ground_citation`; puts a pin in Vietnam.
3. Carry the `hole` / `unknown` date verdicts into `data.js`, so the page can
   show what `--check` already knows.

Then **Block B**: the W2a retrieval baseline, and the first thing in Phase 2
that spends money.

---

# The Da Qin block — what the sources actually support

Started as queue item 1 ("cite Hill, or Leslie & Gardiner, for `Da Qin ≈ Rome`
and `Haixi ≈ Egypt`"). **Both halves of that sentence turned out to be wrong,
and finding out why is the whole value of the block so far.** No placement has
been written yet; what follows is the reasoning that has to be settled first,
recorded now because it took three passes to reach and should not be re-derived.

## 1. The schema cannot express a disputed *referent*

`contested` is legal only on `ground: identified`; `identified` requires exactly
one `gazetteer_id`. So `contested: true` means **"this place is at THAT
location, and scholars dispute it"** — Pattanam's shape, where the coordinate is
certain (it is the excavation site) and only the label *Muziris* is argued over.

Da Qin, Haixi and Angu are the other kind. There is no certain coordinate, and
the dispute is over **which region the name denotes**. Any single id we wrote
would take a side in the very dispute the flag exists to declare:

| name | competing referents in the literature |
| --- | --- |
| Da Qin 大秦 | the whole Roman Empire / the Roman East / Syria specifically |
| Haixi 海西 | Egypt (Hirth 1885; Hill 2004, 2015; Paolillo 2024) vs the Italic peninsula or Rome itself (Leslie & Gardiner 1996, 263–4; Yu Taishan 2013, 40 n.68) |
| Angu 安穀 | Orchoë (Hirth 1885, 187) / Gerrha (Hill 2004) / Antioch-Charax (Leslie & Gardiner 1996, 67) |

> **This is the third state again, at the identification layer.** `unlocated`
> and `no_places_reason` were each split out because a real state had nowhere
> to live in the schema and survived only in free-text `note`. That is exactly
> where these three candidate-sets live today. **Open question, deliberately not
> answered in this block:** whether to add a shape that holds N candidate
> identifications, each with its own id and citation, none asserted as the
> answer. It would touch `places.py`, the build, the UI and the mutation suite,
> and it would probably retire four of the five Weilüe notes.

## 2. Haixi does not survive contact with the primary text

The plan after finding (1) was to sidestep Da Qin and place Haixi instead —
`pleiades:766 Aegyptus` is already cached, so it needed no dump. Reading
Paolillo 2024 in full killed it.

**In the Weilüe, 海西 is an epithet of Da Qin, not a separate country:**
其國在海西。故俗謂之海西 — "This kingdom is located west of the sea: for this
reason, it is popularly called Haixi." The Hou Hanshu says it twice more:
海西即大秦也 (juan 86) and 大秦國一名犁鞬，以在海西，亦云海西國 (juan 88).
Paolillo reads the Weilüe as indicating "that Haixi is a part of Da Qin".

Pinning Haixi to Egypt while leaving Da Qin regional would assert a separation
the text collapses — and would put a pin in Egypt for a name the record uses to
mean the Roman Empire. Paolillo's own support is explicitly tentative ("it is
not far-fetched to identify…", "a place that we may – tentatively – identify
with Egypt").

**And the two translators disagree about the structure of the passage itself.**
Hill separates them — you cross the Mediterranean from Haixi "to reach that
country (Da Qin = Rome)" — while Paolillo has Haixi inside Da Qin. That is not
a dispute a `gazetteer_id` can hold.

> The lesson generalises past this record: **an identification can be
> well-cited and still unplaceable, because the citation settles the gloss and
> not the referent.** Queue item 1 was written as a citation-hunting task. It
> was never one.

## 3. What Paolillo 2024 *does* license

The same paper answers A4's stated objection to a different placement. On p. 30:

> "Tiaozhi, on the other hand, appears to correspond with the territory of
> Characene/Mesene in southern Mesopotamia or its political centre Charax
> Spasinou"

A4's note on Tiaozhi already names the id and the reason for refusing it:
*"Pleiades 912905 'Mesene/Characene' 31.468/47.344 was examined and is not used
… it is the gloss's identification and no citation supports it here."* **That
objection is now met, and only that one.** Territory-to-territory, no
city-standing-for-empire problem, no epithet problem.

Anxi ≈ Parthia is citable from the same paper but is NOT the same case: A4
refused `pleiades:952097` for a second reason — it is *Parthyene*, a region
rather than the empire — which is the Da Qin objection wearing a different hat,
and a citation for "Anxi = Parthia" does not answer it.

**Chosen: Tiaozhi alone.** It takes the chain from 6/24 to 7/24 and is the only
one of the five whose sole stated objection has actually been removed.

The citation is good in the way this project cares about: Maurizio Paolillo,
"Following a Mediterranean Clue. A Reconsideration of the Sources About the
Country of Haixi 海西國 (2nd–3rd Cent. CE)", in R. Vinci (ed.), *Navigating the
Mediterranean Through the Chinese Lens*, Firenze University Press 2024, 25–37 —
peer-reviewed, open access under CC BY 4.0, DOI 10.36253/979-12-215-0598-6.04.

## 4. A corpus-integrity finding, unrelated to placement

`eastasia-01-weilue`'s `original_text_excerpt` does not match the published
text. Ours reads:

    從安谷城乘船直渡海，海西人名之海西

Paolillo, quoting the Sanguozhi (Chen Shou 1975), has:

    從安息界安穀城乘船。直截海西。… 其國在海西。故俗謂之海西。

Beyond the marked elisions and the 谷/穀 variant: `直渡海` where the source has
`直截海西`, and **`海西人名之海西` corresponds to nothing in the source** — it
looks like a corruption of 其國在海西故俗謂之海西.

**No chain is broken today** — all 62 spans on the two Da Qin records target
`reference_translation`, and the English matches Hill verbatim. But this is the
record the AI Technology Showcase brief names as the hero demo *for Classical
Chinese retrieval*, and the field is the one criterion 4's chain indexes
characters into. A cross-lingual demo standing on a corrupted source text is the
same class of defect as a stale bundle: everything downstream is green and the
thing itself is wrong.

**Deliberately not fixed here.** Correcting a primary-source transcription from
a secondary work's quotation would itself be an unsourced edit — the exact move
A4 refused when it declined the translator's glosses. It needs a print edition
(Chen Shou 1975, *Sanguozhi*, Beijing: Zhonghua shuju) or a stable digital
facsimile. zh.wikisource, which the record cites as `citation_original`,
returned nothing fetchable.

## 5. Blocked on

`pleiades:912905` is **not cached**, and neither is `952097` or `423025`. The
Pleiades dump is gitignored and absent, and pleiades.stoa.org now sits behind an
anti-bot challenge, so the id cannot be resolved from the web either. Needs
`pleiades-places-<date>.csv.gz` on disk, then the project's own
`--refresh` / `--find` route as in A5 and A6.

Rinan is blocked the same way, and may not be in Pleiades at all — a Han
commandery in central Vietnam is outside a Greco-Roman gazetteer's scope, which
would put it with Gyeongju and Óc Eo in the GeoNames backlog rather than in this
block.

## The dump arrived, and Tiaozhi is placed — 7/24

The 2026-08-10 CSVs are the right ones and were verified before use: places
**42,389 rows** over 26 columns, which is the identical count A6 recorded when
it derived the period vocabulary, so the cache stays single-dated. A third file,
`pleiades-places-20260813.json.gz`, was the JSON-LD export at 135 MB — the wrong
format, and mixing its newer snapshot in would have produced a cache whose
entries came from two different days. Not used.

### The lookup found a near miss worth recording

```
912905  Mesene/Characene/Shad Bahman/Maisan   31.468,47.344  precise -30..640
897810  Mesene                                            —  unlocated -30..300
```

**Two entries titled Mesene.** 897810 is a settlement near Ctesiphon whose
"location has not been determined" and which carries no coordinate at all. A4's
note recorded 31.468/47.344, which is 912905 — so the right one was already
identified — but nothing in the corpus would have caught the substitution if the
id had been transcribed wrong, because both resolve and only one has a point.
`--find` printing both, with its own standing warning that *a name match is not
an identification*, is what made the distinction visible.

### Written as `identified`, deliberately NOT `contested`

`ground_citation` is Paolillo 2024, p. 30, quoted verbatim in the field. The
scholarship varies over the **extent** rather than the **referent** — Hill
glosses "Characene and Susiana", Paolillo has Characene/Mesene "or its political
centre Charax Spasinou" — and marking that contested would dilute a flag that
currently means a genuine two-sided dispute about *which place is meant*.
Criterion 3 depends on that flag meaning something.

### Rinan: nothing, which is a result

```
searching pleiades-places-20260810.csv.gz for 'Rinan'  -> no match
searching for 'Nhat Nam'                               -> no match
```

`--find`'s own message is the correct reading: *"That is a RESULT, not a
failure… Do not reach for a nearby place."* Rinan stays `regional` — a Han
commandery in central Vietnam is outside a Greco-Roman gazetteer's scope, which
is the project's premise appearing in its own gate for the sixth time.

It does **not** join "the GeoNames backlog" as that list stood in Block A: A5's
GeoNames reader was built and Gyeongju (`geonames:1841603`) and Óc Eo
(`geonames:13405688`) are cached and drawn. What is still unplaced is
`seasia-03-khao-sam-kaeo` and `arabia-04-jabal-dabub`, plus `persia-02-silver-plate`;
`persia-03-coin` carries an honest `no_places_reason` and is not a gap.
Rinan is a harder case than any of them, because it is an **ancient
administrative region** with no single modern settlement standing for it — the
gazetteer that would hold it is neither Pleiades nor GeoNames.

Cattigara *does* resolve, at 10.255/105.152 in the Mekong delta near Óc Eo — and
is dated **1700..2100 modern**, the same shape as the "Parthian empire" entry A4
refused. A modern scholarly label is not an ancient place. Not used, and not
Rinan in any case.

### Result

```
python -m ingest.gazetteer --refresh   53 of 53 ids looked up
python -m ingest.gazetteer --check     Every placement resolves to a cached, dated entry
python ui/build_ui_data.py             wrote ui/data.js (1030 KB)
node ui/check_ui.mjs                   all checks passed
node ui/check_chain.mjs                chain intact — no dead link
node scripts/mutate_chain.mjs          8/8
python scripts/mutate_places.py        43/43   mutate_ui_places.py  3/3
python scripts/mutate_part7b.py        14/14   ingest.verify        clean
```

**The chain is 6/24 → 7/24.** `eastasia-01-weilue` joins africa-03-periplus-adulis,
scandinavia-03-vimose, southasia-01-akananuru-149, southasia-02-periplus-muziris,
southasia-03-muziris-papyrus and southasia-04-pattanam. 52 markers now, 60
members, 996 marker-to-disk paths over 144 distinct quotations.

`quoted, never drawn` is down from 2 to **1** — eastasia-02-hou-hanshu, held
there by Rinan alone. **Both Da Qin records were supposed to be the payoff of
this block; one of them was, and the other is blocked on the gazetteer rather
than on the argument.** That is a better place for it to be stuck.

### Still open, in order

1. **The Weilüe's `original_text_excerpt` is corrupt** (§4 above) — needs a
   print edition or stable facsimile, not a fix derived from a secondary
   quotation.
2. **The candidate-identification schema gap** (§1 above) — would retire four of
   the five Weilüe notes and is the only route by which Da Qin, Haixi and Angu
   ever become placeable.
3. **Rinan**, with the GeoNames backlog it now belongs to.
4. Carry the `hole` / `unknown` date verdicts into `data.js`.

---

# The date verdicts reach the screen — A6's last leftover, closed

`--check` has computed `hole` and `unknown` since A6 and the bundle never
carried them, so **for one release the page could not say that a point's dates
fail to corroborate the record citing it.** On screen, a marker whose gazetteer
entry attests nothing in this era looked exactly like one attesting the right
century. Three layers changed:

| layer | change |
| --- | --- |
| `ui/build_ui_data.py` | `_resolved_geometry` now carries `date_verdict` + `date_detail`, computed by calling `gz.date_audit` — not reimplemented |
| `ui/index.html` | `dateVerdictBox()`, rendered on both the placement and the group panel |
| `ui/check_ui.mjs` | two new assertions, and `scripts/mutate_ui_dates.mjs` proving both can fail |

```
verdict tally across all 89 placements: {"ok":60,"(not resolved)":24,"no_dates":4,"unknown":1}
```

The one `unknown` is the ŠKZ, and it is the honest one A6 identified: its
`achaemenid-central-asia` period appears in no single-period row of the
2026-08-10 dump, so it has no derived range, and a period with no range could be
the one in era.

## Calling `date_audit` rather than porting it

The verdict is computed in the builder by importing the function `--check`
uses, against ranges read from the same cache. **Two implementations of one rule
is the defect this repository keeps paying for** — `--find` vs `--survey`
disagreeing on numeric ids, `translation_chunk` vs `translation_chunk_id` — and
a JS port in `index.html` would have been a third instance, with the added
charm that it would drift silently because nothing compares them.

Where `ranges` is unavailable the verdict is `None`, never a silent `ok`: the
same rule `date_audit` already applies one level down.

## Scoping the mutations, and one thing not guarded

`scripts/mutate_ui_dates.mjs` is deliberately three cases, not thirteen.
`date_audit` — which decides the verdict, and where the hole/unknown boundary
sits — is **already** mutation-verified by `mutate_places.py`, three of whose 43
cases target that function directly. Repeating them would have proved nothing
twice. What was new is the two hops after the verdict is decided: the builder
carrying it, and the renderer surfacing it. Both are now covered, including the
regression of suppressing the box entirely, which is precisely the state the
page was in before this block.

> **Named honestly: a builder that wrote `ok` everywhere would pass both new
> checks.** Neither assertion can tell a correct verdict from a uniformly
> optimistic one, because the only way to check that in `check_ui.mjs` would be
> to reimplement `date_audit` in JS — the very thing rejected above, and it
> would be tautological against itself anyway. What actually guards it is that
> the builder calls the audited function, and that function is mutation-verified
> where it lives. Worth stating plainly rather than leaving the coverage story
> to look better than it is.

The assertion matches on `data-date-verdict`, an attribute the renderer emits
for the purpose, rather than on the prose beside it — the sentence will be
reworded and the claim will not.

## Everything green

```
ingest.verify            clean    ingest.gazetteer --check   clean
ingest.test_places       ok       answer.test_translate      ok
ui/test_build_ui_data.py ok       ui/build_ui_data.py        wrote ui/data.js (1035 KB)
mutate_places.py         43/43    mutate_ui_places.py        3/3
mutate_part7b.py         14/14    mutate_chain.mjs           8/8
check_ui.mjs             all passed (25 assertions)
check_chain.mjs          chain intact — 7/24
mutate_ui_dates.mjs      3/3
```

**Block A's queue is now empty.** What remains is the two items that need
something outside the repository — a print Sanguozhi for the Weilüe excerpt, a
GeoNames dump for Khao Sam Kaeo and Jabal Ḏabūb — and the candidate-identification
schema, which is a design block of its own. Next substantive work is **Block B**:
the W2a retrieval baseline, and the first thing in Phase 2 that spends money.

---

# Phase 2 — Block B1: the ranking gold set, and the denominator that moved

**B1 is done and B2's code is written; neither has spent anything.** 32 pairs in
`eval/gold/ranking_pairs.json`, `eval/run_ranking_check.py` ready to run, 30
offline assertions and 13 mutations green. What follows is mostly what the block
found on the way, because two of the findings change what B2 measures.

## 1. The runbook's "richest seam" is the thinnest one

`PHASE2_PLAN.md` B1 names `eval/answer_runs/` — "61 archived answers, 139
citations" — as the richest source of ranking pairs. The archive is now 77 runs,
and it holds **six distinct questions**:

```
16  What did Rome trade with the Kingdom of Aksum?
15  What did ships carry from Muziris?
15  How did Chinese sources describe the Roman empire?
15  What do the Vimose runes say?
15  When was the Antikythera mechanism built?
 1  What was exported from Adulis?
```

One of those six is the off-corpus refusal case and has no known-good passage at
all. The other five yield **8 distinct (question, quoted-chunk) pairs** between
them. Against a floor of 20, the seam the plan calls richest supplies a quarter
of the set.

That is not a defect in the archive — 77 runs of six questions is exactly what a
sweep of six questions repeated for stability produces, and Part 8 was right to
repeat them. It is a defect in the plan's estimate, and it inverts the block's
shape: the composition is now 8 archived, 11 from `retrieval_probes.json`, 4
from `translation_cases.json`, and **9 written here** for documents no Phase 1
query reaches at all.

> **Those 9 are mine, not yours.** They carry `provenance: "authored"` and each
> note says so. Action #5's principle — *a gold set someone else's judgement
> wrote is not a gold set you can be surprised by* — is about the W4 cases, but
> it applies here the moment a query decides what counts as correct retrieval.
> Read them before B2 records anything; rewriting one is a one-line diff, and
> rewriting one after the baseline is recorded costs the baseline.

## 2. The corpus is 57 chunks and the index is 54 — HALF WRONG, see the correction below

Action #1 — reconcile the corpus counts — was completed on 2026-08-12 and
recorded **24 docs / 56 chunks / 54 eligible / 54 embedded**. That reconciliation
was correct, and it was invalidated the next day by this project's own work.

Loading `data/seed_corpus/` as it stands today gives **24 docs / 59 chunks / 57
eligible**. Loading it at commit `9470506` gives 56 / 54 exactly — so the
chunker is faithful and the corpus genuinely moved. One document accounts for
all of it:

```
africa-03-periplus-adulis    9 chunks -> 12
```

A4's Wikisource recovery of Periplus §4–6 replaced the Greek with the fuller
published text; §6 alone now splits into three chunks where it was one. The
English translations are byte-identical, and every `original::` chunk of that
document has different text under the same id.

**Nothing downstream noticed, because nothing downstream compares them.**
`--check`, `check_ui.mjs` and `check_chain.mjs` are all green: they assert the
bundle is internally consistent, and it is. The bundle was built from disk. The
*index* is what stayed at 54, and no check in the repository looks at both.

> This is *a result is comparable only within the thing that produced it*, sixth
> appearance, and the first time it has bitten the denominator the whole of W2b
> is denominated in. **The W2b curve is 54 → 150 → 450. The 54 does not exist.**

`run_ranking_check.py` therefore refuses to run against an index that does not
match the corpus on disk, and says which command fixes it. The reconciliation is
machinery now rather than something remembered once a phase.

## 3. Chunk ids are not a stable name for a passage — proven twice

The plan's B1 wording is "question → the chunk a citation *resolved to on disk*",
which reads as: key the pair on `chunk_id`. Two independent findings say it
cannot be.

**First, ids move.** The Greek sentence the Adulis answer quotes —
`Φέρεται δὲ ἀπὸ τῶν τόπων ἐλέφας καὶ χελώνη καὶ ῥινόκερως` — is recorded in the
archived run at `africa-03-periplus-adulis::original::002`. It now lives in
`::original::005`. Both ids exist. A pair keyed on `::002` would resolve, rank,
and report a number about §5's obsidian.

**Second, the ids in the archive already do not name the chunk holding the
characters.** Two archived Adulis spans name `translation::000` and
`translation::004` for text that lives in `translation::002` and
`translation::005` — the *first member of the merged section*, not the member
holding the quotation. That is the carried W2 debt (`translation_chunk_id` names
the retrieved member, `translation_chunk` the merged section) showing up in the
data, and it is visible only on Adulis because Adulis is the one document whose
translation sections split across several chunks.

So a pair asserts `expect_doc` **and** `expect_text_contains`, never an id. The
precedent is in this repository already: `expect_text_contains` was added to
`retrieval_probes.json` in Part 6 for the same reason — *a probe that asserts
only the document id can pass against the wrong passage*.

`observed_chunk_id` is recorded on the 8 archived pairs as provenance. It is
never asserted on and never used to select a chunk; the run reports how many
have drifted, in the `unrenderable` / `date_holes` house pattern — count it,
name it, do not fail on it. One has drifted today.

## 4. Where the known-good passage is resolved from, and why it matters

`run_ranking_check.py` resolves each pair's target **by searching the index**,
not the seed files. The metric is a claim about what retrieval can reach; if the
target were resolved from disk, the check would happily rank a passage the index
does not hold, or hold differently. Zero matches and more-than-one matches are
both reported as unmeasurable rather than guessed at — a recall over an
ambiguous target is a number about nothing.

`eval/test_ranking_check.py` runs the same resolution rule against disk, offline,
so a pair that has rotted is caught in a session that costs nothing rather than
in the session that spends the batched request. That check caught **7 of the 32
pairs** on first write: four whose characters appeared in two chunks at once,
three whose snippet was off by a word.

## 5. Two gaps, because one number cannot say which failure happened

B2 asks for "known-good chunk minus *highest-ranked irrelevant* chunk". The word
irrelevant hides a choice, so both readings are computed and printed:

- `gapDoc` — against the best hit from **any other document**
- `gapAny` — against the best other hit of **any kind**, siblings included

A sibling section of the right document outranking the target is a chunking
result. A Scandinavian find outranking it is a retrieval result. They need
different responses in W2c and one number cannot tell them apart.

`top1_to_rank6` is reported alongside, because it is the **only** quantity here
with a Phase 1 prior to be compared against (mean spread 0.105 overall;
0.045–0.094 on the questions that matter). Everything else is new, which is what
makes it a baseline rather than a comparison.

## 6. Two tautologies, both caught by the mutation harness

`scripts/mutate_ranking.py` was written after `eval/test_ranking_check.py` and
immediately found two assertions that could not fail — the eighth and ninth
instances of the standing lesson, and the second time in three blocks that
machinery caught it rather than re-reading.

1. **"gap vs other DOC skips same-document siblings"** was checked against a
   stub ranking in which no sibling outranked the target. With that data the two
   gaps take the same value by construction, so collapsing them in the source
   changed nothing the assertion could see. The stub now puts a sibling on top.
2. **"a gold set below twenty pairs is rejected"** was checked by trimming the
   file to its first ten pairs — which also drops three regions, so the variant
   kept failing on the *region* rule with the twenty-pair floor removed. It now
   trims to one pair per region, seven pairs spanning all seven regions, so the
   floor is the only rule that can reject it.

Both are the same shape: **a negative test must fail for the reason it names, and
the only way to know it does is to remove that reason and watch it pass.**

## What is green

```
python -m eval.test_ranking_check     30 assertions, 0 failed
python scripts/mutate_ranking.py      13/13 mutations, sources restored
python -m ingest.test_chunker         ok
python -m ingest.test_places          ok
python ui/test_build_ui_data.py       ok
eval/goldset.py                       11 probes, 12 translation cases,
                                      5 answer cases, 32 ranking pairs
```

The gold set: **32 pairs, 7 regions, 8 target languages** (grc 12, en 9, lzh 4,
oty 2, xpr 2, gmq-pro 1, xna 1, xsa 1), **20 of 24 documents**. The four not
covered are `arabia-02-palmyrene-tariff` and the other held-back record, plus
`persia-03-coin` and `seasia-02-oc-eo-site`.

## To run B2 — on the host, in this order

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
docker compose up -d db

python -m eval.test_ranking_check     # free; do this first
python scripts\mutate_ranking.py      # free

python -m ingest.run_ingest           # 24 docs / 59 chunks / 57 eligible
python -m ingest.run_embed            # already current; expect "nothing to embed"
python -m ingest.run_embed --stats    # eligible 57, embedded 57, pending 0

python -m eval.run_ranking_check      # ONE batched embedding request
```

`run_ranking_check` will refuse to start until the ingest and embed steps have
run, and the refusal names them. Paste the cohort table into this file **this
session**, before any hardening idea is tried — `PHASE2.md` names the temptation
to skip backwards and `PHASE2_PLAN.md` B2 makes it your action.

## Open, in order

1. **Rule on the 9 `authored` pairs** before B2 spends. Finding 1.
2. **Re-ingest and re-embed.** Finding 2. Until then no ranking number means
   anything, and the W2b denominator is 57, not 54.
3. **B3 distractors** — the shortlist is a separate document and needs your
   ruling on each seam before anything is fetched.
4. Carried: `cite.py`'s `case_folded` state and the `translation_chunk_id`
   rename are Block C's C1, and finding 3 is the second piece of evidence for
   the second of them.

---

# Correction to Block B1 finding 2 — the index was never stale

Ran on the host, 2026-08-13, immediately after the Block B1 notes above:

```
python -m ingest.run_ingest    documents 24 / chunks 59 / pruned 0
                               awaiting_embedding: 0
python -m ingest.run_embed     nothing to embed — every eligible chunk
                               already has a vector
                               eligible 57, embedded 57, pending 0,
                               by_model {voyage/voyage-3.5: 57}
```

**Predicted six chunks pending. Got zero.** The prediction was not off by a
count; it was about a state that did not exist.

## What was right and what was wrong

**Right:** the corpus is 57 eligible chunks, not 54. `PHASE2_PLAN.md` Action #1
records "the W2b denominator of 54 stands" and `PROGRESS.md`'s Block 0 entry
records 54 embedded, and **both of those numbers are stale on the page**. The
W2b rungs are 57 → 150 → 450. A baseline recorded against a denominator read out
of either document would have been denominated wrongly.

**Wrong:** the claim that the *index* had diverged from the corpus. It had not.
A4 re-ingested and re-embedded when it recovered the Greek, and said so —
`PROGRESS.md`, A4's closing lines:

> Block A has spent one batched embedding request in total — for the twelve
> chunks the Greek recovery invalidated.

Twelve is exactly right, and I can now reproduce it: nine chunks whose text
changed under an existing id (three each in `africa-03-periplus-adulis`,
`arabia-01-periplus`, and two in `southasia-02-periplus-muziris` plus one in
`southasia-03-muziris-papyrus`) and three new Adulis ids. `UPSERT_CHUNK` nulls
all four embedding columns on a text change, `run_embed` picked up all twelve,
and the index has been current since.

## How the error was made, which is the part worth keeping

I never had database access — this session ran in the cloud, and the host's
Postgres is not reachable from it. So the index state was not measured. It was
**inferred from a line in `PROGRESS.md` dated 2026-08-12**, compared against a
corpus loaded from disk today, and the difference was reported as a divergence
between two live things.

> **That is the standing lesson, committed by the session that was writing the
> standing lesson down.** Finding 2 above argues that *a result is comparable
> only within the thing that produced it* — and reaches that conclusion by
> comparing a number recorded on one date against a state observed on another,
> which is the same move. Seventh appearance, and the first one that is mine.

Two specific mistakes underneath it, both of the same shape — measuring the
easy thing and reporting it as the thing that mattered:

1. **Chunk *count* was used as a proxy for chunk *text*.** The diff against
   commit `9470506` was computed on counts per document, so only Adulis showed —
   it was the only document whose chunk count moved. The other three Periplus
   records had text replaced under unchanged ids and were invisible to that
   diff. Hence "six" instead of twelve. A count is a proxy; the characters are
   the thing, which is the same argument this block makes for the gold pairs and
   I failed to apply to my own measurement one screen earlier.
2. **`PROGRESS.md` was searched, not read.** It was grepped for `W2a`,
   `Block B` and `Phase 2`, and the A4 line naming the embedding spend was three
   hundred lines from any of those terms. A grep answers the question asked; it
   does not tell you the question was wrong.

## What this does and does not change

- **`eval/gold/ranking_pairs.json` is unaffected.** The pairs were resolved
  against the corpus on disk, which was and is correct, and all 32 resolve.
- **`check_index_is_current` is unaffected and worth keeping.** It did not fire
  because there was nothing to fire on. A guard that stays quiet on a healthy
  system is doing its job; the reason to keep it is that A4's re-embed was a
  thing someone remembered to do, and this makes it a thing that cannot be
  forgotten.
- **B2 is unblocked and was never blocked by this.** The only remaining
  precondition is the ruling on the nine `authored` pairs.
- **`PHASE2_PLAN.md` Action #1 should be amended at source** to read 57, in the
  same way its worked example's wrong Adulis id was flagged for correction at
  source in Block A. A completed action whose recorded result has since moved is
  worse than an open one, because nothing prompts anyone to re-read it.

---

# Block B1 addendum — the nine authored queries, ruled on

The nine `authored` pairs went to the project owner, and measuring them first
turned up something the walkthrough was not looking for.

## The measurement

Share of a query's content words appearing verbatim in its own target chunk:

```
archived_answer    n= 8   0.00
retrieval_probe    n=11   0.09
translation_case   n= 4   0.04
authored           n= 9   0.38   <- written by reading the target
```

Four scored 0.50–0.86. `au-shapur-plate` was the target's opening clause
reworded — *"a Sasanian gilded silver plate showing a king hunting"* against
*"Gilded silver plate showing a king hunting"*. That is a keyword match wearing
a retrieval test's clothes.

**One caveat in my favour, stated anyway:** the other cohorts mostly target
non-English chunks, where overlap with an English query is zero by construction
rather than by discipline. All nine English-target pairs are mine, so the
cross-cohort comparison is partly an artefact. The absolute figures stand alone.

## A second defect the first one hid

Two pairs pointed at the wrong chunk. For records holding both an `original::`
catalogue legend and a `translation::` description, I had anchored on a
distinctive string that happened to sit in the legend:

- `au-hoby-silver` asked about cups in a chieftain's grave but targeted the
  signature line alone; the chieftain and Cheirisophos are in the description.
- `au-oc-eo-medallion` asked about a gold imitation of a coin of Antoninus Pius
  but targeted the legend, millimetres and inventory number.

Retrieval returning the passage that answers would have been scored a miss. Both
re-anchored to `translation::000`.

## Where it went wrong, and the rule that came out of it

Re-anchoring **raised** those two pairs' overlap — 0.25 → 0.62 and 0.11 → 0.56 —
because the passage that answers a question is the passage sharing its
vocabulary. Chasing the number further produced worse pairs, not better ones:

- *"How did Sasanian rulers present themselves in art?"* scores 0.00 and is
  answered just as well by `persia-03-coin`, a bust of Shapur I.
- *"How much Roman coinage ended up in southern Scandinavia?"* scores 0.00 and
  is answered just as well by `illerup-adal`'s 194 denarii.
- *"What Roman-period imports turn up at Indian west-coast excavations?"* scores
  0.13 and is answered by the Periplus §56 import list.

All three traded a real defect for a worse one. **An ambiguous pair scores
CORRECT retrieval as a failure**, and no later run can tell that apart from a
ranking problem.

> **Unambiguity beats overlap, and overlap is a property to record rather than a
> target to minimise.** For a 300-character English object description, a
> faithful and unambiguous question necessarily shares vocabulary with it. This
> is the optimise-the-proxy failure — the same shape as `expect_cited_docs`
> proving a source was *named* rather than *used* — committed while fixing an
> instance of it, and caught only because the rival documents were checked
> before the rewrite was committed.

## What was actually changed

| pair | change | overlap |
| --- | --- | --- |
| `au-shapur-plate` | → "a royal hunt scene on Sasanian metalwork" | 0.86 → 0.00 |
| `au-silla-glass` | → "How did Mediterranean glassware reach Korea?" | 0.50 → 0.00 |
| `au-khao-sam-kaeo` | → "engraved gemstones of Mediterranean workmanship found in Southeast Asia" | 0.50 → 0.00 |
| `au-gudme-hoard` | → "What accompanied the bracteate treasure found on Funen?" | 0.50 → 0.20 |
| `au-pattanam-finds` | kept — the lower-overlap rewrite was ambiguous against the Periplus | 0.33 |
| `au-hoby-silver` | re-anchored to the description | 0.25 → 0.62 |
| `au-oc-eo-medallion` | re-anchored to the description | 0.11 → 0.56 |

`query_target_overlap` is now computed per pair and carried into every archived
run and the printed table (`lexOv`), so the authored cohort's recall is read next
to the reason it may be high. It is **not** a gate: gating on it would be the
same mistake one layer up.

Final: **32 pairs, all resolving to exactly one chunk of the expected document.**
Cohort overlap 0.00 / 0.14 / 0.04 / 0.23 (four probe queries are n/a, being
non-Latin). 30 offline assertions and 13 mutations green.

**Every precondition for B2 is now met.**

---

# Phase 2 — Block B2: the W2a baseline, recorded 2026-08-14

```
ranking check  20260814T074614+0000  view=retrievable_chunks  index=57 chunks
               models=['voyage/voyage-3.5']   32 queries embedded in 1 request

cohort              pairs  recall@6   MRR@10  gapDoc  gapAny  spread  lexOv
archived_answer          8  0.500 ( 4)  0.123  -0.075  -0.086   0.091   0.00
authored                 9  0.889 ( 8)  0.844   0.057   0.047   0.136   0.23
retrieval_probe         11  1.000 (11)  1.000   0.114   0.090   0.178   0.14
translation_case         4  0.750 ( 3)  0.312   0.022  -0.142   0.190   0.04
ALL                     32  0.812 (26)  0.651   0.051   0.014   0.146   0.12
```

Archived at `eval/ranking_runs/20260814T074614+0000-retrievable_chunks.json`.
Nothing has been tuned. **This is the number the hardening is measured against.**

## The prediction was backwards, and that is the finding

The B1 notes warned that the `archived_answer` cohort's recall would be "partly
true by construction" because those pairs name chunks retrieval itself returned,
and that the probe and translation cohorts were "the ones that can actually
surprise". The cohort predicted to be inflated came in **worst at 0.500**; the
cohorts predicted to be honest came in at **1.000** and **0.750**.

The construction argument was not wrong — it is still true that those pairs
cannot contain a passage retrieval never found. It was **irrelevant**, because it
was an argument about the *targets* and the variance turned out to live in the
*queries*.

## The evidence: one chunk, two queries, sixteen ranks apart

Eight target chunks in this gold set are reached by more than one query. The
spread within a single chunk dwarfs the spread between cohorts:

```
southasia-03-muziris-papyrus::original::000
   rank  4   sim 0.449   no filter   "the valuation of a cargo of nard and ivory
                                      shipped on the Hermapollon"
   rank >20      —       no filter   "What did ships carry from Muziris?"

southasia-01-akananuru-149::original::000
   rank  1   sim 0.371   no filter   "யவனர் முசிறி பொன்னொடு வந்து கறியொடு பெயரும்"
   rank >20      —       no filter   "What did ships carry from Muziris?"

africa-03-periplus-adulis::original::001
   rank  1   sim 0.524   filtered    "the port of Adulis and the ivory brought to
                                      the Aksumite capital"
   rank >20      —       no filter   "What did Rome trade with the Kingdom of Aksum?"
```

**Same chunk. Same index. Same embedding model. Same run.**

> **Only one of the eight is a clean single-variable comparison**, and it must be
> named as such rather than allowed to borrow strength from the others. The
> Muziris papyrus pair differs in wording alone — both queries are English, both
> unfiltered, both resolve to the identical chunk. n=1, and a swing of at least
> sixteen ranks. The akananuru and weilue contrasts change the query *language*
> as well; the adulis, hou-hanshu and pepper-cargo contrasts change the *language
> filter* as well. All seven confounded cases point the same way, which is
> suggestive and is not the same as evidence.

## What actually sank the archived cohort

**One question, asked three times.** "What did ships carry from Muziris?" is 3 of
the 8 archived pairs and misses 2 of its 3 targets. "What did Rome trade with the
Kingdom of Aksum?" misses its one. Four of the cohort's eight pairs come from two
broad questions, and those two questions account for **three of the four misses**.

That is not a corpus property or a language property. It is a **query
specificity** property, and it is measurable per pair.

## This puts a number on the Phase 1 exit-gate verdict

The persevere verdict rests on the Adulis discriminator: *the system refused a
question whose answer it was holding, and answered correctly when the question
was reworded against byte-identical evidence.* Until today that was an anecdote
about answering. It is now a measured retrieval fact:

| question | evidence chunk | rank |
| --- | --- | --- |
| "What did Rome trade with the Kingdom of Aksum?" (refused at the gate) | `adulis::original::001` | **>20** |
| "the port of Adulis and the ivory brought to the Aksumite capital" | the same chunk | **1** |
| "What was exported from Adulis?" (the rewording that worked) | `adulis::original::005` | 15 |

The closing summary attributed the failure to "ranking, question handling and
scoring". **It was ranking, and the refusal was correct** — the answerer was not
holding the evidence at all, because retrieval never surfaced it. That is a
better result for the verdict than the verdict claimed: the refusal path worked
on genuinely absent evidence rather than mis-handling present evidence.

## The one number with a Phase 1 prior lands inside it

`spread` (mean top-1 to rank-6) is the only quantity here that can be compared
backwards. Phase 1: **0.105** overall, **0.045–0.094** on the questions that
matter. Today: **0.146** overall, and the `archived_answer` cohort — which *is*
the Phase 1 questions — sits at **0.091**, inside the old band.

So the index has not drifted. The corpus grew by three chunks and the discriminating
power on the original questions is where it was. Everything else in the table is
new and has nothing to be compared against, which is what makes it a baseline.

## Two gaps earned their keep on the first run

`translation_case` is the cohort that proves the split was worth building:
`gapDoc +0.022` against `gapAny -0.142`. Retrieval finds the **right document**
and the **wrong chunk inside it** — and the chunk beating the target is, in every
case, that document's own English translation answering an English query.

```
tc-muziris-papyrus-valuation   gapDoc -0.017   gapAny -0.224
tc-frankincense-harvest        gapDoc -0.053   gapAny -0.178
tc-nabataean-epitaph           gapDoc +0.146   gapAny -0.048
```

One number could not have told those apart, and they need different responses:
the first is a hardening problem for W2c, the second is a question about whether
an English query should be reaching a non-English original at all when a
published translation of the same passage exists.

**The four `lang_pool: non_english` probes score 1.000 partly because that filter
removes exactly this competition.** They are not cheating — the filter is what
makes them a cross-lingual test — but it means the 1.000 and the 0.500 answer
different questions, and the ALL row averages three incomparable things. Read the
cohort table; the total is close to meaningless.

## recall@6 is stricter than the pipeline, deliberately

The answer path retrieves at **k=12** (`retrieval_k` in every archived run). Of
the six recall@6 misses, two are inside the pipeline's reach and four are not:

```
within k=12   au-khao-sam-kaeo 10,  tc-frankincense-harvest 11
outside       adulis-exports 15,  aksum-trade-adulis >20,
              muziris-cargo-papyrus >20,  muziris-cargo-akananuru >20
```

Kept at 6. A metric loosened to match the current pipeline stops being able to
say the pipeline should change — and W2c may well move k. But the k=12 line is
recorded here so the distinction is not lost.

## An improvement to the corpus demoted the evidence it improved

`adulis-exports` was rank 3 at similarity 0.401 in the archived run of
2026-08-12, when the Greek exports sentence sat inside a 919-character chunk. A4
replaced that Greek with the fuller Wikisource text; the sentence now sits in a
477-character chunk of its own and ranks **15 at 0.339**.

Not strictly like-for-like — different chunk boundaries are the whole point — but
the direction is unambiguous. **A more accurate corpus made its most load-bearing
passage harder to retrieve.** Worth carrying into W3: tranche work that improves
source fidelity can cost retrieval, and nothing in the repository would have
reported that before today.

## lexOv's limit, found immediately

`probe-parthian-skz` scores **1.00**. The query is romanised Parthian
(`šāhān šāh Ērān ud Anēran Šābuhr`) and every Latin-alphabet token in it appears
in the transliterated target — so the measure reads a *same-language* query as
maximal reuse. It cannot tell transliteration from English. Four other probes
score blank, their queries carrying no Latin tokens at all.

The field is doing its job for the nine English-target pairs it was added for.
It is noise everywhere else, and this is written down so nobody later reads that
1.00 as a defect in the probe.

## The queue

1. **B3 distractors** — `BLOCK_B3_DISTRACTORS.md`, three decisions outstanding.
2. **Add a `specificity` label to the gold set** (broad / specific), so the B5
   curve can be read by it. On today's evidence that is the largest single
   source of variance in the whole table, and W2b will otherwise measure it as
   noise.
3. **Query rewriting is now a candidate for W2c**, on evidence rather than on
   the general principle. It was not in `PHASE2_PLAN.md`'s C-list.
4. Carried: `cite.py`'s `case_folded` state and the `translation_chunk_id`
   rename (Block C, C1).

---

# Correction to Block B2 — the specificity claim does not survive its own re-cut

The B2 notes above end by calling query specificity "the largest single source of
variance in the whole table" and scheduling a broad/specific label for the gold
set. **The re-cut was run before the label was written, cost nothing because the
per-pair results were already archived, and does not support the claim.**

## What the re-cut actually shows

Five rank-blind cuts over the 32 archived pair results:

```
cut                                          yes            no
query's rarest token points at expect_doc    19/21 = 0.90   7/11 = 0.64
query has any token unique to one document   24/30 = 0.80   2/ 2 = 1.00
query is shared with another pair             3/ 5 = 0.60  23/27 = 0.85
pair carries a language filter                5/ 5 = 1.00  21/27 = 0.78
target chunk is English                       8/ 9 = 0.89  18/23 = 0.78
```

The strongest is lexical anchoring at 0.90 / 0.64. **Three cuts separate, in
different directions, and with six misses in thirty-two pairs no cut has the
sample to be told apart from the others.** The language-filter cut is a perfect
5/5, which on n=5 means nothing at all.

Two of the six misses — `adulis-exports` at 15 and `tc-frankincense-harvest` at
11 — have their rarest token pointing squarely at the expected document and miss
anyway. Lexical anchoring is not sufficient, so it is not the mechanism even
where it correlates.

## What survives, stated at the size the evidence supports

The one-chunk-two-queries table stands: `muziris-papyrus::original::000` at rank
4 for one English unfiltered query and >20 for another is a fact about the query,
and it isolates the query because everything else is held constant. **What does
not follow is that query specificity is the dominant term across the table.** I
generalised one clean n=1 contrast into a claim about thirty-two pairs, and the
free re-cut is what caught it.

> **Second overclaim of this block, same shape as the first.** Finding 2 of B1
> asserted the index had diverged from the corpus on a dated line rather than a
> measurement. This asserted a dominant cause from a single contrast. Both were
> reaching for one clean causal story from a small sample, and both were caught
> by doing the cheap check rather than by thinking harder — which is the Phase 1
> lesson (*two hypotheses stated confidently and refuted by one cheap check
> each*) recurring at the same rate in Phase 2.

## What was built instead of the label

**No broad/specific label was added.** A label assigned after seeing the ranks it
is meant to predict cannot be evidence for anything, and hand-labelling 32 pairs
against a hypothesis I already favour is how the doc-id-proxy probe passed for
the wrong reason.

`run_ranking_check.py` now records two **mechanical, rank-blind** fields per pair:

| field | meaning |
| --- | --- |
| `anchor_doc` / `anchor_points_home` | the document a query's rarest vocabulary points at — a token occurring in exactly one document of the index — and whether it is the expected one |
| `shared_query` | whether another pair uses the same query string |

Both are computed from the index and the gold set, never assigned. The printed
report carries a three-line diagnostics block ending in the sentence *"Do not
read a cause out of them without a run designed to test one."*

## A design question the re-cut did raise, and it is yours

`muziris-cargo` is **one query with three targets**, made three pairs on the B1
reasoning that "a ranking that finds one of the three is not the same result as
one that finds all three". Its only discriminating token — *muziris* — occurs in
one document, the Periplus. The Periplus target ranks 5; the papyrus and
Akananuru targets rank >20.

So the design choice, not the retriever, may be producing two of the six misses:
a multi-target query is scored once per target, and the targets sharing no
vocabulary with it are close to unreachable by construction.

**The alternative** is one pair per query with a set of acceptable targets, where
recall@6 asks whether *any* acceptable target is in the top 6. That would move
`archived_answer` from 0.500 (4/8) to roughly 0.667 (4/6) and change what the
metric means. It is a judgement about what retrieval owes a broad question, and
it should be made deliberately rather than inherited from B1's first instinct.
**Not changed. Flagged.**

## SEARCH_K raised 20 → 50

`recall@6`, `MRR@10` and `top1_to_rank6` are invariant to k — verified against a
constructed ranking. **The score gaps are not**, because a pair with no rank has
no similarity and contributes no gap: at k=20 the 2026-08-14 baseline computed
its gap means over 26 of 32 pairs, silently dropping the three that failed
hardest. On a two-pair worked example the same bias moves a mean gap from 0.40 to
0.05.

That makes the recorded `gapDoc +0.051` / `gapAny +0.014` **survivorship-biased
in the one number `PHASE2.md` says predicts survival at scale.** k is now fixed
at 50 with the reason in a comment, because changing it between rungs would move
the gap means for that reason alone and make the curve incomparable with itself.

The 2026-08-14 run stays in `eval/ranking_runs/`. Its recall, MRR and spread
remain valid and comparable; **its two gap means are superseded** by the re-record.

---

# Block B2, re-recorded at k=50 — the gap is zero

```
ranking check  20260814T082748+0000  index=57 chunks  k=50  voyage/voyage-3.5

cohort              pairs  recall@6   MRR@10  gapDoc  gapAny  spread  lexOv
archived_answer          8  0.500 ( 4)  0.123  -0.111  -0.119   0.091   0.00
authored                 9  0.889 ( 8)  0.844   0.057   0.047   0.136   0.23
retrieval_probe         11  1.000 (11)  1.000   0.114   0.090   0.178   0.14
translation_case         4  0.750 ( 3)  0.312   0.022  -0.142   0.190   0.04
ALL                     32  0.812 (26)  0.651   0.035   0.000   0.146   0.12
```

recall@6, MRR@10 and spread are **identical** to the k=20 run, as predicted. The
gaps moved, and by more than expected.

## The headline number is zero

`gapAny` across the whole gold set is **0.000** — it read **+0.014** at k=20.
`gapDoc` fell from +0.051 to +0.035. `archived_answer`'s gapDoc went from -0.075
to -0.111.

> **Averaged over 32 pairs, the known-good passage scores no better than the best
> competing passage in the index.** `PHASE2.md` names the gap, not the raw
> similarity, as the thing that predicts survival at scale — and the true value
> of it at 57 chunks is zero. The +0.014 was survivorship: three pairs with no
> rank contributed no gap, and they were the three worst.

This is what the k change was for, and it is a materially different starting
point for W2b than the run recorded ninety minutes earlier.

## Two pairs now have a rank, and one still does not

```
aksum-trade-adulis        >20  ->  29   sim 0.373  gapDoc -0.185
muziris-cargo-papyrus     >20  ->  41   sim 0.285  gapDoc -0.218
muziris-cargo-akananuru   >20  ->  >50
```

`muziris-cargo-akananuru` is not in the top **50 of 57**. The Old Tamil chunk sits
in the bottom seven of the index for the English question whose evidence it is —
while ranking **1st** for the Tamil query in `probe-tamil-akananuru`.

**Old Tamil is the corpus's broken cross-lingual link, and it is the only one.**
The other three minority scripts are reached from English without a filter and
rank well: `tc-nabataean-epitaph` (xna) 2, `tc-jabal-dabub` (xsa) 2,
`vimose-runes` (gmq-pro) 3. Part 4 recorded Old Tamil at 0.368 against 0.6–0.7
for other scripts and noted "with one Tamil chunk in the corpus that number means
little". It means something now: the passage is reachable in its own language and
unreachable in English.

**And the gold set has no English→Tamil cross-lingual probe.** The four
`lang_pool: non_english` probes cover grc, lzh and xpr only. The single piece of
evidence for the worst cross-lingual result in the corpus is an archived_answer
pair that was never designed to test it. That is a gap in the gold set, not in
the retriever, and it should be filled before W3 decides how much Tamil to add.

This is the Phase 1 gate's own pivot language arriving with a number:
*"Pivot if cross-lingual retrieval is weak for the sparse-evidence regions."*

## A metric whose name was wrong

`not_in_top_20` was hardcoded and **survived SEARCH_K moving to 50**, so the k=50
run reported its unranked count under a name asserting k=20. The printed `>20`
column marker had the same defect. Both now derive from `SEARCH_K`, the archived
run records `search_k`, and the header prints it.

Cheapest possible instance of the standing lesson, and now impossible: a new
assertion checks the key is named for `SEARCH_K`, and mutation 9 of 14 restores
the hardcoded name to prove it fails.

**Writing that guard exposed a second one.** The mutation initially reported "no
failures" — because the *earlier* aggregate assertion indexed the key with `[]`
and raised `KeyError`, aborting the suite before the guard that owns the defect
ever ran. A crash in an unrelated assertion had hidden it. Changed to `.get()`,
and it is the same shape as Block 0's truncated test run: **a suite that stops
early reports a green-looking absence of failures.**

## State

```
python -m eval.test_ranking_check    32 assertions, 0 failed
python scripts/mutate_ranking.py     14/14, sources restored
```

Baselines archived at k=20 (`20260814T074614`) and k=50 (`20260814T082748`).
**The k=50 run is the baseline.** The k=20 run's recall, MRR and spread stand;
its two gap means are superseded and it records no `search_k` field, which is
why the field now exists.

## Queue

1. **B3 distractors** — three decisions, `BLOCK_B3_DISTRACTORS.md`. Blocks B4.
2. **An English→Tamil cross-lingual probe**, and a ruling on whether a
   multi-target query is N pairs or one pair with N acceptable answers.
3. W2c candidates now carrying evidence: query handling, and whatever addresses
   a mean gap of zero.

---

# Ranking depth settled before B4 — there is no fixed k

`SEARCH_K` is gone. Every pair is ranked against the **whole view**, at every rung.

## Why a constant was the wrong shape

k was 20, then 50, and both were defensible at the index they were chosen for.
That is the problem: **a fixed depth cannot be right at more than one rung of a
curve whose whole subject is index size.**

- At 57 chunks, k=20 left three pairs unranked and biased the gap means over 26
  of 32 pairs.
- k=50 fixed that at 57 — and would have broken at 450. The three deepest targets
  sit at ranks 29, 41 and >50 of 57; at the same relative depth in a 450-chunk
  index they land near **229, 324 and 395**. All three would fall outside k=50,
  contributing no gap.

So the 450 rung would have been survivorship-biased in exactly the way the 57
rung had just been fixed, and **the curve would have compared an unbiased
endpoint against a biased one** — which is the failure the curve exists to avoid,
smuggled into its own instrument.

Ranking everything removes the choice rather than tuning it. `recall@6`,
`MRR@10` and `top1_to_rank6` were always invariant to depth; the gaps now are
too, because no pair can be out of reach. 450 ordered rows per pair is nothing to
Postgres.

## Two names corrected on the way

`not_in_top_20` was hardcoded and survived k moving to 50, so the k=50 run
reported its count under a name asserting k=20. It is now simply `unranked`,
which carries no threshold to go stale. The `>20` column marker had the same
defect and now prints `none`.

**Writing the guard for that exposed a second defect.** The mutation restoring
the hardcoded name reported "no failures" — because an *earlier* assertion
indexed the key with `[]` and raised `KeyError`, aborting the suite before the
guard that owns the defect ever ran. Changed to `.get()`. Same shape as Block 0's
truncated test run: **a suite that stops early reports a green-looking absence of
failures**, and this time the thing doing the truncating was one of my own
assertions.

## State

```
python -m eval.test_ranking_check    35 assertions, 0 failed
python scripts/mutate_ranking.py     14/14, sources restored
```

Mutation 9 now compiles a fixed depth back in and proves the suite catches it.

## The baseline needs one more re-record

The archived 57-chunk runs were taken at k=20 and k=50. Neither ranked the whole
view, so `muziris-cargo-akananuru` has never contributed a gap. One batched
request at full depth gives the first baseline with **all 32 pairs contributing
to every aggregate** — and it will almost certainly push `gapAny` below zero,
because the pair that has never counted is the worst in the set.

Do this **before** B4 loads anything: the 57-chunk rung has to be measured the
same way as the 150 and 450 rungs, or the curve's first point is not on the same
axis as the other two.

## B3 shortlist updated against the baseline

`BLOCK_B3_DISTRACTORS.md` now opens with what B2 changed. The three decisions are
unchanged; what is at stake in each is now evidenced rather than argued:

- the mean gap is **already zero** at 57 chunks, so the curve measures how far
  below zero it goes, not whether erosion begins;
- `archived_answer`'s `gapDoc -0.111` means competing documents already outrank
  the right ones — seam 2's risk is measured, not hypothetical;
- **seam 3 is the highest-value seam, not the safest.** The `authored` cohort
  (0.889, all nine targets English object descriptions) is the strongest in the
  table, and museum catalogue prose is the only candidate that competes with it.
  It is the only seam that can tell whether that result is real or an artefact of
  having no English competition. The reverse of how it was originally framed;
- `muziris-cargo-akananuru` is already unreachable and will read flat across all
  three rungs. **Flat is not robust.**

---

# Block B2 — FINAL baseline, 2026-08-14, full-depth

```
ranking check  20260814T084042+0000  index=57 chunks  depth=57  voyage/voyage-3.5

cohort              pairs  recall@6   MRR@10  gapDoc  gapAny  spread  lexOv
archived_answer          8  0.500 ( 4)  0.123  -0.132  -0.139   0.091   0.00
authored                 9  0.889 ( 8)  0.844   0.057   0.047   0.136   0.23
retrieval_probe         11  1.000 (11)  1.000   0.114   0.090   0.178   0.14
translation_case         4  0.750 ( 3)  0.312   0.022  -0.142   0.190   0.04
ALL                     32  0.812 (26)  0.651   0.025  -0.008   0.146   0.12
```

**This is the W2a baseline.** All 32 pairs contribute to every aggregate for the
first time. The k=20 (`074614`) and k=50 (`082748`) runs stay archived; their
recall, MRR and spread are valid, their gap means are superseded.

## The gap is negative

```
depth   gapDoc   gapAny   pairs contributing a gap
   20   +0.051   +0.014   26 of 32
   50   +0.035    0.000   31 of 32
   57   +0.025   -0.008   32 of 32
```

> **Averaged over the gold set, the known-good passage scores slightly WORSE than
> the best competing passage in the index — at fifty-seven chunks, before a
> single distractor exists.**

The progression is the bias draining out, not the retriever changing: each step
admits pairs that were previously out of reach, and every one of them was worse
than the pairs already counted. The +0.014 first recorded was an artefact of the
three worst pairs having no rank to be measured at.

`PHASE2.md` names the gap, not the raw similarity, as what predicts survival at
scale. **The quantity W2b is designed to watch erode has no positive value to
erode from.**

## The invariance claim held empirically

`recall@6 = 0.812`, `MRR@10 = 0.651` and `spread = 0.146` are **identical across
all three runs** at depths 20, 50 and 57. That was asserted from a constructed
stub ranking before the first re-record; it is now confirmed against three real
runs. Only the gaps moved, exactly as the stub predicted and only in the
direction the bias predicted.

Worth stating because the reverse is the usual outcome: a property proved on a
fixture and quietly false in production.

## Old Tamil, measured at last

```
muziris-cargo-akananuru   rank 51 of 57   sim 0.224   gapDoc -0.278
probe-tamil-akananuru     rank  1 of 57   sim 0.371   gapDoc +0.054
```

Same chunk. **From English it is 51st of 57 with the lowest similarity in the
entire table** (next lowest 0.285); from Tamil it is first — but at 0.371, which
is also **the lowest rank-1 similarity in the table**, every other winner scoring
0.42–0.75.

So there are two distinct results, and they should not be merged:

1. **English → Old Tamil is broken**, not weak. 0.224 and rank 51 is not a
   ranking that hardening moves.
2. **Old Tamil is weakly embedded even in its own language.** Winning at 0.371
   in a 57-chunk index is winning by default. Part 4 recorded 0.368 for this
   script and hedged that "with one Tamil chunk in the corpus that number means
   little". Two independent measurements, fourteen days apart, agreeing to three
   decimal places — it is a property of the model on this script, not noise.

This is the Phase 1 gate's pivot language with a number attached: *"Pivot if
cross-lingual retrieval is weak for the sparse-evidence regions."* It is weak for
exactly one language, and that language has **no English→Tamil probe in the gold
set** — the four `lang_pool: non_english` probes cover grc, lzh and xpr only. The
worst cross-lingual result in the corpus rests on a single archived_answer pair
that was never designed to test it.

## Block B2 is closed

```
python -m eval.test_ranking_check    35 assertions, 0 failed
python scripts/mutate_ranking.py     14/14, sources restored
```

Three baselines archived, the third definitive. Total spend across B1 and B2:
**four batched embedding requests.**

## Open, in order

1. **B3 — yours.** Three decisions in `BLOCK_B3_DISTRACTORS.md`. Blocks B4.
2. **An English→Tamil cross-lingual probe**, and a ruling on whether a
   multi-target query is N pairs or one pair with N acceptable answers. Both
   change what the B5 curve measures; both are free.
3. **W2c now has an evidenced target list**: a mean gap of zero-to-negative,
   `archived_answer` at -0.132, and query handling. None of these were on
   `PHASE2_PLAN.md`'s C-list, which was written before any of them was measured.
4. Carried: `cite.py`'s `case_folded` state, the `translation_chunk_id` rename.

---

# Block B3 — the distractor seams are ruled (2026-08-14)

`PHASE2_PLAN.md` action #3, the one the plan reserves for the project owner.
Full record in `BLOCK_B3_DISTRACTORS.md`.

| # | decision | outcome |
| --- | --- | --- |
| 1 | Periplus scope | **§1–3 and §7–13 only** (~25 chunks) |
| 2 | Indian Ocean / Arabian classical geography | **Admitted freely** |
| 3 | Museum collection | **The Met Open Access**, single collection |

Decision 1 took the strict reading. That included excluding **§57–66**, a range
the shortlist had originally proposed as safe — "the far side past Limyrike" —
before it was noticed that §57–66 is the Ganges, Chryse and Thina, which is
exactly where `seasia-01`, `seasia-03` and `eastasia-03` sit. **The same error as
§7–26, made in the same document, and caught only on a second pass: treating
distance from a gold pair's *document* as distance from its *subject*.**

## Decision 2 went against the recommendation, and changes what the curve means

Recorded as a ruling, not re-argued. What matters is the consequence, which is
not "the shortlist was right":

Admitting Strabo XV and Pliny *NH* VI means some distractors **can genuinely
answer a gold-set question**. When one outranks a gold target that is not
self-evidently an error — a user asking what ships carried from Muziris is
arguably well served by Strabo. So the curve stops measuring *does the right
passage survive noise* and starts measuring *does the designated passage survive
competition*.

That is a defensible question, and arguably the more realistic one. **It is not
the question B5's decision point was written against.** The plan says:

> degradation milder than predicted → W3 can move faster
> degradation as or worse than predicted → W2c is load-bearing and W3 stays shut

Against a curve containing semantically relevant competitors, "worse than
predicted" no longer implies W2c is load-bearing. It may mean the corpus is small
and the world is large — which no reranker fixes, and which is a W3 finding
wearing a W2c costume. **The decision point must be restated before B5 runs.**

> This is the sixth appearance of *a result is comparable only within the thing
> that produced it*, and the first at the level of a research question rather
> than a number: the metric is unchanged, the data under it now answers something
> else, and only the written decision rule would have carried the difference.

## What is being built instead of the objection

B5 will report, for every pair whose rank worsens between rungs, **the text of
whatever outranked it** and whether that thing is a distractor. Twenty-odd lines
of adjudication per rung. Without it a distractor-driven collapse and a
noise-driven collapse are the same number; with it, decision 2's cost is visible
and case-by-case rather than assumed either way.

## Budget under the rulings

```
seam 1  Periplus §1–3, §7–13                                    ~25
seam 2  Strabo IV–VII + XV, Pliny III–IV + VI, Ptolemy VII     ~225
seam 3  The Met, non-Roman-contact material                    ~150
                                                       total   ~400   (+57 = 457)
```

Decision 2 makes seam 2 both the largest and the loosest, which is why the
adjudication step is not optional.

## Before B4 fetches anything

1. **Verify the Met's licence and write `data/met-licence-declaration.txt`**,
   matching `data/pleiades-licence.txt` and `data/geonames-licence.txt`. My
   recollection is CC0 for Open Access object data. **Recollection is not a
   licence check** — this project has already recorded that a remembered
   gazetteer id is an authored coordinate wearing a citation, and a remembered
   licence is the same move.
2. Restate the B5 decision point per above.
3. B4 containment, unchanged: `is_distractor` column, `retrievable_chunks` stays
   distractor-free, separate `retrievable_chunks_with_distractors` view, and a
   mutation-verified test that a distractor is unreachable from the answer path.

---

# Block B4 — containment, built before any distractor exists (2026-08-14)

Nothing has been fetched. The order is deliberate: **a containment test written
after the data can pass because the data happens to sit somewhere harmless.**

## The Met licence, checked rather than recalled

`data/met-licence-declaration.txt`, alongside the Pleiades and GeoNames
declarations. CC0, fetched from https://www.metmuseum.org/hubs/open-access on
2026-08-14 and quoted verbatim.

**One condition that constrains the fetch, and it was not in my recollection:**
the CC0 grant applies to **public-domain artworks only**, and the API serves
non-Open-Access objects too. CC0 is a property of the individual object record,
not of the API. So every ingested record must be filtered on the API's own
`isPublicDomain` field, that field must be **recorded on the row rather than
assumed at fetch time**, and a record failing it is dropped with a counted, named
reason. This is why the licence is checked instead of remembered — the check
produced a constraint the recollection did not have.

## Two hazards found by auditing every reader first

`PHASE2_PLAN.md` B4 names `ingest/verify`, `answer/run_answer` and
`ui/build_ui_data.py` as the readers to make blind. Grepping every `FROM chunks`
and `FROM documents` in the repository found two that are on none of those lists.

### (a) One routine command would have destroyed the whole distractor corpus

`chunks.doc_id REFERENCES documents(doc_id) ON DELETE CASCADE`, and
`ingest/db.py`'s prune runs:

```sql
DELETE FROM documents WHERE NOT (doc_id = ANY(seed_doc_ids));
```

Every distractor document is absent from the seed list by definition. So
`python -m ingest.run_ingest` — **the command at the top of the standing session
ritual** — would have cascade-deleted 400 distractor chunks and the two to three
batched embedding requests behind them. Silently, with a success report.

Both DELETEs now carry `AND NOT is_distractor`, with the reason written beside
them rather than left as a defensive-looking clause someone later tidies away.

### (b) The one reader that spends money

`answer/store.py` reads `FROM chunks` directly in three places, filtering only on
`eligible_for_retrieval` — which a distractor must be, or it cannot be retrieved
at elevated N. The expensive one is `SELECT_TRANSLATABLE`: it would have fed
non-English distractors to the translation pipeline and **spent money translating
Strabo**. `TRANSLATION_STATS` would have reported an inflated `translatable`
count from the same defect.

It reads `chunks` directly for a good reason — the translator needs chunks that
have no vector yet, which the retrieval view excludes by definition. That makes
it the one place where containment cannot be inherited from a view, and the only
place where the guard has to be written out three times.

> **The plan's list of consumers was a list of the ones that read; the one it
> missed was the one that writes an invoice.**

## The schema

`scripts/schema-b4-distractors.sql`, idempotent:

- `is_distractor` on **both** `chunks` and `documents`;
- `distractor_source` and `met_is_public_domain` on `documents`, with a CHECK
  tying them to the flag;
- a **trigger** asserting a chunk agrees with its document about being a
  distractor — without it a distractor document could hold a citable chunk,
  which is this file's whole failure mode arriving through the back door;
- `retrievable_chunks` gains `AND NOT is_distractor`. Every column is unchanged,
  so `citable_passages` and the entire answer path become distractor-free
  **without being edited** — the same inheritance that carried Part 3's
  `pointer` exclusion;
- `retrievable_chunks_with_distractors`, the only surface from which a distractor
  is visible, carrying `is_distractor` so B5's adjudication can say whether the
  thing that outranked a gold target was padding or corpus.

## The canary, and the tautology it was about to become

The schema loads a permanent synthetic distractor so the containment assertions
can run and fail on a database holding no real distractors at all.

**It carries no embedding — and both views require `embedding IS NOT NULL`.** So
the obvious assertion, "the canary is absent from `retrievable_chunks`", passes
*because the vector is missing*, and would keep passing with `AND NOT
is_distractor` deleted from the view. A containment test that cannot fail, in the
file whose entire job is proving containment. Tenth instance of the standing
lesson, caught while writing it rather than by mutation.

Every view assertion therefore runs inside a savepoint that first gives the
canary a vector and then rolls back. Nothing fabricated survives, and the
exclusion being asserted is caused by the distractor flag alone.

The suite also asserts the canary **is** visible to
`retrievable_chunks_with_distractors`. Without that inverse, "invisible to
`retrievable_chunks`" could be passing because nothing is visible anywhere.

## Mutations against a live schema object

`scripts/mutate_distractors.py`. Two of the five guards live in a **view**, and
rewriting the `.sql` file on disk changes nothing about the running database — a
text mutation would have "passed" against an unmodified database and proved
nothing. So the harness replaces the live view with a version missing its guard,
runs the suite, and restores from the schema file.

Five mutations: the baseline view loses its guard; the curve view gains one it
must not have; the trigger is dropped; the translator's guard is removed; the
translatable count's guard is removed. Plus a drift check that the suite's copy
of the prune DELETEs still matches `ingest/db.py`'s — otherwise the suite would
be proving containment for a statement nobody runs.

## To run, on the host

```powershell
python scripts\schema-b4-distractors.sql   # via psql, or apply through ingest.db
python -m ingest.test_distractors          # 10 assertions, no spend
python scripts\mutate_distractors.py       # 5 mutations + drift check, no spend
```

**Then, and only then, the fetch.** `python -m eval.test_ranking_check` and
`scripts/mutate_ranking.py` are unaffected — 35 and 14, still green.

## Still to build in B4

1. The fetcher itself: Periplus §1–3 and §7–13 from the Wikisource route A4
   already built; Strabo, Pliny and Ptolemy; the Met API filtered on
   `isPublicDomain`. ~400 chunks, two or three batched embedding requests.
2. A `--distractors` mode for the ingest path that cannot write a row with
   `is_distractor = false`.
3. The B5 adjudication report — for every pair whose rank worsens between rungs,
   the text of whatever outranked it and whether it was padding. Required by
   Block B3's decision 2.

---

# Block B4 — the containment layer failed on first run, three ways

All three are mine, and one of them is the error class this session has spent the
whole day naming.

## 1. The run instruction was wrong

`python scripts\schema-b4-distractors.sql` hands a SQL file to the Python
interpreter, which dies on the first em-dash. The comment beside the block said
"via psql, or apply through ingest.db" and the block itself said `python`.

Fixed by writing the applier the instruction implied: `scripts/apply_sql.py`.
It resolves the DSN the same way as everything else and sends the file as **one
statement**, so a schema migration is one implicit transaction — which is why
the failed attempt left the database untouched rather than half-migrated.

## 2. The canary INSERT was written against a table whose DDL I had not read

`parallel_group text NOT NULL` exists on `chunks`. The INSERT omitted it and
failed on the constraint.

> **Same error class as B1 finding 2 and the B2 specificity claim: asserting
> something about the repository without measuring it.** Third instance today.
> The first two were caught by cheap checks; this one was caught by the host,
> after I had shipped it, which is the expensive way.

Fixed, and then made impossible: `ingest/test_distractors.py` gained an
**offline pre-flight** that parses `schema-part3.sql`, derives the NOT NULL set
for `documents` and `chunks`, and asserts the canary INSERT covers it. It runs
before any connection is opened, so the next omission fails for free instead of
on the host. Verified it can fail: removing `parallel_group` from the INSERT
reports `missing: ['parallel_group']`; misspelling `text_fidelity` reports both
the missing column and the unknown one.

**The pre-flight's first draft was itself wrong.** It filtered lines by prefix
and so read `OR` — a continuation line of the multi-line
`chunks_embedding_provenance` CHECK, containing the words "NOT NULL" — as a
required column, and reported a missing column that does not exist. A false
alarm in a pre-flight is worse than no pre-flight, because the whole value is
being trusted. Now it tracks parenthesis depth. Caught by running it.

**And the first attempt to prove the pre-flight could fail was also wrong.**
Deleting `parallel_group` from the file with a plain string replace hit the
`retrievable_chunks` view definition instead — the view's SELECT list begins
with the same four column names as the INSERT — so the check appeared unable to
fail when it was the test of the test that was broken. Third layer of the same
morning, and the reason to state which specific text a negative test edits.

## 3. A restore failure could have left a mutated view live

`scripts/mutate_distractors.py` called `restore_schema()` inside `finally`;
restore raised on the broken canary INSERT and killed the harness mid-recovery.
In this instance nothing was lost — the mutation applied at the time was
byte-identical to the pre-B4 view definition, and the schema had never applied,
so the database was in its original state. **That was luck, not design.**

The failure that was one step away: a harness that dies after applying
`VIEW_WITHOUT_GUARD` leaves the live `retrievable_chunks` with **no distractor
guard**, and the next ranking run reads it and reports a clean number over an
index full of padding.

`restore_schema()` now returns a reason instead of raising, the loop breaks on
the first restore failure, and the message names the recovery command. Same
lesson as Block 0's three mutation scripts — a restore failure and a suite
failure are different findings — one layer out, where the thing being restored
is a schema object rather than a file.

## Order corrected

```powershell
python scripts\apply_sql.py scripts\schema-b4-distractors.sql
python -m ingest.test_distractors      # 4 offline pre-flight + 10 DB assertions
python scripts\mutate_distractors.py   # 5 mutations + a drift check
```

`eval.test_ranking_check` (35) and `mutate_ranking.py` (14) are untouched.

---

# Block B4 — containment green (2026-08-14)

```
python scripts\apply_sql.py scripts\schema-b4-distractors.sql   applied
python -m ingest.test_distractors                               15 passed, 0 failed
python scripts\mutate_distractors.py                            5/5, schema restored
```

Every guard is falsifiable and was seen to fail:

| mutation | caught by |
| --- | --- |
| `retrievable_chunks` loses its distractor guard | a vectorised distractor is INVISIBLE to retrievable_chunks |
| `retrievable_chunks_with_distractors` **gains** a guard it must not have | a vectorised distractor is VISIBLE to it |
| the chunk/document agreement trigger dropped | a chunk cannot disagree with its document |
| the translator's guard removed | a non-English distractor is NOT offered to the translator |
| the translatable count's guard removed | a distractor does not inflate the translatable count |

The second is the one that matters most. Without it, "invisible to
`retrievable_chunks`" could have been passing because the row was invisible
everywhere — which is precisely how the canary would have behaved without the
vectorise-and-roll-back savepoint.

**Containment exists before any distractor does.** That ordering was the point.

## A consequence worth stating before the loader is written

`UPSERT_CHUNK` in `ingest/db.py` does not set `is_distractor`, so it inserts the
column's default of `false`. Pointed at a distractor document, the new trigger
will therefore **raise** rather than quietly write a citable chunk into a
distractor document.

That is the containment working, not a bug to route around. The distractor
loader must set the flag explicitly; it cannot inherit the seed corpus's upsert
and hope.

## Two design points the numbers force, before anything is fetched

### 1. The rungs are index sizes, so the load is two tranches, not one

The curve is **57 → 150 → 450**. Those are total index sizes, so the first
tranche is roughly **93** distractors and the second roughly **300** — not one
load of 400. `BLOCK_B3_DISTRACTORS.md`'s budget table gives the total and does
not say this; it is easy to read as a single load and then discover the middle
rung has been skipped.

### 2. Each tranche must be a proportional sample of all three seams

If tranche 1 were all Met catalogue prose and tranche 2 all classical geography,
the 150 and 450 rungs would differ in **composition as well as size**, and the
curve would confound the two — reporting as degradation-with-scale something
that is really a change of what the padding is made of.

> **The curve must vary one thing.** Each tranche is therefore stratified: the
> same seam proportions (~6% Periplus, ~56% classical geography, ~38% Met) at
> both rungs, sampled deterministically so the composition is reproducible and
> recorded in the archived run.

Neither point is in `PHASE2_PLAN.md`, which specifies the rungs and the seams but
not the relationship between them.

## Still to build

1. `ingest/fetch_distractors.py` — three seams to `data/distractors/*.json`, Met
   filtered on `isPublicDomain` with rejects counted and named.
2. `ingest/load_distractors.py` — sets `is_distractor` explicitly, stratified
   tranches, cannot write a distractor row with the flag false.
3. The B5 adjudication report, required by B3's decision 2.

---

# Block B4 seam 3 — the probe earned its keep before a single record was fetched

`ingest/fetch_met_distractors.py --probe` records the live API shape to
`data/distractors/met-api-shape.json` and selects nothing. It found two things.

## 1. A department exclusion that matched nothing

The first draft used a **denylist** of six departments, one of which was
`"Ancient Near Eastern Art"`. The Met's live list has no such department — it has
**`Ancient West Asian Art`** (id 3). The name was renamed at some point and my
list was written from recollection, so the exclusion silently matched nothing.

**That is the department holding Sasanian silver, which is in the seed corpus.**
A denylist that fails open admits exactly the material the ruling excluded, and
reports nothing at all.

Fixed by inverting the structure. A denylist over nineteen departments requires
being right about nineteen names; an **allowlist requires being right about the
six you name**, and `assert_departments()` now refuses to run if any of the six
is absent from the live list, printing the live names. A rename can no longer
quietly widen or empty the selection.

> **Fourth instance this week of asserting something about a system without
> measuring it** — a gazetteer id from memory, an index state from a dated line,
> an INSERT against unread DDL, and now a remote department name. This is the
> first one caught *before* it cost anything, and the only reason is that the
> probe was written to print the live names beside the exclusion marks.

## 2. The material would have been too dissimilar

The probe's two sample records were an **1843 cut-paper silhouette** and a
**1940s photograph of a New York living room**. Both clear the era rule trivially
and both are useless as distractors: `BLOCK_B3_DISTRACTORS.md`'s own warning is
that material too dissimilar makes the curve flat for a reason that has nothing
to do with the corpus, and W2c then looks unnecessary.

The allowlist is therefore chosen for **material culture comparable to the
corpus's find records** — metalwork, ceramics, glass, arms, instruments:

```
American Decorative Arts · Arms and Armor
Arts of Africa, Oceania, and the Americas · Asian Art
European Sculpture and Decorative Arts · Musical Instruments
```

Photographs, Modern Art, Drawings and Prints, European Paintings, The Costume
Institute, The Libraries and the Lehman Collection are all out — not because
they could answer a gold-set question, but because they could not plausibly
compete with one.

## The selection, in the order it applies

| filter | rule |
| --- | --- |
| period | reject if `[objectBeginDate, objectEndDate]` overlaps **27 BC – 1204 AD**. Unknown dates count as overlapping — an unproven negative is not a negative. |
| licence | reject unless `isPublicDomain` is true, per `data/met-licence-declaration.txt`. CC0 is a property of the record, not of the API. |
| department | must be one of the six, re-checked **on the record** rather than trusted from the query |
| text | reject under 120 characters |

Every rejection is counted under a named reason and printed. 502,238 object ids
exist and both probe samples were `isPublicDomain: false`, so the reject counts
are the number to read, not the keeps.

## The text is a rendered catalogue record, stated plainly

The API returns structured metadata, not narrative prose. The distractor text is
assembled from title, objectName, culture, period, dynasty, medium, dimensions,
classification, provenance and credit line. A test render came to 201 characters
against the corpus's `object_description` chunks at 110–409, so the register
matches — and the corpus's own descriptions ("Gold coin. Half-length bust of
Ezanas right, crowned, holding spear...") are themselves rendered catalogue
records. It is not scraped prose and does not pretend to be.

## Next

```powershell
python -m ingest.fetch_met_distractors --preview 8    # read the padding, free
python -m ingest.fetch_met_distractors --fetch --limit 160
```

`--preview` renders eight allowlisted, public-domain, out-of-era records and
stops. **Look at them before committing an embedding request to four hundred.**

---

# Block B4 seam 3 — the preview caught what the probe could not

`--preview 8` rendered eight records. Two defects, one of which would have made
the fetch return almost nothing while blaming the wrong filter.

## The two endpoints do not share a vocabulary

`/departments` calls id 1 **"American Decorative Arts"**. Every object record
returned for id 1 reports `department: "The American Wing"`.

`--fetch` re-checked the record's own `department` against the allowlist, so
**every one of those records would have been rejected** — and counted under
`wrong_department`, a reason that reads like the API returning ids from other
departments rather than like a naming mismatch. The fetch would have come back
near-empty and the era filter would have taken the blame.

`--preview` does not apply that check, which is exactly why it surfaced: the
preview and the fetch disagreed, and the fetch was the one that was wrong.

> **Two names for one thing, in two places, and only one of them checked.**
> This is the `translation_chunk_id` / `translation_chunk` trap in a remote API
> — and the second naming defect in this seam after `Ancient Near Eastern Art`
> / `Ancient West Asian Art`. A display name is not an identifier.

Selection is now keyed on **departmentId**, which is stable across both
endpoints. The record's own name is recorded, its id→name mapping is written
into the output as an artefact, and it is tested against a **denylist** —
correct here because this is a safety net on the record rather than the
selection, and a safety net must fail closed on a name it does not recognise.
The denylist keeps both the current and former names of the West Asian
department, so a revert cannot slip through either.

## The preview showed one sixth of the seam and read like the whole seam

All eight records came from department 1, because the loop filled from the first
department and broke once it had enough. Now round-robin: `preview // 6` from
each, and it prints the listed name beside the reported name with a `DIFFERENT`
flag, so the vocabulary mismatch is visible rather than inferred.

## The material itself looks right

Samplers, candlesticks, a whale oil lamp, pressed glass salts, a hall lantern, a
Bohemian bottle. 150–264 characters against the corpus's 110–409. The register
matches, and the vocabulary genuinely competes: several are **glass** objects,
and the corpus holds Late Roman glass at Hwangnam with an authored pair asking
how Mediterranean glassware reached Korea. An 1815 American "Hall Lantern.
Blown and cut glass" cannot answer that question and will compete for its terms,
which is precisely what a distractor is for.

**One thing to watch rather than fix:** the rendered skeleton is uniform —
*Title. Culture. Dated X. Medium. Dimensions. Credit line.* Four hundred chunks
of near-identical structure may cluster in embedding space and either all
compete or none do. If the 450 rung shows the Met chunks behaving as one block
rather than as individuals, that is the cause, and B5's adjudication report will
show it because it names what outranked each target.

## Re-run before the fetch

```powershell
python -m ingest.fetch_met_distractors --preview 12
```

Twelve, so two from each of the six. Confirm every department returns material
of the right kind — and read the name mapping it now prints.

---

# Block B3 decision 3, amended — a second collection for seam 3 (2026-08-14)

Ruled 2026-08-14: **the Met plus the Cleveland Museum of Art.** The original
ruling was "one collection only — mixing three makes 'where did this come from'
a per-chunk question".

## The reason is not volume, and that matters for the record

The question that prompted this was whether the Met has enough material to cover
the period. **It has the opposite problem.** 502,238 objects, and the era rule
*excludes* anything overlapping 27 BC – 1204 AD — a distractor must not be in
the window. There was never a shortage and there is no coverage gap.

The reason is **skeleton uniformity**. A rendered catalogue record has one shape,
*Title. Culture. Dated X. Medium. Dimensions. Credit line.*, and all eight
preview records had it. Several hundred chunks sharing one skeleton may cluster
in embedding space and either all compete with a gold target or none do — which
would make the W2b curve a measurement of my renderer rather than of the index.

> Recorded plainly because a decision filed under the wrong reason gets revisited
> for the wrong reason. If the curve later looks odd, "we added Cleveland because
> the Met was too small" would send someone hunting a coverage problem that never
> existed.

The original objection is answered by the schema rather than by the ruling:
`distractor_source` is NOT NULL on every distractor row, so "where did this come
from" is a column, not a question.

## Why Cleveland

No API key. The Rijksmuseum and Smithsonian both require one — a credential to
store, rotate and keep out of git, for padding. And its records carry free-text
`description` and `tombstone` fields, so its rendering can differ in *shape*
rather than being the same skeleton with a different accession number.

**That last point is an expectation, not a measurement.** `--probe` reports
`records_with_nonempty_description` out of the sample, and the file says outright
that if the number is near zero, Cleveland renders Met-shaped, the amendment
bought nothing, and that should be said rather than proceeded past.

Licence **not yet verified**. `--fetch` refuses to run until
`data/cma-licence-declaration.txt` exists, the same rule the Met material
followed.

## One era rule, not two

`ingest/distractors_common.py` now holds the era window, the seed, the fetch, the
minimum length and the output shape. Both fetchers import them.

Copying the era rule into a second file would have been **two implementations of
one rule** — the defect this repository has already paid for three times
(`--find` vs `--survey` on numeric ids, `translation_chunk` vs
`translation_chunk_id`, and the JS port of `date_audit` that was rejected on
exactly this argument). A drifted era rule would put in-period material into the
padding on one side only, and nothing downstream would report it.

What is deliberately *not* shared is the field names and the rendering. Those are
genuinely per-API — the Met has `objectBeginDate`, Cleveland has
`creation_date_earliest` — and unifying them would be the opposite error.

`distractors_common.skeleton_report()` profiles how many distinct leading shapes
the padding has and what share the commonest holds. Not a gate; a number to look
at before spending an embedding request on 400 chunks.

## Budget under the amendment

```
seam 1  Periplus §1–3, §7–13                              ~25
seam 2  Strabo, Pliny, Ptolemy (Indian Ocean admitted)   ~225
seam 3a The Met                                          ~100
seam 3b Cleveland                                         ~50
                                                  total  ~400
```

## Next, in order

```powershell
python -m ingest.fetch_cma_distractors --probe      # is `description` populated?
python -m ingest.fetch_met_distractors --preview 12 # 2 per department, and the
                                                    # listed-vs-reported name map
```

Then the Cleveland licence declaration, then both fetches, then the loader.

---

# Block B4 seam 3 — both probes read, and a third naming defect (2026-08-14)

## Cleveland buys what it was added for

```
sampled 40 records · 62 fields
records with a non-empty `description`: 40/40
```

**Every record carries free text.** The fields go well beyond the Met's
structured metadata — `description`, `did_you_know`, `find_spot`, `inscriptions`,
`provenance`, `tombstone`, `artlens_description`. The amendment was made to break
skeleton uniformity and the number says it will: Cleveland chunks lead with prose
rather than with *Title. Culture. Dated X.*

Licence CC0, recorded in `data/cma-licence-declaration.txt`. That file states
plainly that, unlike the Met's, the terms were **not fetched and quoted
in-session** — the fetch needed an approval that was not given, so the claim
rests on the project owner's own reading of the page. A human reading a licence
is a legitimate source; it is recorded as what it is rather than dressed up as a
quotation. CC0 is still checked per record on `share_license_status`, because it
is a property of the record and not of the API.

## The Cleveland allowlist was six guessed names, and the probe could not confirm five

The 40-record sample showed **three** departments, only one of them on the
allowlist. Cleveland has no `/departments` endpoint, so unlike the Met there is
no authoritative list to check against — and **the name is the identifier**,
which is precisely the condition that produced the Met's renamed-department
defect.

Two changes. `--probe` now samples ~1200 records across twelve pages and reports
every department by frequency. And `--fetch` **refuses to run** if any allowlist
entry was never observed, printing the live frequency table. *"Not seen in this
sample"* reads dangerously like *"does not exist"*, and a name that matches
nothing selects nothing and reports nothing.

Expect the six current names to be wrong. They are a guess and the file says so.

## The Met preview found a third naming defect — in the guard written for the first

Two of six departments report a different name on their records:

```
'American Decorative Arts'                  -> 'The American Wing'
'Arts of Africa, Oceania, and the Americas' -> 'The Michael C. Rockefeller Wing'
```

That was the known mismatch, now recorded. **What it exposed is worse.** The
record-level `FORBIDDEN_DEPARTMENT_NAMES` denylist is written in the
`/departments` vocabulary — "Greek and Roman Art", "Ancient West Asian Art" —
but records report *wing* names. A record from a forbidden department, arriving
under a stray id, would report a wing name that is **not in the denylist**, and
the denylist would fail open.

> Same failure as the original `Ancient Near Eastern Art` entry, in the guard
> written to prevent it, one week later. **A denylist of names cannot be
> completed against a vocabulary you do not hold** — and I did not hold it, twice,
> while writing a check that depended on holding it.

Replaced with a vocabulary-agnostic guard that fails **closed** on novelty: the
first record seen for a departmentId establishes the name that id reports, and
any later record reporting a different name is rejected as
`unexpected_department_name`. A stray record cannot pass whatever either endpoint
calls it. Verified: seeding, matching, a forbidden name and an unknown wing name
all behave correctly.

## The Met material is right

Close-helmet, Ancestral Puebloan olla, Chimú silver-and-gold vessel, Meissen wall
bracket, silver candlestick, Solomon Islands panpipe, Chinese dizi. 164–326
characters against the corpus's 110–409, and the vocabulary genuinely competes —
silver, gold, ceramics, textiles, metalwork, bronze — without any of it being
able to answer a gold-set question.

One record drifted: a *drawing* of a firearm decoration, sitting in Arms and
Armor and classified "Works on Paper-Drawings". Harmless, and worth watching only
if drawings come to dominate that department's share.

## Next

```powershell
python -m ingest.fetch_cma_distractors --probe      # ~1200 records, real vocabulary
```

Reconcile `INCLUDED_DEPARTMENTS` against what it prints, then `--preview 12` on
Cleveland to see the prose renderings, then both fetches.

---

# Block B4 seam 3b — Cleveland's real vocabulary (2026-08-14)

The widened probe ran: **1200 records sampled**, written to
`data/distractors/cma-api-shape.json`. (The console output pasted back was stale
scrollback from the earlier 40-record version — the file on disk is the new one,
which is why the file was read rather than the terminal.)

## The allowlist was six guesses and all six exist

```
allowlist_unconfirmed: []

  101  American Painting and Sculpture      74  Decorative Art and Design
   79  Chinese Art                          37  Japanese Art
   15  Korean Art                           14  Textiles
```

`records_with_nonempty_description: 1195/1200`. The second collection does what
it was added for.

**One swap made on the evidence:** `American Painting and Sculpture` (101, and
paintings) out, `Art of the Americas` (46, pre-Columbian material culture) in.
Closer register to the corpus's find records, and geographically disjoint from
all seven regions rather than merely out of era. Flagged for veto; the principle
was already ruled, only the instance changed.

Allowlisted material is **265 of 1200 sampled**, so roughly a fifth before the
era and CC0 filters. Fifty records will need a few thousand scanned. Korean Art
(15) and Textiles (14) are thin and may contribute little.

## The third naming defect of this seam

The denylist listed **"Egyptian Art"** and **"Ancient Near Eastern Art"** as
separate entries, copied straight from the Met's vocabulary. Cleveland combines
them: **"Egyptian and Ancient Near Eastern Art"** (30 in sample). Both entries
matched nothing.

```
Met    Ancient Near Eastern Art   -> renamed to Ancient West Asian Art
Met    /departments names         -> records report wing names
CMA    Egyptian Art               -> Egyptian and Ancient Near Eastern Art
CMA    Ancient Near Eastern Art   -> same
```

> **Three museums, three vocabularies, four silent no-ops.** Each time the
> failure mode is identical: a hardcoded name that matches nothing looks exactly
> like a name that matches and finds nothing to exclude. There is no observable
> difference at the point of use, which is why all four survived review and only
> the probes found them.

Two things changed as a result:

1. `"African Art"` added to the denylist — 44 in sample, and Sub-Saharan Africa
   is a corpus region. It was already excluded by the allowlist; now it is
   excluded twice, deliberately.
2. `--probe` reports **`forbidden_never_observed`** — which forbidden names
   matched nothing. Reported, not gated, because a museum may legitimately have
   no department by a given name. But a no-op now announces itself instead of
   reading like protection. It currently prints `['Ancient Near Eastern Art',
   'Egyptian Art']`, which are the two kept deliberately in case a future rename
   splits the combined department back apart.

**Cleveland's exposure to this was always lower than the Met's**, because its
selection is a strict allowlist — anything not on it is rejected as
`not_in_allowlist` regardless of the denylist. The denylist only matters if a
forbidden department is ever added to the allowlist by mistake. That is exactly
the case it now covers, and the Met's design — select by id, guard by name — was
the one where a wrong name could fail open.

Every rejection path verified: `Art of the Americas` admissible,
`Egyptian and Ancient Near Eastern Art` and `African Art` forbidden,
`Photography` not in the allowlist.

## Next

```powershell
python -m ingest.fetch_cma_distractors --probe        # confirms the swap, ~2 min
python -m ingest.fetch_cma_distractors --preview 12   # the prose renderings
```

The preview is the one that matters now: it is the first sight of a Cleveland
chunk rendered from `description` rather than from the structured fields, and
whether it reads like a different shape from the Met's is the whole case for the
amendment.

---

# Block B4 — the loader, and seams 1 and 2 stopped on the time-box (2026-08-14)

## The loader

`ingest/load_distractors.py`. Two design points, both forced by numbers rather
than preference:

**It takes `--target-index`, not `--limit`.** The W2b rungs 57 → 150 → 450 are
INDEX SIZES. `BLOCK_B3_DISTRACTORS.md` gives a ~400 total and the plan gives the
rungs, and the pair reads as one load of 400 — which skips the middle rung
entirely. The loader is told the index size to reach and works the rest out
against the live count.

**Tranches are stratified.** Verified on a 300-Met / 80-Cleveland simulation:

```
tranche 1  (57 -> 150)   cma  20   met  73    shortfall 0
tranche 2  (150 -> 450)  cma  60   met 227    shortfall 13
composition               cma 22% / 21%   met 78% / 79%
```

The proportions hold across both rungs, no record loads twice, and the shortfall
is **printed with its consequence named** — "the rung will be 437, not 450" —
because a curve whose rungs are not where they claim to be is not a curve.

One chunk per record, deliberately: these texts are 120–400 characters, under
the chunker's ~1200 threshold, so routing them through it would produce exactly
this and add a dependency for nothing.

The loader also refuses to write a row with `is_distractor` false. The trigger
would stop it anyway — but a loader that depends on a trigger to be correct is a
loader that is wrong and lucky.

## Seams 1 and 2 are stopped, and this is the time-box working

The plan for seam 1 was "the Wikisource route A4 already built". **There is no
such route.** `data/a4_ws_sections.py` is a file of Periplus sections
**hand-transcribed** on 2026-08-13, with its own header saying so:
*"Transcribed 2026-08-13 from el.wikisource.org … Working file for the A4
recovery. Not part of the pipeline."* `scripts/recover_periplus_a4.py` compares
that file against the corpus; it fetches nothing.

So seam 1 needs a Wikisource fetcher that does not exist, and seam 2 needs
Strabo, Pliny and Ptolemy from a source that must be found, licence-checked and
parsed. That is three new acquisition paths, and on this seam's record — four
silent naming no-ops across two museums — it is several more rounds.

**Stopped, per the standing instruction: if a source fights back, drop it and
record the shortfall rather than fixing it.**

### What that costs, stated rather than glossed

The padding is now **English catalogue prose only**. The consequence lands on one
cohort in particular: **12 of the 32 gold pairs target Greek chunks**, and they
will face no competing Greek at any rung. Their ranks may hold up across the
curve for a reason that has nothing to do with robustness — nothing in the index
speaks their language.

So the curve measures **degradation under English competition**. That is a real
result and it attacks the right cohort — `authored` is the strongest at 0.889
and all nine of its targets are English — but it is not the general claim
"retrieval degrades with index size", and B5 must not be read as making it.

### The route back, if it is ever wanted

Not scraping. **Perseus publishes canonical Greek and Latin texts as TEI XML in
public git repositories**, which is a clone rather than a crawl and carries a
stated licence. Strabo, Pliny's *Natural History* and Ptolemy's *Geography* are
all there. That is one acquisition path instead of three, and it would give the
Greek-target pairs something to compete against.

Recorded as the option, not taken now.

## Where Block B stands

```
B1  ranking gold set          done, 32 pairs
B2  baseline                  done, three runs, final at full depth
B3  distractor seams          ruled, decision 3 amended for a second museum
B4  containment               done, 15 assertions / 5 mutations
    fetchers                  Met and Cleveland built; seams 1-2 dropped
    loader                    built and verified offline
B5  the curve                 not started
```

## To run

```powershell
python -m ingest.fetch_cma_distractors --preview 12   # the prose renderings
python -m ingest.fetch_met_distractors --fetch --limit 300
python -m ingest.fetch_cma_distractors --fetch --limit 120
python -m ingest.load_distractors --plan
```

`--plan` writes nothing and prints the tranche composition and any shortfall.
Read it before loading.

---

# Block B4 — the first real fetches, and four defects (2026-08-14)

## Cleveland is what the amendment was for

120 records kept, **all 120 rendered from free-text `description`** — narrative
art-historical prose, not a catalogue skeleton:

> *"The figure watching the stars is believed to be the messenger Zhang Qian
> (died 114 BCE). Legend says he lost his way in the Milky Way, where he met the
> Weaving Maid who gave him a stone from her loom…"*

Nothing like *Title. Culture. Dated X. Medium.* The second collection bought
exactly the shape diversity it was added for. Rejections all named: 407
`not_in_allowlist`, 239 `forbidden_department`, 73 `overlaps_era`, 2 `not_cc0`.

## Four defects, in the order they matter

### 1. The Met fetch died on HTTP 403 and discarded everything it had

`get()` raised on any non-404, so a 403 partway through a 300-record run
escaped to the top and **every record gathered was lost**. The traceback gave no
way to tell "this API is refusing" from "this code is broken".

A 403 from a public open-access API at eight requests a second is throttling or
a bot rule, not a permission problem. `get()` now retries 403/429/5xx with
exponential backoff and then raises `Throttled`, which the fetcher catches to
**write what it has** and report `STOPPED EARLY` with the reason. A refused API
is a reason to stop, not a reason to discard work.

### 2. The padding carried HTML

`<br><br>` and `<em>loom stone</em>` came through into the rendered text. Left
in, the distractors would be the **only material in the index containing
markup** — a signal about provenance rather than content, and precisely the kind
of artefact that makes padding distinguishable for the wrong reason. Stripped,
with entities unescaped.

### 3. The padding was longer than the corpus

```
Cleveland as fetched : min 124  median 619  max 1422
corpus chunks        : min  36  median 416  max 1158
```

Uncapped, the padding would differ from the corpus in **length as well as
content**, and a curve that moved could be reporting either. Capped at
`MAX_CHARS = 1200` — the chunker's own splitting threshold, so no distractor is
longer than the longest chunk the project would ever emit for itself — trimmed at
a sentence boundary, never mid-word.

### 4. A justification in the loader was false, and had been from the start

`load_distractors.py` said: *"These texts are 120-400 characters — under the
chunker's ~1200 threshold — so running them through the chunker would produce
exactly this."* Written from the Met preview, never rechecked, and **false the
moment Cleveland arrived at 1422**.

> The same error as everything else in this block — a claim about a system,
> asserted rather than measured — but this time in a *justification* rather than
> in a guard. Nothing enforced it, so nothing caught it. It is the quietest
> version of the failure: a comment explaining why a check is unnecessary is
> itself an unchecked claim.

The loader now **raises** on any record over `MAX_CHARS` rather than explaining
why that cannot happen. The comment is true by construction instead of by
assertion.

## To re-run

The 120 Cleveland records on disk were written by the old code — they carry HTML
and 18 of them exceed the cap. Re-fetch rather than patch, so the file on disk
is what the current code produces:

```powershell
python -m ingest.fetch_cma_distractors --fetch --limit 120
python -m ingest.fetch_met_distractors --fetch --limit 300
python -m ingest.load_distractors --plan
```

If the Met throttles again it will now keep what it got and say so. Two partial
runs are fine — the loader skips ids already loaded.

---

# Block B4 — both fetches ran; the 450 rung is not reachable (2026-08-14)

```
cma  120 records   len 124-1166 (median 605)   over-cap 0   html 0
met   47 records   len 122-1190 (median 193)   over-cap 0   html 0
                   total 167
```

The cap and the markup strip both hold. Every rejection is named. Cleveland
renders 120/120 from free text; the Met's 47 are catalogue skeletons, so the
padding has two registers as intended.

## The arithmetic

```
rung 150  needs  93 distractors   -> available
rung 450  needs 393 distractors   -> SHORT by 226
max index reachable today: 224
```

**The Met stopped at 47.** It threw HTTP 403 at object 71242 after five backed-off
attempts, having examined roughly seventy objects. The new `Throttled` handling
worked exactly as intended — the 47 were written and reported rather than lost —
but the Met is rate-limiting hard enough that a 300-record run is not going to
complete at the default pace.

**This is not a code defect and not a corpus problem.** Cleveland stopped at 120
only because `--limit 120` said so: it rejected 721 and kept 120 from roughly 840
scanned, a ~14% yield against a collection with tens of thousands of open-access
records. Cleveland can supply as much as the curve needs.

## Two changes, both about not losing work

**`write_records` now MERGES rather than overwrites.** A re-run of a throttling
fetcher previously overwrote its own output, so a second run that died *earlier*
would have silently destroyed the first run's records — the same discard-the-work
defect the `Throttled` handling was added to fix, one level up, and worse because
it would have looked like success. Verified: a deliberately worse third run
cannot shrink the file.

**`--pause` added.** The Met returned 403 at the default 0.12s. `--pause 1.0`
asks more slowly, which is the polite response to a rate limit and costs only
wall-clock.

## The decision this forces

The 450 rung needs 393 distractors and 167 exist. Either:

1. **Top up.** `--limit 400` on Cleveland — it has the material and does not
   throttle — plus a slower Met retry to keep both registers present. Ten to
   twenty minutes of wall-clock, no API spend, and the curve is 57 → 150 → 450
   as planned.
2. **Run the curve at 57 → 150 → 224.** Still three points and a 4x growth from
   the baseline, which can still show shape — linear, cliff or flat — but on
   weaker evidence than 8x, and the rungs must be reported as what they are.

**Not a blocker by the bar set before the run** — the fetch behaved correctly and
nothing about the measurement is corrupted. But the fix is one flag, so the
shortfall is a choice rather than a constraint.

## Also worth noting

Composition after a top-up would be roughly 80% Cleveland. That is fine for the
curve — stratification holds the proportions equal *across rungs*, which is what
the comparison needs — and it means the padding is mostly narrative prose rather
than catalogue skeletons. Given the amendment was made to escape skeleton
uniformity, that is the better way round.

---

# Block B4 — fetching complete (2026-08-14)

```
cma  400 records   median 595   398/400 from free-text description
met  200 records   median 196   no throttling at --pause 1.0
     600 total     450 rung needs 393
```

The Met's second run completed cleanly at the slower pace — 153 added to the 47
carried, no 403. The merge behaved: neither run overwrote the other.

Composition lands at **67/33 Cleveland/Met**, and the length question the mix
raised answers itself at that ratio:

```
corpus            median 433   mean 454
padding at 67/33  median ~450  mean ~470
```

Within a few percent of the corpus on both. At 80/20 it was 22% long. No
engineering was needed — the Met simply had to be asked more slowly.

## Three fixes that came out of the fetching, none of them about distractors

1. **`Throttled`** — a 403 stops the fetch and keeps what it gathered, instead of
   raising to the top and discarding it.
2. **`write_records` merges** — a re-run tops up rather than overwriting, so a
   second run that dies earlier cannot destroy the first.
3. **Progress output, capped backoff, interrupt checkpointing** — a `--pause 1.0`
   run went silent for minutes and had to be asked whether it had frozen. Part 4
   recorded the same lesson on 2026-08-09 ("the backfill prints a line per batch,
   so a slow gateway reports instead of looking dead") and it was not applied
   here until it cost a round trip.

## Closing note on this block

Seam 3 took far more rounds than its value warrants, and the reason is worth
recording without dressing it up: **four separate silent no-ops from hardcoded
remote names** — a renamed Met department, two vocabularies for the same Met
department, a combined Cleveland department, and an unverified Cleveland
allowlist. Each fix was a line. The sequence was not.

The generalisable part: **a name that matches nothing is indistinguishable at the
point of use from a name that matches and finds nothing.** Every one of these was
caught by a probe printing the live vocabulary beside the configured one, and
none would have been caught by review.

The padding itself is the least valuable artefact in Block B. The containment
around it is not — the prune cascade and the translator guard would each have
cost real money or real data — and that part was built first, deliberately.

## The remaining B4/B5 sequence, no further tuning

```powershell
python -m ingest.load_distractors --plan
python -m ingest.load_distractors --target-index 150
python -m ingest.run_embed
python -m ingest.test_distractors
python -m eval.run_ranking_check --with-distractors     # rung 2

python -m ingest.load_distractors --target-index 450
python -m ingest.run_embed
python -m eval.run_ranking_check --with-distractors     # rung 3
```

Four batched embedding requests in total. `test_distractors` now runs with real
distractor rows present, so containment stops being a claim about one synthetic
canary and becomes a claim about live padding.

---

# Block B5 — the curve, and a containment failure that was live for the whole run

## The containment failure, first, because it is the serious one

`ingest/test_distractors.py` went from 15/15 to three failures. Cause:

> **`ingest/run_embed.py` re-applied `scripts/schema-part4.sql` on every run**,
> and that file contains `CREATE OR REPLACE VIEW retrievable_chunks` **without**
> Block B4's `AND NOT is_distractor`. `ingest/run_ingest.py` does the same via
> `db.apply_schema`. Two commands in the standing session ritual silently
> reverted distractor containment.

It fired between the containment suite passing 15/15 and the first embed. From
that moment the **answer path could have cited a distractor**. Nothing ran the
answer path in the window, so no answer was contaminated — but the exposure was
real and lasted hours.

### Nothing detected it, including the check written to detect it

`load_distractors` printed **`corpus chunks unchanged: 151 -> 151  OK`** while
reading the reverted view. Both views returned 151 where they should have
returned 57 and 151. The containment check was reading contaminated data and
reporting success — the `--survey`-on-substrings failure in a new costume, and
the eleventh instance of the standing lesson.

### Three fixes

1. **`db.MIGRATIONS`** — part3, part4, then b4, applied in order, absent files
   skipped. `run_embed` now calls `db.apply_schema` instead of executing part4
   directly. A later migration can no longer be undone by an earlier one.
2. **The guard is asserted directly**, by reading `pg_get_viewdef` and looking
   for `is_distractor`, rather than inferred from row counts. A count assertion
   is satisfied by an empty table; a definition assertion is not.
3. **The canary stops pretending it is outside the pipeline.** It was designed
   vectorless so the test could vectorise it in a rolled-back savepoint —
   and then `run_embed` embedded it for real (`chunks to embed: 94` for 93
   loaded records), which is correct behaviour for an eligible chunk and broke
   the fixture. It is now embedded like any other distractor, and the exclusion
   assertion no longer depends on the absence of a vector.

A sixth mutation proves the definition assertion can fail.

### What this does NOT invalidate

**The curve data stands.** Both ranking runs read
`retrievable_chunks_with_distractors`, which `schema-part4.sql` does not define
and therefore never reverted. The contaminated view was the *baseline* one, and
no ranking run at any rung used it.

The canary is one synthetic chunk inside both elevated rungs — 151 and 450
include it. Recorded, negligible.

## The curve

```
index          57        151       450
recall@6      0.812     0.812     0.812
MRR@10        0.651     0.648     0.648
gapDoc       +0.025    +0.023    +0.020
gapAny       -0.008    -0.009    -0.012
spread        0.146     0.141     0.136
```

**Flat.** Recall does not move at all across an eightfold index. MRR moves by
0.003. The gaps drift by three thousandths. Nothing that would be called
degradation happened.

### Where movement did occur

```
muziris-cargo-akananuru    51 -> 112 -> 309      (of 57 / 151 / 450)
muziris-cargo-papyrus      41 -> 109 -> 109  ... 41 -> 53 -> 109
aksum-trade-adulis         29 ->  29 ->  35
au-khao-sam-kaeo           10 ->  12 ->  17
au-silla-glass         gap .112 -> .097 -> .036
au-shapur-plate        gap .106 -> .106 -> .076
```

Every pair that moved was **already failing at 57 chunks**, or is one of the
English-target `authored` pairs whose gap narrowed. Nothing that was passing
started failing. `muziris-cargo-akananuru` fell from 51 to 309 — it holds its
*relative* depth almost exactly (89% → 74% → 69% down the index), which is what
a chunk with no real signal does as the index grows around it.

### The reading, stated at the size the evidence supports

**Retrieval did not degrade with index size over this range.** But the padding is
**English catalogue prose only** — seams 1 and 2 were dropped — so the twelve
Greek-target pairs faced no competing Greek at any rung, and their flatness is
not evidence of robustness.

What the curve does support: **English-target retrieval survives an eightfold
index of plausibly-similar English competition**, with the `authored` cohort's
gap eroding from +0.055 to +0.045. That is a real result, and it is the cohort
the padding was aimed at.

What it cannot support: any claim about non-English retrieval at scale.

### Against the plan's decision point

> degradation milder than predicted → W3 can move faster, and say so

Degradation is **milder than predicted — it is absent**. On the plan's own rule
that is a green light for W3 to move faster. **It should not be taken at face
value**, for the reason above: the curve tested one language.

---

# Block B closed — starting point for Block C (2026-08-14)

Containment re-verified after the reversion was fixed at source:

```
python -m ingest.test_distractors     16 passed, 0 failed
python scripts\mutate_distractors.py   6/6, schema and sources restored
```

The new mutation — *"retrievable_chunks loses its guard (definition assertion)"*
— proves the direct `pg_get_viewdef` check can fail. Both it and the count-based
assertion are kept: a count assertion is satisfied by an empty table, and a
definition assertion is satisfied by a guard that is present but wrong.

## Block B, complete

```
B1  32 ranking pairs, 7 regions, 8 target languages
B2  baseline recorded three times; final at full depth
B3  three seams ruled; decision 3 amended for a second museum
B4  containment 16/16 and 6/6; 600 distractors fetched, 393 loaded
B5  the curve: flat at 57 / 151 / 450
```

Total spend across the whole block: **eight batched embedding requests.** No chat
calls.

## The handoff

`BLOCK_C_START.md` is the starting point for the next thread. It carries the
measured state, the curve with its two caveats, the four blocking rulings, the
traps this block paid for, and the verification commands.

It exists because `PROGRESS.md` is now ~400 KB and a new thread cannot read it
whole — and because grepping it is not a substitute for reading it. **This block
proved that twice**: A4's line recording the twelve chunks it re-embedded sat
three hundred lines from any term I searched, and the claim that the index had
diverged from the corpus was made against a document rather than a database.

## The one thing the next thread must not inherit uncritically

The curve is **flat**, and the plan's decision rule reads *"degradation milder
than predicted → W3 can move faster, and say so"*. Taken at face value that is a
green light.

It should not be taken at face value. The padding is **English catalogue prose
only**; seams 1 and 2 were dropped on a time-box, so the twelve Greek-target
pairs faced no competing Greek at any rung. The curve supports *"English-target
retrieval survives an eightfold index of similar English competition"* and
supports nothing about non-English retrieval at scale.

And `gapAny` is negative at every rung, including at 57 chunks before any padding
existed. **The quantity W2b was built to watch erode had no positive value to
erode from.** A flat curve over a quantity that started at zero is a weaker
result than a flat curve over a healthy one, and G2's *"score gap wider than
baseline"* criterion is measured against that same near-zero number.

---

# Block C session 1 — C1a, C1b, and the four rulings (2026-08-14)

Ran with the repository mounted read/write from a Claude session that could not
reach the host's venv, Docker or Postgres. So: **every edit below is on disk and
every suite quoted below was run against a partial copy of the tree in a Linux
container, not against the host.** The host runs are still owed, and are listed
at the end. Nothing here was measured against the live index; nothing here needed
to be.

## What was believed going in, and how it turned out

**Believed:** the ruling on multi-target queries takes recall to 26/30 = 0.867.
**Found:** the gold set holds *two* shared queries, not one. Besides Muziris
there is *"How did Chinese sources describe the Roman empire?"* — two pairs, at
ranks 4 and 5, both hits. `claude/phase2-block-c-plan.md` collapsed Muziris and
left that one expanded. Applied to both:

```
per pair, today               26/32 = 0.812
collapse Muziris only         26/30 = 0.867   <- the planned figure
collapse both, consistently   25/29 = 0.862   <- the ruling as made
```

Collapsing the China query removes a unit and a hit, so the consistent ruling is
*lower* than the planned one. At 29 units ≥0.95 permits **at most one miss**, and
four units miss: ranks 11, 15, 17 and 35. **Three of those four must be fixed.**
The ruling makes the gate reachable; it does not reach it, and the two claims
were being run together.

**Believed:** the chunk beating a `translation_case` target is always that
document's own English translation.
**Found:** that is not recoverable from either archived run. `PairResult`
recorded `sim_best_other_chunk` and never which chunk it was, so the claim
existed only as a recollection from B5. It is now recorded — see C-extra below —
and **the effect of ruling 2 on `tc-frankincense-harvest` is therefore unknown
and must not be assumed**. Its `gapAny −0.178` against `gapDoc −0.053` says the
chunk beating it is a sibling in its own document; whether that sibling is §29's
English or §27–28's is exactly what was never written down.

**Believed:** six archived spans are affected by the `cite.py` labelling defect.
**Found:** "six" is prose hardcoded in `ui/index.html`; Block 0's own audit
printed nine `case_only`. The sentence was never derived from the audit beside
it. It is now generated from `span_audit`, and so is the spans total, which was
a hardcoded sum of four state names and would have silently dropped the fifth.

## C1a — `cite.py`'s third match state

`locate_in_text` now returns `Located(start, end, match)`, a NamedTuple so that
`span[0]` and `span[1]` keep meaning what they meant. `match` is `exact` or
`case_folded`; `locate_quote` passes it through instead of hardcoding `"exact"`
on three branches. `QuoteSpan.match` is now `exact | case_folded | normalised`,
and `verify()` adds a note when a quote matched only after folding.

The fallback was never wrong. **The label was**, and the span is exact either way
because `_fold` is length-preserving — which is why this is a naming fix and not
a correctness fix.

`build_ui_data.classify_span` gained a fifth state. It now reads the span's own
`match` rather than only the characters:

- `case_folded` — characters differ only in case, and the span says so. Not a
  defect.
- `case_only` — characters differ only in case and the span claims `exact`. Still
  a defect, and **every run archived before today lands here by construction**.

Archived runs are **not** re-labelled. An archive edited to match today's names
stops being evidence that the defect existed, which is the only thing that
bucket is for. `ui/index.html` renders the new state with its own wording and
`check_ui.mjs`'s tally is accumulated rather than declared as a fixed object —
it was a literal `{resolved, case_only, moved, absent}`, so an unlisted state
would have incremented `undefined` and every comparison against NaN would have
been false. The audit would have failed while naming a count and not the missing
state.

Mutation added to `scripts/mutate_part7b.py`: *"case-folded match recorded as
exact again"* → `GUARD a case-folded match is not recorded as exact`.

## C1b — the `translation_chunk*` rename

```
translation_chunk_id  ->  translation_member_chunk_id   the English chunk retrieval
                                                        returned, or the section's
                                                        first chunk. A MEMBER.
translation_chunk     ->  translation_section           every member merged by
                                                        align._merge. The SECTION.
```

Also `build_passages(translation_chunk_by_chunk=, translation_record_by_chunk=)`
→ `(translation_member_by_chunk=, translation_section_by_chunk=)`, and
`fold_hits`'s `folded` → `members`. The serialised key in new archives changes
with the field; runs archived before today keep `translation_chunk_id`, which
held this same value, and are not rewritten.

A merged section carries its **first member's** chunk_id, so the two agree
whenever the original was the hit and disagree whenever a later member of a split
section was. **Nothing in the suite had ever seen them differ.** A new assertion
in `test_section_alignment` builds that case — hits `g4` and `e4b`, section `e4a`
— and checks that the `Passage` carries both under their own names and that
`to_dict()` names the member it actually stood on.

## C-extra — the ranking run now names the chunk it lost to

`PairResult` gained `best_other_chunk_id` and `best_other_doc_chunk_id`, with an
assertion in `eval/test_ranking_check.py` that each gap names the chunk it was
measured against and that a pair with nothing to compare against names nothing.
Two strings per pair, and ruling 2's premise becomes checkable offline from the
next run rather than remembered.

## The rulings

All four are in `BLOCK_C_RULINGS.md`, with the arithmetic and the cost of each.
In short: (1) a multi-target query is one unit scored on its best acceptable
target, with per-unit coverage reported and the Old Tamil failure printed beside
every G2 number; (2) `translation_case` accepts the document's own published
translation of the *same* section, still a miss on a neighbouring one; (3) gap
pre-rerank, recall post-rerank, reranker-score gap under its own name and never
compared to the baseline; (4) "wider than baseline" reads `gapDoc`, which is
positive at every rung, not `gapAny`, which is negative at every rung.

The fifth item is a task, not a choice: **add an English→Tamil probe with
`lang_pool: non_english` before C3**, one query in a batched request. After
ruling 1 the worst cross-lingual result in the corpus rests on a pair that no
longer counts toward the gate.

## Run on the host before anything else this session says is believed

```powershell
python -m answer.test_answer            # 145 in the container; was 133 in the plan
python -m answer.test_translate
python scripts\mutate_part7b.py         # 15 mutations, was 14
python ui\test_build_ui_data.py
python -m eval.test_ranking_check       # 37; the 37th needs the seed corpus
python scripts\mutate_ranking.py
python -m ingest.test_distractors
python scripts\mutate_distractors.py
python ui\build_ui_data.py --verify     # expect the case_only count UNCHANGED and
                                        # case_folded 0 — no answer has been re-run
node ui\check_ui.mjs
```

In the container all of `answer.test_answer` (145 assertions, 0 fail),
`answer.test_translate`, and all **15** mutations in `mutate_part7b.py` passed
with sources restored. `eval.test_ranking_check` reported 36 passed / 1 failed,
the failure being *"every pair resolves to exactly one chunk of its expected
document"* — the seed corpus was not staged into the container, so that
assertion had nothing to resolve against. It is expected to pass on the host and
its passing is the check that the two new assertions did not disturb the loader.

`case_folded` should be **0** after `--verify`. Anything else means an archived
run was rewritten, which is the one thing C1a must not do.

## Not done, and next

- The rulings are written down but **not yet implemented in the checker**. Unit
  scoring, per-unit coverage, and the `translation_case` acceptable-target set
  are code, tests and a mutation, and they change what the metric means — so
  they get their own session and their own re-measure.
- No re-measure was run and no query was embedded. Spend this session: **zero**.

## Host verification of the above, same day

Run on the host in the venv, against the live tree. Everything the container run
claimed, confirmed — and one number the container could not reach.

```
answer.test_answer                 all passed
answer.test_translate              all passed
scripts\mutate_part7b.py           15/15, sources restored
ui\test_build_ui_data.py           all passed
eval.test_ranking_check            37 passed, 0 failed
scripts\mutate_ranking.py          14/14, sources restored
node ui\check_ui.mjs               all checks passed
```

`eval.test_ranking_check` is the one that mattered: the container reported 36/1
because the seed corpus was not staged into it, so *"every pair resolves to
exactly one chunk of its expected document"* had nothing to resolve against. On
the host it passes, which is the check that the two new `best_other_chunk_id`
assertions did not disturb the loader.

### `build_ui_data.py --verify`, the C1a acceptance test

```
168 claimed character span(s):
  resolved     157
  case_folded    0
  case_only      9
  moved          1
  absent         1
```

**`case_folded 0` is the result C1a wanted.** No archived run was re-labelled;
the nine spans that were a labelling defect are still a labelling defect,
reported as one, with `match='exact'` still on the page beside them. The state
exists and is empty because no answer has been produced since it existed —
which is exactly the shape of a correct archive.

`check_ui.mjs` confirms the tally end to end:
`{"resolved":157,"case_folded":0,"case_only":9,"moved":1,"absent":1}`, and it
confirms it through the accumulating counter rather than the fixed object it
used to be — the old literal would have dropped `case_folded` silently and then
compared a count against NaN.

### The nine are one quotation

Worth writing down, because it explains how "six" ever got into `index.html`:
all nine `case_only` spans are the **same quotation in the same field of the
same record** —

```
eastasia-02-hou-hanshu.reference_translation[391:516]
"the tribute brought was neither precious nor rare, raising suspicion t…"
```

— repeated across nine archived runs of the same question. Nine spans, one
defect, one record, and a prose sentence counting something else again. The
sentence is now generated from `span_audit` and cannot drift from it.

`--verify` still exits non-zero on `moved 1` + `absent 1`. Both are the known
Adulis case: A4's Wikisource recovery replaced the record after those runs were
archived. Unchanged by anything in this session, and the standing argument for
D1's corpus version in every answer.

**All seven G2 checklist items that are code are now landed or measured. The
three that remain are the ruling-dependent ones: recall at 450, the gap, and two
sessions on different days.**

---

# Block C session 2 — the rulings become code (2026-08-14)

Offline only. No query embedded, no re-measure, spend **zero**. The rulings from
this morning were written down; this session makes them executable, which is the
only form in which a ruling can be wrong in a way anybody notices.

## Ruling 1 — the unit is DECLARED, not inferred

Each pair may carry `unit_id`; absent, a pair is its own unit. Two units are
multi-target: `muziris-cargo` (3 pairs) and `china-describes-rome` (2).

The alternative was to group by identical query text, which the checker already
does to set `shared_query`. It was rejected: a denominator inferred from text
nobody declared changes the moment somebody edits a query by a character, and
nothing in the run would look wrong. The loader now asserts **both** directions:

- a unit whose members carry different query text is a load error;
- two pairs sharing query text but declaring different units is a load error.

The second is the silent one. Without it, adding a third pair to an existing
question and forgetting `unit_id` adds a unit to the gate's denominator, and the
only symptom is a slightly different number.

`run_ranking_check.py` now reports at two depths and never one in place of the
other. Per pair, everything means what it meant when B2 was recorded — `rank`,
both gaps, the cohort table — so every run since Block B stays comparable. Per
unit, ruling 1: best acceptable target, plus **coverage**, which is how many of
the unit's targets reached the top 6. Coverage is printed and never gated, with
the reason printed under it.

## Ruling 2 — the alternate is COMPUTED, not copied

A pair carrying `accept_aligned_translation` gets its accepted alternate from
`answer.align.pair_chunks` at scoring time. Nothing is written into the gold
file: a hand-copied alternate is a second copy of a passage that drifts from the
record it came from, which is the chunk-id failure in a new hat.

Admitted **only** where align reports the ground as `section`. On `index` —
both sides merely split into the same number of pieces — nothing is admitted,
because that pairing is a coincidence of counting and accepting on it would
admit a *neighbouring* section, which the ruling says is still a miss. The
ground is recorded per pair either way: "none admitted" and "none asked for"
are different facts about a run.

Scoped as ruled — the four `translation_case` pairs and nothing else, asserted.
And `rank_accepted` sits beside `rank` rather than replacing it. Rewriting
`rank` would have restated every number Block B recorded as though the ruling
had always been in force.

`resolve_alternates` is tested offline against a stub connection. The rule that
decides whether four gold pairs become reachable was otherwise only exercisable
in the session that spends.

## The English→Tamil probe, and the arithmetic getting harder

Added as `probe-tamil-akananuru-en` to both `retrieval_probes.json` and
`ranking_pairs.json` — the second so it is actually measured. Query: *"a Tamil
poem describing Yavana ships arriving at Muciri with gold and departing with
pepper"*, `lang_pool: non_english`, so no English can satisfy it.

```
33 pairs / 30 units.  >=0.95 still permits at most ONE miss (29/30 = 0.967).
```

The probe is **unmeasured** — written after the last run. If it misses, which
its own note expects, G2 needs **four of five** in-window misses fixed rather
than three of four. That is the ruling's arithmetic getting harder because of
an instrument added to watch the thing the ruling stopped counting, and it is
the correct direction.

## Verified in the container

```
eval.test_ranking_check      59 passed, 1 failed (the seed-corpus one; see below)
scripts\mutate_ranking.py    21/21 mutations, sources restored
answer.test_answer           all passed  (align.py is shared and unchanged)
answer.test_translate        all passed  (12 probes load; the pool rule holds)
```

Mutations went 14 -> 21. Three of the seven break the gate's **denominator**
specifically — unit scoring collapsed, a unit scored on its worst target,
coverage counting every target as reached — because that is the one quantity in
this check that decides whether W3 starts, and the plan already got it wrong
once.

## A defect found by the write-back guard, not by a test

Committing `eval/goldset.py` was refused: the file on disk had changed since it
was read. It had — `scripts/mutate_ranking.py` ran on the host in between, and
its restore step rewrote the file with **CRLF** line endings. 29144 bytes on
disk against 28463 read; the difference is exactly one byte per line.

The content is identical. The bytes are not. And the harness's own check —

```python
unrestored = [f.name for f in SOURCES
              if f.read_text(encoding="utf-8") != originals[f]]
```

— cannot see it, because `read_text` translates CRLF back to `\n` on the way in.
**"Sources restored cleanly" is a claim about text, and it reads like a claim
about the file.** All five `mutate_*.py` share the pattern.

Not urgent: `.gitattributes` normalises, and nothing is semantically wrong. But
it is the exact shape of defect this repository keeps finding — a check that
passes because it is measuring a projection of the thing it names. The fix is to
keep the original **bytes** and restore those, comparing bytes at the end;
mutation-time writes can stay as they are, since they are transient.

## To run on the host

```powershell
python -m eval.test_ranking_check       # expect 60 passed, 0 failed
python scripts\mutate_ranking.py        # expect 21/21
python -m answer.test_answer
python -m answer.test_translate
```

`eval.test_ranking_check` reports 59/1 in the container because the seed corpus
was not staged into it and *"every pair resolves to exactly one chunk of its
expected document"* had nothing to resolve against. On the host it should pass
— **and it is now also the check that the new English→Tamil pair resolves**, so
a failure there is a real finding about the probe rather than an artefact.

## Next

C3, the cross-encoder rerank — hosted through the gateway or local, established
before anything is designed around it. The re-measure that gives the new pair
its first rank should be its own session, on its own day, because G2 wants two
measurements on different days and a run made in the same session as the code
that changed the metric is a weak first day.

## Host verification, session 2

```
eval.test_ranking_check      60 passed, 0 failed
scripts\mutate_ranking.py    21/21, sources restored
answer.test_answer           all passed
answer.test_translate        all passed  (12 probes; the pool rule holds)
```

Predicted 60/0 and got it. The assertion that matters most in that run is
*"every pair resolves to exactly one chunk of its expected document"*, now over
**33** pairs: the English→Tamil pair added this session resolves against the seed
corpus, so its eventual rank will be a fact about retrieval and not about a
broken pair.

**Block C is not finished, and the three G2 criteria that remain are the three
that need a measurement to exist.** Nothing in either session today improved
recall or the gap; it made both of them mean something specific, and made the
rulings falsifiable. G2 stands at four of seven:

```
[x] ranking metric over >=20 pairs, baseline recorded before any change   B2
[x] distractor curve to >=450, shape stated                               B5
[ ] known-good in top 6 for >=95% at 450                 25/29 pre-probe; UNMEASURED since
[ ] score gap wider than baseline (gapDoc, ruling 4)     no intervention has run
[ ] measured across >=2 sessions on different days       zero days so far under this metric
[x] cite.py third match state, mutation-verified                          C1a
[x] translation_chunk* rename                                             C1b
```

C3 is the decisive one and the only remaining item with a mechanism: five of the
six original misses are English queries against non-English targets, where there
is no shared vocabulary for a lexical index to recover, and a multilingual
cross-encoder scores query and passage jointly. If C3 plus the rulings does not
clear the gate, C2 is the fallback and after that the honest move is kill
trigger 1 — polish the sourcebook at 24-60 records rather than chase 200.

---

# STOP — the 450-chunk rung has not been measured since containment was fixed (2026-08-14)

The post-ruling re-measure was run at both rungs. **The two runs are identical,
pair for pair, digit for digit.**

```
                              57-chunk run    "450-chunk" run   B5's 450 run
muziris-cargo-akananuru            51               51               309
muziris-cargo-papyrus              41               41               109
aksum-trade-adulis                 29               29                35
au-khao-sam-kaeo                   10               10                17
au-silla-glass  gapDoc          +0.112           +0.112            +0.036
```

The header of the second run says `view=retrievable_chunks_with_distractors
index=450 chunks depth=450`. It ranked against 57.

## The mechanism, read off the source and not inferred

`retrieve/search.py` hardcodes the view:

```sql
FROM retrievable_chunks
```

`search()` takes no view parameter and never has — the file has not been touched
since 2026-08-09, before B4 existed. `run_ranking_check.run()` calls it as

```python
hits = search(conn, vector, k=_search_depth(n_index), langs=p.langs, roles=p.roles)
```

So the run counts one view and ranks another. `index_state()` reads
`retrievable_chunks_with_distractors` and truthfully reports 450; every rank in
the table comes from `retrievable_chunks`, which since the B4 guard was restored
truthfully holds 57. **Both numbers are correct and they are about different
things.** The header is not lying about the view; it is silent about the fact
that the view was never searched.

`scripts/schema-b4-distractors.sql` states the intent in writing:

> The ONLY surface from which a distractor is visible. Read by
> `eval/run_ranking_check.py --with-distractors` and by nothing else, ever.

Nothing has ever read it. The comment describes a design that was never wired.

## What this does to Block B's headline

B5's 450 run produced ranks of 109 and 309. Today's produces 51 and 41 through
the same code path. The code did not change; the CONTENTS of
`retrievable_chunks` did. So B5's curve was measured while
`retrievable_chunks` itself held all 450 rows — that is, **during the
containment reversion**, the `CREATE OR REPLACE VIEW` trap this block already
paid for and recorded.

Stated carefully, because the distinction matters:

- The curve's numbers are **real measurements against 450 chunks**. They were
  not fabricated and the pairs did rank against the padding.
- They were producible **only while containment was broken**. Fixing containment
  at the close of Block B silently removed the ability to measure the rung, and
  nothing said so, because the report prints its denominator from a different
  query than its numerator.
- So the W2b curve cannot be reproduced today, and *"flat over an eightfold
  index"* now rests on runs that cannot be repeated until this is fixed.

**G2's third criterion — "top 6 for >=95% at 450 chunks including distractors" —
is currently unmeasurable.** So is the gap criterion at that rung. C3 is blocked
behind this: a reranker cannot be evaluated at 450 while nothing can rank at 450.

## The guard that was missing, and would have caught it in B4

An unfiltered pair ranked to depth N against a view of N rows must come back
with exactly N hits. At the 450 rung it came back with 57. One assertion:

```python
if p.langs is None and p.roles is None and len(hits) != _search_depth(n_index):
    ...fail loudly, naming both numbers...
```

This is the same defect the block has now found three times in three disguises:
a count-based check reading a contaminated view and reporting OK; a metric named
`not_in_top_20` measured at k=50; and now a report whose denominator and
numerator come from different sources. **The pattern is a label that asserts
something nobody measured.**

## Everything else in the run, which is real

At 57 chunks, and only at 57:

- **Ruling 2 is confirmed, and B5's recollection was right.**
  `tc-frankincense-harvest` went rank **11 -> 1**, and the chunk that had been
  beating it is named for the first time: `arabia-01-periplus::translation::002`
  — the document's own English of §29. The claim that had to be remembered is
  now printed by the run that makes it.
- The other three `translation_case` pairs got `ground=index` and no alternate,
  exactly as the rule requires: single short inscriptions, no section markers,
  and admitting an alternate on positional alignment would accept a neighbour.
- **The English->Tamil probe HIT, at rank 4.** Predicted to miss; it did not.
  But read it with its instrument: `lang_pool: non_english` restricts the
  candidate set to the ~21 non-English chunks, so the probe asks "can an English
  query pick the right non-English chunk out of 21", while
  `muziris-cargo-akananuru` — the failure it was added to watch — competes
  against everything. All five non-English-pool probes rank 1 or 4. **The probe
  is easier than the failure**, and it should not be read as evidence that
  English->Tamil retrieval works.
- Unit recall **27/30 = 0.900** at 57 chunks, three misses: `aksum-trade-adulis`
  (29), `adulis-exports` (15), `au-khao-sam-kaeo` (10). The gate needs 29/30, so
  two of those three. At 450 the number is unknown.

## Two further defects found by this run

1. **`--dry-run` crashes when it prints.** `run()` returns before setting
   `report.aggregate`, and `print_report` reads `report.aggregate["pairs"]` for
   the ALL row: `KeyError: 'pairs'`. Pre-existing — the dry run has presumably
   never been used without `--json`. It printed its one useful line first, so
   nothing was lost, but the free pre-flight check is unusable as documented.
2. **The gap criterion has lost "same pairs".** G2 says *"score gap wider than
   baseline, same pairs"*. The set is now 33 pairs; B2's baseline is 32, and the
   new pair carries `gapDoc -0.098`, which moves the aggregate on its own. Any
   G2 gap comparison must be computed over the 32 pairs that existed at B2, or
   it is comparing two different sets and calling the difference an improvement.

## Next, in order

1. Give `search()` an explicit view, default `retrievable_chunks` so Part 7's
   containment stays true by construction; pass it from `run_ranking_check`.
2. Add the hit-count invariant above, and mutation-verify it.
3. Re-run both rungs. **Only then** is there a post-ruling baseline.
4. Re-state the W2b curve with what is now known about how it was produced.
5. C3 after that, not before.

## The fix (2026-08-14, same day)

Four changes, all offline, no spend.

**1. `search()` takes the view.** `retrieve/search.py` now has an allowlist —
`retrievable_chunks` (the default) and `retrievable_chunks_with_distractors` —
and builds its statement from a template. The name is interpolated rather than
bound, so it is checked against the allowlist rather than trusted: it is a
constant at every call site today and stops being one the moment somebody adds a
flag. `SEARCH_SQL` survives as the default-view statement because
`ingest/test_embed.py` asserts against it (cosine operator matches the HNSW
index, every nullable filter cast at every use, query vector cast twice) — all
four still hold.

**The default matters.** The answer path calls `search()` with no view and
therefore still gets containment for free. Containment is what you get by saying
nothing; the distractor view has to be asked for by name.

**2. `run_ranking_check` passes the view it says it is measuring.**

**3. The invariant, split so it can be watched fail.** `reachability_problems()`
is pure — view, rows, hits in; complaint out — and
`check_search_reaches_the_view()` does the database half by borrowing a vector
the view already holds and ranking it to full depth. One row, no API call, and
it runs **before** the batch: a run that cannot measure what it claims should
fail while it is still free.

It is deliberately NOT behind `--skip-check`. That flag covers "the index does
not match the seed corpus", which a person can knowingly override. This covers
"the numbers would be about a different index than the one they name", which
nobody can knowingly want.

**4. `--dry-run` no longer crashes when it prints.** The cohort loop skipped an
aggregate with no pairs rather than faking one.

```
eval.test_ranking_check      66 passed, 1 failed (the container's seed corpus)
scripts\mutate_ranking.py    23/23 — retrieve/search.py added to SOURCES, since
                             a mutation target the harness cannot reach is a
                             guard nobody has watched fail
answer.test_answer           all passed — the answer path is unchanged
```

The two new mutations are the ones that matter: *"a run no longer checks that it
can reach the index it names"* and *"the searchable-view allowlist accepts
anything"*.

### A prediction for the re-run, recorded before it happens

At a working 450 the three misses should deepen roughly as B5 showed (29 -> 35,
10 -> 17, 15 -> ~20), and the pairs at risk of newly falling out are
`muziris-cargo-periplus` and `china-describes-rome-weilue`, both at rank 5.
Expect unit recall **26/30 or 27/30**, not better.

If it comes back at 27/30 with nothing moved, that is not a relief — it would
mean 393 distractors changed nothing, which is B5's claim arriving a second time
from a run that can now actually be repeated, and the English-only padding
caveat still applies to it.

### To run on the host

```powershell
python -m eval.test_ranking_check              # expect 67 passed, 0 failed
python scripts\mutate_ranking.py               # expect 23/23
python -m ingest.test_embed                    # the SEARCH_SQL assertions
python -m answer.test_answer

python -m eval.run_ranking_check --dry-run     # should print and not crash
python -m eval.run_ranking_check
python -m eval.run_ranking_check --with-distractors
```

The distractor run either produces genuinely new numbers or refuses to start.
Both are acceptable outcomes; the previous behaviour — printing 57-chunk ranks
under a 450-chunk header — is not.

# The 450 rung, measured for real (2026-08-16)

`67 passed, 0 failed`; `23/23` mutations; `ingest.test_embed` and
`answer.test_answer` clean; `--dry-run` prints and exits. The distractor run
did not refuse to start, which means the reachability probe found 450 rows
through the same path the ranking uses.

## The fix reproduces B5 exactly, which settles how B5 was produced

```
                          B5 (2026-08-14)   today   verdict
muziris-cargo-akananuru         309          309    identical
muziris-cargo-papyrus           109          109    identical
aksum-trade-adulis               35           35    identical
au-khao-sam-kaeo                 17           17    identical
```

Four ranks, four exact matches, through a code path that now names its view
explicitly. That confirms the inference recorded above: B5's curve was measured
while `retrievable_chunks` itself held the padding, and it is a real measurement
of 450 chunks. **The curve is restored, not lost** — and for the first time it
is reproducible on demand rather than by accident.

## Recall at 450: 27/30 = 0.900, and NOT ONE PAIR crossed the boundary

```
57  chunks   27/30 = 0.900
450 chunks   27/30 = 0.900
pairs changing recall@6 status between the two rungs:  NONE
```

The three misses deepen — `aksum-trade-adulis` 29 -> 35, `au-khao-sam-kaeo`
10 -> 17, `adulis-exports` 15 -> 15 (unmoved) — and the two Muziris targets fall
to 109 and 309. Nothing in the top 6 moves at all.

The prediction recorded before the run was 26/30 or 27/30: right on the number,
**wrong on the mechanism.** `muziris-cargo-periplus` and
`china-describes-rome-weilue`, both at rank 5, were named as at risk of falling
out. Neither moved by a single place. An eightfold index did not perturb the top
of any ranking; it only pushed the already-failing further away.

## Only four pairs saw any gap change, and every one lost to a distractor

```
probe-tamil-akananuru    +0.054 -> +0.026   best other doc: distractor-cma-149943
tc-nabataean-epitaph     +0.146 -> +0.107   best other doc: __canary__
au-silla-glass           +0.112 -> +0.036   best other doc: distractor-cma-98798
au-shapur-plate          +0.106 -> +0.076   best other doc: distractor-cma-112307
```

29 of 33 pairs are numerically untouched by 393 new chunks. `best_other_chunk_id`
— added two days ago because B5's central claim was unrecoverable from its own
archive — is what makes this readable at all.

## The gap, on the same 32 pairs, measured rather than estimated

G2 says *"score gap wider than baseline, **same pairs**"*, and the set is now 33.
Computed over the 32 that existed at B2:

```
B2 baseline, 57 chunks     gapDoc  +0.0249
today,       57 chunks     gapDoc  +0.0249     identical, two days later
today,      450 chunks     gapDoc  +0.0196
```

Two things follow.

**The measurement is stable.** The same 32 pairs, two days apart, across a
rewrite of the metric that scores them, give a byte-identical aggregate. That is
the strongest evidence so far for the C5-C6 criterion — repeatability is not
being assumed.

**The gap criterion is currently FAILING, and by more than it looks.** 0.0196
against a baseline of 0.0249: the gap at 450 is *narrower*. The criterion is not
merely unmet, it is pointing the wrong way.

## The consequence nobody spotted when ruling 3 was made

Ruling 3 fixed the gap to **pre-rerank embedding similarities**, so that it stays
comparable to the recorded baseline. That was right for comparability, and it has
a consequence that was not stated at the time:

> **A cross-encoder cannot move this number.** Reranking reorders candidates; it
> does not alter cosine similarities. Under ruling 3 as made, C3 can satisfy
> G2's recall criterion and cannot touch its gap criterion, ever.

The only planned intervention that can move a pre-rerank gap is **C2**, hybrid
lexical+dense, because it changes what produces the score. C2 was demoted to
"optional, behind C3, only if still short" in `claude/phase2-block-c-plan.md` and
that demotion was ratified. It now has to be revisited, or the criterion does.

## A second finding: the canary is in the ranked index

`scripts/schema-b4-distractors.sql` says of the containment canary:

> It carries NO embedding, which means it is invisible to both views (they
> require `embedding IS NOT NULL`) and cannot perturb a ranking run. It is a
> containment fixture, not a distractor.

It is inserted with `eligible_for_retrieval = true`, so the next
`python -m ingest.run_embed` embedded it along with everything else. It is one of
the 450 — `BLOCK_C_START.md` even says so, *"393 distractors (one of which is the
canary)"*, and the two documents have contradicted each other since B4 with
nobody noticing. Today it turned up as the **best competing document for
`tc-nabataean-epitaph`**, moving that pair's gapDoc from +0.146 to +0.107.

The claim was true at the instant of the INSERT and false after the next
backfill, and nothing tested it. Same shape as everything else this block has
found: a written claim about behaviour that nobody measured.

**It does not change today's verdict** — removing its effect entirely moves the
32-pair gapDoc from +0.0196 to about +0.0208, still short of +0.0249, and
`tc-nabataean-epitaph` is a hit at rank 2 either way. `retrievable_chunks`
excludes it correctly, so the answer path was never exposed. But a synthetic
sentinel string should not be allowed to define a gold pair's gap before the
gate is assessed, or it becomes something to argue about afterwards.

## G2, as it actually stands

```
[x] ranking metric over >=20 pairs, baseline recorded before any change
[x] distractor curve to >=450, shape stated — and now REPRODUCIBLE
[ ] top 6 for >=95% at 450          27/30 = 0.900; needs 2 of 3 misses fixed
[ ] score gap wider than baseline   +0.0196 vs +0.0249 — narrower, and C3
                                    cannot move it under ruling 3
[ ] measured across >=2 days        one clean day today; stability evidenced
[x] cite.py third match state, mutation-verified
[x] translation_chunk* rename
```

All three remaining misses — 35, 17, 15 — sit inside a top-50 rerank window.
Two of the three are English->Greek, which is the case a multilingual
cross-encoder has a mechanism for; `au-khao-sam-kaeo` is English->English and is
an ordinary relevance failure. **The recall criterion is reachable by C3. The
gap criterion is not.**

## Rulings 5 and 6, both forced by the first working 450 run

**Ruling 5 — C2 returns to the critical path.** Ruling 3 fixed the gap to
pre-rerank embedding similarities, which was right for comparability and means a
cross-encoder can never move it. C2 is the only planned intervention that changes
what produces the score, so it is the only one that can widen a pre-rerank gap.
The plan's demotion of C2 to "optional, behind C3" is withdrawn.

Its cost is stated with it: `tsvector` will not tokenise Literary Chinese, and
five of the six original misses were English queries against non-English targets
where there is no shared vocabulary to recover. **C2 may widen the gap while
doing nothing for recall** — a G2 criterion met, and it must be reported as that
rather than as evidence retrieval improved.

**Ruling 6 — the canary stays a distractor.** It is `is_distractor = true` and
`eligible_for_retrieval = true` by design; a canary held back by eligibility
would prove nothing about the distractor flag, which is the reason it exists. The
false comment is struck from `scripts/schema-b4-distractors.sql` and from
`ingest/test_distractors.py`'s docstring — which asserted the canary carried no
embedding while its own body, forty lines lower, recorded `run_embed` embedding
it for real and the fixture being redesigned around that.

No new assertion: the ones needed were already there and already passing.
Containment held throughout. **Only the prose failed**, and it failed in both
directions on the same day — `BLOCK_C_START.md` counted the canary among the 450
while the schema said it could not be there.

Both rulings are in `BLOCK_C_RULINGS.md`, which is now six rulings, not four.

## Where Block C stands

```
C1a  cite.py third match state                     done, mutation-verified
C1b  translation_chunk* rename                     done
C1c  multi-target ruling + English->Tamil probe    done, implemented, measured
C1d  translation_case ruling                       done, implemented, measured
     -- plus: the view defect, and rulings 5 and 6
C3   cross-encoder rerank                          NEXT. Recall only.
C2   hybrid lexical+dense                          REQUIRED, not optional (ruling 5)
C4   the fold                                      not started
C5-6 two measured days                             one clean day banked (2026-08-16)
```

Next action is the C3 path decision — hosted rerank through the gateway versus a
local cross-encoder on cp314 — which costs reading and no spend, and which the
plan says to settle before anything is designed around it.

# C3 path decision — hosted, through the existing gateway (2026-08-16)

Settled by reading, before anything is designed around it, as PHASE2_PLAN.md C3
requires. No spend.

## Hosted: available, multilingual, and effectively free at this scale

LiteLLM supports Voyage rerank directly. The proxy config is the shape the
gateway already uses:

```yaml
model_list:
  - model_name: rerank-2.5
    litellm_params:
      model: voyage/rerank-2.5
      api_key: os.environ/VOYAGE_API_KEY
```

and the SDK call is `litellm.rerank(model=..., query=..., documents=[...],
top_n=...)`. Four Voyage rerankers are exposed: `rerank-2.5` and
`rerank-2.5-lite` (32K context), `rerank-2` (16K) and `rerank-2-lite` (8K).

**All of them are documented as multilingual**, including 2.5 — "our generalist
reranker optimized for quality with instruction-following and multilingual
support". That matters, because the free allowance is not evenly spread:

```
rerank-2.5, rerank-2.5-lite    200,000,000 free tokens
rerank-2,   rerank-2-lite      no free tokens
```

Had multilingual support been confined to the legacy pair — which the model
table alone suggests, since it names multilingual only for `rerank-2*` — the
free tier and the requirement would have pointed at different models. They do
not. `rerank-2.5` is both.

**Cost arithmetic for this gold set.** A full run is 33 queries against a top-50
candidate window; corpus and catalogue chunks are short, so on the order of
330K tokens per run. Against 200M free that is ~0.17% of the allowance, or
roughly six hundred full runs before a bill. Beyond it, $0.05/M. **C3 costs
nothing at this scale**, which matches the plan's expectation that reranking
adds no chat calls.

It also reuses the key, the gateway and the rate-limit family already in place
for `voyage-3.5` embeddings. One vendor, one budget, one failure mode.

## Local: possible, and not worth it

CPU-only `torch` wheels DO exist for cp314 — 2.9.1+cpu installs on Windows via
plain pip. No CUDA wheels for 3.14 yet, which is irrelevant here: 33 queries by
50 documents is a CPU workload.

So the Part 4 dependency trap is NOT fatal on the torch layer. But a local
cross-encoder needs `sentence-transformers`, `transformers` and `tokenizers` on
cp314 as well, plus a ~600MB multilingual model, and none of that chain is
verified. Against a hosted path that is free at this volume and one config
block away, that is dependency archaeology bought with no gain.

**Ruled: hosted, `voyage/rerank-2.5`, through the existing gateway.**

## Two things to design around, both known now rather than found later

1. **Single-vendor blind spot.** Embeddings and reranking would both be Voyage.
   If `voyage-3.5`'s cross-lingual weakness is what puts `aksum-trade-adulis` at
   35 and `adulis-exports` at 15, a Voyage reranker may share it. A cross-encoder
   scores query and passage jointly rather than comparing two independent
   vectors, so it CAN differ — but shared training data is a real unknown and the
   result must be read with it. **If C3 moves nothing, that is the first
   hypothesis, not a mystery.**
2. **The reranker must respect `lang_pool`.** Five pairs filter candidates to
   non-English before ranking, and that filter is what makes them cross-lingual
   tests rather than same-language tests wearing the label. C3 reranks the
   FILTERED candidate set. Reranking a raw top-50 would quietly restore English
   translations to pools built to exclude them.

## What C3 has to clear, and what it cannot

Three misses, all inside a top-50 window: `aksum-trade-adulis` 35,
`au-khao-sam-kaeo` 17, `adulis-exports` 15. The gate needs **two of the three**.
Two are English->Greek, which is the case a multilingual cross-encoder has a
mechanism for; `au-khao-sam-kaeo` is English->English and is an ordinary
relevance failure.

Under ruling 3 C3 cannot touch the gap criterion. That is C2's, per ruling 5.

Sources: docs.litellm.ai/docs/providers/voyage, docs.voyageai.com/docs/reranker,
mongodb.com/docs/voyageai/models, github.com/pytorch/pytorch issue 169929.

## Handoff

`C3_START.md` is the starting point for the next thread, and is also written to
the project as `claude/c3-start.md` so a new session sees it without being told.
It carries the measured state, the six rulings in one line each, the C3 path
decision with its arithmetic, the three design constraints, the traps this block
paid for, and the verification commands with their expected numbers.

`BLOCK_C_START.md` is superseded and says so in `C3_START.md`: its four rulings
are settled and its claim that the canary "cannot perturb a ranking run" was
wrong. It is kept for its traps, not its state.

**Known debt left behind, deliberately and in one place:** all five
`scripts/mutate_*.py` restore sources with `write_text()`, which on Windows
rewrites LF as CRLF, while the harness's own restore check uses `read_text()`,
which translates it back. "Sources restored cleanly" is a claim about text that
reads like a claim about the file. Harmless under `.gitattributes`; the fix is to
keep the original bytes and compare bytes. Recorded rather than done, because it
is not on C3's path.

## What the C1 sessions cost and produced

Six batched embedding requests. No chat calls. Two G2 checklist items landed and
mutation-verified, four rulings made and implemented, two more forced by the
first working measurement, one defect found that had made the 450-chunk rung
unmeasurable since Block B closed, and three false statements in prose corrected
against the behaviour they described.

The gate did not move: 27/30 before, 27/30 after. **What moved is that the
number now means something specific, and can be reproduced.**

# C3 measured: the reranker fixed one miss and broke two (2026-08-16)

Run: `eval/ranking_runs/20260816T091153+0000-retrievable_chunks_with_distractors-reranked50.json`
`rerank-2.5`, window 50, route `/v1/rerank`, 30 requests, 281,722 tokens,
1,554s of it spent waiting on a rate limit. Every number below is from that
file.

## The number

```
                        pre-rerank        post-rerank
unit recall@6           27/30 = 0.900     26/30 = 0.867
unit MRR@10             0.726             0.778
coverage                28/33 targets     26/33 targets
```

**G2 needs 29/30. C3 moves the gate's number the wrong way.** It is not a
near miss to be tuned; it is a negative result, and it is the honest outcome of
the block's most-expected intervention.

## The three units that changed status

```
au-khao-sam-kaeo       MISS -> hit    17 -> 1
muziris-cargo          hit -> MISS     5 -> 7
china-describes-rome   hit -> MISS     4 -> 7
```

`au-khao-sam-kaeo` was the one **English→English** miss, described in
`C3_START.md` as "an ordinary relevance failure". The cross-encoder fixed it
outright, from 17 to 1. That is the mechanism doing exactly what it was bought
to do.

The two it broke are both **cross-lingual and both `archived_answer`** — an
English query against Greek (Periplus) and against Literary Chinese (Weilue,
Hou Hanshu). Every pair that moved DOWN in this run is in that cohort:
`muziris-cargo-periplus` 5→7, `china-describes-rome-houhanshu` 4→7,
`china-describes-rome-weilue` 5→11, `vimose-runes` 3→6 (still a hit).

## The two cross-lingual misses C3 was bought for

```
aksum-trade-adulis     35 -> 8     twenty-seven places, and not enough
adulis-exports         15 -> 16    nothing
```

Both are English→Greek, and **both targets are in the same document**,
`africa-03-periplus-adulis`. One moved twenty-seven places and the other did
not move at all. That is not a mechanism failing; it is a mechanism working
unevenly within one document, which is a more specific finding and a harder one.

## The single-vendor hypothesis is refuted, not confirmed

`C3_START.md`: *"If C3 moves nothing, that is the first hypothesis, not a
mystery."* C3 moved **11 of 33 pairs**, including one by twenty-seven places and
one by sixteen. The cross-encoder is not echoing the bi-encoder. Whatever is
wrong, shared training data between `voyage-3.5` and `rerank-2.5` is not the
available explanation.

## It separates BETTER and ranks WORSE

```
rerank-score gap, 31 scored pairs     gapDoc +0.1500    gapAny +0.0615
embedding gap,    33 pairs            gapDoc +0.016     gapAny -0.015
```

Ruling 3 forbids comparing these two rows — they are different quantities, and
the second is the only one comparable to B2. **The sign is still worth writing
down.** The cross-encoder is far more decisive about which passage it prefers,
and on three units it decisively prefers the wrong one. Confidence is not
correctness, and a metric that rewarded separation would have called this run a
success.

## What the run could not say, and now can

It recorded that three units fell out of the top 6 and **not what displaced
them** — so "the reranker preferred a different passage" and "the reranker
preferred a wrong passage" were indistinguishable without another twenty-six
minutes of paced calls.

**This is the second time in Block C that a run recorded a number and not the
thing it was measured against.** Ruling 2 was the first, and its fix was
`best_other_chunk_id`. Fixed the same day, the same way: `rerank_top_chunk_ids`
and `rerank_beaten_by` are on every reranked pair, computed from an ordering the
run already holds, at no API cost. The next run answers the question offline.

## G2, as it stands

```
[x] ranking metric over >=20 pairs, baseline recorded before any change
[x] distractor curve to >=450, shape stated — and reproducible
[ ] top 6 for >=95% at 450        27/30 unreranked, 26/30 RERANKED. C3 does not close it
[ ] score gap wider than baseline unchanged, and unchangeable by C3 (rulings 3 and 5)
[ ] measured across >=2 days      one clean day banked, 2026-08-16
[x] cite.py third match state, mutation-verified
[x] translation_chunk* rename
```

**C3 is implemented, measured, and NOT ADOPTED.** `--rerank` is opt-in and `rank`
is untouched, so the 27/30 baseline is undisturbed and every run since B2 is
still comparable. That was the whole point of recording beside rather than over,
and it is the reason a negative result costs nothing to absorb.

## What C3 cost

33 queries in 2 batched embedding requests; 30 rerank calls; 281,722 rerank
tokens, or **0.14% of the 200M free allowance**. No chat calls. The expensive
part was time: 26 minutes, all of it waiting on a 10K TPM ceiling.

## Three claims asserted from documents, all wrong, all corrected by measurement

| claimed | from | true |
| --- | --- | --- |
| rerank is 2000 RPM | Voyage's published table | 3 RPM — that table is for accounts with a payment method |
| a 50-document window is ~4.7K tokens | the seed corpus JSON on disk | ~6.1K, from the index, where 393 of 450 chunks are museum catalogue prose |
| the window is too big for 10K TPM | inference from one failure | it fits; the SPACING was too tight, and the failure could not tell the two apart |

The third was diagnosable only because the failure named a pair and not a call
number. `probe-greek-muziris` is the ninth pair, so seven calls had already
succeeded — a fact that took a gold-file lookup to recover. The run now prints
a line per call and the failure says which call it was.

Pacing is no longer an estimate at all: `--rerank-tpm` spaces each call by what
the provider said the PREVIOUS one cost.

## Traps this session paid for, all four in the tooling and not the measurement

- **The repository has not been committed since Block A2, and
  `eval/run_ranking_check.py` is UNTRACKED.** The file every Block B and C
  number is computed by cannot be restored from version control, and
  `mutate_ranking.py`'s own error message advises exactly that.
- **A mutation harness killed mid-iteration leaves a silent one-word edit.**
  `all(` became `any(` in `build_units` and stayed there; the next harness run
  captured it as *originals* and faithfully restored it. Twice in one day.
- **Never run two mutation harnesses over one working tree.** Both capture
  originals at start and restore at exit, so the second adopts the first's
  mutation as ground truth.
- **A crashed suite reads as "no failures".** The harness reads FAIL lines from
  stdout, so an uncaught exception in any check reports the mutation as
  unwatched AND silently skips every check after it. `run_suite()` now returns
  `SUITE_CRASHED` on a non-zero exit with no FAIL lines, and prints
  *"the suite must FAIL on this mutation, not die on it"*.

## Suites, after C3

```
python -m eval.test_ranking_check      105 assertions   (was 67 at the start of the day)
python scripts\mutate_ranking.py        39 mutations    (was 23)
```

## Next, in order

1. **Re-run `--rerank` once** to collect `rerank_beaten_by` for the two lost
   units. Twenty-six minutes, no code change, and it converts the central
   finding from "C3 lost two units" into "C3 lost two units to these chunks".
2. **C2, hybrid lexical+dense.** Per ruling 5 it is the only planned
   intervention that can move the gap criterion, and C3 has now demonstrated it
   is also needed for recall. Its own gotcha is unchanged: `tsvector` will not
   tokenise Literary Chinese, and five of the six original misses were English
   queries against non-English targets.
3. **Rank fusion is available and must be named as what it is.** Combining the
   embedding rank with the rerank rank (RRF or similar) would plausibly keep
   4→~5 while lifting 35→~12, which is worth more than either alone. **But
   choosing fusion AFTER seeing that replacement scored worse is fitting to the
   gold set**, and if it is done it is declared in advance, with the reason, and
   reported as a tuned result rather than a measured one.

## The repository is committed again (2026-08-16, same day)

`bb3bef5` — 87 files, 51,001 insertions, the first commit since `013ae4a` (A2).
`eval/run_ranking_check.py`, `eval/test_ranking_check.py`,
`scripts/mutate_ranking.py` and `retrieve/rerank.py` are tracked for the first
time, along with all ten archived ranking runs and the distractor fetches. The
trap recorded above — *a killed mutation harness leaves a silent one-word edit
with nothing to restore from* — is closed.

**The first attempt at this commit was wrong and had to be undone.** `git add -A`
took `data/pleiades-places-20260813.json.gz` (129 MB) and `_to_delete/` with it.
Caught at the tip, `git reset --soft HEAD~1`, ignored by name, recommitted. Had
it survived to a GitHub push it would have been rejected on the 100 MB limit and
the fix would have been a history rewrite.

Two rules that follow, because the check that missed it was a check:

- **Ignore upstream dumps by name, not the tree.** `data/pleiades-*.gz` and
  `_to_delete/` are in `.gitignore`; `data/gazetteer.json`, built from those
  dumps, is the asset and stays tracked. The existing comment in `.gitignore`
  already argued this for the seed corpus — it just had not been applied to the
  gazetteer archives.
- **Verify a staged commit by NAME, never by count.** `git status | Measure-Object
  -Line` returned 91 and told nobody anything. `git diff --cached --name-only |
  Select-String "\.gz$"` is the check, and it must print nothing.

# What displaced the two lost units: their own English translations (2026-08-16)

Second reranked run, `20260816T095215+0000-...-reranked50.json`. **Identical to
the first in every rank and to the token — 281,722 both times.** The reranker is
deterministic, and the pipeline reproduces. That is worth having, but it is not
the finding.

## The finding

```
muziris-cargo-periplus      target southasia-02-periplus-muziris::original::003
  rank 5 -> 7, displaced by, in order:
    southasia-01-akananuru-149::translation::000
    arabia-01-periplus::original::001
    southasia-02-periplus-muziris::translation::001
    southasia-02-periplus-muziris::translation::003   <- the SAME SECTION, in English
    arabia-01-periplus::translation::001
    africa-03-periplus-adulis::translation::005

china-describes-rome-weilue   target eastasia-01-weilue::original::000
  rank 5 -> 11, displaced at RANK 1 by eastasia-01-weilue::translation::000
china-describes-rome-houhanshu target eastasia-02-hou-hanshu::original::000
  rank 4 -> 7,  displaced at RANK 2 by eastasia-02-hou-hanshu::translation::000

aksum-trade-adulis            target africa-03-periplus-adulis::original::001
  rank 35 -> 8, displaced by africa-03-periplus-adulis::translation::001 and ::005
```

Across the whole run, of the chunks that outranked a target inside the top 6:

```
::translation::   38
::original::      12
::distractor::     3
```

**The cross-encoder is not wrong. It is matching an English query to English
text, which is the linguistically correct thing to do, and the gold pairs demand
the non-English original of the same passage.** In every one of the four cases
above, the chunk beating the target is that same document's own published
translation — for `muziris-cargo-periplus`, the same section index.

This is the premise of ruling 2, arriving unbidden in a cohort ruling 2 does not
cover. Ruling 2 admits an aligned translation for the four `translation_case`
pairs; `muziris-cargo-periplus`, `china-describes-rome-weilue`,
`china-describes-rome-houhanshu` and `aksum-trade-adulis` do not declare it, and
they lose to precisely the chunk it would admit.

## The temptation, named before it is acted on

**Extending ruling 2 to these pairs would very likely take post-rerank recall
from 26/30 to 29 or 30 of 30, which is G2's recall criterion met.** That is
exactly why it must not be decided from this page. The extension is being
considered because it would rescue a failing gate, and a ruling made on that
basis is fitting to the gold set, not measuring against it — the same trap
already recorded for rank fusion.

There is a real argument FOR it, made on ruling 2's own reasoning: cross-lingual
reach is measured by the four `lang_pool: non_english` probes, where English is
excluded by construction and which all rank 1 both pre- and post-rerank, so
admitting a translation elsewhere does not weaken that instrument. There is a
real argument AGAINST it that is stronger: **if an English translation satisfies
an English query, the gate stops testing non-English retrieval almost entirely**
— every English query could be answered by an English chunk, and 4 units of 30
would be the whole cross-lingual test. Ruling 1 already reached the gate partly
by no longer counting the two hardest targets. This would be the second such
narrowing, and B1's refusal — *"weakening what the metric means"* — applies.

**Unruled. If it is ever made, it is made on the reasoning, applied to the
unreranked configuration as well, re-measured everywhere, and reported as a
ruling change with its cost — never as C3 succeeding.**

## What this does to C2, which is the reason the run was worth 26 minutes

`claude/phase2-block-c-plan.md` and every document since have justified C2 as
follows: *"five of the six original misses were English queries against
non-English targets, where there is no shared vocabulary for a lexical index to
recover."* That sentence is true and it is now clearly the wrong conclusion.

A lexical index over an English query will not merely fail to help the Greek or
Chinese original — **it will boost that document's English translation, which is
the chunk already beating the target.** C2 as specified may move recall the same
way C3 did, and for the same reason.

## The structural problem underneath all of it

The index holds the same passage TWICE — as `::original::` and as
`::translation::` — and the two compete for the same six slots. Three of the six
chunks above `muziris-cargo-periplus` are translations of Periplus sections; one
is the translation of the target's own section.

**A retrieval step that collapsed aligned siblings into one result — one record
per document-section, canonically the original, its translation carried
alongside — would fix all four cases without any ruling change and without any
model.** It is also what the product should do: Mundus Ulterior shows a source
passage with its translation, not two competing rows.

That is a change to what the SYSTEM returns, measured by an unchanged metric —
categorically different from a change to what the metric COUNTS, which is what
extending ruling 2 would be. `answer.align.pair_chunks` already computes the
alignment, and ruling 2 already established `ground=section` as the admissible
standard. The pieces exist.

**Proposed as C2a, ahead of C2, and to be ruled on before it is built.** It costs
no API calls and can be measured against the existing pre-rerank ranks.

# C2a measured: 27/30 -> 28/30, on thirteen sections (2026-08-16)

Run: `20260816T152136+0000-…-collapsed.json`. No reranking, two batched
embedding requests, about a minute.

```
                        uncollapsed       collapsed
unit recall@6           27/30 = 0.900     28/30 = 0.933
unit MRR@10             0.726             0.753
gapDoc (ALL, 33 pairs)  +0.016            +0.016   unchanged, by construction
```

One unit changed status, and it is a large move:

```
adulis-exports    MISS -> hit    best rank 15 -> 3
```

The gaps did not move, exactly as ruling 8 said they could not: they are computed
on the uncollapsed ranking, and collapsing within a document cannot touch
`gapDoc`. **C2a is a recall intervention only. The gap remains C2's.**

## The number that bounds this intervention

```
C2a COLLAPSED  sections=13   chunks 450 -> 437 (removed 13)
roles removed: ['translation']
```

**Thirteen aligned sections in a corpus of 24 documents.** Every removed chunk
was a translation, which is the rule behaving; but the reach of the whole
intervention is thirteen sections, and it converted exactly one miss. It is not
a general fix, it is a specific one, and the gate must not be described as
"retrieval deduplicates its own translations" when what is true is "thirteen
sections deduplicate".

**Open question, and the cheapest next measurement in the block:** how many
documents hold both an `original` and a `translation`, and of those, how many
align on `section` rather than `index`? If most of the rest are `index`-ground,
C2a's reach is bounded by MISSING SECTION MARKERS in the seed corpus rather than
by anything in retrieval — and that is an A-block authoring fix, not a C-block
retrieval one.

## What this sets up, and why the composition is not fitting

Standing after C2a alone: **28/30. G2 needs 29/30 — one unit.** The two
remaining misses are `aksum-trade-adulis` (35) and `au-khao-sam-kaeo` (17), and
the 2026-08-16 rerank runs measured both:

```
au-khao-sam-kaeo     17 -> 1     C3 fixed it outright
aksum-trade-adulis   35 -> 8     C3 moved it 27 places, not enough
```

C3 alone was a net loss because it broke `muziris-cargo` and
`china-describes-rome` — **and the chunks that broke them were their own
documents' translations, which is exactly what C2a removes from the candidate
list before the reranker ever sees it.**

**This composition is not chosen after the fact.** `--collapse` runs BEFORE
`--rerank` in the pipeline, and it does so because that order was ruled and
written into the code when C2a was built, for the stated reason that
deduplicating and then reranking is a pipeline whereas reranking and then
deduplicating hands the cross-encoder the very sibling pair C2a exists to
remove. The composition is the design; the measurement is what is outstanding.

**Next run: `--with-distractors --collapse --rerank --rerank-tpm 10000`.**
Twenty-six minutes. It is the first configuration that could plausibly reach
29/30.

**And if it does, the honest reading is still guarded.** The gate would rest on a
thirteen-section deduplication plus a reranker that is otherwise harmful, on one
day, with the gap criterion unmet and untouchable by either. That is a
configuration to understand before it is a result to bank.

# C2a + C3 together: 28/30, and the bottleneck named (2026-08-16)

Run `20260816T160217+0000-…-collapsed-reranked50.json`. **`waiting=0s`** — the
payment method moved the account to the published 2000 RPM / 2M TPM table, now
MEASURED rather than quoted, and a full reranked run costs seconds instead of
twenty-six minutes.

```
uncollapsed, no rerank      27/30 = 0.900
collapsed only              28/30 = 0.933
collapsed + reranked        28/30 = 0.933
gapDoc, ALL 33 pairs        +0.016  unchanged by both, as rulings 3 and 8 said
```

**G2 needs 29/30. Both interventions together land on the same number as C2a
alone.** C3 swaps which units pass rather than adding any:

```
aksum-trade-adulis   MISS -> hit    35 -> 4   (35 -> 8 without the collapse first)
au-khao-sam-kaeo     MISS -> hit    17 -> 1
china-describes-rome hit  -> MISS    4 -> 7
adulis-exports       collapse got it to 3; the reranker pushed it back to 9
```

`aksum-trade-adulis` at 4 rather than 8 is real evidence the pipeline order
works: collapsing before reranking gave the cross-encoder a cleaner window and
it went four places further. **C3 still nets zero at the gate.**

## Why china-describes-rome still breaks, and what it costs to fix

The chunks above it are unchanged from the rerank-only run:
`eastasia-01-weilue::translation::000` at rank 1 and
`eastasia-02-hou-hanshu::translation::000` at rank 2. Both documents are 1
original / 1 translation on `index` ground, so **ruling 8 does not collapse
them.** The mechanism C2a was built for is exactly right and is switched off for
these two documents by the `sole` gap.

Admitting `sole` — the unambiguous 1:1 case, where "the texts merely split into
the same number of pieces" is vacuous because the number is one — would fold
those two translations into their originals and very probably take the gate to
29/30. It would also fold `southasia-01-akananuru-149`, and **the Old Tamil link
at rank 309 would be reported as found at rank 1** on the strength of its
English. That is the standing failure ruling 1 requires printed beside every G2
number.

## The instrument earned its place on its first run

```
3 pair(s) reached their record VIA THE TRANSLATION, not the original text:
  muziris-cargo-periplus    5 -> 2
  adulis-exports           15 -> 3
  tc-frankincense-harvest  11 -> 1
```

**`adulis-exports` is the single unit C2a converted, and it was reached through
its English.** C2a's +1 is therefore not evidence that the Greek is reachable.
The number and the caveat were produced by the same run, which is the only
arrangement under which the caveat survives.

## The finding that matters more than the gate

The gold set already contains the controlled comparison, and nobody had read it
this way:

```
target                              native-language query   English query
eastasia-01-weilue::original::000   probe-chinese-weilue  1  china-…-weilue    5
southasia-01-akananuru-149::…::000  probe-tamil-akananuru 1  muziris-…-akananuru 309
southasia-02-periplus-muziris       probe-greek-muziris   1  muziris-…-periplus  5
persia-01-skz                       probe-parthian-skz    1
```

**Every non-English target is at rank 1 when the query is in its own language.
The same chunks are at 5, 5 and 309 from English.** The index is not the
problem, the embedding of the passages is not the problem, and the reranker is
not the problem: **the bottleneck is the language of the QUERY.**

Every lever tried in Block C — ruling 2's alternates, C2a's collapse, C3's
cross-encoder, and the `sole` amendment — reaches the gate by finding the record
through its English. None makes the non-English text reachable. That is the one
thing this corpus exists to do.

## What this does to C2, again

C2 was specified as hybrid lexical+dense and has now been undermined twice: a
lexical index would boost the English sibling (C3's evidence), and the misses
are not vocabulary-mismatch failures at all (this run's evidence).

**Proposed instead: C2 becomes QUERY TRANSLATION.** Translate the English query
into the target languages and search with both. It is supported by the four
probes rather than argued from first principles; `answer/translate.py` already
exists; machine translation is named in the project's own scope; and — unlike
C2a and C3 — **it changes what produces the score, so it is capable of widening
`gapDoc`**, which is the whole reason ruling 5 put C2 back on the critical path.

To be designed and ruled on, not started. Its own risks are real: a mistranslated
query is a new failure mode with no baseline, and translating into eight target
languages multiplies queries per pair.

# Ruling 11 lands: 25/30 -> 28/30, and the honest number is 21/30 (2026-08-16)

Run `20260816T162248+0000-…-collapsed.json`. `sole` alone had been a regression
— 28/30 down to 25/30 — because three gold pairs name ENGLISH chunks and the
collapse folded them away:

```
au-hoby-silver      expect_lang en   "Roman silver table service"
au-silla-glass      expect_lang en   "Syrian workshop origin"
au-oc-eo-medallion  expect_lang en   "imitating a Roman aureus of Antoninus Pius"
```

Ruling 11 canonicalises to the record's PRIMARY text, derived from
`source_type`. All three are restored and `adulis-exports` is kept:

```
uncollapsed              27/30 = 0.900     MRR 0.726
collapsed, ruling 11     28/30 = 0.933     MRR 0.834
via the original text    21/30 = 0.700
gapDoc, 33 pairs         +0.016  unchanged, as rulings 3, 8 and 11 all require
sections                 24     roles removed: ['original', 'translation']
```

**No seed record was edited.** `ingest/fidelity.py` has carried `FIND_TYPES`
since Part 3 — *"source types where the record describes an object rather than
carrying text"* — and `classify_translation` already stated that for a find
record the translation field *"is a curatorial description, not a translation"*.
The rule is imported from there and never redefined. It predicts exactly the
three failures, and it was available to be written before the run that exposed
them. The fitting hazard the ruling was accepted under is simply absent.

`probe_sections.py` confirms the assignment is doing something and not
everything: 15 documents hold a translation and **three** carry
`primary=translation` — `hwangnam-glass`, `hoby-treasure`, `oc-eo-medallion` —
which are precisely the find records that have both chunks.

## The number to read is 21/30, not 28/30

Twelve pairs entered their record through a translation-role chunk. Ruling 11
splits them, and the split is the point:

- **nine bypassed a real source text** — Periplus Greek, Weilüe and Hou Hanshu
  Literary Chinese, Old Tamil, the four `translation_case` pairs. Among them
  `muziris-cargo-akananuru`, rank **309 -> 5**, the corpus's one genuinely
  broken cross-lingual link, now finding its record on the strength of its
  English;
- **three have no source text at all** — the find records, where the curatorial
  description IS the record and nothing was bypassed.

The printing conflated these under one heading until this run; it now says which
is which, because calling `au-hoby-silver` a pair that failed to reach "the
original text" asserted something false about a record that has none.

**28/30 is whether the record was found. 21/30 is whether the non-English text
was reachable.** Both travel together, always, per ruling 9.

## Where the gate stands

```
[ ] top 6 for >=95% at 450     28/30 = 0.933. Needs 29/30.
[ ] score gap wider            +0.016 vs +0.0249. Untouched and untouchable by
                               C2a and C3 alike; ruling 10's query translation
                               is the only remaining candidate.
```

The two remaining misses are `aksum-trade-adulis` (35) and `au-khao-sam-kaeo`
(17), and the rerank runs have already measured both at **2** and **1** under
collapse. The three `au-*` pairs that reranking previously destroyed were
destroyed because the collapse had removed their targets; ruling 11 makes those
targets the canonical row, so they should survive. **`--collapse --rerank` is
therefore the next run, and 30/30 is on the table.**

If it lands, the honest report is: 30/30 records found, 21-or-so of 30 source
texts reachable, one gate criterion still unmet, and the recall reached partly
through English on nine units. That is a very different sentence from "G2
passed", and it is the one that goes in the deliverable.

# G2's recall criterion is MET: 29/30 = 0.967 (2026-08-16)

Run `20260816T162515+0000-…-collapsed-reranked50.json`, committed at `695a06b`.

```
                                 recall@6      MRR@10
uncollapsed, no rerank           27/30 0.900   0.726
collapsed (C2a, rulings 8-11)    28/30 0.933   0.834
collapsed + reranked (C3)        29/30 0.967   0.841   <- G2 needs >=0.95
via the original text            21/30 0.700
```

**The two interventions are complementary, and neither reaches the gate alone.**

```
collapse alone fixes   adulis-exports        15 -> 3
rerank alone fixes     aksum-trade-adulis    35 -> 2
                       au-khao-sam-kaeo      17 -> 1
rerank alone breaks    adulis-exports         3 -> 8   (its one cost)
```

Together: 27 + collapse(+1) + rerank(+2, −1) = **29/30**. The single remaining
miss is `adulis-exports`, which the collapse fixes and the reranker undoes.

`china-describes-rome` survives this time — `weilue` slips 5 → 7 but `houhanshu`
holds at 4, and the unit scores on its best target under ruling 1.

## What the number does and does not say

Nine pairs reached a SOURCE TEXT through its English, including
`muziris-cargo-akananuru` at 309 → 5 under collapse and → 39 after reranking.
Three more entered through a translation-role chunk of a record that has no
source text, which ruling 11 correctly does not count as a bypass.

**29/30 is whether the record was found. 21/30 is whether the non-English text
was reachable.** G2 asks the first question. This project exists to answer the
second, and the answer is 0.700.

## An instrument gap, recorded rather than fixed in the same breath

`recall@6 via the original text` is computed on the COLLAPSED ordering, before
reranking. **The adopted configuration is collapse + rerank, so the companion
does not currently describe the configuration the gate passed under.** It is a
pre-rerank number reported on a post-rerank page — exactly the kind of mismatch
ruling 3 exists to prevent, arriving in the instrument built to prevent it.

Fix: compute it a second time on the reranked ordering and print both, named for
where each was measured. Not done in this session, deliberately: the number is
currently conservative in the right direction and nothing depends on it yet.

## G2, as it now stands

```
[x] ranking metric over >=20 pairs, baseline recorded before any change
[x] distractor curve to >=450, shape stated and reproducible
[x] top 6 for >=95% at 450        29/30 = 0.967, collapse + rerank
[ ] score gap wider than baseline +0.016 vs +0.0249. NOT MET, and untouchable
                                  by C2a and C3 alike. Ruling 10's query
                                  translation is the only remaining candidate.
[ ] measured across >=2 days      one day. Runs now take seconds, so this is
                                  cheap — but not until the configuration is
                                  final, and it is not.
[x] cite.py third match state, mutation-verified
[x] translation_chunk* rename
```

**Five of seven. The two outstanding are the gap and the second day, and the
second day is blocked on the gap because C2 will change the configuration.**

## The configuration is now declared, because C5-C6 must measure a fixed one

**Adopted: `--collapse --rerank`.** C3 was a net negative on its own and is not
one in combination — it is the difference between 28/30 and 29/30 — so it earns
its place, and the earlier reading that it should be dropped is withdrawn on
this evidence.

## Suites

```
python -m eval.test_ranking_check      131 assertions   (67 at the start of the day)
python scripts\mutate_ranking.py        50 mutations    (23 at the start of the day)
```

## Next, in order

1. **Does C2a subsume C4?** The runbook's C4 re-examines `align._merge`
   presenting a whole section when one member was retrieved — which is the same
   territory ruling 8 has now ruled on from the retrieval side. If it does, an
   item the plan flags as *"most likely to absorb a week for a null result"*
   closes on an argument rather than a week. Ruling, not code.
2. **C2 as query translation**, per ruling 10. The only remaining candidate for
   the gap criterion, and the only intervention aimed at the 21/30 rather than
   the 29/30.
3. **Fix the companion's measurement point** (above) before any number produced
   under it is reported outside this file.
4. **Then, and only then, C5-C6**: two runs on different days against the frozen
   configuration.

## Handoff

`C2_START.md` is the starting point for the next thread, and is also written to
the project as `claude/c2-start.md` so a new session sees it without being told.
It carries the measured state, the eleven rulings in one line each, what C2 must
clear, four design constraints — including the leakage trap that would
invalidate the whole intervention — the traps this session paid for, and the
verification commands with their expected numbers.

`C3_START.md` is superseded and says so in `C2_START.md`. It is kept for its
traps, not its state.

**What this session cost and produced.** Eight reranked runs and four collapse
runs; ~2.4M rerank tokens, 1.2% of the free allowance, and $0. Assertions 67 →
131, mutations 23 → 50. Five rulings made and implemented. G2's recall criterion
moved from unmet to met, 27/30 → 29/30, by two interventions neither of which
reaches it alone. One companion metric added that no translation-mediated fix
can inflate, and which says the honest number is 21/30. Six defects found in the
tooling that measures all of it, and the repository under version control for
the first time since Block A2.

# C2 is measured and REJECTED: the gap moved +0.0003 (2026-08-17)

_Run `20260817T080300+0000-retrievable_chunks_with_distractors-collapsed-reranked50.json`.
Renderings digest `af427581d957d0ba`, 205 admitted, 0 held._

Ruling 10 named query translation as the only remaining candidate for the gap
criterion. It has now been built, declared in advance, and measured. It does not
work, and the run says so in more than one way.

## The number

```
                    recall@6      MRR@10    gapDoc     gapAny
single-variant      27/33 pairs    0.636   +0.0160    -0.0151
fused               26/33 pairs    0.579   +0.0163    -0.0174

per unit            pre    collapsed  reranked   via original
single-variant      27/30    28/30      29/30       21/30
fused               25/30    26/30      29/30       20/30

GAP     B2 baseline +0.0249    single +0.0160    fused +0.0163
```

## Why it is rejected, and it is not close

1. **The gap did not move.** +0.0160 → +0.0163 over 33 pairs: the fourth decimal,
   and still below the baseline G2 names. `gapAny`, the diagnostic, got **worse**.
2. **Recall fell**, 27/30 → 25/30 pre-rerank and 28/30 → 26/30 collapsed. Both
   arms land at 29/30 only because the cross-encoder rescues the fused arm from
   further back.
3. **`recall@6 via the original text` fell, 21/30 → 20/30.** That is the number
   this project exists to raise, and C2 was the only intervention aimed at it.
4. **Old Tamil went 2/3 → 0/3.** The language C2 was built for, and the one most
   of the session's rendering work went into, is the single language fusion
   destroyed. Every other language held or gained; `grc` went 8/12 → 9/12.

## The mechanism, because it generalises

Max over eight variants raises the ceiling for **every** candidate. A target
gains only where its own-language rendering is good; a distractor gains from all
eight draws. Renderings claimed the target's score for 19 of 33 pairs — and
recall still fell, because the same renderings were lifting distractors faster.

That is not a defect in the renderings and not a defect in the fusion. It is what
max-fusion does to a 450-chunk index where, for any given target, seven of eight
variants are in the wrong language. Ruling 13 was declared before a call was
spent and produced a clean negative. **That is the instrument working.**

## Ruling 15b's control fired on the first run that could trip it

`probe-tamil-akananuru` — a Tamil query against a Tamil target, rank 1 in the
single-variant arm — **fell to rank 14 under fusion**. The control was written
the day before precisely to catch a rendering beating a native-language query,
and it caught it. It is reported, never gated, exactly as ruled.

## The gap criterion has never been measured the way it is written

G2 says *"score gap wider than baseline, **same pairs**"*. The pairs changed:
Block C's fifth item added `probe-tamil-akananuru-en` on 2026-08-14, after the
baseline was recorded, and it is the hardest pair in the set at gapDoc −0.098.

```
gapDoc, all 33 pairs                 +0.0161   (the run prints +0.0160)
gapDoc, the 32 pairs B2 measured     +0.0196
W2b's recorded 450-chunk rung        +0.020
```

**The apparent slide from +0.020 to +0.0160 is the denominator changing, not
retrieval degrading.** It does not rescue G2 — +0.0196 at 450 is still under
+0.0249 at 57 — but the criterion as applied has been comparing two different
pair sets *and* two different index sizes, and only one of those was intended.
Figures reconstructed from the printed table, which rounds to three decimals;
recompute from the archived run before either leaves this file.

## Thirteen rulings, 12–24

Full text and costs in `C2_RULINGS.md`. In one line each:

12. The render language set comes from the **INDEX**, never the pair; the file is
    keyed on query text and holds no pair id, so leakage is not representable.
13. Fusion is **max per candidate**, declared before any call. Exact only because
    `SEARCH_K is None`; `fuse` asserts that and refuses otherwise.
14. Every C2 run reports **both arms**, same index, same day. A fused gap below
    the same-run single-variant arm is not a win, and the report will not say it is.
15b. The rule is **uniform**; the control is an assertion the pipeline can fail.
16. The reranker keeps the pair's **own query text**; the cache keys on the arm
    and the candidate ids, or the fused arm gets the single arm's scores.
17. Script check, query-to-query cosine (reported, never gated), renderings
    archived, and the sentence that travels with every number.
18. **C4 closed** as a ranking item — `_merge` is inert in the harness.
19. Renderings are **frozen data**; the content hash is in every run.
20. Script floor **1.0**; a retry is a different prompt under its own version.
21. Attempts are **additive**; a retry can only improve the file.
22. Temperature is **classified, recorded and opt-in** — never dropped.
23. Uneven sampling recorded (23a); marks judged, not only letters (23b).
24. The verdict is **derived on read**, never trusted from disk.

## G2, as it now stands

```
[x] ranking metric over >=20 pairs, baseline recorded before any change
[x] distractor curve to >=450, shape stated and reproducible
[x] top 6 for >=95% at 450        29/30 = 0.967, collapse + rerank
[ ] score gap wider than baseline +0.0160 vs +0.0249. NOT MET, and there is
                                  now NO INTERVENTION LEFT: ruling 5 settled
                                  that no reranker can move it, and C2 — the
                                  only candidate — has been measured.
[ ] measured across >=2 days      C5-C6, and no longer blocked: the adoption
                                  decision the second day was waiting on is
                                  made.
[x] cite.py third match state, mutation-verified
[x] translation_chunk* rename
```

**Five of seven. C5-C6 takes it to six and does not change the verdict.** The
gate now rests entirely on how its gap criterion is read.

## The configuration is unchanged, and now frozen

**`--collapse --rerank`, exactly as adopted on 2026-08-16.** C2 is not adopted.
`--fuse` stays in the repository, off by default, as a measured negative with 209
assertions and 86 mutations behind it. The renderings file is not read by the
frozen configuration at all, so its digest stops being something to hold still.

## Eight defects in the instrument, found by using it

1. **A test whose failure detail is non-Latin DIED instead of failing.** Through
   a pipe on Windows the child's stdout falls back to cp1252 and `print` raises.
   Invisible at baseline — the detail only prints on failure — so the mutation
   harness saw a crash where there was a caught failure and reported a working
   mutation as unwatched. **Every guard in this repository whose message carries
   Greek, Tamil or Chinese was affected.** Both ends fixed: `check()` escapes
   rather than dies, and the harness forces UTF-8 on the child.
2. **Deleting code by line offset took a neighbouring function with it.**
   `write_atomically` vanished and surfaced as a `NameError` at the moment of
   writing, *after* a correction had been detected and announced. Delete by name.
3. **An inverted log line** printed "kept the earlier attempt" on exactly the
   sixteen rows where the new attempt had won.
4. **A loader that dropped `text`/`ok` made the promotion counter blind**, so a
   computed correction was reported as "nothing to do" and thrown away unwritten.
5. **The reader trusted a stored verdict.** The file said `ok: true` for a
   rendering carrying a Malayalam vowel sign, judged under the pre-23b guard, and
   the fusion would have embedded it. Ruling 24.
6. **A retry at temperature 0 is the same call.** The corrective prompt made Old
   Tamil *worse* on seven of ten rows — and the retry pass overwrote the better
   text, which is why attempts are now additive.
7. **A fixture where the max is the last value tests the word "max"**, not the
   behaviour. Two fusion mutations passed until the fixture was rebuilt so that
   neither first-wins nor last-wins reproduces the answer.
8. **A check that greps a heading passes against a report that prints the heading
   and no rows.**

## Suites

```
python -m eval.test_ranking_check      209 assertions   (131 at the start)
python scripts\mutate_ranking.py        86 mutations    (50 at the start)
```

## Next, in order

1. **C5**: the frozen configuration, today. **C6**: the same command on a
   different calendar day. Nothing on the ranking path may change between them.
2. **The via-original measurement point** — still computed pre-rerank while the
   configuration reranks. It touches the ranking path, so it lands **before C5 or
   after C6, never between**.
3. **Decision 3, the gap criterion**, argued against the recomputed same-pairs
   number and not the current one. Recompute **offline from the archives**, not
   by changing the harness. `C2_RESULT.md` sets out 3a (kill trigger 1), 3b
   (recompute first) and 3c (replace the criterion) with their costs.
   **Recommended: 3b, then 3a or 3c. Do not skip to 3c** — changing a gate after
   seeing the number it failed is the most dangerous move available.

## Handoff

`C5_START.md` is the starting point for the next thread, written to the project
as `claude/c5-start.md` so a new session sees it without being told. It carries
the measured state, the frozen configuration as a literal command, the numbers
C5 must reproduce, rulings 12–24 in one line each, the nine traps this session
paid for, and the sequencing trap above.

`C2_START.md` is superseded. `C2_STATUS.md` is marked superseded in place and
kept for its refuse-list, which stands.

**What this session cost and produced.** ~257 chat calls across three models'
worth of rendering attempts, ~454 embedded texts, 60 rerank requests and 627K
rerank tokens — 0.3% of the free allowance, and $0. Assertions 131 → 209,
mutations 50 → 86. Thirteen rulings made and implemented. A complete
query-translation pipeline built, declared in advance, measured, and **rejected
on its own evidence** — which is the outcome the rulings were written to make
possible. Eight defects found in the tooling that measures all of it, one of
which had been silently unwatching guards across the whole repository. G2 is
unchanged at five of seven, and the gap now has no intervention left.

# Decision 3b, and RULING 25: G2's gap criterion has FAILED (2026-08-17)

_Recomputed at full precision from the archived run JSONs. No harness change, no
calls, nothing on the ranking path touched. Full text in
`C5_3B_AND_PROTOCOL.md`._

The previous section closed with decision 3 open and recommended 3b — recompute
the gap the way the criterion is written, on the pairs the baseline measured,
offline from the archives — before ruling on it. That was done first, and the
ruling was made on the corrected number and not the printed one.

## 3b: the gap on the pairs B2 actually measured

```
                                       run                            n   gapDoc      gapAny
B2 baseline, 57 chunks                 20260814T084042               32   +0.024927   -0.008360
W2b 450-chunk rung, same pairs         20260814T133556               32   +0.019586   -0.012406
frozen config, 450 chunks, same pairs  20260817T080300 single-arm    32   +0.019622   -0.012452
frozen config, 450 chunks, all pairs   20260817T080300 single-arm    33   +0.016047   -0.015056
```

The pair sets differ by exactly one member, and it is the one the previous
section named: `probe-tamil-akananuru-en`, gapDoc **−0.098380** at rank 4, worth
**−0.003575** on the mean. `C2_RESULT.md`'s reconstruction was right to four
decimals — **+0.0196 is +0.019622** — and the apparent slide from W2b's recorded
+0.020 is confirmed as the denominator changing rather than retrieval degrading:
the 450-chunk rung on B2's own pair set reads +0.019586, and +0.020 is that
number rounded.

## Ruling 25 — 3a. The criterion fails on its own arithmetic

```
G2 asks     450-chunk gapDoc, same pairs   >   B2 baseline
measured                        +0.019622  <  +0.024927
short by                        0.005305      = 21.3% of the baseline
```

**Kill trigger 1 is pulled. W3 does not start.** The sourcebook is polished at
24–60 records rather than chased to 200, exactly as `PHASE2_PLAN` pre-declared
before any of this was measured.

What the ruling costs, stated here so it is not discovered later: W3 does not
happen, and **`recall@6 via the original text` stays where it is with no
intervention left aimed at it** — ruling 5 settled that no reranker moves the
gap, and C2, the only remaining candidate, was measured on 2026-08-17 and
rejected.

**3c was not taken, and the argument for it is recorded rather than used.** 3b
strengthened the *measurability* half of a 3c case — the 450-chunk rung on B2's
pairs read +0.019586 on 08-14 and +0.019622 on 08-17, agreeing to four decimals
across three days and a harness rewrite — and the *legitimacy* half not at all.
Changing a gate after seeing the number it failed remains the most dangerous
move available, and it was not made. Anyone reopening this must argue from the
W2b curve's shape, recorded before any of this, and must keep the reading below
beside the new one.

## Both readings travel together, permanently

```
gapDoc, all 33 pairs, 450 chunks     +0.016047     the run prints this
gapDoc, B2's 32 pairs, 450 chunks    +0.019622     the criterion asks for this
B2 baseline, 32 pairs, 57 chunks     +0.024927
```

Neither number may be published without the other, and neither without the index
size beside it.

## C5–C6 still run, and the reason is not ceremony

The verdict is settled, so a reader may reasonably ask why two more days of
measurement were spent on it. Because a criterion that fails **alone** is a
stronger record than one that fails with a second criterion still unknown. C5–C6
takes G2 from five of seven to six of seven and isolates the failure to exactly
one line of the checklist.

## Two hazards found in the archive while doing it

Both are in `C5_3B_AND_PROTOCOL.md` §3–4 in full.

1. **The ranking path was uncommitted for two days and unprovable until
   `bff0605`.** The code that produced the 08-17 run existed only as
   working-tree state: `eval/run_ranking_check.py` was 3,557 lines against HEAD,
   with `retrieve/render.py` and `retrieve/fuse.py` untracked. C5 and C6 require
   that no code on the ranking path moves between the two days, and nothing
   could have proved it — an editor autosave, a stash, a partial revert or a
   `git checkout` of one file between them destroys criterion 5 **silently**. A
   commit changes no file content, so it is not a change on the ranking path; it
   is the only thing that makes two days provably one configuration. Committed
   before C5 as `bff0605`.

2. **`20260814T144013` reports `index_chunks=450` and did not search it.** It is
   byte-identical to the 57-chunk run of the same minute on all 33 pairs —
   `sim_target`, `sim_best_other_doc`, `sim_best_other_chunk`, `rank` and
   `top_doc`, zero differences. Adding 393 distractors cannot change nothing.
   The distractors were reachable earlier the same day: the 13:35 run on the
   same view moved gapDoc from +0.024927 to +0.019586 and changed
   `sim_best_other_doc` on 4 of 32 pairs. `check_search_reaches_the_view`, which
   asserts `n_hits == n_index` and refuses otherwise, landed in **bb3bef5 on
   2026-08-16 — after this run** — so the guard already covers C5 and C6 and
   this is an archival caveat, not a live defect. Two things travel with it:
   **`20260814T144013` must never be cited as a 450-chunk measurement** (W2b's
   450 rung is the 13:35 run, which is what 3b uses), and **`index_chunks`
   records the view's row count, not what the search reached** — the number in a
   run header is not self-validating, the guard is what validates it, and
   `--skip-check` is refused by the frozen configuration for exactly that
   reason.

---

# C5 and C6: two days, one tree, and the same number to the bit (2026-08-19 / 2026-08-20)

_`eval/ranking_runs/20260819T102211+0000-…-collapsed-reranked50.json` and
`20260820T151200+0000-…-collapsed-reranked50.json`, both at tree `bff0605`.
Judged against thresholds written in `C5_3B_AND_PROTOCOL.md` §2 **before C5
existed** and not retuned since. Full verdicts in `C5_RESULT.md` and
`C6_RESULT.md`; the runbook C6 was fired from is `C6_RUNBOOK.md`._

## C6 is not "within tolerance" — it is identical

Every threshold was written expecting drift, and there is none to measure:

```
config fields on the abort list                    0 differ
unit-aggregate fields (all 24)                     0 moved
rank changes, pre / collapsed / reranked           NONE, at any stage
per-pair sim_target,  bit-for-bit                  0 of 33 differ
per-pair sim_best_other_doc, bit-for-bit           0 of 33 differ
rerank tokens                                      310185  =  310185

gapDoc, 33 pairs        +0.015946701  ->  +0.015946701   d = 0.000000000
gapAny, 33 pairs        -0.015152071  ->  -0.015152071   d = 0.000000000
gapDoc, B2's 32 pairs   +0.019534956  ->  +0.019534956   d = 0.000000000
```

The gated integers, restated because they are what the criterion reads:

```
recall@6 per unit    pre 27/30 0.900   collapsed 28/30 0.933   reranked 29/30 0.967
recall@6 via the original text         21/30 = 0.700     <- pre-rerank; see the next section
coverage             pre 28   collapsed 30   reranked 29   of 33 targets
```

The tree was verified **without touching it** — blob hash against the committed
blob, so no `git status` and no index lock. `HEAD` `bff0605` unchanged;
`run_ranking_check.py`, `ranking_pairs.json`, `retrieval_probes.json`,
`search.py`, `collapse.py`, `rerank.py`, `fuse.py`, `render.py` and `embed.py`
all UNCHANGED.

Two runs, two calendar days, one provably identical tree, one identical number
to seventeen decimal places. **That is criterion 5 satisfied at the strongest
level it can be.**

## C5 moved, and every part of the movement closes exactly

C5 is judged against the 08-17 single-variant arm, and three units moved a rank,
none across a gate:

```
unit                        pre-rerank   collapsed   effect on a gated figure
probe-tamil-akananuru-en      4 ->  5      4 ->  5   none - still recall@6
aksum-trade-adulis           34 -> 35     11 -> 10   none - a miss either way
au-khao-sam-kaeo             17 -> 16     16 -> 15   none - a miss either way
```

The whole MRR delta is those moves and nothing else, to the last decimal with no
residual: pre-rerank 0.726111 → 0.724444 is `probe-tamil-akananuru-en` alone at
−0.05/30; collapsed 0.830556 → 0.832222 is that pair plus `aksum-trade-adulis`
crossing the rank-10 boundary at +0.10/30. **The reranked stage — the one G2's
recall criterion reads — did not move at all, in any figure, to six decimals.**

## The embedding-régime note, which is new and must not be lost

`C5_3B_AND_PROTOCOL.md` §2 asserted that `voyage-3.5` does not return a
bit-identical vector for identical text across calls. **That was inferred from
two runs and it is wrong.** Traced on `probe-greek-muziris` across every archived
run:

```
run              pairs   embedding call                probe-greek-muziris sim_target
20260814 08:40    32     32 queries,  1 request        0.63747713789207683
20260814 13:35    32     32 queries,  1 request        0.63747713789207683
20260814 14:40    33     33 queries,  2 requests       0.63747713789207683   <- different shape, same vector
20260816 07:36    33     33 queries,  2 requests       0.63747713789207683
20260816 16:25    33     33 queries,  2 requests       0.63747713789207683
20260817 08:03    33    235 texts,    8 requests       0.63969614269161401
20260819 10:22    33     30 texts,    1 request        0.63903526300402180
20260820 15:12    33     30 texts,    1 request        0.63903526300402180   <- C6 reproduces C5 exactly
```

Seven runs, five sessions, three calendar days, two index sizes and two gold-set
sizes — **byte-identical to seventeen decimal places** — then two régime changes,
one at or before 08-17 and one at or before 08-19, and bit-identical again across
C5 and C6.

**Batch composition is refuted as the cause**: 32-queries-in-1-request and
33-in-2 return the same vector. Nothing in the repository explains it either —
no query cache exists (`vector_of` and `rerank_cache` are both built per-run),
`gateway/config.yaml`'s only edit is the additive `chat-strong` alias, the index
is unmoved at 450/450/0 with identical `collapse_stats` and `chunk_id_drift`,
and `ranking_pairs.json` has not changed since 08-14. **The remaining
explanation is provider-side, and it is recorded as an open observation, not a
finding.**

What must travel with future numbers:

```
within a régime      comparisons are EXACT           C5 = C6, to the bit
across a régime      aggregate gapDoc floor  ~1e-4
                     per-pair gapDoc floor   ~2e-3
```

**B2's baseline +0.024927 was measured in the old régime and C5–C6's +0.019535 in
the new one, so the gap criterion's comparison spans a boundary.** It does not
rescue the gap and does not disturb ruling 25 — the deficit is **0.005392** and
the drift is **~1.6% of it**, two orders of magnitude too small to matter. It
belongs beside the number anyway, because every future comparison in this
repository against a pre-08-17 figure carries that floor and nothing else in the
archive says so.

## The criterion earned its keep, and here is the evidence

`C5_START.md` abbreviated criterion 5 to *"measured across ≥2 days"*. The full
wording at line 9229 is *"≥2 **SESSIONS** on **DIFFERENT DAYS**"* — the
abbreviation dropped a word and the dropped word is the stricter one. The
rationale, written 2026-08-14 before any of this was measured, is at line 9199:
a run made in the same session as the code that changed the metric is a weak
first day. So the criterion is not testing arithmetic stability, which a second
run an hour later would test; it is testing whether the number survives the
environment changing underneath it. **The withdrawn determinism claim above is
exactly that failure caught in miniature, and a second run of C5 an hour later
could not have surfaced any of it.**

The two run JSONs are the evidence for criterion 5 and are committed in
`744e57c`, together with `C5_3B_AND_PROTOCOL.md`, `C5_RESULT.md`,
`C6_RUNBOOK.md`, `C6_RESULT.md` and `C7_START.md`.

---

# The sequencing trap is fixed: via-original is measured at both points (2026-08-20)

_Ruled **after C6** so that no code on the ranking path could move between the
two days. C6 was archived first; this landed second; the two-day window was
closed before a line changed._

## What was wrong

`recall@6 via the original text` was computed **PRE-rerank**, in `apply_collapse`
on the collapsed ordering, while the adopted configuration **reranks**. The
report printed recall at 29/30 post-rerank and via-original at 21/30 pre-rerank
on the same page, with nothing to say the two were measured at different points.
They were not the same measurement and the page read as though they were.

## What made the fix cheap, and why no new computation was needed

**The collapse runs BEFORE the rerank and emits one row per section.** So
`collapse_entry_role` is fixed at collapse time and the reranker cannot change
which member of a section surfaced first — there is exactly one row per section
left for it to reorder. The reranker can rescue a record into the top 6; it
cannot change how retrieval reached it. The fix is therefore the **same
predicate** evaluated against the post-rerank recall column, and `apply_rerank`
gained no entry-role logic at all.

## The shape

`PairResult.recall_at_6_via_original_reranked` is a **new field under a new
name**, exactly as `rank_reranked` never overwrote `rank`. Every archived run
holds the pre-rerank figure, and a run that replaced it would be incomparable to
all of them. `UnitResult` gains the same field, gated on `reranked` as the
existing one is gated on `collapsed`; the aggregate gains
`recall_at_6_via_original_reranked` and `…_n`; and the report prints **both
lines, labelled with their measurement point**.

## Ruling 26 — the two via-original keys are emitted from the COLLAPSE block

The entry role the predicate reads is a fact the **collapse** produces. A run
with `--rerank` and no `--collapse` has no entry role for the bypass clause to
fire on, so the post-rerank figure would come out **exactly equal to post-rerank
recall** — 29/30 published under a name that says something else. Both keys are
therefore emitted from the collapse block, the post-rerank one additionally
conditional on rerank:

```
uncollapsed run              NEITHER figure is reported
collapsed, not reranked      the pre-rerank figure alone
collapsed and reranked       both, printed side by side and labelled
```

No archived run has the rerank-only shape and the frozen configuration cannot
produce one. The ruling exists because the harness allows it and a number that
cannot be produced today is still a number the code would publish.

## The result, and the two near-misses that are the whole test

Computed offline from C6's archive **before the code was written**, so the fix
had a target it had to hit rather than a number it was free to produce:

```
via-original, PRE-rerank    21/30 = 0.700      what the harness printed
via-original, POST-rerank   22/30 = 0.733      what it prints now
```

Exactly one unit changes, and the two units that must NOT change are the test:

```
unit                  entry role   primary role   coll rank   rr rank   changes?
au-khao-sam-kaeo      None         translation       15          1      NO -> YES
aksum-trade-adulis    translation  original          10          2      no, and must not
adulis-exports        translation  original           3          7      no, and must not
```

`aksum-trade-adulis` is rescued by the cross-encoder from 35 to 2 and **still
does not count as via-original**, because its entry was the translation and its
record's primary is the original — that is a bypass whatever the reranker does.
**A fix printing 23/30 has dropped the primary-role clause; a fix printing 21/30
has not taken effect. 22/30 is the only correct answer.**

## The verification run, and the proof that the fix is additive

`20260820T161457+0000-…-collapsed-reranked50.json`, the frozen command on the
patched tree. **It is not a third day and must never be cited as one** — same
calendar day as C6, and a changed tree. It exists to verify the fix and nothing
else; criterion 5 was already met by C5 and C6 and does not depend on it.

What it proves is that the change is purely additive, checked field by field
against C6:

```
config fields on the abort list                    0 differ
pairs differing on ANY pre-existing field          0 of 33
unit-aggregate fields moved                        NONE of the 24
keys added                recall_at_6_via_original_reranked, ..._n
keys removed              none

recall@6 VIA THE ORIGINAL TEXT   pre-rerank 0.700 (21/30)   ->   POST-rerank 0.733 (22/30)
```

Every rank, both similarities, both gaps, the collapse stats, the rerank token
count: unchanged. **The harness gained a column and moved nothing.** That is the
strongest available evidence that 22/30 is the same measurement corrected, and
not a new measurement.

## What the mutation harness caught in the fix's own tests

The first C7 run of `mutate_ranking.py` reported one MISS, and it reported it as
possible list drift. It was not drift — it was a single mutation paired with the
wrong guard, and the pairing was wrong because of a real misreading:

**Dropping `and collapse_primary_role == "original"` makes the predicate
STRICTER, not looser.** It removes ruling 11's exemption for records with no
source text, so the guard that fails is *"a rescued record with NO source text
does count as via-original"* — not the English-bypass guard it was filed under.

Two things follow, and the second is the one worth keeping:

1. The guard was re-pointed.
2. **The English-bypass guard had no mutation behind it at all.** The two
   clauses of the predicate need two mutations, and only one had been written.
   A guard nobody has watched fail is worth what no guard is worth — which is
   the sentence this harness exists to enforce, and it enforced it on the
   session that added the guard. The fifth mutation, *"the post-rerank predicate
   stops recognising a translation entry"*, is the analogue of the pre-rerank
   *"a record reached via its translation counts as via-original"* and it now
   watches that guard.

Mutations 86 → 91, not 90.

## What the fix does NOT do

**29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT
was reachable.** The second number moved by one unit because the measurement
point was corrected, not because retrieval improved: `au-khao-sam-kaeo` was
always rescued by the reranker and the harness was always looking at the wrong
column. No text became reachable that was not reachable before.
`muziris-cargo-akananuru` still sits at rank 310, the corpus's one genuinely
broken cross-lingual link, not counted toward the gate.

---

# Block C closes (2026-08-20)

## G2 — six of seven, and the failure is isolated

```
[x] ranking metric over >=20 pairs, baseline recorded before any change    B2
[x] distractor curve to >=450, shape stated and reproducible               W2b
[x] top 6 for >=95% at 450                       29/30 = 0.967
[ ] score gap wider than baseline                +0.019535 vs +0.024927    FAILED, ruling 25
[x] measured across >=2 sessions on different days    C5 2026-08-19 / C6 2026-08-20
[x] cite.py third match state, mutation-verified                           C1a
[x] translation_chunk* rename                                              C1b
```

**The gap is the sole remaining failure, with nothing else unmeasured beside
it.** Kill trigger 1 is pulled and W3 does not start.

## The configuration, unchanged and frozen

```powershell
python -m eval.run_ranking_check --with-distractors --collapse --rerank --rerank-tpm 2000000
```

No `--fuse`. No `--skip-check`. ~90 seconds, ~30 rerank requests, ~310K tokens.
`--rerank-tpm 2000000` is pacing only and cannot move a number; without it two
archived runs took 27 minutes, of which 1,553s was rate-limit waiting.
`gateway/config.yaml`'s `chat-default` (haiku-4-5, greedy) must keep serving
Part 6 and Part 7 — repointing it makes every archived number incomparable.

## Suites

```
python -m eval.test_ranking_check      218 assertions   (209 at the start of C7)
python scripts\mutate_ranking.py        91 mutations    (86 at the start of C7)
```

Not re-run this session: `ingest.test_distractors`, `mutate_distractors`,
`answer.test_answer`, `answer.test_translate`, `mutate_part7b`,
`ui\test_build_ui_data.py`, `ui\check_ui.mjs`.

## The four traps this block paid for, carried forward

The first three have cost this repository a session each and all three were live
for a thread editing `run_ranking_check.py`.

1. **A test whose failure detail is non-Latin DIED instead of failing** — through
   a pipe on Windows the child's stdout falls back to cp1252 and `print` raises.
   Both ends are fixed, but any new assertion whose message carries Greek, Tamil
   or Chinese re-enters this territory. Every assertion added in C7 is Latin-only
   for that reason.
2. **Deleting code by line offset took a neighbouring function with it.**
   `write_atomically` vanished and surfaced as a `NameError` at the moment of
   writing. **Edit by name.** Every C7 edit was an exact string replacement
   required to match exactly once, refusing the whole file otherwise.
3. **A check that greps a heading passes against a report that prints the heading
   and no rows.** C7 added a report line, and the assertion on it reads the two
   VALUES — `(2/5)` and `(3/5)` on one line — never the heading.
4. **A fixture where the two figures agree tests nothing.** The via-original
   fixture is built so the pre-rerank and post-rerank aggregates come out
   different — 2/5 and 3/5 — or a report printing one number twice would pass
   for a report printing both. This is trap 7 of the previous block, the fixture
   whose max was its last value, in its new clothes.
5. **A guard added in the same session as its mutation can still be unwatched.**
   C7's English-bypass guard had no mutation behind it until the harness said
   so, because the mutation written for it broke a different guard. **A
   predicate with two clauses needs two mutations**, and pairing one mutation
   with the guard you expected rather than the guard that fired is how a
   half-watched predicate looks from the outside.

## What this block cost and produced

Ruling 25 made on the recomputed number and kill trigger 1 pulled. Two runs on
two calendar days over one provably identical tree, byte-identical across all 33
pairs, both similarities, every rank, every aggregate and the rerank token count.
The determinism claim in `C5_3B_AND_PROTOCOL.md` §2 withdrawn and replaced with
a measured régime note. Two archival hazards found and written down. The
sequencing trap fixed with ruling 26 beside it, verified against a target
computed from the archive before the code was written, and proved additive
field by field against C6. Assertions 209 → 218, mutations 86 → 91 — the
ninety-first because the harness caught a guard of C7's own that nothing was
watching.

## Next

**The sourcebook, at 24–60 records.** W3 does not start.

## The sentence that travels with all of it

**C5 and C6 measured a stable pipeline. They did not measure a solved problem.**
The W2b curve still rests on **English-only padding** — seams 1 and 2 were
dropped on a time-box, so the twelve Greek-target pairs faced no competing Greek
at any rung, and *"flat over an eightfold index"* still means *"English-target
retrieval survives English competition"*.

---

# State at the close of C7 (2026-08-20)

_A separate section because of a plain ordering fact: the three Block C sections
above were written into the commit that contains them, so none of them can name
it. This one is written after `ccca17e` and names it._

## The tree

```
ccca17e   C7: the via-original sequencing fix (21/30 pre-rerank, 22/30 post),
          ruling 26, Block C closes
744e57c   Block C: C5 and C6 run archives, ruling 25 documents, G2 at six of seven
bff0605   Block C: C2 measured and rejected, rulings 12-25; frozen config for C5-C6
```

Five paths in `ccca17e`, and no others:

```
M  PROGRESS.md
M  eval/run_ranking_check.py
M  eval/test_ranking_check.py
M  scripts/mutate_ranking.py
A  eval/ranking_runs/20260820T161457+0000-...-collapsed-reranked50.json
```

Working tree clean. **The ranking path is committed and provable** — which is
the first of the two archival hazards recorded above, closed.

## The numbers a later thread will want without reading for them

```
corpus      24 documents / 59 chunks / 57 retrieval-eligible
index       450 in retrievable_chunks_with_distractors, 450/450/0 pending
gold set    33 pairs over 30 SCORED UNITS, 7 regions
suites      eval.test_ranking_check  218   |   scripts\mutate_ranking.py  91
G2          six of seven; the gap is the sole failure, ruling 25
recall@6    29/30 = 0.967, post-rerank, per unit
via-orig    21/30 pre-rerank and 22/30 post-rerank — both printed, both archived
```

Three ranking runs are archived from C5 onward and **only two of them are
evidence**:

```
20260819T102211   C5   criterion 5, day one
20260820T151200   C6   criterion 5, day two; byte-identical to C5
20260820T161457   C7   the fix's verification, and nothing else. NOT a third
                       day: same calendar day as C6, and a changed tree.
```

## One loose end, named here so it is not lost

**Rulings 25 and 26 are not in the rulings register.** `BLOCK_C_RULINGS.md`
carries 1-11 and `C2_RULINGS.md`'s last heading is ruling 24. Ruling 25 lives in
`C5_3B_AND_PROTOCOL.md` and in the C5-C6 section above; ruling 26 lives in
`C7_RESULT.md` and in the C7 section above. A thread told to read "rulings 1-24"
in the register will read exactly that and miss the two most recent — one of
which **pulled a kill trigger**. Register both before any Block D document
quotes a ruling number at anything.

## A trap re-tested, and not reproduced

The 08-19 hazard — a `git status` from the Linux side of the device bridge
leaving a stale `.git/index.lock` that had to be cleared by hand — was re-entered
today by accident: one `git status --porcelain` from the mount. It returned
clean and left no lock file.

**So the hazard is not reliably reproducible, and the rule is a precaution
rather than a proven mechanism.** Keep running git in PowerShell on the host
regardless: the precaution costs nothing, and the one time the lock appeared it
cost an hour. An intermittent hazard is the kind this repository has been worst
at, because the run that does not reproduce it is the one that gets believed.


# Block D — TASK 0 and TASK 1 (2026-08-21)

```
7c003a7  D TASK 0: adulis-exports, and the answer path had been dead since bff0605
73e3c80  D1 step 1: one definition of what a seed record is
f54c585  D1 step 2: the corpus version travels with every answer
```

Scope agreed at the start of the session: TASK 0 and TASK 1 only. Both are done.
TASK 2 and TASK 3 are not started.

## TASK 0 — the gold case was the small half

`adulis-exports` was added as **data only** — no loader change, no harness
change, no schema change — because if the instrument changed in the commit that
turned it green, the green would not be evidence the instrument works. Its
assertion block is COPIED from `aksum-exports`, not retyped, and verified
byte-identical across all seven assertion keys. The only field that differs is
the question. That identity IS the instrument: if the two ever drift, the pair
stops discriminating between two questions and starts discriminating between two
tests.

`eval.test_answer_eval` 68+2F -> **71 passed**. The prediction written before the
run was 70 and was wrong by one: `test_answer_eval.py:217` emits one assertion
per NON-REFUSAL case, and its passing is the property the discriminator depends
on — if a refusal could satisfy `adulis-exports`, both halves would be
satisfiable by the same silence.

## Then the seven unwatched suites found the real defect

**The answer path had been dead for five days.**

```
answer/translate.py:377   _chat(...) -> tuple[str, int, float]   since bff0605
answer/assemble.py:449    raw, retries = _chat(                  unchanged since 9470506
```

`_chat` gained `temperature_actually_used` in **ruling 22's own work**, which
updated translate.py's three call sites and missed the one in the answer path.
Every live answer call raised `ValueError` across `bff0605 -> 77d51fa`, invisible
because Block C ran only the ranking suites. **Block E's 270-call sweep would
have died on call one, and so would the D4 pilot that exists to prevent exactly
that.** No archive is contaminated: the newest predates bff0605 by five days.

The third value is now captured, not dropped into `_`. Ruling 22 says temperature
is classified, recorded and opt-in, never dropped; the answer path passes no
temperature, so the value is 0.0 today — which is precisely why it is worth
reading.

**Nothing guards that contract.** `mutate_part7b` verified 15 of 15 and not one
is about it. The suite DIED rather than failing, and a defect that kills a suite
has no guard by definition. A signature is a contract with as many clauses as it
has return values, and the rule this repository already wrote for predicates was
never applied to signatures.

## The cp1252 trap did not reproduce

Checked as `BLOCK_D_START` required. `mutate_part8.py:153` and
`mutate_part7b.py:223` still lack both ends of the fix `mutate_ranking.py:756`
carries. Both ran clean — 11 and 15 mutations, no crash. **Latent, not active:**
no current mutation produces non-Latin failure detail. Same shape as the
`.git/index.lock` hazard at the close of C7 — re-entered, not reproduced,
precaution kept and recorded as a precaution.

## A green mutation run is not evidence the tree was restored

`mutate_part8.py` rewrote `eval/answer_eval.py` from LF to CRLF on every one of
its 11 mutations and printed *"sources restored"*. Its restore check compares
text after universal-newline normalisation, so it is constitutionally unable to
see the damage. **All four harnesses compare text.**

Surveyed at HEAD: **CRLF 13, LF 58, mixed 0.** An earlier note in
`D_TASK0_RESULT.md` said the tree was CRLF except one file; that was generalised
from seven files and is corrected there. LF is the majority four to one, so the
remedy inverts — the fix belongs in the harnesses, which must compare and write
BYTES.

Exposure, measured:

```
mutate_part8       eval/answer_eval.py                     LF   OBSERVED
mutate_places      ingest/places.py, ingest/gazetteer.py   LF
mutate_ui_places   ui/build_ui_data.py                     LF
mutate_part7b      none - all three sources CRLF
mutate_distractors none - the .sql is read-only, both .py CRLF
mutate_ranking     none - all eight sources CRLF
```

Three of six are exposed, and only by the accident of which files are CRLF.

## TASK 1 / D1 — the corpus version travels with every answer

```
172 spans:  resolved 161  case_folded 0  case_only 9  moved 1  absent 1
seed corpus digest 2e84436cb38a463b... (sha256-of-canonical-json-v1), 24 records
corpus provenance:  unchanged 4   changed 0   unrecorded 168   not_in_version 0
```

Before this, *this span broke* and *this span was made against a different
corpus* were one observation, and `classify_span` resolved the ambiguity by
ASSERTING a cause it had no evidence for. There are now two axes, and the second
has **three** states because two would be a lie about the 168.

**Five walks of the seed corpus existed, not one.** `loader.py`, `places.py`,
`verify.py` and `build_ui_data.build_places` globbed `*/*.json`;
`build_ui_data.load_corpus` used `rglob("*.json")` — so that file disagreed with
ITSELF, and the walk that disagreed is the one feeding `--verify`. All five now
call `ingest.loader.iter_seed_records()`, and a `.json` outside
`region/record.json` raises. No lenient flag: a corpus two walks disagree about
is broken for everything.

**`documents.content_hash` is not one quantity** — a sha256 for the 24 seed
records, the literal string `f"{source}-{object_id}"` for the 426 distractors. A
roll-up over both is stable under any edit to a distractor's text. Every roll-up
is scoped to `NOT is_distractor`.

**`answer_id` is unchanged**, so all 78 archived answers keep their identity.

### Proven with one live chat call

`20260821T100448+0000-d2403a22.json` — the first archive carrying a corpus
version, the first live exercise of the answer path since it was unbroken, and
`adulis-exports`. Grounded, 4 quotations all resolving to disk. The digest in the
archive, the digest in the `answers` row and the digest computed from the FILES
all agree; `africa-03-periplus-adulis` hashes to `0e83bf72...` by three
independent paths. **The gold case passes live, on evidence byte-identical to the
seven consecutive refusals of `aksum-exports`.**

### The two anomalous spans, diagnosed

Both are one run and one record, `africa-03-periplus-adulis`. The `moved` span IS
explained — `bb3bef5` grew `original_text_excerpt` 2089 -> 3001 and the span
shifted 850, six days after the run. The `absent` span **can never be
explained**: `reference_translation` is byte-identical in every commit, and the
offsets come from a corpus state git has never seen — the run is 08-10, the
record's first commit is 08-12. Pre-baseline state or `-recovered`
reconstruction artefact, and D1 cannot separate those two.

`BLOCK_D_START` names the `absent` span as the one D1 makes explicable. **It is
the half D1 cannot help with.**

The 9 `case_only` spans are ONE defect: the same quotation in the same field
across nine runs all dated 2026-08-10, the pre-C1a labeller `build_ui_data.py:505`
already predicts. All 172 spans now have an account.

### A migration cannot own a view that schema-part7.sql owns

`run_answer.py:234` re-applies `scripts/schema-part7.sql` on EVERY run. The first
`schema-d1.sql` added `content_hash` to `citable_passages` and the next run died
with `cannot drop columns from view`. **It died loudly only because the migration
ADDED a column** — had it removed one, part7 would have silently restored it. The
loudness was luck. The column now lives in part7; only the `ALTER`s remain in the
migration, because `CREATE TABLE IF NOT EXISTS` does nothing to an existing
table.

**Carried to Block E:** "change nothing between days" currently names prompt,
corpus, retrieval and gateway. It must name **the schema file**, which is
re-applied on every one of ~90 calls a day.

## A restore command with no guard destroys what it cannot see

`git checkout -- ui/build_ui_data.py`, prescribed by this block's OWN step-2
runbook to clear line-ending churn, discarded every uncommitted D1 change in that
file. Step 1's runbook had it right — commit before running the harnesses — and
step 2 put the harnesses first and kept the command anyway.

Recovery was byte-exact, because every edit this session was an exact-string
replacement rather than a line-offset edit. **That rule is why this cost twenty
minutes rather than an afternoon.**

This is the same finding as the harness restore check, from the other side: the
harnesses compare normalised text and cannot see the damage; `git checkout --`
sees the damage and cannot see what else it takes. Both fail by comparing the
wrong thing.

## The rulings register now exists, and four were unfindable

`RULINGS.md` indexes 1-26 and names the file holding each one's text. C7 recorded
that 25 and 26 were unregistered. **It was four, not two:** rulings 20 and 21 are
inside the 1-24 range and have no declaration section anywhere — one line each in
`C5_START.md`'s numbered list, which every heading-based search misses. Both are
built and mutation-verified, so **the code is the authority for them and no prose
is.** They are not reconstructed: filing a plausible after-the-fact declaration
is how a register stops recording what was decided and starts recording what
someone later assumed.

## The state at the close

```
tree            f54c585, clean
corpus          24 documents / 59 chunks, digest 2e84436cb38a463b...
index           450 / 450 / 0 pending
archives        78 runs, ONE of them carrying a corpus version
gold cases      6, need >= 30
suites          eval.test_answer_eval 71 | test_ranking_check 218
mutations       ranking 91 | part8 11 | part7b 15 | distractors 6 | places 43
                | ui_places 3
chat calls      1 spent this session
```

## Open, and deliberately not closed

- **Nothing guards the `_chat` arity contract.**
- **No mutation harness compares bytes on restore.** Four harnesses, one blind
  check each; three of six have LF sources they silently rewrite.
- **`classify_span` still asserts a cause it cannot know**, and `--verify` now
  prints that sentence directly above a provenance line that contradicts it.
- **Rulings 20 and 21 have no full text.**
- **`aksum-exports` remains an open defect.** Adding the passing half did not
  close it and was not recorded as closing it.
- **TASK 2 and TASK 3 are not started.**

---

# Block D — TASK 2 / D2: the expected behaviour schema (2026-08-21)

*Provenance of this section and the four that follow it: they are transcribed
from `D2_RESULT.md`, `D3_RESULT.md`, `D3_RULINGS.md`, `FINDINGS_9_TO_13.md`,
`WEILUE_FIX_RUNBOOK.md` and `D4_START.md`, all of which were written while the
work was being done and every number in which was measured on the host at the
time. **Nothing here was re-measured when this section was written.** Where a
figure has since moved — the corpus digest did, three times — the movement is
stated in the closing section rather than silently applied backwards.*

**DRAFTED 2026-08-23 AND APPLIED 2026-08-28.** These five sections sat written
and unapplied for five days while `PROGRESS.md` ended at TASK 1 and
`BLOCK_F_START.md` sent the next thread to its last section. The delay is
recorded rather than smoothed over: what follows was written when the work was
fresh, and nothing in it was revised on the day it was finally pasted in.

```
tree at start   f54c585, clean
tree at close   9ea1774  D2: every case declares its expected behaviour, and
                         the loader refuses a default

ANSWER          eval.test_answer_eval     71 -> 98    GREEN on the host
mutations       scripts\mutate_part8.py   11 -> 23    all 23 verified on the host
gold cases      6, unchanged in number. All six now carry a ruled label
```

**No suite was red at any point.** Both were run on the host, in that order,
with the commit between them.

D2 is the schema change and nothing else. **No new question was written, on
purpose:** a case drafted against a permissive loader is a case nobody can be
sure the strict loader would have refused. D3 writes the 24 new cases against
the loader below.

## The rule, and where it now lives

> Every case declares its expected behaviour explicitly, and the loader REFUSES
> to inherit it from a default.

`expected_behaviour` is in `_ANSWER_REQUIRED`. A case that omits it is a load
error. Three values, and they are not three flavours of one thing — they are
three different pieces of news:

| value | the corpus | what a red line MEANS |
| :---- | :---- | :---- |
| `answerable` | holds it | retrieval or assembly failed |
| `correctly_refusable` | does not hold it | the model invented something |
| `refusable_with_gloss` | holds it, untranslatably | a machine translation appeared, attached to a citation |

Before D2 a red line said only *"this case failed"*, and which of the three it
was lived in a human's head.

## Eight loader clauses, each with its own mutation

`expect_refusal` was **kept**, not derived. Two fields that must agree are a
guard; one field computed from the other is a guard deleted. The disagreement is
refused in both directions, and that is deliberately two clauses:

```
1  expected_behaviour is required            no default, no fallback
2  the value is one of the three             an unread label is not a label
3  correctly_refusable => expect_refusal     clause one of two
4  expect_refusal => correctly_refusable     clause two of two
5  a speaking case asserts positive content  see below
6  refusable_with_gloss names a quoted doc   the published gloss
7  refusable_with_gloss declares a hedge     expect_hedge_any
8  a hedge outside the gloss arm is refused  a rule that is not in force
```

**Clause 5 is the one that was not asked for and earns its place.** A refusal
contains none of the strings a case excludes, so a case built from
`expect_answer_excludes` alone is passed by silence. `_has_content_assertion`
already accepted such a case, because an exclusion IS a content assertion — it
just is not one an answer has to speak to satisfy. Clause 5 says: if the label
claims the answer should speak, something must require it to.

### The hedge is now a declared field

`expect_hedge_any` is new, and it is the one design decision taken inside the
ruling rather than handed up. The ruling was *"published gloss plus required
hedge"*, and **required** needs a way to identify the hedge. Previously
`vimose-runes`'s hedge group was one entry among four in
`expect_answer_contains_any`, indistinguishable from content — a later edit could
drop it and nothing would notice.

It costs no scorer change: **the loader merges the declared hedge back into
`expect_answer_contains_any` at construction**, so `answer_eval.py` sees exactly
what it saw before. The separation exists only at the point where the rule is
enforced, which is load time.

## The discriminator is now enforced, not described

`paired_with` is symmetric and load-checked. Four clauses, four mutations: a case
may not pair with itself; the partner must exist; the partner must name this case
back; **and the two assertion blocks must be identical**. `_ASSERTION_KEYS` is
what gets compared — everything that IS the test. `id`, `question`, `why`,
`note`, `archived_status` and `paired_with` are excluded, because the question is
the only thing the two halves are allowed to differ on.

Deleting one half is now a load error. Relabelling one half is a load error. Both
were prose in `answer_cases.json`.

## FINDING 8 — the mutation harness was rewriting a source on every run, and said it restored it

Not argued from the code. **Observed, by running it.**

`scripts/mutate_part8.py` held `SOURCES = (eval/goldset.py, eval/answer_eval.py)`
and **those two do not agree on line endings** — `goldset.py` is CRLF,
`answer_eval.py` is LF. It captured originals with `read_text()`, which
normalises every ending to `\n`, and restored with `write_text()`, which writes
the platform's. **On the host it is `answer_eval.py` that gets converted, LF →
CRLF, on every run.** The restore check could not see it: it compared
`read_text()` to `read_text()`, normalised against normalised. It printed
*"sources restored"*.

This is Finding 5 with a name and a reproduction, and D2 could not leave it —
D2 doubles the number of times this harness runs. Fixed in the same file:
originals captured and restored as **bytes**; the unrestored check compares
bytes; each source written back with **its own** line ending, detected at start;
mixed endings inside one source refused rather than silently picked.

Verified twice, and the second check is the one that matters: **on the host,
`git status --short` after the 23-mutation run named no tracked file at all.**
Before D2 that same command would have named `eval/answer_eval.py`.

## Also fixed: the non-Latin pipe, before D3 meets it

Both ends named rather than inherited from the locale — parent
`subprocess.run(..., encoding="utf-8", errors="replace")`, child
`PYTHONIOENCODING=utf-8`.

**Recorded as not proven.** No case in the six-case gold set produces non-Latin
*failure detail*, so the pipe was never asked to carry Greek, Tamil or Chinese
during the 23-mutation run. The fix is defensive and untested; D3 is what will
test it.

## The six labels, as committed in `9ea1774`

```
answerable            aksum-exports        paired_with adulis-exports
answerable            adulis-exports       paired_with aksum-exports
answerable            muziris-cargo
answerable            chinese-da-qin
refusable_with_gloss  vimose-runes
correctly_refusable   antikythera-absent
```

`vimose-runes` was contested at drafting time and **RULED: it stands as
`refusable_with_gloss`.** The Elder Futhark sequences are only partly deciphered,
which argues gloss; the record does carry a `reference_translation`, which argues
`answerable` with a hedge. The label is not cosmetic — gloss says a red line
means *a machine translation appeared*, answerable says *retrieval broke*.

## What D2 did NOT do

- **No new questions.** Still 6 cases; G4 needs ≥30.
- **No scorer change.** `answer_eval.py` untouched. Block E's 270 calls go
  through the same scorer that scored the archives.
- **No floor change.** `calibrated: false` still stands.
- **`aksum-exports` is still an open defect** and D2 did not close it.

---

# Rulings 25 to 31 declared in PROGRESS.md at last (2026-08-21)

*Written because `C7_RESULT.md`, `D1_RESULT.md` and `D2_RESULT.md` each recorded
the same open item: rulings 25 and 26 were being quoted by four Block D documents
and declared in none of them, and `PROGRESS.md` — the file a later thread
actually reads — declared neither. Rulings 27–31 are indexed here in the same
breath so the gap does not reopen. Full text lives where each line says.*

| # | one line | full text in |
| :---- | :---- | :---- |
| 25 | G2's gap criterion FAILS on its own arithmetic; kill trigger 1 pulled; the follow-on is a sourcebook at 24–60 records, not 200 | `C5_3B_AND_PROTOCOL.md` |
| 26 | the two via-original keys are emitted from the COLLAPSE block, so via-original is measured at both points | `C7_RESULT.md` |
| 27 | every case declares its expected behaviour, and the loader refuses to inherit it | `D3_RULINGS.md` |
| 28 | the gloss arm is for a contested READING of a text, and nothing else | `D3_RULINGS.md` |
| 29 | a false premise the corpus can correct is ANSWERABLE | `D3_RULINGS.md` |
| 30 | behaviour balance is held to the definitions, and the shortfall is recorded | `D3_RULINGS.md` |
| 31 | a discriminator loads as one instrument, and `paired_with` means only that | `D3_RULINGS.md` |

**Do not renumber.** Twenty-six numbers were already quoted across `PROGRESS.md`
and seven session documents before 27–31 existed.

**Rulings 20 and 21 still have no full text anywhere** — one line each in
`C5_START.md`'s numbered list, which every heading-based search misses. Both are
built and mutation-verified, so **the code is the authority for them and no prose
is.** They are deliberately not reconstructed: filing a plausible after-the-fact
declaration is how a register stops recording what was decided and starts
recording what someone later assumed.

Two of the five new rulings are worth restating here in full, because they are
the ones a later thread will be tempted to relax.

**Ruling 28 keeps the gloss arm narrow.** It does not cover contested
attribution, disputed dating, uncertain identification of a depicted figure or
unresolved provenance. Those are real uncertainties and none of them is this one;
where a case needs the answer to preserve such a doubt, the doubt is required as
**ordinary content** on an `answerable` case. If the arm widens to any contested
claim, a red line on it stops naming one failure and starts naming several, and
the specific failure it was built to catch — *a machine translation, arriving
attached to a citation* — becomes one meaning among many. **The count would
improve and the instrument would get worse.**

**Ruling 29 says the refusal arm means "the corpus cannot address this" and never
means "the question was badly posed."** Ruled at `oc-eo-roman-coins`, which asks
*"Were Roman coins found at Óc Eo?"* They were not — the record calls them
"costume jewelry rather than circulating coinage". Giving the correction is
answering; refusing would be the wrong behaviour, not the safe one. Letting the
arm mean the second thing turns refusal into the reward for any awkwardly-worded
question, and `floor.json`'s `max_refusal_rate` exists precisely because a prompt
that refuses more while erring no less is a regression no metric built on
grounding can see.

---

# Block D — TASK 2 / D3: the gold set goes from 6 cases to 33 (2026-08-22)

```
gold set                6  ->  33 cases
eval.test_answer_eval  98  ->  203
scripts\mutate_part8   23  ->  27
seed corpus digest     bcfa0211dcbe999a...  (moved again the same day; see the
                                             findings section and the closing state)
```

## G4's stratification, computed by the suite rather than claimed here

```
cases                 33      wants >= 30
behaviours            22 answerable / 3 gloss / 8 correctly_refusable
Arabia 4   East Asia 5   Persia 4   Scandinavia 5
South Asia 5   Southeast Asia 4   Sub-Saharan Africa 5   outside 1
regions at >= 3       7 of 7
source languages      14      wants >= 6
loader-enforced pairs 2
```

`eval.test_answer_eval` computes the per-region tally itself and fails if any
region falls below three. **A gate checked against prose is a gate checked
against whoever wrote the prose** — and until the `region` field landed, eight
cases were invisible to that count while still contributing to the total, because
the loader forbids `expect_quoted_docs` on a refusal case and so a refusal names
no document and nothing tied it to a region.

## Four species of correct refusal, and they were built deliberately

The eight `correctly_refusable` cases are not eight instances of one thing:

```
not in the corpus at all         antikythera-absent
in the corpus, no reachable      palmyrene-tariff-rates, ezana-stone-geez
text                             (both `pointer` chunks, ineligible — the
                                  corpus's only two)
reachable, but the excerpt does  skz-roman-emperors, oc-eo-cattigara,
not hold what the record's own   pattanam-dna-evidence, weilue-ruler-selection
title and notes advertise
adjacency                        gudme-bracteate-runes
```

**The third species is the one a model is most likely to fail, and the fourth is
the one a reader is least likely to catch.** `skz-roman-emperors` asks which
Roman emperors the Res Gestae Divi Saporis names; the record's own notes say it
"directly documents Roman emperors (Gordian III, Philip the Arab, Valerian)" and
the excerpt on disk contains none of *Valerian*, *Gordian*, *Philip*, *emperor*,
*Rome* or *Roman*. A model retrieves it with high confidence, sees a Sasanian
royal *res gestae*, and can supply Valerian from its own weights.

`gudme-bracteate-runes` refuses by **adjacency**: the record does say "nine gold
bracteates", gold bracteates often carry Elder Futhark runes, and the corpus
holds `vimose-runes` as a template for what such an answer looks like. Its
excluded strings, `alu` and `laukaz`, are the formulaic legends that actually
recur on Scandinavian bracteates — exactly what a model would supply.

In every case the excluded strings are **wrong about this corpus, not about
history**, which is why none of them may ever be softened on the grounds that the
answer is correct.

## Two loader-enforced pairs, discriminating on different axes

```
aksum-exports / adulis-exports        varies the WORDING of an English question
akananuru-yavana-ships / -tamil       varies the LANGUAGE it is asked in
```

Both carry byte-identical assertion blocks against one record, enforced at load
under ruling 31. The Tamil pair is the set's first non-English question, and a
run where the Tamil half passes and the English half fails puts the defect in
cross-lingual retrieval and nowhere else — not the corpus, which holds the poem,
and not the answer path, which just answered the same question about the same
record.

**The Tamil question is a verbatim phrase from the poem, not an interrogative
sentence.** It is the already-ranked `probe-tamil-akananuru` string, which buys a
known-good retrieval half and invents no Old Tamil that nobody on this project
can check. If someone who reads Tamil supplies a real interrogative, replace the
question string and **nothing else** — the loader will refuse a drifted pair.

## The behaviour balance is NOT met, and was not negotiated

**3 gloss cases against 22 answerable.** Ruling 30 governs it: write every gloss
case the corpus can honestly carry, fill the rest with the other two arms, and
record the shortfall rather than widen a label to meet a number.

The arm needs a text whose **reading** is unsettled. The seed corpus holds three:
`vimose-runes` (partly undeciphered Elder Futhark), `raqosh-epitaph` (two
competing scholarly readings, stated inside the retrieval-eligible chunk) and
`oc-eo-medallion-legend` (a corrupt Latin coin legend with an alternative reading
and a curator's note that it is corrupt).

**That shortfall is a finding about the corpus, not about the case set**, and it
is worth knowing before Block F decides what to add: this seed corpus contains
very few texts whose reading is genuinely in dispute.

Ruling 28 was applied three times to keep the arm narrow —
`sasanian-hunting-plate` (contested attribution), `khao-sam-kaeo-intaglio`
(contested identification of a carved figure), `hoby-silius-identification`
(contested identification of a person). Each required its uncertainty as ordinary
content instead. Widening the arm would have hit the balance target and cost the
arm its meaning.

## The boundary case, recorded so it is not re-litigated

`hoby-cheirisophos-signature` quotes a Greek signature the corpus gives as
`[ΧEIPI]ΣΟΦΟΣ` — square brackets, an epigraphic restoration, in a
retrieval-eligible chunk. It is `answerable`, not gloss. **Restored is not
contested**: the record supplies a confident published gloss and offers no
alternative, so a required hedge would be a hedge the evidence does not argue
for, and the case could never pass.

## Deliberate known failures

Two cases are expected to fail and say so in the file before they were ever run.
Both are tracked in `floor.json.known_failing_cases` as **open defects, never
tolerated ones**, and both are kept out of `required_cases` so that a floor pass
can never be read as *"the system does this"*.

- **`aksum-exports`** — unchanged from Phase 1. Seven consecutive refusals under
  four prompts, against evidence byte-identical to the passing `adulis-exports`.
- **`weilue-chinese-quotation`** — added 2026-08-22. Fails because nothing in the
  answer path ever asks for a non-English source text to be quoted. See finding
  13 below.

Two more are expected to be hard but are not yet classified as known failures,
because they have never been run: **both halves of the Akanāṉūṟu pair.** Part 4
scored Old Tamil at 0.368 against 0.6–0.7 for other scripts. Neither goes into
`required_cases` until both are seen passing across sessions.

---

# The Weilüe investigation — findings 9 to 13 (2026-08-22)

*Findings 1–5 are in `D_TASK0_RESULT.md`, 6–7 in `D1_RESULT.md`, 8 in
`D2_RESULT.md`. What follows began after D3 had closed, as a single corpus fix,
and turned into four more defects — three of them in the instruments rather than
the data.*

**On the numbering.** Finding 11 was assigned retrospectively. Findings 12 and 13
were named while 11 was still an unfilled gap, and 11 is recorded in the place it
belongs chronologically rather than the order it was numbered. Said plainly,
because a register that quietly renumbers is worse than one with a scar.

## Finding 9 — the flagship record's Classical Chinese was invented

`eastasia-01-weilue` is the record the AI Technology Showcase brief names by
name. Its `original_text_excerpt` held 52 characters of plausible Classical
Chinese **that do not occur in the Weilüe.**

Checked fragment by fragment against the Sanguozhi text: **all three fragments
absent, 0 of 3.** Four divergences, and in each the record's form appears nowhere
in the source while the real form is present:

```
record          source
犂靬            犁靬            the name Lijian
安谷城          安穀城          the city Angu
城以石為壁      以石爲城郭      the stone walls
海西人名之海西  故俗謂之海西    "called Haixi"
```

`ingest.fidelity` classified it `partial_verbatim`, retrieval-eligible. It has no
way to detect this.

**The corruption was not discovered here, and the credit belongs elsewhere.** The
Da Qin block §4 above records it with the specific divergences named. It was
deliberately not fixed then, on a ground worth restating: correcting a primary
source from a secondary work's quotation would itself be an unsourced edit, and
the stated blocker was that zh.wikisource *"returned nothing fetchable"*.

**Why it was fetchable this time: the record was citing the wrong page.** The
魏略輯本 edition's index lists 西戎傳 — including 大秦國 — under 卷二十二, and
卷二十二 is an unwritten page. The text lives where the record's own
`language_note` always said it did: Pei Songzhi's commentary in the Sanguozhi,
Wei Shu 30. That is a primary transmission, so the 2026-08-13 objection is met
rather than waived.

What this session added was not the discovery. It was: that the text was
*invented* rather than corrupted; the 45-of-45 answer-side measurement; the
reason the citation was unusable; and the fix.

### What the fix changed, measured: nothing

```
pairs 33 / units 30                                    unchanged
172 spans  resolved 161 case_only 9 moved 1 absent 1   unchanged
recall@6 via original, reranked        22/30 -> 22/30
china-describes-rome-weilue             5/1/7 -> 5/1/7
probe-chinese-weilue                    1/1/1 -> 1/1/1
```

Only `mrr_at_10_reranked` moved, by 0.0006 — reranker noise under ruling 22.

Retrieval was never going to move, and the entry role says why: the English query
enters through the translation chunk and the Chinese query through the original
chunk, before and after. **Replacing the content of a chunk cannot change which
chunk a query enters through.**

**That the measurements did not move is itself the finding.** The fabrication was
never distorting the ranking figures. It was sitting underneath them.

### A correction to how this was framed

The brief says *"Retrieves the Weilüe passage on Da Qin in Classical Chinese."*
That claim is about **retrieval** and it is satisfied — `probe-chinese-weilue`
ranks the Chinese chunk 1, and it is `[S1]` for an English question too. Reading
it as broken conflated retrieval with quotation. **The brief is fine. The gap is
finding 13**, and nobody had separated the two claims.

### Two `subject_places` notes rested on the fabrication

Angu was spelled `安谷城`, a form absent from the source. More seriously, the Da
Qin entry refused a Pleiades identification partly because *"the Chinese excerpt
is elided at exactly the point where the capital is described"* — true of the
fabrication, false of the Weilüe, which reads `其王治濱側河海，以石爲城郭`. **A4's
decision is unchanged** and stands on its main ground, that the city of Rome is
not the empire; the second reason is recorded as withdrawn and dated.

## Finding 10 — nothing anywhere guarded a process's own stdout

Three boundaries carry non-Latin text out of this project. Until today only two
were guarded anywhere:

```
1. a CHILD process's stdout      PYTHONIOENCODING in the child's env
                                 guarded: mutate_ranking.py (Part 7),
                                          mutate_part8.py (D2)
2. a PARENT decoding that child  subprocess.run(encoding="utf-8")
                                 guarded: the same two files
3. THIS process's own stdout     NOTHING, in any of 43 entry points
```

Boundaries 1 and 2 are about a pipe between two processes. **Boundary 3 is about
where a process writes when nobody is reading its console**, and it is the one
that fires under a redirect. **So the D2 fix was half a fix** — it secured the
pipe into the parent and left the parent's own output open, in a harness that
deliberately prints the child's captured text verbatim to preserve failure
detail. Part 7 made the identical partial fix at `mutate_ranking.py:749`. Two
people, the same blind spot, a month apart.

Found by running `WEILUE_FIX_RUNBOOK.md` step 0 as written: `python -m
ui.build_ui_data --verify >> eval\weilue-before.txt` died at
`build_ui_data.py:730` printing the Greek behind a `case_only` span. On Windows
`print` writes through a stream whose encoding comes from the console code page,
and through a pipe or redirect it falls back to cp1252. **It does not degrade. It
raises, mid-output, with the file half written and every number in it correct.**

**Why it mattered more than the crash:** `eval/run_answer_sweep.py` was
unguarded. Block E is 30 cases × 3 repetitions × 3 days, every answer quoting a
corpus that is Greek, Tamil, Chinese, Geʽez and runic, and nobody runs a
three-day sweep without redirecting it to a log. **It would have died on day one,
after spending real chat calls.**

### The count was wrong four times: 7, 20, 22, 43

Twice from typing a list by hand. Once because `eval/answer_eval.py` — the scorer
itself, which prints failure detail full of corpus text — was missed twice
running. **And once because the list was verified against a partial copy of the
repository rather than the repository**: twenty-one entry points existed that the
checking tree did not contain, so the check passed on a tree where the files were
absent.

So the list was deleted. `test_every_entry_point_guards_its_stdout` asserts the
**rule** — every file under `ui/ eval/ answer/ ingest/ scripts/` carrying a
`__main__` must carry the guard — and enumerates by glob at check time. It also
asserts the glob found **at least forty files**, because an enumeration that
collapses to zero passes vacuously.

Inlined in 43 files rather than shared, for a specific reason:
`ui/build_ui_data.py` documents `python ui/build_ui_data.py` as an invocation,
and under that form the repository root is not on `sys.path` — a helper module
would be unimportable for exactly the file that found the defect.

`errors="replace"` is a judgement. **A mangled character is cosmetic; a sweep
that dies on day two of three is ninety chat calls and an unrepeatable
measurement.**

### Demonstrated, after a first attempt that proved nothing

The first proof was `python -m eval.test_answer_eval > file` returning exit 0.
**It was vacuous.** A passing suite prints only `ok` lines with English labels;
the non-Latin lives in failure detail a green run never emits. Zero non-Latin
characters reached the file. That is this project's own trap — *a check that
greps a heading passes against a report that prints the heading and no rows* —
walked into an hour after being written into a runbook.

The real proof is the command that died, in a fresh shell with **no environment
variable set**:

```
python -m ui.build_ui_data --verify > eval\stdio-guard-proof.txt 2>&1
exit code 1        <- the gate failing on moved 1 / absent 1, BY DESIGN
Traceback present:          False
UnicodeEncodeError present: False
60 lines written, report complete through the final case_only block
```

Boundary 3 fixed. **Boundary 4 — PowerShell decoding the child with
`[Console]::OutputEncoding` — is a shell setting no code can fix**, and the same
file shows 16 mojibake runs to prove it. Both are named in step 0 of the runbook
now. Before the fix there were no bytes at all; now there are correct bytes that
PowerShell mangles on the way in.

## Finding 11 — the paraphrase flag marks suspicion, and nothing ever turned it into a determination

`ingest/fidelity.py` carries `PARAPHRASED_ORIGINALS` and `PARAPHRASE_ID_HINTS`,
five records flagged by the manifest as *"paraphrased or partial rather than
verbatim"*. The branch that reads them says:

> *"Where the original script is actually present, the wording is the source's
> own — it is abridged, not invented."*

**That is the assumption finding 9 disproved on the first record anyone checked.**

Two of the five carry real non-Latin text. `eastasia-01-weilue` was invented.
`eastasia-02-hou-hanshu` was checked the same way on 2026-08-22 and is
**genuine** — 34 of 36 characters identical to the Sanguozhi transcription, one
traditional/simplified pair (獻/献, an artefact of the `zh-hans` view) and one
variant character for the same word (瑇/玳, tortoiseshell), which needs a
traditional-script edition to settle.

So the flag never distinguished them. It marked suspicion; nothing in the
pipeline ever converted suspicion into a finding, and the comment asserting the
benign reading sat there for both.

A related staleness: `southasia-01-akananuru-149` is still on the hint list while
its own note records verbatim Old Tamil recovered on 2026-08-09, and the
corrected Weilüe is still labelled `partial_verbatim` by the override rather than
`verbatim_original`. **Not fixed** — it requires a re-ingest and was deliberately
kept out of the Weilüe measurement.

**A hypothesis about the fabrication, offered as a hypothesis.** The Hou Hanshu's
own Da Qin section opens `大秦国，一名犂鞬` — with **犂**. The Weilüe reads
`大秦國一號犁靬` — with **犁靬**. The invented text read `大秦國一號犂靬`: **犂**
from the Hou Hanshu, **靬** from the Weilüe. A blend of the two Da Qin passages
this corpus holds, adjacent in the same region folder. Consistent with a hurried
synthesis from neighbouring sources rather than a transcription slip, but
circumstantial.

## Finding 12 — the ranking harness drops unresolvable gold pairs silently

Both Weilüe ranking pairs carried `expect_text_contains: 大秦國一號犂靬` — the
**fabricated** form — one of them with an explicit note saying it asserted *"the
characters that are on disk, not the characters that ought to be"*, a documented
workaround for a known-bad record.

When the record was corrected, the assertions matched nothing. Both pairs left
the run. The harness said only:

```
"31 pairs, 29 distinct query text(s) embedded in 1 request(s)"
```

A count line. No warning. And every headline number moved:

```
pairs 33 -> 31     units 30 -> 29
recall@6 via original, reranked   22/30 -> 21/29
```

**The denominator shrank.** `0.7333 → 0.7241` reads like a small regression; it
is a measurement that lost a pair. This is the project's own trap in the
aggregate line of the ranking harness, and it is why the invalid archive
`eval/ranking_runs/20260822T160349…` is **committed deliberately and kept**: it
is what this finding looks like from the inside.

`scripts/weilue_compare.py` reports a vanished pair loudly and says explicitly
that zero movement after a corpus edit is itself a finding. **The harness itself
is still unguarded** — a pair-count check against the gold file, failing loudly
and naming what did not resolve, is scheduled as the first thing in D4.

## Finding 13 — nothing in the answer path ever asks for a source text to be quoted

Not a weak preference. **An absent mechanism.**

Prompt rule 3 permits a quotation from *"the SOURCE TEXT or the ENGLISH shown for
that source"* and requires neither. English is easier and reads better, so
English wins. Measured across 16 archived runs of `chinese-da-qin`: **45 of 45
resolved spans from `reference_translation`, none from `original_text_excerpt`.**

The corpus fix proved retrieval was never the obstacle. On the live run of
2026-08-22 the Chinese chunk was `[S1]` — top of the evidence block, similarity
0.576, traceable to `original_text_excerpt[0:221]` — and the model quoted the
English anyway, five times out of five.

**The corpus fix was necessary and could never have been sufficient**, and it was
predicted here that it might be. It was not.

`expect_quoted_docs` cannot express the difference, because it is satisfied by a
quotation from either of a record's chunks — which is exactly why the hole was
invisible. `expect_quoted_from_original` now can. Strictly additive: a new
optional key and a scorer branch that runs only when the key is present, so no
existing verdict can change, which matters because Block E's 270 calls go through
that scorer.

`weilue-chinese-quotation` is the standing detector, expected to fail, tracked as
an open defect. **Closing it means changing prompt rule 3**, which cannot happen
before Block E without invalidating every archived number.

## What is fixed, and what is not

```
FIXED       9   the record now holds 221 sourced characters; two ranking pairs
                retargeted; two subject_places notes corrected
FIXED      10   43 entry points guarded, demonstrated at the boundary that failed
OPEN       11   the fidelity override is stale on two records and its justifying
                comment is disproved; needs a re-ingest
GUARDED    12   in weilue_compare.py only; the harness itself is unguarded
DETECTED   13   assertable and detected, not fixed — the fix is a prompt change
                and the prompt is frozen
```

---

# State at the close of D3 (2026-08-22)

*A separate section for the same plain ordering reason the C7 state block gives:
the sections above were written into the commits that contain them and cannot
name them. This one is written after `b1e11ab` and names it.*

## The tree

```
b1e11ab, clean

b1e11ab  FINDING 11: the paraphrase flag marked suspicion
2c8f20e  the Finding 10 demonstration
5a3bd7b  D3 and the Weilue investigation, two documents
846d5b9  FINDING 10: stdout guard, 43 entry points
5b9aed2  the runs behind the Weilue fix
d0ef3bc  FINDING 13: expect_quoted_from_original
5289f55  Weilue: invented excerpt -> sourced Sanguozhi text
9ea1774  D2: every case declares its expected behaviour, and the loader
         refuses a default
```

## The numbers a later thread will want without reading for them

```
corpus          24 records / 59 chunks / 57 retrieval-eligible
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
index           450 / 450 / 0 pending
archives        79 answer runs, 26 ranking runs, 3 sweeps (ALL within-session)
gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
                Arabia 4  East Asia 5  Persia 4  Scandinavia 5
                South Asia 5  Southeast Asia 4  Sub-Saharan Africa 5  outside 1
floor           calibrated: false, 4 required, 2 known-failing

ANSWER          eval.test_answer_eval       203   GREEN
mutations       scripts\mutate_part8.py      27   GREEN
```

**THE DIGEST CHANGED THREE TIMES ON 2026-08-22.** `2e84436c` → `bcfa0211` →
`26e4a683`, from two real corpus edits — the Weilüe text, then the Hou Hanshu
note. **Only `26e4a683…` is current**, and it is the number Block E records on
day one and re-asserts on day three. **Any document still naming `2e84436c` or
`bcfa0211` is stale**, including the D3 result section above, which is left as
written because it was true when it was written.

## What is left in Block D — TASK 3 (D4), and nothing else

`BLOCK_D_START.md`'s TASK 3 is still authoritative. Restated, because it is now
the last thing between here and a Block E that can be believed:

0. **Guard FINDING 12 first.** A pair-count check in `run_ranking_check.py`
   against the gold file, failing loudly and naming what did not resolve.
   `scripts/weilue_compare.py` already does this for the Weilüe pairs; the
   harness itself does not.
1. Record a **session identity** — run date at minimum — in every sweep archive.
2. Make floor calibration **refuse to set `calibrated: true`** when distinct
   dates < 3, and **mutation-verify that refusal**.
3. Report **per-case stability and per-session stability as two separate
   numbers.** One number cannot say which of the two is moving.
4. **Pilot on 5 cases across 2 days, ~30 chat calls**, so the three-day sweep is
   not the first time this code runs across a date boundary.

**The gap is confirmed, not assumed.** `eval/run_answer_sweep.py` takes
`--prompt-version --repeat --case --k --max-sources --pause --dry-run --no-write
--json`. There is no session flag and no date field in any archive. Checked
2026-08-22.

**Why it is not optional.** `floor.json` says `calibration_invalidated:
"2026-08-10, hours after being set."` The floor was calibrated on CONTENT being
stable in 10 of 10 cells across three repetitions each. A second sweep, with the
`vimose-runes` evidence block byte-identical across all six archived runs,
produced 3/3 with seven resolved quotations in the first session and 0/3 with
none in the second. Same prompt version, same model, same evidence, temperature
0. All three archived sweeps are within-session. **Block E's 270 calls are worth
nothing if the archives cannot tell a session from a repetition**, and today they
cannot.

## Four traps learned on 2026-08-22, carried forward

- **A green result from a partial copy of the repository is not a result.** The
  stdout-guard count was reported as "22 of 22" from a sandbox that did not
  contain twenty-one of the entry points. Verify against the tree that ships.
- **An enumeration maintained by hand will be wrong.** That same count was wrong
  four times — 7, 20, 22, 43. The check that finally held asserts the RULE and
  globs at check time, and additionally asserts the glob found at least forty
  files, because an enumeration that collapses to zero passes vacuously.
- **A passing suite proves nothing about non-Latin output.** A green run prints
  only `ok` lines in English; the non-Latin lives in failure detail it never
  emits.
- **Encoding has TWO ends on Windows and both must be named.**
  `PYTHONIOENCODING=utf-8` makes Python emit UTF-8; `[Console]::OutputEncoding`
  decides how PowerShell decodes it. Set only the first and you get a capture
  whose numbers are all correct and whose every Greek quotation is mojibake, with
  zero replacement characters, so nothing looks wrong.

## Open, and deliberately not closed

- **`run_ranking_check.py` has no pair-count guard** (finding 12). First item in
  D4.
- **`match_case` returns the FIRST case whose question matches.** Two cases
  sharing a question would leave the second silently unscored against every
  archive — sitting in the gold set looking like a test and never running.
  Avoided by hand in `weilue-chinese-quotation`; unguarded in the loader. Same
  family as finding 12.
- **Two gold cases are expected to fail and must stay failing.** `aksum-exports`
  and `weilue-chinese-quotation`, both tracked in `floor.json.known_failing_cases`
  as OPEN defects, both out of `required_cases`. Neither is closed by D4. **A
  sweep that reports them passing is a finding, not a success.**
- **Behaviour balance unmet**, 3 gloss against 22 answerable, under ruling 30.
- **`ingest/fidelity.py`'s comment is false and its hint list is stale for two
  records** (finding 11). Needs a re-ingest.
- **The 瑇/玳 variant is unresolved** and needs a traditional-script edition.
- **`eastasia-02-hou-hanshu`'s `original_text_note` still promises a cross-check
  "during ingestion"** that has now been performed and should record what was
  checked, against which page, with what result.
- **Nothing guards the `_chat` arity contract.**
- **Five mutation harnesses still restore with `write_text`** — `mutate_ranking`,
  `mutate_part7b`, `mutate_places`, `mutate_ui_places`, `mutate_distractors` and
  `mutate_recover`. Finding 8 was fixed in `mutate_part8.py` only. A known defect
  with a known fix, not an open question.
- **`classify_span` still asserts a cause it cannot know.**
- **Rulings 20 and 21 still have no full text.** The code is the authority.
- **Ruling 25's figure can no longer be re-derived from the tree.** The corpus
  moved. The ruling stands; the cost was accepted deliberately and is recorded
  rather than tidied away.
- **The `weilue-before.txt` capture has mojibake Greek quotations.** Every number
  in it is correct; the quotation lines are not evidence of anything.
- **The Akanāṉūṟu Tamil question is a phrase, not a sentence**, pending someone
  who reads Tamil.
- **Housekeeping.** `_to_delete/` holds three staging tarballs from the
  2026-08-22 session — `f10.tgz`, `f10-guarded.tgz`, `mu-sub.tgz` — alongside
  three older files. The directory is gitignored; nothing depends on any of it.

## The sentence that still travels with all of it

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310. The W2b distractor
curve still rests on English-only padding.

**And one more, earned on 2026-08-22: the answer path has never quoted a
non-English source text.** 45 of 45 resolved spans across 16 runs came from the
English, while the Chinese chunk sat at `[S1]`. That is not retrieval and it is
not the corpus — the corpus was corrected and nothing moved. Nothing in the
prompt ever asks for the source text, and rule 3 permits either. **Block E will
measure a system that reads its sources in translation.**

---

# Block D — TASK 3 / D4: the harness can tell a session from a repetition (2026-08-24 / 2026-08-25)

*Transcribed from `D4_RESULT.md`, `D4_DAY1_STATE.md` and `D4_RULINGS.md`, all
written at the time and every number in them read out of the archives rather
than out of a report. Rulings 32–35 are declared in `D4_RULINGS.md`; ruling 35
is the one to read before quoting a stability number.*

```
1  session identity in every sweep archive     DONE, on two live runs
2  calibration refuses under 3 distinct dates  DONE, mutation-verified, and
                                               REFUSED FOR REAL on 2026-08-25
3  per-case and per-session as two numbers     DONE, each with its own denominator
4  pilot on 5 cases across 2 days              DONE. 6 cases, 36 chat calls
```

## The two pilot sessions

```
                day 1                     day 2
session         792202e7ac58              8ee2273defd6
date            2026-08-24 (UTC)          2026-08-25 (UTC)
window          12:21:08-12:23:10         19:14:21-19:21:21
crossed midnight  false                   false
corpus          26e4a683… at both ends, corpus_moved null, both days
```

The gap is **31 hours, not 24**, on purpose: midday to evening on consecutive
dates is a stronger observation than a few hours either side of midnight UTC,
and it keeps `crossed_midnight_utc` false so neither session's date is
contestable.

## Every verdict agreed, and not one answer text did

```
per-case      12/12 = 100%    the sampler, within one session
per-session    6/6  = 100%    the day, across sessions
60 rows carry no session identity and are counted in NEITHER number
```

**Both numbers are 100% and that is a real result, not a null one.** It is the
first time this project could say its verdicts reproduce across a date boundary.

And then the texts, hashed:

```
case                 day 1        day 2        shared
adulis-exports       2 distinct   1            NONE
aksum-exports        1            1            NONE
antikythera-absent   1            3 distinct   NONE
chinese-da-qin       3 distinct   1            NONE
muziris-cargo        1            1            BYTE-IDENTICAL, all six runs
vimose-runes         1            1            NONE
```

**Five of six cases share not a single answer text between the two days**, at
temperature 0, against an identical corpus digest at all four measurement
points, on a pinned dated model snapshot. Three things follow:

- **Within-session determinism is not a property of the case.**
  `chinese-da-qin` gave three texts on day 1 and one text three times on day 2;
  `antikythera-absent` did the exact reverse.
- **It is not a blanket claim about the model.** `muziris-cargo` returned the
  same answer byte for byte in all six runs. Text-level reproducibility across a
  date boundary is achievable on this stack. Five cases did not achieve it.
- **FINDING 18: `vimose-runes` was internally deterministic on both days, and
  deterministic about a DIFFERENT answer on each.** One text three times on the
  24th, another three times on the 25th. That is the 2026-08-10 phenomenon
  reproduced deliberately. It did not cross a verdict boundary — this time, for
  these six cases.

**Ruling 35 exists because of that table.** `per-session 6/6 = 100%` is a
statement about VERDICTS. It reads 100% in a sweep where five of six cases
changed their answer completely, so the sentence *"the system does the same
thing on two days"* is not supported by a per-session pass, and D4 declines to
let that reading stand. A gate that failed on any text change would fail every
day and measure nothing; the scope is right and the wording has to say so.

## The floor refused, and was right about why

```
5 archived sweep(s), 96 run(s)
distinct dates 2 (floor requires 3): 2026-08-24, 2026-08-25
REFUSED. `calibrated: true` may NOT be written:
  - 2 distinct date(s), and the floor requires 3.
  - 3 sweep(s) carry no session identity and count toward no date.
```

The three pre-D4 sweeps blocking calibration is **correct behaviour, not a
nuisance**: a date assigned to them after the fact is precisely the calibration
`floor.json` already records as invalid. Neither pilot met the floor, both days,
on one case and the same one — `vimose-runes` at 0/3, and a required case must
pass every repetition.

## Two defects D4 filed rather than fixed

- **`calibrate_floor`'s report contradicted itself in its own last line**,
  printing *"re-run with --write to set calibrated: true"* directly under a
  refusal. A reader who skims to the end is invited to do the thing the report
  just refused. Fixed 2026-08-26, before Block E day 1.
- **Three vacuous proofs of the encoding fix, in a row.** The sweep prints
  PASS/FAIL rows and never prints an answer; `eval.answer_eval --archives -v`
  emitted 70,155 characters with **zero above U+024F** except em-dashes. The
  reason is not a bad flag: *there is no non-Latin output because the system has
  never produced any.* FINDING 10's guard is mutation-verified and
  **unprovable on the answer path** until the prompt asks for a source text.
  Written down as FINDING 18's corollary so no fourth attempt is made on a path
  with nothing to print.

## What D4 handed Block E

```
corpus digest    26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
sweeps archived  5, of which 2 carry session identity
distinct dates   2. Block E's first sweep is the third, and the floor becomes
                 calibratable on that day and not before
floor            NOT MET both days, on vimose-runes alone
```

Plus one instruction it did not have to give and did: **record whatever the
gateway says about the serving stack, before spending 270 calls.** Nothing in
the archive could distinguish provider drift from sampling variance, and the
text table above is exactly the observation that needs the distinction. Block E
took it up as decision 3, and the answer turned out to be that the gateway
returns nothing that could identify a stack — which is a stated limit rather
than an oversight only because it was asked before day 1.

---

# Block E — four sessions, three dates, and the day the block stopped replicating (2026-08-26 → 2026-08-28)

*Transcribed from `BLOCK_E_RESULT.md` and its appended correction, with
`BLOCK_E_DAY1_RESULT.md`, `BLOCK_E_DAY2_RESULT.md` and `BLOCK_E_RUNBOOK.md`
behind them. 396 chat calls. **Read `BLOCK_E_RESULT.md` whole before quoting any
number here** — in particular the correction appended hours after it was
committed.*

```
S1  37f79c93b79a  2026-08-26  99 runs        33 cases x 3 repetitions
S2  0c74d52b2c25  2026-08-26  99 runs        p7-answer-v2r, temperature 0,
D2  6715f2a3ab6b  2026-08-27  99 runs        haiku-4-5
D3  6a382f4f9ac7  2026-08-28  99 runs

corpus 26e4a683… asserted at BOTH ends of ALL FOUR sessions. corpus_moved None
0 incomplete, 0 retried, 0 unstable content cells, FLOOR MET, in all four
```

Day 3 was held to the morning slot on purpose: 24h 02m after day 2 and 48h 02m
after day 1 S1, the closest this design can come to a pure 24-hour and a pure
48-hour crossing measured at the same hour of the same kind of morning.

Its own summary, read alone, is the cleanest of the block — `content 72.7%,
per-case stability 33/33, unstable content 0`. **That summary is wrong about
what happened.**

## FINDING 25 — the answer text moved wholesale between the 27th and the 28th. A step, not a gradient.

```
pair       separation          within        across         lost
S1 vs S2   same date, 1.5h    169/198 85%   222/297 75%    +10.6
S1 vs D2   ACROSS,   24.0h    163/198 82%   221/297 74%    + 7.9
S2 vs D2   ACROSS,   22.5h    174/198 88%   228/297 77%    +11.1
D2 vs D3   ACROSS,   24.0h    173/198 87%   134/297 45%    +42.3
S1 vs D3   ACROSS,   48.0h    168/198 85%   135/297 45%    +39.4
S2 vs D3   ACROSS,   46.6h    179/198 90%   135/297 45%    +44.9
```

The three sessions before day 3 agree with each other at 74–77%. All three agree
with day 3 at 45%. **The separation does nothing** — doubling the elapsed time
changes the loss by less than the difference between the two 48-hour pairs
themselves. **Day 3 was not internally noisy**: its within-session agreement is
the highest of the four and its per-case stability is 33/33.

**FINDING 23 is withdrawn**, and it named its own failure condition the day
before — *"wrong if either across-date figure exceeds about +20 pts"* — with
both new figures at twice that. Its negative half survives and is strengthened:
distance across dates still buys nothing, over six pairs from 1.5 to 48 hours.
Its positive half is dead. What day 3 shows is not a date effect but a
**discontinuity located at day 3**, and the difference matters — a date effect
would predict the 48-hour pairs lose most, and they do not.

## FINDING 26 — the verdict layer is NOT invariant, two cases flipped, they cancelled exactly, and the pass rate did not move

```
oc-eo-roman-coins       S1 fail  S2 fail  D2 fail  D3 PASS
pattanam-dna-evidence   S1 pass  S2 pass  D2 pass  D3 FAIL

per-session stability   33/33 = 100%  (three sessions)
                        31/33 =  94%  (four sessions)
```

One case gained a pass and one lost one, so `content_pass_rate` reads
**0.727272… in every one of the four sessions, to every digit printed**. The
session main term estimates negative, clamps to zero, and the entire effect
lands on the interaction. **The aggregate is byte-identical across four sessions
and three dates while the set of cases behind it is not.**

This is FINDING 18's lesson one level up. Part 8 built the two-number stability
report because a single flakiness figure hid a session boundary; day 3 shows
that a single *pass rate* hides one too. A report carrying only 72.7% would have
called day 3 the cleanest replication of the block.

**FINDING 24 is withdrawn.** The prediction committed against day 3 — *"case
100%"* — failed, along with all three others, all in the same direction, all by
a wide margin. They were committed at `4860711` **before day 3 ran**, for the
reason `BLOCK_E_DAY1_DRYRUN` gives: a prediction made before the run is
evidence, and the same observation made afterwards is a story.

## FINDING 27 — it is generation-side. Retrieval held.

```
30 of 33 evidence blocks BYTE-IDENTICAL in every session
 3 moved: akananuru-yavana-ships-tamil, pattanam-dna-evidence,
          weilue-ruler-selection
```

91% of cases were handed the same prompt and the same evidence in every session,
at temperature 0, and **55% of the answer text changed anyway**. The two verdict
flips split cleanly on this: `pattanam-dna-evidence` is one of the three whose
evidence moved and therefore has a retrieval explanation available;
`oc-eo-roman-coins` is one of the thirty that did not, and **that flip has no
explanation in this archive at all**.

## The floor is calibrated, for the first time in this project

```
calibrated            true   (was false since 2026-08-10)
calibrated_at         2026-08-28T10:51:56+00:00
from                  2026-08-26, 2026-08-27, 2026-08-28 — 4 sessions
per_case              132/132 = 1.000
per_session            31/33  = 0.939
excluded by rule      five sweeps, each with the reason it fails
```

**The 94% is IN THE FILE.** The write was defensible only on that condition: the
two flipped cases are recorded in the artefact the floor was calibrated from,
not buried under a pass rate that did not move. It was taken rather than
declined on the ground `calibration_scope` already states in its own
anti-loophole — *a sweep that satisfies the rule cannot be excluded by name*,
because otherwise the list is *"a place to put a sweep whose numbers nobody
liked."* Declining a gate that passes, on the strength of a finding made the
same morning, is that move wearing the other hat. The gate's three required
cases went 12/12 through the very session that changed 55% of the answer text,
which is precisely what a regression gate is for.

**Gate G4 is closed**, all five boxes, and the deliverable was the variance
decomposition rather than the pass rate — which on the last day of the block
stopped being a slogan and became the finding.

## The serving stack, and a correction that arrived hours later

The probe was run before day 1 and after day 3 and both readings were
`{"id": …, "model": "anthropic/claude-haiku-4-5-20251001"}` with no
`system_fingerprint`. **Then correction 8 established that the probe had
bypassed the alias**: `resolve_model_label()` reads `gateway/config.yaml` off
the local disk and never asks the gateway anything, so the probe sent the
concrete model name it had just read out of a file in this repository and the
gateway echoed it back. Every Block E archive carries `"model": "chat-default"`.
**The two readings either side of the block are two echoes of a locally-read
config value, taken on a path the archives were not made on.**

This *strengthens* the section's conclusion rather than weakening it. The limit
stated before day 1 — provider drift and sampling variance are not separable in
these archives — is still true, and now true for a plainer reason:
`_serving_stack`'s `model` is the echo of the string sent, in every path, and
cannot move unless the caller moves it. Findings 25, 26 and 27 stand unchanged.

## The freeze, and the eight corrections it accumulated

Block E ran under a freeze: anything found mid-block was **written down rather
than fixed**, so that day 3 replicated days 1 and 2 rather than a tree that had
moved underneath them. Seven corrections were owed at the close and an eighth
was found while applying them. All eight landed at `1bdaf04`, and two of them
are worth carrying forward:

- **Day 2's capture is mojibake and day 2's result document says the opposite.**
  `eval/block-e-day2.txt` holds Γ×40, Ç×40, ö×39 — UTF-8 em-dashes read back
  through CP850. Days 1 and 3 hold the same characters intact. **No measurement
  is affected**: the archives are JSON written to disk with an explicit encoding
  and never pass through the console. The watch item was also miscast from the
  start — no character beyond ASCII punctuation appears in ANY of the three
  captures, because the sweep prints case ids, PASS/FAIL rows and serving-stack
  JSON and nothing else.
- **The 99 "distinct serving stacks" line** was the per-call `id` inside the
  identity, not a provider changing under the run — and it would have looked
  identical on a day when a provider *had* changed, which is that correction's
  real cost.

## What Block E measured, and what it did not

It set out to ask whether the answers this system gives can be improved on
purpose. It answered a narrower question and answered it well: **you cannot
tell, from a pass rate, whether anything moved.** It could not answer why, and
that was known and written down on 2026-08-26, before the first call.

---

# Block F opens with a decision block, not with curation (2026-08-28)

*The four decisions `BLOCK_F_START.md` left open on purpose, settled before F1.
Full reasoning in `F0_RESULT.md`; rulings 36–42 in `F0_RULINGS.md`, indexed in
`RULINGS.md`. None of this is Block F.*

```
b42ba43  the four decisions, and the arm the archive never recorded
bee344e  the stale stand-in, and the mutation that passed for the wrong reason
3dfcae1  rulings 40-42: the article, the exclusion, and Ardashir
2091e03  the harnesses: mojibake, a discarded return code, and an LF source
         converted in a commit
```

## The finding that reshaped the block: THE ARM WAS NEVER RECORDED

Not one of the nine archived sweeps records which **model** or which
**temperature** produced it. Every Block E number is denominated in an arm that
was a fact about the code on the day rather than about the file — **FINDING 14
one layer up**, and invisible for the same reason: while only one arm has ever
run, the field cannot be missed.

That gap was not merely untidy, and this is the part worth carrying:
`calibration_scope`'s own anti-loophole, `a_named_sweep_must_actually_fail_the_rule`,
refuses an exclusion naming a sweep that SATISFIES the rule. The rule had two
clauses — a session identity, and ≥30 cases. **A sonnet arm at temperature 1
satisfies both**, and `calibrate_floor` globs `eval/sweeps/*.json` and pools
every row it finds. **The guard built to stop inconvenient numbers being hidden
would have made a temperature-1 sonnet sweep impossible to exclude from a floor
calibrated on greedy haiku.**

Ruling 36 closes it before the arm runs. The arm is now `(alias, temperature)`,
recorded on the sweep archive and every row, part of the scope rule, and refused
as a pooling input to the decomposition. The nine legacy archives get their arm
**reconstructed** — alias read from `serving_stack.model`, which correction 4
established is the echo of the string SENT and therefore useless as a drift
detector and faithful as a record of what was asked for; temperature **assumed**
0 and labelled as assumed, because `assemble` had no temperature parameter until
2026-08-28. A sweep archived after that must state its arm or fail.

## The other three decisions

- **G3 is amended in advance** (ruling 39): per-session stability and
  cross-session answer-text agreement at 60, beside the pass rate. Gated on
  Block F's OWN sessions at 60 — Block E's 74–77%/45% were generated over 24
  records and a cross-corpus comparison would be measuring the corpus move it
  was written to survive. **It costs a second session on a second date, ~198
  calls, and the days are booked with the amendment.**
- **One bar governs promotion and reinstatement** (ruling 37): 3/3 in each of
  three sessions on three distinct UTC dates, at the corpus in force. Raised
  from two-on-two by FINDING 26. Three is `min_distinct_dates`, reused rather
  than invented. `weilue-chinese-quotation` leaves `known_failing_cases` — it
  does not fail — for a new `promotion_candidates` state (ruling 38) rather than
  `required_cases`, because its twelve passes are denominated in a corpus Block F
  is about to replace.
- **The assertions were measured rather than argued about.**
  `scripts/assertion_audit.py` re-reads the 396 archived runs against the
  assertions that failed them, at zero chat calls.

## What the assertion audit found, and it was three different defects

All four cases `BLOCK_F_START` named fail **0/12, deterministically, each on
exactly one assertion**:

```
oc-eo-cattigara        refused correctly 12/12 and SAID "Ptolemy's Cattigara" —
                       inside the sentence declining to claim it. RULING 41.
aksumite-coin-imagery  every content assertion passes; both quotations are in
                       the record, case-folded, one word away. The model wrote
                       "a half-length bust…" where the record has
                       "Half-length bust…". RULING 40.
skz-titulature         good answer, four resolved quotations, fails only on
                       ['Ardashir']. The record's §1 IS one titulature formula
                       and the answer quoted from it and stopped at Shapur's own
                       epithets. RULING 42 — tracked, not corrected away.
raqosh-epitaph         states one reading of a disputed text with no hedge. NOT
                       an assertion defect; the gloss arm's teeth are in the
                       right place.
```

**Ruling 41 then turned up a second case while it was being written.**
`antikythera-absent` — REQUIRED, passing 12/12 — excluded *"Antikythera
mechanism was built"* against its own question *"When was the Antikythera
mechanism built?"*. One refusal phrasing from the same failure, with nothing
anywhere that would have said why. That is the argument for a rule rather than a
correction, and the rule is now enforced at load time.

## The harnesses, and three defects PROGRESS.md had already named

Ruling 40 added one guard label containing an em-dash and one mutation that
crashes. Between them:

- **`mutate_ui_places` restored its source with `write_text` and converted
  `ui/build_ui_data.py` from LF to CRLF on a live run**, and its restore check
  compares TEXT so it could not see it. The conversion reached commit `3dfcae1`
  and was undone in `2091e03`. **This section of PROGRESS.md predicted it
  exactly** — *"three of six are exposed, and only by the accident of which
  files are CRLF"* — and named the remedy. All six harnesses now restore and
  compare BYTES. `mutate_places` was the other ACTIVE exposure and had simply
  not been run that day.
- **`mutate_part7b` and `mutate_ui_places` decoded their suites' stdout with the
  locale codec.** Every em-dash came back mojibake and a guard label holding one
  could never match its own failure line; both printed MISS on mutations that
  had worked perfectly. FINDING 10's family, at the parent-decoding-child
  boundary.
- **`mutate_part7b` discarded the child's return code**, so a mutation that
  KILLED the suite was reported as "expected <guard> to fail, got no failures".
- **And one that was found by accident and matters most.** On the first run
  after the arm work, eight checks failed on their own account, and one
  mutation named a guard that was among the eight. It reported `ok`. Its guard
  did fail — it had been failing before the mutation was applied. **A green
  mutation against a red baseline is a vacuous proof**, and it happened inside
  the instrument built to catch vacuous proofs. `mutate_part8`,
  `mutate_part7b` and `mutate_ui_places` now run their suites once unmutated and
  mark any mutation naming an already-failing guard **UNVERIFIED**.

---

# State at the close of F0 (2026-08-28)

```
tree            2091e03 plus the rulings-register catch-up, clean
corpus          24 records / 450 embedded / 0 pending
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                the denominator of all 396 Block E runs, and of the sonnet arm
                if it runs before F3

ANSWER          eval.test_answer_eval       321   GREEN   (was 292)
mutations       scripts\mutate_part8.py      75   GREEN   (was 66)
                scripts\mutate_part7b.py     18   GREEN   (was 15)
                scripts\mutate_ui_places.py   4   GREEN   (was 3)
RANKING         eval.test_ranking_check     236   GREEN
mutations       scripts\mutate_ranking.py   100   GREEN
PART 7          answer.test_answer                GREEN
UI              ui\test_build_ui_data.py         GREEN
--verify        resolved 849, case_folded 26, article_added 0, case_only 9,
                moved 1, absent 1 — the last two are the 2026-08-10 recovered
                run D1 diagnosed and cannot explain

gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
floor           calibrated TRUE, per_case 132/132, per_session 31/33
required        antikythera-absent, chinese-da-qin, muziris-cargo
known-failing   aksum-exports, vimose-runes, skz-titulature
candidate       weilue-chinese-quotation
rulings         1 to 42, indexed in RULINGS.md
gates           G4 CLOSED. G3 is Block F's, amended in advance.
```

## Open, and deliberately not closed

- **The sonnet arm has not run**, and the frozen-corpus window closes the moment
  the first sub-tranche lands. 33 cases × 5 repetitions at temperature 1 through
  `chat-strong`, one session, archiving to `eval/arms/`, never folded into the
  haiku archive. It is the only item in Block F with a hard deadline.
- **Two days at 60 records are owed by the G3 amendment** and should be in a
  calendar before F3, not discovered on the last afternoon of the block.
- **`aksum-exports`, `vimose-runes` and `skz-titulature` are open defects**,
  tracked and never subtracted from a floor verdict.
- **FINDING 11 is still open**: `ingest/fidelity.py`'s hint list is stale for two
  records and its justifying comment is disproved. Needs a re-ingest.
- **Rulings 20 and 21 still have no full text.** The code is the authority.
- **The answer path has still never quoted a non-English source text**, so
  FINDING 10's guard remains unprovable there.
- **`_to_delete/` holds 148 MB** of staging tarballs. Gitignored; nothing
  depends on any of it.

## The sentence that travels

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310.

**Four sessions read 0.727272… and one of them was different. The pass rate
cannot see change.**

And one from 2026-08-28, which travels with them now:

**Nine archives, 396 runs, and not one of them recorded which model answered.**

---

# F1 — the tiering policy, and the suite nobody was listing (2026-08-29)

*Rulings 43–45 and findings 30–31, full text in `F1_RULINGS.md`, indexed in
`RULINGS.md`. F1 declares and does not curate: the corpus is unmoved and
`26e4a683` was CHECKED at the close rather than assumed.*

## The three tiers could not hold the corpus that already existed

`PHASE2_PLAN` F1 asks for a tiering policy and a target mix across the 36 new
records. Running `ingest.loader` over the 24 first, before writing anything:

```
verbatim_with_provenance   11
published_translation_only  1
catalogue_record           11
NEITHER                     1   arabia-02-palmyrene-tariff
```

And the tier F3–F7 explicitly PREDICTS becomes the common case — source-language
text with no published English, where `resolve_english` starts choosing
`machine` — had no name in the table at all. **A mix cannot have a target for a
tier that cannot be written down**, so F7 would have found the mix unaccountable
rather than unmet. Ruling 43 declares five: the two above, plus
`verbatim_machine_english` and `pointer_only`. Ruling 38 one level over.

## G3 has a box that ticks itself, and F1 was the last moment to say so

**"Curation cost per record recorded and trending down" is satisfiable by
curating cheaper records.** A museum object record is the cheapest thing in this
corpus to produce and a cited bilingual inscription the dearest; the box cannot
tell *the same kind of record got cheaper* from *we made more of the cheap
kind*, and kill trigger 3 hangs off the number. Ruling 45 amends it in advance —
cost PER TIER, against the declared mix — because F2 starts the column at record
25 and **nobody times a record twice**. FINDING 26's shape: an aggregate that
moves for two reasons reports one number.

## The digest question, asked before the file was written

A `tier` key on a seed record would have moved `corpus_digest`:
`canonical_record_text` hashes the whole parsed record with sorted keys. That is
the denominator of 396 Block E runs and 165 arm runs. So the declaration is a
sidecar — and not under `data/seed_corpus/` either, because `iter_seed_records`
refuses a `.json` at that depth. **The layout guard fired on the first file
anyone has tried to add since it was written.**

## FINDING 31 — `ingest.verify` had been RED for a week

```
FAILED (1)
  x manifest-flagged record 'weilue' is labelled verbatim_original
```

One claim held in three places — the manifest's prose,
`fidelity.PARAPHRASE_ID_HINTS`, `verify.MANIFEST_FLAGGED`. FINDING 11 corrected
one of the three on 2026-08-22 with the reason written down. The other two were
never told, and the check has been failing through D4, Block E's four sessions
and 396 runs, F0 and the sonnet arm.

**Nothing caught it because no state block in this repository lists
`ingest.verify` among the suites**, and `PHASE2_PLAN` F3–F7 makes it the FIRST
line of the block run after every sub-tranche. F3 would have curated nine
records and met a red suite that had nothing to do with them.

Fixed by deleting the second OPINION, not the check: the assertion now runs over
fidelity's own list, and a lift is a written entry with a reason that
`check_paraphrase_flags` refuses to accept without one. *Two ends of a
comparison must not hold two definitions of the thing being compared.*

## FINDING 30 — and one that only a reader could ever have found

`weilue-chinese-quotation.archived_status` still said the case was tracked in
`floor.json.known_failing_cases` as an open defect, and that no archived answer
has quoted its Chinese. Ruling 38 moved it to `promotion_candidates` on
2026-08-28 on evidence that says the opposite. `archived_status` is prose,
deliberately outside `_ASSERTION_KEYS`, and read by no check anywhere.
Corrected in place; the load-time check deferred to F2 in writing, on FINDING
29's precedent.

---

# State at the close of F1 (2026-08-29)

```
tree            a6442b6 plus one F1 commit, clean
corpus          24 records / 450 embedded / 0 pending   UNMOVED BY F1
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                RECOMPUTED at the close and matched. F3 moves it.

ANSWER          eval.test_answer_eval       333   GREEN
RANKING         eval.test_ranking_check     236   GREEN
PART 7          answer.test_answer                GREEN
UI              ui\test_build_ui_data.py         GREEN
INGEST          ingest.verify                    GREEN  <- first time since
                                                        2026-08-22, FINDING 31
TIERS           ingest.test_fidelity         30   GREEN  <- new
mutations       scripts\mutate_part8.py      82   GREEN
                scripts\mutate_part7b.py     18   GREEN
                scripts\mutate_ui_places.py   4   GREEN
                scripts\mutate_ranking.py   100   GREEN
                scripts\mutate_fidelity.py   24   GREEN  <- new, with BASELINE

record tiers    11 verbatim_with_provenance / 0 verbatim_machine_english /
                1 published_translation_only / 11 catalogue_record /
                1 pointer_only
target at 60    25 / 10 / 5 / 19 / 1, region levelling to 8-9 each,
                >= 4 source-language records per region, 8 gloss-capable,
                >= 6 expect_quoted_from_original cases

gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
floor           calibrated TRUE. ELIGIBLE, 4 sweeps, 3 dates — UNMOVED
rulings         1 to 45.  findings 1 to 31.
gates           G4 CLOSED. G3 is Block F's, amended twice in advance
                (ruling 39, ruling 45).
```

## Open, and deliberately not closed

- **F2 has not started the cost column.** Ruling 45 says what it must carry.
- **FINDING 30's load-time check** is deferred to F2, in writing.
- **Three harnesses still lack the BASELINE check**: `mutate_ranking`,
  `mutate_places`, `mutate_recover`.
- **`ingest/verify.py` check 9 asserts `len(docs) == 24`** and F3 breaks it on
  purpose. Left as written: loosening a count check in advance of the records
  is the floor lowered to what is currently passing.
- Everything carried into F1 is carried out of it: ruling 40's `article_added`
  unverified against a live run, `muziris-cargo` at 3/5 on the arm,
  `--archives` pooling arms, and G3's second session at 60.

## The sentences that travel

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310.

**Four sessions read 0.727272… and one of them was different. The pass rate
cannot see change.**

**Nine archives, 396 runs, and not one of them recorded which model answered.**

**36% and 27% are not two refusal rates. They are two rates of uttering one
sentence.**

And two from 2026-08-29:

**Cost per record trending down is not a fact about efficiency until the mix is
held. The cheapest record in this corpus is the one that teaches a reader the
least.**

**A suite that no state block lists is a suite that can be red for a week, and
this one was the first line of the runbook that would have found it.**

---

# F2 — the column, and the comparator nobody had measured (2026-08-29)

*Rulings 46–48 and finding 32, full text in `F2_RULINGS.md`, indexed in
`RULINGS.md`. F2 builds the instrument and declares what it is allowed to mean;
it times no record, because the column starts at record 25 and that is F3's.
The corpus is unmoved and `26e4a683` is unchanged.*

## Kill trigger 3's comparator does not exist

> *"if record 60 costs what record 12 cost, 200 is a staffing question rather
> than an engineering one"* — `PHASE2.md`, repeated by `PHASE2_PLAN` F2.

**Nothing anywhere records what record 12 cost.** The seed 24 were curated
across Parts 3 to 7, before any column existed. There is no minutes figure for
any of them in any file and none can be reconstructed, so one of the trigger's
two terms has never been measured.

Ruling 46 amends it **before the first number**: a trend across records 25 to
60, per tier, in curation order, with n printed beside it — and it is written
down as **a weaker claim than the trigger as written**. Two ways of
manufacturing the missing term were refused. Re-timing seed records measures
re-doing a solved record, which is systematically cheap in exactly the phases
that dominate curation and would bias the trigger toward *costs have not
fallen*; a comparator whose error has a direction is worse than none, because
the number it produces looks like evidence. Reconstructing estimates was
refused for ruling 39's reason in its purest form.

The n travels with the claim. `min_n_to_read_as_a_trend` is 10, declared with
its consequence rather than discovered at G3: **`published_translation_only` (4
new) and `catalogue_record` (8 new) can never be read as trends inside Block
F.** Two of the four moving tiers can carry the claim, and the report prints
`NOT A TREND (n=4, floor 10)` for the rest.

## A single minutes figure is ruling 45's defect one level down

Cost "trends down" the moment source-hunting becomes research, or rights
checking stops being timed, or gold-case writing moves out into "eval work".
Ruling 45 closed an aggregate satisfied by curating cheaper records; this is an
aggregate satisfied by **counting less of the record**. Ruling 47 fixes seven
phases before the first record is timed — `source_hunting`,
`rights_and_licence`, `text_capture`, `translation_and_fidelity`, `placement`,
`authoring`, `rework` — and `check_ledger` refuses a record entry that omits
one. **A phase that went to zero has to say zero**, so the fall lands in the
phase that stopped. `rework` is in the list because without it the cheapest
curation strategy is the one that fails verification.

Ruling 48 keeps a clocked minute and a remembered one apart: an estimate needs
a written reason, a part-clocked cell is an estimate, a measured span above 240
minutes is refused, and an open clock fails `ingest.verify`. Ruling 36's shape
one level down — recorded and reconstructed are two kinds of knowledge.

## The ledger is the SECOND file that would have moved the digest

`data/curation_cost.json` is a sidecar for ruling 43's reason, unchanged and
not expiring: a `minutes` key would change every `content_hash` and therefore
`corpus_digest`, the denominator of 396 Block E runs and 165 arm runs. And not
under `data/seed_corpus/` either, because `iter_seed_records` refuses a `.json`
at that depth. Seven days after the tier declaration hit the same two walls.

`ingest.verify` check 13 makes the coverage bidirectional: every record in the
corpus is either timed or excused with a written reason, never both. That is
what makes *nobody times a record twice* enforceable rather than aspirational —
a record F3 ingests without a ledger row turns the suite red in the same run
that first loads it, which is the only moment its minutes still exist.

## FINDING 32 — the deferred check could not be built as deferred

F1 deferred FINDING 30's check **and specified it**: one token
(`known_failing_cases`) tested against one file. Built that way it fires on
F1's own correction, which says truly that *ruling 38 moved it OUT of
`floor.json.known_failing_cases`*. **A check whose first true positive is a
false one is a check somebody switches off in a week.**

The claim moved out of the prose and into `floor_state` — one token, four
values, declared in the case and held in `floor.json`, refused when they
disagree, in both directions, with absent meaning `none`. `archived_status` is
untouched and both fields stay outside `_ASSERTION_KEYS`, so **no archived run
is re-scored**. Seven cases now declare; the ANSWER suite went 333 → 343 and
stayed green.

## A mutation harness was killed mid-mutation and left one on disk

`scripts/mutate_part8.py` run through the device bridge was killed by the
bridge's call timeout **between applying a mutation and reaching the `finally`
that restores the sources.** `eval/answer_eval.py` sat in the working tree with
`for doc_id in case.expect_quoted_docs:` mutated to `for doc_id in []:` — every
quotation assertion in the scorer disabled, and every suite still reporting
green because none had been re-run. Found by `git status`; restored with
`git show HEAD:` writing bytes back, because **`git checkout --` fails through
the bridge, which cannot unlink.**

## Two counts that had drifted, both transcribed

`F2_START` says **"FIVE SUITES, not four"** directly above a list of six. The
sentence was true when F1 wrote it and `ingest.test_fidelity` made it false the
same day. With `ingest.test_cost` there are **seven**. It is F1's own closing
correction — one claim held in more than one place, one copy maintained —
reappearing in the document that recorded it, eight hours later.

F1's owed list says the BASELINE check is in "four harnesses of seven". It is
now five; the denominator of seven excludes `mutate_distractors`, which mutates
a live database view rather than a source file.

---

# State at the close of F2 (2026-08-29)

```
tree            577a0e2 plus one F2 commit, clean
corpus          24 records / 450 embedded / 0 pending   UNMOVED BY F2
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                UNMOVED. F3 moves it.

SEVEN SUITES. F2_START said five above a list of six; this is the corrected
count and it is the list, not a sentence about the list.
INGEST          ingest.verify                    GREEN   <- FIRST, always
TIERS           ingest.test_fidelity         30   GREEN
COST            ingest.test_cost             46   GREEN  <- new
ANSWER          eval.test_answer_eval       343   GREEN  <- was 333
RANKING         eval.test_ranking_check     236   GREEN
PART 7          answer.test_answer          150   GREEN  <- was uncounted and
                                                  carried ONE SKIP; sqlglot
                                                  installed, and the suite now
                                                  prints its own count
UI              ui\test_build_ui_data.py     14   GREEN  <- was uncounted too;
                                                  now prints its own count

mutations       scripts\mutate_part8.py      87   GREEN  <- was 82
                scripts\mutate_ranking.py   100   GREEN
                scripts\mutate_cost.py       37   GREEN, with BASELINE  <- new
                scripts\mutate_fidelity.py   24   GREEN, with BASELINE
                scripts\mutate_part7b.py     18   GREEN, with BASELINE
                scripts\mutate_ui_places.py   4   GREEN, with BASELINE

cost ledger     data/curation_cost.json
                0 records timed / 24 excused with a written reason
                comparator: within_tranche (ruling 46)
                7 phases, fixed (ruling 47)
                min_n_to_read_as_a_trend 10; two of four moving tiers can
                carry a trend at all

record tiers    11 verbatim_with_provenance / 0 verbatim_machine_english /
                1 published_translation_only / 11 catalogue_record /
                1 pointer_only
target at 60    25 / 10 / 5 / 19 / 1, regions levelled to 8-9, >= 4
                source-language records per region, 8 gloss-capable,
                >= 6 expect_quoted_from_original cases

gold cases      33   22 answerable / 3 gloss / 8 correctly_refusable
                7 now declare a floor_state, checked against floor.json
floor           calibrated TRUE. ELIGIBLE, 4 sweeps, 3 dates — UNMOVED
rulings         1 to 48.  findings 1 to 32.
gates           G4 CLOSED. G3 is Block F's, amended THREE times in advance
                (ruling 39, ruling 45, ruling 46).
```

## Open, and deliberately not closed

- **No record has been timed.** F3 curates the first one the column measures,
  and the first record is also the first real test of the CLI.
- **The BASELINE check is in five harnesses of eight.** `mutate_ranking`,
  `mutate_places`, `mutate_recover` still lack it.
- **`ingest/verify.py` check 9 asserts `len(docs) == 24`** and F3 breaks it on
  purpose, in the same commit as the records or not at all.
- Everything carried into F2 is carried out of it: ruling 40's `article_added`
  unverified against a live run, `muziris-cargo` at 3/5 on the arm,
  `--archives` pooling arms, and G3's second session at 60.

## The sentences that travel

29/30 is whether the RECORD was found. 22/30 is whether the NON-ENGLISH TEXT was
reachable. `muziris-cargo-akananuru` still sits at rank 310.

**Four sessions read 0.727272… and one of them was different. The pass rate
cannot see change.**

**Nine archives, 396 runs, and not one of them recorded which model answered.**

**36% and 27% are not two refusal rates. They are two rates of uttering one
sentence.**

**Cost per record trending down is not a fact about efficiency until the mix is
held. The cheapest record in this corpus is the one that teaches a reader the
least.**

**A suite that no state block lists is a suite that can be red for a week.**

And four from F2:

**Kill trigger 3 compares record 60 against record 12, and nobody ever wrote
down what record 12 cost.**

**A number is safe from re-labelling only if the thing underneath it is
recorded too — the tier, then the phase, and there is no third level because
nobody times a record twice.**

**A check deferred WITH its implementation described is a check specified
before it was tried, and F1's own correction is what it would have fired on.**

**A suite that prints no count can carry a skip forever, because nobody can
tell one skipped assertion from thirty. Two of the seven were printing
none.**

---

# F3 — the clause the floor did not have, and a date nobody had booked (2026-08-31)

**Three decisions, all recorded BEFORE record 25 is ingested.** `F3_RULINGS.md`
carries the full text of rulings 49-51 and FINDING 33; this is the summary and
the state.

**Ruling 49 — the corpus is part of the calibration scope.** `floor.json`
gained a `corpus` clause: a seed record count and a digest, checked exactly as
ruling 36's arm clause is, optional in the same way, and refused at load if
half-declared. The defect it closes is not that a 33-record sweep might
calibrate the floor by accident — it is that the file's own anti-loophole,
`a_named_sweep_must_actually_fail_the_rule`, would have **INSISTED** on it: a
sweep at 33 records satisfies every other clause, so it could not have been
excluded by name. Measured before the clause was written: all four archives the
floor stands on carry `seed_record_count 24` in their own `corpus_version`
block, put there by FINDING 14 so that a corpus which moved could not go
unnoticed, and `eval/calibrate_floor.py` contained **zero occurrences of the
string "corpus"**. The data was on disk for three weeks and the rule did not
read it.

**The floor is NOT suspended for the tranche.** A run at a moved corpus still
computes a verdict on `required_cases` — that verdict is the regression reading
— and what it may not do is re-calibrate. `calibrate_floor` still reports
ELIGIBLE at this commit, which is checked rather than asserted: a rule that
de-calibrated the floor by arriving would be a rule that lowered the thing it
was written to protect.

**Ruling 50 — the third UTC date at 60 is booked, as a NINTH session.** Three
rules in this repository require three sessions at 60 on three distinct dates:
`min_distinct_dates`, the promotion bar governing `weilue-chinese-quotation`,
and `vimose-runes`'s reinstatement condition. G3's amendment booked two. That
is FINDING 33, and its shape is FINDING 14's one level up from data: a quantity
that has to agree across three declarations, maintained in three places, with
nothing computing the sum — two of the three written on the same day, in the
same file, by the same decision list. `PHASE2_PLAN.md` now carries the session
count and the three rules that set it in one place. **The F8 spike was NOT
spent on it:** the two records it would promote are the corpus's only
`pointer_only` record and its companion, and trading them for a calibration
date is paying for a measurement with the thing being measured.

**Ruling 51 — a sub-tranche re-runs the RANKING check and a floor PROBE.**
`PHASE2_PLAN`'s F3-F7 heading said "re-running the sweep at each" and its own
command block said the ranking check; read the heading the other way and it is
~198 chat calls four or five times over, on top of three sessions at 60. The
command block is what F3-F7 do, and the argument is not only cost: **a full
sweep at 33 records produces a number no rule here may read** — it cannot
calibrate (ruling 49), cannot promote or reinstate (the bar says at 60), and G3
asks for nothing at 33, 42 or 51. The floor's mid-tranche reading is a probe of
the three required cases at `min_repetitions`, ~9 calls, archived to
`eval/probes/` and never to `eval/sweeps/` — **so it cannot calibrate by
construction**, and `excluded_by_rule` does not grow one entry per sub-tranche.
The directory is the rule; the scope clause is still the guard.

**And the 36 records are ALLOCATED.** `target_mix.allocation` places every one
as a slot — region, tier, count — over F3 to F7, and `ingest.verify` FAILS if
the slots do not deliver the declared mix. Southeast Asia's four
source-language records go first because it has zero today; every
source-language record is curated before every catalogue record, and the check
refuses an allocation where that is not true. **That biases the aggregate cost
per record downward by construction, which is why ruling 46 already reports per
tier and in curation order** — said here so nobody at G3 reads a falling total
as efficiency.

## State at the close of F3 (2026-08-31)

*Every number below was printed by the thing it describes, through the device
bridge. The bridge runs a different interpreter from the host venv and one
number differs because of it, which is said where it happens rather than
smoothed over.*

```
tree            F3's commit, on top of
                51e0f21  F3_START names the commit it was written at
                a74a307  F2: a column that cannot be gamed
corpus          24 records / 59 chunks    STILL UNMOVED
digest          26e4a683014bdf8a3dff98d48865a61869d137853333b82d024220c18eda9b28
                >>> F3 declared the rules for moving it and did not move it. <<<

SEVEN SUITES
INGEST          ingest.verify                    GREEN   <- FIRST, always
                                                 + allocation note (ruling 51)
TIERS           ingest.test_fidelity         42   GREEN   was 30, +12
COST            ingest.test_cost             46   GREEN
ANSWER          eval.test_answer_eval       360   GREEN   was 343, +17
RANKING         eval.test_ranking_check     236   GREEN
PART 7          answer.test_answer          149   GREEN, 1 SKIPPED through the
                                                  bridge: sqlglot is in the HOST
                                                  venv, not this interpreter.
                                                  F2 measured 150 on the host;
                                                  F3 did not re-run it there.
UI              ui\test_build_ui_data.py     14   GREEN

mutations       mutate_fidelity  35  +11, all eleven verified here in three
                                     slices (the suite costs 3.9s)
                mutate_part8     94  +7, and the full harness RAN on the host
                                     after the commit: all seven caught by
                                     their own guard.
                TOTAL           288  six harnesses on the host at a1af62d,
                                     no MISS, no UNVERIFIED, no BASELINE block
                                     in any of them, sources restored byte for
                                     byte, git status empty afterwards.
                                     Was 270 at the close of F2.

cost ledger     0 records timed / 24 excused. Comparator within_tranche.
floor           calibrated TRUE, ELIGIBLE, 4 sweeps, 3 dates, all at 24 records
                and now SAYING SO in the rule as well as in the archives.
allocation      F3 8 / F4 7 / F5 7 / F6 7 / F7 7 = 36
rulings         1 to 51.  findings 1 to 33.
gates           G4 CLOSED. G3 is Block F's, amended FOUR times in advance
                (rulings 39, 45, 46, and now 50 and 51 together).
block           NINE sessions, not eight.
```

## Open, and deliberately not closed

- **RECORD 25 EXISTS. The corpus is 25 records and the digest has moved.**
  `seasia-04-dong-yen-chau` — the Đông Yên Châu inscription, Old Cham in
  Pallava script, c. 350 CE, the oldest attested text in any Austronesian
  language — is the first record this project has added since Part 7 and the
  first ever curated with a clock running. **Southeast Asia goes from ZERO
  source-language records to one**, which is why all four of its gold cases
  sat on find records. `ingest/verify.py` check 9 is raised 24 → 25 in the
  same commit as the record, which is the only way F2 permitted it to move.
  The record derives `verbatim_with_provenance` from its own content.
  **11.7 minutes**, and the report prints what ruling 48 asked it to: 9.1
  measured, 2.6 estimated, 22% remembered, decomposed across all seven phases,
  `NOT A TREND (n=1, floor 10)`, and `NOT YET A COST CLAIM` because the mix is
  unmet. Every one of those sentences was written before the first minute was
  timed.
- **A new language costs a declaration in two modules, and it fails at the
  WRONG END.** `ocm` had to be added to `answer.translate.LANG_NAMES` and
  `TRANSLITERATED_LANGS`, or `retrieve.render.required_script` raises and
  ruling 12 renders every query into every non-English index language — so the
  failure lands at `eval.run_ranking_check`, not at ingest. Every sub-tranche
  that introduces a language pays this, and F4–F7 introduce several.
- **Two guards encoded a frozen corpus as an invariant, and record 25 turned
  both red.** `GUARD the measured histogram the target mix is arithmetic over
  still holds` counted the LIVE corpus against `measured_at_24`, which is a
  SNAPSHOT taken at digest 26e4a683; it now counts over the ledger's excused
  seed set. `GUARD every seed record is excused from the column and none is
  timed` asserted the column was EMPTY, true from F2 until the column was
  first used. What replaced it is stronger: **the excused list is frozen, and
  a record excused after the column opened is the column being routed
  around** — a curator who does not want to time a record can satisfy
  coverage by excusing it, and nothing else here would notice. Neither guard
  was named in advance the way check 9 was, and both were rework by ruling
  47's definition, clocked as such.
- **`verify`'s placement note read `25/24 considered`** the moment the corpus
  passed G1's target, because a moving quantity was printed over a closed
  gate's constant. At 60 it would have read `60/24`. Same defect as the
  sentence that read "nine archives, 396 runs" while the archives held 492.
- **RULING 52, and the column opened.** `cost_log start seasia-04-vo-canh
  source_hunting` at 08:18 UTC is the first curation minute this project has
  ever recorded. The hunt those minutes measured is what ruled Võ Cạnh out —
  no open transliteration is published for it — so 2.6 measured minutes were
  filed against a record that will never exist, `ingest.verify` went red on
  the stale row, and the CLI had no way to correct one. **Source hunting is
  the phase that decides which record exists, so the clock cannot be started
  against the right id until the phase it is timing is over**, and that is
  true of all 36 records. `cost_log retire` keeps the row and its written
  reason rather than deleting it; the minutes are re-filed with `add` as
  ESTIMATED, because a span measured against an id the hunt had not settled is
  not a measurement of the record that landed. **The anti-loophole is the
  whole design: a row may be retired only if its record is NOT in the
  corpus**, or retirement takes the expensive records out of the column kill
  trigger 3 reads. Its own mutation then found that the required-terms guard
  loops over `LEDGER_REQUIRED` and can never see a term LEAVE it — true of all
  six original terms, and now declared independently in the suite.
  `ingest.test_cost` 46 → 59, `mutate_cost` 37 → 48 — and the report now
  NAMES every retired row with its minutes and its written reason, because
  a retired row no report mentions is a row that vanished.
- **FINDING 36: the BASELINE check found a red suite on its first run.**
  `scripts/test_recover_baseline.py` fails — `run_answer`'s archived payload
  grew `corpus_version` (D4) and `serving_stack` (Block E) and
  `recover_answer_baseline.ABSENT` was never extended, so the suite has been
  red for a week, through every session of Block F, **and no state block
  listed it**. FINDING 31 one suite over. It needs psycopg and so runs only on
  the host, which is part of how it stayed invisible; it is now listed as the
  EIGHTH suite. `serving_stack` is named ABSENT as unrecoverable, which it is.
  `corpus_version` is named as a DEFERRED DECISION, because `answers` holds
  the digest and the cited hashes and a partial block could be rebuilt —
  whether a recovered payload may carry a corpus identity missing
  `seed_record_count` is a question ruling 49 has just made load-bearing, and
  it belongs to F4 rather than to the last hour of F3. The guard's label also
  carried its own detail, so the mutation read MISS instead of UNVERIFIED;
  the label is bare now.
- **FINDING 37: seven mutations that worked perfectly were reported MISS.**
  `mutate_places` ran its child without `encoding`, so UTF-8 em-dashes in
  guard labels came back mojibake and no label matched. FINDING 10's family,
  already fixed in `mutate_ranking` and already written down in
  `ingest/test_fidelity.py`'s header — it survived here because this harness
  had not been run. `failures_from` also harvested `FAILED (1)` as a phantom
  guard named `ED (1)`. Both fixed; none of the 43 mutations was wrong.
- **FINDING 35: the sentence that travels undercounts its own evidence.**
  *"Nine archives, 396 runs"* has been copied into every block document since
  Block E, and `calibrate_floor` printed `9 archived sweep(s), 492 run(s)` on
  the host. 396 is 4 x 99, the four Block E sweeps alone; the nine archives
  hold 492 once the two D4 pilots (36) and the three pre-D4 sweeps (60) are
  counted. The claim is true of all nine, so the correction STRENGTHENS it by
  ninety-six runs. Corrected in F3's documents; earlier block documents keep
  the sentence as they wrote it.
- **The BASELINE check is now in EIGHT harnesses of eight.** `mutate_ranking`
  (100), `mutate_places` (43) and `mutate_recover` (11) gained it on
  2026-08-31, before the corpus moves and not after -- a guard that goes red
  because of a NEW RECORD, in a harness with no baseline, turns every mutation
  naming it into a green line that proves nothing, and `mutate_ranking` had
  just run 100 mutations without one. The refusal branch was watched firing in
  all three. **The three have not yet been RE-RUN with it**, which is what
  turns the check from present into exercised.
- **FINDING 34, and it was caught by the host suite rather than by a reader.**
  Rulings 49-51 were written on 2026-08-31 and stamped **2026-08-29** in seven
  source files and five documents, including `floor.json`'s own
  `calibration_scope.corpus.declared_on`. The date came from `F3_START.md`'s
  opening line and from the session's device information — neither of them a
  clock — while `session_identity`, the function that dates every sweep,
  printed `2026-08-31` on the host. Corrected in every one of them. A wrong
  date here is a false provenance claim in the file whose business is
  provenance: `min_distinct_dates` counts UTC dates, and ruling 50 has just
  booked a ninth session to buy one. Fourth transcription defect in three
  sessions, and the remedy is the one already written down — the number must be
  produced by something that can be re-run. `F3_RUNBOOK` step 0 is now one
  command that prints the date.
- **No record has been timed, and the corpus has not moved.** F3 spent its
  session on the three things `F3_START` said had to be settled before a single
  record was curated. Curation starts at the top of F3_RUNBOOK step 4.
- ~~`mutate_part8`'s seven new mutations are claimed, not verified.~~
  **CLOSED at `a1af62d`.** All six harnesses ran on the host against the
  committed tree — 288 mutations, no MISS, no UNVERIFIED, no BASELINE block —
  and each of the seven was caught by the guard written for it. The
  one-function pre-verification agreed with the full harness, which is not a
  reason to trust it next time: it would have agreed just as loudly if a guard
  elsewhere had been doing the work.
- **`ingest/verify.py` check 9 still asserts `len(docs) == 24`**, and it is
  broken on purpose in the same commit as the records or not at all.
- ~~The BASELINE check is in five harnesses of eight.~~ **CLOSED 2026-08-31**
  -- it is in eight of eight. `mutate_distractors` stays outside the
  denominator: it mutates a live database view and is a different shape.
- Everything carried into F3 is carried out of it: ruling 40's `article_added`
  unverified against a live run, `muziris-cargo` at 3/5 on the arm,
  `--archives` pooling arms, `ingest/test_sql.py` never run with sqlglot and
  the database, and the `verse` and `documentary` profiles at n=1 — which stop
  being dormant in F3's own sub-tranche, four `verbatim_machine_english`
  records deep.

## The sentences that travel

And three from F3:

**The floor was calibrated on four sweeps at 24 records and the rule that
decides what is allowed to calibrate it could not see the corpus — on data that
had been in every archive for three weeks, put there so that a corpus which
moved could not go unnoticed.**

**Three rules required a third UTC date at 60 records, two of them written on
the same day as the gate that booked two, and no document held the sum.**

**An allocation decided at F7 is an allocation fitted to what was already
curated, and the cheap tier last is the only ordering under which running out
of days costs the corpus least.**

**Eleven documents said 2026-08-29 and the machine that stamps every sweep said
2026-08-31. The date was read off another document, in the repository where a
UTC date is the thing a ninth session was just booked to buy.**
