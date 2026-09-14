# RIGHTS VALIDATION PREDICTIONS — **THE WORKLIST BUCKETS THIRTY-SIX OF THIRTY-EIGHT,
# AND THE TWO IT DROPS ARE THE TWO NOBODY HAS A RULE FOR.**
#
# **Every position figure in `RIGHTS_VALIDATION_START.md` §1 reproduces exactly.
# Its §2 worklist does not: buckets A, B, C and D sum to 36. `scandinavia-03-vimose`
# and `southasia-04-pattanam` are in none of them, and both are `web.archive.org`
# captures — a case the document never names because the repository has never had
# to answer it.**

*Written 2026-09-14, before a single rights target was opened, and handed over
before any cell is filled. RULING 78. Scored at the close in
`RIGHTS_VALIDATION_RESULT.md` and **not amended there**.*

---

# 0. THE STATE THIS IS PREDICTED AGAINST

Recomputed in the session container from the staged copies of
`data/corpus_rights.json` and the 54 records at `data/seed_corpus/*/*.json`,
before anything else was read:

```
records on disk        54        rights cells        54
cells with no record    0        records with no cell 0

unread                        38
open_licence_stated            5
two_positions_stated           3
permission_stated_no_licence   3
all_rights_reserved            2
public_domain                  2
states_no_terms                1

distinct hosts behind the 38                        18
records carrying licence-shaped prose in
  citation_original / notes / original_text_note    15
```

**§1 holds to the record.** 38 unread, 16 read, 18 hosts, 7 positions, and the
fifteen of §2E reproduce as the same fifteen records.

**§2 does not.** Bucket A is 3, B is 21, C is 9, D is 3. **That is 36.** The two
missing are:

```
scandinavia-03-vimose      web.archive.org/web/20151122163034/runenprojekt.uni-kiel.de/...
southasia-04-pattanam      web.archive.org/web/20160304031410/keralahistory.ac.in/...
```

Declared as **FINDING 118**, and the rule they need is **RULING 95**, both in
`RIGHTS_VALIDATION_RULINGS.md`. They are not part of the 24 this session reads.

**One further figure, recorded because the start document states it narrowly and
it will be misread later.** §2C says its nine records "have no `citation_original`
at all". True of those nine — and **17 of the 38 have no `citation_original`**.
The other eight have a non-Wikipedia `citation` and were bucketed by host, which
is correct. The class is bigger than the bucket; only the bucket is the worklist.

## What this session is, and what it is not

**Rob's call, taken at the top of the thread: all of bucket A and bucket B — 24
readings — and NOTHING SIGNED WITHOUT HIM.** Every reading in this block is
captured, quoted and proposed; no cell is written until he has been through the
sheet, and every cell that is then written is signed `curator_and_model`.

**This is the mitigation for the condition §7 names.** Twenty-four readings in a
sitting is FINDING 69's weather. What makes it survivable is that the session
that supplied the capture is not the thing that closes the cell — which is
`F6_RULINGS`' consequence used as a control rather than tripped over.

---

# 1. P1 — **THE FOUR `raw.githubusercontent.com` RECORDS DO NOT ALL SAY WHAT THEIR
# RECORDS SAY THEY SAY, AND THE SPLIT IS CBETA AGAINST KANRIPO.**

The four carry the most confident prose in §2E:

```
eastasia-04-jingjiao-stele   "Licence: CBETA, CC BY-NC-SA."
eastasia-05-liangshu-qin-lun "Licence: CC BY-SA 4.0."        Kanripo
eastasia-06-cefu-yuangui     "Licence: CC BY-SA 4.0."        Kanripo
eastasia-07-tang-huiyao      "Licence: CC BY-SA 4.0."        Kanripo
```

**A `raw.githubusercontent.com` URL serves a file, not a page.** No footer, no
`rel="license"`, no `dcterms.rights`, no badge — nothing a site states, because
nothing here is a site. What the object can state, it states INSIDE ITSELF.

**PREDICTED, and this is the split the start document's correction set up:**

- **`eastasia-04` (CBETA) comes back `open_licence_stated`** — CBETA's XML is TEI
  and the licence lives in the file's own `<publicationStmt>`, which is the
  object stating its terms in the strictest possible sense.
- **`eastasia-05`, `06` and `07` (Kanripo) come back `states_no_terms`** — the
  Kanripo text files carry a small mandoku header and no licence sentence. The
  repository has a LICENSE file; **the file quoted does not**, and a repository
  is not an object. FINDING 87 in a new costume.

**PREDICTED: three cells therefore contradict prose already in their records.**
Not because "CC BY-SA 4.0" is false about Kanripo, but because a rights position
is what the object read says, and the object read says nothing. That distinction
is the entire column.

**PREDICTED: this produces a question this block cannot settle by reading —
whether a repository's LICENSE file is the object's position for a raw file
served out of it.** It is named here so that it is a declared open question at
the close rather than a cell someone rounded off.

---

# 2. P2 — THE DISTRIBUTION OF THE 24, CALLED PER RECORD SO EVERY LINE SCORES

Predicted positions. Each is a separate call; the aggregate below is the sum of
these and is not an independent prediction.

```
BUCKET A — britishmuseum.org
africa-02-aksumite-coin        all_rights_reserved
persia-02-silver-plate         all_rights_reserved
persia-03-coin                 all_rights_reserved

BUCKET B
africa-03-periplus-adulis      open_licence_stated      el.wikisource.org
arabia-01-periplus             open_licence_stated      same object
southasia-02-periplus-muziris  open_licence_stated      same object
eastasia-04-jingjiao-stele     open_licence_stated      CBETA XML header
eastasia-05-liangshu-qin-lun   states_no_terms          Kanripo
eastasia-06-cefu-yuangui       states_no_terms          Kanripo
eastasia-07-tang-huiyao        states_no_terms          Kanripo
africa-04-silko-talmis         states_no_terms          epigraphy.packhum.org
africa-05-adulis-throne        states_no_terms          epigraphy.packhum.org
persia-01-skz                  all_rights_reserved      parthiansources.com
persia-04-bronze-heracles      all_rights_reserved      parthiansources.com
scandinavia-01-hoby-treasure   states_no_terms          en.natmus.dk
scandinavia-02-gudme-hoard     states_no_terms          en.natmus.dk
africa-01-ezana-stone          all_rights_reserved      en.protothema.gr
eastasia-03-hwangnam-glass     open_licence_stated      heritage.go.kr, KOGL
persia-05-abnun                all_rights_reserved      uci.edu
seasia-03-khao-sam-kaeo        states_no_terms          real.mtak.hu (a PDF)
seasia-05-my-son-b6            open_licence_stated      isaw.nyu.edu
southasia-01-akananuru-149     permission_stated_no_licence  projectmadurai.org
southasia-03-muziris-papyrus   open_licence_stated      papyri.info
southasia-05-brihatsamhita     states_no_terms          wisdomlib.org
```

Summing to:

```
states_no_terms                 9
open_licence_stated             7
all_rights_reserved             7
permission_stated_no_licence    1
two_positions_stated            0
public_domain                   0
```

**PREDICTED: `states_no_terms` is the largest single outcome of this block, at 9
of 24, and the honest reading of that is not that the sources are careless.** It
is that most of these objects are texts served by scholars, and a text served by
a scholar states its edition and not its terms.

**PREDICTED: `two_positions_stated` comes back ZERO across the 24**, against a
corpus that already holds three of them. The two-position cases found so far —
parsigdatabase, UNESCO — were found on sites with commercial footers. This
block's hosts are mostly not that.

**The named way P2 goes wrong, so it is not claimed as a win afterwards:**
`el.wikisource.org` is the likeliest to break it. A Wikisource page carries the
project's CC BY-SA footer, and the 1855 Müller edition it reproduces is public
domain; if the page itself carries BOTH — a public-domain banner and the site
licence — then the three Periplus records are `two_positions_stated` and not
`open_licence_stated`, and neither wins. **That is the outcome I am least
confident about and the one where adjudicating would be easiest.**

---

# 3. P3 — **ONE OBJECT, THREE CELLS, AND THAT IS NOT DERIVATION**

`africa-03`, `arabia-01` and `southasia-02` cite **the same `el.wikisource.org`
URL**. One reading legitimately answers all three.

**PREDICTED: this reads as a violation of NEVER DERIVED and is not one.** The
prohibition is on taking a sibling record's position as evidence for this one;
three records pointing at one object are one reading of one object, and each
cell still carries its own `read_off`, `read_by` and `read_on`. **The distinction
is recorded here in advance because it will look like a shortcut in the diff.**

**PREDICTED: nobody reading the closed column six months from now can tell those
two situations apart from the data.** Three identical quotations with three
identical `read_off` URLs is what both look like. If that turns out to be true it
is a schema observation worth a finding, not a defect in this block.

---

# 4. P4 — `persia-05-abnun` IS A CITATION DEFECT WEARING A RIGHTS DEFECT'S CLOTHES

Its rights target computes to **`https://uci.edu/copyright/`** — because that URL
is what the record's `citation_original` prose contains. The text is not there.
That page is the terms; the object is a Sasanika page elsewhere on
`humanities.uci.edu`.

**PREDICTED: reading `uci.edu/copyright/` returns a clean `all_rights_reserved`
quotation that is nonetheless the wrong reading**, because it is a reading of the
policy and not of the object — FINDING 87 exactly, arrived at by following the
record's own pointer.

**PREDICTED: the correct handling is to read the Sasanika object page as well,
record the position off that, and raise the citation pointer as a finding** —
not to fix `citation_original`, which §5 puts out of scope for this thread.

---

# 5. P5 — WHAT CORROBORATES

**PREDICTED: `papyri.info` and `isaw.nyu.edu` come back agreeing with the prose
already in their records** — CC BY 3.0 in both cases, stated on the object.

**PREDICTED: those are the only two clean corroborations in the 24.** §2E's
instruction is that agreement "costs nothing"; this is the prediction that says
how often it happens — twice.

---

# 6. P6 — **THE PREDICTION WRITTEN NOT TO FLATTER THE BLOCK: BUCKET A IS THREE
# READINGS THAT TEACH NOTHING.**

FINDING 87 is why bucket A is three jobs rather than one lookup. It is a good
rule and it was bought with a real error.

**PREDICTED: all three British Museum objects return `all_rights_reserved` with a
quotation materially identical to the one already recorded for
`southasia-07-bm-claudius-aureus`, and the block learns nothing from any of
them.** Three readings, zero new information, and the rule that required them
costs more than it returns on this host.

**PREDICTED: that is still the right rule, and the result document must resist
the sentence "bucket A confirmed the policy transfers".** It did not confirm
that. It failed to disconfirm it on three objects, which is a different and much
weaker claim, and the Walters case is what the difference is worth.

**What would refute P6, and it is the outcome worth wanting:** any one of the
three carrying an image-licence line — a `CC BY-NC-SA 4.0` on the object's
asset — beside the site's reserved-rights statement. That is
`two_positions_stated`, and it would mean the policy did not transfer on the
third object anyone happened to check.

---

# 7. P7 — HOW MUCH OF THIS ACTUALLY LANDS

**PREDICTED: between 2 and 4 of the 24 are not readable to the required standard
this session** — a host that refuses the browser, a page whose terms are an image,
a PDF that must be opened rather than rendered. **Those stay `unread`, and
`states_no_terms` is not available to them.** §4's trap, named before it is felt.

**PREDICTED: Rob's confirmation pass changes at least one of the 24** — a
position, a quotation boundary, or a `read_off` URL. **If it changes none, that
is not a clean sweep; it is evidence the pass was too easy to be a check**, and
the result document says so in those words.

**PREDICTED: this block does not close the column.** After 24 readings, 14 cells
remain `unread` — buckets C and D, and the two in FINDING 118 — and the
Methodology copy has to be able to say that accurately rather than round it up.

---

# 8. WHAT WOULD MAKE THIS BLOCK A FAILURE

Not a wrong prediction. **A cell filled from a sentence already in the record** —
the fifteen of §2E are sitting there, four of them naming a licence and a version
number, and the cheapest afternoon available is the one that imports them.

And the second, quieter one: **a source that could not be opened recorded as
`states_no_terms`.** Every unreadable target in this block is named in the result
document with the reason it could not be read, and its cell stays `unread`.
