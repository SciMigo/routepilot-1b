"""Auditable feasibility and ranking oracle."""

from __future__ import annotations

from typing import Any

from .errors import FixtureError

OPERATORS = ("eq", "lte", "gte", "contains_any")


def _is_number(value: Any) -> bool:
    # JSON booleans are Python ints; a boolean is never a quantity here.
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _same_kind(actual: Any, expected: Any) -> bool:
    """Whether two values are comparable for equality without coercion.

    Python treats ``1 == True`` as true, which would let a candidate reporting
    ``"open": 1`` satisfy an ``eq true`` constraint. In a fixture whose selling
    point is that a reviewer can audit it by hand, that coercion is invisible
    and changes which candidates are feasible.
    """
    if isinstance(actual, bool) or isinstance(expected, bool):
        return isinstance(actual, bool) and isinstance(expected, bool)
    if _is_number(actual) and _is_number(expected):
        return True
    return type(actual) is type(expected)


def _check(actual: Any, operator: str, expected: Any) -> bool:
    if operator == "eq":
        return _same_kind(actual, expected) and actual == expected
    if operator == "lte":
        return _is_number(actual) and _is_number(expected) and actual <= expected
    if operator == "gte":
        return _is_number(actual) and _is_number(expected) and actual >= expected
    if operator == "contains_any":
        return isinstance(actual, list) and any(item in actual for item in expected)
    raise FixtureError(f"unsupported hard-constraint operator: {operator!r}")


def _label(scenario: dict[str, Any], candidate: dict[str, Any] | None = None) -> str:
    scenario_id = scenario.get("id", "<unidentified>")
    if candidate is None:
        return f"scenario {scenario_id!r}"
    return f"scenario {scenario_id!r} candidate {candidate.get('id', '<unidentified>')!r}"


def _rule_parts(rule: Any, scenario: dict[str, Any]) -> tuple[str, str, Any]:
    if not isinstance(rule, dict):
        raise FixtureError(f"{_label(scenario)}: hard constraint must be an object, got {rule!r}")
    missing = [key for key in ("field", "op", "value") if key not in rule]
    if missing:
        raise FixtureError(
            f"{_label(scenario)}: hard constraint {rule!r} is missing {', '.join(missing)}"
        )
    field, operator = rule["field"], rule["op"]
    if not isinstance(field, str):
        raise FixtureError(f"{_label(scenario)}: hard-constraint 'field' must be a string")
    if operator not in OPERATORS:
        raise FixtureError(
            f"{_label(scenario)}: unsupported hard-constraint operator {operator!r}; "
            f"expected one of {', '.join(OPERATORS)}"
        )
    value = rule["value"]
    if operator == "contains_any" and not isinstance(value, list):
        raise FixtureError(
            f"{_label(scenario)}: hard constraint {field!r} contains_any expects a list, "
            f"got {value!r}"
        )
    return field, operator, value


def candidate_is_feasible(candidate: dict[str, Any], scenario: dict[str, Any]) -> bool:
    for rule in scenario.get("hard_constraints", []):
        field, operator, value = _rule_parts(rule, scenario)
        if not _check(candidate.get(field), operator, value):
            return False
    return True


def utility(candidate: dict[str, Any], scenario: dict[str, Any]) -> float:
    """Weighted sum of declared candidate signals.

    A missing signal is an error rather than a zero. Defaulting to zero turned
    a typo in ``utility_weights`` into a silently different ranking, which then
    surfaced only as a disagreement about the scenario's declared choice --
    with nothing pointing back at the typo.
    """
    total = 0.0
    for field, weight in scenario.get("utility_weights", {}).items():
        if field not in candidate:
            raise FixtureError(
                f"{_label(scenario, candidate)}: utility weight {field!r} has no matching "
                f"candidate field; this candidate has {', '.join(sorted(candidate))}"
            )
        value = candidate[field]
        if not _is_number(value):
            raise FixtureError(
                f"{_label(scenario, candidate)}: signal {field!r} is {value!r}, not a number"
            )
        if not _is_number(weight):
            raise FixtureError(
                f"{_label(scenario)}: utility weight {field!r} is {weight!r}, not a number"
            )
        total += float(value) * float(weight)
    return total


def rank_candidates(scenario: dict[str, Any]) -> list[tuple[str, float]]:
    ranked: list[tuple[str, float]] = []
    for candidate in scenario.get("candidates", []):
        if not isinstance(candidate, dict):
            raise FixtureError(
                f"{_label(scenario)}: candidate must be an object, got {candidate!r}"
            )
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str):
            raise FixtureError(
                f"{_label(scenario)}: candidate is missing a string 'id' (got {candidate_id!r})"
            )
        if candidate_is_feasible(candidate, scenario):
            ranked.append((candidate_id, utility(candidate, scenario)))
    return sorted(ranked, key=lambda item: (-item[1], item[0]))


def expected_choice(scenario: dict[str, Any]) -> str | None:
    ranked = rank_candidates(scenario)
    return ranked[0][0] if ranked else None
