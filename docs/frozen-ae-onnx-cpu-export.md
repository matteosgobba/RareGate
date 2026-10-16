# Task0024 — Frozen AE ONNX CPU export and equivalence

**Complete and accepted:** one frozen-model export/equivalence attempt produced a
self-contained11464-byte reconstruction graph, audited all155 FP32 parameters,
passed four fixed synthetic families, then read the existing1024prepared rows
once and passed all1193windows/five batches. All four strict frozen decisions
agree. No performance campaign or scientific training/calibration/test occurred.

[Actual prompt](prompts/0024-frozen-ae-onnx-cpu-export.md),
[handoff](handoffs/0024-frozen-ae-onnx-cpu-export.md),
[strict protocol](../configs/exports/frozen_ae_onnx_cpu_v1.json),
[numerical derivation](arithmetic-onnx-cpu-v1-policy.md),
[dependency record](../configs/dependencies/onnx_cpu_v1.json) and
[curated summary](../results/tables/final/task0024-ae-onnx-cpu-export-summary.json).
The ONNX binary/diagnostic/receipts/acceptance remain ignored. There is no timing CSV.

## Actual repository and preserved prerequisites

Initial `main` tracking `origin/main` was clean with an empty index. Verified full
commits: Task0022 `61611341a90f2bd2225559b8a3245ec3e6ed08a7`; Task0023
`933cba22a2243ecd81d573bef4af8688678b9d33`, also this task's base HEAD.
Current memory/index reconcile those later commits. Original task-time reports
and handoffs are preserved, including their staged/uncommitted historical state.

The accepted [CPUv2 reference](frozen-cpu-benchmark-v2.md) remains complete90cells /
18000timings. [Task0023](frozen-cpu-mps-benchmark.md) remains an unavailable single
MPS check with original admission failure/software-only repair; its proof was
neither repeated nor reused as current admission. All104old source files,101old
operational evidence files and3old acceptances retain their byte hashes.
Scientific model/config/calibration/scaler/split identities, particle192/192 and
unchanged local canonical deferral remain intact. Synced sources are read-only.
No staging/commit/push or unrelated changes.

## Additive optional dependencies

Before installation, all36installed distribution versions and core package file /
accepted build identities were recorded; all existing distributions were pinned
in resolver constraints. Official PyPI metadata/wheel tags and SHA256 values were
verified. The successful dry-run proposed **additions only**, followed by binary
wheel installation inside the project `.venv`, with no core replacement, upgrade,
downgrade, source build or global installation. Resolution/download/install/check
completed in164.87414625000383s≤300s, separate from the execution budget.
The initial sandbox DNS refusal was resolved through the tool's authorized network
execution; no baseline relaxation or MPS privilege workaround occurred.

| Added distribution | Exact version | Wheel compatibility |
| --- | --- | --- |
| ONNX | 1.23.2 | CPython312 ABI3/macOS13 universal2 |
| ONNX Runtime | 1.31.0 | CPython312/macOS14 arm64 |
| ONNX Script | 0.7.2 | Python3 universal |
| onnx-ir | 1.0.0 | Python3 universal |
| ml-dtypes | 0.6.0 | CPython312/macOS universal2 |
| protobuf | 7.36.2 | CPython310 ABI3/macOS universal2 |
| flatbuffers | 25.12.19 | Python2/3 universal |

All36prior versions and the recorded8core file hashes are unchanged, including
Torch2.14.1, NumPy2.5.3, SciPy1.18.1, sklearn1.9.1, threadpoolctl3.7.0. Python
remains3.12.12. Core requirements and existing extras in `pyproject.toml` are
unchanged; new optional `export` extra pins the three direct packages. The small
JSON dependency record pins all seven wheel/package hashes and the preserved
baseline. Optional imports are lazy; default/controller imports do not require
ONNX or numerical frameworks. Dependency consistency passes.

Primary references: [PyPI ONNX1.23.2](https://pypi.org/project/onnx/1.23.2/),
[ONNX Runtime1.31.0](https://pypi.org/project/onnxruntime/1.31.0/) and
[ONNX Script0.7.2](https://pypi.org/project/onnxscript/0.7.2/).
Raw official metadata/resolver/install receipts are ignored and tied to acceptance.
Package/wheel identities are separate from scientific/model/source/export hashes.

## Frozen science and reconstruction-only export

Canonical loader `CompactAutoencoder.load` is reused unchanged through the existing
model loader. Registry bindings are exact:

| Role | File | Canonical/scientific JSON SHA256 |
| --- | --- | --- |
| Config | `configs/models/compact_autoencoder_v2.json` | `0af02cba0dcab4cd750b19f6357fe5030aadb56c7c0422c4f35ea4adc1521800` |
| Model | `artifacts/models/compact-autoencoder-v2/model.json` | `6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b` |
| Calibration | `results/tables/final/task0008-autoencoder-convergence-summary.json` | `324d7363b3e2d2ec96f57cc88790af99895097a35c91efe4839c3cead25c7d33` |

File-byte hashes are separately in the protocol/summary. Preserve155FP32 parameters,
8→6→3→6→8, hidden ReLU, linear latent/output, eight feature names/order, full-training
provenance and original scalers. AE v1/PCA stay historical/reference models.
ONNX contains **only** already-standardized FP32 `event_features[B,8]` to FP32
`reconstruction[B,8]`; no scaler, score head, thresholds, clipping or quantization.

Canonical scoring remains CPU FP64: cast input and reconstruction before subtraction,
square/sum eight channels, higher anomalous. Four immutable thresholds:

| Historical calibration target FPR | Strict threshold |
| --- | --- |
| 0.1 | 3.478338537407165 |
| 0.05 | 4.681070974717348 |
| 0.01 | 8.324174660133213 |
| 0.001 | 16.642218868621573 |

Decisions remain `score > threshold`, rejecting ties. Runtime adapter rejects wrong
feature order before session creation, non-FP32/rank/width, empty/nonfinite inputs
and batches outside1/8/32/128/1024. Symbolic ONNX shape alone is not validation.

## Actual capture, graph and provider audit

Installed [PyTorch2.14 ONNX API](https://docs.pytorch.org/docs/2.14/onnx.html) and
source were inspected. One explicit `torch.export.export(strict=False)` capture
used a synthetic `[8,8]` example and dynamic batch range1…1024, then modern
`dynamo=True`, opset18, weights included, `external_data=False`, `optimize=False`.
No removed `fallback` argument or legacy/opset retry. Decomposition/lowering and
constant folding may still occur; optimize=False does **not** disable them all.

Actual artifact `results/benchmarks/task0024-ae-onnx-cpu/reconstruction.onnx`:

- 11464bytes; ONNX byte SHA256
 `4250b008fb5dfa6f5951e8448a696a1b3a17a9072a8d945ec1fd683204d04793`.
- Opset18, IR10, domain empty/standard, four`Gemm` and two`Relu`, no custom calls,
  unused functions, external data, sparse or training graph.
- One FP32 input/output with common dynamic batch symbol`s59` and fixed width8.
- Eight FP32 initializers map exactly to four original weights and four biases,
  155learned scalars; actual Gemm transpose/alpha/beta semantics are audited.
- Original parameter payload mapping SHA256
 `92e5c96f9b1bc72e4182f58d44b51bc66e9d32c68c0cde92c3064e3703aa26e4`.
- Graph-manifest canonical JSON SHA256
 `1dbfec2e6cb1f7945e406e5ce02f84108eea275497a41cbe6580ac19d3cf6402`.

ONNX checker/full shape inference pass. Tests also validate legitimate transposed
initializer metadata and MatMul/Add/Transpose forms, while refusing malformed
weights/types/counts/layouts/opsets/domains/topology/external weights. The frozen
primary file was never rewritten to make a graph pass. Its file/manifest hashes
were frozen before real opening and restored afterwards. It is a **derived runtime
artifact linked to the canonical scientific model**, not a replacement model.

[ONNX Runtime APIs](https://onnxruntime.ai/docs/api/python/api_summary.html): available
providers were CoreML,Azure,CPU; selected/effective provider **CPU only**, sequential,
intra/inter-op1, graph optimization`ORT_DISABLE_ALL`, fallback disabled. No CoreML /
GPU or provider sweep. ORT build release commit`402979a` recorded. Torch effective
intra/inter-op1/deterministic algorithms, OpenMP pools1 and native Accelerate mode1
were verified pre/post. All five CPU thread environment variables were1 before
imports. Provider selection/session success alone is not numerical acceptance.

Hash-kind checks distinguish raw UTF8 build text from canonical JSON-string hashes.
Torch canonical string SHA `6d6fa299…918b26c`, raw byte SHA `7dc7bbe0…46daa1c` match
the accepted baseline separately; no Task0023hash-convention defect repeats.

## Independent numerical acceptance

[Derivation](arithmetic-onnx-cpu-v1-policy.md) applies validated outward primitives
to the audited affine/ReLU graph under ordinary FP32/FMA bounded-reduction and
CPU FP64 assumptions. m=2n+2 for n8,6,3,6, nonzero band2^-40…2^40, gamma32/gamma64,
per-operation outward evaluation and local affine diagnostics are independently
checked. Specific native kernels remain unknown; scoped samples/local evidence
are not a universal backend certificate. No fitted epsilon/tolerance search.

Each runtime is bounded against the same rounded FP64 diagnostic with E; pair
bound2E includes both path rounding. SSE propagation includes reconstruction drift
and both rounded FP64 score evaluations. The FP64 diagnostic is not real-arithmetic
truth or a new scientific model. An ignored graph copy exposes intermediate outputs;
its final output matches primary bytes on every tested same-shape window before
using intermediate values for local affine/ReLU evidence.

Four fixed Task0021 recipes,1024synthetic rows each: constants0/+1/−1/+8, signed
powers, seed1729uniform[-8,8], clipped seed1729normal. Every family covers1193windows /
5120row-window presentations across the five batches. All pass, with1036288local
affine scalar checks/0violations and zero strict decisions at all thresholds.
Largest per-family reconstruction/SSE deviations: constants2.38419e-6/1.81633e-6,
powers1.73450e-5/8.94008e-5, uniform6.31809e-5/7.21211e-4,
normal1.49012e-5/3.88729e-5. These are frozen-model synthetic results, distinct from
ordinary integration tests on toy models. Every family passed before real access.

Then one authorized `np.load(...,allow_pickle=False)` read only
`results/benchmarks/task0020-frozen-cpu/prepare/input.npy`,32896B,128-byte bounded
NPY1 header, contiguous little-endian FP32[1024,8], original source-ordered dev-training
aggregates already standardized. No new store/population/custody/rescale/selection.
File byte SHA256`7164bfd7a86a9561ae3abc7b44b396c1a60db0114fc8542443ad3f71d2990a5e`;
payload byte SHA256`2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05`.
Metadata/header/file hashing is distinct from the single numerical opening.

Real comparison uses a fresh canonical PyTorch1024 reference and every grid window:

| B | Windows | Unique rows covered | Reconstruction max abs error | Max reconstruction error/bound | SSE max abs error | Max SSE error/bound | Threshold mismatch counts |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 1024 | 1024 | 3.9100646973e-5 | 0.00787368586650 | 4.8503804395e-5 | 0.00160749274372 | 0/0/0/0 |
| 8 | 128 | 1024 | 3.9100646973e-5 | 0.00787368586650 | 4.8503804395e-5 | 0.00160749274372 | 0/0/0/0 |
| 32 | 32 | 1024 | 3.9100646973e-5 | 0.00787368586650 | 4.8503804395e-5 | 0.00160749274372 | 0/0/0/0 |
| 128 | 8 | 1024 | 3.9100646973e-5 | 0.00787368586650 | 4.8503804395e-5 | 0.00160749274372 | 0/0/0/0 |
| 1024 | 1 | 1024 | 3.9100646973e-5 | 0.00787368586650 | 4.8503804395e-5 | 0.00160749274372 | 0/0/0/0 |

Ratios are maximum **pointwise** error/its own bound, not ratios of independent
maxima. Peak utilization0.787369% reconstruction /0.160749% SSE. Numerical bounds
are conservative envelopes, not measured drift or learned tolerances. Total real
windows1193, row-window presentations5120, unique real rows1024. Local scalar
checks259072including canonical reference/ORT/PyTorch window diagnostics,0violations;
maximum local ratio0.27309913548849507. All finite/supported value/bound gates pass.

Own-runtime same-shape repeats, primary/diagnostic final outputs and separated /
adapter FP64 SSE are byte exact; same-runtime1e-12/1e-12 gate passes. Cross-runtime
reconstruction/scores are **not** byte identical and are admitted only by propagated
bounds plus independent strict-decision gates. Same maxima across batches are
observations, not proof of all cross-shape byte equality.

Canonical reference reconstruction payload SHA`d1bd8473…d5f7467`, score SHA
`d2a3ab08…b398117`, diagnostic SHA`979ed84b…6ef517`, envelope SHA`b0115155…27b89`
restore. Parameter/input/threshold payload hashes pre/post match. Threshold payload
SHA`408dc57e…fc21a1`; sample canonical margins remain0.00933623417/0.004083978687/
0.1601266843/3.752131356. ORT per-grid margins are retained in summary. Agreement on
1024training rows is not universal decisions, calibrated FPR, signal discrimination,
AUC/AP, test acceptance or trigger readiness.

## Finite resource, wall and presentation accounting

One stdlib parent/one fresh numerical worker, exclusive ignored root reserved
before exporting frozen weights. No alternate/reset/overwrite/replay selector;
completed attempt consumes its slot. Parent/token/source/acceptance checks precede
work. Parent deadlines cover blocked import/export/runtime calls; original host
helpers retain bytes, fresh phase/window-operation checks and50mswatcher intent.
WARN advisory/unknown disclosed, CRITICAL/malformed primary accounting latched.
Optional global context has no floor/readiness loop; no app/cache/privilege changes.

| Actual stage/accounting | Seconds | Fixed limit |
| --- | ---: | ---: |
| Export + graph/provider/model checks | 0.620290792 | 30 |
| Four-family synthetic equivalence | 12.587494542 | 60 |
| Conditional real equivalence + final checks | 3.290413666 | 60 |
| Instrumented numerical imports | 1.748192458 | Part of30s shared allowance |
| Worker cleanup | 0.000756375 | Bounded2s inside whole budget |
| Whole worker | 18.723150375 | Inside attempt180 |
| Parent dispatch/startup/reaping | 19.113214166 | Inside attempt180 |
| Whole attempt | 19.407739000 | 180 |

Stages use actual phase boundaries; imports/cleanup/parent/worker intervals overlap
as stated and are not summed into a fabricated exclusive cost.150s stage caps
leave30s for shared imports/orchestration/cleanup. These wall numbers are **resource
accounting**, not forward/adapter latency or evidence of speedup.

Worker peak467320832B=445.671875MiB RSS /226148352B=215.671875MiB whole-native,
below1GiB/512MiB; parent29802496B=28.421875MiB below128MiB. RSS/native overlap and
are not added.12304guard samples/331periodic; every observed pressure is unknown /
errno1, not NORMAL. No latched failure, watcher closed, child reaped, stage/whole
parent deadlines passed. Scheduling/GIL/OS limits preclude hard real-time stopping.
Source/config/protocol/library and primary artifact/manifest identities restore.

Synthetic forward row presentations: PyTorch57344, ORT61440, diagnostic ORT20480,
FP64 full-model4096/local-affine180224. Real: PyTorch14336, ORT15360, diagnostic
ORT5120, FP64 full-model1024/local-affine45056. Layer diagnostics are counted
separately from full forward calls and unique rows; none are performance timer
pairs. Real prepared-array reads1/unique rows1024/population requests0/store custody0 /
optimizer updates0/performance timing invocations0. No per-event scores or new
canonical scientific models are persisted.

Fresh filtered MacBook Pro/Mac17,2/M5/16GB/CPU descriptor`proc10:4:6:0`, arm64 /
macOS26.6.2 and shared-host load are recorded. Native sysctl and thermal fields
remain unavailable/unknown; no application contents inspected. Compiled provider
availability and old unavailable MPS receipt are not physical MPS acceptance.

## Software validation and next bounded task

1111full tests /1111portable /78new tests pass, with actual optional ONNX export /
runtime integration and no optional skips. Tests cover lazy absence, exporter API /
opset/shape, layout/155parameter mapping, graph/provider refusal, dynamic B1,
nonfinite/domain/feature inputs, rational/cancellation/local/FP64/SSE bounds,
strict ties, own-repeat/mutation, continued failed-grid reporting, reservation /
foreign/partial states, blocked native/import/export deadlines, peaks and cleanup,
and raw-text versus canonical JSON hash conventions. Existing1033tests remain
history, not the current acceptance count. Lint/format/dependency consistency pass.

Guarded CPU smoke exports only a synthetic model:5.783868s,433160192B RSS /
221954048B native, inside1GiB/512MiB, watcher closed/no MPS check/real read.
Portable copy has no operational inputs, frozen artifacts, receipts or Git;
the three narrowly scoped historical in-memory schema fixtures are unchanged.
Hosted CI remains **unverified**. Complete114source/dependency identities, policy /
protocol and all validation evidence were frozen before the one real attempt;
no executable/policy repair or replay afterwards. Acceptance byte SHA256
`06481f34a3d3691dd4e7a0dc18267ca6f213eef66d99165415fab0b671a16137`.
Final validation uses small metadata/byte hashes/receipts, not a numerical replay.

Recommend **Task0025 — Frozen PyTorch/ONNX Runtime Paired CPU Inference Benchmark**,
with separate authorization. Bind this accepted11464B artifact/hash,155weights,
inputs/calibration/provider/arithmetic policy and current runtime/source acceptance.
One new exclusive independent campaign; PyTorch1,ORT1,PyTorch2,ORT2,PyTorch3,ORT3;
same1024prepared rows, five batches,20warm-ups/200invocations and three clearly
matched forward/CPU score/public adapter scopes. Preserve pre/post local/bound /
repeat/hash/strict decisions and all three distributions. Fresh-process1GiB RSS /
512MiB native, parent128MiB, one worker,60s each/30s aggregation/600swhole and2s
cleanup, no required speedup. Historical CPU times are context, not contemporaneous
repetitions. No new export/refit/calibration/MPS/test. Not implemented/authorized here.

Implemented CLI `.venv/bin/python -m raregate.exports.onnx_controller --run-export`
is now consumed; do not rerun. No accepted performance benefit is claimed.

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

The actual attached prompt was copied byte-for-byte: LF line endings, no terminal
newline in the user's attachment. This exact byte identity remains under the
preregistered prompt hash and is not normalized after execution. All newly authored
text uses LF with a terminal newline; historical CRLF results remain unchanged.
No persistent Git whitespace setting was changed.
