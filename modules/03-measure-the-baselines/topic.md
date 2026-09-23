# Measure the Baselines

## Source alignment

- Holistic Evaluation of Language Models (HELM), fetched 2026-09-23:
  https://arxiv.org/abs/2211.09110
- OpenAI Evals repository, fetched 2026-09-23:
  https://github.com/openai/evals
- MLX-LM HTTP server documentation, fetched 2026-09-23:
  https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/SERVER.md
- Qwen2.5-1.5B-Instruct model card, fetched 2026-09-23:
  https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct
- MLX conversion of Qwen2.5-1.5B-Instruct, fetched 2026-09-23:
  https://huggingface.co/mlx-community/Qwen2.5-1.5B-Instruct-4bit

## Core concepts

- A baseline measures a complete setup: model revision, quantization, prompt,
  visible scenario fields, parser, sampling settings, endpoint, and evaluator.
- The model sees the driver request, permitted context, and simulated tool
  candidates. It never sees expected calls, constraints, utility weights, or
  oracle choices.
- Freeze one prompt version and run it unchanged against the base and teacher.
- Preserve every raw request and response. A malformed first response is a
  schema failure, not an invitation to retry until valid.
- Use temperature zero for the first comparison, while recording that
  deterministic sampling does not guarantee identical outputs across providers.
- Record provider errors, parse errors, usage, latency, model identifier, and
  unknown cost separately from behavioral metrics.
- Compare component failures, not only aggregate selection accuracy. A teacher
  that selects well but violates the output contract is not a clean target.
- Train only when a repeatable failure cluster remains after a reasonable frozen
  prompt and the expected improvement matters to the product.

## Claims and evidence

- **Documented:** HELM releases raw prompts and completions to improve evaluation
  transparency. RoutePilot likewise treats raw model traffic as run evidence.
- **Documented:** OpenAI Evals describes evaluations as a way to test behavior
  across model versions. RoutePilot uses its own deterministic grader rather
  than adopting an external framework.
- **Documented:** MLX-LM exposes a local chat-completions-style HTTP server and
  explicitly says that server is not recommended for production. This course
  uses it only as a local experiment endpoint.
- **Documented:** Qwen publishes the 1.5B instruct checkpoint under Apache 2.0;
  the named MLX community conversion provides a four-bit local artifact.
- **Observed in this repository:** tests prove that benchmark truth is absent
  from prompts, strict JSON parsing rejects fenced or extra-key responses, and
  failed parsing remains present and receives schema failure credit.
- **Not yet observed:** actual Qwen or teacher scores, latency, token usage, or
  cost. No baseline run is claimed until a raw run directory is committed.

## Programming and lab

1. Inspect the frozen prompt and prove benchmark-only fields are absent.
2. Run the four-bit Qwen candidate through a local MLX endpoint.
3. Diagnose first-response parsing and behavior failures without repair.
4. Run one named teacher through the same chat-completions contract.
5. Compare component metrics and write a go/no-go memo for post-training.
