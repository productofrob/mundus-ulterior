"""Why does C2a reach only thirteen sections? (Block C ruling 8)

`--collapse` folded 13 chunks out of 450 and converted one miss. Fifteen
documents hold a translation, so the question is whether the other twelve fail
to align because of something in retrieval — which would be a C-block problem —
or because their seed records carry no section markers, which is an A-block
authoring fix wearing a retrieval costume.

Reads the index and `answer.align.pair_chunks`, the same module ruling 2 and
ruling 8 both use, so this reports the grounds the collapse ACTUALLY sees rather
than a second opinion about them. No API calls, no spend.

Run:  python scripts/probe_sections.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

VIEW = "retrievable_chunks_with_distractors"


def main() -> int:
    import psycopg

    from eval.run_ranking_check import resolve_sections, _AlignRow  # noqa: F401
    from ingest import db

    reason = db.check_connection()
    if reason:
        raise SystemExit(reason)

    with psycopg.connect(db.get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT doc_id, role, count(*) FROM {VIEW} "
                f"WHERE doc_id NOT LIKE 'distractor-%' "
                f"GROUP BY doc_id, role ORDER BY doc_id, role;"
            )
            rows = cur.fetchall()
        groups, primary_by_doc = resolve_sections(conn, VIEW)

    by_doc: dict[str, Counter] = {}
    for doc_id, role, n in rows:
        by_doc.setdefault(doc_id, Counter())[role] = n

    grounds: dict[str, Counter] = {}
    for canon, _members, ground in groups:
        grounds.setdefault(canon.split("::")[0], Counter())[ground] += 1

    print(f"{'document':38s} {'orig':>5s} {'trans':>6s}  alignment grounds")
    both = section_docs = 0
    for doc_id in sorted(by_doc):
        counts = by_doc[doc_id]
        o, t = counts.get("original", 0), counts.get("translation", 0)
        if not t:
            continue
        both += 1
        g = grounds.get(doc_id, Counter())
        if g.get("section"):
            section_docs += 1
        marker = "  <- collapses" if g.get("section") else ""
        marker += f"   primary={primary_by_doc.get(doc_id, '?')}"
        print(f"{doc_id:38.38s} {o:5d} {t:6d}  {dict(g) or 'no aligned pair'}{marker}")

    total = Counter(ground for _c, _m, ground in groups)
    print()
    print(f"documents holding a translation      {both}")
    print(f"  of those, aligning on `section`    {section_docs}   <- these are all C2a can reach")
    print(f"aligned pairs by ground              {dict(total)}")
    print()
    print("A document on `index` ground has a translation that align.pair_chunks")
    print("cannot tie to a SECTION — the two texts merely split into the same")
    print("number of pieces. Ruling 8 refuses to collapse on that, for the same")
    print("reason ruling 2 refuses to accept an alternate on it: it would fold a")
    print("NEIGHBOURING section's translation into a passage and silently remove")
    print("a different passage from the ranking.")
    print()
    print("If most of the gap is `index`, C2a's reach is bounded by missing")
    print("section markers in the seed records, which is Block A authoring work")
    print("and not a retrieval problem at all.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
