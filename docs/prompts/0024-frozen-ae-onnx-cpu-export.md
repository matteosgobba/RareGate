# LatentTrigger — Task 0024: Frozen AE ONNX CPU Export and Equivalence Foundation

You are continuing **LatentTrigger**. Perform **Task0024 only**.

Task0022 supplies the complete accepted CPU benchmark. Task0023 supplies a software-validated CPU/MPS foundation, but its single device check was unavailable and failed admission. No physical MPS equivalence or paired performance evidence exists.

Advance independently to CPU ONNX export and equivalence for the frozen compact-autoencoder-v2.

This prompt authorizes:

1. Minimal missing export/runtime dependency additions under the preservation conditions below.
2. Implementation and self-contained synthetic validation.
3. One conditional bounded frozen-model export/equivalence attempt, including one read of the existing1024 prepared real inputs after successful synthetic verification.

No performance campaign, fitting, optimizer updates, recalibration, MPS check/replay, CoreML, quantization, particle execution or test evaluation is authorized.

## 1. Inspect actual state and preserve history

Read applicable instructions, `docs/development.md`, `docs/project-memory.md`, Task0022’s accepted CPU report/policy/protocol/summary, and Task0023’s report/handoff/protocol/summary and Task0024 brief.

Planning inspection found clean `main` tracking `origin/main`:

```text
Task0023 commit: 933cba2
Task0022 commit: 6161134
```

Verify full commit identities, status/index, upstream and live numbering. Reconcile these later commits in current memory/index while preserving historical task-time reports and handoffs.

Preserve canonical model/config/calibration artifacts, preprocessing/scalers/splits, all Task0020–0023 source/protocol/acceptance/receipt/result bytes and consumed execution paths. Task0023’s old proof cannot become current admission through its software repair.

Particle192/192 and canonical local deferral remain unchanged. Synced `sources/` remain read-only. Preserve unrelated work.

Save:

```text
docs/prompts/0024-frozen-ae-onnx-cpu-export.md
docs/handoffs/0024-frozen-ae-onnx-cpu-export.md
```

Implement isolated export/runtime/policy/controller/worker helpers. Do not change existing canonical loaders, forward/score arithmetic or benchmark launch routes.

## 2. Establish the optional dependency environment

Planning inspection found:

```text
Python3.12.12 / macOS arm64
torch2.14.1
numpy2.5.3
scikit-learn1.9.1
threadpoolctl3.7.0
onnx: not installed
onnxruntime: not installed
onnxscript: not installed
```

Recheck metadata without opening real numerical inputs.

The prompt authorizes adding the missing ONNX/export/runtime libraries and necessary missing transitive dependencies to the project virtual environment. Do not stop merely because their expected absence is confirmed.

Before installation:

- Record all installed distribution versions and relevant core package/build identities.
- Verify official package metadata and compatible macOS-arm64/Python3.12 wheels.
- Select one stable compatible exact version set and save its resolver/dry-run evidence.
- Constrain already installed distributions to their existing versions.
- Confirm the proposed installation adds packages without upgrading, replacing or downgrading any existing distribution.

Preserve Torch, NumPy, SciPy, sklearn, threadpoolctl and their recorded builds. Do not use blanket upgrades, force-reinstall, source builds or global installation. If a compatible additive resolution is unavailable, record the exact dependency conflict rather than modify the baseline.

Bound dependency resolution/download/installation to≤300s, separate from the export/equivalence execution budget. Record actual added versions and verify prior versions/core identities remain unchanged afterwards; run dependency consistency checks.

Add a clearly optional export extra and a small reproducible pinned dependency record where appropriate. Keep core dependency requirements unchanged and optional imports lazy. Record exact wheel/package identities separately from model/source hashes.

If installation or access is blocked, finish unaffected software work and report the concrete blocker. Do not substitute mock export/runtime results for physical validation.

Use primary sources:

- [PyTorch ONNX exporter](https://docs.pytorch.org/docs/2.14/onnx.html)
- [ONNX](https://onnx.ai/onnx/)
- [ONNX Runtime Python API](https://onnxruntime.ai/docs/api/python/api_summary.html)
- Official package metadata on PyPI.

## 3. Bind frozen scientific identity and export scope

Use:

```text
configs/models/compact_autoencoder_v2.json
artifacts/models/compact-autoencoder-v2/model.json
results/tables/final/task0008-autoencoder-convergence-summary.json
```

Verify existing file-byte, canonical/scientific JSON and full-training provenance identities. Load through the existing canonical loader.

Preserve all155 FP32 parameters, architecture8→6→3→6→8, hidden ReLUs, linear latent/output, feature order/scalers and four calibrated thresholds. Keep AE v1/PCA as history/reference.

Export **only reconstruction**:

```text
input: already-standardized FP32 event_features[B,8]
output: FP32 reconstruction[B,8]
```

Canonical scoring stays outside ONNX on CPU: cast input and reconstruction to FP64 before subtraction, square/sum eight residuals, then all four strict `score > threshold` comparisons.

No score-head redesign, embedded scaler, threshold export, quantization, clipping, parameter approximation or scientific retraining.

The runtime adapter must reject wrong feature order, dtype/rank/width, empty/nonfinite inputs and unsupported batch sizes. ONNX symbolic dimensions alone are not an input-validation policy.

## 4. Preregister one export/runtime contract

Create a strict protocol, for example:

```text
configs/exports/frozen_ae_onnx_cpu_v1.json
```

Bind this actual prompt, frozen science/input identities, exact dependency/runtime/exporter settings, operator/shape policy, numerical assumptions, source acceptance, finite limits and fixed output path.

Use the installed modern `dynamo=True` exporter route, verified against current APIs/source. Pin one supported opset before execution; use opset18 if the selected exporter/runtime supports the required graph. Do not search opsets until a real artifact passes.

Use an explicitly synthetic FP32 example with a nontrivial batch and dynamic batch dimension; width8 stays fixed. Require actual equivalence coverage for batches `[1,8,32,128,1024]`.

Request a self-contained file with weights included and no external-data files. Disable optional exporter optimization for this baseline where supported and record the capture strategy.

Do not pass removed API options: installed PyTorch2.14 has no `fallback` argument. Do not manually retry through a legacy exporter after a reserved attempt fails.

Distinguish optional optimization settings from transformations the exporter always performs. In particular, do not claim constant folding is disabled merely because `optimize=False`.

The actual exported graph, rather than requested flags alone, is the acceptance object.

## 5. Audit the graph and provider

After export, run ONNX checker and appropriate shape/type validation.

Audit:

- Opset/IR version, input/output names, FP32 element types and dynamic batch/fixed width.
- Standard operator domains, node histogram and actual topology.
- Four affine stages and two ReLU semantics, including permitted Gemm or MatMul/Add/Transpose representations.
- Every initializer’s shape/dtype/value mapping to the original parameters.
- All155 learned scalar values, exactly preserved in FP32 bytes after any layout transpose.
- No unexpected learned constants, reduced-precision tensors, custom operators, embedded preprocessing or score changes.
- No external weights or unresolved operator/provider dependencies.

Do not silently accept an unaudited fused/reparameterized graph or modify the graph to make it fit after reservation. Metadata/layout changes may be legitimate, but require explicit mapping proof.

Use ONNX Runtime with:

```text
providers = ["CPUExecutionProvider"]
execution mode = sequential
intra-op threads = 1
inter-op threads = 1
graph optimization = disabled
```

Verify effective session options and actual providers; disable provider fallback where the installed API supports it. No CoreML/CUDA/MPS provider or optimization sweep.

Record available versus selected providers distinctly. Session-creation success alone is not numerical equivalence.

Freeze the exported file hash and graph/parameter manifest before opening real inputs. The export is a derived runtime artifact linked to the canonical model, not a replacement canonical scientific model.

## 6. Independent numerical equivalence policy

Derive and validate a separate ONNX CPU numerical contract before real numerical access. Do not assume that CPU execution or FP32 output implies PyTorch arithmetic identity.

You may reuse proven outward primitives and the CPUv2 recurrence only after justifying their application to the audited ONNX affine/ReLU topology and CPU provider assumptions.

Preserve operation-level outward evaluation, FP64 diagnostic-reference rounding, local affine checks, supported input/activation bands and propagated reconstruction/SSE bounds. No decimal epsilon fitted to observed error or tolerance search.

For runtime-local checks, an ignored diagnostic copy may expose intermediate graph outputs. Preserve the primary exported artifact unchanged. Establish that the diagnostic copy’s final output matches the primary session before treating its intermediate tensors as evidence of primary execution.

Check local affine outputs against FP64 evaluation on those same stored FP32 inputs; verify ReLU semantics. Unknown native-kernel details remain unknown, rather than becoming a universal backend guarantee.

Retain independent gates:

- Finite inputs, parameters, outputs, scores and bounds.
- Exact source/initializer/input/threshold identities.
- Same-runtime same-shape repeatability.
- Same-runtime separated/adapter canonical FP64 SSE `atol=rtol=1e-12`.
- Cross-runtime reconstruction and SSE within justified arithmetic envelopes.
- Zero strict decision mismatches at all four thresholds against the canonical PyTorch1024 reference.
- Restored parameter/input/reference/export hashes after verification.

Do not demand cross-runtime byte equality; record it where obtained. Do not use the1e-12 same-runtime score gate as an across-runtime reconstruction tolerance.

FP64 diagnostic copies and graph traces are verification tools, not new scientific models or exact real-arithmetic truth.

## 7. Validate software before the one frozen-model attempt

Add meaningful self-contained tests for:

- Optional dependency absence and lazy imports.
- Export API/opset/shape settings and graph/operator rejection.
- Initializer transposes, wrong weights, dtype/count/order and external-data refusal.
- Dynamic batch handling, especially B1 and wrong width/dtype/nonfinite inputs.
- Exact/rational checks of bounds, cancellation, local affine/FP64 rounding and SSE propagation.
- Same-runtime repeats, strict ties/near-threshold mismatches and source mutations.
- CPU-only provider/session/thread requirements.
- Input refusal before numerical opening.
- Atomic reservation, partial/foreign states and truthful incomplete evidence.
- Blocked imports/export/runtime calls, deadlines, peaks and cleanup.
- Raw text/file hashes versus canonical JSON-string/document hashes.

Ordinary tests must use synthetic models/data and temporary artifacts, without operational inputs, frozen artifacts, receipts or `.git`.

Include actual ONNX export/runtime integration tests on synthetic fixtures when optional dependencies are installed. Clearly report skipped optional checks in environments where they are absent; simulation is not export proof.

Run appropriate full and portable suites, lint/format, dependency consistency and guarded CPU smoke without querying MPS.1033 is historical acceptance; report current results.

Preserve narrowly scoped portable fixtures. Do not generalize identity bypasses or weaken real admission checks for portability.

Freeze executable code/protocol/numerical policy and complete current source acceptance before the scoped frozen-model attempt.

## 8. One bounded export/synthetic/real equivalence attempt

Use one exclusive ignored root:

```text
results/benchmarks/task0024-ae-onnx-cpu/
```

Keep the export, manifests, diagnostics, acceptance, audits and receipts there. No alternate output/reset/overwrite/retry selector.

After successful dependency/software/prerequisite checks, atomically reserve before exporting the frozen artifact. A failure after reservation consumes this attempt even before real numerical access. Preserve partial artifacts and stop dependents; no exporter/policy repair followed by replay.

Run one fresh numerical worker with:

| Scope | Fixed limit |
| --- | --- |
| Worker lifetimeRSS |≤1GiB |
| Whole-native reservation |≤512MiB |
| Stdlib parentRSS |≤128MiB |
| Export and structural/provider checks |≤30s |
| Fixed synthetic equivalence |≤60s |
| Conditional real equivalence |≤60s |
| Whole attempt |≤180s, including imports/orchestration/cleanup |
| Cleanup/reaping |Bounded2s inside budgets |

Stage sums leave30s for shared imports/orchestration/cleanup; record actual boundaries rather than overlapping sums presented as exclusive cost.

Use existing verified host accounting, fresh phase/operation checks and50ms watcher intent. Parent deadlines cover blocked exporter/runtime/native work.

WARN advisory, unknown pressure disclosed, CRITICAL/malformed primary accounting latched. Global context is optional, with no memory floor/readiness loop.

Do not enlarge caps or change runtime settings to complete the attempt.

### Synthetic equivalence first

Use the four fixed Task0021 families and batch grid. Verify every corresponding row/window, including reconstruction, local checks, public/adapter SSE, own repeatability and all four frozen decisions.

No seed/domain/operator/threshold search. Record family hashes and coverage.

Only after graph/provider/numerical synthetic acceptance may the worker open the existing real array.

### Conditional real equivalence

The only numerical real input is:

```text
results/benchmarks/task0020-frozen-cpu/prepare/input.npy
```

Verify original provenance,32896-byte bounded NPY header and exact file/payload hashes before one `np.load(...,allow_pickle=False)`.

Reuse exactly1024 original dev-training rows. No raw/processed store, custody replay, population request, rescaling or row reselection.

Obtain canonical PyTorch references and verify all windows of all five batches:1193 windows,1024 unique rows. Aggregate complete supported comparisons while preserving failed status; critical integrity/resource/nonfinite failures stop.

A successful equivalence claim requires every numerical/local/repeatability/strict-decision gate. Do not stop at one passing batch or treat a successfully written file as an accepted export.

Recheck references, parameters, thresholds, input and primary artifact afterwards. Persist bounded aggregates/examples, not per-event score arrays or new scientific model artifacts.

No performance timer pairs, latency distributions, throughput campaign or speedup claims belong here. Wall measurements serve resource accounting.

## 9. Deliverables, identities and next step

Create:

```text
docs/frozen-ae-onnx-cpu-export.md
results/tables/final/task0024-ae-onnx-cpu-export-summary.json
```

Add the small protocol/derivation, isolated implementation/tests, optional dependency declaration and reproducible dependency record as actually needed.

Keep ONNX binaries, diagnostic copies, arrays, package caches, resolver/raw validation receipts, logs and source acceptance ignored. Do not add a Git exception for exports.

Use explicit hash-kind fields. Distinguish canonical model scientific identity, complete source-file hashes, exported ONNX bytes, graph manifest and raw-versus-JSON build-text hashes. Never compare different hash definitions under one generic label.

Report:

- Dependency additions and preservation of the original stack.
- Exporter/capture/opset/IR and actual operator/initializer/provider audit.
- Export size/hash and155-parameter mapping.
- Synthetic and real coverage, errors/envelope ratios and decision mismatches by batch.
- Own repeatability, identity checks, peak resources and stage/total wall.
- One real prepared-array read and1024 reused rows only if accessed.
- New population/store-custody/optimizer requests0.
- Performance timing invocations0.

Update README, living memory and index in place, reconciling the actual Task0022/0023 commits. Preserve CPUv2 acceptance, unavailable MPS evidence and particle deferral.

Verify JSON/report agreement, counts, dependency/source/graph/science identities, receipt lineage, links, exclusions and whitespace. Hosted CI remains unverified unless established.

State:

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

If accepted, propose one bounded Task0025 paired PyTorch/ONNX Runtime CPU inference benchmark using the accepted artifact/policy and new independent measurements. Equivalence alone establishes no performance benefit.

If blocked/failed, distinguish dependency, export, graph/provider and numerical causes, retained artifacts and missing evidence. Do not propose a performance campaign as if equivalence passed.

Do not implement the next task here.

## 10. Informative Italian final response

Follow `docs/development.md`’s standing preference.

Provide a self-contained Italian response, approximately600–1000 words excluding Git, scaled to the result. Explain:

- What ONNX export changes operationally and what remains scientifically frozen.
- Actual dependencies installed, exact versions and baseline preservation.
- Graph structure/opset/IR/provider and parameter mapping.
- A table of coverage, reconstruction/SSE errors, bound utilization and threshold mismatches by batch.
- Synthetic versus reused real-input evidence.
- Resource/time/access counts, current tests/checks and gaps.
- What export/equivalence supports and what remains unmeasured.
- One concrete recommended next task.
- Report/summary/handoff links and test-exposure declarations.

Do not replace substance with “see report”. Distinguish implemented, generated, structurally validated, numerically accepted, inferred and unverified states. Do not fabricate metrics for blocked phases.

## 11. Required final Git section — last section of the response

Do not automatically stage, commit or push.

End with exact status/diff/index review, selective `git add --` for actual intended files, staged stat/diff, `git diff --cached --check`, an outcome-accurate Conventional Commit and push for the verified branch/upstream.

Include this prompt/handoff, report/summary, protocol/policy/helpers/tests, intentional optional dependency files and affected README/memory/index. Exclude model binaries, inputs, receipts, acceptances, logs, caches, snapshots and unrelated work.

Preserve historical CRLF result files unchanged. Any new text/CSV should use intentional repository-compatible line endings; do not alter persistent Git whitespace settings.

Proceed with **Task0024 only**.