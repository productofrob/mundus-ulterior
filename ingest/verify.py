"""Integrity checks for the Part 3 chunking pass.

Run before trusting anything downstream:

    python -m ingest.verify

These are the invariants Parts 4-8 depend on. If any fail, the cross-lingual
test and the citation trail are unsound regardless of how good the retrieval is.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from .loader import SEED_CORPUS_DIR, load_corpus

EXPECTED_REGIONS = {
    "Arabia", "East Asia", "Persia", "Scandinavia",
    "South Asia", "Southeast Asia", "Sub-Saharan Africa",
}

MANIFEST_FLAGGED = {
    "palmyrene-tariff", "weilue", "hou-hanshu", "akananuru", "ezana-stone",
}


def run(corpus_dir: Path = SEED_CORPUS_DIR) -> int:
    result = load_corpus(corpus_dir)
    docs, chunks = result.documents, result.chunks
    failures: list[str] = []
    notes: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    # 1. Every chunk round-trips exactly to characters on disk. This is the
    #    load-bearing claim for citations in Part 7.
    raw_fields: dict[str, dict] = {}
    for path in sorted(corpus_dir.glob("*/*.json")):
        if path.name == "manifest.json":
            continue
        rec = json.loads(path.read_text(encoding="utf-8"))
        raw_fields[rec["id"]] = rec

    bad_offsets = []
    for c in chunks:
        source = str(raw_fields[c.doc_id].get(c.source_field, ""))
        if source[c.char_start:c.char_end] != c.text:
            bad_offsets.append(c.chunk_id)
    check(not bad_offsets, f"offsets do not round-trip for: {bad_offsets[:5]}")

    # 2. Provenance is never null.
    required = ("doc_id", "region", "citation", "lang", "source_field", "text_fidelity")
    missing = [
        f"{c.chunk_id}.{fname}"
        for c in chunks
        for fname in required
        if not getattr(c, fname)
    ]
    check(not missing, f"missing provenance: {missing[:5]}")

    # 3. All seven regions survived ingestion.
    regions = {c.region for c in chunks}
    check(
        regions == EXPECTED_REGIONS,
        f"region mismatch — missing {EXPECTED_REGIONS - regions}, extra {regions - EXPECTED_REGIONS}",
    )

    # 4. chunk_id uniqueness.
    dupes = [k for k, v in Counter(c.chunk_id for c in chunks).items() if v > 1]
    check(not dupes, f"duplicate chunk_ids: {dupes[:5]}")

    # 5. Original and translation are separate rows sharing a parallel_group —
    #    the precondition for the Part 5 same-query-two-languages test.
    groups: dict[str, set[str]] = defaultdict(set)
    for c in chunks:
        groups[c.parallel_group].add(c.role)
    paired = sum(1 for roles in groups.values() if roles == {"original", "translation"})
    # Find and coin records legitimately have no translation, so the expected
    # pair count is derived from the records that actually carry both fields.
    expect_pairs = sum(
        1 for rec in raw_fields.values()
        if str(rec.get("original_text_excerpt") or "").strip()
        and str(rec.get("reference_translation") or "").strip()
    )
    check(
        paired == expect_pairs,
        f"{paired} parallel original/translation pairs, expected {expect_pairs}",
    )

    # 6. No manifest-flagged record is ever presented as fully verbatim. It may
    #    be held back (pointer/paraphrase) or admitted as partial_verbatim where
    #    the original script is genuinely present — but never as clean source text.
    for hint in MANIFEST_FLAGGED:
        flagged = [
            c for c in chunks
            if hint in c.doc_id.lower() and c.role == "original"
        ]
        check(bool(flagged), f"manifest-flagged record '{hint}' not found in chunks")
        check(
            all(c.text_fidelity != "verbatim_original" for c in flagged),
            f"manifest-flagged record '{hint}' is labelled verbatim_original",
        )

    # 6b. No editorial placeholder reaches the retrieval index. If one did, an
    #     answer in Part 7 could cite the corpus editor's own note as a source.
    from .fidelity import looks_like_placeholder, looks_like_pointer

    leaked = [
        c.chunk_id for c in chunks
        if c.eligible_for_retrieval
        and (looks_like_placeholder(c.text) or looks_like_pointer(c.text))
    ]
    check(not leaked, f"placeholder text is retrieval-eligible: {leaked[:5]}")
    check(
        all(not c.eligible_for_retrieval for c in chunks if c.text_fidelity == "pointer"),
        "a chunk labelled 'pointer' is retrieval-eligible",
    )

    # 7. No chunk exceeds the size budget.
    from .chunker import DEFAULT_MAX_CHARS
    oversize = [c.chunk_id for c in chunks if c.char_count > DEFAULT_MAX_CHARS]
    check(not oversize, f"chunks over {DEFAULT_MAX_CHARS} chars: {oversize[:5]}")

    # 8. Cross-lingual capability sanity: the retrieval-eligible pool must
    #    contain genuine non-English text, or Part 5 has nothing to test.
    eligible_non_en = [c for c in chunks if c.eligible_for_retrieval and c.lang != "en"]
    check(
        len(eligible_non_en) >= 5,
        f"only {len(eligible_non_en)} retrieval-eligible non-English chunks",
    )
    langs = Counter(c.lang for c in eligible_non_en)
    notes.append(f"retrieval-eligible non-English chunks by language: {dict(langs)}")

    # 9. Docs and chunks line up.
    check(len(docs) == 24, f"expected 24 documents, got {len(docs)}")
    orphans = {c.doc_id for c in chunks} - {d.doc_id for d in docs}
    check(not orphans, f"chunks reference unknown docs: {orphans}")

    # 10. A record whose `translation_source` says the English was SUMMARIZED,
    #     while its translation chunk is classified `translation`, is a
    #     divergence between what the record declares and what the classifier
    #     concluded. Same shape as Part 3's `lang` vs `declared_lang`: the
    #     divergence is the signal, and it is a signal for review rather than a
    #     verdict.
    #
    #     It is NOT a failure, because the 2026-08-10 audit showed no mechanical
    #     rule separates the good cases from the bad. Two candidates were tried
    #     and both fired on the wrong records: "a pointer's translation is
    #     suspect" would have flagged the Ezana titulature, which is genuine, and
    #     missed the object records entirely; "summary-declared means not a
    #     translation" flags the Vimose gloss, which is a published hedged
    #     reading and a required floor case. The audit had to be done by reading
    #     24 records, and this check exists so it does not have to be done again
    #     from scratch — only for records not yet triaged.
    reviewed = {
        "scandinavia-03-vimose": (
            "KEPT. A hedged scholarly gloss of six partly undeciphered runic "
            "sequences — 'likely', 'possibly', 'remain only partially "
            "deciphered' — from the Kiel Runenprojekt. Not a running "
            "translation, but published readings presented with their "
            "uncertainty intact, which is what an answer quoting them "
            "reproduces. Excluding it would remove the only Scandinavian "
            "textual evidence in the corpus."
        ),
    }
    translation_fidelity = {
        c.doc_id for c in chunks
        if c.role == "translation" and c.text_fidelity == "translation"
    }
    untriaged = []
    for doc in docs:
        source = (getattr(doc, "translation_source", None) or "").lower()
        if "summar" not in source:
            continue
        if doc.doc_id not in translation_fidelity:
            continue          # e.g. classified object_description — honest label
        if doc.doc_id in reviewed:
            continue
        untriaged.append(doc.doc_id)
    if untriaged:
        notes.append(
            "REVIEW: translation_source declares a summary while the chunk is "
            f"classified `translation`: {untriaged}. Read the field and decide "
            "whether it renders source wording or describes it. Editorial prose "
            "in a quotable field is citable as source evidence — that is how a "
            "modern historian's judgement nearly reached a reader as Palmyrene "
            "testimony."
        )

    print(f"documents: {len(docs)}   chunks: {len(chunks)}   parallel pairs: {paired}")
    for n in notes:
        print(f"note: {n}")
    if result.warnings:
        print(f"loader warnings: {len(result.warnings)}")
        for w in result.warnings:
            print(f"  ! {w}")

    if failures:
        print(f"\nFAILED ({len(failures)})")
        for f in failures:
            print(f"  ✗ {f}")
        return 1

    print("\nAll integrity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
