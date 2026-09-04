# F4 PART 3 RUNBOOK — what to run on the HOST, in order

*PowerShell, repo root, venv active. Steps 1 to 3 need neither the database nor
the gateway. Step 4 needs Docker and the database. Nothing here spends a chat
call — ruling 65 is the reason.*

**Everything in steps 1 and 2 has been run through the bridge at this tree and is
green there. The host run is the one that counts, and step 2 is on the host for a
reason FINDING 59 pays for in full.**

---

## 0. The date, before anything is written down

```powershell
python -c "import datetime as d; print(d.datetime.now(d.timezone.utc).date())"
```

Expect `2026-09-04`. FINDING 34: the host is the authority, because the host is
what stamps a sweep. If it disagrees with the rulings written today, the rulings
are wrong and not the clock.

---

## 1. The eight suites — and this time all eight carry a number

**FINDING 57.** `scripts\test_recover_baseline.py` joined this list in F3 as a
COMMAND with no expected number, and was then reported RED in three consecutive
state blocks while it was green. A suite whose expected output is prose is a
suite whose status gets copied rather than compared. Every line below is a number
printed by the suite that describes it, at `935c35a` plus this session's working
tree, through the bridge, on 2026-09-04.

```powershell
python -m ingest.verify
python -m ingest.test_fidelity
python -m ingest.test_cost
python -m eval.test_answer_eval
python -m eval.test_ranking_check
python -m answer.test_answer
python ui\test_build_ui_data.py
python scripts\test_recover_baseline.py
```

```
ingest.verify                     All integrity checks passed.  35 documents,
                                  82 chunks, 23 parallel pairs
ingest.test_fidelity               58 passed, 0 failed
ingest.test_cost                   64 passed, 0 failed
eval.test_answer_eval             410 passed, 0 failed
eval.test_ranking_check           253 passed, 0 failed
answer.test_answer                150 passed, 0 failed        <- SEE BELOW
ui\test_build_ui_data.py           19 passed, 0 failed
scripts\test_recover_baseline.py   56 passed, 0 failed        <- was 44; +11 for
                                                                 ruling 64, +1 for
                                                                 sqlglot on the host
```

**`answer.test_answer` reads `149 passed, 0 failed, 1 SKIPPED` through the
bridge**, because sqlglot is in the host venv and not in the bridge's
interpreter. 150 is the number to expect on the host. If the host prints 149 with
a skip line, sqlglot has gone missing from the venv — which is a finding, not a
pass.

**`ingest.verify` should print the delivery note reading `Gloss-capable declared
3/8`.** Ruling 62's composition — one of the three is a hedged identification and
not a disputed reading — is not in that number and is not supposed to be. It
travels in the record, in the gold case's `why`, and in F4_RESULT.

---

## 2. The mutation harnesses — ON THE HOST, and FINDING 59 is why

**Do not run any of these through the bridge, and the reason is not the time
limit.** `scripts/mutate_cost.py` was started through the bridge today, the
workspace disconnected mid-run, and it left a live mutation in `ingest/cost.py`
that made `trend_line` report every tier as flat. A harness restores its sources
from inside its own process. Nothing restores them when the process is ended from
outside, and no suite in this repository would have noticed.

Four harnesses changed in this session and are the priority:

```powershell
python scripts\mutate_recover.py        # 17 -- was 11; +6 for ruling 64
python scripts\mutate_cost.py           # 51
python scripts\mutate_part7b.py
python scripts\mutate_distractors.py    # needs the database
```

Four are unchanged here and have not been run since `a5c0ae6`, which every state
block since has said. The corpus has moved twice underneath them:

```powershell
python scripts\mutate_ranking.py        # 108, last verified at a5c0ae6
python scripts\mutate_fidelity.py       # 46
python scripts\mutate_part8.py          # 94
python scripts\mutate_ui_places.py      # 6
```

**Every one of these should print `all N mutations verified; sources restored`
and NO `BASELINE:` line and no `UNVERIFIED`.** A `BASELINE:` line means a guard
was already red before any mutation was applied, and every mutation naming it
proves nothing.

**And all eight now match `FAIL ` with the space (FINDING 58).** If any of them
reports a guard named `ED (n)` or `ED: <name>`, the fix did not take in that
file.

---

## 3. The line-ending check, before the commit and not after

```powershell
git --no-optional-locks diff --stat
git --no-optional-locks status --porcelain
```

FINDING 52. Expect seven modified files and no file whose change count equals its
line count. Expect `status` to list **only** those seven — a ninth name is a live
mutation, and FINDING 59 is four hours old.

```
F4_RULINGS.md                      508 +
scripts/mutate_cost.py              11 +-
scripts/mutate_distractors.py        8 +-
scripts/mutate_part7b.py            10 +-
scripts/mutate_recover.py           68 +-
scripts/recover_answer_baseline.py  85 +-
scripts/test_recover_baseline.py    88 +
```

If a harness has left something behind, restore it with
`git --no-optional-locks cat-file blob HEAD:<path>` written back as BYTES.
**Not `git checkout`** — it takes the index lock, and a lock taken through the
bridge cannot be deleted by it.

---

## 4. THE RANKING RUN — BASELINE only, and nothing reads the archive until it exists

**Ruling 65: no `--fuse`.** `eval/gold/query_renderings.json` has no entries for
Part 2's eight pairs, the fused arm would refuse to run until they are rebuilt,
rebuilding them spends chat calls, and it would move `renderings_digest` inside
the commit that reports the run. Both pre-registered predictions are denominated
in BASELINE.

```powershell
python -m ingest.verify
python -m ingest.run_ingest
python -m ingest.run_embed
python -m eval.run_ranking_check --with-distractors
```

`run_ingest` and `run_embed` are here because the ranking check reads the
DATABASE, not the seed files, and the index must hold all 35 records. If the
digest `ingest.verify` prints and the corpus the run measures disagree, the run
is about a corpus that no longer exists.

The run archives to `eval\ranking_runs\<timestamp>+0000-retrievable_chunks_with_distractors.json`.

**Nothing in this session opens that directory until this command has finished.**
Rulings 55 and 61 are the only two pre-registered predictions this project has
ever made, both are about this run, and both are cheap to spoil.

---

## 5. Then stop, and hand back

Paste the terminal output of steps 1, 2 and 4 — or just say the run is archived
and I will read it out of the folder. What comes next, in this order:

1. **Ruling 55** — do both `china-describes-rome` pairs move down, and does
   `weilue` leave the top 6? Falsified if both hold, which narrows FINDING 43
   from same-subject texts to near-duplicate objects.
2. **Ruling 61** — `best_other_doc_chunk_id` for the three debt pairs.
3. **Ruling 66** — `vimose-runes` at rank 7, ruled on the within-run evidence
   ruling 61 produces rather than on the F3 before/after that ruling 54 bars.
4. **F4_RESULT**, carrying the gloss count with its composition (ruling 62), the
   vme shortfall as ruling 53's NEITHER outcome (ruling 63), the fused arm as
   NOT RUN with its reason (ruling 65), and F5's owed list.

---

## What NOT to do

**Do not rebuild the renderings.** Ruling 65.

**Do not run a harness anywhere it can be interrupted.** FINDING 59.

**Do not read the aggregate cost per record.** Ruling 46, and the allocation
biases it downward by construction.

**Do not re-hunt East Asia or Sub-Saharan Africa.** `F4_CANDIDATES.md` holds
both hunts in full, including every route that failed and why. Ruling 63 has
already read Africa's zero.
