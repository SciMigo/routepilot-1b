# The Contract Before the Model

## Source alignment

- Google Maps with Gemini, official help page, fetched 2026-09-21:
  https://support.google.com/built-in/answer/16537773?hl=en
- Google built-in vehicle data and privacy, official help page, fetched 2026-09-21:
  https://support.google.com/built-in/answer/9941814?hl=en
- Cerence CaLLM Edge product page, fetched 2026-09-21:
  https://www.cerence.com/products/callm-gen-ai-apps
- Qualia product page, fetched 2026-09-21:
  https://quadrillion.ai/qualia
- Qwen2.5-1.5B-Instruct model card and Apache 2.0 license, fetched 2026-09-21:
  https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct

## Core concepts

- A route assistant operates across two kinds of knowledge. Stable behavior—how
  to parse “under ten minutes,” choose a tool, compare candidates, and explain a
  decision—can be post-trained. Dynamic facts—traffic, opening hours, charger
  availability, and POIs—must come from tools at request time.
- The model contract ends at a structured tool call and a proposed choice. It
  does not directly control the vehicle or silently change navigation.
- Hard constraints determine feasibility. Soft preferences only rank candidates
  that remain feasible. A high rating cannot compensate for a closed restaurant
  or incompatible charger.
- The benchmark oracle is deterministic code, not another language model. Every
  expected tool call, feasibility decision, and ranking can be audited by hand.
- Evaluation is decomposed: parse/schema validity, tool choice, constraint
  extraction, hard-constraint violations, clarification behavior, and selection.
- The first student candidate is Qwen2.5-1.5B-Instruct because its size and
  Apache-2.0 license make it a plausible starting point. Model selection remains
  an experiment, not a conclusion.
- Qualia advertises post-training and autonomous experiment workflows. A later
  module may evaluate it as an orchestrator; Module 1 does not assume a native
  distillation feature, a Hugging Face connector, or any achieved result.

## Claims and evidence

- **Documented:** Google's built-in Maps help gives a route-aware restaurant
  example with a maximum detour. This establishes that the interaction pattern
  is a real product behavior, not evidence that RoutePilot matches Google's
  implementation or quality.
- **Documented:** Cerence describes an embedded small language model for core
  in-car functionality and limited-connectivity operation. This supports the
  relevance of an edge-sized student, not a performance claim for our model.
- **Documented:** Qwen publishes a 1.5B instruct checkpoint under Apache 2.0.
- **Documented:** Qualia describes autonomous experiments, post-training, and
  failure diagnosis. We make no claim beyond the advertised capability.
- **Proposed:** 1.5B is sufficient for the contract defined here. The course will
  test this against baselines.
- **Proposed:** 50,000–200,000 licensed synthetic scenarios may be enough for the
  first SFT pass. The volume will be chosen after learning-curve experiments.
- **Not yet observed:** model accuracy, edge latency, memory, power, and the
  benefit of any Qualia-driven iteration.

## Programming and lab

1. Run the reference predictions and explain why every metric is 1.0 except
   hard-violation rate, which is 0.0.
2. Change a choice to an infeasible candidate. Observe that selection accuracy
   and hard-violation rate move independently of tool-call accuracy.
3. Remove one tool argument. Observe constraint recall fall without inventing a
   model-quality story.
4. Add an underspecified scenario that requires clarification and defend which
   missing fact makes action unsafe or useless.
