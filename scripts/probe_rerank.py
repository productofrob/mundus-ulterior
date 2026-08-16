"""C3 pre-flight: does a rerank call actually reach the provider?

One query, three documents, one request. C3_START.md names this as the first
action for a reason — discovering that the key, the alias or the route does not
work halfway through a design is the expensive version of the same finding.

It also settles two things documentation does not: WHICH route the proxy answers
on (LiteLLM has exposed both `/v1/rerank` and `/rerank`), and what the response
JSON actually looks like. Both are printed raw, so the client is written against
an observed response rather than a quoted one.

Run with the gateway up, from the repo root:
    python scripts/probe_rerank.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from retrieve.rerank import (  # noqa: E402
    DEFAULT_MODEL, RerankError, rerank_documents,
)

QUERY = "frankincense harvested on the Arabian coast"

# Ordered deliberately so the right answer is NOT already first: a reranker that
# returned the input order unchanged would look correct against a list whose
# best document was at index 0, and this probe would then pass without the model
# having read anything.
DOCUMENTS = [
    "The Norwegian ship burial contained a wooden cart and twelve horses.",
    "Beyond this place the coast produces frankincense, gathered by the "
    "inhabitants and traded from the harbour to ships bound for Egypt.",
    "A bronze figurine of a dancing girl, cast in the Deccan.",
]
EXPECTED_BEST = 1


def main() -> int:
    print(f"model  {DEFAULT_MODEL}   query {QUERY!r}   {len(DOCUMENTS)} documents")
    try:
        response = rerank_documents(QUERY, DOCUMENTS)
    except RerankError as exc:
        print(f"\nFAILED\n{exc}")
        return 1

    print(f"\nroute answered: {response.path}")
    print(f"tokens: {response.total_tokens if response.total_tokens is not None else 'not reported'}")
    if response.notes:
        for note in response.notes:
            print(f"  note: {note}")

    print("\nranking:")
    for position, (index, score) in enumerate(response.scored, start=1):
        marker = "  <- expected best" if index == EXPECTED_BEST and position == 1 else ""
        print(f"  {position}. doc[{index}]  score {score:.6f}{marker}")
        print(f"       {DOCUMENTS[index][:78]}")

    best = response.scored[0][0] if response.scored else None
    if best != EXPECTED_BEST:
        print(
            f"\nThe call SUCCEEDED and the answer is wrong: the frankincense "
            f"passage is doc[{EXPECTED_BEST}] and the reranker put doc[{best}] "
            f"first. The plumbing works; the model or the alias does not do what "
            f"C3 assumes. Do not build on this until it is explained."
        )
        return 2

    print(
        "\nOK — the key reaches the provider, the alias resolves, and the model "
        "moved the right document from position 2 to position 1.\n"
        "Record the route above; retrieve/rerank.py tries both and this is the "
        "one that answered."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
