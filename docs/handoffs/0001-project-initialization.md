# Task 0001 — Project Initialization

## Metadata

- Task number: 0001
- Task name: Project Initialization
- Project phase: 0.1
- Original date: 2026-10-04; recovery/revalidation date: 2026-10-04 (Europe/Rome)
- Status: completed; resulting commit verified locally in Task 0002
- Git branch: `main`
- Base commit: none; initial directory was empty and not a Git repository
- Resulting commit: `0930b03413c36f9c3c5c4a88e8a89ad4b88d79fc`
- Environment: user-specified MacBook Pro M5; verified macOS 26.6.2 / ARM64 /
  Python 3.12.12, project `.venv`.

**Evidence provenance:** this is a retrospective handoff created during Task
0002, not a document written during the original implementation. Configuration
and file inventory below are reconstructed from Git and repository state.
Original validation outcomes are supported by the available original conversation
and tool outputs, but are historical. The separate revalidation column records
new Task 0002 checks. This file and the [preserved original prompt](../prompts/0001-project-initialization.md)
were not part of the original foundation commit.

## Objective

Establish a small maintainable Python research/software foundation for independent
hardware-aware ML studies of LHC-like event selection, initially on Apple Silicon.

## Scope

In scope: package, metadata/dependencies, lint/format tooling, tests, CPU CI,
README, license, directory/data/results policies, CPU/MPS selection, diagnostic.
Out of scope: dataset selection/download, preprocessing, anomaly models,
evaluation/benchmarks, deployment runtimes, quantization, simulator, CUDA/FPGA,
tracking, containers, and web applications.

## Changes

Reconstructed from the foundation commit: created the `src/latenttrigger` package
with version 0.1.0; Hatchling reads that single version definition. Added
`get_device() -> torch.device`, preferring available MPS and otherwise CPU.
The diagnostic reports PyTorch/device/MPS and checks a small float32 computation
whose scalar result is 16.0. It waits for completion by reading the scalar and
raises on an unexpected value.

Added mocked MPS/CPU selection tests, a real CPU tensor calculation, and execution
of the diagnostic's CPU entry point. Ruff performs linting and formatting.
GitHub Actions is configured for pushes/PRs, Python 3.11/3.12, CPU-only PyTorch,
Ruff lint/format checks, and pytest. No hosted CI success is inferred from that
configuration. Created MIT licensing and ignore rules for datasets/environments/
artifacts; curated final figures/tables have explicit future paths.

Observed original task context: local Git was initialized on `main`; Codex did
not stage, commit, or push. The user's later commit is established from Git.

## Files

`git show --stat 0930b03` verifies 18 created files:

- `.github/workflows/ci.yml`
- `.gitignore`
- `LICENSE`
- `README.md`
- `pyproject.toml`
- `configs/.gitkeep`
- `data/README.md`
- `docs/.gitkeep`
- `notebooks/exploration/.gitkeep`
- `results/benchmarks/.gitkeep`
- `results/figures/.gitkeep`
- `results/tables/.gitkeep`
- `scripts/smoke_test.py`
- `src/latenttrigger/__init__.py`
- `src/latenttrigger/utils/__init__.py`
- `src/latenttrigger/utils/device.py`
- `tests/test_device.py`
- `tests/test_smoke_test.py`

## Technical Decisions

- Recommend Python 3.12, support `>=3.11,<3.13`: conservative stable PyTorch
  macOS ARM64 support, rather than automatically choosing the newest Python.
- Hatchling/pip/venv, src layout, editable development install; no Conda need.
- Single source version 0.1.0 in the package; no release-management abstraction.
- Ruff covers both linting and formatting; pytest tests hardware-independent
  selection branches and real CPU behavior.
- Query actual MPS availability; no assumption that every ARM64 execution context
  exposes Metal, and no CUDA selection behavior introduced.
- MIT for public software; empty useful directories retained with `.gitkeep`.

## Dependencies

Verified in committed `pyproject.toml`: build backend `hatchling>=1.27,<2`;
runtime `numpy>=1.26,<3`, `torch>=2.6,<3`; development extra `pytest>=8,<10`,
`ruff>=0.11,<1`. The original context records NumPy being added to resolve a
PyTorch import-time warning. No future model/runtime stack was installed.

## Validation

All commands ran from the repository root with `.venv/bin/python`.

| Check / command | Original Task 0001 outcome (historical) | New Task 0002 revalidation |
| --- | --- | --- |
| `python -m pip install --no-cache-dir -e '.[dev]'` | Editable installation passed after network escalation and NumPy correction. | No fresh installation attempted; installed package metadata/import independently verified. |
| `python -c 'import latenttrigger; print(latenttrigger.__version__)'` | Printed 0.1.0. | Printed 0.1.0. |
| `python scripts/smoke_test.py` (sandbox) | CPU fallback, scalar 16.0, passed. | CPU fallback, scalar 16.0, passed. |
| Same diagnostic outside sandbox | PyTorch 2.14.1, MPS available, `mps:0`, scalar 16.0, passed. | Same MPS availability/computation independently reproduced. |
| `python -m ruff check .` | Passed. | Passed. |
| `python -m ruff format --check .` | Passed. | Passed. |
| `python -m pytest` | Four passed without warnings after correction. | Four passed without warnings. |
| `python -m pip --no-cache-dir check` | No broken requirements. | No broken requirements. |

Historical original installation is not presented as newly repeated. Task 0002
revalidation uses the existing environment; see its [handoff](0002-data-foundation.md)
for the current documentation audit and Git review.

## Results

The package/tooling/device foundation was implemented and committed. This enables
later work without requiring GPU-specific CI hardware. No scientific result or
dataset-selection conclusion belonged to Task 0001.

## Issues / Limitations

At original completion, no remote was configured and hosted CI had not run.
Task 0002 found `origin` configured and local `origin/main` equal to HEAD; the user
reports the push. No fresh remote fetch or hosted CI inspection was performed.
Python 3.11 is configured in CI but was not tested locally in these checks.
Sandbox GPU restrictions require distinguishing CPU fallback from real MPS access.

## Rejected Alternatives

Original scope/implementation support choosing venv/pip over Conda, Ruff over
multiple overlapping quality tools, and CPU/MPS over prematurely adding CUDA.
No additional historical debate or benchmarking rationale can be established.

## Reproducibility

The original checkout used Python 3.12.12 ARM64, PyTorch 2.14.1, NumPy 2.5.3,
pytest 9.1.1, and Ruff 0.16.10 according to original tool outputs; those versions
also match Task 0002 metadata inspection. Installation instructions and checks
remain in the main README. Dependency ranges permit updates; no lockfile or
claim of a permanently frozen environment was introduced.

## Follow-up

The original next phase was data foundation/design, now handled by Task 0002.
Future tasks must preserve this retrospective record and explicitly annotate
corrections through the development protocol.

## Git

Verified resulting commit: `0930b03413c36f9c3c5c4a88e8a89ad4b88d79fc`.
Actual message: `chore: initializatiom foundation` (preserved as committed).
Commit timestamp: 2026-10-04 09:43:41 +0200. Local HEAD and `origin/main` point
to it at Task 0002 start. Task 0001 did not automatically commit/push; this
retrospective documentation belongs in the Task 0002 commit.
