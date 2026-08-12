# Fixtures — not runs

Five artefacts from a manual check of `run_answer._archive`'s same-second
collision loop, written into `eval/answer_runs/` by hand and left there. They
carry an `answer` key and no `question`, so they are not runs and must not be
counted as any.

Moved here so a Part 8 harness can glob `eval/answer_runs/*.json` without
special-casing them. `recover_answer_baseline.inspect_existing` classifies files
by the presence of a `question` key, so the classification does not depend on
this directory existing — but a directory of runs that holds only runs is worth
more than a filter that has to be remembered.
