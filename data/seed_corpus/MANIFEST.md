# Seed Corpus Manifest — Phase 1, Part 2

24 documents across all 7 regions (target was ~25-30, 3-5 per region). Each document
is a structured JSON record with original-language text (or excerpt/note), a reference
translation where one exists, source language code(s), stable citation, rough date, and
region. See `manifest.json` for a machine-readable index.

## Persia (3)
- **ŠKZ / Res Gestae Divi Saporis** — trilingual (Middle Persian/Parthian/Greek)
  inscription of Shapur I at Naqsh-e Rostam, naming Roman emperors Gordian III, Philip
  the Arab, and Valerian. Hero-demo source named in the AI Technology Showcase brief.
- **Sasanian silver hunting plate** (British Museum 1908,1118.1) — find record.
- **Sasanian silver drachm of Shapur I** (British Museum 1843,0620.5) — coin record.

## Arabia (4)
- **Periplus of the Erythraean Sea**, §27-29 — the Frankincense Country / Cana (Greek).
- **Palmyrene Tax Tariff** (CIS II 3913) — bilingual Palmyrene Aramaic/Greek, 137 CE.
  *Original text not yet transcribed — flagged for follow-up.*
- **Epitaph of Raqōš** (JSNab 17) — Nabataean/Old Arabic tomb inscription, Hegra, 267 CE.
- **Jabal Ḏabūb inscription** — Late Sabaic graffito, 6th c. CE. *Chronologically later
  and not directly Rome-linked — candidate for a stronger replacement.*

## East Asia (3)
- **Weilüe**, Section 11 — "The Kingdom of Da Qin (Rome)" (Classical Chinese). Hero-demo
  source named in the AI Technology Showcase brief.
- **Hou Hanshu** 88 — the 166 CE "Andun, King of Da Qin" embassy record.
- **Hwangnam-daechong Roman Glassware** — Late Roman (Syrian) glass in a Silla royal
  tomb, Gyeongju, South Korea (National Treasure No. 193).

## South Asia (4)
- **Akananuru 149** — Tamil Sangam poem naming Yavana ships at Muziri.
  *Original Tamil text not yet transcribed — flagged for follow-up.*
- **Periplus of the Erythraean Sea**, §53-56 — Muziris, Nelkynda and the Limyrike coast (Greek, Müller 1855; English, Schoff 1912). Original and reference translation both cover §53-56 as of 2026-08-10 — the corpus's primary back-translation gold case.
- **Muziris Papyrus** (SB XVIII 13167) — Roman-Alexandrian loan/cargo contract, 2nd c. CE.
- **Pattanam excavation record** — candidate site of ancient Muziris, Kerala.

## Southeast Asia (3)
- **Óc Eo Antoninus Pius medallion** — gold pendant imitating a Roman coin, Mekong Delta.
- **Óc Eo site report** — Funan port culture, possible identification with Cattigara.
- **Khao Sam Kaeo Roman intaglio** — carnelian gem, Thai-Malay Peninsula.

## Sub-Saharan Africa (3)
- **Ezana Stone** — trilingual (Ge'ez/Sabaean/Greek) royal inscription, Aksum, 4th c. CE.
  *Full trilingual text not yet transcribed — flagged for follow-up.*
- **Aksumite gold coin of Ezanas** (British Museum 1915,0108.81), found in Yemen.
- **Periplus of the Erythraean Sea**, §4-6 — Adulis and King Zoskales (Greek).

## Scandinavia (4)
- **Hoby treasure** — Roman silver drinking cups (signed, Iliad scenes), Lolland, 1st c. CE.
- **Gudme denarius/siliquae hoards** — Funan, Denmark, 4th c. CE Roman silver.
- **Vimose inscriptions** — earliest datable Elder Futhark runic texts, c. 160-300 CE.
- **Illerup Ådal weapon deposit** — 194 Roman denarii among Germanic war booty, c. 205 CE.

## Cross-region notes
- The **Periplus of the Erythraean Sea** appears four times (Arabia, South Asia,
  Sub-Saharan Africa) as different sections of the same Greek text — a deliberate choice:
  it is the connective source spanning three regions and a good test of whether
  retrieval correctly distinguishes sections of one work.
- Several records have a `original_text_excerpt` that is paraphrased or partial rather
  than a verbatim transliteration. These are flagged in each record's
  `original_text_note` field and in `manifest.json` → `follow_up_before_ingestion`.
  Before Part 3 (ingestion & chunking), pull verbatim original-language text from the
  cited critical editions for: Palmyrene Tariff, Weilüe, Hou Hanshu, Akananuru 149, and
  the Ezana Stone.
- Triangulation clusters worth using as hero demos in later phases: **Muziris**
  (Tamil poem + Greek Periplus + Greek papyrus + archaeology, southasia-01 to -04) and
  **Adulis/Aksum** (Greek Periplus + Ge'ez/Greek/Sabaean inscription + coinage,
  africa-01 to -03).
