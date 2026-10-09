# Task0024 — Frozen AE ONNX CPU Export and Equivalence Foundation

## Initial metadata — 2026-10-09

- Branch `main`, upstream `origin/main`.
- Base HEAD `933cba22a2243ecd81d573bef4af8688678b9d33`.
- Initial working tree and index clean; Task0022/0023 later commits require full identity verification.
- Scope: additive optional dependencies, isolated reconstruction-only ONNX CPU foundation and synthetic validation, one conditional frozen-model export/equivalence attempt.
- No fitting/calibration/MPS check/replay/particle/test/performance campaign.
- Dependency, software, source freeze and bounded execution checks pending.
- Preserve all Task0020–0023 source/protocol/results/receipts and scientific/particle identities; sources read-only.

## Final metadata and results — 2026-10-09

The initial metadata above preserves task-start scope/pending state. Actual
Task0022commit`61611341a90f2bd2225559b8a3245ec3e6ed08a7` and Task0023commit /
base HEAD`933cba22a2243ecd81d573bef4af8688678b9d33` verified; main/origin-main and
empty index preserved. Historical reports/handoffs remain byte unchanged; current
README/memory1.17/index reconcile commits and outcomes. No staging/commit/push.

**Status complete/accepted/consumed:** one frozen-model attempt, no replay or
post-freeze executable repair. Derived reconstruction export11464B/opset18/IR10,
all155FP32values mapped exactly, four fixed synthetic families accepted before
one real np.load of the original1024prepared rows; all1193windows/five batches
pass local/outward/repeat/strict-decision gates.0performance invocations.

## Dependencies, changes and technical decisions

- Before installation:36distribution versions/core file/build identities recorded;
  official PyPI metadata/platform wheels validated, all installed distributions
  constrained, additive-only resolver report checked. Sandbox DNS unavailable;
  tool-approved network install remained scoped to `.venv`, no MPS workaround.
- Added ONNX1.23.2, ORT1.31.0, onnxscript0.7.2, onnx-ir1.0.0, ml-dtypes0.6.0,
  protobuf7.36.2, flatbuffers25.12.19,164.874146s≤300. All original36versions /
  core identities/builds retained; optional export extra only, core requirements
  and prior extras unchanged. Exact wheel/package hashes in small dependency record.
- New isolated exports package: lazy graph/export/runtime helper, independent
  numerical checks, strict protocol/source/dependency metadata, stdlib controller,
  guarded worker/synthetic CPU smoke;78self-contained tests. Old104sources unchanged.
- Existing canonical loader/FP32forward/features/scalers/thresholds/FP64CPU SSE
  arithmetic remain. No preprocessing, score/scaler export, approximation/refit.
- One explicit Torch export strict=False capture, synthetic8×8/dynamic batch1–1024;
  dynamo=True/opset18/optimize=False/weights included/no external data. No removed
  fallback flag or legacy/opset retry; constant folding is not claimed disabled.
- Actual standard fourGemm/twoRelu/IR10/dynamicFP32[B,8], eight initializers155values,
  exact transpose/bias mappings, checker/shape/provider audits pass. Session CPU
  only, sequential1/1, optimizer disabled/fallback disabled; available CoreML/Azure
  distinct from selected CPU. No primary graph rewrite to fit policy.
- Independent operation-level outward policy supports ordinaryFP32/FMA affine /
  exactReLU under checked band, local actual inputs, both FP32 and roundedFP64
  errors/SSE evaluation. Native kernel details unknown, no universal certificate
  or observed-tolerance fitting. Diagnostic ignored graph final equals primary
  bytes before using local intermediates. Same-runtimeSSE1e-12 is not cross-runtime
  reconstruction tolerance; strict frozen decisions remain independent.

## Actual numerical/identity evidence

Primary ONNX SHA256`4250b008fb5dfa6f5951e8448a696a1b3a17a9072a8d945ec1fd683204d04793`;
graph-manifest canonical JSON SHA`1dbfec2e6cb1f7945e406e5ce02f84108eea275497a41cbe6580ac19d3cf6402`.
Canonical scientific AE SHA6a7044ae… unchanged; parameter payload92e5c96f… and
threshold payload408dc57e… restore. Raw UTF8/canonicalJSON build hashes are explicit
and separately verified, fixing no historical receipt or relabeling Task0023proof.

Four frozen-model synthetic families constants/powers/uniform/normal,1193windows /
5120row-window presentations each,1036288local scalar checks/0violations and all
four threshold mismatches0. Real:1024unique reused rows/1193windows/5120row-window
presentations,259072local scalar checks/0violations. Every batch1/8/32/128/1024:
maxreconstruction3.910064697265625e-5/error-bound utilization0.00787368586649532;
maxSSE4.850380439513913e-5/utilization0.0016074927437233696; strict decisions0/0/0/0.
Maximum local ratio0.27309913548849507. Own repeats/primary-diag final/separated /
adapterSSE byte exact; cross-runtime outputs/scores not byte identical, accepted
by preregistered envelopes. References/parameters/threshold/input/export restore.

## Resource, wall, access and validation

Single fresh worker: import1.748192458s, export0.620290792s≤30, synthetic12.587494542s≤60,
real3.290413666s≤60, cleanup0.000756375s, worker18.723150375s/whole19.407739s≤180.
These are resource-accounting boundaries, no latency/throughput/timing campaign.
Worker RSS467320832B/445.671875MiB≤1GiB, native226148352B/215.671875MiB≤512MiB;
parent29802496B/28.421875MiB≤128MiB.12304samples/331periodic, unknown pressureerrno1,
no latched failure, watcher closed/child reaped/stage/whole deadlines passed.
GIL/OS stopping limits explicit, caps not machine-wide headroom and RSS/native overlap.

Numerical real array reads1/unique rows1024; source/header/byte verification separate
from array openings. No store/custody/population request/optimizer/performance timer.
Real PyTorch forward14336/ORT15360/diagnosticORT5120row presentations; diagnostic
FP64full1024/local-affine45056. Synthetic totals recorded separately. No per-event
scores, canonical new model, data copy or new scientific population persisted.

1111full/1111portable/78new cases pass; actual optional synthetic export/runtime
integration no skip, lint/format/dependency consistency pass. Guarded CPU smoke
synthetic only5.783868s/RSS433160192/native221954048, watcher closed/no MPS check /
real read. Original narrow three portable legacy schema fixtures unchanged; no
operational input/artifact/receipt/Git in portable tree. Hosted CI unverified.
114-source/dependency acceptance frozen before attempt; original104source /
101oldoperational files/3acceptances preserved. Acceptance byte SHA
06481f34a3d3691dd4e7a0dc18267ca6f213eef66d99165415fab0b671a16137.

Final checks use metadata/byte hashes/receipts only: JSON/report/counts/source /
dependency/graph/science/lineage/local links/exclusions/whitespace. No numerical
replay, export retry or old scientific execution; historical CRLF files unchanged.

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

## Limitations and next task

Accepted derived ONNX graph and scoped equivalence establish correct behavior on
this audited supported domain/sample, not universal decisions/calibratedFPR/signal
quality/trigger readiness or speed benefit. Shared host/load/unknown native kernels
and practical guards remain. Original unavailable MPS failed proof/software repair,
accepted CPUv2/historical failures and particle192/deferral unchanged.

Recommend Task0025 — Frozen PyTorch/ONNX Runtime Paired CPU Inference Benchmark,
with new separate authorization, fixed exclusive slot/current source/artifact /
provider/policy gates, contemporaneous three pairs/five batches/three timing scopes,
20warm-ups/200calls/all distributions, finite guards/no required speedup. Report
contains implementation-ready bounded brief. Not implemented or executed here.

## Files and manual Git

Prompt/handoff, report/summary, strict protocol/arithmetic policy/dependency record,
seven new package files/tests, optional pyproject extra and live README/memory/index
are intended. ONNX/diagnostic binaries, raw acceptance/audits/receipts/arrays/package
cache/resolver/logs/temporary validation helpers remain ignored; no new Git export
exception or CSV. Index left empty, main tracks origin/main, no commit/push claimed.
Suggested outcome-accurate Conventional Commit:
`feat: add validated frozen AE ONNX CPU export and equivalence`.

The actual attached prompt has LF and no terminal newline, copied byte-for-byte
under the frozen prompt hash; do not normalize after execution. All authored new
text isLF/terminal newline and historical resultCRLF remains unchanged. Ordinary
Git whitespace checks pass; no persistent Git setting changed.
