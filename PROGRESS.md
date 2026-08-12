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
