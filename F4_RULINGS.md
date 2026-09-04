# Rulings 53 to 56 — declared 2026-08-31, in F4, before record 31

*Date taken from the host, not from another document: `date -u +%F` printed
`2026-08-31`. FINDING 34 is four days old and cost eleven documents.*

*All four are recorded BEFORE the first candidate is examined. That is ruling
39's argument for the sixth time in this block, and F4 is the session where it
stops being a habit and becomes the instrument: two of these rulings are
PREDICTIONS, and a prediction written after the run is an explanation. This
project already has a sentence about the difference.*

---

## Ruling 53 — F4 curates against the allocation AS WRITTEN, and the `verbatim_machine_english` ruling is DEFERRED to F4's close with its conditions declared today

**`data/corpus_tiers.json` is not changed. `ingest.fidelity.check_allocation`
is not changed. F4's three `verbatim_machine_english` slots stand, an unfilled
one is a SHORTFALL — which `check_delivery` already reports as progress rather
than failing — and the ruling FINDING 41 asks for is made at F4's close, on
Ge'ez evidence, against conditions written here before the hunt begins.**

### Why the ruling is better made after F4 than before it

FINDING 41 is correct about what it saw. It saw Persia and Scandinavia.

```
Kartir KKZ/KNRb                    English on avesta.org and UCI Sasanika
the Pahlavi corpus (five works)    all Englished
M 5794 I                           Skjaervo, free PDF, manichaeism.de
the Istanbul epitaph of Khurdad    de Blois 1990, quoted on en.wikipedia
```

Four disqualifications, one region, one scholarly tradition — and Middle
Persian epigraphy is among the most thoroughly Englished bodies of text in
existence, because the people who learned to read it in the twentieth century
published in English. Scandinavian runology is the other one. F3 tested the
tier where the tier is hardest to fill and reported the result as a property of
the tier.

**The allocation's own sentence, written in F3 before any of this, anticipated
exactly that:**

> *"Africa is at one source-language record of four and Ge'ez has no published
> translation for most of what is open, so it is the second-hardest region and
> the second-largest `verbatim_machine_english` draw."*

That sentence is a prediction and F4 is its test. Re-cutting the mix now
discards the test to act on one tranche of evidence from the two regions least
able to produce it.

### What is being deferred, and what is NOT

Deferred: whether `verbatim_machine_english` is allocated at all, and whether
`by_tier_new`'s ten becomes a floor of the form *"at least N, discovered"*.

Not deferred, and not weakened: **FINDING 41's central claim stands
today.** A curator establishes *"I did not find an English translation"*, which
is a property of the search. Nothing in F4 makes that false. What F4 can settle
is whether the property of the search is stable enough across a tradition to
plan against — which is a different question, and the one the mix actually
needs answered.

### The conditions, declared now so the close reads as a result

**NARROWS** — FINDING 41 becomes *"`verbatim_machine_english` cannot be
targeted from English-language scholarship"*, a rule about where a hunt looks
rather than about the tier: Sub-Saharan Africa delivers **2** honest vme
records, each with its failed English search written down per the anti-loophole
below.

**STANDS AS WRITTEN** — the tier is a residue and the mix re-cuts at F5 with
two tranches of evidence: Africa delivers **0 or 1**, and the disqualifying
reason is again *somebody has already translated this well and posted it*.

**NEITHER, AND SAY SO** — Africa delivers 0 or 1 for a different reason: no
open transliteration, a text outside the window, a source that refuses
automated fetching. That is FINDING 38's supply problem, not FINDING 41's
search problem, and reading it as either would be reading the number without
the reason. **Recorded as a third outcome precisely so the close is not forced
into a binary it can satisfy by choosing.**

East Asia's single vme slot is evidence toward none of the three. One slot in a
tradition with its own enormous English-language scholarship decides nothing,
and its outcome is reported without being read.

### The anti-loophole, which is the part that makes the test honest

**F4 can reach two vme records by not looking, and every check in this
repository would pass.** `derive_record_tier` reads an empty
`translation_source`; an empty field is what a thorough search and no search
both produce.

So: **a `verbatim_machine_english` record curated in F4 must carry, in its own
`notes`, the English-language search that failed — the named sources consulted,
not a count — and any English found must be cited with its URL beside the
reason it was refused as a `translation_source`.** A record whose note says
only *"no English translation found"* is not evidence for any of the three
outcomes above, and F4's close must say so rather than count it.

This is `floor.json`'s `a_named_sweep_must_actually_fail_the_rule` in the
curator's chair: **a tier that can be reached by doing less work is a place to
put records nobody searched for.**

### What it costs to be wrong here

If the deferral is wrong, F5 re-cuts having spent F4's vme hunting time — the
cost F3 measured at ~29 minutes in retired rows. If the re-cut were made today
and wrong, the mix loses its only quota on the tier that turns on the
machine-translation path, and `verse` and `documentary` stay at n=1 with
nothing scheduled to move them. **The recoverable error is the one that is
taken.**

---

## Ruling 54 — a record's ranking pair and its gold case are written in the SAME COMMIT as the record

**No record enters the corpus in a commit that does not also add at least one
ranking pair naming it, or a written reason in that commit that it cannot carry
one. The precedent is in this repository: `ingest/verify.py` check 9 is raised
in the same commit as the records it counts, never in advance and never
later.**

### The defect is structural and it repeats without a rule

FINDING 43, measured:

```
F3 added six records.
Ranking pairs for those six records:                            0
Gold cases written against them that have ever been executed:   0
Pairs that moved:  muziris-cargo-akananuru 310 -> 313
                   tc-jabal-dabub            2 -> 3
                   vimose-runes              3 -> 7   (out of recall@6)
```

**Every tranche adds competition to queries written before it and adds no query
of its own.** So the instrument gets monotonically more pessimistic as the
corpus improves, and `recall@6` at 60 records is partly a measure of how much
the corpus grew. That is not a bad tranche. It is the measurement design, and
F4 inherits it unchanged unless the rule changes.

### Why the same commit and not the same session

A pair written after the ranking run is a pair written knowing the rank. There
is no accusation in that sentence and no need for one: the anchor token, the
phrasing and the expected document are all choices, and a person who has just
seen a record land at rank 9 writes a different query than one who has not.
`archived_status` and `superseded_diagnosis` exist in this project because the
remedy for that class of problem is ORDER, recorded, not intention.

The commit is the only boundary git can prove.

### F3's six, which can never be paired honestly, are named rather than fixed

The six records of F3 are already in the index. Any pair written for them now
is written after their run. **They are given pairs anyway — a corpus where six
records are invisible to the ranking check is worse — and each is stamped
`written_after_the_records_entered_the_index: true`, is excluded from every
before/after claim, and may not be cited as evidence that F3 improved
retrieval.** That is `excluded_by_rule`'s shape: excluding by a recorded rule
is a diff, and excluding by making a row vanish is not.

**The flag is absent from F4 onward, and its absence is the claim.**

### What this buys F4 that F3 could not have

F4 measures both what it added and what it cost. F3 measured only the second,
and *"six records entered the corpus and the only thing any instrument here can
say about them is that two older pairs moved down"* is a sentence about the
instrument, not about the records.

---

## Ruling 55 — the East Asia prediction, registered before the first East Asian candidate is examined

**Prediction: when F4's East Asian records enter the index, both
`china-describes-rome` pairs move DOWN, and `china-describes-rome-weilue` is
the more likely of the two to leave the top 6.**

### The numbers, read from the archive rather than from a document

`eval/ranking_runs/20260831T150406+0000-retrievable_chunks_with_distractors.json`,
view `retrievable_chunks_with_distractors`, index 460 chunks:

```
china-describes-rome-houhanshu   rank 4   recall@6 true    anchor_points_home false
china-describes-rome-weilue      rank 5   recall@6 true    anchor_points_home false
vimose-runes                     rank 7   recall@6 false   anchor_doc
                                                    scandinavia-05-thorsberg-chape
```

### The mechanism, which is FINDING 43's and is not new here

`vimose-runes` fell from 3 to 7 when a record arrived that was its near
neighbour in language, script, period, object type and country. F4 plans two
`verbatim_with_provenance` and one `verbatim_machine_english` East Asian
records, which will be Literary Chinese `lzh` texts **about Rome** — the same
language, the same script, the same period and the SAME SUBJECT as both pairs'
queries.

And **neither pair points home.** `anchor_points_home` is false for both: their
queries carry no rare token resolving to their own record, which is precisely
the condition under which `scandinavia-05-thorsberg-chape` took
`vimose-runes`'s place. Two ranks and one rank of headroom, against three new
competitors written to be about the same thing.

`weilue` is named as the likelier to fall because it sits one rank lower and
because `eastasia-01-weilue` is the record whose Chinese chunk has already been
shown to lose the model's attention to its own English (45 of 45, FINDING 13).

### What falsifies it

**Both pairs hold or improve.** Then FINDING 43's mechanism is narrower than
same-language-same-subject — it is about near-duplicate OBJECTS, a chape beside
a spearhead, not about texts that discuss one another's topic. That is a
smaller and more useful finding than the one currently on file, and it is only
available because the prediction was written first.

**One holds and one falls, and it is `houhanshu` that falls.** The mechanism is
real and the ordering reasoning is wrong, which would say the anchor-token
story is doing less work than the rank gap.

### What the prediction is NOT

It is not a reason to curate fewer East Asian records: the region is at two
source-language records against a floor of four, and ruling 51 put it in F4 for
that reason. It is not a regression claim — a pair moving down inside the top 6
breaks no gate, and both pairs are outside the floor's `required_cases`. And it
is a prediction about a dense retriever measured by one diagnostic, so a
confirmation is evidence and not a proof of cause.

**It is available today, costs nothing, and F3 could not make it.**

---

## Ruling 56 — the quoted-from-original quota splits in two, because the two questions are not one question

**`min_expect_quoted_from_original_cases_at_60: 6` counts ONLY cases written
against records that HOLD a `reference_translation`. Cases on
`verbatim_machine_english` records are counted on their own line,
`vme_quotation_cases`, which every sub-tranche must DECLARE, which is capped by
that sub-tranche's vme slots, and which carries no aggregate minimum.**

### FINDING 40's evidence, restated because the ruling depends on it

On a record carrying both an `original_text_excerpt` and a
`reference_translation`, both chunks are retrieval-eligible, both are in front
of the model, and the assertion records **WHICH ONE** the quotation came out
of. That choice is the defect the assertion was invented to see:

```
chinese-da-qin, 16 archived runs:  45 of 45 resolved quotations came from the
                                   English, while the source chunk sat at [S1]
```

On a `verbatim_machine_english` record there is no second chunk. The machine
English lives in `current_translations`, which is not a corpus field, so a
quotation of it cannot resolve to characters on disk at all. The assertion is
then satisfied by **any resolved quotation whatsoever** — which
`expect_min_resolved_quotes: 1` on the same case already required.

**Six of six is four of the first question and two of the second.**

### The direction is what makes this a ruling rather than a note

The plan predicts `verbatim_machine_english` becomes the common tier. Every vme
record supplies a quotation case that passes by construction. **So the quota
gets easier to satisfy as the thing it measures gets harder to observe** — and
it drifts silently, because the count is the only thing anyone reads and the
count is the only thing G3 will read.

A measure that improves while its subject worsens is a measure on its way to
becoming decoration.

### The tier rule, held in code with its reason

```python
QUOTATION_CHOICE_TIERS = frozenset({"verbatim_with_provenance"})
```

A case that asks WHICH chunk was quoted requires two retrieval-eligible chunks,
an original and its published translation, and exactly one tier holds both.
`published_translation_only` has no original to prefer;
`catalogue_record` has neither; `verbatim_machine_english` has no published
translation. This is `GLOSS_CAPABLE_TIERS`'s shape, one assertion over, and it
is in code for the same reason: **it is a rule and not a number, and a mutation
has to be able to break it.**

### The vme line has no floor, and the reason is ruling 53

A minimum on vme quotation cases is a quota on cases that can only exist on
records of a tier this session has just declined to decide the targetability
of. **Declaring one today would re-target the residue through a different
field.** So the line is declared, capped by capacity, required to be PRESENT in
every sub-tranche — an absent field is a failure, not a zero — and reported.

Said plainly, because a zero in a guard is usually a guard nobody wrote: **the
teeth on this line are the presence check and the capacity cap, not the
minimum.** The number that belongs there is F5's to set, after ruling 53's
deferred ruling, and it is owed.

### What is NOT done

**The six is not lowered.** Lowering a bar because the cases behind it turned
out to be weaker is a different ruling, and the number that belongs at 60 is
not known from four. The allocation already writes seven choice cases across
F3-F5 against a minimum of six, so the split costs nothing that was not already
budgeted.

**No delivered number is rewritten.** F3's row keeps the 2 it declared, and
gains the `vme_quotation_cases: 2` it delivered under a distinction that did
not exist when it was written. Restating a delivered plan to match what
happened is the move this project refuses everywhere else.

**The gold set is now counted AS TWO LINES, and that is the part with teeth at
G3.** This paragraph said something false when it was first written, and the
correction is left in place rather than tidied away, because it is the ruling's
own argument happening to the ruling.

It said the six lived only in the allocation plan and that nothing counted the
cases that exist. **`eval/test_answer_eval.py` has counted them since F1**, in a
test whose own heading is *"the quoted-from-original quota, counted rather than
assumed"* — written precisely so the number could not be transcribed into a
document. It counted six.

So the defect was never that nobody counted. **It is that the count was right
and the READING was wrong, inside the suite built to stop a number being
wrong** — which is a sharper statement of FINDING 40 than FINDING 40 made, and
it means the misreading was sitting in the file nearest to G3.

Both counters are now split, and the split is **imported from
`ingest.fidelity`** rather than recomputed in each place, for
`SOURCE_LANGUAGE_TIERS`' own reason: a rule spelled out twice is a rule that
disagrees once. For one turn today there really were two counters and they
really did disagree — `ingest.verify` read four and the gold suite read six.

Today both read **4 asking WHICH chunk / 2 asking WHETHER anything resolved**,
which is the number FINDING 40 says a reader should have.

**And the reachability guard was reachable through the wrong records.** It
counted `verbatim_machine_english` slots toward a quota those records cannot
satisfy, reporting a target as attainable through the tier that cannot attain
it. Its ceiling is now `QUOTATION_CHOICE_TIERS`.

---

# The sentences that travel, from F4's opening

**FINDING 41 was measured in the two traditions most thoroughly translated into
English, and reported as a property of the tier.**

**A tier that can be reached by doing less work is a place to put records
nobody searched for.**

**A pair written after the run is a pair written knowing the rank, and the
commit is the only boundary git can prove.**

**Two pairs sit at rank 4 and rank 5, neither points home, and three records
about the same subject in the same language are about to enter the index. That
sentence is worth more today than any sentence about it will be worth at F4's
close.**

**A measure that improves as the thing it measures gets harder to observe is a
measure drifting toward decoration, and it drifts silently because the count is
the only thing anyone reads.**

---
---

# Rulings 57 and 58, and FINDINGS 44 to 46 — declared 2026-08-31, LATER THE SAME SESSION, and still before record 31

*Rulings 53 to 56 were written before the hunt. These were written after it and
before any record was curated, and the gap between those two moments is the
only reason they can be trusted: the hunt produced candidates, not numbers. No
record exists, no rank has moved, no suite has been run against a changed
corpus. Ruling 39's line is that a rule written after the first sub-tranche is
a rule written by someone who has seen what the first sub-tranche did to the
numbers. Nobody has seen anything yet.*

*What the hunt DID produce is the answer to ruling 53's own question, four
hours early and in a shape ruling 53 did not have a name for. That is recorded
as FINDING 45 rather than quietly folded into the ruling it embarrasses.*

---

## Ruling 57 — `verbatim_machine_english` means NO ENGLISH A CURATOR CAN REACH, and every record in the tier states the boundary of its own search

**The tier's written definition in `data/corpus_tiers.json` — *"no published
English translation"* — is replaced by *"no English translation reachable by
the curator, with the search recorded."* Every `verbatim_machine_english`
record carries, in its `notes`, the named sources consulted and the boundary
where the search stopped. A record that does not is not in the tier.**

### This is FINDING 41's argument accepted rather than resisted

FINDING 41's central sentence has been treated for a session as a problem to
be worked around:

> *"What a curator can actually establish is 'I did not find an English
> translation.' That is a property of the SEARCH, not of the text."*

**It is not a problem. It is the definition.** The written definition claims
something no curator has ever been able to establish and no check has ever
verified: `derive_record_tier` reads whether a record cites a
`translation_source`, which is a fact about the record, and the JSON above it
claims a fact about the world. Those have never been the same claim, and the
gap between them is where three sessions of confusion has lived.

Once the tier says what a curator can actually establish, it becomes
targetable — which is the thing FINDING 41 said it could not be — because the
search has a shape and a curator can aim at where the shape is thin. FINDING 45
is what that looks like in practice.

### The evidence that forced it, and it is decisive

Three East Asia candidates have no English translation findable anywhere
online: the Tang Huiyao, the Cefu Yuangui and the Taiping Huanyuji. Checked
against Hirth 1885's own contents rather than a bibliography, against Hirth &
Rockhill 1911, Legge 1888 and Yule 1866, against Fordham, Silk Road Seattle,
silkroadfoundation.org and silk-road.com, and against eight databases.

And **Leslie & Gardiner, *The Roman Empire in Chinese Sources* (Rome, 1996), is
the standard translation-corpus of exactly this material, print only, and
nothing available to this project can establish whether it covers them.**

Under the old definition those three records are uncurable, and they are
uncurable for a reason no amount of work removes: to establish "no published
English translation" a curator would have to read every book. Under the new
one they are curable, and each one states where it looked and where it
stopped, which is a claim that can be checked and, if wrong, corrected by
naming the book.

**A definition that can only be satisfied by omniscience is satisfied in
practice by whoever searched least.** That is the loophole ruling 53's
anti-loophole was written against, and this closes it at the definition
instead of patrolling it at each record.

### It also describes F3's own records correctly for the first time

`seasia-06-kedukan-bukit` and `seasia-07-talang-tuo` qualified because the
English that circulates for them is unattributed. FINDING 41 recorded that
their *"JUSTIFICATION is not stable — the day somebody attributes that
translation, the records' written reason becomes false while every check in
this repository continues to pass."*

Under ruling 57 the justification is stable, because it is a different
sentence. It no longer says *nobody has translated this*; it says *this curator
searched here and here and found no attributable English*. That statement does
not become false when somebody attributes the translation. It becomes
INCOMPLETE, and the record's own note says where to look to complete it.

### The anti-loophole, restated, because the definition change makes it load-bearing

Ruling 53 already requires the failed search in the record's notes. Ruling 57
makes that requirement the tier itself rather than a discipline attached to it:

- **Named sources, not a count.** "I searched extensively" is not a search.
- **Any English found is cited with its URL beside the reason it was refused**
  as a `translation_source` — paywalled, print-only, unattributed.
- **The boundary is stated.** "Print-only monographs were not consulted" is a
  legitimate boundary and a useful one. An unstated boundary is not.

### What is NOT decided

The mix is untouched. The allocation is untouched. `check_allocation` is
untouched. Ruling 53's deferral stands and its three outcomes still get their
reading at F4's close — with FINDING 45 as a fourth, which is the whole reason
the third outcome was written.

**And no check enforces this.** Whether a note names its sources is a judgement
about prose, which is `why_gloss_capability_is_DECLARED`'s situation exactly
and gets the same answer: declared, visible in the record, and readable by a
human who wants to argue with it. A checker that counted source names would be
satisfied by a list.

---

## Ruling 58 — Sub-Saharan Africa's source-language floor is being met in GREEK, and that is declared rather than discovered

**F4 curates Silko at Talmis and the Monumentum Adulitanum II as Africa's two
`verbatim_with_provenance` records. Both are Greek. With
`africa-03-periplus-adulis` that puts three of the region's four required
source-language records in the language of the Roman Empire, and this ruling
says so in advance, in the file, because no check in this repository can.**

### What the checks can and cannot see

```
ingest.fidelity  min_source_language_records_per_region  4
                 counted over verbatim_with_provenance + verbatim_machine_english
                 There is no clause about WHICH language.
```

Four Greek records would satisfy the per-region floor, `check_allocation`,
`check_delivery` and `check_target_mix` — every one of them green — and leave
Sub-Saharan Africa's source-language corpus written entirely in the language of
the empire the project exists to measure distance from. The project
instructions ask for *"relevant local, non-English sources from the regions
above."* **Greek from an African findspot is a non-English source and it is not
a local one, and no field in this repository holds that distinction.**

This is ruling 49's shape one dimension over: a rule that could not see the
data it was written to protect. `min_source_language_records_per_region` was
written to stop an aggregate being met inside two regions. It cannot stop a
region being met inside one empire.

### Why the check is not changed today

The third option was a per-region rule that refuses a floor met entirely in
Greek or Latin. It was refused for ruling 53's reason, one field over: it
changes `corpus_tiers.json` and `check_allocation` together, mid-tranche, on
one tranche of evidence, and this session has already declined to do exactly
that for the tier. **Two mid-tranche re-cuts of the same file, in the same
session, in opposite directions, is a session editing its own instruments to
fit what it found.**

It is owed, it is named here, and F5 has both this and ruling 53's deferred
ruling in front of it — which is one re-cut with two tranches of evidence
instead of two re-cuts with one each.

### What the Greek records are, and why they are not a consolation prize

Silko writes Greek in a Roman temple and calls himself `βασιλίσκος`, the
diminutive the Greco-Roman world used for client kings on its edge, and says
God gave him the victory. The Adulis throne inscription has an Aksumite king
listing conquests, recording that he made the trade roads safe by land and sea,
and dedicating the throne **to Ares**. Neither is a Roman text. **Both are
Africans using the empire's language and the empire's gods to say something
about themselves**, which is a sharper statement about influence than a local
language would have made, and it is the reason these two were chosen over the
Dongola Creed and the Qasr Ibrim epitaphs.

That is an argument for these records. **It is not an argument for the floor
being met this way, and the two must not be allowed to blur.** Said here so
that nobody at G3 reads three Greek records as four regions' worth of local
source text.

### The Ge'ez route is closed for a stated reason, not an unstated one

Littmann's *Deutsche Aksum-Expedition* IV (1913) is public domain, downloadable
in full, and prints Aksumite inscriptions in original script with
transliteration and **German translation only** — the exact
`verbatim_machine_english` profile the mix wants. Its contents were read
through. **Every text in it that touches Rome is either Ezana, which this
corpus already holds, or Sembrouthes.** Kaleb (RIÉ 191) and Wa'zeb (RIÉ 192)
are not in Littmann; they are in the RIÉ, which is not open, and the 2019
Drewes/Kropp edition is French and print-only.

**So Ge'ez fails on the ROME criterion, not on the translation criterion.**
That is FINDING 38's supply problem and not FINDING 41's search problem, and it
is ruling 53's third outcome — NEITHER — arriving in the region ruling 53 named
as its test. **The third outcome was written so the close could not be forced
into a binary it could satisfy by choosing, and it earned itself within four
hours.**

---

# FINDING 44 — the tier does not distinguish "nobody translated it" from "nobody can", and the best evidence this project will ever find is for the second

The Hamadab stela of Amanirenas and Akinidad — British Museum EA1650,
excavated 1914 south of Meroe, 42-45 lines of Meroitic cursive, showing the
queen and prince of the Roman war of 25-21 BC above a relief of bound
prisoners. The British Museum's own record states that the word `Areme` in the
text is thought to represent **Rome**, and that the inscription may document
the Kushite raid on Roman Egypt of 24 BC.

**It has the strongest "no English translation exists" evidence this project
will ever assemble.** Four independent authorities say so on the record:

```
British Museum, object EA1650      "remains undeciphered"; meaning "far from clear"
Fontes Historiae Nubiorum II       "no consecutive translations can be provided"
Rilly, UCLA Encyclopedia of        "no more than a hundred words can be
  Egyptology                        translated with some certainty"
ACL 2025, Towards Ancient          available translations are "constrained to
  Meroitic Decipherment             titularies, toponyms, and anthroponyms"
```

**And it is the wrong record, for a reason the tier's definition cannot
express.**

## The three mechanisms, which one field is carrying

`verbatim_machine_english` is derived from an empty `translation_source`. That
one absence is produced by three completely different states of the world:

1. **Nobody has published an English translation** — the tier as intended.
   Machine translation is available and the Part 6 path does real work.
2. **An English translation exists somewhere a curator could not reach** —
   ruling 57's case. Machine translation is available and does real work; the
   record's note says where the search stopped.
3. **No translation exists in any language because the language is not
   understood.** Machine translation is not available in any meaningful sense,
   and the path produces fluent output with no relationship to the source.

**The pipeline cannot tell these apart, because the field it reads is empty in
all three.** A Hamadab record would send Meroitic through `resolve_english`,
get back confident English, attach it to a citation resolving to real
characters in a real record, and every check in this repository would pass. The
`verse` and `documentary` confidence profiles — at n=1, and load-bearing since
the first vme records landed — would score it.

**That is the gloss arm's target output produced by the corpus rather than by
the model.** The one thing this project has built machinery to catch, arriving
through the front door with a British Museum accession number attached.

## What is done, and what is deliberately not

The record is **not curated**, and Meroitic is recorded here as a class rather
than as one refused candidate: Dakka (FHN II 173) and Kharamadoye (REM 0094)
fall the same way, and the whole Meroitic corpus is behind them.

**The tier is NOT given a fourth state today.** A distinction invented in the
hour its first case appeared is a distinction fitted to one record — FINDING
32's precedent, and ruling 53 has already declined one mid-tranche re-cut of
this file. What is owed, and stated so it is not re-derived: **the tier needs
to know whether a machine translation of this record's language is possible at
all**, and that is a property of the language, not of the record, which means
it belongs beside `answer/translate.py`'s language declarations — the ones
F3_RESULT already lists as load-bearing and uncovered by any mutation.

**The sentence that travels: the tier's whole justification is that it turns
the machine-translation path on, and the best-evidenced untranslated text in
the world is one where turning that path on is the failure mode.**

---

# FINDING 45 — `verbatim_machine_english` is fed by GENRE, not by obscurity, and that is a seam a curator can aim at

FINDING 41 concluded that the tier cannot be hunted, on this mechanism:

> *"A text worth curating is a text worth translating. The properties that make
> a record valuable here are the properties that got it translated into English
> by somebody, and being translated is the disqualifier. The tier is fed by
> obscurity and the corpus is trying to be interesting."*

**The East Asia hunt falsifies the mechanism while confirming the observation
that produced it.** Both halves matter.

## What was actually translated, read off the books rather than off a bibliography

Hirth, *China and the Roman Orient* (1885), public domain, contents enumerated
from the volume itself:

```
TRANSLATED, all of it, in one nineteenth-century volume
  Shiji, Qian Hanshu, Hou Hanshu, Weilue, Jinshu, Songshu, Liangshu, Weishu,
  Jiu Tangshu, Xin Tangshu, Songshi, Mingshi, Zhufan Zhi, Wenxian Tongkao

NOT TRANSLATED, and not mentioned anywhere in the volume
  Tang Huiyao        唐會要      an institutional compendium from court archives
  Cefu Yuangui       冊府元龜    1,000 juan, built from Tang court records
  Taiping Huanyuji   太平寰宇記  Northern Song imperial geography
  Lingwai Daida      嶺外代答    a twelfth-century official's merchant report
```

**Every text in the first list is a DYNASTIC HISTORY or its recognised
companion. Every text in the second is a `huiyao`, a `leishu` or a geography.**
The sinologists translated the prestige genre. The Song-era compilations that
preserve the administrative detail — the dated embassy registers, the tribute
lists, the gazetteers — were left alone, and they have stayed alone for a
hundred and forty years.

## Why this is a correction and not a quibble

Obscurity is not a property a curator can aim at: FINDING 41 is right that more
effort finds MORE English, not less, and right that the tier and the corpus
pull in opposite directions if that is the mechanism.

**Genre is a property a curator can aim at.** It is stable, it is knowable in
advance, it is the same in Chinese as it is in Ge'ez and Middle Persian — the
open Littmann volume is a *scholarly epigraphic corpus*, the prestige genre for
Aksum, and it is fully translated into German — and it predicts where to look
before the looking starts. That is exactly what FINDING 41 said the tier did
not have.

**And the seam is not thin material.** The Cefu Yuangui entry is a dated
Byzantine embassy notice naming its gift — 拂菻王波多力遣使獻赤頗黎、綠頗黎 —
red glass and green glass, presented at the Tang court in 643. This corpus
already holds Roman and Byzantine glass as archaeology in three regions. The
text that records the same substance arriving as diplomacy has never been
translated into English, and it is the single strongest East Asia candidate in
either list.

## What FINDING 41 got right, kept

Two of the five East Asia candidates DID have English, found only by looking
hard: one in a 2020 monograph from an Italian academic press, one in a 1984
UNESCO series whose open-access status could not be established. That is
FINDING 41's observation intact — a hunt that goes looking for the absence of
English keeps finding English — and it is why ruling 57 changes the definition
rather than the effort.

**The two findings compose, and the composition is the useful rule:** aim at
the genre nobody translated, and record the boundary of the search, because the
English you have not found is not the English that does not exist.

---

# FINDING 46 — a defect recorded as fixed was fixed in one of four places, and the other three were only invisible because nobody had run them

FINDING 37, five days old, found two defects in `scripts/mutate_places.py` and
records both as fixed. The second:

> *"`failures_from` matched `startswith("FAIL")`, and `ingest.test_places` ends
> with a summary line reading `FAILED (1)` — so every red run harvested a
> phantom guard named `ED (1)` beside the real ones, which the new BASELINE
> block would have reported as a check that is already failing."*

**Three other harnesses carried the identical defect LIVE and were not
touched, and a fourth carries it latent:**

```
scripts/mutate_ui_places.py   suite ends `FAILED (1)`      phantom `ED (1)`
scripts/mutate_fidelity.py    suite ends `FAILED (5)`      phantom `ED (5)`
scripts/mutate_ranking.py     suite ends `FAILED: <name>`  phantom `ED: <name>`
scripts/mutate_part8.py       suite ends `N passed, N failed`   -- nothing to
                              harvest, so the same code is harmless HERE
```

All four fixed in F4, with the space. **The fourth is the one worth the
sentence.** `mutate_part8` is correct today only because
`eval.test_answer_eval` happens never to print a line beginning `FAIL` that is
not a guard. That is a property of the SUITE, not of the harness — and a
harness whose correctness depends on what its suite chooses to print is a
harness one `print` statement away from inventing a failing guard. It was made
the same as the other three so that nobody has to establish this again.

## The mechanism, which is FINDING 37's own and one level up

FINDING 37's closing sentence was *"it survived in `mutate_places` because
`mutate_places` had not been run."* The same sentence explains all three of
these, and it explains why the FIX did not travel either: **a defect is fixed
in the file where it was found, and the search for its siblings is a separate
act that nobody scheduled.** F1 found a transcription defect in an assertion
count, F2 found it in two suite counts, F3 found it in a date. This is the
fourth instance of that family and the first where the remedy already existed
and simply had not been copied.

**What a phantom guard actually costs, which is why this is not cosmetic.**
These harnesses now carry a BASELINE block: before applying a mutation they run
the suite and record which guards are already red, so a mutation caught by a
pre-existing failure is reported UNVERIFIED rather than verified. A phantom
guard is an invented entry in that block. **A harness that invents a failing
guard reports a green suite as partly red** — which is the one thing a mutation
harness must never do quietly, because the whole instrument is an argument that
the guards are watched.

It has cost nothing yet, because a phantom only appears on a red run and these
three have not had one since the BASELINE blocks were added. That is not
reassurance. It is the same silence that hid it for five days.



---

# FINDING 47 — a suite reported green in the commit that made it red, by the run that commit was about

`eval.test_answer_eval` was **382 passed, 1 failed** on the host this morning,
at `ea1b9ae`, before F4 had touched a line of it.

```
FAIL and the greedy archive is known two ways, both named:
     ['assumed', 'reconstructed', 'recorded']
```

F3_RESULT reports, under the heading *"Suites, on the host, at the committed
tree"*:

```
eval.test_answer_eval    383 passed / 0 failed   (377 before F3)
```

**Both statements are true and they are about different trees.**

## What moved, and it was F3's own instrument

The assertion read `bases == {"reconstructed", "assumed"}` — the set of ways a
greedy run can be told which arm it ran on. It was true because **no greedy run
had ever recorded its arm**: the field arrived in Block F, and the 165 runs
carrying it are the sonnet arm, which this line filters out.

Ruling 51 sent F3's mid-tranche floor reading to a **PROBE**: three required
cases at three repetitions, archived to `eval/probes/`. Nine runs, on the greedy
arm, at 14:58 UTC on 2026-08-31 — and, being new runs, **they record their
arm.**

```
greedy archive, by basis:   assumed 115   reconstructed 396   recorded 9
                                                              ^ the probe
git log -1 -- eval/answer_runs/20260831T*.json
    3010abd  F3 CLOSED: the handoff, and two findings the sub-tranche run produced
```

**The nine archives arrived in the same commit whose message reports this suite
green.** The suite was run before the probe; the commit contains both.

## Why this is not a scheduling slip

`eval/probes/` was invented so a probe could not calibrate the floor **by
construction rather than by being remembered** — ruling 51, and it worked
exactly as designed. What nobody asked is what a probe does to everything ELSE
that reads the archive, and the answer is that its per-run payloads land in
`eval/answer_runs/` like any other run, because that is where
`run_answer._archive` puts them. **The directory rule governs the SWEEP
archive. It does not govern the run archive, and a census assertion over the
run archive is downstream of both.**

**This is ruling 49 one level up.** Ruling 49 exists because the rule deciding
what may calibrate could not see the corpus a sweep ran at. Here a suite result
was reported at a tree, and the archive it counts moved inside the commit that
reported it. Same shape, same session — and the remedy ruling 49 chose is the
remedy here: **a suite number in a result document should name the commit it
was run at, and a suite run before the last thing that commit adds is not a
suite run at that tree.**

## The assertion was a frozen census, and that is the repairable part

`bases == {"reconstructed", "assumed"}` is not a rule about the archive. It is
a photograph of it. It was true when written and became false the moment this
project did the thing it has been trying to do for two blocks — archive a run
that says what it ran on. **An assertion that fails when the evidence improves
has to be edited every time the system gets better, and an assertion nobody can
edit without thinking is one somebody eventually edits without thinking.**

Rewritten as three rules that do not expire:

- both reconstruction and assumption are still exercised — the anti-vacuity the
  original was for, kept as a subset test rather than an equality;
- no fourth basis ever appears unnamed;
- **a GREEDY run that records its arm is read from the row**, which is the
  foreign-arm assertion turned around and could not be written until nine
  greedy runs existed to make it assertable. That one gets STRONGER as the
  archive grows.

Plus a counted line rather than an asserted number: *9 greedy run(s) now RECORD
their arm.*

## What is NOT claimed

F3 did not report a false number. It reported a true number about a tree that
existed for twenty minutes, and F3_RESULT's suite table is among the most
carefully assembled parts of that document. **The defect is that "at the
committed tree" was written where "before the probe" was meant, and nothing in
this repository can tell those apart** — FINDING 34's family, with the number
correct and the PROVENANCE wrong.

```
eval.test_answer_eval    383 -> 388 assertions, 0 failed
                         (one rewritten into three, plus the quota split's two)
```

**The sentence that travels: a probe was routed away from the sweep archive so
it could not calibrate the floor, and it landed in the run archive and broke a
census that the same commit reported as green.**

---

# FINDING 48 — the capture path silently rewrites the characters it captures, and this corpus has already lost a record to that once

**`WebFetch` cannot be used to capture source text.** Two defects, measured on
one line of one inscription, by comparing what the fetch returned against what
the same page gives a human who copies it:

```
page (copied by hand)   <— — —> μεθ’ ἃ ἀνδρείωσας τὰ μὲν ἔγγιστα τοῦ βασιλείου
fetch returned                   μεθ' ἃ ἀνδρείωσας τὰ μὲν ἔγγιστα τοῦ βασιλείου

  1. the lacuna marker `<— — —> ` was DROPPED -- eight characters stating that
     text is missing before this point, which is an editorial claim about the
     monument and not decoration
  2. U+2019 RIGHT SINGLE QUOTATION MARK became U+0027 APOSTROPHE
```

Fifty-six characters in, two silent alterations: one deletion of an editorial
statement, one character substitution.

## Why this is disqualifying rather than a quirk to work around

**Neither defect is visible to any check in this repository.** `ingest.verify`
asserts `source_text[char_start:char_end] == chunk.text`, which is a claim about
INTERNAL consistency: an excerpt corrupted before it lands is corrupted
consistently, and every offset resolves perfectly against the wrong characters.
`build_ui_data --verify` compares archived quotations to the seed record, not
the seed record to the page it came from. **Nothing in this project compares a
record to its source.** The curator is that check, and a summarising fetch is
the curator not looking.

And the substitution is precisely the class of edit the corpus cannot survive.
The apostrophe in `μετ’ εἰρήνης` is a character in a chunk whose offsets other
runs cite. FINDING 42 was a whole finding about a newline rendered as a space.

## The precedent, which is in this repository and is the reason this is a rule

`china-describes-rome-weilue`'s own note:

> *"the record's excerpt was known corrupt against Chen Shou 1975 ... The
> excerpt turned out to be NOT CORRUPT BUT INVENTED: none of its three
> fragments occurs in the source. When it was replaced this assertion matched
> nothing and the pair silently left the run — pairs 33 -> 31, units 30 -> 29,
> and every aggregate moved because the DENOMINATOR shrank."*

An excerpt that arrived through a summarising layer, in the corpus whose
central claim is that quotations resolve to exact character offsets, and it
cost a pair, a unit and the comparability of every aggregate before anybody
noticed. **This finding is that incident's mechanism, caught before the second
one.**

## What it costs, and where the cost goes

Source text and its published translation are **pasted by the curator from the
cited page**. Every record. That is not a limitation of one awkward site: F3
budgeted `parsigdatabase.com` as *"a human pass at the keyboard"* as though it
were the exception, and the human pass is the ordinary case — what
parsigdatabase adds is a second one.

This belongs in `text_capture` under ruling 46, and it means the phase has a
floor that no tooling removes. **A tranche that reports `text_capture` falling
is a tranche where somebody stopped checking the page**, which is the shape
ruling 46 already warns about for the aggregate.

## What it does NOT mean

Fetching is still how candidates are FOUND, how translations are located, and
how a search is established as having failed — ruling 57's evidence is built
entirely out of it. The rule is narrow and it is about one step: **the
characters that go on disk are copied by a person from the page, and nothing
between the page and the record is allowed to be a model.**

**The sentence that travels: the corpus check asserts that a quotation resolves
to the characters on disk, and nothing at all asserts that the characters on
disk are the ones on the page.**

---

# FINDING 49 — the rule about numbers in guard labels is written down in this repository, and was being broken two files away

Adding ONE ranking pair, under ruling 54, turned `eval.test_ranking_check` red:

```
FAILED: ruling 12 costs exactly 205 renderings over this gold set
```

The assertion was right and the guard was wrong. `expected_rendering_count` is
computed from the language rule and the gold set, so it moves the moment the
gold set moves — which, from ruling 54 onward, is **every record F4 through F7
curates.**

## The rule already existed, in another file, with its reason attached

`eval/test_answer_eval.py`, written before F4:

> *"The counts go in their OWN line and not into the guard text. A guard named
> by `scripts/mutate_part8.py` is matched as an exact string, so a guard whose
> wording carries a number it computes is a guard the harness stops being able
> to name the moment a mutation changes that number."*

`eval/test_ranking_check.py`'s label carried `205`, and
`scripts/mutate_ranking.py`'s `EXPECTED` list named that label verbatim. So the
guard, the number and the harness were three copies of one figure in three
files — **FINDING 14's shape, in the machinery built to catch FINDING 14's
shape.**

## What the cheap fix would have cost, which is why it was not taken

Bumping `205` to the new total takes one minute and works. It also means the
guard label and the harness's `EXPECTED` entry must be edited **together, on
every tranche, for the rest of Block F** — and an edit that must be made in two
files at once, routinely, by whoever is curating, is an edit that is eventually
made in one. The harness would then print `MISS` on a guard that was working,
which is FINDING 37 exactly, and this project has now spent parts of three
sessions on harnesses that could not name their own guards.

**What is asserted is now the rule rather than the total.** The cost is
computed twice from two directions and the two must agree; the total is printed
in the detail line, where nothing matches on it.

## The part worth keeping

**A rule written down in one file is not a rule.** F1 found a count declared
beside a list, F2 found it in two suite counts, F3 found it in a date, F4 found
it in a harness fix applied to one file of four (FINDING 46) — and here in a
convention stated, argued and then not carried across the directory boundary.
The remedy is the same every time and it is never the number: **derive it, or
put it where no matcher reads it.**

---

## Ruling 59 — a retired ledger row may be REINSTATED when its record lands, and the anti-loophole moves with it unchanged

**`python -m ingest.cost_log reinstate <record-id> --because "..."` stamps a
retired row with a second date and a second reason. It is not an un-retire: the
row stays in `retired`, keeps its minutes, its `retired_on` and its original
`because`. A reinstated row is exempt from ruling 52's two retirement checks
ONLY while an ACTIVE row in `records` carries minutes for the same record.**

### Ruling 52 wrote a permanent property and an event, and they disagree

> *"A row may be retired ONLY if its record is NOT in the corpus."*

That is checked on **every run of `check_ledger`**, not at the moment of
retirement. So a retirement that is legal when made becomes illegal the moment
the record is curated — and ruling 52 provided no way back, because it
deliberately made retirement not a delete.

It is not hypothetical. It happened four hours after ruling 52 was quoted
approvingly in this same session:

```
17:2x  africa-04-silko-talmis retired.  LEGAL: the record was not in the corpus.
       Adulis was curated first, because its published English was readable.
18:0x  africa-04-silko-talmis curated.  The ledger is now permanently red, and
       ingest.verify refuses the tree, on a retirement nobody did wrong.
```

### What was NOT done, and why

**The check was not weakened.** The obvious fix is to make the clause read
*"...unless the record was curated later"*, which is the anti-loophole deleted
by anyone who curates the record afterwards — and curating the record
afterwards is precisely what an expensive record's owner would do.

**The row was not deleted.** Ruling 52's sentence is that excluding by a
recorded rule is a diff and excluding by making a row vanish is not. A
reinstatement is the diff that says the exclusion ended, and it belongs beside
the exclusion rather than in place of it.

### The anti-loophole, carried across intact

Reinstatement means the minutes are **back in a mean**, not that a row escaped
one. So the exemption is conditional on an active row existing:

```
retire an expensive record, declare it reinstated, file nothing
  -> "reinstated, but no row in `records` carries its minutes"
     A reinstated row with nothing filed against it is a retirement wearing a
     different word.
```

A reinstatement also needs a written reason and a real date, on the same
argument ruling 52 makes about retirement: an unexplained reinstatement is the
retirement rule waived by whoever was inconvenienced by it.

### The report prints them under their own heading, with the opposite sentence

Retired rows are announced as *counted in NO mean below*. Reinstated rows say
the reverse — *their minutes ARE counted below* — because a reader who saw them
under the first heading would subtract them twice. Ruling 52's *"named, never
merely subtracted"*, in the direction it did not anticipate.

### The cost this leaves standing, which is ruling 52's and not a defect

The minutes stay **`estimated`**. They were MEASURED, against this very record
id, and ruling 52 forbids carrying measured minutes across a retirement because
*"a span measured against a record id the hunt had not settled is not a
measurement of the record that landed"*. Here the subject never moved — only
the ORDER did — so the downgrade is a real loss of precision for a reason that
does not apply.

**It is accepted rather than carved out.** An exception for *"the subject did
not really change"* is an exception whose test is the curator's account of
their own intent, and ruling 48 already settles the tie-break: the weaker
provenance wins. The price of that rule is visible here and it is small; the
price of a rule that reads intent is not payable at all.

```
ingest/test_cost.py     58 -> 64 assertions
scripts/mutate_cost.py  48 -> 51 mutations
```

---

# FINDING 50 — a model cannot be the capture path, and it can be the diff

FINDING 48 established that source text is copied by a person from the page,
because an automated fetch silently dropped a lacuna marker and substituted
U+0027 for U+2019. **Silko is that finding's second measurement, and its
correction.**

## The second measurement

The same PHI page, fetched and then copied by hand, compared character by
character:

```
431 characters compared
  1 difference:  fetched U+0027 '   <-   page U+2019 ’
```

One substitution in 431, and it is the SAME substitution measured on the Adulis
page. **The normalisation is systematic, not incidental** — which is worse than
a random corruption, because a systematic one produces a corpus that looks
internally consistent and is uniformly wrong about one character.

## And then the human path drifted too

The English for this record exists only as JPEG images on a personal
university page, so the curator typed it out. Compared against the image:

```
line  1   all THE Ethiopians,        ->  all Ethiopians
line  3   gave me THE victory.       ->  gave me victory.
line  5   with my troops.            ->  with my troops,
line  6   themselves to me           ->  themselves to me,
line 10   I withdrew to MY upper     ->  I withdrew to THE upper part OF
          part (of the country).         (of the country)
```

Five divergences in ten short lines: two dropped definite articles, two altered
stops, and one that changes the meaning — *my* upper part is Silko's own
territory and *the* upper part is anywhere. **This is FINDING 42's class of
defect exactly**, and FINDING 42 was a whole finding about a newline.

## The correction to FINDING 48, which is the useful part

FINDING 48 says *"nothing between the page and the record is allowed to be a
model."* That is right and it stays. What it does not say, and what this record
establishes, is that **nothing forbids a model from comparing them afterwards.**

The five divergences above were found by reading the image against the typing.
The capture stayed with the curator, who confirmed each one; the check was
automatic. Those are different jobs and only the first has to be human.

**And it is the check FINDING 48 said did not exist.** Its own words: *"Nothing
in this project compares a record to its source. The curator is that check, and
a summarising fetch is the curator not looking."* One paragraph later there was
something else that could look — not as the authority, but as the second pair
of eyes that had never been in the loop at all.

## What this does not license

It does not license the model correcting the record. Every one of the five was
put back to the curator, and the curator confirmed the reading. **The
difference between proposing a diff and applying one is the whole of the
rule**, and a check that silently repairs its input is a check that has become
the capture path by another route.

**The sentence that travels: the automated path was wrong once in 431
characters and the human path was wrong five times in ten lines, and the useful
arrangement is not to pick one but to make them check each other.**

---
---

# Ruling 60 and FINDING 51 — declared 2026-09-01, F4 PART 2's FIRST ACT

*Date from the host, not from a document: `date -u +%F` printed `2026-09-01`.
This is a THIRD distinct UTC date in Block F, which three rules want and ruling
50 booked.*

*Written before the stele's excerpt has been selected, before any East Asian
record exists, and before anything has been pasted. Ruling 39's discipline for
the seventh time in this block. It is worth the paragraph here because this
ruling's subject is a quota the handoff says F4 is most likely to miss, and a
rule about a likely miss is worthless if it is written after the miss.*

---

## Ruling 60 — F4's two gloss-capable records are FORCED, and the shortfall outcome is declared before the first excerpt is chosen

**The stele and the Liangshu are F4's two gloss-capable records. There is no
third candidate inside this tranche, the choice was made by arithmetic rather
than by curation, and the three outcomes are written here so that F4's close
reads as a result rather than as an account of what happened.**

### The two records are not a choice, and F4_PART2_START does not say so

```
GLOSS_CAPABLE_TIERS = {verbatim_with_provenance,
                       published_translation_only,
                       catalogue_record}      -- ingest/fidelity.py

F4's slots on those tiers    Sub-Saharan Africa vwp 2    East Asia vwp 2
Spent in Part 1              africa-05-adulis-throne     africa-04-silko-talmis
Left                         East Asia vwp 2, and one vme that cannot carry one
```

Neither Africa record is gloss-capable, and record 32's own notes say so in
terms: Satzinger's bare `(?)` against Telelis is outside the excerpt and is a
hedge about a place-name reading, not a published alternative reading with a
statement that the reading is uncertain. The third remaining slot is
`verbatim_machine_english`, barred by the frozenset for the reason held beside
it — a gloss case there would require the answer to quote a MACHINE translation
of a disputed reading, which is the output the gloss arm exists to catch.

**So both East Asia `verbatim_with_provenance` records must carry a gloss case.**
F4_PART2_START names the stele as *"the strongest gloss-capable candidate in the
tranche"* and says nothing at all about the Liangshu. That silence is what this
ruling is written against: it reads as though the second record were still to be
found, and there is nothing left to find it in.

### The three outcomes, declared now

**TWO.** Both records carry a published alternative or hedged reading AND a
statement that the reading is uncertain, both inside a RETRIEVAL-ELIGIBLE chunk
— `original_text_excerpt` or `reference_translation`, never `notes`, which is
the trap `gloss_capable_declared` was added to make visible. Declared 1 -> 3 of
8. **This is the quota met and it is not the target met**, for the reason
FINDING 51 gives below, and F4_RESULT states both numbers in the same sentence.

**ONE.** The Liangshu cannot be made to carry one. Reported as a SHORTFALL in
F4_RESULT **with the passage named** — which Hirth page and which Kanripo lines
were examined, and what they lacked — carried into F5 as a named debt, and NOT
absorbed. The allocation is not re-cut: ruling 53 declined one mid-tranche
re-cut of `corpus_tiers.json` and ruling 58 declined a second, and a third in
the same block would be a block editing its instruments to fit what it found.

**ZERO.** The stele's disputed readings do not survive into a chunked field.
**That is not a supply problem and F4_RESULT may not report it as one.** Legge
1888 prints the alternative readings and the uncertainty in his own notes, so a
zero here is a failure to design the excerpt around them, and the result
document says so in those words. Recorded as a third outcome for ruling 53's
reason: a close that can only say MET or MISSED can satisfy itself by choosing.

### What the gloss case actually requires, restated because it is where F3 lost its second record

`what_gloss_capable_MEANS_mechanically`: a genuine alternative or hedged
reading **and** a statement that the reading is uncertain, both inside a chunk
the model can retrieve. F3 curated two records intending both to be
gloss-capable and declared one, because the hedge went into
`original_text_note`, which the loader does not chunk. The excerpt is therefore
chosen for the gloss BEFORE it is chosen for the passage, and if the two pull
apart the record says which won.

### What is NOT done

**No check is added.** A per-sub-tranche gloss delivery check needs
`gloss_capable_declared` to be attributable to a tranche, and it is a flat list;
attributing it is a data-structure change to the file two rulings have just
declined to re-cut mid-tranche. **It is owed, it is named here, and F5 takes it
beside ruling 53's deferred vme ruling and ruling 58's per-region language rule
— three owed instrument changes, one re-cut, two tranches of evidence.**

**The mix is not touched.** F3's declared 2 stays 2. Restating a delivered plan
to match what happened is the move this project refuses everywhere else, and
ruling 56 refused it four hours before this was written.

**The sentence that travels: a quota declared per tranche and checked only in
aggregate is a quota that can be missed one tranche at a time with every check
green.**

---

# FINDING 51 — the gloss target at 60 is already out of reach by DECLARATION, and the guard that watches it is counting slots

F4_START records that *"the gloss-capable quota is at 1 of 8 declared with 22
slots left — F3 was allocated 2 and delivered 1."* Both halves of that sentence
are true, both have been on file since F4 opened, and **the arithmetic between
them has never been done.**

```
declared to date                                     1
still declared by the plan   F4 2 + F5 2 + F6 1 + F7 1 = 6
                                                     --
maximum deliverable without a tranche exceeding
its own declaration                                  7        against 8
```

**The target of 8 cannot be reached by every remaining sub-tranche delivering
exactly what it declared.** It can only be reached if one of them quietly
over-delivers — and nothing forbids that, because `gloss_capable` is a
per-tranche declaration and no check compares a tranche's declaration to its
delivery at all.

## Three checks look at this and all three pass

```
check_target_mix    sum(sub_tranche.gloss_capable) == 8            PASSES -- it
                    reads the PLAN, and the plan has always summed to 8
check_delivery      len(declared) > 8 ?                            PASSES at 1
                    is the quota REACHABLE from remaining SLOTS?   PASSES: 26
                    gloss-capable-tier slots are planned across F3-F7 and 20 are
                    still unspent at record 32, against 7 declarations wanted
verify note         "Gloss-capable declared 1/8, with N slot(s) left"
                    PRINTS the true numbers and invites the wrong reading
```

**The reachability guard asks whether enough SLOTS remain. The scarce thing is
DECLARATIONS.** Slots are plentiful by construction — every `vwp`,
`published_translation_only` and `catalogue_record` slot in F5, F6 and F7 counts
toward that 20, including the twelve `catalogue_record` and
`published_translation_only` slots in F6 and F7 that no plan intends to spend on
a gloss case. Declarations are four. So the guard
answers a question nobody is asking, in the reassuring direction, and it will go
on passing until the last tranche.

## This is ruling 49's shape, and ruling 56's, arriving in the third place

Ruling 49: a rule that could not see the data it was written to protect. Ruling
56: a measure that improves as its subject gets harder to observe. This one does
not even drift — **it was aimed at the wrong quantity on the day it was
written**, and it reads as correct because SLOTS and DECLARATIONS are both
counts of records and the sentence works either way.

The same family as FINDING 34, FINDING 46 and FINDING 49: the number is right
and something about its provenance or its subject is wrong. Fourth instance in
this block, first where the guard is not transcribing anything.

## What is NOT claimed

**F3 did nothing wrong.** It curated six records and delivered one gloss case,
recorded the shortfall, and F4_START carried it forward in the first table it
prints. Nobody hid anything.

**And this finding does not make the target unreachable — the target was
already unreachable and now somebody has said so.** The remedy is F5's and is
one of two: raise a later tranche's declaration, which is a plan change with a
reason attached, or lower `gloss_capable_records` from 8, which is a re-cut and
belongs with the other two owed. **Not fixed today, because a quota changed in
the session that noticed it is a quota fitted to the session.**

**The sentence that travels: the guard asked whether enough slots remained when
the scarce thing was declarations, and both are counts of records, so the
sentence read correctly for two sub-tranches.**

---

## Ruling 61 — a second pre-registered prediction, on FINDING 43's mechanism, made from WITHIN a single run

**Prediction, registered 2026-09-01 before any ranking run in Part 2 and before
ruling 55's archive has been re-read:**

```
kedukan-bukit-saka-605          best_other_doc_chunk_id names seasia-07-talang-tuo
talang-tuo-sriksetra-park       best_other_doc_chunk_id names seasia-06-kedukan-bukit
thorsberg-chape-niwajemariz     best_other_doc_chunk_id names scandinavia-03-vimose
```

### Why this is available and why it is nearly free

FINDING 43's mechanism is crowding by a near neighbour: `vimose-runes` fell from
rank 3 to rank 7 when `scandinavia-05-thorsberg-chape` entered the index — same
language, script, period, object type and country. That was measured as a
BEFORE and AFTER across two runs, which is the only way the project has ever
looked at it, and it is exactly the claim ruling 54 now bars for the six pairs
paying its debt.

**It does not have to be looked at that way.** `best_other_doc_chunk_id` records
WHICH chunk of another document sat closest behind the target, per pair, in
every run since Block C — added because *"the run recorded the number and not
the thing it was measured against."* If the mechanism is near-duplicate
crowding, the nearest competitor to a Srivijayan Old Malay pair is the other
Srivijayan Old Malay record, in the same run, with no earlier run to compare
against.

**So ruling 54's exclusion does not bar this, and saying so is part of the
ruling.** The exclusion is on before/after claims — that a tranche improved
retrieval — because those turn on when the pair was written relative to the
records. A statement about which document sits second in one run turns on
neither, and a rule that swallowed it would have made the six debt pairs
worthless rather than merely unquotable in one direction.

### The material, which is why these three and not others

`seasia-06-kedukan-bukit` and `seasia-07-talang-tuo` are **the closest
near-duplicate texts this corpus holds**: same language, same script, one year
apart, the same polity, the same region, and both `verbatim_machine_english`
with no English chunk of their own to intervene. They are a cleaner instance of
FINDING 43's configuration than the Scandinavian pair that produced it, because
the Scandinavian records are two OBJECTS and these are two TEXTS.

That is precisely the distinction ruling 55's falsification clause turns on. If
crowding is about near-duplicate objects, these two need not crowd each other.
If it is about same-language-same-subject, they must.

### What falsifies it

**A nearest competitor sharing neither language nor object type with the
target** — an English chunk, or a record from another region. Then the closest
neighbour is being decided by topic or by embedding artefact rather than by
near-duplication, and FINDING 43's mechanism is not what has been assumed.

**Two of three, in either direction, is the informative outcome** and is
reported as such rather than rounded to a verdict.

### What it is NOT

Not a gate, not a regression claim, and not a reason to curate differently. And
**not a substitute for ruling 55**, which is a stronger prediction because it
names a direction of movement and can be wrong in a way this one cannot: a
prediction about who sits second is confirmed by the corpus being what it
already is. It is registered because it costs nothing, because it is the only
FINDING 43 statement the debt pairs are permitted to make, and because it is
available today and will not be after the run.

---

# FINDING 52 — `.gitattributes` stops GIT rewriting line endings, and nothing stops the EDITOR

`* -text` disables end-of-line conversion for every path in this repository, and
the comment above it explains why in the only terms that matter here: a one-byte
shift per line silently invalidates every character offset in the seed corpus
and every archived citation span that points into it.

**It works, and it protects against the wrong actor.** Git is not the only thing
that writes these files. Anything that opens a file in TEXT mode, reads it,
edits it and writes it back normalises the newlines on the way out — and because
`-text` tells git to store exactly what it is handed, the normalised file is
committed exactly as normalised.

## Measured on this commit, before it was committed

Editing four files through a text-mode read-modify-write, and running a mutation
harness that restores its sources the same way, rewrote **seven** files:

```
eval/goldset.py            CRLF -> LF     1,393 lines, 29 of them the actual edit
eval/run_ranking_check.py  CRLF -> LF     2,186 lines, 46 of them the actual edit
retrieve/search.py         CRLF -> LF       302 lines, NONE of them an edit
retrieve/rerank.py         CRLF -> LF       902 lines, NONE of them an edit
retrieve/collapse.py, render.py, fuse.py, answer/translate.py   the same
```

Five of the seven had no intended change at all: the mutation harness restores
its sources correctly, and restoring them through a text-mode write is what
rewrote them. `git diff --stat` reported 1,562 insertions and 1,562 deletions
across files nobody had touched.

## The convention is per-file and historical, which is the part that makes this easy to miss

```
eval/goldset.py            CRLF        eval/test_ranking_check.py   LF
eval/run_ranking_check.py  CRLF        scripts/mutate_ranking.py    LF
                                       eval/gold/ranking_pairs.json LF
```

Six files in one commit, two conventions, no rule. So a tool that writes LF
leaves four files byte-clean and mangles two, and the mangling appears in the
same commit as a legitimate change to those same two files — **which is the
worst available presentation, because the diff is not obviously wrong, it is
obviously huge.**

## Why no check here would have caught it

`ingest.verify` asserts `source_text[char_start:char_end] == chunk.text` over
`data/seed_corpus/`, and every offset survived, because none of the seven files
is corpus data. `eval.test_ranking_check` passed at 253 before and after. **The
whole suite is indifferent to the bytes of its own source.** That is correct —
a test suite that asserted its own file's line endings would be absurd — and it
means the detector for this class is `git diff --stat` and a reader who notices
that a file with a three-line change has a four-thousand-line diff.

## The rule, stated because the remedy is procedural and cannot be a test

**Every write to a file in this repository preserves that file's existing
newline convention, and the way to guarantee that is to write BYTES.** A
read-modify-write in text mode is the capture path from FINDING 48 wearing
different clothes: something in the middle is normalising, it is systematic
rather than random, and it is invisible to every check downstream of it.

**And `git diff --stat` is read before every commit, not after.** A whole-file
rewrite in a file you edited three lines of is the signal, and it is free.

## And the convention was already known here, in a file that got it right

`scripts/mutate_part8.py`, in its own header, before any of this:

> *"It is LF where `eval/goldset.py` is CRLF; the harness reads and restores
> each source under its own newline and compares BYTES, so this costs
> nothing."*

**So the per-file convention was noticed, written down and correctly handled by
one harness, and every other tool touching this repository was free to ignore
it.** That is a sharper statement than the finding above: this was not an
unknown hazard, it was a documented one with a working local remedy that nobody
generalised. FINDING 46's family again — a defect understood in the file where
it was met, and the search for its siblings a separate act nobody scheduled.

**The sentence that travels: the repository forbade git from rewriting a single
byte, and then seven files were rewritten by the tool that was reading them.**

---

# FINDING 53 — `_djvu.txt` is not the page, it is somebody else's OCR of the page, and this project has been reading it as a page since F3

`F4_CANDIDATES.md` lists `archive.org _djvu.txt` under **CLEAN, no difficulty**,
with one failure mode named: *"LONG BOOKS TRUNCATE — front matter and TOC
arrive, body text deep in the volume often does not."*

**Truncation is the safe failure and it is not the dangerous one.** A truncated
fetch is visibly missing. What arrives instead is a machine transcription that
looks like text, reads like text, and is treated as a page by a rule — FINDING
48's — written to keep models out of the capture path.

## Measured on the curator's own capture of Legge 1888, paragraph 9

```
Western Re¬ gions       a soft hyphen and a space where the printed line broke
ap¬ pointed             the same, mid-word
brilliant 3.            a footnote MARKER, inline, indistinguishable from text
0r^n,^ry ... la ism.    a MARGINAL side-note, garbled, sitting INSIDE the
                        sentence, between "Coral Sea," and "and reaches on the
                        north"
```

The first three are cosmetic and a careful curator removes them. **The fourth is
not cosmetic.** It is foreign text spliced into the middle of a quotation, it is
in the position a reader expects a clause, and a curator working at speed pastes
it. Legge's page has marginal headings; the OCR has no column model, so a
heading beside line 3 lands between the words that were beside it.

## Why FINDING 48 did not already cover this

FINDING 48's rule is *"nothing between the page and the record is allowed to be
a model"*, and it was written against `WebFetch` — a model summarising a page in
this session, now. `_djvu.txt` is a model too. It is just somebody else's, run
years ago, and its output is stored as a file with a `.txt` extension on a
domain this project has already decided is clean.

**The rule was about the actor and the exception was read as being about the
mechanism.** A fetch of `_djvu.txt` returns the OCR faithfully, so the fetch is
innocent and the characters are still not the ones on the page.

FINDING 50 is the other half and it stands: the human path drifts too, and the
useful arrangement is to make them check each other. What this finding adds is
that **`_djvu.txt` is not the second party.** Diffing a typed capture against
the OCR of the same page checks the typist against a machine that has already
made its own errors in the same places — a hyphenated word, a marginal note, a
footnote marker — and agrees with itself.

## What changes, narrowly

`archive.org _djvu.txt` moves out of CLEAN. It stays an excellent way to FIND a
passage, to establish that a book contains one, and to locate a page number —
which is what ruling 57's whole evidence base is built from, and none of that is
weakened. **It is not a capture source.** Characters taken from a public-domain
volume on archive.org are read off the PAGE IMAGES by a person, exactly as
record 32's English was read off a JPEG.

And the cost lands where FINDING 48 said it would: `text_capture` has a floor no
tooling removes, and this is the second region in which the floor turned out to
be a human at a keyboard reading a picture.

## The record this was found on chose around it

`eastasia-04-jingjiao-stele` takes its English from a hand-corrected
transcription rather than from OCR, and quotes Legge only for the four words the
gloss needs — read off the page image, because the one piece of punctuation in
them is the apostrophe of `Ta Ts'in`, and U+2019 becoming U+0027 is the exact
substitution FINDING 48 and FINDING 50 measured twice.

**The sentence that travels: a file with a .txt extension on a trusted domain is
still a transcription, and the rule kept models out of the capture path without
noticing that one had already been through it.**

## FINDING 53, continued — the second measurement is a FALSE NEGATIVE, and the remedy is that a locating fetch must not speak

The finding above was written from one measurement: a dropped diacritic and a
marginal note spliced into a sentence. The record it was written on produced a
second, and it is worse.

Asked whether the CBETA file carried a critical apparatus near this passage, a
summarising fetch answered:

```
"No <app>/<lem>/<rdg> apparatus exists for this passage."
```

The curator's capture of the same file's back matter:

```xml
<app from="#beg1289b2001" to="#end1289b2001">
  <lem wit="#wit.cbeta" resp="#resp4">浣 <note type="cf1">T32n1675_p0754c21</note>
                                        <note type="cf2">T48n2003_p0200a02</note></lem>
  <rdg wit="#wit.orig">綄</rdg></app>
```

**A dropped character is a bad error and a false negative about the PRESENCE of
evidence is a worse one**, because nothing downstream can falsify it. A curator
told that an apparatus exists goes and reads it. A curator told that none exists
stops looking, and the record is published without the one thing that would have
made it gloss-capable. This record would have lost its statement of uncertainty
to a sentence a model wrote.

### The discipline this forces, which FINDING 53 did not state

**A locating fetch must not reveal the characters it located.** It may say WHERE
to look — which file, which section, which search string. The moment it says
WHAT is there, the curator's capture stops being an independent second reading
and becomes agreement with a model, and the model has entered the capture path
through the curator's eyes instead of through the keyboard.

That is not a hypothetical refinement. It is why this apparatus was captured
blind, and why the disagreement between the fetch and the page was visible at
all. The same paste also corrected the record's provenance — the author had
written that the text descended from a book recension, and the Taishō note
reads 【原】拓本石田幹之助氏藏, a rubbing held by Ishida Mikinosuke.

**The sentence that travels: a fetch that tells you what it found has spent the
evidence you were going to check it against.**

---

# FINDING 54 — the ledger's span cap is aimed at the spectacular failure, and the ordinary interruption walks under it

`data/curation_cost.json` holds `max_measured_span_minutes: 240`, and `why_240`
states what it is for:

> *"A clock started and left running overnight writes a working day of
> `measured` minutes into the one number kill trigger 3 depends on, and it
> arrives labelled as the most trustworthy kind of figure this file holds."*

**An overnight clock trips it. A coffee break does not.**

```
started_at  2026-09-01T09:41:45Z    text_capture, eastasia-04-jingjiao-stele
session paused
stopped     2026-09-01T11:5x        clock read 131.3 minutes
real work   about 15
cap         240 -- not reached, not approached, silent
```

`stop` with no arguments would have written **131 minutes of `measured`
text_capture**: eight times the true figure, inside the cap, under the label the
file itself calls the most trustworthy kind it holds.

## Why this phase and this label

`text_capture` is the phase FINDING 48 said has a floor no tooling removes, and
ruling 46 says the per-tier means are the only place a curation-cost number may
be read from. So it is the phase most likely to be quoted at a close, and an
inflated figure there does not read as an error — **it reads as confirmation of
FINDING 48**, which is exactly the shape of a number nobody checks.

## What was done, and what was not

Closed as an **ESTIMATE with a written reason**, which is `stop --minutes
--because`, which is the tool's own escape hatch and is a diff. The 240 cap is
**not lowered**: a cap that fires on real work is a cap people route around, and
`why_240` argues that correctly at four hours. The defect is not the number.

**What is owed is a different instrument: the clock has no idea whether anybody
was at the keyboard.** A pause is not distinguishable from work by anything the
ledger can see, and the only honest fixes are a `pause`/`resume` verb or a
prompt on `stop` when a span is long relative to its phase's own history. Named
here, not built today, and it joins F5's list — which is now four owed
instrument changes and still one re-cut.

**The sentence that travels: the guard was written against the clock left
running overnight, and the clock left running over lunch writes the same kind of
lie under the same trusted label.**

---

# FINDING 55 — ruling 57 drew a reachability boundary around the MACHINE-ENGLISH tier, and the same boundary is silently bounding the quality of the PUBLISHED-TRANSLATION one

Ruling 57 redefined `verbatim_machine_english` as *"no English translation
reachable by the curator, with the search recorded"*, because the old definition
claimed a fact about the world that no curator could establish. That was the
right correction and it stands.

**What nobody noticed is that reachability bounds the other tier too, and in a
way no check can see.** `verbatim_with_provenance` requires a CITED PUBLISHED
translation. It says nothing about how good that translation is, how old it is,
or whether anyone has disputed it — and for one whole genre this corpus is
committed to, there is exactly one reachable English translation and it is from
1885.

## Measured on record 34

FINDING 45 established that the nineteenth-century sinologists translated the
dynastic histories and left the huiyao, the leishu and the geographies alone.
The corollary is that for the dynastic histories they are still, in 2026, the
only open English. Hirth 1885 renders 獲黝歙短人 as:

```
"they had caught blackish coloured dwarfs"
```

reading 黝 as a colour. 黝 and 歙 are also the names of two counties in Danyang
commandery — the reading under which the sentence means *the short people of Yi
and She*, local people of the Wu heartland, and not dark-skinned ones. The two
readings say different things about who those people were, and the difference is
of exactly the kind this corpus exists to be careful about.

**This record does not adjudicate it and must not.** What it does is carry an
1885 construal into the corpus as its English, cited and correct by every rule
this repository has, with nothing anywhere able to ask the question.

## The boundary, arriving from the other side

The reason this could not be made a gloss case is the same reason ruling 57
exists. A gloss requires a PUBLISHED alternative reading the curator can reach,
and four searches found no second English translation of this passage and no
open source stating the county reading. Leslie & Gardiner 1996 is print-only and
may settle it; nothing available here can say.

```
ruling 57   vme tier   the tier is bounded by what English a curator can REACH
FINDING 55  vwp tier   the tier's QUALITY is bounded by the same reachability,
                       and unlike the vme tier it records nothing about it
```

A `verbatim_machine_english` record must now state where its search stopped. A
`verbatim_with_provenance` record states only what it cited. **The tier that
admits it does not know is the one that writes its ignorance down.**

## What no check here can do

`ingest.verify` asserts `source_text[char_start:char_end] == chunk.text` —
internal consistency. `build_ui_data --verify` compares archived quotations to
the seed record. FINDING 48's sentence covers the original: *nothing in this
project compares a record to its source*. **Nothing compares a record's
translation to its original either**, and that is a larger hole, because the
English chunk is the one FINDING 13 measured the model quoting 45 times out of
45.

## What is NOT done

**No field is added.** The obvious move is a `translation_age` or a
`translation_contested` flag, and it is the wrong one twice over: it invents a
distinction in the hour its first case appeared, which is FINDING 32's
precedent, and both values would be curator judgements no check could verify —
`why_gloss_capability_is_DECLARED`'s situation without its discipline.

What is owed, and is stated so it is not re-derived: **the vwp tier should
record the boundary of its translation search the way ruling 57 makes the vme
tier record the boundary of its English search.** Not the age, not a verdict on
quality — just what was looked at and what was not. That is F5's, beside the
other four.

**The sentence that travels: the tier that admits it could not find an English
translation is the only one that writes down where it looked, and the tier that
found one writes down nothing at all.**

---

## Ruling 62 — a translator's hedged IDENTIFICATION counts as gloss material, it is declared with a discount, and the distinction it exposes is owed to F5

**`eastasia-05-liangshu-qin-lun` is gloss-capable on Hirth's `Fu-nan [Siam,
Cambodja?]`. The gloss count goes to 3 of 8. It is reported at F4's close, and
at G3, as *three, of which one is a hedged identification rather than a disputed
reading* — never as three equivalent cases.**

### The two readings of the definition, both of which are correct

```
what_gloss_capable_MEANS_mechanically
  a genuine alternative or hedged reading
  AND a statement that the reading is uncertain
  both inside a RETRIEVAL-ELIGIBLE chunk
```

`Fu-nan [Siam, Cambodja?]` is two named alternatives and a question mark, inside
`reference_translation`. **Mechanically it qualifies and there is no reading of
that sentence on which it does not.**

And the gloss arm was built to catch something else. Its four earlier cases are
undeciphered runes, a corrupt Latin legend, two scholarly readings of a
Nabataean epitaph, and one set of Chinese characters that two translators put in
two different countries. **In every one of them the SOURCE TEXT is contested.**
Here 扶南 is not in doubt at all; what Hirth is unsure of is which modern country
it answers to. The instrument exists to see whether a model will render a
disputed text confidently, and this case cannot see that, because nothing about
the text is disputed.

### Why it is taken, and by whom

The project owner ruled it in, with the discount attached, and that is recorded
because it matters who decided. **The alternative was for this session to refuse
it — and this session had a quota riding on the answer.** A curator who has just
seen the page and needs one more gloss record is not the right party to narrow a
definition, and neither is the model drafting the record.

Record 32 refused Satzinger's bare `(?)` four hours earlier, on two grounds
stated independently: that it sat outside the excerpt, and that it was *"a hedge
about a place-name reading rather than a published alternative reading with a
statement that the reading is uncertain."* **The second ground is the one this
ruling declines to apply here, and the difference is narrow and is named: a bare
`(?)` offers no alternative, and `[Siam, Cambodja?]` offers two.** That is a real
distinction and it is thin, and calling it thin in the ruling is cheaper than
discovering in F6 that nobody knows where the line is.

### The anti-loophole, which is the whole reason this is a ruling and not a note

A count that includes a weaker case and reports one number is a count that gets
easier to satisfy as the evidence gets thinner — ruling 56's sentence, one
quota over. So:

- **the discount travels with the number.** F4_RESULT, and any G3 reading, states
  the composition and not just the total.
- **the record says so itself**, in its own `reference_translation` and `notes`,
  where a reader who never opens this file will still meet it.
- **the gold case says so in its `why`**, which is the field a reader of the
  gold set actually reads.

Three places, because the count is the only thing anyone reads and the count is
the only thing G3 will read.

### What is owed

**The definition should distinguish a contested READING from a translator's
hedged IDENTIFICATION, and today it cannot.** Both are "a hedged reading and a
statement that the reading is uncertain" to any checker, and they are different
evidence about different failure modes. That is a change to
`corpus_tiers.json`, which rulings 53 and 58 have each declined to re-cut
mid-tranche and which ruling 60 declined a third time this session.

It joins F5's list, which is now **five owed instrument changes** against one
re-cut with two tranches of evidence: ruling 53's deferred vme ruling, ruling
58's per-region language rule, FINDING 51's per-sub-tranche gloss delivery
check, FINDING 55's translation-search boundary on the vwp tier, and this.

**The sentence that travels: the definition could not tell a disputed text from
an uncertain translator, and the quota could not tell a strong case from a weak
one, so the ruling had to carry both distinctions in prose.**

---

# FINDING 56 — corpus_tiers.json's gloss rule was never mechanically checked, and writing the checker produced a STRICTER rule nobody had agreed to

`corpus_tiers.json` has said since F1 what gloss capability means:

> *"a genuine alternative or hedged reading AND a statement that the reading is
> uncertain, both inside a RETRIEVAL-ELIGIBLE chunk. Not in `notes` — the notes
> field is not chunked and the model never sees it."*

F3 broke that rule twice in one session, declared one gloss record instead of
two, and the remedy was `gloss_capable_declared`: a list in a sidecar, checked
for everything mechanical ABOUT the declaration — that the record exists, that
its tier can carry a case, that the quota is not exceeded — and **nothing at all
about whether the hedge is in a chunk.** The one clause the rule actually turns
on was the one clause no check read.

It is checkable, through the CASE rather than the record. A
`refusable_with_gloss` case declares `expect_hedge_any`; if no retrieval-eligible
chunk of the document it expects to be quoted contains any of those strings, the
corpus cannot support the hedge and the case can never pass for reasons that
have nothing to do with the model. Added in F4, over all six gloss cases,
failing rather than reporting.

## The part worth recording is what the FIRST draft asserted

It required **every** assertion group to be satisfiable from ONE chunk. It went
red immediately, on `raqosh-epitaph` — a case curated long before this session:

```
arabia-03-jsnab17::original::000      Rqwš  +  "two competing scholarly readings"
arabia-03-jsnab17::translation::000   Raqash  +  "curse"
```

**The case is built that way deliberately and its own note says so:** the hedge
sits in the source chunk so that *"an answer CAN know the reading is contested
without being told."* An original and its published translation are two chunks
by construction, and every `expect_quoted_from_original` case in this gold set
depends on both being reachable.

So the check was wrong and the case was right. **`corpus_tiers.json` makes a
claim about the RECORD's capability, and the first draft turned it into a claim
about the CASE's assertions — a different and stricter rule, invented in the
hour the checker for it was written, by the session that had a gloss quota
riding on the outcome.** That is FINDING 32's precedent and ruling 62's
situation, arriving in a checker instead of a definition.

The stricter idea survives as a COUNTED line rather than an assertion — five of
six gloss cases resolve from a single chunk, `raqosh-epitaph` needs two — because
a case needing three chunks of one record is worth seeing and is not a failure.

## What caught it

Not a review, and not the session that wrote it. **A record curated in an
earlier tranche, by a curator who had written down why it was shaped that way.**
The note that saved this was defensive prose in a gold case, aimed at nobody in
particular, and it is the reason the wrong rule did not become the rule.

## What is NOT covered, stated rather than implied

`scripts/mutate_part8.py` mutates `eval/goldset.py`, `eval/answer_eval.py` and
`eval/run_answer_sweep.py`. It does not mutate `eval/test_answer_eval.py`, so
assertions there that read the CORPUS and the GOLD SET rather than a module's
behaviour have no mutation proving they can fail. This new check joins
`test_a_record_cannot_falsify_a_refusal_case` and the quoted-from-original quota
in that class. **Three data-driven guards, none of them mutation-covered, and
this is the first time it has been written down.** Owed, and it is a different
kind of owed from the other five: those are instrument changes, this is coverage
of instruments that already exist.

**The sentence that travels: writing the checker for a rule is an invitation to
write a stricter rule by accident, and what caught it was a record curated
before this session by somebody who explained themselves in a note.**

---
---

# Rulings 63 to 65 and FINDING 57 — declared 2026-09-04, F4 PART 3's FIRST ACT, BEFORE THE RANKING RUN

*Date from the host, not from a document: `date -u +%F` printed `2026-09-04`.
That is a FOURTH distinct UTC date in Block F. Ruling 50 booked a ninth session
to buy a third; this one arrives for free because Part 3 is a separate day.*

*Every line below was written before `eval/run_ranking_check.py` was invoked
and before `eval/ranking_runs/` was opened. Rulings 55 and 61 are the only two
pre-registered predictions this project has ever made, both are denominated in
the BASELINE arm of the run this session is about to take, and both are cheap
to spoil. So everything that had to be decided at F4's close and could be
decided without a rank was decided while nobody had seen one — which is ruling
39's discipline for the eighth time in this block, and the first time it has
been applied to a session's own reading of its instruments rather than to its
records.*

---

## Ruling 63 — Sub-Saharan Africa's two unfilled `verbatim_machine_english` slots are ruling 53's NEITHER outcome, and it is recorded in ruling 53's own words

**F4 delivered 5 records against 7 allocated. Both missing records are Sub-Saharan
Africa `verbatim_machine_english` slots. Ruling 53 wrote three outcomes before
the hunt began and ruling 58 established, within four hours, which one fired:
Ge'ez fails on the ROME criterion, not on the translation criterion. That is
FINDING 38's supply problem and it is not FINDING 41's search problem. NEITHER.**

### Why this is a reading and not an excuse

Ruling 53's first two outcomes both require Africa's vme delivery to be evidence
about a SEARCH:

```
NARROWS            Africa delivers 2 honest vme records, each with its failed
                   English search written down -> FINDING 41 becomes a rule about
                   where a hunt LOOKS rather than about the tier
STANDS AS WRITTEN  Africa delivers 0 or 1 and the disqualifying reason is again
                   somebody has already translated this well and posted it
NEITHER            Africa delivers 0 or 1 for a different reason -- no open
                   transliteration, a text outside the window, a source that
                   refuses automated fetching
```

Africa delivered **0**, and no candidate was disqualified because somebody had
translated it. Littmann's *Deutsche Aksum-Expedition* IV (1913) is public domain,
downloadable in full, prints Aksumite inscriptions in original script with
transliteration and **German translation only** — which is the
`verbatim_machine_english` profile exactly, arriving in the region ruling 53
named as its test, in the prestige genre FINDING 45 says gets translated. Its
contents were read through. **Every text in it that touches Rome is either Ezana,
which this corpus already holds, or Sembrouthes, disqualified because a Wikipedia
editor attributed his English.** Kaleb (RIÉ 191) and Wa'zeb (RIÉ 192) are not in
Littmann; the RIÉ is not open and the 2019 Drewes/Kropp edition is French and
print-only.

So the texts that were reachable and untranslated did not touch Rome, and the
texts that touched Rome were held or attributed. **The window closed on the
subject, not on the language.**

### The part that costs something to write

**Ruling 53 designed a test and the test did not run.** NEITHER is not a third
result on the same axis as the first two; it is the statement that this tranche
produced no evidence about the axis at all. F5's deferred vme ruling therefore
inherits **an experiment that was not performed**, not a null result — and those
are read differently by anyone deciding whether to keep the tier.

East Asia's single vme slot was filled (record 35, `eastasia-06-cefu-yuangui`).
Ruling 53 already said what to do with it: *"One slot in a tradition with its own
enormous English-language scholarship decides nothing, and its outcome is
reported without being read."* It is reported here and it is not read.

**And FINDING 45's genre seam is untested in Africa.** The seam was discovered in
the East Asia hunt and it predicts where to look before the looking starts — but
in Africa the Ge'ez route closed on Rome before genre could be aimed at anything,
and Littmann is itself the prestige genre and is fully translated into German,
which FINDING 45 already says. So the one instrument F4 built for this tier has
been exercised in one region.

### The anti-loophole, and why a zero is the honest number here

Ruling 53's anti-loophole exists because **F4 could have reached two vme records
by not looking, and every check in this repository would have passed**: an empty
`translation_source` is what a thorough search and no search both produce.

A zero cannot be reached that way. It is the one delivery number that costs
something to report, and the reason behind it is checkable in the direction that
matters: **anybody who wants to falsify this ruling names a Ge'ez text that
touches Rome, sits inside 27 BC to 1204 AD, and is printed in an open volume
without an English translation.** That is a smaller thing to ask for than *"prove
you searched"*, and it is the shape ruling 57 gave the whole tier.

### What is NOT done

**The allocation is not re-cut.** Ruling 53 declined one mid-tranche re-cut of
`data/corpus_tiers.json`, ruling 58 declined a second, ruling 60 declined a
third and ruling 62 declined a fourth. A fifth in the same block, in the session
closing it, on the tranche that missed, would be a block editing its instruments
to fit what it found.

**The shortfall is not absorbed.** `check_delivery` already reports a shortfall
as progress rather than failing, which is correct and is also exactly how a
shortfall becomes invisible. F4_RESULT carries it as two named records that do
not exist, in a region that is at 3 source-language records against a floor of
4 — and ruling 58 has already said that three of those are Greek.

---

# FINDING 57 — a suite was fixed in the commit that found it broken, and three consecutive state blocks have reported it broken ever since

`scripts/test_recover_baseline.py` is listed `RED, see below` in
`F4_PART2_START.md`, and `STILL RED` in `F4_PART3_START.md`, both on
`corpus_version` and `serving_stack`. Run today, at `935c35a`:

```
44 passed, 0 failed          (1 skip: sqlglot not in this interpreter)
  ok   GUARD every native payload key is either recoverable or named in ABSENT
```

It is green, and it cannot have been anything else at any point in F4. The guard
reads three files and nothing else, and all three are **byte-identical from
`e7d932e` to `HEAD`**:

```
                                        e7d932e  58c6b77  4f95db2  HEAD
scripts/recover_answer_baseline.py      f00c745  f00c745  f00c745  f00c745
scripts/test_recover_baseline.py        58b1b8f  58b1b8f  58b1b8f  58b1b8f
answer/run_answer.py                    1af810a  1af810a  1af810a  1af810a
```

`e7d932e` is F3's own commit, and its message is *"the baseline check pays for
itself in an hour — FINDINGS 36 and 37"*. **The commit that discovered the
redness is the commit that ended it**, by naming `serving_stack` in `ABSENT` as
unrecoverable and `corpus_version` as a deferred decision. F4 Part 1's state
block then wrote `RED`, Part 2 copied it, Part 3 wrote `STILL RED`, and F4 Parts
1, 2 and 3 each carried a step for work that had already been done.

## The remedy for the last one of these is what caused this one

FINDING 36's closing move was *"`scripts/test_recover_baseline.py` is now listed
as the EIGHTH suite"* — FINDING 31's lesson, one suite over. It went into
`F3_RUNBOOK.md`'s command list. It did **not** go into the block underneath,
which is where the other seven suites carry the number they printed:

```
ingest.verify            All integrity checks passed.
ingest.test_fidelity     42 passed, 0 failed
ingest.test_cost         59 passed, 0 failed
eval.test_answer_eval   360 passed, 0 failed
eval.test_ranking_check 236 passed, 0 failed
answer.test_answer      150 passed, 0 failed
ui\test_build_ui_data.py 14 passed, 0 failed
scripts\test_recover_baseline.py            <- in the command list, and nowhere here
```

**It is the only one of the eight whose expected output is prose.** A suite with
a number is compared. A suite with prose is transcribed — and this one was
transcribed three times, each time by somebody reading the previous document
rather than the suite, which is the exact mechanism FINDING 34 measured on a
date and FINDING 47 measured on a commit.

## What it actually cost, which is not the wasted step

Three budgeted steps that were not needed is the cheap half. The expensive half
is this: **a green suite carried as red is a suite whose next real failure reads
as the old one.** `answer/run_answer.py`'s archived payload has grown a key twice
in this project's life — `corpus_version` in D4 and `serving_stack` in Block E —
and each time this guard went red. Had it grown a third in F4, the guard would
have gone red for a NEW reason into a state block that already said RED, and the
new reason would have been indistinguishable from the stale sentence describing
the old one.

That is FINDING 36's own defect turned inside out. FINDING 36 was a suite red and
unlisted. This is **a suite listed, green, and reported red**, and the second is
worse, because the first is silent and the second is reassuring in the wrong
direction.

## The rule, which is FINDING 47's applied one document earlier

FINDING 47 established that *"a suite number in a result document should name the
commit it was run at."* The state block at the head of a START document is the
same claim made earlier and read more often. So:

**A suite named in a state block carries the number it last printed and the
commit it printed it at. A suite whose entry is a word rather than a number has
not been run — it has been remembered.**

`STARTUP.md` and the runbooks are amended in F4's close. Nothing else changes:
the suite is green and there is nothing to fix in it.

**The sentence that travels: the remedy for a suite nobody listed was to list it,
and it was listed in the place that holds commands and not in the place that
holds numbers, so for three sessions it was named and never read.**

---

## Ruling 64 — the `corpus_version` deferral is DECIDED: a recovered payload rebuilds the corpus identity it can prove, under its own key, and `corpus_version` stays absent

**FINDING 36 deferred one question to F4 by name: whether a recovered payload may
carry a corpus identity missing `seed_record_count` and `record_hashes`. It may
not carry it under `corpus_version`. It carries what the `answers` row proves
under `recovered_corpus_identity`, whose `basis` is the literal `"recovered"`,
whose hash map is named `cited_record_hashes` and never `record_hashes`, and
which no reader of `corpus_version` can see. `corpus_version` remains in
`ABSENT`, with its reason rewritten from a deferral to a decision that points at
the replacement.**

### Why not under `corpus_version`, when the evidence is real

`answer_store.corpus_version(conn)` has a shape, and the shape is a contract:

```
algorithm  scope  source  seed_record_count  seed_corpus_digest  record_hashes
                                                                 ^ THE WHOLE CORPUS
```

`answers` holds `seed_corpus_digest`, `corpus_digest_algorithm` and
`cited_record_hashes`. The last is **a subset by construction** — its own
docstring says it is *"the subset of the corpus version the answer actually
cited"*, and that it writes a null hash for a cited document absent from the
version, precisely so that two different absences cannot be confused.

`corpus_moved` diffs `record_hashes` before against after and reports
`vanished` for every key on one side and not the other. **A cited-only map placed
under `record_hashes` makes every uncited record in the corpus report as
vanished** — a true measurement, correctly recovered, producing a false sentence
because it was filed under a name that means something else. FINDING 34's family,
and this project has now met it on a date, on a commit, on a quota's subject, and
here on a field's scope.

### And ruling 49's `basis` has two values on purpose

`sweep_corpus` classifies a run's corpus as `recorded` or `unidentifiable`, and
ruling 49 made that classification decide what may write `calibrated: true`.
**A reconstruction is neither.** It is not `recorded`, because nothing recorded it
at run time; it is not `unidentifiable`, because the database can prove it.

Adding a third value is a change to the field ruling 49 made load-bearing for
calibration, proposed in the session closing a tranche. Rulings 53, 58, 60 and 62
each refused a mid-tranche re-cut of the file they turned on. **This is the fifth
refusal and it is the first one outside `corpus_tiers.json`**, which is worth
saying: the discipline is about the timing, not about the file.

The separate key is what makes the refusal free. `sweep_corpus` reads
`corpus_version`; it will not find one; it will answer `unidentifiable`, which is
the true answer about a reconstruction and is already the safe one — *"an
unidentifiable corpus is never read as the current one."*

### And the evidence is not thrown away

The alternative was to close the deferral as an impossibility. It is not one, and
FINDING 36 already said so. `answers` genuinely holds the digest each answer was
made against; discarding it because it does not fit an existing key would be the
`pointer_only` mistake — refusing a partial record because it is not a whole one.

```python
"recovered_corpus_identity": {
    "basis": "recovered",              # NOT one of ruling 49's two values
    "algorithm": ...,                  # answers.corpus_digest_algorithm
    "seed_corpus_digest": ...,         # answers.seed_corpus_digest
    "cited_record_hashes": {...},      # answers.cited_record_hashes -- CITED ONLY
    "scope": "the digest this answer was stored with; the hash map is the CITED "
             "subset and is not the corpus",
    "absent": ["seed_record_count", "record_hashes"],
}
```

`absent` inside the block, as well as `corpus_version` inside `ABSENT`, because a
reader who reaches this key has stopped reading the payload's top level.

### The anti-loophole

Four guards, and they are guards rather than notes because the failure mode here
is a later session helpfully renaming the key:

- **a recovered payload never carries `corpus_version`.** Asserted over the key
  set, not over the code that builds it.
- **`recovered_corpus_identity` never carries a key named `record_hashes`.** The
  whole ruling is that the two names mean different things.
- **`basis` is not `recorded` and not `unidentifiable`.** Asserted against
  `answer_eval.sweep_corpus`'s own vocabulary, imported rather than re-spelled —
  `SOURCE_LANGUAGE_TIERS`' reason, and ruling 56's.
- **`ABSENT`'s `corpus_version` entry names the replacement key.** An entry that
  says a thing was not rebuilt, in a payload that rebuilt part of it elsewhere,
  is worse than either.

### What is NOT done

**The 16 recovered archives already on disk are not rewritten.** They were
written before this ruling and their own `recovered_absent` correctly says
`corpus_version` was not rebuilt. Backfilling would give a payload a corpus
identity it did not have when it was written, which is a provenance moving
backwards — the thing `archived_status` and `superseded_diagnosis` exist to
refuse. Two shapes of recovered payload now exist on disk;
`ui/build_ui_data.py` already handles two shapes for a different reason and this
is named rather than tidied.

**`SELECT_ANSWERS` gains three columns and nothing else changes about recovery.**
It is read-only, it stays read-only, and the read-only guard already covers it.

---

## Ruling 65 — F4 closes on the BASELINE arm alone, and the C2 FUSED arm is recorded as DELIBERATELY NOT RUN

**`eval/gold/query_renderings.json` has no entries for the eight ranking pairs
ruling 54 added in Part 2. The BASELINE arm does not read that file and is
unaffected. The fused arm is not run at F4's close, F4_RESULT prints its row as
NOT RUN with this reason, and the eight pairs' missing renderings become a named
debt for F5.**

### Three reasons, and the second is the one that decides it

**It answers no question F4 asked.** Rulings 55 and 61 are the only two
pre-registered predictions this project has, and both are denominated in
BASELINE. A fused number at F4's close would be a number with nothing to compare
it to and no prediction riding on it.

**Rebuilding the renderings moves the instrument inside the session that reads
the predictions off it.** Every fused run records `renderings_digest`. Rebuilding
for the eight new pairs changes that digest, in the same commit as the run whose
two predictions are the whole point of taking it. That is FINDING 47 exactly — a
suite reported at a tree by the run that the same commit moved — and FINDING 47
is four days old.

**It costs chat calls.** `scripts/build_query_renderings.py` spends them, and
ruling 46's ledger is not the only budget in this project.

### What it costs, said plainly rather than left as a gap

C2's arm goes another tranche without a reading, and the eight new pairs have no
renderings, so the *next* fused run cannot include them either without the same
spend. **That is a debt and it is now the sixth item on F5's list** — five
instrument changes, one coverage gap, and this.

### The anti-loophole

**An arm that was not run must be visible as an arm that was not run.** F4_RESULT
prints the fused row with the word and the reason, never blank and never omitted.
Ruling 52's sentence, one instrument over: *named, never merely subtracted.* A
missing row and a row reading NOT RUN are the same absence to a reader who is
skimming, and only one of them can be argued with.

---

# The sentences that travel, from F4 Part 3's opening

**Ruling 53 designed a test and the test did not run, so F5 inherits an
experiment that was not performed rather than a null result.**

**The remedy for a suite nobody listed was to list it, and it was listed in the
place that holds commands and not in the place that holds numbers, so for three
sessions it was named and never read.**

**A green suite carried as red is a suite whose next real failure reads as the
old one.**

**A cited-only hash map under a whole-corpus name is a true measurement producing
a false sentence, and nothing in the payload would have said which.**

**A missing row and a row reading NOT RUN are the same absence to a reader who is
skimming, and only one of them can be argued with.**

---

# FINDING 58 — FINDING 46 went looking for a defect's siblings and enumerated four files by name; there were eight, and the one it missed is the only one that was live

FINDING 46, five days old, found `startswith("FAIL")` — matching the `FAILED`
of a suite's own summary line and harvesting a phantom guard named `ED (n)` —
in three harnesses beyond the one FINDING 37 fixed, and a fourth where the same
code is latent. Its closing move: *"All four fixed in F4, with the space."*

**`scripts/` holds EIGHT files that harvest guard names out of a suite's
stdout.** Today, at `935c35a`:

```
FIXED by FINDING 37/46      places  ui_places  fidelity  ranking  part8
STILL BARE                  cost        LIVE  -- ingest/test_cost.py:728
                                              prints FAILED (n)
                            recover     latent
                            part7b      latent
                            distractors latent
```

## The live one is the ledger's

`scripts/mutate_cost.py` drives `ingest.test_cost`, which ends a red run with
`print(f"FAILED ({len(failures)})")`. So a bare matcher harvests `ED (n)` into
that harness's BASELINE block — and the BASELINE block is the thing that decides
whether a mutation is `verified` or `UNVERIFIED`. **A harness that invents a
failing guard reports a green suite as partly red**, which FINDING 46 already
named as the one thing a mutation harness must never do quietly.

It is the ledger's harness. Ruling 46 says the per-tier means in
`ingest.cost_log` are *the only place a curation-cost number may be read from*,
ruling 52 and ruling 59 have both added rules to it this block, and
`ingest.test_cost` went 46 → 59 → 64 assertions in two sessions. It has also not
been run since `a5c0ae6`, which every state block since has said, and which is
the same silence that hid the other four: *"it survived because it had not been
run."*

## The fourth latent one had never been searched for, because it is not called that

`scripts/mutate_distractors.py` has no `failures_from`. It has the identical
three lines inlined in `run_suite()`. **Every search for this defect — FINDING
46's, and the first pass of this one — looked for a function name, and the
defect is in the code.** It was found by grepping for
`startswith("FAIL")` across the directory, which took one command and would have
taken one command five days ago.

## The mechanism is FINDING 46's own, happening to FINDING 46

> *"A defect is fixed in the file where it was found, and the search for its
> siblings is a separate act that nobody scheduled."*

FINDING 46 **scheduled** that act. It then performed it by listing the harnesses
it happened to have open. **An enumeration is not a search**, and the difference
is invisible in the write-up, because a list of four names reads exactly like a
complete list of four names. FINDING 49 said the same thing about a rule written
down in one file; this is the same sentence about a fix applied in four.

All four are fixed here, with the space, and the space alone is not the remedy.

## What is owed, and why it is not done today

**Eight copies of one three-line rule is FINDING 14's shape inside the machinery
built to catch FINDING 14's shape.** The eighth careful copy is not the answer;
one matcher in one module, imported by all eight, is — for
`SOURCE_LANGUAGE_TIERS`' reason, which ruling 56 has already quoted this block:
*a rule spelled out twice is a rule that disagrees once.* Spelled out eight
times, it has now disagreed twice.

Not done in F4's close: it edits eight harnesses at once, **none of them can be
run through the bridge** — each call is killed at 45 seconds and a killed
harness leaves a live mutation in the tree — and a consolidation nobody can
execute in the session that writes it is a consolidation that lands unverified.
It joins F5's list.

**The sentence that travels: the remedy for a defect nobody had searched for was
a search, and the search was performed by listing the files that were already
open, which is why the only live instance is the one that was not on the list.**

---

# FINDING 59 — the rule against running a harness through the bridge is written against a TIMEOUT, and today it was a DISCONNECT

`F1_RUNBOOK.md`, unchanged since F1:

> *"Never run a suite or a harness through the Cowork bridge: each call is
> killed at 45 seconds and a killed harness leaves a live mutation in the tree."*

The bridge's per-call limit is no longer 45 seconds. `scripts/mutate_recover.py`
ran through it today — 17 mutations, all verified, sources restored
byte-identical — which is what made the next one look safe. `scripts/mutate_cost.py`
was started the same way and the **workspace disconnected mid-run**:

```
git status   M ingest/cost.py

-    direction = "down" if b < a else ("up" if b > a else "flat")
+    direction = "flat"
```

A live mutation, sitting in the tree, in the module ruling 46 names as the only
place a curation-cost number may be read from — and it is a mutation that makes
`trend_line` report every tier as flat, which is a plausible-looking sentence
rather than a crash.

## The reason the rule gives is not the reason the rule is right

`mutate_cost.py` restores its sources in a `finally`, from bytes, and its
restore check compares bytes — every remedy this project has built since Block D.
**None of them run in a process that was killed.** So the exposure is not the
45-second limit and never was; it is that the restore lives inside the process,
and any way of ending that process early — a timeout, a disconnect, a laptop
lid — leaves the tree mutated and every check downstream green against it.

**A rule whose stated cause is fixed reads as a rule that has expired.** The
limit changed, the sentence stopped describing the world, and the hazard did not
move at all. That is the same shape as FINDING 57 one layer down: a written
status carried forward while the thing it described went elsewhere.

## What caught it, and what would not have

`git --no-optional-locks status --porcelain`, run before the next edit — FINDING
52's habit, which exists for a different defect and cost nothing here. **No suite
would have caught it.** `ingest.test_cost` has 64 assertions and none of them
asserts a direction word; `ingest.verify` does not read `ingest/cost.py`; the
mutation harness that produced it had already exited. It was recovered with
`git cat-file blob HEAD:ingest/cost.py` written back as BYTES, per
`BLOCK_E_RUNBOOK.md` — `git checkout` through the bridge leaves an
`.git/index.lock` the bridge cannot delete.

## What changes

The runbooks' sentence is amended to give the reason rather than the number:
**a mutation harness restores its sources from inside itself, so it must be run
where nothing else can end it — on the host, in a window somebody is watching.**
`scripts/mutate_recover.py`'s 17 verified mutations are reported here as having
been run through the bridge, and F4_PART3_RUNBOOK asks for them again on the
host, because a harness run that happened to survive is not evidence that it was
safe to take.

**The sentence that travels: the restore lives inside the process, so every
argument about how long the process is allowed to live is an argument about the
wrong thing.**

## FINDING 57, continued — the remedy was applied and the number it wrote was one short

`F4_PART3_RUNBOOK.md` gave `scripts\test_recover_baseline.py` an expected total
of **55**, which is what FINDING 57 asked for: a number instead of prose. The
host printed **56**.

```
bridge      skip sqlglot not installed (pip install -r requirements-dev.txt)   55
host        ok   every query parses as PostgreSQL                              56
```

The runbook already carried this exact caveat for `answer.test_answer` — *"reads
149 through the bridge, because sqlglot is in the host venv and not in the
bridge's interpreter; 150 is the number to expect on the host"* — because F3 had
been bitten by it and written it down. **The caveat was carried for the suite
that had it before, and not derived for the suite that had just been given a
number.** Both suites parse SQL with sqlglot; only one of them was known to.

So the rule FINDING 57 adopted is not enough, and the correction is one clause:

**A suite number in a state block names the commit it was printed at AND the
interpreter that printed it.** A number measured where an optional dependency is
missing is a different number, and it is off by exactly the assertions that
dependency enables — which is a silent, plausible, small discrepancy, and
therefore the kind that gets reconciled by editing the expectation.

Nothing is wrong with the suite. `56 passed, 0 failed` on the host is the number
F4_RESULT carries, with `55 (bridge, sqlglot absent)` beside it rather than
instead of it.

**The sentence that travels: the remedy for a status that was remembered was to
write down a number, and the first number it wrote was measured somewhere the
document did not say.**
