# RoutePilot benchmark contract

Each JSONL scenario contains the original request and synthetic context, an
expected tool call (or required clarification), simulated tool candidates,
explicit hard constraints, utility weights, and the oracle's expected choice.

Predictions contain `scenario_id`, `tool_call`, `choice_id`, and
`clarification`. The evaluator never asks a model to grade another model.

The Module 1 fixture is deliberately small enough to audit by hand. It tests
the evaluator and contract, not model quality. Later releases should add held-
out cases without silently editing these fixtures.

## Scoring rules

Three rules decide what the numbers mean. They are stated here, in the module
reading, and in the `scoring.py` docstring so they cannot drift apart.

1. **Silence is never credited.** A prediction that is absent from the file, or
   that fails the schema check, scores as incorrect on schema validity, tool
   accuracy, constraint precision and recall, clarification accuracy, and
   selection accuracy. Declining to answer is a legitimate product behavior,
   but it is not the same as answering correctly.
2. **Safety is judged on whatever the prediction named.** A hard violation is
   charged against any candidate id the prediction carries, in every scenario —
   including one whose correct action was to ask a clarifying question — and
   regardless of whether the rest of the payload validated.
3. **No denominator moves when a model emits less.** Every rate is divided by a
   count taken from the scenario file. `selection_coverage` reports how often
   the model committed to a choice, so a model that answers nothing shows up as
   uncovered rather than merely blameless.

## Reconciliation

A prediction file can disagree with a scenario file in three ways that would
otherwise pass unnoticed: a scenario with no prediction, two predictions for
one scenario, and a prediction whose `scenario_id` names nothing. The result's
`reconciliation` block lists each one, and the CLI exits non-zero when the two
files do not line up, because metrics computed over a mismatched pair describe
a different run than the caller is reading.

Duplicate `scenario_id` lines resolve to the first occurrence, so a re-run of
the same file always produces the same score.
