# F5 PART 3 START — one record delivered of seven, four candidates settled and waiting on a paste, and two slots that failed after finding exactly what they were looking for

**Read this before `F5_CANDIDATES.md`.** That document is the hunt. This is the
operating document for the session that finishes the tranche.

---

## THIS IS STILL F5, AND IT IS STILL OPEN

`F5.closed` is `false` and **1 of 7 delivered**. The trap `F5_PART2_START.md`
named has not gone away, it has only moved: two documents now say F5 curated
something, and a session that reads them and opens F6 strands six allocated
slots and all three registered predictions.

```
sub-tranche  closed  slots  delivered   gloss  eqfo  vme_q
  F3         True       8    6 of 8       2      2     2
  F4         True       7    5 of 7       2      2     1
  F5         False      7    1 of 7       2      3     1   <-- HERE
  F6         False      7    0 of 7       1      0     0
  F7         False      7    0 of 7       1      0     0
```

**Set `F5.closed` to `true` only when its seven cells are filled or its shortfall
is written down.** That flag is what `check_delivery`'s reachability arithmetic
reads to decide which gloss declarations are still available, and F5 has two of
the four remaining declarations in the whole plan.

**On dates.** F4's close, F5 Part 1 and F5 Part 2 all ran on **2026-09-04** —
three sessions on one UTC date, and Block F still stands at four distinct dates.
If Part 3 runs on a new date it is the fifth. Three rules in this repository
count dates and `recalibration_corpus` is booked against them, so take the date
from the host with `date -u +%F` before writing anything down.

---

## The state

```
HEAD                7e6c021          corpus 36 records, 83 chunks, 23 parallel pairs

nine suites, on the BRIDGE, at one tree and one interpreter
ingest.verify        green            ingest.test_fidelity          77
ingest.test_cost        64            eval.test_answer_eval        416
eval.test_ranking_check 258           answer.test_answer           150
ui/test_build_ui_data    19           scripts/test_recover_baseline 56
scripts/test_harnesses   43

verbatim_machine_english 4/10    gloss-capable declared 3/7    12 records timed
```

**THE INTERPRETER IS NOT THE ONE EARLIER NUMBERS WERE TAKEN AT, and that is
stated rather than left implied because FINDING 57 is about exactly this
sentence.** The bridge ran all nine for the first time only because
`psycopg[binary]` 3.3.5 and `sqlglot` 30.18.0 were installed into it mid-session.
`answer.test_answer` therefore reads **150 and not the 149 the bridge has always
printed**. Two consequences:

- **F5 Part 1's framing is revised.** It filed the bridge's shortfall under *"the
  bridge is a different PLATFORM, not a host missing sqlglot."* That is right
  about path separators and default encoding and it was wrong about these two
  suites: `pip install "psycopg[binary]" sqlglot` took about forty seconds. What
  changed is that the bridge can now **fail** those two suites where before it
  could only decline to run them, and a suite that cannot run is not a suite that
  passes.
- **A bridge run is still not a host run.** The Windows path-key defect F5 caught
  was green on the bridge and red on the host. **The nine have not been run on the
  host at this tree and that is Part 3's first job.**

---

## What Part 2 delivered

**Record 36, `eastasia-07-tang-huiyao`** — Tang Huiyao 99, 拂菻國, 429 verbatim
characters in 22 columns, Kanripo `KR2m0002_099`, pages 099-24a to 099-25a of the
Wenyuange Siku Quanshu recension. `verbatim_machine_english`, on FINDING 45's
seam, and **the last record on that tier this project can curate** — F6 and F7
place none.

Also in that commit, each because it belongs in the record's own commit and
nowhere else: `ingest/verify.py`'s document count 35 → 36; the tier declaration;
and `tang-huiyao-fulin-clock`, F5's one `vme_quotation_case` and the last case of
its kind this project can write.

**Three things came out of the capture that no amount of re-fetching would have
produced, and they are why the rule exists:**

1. **The locating fetch put the lemma's start on page 24b. The heading is on 24a.**
2. **The fetch reported the lemma at "about 1,200" and "about 1,388 characters".
   It is 429.** 429 characters is 1,287 bytes in UTF-8 and the marked span is
   about 1,388 BYTES — **the figure was measured in bytes and reported in
   characters**, threefold, in the direction that makes a passage look more
   substantial than it is.
3. **The two Song compendia disagree about the 643 embassy.** `eastasia-06` has
   red glass, GREEN glass, malachite, gold-essence; `eastasia-07` has red glass,
   malachite, gold-essence and writes the glass graph 璃 where the other writes
   黎. Recorded in both records and corrected in neither.

That third fact decided the gold case. The obvious question — what the embassy
presented — would pass or fail according to which of two witnesses retrieval
reached, so it would measure retrieval while wearing the name of a case measuring
the machine-translation path. **The case asks about the striking clock instead**,
which is in this record and no other.

**The capture was also repeated and the repetition agrees.** The curator pasted
the six columns on 24a twice, in two messages, byte-identical at 126 characters.
First capture in this corpus checked against anything but itself — possible
because the text has two open witnesses.

**Two corrections to `F4_CANDIDATES.md`:** Kanripo carries the Tang Huiyao at
**KR2m0002**, because 會要 works sit in KR2m (政書類) and not the KR2k geography
class, and F4 recorded no Kanripo id for it at all; and there is **no file-number
offset** on any of the three East Asia candidates, against the runbook's warning.

---

## The four records still to curate — SETTLED, VERIFIED, AND NOT TO BE RE-HUNTED

**Every one of these was read at source by Part 2, not taken from the hunt
agents' reports.** `F5_CANDIDATES.md` carries the full hunt, both search
batteries, every disqualification, and a block naming what was verified by whom.
**Do not re-open the search. Capture these.**

### `arabia-05-ruwafa` — the Nabataean–Greek bilingual, 164/166–169 CE

A temple dedication by the Thamud honouring **Marcus Aurelius Antoninus and
Lucius Aurelius Verus** for the Parthian victories, naming **Claudius Modestus**
and **Quintus Antistius Adventus**. Al-Ruwāfah, 75 km south-west of Tabūk.

- **Capture from the PER-CHAPTER PDF.** The book PDF and the HTML chapter page
  both refuse automated fetching; this one loads cleanly:
  `https://edizionicafoscari.unive.it/media/pdf/books/978-88-6969-508-7/978-88-6969-508-7-ch-04.pdf`
- Giuseppe Petrantoni, "Saudi Arabia", in *Corpus of Nabataean Aramaic–Greek
  Inscriptions*, Antichistica 28 / Studi orientali 11 (Venezia: Edizioni Ca'
  Foscari, 2021), **entry 47, pp. 121–128**. DOI 10.30687/978-88-6969-507-0/004;
  book DOI 10.30687/978-88-6969-507-0; ISBN 978-88-6969-508-7; eISBN
  978-88-6969-507-0. **Licence verified: "This is an open-access work distributed
  under the terms of the Creative Commons Attribution License (CC BY)", © 2021
  Giuseppe Petrantoni, issued 2021-04-26.**
- **Sections A, C, E are Greek; B and D are Nabataean**, each with an English
  translation following.
- **GLOSS-CAPABLE, `contested_reading`.** The dispute is between named editors and
  printed in the reachable edition: *"Macdonald does not agree with this reading
  and, conversely, he points out that there are two ṭ"* (p. 126); *"Macdonald
  suggests that this translation is philologically impossible because here ramaṣa
  is not followed by bayna"* (p. 126); *"the initial sequence, which Milik
  originally read ϹIϹΘAΙΟΙ (on the copy of Philby), turns out to be problematic in
  its interpretation"* (p. 128).

### `arabia-06-syllaeus` — the Safaitic inscription dated by "the year Syllaeus fled from Rome", c. 12–9 BC

A man records his genealogy, three named dead and a drought, and dates it by the
year S¹ly fled from Rome — identified as **Syllaeus, the Nabataean minister who
guided Aelius Gallus's expedition into Arabia and was tried and executed at
Rome**. Wādī al-Ḥašad, about 45 km north-east of as-Safawi, Jordan.

- Transliteration, English translation and commentary in one open repository PDF:
  `https://real.mtak.hu/53785/1/062.2017.70.1.2.pdf`
- Nada Al-Rawabdeh & Sabri Abbadi, *Acta Orientalia Academiae Scientiarum
  Hungaricae* 70/1 (2017), 21–30, DOI 10.1556/062.2017.70.1.2.
- **Rome is NAMED IN THE TEXT.** No other Arabian record in this corpus is; the
  seed manifest flagged `arabia-04-jabal-dabub` as "not directly Rome-linked".
- **GLOSS-CAPABLE, `contested_reading`**, and the hedge is the editors' own and is
  about the reading: *"the letter y has been added because it does not exist in
  the inscription, but it is clear that the name s¹ly is intended because of the
  parallel with AbNSJ 1."*
- **Two warnings.** It has **no corpus siglum** — the article calls it
  "Inscription 1" — which is a durability risk `arabia-04` does not carry. And
  there is a citation trap: the same authors have a near-identical paper in
  *Mediterranean Archaeology and Archaeometry* 16/2 (2016), 33–40. **Cite the
  Acta Orientalia version; it is the one verified open.**

### `persia-05-abnun` — the Abnūn inscription (ŠAb), 243/4 CE, Middle Persian

Ābnūn, a courtier of Šābuhr I, vows a fire if Šābuhr defeats the Romans who came
against Pārs and Pahlaw, then records that he did and that Romans fell into
captivity. **The Gordian III war seen from below** — the corpus already holds the
king's side of it in `persia-01-skz`. Barm-e Delak, Fārs; the fire-altar now at
the Narenjestān, Shiraz.

- Transliteration, transcription and English in parallel:
  `https://sites.uci.edu/sasanika/abnun-inscription/`
- **GLOSS-CAPABLE, `contested_reading`, and the cleanest in the hunt.** The page
  states in its own words that five published translations exist — Tavoosi & Frye
  (*BAI* 3, 1989), Gignoux (*Studia Iranica* 20, 1991), Livshits & Nikitin (*BAI*
  n.s. 5, 1991), MacKenzie (*BAI* 7, 1993), Skjærvø (*Studia Iranica* 21, 1992) —
  and that **"all five translations are at times significantly different from
  another"**.
- **Two boundaries to state in the record.** The English is Sasanika's rendering
  *after* MacKenzie rather than a verbatim reprint, so the published-translation
  test is met by citation-of-record. And **BAI 7 could not be reached**:
  `bulletinasiainstitute.org/vol7.htm` sits in an https→http redirect loop and
  JSTOR `stable/i24045519` is paywalled. **Sasanika states no licence, no terms of
  use and no citation guidance anywhere on its site** — checked, and it belongs in
  the record.

### `southasia-05-brihatsamhita` — Bṛhatsaṃhitā **2.14**, c. 550 CE, Sanskrit

Varāhamihira on the standing of the **Yavanas**. The corpus's first Sanskrit
record and its first record of an Indian intellectual **judging** the
Mediterranean rather than trading with it. South Asia holds only ONE
source-language record in a language of the region; this is the second.

- **Original**, Devanagari with IAST:
  `https://www.wisdomlib.org/hinduism/book/brihat-samhita-sanskrit/d/doc1218183.html`
  (Achyutānanda Jhā's Sanskrit, 2001). **wisdomlib carries no copyright or licence
  statement of any kind — checked.** Public-domain second witness for the verbatim
  field: **Kern, *The Bṛhat Sañhitā of Varāha-Mihira*, Baptist Mission Press,
  Calcutta 1865**, `archive.org/details/bhatsahitavarha00kerngoog`,
  NOT_IN_COPYRIGHT.
- **THE VERSE IS 2.14 AND ONE OPEN TRANSLATION CALLS IT 15.** `doc1218184` is
  2.15 and contains neither `yavana` nor `mleccha` — the hunt's first report had
  that URL and checking caught it. **Cite as Bṛhatsaṃhitā 2.14 (= Iyer ch. 2
  v. 15) with the offset stated**, or a reviewer comparing the two open sources
  will read the record as misattributed.
- **GLOSS-CAPABLE, `contested_reading`. Both sides open, published, and read at
  source by Part 2:**

```
N. Chidambaram Iyer, 1884, ch. 2 v. 15
  wisdomlib.org/hinduism/book/brihat-samhita/d/doc226718.html
  PD scan, CC0: archive.org/details/
    brihatsamhitaenglishtranslationchidambaramiyerpart121884_478_p
  "Even the Mlecchas and the Yavanas (Greeks) who have well-studied the
   science are respected as Rsis."                TWO GROUPS, coordinated

Subrahmanya Sastri & M. Ramakrishna Bhat, 1946, Adhyaya II sloka 14, p. 19
  V. B. Soobbiah & Sons, Bangalore City
  archive.org/details/VarahamihirasBrihatSamhitaByVSubrahmanyaSastri
  "The Yavanas are of low origin. When this science has come to stay with
   them and when such astrologers are worshipped as sages, how much more
   should an astrologer of the Brahmin origin be?"
                            ONE GROUP; low birth PREDICATED of the Yavanas
```

  On Iyer's reading Varāhamihira lists barbarians alongside Greeks; on Sastri &
  Bhat's he concedes the Greeks **are** the barbarians and honours them anyway.
  The verse-number divergence travels with the construal divergence as one
  editorial split. **Cite archive.org and not the blog**: both books also
  circulate as unauthorised uploads on `astrofoxx.wordpress.com`.
- **AND ONE HONESTY NOTE THAT GOES INTO THE RECORD.** Part 2 broke the capture
  rule on this one — not with a fetch, which stayed silent, but in a progress
  message to the curator, which quoted both English renderings. **The paste of the
  two translations is a confirmation, not an independent second reading, and the
  record must say so.** The Devanagari was never shown and its paste is still
  blind.

---

## The two `verbatim_machine_english` slots that FAILED, and why the failure is the deliverable

**Ruling 72 predicted Persia's and South Asia's vme slots would fail because
English EXISTS AND WAS FOUND. On the layer ruling 67 named, that is exactly what
happened — and harder than the prediction asked for.**

```
FAILURE MODE 1 -- English exists and was found. Not "at least one". Every one.

Persia, 13 candidates    Kartir KKZ/KNRb/KNRm/KSM; Paikuli; Abnun; M2 I;
                         Hudud al-Alam; the Istanbul epitaph; Shahnama;
                         Zand i Wahman Yasn; Denkard; Sahrestaniha;
                         Safarnama; Siyasatnama/Qabusnama
South Asia, 8 candidates Yavanajataka (Pingree HOS 48, BOTH volumes open);
                         Samantapasadika (Jayawickrama 1962, open); ALL Sangam
                         Tamil (Chelliah CC0; Vaidehi Herbert free online);
                         the whole EI epigraphic layer, which prints text and
                         translation together by construction;
                         Milindapanha; Mahavamsa; Dipavamsa;
                         Brahmasphutasiddhanta; Pancasiddhantika
```

**Then both hunts kept going, found the untranslated genre in both traditions,
and failed a SECOND time on an axis nothing in this repository had named.**

```
FAILURE MODE 2 -- the untranslated genre exists and the ORIGINAL cannot be reached

Bhattotpala's Vivrti on Brhatsamhita 2.14, Kashmir 966 CE
   Utpala glossing the very verse southasia-05 carries. NO English translation
   exists, and the negative is checkable because two near misses do: his
   Prasnajnana IS translated, and Sengupta translated the Khandakhadyaka WITH
   his commentary -- different works both. Two open Devanagari editions,
   NEITHER body text reachable: fulltext/inside.php returns HTTP 403 to the
   fetch proxy on BOTH items' hosts, and the djvu text comes back with adhyaya 2
   unreachable, यवन absent, and the Devanagari OCR "significantly corrupted
   throughout".
Angavijja, Prakrit, c. 4th c, ed. Punyavijaya, Prakrit Text Society 1957
   Names dinara, sateraka and a jonika -- the Roman-period economy inside a text
   with no interest in Rome. Open on archive.org, no English anywhere. REFUSED:
   the Roman content is confirmed only from a secondary essay and NOBODY HAS
   LOCATED THE PAGE.
Mojmal al-Tawarikh ch. 14, "the kings of Rum", 1126 CE
   Iranica names NO translation into any European language. REFUSED on the
   source side: edition UNIDENTIFIED; page_numbers.json holds 588 leaves and
   EVERY pageNumber is an empty string; the search index was never built
   ("No hOCR or Abbyy file present"); Persian OCR corrupt.
Farsnama of Ibn al-Balkhi, before 1116 CE
   STRONGER negative -- Iranica states Le Strange translated the GEOGRAPHICAL
   SECTION ONLY (JRAS 1912, 1-30), so the pre-Islamic two-thirds where the
   Sasanian wars sit has no English named by the authority on the text. Le
   Strange & Nicholson's Persian edition is open WITH editors, publisher and
   year in its own metadata. REFUSED anyway: OCR corrupt, page-number series
   never disentangled, and NO ROMAN PASSAGE CONFIRMED AT ANY PAGE.
```

**THE CANDIDATE FINDING, RECORDED IN `F5_CANDIDATES.md` AND NOT TAKEN AS A
RULING: FINDING 45's seam is necessary and it is not sufficient.** The tier needs
a genre nobody translated **and** a text somebody keyed. East Asia has Kanripo;
Southeast Asia had digital epigraphic texts; Persia and South Asia have
photographs of books. That predicts the tier's yield from a tradition's
**digitisation** history, which is a public fact about infrastructure rather than
a judgement about scholarship — a different claim from FINDING 41's and from
FINDING 45's, and testable in a way neither of them is. **Ruling 39 is why the
hunt document does not take it: Part 3 rules.**

### The four browser passes that were asked for and are still owed

**Only the first can still fill a slot.** All four are blocked to every fetcher
tried and none is blocked to a person.

1. **Bhaṭṭotpala.** `archive.org/details/brihatsamhitavarahamihirabruhatcommentaryofbhattotpalasudhakaradvivedipart1vss18_575_C`
   (Dvivedī, VSS 18, **CC0**, the edition scholarship cites) or
   `archive.org/details/BrihatSamhitaBhattotpalasSanskritCommentaryVol1`
   (Tripāṭhī — its own contents list puts adhyāya 2 at pp. 12–24, so verse 14
   should fall near printed **pp. 17–19**, roughly **scan pages 47–49**; that is an
   inference from page density and **must not be written up as a reading**). Find
   adhyāya 2 verse 14 and answer four things: is there commentary under it, is it
   running prose or a three-word gloss, roughly how many lines, and which scan is
   more legible. **Know what "yes" buys before saying it:** discursive prose commits
   the curator to hand-capturing a page of Devanagari from a corrupt-OCR scan,
   the most expensive capture in this tranche.
2. **`parsigdatabase.com` and `noorlib.ir`** — both have refused every automated
   request since F3, and every claim in this repository resting on parsigdatabase
   rests on a human pass nobody has made. Does either give clean copyable Persian?
3. **DASI, `dasi.cnr.it`, for CIH 541** — Abraha receiving embassies from the
   Negus, the Roman emperor and the Persian king, 548 CE. Anubis blocks fetchers,
   not people. This fills no F5 slot; it either opens or closes the entire Ancient
   South Arabian corpus for F6 and F7.
4. **The Mojmal's title page**, `archive.org/details/MujmalUt-TawarikhWal-QisasFarsi/page/n0/mode/2up`
   — editor, publisher, year. Expected: Bahār, Tehran 1318 Sh./1939.

### The arithmetic, so Part 3 decides it with the number in front of it

If both slots are recorded as failures, **F5 delivers 5 of 7, the vme tier lands
at 5 of 10, and the corpus lands at 54 against the 56 ruling 69 recorded as
missed.** The alternative Part 2 put to the project owner and he declined for now
was re-pointing a failing slot to East Asia and taking the Taiping Huanyuji —
which qualifies, and whose opening ~1,693 characters are Hou Hanshu matter the
corpus already holds as `eastasia-02` and Hirth translates in full. **That option
is still open and it is Part 3's to take or refuse.**

---

## The gloss declarations — F5 must declare 2 and has 4 candidates

`gloss_capable_records` is **7, reachable with zero slack**: 3 declared + F5 2 +
F6 1 + F7 1. **If F5 declares fewer than two, `check_delivery` fails the tree
that day rather than at F7's close.**

All four candidates above are `contested_reading`; **none is a
`hedged_identification`**, the kind ruling 62 had to take at a discount; and each
has a published, reachable source **on both sides** of the dispute. Three are
stronger than anything F3 or F4 declared.

**The mechanical requirement still governs and it is where F3 lost a declaration:
the hedge AND the statement that the reading is uncertain must both sit inside a
RETRIEVAL-ELIGIBLE chunk — `original_text_excerpt` or `reference_translation` —
and not in `notes`, which the loader does not chunk.**
`eastasia-05-liangshu-qin-lun` is the pattern: the published alternative and the
uncertainty go into `reference_translation`, after the translation itself.

**And the rule that killed the Liangshu's second reading applies to all four: an
alternative this project supplied itself is worth nothing.** That is why the
Bṛhatsaṃhitā survived — and why it took reading Sastri & Bhat at the page rather
than accepting the hunt's report of it.

## Also owed by F5 and not yet written

**Three `expect_quoted_from_original` gold cases.** The allocation declares 3 and
none is written. They are capped by F5's `verbatim_with_provenance` slots, and
under ruling 56 they count only on records that HOLD a `reference_translation` —
so all four candidates above qualify and the vme record does not. The one
`vme_quotation_case` is done (`tang-huiyao-fulin-clock`).

---

## What Part 2 found and did NOT rule on

**1. A tenth instrument and an eleventh exist, both are RED, and neither is in
any state block this block has written.**

```
python -m ingest.gazetteer --check      RED, exit 1
node ui/check_ui.mjs                    RED, exit 1
```

Both are working instruments exiting non-zero correctly. **The trap is the shape
of the omission:** `ui/test_build_ui_data.py` IS in the nine and is green at 19 —
it tests the build LAYER — so a UI-named suite reports green in the block a reader
actually meets, while the UI's own staleness guard reports `ui/data.js` behind by
**622 files**. That bundle was last committed at `f54c585`, D1 step 2, and carries
three East Asia records against the corpus's seven, so it predates F3's first
curated record. `ingest.verify` prints the pointer in its own note: *"Resolution
is not checked here — run `python -m ingest.gazetteer --check`, which is the only
thing that turns an id into a coordinate."* The pointer exists; the block ignores
it.

**The gazetteer red line is ONE line with TWO unrelated causes**, separated by a
refresh run against the pinned dump **on a copy in /tmp — nothing tracked was
touched**:

- `africa-04-silko-talmis` → `pleiades:786108` — **resolvable from the pinned
  2026-08-10 dump**; the cache was simply never refreshed after that placement was
  added. A repair, not a decision.
- `eastasia-04-jingjiao-stele` → `pleiades:246024` — **not in the pinned snapshot
  at all**: *"These ids are not in the dump. They have not been guessed."* Either
  the id is wrong or it is a Pleiades place created after 2026-08-10, and
  resolving it means a newer dump, which moves a dated provenance artifact.

Side observations from the same run: 54 of 55 ids resolve; `40186` and `906027`
have neither point nor extent. **`--probe` needs the network and the bridge proxy
returns 403 for `pleiades.stoa.org`, so checking 246024 is a browser job.**

**2. The curation-cost column has changed meaning, and the ledger says so rather
than the result document.** Record 36's `source_hunting` is entered as an
**estimate carrying a warning**: the hunt ran as a machine re-verification in
parallel across four regions, and that is not a human reading catalogues, which
is what the same phase measured for records 25–35. Ruling 46's comparator is
`within_tranche`, so this is a change in what the number MEANS and **not a faster
tranche**. Record 36 totals 35.0 min — 7.5 `text_capture` measured, 25
`source_hunting` estimated, 2.5 `authoring` measured. **A G3 reader must not read
the tranche's falling per-record cost as efficiency.**

**3. `git diff --stat` structurally cannot see a record.** `.gitattributes` sets
`data/seed_corpus/** -text -diff=auto` to protect the citation offsets — correctly,
and for the reason the file states at length. The consequence is that every record
commits as `Bin 0 -> N bytes` with zero insertions. **FINDING 52 and FINDING 61
make reading `git diff --stat` before every commit a rule, and for the one class
of file this project cares about most that instrument reports a byte delta and no
lines.** Observed on record 36; record 35 committed the same way. Named, not
fixed.

**4. The capture rule was broken by a progress report, not by a fetch** — see
`southasia-05` above. The rule as written guards the locating fetch. Nothing
guards the session's own summaries back to the curator, and that is where it went.

---

## What has already been decided — do not re-open these

- **56, not 60**, recorded as missed (ruling 69, amended by 73). `total_at_60` and
  `by_tier_at_60` are not lowered. **If both vme slots fail, the number becomes 54
  and it is recorded as missed in the same way** — it is not lowered either.
- **The gloss target is 7**, reached twice from two directions, with zero slack.
- **Every region clears the source-language floor** under the plan.
- **Sub-Saharan Africa's F6 slot requires `local_language`** and cannot be filled
  with a third Greek record. F6's, not this session's.
- **FINDING 41 NARROWS** rather than standing (ruling 67), and the evidence is
  delivery, not the experiment ruling 53 designed.
- **Ruling 46 forbids reading the aggregate cost per record.**
- **Do not re-take the F4 ranking run.**
- **`[Siam, Cambodja?]` is not an ordinary gloss** — ruling 62 took it with a
  discount and the discount is DATA.

---

## The workflow rules that carry

**The capture path.** Source text and published translations are **pasted by the
curator from the cited page**, every record. `WebFetch` drops lacuna markers and
substitutes U+0027 for U+2019 — measured twice (FINDINGS 48, 50).
`archive.org/_djvu.txt` is **not the page** (FINDING 53), and Part 2 measured what
that costs on a Devanagari scan.

**A locating fetch must not reveal what it located — and neither must a progress
message.** Part 2 kept the first half and broke the second. The corrections the
blind paste made to record 36's locating fetch are what the rule is for.

**A model CAN be the diff. Propose it; never apply it.**

**Write BYTES**, under each file's own newline convention — this repository is LF
throughout and `.gitattributes` disables all EOL conversion because 168 archived
citation spans point into the corpus by exact offset. Read `git diff --stat`
before every commit, **and know that it cannot see a record** (item 3 above).

**Never run a mutation harness where it can be interrupted** (FINDING 59). Host
only. And **check your own edits against FINDING 66** — Part 2 moved a literal in
`ingest/verify.py` and checked no harness named it before committing.

**From the bridge use `git --no-optional-locks`.** And note what Part 2 hit: the
bridge **cannot delete files by default**, so git cannot remove its own
`.git/index.lock` and a commit dies half-done. `device_request_delete_permission`
on the repo root fixes it for the session. The bridge also has **no git identity**
— pass `-c user.name -c user.email` per commit rather than writing to
`.git/config`.

**Close a span that crossed a break** with `stop --minutes N --because "…"`
(FINDING 54).

---

## Still owed, unchanged from F5 Part 1 unless marked

- **`scripts/mutate_part8.py` does not mutate `eval/test_answer_eval.py`** — six
  data-driven guards with no mutation proving they can fail.
- **`scripts/test_harnesses.py` is mutated by nothing**, and it is now at **43**
  assertions.
- **`mutate_distractors.py`** has no BASELINE block, no `MUTATIONS` list and no
  target verification.
- **Six mutation targets across three harnesses match more than one line.**
  Counted, not gated; the condition for asserting it is in FINDING 66.
- **FINDING 58's shared matcher** — nine copies of one three-line rule.
- **Ruling 65's renderings debt** — the C2 fused arm, now four tranches without a
  reading.
- **FINDING 67** — `total_at_60` is the size of the plan and the file calls it a
  target.
- **FINDING 68** — the SPEAKING subtotal is reported nowhere.
- **NEW: the two red instruments** are in no state block, and `ui/data.js` is
  stale by a whole block.
- **The floor is calibrated at 24 records**; `recalibration_corpus` is a pair with
  both halves null until Block F closes.

---

## Order of work

1. **The nine suites on the HOST at `7e6c021`.** They have only been run on the
   bridge, on an interpreter this session changed under its own hand.
2. **Capture the four records.** Blind paste, curator only. `arabia-05`,
   `arabia-06`, `persia-05`, `southasia-05`.
3. **Declare F5's two gloss-capable records** from the four candidates.
4. **Write the three `expect_quoted_from_original` gold cases.**
5. **The four browser passes** — pass 1 can still fill South Asia's vme slot.
6. **Decide the two vme slots**: record both as searched failures, or re-point one.
   The evidence is in `F5_CANDIDATES.md` and the arithmetic is above.
7. **Ingest, embed, and take the ranking run AFTER the records are in the index.**
   Host work, Docker and the gateway, and it costs API calls. `beaten_by` landed
   in F5 and no archived run carries it, so the archive this produces is the first
   that can see a crowder.
8. **Read rulings 70, 71 and 72.** Report `beaten_by` AND `rank` for both
   `china-describes-rome` pairs — ruling 71's blind spot is declared in advance and
   ranks falling while the record is absent from both intervals is the recall
   window, not evidence against FINDING 43.
9. **`F5_PART2_RESULT.md`**, and only then **`F5.closed = true`**.

---

# The sentences that travel, into F5 Part 3

**F5 has delivered one record of seven and two of its documents now say it
curated something, which is the same trap one step further on.**

**Two slots failed after finding exactly what they were looking for: the
untranslated genre is there in Persian and in Sanskrit, and the original is a
photograph of a book.**

**The tier needs a genre nobody translated AND a text somebody keyed, and that is
a claim about digitisation rather than about scholarship.**

**A length reported in characters had been measured in bytes, and the only
instrument that could see it was a person reading the page.**

**Two Song compendia disagree about one embassy in 643, and the corpus now holds
both without correcting either.**

**There is a tenth instrument and an eleventh, both red, and the state block
everybody reads lists a UI suite that is green while the UI's own bundle is stale
by a whole block.**
