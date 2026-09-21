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

## Current module

**Module 1 — The Contract Before the Model** freezes the behavior and evaluation
contract before synthetic data or training begins. It includes:

- the course topic and slide outline;
- a source-backed reading;
- a deterministic scenario format and oracle;
- a small, hand-auditable benchmark fixture;
- an evaluator with component metrics and tests.

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

See [PLAN.md](PLAN.md) for the planned course sequence and
[AUTHORING.md](AUTHORING.md) for evidence and publishing rules.

## Status

This repository contains course source and an early benchmark contract. It does
not yet contain a trained model, a measured edge deployment, or a published
Hugging Face artifact. Results will be added only after reproducible runs.
