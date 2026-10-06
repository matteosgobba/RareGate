# LatentTrigger — Task 0009: Particle-Level / Set-Aware Neural Baseline Design

You are continuing development of **LatentTrigger — Hardware-Aware Machine Learning for Real-Time LHC Event Selection**.

Tasks 0001–0008 are complete. Verify the actual repository state before proceeding.

Task 0008 closed compact-autoencoder convergence under the unchanged background-only early-stopping protocol:

- canonical compact AE: `compact-autoencoder-v2`;
- architecture: `8 → 6 → 3 → 6 → 8`, 155 parameters;
- best epoch: 381; stopping epoch: 396;
- restored selection-background MSE: approximately 0.21447599;
- first 200 epochs exactly reproduce Task 0007;
- independent CPU rerun reproduces the documented result;
- no real test model/evaluation access.

Preserve PCA and both AE generations. Do not repeat their training without a concrete integrity problem.

This is **Task 0009 — Particle-Level / Set-Aware Neural Baseline Design**.

The question is:

> What is the simplest defensible unsupervised model and event score that use the existing particle representation, capture information absent from the eight aggregates, and remain feasible for later training and hardware evaluation?

This task must produce **one concrete, implementation-ready design**, supported by a bounded comparison and explicit mathematical/resource contracts.

Do not implement or train the new neural baseline in this task. Do not automatically choose a Transformer.

## 0. Repository inspection and living memory

Before substantive work:

1. Locate the operational repository; distinguish it from any ChatGPT project mirror.
2. Read applicable repository instructions, `docs/project-memory.md`, and `docs/development.md`.
3. Inspect Git status, branch/upstream, HEAD/base, recent history, and unrelated changes.
4. Verify Task 0008 completion against its report, handoff, configuration, curated results, and canonical artifact. Do not infer remote push or hosted CI success from local Git history.
5. Read:
   - `docs/preprocessing-contract.md`;
   - `docs/preprocessing-pipeline.md`;
   - `docs/evaluation-protocol.md`;
   - relevant Task 0004/0005 reports and handoffs;
   - `docs/compact-autoencoder.md` and `docs/autoencoder-convergence.md`;
   - `configs/data/lhco_rnd_v5.json`;
   - processed-store reader/model-view code;
   - existing background access guards, scoring/calibration interfaces, and artifact policy.

The project memory is a **living explanation of vision, objectives, reasoning, decisions, evidence, roadmap, and open questions**. It complements prompt/handoff records; it does not replace them.

Its current wording is not an absolute plan. Reconcile it with verified files and current user instructions. Revise proposals and project direction when justified. Changes to established scientific contracts still require an explicit versioned decision; do not silently change them.

Preserve existing user-authored memory content and unrelated work, including an untracked memory file. Update the operational `docs/project-memory.md`; never edit read-only synced `sources/` files.

## 1. Task records and deliverables

Save the actual task prompt before substantive work and create the initial handoff:

```text
docs/prompts/0009-particle-set-baseline-design.md
docs/handoffs/0009-particle-set-baseline-design.md
```

Create:

```text
docs/particle-set-baseline-design.md
configs/models/particle_set_baseline_design_v1.json
results/tables/final/task0009-particle-set-design-budget.csv
```

Update:

```text
docs/handoffs/README.md
docs/project-memory.md
```

Update `docs/development.md` minimally if it does not already require every task to read and maintain the living memory alongside existing records. Add concise README links/status only where useful.

The design JSON must explicitly declare `status: design_only` and a design/schema version. It is a specification, not a trained model artifact or an already supported training configuration. Do not modify existing runners merely to accept it.

Do not rewrite historical handoffs or Task 0008 results.

## 2. Preserve the test embargo

Real model/evaluation requests for these populations remain forbidden:

```text
test_background
test_signal
```

No test scores, losses, physics distributions, latent distributions, AUC, AP, signal efficiency, or test-background FPR.

Use existing reports, frozen configuration, and manifests first. If a specific design question requires new real-data inspection, use only a small, explicitly bounded `train_background` sample through the guarded processed reader, with test/label access disabled. Record the reason, population, count, and access audit.

Selection background is reserved for the future preregistered selection protocol. Calibration background must not choose this design, its objective, dimensions, or training policy. No new calibration access is needed in Task 0009.

Whole-file integrity operations remain distinct from model/evaluation access. Do not rerun costly full-store verification or rebuild preprocessing merely as ceremony for a design task.

Do not train or score a new model on any real population in this task.

## 3. Reuse the frozen particle input

Inspect and reuse the actual current contract:

```text
features: [B, 384, 4], FP32
mask:     [B, 384], boolean
True = real retained particle
False = padding
```

The ordered channels are:

1. standardized `log1p(pT / 1 GeV)`;
2. standardized signed eta;
3. `sin(phi)`;
4. `cos(phi)`.

Read exact scalers and identities from the frozen JSON. Do not copy rounded values, refit statistics, rotate events, remove event scale, clip features, or add unavailable particle types/charges/masses/jet labels.

Preserve `Nmax=384`, deterministic leading-pT retention, transformed-then-zero-padded inputs, and existing split membership. The canonical ragged store retains all physical particles; the model view is truncated.

No original-slot features or input position embeddings for the initial permutation-symmetric set baseline. Sorting for deterministic retention is not a substitute for explaining the model's symmetry.

Original multiplicity and retained-pT fraction are diagnostics unless explicitly included in the selected design with a scientific rationale and versioned model-input contract. Labels, row IDs, fingerprints, and split names are never model inputs.

## 4. Bounded architectural comparison

Compare at most three concrete directions:

- a shared particle MLP with masked invariant pooling, an event bottleneck, and an explicitly specified decoder/objective;
- a compact permutation-equivariant particle model with event context and an explicitly constrained reconstruction or alternative unsupervised objective;
- a compact attention-based set model, considered only where interactions justify its extra complexity.

Use primary sources for externally grounded architecture claims. Relevant starting points are:

- [Deep Sets](https://arxiv.org/abs/1703.06114), for invariant/equivariant set constructions;
- [Energy Flow Networks: Deep Sets for Particle Jets](https://arxiv.org/abs/1810.05165), for particle-physics set representations;
- [Set Transformer](https://arxiv.org/abs/1810.00825), for attention-based set modeling;
- [Learning Representations and Generative Models for 3D Point Clouds](https://arxiv.org/abs/1707.02392), for set reconstruction as a related design reference.

Separate what those papers establish from your proposed adaptation. A particle-set encoder or supervised classifier is not by itself a complete unsupervised anomaly detector.

For each candidate compare:

- particle and event information retained;
- symmetry and cardinality handling;
- actual unsupervised objective and score;
- information paths and possible trivial solutions;
- parameter, compute, activation, and scoring costs;
- feasibility on the 16 GiB development machine;
- operator simplicity and likely later export obstacles;
- limitations and reason to select/reject it.

Do not train candidates, run a search, or choose using published signal-performance rankings on another problem. Select **one** design using methodological completeness, simplicity, and resource reasoning. Do not leave the final decision as an unresolved menu.

## 5. Specify the selected architecture completely

Provide an ordered layer table and pseudocode with:

- exact inputs and mask semantics;
- every layer width, activation, bias, and shared operation;
- intermediate shapes;
- pooling/reduction formula and denominator;
- latent dimensions and all local/global information paths;
- decoder or other objective head;
- exact output shape and output-validity convention;
- inference inputs/outputs;
- analytic trainable parameter count, including queries/embeddings if used.

Explain how this model uses particle structure beyond reproducing the existing eight aggregates.

Trace whether target information can bypass the intended bottleneck through particle inputs, local embeddings, skip connections, masks, counts, or decoder conditioning. If local latents are retained, state their total capacity and the resulting compression claim accurately.

For a pooled event latent and particle decoder, explain how different output particles are generated. A shared decoder receiving only the same event vector for every output needs an explicit mechanism to produce distinct outputs. Distinguish output-generation queries from forbidden input slot identities; any such design choice must be documented.

Avoid auxiliary heads, regularizers, normalization layers, and architectural additions without a specific need. Do not assume the set model should share the AE's three-dimensional latent merely for superficial comparability.

## 6. Resolve reconstruction correspondence and exact loss

If reconstruction is selected, define the mathematical objective completely:

- feature-space distance and exact channel weights;
- treatment of the angular pair and off-circle predictions;
- input/output cardinalities;
- valid masks in both directions;
- matching or correspondence rule;
- sums/means and every denominator;
- aggregation across events and batches;
- any additional loss terms and fixed weights.

Choose and justify the applicable approach: equivariant particle correspondence, canonical rank reconstruction, Chamfer-style nearest-neighbor reconstruction, assignment/transport, or a clearly specified alternative.

Do not apply slot-wise MSE between an unordered generated set and the input prefix without a justified correspondence contract. If correspondence is preserved by an equivariant decoder, demonstrate that property and audit its information bypasses. If canonical ordering is used, state the resulting symmetry and where canonicalization occurs.

For nearest-neighbor/set matching, address duplicate/collapsed outputs, unequal cardinalities, tie behavior, and whether the objective detects multiplicity differences. For assignment/transport, include solver/iteration costs and dependencies.

The sin/cos representation must handle the phi seam without introducing a naive linear phi residual. State whether predictions remain unconstrained, are normalized with a defined zero-norm rule, or use an explicit penalty.

If a different unsupervised objective is selected, specify it equally precisely and address collapse, scale degeneracy, and why its score is meaningful. Do not invent labels or introduce signal-contaminated training.

## 7. Freeze one event score

Define exactly one canonical finite scalar `s(X)` with **larger = more anomalous**.

Specify its relationship to the training objective, inference precision, reduction precision, mask, cardinality, and any matching/normalization. State whether the deployed scorer needs reconstructed particles, pairwise distances, an assignment solver, or other operations beyond the network forward pass.

For particle-wise residuals, explain why the chosen sum/mean/weighting is appropriate. A masked mean must divide by the valid-particle count, not 384; event weighting must not change accidentally across batches.

Distinguish original multiplicity from retained multiplicity. If reconstruction is conditioned on the observed retained count, state that count mismatch is not independently reconstructed. If count contributes to the score, specify its term and weight before training.

No post-hoc multiplicity correction, score-component selection, or tail clipping. Additional components may be descriptive diagnostics but must not silently become alternative canonical scores.

Keep PCA and compact-AE score definitions unchanged. Their raw loss/score magnitudes are not directly comparable with a different particle-space objective. Lower background loss will not establish better signal discrimination.

## 8. Mask, symmetry, and edge-case contract

Specify the required behavior and future tests for:

- permutation of valid particles, with the mask transformed consistently;
- invariant event score/latent where claimed;
- equivariant particle outputs where claimed;
- finite changes in padded values having no effect on valid outputs or score;
- no gradients from excluded padding;
- one-particle and full-384-particle events;
- truncated events and equal-pT/tie cases;
- empty/all-padding events rejected consistently with the nonempty-event contract;
- malformed shape/dtype/mask and nonfinite values;
- repeated particles and degenerate matching cases;
- angular values on opposite sides of the phi seam.

Separate the reader's prefix-mask contract from the mathematical symmetry test. A reader accepting only canonical prefixes should not be silently weakened; test valid-particle permutations within that contract or specify an internal set-kernel boundary.

Define numerical tolerances where floating-point reduction order prevents bitwise permutation equality. Do not claim rotation invariance, infrared/collinear safety, or other physics properties without establishing them.

## 9. Quantify network and scoring budgets

For the selected design calculate:

- parameter count and FP32 parameter bytes;
- input/mask/output bytes;
- main forward multiply-accumulate counts with a stated convention;
- largest intermediate tensor shapes/bytes;
- separately, loss/anomaly-scoring cost;
- scaling with retained count, `Nmax`, latent width, and batch size;
- approximate training storage, including gradients, optimizer state, and relevant saved tensors.

Show at least batch sizes 1 and 32 at `Nmax=384`. If the preregistered training batch differs, include it too.

Use consistent units and expose arithmetic assumptions in the budget table. Label estimates and lower bounds honestly; they are not measured peak RSS or latency.

A linear-cost encoder does not make the entire detector linear-cost if decoding, matching, or scoring is quadratic. Include any `N×N` distance/attention tensors, head counts, solver work, and potential temporary broadcasts. Describe chunking only where it preserves the exact objective.

Set explicit numerical implementation/training memory budgets with headroom for the OS, runtime, and mapped store. Do not materialize the full population as a padded tensor.

Discuss likely operator portability without installing export libraries, creating exports, or claiming demonstrated backend support, latency, speedup, or trigger readiness.

## 10. Preregister the future training and convergence protocol

Before any future training, specify concrete initial values for:

- seed, initialization, optimizer and all optimizer options;
- learning rate, batch size, shuffle policy, workers, tail-batch behavior;
- precision, device policy, and deterministic settings;
- objective and event weighting;
- selection metric, checkpoint rule, tie handling, `min_delta`, patience, and maximum epochs;
- best-state restoration and independent restored-score verification;
- reproducibility rerun and artifact/provenance requirements.

Use training background for fitting and selection background for the fixed stopping rule. Calibration background is accessed only after model selection/restoration/freeze.

CPU is the initial canonical reference. Evaluate feasibility analytically; do not assume this much larger input has the tiny AE's training cost. Define a future bounded smoke/dev resource gate and numerical wall-time/memory ceilings before authorizing a full run in the implementation task.

Do not copy AE batch size 4096 or its horizon mechanically. Choose justified initial values without search. Any fallback device/batch policy must be explicit and versioned before a canonical run; resource observations must not silently select a scientifically different model.

If the future epoch/resource ceiling is reached without the fixed stopping criterion, the outcome is **convergence unresolved**, not a finalized baseline. A new bounded methodological decision must precede any extension or training-policy change. Preserve this lesson from Tasks 0007–0008.

No training is authorized by this preregistration in Task 0009.

## 11. Future calibration and background diagnostics

Preregister reuse of the current evaluation framework:

```text
target FPRs: 0.1, 0.05, 0.01, 0.001
calibration: validation_calibration_background
quantile: existing higher convention
accept iff: score > threshold
```

Plan score summaries, counts, threshold transfer, KS diagnostics, and existing finite-sample intervals. Thresholds must not be retuned against selection or test data.

Plan descriptive background diagnostics against retained/original multiplicity, truncation, event scale, and the existing mass proxy. Since selection background is used for early stopping, distinguish that diagnostic population from a completely untouched model-validation sample.

Preserve tails and report limitations. Diagnostics after calibration must not feed back into architecture, loss weights, or score normalization within the same supposedly frozen run.

No thresholds or new score distributions are computed in Task 0009.

## 12. Implementation specification and acceptance gates

Define the next task's minimal modules/interfaces, batch-loading strategy, tests, artifact representation, scientific identity fields, and compatibility checks. Reuse existing guards and evaluation code; do not propose a framework rewrite.

The particle loader must stream bounded model views from the ragged store, reject forbidden populations before reads, and record access. Do not reuse the aggregate loader while describing its output as particles.

Scientific identity must include exact architecture, ordered parameters once trained, input/preprocessing/split identities, loss/score semantics, and training configuration. Keep timestamps, paths, and engineering timings outside scientific identity. A design hash is not a trained-model hash.

Specify staged acceptance gates: synthetic correctness → bounded dev/resource feasibility → authorized canonical training → restoration/reproduction → freeze → calibration. Explain which gate failure blocks later stages.

Propose **Task 0010 — Compact Particle/Set Baseline Implementation and Background Validation**, subject to the live task index and the design's resource gate. Do not execute it automatically.

## 13. Design validation

Validate within this task:

- design JSON parses and agrees with the report;
- tensor shapes, parameter count, units, and budget arithmetic;
- hand-computable synthetic examples of the selected loss/score;
- mask/cardinality/permutation/angle edge cases implied by those formulas;
- completeness of training/convergence/calibration preregistration;
- local documentation links and consistent current-state wording;
- intended-file scope, historical preservation, and `git diff --check`.

Small standalone calculations on synthetic values are permitted. Do not build a trainable network or training loop under the label of a design check. New production code, dependencies, and CI changes are outside scope.

Do not add redundant tests or rerun full-data training/store checks for documentation-only changes. Report checks actually performed, with any unverified implementation behavior clearly labeled as future acceptance criteria.

## 14. Update project memory and handoff

Before completion, update the affected memory sections **in place**:

- latest completed task: design completed, where justified;
- selected architecture/objective and rationale;
- rejected alternatives and reconsideration conditions;
- representation, cardinality, matching, and scoring limitations;
- resource targets, future gates, roadmap, and next task;
- resolved/new open questions and short revision entry.

Keep PCA/AE v2 canonical state and verified results accurate. Explicitly mark the particle model **designed; implementation/training/calibration pending**. Do not add fictitious trained hashes or performance results.

The memory may evolve beyond its earlier proposals; explain durable changes and motivation. Keep execution chronology and detailed checks in the Task 0009 handoff. Update the handoff index and protocol routing without replacing existing records.

The handoff must contain base commit/environment, inspected evidence, candidate comparison, final decision, exact score/loss contract, parameter/resource calculations, future training policy, design validation, access audit, limitations, files, and next step.

## 15. Definition of done and exclusions

Task 0009 is complete when one selected design is specified well enough to implement without inventing its architecture, objective, score, cardinality handling, or stopping policy; budgets and synthetic formula checks agree; task records and living memory are updated; and the embargo is intact.

If no candidate passes the scientific/resource requirements, document the precise unresolved issue and the smallest next decision. Do not manufacture a complete design or begin experiments to hide it.

Do not perform new-model implementation/training, hyperparameter search, AE/PCA retraining, preprocessing/split changes, real signal/test evaluation, exports, quantization, latency benchmarks, NVIDIA/TensorRT, hls4ml, or trigger simulation.

## 16. Final response and manual Git delivery

Return:

1. What was designed, explicitly distinguishing it from implemented/trained work.
2. Candidate comparison and selected design with rationale.
3. Exact architecture, shapes, latent capacity, and parameter count.
4. Loss, event score, mask, permutation, cardinality, and angular contracts.
5. Resource budget, assumptions, and future feasibility gates.
6. Preregistered training, convergence, and calibration policy.
7. Design validation actually performed and remaining implementation checks.
8. Test-access audit, explicitly stating:

   ```text
   test_background model/evaluation accessed: NO
   test_signal model/evaluation accessed: NO
   ```

9. Project-memory changes, limitations, and next task.
10. Files changed, separating intended tracked files from local temporary outputs.
11. **Git commit and push commands — mandatory and last.**

Do not automatically stage, commit, or push.

Provide exact commands for status/diff, selective `git add` of the actual intended Task 0009 files including the memory update, status/staged review, `git diff --cached --check`, an appropriate Conventional Commit, and push for the actual branch/upstream.

Replace all placeholders with the reviewed file list and actual branch information. Preserve unrelated staged changes; do not use broad staging or include data, caches, logs, models, or unrelated user work. A suitable commit message if the design is completed is:

```text
docs: define compact particle set baseline
```

Proceed with **Task 0009 only**.
