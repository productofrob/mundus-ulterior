# UI DESIGN START — AMENDMENT 1. **THE DESIGN BLOCK IS NOW DESIGNING SOMETHING
# THAT WILL BE PORTED, AND THAT CHANGES WHAT GOOD LOOKS LIKE.**

*Written 2026-09-07, after `UI_DESIGN_START.md` and before the design block
opens. `UI_DESIGN_START.md` is **correct as written** and is not edited — its
§4 guards, §5 arguments and §6 measurements all still hold, because the design
work happens on `ui/index.html` where all 39 checks run. This amendment adds
what that document could not know: **where the page goes afterwards.***

---

# 1. THE SEQUENCE, DECIDED 2026-09-07

```
1  DESIGN, LOCALLY, on ui/index.html          <- the block UI_DESIGN_START.md scopes
2  PORT the settled design to Lovable         <- a shareable, interactive URL
3  CHAT SEARCH                                <- ruling 83's question box
4  THE section 8 RULING                       <- W3_DECLARE_DONT_INFER.md section 8
5  GITHUB / SHARING DECISIONS
```

**Two decisions were taken with it, and both were taken on the reasoning below
rather than on convenience.**

**Design locally first, then port.** Designing and re-platforming at the same
time means doing both with no guards running on either, and this project has now
been saved twice by a check or by looking — the inside-out coastline and every
citation marker on the page being broken HTML. **The port becomes a translation
job with a known-good target instead of a rebuild.**

**The Lovable app reads the SAME generated `ui/data.js` and asserts
`ui/data.manifest.json` against it at build time.** The data path is therefore
verified from the day the shareable version exists — including the staleness
check that already caught a bundle built four hours behind the archive
(`check_ui.mjs` §0). **The render guards are ported in a following pass, and
until they are, the port block says so rather than implying the shipped page is
as checked as the local one.**

---

# 2. WHAT "WILL BE PORTED" CHANGES FOR THE DESIGN BLOCK

**Nothing in `UI_DESIGN_START.md` §3's scope shrinks.** All four kinds of change
are still in. What changes is **where the design should live in the file**, and
it is worth an explicit instruction because the current page gets it wrong.

## A DESIGN IN CSS CUSTOM PROPERTIES PORTS AS A FILE. A DESIGN IN INLINE `style=` PORTS AS A REWRITE.

The page today generates all its markup as template strings inside one function
per view, and **several `<h2>` elements carry a repeated inline
`style="font-family:system-ui,sans-serif;font-size:11px;text-transform:uppercase;letter-spacing:.11em;color:var(--ink-faint)"`.**
`UI_DESIGN_START.md` §6 called that the clearest sign nobody has built a type
scale. **Under a port it stops being untidy and becomes expensive:** a React
component tree re-implements every template string, so anything expressed in the
markup is retyped by hand, and anything expressed in `:root` custom properties
and class rules is copied across as a stylesheet.

```
PORTS VERBATIM        :root custom properties, class rules, media queries,
                      a type scale, spacing tokens, the whole cascade

PORTS BY HAND         inline style= attributes, template-string markup,
                      anything computed in JS that could have been a class
```

**So: every value the design block introduces goes in `:root` and gets a name.**
Not because it is tidier — because it is the difference between the port being a
stylesheet copy and the port being a second design pass with a second set of
judgement calls in it.

## THE PAGE HAS NO LOADING STATE, AND IT IS ABOUT TO NEED ONE

`ui/data.js` is **9.5MB on one line**, loaded by a synchronous `<script src>`.
From `file://` that is instant and the page has never needed to think about it.
**Served over HTTP it is a 9.5MB download before first paint**, and the design
block is the one that should decide what a visitor sees during it — because the
port block will otherwise invent something at three in the morning.

**This is a design question, not a plumbing one.** A page whose claim is that
every quotation resolves to characters on disk has an honest and rather good
answer available to it: say what is loading and how big the evidence is. That is
a better first impression than a spinner.

## DEEP LINKS: BUILD THEM NOW, IN THE DESIGN BLOCK

`UI_DESIGN_START.md` §6 records that the page has no URL state at all — nothing
on it can be linked to, on a page whose claim is *"click any highlighted phrase
and see the characters on disk"*. **Do it in the design block, with
`location.hash`.** `state` already holds exactly the four fields it needs
(`view`, `question`, `runIndex`, `selection`).

**Doing it now rather than in the port is the cheap order.** A hash scheme
designed against the local page ports straight onto a router; a router invented
during the port produces URLs nobody chose, and they are permanent the moment
one is shared.

## WHAT NOT TO DO FOR THE PORT'S SAKE

- **Do not split the inline script to make the port easier.** It fails
  `check_ui.mjs`'s first structural check and would leave the design block
  running without a harness — for the port's convenience, at the cost of the
  design block's safety net. The port re-implements the script anyway.
- **Do not restructure the render functions into "component-shaped" ones.**
  That is the port's job, done once, against a settled design. Doing it early
  means doing it twice.
- **Do not drop a card, a list or a gap row to tidy the page.** §4's structural
  guards will catch it, and they are right to.

---

# 3. WHAT THE PORT BLOCK INHERITS, WRITTEN NOW SO IT IS NOT REDERIVED

```
DATA        ui/data.js, generated by `python ui/build_ui_data.py`, never
            hand-edited. 9.5MB, one line, window.MU_DATA
GUARD       ui/data.manifest.json beside it -- counts, both verify axes kept
            separate, per-section sha256, and the sha256 OF data.js ITSELF.
            The port asserts manifest.data_js.sha256 against the bundle it
            ships AT BUILD TIME. That is the whole day-one contract
STALENESS   check_ui.mjs section 0 exists because this file once reported
            "all checks passed" over 61 runs and 139 spans while the archive
            held 77 and 168. A checker that validates whatever it is handed
            will certify a stale artefact without complaint. THE PORT NEEDS
            ITS OWN VERSION OF THIS CHECK
REFERENCE   ui/index.html stays in the repository as the checked reference
            implementation. It is not deleted when Lovable exists
NOT YET     the render guards -- FINDING 98's state table, FINDING 99's
            tag check, the second axis's never-collapse rule, A6's date
            verdicts. Ported in a following pass, and until then the port
            block does not imply the shipped page is as checked as this one
```

---

# 4. TWO THINGS THAT MOVED EARLIER IN THE SEQUENCE AND ARE OPEN

## THE 38 UNREAD RIGHTS POSITIONS. **OPEN, AND IT LANDS AT STEP 2, NOT STEP 5.**

```
rights positions (ruling 74): open_licence_stated 5, permission_stated_no_licence 3,
public_domain 2, all_rights_reserved 2, states_no_terms 1, two_positions_stated 3,
UNREAD 38
```

**`unread` is a state of this project's knowledge and not of the source**, and
counting-not-gating it is the honest position for a file you open by
double-clicking. **A public URL displaying source-text excerpts and published
translations from museums and institutions is a different act**, and 38 of 54
records have a rights position nobody has read.

**FINDING 69 exists because two licence claims were checked and were wrong in
opposite directions in a single session.** That is the reason this is not a
formality: the failure mode is being wrong in the permissive direction on a
public page.

**Not a reason to delay the port.** A reason those 38 are read before the URL is
shared rather than after — and a reason the reading is done by someone reading
each source's terms, not by a matcher over `citation_original`, which would read
the word `open` in a sentence about reachability. That is FINDING 69 with a
regular expression in front of it, and ruling 74 already refuses it.

## LOVABLE IS GITHUB-BACKED BY DEFAULT

Step 5 is *"decisions on sharing source code and data on GitHub"*. **Step 2 may
make part of that decision implicitly**, because Lovable syncs projects to a
GitHub repository. If the sequence is to hold, that repository is created
**private and stays private** until step 5 decides otherwise — deliberately,
rather than by accepting a default.

**And the data question is separate from the code question.** `data/seed_corpus/`
is 54 curated records with rights positions 38 of which are unread; `ui/data.js`
is a derived bundle containing every one of those records' text fields in full.
**A decision to open the source code is not a decision to open the corpus**, and
the two should be taken as two decisions.

---

# 5. WHAT THIS AMENDMENT DOES NOT CHANGE

- `UI_DESIGN_START.md` §4's guard inventory, §5's list of things that look like
  style and are arguments, and §6's measurements. All still exactly right.
- §7's first five minutes, **including step 4** — render the page and look at
  it, at 1600px and at 390px, before changing anything.
- §8's prohibitions. **The design block still does not build the chatbot or its
  question box**, and now has a second reason: it is step 3, two blocks away,
  and ruling 83 specifies it.
- The next free ruling is **84** and the next free finding is **100**. Read
  `RULINGS.md` at the time anyway.
