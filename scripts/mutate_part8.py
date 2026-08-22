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
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# The child prints failure detail carrying Greek, Tamil and Chinese. Through a
# pipe on Windows its stdout falls back to cp1252 and `print` raises; the parent
# decodes with the locale codec and raises in the other direction. Both ends are
# named because the ranking harness lost a run to exactly this, and this is the
# harness pair BLOCK_D_START records as never having been checked against it.
CHILD_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
GOLDSET = ROOT / "eval" / "goldset.py"
EVAL = ROOT / "eval" / "answer_eval.py"
SOURCES = (GOLDSET, EVAL)

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
        [("""    return re.sub(r"\\s+", " ", text).strip().casefold()""",
          """    return re.sub(r"\\s+", " ", re.sub(r"[^\\w\\s]", " ", text)).strip().casefold()""")],
    ),
    (
        "the refusal sentence is no longer recognised",
        [("""    return REFUSAL_SENTENCE.rstrip(".").casefold() in answer_text.casefold()""",
          """    return False""")],
    ),
    (
        "the alternatives assertion is never scored",
        [("""    for group in case.expect_answer_contains_any:""",
          """    for group in []:""")],
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
        [("""    if case.expect_min_resolved_quotes:""", """    if False:""")],
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
            for old, new in patches:
                target = next(f for f in SOURCES if old in edited[f])
                edited[target] = edited[target].replace(old, new, 1)
            for f in SOURCES:
                _write(f, edited[f], newlines[f])

            result = subprocess.run(
                [sys.executable, "-m", "eval.test_answer_eval"],
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

    check = subprocess.run(
        [sys.executable, "-m", "eval.test_answer_eval"],
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
