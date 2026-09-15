# UI LOOSE ENDS START — **EVERYTHING THE METHODOLOGY BLOCK ACCUMULATED AND DID NOT
# FINISH, NAMED IN ONE PLACE SO IT STOPS BEING CARRIED IN PEOPLE'S HEADS.**
#
# **Scoped 2026-09-15 by Rob, who took the Methodology build thread down to text and
# page design only. This is the other half. It is not a tidy-up: two items on it are
# known defects shipping in prose, and one of them is drawn rather than written, which
# is the easy way to miss it.**

*This document assigns nothing new. Every item below was already owed by an earlier
block and is recorded here with the evidence that established it, so no item has to be
re-derived before it can be worked.*

---

# 1. THE ITEMS, AND THEY ARE NOT ONE KIND OF JOB

```
A  the port sweep                      prose that is false of the Lovable port        P5
B  the figures' port-false wording     the same defect, drawn                         —
C  the owed corpus_rights.json guards  two declared fields nothing validates          —
D  the Old Tamil model question        a claim in §8 resting on one untested tier     —
E  repo hygiene                        three commits whose status nobody can read     —
F  the question box / chat search      RULING 83, its own block, sequenced last       —
```

**A and B are the same defect and must be worked together.** C is a guard. D is a
measurement. E is a verification. F is a block in its own right and is on this list only
so that it is not mistaken for forgotten.

---

# 2. **A — THE PORT SWEEP.** The whole Methodology draft describes a file the site is not

The copy was written describing `ui/index.html` opened from disk. The portal is being
ported to Lovable (`UI_DESIGN_START_AMENDMENT_1.md`, which also fixes the sequence:
design locally → port → chat search → §8 ruling → GitHub decisions).

**Three statements are already known false of the port:**

```
§5   "the checks run against the site"
§7   "one HTML file, openable from disk"
§10  "no framework, no build step"
```

**P5 in `UI_METHODOLOGY_DESIGN_PREDICTIONS.md` predicts a sweep finds at least three
more, and is REFUTED by a sweep that finds two or fewer.** That prediction is scored
here, not in the design thread.

## Why Rob put this here rather than in the text thread

**The sweep cannot close before the port exists.** A statement is marked false against a
port somebody can look at; against a port that has not been built, every finding is
provisional. The design thread would produce a list it could not close. It flags
candidates as it writes and passes them over; this thread owns the sweep and the fixes.

## The one thing that makes this harder than reading ten sections

The false statements are not all of the form "this file". Some are claims about
*behaviour* that the hosting change breaks quietly — what runs at read time, what is
fetched, what a check is actually running against. §5 is the section most exposed and it
is also the section that documents this exact failure mode, which is worth noticing
before writing its replacement.

---

# 3. **B — THE FIGURES SAY IT TOO, AND THEY SAY IT IN PICTURES**

`architecture-detail.html` (the §10 figure) contains three port-false elements:

```
the index.html box      "one hand-written file; no framework or build step"
the zone eyebrow        "Published site — static files, no server, no database"
the caption             "two static files … no server and no database behind it"
```

**The figure and §10's prose assert the same thing, so they change together or not at
all.** A sweep that fixes the prose and leaves the figure produces a page that
contradicts itself in the same section.

## Two mechanical facts before anyone edits it

1. **The figure is generated.** `architecture-detail.build.py` computes every coordinate
   and carries its routing constraints as asserts. **Edit the generator and regenerate**;
   hand-edited numbers in the HTML hold until the next regeneration and no longer.
2. **Re-render and re-check after any text change.** Box text drives nothing
   automatically — a longer label can overflow its chip or collide with a line, and the
   collision check is a script, not a habit. The design thread's own §10 figure passed a
   zero-collision geometric check and still shipped an arrowhead eight pixels from a
   heading, which only the render caught. **Both passes happen.**

The §1 figure (`architecture-figure.html`) is approved and is **not** in this item. Its
claims are about when answers are produced, not about how the site is hosted.

---

# 4. **C — TWO DECLARED FIELDS AND NOTHING VALIDATES EITHER**

The design thread added two fields to `data/corpus_rights.json`:

```
contradicts_record_prose   true on exactly 4 cells — eastasia-04-jingjiao-stele,
                           eastasia-05-liangshu-qin-lun, eastasia-06-cefu-yuangui,
                           eastasia-07-tang-huiyao. Each of those notes opens
                           "THIS CONTRADICTS THE RECORD'S OWN PROSE"
unread_reason              on all 14 unread cells — source_not_established (9),
                           host_refuses (3), archived_capture (2)
```

**`ingest.fidelity.check_rights` returns early on `unread`, so neither field is
checked.** The file's own header keys record both fields and state that a guard is owed;
that is a debt written down, not a guard.

**Why it matters more than it looks.** `unread_reason` is the field that keeps
`states_no_terms` (the object was reached and says nothing) distinct from `unread` (the
object could not be opened). `RIGHTS_VALIDATION_START.md` §4 names collapsing those two
as the most likely way that block ships a lie. An unvalidated field carrying that
distinction is a distinction that can rot without anything going red.

**Sequencing: the blocker is gone.** `RIGHTS_VALIDATION_RESULT.md` closed 2026-09-14 —
24 cells read, confirmed and written, the column at **40 read / 14 unread**. The sidecar
is no longer mid-clearance, so **this guard can be written now**. It still belongs
written against the schema rather than against today's 14 values, so that the next
reading does not turn it red for being correct.

---

# 5. **D — §8 NAMES OLD TAMIL AS THE WORST CASE ON ONE MODEL TIER**

Old Tamil fails at three stages across two vendors: retrieval (cosine 0.368 against
0.61–0.68), translation (one valid round trip in three), and query rendering — **all
sixteen rejected renderings in C2 were Old Tamil**, the model returning Devanagari,
Malayalam, Sinhala or Bengali instead.

**Every one of those 205 renderings was made by `chat-default`, which is
`claude-haiku-4-5`.** `gateway/config.yaml` added `chat-strong` (`claude-sonnet-5`) for
exactly this reason, in its own words: *"That is a statement about one model tier and it
had never been tested against another."*

**It still has not been.** §8 says Old Tamil performs worst; that is true of what was
measured and untested against the stronger tier. **P6 names this sentence as one of
three candidates for a claim that ships with no check behind it.**

```
python scripts/build_query_renderings.py --model chat-strong --attempt-all
```

The config file also records the constraint: **`chat-default` must not be repointed.**
Part 6's translations and Part 7's answers were measured on haiku, and repointing the
alias would silently make every archived number incomparable.
`answer.translate.resolve_model_label` records whichever concrete model answered beside
every rendering, so a run under `chat-strong` stays comparable and a wrong model string
is a failed call rather than a mislabelled rendering.

---

# 6. **E — THREE COMMITS AND NOBODY CAN READ WHETHER THEY LANDED**

```
commit-design-predictions.txt       UI_METHODOLOGY_DESIGN_PREDICTIONS.md
commit-measure-data.txt             ui/measure_data.mjs
commit-rights-validation-start.txt  RIGHTS_VALIDATION_START.md
```

**All three files are present in the working tree**, confirmed over the file bridge on
2026-09-15 at the sizes and times they were handed over, with their `commit-*.txt`
messages beside them. **"Never written" is ruled out. Whether they were committed is
not** — the bridge shell has been dead since the 2026-09-08 Windows update and no
session has read the real log; the design thread's snapshot carried a `.git/logs/HEAD`
from 2026-09-12 whose last entry was `1a53df7`. FINDING 116 — a commit message written
to its own file is not a commit — is already in that log.

**The build thread claims this one as a declared exception** and commits any that are
uncommitted, because RULING 78 makes a missing predictions commit a hard prerequisite it
cannot delegate. **It is listed here so that if the build thread's log check comes back
clean, this item is closed rather than carried.**

---

# 7. **F — THE QUESTION BOX, AND IT IS A BLOCK AND NOT A LOOSE END**

RULING 83: no live generation. The Methodology copy says "type a question" and **there is
no such control on the site.** Rob raised this in the design thread and ruled it a
separate thread.

What the design thread established, so the block does not start from nothing:

- **The cost objection is the real one**, not the confidence one. An earlier framing
  argued that a question outside the test set cannot be scored — Rob rejected it,
  correctly: *"the ultimate use case for this portal is EXACTLY handling questions
  outside of test sets."* The constraints that survive are API cost, rate limits, and
  presentation.
- **Grounding checks already run at generation.** An earlier draft claimed a live answer
  "could not have been checked before you read it" and that is false.
- **Sequence:** `UI_DESIGN_START_AMENDMENT_1.md` puts chat search *after* the Lovable
  port, which means after item A.

---

# 8. ORDERING — **AND TWO OF THESE HAVE HARD PREDECESSORS**

```
E   closed by the build thread's log check, or worked here if it is not
D   independent. Can run any time; one command and a comparison
C   UNBLOCKED — the rights block closed 2026-09-14. Write it to the schema, not to
    today's fourteen values
A   AFTER the Lovable port exists. Provisional before then
B   WITH A, never separately
F   AFTER A
```

**Nothing here blocks the Methodology build thread**, which is the point of the split.
The one shared surface is §10's prose, which the build thread writes and this thread
later corrects — **so this thread reads Rob's shipped §10, not the design draft**, or it
will correct a sentence that no longer exists.

---

# 9. WHAT THIS THREAD MUST NOT DO

- **Not edit the Methodology tab's text or design for any reason other than an item on
  this list.** Two threads editing the same section from different premises is how a
  correction gets reverted by the other one's merge.
- **Not repoint `chat-default`.** Item D says why.
- **Not relax a check to fit a finding.** RULING 88.
- **Not type a count into prose**, in digits or in letters. Guard 2g holds everywhere,
  not only on the tab being built.
- **Not amend `UI_METHODOLOGY_DESIGN_PREDICTIONS.md`.** P5 is scored here; the document
  is not rewritten.
- **Not assign ruling or finding numbers from this document.**

---

# 10. FIRST FIVE MINUTES

```
cd C:\path\to\mundus-ulterior
git log --oneline -8
git status --short
node ui/check_ui.mjs
```

**The bridge shell has been dead since the 2026-09-08 Windows update.**
`device_list_dir`, `device_stage_files` and `device_commit_files` work; there is no git
and no python reachable from the session. **Every command is run by Rob on the host and
pasted back** — and per his standing instruction, every script handed to him arrives with
its directory command attached.

Playwright in the session container needs manual symlinks (1194 against 1243) before a
headless render will run, which item B needs.
