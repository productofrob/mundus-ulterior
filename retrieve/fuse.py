"""C2 — one score per candidate, fused across the query's renderings.

Block C ruling 13, declared in `C2_RULINGS.md` before a single call was spent
and not chosen after seeing a result:

    score(c) = max over variants v of cosine(q_v, c)

Everything here is pure. It takes ranked hit lists and returns one ranked hit
list, so the rule that decides whether a C2 gap number means anything is
testable and mutatable without a database, a gateway or an embedding.

WHY MAX, AND WHY NOT THE OTHERS
-------------------------------
**Mean** was refused because a target in one of eight languages scores well on
one variant and poorly on seven; averaging penalises precisely the case C2
exists to fix and would make the intervention look worst where it works best.

**Best-query-wins** was refused because it needs a criterion for picking one
variant's whole ranking, and every gold-blind criterion available — top-1
similarity, score spread — is itself a retrieval decision that would need its
own baseline. It is a second intervention wearing the first one's name.

THE EXACTNESS CONDITION, AND IT IS NOT A GENERAL PROPERTY
---------------------------------------------------------
A max over truncated result lists is not a max: a chunk missing from variant
v's top-k has an unknown similarity, not a low one, and taking the max over
survivors quietly favours whatever the truncation happened to keep.

This harness is exact only because `eval.run_ranking_check.SEARCH_K is None`,
so every variant's search returns the entire filtered view and no chunk is ever
absent for a reason other than a `langs`/`roles` filter that applies to all
variants alike. `fuse` ASSERTS that condition rather than trusting it, because
the day SEARCH_K becomes a number is the day this file starts producing a
plausible number with no warning attached.

WHAT IS RECORDED, AND WHY IT IS NOT OPTIONAL
--------------------------------------------
`winning_lang` per chunk. A run in which the winner is the query's own text for
every pair is a run in which C2 did nothing — which is a result, and the header
must be able to state it rather than leaving it to be inferred from a gap that
did not move.
"""

from __future__ import annotations

from dataclasses import dataclass


class FusionError(RuntimeError):
    pass


@dataclass
class Fused:
    """The fused ranking, plus what produced it."""
    hits: list                      # one Hit per chunk, fused similarity, sorted
    winning_lang: dict              # chunk_id -> the variant language that won
    variants: list                  # the variant languages actually fused
    n_candidates: int

    def lang_of(self, chunk_id: str) -> str | None:
        return self.winning_lang.get(chunk_id)


def fuse(per_variant, search_k) -> Fused:
    """`per_variant` is [(lang, hits)], in the order the variants were declared.

    Returns one hit per chunk carrying the MAXIMUM similarity any variant gave
    it, ordered by that score. The Hit emitted for a chunk is the one the
    winning variant returned — same chunk id, same text, same document; only
    the distance differs between variants, and the winner's is the one that
    matches the score.

    Ties keep the EARLIEST variant, and the query's own text is always declared
    first (`retrieve.render.Renderings.variants_for`). So a rendering that
    merely equals the original never displaces it, and `winning_lang` reads as
    "a rendering beat the query" only where one actually did.
    """
    if search_k is not None:
        raise FusionError(
            f"fusion refuses to run at SEARCH_K={search_k}. Ruling 13's max is "
            f"exact only over untruncated result lists: a chunk missing from a "
            f"variant's top-{search_k} has an UNKNOWN similarity, not a low "
            f"one, and a max over survivors favours whatever the truncation "
            f"kept. Set SEARCH_K back to None, or replace ruling 13 with a "
            f"rule that is honest about truncation — do not fuse anyway."
        )
    if not per_variant:
        raise FusionError(
            "nothing to fuse. A pair always has at least its own query text as "
            "a variant, so an empty list means the variant builder returned "
            "nothing and the run would silently be about no query at all."
        )

    best: dict[str, tuple[float, object, str]] = {}
    for lang, hits in per_variant:
        for hit in hits:
            current = best.get(hit.chunk_id)
            # Strictly greater: a tie keeps the earlier variant, and the query's
            # own text is first.
            if current is None or hit.similarity > current[0]:
                best[hit.chunk_id] = (hit.similarity, hit, lang)

    # The winning variant's Hit is emitted UNCHANGED. Its own similarity is
    # already the fused maximum, so there is no synthetic distance to fabricate
    # and no second definition of "the score" to drift from the first. It also
    # means every field a caller reads downstream — text, lang, role, citation —
    # is the row a real search returned, not a constructed one.
    ordered = sorted(best.values(), key=lambda row: -row[0])
    return Fused(
        hits=[hit for _similarity, hit, _lang in ordered],
        winning_lang={hit.chunk_id: lang for _s, hit, lang in ordered},
        variants=[lang for lang, _hits in per_variant],
        n_candidates=len(best),
    )


def pool_problems(per_variant) -> list[str]:
    """Why these variant results may not be fused. Empty means they may.

    Every variant of one pair must have been searched under the SAME filters,
    or the max is taken over candidate sets that were never comparable — a
    `lang_pool: non_english` pair fused with one unfiltered variant would have
    English competing in five cross-lingual tests, and no rank would say so.
    This is the same assertion `retrieve.rerank.pool_problems` makes for the
    cross-encoder, made again here because fusion is a second place the pool
    can silently widen.
    """
    problems: list[str] = []
    sizes = {lang: len(hits) for lang, hits in per_variant}
    distinct = set(sizes.values())
    if len(distinct) > 1:
        problems.append(
            f"the variants returned different numbers of candidates {sizes}. "
            f"Every variant of one pair searches the same view under the same "
            f"filters, so a difference means the filters were not applied "
            f"alike and the max is over sets that were never comparable."
        )
    seen_langs = [lang for lang, _ in per_variant]
    if len(seen_langs) != len(set(seen_langs)):
        problems.append(
            f"a variant language appears twice {seen_langs}. Fusing a query "
            f"with itself is a max over two copies of one score, which changes "
            f"nothing and hides that it changed nothing."
        )
    return problems


def fusion_report(single, fused: Fused) -> dict:
    """What the fusion actually did, for the archived run.

    A step that silently changes a candidate list is the defect this repository
    has paid for three times — a view counted in one place and ranked in
    another, a canary described as invisible while it competed, and a collapse
    whose keys were dropped by an `=` that should have been `.update`. So the
    numbers are recorded rather than described.

    `moved` is how many of the top six the fusion changed. `won_by_rendering`
    is the count of top-six chunks a RENDERING claimed from the query's own
    text; if it is zero, C2 did nothing to what the user would see, whatever
    the aggregate gap says.
    """
    top = 6
    before = [h.chunk_id for h in single[:top]]
    after = [h.chunk_id for h in fused.hits[:top]]
    own = fused.variants[0] if fused.variants else None
    return {
        "variants": fused.variants,
        "candidates": fused.n_candidates,
        "top6_before": before,
        "top6_after": after,
        "moved": sum(1 for a, b in zip(before, after) if a != b),
        "entered_top6": sorted(set(after) - set(before)),
        "won_by_rendering": sum(
            1 for chunk_id in after
            if fused.winning_lang.get(chunk_id) not in (None, own)
        ),
        "won_by_lang": {
            lang: sum(1 for c in after if fused.winning_lang.get(c) == lang)
            for lang in fused.variants
        },
    }
