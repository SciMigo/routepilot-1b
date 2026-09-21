from __future__ import annotations

import unittest

from benchmark.routepilot_eval.io import load_jsonl
from benchmark.routepilot_eval.oracle import candidate_is_feasible, expected_choice
from benchmark.routepilot_eval.scoring import evaluate


SCENARIO_PATH = "benchmark/scenarios/module-01.jsonl"
PREDICTION_PATH = "benchmark/predictions/reference.jsonl"


class OracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenarios = load_jsonl(SCENARIO_PATH)

    def test_declared_choices_match_oracle(self) -> None:
        for scenario in self.scenarios:
            with self.subTest(scenario=scenario["id"]):
                self.assertEqual(scenario["expected_choice_id"], expected_choice(scenario))

    def test_closed_candidate_is_infeasible(self) -> None:
        scenario = self.scenarios[0]
        candidate = next(item for item in scenario["candidates"] if item["id"] == "closed-ramen")
        self.assertFalse(candidate_is_feasible(candidate, scenario))

    def test_reference_predictions_are_perfect(self) -> None:
        result = evaluate(self.scenarios, load_jsonl(PREDICTION_PATH))
        metrics = result["metrics"]
        for name, value in metrics.items():
            expected = 0.0 if name == "hard_violation_rate" else 1.0
            with self.subTest(metric=name):
                self.assertEqual(expected, value)

    def test_infeasible_choice_is_reported_separately(self) -> None:
        predictions = load_jsonl(PREDICTION_PATH)
        predictions[0]["choice_id"] = "thai-express"
        result = evaluate(self.scenarios, predictions)
        self.assertEqual(1.0, result["metrics"]["tool_accuracy"])
        self.assertGreater(result["metrics"]["hard_violation_rate"], 0.0)
        self.assertLess(result["metrics"]["selection_accuracy"], 1.0)

    def test_missing_argument_reduces_recall_not_selection(self) -> None:
        predictions = load_jsonl(PREDICTION_PATH)
        del predictions[0]["tool_call"]["arguments"]["max_detour_minutes"]
        result = evaluate(self.scenarios, predictions)
        self.assertLess(result["metrics"]["constraint_recall"], 1.0)
        self.assertEqual(1.0, result["metrics"]["selection_accuracy"])


if __name__ == "__main__":
    unittest.main()
