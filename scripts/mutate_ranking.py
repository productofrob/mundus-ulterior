"""Mutation-verify the W2a ranking metrics (PHASE2_PLAN.md Block B2).

Each mutation breaks exactly one thing and asserts that the check protecting it
— and specifically that one, not merely *a* check — reports FAIL. The whole
reason this file exists is written into `eval/test_ranking_check.py`: a
recall@6 that cannot fail reads exactly like a recall@6 that passes.

Two mutation targets, deliberately:

  eval/run_ranking_check.py   the metrics — rank, recall, MRR, the two gaps
  eval/goldset.py             the loader's strictness — the gold set's own floor

The second matters as much as the first. Every number in a ranking run is
denominated in the gold set, so a loader that quietly accepts a set of three
Greek pairs produces a clean-looking baseline for a corpus of one language.

Run: python scripts/mutate_ranking.py
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECK = ROOT / "eval" / "run_ranking_check.py"
GOLDSET = ROOT / "eval" / "goldset.py"
# Added 2026-08-14. The view the ranking reads lives here, and the defect that
# made the whole 450-chunk rung unmeasurable was a hardcoded view in this file
# disagreeing with the one the checker counted. A mutation target the harness
# cannot reach is a guard nobody has watched fail.
SEARCH = ROOT / "retrieve" / "search.py"
# Added 2026-08-16 for C3. The reorder, the response parser and the lang_pool
# guard all live here, and they are the three places where a reranked run could
# produce a plausible number about the wrong candidates.
RERANK = ROOT / "retrieve" / "rerank.py"
# Ruling 8's collapse. It decides which chunk retrieval RETURNS, so it decides
# whether a G2 recall number is about the passage the pair names.
COLLAPSE = ROOT / "retrieve" / "collapse.py"
# Ruling 13's fusion. It decides the SIMILARITY every gap is denominated in
# under C2, which makes it the one file that can move the gap criterion -- the
# outstanding half of G2 -- without moving a single rank anybody would notice.
FUSE = ROOT / "retrieve" / "fuse.py"
# Added 2026-08-16 for C2. The language rule is the one place the leakage trap
# can be sprung — a target language chosen by reading the pair's `expect_lang`
# produces a beautiful curve that measures nothing — and it is invisible in
# every rank the run prints. A guard on that nobody has watched fail is worth
# as much as no guard at all.
RENDER = ROOT / "retrieve" / "render.py"
# The render prompt's writing-system rule lives here, beside the
# back-translation rule it is read from. Getting it wrong is the Part 4
# chrF-0.004 incident moved to a place where it produces a bad rank rather than
# a bad row.
TRANSLATE = ROOT / "answer" / "translate.py"
SOURCES = (CHECK, GOLDSET, SEARCH, RERANK, COLLAPSE, RENDER, TRANSLATE, FUSE)

SUITE = "eval.test_ranking_check"

MUTATIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "rank reported 0-indexed",
        [("        if h.chunk_id == target_chunk_id:\n            rank = i",
          "        if h.chunk_id == target_chunk_id:\n            rank = i - 1")],
    ),
    (
        "recall@6 made inclusive at rank 7",
        [("        recall_at_6=bool(rank and rank <= RECALL_AT),",
          "        recall_at_6=bool(rank and rank <= RECALL_AT + 1),")],
    ),
    (
        "MRR@10 scores a target past rank 10 as 1/rank",
        [("        rr_at_10=(1.0 / rank) if (rank and rank <= MRR_AT) else 0.0,",
          "        rr_at_10=(1.0 / rank) if rank else 0.0,")],
    ),
    (
        "the two gaps collapsed into one — siblings no longer excluded",
        [("    others_doc = [h for h in hits if h.doc_id != p.expect_doc]",
          "    others_doc = [h for h in hits if h.chunk_id != target_chunk_id]")],
    ),
    (
        "top1_to_rank6 measured over the whole result instead of six hits",
        [("        spread = hits[0].similarity - hits[RECALL_AT - 1].similarity",
          "        spread = hits[0].similarity - hits[-1].similarity")],
    ),
    (
        "an unranked target treated as a zero measurement rather than none",
        [("    sim_target = hits[rank - 1].similarity if rank else None",
          "    sim_target = hits[rank - 1].similarity if rank else 0.0")],
    ),
    (
        "the archived observed_chunk_id used as the scoring target",
        [("""    rank = None
    for i, h in enumerate(hits, start=1):
        if h.chunk_id == target_chunk_id:""",
          """    rank = None
    target_chunk_id = p.observed_chunk_id or target_chunk_id
    for i, h in enumerate(hits, start=1):
        if h.chunk_id == target_chunk_id:""")],
    ),
    (
        "aggregate mean treats a missing gap as zero",
        [("""def _mean(values):
    vals = [v for v in values if v is not None]
    return (sum(vals) / len(vals)) if vals else None""",
          """def _mean(values):
    vals = [0.0 if v is None else v for v in values]
    return (sum(vals) / len(vals)) if vals else None""")],
    ),
    (
        "a fixed search depth compiled back in",
        [("SEARCH_K = None  # None means \"the whole view\"; see _search_depth()",
          "SEARCH_K = 50  # None means \"the whole view\"; see _search_depth()")],
    ),
    (
        "loader accepts unknown keys, so a misspelled assertion disappears",
        [("        _check_keys(raw, _PAIR_REQUIRED, _PAIR_OPTIONAL, where)",
          "        _check_keys(raw, _PAIR_REQUIRED, _PAIR_OPTIONAL | set(raw), where)")],
    ),
    (
        "loader accepts an empty expect_text_contains",
        [("""        if not str(raw["expect_text_contains"]).strip():""",
          """        if False:""")],
    ),
    (
        "loader drops the seven-region requirement",
        [("    if len(regions) < 7:", "    if False:")],
    ),
    (
        "loader drops the twenty-pair floor",
        [("    if len(pairs) < 20:", "    if False:")],
    ),
    (
        "loader accepts a pair whose expect_lang its own pool excludes",
        [("        if langs is not None and raw.get(\"expect_lang\") and raw[\"expect_lang\"] not in langs:",
          "        if False:")],
    ),
    # ----------------------------------------------------------------------
    # Block C. The first three below move the gate's DENOMINATOR, which is the
    # one quantity in this file that decides whether W3 starts. The plan itself
    # got that arithmetic wrong — it collapsed one shared query and left the
    # other expanded — so these exist to make the same slip fail loudly.
    # ----------------------------------------------------------------------
    (
        "unit scoring collapsed: every pair is its own unit again",
        [("        unit = r.unit or r.id", "        unit = r.id")],
    ),
    (
        "a unit scored on its WORST acceptable target instead of its best",
        [("        best = min(ranked, key=lambda m: m.rank_accepted) if ranked else None",
          "        best = max(ranked, key=lambda m: m.rank_accepted) if ranked else None")],
    ),
    (
        # Coverage is the entire honesty cost of ruling 1. Counting every target
        # as covered turns "1 of 3 targets reached" into "3 of 3" and the number
        # that was supposed to print the ruling's cost prints a clean sheet.
        "coverage counts every target as reached",
        [("        hits = sum(1 for m in members if m.recall_at_6_accepted)",
          "        hits = len(members)")],
    ),
    (
        # Ruling 2 must not reach backwards into the baseline. The gaps and the
        # B2-comparable aggregate are all denominated in `recall_at_6`; letting
        # the alternate set it would silently restate every number recorded in
        # Block B as though the ruling had always been in force.
        "the aligned alternate quietly redefines the pre-ruling recall",
        [("        recall_at_6=bool(rank and rank <= RECALL_AT),",
          "        recall_at_6=bool(rank_accepted and rank_accepted <= RECALL_AT),")],
    ),
    (
        "an alternate admitted on positional alignment, not section alignment",
        [("            if aligned.ground == \"section\":", "            if True:")],
    ),
    (
        "loader accepts a unit spanning two different questions",
        [("        if len(queries) > 1:", "        if False:")],
    ),
    (
        "loader accepts a shared query that declares no unit",
        [("        if len(members) > 1 and len(units) > 1:", "        if False:")],
    ),
    (
        # The 2026-08-14 defect: the run counted one view and ranked another,
        # and every individual number was correct. This is the assertion that
        # compares them.
        "a run no longer checks that it can reach the index it names",
        [("    if n_hits == n_index:\n        return []",
          "    if True:\n        return []")],
    ),
    (
        "the searchable-view allowlist accepts anything",
        [("    if view not in SEARCHABLE_VIEWS:\n        raise ValueError(\n"
          "            f\"{view!r} is not a searchable view. Known: \"",
          "    if False:\n        raise ValueError(\n"
          "            f\"{view!r} is not a searchable view. Known: \"")],
    ),
    # ----------------------------------------------------------------------
    # Block C3. The cross-encoder is a recall intervention, so the failures
    # worth mutating are the ones that would let it report a recall about
    # something other than what it measured: a baseline quantity overwritten, a
    # pool the pair excluded, a partial response rendered as a ranking, or a
    # denominator smaller than the gate's.
    # ----------------------------------------------------------------------
    (
        "the post-rerank rank quietly overwrites `rank`",
        [("    result.rank_reranked = rank_of(ordering, [result.resolved_chunk_id])",
          "    result.rank_reranked = rank_of(ordering, [result.resolved_chunk_id])\n"
          "    result.rank = result.rank_reranked")],
    ),
    (
        "the rerank window truncates the ranking instead of reordering it",
        [("    return [head[i] for i, _ in scored] + tail",
          "    return [head[i] for i, _ in scored]")],
    ),
    (
        "a partial rerank response is reordered as though it were complete",
        [("    if named != list(range(len(head))):", "    if False:")],
    ),
    (
        "rerank ties broken in reverse of the pre-rerank order",
        [("    scored.sort(key=lambda pair: (-pair[1], pair[0]))",
          "    scored.sort(key=lambda pair: (-pair[1], -pair[0]))")],
    ),
    (
        "a rerank result index outside the submitted set accepted",
        [("        if not 0 <= idx < n_documents:", "        if False:")],
    ),
    (
        "a target below the window scored 0.0 instead of none",
        [("    result.rerank_score_target = scores.get(result.resolved_chunk_id)",
          "    result.rerank_score_target = scores.get(result.resolved_chunk_id) or 0.0")],
    ),
    (
        "post-rerank recall averaged over the reranked units, not the gate",
        [('            "recall_at_6_reranked": sum(u.recall_at_6_reranked for u in units) / len(units),',
          '            "recall_at_6_reranked": sum(u.recall_at_6_reranked for u in reranked) / len(reranked),')],
    ),
    (
        "a unit counts as reranked if ANY of its pairs was",
        [("        reranked = bool(members) and all(m.reranked for m in members)",
          "        reranked = bool(members) and any(m.reranked for m in members)")],
    ),
    (
        "only the first rerank route is ever tried",
        [("    for path in paths:", "    for path in paths[:1]:")],
    ),
    (
        "a gateway refusal falls through to the response parser",
        [("            if status >= 400:", "            if False:")],
    ),
    (
        "the rate-limit backoff waits no time at all",
        [("                sleep(RATE_LIMIT_BACKOFF_SECONDS)", "                sleep(0)")],
    ),
    (
        "pacing never happens, so a throttled account is rediscovered every call",
        [("    if _LAST_CALL_AT[0] is None:\n        return 0.0\n    needed",
          "    if True:\n        return 0.0\n    needed")],
    ),
    (
        "the pacing wait is the time already spent, not the remainder",
        [("    return max(0.0, needed - (now - _LAST_CALL_AT[0]))",
          "    return max(0.0, (now - _LAST_CALL_AT[0]) - needed)")],
    ),
    (
        "the run stops recording what displaced a target",
        [("    for hit in ordering[:RECALL_AT]:\n        if hit.chunk_id in accepted:\n            break",
          "    for hit in ordering[:RECALL_AT]:\n        if True:\n            break")],
    ),
    (
        "token pacing takes the SHORTER of the two constraints",
        [("        needed = max(needed, 60.0 * last_tokens / tpm_budget)",
          "        needed = min(needed, 60.0 * last_tokens / tpm_budget)")],
    ),
    # ----------------------------------------------------------------------
    # C2a, ruling 8. Each of these produces a plausible collapsed ranking that
    # is about the wrong chunks — which is the only way this step can do harm,
    # since it cannot touch a gap and cannot add a chunk retrieval did not find.
    # ----------------------------------------------------------------------
    (
        "a section collapsed on positional alignment, not section alignment",
        [("        if ground not in COLLAPSIBLE_GROUNDS:\n            continue",
          "        if False:\n            continue")],
    ),
    (
        "the collapsed row is whichever member ranked higher, not the original",
        [("        canon_id = canonical.get(key, hit.chunk_id)",
          "        canon_id = hit.chunk_id")],
    ),
    (
        "a section is emitted once per member instead of once",
        [("        if key in seen:\n            continue", "        if False:\n            continue")],
    ),
    (
        "the collapse stops recording that a record was reached via English",
        [("        if key is None or key in entry:\n            continue",
          "        if key is None or True:\n            continue")],
    ),
    (
        "collapsing quietly overwrites `rank`",
        [("    result.rank_collapsed = rank_of(ordering, [result.resolved_chunk_id])",
          "    result.rank_collapsed = rank_of(ordering, [result.resolved_chunk_id])\n"
          "    result.rank = result.rank_collapsed")],
    ),
    (
        # Ruling 9's whole strictness: a document with TWO index groups is the
        # coincidence-of-counting case, and promoting it would fold a
        # NEIGHBOURING section's translation into a passage.
        "`sole` promotes any index group, not only the unambiguous one",
        [("        if (ground == \"index\" and len(members) == 1\n"
          "                and per_doc[canon.split(\"::\")[0]] == 1):",
          "        if ground == \"index\":")],
    ),
    (
        # Ruling 9's companion is the only number no translation-mediated fix
        # can raise. Counting a translation entry as an original entry is
        # exactly the inflation it exists to refuse.
        "a record reached via its translation counts as via-original",
        [('        and not (result.collapse_entry_role == "translation"\n                 and result.collapse_primary_role == "original")',
          '        and not (result.collapse_entry_role == "not-a-role"\n                 and result.collapse_primary_role == "original")')],
    ),
    (
        "every record's primary text is its original",
        [('    return "translation" if source_type in FIND_TYPES else "original"',
          '    return "original"')],
    ),
    (
        'a multi-member section guesses a member instead of falling back',
        [('        canonical[canon] = (members[0] if (wants == "translation"\n                                           and len(members) == 1) else canon)',
          '        canonical[canon] = (members[0] if wants == "translation" else canon)')],
    ),
    (
        'the via-original companion ignores whether a record HAS a source text',
        [('        and not (result.collapse_entry_role == "translation"\n                 and result.collapse_primary_role == "original")',
          '        and not (result.collapse_entry_role == "translation")')],
    ),
    (
        "the rerank summary reassigns its dict and drops the collapse keys",
        [("        extra.update({\n            \"reranked_units\":",
          "        extra = ({\n            \"reranked_units\":")],
    ),
    (
        "the lang_pool guard stops looking at the pool it is handed",
        [("    if langs:\n        wrong = sorted({h.lang for h in hits if h.lang not in set(langs)})",
          "    if False:\n        wrong = sorted({h.lang for h in hits if h.lang not in set(langs)})")],
    ),
    # ----------------------------------------------------------------------
    # C2 — rulings 12 / 15b / 17a / 19. Thirteen mutations, and the first two
    # are the reason this block exists: the leakage trap cannot be caught by
    # reading a rank, so the only thing that can catch it is a guard that has
    # been watched failing.
    # ----------------------------------------------------------------------
    (
        "the language rule renders a query into its own language",
        [('        if lang and lang != "en" and lang != query_lang',
          '        if lang and lang != "en"')],
    ),
    (
        "English becomes a render target for a non-English query",
        [('        if lang and lang != "en" and lang != query_lang',
          '        if lang and lang != query_lang')],
    ),
    (
        "the cost of the rule is computed over the whole index, not the rule",
        [("    return sum(len(target_langs(index_langs, q)) for q in query_langs)",
          "    return sum(len(index_langs) for q in query_langs)")],
    ),
    (
        "the script floor is lowered to nothing",
        [("SCRIPT_FLOOR = 1.0", "SCRIPT_FLOOR = 0.0")],
    ),
    (
        "one character of the right script passes the whole rendering",
        [("    return hits / len(counted)", "    return 1.0 if hits else 0.0")],
    ),
    (
        "the echo refusal is dropped",
        [("    if source_text and text.strip() == source_text.strip():",
          "    if False and text.strip() == source_text.strip():")],
    ),
    (
        "a rendering the script check refused is fused anyway",
        [('            if row.get("ok"):', "            if True:")],
    ),
    (
        "a query with no renderings degrades silently to the English-only arm",
        [("        entry = self.by_query.get(query)",
          "        entry = self.by_query.get(query) or {}")],
    ),
    (
        "the rendering file may name a pair after all",
        [('    if "pair_ids" in json.dumps(doc):', "    if False:")],
    ),
    (
        "the file may hold renderings the language rule never asked for",
        [("        if have - wanted:", "        if False:")],
    ),
    (
        "the coverage check stops comparing the file's index to the run's",
        [("    if sorted(set(index_langs)) != sorted(set(renderings.index_langs)):",
          "    if False:")],
    ),
    (
        "ruling 15b's native-language control reports nothing",
        [('    if query_lang == "en":\n        return []',
          "    if True:\n        return []")],
    ),
    (
        "a language may be rendered into itself at the call",
        [("    if target_lang == source_lang:", "    if False:")],
    ),
    (
        # Ruling 20. 0.6 is the value the first real run was made at, and it
        # admitted ten mixed-script renderings; this is that regression, kept
        # as a mutation so the raise can never be quietly undone.
        "the script floor is put back to the value that admitted mixed scripts",
        [("SCRIPT_FLOOR = 1.0", "SCRIPT_FLOOR = 0.6")],
    ),
    (
        "the Latin ranges lose the modifier letters transliteration needs",
        [("(0x02B0, 0x02FF), (0x1E00, 0x1EFF)),", "(0x1E00, 0x1EFF)),")],
    ),
    (
        "a retry re-issues the same prompt at temperature zero",
        [("    if retry:\n        system = system.replace(",
          "    if False:\n        system = system.replace(")],
    ),
    (
        # Ruling 21. This is the defect the retry pass created, kept as a
        # mutation: taking the newest attempt replaced a 98%-Tamil rendering
        # with a 5% one.
        "the newest attempt becomes the rendering, whatever it came back as",
        [("    return min(enumerate(attempts), key=key)[1]",
          "    return attempts[-1]")],
    ),
    (
        "a held attempt ranks equal with an admitted one",
        [('        return (0 if attempt.get("ok") else 1,', "        return (0,")],
    ),
    (
        "a tie between attempts keeps the later one, so a re-run churns",
        [("                -float(attempt.get(\"script_ratio\") or 0.0),\n                position)",
          "                -float(attempt.get(\"script_ratio\") or 0.0),\n                -position)")],
    ),
    (
        "a superseded rendering schema is read as though it were current",
        [("    if doc.get(\"schema\") in SUPERSEDED_SCHEMAS:", "    if False:")],
    ),
    (
        # Ruling 22. Unclassified, this arrives as a bare 400 that the retry
        # policy tries three times and then reports as "translation failed" —
        # 615 requests on the first chat-strong run before it was read by hand.
        "a temperature refusal is left unclassified",
        [('    lowered = (message or "").lower()', '    lowered = ""')],
    ),
    (
        "the temperature fallback applies whether or not a caller asked for it",
        [("            if temperature_fallback is None or used == temperature_fallback:",
          "            if temperature_fallback is None and False:")],
    ),
    (
        "the temperature fallback becomes the default for every caller",
        [("    temperature_fallback: float | None = None,",
          "    temperature_fallback: float | None = 1.0,")],
    ),
    (
        # Ruling 23b. Letters-only was the rule until the Malayalam vowel sign
        # in `adulis-exports` passed at "100% Tamil".
        "the script check counts letters only, as it did before ruling 23b",
        [('        elif category in ("Mn", "Mc", "Me") and not (',
          '        elif False and not (')],
    ),
    (
        "script-neutral diacritics are counted against the script that uses them",
        [("_NEUTRAL_MARKS = (0x0300, 0x036F)", "_NEUTRAL_MARKS = (0x0, 0x0)")],
    ),
    (
        "the fusion takes the LAST variant's score instead of the best",
        [("            if current is None or hit.similarity > current[0]:",
          "            if True:")],
    ),
    (
        "a tie promotes the later variant, so a no-op rendering reads as a win",
        [("            if current is None or hit.similarity > current[0]:",
          "            if current is None or hit.similarity >= current[0]:")],
    ),
    (
        "fusion proceeds over truncated result lists",
        [("    if search_k is not None:", "    if False:")],
    ),
    (
        "the fused list is emitted unsorted, in insertion order",
        [("    ordered = sorted(best.values(), key=lambda row: -row[0])",
          "    ordered = list(best.values())")],
    ),
    (
        "the fusion stops recording that a rendering beat the query's own text",
        [('        "won_by_rendering": sum(\n            1 for chunk_id in after\n            if fused.winning_lang.get(chunk_id) not in (None, own)\n        ),', '        "won_by_rendering": 0,')],
    ),
    (
        "variants searched under different filters are fused anyway",
        [("    if len(distinct) > 1:", "    if False:")],
    ),
    (
        "the reader trusts the verdict stored in the file",
        [("            settle_row(row, lang, entry[\"query\"])",
          "            pass")],
    ),
    (
        "the reader stops recording that a stored verdict was stale",
        [("            was_ok, was_text = row.get(\"ok\"), row.get(\"text\")",
          "            was_ok, was_text = None, None")],
    ),
    (
        "a fused gap is called a win without beating the same-run arm",
        [("        if fd <= sd:", "        if False:")],
    ),
    (
        "the two-arm report stops breaking recall down by language",
        [("    for lang in langs:", "    for lang in []:")],
    ),
    (
        "the render prompt drops its writing-system rule",
        [("""    if target_lang in TRANSLITERATED_LANGS:
        script_rule = _TRANSLITERATION_RULE
    elif target_lang in NATIVE_SCRIPT_LANGS:
        script_rule = _NATIVE_SCRIPT_RULE.format(script=NATIVE_SCRIPT_LANGS[target_lang])
    else:
        script_rule = ""

    system = SYSTEM_RENDER.format(""",
          """    script_rule = ""

    system = SYSTEM_RENDER.format(""")],
    ),
    # ------------------------------------------------------------------
    # C7 — the sequencing-trap fix. `recall@6 via the original text` was
    # computed pre-rerank while the adopted configuration reranks.
    # ------------------------------------------------------------------
    (
        # The archive is what makes this unrecoverable rather than merely
        # wrong: every run since ruling 9 holds the pre-rerank figure.
        "the post-rerank via-original silently overwrites the pre-rerank one",
        [("""    result.recall_at_6_via_original_reranked = bool(
        result.recall_at_6_accepted_reranked""",
          """    result.recall_at_6_via_original = bool(
        result.recall_at_6_accepted_reranked""")],
    ),
    (
        # Ruling 11 lives in the second clause. Without it, a source text
        # reached through its English counts as reached through its original —
        # the exact inflation ruling 9's companion exists to refuse.
        "the post-rerank predicate drops the primary-role clause",
        [("""        result.recall_at_6_accepted_reranked
        and not (result.collapse_entry_role == "translation"
                 and result.collapse_primary_role == "original")""",
          """        result.recall_at_6_accepted_reranked
        and not (result.collapse_entry_role == "translation")""")],
    ),
    (
        # A run that fell over between the collapse and the rerank would
        # otherwise be scored on a post-rerank figure it never measured.
        "the post-rerank unit gate reads `collapsed` instead of `reranked`",
        [("                via_original_rr if reranked else False),",
          "                via_original_rr if collapsed else False),")],
    ),
    (
        # Printing one of the two is how the trap looked in the first place.
        "the report prints only one of the two via-original figures",
        [("""              f"   ->   POST-rerank "
              f"{u['recall_at_6_via_original_reranked']:.3f} "
              f"({u['recall_at_6_via_original_reranked_n']}/{u['units']})")""",
          """              f"")""")],
    ),
    (
        # The other half of the predicate, and the one the English-bypass guard
        # reads. Added after the first run of this harness showed that guard had
        # no mutation behind it: dropping the primary-role clause tightens the
        # predicate and fires a different guard entirely, so the two clauses
        # need two mutations. The analogue of the pre-rerank mutation "a record
        # reached via its translation counts as via-original".
        "the post-rerank predicate stops recognising a translation entry",
        [("""        result.recall_at_6_accepted_reranked
        and not (result.collapse_entry_role == "translation\"""",
          """        result.recall_at_6_accepted_reranked
        and not (result.collapse_entry_role == "not-a-role\"""")],
    ),
]

EXPECTED = [
    "rank is 1-indexed",
    "a target at rank 7 does not",
    "a target past rank 10 scores 0 reciprocal rank, not 1/rank",
    "gap vs other DOC skips same-document siblings",
    "top1_to_rank6 is the spread over the first six hits",
    "an absent target has no similarity and therefore no gap",
    "scoring uses the resolved chunk, not the archived observed_chunk_id",
    "aggregate gap averages only the pairs that have one",
    "no fixed search depth is compiled in",
    "a misspelled key is a load-time error, not a weaker pair",
    "an empty expect_text_contains is rejected",
    "a gold set missing a region is rejected",
    "a gold set below twenty pairs is rejected",
    "a pair whose expect_lang is excluded by its own pool is rejected",
    "three pairs sharing a unit_id are one unit",
    "the unit is scored on its BEST acceptable target",
    "coverage reports the targets the unit does NOT reach",
    "the alternate does NOT move `rank`, which the baseline is denominated in",
    "an alternate is NOT admitted on positional alignment",
    "a unit grouping two different questions is rejected",
    "a pair sharing a query but declaring no unit is rejected",
    "a search that cannot reach the whole view is a loud failure",
    "an unknown view name is refused rather than interpolated",
    # Block C3
    "reranking does not touch `rank`, which every gap is denominated in",
    "a candidate below the rerank window keeps its pre-rerank position",
    "a partial rerank response is refused rather than reordered",
    "rerank ties break on the pre-rerank order, not arbitrarily",
    "a rerank result out of the submitted set is refused",
    "a target below the window has no reranker score, not a zero",
    "post-rerank recall is reported over ALL units, not only reranked ones",
    "a unit with any un-reranked pair is not scored as reranked",
    "a 404 on the first rerank route falls through to the second",
    "a gateway refusal is raised, never scored as an empty ranking",
    "a rate-limited rerank waits a full window and retries",
    # ORDER IS THE CONTRACT. This list is zipped against MUTATIONS positionally,
    # so an entry added to one list and not the other in the same place silently
    # mispairs EVERY entry after it — and the harness then reports a row of
    # MISSes that read like real failures. That happened on 2026-08-16: four
    # C2a guards were inserted here at a different offset than their mutations,
    # and eight mutations that all worked were reported as unwatched.
    "a paced client waits before the call, not after it is refused",
    "the wait is the remainder of the interval, not the time already spent",
    "the run records WHAT the cross-encoder put above the target",
    "the longer of the two pacing constraints wins",
    "only a section-aligned group becomes one record",
    "the row is the ORIGINAL even when the translation ranked higher",
    "each section appears exactly once",
    "the run records WHICH member of a section got there first",
    "collapsing does not touch `rank`, which every gap is denominated in",
    "an `index` group in a document with others stays refused",
    "a record reached via its translation does NOT count as via-original",
    "a find record's primary text is its curatorial description",
    "a multi-member section falls back to the original rather than guessing",
    "reaching a record with no source text is not counted as a bypass",
    "a run with BOTH collapse and rerank keeps BOTH sets of keys",
    "a pool that violates the pair's own lang filter is a loud failure",
    # C2 — fourteen, in the same order as the fourteen mutations above.
    "a query is never rendered into its own language",
    "English is never a render target — it is the single-variant arm",
    "ruling 12 costs exactly 205 renderings over this gold set",
    "ROMANISED Tamil is refused for oty — the Part 4 chrF-0.004 failure",
    "Literary Chinese inside an English sentence is refused for lzh",
    "a rendering identical to its query is refused as an echo",
    "a rendering the script check refused is never fused",
    "a query with no renderings raises rather than degrading silently",
    "a rendering file that mentions a pair id is refused outright",
    "a rendering the language rule never asked for is refused",
    "a file built against a different index is refused",
    "a rendering beating the native text on a native query is a finding",
    "rendering a language into itself is refused at the call",
    "a rendering admitted by the old 0.6 floor is refused at 1.0",
    "scholarly modifier letters do not make a Latin rendering foreign",
    "the retry prompt is a different prompt from the first",
    "a retry that came back worse does not become the rendering",
    "an admitted attempt beats a held one whatever the order",
    "among equals the earlier attempt is kept, so a re-run changes nothing",
    "a rendering file under a superseded schema is refused by the reader",
    "a temperature refusal is classified, not left as a mystery 400",
    "without an opt-in, a temperature refusal is raised and NAMED",
    "the temperature fallback is off by default, so archived paths stay greedy",
    "a foreign VOWEL SIGN inside a native word is refused",
    "script-neutral combining diacritics are not counted against anyone",
    "a candidate takes the BEST score any variant gave it",
    "a tie keeps the query's own text, which is always declared first",
    "fusion REFUSES to run over truncated result lists",
    "the fused order is by fused score, not by any one variant's order",
    "the run records how many of the top six a RENDERING claimed",
    "variants searched under different filters are refused",
    "a stored verdict is re-derived on read, never trusted",
    "the reader records which rows disagreed with the file",
    "a fused gap narrower than the single-variant arm is NOT called a win",
    "the report prints per-language recall for both arms",
    "the render prompt demands the Tamil script for oty",
    # C7 — in the same order as the four mutations appended above.
    "the pre-rerank via-original is not overwritten by the post-rerank one",
    # Mispaired on this harness's first C7 run, and it reported itself as list
    # drift. It was not drift: dropping the primary-role clause removes ruling
    # 11's exemption, which makes the predicate STRICTER, so the guard that
    # fails is the record-with-no-source-text one.
    "a rescued record with NO source text does count as via-original",
    "a unit whose pairs were not all reranked is refused the post-rerank figure",
    "the report prints BOTH via-original values, pre and post",
    "a record rescued into the top 6 through its ENGLISH is still not via-original",
]


def failures_from(output: str) -> set[str]:
    return {
        line.split("FAIL", 1)[1].strip()
        for line in output.splitlines()
        if line.strip().startswith("FAIL")
    }


# -B is a precaution, and the honest version of why it is here.
#
# On 2026-08-16 this harness reported guards as verified that it had not
# exercised: the failures of the PREVIOUS mutation arrived attached to the next
# one. The first suspect was bytecode caching — CPython validates a cached .pyc
# against its source's mtime AND SIZE, so a mutation that changes neither
# (`all(` -> `any(`, `min` -> `max`) written inside the same mtime second is
# invisible to the interpreter. That is a real mechanism and -B forecloses it.
#
# It was NOT what happened. The symptom appeared only when the harness was run
# against this repository over a NETWORK MOUNT, where a write is not reliably
# visible to a subprocess spawned immediately after it, and it never appeared on
# the host. Two things follow, and they are the actual findings:
#
#   * run this harness on the host, against a local filesystem, and nowhere else;
#   * never run two mutation harnesses over one working tree at once. Both
#     capture `originals` at start and both restore at exit, so the second
#     captures the first's mutation as the original and writes it back as the
#     restore. A killed harness does the same thing with no restore at all.
#
# -B stays because it costs nothing and closes the mechanism that was suspected.
# It is not credited with fixing anything, because nothing here measured it.


# A suite that DIED is not a suite that caught something. Every check after the
# crash never ran, and this harness reads FAIL lines out of stdout — so an
# uncaught exception reports as "no failures" and the mutation is recorded as
# unwatched. Distinguished here rather than diagnosed by hand, because that is
# how it presented on 2026-08-16 and it cost half an hour.
SUITE_CRASHED = "<the suite CRASHED instead of reporting a failure>"

# Where the last crash came from. Naming the crash was the 2026-08-16 fix; it
# stopped a died-suite reading as "no failures", but it still left you to
# reproduce the mutation by hand to find out WHY. The traceback is right there
# in the subprocess's stderr, and throwing it away cost another round trip the
# first time a mutation crashed on a machine the author could not reach.
LAST_CRASH = {"stderr": ""}


def run_suite() -> set[str]:
    # PYTHONIOENCODING is not decoration. Through a pipe on Windows the child's
    # stdout falls back to cp1252, and this suite's failure messages carry
    # Greek, Tamil and Chinese — so a guard whose detail is non-Latin raised
    # UnicodeEncodeError and DIED rather than printing FAIL. This harness reads
    # FAIL lines out of that pipe, so it saw a crash where there was a caught
    # failure, and reported a working mutation as unwatched. Both ends are
    # fixed: the child is told to write UTF-8, and the parent to read it.
    result = subprocess.run(
        [sys.executable, "-B", "-m", SUITE], cwd=ROOT, capture_output=True,
        text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    failures = failures_from(result.stdout)
    if result.returncode != 0 and not failures:
        LAST_CRASH["stderr"] = result.stderr
        return {SUITE_CRASHED}
    return failures


def main() -> int:
    if len(MUTATIONS) != len(EXPECTED):
        print(f"harness is inconsistent: {len(MUTATIONS)} mutations, "
              f"{len(EXPECTED)} expected guards")
        return 1

    originals = {f: f.read_text(encoding="utf-8") for f in SOURCES}
    problems: list[str] = []
    try:
        for (label, patches), guard in zip(MUTATIONS, EXPECTED):
            edited = dict(originals)
            missing = [old for old, _ in patches
                       if not any(old in originals[f] for f in SOURCES)]
            if missing:
                problems.append(f"{label}: mutation target not found in any source")
                print(f"  MISS {label} (target not found)")
                continue
            for old, new in patches:
                target = next(f for f in SOURCES if old in edited[f])
                edited[target] = edited[target].replace(old, new, 1)
            for f in SOURCES:
                f.write_text(edited[f], encoding="utf-8")

            failed = run_suite()
            if guard in failed:
                print(f"  ok   {label}")
                print(f"       -> {guard}")
            else:
                # A mutation that made the suite fail — just not on the guard
                # named for it — is almost never an unwatched mutation. It is
                # these two lists having drifted out of alignment, and saying so
                # is the difference between a one-line fix and an afternoon.
                drifted = bool(failed) and SUITE_CRASHED not in failed
                problems.append(
                    f"{label}: expected {guard!r} to fail, got "
                    f"{sorted(failed) or 'no failures'}"
                    + ("  <- the suite must FAIL on this mutation, not die on it"
                       if SUITE_CRASHED in failed else "")
                    + ("  <- DETECTED, by a different guard. Check that "
                       "MUTATIONS and EXPECTED are still in the same order."
                       if drifted else "")
                )
                if SUITE_CRASHED in failed:
                    tail = [line for line in
                            LAST_CRASH["stderr"].strip().splitlines() if line][-12:]
                    problems[-1] += "\n      " + "\n      ".join(tail)
                print(f"  MISS {label}"
                      + ("  (suite crashed)" if SUITE_CRASHED in failed else "")
                      + ("  (detected by another guard - list drift?)"
                         if drifted else ""))
    finally:
        for f in SOURCES:
            f.write_text(originals[f], encoding="utf-8")

    # Restore is verified by comparing content; a suite failure is a separate
    # finding and must not be reported as a corrupted working tree. Block 0
    # found all three existing mutation scripts conflating the two.
    unrestored = [f.name for f in SOURCES
                  if f.read_text(encoding="utf-8") != originals[f]]
    if unrestored:
        problems.append(
            "sources were NOT restored cleanly: " + ", ".join(unrestored)
            + " — restore from version control before running anything else"
        )

    check = subprocess.run(
        [sys.executable, "-B", "-m", SUITE], cwd=ROOT, capture_output=True, text=True
    )
    if check.returncode != 0:
        problems.append(
            f"sources restored, but `{SUITE}` fails on its own account — a "
            f"finding about the suite, not about this harness"
        )
        print(f"\n--- {SUITE} output, so it is not lost ---")
        print((check.stdout or "") + (check.stderr or ""), end="")
        print("--- end ---")

    print()
    if problems:
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"all {len(MUTATIONS)} mutations verified; sources restored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
