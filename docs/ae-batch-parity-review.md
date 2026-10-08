# Frozen AE batch-shape numerical parity review — Task0021

The isolated review is implemented, validated and complete. The single authorized
AE-only diagnostic reused the exact prepared1024 rows once. It confirms the
Task0020 failure and extends coverage to every window in all five batches.
Reconstructions **and scores fail the unchanged v1 tolerance**; all four frozen
strict decisions agree on this sample. Task0020 remains partial, failed and
consumed:15/90cells and3000/18000timings. No new performance measurement exists.

The recommended next route is a **separately versioned, arithmetic-aware CPU
numerical contract**, then a separately authorized complete CPU campaign in
Task0022. This is an inactive proposal. The active v1 full benchmark remains
blocked; no tolerance, canonical artifact, calibration or launch permission changed.

[Curated summary](../results/tables/final/task0021-ae-batch-parity-review-summary.json),
[review-only protocol](../configs/benchmarks/ae_batch_parity_review_v1.json),
[actual prompt](prompts/0021-ae-batch-parity-review.md) and
[handoff](handoffs/0021-ae-batch-parity-review.md) distinguish historical,
newly measured, inferred, proposed and unverified statements.

## State, history and frozen bindings

Initial Git state was clean `main` tracking `origin/main`, empty index, HEAD
`dba4635dfad1f29a06a3b1fb6c138885620be83e`: Task0020 is committed. Its historical
handoff retains task-time “awaiting commit” wording; only living documents
reconcile the later commit. Task0019's decision/brief and Task0020 report,
protocol, summary, CSV, accepted numerical/worker/thread/source and original
workflow/reservation/preparation/access/AE1 receipts were inspected. Original
Task0020 executable/protocol/acceptance/receipt/CSV bytes are preserved, including
all86 previously accepted source entries. New acceptance covers90 entries.

The model is still compact-autoencoder-v2,155 exact FP32 parameters,
8→6→3→6→8 with hidden ReLU and linear latent/output. It is loaded through the
existing `CompactAutoencoder.load`; v1/PCA/particle artifacts and source remain
unchanged. Config canonical SHA256 is
`0af02cba0dcab4cd750b19f6357fe5030aadb56c7c0422c4f35ea4adc1521800`;
model scientific SHA256 is
`6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b`;
calibration-result scientific SHA256 is
`324d7363b3e2d2ec96f57cc88790af99895097a35c91efe4839c3cead25c7d33`.
File-byte identities, which differ from scientific/canonical JSON hashes, are
listed separately in the protocol/summary and recomputed without population reads.
Full-training provenance and the frozen preprocessing/feature order remain bound.

The only numerical real input opened was
`results/benchmarks/task0020-frozen-cpu/prepare/input.npy`:32896file bytes,
FP32[1024,8], already standardized. File SHA256:
`7164bfd7a86a9561ae3abc7b44b396c1a60db0114fc8542443ad3f71d2990a5e`;
array C-order bytes SHA256:
`2ba0776aa1b5dfb7eb91dc0df4993d0a2ec52c83a79cc5424acc9b98a59b3d05`.
Rows are the previously prepared first1024 source-ordered dev-training aggregates
of all physical particles before truncation. No scaling, IDs, labels, truth,
processed/raw store constructor or population request enters this review.

Canonical scores cast input and reconstruction to FP64 **before** subtraction,
then square/sum eight residual channels. Higher scores are more anomalous.
Four unchanged thresholds, read from verified frozen result metadata, are:

| Target FPR | AE threshold; strict `score > threshold` |
| ---: | ---: |
| 0.1 | 3.478338537407165 |
| 0.05 | 4.681070974717348 |
| 0.01 | 8.324174660133213 |
| 0.001 | 16.642218868621573 |

No calibration inputs were reopened. These are historical calibration thresholds,
not newly measured dev FPRs.

## Reconstructing the historical failure

Task0020's `reconstruction_across_batch` first failure was within-window[0,5],
actual−0.09302544593811035 versus reference−0.09302345663309097,
absolute error1.989305019378662e−6. Ideal FP64 arithmetic gives
`1e-6+1e-5*abs(reference)=1.9302345663309095e−6`;
excess5.907045304775261e−8, or3.0602732993%.

The original comparator casts both arrays to FP64 when computing error, but its
RHS retains a FP32 reference array. Actual NumPy2.5.3 promotion executes the RHS
in FP32:1.9302344753668876e−6, lower by9.0964e−14.
Both calculations fail. This small dtype effect did **not** cause the failure;
changing promotion alone would not repair it. Across the complete real review,
no verdict changed between executed and ideal bounds. The largest RHS rounding
difference across reconstruction channels was1.5901401641824423e−11.

The original prefix contained eight byte-exact same-shape reconstruction/SSE
windows and seven across-shape score/decision windows with zero threshold
mismatches. It had no AE timing or post-timing checks. Its prior passing windows
already reached3.814697265625e−6 absolute reconstruction error: relative bounds
vary by channel, so1.989305e−6 was never an all1024 maximum.

Row7/channel5 was originally **inferred** from loop order and prefix counts.
The separately authorized review now **measures and confirms** that coordinate
with exactly the recorded values on identical input bytes. Versions and effective
thread settings match the original AE1; process/thread IDs naturally differ.
No reference-slicing, parameter-mutation or forward-bookkeeping defect was
demonstrated. The old verifier and its stop-on-first-failure behavior are unchanged.

## Execution mechanism and diagnostic methods

PyTorch explicitly documents that corresponding batched and sliced computations
need not match bitwise, because operation/reduction order affects floating-point
results. [PyTorch numerical accuracy](https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html).
Deterministic algorithms govern repeated execution, while shape changes describe
a different operation instance. [PyTorch reproducibility](https://docs.pytorch.org/docs/2.14/notes/randomness.html).
Repeatability, reconstruction closeness, SSE closeness and frozen decisions are
separate checks; none implies the others universally.

The unchanged runtime is CPU eager FP32 forward/FP64 score, eval/inference mode,
PyTorch intra/inter-op1, deterministic algorithms, and five environment variables
set to1 before imports. Effective OpenMP pools were queried, and public
Accelerate thread-local setter/getter verification reports single-thread mode.
Input shape/strides are[1024,8]/[32,4]bytes, contiguous FP32; ascending windows
are contiguous source-order slices with identical row contents.

NumPy's build reports Accelerate. Independently, the **actual PyTorch build**
reports `BLAS_INFO=accelerate`, `USE_EIGEN_FOR_BLAS=ON`, `USE_MKL=OFF`,
`USE_MKLDNN=OFF`, `USE_OPENMP=ON`; CPU addmm registration was recorded through
read-only dispatcher inspection. These do not identify the executed native kernel
or reduction sequence for each shape. **GEMV/GEMM attribution is unverified**;
no backend switch, tuning or operator replacement was used.

Review helpers install temporary read-only hooks on the existing four Linear and
two ReLU modules, remove them in `finally`, and compare layer traces against the
full1024 canonical reference. Each window has a traced canonical forward, a
plain repeated canonical forward and public canonical `score`. Actual-batch
reconstructions are concatenated in bounded memory; separated FP64 SSE is then
computed on that concatenation and compared with all public actual-B scores.
Thus it uses the correct reconstruction for each batch, and obtains exact score
agreement; it does not substitute slices of the full-reference reconstruction.

A diagnostic FP64 copy converts the exact stored155 FP32 values and invokes its
same encoder/decoder layers, bypassing only the canonical FP32 input validator
for that expressly permitted comparison. It is not serialized, canonical or
exact real-arithmetic truth. Full1024 canonical reconstruction/score references
and parameter/input/threshold hashes are rechecked after the grid, byte-exact.
No per-event arrays or scores are persisted; raw aggregates contain all bounded
violation coordinates, mask hashes and at most eight discrepancy examples per
comparison. This study contains no latency timer pairs.

## Preregistered synthetic study and validation

Before the single study, the strict protocol fixed four1024×8 families:
256-row constant blocks0,+1,−1,+8; signed powers2^−3…2^3 with the recorded
row/channel formula; independent `default_rng(1729)` uniform[-8,8]; independent
seed1729 standard normal clipped[-8,8]. Recipes and hashes are in the summary.
There was no seed/domain search. All1193windows per family were reviewed on
batches1/8/32/128/1024 in one fresh guarded worker.

| Synthetic family | B1 max reconstruction error | B1 max SSE error | Reconstruction violations B1 / B8 / B32 / B128 / B1024 |
| --- | ---: | ---: | --- |
| Constants | 5.0067901611e−6 | 2.0894862871e−5 | 256 / 256 / 256 / 256 / 0 |
| Powers | 3.3140182495e−5 | 1.4510675123e−4 | 657 / 438 / 438 / 438 / 0 |
| Uniform | 1.1038780212e−4 | 1.6994593475e−3 | 589 / 427 / 427 / 427 / 0 |
| Normal | 1.5676021576e−5 | 3.7264889473e−5 | 359 / 286 / 286 / 286 / 0 |

Uniform B1 has three v1 score violations; the other synthetic score comparisons
pass. Every family/grid has byte-exact same-shape reconstruction and score
repeats, zero frozen decision mismatches and zero observed ReLU sign changes.
First divergence in nonreference batches is `encoder.0`. Synthetic findings do
not enlarge the real sample or establish physical acceptance.

**827 full and827 portable self-contained tests pass**, including64 new focused
cases. The portable copy has no operational `data/`, ignored receipts or `.git`.
New tests cover strict protocol rejection, fixed recipes, full-grid bookkeeping,
legacy dtype behavior, all violation locations, finite output refusal, strict
threshold ties/adjacent representable values, cast-before-subtraction SSE, hook
cleanup, diagnostic-copy parameter preservation, one non-pickle array open,
unsafe/altered paths/size/hash rejection before opening, exclusive competing
reservations, consumed states, cap equality/exceedance and pressure semantics,
truthful incomplete summaries and stdlib controller imports. The rerun full suite
also exercises reused blocked-import/native-work deadlines, crashes,
interruptions, thread enforcement and child/watcher cleanup. Lint, format,
dependency and CPU smoke pass. Hosted CI is unverified.

One pre-study metadata check initially rejected the preserved5.5MiB PCA guard
journal under an overly general4MiB byte-hash cap. This occurred before any
study/review reservation or numerical array opening. The isolated checker was
corrected to a bounded16MiB file-byte cap; full/portable validation was rerun
before the sole study. Historical bytes did not change.

Current90-source acceptance, successful guarded study, evidence hashes and
runtime versions were frozen before real work. No executable repair or replay
occurred after real reservation. Old763-test acceptance remains historical.

## Complete newly measured real coverage

Each row below covers all1024 events. Violations count reconstructed channels
(out of8192) or event scores (out of1024), using the unchanged v1
`atol=1e−6,rtol=1e−5`. SSE here is the canonical public score; separated SSE
has identical values. Relative errors divide by `max(abs(reference),atol)`.

| B | Windows | Max reconstruction abs / relative error | Max SSE abs / relative error | v1 reconstruction / SSE violations | Four threshold mismatches | Same-shape repeats |
| ---: | ---: | --- | --- | --- | --- | --- |
| 1 | 1024 | 5.4359436035e−5 / 0.0111504975 | 2.0492837961e−4 / 4.49954884e−5 | 295 / 12 | 0 / 0 / 0 / 0 | Byte exact |
| 8 | 128 | 1.3351440430e−5 / 0.00507116822 | 1.1829054195e−4 / 1.78115006e−5 | 211 / 4 | 0 / 0 / 0 / 0 | Byte exact |
| 32 | 32 | 1.3351440430e−5 / 0.00507116822 | 1.1829054195e−4 / 1.78115006e−5 | 211 / 4 | 0 / 0 / 0 / 0 | Byte exact |
| 128 | 8 | 1.3351440430e−5 / 0.00507116822 | 1.1829054195e−4 / 1.78115006e−5 | 211 / 4 | 0 / 0 / 0 / 0 | Byte exact |
| 1024 | 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 / 0 / 0 | Byte exact |

All1193windows and5120grid row comparisons completed; violated comparisons
retain `passed:false`. Completing a diagnostic is **not** passing benchmark v1.
The identical statistics of B8/B32/B128 are observations, not a guarantee for
other shapes/platforms.

B1 first-affine maximum difference is1.9073486328125e−6 across3830elements;
latent max7.62939453125e−6; decoder preactivation max3.0517578125e−5;
output max5.435943603515625e−5. B8/32/128 also first differ in `encoder.0`.
Every recorded positive-versus-nonpositive sign comparison is unchanged, including
both hidden ReLU boundaries. Differences therefore arise before ReLU and propagate
through fixed affine operations. Cancellation in an output near zero can make an
output-relative tolerance stringent despite small local arithmetic errors.
This is a supported explanation, not a causal proof of the native kernel.

The full1024 FP32 reference differs from the rounded FP64 diagnostic by at most
2.464197578255778e−5; B1 by4.15249496810155e−5. The explanatory affine roundoff
model has maximum per-channel envelope0.0073772755269985064, and the largest
observed across-shape error/envelope-pair ratio is0.01021729353734415.
The envelope is conservative, assumes ordinary FP32 products/sums, and is **not
certified**. FP64 reference error and envelope-evaluation rounding are not
included in that measured explanatory ratio; a future acceptance implementation
must account for them explicitly. No alternative model precision was adopted.

## SSE propagation and frozen decisions

For `r=x−y_ref`, `d=y_actual−y_ref`, exact algebra gives
`ΔS=−2*r·d+sum(d²)` and `|ΔS|≤2*sum(|r*d|)+sum(d²)`.
B1 max algebra delta2.0492837960639498e−4, explanatory absolute bound
2.2576760144299435e−4; B8/32/128 bound1.1829099990862124e−4.
Difference between the computed algebra delta and subtracting canonical FP64
scores is at most2.831068712794149e−15. That rounding residue matters for a
rigorous inequality: the displayed bound is explanatory, not a certified
floating-point guarantee.

| Threshold | Minimum absolute full-reference score margin | B1 minimum actual margin |
| ---: | ---: | ---: |
| 3.478338537407165 | 0.009336234173192182 | 0.009335349596034881 |
| 4.681070974717348 | 0.004083978687090983 | 0.004084621937452404 |
| 8.324174660133213 | 0.16012668428443355 | 0.1601238970173604 |
| 16.642218868621573 | 3.752131356020776 | 3.7519680489471874 |

All actual margins, for every grid, are in the summary. The largest eventwise
score-change/reference-margin ratio is0.0016180638823867584. This sample has
room between scores and thresholds, explaining its unchanged decisions despite
v1 numerical failures. It does not show that future events near a threshold,
calibration FPR or test acceptance are unchanged. No calibration/selection/test
population was opened; no scientific-quality ranking follows from residual scales.

## Finite execution, resources and actual access

Both workers use the unchanged low-level guard/accounting/cleanup helpers with
fresh process checks before data and at operation/phase boundaries, plus50ms
periodic scheduling intent. Caps: worker1GiB RSS/512MiB whole native, parent128MiB;
worker60s including imports/cleanup, real review120s total,2s termination/reap
slack inside the budget. Parent remains free of numerical-framework imports and
covers blocked imports/native work. Process ceilings do not guarantee machine-wide
headroom or hard real-time stopping; OS/GIL/signal scheduling remains a limitation.

| Newly measured stage | Worker wall seconds | Whole controller wall seconds | Worker peak RSS bytes / MiB | Native reserved bytes / MiB |
| --- | ---: | ---: | --- | --- |
| Fixed four-family synthetic study | 4.173175957999774 | 4.537188542002696 | 343523328 / 327.609375 | 188399616 / 179.671875 |
| One real AE diagnostic | 2.557518750007148 | 2.9118584580137394 | 358645760 / 342.03125 | 180011008 / 171.671875 |

Real parent peak27852800bytes=26.5625MiB, dispatch2.8755632500106003s.
Import wall1.400132875001873s; real-family analysis wall0.5562434580060653s;
cleanup0.00043183400703128427s. These are resource/deadline accounting, **not
performance latency measurements**. Other loading/thread/orchestration work is
included in the whole-worker/review wall; it was not separately instrumented.
Do not infer kernel timing from analysis wall or subtract monitor work.

Real4833guard checks include37periodic checks, all pressure unknown/errno1;
NORMAL/WARN were not observed. WARN would be advisory, CRITICAL/malformed primary
accounting would latch a veto. Optional start/end available-memory context was
2.9111480712890625/2.9148406982421875GiB, never an admission floor or readiness
loop. Guard work may overlap diagnostics. Child reaped and owned watcher closed;
no failed peaks were hidden. No app content/closure, reboot, cache/swap operation,
privilege workaround or dedicated idle window was requested.

Runtime versions match AE1: Python3.12.12, NumPy2.5.3, PyTorch2.14.1,
scikit-learn1.9.1, SciPy1.18.1, threadpoolctl3.7.0. Current metadata confirms
arm64/macOS26.6.2; native hardware sysctl fields are unavailable in this sandbox.
Apple M5/16GB/core descriptor10:4:6:0 remains **historical Task0020 metadata**,
not a fresh hardware measurement. Supplementary bounded stdlib context is saved
separately after the review; thermal/power gaps stay explicit.

- Synthetic fixed study:77824 FP32 forward row presentations plus4096 diagnostic
  FP64 presentations,81920total,4096synthetic rows;0real numerical input loads.
- Real diagnostic: one `np.load(...,allow_pickle=False)` of the bound file;
  1024 unique reused rows;19456FP32 forward presentations plus1024diagnostic FP64,
  20480total. Repeated in-memory computation is distinct from population access.
- Bounded prepared-file byte hashing/metadata verification occurs before/after
  access and is **not** a numerical array open or fresh store custody replay.
- New processed/raw population requests0, new store custody operations0,
  optimizer updates0, performance timing invocations0. Real rows/IDs are not
  selected again; prepared inputs/arrays/models are not newly persisted.

Unit-test synthetic work is separate from the fixed study counts. Raw evidence,
acceptance, source snapshots, logs and diagnostic coordinate records stay ignored.
The exclusive Task0021 directory now consumes this review; no retry/alternate
output/reset/replay route exists. Task0020's reserved anchor and failed completed
workflow remain jointly interpreted as consumed. Particle192/192, remaining0,
local canonical deferral and all scientific/resource/time contracts are unchanged.

## Decision and inactive Task0022 implementation brief

| Route assessed | Evidence and consequence |
| --- | --- |
| Keep v1 and leave the complete benchmark blocked | Honest current status, but it treats output-relative closeness as a shape-invariant requirement not established by FP32 arithmetic; both synthetic and complete real checks violate it |
| Separately version an arithmetic-aware contract | **Recommended next route.** Distinguish per-shape repeatability, arithmetic-scaled reconstruction error, propagated FP64 SSE and exact sampled threshold decisions; retain canonical artifacts and old failures |
| Correct a demonstrated implementation defect | No such forward/slicing defect was demonstrated. FP32 RHS promotion is disclosed but explains neither the original nor the complete-grid failures; a bug-fix/replay story is unsupported |

This recommendation is an engineering compatibility decision for a frozen CPU
benchmark sample, not deployment equivalence, a scientific improvement or a
relaxation of particle/time contracts. The proposed criterion is derived from
layer arithmetic, not a multiple or rounding-up of the observed maximum.

**Task0022 — Arithmetic-Aware Frozen CPU Benchmark v2** should directly implement
and validate the new numerical gate and, only with separate explicit conditional
authorization, run one complete new CPU campaign. No standalone readiness task.
Concrete proposed prerequisites and protocol:

1. Keep PCA/AE v2 config/model/calibration scientific and file identities, frozen
   feature/scaler contract, prepared input bytes and all four strict thresholds.
   Reuse these1024prepared rows after byte/provenance validation; no new population,
   fitting, optimizer, checkpoint selection or calibration. Preserve AE v1/PCA/
   particle history and all v1 benchmark evidence. Verify live numbering.
2. Implement an isolated versioned numerical-policy source and new strict protocol
   and exclusive path `results/benchmarks/task0022-frozen-cpu-v2/`, with its own
   complete source acceptance. Nothing at that path is created by Task0021.
3. For AE let `u32=2^-24`, `u64=2^-53`, `gamma_m(u)=m*u/(1−m*u)`,
   `m=2*n+2` per affine layer (n=8,6,3,6). Starting `E0=0`, use fixed rounded
   FP64 diagnostic activations `h64` and
   `M_l=abs(W_l)*abs(h64_(l−1))+abs(b_l)` (matrix-vector sums).
   Propagate
   `E_l=(1+gamma_m(u32))*abs(W_l)*E_(l−1)
       +(gamma_m(u32)+gamma_m(u64))*M_l`.
   ReLU is1-Lipschitz, so propagates that envelope without multiplying it.
   Across two FP32 shapes require each channel `abs(y_B−y_1024)≤D=2*E_output`,
   with explicit outward/error accounting for FP64 bound evaluation. Include local
   affine diagnostic checks against FP64 operations on the same stored FP32
   layer inputs, and fail on violated assumed local rounding bounds. This is a
   conservative engineering criterion under ordinary FP32 product/sum semantics,
   no overflow; do not claim a universal backend certificate. Unsupported or
   unverifiable arithmetic assumptions block rather than enlarge the envelope.
4. Preserve actual canonical FP64 SSE and require separated/public same-shape
   `atol=rtol=1e−12`; require byte-exact same-shape repeats and restored reference
   hashes on the supported identical runtime. For across-shape SSE, use
   `Q=2*sum(abs(r)*D)+sum(D²)` plus explicitly derived FP64 subtraction, square,
   reduction and bound-evaluation roundoff. A proposed implementation can bound
   SSE evaluation error with `gamma_32(u64)` times both nonnegative score scales,
   accounting for input subtraction and all eight products/reduction steps;
   derive and test that allowance before freezing, do not use an unexplained
   decimal epsilon. Keep output checking, finite checks and zero decision
   mismatches on every1024row/grid pre/post. Strict ties remain rejected.
5. PCA retains1e−12/1e−12 reconstruction/score gate. No model/backend/precision/
   thread/grid change, AMP, compilation or tuning. Synthetic validation must test
   bound construction, cancellation, local affine roundoff, ReLU near-zero
   behavior, FP64 score propagation, ties/near-threshold mismatches, nonfinite/
   mutation refusal and same-batch score boundary. Use self-contained fixtures;
   ordinary tests must not require operational artifacts. Validate startup/operation
   footprint, source/identity refusal, guards and exclusive failure handling.
6. Preserve the existing three timing scopes and input-preparation exclusion,
   CPU1+1/effective BLAS1, batches[1,8,32,128,1024],20warm-ups/200invocations,
   fixed window schedule and timer context. New workers PCA1,AE1,PCA2,AE2,PCA3,AE3
   must yield their own90cells/18000timings/1800warm-ups and all three distributions.
   **Do not merge historical PCA1 into the new repetitions.** Kernel cost versus
   numerical-verification/FP64-diagnostic cost must remain separate.
7. Preregister finite1GiB RSS/512MiB native numerical workers,128MiB stdlib parent,
   preparation≤60s, six timing workers≤60s each, aggregation≤30s,450sallocated/
   600swhole wall,2scleanup slack; fresh/periodic primary guards and contextual
   pressure handling as Task0020. Validate, freeze, then atomically claim the one
   separately authorized campaign. Any failure consumes it, preserve partial
   values and stop dependent stages; no repair/replay or favorable-run selection.
8. Report all distributions, numerical diagnostics, sampled frozen decisions,
   imports/verification/loading/guard/cleanup/wall costs, thread/build/hardware/
   shared-host provenance and raw/curated exclusions. MPS comes only after a
   complete accepted CPU reference with separately verified availability/parity.

The measured Task0021 envelope omitted FP64 reference/evaluation rounding and
was explanatory. The proposed Task0022 formula expressly adds those obligations;
it has **not** been implemented or accepted here. Conservative envelopes can
permit more reconstruction drift than observed; strict sample decisions are an
independent requirement. No inference about calibration/test or future inputs.

## Delivery and evidence limits

The new standing delivery preference is persisted in [development.md](development.md):
final handoffs should explain work, key data, validation, limitations, decisions
and concrete next scope for the planning chat. Living memory references it.
Final review checks JSON/report agreement, original receipts/source/frozen byte
identities, local links, whitespace, actual Git scope and ignored outputs.
Hosted CI, precise native kernel, universal FP32 error guarantees, calibrated/test
acceptance and complete CPU performance remain unverified. No new Task0022 code,
policy activation, MPS, export, quantization or trigger simulation exists.

```yaml
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```
