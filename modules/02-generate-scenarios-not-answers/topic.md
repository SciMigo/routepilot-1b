# Generate Scenarios, Not Answers

## Source alignment

- Self-Instruct, ACL 2023, fetched 2026-09-23:
  https://arxiv.org/abs/2212.10560
- WizardLM / Evol-Instruct, ICLR 2024, fetched 2026-09-23:
  https://arxiv.org/abs/2304.12244
- Benchmark Data Contamination of Large Language Models: A Survey, fetched
  2026-09-23:
  https://arxiv.org/abs/2406.04244

## Core concepts

- Generate the structured world before its wording: context, tool arguments,
  candidates, constraints, utility weights, and clarification requirement.
- Derive `expected_choice_id` by executing the same deterministic oracle used in
  evaluation. Neither an author nor a teacher model types the label.
- Give every hard constraint a provenance: request, context, or declared policy.
- Create boundary candidates deliberately: just inside a limit, just outside it,
  attractive but infeasible, and feasible but less preferred.
- Treat the seed as provenance. It makes a data release reproducible; it does
  not prove that the distribution is diverse or realistic.
- Split by template family before generating rows. A random row split can place
  near-identical siblings on both sides and reward memorizing generator style.
- A teacher model may paraphrase requests only after truth exists. Its output is
  retained only when a constraint-preservation check passes.
- Dataset volume is not a quality metric. Coverage, validity, duplication,
  provenance, licensing, and held-out generalization are reported separately.

## Claims and evidence

- **Documented:** Self-Instruct generates instructions and examples with a
  language model and filters invalid or similar generations. RoutePilot borrows
  the generate-and-filter idea, but keeps its task labels executable.
- **Documented:** Evol-Instruct demonstrates controlled rewriting toward more
  complex instructions. RoutePilot may later use constrained rewriting for
  wording diversity; Module 2 does not assume complexity means quality.
- **Documented:** published contamination research warns that benchmark exposure
  can inflate evaluation. RoutePilot addresses its own controllable leakage by
  assigning whole template families to one split.
- **Observed in this repository:** the committed Module 2 fixture is reproduced
  byte-for-byte by the documented seed and passes the fixture validator.
- **Proposed:** these four initial template families are representative enough
  to teach the method. They are not claimed to cover production route requests.
- **Not yet observed:** whether teacher paraphrases improve the trained student,
  how many scenarios are needed, or which coverage mix yields the best model.

## Programming and lab

1. Reproduce the committed eight-scenario fixture from its seed.
2. Show that no template family appears in both train and development.
3. Change a candidate so the oracle selects a different answer; confirm that
   regeneration restores the derived label.
4. Add a new template family with one feasible, one boundary, and one attractive
   but infeasible candidate.
5. Optionally paraphrase requests, then audit every named value and constraint
   before retaining the text.
