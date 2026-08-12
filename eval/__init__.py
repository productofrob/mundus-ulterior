"""Evaluation harness and gold data (Phase 1, Part 8 — started in Part 6).

The probes that decide whether retrieval and translation work are *data*, in
eval/gold/, not Python. They were code until Part 6, and code is where a probe
quietly passes for the wrong reason: the pepper probe asserted a doc_id, matched
a different passage of the same document, and reported PASS while the passage it
was asking about was not in the database at all.

Data does not stop that on its own. What it buys is that the expectation, the
rationale for it, and the thing being asserted all sit in one reviewable file,
and that adding a case does not mean editing a runner.
"""
