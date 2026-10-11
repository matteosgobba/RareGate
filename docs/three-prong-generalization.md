# Frozen three-prong signal generalization — Task0028

**Phase A software accepted; explicitly authorized Phase B failed and consumed at
acquisition, with no retry/resume.** The sole campaign stopped at the frozen298s
operation deadline inside its300s stage cap, before raw integrity acceptance,
preparation or model evaluation. There are **no three-prong scientific results**.
Original Task0026/0027 native study remains completed, accepted and consumed;
its background/two-prong tests remain permanently exposed.

[Original specification](prompts/0028-three-prong-generalization.md),
[handoff](handoffs/0028-three-prong-generalization.md),
[strict protocol](../configs/evaluation/frozen_three_prong_v1.json),
[curated summary](../results/tables/final/task0028-three-prong-generalization-summary.json),
[phase outcomes](../results/tables/final/task0028-phase-outcomes.csv),
[actual Phase B authorization](prompts/0028-phase-b-authorization.md)
and [completed initial synthesis](scientific-synthesis.md).

## Actual Phase B outcome — 2026-10-11

The user approved exactly planSHA256
`77f92d951b034575299ed81d6cf61d19d49430b41b954d03b5d3ec62b1179fa9`.
Before the sole invocation, current protocol,139source/dependency files, acceptance,
candidates, transformations, calibrations, official source metadata and both
accepted background reference lineages agreed. The actual human message was
recorded in the prescribed audit and copied into the exclusive reservation. Live
main/origin/main HEAD was the actual Phase A commit
`e381f549225fa9e0960633a9a2093fa295bf39fe`, with initially clean index/worktree.
No Phase A continuation remained uncommitted; no push/hosted CI is inferred.

Acquisition began for the pinned235488994-byte v5 payload. The downloader logged
24117248 and47185920bytes transferred. The latter is a **lower bound**, not the
final transfer total or an accepted byte count. At the operation deadline it
raised `GuardError: Worker signal/deadline interruption.` and exited1; the parent
reaped it and rejected the stage. The workflow and root parent status are
`failed_consumed_no_retry`. No forced parent termination occurred; exit1 is a
failed worker exit, not normal successful termination. The300s stage includes a
2s cleanup allowance, leaving298s for the worker operation. Full campaign wall
was298.116751583s, within900s; this does not override the acquisition failure.

| Phase | Actual lifecycle / seconds | Outcome |
| --- | ---: | --- |
| Acquisition, startup/guards/network/cleanup included | 298.033886542 parent;297.972533500 worker | Failed, exit1/reaped/parent rejected |
| Integrity/overlap/feature preparation | Not started | Blocked by acquisition failure |
| PCA new-signal evaluation + cached background | Not started | No model request or cached numeric load |
| AE new-signal evaluation + cached background | Not started | No model request or cached numeric load |
| Campaign consolidation/reporting | Not started | No scientific outputs |

Interrupted acquisition body/network/integrity durations were not separately
recorded; do not substitute a fabricated body time. Worker cleanup was0.001298208s.
Offline metadata curation and this documentation are separate, untimed work; they
are not campaign consolidation or an inference benchmark.

Observed worker lifetime peakRSS41353216B=39.4375MiB, native reservation46137344B=
44MiB, controller peakRSS29868032B=28.484375MiB stayed below the frozen6GiB /
512MiB/128MiB envelopes.5494primary samples (5492periodic) all observed WARN,
which is advisory; CRITICAL/unknown0. No memory veto is recorded. Guard error is
the deadline interruption. Guard closure-to-parent-observed-exit gap0.020402125s
is unaccounted; sampled/lifetime accounting and overlapping RSS/native scopes do
not certify continuous memory or hard real time. The guard thread is closed.

The frozen acquisition routine automatically removed its own unsuccessful `.part`
in its existing `finally` block. No payload, partial file or acquisition manifest
remains, and the agent performed no deletion. The reservation, copied consent /
acceptance/protocol, grant, log, all guard samples, interrupted access record,
receipt, dispatch, parent rejection, exposure and workflow are preserved locally.
This documents a partial **access**, not a preserved complete/verified payload.

The durable raw-acquisition request still has `inflight=before_open`, expected
235488994bytes and confirmed-complete bytes0. That conservative state does not
mean no network transfer: logs prove partial transfer. It is retained as
`potential_inflight=true`, rather than cleared after failure. The worker has
exited and been reaped; there is no live child or model-scoring in-flight work.
All later phase records are empty. Raw numerical custody, original fingerprint
numerical access, feature preparation, model requests/scoring/batches and cached
background numerical reuse are all0. Optimizer/fitting/recalibration/selection /
export/benchmark/MPS/particle work and retry/resume are0.

## Scientific availability and retained reference

Payload integrity, local SHA256, actual HDF layout/count/labels/padding, within-source
uniqueness and all-role overlap are **unverified**. The published100000events remain
a source declaration, not a confirmed new population. No three-prong ROC-AUC/AP,
evaluated prevalence, frozen-threshold signal counts/efficiencies/Wilson intervals,
relative acceptance, selected fraction or tight-tail behavior can be reported.
Unavailable results are not zero rates. Expected39.9247817%prevalence remains
conditional count arithmetic; it was not evaluated on the new signal.

All four thresholds below remain frozen. The following historical references
are copied from accepted Task0026/0027 aggregates, **not Task0028 measurements**:

| Candidate | Two-prong ROC-AUC / AP | Three-prong ROC-AUC / AP |
| --- | --- | --- |
| PCA-v1 | 0.4684886579473786 / 0.36437915494963025 | Unavailable |
| Compact AE v2 | 0.6600638025267328 / 0.5474272683246686 | Unavailable |

The earlier evaluated mixture was150471background/100000two-prong signal,
prevalence0.3992478171125599. At the original target0.001, PCA accepted124background /
2signal; AE116background/56signal. AE's historical TPR0.00056 was below inherited
FPR116/150471=0.0007709126675572038: descriptive relative acceptance0.7264117241,
selected56/172=32.55813953% below initial39.92478171%. This establishes no observed
enrichment in that earlier selected slice. It says nothing measured about the
new signal. No three-prong-versus-two-prong comparison or new significance analysis
exists. Had the extension completed, the shared exposed background would still
make the comparisons dependent, without fresh background-generalization evidence.
AP/selected fractions depend on the evaluated mixture, not physical LHC rates /
purity. Conditional Wilson rate intervals exclude calibration/model/simulation
uncertainty; no unsupported ratio, AUC/AP or model-difference interval is added.

The initial observed AE advantage remains limited to the accepted two-prong
sample and frozen aggregate models, with higher accepted Task0022 CPU cost and
weak strict-tail utility. Different6vs3retained dimensions and reconstruction
residual magnitudes do not isolate nonlinearity. This acquisition failure supports
no new scientific claim and no mechanism for either model's signal behavior.

## Post-execution validation and next decision

Post-run source/acceptance/plan/reference checks agree; all139 frozen source /
dependency bytes and protocol are unchanged. Historical1333full/1333portable /
62new synthetic tests and toy integration remain the Phase A software acceptance,
not a passed real scientific campaign. No suite or native smoke was replayed;
read-only lint/format/dependency checks and metadata/documentation consistency /
relative-link/whitespace/Git exclusion checks are recorded in the handoff.

The complete initial scientific study remains accepted. Task0028 Phase B is
**failed/consumed**, not pending approval or resumable; Task0025 remains failed /
consumed with provisional ratios, particle192/192consumed and locally deferred.
One justified follow-up is an offline review of the transfer deadline and incomplete
payload evidence-retention policy, to design a prospective acquisition/custody
attempt. Any replacement would require a separate versioned protocol, source-bound
software acceptance, distinct namespace and explicit new human authorization. It
must preserve this failure and the original scientific contracts. No new campaign,
schema expansion, limit change, download, retry or next task is launched here.

## Question and scientific scope

How do the **same frozen native PCA-v1 and compact-autoencoder-v2** respond to
the reserved LHCO three-prong signal, using the accepted Task0026 background
scores and original calibrated thresholds?

This is a prospective signal-topology generalization study with a reused,
already-exposed background reference. It is not a fully independent signal /
background benchmark and does not test background domain shift. The two signal
studies share their background reference; comparisons are statistically dependent.
A separate file or generator description does not establish event independence.
No model/feature/threshold choice, fitting, optimizer update, recalibration,
export, runtime benchmark, MPS check or particle execution is part of this task.

## Primary-source facts and Phase A metadata provenance

The [version-specific Zenodo record](https://zenodo.org/records/6466204) describes
an additional 100000-event W′→XY signal with X,Y→qqq three-prong substructure,
with the same masses, trigger, generator configuration and detector simulation as
the original signal. The description records masses3.5TeV/500GeV/100GeV,
Pythia8/Delphes3.4.1, no pileup/MPI and a single R=1 fat-jet trigger at1.2TeV.
These are **publisher-declared facts**, not observations of the new payload.
The filename's `Z` substring is not used to infer the physics.

Freshly retrieved official [API metadata](https://zenodo.org/api/records/6466204)
on2026-10-11 confirm the following, agreeing with historical Task0002 metadata:

| Binding | Frozen value / verification scope |
| --- | --- |
| Record / version DOI | 6466204 / v5 / 10.5281/zenodo.6466204 |
| Particle file | `events_anomalydetection_Z_XY_qqq.h5` |
| Publisher size | 235488994 bytes, fresh API metadata |
| Publisher MD5 | `54e123a86143b668f9cb76905152a124`, fresh API metadata/record |
| Download URL | `https://zenodo.org/api/records/6466204/files/events_anomalydetection_Z_XY_qqq.h5/content` |
| Attribution/license | Gregor Kasieczka, Ben Nachman, David Shih; CC BY4.0, fresh API |
| Locally computed signal-payload SHA256 | **Absent**: acquisition interrupted before integrity acceptance |
| Confirmed payload count/layout/labels/units/padding/duplicates/overlap | **Unverified**: no custody/preparation phase started |

During Phase A, the web tool's API/card requests failed; a separately scoped metadata-only HTTPS
request succeeded after sandbox DNS restriction, fetching only9124-byte JSON,
2029-byte generator card and22436-byte detector card. That Phase A research requested no HDF payload, remote HDF
preview, feature file, black box or answer key; the later interrupted Phase B
payload request is recorded above. Metadata/card hashes
are pinned separately in the protocol/summary and retained locally ignored.

The official [three-prong Pythia card](https://zenodo.org/records/6466204/files/pythia_RnD_Z_XY_qqq.cmnd?download=1)
records13TeV beams, pTHatMin500GeV, MPI off, mass assignments3500/500/100GeV,
three-quark decay channels and the literal `NSEED` placeholder. It does not disclose
the seeds of individual released events or prove independence. Its
`Main:numberOfEvents=1000` setting is not a verification of the released sample
count; the protocol retains the publisher's100000 count as a custody requirement.
The official [Delphes card](https://zenodo.org/records/6466204/files/delphes_card_RnD.dat?download=1)
was inspected for its detector/reconstruction execution path, particle filtering
and jet-finder settings. Those configuration settings do not alone validate the
released event selection, layout or actual runtime versions. No new jet clustering
is introduced. Particle data are required because the published jet-feature view
cannot replace the frozen eight aggregates.

## Frozen scientific identities and isolated compatibility

PCA-v1 retains six centered, non-whitened FP64 components. Compact AE v2 retains
8→6→3→6→8,155 FP32 parameters, native CPU FP32 reconstruction and the frozen
background-selected state. Both retain eight-channel FP64 SSE, casting input and
reconstruction before subtraction, higher-score-is-more-anomalous orientation and
strict `score > threshold`, rejecting ties.

| Candidate | Model scientific SHA256 | Calibration scientific SHA256 |
| --- | --- | --- |
| PCA-v1 | `d09f96bb7b1536e8da147458f3b0bf50a120bdf6cfc4c247b37970f4f51bf42f` | `285a254847424870b5bee08e5a218733dcbe553ff7a4d00ec5c9493288600ccb` |
| Compact AE v2 | `6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b` | `324d7363b3e2d2ec96f57cc88790af99895097a35c91efe4839c3cead25c7d33` |

Config canonical hashes and config/model/calibration **file-byte** hashes are
separately bound in the protocol/summary, without replacing scientific hashes.
Original full-training scientific identity remains
`d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2`.
Frozen transform configuration byte SHA256 is
`2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68`;
canonical JSON SHA256 is
`4eae7a9f689ad8bd9faaa56f439e33540fddc586a8e9a51be96ea78dc52ec8ea`.

The unchanged [preprocessing contract](preprocessing-contract.md) and
[evaluation-v1](evaluation-protocol.md) remain authoritative. Feature order is
multiplicity, scalar_pt, max_pt, pt_balance, weighted_eta_mean, weighted_eta_std,
pt_concentration, massless_event_mass. Canonical physical normalization/sorting /
FP32 storage precedes all-particle FP64 aggregation and original log1p/scalers;
final model features are FP32. No truncation, fitted statistics, clipping,
new feature, precision change or score inversion is introduced.

| Nominal calibration FPR | Original PCA threshold | Original AE threshold |
| ---: | ---: | ---: |
| 0.1 | 0.3496768162794852 | 3.478338537407165 |
| 0.05 | 0.5642097175249418 | 4.681070974717348 |
| 0.01 | 1.4232146905138892 | 8.324174660133213 |
| 0.001 | 4.1356483360291865 | 16.642218868621573 |

The new signal artifact has its **own** raw source/actual SHA256/scientific identity,
with original training and transform references kept distinct. The isolated
compatibility contract requires exact transform/features/dtype, count/source,
passed overlap/custody and cached-background bindings. Original `run_final`,
validators, readers and model arithmetic remain byte unchanged. Original validators
apply to the genuine original training manifest, never a fabricated original-store
identity for the new signal. New-source compatibility is checked separately.

## Reused accepted background and its limits

Only the two accepted original background score files are permitted:

| Candidate | Accepted cached score path | SHA256 file bytes |
| --- | --- | --- |
| PCA | `results/evaluation/task0026-frozen-pca-ae/final/PCA/test_background-scores.npy` | `7e8762a1b675c637ed1533eab1b96686bc7ffd364666aea022a0f6e48766987d` |
| AE | `results/evaluation/task0026-frozen-pca-ae/final/AE/test_background-scores.npy` | `65711ecda105801c07855d9f6d8e4d5fa9264daac993b8ed10e362166c5efee3` |

Both are1203896-byte NPY1 files,128-byte bounded headers, little-endian FP64
shape[150471], original source order. Phase A verifies size/header/file bytes
and candidate/calibration/evaluation/audit/receipt/parent-acceptance lineage only.
**Zero numerical cached-score loads** occurred. Complete37-background-batch audit
(36×4096+3015),150471confirmed read/scored rows, supplied orientation and normal
exit/reaping are bound to each reference. Original raw/processed populations are
not reopened or rescored; missing/inconsistent references block execution, with
no reconstruction from quantiles or synthetic/forward fallback.

The explicit Phase B approval included conditional numerical reuse, one accepted
array per candidate; neither was reached. Its background FPR/conditional interval
would be inherited from the same
exposed finite sample, not fresh independent background evidence. Shared references
limit topology comparisons; this is no background domain-shift measurement.

## Preregistered HDF, integrity and overlap gates

The publisher describes compressed pandas HDF frames and massless (pT,eta,phi)
particles, zero-padded to700 slots. The appended truth column description pertains
to the original mixture; the three-prong payload's exact layout is unverified.

Supported subset: pandas **fixed**, one homogeneous FP64 numeric block at
`/df/block0_values`, exactly100000×2100 or100000×2101. Integer ordinal `axis0` /
`block0_items` must match complete column order; `axis1` must match source row
ordinals, checked chunkwise. Four exact datasets only; table/compound/mixed blocks,
alternate/dense layouts, wrong types/counts/columns, soft/external/virtual HDF links
are refused. Installed h5py/Blosc decoder is reused; no pandas/PyTables dependency
or unchecked reader. This supported subset is preregistered, **not** a claim that
the actual reserved file has that encoding. Unsupported layout consumes a reserved
failure and stops; no post-observation schema expansion/replay is authorized.

2100columns mean no label field: class is recorded from publisher signal-only
provenance, with its limits. With2101columns, last-column values must all equal1
and remain metadata. Units rely on declared GeV/eta/radian source provenance;
there is no empirical unit inference/rescaling. Nonfinite/negative pT, malformed /
nontrailing padding, empty events, bad labels/order or invalid aggregate arithmetic
refuse preparation. All valid particles enter aggregates before particle-view
truncation. No exclusions or favorable subset can rescue a failed gate.

Exact-content fingerprints reuse the unchanged algorithm: remove padding,
normalize signed zero/wrap out-of-range phi, canonical sorted source FP64 triplets
plus particle count, excluding labels/IDs. Require complete within-source uniqueness
and zero overlap with **all** original R&D roles. Original registry reference:
`data/processed/lhco-rd-v1/schema-v1/full/fingerprints.npy`,1100000×V32,
35200128bytes, previously accepted byte SHA256
`6de687560f3e2ab6a5704226eef18a35d87106c4a56799fba62e449316191067`.
Phase A checks its manifest reference/presence/size only; no fingerprint payload
opening or hashing. The actual Phase B approval included integrity-only byte/numerical inspection
of this registry, contingent on prior acquisition acceptance; that phase never
started. Exact checking would not prove absence of approximate duplicates.
Failed overlap/custody evidence is retained and prevents any candidate scoring.

## Minimal guarded execution and prospective budgets

The new stdlib controller has one numerical child at a time, fixed order:
acquire→prepare→PCA→AE→consolidate. It reuses validated supervision/guards and
scientific functions without invoking old consumed controllers. Each worker
independently checks source/protocol/dependencies/actual parent/token/approved plan,
consent copy and accepted predecessor output identities. Effective native threads /
build are pinned; ONNX/MPS are not execution paths of this study.

Fixed real namespace: `results/evaluation/task0028-three-prong/`.
Distinct raw/preparation namespace: `data/task0028-three-prong/`; raw file under
`raw/lhco/6466204/`, prepared features/fingerprints/manifest under`prepared/`.
Exclusive reservation precedes any real work. Existing/partial/foreign/failed /
completed namespace refuses retry/resume/alternate input, not a stale-lock cleanup.

Durable fsync access records distinguish raw acquisition/custody, original
fingerprint integrity, feature preparation, new signal model access and cached
background numerical reuse. Records precede network/open/read/scoring and retain
confirmed progress plus potential in-flight interruption. Model exposure is
recorded even if the first scoring request fails. A body is only
`body_complete_awaiting_exit`: parent acceptance additionally requires normalexit0,
reaping, deadlines, output/count/gate/source integrity and closed valid guards.
Timeout/forced termination/body-complete hang never becomes success; a failed
stage prevents all dependent work and consumes the reservation.

| Prospective phase / process scope | Fixed ceiling |
| --- | ---: |
| Acquisition and raw integrity, including startup/cleanup | 300s |
| Streaming custody/overlap/frozen preparation | 180s |
| Each native candidate, including cached reuse/metrics | 120s |
| Consolidation/reporting | 30s |
| Whole study, orchestration/imports/cleanup included | 900s |
| Terminate/kill/reap grace, inside stage caps | 2s |
| Numerical-worker observed lifetime RSS | 6GiB |
| Whole native reservation | 512MiB |
| Stdlib controller RSS | 128MiB |

750s stage caps leave150s whole-study orchestration slack. Raw processing uses
992-row chunks; a2101-wide FP64 chunk is16673536bytes. Full expanded HDF is never
loaded. Persistent new aggregates are3.2MB, new fingerprint payload3.2MB; original
registry payload35.2MB. These are bounded layout arithmetic, not measured real
future peaks. Acquisition/decompression/preprocessing/model-scoring wall scopes
remain separate and are not inference benchmarks.

Fresh primary guards surround phases/chunks/scoring, with50ms periodic sampling
intent and independent parent deadlines for blocked imports/native/network calls.
WARN advisory, CRITICAL veto, unavailable pressure disclosed; invalid primary
accounting blocks. Global availability is optional context without floor/idle wait.
RSS/native can overlap. Worker guard closure-to-exit gaps are recorded; GIL/OS /
scheduling/termination limits preclude continuous memory/hard-real-time guarantees.
All limits are prospective; no real payload/custody feasibility pass is claimed.

## Metrics and prospective access counts

Use unchanged evaluation-v1 ROC-AUC, supplied orientation, AP with actual counts /
prevalence, original calibrated thresholds/counts/TPR/achieved inherited FPR,
conditional Wilson intervals and finite zero-acceptance conventions. Attainable
empirical fixed-FPR/TPR cutoffs stay descriptive, without interpolation or adopted
thresholds. Relative acceptance=TPR/FPR and selected signal fraction=S/(S+B) are
labeled descriptive aggregate arithmetic. No ratio/model-difference uncertainty /
significance or physical purity/rate claim is introduced.

If custody confirms100000new signal events, canonical B4096 yields24full batches
plus1696tail,25batches per candidate:50new batches/200000signal presentations /
100000unique new events. Two accepted background arrays are loaded numerically,
with zero new original-background model population requests/forward calls.
Expected mixture prevalence is100000/250471=0.3992478171125599 **conditional on
confirmed counts**, not a new measured AP/result or physical LHC signal rate.
There is no signal development/tuning subset. Never select a model/threshold
from this extension or use original exposed tests as fresh evaluation.

## Historical Phase A validation and readiness

New code has its own full/portable/synthetic/source acceptance. Historical
Task0026's1259 and Task0027's12 tests are preserved, not treated as coverage of
new orchestration. New tests exercise toy HDF/model/feature/fingerprint/score
fixtures only, including physical/scaler compatibility, refused encodings,
source/checksum/count/type/identity failures, duplicates/cross-role overlap,
canonical FP64 SSE/strict comparisons,4096/1696tail, unchanged metric equivalence,
durable in-flight interruption, atomic reservation/consumed failure, failed-stage
propagation, body-complete hang and resource/deadline/cleanup/reaping behavior.
Actual installed NumPy/h5py/Blosc/PyTorch/sklearn run on synthetic inputs.

Actual validation: **1333 full and1333 portable tests passed**,62new cases;
repository lint/format(232files) and dependency checks passed. Protected native toy
integration exits0/reaped in1.997238s, observed378306560B RSS/184205312B native,
closed guard/no latch. Own139-source acceptance is separate from real custody.

Full/portable counts, scoped and repository quality checks, protected toy integration,
new source freeze and final plan digest are in the curated summary/handoff. The
portable tree excludes operational data/artifacts/sources/Git; existing narrow
three-schema synthetic plugin remains unchanged. No hosted CI/push is implied.

The readiness package verifies metadata/current source acceptance and cached
reference lineage; **real payload custody/compatibility remains conditional**.
At Phase A completion no consent audit existed and no real namespace was reserved.
The later human-approved Phase B above is now consumed. An authorization file,
CLI flag or synthetic readiness alone is not human consent.

The historical Phase A procedure required actual approval, recording the human
message and its source/acceptance/plan binding before invocation. Its plan command
is shown for provenance only; **do not execute it or rerun the consumed campaign**:

```bash
.venv/bin/python -m latenttrigger.evaluation.three_prong --prepare-plan
```

The exact approved-plan digest and subsequent guarded command are in the summary /
handoff. The Phase B authorization covered one pinned acquisition, integrity-only
raw/all-role original-fingerprint overlap audit, frozen preparation, one signal
evaluation per candidate and numerical reuse of both accepted background arrays,
with no subsequent test-guided fitting/recalibration/candidate/threshold selection.
All custody/compatibility gates must pass; interruption is still disclosed.

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
new_three_prong_signal model/evaluation accessed: NO
new_original_background_forward_calls_in_Task0028: 0
new_numeric_cached_background_score_loads_in_Phase_A: 0
new_numeric_cached_background_score_loads_in_Phase_B: 0
raw_acquisition_interrupted_in_Phase_B: YES
potential_inflight_raw_acquisition_record: YES
live_worker_or_model_scoring_inflight: NO
```

Original YES/YES preserves Task0026 exposure; new signal model NO reflects no
model request, despite the interrupted raw network access in Phase B. New signal
numerical custody/preparation/scoring, original-fingerprint numeric access and
cached-score numeric reuse remain0 in both phases. No new scientific metrics /
scores/figures exist. Particle192/192consumed/deferred and Task0025failed/consumed /
provisional ratios remain. The sole approved campaign is consumed; an offline
prospective policy review is the next decision, without automatic execution.
