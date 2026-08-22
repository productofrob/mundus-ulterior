# D2 — the expected_behaviour schema (2026-08-21)

*Drafted in a container holding a byte-copy of the four source files plus
`eval/answer_eval.py`, `answer/*.py`, the 24 seed records and all 78 archives —
a tree that reproduced the host's `71 passed, 0 failed` exactly before any edit
was made. **Every number below has since been re-measured on the host** and the
two agree.*

```
tree at start   f54c585, clean
tree at close   9ea1774  D2: every case declares its expected behaviour, and
                         the loader refuses a default

files changed   eval/goldset.py            CRLF   (unchanged: still CRLF)
                eval/gold/answer_cases.json  LF
                eval/test_answer_eval.py     LF
                scripts/mutate_part8.py      LF

ANSWER          eval.test_answer_eval    71 -> 98   GREEN on the host
mutations       mutate_part8             11 -> 23   all 23 verified on the host
gold cases      6, unchanged in number. All six now carry a ruled label
```

**No suite is red.** Both were run on the host, in that order, with the commit
between them.

D2 is the schema change and nothing else. **No new question was written**, on
purpose: a case drafted against a permissive loader is a case nobody can be sure
the strict loader would have refused. D3 writes the 24 new cases against the
loader below.

## The rule, and where it now lives

> Every case declares its expected behaviour explicitly, and the loader REFUSES
> to inherit it from a default.

`expected_behaviour` is in `_ANSWER_REQUIRED`. A case that omits it is a load
error. Three values:

| value | the corpus | what a red line MEANS |
| :---- | :---- | :---- |
| `answerable` | holds it | retrieval or assembly failed |
| `correctly_refusable` | does not hold it | the model invented something |
| `refusable_with_gloss` | holds it, untranslatably | a machine translation appeared, attached to a citation |

Those are three different pieces of news. Before D2 a red line said only *"this
case failed"*, and which of the three it was lived in a human's head.

## Eight new loader clauses, each with its own mutation

`expect_refusal` was **kept**, not derived. Two fields that must agree are a
guard; one field computed from the other is a guard deleted. The disagreement is
refused in both directions, and that is deliberately two clauses:

```
1  expected_behaviour is required            no default, no fallback
2  the value is one of the three             an unread label is not a label
3  correctly_refusable => expect_refusal     clause one of two
4  expect_refusal => correctly_refusable     clause two of two
5  a speaking case asserts positive content  see below
6  refusable_with_gloss names a quoted doc   the published gloss
7  refusable_with_gloss declares a hedge     expect_hedge_any
8  a hedge outside the gloss arm is refused  a rule that is not in force
```

**Clause 5 is the one that was not asked for and earns its place.** A refusal
contains none of the strings a case excludes, so a case built from
`expect_answer_excludes` alone is passed by silence. `_has_content_assertion`
already accepted such a case, because an exclusion IS a content assertion — it
just is not one an answer has to speak to satisfy. Clause 5 says: if the label
claims the answer should speak, something must require it to.

### The hedge is now a declared field

`expect_hedge_any` is new, and it is the one design decision taken inside the
ruling rather than handed up. The ruling was *"published gloss plus required
hedge"*, and **required** needs a way to identify the hedge. Previously
`vimose-runes`'s hedge group was one entry among four in
`expect_answer_contains_any`, indistinguishable from content — a later edit could
drop it and nothing would notice.

It costs no scorer change: **the loader merges the declared hedge back into
`expect_answer_contains_any` at construction**, so `answer_eval.py` sees exactly
what it saw before and `vimose-runes` still carries four groups. The separation
exists only at the point where the rule is enforced, which is load time. Reject
this and the fallback is to require *some* alternatives group and hope it is the
hedges.

## The discriminator is now enforced, not described

`paired_with` is symmetric and load-checked. Four clauses, four mutations:
a case may not pair with itself; the partner must exist; the partner must name
this case back; **and the two assertion blocks must be identical**.

`_ASSERTION_KEYS` is what gets compared — everything that IS the test.
`id`, `question`, `why`, `note`, `archived_status` and `paired_with` are
excluded, because the question is the only thing the two halves are allowed to
differ on. Confirmed identical on disk:

```
expected_behaviour  expect_cited_docs  expect_quoted_docs
expect_answer_contains_any  expect_answer_excludes  expect_min_resolved_quotes
```

Deleting one half is now a load error. Relabelling one half is a load error.
Both were prose in `answer_cases.json` and are now refusals with a message.

## FINDING 8 — the mutation harness was rewriting a source on every run, and said it restored it

Not argued from the code. **Observed, in this session, by running it.**

`scripts/mutate_part8.py` held `SOURCES = (eval/goldset.py, eval/answer_eval.py)`
and **those two do not agree on line endings** — goldset.py is CRLF, answer_eval.py
is LF. It captured originals with `read_text()`, which normalises every ending to
`\n`, and restored with `write_text()`, which writes the platform's. So a
mutation run converted one of the two to whatever the machine preferred: on the
container, goldset.py went 965 CRLF → 965 LF. **On the host it is answer_eval.py
that gets converted, LF → CRLF, on every run.**

The restore check could not see it, because it compared `read_text()` to
`read_text()` — normalised against normalised. It printed *"sources restored"*.

This is Finding 5 with a name and a reproduction, and D2 could not leave it: D2
doubles the number of times this harness runs. Fixed in the same file:

- originals captured and restored as **bytes**; the unrestored check compares
  bytes; the success line now reads *"sources restored byte for byte"*;
- each source is written back with **its own** line ending, detected at start;
- mixed endings inside one source are refused rather than silently picked.

Verified twice. In the container, `sha256` of both sources identical before and
after a full 23-mutation run, with goldset.py still CRLF and answer_eval.py
still LF. **On the host, `git status --short` after the 23-mutation run named no
tracked file at all** — only the untracked `commit-d2.txt`. Before D2 that same
command would have named `eval/answer_eval.py`, rewritten LF → CRLF by a harness
printing *"sources restored"*.

That second check is the one that matters, because the container and the host
convert in opposite directions and only one of them is the machine this project
is worked on.

## Also fixed: the non-Latin pipe, before D3 meets it

`BLOCK_D_START.md` records that a test whose failure detail is non-Latin **died
instead of failing**, through a pipe on Windows, and notes that `mutate_part8.py`
and `eval.test_answer_eval` are *"a different harness pair and have not been
checked against this"*. D3's cases carry Greek, Tamil and Chinese by
construction. Both ends are now named rather than inherited from the locale:

```
parent   subprocess.run(..., encoding="utf-8", errors="replace")
child    env PYTHONIOENCODING=utf-8
```

**Not proven, and deliberately recorded as not proven.** The host run was clean,
but no case in the gold set currently produces non-Latin *failure detail* — the
six that exist fail, when they fail, on English content terms. The pipe was
therefore never asked to carry Greek, Tamil or Chinese during the 23-mutation
run. The fix is defensive and untested; **D3 is what will test it**, on the first
mutation run after a case carrying non-Latin script fails.

## The six labels, as committed

Action item #5 says the owner rules on every expected-behaviour label. These six
went into `9ea1774`:

```
answerable            aksum-exports        paired_with adulis-exports
answerable            adulis-exports       paired_with aksum-exports
answerable            muziris-cargo
answerable            chinese-da-qin
refusable_with_gloss  vimose-runes
correctly_refusable   antikythera-absent
```

**One of them was contested at drafting time and has since been ruled on
explicitly.** `vimose-runes` could be read either way: the Elder Futhark
sequences are only partly deciphered, which argues gloss, but the record does
carry a `reference_translation`, which argues `answerable` with a hedge
assertion attached. The label is not cosmetic — gloss says a red line means *a
machine translation appeared*, answerable says *retrieval broke*.

**RULED: it stands as `refusable_with_gloss`.** The correct output is the source
plus its published hedged gloss, which is what the Part 6 translation case
asserts from the other side by passing only when the round trip is refused. It
also keeps one live example of the gloss arm on disk for D3 to pattern-match
against, rather than leaving the third value unexercised until D3 writes one.

## What D2 did NOT do

- **No new questions.** The gold set is still 6 cases. G4 needs ≥30.
- **No scorer change.** `answer_eval.py` is untouched. Block E's 270 calls go
  through the same scorer that scored the archives.
- **No floor change.** `floor.json` still names four required cases and
  `aksum-exports` as an open defect. `calibrated: false` still stands.
- **`aksum-exports` is still an open defect** and D2 did not close it.

## D3 — what it starts from

The stratification target, from `BLOCK_D_START.md` TASK 2: **≥3 per region
across seven regions (21 minimum), ≥6 source languages, balanced across the
three behaviours.** The corpus supports it:

```
arabia       4 records   grc, arc, xna, xsa
east_asia    3           lzh, ko
persia       3           xpr, pal, grc, en
scandinavia  4           gmq-pro, da, grc, en
south_asia   4           grc, oty, en
seasia       3           en, la, vi, fr
africa       3           grc, gez, xsa
```

Seven regions at ≥3 records each, and seventeen distinct language codes. The
stratification is reachable without inventing a record.

Three things D3 should not have to rediscover:

1. **Every label is the owner's to rule on.** The loader now refuses a case with
   no label; it cannot refuse a case with the *wrong* label. That check is human
   and has no mechanical substitute.
2. **`expect_quoted_docs`, not `expect_cited_docs`.** Unchanged advice, and the
   reason is still in the file: three of six passages in the Aksum evidence set
   carry gold terms.
3. **Every assertion is a fact about strings on disk.** Write the case against
   the record's `reference_translation`, not against a memory of what it says.

## Open, and deliberately not closed

- **Rulings 25 and 26 are still not in the register**, now quoted by four Block D
  documents. `RULINGS.md` indexes them; `PROGRESS.md` still does not declare them.
- **Nothing guards the `_chat` arity contract.** Untouched by D2.
- **`classify_span` still asserts a cause it cannot know.** Untouched by D2.
- **`mutate_ranking`, `mutate_part7b`, `mutate_places`, `mutate_ui_places`,
  `mutate_distractors` and `mutate_recover` still restore with `write_text`.**
  Finding 8 was fixed in `mutate_part8.py` only, because that is the file D2
  touched. **Five harnesses still rewrite line endings and still report
  "sources restored".** This is now a known defect with a known fix, not an
  open question.
