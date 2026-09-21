# RoutePilot benchmark contract

Each JSONL scenario contains the original request and synthetic context, an
expected tool call (or required clarification), simulated tool candidates,
explicit hard constraints, utility weights, and the oracle's expected choice.

Predictions contain `scenario_id`, `tool_call`, `choice_id`, and
`clarification`. The evaluator never asks a model to grade another model.

The Module 1 fixture is deliberately small enough to audit by hand. It tests
the evaluator and contract, not model quality. Later releases should add held-
out cases without silently editing these fixtures.
