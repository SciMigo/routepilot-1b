# Lab 3: Run comparable base and teacher baselines

This lab uses a local Python environment because it connects to model endpoints
and writes run artifacts. Do not paste API keys into commands, notebooks, JSONL,
or course submissions.

## 3.1 Audit the frozen prompt

Read `benchmark/routepilot_baselines/prompt.py`. Render one development scenario
and confirm that it includes only `request`, `context`, and `candidates`:

```bash
python3 - <<'PY'
import json
from benchmark.routepilot_baselines import build_messages
from benchmark.routepilot_eval.io import load_jsonl

scenario = next(
    item for item in load_jsonl("benchmark/scenarios/module-02.jsonl")
    if item["split"] == "development"
)
print(json.dumps(build_messages(scenario), indent=2))
PY
```

Explain why candidates are visible while constraints and utility weights are
not. Record the prompt version; do not edit it between model runs.

## 3.2 Run the unmodified student

On Apple Silicon, install MLX-LM in an isolated environment and start its local
experiment server with the four-bit conversion:

```bash
mlx_lm.server \
  --model mlx-community/Qwen2.5-1.5B-Instruct-4bit \
  --port 8080
```

In another terminal:

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

Pin the installed MLX-LM version in `environment.json` before treating the run
as publishable evidence. The bundled environment record captures Python and OS
information but cannot infer every server package or model-file revision.

If Apple Silicon is unavailable, use another OpenAI-compatible endpoint and
record its provider, exact artifact, quantization, and serving configuration.
Do not describe that result as the MLX baseline.

## 3.3 Inspect failures before changing anything

Open `requests.jsonl`, `responses.jsonl`, `predictions.jsonl`, and
`metrics.json`. Inspect every parse failure and at least five behavioral
failures when the dataset is expanded enough to contain them.

Classify each as:

- provider or truncation failure;
- invalid JSON/output schema;
- wrong tool;
- missing or added argument;
- incorrect clarification behavior;
- infeasible selection;
- feasible but incorrectly ranked selection.

Do not strip markdown fences, extract JSON substrings, or retry. Those can be
evaluated later as a separately named application strategy.

## 3.4 Run a named teacher

Choose a teacher whose terms permit this evaluation. Set its credential in an
environment variable and run the identical harness:

```bash
export ROUTEPILOT_TEACHER_API_KEY="..."

python3 -m benchmark.routepilot_baselines.cli \
  --scenarios benchmark/scenarios/module-02.jsonl \
  --split development \
  --output-dir runs/teacher-baseline \
  --run-id teacher-baseline \
  --provider-name YOUR_PROVIDER \
  --base-url YOUR_OPENAI_COMPATIBLE_V1_URL \
  --model EXACT_MODEL_IDENTIFIER \
  --api-key-env ROUTEPILOT_TEACHER_API_KEY
```

Replace placeholders; never commit the key. Record pricing used to calculate
cost, geographic endpoint if relevant, retention setting, model/version, and
terms governing later use of outputs. Evaluation permission is not automatically
permission to train on or redistribute those outputs.

## 3.5 Decide whether to train

Create a table comparing both runs on every RoutePilot metric, parse/provider
failure count, tokens, latency distribution, and cost. Inspect raw examples
behind the largest deltas.

Write a go/no-go memo answering:

1. Which repeated base-model failure matters most to the product?
2. Does the teacher show that the behavior is achievable under this contract?
3. Could deterministic application code or a prompt change solve it more safely?
4. Which scenario family would supply training evidence without touching the
   final holdout?
5. What metric must improve, and what protected metric must not regress?

“Do not train yet” is a successful lab outcome when the evidence supports it.

## Completion check

```bash
python3 -m unittest discover -s benchmark/tests -v
```

Submit the two run directories and memo. Remove secrets; retain raw failures.
