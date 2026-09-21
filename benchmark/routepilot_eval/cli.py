"""Command-line entry point for deterministic RoutePilot evaluation."""

from __future__ import annotations

import argparse
import json

from .io import load_jsonl
from .scoring import evaluate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenarios", help="scenario JSONL path")
    parser.add_argument("predictions", help="prediction JSONL path")
    args = parser.parse_args()
    result = evaluate(load_jsonl(args.scenarios), load_jsonl(args.predictions))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
