# UI METHODOLOGY BUILD START — **THE COPY IS WRITTEN AND NOT ONE LINE OF IT IS IN
# `ui/index.html`. THIS THREAD BUILDS THE METHODOLOGY TAB AND NOTHING ELSE.**
#
# **Scoped 2026-09-15 by Rob: text and page design only. Everything else this block
# accumulated — the port sweep, the owed rights guards, the question box — moves to
# `UI_LOOSE_ENDS_START.md` and is named there rather than left implied here.**

*Scored against `UI_METHODOLOGY_DESIGN_PREDICTIONS.md`, which was committed before any
of this work and is **not amended** — this thread scores it, it does not rewrite it.*

---

# 1. THE SCOPE LINE, AND THE ONE EXCEPTION TO IT

## In scope

**The Methodology tab's text and its page design.** The ten sections, their evidence
panels, the section nav, the two architecture figures, the six derived slots in §2, the
guards that read the surfaces being edited, and the length measurement at both widths.

## Out of scope, and it belongs to `UI_LOOSE_ENDS_START.md`

```
the port sweep                      P5, and it cannot close before the port exists
the figures' port-false wording     the same defect, drawn rather than written
the owed corpus_rights.json guards  contradicts_record_prose, unread_reason
the question box / chat search      RULING 83, its own block
the Old Tamil model question        whether chat-strong beat chat-default
```

**If this thread finds one of those, it writes it down and does not fix it.** Two
threads editing the same sentence from different premises is how a correction gets
reverted by the other one's merge.

## The one declared exception: **the commit check**

Three commits were handed over by the design thread:

```
commit-design-predictions.txt       UI_METHODOLOGY_DESIGN_PREDICTIONS.md
commit-measure-data.txt             ui/measure_data.mjs
commit-rights-validation-start.txt  RIGHTS_VALIDATION_START.md
```

**All three files are present in the working tree**, confirmed over the file bridge on
2026-09-15 at the sizes and times they were handed over, with their `commit-*.txt`
messages beside them. **What is still unknown is whether they were committed.** The
bridge shell has been dead since the 2026-09-08 Windows update, so no session has read
the real log; the design thread's staged snapshot carried a `.git/logs/HEAD` from
2026-09-12 whose last entry was `1a53df7`. FINDING 116 — a commit message written to its
own file is not a commit — is already in that log.

**This thread runs the check itself and makes any of the three that are uncommitted**,
even though two are not its subject. The reason is RULING 78: the predictions document
must be committed before the code it predicts, so a missing predictions commit is a hard
prerequisite this thread cannot delegate to a parallel thread — and once the log is
open, the other two cost one command each. **Declared here so it is not a surprise at
the close.**

```
cd C:\path\to\mundus-ulterior
git log --oneline -8
git status --short
```

---

# 2. THE COPY — **ROB'S VERSION IS THE ONE THAT SHIPS, NOT MINE**

`METHODOLOGY_COPY_DRAFT.md` in the working directory is **not authoritative.** Rob has
been revising in his own copy since the §2 rewrite, and two cuts are known to have been
made there and never applied here:

- the register passage in §5 ("The register records its own gaps…"), cut by Rob
- the fourth practice in §5's practices list, cut by Rob

There will be more. **Take Rob's file as the source and treat the draft here as a
reference for the material only** — the evidence panels, the derived slots, the section
ordering. Where the two disagree about wording, Rob's wins without discussion.

## The five standing rules the copy was written under

Set by Rob across the design thread. They govern every edit this thread makes to prose,
including anything it adds — a caption, an empty state, a panel summary.

1. **Tone matches productofrob.com.**
2. **General-interest audience, assuming ZERO prior project knowledge.** Every internal
   reference removed or explained.
3. **Each section as concise as possible.** Extended technical explanations out of scope.
4. **Procedural and matter-of-fact, NOT narrative.** No amusing language, no colourful
   anecdotes. Justifications only where they are needed.
5. **Ask for a ruling when unsure rather than creating.**

Rule 4 arrived late and §§3–8 and §10 were rewritten to meet it.

## The shape

```
4,625 words        ten sections, ten collapsed evidence panels
§1                 intro, architecture figure immediately below the heading
§2                 source compilation — opening is Rob's own text
§7                 STUB. Rob's to fill, or a placeholder he will ship
§10                tooling, and the detail figure belongs to it
```

---

# 3. THE SIX RIGHTS SLOTS — **IN SCOPE, BY RULING, AND THE TRAP IS IN THE NOTATION**

`ui/build_ui_data.py` does not read `data/corpus_rights.json`. Until it does, six slots
in §2 have nothing behind them. **Rob ruled on 2026-09-15 that this thread makes that
extension**, as a declared dependency rather than a scope creep: §2 is the strongest
material in the first half of the page, and a tab carrying six visible gaps cannot be
reviewed at either width — which is the condition the block does not close without.

```
{{derived: total sources}}                                 expected 54
{{derived: sources with a reuse reading}}                  expected 40
{{derived: distinct hosts read}}                           expected 26
{{derived: readings made by two readers}}                  expected 25
{{derived: unread sources}}                                expected 14
{{derived: records whose licence claim was contradicted}}  expected  4
```

**P4 predicts this is one commit, adds no guard failure, and resolves to exactly those
six values.** REFUTED by any of the six differing, by the extension needing more than
one commit, or by it turning an existing check red.

## The trap

**The draft writes those slots with their values inside the slot name** —
`{{derived: total sources = 54}}`. That was an annotation for reading the draft. If the
` = 54` survives into markup, **guard 2g goes red and P3 is refuted by a count that was
never meant to ship.** Strip the `= N` from all six.

## What this thread does NOT touch in the same file

`data/corpus_rights.json` gained `contradicts_record_prose` and `unread_reason` in the
design thread, and **neither field is validated** — `ingest.fidelity.check_rights`
returns early on `unread`. The file's own header keys say a guard is owed. **That guard
belongs to the loose-ends thread.** Reading the sidecar and validating it are different
jobs and this one only reads.

## **§2 DOES NOT MOVE UNDER THIS THREAD'S FEET — THE RIGHTS BLOCK HAS CLOSED**

The design thread wrote as though the rights backlog were still being cleared. **It is
not.** `RIGHTS_VALIDATION_RESULT.md` closed 2026-09-14: 24 cells read, confirmed and
written, all signed `curator_and_model`, the column now **40 read / 14 unread with every
one of the fourteen named.** The six values above are post-close and are the values §2
describes.

## **REQUIRED READING FOR §2, AND IT IS NOT THE DRAFT**

```
RIGHTS_FOR_METHODOLOGY_SECTION2.md
```

The rights block wrote it *for this thread*. Every figure in it was computed
2026-09-14 from a clean tree at `219c8a5` with `python -m ingest.verify` green, and §6
names each figure's provenance **so this thread recomputes rather than quotes on trust.**
It is explicitly not copy and nothing in it is committed to `ui/`.

Also in it: the corpus in figures — 54 records, **170 chunks**, 33 parallel pairs, 49
non-English retrieval-eligible chunks across 14 language codes, the tier and placement
breakdowns, and a region table separating a region *speaking* from a region *spoken
about*.

**One figure to reconcile before using either.** The design draft's §§8–9 describe the
index growing "450 → 561 chunks"; this document says 170. They may be different units —
index entries against source chunks — or one may be stale. **Establish which before a
chunk figure goes on the page**, and do not put either number in prose: guard 2g.

---

# 4. THE TWO FIGURES

```
architecture-figure.html   §1, viewBox 1000×336, APPROVED by Rob
architecture-detail.html   §10, viewBox 1240×680, BUILT, NOT APPROVED
architecture-detail.build.py   the generator that emits the §10 figure
```

Also delivered as images for the portfolio writeup rather than the page:
`architecture-figure.png` (3×, light), `architecture-figure-dark.png`,
`architecture-figure.svg` (standalone, light-scheme colours baked in). **The image
versions cannot follow the dark scheme**; the HTML versions read the page tokens and do.

## Three mechanical facts that will break the page if they are missed

1. **CSS order.** The §1 file's `<style>` defines the shared `.archfig` rules; the §10
   file's `<style>` defines only what it adds (`.af-chip`, `.af-mono`, `.af-chip-title`,
   and a wider `min-width`). **Paste §1's block first.** §10's alone renders unstyled.
2. **Marker ids differ on purpose** — `af-arrow` and `ad-arrow`. An SVG marker resolves
   by id across the whole document, so two figures sharing an id means one steals the
   other's arrowheads. Do not tidy them to match.
3. **The §10 figure is generated.** `architecture-detail.build.py` computes every
   coordinate and carries its routing constraints as asserts. Hand-editing the numbers
   in the HTML holds until the next regeneration and no longer.

## The §10 figure carries port-false wording, and this thread leaves it alone

Its `index.html` box, its "Published site" eyebrow and its caption all describe a
hand-written file with no server and no build step. True of the reference copy, false of
the Lovable port. **That is the loose-ends thread's, together with §10's prose, because
the figure and the prose say the same thing and must change together.**

## What the figures cost in page height — **measured**

```
§1  figure    404px at 390px wide
§10 figure    690px at 390px wide, 927px in a 1568px column
```

`UI_METHODOLOGY_DESIGN_PREDICTIONS.md` §1 estimated the rebuilt tab at **9,741 /
14,356** with *one* figure at its drawn height. **The §10 figure did not exist when that
estimate was made and is not in it.** Adding its measured phone height gives a revised
estimate of about **15,050 at 390px** — still inside P1's 13,000–16,000 range and far
above the 12,000 refutation floor, but headroom to the top of the range drops from
1,644px to about 950px. **P1 is not amended. The result document records that the
estimate under-counted by one figure.**

The §10 figure holds at a 1,100px `min-width` and scrolls sideways on a phone, where a
reader sees roughly a third of it at a time. Same trade-off Rob accepted for the §1
figure, at twice the height, and a fair charge against the block's length claim.

---

# 5. THE GUARDS

P2 predicts the first render:

```
53  geography ledger figures re-derived     STAYS GREEN, unmodified
58  withheld failures named, Home agrees    RED, expected — Home clause deleted by
                                            ruling, the naming half stays
59  partial-archive figures + the label     RED on first render, green once re-homed
60  closing paragraph derives its figures   RED on first render, same reason
2g  no count written down                   NEVER RED
49  panel empty state declares its kinds    STAYS GREEN
61  every kind round-trips the address bar  STAYS GREEN
```

**REFUTED** by 2g going red at any point, by 53 needing modification, or by 49 or 61
moving. **The harness ends at 61 checks or higher, never lower.**

**RULING 88: do not relax a check to fit the design.** Three guards go red by
prediction. They go green by re-homing the content they read, never by re-pointing them
at a weaker claim.

---

# 6. WHAT THIS THREAD MUST NOT DO

- **Not type a count into prose**, in digits or in letters. Guard 2g, P3.
- **Not relax a check to fit the design**, and not re-point one at a weaker claim.
- **Not delete evidence.** The card prose is retired; its derived figures move into the
  collapsed panels.
- **Not author a coordinate**, and not hand-edit `ui/data.js`.
- **Not run the port sweep or fix a port-false statement.** Loose-ends thread. Write
  candidates down and pass them over.
- **Not build the chatbot or the question box.** RULING 83, its own block.
- **Not write the owed guards on `corpus_rights.json`'s declared fields.**
- **Not amend `UI_METHODOLOGY_DESIGN_PREDICTIONS.md`.** Score it.
- **Not assign ruling or finding numbers from this document.**
- **Not edit Home beyond the one declared sentence.** §4 of the predictions document
  promises exactly one sentence and one guard clause, and the regions block was scored
  REFUTED for taking a neighbouring tab at Rob's instruction. Anything beyond that
  refutes that paragraph.

---

# 7. THE RULINGS STILL OPEN

1. **§7 "Creating the portal" is a stub.** Rob's to fill, or a placeholder he is happy
   to ship. Nothing else in the block can close around an empty section.
2. **Does the §10 figure ship at all?** Built and collision-checked; not approved.
3. **Does the zero-suppression rule cover all five citation-outcome bullets or only
   `absent`?** Rob ruled `{{derived: absent quotation count}}` is suppressed at zero.
   Whether that extends to the other four was never settled. **Get the ruling before
   building the suppression**, not after.
4. **Two figures on one tab.** The §10 figure restates the §1 figure's pipeline in
   detail. §6 of the predictions document already names *"the architecture figure says
   the same thing as the paragraph beneath it"* as a likely finding; with two figures
   the question is sharper. Rob's call, not a defect.

---

# 8. FIRST FIVE MINUTES — **AND THE ENVIRONMENT HAS NOT IMPROVED**

```
cd C:\path\to\mundus-ulterior
git log --oneline -8
git status --short
node ui/check_ui.mjs
node ui/measure_data.mjs
```

The last command is the baseline this block is scored against. It must reproduce
**10161 at 1600px and 17970 at 390px** before any edit. **If it does not, the baseline
moved for a reason nobody recorded, and that is the finding** — not a number to quietly
adopt.

**The bridge shell has been dead since the 2026-09-08 Windows update.** `device_list_dir`,
`device_stage_files` and `device_commit_files` work; there is no git and no python
reachable from the session. **Every command above is run by Rob on the host and pasted
back** — and per his standing instruction, every script handed to him arrives with its
directory command attached.

Playwright in the session container needs manual symlinks (1194 against 1243) before a
headless render will run.

---

# 9. THREE THINGS WORTH CARRYING IN

**The instrument has no taste.** `ui/measure_data.mjs`'s own header says it: *"The
instrument is very good at saying a number moved and has no opinion about whether the
page is better."* The design thread's §10 figure passed a zero-collision geometric check
and still had an arrow whose head cleared a heading by eight pixels. The check found the
collision that mattered; the render found the one that only looked wrong. **Both passes
happen.**

**A sentence goes false while the number beside it stays right.** This is the tab's own
§5 subject and the design thread committed it twice: §8's "most sources' reuse terms
have not been re-read" was made false by the rights work, and §4's cut was approved and
then not applied for several turns. **P6 predicts at least one such sentence ships** and
names three candidates in advance so they cannot be claimed afterwards.

**The block does not close until Rob has used the tab at both widths.** §6 of the
predictions document is unscored on purpose and nothing in a result document can score
it. Its named candidates: that the collapsed evidence is never opened and the disclosure
has solved the length by hiding the strongest material on the page; that ten sections in
a sticky nav is more navigation than a single tab wants; and that the architecture figure
says the same thing as the first paragraph beneath it.
