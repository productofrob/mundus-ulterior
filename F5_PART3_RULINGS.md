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

# Ruling 75 — South Asia's `verbatim_machine_english` slot is recorded as a FAILURE, and the cause is a capability of this project rather than a property of the source

## What was tried, in order, and what each attempt established

```
browser pass 1   Is Bhattotpala's Vivrti on Brhatsamhita 2.14 reachable?
                 YES. About ten printed lines on ONE page of the clean CC0
                 Dvivedi scan, leaf n101, printed p. 82, legible at zoom, with
                 a second open witness in Tripathi. The hunt's "the original
                 cannot be reached" was WRONG, and F5_PART3_BROWSER_PASSES
                 records it.

capture 1        Curator's paste. WRONG PASSAGE, and machine-read: the
                 geography-and-gnomon material, dozens of pages away, carrying
                 a `®` and a `#` where Devanagari numerals belong, an ASCII
                 pipe used as a danda, stray ZWNJ, and four sequences Devanagari
                 cannot form.

capture 2        Curator's paste. RIGHT PASSAGE -- verse 13's tail, verse 14,
                 the gloss, the two quoted verses, `iti || 14 ||` and the start
                 of verse 15 -- and still the text layer. Measured against the
                 SAME verse already held clean in record 40 from wisdomlib:
                 91.7% character agreement, nine divergences, including the
                 verse number 1 read as 9.

capture 3        Not attempted. The curator cannot type Devanagari.
```

## The two facts that compound, and neither alone would have been fatal

**NO KEYED TEXT OF BHATTOTPALA EXISTS ANYWHERE THIS PROJECT CAN REACH.** GRETIL
carries the Brhatsamhita and Brhajjataka in transliteration -- the mula only, not
Utpala. SARIT advertises source texts and its holdings did not render. Forty
archive.org items answer to `bhattotpala` and every one is a page-image edition.
The item's own search-inside is dead, so even locating a string inside it is
eyes-only. **This is a STRUCTURAL absence**, and by this session's own finding it
is the class of negative an automated fetcher reads CORRECTLY -- confirmed
independently on the Mojmal, whose missing search index defeated a person exactly
as it defeated the fetch.

**AND THE CURATOR CANNOT KEY DEVANAGARI.** Where no machine-readable text exists,
the tier's source text has to be typed by a person, and on this project that
person is one man who does not have the script.

Either alone is survivable. A keyed text would make the curator's script
irrelevant. A curator who could key it would make the absence of a digital
edition merely expensive. Together they close the slot.

## What was refused, and why each refusal was not close

**The model transcribing from a page image.** Offered and declined. A
`verbatim_machine_english` record has model-produced ENGLISH by construction --
that is the tier -- so model-produced SOURCE TEXT as well would leave nothing in
the record that a person had read. The tier exists to test the
machine-translation path against a human-verified original; a record with no
human-verified original tests the path against itself. This is also the second
time in one session the same line had to be drawn: record 40 already carries a
declared breach for a translation the model transcribed from an image, and doing
it again on a source text would be that error promoted from a note to a method.

**Accepting the OCR.** FINDING 53 forbids `_djvu.txt` as the page, and this item
is the reason the rule is not merely procedural: the corruption was MEASURED at
91.7% agreement against a known-good witness of one line.

**An IAST transliteration by the curator.** Would still require reading the
script.

## The acceptance test this ruling was nearly written on, and why it was void

A stopping rule was agreed in advance: if the curator's corrected mula verse
matched record 40's character for character, record 41 would be written; if not,
the slot would fail. **THE TEST WAS INVALID AND IT NEARLY RECORDED A FAILURE ON
EVIDENCE OF A FINDING.**

It compared a reading of **Dvivedi (VSS 18)** against record 40's text, which is
**Achyutananda Jha (2001)** by way of wisdomlib. Two editions. When the curator
reported no match, the reason was that **the Dvivedi page prints MORE characters
in the second pada than the Jha text does** -- a textual variant between two
printed editions, on the verse South Asia's records stand on, and Dvivedi is the
edition scholarship conventionally cites.

**One instrument, two questions, and the reassuring name on it: is this
transcription faithful, against do these two editions agree.** Written three
hours after FINDING 69 named that exact shape, by the session that named it.

## The variant is REAL and is NOT recorded, because nobody has read it

The divergence is reported by the curator from the page and **this project holds
no transcription of it**. Record 40 is not amended: it carries Jha's text,
correctly cited, and adding "another edition differs" without being able to say
HOW is a claim no reader could act on and no reviewer could check.

**What is owed is a reading of Dvivedi's mula verse 2.14**, which is two lines
rather than ten and would let both records carry the divergence the way
`eastasia-06` and `eastasia-07` carry their disagreement about the 643 embassy --
recorded in both and corrected in neither. It needs the same script the slot
failed on. **Recorded here as owed, and named as unfinished rather than
described as absent.**

## What this costs, and it is not hidden

```
F5 delivers          5 of 7          (was 6 of 7 on the strength of pass 1)
vme tier             5 of 10
corpus               54, RECORDED AS MISSED, not lowered
```

Ruling 69 recorded 56 as missed and did not lower `total_at_60` or
`by_tier_at_60`; 54 is recorded the same way and neither is lowered here either.

## Ruling 72's prediction is CONFIRMED and its mechanism is REFUTED

Ruling 72 predicted both `verbatim_machine_english` slots in F5 would fail, and
gave a mechanism: **English exists and was found.** Persia failed exactly that
way -- thirteen candidates, thirteen open English translations.

**South Asia did not.** No English translation of Bhattotpala's Vivrti exists,
and the negative is checkable because two near misses do: Utpala's Prasnajnana
IS translated and Sengupta translated the Khandakhadyaka WITH Utpala's
commentary, different works both. The prediction came true on the other side of
the record entirely -- not the translation, the ORIGINAL, and not its
reachability either, which pass 1 disproved.

**A pre-registered prediction that comes true for a reason its author did not
name is worth more than one that comes true for the stated reason**, and it is
worth more than the record would have been. It is also the only outcome in this
tranche that could have distinguished the two mechanisms, because it is the only
slot where they pointed in opposite directions.

---

# FINDING 72 — the tier needs a genre nobody translated, a text somebody keyed, AND a curator who can key it

`F5_CANDIDATES.md` proposes, as a candidate finding this document is asked to
rule on: the `verbatim_machine_english` tier's yield tracks a tradition's
**digitisation** history -- "East Asia has Kanripo; Persia and South Asia have
photographs of books."

**IT CANNOT BE WRITTEN AS IT STANDS, AND THE SESSION THAT WOULD HAVE WRITTEN IT
DISPROVED IT TWICE.** Browser pass 3 found DASI -- recorded as "the single most
valuable thing lost in this hunt" -- fully open to a person, CC BY 4.0, DOI'd,
9,102 keyed epigraphs, invisible only because a bot check stood in front of it.
That vein was never a digitisation problem. And browser pass 1 found the South
Asian "photographs of books" perfectly legible.

**The corrected claim has three conditions and the third one is new:**

```
1  A GENRE NOBODY TRANSLATED       FINDING 45's seam. Necessary, not sufficient.
2  A TEXT SOMEBODY KEYED           East Asia has Kanripo. Bhattotpala has
                                   nothing: GRETIL the mula only, SARIT nothing,
                                   forty archive.org items all page images.
3  A CURATOR WHO CAN KEY IT        Where condition 2 fails, the source text must
                                   be typed by a person, and that person must
                                   have the script. THIS PROJECT'S CURATOR DOES
                                   NOT HAVE DEVANAGARI.
```

**Condition 3 is a fact about this project and not about the world**, which is
what makes it worth naming rather than embarrassing to name. It is also the only
one of the three that no amount of hunting could have discovered: it is
invisible until a slot reaches capture and it does not appear in any candidate's
provenance. F5's hunt could not have found it, ran a full battery, and refused
the right candidates for the wrong reason.

**And it separates two words this project has been using as one.** REACHABLE is
what pass 1 and pass 3 measured. KEYED is what the Mojmal and Bhattotpala lack.
The hunt's failures were written as reachability failures and at least two of
them were keying failures -- which is FINDING 69's shape a third time, on a third
pair of words.

**What follows for F6 and F7.** They place no `verbatim_machine_english` slot, so
nothing in the remaining plan depends on this. What does depend on it is any
future tranche that tries to fill one: **the question to ask of a candidate is
not "can this be reached" but "can this be reached AND is it keyed AND can we key
it if it is not"**, and the third clause is answered by looking at the project
rather than at the source.

---

# Rulings 70, 71 and 72, READ against the run of 2026-09-05

*Run `20260905T183224+0000-retrievable_chunks_with_distractors.json`. Index 507
chunks, depth 507, `voyage/voyage-3.5`, 44 pairs over 41 units, BASELINE arm, no
`--fuse` (ruling 65). Unit recall@6 0.805 (33/41), MRR@10 0.621.*

*Comparator: `20260904T081155+0000`, the immediately preceding archive on the
same view. **IT PREDATES RECORD 36.** `eastasia-07-tang-huiyao` appears nowhere in
it, so this diff measures FIVE records entering the index — 36 through 40 — and
not four. Every attribution below is made from `beaten_by` chunk ids, which name
records directly, and not from the diff.*

---

## Ruling 70 — CONFIRMED, and by a wider margin than it asked for

**The prediction:** *"after F5's two Arabia `verbatim_with_provenance` records
enter the index, at least one of them appears in `vimose-runes`'s `beaten_by`."*

**The result: FOUR of the six.**

```
vimose-runes    rank 7 -> 16      recall@6 False -> False

beaten_by
  1. arabia-05-ruwafa::translation::000        <- F5, and now the CEILING
  2. arabia-05-ruwafa::translation::002        <- F5
  3. arabia-05-ruwafa::original::002           <- F5
  4. arabia-04-jabal-dabub::original::000
  5. scandinavia-05-thorsberg-chape::translation::000
  6. arabia-06-syllaeus::translation::000      <- F5
```

Ruwāfa took the top three places outright and **displaced `arabia-04-jabal-dabub`
as `best_other_doc_chunk_id`**, which is the ceiling `floor.json`'s
`superseded_diagnosis` recorded and which the F4 archive still had. The ruling's
falsification condition — *"Neither new Arabian record reaches the six"* — is not
close: both reached, and one of them owns most of the interval.

**THE COST THE RULING REGISTERED IN ADVANCE IS NOW MEASURED AT NINE RANKS.** It
wrote: *"curating Arabia measurably damages a Scandinavian gold case that is
already a known failure, and nothing in the allocation accounts for a region's
records degrading another region's retrieval."* `vimose-runes` is a known failure
in `floor.json` and it has gone from 7 to 16 in one tranche.

**Three of the four crowding chunks are ENGLISH** — two Ruwāfa translation chunks
and one Syllaeus translation chunk. The class doing the damage is not "Arabian
inscription in its own script"; it is the record, through whichever chunk ranks.

## Ruling 71 — NOT CONFIRMED, and the blind spot it declared is what lets us say so cleanly

**The prediction:** *"F5's East Asia `verbatim_machine_english` record appears in
`beaten_by` for at least one of `china-describes-rome-houhanshu` and
`china-describes-rome-weilue`."*

**`eastasia-07-tang-huiyao` appears in NEITHER.** Both intervals are identical
and are made of other East Asian records plus one Southeast Asian site:

```
china-describes-rome-houhanshu   rank 8 -> 8     ceiling eastasia-01-weilue::translation::000
china-describes-rome-weilue      rank 9 -> 10    ceiling seasia-02-oc-eo-site::original::000

both beaten_by
  1. eastasia-01-weilue::translation::000
  2. seasia-02-oc-eo-site::original::000
  3. eastasia-02-hou-hanshu::translation::000
  4. eastasia-04-jingjiao-stele::translation::001
  5. eastasia-04-jingjiao-stele::original::000
  6. eastasia-05-liangshu-qin-lun::original::000
```

**The blind spot was declared before the run and it separates the two pairs.** The
ruling said: *"if the ranks fall while the record is absent from both intervals,
that is the recall window and not evidence against FINDING 43."*

- **houhanshu held at 8.** The record is absent from the interval AND THE RANK DID
  NOT MOVE. The blind-spot clause covers ranks that FALL; this one did not. **This
  is a clean negative** — on this pair the mechanism did not operate at all.
- **weilue fell 9 → 10.** Record absent, rank fell by one. **This is exactly the
  declared blind spot and is unreadable in either direction**, as pre-registered.

**AND THE RECORD IS NOT RETRIEVAL-INVISIBLE, WHICH IS WHAT MAKES THE NEGATIVE
INTERESTING RATHER THAN EMPTY.** It crowds two other targets:

```
probe-tamil-akananuru-en    rank 6     beaten_by eastasia-07-tang-huiyao::original::000
adulis-throne-leuke-kome    rank 31    beaten_by eastasia-07-tang-huiyao::original::000
```

A Literary Chinese dossier on Byzantium is crowding a Tamil-to-English probe and
an Aksumite throne inscription, and is not crowding either Chinese-describes-Rome
pair. **The mechanism operated; the prediction pointed it at the wrong targets.**

**One thing this run cannot tell us, and it is owed.** NO GOLD RANKING PAIR NAMES
RECORD 36 AS A TARGET. Its own retrievability is untested by this instrument. A
pair written now would fall under ruling 54 — written after the record was in the
index, scored but not citable as evidence that the tranche improved retrieval.

## Ruling 72 — a correction to how ruling 75 reported it

Ruling 75 wrote that ruling 72's *"prediction is CONFIRMED and its mechanism is
REFUTED."* **That is more generous to ruling 75 than ruling 72's own text
allows**, and the correction belongs here rather than in a result document.

Ruling 72 enumerated its falsification conditions in advance, and one of them
reads: *"Persia or South Asia fails on SUPPLY rather than on found English: that
is FINDING 38's problem again and evidence for neither, which is ruling 53's
third outcome and is reported as such rather than folded into a binary."*

South Asia's slot failed on **neither** found English **nor** supply. The material
exists, is reachable, is legible, and is not keyed anywhere — and the curator
cannot key it (FINDING 72). **That outcome falls outside all three branches ruling
72 named.** The honest report is not "prediction confirmed, mechanism refuted" but
**ruling 72's enumeration was incomplete, and the case that arrived is one it did
not anticipate.** Persia confirms it exactly as written; South Asia is off its
map.

---

# FINDING 73 — nine pairs fell, none improved, and the headline number did not move

## What the run measured

```
                       improved   unchanged   FELL
pairs (44)                    0          35      9

pair-level recall@6      old 32/44        new 32/44
pairs crossing the window                 NONE
```

**Five records entered the index and made nine gold pairs worse and none better.**
Not one pair crossed the recall@6 boundary, so **the number a reader meets is
unchanged**, and `ALL recall@6 0.727` in the cohort table is the same as it was.

## What actually moved is the margins, and two cases are now ON the edge

```
tc-jabal-dabub              3 -> 6     slack to rank 6: 0
probe-tamil-akananuru-en    5 -> 6     slack to rank 6: 0
```

**One more record of the wrong kind and either leaves the window.** Three chunks of
`arabia-06-syllaeus` are already inside `tc-jabal-dabub`'s interval, and
`eastasia-07-tang-huiyao` is inside `probe-tamil-akananuru-en`'s. These are not
hypothetical crowders; they are this block's own records, and F6 places seven more.

## The full fall list, with the crowder named where `beaten_by` names it

```
vimose-runes                              7 ->  16    4 of 6 are F5 Arabia
bronze-heracles-verethragna-from-mesene  58 ->  86    2 chunks of persia-05-abnun
thorsberg-chape-niwajemariz              16 ->  24    persia-05-abnun
muziris-cargo-akananuru                 319 -> 333
tc-jabal-dabub                            3 ->   6    3 chunks of arabia-06-syllaeus
adulis-throne-leuke-kome                 28 ->  31    eastasia-07-tang-huiyao
china-describes-rome-weilue               9 ->  10
aksum-trade-adulis                       38 ->  39
probe-tamil-akananuru-en                  5 ->   6    eastasia-07-tang-huiyao
```

## This GENERALISES ruling 70 past what it claimed, in the direction nobody wrote down

Ruling 70 framed the damage as **cross-regional** — *"a region's records degrading
another region's retrieval"* — and registered that as the surprising cost. The run
says same-region crowding is at least as strong:

```
arabia-06-syllaeus  crowds  tc-jabal-dabub                   Arabia -> Arabia
persia-05-abnun     crowds  bronze-heracles-verethragna      Persia -> Persia
persia-05-abnun     crowds  thorsberg-chape-niwajemariz      Persia -> Scandinavia
arabia-05/06        crowd   vimose-runes                     Arabia -> Scandinavia
eastasia-07         crowds  probe-tamil-akananuru-en         East Asia -> South Asia
```

**Curating a region damages that region's own gold cases**, and `tc-jabal-dabub`
— an Arabia translation case crowded to the window's edge by an Arabia record
curated the same week — is the sharpest instance in the table.

## And one record crowds nothing at all

`southasia-05-brihatsamhita` appears **nowhere in this run**: not as a target, not
in any `beaten_by`, not as any pair's `top_doc` or ceiling. It is in the index —
`run_embed` embedded its Sanskrit chunk — and it surfaces in no interval this
gold set can see. Whether that is a property of the record, of Sanskrit against
this embedding model, or of a gold set that asks it nothing, **this run cannot
say, because no pair targets it.**

## Why this is the same shape as everything else this session found

`recall@6` is unchanged at 32/44 and every margin behind it eroded. A reader
checking whether F5 hurt retrieval would read the aggregate, find it flat, and be
wrong. **An aggregate that reads reassuringly while the thing underneath degrades**
is FINDING 51's shape, FINDING 64's shape, FINDING 65's shape, and FINDING 69's
shape — and it is now measured on the retrieval side, where the project's central
claim actually lives.

**Not gated, and deliberately not.** Nothing here fails a check, and nothing should
be made to: the margins are real information and a gate on them would be a
threshold nobody has evidence for. What is owed is that **F6 reads this table
before it curates**, because seven more records enter on top of two gold cases
sitting at rank 6.

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
