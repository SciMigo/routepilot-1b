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

Then find the single constraint that makes `thai-express` infeasible. It is not
the detour (4 minutes against a 10-minute limit) and not the deadline (arrival
104 against 105). It is `service_minutes <= 25`, whose `source` is `policy`:
a declared decision about what "quick" means, which no amount of reading the
request will derive. Read its `note`, then argue for or against the number.
Deciding it is wrong is a legitimate outcome — the response is to change the
policy and version the benchmark, not to relabel the expected answer.

## 1.3 Lose a constraint

Restore the choice, then remove `max_detour_minutes` from the same prediction's
tool arguments. Confirm that constraint recall falls while selection remains
correct. Explain why an end-to-end pass/fail would hide this defect.

## 1.4 Add a clarification case

Add a scenario where a required compatibility fact is missing. Every scenario
needs `id`, `expected_clarification`, and `expected_choice_id`; for this one set
`expected_clarification` to `true`, `expected_call` to `null`, and
`expected_choice_id` to `null`. Write a prediction that asks for the missing
fact, and add a unit test for the behavior.

Check your scenario before scoring it:

```bash
python3 -c "from benchmark.routepilot_eval import validate_scenario_file; \
  print(validate_scenario_file('benchmark/scenarios/module-01.jsonl'))"
```

An empty list means the fixture is sound. Every other line names the file, the
line, and the scenario it came from. The evaluator runs the same check and
exits `2` before scoring if anything is wrong, so a malformed fixture can never
be mistaken for a bad model.

Now make the same scenario harder: give it a candidate list, and write a second
prediction that skips the question and picks one anyway. Confirm that this
raises `hard_violation_rate` and lowers both `clarification_accuracy` and
`selection_accuracy`. A model that guesses a safety-relevant fact must not be
scored as if it had asked.
