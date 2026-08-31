# F4 PART 2 START — East Asia, and a workflow that changed under F4

F4 Part 1 closed at `58c6b77`, working tree clean. The corpus is **32 records**,
digest `06aa355e9239a6c8...`, 73 chunks, 21 parallel pairs.

```
ingest.verify              green -- 32 documents
ingest.test_fidelity        58      ingest.test_cost            64
eval.test_ranking_check    241      eval.test_answer_eval      394
ui.test_build_ui_data       19      scripts/test_recover_baseline.py  RED, see below
mutate_ui_places  6   mutate_fidelity 46   mutate_ranking 103
mutate_part8     94   mutate_cost     51   -- 300 mutations
```

Read `F4_RULINGS.md` first. It is the handoff: rulings 53-59 and findings
44-50, all of them declared in Part 1 and most of them before the records they
govern. This document is only what has to be **decided or known** before Part 2
curates anything.

---

## What Part 1 delivered, against what F4 was allocated

```
ALLOCATED 7        Sub-Saharan Africa 2 vwp + 2 vme     East Asia 2 vwp + 1 vme
DELIVERED 2        africa-05-adulis-throne   (vwp, grc)  record 31
                   africa-04-silko-talmis    (vwp, grc)  record 32
```

Africa's two `verbatim_with_provenance` slots are **filled**. Everything else is
Part 2's.

**Quota state.** `expect_quoted_from_original` reached **6 of 6 at 60** and both
of Part 1's are WHICH-CHUNK cases under ruling 56 — the reading is now 6 choice
/ 2 whether-resolved, computed in two places from one imported rule. The
gloss-capable quota is at **1 of 8** and **F4 has declared none**: both of its
gloss-capable records are owed in Part 2, and F3 managed one in eight slots, so
this is the quota most likely to be missed.

---

## THE WORKFLOW CHANGED, and this is the part that will surprise Part 2

**Source text and its published translation are pasted by the curator from the
cited page. Every record. No exceptions, and no tooling removes it.**

FINDING 48 measured `WebFetch` dropping a lacuna marker and substituting U+0027
for U+2019; FINDING 50's second measurement found the same substitution again,
one character in 431, so the normalisation is systematic. Neither is visible to
any check here: `ingest.verify` asserts internal consistency, so an excerpt
corrupted before it lands resolves perfectly against the wrong characters.

**The corollary, which is FINDING 50 and is new:** the curator captures, and the
model may then DIFF the capture against the source. That is not the same job.
On record 32 the typed English differed from its source image in five places,
including one that changed the meaning, and every one was put back to the
curator and confirmed by the curator. **Proposing a diff and applying one are
different acts, and only the first is permitted.**

Budget accordingly. Two pastes per `verbatim_with_provenance` record, one per
`verbatim_machine_english` record.

---

## The three East Asia records, with their sources already established

`F4_CANDIDATES.md` carries both hunts in full. For Part 2:

**1. Cefu Yuangui 冊府元龜 970, 外臣部・朝貢 — the `verbatim_machine_english`
slot, and the most important record in F4.** A dated Byzantine embassy notice
naming its gift: 拂菻王波多力遣使獻赤頗黎、綠頗黎 — the Fulin king Boduoli sent
envoys presenting red glass and green glass, at the Tang court in Zhenguan 17
(643). This corpus already holds Roman and Byzantine glass as ARCHAEOLOGY in
three regions; this is the same substance arriving as diplomacy.
- Source text: `raw.githubusercontent.com/kanripo/KR3k0013/master/KR3k0013_970.txt`
  — clean UTF-8, CC BY-SA 4.0.
- **`zh.wikisource.org/wiki/冊府元龜` is an EMPTY SHELL** and F4_START's
  suggested route: it carries the 31 部 headings and a notice that the content
  has not been entered. Kanripo is the only reachable full text.
- English: none found, across Hirth 1885's own contents, Hirth & Rockhill 1911,
  Legge, Yule, four open sourcebook sites and eight databases. **The unresolved
  risk is Leslie & Gardiner, *The Roman Empire in Chinese Sources* (Rome 1996),
  print only** — nothing available to this project can establish whether it
  covers this text. Ruling 57 is what makes that a curable record rather than
  an impossible one, and the record must carry that boundary in its notes.

**2. Liangshu 梁書 54 — the Da Qin merchant Qin Lun 秦論, `vwp`.** In 226 CE a
merchant from Da Qin reaches Jiaozhi, is sent on to Sun Quan, is questioned
about the customs of his country, is shown captured short-statured people and
says 大秦希見此人 — "Da Qin rarely sees such people" — and is sent home with an
escort who dies on the road.
- Source: Kanripo `KR2a0018_054.txt`. English: Hirth 1885 p. 46, and **the body
  of that page was never read** — the archive.org fetch truncated. Verify it
  before relying on it.

**3. The Da Qin Jingjiao stele 大秦景教流行中國碑, 781 CE, `vwp`.** F3 banked
this as a parsigdatabase record costing a human pass; the hunt improved it.
**James Legge, *The Nestorian Monument of Hsî-an Fû* (1888) prints the Chinese
text alongside the English translation** — one public-domain volume for both
halves, at `archive.org/stream/nestorianmonumen00legg/nestorianmonumen00legg_djvu.txt`.
Alopen 阿羅本 arrives from 大秦國 in the ninth year of Zhenguan (635).
- **This is the strongest gloss-capable candidate in the tranche.** The stele's
  readings and its Syriac colophon are genuinely disputed in print, which is
  what a `refusable_with_gloss` case needs: a published alternative reading AND
  a statement that the reading is uncertain, both inside a retrieval-eligible
  chunk. Design it deliberately or the gloss quota will not be met.

**Access, established rather than assumed:** `ctext.org` returns 403 on every
text page; `zh.wikisource.org` served 2 of ~17 pages tried; the Korean NIKH
databases are robots-disallowed; `kanripo.org` itself returns 525 while its
GitHub raw mirror works perfectly. **Kanripo's base edition is the Wenyuange
Siku Quanshu**, a Qianlong recension whose editors are known to have altered
passages about foreign peoples — every Kanripo passage should be collated
against a Zhonghua Shuju edition before it is published as the reading.

---

## RULING 55's prediction is still unread, and it is the reason to curate East Asia carefully

Registered before any candidate was examined, from the archive rather than from
a document:

```
china-describes-rome-houhanshu   rank 4   recall@6 true   anchor_points_home false
china-describes-rome-weilue      rank 5   recall@6 true   anchor_points_home false
```

**Prediction: both move DOWN when Part 2's Literary Chinese records about Rome
enter the index, and `weilue` is the likelier to leave the top 6.** Falsified if
both hold — which would narrow FINDING 43 from same-subject texts to
near-duplicate objects, a smaller and more useful finding than the one on file.

Part 2 must not read this until the ranking check runs at the close. It is the
only pre-registered prediction this project has ever made.

---

## Still owed, in the order that will hurt most if forgotten

1. **RULING 54's debt: F3's six records still have no ranking pairs.** The
   ruling says they get them, each stamped
   `written_after_the_records_entered_the_index: true` and barred from every
   before/after claim. Six pairs. The flag's ABSENCE from Part 2's own pairs is
   the claim.
2. **Two gloss-capable records.** See the stele above.
3. **Africa's two `verbatim_machine_english` slots will be a SHORTFALL.** Ruling
   53 pre-declared this outcome: Ge'ez fails on the ROME criterion, not the
   translation one — every Rome-touching Ge'ez text in the open Littmann volume
   is Ezana, which this corpus holds, or Sembrouthes. That is FINDING 38's
   supply problem and not FINDING 41's search problem, and the third outcome was
   written down precisely so the close could not be forced into a binary.
4. **The FINDING 41 ruling, deferred by ruling 53**, made at F4's close with
   FINDING 45's genre seam in hand.
5. **`vimose-runes` at rank 7** — decided in F4 as a ruling, per the opening
   decision. F4 adds no Scandinavian records, so the neighbourhood will never be
   quieter.
6. **`scripts/test_recover_baseline.py` has been RED since Block E**, on
   `corpus_version` and `serving_stack`. F3 named it, F4 did not touch it, and
   it is listed here so no state block is silent about it again.
7. Carried from F2 and F3: `mutate_ranking`/`places`/`recover` BASELINE checks
   present but unexercised; ruling 40's `article_added` still reads 0;
   `ingest/test_sql.py` has never run with sqlglot AND the database; a third
   distinct UTC date at 60 is owed by three rules and booked by ruling 50.

---

## What NOT to re-derive

**Do not hunt Sub-Saharan Africa again.** `F4_CANDIDATES.md` records the whole
search, including the routes that failed and why: Meroitic is refused by
FINDING 44 (untranslated because unread, so the machine-translation path the
tier exists to exercise would produce fluent nonsense attached to a resolving
citation), the Ge'ez route is closed on the Rome criterion, and Polish
Nubiology publishes in English.

**Do not treat a tooling limit as unreachability.** Silko's English was in a 54
MB PDF this project could not open and then in JPEGs it could not parse, and
neither made it a `verbatim_machine_english` record. Ruling 57 turns on whether
a curator can REACH a translation; FINDING 50 records that reachable and
capturable are different properties, and only the first decides the tier.

**Do not read the aggregate cost per record.** Ruling 46 forbids it and the
allocation biases it downward by construction. The per-tier means today are
`verbatim_with_provenance` n=6 at 5.9 min and `verbatim_machine_english` n=2 at
3.3 min, both below `min_n_to_read_as_a_trend`, and the report says so itself.

---

## The sentences that travel, from Part 1

**FINDING 41 was measured in the two traditions most thoroughly translated into
English, and reported as a property of the tier.**

**The nineteenth-century sinologists translated the dynastic histories and left
the huiyao, the leishu and the geographies alone. The tier is fed by GENRE, not
by obscurity — and genre is something a curator can aim at.**

**A tier that can be reached by doing less work is a place to put records nobody
searched for.**

**The corpus check asserts that a quotation resolves to the characters on disk,
and nothing at all asserts that the characters on disk are the ones on the
page.**

**The automated path was wrong once in 431 characters and the human path was
wrong five times in ten lines, and the useful arrangement is not to pick one but
to make them check each other.**

**A probe was routed away from the sweep archive so it could not calibrate the
floor, and it landed in the run archive and broke a census that the same commit
reported as green.**

**Ruling 52 wrote its anti-loophole as a permanent property of the ledger and
retirement as an event, and the two disagree the moment a record that did not
exist comes to exist.**
