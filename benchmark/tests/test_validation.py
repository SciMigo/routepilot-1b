"""Fixture validation, oracle typing, and error messages that name their row."""

from __future__ import annotations

import copy
import unittest

from benchmark.routepilot_eval.errors import FixtureError
from benchmark.routepilot_eval.io import load_jsonl
from benchmark.routepilot_eval.oracle import candidate_is_feasible, utility
from benchmark.routepilot_eval.scoring import evaluate
from benchmark.routepilot_eval.validation import validate_scenario_file, validate_scenarios


SCENARIO_PATH = "benchmark/scenarios/module-01.jsonl"


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenarios = load_jsonl(SCENARIO_PATH)

    def altered(self) -> list[dict]:
        return copy.deepcopy(self.scenarios)

    def test_committed_fixture_validates_clean(self) -> None:
        self.assertEqual([], validate_scenario_file(SCENARIO_PATH))

    def test_file_problems_name_the_file_and_line(self) -> None:
        problems = validate_scenarios(
            [{"id": "x", "expected_clarification": False, "expected_choice_id": "nope"}],
            locate=lambda index: f"{SCENARIO_PATH}:{index + 1}",
        )
        self.assertEqual(1, len(problems))
        self.assertTrue(problems[0].startswith(f"{SCENARIO_PATH}:1"))

    def test_missing_expected_choice_id_is_reported_as_missing(self) -> None:
        scenarios = self.altered()
        del scenarios[0]["expected_choice_id"]
        problems = validate_scenarios(scenarios)
        self.assertEqual(1, len(problems))
        self.assertIn("missing required key 'expected_choice_id'", problems[0])

    def test_declared_choice_disagreement_is_reported_not_raised(self) -> None:
        scenarios = self.altered()
        scenarios[0]["expected_choice_id"] = "thai-express"
        problems = validate_scenarios(scenarios)
        self.assertIn("the oracle ranks 'seoul-kitchen' highest", problems[0])
        # Scoring no longer aborts on a fixture disagreement; it is not its job.
        self.assertIn("metrics", evaluate(scenarios, []))

    def test_every_problem_is_collected_not_just_the_first(self) -> None:
        scenarios = self.altered()
        scenarios[0]["expected_choice_id"] = "thai-express"
        scenarios[2]["expected_choice_id"] = "route-roast"
        self.assertEqual(2, len(validate_scenarios(scenarios)))

    def test_utility_weight_typo_points_at_the_typo(self) -> None:
        scenarios = self.altered()
        weights = scenarios[2]["utility_weights"]
        weights["servce_minutes"] = weights.pop("service_minutes")
        problems = validate_scenarios(scenarios)
        self.assertIn("utility weight 'servce_minutes' has no matching candidate field", problems[0])

    def test_null_signal_is_an_error_not_a_crash(self) -> None:
        scenarios = self.altered()
        scenarios[2]["candidates"][0]["rating"] = None
        problems = validate_scenarios(scenarios)
        self.assertIn("signal 'rating' is None, not a number", problems[0])

    def test_missing_signal_is_not_silently_zero(self) -> None:
        scenario = {"id": "s", "utility_weights": {"rating": 1}}
        with self.assertRaises(FixtureError) as caught:
            utility({"id": "c"}, scenario)
        self.assertIn("candidate 'c'", str(caught.exception))

    def test_clarification_scenario_must_not_declare_a_call(self) -> None:
        scenarios = self.altered()
        scenarios[3]["expected_call"] = {"name": "search_route_chargers", "arguments": {}}
        problems = validate_scenarios(scenarios)
        self.assertIn("must not declare an expected_call", problems[0])

    def test_malformed_rows_name_the_scenario_and_candidate(self) -> None:
        scenarios = self.altered()
        del scenarios[0]["candidates"][1]["id"]
        self.assertIn("candidate[1] is missing a string 'id'", validate_scenarios(scenarios)[0])

        scenarios = self.altered()
        scenarios[0]["expected_call"]["arguments"] = ["not", "an", "object"]
        self.assertIn("'expected_call.arguments' must be an object", validate_scenarios(scenarios)[0])

        with self.assertRaises(FixtureError) as caught:
            evaluate([{"no": "id"}], [])
        self.assertIn("scenario[0]", str(caught.exception))

    def test_duplicate_ids_are_reported(self) -> None:
        scenarios = self.altered()
        scenarios.append(copy.deepcopy(scenarios[0]))
        self.assertIn("duplicate scenario id", " ".join(validate_scenarios(scenarios)))

        scenarios = self.altered()
        scenarios[0]["candidates"][1]["id"] = "seoul-kitchen"
        self.assertIn("duplicate candidate id", " ".join(validate_scenarios(scenarios)))


class OracleTypingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = load_jsonl(SCENARIO_PATH)[0]

    def candidate(self, **overrides) -> dict:
        base = {
            "id": "probe",
            "open": True,
            "cuisines": ["thai"],
            "detour_minutes": 4,
            "service_minutes": 18,
            "arrival_minutes": 90,
        }
        base.update(overrides)
        return base

    def test_numeric_one_does_not_satisfy_a_boolean_constraint(self) -> None:
        self.assertTrue(candidate_is_feasible(self.candidate(), self.scenario))
        self.assertFalse(candidate_is_feasible(self.candidate(open=1), self.scenario))
        self.assertFalse(candidate_is_feasible(self.candidate(open=1.0), self.scenario))

    def test_non_numeric_value_fails_a_range_constraint_without_crashing(self) -> None:
        self.assertFalse(
            candidate_is_feasible(self.candidate(detour_minutes="4"), self.scenario)
        )
        self.assertFalse(
            candidate_is_feasible(self.candidate(detour_minutes=None), self.scenario)
        )

    def test_unsupported_operator_names_the_scenario(self) -> None:
        scenario = {
            "id": "s",
            "hard_constraints": [{"field": "x", "op": "approximately", "value": 1}],
        }
        with self.assertRaises(FixtureError) as caught:
            candidate_is_feasible({"id": "c", "x": 1}, scenario)
        self.assertIn("scenario 's'", str(caught.exception))
        self.assertIn("approximately", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
