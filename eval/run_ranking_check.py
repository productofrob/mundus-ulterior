"""W2a — the retrieval ranking baseline (PHASE2_PLAN.md Block B2).

Reports, per pair and in aggregate:

  recall@6    is the known-good passage in the top 6
  MRR@10      1/rank, 0 if it is not in the top 10
  score gap   known-good similarity minus the highest-ranked irrelevant one

The gap, not the raw similarity, is what predicts survival at scale, so it is
computed two ways and both are printed: against the best passage from any OTHER
document, and against the best other passage of ANY kind including siblings of
the same document. A sibling outranking the target is not the same failure as a
Scandinavian find outranking it, and one number cannot say which happened.

`top1_to_rank6` is also reported because it is the one quantity comparable to
Phase 1's recorded number (mean spread 0.105; 0.045–0.094 on the questions that
matter). Everything else here is new and has nothing to be compared against yet
— which is the point of recording it before anything is tuned.

Since Block C the run reports at TWO depths, and never one in place of the other:

  per pair    the original metric, unchanged. `rank`, both gaps and the cohort
              table mean exactly what they meant when the B2 baseline was
              recorded, so every run since is comparable to every other.
  per unit    Block C ruling 1. A query with several acceptable targets is one
              scored unit on its best target, with COVERAGE — how many of its
              targets reached the top 6 — beside it. G2's recall criterion reads
              this table. Coverage is reported and never gated, because the
              ruling reaches the gate partly by no longer counting the two
              hardest Muziris targets, and a gate that passes while a known
              failure goes uncounted is honest only if the failure is printed.

Ruling 2 sits inside the per-pair row rather than replacing it: a declaring pair
also accepts its document's own published translation of the same section, in
`rank_accepted`, while `rank` is left alone. Rewriting `rank` would have
restated every number Block B recorded as though the ruling had always been in
force.

Three things this file refuses to do, each for a reason the repository has
already paid for:

1. **It will not run against a stale index.** The gold set names passages by
   their characters; if the index does not hold those characters, every number
   is about a corpus that no longer exists. `--check` is the precondition and it
   is on by default.
2. **It resolves the known-good passage from the index, not from disk.** The
   metric is a claim about what retrieval can reach. Resolving the target from
   the seed files would let the check pass while the index held something else.
3. **It never writes `_last_run.json`.** A one-case run once replaced a
   nine-case baseline and calibration was done from it. Runs are archived under
   `eval/ranking_runs/<timestamp>.json` and nothing overwrites anything.

Block C3 adds a cross-encoder stage, and it is added the same way: BESIDE.
`--rerank` reorders the top `--rerank-window` candidates and records the result
in `rank_reranked` / `rank_accepted_reranked`, leaving `rank`, `rank_accepted`
and every gap exactly as they were. Ruling 3 is the reason the gaps do not move:
G2's gap criterion is denominated in embedding similarities, which reranking
does not alter. A reranker-score gap is recorded under `rerank_gap_*` and is
never compared to the baseline number. **C3 is a recall intervention only.**

Usage:
    python -m eval.run_ranking_check                 # baseline, 57-chunk index
    python -m eval.run_ranking_check --with-distractors   # B5, elevated N
    python -m eval.run_ranking_check --dry-run       # load + resolve, no spend
    python -m eval.run_ranking_check --with-distractors --rerank   # C3
    python -m eval.run_ranking_check --with-distractors --collapse --rerank --fuse
                                                     # C2: both arms, ruling 14
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# FINDING 10: this process's own stdout. On Windows `print` writes through a
# stream whose encoding comes from the console code page, and through a PIPE or
# a REDIRECT it falls back to the locale codec — cp1252, which cannot encode
# Greek, Tamil, Chinese, Ge'ez or runic. It does not degrade: it raises
# UnicodeEncodeError mid-output, with the file half written and every number in
# it correct. Found 2026-08-22 at build_ui_data.py:730, printing the Greek behind
# a `case_only` span into a redirect.
#
# Two neighbouring boundaries were already guarded and are NOT this one: a CHILD
# process's stdout (PYTHONIOENCODING in its env) and a PARENT decoding that child
# (subprocess encoding=). Both are about a pipe between two processes. This is
# about where THIS process is writing, and until 2026-08-22 nothing anywhere
# guarded it.
#
# errors="replace" is deliberate. A harness that cannot encode one character
# should print a replacement character and finish; it should never lose a run to
# a formatting problem. A mangled character is cosmetic. A three-day sweep that
# dies on day one is ninety chat calls.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

RUNS_DIR = Path(__file__).parent / "ranking_runs"
# C2. Named here rather than at the call site, for the same reason the two view
# names are: "which renderings was this measured against" should be one grep and
# should appear in the archived run.
_DEFAULT_RENDERINGS = Path(__file__).parent / "gold" / "query_renderings.json"

# The two views, named here rather than interpolated at the call site so that
# "which index was this measured against" is one grep and appears in the
# archived run.
# The pair the coverage prose points at: the corpus's one genuinely broken
# cross-lingual link. Named here rather than written into the sentence, so the
# sentence can DERIVE its rank instead of stating one. FINDING 43.
BROKEN_CROSSLINGUAL_PAIR = "muziris-cargo-akananuru"


VIEW_BASELINE = "retrievable_chunks"
VIEW_WITH_DISTRACTORS = "retrievable_chunks_with_distractors"

# Words too common to say anything about whether a query reused its target's
# wording. Deliberately short: the measure is a reported property, not a gate,
# and a long list would make it look more precise than it is.
_OVERLAP_STOPWORDS = frozenset("""
the a an of and or in on at to from for with by is are was were be been that
this these those there it its as into not no than then when where which who
whom whose how what did do does made make new one two
""".split())


def query_target_overlap(query: str, text: str) -> float | None:
    """Share of a query's content words that appear verbatim in its target.

    NOT a quality gate, and not a thing to minimise. For a 300-character English
    object description a faithful, unambiguous question necessarily shares
    vocabulary with the passage that answers it, and pushing this toward zero
    buys either contrived questions or ambiguous ones — and an ambiguous pair
    scores CORRECT retrieval as a failure, which is the worse defect. It is
    recorded so that a high recall on the English-target pairs can be read with
    the reason beside it. Meaningless across a language boundary, where it is
    zero by construction rather than by discipline.
    """
    import re

    def content(t: str) -> set:
        return {w for w in re.findall(r"[a-z]+", t.lower())
                if w not in _OVERLAP_STOPWORDS and len(w) > 3}

    q = content(query)
    if not q:
        return None
    return len(q & content(text)) / len(q)


RECALL_AT = 6
MRR_AT = 10
# There is no fixed k. Every pair is ranked against the WHOLE view.
#
# A fixed depth cannot be right at more than one rung of the W2b curve. k=20 was
# too shallow at 57 chunks and biased the gap means over 26 of 32 pairs; k=50 was
# right at 57 and would have been too shallow at 450, where the three deepest
# targets project to ranks ~229, ~324 and ~395 and would have contributed no gap
# at all. An unbiased endpoint compared against a biased one is not a curve.
#
# recall@6, MRR@10 and top1_to_rank6 are invariant to depth; only the gaps are
# not, because a pair with no rank has no similarity. Ranking everything removes
# the choice rather than tuning it, and 450 ordered rows per pair is nothing.
SEARCH_K = None  # None means "the whole view"; see _search_depth()


@dataclass
class UnitResult:
    """One query, scored once, under Block C ruling 1.

    `recall_at_6` is the unit's own — its best acceptable target in the top 6.
    `coverage` is how many of its targets got there, reported and NEVER gated:
    the ruling reaches G2 partly by no longer counting the two hardest Muziris
    targets, and a gate that passes while a known failure goes uncounted is only
    honest if the failure is printed beside it. Coverage is that printing.
    """
    unit: str
    query: str
    pairs: list[str]
    best_rank: int | None
    recall_at_6: bool
    rr_at_10: float
    coverage_n: int
    coverage_total: int
    coverage: float
    best_pair: str | None = None
    # Block C3. Same three quantities, computed on the post-rerank ordering.
    # `recall_at_6_reranked` is what G2's recall criterion reads once a run is
    # reranked; `recall_at_6` above stays the pre-rerank number so the two are
    # printed side by side and the intervention's effect is visible rather than
    # substituted.
    collapsed: bool = False
    best_rank_collapsed: int | None = None
    recall_at_6_collapsed: bool = False
    rr_at_10_collapsed: float = 0.0
    coverage_n_collapsed: int = 0
    recall_at_6_via_original: bool = False
    reranked: bool = False
    best_rank_reranked: int | None = None
    recall_at_6_reranked: bool = False
    rr_at_10_reranked: float = 0.0
    coverage_n_reranked: int = 0
    # C7. Beside `recall_at_6_via_original` above, never over it.
    recall_at_6_via_original_reranked: bool = False
    coverage_reranked: float | None = None
    best_pair_reranked: str | None = None


@dataclass
class PairResult:
    id: str
    provenance: str
    region: str
    query_lang: str
    expect_lang: str | None
    expect_doc: str
    resolved_chunk_id: str | None
    rank: int | None
    recall_at_6: bool
    rr_at_10: float
    sim_target: float | None
    sim_best_other_doc: float | None
    sim_best_other_chunk: float | None
    gap_vs_other_doc: float | None
    gap_vs_other_chunk: float | None
    top1_to_rank6: float | None
    top_doc: str | None
    query_target_overlap: float | None = None
    # WHICH chunk each of the two "best other" similarities belongs to. Added
    # 2026-08-14 (Block C) because the run recorded the number and not the thing
    # it was measured against, so the most consequential claim about `gapAny` —
    # that the chunk beating a `translation_case` target is always that
    # document's own English translation — was recoverable from neither archived
    # run. It had to be re-derived by hand, and could afterwards only be
    # recalled, not checked.
    #
    # A chunk id carries its own role (`::original::` / `::translation::`) and
    # its own document, so these two strings settle that question offline for
    # every run made from here on, at the cost of two strings per pair.
    best_other_doc_chunk_id: str | None = None
    best_other_chunk_id: str | None = None
    # ------------------------------------------------------------------
    # Block C. Everything above keeps the meaning it had when the B2 baseline
    # was recorded — `rank` is still the rank of the ONE chunk this pair's
    # characters resolve to, and `recall_at_6` is still computed from it. The
    # post-ruling numbers are recorded BESIDE them rather than in place of
    # them, so every run since B2 stays comparable to every other and the
    # ruling can be re-argued against the same archive.
    # ------------------------------------------------------------------
    unit: str = ""
    # Ruling 2: the target, plus its document's own published translation of the
    # same section where the pair declares that alternate and align.py reports
    # the ground as "section". The ground is recorded even when no alternate was
    # admitted, because "none was admitted" and "none was asked for" are
    # different facts about a run.
    accepted_chunk_ids: list[str] = field(default_factory=list)
    alternate_ground: str | None = None
    rank_accepted: int | None = None
    recall_at_6_accepted: bool = False
    # Mechanical, rank-blind diagnostics. Neither is a judgement about the query
    # and neither is a gate; they exist so a later run can test an explanation
    # for a miss instead of asserting one. See the 2026-08-14 correction in
    # PROGRESS.md for why a hand-assigned broad/specific label was NOT added.
    anchor_doc: str | None = None
    anchor_points_home: bool | None = None
    shared_query: bool = False
    observed_chunk_id: str | None = None
    observed_chunk_still_exists: bool | None = None
    observed_chunk_matches_resolved: bool | None = None
    # RULING 54, F4. Carried onto the RESULT and not only held in the gold file,
    # because the exclusion has to survive into the archive: a run read six
    # months from now has the JSON and not the reasoning, and "these pairs may
    # not be cited in a before/after claim" is a property of the measurement,
    # not of the file it was loaded from.
    written_after_the_records_entered_the_index: bool = False
    # ------------------------------------------------------------------
    # Block C3 — the cross-encoder, recorded beside everything above and never
    # over it. `rank` and `rank_accepted` keep their meaning, so a reranked run
    # and every run since B2 remain the same measurement plus one more column.
    # ------------------------------------------------------------------
    # Ruling 8 (C2a). Sits beside `rank` for the same reason `rank_accepted`
    # and `rank_reranked` do: collapsing changes what retrieval RETURNS, and
    # every gap and the B2-comparable aggregate stay denominated in the
    # uncollapsed ranking they were recorded against.
    collapsed: bool = False
    # Which member of the target's section got there first. "translation" means
    # the record was reached on the strength of its ENGLISH, and the original is
    # reported as found because its translation was. Reported, never gated —
    # the same standing as ruling 1's coverage, and for the same reason.
    collapse_entry_role: str | None = None
    # Ruling 11. Which text IS this record, derived from `source_type` via
    # `ingest.fidelity.FIND_TYPES`. It decides both which chunk the collapse
    # emits and whether reaching the record through English was a shortcut past
    # a source text or simply the record being read.
    collapse_primary_role: str | None = None
    rank_collapsed: int | None = None
    recall_at_6_collapsed: bool = False
    rank_accepted_collapsed: int | None = None
    recall_at_6_accepted_collapsed: bool = False
    # Ruling 9's mandatory companion. True only when the record was reached
    # through its ORIGINAL. No translation-mediated intervention can inflate it:
    # not ruling 2's alternates, not the collapse, not `sole`, not a reranker
    # preferring English. It is defined on the COLLAPSED ordering, because the
    # entry role is a fact about how retrieval reached the record and reranking
    # only reorders what retrieval already found.
    recall_at_6_via_original: bool = False
    reranked: bool = False
    rerank_window: int | None = None
    # Strict analogue of `rank`: where the resolved target ended up.
    rank_reranked: int | None = None
    recall_at_6_reranked: bool = False
    # Ruling 2's analogue: the best of the accepted chunks. This is what the
    # unit table reads, so ruling 2 and C3 compose rather than each being
    # applied at a different depth.
    rank_accepted_reranked: int | None = None
    recall_at_6_accepted_reranked: bool = False
    # C7. The post-rerank companion to `recall_at_6_via_original` above, under
    # its OWN name and never over it, exactly as `rank_reranked` sits beside
    # `rank`. Every archived run holds the pre-rerank figure; overwriting it
    # would make the archive incomparable to itself.
    #
    # It is the SAME predicate — only the recall column moves. That is sound
    # because the collapse runs BEFORE the rerank and emits one row per
    # section, so `collapse_entry_role` is fixed at collapse time and there is
    # exactly one member of each section left for the reranker to reorder. The
    # reranker can rescue a record into the top 6; it cannot change which
    # member of that record's section retrieval reached first. No new
    # entry-role computation belongs in `apply_rerank`.
    recall_at_6_via_original_reranked: bool = False
    # Ruling 3: reranker scores live under their own names and are NEVER
    # compared to `gap_vs_*` above, which are embedding similarities. Two
    # different quantities agreeing on a sign would not make them comparable.
    rerank_score_target: float | None = None
    rerank_score_best_other_doc: float | None = None
    rerank_score_best_other_chunk: float | None = None
    rerank_gap_vs_other_doc: float | None = None
    rerank_gap_vs_other_chunk: float | None = None
    # WHAT the cross-encoder promoted above the target. Added 2026-08-16, in the
    # same session and for the same reason as `best_other_chunk_id` in ruling 2:
    # the first C3 run recorded that three units fell out of the top 6 and NOT
    # what displaced them, so "the reranker preferred a different passage" and
    # "the reranker preferred a wrong passage" were indistinguishable without
    # another twenty-six minutes of paced calls. A chunk id carries its own role
    # and document, so this settles it offline for every run from here on.
    rerank_top_chunk_ids: list[str] = field(default_factory=list)
    rerank_beaten_by: list[str] = field(default_factory=list)
    # ------------------------------------------------------------------
    # C2 — ruling 13. A fused row is a SEPARATE PairResult in
    # `Report.pairs_fused`, not extra columns on this one, because ruling 14
    # requires the two arms side by side and an arm is a whole measurement:
    # its own rank, its own gaps, its own collapse and its own rerank. The
    # fields below say which arm a row belongs to and what produced it.
    # ------------------------------------------------------------------
    fused: bool = False
    # The variant languages fused for this pair, in declaration order. The
    # query's own language is always first.
    fused_variants: list[str] = field(default_factory=list)
    # Which variant produced the TARGET's score. If this is the query's own
    # language for every pair, C2 did nothing — a result, and one the header
    # has to be able to state rather than leave to be inferred from a gap that
    # did not move.
    fused_from_lang: str | None = None
    # Ruling 15b's control, per pair. Empty for an English query. A violation
    # is a FINDING printed beside the number, never a gate.
    native_control_problems: list[str] = field(default_factory=list)
    note: str = ""


@dataclass
class Report:
    timestamp: str
    view: str
    search_k: int
    index_chunks: int
    embedding_models: list[str]
    query_embedding_model: str
    pairs: list[PairResult] = field(default_factory=list)
    aggregate: dict = field(default_factory=dict)
    by_cohort: dict = field(default_factory=dict)
    # Block C. `aggregate` above is per pair and comparable to B2; this is per
    # unit and is what G2's recall criterion reads.
    units: list[UnitResult] = field(default_factory=list)
    aggregate_units: dict = field(default_factory=dict)
    unresolvable: list[dict] = field(default_factory=list)
    # FINDING 12. Every id here was named on the command line by a person who
    # knew the pair would not resolve. An empty list is the only state in which
    # this run's aggregates share a denominator with the runs before it.
    allowed_unresolvable: list[str] = field(default_factory=list)
    chunk_id_drift: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    # Block C3. The window is a PARAMETER: a different window is a different
    # measurement, not a better one, so it is archived with the numbers it
    # produced. The route is recorded because LiteLLM has exposed rerank at more
    # than one path and which one answered is an observation, not a citation.
    collapsed: bool = False
    collapse_sections: int = 0
    collapse_stats: dict = field(default_factory=dict)
    reranked: bool = False
    rerank_model: str | None = None
    rerank_window: int | None = None
    rerank_route: str | None = None
    rerank_requests: int = 0
    rerank_tokens: int | None = None
    # Seconds left between rerank calls. Archived because a run that was paced
    # and one that was not are the same measurement made under different account
    # limits, and the only way to show that is to record which was which.
    rerank_pace_seconds: float = 0.0
    rerank_tpm_budget: float = 0.0
    rerank_seconds_waiting: float = 0.0
    # ------------------------------------------------------------------
    # C2 — rulings 13/14/19. `pairs` above stays the SINGLE-VARIANT arm and
    # keeps every meaning it has had since B2, so a fused run is still
    # comparable to every run before it. The fused arm lives here.
    # ------------------------------------------------------------------
    fused: bool = False
    renderings_path: str | None = None
    # Ruling 19. Two runs on different days are the same configuration only if
    # this string is the same in both.
    renderings_digest: str | None = None
    # Ruling 24. Rows whose verdict on disk disagreed with the guard that read
    # them. The digest says the bytes are the same; this says whether the rules
    # that judged them are.
    renderings_stale: list = field(default_factory=list)
    fused_variant_langs: list[str] = field(default_factory=list)
    fusion_stats: dict = field(default_factory=dict)
    pairs_fused: list[PairResult] = field(default_factory=list)
    aggregate_fused: dict = field(default_factory=dict)
    by_cohort_fused: dict = field(default_factory=dict)
    units_fused: list[UnitResult] = field(default_factory=list)
    aggregate_units_fused: dict = field(default_factory=dict)
    # Ruling 15b, collected across pairs so the control is one line rather than
    # something the reader has to assemble from a table.
    native_control: list = field(default_factory=list)


# --------------------------------------------------------------------------
# Preconditions
# --------------------------------------------------------------------------

def _RR_WINDOW_DEFAULT() -> int:
    from retrieve.rerank import DEFAULT_WINDOW

    return DEFAULT_WINDOW


def _search_depth(n_index: int) -> int:
    """How deep to rank. SEARCH_K is None, so: everything in the view."""
    return n_index if SEARCH_K is None else SEARCH_K


def index_state(conn, view: str) -> tuple[int, list[str]]:
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM {view};")
        n = int(cur.fetchone()[0])
        cur.execute(
            f"SELECT DISTINCT embedding_model FROM {view} "
            f"WHERE embedding_model IS NOT NULL ORDER BY 1;"
        )
        models = [r[0] for r in cur.fetchall()]
    return n, models


def corpus_on_disk() -> tuple[int, int]:
    """(chunks, eligible) as the seed files would produce them today."""
    from ingest.loader import load_corpus

    result = load_corpus()
    eligible = sum(1 for c in result.chunks if c.eligible_for_retrieval)
    return len(result.chunks), eligible


def broken_link_phrase(pairs, view: str) -> str:
    """Where the corpus's one broken cross-lingual link sits IN THIS RUN.

    FINDING 43, F3, fixed in F4. The coverage prose beneath the unit table
    stated one rank as a string literal: the same number under every view,
    under every corpus, and under whatever the table above it happened to say.
    It disagreed with its own table in the with-distractors view and with the
    baseline table twenty minutes later -- three numbers, one sentence, and no
    check able to compare them. The numbers are in FINDING 43, which is where
    an incident belongs; this docstring states the rule.

    `reachability_problems` above records the same confusion at the level of
    data -- a count taken from one surface printed over ranks taken from
    another -- and the resolution then was to make the view explicit. The PROSE
    was not brought along, because prose is where no check could reach it.

    So the rank is derived from the run's own pairs and the phrase names the
    view it was measured in, which is the thing that makes a sentence safe to
    quote in a document beside a different run. Pure, so it can be tested and
    mutated without a database, and `eval/test_ranking_check.py` additionally
    refuses a literal rank in any string in this module.
    """
    rank = next((p.rank for p in pairs if p.id == BROKEN_CROSSLINGUAL_PAIR), None)
    if rank is None:
        return ("not among this run's pairs, so this report states no rank "
                "for it")
    return f"at rank {rank} in {view}"


def reachability_problems(view: str, n_index: int, n_hits: int) -> list[str]:
    """Did the ranking actually reach the view the header names?

    An unfiltered query ranked to depth N against a view of N rows comes back
    with N rows. Anything less means the search read a different — smaller —
    surface than the one counted, which is precisely the 2026-08-14 defect:
    `index_state()` counted `retrievable_chunks_with_distractors` and reported
    450, `search()` hardcoded `retrievable_chunks` and ranked 57, and both
    counts were individually correct. The run printed `index=450 depth=450` over
    a table of 57-chunk ranks, and the only reason B5's curve was ever
    measurable is that containment happened to be broken at the time.

    Pure, so it can be tested and mutated without a database. The half that
    needs one is `check_search_reaches_the_view` below.
    """
    if n_hits == n_index:
        return []
    return [
        f"the ranking cannot reach {view}: it holds {n_index} rows and an "
        f"unfiltered search to depth {n_index} returned {n_hits}. The count and "
        f"the ranking are coming from different surfaces, so every rank in this "
        f"run would be about an index that is not the one named in its header. "
        f"Check that retrieve.search.search() is being passed view={view!r}."
    ]


def check_search_reaches_the_view(conn, view: str, n_index: int) -> list[str]:
    """Run the invariant above for real, before a single query is embedded.

    Borrows a vector the view already holds, so this costs one row and no API
    call. It runs before the batch deliberately: a run that cannot measure what
    it claims should fail while it is still free.
    """
    from retrieve.search import sample_vector, search

    vector = sample_vector(conn, view)
    if vector is None:
        return [f"{view} holds no embedding to probe with"]
    hits = search(conn, vector, k=_search_depth(n_index), view=view)
    return reachability_problems(view, n_index, len(hits))


def check_index_is_current(conn, view: str) -> list[str]:
    """Loud, specific complaints. Empty list means the index is usable.

    W2b's whole curve is denominated in chunk counts, and PHASE2_PLAN.md's first
    action is 'a baseline recorded against an uncertain denominator is not a
    baseline'. That action recorded 54 on 2026-08-12; the true count is 57, and
    has been since A4's Greek recovery re-chunked africa-03-periplus-adulis the
    next day. A4 re-embedded the twelve chunks it invalidated and the index has
    been current ever since — which is the point. That was a thing someone
    remembered to do. This makes it a thing that cannot be forgotten, and it
    reads the count from disk rather than from any document, because both
    PHASE2_PLAN.md and PROGRESS.md still say 54 on the page.
    """
    problems: list[str] = []
    n_index, models = index_state(conn, view)
    _, eligible = corpus_on_disk()

    if view == VIEW_BASELINE and n_index != eligible:
        problems.append(
            f"the index holds {n_index} retrievable chunks; the seed corpus on "
            f"disk would produce {eligible}. Re-run `python -m ingest.run_ingest` "
            f"then `python -m ingest.run_embed` before recording a baseline — "
            f"the pairs name passages by their characters, and characters that "
            f"are not in the index cannot be ranked."
        )
    if len(models) > 1:
        problems.append(
            f"the index holds vectors from {len(models)} models {models}. "
            f"Similarities from different embedding spaces are not comparable, "
            f"so an aggregate over them means nothing."
        )
    if not models:
        problems.append(f"no chunk in {view} records an embedding_model.")
    return problems


# --------------------------------------------------------------------------
# Resolving the known-good passage — from the index
# --------------------------------------------------------------------------

def resolve_targets(conn, pairs, view: str) -> tuple[dict, list[dict]]:
    """pair.id -> (chunk_id, text), plus the pairs that could not be resolved.

    Exactly one chunk must contain the substring. Zero means the index does not
    hold the passage. More than one means the pair does not identify a passage,
    and a 'recall' over an ambiguous target is a number about nothing.
    """
    resolved: dict[str, tuple[str, str]] = {}
    unresolvable: list[dict] = []
    with conn.cursor() as cur:
        for p in pairs:
            cur.execute(
                f"SELECT chunk_id, doc_id, lang, text FROM {view} "
                f"WHERE position(%(needle)s in text) > 0 ORDER BY chunk_id;",
                {"needle": p.expect_text_contains},
            )
            rows = cur.fetchall()
            if len(rows) != 1:
                unresolvable.append({
                    "id": p.id,
                    "reason": ("the index holds no chunk containing this pair's "
                               "characters" if not rows else
                               f"{len(rows)} chunks contain them, so the pair "
                               f"does not identify a passage"),
                    "chunks": [r[0] for r in rows],
                })
                continue
            chunk_id, doc_id, lang, text = rows[0]
            if doc_id != p.expect_doc:
                unresolvable.append({
                    "id": p.id,
                    "reason": (f"characters resolve to {doc_id}, but the pair "
                               f"expects {p.expect_doc}"),
                    "chunks": [chunk_id],
                })
                continue
            if p.expect_lang and lang != p.expect_lang:
                unresolvable.append({
                    "id": p.id,
                    "reason": (f"characters resolve to a chunk in '{lang}', but "
                               f"the pair expects '{p.expect_lang}'"),
                    "chunks": [chunk_id],
                })
                continue
            resolved[p.id] = (chunk_id, text)
    return resolved, unresolvable


# --------------------------------------------------------------------------
# FINDING 12 — the denominator is a fact about the gold file
# --------------------------------------------------------------------------

def unresolved_pair_problem(pairs, resolved: dict, unresolvable: list[dict],
                            allowed: set[str]) -> str | None:
    """The message this run must die on, or None if every pair is accounted for.

    Pure — no database, no index — so `eval/test_ranking_check.py` exercises it
    offline and `scripts/mutate_ranking.py` can break it.

    FINDING 12, 2026-08-22. Both Weilue ranking pairs asserted the FABRICATED
    characters the record used to hold. When the record was corrected the
    assertions matched nothing, both pairs left the run, and the harness said
    only:

        "31 pairs, 29 distinct query text(s) embedded in 1 request(s)"

    A count line. Every headline number then moved because the DENOMINATOR had
    shrunk — recall@6 via original, reranked, read `22/30 -> 21/29`, which
    reads like a small regression and is a measurement that lost a pair. The
    `unresolvable` list was archived correctly and the NOT MEASURED block WAS
    printed — thirty lines below the aggregates, after the exit code was
    already zero. **Recording a fault under a heading nobody reaches is not a
    guard.** `eval/ranking_runs/20260822T160349…json` is committed deliberately
    as the exhibit of what that looks like from the inside.

    Two rules, and the second matters as much as the first:

    * a pair that does not resolve and is NOT named in `--allow-unresolvable`
      kills the run — before the batched embedding request and before the
      twenty-six-minute rerank, because a measurement that cannot be compared
      should not be paid for;
    * an allowance naming a pair that DOES resolve also kills the run. A stale
      allowance is a standing permission for the next pair to vanish quietly,
      which is this very defect wearing the uniform of the fix.

    The denominator is read from the loaded pairs, never from `unresolvable`.
    A pair that fell out for a reason `resolve_targets` never classified would
    otherwise be missing from both lists at once.
    """
    missing = [p.id for p in pairs if p.id not in resolved]
    why = {u["id"]: u["reason"] for u in unresolvable}

    unnamed = [pair_id for pair_id in missing if pair_id not in allowed]
    stale = sorted(allowed - set(missing))
    if not unnamed and not stale:
        return None

    lines: list[str] = []
    if unnamed:
        lines.append(
            f"{len(unnamed)} of {len(pairs)} gold pair(s) did not resolve and "
            f"were not named in --allow-unresolvable. Every aggregate this run "
            f"would print is computed over a denominator that silently shrank:"
        )
        for pair_id in unnamed:
            lines.append(f"  {pair_id}: {why.get(pair_id, 'did not resolve')}")
    if stale:
        lines.append(
            "--allow-unresolvable names pair(s) that resolve perfectly well: "
            + ", ".join(stale)
            + ". An allowance nobody removed is a standing permission for the "
              "next pair to disappear without a word."
        )
    lines.append(
        "The pair count is a fact about eval/gold/ranking_pairs.json and not "
        "about what happened to resolve today. Fix the pair, or retire it from "
        "the gold file, or name it — and a run carrying any allowance is "
        "archived as NOT COMPARABLE to one that carries none."
    )
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Block C ruling 2 — the accepted alternate, computed and never copied
# --------------------------------------------------------------------------

@dataclass
class _AlignRow:
    """The minimum `answer.align` needs, and deliberately no offsets.

    `align.has_offsets` decides between exact character arithmetic and a plain
    join, and a chunk type that lies about having offsets is the A4 defect that
    cost a day. Nothing here needs a span — only which chunk ids belong to which
    section — so this type honestly has none and `_merge` takes the safe branch.
    """
    chunk_id: str
    text: str


def resolve_alternates(conn, pairs, view: str, resolved: dict) -> dict:
    """pair.id -> (accepted alternate chunk ids, alignment ground).

    Ruling 2: a declaring pair also accepts its document's own published
    translation OF THE SAME SECTION. Computed here from `answer.align`, which
    already owns "same section", rather than written into the gold file — a
    hand-copied alternate is a second copy of a passage that drifts from the
    record it came from, which is the chunk-id failure wearing a different hat.

    Admitted ONLY where align reports the ground as "section". Where both sides
    merely split into the same number of pieces (`index`), the pairing is a
    coincidence of counting and admitting an alternate on it would accept a
    neighbouring section — the exact thing the ruling says is still a miss.
    """
    from answer.align import pair_chunks

    out: dict[str, tuple[list[str], str | None]] = {}
    wanted = [p for p in pairs
              if getattr(p, "accept_aligned_translation", False)
              and p.id in resolved]
    if not wanted:
        return out

    docs = sorted({p.expect_doc for p in wanted})
    rows_by_doc: dict[str, list[tuple[str, str, str]]] = {}
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT doc_id, chunk_id, role, text FROM {view} "
            f"WHERE doc_id = ANY(%(docs)s::text[]) "
            f"ORDER BY doc_id, role, char_start, chunk_id;",
            {"docs": docs},
        )
        for doc_id, chunk_id, role, text in cur.fetchall():
            rows_by_doc.setdefault(doc_id, []).append((chunk_id, role, text))

    for p in wanted:
        rows = rows_by_doc.get(p.expect_doc, [])
        originals = [_AlignRow(c, t) for c, r, t in rows if r == "original"]
        translations = [_AlignRow(c, t) for c, r, t in rows if r == "translation"]
        target_id, _ = resolved[p.id]
        ground: str | None = None
        alternates: list[str] = []
        for aligned in pair_chunks(originals, translations):
            if aligned.original.chunk_id != target_id:
                continue
            ground = aligned.ground
            if aligned.ground == "section":
                alternates = [m.chunk_id for m in aligned.members]
            break
        out[p.id] = (alternates, ground)
    return out


def resolve_sections(conn, view: str) -> list:
    """[(canonical chunk id, [member ids], ground)] for every document. Ruling 8.

    Built from `answer.align.pair_chunks`, the same module ruling 2 uses, so
    "same section" has ONE definition in this repository rather than two that
    agree until they do not. A document with no translation, or whose alignment
    ground is not `section`, contributes nothing and its chunks are never
    collapsed.
    """
    from answer.align import pair_chunks
    from retrieve.collapse import primary_role

    rows_by_doc: dict[str, list] = {}
    source_types: dict[str, str] = {}
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT doc_id, chunk_id, role, text, source_type FROM {view} "
            f"ORDER BY doc_id, role, char_start, chunk_id;"
        )
        for doc_id, chunk_id, role, text, source_type in cur.fetchall():
            rows_by_doc.setdefault(doc_id, []).append((chunk_id, role, text))
            source_types[doc_id] = source_type

    groups = []
    for rows in rows_by_doc.values():
        originals = [_AlignRow(c, t) for c, r, t in rows if r == "original"]
        translations = [_AlignRow(c, t) for c, r, t in rows if r == "translation"]
        if not originals or not translations:
            continue
        for aligned in pair_chunks(originals, translations):
            groups.append((aligned.original.chunk_id,
                           [m.chunk_id for m in aligned.members],
                           aligned.ground))
    # Ruling 11: the caller needs to know which text is a record's primary, and
    # `source_type` is where that already lives.
    return groups, {d: primary_role(t) for d, t in source_types.items()}


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def score_pair(p, hits, target_chunk_id: str, target_text: str = "",
               doc_texts: dict | None = None, shared_query: bool = False,
               alternates: list[str] | None = None,
               alternate_ground: str | None = None) -> PairResult:
    """`hits` is the ranked search result: objects with .chunk_id, .doc_id, .similarity."""
    rank = None
    for i, h in enumerate(hits, start=1):
        if h.chunk_id == target_chunk_id:
            rank = i
            break

    # Ruling 2. `rank` above keeps its pre-Block-C meaning and is what the gaps
    # and the B2-comparable aggregate are computed from; the accepted rank is a
    # second, separately named quantity.
    accepted = [target_chunk_id] + [
        c for c in (alternates or []) if c != target_chunk_id
    ]
    rank_accepted = None
    for i, h in enumerate(hits, start=1):
        if h.chunk_id in accepted:
            rank_accepted = i
            break

    sim_target = hits[rank - 1].similarity if rank else None
    others_any = [h for h in hits if h.chunk_id != target_chunk_id]
    others_doc = [h for h in hits if h.doc_id != p.expect_doc]
    sim_other_chunk = others_any[0].similarity if others_any else None
    sim_other_doc = others_doc[0].similarity if others_doc else None

    spread = None
    if len(hits) >= RECALL_AT:
        spread = hits[0].similarity - hits[RECALL_AT - 1].similarity

    return PairResult(
        id=p.id,
        provenance=p.provenance,
        region=p.region,
        query_lang=p.query_lang,
        expect_lang=p.expect_lang,
        expect_doc=p.expect_doc,
        resolved_chunk_id=target_chunk_id,
        rank=rank,
        recall_at_6=bool(rank and rank <= RECALL_AT),
        rr_at_10=(1.0 / rank) if (rank and rank <= MRR_AT) else 0.0,
        sim_target=sim_target,
        sim_best_other_doc=sim_other_doc,
        sim_best_other_chunk=sim_other_chunk,
        gap_vs_other_doc=(sim_target - sim_other_doc)
        if (sim_target is not None and sim_other_doc is not None) else None,
        gap_vs_other_chunk=(sim_target - sim_other_chunk)
        if (sim_target is not None and sim_other_chunk is not None) else None,
        top1_to_rank6=spread,
        top_doc=hits[0].doc_id if hits else None,
        query_target_overlap=(
            query_target_overlap(p.query, target_text) if target_text else None
        ),
        best_other_doc_chunk_id=others_doc[0].chunk_id if others_doc else None,
        best_other_chunk_id=others_any[0].chunk_id if others_any else None,
        unit=p.unit,
        accepted_chunk_ids=accepted,
        alternate_ground=alternate_ground,
        rank_accepted=rank_accepted,
        recall_at_6_accepted=bool(rank_accepted and rank_accepted <= RECALL_AT),
        anchor_doc=(query_anchor(p.query, doc_texts) if doc_texts else None),
        anchor_points_home=(
            (query_anchor(p.query, doc_texts) == p.expect_doc) if doc_texts else None
        ),
        shared_query=shared_query,
        observed_chunk_id=p.observed_chunk_id,
        observed_chunk_still_exists=None,
        observed_chunk_matches_resolved=(
            None if p.observed_chunk_id is None
            else p.observed_chunk_id == target_chunk_id
        ),
        written_after_the_records_entered_the_index=(
            p.written_after_the_records_entered_the_index),
        note=p.note,
    )


def _own_variant(pair):
    """The single-variant arm's one variant: the pair's own query text.

    Built here rather than imported so that an unfused run does not depend on
    `retrieve.render` at all — a run with no renderings file must behave exactly
    as it did before C2 existed, including when that file is absent.
    """
    from types import SimpleNamespace

    return SimpleNamespace(lang=pair.query_lang, text=pair.query, source="query")


def apply_collapse(result: PairResult, ordering: list,
                   entry: dict | None = None,
                   section_of: dict | None = None,
                   primary_by_doc: dict | None = None) -> PairResult:
    """Record the post-collapse position. Pure, and it touches nothing else.

    `ordering` is the collapsed ranked list — one row per aligned section, as
    the ORIGINAL. The target chunk is either in it or it is not; nothing here
    accepts a chunk retrieval did not return, which is the line ruling 7 drew
    and ruling 8 stays on the correct side of.
    """
    from retrieve.rerank import rank_of

    result.collapsed = True
    result.collapse_primary_role = (primary_by_doc or {}).get(
        result.expect_doc, "original"
    )
    if entry is not None and section_of is not None:
        key = section_of.get(result.resolved_chunk_id)
        result.collapse_entry_role = entry.get(key) if key else None
    result.rank_collapsed = rank_of(ordering, [result.resolved_chunk_id])
    result.recall_at_6_collapsed = bool(
        result.rank_collapsed and result.rank_collapsed <= RECALL_AT
    )
    result.rank_accepted_collapsed = rank_of(ordering, result.accepted_chunk_ids)
    result.recall_at_6_accepted_collapsed = bool(
        result.rank_accepted_collapsed
        and result.rank_accepted_collapsed <= RECALL_AT
    )
    # `!= "translation"` and not `== "original"`: a chunk belonging to no
    # section has no entry role at all, and there was no translation for it to
    # have been reached through. None means "the question does not arise", which
    # is not the same as a miss.
    # Ruling 11: a find record has no source text, so reaching it through its
    # curatorial description is not a shortcut past anything. A unit counts as
    # bypassed only where the record's primary IS the original and the entry was
    # the translation.
    result.recall_at_6_via_original = bool(
        result.recall_at_6_accepted_collapsed
        and not (result.collapse_entry_role == "translation"
                 and result.collapse_primary_role == "original")
    )
    return result


def apply_rerank(result: PairResult, ordering: list, scores: dict,
                 window: int, expect_doc: str) -> PairResult:
    """Record the post-rerank position on an already-scored pair. Pure.

    `ordering` is the reranked candidate list — a PERMUTATION of the pre-rerank
    hits, produced by `retrieve.rerank.reorder`, not a truncation. A target the
    window never reached therefore still has a position, and keeps the one it
    had; `muziris-cargo-akananuru` stays recognisably at 309 rather than becoming
    `none` and looking like a regression the reranker caused.

    Nothing here touches `rank`, `recall_at_6`, `rank_accepted` or either gap.
    The one quantity this function is forbidden to produce is a number that could
    be mistaken for the pre-rerank gap, which is why the reranker-score gaps are
    named `rerank_gap_*` and computed only from `scores`.
    """
    from retrieve.rerank import rank_of

    result.reranked = True
    result.rerank_window = window
    result.rank_reranked = rank_of(ordering, [result.resolved_chunk_id])
    result.recall_at_6_reranked = bool(
        result.rank_reranked and result.rank_reranked <= RECALL_AT
    )
    result.rank_accepted_reranked = rank_of(ordering, result.accepted_chunk_ids)
    result.recall_at_6_accepted_reranked = bool(
        result.rank_accepted_reranked
        and result.rank_accepted_reranked <= RECALL_AT
    )
    # C7 — the sequencing fix. `recall_at_6_via_original` is computed in
    # `apply_collapse`, on the COLLAPSED ordering, while the adopted
    # configuration reranks. The report therefore printed a POST-rerank recall
    # and a PRE-rerank via-original on the same page as though they shared a
    # measurement point. They do not. This is the same predicate evaluated
    # against the post-rerank column, under its own name; nothing above is
    # touched, and `recall_at_6_via_original` keeps the value the collapse gave
    # it.
    result.recall_at_6_via_original_reranked = bool(
        result.recall_at_6_accepted_reranked
        and not (result.collapse_entry_role == "translation"
                 and result.collapse_primary_role == "original")
    )

    # Scores exist for the window only. A target below it has no reranker score,
    # and None is the honest value — not 0.0, which would sort and average.
    result.rerank_top_chunk_ids = [h.chunk_id for h in ordering[:RECALL_AT]]
    # Everything the accepted set now sits below, capped at the recall window —
    # an unranked target would otherwise record four hundred ids saying nothing.
    accepted = set(result.accepted_chunk_ids)
    beaten: list[str] = []
    for hit in ordering[:RECALL_AT]:
        if hit.chunk_id in accepted:
            break
        beaten.append(hit.chunk_id)
    result.rerank_beaten_by = beaten

    result.rerank_score_target = scores.get(result.resolved_chunk_id)
    best_other_doc = None
    best_other_chunk = None
    for hit in ordering:
        score = scores.get(hit.chunk_id)
        if score is None:
            continue
        if hit.chunk_id != result.resolved_chunk_id and best_other_chunk is None:
            best_other_chunk = score
        if hit.doc_id != expect_doc and best_other_doc is None:
            best_other_doc = score
        if best_other_chunk is not None and best_other_doc is not None:
            break
    result.rerank_score_best_other_doc = best_other_doc
    result.rerank_score_best_other_chunk = best_other_chunk
    if result.rerank_score_target is not None:
        if best_other_doc is not None:
            result.rerank_gap_vs_other_doc = result.rerank_score_target - best_other_doc
        if best_other_chunk is not None:
            result.rerank_gap_vs_other_chunk = (
                result.rerank_score_target - best_other_chunk
            )
    return result


def query_anchor(query: str, doc_texts: dict) -> str | None:
    """The document a query's rarest vocabulary points at, if any.

    A token occurring in exactly one document of the index is discriminating;
    if a query has one, this returns that document. `anchor_points_home` is then
    whether it is the document the pair expects.

    This is a LEXICAL property being recorded against a DENSE retriever, so it
    is a diagnostic and not an explanation — the retriever does not match on
    tokens. It is here because the alternative was a hand-assigned
    broad/specific label, and a label assigned after seeing the ranks it is
    meant to predict cannot be evidence for anything.
    """
    import re

    words = {w for w in re.findall(r"\w+", query.lower(), re.UNICODE)
             if w not in _OVERLAP_STOPWORDS and len(w) > 2}
    for w in sorted(words):
        holders = [d for d, t in doc_texts.items() if w in t]
        if len(holders) == 1:
            return holders[0]
    return None


def _mean(values):
    vals = [v for v in values if v is not None]
    return (sum(vals) / len(vals)) if vals else None


def build_units(results: list[PairResult], queries: dict | None = None
                ) -> list[UnitResult]:
    """Collapse pairs into scored units, in first-appearance order.

    A unit is scored on its BEST acceptable target and reports coverage over
    all of them. Both numbers come from `rank_accepted`, so ruling 2's alternate
    is visible at unit level too — the two rulings compose rather than being
    applied at different depths.
    """
    order: list[str] = []
    grouped: dict[str, list[PairResult]] = {}
    for r in results:
        unit = r.unit or r.id
        if unit not in grouped:
            order.append(unit)
        grouped.setdefault(unit, []).append(r)

    units: list[UnitResult] = []
    for unit in order:
        members = grouped[unit]
        ranked = [m for m in members if m.rank_accepted is not None]
        best = min(ranked, key=lambda m: m.rank_accepted) if ranked else None
        hits = sum(1 for m in members if m.recall_at_6_accepted)
        # Block C3, computed exactly as above on the post-rerank column. A unit
        # counts as reranked only if every one of its pairs was, so a partial
        # run cannot produce a unit scored half one way and half the other.
        collapsed = bool(members) and all(m.collapsed for m in members)
        ranked_co = [m for m in members if m.rank_accepted_collapsed is not None]
        best_co = (min(ranked_co, key=lambda m: m.rank_accepted_collapsed)
                   if (collapsed and ranked_co) else None)
        hits_co = sum(1 for m in members if m.recall_at_6_accepted_collapsed)
        # A unit counts as reached via its original if ANY of its acceptable
        # targets got there that way — the same "best acceptable target" reading
        # ruling 1 gave the unit itself.
        via_original = any(m.recall_at_6_via_original for m in members)
        reranked = bool(members) and all(m.reranked for m in members)
        ranked_rr = [m for m in members if m.rank_accepted_reranked is not None]
        best_rr = (min(ranked_rr, key=lambda m: m.rank_accepted_reranked)
                   if (reranked and ranked_rr) else None)
        hits_rr = sum(1 for m in members if m.recall_at_6_accepted_reranked)
        # C7. The same "ANY acceptable target got there that way" reading as
        # `via_original` above, on the post-rerank column.
        via_original_rr = any(m.recall_at_6_via_original_reranked
                              for m in members)
        units.append(UnitResult(
            unit=unit,
            query=(queries or {}).get(unit, ""),
            pairs=[m.id for m in members],
            best_rank=best.rank_accepted if best else None,
            recall_at_6=bool(best and best.rank_accepted <= RECALL_AT),
            rr_at_10=(1.0 / best.rank_accepted)
            if (best and best.rank_accepted <= MRR_AT) else 0.0,
            coverage_n=hits,
            coverage_total=len(members),
            coverage=hits / len(members),
            best_pair=best.id if best else None,
            collapsed=collapsed,
            best_rank_collapsed=best_co.rank_accepted_collapsed if best_co else None,
            recall_at_6_collapsed=bool(
                best_co and best_co.rank_accepted_collapsed <= RECALL_AT
            ),
            rr_at_10_collapsed=(1.0 / best_co.rank_accepted_collapsed)
            if (best_co and best_co.rank_accepted_collapsed <= MRR_AT) else 0.0,
            coverage_n_collapsed=hits_co if collapsed else 0,
            recall_at_6_via_original=via_original if collapsed else False,
            reranked=reranked,
            best_rank_reranked=best_rr.rank_accepted_reranked if best_rr else None,
            recall_at_6_reranked=bool(
                best_rr and best_rr.rank_accepted_reranked <= RECALL_AT
            ),
            rr_at_10_reranked=(1.0 / best_rr.rank_accepted_reranked)
            if (best_rr and best_rr.rank_accepted_reranked <= MRR_AT) else 0.0,
            coverage_n_reranked=hits_rr if reranked else 0,
            # Gated on `reranked`, exactly as the pre-rerank one is gated on
            # `collapsed`. A unit with any un-reranked pair is not scored as
            # reranked, so it cannot be scored half one way and half the other.
            recall_at_6_via_original_reranked=(
                via_original_rr if reranked else False),
            coverage_reranked=(hits_rr / len(members)) if reranked else None,
            best_pair_reranked=best_rr.id if best_rr else None,
        ))
    return units


def summarise_units(units: list[UnitResult]) -> dict:
    if not units:
        return {"units": 0}
    multi = [u for u in units if u.coverage_total > 1]
    reranked = [u for u in units if u.reranked]
    extra: dict = {}
    if any(u.collapsed for u in units):
        # Over ALL units, like the reranked keys and for the same reason: the
        # gate's denominator is 30 whatever a run happened to touch.
        extra.update({
            "collapsed_units": sum(1 for u in units if u.collapsed),
            "recall_at_6_collapsed": sum(u.recall_at_6_collapsed for u in units) / len(units),
            "recall_at_6_collapsed_n": sum(u.recall_at_6_collapsed for u in units),
            "mrr_at_10_collapsed": sum(u.rr_at_10_collapsed for u in units) / len(units),
            "targets_in_top_6_collapsed": sum(u.coverage_n_collapsed for u in units),
            "recall_at_6_via_original": sum(u.recall_at_6_via_original for u in units) / len(units),
            "recall_at_6_via_original_n": sum(u.recall_at_6_via_original for u in units),
        })
        # C7, ruling 26. The post-rerank member of the pair is emitted HERE,
        # inside the collapse block, and not in the rerank block below — the
        # entry role it reads is a fact the COLLAPSE produces. A run that
        # reranked WITHOUT collapsing has no entry role for the bypass clause
        # to fire on, so the number would come out exactly equal to post-rerank
        # recall and be published under a name that says something else.
        # An uncollapsed run reports neither figure; an unreranked run reports
        # the pre-rerank one alone.
        if reranked:
            extra.update({
                "recall_at_6_via_original_reranked":
                    sum(u.recall_at_6_via_original_reranked for u in units) / len(units),
                "recall_at_6_via_original_reranked_n":
                    sum(u.recall_at_6_via_original_reranked for u in units),
            })
    if reranked:
        # `.update`, NOT `=`. This was `extra = {...}` until 2026-08-16, which
        # silently discarded the collapse keys added above it — so a run with
        # BOTH interventions on died in print_report with KeyError after
        # twenty-six minutes and 294,699 tokens of measurement. Neither
        # intervention alone could show it.
        extra.update({
            "reranked_units": len(reranked),
            "recall_at_6_reranked": sum(u.recall_at_6_reranked for u in units) / len(units),
            "recall_at_6_reranked_n": sum(u.recall_at_6_reranked for u in units),
            "mrr_at_10_reranked": sum(u.rr_at_10_reranked for u in units) / len(units),
            "targets_in_top_6_reranked": sum(u.coverage_n_reranked for u in units),
            "unranked_reranked": sum(1 for u in units if u.best_rank_reranked is None),
        })
    return {**extra,
        "units": len(units),
        "pairs": sum(u.coverage_total for u in units),
        "recall_at_6": sum(u.recall_at_6 for u in units) / len(units),
        "recall_at_6_n": sum(u.recall_at_6 for u in units),
        "mrr_at_10": sum(u.rr_at_10 for u in units) / len(units),
        # Reported, never gated. See UnitResult's docstring.
        "mean_coverage": sum(u.coverage for u in units) / len(units),
        "targets_in_top_6": sum(u.coverage_n for u in units),
        "targets_total": sum(u.coverage_total for u in units),
        "multi_target_units": len(multi),
        "multi_target_coverage": (
            sum(u.coverage_n for u in multi) / sum(u.coverage_total for u in multi)
            if multi else None
        ),
        "unranked": sum(1 for u in units if u.best_rank is None),
    }


def summarise(results: list[PairResult]) -> dict:
    if not results:
        return {"pairs": 0}
    return {
        "pairs": len(results),
        "recall_at_6": sum(r.recall_at_6 for r in results) / len(results),
        "recall_at_6_n": sum(r.recall_at_6 for r in results),
        "mrr_at_10": sum(r.rr_at_10 for r in results) / len(results),
        "mean_gap_vs_other_doc": _mean(r.gap_vs_other_doc for r in results),
        "mean_gap_vs_other_chunk": _mean(r.gap_vs_other_chunk for r in results),
        "mean_top1_to_rank6": _mean(r.top1_to_rank6 for r in results),
        "mean_query_target_overlap": _mean(r.query_target_overlap for r in results),
        # Named for the k it is actually measured at. It was hardcoded to
        # "not_in_top_20" and survived SEARCH_K moving to 50, which is a metric
        # whose NAME is wrong — the failure this repository keeps paying for,
        # in its cheapest form. eval/test_ranking_check.py now asserts the
        # label tracks SEARCH_K.
        "unranked": sum(1 for r in results if r.rank is None),
    }


# --------------------------------------------------------------------------
# The run
# --------------------------------------------------------------------------

def run(view: str, dry_run: bool = False, skip_check: bool = False,
        collapse_sections: bool = False,
        rerank: bool = False, rerank_window: int | None = None,
        rerank_model: str | None = None, rerank_pace: float = 0.0,
        rerank_tpm: float = 0.0, fuse_renderings: str | None = None,
        allow_unresolvable: set[str] | None = None) -> Report:
    from eval.goldset import load_ranking_pairs
    from retrieve.search import search

    pairs = load_ranking_pairs()

    try:
        import psycopg  # noqa: F401
    except ModuleNotFoundError as exc:
        raise SystemExit(
            f"{exc}. This check reads the live index, so it needs the host's "
            f"venv:\n  .venv\\Scripts\\Activate.ps1\n"
            f"For a database-free check of the gold set itself, run "
            f"`python -m eval.test_ranking_check`."
        ) from exc

    from ingest import db

    reason = db.check_connection()
    if reason:
        raise SystemExit(reason)

    import psycopg

    with psycopg.connect(db.get_dsn()) as conn:
        problems = [] if skip_check else check_index_is_current(conn, view)
        if problems:
            raise SystemExit(
                "the index is not in a state a baseline can be recorded "
                "against:\n  - " + "\n  - ".join(problems)
                + "\n(--skip-check overrides this, and the override is recorded "
                  "in the archived run so a number produced that way can never "
                  "be mistaken for a clean one.)"
            )

        n_index, models = index_state(conn, view)

        # Not behind --skip-check. That flag is for "the index does not match
        # the seed corpus", which is a judgement a person can knowingly
        # override; this is "the numbers would be about a different index than
        # the one they name", which nobody can knowingly want.
        unreachable = check_search_reaches_the_view(conn, view, n_index)
        if unreachable:
            raise SystemExit("\n  - ".join(["the ranking cannot reach its own index:"]
                                           + unreachable))

        resolved, unresolvable = resolve_targets(conn, pairs, view)

        # FINDING 12, and it fires HERE — before resolve_alternates, before the
        # batched embedding request, before the rerank. A run whose denominator
        # has moved cannot be compared to the runs before it, and the cheapest
        # moment to say so is the one where nothing has been spent yet.
        allowed = set(allow_unresolvable or ())
        problem = unresolved_pair_problem(pairs, resolved, unresolvable, allowed)
        if problem:
            raise SystemExit(problem)

        alternates = resolve_alternates(conn, pairs, view, resolved)

        section_of: dict = {}
        canonical: dict = {}
        primary_by_doc: dict = {}
        if collapse_sections:
            from retrieve.collapse import section_maps

            from retrieve.collapse import promote_sole

            _groups, primary_by_doc = resolve_sections(conn, view)
            section_of, canonical = section_maps(
                promote_sole(_groups), primary_by_doc
            )

        with conn.cursor() as cur:
            cur.execute(
                f"SELECT doc_id, lower(string_agg(text, ' ')) FROM {view} "
                f"GROUP BY doc_id;"
            )
            doc_texts = {d: t for d, t in cur.fetchall()}
        import collections as _c
        _qn = _c.Counter(x.query for x in pairs)
        # Pairs sharing a query AND the same filters see the same candidate
        # pool, so they share one rerank call. Two of the 33 pairs do. This is a
        # spend optimisation only: it cannot change a rank, because the pool it
        # keys on is the thing that determines one.
        rerank_cache: dict = {}

        report = Report(
            timestamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S+0000"),
            view=view,
            search_k=_search_depth(n_index),
            index_chunks=n_index,
            embedding_models=models,
            query_embedding_model="",
            unresolvable=unresolvable,
            allowed_unresolvable=sorted(allowed),
        )
        if allowed:
            report.notes.append(
                "RAN WITH --allow-unresolvable " + ", ".join(sorted(allowed))
                + ": these gold pairs were knowingly left out, so this run's "
                "denominator is smaller than that of a run carrying no "
                "allowance. NOT COMPARABLE to one. (FINDING 12.)"
            )
        if collapse_sections:
            report.collapsed = True
            report.collapse_sections = len(canonical)
            if not canonical:
                raise SystemExit(
                    "--collapse was asked for and the alignment produced NO "
                    "sections. A collapse that collapses nothing would report "
                    "the uncollapsed ranking under a name that says otherwise, "
                    "which is the failure this repository keeps paying for."
                )
        if rerank:
            from retrieve.rerank import DEFAULT_MODEL as _RR_MODEL
            report.reranked = True
            report.rerank_model = rerank_model or _RR_MODEL
            report.rerank_window = rerank_window or _RR_WINDOW_DEFAULT()
            report.rerank_pace_seconds = rerank_pace
            report.rerank_tpm_budget = rerank_tpm
        if skip_check:
            report.notes.append(
                "RAN WITH --skip-check: the index was not verified against the "
                "seed corpus on disk. Do not compare this run to a clean one."
            )
        if not resolved:
            raise SystemExit(
                "no pair resolved to a passage in the index. A ranking run with "
                "nothing to rank prints green while asserting nothing, which is "
                "the failure this file exists to rule out."
            )

        live = [p for p in pairs if p.id in resolved]
        if dry_run:
            report.notes.append(
                f"--dry-run: {len(live)} of {len(pairs)} pairs resolved; no "
                f"query was embedded and no similarity was computed."
            )
            return report

        # One batched request for every query. Voyage free tier is 3 req/min,
        # and 32 separate calls would be eleven minutes of sleeping.
        from ingest.embed import embed_texts, resolve_model_label

        # ------------------------------------------------------------------
        # C2 — ruling 12/13. The variants, and the coverage check that refuses
        # to measure a configuration nobody chose.
        # ------------------------------------------------------------------
        variants_by_pair: dict = {}
        if fuse_renderings:
            from retrieve.render import (
                Variant, coverage_problems, load as load_renderings,
            )

            renderings = load_renderings(fuse_renderings)
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT DISTINCT lang FROM {view} WHERE lang IS NOT NULL;")
                index_langs = sorted(r[0] for r in cur.fetchall())
            bad = coverage_problems(
                renderings, {p.query: p.query_lang for p in live}, index_langs)
            if bad:
                raise SystemExit(
                    "the rendering file does not match this run:\n  - "
                    + "\n  - ".join(bad)
                    + "\n(ruling 12 derives the language set from the INDEX, so "
                      "a file built against another index is a different rule.)"
                )
            for pair in live:
                variants_by_pair[pair.id] = renderings.variants_for(
                    pair.query, pair.query_lang)
            report.fused = True
            report.renderings_path = str(fuse_renderings)
            report.renderings_digest = renderings.digest
            report.renderings_stale = [
                {"query": q, "lang": lang, "ok_now": ok}
                for q, lang, ok in renderings.stale
            ]
            report.fused_variant_langs = sorted({
                v.lang for vs in variants_by_pair.values() for v in vs})
            if renderings.stale:
                report.notes.append(
                    f"{len(renderings.stale)} rendering(s) carried a verdict "
                    f"the current guard disagrees with and were re-judged on "
                    f"read (ruling 24). The content hash alone would not have "
                    f"shown this."
                )

        # Every distinct text embedded ONCE. Two pairs sharing a query share a
        # vector, and so do a query and any rendering identical to it.
        texts: list[str] = []
        position: dict[str, int] = {}
        for pair in live:
            for variant in variants_by_pair.get(
                    pair.id, [_own_variant(pair)]):
                if variant.text not in position:
                    position[variant.text] = len(texts)
                    texts.append(variant.text)

        embedded = embed_texts(texts, input_type="query")
        report.query_embedding_model = resolve_model_label()
        vector_of = {text: embedded.vectors[i] for text, i in position.items()}
        report.notes.append(
            f"{len(live)} pairs, {len(texts)} distinct query text(s) embedded "
            f"in {embedded.batches} request(s)"
            + (f"; fused over {report.fused_variant_langs}" if fuse_renderings
               else "")
        )

        def score_arm(p, hits, arm: str) -> PairResult:
            """One pair, one candidate list, through the whole pipeline.

            Ruling 14 needs two arms measured on the same index on the same day,
            and an arm is a WHOLE measurement — its own rank, its own gaps, its
            own collapse and its own rerank. So the pipeline is written once and
            called twice rather than copied, and `arm` exists for exactly one
            reason: the rerank cache keys on it. Two arms hand the cross-encoder
            different candidate sets under the same query, and a cache that
            could not tell them apart would score the fused arm with the
            single-variant arm's answer and report it as a rerank.
            """
            target_id, target_text = resolved[p.id]
            alt_ids, alt_ground = alternates.get(p.id, ([], None))
            result = score_pair(p, hits, target_id, target_text,
                                doc_texts=doc_texts, shared_query=_qn[p.query] > 1,
                                alternates=alt_ids, alternate_ground=alt_ground)

            # The list everything downstream ranks against. Collapse comes
            # FIRST when both are asked for: deduplicating a candidate set and
            # then reranking it is a pipeline; reranking and then deduplicating
            # would hand the cross-encoder the very sibling pair C2a exists to
            # remove. The order is recorded in the header.
            base = hits
            if collapse_sections:
                from retrieve.collapse import collapse, collapse_report

                from retrieve.collapse import entry_roles

                base = collapse(hits, section_of, canonical)
                if arm == "single" and not report.collapse_stats:
                    report.collapse_stats = collapse_report(hits, base)
                apply_collapse(result, base, entry_roles(hits, section_of),
                               section_of, primary_by_doc)

            if rerank:
                from retrieve.rerank import (
                    RerankError, pool_problems, reorder, rerank_documents,
                    scores_by_chunk,
                )
                window = report.rerank_window
                candidates = base[:window]
                # Design constraint 1, asserted rather than described. `search()`
                # applies langs and roles in SQL, so this is expected to be
                # silent — and if a later change reranks a raw pool instead, five
                # cross-lingual tests become same-language tests still wearing
                # the label, and no rank would say so.
                bad_pool = pool_problems(candidates, langs=p.langs, roles=p.roles)
                if bad_pool:
                    raise SystemExit(
                        f"{p.id}: the set about to be reranked does not match the "
                        f"pair's own filters:\n  - " + "\n  - ".join(bad_pool)
                    )
                # The ARM is part of the key. Ruling 16 keeps `p.query` as what
                # the cross-encoder is asked, so two arms of one pair send the
                # same query — but over different candidate sets, and a rerank
                # is a function of both. Keying on the query alone would hand
                # the fused arm the single-variant arm's scores and print them
                # as a reranked result.
                key = (arm, p.query, tuple(p.langs or ()), tuple(p.roles or ()),
                       tuple(h.chunk_id for h in candidates))
                if key not in rerank_cache:
                    try:
                        rr = rerank_documents(
                            p.query, [h.text for h in candidates],
                            model=report.rerank_model,
                            min_interval=rerank_pace,
                            tpm_budget=rerank_tpm,
                        )
                    except RerankError as exc:
                        # WHERE it failed, not just that it did. The first C3
                        # rate-limit failure said only "probe-greek-muziris",
                        # and whether that was call 1 or call 8 is the whole
                        # difference between "the limit blocks rerank outright"
                        # and "the spacing is too tight" — two different
                        # diagnoses, and it took a gold-file lookup to tell them
                        # apart.
                        raise SystemExit(
                            f"{p.id}: rerank failed on call "
                            f"{report.rerank_requests + 1}; "
                            f"{report.rerank_requests} call(s) had already "
                            f"succeeded. A partial run is not archived.\n{exc}"
                        ) from exc
                    rerank_cache[key] = rr
                    report.rerank_requests += 1
                    report.rerank_seconds_waiting += rr.waited
                    print(f"  rerank {report.rerank_requests:3d}  {p.id:28.28s} "
                          f"waited {rr.waited:5.1f}s  "
                          f"tokens {rr.total_tokens}", flush=True)
                    report.rerank_route = rr.path
                    if rr.total_tokens is not None:
                        report.rerank_tokens = (report.rerank_tokens or 0) + rr.total_tokens
                rr = rerank_cache[key]
                ordering = reorder(base, rr.scored, window)
                apply_rerank(result, ordering,
                             scores_by_chunk(base, rr.scored, window),
                             window, p.expect_doc)

            if p.observed_chunk_id:
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT 1 FROM {view} WHERE chunk_id = %s;",
                        (p.observed_chunk_id,),
                    )
                    result.observed_chunk_still_exists = cur.fetchone() is not None
                if arm == "single" and not result.observed_chunk_matches_resolved:
                    report.chunk_id_drift.append({
                        "id": p.id,
                        "archived_chunk_id": p.observed_chunk_id,
                        "resolves_to": target_id,
                        "archived_id_still_exists": result.observed_chunk_still_exists,
                    })
            return result

        for p in live:
            # ARM ONE — the query's own text alone. This is the configuration
            # adopted on 2026-08-16, and `report.pairs` keeps every meaning it
            # has had since the B2 baseline was recorded.
            hits = search(conn, vector_of[p.query], k=_search_depth(n_index),
                          langs=p.langs, roles=p.roles, view=view)
            report.pairs.append(score_arm(p, hits, "single"))

            if not fuse_renderings:
                continue

            # ARM TWO — ruling 13. One search per variant over the SAME view
            # under the SAME filters, fused by max.
            from retrieve.fuse import fuse
            from retrieve.fuse import pool_problems as fuse_pool_problems

            per_variant = []
            for variant in variants_by_pair[p.id]:
                if variant.text == p.query:
                    per_variant.append((variant.lang, hits))
                    continue
                per_variant.append((variant.lang, search(
                    conn, vector_of[variant.text], k=_search_depth(n_index),
                    langs=p.langs, roles=p.roles, view=view)))
            bad_variants = fuse_pool_problems(per_variant)
            if bad_variants:
                raise SystemExit(
                    f"{p.id}: the variants about to be fused are not "
                    f"comparable:\n  - " + "\n  - ".join(bad_variants)
                )
            fused = fuse(per_variant, SEARCH_K)
            fused_result = score_arm(p, fused.hits, "fused")
            fused_result.fused = True
            fused_result.fused_variants = list(fused.variants)
            fused_result.fused_from_lang = fused.lang_of(
                fused_result.resolved_chunk_id)
            if not report.fusion_stats:
                from retrieve.fuse import fusion_report
                report.fusion_stats = fusion_report(hits, fused)
            # Ruling 15b. The control is an assertion the pipeline can fail,
            # and a violation is printed, never gated.
            from retrieve.render import native_query_problems

            fused_result.native_control_problems = native_query_problems(
                p.query_lang, fused_result.fused_from_lang,
                report.pairs[-1].rank, fused_result.rank)
            if fused_result.native_control_problems:
                report.native_control.append({
                    "id": p.id, "query_lang": p.query_lang,
                    "problems": fused_result.native_control_problems,
                })
            report.pairs_fused.append(fused_result)

    report.aggregate = summarise(report.pairs)
    cohorts = sorted({r.provenance for r in report.pairs})
    report.by_cohort = {
        c: summarise([r for r in report.pairs if r.provenance == c]) for c in cohorts
    }
    report.units = build_units(
        report.pairs, {p.unit: p.query for p in pairs}
    )
    report.aggregate_units = summarise_units(report.units)
    if report.pairs_fused:
        report.aggregate_fused = summarise(report.pairs_fused)
        report.by_cohort_fused = {
            c: summarise([r for r in report.pairs_fused if r.provenance == c])
            for c in sorted({r.provenance for r in report.pairs_fused})
        }
        report.units_fused = build_units(
            report.pairs_fused, {p.unit: p.query for p in pairs}
        )
        report.aggregate_units_fused = summarise_units(report.units_fused)
    return report


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def _fmt(value, width=7, places=3):
    return " " * width if value is None else f"{value:>{width}.{places}f}"


def print_report(report: Report) -> None:
    print(f"ranking check  {report.timestamp}  view={report.view}  "
          f"index={report.index_chunks} chunks  depth={report.search_k}  "
          f"models={report.embedding_models}")
    if report.collapsed:
        c = report.collapse_stats or {}
        print(f"  C2a COLLAPSED  sections={report.collapse_sections} "
              f"chunks {c.get('in', 0)} -> {c.get('out', 0)} "
              f"(removed {c.get('removed', 0)})"
              + ("  [collapse runs BEFORE rerank]" if report.reranked else ""))
    if report.reranked:
        print(f"  C3 RERANKED  model={report.rerank_model} "
              f"window={report.rerank_window} route={report.rerank_route} "
              f"requests={report.rerank_requests} "
              f"pace={report.rerank_pace_seconds:g}s "
              f"tpm={report.rerank_tpm_budget:g} "
              f"waiting={report.rerank_seconds_waiting:.0f}s "
              f"tokens={report.rerank_tokens if report.rerank_tokens is not None else 'not reported'}")
    if report.fused:
        f = report.fusion_stats or {}
        print(f"  C2 FUSED  renderings={report.renderings_path} "
              f"digest={report.renderings_digest} "
              f"variants={report.fused_variant_langs}")
        print(f"            top6 moved={f.get('moved', 0)} "
              f"won_by_rendering={f.get('won_by_rendering', 0)} "
              f"won_by_lang={f.get('won_by_lang', {})}")
        if report.renderings_stale:
            print(f"            STALE {len(report.renderings_stale)} row(s) "
                  f"were re-judged on read; the digest alone would not say so")
    for note in report.notes:
        print(f"  note: {note}")
    print()
    print(f"{'pair':30s} {'coh':4s} {'rank':>5s} {'r@6':>4s} "
          f"{'sim':>7s} {'gapDoc':>7s} {'gapAny':>7s} {'spread':>7s} {'lexOv':>6s}")
    for r in sorted(report.pairs, key=lambda r: (r.provenance, r.id)):
        print(f"{r.id:30.30s} {r.provenance[:3]:4s} "
              f"{(str(r.rank) if r.rank else 'none'):>5s} "
              f"{('yes' if r.recall_at_6 else 'NO'):>4s} "
              f"{_fmt(r.sim_target)} {_fmt(r.gap_vs_other_doc)} "
              f"{_fmt(r.gap_vs_other_chunk)} {_fmt(r.top1_to_rank6)} "
              f"{_fmt(r.query_target_overlap, 6, 2)}")

    print()
    print("cohort              pairs  recall@6   MRR@10  gapDoc  gapAny  spread  lexOv")
    for name, s in list(report.by_cohort.items()) + [("ALL", report.aggregate)]:
        # A --dry-run report has resolved pairs but no metrics, because run()
        # returns before aggregating. Printing the header and then dying on
        # `KeyError: 'pairs'` made the one free pre-flight check unusable
        # without --json; it is skipped rather than faked.
        if not s.get("pairs"):
            continue
        print(f"{name:20.20s} {s['pairs']:5d}  "
              f"{s['recall_at_6']:.3f} ({s['recall_at_6_n']:2d})  "
              f"{s['mrr_at_10']:.3f}  {_fmt(s['mean_gap_vs_other_doc'], 6)}  "
              f"{_fmt(s['mean_gap_vs_other_chunk'], 6)}  "
              f"{_fmt(s['mean_top1_to_rank6'], 6)}  "
              f"{_fmt(s.get('mean_query_target_overlap'), 5, 2)}")

    if report.units:
        u = report.aggregate_units
        print()
        print(f"BLOCK C, scored by UNIT — {u['units']} units over {u['pairs']} "
              f"pairs. This is the number G2's recall criterion reads.")
        print(f"{'unit':30s} {'pairs':>5s} {'best':>5s} {'r@6':>4s} {'coverage':>9s}")
        for unit in report.units:
            if unit.coverage_total == 1 and unit.recall_at_6:
                continue                      # single-target units that hit: no news
            print(f"{unit.unit:30.30s} {unit.coverage_total:5d} "
                  f"{(str(unit.best_rank) if unit.best_rank else 'none'):>5s} "
                  f"{('yes' if unit.recall_at_6 else 'NO'):>4s} "
                  f"{unit.coverage_n:4d}/{unit.coverage_total:<4d}")
        print("  (single-target units that reached the top 6 are omitted above)")
        print()
        print(f"  recall@{RECALL_AT}   {u['recall_at_6']:.3f} "
              f"({u['recall_at_6_n']}/{u['units']})     "
              f"MRR@{MRR_AT} {u['mrr_at_10']:.3f}")
        print(f"  coverage   {u['targets_in_top_6']}/{u['targets_total']} targets "
              f"in the top {RECALL_AT}; mean per unit {u['mean_coverage']:.3f}")
        if u["multi_target_coverage"] is not None:
            print(f"             over the {u['multi_target_units']} multi-target "
                  f"unit(s) alone: {u['multi_target_coverage']:.3f}")
        where = broken_link_phrase(report.pairs, report.view)
        print(f"  Coverage is REPORTED, never gated. Ruling 1 reaches the gate "
              f"partly by no\n  longer counting the two hardest Muziris targets "
              f"— one of them the corpus's\n  only genuinely broken "
              f"cross-lingual link, {where}. That failure is real\n  whatever "
              f"this table says, and belongs on the same page as any G2 number.")

        admitted = [r for r in report.pairs if len(r.accepted_chunk_ids) > 1]
        asked = [r for r in report.pairs if r.alternate_ground is not None]
        if asked:
            print()
            print(f"  ruling 2: {len(asked)} pair(s) accept an aligned "
                  f"translation; {len(admitted)} had one admitted")
            for r in asked:
                extra = [c for c in r.accepted_chunk_ids if c != r.resolved_chunk_id]
                moved = (r.rank_accepted != r.rank)
                print(f"    {r.id:28.28s} ground={r.alternate_ground or 'none':8s} "
                      f"rank {r.rank} -> {r.rank_accepted}"
                      f"{'  (the alternate is what reached it)' if moved else ''}")
                if extra:
                    print(f"      accepts also: {extra}")

        if report.collapsed:
            _print_collapse(report)
        if report.reranked:
            _print_rerank(report)
        if report.fused:
            _print_fused(report)

    _print_ruling_54(report)

    print()
    print("Phase 1's comparable number is `spread` (mean top-1 to rank-6): 0.105 "
          "overall,\n0.045-0.094 on the questions that matter. Nothing else in "
          "this table has a\nprior to be compared against — that is what makes "
          "it a baseline.")

    if report.unresolvable:
        print(f"\n{len(report.unresolvable)} pair(s) NOT MEASURED — the index does "
              f"not hold what they name:")
        for u in report.unresolvable:
            print(f"  {u['id']}: {u['reason']}")
            if u["chunks"]:
                print(f"      {u['chunks']}")
        # FINDING 12. Since the guard, reaching this block at all means every
        # id in it was named on the command line: an unnamed one would have
        # killed the run before a single query was embedded. Said here because
        # this block used to print under a green exit code, thirty lines below
        # aggregates computed over the shrunken denominator.
        print(f"  All of these were named in --allow-unresolvable. The "
              f"aggregates above are over {len(report.pairs)} pairs, NOT over "
              f"the gold file's full count, and are not comparable to a run "
              f"carrying no allowance.")

    if report.chunk_id_drift:
        print(f"\n{len(report.chunk_id_drift)} archived chunk_id(s) no longer name "
              f"the passage they were recorded against:")
        for d in report.chunk_id_drift:
            exists = "still exists" if d["archived_id_still_exists"] else "is gone"
            print(f"  {d['id']}: {d['archived_chunk_id']} ({exists}) "
                  f"-> {d['resolves_to']}")
        print("  Counted, not failed on. This is why pairs assert characters and "
              "not ids.")

    anchored = [r for r in report.pairs if r.anchor_points_home]
    unanchored = [r for r in report.pairs if r.anchor_points_home is False]
    shared = [r for r in report.pairs if r.shared_query]
    if anchored and unanchored:
        def _rate(v):
            return f"{sum(x.recall_at_6 for x in v):2d}/{len(v):2d} = {sum(x.recall_at_6 for x in v)/len(v):.2f}"
        print(f"\nrank-blind diagnostics, recall@{RECALL_AT}:")
        print(f"  query's rarest token points at the expected document   {_rate(anchored)}")
        print(f"  it points elsewhere, or the query has no rare token    {_rate(unanchored)}")
        if shared:
            print(f"  query is shared with another pair                       {_rate(shared)}")
        print("  Diagnostics, not explanations: a lexical property recorded")
        print("  against a dense retriever, on a handful of misses. Do not read")
        print("  a cause out of them without a run designed to test one.")

    cohort_counts = {c: s["pairs"] for c, s in report.by_cohort.items()}
    if cohort_counts.get("archived_answer"):
        print(f"\nRead the cohort table before the total. The "
              f"{cohort_counts['archived_answer']} `archived_answer` pairs name "
              f"chunks retrieval\nitself returned, so they cannot contain the "
              f"case where retrieval missed a\npassage entirely — their recall is "
              f"partly true by construction.")


def _print_ruling_54(report: Report) -> None:
    """Ruling 54's exclusion, printed rather than remembered.

    The pairs written after their records were already in the index are named
    here, every run, with the sentence that says what may not be done with
    them. The alternative was to drop them from the tables, and ruling 52's
    argument applies unchanged: excluding by a recorded rule is a diff, and
    excluding by making a row vanish is not. They are scored, they are in every
    aggregate, and the aggregate is not a before/after number for them.

    No count goes in this function's printed labels -- FINDING 49. The number
    is in the detail line, where nothing matches on it.
    """
    stamped = [r for r in report.pairs
               if r.written_after_the_records_entered_the_index]
    print()
    if not stamped:
        print("  ruling 54: no pair in this run was written after its record "
              "entered the index.")
        return
    print(f"  ruling 54: {len(stamped)} pair(s) were written AFTER their "
          f"records were already")
    print("  in the index. They are scored and they are in every aggregate "
          "above. They may")
    print("  NOT be cited as evidence that the tranche which added those "
          "records improved")
    print("  retrieval -- a pair written after the run is a pair written "
          "knowing the rank.")
    for r in stamped:
        print(f"    {r.id:30.30s} {r.expect_doc:32.32s} "
              f"rank {(str(r.rank) if r.rank else 'none'):>4s}")
    print("  Every pair NOT listed here was written before its record was ever "
          "ranked.")
    print("  That absence is the claim.")


def _print_collapse(report: Report) -> None:
    """The C2a block. Prints what was removed, not just that something was."""
    u = report.aggregate_units
    c = report.collapse_stats or {}
    print()
    print(f"  C2a collapse (ruling 8) — {report.collapse_sections} aligned "
          f"section(s); on a full ranking {c.get('removed', 0)} of "
          f"{c.get('in', 0)} chunks fold into a sibling, "
          f"roles removed: {c.get('roles_removed', [])}")
    print(f"  recall@{RECALL_AT} per unit   "
          f"uncollapsed {u['recall_at_6']:.3f} ({u['recall_at_6_n']}/{u['units']})"
          f"   ->   COLLAPSED {u['recall_at_6_collapsed']:.3f} "
          f"({u['recall_at_6_collapsed_n']}/{u['units']})")
    print(f"  MRR@{MRR_AT} per unit        uncollapsed {u['mrr_at_10']:.3f}"
          f"   ->   collapsed {u['mrr_at_10_collapsed']:.3f}")

    # C7. "PRE-rerank" is not decoration. This figure is computed on the
    # COLLAPSED ordering, and a reranked run prints a post-rerank recall further
    # down the same page; until the point was named, the two read as one
    # measurement.
    print(f"  recall@{RECALL_AT} VIA THE ORIGINAL TEXT, PRE-rerank   "
          f"{u['recall_at_6_via_original']:.3f} "
          f"({u['recall_at_6_via_original_n']}/{u['units']})"
          f"   <- ruling 9's companion; no translation-mediated fix can raise it")

    via_translation = [r for r in report.pairs
                       if r.collapse_entry_role == "translation"
                       and r.recall_at_6_collapsed]
    if via_translation:
        # Ruling 11 splits this list, and the split matters. A literary text or
        # an inscription reached through its English was a SOURCE TEXT bypassed.
        # A find record has no source text — its curatorial description IS the
        # record — so reaching it that way bypasses nothing. Printing both under
        # one heading said something false about three of them.
        bypassed = [r for r in via_translation
                    if r.collapse_primary_role == "original"]
        no_source = [r for r in via_translation if r not in bypassed]
        print(f"  {len(bypassed)} pair(s) reached a SOURCE TEXT through its "
              f"English, bypassing the original:")
        for r in bypassed:
            print(f"    {r.id:28.28s} rank {r.rank} -> {r.rank_collapsed}")
        if no_source:
            print(f"  {len(no_source)} further pair(s) entered through a "
                  f"translation-role chunk, but their record has NO source "
                  f"text\n  (find or coin records, where the curatorial "
                  f"description IS the record) — not a bypass:")
            for r in no_source:
                print(f"    {r.id:28.28s} rank {r.rank} -> {r.rank_collapsed}")
        print("  Reported, never gated. The record was found, which is what the "
              "product owes\n  the reader; for the first group the non-English "
              "text was NOT shown to be\n  reachable, which is what the corpus "
              "exists to demonstrate. Both are true\n  and only one is in the "
              "number.")

    flipped = [x for x in report.units
               if x.collapsed and x.recall_at_6_collapsed != x.recall_at_6]
    if flipped:
        print(f"  {len(flipped)} unit(s) changed status:")
        for x in flipped:
            direction = "MISS -> hit" if x.recall_at_6_collapsed else "hit -> MISS"
            print(f"    {x.unit:28.28s} {direction}   best rank "
                  f"{x.best_rank} -> {x.best_rank_collapsed}")
    else:
        print("  no unit changed status.")
    print("  Ruling 8's cost, which travels with this number: a collapsed "
          "top 6 is six\n  RECORDS, not six chunks, and therefore covers more "
          "underlying text than an\n  uncollapsed six. The gaps above are "
          "computed on the UNCOLLAPSED ranking and\n  are unaffected — "
          "collapsing within a document cannot move gapDoc, so C2a\n  is a "
          "recall intervention only and the gap remains C2's.")


def _print_rerank(report: Report) -> None:
    """The C3 block. Prints what moved, and says which quantity came from where.

    The last line is not decoration. G2's checklist has a recall criterion and a
    gap criterion, and ruling 3 measures them at different points; a run that
    printed both without saying so would let the gate be assessed against two
    incompatible readings of its own checklist, which is the failure ruling 3
    exists to foreclose.
    """
    u = report.aggregate_units
    print()
    print(f"  C3 rerank, model={report.rerank_model}, window={report.rerank_window}")
    print(f"  recall@{RECALL_AT} per unit   "
          f"pre-rerank {u['recall_at_6']:.3f} ({u['recall_at_6_n']}/{u['units']})"
          f"   ->   POST-rerank {u['recall_at_6_reranked']:.3f} "
          f"({u['recall_at_6_reranked_n']}/{u['units']})")
    print(f"  MRR@{MRR_AT} per unit        pre {u['mrr_at_10']:.3f}"
          f"   ->   post {u['mrr_at_10_reranked']:.3f}")
    print(f"  coverage (reported, never gated)   "
          f"{u['targets_in_top_6']} -> {u['targets_in_top_6_reranked']} "
          f"of {u['targets_total']} targets in the top {RECALL_AT}")

    # C7 — the sequencing fix, and the reason BOTH lines are printed together.
    # Neither replaces the other: the pre-rerank figure is what every archived
    # run holds and what the archive is comparable in, and the post-rerank
    # figure is what the adopted configuration actually delivers.
    if "recall_at_6_via_original_reranked_n" in u:
        print(f"  recall@{RECALL_AT} VIA THE ORIGINAL TEXT   "
              f"pre-rerank {u['recall_at_6_via_original']:.3f} "
              f"({u['recall_at_6_via_original_n']}/{u['units']})"
              f"   ->   POST-rerank "
              f"{u['recall_at_6_via_original_reranked']:.3f} "
              f"({u['recall_at_6_via_original_reranked_n']}/{u['units']})")
        print("  These two are measured at DIFFERENT points, and they are "
              "printed together for\n  that reason. The collapse emits one row "
              "per section before the reranker\n  sees it, so reranking can "
              "rescue a record into the top 6 but can never\n  change which "
              "member of that section retrieval reached first: a record\n  "
              "entered through its English stays out of BOTH figures.")

    movers = [r for r in report.pairs
              if r.reranked and r.rank_reranked != r.rank]
    print()
    if not movers:
        print("  NOTHING MOVED. Per C3_START.md's third design constraint the "
              "first hypothesis is\n  the single-vendor blind spot — embeddings "
              "and reranking are both Voyage — and\n  not a mystery. It is a "
              "finding, and it is C2's cue.")
    else:
        print(f"  {len(movers)} pair(s) moved:")
        print(f"    {'pair':28s} {'rank':>5s} {'->':^4s} {'new':>5s}  effect")
        for r in sorted(movers, key=lambda r: (r.rank_reranked or 10**6)):
            if r.recall_at_6_reranked and not r.recall_at_6:
                effect = "ENTERS the top 6"
            elif r.recall_at_6 and not r.recall_at_6_reranked:
                effect = "LEAVES the top 6"
            else:
                effect = "no change to recall@6"
            print(f"    {r.id:28.28s} {(str(r.rank) if r.rank else 'none'):>5s} "
                  f"{'->':^4s} "
                  f"{(str(r.rank_reranked) if r.rank_reranked else 'none'):>5s}"
                  f"  {effect}")

    by_id = {r.id: r for r in report.pairs}
    flipped_units = [x for x in report.units
                     if x.reranked and x.recall_at_6_reranked != x.recall_at_6]
    lost = [x for x in flipped_units if not x.recall_at_6_reranked]
    if lost:
        print()
        print("  what the cross-encoder put above the units it displaced:")
        for x in lost:
            for pid in x.pairs:
                r = by_id.get(pid)
                if r and r.rerank_beaten_by:
                    print(f"    {pid:28.28s} rank {r.rank} -> {r.rank_reranked}")
                    for cid in r.rerank_beaten_by:
                        print(f"        {cid}")

    flipped = [x for x in report.units
               if x.reranked and x.recall_at_6_reranked != x.recall_at_6]
    if flipped:
        print()
        print(f"  {len(flipped)} UNIT(S) changed status — these are the ones the "
              f"gate counts:")
        for x in flipped:
            direction = "MISS -> hit" if x.recall_at_6_reranked else "hit -> MISS"
            print(f"    {x.unit:28.28s} {direction}   best rank "
                  f"{x.best_rank} -> {x.best_rank_reranked}")

    scored = [r for r in report.pairs if r.rerank_gap_vs_other_doc is not None]
    if scored:
        print()
        print(f"  rerank-score gap over {len(scored)} pair(s) with a scored "
              f"target:  gapDoc {_mean(r.rerank_gap_vs_other_doc for r in scored):+.4f}"
              f"   gapAny {_mean(r.rerank_gap_vs_other_chunk for r in scored):+.4f}")
    print("  Ruling 3: the gapDoc/gapAny in the cohort table above are EMBEDDING "
          "similarities,\n  measured PRE-rerank, and are the only ones comparable "
          "to the B2 baseline. The\n  rerank-score gap on this line is a "
          "different quantity under its own name and is\n  never compared to "
          "that baseline. Recall on this page is POST-rerank; the gap is not.\n"
          "  C3 cannot move the gap criterion at all — that is C2's, per ruling 5.")


def _print_fused(report: Report) -> None:
    """Ruling 14, and the whole point of it is the last two lines.

    G2 asks for a gap "wider than baseline", and the baseline is B2's gapDoc
    +0.0249 recorded at 57 chunks. This run is at 450, where the SAME
    configuration reads about +0.016. A fused gap that beats the historical
    number while sitting below the same-run single-variant arm is not evidence
    that C2 widened anything, and this function refuses to print it as though
    it were.
    """
    if not report.pairs_fused:
        return
    single, fused = report.aggregate, report.aggregate_fused
    us, uf = report.aggregate_units, report.aggregate_units_fused

    print()
    print("C2 — the two arms, same index, same day, same pairs (ruling 14)")
    print(f"{'':22s} {'recall@6':>10s} {'MRR@10':>8s} "
          f"{'gapDoc':>8s} {'gapAny':>8s}")
    for name, agg in (("single-variant", single), ("fused", fused)):
        print(f"  {name:20.20s} "
              f"{agg.get('recall_at_6_n', 0):3d}/{agg.get('pairs', 0):<6d} "
              f"{_fmt(agg.get('mrr_at_10'), 8)} "
              f"{_fmt(agg.get('mean_gap_vs_other_doc'), 8, 4)} "
              f"{_fmt(agg.get('mean_gap_vs_other_chunk'), 8, 4)}")

    print()
    print("  per unit — what G2's recall criterion reads")
    for name, agg in (("single-variant", us), ("fused", uf)):
        if not agg:
            continue
        for label, key in (("", "recall_at_6"),
                           ("collapsed", "recall_at_6_collapsed"),
                           ("reranked", "recall_at_6_reranked"),
                           ("via original, pre", "recall_at_6_via_original"),
                           ("via original, post",
                            "recall_at_6_via_original_reranked")):
            if f"{key}_n" not in agg:
                continue
            print(f"    {name:16.16s} {label:18.18s} "
                  f"{agg[f'{key}_n']:3d}/{agg.get('units', 0):<4d} "
                  f"{agg[key]:.3f}")

    # Per language, because the plan's own C2 instruction is that an aggregate
    # win which loses Chinese is a loss.
    print()
    print("  per expected language — recall@6, single -> fused")
    langs = sorted({r.expect_lang or "?" for r in report.pairs})
    by_id = {r.id: r for r in report.pairs_fused}
    for lang in langs:
        rows = [r for r in report.pairs if (r.expect_lang or "?") == lang]
        s = sum(1 for r in rows if r.recall_at_6)
        f = sum(1 for r in rows if by_id.get(r.id) and by_id[r.id].recall_at_6)
        flag = "  <- LOST" if f < s else ("  <- gained" if f > s else "")
        print(f"    {lang:10.10s} {s:2d}/{len(rows):<2d} -> {f:2d}/{len(rows):<2d}{flag}")

    won = [r.fused_from_lang for r in report.pairs_fused if r.fused_from_lang]
    from collections import Counter
    print()
    print(f"  the target's winning variant, per pair: {dict(Counter(won))}")
    if report.native_control:
        print("  RULING 15b CONTROL — findings, printed and never gated:")
        for row in report.native_control:
            for problem in row["problems"]:
                print(f"    {row['id']:28.28s} {problem}")
    else:
        print("  ruling 15b control: no native-language query moved or lost "
              "to a rendering")

    baseline = 0.0249
    sd = single.get("mean_gap_vs_other_doc")
    fd = fused.get("mean_gap_vs_other_doc")
    print()
    print(f"  GAP, the outstanding half of G2")
    print(f"    B2 baseline (57 chunks)      {baseline:+.4f}")
    print(f"    single-variant, this run     {sd:+.4f}" if sd is not None else
          "    single-variant, this run     none")
    print(f"    fused, this run              {fd:+.4f}" if fd is not None else
          "    fused, this run              none")
    if sd is not None and fd is not None:
        if fd <= sd:
            verdict = ("NOT a C2 win: the fused gap is not wider than the "
                       "same-run single-variant arm.")
        elif fd <= baseline:
            verdict = ("wider than the single-variant arm, but NOT wider than "
                       "the B2 baseline G2 names.")
        else:
            verdict = ("wider than BOTH the same-run single-variant arm and the "
                       "B2 baseline.")
        print(f"    -> {verdict}")
    print()
    print("  A translated query that succeeds proves the pipeline works, not "
          "that the retriever is cross-lingual.")


def archive(report: Report) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    # A reranked run is a different measurement from an unreranked one at the
    # same view, and the two must not be told apart only by opening them.
    suffix = "-collapsed" if report.collapsed else ""
    suffix += f"-reranked{report.rerank_window}" if report.reranked else ""
    path = RUNS_DIR / f"{report.timestamp}-{Path(report.view).name}{suffix}.json"
    payload = asdict(report)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--with-distractors", action="store_true",
                    help=f"read {VIEW_WITH_DISTRACTORS} instead of {VIEW_BASELINE} (B5)")
    ap.add_argument("--dry-run", action="store_true",
                    help="load the pairs and resolve targets against the "
                         "index; embed nothing. Still needs the database — for "
                         "a database-free check run eval.test_ranking_check.")
    ap.add_argument("--skip-check", action="store_true",
                    help="run against an index that does not match the seed "
                         "corpus. Recorded in the archived run.")
    ap.add_argument("--collapse", action="store_true",
                    help="C2a (ruling 8): return one row per aligned section, "
                         "as the ORIGINAL, instead of letting a passage compete "
                         "with its own translation. Recorded BESIDE rank; the "
                         "gaps are computed on the uncollapsed ranking.")
    ap.add_argument("--rerank", action="store_true",
                    help="C3: reorder the top --rerank-window candidates with "
                         "the cross-encoder. Recorded BESIDE rank; the gap is "
                         "unaffected by construction (ruling 3).")
    ap.add_argument("--rerank-window", type=int, default=None,
                    help="how many pre-rerank candidates go to the "
                         "cross-encoder (default 50). A different window is a "
                         "different measurement; it is archived with the run.")
    ap.add_argument("--rerank-pace", type=float, default=0.0,
                    help="seconds to leave between rerank calls. An account "
                         "with no payment method is held to 3 RPM / 10K TPM, "
                         "where a 50-document window needs about 30. Archived "
                         "with the run.")
    ap.add_argument("--rerank-tpm", type=float, default=0.0,
                    help="tokens-per-minute ceiling to pace against. Each call "
                         "is spaced by what the PREVIOUS one actually cost, "
                         "which the provider reports. 10000 is the no-payment-"
                         "method limit. Preferred over --rerank-pace, which is "
                         "a guess by construction.")
    ap.add_argument("--rerank-model", default=None,
                    help="gateway alias for the reranker (default rerank-2.5)")
    ap.add_argument("--fuse", nargs="?", const=str(_DEFAULT_RENDERINGS),
                    default=None, metavar="PATH",
                    help="C2 (ruling 13): also score every pair over its query "
                         "RENDERINGS, fused by max per candidate, and report "
                         "that arm beside the single-variant one (ruling 14). "
                         "Reads eval/gold/query_renderings.json unless a path "
                         "is given; the file's content hash is archived with "
                         "the run.")
    ap.add_argument("--allow-unresolvable", action="append", default=[],
                    metavar="PAIR_ID",
                    help="FINDING 12: proceed even though this gold pair does "
                         "not resolve against the index. Repeatable, and each "
                         "pair must be named — an unnamed one kills the run "
                         "before anything is embedded. Naming any pair archives "
                         "the run as NOT COMPARABLE, and naming a pair that "
                         "does resolve is itself an error.")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    view = VIEW_WITH_DISTRACTORS if args.with_distractors else VIEW_BASELINE
    if args.rerank_window is not None and args.rerank_window < RECALL_AT:
        raise SystemExit(
            f"--rerank-window {args.rerank_window} is smaller than recall@"
            f"{RECALL_AT}. A window that cannot contain the top 6 cannot change "
            f"the number the gate reads."
        )
    report = run(view, dry_run=args.dry_run, skip_check=args.skip_check,
                 collapse_sections=args.collapse,
                 rerank=args.rerank, rerank_window=args.rerank_window,
                 rerank_model=args.rerank_model, rerank_pace=args.rerank_pace,
                 rerank_tpm=args.rerank_tpm, fuse_renderings=args.fuse,
                 allow_unresolvable=set(args.allow_unresolvable))

    # ARCHIVE FIRST, then print. On 2026-08-16 a KeyError in `print_report`
    # killed the process before `archive()` ran and a twenty-six-minute run —
    # the first with both C2a and C3 on — was lost entirely. The archived run IS
    # the evidence; the terminal output is a rendering of it. Ordering these the
    # other way round made a formatting defect capable of destroying data.
    path = None
    if not args.dry_run:
        path = archive(report)

    if args.json:
        print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
    else:
        print_report(report)

    if path:
        print(f"\narchived: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
