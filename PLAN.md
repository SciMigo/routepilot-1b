# Course plan

The course follows one artifact from behavioral contract to edge deployment.
Each module must leave behind something executable or inspectable.

1. **The Contract Before the Model** *(free)* — define the tool schema, scenario format,
   deterministic oracle, component metrics, and safety boundary.
2. **Generate Scenarios, Not Answers** *(free)* — construct diverse contexts and derive
   labels from explicit constraints and a deterministic utility function.
3. **Measure Teacher and Base-Model Baselines** *(free)* — establish comparable prompting,
   parsing, cost, and error reports before training.
4. **Build the Training Set** *(paid)* — construct the licensed SFT dataset,
   renderer, loss masks, contamination checks, and data card.
5. **Post-Train the Student** *(paid)* — train the selected 1B-class model with
   a local MLX or hosted-provider track and record a reproducible controlled run.
6. **Turn Failures into Hard Negatives** *(paid)* — use failure clusters to
   generate targeted cases, retrain, and guard against regression.
7. **Try Verifier-Guided Improvement** *(paid)* — derive preferences or rewards
   from the oracle and compare a supported post-training method against the SFT
   result without assuming the more complex method wins.
8. **Run Bounded Autonomous Experiments** *(paid)* — evaluate Qualia or a
   provider-neutral orchestrator over a fixed search space, budget, and immutable
   evaluator. Include one optional structural-pruning branch that selects whole
   Transformer blocks by a recorded importance rule. Orchestration remains
   distinct from the training backend.
9. **Prune, Recover, Quantize, and Test at the Edge** *(paid)* — compare the
   post-trained model with a structurally pruned model before and after recovery
   training or distillation, then quantize and measure quality, latency, memory,
   artifact size, and power on named hardware with a fixed protocol.
10. **Defend and Publish the Artifact** *(paid)* — integrate mock live tools and
    the application policy boundary, pass a private holdout, then ship the model
    card, data card, benchmark, licenses, limitations, and integration contract.

The benchmark grows across modules, but Module 1 fixtures remain immutable
except for corrections documented in `benchmark/CHANGELOG.md`, which also
records what counts as a correction rather than a new benchmark version.
Compression experiments must preserve an unpruned checkpoint so pruning loss
and recovery gain can be measured independently.

See [LABS.md](LABS.md) for executable outcomes, service boundaries, and the
proposed local, hosted, and autonomous-experiment tracks.
See [OFFERING.md](OFFERING.md) for the proposed free/paid boundary and the
separation between durable course access and finite managed compute.
