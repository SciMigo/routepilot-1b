# RoutePilot free and paid offering

Status: **proposed product design**. Prices, provider partnerships, included
compute, certificates, and service levels are not configured promises.

## What is free

The free path should be useful on its own and prove that the course is rigorous:

1. **The Contract Before the Model** — tool schema, safety boundary,
   deterministic oracle, and component metrics.
2. **Generate Scenarios, Not Answers** — typed scenario generation, policy
   provenance, deterministic labels, and leakage-resistant splits.
3. **Measure the Baselines** — run the public fixture through supplied base and
   teacher predictions, inspect failures, and decide whether training is
   justified. Learners can connect their own inference provider, but no paid
   provider is required to complete the public exercise.

Free learners leave with a working benchmark and a defensible product contract,
not a teaser whose only lesson is to buy the rest. The public repository or
public course artifacts may contain these modules and a small benchmark fixture.

## What the durable course purchase unlocks

The paid boundary begins when the learner builds and improves the model:

4. **Build the Training Set** — licensed example construction, chat rendering,
   loss masks, contamination checks, data card, and a reproducible dataset
   release.
5. **Post-Train the Student** — one controlled LoRA/QLoRA run with a local or
   hosted backend, checkpoint comparison, and run provenance.
6. **Engineer Hard Negatives** — cluster failures, create targeted examples,
   retrain, and prove that a local improvement did not regress protected
   behavior.
7. **Try Verifier-Guided Improvement** — turn the deterministic oracle into
   preference pairs or a reward signal; compare rejection sampling, preference
   optimization, or reinforcement fine-tuning only where the selected backend
   supports it. The lesson is the controlled comparison, not a promise that a
   more complex method wins.
8. **Run Bounded Autonomous Experiments** — use Qualia or a provider-neutral
   orchestration loop to propose and execute experiments within an explicit
   budget, mutable search space, and immutable evaluator, including an optional
   whole-block structural-pruning branch.
9. **Prune, Recover, Quantize, and Deploy the Edge Candidate** — measure the
   loss from structural pruning, the gain from recovery training or
   distillation, and the additional effect of quantization on named hardware;
   then integrate the selected model behind mock maps/POI tools plus an
   application policy and confirmation layer.
10. **Defend and Publish the Artifact** — submit to a private holdout, reproduce
    a clean run, and ship a model card, data card, benchmark report, license
    inventory, and known-failure analysis.

The course purchase is durable access to private lessons, lab capsules, starter
code, instructor run artifacts, reference adapters, expanded development cases,
private evaluator submissions, and future corrections to that course version.
It should not be represented as unlimited compute.

## The paid service layer

There are two distinct things to sell. They must remain separate in billing and
in learner-facing language.

### 1. Durable course entitlement

This is the one-time course or track purchase. It grants the protected material
listed above. It can be completed with Apple Silicon and learner-owned API keys,
so purchasing the course does not force another infrastructure purchase.

The high-value SciMigo-operated service is the **private evaluation path**:

- receive a learner's prediction file and run manifest;
- score it against hidden scenario families server-side;
- return component metrics and failure categories without returning hidden
  prompts, labels, or tests;
- preserve attempt history so the learner can compare base, trained, iterated,
  and quantized candidates;
- issue a completion result only after provenance and safety checks pass.

This is more defensible than charging merely for Markdown: the learner receives
an independent assessment they cannot reproduce by reading the answer files.

### 2. Finite managed-compute pack

This optional consumable covers a declared number or budget of hosted inference,
training, and autonomous experiment runs. It may be backed by Qualia Cloud,
Tinker, Fireworks, or another reviewed provider. The UI must state what is
included, what consumes a credit, maximum runtime or spend, retention, and what
happens when a run fails.

Suggested pack units are outcomes rather than raw GPU-hours:

- one baseline inference sweep;
- one controlled LoRA training run plus checkpoint export;
- one bounded experiment campaign of at most a stated number of trials;
- one final quantized-candidate evaluation.

Do not promise this pack until a real provider run establishes cost and failure
behavior. Learners may always choose the BYOK/local path instead.

## Why the expanded scope is worth paying for

The paid course produces a portfolio-grade system rather than a single notebook:

```text
licensed scenario/data factory
        -> baseline and failure report
        -> reproducible adapter
        -> hard-negative and verifier-guided comparison
        -> bounded autonomous experiment ledger
        -> pruned, recovered, and quantized edge candidate
        -> tool + policy integration demo
        -> independently scored publication package
```

The learner finishes with inspectable artifacts: dataset and model cards, run
directories, an adapter or checkpoint reference, a quantized package, an eval
report, and a safe integration contract. Each artifact corresponds to work that
teams actually need when moving from an LLM demo to a controlled model release.

## Content and access boundary

Public artifacts may advertise paid module titles, outcomes, prerequisites, and
sample metrics. They must not contain protected URLs, private object keys,
instructor adapters, expanded fixtures, hidden test cases, solutions, or full
transcripts.

Paid course artifacts live in private object storage and are returned only after
authentication and entitlement checks. Managed-compute credentials remain with
the backend or the learner's provider; they never appear in course manifests or
browser-visible configuration. Anything delivered to an authorized learner can
be saved by that learner, so this is access control rather than DRM.

## Evidence required before launch

Before setting a price or promising included compute, commit:

1. one complete local MLX run on named hardware;
2. one complete hosted-provider run with raw cost and failure records;
3. one bounded Qualia or provider-neutral orchestration campaign;
4. an anonymous-access test proving that protected R2 objects cannot be fetched;
5. entitlement, refund, and compute-credit behavior tested independently;
6. a private holdout service that cannot leak cases through error messages,
   caching, or repeated unlimited submissions.
