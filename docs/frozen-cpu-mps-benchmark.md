# Task0023 — Frozen CPU/MPS comparison foundation

Implemented software, **no accepted physical MPS proof or paired measurements**.
The sole fresh check observed `is_built=True`, `is_available=False`. An initial
build-hash integration defect also failed admission; it was repaired with software
validation only, preserving the original source/acceptance/failed receipt and
without another device check. The real campaign is **unreserved**, with zero real
array reads, rows, presentations, population/custody requests and optimizer updates.

This is an engineering/device admission outcome, not a scientific rejection of
compact AE v2 or evidence of absent physical GPU. The cause of unavailability is
unverified. Task0022's accepted90-cell CPU reference and Task0020–0022 history,
all scientific artifacts and particle192/192 consumption/deferral are unchanged.

[Actual prompt](prompts/0023-frozen-cpu-mps-benchmark.md),
[handoff](handoffs/0023-frozen-cpu-mps-benchmark.md),
[strict protocol](../configs/benchmarks/frozen_cpu_mps_v1.json),
[device arithmetic policy](arithmetic-mps-v1-policy.md), and
[curated summary](../results/tables/final/task0023-cpu-mps-benchmark-summary.json).
No cell CSV exists because no timing cells exist.

## Verified prerequisites and scientific contracts

`main` tracks `origin/main`, HEAD `17a7146f775df47f1b542e18300860275f01c10c`.
Task0022 remains16 staged files, not a claimed commit. Its exact index blob map
and initial live README/memory/index snapshots were saved ignored. Task0023 edits
those three working files without changing their staged Task0022 versions. The
old report/handoff/protocol/derivation/summary/CSV and complete next-task brief
were inspected. Historical handoffs and accepted bytes were preserved.

Use only the unchanged canonical compact-autoencoder-v2 loader:

| Binding | Frozen value |
| --- | --- |
| Configuration | `configs/models/compact_autoencoder_v2.json` |
| Artifact | `artifacts/models/compact-autoencoder-v2/model.json` |
| Calibration | `results/tables/final/task0008-autoencoder-convergence-summary.json` |
| Config canonical JSON SHA256 | `0af02cba0dcab4cd750b19f6357fe5030aadb56c7c0422c4f35ea4adc1521800` |
| Model scientific JSON SHA256 | `6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b` |
| Calibration scientific JSON SHA256 | `324d7363b3e2d2ec96f57cc88790af99895097a35c91efe4839c3cead25c7d33` |
| Architecture | `8→6→3→6→8`,155 frozen FP32 parameters, two ReLUs, eval/inference |
| Input | Already standardized FP32 eight aggregates, original feature/scaler/full-training provenance |
| Canonical score | CPU FP64 casts of input and reconstruction **before** subtraction, squares and eight-channel SSE; higher is more anomalous |

All file-byte hashes are separately bound by the protocol; they are not the
canonical/scientific JSON hashes above. AE v1 remains historical. PCA remains
Task0022's accepted CPU reference; no PCA/MPS redesign occurs.

| Target FPR from frozen calibration | Immutable threshold; strict `score > threshold` |
| --- | --- |
| 0.1 | 3.478338537407165 |
| 0.05 | 4.681070974717348 |
| 0.01 | 8.324174660133213 |
| 0.001 | 16.642218868621573 |

The sole permitted source is
`results/benchmarks/task0020-frozen-cpu/prepare/input.npy`:32896 bytes,128-byte
bounded non-pickle NPY1 header, little-endian contiguous FP32 `[1024,8]`.
File SHA256 is `7164bfd7a86a9561ae3abc7b44b396c1a60db0114fc8542443ad3f71d2990a5e`;
payload SHA256 is `2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05`.
Original preparation lineage and these small-file metadata/byte hashes were
verified. **No numerical array opening occurred.** Hash/header verification is
separate from counted numerical reads and is not a processed-store custody replay.
The prospective preparation worker opens the original once and copies its bytes;
each of six workers opens its local copy once. No other population, source,
label, test, store, scale, row selection or second read is accepted.

## Isolated foundation and numerical policy

New `cpu_mps*.py` modules implement a stdlib parent, guarded fresh workers,
primary device accounting, numerical diagnostics, timing and forced CPU software
smoke. Existing loaders, score code, timing kernels, launch routes and policies
remain byte unchanged. The portable test plugin supplies in-memory synthetic
model/history documents to three old schema tests, without changing their source
or reading frozen artifact files in the portable copy.

The [new derivation](arithmetic-mps-v1-policy.md) consults installed APIs and
PyTorch2.14 primary MPS/backend/environment/synchronization/allocation docs plus
matching native Linear/fallback/shader source. Ordinary FP32 operations, no
reduced precision, bounded affine reductions and exact ReLU are **supported
operation-level assumptions**, not inferred solely from output dtype or promoted
into a universal Metal certificate. Internal native accumulation/order remain
unknown. Mandatory device-local checks and the fixed physical study are required
for scoped admission; their physical validity has **not** been established here.

Reuse outward FP64 primitives only. The n=8,6,3,6 recurrence uses m=2n+2,
u32=2^-24/u64=2^-53, gamma rounding and the sum of CPU/device reconstruction
bounds; independent local affine checks use actual captured device FP32 inputs.
Checked nonzero support is `[2^-40,2^40]`; finite normal bounds exclude underflow /
overflow domains. ReLU is checked against exact max. CPU SSE bounds include
reconstruction propagation and32-operation FP64 evaluation allowance. No fitted
error multiplier/tolerance search or real maxima influence policy.

Every actual-shape window must satisfy separated/public SSE atol=rtol=1e-12,
exact own same-shape repeats, frozen FP32 parameter/input transfer round trips,
finite/local/global bounds and **zero** strict decision mismatches versus a fresh
canonical CPU1024 reference. CPU/device reference hashes, CPU diagnostic/envelope
and frozen hashes must repeat pre/post. Cross-device byte equality is recorded
where obtained, never required. Relative-error denominator is explicitly
`max(abs(reference),float64.tiny)`. Diagnostic hooks/copies/bounds stay on CPU,
outside timing. No actual MPS numerical/threshold/roundtrip acceptance is claimed.

Five CPU thread variables are1 before imports; effective PyTorch1/1, deterministic
algorithms, OpenMP1 and Accelerate native getter/setter mode1 are verified.
`PYTORCH_ENABLE_MPS_FALLBACK=0`, `PYTORCH_MPS_FAST_MATH=0` are requested/observed;
normal operators/allocator protections remain. Watermark, preference and profiler
overrides are refused. There is no public getter for every internal math option.

## Fixed timing and finite protection

The paired campaign path is only `results/benchmarks/task0023-cpu-mps/`.
Availability/device proof has a separate exclusive ignored path
`data/task0023-device-proof/`. Any existing state blocks another automatic route.
The parent atomically reserves real work only after current source-bound software,
availability and device study success. No old receipt is reusable admission.
Fresh workers verify parent/token/predecessors, source, dependencies, frozen
metadata and current device flags. No numerical framework enters the parent.

Fixed order: CPU1,MPS1,CPU2,MPS2,CPU3,MPS3; batches `[1,8,32,128,1024]`, ascending
batch then reconstruction / CPU score-decision / public adapter-decision.
Per cell20 untimed warm-ups then200 measurements, independent resets of
`start=(i mod(1024/B))*B`. Timer `perf_counter_ns`;200 empty pairs per worker,
reported without subtraction. A complete campaign would have90cells/18000timings/
1800warm-ups/1200empty pairs, with all outliers retained and no speed requirement.

1. Prepared reconstruction uses preloaded FP32 CPU/device tensors. MPS pre-sync
   is outside the pair; forward plus completion sync are inside. No output CPU
   transfer occurs inside this scope; allocations/encode validation are retained.
2. Score/decision is **CPU postprocessing for both paths** using actual-shape
   precomputed reconstruction already copied to CPU. It includes FP64 casts,
   finite SSE and all four comparisons; no forward or device transfer.
3. Public adapter invokes the unchanged score on NumPy FP32 inputs and the model
   on its selected device. MPS input transfer, forward, output transfer, CPU FP64
   SSE/decisions and final completion sync remain inside. No custom fast scorer.

Loading/imports/model-device setup/window transfers/diagnostics/guards/cleanup
are outside pairs but inside wall budgets. Monitor interference may overlap;
no counters or timer/sync costs are subtracted. Separate medians are never summed
as measured end-to-end cost. Raw decompression and online aggregates are unmeasured.

Worker caps:1GiB lifetimeRSS/512MiB whole native; parent128MiB. MPS tensor current
allocations256MiB, driver512MiB, validated primary APIs. CPU device accounting is
not applicable. Metrics overlap on unified memory; no disjoint sum. Process caps
are engineering limits, not available-machine headroom or allocator tuning.
Preparation60s, six workers60s each, aggregation30s:450sallocated/600swhole;
2s terminate/kill/reap slack inside each budget. Availability30s/device study60s,
combined orchestration120s, separate from the real budget. One numerical worker;
fresh phase and invocation checks,50ms periodic scheduling intent, independent
parent deadlines cover blocked imports/sync/accounting/native work. Grace and
watcher closure are finite; GIL/OS scheduling prevent hard real-time guarantees.
NORMAL permits, WARN advisory, unknown pressure disclosed, CRITICAL/malformed
primary accounting latches. Optional global context≤2s has no floor/stability loop.
No apps inspected/managed, dedicated window, cache manipulation or privilege work.

Statistics retain count/min/max/mean/population std and linear p50/p95/p99 for each
cell and all three worker distributions, plus median worker medians. Pooled
throughput is `B/mean(invocation seconds)`; amortized event time is mean/B and
B1 measures single-event latency. Paired CPU mean/MPS mean (>1 faster MPS) equals
matching MPS/CPU throughput ratio; retain each pair and geometric mean of the three.
Score-only differences would not measure MPS acceleration. No latency/ratio table
is manufactured for this blocked outcome; historical CPU values are not substituted.

## Actual check, failure lineage and software-only repair

The frozen precheck acceptance covered104source files,1032full/portable tests,
90 new tests, lint/format/dependencies and guarded CPU smoke. The one fresh
availability process completed within budget, observed PyTorch2.14.1/Python3.12.12,
arm64/macOS26.6.2, build support true and availability false. No MPS tensor operation,
device allocation query, synthetic device study, prepared array or real slot began.

Its original receipt status is **failed** (`Unsupported pinned PyTorch build`).
Metadata-only review established that this diagnosis came from an integration
error: the new helper compared raw UTF8 SHA256 `7dc7bbe0…46daa1c` against Task0022's
canonical JSON-string SHA256 `6d6fa299…918b26c`. The stored build texts are byte
identical; a changed runtime is not established. Actual flags survive in failed
values. The original code/acceptance/protocol/receipt remain preserved ignored.

Only the software comparison was corrected: compare canonical JSON-string hashes
and disclose raw hashing separately. A regression test now catches the distinction.
Final software-only acceptance covers104files,1033full/portable tests and91new
cases. It is **not physical or execution acceptance**. Three project source files
changed after the blocked check; that check is not promoted to current-source
proof. Original precheck acceptance/validation outputs were preserved, final
software evidence is separate, and no automatic check/study/campaign was replayed.
The ordinary CLI remains consumed/blocked, including after software repair.

| Actual observation | Value |
| --- | --- |
| Whole automatic orchestration | 2.5725052500056336s |
| Child wall including imports/cleanup | 1.9658761250029784s |
| Parent dispatch including startup/reap | 2.268225749998237s |
| Child numerical imports / cleanup | 1.3207439169927966s /0.00017954201030079275s |
| Availability child RSS / whole native | 338690048B =323MiB /180011008B =171.671875MiB |
| Stdlib parent peakRSS | 29097984B =27.75MiB |
| Guard samples / periodic checks | 36 /31; unknown pressure errno1, no latched cap failure |
| Owned watcher / child | Closed /reaped; parent deadline passed |
| Device peaks | Unknown/unverified, no query; no fabricated zeros |
| Real rows/reads/presentations, store/population/custody/updates | 0 throughout |
| Timing cells, invocations, warm-ups, empty pairs | 0;90 scheduled cells absent |

Fresh filtered hardware: MacBook Pro/Mac17,2, Apple M5,16GB; processor descriptor
`proc 10:4:6:0` indicates ten CPU cores. AC power, charged100%; load averages
2.0405/2.5527/2.9473. Native sysctl RAM/core/OS build fields and thermal fields
were unavailable; GPU cores, Metal version and kernel details remain unknown.
Start-only optional available context3.316650390625GiB was not admission; no
end sample was collected after failure. No inference from failed availability to
physical GPU absence or sandbox causation. No application content was inspected.

## Validation, limits and next task

Final1033full synthetic tests /1033portable /91new cases pass; lint, format,
dependency consistency and forced CPU smoke pass. CPU smoke never queried MPS;
it confirms own finite host footprint/thread enforcement/cleanup on synthetic
inputs, not MPS support. A precheck software-smoke cleanup-method error was fixed
before physical work; initial failed smoke evidence is retained. Portable tests
use source/config/docs/curated small metadata and three synthetic schema
substitutions, without data, frozen artifacts, operational receipts or `.git`.
Hosted CI is **unverified**. Final metadata-only validation checks JSON/report,
receipt/source/frozen/index relationships, local links, exclusions and whitespace.

No paired timing tail/outlier/ratio exists. Fixed ordering, shared-host variability,
200-call p99 resolution, monitoring and synchronization overhead limit any future
interpretation. Agreement on1024training rows would not establish universal
threshold decisions, calibrated FPR, AUC/AP, signal discrimination or trigger
readiness. Particle contracts and consumed192/192 remain unchanged.

Recommend **Task0024 — Frozen AE ONNX CPU Export/Equivalence Foundation**, independent
of MPS readiness. With separate authorization, verify installed export/ONNX Runtime
operator/provider support, pin one supported opset and CPU FP32 Linear/ReLU graph,
preserve155weights/features/scalers/all thresholds, derive an independent numerical
and strict-decision gate and validate synthetically before any existing-input read.
Prospective bounds: one worker,1GiB RSS/512MiB native, export30s/synthetic60s/
conditional1024-row equivalence60s,≤180swhole including cleanup; exclusive new
artifact/evidence paths, no refit/calibration/test or timing campaign. Reuse only
the original prepared inputs if explicitly authorized; unsupported dependencies
stop before real access. No exports/dependencies/task0024code are created here.

The implemented manual entry point is:

```bash
.venv/bin/python -m latenttrigger.benchmarks.cpu_mps --run-campaign
```

It has no output/retry/fallback/override selector. **Do not run it again for this
allowance:** the device-proof path is consumed and the current final software
acceptance cannot turn the old failed proof into admission. A later device attempt
requires separate authorization and an explicit preserved-history/source/policy
revision; no readiness series is recommended.

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

Final Git review found the preserved Task0022staged CSV uses CRLF on91lines.
Default `git diff --cached --check` flags those pre-existing line endings; no
Task0022byte/index was normalized. Command-local
`git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --cached --check`
passes while retaining ordinary whitespace checks. Task0023 working diff and new
files pass whitespace validation. No persistent Git setting was changed.
