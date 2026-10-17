# Experiment design

The comparison tests a specific proposition: a compact background-trained
autoencoder should retain at least 90% of a larger reference model's signal
efficiency while reducing measured joint CPU cost by at least 25%. Analytical
baselines test whether the same representation benefits from a simpler score.

## Inputs and models

The input is a standardized vector of twelve event aggregates from ADC2021
simulation. Preprocessing is fitted on training background only. Background
roles for fitting, checkpoint selection, calibration and evaluation are separate;
exact duplicate content is grouped before partitioning. Signals are used only
for evaluation. The [data guide](data-preparation.md) gives the sources, role
sizes and feature definitions.

| Model | Design | Fits |
|:--|:--|--:|
| Compact autoencoder | 12 → 8 → 3 → 8 → 12; 271 parameters | 3 seeds |
| Reference autoencoder | 12 → 32 → 16 → 3 → 16 → 32 → 12; 1,999 parameters | 3 seeds |
| PCA | Three retained components from centered FP64 SVD | 1 |
| Mahalanobis | Covariance with 0.1 isotropic shrinkage; Cholesky solve | 1 |

Autoencoders use background reconstruction MSE, Adam with learning rate 0.001,
batches of 2,048 and an 80-epoch limit. Seeds are 1729, 1730 and 1731. Within each
seed, both architectures use paired shuffle histories; each model selects its own
minimum-loss checkpoint on selection background. Every fit reaches the epoch
limit, so the comparison concerns these finite-budget fits rather than converged
or optimal networks.

Scores increase with anomalousness. Autoencoder scores sum squared reconstruction
residuals using FP64 subtraction after FP32 reconstruction; PCA uses residual
SSE and Mahalanobis uses a nonnegative quadratic score. Each fitted stream
receives its own background calibration cut, using the higher empirical quantile
and the strict decision rule `score > threshold`.

## Decision criteria

The primary background target is 0.01; 0.001 is a secondary check. Compact must
satisfy all of the following at the primary point:

- A positive lower bound for compact minus 0.9 times reference efficiency on
  **both** signals.
- Efficiency lower bounds of at least 15% on both signals.
- Comparable achieved background acceptance: individual arm intervals within
  [0.009, 0.011], and pairwise differences within ±0.001.
- A joint batch-32 CPU median paired ratio no greater than 0.75, with at least
  seven of eight block ratios no greater than 0.80.

A simple baseline must additionally improve compact by more than one percentage
point on both signals, with the same utility, rate and CPU checks. The 15% target
is a declared utility criterion for this study, not a detector-derived requirement.
The secondary point uses a 5% utility target and wider relative rate tolerance;
it cannot replace the primary decision.

## Measurement and uncertainty

Quality evaluation uses one million background events and 40,000 events per
signal. Repeated models do not increase the independent event count. Calibrated
cuts and model choices are fixed before final outcome comparisons.

CPU comparisons use the same 4,096 training-development events across eight
paired blocks, batch sizes 1, 32 and 512, and two directly measured boundaries:
scoring with masks/outputs, and in-memory objects through feature construction,
scaling, scoring and outputs. Loading and HDF5 I/O remain outside the timers.
Neural seeds are averaged within each block before forming paired ratios.

[Evaluation methods](evaluation-methods.md) explain the simultaneous uncertainty
bounds. The [scientific report](scientific-report.md) gives the outcome.
