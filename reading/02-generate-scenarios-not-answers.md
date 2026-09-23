# Generate Scenarios, Not Answers

The first module froze what RoutePilot is allowed to do. That contract gives us
an unusual advantage when constructing training data: much of the answer is
executable. We do not need a language model to decide whether a closed
restaurant is feasible, whether a charger has the right connector, or which
candidate wins a declared utility function.

The tempting pipeline asks a powerful teacher to write thousands of request and
answer pairs. The safer pipeline creates a structured situation, derives its
answer with code, and asks a teacher—if one is used at all—to vary only the
surface language.

## Truth before text

A RoutePilot scenario has four layers:

1. **Context** contains facts already known to the application, such as vehicle
   connector or arrival deadline.
2. **Candidates** represent current results returned by a maps, POI, or charging
   service. In this course they are synthetic records, never claims about a real
   place.
3. **Decision rules** state hard constraints and soft utility weights, including
   where each hard value came from.
4. **Rendering** expresses some of those constraints as a driver request.

Generation follows that order. If prose comes first, an author must reverse
engineer all implied constraints and may quietly add assumptions. If structured
truth comes first, prose is one representation that can be checked against it.

```text
template + seed
      |
      v
context + candidates + policy
      |
      v
hard constraints + utility weights
      |
      +---- deterministic oracle ----> expected choice
      |
      +---- renderer/paraphraser ----> request text
```

The expected choice is never typed into the generator. The generator calls the
same oracle used by evaluation:

```python
scenario["expected_choice_id"] = expected_choice(scenario)
```

This does not make the policy correct. It guarantees the label follows the
policy that was actually declared. Reviewers can debate a 25-minute definition
of “quick,” change it, version the dataset, and observe every affected label.

## Generate candidates that test the contract

Uniform random candidates produce many boring cases. A useful template assigns
roles deliberately:

- a candidate that is feasible and strongly preferred;
- a feasible alternative so ranking has work to do;
- an attractive candidate that violates one hard constraint;
- a candidate on or just across a numerical boundary;
- for clarification families, missing context that makes a call invalid.

The attractive-but-infeasible case is essential. Without it, a model can ignore
hard constraints and still select the same option as the oracle. The feasible
alternative is equally important: without it, selection accuracy says nothing
about ranking.

Randomness can vary values inside those roles. It should not decide whether a
scenario accidentally has no feasible answer unless that is the behavior being
generated intentionally.

## Reproducibility is not coverage

The committed generator uses a local pseudorandom number generator, a recorded
seed, and a generator version. The same version and seed reconstruct the same
fixture. That makes a release inspectable and makes a changed JSONL file easy to
explain.

A reproducible dataset can still be narrow, biased, or unrealistic. A seed does
not answer:

- Which domains are present?
- Which limits appear exactly at equality?
- How many cases require clarification?
- Are constraints sourced from requests, context, and policy?
- Does one wording pattern dominate?
- Are any train examples siblings of development examples?

Those questions require a coverage report. Scenario count is only one line in
that report.

## Split the generator, not its output rows

Suppose one template produces 10,000 requests by changing cuisine names and
detour limits. A random 80/20 split puts the same syntax, candidate roles, and
field relationships in train and development. The model can learn the
generator's fingerprint rather than the product behavior.

RoutePilot assigns each `template_family` to one split before generating rows.
The first scaffold uses explicit-cuisine and explicit-connector families for
training, while arrival-deadline and context-connector families go to
development. Both splits contain food and charging behavior, but the mechanism
that constructs each example does not cross the boundary.

This is still not a final holdout. A private holdout should contain additional
families and remain unavailable to training, autonomous experiment agents, and
repeated unlimited submissions.

## Use a teacher for language, not truth

Self-Instruct demonstrated that model-generated instructions can expand
instruction-tuning data, with filtering of invalid and similar generations.
Evol-Instruct explored controlled rewriting toward more complex instructions.
These results motivate language generation, but they do not require RoutePilot
to delegate its verifiable labels.

For this task, a teacher can:

- paraphrase a canonical request;
- introduce ordinary linguistic variation;
- propose difficult but reviewable ways to state the same constraints.

A teacher must not:

- invent the tool result or live availability;
- choose the winning candidate;
- convert an unstated product policy into a supposed driver quote;
- see the private holdout;
- change a number while preserving fluent prose.

Every retained paraphrase needs a constraint-preservation check. At minimum,
compare the required typed arguments and numeric values with the rendered text
and context. Store the raw generation record, model version, sampling settings,
filter decision, and terms governing use of the output.

## Contamination begins in your own pipeline

Benchmark contamination is often discussed as an unknowable property of a
model's pretraining corpus. Course authors also control a simpler form: whether
their own train and evaluation examples overlap.

Exact-string deduplication is not enough for generated data. Two rows can differ
in every restaurant name and number while sharing the same template, candidate
roles, and solution path. Family-level splits make that relationship explicit.
Later modules should add similarity and contamination reports, but no detector
replaces a split designed before generation.

## The Module 2 artifact

The first generator deliberately stays small. Four template families produce
eight committed scenarios from seed `20260923`. The CLI validates every row
before writing it, and tests confirm:

- identical seeds produce identical structures;
- a different seed changes the release;
- every declared choice equals the oracle result;
- no family crosses train and development;
- the committed JSONL equals a fresh documented generator run.

Eight scenarios cannot train RoutePilot. They establish the machinery that a
larger release must use. Scaling comes after a coverage matrix, rights review,
and baseline measurement show which examples are worth generating.

## What comes next

Module 3 freezes prompts, model revisions, parsing behavior, and sampling
settings for base and teacher baselines. If the base model already satisfies the
contract reliably, training may not be justified. If failures cluster around
constraint extraction, clarification, or ranking, the scenario factory can
produce targeted evidence instead of an undirected pile of synthetic text.

## Sources

- Wang et al., [Self-Instruct: Aligning Language Models with Self-Generated
  Instructions](https://arxiv.org/abs/2212.10560), ACL 2023.
- Xu et al., [WizardLM: Empowering Large Language Models to Follow Complex
  Instructions](https://arxiv.org/abs/2304.12244), ICLR 2024.
- Xu et al., [Benchmark Data Contamination of Large Language Models: A
  Survey](https://arxiv.org/abs/2406.04244), 2024.
