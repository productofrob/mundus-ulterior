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


def iter_record_paths(corpus_dir: Path) -> Iterator[Path]:
    for path in sorted(corpus_dir.glob("*/*.json")):
        if path.name == "manifest.json":
            continue
        yield path


def build_document(record: dict[str, Any], path: Path, corpus_dir: Path) -> Document:
    raw = json.dumps(record, ensure_ascii=False, sort_keys=True)
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
        content_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
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
