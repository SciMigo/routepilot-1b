# Lab 2: Build a deterministic scenario factory

Run commands from the repository root with Python 3.11 or newer.

## 2.1 Reproduce the committed fixture

Generate the public Module 2 fixture into a temporary path:

```bash
python3 -m benchmark.routepilot_data.cli \
  --seed 20260923 \
  --count-per-family 2 \
  --output /tmp/routepilot-module-02.jsonl

cmp benchmark/scenarios/module-02.jsonl /tmp/routepilot-module-02.jsonl
```

`cmp` must produce no output. Explain why a seed without a generator version
would still be insufficient provenance after the code changes.

## 2.2 Audit the split boundary

Write a short Python check that groups scenarios by `template_family` and fails
if a family has more than one `split`. Confirm that both `train` and
`development` exist.

Then compare `food-explicit-cuisine` with `food-arrival-deadline`. They share a
domain but not a construction template. Explain why this is a stronger check
than randomly splitting eight rows.

## 2.3 Let the oracle own the answer

In a copy of one generated scenario, make the preferred candidate exceed its
detour limit. Run `expected_choice()` and record which candidate becomes best.
Do not edit `expected_choice_id` directly.

Regenerate the fixture and confirm your mutation disappears. Explain which file
is source—the generator or generated JSONL—and why the JSONL is still committed.

## 2.4 Add one template family

Add a deterministic family for either parking or an arrival-sensitive errand.
It must include:

- one feasible preferred candidate;
- one feasible but weaker candidate;
- one attractive candidate that violates a hard constraint;
- provenance and a note for every hard constraint;
- a split assigned at the family level;
- an oracle-derived choice.

Add tests proving that the same seed reproduces it and that the full generated
set passes `validate_scenarios()`.

## 2.5 Optional: paraphrase without relabeling

Using a teacher model of your choice, produce three rewrites of one canonical
request. Record the model, version, sampling settings, terms applicable to
retaining its output, and raw response.

For each rewrite, make a table of every required value and whether it is still
stated or recoverable from context. Reject any rewrite that drops a constraint,
changes a number, adds an unsupported preference, or turns policy into something
the driver supposedly said. Do not send candidate facts or expected labels to
the teacher; it is varying language, not solving the scenario.

## Completion check

```bash
python3 -m unittest discover -v
python3 -c "from benchmark.routepilot_eval import validate_scenario_file; \
print(validate_scenario_file('benchmark/scenarios/module-02.jsonl'))"
```

The second command must print `[]`.
