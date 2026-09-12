# UI METHODOLOGY RULINGS — **decided before the build, so they cannot have been
# fitted to it.**

*Written 2026-09-12 alongside `UI_METHODOLOGY_PREDICTIONS.md` and committed with
it, before a line of `ui/index.html` was edited. `RULINGS.md` was read at the
time: **the next free ruling number is 94 and the next free finding is 115.***

---

# RULING 94 — **A SELECTION IS ADDRESSED UNDER THE TAB IT WAS MADE ON, AND AN
# ADDRESS THIS PROJECT HAS ALREADY HANDED OUT NEVER CHANGES WHAT IT OPENS.**

`hashOf` returns `#data` for the Methodology tab and nothing more. Measured at
the open of this block: **117 clickable rows** — 65 placements, 22 records, 30
edges — and a Guide that answers every one of them, all sharing one address. A
reader who opens a refused placement and copies the link hands over a link to the
tab and not to the thing.

The placement is not unaddressable: `#place/<key>` resolves. **It resolves onto
the Map tab**, which is a different question from the one the reader was looking
at, in a different apparatus, with a different Guide. That is RULING 84's own
objection in its own words — *"a shared link that quietly lands on a different
question is a viewer that would look entirely convincing and be wrong"* — and it
is why this needs a scheme rather than a patch.

## THE SCHEME

```
#data                          the tab
#data/place/<placement-key>    a placement, selected on Methodology
#data/record/<doc_id>          a record, selected on Methodology
#data/edge/<index>             an undrawn edge, selected on Methodology
```

## THE THREE DECISIONS INSIDE IT

**1. THE BARE FORMS ARE NOT TOUCHED.** `#place/…`, `#record/…`, `#point/…` and
`#edge/…` keep meaning exactly what they have meant since RULING 84: the Map tab,
with that thing selected. **They are addresses this project has handed out**, and
the one promise a hash scheme makes is that a link keeps meaning what it meant.
Re-pointing them at whichever tab currently renders the same apparatus would make
every existing link change destination the next time a card moves tabs — which is
precisely what happened to those five cards in the regions block.

**2. A TAB'S SELECTIONS LIVE UNDER THE TAB'S OWN PREFIX**, rather than each
getting a new top-level word. `#data/place/…` says where the reader was, not only
what they had open, and the same placement is legitimately addressable in two
places because it is legitimately readable in two places — with different
surroundings and a different Guide in each. Two addresses for two views of one
thing is correct; one address that silently picks a view is not.

**3. THE KINDS ARE DECLARED ONCE AND CHECKED TWICE.** `PANEL_EMPTY.data.selects`
already declares what this tab can select, and guard 49 re-derives that
declaration from the view's own markup. **The router reads the same list**, and a
guard asserts that every kind in it round-trips: `hashOf` writes an address and
`applyHash` reads the same selection back, on the same view. That is the
`--map-label` pattern one axis over — a value declared in two places with
something checking they agree — and it exists because FINDING 112 is what happens
when a guard recomputes from the thing it is checking.

## WHAT RULING 94 DOES NOT DECIDE

- **It does not make the hash a second source of truth.** `state` remains the
  only one. RULING 84, unchanged.
- **It does not give the Questions tab a prefix.** `#q/…` is a scheme of its own
  and is not renamed; a question is not "a selection on a tab", it is the thing
  the tab is about.
- **It says nothing about the trail.** The trail is furniture over the top of the
  address, RULING 85's distinction, and stepping it writes `state.selection` like
  any other selection.

---

# FINDING 115 — **the Methodology tab's closing paragraph makes four claims about
# one question's archive, and the archive has grown past two of them. No guard on
# this page can read a sentence.**

`viewAbout`'s last card says:

> *"And one question, on Aksumite trade, has failed to produce a grounded answer
> in every attempt under four different prompts, with the answer sitting in its
> own evidence in English."*

Measured against the bundle at `19cfba0`, on
`What did Rome trade with the Kingdom of Aksum?`:

```
39 runs                      five prompt versions — v1, v2, v3, v2r, v4
34 of 39 grounded            33 refused
22 character spans claimed   2 runs showable on the rail today
v1 1/1 showable · v2 0/1 · v3 0/2 · v2r 1/32 · v4 0/3
```

**"Four different prompts" is five, and "failed to produce a grounded answer in
every attempt" is 34 of 39 grounded with two showable runs.** The sentence was
true of a smaller archive and the archive grew underneath it. Nothing on the page
or in the harness noticed, because **every figure in it is prose**: guard 2g
hunts specific numeric literals it was told about, and no guard on this page can
read a sentence at all.

**This is FINDING 105's shape on a third surface.** It has now happened on the
cross-tabulation (FINDING 105), twice on the geography ledger's prose
(`UI_METHODOLOGY_START.md` §4B), and here. Each time a guard asserted that a
value was present and could not see that the words around it were wrong. RULING
90 exists for the same family.

**And the sharper half, which is why this is recorded rather than quietly fixed:
the one failing question this tab names is a question that IS IN THE RAIL, while
the two failures the rail withholds and counts have never been named anywhere on
the page.** The stale sentence and the two-block-old §3 debt are the same defect
seen from two sides.

**Found by reading `ui/index.html` whole at the open of the block** — the fifth
block running in which that read has found a real defect — and measured before it
was believed.
