# MUNDUS ULTERIOR

*“The world beyond”*

**AI Technology Showcase**

A companion technical brief — the AI techniques the product is designed to demonstrate,

and how each one earns its place in the build.

**Product concept:** An interactive web portal — maps + chat — tracing the connections between the Roman Empire (27 BC – 1204 AD) and Sub-Saharan Africa, Persia, Arabia, South Asia, Southeast Asia, East Asia, and Scandinavia.

**Prepared for:** Rob Padilla, PhD

**Goal of this document:** Technology exploration — maximize the surface area of modern AI techniques the build gets to touch, compare, and honestly evaluate.

## 1. Purpose & the distinctive bet

This brief accompanies the Mundus Ulterior product concept. Where the concept describes what the portal is for a history enthusiast, this document describes what it is for a builder: a deliberately ambitious testbed for the modern AI stack, chosen because the subject matter forces the interesting problems rather than letting you route around them.

Most portfolio-grade AI portals are, underneath, “RAG over an English Wikipedia dump.” Mundus Ulterior cannot be that, and that is the point. Its concept — *connections and influence between Rome and seven regions — from its frontier neighbours in Persia and Arabia to the far reaches of East Asia and Scandinavia, drawn from local non-English sources* — breaks the easy path in three productive ways:

  - **The best sources are not in English.** Tamil, Geʿez, Middle Persian (Pahlavi), Classical Arabic, Classical Chinese, and Old Norse corpora make cross-lingual retrieval and machine translation load-bearing, not decorative.

  - **The thesis is connection, not fact.** “How did Roman glass reach Han China?” is a multi-hop question across regions and centuries — the query type that justifies a knowledge graph instead of flat retrieval.

  - **The evidence is multimodal.** Museum data is images of artefacts and inscriptions, not clean prose — which pulls vision, OCR/HTR, and geospatial reasoning into scope.

The through-line of everything below: cross-lingual retrieval is the hero capability, the knowledge graph is justified by cross-region multi-hop queries, and every claim the system makes is provable through a clickable citation that shows the original-language source beside its translation. Techniques that cannot be tied back to that line are noted as optional.

> **The one-sentence pitch**
>
> *Mundus Ulterior turns scattered, multilingual, half-digitized scholarly and museum sources into a grounded, explorable knowledge product — and proves each answer against a source the user can open in its original language.*

### The region gradient — and why Persia and Arabia matter

The seven regions are not equidistant from Rome, and that is analytically useful rather than a complication. Persia and Arabia sat on Rome's doorstep: Parthia and then Sasanian Iran were Rome's peer rivals for the better part of five centuries, while Arabia anchored the incense trade and — through Palmyra and the Nabataeans — brokered goods between the Mediterranean and the Indian Ocean. Their evidence is dense, frequently bilingual at the source, and documented from both sides. The farther regions — East Asia, Southeast Asia, Scandinavia — yield sparse, mediated, often single-sided evidence. Designing for both ends of that gradient is itself part of what the build demonstrates: the same pipeline must handle a trilingual royal inscription on a contested frontier and a lone hoard of denarii at the edge of the known world.

> **Why Persia and Arabia sharpen the showcase**
>
> **Persia —** Rome's peer rival for five centuries left the densest external record of any region, including trilingual royal inscriptions (Middle Persian, Parthian, and Greek) — a perfect cross-lingual retrieval testbed, since one of the three languages is the Roman side's own.
>
> **Arabia —** The incense route and the caravan cities of Petra and Palmyra make it the archetypal intermediary between Rome and the Indian Ocean world — an ideal multi-hop, broker-node case for the knowledge graph.

## 2. The six pillars at a glance

Each pillar is a technique family the build showcases. They are ordered by how distinctive each is to this project specifically — pillar one is the capability a generic portal cannot copy; pillar six is table stakes done unusually rigorously.

| \# | Pillar                                                  | Headline technique                              | Distinctiveness to MU     |
| ------ | ----------------------------------------------------------- | --------------------------------------------------- | ----------------------------- |
| **1**  | Cross-lingual retrieval & provenance-preserving translation | Multilingual embeddings + in-loop translation agent | Very high — unique hero       |
| **2**  | GraphRAG for cross-region connections                       | Knowledge graph + graph/vector fusion               | High — justifies the graph    |
| **3**  | Multi-agent orchestration                                   | Planner / retriever / translator / verifier team    | Medium — earns its keep here  |
| **4**  | Multimodal artefact & inscription intelligence              | Vision-language models + HTR/OCR                    | High — museum data is visual  |
| **5**  | Geospatial & temporal agentic reasoning                     | Map/route tools + time-aware diffusion              | High — the Orbis parallel     |
| **6**  | Groundedness, citation & evaluation                         | Inline cited answers + eval harness                 | Table stakes, done rigorously |

## 3. The pillars in depth

### Pillar 1: Cross-lingual retrieval & provenance-preserving translation

**What it is** A user asks in English; the system retrieves from documents written in the regional languages and answers in English while showing the original passage, its translation, and a translation-confidence flag. This is powered by multilingual embedding models that place a query and a differently-languaged document into the same vector space, plus a dedicated translation step inside the answer loop with a back-translation self-check.

**Why Mundus Ulterior justifies it** The concept explicitly calls for local, non-English sources and machine translation as a first-class feature. The best evidence for Roman contact with these regions is frequently only available in the regional language, so retrieval that is blind to non-English text would miss the very connections the product exists to surface.

**What it demonstrates** That you can build retrieval that is genuinely language-agnostic, reason about translation quality rather than trusting it blindly, and preserve provenance across a language boundary — the hardest and most credible part of the whole system.

**How you'd demo it** Ask a question in English and watch the answer cite a Classical Chinese or Geʿez passage, rendered side-by-side original/English, with a confidence badge and a “why this translation” expander showing the back-translation. Then repeat the query typed in the source language and show it returns the same evidence — proof the embedding space, not a keyword match, did the work.

> **Hero demo — cross-lingual retrieval**
>
> *Query (English): “What did Chinese records say about Roman envoys or traders?”*
>
> *Retrieves the Weilue passage on Da Qin in Classical Chinese → shows original + translation + 0.91 confidence → same result when the query is typed in Chinese.*

### Pillar 2: GraphRAG for cross-region, multi-hop connections

**What it is** A knowledge graph models artefacts, sites, materials, trade routes, texts, people, and time-spans as nodes and typed relationships. At query time the system fuses graph traversal (precise, multi-hop) with vector retrieval (fuzzy, semantic) — GraphRAG — so a question can walk a chain of relationships that flat retrieval cannot follow.

**Why Mundus Ulterior justifies it** The product’s thesis is connection and influence, not single facts. Straight Q&A over one region needs no graph — vanilla RAG handles it. But “trace the path by which a Roman material reached East Asia” is an inherently multi-hop traversal, and that class of question is exactly what the graph is designed around. If a query can be answered without the graph, it belongs in pillar one; the graph exists for the ones that can’t.

**What it demonstrates** That you know when a knowledge graph is warranted rather than reflexive — and can implement graph/vector fusion and text-to-Cypher retrieval, not just describe it on a slide.

**How you'd demo it** Run a designated hero query end-to-end and expose the traversal: show the chain of nodes and edges the system walked (glass → workshop → route → entrepot → findspot), then the grounded prose answer built from it. Contrast it live against a vanilla-RAG baseline that fumbles the same question to make the graph’s contribution visible.

> **Hero demo — multi-hop traversal**
>
> *Query: “How did Roman glassmaking connect to trade routes that reached Han China?”*
>
> *The answer is assembled by walking a path across regions and centuries — and the walked path is shown as evidence, not hidden.*

### Pillar 3: Multi-agent orchestration

**What it is** A small team of specialized agents — a planner that decomposes the question, a retriever, a translator, a graph/traversal agent, and a verifier that checks the draft answer against sources — coordinated by an orchestration loop rather than a single monolithic prompt.

**Why Mundus Ulterior justifies it** Here the extra agents are justified by real heterogeneity of work: deciding a query needs the graph vs. flat retrieval, translating a retrieved passage, and independently verifying groundedness are genuinely different jobs with different failure modes. The honest framing for a tech-exploration build is that this is where you get to compare a multi-agent design against a single instrumented loop and measure whether the agents actually earned their latency and cost.

**What it demonstrates** Orchestration judgment: composing agents around distinct responsibilities, and the maturity to show where the multi-agent version did and did not beat a simpler baseline.

**How you'd demo it** Expose the agent trace for a single question — planner’s decomposition, each agent’s tool calls, the verifier’s accept/repair decision — as an inspectable timeline. Then show the eval slide where a one-agent baseline is compared head-to-head on groundedness, latency, and cost, and be candid about the result.

### Pillar 4: Multimodal artefact & inscription intelligence

**What it is** Vision-language models describe and classify artefact photographs; handwritten-text-recognition (HTR) and OCR transcribe inscriptions and manuscripts, including non-Latin scripts; visual-similarity search finds stylistically related objects across regions. Extracted attributes flow back into the knowledge graph as new nodes and edges.

**Why Mundus Ulterior justifies it** Museum and institutional collections are fundamentally visual — an artefact is a photograph with a catalogue record, and an inscription is an image of a script. A text-only pipeline simply cannot ingest most of the primary evidence for cross-region contact, so vision and HTR are how the corpus gets built, not an add-on.

**What it demonstrates** That you can bring genuinely multimodal evidence into a grounded system — turning a photograph of a coin or a page of Devanagari into structured, queryable, cited knowledge.

**How you'd demo it** Upload an artefact image and show the system describe it, place it on the map and timeline, and surface visually similar objects from other regions. Separately, run HTR over a manuscript page in a non-Latin script and show the transcription feeding straight into cross-lingual retrieval (pillar one).

> **Hero demo — image to knowledge**
>
> *Drop in a photo of a Roman-style glass bead found at an Indian Ocean site.*
>
> *System classifies it, links it to comparable finds across regions, and cites the collection record it came from — an image becomes a graph node with provenance.*

### Pillar 5: Geospatial & temporal agentic reasoning

**What it is** The chat agent can compose map and timeline views as tool calls — plotting where and when a material, good, or belief appears and animating its plausible spread along trade routes. This is the Orbis parallel: Orbis modelled the cost and time of Roman travel; Mundus Ulterior models diffusion of influence across space and time.

**Why Mundus Ulterior justifies it** The concept names Orbis as the reference model and centres on interactive maps. Contact between Rome and distant regions is inherently spatial and temporal — a claim about influence is really a claim about something appearing in a place at a time — so an agent that reasons over geography and chronology is core, not cosmetic.

**What it demonstrates** That an agent can drive a rich visualization surface — answering by constructing a map or timeline the user can manipulate — rather than only emitting text, which is a markedly more advanced interaction pattern.

**How you'd demo it** Ask “show me how a Roman good spread eastward over three centuries” and watch the agent build an animated map with a time slider, each plotted point clickable through to its cited, possibly-translated source. The visualization is generated from a tool call, so it is grounded in the same evidence as the prose.

> **Hero demo — agent-composed map**
>
> *Query: “Map the appearance of Roman coins across the Indian Ocean world, 1st–4th century.”*
>
> *The agent returns an animated, time-sliced map; every point links to the find record behind it.*

### Pillar 6: Groundedness, citation & evaluation — the trust layer

**What it is** Every claim in an answer is anchored to a clickable source showing the original passage and, where relevant, its translation. Behind it sits an evaluation harness that scores groundedness (does the claim follow from the cited source?), retrieval quality, and translation faithfulness, with a hard groundedness floor below which an answer is withheld or flagged.

**Why Mundus Ulterior justifies it** This is table stakes for any credible system, but Mundus Ulterior raises the bar: groundedness must hold across a translation boundary, so “is this English claim faithful to a Geʿez source?” is a genuinely novel evaluation problem. Solving it visibly is what turns “I designed a system” into “I can prove this one is trustworthy.”

**What it demonstrates** Evaluation discipline — the single strongest senior signal. A number in a document proves nothing; a clickable, verifiable citation and an honest eval dashboard prove judgment.

**How you'd demo it** Make groundedness felt, not asserted: let a reviewer click any sentence and land on the source passage in its original language beside the translation. Then show the eval dashboard — including the cases where a technique from pillars 2–5 did not beat a simpler baseline, because showing negative results is itself the signal.

> **Hero demo — groundedness you can click**
>
> *Every sentence of an answer is a link. Click one → the exact source passage, original + translation + confidence.*
>
> *The eval tab shows the groundedness floor holding — and names where the graph or extra agents didn’t earn their keep.*

## 4. Reference stack

The build stays **model-agnostic behind a gateway** — the mature call and the one that keeps the showcase current as models change. Named tools below are representative choices as of mid-2026; the point of a tech-exploration build is to swap and compare them, so treat the table as a starting slate, not a commitment.

| Layer                   | Representative choice                                           | Role in the showcase                                                             |
| --------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Orchestration**           | LangGraph                                                           | Multi-agent loop, planner/verifier control flow, inspectable traces                  |
| **Vector retrieval**        | pgvector → Qdrant                                                   | Semantic + cross-lingual retrieval; start in Postgres, graduate to a dedicated store |
| **Multilingual embeddings** | BGE-M3 (open, 100+ langs) / Gemini Embedding 2 / Cohere Embed       | Cross-lingual vectors so an English query hits regional-language sources             |
| **Knowledge graph**         | Neo4j + GraphRAG                                                    | Nodes/edges for cross-region multi-hop; text-to-Cypher + graph/vector fusion         |
| **Vision & HTR**            | VLM for artefacts; Transkribus / TrOCR for scripts                  | Turn artefact images and inscriptions into structured, queryable evidence            |
| **Translation**             | LLM translation agent + back-translation check                      | In-loop translation with confidence scoring and provenance                           |
| **Geospatial**              | Map/timeline tools the agent calls (e.g. MapLibre + a routes layer) | Agent-composed, time-sliced diffusion maps                                           |
| **Evaluation**              | Groundedness + retrieval + translation-faithfulness harness         | Hard groundedness floor; baseline vs. technique comparisons                          |
| **Gateway**                 | Model-agnostic router                                               | Swap/compare LLMs and embedders without touching app code                            |

## 5. A build order that showcases early

Phase the build so it demonstrates something compelling at the end of each stage rather than only at the finish. Each phase is gated on an honest kill / pivot / persevere decision, so the project ships value even if it stops early.

| Phase                           | Focus                                                                                                                                  | What it proves                                                                       |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| **1 — Grounded cross-lingual Ask**  | Pillars 1 & 6: multilingual retrieval + clickable, translated citations over the densest, most bilingual region pair first (Rome ↔ Persia) | The hero capability and the trust layer — the felt experience that sells everything else |
| **2 — The graph earns its place**   | Pillar 2: knowledge graph + GraphRAG, built around 2–3 multi-hop hero queries                                                              | That connection-style questions work — and that you added the graph deliberately         |
| **3 — Multimodal & map**            | Pillars 4 & 5: artefact/HTR ingestion and agent-composed diffusion maps                                                                    | The corpus grows from visual evidence; answers become spatial and interactive            |
| **4 — Orchestration & honest eval** | Pillar 3: multi-agent design compared head-to-head against a single-loop baseline                                                          | Judgment — which techniques earned their keep, shown with data                           |

> **The sharp move for a tech-exploration goal**
>
> *Build Phase 1 first and make it feel real. A spec says “I designed a system.” A working, grounded, translated citation says “I shipped one.” Everything after Phase 1 is you choosing to explore more surface area — which, for this stated goal, is exactly the point.*

## 6. What each technique demonstrates

Read this as the “why a reviewer should care” column — the capability each pillar signals to someone judging the engineering.

| Technique                         | The signal it sends                                                                |
| ------------------------------------- | -------------------------------------------------------------------------------------- |
| **Cross-lingual retrieval**           | You can build retrieval that isn’t anchored to English — rare, and hard to fake        |
| **Provenance-preserving translation** | You treat MT output as something to verify, not trust — senior instinct                |
| **GraphRAG multi-hop**                | You reach for a knowledge graph when the question needs it, not reflexively            |
| **Multi-agent orchestration**         | You can compose and, crucially, evaluate an agent system against a baseline            |
| **Vision + HTR**                      | You can bring genuinely multimodal, messy real-world evidence into a grounded pipeline |
| **Agent-composed maps**               | Your agent drives a rich UI surface, not just a text box                               |
| **Groundedness eval**                 | You can prove trustworthiness — the difference between a demo and a system             |

## Appendix A — Representative source types by region

Illustrative, non-exhaustive — the ingestion strategy (pillar 4 plus an agentic source-discovery crawler) is designed to pull from open museum and institutional collections and openly accessible scholarship, with a bias toward local-language material.

  - **Persia:** Middle Persian (Pahlavi) and Parthian inscriptions and Sasanian records; trilingual royal inscriptions such as Shapur I's at Naqsh-e Rostam; Roman–Sasanian frontier accounts and Silk Road intermediary evidence; Sasanian silver and coinage in museum collections.

  - **Arabia:** Old South Arabian (Sabaic) inscriptions, Nabataean and Palmyrene bilingual texts; frankincense and myrrh incense-route evidence; Red Sea and Indian Ocean trade records including the Periplus of the Erythraean Sea.

  - **East Asia:** Classical Chinese dynastic records and geographies (e.g. accounts of Da Qin), coin and glass finds in institutional collections.

  - **South Asia:** Tamil Sangam-era references, Indo-Roman trade-site finds and hoards, Devanagari and Tamil manuscript scholarship.

  - **Southeast Asia:** Findspot records of Roman and Mediterranean-style objects along maritime routes; regional archaeological reporting.

  - **Sub-Saharan Africa:** Aksumite coinage and inscriptions (Geʿez), Indian Ocean and Red Sea trade evidence.

  - **Scandinavia:** Roman-import finds, denarius hoards, runic and Old Norse source scholarship.

## Appendix B — Optional / stretch techniques

Legitimate additional surface area for a tech-exploration build, flagged as optional because they are not required by the core through-line:

  - **Agentic source discovery:** a long-running ingestion agent that crawls museum/institutional APIs, dedupes, extracts entities, and proposes new graph edges for human review — the corpus as a living system.

  - **Confidence-aware graph construction:** edges carry a certainty score, so speculative connections are visible as speculative rather than presented as fact.

  - **Reranking & hybrid search:** a cross-encoder reranker over the hybrid dense/sparse results — an easy, measurable groundedness win worth putting on the eval board.

*Companion to the Mundus Ulterior product concept. Tooling references current as of mid-2026 and intentionally model-agnostic; named tools are representative, not prescriptive.*
