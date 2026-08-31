"""Mutation-verify the F1 record-tier guards.

Same standard as `mutate_part8.py`, `mutate_part7b.py`, `mutate_places.py` and
`mutate_recover.py`: each mutation breaks exactly one rule and asserts that the
guard protecting THAT rule reports FAIL -- not merely that something failed. A
guard that has never been seen to fail is not known to work, and F1 declares a
tiering policy that 36 records will be curated against before a single one of
them exists.

Built on 2026-08-29 WITH the BASELINE check that `mutate_part8.py` gained on
2026-08-28, rather than without it. F1_HANDOFF item 4 of what is owed records
that the baseline check "is still not in the other five harnesses"; a seventh
harness shipped without it would have made that six.

Run: python scripts/mutate_fidelity.py
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys

# FINDING 10: this process's own stdout. Through a pipe or a redirect on
# Windows it falls back to the locale codec, which cannot encode Greek, Tamil,
# Chinese, Ge'ez or runic, and it raises mid-output with the file half written
# and every number in it correct. errors="replace" is deliberate: a mangled
# character is cosmetic, a lost run is not.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
# FINDING 16, and FINDING 10's other two boundaries: the CHILD's stdout encoding,
# and no bytecode cache for the child to read a stale mutation out of.
CHILD_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8",
             "PYTHONDONTWRITEBYTECODE": "1"}
FIDELITY = ROOT / "ingest" / "fidelity.py"
SOURCES = (FIDELITY,)
SUITE = ["-B", "-m", "ingest.test_fidelity"]


def _purge_bytecode() -> None:
    """FINDING 16. `-B` stops the child WRITING a cache; it does not stop it
    reading one an ordinary run left behind. Both, always."""
    for source in SOURCES:
        shutil.rmtree(source.parent / "__pycache__", ignore_errors=True)


ELIGIBLE_SET = (
    'ELIGIBLE_ORIGINAL_FIDELITIES = frozenset(\n'
    '    {"verbatim_original", "partial_verbatim", "transliteration"}\n'
    ')'
)

GLOSS_SET = (
    'GLOSS_CAPABLE_TIERS = frozenset(\n'
    '    {"verbatim_with_provenance", "published_translation_only", "catalogue_record"}\n'
    ')'
)

# Ruling 51's ordering rule, which is two lines and therefore cannot be
# mutated by a one-line anchor. Written out here for the same reason
# ELIGIBLE_SET and GLOSS_SET are.
ORDER_RULE = (
    "    if (first_catalogue is not None and last_source_language is not None\n"
    "            and first_catalogue < last_source_language):"
)

MUTATIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "a find record is no longer decided by source_type",
        [('    if source_type in FIND_TYPES:\n        return "catalogue_record", (',
          '    if False:\n        return "catalogue_record", (')],
    ),
    (
        "nothing retrieval-eligible no longer means pointer_only",
        [('    if not eligible:\n        return "pointer_only", (',
          '    if False:\n        return "pointer_only", (')],
    ),
    (
        "a record with no published translation is read as verbatim_with_provenance anyway",
        [('        if not published:\n            return "verbatim_machine_english", (',
          '        if False:\n            return "verbatim_machine_english", (')],
    ),
    (
        "the published-translation test no longer reads the ROLE",
        [('    published = [r for r in eligible if r[0] == "translation" and r[1] == "translation"]',
          '    published = [r for r in eligible if r[0] == "original" and r[1] == "translation"]')],
    ),
    (
        "partial_verbatim no longer counts as source-language text",
        [(ELIGIBLE_SET,
          'ELIGIBLE_ORIGINAL_FIDELITIES = frozenset(\n'
          '    {"verbatim_original", "transliteration"}\n'
          ')')],
    ),
    (
        "a transliteration no longer counts as source-language text",
        [(ELIGIBLE_SET,
          'ELIGIBLE_ORIGINAL_FIDELITIES = frozenset(\n'
          '    {"verbatim_original", "partial_verbatim"}\n'
          ')')],
    ),
    (
        "'both cited' stops being a clause: an unattributed translation passes",
        [('        if not (translation_source or "").strip():',
          '        if False:')],
    ),
    (
        "an English original on a non-find record falls through instead of blocking",
        [('    if english_original:\n        return UNCLASSIFIABLE, (',
          '    if False:\n        return UNCLASSIFIABLE, (')],
    ),
    (
        "English stops being excluded from source-language text",
        [('        and r[2] != "en"',
          '        and True')],
    ),
    (
        "a record no tier holds is given a default instead of blocking",
        [('    return UNCLASSIFIABLE, (\n'
          '        "a retrieval-eligible chunk exists but it is neither source-language "',
          '    return "catalogue_record", (\n'
          '        "a retrieval-eligible chunk exists but it is neither source-language "')],
    ),
    (
        "pointer_only is derived as catalogue_record, against the declaration on disk",
        [('        return "pointer_only", (\n'
          '            "no chunk in either role is retrieval-eligible',
          '        return "catalogue_record", (\n'
          '            "no chunk in either role is retrieval-eligible')],
    ),
    (
        "a record with no declared tier stops being reported",
        [('    for doc_id in sorted(set(derived) - set(declared)):',
          '    for doc_id in sorted([]):')],
    ),
    (
        "a declaration naming a record that is not in the corpus stops being reported",
        [('    for doc_id in sorted(set(declared) - set(derived)):',
          '    for doc_id in sorted([]):')],
    ),
    (
        "declared and derived no longer have to agree",
        [('        if want != got:', '        if False:')],
    ),
    (
        "unclassifiable becomes a declarable tier",
        [('        if want == UNCLASSIFIABLE:', '        if False:')],
    ),
    (
        "a declared tier outside the vocabulary stops being named as such",
        [('        if want not in RECORD_TIERS:', '        if False:')],
    ),
    (
        "the target mix no longer has to sum to the tranche",
        [('    if sum(new.values()) != want_new:', '    if False:')],
    ),
    (
        "a new pointer_only record is allowed",
        [('    if new.get("pointer_only", 0) != 0:', '    if False:')],
    ),
    (
        "a per-region minimum the aggregate targets cannot reach is allowed",
        [('    if per_region * REGION_COUNT > source_language_at_60:', '    if False:')],
    ),
    (
        "a gloss case becomes declarable on the tier whose only English is machine",
        [(GLOSS_SET,
          'GLOSS_CAPABLE_TIERS = frozenset(\n'
          '    {"verbatim_with_provenance", "published_translation_only",\n'
          '     "catalogue_record", "verbatim_machine_english"}\n'
          ')')],
    ),
    # Ruling 51, F3. check_allocation, one branch at a time.
    (
        "the allocation no longer has to place every record in the tranche",
        [("    if total != want_new:", "    if False:")],
    ),
    (
        "the allocation's tier totals no longer have to match by_tier_new",
        [("        if per_tier.get(tier, 0) != new.get(tier, 0):",
          "        if False:")],
    ),
    (
        "the allocation's per-region totals no longer have to reach the target at 60",
        [("        if per_region.get(region, 0) != want:", "        if False:")],
    ),
    (
        "a region may be left below the source-language floor",
        [("        if at_60 < per_region_floor:", "        if False:")],
    ),
    (
        "the cheap tier may jump the queue",
        [(ORDER_RULE, "    if False:")],
    ),
    (
        "a gloss-capable record may be dropped from the allocation",
        [('    if gloss != int(mix.get("gloss_capable_records") or 0):',
          "    if False:")],
    ),
    (
        "gloss-capable records may be allocated to a sub-tranche that cannot carry one",
        [('        if int(tranche.get("gloss_capable") or 0) > capacity:',
          "        if False:")],
    ),
    (
        "fewer quoted-from-original cases than the mix requires becomes allowed",
        [("    if quoted < want_quoted:", "    if False:")],
    ),
    (
        "an allocation with no sub-tranches stops being refused",
        # Two functions now open with this line, so the anchor carries the
        # NEXT one. An ambiguous target resolves first-occurrence-wins in
        # silence, which is the defect this harness refuses to have.
        [("    if not tranches:\n        return [\"target_mix.allocation",
          "    if False:\n        return [\"target_mix.allocation")],
    ),
    (
        "two sub-tranches may share a name",
        [("    if not all(names) or len(set(names)) != len(names):",
          "    if False:")],
    ),
    (
        "a slot may name a region that has no target at 60",
        [("            if region not in by_region_at_60:", "            if False:")],
    ),
    # F3, check_delivery. The plan was guarded eleven ways and delivery not at
    # all, which is how two records missed the gloss quota in silence.
    (
        "a record curated outside the plan stops being reported",
        [("        if key not in planned:", "        if False:")],
    ),
    (
        "a cell may be curated past its planned count",
        [("        if count > planned.get(key, 0):", "        if False:")],
    ),
    (
        "a gloss declaration may name a record the tranche never curated",
        [("        if record_id not in delivered:", "        if False:")],
    ),
    (
        "a gloss case becomes declarable on a tier that cannot carry one",
        [("        elif tier_of not in GLOSS_CAPABLE_TIERS:", "        elif False:")],
    ),
    (
        "the gloss quota stops being a ceiling",
        [("    if len(gloss_declared) > want_gloss:", "    if False:")],
    ),
    (
        "an unreachable gloss quota is reported as a shortfall instead of a failure",
        [("    if len(gloss_declared) + capacity < want_gloss:", "    if False:")],
    ),
    (
        "a manifest flag the code neither honours nor lifts stops being reported",
        [("    if unaccounted:", "    if False:")],
    ),
    (
        "a lift no longer needs a written reason",
        [('        if not (reason or "").strip():', "        if False:")],
    ),
    (
        "a flag may be honoured and lifted at once",
        [("    if both:", "    if False:")],
    ),
    (
        "a lift may name a flag the manifest does not carry",
        [("    if stray:", "    if False:")],
    ),
]

EXPECTED = [
    "GUARD a find record tiers as catalogue_record whatever its text fields contain",
    "GUARD a record with nothing retrieval-eligible in either role tiers as pointer_only",
    "GUARD source-language text with no published translation tiers as verbatim_machine_english",
    "GUARD source-language text with a cited published translation tiers as verbatim_with_provenance",
    "GUARD a partial_verbatim original counts as source-language text",
    "GUARD a transliteration original counts as source-language text",
    "GUARD a translation with an empty translation_source is refused, because both cited is the clause",
    "GUARD a retrieval-eligible English original on a non-find record is refused rather than read as published_translation_only",
    "GUARD a retrieval-eligible English original on a non-find record is refused rather than read as published_translation_only",
    "GUARD a record no tier holds returns unclassifiable rather than a default",
    "GUARD every seed record derives the tier data/corpus_tiers.json declares",
    "GUARD a record with no declared tier is refused",
    "GUARD a declared tier naming a record that is not in the corpus is refused",
    "GUARD a declared tier that disagrees with the derived one is refused",
    "GUARD unclassifiable is refused as a declared tier",
    "GUARD a declared tier outside the vocabulary is refused",
    "GUARD a target mix whose tier targets do not sum to the tranche is refused",
    "GUARD a target mix that allows a new pointer_only record is refused",
    "GUARD a per-region minimum the aggregate targets cannot reach is refused",
    "GUARD a gloss case may not be declared possible on verbatim_machine_english",
    "GUARD an allocation that does not place every record in the tranche is refused",
    "GUARD an allocation whose tier totals differ from by_tier_new is refused",
    "GUARD an allocation whose per-region totals miss the target at 60 is refused",
    "GUARD a region left below the source-language floor is refused",
    "GUARD an allocation that curates a catalogue record before a source-language record is refused",
    "GUARD an allocation that drops a gloss-capable record is refused",
    "GUARD gloss-capable records allocated to a sub-tranche that cannot carry one are refused",
    "GUARD an allocation writing fewer quoted-from-original cases than the mix requires is refused",
    "GUARD an allocation with no sub-tranches is refused",
    "GUARD two sub-tranches with the same name are refused",
    "GUARD a slot naming a region with no target at 60 is refused",
    "GUARD a record curated into a cell the allocation does not place is refused",
    "GUARD a cell curated past its planned count is refused",
    "GUARD a gloss-capable declaration naming a record the tranche did not curate is refused",
    "GUARD a gloss-capable declaration on a tier whose only English is machine is refused",
    "GUARD more gloss-capable records than the mix asks for is refused",
    "GUARD a gloss quota the remaining slots cannot carry is refused, rather than reported as a shortfall nobody acts on",
    "GUARD a manifest flag the code neither honours nor lifts is refused",
    "GUARD a lift with no written reason is refused",
    "GUARD a flag cannot be honoured and lifted at once",
    "GUARD a lift naming a flag the manifest does not carry is refused",
]

# NOT mutation-verified from this source, and said so rather than left to be
# noticed. `GUARD the measured histogram the target mix is arithmetic over
# still holds` cannot be broken by an edit to ingest/fidelity.py without also
# breaking `GUARD every seed record derives the tier ... declares` -- the two
# move together under every source mutation. What it protects against is a DATA
# edit: someone changing `measured_at_24` in data/corpus_tiers.json without
# changing `tiers`, which would leave every target above it denominated in a
# corpus that is not the one on disk. That is FINDING 14's shape, and it has no
# mutation here because this harness mutates code.
UNMUTATED_BY_DESIGN = (
    "GUARD the measured histogram the target mix is arithmetic over still holds",
    "GUARD the declared allocation delivers the declared mix",
    "GUARD a tranche that has curated nothing yet reports no problem",
    "GUARD records curated into cells the allocation places report nothing",
    "GUARD a gloss-capable declaration on a tier that CAN carry one reports nothing",
    "GUARD an empty tranche is not called unreachable — every slot is still there",
    "GUARD a declaration that matches the derivation reports no problem",
    "GUARD every tier the derivation returns is in the declared vocabulary",
    "GUARD the declared target mix is internally coherent",
    "GUARD the gloss-capable tier set excludes the tier whose only English is machine",
    "GUARD every record the manifest flags is either honoured in code or carries a written lift",
)


def failures_from(output: str) -> set[str]:
    return {
        line.split("FAIL", 1)[1].strip()
        for line in output.splitlines()
        if line.strip().startswith("FAIL")
    }


def _newline_of(raw: bytes) -> str:
    """The file's own line ending, so a mutation run does not change it."""
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
    if len(MUTATIONS) != len(EXPECTED):
        print(f"{len(MUTATIONS)} mutations against {len(EXPECTED)} expectations")
        return 1

    # BYTES on the way out, whatever the harness did on the way in. On
    # 2026-08-28 mutate_ui_places converted ui/build_ui_data.py from LF to CRLF
    # on a live run, its text-comparing restore check could not see it, and the
    # conversion reached a commit. 168 archived citation spans point into the
    # corpus by exact offset.
    original_bytes = {f: f.read_bytes() for f in SOURCES}
    newlines = {f: _newline_of(original_bytes[f]) for f in SOURCES}
    originals = {
        f: original_bytes[f].decode("utf-8").replace("\r\n", "\n")
        for f in SOURCES
    }
    problems: list[str] = []
    try:
        # THE BASELINE. A mutation is verified by naming a guard and checking
        # the guard FAILS once the code is broken -- which is only evidence if
        # the guard was PASSING beforehand. A green mutation against a red
        # baseline is a vacuous proof, and on 2026-08-28 one happened inside
        # the instrument built to catch vacuous proofs.
        _purge_bytecode()
        _baseline = subprocess.run(
            [sys.executable, *SUITE], cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=CHILD_ENV,
        )
        already_failing = failures_from(_baseline.stdout)
        if already_failing:
            print(f"  BASELINE: {len(already_failing)} check(s) already fail "
                  f"with NO mutation applied. Any mutation naming one of\n"
                  f"            them cannot be verified by this run.")
            for name in sorted(already_failing):
                print(f"            - {name}")
            print()

        for (label, patches), guard in zip(MUTATIONS, EXPECTED):
            if guard in already_failing:
                problems.append(
                    f"{label}: UNVERIFIED - its guard {guard!r} was already "
                    f"failing before any mutation was applied, so this "
                    f"mutation proves nothing. Fix the suite, then re-run."
                )
                print(f"  UNVERIFIED {label} (its guard was already red at baseline)")
                continue

            edited = {f: originals[f] for f in SOURCES}
            missing = [
                old for old, _ in patches
                if not any(old in originals[f] for f in SOURCES)
            ]
            if missing:
                problems.append(f"{label}: mutation target not found")
                print(f"  MISS {label} (target not found)")
                continue

            # A target occurring more than once resolves first-source-wins and
            # then first-occurrence-wins, both in silence. It bit on the day the
            # check was written, in this repository, and left a guard unwatched
            # while the harness reported only that it had not failed.
            ambiguous = [
                (old, sum(originals[f].count(old) for f in SOURCES))
                for old, _ in patches
            ]
            ambiguous = [(old, n) for old, n in ambiguous if n > 1]
            if ambiguous:
                problems.append(
                    f"{label}: mutation target is AMBIGUOUS - "
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
                [sys.executable, *SUITE], cwd=ROOT, capture_output=True, text=True,
                encoding="utf-8", errors="replace", env=CHILD_ENV,
            )
            failed = failures_from(result.stdout)
            if guard in failed:
                print(f"  ok   {label}")
                print(f"       -> {guard}")
            elif result.returncode != 0 and not failed:
                # A crash is not a guard firing. test_embed.py spent two days
                # crashing where it should have been asserting.
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

    unrestored = [f.name for f in SOURCES if f.read_bytes() != original_bytes[f]]
    if unrestored:
        problems.append(
            "sources were NOT restored cleanly: " + ", ".join(unrestored)
            + " - restore from version control before running anything else"
        )

    _purge_bytecode()
    check = subprocess.run(
        [sys.executable, *SUITE], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=CHILD_ENV,
    )
    if check.returncode != 0:
        problems.append(
            "sources restored, but `ingest.test_fidelity` fails on its own "
            "account - a finding about the suite, not about this harness"
        )
        print("\n--- ingest.test_fidelity output, so it is not lost ---")
        print((check.stdout or "") + (check.stderr or ""), end="")
        print("--- end ---")

    print()
    print(f"  {len(UNMUTATED_BY_DESIGN)} guard(s) are not mutated from this "
          f"source, by design and listed in UNMUTATED_BY_DESIGN.")
    if problems:
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"all {len(MUTATIONS)} mutations verified; sources restored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
