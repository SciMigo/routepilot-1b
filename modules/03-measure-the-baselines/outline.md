# Measure the Baselines — Slide Outline

## Slide 1: “The model scored 80%” is incomplete
- Which model revision and quantization?
- Which prompt, parser, retries, and sampling settings?
- Which scenario split and evaluator version?

## Slide 2: Measure the system under test
```text
scenario -> frozen prompt -> endpoint -> raw response -> strict parser -> metrics
              versioned        named       retained        no repair
```
- Change any box and you have a different baseline.

## Slide 3: Keep benchmark truth out of the prompt
- Visible: request, application context, simulated tool candidates.
- Hidden: expected call, hard constraints, weights, oracle choice, split labels.
- A passing prompt-leak test is part of the harness.

## Slide 4: One output contract
```json
{
  "tool_call": {"name": "search_route_stops", "arguments": {}},
  "choice_id": "candidate-id",
  "clarification": null
}
```
- Exactly three keys; one JSON object; no prose or fences.

## Slide 5: Do not repair the baseline
- Stripping fences changes measured schema reliability.
- Retrying changes the number of opportunities the model received.
- Preserve failure now; test a repair strategy later as a separate system.

## Slide 6: The student path
- Qwen2.5-1.5B-Instruct is the proposed student, not the presumed winner.
- Four-bit MLX conversion enables a local Apple Silicon experiment.
- MLX's server is an experiment endpoint, not production infrastructure.

## Slide 7: The teacher path
- Name the exact model/version and applicable output terms.
- Use the same prompt, temperature, token cap, parser, and development rows.
- Record usage and cost; never paste a secret into a run artifact.

## Slide 8: Why raw traffic matters
- A score cannot explain truncation, refusals, prose wrappers, or provider errors.
- `requests.jsonl` and `responses.jsonl` make every metric inspectable.
- Request IDs support provider-side investigation without storing credentials.

## Slide 9: Compare components
- Schema, tool choice, extraction precision/recall, clarification.
- Selection accuracy and coverage; hard violations separately.
- Latency and cost describe operation, not intelligence.

## Slide 10: Cluster before training
- Parser failures suggest prompt/decoding or model-format issues.
- Extraction failures suggest targeted language coverage.
- Correct calls but wrong choices suggest ranking examples.
- Guessing missing facts suggests clarification hard negatives.

## Slide 11: A teacher is not automatically a training target
- It may be expensive, verbose, or weak on the exact contract.
- Teacher outputs need rights review before becoming training data.
- A baseline can be useful even when its outputs are never retained for SFT.

## Slide 12: Go/no-go criteria
- Is the base failure repeatable and product-relevant?
- Does the teacher demonstrate achievable improvement?
- Could prompting or deterministic code solve it more simply?
- Is post-training worth its data, compute, and maintenance cost?

## Slide 13: Lab deliverable
- Two complete run directories with identical prompt version.
- A metric delta table and five inspected raw failures.
- A one-page decision memo, including reasons not to train.

## Slide 14: Next paid module
- Render licensed examples and loss masks from validated scenarios.
- Freeze dataset version before the first adapter run.
- No training claim without a reproducible baseline to beat.
