# RIGHTS VALIDATION START — **THIRTY-EIGHT OF FIFTY-FOUR RECORDS SIT AT `unread`,
# AND THE SCHEMA ALREADY SAYS WHO IS ALLOWED TO CLEAR THEM.**
#
# **`read_by` accepts `model` and `curator_and_model`. A reading does not have to be
# done by hand to count — it has to be done off the object, quoted verbatim, and
# signed. That is what makes this a session's work and not a wet afternoon.**

*Written 2026-09-14, out of the Methodology design thread, which stopped to ask what
`unread` actually means on a public page and did not like the answer. **Every figure
in §1 and §2 was computed at that moment from `data/corpus_rights.json` and the 54
seed records, not inherited from a document.** The first thing this thread does is
recompute them and stop if they have moved.*

---

# 1. WHERE THIS STANDS

```
54 records          16 rights positions read        38 unread
18 distinct hosts behind the 38                     7 positions in the vocabulary
15 of the 38 already carry licence-shaped prose that is NOT a reading — see §2E
```

Current distribution, computed from `data/corpus_rights.json`:

```
unread                        38
open_licence_stated            5
two_positions_stated           3
permission_stated_no_licence   3
all_rights_reserved            2
public_domain                  2
states_no_terms                1
```

**`RULINGS.md` is the authority: next free ruling 95, next free finding 118.** Read
it at the time anyway. The register was clean at the close of the Methodology block.

**Read `data/corpus_rights.json`'s own header keys before anything else** —
`why_unread_is_the_default_and_not_a_guess` and
`why_it_is_not_DERIVED_from_citation_original`. They are short, they are the whole
argument, and this block is the one most likely to violate them by being efficient.

---

# 2. THE WORKLIST — **THIRTY-EIGHT RECORDS, AND THEY ARE NOT THIRTY-EIGHT EQUAL JOBS**

Bucketed by what actually has to happen, computed from each record's rights target —
`citation_original` where the record has one, otherwise `citation`.

## A. The policy is already located — 3 records

```
africa-02-aksumite-coin        britishmuseum.org
persia-02-silver-plate         britishmuseum.org
persia-03-coin                 britishmuseum.org
```

The British Museum's position was read verbatim for `southasia-07-bm-claudius-aureus`
and recorded as `all_rights_reserved`, including the searches that came back empty.
**That does not transfer.** FINDING 87 is the Walters case: eleven CC0 badges on the
object page, and a policy page assigning CC0 to images and metadata while the longer
text descriptions — the thing actually quoted — fall under the GFDL. Read each object.
What is saved here is finding the policy, not reading it.

## B. Read the policy, per object — 21 records

```
el.wikisource.org          africa-03-periplus-adulis, arabia-01-periplus,
                           southasia-02-periplus-muziris
raw.githubusercontent.com  eastasia-04-jingjiao-stele, eastasia-05-liangshu-qin-lun,
                           eastasia-06-cefu-yuangui, eastasia-07-tang-huiyao
epigraphy.packhum.org      africa-04-silko-talmis, africa-05-adulis-throne
parthiansources.com        persia-01-skz, persia-04-bronze-heracles
en.natmus.dk               scandinavia-01-hoby-treasure, scandinavia-02-gudme-hoard
en.protothema.gr           africa-01-ezana-stone
heritage.go.kr             eastasia-03-hwangnam-glass
uci.edu                    persia-05-abnun
real.mtak.hu               seasia-03-khao-sam-kaeo
isaw.nyu.edu               seasia-05-my-son-b6
projectmadurai.org         southasia-01-akananuru-149
papyri.info                southasia-03-muziris-papyrus
wisdomlib.org              southasia-05-brihatsamhita
```

The `raw.githubusercontent.com` four are not one source: `eastasia-04-jingjiao-stele`
is **CBETA**, the other three are **Kanripo**. Both already have a licence written
into `citation_original` — see §2E, which is the trap.

`persia-05-abnun` carries a warning in the cost ledger worth reading first: the terms
were found on a different page from the text, and the finding was a **correction** —
an earlier document had asserted the site states no terms anywhere, and it is a UC
Irvine site with copyright terms at `uci.edu/copyright/`. The work was done and never
written into the column in the required form. That is what most of this backlog is.

## C. The source is not established — 9 records, and this is the slow bucket

```
arabia-02-palmyrene-tariff     arabia-03-jsnab17          arabia-04-jabal-dabub
scandinavia-04-illerup-adal    scandinavia-05-thorsberg-chape
seasia-02-oc-eo-site           seasia-04-dong-yen-chau
seasia-06-kedukan-bukit        seasia-07-talang-tuo
```

**These nine have no `citation_original` at all, so the rights target computes to the
English Wikipedia article cited as `citation`.** That is not one situation, it is at
least three, and the first job on each is to read its `original_text_note` and work
out which:

- **The text really is the aggregator's.** `scandinavia-04-illerup-adal` says so
  outright: *"Summarized from excavation reporting (Ilkjær) as synthesized on
  Wikipedia."* Wikipedia's own licence is then the correct position and this is a
  bucket-B job.
- **The text is an edition's and the edition is named in prose but not cited.**
  `arabia-04-jabal-dabub` carries a Sabaic transliteration per Al-Jallad's 2022
  revised reading, and names the article in full in `translation_source` — a journal
  paper, in copyright. The position must be read off **that**, and `citation_original`
  should point at it.
- **The text is an edition's and the edition is not named anywhere.**
  `seasia-06-kedukan-bukit` carries ten lines of Old Malay with a detailed note about
  the edition's hyphenation and the source's ellipsis, and cites only Wikipedia. Until
  somebody establishes which edition that is, there is no object to read a position
  off.

**The third case is a citation defect, not a rights defect, and it is very likely a
finding.** Do not close it by recording Wikipedia's licence over an edition's text.

## D. Hosts already documented as resisting — 3 records

```
eastasia-01-weilue          zh.wikisource.org
eastasia-02-hou-hanshu      zh.wikisource.org
seasia-01-oc-eo-medallion   academia.edu
```

`F4_CANDIDATES.md` and `F5_CANDIDATES.md` list both hosts among the sources that
refuse or degrade — zh.wikisource as cache-only, academia.edu behind a login. **If the
object cannot be reached, the cell stays `unread`.** See §4.

## E. **FIFTEEN OF THE THIRTY-EIGHT ALREADY LOOK ANSWERED. THAT IS THE TRAP.**

Measured, not guessed: **15 of the 38 unread records already carry licence-shaped
prose** in `citation_original`, `notes` or `original_text_note`. Some of it is
specific and confident:

```
eastasia-04-jingjiao-stele   "Licence: CBETA, CC BY-NC-SA."
eastasia-05/06/07            "Licence: CC BY-SA 4.0."            (Kanripo)
southasia-03-muziris-papyrus "(DDbDP, CC BY 3.0)"
africa-03 / arabia-01 /
  southasia-02 (Periplus)    "(ed. C. Müller, ... Paris 1855; public domain)"
seasia-06 / seasia-07        "The inscription itself is 7th-century and out of
                              copyright."
seasia-05-my-son-b6          "THE FIRST RECORD IN THIS CORPUS UNDER AN EXPLICIT
                              OPEN LICENCE."
```

**Every one of those is a sentence a curator typed. None of them is a reading.** They
are precisely the material `why_it_is_not_DERIVED_from_citation_original` refuses, and
importing them would fill fifteen cells in an afternoon and reproduce FINDING 69
fifteen times. Two of them are already visibly the wrong shape for a rights cell: the
Periplus line dates the *edition* rather than quoting the host's terms, and
`persia-05-abnun`'s prose repeats an assertion that a later reading **corrected**.

Treat all fifteen as unread and open the source. Where the reading agrees with the
prose, that is corroboration and costs nothing. Where it does not, that is the finding
this block exists to produce.

---

# 3. WHAT THIS BLOCK IS FOR

**Clear the backlog to the standard already declared, and make the residue nameable.**
A page that says *most sources have not been checked* reads as carelessness. A page
that says *these were read on these dates, and these four could not be reached and
here is why* reads as what it is. The copy is not the deliverable; the readings are.

Secondary, and only if the readings are done: **the triage script.** A pass that
fetches each rights target and surfaces the candidate signals — `rel="license"`,
any `creativecommons.org` href, licence badges, `dcterms.rights` metadata, footer
text — and prints them beside the record for a person to accept or reject. **This does
not break the never-derive rule, because it proposes a sentence to read and writes
nothing.** Guard the distinction in the file's own header or it will be lost in a
year.

---

# 4. THE RULES THAT WILL FIGHT YOU

`ingest/fidelity.py check_rights`, run through `python -m ingest.verify`. It checks
**shape and coverage, never content.**

```
BIDIRECTIONAL   every record has a cell; every cell names a real record

SIGNED          any position other than `unread` must carry read_off (URL),
                read_by (curator | model | curator_and_model) and an ISO read_on.
                A reading nobody signed is a claim about a source nobody opened.

QUOTED          five of the seven positions must carry a verbatim quotation.
                two_positions_stated must carry TWO OR MORE, in the order they
                appear on the page. states_no_terms must carry NONE — if there is
                a sentence to quote, the source states terms.

COUNTED         never gated. A position is reported; it does not block a record.
                all_rights_reserved is a statement about what the source said, not
                a verdict on whether the quotation may stand. RULING 74 decides that.

NEVER DERIVED   not from citation_original, not from a matcher, not from a sibling
                record on the same host.
```

**AND THE TRAP THAT IS NOT A CHECK.**

> **`states_no_terms` means the object WAS REACHED and says nothing. A source you
> could not open is `unread`.** Nothing in the schema can tell those apart, and
> collapsing them is the single most likely way this block ships a lie. Bucket D
> exists so that temptation has a name before anyone feels it.

**The second trap: the site is not the object.** FINDING 87. A policy located at
host level tells you where to read; it does not tell you what the object says.

**The third: do not adjudicate.** Where a source states two positions that disagree,
both are quoted in the order they appear and neither wins. `parsigdatabase.com` and
the UNESCO record are the precedents.

---

# 5. WHAT THIS THREAD MUST NOT DO

- **Not fill a cell from prose already in the record.** That prose is what produced
  FINDING 69. *An unread cell is a debt with a name; a guessed cell is a finding
  waiting.*
- **Not record an unreachable source as `states_no_terms`.** §4.
- **Not let a host-level policy stand as an object's position** without opening the
  object. FINDING 87.
- **Not adjudicate between two stated positions.**
- **Not change a record's text, tier, placements or citation offsets.** Archived
  citation spans point into these files by exact offset; a rights fix is not a text
  edit. If
  `citation_original` genuinely needs to be added for a bucket-C record, that is a
  record edit, it moves the content hash, and it is its own decision with its own
  commit — not something folded into a rights pass.
- **Not touch `ui/` or the Methodology copy.** That is the other thread and it is
  mid-review.
- **Not hand-edit `ui/data.js`.** `python ui/build_ui_data.py`, and FINDING 101 before
  running it on Windows.
- **Not assign ruling or finding numbers from this document.** `RULINGS.md` is the
  authority and the next free number is read from it at the time.

---

# 6. FIRST FIVE MINUTES — **AND THE ENVIRONMENT HAS NOT IMPROVED**

**THE BRIDGE SHELL IS STILL GONE.** A Windows update released 2026-09-08 stops
Claude's isolated Linux workspace reaching the repository; `device_bash` reports no
drive shares mounted. Confirmed still broken 2026-09-12 and again 2026-09-14. **Do not
spend a turn diagnosing it.**

```
WORKS         device_list_dir / device_stage_files / device_commit_files
              a browser — Claude in Chrome, or the desktop app's own pane
DOES NOT      any shell on the host. No git, no pytest, no ingest.verify
NOT A WAY     computer-use. Terminals resolve at `click` tier
ROUND IT
```

1. **Recompute §1 and §2 before trusting them.** Stage `data/corpus_rights.json` and
   the 54 records under `data/seed_corpus/*/*.json` and rebuild the buckets. If the
   distribution has moved, find out what moved it before reading a single page.
2. **Read the three header keys of `data/corpus_rights.json`.** They are the argument.
3. **Write the predictions and commit them BEFORE any cell is filled.** RULING 78.
   Include one built not to flatter the block. Candidates worth being wrong about:
   how many of bucket B come back `states_no_terms`; whether any reading *contradicts*
   a claim already in a record's prose, as `persia-05-abnun`'s did; whether bucket C
   produces a citation finding.
4. **A browser pass is an established, declared practice here** —
   `F5_PART3_BROWSER_PASSES.md`, `F6_BROWSER_PASS2.md`. It carries a consequence
   recorded in `F6_RULINGS.md`: a session that supplied a capture is no longer an
   independent check on it. Declare `read_by` honestly — `model` where the session
   read the page, `curator_and_model` where Rob confirmed it.
5. **`data/corpus_rights.json` is hand-maintained data, not generated.** Editing it is
   a text edit: stage it, edit in the container, commit it back, **and check the byte
   count after every write** — FINDING 104.
6. **`python -m ingest.verify` is host-only** and is the gate on shape. Hand it to Rob
   in a runbook; do not claim green from the container.
7. **Commit messages: `commit-<topic>.txt`, one per commit** — RULING 93 — naming
   every file the commit touches. **Then read `git status --short`** — FINDING 116.

---

# 7. THREE THINGS WORTH CARRYING IN

**THE BACKLOG IS NOT UNEXAMINED WORK.** Rights were investigated during curation —
the cost ledger tracks `rights_and_licence` as its own phase precisely because it is
*"the phase most easily dropped without anyone noticing it has been."* Twenty of the
thirty timed records carry minutes against it. What is missing is not the looking; it
is the looking written down in a form a check can see and a reader can trust. Say that
accurately in the result document, because the Methodology copy will quote it.

**THE COLUMN WAS BUILT BECAUSE A SENTENCE COULD NOT BE READ.** `RULING 74` had
required the rights position to be stated in the record since F5 Part 3, and the
requirement was invisible: it lived in free prose, and `ingest.verify` never opened
it. This is the same shape as FINDING 115 and the geography ledger — a guard can
assert a figure is present and cannot read the sentence around it. The column is what
turned an unreadable requirement into a checkable one, and this block is the first
time it gets used for the thing it was built for.

**AND THE ONE FIGURE THAT WOULD MAKE THIS BLOCK A FAILURE:** thirty-eight cells
filled and one of them wrong. FINDING 69 was two wrong claims in a single afternoon,
made by moving fast over sources that mostly cooperated. Reading thirty-eight pages in
one sitting is the same conditions again. **Prefer a smaller number of readings each
of which is right, and leave the rest `unread` — which is exactly what the state is
for.**
