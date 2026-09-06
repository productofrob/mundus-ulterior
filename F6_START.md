# F6 START — F5 is closed at 5 of 7, the corpus is 40, and the strongest source this project has ever found is sitting unclaimed in front of you

**Read this before `F5_CANDIDATES.md` or `F5_PART3_RESULT.md`.** Those are F5's
hunt and F5's close. This is the operating document for F6.

---

## THE STATE BLOCK IS VERBATIM `ingest.verify` OUTPUT AND NOT A RESTATEMENT

**This is the first opening document in Block F that does not hand-copy its
predecessor's numbers, and FINDING 75 is why.** Three tier counts in F5 Part 3's
own documents were wrong because each was copied from the document before it
rather than counted from the corpus, and the instrument that prints the right
number had already printed it into that session. **If you need a figure, run the
command. If you quote a figure here, quote it from this block.**

Run on the host, at F5's closing tree, 2026-09-05:

```
documents: 40   chunks: 116   parallel pairs: 27

record tiers: verbatim_with_provenance 23/27, verbatim_machine_english 4/10,
  published_translation_only 1/5, catalogue_record 11/17, pointer_only 1/1
  (F1 target at 60 records)

source-language records by region (F1 floor 4 each at 60):
  {'Arabia': 5, 'East Asia': 6, 'Persia': 3, 'Scandinavia': 2,
   'South Asia': 4, 'Southeast Asia': 4, 'Sub-Saharan Africa': 3}
  Below the floor: {'Persia': 3, 'Scandinavia': 2, 'Sub-Saharan Africa': 3}

by PROVENANCE -- is the region SPEAKING, or being SPOKEN ABOUT?
  Arabia            5 = 4 local + 0 empire-language from the region + 1 about it
  East Asia         6 = 6 local + 0 + 0
  Persia            3 = 3 local + 0 + 0
  Scandinavia       2 = 2 local + 0 + 0
  South Asia        4 = 2 local + 0 + 2 about it
  Southeast Asia    4 = 4 local + 0 + 0
  Sub-Saharan Afr.  3 = 0 local + 2 empire-language FROM THE REGION + 1 about it
  Regions with no source-language record in a language of the region:
    ['Sub-Saharan Africa']

delivery against the allocation: 16 of 36 tranche records curated.
  Gloss-capable declared 5/7 (4 contested_reading, 1 hedged_identification),
  with 2 declaration(s) left in sub-tranches still open.

quotation cases: 9 ask WHICH chunk was quoted (target 6 at 60) and 4 ask only
  WHETHER anything resolved.

curation cost: 16 record(s) timed, 24 excused, 6 RETIRED.

loader warnings: 5   (empty reference_translation, no translation chunk emitted)
  arabia-02-palmyrene-tariff   eastasia-06-cefu-yuangui
  eastasia-07-tang-huiyao      seasia-06-kedukan-bukit
  seasia-07-talang-tuo

All integrity checks passed.
```

**Eleven instruments and all eleven are green**, including the two that were red
when F5 Part 3 opened and were in no state block anybody read:

```
ingest.verify        green, 40 documents      ingest.test_fidelity           77
ingest.test_cost                        64    eval.test_answer_eval         425
eval.test_ranking_check                258    answer.test_answer            150
ui/test_build_ui_data.py                19    scripts/test_recover_baseline  56
scripts/test_harnesses.py               43
python -m ingest.gazetteer --check   GREEN    node ui/check_ui.mjs        GREEN
```

*CORRECTED 2026-09-06, F6, FINDING 76. The table above read
`eval.test_answer_eval         422`. It is **425**, run on the bridge at
`a20214e`, the tree this block describes. The 422 was inherited from
`F5_PART3_RESULT.md`, where it was computed from a measured 416 plus an assumed
per-case assertion rate. **The state block above IS verify's output and is
correct character for character; this table never was verify's output**, and the
rule this document opens with was scoped to one command while eleven were
printed.*

**The host/bridge question is settled — do not re-open it.** All nine suites give
identical counts on both once `psycopg[binary]` and `sqlglot` are installed;
`answer.test_answer` is **150** on both, and the bridge's historic 149 was two
missing packages, not a platform difference. **Mutation harnesses are host only**
(FINDING 59).

---

## F6's seven slots

```
region              tier                        n   note
Sub-Saharan Africa  verbatim_with_provenance    1   requires_provenance:
                                                    LOCAL_LANGUAGE
Sub-Saharan Africa  published_translation_only  1
East Asia           verbatim_with_provenance    1
Scandinavia         verbatim_with_provenance    2   both, re-pointed by ruling 73
Persia              published_translation_only  1
Persia              catalogue_record            1

gloss_capable 1     expect_quoted_from_original_cases 0     vme_quotation_cases 0
```

**Four source-language records, and two of them are the only records in the whole
remaining allocation that move a per-region floor from missed to met.** F7 places
none. **F6 is the last sub-tranche with a session behind it**, which is the
argument ruling 73 used to put the re-pointed slots here.

**No `verbatim_machine_english` slot is placed in F6 or F7.** The tier ends at 4
of 10 and F5's two recorded failures are what fix it there. Nothing you do can
move it, and nothing should try.

---

# The four things to decide before curating anything

## 1. PERSIA'S FLOOR IS UNREACHABLE AND ONLY F6 CAN CHANGE THAT

FINDING 71. Persia sits at 3 against a floor of 4. **Its two F6 slots are
`published_translation_only` and `catalogue_record`, neither of which counts
toward the floor, and F7 places no Persia slot at all.** So Persia ends at 3
unless F6 re-points.

**Confirmed by observation on 2026-09-05**: verify was run with `F5.closed = true`
and Persia appears in `Below the floor` in the same dict, in the same sentence, as
Scandinavia and Sub-Saharan Africa, whose shortfalls **are** recoverable — and
`All integrity checks passed`. `check_allocation` reads the PLAN, and the plan
assumes its slots fill.

**Re-pointing is legitimate** — ruling 73 established it and used it once. **The
supply argument has moved a long way** since F5's hunt refused this vein:

- **Browser pass 2 is still owed and is load-bearing for this decision.**
  `parsigdatabase.com` and `noorlib.ir` have refused every automated request
  since F3, **and every claim in this repository resting on parsigdatabase rests
  on a human pass nobody has made.** Passes 1 and 3 both overturned negatives of
  exactly this shape. **Run it before deciding.**
- **F3 banked the Istanbul epitaph of Khurdad** and F5 removed its blocker:
  Sasanika carries transliteration and transcription at a stable per-record URL.
  One discrepancy is unresolved — Sasanika dates it no later than Bahram V, fifth
  century; F3's note has early 8th to late 10th.
- **`M2 I` and the banked `M 5794 I` are Turfan finds** and are EAST ASIA records
  under this corpus's findspot rule, not Persia. Settling that mis-regioning is
  F6's and **does not help Persia**.

**Recommendation, stated because this project asks for one: re-point Persia's
`published_translation_only` slot to `verbatim_with_provenance`, after running
browser pass 2.** It is the slot whose tier is furthest from its target anyway
(1 of 5), and the cost of being wrong is a `published_translation_only` record
F7 could absorb; the cost of not deciding is a floor that can never be reached.

## 2. SUB-SAHARAN AFRICA IS THE ONLY REGION WITH NO RECORD IN A LANGUAGE OF THE REGION — AND ITS TWO GREEK RECORDS ARE AFRICANS SPEAKING

Its three source-language records are **0 local + 2 empire-language from the
region + 1 about it**. The two are `africa-01-ezana-stone` and
`africa-04-silko-talmis`: **African rulers writing in Greek**, not Romans writing
about Africa. **That distinction is real, it is already the thing ruling 58 and
FINDING 62 built the provenance line to see, and the project owner has accepted
Greek on those terms.**

**But FINDING 68 is still open and this is exactly where it bites: the SPEAKING
subtotal is reported nowhere.** The line prints three components and then a
separate sentence — *"Regions with no source-language record in a language of the
region: ['Sub-Saharan Africa']"* — which reads as a deficit and cannot be
distinguished, in that sentence, from a region that only ever gets spoken about.
**South Asia's 4 = 2 local + 2 about it is the comparison that makes the point**:
Africa has zero local and two speaking; South Asia has two local and two being
spoken about. **Closing FINDING 68 costs one printed subtotal and is F6's cheapest
win.**

`requires_provenance: local_language` on F6's Africa slot stands. **Ge'ez is what
that slot is for**, and it is the region's hardest capture.

## 3. DASI IS UNCLAIMED AND IS BETTER PROVENANCED THAN ANYTHING F5 CURATED

`F5_CANDIDATES.md` recorded `dasi.cnr.it` as *"the single most valuable thing lost
in the hunt"* — an Anubis wall, Access Denied to every route. **Chrome was not
challenged once.** Browser pass 3, `F5_PART3_BROWSER_PASSES.md`:

```
CIH 541 Sadd Ma'rib 5
  stable URL   dasi.cnr.it/project/1/epigraphs/2382     DOI 10.82194/dasi-epi-2382
  LICENCE      CC BY 4.0, stated on the record (images excepted, credited)
  text         136 numbered lines of Late Sabaic, word dividers, restorations,
               line-continuation and editorial markers intact
  TRANSLATIONS TWO -- CSAI's own (ENGLISH, on the record, same CC BY 4.0) and
               Nebes 2005
  apparatus    named-editor variants PRINTED ON THE RECORD:
                 84       Glaser and CIH: (S²)wlmn.
                 87       Muller and CIH: Frnt.
                 129-130  Muller and CIH: 'l[y] hlb.
  date         548 CE, "Date accuracy: Accurate"
  object       Marib Museum, inv. BAR 2, monumental stela, h.250 w.66 th.40
  site         linked site record, Ma'rib, Yemen -- so placements resolve
  ROMAN CONTENT at line 89: mhs²kt ngs²yn (the Negus's delegation), then
    mhs²kt mlk Rmn (the delegation of the king of Rome), then tnblt mlk Frs¹
  behind it    9,102 keyed epigraphs of 14,617 titles, each with URL and DOI
```

**A CC BY 4.0 source text AND a CC BY 4.0 English translation on the same page, a
DOI, a stable per-record URL, a linked site record, and three named-editor variant
readings in a printed apparatus.** That is gloss-capable on the same standard
`arabia-05-ruwafa` was declared on, **and F6 has exactly one gloss declaration to
make.**

**Two things stand in the way and neither is fatal.** It is an **Arabia** record
and F6 places no Arabia slot — so taking it means a re-point, and Arabia is
already at 5 against a floor of 4, so a re-point that spends an Arabia slot buys
no floor. **And this session read CIH 541's text and the opening of its English
translation**, so if F6 curates it the capture is still a curator's blind paste
but F5's session is no longer an independent check on it. **Declared, the same way
browser pass 1 and `southasia-05` are.**

## 4. READ FINDING 73'S FALL TABLE BEFORE YOU CURATE

Five records entering the index made **nine gold pairs worse and none better**,
and because no pair crossed the recall@6 boundary **the headline did not move**:
`ALL recall@6 0.727`, pair-level 32/44 before and after.

**Two cases now sit at rank 6 with zero slack:**

```
tc-jabal-dabub              3 -> 6    3 chunks of arabia-06-syllaeus inside it
probe-tamil-akananuru-en    5 -> 6    eastasia-07-tang-huiyao inside it
```

**F6 places seven more records on top of that.** One more record of the wrong kind
and either leaves the window — and the aggregate will still read flat until it
does, then move by two at once.

**Same-region crowding is at least as strong as the cross-regional kind ruling 70
predicted**: `arabia-06-syllaeus` crowds `tc-jabal-dabub`, Arabia to Arabia.
**Curating a region damages that region's own gold cases.** Scandinavia is F6's
biggest draw at two records and `vimose-runes` has already gone 7 → 16.

**Not gated and deliberately not.** The margins are information; a gate on them
would be a threshold nobody has evidence for.

---

# The rules that carry into F6

**THE CAPTURE PATH.** Source text and published translations are **pasted by the
curator from the cited page, every record.** `WebFetch` drops lacuna markers and
substitutes U+0027 for U+2019, measured twice (FINDINGS 48, 50).
`archive.org/_djvu.txt` is **not the page** (FINDING 53) — measured at 91.7%
agreement against a known-good witness on one line of Devanagari.

**A locating fetch must not reveal what it located — AND NEITHER MUST A PROGRESS
MESSAGE.** F5 Part 2 kept the first half and broke the second.

**A model CAN be the diff. Propose it; never apply it.**

**AN ALTERNATIVE THIS PROJECT SUPPLIED ITSELF IS WORTH NOTHING** (FINDING 55).
This is what a gloss declaration lives or dies on.

**THE GLOSS MECHANICAL REQUIREMENT, which is where F3 lost a declaration:** the
hedge AND the statement that the reading is uncertain must both sit inside a
**retrieval-eligible chunk** — `original_text_excerpt` or `reference_translation`
— and **not** in `notes`, which the loader does not chunk.
`eastasia-05-liangshu-qin-lun` is the pattern.

**RULING 74 — an in-copyright source may be cited and quoted under four
conditions**, declared in the record: the quotation is short and bounded by the
source itself; the work is fully cited; **the rights position is stated verbatim,
and where a source states no terms the record says THAT, in those words**; and the
use is non-commercial research. **Where a condition cannot be met, the source is
not taken.**

**RULING 65 — no `--fuse`.** Four tranches without a reading of the C2 fused arm.

**WRITE BYTES.** `json.dumps(d, ensure_ascii=False, indent=2) + "\n"`, UTF-8, LF
only, no BOM. `.gitattributes` disables EOL conversion because 168 archived
citation spans point into the corpus by exact offset.

**READ `git diff --stat` BEFORE EVERY COMMIT — AND KNOW IT CANNOT SEE A RECORD**
(FINDINGS 52, 61), **OR THE UI BUNDLE** (FINDING 74). Three instruments in this
repository report changes they cannot show.

**Never run a mutation harness where it can be interrupted** (FINDING 59). Host
only. **Check your own edits against FINDING 66** before committing a changed
literal.

**From the bridge use `git --no-optional-locks`**, and note that the bridge cannot
delete files by default, so git cannot remove its own `.git/index.lock` and a
commit dies half-done; `device_request_delete_permission` on the repo root fixes
it for the session. The bridge has **no git identity** — pass `-c user.name
-c user.email` per commit.

**Commit messages go in `commit-*.txt` and are gitignored.** Do not `git add`
them.

**`F5.closed` is `true`. Do not touch `F6.closed` until F6's result document is
written** — and locate it by reading the block, not by line number. F5 Part 3's
first attempt at that edit set F6's flag instead, caught by its own check.

---

# The debt list, in the order F6 will want it

**Do these before or during curation:**

1. **Browser pass 2** — `parsigdatabase.com`, `noorlib.ir`. Load-bearing for the
   Persia decision. Nothing in this repository has ever tested them by a person.
2. **Read FINDING 73's fall table**, above.
3. **Decide Persia's floor.**
4. **Close FINDING 68** — print the SPEAKING subtotal. One line.

**Cheap fixes with their design already written down:**

5. **An `agent` field for the cost ledger** (FINDING 70). Six of seven phases
   changed hands in one session and the ledger cannot see it; 16 records are now
   timed against `min_n_to_read_as_a_trend` of 10.
6. **A rights column** (Ruling 74). The corpus sits in at least four rights states
   and `ingest.verify` does not read `citation_original` — the position is
   recoverable only by reading 40 records by hand.
7. **A diffable manifest beside `ui/data.js`** — run count, record count, corpus
   digest, span audit (FINDING 74).
8. **A generated state block** — `ingest.verify --state`, or a rule that opening
   documents paste verify's output rather than restate it (FINDING 75).

**Investigations owed:**

9. **`git log --follow` on `africa-03-periplus-adulis`.** An archived answer cites
   a passage the corpus no longer contains, and the record's provenance is
   `unrecorded`. Three instruments noticed it was re-cut on one day.
10. **A ranking pair targeting `eastasia-07-tang-huiyao`** — no gold pair names it
    and its retrievability is untested. It would fall under ruling 54.
11. **`southasia-05-brihatsamhita` appears NOWHERE in the ranking run** — not as a
    target, not in any `beaten_by`, not as any ceiling. It is in the index. Check
    whether a record with one chunk is reachable by this gold set at all.
12. **Re-read `arabia-04-jabal-dabub` and `eastasia-07-tang-huiyao` against Ruling
    74.** The Kanripo CC BY-SA 4.0 claim is exactly the kind FINDING 69 makes
    suspect.
13. **The unlocated "two ṭ" sentence** in Petrantoni. `F5_CANDIDATES.md` and
    `F5_PART3_START.md` both quote it as verbatim from p. 126 and a curator did
    not find it there. **Until it is located or declared absent, both documents
    carry a quotation with no established page.**
14. **A reading of Dvivedī's mūla Bṛhatsaṃhitā 2.14.** A real textual variant
    against record 40's Jhā text is reported by the curator and this project holds
    no transcription of it. Two lines. **Needs Devanagari, which is the capability
    that closed F5's South Asia slot.**
15. **A GeoNames search for al-Ruwāfa**, and record 37's placement finished.
16. **Book browser pass 1's ~20 minutes** as `source_hunting` on record 41 if a
    Bhaṭṭotpala record is ever written, or the one record whose source was hunted
    by eye will show a zero.

**Long-standing and untouched by F5:** `scripts/mutate_part8.py` does not mutate
`eval/test_answer_eval.py`; `scripts/test_harnesses.py` is mutated by nothing and
is at 43 assertions; `mutate_distractors.py` has no BASELINE block; six mutation
targets match more than one line; FINDING 58's shared matcher, nine copies of one
three-line rule; ruling 65's renderings debt; FINDING 67 — `total_at_60` is the
size of the plan and the file calls it a target; `recalibration_corpus` is a pair
with both halves null until Block F closes.

---

# The sentences that travel, into F6

**A fetcher misreads access control and metadata, and reads structural absence
correctly — and this project's hunt documents recorded both kinds of negative in
the same words.** Two negatives were overturned by a person in one afternoon; the
one that held was the Mojmal's missing search index, which defeated the person
exactly as it defeated the fetch.

**The `verbatim_machine_english` tier needs a genre nobody translated, a text
somebody keyed, and a curator who can key it** — and the third condition is a
fact about this project that no amount of hunting could have discovered.

**Recording a slot as a failure moved a per-region floor from missed to
unreachable, and the guard reports it as a note, because it reads the plan and
not the delivery.**

**Nine gold pairs fell, none improved, and the number a reader meets did not
move. Two cases are now at rank 6 with zero slack and F6 places seven records.**

**Curating a region damages that region's own gold cases**, which is not what the
ruling that predicted the damage said.

**Three instruments in this repository report a change they cannot show**, and a
fourth reported the right number into a session that preferred its own prose.

**Seven claims in this project's own documents were corrected by a person opening
the page they cite, and four of them were quotations cut at a comma.**

**Sub-Saharan Africa has no record in a language of the region, and its two Greek
records are Africans speaking. The instrument can see the difference and does not
print it.**
