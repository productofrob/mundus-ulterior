# F5 Part 3 rulings — 2026-09-05

*Block F's fifth distinct date. `date -u +%F` on the host of record gives
`2026-09-05`; F4's close, F5 Part 1 and F5 Part 2 all ran on `2026-09-04`.*

*This session had NO SHELL on the repository's host and no bridge. Nothing here
was measured by running anything in this repository. Where a number appears it
came from reading a file, and it says so.*

---

# FINDING 69 — "open" names two different properties and this project's hunt documents use one word for both

## The observation

`F5_CANDIDATES.md` records, of the Syllaeus article: **"Cite the Acta Orientalia
version; it is the one verified open."** A curator opened it on 2026-09-05 and
found it is © Akadémiai Kiadó, all rights reserved, sold at
`akjournals.com/view/journals/062/70/1/article-p21.xml`. The copy at
`real.mtak.hu` is a deposit in the Hungarian Academy of Sciences' repository:
free to read, under a repository policy, under no Creative Commons licence at
all.

**Nothing in the hunt was wrong.** The session that wrote that line reached the
PDF, read it, and recorded that it had. What it recorded was **reachability**,
and the word it recorded it in was **"open"**, which in every other line of the
same document means **openly licensed**.

## The same defect, four hours earlier, on a different axis

The Ruwāfa capture on the same day produced the same shape from the other
direction. `F5_CANDIDATES.md` records the Ca' Foscari licence as verified, with
the sentence quoted and the chapter cited. The chapter has **no front matter**:
the licence sentence is the BOOK's, at a different URL, and the issue date
`2021-04-26` that travelled with it could not be confirmed at all. A licence
verified against the wrong object, and a licence claim made out of a
reachability check. Twice in one session, in opposite directions.

## Why this is the shape this repository has already paid for

`PLACES.md` names four prior instances by hand — `has_extent` against
`has_area`, `translation_chunk` against `translation_chunk_id`, `--find` against
`--survey`, and the field once called `pleiades_id`. Each is **two questions
under one name**, and each was found the same way: something that read correctly
for a while, in the reassuring direction, until a case arrived where the two
answers differed.

Reachability and licence differ constantly. A CC BY article behind a broken
fetcher is licensed and unreachable. A subscription article in a green
repository is reachable and unlicensed. **This corpus needs both facts about
every source and has been carrying one word for them.**

## What follows

`F5_CANDIDATES.md`'s Arabia block is corrected in place, and the correction is
the two properties named separately rather than the adjective changed:

- **Ruwāfa** — reachable via the per-chapter PDF; licensed CC BY 4.0, verified
  on the book's front matter and not the chapter's, issue date unconfirmed.
- **Syllaeus** — reachable via the REAL repository deposit; **not openly
  licensed**, © Akadémiai Kiadó, all rights reserved.

**Every other licence claim in this repository is now suspect until re-read, and
two are named in the block's own documents as already unclear:** Sasanika
"states no licence, no terms of use and no citation guidance anywhere on its
site", and wisdomlib "carries no copyright or licence statement of any kind".
Both were written as per-record notes. Neither was read as the same fact
twice.

**This finding does not adjudicate any of them.** It says the vocabulary was
carrying two facts in one word. Ruling 74 is what decides what to do about the
sources.

---

# Ruling 74 — an in-copyright source may be cited and quoted, under four conditions, declared in the record

## What forced it

Of the four captures F5 Part 3 still owes, **three have no clean licence**:

```
arabia-06-syllaeus      IN COPYRIGHT, all rights reserved (Akademiai Kiado).
                        Free to read in the REAL repository deposit.
persia-05-abnun         NO LICENCE STATED ANYWHERE. Sasanika states no licence,
                        no terms of use and no citation guidance -- checked by
                        F5 Part 2 and recorded in F5_PART3_START.
southasia-05            NO LICENCE STATED ANYWHERE. wisdomlib carries no
  -brihatsamhita        copyright or licence statement of any kind -- checked.
```

Every one of them was written as a note inside its own candidate entry. **The
rule was never written**, and `arabia-06` would have been the first record in
this corpus to reproduce a TRANSLATION from an in-copyright, all-rights-reserved
publication — the existing records lean on Hirth 1885, Kern 1865, Iyer 1884,
CC BY, CC BY-SA or CC0. A threshold crossed with no ruling is the shape
FINDING 47 is about, and it was about to be crossed three times in one session.

## The rule

**A record may carry source-language text and a published translation from an
in-copyright work when all four of these hold, and the record says so in its own
`citation_original`:**

1. **The quotation is short and is bounded by the source itself** — a single
   inscription, a single lemma, a single verse and its gloss. Not a chapter, not
   a run of pages, not everything the article prints.
2. **The work is fully cited** — author, title, journal or publisher, volume,
   year, pages, and DOI where one exists. The record cites the publication, not
   only the URL it was read at.
3. **The rights position is stated verbatim in the record**, naming the
   copyright holder and the terms, and naming the repository or host separately
   from the publisher when they differ. Where a source states no terms at all,
   the record says *that*, in those words, rather than leaving the field silent.
4. **The use is non-commercial research** and the corpus stays so.

**Where a condition cannot be met, the source is not taken.** Condition 3 is the
one that does work: a source with no reachable statement of terms is admitted
only by recording that it has none, which is a fact a reviewer can act on and an
adjective is not.

## What this is not

**It is not a legal opinion and this document does not pretend to give one.** It
is a standard this project holds itself to, of the kind scholarly publication
already applies to quotation, written down so that four records are decided the
same way instead of four different ways by whoever happened to curate them.

**It does not make an unlicensed source equal to a licensed one.** The two facts
FINDING 69 separates stay separate: `citation_original` records the licence where
there is one and records its absence where there is not, and a future reader
sorting the corpus by rights position can do so.

**It does not reach the distractor corpora.** `data/distractors` carries
per-source licence declarations from the Met and the Cleveland Museum of Art, and
those are publisher declarations obtained under each institution's own terms.
Nothing here loosens them.

## What it costs, stated rather than buried

**The corpus's rights position becomes heterogeneous and the file that would say
so does not exist.** Records now sit in at least four states — public domain,
CC0/CC BY/CC BY-SA, in copyright and quoted, and no terms stated — and nothing
counts them. `ingest.verify` does not read `citation_original`. **A rights
column is owed and is not built today**; until it is, the position is
recoverable only by reading 38 records by hand.

**And two records already in the corpus were admitted before this rule existed
and have not been re-read against it.** `arabia-04-jabal-dabub` cites Al-Jallad
in *Jerusalem Studies in Arabic and Islam* 52 (2022) and reproduces his
translation; `eastasia-07-tang-huiyao` cites Kanripo as CC BY-SA 4.0, which is a
licence claim of exactly the kind FINDING 69 says is now suspect. **Neither is
amended here.** Re-reading them is owed to F6, and doing it in the same session
that wrote the rule would be the rule fitted to what already passed — which is
the complaint ruling 51 records against an allocation decided at F7.

## The alternative that was refused, and it had the better argument on one axis

**Take the transliteration and not the translation** where rights are unclear.
The source-language text of an inscription is a mechanical rendering of an
ancient object; the English is a scholar's work. On the rights axis that is
plainly the safer line and it was the option this session put first.

**It was refused on what it does to the plan, and the cost of refusing it is
recorded here rather than in the record it saves.** Arabia's second F5 slot is
`verbatim_with_provenance`, which requires a cited published translation by
definition — `corpus_tiers.json`'s own vocabulary. A record carrying only the
transliteration is `verbatim_machine_english`, which is not the slot. So the
safer line does not produce a weaker record: **it produces a failed slot**, F5
returns to 5 of 7 and the corpus to 54, and the tranche would record as a
supply failure something that is a rights question about one journal.

That is a real argument on the other side and it is why this ruling names four
conditions instead of asserting a permission. **A reader who thinks condition 1
is too loose should say which record breaches it.**

---

# FINDING 70 — the curation-cost column now measures two different agents in one number, and six of its seven phases changed hands in a single session

## What happened

Records 37 to 40 were curated on 2026-09-05 by a session with no shell on the
host. The work divided like this, and the ledger cannot see the division:

```
phase                       who did it            what the number is
source_hunting              F5 Part 2, YESTERDAY  0, and it is an ACCOUNTING GAP
rights_and_licence          the model             model wall-clock
text_capture                THE CURATOR           self-reported, "6 minutes, average 5-7"
translation_and_fidelity    the model             model wall-clock
placement                   the model             model wall-clock
authoring                   the model             model wall-clock
rework                      nobody                0
```

**One phase of seven is a human's minutes. Five are a model's. One is a gap.**

## Why this is not the same as record 36's warning, and is worse

`eastasia-07-tang-huiyao` already carries a warning on this column: its
`source_hunting` is an estimate, because the hunt ran as a machine
re-verification across four regions in parallel and "is not a human reading
catalogues, which is what the same phase measured for records 25 to 35."

**That was one phase. This is six.** And the direction is the same one ruling 46
already forbids reading: a model apportioning its own wall clock produces
smaller, smoother numbers than a human timing themselves, and it produces them
across every phase at once. `min_n_to_read_as_a_trend` is 10 and
`verbatim_with_provenance` now holds 23 declared records — comfortably above it,
and about to be read as a trend by somebody who does not know that four of its
timed entries measure a different agent.

## The apportionment is judgement, and it is not disguised as anything else

The model's total wall clock for the session is bounded by file timestamps —
08:06Z to 09:55Z. **Splitting that total across four records and five phases was
done by judgement, not by a clock per phase**, and every one of those figures is
marked `estimated` with the reason attached. No `measured` provenance is claimed
anywhere on these four records except `rework`, which is genuinely zero.

`rights_and_licence` is the exception worth naming: it is **the first non-zero
figure that phase has ever carried in this ledger.** Records 25 to 36 all book it
at 0. It is 12 minutes on `arabia-06-syllaeus` alone, and the whole of that is
booked on the one record rather than spread across four, because spreading it
would hide that a single record's rights check produced FINDING 69 and Ruling 74.

## What is NOT booked, and where it belongs

**Browser pass 1 — roughly twenty minutes on the two Bhaṭṭotpala editions — is
`source_hunting` for RECORD 41 and is not booked here.** It must go into that
record's entry when it is written, or the one record in this tranche whose source
genuinely had to be hunted by eye will show a zero.

**Browser passes 3 and 4 — DASI and the Mojmal title page — are F6 and F7
hunting**, done in F5's session. They fill no F5 slot and are booked nowhere.
That is the same class of gap as the `source_hunting` zeros above, arriving from
the other end: work done in one sub-tranche for another.

## What follows

**Nothing is corrected here and no number is withdrawn.** The four entries stand
with their warnings, because the alternative — excusing them into `not_timed` —
would leave them unattributed to F5 and would fail this tranche's two gloss
declarations, which are the scarce thing in the whole plan.

**What is owed is a way for the ledger to say who was holding the clock.** The
file already separates seven phases precisely because "a single minutes figure
per record is gameable by re-labelling work"; it does not separate agents, and
after today that is the same defect one level further out. An `agent` field per
phase, or per record, is the obvious shape and this session did not add one:
adding a field to this file changes nothing about the corpus digest, but choosing
its vocabulary in the same session that first needed it is the allocation-decided-
at-F7 mistake ruling 51 records. **F6's, with the evidence already in the file.**

---

# FINDING 71 — recording Persia's vme slot as a failure put the per-region source-language floor OUT OF REACH for Persia, and the guard reports it as a note

## The arithmetic

`ingest.verify` on 2026-09-05, at 40 records:

```
region                now   still to come in F6/F7   ends at   floor
Arabia                  5   -- F5's two delivered        5       4  ok
East Asia               6   F6 vwp 1                     7       4  ok
Persia                  3   NONE                         3       4  <-- CANNOT REACH
Scandinavia             2   F6 vwp 2                     4       4  ok
South Asia              4   F5 vme 1 (Bhattotpala)       5       4  ok
Southeast Asia          4   none needed                  4       4  ok
Sub-Saharan Africa      3   F6 vwp 1 (local_language)    4       4  ok
```

**Persia's two F5 slots are both resolved.** The `verbatim_with_provenance` one
is spent on `persia-05-abnun`, delivered today. The `verbatim_machine_english`
one is the slot F5 recorded as a searched failure. **F6 and F7 place no further
Persia source-language slot**: F6 gives Persia one `published_translation_only`
and one `catalogue_record`, and neither counts toward this floor.

## Why this is a failure and not a shortfall, in the checker's own words

`ingest.verify` prints the distinction on the delivery line: *"A SHORTFALL is
progress and is reported here; an UNREACHABLE quota is a failure above, because a
target that can no longer be reached has already been missed and nobody
re-curates a record."*

**Scandinavia at 2 and Sub-Saharan Africa at 3 are shortfalls** — the slots to
close them exist and are still open. **Persia at 3 is unreachable**, and it
appears on the same line, in the same shape, as the two that are recoverable.

## Why nothing failed

`check_allocation` reads the per-region floor against **the PLAN**, and the plan
clears the floor in every region because the plan assumes its slots fill.
`F5_RULINGS.md` already records this under what F5 did not fix: *"a delivery-side
per-region floor check would fail the tree on two regions whose shortfall is
already recorded and cannot be recovered."*

**Today makes it three regions and changes the kind.** When that sentence was
written, the two regions below the floor were below it because of delivery
misses. Persia is below it because a slot was DECIDED to fail — a judgement made
in this session, on evidence, and recorded — and the guard cannot tell a decision
from a miss because it is not looking at delivery at all.

## The fix, named and not taken

**F6 can restore Persia to the floor by re-pointing one of its two Persia slots
to a source-language tier.** Ruling 73 established re-pointing as the legitimate
move and did it once already, and the supply argument has moved a long way since
F5's hunt refused this vein:

- **`parsigdatabase.com` and `noorlib.ir` have never been tested by a person.**
  Browser pass 2 is still owed. Every claim in this repository resting on
  parsigdatabase rests on a human pass nobody has made, and passes 1 and 3 both
  overturned negatives of exactly that shape (FINDING 69's neighbourhood, and the
  fetcher/structural asymmetry recorded in `F5_PART3_BROWSER_PASSES.md`).
- **F3 banked the Istanbul epitaph of Khurdad** and F5 removed its blocker:
  Sasanika carries transliteration and transcription at a stable per-record URL.
  One discrepancy stands unresolved — Sasanika dates it no later than Bahram V,
  fifth century, where F3's note has early 8th to late 10th.
- **`M2 I` and the already-banked `M 5794 I` are Turfan finds** and are EAST ASIA
  records under this corpus's findspot rule, not Persia. That mis-regioning is
  F6's to settle and it does not help Persia.

**This document does not re-point anything.** F5's allocation is closed on this
question, ruling 39 keeps the ruling out of a hunt document, and an allocation
edited to rescue a number the same session that missed it is the mistake ruling
51 records. What is owed to F6 is the decision, with this arithmetic in front of
it.

---

# What Part 3 has NOT ruled on

- **The candidate finding from `F5_CANDIDATES.md`** — that the vme tier's yield
  tracks a tradition's DIGITISATION history — is still not taken, and browser
  pass 1 has now narrowed it in a way that matters. The Bhaṭṭotpala original was
  unreachable to every fetcher and legible to a person on the first attempt. That
  makes the failure a fact about FETCHERS at least as much as about digitisation,
  and the finding cannot be written as stated. **It is Part 3's to rule on and it
  is not ruled on here.**
- **Whether `arabia-06`'s `ngy` dispute supersedes the restoration hedge in
  `F5_CANDIDATES.md` as a matter of record** — the record uses the `ngy` dispute
  and says why; the hunt document's version is corrected, not overruled.
- **The `ʿlmlṭ` / `Mṭl` discrepancy** in the Syllaeus edition. Recorded in the
  record, unrepaired, uncollated, and not attributed to either the edition or the
  paste.
- **The unlocated "two ṭ" sentence** in Petrantoni. Two project documents quote it
  as verbatim from p. 126 and a curator did not find it there. Until it is located
  or declared absent, `F5_CANDIDATES.md` and `F5_PART3_START.md` both carry a
  quotation with no established page.
