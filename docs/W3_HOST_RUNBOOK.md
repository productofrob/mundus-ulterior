# W3 HOST RUNBOOK — the two things the bridge cannot do, and one it must not

*Everything else in W3 is done and green through the bridge. `W3_RESULT.md`
records what it can and marks these OWED; it does not report a figure for them.*

---

## Step 0 — the session ritual, and the thing that bit this session

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
}
git status --porcelain
```

**`git status` must print nothing** once W3's commit has landed. If it prints
`.git/index.lock`, delete it: `Remove-Item .git\index.lock`. **A `git status`
issued from the Linux side of the bridge leaves that lock and CANNOT CLEAR IT** —
`rm` on a mounted file returns `Operation not permitted`, so a bridge session
that trips it has to interrupt you. `BLOCK_D_START.md` gives one reason for the
host-only git rule; that is a second and worse one, and it is in FINDING 94.

---

## Step 1 — the mutation harnesses. HOST ONLY, FINDING 59.

**Never through the bridge.** A call killed at 45 seconds leaves a live mutation
in the tree. Never two harnesses over one working tree at once — both capture
originals at start and restore at exit, so the second captures the first's
mutation as the original.

```powershell
python scripts\mutate_fidelity.py
python scripts\mutate_cost.py
git diff --stat
```

```
EXPECTED
  mutate_fidelity   84/84     was 70/70 at F7. W3 adds fourteen: six refusal
                              clauses, the section 8 curation gate, the two
                              classifier constants FINDINGS 82 and 86 lived in,
                              non_latin_ratio's rule, the script-neutral skip,
                              the whitespace clause, the empty-field clause and
                              the wrong-script branch
  mutate_cost       58/58     must NOT move. W3 does not touch ingest/cost.py
  UNMUTATED_AND_OWED   3      must NOT move. Not one W3 clause joined it
  git diff --stat            no file whose every line changed
```

**A file whose every line changed is the line-ending defect, not your edit.**
Checked from the bridge already and clean — no CRLF in any of the 63 files W3
touched — but the harnesses rewrite `ingest/fidelity.py` sixty-odd times and
restore it, and that is exactly where the defect would appear.

**If `mutate_fidelity` reports UNVERIFIED for any W3 mutation**, its guard was
already red at baseline, which means the suite is not green on the host. Stop and
say so; the bridge reads `ingest.test_fidelity` at **145** and all eleven
instruments green.

---

## Step 2 — the re-ingest, and PREDICTION P3's open half

The bridge cannot reach `postgresql://mundus:mundus@localhost:5432/mundus`, so
**no chunk in the index yet knows the declarations exist.**

```powershell
docker compose up -d db
python scripts\check_db.py                 # pgvector installed: True
python -m ingest.run_embed --stats         # BEFORE
python -m ingest.run_ingest
python -m ingest.run_embed --stats         # AFTER
```

```
P3 SAYS, and W3_START.md said it at 59dcd1e before the fix existed:

  MOVES        the corpus digest, and all 54 record content_hashes
  DOES NOT     chunk ids, chunk count (170), chunk text, char offsets, embeddings

REFUTED BY  any change to a chunk id, a chunk count, a chunk text, an offset or
            an embedding.

So `run_embed --stats` must read the SAME `embedded` count before and after, and
`pending: 0` after. IF IT REPORTS PENDING WORK, P3 IS REFUTED AND 561 CHUNKS OF
EMBEDDINGS ARE IN PLAY -- stop, do not let it re-embed, and say so. W3
section 4 asked for this to be VERIFIED rather than assumed and this is where
that happens.
```

`run_embed` is NOT to be run. If the stats disagree, that is the finding.

---

## Step 3 — nothing else

**No ranking run. No sweep. No PG5.** PG5's run is booked in
`BLOCK_G_RESULT.md` §4 and belongs to the block that takes it, and W3 added six
records to nothing — it added a field to fifty-four.

**Do not re-point `floor.json`'s digest pin.** Ruling 82. The new digest
`0e784505…` is recorded in `superseded_by` and the pin still names `26e4a683…`
on purpose.
