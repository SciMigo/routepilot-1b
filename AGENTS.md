# Repository instructions

This is a SciMigo course-content repository. Keep course-specific metadata,
readings, module definitions, labs, benchmark fixtures, and observed results
here. Do not add RoutePilot-specific content to `scimigo-learn`; that repository
is only the generic viewer.

## Evidence rules

- Label plans, hypotheses, and proposed experiments as such.
- Do not claim model quality, latency, memory, or power results without a
  committed command, environment, and raw result.
- Prefer primary sources. Paraphrase and link; do not copy source text.
- Record model and dataset licenses before using generated outputs for training
  or publishing weights.
- Keep live POI, traffic, opening-hours, and charger facts behind tools.
- Any vehicle action is a proposal. Policy and user confirmation remain outside
  the model contract.

## Verification

```bash
python3 -m unittest discover -s benchmark/tests -v
python3 -m benchmark.routepilot_eval.cli \
  benchmark/scenarios/module-01.jsonl \
  benchmark/predictions/reference.jsonl
```
