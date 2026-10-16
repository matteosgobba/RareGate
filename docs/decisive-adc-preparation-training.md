# Controlled ADC preparation, finite training and freeze — Task0061

2026-10-16 Europe/Rome. This task implements the preparation half of the
[immutable Task0060 protocol](decisive-scientific-experiment.md). The actual
[human prompt](prompts/0061-adc-preparation-training-freeze.md) authorizes only
the bounded ADC acquisition, structural preparation, training/selection,
background calibration and freeze. Final quality, final robustness and the real
CPU cost comparison require Task0062. No result is assessed against scientific
utility/retention/rate/cost gates here. Operational readiness remains false.

## Verified baseline and implementation boundary

Entry was clean `main` tracking `origin/main`, empty index, HEAD and local upstream
ref `d02e6a5f114e1979a5a5b5e8f11c84aba02eed41`, memory1.55. All four user-specified
Task0060 byte/SHA256 anchors match. No remote freshness, push or hosted CI proof
was inferred. The actual prompt and Italian handoff preceded implementation.

New code lives in `research/decisive_adc`, with schema2 models under
`artifacts/models/decisive-v2-adc/<arm>/<seed-or-fit>`. The old eight-input
model/PCA/ProcessedStore contracts and Task0060 FP32/cleanup corrections remain
unchanged. Help/import cannot acquire data or fit anything. Explicit phases require
a current generated-validation/code/config/prompt binding and an exclusive stage
intent. An incomplete phase prevents continuation; fit attempts cannot be replaced.

## Rules fixed before payload decisions

The execution sidecar is
[`decisive_adc_preparation_v2.json`](../configs/research/decisive_adc_preparation_v2.json).
It pins the existing immutable protocol, source definitions, stage order, absolute
layout derived from this checkout, acceptance constants, role names, resources,
schedule and denial of final evaluation. It does not alter Task0060 authorization.

The owned root is `data/decisive-v2-adc-task0061/`: raw partial/accepted files in
`raw`, physically distinct roles in `prepared/<role>`, private group SQLite,
scaler/manifests/calibration evidence in `private`, append-only events/exclusive
intents/results in `ledger`, numerical/build/process logs in `diagnostics`, source
snapshots in `snapshots`, and contained tests/cache/temp in their own directories.
All are ignored. Curated tables contain no events, membership IDs, arrays or tensors.

Quarantine denominator is **all source Particles rows**, before deduplication.
Each source and the pooled source total must have union-of-rule failure fraction
≤1%; rule-specific counts can overlap and are not summed as unique failed rows.
Duplicates are not quarantined. Cross-label groups stop preparation. Source labels
are background, A→4l, LQ→bτ; ambiguous cross-source content cannot be reassigned.

The publisher descriptor (pp3–4) supplies GeV/radian, slot/type and cut meanings.
Names/classes must decode consistently; no numeric axis inference or alternative
dataset resolver. MET eta is zero; nonnegative MET pT including zero is legitimate.
Visible objects have positive pT, class IDs in their declared slots, all-zero
type0 padding, sorted prefix/decreasing pT, |eta|<3/2.1/4 and pT thresholds3/3/15.
The fixed rounding allowance is implemented as pT≥cut−1e-5 GeV; the lepton filter
uses the same allowance at23 GeV and the strict eta limits. Nonfinite/shape/storage
contradictions fail validation. HDF external/soft/virtual storage and unapproved
filters are rejected before payload reads. Chunks have at most8192 rows.

Canonical bytes are `adc-exact-content-v2\0`, followed for classes1,2,3,4 by
little-endian FP64 `[class,count]` and lexicographically sorted FP64 pT/eta/wrapped-phi
triplets. Signed zero is normalized and type0 slots removed. SHA256 groups retain
the lowest source-row representative; identical content across labels stops fits.
SHA256 of UTF8 `adc-split-v2|1729|fingerprint_hex`, then fingerprint, fixes role
order. No near-duplicate or generation-independence proof follows.

Exactly200000/50000/1000000/1000000 background groups become train/selection/
calibration/final background; exactly40000 of each signal are final-only. Remaining
groups stay unused. Train-only FP64 mean/ddof0 std transforms the frozen12 features,
with std>1e-12 and a single FP32 cast. Final preparation is structural access,
not true blindness; no final distributions/losses/scores or model-based exclusions
are permitted. Role matrices and their hashes are sealed separately.

Training loaders and a supplementary Python open audit permit train/selection and
the fixed training-development subset only; calibration is a distinct later phase.
Explicit path checks protect native HDF opens, which Python audit hooks alone do
not sandbox. This is reproducible application enforcement, not an OS adversarial
security boundary. The v1 all-role store is never used.

## Finite numerical work and freeze rules

Seed order1729/1730/1731, compact then reference; PCA3 and regularized Mahalanobis
last. At most six neural and two analytical attempts. Isolated CPU FP32 factories,
local paired per-epoch sampler hashes, complete2048 tails, exact Adam options,
own selection minimum/strict ties/restore and artifact reload are checked. An
80-epoch cap is reported as a cap. Every attempted batch and completed update is
recorded; interrupted work remains incomplete rather than a fresh allowance.

After all fits are bound, each of eight streams scores only calibration at public
B32, padded final tail, FP64 SSE/quadratic score. Deployment uses `higher` quantiles
and strict `>` at.01/.001; one-based uncertainty brackets use the preregistered
.01/16 family allocation. Artificial-score tests independently check ties, endpoints
and the million-row rank constants. Calibration tails are not final FPR estimates.

Development is the first4096 hash-ordered training groups (first512 for symmetry).
The future CPU schedule, eight rotated blocks, B1/B32/B512 and two direct timer
boundaries are fixed in config/helpers; no real performance matrix runs here.
After cuts freeze, rotation.7/reflection checks on those512 training rows record
feature/score errors, margins and decision changes with unchanged tolerances.
The separate512 final-background rows remain Task0062 work.

The complete private manifest binds source/role/scaler, all eight model/history/
checkpoint identities, calibration cuts/rank endpoints, code/tests/config/prompt,
runtime builds/threads, schedule and statistics. The final-stage preflight recipe
verifies identities and requires fresh human Task0062 scope plus persisted
unblinding intent before any final scoring. This entrypoint has no evaluate phase.

## Resources, validation and actual outcome

The whole0061/0062 storage cap is8GiB, own numerical worker RSS4GiB, one active
worker, zero services. Initial pre-header reservations summed7486515200B;
the explicit revised phase-aware reservations below sum8044830464B. They include
retained sources/partials, role object/feature/
membership files, grouping/index/sort scratch, fixtures/failures, models/histories/
snapshots/receipts and Task0062 outputs. No per-phase storage reset occurs.

Task start is12:15:45 UTC. The4h clock includes implementation/relevant validation,
imports/reporting/finalization. Acquisition≤45min/≤20min per source including
attempts; preparation≤30min; fits≤20min each; cleanup reserve10s. Outer observation
covers supervisor reporting/exit/reap; inner observation covers the worker. Own-pid
RSS and logical owned-file bytes are sampled, lifetime worker RSS is recorded.
Sampling, native/unlinked scratch and OS cache behavior are limitations: no global
host survey, OS all-write guarantee, physical disk-use proof or favorable-scheduling
retry is claimed. Bounded allocations, explicit scratch reservations and retained
receipts supplement observation. Old caches/pilots/allowances are untouched.

## Execution evidence and explicit pre-fit corrections

Acquisition completed once:680426757 accepted/wire bytes in3 event requests,
zero redirects/retries,216.925784125s transport function,219.055715084s external
supervisor lifecycle including reporting/exit/reap. Every source passed streamed
and separate on-disk checks;3 current metadata bodies match the retained Task0060
metadata hashes. No additional source or blackbox was acquired.

| Source | Actual header rows | dtype | Local accepted SHA256 |
|---|---:|---|---|
| Background | 13451915 | float64 | `5f460bd3af441d98a7962a83f3964d9b5fea7f2163e35532066adc9a9696cfe5` |
| A→4l | 55969 | float64 | `a73701afedaf11a74b3755ddb8ce2a5e963f5784a1c2b49f738dd310ad18f75c` |
| LQ→bτ | 340544 | float64 | `7a636fc1e6801406aee17223c28ebdbf42ebd7c491f3f27f4861fcc30cd66884` |

The background count differs from the descriptor's4M expectation. Equality was
never a scientific acceptance criterion. The first preparation attempt nevertheless
failed before event decoding because this implementation introduced a5M header
admission bound. Bounded header-only diagnosis identified that defect and the
actual publisher descriptions `MET_class_1`, `Four_Ele_class_2`, `Four_Mu_class_3`,
`Ten_Jet_class_4`; their explicit IDs/meaning agree with the protocol. Coordinate
metadata are `Pt,Eta,Phi,Class`. The generic-only parser also needed correction.

These are implementation/resource amendments before the first decoded event row,
not relaxed physics cuts or a contradictory type/coordinate mapping. The new15M
finite header bound does not allocate the raw logical array. Bounded vectorized
class sorting produces exactly the original canonical bytes, checked against both
the single-event implementation and hand-encoded golden bytes. Preparation-v2
preserves the failed first intent/result and its empty SQLite database. Its
**cumulative30min clock still starts13:00:34.363160 UTC**, covering diagnosis,
implementation/revalidation, imports and finalization. It does not restart.

Revised reservations are explicit in the execution config:3.6GB retained grouping/
index,2.2GB roles,1GiB raw/partials,256MiB tests,128MiB model/history/snapshot/
receipt,256MiB future0062 score/timing reserve and500MB headroom; sum8044830464B.
During index construction≤1.8GiB transient sort scratch can use the not-yet-created
role reservation. The observed global8GiB cap remains unchanged. Original source
logical arrays would exceed8GB before other study storage, and are never expanded.

Validation1 was interrupted when the sandbox denied own-pid `ps`; the child was
terminated/waited, with no test reports and unknown work before termination.
Validation2/3 retained18/112 completed call passes before the ownership monitor
rejected pytest/intentional fixture aliases. Contained test-only links are now
never followed; real raw/prepared/model aliases remain forbidden. Validation4
passed162;5 passed163. Their bundles precede later explicit corrections.

The telemetry plugin initially looked up a package-qualified module, while pytest
loaded the basename. Its scalar TALLY output was missing; numerical assertions and
incremental node/stage reports remained intact. The two lookup corrections were
requalified together with the same group in validation6:163pass. Acquisition had
already completed and does not import this plugin; binding revision2 preserves
revision1, source snapshots and that dependency assessment without an acquisition
repeat. The adapter/resource corrections above then passed **validation7:164pass
in7.14s**,7.697779708s external, with observed study694606513B and sampled worker
418414592B. Binding revision3 is
`807266df548528cc9594ee5eb1e4f6956694502cf171ef6f34fde0a0691bae70`.
No old source pass is substituted for this final-source result.

The final group includes the98 scientific-core expectations,20 audit regressions
and46 new ADC cases together. No shared historical source was changed, so costly
old complete matrices, physical MPS/ONNX/streaming and a3002-case repeat were not
needed. The ADC counters for validation7 record52 constructions,138 forwards/
2372 rows,66 toy Adam updates,68 public calls/2176 padded rows,128 retained
calibration scores, one complete generated6-neural/2-analytical matrix and two
additional analytical-oracle fits. Existing scientific-core toys are additional
and outside this ADC counter scope. Earlier test work remains positive; missing
early telemetry is not retroactively fabricated or replaced by the last run.

Necessary actual role/model/calibration/freeze outcomes are recorded below only
after their stages finish. Final quality and CPU outcomes remain protected.

## Accepted roles and original ADC work

All13848428 source rows passed every declared structural rule: zero quarantines,
zero cross-label conflicts. Exact grouping removes2761 duplicate background rows,
leaving13449154 background,55969 A and340544 LQ groups. The selected2330000 unique
groups are exactly200000 train,50000 selection,1000000 calibration,1000000 final
background and40000 per signal. Unused11199154/15969/300544 groups remain sealed;
they are not retry pools. The4096 development groups are a training subset.

Preparation-v2 took674.801706917s including supervisor reporting/exit/reap.
An independent post-preparation check rehashed role payloads and the closed group
database, recomputed hash ordering on2330000 private memberships, checked global
disjointness and the exact4096 training prefix. It passed. The complete cumulative
preparation campaign including first failure, diagnosis/amendments/checks and this
identity pass was1326.378265s, below1800s. Maximum recorded worker lifetime RSS
was901611520B; study storage after preparation was4740298083B.

Before the first real fit, the phase guard was strengthened to deny private
nontraining score arrays and all-role SQLite, including native `sqlite3.connect`
audit events. Calibration/group identities were explicitly included in the
manifest. A fresh coherent validation8 passed164cases in10.09s. Successful
preparation's numerical functions had identical ASTs; binding revision4,
`e12c417f9d9373c509b56065681d537b592be21d214decebb2966c3743071a95`,
qualified every real fit and the single calibration pass. No preparation replay.

| Model | Seed | Epochs | Selected epoch | Stop |
|---|---:|---:|---:|---|
| compactAE | 1729 | 80 | 80 | epoch cap |
| referenceAE | 1729 | 80 | 80 | epoch cap |
| compactAE | 1730 | 80 | 80 | epoch cap |
| referenceAE | 1730 | 80 | 78 | epoch cap |
| compactAE | 1731 | 80 | 80 | epoch cap |
| referenceAE | 1731 | 80 | 79 | epoch cap |
| PCA3 | fit | — | — | analytical complete |
| regularizedMahalanobis | fit | — | — | analytical complete |

Exactly six neural/two analytical attempts completed; all allowances are consumed,
no failed/incomplete fit and no replacement. Every AE has7840updates, for47040
updates/480epochs/96000000 training row presentations in total. Selection including
restoration is24300000 presentations of the same50000 groups. Epoch caps do **not**
prove convergence. All common-epoch sampler hashes match across architectures;
own selected-state restoration and serialized B32 repeat/reload checks pass. Full
checkpoint/state/history/source identities are in the
[eight-row model table](../results/tables/final/task0061-adc-model-freeze.csv).

One pass per stream scored1000000 calibration groups:8000000 retained scores,
250000 public B32 calls, no padded actual calibration rows. For all eight streams,
strict cuts accept9999 at.01 and999 at.001, with one tied score at each cutoff.
These are **calibration counts**, not final measured FPR. All16one-based uncertainty
brackets are [989658,990340] / [998890,999107], with endpoint values and conventions
in the [calibration table](../results/tables/final/task0061-adc-calibration.csv).
Thresholds never select a model or checkpoint.

Development reload/repeat scoring adds98304score rows/3072calls. Post-cut rotation
and reflection add16384rows/512calls on the fixed512training events; all16reports
have zero raw/scaled feature error, zero score error and zero decision changes.
No signal or final-background robustness rows were evaluated. All original public
scoring therefore totals8114688presentations/253584calls on1004096unique events
(1M calibration +4096 training-development), never that many independent samples.
HDF gather rereads are positive work but were not individually counted: their
actual-header upper bound is54204173rows, in addition to13848428structural scan
rows; native HDF decompression may touch larger chunks. Exactly2330000 selected
object/feature rows were prepared. No global zero or inflated independent N claim.

## Corrected immutable freeze and readiness

The first freeze's development checks completed successfully, but post-exit
verification found that its file map included `ledger/active.json`, correctly
removed by cleanup. This is a manifest/ownership accounting defect, **not a score
or parity defect**. Its ready flag is explicitly withdrawn in a dated private
record. Original `complete-freeze.json`, identity, receipts and source remain
preserved. They must never be used as the Task0062 preflight.

The finalization-only correction excludes the transient owner and writes a new
immutable **`data/decisive-v2-adc-task0061/private/complete-freeze-v2.json`**.
A generated regression creates a real active tracker, seals, removes it and
verifies every retained entry after cleanup. One coherent final validation9
passes164cases in9.73s (10.316724208s external). Current binding revision5 is
`162e61abaad164b3c15a2609016ca97c679af0669a7c7847ec0fd72f3e5e9ec2`.
All numerical/data/model/score/statistical files are byte-identical to the actual
fits/calibration bundle. No fit, calibration or development inference was repeated;
existing scientific evidence is reused only after its hashes match.

**Final manifest:**130765B, SHA256
`e425d1bc50c644caf7c3fad1f2317472e33eca68686022d4eac52bf04d804ce6`.
The independent post-cleanup reader verifies all184bound files (4791963942B
rehashed) and current code/config/test/prompt identities. No missing/mismatching
file or active worker remains. Sealing's external lifecycle is2.249062500s and
post-seal identity verification2.348140250s. Observed study storage is about4.825GB,
below8GiB; final curated/report bytes are included in later delivery accounting.

`completed_adc_preparation_training_and_freeze`; `ready_for_Task0062:true`,
`final_evaluation_performed:false`, `Task0062_started:false`, scientific usefulness
not evaluated, operational readiness false. See the
[custody table](../results/tables/final/task0061-adc-source-and-role-custody.csv) and
[full summary](../results/tables/final/task0061-adc-preparation-summary.json) for
actual attempts, identities, counters, limits and versioned corrections. Nine
generated invocations retain164unique observed nodes/1110completed main call
passes; validation1 has unreported early work. These are not nine independent
scientific confirmations or the single final164case acceptance result.

## Task0062 preflight and boundary

Use only the revision2 manifest and exact SHA above. In a fresh human-authorized
Task0062 scope, verify184file hashes, each bound source/config/test/prompt identity,
models/scaler/cuts/role manifests and resolved runtime/build/threads **before** any
final score access. Preserve the withdrawal of revision1. Persist exclusive
unblinding intent, then perform the predeclared once-only quality/uncertainty,
final robustness/bias and coherent CPU schedule. No acquisition, fit, checkpoint
choice, recalibration, threshold search, best seed, easier rate or unused-pool
retry is implied. A validity failure stops with preserved exposure.

Task0062 alone assesses primary.01 retention90%, utility≥.15 on both topologies,
achieved-rate comparability and directly measured joint CPU reduction25%;.001
stays secondary. A valid negative/simple-baseline or inconclusive result remains
acceptable. Current models are prepared, not demonstrated scientifically useful.
Generation independence and true blindness remain unestablished; ADC is a
lepton-prefiltered simulation with capped provided objects, not the old LHCO
representation or general detector deployment. No Task0062 is launched here.
