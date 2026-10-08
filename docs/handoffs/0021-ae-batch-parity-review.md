# Task0021 — Frozen AE Batch-Shape Numerical Parity Review

## Metadata

- Date: 2026-10-08; branch: `main`, upstream: `origin/main`.
- Verified base/HEAD: `dba4635dfad1f29a06a3b1fb6c138885620be83e`.
- Initial status: clean working tree and empty index; Task0020 committed.
- Scope: isolated numerical review, bounded synthetic study and one conditional
  AE-only diagnostic of the existing prepared1024 inputs. No performance timing.
- Final status: implemented/validated; one complete diagnostic, consumed/no retry.
- Initial validation/execution: pending. Task0020 remains failed/consumed;
  particle192/192 and canonical deferral remain unchanged.

## Objective and initial plan

Preserve historical source/artifact/receipt bytes; reconstruct the original
failure; preregister and test isolated review helpers; freeze source acceptance
before the separately authorized diagnostic; aggregate old-tolerance violations
without stopping numerical coverage. Record measured evidence, limits, an inactive
prospective recommendation, living-document updates and manual Git commands.

## Changes and files

Implemented only isolated `ae_parity_protocol.py`, `ae_parity_numerics.py` and
`ae_parity_review.py`, plus64 focused self-contained tests. The strict review-only
JSON binds the actual prompt, frozen AE/input/calibration and Task0020 lineage;
unknown keys/selectors/overrides fail. Standard-library controller, exclusive
single directory, one fresh worker, finite caps/deadlines and consumed-no-retry
semantics reuse unchanged low-level guard/thread/supervision helpers. New numeric
helpers aggregate all v1 violations with `passed:false`, trace existing modules,
check same-shape repeats/SSE/strict decisions, use one diagnostic FP64 copy and
restore/hash-check canonical FP32 state. No performance timer pairs or stores.

Added report/curated summary and Task0022 inactive implementation-ready brief;
updated README, memory revision1.14 and index. Development protocol now persists
the user's informative final-handoff preference. Only these13files are intended.
Task0020 historical handoff/report/source/protocol/acceptance/CSV/receipts remain
byte unchanged; index/living memory reconcile its later commit.

## Validation and source freeze

827full self-contained tests pass (8.13s),827portable tests pass (7.74s) with no
operational data or `.git`;64new focused cases. Ruff lint/format, dependency check
and CPU smoke pass. Full suite revalidates reused deadlines/crashes/interruption/
thread/guard/cleanup coverage; do not call the preserved historical763-test
acceptance newly generated. Current90-source map includes all original86entries
unchanged. New acceptance file SHA256:
`ada23775b6c8770b354d500d58e3db45e7c30caee90ea42ca39d69c5de2ae7d1`.
Protocol canonical SHA256:
`9ecf458708c68f1464ac396f924d2e8a619f5e5d10b9734bfb9984c1cd450d14`.

A pre-study metadata check initially blocked on the preserved5.5MiB PCA guard
journal versus a4MiB generic byte-hash cap. Before either slot/reservation or
numerical opening, only the isolated checker was corrected to16MiB and the
full/portable checks rerun. No old file changed. The fixed synthetic study then
completed once, followed by acceptance/source freeze, explicit metadata-only
prerequisite validation and the one real review. No executable repair after real
reservation, no real replay. Remaining review allowance0.

## Measured results and original failure

Original first failure1.989305019378662e−6 survives: idealFP64 RHS
1.9302345663309095e−6, executedFP32 RHS1.9302344753668876e−6.
Their difference9.0964e−14 does not change the outcome. No grid verdict
changes solely from promotion. Row7/channel5, previously inferred from prefix
counts, is now measured and exactly confirmed on identical input bytes/runtime
versions. Original eight same-shape/seven across-shape prefix checks remain the
limits of Task0020 evidence; new findings do not retroactively extend its receipt.

| Batch | New complete windows / rows | Max reconstruction error | Max public SSE error | v1 reconstruction / score violations | Four frozen decision mismatches |
| ---: | --- | ---: | ---: | --- | --- |
| 1 | 1024 / 1024 | 5.435943603515625e−5 | 2.0492837960617294e−4 | 295 / 12 | 0 / 0 / 0 / 0 |
| 8 | 128 / 1024 | 1.33514404296875e−5 | 1.1829054195189315e−4 | 211 / 4 | 0 / 0 / 0 / 0 |
| 32 | 32 / 1024 | 1.33514404296875e−5 | 1.1829054195189315e−4 | 211 / 4 | 0 / 0 / 0 / 0 |
| 128 | 8 / 1024 | 1.33514404296875e−5 | 1.1829054195189315e−4 | 211 / 4 | 0 / 0 / 0 / 0 |
| 1024 | 1 / 1024 | 0 | 0 | 0 / 0 | 0 / 0 / 0 / 0 |

Every same-shape reconstruction/SSE repeat and restored full reference is byte
exact. First divergence is the initial Linear layer for nonreference batches;
all observed affine/ReLU positive-sign comparisons unchanged. FP32 shape-related
roundoff is supported, specific native kernel/reduction causality unverified.
Both NumPy and PyTorch build report Accelerate; Torch also enables Eigen BLAS.
No attribution based solely on NumPy backend. Full1024 FP32-vs-diagnostic-FP64
max error2.464197578255778e−5; FP64 is rounded diagnostic arithmetic, not a new
canonical artifact or exact truth.

Four fixed synthetic families complete all five batches/1193windows each,
81920forward row presentations (77824FP32+4096FP64);0real numeric reads.
They reproduce shape differences/v1 violations, with zero strict decision
mismatches and exact same-shape repeats. No recipe/seed/domain search.

Real analysis reads the existing prepared array once:1024unique reused rows,
19456FP32+1024diagnostic FP64 forward presentations,20480total;1193windows and
5120grid row comparisons. No new population request/store custody/optimizer/
performance invocation. Parameter/input/threshold hashes equal original AE1 and
pre/post; every full-reference hash restored. Metadata/file-byte hashes are
separate from a numerical array load. Per-event arrays remain bounded RAM only;
raw locations/examples/guard/audit records ignored, no event IDs/labels persisted.

Real worker2.557518750007148s/whole review2.9118584580137394s,
RSS358645760bytes=342.03125MiB/native180011008bytes=171.671875MiB,
parent27852800bytes=26.5625MiB. One child reaped/watcher closed,4833guard checks
including37periodic; pressure unknown/errno1, optional context2.911148/
2.914841GiB without admission floor. Synthetic worker4.173175957999774s,
whole4.537188542002696s/RSS327.609375MiB/native179.671875MiB. All fixed
process/deadline caps passed. These wall measurements enforce resource budgets;
no inference-performance timing. Shared normal Mac use retained.

Reference threshold margins0.00933623417/0.00408397869/0.160126684/
3.752131356; maximum eventwise score-change/margin ratio0.00161806388.
Computed SSE propagation identity differs from canonical score subtraction by
≤2.831068712794149e−15. Explain rounding and conservative envelopes; no universal
or calibrated/test FPR guarantee follows from sample agreement.

## Decision, compatibility and follow-up

Recommend route2: separately version an arithmetic-aware numerical contract,
then separately authorize **Task0022 — Arithmetic-Aware Frozen CPU Benchmark v2**.
The report's concrete brief defines layer gamma-roundoff envelopes with explicit
FP64 reference/evaluation rounding, propagated SSE bounds, byte-exact same-shape
repeats/original same-shape SSE1e−12, finite/hash checks and zero strict sampled
frozen decisions. Bound assumptions/local affine arithmetic must be validated;
unsupported assumptions block, never enlarge to pass. PCA1e−12 unchanged.
This proposal is inactive here; v1 still blocked. No demonstrated forward/slicing
bug justifies a correction/replay account. Historical Task0020 remains failed and
consumed15/90cells/3000timings, not accepted or combined into future repetitions.

Task0022 brief preserves all scientific identities, precision/backend/threads/
input/grid/thresholds, defines independent six workers/90cells/18000timings and
bounded separate slot/source acceptance/finite failure handling. MPS requires a
complete accepted CPU reference and separate verified availability/parity.
No benchmarkv2 implementation, policy activation, performance campaign, model
conversion/export/quantization or test evaluation in Task0021. Particle192/192,
remaining0 and canonical deferral under unchanged contracts remain intact.

## Issues, limitations and evidence

Specific native kernel/reduction order, exact arithmetic truth, universal bounds,
real input range (not separately logged), calibration/test equivalence, complete
CPU frontier/AE timing and hosted CI are unverified. Current runtime versions
match original AE1; same-shape repeatability is an observation for this runtime.
Sampled resource guards are finite engineering protection, not hard real-time
stopping or guaranteed global headroom. Hardware native sysctl unavailable;
M5/16GB/core descriptor remain historical Task0020 metadata. Separate bounded
post-review context records current arm64/macOS26.6.2, shared load/AC power;
thermal queries return errors despite exit0 and remain unknown.

Ignored evidence: `data/task0021-validation/`, new acceptance,
`data/task0021-synthetic-study/`, fixed real review directory with reservation,
acceptance mirror, protocol copy, access/guard/partial/numerical receipt/workflow/
worker log. No replacement input/model artifacts. Curated summary links/hash
lineage; real receipt SHA256
`45a910dda6291a396135da6314189900b8efff7d971abdc02eace4cf3e7f5560`.
Final metadata-only validation record is
`data/task0021-validation/final-validation.json`; no additional numerical read.

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

## Git

No staging/commit/push performed. Clean original base, Task0020 prerequisite
already committed, only13Task0021files intended. No resulting commit invented.

```bash
git status --short --branch
git diff --stat
git diff
git diff --cached --stat
git diff --cached
git ls-files --others --exclude-standard
git add -- README.md docs/development.md docs/project-memory.md docs/handoffs/README.md docs/prompts/0021-ae-batch-parity-review.md docs/handoffs/0021-ae-batch-parity-review.md docs/ae-batch-parity-review.md configs/benchmarks/ae_batch_parity_review_v1.json src/latenttrigger/benchmarks/ae_parity_protocol.py src/latenttrigger/benchmarks/ae_parity_numerics.py src/latenttrigger/benchmarks/ae_parity_review.py tests/test_ae_batch_parity_review.py results/tables/final/task0021-ae-batch-parity-review-summary.json
git diff --cached --stat
git diff --cached
git diff --cached --check
git commit -m "feat: add AE parity review and document batch-shape drift"
git push origin main
```
