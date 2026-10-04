# Task 0002 — Data Foundation and Dataset Design

## Metadata

- Task number: 0002
- Task name: Data Foundation and Dataset Design
- Project phase: data foundation/design, following Phase 0.1
- Date: 2026-10-04 (Europe/Rome)
- Status: completed and validated; awaiting user commit/push
- Git branch: `main`, tracking `origin/main`
- Base commit: `0930b03413c36f9c3c5c4a88e8a89ad4b88d79fc`
- Environment: user-specified MacBook Pro M5; verified macOS 26.6.2 ARM64,
  Python 3.12.12, existing `.venv`; PyTorch 2.14.1, NumPy 2.5.3, pytest 9.1.1,
  Ruff 0.16.10.

## Objective

Establish permanent prompt/handoff history and decide the scientific/data
contract before implementing the pipeline. [Task specification](../prompts/0002-data-foundation.md).

## Scope

In scope: repository/history inspection, primary-source research, dataset
comparison, data design, documentation, and existing foundation validation.
Out of scope: dataset acquisition, production downloader/preprocessing, full EDA,
models, runtimes, quantization, benchmarks, simulator, deployment, and tracking.

## Changes

- Confirmed a clean starting tree and committed Phase 0.1 foundation.
- Created the development protocol, index, and this working handoff.
- Verified LHCO v5 metadata and the corrected R&D v2 filename; researched Dark
  Machines and CMS NanoAOD alternatives. Data files have not been downloaded.
- Preserved both original user specifications from available conversation context.
  Recovered Task 0001 using its commit/files and historical tool outputs, explicitly
  separating reconstructed implementation facts, historical outcomes, and current
  revalidation. No historical prompt had to be invented.
- Wrote the data-design contract and updated the two existing READMEs to mark
  selected/planned data work accurately. Left working Phase 0.1 functionality intact.
- Completed the protocol/index and final review. Nothing staged or committed.

## Files

- Modified [main README](../../README.md) and [data README](../../data/README.md).
- Created [data design](../data-design.md) and [development protocol](../development.md).
- Created [Task 0001 prompt](../prompts/0001-project-initialization.md) and
  [Task 0002 prompt](../prompts/0002-data-foundation.md).
- Created [handoff index](README.md), [Task 0001 handoff](0001-project-initialization.md),
  and this Task 0002 handoff.

Nine Markdown files in total. The existing `docs/.gitkeep` was retained; no
directory restructuring, executable functionality, configuration, or dependency
changes were needed.

## Technical Decisions

Selected pinned LHCO R&D v5 (`10.5281/zenodo.6466204`), particle-level
`events_anomalydetection_v2.h5`; black boxes and supplemental three-prong signals
are reserved. Wrote [the full design](../data-design.md): deterministic duplicate
groups and seed-1729 background split, signal embargo, shared ragged physical
records, model-specific views, NPY/JSON storage direction, 1% train/val dev subset,
provenance, and separate ML/systems boundaries. Numerical sequence length is
deferred to training-background EDA. No pipeline was implemented.

Initial model/normalizer training and validation are pure background. Background
groups use expected 70/15/15 train/validation/test fractions with independent
validation-selection/calibration roles. All two-prong signals are test-only.
Duplicate groups precede splitting/subsetting; labels/IDs never become features.
Store physical ragged triplets and derive eight aggregate features for baselines
and a compact AE, or four periodic-aware object channels plus masks for set
models. Keep every stored particle canonically; select any smaller L later using
training-background retention criteria. Preload/materialize tensors for future
inference timing and account for I/O/transfers separately.

Evidence used: [pinned R&D v5](https://zenodo.org/records/6466204) and its
[API metadata](https://zenodo.org/api/records/6466204), older R&D schema description,
official LHCO site/paper, [black-box v6](https://zenodo.org/records/4536624),
[Dark Machines hackathon](https://zenodo.org/records/3961917) and
[original paper](https://arxiv.org/html/2105.14027v3), and
[CMS JetHT NanoAOD record 30558](https://opendata.cern.ch/record/30558) with official
NanoAOD/variable documentation. The data-design document ties individual facts
to sources and lists persistent identifiers. Metadata verified licenses (LHCO/
Dark Machines CC BY 4.0; CMS record CC0), published sizes/checksums, and components.
No checksum was computed for a data file because none was retrieved.

## Dependencies

No dependencies, package source, tests, CI, or ignore rules changed. Research used
web browsing and small HTTPS metadata/documentation requests.

## Validation

Executed from the repository root on 2026-10-04:

| Command / check | Actual outcome |
| --- | --- |
| `.venv/bin/python -m pytest` | Four passed, no warnings. |
| `.venv/bin/python -m ruff check .` | All checks passed. |
| `.venv/bin/python -m ruff format --check .` | Passed. |
| `.venv/bin/python -c 'import latenttrigger; print(latenttrigger.__version__)'` | Printed 0.1.0. |
| `.venv/bin/python scripts/smoke_test.py` | Sandbox: CPU/MPS unavailable, scalar 16.0, passed. |
| Same diagnostic with sandbox escalation for GPU access | MPS available, device mps, tensor on mps:0, scalar 16.0, passed. |
| `.venv/bin/python -m pip --no-cache-dir check` | No broken requirements. |
| `git status --short --branch --untracked-files=all` | Only expected Task 0002 documentation; main tracks origin/main. |
| `git diff --check` and tracked/untracked diff review | Passed; changes confined to documentation. |
| One-off `python3.12` heredoc documentation/artifact audit | Relative links resolve; nine intended Markdown files, each under 100 KB; no data files or staged changes; HEAD/upstream unchanged; raw/processed/cache/checkpoint ignore rules hold. |

Initial status was clean. No hosted CI run, fresh installation, remote fetch, or
Python 3.11 execution was performed; those are not presented as validation here.
Current package installation/import metadata was verified in the existing `.venv`.

## Results

Development history, source comparison, selected dataset, mathematical ML task,
split/leakage policy, canonical/model-view schemas, feature/multiplicity policy,
local subset, storage direction, provenance, and benchmark boundaries are now
documented. Future acquisition/preprocessing has a concrete contract. Phase 0.1
checks still pass. The task produced no data, model, scientific measurement, or
benchmark result, and no runtime/development dependency changes.

## Issues / Limitations

File contents, HDF layout, multiplicity distribution, and numerical behavior
require later acquisition/EDA; metadata verification is not file validation.
Specifically deferred: source dtypes and unit/padding conventions, duplicate and
near-duplicate incidence, empirical tails/subset coverage, model L, float32
tolerances, reader packages, and processed shard size. The proposed GeV convention
has not been verified against a downloaded file. Generator cards are listed but
not inspected. The Dark Machines dataset.pdf request was rate-limited; counts
and format were verified from the original paper rather than that attachment.
Some web API endpoints failed, but direct official HTTPS metadata requests
succeeded; network access was sufficient for selection. Published black-box keys
exist, so later evaluation must acknowledge public answers and cannot claim
original challenge blindness. Exact archive contents remain externally unverified.

## Rejected Alternatives

Rejected LHCO black boxes as the initial tuning population, old uncorrected R&D
raw files, Dark Machines as the initial primary workload, and CMS JetHT as the
initial labeled benchmark. Rationale and authoritative source comparison are in
the data-design document. Also rejected full-dataset normalization, signal-based
model selection, arbitrary L, global dense padding, and immediate format/tooling
dependencies.

## Reproducibility

Base commit recorded above; use pinned primary dataset identifiers in the final
data-design document. No generated dataset manifest exists yet.
The design specifies source DOI/file/expected bytes and MD5, seed 1729, hash
domains/grouping and subset rules, features/units, separate roles, and required
manifest fields. Actual SHA-256/download dates belong to future acquisition.
The original prompts record requested scope; handoffs record achieved work.
To revalidate the foundation, activate the existing `.venv` and rerun the commands
in the validation table. Review relative links, both tracked/untracked diffs, and
`git check-ignore` for proposed data paths before the user commits. Small source
metadata was read into memory; no research download was saved as event data.

## Follow-up

Task 0003: verified acquisition and bounded schema/EDA audit of pinned R&D v2,
establishing split/embargo before training-background exploration. Resolve reader,
units/padding, numerical precision, multiplicity, and dev-subset/L budget.

## Git

No staging, commit, or push performed. Suggested message:
`docs: define LatentTrigger data foundation`.
Base remains `0930b03413c36f9c3c5c4a88e8a89ad4b88d79fc`; no resulting Task 0002
commit hash is recorded. `main` already has an upstream, so the user uses normal
`git push` after selective staging/review and committing all nine task documents.
