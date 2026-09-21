"""Auditable feasibility and ranking oracle."""

from __future__ import annotations

from typing import Any


def _check(actual: Any, operator: str, expected: Any) -> bool:
    if operator == "eq":
        return actual == expected
    if operator == "lte":
        return actual is not None and actual <= expected
    if operator == "gte":
        return actual is not None and actual >= expected
    if operator == "contains_any":
        return isinstance(actual, list) and any(item in actual for item in expected)
    raise ValueError(f"unsupported hard-constraint operator: {operator}")


def candidate_is_feasible(candidate: dict[str, Any], scenario: dict[str, Any]) -> bool:
    return all(
        _check(candidate.get(rule["field"]), rule["op"], rule["value"])
        for rule in scenario.get("hard_constraints", [])
    )


def utility(candidate: dict[str, Any], scenario: dict[str, Any]) -> float:
    return sum(
        float(candidate.get(field, 0)) * float(weight)
        for field, weight in scenario.get("utility_weights", {}).items()
    )


def rank_candidates(scenario: dict[str, Any]) -> list[tuple[str, float]]:
    ranked = [
        (candidate["id"], utility(candidate, scenario))
        for candidate in scenario.get("candidates", [])
        if candidate_is_feasible(candidate, scenario)
    ]
    return sorted(ranked, key=lambda item: (-item[1], item[0]))


def expected_choice(scenario: dict[str, Any]) -> str | None:
    ranked = rank_candidates(scenario)
    return ranked[0][0] if ranked else None
