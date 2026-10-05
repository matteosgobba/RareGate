# LHCO R&D preprocessing contract — version 1

Decisions frozen by Task 0004 on 2026-10-04; documentation finalized 2026-10-05
for Task 0005 implementation. This is an input
contract, not an implemented production pipeline. Measured evidence is in
[the EDA report](training-data-eda.md); exact fitted values and membership
fingerprints are in [configs/data/lhco_rnd_v5.json](../configs/data/lhco_rnd_v5.json).
That JSON is the numeric source of truth. Do not refit from validation/test or
copy rounded report values. Changes require a versioned rationale and handoff.

## Source and acceptance

Use only corrected `events_anomalydetection_v2.h5`, Zenodo v5 record 6466204,
DOI [10.5281/zenodo.6466204](https://doi.org/10.5281/zenodo.6466204), verified
size 2,908,260,409 bytes and MD5 `629789d55813be3860781b084ae7f1de`.
SHA-256 is also frozen in the JSON and split manifest. Read `/df/block0_values`
in bounded chunks; 700 `(pT,eta,phi)` triplets followed by truth column 2100.
Require finite values, pT>0 for every real particle, exactly zero trailing
padding, nonempty events and truth in {0,1}. Structural/conflicting-label failures
must be reported and block preprocessing until reviewed. Do not silently drop
them. Task 0004 found no violations and no duplicates.

## Canonical physical particle records

For event X={x_1,...,x_N}, real x_i=(pT_i [GeV], eta_i, phi_i [rad]). Strip
only exact zero-triplet padding. No categorical/object-type channel exists.
No masses, charges, jet identities or event-level trigger quantities are supplied.

- Store all real particles as FP32 `[N,3]`, exact channel order
  **`[pt_GeV, eta, phi_rad]`**. No truncation, padding, scaling, logs, or angular
  sine/cosine replacement in this physical record.
- Normalize signed zero. For phi outside `[-pi,pi)`, use
  `((phi+pi) mod (2*pi))-pi` in float64; preserve in-range angles exactly.
  Cast after wrapping. A rounded FP32 boundary can differ by one ULP; treat
  physical phi modulo 2*pi, not as a strictly ordered linear coordinate.
- Sort the full event using original float64 source values: descending pT,
  ascending eta, ascending wrapped phi, ascending original slot. This gives a
  deterministic leading-pT prefix. Preserve original slot indices as uint16
  provenance, never as model channels. Hash identity uses its separately
  documented ascending lexicographic order before precision conversion.
- Store primitive ragged NPY values plus int64 offsets, ordinal event IDs and
  original multiplicity. Identity is `(source SHA-256, raw row ordinal)`;
  duplicate-group fingerprint is separate provenance. Keep labels separately.
  Memory mapping and chunked construction must avoid loading the full source.
- Exact content groups have one lowest-ordinal representative; group/alias
  provenance remains available. Do not independently resplit aliases.

## Object model view

Produce FP32 `[384,4]` and boolean `[384]` mask on demand or in a separately
versioned cached view. Compute transforms in float64 from canonical physical
values; then cast once to FP32. Ordering is already established before casting.
For each real retained particle, channels in this exact order are:

1. `(log1p(pT / 1 GeV) - pt_mean) / pt_std`.
2. `(eta - eta_mean) / eta_std`.
3. `sin(wrapped phi)`.
4. `cos(wrapped phi)`.

Read scalers from JSON `preprocessing.object_view`. They are fitted on all
127,379,949 valid **training-background** particles, with equal particle weights,
in float64, population std (`ddof=0`), before truncation. pT mean/std here refer
to **log1p** pT. Eta is signed and nonperiodic. No clipping, winsorization, event
rotation, per-event scale removal, or angular standardization. Validate fitted
std>0; a zero/nonfinite scale is an error, not an invitation to refit on test.

Nmax is **384**, chosen by the declared >=99% full-event coverage and <=0.1%
event-mean lost scalar-pT rule. Retain the first `min(N,384)` sorted particles.
Record original/retained multiplicity and retained scalar-pT fraction. Full
canonical records preserve discarded-view particles. Alternative Nmax values
are later controlled experiments; do not tune against test signals.

Pad **after transformation** with `[0,0,0,0]`; otherwise a zero physical padding
triplet would incorrectly become cos(phi)=1 or a negative standardized feature.
Mask **True = real retained particle**, **False = padding**; True entries form a
prefix. Mask padding in attention, pooling, losses and statistics. No position
embeddings or original-slot features for the initial permutation-symmetric set
view. Models must handle fewer than 384 objects through the mask.

## Baseline aggregate view

Compute from **all full canonical physical particles**, before truncation, with
float64 accumulation. Eight channels, exact order below. Let
S=sum_i pT_i, Qx=sum_i pT_i cos(phi_i), Qy=sum_i pT_i sin(phi_i),
mu_eta=sum_i pT_i eta_i / S, E=sum_i pT_i cosh(eta_i),
Pz=sum_i pT_i sinh(eta_i). Units are GeV with c=1 for momentum/mass proxies.

| Index / JSON name | Definition | Units | Motivation | Transform before standardization |
| --- | --- | --- | --- | --- |
| 0 `multiplicity` | N | count | Event complexity | log1p(N) |
| 1 `scalar_pt` | S | GeV | Visible transverse scale | log1p(S / 1 GeV) |
| 2 `max_pt` | max_i pT_i | GeV | Hardest constituent | log1p(max pT / 1 GeV) |
| 3 `pt_balance` | sqrt(Qx²+Qy²) / S | dimensionless | Relative visible transverse imbalance | identity |
| 4 `weighted_eta_mean` | mu_eta | dimensionless | Longitudinal placement | identity |
| 5 `weighted_eta_std` | sqrt(sum_i pT_i(eta_i-mu_eta)² / S) | dimensionless | Longitudinal width | identity |
| 6 `pt_concentration` | sum_i pT_i² / S² | dimensionless | Hardness concentration | identity |
| 7 `massless_event_mass` | sqrt(E²-Qx²-Qy²-Pz²) | GeV | Full visible massless scale | log1p(M / 1 GeV) |

M assumes massless constituents; it is not reconstructed dijet mass. Q/S is not
experiment-provided missing energy. All eight observed training features are
finite and nonconstant. Guard S>0. For M² only, clamp negative floating roundoff
to zero if its magnitude is <= `64*float64_eps*(E²+Qx²+Qy²+Pz²)`; material
negative mass² is an error. Do not clip other features by test-derived ranges.

Apply the listed transforms, then `(value-mean[j])/std[j]` for every channel,
using JSON `preprocessing.aggregates.mean/std`. These are **transformed-feature**
statistics fitted in float64 with equal training-event weights and `ddof=0`.
Output FP32 `[8]`; no production matrix has been materialized in Task 0004.
Small differences caused by wrapped-angle/FP32-derived calculations must be
tested with numeric tolerances in Task 0005; frozen scalers remain unchanged.

## Labels and split permissions

Labels are uint8: 0=background, 1=two-prong signal. Keep them outside feature
arrays and training batches; expose test truth only to final evaluation code.
No event ID, truth, source, split, fingerprint or original slot is a model input.
Use saved row membership from ignored `data/analysis/lhco-rd-v1/`, with verified
artifact hashes and group-safe assignment; no resampling/resplitting per model.

| Population | Permitted purpose |
| --- | --- |
| 699,957 train background | Fit all preprocessing, EDA and unsupervised models |
| 74,749 selection-validation background | Background generalization/model selection; no scaler fit |
| 74,823 calibration-validation background | Predetermined background operating-point calibration; no scaler fit |
| 150,471 test background | Once-frozen final evaluation only |
| 100,000 test signal | Once-frozen anomaly evaluation only |
| 8,494 dev background (6,999/747/748 roles) | Pipeline/smoke development, never final reported ML results |

Validation roles have distinct hash domains, and no anomaly validation sample
exists. Signal-informed selection requires an explicitly revised protocol with
new held-out evaluation. Test integrity/schema checks are allowed; test feature
distributions, score performance and labels must not tune preprocessing/models.

## Provenance and future benchmark boundary

Task 0005 must record source record/DOI/checksums, acquisition metadata where
known, preprocessing/aggregate/schema versions, this configuration and its
SHA-256, split seed/version and membership hashes, code commit (or base commit
plus dirty code hashes), environment, artifact sizes/hashes and creation metadata
in a simple ignored JSON manifest. Verify rather than assume compatibility.
NPY primitive arrays permit PyTorch access and memory-mapped repeated loading;
no extra storage dependency or database is required.

ML evaluation may time the scientifically appropriate loading/preparation path
separately. Inference benchmarking must use preloaded deterministic views and
define whether device transfer is included; exclude download/disk read and
preprocessing fitting from model/runtime latency. No inference timings exist yet.
Later monitor score/acceptance bias versus N, S, max pT, M and retained-pT fraction.
