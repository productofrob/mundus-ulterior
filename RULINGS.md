# Rulings register — 1 to 52, and 80 to 82. **53 to 79 ARE NOT INDEXED
# HERE**, and the note under the table says why.

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
32-35       D4_RULINGS.md             full text, "## Ruling N" headings
36-42       F0_RULINGS.md             full text, "## Ruling N" headings
43-45       F1_RULINGS.md             full text, "## Ruling N" headings
46-48       F2_RULINGS.md             full text, "## Ruling N" headings
49-52       F3_RULINGS.md             full text, "## Ruling N" headings
53-79       NOT INDEXED. See the note below.
80-82       W3_RULINGS.md             full text, "## Ruling N" headings
83          UI_RULINGS.md             full text, "# RULING N" heading
84          UI_DESIGN_RULINGS.md      full text, "# RULING N" heading
85-87       UI_QUESTIONS_RULINGS.md   full text, "# RULING N" headings
```

## Why 53 to 79 are not indexed, written by the session that tried

**W3 needed the next free ruling number, found this file stops at 52, scanned the
F-block ruling files for the rest — and got three of twenty-seven wrong.** A
search for `## Ruling N` headings returned `F5_PART3_RESULT.md` for rulings 70,
71 and 74, because that file is where those rulings were READ AGAINST A RUN, and
the file where each was DECLARED is a different one. An index that names the
wrong file is worse than an index that stops, and this file exists precisely
because four rulings were once unfindable.

**So the gap is recorded rather than filled by a guess.** 53 to 79 are declared
across `F4_RULINGS.md`, `F5_RULINGS.md`, `F5_PART3_RULINGS.md`, `F6_RULINGS.md`
and `F7_CURATION_START.md`, and a session needing one of them reads those five
files rather than trusting a line here. **Filling this in correctly is one
careful pass by somebody who checks each entry against the file that DECLARES it
rather than the file that mentions it, and it is worth doing.** W3 is not that
session: it had already caught itself getting it wrong.

**The next free ruling number is 88. The next free finding is 105.**

> **FINDING 104, 2026-09-08.** A file written from the cloud session to this
> machine can report SUCCESS and not land. Seen twice in one sitting on
> `ui/index.html`: the write returned the path as written, and the file on disk
> still had its old size and old content. The second identical write landed
> both times.
>
> **The danger is not the lost write, it is what happens next.** After the
> first occurrence the harness was run against what was believed to be the new
> file and reported 45 green — it was reading the OLD one, and would have
> reported the same on a change that broke the page. A green harness proves
> nothing about a file that never arrived.
>
> So: after writing a file to this machine, CHECK THE FILE — byte count, or a
> grep for a string the change introduced — BEFORE running anything against
> it. `git status` is the cheapest version: a write that landed shows the file
> as modified.

> **UPDATED 2026-09-08, same block, after its first close.** **Ruling 87**: a
> refusal says WHICH KIND of refusal it is — outside the corpus, a record whose
> text is unreachable, a record whose notes advertise what its text does not
> hold, or an answer everything nearby makes look available — in one sentence
> per case, shown when the question is opened, and **every claim those
> sentences make is re-derived from the bundle by guard 46**, because a typed
> sentence about the corpus is the prose form of a typed count. The rail group
> is renamed *Not fully answerable*. Full text in `UI_QUESTIONS_RULINGS.md`.

> **FINDING 103, added by the same block, 2026-09-08.** Git cannot commit from
> the Linux bridge unless FILE DELETION is enabled for the repository folder.
> Every commit creates and removes `.git/index.lock` and `HEAD.lock`, and an
> unlink that is refused leaves a lock behind that blocks every attempt after
> it — `git add` and `git commit` both fail with "Another git process seems to
> be running", which names the wrong cause. This session found a stale
> `index.lock` already sitting in `.git/`, dated before it started: the fossil
> of an earlier attempt that hit the same wall and left no other trace.
> Enable deletion for the folder at the START of a block. FINDING 94 is the
> neighbouring one — the bridge needs `psycopg[binary]` and `sqlglot` installed
> or `scripts/state_block.py` reports a RED that is not about the repository.

> **UPDATED BY THE UI QUESTIONS BLOCK, 2026-09-08.** This line read *"The next
> free ruling number is 85. The next free finding is 102."* The block used
> **ruling 85** (the run picker retired: a run keeps its ADDRESS and loses its
> CONTROL — `#q/<slug>/r/<stamp>` still resolves and nothing on the page offers
> the other runs, which narrows ruling 84 without reversing it), **ruling 86**
> (what the question rail lists: the 24 questions with a showable run, grouped
> by the region `gold.answer_cases` declares; the 7 the project declared
> `correctly_refusable` grouped and labelled as that rather than deleted; the 2
> failures counted in a derived line rather than dropped in silence — and
> `QUESTIONS` itself left unfiltered, so every question is still addressable)
> and **FINDING 102** (clicking a question from the foot of the rail left the
> answer 1,461px above the viewport at 1600px and 2,505px on a phone; found by
> using the page, fixed in the same commit). Full text in
> `UI_QUESTIONS_RULINGS.md`, scored in `UI_QUESTIONS_RESULT.md`, and carried
> back here in the same sitting.
>
> **And one thing corrected while here:** the index table above stopped at 83
> and did not name `UI_DESIGN_RULINGS.md` for ruling 84, which the design block
> declared. It does now. That is exactly the drift the note below describes,
> one row rather than one number.

> **UPDATED 2026-09-08.** FINDING 101: build_ui_data.py writes with
> `Path.write_text`, which is text mode, so a run on the Windows host turns
> every `\n` into `\r\n` — and `.gitattributes` is `* -text`, so git stores
> those CR bytes verbatim. It surfaced on `ui/data.js`, where it is harmless.
> It would not be harmless on `data/seed_corpus/`, where 168 archived citation
> spans point into the records BY EXACT OFFSET and one inserted byte per line
> shifts every offset after the first newline. Recorded in the commit that
> carried the regenerated bundle.

> **UPDATED BY THE UI DESIGN BLOCK, 2026-09-07.** This line read *"The next free
> ruling number is 84. The next free finding is 100."* and was correct when it
> was written. The design block used **ruling 84** (the hash scheme: a run is
> named by its timestamp and never by its index, a question by a slug of its own
> text, and a hash that does not resolve says so rather than landing on the
> default view) and **FINDING 100** (`check_ui.mjs` counts inline scripts inside
> HTML comments, so a comment containing the text of a script tag turns the
> harness red — it fails safe, and it is recorded rather than fixed because a
> design block editing the guard file it is judged by is worse than the defect).
> Both are declared in `UI_DESIGN_RULINGS.md` and `UI_DESIGN_RESULT.md`, and
> carried back here in the same sitting, which is the practice the correction
> below exists to enforce.

> **CORRECTED BY THE UI BLOCK, 2026-09-07.** This line read *"The next free
> ruling number is 83. The next free finding is 97."* and the finding half was
> already one behind when it was written: **W3 used 97** — the three
> `mutate_fidelity` mutations that reported MISS — and recorded it in
> `W3_RESULT.md` §5 without carrying it here. `UI_START.md` §10 said 98 and was
> right. The UI block then used **98** (the `whitespace_only` span rendering
> clean, reading broken and explaining nothing) and **99** (every citation
> marker on the page emitted as broken HTML), and **ruling 83**. The original
> sentence is quoted rather than deleted, because a next-free line that has
> silently drifted once will drift again, and the way it drifted is the useful
> part: **a number used in a RESULT document and not carried back here is
> invisible to the next session that needs one.**

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
32  a lost gold pair kills the run; the only way past it is --allow-unresolvable
    naming the pair, and an allowance that has gone stale is itself refused
33  DATES gate calibration (three distinct UTC dates); sessions are recorded and
    named beside them and gate nothing; a sweep with no session identity blocks
    calibration permanently rather than being given a date after the fact
34  a mutation target must be unique across SOURCES and is refused when it is
    not; the child runs with -B AND the bytecode cache is purged before it
35  per-session stability is a statement about VERDICTS and may not be quoted as
    a statement about behaviour; behaviour is distinct_texts and the answer
    hashes, reported separately
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

**Do not renumber.** Thirty-one numbers were quoted across `PROGRESS.md` and a
dozen session documents before 32-35 were added on 2026-08-25. Originally:
Twenty-six numbers were already quoted across `PROGRESS.md`
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

## 49-51, declared in F3 before record 25 was ingested

Full text in `F3_RULINGS.md`, in the same session, together with FINDING 33.

```
49  the CORPUS is part of the calibration scope. floor.json gains a corpus
    clause -- a seed record count and a digest -- and a sweep calibrates only
    at the declared corpus. Ruling 36's sentence one dimension over: without
    it, the moment record 25 lands, the file's own anti-loophole would have
    INSISTED that a 33-record sweep calibrate a floor set at 24. FINDING 14
    put corpus_version into every archive so a corpus that moved could not go
    unnoticed; calibration_scope was written twice without reaching for it.
    The floor is NOT suspended for the tranche: a run at a moved corpus still
    computes a verdict, and what it may not do is RE-CALIBRATE.
50  the THIRD UTC date at 60 records is BOOKED, as a ninth session. Three
    rules require three dates at 60 -- min_distinct_dates, the promotion bar
    and vimose's reinstatement condition -- and G3's amendment booked two.
    The F8 spike is not spent on it: the two records it would promote are the
    corpus's only pointer_only record and its companion.
51  a sub-tranche re-runs the RANKING check and a floor PROBE; the answer
    sweep runs at 60 and nowhere else. A mid-tranche sweep produces a number
    no rule here may read. The probe is the three required cases at
    min_repetitions, archived to eval/probes/ and never to eval/sweeps/, so it
    cannot calibrate BY CONSTRUCTION. And the 36 records are ALLOCATED across
    F3-F7 as slots, hard regions first, every source-language record before
    every catalogue record, checked by ingest.verify.
52  a ledger row may be RETIRED, and only if its record does not exist.
    Source hunting is the phase that DECIDES which record exists, so the clock
    cannot be started against the right id until the phase it is timing is
    over -- the first record this project ever timed proved it in three
    minutes. `retire` keeps the row and its written reason rather than
    deleting it, and the minutes are re-filed with `add` as ESTIMATED, because
    a span measured against a record id the hunt had not settled is not a
    measurement of the record that landed. The anti-loophole is the whole
    design: a row may be retired only if its record is NOT in the corpus,
    or retirement takes the expensive records out of the column kill trigger 3
    reads.
```

Ruling 49 is the one to read before archiving or quoting any sweep run after
record 25. Ruling 51 is the one to read before running anything at a
sub-tranche.

FINDING 39 is the one to read before curating ANY record: a
correctly_refusable case asserts what the corpus does NOT hold, and a record
can falsify it. Eight cases make that claim.

FINDING 38 is the one to read before hunting a verbatim_machine_english
record: publishing an inscription means translating it, so the tier cannot be
filled from English-language scholarship at all.

FINDING 35 is the one to read before quoting a number out of a document
rather than out of a tool: *"nine archives, 396 runs"* had been copied
since Block E, and the archives hold 492.

FINDING 34 is the one to read before writing a date into anything: rulings
49-51 were stamped 2026-08-29 on 2026-08-31, from `F3_START.md`'s opening line
rather than from a clock, and the host suite caught it.

FINDING 33 is the one to read before booking a day: three rules required a
third date at 60, two of them written on the same day as the gate that booked
two, and no document held the sum.

## 46-48, declared in F2 before a single record was timed

Full text in `F2_RULINGS.md`, in the same session, together with FINDING 32.

```
46  KILL TRIGGER 3 IS EVALUATED WITHIN THE TRANCHE. Nothing anywhere records
    what record 12 cost, so the trigger as written -- "if record 60 costs what
    record 12 cost" -- cannot be evaluated at all. The measurable claim is a
    trend across records 25 to 60, per tier, in curation order, with n stated
    beside it, and it is a WEAKER claim than the trigger as written. A
    manufactured baseline was refused: re-curating a solved record is
    systematically cheap and would bias the trigger toward "costs have not
    fallen". min_n_to_read_as_a_trend is 10, so published_translation_only (4
    new) and catalogue_record (8 new) can never be read as trends in Block F.
47  the minutes are divided into SEVEN PHASES -- source_hunting,
    rights_and_licence, text_capture, translation_and_fidelity, placement,
    authoring, rework -- fixed before the first record is timed, and a record
    entry that omits a phase is REFUSED. A single figure per record is
    gameable by re-labelling work, which is ruling 45's defect one level down.
    A phase that went to zero has to say zero.
48  measured and remembered minutes are two kinds of knowledge and are
    reported as two. An estimate needs a written reason, a part-clocked cell
    is an estimate, a measured span above 240 minutes is refused, and an open
    clock fails ingest.verify.
```

Ruling 46 is the one to read before quoting any curation-cost number: the
comparator is not the one `PHASE2.md` names, and the difference is the whole
of the ruling. Ruling 47 is the one to read before timing a record, because
nobody times a record twice.

FINDING 32 is the one to read before deferring a check with its implementation
described: the check FINDING 30 deferred could not be built as deferred, and
F1's own correction to `archived_status` is the counterexample.

## 43-45, declared in F1 before a single new record was curated

Full text in `F1_RULINGS.md`, in the same session, together with FINDING 30 and
FINDING 31.

```
43  a record's TIER is one of five, not three. It is DECLARED in
    data/corpus_tiers.json and DERIVED by ingest.fidelity.derive_record_tier,
    and ingest.verify fails when they disagree, when a record has no
    declaration, and when a declaration names a record that is not in the
    corpus. `unclassifiable` is not a tier and may not be declared. The
    declaration is a sidecar OUTSIDE the record because a `tier` key would
    move the corpus digest, and outside data/seed_corpus/ because
    iter_seed_records refuses a .json at that depth.
44  the target mix across the 36 new records, declared before the first one
    exists: 14 / 10 / 4 / 8 / 0 by tier, region levelling to 8-9 each, at
    least 4 source-language records PER REGION, 8 gloss-capable records, and
    at least 6 expect_quoted_from_original cases at 60.
45  G3's curation-cost box is amended in advance: cost per record is reported
    PER TIER and against the declared mix. "Trending down" is otherwise
    satisfiable by curating cheaper records, and kill trigger 3 hangs off it.
```

Ruling 43 is the one to read before adding any record to the corpus. Ruling 45
is the one to read before F2 starts the minutes-per-record column, because a
column that does not carry the tier cannot be decomposed by it afterwards.

FINDING 31 is the one to read before believing the tree is green: there are
FIVE suites, and `ingest.verify` — absent from every state block in this
repository — had been red for a week.

## 40-42, declared before F1 curates anything

Full text in `F0_RULINGS.md`, in the same session. Each settles what a whole
family of the 36 new records will be scored against, which is why they are
recorded before the records are written:

```
40  an article the writer added to a quotation is a NAMED match class,
    `article_added`, and it resolves. The span covers the record's characters
    and not the article, and it is never reported as `exact`.
    cite.QUOTE_RESOLUTION_CONTRACT dates what counts as resolved, because
    archived spans are never re-resolved.
41  on a correctly_refusable case, an expect_answer_excludes entry may not be
    built from the case's own question — a correct refusal restates the
    question it refuses. Refusal cases exclude FABRICATION MARKERS.
42  skz-titulature is tracked as an open defect rather than corrected away.
```

Ruling 40 carries a CORRECTION made the same day, in the same section: it first
said such a span landed in `absent`, and it landed in `case_only`. Read the
correction, not only the ruling.

## 36-39, declared before F1

Full text in `F0_RULINGS.md`, written in the session that made them. All four
settle questions `BLOCK_F_START.md` left open on purpose, and all four are
recorded BEFORE the first sub-tranche moves the corpus:

```
36  the ARM — (model alias, temperature) — is part of a sweep's identity and
    part of the calibration scope. Without it, floor.json's own anti-loophole
    would have INSISTED that a temperature-1 sonnet sweep calibrate a floor
    set on greedy haiku.
37  ONE bar governs promotion and reinstatement: 3/3 in each of three sessions
    on three distinct UTC dates, at the corpus in force. Raised from two on
    two, by FINDING 26.
38  the promotion-candidate state — not required, not known-failing, reported
    beside the floor verdict and counted toward neither.
39  G3 is amended in advance, gated on Block F's own numbers at 60, and the
    second session the amendment costs is booked with it.
```

Ruling 36 is the one to read before archiving any sweep that is not
`chat-default` at temperature 0.

## 32-35, declared in TASK 3

Full text in `D4_RULINGS.md`, written in the session that made them, for the
reason this file gives about 20 and 21. Ruling 35 is the one to read before
quoting a stability number: it constrains prose and adds no code.
