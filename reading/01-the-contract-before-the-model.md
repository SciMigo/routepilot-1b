---
title: The Contract Before the Model
module: 01-the-contract-before-the-model
sources:
  - google-maps-gemini-cars
  - google-built-in-vehicle-data
  - cerence-callm-edge
  - qualia
  - qwen25-15b-instruct
---

# The Contract Before the Model

The tempting first step in a post-training project is to generate examples. It
is also the easiest way to produce a large dataset whose correctness nobody can
explain. RoutePilot begins one step earlier: define what the product is allowed
to know, what it must retrieve, and how each kind of mistake will be measured.

Consider a driver who says:

> Find a quick Asian stop on my route. Keep the detour under ten minutes; I
> still need to reach the airport on time.

This is a credible product interaction. Google's official help for Maps with
Gemini in cars includes conversational restaurant search constrained by a route
and a small detour. Cerence separately describes an embedded small language
model for core automotive functions, including operation when connectivity is
limited. These sources establish that route-aware conversation and edge-sized
models are commercially relevant. They do not tell us how those products are
implemented, and they do not prove that our student will work.

## Train the stable decision, retrieve the changing facts

The request mixes stable reasoning with volatile world state.

The stable part includes recognizing that “under ten minutes” is a maximum,
mapping “Asian” to a declared cuisine taxonomy, choosing a route-stop search,
and treating the airport arrival time as a hard deadline. These behaviors can
be represented in training examples and evaluated repeatedly.

The volatile part includes which restaurants exist, whether they are open, how
traffic affects the detour, how long a stop will take, and whether a charger is
available. Putting those facts into model weights would turn yesterday's
answer into today's hallucination. RoutePilot asks an external tool for them at
request time.

That gives the system a clean boundary:

1. The application supplies the utterance and the minimum permitted context.
2. The model emits a typed tool call or asks a necessary clarification.
3. A maps, POI, traffic, or charger service returns current candidates.
4. The model, or deterministic application code, rejects infeasible candidates
   and ranks the remainder.
5. The system explains a proposed action. Product policy and the driver decide
   whether to apply it.

The final point matters. A conversational model is not a vehicle controller.
It must not silently change navigation or actuate the car. Driver-distraction
rules, confirmation, location-data retention, and regional requirements live in
the integrating product and need their own review. Google's vehicle-data help
is useful here because it makes clear that in-car features may use vehicle and
sensor context; RoutePilot's benchmark uses synthetic context and does not
grant an application unlimited access to real vehicle data.

## Freeze the call before judging the answer

For the example request, the expected call can be made explicit:

```json
{
  "name": "search_route_stops",
  "arguments": {
    "category": "food",
    "cuisines": ["chinese", "japanese", "korean", "thai", "vietnamese"],
    "max_detour_minutes": 10,
    "max_service_minutes": 25
  }
}
```

This object is intentionally boring. Typed fields make omissions visible. An
exact tool name makes routing testable. The object contains constraints, not a
fabricated restaurant. A production schema may evolve, but each benchmark
version must freeze the contract it scores.

An invalid call and a bad ranking are different failures. If the model omits
the detour limit, the retrieval service may return unusable candidates even if
the model is excellent at comparing them. If the call is perfect but the model
chooses a closed restaurant, the failure is in feasibility reasoning. The
course reports these components separately so the next training pass targets
the actual defect.

## Hard constraints come before preferences

A ranking score is convenient, but it can hide a serious category error. A
five-star restaurant does not become acceptable by scoring enough points to
offset being closed. A 350 kW charger with the wrong connector is not “almost”
compatible. RoutePilot therefore evaluates candidates in two stages.

First, every hard constraint is applied as a Boolean rule. A candidate that
fails one is removed. The Module 1 fixture uses simple typed operations such as
equal, less-than-or-equal, greater-than-or-equal, and contains-any. Later
modules may add derived fields, but the derivation must remain inspectable.

Second, feasible candidates receive a utility score from declared weights:

```text
utility(candidate) = sum(candidate[signal] * weight[signal])
```

Positive weights reward a preference match or rating. Negative weights penalize
detour and service time. A stable candidate ID breaks exact ties. Because the
fixture includes both the facts and weights, a reviewer can reproduce the
expected ordering without asking another model to judge it.

This oracle is deliberately narrower than human taste. Its job is not to define
the one true restaurant choice. Its job is to test whether a model follows a
declared product policy consistently. If the policy is wrong, change the policy
and version the benchmark; do not quietly relabel whichever answer the newest
model prefers.

## Clarification is part of the contract

Some requests should not trigger a tool immediately. “Find a charger” is
underspecified when the vehicle connector is unavailable. Guessing can produce
a fluent list of unusable results. In such cases, the correct next action is to
ask for the missing compatibility fact.

The benchmark scores whether clarification was required, independently of the
exact wording. This prevents a common dataset bias in which every prompt is
forced to have an answer. A useful agent must know when the input is not yet
sufficient for a useful action.

## Measure components, not vibes

Module 1 reports six quantities:

- **schema validity** — the prediction has the required types and shape;
- **tool accuracy** — the selected tool matches the expected capability;
- **constraint precision and recall** — the arguments preserve required values
  without inventing extra ones;
- **clarification accuracy** — the model acts or asks at the right time;
- **hard-violation rate** — a chosen candidate violates at least one declared
  hard constraint;
- **selection accuracy** — the chosen candidate matches the deterministic
  oracle's highest-utility feasible result.

The hard-violation metric has the opposite direction: zero is best. A model may
have high selection accuracy on easy scenarios while still occasionally
breaking a hard constraint. That failure must remain visible.

## A candidate model, not a predetermined winner

The initial student candidate is Qwen2.5-1.5B-Instruct. Its published model card
describes a 1.5-billion-parameter instruction-tuned checkpoint, and its
repository includes an Apache 2.0 license. That makes it a practical candidate
for a reproducible course and an eventual edge experiment. It does not establish
that it can meet this contract after post-training.

Later modules will compare the base model, a teacher baseline, and post-trained
students. The “1B” in the course title means the 1B class rather than an exact
parameter count. If a different suitably licensed model produces a better
quality-and-resource tradeoff, the evidence should win.

Teacher outputs require their own rights check. Before any synthetic output is
used for training or weight publication, the repository must record the model,
terms, intended use, prompts, filters, and handling of location-like data. A
convenient API is not automatically permission to create and redistribute a
derived model.

## Where autonomous experimentation enters

Quadrillion advertises Qualia as an autonomous research system that can run
experiments, diagnose failures, and support post-training workflows. That makes
it relevant to the later loop: train a candidate, evaluate it, cluster failures,
generate targeted hard negatives, and run the next experiment.

For now, that is a proposed use. We do not claim that Qualia has a particular
one-click distillation feature, a native Hugging Face publishing connector, or
that it improves RoutePilot. Those become observed facts only after a pinned,
reproducible run. The deterministic benchmark built in this module is what
would let an autonomous researcher improve the system without grading its own
homework.

## The artifact you leave behind

At the end of this module, there is no trained model—and that is a feature. There
is a contract:

- dynamic facts stay behind tools;
- tool calls have a typed, versioned shape;
- hard constraints filter before soft utility ranks;
- clarification is a valid next action;
- evaluation exposes the layer that failed;
- model actions remain proposals behind application policy;
- claims are marked documented, observed, or proposed.

The next module can now generate scenarios whose labels follow code instead of
intuition. Training will have a target, failure analysis will have categories,
and a future weekly dashboard will have metrics worth plotting.
