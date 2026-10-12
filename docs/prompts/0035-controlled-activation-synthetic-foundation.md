# LatentTrigger — Task0035: Synthetic Foundation for the Controlled Activation Study

You are continuing **LatentTrigger**. Perform **Task0035 only**.

## Objective and authorization

Implement and validate the smallest software foundation for Task0034's paired nonlinear/linear aggregate-autoencoder comparison. Make model construction, initialization and row-order pairing, own-checkpoint restoration, score/calibration arithmetic, shared-event uncertainty and acceptance lifecycle reviewable on synthetic fixtures.

This prompt authorizes additive implementation, ordinary iterative synthetic software validation, and bounded native synthetic integration. Synthetic model instantiation, forwards, reconstruction, calibration and optimizer updates are permitted within the declared test scope. They must be reported separately from operational scientific work.

It authorizes **zero operational population requests, feature/score/membership/fingerprint-array loads, real-data fitting or calibration, confirmation scoring, event-payload acquisition, or historical campaign replay**. Task0034's six future fits and resource projections are not an execution grant. Do not start Task0036 automatically.

## 1. Verify state and preserve the accepted design

Read applicable instructions, `docs/development.md`, living memory, Task0034's actual prompt/protocol/sidecar/summary/handoff, relevant historical AE model/training utilities, and the scoped Task0030/0033 clock, assertion, resource and synthetic-validation helpers.

Planning inspection on 2026-10-12, Europe/Rome found:

- Clean `main` tracking `origin/main`, empty index.
- HEAD `f27ce613565fff4d5107b1699af485afb582edd3`: committed Task0034.
- Memory revision 1.29.
- Task0034 is `design_only`; zero confirmation sources accepted.

Reconfirm actual state. Preserve unrelated changes. Save the actual prompt and initial handoff before implementation:

- `docs/prompts/0035-controlled-activation-synthetic-foundation.md`
- `docs/handoffs/0035-controlled-activation-synthetic-foundation.md`

Bind the raw-byte identities of Task0034's design artifacts as prerequisites. Preserve their scientific choices, historical AE/PCA source and validators, model parameters, transformations, thresholds, reports, accepted arrays, receipts and campaign states. Add new research code rather than weakening historical validators to accept a linear model.

Task0032 remains the completed baseline; Task0033 remains exploratory; all three evaluated populations remain permanently exposed. Particle192/192 remains consumed with canonical training deferred. Task0025 remains a failed performance campaign. No allowance reset, heatmap repair or new source search is required here.

## 2. Implement a separate, narrow research schema and factory

Use a dedicated namespace, such as `src/latenttrigger/research/controlled_activation/`, with only the helpers needed by this task. A strict implementation-test configuration, such as `configs/research/controlled_activation_synthetic_v1.json`, must reference the unchanged Task0034 design and identify itself as synthetic-only.

Accept exactly the two prescribed arms, fixed seeds1729/1730/1731, eight frozen feature names/order, FP32 inputs/forward and the biased structure8→6→3→6→8. Both arms have155parameters. Nonlinear uses the two historical ReLU locations; linear substitutes identity there. Latent/output remain linear. PCA-three stays disabled and unimplemented in this task.

Preserve the exact future training contract: CPU, one native thread, zero loader workers, deterministic algorithms, Adam learning rate0.001 and the resolved Task0034 options, batch4096 with complete tails, max1000epochs/patience15/min_delta0. Bind actual dependency/build identities and fail on incompatible resolved settings; do not silently accept changing optimizer defaults.

Define a visibly separate bounded synthetic profile for tiny fixtures and test termination. It cannot become a new canonical training recipe or an arbitrary override/unsafe flag. No operational CLI, downloader, full-store reader or real-background run path is to be exposed in Task0035.

On synthetic tensors, verify the nonlinear factory against a freshly initialized historical `CompactAutoencoder` under the same controlled seed/initialization. Verify that the linear factory implements the intended affine composition. This does not compare against operational checkpoints or establish scientific performance.

## 3. Prove initialization and actual loader pairing

Create one fixed-order named FP32 weight/bias initialization document per seed and copy its tensors into both arms. Bind names, shapes, dtype, finite values and raw tensor bytes. States must own independent storage: changing one arm cannot mutate the other arm or the initialization record. Hash equality alone is not a storage-alias test.

Separate initialization RNG effects from the local loader generator. Preserve the existing historical loader semantics: its `RandomSampler` and `DataLoader` share the local CPU generator; loader base-seed consumption and advancement across epochs are part of the recipe.

Instrument the batches actually emitted without a second sampler pass, an extra random draw, per-epoch reseeding or materializing another full permutation. Hash ordered row indices as consumed, including complete tails, with coverage/uniqueness/count checks. Pairing evidence must describe actual consumed order, not merely matching seed integers or generator states.

Require identical initial tensor hashes and permutation hashes for every common completed epoch. An arm may stop earlier under its own selection history; absence of later epochs is disclosed, not repaired by retraining. Reject mismatched seed/arm/order/completeness before accepting a pair. Do not export row permutations.

Test that instrumentation leaves the historical synthetic loader stream unchanged, that the stream advances across epochs, and that a dataset with4097rows yields the exact4096+1tail. Tiny native training fixtures may use fewer rows under the synthetic profile; the canonical batching contract still needs its own meaningful synthetic check.

Restore caller Python/NumPy/Torch RNG, deterministic and thread state on success and exceptions where the underlying runtime permits restoration. Document nonrestorable process-global settings and isolate them in workers.

## 4. Implement independent selection and state restoration

Reuse unchanged pure utilities when compatible, or add a thin separate research adapter. Maintain equal-event mean reconstruction loss, including incomplete batches, and prohibit optimizer mutations during selection/calibration/evaluation.

Each arm owns its best state, selected by strict `loss < best_loss` with earliest ties and15consecutive nonimprovements. Restore its own selected weights; verify parameter bytes and selected-state score identity. Cap endings and divergent stopping epochs are valid outcomes, not convergence proof.

Test strict ties, repeated nonimprovements, later deterioration, divergent arm stopping histories, state-copy independence, nonfinite losses, missing/malformed checkpoints, incomplete training, and restoration failures. Synthetic scripted loss histories may test stopping semantics without spending additional optimizer steps in the native integration.

Use a separate arm-aware research artifact identity and a safe finite parameter representation. Reject missing/extra names, wrong shapes/dtypes, wrong arm/seed/design, incompatible provenance or altered identities. A synthetic linear artifact must never load as an accepted historical AE-v2 artifact. No pickle or historical-checkpoint mutation.

Only owned synthetic fixtures/checkpoints may be written and reloaded for tests. Keep temporary tensors/checkpoints ignored; curate hashes/statuses rather than model weights.

## 5. Implement frozen score and calibration semantics

Convert FP32 input and reconstruction to FP64 **before** subtraction; sum eight squared residuals. Require finite nonnegative FP64 scores with high-score orientation. Test a case that distinguishes this arithmetic from FP32 subtraction followed by conversion.

For each synthetic restored arm/seed, compute its own four thresholds with NumPy `higher` at0.1/0.05/0.01/0.001 and strict `score > threshold`. Preserve the Task0034 primary alpha0.001. Test ties and exact quantile indices, zero/equal scores, altered threshold provenance and separation of historical thresholds from new-arm thresholds. Synthetic calibration does not calibrate an operational model.

API role checks must keep fitting/selection/calibration distinct and reject test/signal/confirmation roles from development before any data-provider call. In-memory synthetic providers are sufficient; do not build a real numerical adapter or construct `ProcessedStore`.

## 6. Implement paired aggregate inference and decision gates

Use the fixed six-candidate order: nonlinear then linear for seed1729, then1730, then1731. Accumulate the64six-bit primary acceptance-pattern counts in a streamable aggregate. Validate Boolean decisions, complete candidate coverage, exact nonnegative integer counts, pattern order and denominator consistency. Merge chunks without changing results or exporting event decisions.

For each event, `D_i = sum_seed(A_N - A_L)/3` lies in[-1,1]. Compute its mean and unbiased sample variance from the pattern counts, preserving all within-event dependence. Also derive all six individual rates and seed-specific paired contrasts. N is the source-event denominator, never3N.

Use integer or otherwise demonstrably stable moment arithmetic to avoid overflow/cancellation in large, sparse counts. Test against direct synthetic event calculations and rational/integer reference moments, including fully correlated seeds, opposing decisions, all64patterns, zero discordance and chunk merging.

Implement the Task0034 two-sided empirical Bernstein halfwidth for N≥2:

`h = sqrt(2*V*ln(4/delta)/N) + 7*R*ln(4/delta)/(3*(N-1))`.

Verify the affine range scaling and two-tail allocation against [Maurer and Pontil2009, theorem4](https://arxiv.org/pdf/0907.3740). R=2 for paired differences; R=1 for rates. Use unbiased sample variance. Clip displayed endpoints to the possible mean range, but precision uses unclipped h. Constant observations retain positive uncertainty; N<2 is explicitly undefined/inconclusive.

Preserve family error0.05: signal contrast0.025, background paired contrast0.0125, and0.0125/6 for each background rate. Separate individual Wilson95% and exact one-sided zero-rate bounds retain their conditional/descriptive status; their overlap is not the comparison test. No p-values, AUC/AP, ROC/PR or subgroup searches.

Implement the unchanged gates: six simultaneous FPR intervals wholly within[0.00075,0.00125]; paired background upper≤0.0001; signal halfwidth≤0.0001; background contrast halfwidth≤0.0001; individual background halfwidth≤0.0002; practical nonlinear advantage lower>0.0002. Preserve the stated linear-advantage/equivalence/negative/inconclusive conditions.

Make all gate results and validity/completeness reasons explicit. Resolve overlapping descriptive labels with documented precedence or separate Boolean fields; do not silently change any scientific boundary. Missing source acceptance, model, pairing, threshold freeze, lifecycle acceptance, i.i.d. justification or adequate precision prohibits a confirmation claim regardless of favorable synthetic counts.

Test equality at every boundary, invalid/missing inputs, stability failure, precision failure, nonlinear/linear advantage, equivalence and inconclusive outcomes. Reproduce the design's236843zero-variance signal floor and planning minimum-N cases from synthetic aggregate counts/arithmetic. Small fixtures must remain inconclusive under the original precision requirements. Do not relax criteria to make the current source shortlist or toy examples pass. Numerical synthetic checks do not prove statistical coverage; explain the theorem assumptions.

## 7. Validate the native lifecycle within the synthetic envelope

Reuse inspected clock/assertion/resource helpers through a narrowly scoped adapter; avoid modifying historical controllers or creating a generic scheduler. The executable test path must generate deterministic synthetic arrays in its own fixture workspace and refuse operational input paths, model artifacts, source roots and network access.

Use these fixed limits for each native integration invocation:

| Scope | Maximum |
| --- | ---: |
| Prerequisites |30s |
| One numerical synthetic worker, dispatch through normal exit/reaping |60s |
| Parent finalization |15s |
| Whole invocation, including prerequisites/finalization |120s |
| Cleanup inside the worker ceiling |2s |
| Worker RSS |1GiB |
| Whole native reservation |512MiB |
| Controller RSS |128MiB |
| Guard journal |64MiB |
| Worker text log |1MiB |
| Total owned storage |128MiB |
| Optimizer steps per arm/seed in that integration |2 |

At most12synthetic optimizer steps per native invocation. Exercise all six arms, actual initialization/permutation pairing, own-state restore, score/calibration and aggregate uncertainty with fixed tiny fixtures. Keep these limits distinct from ordinary synthetic unit-test cases and all future real training budgets. Do not present this toy execution as scientific model training or a performance benchmark.

Enforce continuous deadlines across suspension, cleanup inside caps, explicit1GiB RSS, WARN advisory/CRITICAL veto, invalid-primary-accounting veto and disclosed unavailable pressure. Global available RAM is context only. Verify the owned temporary idle-system-sleep assertion before dispatch and during the worker; permit display sleep and verify release/reaping on success and failure. No persistent power changes, app closure, polling or monitor optimization.

Accept only normal exit/reaping plus source/output identities, complete counters and resource/deadline checks. Body-complete followed by stalled/failed exit must remain rejected. Test assertion failure/loss/release, suspension, timeout, guard failure, partial/inflight updates, journal/storage overflow, output tampering and publication failure with synthetic injection/simulated clocks.

Synthetic software repair and revalidation are permitted in this task. Preserve all failed native receipts, bind each invocation to its source version, and report actual attempts/steps; do not overwrite a failed receipt or treat it as an operational scientific allowance. Complete a final bounded native integration on the final source when the platform supports it. If unavailable or rejected, disclose the blocker and leave native acceptance unverified rather than weakening caps or claiming success.

## 8. Fresh software acceptance and deliverables

Run targeted meaningful tests, lint/format/dependency checks, and the full/portable synthetic suites in artifact-free isolated source copies using the existing validated approach. Fixtures must not discover repository operational artifacts. No dependency install/update is needed. Inspect every reused helper for hard-coded Task0033 paths, input allowlists, ceilings and acceptance assumptions.

Bind a fresh final source/config/test map, exact environment/dependency identities, unchanged Task0034 design and actual synthetic validation evidence. Distinguish software acceptance from model freeze, source acceptance, human authorization and real execution readiness. Historical1728tests do not cover new research code; report actual new totals and scope. No hosted CI or physical suspension test is implied.

Produce:

- `docs/controlled-activation-synthetic-foundation.md`
- Task0035 prompt/handoff and synthetic implementation config.
- Separate research helpers and focused synthetic tests/validation entrypoint.
- `results/tables/final/task0035-controlled-activation-synthetic-summary.json`.

Keep detailed receipts, acceptance maps, synthetic tensors/checkpoints, logs and journals ignored. The summary should curate pairing/restoration/statistical/guard results and limitations, without toy scientific rankings or operational per-event arrays. Update README, index and memory from revision1.29.

The Italian final handoff should explain what is now implemented, which properties were verified, the actual native status/durations/resources/assertion release, and what remains unverified. Separate actual synthetic work from zero operational work:

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
new_operational_population_requests_in_Task0035: 0
new_operational_feature_rows_read_in_Task0035: 0
new_operational_stored_score_array_loads_in_Task0035: 0
new_operational_membership_or_fingerprint_loads_in_Task0035: 0
operational_model_forward_calls_in_Task0035: 0
operational_reconstruction_computations_in_Task0035: 0
operational_calibrations_or_scientific_evaluations_in_Task0035: 0
operational_optimizer_updates_in_Task0035: 0
event_payload_downloads_in_Task0035: 0
native_synthetic_invocations: ACTUAL_COUNT
native_synthetic_optimizer_steps_started_completed_inflight: ACTUAL_COUNTS
native_synthetic_final_status: ACTUAL_STATUS
```

Also disclose actual new research-test synthetic forwards/reconstructions/updates where instrumented and the scope of those counters. Do not claim globally zero model instantiation or optimizer work: synthetic work is authorized. YES above preserves historical exposure.

End with a concrete next-task brief that separates possible background-development implementation/execution from the still-conditional acquisition/confirmation route. Retain unresolved full-event coverage, generation independence, counts, overlap and sample-precision requirements. Software readiness does not unblock confirmation; training need not be presented as useful confirmatory progress if a suitable source cannot meet the design. Do not initiate either campaign or another task.

Finish with actual Git review, selective staging, staged review, Conventional Commit and push commands for the verified branch/upstream. Do not stage, commit or push. Preserve all historical scientific/configuration/artifact bytes and unrelated work.

Proceed with **Task0035 only**.
