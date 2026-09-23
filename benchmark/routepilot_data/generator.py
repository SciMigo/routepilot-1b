"""Generate structured RoutePilot scenarios before generating prose.

The generator owns contexts, candidates, constraints, and deterministic labels.
A later paraphrasing stage may rewrite ``request`` only after proving that the
same typed constraints are still present.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Callable

from benchmark.routepilot_eval.oracle import expected_choice

DEFAULT_SEED = 20260923
DEFAULT_COUNT_PER_FAMILY = 2

CUISINES = ("korean", "thai", "japanese", "vietnamese")
CONNECTORS = ("CCS", "NACS")


def _finalize(scenario: dict[str, Any]) -> dict[str, Any]:
    """Derive the label instead of accepting one from a model or author."""
    scenario["expected_choice_id"] = expected_choice(scenario)
    return scenario


def _food_explicit(rng: random.Random, index: int) -> dict[str, Any]:
    cuisine = rng.choice(CUISINES)
    max_detour = rng.randint(6, 10)
    max_service = rng.randint(18, 26)
    candidates = [
        {
            "id": f"{cuisine}-route-{index}",
            "open": True,
            "cuisines": [cuisine],
            "detour_minutes": rng.randint(2, max_detour),
            "service_minutes": rng.randint(8, max_service),
            "rating": round(rng.uniform(4.0, 4.8), 1),
            "preference_match": 1.0,
        },
        {
            "id": f"{cuisine}-backup-{index}",
            "open": True,
            "cuisines": [cuisine],
            "detour_minutes": rng.randint(2, max_detour),
            "service_minutes": rng.randint(8, max_service),
            "rating": round(rng.uniform(3.7, 4.6), 1),
            "preference_match": 0.7,
        },
        {
            "id": f"too-far-{index}",
            "open": True,
            "cuisines": [cuisine],
            "detour_minutes": max_detour + rng.randint(1, 4),
            "service_minutes": rng.randint(8, max_service),
            "rating": 4.9,
            "preference_match": 1.0,
        },
        {
            "id": f"closed-favorite-{index}",
            "open": False,
            "cuisines": [cuisine],
            "detour_minutes": 1,
            "service_minutes": 6,
            "rating": 5.0,
            "preference_match": 1.0,
        },
    ]
    return _finalize(
        {
            "id": f"food-explicit-{index:03d}",
            "template_family": "food-explicit-cuisine",
            "split": "train",
            "request": (
                f"Find an open {cuisine} stop on my route with no more than a "
                f"{max_detour}-minute detour and service within {max_service} minutes."
            ),
            "context": {"destination": "current route destination"},
            "expected_call": {
                "name": "search_route_stops",
                "arguments": {
                    "category": "food",
                    "cuisines": [cuisine],
                    "max_detour_minutes": max_detour,
                    "max_service_minutes": max_service,
                    "open_now": True,
                },
            },
            "expected_clarification": False,
            "candidates": candidates,
            "hard_constraints": [
                {
                    "field": "open",
                    "op": "eq",
                    "value": True,
                    "source": "request",
                    "note": "The request explicitly requires an open stop.",
                },
                {
                    "field": "cuisines",
                    "op": "contains_any",
                    "value": [cuisine],
                    "source": "request",
                    "note": f"The request names {cuisine} cuisine.",
                },
                {
                    "field": "detour_minutes",
                    "op": "lte",
                    "value": max_detour,
                    "source": "request",
                    "note": f"The request caps detour at {max_detour} minutes.",
                },
                {
                    "field": "service_minutes",
                    "op": "lte",
                    "value": max_service,
                    "source": "request",
                    "note": f"The request caps service at {max_service} minutes.",
                },
            ],
            "utility_weights": {
                "preference_match": 35,
                "rating": 5,
                "detour_minutes": -3,
                "service_minutes": -1,
            },
            "generator": {"version": 1, "seed": None},
        }
    )


def _food_deadline(rng: random.Random, index: int) -> dict[str, Any]:
    max_detour = rng.randint(5, 9)
    deadline = rng.randint(45, 75)
    candidates = [
        {
            "id": f"deadline-safe-{index}",
            "open": True,
            "detour_minutes": rng.randint(2, max_detour),
            "arrival_minutes": deadline - rng.randint(5, 15),
            "rating": round(rng.uniform(4.0, 4.7), 1),
            "preference_match": 0.9,
        },
        {
            "id": f"deadline-backup-{index}",
            "open": True,
            "detour_minutes": rng.randint(2, max_detour),
            "arrival_minutes": deadline - rng.randint(1, 5),
            "rating": round(rng.uniform(3.8, 4.5), 1),
            "preference_match": 0.7,
        },
        {
            "id": f"deadline-late-{index}",
            "open": True,
            "detour_minutes": 1,
            "arrival_minutes": deadline + rng.randint(1, 10),
            "rating": 5.0,
            "preference_match": 1.0,
        },
        {
            "id": f"deadline-closed-{index}",
            "open": False,
            "detour_minutes": 1,
            "arrival_minutes": deadline - 20,
            "rating": 5.0,
            "preference_match": 1.0,
        },
    ]
    return _finalize(
        {
            "id": f"food-deadline-{index:03d}",
            "template_family": "food-arrival-deadline",
            "split": "development",
            "request": (
                f"Find an open food stop within {max_detour} minutes of my route, but keep "
                "me on time."
            ),
            "context": {"arrival_deadline_minutes_from_now": deadline},
            "expected_call": {
                "name": "search_route_stops",
                "arguments": {
                    "category": "food",
                    "max_detour_minutes": max_detour,
                    "arrival_deadline_minutes_from_now": deadline,
                    "open_now": True,
                },
            },
            "expected_clarification": False,
            "candidates": candidates,
            "hard_constraints": [
                {
                    "field": "open",
                    "op": "eq",
                    "value": True,
                    "source": "request",
                    "note": "The request explicitly requires an open stop.",
                },
                {
                    "field": "detour_minutes",
                    "op": "lte",
                    "value": max_detour,
                    "source": "request",
                    "note": f"The request caps detour at {max_detour} minutes.",
                },
                {
                    "field": "arrival_minutes",
                    "op": "lte",
                    "value": deadline,
                    "source": "context",
                    "note": "The maximum comes from context.arrival_deadline_minutes_from_now.",
                },
            ],
            "utility_weights": {
                "preference_match": 20,
                "rating": 5,
                "detour_minutes": -3,
                "arrival_minutes": -0.2,
            },
            "generator": {"version": 1, "seed": None},
        }
    )


def _charger_explicit(rng: random.Random, index: int) -> dict[str, Any]:
    connector = rng.choice(CONNECTORS)
    minimum_power = rng.choice((100, 150, 200))
    max_detour = rng.randint(5, 9)
    return _charger_scenario(
        rng,
        index,
        connector=connector,
        minimum_power=minimum_power,
        max_detour=max_detour,
        family="charger-explicit-connector",
        split="train",
        request=(
            f"Find an available {connector} charger with at least {minimum_power} kW, "
            f"within {max_detour} minutes of my route."
        ),
        connector_source="request",
    )


def _charger_context(rng: random.Random, index: int) -> dict[str, Any]:
    connector = rng.choice(CONNECTORS)
    minimum_power = rng.choice((100, 150, 200))
    max_detour = rng.randint(5, 9)
    return _charger_scenario(
        rng,
        index,
        connector=connector,
        minimum_power=minimum_power,
        max_detour=max_detour,
        family="charger-context-connector",
        split="development",
        request=(
            f"Find a compatible available charger of at least {minimum_power} kW no more "
            f"than {max_detour} minutes off route."
        ),
        connector_source="context",
    )


def _charger_scenario(
    rng: random.Random,
    index: int,
    *,
    connector: str,
    minimum_power: int,
    max_detour: int,
    family: str,
    split: str,
    request: str,
    connector_source: str,
) -> dict[str, Any]:
    other_connector = next(item for item in CONNECTORS if item != connector)
    candidates = [
        {
            "id": f"charge-fast-{index}-{split}",
            "available": True,
            "connectors": [connector],
            "power_kw": minimum_power + rng.randint(25, 150),
            "detour_minutes": rng.randint(2, max_detour),
            "rating": round(rng.uniform(3.8, 4.8), 1),
            "preference_match": 1.0,
        },
        {
            "id": f"charge-backup-{index}-{split}",
            "available": True,
            "connectors": [connector],
            "power_kw": minimum_power,
            "detour_minutes": rng.randint(2, max_detour),
            "rating": round(rng.uniform(3.7, 4.6), 1),
            "preference_match": 0.7,
        },
        {
            "id": f"charge-wrong-plug-{index}-{split}",
            "available": True,
            "connectors": [other_connector],
            "power_kw": minimum_power + 200,
            "detour_minutes": 1,
            "rating": 5.0,
            "preference_match": 1.0,
        },
        {
            "id": f"charge-unavailable-{index}-{split}",
            "available": False,
            "connectors": [connector],
            "power_kw": minimum_power + 200,
            "detour_minutes": 1,
            "rating": 5.0,
            "preference_match": 1.0,
        },
    ]
    return _finalize(
        {
            "id": f"{family}-{index:03d}",
            "template_family": family,
            "split": split,
            "request": request,
            "context": {"vehicle_connector": connector, "state_of_charge_percent": 18},
            "expected_call": {
                "name": "search_route_chargers",
                "arguments": {
                    "connector": connector,
                    "minimum_power_kw": minimum_power,
                    "max_detour_minutes": max_detour,
                    "available_now": True,
                },
            },
            "expected_clarification": False,
            "candidates": candidates,
            "hard_constraints": [
                {
                    "field": "available",
                    "op": "eq",
                    "value": True,
                    "source": "request",
                    "note": "The request explicitly requires an available charger.",
                },
                {
                    "field": "connectors",
                    "op": "contains_any",
                    "value": [connector],
                    "source": connector_source,
                    "note": (
                        f"The connector is named in the {connector_source}; incompatible "
                        "hardware is infeasible."
                    ),
                },
                {
                    "field": "power_kw",
                    "op": "gte",
                    "value": minimum_power,
                    "source": "request",
                    "note": f"The request requires at least {minimum_power} kW.",
                },
                {
                    "field": "detour_minutes",
                    "op": "lte",
                    "value": max_detour,
                    "source": "request",
                    "note": f"The request caps detour at {max_detour} minutes.",
                },
            ],
            "utility_weights": {
                "power_kw": 0.05,
                "preference_match": 25,
                "rating": 4,
                "detour_minutes": -4,
            },
            "generator": {"version": 1, "seed": None},
        }
    )


FAMILIES: tuple[Callable[[random.Random, int], dict[str, Any]], ...] = (
    _food_explicit,
    _charger_explicit,
    _food_deadline,
    _charger_context,
)


def generate_scenarios(
    seed: int = DEFAULT_SEED,
    count_per_family: int = DEFAULT_COUNT_PER_FAMILY,
) -> list[dict[str, Any]]:
    if count_per_family < 1:
        raise ValueError("count_per_family must be at least 1")
    rng = random.Random(seed)
    scenarios: list[dict[str, Any]] = []
    for builder in FAMILIES:
        for index in range(1, count_per_family + 1):
            scenario = builder(rng, index)
            scenario["generator"]["seed"] = seed
            scenarios.append(scenario)
    return scenarios


def write_jsonl(path: str | Path, scenarios: list[dict[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(item, sort_keys=True) + "\n" for item in scenarios)
    output.write_text(text, encoding="utf-8")
