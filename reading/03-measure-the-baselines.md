# Measure the Baselines

Post-training begins with a comparison, not a training command. Before changing
weights, we need to know what the proposed student already does, what a stronger
teacher can do under the same contract, and which failures are important enough
to justify a data and maintenance program.

A number without its setup is not a baseline. “The model scored 80%” omits the
model revision, quantization, prompt, parser, retry policy, sampling settings,
scenario split, serving stack, and evaluator. RoutePilot stores those choices
alongside raw requests and responses so later adapter claims can compare like
with like.

## Evaluate the application contract

RoutePilot does two model-facing jobs in one benchmark record. It extracts a
structured tool request, then ranks simulated candidates that represent the
tool's current result. The baseline prompt therefore exposes:

- the driver's request;
- permitted application context;
- simulated candidate records.

It withholds:

- the expected tool call;
- hard-constraint annotations;
- utility weights;
- the oracle's expected choice;
- split and generator metadata.

Candidates are visible because ranking them is part of the intended behavior.
Oracle rules are hidden because they are benchmark truth. A unit test checks
this boundary so a later refactor cannot quietly make the task easier.

## Freeze adaptation before comparison

HELM frames evaluation as more than a dataset and model: a scenario is adapted
to a model through prompting and inference choices, then measured. RoutePilot's
baseline freezes those choices in `routepilot-baseline-v1`:

- one system instruction;
- a compact JSON rendering of the public scenario fields;
- temperature zero;
- a fixed output-token cap;
- exact JSON parsing;
- zero retries and zero repairs.

Temperature zero reduces one source of variation, but it is not a universal
reproducibility guarantee. Providers can change kernels, model aliases, serving
stacks, or tie-breaking. Record exact identifiers and provider request IDs when
available, and treat a rerun as new evidence rather than overwriting an old one.

## Strict output is part of the behavior

The model must return exactly one object:

```json
{
  "tool_call": {"name": "search_route_stops", "arguments": {}},
  "choice_id": "candidate-id",
  "clarification": null
}
```

Markdown fences, leading explanations, extra reasoning keys, and malformed JSON
fail parsing. The runner does not search for a JSON substring or ask the model
again. Repair and retries may be sensible product features, but adding them
changes the system under test. They deserve a separately named run with their
own latency, cost, and failure behavior.

A parse failure remains in `responses.jsonl`. Its corresponding prediction is
deliberately schema-invalid, so it stays reconciled to the scenario while
receiving no behavioral credit. Silence or bad packaging cannot improve a rate.

## Preserve raw evidence

HELM publishes raw prompts and completions as part of transparent evaluation.
The RoutePilot run contract follows the same principle at course scale. Each run
contains:

- `requests.jsonl` with the exact messages and prompt version;
- `responses.jsonl` with raw text, usage, latency, errors, and request IDs;
- `predictions.jsonl` with parsed or explicitly invalid predictions;
- `metrics.json` with component scores and reconciliation;
- run, environment, cost, log, and checksum records.

This structure separates facts from interpretation. A future reader can tell
whether poor schema validity came from prose wrappers, truncation, endpoint
errors, or a model that misunderstood the requested object.

Credentials never belong in this evidence. The CLI reads an API key from a
named environment variable and records neither its name nor its value in model
traffic.

## Run the proposed student locally

The proposed student remains Qwen2.5-1.5B-Instruct. Qwen's model card identifies
the checkpoint and Apache 2.0 license. The MLX community publishes a four-bit
conversion for Apple Silicon, and MLX-LM exposes an HTTP endpoint similar to the
OpenAI chat-completions interface.

MLX-LM warns that its server has only basic security checks and is not
recommended for production. That is acceptable for a loopback-only course
experiment; it is not evidence for the eventual vehicle serving architecture.
Bind and expose local model servers cautiously.

Quantization is part of the model setup. A score from the four-bit conversion
is a four-bit baseline, not an unqualified score for every representation of
Qwen2.5-1.5B-Instruct.

## Compare a teacher without changing the test

A teacher establishes a stronger reference and may later help create language
variation or training targets. It does not receive a friendlier prompt, more
retries, or hidden benchmark fields. Both models use the same development
scenarios, prompt version, temperature, token cap, parser, and evaluator.

Record the exact teacher identifier. A rolling alias is poor experimental
provenance because the underlying model may change. Record usage, applicable
price, retention configuration, endpoint, and terms. Permission to call a model
for evaluation does not automatically permit using its outputs for training or
redistributing derived weights.

## Read component failures as hypotheses

Aggregate selection accuracy is not a data plan. Component failures suggest
different next actions:

- Low schema validity may call for a better output protocol, constrained
  decoding, or format examples—not domain training data.
- Wrong tools point to routing examples.
- Low constraint recall points to linguistic coverage around limits and context.
- Hard violations demand protected negative examples and application safeguards.
- Clarification failures need missing-context cases.
- Correct extraction but wrong feasible choice points to ranking evidence.

These are hypotheses until raw failures are inspected. A single scenario can
fail multiple components, and a tiny public fixture supports debugging rather
than a stable quality estimate.

## Decide whether training is justified

Training is warranted only when the base-model defect is repeatable,
product-relevant, and not more safely handled by deterministic code or a modest
prompt change. The teacher should demonstrate that the output contract is
achievable, but matching the teacher is not automatically the objective.

Before proceeding, write a decision with:

- the target failure family;
- the metric expected to improve;
- a protected metric that may not regress;
- the data source and rights boundary;
- the base and teacher run identifiers;
- the simpler alternatives considered.

“Do not train” is a valid conclusion. Post-training is a means of changing
repeatable behavior, not a required ritual in a course bearing its name.

## Current evidence boundary

The repository contains and tests the frozen prompt, strict parser,
OpenAI-compatible client, and complete run-artifact writer. It does not yet
contain a real Qwen or teacher run. Until raw directories are committed, all
quality, latency, usage, and cost outcomes remain unobserved.

## Sources

- Liang et al., [Holistic Evaluation of Language
  Models](https://arxiv.org/abs/2211.09110), 2022.
- OpenAI, [Evals](https://github.com/openai/evals).
- Apple MLX team, [MLX-LM HTTP Model
  Server](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/SERVER.md).
- Qwen, [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct).
- MLX Community,
  [Qwen2.5-1.5B-Instruct-4bit](https://huggingface.co/mlx-community/Qwen2.5-1.5B-Instruct-4bit).
