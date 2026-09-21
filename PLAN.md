# Course plan

The course follows one artifact from behavioral contract to edge deployment.
Each module must leave behind something executable or inspectable.

1. **The Contract Before the Model** — define the tool schema, scenario format,
   deterministic oracle, component metrics, and safety boundary.
2. **Generate Scenarios, Not Answers** — construct diverse contexts and derive
   labels from explicit constraints and a deterministic utility function.
3. **Measure Teacher and Base-Model Baselines** — establish comparable prompting,
   parsing, cost, and error reports before training.
4. **Post-Train the Student** — build a licensed SFT/LoRA dataset, train the
   selected 1B-class model, and record reproducible runs.
5. **Turn Failures into Hard Negatives** — use failure clusters to generate
   targeted cases, retrain, and guard against regression. Qualia is evaluated
   here as an orchestration option; its use is not assumed.
6. **Quantize and Test at the Edge** — measure quality, latency, memory, and
   power on named hardware with a fixed protocol.
7. **Publish the Artifact** — ship model card, data card, benchmark, licenses,
   limitations, and integration contract.

The benchmark grows across modules, but Module 1 fixtures remain immutable
except for corrections documented in the changelog.
