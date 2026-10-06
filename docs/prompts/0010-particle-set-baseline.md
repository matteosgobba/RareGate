# LatentTrigger — Task 0010: Compact Particle/Set Baseline Implementation and Background Validation

You are continuing **LatentTrigger — Hardware-Aware Machine Learning for Real-Time LHC Event Selection**.

Tasks 0001–0008 established the data/evaluation foundation, PCA, and canonical compact AE v2. Task 0009 completed the **design only** of the initial particle/set baseline. No particle model has yet been implemented, trained, restored, reproduced, frozen, or calibrated.

This is **Task 0010 — Compact Particle/Set Baseline Implementation and Background Validation**.

Implement the selected design and execute its preregistered gates in order. This prompt authorizes the bounded dev check and, **only if the preceding gates pass**, full background-only training and independent reproduction within the existing resource limits.

Do not redesign the model or assume that the analytic budgets prove CPU feasibility.

## 0. Mandatory inspection and living memory

Before changing anything:

- locate the operational repository, distinguishing it from any read-only project mirror;
- read applicable instructions, `docs/development.md`, and `docs/project-memory.md`;
- inspect Git status, branch/upstream, HEAD/base, index, and recent commits;
- verify Task 0009's actual state, including any uncommitted prerequisite files; do not claim it is committed unless Git confirms this;
- preserve unrelated changes and snapshot initial hashes/diffs of any already modified files that this task must also update;
- inspect the Task 0009 prompt/handoff, `docs/particle-set-baseline-design.md`, `configs/models/particle_set_baseline_design_v1.json`, and its analytic budget CSV;
- inspect preprocessing/evaluation contracts, the frozen data configuration, processed reader/model-view code, existing training/stopping, evaluation, artifact, and ignore policies;
- verify small-file identities and relevant store/config manifests against the design before real reads.

The Task 0009 JSON and report are the exact methodological sources for this implementation. Investigate inconsistencies before training. Preserve their historical specification; create a separate executable configuration.

The living memory is evolutionary. Verify its current-state claims and update affected reasoning, results, limitations, goals, roadmap, and open questions before completion. Preserve existing handoffs and their index. Do not modify synced `sources/` references.

If Task 0009 remains uncommitted, record prerequisite content hashes and initial dirty state separately from Task 0010 changes. Do not automatically stage/commit those files or silently absorb unrelated work. Final Git guidance must make pre-existing prerequisite changes explicit rather than describe the entire dirty tree as Task 0010.

## 1. Records, configuration, and minimal implementation

Create the prompt and initial handoff before substantive changes:

```text
docs/prompts/0010-particle-set-baseline.md
docs/handoffs/0010-particle-set-baseline.md
```

Create an executable configuration, for example:

```text
configs/models/compact_particle_set_autoencoder_v1.json
```

It must preserve every scientific choice in design v1 and bind to its verified identity. Document the mapping from design-only fields to executable fields; metadata/schema adaptation is not permission to change architecture, numerics, training, scoring, or resource policy. Existing runners must continue rejecting the original `status: design_only` specification as an executable configuration.

Follow the minimal modules proposed in Task 0009:

```text
src/latenttrigger/models/particle_set.py
src/latenttrigger/training/particle_set.py
src/latenttrigger/models/particle_background.py
```

Use the repository's established interfaces where practical. Do not rewrite the framework, weaken existing artifact parsers, or change dependency versions without an actual implementation need. Keep unrelated PCA/AE behavior intact.

## 2. Exact architecture — 478 parameters

Implement in this construction order:

```text
e1:    Linear(4,16,bias=True) → ReLU
e2:    Linear(16,8,bias=True) → ReLU
local: Linear(8,2,bias=True), linear output

h = eight-channel e2 representation, padding zeroed
local_code = local(h), padding zeroed
g = masked mean of h over valid particles
decoder_input = concat(local_code, broadcast(g)), local then global

d1:    Linear(10,16,bias=True) → ReLU
d2:    Linear(16,4,bias=True), linear output
Y = reconstruction, excluded outputs exactly zero
```

Pooling sums/division use FP64; cast the resulting eight-value context to FP32 for the decoder. All Linear layers, parameters, reconstructions, gradients, and Adam state are FP32. ReLU is not in place.

Verify 478 parameters, 1,912 FP32 parameter bytes, and exact names/order/shapes from the design JSON.

No raw-input or hidden-feature skips to the decoder, attention, learned queries, positions, BatchNorm, Dropout, new heads, or auxiliary losses.

The code capacity is **`2*n_retained + 8`**, up to 776 values. It is a distributed particle code plus event context, not an eight-value event-only bottleneck. Preserve the documented small-cardinality and uniform-replication limitations.

## 3. Input, mask, and validation

Use the existing on-demand model view:

```text
X: FP32 [B,384,4]
M: boolean [B,384]
True = valid retained particle
False = padding
```

Preserve frozen channel order, scalers, transforms, `Nmax=384`, leading-pT retention, source-before-cast ordering, and zero padding after transformation. Do not refit or add feature transformations.

The public interface requires a nonempty prefix mask. An explicitly internal set kernel may accept a nonempty mask with holes for symmetry testing. Do not relax the reader/public contract.

Reject empty batches/events, unsupported devices, wrong shape/dtype, implicit casts, malformed masks, and nonfinite inputs anywhere, including padding. Validate the valid angular pair in FP64 using the design tolerance `abs(sin²+cos²-1) <= 2e-6`.

After finite-input validation, sanitize every excluded row to zero **before the first Linear layer**. Finite padding replacements, including very large finite values, must not affect valid output, context, score, or gradients. Padded local codes, outputs, and input gradients must be exactly zero.

Reject nonfinite parameters, relevant intermediates, outputs, losses, or gradients. Preserve failure evidence; do not drop events, clip tails, or substitute finite values for failures.

## 4. Differentiable loss and canonical score

For corresponding valid particle residuals `r = X - Y`, use exactly:

\[
d_i = \frac{r_{i0}^2+r_{i1}^2+0.5r_{i2}^2+0.5r_{i3}^2}{3},
\qquad s(X)=\frac{1}{n}\sum_{i:M_i}d_i.
\]

Convert X and Y to FP64 **before subtraction**. Residuals, squares, and loss/score reductions are FP64. The training cast/reduction must preserve autograd; do not detach or use a NumPy computation for the optimizer's loss.

`event_loss(X,Y,M)` returns one FP64 value per event. Training uses the equal-event mean over the actual batch size. Epoch summaries weight tail batches by their event count. Do not pool particles across events or divide by 384.

Sin/cos outputs remain unconstrained. No normalization, projection, atan2 residual, extra angular penalty, matching solver, or count term.

`score(X,M)` returns finite FP64 `[B]` scores on CPU, with larger meaning more anomalous. Use the same scientific formula and a documented deterministic reduction path for selection, reload verification, and background reporting. Test the formula independently on small known examples.

Distinguish online training objective from restored-model training score. Do not label this weighted objective ordinary unweighted MSE or compare its raw magnitude with PCA/aggregate-AE losses.

## 5. Stream particles and preserve population guards

Implement bounded particle loading from `ProcessedStore` and `EventBatch.model_view(nmax=384)`. Do not call the aggregate loader and describe its eight features as particles.

Reject forbidden/unknown roles and truth requests before store construction or population reads. Fit APIs accept training and selection backgrounds only; calibration must not be an optimizer/stopping argument. The dev gate accepts only its specified dev-training sample.

Record purpose, representation, population, allowed scope, and disabled test/label flags before each population request; update counts as batches complete. Preserve failed/interrupted audits.

Full canonical counts remain:

```text
train_background:                  699957
validation_selection_background:   74749
validation_calibration_background: 74823
```

Keep one verified store open per fresh run, following existing constructor integrity checks. Those checks are custody operations, distinct from population model/evaluation access. Include verification overhead in the appropriate process/resource accounting; do not bypass verification or repeatedly re-open the store per batch.

Cache allowed source IDs/shuffle indices, not a padded population. Stream at most 32 padded events. Keep labels, provenance, original counts, and physical aggregates outside the model input.

For shuffled training, use the minimal optional split-relative permutation iterator proposed in Task 0009: validate role, guards, membership, permutation coverage, and integer positions once per epoch; retain bounded `_batch` reads. Preserve the existing sequential API.

Repeated full split scans inside every shuffled batch are avoidable implementation overhead. Optimize that routing without changing membership/order semantics or exposing direct unaudited reads. Test malformed, duplicate, missing, and foreign indices before any particle read.

## 6. Meaningful synthetic acceptance tests first

Before real model-view reads, test:

- exact architecture/parameter count/order and configured initialization;
- known weighted residuals, angular seam, zero/off-circle predictions;
- equal-event means, actual tail batches, full-population aggregation;
- n=1, n=384, empty/B=0, malformed shapes/dtypes/masks, angular/nonfinite failures;
- valid-particle permutation invariance/equivariance, including aligned input gradients;
- internal consistently permuted masks while public non-prefix masks reject;
- finite padding invariance and exact-zero padding gradients/local codes/output;
- repeated particles and the documented uniform-replication property;
- finite nonzero valid gradients and the FP64 loss path back to FP32 parameters;
- deterministic shuffling, once-per-epoch coverage, source order, and retained tails;
- forbidden population refusal before construction/read and failed audit preservation;
- calibration inaccessible before every prerequisite gate passes;
- strict improvement/ties, patience, cap priority, best cloning/restoration;
- artifact roundtrip, corruption, schema/type/version/shape/identity rejection;
- resource failure interruption and refusal to publish/freeze/calibrate incomplete runs.

Use Task 0009's exact numerical tolerances/domain. Formula checks use FP64 `atol=rtol=1e-12`; same-environment canonical reruns require exact equality. Do not loosen tolerances to hide an implementation mistake.

CI tests use synthetic stores and controlled clocks/resource probes. CI must not need the real dataset or full training.

## 7. Bounded dev/resource gate

Run a disposable model in a fresh CPU process on exactly the first 1,024 source-ordered IDs in the frozen **dev `train_background`** subset.

Use batch 32 and the preregistered numerical/optimizer policy. At most three complete training passes, 96 optimizer steps, then one no-grad score pass on the same sample. No selection or calibration population access.

Measure loading/view preparation, complete train-pass times, score-pass time, relevant workspace/tensor memory, process RSS, and available system memory. Do not substitute network-only timings into the feasibility estimate.

Require all design limits:

```text
fresh-process whole dev gate:          <= 300 seconds
working tensors/workspace:            <= 512 MiB
process peak RSS:                     <= 6 GiB
system available memory before launch: >= 8 GiB
stop if system available memory:       < 4 GiB
```

Document how working tensors/workspace are accounted for, including temporaries. A tensor inventory estimate or passing the RSS limit alone is not a measured proof of the separate workspace limit.

Compute the frozen conservative extrapolation, using the maximum training-pass time:

\[
2\left(699957\frac{t_{train}}{1024}+74749\frac{t_{score}}{1024}\right)\le180\text{ s}.
\]

This is a feasibility gate, not an inference benchmark. No required loss decrease on this small sample selects model settings.

If the gate fails, preserve results and stop dependent real-data stages. Do not change batch size, CPU threads, device, horizon, architecture, or the factor of two. Do not repeat real dev optimization beyond the declared bounds as a hidden search. Correctness bugs may be repaired and tested synthetically; any further real attempt must remain within the original bounds or await a new explicit bounded decision.

Never promote dev weights/history to canonical status. After a successful gate, initialize canonical training from scratch in a new process.

## 8. Canonical CPU training — frozen policy

Only after synthetic correctness, compatibility, and the dev/resource gate pass, execute the full training/selection run.

Preserve all Task 0009 settings, including:

- seeds 1729; default FP32 Linear initialization in `e1,e2,local,d1,d2` order;
- a separate CPU shuffle generator seeded once and advanced across epochs;
- Adam lr 0.001, betas `(0.9,0.999)`, eps `1e-8`, weight decay 0;
- all other optimizer switches exactly as specified, including `foreach=False` and `fused=False`;
- batch/scoring batch 32, workers 0, no pinning/prefetch pool, retained tail;
- uniform training permutation without replacement from source-ordinal base order;
- source-ordinal selection/scoring order;
- CPU, one intra-op and one inter-op thread, fresh process;
- deterministic algorithms enabled with `warn_only=False`;
- no AMP, schedule, clipping, accumulation, or automatic device fallback.

Record actual software, thread, BLAS, and optimizer options. Use the narrowly documented compatibility rule if an optional Adam keyword is unavailable; do not upgrade dependencies to alter scientific behavior.

After each complete training epoch, score **all 74,749 selection events** using the canonical score and equal-event FP64 mean.

```text
improvement: selection_mean < best - 0.0
min_delta: 0
patience: 20 consecutive non-improvements
max_epochs: 200
exact ties: keep earliest best; increment bad-epoch count
```

Clone all best FP32 parameters on improvement. Patience wins if it is satisfied at epoch 200; otherwise the cap leaves convergence unresolved. A best epoch before the cap alone is not evidence that patience was satisfied.

Log small scientific history rows per completed epoch, and keep engineering times/resources separate. Partial/interrupted epochs cannot become completed history or selected checkpoints.

## 9. Enforce runtime ceilings during every real stage

Implement monitored, testable interruption; do not wait until a long run ends to discover a violated ceiling.

```text
each actual full train+selection epoch cycle: <= 180 seconds
fitting+selection per canonical run:          <= 36000 seconds
postfit stages per canonical run:            <= 3600 seconds
two complete canonical repetitions total:    <= 79200 seconds
```

Maintain the existing memory limits throughout. Define and record start/end boundaries consistently with the design, account for startup/store verification, and avoid silently excluding overhead to manufacture a pass.

Update the user periodically while monitoring long runs. Do not suspend progress merely because a preregistered run takes sustained work, but do stop at its explicit resource ceilings.

No automatic warm start, resume, partial-population canonical fit, cache of the padded population, device switch, batch adjustment, or horizon extension. Failed attempts do not reset limits to authorize unlimited retries.

If a gate or ceiling prevents the specified endpoint, retain ignored diagnostic outputs, audits, and completed history. Report the precise failure and convergence status; do not publish a finalized artifact or access calibration.

## 10. Best restoration and independent reproduction

If the first canonical run reaches the patience endpoint within all gates:

1. Restore the best state, not the last state.
2. Serialize a diagnostic candidate in an ignored run directory.
3. Reload it through strict model/config/identity validation.
4. Require exact parameter bytes and source-ordered selection score bytes/mean matching the selected record.
5. Execute a second independent fresh CPU run from initialization under the same configuration/store/code/environment and gates.
6. Require exact scientific history, shuffle progression where recorded, stopping/best epochs, parameters, selected selection scores, and scientific artifact identity.

Engineering wall times/RSS/timestamps need not match. They must not contaminate scientific identity or an exact history comparison.

Investigate any scientific mismatch. Do not loosen exact same-environment criteria or proceed to calibration after a failed reproduction. No second full run is required merely to repeat a first-run resource/convergence failure.

## 11. Freeze a separate particle-model artifact only after success

After convergence, restoration/reload verification, and exact independent reproduction succeed, curate the tiny transparent artifact, for example:

```text
artifacts/models/compact-particle-set-autoencoder-v1/model.json
```

Use a distinct model type and strict schema. Preserve PCA, aggregate AE v1/v2, and their loaders/artifacts. This adds a baseline for a different representation; it does not supersede compact AE v2.

Scientific content must include all fields required by Task 0009: ordered exact FP32 parameters; architecture; design/runtime/input versions; channel/mask/pooling/correspondence/cardinality/angular semantics; loss/score precision; source/preprocessing/processed/split/config identities; canonical-full scope; actual counts; training policy; best/stopping state; history identity; and successful gate/convergence status.

Use the established deterministic scientific hashing procedure; exclude paths, timestamps, timings, RSS, and machine metadata. Report file-byte hashes separately where relevant. A design or checkpoint hash is not a finalized trained-model identity.

Reject corrupted or incompatible artifacts, wrong model types, nonfinite/inexact FP32 values, missing/wrong parameters, mismatched source/config/splits, and dev/incomplete scope masquerading as canonical.

Add only a narrow ignore exception for the curated tiny artifact if needed. Temporary candidate JSONs, checkpoints, logs, score arrays, and run manifests remain ignored.

## 12. Postfreeze background scoring and calibration

Only after the previous gates pass, score training, selection, and calibration backgrounds in bounded source-ordered batches. Compact score vectors may remain in memory; do not persist per-event scores, reconstructed particle populations, or local codes.

Reproduce allowed score-byte hashes/summaries with the independently reproduced/reloaded model after freeze, within postfit budgets. Reuse existing summary, KS, threshold, operating-point, and uncertainty functions.

Calibrate only on `validation_calibration_background`:

```text
target FPRs: 0.1, 0.05, 0.01, 0.001
quantile: existing higher convention
accept iff: score > threshold
```

Verify frozen thresholds on selection background without retuning. Report accepted/total counts, realized FPR, absolute/signed relative deviations, Wilson 95% intervals, tail support, and existing zero-count handling.

Keep calibration out of model/epoch selection. Do not tune the score or objective after looking at calibration/diagnostics. Compare background stability and complexity descriptively; do not infer signal superiority.

## 13. Preregistered descriptive diagnostics

Implement the Task 0009 diagnostics exactly: retained/original multiplicity, truncation flag, retained-pT fraction, full-event scalar/max pT, and existing massless event mass.

Use ten equal-count postfreeze training-quantile bins with linear summary quantiles; merge tied edges, retain overflow tails, report merged/empty bins, and transfer edges unchanged to selection/calibration. Truncation has two groups.

Report counts, mean/median/p99/max score and frozen-threshold acceptance/intervals. Read diagnostic metadata separately; it is not a learned feature. No correction, clipping, extra score, or post-hoc bin choice.

Selection was used for early stopping. Calibration estimates thresholds. Describe their respective reuse honestly; neither supplies all forms of independent validation.

Preserve count blindness, mean dilution, local-code capacity, truncation, angular-output, and limited-context caveats even if diagnostics look favorable.

## 14. Curated results and documentation

Create `docs/particle-set-baseline.md` documenting actual gate outcomes, architecture/score, loader guards, training/convergence, restoration/reproduction, artifact, postfreeze results where authorized, resources, limitations, and commands to reproduce.

Create small curated Task 0010 outputs as applicable:

- gate/resource summary;
- executed training history and scientific summary;
- background score summary and threshold table if calibration is authorized;
- preregistered diagnostic profiles if reached;
- a clear training/selection figure if full epochs execute.

Mark analytic estimates versus measurements and diagnostic/dev versus canonical scope. Do not produce empty success tables or invent thresholds/hashes for stages not reached. Keep large/local outputs ignored.

Update README, handoff/index, and the living memory in place. Add a concise dated implementation-status link to the Task 0009 design report only if useful; preserve its original design choices and historical handoff.

Memory must distinguish implemented/tested code, dev feasibility, canonical convergence, exact reproduction, freeze, and calibration. A failed gate can leave useful implementation complete while the canonical baseline remains pending. Update objectives, rationale, measured state, limitations, roadmap, open questions, and revision history accordingly.

## 15. Validation and embargo

Run the relevant implementation checks in the established environment: editable installation/import, dependency consistency, Ruff lint/format, full synthetic pytest suite, CPU model smoke, artifact/config checks, documentation links, exclusions, historical preservation, and `git diff --check`/final diff review.

Existing generic MPS smoke may be run if available. It does not establish particle-model MPS compatibility: the canonical particle model and its FP64 policy are CPU-only in this task. No MPS particle training experiment or speed comparison.

Real-stage validation is conditional on the gate order. Report the actual test count and each reached/not-reached stage; do not claim full training/calibration passed when only synthetic/dev checks passed. Hosted CI is unverified unless actually observed.

Under every outcome:

```text
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

No test losses, scores, distributions, AUC/AP, signal efficiency, final-unblinding invocation, or changes to the test-access gate. No exports, quantization, latency benchmarking, Transformer, NVIDIA/TensorRT, hls4ml, or trigger simulation.

## 16. Completion states and next task

Report one precise outcome:

- **Canonical baseline completed:** all gates pass, patience endpoint reached, exact reproduction succeeds, model freezes, and background calibration/diagnostics complete.
- **Implementation completed; canonical baseline pending:** a documented correctness/resource/convergence/reproduction gate blocks later stages. Preserve actual completed work and explain the smallest next decision; do not call training finalized.

If successful, the next proposed task is **Task 0011 — Apple Silicon Inference Benchmark Protocol and Foundation**, subject to the live index. It must define measurement/compatibility boundaries before exports or speed claims.

If unsuccessful, the next task must instead address the demonstrated blocker through a bounded, explicit versioned decision. Do not assume an automatic epoch extension or device/model change. Do not execute the next task here.

## 17. Final response and manual Git commands

Return:

1. What was implemented and exact design/config fidelity.
2. Synthetic validation and actual pytest count.
3. Dev gate measurements, extrapolation, memory accounting, and pass/fail.
4. Canonical training result, if reached: epochs/best/stop/reason, online/restored training objectives, full-selection mean score, convergence and resource limits.
5. Restoration and independent reproduction outcome.
6. Frozen artifact path/type/version/count/size/scientific hash, only if justified.
7. Background summaries, thresholds/FPR table and diagnostics, only if reached.
8. Explicit test-access audit.
9. Project-memory changes, completion status, limitations/blockers, and next task.
10. Actual intended files versus pre-existing changes and ignored/generated outputs.
11. **Exact Git commit and push commands — mandatory and last.**

Do not stage, commit, or push automatically. Provide status/diff, selective staging of the actual reviewed Task 0010 files, staged status/diff and `git diff --cached --check`, a suitable Conventional Commit, and the correct push command for the actual branch/upstream.

Handle pre-existing Task 0009/unrelated changes explicitly; do not claim ordinary whole-file staging isolates Task 0010 content in a file already modified beforehand. Provide a concrete separate prerequisite-review/commit sequence where needed, without performing it automatically or mixing histories silently.

Never use broad staging or include raw/processed data, per-event arrays, checkpoints, caches, logs, or unrelated work. Use an outcome-appropriate commit message; for a successful finalized baseline, a possible message is `feat: add compact particle set anomaly baseline`. For a gated outcome, state implementation and the unresolved baseline accurately.

Proceed with **Task 0010 only**.
