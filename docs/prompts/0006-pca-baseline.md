# Task 0006 prompt record

Original supplied specification; only terminal blank lines are normalized.

---

# LatentTrigger — Task 0006: PCA Baseline and Evaluation Framework

You are continuing development of **LatentTrigger**.

Tasks 0001–0005 are complete and committed.

Task 0005 produced a deterministic, verified processed dataset with:

- a compact FP32 ragged canonical particle store;
- frozen split membership;
- standardized 8-dimensional baseline features;
- guarded split access;
- deterministic particle-model views;
- verified provenance and integrity.

Read before modifying anything:

- `docs/development.md`
- `docs/data-design.md`
- `docs/preprocessing-contract.md`
- `docs/preprocessing-pipeline.md`
- `docs/training-data-eda.md`
- `docs/handoffs/0005-preprocessing-pipeline.md`
- `configs/data/lhco_rnd_v5.json`
- the relevant processed-data reader/source code.

This is:

**Task 0006 — PCA Baseline and Evaluation Framework**

This is the first actual anomaly-detection model task.

The goals are:

1. establish a scientifically clean, reproducible anomaly-detection evaluation framework;
2. implement and freeze a simple PCA reconstruction baseline;
3. calibrate operating thresholds using background-only data;
4. produce background-only baseline diagnostics;
5. prepare signal-aware evaluation code without unblinding the real test sets.

Do not implement an autoencoder or Transformer yet.

---

# 0. Mandatory repository inspection

Before modifying anything:

- inspect Git status;
- identify current branch and HEAD/base commit;
- verify Tasks 0001–0005 are committed;
- inspect all relevant data/preprocessing modules;
- verify the processed full store;
- verify split counts;
- inspect how guarded test access currently works;
- inspect the exact 8 baseline feature names/order;
- inspect whether baseline features are already standardized and how those statistics were obtained;
- inspect current dependencies;
- inspect available local generated artifacts.

Do not modify unrelated work.

Follow the permanent LatentTrigger prompt/handoff protocol.

---

# 1. Task records

Create:

```text
docs/prompts/0006-pca-baseline.md
docs/handoffs/0006-pca-baseline.md
```

Update:

`docs/handoffs/README.md`

Do not rewrite historical task records.

---

# 2. Critical evaluation policy: do not unblind the real test sets

This task MUST NOT inspect model scores, distributions or performance on:

```text
test_background
test_signal
```

They remain embargoed.

This applies even though the processed store physically contains those events.

Do not request explicit test access merely because it is technically available.

The intended data use for Task 0006 is:

```text
train_background
    ↓
fit PCA

validation_selection_background
    ↓
background-only model diagnostics / selection checks

validation_calibration_background
    ↓
operating-threshold calibration

test_background
test_signal
    ↓
DO NOT ACCESS FOR MODEL EVALUATION IN THIS TASK
```

The development subset may be used for implementation/smoke testing.

---

# 3. Why test embargo matters

Future LatentTrigger stages will introduce:

- compact autoencoders;
- particle/set models;
- hardware optimization.

If real test-signal AUC is repeatedly observed while developing those models, the test set effectively becomes a validation set.

Task 0006 should therefore establish a reusable framework that makes this difficult to do accidentally.

Document this explicitly.

---

# 4. Future final evaluation policy

Design the evaluation framework so that a future explicitly authorized benchmark stage can evaluate frozen candidate models on:

```text
test_background + test_signal
```

but do not perform that evaluation now.

Future signal-aware metrics should therefore already be implementable without changing metric definitions later.

The framework must distinguish clearly between:

### development/background evaluation

allowed now;

and:

### final signal-aware benchmark

embargoed now.

---

# 5. Baseline input

The PCA baseline must operate on the **eight frozen aggregate event features** established in Tasks 0004–0005.

Inspect their exact names/order from the repository.

Do not redefine the feature set.

Do not use:

- labels;
- split identity;
- event ID;
- particle padding information;

as model inputs.

Use the existing standardized baseline representation if that is the frozen Task 0005 representation.

Do not refit preprocessing statistics.

---

# 6. PCA baseline definition

Implement a standard PCA reconstruction anomaly detector.

Conceptually:

\[
x \in \mathbb{R}^{8}
\]

is projected onto a lower-dimensional PCA subspace:

\[
z = W_k^\top(x-\mu)
\]

and reconstructed:

\[
\hat{x} = \mu + W_kz
\]

Define the anomaly score as squared reconstruction error:

\[
s(x)=\|x-\hat{x}\|_2^2
\]

unless repository conventions justify a mathematically equivalent normalization.

Higher score must always mean:

> more anomalous.

Document exact score semantics.

---

# 7. PCA implementation choice

Prefer a mature, transparent implementation such as:

`scikit-learn`

if appropriate.

If adding scikit-learn:

- add it as a justified runtime/modeling dependency;
- pin/constrain it sensibly according to existing project policy;
- document the dependency change.

Do not implement custom PCA linear algebra merely to avoid a reasonable dependency unless there is a concrete benefit.

If the project already contains an appropriate dependency, reuse it.

---

# 8. PCA component-selection rule

Do NOT choose the number of components by looking at signal performance.

Use a deterministic background-only rule.

Preferred default:

> choose the smallest number of principal components whose cumulative explained variance on `train_background` reaches a frozen target.

A reasonable target is:

\[
95\%
\]

but before hardcoding it, inspect the resulting spectrum.

If 95% produces a pathological choice such as keeping all 8 dimensions or collapsing to an unreasonably small representation, document the issue and use a principled alternative.

The final selection rule must:

- use training background only;
- be deterministic;
- be documented before any signal evaluation;
- produce a fixed `k`.

Also report the full 8-component explained-variance spectrum for scientific transparency.

Do not search for `k` using test AUC.

---

# 9. Selection-validation role

Use:

`validation_selection_background`

to verify that the selected PCA behaves consistently out of sample.

Useful background-only diagnostics include:

- reconstruction-score distribution;
- mean/median score;
- relevant quantiles;
- comparison with training-background score distribution;
- stability/drift measures.

Do not change `k` simply to minimize validation reconstruction error unless a selection criterion is explicitly preregistered.

Avoid post-hoc tuning.

---

# 10. Calibration-validation role

Use:

`validation_calibration_background`

only for threshold calibration.

Calibrate score thresholds corresponding to several target background false-positive rates / acceptance rates.

At minimum consider:

\[
FPR = 10^{-1}
\]

\[
FPR = 5\times10^{-2}
\]

\[
FPR = 10^{-2}
\]

\[
FPR = 10^{-3}
\]

You may include another scientifically useful operating point if justified.

For each target FPR, determine the empirical score threshold using a clearly defined quantile convention.

Document the convention exactly.

Do not derive thresholds from test background.

---

# 11. Threshold verification

After calibration, evaluate the realized background acceptance/FPR on:

`validation_selection_background`

as an independent background population.

This is allowed because it remains background-only.

For each threshold report:

- target FPR;
- calibration threshold;
- realized selection-validation FPR;
- absolute deviation;
- relative deviation where meaningful.

This gives an initial estimate of threshold stability.

Do not evaluate signal efficiency yet.

---

# 12. Evaluation framework

Create reusable evaluation utilities under an appropriate structure such as:

```text
src/latenttrigger/evaluation/
    __init__.py
    metrics.py
    thresholds.py
```

and model code under something like:

```text
src/latenttrigger/models/
    __init__.py
    pca.py
```

Use existing repository conventions where appropriate.

Avoid a large generic framework.

The API should be simple enough for later autoencoder/Transformer scores to reuse the same evaluation functions.

---

# 13. Score-oriented interface

The evaluation framework should primarily consume:

```text
background_scores
signal_scores
```

rather than depending on PCA internals.

This will allow later models to plug in their anomaly scores without rewriting metrics.

Establish one universal convention:

\[
\text{larger score} \Rightarrow \text{more anomalous}
\]

If any future model naturally produces the opposite orientation, score orientation must be normalized before evaluation.

---

# 14. Signal-aware metrics to implement now

Implement, test and document the metrics that will be used during the future final benchmark.

Do NOT run them on the real embargoed signal data in this task.

At minimum implement:

### ROC-AUC

### PR-AUC / Average Precision

Be explicit that PR metrics depend on class prevalence.

### Signal efficiency

\[
\epsilon_S = TPR
\]

### Background efficiency

\[
\epsilon_B = FPR
\]

### Background rejection

\[
R_B = \frac{1}{\epsilon_B}
\]

Handle zero-FPR cases explicitly rather than returning misleading infinities without context.

### TPR at fixed FPR

Support at least future evaluation at:

- `1e-1`
- `5e-2`
- `1e-2`
- `1e-3`

### FPR / background rejection at fixed signal efficiency

Support useful values such as:

- 50%;
- 80%;
- 90%;

where statistically defined.

---

# 15. Finite-sample awareness

The eventual test background contains approximately 150k events.

The evaluation code must acknowledge finite-sample limits.

For example, extremely small empirical FPR claims may not be meaningful when only a small number of background events are available.

Do not extrapolate empirical rejection beyond what the sample supports unless a later task explicitly introduces a justified statistical model.

Where useful, report counts alongside rates.

Design metric results so that:

```text
FPR = x
background false positives = n
background total = N
```

can be recovered.

---

# 16. ROC/PR implementation

Prefer mature implementations where appropriate, e.g. scikit-learn metrics.

Tests should verify:

- perfect separation;
- random-like toy data;
- reversed score orientation behavior;
- ties;
- highly imbalanced classes;
- degenerate inputs;
- invalid labels.

Do not silently accept unusable metric inputs.

---

# 17. Background-only diagnostics

Since test signal remains embargoed, Task 0006's real-data output should focus on background-only behavior.

Compute for training and allowed validation backgrounds:

- score count;
- mean;
- standard deviation;
- minimum;
- median;
- p90;
- p95;
- p99;
- p99.9;
- maximum.

Also inspect whether the PCA score distribution shows obvious pathological tails.

---

# 18. PCA explained-variance diagnostics

Report:

\[
\lambda_i
\]

or the normalized explained-variance ratios for all PCA components.

Produce a compact figure showing:

- per-component explained variance;
- cumulative explained variance;
- selected `k`;
- selection target.

This figure may be curated into the repository if useful.

---

# 19. Reconstruction-score diagnostics

Produce a background-only plot comparing anomaly-score distributions for:

- training background;
- selection-validation background;
- calibration-validation background.

Use appropriate scaling if the distribution is strongly skewed.

Do not include test background or signal.

A second plot may show empirical score tail / survival probability if that helps visualize calibrated thresholds.

Keep the figure set concise.

---

# 20. Distribution stability

Quantify whether reconstruction-score behavior differs materially across background splits.

Use one or more simple, interpretable diagnostics.

Examples:

- relative quantile differences;
- Kolmogorov-Smirnov statistic;
- Wasserstein distance.

Do not introduce a large statistical-testing suite.

If adding a statistical metric dependency beyond existing libraries, justify it.

The goal is to detect obvious split drift, not to chase p-values on hundreds of thousands of events.

---

# 21. Model artifact

Persist the fitted PCA baseline in a reproducible manner.

Prefer a transparent artifact over an opaque large binary.

Because the PCA model has only eight input dimensions, consider storing small numeric parameters such as:

- feature names/order;
- training mean if PCA centers internally;
- components;
- explained variance;
- explained variance ratio;
- selected `k`;
- score definition;
- implementation/library version.

A compact JSON/NPZ representation is acceptable.

If using joblib/pickle, explain why and treat it as a generated local artifact rather than the sole reproducibility mechanism.

Another developer should be able to reproduce the fitted baseline from tracked config + processed data.

---

# 22. Baseline configuration

Create a tracked configuration file such as:

```text
configs/models/pca_baseline.json
```

containing the preregistered/frozen modeling choices, including:

- model type;
- input feature schema/version;
- component-selection rule;
- explained-variance target;
- anomaly-score definition;
- split roles;
- threshold target FPRs;
- random state if relevant;
- evaluation protocol version.

Do not copy fitted test-dependent results into model configuration.

---

# 23. Results artifacts

Create small machine-readable baseline results for allowed background data.

For example:

```text
results/tables/final/task0006-pca-background-summary.csv
results/tables/final/task0006-pca-thresholds.csv
```

or an equivalent sensible format.

Tracked results must contain only allowed Task 0006 information.

Do not include test-signal metrics because they must not exist yet.

Curated plots may be placed under the existing final figure policy.

Generated intermediate arrays/scores should remain ignored.

---

# 24. Run provenance

Every baseline run should record enough provenance to identify:

- processed-data schema/version;
- source dataset checksum;
- preprocessing config identity/hash;
- split provenance;
- model config;
- software/library versions;
- baseline feature order;
- fitted training population count;
- model artifact/hash where practical;
- run timestamp;
- Git commit/base state where practical.

Keep it lightweight.

Do not add MLflow/W&B in this task.

---

# 25. Training/fitting CLI

Provide a reproducible command such as:

```bash
python -m latenttrigger.models.pca \
    --config configs/models/pca_baseline.json
```

or an equivalent clean interface.

A single command should be able to:

1. open the processed store;
2. access allowed training/validation splits;
3. fit PCA;
4. select `k` using the frozen rule;
5. compute background-only diagnostics;
6. calibrate thresholds;
7. produce model/result artifacts;
8. verify provenance;
9. refuse accidental test access.

Exact architecture may differ if cleaner.

---

# 26. Evaluation CLI / future test gate

Design the evaluation interface so that final test evaluation requires an **explicit opt-in**.

Conceptually something like:

```bash
python -m latenttrigger.evaluation.run \
    --model ... \
    --split test \
    --allow-test
```

Do not actually execute it on real test data in this task.

Normal/default execution must not access embargoed test splits.

If the processed reader already has test guards, integrate with them rather than implementing a conflicting second system.

---

# 27. Explicit test-unblinding record

Prepare for a future requirement:

when real test access eventually occurs, it should leave an explicit provenance/log record stating:

- when it occurred;
- which frozen model/config was evaluated;
- which commit/model artifact;
- which metrics were computed.

Do not implement an elaborate audit database.

A future handoff plus evaluation output manifest may be enough.

For Task 0006, document the intended policy.

---

# 28. Do not create signal proxies unless necessary

Do not fabricate physics anomalies merely to produce an AUC number.

Synthetic score arrays are appropriate for unit tests.

Synthetic perturbations of real HEP events should not be presented as real anomaly-detection performance.

The PCA baseline can be considered successfully established without seeing real signal performance yet.

---

# 29. Tests

Add meaningful tests.

At minimum cover:

### PCA model

- fit on synthetic background;
- selected component count follows the configured rule;
- reconstruction works;
- score shape;
- higher reconstruction error yields higher anomaly score;
- deterministic fitted result where expected;
- invalid feature dimension rejected;
- feature ordering validated.

### Threshold calibration

- correct empirical quantile behavior;
- ties;
- very small samples;
- invalid target FPR;
- deterministic output.

### Metrics

- ROC-AUC perfect separation;
- Average Precision;
- fixed-FPR TPR;
- fixed-TPR FPR;
- background rejection;
- finite-sample counts;
- invalid/degenerate inputs.

### Test embargo

- default baseline workflow cannot read real test splits;
- explicit test-gate behavior works on synthetic/test fixtures only;
- no accidental test access occurs during normal fit/calibration.

### Provenance

- manifest/config identity;
- feature schema mismatch rejected;
- processed schema mismatch rejected where applicable.

CI must not require the local 2.9 GB processed dataset.

---

# 30. Real-data baseline run

After unit tests succeed, run the PCA baseline against the real processed store using only:

- `train_background`;
- `validation_selection_background`;
- `validation_calibration_background`.

Do not access:

- `test_background`;
- `test_signal`.

Record exact results.

At minimum report:

- training event count;
- input feature count;
- explained-variance spectrum;
- selected `k`;
- background score summaries;
- calibrated thresholds;
- realized FPRs on selection-validation background;
- fit/runtime;
- scoring/runtime;
- memory where practical.

This is not yet a formal hardware benchmark.

---

# 31. Reproducibility run

Repeat the PCA baseline pipeline independently.

Verify:

- selected `k` identical;
- PCA parameters identical within expected deterministic numerical behavior;
- scientific result artifact content identical or numerically equivalent;
- thresholds identical;
- background summary metrics identical;
- model scientific hash identical where designed.

Timestamp/provenance fields may differ without affecting scientific identity.

If BLAS/library behavior prevents bitwise identity, quantify the numerical difference rather than claiming failure automatically.

---

# 32. Baseline report

Create:

`docs/pca-baseline.md`

Suggested structure:

## Purpose

## Input representation

## Training protocol

## Component-selection rule

## PCA spectrum

## Anomaly score

## Background-only validation

## Threshold calibration

## Evaluation metrics

## Test embargo

## Reproducibility

## Limitations

## Future final benchmark

Be explicit:

> No real test-signal performance was inspected during Task 0006.

Do not put placeholder AUC values.

---

# 33. Evaluation protocol document

Create or update an authoritative document such as:

`docs/evaluation-protocol.md`

This should become the common evaluation contract for future models.

Define:

### Score convention

Higher = more anomalous.

### Split roles

Exact permitted use of every split.

### Model selection

What information may be used.

### Threshold calibration

Which split and procedure.

### Final benchmark

Which splits remain embargoed.

### Metrics

Exact metric definitions.

### Finite-sample limitations

### Test-unblinding policy

### Reporting requirements

Future autoencoder/Transformer tasks must follow this document.

---

# 34. README updates

Update the main README minimally.

Reflect that:

- deterministic preprocessing is complete;
- PCA anomaly-detection baseline is implemented;
- background-only evaluation/calibration is complete;
- real test performance remains intentionally embargoed;
- next model stage is planned.

Do not advertise an AUC that has not been measured.

Link to:

- PCA baseline report;
- evaluation protocol.

---

# 35. Dependency discipline

Only add dependencies required for this task.

`scikit-learn` is reasonable if selected.

Do not add:

- MLflow;
- W&B;
- Optuna;
- pandas merely for tiny result files if stdlib/NumPy suffices;
- plotting frameworks beyond what is already present without need;
- deep-learning/model dependencies unrelated to the baseline.

PyTorch already exists but PCA should not be implemented in PyTorch simply because it is available unless there is a clear reason.

---

# 36. Scope exclusions

Do NOT:

- train an autoencoder;
- implement Transformer models;
- inspect `test_signal`;
- inspect test-signal score distributions;
- compute real test ROC-AUC;
- optimize PCA against signal labels;
- perform hyperparameter search using signal;
- implement ONNX;
- implement CoreML;
- run hardware latency benchmarks;
- quantize models;
- implement TensorRT;
- implement hls4ml;
- implement the trigger simulator;
- add experiment-tracking services.

This task is baseline modeling + evaluation infrastructure only.

---

# 37. Validation

Before completion run:

- editable installation;
- dependency consistency;
- package import;
- Ruff lint;
- Ruff formatting check;
- full pytest suite;
- CPU smoke test;
- MPS smoke test;
- processed-store verification;
- real PCA fit;
- real background-only scoring;
- threshold calibration;
- selection-validation threshold verification;
- independent reproducibility rerun;
- documentation-link validation;
- Git exclusion verification;
- `git diff --check`;
- final diff inspection.

Explicitly verify through logs/code paths that no real test split was accessed during the Task 0006 model run.

---

# 38. Definition of done

Task 0006 is complete only when:

- prompt/handoff files exist;
- handoff index is updated;
- reusable evaluation framework exists;
- signal-aware metric functions exist and are unit-tested;
- PCA baseline exists;
- PCA component rule is frozen;
- PCA is fitted on training background only;
- background validation diagnostics exist;
- thresholds are calibrated on calibration background only;
- thresholds are checked on selection-validation background;
- model/config provenance exists;
- real test splits remain unopened;
- baseline documentation exists;
- evaluation protocol exists;
- reproducibility rerun succeeds;
- all tests pass;
- no large generated score arrays are accidentally committed.

---

# 39. Mandatory Task 0006 handoff

Update:

`docs/handoffs/0006-pca-baseline.md`

with actual facts including:

- base commit;
- environment;
- dependency changes;
- processed schema/config identity;
- PCA implementation/library;
- feature order;
- training count;
- explained-variance ratios;
- component-selection target;
- selected `k`;
- score definition;
- background score statistics;
- thresholds;
- realized validation FPRs;
- runtimes;
- reproducibility results;
- test count;
- confirmation that real test splits were not accessed;
- issues;
- rejected alternatives;
- next task.

Update the handoff index.

Do not rewrite old handoffs.

---

# 40. Final response format

Return:

## 1. What was implemented

## 2. PCA baseline

Include:

- features;
- training population;
- explained variance;
- selected component count;
- anomaly score.

## 3. Background validation

Summarize allowed score diagnostics.

## 4. Threshold calibration

Include a concise table of target and realized background FPR.

## 5. Evaluation framework

Summarize implemented future signal-aware metrics.

## 6. Test embargo status

Explicitly state whether `test_background` or `test_signal` was accessed.

The expected answer for Task 0006 is:

**No.**

If they were accessed for any reason, disclose that immediately and explain exactly what was inspected.

## 7. Reproducibility and validation

Include actual pytest count and reproducibility outcome.

## 8. Files changed

Separate tracked files from ignored generated artifacts.

## 9. Issues / deferred decisions

## 10. Recommended next task

Expected:

**Task 0007 — Compact Autoencoder Baseline**

unless Task 0006 reveals a blocker.

The next task should reuse the same evaluation protocol and preserve the test embargo.

## 11. Git commit and push commands

This section is mandatory and MUST be last.

Do NOT commit or push automatically.

Provide exact commands to:

```bash
git status
git diff

git add <only intended Task 0006 files>

git status
git diff --cached
git diff --cached --check

git commit -m "<specific conventional commit>"
git push
```

Selectively stage only intended Task 0006:

- source;
- tests;
- configuration;
- documentation;
- small curated result tables/figures.

Never stage:

- processed multi-GB data;
- raw dataset;
- large score arrays;
- temporary model artifacts;
- caches;
- logs;
- credentials;
- unrelated work.

An appropriate commit message will likely be:

`feat: add PCA anomaly baseline and evaluation framework`

but adjust it to reflect the actual implementation.

Proceed with **Task 0006 only**.
