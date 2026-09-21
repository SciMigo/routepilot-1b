"""Command-line entry point for deterministic RoutePilot evaluation."""

from __future__ import annotations

import argparse
import json
import sys

from .io import load_jsonl
from .scoring import evaluate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenarios", help="scenario JSONL path")
    parser.add_argument("predictions", help="prediction JSONL path")
    args = parser.parse_args()
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
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
