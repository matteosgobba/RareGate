# LatentTrigger — Task 0026: Guarded Frozen PCA/AE Scientific Evaluation and Unblinding Readiness

You are continuing **LatentTrigger**. Perform **Task0026 only**.

Advance toward the first final scientific comparison of the two existing frozen native CPU candidates:

- PCA-v1, with six retained components.
- Compact-autoencoder-v2, architecture `8 → 6 → 3 → 6 → 8`, with 155 FP32 parameters.

The scientific contract already exists. The missing prerequisite is finite, audited full-store execution with independent process supervision.

**Complete the implementation and readiness work before asking for final test authorization.**

This prompt authorizes Phase A:

1. Inspection and metadata verification.
2. Implementation of guarded evaluation orchestration.
3. Self-contained synthetic validation.
4. Current-source acceptance.
5. One bounded real full-store custody-only readiness check after validation passes.
6. Preparation of a concrete, reviewable final-evaluation plan and command.

**This prompt does not authorize real test unblinding.**

At the end of successful Phase A, ask for explicit authorization covering the frozen candidate list and the exact planned test access. Phase B may execute only after the human provides that authorization.

No refitting, scientific optimizer updates, recalibration, new candidate selection, export, quantization, MPS check, ONNX benchmark replay or particle execution.

## 1. Inspect current state and preserve history

Read applicable instructions, `docs/development.md`, `docs/project-memory.md`, `docs/evaluation-protocol.md`, the frozen PCA/AE reports and the relevant Task0022–0025 records.

Planning inspection found clean `main` tracking `origin/main`:

```text
Task0025 commit:
2f3cde01c9a2c91780d22df791c897891338fdc5

Task0024 commit:
cacaefd3ac00a6c657b14109eb19e0119e25ada4
```

Verify live branch, full HEAD, upstream, index, unrelated changes and task numbering.

Save:

```text
docs/prompts/0026-guarded-pca-ae-evaluation.md
docs/handoffs/0026-guarded-pca-ae-evaluation.md
```

Preserve prior executable/protocol/acceptance/evidence bytes and frozen science.

Task0025 remains failed and consumed despite complete numerical/timing coverage. Preserve ORT3’s completed local receipt, failed parent lifecycle record, provisional statistics and unknown shutdown cause. Do not repair, replay or reinterpret it as an accepted speedup.

Task0022’s accepted CPU reference and Task0024’s accepted ONNX export/equivalence remain valid.

Particle updates remain 192/192 consumed; canonical local execution remains deferred.

Synced `sources/` remain read-only.

## 2. Freeze the two native scientific candidates

Use the existing artifacts and canonical loaders:

```text
PCA:
configs/models/pca_baseline.json
data/baselines/pca-v1/model.json
results/tables/final/task0006-pca-background-results.json

AE:
configs/models/compact_autoencoder_v2.json
artifacts/models/compact-autoencoder-v2/model.json
results/tables/final/task0008-autoencoder-convergence-summary.json
```

Verify their actual file-byte, canonical scientific, configuration and calibration identities against existing provenance.

Expected model scientific identities:

```text
PCA:
d09f96bb7b1536e8da147458f3b0bf50a120bdf6cfc4c247b37970f4f51bf42f

AE v2:
6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b

Full processed store:
d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2
```

Verify preprocessing/scalers, split identity, eight feature names/order, full-training provenance, selected states, score orientation and all frozen calibrated thresholds.

PCA retains its original FP64 reconstruction arithmetic. AE retains native CPU FP32 reconstruction and canonical FP64 scoring.

Both scores remain eight-channel reconstruction SSE, higher anomalous, with strict `score > threshold`.

Do not insert ONNX as a third candidate or replace the AE’s native path. Task0024/0025 numerical evidence on selected inputs does not establish universal held-out runtime equivalence.

No test-dependent model choice, threshold revision, score flipping or architecture change.

## 3. Reuse the existing scientific contract

Reuse the validated metric and threshold functions. Preserve:

- ROC-AUC with the supplied score orientation.
- Average Precision as recall-increment-weighted precision.
- Background/signal counts and sample prevalence.
- Frozen-calibration operating points at target FPRs `0.1, 0.05, 0.01, 0.001`.
- Attainable empirical TPR at those fixed FPR targets.
- Attainable FPR at fixed TPR targets `0.5, 0.8, 0.9`.
- Accepted counts, totals, achieved rates and empirical resolution.
- Existing 95% Wilson rate intervals.
- Existing one-sided exact upper bound for zero observed background acceptance.
- Null rejection when zero background events are accepted.
- Strict-threshold tie handling and explicit accept-none/accept-all cases.

Do not introduce interpolated unattainable operating points, tail extrapolation, unregistered significance tests or additional metric searches.

Distinguish calibration-frozen thresholds from descriptive thresholds derived from the final empirical ROC.

Keep the existing evaluation batch size **4096**, source ordering and complete tail batches. Do not substitute the benchmark’s smaller batches.

The two candidates have different latent dimensions, six versus three. Their comparison is not a capacity-controlled experiment isolating linearity from nonlinearity.

## 4. Implement isolated guarded orchestration

Inspect `evaluation.run.run_final`, `ProcessedStore`, model validation and metadata helpers.

Implement a new isolated controller/worker route that reuses scientific behavior while adding:

- A stdlib-only controller.
- Fresh sequential native CPU workers.
- Independent import/operation/exit deadlines.
- Explicit full-store resource policy.
- Current source/dependency/artifact acceptance.
- Exclusive fixed campaign outputs.
- Durable pre-read exposure records and batch progress.
- Partial-failure handling.
- Parent-confirmed process termination and reaping.

Preserve old source behavior and execution routes.

If existing `run_final` cannot provide durable batch progress and phase guards without modification, implement the new orchestration around its unchanged loaders, validation and metric primitives. Demonstrate equivalence on synthetic fixtures.

Do not bypass reader validation, introduce an unverified fast reader or skip full constructor integrity checks based on cached metadata.

Model loading, store construction, scoring, metric computation, serialization and cleanup all belong to bounded execution.

## 5. Preregister the full-store policy

Create a strict versioned protocol, for example:

```text
configs/evaluation/frozen_pca_ae_final_v1.json
```

Bind the actual prompt, candidate order, all frozen identities, source/dependency acceptance, scientific reporting plan, resource limits, deadlines, output paths and authorization state.

Use a fixed namespace with separate readiness and final areas:

```text
results/evaluation/task0026-frozen-pca-ae/
```

Keep readiness evidence distinct from the final unblinding attempt. Phase A must not reserve or consume the final-evaluation slot.

For this short native evaluation, preregister:

```text
numeric-worker lifetime RSS ceiling: 6 GiB
native reservation ceiling: 512 MiB
stdlib controller RSS ceiling: 128 MiB

custody-only readiness check: ≤ 60 s
each final candidate worker: ≤ 120 s
final consolidation: ≤ 30 s
whole final campaign: ≤ 600 s
termination/kill/reap grace: ≤ 2 s, within the relevant deadline
```

Explain the policy’s scope. Historical full-store custody observed approximately 3.121 GiB lifetime RSS and 197.25 MiB native reservation; it did not validate future scoring or sustained training.

These are prospective evaluation limits, not an extension of particle training authorization or proof that the host has spare RAM.

Keep global available memory contextual, without an idle-host requirement or readiness loop. WARN is advisory, CRITICAL blocks, unknown pressure is explicitly disclosed. Invalid primary resource accounting blocks execution.

Reuse existing validated observation primitives where appropriate, but do not alter old benchmark guards to replace their historical caps.

Record units, measurement methods, sampling intent, observed coverage and limitations. RSS/native measurements overlap and must not be added.

## 6. Supervise the entire process lifecycle

Task0025 demonstrates that a completed body receipt is insufficient.

Require independent parent confirmation of:

- Completion within the deadline.
- Normal zero exit status.
- Process reaping.
- No latched guard failure.
- Valid complete output and source/artifact identities.

A worker may record `body_complete_awaiting_exit`; only the parent may accept the stage after termination is observed.

Keep parent deadline supervision active through actual process exit. Record resource-monitor closure and any interval whose memory accounting is unavailable.

Do not claim continuous or full-lifetime resource coverage from samples that ended before process termination.

Do not use a forced `os._exit`, a success receipt or termination signal to manufacture successful lifecycle acceptance.

No success promotion after a timeout, no automatic retry, no alternate output namespace and no enlarged limit after seeing a failure.

## 7. Complete Phase A without test exposure

Before any real custody check:

- Finish the implementation.
- Pass self-contained tests and guarded synthetic integration.
- Freeze source/protocol/dependency acceptance.

Then perform one explicitly bounded custody-only check of the existing full processed store using the unchanged verification path.

This check may hash files and validate stored schema, membership, labels and preprocessing as permitted integrity operations. It must not request a model population, score real events, print physics distributions or inspect test performance.

Report custody operations separately from population access.

Require normal worker exit, parent reaping, identity agreement and policy acceptance. Preserve failed evidence without retry.

If prerequisites fail, finish unaffected work and document the blocker. Do not request approval for an execution that is not ready.

If readiness passes, prepare a reviewable package containing:

- Candidate/config/calibration/store identities.
- Scientific metrics and reporting plan.
- Fixed execution order: PCA, then AE.
- Exact access counts and batch/tail schedule.
- Resource/deadline policy.
- Current-source acceptance.
- Exact guarded CLI command.
- Expected output files and failure/exposure behavior.

Do not run the real test CLI during Phase A.

## 8. Make authorization the final prerequisite

The standing evaluation protocol reserves test populations for an explicitly authorized final evaluation. An available API, CLI flag, readiness result or this preparation prompt is not authorization.

After successful Phase A, ask the human a single concise question explicitly covering:

- Both named frozen native candidates.
- 150,471 test-background events.
- 100,000 test-signal events.
- One pass per candidate under the frozen protocol.
- No retraining, recalibration or candidate selection afterward.

Explain that this consent is required because the first access exposes the held-out test, including an interrupted attempt.

Do not infer consent from elapsed time, generic approval of implementation, tool configuration or a locally created authorization file.

Once explicit consent is received, record it against the approved plan/source identities and proceed without asking again for the same authorized campaign.

Recheck identities before execution. If the approved scientific plan or executable changes, finish a new reviewable acceptance before relying on approval of the earlier plan.

## 9. Define Phase B’s exact access and exposure accounting

Only after explicit authorization, reserve one exclusive final campaign.

Each candidate evaluates:

```text
test_background:
150471 events
36 full batches of 4096 + final batch of 3015
37 score batches

test_signal:
100000 events
24 full batches of 4096 + final batch of 1696
25 score batches
```

Complete totals:

```text
2 candidates
4 model/population requests
124 score batches
500942 scored event presentations
250471 unique held-out events, reused across both candidates
```

No train/selection/calibration population reread is needed. Frozen calibration artifacts supply thresholds.

Persist `test-unblinding.json` before each population request, including:

- UTC and explicit authorization binding.
- Actual commit/base/dirty source identities.
- Candidate/config/calibration/store/split identities.
- Planned metrics and access flags.
- Requested population and expected count.
- Durable completed-read/scored progress.
- Potential in-flight read/score state.
- Final status and output hashes.

Persist progress per batch so abrupt termination cannot leave a misleading zero-access record. Distinguish confirmed completed access from uncertain in-flight access.

Parent failure handling must preserve the last durable journal and record interruption. A failed or partial unblinding remains exposure.

Do not begin a second candidate after a first-stage failure. Do not automatically rerun or resume interrupted test evaluation.

Stop using the term “untouched test” after any real exposure. Update handoff and living memory accordingly.

## 10. Validate with meaningful synthetic fixtures

Tests must remain independent of operational data and artifacts.

Cover:

- Embargo rejection before real test population access.
- Explicit authorization and identity binding.
- Unknown selectors and unsafe/alternate output paths.
- Atomic reservation and consumed/partial states.
- Frozen model/calibration/store mismatches.
- Native CPU configuration and source acceptance.
- Batch size 4096, complete tails and exact counts.
- Feature order, label separation and finite scores.
- Strict ties, zero acceptance and empirical ROC conventions.
- Equivalence with existing `run_final` on both model families.
- Durable pre-read and per-batch audit ordering.
- Interrupted reads/scoring and unknown in-flight state.
- Failed guard/deadline propagation.
- A worker that writes a successful body receipt and then hangs.
- Nonzero exit, forced termination, cleanup and reaping.
- Consolidation refusing incomplete candidate pairs.

Exercise actual NumPy/sklearn/PyTorch native paths on synthetic fixtures. No ONNX session is needed.

Run the appropriate full suite, Ruff, dependency consistency, guarded synthetic smoke, portable checkout checks, links, JSON and whitespace checks.

Report actual counts. Historical 1179 is Task0025’s result, not automatic Task0026 acceptance.

Do not change installed packages. Hosted CI remains unverified unless an actual hosted run is inspected.

## 11. Prepare scientific reporting before unblinding

Implement and validate the reporting pipeline using synthetic fixtures.

After an authorized complete evaluation, report:

- ROC-AUC and AP for both candidates.
- Class counts and released-sample prevalence.
- Calibrated background FPR and signal efficiency at all four frozen thresholds.
- Counts, intervals and achieved rather than merely targeted rates.
- Descriptive fixed-FPR and fixed-TPR results.
- Background score summaries.
- Model capacity and accepted CPU-cost context.
- Resource/lifecycle acceptance and actual exposure.

Prepare standard static ROC/precision-recall figures if useful. Label prevalence and distinguish calibrated operating points from empirical ROC points.

Keep score arrays, curve arrays, unblinding manifests, logs, acceptance and execution receipts ignored. Only intentionally curated small tables/figures enter Git under the existing results policy.

Do not use Task0025’s provisional speedups as accepted deployment measurements. Use Task0022’s accepted CPU reference with its stated scope.

A negative or modest discrimination result is valid. Do not tune models against the newly exposed test.

## 12. Update documentation and deliver detailed Italian output

Create or update:

```text
docs/guarded-pca-ae-evaluation.md
docs/handoffs/0026-guarded-pca-ae-evaluation.md
results/tables/final/task0026-guarded-pca-ae-evaluation-summary.json
```

Before unblinding, these must describe readiness and authorization pending, without fabricated test metrics.

After an authorized complete Phase B, add curated comparison tables and actual scientific results.

Update README, living memory and index consistently. Reconcile Task0025’s verified commit while preserving its historical handoff. Increment the living-memory revision from the verified current state.

Final response in Italian, approximately 600–1000 words excluding Git:

- What was implemented.
- Which science and artifacts remained frozen.
- Validation and custody-only evidence.
- Full-store limits and lifecycle protections.
- Readiness, authorization and exposure status.
- Actual scientific findings if Phase B was authorized and completed.
- Limitations and concrete next step.

At the end of Phase A, include the concrete authorization question only after presenting the completed readiness package.

Report test-access flags truthfully. During Phase A:

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

After Phase B starts, report actual exposure, including failures and uncertainty. Never retain `NO` after a test request/read.

Scientific optimizer updates remain zero. Particle remains 192/192 consumed.

Finish with actual manual Git commands: status, tracked/untracked review, unstaged/staged diff review, explicit selective staging, staged whitespace checks, outcome-appropriate Conventional Commit and push to the verified upstream.

Do not stage, commit or push automatically. Exclude operational arrays, scores, logs, manifests, acceptance snapshots and raw receipts.
