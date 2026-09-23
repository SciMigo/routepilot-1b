# Generate Scenarios, Not Answers — Slide Outline

## Slide 1: A fluent answer can still be a bad label
- A teacher can write plausible tool calls that violate the declared policy.
- More generated prose scales mistakes as efficiently as correct examples.
- Build the world first; derive the answer with code.

## Slide 2: The scenario factory
```text
seed + template family + policy ranges
                |
                v
 context -> candidates -> hard constraints -> utility
                |                              |
                +---------- oracle ------------+
                              |
                       expected choice
```
- Natural-language rendering is downstream of structured truth.

## Slide 3: Four layers, four owners
- Context: vehicle and route facts already known to the application.
- Candidates: current facts a tool could return.
- Policy: explicit product decisions, never disguised as user language.
- Wording: a representation of constraints, not their source of truth.

## Slide 4: Derive, do not type, the label
```python
scenario["expected_choice_id"] = expected_choice(scenario)
```
- The generator cannot disagree silently with the evaluator.
- A changed candidate may change the label; regeneration records that fact.

## Slide 5: Construct informative candidates
- Feasible and preferred: the intended best option.
- Feasible but weaker: proves ranking matters.
- Attractive but infeasible: proves hard constraints dominate.
- Just across a boundary: exposes `<=` versus `<` mistakes.

## Slide 6: A seed is necessary, not sufficient
- Same code + version + seed gives the same release.
- A seed says nothing about realism, coverage, or bias.
- Record generator version and seed on every scenario.

## Slide 7: The random-split trap
```text
food-template -> row A -> train
              -> row B -> development   # leakage
```
- Shared wording and candidate roles make siblings unusually easy.
- Assign the whole family before generating rows.

## Slide 8: RoutePilot's family split
- Train: explicit cuisine and explicit connector families.
- Development: arrival-deadline and context-connector families.
- The domains overlap; the construction pattern does not.

## Slide 9: Where a teacher model helps
- Paraphrase a canonical request; propose surface-form diversity.
- Do not invent expected calls, live facts, or oracle choices.
- Reject text that drops, changes, or adds a hard constraint.

## Slide 10: Filtering is part of generation
- Schema validation and oracle agreement.
- Constraint-value preservation and duplicate detection.
- Rights, privacy, and location-data review before retention.

## Slide 11: Coverage before volume
- Domain: food, charging, parking, arrival-sensitive errands.
- Behavior: action, clarification, no feasible result.
- Boundary: equality, just-inside, just-outside, conflicting preferences.
- Source: request, context, and product policy.

## Slide 12: What the first generator does not prove
- Eight rows demonstrate reproducibility, not model readiness.
- Synthetic candidates are not live POIs or charger availability.
- Four families are a scaffold for coverage analysis.

## Slide 13: Lab — reproduce before extending
- Regenerate `module-02.jsonl` from seed `20260923`.
- Validate the fixture and inspect family isolation.
- Add one family without editing a label by hand.

## Slide 14: Next module
- Freeze the prompt and inference settings.
- Measure the base model and teacher on the same scenarios.
- Train only after a repeatable failure cluster survives prompting.
