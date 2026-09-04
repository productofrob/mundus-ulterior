"""The mutation harnesses, checked as a DIRECTORY rather than one at a time.

FINDING 61, 2026-09-04, and it is the third instance of one mechanism inside two
days:

    FINDING 37  the `FAIL ` space, found in mutate_places and fixed there
    FINDING 46  its siblings sought, four harnesses named, four fixed -- of eight
    FINDING 58  the other four, one of them LIVE against the ledger suite
    FINDING 52  write BYTES, stated as a rule for the whole repository
    FINDING 61  that remedy present in five harnesses of nine, and absent from
                the only one whose sources do not share a convention

Nobody was careless in any of those. Each commit fixed the file it was working
in and said so accurately. The defect is that **there is no moment in this
project's workflow at which a directory is enumerated**, and every finding of
this family has been closed by a person noticing rather than by a rule.

So this file enumerates it. `scripts/mutate_*.py` is a population with a name,
the same way `data/seed_corpus/` is, and a convention that holds for five of its
members is not a convention.

WHAT THIS ASSERTS IS ONLY WHAT WAS ALREADY WRITTEN DOWN. FINDING 56 is the
warning here: writing the checker for a rule is an invitation to write a
stricter rule by accident, and it cost that session a red run on a case that was
correct. Every assertion below quotes a finding that states it in prose:

    FINDING 37/46/58   the guard matcher takes `FAIL ` WITH THE SPACE
    FINDING 52/61      a mutation is applied by writing BYTES under the file's
                       own newline, never through write_text
    the harnesses' own  MUTATIONS and EXPECTED are zipped POSITIONALLY, so a
    internal contract   length disagreement silently pairs a mutation with
                        another mutation's guard

Anything else a reader might want -- that every harness has a BASELINE block,
that every EXPECTED label is one its suite really prints -- is COUNTED and
printed below, not asserted. A count that surprises somebody is a conversation.
An assertion invented today is a rule nobody agreed to.

Checked by parsing, never by grepping. Five of these files discuss
`startswith("FAIL")` in their own comments, and a grep would read the
explanation of the defect as the defect.
"""

from __future__ import annotations

import ast
import pathlib
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
HARNESSES = sorted(ROOT.joinpath("scripts").glob("mutate_*.py"))

PASSED = 0
FAILED = 0


def expect(condition: bool, label: str) -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ok   {label}")
    else:
        FAILED += 1
        print(f"  FAIL {label}")


def _tree(path: pathlib.Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _fail_calls(tree: ast.Module, attr: str) -> int:
    """Calls to .<attr>("FAIL") — the literal without the trailing space."""
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == attr
        and any(isinstance(a, ast.Constant) and a.value == "FAIL" for a in node.args)
    )


def _write_text_calls(tree: ast.Module) -> int:
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "write_text"
    )


def _defines(tree: ast.Module, name: str) -> bool:
    return any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
        for node in ast.walk(tree)
    )


def _literal(tree: ast.Module, name: str):
    for node in ast.walk(tree):
        target = None
        if isinstance(node, ast.Assign) and node.targets:
            target = getattr(node.targets[0], "id", None)
        elif isinstance(node, ast.AnnAssign):
            target = getattr(node.target, "id", None)
        if target == name:
            try:
                return ast.literal_eval(node.value)
            except (ValueError, TypeError, SyntaxError):
                return None
    return None


def test_the_population_exists() -> None:
    """A glob that stopped matching makes every check below vacuously true."""
    print("\nthe population")
    expect(len(HARNESSES) >= 8,
           f"{len(HARNESSES)} mutation harness(es) found — if this collapsed, "
           f"the glob stopped matching and every check below passes vacuously")
    names = [h.name for h in HARNESSES]
    print(f"       {', '.join(names)}")


def test_the_fail_matcher_takes_the_space() -> None:
    """FINDING 37, 46, 58 — and the assertion is on the FILTER only.

    The first draft of this check also required `split("FAIL ", 1)`, and went
    red on `scripts/mutate_places.py`, which is the file FINDING 37 was found
    in. It was WRONG and the harness was right: the phantom guard comes from
    the predicate that decides which lines are guards, not from the split that
    slices the label off one. Given `startswith("FAIL ")`, the first occurrence
    of `FAIL` is always the prefix, so both spellings yield the same label.

    FINDING 56, exactly, inside the hour: writing the checker for a rule is an
    invitation to write a stricter rule by accident. The stricter idea survives
    below as a COUNTED line, which is the same remedy FINDING 56 chose.
    """
    print("\nthe guard matcher (FINDINGS 37, 46, 58)")
    for h in HARNESSES:
        bare = _fail_calls(_tree(h), "startswith")
        if bare:
            print(f"       {h.name}: {bare} bare startswith(\"FAIL\")")
        expect(bare == 0,
               f"GUARD {h.name} FILTERS on `FAIL ` with the space, so a suite's "
               f"own FAILED summary cannot become a phantom guard")


def test_mutations_are_applied_as_bytes() -> None:
    """FINDING 52, 61. write_text translates a newline to os.linesep."""
    print("\nthe newline convention (FINDINGS 52, 61)")
    for h in HARNESSES:
        tree = _tree(h)
        expect(_defines(tree, "_newline_of") and _defines(tree, "_write"),
               f"GUARD {h.name} carries _newline_of and _write, so a mutation "
               f"is written under the source's OWN newline")
        calls = _write_text_calls(tree)
        if calls:
            print(f"       {h.name}: {calls} write_text call(s)")
        expect(calls == 0,
               f"GUARD {h.name} applies no mutation through write_text — the "
               f"byte-safe restore only runs if the process is allowed to finish")


def test_mutations_and_expected_are_the_same_length() -> None:
    """They are zipped positionally. A mismatch pairs a mutation with another
    mutation's guard, and every line after the gap reads as a passing check of
    something nobody wrote."""
    print("\nMUTATIONS against EXPECTED")
    for h in HARNESSES:
        tree = _tree(h)
        muts = _literal(tree, "MUTATIONS")
        exp = _literal(tree, "EXPECTED")
        if muts is None or exp is None:
            print(f"       {h.name}: not a positional pair "
                  f"(MUTATIONS={'-' if muts is None else len(muts)}, "
                  f"EXPECTED={'-' if exp is None else len(exp)}) — counted, not failed on")
            continue
        expect(len(muts) == len(exp),
               f"GUARD {h.name} zips {len(muts)} mutation(s) against "
               f"{len(exp)} expected guard(s), and the two agree")


def _mutation_targets(tree: ast.Module):
    """Every string literal a MUTATIONS entry names as the text to REPLACE.

    Not `_literal`, deliberately. `_literal` runs ast.literal_eval over the whole
    list and returns None the moment one entry interpolates a module constant --
    which is exactly what `scripts/mutate_fidelity.py` does, and which is why the
    file where the stale target below was FOUND is the file this check would have
    skipped if it reused the existing reader. Entries it cannot evaluate are
    COUNTED and named rather than silently dropped.
    """
    node = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(
                isinstance(x, ast.Name) and x.id == "MUTATIONS" for x in n.targets):
            node = n.value
        elif (isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
              and n.target.id == "MUTATIONS"):
            node = n.value
    if node is None or not isinstance(node, (ast.List, ast.Tuple)):
        return None, 0
    targets, opaque = [], 0
    for entry in node.elts:
        if not isinstance(entry, (ast.Tuple, ast.List)) or len(entry.elts) < 2:
            opaque += 1
            continue
        edits = entry.elts[1]
        if not isinstance(edits, (ast.List, ast.Tuple)):
            opaque += 1
            continue
        for pair in edits.elts:
            if not isinstance(pair, (ast.Tuple, ast.List)) or not pair.elts:
                opaque += 1
                continue
            old = pair.elts[0]
            if isinstance(old, ast.Constant) and isinstance(old.value, str):
                targets.append(old.value)
            else:
                opaque += 1
    return targets, opaque


def _mutable_sources() -> "dict[str, str]":
    """Every Python source a harness could be pointed at, minus the harnesses.

    The harness files are excluded because a mutation's target text is a literal
    INSIDE the harness, so a search that included them would find every target
    exactly where it was written and prove nothing.
    """
    root = ROOT
    out = {}
    for d in ("ingest", "eval", "answer", "retrieve", "scripts", "ui"):
        for f in sorted((root / d).rglob("*.py")):
            if f.parent.name == "__pycache__":
                continue
            if f.parent.name == "scripts" and (
                    f.name.startswith("mutate_") or f.name == "test_harnesses.py"):
                continue
            # as_posix(), and the reason is a red guard on the host. `str()` on a
            # Windows PurePath gives "ingest\\fidelity.py"; the membership test
            # below names "ingest/fidelity.py", so the anti-vacuity assertion
            # FAILED on the host and PASSED on the bridge -- while every real
            # guard passed on both, because those search the VALUES. A key
            # shaped by the platform is a guard that is true on one interpreter
            # and false on another, which is FINDING 57's rule arriving in an
            # assertion instead of in a number.
            out[f.relative_to(root).as_posix()] = f.read_text(encoding="utf-8")
    return out


def test_every_mutation_target_still_exists() -> None:
    """A mutation whose target text has moved proves nothing, and says so only
    when somebody runs that harness on the host.

    F5, and it is this session's own defect. Ruling 68 relaxed one clause in
    `ingest/fidelity.py` from `!=` to `<` and FINDING 51 replaced a whole
    reachability expression; two mutations in `scripts/mutate_fidelity.py` still
    named the old text and reported MISS -- "mutation target not found". Nothing
    caught it. The length check above passed, because 55 still equals 55; the
    suites passed, because a suite is indifferent to what a harness names; and
    the only detector was a host run of that one harness.

    FINDING 46's sentence, in a new direction: a defect is fixed in the file
    where it was found and the search for its siblings is a separate act nobody
    scheduled. This is that act, scheduled. Eight of nine harnesses were clean
    when it was written, which is what makes the ninth worth an assertion rather
    than a note.
    """
    print("\nevery mutation target still exists in the source it names")
    sources = _mutable_sources()

    # Anti-vacuity, both directions. A search corpus that collapsed would report
    # every target as present; a matcher that always said "found" would too.
    expect(len(sources) > 20 and "ingest/fidelity.py" in sources,
           "the searchable sources are found and counted -- a collapsed corpus "
           "would pass every guard below by finding nothing to contradict them")
    expect(not any("a mutation target that cannot exist in any source" in s
                   for s in sources.values()),
           "GUARD a target absent from every source really is reported absent, "
           "so a clean result below is a reading and not an empty haystack")

    opaque_total = 0
    for h in HARNESSES:
        targets, opaque = _mutation_targets(_tree(h))
        opaque_total += opaque
        if targets is None:
            print(f"       {h.name}: no MUTATIONS list -- its targets are inlined "
                  f"and cannot be read here. Counted, not failed on")
            continue
        missing = sorted({t for t in targets
                          if not any(t in s for s in sources.values())})
        expect(not missing,
               f"GUARD every mutation target in {h.name} still occurs in the "
               f"sources it names")
        if missing:
            for t in missing[:4]:
                print(f"       gone: {t.strip()[:88]!r}")
    if opaque_total:
        print(f"       {opaque_total} mutation target(s) are not string literals "
              f"and are not checked here -- counted, because a target this cannot "
              f"read is not a target it has verified")


def counted_lines() -> None:
    """Reported, never gated. FINDING 56: a count that surprises somebody is a
    conversation, and an assertion invented today is a rule nobody agreed to."""
    print("\ncounted, not gated")
    with_baseline = [h.name for h in HARNESSES
                     if "BASELINE" in h.read_text(encoding="utf-8")]
    print(f"       {len(with_baseline)} of {len(HARNESSES)} harness(es) carry a "
          f"BASELINE block")
    missing = sorted({h.name for h in HARNESSES} - set(with_baseline))
    if missing:
        print(f"       without one: {', '.join(missing)}")
    totals = []
    for h in HARNESSES:
        muts = _literal(_tree(h), "MUTATIONS")
        if muts is not None:
            totals.append((h.name, len(muts)))
    print(f"       declared mutations: "
          + ", ".join(f"{n}={c}" for n, c in totals))
    print(f"       total: {sum(c for _, c in totals)} across "
          f"{len(totals)} harness(es) that declare a MUTATIONS list")
    # The stricter idea this check's first draft asserted and should not have.
    # Harmless under the filter above, and worth seeing rather than gating.
    split_bare = [h.name for h in HARNESSES if _fail_calls(_tree(h), "split")]
    print(f"       {len(split_bare)} harness(es) slice the label with "
          f"split(\"FAIL\", 1) rather than split(\"FAIL \", 1)"
          + (f": {', '.join(split_bare)}" if split_bare else ""))
    print(f"       Both spellings give the same label once the filter takes the "
          f"space. Reported because nine copies of one matcher is the "
          f"consolidation owed to F5, not because either is wrong.")


def main() -> int:
    print("the mutation harnesses, as a directory — FINDING 61")
    test_the_population_exists()
    test_the_fail_matcher_takes_the_space()
    test_mutations_are_applied_as_bytes()
    test_mutations_and_expected_are_the_same_length()
    test_every_mutation_target_still_exists()
    counted_lines()
    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
