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

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
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
]


def failures_from(output: str) -> set[str]:
    return {
        line.split("FAIL", 1)[1].strip()
        for line in output.splitlines()
        if line.strip().startswith("FAIL")
    }


def main() -> int:
    originals = {f: f.read_text(encoding="utf-8") for f in SOURCES}
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
                f.write_text(edited[f], encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "eval.test_answer_eval"],
                cwd=ROOT, capture_output=True, text=True,
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
            f.write_text(originals[f], encoding="utf-8")

    # Two different failures, kept apart. Collapsing them is how a real finding
    # spent an afternoon looking like a corrupted working tree: on 2026-08-12
    # this line reported "sources were not restored cleanly" while the restore
    # was perfect and the suite was failing on its own account — an archived
    # answer run with no gold case. Same defect family as Part 4's Voyage rate
    # limit reported as a dead gateway: the check matched too broadly and the
    # message named the wrong cause.
    unrestored = [
        f.name for f in SOURCES
        if f.read_text(encoding="utf-8") != originals[f]
    ]
    if unrestored:
        problems.append(
            "sources were NOT restored cleanly: " + ", ".join(unrestored)
            + " — restore from version control before running anything else"
        )

    check = subprocess.run(
        [sys.executable, "-m", "eval.test_answer_eval"],
        cwd=ROOT, capture_output=True, text=True,
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
    print(f"all {len(MUTATIONS)} mutations verified; sources restored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
