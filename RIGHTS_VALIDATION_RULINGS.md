# Rights validation — rulings and findings. **RULING 95 and FINDING 118**,
# declared 2026-09-14, before any rights target was opened.

*Numbers read from `RULINGS.md` at the time, per `RIGHTS_VALIDATION_START.md` §5:
the register's own line said "The next free ruling number is 95. The next free
finding is 118." That line is updated in the same commit as this file.*

---

# FINDING 118, 2026-09-14, in the first ten minutes of the rights block.

**A worklist that buckets by host will silently drop the records whose host is
not a source.**

`RIGHTS_VALIDATION_START.md` §2 sorts the 38 unread records into four buckets —
3 + 21 + 9 + 3. **That is 36.** Recomputed from `data/corpus_rights.json` and the
54 seed records before any page was opened, the two records in no bucket are:

```
scandinavia-03-vimose    web.archive.org/web/20151122163034/
                         http://www.runenprojekt.uni-kiel.de/...
southasia-04-pattanam    web.archive.org/web/20160304031410/
                         http://www.keralahistory.ac.in/...
```

**Both are Wayback Machine captures, and that is why they fell out.** Every other
bucket is defined by a host that is a publisher — a museum, a library, a
repository, an aggregator. `web.archive.org` is a host that is not a source, and
a rule written by grouping hostnames has nowhere to put it. The start document's
own §1 figures are exact — 38 unread, 18 hosts — and `web.archive.org` is one of
the 18 it counted and none of the four it bucketed.

**This is FINDING 115's shape once more, and the start document warned about it
in its own §7.** A figure can be right while the prose built on it is short: §1
counted 38 and §2 worked 36, and nothing in either document could see the gap
because no instrument reads a worklist. The gap was found by recomputing the
buckets rather than by reading them, which is exactly what §6.1 told this thread
to do and the only reason it was found before the block closed instead of after.

**What it costs:** two records that would have stayed `unread` with no name
against them, in a block whose entire purpose is to make the residue nameable.

---

# RULING 95 — **AN ARCHIVED CAPTURE IS THE PAGE AS CAPTURED. THE ARCHIVE'S OWN
# TERMS ARE NOT THE SOURCE'S POSITION.**

Where a record's rights target is a `web.archive.org` capture, the object is the
**original page at the moment of capture**, and the rights position is read off
the captured page.

```
THE OBJECT        the archived page, as rendered inside the capture

READ_OFF          the full Wayback URL, timestamp included. The timestamp is
                  part of the reading: it says WHICH state of the source was
                  read, and a live site may state something else today

EXCLUDED          everything archive.org injects -- the toolbar, the banner,
                  the "About this capture" panel, any archive.org footer.
                  None of it is the source speaking, and none of it may be
                  quoted into a cell

NOT THE POSITION  archive.org's own terms of use. They govern the archive,
                  not the archived. A cell quoting them is a reading of the
                  wrong object -- FINDING 87, one layer up

STATES_NO_TERMS   available only if the capture RENDERED and the captured page
                  states nothing. A capture that will not load, or that loads
                  without the region of the page where terms would sit, is
                  `unread` -- section 4 of the start document, unchanged
```

**Why this and not the alternative.** The obvious competing rule is that a
capture states two positions — the archived site's and archive.org's — to be
quoted in the order they appear under the parsigdatabase precedent. **It is
wrong, and it is worth saying why, because it looks rigorous.** Two positions
means one source contradicting itself. The archive is not the source; it is the
delivery. Recording archive.org's terms beside the captured page's would make
every archived record in this corpus `two_positions_stated` by construction,
which is a fact about how the text was fetched and not about who holds rights in
it — **the reachability-for-licence substitution FINDING 69 exists to forbid,
committed in a new place.**

**What this ruling does not settle**, recorded so nobody reads it as settled: it
says nothing about whether the archived page's terms are still in force, and
nothing about whether the capture is a faithful rendering of what the page said.
It fixes which object is read. The freshness question belongs to whoever next
argues about `read_on`.

**Neither of the two records in FINDING 118 is read in this session.** Rob's
scope for the block is bucket A and bucket B. The ruling exists so that when they
are read, the rule was written before the reading and not around it.
