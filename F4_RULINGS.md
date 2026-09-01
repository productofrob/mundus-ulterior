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

**The sentence that travels: the repository forbade git from rewriting a single
byte, and then seven files were rewritten by the tool that was reading them.**
