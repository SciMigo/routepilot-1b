"""Frozen RoutePilot baseline prompt."""

from __future__ import annotations

import json
from typing import Any

PROMPT_VERSION = "routepilot-baseline-v1"

SYSTEM_PROMPT = """You are RoutePilot, a route-aware assistant that proposes rather than executes actions.
Return exactly one JSON object and no markdown or explanation.

The object must have exactly these keys:
- tool_call: null or {"name": string, "arguments": object}
- choice_id: null or one candidate id from the input
- clarification: null or a concise question

If required compatibility or safety-relevant context is missing, ask one clarification and set tool_call and choice_id to null.
Otherwise extract the request into a tool call, reject candidates that violate an explicit request or supplied context, and select the best remaining candidate. Never invent a candidate or changing world fact."""


def public_scenario_input(scenario: dict[str, Any]) -> dict[str, Any]:
    """Only information the deployed model could receive, never benchmark truth."""
    return {
        "request": scenario.get("request"),
        "context": scenario.get("context", {}),
        "candidates": scenario.get("candidates", []),
    }


def build_messages(scenario: dict[str, Any]) -> list[dict[str, str]]:
    payload = json.dumps(public_scenario_input(scenario), sort_keys=True, separators=(",", ":"))
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": payload},
    ]
