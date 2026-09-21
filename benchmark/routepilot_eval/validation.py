"""Fixture validation, kept out of the scoring loop.

`evaluate` used to raise part-way through scoring when a scenario's declared
choice disagreed with the oracle. That conflated two different jobs: checking
that a fixture is well formed, and measuring a model against it. It also meant
one bad scenario produced no metrics at all, and reported a missing
`expected_choice_id` as a disagreement about its value.

Validation now runs as its own pass, collects every problem instead of
stopping at the first, and names the file and line each one came from.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .errors import FixtureError
from .io import load_jsonl_with_lines
from .oracle import expected_choice

REQUIRED_SCENARIO_KEYS = ("id", "expected_clarification", "expected_choice_id")

#: Where a hard constraint came from. `request` and `context` mean a reader can
#: derive the value from the scenario itself; `policy` means it is a declared
#: product decision that no amount of reading will derive, and so must carry a
#: note saying what the decision is.
CONSTRAINT_SOURCES = ("request", "context", "policy")


def _check_constraints(scenario: dict[str, Any], where: str, problems: list[str]) -> None:
    """Every hard constraint must say where its value came from.

    The fixture's claim to be auditable by hand depends on this. A constant a
    reader cannot derive and cannot trace is indistinguishable from a mistake,
    and here it is the only thing standing between a candidate and the
    module's flagship safety example.
    """
    for position, rule in enumerate(scenario.get("hard_constraints", [])):
        if not isinstance(rule, dict):
            problems.append(f"{where}: hard_constraints[{position}] must be an object")
            continue
        label = f"{where}: hard constraint {rule.get('field', position)!r}"
        for key in ("field", "op", "value"):
            if key not in rule:
                problems.append(f"{label} is missing {key!r}")
        source = rule.get("source")
        if source is None:
            problems.append(
                f"{label} is missing 'source'; say whether the value comes from the "
                f"request, the context, or declared policy"
            )
        elif source not in CONSTRAINT_SOURCES:
            problems.append(
                f"{label} has source {source!r}; expected one of "
                f"{', '.join(CONSTRAINT_SOURCES)}"
            )
        elif source == "policy" and not str(rule.get("note", "")).strip():
            problems.append(
                f"{label} is declared policy and must carry a 'note' saying what the "
                f"decision is; a reader cannot derive it from the scenario"
            )


def _check_shape(scenario: dict[str, Any], where: str, problems: list[str]) -> bool:
    """Structural checks. Returns False when the oracle cannot safely run."""
    before = len(problems)

    for key in REQUIRED_SCENARIO_KEYS:
        if key not in scenario:
            problems.append(f"{where}: missing required key {key!r}")

    if "id" in scenario and not isinstance(scenario["id"], str):
        problems.append(f"{where}: 'id' must be a string, got {scenario['id']!r}")

    if "expected_clarification" in scenario and not isinstance(
        scenario["expected_clarification"], bool
    ):
        problems.append(
            f"{where}: 'expected_clarification' must be true or false, "
            f"got {scenario['expected_clarification']!r}"
        )

    expected_call = scenario.get("expected_call")
    if expected_call is not None:
        if not isinstance(expected_call, dict):
            problems.append(f"{where}: 'expected_call' must be an object or null")
        else:
            if not isinstance(expected_call.get("name"), str):
                problems.append(f"{where}: 'expected_call.name' must be a string")
            if not isinstance(expected_call.get("arguments"), dict):
                problems.append(f"{where}: 'expected_call.arguments' must be an object")

    candidates = scenario.get("candidates", [])
    if not isinstance(candidates, list):
        problems.append(f"{where}: 'candidates' must be a list")
        candidates = []

    seen: set[str] = set()
    for position, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            problems.append(f"{where}: candidate[{position}] must be an object")
            continue
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str):
            problems.append(
                f"{where}: candidate[{position}] is missing a string 'id' (got {candidate_id!r})"
            )
            continue
        if candidate_id in seen:
            problems.append(f"{where}: duplicate candidate id {candidate_id!r}")
        seen.add(candidate_id)

    weights = scenario.get("utility_weights", {})
    if not isinstance(weights, dict):
        problems.append(f"{where}: 'utility_weights' must be an object")

    if not isinstance(scenario.get("hard_constraints", []), list):
        problems.append(f"{where}: 'hard_constraints' must be a list")
    else:
        _check_constraints(scenario, where, problems)

    return len(problems) == before


def _check_oracle(
    scenario: dict[str, Any], where: str, location: str, problems: list[str]
) -> None:
    """Semantic checks that require running the oracle."""
    try:
        oracle_choice = expected_choice(scenario)
    except FixtureError as error:
        # The oracle's message already names the scenario, so prefix only the
        # file and line rather than repeating the id.
        problems.append(f"{location}: {error}")
        return

    declared = scenario.get("expected_choice_id")
    if declared is not None and not isinstance(declared, str):
        problems.append(f"{where}: 'expected_choice_id' must be a string or null")
        return
    if declared != oracle_choice:
        problems.append(
            f"{where}: declared 'expected_choice_id' is {declared!r} but the oracle ranks "
            f"{oracle_choice!r} highest among feasible candidates"
        )

    if scenario.get("expected_clarification") and scenario.get("expected_call") is not None:
        problems.append(
            f"{where}: a scenario that requires clarification must not declare an expected_call"
        )
    if scenario.get("expected_clarification") and oracle_choice is not None:
        problems.append(
            f"{where}: a scenario that requires clarification must not have a feasible "
            f"candidate for the oracle to choose (it ranks {oracle_choice!r})"
        )


def validate_scenarios(
    scenarios: list[dict[str, Any]], locate: Callable[[int], str] | None = None
) -> list[str]:
    """Every problem found in `scenarios`, as human-readable lines.

    An empty list means the fixture is sound. `locate` maps a scenario's index
    to the label used in messages; the default is positional, and
    `validate_scenario_file` supplies one built from real file lines.
    """
    locate = locate or (lambda index: f"scenario[{index}]")
    problems: list[str] = []
    seen: set[str] = set()

    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            problems.append(f"{locate(index)}: scenario must be an object")
            continue
        scenario_id = scenario.get("id")
        location = locate(index)
        where = location
        if isinstance(scenario_id, str):
            where = f"{location} {scenario_id!r}"
            if scenario_id in seen:
                problems.append(f"{where}: duplicate scenario id")
            seen.add(scenario_id)
        if _check_shape(scenario, where, problems):
            _check_oracle(scenario, where, location, problems)

    return problems


def validate_scenario_file(path: str | Path) -> list[str]:
    """Validate a scenario JSONL file, labelling problems `path:line`."""
    pairs = load_jsonl_with_lines(path)
    lines = [line_number for line_number, _ in pairs]
    scenarios = [scenario for _, scenario in pairs]
    return validate_scenarios(scenarios, locate=lambda index: f"{path}:{lines[index]}")
