"""Command-line entry point for deterministic RoutePilot evaluation."""

from __future__ import annotations

import argparse
import json
import sys

from .io import load_jsonl
from .scoring import evaluate
from .validation import validate_scenario_file

EXIT_OK = 0
EXIT_RECONCILIATION = 1
EXIT_INVALID_FIXTURE = 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenarios", help="scenario JSONL path")
    parser.add_argument("predictions", help="prediction JSONL path")
    args = parser.parse_args()

    # Validate the fixture before scoring anything. A malformed scenario is a
    # problem with the benchmark, not with the model under test, and every
    # problem is reported at once rather than one exception at a time.
    problems = validate_scenario_file(args.scenarios)
    if problems:
        print(f"{args.scenarios}: {len(problems)} problem(s)", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return EXIT_INVALID_FIXTURE

    result = evaluate(load_jsonl(args.scenarios), load_jsonl(args.predictions))
    print(json.dumps(result, indent=2, sort_keys=True))

    # Metrics computed over a prediction file that does not line up with the
    # scenario file describe a different run than the caller thinks they are
    # reading, so this is an error rather than a note in the JSON.
    reconciliation = result["reconciliation"]
    if not reconciliation["clean"]:
        print(
            f"{args.predictions}: does not reconcile with {args.scenarios} "
            f"({len(reconciliation['missing_predictions'])} missing, "
            f"{len(reconciliation['duplicate_prediction_ids'])} duplicate, "
            f"{len(reconciliation['unknown_prediction_ids'])} unknown); "
            'see "reconciliation" in the result',
            file=sys.stderr,
        )
        return EXIT_RECONCILIATION
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
