"""The three scoring rules stated at the top of `scoring.py`, as tests.

Each case here is a way a model can look correct while doing something wrong.
They are written against the committed Module 1 fixture so a student can run
them, read the numbers, and see which metric is supposed to move.
"""

from __future__ import annotations

import copy
import unittest

from benchmark.routepilot_eval.io import load_jsonl
from benchmark.routepilot_eval.scoring import evaluate


SCENARIO_PATH = "benchmark/scenarios/module-01.jsonl"
PREDICTION_PATH = "benchmark/predictions/reference.jsonl"


class ScoringRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenarios = load_jsonl(SCENARIO_PATH)
        cls.reference = load_jsonl(PREDICTION_PATH)

    def predictions(self) -> list[dict]:
        return copy.deepcopy(self.reference)

    # Rule 1: silence is never credited.

    def test_empty_predictions_do_not_look_safe(self) -> None:
        metrics = evaluate(self.scenarios, [])["metrics"]
        for name in (
            "schema_valid_rate",
            "tool_accuracy",
            "clarification_accuracy",
            "selection_accuracy",
            "constraint_recall",
            "constraint_precision",
        ):
            with self.subTest(metric=name):
                self.assertEqual(0.0, metrics[name])
        # A model that chose nothing did not violate a hard constraint, so the
        # safety metric is honestly zero -- coverage is what exposes it.
        self.assertEqual(0.0, metrics["hard_violation_rate"])
        self.assertEqual(0.0, metrics["selection_coverage"])

    def test_missing_prediction_is_reported_and_not_credited(self) -> None:
        predictions = self.predictions()
        del predictions[0]
        result = evaluate(self.scenarios, predictions)
        self.assertEqual(["ord-asian-stop"], result["reconciliation"]["missing_predictions"])
        self.assertFalse(result["reconciliation"]["clean"])
        row = result["details"][0]
        self.assertFalse(row["prediction_present"])
        self.assertFalse(row["tool_correct"])
        self.assertFalse(row["clarification_correct"])
        self.assertFalse(row["selection_correct"])

    def test_invalid_prediction_is_not_a_correct_abstention(self) -> None:
        predictions = self.predictions()
        # A malformed tool call, on the one scenario whose expected call is None.
        predictions[3]["tool_call"] = {"name": 123}
        result = evaluate(self.scenarios, predictions)
        row = result["details"][3]
        self.assertFalse(row["schema_valid"])
        self.assertFalse(row["tool_correct"])
        self.assertLess(result["metrics"]["tool_accuracy"], 1.0)

    def test_schema_failure_does_not_spare_selection(self) -> None:
        predictions = self.predictions()
        predictions[0]["clarification"] = 12345
        result = evaluate(self.scenarios, predictions)
        row = result["details"][0]
        self.assertFalse(row["schema_valid"])
        self.assertFalse(row["tool_correct"])
        self.assertFalse(row["selection_correct"])
        self.assertLess(result["metrics"]["selection_accuracy"], 1.0)

    def test_duplicate_and_unknown_prediction_ids_are_reported(self) -> None:
        predictions = self.predictions()
        predictions.append(copy.deepcopy(predictions[0]))
        predictions.append({"scenario_id": "no-such-scenario"})
        reconciliation = evaluate(self.scenarios, predictions)["reconciliation"]
        self.assertEqual(["ord-asian-stop"], reconciliation["duplicate_prediction_ids"])
        self.assertEqual(["no-such-scenario"], reconciliation["unknown_prediction_ids"])
        self.assertFalse(reconciliation["clean"])

    def test_duplicate_prediction_does_not_change_the_score(self) -> None:
        predictions = self.predictions()
        losing = copy.deepcopy(predictions[0])
        losing["choice_id"] = "thai-express"
        predictions.append(losing)
        metrics = evaluate(self.scenarios, predictions)["metrics"]
        self.assertEqual(1.0, metrics["selection_accuracy"])

    # Rule 2: safety is judged on whatever the prediction named.

    def test_guessing_instead_of_clarifying_is_a_hard_violation(self) -> None:
        predictions = self.predictions()
        predictions[3]["clarification"] = None
        predictions[3]["choice_id"] = "some-charger"
        result = evaluate(self.scenarios, predictions)
        row = result["details"][3]
        self.assertTrue(row["hard_violation"])
        self.assertFalse(row["selection_correct"])
        self.assertGreater(result["metrics"]["hard_violation_rate"], 0.0)
        self.assertLess(result["metrics"]["clarification_accuracy"], 1.0)

    def test_hard_violation_is_charged_even_when_the_schema_fails(self) -> None:
        predictions = self.predictions()
        predictions[0]["choice_id"] = "thai-express"
        predictions[0]["clarification"] = 12345  # invalidates the payload
        result = evaluate(self.scenarios, predictions)
        row = result["details"][0]
        self.assertFalse(row["schema_valid"])
        self.assertTrue(row["hard_violation"])

    # Rule 3: no denominator the model can move.

    def test_abstaining_cannot_improve_the_safety_rate(self) -> None:
        violating = self.predictions()
        violating[0]["choice_id"] = "thai-express"
        abstaining = self.predictions()
        abstaining[0]["choice_id"] = None
        abstaining[1]["choice_id"] = None
        abstaining[2]["choice_id"] = None
        self.assertGreater(
            evaluate(self.scenarios, violating)["metrics"]["hard_violation_rate"], 0.0
        )
        # Dropping every other choice must not dilute the one violation away.
        diluted = self.predictions()
        diluted[0]["choice_id"] = "thai-express"
        diluted[1]["choice_id"] = None
        diluted[2]["choice_id"] = None
        self.assertEqual(
            evaluate(self.scenarios, violating)["metrics"]["hard_violation_rate"],
            evaluate(self.scenarios, diluted)["metrics"]["hard_violation_rate"],
        )
        self.assertLess(
            evaluate(self.scenarios, abstaining)["metrics"]["selection_coverage"], 1.0
        )

    # Argument comparison: same constraint, different JSON spelling.

    def test_list_argument_order_is_not_an_extraction_defect(self) -> None:
        predictions = self.predictions()
        arguments = predictions[0]["tool_call"]["arguments"]
        arguments["cuisines"] = list(reversed(arguments["cuisines"]))
        metrics = evaluate(self.scenarios, predictions)["metrics"]
        self.assertEqual(1.0, metrics["constraint_precision"])
        self.assertEqual(1.0, metrics["constraint_recall"])

    def test_integral_float_matches_integer(self) -> None:
        predictions = self.predictions()
        predictions[0]["tool_call"]["arguments"]["max_detour_minutes"] = 10.0
        metrics = evaluate(self.scenarios, predictions)["metrics"]
        self.assertEqual(1.0, metrics["constraint_precision"])
        self.assertEqual(1.0, metrics["constraint_recall"])

    def test_a_genuinely_different_value_still_misses(self) -> None:
        predictions = self.predictions()
        predictions[0]["tool_call"]["arguments"]["max_detour_minutes"] = 10.5
        self.assertLess(
            evaluate(self.scenarios, predictions)["metrics"]["constraint_recall"], 1.0
        )

    def test_repeated_list_entry_still_differs(self) -> None:
        predictions = self.predictions()
        arguments = predictions[0]["tool_call"]["arguments"]
        arguments["cuisines"] = arguments["cuisines"] + ["thai"]
        self.assertLess(
            evaluate(self.scenarios, predictions)["metrics"]["constraint_recall"], 1.0
        )

    def test_arguments_do_not_count_for_the_wrong_tool(self) -> None:
        predictions = self.predictions()
        predictions[0]["tool_call"]["name"] = "search_route_chargers"
        metrics = evaluate(self.scenarios, predictions)["metrics"]
        self.assertLess(metrics["tool_accuracy"], 1.0)
        self.assertLess(metrics["constraint_precision"], 1.0)
        self.assertLess(metrics["constraint_recall"], 1.0)


if __name__ == "__main__":
    unittest.main()
