# Rulings 43 to 45, and findings 30 to 31 — declared 2026-08-29, in F1

*Written in the session that made them, for the reason `RULINGS.md` records
about rulings 20 and 21: a ruling that exists only as a line in a summary list
is a ruling nobody can quote, check, or argue with later.*

*All three rulings are recorded BEFORE the first new record is curated. That is
not a preference. `PHASE2_PLAN` F1 says "declare the tiering policy before
curating anything" and ruling 39 says a gate amended at the end is a gate
fitted to its result; a target mix set after the tranche exists is the same
move, and F1 is the last moment either can be made in advance.*

---

## Ruling 43 — the record tier vocabulary is FIVE, it is derived in code, and the declaration lives outside the record

**A record's tier is one of `verbatim_with_provenance`,
`verbatim_machine_english`, `published_translation_only`, `catalogue_record`,
`pointer_only`. It is DECLARED in `data/corpus_tiers.json` and DERIVED by
`ingest.fidelity.derive_record_tier`; `ingest.verify` fails when the two
disagree, when a record has no declaration, and when a declaration names a
record that is not in the corpus. `unclassifiable` is not a tier and may not be
declared.**

### The three tiers in PHASE2_PLAN could not hold the corpus that already exists

Measured, not argued. `ingest.loader` over the 24 records on 2026-08-29:

```
verbatim_with_provenance   11
published_translation_only  1   africa-01-ezana-stone
catalogue_record           11
NEITHER                     1   arabia-02-palmyrene-tariff
```

The Palmyrene Tariff has been in this corpus since Part 3. Its
`original_text_excerpt` is a pointer and it has no `reference_translation`, so
it is not verbatim, has no published translation to be the only thing it has,
and is not a find record. **No tier held it, and none of the three ever could.**

### The tier the tranche is PREDICTED to fill had no name at all

`PHASE2_PLAN` F3–F7 says it in terms:

> Expect the machine-translation path to fire. Local non-English sources mostly
> will not have published English, so `resolve_english` starts choosing
> `machine` and the Part 6 confidence machinery goes from dormant to
> load-bearing.

A record with source-language text and no published translation is not
`verbatim_with_provenance` — there is no published translation to cite — and it
is not `published_translation_only`, because there IS an original. **The tier
Block F expects to become its common case could not be written down, so the
target mix could not have a target for it**, and F7 would have discovered the
gap by finding the mix unaccountable rather than unmet.

`verbatim_machine_english` is that tier. `pointer_only` is the smaller half of
the same defect.

**This is ruling 38 one level over.** `floor.json` spent two days asserting the
opposite of what it had measured because no state fitted, and the answer was a
third state rather than a better argument about the two. A file with two states
will keep producing that contradiction; so will a table with three.

### What a tier is deliberately NOT

**A fact about the aligner.** `answer.align.Pair.ground` is
`section | index | document | none`, and an unalignable published translation
lands a reader on `published_document` rather than `published` —
`resolve_english`'s step 4, and a real distinction. It is reported beside the
tier and never inside it. A tier that moved when `align.py` changed would stop
being a property of the record, and the whole point of counting records is that
the count means the same thing in F3 as in F7.

### Why the declaration is a sidecar, and why the sidecar is not in the corpus directory

**Because a `tier` key on a seed record would MOVE THE CORPUS DIGEST.**
`loader.canonical_record_text` hashes the whole parsed record with sorted keys,
so any new key changes that record's `content_hash` and therefore
`corpus_digest` — `26e4a683`, the denominator of all 396 Block E runs and of
the sonnet arm's 165. `F1_START` says F1 does not move the corpus. Checked
before the file was written rather than after.

**And it is not under `data/seed_corpus/` either**, because `iter_seed_records`
refuses a `.json` at that depth: `glob("*/*.json")` would not see a top-level
file and `rglob("*.json")` would, and *a file that some walks see and others do
not is the exact failure this function exists to prevent*. Only
`manifest.json` is exempt, by name. **The layout guard fired on the first file
anyone has tried to add since it was written**, which is the only evidence a
guard of that kind can ever produce short of a defect.

So: `data/corpus_tiers.json`, one directory up, where no corpus walk reaches
it.

### Why DECLARED as well as derived

A tier that were only derived could never be wrong — and could never be checked
either. The declaration is what a curator believes the record is; the
derivation is what the classifier reads it as. **That is ruling 36's shape one
level down**: recorded and reconstructed are two kinds of knowledge and have to
be reported as two.

Both drift directions are refused, and that is deliberate. A record with no
declared tier is a record the mix cannot count. A declaration naming a record
that is not in the corpus is a stale entry making the count wrong in the
direction nobody checks — `calibration_scope`'s
`a_named_sweep_must_actually_fail_the_rule`, one level down again.

### Two clauses that are not obvious and are load-bearing

- **`partial_verbatim` and `transliteration` count as source-language text.**
  `partial_verbatim` means *flagged and unchecked*, not *not there*. Three of
  the eleven verbatim records carry it and four carry `transliteration`;
  excluding either would tier **seven of eleven** as holding no source text.
- **`verbatim_with_provenance` requires a non-empty `translation_source`.**
  `PHASE2_PLAN`'s wording is *"original text, published translation, both
  cited"*, and *both cited* is the clause that makes the tier a description
  rather than a claim. A record with a translation and no attribution derives
  `unclassifiable`, not a sixth tier: an unattributed translation is a curation
  defect. All eleven current records satisfy it, so the guard has eleven
  witnesses on the day it was written.

**Guarded:** 30 assertions in `ingest/test_fidelity.py`, 24 mutations in
`scripts/mutate_fidelity.py`, which carries the BASELINE check from the day it
was built rather than acquiring it later.

---

## Ruling 44 — the target mix across the 36 new records, declared before the first one exists

**Full numbers in `data/corpus_tiers.json.target_mix`, checked by
`ingest.fidelity.check_target_mix`, reported as a NOTE by `ingest.verify`.**

```
                             at 24    new    at 60
verbatim_with_provenance        11    +14       25
verbatim_machine_english         0    +10       10
published_translation_only       1     +4        5
catalogue_record                11     +8       19
pointer_only                     1     +0        1     <- a ceiling, not a target
                                --    ---       --
                                24    +36       60
```

```
region levelling      Africa, East Asia, Persia, SE Asia   3 -> 9  (+6 each)
                      Arabia, Scandinavia, South Asia      4 -> 8  (+4 each)
per region, at least  4 records carrying retrieval-eligible SOURCE-LANGUAGE text
gloss-capable         8 of the 36
quoted-from-original  at least 6 cases at 60
```

**Why a per-region floor as well as an aggregate.** Southeast Asia has **zero**
records carrying retrieval-eligible source-language text, which is why all four
of its gold cases sit on find records; Africa, Persia and Scandinavia have one
each. Every aggregate target above could be met inside Arabia and South Asia
alone, leaving five regions exactly as unable to answer a source-text question
as they are now. **An aggregate lets a total failure in one place be paid for by
successes in another, and the questions are not interchangeable** — which is
`required_cases_note`'s argument about the floor, one level up.

**Why zero new `pointer_only` records.** A record whose text lives somewhere
else grows the record count without growing the corpus. The one the corpus has
is a standing F8 spike.

**What "gloss-capable" means, mechanically, so it can be checked at curation
time rather than at sweep time.** The record carries, **inside a
retrieval-eligible chunk**, both a genuine alternative or hedged reading and a
statement that the reading is uncertain. Not in `notes` — the notes field is not
chunked and the model never sees it. This is not invented here:
`raqosh-epitaph`'s own note records that the case *"was nearly written that
way"* against the notes field, and *"a hedge assertion the corpus cannot support
is a case that can never pass."*

**And a gloss case may not sit on `verbatim_machine_english`.** A
`refusable_with_gloss` case requires the answer to quote a PUBLISHED hedged
reading. On that tier the only English is machine, and a machine translation of
a disputed reading arriving attached to a citation is *the worst output this
system could produce* — the thing the gloss arm exists to catch. A gloss case
there would test for the defect by requiring it. `GLOSS_CAPABLE_TIERS` is in
code and mutation-verified.

**Why eight.** The gloss arm is 3 against 22, which `F1_START` records as a fact
about the seed corpus rather than a defect. The sonnet arm then showed the
assertions **discriminate rather than being impossible** — `vimose-runes` went
0/12 to 5/5 with a real hedged gloss. A starved arm whose instruments work means
the supply of gloss-capable RECORDS is the binding constraint, and choosing the
records is the only moment it can be relieved.

**Why at least six `expect_quoted_from_original` cases.** There is exactly
**one** in thirty-three today, `weilue-chinese-quotation`, which is also the
corpus's only promotion candidate. One case is not a measurement of whether the
answer path quotes source texts; it is a measurement of whether it quotes THAT
source text. Six is the smallest number that can tell the two apart.

---

## Ruling 45 — G3's curation-cost box is amended in advance: cost is reported PER TIER, and against the declared mix

**The G3 checklist box "curation cost per record recorded and **trending
down**" is amended to: cost per record recorded PER TIER, reported beside the
declared target mix, and read as a cost claim only when the mix is met.**

**The box as written can be ticked by curating cheaper records.** A museum
object record is the cheapest record in this corpus to produce and a cited
bilingual inscription with a verified transliteration is the dearest. Nothing in
the original box distinguishes *the same kind of record got cheaper to make*
from *we made more of the cheap kind*, and the second reading satisfies it
completely while making the corpus worse. Kill trigger 3 hangs off this number:
*"if record 60 costs what record 12 cost, 200 is a staffing question rather than
an engineering one."* A mean over a shifting mix cannot answer that.

**This is FINDING 26's shape.** *Four sessions read 0.727272… and one of them
was different; the pass rate cannot see change.* An aggregate that moves for two
unrelated reasons reports one number and hides which one moved it, and the fix
both times is to report the thing underneath rather than to distrust the
aggregate.

**Recorded before F2 starts the column, not after.** Ruling 39 amended G3 in
advance because *a gate amended at the end is a gate fitted to its result*, and
this is the third box in the same checklist. F2 begins the minutes-per-record
column at record 25; a column that does not carry the tier cannot be
decomposed by it afterwards, because nobody times a record twice.

**Costs nothing.** The tier is derived from the record, so the column gains one
field that is already computed.

---

# FINDING 30 — a case's `archived_status` asserted another file's state, and went on asserting it after that file changed

**`weilue-chinese-quotation.archived_status` said the case was "tracked in
`floor.json.known_failing_cases` as an OPEN DEFECT". Ruling 38 moved it out on
2026-08-28, into the `promotion_candidates` state that ruling created. Nothing
anywhere had to notice.**

The field also said *"No archived answer has quoted this record's Chinese; the
count is 45 of 45 from the English across 16 runs."* `floor.json`'s own evidence
for the candidacy is *"3/3 in each of four sessions across three distinct UTC
dates… Chinese source text resolved in the answer."* The two files were stating
opposite facts about the same case.

**Why nothing caught it.** `archived_status` is prose. It is deliberately
outside `_ASSERTION_KEYS` — *"the QUESTION is the only thing the two halves are
allowed to differ on"* — so it is not scored, not compared, and not read by any
load-time check. It cannot re-score an archive and it cannot fail a suite. It
can only be read by a person, and a person read it on 2026-08-29 while counting
`expect_quoted_from_original` cases for ruling 44.

**This is ruling 38's own defect wearing the other file's clothes.** Ruling 38
exists because `known_failing_cases.weilue-chinese-quotation` said the case
fails while its own corrected text recorded 12/12, and the ruling's sentence
was: *a file that states a falsified claim about a case is worse through a
corpus move than either resolution of it.* Here the falsified claim is in the
other file and points back.

**CORRECTED, and the check DEFERRED, in writing.** The stale sentences are
corrected in place with the correction recorded beside them, which is
`excludes_corrected_on`'s precedent. The missing check — `eval/goldset.py`
refusing a case whose `archived_status` names a `floor.json` state that
`floor.json` contradicts — is **not built here**, for FINDING 29's stated
reason: it is recorded rather than fixed in the same hour as the thing that
found it. It is one token (`known_failing_cases`) tested against one file, not
prose interpretation, so it is a small F2 item and not a research question.

**PROGRESS.md's F0 state block carries the same stale claim** — *"The answer
path has still never quoted a non-English source text, so FINDING 10's guard
remains unprovable there."* It is left as written: `PROGRESS.md` is the record
of what was believed on the day, and correcting a historical state block is how
a history stops being one.

---

# FINDING 31 — `python -m ingest.verify` has been RED since 2026-08-22, and it is the first line of the F3 runbook

**Found the way the Block D findings were found: by running an instrument, not
by reading one.**

```
FAILED (1)
  x manifest-flagged record 'weilue' is labelled verbatim_original
```

`data/seed_corpus/manifest.json` names five records as paraphrased or partial.
That claim was held in **three** places: the manifest's prose,
`fidelity.PARAPHRASE_ID_HINTS`, and `verify.MANIFEST_FLAGGED`. On 2026-08-22,
commit `b1e11ab`, FINDING 11 corrected **one** of the three — the Weilüe's
excerpt is 221 verbatim characters from zh.wikisource and the hint was removed
with the reason written down, *"leaving it here would have the corpus report a
sourced text as paraphrased."* `verify.py` kept its copy and has been asserting
the opposite ever since.

**Seven days, and everything that ran in them.** D4, Block E's four sessions and
396 runs, F0, the sonnet arm's 165. Nothing caught it because **no state block
in this repository lists `ingest.verify` among the suites** — `F1_START` and
`F1_HANDOFF` both name six harnesses and four suites, and this is not one of
them — while `PHASE2_PLAN` F3–F7 puts `python -m ingest.verify` as the **first
line** of the block run after every sub-tranche.

**What it would have cost F3.** Nine records curated, then a red suite that has
nothing to do with them. *A true report inviting a false diagnosis* is the
misreading `BLOCK_D_START` warns about by name, and `F1_HANDOFF` adds the
2026-08-28 instance that cost twenty minutes. This one had a week's head start
and would have arrived on the day the corpus first moved.

**Fixed, and not by deleting the check.** `verify.MANIFEST_FLAGGED` stays: it is
this file's transcription of the manifest's prose, and transcribing prose by
hand is fine. What is not fine is holding a second **opinion** about what the
code does with it. So the never-`verbatim_original` assertion now runs over
`fidelity.PARAPHRASE_ID_HINTS`, a lift is a **written entry with a reason** in
`fidelity.PARAPHRASE_FLAG_LIFTED`, and `check_paraphrase_flags` refuses a
manifest flag that is neither honoured nor lifted, a lift with no reason, a
record that is both, and a lift naming a flag the manifest does not carry.
*Two ends of a comparison must not hold two definitions of the thing being
compared* — `iter_seed_records`'s own lesson, between two modules rather than
between two walks.

**Four guards, four mutations.** And the Weilüe's exemption is now written where
a reader of either file will find it, instead of in a commit message from a
week ago.

**What is still owed from this.** `ingest.verify` belongs in the state block of
every handoff document from here on, and in the suite list any thread checks
before believing the tree is green. Four suites and six harnesses were listed;
there are five suites.
