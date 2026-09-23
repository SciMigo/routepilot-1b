# RoutePilot lab design

Status: **proposed**. Only Lab 1 is implemented. Commands, provider support,
cost, model quality, training time, and hardware results in later labs remain to
be measured and committed before publication.

## Design boundary

The course teaches the post-training loop, not one vendor's interface. Every
student should be able to complete the core path without provisioning a CUDA
machine:

- deterministic data generation and evaluation run in the SciMigo lab or
  ordinary Python;
- teacher and hosted-model calls use the learner's own API account;
- the first student adapter uses QLoRA on Apple Silicon through MLX-LM when
  compatible hardware is available, or a hosted training API otherwise;
- provider-specific work is isolated behind a run contract, so the resulting
  predictions and evidence are scored by the same local evaluator.

Qualia, Tinker, Fireworks, MLX-LM, or any successor is a replaceable execution
surface. None owns the benchmark, labels, data card, or pass criteria.

## Common run contract

Every baseline or training run must export a directory with:

```text
runs/<run-id>/
  run.json                 # provider, model revision, recipe, seed, timestamps
  environment.json         # packages and named hardware or hosted service
  predictions.jsonl        # one result for every evaluation scenario
  metrics.json             # output from the committed evaluator
  stdout.log               # unedited command or service log
  costs.json               # tokens, provider charges, or "not recorded"
  artifacts.json           # adapter/checkpoint identifiers and checksums
```

`run.json` must identify whether the run used local MLX, Qualia, Tinker,
Fireworks, or another service. A screenshot or vendor dashboard is supporting
evidence, not a substitute for these machine-readable files.

Training and orchestration tools may write under `runs/` and a disposable work
directory. They must not edit the evaluator, the frozen evaluation split, or
expected labels during an experiment. The final holdout is scored only after a
recipe has been selected.

## Lab sequence

### Lab 1 — Audit the behavioral contract

**Implemented:** `modules/01-the-contract-before-the-model/lab.md`.

Students run the deterministic reference, introduce one infeasible choice,
remove one extracted constraint, and add a clarification case. The output is a
validated scenario plus an explanation of which component metric moved.

No model or external service belongs in this lab. Automating it would hide the
contract the rest of the course depends on.

### Lab 2 — Generate scenarios, derive answers

Students build a typed scenario generator from explicit policy ranges. Code,
not a teacher model, applies hard constraints and derives the expected choice.
They then generate natural-language request variants without changing the
underlying structured scenario.

Required checks:

1. the same seed reproduces the same structured scenario;
2. every expected choice is recomputed by the oracle;
3. paraphrases preserve all hard constraints;
4. train, development, and hidden-test families are split by scenario template,
   not by randomly shuffling near-duplicates;
5. a data card records sources, licenses, teacher terms, filtering, and location
   data policy before any generated output is retained.

A teacher API may propose or paraphrase requests after the structured truth
exists. Qualia may inspect a generated batch for coverage, but it must not
author expected labels or see the hidden-test split.

### Lab 3 — Establish teacher and base-model baselines

Students implement one provider-neutral inference adapter that accepts a model
request and writes `predictions.jsonl`. They evaluate:

- a frozen prompt against the unmodified 1B-class base model; and
- one named teacher model, with exact model revision and sampling settings.

The lab compares schema validity, tool choice, constraint precision/recall,
clarification behavior, hard violations, selection coverage, and selection
accuracy. It also records parse failures and per-run cost rather than silently
retrying until output is valid.

This is an inference lab. Use local quantized inference, a serverless endpoint,
or an API; do not allocate a training service yet. The decision to train must be
supported by a failure cluster that prompting alone did not resolve.

### Lab 4 — Build the training set

Students convert the licensed training split into chat examples, inspect loss
masks, run contamination and near-duplicate checks, and publish a versioned data
card. The output must be reproducible without invoking a model provider.

This is the first paid lab because it introduces the protected production data
pipeline and expanded development cases. It does not consume managed training
compute.

### Lab 5 — Perform one controlled post-training run

Students execute one deliberately small LoRA or QLoRA run. They hold the
dataset, seed, rank, learning rate, number of steps, and checkpoint cadence
fixed, then compare base and adapted models with the Lab 3 runner and submit the
candidate to the private evaluator.

Execution tracks:

- **Local default on Apple Silicon:** MLX-LM QLoRA. This avoids provisioning a
  cloud GPU but still uses the Mac's integrated GPU and unified memory.
- **Hosted training API:** Tinker or Fireworks when the selected model is
  supported. The learner's CPU-side script owns data preparation, evaluation,
  and the run manifest; the provider performs training.
- **Instructor artifact:** evaluate a supplied adapter when neither local nor
  hosted training is available. This preserves the analytical exercise but is
  not represented as the learner having trained the model.

Qualia is intentionally not the primary path in this lab. A student should see
and understand one complete run before delegating experiment choice. Qualia may
execute the already-written notebook or script, but it may not choose the
objective, metric, or search space yet.

### Lab 6 — Engineer hard negatives

Students cluster Lab 5 errors, select one failure family, add targeted examples,
retrain, and prove the change did not regress protected behavior. They must
distinguish a data defect, prompt defect, evaluator defect, and genuine model
capacity limit before deciding to add data.

### Lab 7 — Try verifier-guided improvement

Students turn deterministic comparisons into preference pairs or a reward
signal. Depending on backend support, they compare rejection sampling, a
preference method, or reinforcement fine-tuning with the SFT-plus-hard-negative
candidate. A valid conclusion may be that the added complexity did not help.

The lab freezes the same train/development boundary and reports provider cost,
invalid-output rate, protected safety metrics, and selection quality. It does
not treat reward increase as sufficient evidence by itself.

### Lab 8 — Run bounded autonomous experiments

This is the first lab where **Qualia is a natural fit**. Students review the
evidence from Labs 5–7, choose an allowed experiment family, and compare a
manually chosen follow-up against an orchestrated search.

The Qualia workspace receives:

- the repository or a protected lab capsule;
- the development split, never the final holdout;
- the immutable evaluator command;
- an experiment budget expressed as maximum runs and provider spend;
- an allowlist of mutable hyperparameters and training-data slices;
- a stop rule and the common run contract.

Qualia may propose hypotheses, launch scripts/notebooks, call an attached local
trainer, or use Qualia Cloud. Quadrillion currently also describes using
standard training services such as Tinker or Fireworks; in that arrangement,
Qualia is the research orchestrator and the other service is the training
backend. Those are separate roles and must be recorded separately.

One permitted experiment family is structural pruning. Students rank complete
Transformer blocks with a documented importance rule, choose a bounded target
such as 15–25% depth reduction, and save the pruned checkpoint without recovery
training. Whole-block pruning is the required first implementation because it
can produce a regular dense architecture; attention-head or MLP-width pruning
is an optional extension whose parameter reduction must not be presented as a
latency gain until the target runtime demonstrates one.

The student must reject any experiment that changes expected labels, tunes on
the final holdout, omits a failed run, exceeds the budget, or improves aggregate
accuracy while worsening the protected hard-violation threshold. The deliverable
is an experiment ledger and a short decision memo, not merely the best adapter.

Qualia remains an optional track until a stable, documented automation interface
and a reproducible end-to-end run are committed. Its current desktop/cloud
workspace can be taught through a notebook or script workflow without claiming
a native RoutePilot connector.

### Lab 9 — Prune, recover, quantize, and measure on a named target

Students compare the selected unpruned checkpoint, the structurally pruned
checkpoint before recovery, and the same checkpoint after recovery training or
knowledge distillation. The recovery data remains inside the licensed training
boundary; the development and final holdout splits are never used as training
tokens. They then quantize the best eligible candidate and run the fixed
evaluation plus a deployment protocol on named hardware.

The report must separate pruning loss, recovery gain, and quantization loss. It
includes RoutePilot component metrics and hard violations alongside cold and
warm latency distributions, peak memory, artifact size, and—only where
measurement is available—power. A smaller parameter count is not accepted as a
latency claim without a measured improvement on the named runtime.

MLX or llama.cpp can provide the local inference path. Structural surgery and
recovery training may use a supported hosted or PyTorch backend; learners who
cannot run it may evaluate supplied pruned and recovered instructor artifacts.
A hosted inference service can be a comparison point, but it cannot establish
an in-vehicle edge claim. Qualia may orchestrate a bounded pruning or
quantization sweep, subject to the same run contract, but measurement must come
from the named target.

The deployment exercise also places the model behind mock maps/POI tools and an
application policy layer. The model may propose a route action; only the policy
and confirmation layer may approve it.

### Lab 10 — Defend and publish an auditable artifact

Students produce the model card, data card, benchmark version, adapter or model
checksums, license inventory, integration schema, known failures, and safety
boundary. A clean-room evaluator rerun must reproduce the published metrics.

No research agent is needed. Qualia may draft a write-up from recorded evidence,
but the student verifies every claim and publishes no metric lacking a raw run.

## Delivery through SciMigo

Students do not need Git access. Each lesson can publish a small lab capsule:

- free labs expose instructions, fixtures, and starter files through the public
  course artifact path;
- paid labs deliver the capsule only after authentication and entitlement
  checks, from private object storage;
- provider credentials stay in the learner's selected service or local runtime
  and are never placed in a course manifest;
- run directories are uploaded back to the lab for scoring as learner artifacts,
  rather than granting a service access to protected answer material;
- hidden evaluation cases remain server-side.

Any file delivered to an entitled browser can be saved by that learner. The
access design prevents unauthorized retrieval; it does not promise DRM.

The durable course entitlement and variable-cost compute are separate products.
Paid course access unlocks private labs, starter artifacts, expanded development
cases, instructor runs, and private holdout submissions. An optional finite
compute pack may fund named hosted training and orchestration runs. Local MLX or
learner-owned provider credentials remain a supported alternative.

## Provider roles and evidence

| Option | Appropriate role | Not delegated |
| --- | --- | --- |
| MLX-LM | Local LoRA/QLoRA and inference on Apple Silicon | Benchmark ownership and edge claims beyond the measured Mac |
| Tinker | Hosted LoRA training controlled by a CPU-side Python loop; exportable weights | Scenario truth, data rights, and experiment selection |
| Fireworks | Managed inference, fine-tuning, evaluation, or a training backend | RoutePilot's safety boundary and final acceptance decision |
| Quadrillion Qualia | Notebook/script execution, experiment orchestration, failure analysis, and bounded follow-ups | Labels, hidden holdout, unlimited search, or automatic publication |

Primary capability references, checked 2026-09-23:

- Quadrillion, [Qualia](https://quadrillion.ai/qualia)
- Thinking Machines Lab, [Tinker documentation](https://tinker-docs.thinkingmachines.ai/)
- Fireworks AI, [developer documentation](https://docs.fireworks.ai/)
- Apple MLX team, [MLX-LM LoRA/QLoRA guide](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md)
