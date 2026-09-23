# RoutePilot-1B

RoutePilot-1B is a practical course about post-training a small, route-aware
automotive agent. The running artifact turns requests such as “find a quick
Asian stop on my route with no more than a ten-minute detour” into a structured
tool call, then ranks the candidates returned by a maps or POI service.

The model is deliberately **not** a database of restaurants, opening hours,
traffic, or charger availability. Those facts change and belong behind tools.
The model learns to extract constraints, choose a tool, reason over returned
candidates, and propose an action that a policy layer and driver can approve.

The initial student candidate is
[`Qwen2.5-1.5B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct),
an Apache-2.0-licensed 1B-class model. That is a starting hypothesis, not a
claim that it will win the benchmark.

## Current modules

**Module 1 — The Contract Before the Model** freezes the behavior and evaluation
contract before synthetic data or training begins.

**Module 2 — Generate Scenarios, Not Answers** adds a deterministic scenario
factory, oracle-derived labels, family-level train/development splits, and a
reproducible eight-scenario fixture.

**Module 3 — Measure the Baselines** freezes a provider-neutral prompt and
strict parser, runs the same development cases against an unmodified student
and a named teacher, and preserves the raw evidence needed to decide whether
training is justified. Together, the modules include:

- the course topic and slide outline;
- a source-backed reading;
- a deterministic scenario format and oracle;
- a small, hand-auditable benchmark fixture;
- an evaluator with component metrics and tests;
- a seeded scenario generator and validation CLI;
- an OpenAI-compatible baseline runner with raw response, environment, usage,
  metric, log, and checksum artifacts.

Run the benchmark:

```bash
python3 -m benchmark.routepilot_eval.cli \
  benchmark/scenarios/module-01.jsonl \
  benchmark/predictions/reference.jsonl
```

Run the tests:

```bash
python3 -m unittest discover -s benchmark/tests -v
```

Reproduce the Module 2 fixture:

```bash
python3 -m benchmark.routepilot_data.cli \
  --seed 20260923 \
  --count-per-family 2 \
  --output /tmp/routepilot-module-02.jsonl
cmp benchmark/scenarios/module-02.jsonl /tmp/routepilot-module-02.jsonl
```

Run the Module 3 baseline harness against a local OpenAI-compatible endpoint:

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

See [PLAN.md](PLAN.md) for the planned course sequence and
[LABS.md](LABS.md) for the proposed lab and provider boundaries. See
[OFFERING.md](OFFERING.md) for the proposed free/paid product boundary and
[AUTHORING.md](AUTHORING.md) for evidence and publishing rules.

## Status

This repository contains three authored course modules, an early benchmark
contract, a deterministic scenario-generation scaffold, and a tested baseline
runner. It does not yet contain a real model run, a trained model, a measured
edge deployment, or a published Hugging Face artifact. Results will be added
only after reproducible runs.
