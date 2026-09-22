# DEPLOY START — THE LAST BLOCK, AND IT IS NOT THE LOVABLE PORT

*Written 2026-09-22, at `5863383`, 63 checks green, tree clean. Nothing here is
measured: it is a scope and an order of work, assembled from
`UI_DESIGN_START_AMENDMENT_1.md`, `UI_LOOSE_ENDS_START_AMENDMENT_1.md`,
`UI_METHODOLOGY_FINAL_RESULT.md` and the state of the repository today. The
first thing the deploy thread does is confirm the harness still reproduces — if
it does not, stop and find out what moved.*

---

# 1. THE PORT BECAME A DEPLOY, AND THAT IS A RULING

`UI_LOOSE_ENDS_START_AMENDMENT_1.md` says: **"LOVABLE PORT — LAST. Held pending
Rob's explicit order. Nothing prepares it."** The order came on 2026-09-22, and
it came with a change of shape.

**Rob's requirement, stated:** a version that can be shared and run online,
depending on no file on his machine. **Rob's ruling, stated:** he does not
intend to keep editing in Lovable.

Those two facts together dissolve the port. The page is ALREADY what the
requirement asks for, and this is checkable rather than asserted:

```
everything ui/index.html loads          src="data.js"
                                        src="banner/<code>.png"   (9 images)
external hosts loaded                   none
absolute or machine paths loaded        none
the deployable artifact                 11 files, 9.9 MB
```

**So the final block publishes the files that already exist.** Lovable's one
advantage over a static host was conversational editing of the UI, and that is
the thing Rob has ruled out. What remained would have been pure cost: every view
function rewritten, the public artifact moved outside the harness, and the
`data.js` contract re-established by hand.

**THIS IS THE RARE CASE WHERE THE SCOPE GOT SMALLER ON INSPECTION.** Record it
as that. The project spent several blocks scoping prose around a port that, on
the day it was ordered, turned out not to be needed — and `UI_DESIGN_START_
AMENDMENT_1.md`'s sequencing work was not wasted, because the A/B "reference
copy" scoping it forced into the copy is what makes this deploy honest: the
version the checks run against IS the version being published.

## What this changes about the harness: nothing

The 63 checks execute the page's own functions. That is only possible because
the page is a set of plain functions in one file. A React rebuild would have
ended that, and the block would have had to choose between rewriting the
harness on Playwright and publishing outside it. **The deployed artifact is the
checked artifact.** No new check is needed to establish parity, because there
are not two things.

---

# 2. THE ONE IRREVERSIBLE STEP, AND IT COMES FIRST

**RULED 2026-09-22: the 14 outstanding reuse terms are read BEFORE a public URL
exists.**

A public URL serving `data.js` publishes every record's full text. **Repo
visibility is a side issue and must not be mistaken for the decision** — a
private repository serving a public site puts the same text on the open web.
`UI_DESIGN_START_AMENDMENT_1.md` already separated these two questions and the
separation holds: *"A decision to open the source code is not a decision to open
the corpus."* This block adds the sharper version: **a decision to publish the
SITE is a decision to open the corpus, whatever the repo does.**

What is outstanding, from the rights validation block:

- **14 sources have no terms read**, and the rights column is counted, never
  gated — nothing excludes a source on rights today
- **2 PHI records (`africa-04`, `africa-05`) sit under "personal study only"
  terms that were flagged and never decided.** A public portfolio site is not
  personal study. This needs a ruling, not a reading
- **7 cells take the "states no terms" route** allowed by RULING 74

**The machinery exists.** `RIGHTS_VALIDATION_RUNBOOK.md` and
`RIGHTS_VALIDATION_READINGS.md` are the shape; 14 is a bounded job.

**Methodology §2 already discloses the position** — *"Terms are recorded and
counted; they are not yet used to exclude a source."* That sentence is honest
today and becomes a much louder admission the moment the site is public. If the
readings change the position, §2 changes with them.

---

# 3. THE OPEN DECISION THIS DOCUMENT DOES NOT TAKE

**Does the record pass, S9–S18, land before or after the deploy?** Put to Rob
on 2026-09-22 and not answered; the conversation moved.

```
BEFORE   S9 alone puts "Nabataean Aramaic" on the Safaitic record, and it
         reaches Home's language list and the retrieval table from there.
         Deploying first publishes a known-wrong label to a shareable,
         indexable URL and changes fingerprints underneath it afterwards
AFTER    the deploy is purely mechanical and no data moves until it is done.
         The URL arrives sooner; the record pass then absorbs a live site
```

**Recommendation: BEFORE.** S9 through S18 are wrong today, several of them
visibly (a record claiming to be the first of something it is not; "four hundred
years" where it is three). They are also the last things in the project that are
known-wrong and unfixed. Publishing them is the one move that makes an error
harder to retract rather than easier.

**This is Rob's call and the deploy thread must not assume it.**

---

# 4. WHAT THE DEPLOY IS, MECHANICALLY

```
the artifact      ui/index.html, ui/data.js, ui/banner/*.png     11 files, 9.9 MB
the build         build_ui_data.py -> data.js                    run locally, before deploy
                  build_banner.mjs -> banner/*.png               run locally, before deploy
the host          a static host. GitHub Pages, Netlify or Cloudflare Pages
compression       gzip/Brotli at the host, automatic on all three.
                  data.js is JSON-ish text and should compress hard
```

**BUNDLE SIZE IS NOTED AND NOT ADDRESSED.** 9.9 MB is slow on a phone and works.
Splitting it changes the page's "loads nothing from outside" claim into "fetches
its own data" and several guards read the whole bundle. **That is its own block,
with its own predictions, if it is ever wanted.** Compression is free and
changes no claim.

**A domain is a decision this block should surface rather than default.**
`productofrob.com` is the portfolio this project was built for, and a subdomain
of it is the obvious home. A host's default subdomain is also a real answer.
Either way it should be chosen, not accepted.

---

# 5. WHAT THIS BLOCK DOES NOT DO

- **No chat search.** RULING 83 put it after the port, and §9 of the Methodology
  copy already describes it as out of scope with the reason
- **No bundle splitting.** §4 above
- **No rebuild, in Lovable or anything else.** §1 above
- **No new claims in the copy.** If the rights readings change §2's position,
  that is a correction to an existing sentence, not new prose
- **No harness rewrite.** There is nothing to establish parity with

---

# 6. WHAT THE THREAD PREDICTS BEFORE IT TOUCHES ANYTHING

Per RULING 78, predictions are committed before any code is edited and scored
afterwards without amendment. At least these, and one written not to flatter:

- **P1** — how many of the 14 terms readings come back permissive enough to
  publish unchanged, and how many force a record to change or leave
- **P2** — whether `data.js` compresses below 2 MB over the wire
- **P3** — whether the deployed site renders identically to the local file.
  It should; the interesting prediction is the specific way it will not
  (relative paths, MIME type on `.js`, case-sensitive filenames on a Linux host
  where the local filesystem was not)
- **P4** — whether any guard in the harness turns out to depend on the file
  being opened from disk rather than served over HTTP

---

# 7. STATE AT HANDOFF

```
HEAD                    5863383  Home and Questions stop reading as narrow columns
harness                 63 checks, green
tree                    clean
next free ruling        98
next free finding       123
```

**RULING 97 IS NOT IN `RULINGS.md` YET.** It was taken on 2026-09-22 — languages
a record references rather than holds, which is how Danish, French and
Vietnamese left Home's language sentence — and it is recorded in
`ui/index.html` beside `LANG_REFERENCED_NOT_HELD` and in `commit-home-text.txt`.
`RULINGS.md` already does not index 53–79; this is one more, and the deploy
thread should not inherit the habit.

## Debts carried in, none of them blocking the deploy

- **FINDING (unnumbered, next free is 123): 635 of 1227 "resolved" spans do not
  hold their quote exactly.** 610 record an end offset one or two characters
  short, almost always a closing bracket or comma. The corpus-wide check
  compares with `includes` in either direction and cannot see it; the chain
  figure's guard compares exactly and found it the moment the example moved.
  **It bears directly on Home's own claim — "almost every click lands on the
  exact characters."** The 25 spans that are not a simple 1–2 character
  shortfall are a separate shape and uncharacterised
- **The Questions tab still says "every quotation resolves to the specific
  characters in a field."** Home now says "almost every ... and the few that
  don't are shown with the reason", and Methodology says "Almost every". The
  three tabs disagree. This is S5, on a tab the S1–S8 pass did not reach
- **S4 is half-closed.** The language list is derived, so it still carries the
  `xna` mapping the record pass owns, and Korean and Latin still reach the
  sentence through catalogue text
- **`measure_data.mjs` cannot run on the device VM** — Playwright is not
  installed there, and the P1 layout figures in
  `UI_METHODOLOGY_FINAL_RESULT.md` are now stale, because Home's cards and the
  Questions intro both changed width after they were taken

---

# 8. THE FIRST FIVE MINUTES

1. `node ui/check_ui.mjs` — 63 green, or stop
2. `git log --oneline -3` — `5863383` on top
3. Open `ui/index.html` from disk at 1600px and at 390px and LOOK at it, before
   changing anything. `UI_DESIGN_START.md` §7 has said this for every block and
   it has been right every time
4. Read `RIGHTS_VALIDATION_RESULT.md` and `RIGHTS_VALIDATION_RULINGS.md` before
   reading a single source's terms
5. Write the predictions document and commit it before editing anything
