"""Mutation-verify the Part 8 gold-case guards.

Same standard as mutate_part7b.py and mutate_recover.py: each mutation breaks
exactly one fix and asserts that the guard protecting *that* fix reports FAIL,
not merely that something failed.

The mutations worth reading are the first two. They remove the rule that a case
must assert what an answer *says*, which is the rule that makes this harness
different from the exit code it replaces. If those two ever stop breaking their
guards, Part 8 has quietly become `assert grounding.ok` again.

Run: python scripts/mutate_part8.py
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys

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

ROOT = pathlib.Path(__file__).resolve().parent.parent

# The child prints failure detail carrying Greek, Tamil and Chinese. Through a
# pipe on Windows its stdout falls back to cp1252 and `print` raises; the parent
# decodes with the locale codec and raises in the other direction. Both ends are
# named because the ranking harness lost a run to exactly this, and this is the
# harness pair BLOCK_D_START records as never having been checked against it.
CHILD_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8",
             # FINDING 16, and see `_purge_bytecode` below for what it cost.
             "PYTHONDONTWRITEBYTECODE": "1"}
GOLDSET = ROOT / "eval" / "goldset.py"
EVAL = ROOT / "eval" / "answer_eval.py"
SOURCES = (GOLDSET, EVAL)


def _purge_bytecode() -> None:
    """FINDING 16, 2026-08-24. CPython validated a mutation away.

    A cached `.pyc` is keyed on its source's mtime SECOND and its source's
    SIZE. Two mutations that produce the same file size, written inside the
    same second, therefore share a cache key — and the second one runs the
    first one's bytecode.

    That is not hypothetical here. `scripts/mutate_ranking.py` has carried
    `-B` since 2026-08-16 with a note describing this exact mechanism as
    "a real mechanism" that "-B forecloses", and adding that it "is not
    credited with fixing anything, because nothing here measured it". This
    harness never got the flag.

    On 2026-08-24 it measured it. Mutations 39 and 40 —

        distinct dates are counted from session ids        (-2 bytes)
        a sweep with no session identity stops blocking …  (-2 bytes)

    — are the ONLY consecutive pair in this file with an identical size
    delta. Mutation 40 ran mutation 39's bytecode, reported mutation 39's
    failures, and was recorded as a MISS: a working guard reported as
    unwatched. The other direction is worse and equally available — a
    mutation whose guard genuinely does not fire, reported as verified
    because the previous mutation's failures arrived attached to it, which
    is precisely what 2026-08-16 saw and could not explain.

    So the comment's model needs one correction: the dangerous case is not a
    mutation that preserves the ORIGINAL's size. It is two CONSECUTIVE
    mutations that produce the same size as each other. That is far more
    common — mutating `["date"]` to `["id"]` and `undated` to `False` both
    remove two bytes — and nothing about it looks unusual.

    `-B` stops this process's children WRITING a cache. It does not stop them
    READING one an ordinary `python -m eval.test_answer_eval` left behind, so
    the directory is removed as well. Both, always: the flag alone is half a
    fix, which is a sentence this repository has now written three times.
    """
    for source in SOURCES:
        shutil.rmtree(source.parent / "__pycache__", ignore_errors=True)


MUTATIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "the content-assertion rule is removed entirely",
        [("""        if not _has_content_assertion(raw):""",
          """        if False:""")],
    ),
    (
        "the content-assertion rule is satisfied by groundedness alone",
        [("""def _has_content_assertion(raw: dict) -> bool:
    if any(raw.get(key) for key in _CONTENT_KEYS):
        return True""",
          """def _has_content_assertion(raw: dict) -> bool:
    if "expect_grounded" in raw:
        return True
    if any(raw.get(key) for key in _CONTENT_KEYS):
        return True""")],
    ),
    (
        "an empty alternatives group is allowed through",
        [("""            if not isinstance(group, list) or not group:""",
          """            if not isinstance(group, list) and not group:""")],
    ),
    (
        "a refusal no longer has to justify itself",
        [("""            if not str(raw.get("refusal_is_correct_because", "")).strip():""",
          """            if False:""")],
    ),
    (
        "a case may demand both a refusal and the content it excludes",
        [("""            if contradictory or minimum > 0:""", """            if False:""")],
    ),
    (
        # Punctuation tolerance sounds like kindness and is not: it decides on
        # the case author's behalf that `tortoise shell` and `tortoise-shell`
        # are the same claim about a source's wording.
        # First attempt deleted punctuation outright, turning `tortoise-shell`
        # into `tortoiseshell`, which still fails to match `tortoise shell` —
        # the mutation did not mutate. Replacing punctuation with a space is the
        # tolerance a well-meaning author would actually add.
        "matching becomes punctuation-insensitive",
        # ANCHORED on `def contains` below it. The bare line is not unique:
        # eval/goldset.py's question_key() has a byte-identical body, goldset
        # comes first in SOURCES, and on 2026-08-24 this mutation silently
        # moved there and left its guard unwatched. See the ambiguity check in
        # main().
        [("""    return re.sub(r"\\s+", " ", text).strip().casefold()


def contains(haystack: str, needle: str) -> bool:""",
          """    return re.sub(r"\\s+", " ", re.sub(r"[^\\w\\s]", " ", text)).strip().casefold()


def contains(haystack: str, needle: str) -> bool:""")],
    ),
    (
        "the refusal sentence is no longer recognised",
        [("""    return REFUSAL_SENTENCE.rstrip(".").casefold() in answer_text.casefold()""",
          """    return False""")],
    ),
    (
        "the alternatives assertion is never scored",
        # ANCHORED. The bare line appears again in the --list CLI branch.
        [("""    for group in case.expect_answer_contains_any:
        hit = next((item for item in group if contains(answer_text, item)), None)""",
          """    for group in []:
        hit = next((item for item in group if contains(answer_text, item)), None)""")],
    ),
    (
        # The hole a dry run of the sweep found: expect_cited_docs says the model
        # named a document, not that it used one. Three of the six passages in
        # the Aksum evidence set carry gold terms.
        "the quoted-document assertion is never scored",
        [("""    for doc_id in case.expect_quoted_docs:""", """    for doc_id in []:""")],
    ),
    (
        # The 30-chat-call bug: the scorer assumed a key only the archives carry.
        "the cited fallback for live payloads is removed",
        [("""    markers = set((payload.get("grounding") or {}).get("cited_markers") or [])
    return [p for p in passages if p.get("marker") in markers]""",
          """    return []""")],
    ),
    (
        "the quotation floor is never scored",
        # ANCHORED. The bare line appears again in the --list CLI branch.
        [("""    if case.expect_min_resolved_quotes:
        add(Assertion(""",
          """    if False:
        add(Assertion(""")],
    ),

    # ----------------------------------------------------------------------
    # D2: the expected_behaviour schema. Every clause the loader gained has a
    # mutation here, and each is pinned by the guard for THAT clause.
    # ----------------------------------------------------------------------
    (
        # TASK 2's whole rule, and the only way it can be lost quietly: not by
        # deleting the field but by giving it a fallback. Two patches, because
        # dropping it from _ANSWER_REQUIRED alone raises KeyError, and a
        # mutation that crashes the suite pins nothing.
        "a missing expected_behaviour falls back to a default",
        [("""_ANSWER_REQUIRED = {"id", "question", "why", "expected_behaviour"}""",
          """_ANSWER_REQUIRED = {"id", "question", "why"}"""),
         ("""        behaviour = str(raw["expected_behaviour"]).strip()""",
          """        behaviour = str(raw.get("expected_behaviour", "answerable")).strip()""")],
    ),
    (
        "an unrecognised behaviour label is carried through",
        [("""        if behaviour not in ANSWER_BEHAVIOURS:""", """        if False:""")],
    ),
    (
        # Clause one of two. Only the assertion is scored, so when the label and
        # the assertion disagree it is the label that is wrong -- and the label
        # is what a reader uses to decide what a red line means.
        "a refusable label need not assert a refusal",
        [("""        if behaviour == BEHAVIOUR_REFUSABLE and not refusal:""",
          """        if False:""")],
    ),
    (
        "a refusal may be filed under any label at all",
        [("""        if refusal and behaviour != BEHAVIOUR_REFUSABLE:""",
          """        if False:""")],
    ),
    (
        # A refusal contains none of the strings a case excludes, so a case
        # built from exclusions alone is passed by silence.
        "a speaking case may be built from exclusions alone",
        [("""        if speaks and not positive:""", """        if False:""")],
    ),
    (
        "a gloss case need not quote the source it glosses",
        [("""            if not raw.get("expect_quoted_docs"):
                raise GoldSetError(""",
          """            if False:
                raise GoldSetError(""")],
    ),
    (
        # The hedge is the entire assertion on this arm. Without it a confident
        # English rendering of a partly undeciphered text passes, and it arrives
        # attached to a citation.
        "the hedge requirement is dropped from the gloss arm",
        [("""            if not hedge:""", """            if False:""")],
    ),
    (
        "a hedge may be declared on a case that is not a gloss case",
        [("""        elif hedge:""", """        elif False:""")],
    ),
    (
        "a case may pair with itself",
        [("""        if partner_id == case_id:""", """        if False:""")],
    ),
    (
        # `continue` rather than `if False:`, because falling through to
        # partner.get() on None crashes the suite instead of failing the guard.
        "a pairing may name a case that is not in the file",
        [("""        if partner is None:
            raise GoldSetError(""",
          """        if partner is None:
            continue
        if False:
            raise GoldSetError(""")],
    ),
    (
        "a pairing need not be symmetric",
        [("""        if back != case_id:""", """        if False:""")],
    ),
    (
        # The one the handoff singles out: once the two assertion blocks drift,
        # the pair stops discriminating between two QUESTIONS and starts
        # discriminating between two TESTS, while still reading like the first.
        "two halves of a discriminator may assert different things",
        [("""        if mine != theirs:""", """        if False:""")],
    ),

    # ----------------------------------------------------------------------
    # D3: the region field, so G4's stratification is a number and not a claim.
    # ----------------------------------------------------------------------
    (
        "an unrecognised region is carried through",
        [("""        if region and region not in ANSWER_REGIONS:""",
          """        if False:""")],
    ),
    (
        # Eight of the thirty-two cases name no document. Without this clause
        # they count toward the total and vanish from the per-region count,
        # which is a gate passed on arithmetic nobody redid.
        "a case naming no document need not declare a region",
        [("""        if not region and not (raw.get("expect_cited_docs")""",
          """        if False and not (raw.get("expect_cited_docs")""")],
    ),
    (
        # FINDING 13. Without this the source-text assertion is never scored and
        # a case demanding the Chinese passes on the English -- which is the
        # exact hole the key was added to close.
        "the source-text assertion is never scored",
        [("""    for doc_id in case.expect_quoted_from_original:""",
          """    for doc_id in []:""")],
    ),
    (
        # The field is what distinguishes the two chunks. Ignoring it makes the
        # new key a synonym for expect_quoted_docs.
        "the source-text assertion accepts a quotation from any field",
        [("""        and span.get("source_field") == "original_text_excerpt"
    }""",
          """        and span.get("source_field") is not None
    }""")],
    ),

    # ----------------------------------------------------------------------
    # D4: a duplicate question cannot shadow a case. Four clauses, and the
    # last two are about the loader and the matcher being ONE rule rather than
    # two that currently agree.
    # ----------------------------------------------------------------------
    (
        "two cases may ask the same question",
        [("""        key = question_key(raw["question"])
        if key in asked:""",
          """        key = question_key(raw["question"])
        if False:""")],
    ),
    (
        # Refusing only byte-identical questions is a guard that looks
        # complete. The matcher folds case and collapses whitespace, so two
        # questions differing by a double space shadow each other exactly as a
        # byte-identical pair does.
        "the same question is only the same when it is byte-identical",
        [("""    return re.sub(r"\\s+", " ", text).strip().casefold()


def _has_content_assertion(raw: dict) -> bool:""",
          """    return text


def _has_content_assertion(raw: dict) -> bool:""")],
    ),
    (
        # The original defect, restored exactly: return the first match.
        "match_case picks the first of two cases instead of refusing",
        [("""    if len(hits) > 1:""", """    if False:""")],
    ),
    (
        # The two functions agree today. A matcher with its OWN copy of the
        # rule can stop agreeing, and the case the loader refused to admit is
        # then findable again with nothing saying so.
        "the matcher keeps its own copy of what the same question means",
        [("""    question = question_key(payload.get("question") or "")
    hits = [case for case in cases if question_key(case.question) == question]""",
          """    question = normalise(payload.get("question") or "")
    hits = [case for case in cases if normalise(case.question) == question]""")],
    ),

    # ----------------------------------------------------------------------
    # D4: session identity, the two stability numbers, and the calibration
    # refusal. TASK 3 items 1-3.
    # ----------------------------------------------------------------------
    (
        # Two sweeps an hour apart on one afternoon are TWO sessions and one
        # date. An id that could not tell them apart is the blindness that
        # invalidated the floor, reintroduced.
        "every invocation reports the same session id",
        [("""        "id": uuid.uuid4().hex,""", """        "id": "one-session",""")],
    ),
    (
        "a session that ran past midnight UTC does not say so",
        [("""        "crossed_midnight_utc": now.strftime("%Y-%m-%d") != session["date"],""",
          """        "crossed_midnight_utc": False,""")],
    ),
    (
        # A session that changed its own date halfway through would be
        # uncountable, and a two-day sweep whose day 2 ran late could present
        # itself as three dates.
        "a session that crossed midnight adopts the new date",
        [("""    return {
        **session,
        "finished_at": now.isoformat(timespec="seconds"),""",
          """    return {
        **session,
        "date": now.strftime("%Y-%m-%d"),
        "finished_at": now.isoformat(timespec="seconds"),""")],
    ),
    (
        # `split` is the condition floor.json refuses outright under
        # max_unstable_content_cells: the floor stops being MEASURABLE before
        # it stops being met. Folding it into `fail` hides exactly that.
        "a cell that splits across its repetitions is called a failure",
        [("""    if passed == 0:
        return "fail"
    return "split\"""",
          """    return "fail\"""")],
    ),
    (
        # A cell of one repetition is unanimous with itself. Counting it
        # raises the figure with observations that cannot disagree.
        "an unrepeated cell counts toward per-case stability",
        [("""    repeated = {k: v for k, v in by_cell.items() if len(v) > 1}""",
          """    repeated = by_cell""")],
    ),
    (
        # The whole of item 3. With this, the 2026-08-10 observation reports
        # 100% per case and 100% per session, and the finding disappears.
        "per-session stability stops comparing the sessions",
        [("""    agreeing = sum(1 for verdicts in across.values()
                   if len(set(verdicts.values())) == 1)""",
          """    agreeing = len(across)""")],
    ),
    (
        # Folding pre-D4 rows into one anonymous session returns a
        # per-session number computed over a session that never existed.
        "rows with no session are folded into one anonymous session",
        [("""        session_id = row.get("session_id")
        if not session_id:
            without += 1
            continue""",
          """        session_id = row.get("session_id") or "unknown"
        if False:
            without += 1
            continue""")],
    ),
    (
        "the distinct-date threshold is not applied",
        [("""    if len(dates) < minimum:""", """    if False:""")],
    ),
    (
        # Counting sessions where the floor says dates lets one afternoon of
        # three sweeps calibrate — which is the 2026-08-10 shape exactly.
        "distinct dates are counted from session ids",
        # Re-pointed 2026-08-26: `dated` became `eligible` when the
        # calibration scope landed. The guard is unchanged and so is the
        # mutation's meaning — counting sessions where the floor says dates.
        [("""    dates = sorted({(s.get("session") or {})["date"] for s in eligible})""",
          """    dates = sorted({(s.get("session") or {})["id"] for s in eligible})""")],
    ),
    (
        # A date assigned to a pre-D4 archive after the fact is the
        # calibration floor.json already records as invalid.
        "a sweep with no session identity stops blocking calibration",
        # Re-pointed 2026-08-26. The refusal is now raised on undated
        # sweeps that are NOT named in calibration_scope.excluded_by_rule;
        # an undated sweep still contributes no date either way.
        [("""    if unnamed_undated:
        refusals.append(""",
          """    if False:
        refusals.append(""")],
    ),
    (
        "three dates of single shots may calibrate",
        # Re-pointed 2026-08-26: `dated` became `eligible`.
        [("""    thin = [s for s in eligible if int(s.get("repeat", 0)) < reps_needed]""",
          """    thin = []""")],
    ),
    (
        # The threshold lives in the floor FILE so that loosening it is a
        # diff. There is still a value below which the term means nothing.
        "the floor may permit calibration from a single day",
        [("""    if int(data["min_distinct_dates"]) < 2:""", """    if False:""")],
    ),
    # ----------------------------------------------------------------------
    # FINDING 14 — did the corpus move underneath the sweep?
    # ----------------------------------------------------------------------
    (
        "a corpus that moved under the sweep is not detected",
        [("""    if before.get("seed_corpus_digest") == after.get("seed_corpus_digest"):
        return None""",
          """    if True:
        return None""")],
    ),
    (
        # On 2026-08-22 the digest moved three times in one day. "the digest
        # changed" is a fact; "eastasia-01-weilue changed" is something a
        # person can act on.
        "the records that changed are counted rather than named",
        [("""    changed = sorted(d for d in set(was) & set(now) if was[d] != now[d])""",
          """    changed = []""")],
    ),
    (
        "a record that appeared mid-sweep is not reported",
        [("""    appeared = sorted(set(now) - set(was))""", """    appeared = []""")],
    ),
    (
        "a record that vanished mid-sweep is not reported",
        [("""    vanished = sorted(set(was) - set(now))""", """    vanished = []""")],
    ),
    (
        # The digest covers sorted (doc_id, hash) pairs and cannot move while
        # every pair is identical. Reporting that as an empty list of changes
        # would hide a finding about corpus_digest itself.
        "a digest that moves while no record differs is reported as nothing",
        [("""    if not (changed or vanished or appeared):""", """    if False:""")],
    ),
    # ----------------------------------------------------------------------
    # Block E — the variance decomposition. G4's deliverable, and the first
    # instrument in this project that was mutation-verified BEFORE the runs it
    # was built to measure rather than after.
    (
        # Part 8's archived grid is two prompt versions and it is on disk.
        "two prompt versions are pooled into one decomposition",
        [("""    if len(versions) > 1:""", """    if False:""")],
    ),
    (
        # The balanced estimators are only these expressions on a balanced
        # grid. A day that lost one case to a rate limit is unbalanced, and
        # the imbalance is then charged to whichever term absorbs it.
        "an unbalanced grid is decomposed anyway",
        [("""        elif len(sizes) > 1:""", """        elif False:""")],
    ),
    (
        "a grid with a missing cell is decomposed anyway",
        [("""        if missing:""", """        if False:""")],
    ),
    (
        # Every run agreeing is the commonest outcome here. Four terms reading
        # 0% are four numbers that add to nothing.
        "zero total variance is reported as four zero shares rather than NOT "
        "MEASURED",
        [("""                   if total > _TINY else None),""",
          """                   if total > _TINY else {k: 0.0 for k in DECOMPOSITION_TERMS}),""")],
    ),
    (
        # A negative estimate is the estimator saying the term is not
        # distinguishable from zero. Clamping it is right for a share and
        # wrong for a finding, so both are reported.
        "a negative component estimate is clamped in silence",
        [("""    negative = sorted(k for k, v in raw.items() if v < -_TINY)""",
          """    negative = []""")],
    ),
    (
        # The textbook slip, and the one a careless implementation makes:
        # var(session) = (MS_B - MS_AB) / na, NOT (MS_B - MS_E) / na. Against
        # the residual, a crossover design returns exactly 0 for the session
        # term and the negative estimate that says the term is not there
        # vanishes without a trace.
        "the session term is estimated against the residual instead of the "
        "interaction",
        [("""        "session": (ms_b - ms_ab) / (n * a),""",
          """        "session": (ms_b - ms_e) / (n * a),""")],
    ),
    (
        # The same refusal `stability` already makes: sixty pre-D4 rows folded
        # into one anonymous session would decompose over a session that never
        # existed.
        "rows with no session identity are folded into an anonymous session",
        [("""    dated = [r for r in rows if r.get("session_id")]""",
          """    dated = [dict(r, session_id=r.get("session_id") or "anonymous")
             for r in rows]""")],
    ),
    (
        # If the cross-session loop also pairs a session with itself, the
        # boundary this whole block exists to measure stops existing.
        "same-session pairs are counted as crossing the session boundary",
        [("""            for y in range(x + 1, len(ids)):""",
          """            for y in range(x, len(ids)):""")],
    ),
    # ----------------------------------------------------------------------
    # Block E — decisions 1 and 4. The scope that decides which archived
    # sweeps may calibrate, and what a demotion costs to write down.
    (
        # Without the case-set half of the rule, a six-case pilot calibrates a
        # thirty-case floor and the denominator changes between dates.
        "the scope minimum is ignored and any sweep calibrates",
        [("""        if min_cases and len(cases) < min_cases:""",
          """        if False:""")],
    ),
    (
        # The anti-loophole. Without it, excluded_by_rule is a place to put a
        # sweep whose numbers nobody liked — which is the move calibrate_floor
        # exists to make impossible.
        "a sweep that satisfies the rule can be excluded by naming it",
        [("""            if name is not None and name in named:""",
          """            if False:""")],
    ),
    (
        # required_cases_note says removing a case because the model had a bad
        # session is how a floor is quietly lowered. These three fields are
        # what separate a demotion from that, and nothing else is.
        "a demotion need not say what would put the case back",
        [("""        thin = [key for key in ("evidence", "diagnosis", "reinstated_when")
                if not str(record.get(key, "")).strip()]""",
          """        thin = []""")],
    ),
    (
        "a demoted case need not stay reported as an open defect",
        [("""        if case_id not in (data.get("known_failing_cases") or {}):""",
          """        if False:""")],
    ),
    (
        # A day that lost four of its ninety-nine calls carries the full case
        # set and a hole in its grid. The sweep refuses it a floor verdict;
        # this is the other end.
        "a sweep archived incomplete calibrates the floor anyway",
        [("""        if sweep.get("incomplete"):""", """        if False:""")],
    ),
]

EXPECTED = [
    "GUARD a case asserting only groundedness is refused",
    "GUARD a case asserting only groundedness is refused",
    "GUARD an empty alternatives group is refused",
    "GUARD expect_refusal with no justification is refused",
    "GUARD a case cannot demand both a refusal and content",
    "GUARD matching is NOT punctuation-insensitive — a case must say which "
    "spelling it accepts rather than let the matcher decide",
    "a correct refusal passes",
    # NOT the Aksum ok/not-ok guard: that case fails on five assertions, so
    # removing one leaves it failing. Defence in depth is good and it means the
    # verdict cannot pin any single assertion. The guard that does pin this one
    # is the check on what the failure NAMES.
    "the failure names the content the corpus contains and the answer omits",
    "GUARD content drawn from the wrong document fails the case",
    "GUARD a good answer in the LIVE payload shape passes — this is the case "
    "that failed 0/3 across two prompt versions",
    # Over-determined for the same reason as the Aksum case: expect_quoted_docs
    # ALSO fails when nothing is quoted, so deleting the floor leaves the verdict
    # unchanged. The guard that pins the floor is what the failure NAMES. This is
    # the second time a mutation has shown a verdict cannot pin a single
    # assertion, and both times the naming check was the one doing the work.
    "the failure names the missing quotation, not the content",

    # D2, in the order above.
    "GUARD a case with no expected_behaviour is refused",
    "GUARD an unrecognised expected_behaviour is refused",
    "GUARD a refusable label with no expect_refusal is refused",
    "GUARD an expect_refusal filed under another label is refused",
    "GUARD a speaking case built only from exclusions is refused",
    "GUARD a gloss case with no quoted document is refused",
    "GUARD a gloss case with no declared hedge is refused",
    "GUARD a hedge on a non-gloss case is refused",
    "GUARD a paired case naming itself is refused",
    "GUARD a paired case whose partner is absent is refused",
    "GUARD an asymmetric pairing is refused",
    "GUARD paired cases whose assertions differ are refused",

    # D3, in the order above.
    "GUARD an unrecognised region is refused",
    "GUARD a case naming no document must declare a region",

    # FINDING 13.
    "GUARD quoting only the translation FAILS a source-text case",
    "GUARD quoting only the translation FAILS a source-text case",

    # D4, in the order above.
    "GUARD two cases asking the same question are refused",
    "GUARD two questions differing only in spacing and case are refused",
    "GUARD match_case refuses to choose between two cases",
    "GUARD match_case matches on the loader's key, not a copy of it",

    # D4 items 1-3, in the order above.
    "GUARD two invocations are two sessions, not one",
    "GUARD a session that ran past midnight UTC records that it did",
    "GUARD a session that crossed midnight keeps the date it began on",
    "GUARD a cell splitting across its own repetitions is unstable per case",
    "GUARD an unrepeated cell is NOT MEASURED, never 100%",
    "GUARD and 0% stable PER SESSION — which is the finding, and what one "
    "number would have shown as a flaky 50%",
    "GUARD rows with no session are counted in NEITHER number",
    "GUARD two distinct dates cannot calibrate",
    "GUARD three sessions on one day are still one date and cannot calibrate",
    "GUARD a sweep with no session identity blocks calibration rather than "
    "being counted as a date",
    "GUARD three dates of single shots cannot calibrate either",
    "GUARD a floor permitting calibration from a single day is refused",

    # FINDING 14, in the order above.
    "GUARD a corpus that moved under the sweep is detected",
    "the record that changed is NAMED, not counted",
    "a record that appeared mid-sweep is named as having appeared",
    "a record that vanished mid-sweep is named as having vanished",
    "GUARD a digest that moves while no record differs says so",

    # Block E — the variance decomposition, in the order above.
    "GUARD a decomposition refuses to pool two prompt versions",
    "GUARD an unbalanced grid is refused rather than decomposed",
    "GUARD an incomplete grid is refused rather than decomposed",
    "GUARD zero total variance is NOT MEASURED, never 0%",
    "GUARD a negative component estimate is named, not clamped in silence",
    "GUARD the session term is estimated against the interaction mean square, "
    "not the residual",
    "GUARD a row with no session identity is excluded from the decomposition "
    "and counted",
    "GUARD text agreement separates within-session from across-session",

    # Block E — the calibration scope and the demotion, in the order above.
    "GUARD a sweep below the scope minimum blocks calibration when it is not "
    "named",
    "GUARD a sweep that SATISFIES the rule cannot be excluded by name",
    "GUARD a demotion with no written condition for return is refused",
    "GUARD a demoted case that is not tracked as a known failure is refused",
    "GUARD a sweep archived INCOMPLETE cannot calibrate, even with the full "
    "case set",
]


def failures_from(output: str) -> set[str]:
    return {
        line.split("FAIL", 1)[1].strip()
        for line in output.splitlines()
        if line.strip().startswith("FAIL")
    }


def _newline_of(raw: bytes) -> str:
    """The file's own line ending, so a mutation run does not change it.

    SOURCES do not agree: eval/goldset.py is CRLF and eval/answer_eval.py is LF.
    Writing both with the platform's ending converts one of them on every run,
    in whichever direction the machine prefers.
    """
    crlf = raw.count(b"\r\n")
    if crlf and raw.count(b"\n") - crlf:
        raise SystemExit(
            "a mutation source has MIXED line endings. Resolve that by hand "
            "before running this harness, which would otherwise pick one."
        )
    return "\r\n" if crlf else "\n"


def _write(path: pathlib.Path, text: str, newline: str) -> None:
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def main() -> int:
    # Bytes are what gets restored; the normalised text is only for matching
    # the mutation targets, which are written with \n whatever the file uses.
    original_bytes = {f: f.read_bytes() for f in SOURCES}
    newlines = {f: _newline_of(original_bytes[f]) for f in SOURCES}
    originals = {
        f: original_bytes[f].decode("utf-8").replace("\r\n", "\n")
        for f in SOURCES
    }
    problems: list[str] = []
    try:
        for (label, patches), guard in zip(MUTATIONS, EXPECTED):
            edited = {f: originals[f] for f in SOURCES}
            missing = [
                old for old, _ in patches
                if not any(old in originals[f] for f in SOURCES)
            ]
            if missing:
                problems.append(f"{label}: mutation target not found")
                print(f"  MISS {label} (target not found)")
                continue

            # D4, 2026-08-24. A target that occurs in more than one place is
            # resolved twice over in silence: `next(f for f in SOURCES if old
            # in edited[f])` takes the FIRST source, and `.replace(old, new,
            # 1)` takes the FIRST occurrence within it. Neither says so.
            #
            # It bit on the day it was written. `eval/goldset.py`'s
            # `question_key` was given a body byte-identical to
            # `answer_eval.normalise`; goldset comes first in SOURCES; the
            # punctuation mutation silently moved onto the new function, and
            # `GUARD matching is NOT punctuation-insensitive` was left
            # unwatched while this harness reported only that its guard had
            # not failed. The report was true and the diagnosis it invited —
            # "the guard is broken, or the lists have drifted" — was wrong,
            # and BLOCK_D_START already warns about exactly that misreading.
            #
            # So: pick-the-first-and-say-nothing, inside the instrument this
            # project built to catch pick-the-first-and-say-nothing. Anchor
            # the target with surrounding lines until it is unique.
            ambiguous = [
                (old, sum(originals[f].count(old) for f in SOURCES))
                for old, _ in patches
            ]
            ambiguous = [(old, n) for old, n in ambiguous if n > 1]
            if ambiguous:
                problems.append(
                    f"{label}: mutation target is AMBIGUOUS — "
                    + "; ".join(
                        f"{n} occurrences of "
                        f"{old.splitlines()[0].strip()[:60]!r}"
                        for old, n in ambiguous
                    )
                    + ". The first is chosen silently, so this mutation may be "
                      "pointing at code it was not written for. Anchor it with "
                      "surrounding lines until it is unique."
                )
                print(f"  MISS {label} (ambiguous target)")
                continue
            for old, new in patches:
                target = next(f for f in SOURCES if old in edited[f])
                edited[target] = edited[target].replace(old, new, 1)
            for f in SOURCES:
                _write(f, edited[f], newlines[f])

            _purge_bytecode()
            result = subprocess.run(
                [sys.executable, "-B", "-m", "eval.test_answer_eval"],
                cwd=ROOT, capture_output=True, text=True,
                encoding="utf-8", errors="replace", env=CHILD_ENV,
            )
            failed = failures_from(result.stdout)
            if guard in failed:
                print(f"  ok   {label}")
                print(f"       -> {guard}")
            elif result.returncode != 0 and not failed:
                problems.append(
                    f"{label}: the suite crashed rather than failing the guard"
                )
                print(f"  MISS {label} (crash, not a guard failure)")
            else:
                problems.append(
                    f"{label}: expected {guard!r} to fail, got "
                    f"{sorted(failed) or 'no failures'}"
                )
                print(f"  MISS {label}")
    finally:
        for f in SOURCES:
            f.write_bytes(original_bytes[f])

    # Two different failures, kept apart. Collapsing them is how a real finding
    # spent an afternoon looking like a corrupted working tree: on 2026-08-12
    # this line reported "sources were not restored cleanly" while the restore
    # was perfect and the suite was failing on its own account — an archived
    # answer run with no gold case. Same defect family as Part 4's Voyage rate
    # limit reported as a dead gateway: the check matched too broadly and the
    # message named the wrong cause.
    # BYTES, not text. The previous version compared read_text() to
    # read_text(), so a line-ending rewrite passed it as "sources restored" --
    # which is what this harness was doing to eval/goldset.py on every run, and
    # what a green mutation run therefore could not be read as ruling out.
    unrestored = [
        f.name for f in SOURCES
        if f.read_bytes() != original_bytes[f]
    ]
    if unrestored:
        problems.append(
            "sources were NOT restored cleanly: " + ", ".join(unrestored)
            + " — restore from version control before running anything else"
        )

    _purge_bytecode()
    check = subprocess.run(
        [sys.executable, "-B", "-m", "eval.test_answer_eval"],
        cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=CHILD_ENV,
    )
    if check.returncode != 0:
        problems.append(
            "sources restored, but `eval.test_answer_eval` fails on its own "
            "account — a finding about the suite, not about this harness"
        )
        print("\n--- eval.test_answer_eval output, so it is not lost ---")
        print((check.stdout or "") + (check.stderr or ""), end="")
        print("--- end ---")

    print()
    if problems:
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"all {len(MUTATIONS)} mutations verified; "
          f"sources restored byte for byte")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
