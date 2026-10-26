# **Mundus Ulterior — Phase 1 Getting-Started Guide**

*Grounded Cross-lingual Ask — Pillars 1 (cross-lingual retrieval & provenance-preserving translation) and 6 (groundedness, citation & evaluation). Companion to the AI Technology Showcase brief.*  
**Scope decision for this phase:** a **broad thin slice** — 3–5 sources from *every* one of the seven regions — rather than the brief's deep dive into Rome ↔ Persia. You get end-to-end proof of the hero capability and the trust layer across the full geographic spread first, and go deep in later phases. Stack is the brief's reference stack, used as-is.

## **0\. What "done" looks like for Phase 1**

Before any code, fix the target so every step below has a purpose. At the end of Phase 1 you should be able to: type a question **in English**, have the system retrieve a passage that was written in a **regional language** (Classical Chinese, Geʿez, Middle Persian, Tamil, etc.), answer in English, and render the answer as a set of **clickable claims** — each opening the **original passage beside its translation** with a **translation-confidence badge**. Behind it, an **eval harness** scores groundedness and refuses/flags any answer below a hard floor. Typing the same query *in the source language* should return the same evidence — proof the embedding space, not a keyword match, did the work.  
That single sentence is the Phase 1 exit gate. Everything below builds toward it.

## **1\. Prerequisites & environment**

Set up the skeleton once so later steps are pure feature work.

> * **Language/runtime:** Python 3.11+. Create a fresh virtual environment (python \-m venv .venv) and a requirements.txt / pyproject.toml.  
> * **Repo layout:** ingest/ (fetch \+ chunk \+ embed), retrieve/ (search), answer/ (translation \+ assembly), eval/ (harness \+ datasets), ui/ (thin front end), data/ (seed corpus, git-ignored for large blobs).  
> * **Postgres 16 with pgvector:** run it in Docker (pgvector/pgvector:pg16 image, port 5432). This is your vector store for Phase 1; the brief graduates to Qdrant later.  
> * **Model-agnostic gateway:** stand up a thin router (LiteLLM proxy, or a small internal module) that all LLM and embedding calls go through. This is the "mature call" from the brief — it lets you swap/compare models without touching app code, which is the whole point of a tech-exploration build. Do this *first*, before you wire any model in directly.  
> * **Secrets:** put API keys behind the gateway config, never inline.

**Milestone check:** a script that sends "hello" through the gateway to one chat model and one embedding model and prints both responses. If that works, the plumbing is sound.

## **2\. Assemble the seed corpus — the thin slice**

This is the step that makes the phase broad instead of deep. Pull **3–5 sources per region** (\~25–30 documents total). Bias hard toward sources that are (a) in the regional language, (b) already have a scholarly translation you can hold out as ground truth, and (c) come from an **openly accessible** corpus or museum API with a stable citation. Candidates below are a starting slate, not a commitment — swap freely.

| Region | Candidate seed sources (3–5) | Where to get them (open) |
| :---- | :---- | :---- |
| Persia | Šapur I trilingual inscription (ŠKZ) at Naqsh-e Rostam; Paikuli inscription (Narseh); a Sasanian frontier account; Sasanian coin/silver catalogue records | Corpus Inscriptionum Iranicarum; DASI; museum collections (British Museum, Hermitage) |
| Arabia | Periplus of the Erythraean Sea (Red Sea / incense-route sections); a Palmyrene bilingual text (e.g. Tariff); a Nabataean inscription; an Old South Arabian (Sabaic) inscription | DASI (pre-Islamic Arabian inscriptions); PHI Greek Inscriptions; Perseus/topostext for the Periplus |
| East Asia | Weilüe account of Da Qin (Classical Chinese); Hou Hanshu account of the 166 AD "Da Qin envoy"; a Roman glass/coin find record | ctext.org (Chinese Text Project); museum collections for finds |
| South Asia | Tamil Sangam poems referencing Yavanas (Tamil); Periplus Muziris passage; Arikamedu/Pattanam Indo-Roman find record; the Muziris papyrus | Project Madurai (Tamil e-texts); topostext; institutional archaeology reports |
| Southeast Asia | Óc Eo Roman medallion / Antoninus Pius coin find record; a regional maritime-route archaeological report; a Mediterranean-style object findspot record | National museum collections (Vietnam, Thailand); open archaeology journals |
| Sub-Saharan Africa | Ezana / Aksumite Geʿez inscription; Aksumite coinage record; Periplus passage on Adulis | Beta maṣāḥǝft (Geʿez); museum coin collections; topostext |
| Scandinavia | A denarius hoard record (e.g. Gudme/Fyn); a Roman-import find (bronze, glass); a runic/Old Norse scholarly source | National museums (Denmark, Sweden); Skaldic Project; Europeana |

**For each document capture, at minimum:** the source text (original language), a reference translation if one exists, source language code, region, a stable citation/permalink, and rough date. Store this as structured records — you will need every field for provenance and eval.  
**Milestone check:** \~25–30 documents on disk, each with original text \+ provenance metadata, spanning all seven regions.

## **3\. Ingestion & chunking with provenance baked in**

Write an ingestion pass (ingest/) that reads each seed record and splits it into passages. Two rules that matter for the trust layer:

> * **Chunk on meaning, not bytes.** Keep an inscription line or a poem stanza whole where you can — a mangled half-passage destroys both retrieval and groundedness.  
> * **Every chunk carries its provenance forward:** source id, language, region, char offsets into the original, citation, date. This metadata is what makes a citation clickable later; if you drop it here you cannot reconstruct it.

Persist chunks to a Postgres table with columns for the text, the metadata, and a vector column (added in the next step).

## **4\. Multilingual embeddings & the cross-lingual index**

This is the mechanism that makes Pillar 1 real. Use **BGE-M3** (open, 100+ languages) as the primary embedder, called through the gateway so you can later A/B it against Gemini Embedding or Cohere Embed.

> * Embed every chunk and write the vector into the pgvector column; build an index (HNSW or IVFFlat).  
> * The key property: BGE-M3 places an **English query** and a **Classical-Chinese passage** near each other in the same vector space. Verify this explicitly — embed an English sentence and its known translation and confirm high cosine similarity across the language boundary. If that check fails, nothing downstream works.  
> * BGE-M3 also gives you sparse \+ dense signals; for Phase 1 dense-only is fine. Hybrid/reranking is an optional later win (Appendix B of the brief).

**Milestone check:** the cross-lingual similarity sanity test passes for at least one pair per region.

## **5\. Cross-lingual retrieval**

Build retrieve/: take an English (or any-language) query, embed it through the same gateway/embedder, run a vector search over pgvector, return the top-k chunks *with their full provenance metadata attached*. Add optional filters (region, date range) — cheap now, useful for demos.  
**The defining test for Pillar 1:** run a query in English, note the retrieved chunks; run the semantic equivalent typed in the source language; confirm you get substantially the same chunks. That equivalence is the proof the brief's hero demo hinges on.

## **6\. In-loop translation with a back-translation confidence check**

Now the "provenance-preserving translation" half of Pillar 1\. Inside the answer loop (answer/):

> * **Translate** each retrieved non-English passage to English via an LLM translation step (through the gateway).  
> * **Back-translate** the English back to the source language and compare against the original (embedding similarity and/or an LLM judge). Turn the agreement into a **confidence score** and a badge (e.g. 0.91).  
> * **Preserve provenance:** keep original text, translation, and confidence bound together on the passage object all the way to the UI. Never discard the original.

Treating MT output as something to *verify* rather than trust is the senior signal the brief calls out — build the self-check in from day one, not as a later polish.

## **7\. Grounded answer assembly with inline citations**

Compose the answer (answer/): give the LLM the translated, retrieved passages and instruct it to write an English answer where **every claim is tied to a specific source passage**. Emit the answer as structured claim→citation pairs, not a prose blob — each claim references the chunk id it came from, so the UI can make each sentence clickable. If a claim can't be tied to a retrieved passage, it doesn't ship.

## **8\. The trust layer — groundedness eval harness & hard floor (Pillar 6\)**

This is what turns "I designed a system" into "I can prove this one is trustworthy," and it is half of Phase 1 — not an afterthought. Build eval/:

> * **Hand-label a small gold set** — 20–40 question/answer/source triples spread across the seven regions. This is your Phase 1 ground truth; keep it in the repo.  
> * **Score three things per answer:** *groundedness* (does each claim follow from its cited source?), *retrieval quality* (did the right passage get retrieved?), and *translation faithfulness* (is the English claim faithful to the original-language source?). Use an LLM-judge plus your back-translation signal; spot-check judges against your hand labels.  
> * **Enforce a hard groundedness floor:** below a threshold, the system withholds or visibly flags the answer instead of guessing. Make the refusal path work — it's a feature, not a failure.  
> * The novel problem the brief highlights: groundedness must hold *across a translation boundary* ("is this English claim faithful to a Geʿez source?"). Make that its own metric.

**Milestone check:** a dashboard/report showing the three scores over the gold set, and at least one example where the floor correctly withheld a weak answer.

## **9\. A thin UI that makes groundedness felt**

Keep it minimal for Phase 1 — no maps yet (that's Pillar 5, Phase 3). One page: a query box, the English answer with **every claim rendered as a link**, and a panel that opens on click showing **original passage \| English translation \| confidence badge**, plus a "why this translation" expander revealing the back-translation. A reviewer clicking a sentence and landing on a Geʿez source beside its translation is the moment that sells the whole project.

## **10\. Phase 1 gate — kill / pivot / persevere**

The brief phases each stage on an honest decision. For Phase 1, **persevere** if: cross-lingual retrieval returns the right regional-language passage for English queries across most regions; translation confidence tracks real quality; the groundedness floor holds; and the click-through citation experience feels real. **Pivot** if cross-lingual retrieval is weak for the sparse-evidence regions (Southeast Asia, Scandinavia) — narrow the slice or lean on the denser pairs. **Kill/rethink** if the embedding space can't bridge languages at all (it should — BGE-M3 is proven — so this is a real red flag pointing at a data or indexing bug).

## **Suggested order of attack (dependency-aware)**

> 1. Gateway \+ Postgres/pgvector skeleton (§1)  
> 2. Seed corpus with provenance metadata (§2)  
> 3. Ingestion & chunking (§3)  
> 4. BGE-M3 embeddings \+ cross-lingual similarity sanity test (§4)  
> 5. Retrieval \+ the same-query-two-languages test (§5)  
> 6. Translation \+ back-translation confidence (§6)  
> 7. Grounded claim→citation answer assembly (§7)  
> 8. Eval harness, gold set, groundedness floor (§8) — build alongside 5–7, not after  
> 9. Thin click-through UI (§9)  
> 10. Run the exit gate, make the kill/pivot/persevere call (§10)

## **Notes on going broad instead of deep**

Two things to watch with the thin-slice approach. First, the **region gradient** from the brief is now visible immediately: Persia and Arabia give dense, often bilingual-at-source evidence, while Southeast Asia and Scandinavia give sparse, single-sided finds. Expect retrieval and eval numbers to be lopsided — that's a finding to report, not a bug to hide. Second, keep the slice **balanced**: it's tempting to over-collect for the easy regions. Cap each region at 3–5 so the demo genuinely spans all seven and you don't accidentally rebuild the Persia deep-dive. When Phase 1 clears its gate, Phase 2 (the graph) is where you pick the dense pairs to go deep on.