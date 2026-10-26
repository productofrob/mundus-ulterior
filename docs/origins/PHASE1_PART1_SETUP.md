# Mundus Ulterior — Phase 1, Part 1: Prerequisites & Environment

**Status: ✅ COMPLETE** (verified working). This document reflects the setup *as
actually built and run on Windows*, including the fixes we hit along the way. Use
it as the source of truth if you ever rebuild the environment.

Goal of this part: stand up the scaffold once so everything after §1 is pure
feature work. **Exit gate (both must pass):**

1. `scripts/hello.py` prints a chat reply *and* an embedding vector length, and
2. `scripts/check_db.py` prints `pgvector installed: True`.

Both confirmed:

```
CHAT: Hello! How can I help you today?
EMBED: dims = 1024 | first 3 = [-0.0195..., 0.0627..., -0.0155...]
pgvector installed: True
PostgreSQL 16.14 ...
```

Build order: **gateway config first**, then Postgres, then repo layout, then the
milestone. No model is wired into app code directly — everything goes through the
gateway.

---

## Environment as built

- **OS / shell:** Windows, PowerShell.
- **Python:** 3.14 (works, but see the FastAPI pin in "Gotchas" — bleeding-edge
  Python forced a version fix). Python 3.11–3.12 would avoid that entirely.
- **Chat model:** Anthropic Claude (`claude-haiku-4-5` for the cheap hello test).
- **Embedding model:** Voyage AI `voyage-3.5` (1024-dim). Anthropic doesn't make
  an embedding model, so Voyage — its recommended embeddings partner — fills that
  role. BGE-M3 replaces it in Part 4.
- **Vector store:** Postgres 16 + pgvector in Docker.
- **Gateway:** LiteLLM proxy on `http://localhost:4000`.

Repo lives at:
`C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior`

---

## Step 0 — Base tooling

- **Python 3.11+** — `python --version`. (We used 3.14; see Gotchas.)
- **Docker Desktop** — must be *running* ("Engine running") before any `docker`
  command. `docker --version`, `docker compose version`.
- **Git** — `git --version`.

Postgres and the models are not installed locally — they run via Docker / the gateway.

---

## Step 1 — Repo layout

Seven working dirs (each with a `.gitkeep`), plus `scripts/`:

| Dir | Purpose |
| --- | --- |
| `ingest/` | fetch + chunk + embed the seed corpus |
| `retrieve/` | vector search over pgvector |
| `answer/` | translation + grounded answer assembly |
| `eval/` | groundedness harness + gold datasets |
| `ui/` | thin front end |
| `data/` | seed corpus (large blobs git-ignored) |
| `gateway/` | LiteLLM proxy config |
| `scripts/` | setup + milestone scripts |

`.gitignore` excludes `.venv/`, `__pycache__/`, `.env`, and `data/**`.

---

## Step 2 — Python venv + dependencies

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` (note the FastAPI pin — see Gotchas):

```txt
litellm[proxy]        # model-agnostic gateway
fastapi==0.115.5      # pinned: newer FastAPI removed get_flat_dependant, which litellm proxy imports
psycopg[binary]       # Postgres client
pgvector              # pgvector Python bindings
python-dotenv         # env/secrets loading
openai                # OpenAI-compatible client for the LiteLLM proxy
```

If PowerShell blocks activation with a "running scripts is disabled" error, allow
local scripts once for your user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Activation is per-window.** Every new PowerShell window needs
`.venv\Scripts\Activate.ps1` (prompt shows `(.venv)`) *and* a fresh env load.

---

## Step 3 — Postgres 16 + pgvector in Docker

`docker-compose.yml` runs `pgvector/pgvector:pg16` on port 5432 and mounts
`scripts/init-db.sql`, which auto-runs `CREATE EXTENSION IF NOT EXISTS vector;`
on first boot — so no manual extension step is needed.

```powershell
docker compose up -d db
python scripts\check_db.py     # expect: pgvector installed: True
```

---

## Step 4 — Gateway config (Claude + Voyage)

`gateway/config.yaml`:

```yaml
model_list:
  - model_name: chat-default
    litellm_params:
      model: anthropic/claude-haiku-4-5-20251001   # swap to claude-sonnet-5 anytime
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: embed-default
    litellm_params:
      model: voyage/voyage-3.5                      # BGE-M3 replaces this in Part 4
      api_key: os.environ/VOYAGE_API_KEY
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
```

The gateway reads these keys **from its own window's environment** at startup —
so if you change a key, you must restart the gateway (see Gotchas).

---

## Step 5 — Secrets in `.env`

Copy the template and fill in real keys — **no inline comments or trailing spaces
on the key lines** (they become part of the value and cause 401s):

```
ANTHROPIC_API_KEY=sk-ant-yourkey
VOYAGE_API_KEY=pa-yourkey
LITELLM_MASTER_KEY=sk-local-dev
APP_DATABASE_URL=postgresql://mundus:mundus@localhost:5432/mundus
```

> The app DB variable is `APP_DATABASE_URL`, **not** `DATABASE_URL` — LiteLLM
> treats `DATABASE_URL` as a reserved trigger for its own Prisma database. See Gotchas.

PowerShell doesn't auto-read `.env`. Load it into the current window with:

```powershell
Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
```

---

## Step 6 — Run it (two windows)

**Window A — gateway** (activate venv, load env, then):

```powershell
litellm --config gateway/config.yaml --port 4000
```

Wait for `Application startup complete` / `Uvicorn running on http://0.0.0.0:4000`.
Leave it running. To stop it: click into the window, `Ctrl+C`; if unresponsive,
just close the window.

**Window B — milestone** (activate venv, load env, then):

```powershell
python scripts\check_db.py     # pgvector installed: True
python scripts\hello.py        # chat reply + embedding dims = 1024
```

Both passing = Part 1 gate cleared.

---

## Gotchas we hit (and the permanent fixes, already in the repo)

1. **Global vs venv install.** The first `pip install` ran before the venv was
   active (PowerShell blocked activation), so packages landed in global Python and
   `litellm` wasn't found in the venv. Fix: activate the venv *first*, then
   `pip install -r requirements.txt`.

2. **PowerShell execution policy.** `Activate.ps1` was blocked. Fix:
   `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.

3. **FastAPI too new.** LiteLLM proxy imports `get_flat_dependant`, removed in
   FastAPI ≥ 0.140. Symptom: `ImportError: cannot import name 'get_flat_dependant'`.
   Fix: pinned `fastapi==0.115.5` in `requirements.txt`.

4. **`DATABASE_URL` collision.** LiteLLM sees `DATABASE_URL` and tries to spin up
   its own Prisma database (`ModuleNotFoundError: No module named 'prisma'`). Fix:
   renamed the app's variable to `APP_DATABASE_URL` (used by `check_db.py` and
   later steps); the gateway no longer sees a reserved var.

5. **Key changes need a gateway restart.** The Anthropic key is used by the
   *gateway*, not `hello.py`. Editing `.env` and reloading in the client window
   does nothing until the gateway is restarted with the corrected env.

6. **Invalid-key 401 from a trailing comment.** Leaving `# from console...` after
   a key in `.env` made the value include the comment → `API key is invalid`. Fix:
   key lines contain the key only.

---

## Verification checklist (all ✅)

- [x] `python --version` → 3.11+ inside `.venv`
- [x] Docker Desktop running; `docker compose up -d db` → `mundus-db` up on 5432
- [x] `scripts/check_db.py` → `pgvector installed: True` (PostgreSQL 16.14)
- [x] LiteLLM proxy starts on :4000, no inline keys, no Prisma error
- [x] `scripts/hello.py` → Claude chat reply + Voyage embedding (1024 dims)

---

**Next: Part 2 — assemble the seed corpus** (3–5 sources per region, ~25–30 docs,
each with original text + provenance metadata). To be done in a separate thread.
