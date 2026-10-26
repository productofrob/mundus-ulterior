# D1 — result (2026-08-21)

*Every number measured on the host. Tree `f54c585`, clean.*

```
7c003a7  D TASK 0: adulis-exports, and the answer path had been dead since bff0605
73e3c80  D1 step 1: one definition of what a seed record is
f54c585  D1 step 2: the corpus version travels with every answer
```

## The line D1 exists to produce

```
172 claimed character span(s) checked against the seed corpus:
  resolved 161   case_folded 0   case_only 9   moved 1   absent 1

seed corpus on disk: 24 record(s), digest 2e84436cb38a463b... (sha256-of-canonical-json-v1)
corpus provenance of those spans:
  unchanged       4        <- the one run made after D1 landed
  changed         0
  unrecorded      168      <- every archive that predates it
  not_in_version  0
```

Before today those 172 spans had one axis. *This span broke* and *this span was
made against a different corpus* were the same observation, and `classify_span`
resolved the ambiguity by **asserting** a cause it had no evidence for. There
are now two axes, and the second one has three states because two would be a
lie about the 168.

## Proven end to end, with one live chat call

`eval/answer_runs/20260821T100448+0000-d2403a22.json` — the first archive in
this repository to carry a corpus version, and the first live exercise of the
answer path since it was unbroken this morning.

```
question          "What was exported from Adulis?"          (adulis-exports)
grounded          true, 4 quotations, all resolved to characters on disk
seed_corpus_digest        2e84436c...   matches the digest computed from FILES
record_hashes[adulis]     0e83bf72...   matches bb3bef5, computed independently
answers row               both columns populated, 4 cited records
--verify                  those 4 spans report `unchanged`
```

`0e83bf72...` was computed **three separate ways** today and agreed every time:
by a throwaway script diagnosing the moved span, by `seed_record_hashes()` over
the files, and by Postgres from a hash written at ingest days ago.

`adulis-exports` **passes live**, on evidence byte-identical to the seven
consecutive refusals of `aksum-exports`. The discriminator is a regression test
now, not an anecdote — which is what TASK 0 set out to make it.

## The five decisions, as built

1. **The digest is scoped to `NOT is_distractor`** — correctness, not tidiness.
   `documents.content_hash` is a sha256 for the 24 seed records and the literal
   string `f"{source}-{object_id}"` for the 426 distractors, so a roll-up over
   both would be **stable under any edit to a distractor's text**.
2. **One walk, not five.** `iter_seed_records()`. Four callers globbed
   `*/*.json`; `build_ui_data.load_corpus` used `rglob("*.json")`, so that file
   disagreed with itself — and the walk that disagreed fed `--verify`. A `.json`
   outside `region/record.json` now raises. No lenient flag.
3. **`answer_id` unchanged.** All 78 archived answers keep their identity.
4. **Two numbers.** Per-record hashes answer *did the record this span quotes
   move?*; the digest answers *is this the corpus that made this answer?*
   Neither is recoverable from the other.
5. **Three states at `--verify`**, and the gate is deliberately unmoved:
   `moved + absent` still fail. D1 changes what is reported, not what fails.

## The two anomalous spans, diagnosed

Both are the same run and the same record, `africa-03-periplus-adulis`.

- **`moved` IS explained**: `bb3bef5` grew `original_text_excerpt` 2089 → 3001;
  the span shifted 850. The run predates it by six days.
- **`absent` can NEVER be explained**: `reference_translation` is byte-identical
  in every commit, and the archived offsets come from a corpus state git has
  never seen — the run is 08-10 and the record's first commit is 08-12. Either a
  pre-baseline state, or an artefact of `-recovered` reconstruction. **D1 cannot
  separate those two, ever.**

`BLOCK_D_START` names the `absent` span as the one D1 makes explicable. It is
the half D1 cannot help with.

The 9 `case_only` spans are **one defect, not nine**: the same quotation in the
same field across nine runs all dated 2026-08-10, the pre-C1a labeller that
`build_ui_data.py:505` already predicts. All 172 spans now have an account.

## What this session cost, and what it caught

```
suites run          12, all green on the host
mutations verified  123 + 15 + 3 + 43 = 184 across six harnesses
chat calls spent    1
```

Findings are in `D_TASK0_RESULT.md` (1-5). Two more from D1:

**FINDING 6 — a migration cannot own a view that `schema-part7.sql` owns.**
`run_answer.py:234` re-applies that file on EVERY run. The first `schema-d1.sql`
added `content_hash` to `citable_passages`; the next run died with `cannot drop
columns from view`. **It died loudly only because the migration ADDED a column.**
Had it removed one, `schema-part7.sql` would have silently restored it. The
loudness was luck. The column now lives in `schema-part7.sql`; only the `ALTER`s
remain in the migration, because `CREATE TABLE IF NOT EXISTS` does nothing to a
table that already exists. Both files carry the reason.

**FINDING 7 — a restore command with no guard cannot tell the file it is about
to fix from the file it is about to destroy.** `git checkout --
ui/build_ui_data.py`, prescribed by this block's own step-2 runbook to clear
line-ending churn, discarded every uncommitted D1 change in that file. Step 1's
runbook had gotten this right — *commit before running the harnesses* — and step
2 put the harnesses first and kept the command anyway.

Recovery was byte-exact because every edit this session was an exact-string
replacement rather than a line-offset edit. **That rule is why this cost twenty
minutes instead of an afternoon.**

This is Finding 5 seen from the other side. The harnesses' restore check
compares normalised text and cannot see the damage; `git checkout --` sees the
damage and cannot see what else it takes. Both fail by comparing the wrong
thing.

## Carried into Block E

**`2e84436cb38a463b0110613d5662d0067b8d16cc9e28e1db4c8374882314ecfc`** is the
corpus digest to record on day one and re-assert on day three. Until today no
such number existed.

**"Change nothing between days" must name the schema file.** The current list is
prompt, corpus, retrieval, gateway. `run_answer.py` re-applies
`scripts/schema-part7.sql` on every one of ~90 calls a day, and any drift between
file and database resolves silently, mid-sweep, in the direction of the file.

## Open, and deliberately not closed

- **Rulings 25 and 26 are still not in the register.** Now quoted by three Block
  D documents.
- **Nothing guards the `_chat` arity contract** (Finding 2). `mutate_part7b`
  verified 15 of 15 and not one is about the contract that was broken for five
  days.
- **No mutation harness compares bytes on restore** (Finding 5). Four harnesses,
  one blind check each; three of six have LF sources they silently rewrite.
- **`classify_span` still asserts a cause it cannot know.** `--verify` now
  prints that sentence directly above `corpus provenance: unrecorded`, which
  contradicts it. The wording should lose the claim and leave it to the
  provenance line, which has evidence.
- **`aksum-exports` remains an open defect.** Adding the passing half did not
  close it and was not recorded as closing it.
