# Authoring and evidence policy

## Separate product facts from course hypotheses

The course uses three evidence labels:

- **Documented** — supported by a linked primary source.
- **Observed** — produced by a committed, reproducible experiment in this repo.
- **Proposed** — a design choice or experiment that has not yet been measured.

The 1B-class model, synthetic-data volume, fine-tuning recipe, quantization
format, and edge latency are proposed until experiments make them observed.

## Data and model gates

Before generating training data, add a data card that records:

1. the teacher model and exact terms that permit the intended use of outputs;
2. the prompt and filtering pipeline;
3. whether user or production data is excluded;
4. personally identifying and location-data handling;
5. the license for every base model, dataset, and published artifact.

Source and model licenses are recorded in `reading/_sources/manifest.json`.
Each entry carries a `licenseStatus`: `documented` means the license was read
from the linked primary source, `unverified` means it has not been checked.
An `unverified` entry is safe to paraphrase and link, but it is not evidence
of a right to train on or redistribute anything.

If those rights are ambiguous, do not train or publish weights from the data.

## Safety boundary

RoutePilot may propose a search, rank candidates, or suggest a route stop. It
does not actuate the vehicle, silently alter navigation, or override a driver.
Applications integrating it must enforce policy, distraction controls, and
confirmation outside the model.

## Generated artifacts

Markdown under `reading/` is source. Generated HTML, lecture bundles, and audio
are build artifacts and must be reproducible. Pin the renderer and syntax
highlighter versions before committing generated HTML so rebuilds are no-ops.

`tools/build_pages.py` is that renderer, pinned by `requirements-build.txt`.
It builds `reading/NN-slug.html` from each reading and
`reading/lab-NN-slug.html` from each `modules/NN-slug/lab.md`; rebuild after
editing either, commit the output, and confirm `python tools/build_pages.py
--check` exits 0. A module manifest still points at the Markdown source. A manifest must not reference a build artifact that nothing in the
repository produces: a path that resolves to nothing is worse than a path to
the source, because it fails only at view time.
