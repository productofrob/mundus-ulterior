# F6 RESULT — seven of seven placed, the last per-region floor in Block F
# closed, and F6 IS CLOSED

**`F6.closed` is `true` as of this document, and not before it.** It was set by
locating the sub-tranche named `F6` in
`data/corpus_tiers.json → target_mix → allocation → sub_tranches`, **by name and
not by line number** — F5 Part 3's first attempt at that edit set the wrong
sub-tranche's flag.

---

## THE STATE BLOCK IS GENERATED. NOTHING BELOW IT IS RESTATED.

Run by `python -m ingest.verify --state` on 2026-09-06. PASTE THIS BLOCK. Do not restate it.

```
documents: 47   chunks: 153   parallel pairs: 33
note: paraphrase flag LIFTED on 'weilue': LIFTED 2026-08-22, FINDING 11. eastasia-01-weilue's original_text_excerpt is 221 verbatim characters from zh.wikisource 三國志/卷30 and classifies as verbatim_original on its own merits. The manifest's flag marked SUSPICION and nothing in the pipeline ever turned suspicion into a determination; when two of its entries were finally checked they came back opposite ways. Leaving the flag on would have the corpus report a sourced text as paraphrased.
note: retrieval-eligible non-English chunks by language: {'xsa': 2, 'xna': 2, 'arc': 3, 'grc': 16, 'lzh': 7, 'pal': 6, 'xpr': 2, 'non': 1, 'gmq-pro': 3, 'oty': 1, 'san': 2, 'ocm': 1, 'omy': 2, 'gez': 1}
note: W1 placements: 46 placed + 1 declared unplaceable = 47/47 considered (G1's target was 24, met), 28 with a named place (G1 wanted 17), 65 distinct gazetteer ids, 1 contested (G1 criteria 1 and 3). Grounds: {'identified': 3, 'regional': 81, 'stated': 64}. Resolution is not checked here — run `python -m ingest.gazetteer --check`, which is the only thing that turns an id into a coordinate.
note: rights positions (ruling 74, column built in F6): {'open_licence_stated': 3, 'permission_stated_no_licence': 3, 'public_domain': 1, 'all_rights_reserved': 1, 'two_positions_stated': 1, 'unread': 38}. 38 of 47 record(s) are UNREAD -- nobody has read that source's rights position since FINDING 69, which was produced by two licence claims that were wrong in opposite directions in a single session. `unread` is a state of this project's knowledge and not of the source. COUNTED, NOT GATED, and never derived: citation_original is prose, and a matcher over it would read the word `open` in a sentence about reachability, which is FINDING 69 with a regular expression in front of it.
note: quotation cases: 9 ask WHICH chunk was quoted (target 6 at 60) and 4 ask only WHETHER anything resolved. Ruling 56: they are two questions under one name. The second line rises by construction with every verbatim_machine_english record, so a total that is climbing is not evidence that this system quotes sources rather than translations.
note: record tiers: verbatim_with_provenance 29/29, verbatim_machine_english 4/10, published_translation_only 2/4, catalogue_record 11/16, pointer_only 1/1 (F1 target at 60 records). Progress, not a threshold: the mix is a target for the end of Block F and a suite that failed on it throughout would be ignored throughout.
note: source-language records by region (F1 floor 4 each at 60): {'Arabia': 6, 'East Asia': 7, 'Persia': 4, 'Scandinavia': 4, 'South Asia': 4, 'Southeast Asia': 4, 'Sub-Saharan Africa': 4}. Below the floor: none. An aggregate tier target met entirely inside two regions leaves the other five exactly as unable to answer a source-text question as they are now.
note: allocation (ruling 51): F3 8, F4 7, F5 7, F6 7, F7 7 = 36 record(s), every source-language record before every catalogue record. The sub-tranche a record was curated in is NOT a field on the record and is not derivable from one: this line reports the PLAN, and data/curation_cost.json in curation order reports what happened.
note: delivery against the allocation: 23 of 36 tranche record(s) curated. Gloss-capable declared 6/7 (5 contested_reading, 1 hedged_identification), with 2 declaration(s) left in sub-tranches still open and 7 slot(s) left on a tier that can carry one. The DECLARATIONS are the scarce number: slots are plentiful by construction, and a guard that read them reported an unreachable quota as progress for two sub-tranches (FINDING 51). A SHORTFALL is progress and is reported here; an UNREACHABLE quota is a failure above, because a target that can no longer be reached has already been missed and nobody re-curates a record.
note: source-language records by PROVENANCE rather than by language (ruling 58, in the shape FINDING 62 gave it): is the region SPEAKING, or being SPOKEN ABOUT? Arabia 6 = 5 local + 0 empire-language from the region + 1 about it, so 5 SPEAKING and 1 spoken about; East Asia 7 = 7 local + 0 empire-language from the region + 0 about it, so 7 SPEAKING and 0 spoken about; Persia 4 = 4 local + 0 empire-language from the region + 0 about it, so 4 SPEAKING and 0 spoken about; Scandinavia 4 = 4 local + 0 empire-language from the region + 0 about it, so 4 SPEAKING and 0 spoken about; South Asia 4 = 2 local + 0 empire-language from the region + 2 about it, so 2 SPEAKING and 2 spoken about; Southeast Asia 4 = 4 local + 0 empire-language from the region + 0 about it, so 4 SPEAKING and 0 spoken about; Sub-Saharan Africa 4 = 1 local + 2 empire-language from the region + 1 about it, so 3 SPEAKING and 1 spoken about. Regions with no source-language record in a language of the region: []. Regions with NO RECORD SPEAKING AT ALL -- neither in a language of the region nor in an empire language from it: []. FINDING 68, closed in F6: those two lists are different questions and only the first was ever printed, so a region whose own rulers wrote in Greek was reported in the same words as a region that is only ever written about. One text counted as a source-language record in more than one region: [[('Arabia', 'arabia-01-periplus'), ('South Asia', 'southasia-02-periplus-muziris'), ('Sub-Saharan Africa', 'africa-03-periplus-adulis')]]. COUNTED, NOT GATED. A language-only rule -- the one ruling 58 proposed -- cannot tell a record whose findspot is in the region from a Roman-world text about it, because both are grc, so it would refuse the two records ruling 58 argued to keep and admit the one it should refuse.
note: curation cost: 23 record(s) timed, 24 excused, 6 RETIRED (ruling 52: kept and named, counted in no mean). Comparator: within_tranche (ruling 46 -- nothing records what record 12 cost). Run `python -m ingest.cost_log report` for the per-tier table; it is the only place a curation-cost number may be read from.
loader warnings: 6
  ! arabia-02-palmyrene-tariff: empty reference_translation, no translation chunk emitted
  ! eastasia-06-cefu-yuangui: empty reference_translation, no translation chunk emitted
  ! eastasia-07-tang-huiyao: empty reference_translation, no translation chunk emitted
  ! seasia-06-kedukan-bukit: empty reference_translation, no translation chunk emitted
  ! seasia-07-talang-tuo: empty reference_translation, no translation chunk emitted
  ! africa-07-cosmas-sasu: empty original_text_excerpt, no original chunk emitted

All integrity checks passed.
```

And the eleven instruments, generated by `python scripts/state_block.py`, run on
the bridge under an interpreter with `psycopg[binary]`, `sqlglot` and
`python-dotenv`:

Run by `python scripts/state_block.py` at 114ce15 on 2026-09-06. PASTE THIS BLOCK. Do not restate it, and do not compute a figure in it from another figure -- FINDING 76.

```
ingest.verify                        green, 47 documents
ingest.test_fidelity                 115   [green]
ingest.test_cost                     78   [green]
eval.test_answer_eval                425   [green]
eval.test_ranking_check              258   [green]
answer.test_answer                   150   [green]
ui/test_build_ui_data.py             19   [green]
scripts/test_recover_baseline.py     56   [green]
scripts/test_harnesses.py            43   [green]
python -m ingest.gazetteer --check   GREEN
node ui/check_ui.mjs                 GREEN
```

*Mutation harnesses are HOST ONLY (FINDING 59) and are not in that table. They
were last run green on 2026-09-06 — `mutate_fidelity` 70/70, `mutate_cost` 58/58
— BEFORE this session's four records. **They have not been re-run since** and
that is in the debt list below.*

---

# THE SEVEN RECORDS

```
41  persia-06-shahrestaniha           verbatim_with_provenance    Persia       pal
42  scandinavia-06-tjurko-bracteate   verbatim_with_provenance    Scandinavia  gmq-pro
43  scandinavia-07-rycksta-grikkium   verbatim_with_provenance    Scandinavia  non
44  africa-06-ezana-rie189            verbatim_with_provenance    Africa       gez
45  arabia-07-cih541                  verbatim_with_provenance    Arabia       xsa   GLOSS
46  eastasia-08-songshi-fulin         verbatim_with_provenance    East Asia    lzh
47  africa-07-cosmas-sasu             published_translation_only  Africa       en
```

**Six source-language records and one published translation, exactly as rulings
76 and 77 left the allocation.** F6 placed no catalogue record at all.

## What the four records of this session are, in one sentence each

- **44 — RIÉ 189, lines 39–52.** ‘Ēzānā of Aksum's vocalized Ge‘ez: the tally of
  the Nubian campaign, the throne set up at Śadō, and the curse on whoever tears
  it down. **The first text this corpus has ever held in a language of
  Sub-Saharan Africa**, from Hatke's open-access *Aksum and Nubia* under CC BY-NC,
  quoting Bernand, Drewes & Schneider's *RIÉ* I for the text.
- **45 — CIH 541 Sadd Maʾrib 5, lines 80–92.** `mḥs²kt mlk Rmn` — **the
  ambassador of the king of Rome arrives at a South Arabian court in 548 CE**, in
  one sentence with the Negus, the king of Persia and three Arab rulers. Rome as
  one delegation among six, in the world beyond it. CC BY 4.0 on text and
  translation both. **Carries F6's one `gloss_capable` declaration.**
- **46 — 宋史 490 拂菻.** The Fulin embassy of 1081 and the two of 1091. **The
  corpus's East Asian view of Rome stopped at 643 CE and now reaches 1091**,
  inside the last century of the project's window, with a Byzantine king whose
  name ends 改撒.
- **47 — Cosmas Indicopleustes, *Christian Topography* II.** The Aksumite gold
  expedition to Sasu: five hundred traders, oxen and salt and iron carried six
  months inland, and the silent trade at a hedge of thorns. **The first record in
  this corpus of trade going INLAND** from the coast the Periplus describes.

---

# WHAT CLOSED

```
THE LAST PER-REGION FLOOR IN BLOCK F
  region              at F6 open   now   floor
  Persia                       3     4       4   RULING 76, record 41
  Scandinavia                  2     4       4   ruling 73, records 42 and 43
  Sub-Saharan Africa           3     4       4   record 44
  Below the floor: none.

AND THE DEFICIT THE COUNT DID NOT SHOW
  Africa was 0 local + 2 empire-language from the region + 1 about it —
  its two speaking records were African rulers writing in GREEK.
  It is now 1 local + 2 + 1, three SPEAKING.

THE FLAGSHIP TIER'S TARGET IS MET, THIRTEEN RECORDS EARLY
  verbatim_with_provenance 29/29 at 47 records, against a target set at 60.

F6's ONE GLOSS DECLARATION IS MADE
  gloss_capable declared 6/7. arabia-07-cih541, contested_reading.
  persia-06 and scandinavia-07 both carry declarable material and NEITHER is
  declared: a second declaration is over-delivery that check_delivery fails on.

TWO RIGHTS POSITIONS EXERCISED FOR THE FIRST TIME
  public_domain      africa-07-cosmas-sasu — the last of the seven to be used
  open_licence_stated x2 more, and one of them names a licence with NO VERSION,
                     which the column records as printed rather than levelling.
```

---

# THE FIVE FINDINGS

**FINDING 80 — the handoff document mis-describes the record it points the Africa
hunt at.** `africa-01-ezana-stone` is not "already the GREEK of a stone that also
carries Ge'ez". It holds no Greek, no Ge'ez and no Sabaean: its
`original_text_excerpt` is a bracketed instruction to a later session that
`classify_original` returns `('pointer', 'en', False)` on, and its translation is
a titulature quoted from a news website. Corrected in place in both documents
that carried the sentence.

**FINDING 81 — a gold refusal case named a fabrication marker the corpus acquired
four records later, and the guard that had never fired, fired.**
`eval.test_answer_eval` went 425 → 424/1 the moment record 44 landed:
`ezana-stone-geez` excludes `Lord of Heaven`, and RIÉ 189's published English
carries it. **The case survives — the corpus still holds no Ge'ez of the Ezana
Stone — and one marker dies**, because a phrase now grounded elsewhere is no
longer evidence of fabrication. Nobody could have caught this by reading.

**FINDING 82 — `classify_translation` hard-codes `lang = "en"`.** Every
translation chunk in this corpus is declared English by construction and nothing
checks it. That is why the East Asia slot could not take the Turfan Manichaean
text it was pointed at: parsigdatabase's Manichaean translations are **Persian**,
by its own interface heading, and would have entered the index declared English.
Not fixed here; a fix changes what every existing record declares.

**And two corrections to `F6_CURATION_START.md`'s own warnings.** `--refresh` did
not re-stamp anything today — 26 added lines, no changed ones — because the cache
had already been stamped this morning; the warning is date-dependent. And the
`grep -rn "== NN"` guard collides at 45 with a pacing assertion in
`eval/test_ranking_check.py`, which is the failure mode FINDING 66 exists to
remove.

---

# THE PRACTICE THIS SESSION ADDED, AND IT SHOULD BE STANDING

**EVERY CAPTURE WAS VERIFIED BY SHA-256 ACROSS TWO MACHINES.** The excerpt was
typed into a file on the bridge; the same span was sliced independently out of
the live page in the browser; digests were computed on both and compared.

```
record  field                    chars   digest (first 24)
44      original_text_excerpt      852   30b926e0d45f8ffd1023c589
44      reference_translation     1201   eb163366fd55408152e24174
45      original_text_excerpt      485   d48ef25adba2a910996291d3
45      reference_translation      682   a43e1fcdab78be68961dd415
46      original_text_excerpt      295   7ff3f9f7bd71fe23d6e08738
46      reference_translation     2779   12199def3bdee4a1161adaf1
47      reference_translation     2777   7f8b6d4d2877ea5095ef66a8
```

**It earned its keep on the second record it was used on.** The line-number
gutter on the DASI record is made of **non-breaking spaces, U+00A0, four per
line, forty-four in the span**. A curator retyping that passage would have typed
ordinary spaces and the record would have differed from its source in
forty-four characters with **nothing visible to see**. FINDINGS 48 and 50 are
that failure with a different codepoint and FINDING 53 is that failure with a
different file; a digest answers all three at once, and it answers them in a way
two texts read side by side cannot.

**And on record 46 it verified an EDIT rather than a paste.** Kanripo's `¶` line
markers and `<pb:...>` page markers were stripped by the same two rules in the
browser and on the bridge, and the digests were compared over the RESULT. The
editorial act is the part a curator's eye is worst at checking, and it is now the
part that is checked.

**Cost: about a minute a record.** It is in the `text_capture` line of each
ledger entry.

---

# WHAT F6 HANDS ON

## Owed by F6 and NOT DONE — the ranking run, and it is host-only

**`eval.run_ranking_check` cannot run from the bridge.** It needs Postgres:
`cannot reach Postgres at postgresql://mundus:mundus@localhost:5432/mundus`. So
do `run_ingest` and `run_embed`, so **the four records of this session are not in
the index at all**, and no ranking number in this repository yet knows they
exist.

**On the host, in this order:**

```
docker compose up -d db
python scripts/check_db.py
python -m ingest.run_ingest
python -m ingest.run_embed
python -m eval.run_ranking_check --with-distractors
python scripts/mutate_fidelity.py
python scripts/mutate_cost.py
```

**Three predictions are waiting on that run and all three were written before the
records existed:**

```
P1   ruling 78, a20214e.  tc-jabal-dabub sat at rank 6 with zero slack with three
     chunks of arabia-06-syllaeus inside its window. A FOURTH Arabia
     source-language record now exists — arabia-07-cih541, two retrieval-eligible
     chunks, both about a South Arabian monumental inscription naming Rome.
     PREDICTED: it falls out of the top 6, and ALL recall@6 moves off 0.727 for
     the first time since F4.

P2   ruling 78, a20214e.  probe-tamil-akananuru-en, also rank 6 with zero slack,
     with eastasia-07-tang-huiyao inside it. F6 has now placed one East Asia
     record and no South Asia record. PREDICTED: it falls, to a CROSS-REGIONAL
     crowder, which is ruling 70's mechanism and not ruling 73's.

P4   ruling 78, 2991e04, written after the Africa candidate was located and
     before the record file existed. FINDING 73 predicts Africa's six ranking
     pairs degrade as a group; FINDING 79 predicts that ONLY au-ezana-titles
     moves, because the other five expect GREEK chunks and record 44 contains no
     Greek at all. PREDICTED: au-ezana-titles falls, the five Greek-target pairs
     do not move. Three distinguishable refutations are named in the ruling.
```

**P1 and P4 are the interesting pair.** If P1 confirms, FINDING 79's resemblance
mechanism and FINDING 73's same-region mechanism BOTH predict it and the run
cannot tell them apart — record 45 is Arabia AND resembles the target. **Record
44 is the experiment that separates them**, because it is same-region and
resembles nothing.

## Debts inherited and still unclaimed

1. **A Swedish GeoNames dump** — closes both Scandinavian placements, which
   refused coordinates their source handed over. Still the cheapest work in the
   repository.
2. **`GUARD a reinstated_on that is not a date is refused`** and three guards in
   `mutate_fidelity` are in `UNMUTATED_AND_OWED`.
3. **A diffable manifest beside `ui/data.js`** (FINDING 74).
4. **`git log --follow` on `africa-03-periplus-adulis`** — its chunk-id drift is
   in every ranking run and unchanged.
5. A ranking pair targeting `eastasia-07-tang-huiyao`;
   `southasia-05-brihatsamhita` appearing nowhere in the ranking run; re-reading
   `arabia-04-jabal-dabub` and `eastasia-07-tang-huiyao` against ruling 74; the
   unlocated "two ṭ" sentence in Petrantoni; Dvivedī's mūla Bṛhatsaṃhitā 2.14; a
   GeoNames search for al-Ruwāfa.

## New debts this session created

6. **FINDING 82's fix** — a language check over translation chunks. It changes
   what every existing record's translation chunk declares and it is not a
   last-hour job.
7. **The Turfan Manichaean vein, recorded as a SEARCHED FAILURE and still open.**
   `parsigdatabase.com` and TITUS both work; what is missing is a reachable
   English translation. `M2 I` — Mani dispatching Mār Addā **into the Roman
   Empire** — remains the best unclaimed candidate this project has found for
   East Asia, and it is a Persian religious movement acting ON Rome rather than
   reacting to it.
8. **`betamasaheft.eu` returns 403 to a real browser**, at root and at
   `/inscriptions`, with its own page saying it is behind a firewall and inviting
   an email. The first negative ever recorded against the Africa slot. **The
   printed RIÉ corpus was NOT opened and no negative is recorded against it.**
9. **East Asia is now seven source-language records in ONE language.** Africa
   gained its first local language today; East Asia's seven are all Literary
   Chinese, and **no line in `ingest.verify --state` reports language
   concentration within a region**. A region that speaks in only one language is
   a narrower witness than its count suggests.
10. **`U 431 Åshusby`** — *"and he died abroad among the Greeks"* — found in F6
    and not taken. A live F7 candidate.

## Standing

The two older Scandinavian source-language records cite Wikipedia. Neither is
re-curated — nobody re-curates a record — but Runor now exists in this repository
with signa, persistent URIs, a named edition and a stated reuse permission.

**And `africa-01-ezana-stone` is a placeholder with a newspaper citation, and it
is one of the two members of the `published_translation_only` tier.** The other
is record 47. The tier's two members are a fair picture of how far this project's
standards moved between its seed corpus and Block F, and that comparison is worth
more than the count.
