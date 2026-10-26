# D1 step 2 — the plumbing. Runbook

*PowerShell on the host, repository root, venv active. Step 1 must be committed
first. One live chat call at the end, and only one.*

## What changed

```
scripts/schema-d1.sql        NEW   answers += corpus_digest_algorithm,
                                            seed_corpus_digest,
                                            cited_record_hashes jsonb
                                   citable_passages += d.content_hash
answer/evidence.py                 ChunkRecord.content_hash
answer/answer_store.py             PASSAGE_COLUMNS, _record, UPSERT_ANSWER,
                                   SELECT_SEED_RECORD_HASHES,
                                   corpus_version(), cited_record_hashes()
answer/assemble.py                 AssembledAnswer.corpus_version; store() writes it
answer/run_answer.py               archive payload += "corpus_version"
ui/build_ui_data.py                corpus_provenance(), the three-state report
```

`answer_id` is **unchanged**. Corpus state does not enter the key, so all 77
archived answers keep their identity — the discipline ruling 26 held to when
`rank_reranked` never overwrote `rank`.

## 1. Migration

```powershell
docker compose up -d db
python scripts\apply_sql.py scripts\schema-d1.sql
```

Applied as one transaction. `ADD COLUMN IF NOT EXISTS` throughout, and
`citable_passages` gains its column at the END of the select list, which is the
only place `CREATE OR REPLACE VIEW` permits.

## 2. Offline suites

```powershell
python -m answer.test_answer          # all Part 7 offline checks passed
python -m answer.test_translate
python -m eval.test_answer_eval       # 71
python ui\test_build_ui_data.py
python -m ingest.verify
python -m ingest.test_sql
```

## 3. The three-state report

```powershell
python ui\build_ui_data.py --verify
```

Expect the five span states **unchanged** — `157 / 0 / 9 / 1 / 1` — plus a new
block:

```
seed corpus on disk: 24 record(s), digest 2e84436cb38a463b... (sha256-of-canonical-json-v1)
corpus provenance of those spans:
  unchanged       0
  changed         0
  unrecorded      168
  not_in_version  0
```

**All 168 unrecorded is the correct answer, not a failure.** Every archive
predates D1, so whether the record moved is not knowable from it. The exit code
is deliberately unchanged: `moved` + `absent` still fail. D1 changes what is
reported, not what fails.

## 4. Rebuild the bundle

```powershell
python ui\build_ui_data.py
node ui\check_ui.mjs
```

## 5. Mutation, one at a time

`assemble.py` and `build_ui_data.py` both changed.

```powershell
python scripts\mutate_part7b.py
python scripts\mutate_ui_places.py
```

Then clear the line-ending churn. `mutate_part7b`'s three sources are all CRLF
so it leaves none; `mutate_ui_places` rewrites `ui/build_ui_data.py`, which is
LF.

**DO NOT use `git checkout --` here.** The first version of this runbook did,
and on 2026-08-21 it discarded every uncommitted D1 change in
`ui/build_ui_data.py` - `corpus_provenance`, `PROVENANCE_STATES`, the three-state
report, the whole step. Step 1's runbook had you commit BEFORE running the
harnesses precisely so that checkout was safe; step 2 put the harnesses first
and left the same command in. That is the same hazard, one step later.

Convert the endings IN PLACE instead, which keeps the content:

```powershell
git diff --stat
python -c "import pathlib; p=pathlib.Path('ui/build_ui_data.py'); b=p.read_bytes(); assert b'def corpus_provenance' in b; p.write_bytes(b.replace(b'\r\n', b'\n'))"
git diff --stat
```

The assertion is the point: it refuses to touch the file unless the D1 work is
actually in it. A restore command with no such guard cannot tell the file it is
about to fix from the file it is about to destroy.

**Better still: commit before running any mutation harness.** That is what step
1 did and it is the rule, not the exception.

## 6. The end-to-end proof — ONE live chat call

Everything above tests the read path. The write path — `corpus_version()` →
`answers` row → archive — cannot be reached by `--dry-run`, because the dry run
returns before the model label is resolved. It needs one real answer.

**Use a question that already has a gold case**, or
`eval.test_answer_eval`'s *"every archived question has a gold case"* will go
red on the new archive.

```powershell
litellm --config gateway/config.yaml --port 4000     # separate window
python -m answer.run_answer "What was exported from Adulis?"
```

That is `adulis-exports`, which does three things at once: it becomes **the
first archive in this repository to carry a corpus version**, it exercises the
answer path that was dead from `bff0605` until this morning, and it re-runs the
half of the discriminator that works.

Then check what it wrote:

```powershell
python -m eval.test_answer_eval        # 72 archives, still 0 failed
python ui\build_ui_data.py --verify    # unrecorded 168, unchanged N>0
```

The new run's spans should come back **`unchanged`**, not `unrecorded` — that is
the whole of D1 in one line. If they come back `changed`, the database and the
seed files disagree and the ingest is stale, which is a real finding and exactly
the one this was built to surface.

## The decision this step surfaced, and did not take

`--verify` now prints two lines that contradict each other:

```
MOVED  africa-03-periplus-adulis.original_text_excerpt[1902:1958]
  the seed record was edited after this run was archived; ...
  corpus provenance: unrecorded
```

`classify_span` **asserts a cause it cannot know**. It happens to be right here —
`bb3bef5` did edit that record — but it is right by luck, and it says the same
sentence for every `moved` span whether or not anything is known about the
corpus. D1 has made the unsupported claim visible rather than removing it.

The wording should probably become *"the quotation is still in the field, at a
different offset"*, leaving the cause to the provenance line, which now has
evidence for it. That is a change to a message, not to a state, and it is left
here as a decision rather than made silently.


## Correction, 2026-08-21

The first version of this runbook wrote the question as `--question "..."`.
There is no such flag: `run_answer.py:185` declares the question as a
POSITIONAL argument, `nargs="?"`. The correct form is

```powershell
python -m answer.run_answer "What was exported from Adulis?"
```

Cost of the error: one rejected command line and nothing else - argparse
refused before any work was done, so no embedding and no chat call were spent.
Recorded because the same mistake in the Block E sweep script would be found
after the gateway was up and a run had started.
