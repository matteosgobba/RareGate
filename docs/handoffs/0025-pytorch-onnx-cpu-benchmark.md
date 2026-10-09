# Task0025 — Frozen PyTorch/ONNX paired CPU benchmark

## Metadata
- Date: 2026-10-09; branch main, upstream origin/main.
- Base: cacaefd3ac00a6c657b14109eb19e0119e25ada4 (Task0024 committed).
- Initial index and working tree clean. Task0025 only; validation/execution pending.

## Scope
Isolated foundation, synthetic validation, current-source freeze and one conditional
paired campaign; no scientific training/calibration/test exposure. Preserve prior
source, protocols, receipts, raw results and scientific bytes.

## Final outcome — 2026-10-09

Implementation/software validation complete. **Campaign failed/consumed, with
complete numerical/timing coverage but no accepted paired performance comparison.**
All 90 cells, 18000 measured invocations, 1800 warm-ups and 1200 empty pairs exist.
All six local timing bodies pass pre/post gates and write completed receipts.
Preparation + first five timing processes exit 0; ORT3 writes its receipt at
10.072625083994353 s but remains alive. Parent operation deadline terminates/reaps
it at 58.03058020900062 s, SIGTERM / exit −15. Raw worker receipt is unchanged;
workflow independently records failed parent acceptance. Cause of exit wait unknown.
Whole campaign 128.7809915830003 s ≤ 600 s. No normal aggregation stage reached;
failure-path aggregation preserves all distributions/counters and provisional ratios.
No executable/policy repairs, replay or replenished allowance after reservation.

An intermediate update identified complete worker-local measurements/numerical gates
before the final parent dispatch was available. Final report/summary/memory explicitly
resolve this distinction: completed local receipt is not accepted process lifecycle.

## Changes, files and decisions

Six isolated source modules implement strict metadata/source/acceptance, stdlib
controller/exclusive reservation, fresh sequential workers, numerical admission,
three scope boundaries, and paired/pooled statistics plus guarded toy smoke.
One strict benchmark protocol and 68 self-contained new cases. Existing source,
launch routes, guards, numerical policies, loaders, model/scaler/calibration/
input/graph/dependency and receipt bytes unchanged. Initial snapshots are ignored;
only current README/project-memory/index overlap old tracked files. Memory 1.18
reconciles actual Task0024 commit without changing its historical handoff.

Prompt normalized to LF with terminal newline **before** identity freeze; body is
the actual attached Task0025 request. Historical Task0024 raw prompt bytes remain
unchanged. No new scientific model/export/dependency/device/test work.

See [report](../pytorch-onnx-cpu-benchmark.md),
[protocol](../../configs/benchmarks/pytorch_onnx_cpu_v1.json),
[summary](../../results/tables/final/task0025-pytorch-onnx-cpu-benchmark-summary.json),
[90-cell CSV](../../results/tables/final/task0025-pytorch-onnx-cpu-benchmark-cells.csv).
Input/graphs/acceptance/logs/timing/guard/numerical receipts and snapshots remain
ignored. The diagnostic graph's literal byte SHA is newly recorded for the existing
file; Task0024 receipt recorded creation/final parity but no separate SHA field.
No graph was regenerated, and no old identity field was invented.

## Measured results and numerical/resource limits

All 12 pre/post grid gates, 14316 windows, 3108864 local affine scalar checks:
0 violations, four threshold mismatches 0/0/0/0. Reconstruction max absolute
3.910064697265625e-5 / max pointwise bound utilization0.00787368586649532;
SSE4.850380439513913e-5 /0.0016074927437233696. Exact own-repeat,
diagnostic/primary final, same-shape SSE, restored CPU/ORT/diagnostic/envelope /
model/input/threshold/source/graph/provider/thread identities. Cross-runtime bytes
not required; supported rounding contract/local evidence is not universal parity.

Descriptive pooled mean ratios PyTorch/ORT for reconstruction B1/B128/B1024:
1.908984 /1.581537 /1.390765; public adapter4.628969 /1.973579 /1.346169.
All raw forward pair ratios >1, but none is an accepted campaign speedup.
PyTorch1 B1 adapter mean169.292 µs versus23.662/23.599 µs later; max1.594166 ms;
no outlier removal or inferred causal attribution. Shared score-only CPU scope
is not ONNX graph performance. All three ratios/geometric means/pooled means,
worker distributions and linear population statistics are preserved separately.

Observed worker RSS417841152 B =398.484375 MiB; whole-native213565440 B
=203.671875 MiB, below sampled1GiB/512MiB caps; parent38748160 B
=36.953125 MiB ≤128MiB. RSS/native overlap. Worker guard closes at reported cleanup;
ORT3 memory/pressure during later process-exit wait unknown, so its full-lifetime
memory cap is not certified. Parent deadline remains active; child reaped.
Pressure always unknown/errno1, no fabricated NORMAL; optional context has no floor.
Watcher50msintent may overlap timings, no counter/timer subtraction/hard-real-time
claim. No OS/app/cache/privilege management.

## Access and provenance

1 original +6 local prepared-array loads, same1024unique dev-training rows;
byte-identical copy. 0 population requests /0 store custody /0 calibration /0 optimizer.
Timed presentations4294800 (2863200 forward); warmup429480 (286320 forward).
Verifier Torch172032 /ORT208896 /diagnosticORT61440 forward rows; FP64 diagnostic
12288 full-model/540672 local-affine rows. Prepared forward30720 /
prepared equality184320 /CPU reference12288 rows. Unique rows are not presentation
counts; synthetic families are counted separately in the summary.
MacBook Pro/Mac17,2/M5/16GB/proc10:4:6:0, arm64/macOS26.6.2, AC/battery100%,
shared load recorded; thermal/native sysctl unknown. Python3.12.12/Torch2.14.1 /
NumPy2.5.3/ONNX1.23.2/ORT1.31.0/script0.7.2 and typed build hashes unchanged.
Particle192/192consumed/canonical deferral unchanged; no MPS check.

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

## Validation and reproducibility

Before freeze/reservation: `pytest -q` 1179 pass; portable isolated copy1179 pass,
no operational data/artifacts/receipts/Git; 68 new tests include actual optional
synthetic runtime sessions/all three boundaries. Ruff lint/format pass, pip check
no broken requirements. Guarded toy CPU smoke30cells/6000timings passes,8.449469s,
462520320B RSS/226148352B native, closed guard, no real inputs/MPS. Temporary toy
export in tests/smoke is not another frozen scientific export.

121 applicable source/dependency hashes/protocol/prompt and validation files froze
before atomic reservation. Source acceptance byte SHA256
`0e00addf4d2668733043a7ca466f337de5ba0afa9546d1786f5d655b5a4a290a`.
Final checks recompute raw statistics/counts/ratios, JSON/CSV/report agreement,
prior identities/receipt/grant/source/graph/input-copy relationships, links/JSON/
whitespace/exclusions and Git state; metadata-only, no numerical array reopening.
Synthetic validation does not prove every framework/interpreter exit behavior.
Hosted CI unverified; no successful real-campaign acceptance invented.

CLI explicit campaign action:
`.venv/bin/python -m latenttrigger.benchmarks.pytorch_onnx_cpu --run-campaign`.
**Consumed: do not rerun.** No alternate output/reset/retry selector; a future replay
requires separate authorization and implementation/source acceptance.

## Follow-up

Recommend **Task0026 — Guarded Frozen PCA/AE Final Scientific Comparison**.
Existing evaluation-v1 and run_final support current native PCA-v1 and compact AE
v2 identities/calibration/metrics. Scientific contract sufficient; finite full-store
process/deadline/campaign orchestration is the narrow missing implementation.
A separately authorized task should validate/freeze that protection, preserve
4096-row evaluation/tail/config/scaler/score/frozen thresholds, then explicitly
unblind once with pre-read/partial-failure audit and counts/uncertainty. Current
benchmark dev caps do not validate full-store custody/evaluation. No held-out
access/next-task implementation here; optional ORT shutdown investigation/MPS /
CoreML/quantization do not automatically block scientific closure.

## Git

Initial and final branch main/upstream origin/main, HEAD cacaefd3 unchanged,
index empty; no staging/commit/push. Intended sixteen files only: prompt/handoff,
protocol, six modules, test, report/JSON/CSV, README/memory/index. Exclude ignored
campaign evidence, scientific arrays/graphs, source acceptance, logs and snapshots.
Suggested Conventional Commit:
`feat: add paired CPU benchmark with numerical evidence and exit failure`.
