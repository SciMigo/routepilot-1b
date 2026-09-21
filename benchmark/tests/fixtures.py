"""Fixture locations, resolved from this file rather than the working directory."""

from __future__ import annotations

from pathlib import Path

BENCHMARK_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = BENCHMARK_ROOT / "scenarios" / "module-01.jsonl"
PREDICTION_PATH = BENCHMARK_ROOT / "predictions" / "reference.jsonl"
