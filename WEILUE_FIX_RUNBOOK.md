# Weilüe corpus fix — runbook

*Written 2026-08-21 at the close of D3, for FINDING 9. Not yet run. Every step
you run yourself on the host; nothing here is a measurement until it is.*

## What this fixes, and what it costs

`eastasia-01-weilue` is the record the project's AI Technology Showcase brief
names by name — *"Retrieves the Weilüe passage on Da Qin in Classical Chinese"*
— and its Classical Chinese has never been quoted in any archived answer.
**40 of 40** resolved spans across 15 archived `chinese-da-qin` runs came from
`reference_translation`. The Chinese excerpt is 52 characters against 693 of
English, and the English carries content the Chinese does not have:

```
"four hundred" cities   original: no    translation: yes
Tiber / river capital   original: no    translation: yes
two-month voyage        original: no    translation: yes
```

The record's own `original_text_note` asked for the fix and it was never done:
*"should be pulled verbatim, character-by-character, during ingestion rather
than reproduced from this summary."*

**This moves the corpus, and the corpus is what Block E exists to measure while
frozen.** Before starting, know what it touches:

| touched | why it matters |
| :---- | :---- |
| the seed digest `2e84436c…` | D1 exists so you can re-assert it on day three. It changes. |
| the index `450 / 450 / 0` | the record re-chunks and re-embeds; the count may move |
| `probe-chinese-weilue` | a `lzh` ranking pair querying the chunk you are replacing |
| `chinese query -> Weilue Da Qin` | a `lzh` retrieval probe, same |
| `translation_cases.json` | the Part 6 round-trip case on this record, chrF-calibrated |
| **ruling 25's evidence** | G2's gap was `+0.019622` against `+0.024927` — a margin of `0.005305`, measured on this index |

Ruling 25 stands whatever happens here. What changes is that **its number can no
longer be re-derived from the tree**, and that is the cost being accepted.

## Step 0 — commit first, and record the before

**Commit before anything else.** This block has already lost a completed task to
a restore command that could not tell uncommitted work from churn.

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
git status --short          # expect: clean
```

Then capture the BEFORE state into a file, so the after-comparison is against a
record and not a memory:

```powershell
docker compose up -d db
litellm --config gateway/config.yaml --port 4000     # separate window

python -m ingest.run_embed --stats                   > eval\weilue-before.txt
python -m ui.build_ui_data --verify                 >> eval\weilue-before.txt
python -m eval.run_ranking_check --with-distractors --collapse --rerank --rerank-tpm 2000000 >> eval\weilue-before.txt
```

That ranking run is the expensive one and it is the point of the exercise: the
two `lzh` queries' ranks BEFORE the change are the only baseline you will get.

## Step 1 — fetch the verbatim text yourself

The record cites **`https://zh.wikisource.org/wiki/魏略輯本`** as the authority for
its original, and the Silk Road Seattle translation
(`https://depts.washington.edu/silkroad/texts/weilue/weilue.html#section11`) as
the authority for its English.

**Do not let me write this text.** Composing Classical Chinese from a model's
weights and filing it under a citation is the same error as encoding a
misquotation in a gold case — and it is the error the corpus already caught
once, in `southasia-03`'s note, as *"a claim carried by editorial scaffolding
rather than by the source"*.

What to take: the Section 11 (Da Qin) passage, in the characters the Wikisource
transcription gives, covering **at minimum** the material Hill's English already
in `reference_translation` covers — the location relative to Anxi and Tiaozhi,
the sea crossing from Angu, the four hundred cities, the capital near the
river's mouth, and the stone walls. If the English asserts it, the Chinese
should carry it, because that mismatch is the whole finding.

Keep the characters exactly as transcribed. Strip only line numbers and
editorial apparatus, and write down what you stripped.

## Step 2 — write it into the record

Edit `data/seed_corpus/east_asia/weilue-da-qin.json`:

- **`original_text_excerpt`** — replace with the verbatim text.
- **`original_text_note`** — replace with what was actually done. Follow the
  shape `southasia-03-muziris-papyrus` set on 2026-08-13, which is the best
  example of this in the repository: what was taken, from where, under what
  licence, what was normalised, what was left, and why. State plainly that the
  previous value was a paraphrase-reconstruction and that 40 of 40 archived
  quotations had come from the translation.

Do **not** touch `reference_translation`. The 40 archived spans resolve into it
and D1's `--verify` should keep reporting them `resolved`.

## Step 3 — re-ingest and re-embed

```powershell
python -m ingest.run_ingest --dry-run         # chunk only, NO DB writes - read this first
python -m ingest.run_ingest                   # re-chunks and writes
python -m ingest.run_embed                    # embeds new/changed chunks only
python -m ingest.run_embed --stats            # expect N / N / 0 pending
```

The module is `ingest.run_ingest`. An earlier draft of this runbook said
`ingest.run_load`, which does not exist — caught before it wasted a session.
Run `--dry-run` first and read how many chunks the new original splits into
BEFORE anything touches the database.

**Record the new chunk count.** If `original` splits into more than one chunk,
chunk ids move — `eastasia-01-weilue::original::000` may gain siblings — and the
59/57 corpus figure changes. That is expected and must be written down, not
absorbed.

## Step 4 — the after, and the comparison

```powershell
python -m ingest.run_embed --stats                   > eval\weilue-after.txt
python -m ui.build_ui_data --verify                 >> eval\weilue-after.txt
python -m eval.run_ranking_check --with-distractors --collapse --rerank --rerank-tpm 2000000 >> eval\weilue-after.txt
python -m eval.test_answer_eval
python scripts\mutate_part8.py
```

Then compare, and the four things to look at are:

1. **The seed digest.** It WILL differ from
   `2e84436cb38a463b0110613d5662d0067b8d16cc9e28e1db4c8374882314ecfc`. Write the
   new one down. It is the number Block E records on day one.
2. **The 172 claimed spans.** `resolved / case_only / moved / absent` should be
   unchanged, because `reference_translation` did not move. **If `moved` or
   `absent` grew, stop** — something touched the translation.
3. **`probe-chinese-weilue` and the `lzh` retrieval probe.** Their ranks before
   and after. An improvement is the fix working. A regression is a finding.
4. **29/30 and 22/30.** Both are recomputed by that ranking run. If 22/30 moves,
   that is the non-English-reachability figure moving, and it is the number this
   whole exercise is about.

## Step 5 — record it, then re-run the answer path once

```powershell
python -m answer.run_answer "How did Chinese sources describe the Roman empire?"
```

One live call. Then check what it quoted:

```powershell
python -c "import json,glob; f=sorted(glob.glob('eval/answer_runs/*.json'))[-1]; a=json.load(open(f,encoding='utf-8')); print([(q['doc_id'], q['source_field']) for q in a['grounding']['quote_spans']])"
```

**This is the acceptance test for the whole fix.** If a span comes back with
`source_field = original_text_excerpt`, the hero demo does what the brief says it
does, for the first time. If all of them still say `reference_translation`, the
corpus was not the only problem and that is a larger finding than Finding 9.

Update `chinese-da-qin`'s `archived_status` afterwards to record the 40/40
history and what changed — it is an observation field and must never be edited
to make a case pass, but this is a new observation, not a repair.

## What NOT to do

- **Do not re-run the sweep or recalibrate the floor as part of this.** They are
  Block E's, and mixing them in makes the corpus change unattributable.
- **Do not `git checkout --` anything** to tidy line-ending churn. Commit first
  and convert in place behind an assertion that your work is still in the file.
- **Do not run two mutation harnesses over one working tree at once.**
- **Do not renumber the rulings**, and do not delete ruling 25's recorded figure
  because it can no longer be re-derived. That it can no longer be re-derived is
  the cost, and it should be legible.
