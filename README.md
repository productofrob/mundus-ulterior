# Mundus Ulterior

**Ancient Rome seen from beyond its frontiers, 27 BC to 1204 AD, in the words of
the sources themselves.**

Live site: **https://mundus-ulterior.pages.dev/**

Mundus Ulterior gathers 54 source records from seven regions beyond the Roman
Empire: Sub-Saharan Africa, Arabia, Persia, South Asia, Southeast Asia, East
Asia, and Scandinavia. Each record holds an inscription, a chronicle passage, a
poem, or a find record, in its original language beside a published
translation, with a full citation and its rights position read off the source.
Prepared questions are answered from those records. Every quotation in an
answer points at the exact characters it came from, and the site checks each
one against the source file when it loads.

It is a portfolio project by Rob Padilla, built in working sessions with
Claude, Anthropic's AI assistant. It was also an experiment, and the
[Methodology tab](https://mundus-ulterior.pages.dev/) on the site reports what
worked and what did not, with the numbers.

## What was built, and what was not

The [original brief](docs/origins/AI_TECH_SHOWCASE_BRIEF.md) set out six
"pillars". Two were built in full:

- **Cross-lingual retrieval with preserved provenance** (Pillar 1). An English
  question retrieves passages in Koine Greek, Literary Chinese, Old Tamil,
  Parthian, Ge'ez, Sabaic, Proto-Norse, and other languages, through
  multilingual embeddings in Postgres with pgvector. Machine translation, with
  a back-translation confidence check, is built in. It almost never ran,
  because nearly every source already had a published English translation, and
  the site says so.
- **Groundedness, citation, and evaluation** (Pillar 6). Every quotation
  resolves to a character range in a named field of a named file. A gold set
  of prepared questions, 685 archived answers, and mutation-tested checks stand
  behind every number on the site. Each block of work committed its predictions
  before any code changed.

A **map** of the places the sources name stands in for Pillar 5, drawn from the
data rather than composed by an agent. **Not built:** the knowledge graph
(Pillar 2), multi-agent orchestration (Pillar 3), and image and handwriting
recognition (Pillar 4). **There is no live chat:** the questions are prepared,
and their answers are archived.

**The main finding** is in [`docs/BLOCK_G_RESULT.md`](docs/BLOCK_G_RESULT.md).
As the corpus grew, retrieval in English held, and retrieval in the sources'
own languages got worse. The corpus stopped at 54 records rather than the 200
planned, and the work turned to making what existed inspectable.

## Three ways in

Tested on Windows 11 with PowerShell. The first two also run as they are on
Linux. The third has been run only on Windows.

**1. Look at it. No install, no server, no keys.** Open `ui/index.html` in a
browser. The page loads one file beside it, `ui/data.js`, and works from disk
exactly as it does on the live site.

**2. Run the checks. Node and Python, no keys, no database.**

```
node ui/check_ui.mjs                # 65 checks over the page's own code and every archived answer
node ui/check_chain.mjs             # marker -> record -> quotation -> characters on disk
python ui/test_build_ui_data.py     # the data-bundle build, standard library only
```

None of these needs a package install, a key, or a network connection.

**3. Run the pipeline. Python, Docker, and two API keys.** This rebuilds the
database from the records, embeds them, and answers questions. You need:

- Python 3.11 or newer in a virtual environment, with `pip install -r requirements.txt`
- Docker, for Postgres 16 with pgvector (`docker compose up -d db`)
- an Anthropic API key and a Voyage AI API key, in `.env` (copy `.env.example`)
- the LiteLLM gateway running (`litellm --config gateway/config.yaml --port 4000`)

[`docs/origins/PHASE1_PART1_SETUP.md`](docs/origins/PHASE1_PART1_SETUP.md) walks
through the first-time setup, including the fixes it needed.
[`docs/STARTUP.md`](docs/STARTUP.md) gives the commands for a working session.
Both are written for PowerShell, and both name the Windows path the project was
built at. Use your own. Embedding the corpus and answering questions make paid
API calls.

## What is where

```
ui/          the site: index.html (the page), data.js (generated, never
             hand-edited), build_ui_data.py (builds it), and the checks
data/        seed_corpus/ (the 54 records, one JSON file each, by region),
             corpus_rights.json (every record's rights position), the
             gazetteer, the coastline, the distractor records, and data/rights/
ingest/      loading, chunking with exact character offsets, embedding, and
             corpus verification
retrieve/    vector search, reranking, and the cross-lingual checks
answer/      translation and its confidence check, answer assembly, and
             cite.py, which resolves every quotation to characters on disk
eval/        the gold set, the scorers, and the archived runs
scripts/     database schema, recovery, and mutation tests
gateway/     the LiteLLM gateway configuration
docs/        the project's working documents, indexed in docs/README.md
```

[`docs/PHASE1_README.md`](docs/PHASE1_README.md), the README as it stood in
August, has a module-by-module map of the Python code. Its counts are from that
time.

## Where to start reading

[`docs/README.md`](docs/README.md) indexes every working document by phase and
block, and says where to start. The documents were written as the work
happened: predictions before results, rulings as they were taken, and defects
written up where they were found.

The record notes shown on the site, and kept in `ui/data.js`, are the
curators' working notes. They are published as they were written, in the
project's internal vocabulary and in British spelling.

## Building on it

Section 9 of the Methodology tab sets out the directions. In short:

- **Report retrieval by language as the test runs,** so a change to the
  collection can be judged while it is made.
- **Add sources in the languages that fail,** after first stopping new English
  translations from crowding out original-language passages.
- **Set Roman and Byzantine accounts beside these,** so the same objects,
  routes, and embassies are described from both ends.
- **Extend the span** earlier, into the Republic, and later, to 1453.
- **Correct it.** Someone who reads Ge'ez, has excavated one of these sites, or
  knows which identification the field has settled on can fix what nobody here
  could check. **Issues are open for corrections.**
- **Add sources with no published translation,** so the translation checks
  finally run.
- **A live question box,** scored and presented differently from the prepared
  questions.

## License

**This repository is not under one license.** The code is under MIT. Rob
Padilla's own writing is under CC BY 4.0, except anything it quotes. The source
corpus, and everything that quotes it, carries no license from this project,
because each source's own terms govern. [`LICENSE.md`](LICENSE.md) says which
part is which, and [`DATA_RIGHTS.md`](DATA_RIGHTS.md) gives every record's
position and the terms of the third-party datasets.

Every effort has been made to verify that each source is used in line with its rights. Mundus Ulterior makes no copyright claim of its own to any of the source data it uses. If you hold rights in any of that material and have a concern about its use here, please contact Rob Padilla at rob@productofrob.com.

## Credits

The source texts belong to their authors, editors, and publishers, and each
record cites them. Places are from Pleiades and GeoNames, the coastline is from
Natural Earth, and the distractor records are from the Cleveland Museum of Art
and the Metropolitan Museum of Art, all under the terms in
[`DATA_RIGHTS.md`](DATA_RIGHTS.md). Answers were generated by Anthropic's
claude-haiku-4-5, with claude-sonnet-5 for one re-test. Embeddings are Voyage
AI's voyage-3.5, and reranking in the retrieval tests is Voyage's rerank-2.5.

## Citation and contact

To cite the project, use GitHub's "Cite this repository" button, which reads
[`CITATION.cff`](CITATION.cff). To cite a source text, cite it from its record.

For corrections, open an issue. For anything about rights, write to
rob@productofrob.com.
