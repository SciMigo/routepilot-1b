"""Run the frozen RoutePilot baseline against an OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse

from benchmark.routepilot_eval.io import load_jsonl
from benchmark.routepilot_eval.validation import validate_scenarios

from .runner import OpenAICompatibleProvider, api_key_from_environment, run_baseline


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenarios", required=True)
    parser.add_argument("--split", default="development")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--provider-name", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key-env")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=512)
    args = parser.parse_args()

    all_scenarios = load_jsonl(args.scenarios)
    problems = validate_scenarios(all_scenarios)
    if problems:
        for problem in problems:
            print(problem)
        return 2
    scenarios = [item for item in all_scenarios if item.get("split") == args.split]
    if not scenarios:
        print(f"no scenarios found for split {args.split!r}")
        return 2

    provider = OpenAICompatibleProvider(
        base_url=args.base_url,
        model=args.model,
        api_key=api_key_from_environment(args.api_key_env),
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    metrics = run_baseline(
        scenarios,
        provider,
        output_dir=args.output_dir,
        run_id=args.run_id,
        provider_name=args.provider_name,
        model=args.model,
        scenario_source=f"{args.scenarios}#{args.split}",
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    print(metrics["metrics"])
    return 0 if metrics["reconciliation"]["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
