"""Restore the three Periplus records to the full text of the edition they cite.

Found during A4 (2026-08-13), while extracting subject places: four places named
in the reference translation were absent from the original text on disk. The
cause was not an edition difference. **1,483 characters of Koine Greek — 20% of
the three records' original text — were missing from the excerpts**, against the
same Greek Wikisource text of C. Müller, *Geographi Graeci Minores* I (1855)
that every one of them names in `citation_original`.

    §4   58.8% present   internal sentences dropped (Diodorus island; the
                         elephant/rhinoceros note; the Alalaei islands)
    §5  100.0%
    §6   70.5% present   internal sentences dropped (the bronze melievtha; the
                         Arabian/Indian imports; the January-September season)
    §27  84.5% present   truncated: "Ἔχει δὲ καὶ αὐτὴ σύγχρησιν τῶν τοῦ πέραν
                         ἐμπορίων, Βαρυγάζων καὶ Σκυθίας καὶ Ὀμάνων καὶ τῆς
                         παρακειμένης Περσίδος."
    §28  86.0% present   truncated: the sailing season
    §29  74.8% present   truncated: the unhealthiness of the frankincense coast
    §53 100.0%
    §54 100.0%
    §55  59.1% present   truncated: the sea-serpents landfall sign
    §56 100.0%           one character differs: πολύς where Müller has πολὺς

The omissions were invisible for three reasons at once. `original_text_note`
said "wording is otherwise unaltered", which is true of every word present and
silent about the ones that are not. The reference translations were replaced
with *complete* Schoff in Part 6, so the two sides of each record drifted
further apart at the moment they were supposed to be reconciled. And nothing in
the pipeline compares an excerpt against its own cited source — `ingest/verify`
checks internal consistency, and internal consistency is exactly what a
uniformly short excerpt has.

Three consequences beyond A4, in descending order of how much they should worry
someone:

1. **`align.py` reports `ground="section"` for these pairs.** A §4 Greek chunk
   58.8% the length of its §4 English is a *strong* pairing claim over
   materially different text. The ground was honest about its evidence and the
   evidence was wrong.
2. **`chrf_ref` is confounded for exactly these records.** It compares a machine
   translation of a short Greek chunk against a full published English section,
   and PROGRESS.md calls `chrf_ref` "the only accuracy signal" the project has.
   This does not explain the Part 6 numbers by itself — §28 is 86% present and
   scored 0.275, while §4 is 58.8% present and scored 0.427 — but it is an
   uncontrolled variable in the measurement, and it was not known to be there.
3. **A Part 7 citation of Schoff's Alalaei or Diodorus sentence had no Greek to
   resolve to.** The two records held back as `pointer` are unreachable by
   construction; this was reachable and wrong.

Run:  python scripts/recover_periplus_a4.py [--check]

`--check` reports and writes nothing. Re-running is safe: it rebuilds each
excerpt from `data/a4_ws_sections.py` and writes only if the result differs.

After running, on the host:

    python -m ingest.verify
    python -m ingest.run_ingest        # changed chunks come back pending
    python -m ingest.run_embed         # re-embed them
    python -m retrieve.crosslingual_check
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "data" / "seed_corpus"

sys.path.insert(0, str(ROOT / "data"))
from a4_ws_sections import RECORDS, WS  # noqa: E402

RECOVERED_ON = "2026-08-13"
SOURCE_URL = "https://el.wikisource.org/wiki/Περίπλους_της_Ερυθράς_Θαλάσσης"

NOTE_SUFFIX = (
    " RECOVERY {date}: the excerpt held on disk was found to be {pct}% of this "
    "section range as the cited Wikisource text gives it — {missing} characters "
    "of Koine Greek missing across {n} sections, dropped silently and not "
    "recorded by the note above, which described only the wording of what was "
    "present. Restored in full from the same source and the same edition, with "
    "the same normalisation applied as on 2026-08-09: editorial brackets and "
    "parentheses removed and their contents kept, asterisk sigla removed, runs "
    "of whitespace collapsed, and Müller's section numbers retained so the "
    "chunker can still split on them. No word is altered, added or reordered. "
    "Found while extracting subject places for Phase 2 A4: places named in the "
    "reference translation had no counterpart in the original — see PROGRESS.md."
)


def normalise(text: str) -> str:
    """Exactly the normalisation the 2026-08-09 recovery applied.

    Verified against the three sections that survived intact (§5, §53, §54):
    under these rules they compare identical to the source, character for
    character. A rule set that could not reproduce the text already on disk
    would not be safe to rebuild the rest of it with.
    """
    for ch in "[]()*":
        text = text.replace(ch, "")
    text = re.sub(r"\s+", " ", text)
    return unicodedata.normalize("NFC", text).strip()


def build_excerpt(sections: list[int]) -> str:
    return "\n\n".join(f"{n}. {normalise(WS[n])}" for n in sections)


def split_sections(excerpt: str, sections: list[int]) -> dict[int, str]:
    out: dict[int, str] = {}
    for n in sections:
        m = re.search(rf"(?m)^{n}\. (.*?)(?=\n\n\d+\. |\Z)", excerpt, re.S)
        out[n] = normalise(m.group(1)) if m else ""
    return out


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    changed = 0

    for rel, sections in RECORDS.items():
        path = SEED / rel
        record = json.loads(path.read_text(encoding="utf-8"))
        before = record["original_text_excerpt"]
        after = build_excerpt(sections)

        old = split_sections(before, sections)
        new = split_sections(after, sections)

        short = {n: len(new[n]) - len(old[n]) for n in sections if len(new[n]) > len(old[n])}
        missing = sum(short.values())
        pct = 100 * sum(len(old[n]) for n in sections) / sum(len(new[n]) for n in sections)

        print(f"\n{rel}")
        for n in sections:
            gap = len(new[n]) - len(old[n])
            if gap > 0:
                kind = "truncated" if new[n].startswith(old[n]) else "internal omission"
                print(f"  §{n}: {100*len(old[n])/len(new[n]):5.1f}%  -{gap:4d}  {kind}")
            elif old[n] != new[n]:
                print(f"  §{n}: 100.0%  same length, {sum(a != b for a, b in zip(old[n], new[n]))} char(s) differ")
            else:
                print(f"  §{n}: 100.0%  identical")

        if before == after:
            print("  -> already current, nothing written")
            continue

        if check_only:
            print(f"  -> WOULD rewrite ({missing} chars recovered)")
            changed += 1
            continue

        record["original_text_excerpt"] = after
        record["original_text_note"] = record["original_text_note"].rstrip() + NOTE_SUFFIX.format(
            date=RECOVERED_ON, pct=f"{pct:.1f}", missing=missing, n=len(short)
        )
        record["text_recovered"] = RECOVERED_ON
        path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"  -> rewritten, {missing} characters recovered")
        changed += 1

    print(f"\n{changed} record(s) {'would be ' if check_only else ''}updated.")
    print(f"Source: {SOURCE_URL} (ed. C. Müller, GGM I, Paris 1855; public domain)")
    if changed and not check_only:
        print("\nNext, on the host: ingest.verify -> run_ingest -> run_embed "
              "-> retrieve.crosslingual_check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
