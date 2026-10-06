# LatentTrigger — Task 0008: Compact Autoencoder Convergence Closure

You are continuing development of **LatentTrigger**.

Tasks 0001–0007 are complete and committed.

Task 0007 implemented the first compact neural anomaly-detection baseline:

```text
8 → 6 → 3 → 6 → 8
```

with:

- 155 trainable parameters;
- standardized 8-dimensional event-level input;
- CPU canonical training;
- background-only selection and calibration;
- deterministic reproducibility;
- a frozen model artifact;
- strict preservation of the real-test embargo.

However, Task 0007 revealed an important unresolved issue:

> The best model occurred at epoch 200 out of 200, and training was still improving when the configured maximum epoch limit was reached.

Therefore convergence was not established.

This task exists solely to resolve that methodological issue **before any more complex neural architecture is introduced**.

This is:

**Task 0008 — Compact Autoencoder Convergence Closure**

The purpose is to determine whether the existing compact autoencoder was prematurely stopped by the epoch cap and, if so, establish a properly converged canonical baseline.

Do NOT change the architecture.

Do NOT perform hyperparameter search.

Do NOT access any real test split.

---

# 0. Mandatory repository inspection

Before changing anything:

- inspect Git status;
- identify current branch and HEAD/base commit;
- verify Tasks 0001–0007 are committed;
- inspect:
  - `docs/compact-autoencoder.md`;
  - `docs/evaluation-protocol.md`;
  - Task 0007 handoff;
  - Task 0007 training configuration;
  - Task 0007 training history;
  - frozen v1 model artifact;
  - autoencoder training implementation;
- verify the processed store;
- confirm that the Task 0007 canonical CPU run can still be reproduced.

Do not modify unrelated work.

Follow the permanent LatentTrigger prompt/handoff protocol.

---

# 1. Task records

Create:

```text
docs/prompts/0008-autoencoder-convergence.md
docs/handoffs/0008-autoencoder-convergence.md
```

Update:

`docs/handoffs/README.md`

Do not rewrite Task 0007 history.

Task 0007 must remain an accurate record of what happened.

---

# 2. Scientific rationale

Task 0007 produced:

```text
best epoch = 200
maximum epochs = 200
```

with loss still improving.

This means the stopping mechanism did not determine the training endpoint.

The epoch cap did.

That makes it inappropriate to assume that the Task 0007 artifact is a fully trained baseline.

Task 0008 must answer:

> Does the same compact autoencoder converge when given a sufficiently long training horizon under exactly the same scientific protocol?

---

# 3. Preserve the real-test embargo

Real model/evaluation access to the following remains forbidden:

```text
test_background
test_signal
```

Allowed real populations remain:

```text
train_background
validation_selection_background
validation_calibration_background
```

Do not compute:

- test anomaly scores;
- test reconstruction losses;
- ROC-AUC;
- Average Precision;
- signal efficiency;
- test-background FPR;
- signal latent distributions.

The result of this task must remain completely signal-blind.

---

# 4. Do not redesign the model

The architecture MUST remain exactly:

```text
8 → 6 → 3 → 6 → 8
```

with:

- ReLU after the first encoder layer;
- linear latent layer;
- ReLU after the first decoder layer;
- linear output;
- 155 parameters.

Do not add or change:

- hidden widths;
- latent dimensionality;
- activation functions;
- BatchNorm;
- Dropout;
- residual connections;
- regularization terms;
- alternative losses.

This task is about convergence, not model selection.

---

# 5. Preserve all training choices except the epoch ceiling

Use the exact Task 0007 choices for:

- optimizer;
- learning rate;
- batch size;
- shuffle policy;
- initialization;
- seed;
- early-stopping criterion;
- early-stopping patience;
- `min_delta`;
- training split;
- validation split;
- reconstruction loss;
- CPU canonical device;
- deterministic settings.

The only intended scientific training-policy change is:

```text
max_epochs: 200
```

→

```text
max_epochs: 1000
```

Do not add:

- learning-rate schedules;
- LR decay;
- warmup;
- optimizer changes;
- gradient clipping;

unless Task 0007 already used them.

Do not alter patience just to force an early-stop result.

---

# 6. New configuration

Do not overwrite the historical Task 0007 configuration.

Create a separate tracked configuration such as:

```text
configs/models/compact_autoencoder_v2.json
```

It should be identical to the Task 0007 canonical configuration except for:

```text
max_epochs = 1000
```

and any explicit model/version identifier required for provenance.

Document the exact config diff.

---

# 7. Retrain from scratch

Do NOT simply continue training the Task 0007 checkpoint.

The canonical Task 0008 experiment must retrain from scratch using:

- the same seed;
- the same initialization procedure;
- the same sample ordering;
- the same optimizer initialization;
- the same deterministic CPU path.

This gives a much stronger reproducibility check.

The first 200 epochs should reproduce Task 0007 exactly if the implementation is deterministic.

---

# 8. Mandatory first-200-epochs equivalence check

Before interpreting later epochs, compare Task 0008 epochs 1–200 against the historical Task 0007 training history.

Verify:

- training losses;
- selection-validation losses;
- best-state progression;
- epoch 200 parameters where practical.

Ideally these should be exactly identical.

If not, stop and investigate the source of divergence before interpreting convergence.

Possible causes could include:

- changed code;
- changed dependency behavior;
- changed shuffle order;
- changed preprocessing identity;
- seed handling;
- nondeterministic operations.

Do not simply accept a mismatch.

Document the result.

---

# 9. Convergence criterion

Use the existing Task 0007 background-only early-stopping rule.

Training should stop when:

- the configured early-stopping criterion is satisfied,

or when:

- epoch 1000 is reached.

Do not create a new convergence rule after observing the curve.

The best allowed model remains the epoch with the best:

`validation_selection_background`

reconstruction loss according to the existing training protocol.

---

# 10. If early stopping triggers

If early stopping occurs before epoch 1000:

Record:

- best epoch;
- stopping epoch;
- best training loss;
- best selection-validation loss;
- improvement relative to Task 0007;
- number of epochs since last improvement.

This establishes convergence according to the frozen protocol.

---

# 11. If epoch 1000 is reached

If:

```text
best epoch = 1000
```

or training remains clearly improving at the 1000-epoch cap:

do NOT silently extend training again.

Task 0008 should report:

> convergence remains unresolved under the current protocol.

Provide quantitative evidence such as:

- recent validation-loss slope;
- improvement over the last 50/100 epochs;
- distance between current and historical loss.

Do not start changing learning rates or architecture within this task.

That would require a new explicit methodological decision.

---

# 12. Frozen v2 artifact

If Task 0008 produces a later best epoch and a legitimately improved selection-background model, create a new artifact:

```text
artifacts/models/compact-autoencoder-v2/
    model.json
```

Do not delete or overwrite:

```text
compact-autoencoder-v1
```

The v1 artifact is historical evidence from Task 0007.

The v2 artifact should use the same transparent model representation introduced previously.

---

# 13. Canonical-model supersession rule

The decision must be deterministic.

Use Task 0008 v2 as the canonical compact AE for future stages if:

1. first-200-epoch reproducibility is verified;
2. training continues beyond epoch 200;
3. the best permitted selection-validation reconstruction loss is strictly better than the v1 best;
4. no methodological/test-embargo violation occurred.

If these conditions hold, document:

> compact-autoencoder-v2 supersedes compact-autoencoder-v1 as the canonical compact AE baseline.

Do not delete v1.

If they do not hold, retain v1 as canonical and explain why.

---

# 14. No signal-based supersession

Under no circumstances may v1 versus v2 be chosen using:

- anomaly AUC;
- signal efficiency;
- test score distribution;
- test labels.

Selection is entirely background-only.

---

# 15. Scientific identity

If v2 becomes canonical, compute its deterministic scientific SHA-256 identity using the established Task 0007 procedure.

Record:

- architecture;
- exact ordered parameters;
- preprocessing identity;
- feature order;
- training-config identity;
- model hash.

Exclude timestamps and machine-specific paths from scientific identity.

---

# 16. Training history

Store the complete Task 0008 training history in a small tracked artifact.

For each executed epoch include:

- epoch;
- training MSE;
- selection-validation MSE.

Do not store per-event scores.

---

# 17. Updated training figure

Produce a curated convergence figure.

It should show:

- Task 0008 training loss;
- Task 0008 selection-validation loss;
- historical epoch-200 boundary;
- selected best epoch;
- stopping epoch.

The purpose is to make visually obvious whether Task 0007 was prematurely capped.

Avoid decorative complexity.

---

# 18. Restore best state

After training:

- restore the best allowed model state;
- do not evaluate using the last epoch merely because it was last;
- verify the restored validation loss independently.

The scientific artifact must correspond to the restored best state.

---

# 19. Background scoring

If v2 becomes the candidate baseline, score only:

- training background;
- selection-validation background;
- calibration-validation background.

Use the same anomaly-score definition:

\[
s(x)
=
\sum_{j=1}^{8}(x_j-\hat{x}_j)^2
\]

Use the existing evaluation framework.

Do not modify score semantics.

---

# 20. Threshold calibration

Use the same frozen target FPRs:

```text
0.1
0.05
0.01
0.001
```

Calibration split:

`validation_calibration_background`

Independent background verification:

`validation_selection_background`

Use exactly the existing Task 0006/0007 quantile convention.

Do not introduce a new calibration method.

---

# 21. v1 vs v2 background comparison

If v2 exists, compare v1 and v2 only using permitted background information.

Report:

### Optimization

- best epoch;
- validation MSE;
- training MSE.

### Score stability

- train/selection/calibration score statistics;
- KS or existing stability diagnostics;
- threshold transfer stability.

### Model complexity

Identical:

- architecture;
- parameter count;
- artifact format.

Do not compare signal discrimination.

---

# 22. PCA context

You may retain the existing background-only PCA context for documentation.

Do not rerun or reinterpret PCA using any signal information.

The principal purpose of Task 0008 is v1 → v2 convergence closure, not another model comparison study.

---

# 23. Calibration must remain isolated from training

Ensure:

`validation_calibration_background`

is not used for:

- gradient training;
- early stopping;
- epoch selection;
- architecture decisions.

It is accessed only after the best model is restored/frozen for threshold calibration and allowed diagnostics.

Audit this explicitly.

---

# 24. Reproducibility rerun

After obtaining the canonical Task 0008 result, perform a second independent CPU run from scratch.

Verify:

- identical first 200 epochs;
- identical stopping epoch;
- identical best epoch;
- identical model parameters;
- identical model scientific hash;
- identical allowed background score arrays;
- identical calibrated thresholds;
- identical summary tables.

For this tiny CPU model, aim for exact reproducibility.

If exact reproducibility fails, investigate rather than merely loosening tolerances.

---

# 25. MPS

A new MPS training experiment is not scientifically necessary.

Task 0007 already established MPS compatibility.

You may run the existing MPS smoke tests as part of normal validation.

Do not perform a 1000-epoch MPS experiment.

Do not compare CPU/MPS speed.

---

# 26. Tests

Add or update meaningful tests for any new convergence/versioning behavior.

At minimum, where applicable, test:

- historical config remains unchanged;
- v2 config differs only in allowed fields;
- max-epoch parsing;
- early-stop behavior;
- canonical supersession logic;
- v1 artifact remains readable;
- v2 serialization/identity;
- artifact version mismatch handling;
- convergence-run provenance.

Do not add redundant tests just to inflate test count.

CI must remain independent of the real processed dataset.

---

# 27. Documentation

Create:

`docs/autoencoder-convergence.md`

Document:

## Motivation

Why Task 0007 did not establish convergence.

## Controlled protocol change

Exactly what changed and what did not.

## First-200-epoch reproduction

## Extended training

## Early stopping / convergence outcome

## v1 vs v2

## Canonical model decision

## Background calibration

## Reproducibility

## Test embargo

## Limitations

Explicitly state that no signal information was used.

---

# 28. Update compact autoencoder documentation

Update:

`docs/compact-autoencoder.md`

without rewriting Task 0007 history.

Add a concise note indicating whether:

- v1 remains canonical,

or

- v2 supersedes it after Task 0008.

Link to the convergence report.

Make the distinction between historical and current canonical artifacts explicit.

---

# 29. README

Update the main README minimally.

If convergence is established, state that the compact AE baseline is now finalized.

Do not advertise real anomaly-discrimination performance.

Do not add signal metrics.

---

# 30. Results artifacts

Create small curated Task 0008 results, e.g.:

```text
results/tables/final/
    task0008-autoencoder-convergence-history.csv
    task0008-autoencoder-convergence-summary.json
    task0008-autoencoder-thresholds.csv
```

and a curated figure such as:

```text
results/figures/final/
    task0008-autoencoder-convergence.png
```

Follow existing repository policy.

Do not commit large score arrays/checkpoints.

---

# 31. Runtime/resource observations

Report:

- epochs executed;
- best epoch;
- stopping epoch;
- training wall time;
- restored-model scoring time;
- peak RSS where practical.

These remain engineering observations, not hardware benchmarks.

---

# 32. Scope exclusions

Do NOT:

- change AE architecture;
- change latent dimension;
- change learning rate;
- change optimizer;
- change batch size;
- add a scheduler;
- run hyperparameter search;
- inspect test background;
- inspect test signal;
- train a particle-level network;
- implement a Transformer;
- implement ONNX;
- implement CoreML;
- quantize models;
- run latency benchmarks;
- implement TensorRT;
- implement hls4ml;
- implement trigger simulation.

---

# 33. Validation

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
- first-200-epoch equivalence check;
- extended canonical CPU training;
- restored-best validation;
- allowed background scoring;
- threshold calibration;
- independent reproducibility rerun;
- test-access audit;
- documentation-link validation;
- Git exclusion verification;
- `git diff --check`;
- final diff inspection.

Explicitly verify:

```text
test_background accessed: NO
test_signal accessed: NO
```

---

# 34. Definition of done

Task 0008 is complete when:

- task prompt/handoff exist;
- handoff index is updated;
- historical Task 0007 artifacts remain intact;
- v2 config exists;
- first 200 epochs reproduce Task 0007;
- extended training completes according to frozen rules;
- convergence status is determined;
- canonical v1/v2 decision is made using background-only information;
- a v2 artifact exists if justified;
- background calibration is updated if v2 becomes canonical;
- independent rerun reproduces the result;
- no test split was accessed;
- documentation clearly records the supersession decision;
- all tests pass.

---

# 35. Mandatory handoff

Update:

`docs/handoffs/0008-autoencoder-convergence.md`

with actual facts including:

- base commit;
- environment;
- reason for Task 0008;
- exact config difference from v1;
- first-200-epoch equivalence result;
- epochs executed;
- best epoch;
- stopping epoch;
- best training/validation MSE;
- v1 vs v2 improvement;
- convergence determination;
- canonical-model decision;
- artifact path/hash/size;
- background summaries;
- thresholds/FPR stability;
- reproducibility rerun;
- runtimes;
- test count;
- test-access audit;
- issues;
- rejected alternatives;
- next recommended task.

Update the handoff index.

Do not rewrite old handoffs.

---

# 36. Final response format

Return:

## 1. What was implemented

## 2. First-200-epoch reproduction

State whether Task 0007 was exactly reproduced.

## 3. Convergence result

Include:

- epochs executed;
- best epoch;
- stopping epoch;
- best training MSE;
- best selection-validation MSE;
- whether early stopping triggered.

## 4. Canonical model decision

Clearly state either:

**v1 remains canonical**

or:

**v2 supersedes v1**

and why.

## 5. Background validation and calibration

If v2 is canonical, provide the updated allowed background summaries and target/realized FPR table.

## 6. Frozen artifact

Include:

- artifact version;
- parameter count;
- size;
- scientific SHA-256.

## 7. Reproducibility

Report the independent rerun outcome.

## 8. Test embargo

Explicitly report:

```text
test_background accessed: NO
test_signal accessed: NO
```

## 9. Validation results

Include actual pytest count and relevant checks.

## 10. Files changed

Separate tracked from ignored/generated files.

## 11. Issues / deferred decisions

## 12. Recommended next task

If convergence is successfully closed, the expected next task is:

**Task 0009 — Particle-Level / Set-Aware Neural Baseline Design**

Do not automatically choose a Transformer.

The next model should first answer which compact particle-level architecture best fits the LatentTrigger research question and future hardware constraints.

## 13. Git commit and push commands

This section is mandatory and MUST be last.

Do NOT commit or push automatically.

Provide exact commands for:

```bash
git status
git diff

git add <only intended Task 0008 files>

git status
git diff --cached
git diff --cached --check

git commit -m "<specific conventional commit>"
git push
```

Selectively stage only intended Task 0008:

- source/tests if modified;
- v2 configuration;
- documentation;
- small curated result tables/figure;
- tiny v2 frozen artifact if created.

Never stage:

- raw data;
- processed multi-GB data;
- per-event score arrays;
- temporary checkpoints;
- logs;
- caches;
- unrelated work.

A likely commit message, if convergence is successfully resolved, is:

`fix: close compact autoencoder convergence`

Adjust it to match the actual outcome.

Proceed with **Task 0008 only**.
