# Lab 1: Audit the RoutePilot contract

Run commands from the repository root with Python 3.11 or newer.

## 1.1 Establish the reference result

```bash
python3 -m benchmark.routepilot_eval.cli \
  benchmark/scenarios/module-01.jsonl \
  benchmark/predictions/reference.jsonl
```

Explain why `hard_violation_rate` has the opposite direction from the other
metrics. Keep the raw JSON result for comparison.

Then run the evaluator against an empty prediction file and compare. Every
accuracy falls to zero, `hard_violation_rate` stays at `0.0`, and
`selection_coverage` falls to `0.0`. Explain why a zero hard-violation rate is
the honest answer for a model that suggested nothing, and which metric is doing
the work of telling you so.

## 1.2 Choose an infeasible candidate

Copy the reference predictions and change `ord-asian-stop` to choose
`thai-express`. Run the evaluator again. Identify which metrics changed and why
the tool-call metric did not.

## 1.3 Lose a constraint

Restore the choice, then remove `max_detour_minutes` from the same prediction's
tool arguments. Confirm that constraint recall falls while selection remains
correct. Explain why an end-to-end pass/fail would hide this defect.

## 1.4 Add a clarification case

Add a scenario where a required compatibility fact is missing. Set
`expected_clarification` to `true`, provide no expected tool call, and write a
prediction that asks for the missing fact. Add a unit test for the behavior.
