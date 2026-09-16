# UI LOOSE ENDS RESULT — **C, D AND E CLOSED IN ONE SESSION. E WAS ALREADY
# DONE, D HAD ALREADY BEEN MEASURED, AND C IS THE ONLY ONE THAT NEEDED CODE.**
#
# **Scope per `UI_LOOSE_ENDS_START_AMENDMENT_1.md`: C, D, E. A and B moved to
# Methodology Final; F is cut. Nothing here touches the Methodology tab or the
# Lovable port.**

*Closed 2026-09-16. No ruling or finding numbers are assigned here.*

---

## 0. The bridge shell is back

`device_bash` ran git, python and node from the session this morning — the first
time since the 2026-09-08 Windows update. **One cost, paid and cleared:** a plain
`git status` from the bridge left `.git/index.lock` (FINDING 94's exact shape).
Delete permission was granted, the empty lock was removed, and every later git
read ran with `GIT_OPTIONAL_LOCKS=0`, which leaves no lock. **Commits stay on the
host.**

---

## 1. E — the commit check. **CLOSED, NOTHING TO COMMIT**

`git log --oneline -8` tops at `90a5a5e` (Amendment 1), working tree clean before
this block wrote anything. All three handovers are tracked and in the log:

```
UI_METHODOLOGY_DESIGN_PREDICTIONS.md   671e5c8
ui/measure_data.mjs                    596d74c
RIGHTS_VALIDATION_START.md             8e1f8f9
```

The open question in Amendment 1 §5 is answered: they landed.

---

## 2. C — the two declared rights fields. **CLOSED, GUARDED AND MUTATION-VERIFIED**

`ingest.fidelity.check_rights` now checks both fields before the `unread` early
return, against the schema and not against today's cells:

```
unread cell   unread_reason required               "no unread_reason"
              unread_reason in UNREAD_REASONS      "is not one of"
              no contradicts_record_prose          a contradiction needs a reading
read cell     no unread_reason                     the unread/states_no_terms collapse
              contradicts_record_prose, if present, is a boolean
```

`UNREAD_REASONS` is the three values the file header defines. An absent
`contradicts_record_prose` still means *not judged*, and `false` passes.

**Instruments**

```
ingest.test_fidelity        green; five new refusals, five acceptances (three replace `unread needs nothing else`)
ingest.verify               All integrity checks passed, on the live sidecar
node ui/check_ui.mjs        all checks passed (untouched; confirmed)
mutate_fidelity coverage    no guard in no list, no stale name
mutate_fidelity MUTATIONS   84 -> 89, EXPECTED in lockstep
UNMUTATED_AND_OWED          3, unchanged. None of the five refusals joined it
rights mutations            15 of 15 verified, sources restored byte-identical
```

**How the mutations were run, since FINDING 59 says host only.** Not in the
working tree. The harness was driven from a scratch copy outside the connected
folder, restricted to the rights block (the ten F6 mutations and the five new
ones), with the coverage check run separately against the real tree's green suite.
No live mutation was ever in the repository. **The full 89-mutation run on the
host is still the canonical number** and is in the runbook below; the other 74
mutate code this block did not touch.

**The sidecar header was corrected in the same change.** `why_unread_carries_a_reason`
said *"NOTE THAT NOTHING CHECKS THIS FIELD … A guard is owed."* — true yesterday,
false the moment the guard exists. It now says what guards it and from when. No
cell was touched.

---

## 3. D — Old Tamil on the stronger tier. **CLOSED FROM THE ARCHIVE. NO CALL SPENT**

**The start document's premise was wrong.** It said `chat-strong` "has never been
run" and quoted `gateway/config.yaml` saying so. That comment was written on
2026-08-16 *before* the run it was written to enable, and the run happened the
same day: `--only-lang oty --attempt-all --model chat-strong`. RULING 23a records
it, and C2_RESULT.md §23a says the file's selection regime is uneven because of it.

**What the frozen file holds, read attempt by attempt:**

```
Old Tamil rows                         29
  chat-default attempts admitted       12 of 29   (17 held)
  chat-strong  attempts admitted       29 of 29
  row text now read from chat-strong   17
every other language                   one draw, chat-default, all admitted
```

**So, for the Methodology Final thread, which writes §8:**

- **Query rendering:** "Old Tamil fails" is true of `claude-haiku-4-5` and
  **false of `claude-sonnet-5`**, which rendered every Old Tamil query in the right
  script. At this stage the failure is a model-tier result, and §8 must say which
  tier or stop calling it the worst case.
- **Retrieval** (cosine 0.368 against 0.61–0.68) is the embedding model. No chat
  tier touches it; that claim stands as measured.
- **Translation** (one valid round trip in three) was Part 6, on `chat-default`.
  Untested on the stronger tier; §8 should name the tier.
- **Any per-language rendering number** has to carry RULING 23a's caveat.

**Why the start document's command was not run.** Two reasons, either sufficient:

1. **It writes the frozen file.** `--attempt-all` without `--out` appends to
   `eval/gold/query_renderings.json`, whose hash every ranking run records
   (ruling 19). The start document's command has no `--out`.
2. **It cannot measure anything for the other six.** They are already admitted
   at the guard's ceiling on chat-default, and four of them are romanised, where
   the guard is a null check (C2 rendering review, hole 1). A second draw on
   Sonnet could not move a verdict.

`gateway/config.yaml` now carries a comment saying the Old Tamil comparison was
made, where the evidence is, and that `--attempt-all` needs `--out`. Comment
only; `chat-default` is not repointed and the YAML parses to the same model list.

**P6** names the §8 sentence as a candidate for a claim with no check behind it.
It is scored in Methodology Final, unamended; this section is the evidence that
thread reads.

---

## 4. Host runbook — two commits, then the full harness

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
.venv\Scripts\Activate.ps1
git status --short
```

**Expect exactly these six paths and nothing else:**

```
 M data/corpus_rights.json
 M gateway/config.yaml
 M ingest/fidelity.py
 M ingest/test_fidelity.py
 M scripts/mutate_fidelity.py
?? UI_LOOSE_ENDS_RESULT.md
```

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
python scripts\mutate_fidelity.py
```

**Expect** `all 89 mutations verified`, 3 unmutated-and-owed, no COVERAGE line,
and `git diff --stat` unchanged afterwards (no file whose every line changed).

```powershell
cd "C:\Users\chemi\Documents\Claude\Museums Project Number 1\mundus-ulterior"
git add data/corpus_rights.json ingest/fidelity.py ingest/test_fidelity.py scripts/mutate_fidelity.py
git commit -F commit-loose-ends-c.txt
git add gateway/config.yaml UI_LOOSE_ENDS_RESULT.md
git commit -F commit-loose-ends-result.txt
git status --short
git log --oneline -3
```

**`git status --short` must print nothing.** FINDING 116.

---

## 5. What this block leaves open

Nothing of its own. Handed forward by Amendment 1, not by this block: A, B and F
to Methodology Final; the Lovable port held.
