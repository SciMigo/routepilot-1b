"""Run a frozen baseline against an OpenAI-compatible chat endpoint."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from benchmark.routepilot_eval.scoring import evaluate

from .prompt import PROMPT_VERSION, build_messages


class BaselineParseError(ValueError):
    pass


@dataclass(frozen=True)
class ModelResponse:
    text: str
    usage: dict[str, Any]
    provider_request_id: str | None = None


class Provider(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> ModelResponse: ...


class OpenAICompatibleProvider:
    """Minimal chat-completions client with no retry or repair behavior."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 512,
        timeout_seconds: float = 120.0,
    ) -> None:
        self.url = f"{base_url.rstrip('/')}/chat/completions"
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds

    def complete(self, messages: list[dict[str, str]]) -> ModelResponse:
        body = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False,
            }
        ).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(self.url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))

        try:
            message = payload["choices"][0]["message"]
            text = message["content"] if isinstance(message, dict) else message
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError("provider response did not contain choices[0].message") from error
        if not isinstance(text, str):
            raise RuntimeError("provider response message was not text")
        request_id = payload.get("id")
        return ModelResponse(
            text=text,
            usage=payload.get("usage") if isinstance(payload.get("usage"), dict) else {},
            provider_request_id=request_id if isinstance(request_id, str) else None,
        )


def parse_prediction(scenario_id: str, text: str) -> dict[str, Any]:
    """Strictly parse one model response; do not strip fences or repair JSON."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise BaselineParseError(f"response is not one JSON object: {error.msg}") from error
    if not isinstance(payload, dict):
        raise BaselineParseError("response must be a JSON object")
    expected_keys = {"tool_call", "choice_id", "clarification"}
    if set(payload) != expected_keys:
        raise BaselineParseError(
            f"response keys must be exactly {sorted(expected_keys)}; got {sorted(payload)}"
        )
    call = payload["tool_call"]
    if call is not None and not (
        isinstance(call, dict)
        and isinstance(call.get("name"), str)
        and isinstance(call.get("arguments"), dict)
        and set(call) == {"name", "arguments"}
    ):
        raise BaselineParseError("tool_call must be null or contain exactly name and arguments")
    if payload["choice_id"] is not None and not isinstance(payload["choice_id"], str):
        raise BaselineParseError("choice_id must be a string or null")
    if payload["clarification"] is not None and not isinstance(payload["clarification"], str):
        raise BaselineParseError("clarification must be a string or null")
    return {"scenario_id": scenario_id, **payload}


def _invalid_prediction(scenario_id: str, message: str) -> dict[str, Any]:
    # A string tool_call intentionally fails the evaluator's prediction schema.
    return {
        "scenario_id": scenario_id,
        "tool_call": "invalid",
        "choice_id": None,
        "clarification": None,
        "parse_error": message,
    }


def _jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def run_baseline(
    scenarios: list[dict[str, Any]],
    provider: Provider,
    *,
    output_dir: str | Path,
    run_id: str,
    provider_name: str,
    model: str,
    scenario_source: str,
    temperature: float = 0.0,
    max_tokens: int = 512,
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc)
    requests: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    predictions: list[dict[str, Any]] = []
    usage_totals: dict[str, float] = {}

    for scenario in scenarios:
        scenario_id = scenario["id"]
        messages = build_messages(scenario)
        requests.append(
            {"scenario_id": scenario_id, "prompt_version": PROMPT_VERSION, "messages": messages}
        )
        before = time.monotonic()
        try:
            response = provider.complete(messages)
            latency_ms = round((time.monotonic() - before) * 1000, 3)
            parse_error = None
            try:
                prediction = parse_prediction(scenario_id, response.text)
            except BaselineParseError as error:
                parse_error = str(error)
                prediction = _invalid_prediction(scenario_id, parse_error)
            for key, value in response.usage.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    usage_totals[key] = usage_totals.get(key, 0) + value
            responses.append(
                {
                    "scenario_id": scenario_id,
                    "text": response.text,
                    "usage": response.usage,
                    "provider_request_id": response.provider_request_id,
                    "latency_ms": latency_ms,
                    "parse_error": parse_error,
                    "provider_error": None,
                }
            )
        except Exception as error:  # preserve provider failures as scored evidence
            latency_ms = round((time.monotonic() - before) * 1000, 3)
            message = f"{type(error).__name__}: {error}"
            prediction = _invalid_prediction(scenario_id, message)
            responses.append(
                {
                    "scenario_id": scenario_id,
                    "text": None,
                    "usage": {},
                    "provider_request_id": None,
                    "latency_ms": latency_ms,
                    "parse_error": None,
                    "provider_error": message,
                }
            )
        predictions.append(prediction)

    metrics = evaluate(scenarios, predictions)
    _jsonl(output / "requests.jsonl", requests)
    _jsonl(output / "responses.jsonl", responses)
    _jsonl(output / "predictions.jsonl", predictions)
    _write_json(output / "metrics.json", metrics)
    _write_json(
        output / "environment.json",
        {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
    )
    _write_json(
        output / "costs.json",
        {"usage": usage_totals, "amount": "not_recorded", "currency": "not_recorded"},
    )
    completed = datetime.now(timezone.utc)
    run = {
        "run_id": run_id,
        "provider": provider_name,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "scenario_source": scenario_source,
        "scenario_count": len(scenarios),
        "retry_count": 0,
        "repair_count": 0,
        "started_at": started.isoformat(),
        "completed_at": completed.isoformat(),
        "status": "complete",
    }
    _write_json(output / "run.json", run)
    (output / "stdout.log").write_text(
        f"completed {run_id}: {len(scenarios)} scenarios; no retries; no JSON repair\n",
        encoding="utf-8",
    )

    artifact_names = (
        "run.json",
        "environment.json",
        "requests.jsonl",
        "responses.jsonl",
        "predictions.jsonl",
        "metrics.json",
        "costs.json",
        "stdout.log",
    )
    _write_json(
        output / "artifacts.json",
        {"files": {name: {"sha256": _sha256(output / name)} for name in artifact_names}},
    )
    return metrics


def api_key_from_environment(name: str | None) -> str | None:
    if not name:
        return None
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"environment variable {name!r} is not set")
    return value
