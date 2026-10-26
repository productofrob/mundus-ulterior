# Findings 9 to 13

*Written 2026-08-22, after D3 had closed. Findings 1–5 are in `D_TASK0_RESULT.md`,
6–7 in `D1_RESULT.md`, 8 in `D2_RESULT.md`. This document covers an investigation
that began as a single corpus fix and turned into four more defects, three of
them in the instruments rather than the data.*

**On the numbering.** Finding 11 was assigned retrospectively. Findings 12 and 13
were named while 11 was still an unfilled gap, and 11 is recorded here in the
place it belongs chronologically rather than the order it was numbered. Said
plainly because a register that quietly renumbers is worse than one with a scar.

---

## Finding 9 — the flagship record's Classical Chinese was invented

`eastasia-01-weilue` is the record the AI Technology Showcase brief names by
name. Its `original_text_excerpt` held 52 characters of plausible Classical
Chinese **that do not occur in the Weilüe**.

Checked fragment by fragment against the Sanguozhi text: **all three fragments
absent, 0 of 3.** Four divergences, and in each the record's form appears nowhere
in the source while the real form is present:

```
record          source          
犂靬            犁靬            the name Lijian
安谷城          安穀城          the city Angu
城以石為壁      以石爲城郭      the stone walls
海西人名之海西  故俗謂之海西    "called Haixi"
```

`ingest.fidelity` classified it `partial_verbatim`, retrieval-eligible. It has no
way to detect this.

**The corruption was not discovered here, and the credit belongs elsewhere.**
`PROGRESS.md`, Da Qin block §4, records it with the specific divergences named
and states that `海西人名之海西` *"corresponds to nothing in the source"*. It was
deliberately not fixed then, on a ground worth restating: correcting a primary
source from a secondary work's quotation (Paolillo quoting Chen Shou 1975) would
itself be an unsourced edit. The stated blocker was a print edition or a stable
digital facsimile, *"zh.wikisource, which the record cites as citation_original,
returned nothing fetchable."*

**Why it was fetchable this time: the record was citing the wrong page.** The
魏略輯本 edition's index lists 西戎傳 — including 大秦國 — under 卷二十二, and
卷二十二 is an unwritten page. The text lives where the record's own
`language_note` always said it did: Pei Songzhi's commentary in the Sanguozhi,
Wei Shu 30. That is a primary transmission, so the 2026-08-13 objection is met
rather than waived.

**What this session added** was not the discovery. It was: that the text was
*invented* rather than corrupted; the 45-of-45 answer-side measurement; the
reason the citation was unusable; and the fix.

### What the fix changed, measured: nothing

```
pairs 33 / units 30                      unchanged
172 spans  resolved 161 case_only 9 moved 1 absent 1   unchanged
recall@6 via original, reranked  22/30 -> 22/30
china-describes-rome-weilue       5/1/7 -> 5/1/7
probe-chinese-weilue              1/1/1 -> 1/1/1
```

Only `mrr_at_10_reranked` moved, by 0.0006 — reranker noise under ruling 22.

Retrieval was never going to move, and the entry role says why: the English query
enters through the translation chunk and the Chinese query through the original
chunk, before and after. **Replacing the content of a chunk cannot change which
chunk a query enters through.**

**That the measurements did not move is itself the finding.** The fabrication was
never distorting the ranking figures. It was sitting underneath them.

### A correction to how this was framed

The brief says *"Retrieves the Weilüe passage on Da Qin in Classical Chinese."*
That claim is about **retrieval** and it is satisfied — `probe-chinese-weilue`
ranks the Chinese chunk 1, and it is `[S1]` for an English question too. Reading
it as broken conflated retrieval with quotation. The brief is fine. The gap is
finding 13, and nobody had separated the two claims.

### Two `subject_places` notes rested on the fabrication

Angu was spelled `安谷城`, a form absent from the source. More seriously, the Da
Qin entry refused a Pleiades identification partly because *"the Chinese excerpt
is elided at exactly the point where the capital is described"* — true of the
fabrication, false of the Weilüe, which reads `其王治濱側河海，以石爲城郭`. **A4's
decision is unchanged** and stands on its main ground, that the city of Rome is
not the empire; the second reason is recorded as withdrawn and dated.

---

## Finding 10 — nothing anywhere guarded a process's own stdout

Three boundaries carry non-Latin text out of this project. Until today only two
were guarded anywhere:

```
1. a CHILD process's stdout      PYTHONIOENCODING in the child's env
                                 guarded: mutate_ranking.py (Part 7),
                                          mutate_part8.py (D2)
2. a PARENT decoding that child  subprocess.run(encoding="utf-8")
                                 guarded: the same two files
3. THIS process's own stdout     NOTHING, in any of 43 entry points
```

Boundaries 1 and 2 are about a pipe between two processes. **Boundary 3 is about
where a process writes when nobody is reading its console**, and it is the one
that fires under a redirect.

**So the D2 fix was half a fix.** It secured the pipe into the parent and left the
parent's own output open — in a harness that deliberately prints the child's
captured text verbatim to preserve failure detail. Part 7 made the identical
partial fix at `mutate_ranking.py:749`. Two people, the same blind spot, a month
apart.

Found by running `WEILUE_FIX_RUNBOOK.md` step 0 as written: `python -m
ui.build_ui_data --verify >> eval\weilue-before.txt` died at
`build_ui_data.py:730` printing the Greek behind a `case_only` span. On Windows
`print` writes through a stream whose encoding comes from the console code page,
and through a pipe or redirect it falls back to cp1252. **It does not degrade. It
raises, mid-output, with the file half written and every number in it correct.**

**Why it mattered more than the crash:** `eval/run_answer_sweep.py` was
unguarded. Block E is 30 cases × 3 repetitions × 3 days, every answer quoting a
corpus that is Greek, Tamil, Chinese, Geʽez and runic, and nobody runs a
three-day sweep without redirecting it to a log. It would have died on day one,
after spending real chat calls.

### The count was wrong four times: 7, 20, 22, 43

Twice from typing a list by hand. Once because `eval/answer_eval.py` — the scorer
itself, which prints failure detail full of corpus text — was missed twice
running. **And once because the list was verified against a partial copy of the
repository rather than the repository**: twenty-one entry points existed that the
checking tree did not contain, so the check passed on a tree where the files were
absent.

So the list was deleted. `test_every_entry_point_guards_its_stdout` asserts the
**rule** — every file under `ui/ eval/ answer/ ingest/ scripts/` carrying a
`__main__` must carry the guard — and enumerates by glob at check time. It also
asserts the glob found at least forty files, because an enumeration that
collapses to zero passes vacuously.

Inlined in 43 files rather than shared, for a specific reason:
`ui/build_ui_data.py` documents `python ui/build_ui_data.py` as an invocation, and
under that form the repository root is not on `sys.path` — a helper module would
be unimportable for exactly the file that found the defect.

`errors="replace"` is a judgement. A harness that cannot encode one character
should print a replacement and finish. **A mangled character is cosmetic; a sweep
that dies on day two of three is ninety chat calls and an unrepeatable
measurement.**

### Demonstrated, after a first attempt that proved nothing

The first proof was `python -m eval.test_answer_eval > file` returning exit 0.
**It was vacuous.** A passing suite prints only `ok` lines with English labels;
the non-Latin lives in failure detail a green run never emits. Zero non-Latin
characters reached the file. That is the project's own trap — *a check that greps
a heading passes against a report that prints the heading and no rows* — written
into a runbook an hour after being invoked against someone else's code.

The real proof is the command that died, in a fresh shell with **no environment
variable set**:

```
python -m ui.build_ui_data --verify > eval\stdio-guard-proof.txt 2>&1
exit code 1        <- the gate failing on moved 1 / absent 1, BY DESIGN
Traceback present:          False
UnicodeEncodeError present: False
60 lines written, report complete through the final case_only block
```

Boundary 3 fixed. **Boundary 4 — PowerShell decoding the child with
`[Console]::OutputEncoding` — is a shell setting no code can fix**, and the same
file shows 16 mojibake runs to prove it. Both are named in step 0 of the runbook
now. Before the fix there were no bytes at all; now there are correct bytes that
PowerShell mangles on the way in.

---

## Finding 11 — the paraphrase flag marks suspicion, and nothing ever turned it into a determination

`ingest/fidelity.py` carries `PARAPHRASED_ORIGINALS` and `PARAPHRASE_ID_HINTS`,
five records flagged by the manifest as *"paraphrased or partial rather than
verbatim"*. The branch that reads them says:

> *"Where the original script is actually present, the wording is the source's
> own — it is abridged, not invented."*

**That is the assumption finding 9 disproved on the first record anyone checked.**

Two of the five carry real non-Latin text. `eastasia-01-weilue` was invented.
`eastasia-02-hou-hanshu` was checked the same way on 2026-08-22 and is **genuine**
— 34 of 36 characters identical to the Sanguozhi transcription, one traditional/
simplified pair (獻/献, an artefact of the `zh-hans` view), and one variant
character for the same word (瑇/玳, tortoiseshell), which needs a traditional-script
edition to settle.

So the flag never distinguished them. It marked suspicion; nothing in the
pipeline ever converted suspicion into a finding, and the comment asserting the
benign reading sat there for both.

A related staleness: `southasia-01-akananuru-149` is still on the hint list while
its own note records verbatim Old Tamil recovered on 2026-08-09, and the
corrected Weilüe is still labelled `partial_verbatim` by the override rather than
`verbatim_original`. **Not fixed at the time of writing** — it requires a
re-ingest and was deliberately kept out of the Weilüe measurement.

**A hypothesis about the fabrication, offered as a hypothesis.** The Hou Hanshu's
own Da Qin section opens `大秦国，一名犂鞬` — with **犂**. The Weilüe reads
`大秦國一號犁靬` — with **犁靬**. The invented text read `大秦國一號犂靬`: **犂**
from the Hou Hanshu, **靬** from the Weilüe. A blend of the two Da Qin passages
this corpus holds, adjacent in the same region folder. Consistent with a hurried
synthesis from neighbouring sources rather than a transcription slip, but
circumstantial.

---

## Finding 12 — the ranking harness drops unresolvable gold pairs silently

Both Weilüe ranking pairs carried `expect_text_contains: 大秦國一號犂靬` — the
**fabricated** form — one of them with an explicit note saying it asserted *"the
characters that are on disk, not the characters that ought to be"*, a documented
workaround for a known-bad record.

When the record was corrected, the assertions matched nothing. Both pairs left
the run. The harness said only:

```
"31 pairs, 29 distinct query text(s) embedded in 1 request(s)"
```

A count line. No warning. And every headline number moved:

```
pairs 33 -> 31     units 30 -> 29
recall@6 via original, reranked   22/30 -> 21/29
```

**The denominator shrank.** `0.7333 → 0.7241` reads like a small regression; it is
a measurement that lost a pair. This is the project's own trap in the aggregate
line of the ranking harness, and it is the reason the invalid `160349` archive is
committed and kept: it is what this finding looks like from the inside.

`scripts/weilue_compare.py` reports a vanished pair loudly and says explicitly
that zero movement after a corpus edit is itself a finding. **The harness itself
is still unguarded** — a pair-count check against the gold file is scheduled
before Block E.

---

## Finding 13 — nothing in the answer path ever asks for a source text to be quoted

Not a weak preference. An absent mechanism.

Prompt rule 3 permits a quotation from *"the SOURCE TEXT or the ENGLISH shown for
that source"* and requires neither. English is easier and reads better, so English
wins. Measured across 16 archived runs of `chinese-da-qin`: **45 of 45 resolved
spans from `reference_translation`, none from `original_text_excerpt`.**

The corpus fix proved retrieval was never the obstacle. On the live run of
2026-08-22 the Chinese chunk was `[S1]` — top of the evidence block, similarity
0.576, traceable to `original_text_excerpt[0:221]` — and the model quoted the
English anyway, five times out of five.

**The corpus fix was necessary and could never have been sufficient**, and it was
predicted here that it might be. It was not.

`expect_quoted_docs` cannot express the difference, because it is satisfied by a
quotation from either of a record's chunks — which is exactly why the hole was
invisible. `expect_quoted_from_original` now can. Strictly additive: a new
optional key and a scorer branch that runs only when the key is present, so no
existing verdict can change, which matters because Block E's 270 calls go through
that scorer.

`weilue-chinese-quotation` is the standing detector, expected to fail, tracked as
an open defect. **Closing it means changing prompt rule 3**, which cannot happen
before Block E without invalidating every archived number.

---

## What is fixed, and what is not

```
FIXED       9   the record now holds 221 sourced characters; two ranking pairs
                retargeted; two subject_places notes corrected
FIXED      10   43 entry points guarded, demonstrated at the boundary that failed
OPEN       11   the fidelity override is stale on two records and its justifying
                comment is disproved; needs a re-ingest
GUARDED    12   in weilue_compare.py only; the harness itself is unguarded
DETECTED   13   assertable and detected, not fixed — the fix is a prompt change
                and the prompt is frozen
```

## Open, and deliberately not closed

- **`eastasia-02-hou-hanshu`'s `original_text_note` still promises a cross-check
  "during ingestion"** that has now been performed. It should record what was
  checked, against which page, with what result, and flag the 瑇/玳 variant as
  unresolved.
- **The 瑇/玳 variant is unresolved** and needs a traditional-script edition.
- **`ingest/fidelity.py`'s comment is false** and its hint list is stale for two
  records.
- **`run_ranking_check.py` has no pair-count guard.**
- **`match_case` silently shadows a duplicate question.**
- **The `weilue-before.txt` capture has mojibake Greek quotations.** Every number
  in it is correct; the quotation lines are not evidence of anything.
- **Ruling 25's figure can no longer be re-derived from the tree.** The corpus
  moved. The ruling stands; the cost was accepted deliberately and is recorded
  rather than tidied away.
