"""W3's four worked examples -- the section 5 proof, as a command.

THE DELIVERABLE IS THAT ALL FOUR CLASSIFY CORRECTLY AND NONE IS CURATED.

Three of them are the sources Block F refused FOR AN INSTRUMENT REASON AND NOT
A SOURCE REASON: the BnF cameo of Shapur I seizing Valerian, whose description
is French, and the two Thai institutional records, Phu Khao Thong and Khlong
Thom. The fourth is FINDING 82's half of the same defect, which lives in
`classify_translation` and would otherwise be asserted rather than shown.

Run: python scripts/w3_worked_examples.py
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# FINDING 10: this process's own stdout. Through a pipe or a redirect on
# Windows it falls back to the locale codec, which cannot encode Thai, French
# accents or Persian, and it raises mid-output with the file half written and
# every tuple in it correct. This file prints all three by construction, so it
# is the entry point most likely to hit it.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

from ingest.fidelity import (  # noqa: E402
    DeclarationError,
    check_curation_gate,
    check_declaration,
    classify_original,
    classify_translation,
    non_latin_ratio,
)

DATA = ROOT / "data" / "w3_worked_examples.json"

# WRITTEN IN W3_START.md AT COMMIT 59dcd1e, BEFORE THE FIX EXISTED, as
# prediction P2. Each names what the tuple was and what it becomes. Kept here
# rather than in prose so the run either matches the prediction or does not.
PREDICTED = {
    "bnf-camee-360":          (("object_description", "en", True),
                               ("object_description", "fra", True)),
    "phu-khao-thong":         (("object_description", "en", True),
                               ("object_description", "tha", True)),
    "khlong-thom":            (("object_description", "en", True),
                               ("object_description", "tha", True)),
    "parsigdatabase-persian": (("translation", "en", True),
                               ("translation", "pes", True)),
}


def main() -> int:
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    failures: list[str] = []

    for ex in doc["examples"]:
        key = ex["key"]
        text, code, role = ex["text"], ex["declared"], ex["role"]
        was, expected = PREDICTED[key]

        print(f"\n{key}  --  {ex['source']}")
        print(f"  refused by   {ex['refused_by']}")
        print(f"  declared     {code!r}   non_latin_ratio {non_latin_ratio(text):.3f}")

        # The cross-check accepts the declaration. This is FINDING 86's half:
        # under the deleted allowlist a page of Thai scored 0.00 and the field
        # could not be told from English.
        try:
            check_declaration(key, "original_text_excerpt"
                              if role == "original" else "reference_translation",
                              code, text)
            print("  declaration  ACCEPTED by the cross-check")
        except DeclarationError as exc:
            failures.append(f"{key}: cross-check refused a correct declaration: {exc}")
            print(f"  declaration  REFUSED -- {exc}")
            continue

        if role == "original":
            got = classify_original(text, key, code, ex["source_type"])
        else:
            got = classify_translation(text, ex["source_type"], code)

        print(f"  before W3    {was}")
        print(f"  predicted    {expected}")
        print(f"  classifies   {got}   {'MATCH' if got == expected else 'DOES NOT MATCH'}")
        if got != expected:
            failures.append(f"{key}: predicted {expected}, got {got}")

        # AND IT IS STILL NOT CURATABLE. Section 5: the instrument is fixed and
        # no record is added. The gate is what makes the second half true, and
        # it is the ruling W3 does not make, enforced.
        try:
            check_curation_gate(key, "original_text_excerpt", code)
            gated = False
        except DeclarationError:
            gated = True
        if code in ("tha", "fra"):
            print(f"  as a RECORD  REFUSED at load, pending the section 8 ruling"
                  f"{'' if gated else '  <-- EXPECTED A REFUSAL AND GOT NONE'}")
            if not gated:
                failures.append(f"{key}: the curation gate did not refuse {code!r}")
        else:
            print("  as a RECORD  not gated -- a modern scholarly translation is "
                  "a translation, not the category section 8 is about")

    print()
    if failures:
        print(f"FAILED ({len(failures)})")
        for f in failures:
            print(f"  x {f}")
        return 1
    print("All four worked examples classify as W3_START.md predicted, "
          "and none of them is curated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
