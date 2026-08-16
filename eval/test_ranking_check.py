"""Offline checks for the W2a ranking gold set and its metrics.

No database, no gateway, no spend. Two halves:

1. The gold set is checked against the seed corpus on disk — every pair must
   resolve to exactly one chunk, of the expected document, in the expected
   language. This is the same resolution rule `run_ranking_check.py` applies
   against the index, run here against the source of truth, so a pair that has
   rotted is caught in a session that costs nothing rather than in the session
   that spends the batched embedding request.

2. The metrics are checked against a stub ranking with known answers. Every
   metric is exercised at a value where a plausible off-by-one would change it.

Run: python -m eval.test_ranking_check
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.goldset import GoldSetError, load_ranking_pairs  # noqa: E402
from eval.run_ranking_check import (  # noqa: E402
    MRR_AT,
    RECALL_AT,
    SEARCH_K,
    _search_depth,
    build_units,
    reachability_problems,
    score_pair,
    summarise,
    summarise_units,
)
from ingest.loader import load_corpus  # noqa: E402

PASS, FAIL = [], []


def check(name: str, ok: bool, detail: str = "") -> None:
    (PASS if ok else FAIL).append(name)
    print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f"\n       {detail}" if detail and not ok else ""))


@dataclass
class StubHit:
    chunk_id: str
    doc_id: str
    similarity: float
    # Block C3. `retrieve.rerank.pool_problems` reads these to assert that the
    # set handed to the cross-encoder still satisfies the pair's own filters.
    lang: str = "en"
    role: str = "original"
    text: str = ""


@dataclass
class StubPair:
    id: str = "stub"
    provenance: str = "authored"
    region: str = "arabia"
    query: str = "a stub query"
    query_lang: str = "en"
    expect_lang: str | None = None
    expect_doc: str = "doc-a"
    observed_chunk_id: str | None = None
    langs: list | None = None
    roles: list | None = None
    unit_id: str | None = None
    accept_aligned_translation: bool = False
    note: str = ""

    @property
    def unit(self) -> str:
        return self.unit_id or self.id


def ranking(*specs) -> list[StubHit]:
    """ranking(('doc-a::0', 0.9), ...) -> hits in the order given."""
    return [StubHit(cid, cid.split("::")[0], sim) for cid, sim in specs]


# --------------------------------------------------------------------------
# 1. The gold set against the corpus on disk
# --------------------------------------------------------------------------

def test_gold_set() -> None:
    pairs = load_ranking_pairs()
    chunks = [c for c in load_corpus().chunks if c.eligible_for_retrieval]

    check("gold set loads and clears W2a's floor of 20 pairs", len(pairs) >= 20,
          f"{len(pairs)} pairs")

    broken = []
    for p in pairs:
        hits = [c for c in chunks if p.expect_text_contains in c.text]
        if len(hits) != 1:
            broken.append(f"{p.id}: {len(hits)} chunk(s) contain its characters")
        elif hits[0].doc_id != p.expect_doc:
            broken.append(f"{p.id}: characters live in {hits[0].doc_id}, not {p.expect_doc}")
        elif p.expect_lang and hits[0].lang != p.expect_lang:
            broken.append(f"{p.id}: resolves to lang '{hits[0].lang}', expected '{p.expect_lang}'")
    check("every pair resolves to exactly one chunk of its expected document",
          not broken, "; ".join(broken))

    # A pair whose characters appear in two chunks does not identify a passage,
    # and a recall over an ambiguous target is a number about nothing. This is
    # the check that caught four such pairs when the file was first written.
    regions = {p.region for p in pairs}
    check("pairs span all seven regions", len(regions) == 7, f"{sorted(regions)}")

    langs = {p.expect_lang for p in pairs if p.expect_lang}
    check("pairs span more than one non-English target language",
          len(langs - {"en"}) >= 5, f"{sorted(langs)}")

    # 'a gold set that is 15 Greek pairs measures Greek' — PHASE2_PLAN.md B1.
    biggest = max(sum(1 for p in pairs if p.expect_lang == l) for l in langs)
    check("no single target language is more than half the set",
          biggest * 2 <= len(pairs), f"largest language cohort is {biggest}/{len(pairs)}")

    cohorts = {p.provenance for p in pairs}
    check("more than one provenance cohort is present", len(cohorts) > 1, f"{sorted(cohorts)}")
    non_archive = sum(1 for p in pairs if p.provenance != "archived_answer")
    check("a majority of pairs were NOT mined from retrieval's own output",
          non_archive * 2 > len(pairs),
          f"only {non_archive}/{len(pairs)} pairs are independent of past rankings")

    # Block C ruling 1. The denominator of the gate is written down here, in a
    # test, because "29 units" was the arithmetic the plan got wrong — it
    # collapsed one shared query and left the other expanded, and nothing in the
    # repository would have contradicted it.
    units = {}
    for p in pairs:
        units.setdefault(p.unit, []).append(p.id)
    multi = {u: ids for u, ids in units.items() if len(ids) > 1}
    check("the gate's denominator is units, and there are fewer of them than pairs",
          len(units) < len(pairs),
          f"{len(units)} units over {len(pairs)} pairs")
    check("every multi-target unit is declared, and there are two of them",
          sorted(multi) == ["china-describes-rome", "muziris-cargo"],
          f"{sorted(multi)}")

    # Block C ruling 2, scoped as it was ruled: the four translation_case pairs
    # and nothing else. If this ever grows, it grew by an edit to the gold file.
    accepts = sorted(p.id for p in pairs if p.accept_aligned_translation)
    check("only the four translation_case pairs accept an aligned translation",
          len(accepts) == 4
          and all(p.provenance == "translation_case"
                  for p in pairs if p.accept_aligned_translation),
          f"{accepts}")


def test_loader_is_strict() -> None:
    """The whole reason this data goes through goldset.py and not json.load."""
    import json
    import tempfile

    base = json.loads((Path(__file__).parent / "gold" / "ranking_pairs.json").read_text(encoding="utf-8"))

    def load_variant(mutate) -> Exception | None:
        data = json.loads(json.dumps(base))
        mutate(data)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
            path = Path(fh.name)
        try:
            load_ranking_pairs(path)
            return None
        except GoldSetError as exc:
            return exc
        finally:
            path.unlink(missing_ok=True)

    def misspell(d):
        # An EXTRA key beside the real one, not a renamed required key. A
        # renamed required key is caught by the missing-key rule, so a variant
        # built that way would pass even with unknown-key checking removed —
        # which is what this assertion is meant to be about.
        d["pairs"][0]["expect_contains"] = "already asserted elsewhere"

    check("a misspelled key is a load-time error, not a weaker pair",
          load_variant(misspell) is not None)

    check("an empty expect_text_contains is rejected",
          load_variant(lambda d: d["pairs"][0].__setitem__("expect_text_contains", "")) is not None)

    check("a duplicate pair id is rejected",
          load_variant(lambda d: d["pairs"].append(dict(d["pairs"][0]))) is not None)

    check("an unrecognised provenance is rejected",
          load_variant(lambda d: d["pairs"][0].__setitem__("provenance", "vibes")) is not None)

    def strand_a_pair(d):
        for p in d["pairs"]:
            if p.get("pair"):
                p.pop("pair")
                break
    check("a paired pair with no partner is rejected",
          load_variant(strand_a_pair) is not None)

    def one_per_region(d):
        # Seven pairs, one per region, none of them half of a paired pair — so
        # the region rule and the partner rule both still pass and the ONLY
        # thing that can reject this variant is the twenty-pair floor. Trimming
        # to the first ten instead would also drop three regions, and the
        # variant would keep failing for a reason that is not the one under
        # test: an assertion that passes for the wrong reason proves nothing.
        kept, seen = [], set()
        for p in d["pairs"]:
            if p.get("pair") or p["region"] in seen:
                continue
            seen.add(p["region"])
            kept.append(p)
        d["pairs"] = kept
    check("a gold set below twenty pairs is rejected",
          load_variant(one_per_region) is not None)

    def drop_a_region(d):
        d["pairs"] = [p for p in d["pairs"] if p["region"] != "southeast_asia"]
    check("a gold set missing a region is rejected",
          load_variant(drop_a_region) is not None)

    def contradict_pool(d):
        for p in d["pairs"]:
            if p.get("lang_pool"):
                p["expect_lang"] = "en"   # excluded by the non_english pool
                break
    check("a pair whose expect_lang is excluded by its own pool is rejected",
          load_variant(contradict_pool) is not None)

    # ------------------------------------------------------------------
    # Block C ruling 1, both directions. Each of these moves the gate's
    # denominator, which is the one number in the whole check that decides
    # whether W3 starts.
    # ------------------------------------------------------------------
    def unit_over_two_questions(d):
        for p in d["pairs"]:
            if p.get("unit_id") == "muziris-cargo":
                p["query"] = "What did ships carry from Barygaza?"
                break
    check("a unit grouping two different questions is rejected",
          load_variant(unit_over_two_questions) is not None)

    def undeclared_shared_query(d):
        for p in d["pairs"]:
            if p.get("unit_id") == "muziris-cargo":
                p.pop("unit_id")
                break
    check("a pair sharing a query but declaring no unit is rejected",
          load_variant(undeclared_shared_query) is not None,
          "this is the silent one: it adds a unit to the denominator and "
          "nothing else in the run would look wrong")

    check("accept_aligned_translation must be a boolean, not a truthy string",
          load_variant(lambda d: d["pairs"][0].__setitem__(
              "accept_aligned_translation", "yes")) is not None)

    def accept_on_english_target(d):
        for p in d["pairs"]:
            if p["expect_lang"] == "en" if "expect_lang" in p else False:
                p["accept_aligned_translation"] = True
                break
    check("accepting an aligned translation of an English target is rejected",
          load_variant(accept_on_english_target) is not None)


# --------------------------------------------------------------------------
# 2. The metrics against a stub ranking
# --------------------------------------------------------------------------

def test_metrics() -> None:
    p = StubPair()

    # A sibling of the expected document sits ABOVE the target on purpose. With
    # the target on top of its own document the two gaps take the same value by
    # accident, and the assertion that they differ cannot fail — the first draft
    # of this file was written that way and scripts/mutate_ranking.py caught it.
    hits = ranking(("doc-a::1", 0.95), ("doc-b::0", 0.90), ("doc-a::0", 0.80),
                   ("doc-c::0", 0.60), ("doc-d::0", 0.50), ("doc-e::0", 0.40),
                   ("doc-f::0", 0.30))
    r = score_pair(p, hits, "doc-a::0")
    check("rank is 1-indexed", r.rank == 3, f"rank={r.rank}")
    check("MRR@10 is 1/rank", abs(r.rr_at_10 - 1 / 3) < 1e-9, f"{r.rr_at_10}")
    check("gap vs other DOC skips same-document siblings",
          abs(r.gap_vs_other_doc - (0.80 - 0.90)) < 1e-9, f"{r.gap_vs_other_doc}")
    check("gap vs any other CHUNK does not skip siblings",
          abs(r.gap_vs_other_chunk - (0.80 - 0.95)) < 1e-9, f"{r.gap_vs_other_chunk}")
    check("top1_to_rank6 is the spread over the first six hits",
          abs(r.top1_to_rank6 - (0.95 - 0.40)) < 1e-9, f"{r.top1_to_rank6}")

    # The two gaps must be able to disagree, or reporting both is decoration.
    hits = ranking(("doc-a::1", 0.95), ("doc-a::0", 0.80), ("doc-b::0", 0.50))
    r = score_pair(p, hits, "doc-a::0")
    check("a sibling outranking the target shows in gapAny but not gapDoc",
          abs(r.gap_vs_other_chunk - (0.80 - 0.95)) < 1e-9
          and abs(r.gap_vs_other_doc - (0.80 - 0.50)) < 1e-9,
          f"any={r.gap_vs_other_chunk} doc={r.gap_vs_other_doc}")
    # ...and each gap must NAME the chunk it was measured against. Block B
    # recorded both numbers and neither identity, so the one structural claim
    # made about gapAny — that a translation_case target is beaten by its own
    # document's English — could not be checked against either archived run.
    check("each gap names the chunk it was measured against",
          r.best_other_chunk_id == "doc-a::1"
          and r.best_other_doc_chunk_id == "doc-b::0",
          f"any={r.best_other_chunk_id} doc={r.best_other_doc_chunk_id}")
    check("a target with nothing to compare against names nothing",
          score_pair(p, ranking(("doc-a::0", 0.9)), "doc-a::0")
          .best_other_chunk_id is None)

    # recall@6 must be exclusive at the boundary in the right direction.
    at6 = ranking(*[(f"doc-x::{i}", 0.9 - i / 100) for i in range(5)],
                  ("doc-a::0", 0.4), ("doc-y::0", 0.3))
    check(f"a target at rank {RECALL_AT} counts as recall@{RECALL_AT}",
          score_pair(p, at6, "doc-a::0").recall_at_6)
    at7 = ranking(*[(f"doc-x::{i}", 0.9 - i / 100) for i in range(6)],
                  ("doc-a::0", 0.3))
    check(f"a target at rank {RECALL_AT + 1} does not",
          not score_pair(p, at7, "doc-a::0").recall_at_6)

    deep = ranking(*[(f"doc-x::{i}", 0.9 - i / 100) for i in range(10)],
                   ("doc-a::0", 0.1))
    r = score_pair(p, deep, "doc-a::0")
    check(f"a target past rank {MRR_AT} scores 0 reciprocal rank, not 1/rank",
          r.rr_at_10 == 0.0 and r.rank == 11, f"rr={r.rr_at_10} rank={r.rank}")

    missing = ranking(("doc-x::0", 0.9), ("doc-y::0", 0.8))
    r = score_pair(p, missing, "doc-a::0")
    check("a target absent from the results is rank None, not rank 0",
          r.rank is None and r.rr_at_10 == 0.0 and not r.recall_at_6)
    check("an absent target has no similarity and therefore no gap",
          r.sim_target is None and r.gap_vs_other_doc is None)

    # An absent target must not drag the mean gap toward zero — a missing
    # measurement and a zero measurement are different things, and averaging
    # them together is how a failure looks like mediocrity.
    good = score_pair(p, ranking(("doc-a::0", 0.9), ("doc-b::0", 0.5)), "doc-a::0")
    agg = summarise([good, r])
    check("aggregate gap averages only the pairs that have one",
          abs(agg["mean_gap_vs_other_doc"] - 0.4) < 1e-9,
          f"{agg['mean_gap_vs_other_doc']}")
    check("aggregate recall counts the missing pair as a miss",
          # .get(), not [] — a KeyError here would abort the suite before
          # test_labels_track_their_thresholds() runs, hiding the guard that
          # owns this defect behind a crash in an unrelated assertion. Same
          # shape as Block 0's truncated test run.
          abs(agg["recall_at_6"] - 0.5) < 1e-9 and agg.get("unranked") == 1,
          f"{agg}")


def test_search_depth_is_the_whole_view() -> None:
    """The gap means are only unbiased if nothing is out of reach.

    A fixed depth cannot be right at more than one rung of the W2b curve:
    k=20 biased the 57-chunk baseline over 26 of 32 pairs, and k=50 would have
    biased the 450-chunk rung. `not_in_top_20` was also hardcoded and survived
    k moving to 50 — a metric whose NAME asserted a threshold it was not
    measured at.
    """
    check("no fixed search depth is compiled in", SEARCH_K is None,
          f"SEARCH_K={SEARCH_K}")
    for n in (57, 150, 450):
        check(f"an index of {n} chunks is ranked to depth {n}",
              _search_depth(n) == n, f"got {_search_depth(n)}")

    p = StubPair()
    agg = summarise([score_pair(p, ranking(("doc-x::0", 0.9)), "doc-a::0")])
    check("the unranked count carries no threshold in its name",
          "unranked" in agg and not any(k.startswith("not_in_top") for k in agg),
          f"keys: {sorted(agg)}")


def test_units_are_scored_once() -> None:
    """Block C ruling 1: one query with N acceptable targets is ONE unit."""
    # The Muziris shape, in miniature: three pairs, one query, one of them in
    # the top 6 and two of them nowhere near it.
    hits = ranking(("doc-x::0", 0.9), ("doc-a::0", 0.8),
                   *[(f"doc-p::{i}", 0.5 - i / 100) for i in range(40)],
                   ("doc-b::0", 0.05), ("doc-c::0", 0.04))
    members = [
        score_pair(StubPair(id="m-1", unit_id="m", expect_doc="doc-a"), hits, "doc-a::0"),
        score_pair(StubPair(id="m-2", unit_id="m", expect_doc="doc-b"), hits, "doc-b::0"),
        score_pair(StubPair(id="m-3", unit_id="m", expect_doc="doc-c"), hits, "doc-c::0"),
    ]
    units = build_units(members)
    check("three pairs sharing a unit_id are one unit",
          len(units) == 1 and units[0].coverage_total == 3,
          f"{[u.unit for u in units]}")
    check("the unit is scored on its BEST acceptable target",
          units[0].best_rank == 2 and units[0].recall_at_6
          and units[0].best_pair == "m-1",
          f"best={units[0].best_rank} pair={units[0].best_pair}")
    # The whole cost of the ruling in one assertion: the unit passes while two
    # of its three targets are out of reach, and coverage is what says so.
    check("coverage reports the targets the unit does NOT reach",
          units[0].coverage_n == 1 and abs(units[0].coverage - 1 / 3) < 1e-9,
          f"{units[0].coverage_n}/{units[0].coverage_total}")

    solo = score_pair(StubPair(id="alone"), hits, "doc-a::0")
    check("a pair declaring no unit_id is its own unit",
          [u.unit for u in build_units([solo])] == ["alone"])

    agg = summarise_units(build_units(members + [solo]))
    check("the unit aggregate counts units, not pairs",
          agg["units"] == 2 and agg["pairs"] == 4,
          f"{agg['units']} units / {agg['pairs']} pairs")
    check("the unit aggregate reports coverage over every target",
          agg["targets_in_top_6"] == 2 and agg["targets_total"] == 4,
          f"{agg['targets_in_top_6']}/{agg['targets_total']}")
    check("multi-target coverage is reported separately from the mean",
          agg["multi_target_units"] == 1
          and abs(agg["multi_target_coverage"] - 1 / 3) < 1e-9,
          f"{agg['multi_target_coverage']}")


def test_aligned_alternate_is_a_second_acceptable_target() -> None:
    """Block C ruling 2, and the line it must not cross.

    The alternate makes a pair reachable through its document's own English of
    the SAME section. It must not quietly redefine `rank`, which is the number
    the B2 baseline recorded and every gap is computed from.
    """
    hits = ranking(("doc-a::t::1", 0.9), ("doc-b::0", 0.7),
                   *[(f"doc-p::{i}", 0.6 - i / 100) for i in range(8)],
                   ("doc-a::o::1", 0.2))
    p = StubPair(id="tc", accept_aligned_translation=True)
    strict = score_pair(p, hits, "doc-a::o::1")
    check("without an alternate the pair is a miss at its own rank",
          strict.rank == 11 and not strict.recall_at_6
          and strict.rank_accepted == 11)

    admitted = score_pair(p, hits, "doc-a::o::1",
                          alternates=["doc-a::t::1"], alternate_ground="section")
    check("an admitted alternate reaches the target the original could not",
          admitted.rank_accepted == 1 and admitted.recall_at_6_accepted,
          f"rank_accepted={admitted.rank_accepted}")
    check("the alternate does NOT move `rank`, which the baseline is denominated in",
          admitted.rank == 11 and not admitted.recall_at_6,
          f"rank={admitted.rank} recall={admitted.recall_at_6}")
    check("the run records what was accepted and on what ground",
          admitted.accepted_chunk_ids == ["doc-a::o::1", "doc-a::t::1"]
          and admitted.alternate_ground == "section",
          f"{admitted.accepted_chunk_ids} {admitted.alternate_ground}")

    # Asked for and refused: align reported a ground weaker than "section", so
    # resolve_alternates admits nothing. The pair must be unchanged, and the run
    # must still say the question was asked — "none admitted" and "none asked
    # for" are different facts.
    refused = score_pair(p, hits, "doc-a::o::1",
                         alternates=[], alternate_ground="index")
    check("an alternate refused on a weak alignment ground changes nothing",
          refused.rank_accepted == 11 and not refused.recall_at_6_accepted
          and refused.alternate_ground == "index")


def test_a_run_must_reach_the_index_it_names() -> None:
    """The 2026-08-14 defect, as an assertion.

    `--with-distractors` counted 450 rows for its header and ranked against a
    57-row view, and every individual number was correct. Nothing in the run
    compared them, so the report printed `index=450 depth=450` over a table of
    57-chunk ranks and the whole W2b curve turned out to have been measurable
    only while containment was broken.
    """
    from retrieve.search import SEARCH_SQL, SEARCHABLE_VIEWS, search_sql

    ok = reachability_problems("retrievable_chunks_with_distractors", 450, 450)
    check("a search that reaches every row of its view is silent", ok == [])

    short = reachability_problems("retrievable_chunks_with_distractors", 450, 57)
    check("a search that cannot reach the whole view is a loud failure",
          len(short) == 1 and "450" in short[0] and "57" in short[0],
          f"{short}")
    check("the complaint names the view and how to fix it",
          "retrievable_chunks_with_distractors" in short[0]
          and "view=" in short[0])

    # The view reaches SQL by interpolation, so it is checked and not trusted.
    check("both real views are searchable",
          SEARCHABLE_VIEWS == {"retrievable_chunks",
                               "retrievable_chunks_with_distractors"},
          f"{sorted(SEARCHABLE_VIEWS)}")
    check("the default statement still reads the contained view — the answer "
          "path gets containment from saying nothing",
          "FROM retrievable_chunks\n" in SEARCH_SQL)
    check("the distractor view can be asked for explicitly",
          "FROM retrievable_chunks_with_distractors\n"
          in search_sql("retrievable_chunks_with_distractors"))
    try:
        search_sql("chunks; DROP TABLE documents")
        refused = False
    except ValueError:
        refused = True
    check("an unknown view name is refused rather than interpolated", refused)


class _StubCursor:
    def __init__(self, rows): self.rows = rows
    def __enter__(self): return self
    def __exit__(self, *exc): return False
    def execute(self, *args, **kwargs): pass
    def fetchall(self): return self.rows


class _StubConn:
    """Enough of a connection for `resolve_alternates`, and no database.

    The alternate is computed from `answer.align`, so the only thing the
    database contributes is the rows. Stubbing them keeps this rule — which
    decides whether four gold pairs become reachable — testable in the session
    that costs nothing, rather than only in the one that spends.
    """
    def __init__(self, rows): self.rows = rows
    def cursor(self): return _StubCursor(self.rows)


def test_alternates_are_admitted_only_on_section_alignment() -> None:
    from eval.run_ranking_check import resolve_alternates

    p = StubPair(id="tc", expect_doc="d", accept_aligned_translation=True)
    resolved = {"tc": ("d::o::0", "4. Μετὰ δὲ τὴν Πτολεμαΐδα")}

    # §4's English runs to two chunks and only the first carries the marker —
    # the A4 shape that align.py's label inheritance was written for. BOTH
    # members must be admitted, or a quotation from the second half of a section
    # is unreachable through an alternate that claims to cover the section.
    aligned = _StubConn([
        ("d", "d::o::0", "original", "4. Μετὰ δὲ τὴν Πτολεμαΐδα"),
        ("d", "d::o::1", "original", "6. Προχωρεῖ δὲ εἰς τοὺς τόπους"),
        ("d", "d::t::0", "translation", "§4 Below Ptolemais of the Hunts"),
        ("d", "d::t::1", "translation", "Opposite Mountain Island, twenty stadia"),
        ("d", "d::t::2", "translation", "§6 There are imported into these places"),
    ])
    alts, ground = resolve_alternates(aligned, [p], "v", resolved)["tc"]
    check("a section-aligned translation is admitted, every member of it",
          alts == ["d::t::0", "d::t::1"] and ground == "section",
          f"{alts} ground={ground}")

    # Same counts, no markers: align calls this "index", which it labels as the
    # weaker ground because two texts numbered independently pair by coincidence
    # of counting. Admitting an alternate on that would accept a NEIGHBOURING
    # section — the thing ruling 2 says is still a miss.
    positional = _StubConn([
        ("d", "d::o::0", "original", "4. Μετὰ δὲ τὴν Πτολεμαΐδα"),
        ("d", "d::o::1", "original", "6. Προχωρεῖ δὲ εἰς τοὺς τόπους"),
        ("d", "d::t::0", "translation", "Below Ptolemais of the Hunts"),
        ("d", "d::t::1", "translation", "There are imported into these places"),
    ])
    alts, ground = resolve_alternates(positional, [p], "v", resolved)["tc"]
    check("an alternate is NOT admitted on positional alignment",
          alts == [] and ground == "index", f"{alts} ground={ground}")
    check("the run still records that the alternate was asked for",
          ground is not None)

    silent = StubPair(id="plain", expect_doc="d")
    check("a pair that never declared the ruling is not given an alternate",
          "plain" not in resolve_alternates(aligned, [silent], "v",
                                            {"plain": ("d::o::0", "")}))


def test_observed_chunk_id_is_never_the_target() -> None:
    """The archived id is provenance. If it were the target, the check would
    measure the wrong passage the moment a document is re-chunked — which
    africa-03-periplus-adulis did on 2026-08-13."""
    p = StubPair(observed_chunk_id="doc-a::9")
    hits = ranking(("doc-a::0", 0.9), ("doc-a::9", 0.8), ("doc-b::0", 0.7))
    r = score_pair(p, hits, "doc-a::0")
    check("scoring uses the resolved chunk, not the archived observed_chunk_id",
          r.rank == 1 and r.resolved_chunk_id == "doc-a::0")
    check("a drifted observed_chunk_id is reported, not acted on",
          r.observed_chunk_matches_resolved is False)


def _rr_pair(**kw):
    """A PairResult already scored pre-rerank, so a mutation that reaches
    backwards into the baseline shows up as a changed field rather than as a
    missing one."""
    from eval.run_ranking_check import PairResult

    base = dict(
        id="p", provenance="authored", region="arabia", query_lang="en",
        expect_lang=None, expect_doc="doc-a", resolved_chunk_id="doc-a::0",
        rank=4, recall_at_6=True, rr_at_10=0.25, sim_target=0.51,
        sim_best_other_doc=0.44, sim_best_other_chunk=0.46,
        gap_vs_other_doc=0.07, gap_vs_other_chunk=0.05, top1_to_rank6=0.13,
        top_doc="doc-b", unit="u", accepted_chunk_ids=["doc-a::0"],
    )
    base.update(kw)
    return PairResult(**base)


def test_rerank_is_recorded_beside_the_baseline_and_never_over_it() -> None:
    """Block C3. The cross-encoder is a recall intervention, and the two things
    that could make its number meaningless are both structural: overwriting a
    quantity the baseline is denominated in, and reordering a pool the pair's
    own filters excluded. Both are asserted here, offline."""
    from eval.run_ranking_check import apply_rerank
    from retrieve.rerank import (
        RerankError, parse_rerank_payload, pool_problems, rank_of, reorder,
        scores_by_chunk,
    )

    hits = ranking(*[(f"doc-{'ab'[i % 2]}::{i}", 0.9 - i / 100) for i in range(12)])
    scored = [(3, 0.99), (0, 0.80), (1, 0.80), (2, 0.10)]

    order = reorder(hits, scored, 4)
    check("the reranked ordering is a permutation, not a truncation",
          len(order) == len(hits)
          and {h.chunk_id for h in order} == {h.chunk_id for h in hits},
          f"{len(order)} of {len(hits)}")
    check("a candidate below the rerank window keeps its pre-rerank position",
          rank_of(order, ["doc-b::11"]) == 12,
          f"rank {rank_of(order, ['doc-b::11'])}")
    check("the tail below the window keeps its pre-rerank ORDER",
          [h.chunk_id for h in order[4:]] == [h.chunk_id for h in hits[4:]])
    check("rerank ties break on the pre-rerank order, not arbitrarily",
          [i for i, _ in parse_rerank_payload(
              {"results": [{"index": 1, "relevance_score": 0.8},
                           {"index": 0, "relevance_score": 0.8}]}, 2)] == [0, 1])

    r = _rr_pair()
    apply_rerank(r, order, scores_by_chunk(hits, scored, 4), 4, "doc-a")
    check("reranking does not touch `rank`, which every gap is denominated in",
          (r.rank, r.recall_at_6, r.gap_vs_other_doc, r.gap_vs_other_chunk)
          == (4, True, 0.07, 0.05),
          f"rank={r.rank} gapDoc={r.gap_vs_other_doc}")
    check("the post-rerank position is recorded under its own name",
          r.rank_reranked == 2 and r.reranked and r.rerank_window == 4,
          f"rank_reranked={r.rank_reranked} window={r.rerank_window}")
    check("the run records WHAT the cross-encoder put above the target",
          r.rerank_top_chunk_ids == [h.chunk_id for h in order[:RECALL_AT]]
          and r.rerank_beaten_by == ["doc-b::3"],
          f"top={r.rerank_top_chunk_ids} beaten_by={r.rerank_beaten_by}")
    check("a target the reranker put first is beaten by nothing",
          _rr_pair(resolved_chunk_id="doc-b::3",
                   accepted_chunk_ids=["doc-b::3"]) is not None
          and apply_rerank(_rr_pair(resolved_chunk_id="doc-b::3",
                                    accepted_chunk_ids=["doc-b::3"]),
                           order, scores_by_chunk(hits, scored, 4), 4,
                           "doc-b").rerank_beaten_by == [])
    check("the reranker-score gap is recorded under its own name",
          r.rerank_gap_vs_other_doc is not None
          and r.rerank_score_target == 0.80)

    # A target the window never reached: `muziris-cargo-akananuru` at 309 is the
    # real instance. It keeps a rank, and it has no reranker score — 0.0 would
    # sort and average as though the model had judged it.
    deep = _rr_pair(resolved_chunk_id="doc-b::11", rank=12,
                    accepted_chunk_ids=["doc-b::11"])
    apply_rerank(deep, order, scores_by_chunk(hits, scored, 4), 4, "doc-a")
    check("a target below the window has no reranker score, not a zero",
          deep.rerank_score_target is None
          and deep.rerank_gap_vs_other_doc is None,
          f"score={deep.rerank_score_target}")
    check("a target below the window still has a post-rerank rank",
          deep.rank_reranked == 12)

    for label, payload in (
        ("out of the submitted set", {"results": [{"index": 9, "relevance_score": 1.0}]}),
        ("named twice", {"results": [{"index": 0, "relevance_score": 1.0},
                                     {"index": 0, "relevance_score": 0.5}]}),
        ("carrying no relevance_score", {"results": [{"index": 0}]}),
    ):
        try:
            parse_rerank_payload(payload, 2)
            refused = False
        except RerankError:
            refused = True
        check(f"a rerank result {label} is refused", refused)

    try:
        reorder(hits, scored[:2], 4)
        refused = False
    except RerankError:
        refused = True
    check("a partial rerank response is refused rather than reordered", refused)

    # Design constraint 1. Five pairs restrict candidates to non-English before
    # ranking, and that filter is the only thing making them cross-lingual tests.
    mixed = [StubHit("d::t::0", "d", 0.9, lang="en"),
             StubHit("d::o::0", "d", 0.8, lang="grc")]
    check("a pool that violates the pair's own lang filter is a loud failure",
          bool(pool_problems(mixed, langs=["grc"])),
          f"{pool_problems(mixed, langs=['grc'])}")
    check("a correctly filtered pool passes silently",
          pool_problems(mixed[1:], langs=["grc"]) == []
          and pool_problems(mixed, langs=None) == [])


def test_the_rerank_transport_fails_loudly_and_never_silently() -> None:
    """The route is an OBSERVATION, not a citation. LiteLLM has exposed rerank
    at both `/v1/rerank` and `/rerank`; the client tries them in order and
    records which answered, so the archived run says where its numbers came
    from. Exercised with an injected transport — no gateway, no key, no spend."""
    from retrieve.rerank import RerankError, rerank_documents

    calls = []

    def post_404_then_ok(url, key, body, timeout):
        calls.append(url)
        if url.endswith("/v1/rerank"):
            return 404, {"error": "not found"}
        return 200, {"results": [{"index": 1, "relevance_score": 0.9},
                                 {"index": 0, "relevance_score": 0.2}],
                     "meta": {"tokens": {"total_tokens": 314}}}

    # Caught, not allowed to propagate. A check that dies instead of failing
    # takes every check after it with it, and `scripts/mutate_ranking.py` reads
    # FAIL lines from stdout — so a crashed suite reports NO failures and the
    # mutation that caused it is recorded as unwatched. Found on 2026-08-16 by
    # the "only the first rerank route is ever tried" mutation.
    try:
        r = rerank_documents("q", ["a", "b"], base_url="http://x", api_key="k",
                             post=post_404_then_ok, sleep=lambda _s: None)
    except RerankError:
        r = None
    check("a 404 on the first rerank route falls through to the second",
          r is not None and r.path == "/rerank"
          and [c.split("http://x")[1] for c in calls] == ["/v1/rerank", "/rerank"],
          f"path={r and r.path} calls={calls}")
    check("the run records the route that answered and the tokens it reported",
          r is not None and r.scored == [(1, 0.9), (0, 0.2)]
          and r.total_tokens == 314)

    def post_500(url, key, body, timeout):
        return 500, {"error": "upstream exploded"}

    try:
        rerank_documents("q", ["a"], base_url="http://x", post=post_500,
                         sleep=lambda _s: None)
        loud = False
    except RerankError as exc:
        loud = "500" in str(exc) and "gateway" in str(exc).lower()
    check("a gateway refusal is raised, never scored as an empty ranking", loud)

    def post_404_always(url, key, body, timeout):
        return 404, {"error": "not found"}

    try:
        rerank_documents("q", ["a"], base_url="http://x", post=post_404_always,
                         sleep=lambda _s: None)
        loud = False
    except RerankError as exc:
        loud = "no rerank route answered" in str(exc)
    check("no route answering is a failure, not a silent unreranked run", loud)

    sleeps = []

    def post_429_then_ok(url, key, body, timeout):
        if len(sleeps) < 1:
            return 429, {"error": "rate limited"}
        return 200, {"results": [{"index": 0, "relevance_score": 0.5}]}

    r = rerank_documents("q", ["a"], base_url="http://x",
                         post=post_429_then_ok, sleep=sleeps.append)
    check("a rate-limited rerank waits a full window and retries",
          r.retries == 1 and sleeps and sleeps[0] >= 20, f"{sleeps}")


def test_the_paced_client_waits_before_the_call_not_after_the_refusal() -> None:
    """This account has no payment method, so Voyage holds it to 3 RPM / 10K TPM
    — the same throttle the embedding path batches around. Rerank cannot batch
    queries, so spacing is the only lever, and spacing that only happens after a
    429 spends the retry budget rediscovering a known limit every call."""
    from retrieve import rerank as rr
    from retrieve.rerank import pace, rerank_documents

    rr._LAST_CALL_AT[0] = None
    rr._LAST_TOKENS[0] = None
    check("the first call of a process is never delayed", pace(1000.0, 30.0) == 0.0)
    rr._LAST_CALL_AT[0] = 1000.0
    check("the wait is the remainder of the interval, not the time already spent",
          pace(1010.0, 30.0) == 20.0, f"{pace(1010.0, 30.0)}")
    check("an interval already elapsed costs nothing",
          pace(1099.0, 30.0) == 0.0)
    check("an unpaced client is not slowed down at all",
          pace(1000.5, 0.0) == 0.0)

    # Token-aware pacing. The estimate of what a 50-document window costs has
    # been wrong twice — once from a docs table, once from the seed corpus on
    # disk. What the provider hands back with each response is not an estimate,
    # so the NEXT call is spaced by what the LAST one actually cost.
    rr._LAST_CALL_AT[0] = 1000.0
    check("the next call is spaced by the tokens the last one actually cost",
          pace(1000.0, 0.0, last_tokens=6000, tpm_budget=10000) == 36.0,
          f"{pace(1000.0, 0.0, last_tokens=6000, tpm_budget=10000)}")
    check("the longer of the two pacing constraints wins",
          pace(1000.0, 45.0, last_tokens=6000, tpm_budget=10000) == 45.0
          and pace(1000.0, 20.0, last_tokens=6000, tpm_budget=10000) == 36.0)
    check("a call the provider did not cost falls back to the interval",
          pace(1000.0, 20.0, last_tokens=None, tpm_budget=10000) == 20.0)
    check("no budget means no token pacing, however large the last call",
          pace(1000.0, 0.0, last_tokens=999999, tpm_budget=0) == 0.0)

    # End to end, with an injected clock and sleep: no gateway, no waiting.
    slept, now = [], [500.0]
    def clock():
        return now[0]
    def sleeper(seconds):
        slept.append(seconds)
        now[0] += seconds
    def ok(url, key, body, timeout):
        now[0] += 1.0
        return 200, {"results": [{"index": 0, "relevance_score": 0.5}]}

    rr._LAST_CALL_AT[0] = None
    for _ in range(2):
        rerank_documents("q", ["a"], base_url="http://x", post=ok,
                         sleep=sleeper, clock=clock, min_interval=30.0)
    check("a paced client waits before the call, not after it is refused",
          slept == [29.0], f"slept={slept}")

def test_post_rerank_units_are_scored_over_the_whole_gate() -> None:
    """The denominator is the thing the plan already got wrong once. G2 reads
    29/30, so a post-rerank recall averaged over the units that happened to be
    reranked would be a number about a smaller gate than the one it names."""
    from eval.run_ranking_check import build_units, summarise_units

    def pair(pid, unit, rank_acc, rank_rr, reranked=True):
        return _rr_pair(
            id=pid, unit=unit, resolved_chunk_id=f"{pid}::0",
            accepted_chunk_ids=[f"{pid}::0"],
            rank=rank_acc, rank_accepted=rank_acc,
            recall_at_6_accepted=bool(rank_acc and rank_acc <= RECALL_AT),
            reranked=reranked, rank_accepted_reranked=rank_rr,
            recall_at_6_accepted_reranked=bool(rank_rr and rank_rr <= RECALL_AT),
        )

    # One unit with two targets: 15 -> 2 and 35 -> 9. Best is what scores.
    units = build_units([
        pair("a", "u1", 15, 2), pair("a2", "u1", 35, 9),
        pair("b", "u2", 17, 21),
        pair("c", "u3", 3, 3, reranked=False),
        # u4 is MIXED: one pair reranked, one not. A run that fell over halfway
        # must not produce a unit scored half one way and half the other, and
        # "any pair was reranked" is exactly the wrong test.
        pair("d", "u4", 5, 5),
        pair("d2", "u4", 9, 2, reranked=False),
    ])
    by = {u.unit: u for u in units}
    check("a unit is scored post-rerank on its BEST acceptable target",
          by["u1"].best_rank_reranked == 2 and by["u1"].recall_at_6_reranked
          and by["u1"].best_pair_reranked == "a",
          f"best={by['u1'].best_rank_reranked}")
    check("post-rerank coverage counts every target that reached the top 6",
          by["u1"].coverage_n_reranked == 1 and by["u1"].coverage_n == 0,
          f"{by['u1'].coverage_n_reranked}/{by['u1'].coverage_total}")
    check("a unit reranked into a MISS is recorded as one",
          by["u2"].recall_at_6_reranked is False
          and by["u2"].best_rank_reranked == 21)
    check("a unit with any un-reranked pair is not scored as reranked",
          by["u3"].reranked is False and by["u3"].best_rank_reranked is None
          and by["u4"].reranked is False and by["u4"].best_rank_reranked is None,
          f"u4 reranked={by['u4'].reranked} "
          f"best={by['u4'].best_rank_reranked}")

    s = summarise_units(units)
    check("post-rerank recall is reported over ALL units, not only reranked ones",
          s["recall_at_6_reranked_n"] == 1 and s["units"] == 4
          and abs(s["recall_at_6_reranked"] - 1 / 4) < 1e-9,
          f"{s['recall_at_6_reranked_n']}/{s['units']} = {s['recall_at_6_reranked']:.3f}")
    check("the pre-rerank unit recall is still reported beside it",
          s["recall_at_6_n"] == 2 and s["reranked_units"] == 2)
    check("an unreranked run reports no post-rerank keys at all",
          "recall_at_6_reranked" not in summarise_units(
              build_units([pair("z", "u9", 3, None, reranked=False)])))

def main() -> int:
    test_gold_set()
    test_loader_is_strict()
    test_metrics()
    test_search_depth_is_the_whole_view()
    test_units_are_scored_once()
    test_aligned_alternate_is_a_second_acceptable_target()
    test_alternates_are_admitted_only_on_section_alignment()
    test_a_run_must_reach_the_index_it_names()
    test_observed_chunk_id_is_never_the_target()
    test_rerank_is_recorded_beside_the_baseline_and_never_over_it()
    test_the_rerank_transport_fails_loudly_and_never_silently()
    test_the_paced_client_waits_before_the_call_not_after_the_refusal()
    test_post_rerank_units_are_scored_over_the_whole_gate()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for name in FAIL:
            print(f"  FAILED: {name}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
