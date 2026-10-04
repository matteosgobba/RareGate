# Task 0002 prompt record

Date: 2026-10-04 (Europe/Rome). Source: original user message in this task.
The task specification is transcribed below; this record does not describe
implementation or validation outcomes. See the separate handoff for those.

<!-- BEGIN ORIGINAL USER SPECIFICATION -->

LatentTrigger — Task 0002: Data Foundation and Dataset Design

You are continuing development of LatentTrigger, an independent research and engineering project for hardware-aware machine learning applied to real-time LHC event selection.

The repository already contains the completed Phase 0.1 foundation and has been committed and pushed to GitHub.

Do not rebuild or restructure working Phase 0.1 functionality without a concrete reason.

This task has two purposes:

1. establish the permanent prompt/handoff development-history system;
2. make and document the scientific/data-design decisions required before implementing the data pipeline.

This is primarily a research/design/documentation task, not a feature implementation task.

Do not download large datasets or implement the full preprocessing pipeline yet.

⸻

0. Inspect the repository first

Before changing anything:

* inspect the repository structure;
* inspect README.md;
* inspect pyproject.toml;
* inspect .gitignore;
* inspect data/README.md;
* inspect existing tests;
* inspect the current Git status;
* identify the current branch;
* identify the current HEAD commit;
* confirm that Task 0001 / Phase 0.1 is committed;
* do not overwrite existing work.

If the working tree contains unrelated uncommitted changes, do not silently modify or stage them.

⸻

1. Establish the permanent development-history system

Create:

docs/
├── development.md
├── prompts/
│   ├── 0001-project-initialization.md
│   └── 0002-data-foundation.md
└── handoffs/
    ├── README.md
    ├── 0001-project-initialization.md
    └── 0002-data-foundation.md

Use sensible filenames if the repository already contains a conflicting structure.

⸻

2. Recover Task 0001 history

Task 0001 was the initial project foundation.

Reconstruct its historical record from:

* Git history;
* current repository state;
* Phase 0.1 files;
* tests;
* project configuration;
* any available task context.

Create:

docs/handoffs/0001-project-initialization.md

It should record, as accurately as can be verified:

* objective;
* scope;
* files created;
* package initialization;
* Python compatibility decision;
* Hatchling/pip packaging;
* runtime/development dependencies;
* Ruff;
* pytest;
* GitHub Actions;
* Apple MPS/CPU device detection;
* smoke test;
* validation outcomes that can still be verified;
* limitations;
* resulting commit where it can be determined from Git history.

Do not invent historical facts that cannot be established.

Clearly label anything reconstructed from repository state rather than directly observed during the original task.

The Phase 0.1 validation reportedly included:

* editable installation passed;
* package import returned version 0.1.0;
* PyTorch MPS was available on the Apple Silicon development machine;
* tensor computation succeeded;
* CPU fallback succeeded;
* Ruff lint passed;
* Ruff formatting passed;
* pytest reported 4 passing tests;
* dependency consistency check reported no broken requirements.

Verify what can still be verified locally. Historical results that cannot be independently reproduced now should be identified as historical rather than presented as newly validated.

⸻

3. Preserve the Task 0001 prompt

Create:

docs/prompts/0001-project-initialization.md

The exact original prompt may not be available inside the repository.

If the exact prompt is unavailable, do NOT fabricate a verbatim historical prompt.

Instead create a clearly labelled reconstructed task specification based on the implemented Phase 0.1 scope and state explicitly that it is a reconstructed record.

The record should capture the original intent sufficiently for future maintainers to understand Task 0001.

⸻

4. Record this task

Create:

docs/prompts/0002-data-foundation.md

containing this task specification.

Create:

docs/handoffs/0002-data-foundation.md

and update it throughout the task with the actual work performed and decisions made.

⸻

5. Handoff format

Each handoff should contain, where applicable:

Metadata

* Task number
* Task name
* Project phase
* Date
* Status
* Git branch
* Base commit
* Environment

Objective

Scope

Include both in-scope and explicitly out-of-scope work.

Changes

Files

Technical Decisions

Dependencies

Validation

Results

Issues / Limitations

Rejected Alternatives

Reproducibility

Follow-up

Git

For Task 0002, do not invent a resulting commit hash before the commit exists.

Record the base commit and suggested commit message instead.

⸻

6. Handoff index

Create:

docs/handoffs/README.md

as the chronological project-development index.

Include Task 0001 and Task 0002.

Each entry should contain:

* task number;
* title;
* phase;
* status;
* concise description;
* relative link to handoff.

This index must be maintained by every future development task.

⸻

7. Development protocol

Create:

docs/development.md

formalizing the LatentTrigger development workflow.

Document at least:

inspect
→ plan
→ implement/research
→ test/validate
→ document handoff
→ review Git diff
→ user commits
→ user pushes

State that:

* each operational Codex task gets a sequential task number;
* each task has a prompt record;
* each task has a handoff;
* historical handoffs should not be silently rewritten;
* implementation, validation and planning must be distinguished;
* Codex must not automatically commit or push unless explicitly instructed;
* every task must end with exact Git review/stage/commit/push commands;
* handoff and prompt files belong in the same commit as the work they document;
* generated data/results should not be committed unless intentionally curated;
* decisions that affect future phases must include rationale.

Keep this document concise and operational.

⸻

8. Scientific goal of the data-design work

The central LatentTrigger research question is:

How much anomaly-detection performance can be retained when machine-learning models are optimized for real-time LHC event selection under strict computational constraints?

The data foundation must support future comparison between:

* simple statistical anomaly-detection baselines;
* compact autoencoders;
* particle/set-based neural architectures;
* later hardware-aware optimized versions of those models.

The dataset must therefore allow meaningful event-level anomaly detection while remaining feasible for an independent project developed initially on a MacBook Pro M5.

⸻

9. Evaluate candidate datasets

Before selecting a dataset, evaluate credible public datasets suitable for this project.

At minimum, investigate:

LHC Olympics 2020 / Dark Machines-style anomaly-detection data

Evaluate whether the LHC Olympics 2020 dataset, especially the R&D dataset and/or black-box datasets, is suitable as the primary benchmark.

Investigate authoritative sources for:

* dataset provenance;
* licensing/access;
* event representation;
* features;
* number of events;
* approximate storage requirements;
* background/signal composition;
* labels or hidden labels;
* intended anomaly-detection use;
* citation/DOI;
* practical download method.

CERN Open Data alternatives

Evaluate at least one plausible CERN Open Data dataset that could support event-level ML/anomaly detection.

Consider the trade-off between:

* realism;
* experiment provenance;
* preprocessing complexity;
* storage;
* software dependencies;
* suitability for an independent ML systems benchmark.

Other credible HEP anomaly-detection datasets

If another established public benchmark is materially better for LatentTrigger, evaluate it as well.

Do not add candidates merely to make the comparison longer.

⸻

10. Use authoritative sources

For dataset facts, prioritize:

1. official dataset repositories;
2. CERN Open Data;
3. Zenodo records associated with the benchmark;
4. official benchmark documentation;
5. original papers.

Avoid relying on random tutorials, Kaggle mirrors or secondary blog posts for foundational dataset decisions.

Record references and persistent identifiers/DOIs where available.

Do not fabricate URLs, DOIs, dataset sizes or event counts.

If network access is unavailable in the Codex environment, state this clearly.

In that case, distinguish:

* facts verified from available repository/environment sources;
* facts that require external verification.

Do not present uncertain external facts as verified.

⸻

11. Dataset-selection criteria

Evaluate candidates explicitly against:

Scientific relevance

Does the dataset represent a meaningful HEP anomaly-detection problem?

Trigger relevance

Can events reasonably be treated as independent units arriving in a trigger-like stream?

Representation

Can the data support particle/object-level models rather than only flat tabular classification?

Unsupervised/semi-supervised suitability

Can models learn primarily from background events and be evaluated against injected/known anomalies?

Scale

Is the dataset large enough to make throughput and streaming benchmarks meaningful?

Local feasibility

Can a useful subset be developed and tested on the M5 without requiring enormous local storage or memory?

Reproducibility

Can another researcher obtain and reconstruct the benchmark?

Model compatibility

Can the representation support both simple baselines and future Transformer/set architectures?

Hardware benchmarking

Can a deterministic/preprocessed representation later be fed repeatedly into inference benchmarks without I/O dominating the measurement?

⸻

12. Select one primary dataset

Make a clear recommendation for the primary LatentTrigger dataset.

Do not leave the decision as:

several datasets could work.

Choose one unless external information is genuinely insufficient to make a responsible decision.

Document:

* why it was selected;
* why alternatives were rejected;
* which exact dataset component(s) should be used;
* which component should be used for initial development;
* which component(s) may be reserved for later validation.

If LHC Olympics is selected, be precise about whether LatentTrigger should initially use:

* the R&D dataset;
* one or more black boxes;
* both, but for different purposes.

⸻

13. Define the ML task formally

Write a data-design document:

docs/data-design.md

Define the initial anomaly-detection problem mathematically.

Use notation such as:

[
X = {x_1,\ldots,x_N}
]

for an event containing reconstructed objects/particles.

Define, based on the actual selected dataset:

* event representation;
* per-object features;
* variable event length;
* labels, if available;
* background distribution;
* signal/anomaly distribution;
* training population;
* validation population;
* test population.

The intended paradigm should preferably be:

[
\text{train primarily on background}
]

and then evaluate:

[
\text{background vs unseen/held-out anomaly}
]

but adapt this if the selected benchmark requires a more scientifically correct protocol.

⸻

14. Avoid data leakage

Explicitly design protections against leakage.

Consider:

* duplicated events;
* using test labels during model selection;
* normalization fitted on the full dataset;
* signal contamination;
* preprocessing statistics;
* hyperparameter tuning against final test anomalies;
* black-box labels or benchmark answers.

Define which statistics may be learned from:

* training data;
* validation data;
* test data.

The final test set must remain genuinely held out.

⸻

15. Dataset split strategy

Define a deterministic initial split strategy.

Specify:

* train;
* validation;
* test;
* random seed;
* whether splitting is stratified;
* whether signal is allowed in training;
* how anomalies are allocated.

Do not implement the split yet unless a tiny pure utility is necessary to validate the design.

The split strategy must support future reproducibility.

If the benchmark provides an official split or intended protocol, prefer respecting it and explain why.

⸻

16. Representation strategy

This decision is particularly important.

Determine how events should eventually be represented for:

simple baseline

A fixed-dimensional event-level representation.

autoencoder

A representation that is simple enough for a compact hardware-oriented model.

particle/set model

A variable-length or padded/masked object representation.

Do not prematurely force every model to consume exactly the same tensor if that would be scientifically inappropriate.

However, avoid building unrelated pipelines that make model comparison impossible.

Design a shared canonical processed-event representation from which model-specific views can later be derived.

⸻

17. Feature policy

For every selected raw feature, document:

* physical meaning;
* units where known;
* expected range where known;
* whether transformation is likely needed;
* whether normalization will be required;
* whether the feature is periodic.

Pay particular attention to angular variables such as:

[
\phi
]

where naïve numerical treatment can introduce discontinuities around (-\pi/\pi).

Do not implement transformations yet, but document the intended handling.

Also identify any categorical/object-type features and how they may eventually be encoded.

⸻

18. Variable-length events

Design how variable particle/object multiplicity will be handled.

Consider:

* padding;
* masks;
* truncation;
* maximum sequence length;
* ordering;
* permutation invariance;
* impact on latency.

Do not arbitrarily choose a truncation threshold without inspecting or citing the dataset distribution.

If the exact threshold requires EDA, explicitly defer the numerical choice to the EDA task.

Document the decision rule that will later be used.

⸻

19. Canonical processed-data schema

Design the intended processed-event schema.

For example, conceptually:

event_id
objects:
    features: [N, F]
    mask: [N]
event_features: [...]
label:
    background / signal
metadata:
    source
    split

This is illustrative only.

Choose a schema appropriate to the actual selected dataset.

The schema should eventually support:

* PyTorch loading;
* baseline feature derivation;
* Transformer/set input;
* repeated hardware benchmarking;
* provenance;
* deterministic splits.

Do not implement a heavyweight storage format yet.

⸻

20. Processed storage-format decision

Evaluate appropriate formats such as:

* Parquet;
* HDF5;
* NumPy arrays;
* memory-mapped arrays;
* another justified format.

Consider:

* variable-length data;
* storage efficiency;
* loading speed;
* interoperability;
* reproducibility;
* later inference benchmarking.

Choose an intended direction if enough information is available.

If EDA is required before deciding, explicitly identify the decision as deferred rather than guessing.

Do not add a large dependency just to support a format that is not yet implemented.

⸻

21. Separate ML evaluation from systems benchmarking

Document a crucial methodological distinction.

ML evaluation

May include the complete preprocessing/data-loading path where scientifically appropriate.

Inference benchmarking

Must later isolate model/runtime performance from disk/network I/O.

We will eventually benchmark preloaded/preprocessed tensors so that:

[
\text{measured latency}
\neq
\text{dataset download/read latency}
]

Define future benchmark boundaries conceptually now.

This is important for the scientific validity of LatentTrigger.

⸻

22. Initial local development subset

The full benchmark may be too large for rapid iteration.

Define a reproducible development subset strategy for the M5.

It must:

* preserve relevant distributions as much as practical;
* be deterministic;
* be large enough to expose data-pipeline problems;
* be small enough for fast iteration;
* never be confused with the final benchmark.

Give it an explicit conceptual name such as:

dev subset

and document that final reported ML results must use the proper evaluation dataset rather than this convenience subset.

Do not choose arbitrary sample counts unless justified by known dataset scale.

⸻

23. Data provenance

Design a future provenance mechanism.

At minimum, processed datasets should eventually record:

* source dataset;
* source version/DOI;
* download date where appropriate;
* file hashes;
* preprocessing version;
* preprocessing configuration;
* split seed;
* code version/commit where practical.

Do not build an elaborate metadata database.

A simple reproducible manifest design is preferable.

⸻

24. Update data/README.md

Update the existing data README to reflect the selected design while maintaining the rule that datasets are not committed.

It should eventually guide a developer through the intended structure:

data/
├── raw/
├── processed/
└── ...

but do not claim that download/preprocessing scripts already exist.

Clearly distinguish planned commands from implemented commands.

⸻

25. Update the main README

Make only necessary updates.

Add the selected dataset and data-design status to the roadmap/current-status section.

Do not make the README excessively long.

Link to:

docs/data-design.md

for details.

Do not claim that the dataset has been downloaded or preprocessing implemented.

⸻

26. No implementation creep

This task must NOT:

* download the full dataset;
* commit data;
* implement the production downloader;
* implement preprocessing;
* perform full EDA;
* train models;
* implement PCA;
* implement autoencoders;
* implement Transformers;
* implement ONNX;
* implement CoreML;
* implement quantization;
* implement benchmarks;
* implement the trigger simulator;
* add CUDA/TensorRT;
* add hls4ml;
* add Docker;
* add experiment tracking.

The output of this task should make the next implementation tasks safer and more precise.

⸻

27. Validation

Before completing the task:

* run existing tests;
* run Ruff lint;
* run Ruff formatting/check;
* verify package import still works;
* verify the smoke test still works;
* verify Git status;
* inspect the final diff;
* ensure documentation links are valid relative paths;
* ensure no dataset or large generated file has entered Git;
* ensure no existing Phase 0.1 functionality was accidentally broken.

If documentation changes do not require dependency changes, do not modify dependencies unnecessarily.

⸻

28. Definition of done

Task 0002 is complete only when:

* development-history protocol exists;
* Task 0001 history has been reconstructed responsibly;
* Task 0002 prompt/handoff exists;
* handoff index exists;
* development workflow is documented;
* credible datasets have been compared;
* one primary dataset has been selected, or a clearly justified verification blocker is documented;
* anomaly-detection task is formally defined;
* split/leakage policy is defined;
* event representation strategy is defined;
* canonical processed-data design is defined;
* local-development subset strategy is defined;
* provenance strategy is defined;
* docs/data-design.md exists;
* README/data README reflect the decision;
* existing tests and quality checks still pass.

⸻

29. Mandatory handoff protocol

Before finishing, update:

docs/handoffs/0002-data-foundation.md

with the actual final state.

Record facts, not intentions.

Specifically record:

* selected dataset;
* evidence/source used;
* rejected alternatives;
* unresolved questions;
* design decisions;
* files changed;
* validation commands;
* actual validation outcomes;
* any external facts that could not be verified;
* next recommended task.

Update:

docs/handoffs/README.md

accordingly.

Historical Task 0001 records must not be silently rewritten in future tasks.

⸻

30. Final response format

Your final response must contain:

1. What was done

2. Dataset decision

State the selected primary dataset clearly.

3. Data protocol

Summarize training/validation/test and leakage decisions.

4. Representation decision

Summarize canonical event representation and model-specific views.

5. Development-history system

Confirm prompt/handoff files and index.

6. Validation results

Report actual outcomes.

7. Files changed

8. Open issues / deferred decisions

9. Recommended next task

Recommend only the immediate next development step.

10. Git commit and push commands

This section is mandatory and MUST be the final section.

Do not commit or push automatically.

Provide exact commands to:

1. inspect status;
2. inspect the diff;
3. selectively stage only Task 0002 files;
4. inspect staged changes;
5. commit;
6. push.

Use a specific Conventional Commit message appropriate to the completed task.

Prefer something along the lines of:

docs: define LatentTrigger data foundation

but adjust it if another message more accurately describes the actual work.

Determine the current branch rather than assuming main.

If an upstream already exists, use normal git push.

Do not stage unrelated files.

⸻

Proceed with Task 0002 only.

<!-- END ORIGINAL USER SPECIFICATION -->

