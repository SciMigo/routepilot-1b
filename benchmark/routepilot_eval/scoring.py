"""Component metrics for RoutePilot predictions."""

from __future__ import annotations

from typing import Any

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


def _argument_pairs(call: dict[str, Any] | None) -> set[tuple[str, str]]:
    if not call:
        return set()
    return {(key, repr(value)) for key, value in call.get("arguments", {}).items()}


def evaluate(
    scenarios: list[dict[str, Any]], predictions: list[dict[str, Any]]
) -> dict[str, Any]:
    by_id = {prediction.get("scenario_id"): prediction for prediction in predictions}
    totals = {
        "schema_valid": 0,
        "tool_correct": 0,
        "clarification_correct": 0,
        "true_arguments": 0,
        "predicted_arguments": 0,
        "matched_arguments": 0,
        "selection_correct": 0,
        "action_scenarios": 0,
        "hard_violations": 0,
        "chosen_candidates": 0,
    }
    details: list[dict[str, Any]] = []

    for scenario in scenarios:
        prediction = by_id.get(scenario["id"], {})
        valid = _valid_prediction(prediction)
        totals["schema_valid"] += int(valid)

        expected_call = scenario.get("expected_call")
        predicted_call = prediction.get("tool_call") if valid else None
        tool_correct = (
            expected_call is None
            and predicted_call is None
            or expected_call is not None
            and predicted_call is not None
            and predicted_call.get("name") == expected_call.get("name")
        )
        totals["tool_correct"] += int(tool_correct)

        true_arguments = _argument_pairs(expected_call)
        predicted_arguments = _argument_pairs(predicted_call)
        totals["true_arguments"] += len(true_arguments)
        totals["predicted_arguments"] += len(predicted_arguments)
        totals["matched_arguments"] += len(true_arguments & predicted_arguments)

        expected_clarification = bool(scenario.get("expected_clarification"))
        predicted_clarification = bool(prediction.get("clarification")) if valid else False
        clarification_correct = expected_clarification == predicted_clarification
        totals["clarification_correct"] += int(clarification_correct)

        oracle_choice = expected_choice(scenario)
        declared_choice = scenario.get("expected_choice_id")
        if oracle_choice != declared_choice:
            raise ValueError(
                f"scenario {scenario['id']}: declared choice {declared_choice!r} "
                f"does not match oracle {oracle_choice!r}"
            )

        selection_correct: bool | None = None
        hard_violation = False
        if not expected_clarification:
            totals["action_scenarios"] += 1
            selection_correct = prediction.get("choice_id") == oracle_choice
            totals["selection_correct"] += int(selection_correct)

            chosen_id = prediction.get("choice_id")
            if chosen_id is not None:
                totals["chosen_candidates"] += 1
                candidate = next(
                    (item for item in scenario.get("candidates", []) if item["id"] == chosen_id),
                    None,
                )
                hard_violation = candidate is None or not candidate_is_feasible(candidate, scenario)
                totals["hard_violations"] += int(hard_violation)

        details.append(
            {
                "scenario_id": scenario["id"],
                "schema_valid": valid,
                "tool_correct": tool_correct,
                "clarification_correct": clarification_correct,
                "selection_correct": selection_correct,
                "hard_violation": hard_violation,
            }
        )

    count = len(scenarios)
    matched = totals["matched_arguments"]
    predicted = totals["predicted_arguments"]
    true = totals["true_arguments"]
    chosen = totals["chosen_candidates"]
    action_count = totals["action_scenarios"]
    metrics = {
        "schema_valid_rate": totals["schema_valid"] / count if count else 0.0,
        "tool_accuracy": totals["tool_correct"] / count if count else 0.0,
        "constraint_precision": matched / predicted if predicted else (1.0 if not true else 0.0),
        "constraint_recall": matched / true if true else 1.0,
        "clarification_accuracy": totals["clarification_correct"] / count if count else 0.0,
        "selection_accuracy": totals["selection_correct"] / action_count if action_count else 1.0,
        "hard_violation_rate": totals["hard_violations"] / chosen if chosen else 0.0,
    }
    return {"scenario_count": count, "metrics": metrics, "details": details}
