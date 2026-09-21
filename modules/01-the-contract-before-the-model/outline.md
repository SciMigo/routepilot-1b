# The Contract Before the Model — Slide Outline

## Slide 1: One request, three different jobs
- “Find a quick Asian stop on my route, at most ten minutes out of the way.”
- Extract constraints, retrieve current facts, then rank feasible results.
- Which facts should a 1B-class model memorize? None of the live ones.

## Slide 2: The product behavior already exists
- Google's official Maps help documents conversational, route-aware restaurant search.
- Cerence markets an embedded automotive SLM for core functionality.
- These establish relevance, not equivalence or benchmark performance.

## Slide 3: Draw the knowledge boundary
```text
driver utterance + route context
        | stable reasoning
        v
constraint JSON -> maps/POI tool -> current candidates
                                      |
                                      v
                         feasibility -> ranking -> proposal
```
- Model: language, schema, comparison, explanation.
- Tool: POIs, opening hours, traffic, charger status.

## Slide 4: Freeze the tool call
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
- No prose hidden inside arguments; no invented live results.
- Parsing and tool choice are independently scoreable.

## Slide 5: Hard constraints are not weights
- Closed, too much detour, late arrival, wrong connector: disqualify.
- Rating, preference match, shorter stop: rank feasible candidates.
- A weighted sum must never buy its way out of a product invariant.

## Slide 6: The deterministic oracle
```python
feasible = [c for c in candidates if all(check(c, rule) for rule in hard)]
ranked = sorted(feasible, key=lambda c: (-utility(c), c["id"]))
```
- Explicit rules, explicit weights, stable tie-break.
- The expected answer is executable and reviewable.

## Slide 7: One number hides five failures
- Schema validity, tool accuracy, and constraint precision/recall.
- Hard-violation rate, clarification behavior, and selection accuracy.
- Report each component so the next data pass targets the defect.

## Slide 8: Clarification is an action
- “Find me somewhere to charge” is incomplete when the connector is unknown.
- Calling a tool with a guessed connector creates plausible but unusable output.
- Benchmark the decision to ask, not just the wording of the question.

## Slide 9: The vehicle boundary
- RoutePilot proposes; application policy decides what is allowed.
- A driver confirms consequential route changes.
- Privacy and retention for location context belong to the integration.

## Slide 10: Why a 1B-class student is a hypothesis
- Initial candidate: Qwen2.5-1.5B-Instruct, Apache 2.0.
- Small enough to investigate edge deployment; not proven sufficient.
- Teacher and base-model baselines come before declaring a win.

## Slide 11: Where autonomous post-training fits
- Generate scenarios from a typed grammar, not unbounded stories.
- Train, evaluate, cluster failures, create hard negatives, retrain.
- Qualia is one orchestration candidate, not an observed result.

## Slide 12: Lab — break one dimension at a time
- Select a closed candidate: hard-violation rate rises.
- Drop `max_detour_minutes`: extraction recall falls.
- Call the wrong tool: tool accuracy falls.

## Slide 13: Contract checklist
- Dynamic facts behind tools; typed call and prediction schemas.
- Hard constraints before utility; clarification cases included.
- Policy/confirmation outside the model; reproducible evidence labels.

## Slide 14: Next module
- Generate contexts and candidates first; derive labels with this oracle.
- Add a data-rights gate before asking any teacher model for outputs.
