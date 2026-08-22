# Rulings register — 1 to 31

*Created 2026-08-21, at the close of Block D's TASK 0 and TASK 1. Extended the
same day with 27-31, declared during TASK 2 (D2's schema change and D3's case
work) and written up as they were made rather than afterwards — see the note on
rulings 20 and 21 at the foot of this file for why that matters.*

**This file is an INDEX, not the text.** Each ruling's authoritative wording
lives in the file named beside it, and that file is what to read before quoting
a ruling number at anything. This index exists because the rulings are spread
across five documents in three formats, and the failure that produced it was
specific:

> `PROGRESS.md`, at the close of C7: *"A thread told to read 'rulings 1-24' in
> the register will read exactly that and miss the two most recent — one of
> which pulled a kill trigger."*

Investigating that turned out to understate it. **Four rulings were unfindable,
not two.** Rulings 20 and 21 are inside the 1-24 range and have no declaration
section anywhere — they exist only as one-line entries in a numbered list in
`C5_START.md`, which every heading-based search misses.

## Where the text lives

```
1-11        BLOCK_C_RULINGS.md        full text, "## Ruling N" headings
12-19       C2_RULINGS.md             full text, "## Ruling N" headings
20-21       C5_START.md:149-150       ONE LINE EACH. No full text exists.
22-24       C2_RULINGS.md             full text, "## Ruling N" headings
25          C5_3B_AND_PROTOCOL.md §6  full text
26          C7_RESULT.md              full text
27-31       D3_RULINGS.md             full text, "## Ruling N" headings
```

## The register

```
 1  a multi-target query is ONE unit with N acceptable targets
 2  the four translation_case pairs accept the document's own published
    translation of the same section
 3  the gap is measured PRE-rerank, recall POST-rerank
 4  "wider than baseline" reads gapDoc
 5  C2 returns to the critical path
 6  the canary is a distractor, and the comment was wrong
 7  ruling 2 does NOT extend to the pairs C3 displaced
 8  a section is ONE retrievable record, canonically the original (C2a)
 9  `sole` is a ground, and it collapses
10  C2 is QUERY TRANSLATION, not hybrid lexical+dense
11  the record declares which text is primary, and it already does
12  the language set is derived from the INDEX, never from the pair
13  the fusion rule is MAX per candidate, declared before any run
14  every C2 run reports both arms, and the C2 claim is made against the
    same-run English-only arm
15  RULED 15b. What the five native-language queries are for
16  the reranker keeps receiving the pair's own query text
17  two mechanical guards on mistranslation, both free, and one sentence that
    travels with every number
18  C2a does not subsume C4, and the ranking harness cannot measure C4 at all
19  the renderings are frozen data, not a pipeline step
20  script floor 1.0; a retry is a different prompt under its own version
    -- SUMMARY ONLY, see below
21  attempts are additive; best_attempt promotes, a retry can only improve
    -- SUMMARY ONLY, see below
22  a stronger model refuses greedy decoding, and that is recorded rather than
    dropped
23  what the first real rendering run changed about the guard (23a uneven
    sampling recorded; 23b marks judged, not just letters)
24  the verdict is derived on read, never trusted from disk
25  RULED 3a. G2's gap criterion has FAILED. Kill trigger 1 pulled.
26  the two via-original keys are emitted from the COLLAPSE block
27  every case declares its expected behaviour, and the loader refuses to
    inherit it; expect_refusal is kept, not derived, and the two must agree in
    both directions
28  the gloss arm is for a contested READING of a text and nothing else;
    attribution, dating and identification doubts are ordinary content on an
    answerable case
29  a false premise the corpus can correct is ANSWERABLE; the refusal arm never
    means "the question was badly posed"
30  behaviour balance is held to the definitions and the shortfall recorded,
    never reached by widening a label
31  a discriminator loads as one instrument: paired_with is symmetric and the
    two assertion blocks must be identical, and it is NOT for two cases that
    merely share a record
```

## The two that pulled or nearly pulled something

**Ruling 25 is the one a reader must not miss.** It is the ruling that ended W3.

```
G2, gap criterion, on the pairs the baseline measured
    450-chunk gapDoc   +0.019622     B2 baseline   +0.024927     FAILED
    short by 0.005305 = 21.3% of the baseline
```

*"Kill trigger 1 is pulled. W3 does not start."* The sourcebook is polished at
24-60 records rather than chased to 200. Full text and the reasoning about what
the ruling costs: `C5_3B_AND_PROTOCOL.md` §6.

**Ruling 26** governs which figures a ranking run may print:

```
uncollapsed run              NEITHER via-original figure is reported
collapsed, not reranked      the pre-rerank figure alone
collapsed and reranked       both, side by side and labelled
```

The entry role the predicate reads is a fact the collapse produces, so a
reranked-but-uncollapsed run would publish post-rerank recall under a name that
says something else. Full text: `C7_RESULT.md`.

## Rulings 20 and 21 have no full text, and that is recorded rather than fixed

Both are referenced in `C2_RULINGS.md` prose — at lines 351, 358 and 425 — as
though a declaration existed. It does not. What exists is two lines in
`C5_START.md`'s summary list:

```
20. Script floor 1.0; a retry is a different prompt under its own version.
21. Attempts are additive; best_attempt promotes, a retry can only improve.
```

Both are nevertheless **built and mutation-verified** — `eval/test_ranking_check.py`
carries *"a rendering admitted by the old 0.6 floor is refused at 1.0"*, *"the
retry prompt is a different prompt from the first"*, *"a retried rendering
carries its own prompt version"*, *"an admitted attempt beats a held one whatever
the order"* and *"among equals the earlier attempt is kept, so a re-run changes
nothing"*, each with a mutation in `scripts/mutate_ranking.py`.

**So the code is the authority for 20 and 21, and no prose is.** They are NOT
reconstructed here: writing a plausible declaration after the fact and filing it
as the ruling is how a register stops being a record of what was decided and
becomes a record of what someone later assumed. If a full text is wanted,
someone who was there should write it — and until then this entry says so.

**Do not renumber.** Twenty-six numbers were already quoted across `PROGRESS.md`
and seven session documents before 27-31 were added, and 27-31 are quoted across
`D2_RESULT.md`, `D3_RULINGS.md` and the D3 batch commits.

## What 27-31 were written to avoid

Rulings 27 to 31 were declared and written up in the same session that made
them, with full text in `D3_RULINGS.md` and index lines above. That is a direct
response to what this file records about 20 and 21: a ruling that exists only as
a line in a summary list is a ruling nobody can quote, check, or argue with
later. The cost of writing the declaration at the time is a few paragraphs. The
cost of not writing it is that the code becomes the only authority for what was
decided, and code says what a thing does rather than why it was chosen.
