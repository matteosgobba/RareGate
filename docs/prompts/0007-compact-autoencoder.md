# LatentTrigger — Task 0007: Compact Autoencoder Baseline

You are continuing development of **LatentTrigger**.

Tasks 0001–0006 are complete and committed.

Task 0006 established:

- the PCA reconstruction baseline;
- the common anomaly-score convention;
- background-only validation;
- threshold calibration;
- reusable signal-aware metrics;
- a formal test embargo;
- a future explicit test-unblinding gate.

Read before modifying anything:

- `docs/development.md`
- `docs/evaluation-protocol.md`
- `docs/pca-baseline.md`
- `docs/preprocessing-contract.md`
- `docs/preprocessing-pipeline.md`
- `docs/handoffs/0006-pca-baseline.md`
- `configs/models/pca_baseline.json`
- relevant model/evaluation/data source code.

This is:

**Task 0007 — Compact Autoencoder Baseline**

The purpose is to implement the first neural anomaly detector while preserving the exact scientific discipline introduced in Task 0006.

The autoencoder must be:

- compact;
- deterministic where practical;
- hardware-friendly;
- trained exclusively on background;
- selected without signal information;
- evaluated on background-only development populations;
- compatible with the existing evaluation framework.

Do NOT implement particle Transformers, ONNX, CoreML, quantization, latency benchmarking, or test-signal evaluation in this task.

---

# 0. Mandatory repository inspection

Before modifying anything:

- inspect Git status;
- identify current branch and HEAD/base commit;
- verify Tasks 0001–0006 are committed;
- inspect `docs/evaluation-protocol.md`;
- inspect PCA model and evaluation APIs;
- inspect processed-data reader guards;
- inspect exact baseline feature order;
- verify the full processed store;
- inspect current PyTorch/device utilities;
- inspect dependency versions;
- inspect result/artifact policies.

Do not modify unrelated work.

Follow the permanent LatentTrigger prompt/handoff protocol.

---

# 1. Task records

Create:

```text
docs/prompts/0007-compact-autoencoder.md
docs/handoffs/0007-compact-autoencoder.md
```

Update:

`docs/handoffs/README.md`

Preserve all previous task records.

---

# 2. Preserve the real-test embargo

Task 0007 MUST NOT inspect model performance, score distributions, AUC, AP, signal efficiency or background rejection on:

```text
test_background
test_signal
```

Do not request explicit test access.

Allowed real populations are:

```text
train_background
validation_selection_background
validation_calibration_background
```

The deterministic development subset may also be used for implementation validation.

The autoencoder must be developed without knowledge of real signal performance.

---

# 3. Scientific comparison

The intended comparison is:

\[
\text{PCA}
\quad vs \quad
\text{Compact Autoencoder}
\]

Both consume the exact same frozen eight-dimensional standardized aggregate representation.

This isolates the effect of introducing nonlinear representation learning.

Do not modify the feature representation in order to improve autoencoder results.

Do not add extra engineered features.

---

# 4. Autoencoder input

Use the exact standardized eight-feature vector produced by the existing preprocessing pipeline.

Inspect and validate the feature order from the repository.

The model must receive:

\[
x \in \mathbb{R}^8
\]

and reconstruct:

\[
\hat{x} \in \mathbb{R}^8
\]

Labels, split identity and event IDs must never enter the model input.

---

# 5. Freeze one compact architecture

Do NOT perform architecture search in Task 0007.

Use one preregistered compact architecture.

Use the following default unless repository constraints reveal a concrete technical problem:

```text
Input:   8
         ↓
Linear:  8 → 6
ReLU
         ↓
Linear:  6 → 3
         ↓
latent z ∈ R^3
         ↓
Linear:  3 → 6
ReLU
         ↓
Linear:  6 → 8
         ↓
Output
```

The output layer must be linear.

Do not use:

- BatchNorm;
- Dropout;
- residual blocks;
- attention;
- convolution;
- stochastic latent variables.

The model is intentionally small.

If the exact architecture must be changed for a concrete reason, document the deviation before running the full training experiment.

---

# 6. Why the architecture is intentionally small

The purpose is not to maximize capacity.

This model should establish a hardware-friendly nonlinear baseline that can later be:

- benchmarked on CPU/MPS;
- exported;
- quantized;
- potentially mapped to FPGA-oriented tooling.

Keep the parameter count explicitly reported.

The architecture should be understandable at a glance.

---

# 7. Loss and anomaly score

Train using reconstruction mean squared error over the eight standardized input features.

For optimization, a batch mean is appropriate.

For per-event anomaly scoring, use:

\[
s(x)
=
\sum_{j=1}^{8}
(x_j-\hat{x}_j)^2
\]

so that the score semantics match the PCA reconstruction baseline as closely as possible.

Universal LatentTrigger convention remains:

\[
\text{larger score}
\Rightarrow
\text{more anomalous}
\]

Do not normalize the anomaly score using signal information.

---

# 8. Canonical training device

The **canonical scientific model must be trained on CPU** unless inspection reveals a strong reason this is impractical.

Reason:

- the network is tiny;
- the data representation is small;
- CPU training is expected to be fast enough;
- deterministic reproducibility is easier to establish;
- the frozen scientific model should not depend on MPS-specific numerical behavior.

MPS compatibility should still be tested separately.

Do not use MPS-trained weights as the canonical model merely because MPS is available.

---

# 9. MPS compatibility

After the canonical CPU pipeline works, perform a bounded MPS compatibility run.

This is NOT a hardware benchmark and must not be presented as one.

The MPS check should establish that:

- the model can move to MPS;
- batches can be trained;
- loss remains finite;
- inference works;
- anomaly scores are finite.

It is acceptable for CPU and MPS training trajectories not to be bit-identical.

Do not choose the scientific model based on which device produces better validation loss.

---

# 10. Reproducibility

Set and record all relevant random seeds.

Use deterministic PyTorch behavior where supported and practical.

The canonical CPU run should be repeatable.

Record:

- Python seed;
- NumPy seed;
- PyTorch seed;
- deterministic-algorithm settings;
- DataLoader shuffling behavior if used;
- initialization method.

If an operation prevents full determinism, document it explicitly.

---

# 11. Frozen training configuration

Create a tracked configuration such as:

```text
configs/models/compact_autoencoder.json
```

Freeze one training configuration before the canonical full run.

A reasonable starting specification is:

```text
architecture:
  input_dim: 8
  encoder_hidden: 6
  latent_dim: 3
  decoder_hidden: 6
  activation: relu

training:
  optimizer: adam
  learning_rate: 0.001
  batch_size: 4096
  max_epochs: 200
  early_stopping_patience: 15
  min_delta: 0.0
  seed: 1729
```

Use JSON according to existing project conventions.

You may adjust exact engineering parameters before the full canonical run if necessary for correctness or resource feasibility, but:

- do not use signal information;
- document the reason;
- do not conduct a broad hyperparameter search.

Once the canonical run starts, treat the configuration as frozen.

---

# 12. Training populations

Use:

`train_background`

for gradient-based training.

Use:

`validation_selection_background`

for early stopping / background-only generalization monitoring.

Do NOT use:

`validation_calibration_background`

for early stopping or model selection.

That population remains reserved for threshold calibration.

Do not train on the dev subset for the final canonical model.

The dev subset is only for implementation checks.

---

# 13. Early stopping

Use background validation reconstruction loss.

Store the model state corresponding to the best allowed validation epoch.

Document:

- best epoch;
- training loss at that epoch;
- validation loss at that epoch;
- stopping epoch;
- patience behavior.

Do not examine signal performance when selecting the epoch.

---

# 14. No hyperparameter optimization

Task 0007 must NOT run:

- Optuna;
- grid search;
- random search;
- architecture sweeps;
- learning-rate sweeps;
- latent-dimension sweeps;
- activation-function comparisons.

We need one clean nonlinear baseline.

Hyperparameter optimization would add complexity before we even know real anomaly performance.

---

# 15. Training data access

Use the existing feature-only guarded data access layer.

Avoid loading unnecessary particle arrays.

The model needs only the eight baseline features.

The implementation should not require the 2.9 GB canonical particle array to be copied into RAM.

Efficient access to the small event-feature matrix is sufficient.

---

# 16. PyTorch data pipeline

Implement a minimal, reusable PyTorch data path.

A simple Dataset/DataLoader abstraction is appropriate now.

Avoid overengineering.

Requirements:

- deterministic training shuffle given the seed;
- configurable batch size;
- feature-only data;
- no labels required for training;
- no test split access;
- efficient CPU batching.

Use suitable DataLoader settings for macOS.

Do not blindly enable large numbers of workers.

Benchmarking DataLoader performance is out of scope.

---

# 17. Model module

Create an appropriate model implementation, e.g.:

```text
src/latenttrigger/models/autoencoder.py
```

The module should expose:

- model construction;
- forward reconstruction;
- encoding where useful;
- parameter count;
- anomaly scoring;
- artifact serialization/loading where appropriate.

Keep training orchestration separate from the pure network definition when practical.

---

# 18. Training module

Create a small reusable training implementation under an appropriate structure.

For example:

```text
src/latenttrigger/training/
    __init__.py
    autoencoder.py
```

or another clean repository-compatible layout.

Avoid building a universal deep-learning framework.

We currently need:

- training epoch;
- validation epoch;
- early stopping;
- checkpoint/best-state handling;
- deterministic run orchestration.

Future particle models may reuse selected utilities later, but do not abstract prematurely.

---

# 19. Canonical model artifact

Unlike temporary training checkpoints, the final frozen compact autoencoder must be reproducibly identifiable for later:

- evaluation;
- hardware benchmarking;
- export;
- quantization.

Because this model is extremely small, prefer a **small deterministic and portable scientific artifact**.

Evaluate a design such as:

```text
artifacts/models/compact-autoencoder-v1/
    model.json
```

containing:

- architecture;
- exact float32 parameters;
- feature order;
- model schema/version;
- training config identity;
- preprocessing identity;
- scientific hash.

A framework-neutral deterministic JSON representation is acceptable because the parameter count is tiny.

Alternatively use another compact tracked representation if it provides materially better correctness.

Do not make an opaque Pickle the only source of truth.

A local `.pt` state dict may be produced for convenience, but if ignored it must not be the only way to reconstruct the frozen model.

If adding a tracked model artifact, ensure it is small and intentional.

Document the decision.

---

# 20. Model identity

Create a deterministic scientific model identity/hash based on:

- architecture;
- ordered parameters;
- relevant preprocessing identity;
- training configuration;
- feature schema.

Do not include:

- timestamps;
- absolute file paths;
- transient local environment fields

in the scientific identity.

This model identity will later be important when test data is finally unblinded.

---

# 21. Training history

Record training history in a small machine-readable result artifact.

Include per epoch:

- epoch;
- training loss;
- selection-validation loss.

Do not save per-event training scores unnecessarily.

A compact CSV is suitable.

Curate it into tracked results if small.

---

# 22. Training curve

Produce one concise curated figure showing:

- training reconstruction loss;
- selection-validation reconstruction loss;
- selected best epoch;
- early-stopping point if different.

Use appropriate scale if helpful.

Do not create excessive visualizations.

---

# 23. Background anomaly-score evaluation

After freezing the best model, score only:

- train background;
- selection-validation background;
- calibration-validation background.

Use the existing evaluation framework wherever possible.

Report the same background score summaries used for PCA:

- count;
- mean;
- std;
- min;
- median;
- p90;
- p95;
- p99;
- p99.9;
- max.

Do not access real test populations.

---

# 24. Threshold calibration

Use:

`validation_calibration_background`

to calibrate the same target FPRs defined by the evaluation protocol:

```text
0.1
0.05
0.01
0.001
```

Use the existing threshold-calibration implementation from Task 0006.

Do not create autoencoder-specific threshold semantics.

Then evaluate realized FPR using:

`validation_selection_background`.

Report the same table structure used by PCA.

---

# 25. Background stability

Use the same background-stability diagnostics as Task 0006 where applicable.

This makes PCA and AE background behavior directly comparable.

Do not introduce a different statistical framework simply because this model is neural.

---

# 26. PCA comparison

Produce a concise **background-only** comparison between PCA and the compact autoencoder.

Allowed comparisons include:

- parameter count;
- latent dimensionality;
- model artifact size;
- fit/training time;
- background reconstruction-score stability;
- calibrated threshold stability.

Do NOT claim:

> autoencoder is better at anomaly detection

because real signal performance is still unknown.

Do not compare AUC/AP.

If score scales differ, do not directly compare absolute thresholds as if they had the same meaning.

---

# 27. Latent representation diagnostics

Because this model has a three-dimensional latent space, perform only a bounded background-only sanity check.

Allowed:

- latent component means/stds on training background;
- finite-value verification;
- detection of collapsed dimensions.

Do not:

- cluster signal;
- visualize test signal in latent space;
- tune model architecture based on aesthetically pleasing latent plots.

A latent-space plot is optional and probably unnecessary at this stage.

---

# 28. Avoid anomaly-score leakage

Do not calculate any global normalization of anomaly scores using:

- test background;
- test signal;
- signal events.

If score normalization is required at all, it must derive solely from permitted background populations and be frozen.

Prefer raw reconstruction SSE unless there is a strong reason otherwise.

---

# 29. Future signal-aware evaluation

The existing evaluation framework already supports ROC-AUC, AP and fixed operating-point metrics.

Do not duplicate those functions.

Ensure the compact autoencoder artifact can later be passed through the same future test-evaluation gate used by PCA.

Do not open that gate in Task 0007.

---

# 30. Training CLI

Provide a reproducible command such as:

```bash
python -m latenttrigger.models.autoencoder \
    --config configs/models/compact_autoencoder.json
```

or an equally clear repository-compatible interface.

One normal canonical invocation should:

1. validate processed-data provenance;
2. open allowed feature splits;
3. configure deterministic CPU training;
4. train;
5. early-stop using selection-validation background;
6. restore the best model;
7. freeze/export the canonical model artifact;
8. score allowed background splits;
9. calibrate thresholds;
10. create allowed reports/results;
11. record provenance;
12. refuse test access.

---

# 31. Optional separate MPS diagnostic command

If useful, expose an explicit MPS diagnostic mode such as:

```bash
python -m latenttrigger.models.autoencoder \
    --config configs/models/compact_autoencoder.json \
    --device mps \
    --smoke
```

or equivalent.

This must not overwrite the canonical CPU model.

Clearly label MPS results as compatibility/engineering checks, not scientific model-selection results.

---

# 32. Result artifacts

Create small curated machine-readable outputs.

Potential structure:

```text
results/tables/final/
    task0007-autoencoder-background-summary.csv
    task0007-autoencoder-thresholds.csv
    task0007-autoencoder-training-history.csv
    task0007-autoencoder-results.json
```

Use repository conventions.

Do not track:

- millions of per-event scores;
- temporary checkpoints;
- training caches;
- large tensors.

---

# 33. Curated figures

Produce a concise figure set, likely:

### Figure 1
Training/validation reconstruction loss.

### Figure 2
Background anomaly-score distributions for:

- training;
- selection validation;
- calibration validation.

Optionally:

### Figure 3
Background-only PCA vs autoencoder stability comparison if genuinely informative.

Do not produce signal plots.

---

# 34. Autoencoder report

Create:

`docs/compact-autoencoder.md`

Suggested structure:

## Purpose

## Architecture

## Parameter count

## Input representation

## Training protocol

## Reproducibility

## Training dynamics

## Anomaly score

## Background validation

## Threshold calibration

## PCA background-only comparison

## MPS compatibility

## Frozen model artifact

## Test embargo

## Limitations

## Future final evaluation

Explicitly state:

> No real test-signal performance was inspected during Task 0007.

---

# 35. Reproducibility rerun

Perform an independent second canonical CPU training run using the same configuration and seed.

Verify:

- same best epoch;
- same final model parameters, ideally bitwise;
- same scientific model hash;
- same background scores;
- same thresholds;
- same summary results.

If exact bitwise reproducibility is not achieved:

- quantify the differences;
- identify the likely source;
- do not simply loosen tolerances until tests pass.

The tiny CPU model should make strong reproducibility practical.

---

# 36. MPS comparison boundaries

You may report engineering observations such as:

- MPS smoke run succeeded;
- MPS loss remained finite.

Do not yet publish:

- formal CPU vs MPS latency;
- events/s;
- energy;
- speedup claims.

Those belong to later hardware benchmarking.

---

# 37. Unit tests

Add meaningful tests.

At minimum:

### Architecture

- correct layer dimensions;
- correct output shape;
- latent shape;
- parameter count;
- invalid input dimension rejected.

### Scoring

- zero reconstruction error gives zero score;
- larger reconstruction residual gives larger score;
- score shape;
- finite values.

### Serialization

- exported model reconstructs exactly;
- model identity stable;
- corrupted/mismatched artifacts rejected.

### Training

Using tiny synthetic background data:

- training reduces reconstruction loss;
- early stopping logic;
- best-state restoration;
- deterministic CPU training;
- invalid config rejection.

### Data access

- only feature inputs used;
- training cannot access test splits;
- calibration population is not used for optimization.

### Integration

- synthetic/dev-like end-to-end fit → score → threshold path.

CI must not require the real processed dataset.

---

# 38. Real-data validation

On the real allowed background data verify:

- training count = `699,957`;
- selection validation count = `74,749`;
- calibration validation count = `74,823`;
- input dimension = `8`;
- all model inputs finite;
- all losses finite;
- all reconstruction outputs finite;
- all anomaly scores finite;
- no test split was opened;
- threshold counts and FPR calculations are consistent.

---

# 39. Resource observations

Record for the canonical CPU run:

- total trainable parameters;
- model artifact size;
- number of epochs executed;
- best epoch;
- total training wall time;
- scoring time;
- approximate peak RSS if readily measurable.

These are engineering observations, NOT yet formal hardware benchmarks.

---

# 40. Dependency discipline

PyTorch already exists.

Do not add:

- PyTorch Lightning;
- Keras/TensorFlow;
- MLflow;
- W&B;
- Optuna;
- Hydra;
- Accelerate;
- other training frameworks.

The model is too small to justify them.

Use the existing lightweight project structure.

---

# 41. Scope exclusions

Do NOT:

- inspect `test_background`;
- inspect `test_signal`;
- compute real signal AUC/AP;
- perform architecture search;
- tune latent dimension;
- tune against signal;
- train a particle-level model;
- implement attention;
- implement Transformer models;
- implement ONNX export;
- implement CoreML export;
- quantize the model;
- benchmark inference latency;
- measure energy;
- implement TensorRT;
- implement hls4ml;
- implement the trigger simulator.

---

# 42. Validation

Before completion run:

- editable installation;
- dependency consistency;
- package import;
- Ruff lint;
- Ruff formatting check;
- full pytest suite;
- existing CPU smoke test;
- existing MPS smoke test;
- processed-store verification;
- dev AE pipeline validation;
- canonical real CPU training;
- background scoring;
- threshold calibration;
- independent CPU reproducibility rerun;
- bounded MPS compatibility run;
- documentation-link validation;
- Git exclusions;
- `git diff --check`;
- final Git diff inspection.

Explicitly audit logs/code paths to verify:

```text
test_background accesses = 0
test_signal accesses = 0
```

for the real Task 0007 workflow.

---

# 43. Definition of done

Task 0007 is complete only when:

- Task prompt/handoff exist;
- handoff index is updated;
- compact autoencoder implementation exists;
- architecture is frozen;
- training configuration is tracked;
- canonical CPU model trains successfully;
- best epoch is selected background-only;
- model artifact is frozen and reproducibly identifiable;
- anomaly scores use the common convention;
- allowed background splits are scored;
- thresholds are calibrated using the existing protocol;
- PCA comparison remains background-only;
- independent CPU rerun reproduces the model/results;
- MPS compatibility succeeds or a concrete blocker is documented;
- no real test split is accessed;
- tests pass;
- documentation/reporting is complete.

---

# 44. Mandatory Task 0007 handoff

Update:

`docs/handoffs/0007-compact-autoencoder.md`

with actual facts including:

- base commit;
- environment;
- architecture;
- parameter count;
- input feature order;
- training configuration;
- seed/determinism settings;
- train/validation populations;
- epochs executed;
- best epoch;
- training/validation loss;
- model scientific hash;
- model artifact format/size;
- background score summaries;
- calibrated thresholds;
- realized selection-validation FPRs;
- PCA background-only comparison;
- MPS compatibility outcome;
- runtimes/resource observations;
- reproducibility rerun;
- test count;
- confirmation that real test access remained zero;
- issues;
- rejected alternatives;
- next recommended task.

Update the handoff index.

Do not rewrite old handoffs.

---

# 45. Final response format

Return:

## 1. What was implemented

## 2. Compact autoencoder

Include:

- architecture;
- parameter count;
- latent dimension;
- feature input;
- score definition.

## 3. Training result

Include:

- training events;
- best epoch;
- epochs executed;
- final/best training loss;
- selection-validation loss;
- CPU training time.

## 4. Background validation

Summarize allowed score distributions and stability.

## 5. Threshold calibration

Provide target vs realized background FPR table.

## 6. PCA comparison

Background-only comparison only.

Do not imply superior real anomaly detection.

## 7. Frozen artifact and reproducibility

Include:

- model identity/hash;
- artifact format/size;
- second-run result.

## 8. MPS compatibility

State what was actually tested.

## 9. Test embargo status

Explicitly report:

```text
test_background accessed: NO
test_signal accessed: NO
```

for real model evaluation.

If either answer is YES, disclose exactly why and what was observed.

## 10. Validation results

Include actual pytest count and other checks.

## 11. Files changed

Separate tracked files from ignored generated artifacts.

## 12. Issues / deferred decisions

## 13. Recommended next task

Expected:

**Task 0008 — Particle-Level Autoencoder or Set-Based Neural Baseline Design**

However, do not automatically assume a Transformer should come next.

Based on Task 0007 results and project architecture, recommend whether the next best step should be:

- a particle-level/set-aware model;
- initial inference/export groundwork;
- another clearly justified stage.

Preserve the real-test embargo.

## 14. Git commit and push commands

This section is mandatory and MUST be last.

Do NOT commit or push automatically.

Provide exact commands to:

```bash
git status
git diff

git add <only intended Task 0007 files>

git status
git diff --cached
git diff --cached --check

git commit -m "<specific conventional commit>"
git push
```

Selectively stage only intended Task 0007:

- source;
- tests;
- configuration;
- documentation;
- tiny intentionally tracked frozen model artifact if applicable;
- small curated result tables/figures.

Never stage:

- raw data;
- processed multi-GB stores;
- per-event score arrays;
- temporary checkpoints;
- logs;
- caches;
- credentials;
- unrelated files.

An appropriate commit message will likely be:

`feat: add compact autoencoder anomaly baseline`

but adjust it to the actual completed work.

Proceed with **Task 0007 only**.