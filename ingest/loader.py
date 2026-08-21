"""Read the seed corpus and turn each record into documents + chunks.

Provenance is carried forward at every step: nothing reaches the chunk table
without a doc_id, region, language, citation, date, source field and exact
character offsets attached.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterator

from .chunker import chunk_field, estimate_tokens
from .fidelity import FIND_TYPES, classify_original, classify_translation

SEED_CORPUS_DIR = Path("data/seed_corpus")
MANIFEST_NAME = "manifest.json"

# Citation keys beyond the two first-class ones; kept as jsonb so no source
# reference is ever silently dropped.
EXTRA_CITATION_KEYS = (
    "secondary_citation",
    "tertiary_citation",
    "citation_pdf",
    "museum_number",
)


@dataclass
class Document:
    doc_id: str
    region: str
    title: str
    source_type: str
    language_codes: list[str]
    language_note: str | None
    date_text: str | None
    findspot: str | None
    citation: str
    citation_original: str | None
    extra_citations: dict[str, Any]
    translation_source: str | None
    notes: str | None
    source_path: str
    content_hash: str


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    parallel_group: str
    role: str
    seq: int
    lang: str
    declared_lang: str | None
    text: str
    char_start: int
    char_end: int
    source_field: str
    text_fidelity: str
    is_pointer: bool
    eligible_for_retrieval: bool
    region: str
    source_type: str
    citation: str
    date_text: str | None
    char_count: int
    token_estimate: int


@dataclass
class IngestResult:
    documents: list[Document] = field(default_factory=list)
    chunks: list[Chunk] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _norm_langs(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw.strip()]
    return [str(x).strip() for x in raw if str(x).strip()]


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _relative_source_path(path: Path, corpus_dir: Path) -> str:
    """Stable, POSIX-style path recorded for provenance (e.g. 'persia/x.json')."""
    try:
        rel = path.resolve().relative_to(corpus_dir.resolve())
    except ValueError:
        rel = Path(path.parent.name) / path.name
    return f"data/seed_corpus/{rel.as_posix()}"


class CorpusLayoutError(Exception):
    """A JSON file under the seed corpus that the walks would not agree about."""


def iter_seed_records(corpus_dir: Path = SEED_CORPUS_DIR) -> list[Path]:
    """The single definition of what a seed record is.

    Before D1 the repository held FIVE independent walks of data/seed_corpus.
    Four of them - here, `places.load_places`, `verify.run` and
    `build_ui_data.build_places` - globbed `*/*.json`. The fifth,
    `build_ui_data.load_corpus`, used `rglob("*.json")`, so `build_ui_data.py`
    disagreed with ITSELF about the same directory, and the walk that
    disagreed is the one feeding `--verify`'s span classification.

    All five returned the same 24 records, and they did so by coincidence of
    the current layout rather than by construction. A record at
    `data/seed_corpus/a/b/c.json` is a seed record to `rglob` and invisible to
    `glob("*/*.json")`. D1 writes a corpus digest at answer time and recomputes
    it at verify time; if those two ends ever walk the corpus differently the
    digests never match again - for every answer, permanently, and in the
    direction of alarm, so everything looks changed and nothing gets read.
    Block F takes this corpus from 24 records to 60 and is the block that would
    introduce that file.

    The layout is region/record.json. A .json anywhere else under the corpus
    directory is REFUSED, not silently included and not silently skipped,
    because a file that some walks see and others do not is the exact failure
    this function exists to prevent.
    """
    records = sorted(
        p for p in corpus_dir.glob("*/*.json") if p.name != MANIFEST_NAME
    )
    seen = set(records)
    stray = sorted(
        p for p in corpus_dir.rglob("*.json")
        if p.name != MANIFEST_NAME and p not in seen
    )
    if stray:
        raise CorpusLayoutError(
            f"{len(stray)} JSON file(s) under {corpus_dir} are not at the "
            f"region/record.json depth every seed-record walk assumes: "
            f"{[str(p) for p in stray]}. Move them, or change this function - "
            f"but do not leave one walk seeing them and another not."
        )
    return records


def iter_record_paths(corpus_dir: Path) -> Iterator[Path]:
    """Kept for loader's own callers. `iter_seed_records` is the definition."""
    yield from iter_seed_records(corpus_dir)


# --------------------------------------------------------------------------
# Corpus version (D1)
# --------------------------------------------------------------------------

# Bumped only if the canonicalisation below changes. An archived digest carries
# this string so a future reader can tell "the corpus moved" from "the way we
# hash the corpus moved" - two observations that would otherwise be one.
CORPUS_DIGEST_ALGORITHM = "sha256-of-canonical-json-v1"


def canonical_record_text(record: dict[str, Any]) -> str:
    """The exact string a record's content_hash is taken over.

    Extracted from `build_document`, which computed it inline, so that the hash
    written at ingest time and the hash recomputed at verify time cannot drift
    apart. Same lesson as `iter_seed_records`: two ends of a comparison must not
    hold two definitions of the thing being compared.

    Note what this is deliberately blind to. It hashes the PARSED record with
    sorted keys, not the file's bytes, so reindenting or reordering keys in a
    seed file does not change the hash. That is correct - the content did not
    move - and it is written down here so nobody later "fixes" it into a hash of
    the raw file.
    """
    return json.dumps(record, ensure_ascii=False, sort_keys=True)


def record_content_hash(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_record_text(record).encode("utf-8")).hexdigest()


def seed_record_hashes(corpus_dir: Path = SEED_CORPUS_DIR) -> dict[str, str]:
    """Every seed record's content hash, keyed by doc_id.

    Raises on a record with no `id` and on a duplicate `id`. Both are currently
    impossible - all 24 records carry a distinct id - and both would otherwise
    be SILENT: a record without an id cannot be keyed, and a duplicate id would
    overwrite its predecessor, so in either case the digest would quietly
    describe a corpus smaller than the one on disk.
    """
    out: dict[str, str] = {}
    for path in iter_seed_records(corpus_dir):
        record = json.loads(path.read_text(encoding="utf-8"))
        doc_id = record.get("id")
        if not doc_id:
            raise CorpusLayoutError(
                f"{path} has no 'id'. A seed record with no id cannot be keyed, "
                f"and a corpus digest that silently omits it would describe a "
                f"corpus that is not the one on disk."
            )
        if doc_id in out:
            raise CorpusLayoutError(
                f"{path} repeats doc_id {doc_id!r}. One of the two would "
                f"overwrite the other and the digest would cover 23 records "
                f"while reporting 24."
            )
        out[doc_id] = record_content_hash(record)
    return out


def corpus_digest(hashes: dict[str, str]) -> str:
    """One value over the whole seed corpus.

    Answers a different question from the per-record hashes that travel beside
    it. The per-record hashes say *did the record this span quotes move?*; this
    says *is this the corpus that made this answer at all?* A corpus can move
    somewhere else entirely while every cited record is untouched, which is
    exactly the state Block E must be able to assert did NOT happen between day
    one and day three.

    Sorted by doc_id so the value depends on the corpus and not on the order a
    filesystem happened to yield it in. US (0x1f) separates the two fields
    because it cannot occur in either.
    """
    payload = "\n".join(f"{doc_id}\x1f{h}" for doc_id, h in sorted(hashes.items()))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_document(record: dict[str, Any], path: Path, corpus_dir: Path) -> Document:
    extra = {k: record[k] for k in EXTRA_CITATION_KEYS if record.get(k)}
    return Document(
        doc_id=record["id"],
        region=record["region"],
        title=record["title"],
        source_type=record.get("source_type", "unknown"),
        language_codes=_norm_langs(record.get("language_code")),
        language_note=_clean(record.get("language_note")),
        date_text=_clean(record.get("date")),
        findspot=_clean(record.get("findspot")),
        citation=record["citation"],
        citation_original=_clean(record.get("citation_original")),
        extra_citations=extra,
        translation_source=_clean(record.get("translation_source")),
        notes=_clean(record.get("notes")),
        source_path=_relative_source_path(path, corpus_dir),
        content_hash=record_content_hash(record),
    )


def build_chunks(record: dict[str, Any], doc: Document) -> tuple[list[Chunk], list[str]]:
    """Emit language-separated chunks for one record.

    Original-language text and its translation become separate chunks sharing a
    `parallel_group`, which is what makes the Part 5 cross-lingual test possible:
    a query can retrieve the Greek without the English coming along for free.
    """
    chunks: list[Chunk] = []
    warnings: list[str] = []
    declared = doc.language_codes[0] if doc.language_codes else None

    plan = [
        ("original", "original_text_excerpt"),
        ("translation", "reference_translation"),
    ]

    for role, source_field in plan:
        source_text = record.get(source_field)
        if not source_text or not str(source_text).strip():
            # Find and coin records have no translation because they have no
            # source-language text to translate — expected, not a defect.
            if not (role == "translation" and doc.source_type in FIND_TYPES):
                warnings.append(
                    f"{doc.doc_id}: empty {source_field}, no {role} chunk emitted"
                )
            continue
        source_text = str(source_text)

        spans = chunk_field(source_text)
        for seq, span in enumerate(spans):
            text = span.text_of(source_text)

            if role == "original":
                fidelity, lang, eligible = classify_original(
                    text, doc.doc_id, doc.language_codes, doc.source_type
                )
            else:
                fidelity, lang, eligible = classify_translation(text, doc.source_type)

            # Parallel grouping is at DOCUMENT level, deliberately. An earlier
            # version grouped by span index so passage N of the original would
            # line up with passage N of the translation — but that only holds
            # when both sides split into the same number of pieces, which is
            # not true in general (the Greek Periplus §4-6 splits into three
            # chunks; its English summary is one). Claiming passage alignment
            # we don't have would be false precision, and it silently broke the
            # original↔translation link for exactly the records that matter.
            # Sentence-level cross-lingual alignment is a Part 6 problem.
            parallel_group = doc.doc_id

            chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}::{role}::{seq:03d}",
                    doc_id=doc.doc_id,
                    parallel_group=parallel_group,
                    role=role,
                    seq=seq,
                    lang=lang,
                    declared_lang=declared if role == "original" else "en",
                    text=text,
                    char_start=span.start,
                    char_end=span.end,
                    source_field=source_field,
                    text_fidelity=fidelity,
                    is_pointer=(fidelity == "pointer"),
                    eligible_for_retrieval=eligible,
                    region=doc.region,
                    source_type=doc.source_type,
                    citation=doc.citation,
                    date_text=doc.date_text,
                    char_count=len(text),
                    token_estimate=estimate_tokens(text),
                )
            )

    if not chunks:
        warnings.append(f"{doc.doc_id}: produced NO chunks")
    return chunks, warnings


def load_corpus(corpus_dir: Path = SEED_CORPUS_DIR) -> IngestResult:
    result = IngestResult()
    seen: set[str] = set()

    for path in iter_record_paths(corpus_dir):
        record = json.loads(path.read_text(encoding="utf-8"))
        doc = build_document(record, path, corpus_dir)

        if doc.doc_id in seen:
            result.warnings.append(f"duplicate doc_id {doc.doc_id} at {path}")
            continue
        seen.add(doc.doc_id)

        doc_chunks, warns = build_chunks(record, doc)
        result.documents.append(doc)
        result.chunks.extend(doc_chunks)
        result.warnings.extend(warns)

    return result


def to_jsonable(result: IngestResult) -> dict[str, Any]:
    return {
        "documents": [asdict(d) for d in result.documents],
        "chunks": [asdict(c) for c in result.chunks],
        "warnings": result.warnings,
    }
