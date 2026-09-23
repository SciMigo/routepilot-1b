import json
import tempfile
import unittest
from pathlib import Path

from benchmark.routepilot_data import (
    DEFAULT_COUNT_PER_FAMILY,
    DEFAULT_SEED,
    generate_scenarios,
    write_jsonl,
)
from benchmark.routepilot_eval import validate_scenarios
from benchmark.routepilot_eval.oracle import expected_choice


class ScenarioGenerationTests(unittest.TestCase):
    def test_same_seed_produces_identical_scenarios(self):
        self.assertEqual(generate_scenarios(17, 3), generate_scenarios(17, 3))
        self.assertNotEqual(generate_scenarios(17, 3), generate_scenarios(18, 3))

    def test_every_generated_scenario_validates_and_derives_its_choice(self):
        scenarios = generate_scenarios(DEFAULT_SEED, DEFAULT_COUNT_PER_FAMILY)
        self.assertEqual(validate_scenarios(scenarios), [])
        for scenario in scenarios:
            self.assertEqual(scenario["expected_choice_id"], expected_choice(scenario))

    def test_template_families_do_not_cross_splits(self):
        seen: dict[str, str] = {}
        for scenario in generate_scenarios(DEFAULT_SEED, 4):
            family, split = scenario["template_family"], scenario["split"]
            self.assertEqual(seen.setdefault(family, split), split)
        self.assertEqual(set(seen.values()), {"train", "development"})

    def test_writer_is_stable_jsonl(self):
        scenarios = generate_scenarios(23, 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scenarios.jsonl"
            write_jsonl(path, scenarios)
            loaded = [json.loads(line) for line in path.read_text().splitlines()]
        self.assertEqual(loaded, scenarios)

    def test_committed_fixture_matches_the_documented_generator_run(self):
        expected = generate_scenarios(DEFAULT_SEED, DEFAULT_COUNT_PER_FAMILY)
        path = Path("benchmark/scenarios/module-02.jsonl")
        actual = [json.loads(line) for line in path.read_text().splitlines()]
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
