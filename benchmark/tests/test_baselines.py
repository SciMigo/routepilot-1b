import json
import tempfile
import unittest
from pathlib import Path

from benchmark.routepilot_baselines import ModelResponse, build_messages, parse_prediction, run_baseline
from benchmark.routepilot_baselines.runner import BaselineParseError
from benchmark.routepilot_eval.io import load_jsonl


class FakeProvider:
    def __init__(self, texts):
        self.texts = iter(texts)

    def complete(self, messages):
        return ModelResponse(next(self.texts), {"total_tokens": 17}, "fixture-request")


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.scenarios = load_jsonl("benchmark/scenarios/module-02.jsonl")[:2]

    def test_prompt_excludes_benchmark_truth(self):
        rendered = json.dumps(build_messages(self.scenarios[0]))
        for forbidden in ("expected_call", "expected_choice_id", "hard_constraints", "utility_weights"):
            self.assertNotIn(forbidden, rendered)
        self.assertIn(self.scenarios[0]["request"], rendered)

    def test_parser_accepts_only_exact_unfenced_schema(self):
        text = json.dumps(
            {"tool_call": None, "choice_id": None, "clarification": "Which connector?"}
        )
        prediction = parse_prediction("case-1", text)
        self.assertEqual(prediction["scenario_id"], "case-1")
        with self.assertRaises(BaselineParseError):
            parse_prediction("case-1", f"```json\n{text}\n```")
        with self.assertRaises(BaselineParseError):
            parse_prediction("case-1", json.dumps({**json.loads(text), "reasoning": "extra"}))

    def test_run_keeps_raw_responses_and_scores_parse_failure(self):
        valid = json.dumps(
            {
                "tool_call": self.scenarios[0]["expected_call"],
                "choice_id": self.scenarios[0]["expected_choice_id"],
                "clarification": None,
            }
        )
        provider = FakeProvider([valid, "not-json"])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            metrics = run_baseline(
                self.scenarios,
                provider,
                output_dir=output,
                run_id="fixture",
                provider_name="fake",
                model="fixture-model",
                scenario_source="test",
            )
            responses = load_jsonl(output / "responses.jsonl")
            predictions = load_jsonl(output / "predictions.jsonl")
            self.assertTrue((output / "artifacts.json").exists())
        self.assertEqual(responses[1]["text"], "not-json")
        self.assertIsNotNone(responses[1]["parse_error"])
        self.assertEqual(predictions[1]["tool_call"], "invalid")
        self.assertEqual(metrics["metrics"]["schema_valid_rate"], 0.5)
        self.assertTrue(metrics["reconciliation"]["clean"])


if __name__ == "__main__":
    unittest.main()
