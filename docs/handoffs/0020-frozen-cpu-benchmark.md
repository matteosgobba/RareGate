# Task0020 — Frozen PCA/AE CPU Inference Benchmark Foundation

## Metadata and initial handoff

- Date: 2026-10-08, Europe/Rome.
- Initial status: implementation/validation/prerequisite checks pending; no campaign reserved.
- Verified HEAD/base: `c3008d43ddd6ec8aed5999056dc140faba33d84a`.
- Branch/upstream: `main` / `origin/main`; initial worktree/index clean.
- Task0019 has been committed since planning inspection; confirm the actual commit and preserve its original records.
- Prompt: [actual specification](../prompts/0020-frozen-cpu-benchmark.md), saved before substantive work.
- Scope: implement benchmark-specific CPU guards/controller/workers and self-contained tests, freeze new acceptance, then one conditionally authorized campaign on frozen PCA/AE v2 and1024dev-training aggregate inputs.
- No fitting/optimizer/checkpoint/calibration/particle/MPS/export/quantization/test execution. Particle192/192 and canonical anchor unchanged.
- Pending: prerequisite snapshot/identity checks, exact protocol, synthetic/full/portable validation, one campaign outcome, documentation/curation, link/identity/diff/exclusion review.
- No automatic stage/commit/push; hosted CI/remote delivery unverified.

## Final outcome

**Implementation validated; one conditional real campaign partial/failed and
consumed.** Preparation/PCA1 completed; AE1 failed the unchanged across-batch FP32
reconstruction tolerance before timing.15of90 cells/3000timings/300warm-ups;
75missing. No retry, executable repair after reservation, tolerance/threshold/
sample/precision/grid change or complete two-model/three-worker claim.

## Inspection and preserved prerequisites

Read development protocol/living memory and complete Task0019 brief/curated
summary before implementation. No applicable repository/ancestor AGENTS.md found.
Initial worktree/index clean, main→origin/main, actual HEAD/base
`c3008d43ddd6ec8aed5999056dc140faba33d84a`. Task0019's seven files are already
committed at that base, after5da9094. The planning snapshot was historical.
Current index/memory confirm its commit; original Task0019 prompt/handoff/report/
summary remain unchanged. No combined uncommitted-prerequisite Git sequence or
staging helper is needed. Remote push/hosted CI not established.

Initial409 small tracked/engineering entries hashed, three overlapping current
documents copied under ignored `data/task0020-snapshots/`. Initial state is
`data/task0020-initial-state.json`. Preserve406 entries outside README/memory/index,
including all scientific configurations/artifacts, particle source/acceptance/
slots/receipts, and historical Task0019 records. No synced source edit or unrelated
work. Small-file verification initially; one fresh full **dev** constructor
verification only in the authorized campaign, no raw/full-store payload replay.

## Implementation and files

New strict [protocol](../../configs/benchmarks/frozen_cpu_v1.json) binds actual
prompt/Task0019 brief, file-byte versus scientific/canonical identities, frozen
models/scalers/split/dev input/calibration, fixed timing semantics, caps, current
source acceptance and one exclusive output. Unknown keys/overrides/selectors,
duplicate/nonfinite JSON, truth/test/full-store roles are rejected before data.
PCA's original fitting validator and every canonical source/config remain intact.

Seven benchmark modules under `src/latenttrigger/benchmarks/`: package initializer,
stdlib protocol/metadata/acceptance/statistics, stdlib controller, own-process
guard, guarded worker, numerical/timing boundaries and public Accelerate thread
control. Low-level unchanged DarwinBindings/parser are reused; no particle
policy/controller/slot is invoked. Canonical PCA/AE artifact loaders/math are
unchanged; no dependency or CI modification. New self-contained synthetic tests
are in `tests/test_frozen_cpu_benchmark.py`.

Deliverables: [report](../frozen-cpu-benchmark.md),
[curated partial summary](../../results/tables/final/task0020-frozen-cpu-benchmark-summary.json)
and [90-row cell CSV](../../results/tables/final/task0020-frozen-cpu-benchmark-cells.csv).
CSV includes15 measured cells and75 missing statuses. README/memory1.13/index
update current implementation/partial execution/next dependency in place.
Actual prompt and this initial/final handoff belong with the work.

## Protocol and technical decisions

CPU eager NumPy/PyTorch; intra-op1/inter-op1/effective BLAS/OpenMP1, five thread
variables set before imports. PCA FP64 reconstruction, AE155FP32 parameters and
8→6→3→6→8 forward, both SSE FP64 casts **before** subtraction, strict frozen
threshold comparisons. Frozen model scientific hashes, artifact/config/results
byte/content identities and full-training provenance are verified independently
by workers; no refitting/scaling twice/recalibration/checkpoint work. AE v1 intact.

One preparation worker fully verifies the small dev store, then exactly one
public iter_features batch1024 of first source-ordered dev train background,
without labels/test/private memmap/all-population loader. Explicit iterator/store
close; persist bounded FP32 input and ID/provenance hashes only. Same inputs for
all model workers; IDs never enter tensors. Audited custody separate from one
population request. No full-store/raw constructor/hash/new model artifact.

Grid1/8/32/128/1024; workersPCA1,AE1,PCA2,AE2,PCA3,AE3; ascending batches, scopes
prepared reconstruction→precomputed actual-batch reconstruction SSE/decision→
existing public adapter/decision.20warm-ups then200timings per cell, independently
reset deterministic windows; perf_counter_ns/CPU completion,200empty timer pairs
separately. Kernel allocations and inherent AE encode checks included in scope1;
loading/preparation/logging/guard queries excluded. Score-only never uses a split
full1024 reconstruction as a different-batch same-shape target. No adaptive timing,
best run, overhead subtraction, operator replacement or sum-of-medians end-to-end.

Before/after references from canonical implementations on full1024 plus every
grid window; same-shape separated SSE1e−12/1e−12, PCA across-shape1e−12/1e−12,
AE across-shapeatol1e−6/rtol1e−5, zero frozen-threshold decision mismatches. Stable
relative denominator max(abs(reference),comparison_atol); elementwise acceptance.
Frozen input/parameter/threshold hashes before/after successful timing. Preserve
failed values/prefix checks; aborted AE postchecks not claimed.

Chosen finite caps: numerical worker1GiB lifetimeRSS/512MiB whole-native,
stdlib parent128MiB, one numeric worker; prep60s/six workers60s/aggregation30s
(450s allocated)/campaign600s, import/orchestration/cleanup inclusive.2s cleanup/
terminate-kill-reap slack. Fresh own-process/pressure at startup/phase and timed
boundaries,50ms-intent watcher; failed peaks/latches; unavailable/malformed primary
or provenance fails closed. NORMALpermit/WARNadvisory/CRITICALveto/unknowndisclosed
under finite caps. Optional global context start/end≤2s, no floor/age/stability
veto or polling. Watcher/GIL/OS interference/termination limits are disclosed.
RSS/native overlap; no machine-wide capacity guarantee or full-particle policy.

Atomic fixed directory creation reserves/consumes
`results/benchmarks/task0020-frozen-cpu/` before real data. Existing any-state output
blocks all real routes. Race loser never overwrites winner. Fresh workers bind
parent/token/source/protocol/prior receipts/artifacts. Failure after reservation
stops all dependent stages and spends the campaign even with zero work. No reset/
alternative output/overwrite/replay switch. Partial/crash receipts retain actual
flushed counts/lower bounds and cleanup facts.

## Validation and source freeze chronology

Focused fixtures initially exposed an incorrect synthetic deadline and a string
assertion (`np.float64(nan)`); corrected before final acceptance. Full757tests
passed before the six Accelerate cases, then final **763 pass8.14s** (93new).
Same763 pass8.05s in `/private/tmp/task0020-portable-j0uzkccn`, without operational
data or `.git`. Ruff lint/format152 files, pip dependency consistency, forced
CPU16smoke/PyTorch2.14.1 pass. No installed dependency changes; hosted CI unverified.

Initial data-free startup proof correctly failed effective threading because
NumPy uses Accelerate, not a BLAS pool exposed by threadpoolctl. Original failed
proof preserved separately. Installed SDK thread_api.h plus Apple primary docs
verify public BLASSetThreading(unsigned enum)/BLASGetThreading thread-local ABI,
single mode1/macOS15+. New helper requires setter0/getter1 on computation owner,
rechecks mode/owner, restores old mode, blocks unsupported symbols/state. No BLAS
replacement/model change or environment-only threading inference.
Primary sources are linked in the report; ignored SDK hash evidence retained.

Final data-free benchmark startup/operation proof passes:336101376RSS/
184205312native bytes under fixed caps, actual PyTorch1+1/OpenMP1/Accelerate
mode1 proven,0real data/optimizer updates. All applicable source/test/script
helpers frozen as86 entries before real work. New acceptance file SHA256
`cc61e7c1f42777ca5ea40f5192fe8d39be57041d67f1218d5a332e578549297e`, mirrored
byte-for-byte inside the campaign directory. Full/portable logs/XML, footprint,
quality/runtime/SDK proof bind that acceptance. Old670 acceptance remains historical.

Commands actually performed: full pytest with new XML/log, portable full pytest,
Ruff check/format-check, pip check, explicitly forced CPU smoke; data-free guarded
synthetic footprint; metadata-only CLI prerequisites; **one** --run-campaign.
No full-suite rerun or new acceptance after execution was needed: only docs/curated
metadata changed, all86 accepted executable hashes remain identical.

## Actual campaign and failure evidence

Total7.989795207999123s; controller28049408bytes/26.75MiB RSS. Reached stages:

| Phase | Actual result | Whole worker seconds | PeakRSS bytes | Whole native bytes |
| --- | --- | ---: | ---: | ---: |
| prepare | Completed1024rows | 2.1435329579981044 | 363200512 | 188399616 |
| PCA1 | Completed15cells/3000timings | 3.45889399999578 | 306675712 | 180011008 |
| AE1 | Numerical failure before timing | 1.3852602919942 | 362086400 | 180011008 |

All reached guards pass, children reaped and owned watchers closed. Live pressure
unknown/errno1, not NORMAL or WARN. Optional context2.415329–2.570404GiB was not
admission. No app cleanup/closure/reboot/swap/cache/privilege/dedicated window/poll.

Actual counts15/90cells,3000/18000timings,300/1800warm-ups,200/1200empty pairs.
PCA2/AE2/PCA3/AE3 never dispatched; AE1has zero timing cells. Full shared input
references are in-memory/hash records, no per-event score output. One dev custody
and one population request1024rows/1024unique. Timing715800+71580warm-up input
presentations reuse those rows; numerical/preparation forward checks47128.
New real optimizer updates0; no model/threshold/calibration/test artifact change.

AE1 fails `reconstruction_across_batch`: actual−0.09302544593811035,
full1024reference−0.09302345663309097 at within-window[0,5], absolute error
1.989305019378662e−6/relative2.1384982792297272e−5, versus approximately
1.9302345663309095e−6 allowed at this reference. Eight prepared/same-shape SSE
windows and seven across-shape/decision windows precede the error, locating B1/
sample-relative row7/channel5 by **receipt/order inference**, not another array read.
Larger prior absolute errors can pass an elementwise relative tolerance.
All-grid AE score/decision parity and post-timing identity checks were not reached.
No assumption of safe decisions or AE timing; no scientific/convergence rejection.

PCA verifies every1024row/grid window pre/post with zero decision mismatches;
max absolute numeric error3.552713678800501e−15, full-reference hashes match.
All15single-worker latency distributions and defined B/mean throughput retained;
no three-worker estimate or complete model comparison.200samplep99/fixed order/
watchdog/shared-host limits explicit. Different reconstruction scales, dev rates
and compression/precision cannot establish discrimination or a trigger deadline.

Hardware native sysctl queries unavailable; separate filtered0.122624s metadata
capture reports MacBook Pro/Mac17,2/Apple M5/16 GB and CPU descriptor
`proc 10:4:6:0`. No serial/UUID retained. Architecture/macOS26.6.2 and actual
library/threadpool versions recorded. AC power80% battery/load averages captured.
Thermal command returned error0xe00002bc despite exit0: values unknown, not normal.
This metadata capture is outside the measured campaign, no numerical replay.

## Current decision and next dependency

Task0020 delivers validated implementation and honest partial evidence. Preserve
the consumed failed v1 and PCA1data. No code repair/real replay or tolerance/
threshold/sample/precision/grid change after reservation. Frozen PCA/AE v1/v2,
source/config/scalers/calibration and particle192/192/deferral/anchor remain intact.
No inference of available particle allowance from this separate benchmark.

The full-reference success prerequisite for CPU/MPS comparison is unmet. One
proposed next task: **Task0021 — Frozen AE Batch-Shape Numerical Parity Review**,
existing failed receipts/frozen source/small metadata plus bounded self-contained
synthetic analysis. Explicit compatible methodological decision and separate finite
authorization/guarded slot before any new real verification/replay. Preserve strict
thresholds and old failure; no automatic retolerance/refit/calibration/test access.
Do not implement Task0021 or MPS/export/quantization/simulator/unblinding here.

## Final validation and exclusions

Metadata-only final review recomputes JSON/scientific/file identities and original
receipt relationships, raw timing stats/counts, report/summary/CSV agreement,
all86 source hashes and initial406 preserved entries outside three live-doc edits.
Check relative links/anchors, whitespace, explicit17-file scope, empty index,
branch/upstream/HEAD and ignored operational outputs. Validation helper/records
stay ignored under `data/task0020-*`; no additional model scoring or array access.
Final factual output is `data/task0020-final-validation.json`.

Ignored: prerequisite snapshots/full+portable logs/XML/SDK/thread proof/current
acceptance; campaign reservation/protocol/acceptance/prepared input/ID hashes/
phase grants/bootstrap/access/resource/numerical/raw timing/receipt/workflow/logs.
No large scientific arrays, model artifacts, caches or unrelated edits in Git.
No staging, resulting Task0020 commit, push or hosted CI success is claimed.

```yaml
new_real_population_accesses: 1
new_dev_custody_operations: 1
unique_real_rows: 1024
population_presentations: 1024
new_optimizer_updates: 0
particle_remaining_granted_dev_updates: 0
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

## Manual Git delivery

Task0019 is already committed at the verified base; stage only these Task0020
files after review. No task-scope isolation claim based on uncommitted prerequisites.

```bash
git status --short --branch
git diff --stat
git diff
git diff --cached --stat
git diff --cached
git ls-files --others --exclude-standard
git add -- README.md docs/project-memory.md docs/handoffs/README.md docs/prompts/0020-frozen-cpu-benchmark.md docs/handoffs/0020-frozen-cpu-benchmark.md docs/frozen-cpu-benchmark.md configs/benchmarks/frozen_cpu_v1.json src/latenttrigger/benchmarks/__init__.py src/latenttrigger/benchmarks/protocol.py src/latenttrigger/benchmarks/guard.py src/latenttrigger/benchmarks/core.py src/latenttrigger/benchmarks/worker.py src/latenttrigger/benchmarks/frozen_cpu.py src/latenttrigger/benchmarks/accelerate_threads.py tests/test_frozen_cpu_benchmark.py results/tables/final/task0020-frozen-cpu-benchmark-summary.json results/tables/final/task0020-frozen-cpu-benchmark-cells.csv
git diff --cached --stat
git diff --cached
git diff --cached --check
git commit -m "feat: add guarded CPU benchmark and record AE parity failure"
git push origin main
```
