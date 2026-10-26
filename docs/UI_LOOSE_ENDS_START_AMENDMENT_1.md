# UI LOOSE ENDS START — AMENDMENT 1
# **THE LOVABLE PORT IS THE FINAL BLOCK. EVERYTHING ELSE PRECEDES IT.**
#
# **This amends BOTH `UI_LOOSE_ENDS_START.md` AND `UI_METHODOLOGY_BUILD_START.md`.
# Three of the loose-ends items were sequenced behind the port; the port is now last,
# so they could not run where they were put. Two of them leave that thread entirely
# and one is cut.**

*Ruled by Rob 2026-09-15, after both start documents were written and before either
thread opened. The originals are not rewritten — they are scoreable as written, and
this document is what disagrees with them.*

---

# 1. THE RUNNING ORDER

```
1  Loose Ends              next
2  Methodology Final       after it
3  Lovable port            LAST, and nothing follows it
```

**Rob's rule, in his words: anything else that needs work MUST be done before the
port.** That is the constraint every reassignment below follows from.

## What it broke

`UI_LOOSE_ENDS_START.md` §8 sequenced three items *behind* the port:

```
A  the port sweep     AFTER the Lovable port exists. Provisional before then
B  the figures        WITH A, never separately
F  the question box   AFTER A
```

**None of those can run in a thread that precedes the port.** A and B were written on
the assumption that a statement is marked false against a port somebody can look at.
There will be no such port until the last block.

---

# 2. THE REASSIGNMENT

```
item  was                         now
----  --------------------------  --------------------------------------------
A     Loose Ends, after the port  METHODOLOGY FINAL — it is a writing job now
B     Loose Ends, with A          METHODOLOGY FINAL — with A, as before
C     Loose Ends                  LOOSE ENDS, unchanged
D     Loose Ends                  LOOSE ENDS, unchanged
E     Build thread's exception    LOOSE ENDS — it reaches the log first now
F     Loose Ends, after the port  CUT. Not built. §4 below
```

**The Loose Ends thread is now three items: C, D and E.** It is a smaller thread than
its start document describes, and the three it keeps are the three that never depended
on the port.

---

# 3. **A AND B — RULED: SCOPE THE CLAIMS TO THE REFERENCE COPY**

The problem was never the wording. §§5, 7 and 10 say things like *"one HTML file,
openable from disk"* and *"no framework, no build step"*, and the §10 figure draws the
same claim in its `index.html` box, its "Published site" eyebrow and its caption. Each is
true of the version the checks run against and false of a Lovable-hosted site.

**Rob's ruling: keep the precise wording and scope it.** The page says these things about
**the reference copy — the version the checks run against** — and says so plainly.

## Why this and not the alternatives

- **It stays specific.** Rule 2 of the copy standards needs the reader to understand what
  was built; *"no framework, no build step"* is the kind of concrete detail a hedge
  cannot replace.
- **It is true before and after the port.** No sentence goes false the day Lovable goes
  live, so nothing has to be chased afterwards.
- **The tab already documents this exact distinction.** §5's subject is a sentence going
  false while the number beside it stays right, and the checks band in the §10 figure
  already reads *"run against the reference copy, not the published one."* The copy was
  making the distinction in one place and ignoring it in three others.

## What this means in practice

**A and B are one job in the Methodology Final thread, not a sweep in a later one.**
The thread that writes §§5, 7 and 10 scopes them as it writes, and regenerates the §10
figure in the same pass so the drawn claim and the written claim agree.

**P5 moves with the work.** It predicts a sweep finds at least three false statements
beyond the three already named, and is REFUTED by a sweep finding two or fewer. **It is
scored in the Methodology Final thread**, not in Loose Ends and not in the port block.
It has now been assigned twice and this is the assignment that holds.

**Do not regenerate the figure by hand.** `ui/figures/architecture-detail.build.py`
computes every coordinate and carries its routing constraints as asserts; edit the
generator, regenerate, then re-render and re-run the collision check, because a longer
label can overflow a chip or collide with a line and nothing catches that automatically.

---

# 4. **F — CUT. THE PROMISE GOES, THE CONTROL IS NOT BUILT**

The Methodology copy says **"type a question"** and there is no such control on the
site. That is a false statement on the page **today**, not only after the port.

**Rob's ruling: cut the promise.** The question box is not built before the port. The
copy stops claiming a control that does not exist.

**This is a copy change and it belongs to the Methodology Final thread.** It is not a
block, it is a deletion.

## The distinction that thread must not collapse

**Promising a control the site does not have is the defect. Naming a conversational
interface as a future direction is not.** §9 lists it among the ideas for future
development and nothing in this ruling touches that. Cut the sentences that imply a
reader can type a question now; leave §9's forward-looking mention alone unless Rob says
otherwise.

## What is preserved, so the block is not re-derived from nothing later

RULING 83 stands: no live generation. And the design thread established two things that
should survive the cut:

- **The cost objection is the real one** — API cost, rate limits, presentation. An
  earlier framing argued a question outside the test set cannot be scored and Rob
  rejected it, correctly: *"the ultimate use case for this portal is EXACTLY handling
  questions outside of test sets."*
- **Grounding checks already run at generation.** An earlier draft claimed a live answer
  *"could not have been checked before you read it"*, and that is false.

---

# 5. **E — THE COMMIT CHECK MOVES TO LOOSE ENDS**

`UI_METHODOLOGY_BUILD_START.md` §1 claims the commit check as a declared exception, on
the grounds that RULING 78 makes a missing predictions commit a hard prerequisite the
build thread cannot delegate to a *parallel* thread.

**The threads are no longer parallel.** Loose Ends runs first and reaches the log first.

**So: Loose Ends runs `git log --oneline -8`, and commits any of the three handovers
that are uncommitted.** The build document's declared exception is withdrawn by this
amendment. Leaving it in place means both threads believe they own the same check, which
is how it gets done twice or not at all.

```
commit-design-predictions.txt       UI_METHODOLOGY_DESIGN_PREDICTIONS.md
commit-measure-data.txt             ui/measure_data.mjs
commit-rights-validation-start.txt  RIGHTS_VALIDATION_START.md
```

All three files are present in the working tree, confirmed over the file bridge
2026-09-15. **Whether they were committed is the open question, and FINDING 116 is why
the distinction is kept rather than collapsed.**

---

# 6. WHAT THIS AMENDMENT DOES NOT DO

- **It does not create a start document for the Lovable port**, and nothing in this
  thread prepares one. **Rob has ordered an explicit hold: no work on the port, of any
  kind, until he says so.**
- **It does not rewrite either start document.** They are scoreable as written. This is
  the document that disagrees with them, and a reader of either should be pointed here.
- **It does not change the six rights slots ruling.** They stay in the Methodology Final
  thread, as ruled 2026-09-15.
- **It does not assign ruling or finding numbers.**
- **It does not reopen P1 through P4 or P6.** Those are scored in the Methodology Final
  thread against `UI_METHODOLOGY_DESIGN_PREDICTIONS.md`, unamended.

---

# 7. THE THREADS AS THEY NOW STAND

```
LOOSE ENDS          C   the two declared fields in data/corpus_rights.json that
(next)                  nothing validates. Unblocked — the rights block closed
                        2026-09-14. Write it to the schema, not to today's values
                    D   §8's Old Tamil claim rests on 205 renderings all made by
                        chat-default. chat-strong exists for exactly that comparison
                        and has never been run. Do not repoint chat-default
                    E   the commit check, moved here by §5 above

METHODOLOGY FINAL   the tab: text and page design, per UI_METHODOLOGY_BUILD_START.md
(after it)          + the six rights slots, and RIGHTS_FOR_METHODOLOGY_SECTION2.md as
                      required reading for §2
                    + A and B — scope the hosting claims to the reference copy, in
                      prose and in the §10 figure, in one pass. P5 scored here
                    + F — cut "type a question" from the copy

LOVABLE PORT        LAST. Held pending Rob's explicit order. Nothing prepares it.
```
