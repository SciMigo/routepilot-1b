# Benchmark changelog

`PLAN.md` states that Module 1 fixtures remain immutable except for corrections
documented here. This file is that record.

Immutability is what makes a result comparable across modules. A score quoted
for module 3 means nothing if the fixtures moved underneath it and nobody wrote
down how. So: fixtures are not edited silently, and every edit lands here with
its reason and its effect on the reference result.

## What belongs here

Changes to files under `benchmark/scenarios/` and `benchmark/predictions/`.

Evaluator code changes do not belong here — they are in the git history and do
not alter the fixtures. The exception is an evaluator change that moves the
reference result, which is recorded here because the number it produces is what
later modules compare against.

## Correction vs. new version

- **Correction** — the fixture disagreed with its own declared contract: a typo
  in a `utility_weights` key, a candidate field that no constraint can read, a
  declared `expected_choice_id` the oracle does not select. The intended
  meaning is unchanged, so the scenario id is kept.
- **New version** — the contract itself changes: a different constraint, a
  different threshold, a different notion of what the scenario tests. This is
  not a correction. Version the benchmark and leave the old scenario id alone,
  so results quoted against it stay interpretable.

The reading makes the same point about the `service_minutes <= 25` policy
constant: a policy judged wrong is changed and versioned, not relabelled.

## Entry format

```
## <YYYY-MM-DD> — <correction | version> — <scenario id or file>

**What changed:** one line.
**Why:** the contract it violated, or the decision that changed it.
**Effect on the reference result:** the metric before and after, or "none".
**Verified:** the command that was run.
```

## Entries

## 2026-09-21 — baseline — `benchmark/scenarios/module-01.jsonl`

**What changed:** nothing; this records the starting state.
**Why:** establishes the immutable baseline for Module 1.
**Effect on the reference result:** 4 scenarios; all positive metrics `1.0`,
`hard_violation_rate 0.0`, `selection_coverage 1.0`.
**Verified:**

```bash
python3 -m unittest discover -v
python3 -m benchmark.routepilot_eval.cli \
  benchmark/scenarios/module-01.jsonl \
  benchmark/predictions/reference.jsonl
```

No corrections yet.
