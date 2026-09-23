"""Command-line entry point for deterministic RoutePilot scenario generation."""

from __future__ import annotations

import argparse

from benchmark.routepilot_eval.validation import validate_scenarios

from .generator import DEFAULT_COUNT_PER_FAMILY, DEFAULT_SEED, generate_scenarios, write_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--count-per-family", type=int, default=DEFAULT_COUNT_PER_FAMILY)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    scenarios = generate_scenarios(args.seed, args.count_per_family)
    problems = validate_scenarios(scenarios)
    if problems:
        for problem in problems:
            print(problem)
        return 2
    write_jsonl(args.output, scenarios)
    print(f"wrote {len(scenarios)} validated scenarios to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
