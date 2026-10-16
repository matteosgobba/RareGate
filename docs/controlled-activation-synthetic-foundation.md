# Controlled activation study: synthetic software foundation

Task0035,2026-10-12 Europe/Rome. Additive **synthetic-only** implementation of
[Task0034's design](controlled-follow-up-protocol.md), with zero operational
population/feature/score/membership/fingerprint reads, real fitting/calibration,
confirmation scoring or event acquisition. Task0032 remains complete; Task0033
remains accepted exploratory/result-informed; permanent exposureYES/YES/YES,
Task0025's failed performance campaign and particle192/192 deferral are preserved.
No Task0036 starts automatically.

The starting checkout was clean `main`/`origin/main`, empty index, HEAD
`f27ce613565fff4d5107b1699af485afb582edd3`, committed Task0034, memory1.29.
The [actual prompt](prompts/0035-controlled-activation-synthetic-foundation.md)
is a raw-byte copy of the human attachment; SHA256
`ba4442f42fc445f37905f5f34a4d737e040b63b0c2310d419cf2fa2717f5d2ec`.
This authorizes synthetic models/forwards/reconstruction/calibration/updates,
without authorizing scientific execution. [Handoff](handoffs/0035-controlled-activation-synthetic-foundation.md)
and [curated summary](../results/tables/final/task0035-controlled-activation-synthetic-summary.json)
record final validation and all real native attempts.

## Separate implementation boundary

[Research helpers](../src/raregate/research/controlled_activation/)
and [strict implementation configuration](../configs/research/controlled_activation_synthetic_v1.json)
are separate from historical AE/PCA validators and controllers. Six unchanged
Task0034 artifacts are raw-byte prerequisites: prompt, handoff, protocol, sidecar,
registry and summary. The sidecar remains `design_only`, with zero accepted
confirmation sources. New software acceptance accepts neither a model nor a source,
and issues no operational authorization.

The schema admits only nonlinear/linear arms, seeds1729/1730/1731, ordered eight
feature names, CPU FP32 input/forward, biased8→6→3→6→8 layers/155parameters,
linear latent/output and the two prescribed hidden activation locations.
PCA-three is disabled/unimplemented. Exact future recipe remains Adam0.001 with
the resolved/pinned Task0034 defaults, batch4096, max1000/patience15/min_delta0,
CPU1thread/0workers/deterministic. Installed Python/NumPy/Torch versions, Torch
build text and Adam source byte hash are checked; optimizer-default drift fails.

The fixed `tiny_two_epoch_v1` profile generates its own train17/selection13 /
calibration21 rows and aggregate fixtures127/131 rows, with two optimizer steps
per arm/seed. Its two-epoch termination is a software fixture, not a canonical
recipe or convergence result. No operational CLI, numerical adapter, downloader,
arbitrary profile override, real-model input or `ProcessedStore` construction exists.

## Pairing, selection and score properties

One ordered named FP32 initialization document per seed stores names/shapes/
finite raw little-endian bytes and hashes. Both arms load independent tensor
storage; mutating one cannot mutate the other or the initialization record.
Synthetic fresh nonlinear initialization/forward is checked against historical
`CompactAutoencoder`. Linear output matches the intended affine composition,
including a closed-form FP64 reference within FP32 rounding tolerance.

The indexed loader preserves the historical shared local CPU generator for
`RandomSampler` and `DataLoader`, including loader base-seed consumption and
epoch advancement. Only indices actually emitted are hashed, with batch/tail,
coverage/uniqueness/completion checks. No extra sampler pass, reseeding, full
second permutation or exported row order. Synthetic4097rows prove4096+1tail and
two-epoch equality to the historical stream for all three seeds. Pair acceptance
requires correct arms/seed/input identity/initial hashes and common completed
epoch hashes; later missing epochs from divergent stopping are reported.

Python/NumPy/Torch CPU RNG, deterministic/warn flags and thread state are restored
on success and exceptions. The research context seeds only Torch's CPU default
generator, avoiding changes to CUDA/MPS RNGs. Layers explicitly use CPU/FP32,
independent of caller default dtype. Native library thread/cache environment is
set before imports in fresh workers; process-global BLAS initialization is not
claimed reversible. No GPU initialization or physical-device proof is implied.

Own selection uses unchanged pure `EarlyStopping(15,0)`, strict improvement and
earliest ties. Complete sequential epochs/finite nonnegative losses are required.
Each selected checkpoint binds arm/seed/design/initialization/epoch and finite
parameter bytes; selected-state score hashes are verified after own restoration.
Missing/altered/incompatible checkpoints, incomplete training and restoration
failure reject. JSON raw-byte representation uses no pickle; a synthetic linear
artifact rejects through the unchanged historical artifact loader. Only owned
synthetic checkpoints are serialized/reloaded, with atomic durable publication.

Selection/scoring preserve parameter bytes; equal-event MSE includes incomplete
batches. SSE casts input and reconstruction to FP64 before subtraction, then
sums eight squares and requires finite nonnegative FP64 output. An adversarial
synthetic example distinguishes this from FP32 subtraction then casting.
Each restored model calibrates once using its own four `higher` quantiles and
strict `score > threshold`, primaryalpha0.001. Threshold identity binds restored
weights/arm/seed/design and owned fixture bytes. Ties, zero/equal scores and
quantile indices are tested. Wrong development roles fail before provider calls;
there is only an in-memory synthetic provider.

## Shared-event arithmetic and decision gates

Bit order is N1729,L1729,N1730,L1730,N1731,L1731. Streaming/chunk merging produces
64 nonnegative Python-integer counts. Boolean decisions, complete ordered candidate
coverage and source denominator are checked. For `K_i=sum_s(A_N−A_L)`, moments are
computed with exact integer sums and rational denominators:
`mean=sumK/(3N)` and `V=(N*sumK²−(sumK)²)/(9N(N−1))`.
This avoids integer overflow/cancellation and retains seed/model dependence;
six rates and three seed contrasts use the same N, never3N.

The [primary theorem](https://arxiv.org/pdf/0907.3740), Maurer–Pontil2009 theorem4,
is one-sided on[0,1]. Applying it to both directions at delta/2 and scaling by
range R gives the prescribed `ln(4/delta)` formula. Unbiased sample variance,
R2paired/R1rates, clipped display endpoints and **unclipped precision halfwidth**
are implemented. Constant observations retain positive width; N<2 is undefined /
inconclusive. Unsupported finite-precision bounds reject. Integer/rational reference
tests include all64patterns, fully correlated/opposing seeds and sparse counts up
to10^25; numerical tests do not establish statistical coverage.

Family allocation0.05 remains signal0.025/background contrast0.0125/six rates
0.0125/6. Wilson95% individual intervals and exact zero-rate upper bounds are
conditional descriptions, not a comparison test. No p-values, AUC/AP, ROC/PR or
subgroup computation. Inference assumes independent i.i.d. events conditional on
frozen models/thresholds and excludes calibration/training/simulation uncertainty.

All original numerical gates remain: six FPR bounds inside[0.00075,0.00125],
paired background upper≤0.0001, signal/background contrast halfwidth≤0.0001,
each rate halfwidth≤0.0002, practical nonlinear advantage lower>0.0002. Linear
advantage/equivalence/negative/inconclusive conditions are retained. Precedence
is nonlinear advantage→linear advantage→equivalence→no practical nonlinear
advantage→background stability failure→inconclusive, with separate Boolean flags
and all failed gates. Eight-ULP allowance only validates consistency of displayed
floating endpoints; **scientific gate comparisons have no tolerance**.

Missing source/model/pairing/threshold/lifecycle/i.i.d. eligibility blocks favorable
arithmetic. `actual_confirmation_claim` is always false in this foundation;
counterfactual gate fixtures confer no acceptance. The236843zero-variance floor
and all four Task0034 variance planning cases are reproduced. Tiny fixtures
remain inconclusive under the unchanged precision requirements.

## Native lifecycle and validation status

The numerical test path has no operational input flags. It creates a unique owned
fixture workspace, validates source/config/dependencies and a parent-owned grant,
denies operational/synced/model/numerical-file reads and network/subprocess actions
in the numerical worker. The temporary sleep assertion uses inspected Task0030
continuous timing/verification/release helpers; the guard adapter explicitly
narrows historical6GiB RSS to1GiB and total owned storage to128MiB. Task0033's
Torch-prohibiting boundary and256MiB storage helper are not reused.

Fixed limits:30s prerequisites,60s worker through exit/reaping (operation stops
at58s to reserve2s cleanup),15s finalization,120s whole;1GiB RSS/512MiB whole
native/128MiB parent;64MiB journal/1MiB text log/128MiB owned storage;12updates
maximum. WARN advisory/CRITICAL and invalid-primary veto; pressure unavailable
disclosed, RAM contextual. Display sleep allowed/no persistent settings change.
Body-complete is provisional until normal exit/reaping, source/output identities,
complete integer counters, restoration/pair checks, continuous/resource checks
and publication all pass. Failed attempts remain distinct and immutable.

Fresh focused/full/portable source validation, lint/format/dependencies and final
bounded native integration are detailed in the summary. Both complete suites run
in artifact-free isolated copies with the existing portable legacy-schema plugin;
data, checkpoints, model artifacts and accepted arrays are absent. New research
counter instrumentation covers helper model instances/forward calls+rows /
reconstruction/optimizer started-completed-inflight/calibrations in each pytest
process and native worker. Unrelated historical synthetic models are outside that
counter scope; globally zero model or optimizer work is not claimed.

Final source:189focused tests,1917full+1917portable pass, with219source/config /
test/design bindings and43installed distributions; lint/format(301Python files)
and dependencies pass. Each final pytest process records85new research model
instances,31forwards/reconstructions on8710rows,2started/completed updates /
0inflight and2synthetic calibrations. These are per-process instrumented-helper
counters, not a global count of unrelated historical synthetic tests or earlier
software-repair runs. All details/receipts/maps remain ignored.

The first native attempt stopped in prerequisites because sandboxed `/bin/ps`
was unavailable; assertion release was verified. Automatic review initially
misapplied Task0034's no-automatic-successor restriction, then approved after the
current human attachment/prompt identity and explicit Task0035 authorization were
verified. A second attempt exposed the `__main__` child-module dispatch issue,
exited/reaped before numerical work and released its assertion. The dispatch
literal and regression test were corrected; source versions/failed evidence remain
preserved. Final actual status/resources/counts are recorded below in the summary /
handoff, without converting failed attempts into scientific allowances.

There were **three actual native invocations**, all with assertion release verified.
The first two failed before numerical work,0updates. The final source is
`parent_accepted_synthetic`:12started/12completed/0inflight,9research model
instances,65forwards/reconstructions on2333rows and6own synthetic calibrations.
The three fresh historical reference instances/forwards on39rows are separately
recorded. Three seed pairs have two matching completed epochs each; all six
selected-state bytes/scores restore successfully. Tiny inference is inconclusive.

Final continuous durations: prerequisites0.083132s, dispatch through normal exit /
reap2.515030s, worker2.270242s, finalization0.084262s, whole2.683233s; overshoot0,
cleanup0.000094s. Observed worker RSS373604352bytes/native171622400bytes,
controller30064640bytes;102NORMAL pressure samples,0WARN/CRITICAL/unavailable.
Actual owned storage151885bytes at final measurement is below128MiB. Three active
assertion observations, owned helper terminated/reaped and absence confirmed;
display sleep permitted/no persistent power changes. Sampling is not continuous:
maximum query gap0.107453s and terminal unmonitored worker interval0.245562s are
disclosed. Optional global-RAM context is unavailable because worker subprocess
execution is prohibited; this does not veto primary accounting. No physical
suspension or synthetic-performance/real-training-time claim is made.

## Concrete next decision

The foundation makes the comparison reviewable. It does not implement or authorize
real-background fitting/calibration, acquire events, accept a confirmation source,
freeze operational models or establish scientific utility. First resolve source
adequacy through a separate metadata-only go/no-go brief: full-event coverage,
units/run lineage/independent generation, declared selected signal count, all-role
overlap audit prerequisites and precision/storage feasibility. The transported SR
route remains conditional and lacks a matched independent original topology pair.

A separate background-development task could implement a narrow role reader and
bounded six-fit/calibration controller, with new synthetic acceptance/source freeze
and explicit execution authorization. Acquisition and independent confirmation
remain separate scopes. If no source can meet the fixed requirements, fitting
should not be portrayed as useful confirmatory progress. No Task0036 launched.
