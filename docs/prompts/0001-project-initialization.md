# Task 0001 prompt record

Recorded on 2026-10-04 during Task 0002. The original user message is available
in the continuing task conversation and is transcribed below. This is a preserved
original specification, not a reconstructed or retroactively rewritten prompt.
The handoff is separately reconstructed from Git, files, and observed task context.

<!-- BEGIN ORIGINAL USER SPECIFICATION -->

LatentTrigger — Phase 0.1: Project Initialization

You are helping me develop LatentTrigger, an independent research and engineering project focused on hardware-aware machine learning for real-time LHC event selection.

The project will be developed incrementally. Do not attempt to implement the entire project now.

Your task in this phase is only to establish a clean, professional, maintainable project foundation.

Project context

LatentTrigger will eventually investigate the trade-off between anomaly-detection performance and computational constraints for LHC-like event selection.

The long-term project will include:

* scientific event-data preprocessing;
* anomaly-detection baselines;
* autoencoders;
* particle/set-based Transformer models;
* scientific evaluation and bias analysis;
* latency, throughput and memory benchmarking;
* heterogeneous inference;
* Apple Silicon CPU/GPU benchmarking;
* ONNX Runtime and CoreML;
* later NVIDIA CUDA/TensorRT experiments on Linux/NVIDIA hardware;
* quantization;
* a trigger-like event-stream simulator;
* optionally FPGA-oriented deployment using hls4ml.

These are future phases.

Do not implement them now.

The current development machine is a MacBook Pro with Apple Silicon M5.

The repository should therefore work cleanly on macOS/ARM64 and must not require CUDA, TensorRT, FPGA tools, or Linux-specific dependencies at this stage.

⸻

Goal of this phase

Initialize LatentTrigger as a modern Python research/software-engineering project with:

1. a proper Python package;
2. dependency and project metadata management;
3. linting/formatting configuration;
4. testing infrastructure;
5. basic CI;
6. an initial README;
7. an initial project directory structure;
8. device-detection utilities for CPU/MPS;
9. a minimal smoke test proving that the environment works on Apple Silicon.

Do not add unnecessary complexity.

⸻

Project naming

Use these names consistently:

Project name:

LatentTrigger

Repository name:

latent-trigger

Python package:

latenttrigger

Do not use the old name TriggerBench anywhere.

⸻

Python version

Choose a stable Python version compatible with the current PyTorch/macOS Apple Silicon ecosystem.

Do not blindly choose the newest Python release.

Before configuring the project, determine a sensible supported Python range and briefly explain your choice in the final summary.

Use modern Python packaging through pyproject.toml.

Avoid Conda unless there is a concrete technical reason for requiring it.

⸻

Initial repository structure

Create a clean structure approximately like this:

latent-trigger/
├── .github/
│   └── workflows/
├── configs/
├── data/
│   └── README.md
├── docs/
├── notebooks/
│   └── exploration/
├── results/
│   ├── figures/
│   ├── tables/
│   └── benchmarks/
├── scripts/
├── src/
│   └── latenttrigger/
│       ├── __init__.py
│       └── utils/
├── tests/
├── .gitignore
├── LICENSE
├── README.md
└── pyproject.toml

You may make small changes if there is a strong software-engineering reason, but explain them.

Do not create large numbers of empty placeholder Python files for functionality that does not exist yet.

Empty directories that Git would otherwise ignore may use .gitkeep only when retaining the directory is useful.

⸻

Python package

Configure src/latenttrigger as an installable Python package.

The following should eventually work from the project environment:

python -c "import latenttrigger; print(latenttrigger.__version__)"

Define a project version following semantic versioning.

For this initial development stage, use an appropriate 0.x version.

Keep version management simple.

⸻

Dependencies

For this phase, install only dependencies genuinely needed for the foundation and smoke test.

We will eventually need libraries such as PyTorch, NumPy, pandas, scikit-learn, plotting libraries, ONNX, etc., but do not install the entire future stack preemptively.

PyTorch may be included now because we want to verify CPU/MPS device detection on the M5.

Separate runtime and development dependencies appropriately.

Development tooling should include at least:

* pytest;
* a modern linter/formatter such as Ruff.

Avoid adding multiple tools that perform the same job unless necessary.

⸻

Apple Silicon / MPS support

Implement a small reusable device utility under an appropriate module such as:

src/latenttrigger/utils/device.py

It should detect available PyTorch execution devices with the following priority:

1. MPS when available;
2. CPU otherwise.

Do not add CUDA-specific behavior yet unless keeping the utility future-compatible requires only a trivial and clean abstraction.

The code must not assume that MPS is always available.

Expose a simple function such as:

get_device()

with appropriate type hints and documentation.

⸻

Smoke test

Create a minimal executable smoke test or diagnostic script that:

1. imports PyTorch;
2. reports the PyTorch version;
3. reports the detected device;
4. reports whether MPS is available;
5. creates a small tensor;
6. moves it to the selected device;
7. performs a trivial tensor operation;
8. confirms successful execution.

Keep this diagnostic lightweight.

It must not download any dataset or train any model.

If appropriate, place it under scripts/.

⸻

Tests

Create meaningful tests for the functionality introduced in this phase.

At minimum, test the device-selection logic in a way that does not make CI depend on Apple MPS hardware.

The tests should run successfully on a normal CPU-only GitHub Actions runner.

Avoid tests that simply assert trivial constants.

Run the tests before considering the task complete.

⸻

Code quality

Use:

* Python type hints;
* concise docstrings where useful;
* clear naming;
* simple modular design;
* Ruff for linting/formatting;
* pytest for testing.

Do not overengineer abstractions for functionality that does not exist yet.

Configure these tools in pyproject.toml where appropriate.

⸻

GitHub Actions

Create a minimal CI workflow that runs on pushes and pull requests.

It should:

1. check out the repository;
2. install the supported Python version;
3. install the project and development dependencies;
4. run Ruff;
5. run pytest.

Do not add deployment, Docker builds, GPU jobs, code coverage services, or other infrastructure yet.

Keep CI fast.

⸻

.gitignore

Create a comprehensive but reasonable .gitignore suitable for:

* Python;
* macOS;
* virtual environments;
* IDE metadata;
* pytest/cache files;
* generated results;
* local datasets;
* model checkpoints;
* experiment artifacts.

Be careful not to ignore source files or documentation that should be version controlled.

Large datasets must never be committed.

⸻

Data policy

Create data/README.md explaining that:

* datasets are not committed to Git;
* data/raw/ will contain downloaded source data;
* data/processed/ will contain derived/preprocessed data;
* future scripts will provide reproducible download/preparation procedures.

Configure .gitignore accordingly.

Do not choose or download the LHC dataset in this phase.

That decision belongs to the next data-design phase.

⸻

Results policy

Generated benchmark results, temporary outputs, model checkpoints and large experiment artifacts should not accidentally enter Git.

However, the repository will eventually contain selected final figures and small result tables used in the README/documentation.

Design .gitignore so that this distinction can be maintained cleanly later.

Do not generate fake results.

⸻

README

Create an initial professional README.md.

It should include:

LatentTrigger

Subtitle:

Hardware-Aware Machine Learning for Real-Time LHC Event Selection

Explain clearly that this is an independent research and engineering project inspired by the computational challenges of real-time event selection at the LHC.

Do not imply that LatentTrigger is an official CERN, ATLAS, CMS, or CERN openlab project.

Include concise sections for:

* Motivation;
* Research question;
* Project scope;
* Planned methodology;
* Current status;
* Repository structure;
* Installation;
* Apple Silicon / MPS diagnostic;
* Testing;
* Roadmap;
* Disclaimer.

Use the following central research question:

How much anomaly-detection performance can be retained when machine-learning models are optimized for real-time LHC event selection under strict computational constraints?

The roadmap should indicate future work at a high level without claiming that unimplemented features already exist.

Use checkboxes or another clear mechanism to distinguish completed from planned functionality.

Do not include fabricated benchmark numbers, results, badges, affiliations, citations, or claims.

⸻

License

Add an appropriate permissive open-source license suitable for a public research/software portfolio project.

A standard MIT license is acceptable unless you identify a concrete reason to choose differently.

⸻

Documentation

Do not write extensive documentation yet.

The README is sufficient for this phase.

The docs/ directory may remain minimal until methodology and benchmarking are implemented.

⸻

Validation

Before finishing, actually inspect and validate the project.

At minimum:

1. install the package in the development environment;
2. verify import latenttrigger;
3. run the diagnostic/smoke test;
4. run Ruff;
5. run pytest;
6. inspect git status;
7. check that datasets, virtual environments, caches and generated artifacts would not accidentally be committed.

Fix any problems you encounter.

Do not report a command as successful unless you actually ran it successfully.

If something cannot be executed because of the environment, state exactly what could not be validated and why.

⸻

Scope discipline

This phase is intentionally small.

Do NOT:

* download CERN/LHC datasets;
* implement preprocessing;
* implement PCA;
* implement an autoencoder;
* implement a Transformer;
* implement anomaly detection;
* add ONNX;
* add CoreML conversion;
* add TensorRT;
* add CUDA dependencies;
* add hls4ml;
* implement quantization;
* implement the trigger simulator;
* add experiment tracking;
* add Docker;
* build a dashboard;
* add a web application;
* fabricate benchmark results.

Those belong to later phases.

Prioritize a clean foundation over feature count.

⸻

Final response requirements

When you finish, provide a concise but complete report containing:

1. What was implemented

Summarize the work completed in this phase.

2. Project structure

Show the resulting relevant directory tree.

3. Technical decisions

Briefly explain important choices such as:

* Python version/range;
* dependency management;
* linting/formatting;
* test strategy;
* Apple Silicon/MPS handling;
* license choice.

4. Validation results

Report the actual results of:

* package installation;
* import check;
* device diagnostic;
* Ruff;
* pytest.

Do not invent successful results.

5. Files changed

List the files created or modified.

6. Issues or limitations

Mention anything that could not be validated or anything I should know before continuing.

7. Git commit and push commands

This section is mandatory for this phase and every future LatentTrigger development phase.

Do NOT commit or push automatically unless I explicitly ask you to.

At the end of your response, provide the exact shell commands I should run to review the changes, stage them, commit them, and push them to the GitHub repository.

The commands should follow this general workflow:

git status
git diff
git add <appropriate files>
git status
git commit -m "<specific conventional commit message>"
git push

Use an appropriate, specific commit message for the work actually completed.

Prefer Conventional Commits such as:

chore:
feat:
fix:
test:
docs:
refactor:
perf:

Do not blindly use git add . if there are unrelated or potentially unsafe untracked files. Explicitly stage the files created or modified by this task whenever practical.

If this is the first push and the current branch has no upstream, provide:

git push -u origin <current-branch>

instead of plain git push.

Determine the current branch when possible rather than assuming main.

If no Git repository or GitHub remote exists yet, detect that and give me the exact commands needed to initialize Git and/or configure the remote, but do not invent my GitHub username or repository URL.

This Git section must be the last section of your response so I can always find the commands easily.

⸻

Before modifying files, inspect the current working directory and existing repository state so you do not overwrite existing work accidentally.

Proceed with Phase 0.1 only.

<!-- END ORIGINAL USER SPECIFICATION -->

