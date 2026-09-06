# F5 PART 3 RESULT — the tranche closes at 5 of 7, both remaining `verbatim_machine_english` slots are recorded as failures, and the session's central finding is that this project's negatives were about its FETCHER and were written down as facts about the world

**Date: 2026-09-05**, taken from the host with `date -u +%F`. **Block F's fifth
distinct date.** F4's close, F5 Part 1 and F5 Part 2 all ran on 2026-09-04.

**`F5.closed` is set to `true` by this document and by nothing before it.** The
seven cells are not filled. Five are. **The shortfall is written down here, and
that is the condition `F5_PART3_START.md` set.**

---

# The headline

```
                            opened           closed
HEAD                        7e6c021          this session's commits on top
corpus                      36 records       40 records, 116 chunks, 27 pairs
F5 delivered                1 of 7           5 OF 7
verbatim_with_provenance    19 of 27         23 of 27
verbatim_machine_english    4 of 10          4 of 10   -- UNCHANGED
gloss-capable declared      3 of 7           5 of 7
records timed               12               16
gold answer cases           45               48
quoted-from-original cases  6 of target 6    9 of target 6   -- ALREADY met at open
ingest.gazetteer --check    RED since F4     GREEN
node ui/check_ui.mjs        RED since D1     GREEN
```

*The 507 that appears in the ranking-run section below is the INDEX depth with
distractors, not the corpus. The corpus is 116 chunks. **Three figures in an
earlier draft of this table were wrong and are corrected here; FINDING 75 records
what they were and how they got in.***

**Both red instruments the block inherited are green.** They were the tenth and
eleventh instruments in this repository and neither appeared in any state block
a session actually reads. That is fixed by having run them, not by having
listed them.

**The corpus lands at 54 and 54 is RECORDED AS MISSED.** `total_at_60` and
`by_tier_at_60` are not lowered, exactly as ruling 69 handled 56. Nobody
re-curates a record; a target that moves to meet the delivery is not a target.

---

# What was delivered

## Four records, captured by the curator from the cited page, every one

```
37  arabia-05-ruwafa           Nabataean-Greek bilingual, al-Ruwafa, 164/166-169 CE
    23,382 bytes               Petrantoni entry 47, five lettered sections,
                               A/C/E Greek and B/D Nabataean. GLOSS DECLARED.

38  arabia-06-syllaeus         Safaitic, Wadi al-Hasad, c. 12-9 BC
    17,959 bytes               "the year S1ly fled from Rome". ROME IS NAMED IN
                               THE TEXT -- the only Arabian record in the corpus
                               of which that is true.

39  persia-05-abnun            Middle Persian, Barm-e Delak, 243/4 CE
    22,144 bytes               The Gordian III war from below, against the king's
                               side of it in persia-01-skz. GLOSS DECLARED.

40  southasia-05-brihatsamhita Sanskrit, Brhatsamhita 2.14, c. 550 CE
    17,105 bytes               The corpus's first Sanskrit record, and its first
                               record of an Indian intellectual JUDGING the
                               Mediterranean rather than trading with it.
```

**Three findings came out of the captures that no re-fetch would have produced**,
which is the whole reason the blind-paste rule exists:

- **Record 37.** The lacuna notation in Petrantoni is **italic English prose set
  inside the edited text**, not a bracket convention. Section E's disputed
  sequence is encoded three ways in one record because the edition prints it
  three ways.
- **Record 38.** The record uses the editors' **`ngy` dispute**, not the
  `y`-restoration hedge `F5_CANDIDATES.md` planned on. The hunt document's
  version is corrected, not overruled. An **`ʿlmlṭ` / `Mṭl` transposition** in
  the printed edition is recorded unrepaired and uncollated: it is not attributed
  to the edition or to the paste, because nobody has collated it.
- **Record 39.** **The published English omits the fulfilment clause.** The
  record declares it. That is a discrepancy between a translation and its own
  original, found by a person reading both registers side by side, in a source
  the hunt had already read.

## Record 40's declared breach, and its retirement

Record 40 was written carrying a **declared transcription breach**: the English
of Sastri & Bhat had been transcribed by the model from a page image, and the
record said so in its own text rather than in a note. **The curator confirmed it
on 2026-09-05 against the printed page, character for character over all 188
characters, and the record now says the breach is retired.**

**ONE ELEMENT IS STILL THE MODEL'S READING and the record still says so**: the
leading label `Sloka 14.—`. A retirement that quietly swallowed the remainder
would be worth less than the breach it replaced.

## Two gloss declarations, `arabia-05-ruwafa` and `persia-05-abnun`

Both `contested_reading`. Both hedges sit inside `reference_translation`, which
**is** chunked — the trap that cost F3 a declaration was the hedge going into
`original_text_note`, which the loader does not chunk. `arabia-06-syllaeus` and
`southasia-05-brihatsamhita` are gloss-capable in substance and are **not**
declared, because F5's quota is two and `check_delivery` refuses more.

**`gloss_capable_records` now stands at 5 of 7**, with F6 and F7 holding one
each and zero slack. That was true before this session and is still true.

## Three `expect_quoted_from_original` gold cases — the quota is MET

```
ruwafa-thamud-in-two-languages   answerable   arabia-05-ruwafa
abnun-fire-altar-name            answerable   persia-05-abnun
brihatsamhita-yavana-sanskrit    answerable   southasia-05-brihatsamhita
```

45 cases → 48. **F5's allocation places three and F5 wrote three.** All three
target `verbatim_with_provenance` records, so all three land on the line
`ingest.verify` calls *"ask WHICH chunk was quoted"*, which goes **6 → 9 against
a target of 6 at 60**.

**The target was ALREADY MET before this session and this document must not claim
otherwise.** The allocation places seven cases against a target of six
deliberately — `gloss_and_quotation_are_CASE_quotas` says so in the file: *"so
that one may fail without the target failing with it."* F6 and F7 place none, so
the quota is closed, and it closed over rather than short. **An earlier draft of
this section said the quota was "met at 7" by these three cases. It was not; it
was met before them, and the figure was wrong as well.** FINDING 75.

**The Greek alternatives in the Ruwāfa case carry the editorial brackets
verbatim** — `Θ](αμ)ουδην(ω)ν`, `Θ(α)μου(δ)ηνων`, `(Θ)[αμ](ου)δ(η)νω` — because
gold matching is case-insensitive and whitespace-collapsing and **is not
punctuation-insensitive**. A case written with the brackets stripped would have
passed nothing and would have looked like a retrieval failure.

## A placement corrected in `eastasia-04-jingjiao-stele`

Chang'an moved out of `subject_places` into a new **`findspot_places`**, with
`geonames:1790630`, ground `stated`. **GeoNames `1791624` was refused**: it is
Chang'an District, `P.PPLA3`, twelve kilometres south of the city the stele was
found in. `subject_places` now holds `大秦 (Da Qin)`, `regional`, **no id**, role
`focus` — because no id exists for it and none is written from memory.

That, plus a gazetteer cache refresh against the pinned 2026-08-10 dump, is what
turned `ingest.gazetteer --check` green.

---

# The two slots that failed, and the failures are the deliverable

## Persia — failed exactly as ruling 72 predicted, for the reason ruling 72 gave

Thirteen candidates, thirteen open English translations. **English exists and was
found.** Ruling 72 is confirmed here as written.

## South Asia — failed OFF RULING 72'S MAP, and that is worth more

Ruling 75 records it in full. In order:

```
browser pass 1   Is Bhattotpala's Vivrti on 2.14 reachable?  YES -- ten printed
                 lines on ONE page of the clean CC0 Dvivedi scan, leaf n101,
                 printed p. 82, with a second open witness in Tripathi. The
                 hunt's "the original cannot be reached" was WRONG.
capture 1        Wrong passage, and machine-read.
capture 2        Right passage, still the text layer. Measured against the same
                 verse already held clean in record 40: 91.7% character
                 agreement, nine divergences, the numeral 1 read as 9.
capture 3        Not attempted. THE CURATOR CANNOT TYPE DEVANAGARI.
```

**Two facts compound and neither alone would have been fatal.** No keyed text of
Bhaṭṭotpala exists anywhere this project can reach — GRETIL has the mūla only,
SARIT did not render, forty archive.org items are all page images, and the item's
own search-inside is dead. **And the curator does not have the script.** A keyed
text would make the script irrelevant; a curator with the script would make the
absence merely expensive.

**Ruling 72's own falsification text enumerates three branches and South Asia is
in none of them.** It is not found English and it is not supply: the material
exists, is reachable, is legible, and is not keyed. **The honest report is that
ruling 72's enumeration was incomplete**, and that correction was made against an
earlier and more flattering sentence in ruling 75 itself.

## The consequence for the plan, which is real and is not softened

**FINDING 71: recording Persia's vme slot as a failure puts Persia's per-region
source-language floor OUT OF REACH.**

```
region                now   still to come in F6/F7   ends at   floor
Persia                  3   NONE                          3       4   CANNOT REACH
Scandinavia             2   F6 vwp 2                      4       4   shortfall
Sub-Saharan Africa      3   F6 vwp 1                      4       4   shortfall
```

`ingest.verify` prints the distinction itself: *"A SHORTFALL is progress … an
UNREACHABLE quota is a failure above."* **Persia's is unreachable and it appears
on the same line, in the same shape, as two that are recoverable.** Nothing
fails, because `check_allocation` reads the floor against the PLAN and the plan
assumes its slots fill.

**And the kind has changed.** When `F5_RULINGS.md` first noted two regions below
the floor, both were there because of delivery misses. **Persia is below it
because a slot was decided to fail** — a judgement made on evidence, in this
session, recorded — and the guard cannot tell a decision from a miss because it
is not looking at delivery at all.

## CONFIRMED BY OBSERVATION, on the first run after the flag was flipped

`python -m ingest.verify` was run against the tree with `F5.closed = true`, before
the close was committed and for the purpose of seeing this. **The output is
identical in shape to what it prints with F5 open:**

```
note: source-language records by region (F1 floor 4 each at 60):
  {'Arabia': 5, 'East Asia': 6, 'Persia': 3, 'Scandinavia': 2,
   'South Asia': 4, 'Southeast Asia': 4, 'Sub-Saharan Africa': 3}.
  Below the floor: {'Persia': 3, 'Scandinavia': 2, 'Sub-Saharan Africa': 3}.
...
All integrity checks passed.
```

**Persia appears in the same dict, in the same sentence, as the two regions whose
shortfalls are still recoverable, and nothing above it fired.** The delivery line
four notes earlier prints the distinction — *"A SHORTFALL is progress and is
reported here; an UNREACHABLE quota is a failure above"* — in a run where one of
the three IS unreachable and the failure section is empty.

**The finding predicted a silence and the silence was then measured.** That is
worth more than the arithmetic alone, because the arithmetic could have been
wrong about which guard reads what.

## The fix is named and is not taken

F6 can restore Persia by re-pointing one
of its two Persia slots to a source-language tier; ruling 73 already established
re-pointing as legitimate. **This document does not re-point it.** An allocation
edited to rescue a number by the session that missed it is the mistake ruling 51
records. F6 gets the decision with the arithmetic in front of it.

## The option that was open and is refused

`F5_PART3_START.md` left open re-pointing a failing vme slot to East Asia and
taking the Taiping Huanyuji. **Refused.** Its opening ~1,693 characters are Hou
Hanshu matter the corpus already holds as `eastasia-02`, and Hirth translates it
in full — so it would fill a `verbatim_machine_english` cell with a text that
fails the tier's own premise twice over. A slot filled by something that does not
test what the tier tests is worse than a slot recorded as failed.

---

# THE SESSION'S CENTRAL RESULT: the negatives were about the fetcher

Two browser passes were run by a person against sources this repository had
written off. **Both opened. Neither was blocked for the reason the hunt
recorded.**

```
recorded by the hunt                          measured by a person
------------------------------------------    ------------------------------
"the original cannot be reached" --            ten legible lines on ONE page
  fulltext/inside.php 403, djvu OCR            of a clean CC0 letterpress scan
  "significantly corrupted throughout"

"Anubis anti-bot wall, Access Denied to        CC BY 4.0, a DOI, a stable URL,
  every route tried. This closes the           two translations, and a
  whole Sabaic vein"                           named-editor apparatus
```

**DASI opened completely.** `dasi.cnr.it` was recorded as the single most
valuable thing lost in F5's hunt. Chrome was not challenged once. Behind it:
**9,102 keyed epigraphs of 14,617 titles**, each with a stable URL and a DOI, and
CIH 541 itself — 136 numbered lines of Late Sabaic, CC BY 4.0, two translations
including an English one on the record, a printed apparatus with Glaser and
Müller against CIH, a linked site record so placements resolve, **and the Roman
content at line 89**: `mḥs²kt mlk Rmn`, the delegation of the king of Rome,
between the Negus's and the Persian king's.

**It is not F5's** — both Arabia slots are filled and the sub-tranche is closed.
**It is the strongest thing now sitting unclaimed in front of F6 and F7**, and
Sub-Saharan Africa's F6 slot that `requires_provenance: local_language` should be
read against it too.

## But the asymmetry is the finding, not the reversals

**A fetcher misreads ACCESS CONTROL and METADATA. It reads STRUCTURAL ABSENCE
correctly.**

```
the fetcher got these WRONG           the fetcher got these RIGHT
---------------------------------     ---------------------------------
DASI's Anubis wall                    the Mojmal's never-built search index --
Bhattotpala's 403                       it defeated a PERSON exactly as it
four separate licence claims            defeated the fetch
                                      Bhattotpala's absence from every keyed
                                        corpus
```

That is why FINDING 72 does **not** simply invert the hunt's negatives. It
rewrites the candidate finding `F5_CANDIDATES.md` proposed — that the tier's
yield tracks a tradition's **digitisation** history — into three conditions:

```
1  A GENRE NOBODY TRANSLATED       FINDING 45's seam. Necessary, not sufficient.
2  A TEXT SOMEBODY KEYED           East Asia has Kanripo. Bhattotpala has nothing.
3  A CURATOR WHO CAN KEY IT        A fact about THIS PROJECT, invisible until a
                                   slot reaches capture, and undiscoverable by
                                   any amount of hunting.
```

**Condition 3 is the one no hunt could have found.** F5's hunt ran a full
battery, refused the right candidates, and refused them for the wrong reason.

---

# FINDING 69, and it is the shape of most of the rest

**"Open" names two different properties and this project's hunt documents use one
word for both.** `F5_CANDIDATES.md` records of the Syllaeus article: *"Cite the
Acta Orientalia version; it is the one verified open."* A curator opened it and
found **© Akadémiai Kiadó, all rights reserved**, sold at akjournals.com. The
`real.mtak.hu` copy is a green-repository deposit: free to read, no Creative
Commons licence at all.

**Nothing in the hunt was wrong.** It recorded **reachability** in a word that
everywhere else in the same document means **openly licensed**.

**The same defect, four hours earlier, from the other direction.** The Ruwāfa
licence was verified against the BOOK's front matter; the chapter has none, and
the issue date that travelled with the claim could not be confirmed at all.

**This is the fifth instance of one shape in this repository** — after
`has_extent`/`has_area`, `translation_chunk`/`translation_chunk_id`,
`--find`/`--survey`, and the field once called `pleiades_id`. It recurred **three
more times inside this one session**:

- **`reachable` against `keyed`** (FINDING 72). Two of the hunt's failures were
  written as reachability failures and were keying failures.
- **"is this transcription faithful" against "do these two editions agree"**
  (ruling 75). An acceptance test was agreed in advance, run, and **was void**:
  it compared the curator's reading of **Dvivedī** against record 40's
  **Achyutānanda Jhā** text. When the curator reported no match, the cause was a
  **real textual variant between two printed editions** on the verse South Asia's
  records stand on. **The test nearly recorded a slot failure on evidence of a
  finding, and it was written three hours after the session named FINDING 69.**
- **`git diff --stat`'s "nothing changed" against "I cannot see this file"**
  (FINDING 74, below).

**The Dvivedī variant is real and is NOT recorded**, because nobody has read it.
Record 40 carries Jhā's text, correctly cited; "another edition differs" without
being able to say how is a claim no reviewer could check. **A reading of
Dvivedī's mūla 2.14 is owed** — two lines, not ten — and it needs the same script
the slot failed on.

---

# Ruling 74 — in-copyright sources, admitted under four conditions

**Three of the four captures had no clean licence**: Syllaeus in copyright, and
Sasanika and wisdomlib stating no terms of any kind. Each was already written as
a note inside its own candidate entry. **The rule was never written**, and
`arabia-06` was about to become the first record in this corpus to reproduce a
translation from an all-rights-reserved publication — a threshold crossed with no
ruling, which is what FINDING 47 is about, three times in one session.

The rule: a record may carry source text and a published translation from an
in-copyright work when **(1)** the quotation is short and bounded by the source
itself — one inscription, one lemma, one verse and its gloss; **(2)** the work is
fully cited, publication and not only URL; **(3)** the rights position is stated
verbatim in the record, naming holder and terms, and naming repository separately
from publisher — **and where a source states no terms at all, the record says
that, in those words**; **(4)** the use is non-commercial research.

**Condition 3 is the one that does work.** A source with no reachable statement
of terms is admitted only by recording that it has none, which is a fact a
reviewer can act on and an adjective is not.

**What it costs, and the cost is stated rather than buried.** The corpus's rights
position is now heterogeneous across at least four states and **nothing counts
them**: `ingest.verify` does not read `citation_original`. **A rights column is
owed and is not built today.** And **two records already in the corpus were
admitted before the rule existed and are not re-read against it** —
`arabia-04-jabal-dabub` and `eastasia-07-tang-huiyao`, whose Kanripo CC BY-SA 4.0
claim is exactly the kind FINDING 69 makes suspect. Re-reading them in the
session that wrote the rule would be the rule fitted to what already passed.

**The safer alternative was refused, and the refusal is recorded with its
argument.** Taking the transliteration and not the translation is plainly safer
on the rights axis. It was refused because `verbatim_with_provenance` requires a
cited published translation by definition, so the safer line **does not produce a
weaker record — it produces a failed slot**, and F5 would record as a supply
failure what is a rights question about one journal.

---

# FINDING 70 — the cost ledger now measures two different agents in one number

Records 37–40 were curated by a session with **no shell on the host**. The work
divided like this and the ledger cannot see the division:

```
source_hunting            F5 Part 2, YESTERDAY   0, an ACCOUNTING GAP
rights_and_licence        the model              model wall-clock
text_capture              THE CURATOR            self-reported, "6 min, avg 5-7"
translation_and_fidelity  the model              model wall-clock
placement                 the model              model wall-clock
authoring                 the model              model wall-clock
rework                    nobody                 0
```

**One phase of seven is a human's minutes. Five are a model's. One is a gap.**
Record 36 already carried this warning on **one** phase. This is six.

`verbatim_with_provenance` now holds 23 declared records against
`min_n_to_read_as_a_trend` of 10 — **comfortably readable as a trend by somebody
who does not know four of its timed entries measure a different agent.**

The apportionment is judgement and is not disguised: the model's wall clock is
bounded by file timestamps 08:06Z–09:55Z, split across four records and five
phases by judgement, **every figure marked `estimated` with its reason
attached**, and no `measured` provenance claimed anywhere except `rework`, which
is genuinely zero. **`rights_and_licence` carries its first non-zero figure in
the ledger's history** — 12 minutes, all of it on `arabia-06-syllaeus`, booked on
the one record rather than spread across four because spreading it would hide
that one record's rights check produced FINDING 69 and Ruling 74.

**Nothing is corrected and no number is withdrawn.** Excusing the four into
`not_timed` would leave them unattributed to F5 and would fail this tranche's two
gloss declarations, which are the scarce thing in the whole plan. **What is owed
is an `agent` field**, and choosing its vocabulary in the session that first
needed it is the allocation-decided-at-F7 mistake. F6's, with the evidence
already in the file.

**Not booked anywhere:** browser pass 1's ~20 minutes are `source_hunting` for
**record 41** and must go into that record's entry, or the one record in this
tranche whose source genuinely had to be hunted by eye will show a zero. Passes 3
and 4 are F6 and F7 hunting done in F5's session.

---

# The ranking run, and FINDING 73

Run `20260905T183224+0000-retrievable_chunks_with_distractors.json`. 507 chunks,
depth 507, `voyage/voyage-3.5`, 44 pairs over 41 units, **BASELINE arm, no
`--fuse`** (ruling 65). Unit recall@6 **0.805** (33/41), MRR@10 **0.621**.

**The comparator predates record 36**, so this diff measures **five** records
entering the index, not four. Every attribution below is from `beaten_by` chunk
ids, which name records directly, and not from the diff.

## Ruling 70 — CONFIRMED, by a wider margin than it asked for

Predicted: at least one F5 Arabia record appears in `vimose-runes`'s `beaten_by`.
**Four of the six are F5 records.** Ruwāfa took the top three places outright and
**displaced `arabia-04-jabal-dabub` as `best_other_doc_chunk_id`** — the ceiling
`floor.json`'s `superseded_diagnosis` recorded.

**The cost the ruling registered in advance is now measured at nine ranks.**
`vimose-runes` went 7 → 16. **Three of the four crowding chunks are English**, so
the class doing the damage is not "Arabian inscription in its own script"; it is
the record, through whichever chunk ranks.

## Ruling 71 — NOT CONFIRMED, and its declared blind spot is what lets us say so

`eastasia-07-tang-huiyao` appears in **neither** `china-describes-rome` interval.

- **houhanshu held at 8.** Record absent AND the rank did not move. The
  blind-spot clause covers ranks that FALL. **A clean negative.**
- **weilue fell 9 → 10.** Record absent, rank fell by one. **Exactly the declared
  blind spot, unreadable in either direction**, as pre-registered.

**And the record is not retrieval-invisible**, which is what makes the negative
interesting rather than empty: it crowds `probe-tamil-akananuru-en` (rank 6) and
`adulis-throne-leuke-kome` (rank 31). **The mechanism operated; the prediction
pointed it at the wrong targets.**

**No gold ranking pair names record 36 as a target.** Its own retrievability is
untested by this instrument, and a pair written now would fall under ruling 54.

## FINDING 73 — nine pairs fell, none improved, and the headline did not move

```
                       improved   unchanged   FELL
pairs (44)                    0          35      9
pair-level recall@6      old 32/44   new 32/44   crossings: NONE
```

**Five records entered and made nine gold pairs worse and none better**, and
because no pair crossed the window, `ALL recall@6 0.727` **is unchanged**. A
reader checking whether F5 hurt retrieval would read the aggregate, find it flat,
and be wrong.

**Two cases are now ON the edge, with zero slack to rank 6**:
`tc-jabal-dabub` 3 → 6 and `probe-tamil-akananuru-en` 5 → 6. Their crowders are
this block's own records, and **F6 places seven more**.

**This generalises ruling 70 past what it claimed.** Ruling 70 framed the damage
as cross-regional. Same-region crowding is at least as strong:
`arabia-06-syllaeus` crowds `tc-jabal-dabub`, Arabia → Arabia, the sharpest
instance in the table; `persia-05-abnun` crowds
`bronze-heracles-verethragna`, Persia → Persia. **Curating a region damages that
region's own gold cases.**

**And `southasia-05-brihatsamhita` appears nowhere in this run** — not as a
target, not in any `beaten_by`, not as any ceiling. It is in the index; its
Sanskrit chunk was embedded. Whether that is a property of the record, of
Sanskrit against this embedding model, or of a gold set that asks it nothing,
**this run cannot say, because no pair targets it.**

**Not gated, and deliberately not.** The margins are real information and a gate
on them would be a threshold nobody has evidence for. **What is owed is that F6
reads this table before it curates.**

---

# FINDING 74 — the bundle is tracked so it can be diffed, and it is one line

`ui/data.js` went 673 KB / ~60 archived runs → **9,312 KB / 685**, the first
rebuild since D1 step 2 at `f54c585`. `--verify` first, per the discipline of
looking before writing: **1,289 claimed character spans checked**, 1,227
resolved, 50 case-folded, 9 case-only, 1 whitespace-only, **1 moved and 1
absent**, both on `africa-03-periplus-adulis` and both from the same 2026-08-10
recovered run whose provenance is `unrecorded`. **An archived answer cites a
passage the corpus no longer contains** — the third instrument today to notice
that record was re-cut. `git log --follow` on it is owed to F6.

`node ui/check_ui.mjs`: all checks passed. 685 runs, 5,399 provenance panels, 40
record panels, 121 placements, 18 edges, 1289/1289 quotations highlighted, and
**the bundle's own headline audit reproduces `--verify`'s span counts exactly**.

`git diff --stat` reports the nine-megabyte rewrite as:

```
 ui/data.js | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

`.gitignore` exempts this file with a stated reason — *"having the bundle in
history lets you diff what it looked like at each gate"* — **and its format makes
that comparison unavailable to every ordinary git instrument.** Not a storage
problem: git deltas and packs it fine. What is lost is readability.

**Third instrument in this repository to report a change it cannot show**, after
the corpus records that commit as `Bin 0 -> N bytes` (FINDINGS 52, 61) and
`git diff --stat` itself, which this project made a rule to read before every
commit. **Not fixed.** Pretty-printing costs millions of lines and changes what
`check_ui.mjs` parses; **a diffable manifest beside the bundle** — run count,
record count, corpus digest, span audit — is the cheap option and is written
down.

---

# The instruments, at close

```
ingest.verify                    green, 40 documents
ingest.test_fidelity             77
ingest.test_cost                 64
eval.test_answer_eval            425    (416 at open; +9 for three gold cases)
eval.test_ranking_check          258
answer.test_answer               150
ui/test_build_ui_data.py         19
scripts/test_recover_baseline.py 56
scripts/test_harnesses.py        43
python -m ingest.gazetteer --check   GREEN   -- every placement resolves to a
                                             cached, dated gazetteer entry
node ui/check_ui.mjs                 GREEN   -- all checks passed
```

*CORRECTED 2026-09-06, F6, FINDING 76. This table read `422    (416 at open;
+6 for three gold cases)`. The 416 was measured; the 422 was not. `0f5bfe0`
changes `eval/gold/answer_cases.json` from 45 to 48 cases and does not touch
`eval/test_answer_eval.py` at all, and the three cases carry THREE assertions
each, not two. Run on the bridge 2026-09-06: 416 at `0f5bfe0^`, **425** at
`a20214e`. The per-case assertion rate behind the +6 was assumed and never
counted -- which is FINDING 75 arrived at by arithmetic instead of by copying,
in the document that discovered FINDING 75.*

**The nine were run on the HOST at `7e6c021` before anything was curated**, which
was Part 3's first job and had never been done. **`answer.test_answer` is 150 on
both the host and the bridge**, once `psycopg[binary]` and `sqlglot` are
installed — so the bridge's historic 149 was two missing packages and not a
platform difference. **The host/bridge question is settled and should not be
re-opened.**

`ingest/verify.py`'s document count was raised **36 → 40** with a comment block
declaring the raise unverified and recording FINDING 66's hand-check: no harness
names that literal.

---

# What a person opening a page corrected, and it is a count

**Seven claims in this project's own documents were corrected by a curator
opening the cited page.** Two of them were in `F5_PART3_START.md` itself. **Four
were quotations truncated at a comma, where the half after the cut mattered.**

That is the same instrument that reversed DASI and Bhaṭṭotpala, applied to this
repository instead of to the web. **The blind-paste rule was written to protect
the corpus from the fetcher. It turns out to protect the documents too.**

---

# What Part 3 did NOT rule on, and what it owes forward

**Owed to F6, in the order F6 will want them:**

1. **Read FINDING 73's fall table before curating.** Two gold cases sit at rank 6
   with zero slack and F6 places seven records.
2. **Decide Persia's floor** — re-point one of F6's two Persia slots to a
   source-language tier, or accept an unreachable quota. FINDING 71 has the
   arithmetic.
3. **Browser pass 2 — `parsigdatabase.com` and `noorlib.ir`.** Still owed, still
   never tested by a person, and **every claim in this repository resting on
   parsigdatabase rests on a human pass nobody has made.** Passes 1 and 3 both
   overturned negatives of exactly this shape; the prior has moved a long way.
   This is load-bearing for FINDING 71's fix.
4. **DASI/CIH 541** is unclaimed and is better provenanced than anything F5
   curated.
5. **Re-read `arabia-04-jabal-dabub` and `eastasia-07-tang-huiyao` against Ruling
   74.**
6. **An `agent` field for the cost ledger** (FINDING 70).
7. **A rights column** (Ruling 74) — the position is currently recoverable only
   by reading 40 records by hand.
8. **A diffable manifest beside `ui/data.js`** (FINDING 74).
9. **`git log --follow` on `africa-03-periplus-adulis`** — turns a vanished
   quotation into a named commit.
10. **A reading of Dvivedī's mūla 2.14**, and a ranking pair targeting record 36.
11. **The unlocated "two ṭ" sentence** in Petrantoni. Two project documents quote
    it as verbatim from p. 126 and a curator did not find it there. **Until it is
    located or declared absent, both documents carry a quotation with no
    established page.**
12. **A GeoNames search for al-Ruwāfa**, and record 37's placement finished.

**Still open from before F5 and untouched by it:** `scripts/mutate_part8.py` does
not mutate `eval/test_answer_eval.py`; `scripts/test_harnesses.py` is mutated by
nothing and is now at 43 assertions; `mutate_distractors.py` has no BASELINE
block; six mutation targets match more than one line; FINDING 58's shared
matcher; ruling 65's renderings debt, now five tranches without a reading;
FINDING 67; FINDING 68; `recalibration_corpus` is a pair with both halves null
until Block F closes.

---

# `F5.closed = true`

Set in `data/corpus_tiers.json` **as the last change of this session and
deliberately last**, because the flag is what `check_delivery`'s reachability
arithmetic reads: closing F5 is the moment a shortfall becomes an unreachable
quota, and a checker that would act on it should act on it against a tree where
everything else is already committed and green.

**And one near-miss is recorded rather than tidied away.** The flag was located
by line number, and **the first edit set F6's `closed` to `true` instead of
F5's** — five sub-tranches, five identical `"closed": false` lines, and the block
name forty lines above each. It was caught immediately by the same edit's own
backward search for the enclosing `"name"`, which printed `F6`, and it was
reverted before the file left this container. **Nothing was committed wrong.**
It is written down because a check that fires is evidence the check is worth
running, and because setting F6 closed would have deleted three of the four
remaining gloss declarations from `check_delivery`'s reachability arithmetic in a
file where every other guard reads the plan and not the delivery.

**F5 closes at 5 of 7.** Its two gloss declarations are made, its three
`expect_quoted_from_original` cases are written and the corpus-wide quota of
seven is met, its one `vme_quotation_case` was delivered in Part 2, and its two
remaining `verbatim_machine_english` slots are recorded as searched failures with
their evidence.

---

# The sentences that travel, into F6

**Both `verbatim_machine_english` slots failed, one exactly as predicted and one
off the map entirely, and the second is worth more than the record would have
been.**

**The tier needs a genre nobody translated, a text somebody keyed, and a curator
who can key it — and the third condition is a fact about this project that no
amount of hunting could have discovered.**

**A fetcher misreads access control and metadata, and reads structural absence
correctly. This project's hunt documents recorded both kinds of negative in the
same words.**

**"Open" was two questions under one name, and so were `reachable`/`keyed`,
"is this transcription faithful"/"do these two editions agree", and
`git diff --stat`'s silence. Four instances in one session, of a shape this
repository has now hit nine times.**

**Recording a slot as a failure moved a per-region floor from missed to
unreachable, and the guard reports it as a note, because it reads the plan and
not the delivery.**

**Nine gold pairs fell, none improved, and the number a reader meets did not
move.**

**Curating a region damages that region's own gold cases, which is not what the
ruling that predicted the damage said.**

**The bundle is in version control so that it can be diffed, and it is one line
long — the third instrument here that reports a change it cannot show.**

**Seven claims in this project's own documents were corrected by a person opening
the page they cite, and four of them were quotations cut at a comma.**
