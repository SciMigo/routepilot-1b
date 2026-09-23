# RoutePilot benchmark contract

Each JSONL scenario contains the original request and synthetic context, an
expected tool call (or required clarification), simulated tool candidates,
explicit hard constraints, utility weights, and the oracle's expected choice.

Predictions contain `scenario_id`, `tool_call`, `choice_id`, and
`clarification`. The evaluator never asks a model to grade another model.

The Module 1 fixture is deliberately small enough to audit by hand. It tests
the evaluator and contract, not model quality. Later releases should add held-
out cases without silently editing these fixtures.

## Module 2 scenario generation

`benchmark.routepilot_data` creates contexts, candidates, hard constraints, and
utility weights before rendering request text. It derives every
`expected_choice_id` by executing the oracle; the generator never accepts a
teacher-authored label.

Reproduce the committed fixture:

```bash
python3 -m benchmark.routepilot_data.cli \
  --seed 20260923 \
  --count-per-family 2 \
  --output /tmp/routepilot-module-02.jsonl

cmp benchmark/scenarios/module-02.jsonl /tmp/routepilot-module-02.jsonl
```

The eight rows are a generator scaffold, not a training dataset. Entire
`template_family` values are assigned to either `train` or `development`; a
family cannot cross the boundary merely because its rows have different names
or numbers. The private final holdout is not generated or committed here.

## Module 3 baseline runs

`benchmark.routepilot_baselines` sends a frozen prompt to any compatible
chat-completions endpoint. It exposes only the request, application context,
and simulated candidates—not constraints, utility weights, expected calls, or
oracle choices. Responses are parsed as exact, unfenced JSON with no retries or
repairs.

Start the local model server as described in the Module 3 lab, then run:

```bash
python3 -m benchmark.routepilot_baselines.cli \
  --scenarios benchmark/scenarios/module-02.jsonl \
  --split development \
  --output-dir runs/qwen25-15b-base \
  --run-id qwen25-15b-base \
  --provider-name mlx-local \
  --base-url http://127.0.0.1:8080/v1 \
  --model mlx-community/Qwen2.5-1.5B-Instruct-4bit
```

The output directory is new for every run and contains exact requests, raw
responses, parsed predictions, component metrics, environment details, usage,
run metadata, a log, and checksums. Provider errors and parsing failures remain
in the evidence and receive no behavioral credit. The repository intentionally
does not ship invented base- or teacher-model scores.

## Where every constraint came from

Auditing by hand only works if a reader can trace each constraint to something.
Every hard constraint therefore declares a `source`:

- `request` — quoted or paraphrased from the driver's words;
- `context` — taken from the scenario's synthetic context block;
- `policy` — a declared product decision that cannot be derived from either,
  and which must carry a `note` saying what the decision is.

`ord-asian-stop` is the case that makes this matter. Its
`service_minutes <= 25` rule is the only thing that makes `thai-express`
infeasible, and it is `policy`: the deadline is already enforced by
`arrival_minutes <= 105`, and a 30-minute service budget would satisfy the
deadline too. The number is a choice about what "quick" means, not a
derivation. If it is the wrong choice, change the policy and version the
benchmark — do not relabel the expected answer.

`source` and `note` are documentation. The oracle reads only `field`, `op`,
and `value`, and a test asserts that stripping the annotations leaves every
expected choice unchanged.

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

## Fixture validation

Scenario files are validated before any scoring happens. `validate_scenario_file`
returns one line per problem — an empty list means the fixture is sound — and
each line names the file, the line, and the scenario it came from:

```text
benchmark/scenarios/module-01.jsonl:1: scenario 'ord-asian-stop' candidate
'seoul-kitchen': utility weight 'servce_minutes' has no matching candidate field
```

The CLI runs this first and exits `2` without scoring if anything is wrong, so
a malformed fixture is never reported as a bad model. Validation collects every
problem rather than stopping at the first, and it is a separate pass from
scoring: a scenario whose declared `expected_choice_id` disagrees with the
oracle is a fixture defect, not a reason for the evaluator to produce no
metrics at all.

Two rules about types are worth stating because they decide feasibility:

- **Equality is type-checked.** `"open": 1` does not satisfy `open == true`.
- **A utility weight naming an absent candidate signal is an error**, not a
  zero, so a typo in `utility_weights` cannot quietly reorder the ranking.
