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
# about where THIS process is writing, and until 2026-08-22 nothing guarded it.
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

PASS, FAIL = [], []


def check(name: str, ok: bool, detail: str = "") -> None:
    """Record and print one assertion.

    The print is encode-guarded, and the reason is a defect this suite had for
    as long as it has had a non-English corpus. A failing check prints its
    detail, and details here carry Greek, Tamil and Chinese. Run in a terminal
    that is UTF-8 the line prints; run through a PIPE on Windows the child's
    stdout falls back to cp1252, `print` raises UnicodeEncodeError, and the
    suite DIES instead of failing.

    That is invisible at baseline — the line is only printed when the check
    fails — so it surfaced first under `scripts/mutate_ranking.py`, which reads
    FAIL lines out of a pipe. Every guard whose failure message contains a
    non-Latin character was, until 2026-08-16, a guard that could not be
    watched failing: the harness saw a crash, not a failure.

    Escaping beats dying. The mutation harness now also forces UTF-8 on the
    child, so both ends of the pipe are fixed rather than one.
    """
    (PASS if ok else FAIL).append(name)
    line = f"{'ok  ' if ok else 'FAIL'} {name}" + (
        f"\n       {detail}" if detail and not ok else "")
    try:
        print(line)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "ascii"
        print(line.encode(encoding, "backslashreplace").decode(encoding))


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
    # Ruling 54's stamp. Defaults FALSE here for the same reason it defaults
    # false in the loader: absence is the claim, so the stub's ordinary state
    # has to be the unstamped one.
    written_after_the_records_entered_the_index: bool = False
    note: str = ""

    @property
    def unit(self) -> str:
        return self.unit_id or self.id


def ranking(*specs) -> list[StubHit]:
    """ranking(('doc-a::0', 0.9), ...) -> hits in the order given.

    The role is read out of the chunk id, because that is where a real chunk
    carries it: `d::t::0` and `arabia-01-periplus::translation::002` are
    translations, everything else is an original. Ruling 8's honesty instrument
    reads `.role`, and a stub that called every chunk an original would have let
    "this record was reached via its English" pass while measuring nothing.
    """
    def role_of(cid: str) -> str:
        parts = cid.split("::")
        return ("translation" if len(parts) > 1 and parts[1].startswith("t")
                else "original")

    return [StubHit(cid, cid.split("::")[0], sim, role=role_of(cid))
            for cid, sim in specs]


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


def test_a_section_is_one_record_and_it_is_the_original() -> None:
    """Block C ruling 8 (C2a). The index holds each passage twice and the two
    competed for the same six slots; on 2026-08-16 that cost two units at the
    gate. Collapsing changes what retrieval RETURNS — ruling 7 refused to change
    what the metric COUNTS, and the difference is that after a collapse the top
    6 literally contains the original chunk the pair names."""
    from eval.run_ranking_check import apply_collapse
    from retrieve.collapse import (
        collapse, collapse_report, primary_role, promote_sole, section_maps,
    )

    # Ruling 11. Derived from `source_type` via ingest.fidelity.FIND_TYPES, not
    # authored: the distinction has been in the codebase since Part 3, and it
    # predicts which records break without having been fitted to them.
    check("a source text IS its record, so its primary is the original",
          primary_role("literary_text") == "original"
          and primary_role("inscription") == "original")
    check("a find record's primary text is its curatorial description",
          primary_role("find_record") == "translation"
          and primary_role("coin_record") == "translation",
          f"{primary_role('find_record')}")

    # `f` is a 1:1 find record: the row must be the TRANSLATION, because that is
    # the text `au-hoby-silver` and two others name, and which the collapse
    # folded away on 2026-08-16.
    find_groups = [("f::o::0", ["f::t::0"], "sole"),
                   ("g::o::0", ["g::t::0", "g::t::1"], "section")]
    _so, canon_find = section_maps(find_groups, {"f": "translation",
                                                 "g": "translation"})
    check("a find record collapses to its curatorial description, not its caption",
          canon_find["f::o::0"] == "f::t::0", f"{canon_find}")
    check("a multi-member section falls back to the original rather than guessing",
          canon_find["g::o::0"] == "g::o::0", f"{canon_find}")

    groups = [
        ("d::o::0", ["d::t::0", "d::t::1"], "section"),
        ("d::o::1", ["d::t::2"], "index"),          # positional: NOT a section
        ("e::o::0", ["e::t::0"], "section"),
    ]
    # Ruling 9. `d` contributes TWO groups, so its `index` one stays the
    # coincidence-of-counting case and is refused. `f` contributes exactly one
    # group with exactly one member — no neighbour exists to confuse it with,
    # and that is the whole argument.
    promoted = promote_sole(groups + [("f::o::0", ["f::t::0"], "index")])
    by_canon = {c: g for c, _m, g in promoted}
    check("a lone 1:1 `index` group is the mislabelled case and becomes `sole`",
          by_canon["f::o::0"] == "sole", f"{by_canon}")
    check("an `index` group in a document with others stays refused",
          by_canon["d::o::1"] == "index")
    check("`sole` collapses and `index` still does not",
          set(section_maps(promoted)[1]) == {"d::o::0", "e::o::0", "f::o::0"},
          f"{sorted(section_maps(promoted)[1])}")

    section_of, canonical = section_maps(groups)
    check("only a section-aligned group becomes one record",
          set(canonical) == {"d::o::0", "e::o::0"}
          and "d::t::2" not in section_of and "d::o::1" not in section_of,
          f"canonical={sorted(canonical)}")
    check("every member of a section maps to its original",
          section_of["d::t::0"] == "d::o::0"
          and section_of["d::t::1"] == "d::o::0")

    # The translation outranks the original — the exact 2026-08-16 shape, where
    # eastasia-01-weilue::translation::000 sat at rank 1 and its original at 5.
    hits = ranking(("d::t::0", 0.90), ("x::o::0", 0.85), ("d::t::1", 0.80),
                   ("e::t::0", 0.75), ("d::o::0", 0.70), ("e::o::0", 0.65),
                   ("d::o::1", 0.60), ("d::t::2", 0.55))
    out = collapse(hits, section_of, canonical)
    ids = [h.chunk_id for h in out]
    check("a section takes the position of its best-ranked member",
          ids[0] == "d::o::0", f"{ids}")
    check("the row is the ORIGINAL even when the translation ranked higher",
          "d::t::0" not in ids and "d::t::1" not in ids and "e::t::0" not in ids,
          f"{ids}")
    check("each section appears exactly once",
          ids == ["d::o::0", "x::o::0", "e::o::0", "d::o::1", "d::t::2"], f"{ids}")
    check("a chunk in no section passes through untouched",
          "x::o::0" in ids and "d::o::1" in ids and "d::t::2" in ids)
    check("collapsing never lengthens the ranking and never invents a chunk",
          len(out) <= len(hits)
          and {h.chunk_id for h in out} <= {h.chunk_id for h in hits})
    check("collapsing twice is collapsing once",
          [h.chunk_id for h in collapse(out, section_of, canonical)] == ids)

    stats = collapse_report(hits, out)
    # `roles_removed == ["translation"]` is the assertion, and until the stub
    # ranking carried real roles it read `["original"]` and PASSED — a green
    # check about a fiction. What a collapse removes is translations, by
    # construction, and a run reporting otherwise means ruling 8 is folding the
    # wrong way round.
    check("the run records what the collapse actually removed",
          stats["in"] == 8 and stats["out"] == 5 and stats["removed"] == 3
          and stats["roles_removed"] == ["translation"],
          f"{stats}")

    # The gate's arithmetic, on the shape that cost china-describes-rome.
    r = _rr_pair(id="weilue", unit="china", expect_doc="d",
                 resolved_chunk_id="d::o::0", accepted_chunk_ids=["d::o::0"],
                 rank=5, recall_at_6=True, rank_accepted=5)
    apply_collapse(r, out)
    check("the collapsed rank is recorded under its own name",
          r.collapsed and r.rank_collapsed == 1
          and r.recall_at_6_collapsed and r.rank_accepted_collapsed == 1)
    check("collapsing does not touch `rank`, which every gap is denominated in",
          (r.rank, r.recall_at_6, r.gap_vs_other_doc) == (5, True, 0.07),
          f"rank={r.rank} gapDoc={r.gap_vs_other_doc}")

    # The honesty instrument. `d::t::0` reached rank 1 and `d::o::0` sat at 5,
    # so the record was found on the strength of its ENGLISH. The number says
    # hit; this says how.
    from retrieve.collapse import entry_roles

    entry = entry_roles(hits, section_of)
    # `.get`, not `[...]`. With subscripting, the mutation that empties this map
    # raised KeyError and KILLED the suite instead of failing this check — which
    # `scripts/mutate_ranking.py` correctly reported as "(suite crashed)" rather
    # than as a pass. A check must fail on the defect it guards, not die on it.
    check("the run records WHICH member of a section got there first",
          entry.get("d::o::0") == "translation"
          and entry.get("e::o::0") == "translation",
          f"{entry}")
    r2 = _rr_pair(id="w2", expect_doc="d", resolved_chunk_id="d::o::0",
                  accepted_chunk_ids=["d::o::0"], rank=5, rank_accepted=5)
    apply_collapse(r2, out, entry, section_of)
    check("a record reached via its translation says so on the pair",
          r2.collapse_entry_role == "translation" and r2.recall_at_6_collapsed,
          f"entry_role={r2.collapse_entry_role}")
    check("a record reached via its translation does NOT count as via-original",
          r2.recall_at_6_via_original is False)

    # A chunk in no section has no entry role, and there was no translation for
    # it to have been reached through — the question does not arise, which is
    # not the same as a miss.
    r3 = _rr_pair(id="x", expect_doc="x", resolved_chunk_id="x::o::0",
                  accepted_chunk_ids=["x::o::0"], rank=2, rank_accepted=2)
    apply_collapse(r3, ranking(("x::o::0", 0.9)), {}, {})
    check("a record with no translation at all counts as via-original",
          r3.recall_at_6_via_original and r3.collapse_entry_role is None)

    # Ruling 11's consequence for ruling 9's companion: a find record has no
    # source text, so reaching it through its description bypasses nothing.
    r4 = _rr_pair(id="find", expect_doc="d", resolved_chunk_id="d::o::0",
                  accepted_chunk_ids=["d::o::0"], rank=5, rank_accepted=5)
    apply_collapse(r4, out, entry, section_of, {"d": "translation"})
    check("reaching a record with no source text is not counted as a bypass",
          r4.collapse_primary_role == "translation"
          and r4.recall_at_6_via_original,
          f"primary={r4.collapse_primary_role} via={r4.recall_at_6_via_original}")

    plain = ranking(("d::o::0", 0.9), ("d::t::0", 0.5))
    check("a record reached via its original says THAT",
          entry_roles(plain, section_of)["d::o::0"] == "original")

    # A target that is a TRANSLATION is folded away, and that is a miss, not a
    # hit by proxy. Ruling 7 is what forbids scoring it any other way.
    t = _rr_pair(id="tr", unit="tr", expect_doc="d",
                 resolved_chunk_id="d::t::0", accepted_chunk_ids=["d::t::0"],
                 rank=1, rank_accepted=1)
    apply_collapse(t, out)
    check("a target folded into its section is not counted as returned",
          t.rank_collapsed is None and t.recall_at_6_collapsed is False,
          f"rank_collapsed={t.rank_collapsed}")

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
    # BOTH interventions at once. Neither alone could catch the defect this
    # guards: the rerank branch of summarise_units REASSIGNED its dict instead
    # of updating it, so a collapsed+reranked run lost every collapse key and
    # died in print_report after twenty-six minutes of paced calls.
    both = [pair("m", "u5", 9, 3)]
    both[0].collapsed = True
    both[0].rank_accepted_collapsed = 2
    both[0].recall_at_6_accepted_collapsed = True
    s_both = summarise_units(build_units(both))
    check("a run with BOTH collapse and rerank keeps BOTH sets of keys",
          "recall_at_6_collapsed" in s_both and "recall_at_6_reranked" in s_both
          and s_both["recall_at_6_collapsed_n"] == 1
          and s_both["recall_at_6_reranked_n"] == 1,
          f"{sorted(s_both)}")

    check("an unreranked run reports no post-rerank keys at all",
          "recall_at_6_reranked" not in summarise_units(
              build_units([pair("z", "u9", 3, None, reranked=False)])))


def test_the_via_original_companion_is_measured_at_both_points() -> None:
    """C7. `recall@6 via the original text` is computed on the COLLAPSED
    ordering, while the adopted configuration RERANKS. The report printed it on
    the same page as a post-rerank recall with nothing to say the two were
    measured at different points, so 29/30 and 21/30 read as one measurement.

    The fix is a SECOND field under a second name. Overwriting the first would
    be unrecoverable: every run archived since ruling 9 holds the pre-rerank
    figure, and a run that replaced it would be incomparable to all of them —
    which is the same reason `rank_reranked` never overwrote `rank`.

    Every condition below reads the aggregate with `.get`. A check that raises
    KeyError on the defect it guards DIES instead of failing, and this harness
    reads FAIL lines out of stdout.
    """
    import io
    from contextlib import redirect_stdout

    from eval.run_ranking_check import (
        Report, _print_collapse, _print_rerank, apply_collapse, apply_rerank,
        build_units, summarise_units,
    )

    def at(cid, rank):
        """A ranking with `cid` at `rank` and fillers everywhere else."""
        specs = [(f"filler-{i}::original::000", 0.9 - i / 100)
                 for i in range(1, max(rank, RECALL_AT) + 3)]
        specs[rank - 1] = (cid, 0.99)
        return ranking(*specs)

    def scored(name, entry_role, primary, rank_co, rank_rr):
        """One unit of one pair, collapsed at `rank_co`, reranked to `rank_rr`."""
        cid = f"{name}::original::000"
        r = _rr_pair(id=name, unit=name, expect_doc=name,
                     resolved_chunk_id=cid, accepted_chunk_ids=[cid],
                     rank=rank_co, rank_accepted=rank_co,
                     recall_at_6_accepted=rank_co <= RECALL_AT)
        apply_collapse(r, at(cid, rank_co),
                       {cid: entry_role} if entry_role else {},
                       {cid: cid} if entry_role else {},
                       {name: primary})
        apply_rerank(r, at(cid, rank_rr), {}, 50, name)
        return r

    # The three shapes C7 named, and two more that make the two figures come
    # out DIFFERENT — 2/5 and 3/5. A fixture where they agree would let a report
    # printing one number twice pass for a report printing both, which is the
    # same defect as the fixture whose max was its last value.
    bypassed = scored("bypassed", "translation", "original", 10, 2)
    no_source = scored("no-source-text", "translation", "translation", 10, 2)
    leaves = scored("leaves-top-6", "original", "original", 3, 9)
    steady = scored("steady", "original", "original", 2, 2)
    rescued = scored("rescued", None, "original", 12, 3)
    pairs = [bypassed, no_source, leaves, steady, rescued]
    units = build_units(pairs)
    agg = summarise_units(units)

    check("a record rescued into the top 6 through its ENGLISH is still not "
          "via-original",
          bypassed.recall_at_6_accepted_reranked
          and bypassed.recall_at_6_via_original_reranked is False,
          f"rank {bypassed.rank_accepted_collapsed} -> "
          f"{bypassed.rank_accepted_reranked}; entry "
          f"{bypassed.collapse_entry_role}, primary "
          f"{bypassed.collapse_primary_role}")
    check("a rescued record with NO source text does count as via-original",
          no_source.recall_at_6_via_original_reranked
          and no_source.recall_at_6_via_original is False,
          f"pre={no_source.recall_at_6_via_original} "
          f"post={no_source.recall_at_6_via_original_reranked}")
    check("a unit reranked OUT of the top 6 loses the post-rerank figure and "
          "keeps the pre-rerank one",
          leaves.recall_at_6_via_original
          and leaves.recall_at_6_via_original_reranked is False,
          f"rank {leaves.rank_accepted_collapsed} -> "
          f"{leaves.rank_accepted_reranked}; "
          f"pre={leaves.recall_at_6_via_original} "
          f"post={leaves.recall_at_6_via_original_reranked}")
    check("the pre-rerank via-original is not overwritten by the post-rerank one",
          agg.get("recall_at_6_via_original_n") == 2
          and agg.get("recall_at_6_via_original_reranked_n") == 3,
          f"pre {agg.get('recall_at_6_via_original_n')}/5   "
          f"post {agg.get('recall_at_6_via_original_reranked_n')}/5")

    # A run that fell over after the collapse and before the rerank. The pair
    # carries a post-rerank figure it was never entitled to, and the unit gate
    # is the only thing that refuses it — which is why the gate reads
    # `reranked` and not `collapsed`.
    half = _rr_pair(id="half", unit="half", expect_doc="half",
                    resolved_chunk_id="half::original::000",
                    accepted_chunk_ids=["half::original::000"],
                    rank=2, rank_accepted=2, recall_at_6_accepted=True)
    apply_collapse(half, at("half::original::000", 2), {}, {}, {})
    half.recall_at_6_via_original_reranked = True
    gate = build_units([half, scored("gate-ok", "original", "original", 2, 2)])
    by_gate = {u.unit: u.recall_at_6_via_original_reranked for u in gate}
    check("a unit whose pairs were not all reranked is refused the post-rerank "
          "figure",
          by_gate == {"half": False, "gate-ok": True}
          and summarise_units(gate).get(
              "recall_at_6_via_original_reranked_n") == 1,
          f"{by_gate}")

    lone = _rr_pair(id="lone", unit="lone", expect_doc="lone",
                    resolved_chunk_id="lone::original::000",
                    accepted_chunk_ids=["lone::original::000"],
                    rank=2, rank_accepted=2, recall_at_6_accepted=True)
    apply_collapse(lone, at("lone::original::000", 2), {}, {}, {})
    s_co = summarise_units(build_units([lone]))
    check("an unreranked run reports no post-rerank via-original key at all",
          "recall_at_6_via_original_n" in s_co
          and "recall_at_6_via_original_reranked_n" not in s_co,
          f"{sorted(k for k in s_co if 'via_original' in k)}")

    # Ruling 26. Without a collapse there is no entry role for the bypass
    # clause to fire on, so the post-rerank figure would come out exactly equal
    # to post-rerank recall — 29/30 published under a name that says something
    # else. An uncollapsed run reports neither.
    rr_only = _rr_pair(id="rr", unit="rr", expect_doc="rr",
                       resolved_chunk_id="rr::original::000",
                       accepted_chunk_ids=["rr::original::000"],
                       rank=2, rank_accepted=2, recall_at_6_accepted=True)
    apply_rerank(rr_only, at("rr::original::000", 2), {}, 50, "rr")
    s_rr = summarise_units(build_units([rr_only]))
    check("a run that reranked without collapsing reports NEITHER via-original "
          "figure",
          not [k for k in s_rr if "via_original" in k],
          f"{sorted(k for k in s_rr if 'via_original' in k)}")

    report = Report(timestamp="t", view="v", search_k=1, index_chunks=1,
                    embedding_models=[], query_embedding_model="")
    report.pairs, report.units, report.aggregate_units = pairs, units, agg
    report.collapsed, report.collapse_sections = True, 1
    report.collapse_stats = {"in": 5, "out": 5, "removed": 0,
                             "roles_removed": []}
    report.reranked = True
    report.rerank_model, report.rerank_window = "rerank-2.5", 50
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        _print_collapse(report)
        _print_rerank(report)
    printed = buffer.getvalue()
    shown = "\n".join(line for line in printed.splitlines()
                      if "VIA THE ORIGINAL" in line)

    # Asserted on the VALUES and never on the heading: a check that greps a
    # heading passes against a report that prints the heading and no number.
    check("the report says which measurement point the collapsed figure is",
          any("VIA THE ORIGINAL TEXT, PRE-rerank" in line and "(2/5)" in line
              for line in printed.splitlines()), shown)
    check("the report prints BOTH via-original values, pre and post",
          any("(2/5)" in line and "(3/5)" in line
              for line in printed.splitlines()), shown)


def test_the_query_rendering_rule_cannot_see_the_answer() -> None:
    """C2, Block C rulings 12 / 15b / 17a / 19.

    The leakage trap is the one that would invalidate every C2 number, and it
    cannot be caught by looking at a rank: a run that chose each query's target
    language by reading `expect_lang` would produce a beautiful curve and would
    measure nothing at all. So it is caught here, structurally, before a call is
    spent — the rule's SIGNATURE is asserted, not merely its output.
    """
    import inspect
    import json as _json
    import tempfile
    from pathlib import Path as _Path

    from answer.translate import (  # noqa: E402
        TranslationError,
        build_render_messages,
        render_query,
    )
    from retrieve.render import (  # noqa: E402
        SCHEMA as R_SCHEMA,
        SCRIPT_FLOOR,
        RenderingError,
        Renderings,
        coverage_problems,
        expected_rendering_count,
        load,
        native_query_problems,
        rendering_problems,
        required_script,
        script_ratio,
        target_langs,
    )

    gold_path = _Path(__file__).resolve().parent / "gold" / "ranking_pairs.json"
    gold_doc = _json.loads(gold_path.read_text(encoding="utf-8"))

    # ---- ruling 12: the signature is the assertion -----------------------
    params = list(inspect.signature(target_langs).parameters)
    check("the language rule takes the index and the query and nothing else",
          params == ["index_langs", "query_lang"],
          f"signature is {params} — a third parameter is how expect_lang gets in")

    corpus_langs = sorted(gold_doc["pools"]["non_english"]["langs"])
    index_langs = sorted(set(corpus_langs) | {"en"})

    # Both directions. Excluding English only for an English query would leave
    # a Greek query rendered into English — which is the index's own
    # translations answering a query about the original, the thing ruling 8's
    # collapse exists to stop competing.
    check("English is never a render target — it is the single-variant arm",
          "en" not in target_langs(index_langs, "en")
          and "en" not in target_langs(index_langs, "grc"),
          f"grc -> {target_langs(index_langs, 'grc')}")
    check("a query is never rendered into its own language",
          "grc" not in target_langs(index_langs, "grc")
          and "oty" not in target_langs(index_langs, "oty"))
    check("ruling 15b: an English query gets every non-English index language",
          target_langs(index_langs, "en") == corpus_langs,
          f"{target_langs(index_langs, 'en')}")
    check("ruling 15b: a native-language query is rendered too, minus its own",
          len(target_langs(index_langs, "grc")) == len(corpus_langs) - 1)

    # The whole cost of ruling 12, computed rather than estimated:
    # one rendering per (distinct query, index language it is not already in).
    #
    # F4, 2026-08-31. THE NUMBER HAS LEFT THIS GUARD'S LABEL, and the reason is
    # written in this repository already, in eval/test_answer_eval.py:
    #
    #   "The counts go in their OWN line and not into the guard text. A guard
    #    named by scripts/mutate_part8.py is matched as an exact string, so a
    #    guard whose wording carries a number it computes is a guard the
    #    harness stops being able to name the moment a mutation changes that
    #    number."
    #
    # This label read "costs exactly 205 renderings" and was named verbatim in
    # scripts/mutate_ranking.py's EXPECTED list. Adding ONE ranking pair under
    # ruling 54 moved the cost, and the guard and its harness would have had to
    # be edited together on every tranche for the rest of Block F -- which is
    # how a harness quietly stops naming the guard it is exercising. The rule
    # was written for one file and broken in another.
    #
    # What is asserted is now the RULE and not the total: the cost is exactly
    # what the language rule says it is, computed the same way twice from two
    # different directions, and the total is printed beside it.
    query_langs = {p["query"]: p["query_lang"] for p in gold_doc["pairs"]}
    cost = expected_rendering_count(index_langs, query_langs.values())
    by_hand = sum(len(target_langs(index_langs, lang))
                  for lang in query_langs.values())
    check("ruling 12's cost is the language rule applied to every distinct "
          "query, and nothing else",
          cost == by_hand and cost > 0, f"{cost} renderings over "
          f"{len(query_langs)} distinct queries")

    # ---- ruling 17(a): the script check ---------------------------------
    check("Greek script passes a grc rendering",
          not rendering_problems("τί ἔφερον τὰ πλοῖα ἐκ Μουζιρίδος;", "grc"))
    check("ROMANISED Tamil is refused for oty — the Part 4 chrF-0.004 failure",
          any(p.startswith("script") for p in
              rendering_problems("yavanar muciri ponnotu vantu", "oty")),
          "a romanised query retrieves badly for a reason no rank can report")
    check("Literary Chinese inside an English sentence is refused for lzh",
          any(p.startswith("script") for p in rendering_problems(
              "the country 大秦 that the query asks about", "lzh")),
          f"ratio {script_ratio('the country 大秦 that the query asks about', 'han'):.2f} "
          f"against a floor of {SCRIPT_FLOOR}")
    check("Chinese characters pass a lzh rendering",
          not rendering_problems("大秦國的使者從何處來", "lzh"))
    check("scholarly transliteration passes xpr, and Greek script does not",
          not rendering_problems("šāhān šāh Ērān ud Anēran Šābuhr", "xpr")
          and any(p.startswith("script") for p in
                  rendering_problems("βασιλεὺς βασιλέων", "xpr")))
    check("an empty rendering is refused before it can be embedded",
          rendering_problems("   ", "grc")
          == ["empty: the model returned no usable rendering"])
    check("a rendering identical to its query is refused as an echo",
          any(p.startswith("echo") for p in
              rendering_problems("Μουζιρίς", "grc", source_text="Μουζιρίς")),
          "fused by max, an echo is a second copy of the single-variant arm")
    try:
        required_script("qqq")
        raised = False
    except RenderingError:
        raised = True
    check("a language with no declared writing system is refused, not waved through",
          raised)

    # ---- ruling 20: the floor was 0.6 and the first real run found the band --
    # This exact string was ADMITTED at floor 0.6: Tamil, Hangul, Han and Latin
    # in one rendering. The argument for 0.6 was that a wholly-wrong rendering
    # sits at 0.0 and the band between is empty. Ten of 205 renderings were in
    # it.
    mixed = "கேரளக் கரையில்발掘된 지중해 amphora sherds"
    problems = rendering_problems(mixed, "oty")
    check("a rendering one third in another writing system is refused",
          any(p.startswith("script") for p in problems),
          f"ratio {script_ratio(mixed, 'tamil'):.2f}, floor {SCRIPT_FLOOR}")
    check("the refusal names the letters that do not belong",
          bool(problems) and "발" in problems[0] and "amphora" not in problems[0],
          problems[0] if problems else "no problem reported")
    # Indexed defensively. A mutation that drops the floor makes this list
    # empty, and an IndexError here would CRASH the suite — which the mutation
    # harness reads as "no failures", marking the mutation unwatched and
    # skipping every check after it. That is the SUITE_CRASHED failure the
    # harness was taught to name on 2026-08-16; a test must fail, not die.
    _wholly = rendering_problems("romanised", "oty")
    wholly = _wholly[0] if _wholly else ""
    check("mixed script and wrong script are different diagnoses, both printed",
          bool(problems) and "41%" in problems[0]
          and "0% of the judged" in wholly and problems[0] != wholly,
          f"{problems[0][:70] if problems else ''} || {wholly[:40]}")
    # THE BAND. 69% Han, admitted by the 0.6 floor the first run was made at
    # and refused at 1.0. Written as its own check because the 30% string above
    # is refused under either floor and so cannot witness the raise.
    check("a rendering admitted by the old 0.6 floor is refused at 1.0",
          any(p.startswith("script") for p in
              rendering_problems("乳香國及阿拉伯之Kane港", "lzh")),
          f"ratio {script_ratio('乳香國及阿拉伯之Kane港', 'han'):.2f}, "
          f"floor {SCRIPT_FLOOR}")
    # ʾ and ʿ are Unicode LETTERS in no Latin block. Before U+02B0-02FF was
    # added to the Latin ranges, a whole-language floor would have refused the
    # corpus's own transliteration convention — 118 Sabaic and Nabataean rows.
    check("scholarly modifier letters do not make a Latin rendering foreign",
          not rendering_problems("mlk mlkn Saba wa-l-ʿArab Šabur", "xsa")
          and not rendering_problems("ʾrḍ dkrt lbnt w-mnt Kn b-ʿrb", "xsa"))
    check("a stray Greek letter still refuses a Latin rendering",
          any(p.startswith("script") for p in
              rendering_problems("pad dānmārkīg bataγ nihād", "xpr")),
          "the one genuinely impure Latin rendering of the 2026-08-16 run")

    # ---- ruling 19, and ruling 12's structural half ----------------------
    def _file(doc) -> _Path:
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8")
        handle.write(_json.dumps(doc, ensure_ascii=False))
        handle.close()
        return _Path(handle.name)

    good = {
        "schema": R_SCHEMA, "prompt_version": "c2-render-v1",
        "chat_model": "stub", "view": "v", "index_langs": index_langs,
        "queries": [{
            "query": "q", "query_lang": "en",
            "renderings": {
                "grc": {"text": "ἑλληνικά", "ok": True},
                "oty": {"text": "romanised", "ok": False,
                        "problems": ["script: 0% of the letters are tamil"]},
            },
        }],
    }
    loaded = load(_file(good))
    variants = loaded.variants_for("q", "en")
    check("the query's own text is always the first variant",
          variants[0].source == "query" and variants[0].text == "q"
          and variants[0].lang == "en")
    check("a rendering the script check refused is never fused",
          [v.lang for v in variants] == ["en", "grc"],
          f"{[v.lang for v in variants]}")
    check("a refused rendering is kept as evidence rather than deleted",
          bool(loaded.rejected()) and loaded.rejected()[0][1] == "oty")
    check("the rendering file carries a content hash for the two-day criterion",
          len(loaded.digest) == 16)

    try:
        loaded.variants_for("a query nobody rendered", "en")
        raised = False
    except RenderingError:
        raised = True
    check("a query with no renderings raises rather than degrading silently",
          raised,
          "falling back to the English-only arm for SOME pairs would report a "
          "C2 number about a configuration nobody chose")

    leaky = _json.loads(_json.dumps(good))
    leaky["queries"][0]["pair_ids"] = ["muziris-cargo-periplus"]
    try:
        load(_file(leaky))
        raised = False
    except RenderingError:
        raised = True
    check("a rendering file that mentions a pair id is refused outright", raised,
          "ruling 12: the file must be structurally incapable of recording a "
          "per-pair language choice")

    wrong_schema = _json.loads(_json.dumps(good))
    wrong_schema["schema"] = "something/else"
    try:
        load(_file(wrong_schema))
        raised = False
    except RenderingError:
        raised = True
    check("a rendering file of an unknown schema is refused", raised)

    # ---- the file and the run must be about the same index ---------------
    check("a query missing from the file is a refusal, not a gap",
          any("no renderings for query" in p for p in
              coverage_problems(loaded, {"q": "en", "other": "en"}, index_langs)))
    check("a file built against a different index is refused",
          any("index languages" in p for p in
              coverage_problems(loaded, {"q": "en"}, ["en", "grc"])))
    over = Renderings(
        path=_Path("x"), prompt_version="", chat_model="", view="v",
        index_langs=index_langs,
        by_query={"q": {lang: {"text": "t", "ok": True}
                        for lang in corpus_langs + ["la"]}})
    check("a rendering the language rule never asked for is refused",
          any("does not ask for" in p for p in
              coverage_problems(over, {"q": "en"}, index_langs)))

    # ---- ruling 15b: the assertion that replaces invariance --------------
    check("an English query is not subject to the native-query control",
          native_query_problems("en", "grc", 1, 1) == [])
    check("a native query winning in its own language at the same rank passes",
          native_query_problems("grc", "grc", 1, 1) == [])
    check("a rendering beating the native text on a native query is a finding",
          any("beat the query's own" in p for p in
              native_query_problems("grc", "lzh", 1, 1)))
    check("fusion making a native-language query worse is a finding",
          any("rank 1 to 4" in p for p in
              native_query_problems("grc", "grc", 1, 4)))
    check("fusion losing a native-language query entirely is a finding",
          any("lost a native-language query" in p for p in
              native_query_problems("grc", "grc", 1, None)))

    # ---- the prompt asks for the script rule, it is not only checked -----
    tamil = build_render_messages("a query", "en", "oty")[0]["content"]
    parthian = build_render_messages("a query", "en", "xpr")[0]["content"]
    check("the render prompt demands the Tamil script for oty",
          "Tamil script" in tamil and "Do NOT romanise" in tamil)
    check("the render prompt demands transliteration for xpr",
          "transliteration" in parthian
          and "not in its historical script" in parthian)
    check("the render prompt asks for the query, not for an answer to it",
          "Do not answer it" in tamil and "SEARCH QUERY" in tamil)
    # Asserted on the MESSAGE, not merely on the exception type. A stub client
    # and a stub sleep mean the mutated arm also ends in a TranslationError —
    # three failed attempts against an object with no `chat` — so a check that
    # only caught the type would pass against a bypassed guard and report a
    # mutation as watched. It is the same class of defect as a stub that lies.
    try:
        render_query("q", "grc", "grc", client=object(), sleep=lambda _s: None)
        raised = ""
    except TranslationError as exc:
        raised = str(exc)
    check("rendering a language into itself is refused at the call",
          "the language rule was bypassed" in raised, raised[:140])

    # ---- ruling 20: a retry has to be a different prompt ------------------
    from answer.translate import (  # noqa: E402
        QUERY_PROMPT_VERSION,
        QUERY_RETRY_PROMPT_VERSION,
    )

    first = build_render_messages("a query", "en", "oty")[0]["content"]
    again = build_render_messages("a query", "en", "oty", retry=True)[0]["content"]
    check("the retry prompt is a different prompt from the first",
          again != first and "WRONG WRITING SYSTEM" in again,
          "at temperature=0 the same prompt is the same call, not a second "
          "attempt — it would return the same wrong-script string")
    check("the retry prompt keeps the writing-system rule it is retrying",
          "Tamil script" in again)
    check("a retried rendering carries its own prompt version",
          QUERY_RETRY_PROMPT_VERSION != QUERY_PROMPT_VERSION,
          "otherwise the file holds two prompts' output under one provenance "
          "string")

    # ---- ruling 21: a retry may improve a row and may never destroy it -----
    # The 2026-08-16 retry pass is the argument, and it is the reason this
    # exists rather than a hypothetical: the corrective prompt came back WORSE
    # on seven of ten Old Tamil rows — one went from a single stray letter to
    # thirty-six — and a pipeline that takes the newest attempt would have
    # replaced a rendering at 98% Tamil with one at 5% and called it a fix.
    from retrieve.render import SUPERSEDED_SCHEMAS, best_attempt  # noqa: E402

    first_try = {"text": "ok text", "ok": True, "script_ratio": 0.98}
    worse = {"text": "worse", "ok": False, "script_ratio": 0.05}
    better = {"text": "better", "ok": True, "script_ratio": 1.0}
    # The case that makes `ok` load-bearing rather than decorative. An ECHO is
    # 100% in the right script and still not a rendering, so script ratio alone
    # would rank it first — and it arrived first, so position would too. Only
    # the admitted/held term separates them.
    echo_attempt = {"text": "same as the query", "ok": False,
                    "script_ratio": 1.0}
    admitted = {"text": "a real rendering", "ok": True, "script_ratio": 1.0}
    check("an admitted attempt beats a held one whatever the order",
          best_attempt([echo_attempt, admitted])["text"] == "a real rendering"
          and best_attempt([admitted, echo_attempt])["text"] == "a real rendering",
          "an echo is wholly in the right script and is still not a rendering")
    check("a retry that came back worse does not become the rendering",
          best_attempt([first_try, worse])["text"] == "ok text",
          "seven of ten Old Tamil retries were worse than what they replaced")
    check("a retry that came back better does become the rendering",
          best_attempt([first_try, better])["text"] == "better")
    check("among equals the earlier attempt is kept, so a re-run changes nothing",
          best_attempt([dict(better, text="a"), dict(better, text="b")])["text"]
          == "a")
    check("no attempts at all is None, not an empty rendering",
          best_attempt([]) is None)

    # ---- ruling 23b: combining marks are not letters, and Indic ones carry
    # much of the phonology. This exact string passed at "100% Tamil" while a
    # Malayalam vowel sign sat inside the place name, and it is the query for
    # `adulis-exports` — the pair C2a's collapse moved from 15 to 3.
    adulis = "\u0b85\u0b9f\u0bc1\u0bb2\u0d3f\u0b9a\u0bbf\u0bb2\u0bbf\u0bb0\u0bc1\u0ba8\u0bcd\u0ba4\u0bc1"
    marked = rendering_problems(adulis, "oty")
    check("a foreign VOWEL SIGN inside a native word is refused",
          any(p.startswith("script") for p in marked),
          f"ratio {script_ratio(adulis, 'tamil'):.3f}")
    check("the refusal names the mark, not just a percentage",
          bool(marked) and "\u0d3f" in marked[0], marked[0] if marked else "")
    check("a script's OWN marks are not foreign to it",
          not rendering_problems("\u0bae\u0bc1\u0b9a\u0bbf\u0bb1\u0bbf", "oty"),
          "Tamil vowel signs live inside the Tamil block")
    # U+0300-036F belongs to no script and is used by Greek and by scholarly
    # transliteration alike. Refusing it would refuse correct renderings.
    check("script-neutral combining diacritics are not counted against anyone",
          not rendering_problems("s\u0301abuhr", "xpr")
          and not rendering_problems("\u03b2\u03b1\u03c3\u03b9\u03bb\u03b5\u03cd\u03c2", "grc"))

    # ---- ruling 22: a model that refuses greedy decoding -----------------
    from answer.translate import _chat, _is_unsupported_temperature  # noqa: E402

    SONNET_400 = (
        "Error code: 400 - {'error': {'message': "
        "'litellm.UnsupportedParamsError: claude-sonnet-5 does not support "
        "temperature=0. Only temperature=1 is supported.'}}"
    )
    check("a temperature refusal is classified, not left as a mystery 400",
          _is_unsupported_temperature(SONNET_400)
          and not _is_unsupported_temperature("rate limit exceeded"),
          "615 requests were spent on this before it was read by hand")

    class _Refusing:
        """Refuses temperature=0 exactly as the gateway did, then answers."""
        def __init__(self):
            self.temperatures = []
            self.chat = self

        @property
        def completions(self):
            return self

        def create(self, **kwargs):
            self.temperatures.append(kwargs["temperature"])
            if kwargs["temperature"] == 0:
                raise RuntimeError(SONNET_400)
            class R:
                choices = [type("C", (), {"message": type(
                    "M", (), {"content": "<translation>ok</translation>"})()})()]
            return R()

    client = _Refusing()
    try:
        _chat([], model="m", client=client, sleep=lambda _s: None)
        refused = ""
    except TranslationError as exc:
        refused = str(exc)
    check("without an opt-in, a temperature refusal is raised and NAMED",
          "refuses temperature=0" in refused and "drop_params" in refused,
          "LiteLLM's own fix drops the parameter for every call in the "
          "gateway, embeddings included")
    check("the refusal is raised on the FIRST call, not after three retries",
          client.temperatures == [0], f"{client.temperatures}")

    client = _Refusing()
    # Guarded, for the SUITE_CRASHED reason again: a mutation that unclassifies
    # the refusal makes this raise, and an uncaught raise would be read by the
    # mutation harness as "no failures".
    try:
        text, _retries, used = _chat([], model="m", client=client,
                                     sleep=lambda _s: None,
                                     temperature_fallback=1.0)
    except TranslationError as exc:
        text, used = f"raised instead of falling back: {exc}", None
    check("a caller that opts in falls back once and reports what it used",
          used == 1.0 and client.temperatures == [0, 1.0]
          and "<translation>ok</translation>" in text,
          f"{client.temperatures}")
    # The opt-in must DEFAULT to off, or Part 6's translations and Part 7's
    # answers would start sampling the moment their alias moved, and every
    # archived number would quietly stop being comparable to the new ones.
    check("the temperature fallback is off by default, so archived paths stay greedy",
          inspect.signature(_chat).parameters["temperature_fallback"].default
          is None,
          f"{inspect.signature(_chat).parameters['temperature_fallback'].default!r}")

    # ---- Block E decision 3: which stack served the call -----------------
    #
    # FINDING 18: five of six cases changed their answer text completely
    # between two dates at temperature 0, and nothing in the archive could
    # distinguish provider drift from sampling variance. `model` is the alias
    # this repository SENT and cannot move. These guards protect the field
    # that can.
    from answer.translate import _serving_stack  # noqa: E402

    class _Response:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    stack = _serving_stack(_Response(id="chatcmpl-9", model="claude-x",
                                     system_fingerprint=None,
                                     service_tier=None))
    check("GUARD a serving-stack key the gateway did not populate is OMITTED, "
          "never written as null",
          stack == {"id": "chatcmpl-9", "model": "claude-x"},
          "a column reading null on all 270 calls is the fourth vacuous proof "
          "in five days")
    populated = _serving_stack(_Response(id="c", model="m",
                                         system_fingerprint="fp_abc",
                                         service_tier="standard"))
    check("a serving-stack key the gateway DID populate is recorded",
          populated.get("system_fingerprint") == "fp_abc"
          and populated.get("service_tier") == "standard")
    hidden = _serving_stack(_Response(
        id="c", model="m",
        _hidden_params={"model_id": "abc123", "custom_llm_provider": "anthropic",
                        "response_ms": 812}))
    check("LiteLLM's own resolved model id is recorded, and its timing is not",
          hidden.get("model_id") == "abc123"
          and hidden.get("custom_llm_provider") == "anthropic"
          and "response_ms" not in hidden,
          "response_ms moves on every call and is not provenance")

    # ---- Block E corrections 3 and 4, 2026-08-28 -------------------------
    #
    # What is RECORDED and what can IDENTIFY A STACK are two different sets,
    # and Block E archived 396 runs without the distinction. `id` is a fresh
    # uuid per call, so counting recorded stacks reported 99 distinct stacks on
    # a 99-call day under a heading that reads like a provider changing under
    # the run. `model` is the echo of the string SENT — the sweep sends the
    # alias and the archives duly say `chat-default` — so it cannot move unless
    # the caller moves it, and a key that cannot vary independently of the
    # request is not provenance.
    from answer.translate import serving_stack_identity  # noqa: E402

    check("GUARD the per-call `id` is excluded from the stack identity",
          "id" not in serving_stack_identity({"id": "chatcmpl-9",
                                              "system_fingerprint": "fp"}),
          "a uuid per call made every sweep report one distinct stack per call")
    check("GUARD the echoed `model` is excluded from the stack identity",
          "model" not in serving_stack_identity({"model": "chat-default",
                                                 "system_fingerprint": "fp"}),
          "it is the string this repository sent, echoed back, in every path")
    check("a key that could actually identify a stack survives into the identity",
          serving_stack_identity({"id": "c", "model": "m",
                                  "system_fingerprint": "fp_abc",
                                  "custom_llm_provider": "anthropic"})
          == {"system_fingerprint": "fp_abc",
              "custom_llm_provider": "anthropic"})
    check("GUARD a Block E archive's recorded stack has an EMPTY identity — "
          "which is what the 99-distinct-stacks line was counting",
          serving_stack_identity({"id": "chatcmpl-4abe06e0",
                                  "model": "chat-default"}) == {},
          "decision 3a said this in words before day 1; it is now in code")
    check("an absent stack is an empty identity, not an error",
          serving_stack_identity(None) == {}
          and serving_stack_identity({}) == {})

    class _Plain:
        """Answers once, carrying a fingerprint."""
        def __init__(self):
            self.chat = self

        @property
        def completions(self):
            return self

        def create(self, **kwargs):
            class R:
                id = "chatcmpl-7"
                model = "claude-haiku-4-5-20251001"
                system_fingerprint = "fp_seen"
                choices = [type("C", (), {"message": type(
                    "M", (), {"content": "ok"})()})()]
            return R()

    seen: dict = {}
    _chat([], model="m", client=_Plain(), sleep=lambda _s: None,
          provenance=seen)
    check("GUARD _chat fills the serving-stack out-parameter it was given",
          seen.get("system_fingerprint") == "fp_seen"
          and seen.get("id") == "chatcmpl-7",
          "an out-parameter and not a fourth return value: the last time this "
          "function's arity moved, one of four call sites was missed and every "
          "live answer call raised ValueError for five days")
    # The five callers that do not want it must be untouched, or Block E's
    # freeze is standing on a change nobody checked.
    check("the serving-stack out-parameter defaults to off",
          inspect.signature(_chat).parameters["provenance"].default is None,
          f"{inspect.signature(_chat).parameters['provenance'].default!r}")

    # ---- ruling 24: the reader re-derives the verdict, never trusts it ----
    # The file below claims ok:true for a rendering the CURRENT guard refuses,
    # exactly as eval/gold/query_renderings.json did on 2026-08-16: the row had
    # been judged before ruling 23b and carried a Malayalam vowel sign. A reader
    # that trusts a stored verdict embeds whatever the last guard permitted.
    stale_doc = {
        "schema": R_SCHEMA, "prompt_version": "c2-render-v1",
        "chat_model": "stub", "view": "v", "index_langs": index_langs,
        "queries": [{
            "query": "q", "query_lang": "en",
            "renderings": {"oty": {
                "text": "\u0b85\u0b9f\u0bc1\u0bb2\u0d3f",
                "ok": True, "problems": [],
                "attempts": [
                    {"text": "\u0b85\u0b9f\u0bc1\u0bb2\u0d3f",
                     "chat_model": "old"},
                    {"text": "\u0b85\u0b9f\u0bc1\u0bb2\u0bbf",
                     "chat_model": "new"},
                ],
            }},
        }],
    }
    rejudged = load(_file(stale_doc))
    check("a stored verdict is re-derived on read, never trusted",
          rejudged.by_query["q"]["oty"]["text"] == "\u0b85\u0b9f\u0bc1\u0bb2\u0bbf",
          f"got {rejudged.by_query['q']['oty']['text']!r} — the file said the "
          f"first attempt was fine and the current guard says it is not")
    check("the reader records which rows disagreed with the file",
          [(q, l) for q, l, _ok in rejudged.stale] == [("q", "oty")],
          f"{rejudged.stale}")
    # .get, not [] — a mutation that skips the re-derivation leaves the row
    # without these keys, and a KeyError here would CRASH the suite, which the
    # mutation harness reads as "no failures".
    check("a clean attempt beside a stale one is promoted without a call",
          rejudged.by_query["q"]["oty"].get("chat_model") == "new"
          and rejudged.by_query["q"]["oty"].get("ok") is True,
          f"{rejudged.by_query['q']['oty'].get('chat_model')!r}")
    check("a file whose verdicts already match the guard reports nothing stale",
          load(_file(good)).stale == [], f"{load(_file(good)).stale}")

    superseded = _json.loads(_json.dumps(good))
    superseded["schema"] = sorted(SUPERSEDED_SCHEMAS)[0]
    try:
        load(_file(superseded))
        raised = ""
    except RenderingError as exc:
        raised = str(exc)
    check("a rendering file under a superseded schema is refused by the reader",
          "superseded" in raised and "build_query_renderings" in raised,
          "a v1 row holds one text and no history, so a run could not say "
          "whether a rendering had been retried or what the retry replaced")


def test_the_fusion_is_a_max_and_says_what_won() -> None:
    """C2, Block C ruling 13. Declared before any call was spent."""
    from retrieve.fuse import FusionError, fuse, fusion_report, pool_problems

    def hits(*rows):
        return [StubHit(c, c.split("::")[0], s) for c, s in rows]

    # The fixture is built so that NEITHER "first variant wins" nor "last
    # variant wins" reproduces the max, and so that insertion order is not
    # score order. A fixture where the max happens to be the last value tests
    # the word "max" and not the behaviour.
    #
    #            en     grc    fused   won by
    #   doc-a   0.50   0.55    0.55    grc      a rendering wins
    #   doc-b   0.60   0.30    0.60    en       the query's own text wins
    #   doc-c   0.10   0.70    0.70    grc      a rendering wins, from last place
    en = hits(("doc-a::original::000", 0.50), ("doc-b::original::000", 0.60),
              ("doc-c::original::000", 0.10))
    grc = hits(("doc-a::original::000", 0.55), ("doc-b::original::000", 0.30),
               ("doc-c::original::000", 0.70))

    f = fuse([("en", en), ("grc", grc)], None)
    by_id = {h.chunk_id: h.similarity for h in f.hits}
    check("a candidate takes the BEST score any variant gave it",
          abs(by_id["doc-b::original::000"] - 0.60) < 1e-9
          and abs(by_id["doc-c::original::000"] - 0.70) < 1e-9
          and abs(by_id["doc-a::original::000"] - 0.55) < 1e-9,
          f"{ {k: round(v, 2) for k, v in by_id.items()} }")
    check("the fused order is by fused score, not by any one variant's order",
          [h.chunk_id for h in f.hits] == ["doc-c::original::000",
                                           "doc-b::original::000",
                                           "doc-a::original::000"],
          "insertion order here is doc-a, doc-b, doc-c — deliberately not the "
          "score order, so an unsorted emit cannot pass")
    check("the run records WHICH variant won each candidate",
          f.lang_of("doc-a::original::000") == "grc"
          and f.lang_of("doc-b::original::000") == "en"
          and f.lang_of("doc-c::original::000") == "grc")
    check("fusing never invents or loses a candidate",
          f.n_candidates == 3 and len(f.hits) == 3)

    # The query's own text is declared first, so a rendering that merely equals
    # it must not be recorded as having beaten it.
    tie = fuse([("en", hits(("c::original::000", 0.7))),
                ("grc", hits(("c::original::000", 0.7)))], None)
    check("a tie keeps the query's own text, which is always declared first",
          tie.lang_of("c::original::000") == "en")

    # Ruling 13's exactness condition, asserted rather than trusted.
    try:
        fuse([("en", en)], 50)
        refused = ""
    except FusionError as exc:
        refused = str(exc)
    check("fusion REFUSES to run over truncated result lists",
          "unknown" in refused.lower() and "50" in refused,
          "a max over survivors favours whatever the truncation kept")
    try:
        fuse([], None)
        raised = False
    except FusionError:
        raised = True
    check("fusing no variants at all is a loud failure", raised)

    check("variants searched under different filters are refused",
          any("never comparable" in p for p in
              pool_problems([("en", en), ("grc", grc[:2])])))
    check("one variant language appearing twice is refused",
          any("twice" in p for p in pool_problems([("en", en), ("en", en)])))
    check("variants of equal size and distinct language pass silently",
          pool_problems([("en", en), ("grc", grc)]) == [])

    report = fusion_report(sorted(en, key=lambda h: -h.similarity), f)
    check("the run records what the fusion moved in the top six",
          report["moved"] == 3 and report["candidates"] == 3
          and report["entered_top6"] == [],
          f"{report}")
    check("the run records how many of the top six a RENDERING claimed",
          report["won_by_rendering"] == 2
          and report["won_by_lang"] == {"en": 1, "grc": 2},
          "if this is zero, C2 changed nothing the reader would see, whatever "
          "the aggregate gap says")


def test_the_two_arm_report_cannot_kill_a_run() -> None:
    """Ruling 14's printer, exercised because printing has destroyed a run here.

    On 2026-08-16 a KeyError in `print_report` killed the process before
    `archive()` and a twenty-six-minute reranked run was lost. Archiving now
    happens first, so a crash here costs the terminal output and not the
    evidence — but `_print_fused` is a new printer full of `.get`s over
    aggregates that are empty on a dry run, None when no pair ranked, and
    partial when only one intervention is on. It is the exact shape of the thing
    that already cost a day, so it is called here over the degenerate cases
    rather than trusted.
    """
    import io
    from contextlib import redirect_stdout

    from eval.run_ranking_check import Report, _print_fused, print_report

    def pair(pid, rank, fused=False, gap=0.02):
        r = score_pair(StubPair(id=pid, expect_lang="grc"),
                       [StubHit("doc-a::original::000", "doc-a", 0.9),
                        StubHit("doc-b::original::000", "doc-b", 0.9 - gap)],
                       "doc-a::original::000" if rank else "nowhere")
        r.fused = fused
        r.fused_from_lang = "grc" if fused else None
        return r

    for label, build in (
        ("no fused pairs at all", lambda rep: None),
        ("fused pairs but empty aggregates", lambda rep: rep.pairs_fused.append(pair("a", 1, True))),
        ("a pair that never ranked, so the gaps are None", lambda rep: (
            rep.pairs.append(pair("b", 0)), rep.pairs_fused.append(pair("b", 0, True)))),
    ):
        report = Report(timestamp="t", view="v", search_k=1, index_chunks=1,
                        embedding_models=[], query_embedding_model="")
        report.fused = True
        report.pairs.append(pair("a", 1))
        build(report)
        report.aggregate = summarise(report.pairs)
        if report.pairs_fused:
            report.aggregate_fused = summarise(report.pairs_fused)
            report.units_fused = build_units(report.pairs_fused)
            report.aggregate_units_fused = summarise_units(report.units_fused)
        report.units = build_units(report.pairs)
        report.aggregate_units = summarise_units(report.units)
        try:
            with redirect_stdout(io.StringIO()):
                _print_fused(report)
                print_report(report)
            crashed = ""
        except Exception as exc:            # noqa: BLE001 — that IS the test
            crashed = f"{type(exc).__name__}: {exc}"
        check(f"the two-arm report survives: {label}", not crashed, crashed)

    # Ruling 14's verdict line must not call a fused gap a win when it is not.
    report = Report(timestamp="t", view="v", search_k=1, index_chunks=1,
                    embedding_models=[], query_embedding_model="")
    report.fused = True
    report.pairs = [pair("a", 1, gap=0.05)]
    report.pairs_fused = [pair("a", 1, True, gap=0.01)]
    report.aggregate = summarise(report.pairs)
    report.aggregate_fused = summarise(report.pairs_fused)
    report.units = build_units(report.pairs)
    report.aggregate_units = summarise_units(report.units)
    report.units_fused = build_units(report.pairs_fused)
    report.aggregate_units_fused = summarise_units(report.units_fused)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        _print_fused(report)
    printed = buffer.getvalue()
    check("a fused gap narrower than the single-variant arm is NOT called a win",
          "NOT a C2 win" in printed,
          "\n".join(line for line in printed.splitlines() if "->" in line))
    # Asserted on a language ROW, not on the heading. A check that greps for
    # the heading passes against a report that prints the heading and no rows —
    # which is exactly what the first mutation written for it produced, and it
    # was reported as an unwatched guard.
    check("the report prints per-language recall for both arms",
          any(line.strip().startswith("grc") and "->" in line
              for line in printed.splitlines()),
          "an aggregate win that loses Chinese is a loss")


def test_a_lost_gold_pair_kills_the_run() -> None:
    """FINDING 12, guarded. The denominator is a fact about the gold file.

    On 2026-08-22 both Weilue pairs stopped resolving, left the run, and the
    harness reported it as `"31 pairs, 29 distinct query text(s) embedded"`.
    Every aggregate then moved because the denominator had shrunk — via-original
    reranked read `22/30 -> 21/29`, which reads like a regression and is a lost
    pair. The `unresolvable` list was archived correctly and the NOT MEASURED
    block WAS printed, thirty lines below the aggregates, under exit code 0.

    So the assertions here are about the RUN DYING, not about the fault being
    recorded. Recording it was never the part that was missing.
    """
    print("\nFINDING 12: a gold pair that stops resolving")

    from eval.run_ranking_check import unresolved_pair_problem

    # The ids are distinctive on purpose. A stub called "c" would be found in
    # every sentence of the message by `in`, so a message that stopped naming
    # the pair would still pass — the fixture-where-the-max-is-the-last-value
    # trap, one layer down.
    GONE = "china-describes-rome-weilue"
    pairs = [StubPair(id="alpha"), StubPair(id="beta"), StubPair(id=GONE)]
    everything = {p.id: (f"{p.id}::0", "t") for p in pairs}
    lost = {"alpha": ("alpha::0", "t"), "beta": ("beta::0", "t")}
    because = [{"id": GONE, "chunks": [],
                "reason": "the index holds no chunk containing this pair's "
                          "characters"}]

    check("a run in which every gold pair resolves is not disturbed",
          unresolved_pair_problem(pairs, everything, [], set()) is None)

    problem = unresolved_pair_problem(pairs, lost, because, set())
    check("GUARD a gold pair that stops resolving kills the run",
          problem is not None,
          "the 21/29 archive is what this looks like when it does not")

    # Naming it is the whole guard. "2 pairs did not resolve" is roughly what
    # the harness printed on 2026-08-22 and it is not something a reader can
    # act on. The message has to say WHICH pair and WHY.
    check("the killed run names the pair and why it did not resolve",
          bool(problem) and GONE in problem and "no chunk containing" in problem,
          problem or "")
    # 3, not 2. Denominated in the gold file, because the number the reader is
    # being warned about is the one that moved underneath them.
    check("the message counts against the gold file, not against what resolved",
          bool(problem) and "of 3 gold pair(s)" in problem,
          problem or "")

    check("a pair named in --allow-unresolvable is allowed through",
          unresolved_pair_problem(pairs, lost, because, {GONE}) is None)

    # The second rule, and it is not decoration. An allowance nobody removed is
    # a standing permission for the NEXT pair to vanish quietly — this defect
    # wearing the uniform of its own fix.
    stale = unresolved_pair_problem(pairs, everything, [], {GONE})
    check("GUARD an allowance naming a pair that resolves is itself refused",
          stale is not None and GONE in (stale or ""),
          stale or "the allowance was accepted against a pair that resolved")

    # A pair can leave `resolved` without `resolve_targets` classifying why.
    # Reading the denominator off `unresolvable` would miss such a pair in both
    # lists at once — the same blindness, one level down.
    silent = unresolved_pair_problem(pairs, lost, [], set())
    check("GUARD a pair missing from the unresolvable list still kills the run",
          silent is not None and GONE in (silent or ""),
          silent or "")

    # WHERE it fires, asserted against the source rather than described in a
    # comment. Dying after the batched embedding and the twenty-six-minute
    # rerank would still be a guard; it would just be one that costs the run it
    # refuses to publish. A rule, checked at check time, because an enumeration
    # maintained by hand will be wrong.
    source = (Path(__file__).resolve().parent / "run_ranking_check.py").read_text(
        encoding="utf-8")
    guard_at = source.find("problem = unresolved_pair_problem(")
    embed_at = source.find("embedded = embed_texts(")
    check("the guard fires BEFORE anything is embedded",
          0 < guard_at < embed_at,
          f"guard at {guard_at}, embedding at {embed_at}")


def test_report_prose_derives_every_rank_it_states() -> None:
    """FINDING 43, F3, fixed in F4: a rank stated in English that no check read.

    The coverage prose printed `at rank 309` as a string literal for weeks. It
    printed 309 while its own table said 313, and 309 while the baseline-view
    table said 54 -- two views, twenty minutes apart, one number. Nothing was
    wrong with the tables.

    Two assertions, and they are different rules. The first is about the ONE
    sentence: it must derive its rank from the run's pairs and name the view it
    was measured in, so the sentence stays true when lifted into a document
    beside another run. The second is about the MODULE: no string literal in it
    may state a rank at all, which is the guard that stops the next sentence
    from being written the same way. `run_ranking_check.py:471` records that
    this confusion has bitten here before at the level of data; this is the
    same rule for prose.
    """
    import ast as _ast
    import re as _re

    from eval import run_ranking_check as rc

    class _P:
        def __init__(self, pid, rank): self.id, self.rank = pid, rank

    pairs = [_P("tc-jabal-dabub", 3),
             _P(rc.BROKEN_CROSSLINGUAL_PAIR, 313)]
    phrase = rc.broken_link_phrase(pairs, rc.VIEW_WITH_DISTRACTORS)
    check("GUARD the coverage prose derives the broken link's rank from THIS "
          "run's pairs", "313" in phrase and "309" not in phrase, phrase)
    check("GUARD the coverage prose names the view its rank was measured in",
          rc.VIEW_WITH_DISTRACTORS in phrase, phrase)

    other = rc.broken_link_phrase([_P(rc.BROKEN_CROSSLINGUAL_PAIR, 54)],
                                  rc.VIEW_BASELINE)
    check("the same pair at a different rank in a different view produces a "
          "different sentence", "54" in other and rc.VIEW_BASELINE in other,
          other)

    absent = rc.broken_link_phrase([_P("tc-jabal-dabub", 3)],
                                   rc.VIEW_WITH_DISTRACTORS)
    check("a run whose pairs do not include it states no rank rather than the "
          "last one anybody saw",
          "rank" not in absent or "no rank" in absent, absent)

    # The module-level rule. Comments and this test are not the target: a
    # literal rank in a STRING is what gets printed into a report and quoted
    # into a document.
    source = Path(rc.__file__).read_text(encoding="utf-8")
    offenders = []
    for node in _ast.walk(_ast.parse(source)):
        if isinstance(node, _ast.Constant) and isinstance(node.value, str):
            if _re.search(r"\brank\s+\d", node.value):
                offenders.append(node.value.strip()[:60])
    check("GUARD no string in run_ranking_check.py states a literal rank; a "
          "report derives every rank it prints", not offenders,
          f"{len(offenders)} offender(s): {offenders[:3]}")


def test_ruling_54_stamp_is_a_field_and_its_absence_is_the_claim() -> None:
    """Ruling 54's exclusion, held as a field rather than as prose.

    F3 added six records and wrote no ranking pair for any of them. They are
    given pairs in F4 Part 2, and the ruling says each one is stamped, is
    excluded from every before/after claim, and may not be cited as evidence
    that F3 improved retrieval.

    A note saying so would have been cheaper and would have excluded nothing.
    The whole of ruling 54's argument is that ORDER is the remedy and that
    intention is not, which needs the order to be readable by something other
    than a person who remembers it -- so the stamp is a loader-validated field,
    it is carried onto the RESULT so it survives into the archive, and the run
    prints it under its own heading every time.

    The asymmetry is the point and it is asserted here: the flag may be TRUE or
    ABSENT, never false. A field that can be written false is a field somebody
    writes false, and then the claim made by every unstamped pair in this file
    -- that it was written before its record had ever been ranked -- becomes a
    claim anyone can forge by typing a word.
    """
    import io
    import json
    import tempfile
    from contextlib import redirect_stdout

    from eval.run_ranking_check import Report, print_report

    base = json.loads((Path(__file__).parent / "gold" / "ranking_pairs.json")
                      .read_text(encoding="utf-8"))

    def load_variant(mutate) -> Exception | None:
        data = json.loads(json.dumps(base))
        mutate(data)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
            path = Path(fh.name)
        try:
            load_ranking_pairs(path)
            return None
        except GoldSetError as exc:
            return exc
        finally:
            path.unlink(missing_ok=True)

    KEY = "written_after_the_records_entered_the_index"

    check("an explicit false stamp is REFUSED -- absence is the claim",
          load_variant(lambda d: d["pairs"][0].__setitem__(KEY, False)) is not None)

    check("a truthy string is not a stamp",
          load_variant(lambda d: d["pairs"][0].__setitem__(KEY, "yes")) is not None)

    check("a stamp of 1 is not a stamp either",
          load_variant(lambda d: d["pairs"][0].__setitem__(KEY, 1)) is not None)

    pairs = load_ranking_pairs()
    stamped = [p for p in pairs if getattr(p, KEY)]

    # NOT a census of which pairs are stamped. FINDING 47: an assertion that
    # photographs the data has to be edited every time the data improves, and
    # this file will gain stamped pairs whenever a record is paired late. What
    # is asserted is the PROPERTY every stamped pair must have.
    check("the debt is paid -- at least one pair carries the stamp",
          bool(stamped), f"{len(pairs)} pairs, none stamped")

    check("every stamped pair says in source_ref when it was written and "
          "against what",
          all(p.source_ref.strip() for p in stamped),
          [p.id for p in stamped if not p.source_ref.strip()])

    check("every stamped pair names ruling 54 in its own note, so the "
          "exclusion travels with the row",
          all("54" in p.note for p in stamped),
          [p.id for p in stamped if "54" not in p.note])

    # The stamp reaches the RESULT, not only the gold file. A run archived
    # today is read by somebody who has the JSON and not the reasoning.
    stub = StubPair(id="late", expect_doc="doc-a")
    stub.written_after_the_records_entered_the_index = True
    result = score_pair(stub,
                        [StubHit("doc-a::original::000", "doc-a", 0.9)],
                        "doc-a::original::000")
    check("the stamp is carried onto the pair RESULT and into the archive",
          result.written_after_the_records_entered_the_index)

    def printed(results) -> str:
        report = Report(timestamp="t", view="v", search_k=1, index_chunks=1,
                        embedding_models=[], query_embedding_model="")
        report.pairs = results
        report.aggregate = summarise(report.pairs)
        report.units = build_units(report.pairs)
        report.aggregate_units = summarise_units(report.units)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            print_report(report)
        return buffer.getvalue()

    blind = score_pair(StubPair(id="written-blind", expect_doc="doc-a"),
                       [StubHit("doc-a::original::000", "doc-a", 0.9)],
                       "doc-a::original::000")

    out = printed([blind, result])
    # Asserted on the ruling 54 BLOCK, never on the whole report. Every pair is
    # named in the per-pair table above, so a check that greps the REPORT for a
    # pair id passes against a printer whose exclusion block is empty -- which
    # is not a hypothetical: it is what the first version of this assertion did,
    # and scripts/mutate_ranking.py caught it on the mutation that empties the
    # block. The guard that greps the widest text is the guard that fails last.
    block_printed = out.split("ruling 54")[-1]
    check("the exclusion block NAMES each stamped pair rather than counting them",
          "late" in block_printed, block_printed)
    check("the exclusion block does not name a pair that was written blind",
          "written-blind" not in block_printed, block_printed)
    check("the report states what may NOT be done with a stamped pair",
          "may" in block_printed and "NOT" in block_printed, block_printed)

    out_none = printed([blind])
    check("a run with no stamped pair SAYS SO rather than printing nothing",
          "no pair in this run was written after" in out_none, out_none)

    # FINDING 49, one directory over: mutate_ranking names guards as exact
    # strings, so a printed label carrying a computed number is a label the
    # harness stops being able to name the moment the gold set grows -- which,
    # from ruling 54 onward, is every tranche.
    source = (Path(__file__).parent / "run_ranking_check.py").read_text(
        encoding="utf-8")
    block = source.split("def _print_ruling_54")[1].split("\ndef ")[0]
    check("GUARD ruling 54's printer states no literal pair count",
          not any(tok.isdigit() and tok not in ("54",)
                  for line in block.splitlines() if "print(" in line
                  for tok in line.replace('"', " ").replace("'", " ").split()),
          [line.strip() for line in block.splitlines() if "print(" in line])


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
    test_a_section_is_one_record_and_it_is_the_original()
    test_the_paced_client_waits_before_the_call_not_after_the_refusal()
    test_post_rerank_units_are_scored_over_the_whole_gate()
    test_the_via_original_companion_is_measured_at_both_points()
    test_the_query_rendering_rule_cannot_see_the_answer()
    test_the_fusion_is_a_max_and_says_what_won()
    test_the_two_arm_report_cannot_kill_a_run()
    test_a_lost_gold_pair_kills_the_run()
    test_report_prose_derives_every_rank_it_states()
    test_ruling_54_stamp_is_a_field_and_its_absence_is_the_claim()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for name in FAIL:
            print(f"  FAILED: {name}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
