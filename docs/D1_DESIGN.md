# D1 — corpus version in every answer: the five decisions

*Written 2026-08-21, before any code. Every claim below was read out of a file
on the host and the line numbers are given so they can be checked rather than
believed.*

## What already exists, and what D1 actually has to build

The plan says *"hash each seed record on load"*. **That half is already done.**
`ingest/loader.py:113` computes

```python
raw = json.dumps(record, ensure_ascii=False, sort_keys=True)
...
content_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
```

and `ingest/db.py:86` stores it on `documents`. So D1 is not a hashing task. It
is a **carrying** task: getting that hash from the documents table to the
`answers` row, to the `eval/answer_runs/` archive, and back out at `--verify`.

`citable_passages` (`scripts/schema-part7.sql:36`) already joins `documents d`,
so the answer path can have the hash per passage for the cost of one column in
the view.

---

## Decision 1 — the digest covers SEED RECORDS ONLY, and that is correctness, not tidiness

`documents.content_hash` is **not one quantity**. Two writers populate it:

```
ingest/loader.py:130           sha256 of the canonicalised record       24 docs
ingest/load_distractors.py:126 the literal string f"{source}-{id}"     426 docs
```

A roll-up over the whole `documents` table would therefore be a hash over a
mixture of a digest and an identifier — and, worse, it would be **completely
stable under any edit to a distractor's text**, because a distractor's
`content_hash` is derived from its object id and not from its content. A number
that cannot move when the thing it measures moves is not a version.

**Scope the digest to `is_distractor = false`, and write the reason into the
file beside it**, or the next person to widen it will widen it for symmetry.

## Decision 2 — ONE glob, not two, and this one is a live hazard for Block F

Two functions decide what a seed record is, and they do not agree by
construction:

```
ingest/loader.py:106        corpus_dir.glob("*/*.json")     one level deep
ui/build_ui_data.py:92      CORPUS_DIR.rglob("*.json")      any depth
```

Today they agree — 24 records each, both skipping `manifest.json`, measured on
the host. **They agree by coincidence of the current layout.** A record added at
`data/seed_corpus/a/b/c.json` is a seed record to one and invisible to the
other, and the digest written at answer time would then never equal the digest
recomputed at verify time, for every answer, permanently.

Block F grows this corpus from 24 to 60 records. This is the block that would
introduce that file.

**D1 must expose one `iter_seed_records()` and have both callers use it.** A
digest whose two ends are computed by two different definitions of the corpus is
worse than no digest, because it fails in the direction of alarm: everything
looks changed, so nothing gets read.

## Decision 3 — `answer_id` does not change

`answer_store.py:278` keys an answer on `(question, model, prompt_version,
chunk_ids)`. Corpus state **must not** enter it.

Adding it would rewrite the identity of every one of the 77 archived answers and
make the whole Part 7–8 archive incomparable with itself — the same class of
error ruling 26 exists for, and the same discipline `rank_reranked` held to when
it never overwrote `rank`. **New fields, new names, additive, and the additivity
gets proved by diff the way C7 proved its own.**

## Decision 4 — two numbers, because they answer two questions

```json
"prompt_version": "p7-answer-v2r",
"corpus_version": {
  "algorithm": "sha256-of-canonical-json",
  "scope": "seed records only; distractors excluded, see Decision 1",
  "seed_record_count": 24,
  "seed_corpus_digest": "<64 hex>",
  "cited_records": { "africa-03-periplus-adulis": "<64 hex>" }
}
```

- `cited_records` answers **"did the record this span quotes move?"**
- `seed_corpus_digest` answers **"is this the corpus that made this answer at
  all?"**

They are not the same question and one cannot be recovered from the other. A
corpus can move somewhere else entirely while every cited record is untouched —
which is precisely the state Block E must be able to assert did *not* happen
between day one and day three.

Note what the hash is deliberately blind to: it is computed over
`json.dumps(..., sort_keys=True)`, so **reindenting a seed file does not change
it.** That is correct — the content did not move — and it should be written down
so that nobody later "fixes" it into a hash of the file bytes.

## Decision 5 — `--verify` reports THREE states, and the third is the point

`ui/build_ui_data.py:521` already classifies a span into `resolved`,
`case_folded`, `case_only`, `moved`, `absent`. The `moved` verdict currently
*asserts* a cause it cannot know:

> *"the seed record was edited after this run was archived"*

With a recorded hash that stops being an inference and becomes a fact. But there
are three outcomes, not two:

| recorded hash | verdict |
| :---- | :---- |
| present and **equal** to today's | the record did **not** move — an `absent` or `moved` span is a real defect in the span |
| present and **different** | the record moved — the span is **explained** |
| **not recorded** | **unknown**, and reported on its own line |

**All 77 existing archives are in the third bucket by construction**, and they
must never be silently counted as either of the first two. Collapsing "unknown"
into "unchanged" would let D1 report the Part 9 `1 absent` span as a real defect
on no evidence; collapsing it into "changed" would explain away every defect the
archive holds.

This file already sets that precedent, at `build_ui_data.py:505`, for exactly
the same reason:

> *"Every archived run made before C1a (2026-08-14) lands here by construction …
> They are not re-labelled retroactively: the archive records what was claimed
> at the time, and rewriting it would destroy the only evidence that the defect
> existed."*

---

## What lands on disk

```
scripts/schema-d1.sql       answers += seed_corpus_digest text,
                                       cited_record_hashes jsonb
                            citable_passages += d.content_hash
ingest/loader.py            iter_seed_records() extracted, single definition
ui/build_ui_data.py         uses it; --verify grows the three-state column
answer/assemble.py          store() carries the two new fields
answer/run_answer.py:321    archive payload gains "corpus_version"
```

## What gets mutation-verified

Three claims, and a mutation each — because a predicate with two clauses needs
two mutations:

1. **the distractor filter is load-bearing** — drop `is_distractor = false` and
   the digest must change;
2. **an unrecorded hash reports UNKNOWN and never MATCHED** — delete the
   `corpus_version` key from a fixture archive and the guard that fails must be
   the one naming the unknown state, not a general span guard;
3. **the two globs are one glob** — add a seed record two levels deep in a
   fixture corpus and both ends must see it, or both must not.

## The open question for you

The 77 existing archives cannot be given a corpus version retroactively without
inventing one. **They stay unversioned**, which is the honest option and the one
this repository has taken every previous time. The consequence is that Block E's
sweep archives will be the first that can ever be checked this way — so D1 buys
nothing for the past and everything for the next three days.

Worth saying out loud before it is discovered later: this means **D1 cannot
explain the Part 9 `1 absent` span.** It can only stop the next one from being
unexplainable. The plan's wording — *"the Part 9 `1 absent` span should become
explicable rather than merely absent"* — is achievable only in the weaker sense
that the span will be labelled **unknown-provenance** rather than silently
lumped in with real defects.
---

# Appendix — the two anomalous spans, diagnosed (2026-08-21)

`check_ui.mjs` reports `{"resolved":157,"case_folded":0,"case_only":9,"moved":1,
"absent":1}`. Both anomalies were located by re-deriving the classification
against the seed corpus. **They are the same run and the same record:**

```
run   20260810T124614+0000-52e5b803-recovered      archived 2026-08-10
doc   africa-03-periplus-adulis                    the discriminator's own record

moved   original_text_excerpt  [1902:1958] -> [2752:2808]
        "Φέρεται δὲ ἀπὸ τῶν τόπων ἐλέφας καὶ χελώνη καὶ ῥινόκερως"
absent  reference_translation  [409:628]
        "There are imported into these places, undressed cloth made in Egypt..."
```

**A methodological note first, because it nearly became a false finding.** The
first re-derivation used normalised equality and reported **115** broken spans
against the harness's 2. The harness was right. `build_ui_data.py:475`
`_same_characters` is *containment in either direction*, not equality —
`cite.py` trims edge punctuation before recording a span, so a quotation ending
in a comma the source lacks is a quoting convention, not a corruption. Re-run
with the harness's own predicate, the re-derivation reproduces
`157 / 0 / 9 / 1 / 1` exactly. **A re-derivation that disagrees with the
instrument by two orders of magnitude is a defect in the re-derivation.**

## The `moved` span IS explained by a recorded corpus edit

```
9470506  2026-08-12   original_text_excerpt  2089 chars
bb3bef5  2026-08-16   original_text_excerpt  3001 chars   +912
DISK                  original_text_excerpt  3001 chars   identical to bb3bef5
```

912 characters were inserted into the Greek; the span shifted by 850. The run
predates the edit by six days. **This is exactly the case D1 is built for**, and
with a recorded corpus hash it stops being an inference — `build_ui_data.py:546`
currently *asserts* "the seed record was edited after this run was archived"
without being able to know it, and here it happens to be right.

## The `absent` span is NOT explained by any recorded corpus edit, and never can be

```
reference_translation   9470506 == bb3bef5 == DISK      BYTE-IDENTICAL
```

The English field has never changed in any commit. The archived quotation's
first 67 characters sit at offset **1917** today, while the archive claims
**[409:628]**. So the passage is present and the offsets are from a corpus state
that **git has never seen**: the run is dated 2026-08-10 and `9470506`, the
record's first commit, is 2026-08-12.

Two explanations remain and **they cannot be separated**:

- **(a)** the run quoted a pre-baseline corpus state that was never committed;
- **(b)** the span is an artefact of reconstruction. This is a `-recovered.json`
  file, rebuilt by `scripts/recover_answer_baseline.py` in Part 8, and
  `build_ui_data.py:120` already warns those carry a thinner passage record.

**D1 cannot distinguish (a) from (b) for this span, ever.** A corpus hash
recorded at answer time would settle (a); nothing settles (b) except not
reconstructing archives in the first place.

## What this changes

- The honest limit stated above is no longer an argument, it is a **measured
  fact about a specific span**. D1 buys nothing for this one.
- **Decision 5 is confirmed by the data.** `moved` here is explained and
  `absent` here is unexplainable, and both are `africa-03-periplus-adulis` in one
  run. A two-state `--verify` would have to put them in the same bucket and
  would therefore be wrong about one of them whichever bucket it chose.
- `BLOCK_D_START` names only "the Part 9 `1 absent` span". **The `absent` one is
  the half D1 cannot help with; the `moved` one is the half it can.** The plan's
  wording points at the wrong span.
