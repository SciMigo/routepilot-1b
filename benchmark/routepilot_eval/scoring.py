"""Component metrics for RoutePilot predictions.

Three scoring rules govern this module. A reader should be able to state them
without reading the code, because the lab asks students to reason about the
numbers it produces.

1. Silence is never credited. A prediction that is absent from the prediction
   file, or that fails the schema check, scores as incorrect on schema
   validity, tool accuracy, constraint precision and recall, clarification
   accuracy, and selection accuracy. Declining to answer is a legitimate
   product behavior, but it is not the same as answering correctly, and the
   benchmark must not report it as such.

2. Safety is judged on whatever the prediction named. A hard violation is
   charged against any candidate id the prediction carries, in every scenario
   -- including one whose correct action was to ask a clarifying question --
   and regardless of whether the surrounding payload passed the schema check.
   An unsafe suggestion is unsafe however it was packaged.

3. Every rate is denominated by a count the model cannot influence: the number
   of scenarios, or the number of scenarios for which the oracle has a feasible
   answer. No metric improves because a model produced less output.
   ``selection_coverage`` reports how often the model actually committed to a
   choice, so an abstaining model is visible rather than merely blameless.
"""

from __future__ import annotations

from typing import Any

from .errors import FixtureError
from .oracle import candidate_is_feasible, expected_choice


def _valid_prediction(prediction: dict[str, Any]) -> bool:
    if not isinstance(prediction.get("scenario_id"), str):
        return False
    if prediction.get("choice_id") is not None and not isinstance(prediction["choice_id"], str):
        return False
    if prediction.get("clarification") is not None and not isinstance(
        prediction["clarification"], str
    ):
        return False
    call = prediction.get("tool_call")
    if call is not None and not (
        isinstance(call, dict)
        and isinstance(call.get("name"), str)
        and isinstance(call.get("arguments"), dict)
    ):
        return False
    return True


def _canonical(value: Any) -> tuple[Any, ...]:
    """A hashable, comparison-stable form of a JSON value.

    Two arguments express the same constraint when they differ only in how
    JSON spelled them: `10` against `10.0`, or a filter list in a different
    order. Comparing `repr()` scored those as extraction defects, which is
    exactly the signal the module says should drive the next data pass.
    """
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, (int, float)):
        number = float(value)
        return ("number", int(number) if number.is_integer() else number)
    if isinstance(value, str):
        return ("string", value)
    if value is None:
        return ("null",)
    if isinstance(value, list):
        # List-valued arguments in this contract are filter sets -- cuisines,
        # connectors -- so order carries no meaning. Repetition still does.
        return ("list", tuple(sorted((_canonical(item) for item in value), key=repr)))
    if isinstance(value, dict):
        return ("object", tuple(sorted((key, _canonical(item)) for key, item in value.items())))
    return ("other", repr(value))


def _argument_pairs(call: dict[str, Any] | None) -> set[tuple[str, tuple[Any, ...]]]:
    if not call:
        return set()
    arguments = call.get("arguments", {})
    if not isinstance(arguments, dict):
        raise FixtureError(
            f"tool call {call.get('name')!r}: 'arguments' must be an object, "
            f"got {arguments!r}"
        )
    return {(key, _canonical(value)) for key, value in arguments.items()}


def _tool_matches(
    expected_call: dict[str, Any] | None, predicted_call: dict[str, Any] | None
) -> bool:
    if expected_call is None:
        return predicted_call is None
    if predicted_call is None:
        return False
    return predicted_call.get("name") == expected_call.get("name")


def reconcile(
    scenarios: list[dict[str, Any]], predictions: list[dict[str, Any]]
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Match predictions to scenarios and report every line that did not match.

    A prediction file can disagree with a scenario file in three ways that all
    used to pass unnoticed: a scenario with no prediction, two predictions for
    one scenario, and a prediction whose ``scenario_id`` names nothing. Each is
    reported rather than silently resolved, because each one means the reported
    metrics describe a different set of scenarios than the caller believes.
    """
    scenario_ids = [scenario.get("id") for scenario in scenarios]
    known = {scenario_id for scenario_id in scenario_ids if isinstance(scenario_id, str)}

    matched: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    unknown: list[Any] = []
    for prediction in predictions:
        scenario_id = prediction.get("scenario_id")
        if not isinstance(scenario_id, str) or scenario_id not in known:
            unknown.append(scenario_id)
            continue
        if scenario_id in matched:
            # First line wins so the result stays deterministic; the collision
            # is reported instead of quietly changing the score.
            duplicates.append(scenario_id)
            continue
        matched[scenario_id] = prediction

    missing = [
        scenario_id
        for scenario_id in scenario_ids
        if isinstance(scenario_id, str) and scenario_id not in matched
    ]
    report = {
        "scenario_count": len(scenarios),
        "prediction_count": len(predictions),
        "matched": len(matched),
        "missing_predictions": missing,
        "duplicate_prediction_ids": duplicates,
        "unknown_prediction_ids": unknown,
    }
    report["clean"] = not (missing or duplicates or unknown)
    return matched, report


def evaluate(
    scenarios: list[dict[str, Any]], predictions: list[dict[str, Any]]
) -> dict[str, Any]:
    by_id, reconciliation = reconcile(scenarios, predictions)
    totals = {
        "present": 0,
        "schema_valid": 0,
        "tool_correct": 0,
        "clarification_correct": 0,
        "true_arguments": 0,
        "predicted_arguments": 0,
        "matched_arguments": 0,
        "selection_correct": 0,
        "selectable_scenarios": 0,
        "selections_made": 0,
        "hard_violations": 0,
    }
    details: list[dict[str, Any]] = []

    for index, scenario in enumerate(scenarios):
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str):
            raise FixtureError(
                f"scenario[{index}]: 'id' must be a string, got {scenario_id!r}; "
                f"run validate_scenarios() for the full report"
            )
        prediction = by_id.get(scenario_id)
        present = prediction is not None
        valid = present and _valid_prediction(prediction)
        totals["present"] += int(present)
        totals["schema_valid"] += int(valid)

        # Rule 1: only a present, schema-valid payload earns behavior credit.
        payload = prediction if valid else {}

        expected_call = scenario.get("expected_call")
        predicted_call = payload.get("tool_call")
        tool_correct = valid and _tool_matches(expected_call, predicted_call)
        totals["tool_correct"] += int(tool_correct)

        true_arguments = _argument_pairs(expected_call)
        predicted_arguments = _argument_pairs(predicted_call)
        totals["true_arguments"] += len(true_arguments)
        totals["predicted_arguments"] += len(predicted_arguments)
        if tool_correct:
            # Arguments only preserve a constraint if they reached the tool
            # that consumes them; handing them to another tool extracts nothing.
            totals["matched_arguments"] += len(true_arguments & predicted_arguments)

        expected_clarification = bool(scenario.get("expected_clarification"))
        predicted_clarification = bool(payload.get("clarification"))
        clarification_correct = valid and expected_clarification == predicted_clarification
        totals["clarification_correct"] += int(clarification_correct)

        oracle_choice = expected_choice(scenario)

        # Rule 2: read the named choice off the raw prediction, not the payload,
        # so a schema failure cannot hide an unsafe suggestion.
        chosen_id = prediction.get("choice_id") if present else None
        if not isinstance(chosen_id, str):
            chosen_id = None

        selection_correct = valid and chosen_id == oracle_choice
        totals["selection_correct"] += int(selection_correct)
        if oracle_choice is not None:
            totals["selectable_scenarios"] += 1
            totals["selections_made"] += int(chosen_id is not None)

        hard_violation = False
        if chosen_id is not None:
            candidate = next(
                (
                    item
                    for item in scenario.get("candidates", [])
                    if item.get("id") == chosen_id
                ),
                None,
            )
            hard_violation = candidate is None or not candidate_is_feasible(candidate, scenario)
        totals["hard_violations"] += int(hard_violation)

        details.append(
            {
                "scenario_id": scenario_id,
                "prediction_present": present,
                "schema_valid": valid,
                "tool_correct": tool_correct,
                "clarification_correct": clarification_correct,
                "chosen_id": chosen_id,
                "selection_correct": selection_correct,
                "hard_violation": hard_violation,
            }
        )

    count = len(scenarios)
    matched_arguments = totals["matched_arguments"]
    predicted_arguments = totals["predicted_arguments"]
    true_arguments = totals["true_arguments"]
    selectable = totals["selectable_scenarios"]

    # Rule 3: `count` and `selectable` come from the scenario file, so no
    # denominator here moves when a model emits less.
    metrics = {
        "schema_valid_rate": totals["schema_valid"] / count if count else 0.0,
        "tool_accuracy": totals["tool_correct"] / count if count else 0.0,
        "constraint_precision": (
            matched_arguments / predicted_arguments
            if predicted_arguments
            else (1.0 if not true_arguments else 0.0)
        ),
        "constraint_recall": (
            matched_arguments / true_arguments if true_arguments else 1.0
        ),
        "clarification_accuracy": totals["clarification_correct"] / count if count else 0.0,
        "selection_accuracy": totals["selection_correct"] / count if count else 0.0,
        "selection_coverage": (
            totals["selections_made"] / selectable if selectable else 1.0
        ),
        "hard_violation_rate": totals["hard_violations"] / count if count else 0.0,
    }
    return {
        "scenario_count": count,
        "metrics": metrics,
        "counts": totals,
        "reconciliation": reconciliation,
        "details": details,
    }
