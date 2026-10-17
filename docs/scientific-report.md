# Scientific findings

RareGate asks whether a compact anomaly detector can preserve sensitivity to rare
signals while reducing the cost of event selection. The main comparison uses
lepton-prefiltered ADC2021 simulation and a common twelve-feature representation.
Two autoencoders are compared with PCA and regularized Mahalanobis distance.
Training uses background events only; signals enter the final evaluation.

## Detection performance

The evaluation contains one million background events and 40,000 events for each
signal, A → 4ℓ and LQ → bτ. At a target background acceptance of 1%, the results are:

| Method | A → 4ℓ efficiency | LQ → bτ efficiency |
|:--|--:|--:|
| Compact autoencoder | 37.33% | 6.90% |
| Reference autoencoder | 50.53% | 10.63% |
| PCA, three components | 22.72% | 11.91% |
| Regularized Mahalanobis | 50.13% | 15.84% |

Neural results average three separately trained models, rather than an ensemble.
The corresponding simultaneous efficiency bounds include uncertainty in the
background calibration quantile. All methods have comparable achieved background
acceptance within the specified tolerance.

The compact autoencoder fails the stated compression objective. Paired bounds
exclude retention of 90% of reference efficiency on both signals: compact minus
0.9 times reference lies in [−0.09795, −0.06495] for A and [−0.03595, −0.01709]
for LQ. The smaller network therefore loses sensitivity under this training budget.

Mahalanobis improves on compact for both signals. On LQ it also improves on the
reference autoencoder, with a paired difference of 3.95–6.46 percentage points.
The reference–Mahalanobis difference on A remains unresolved; this is not evidence
of equivalence. Mahalanobis is a useful baseline for these features and workload.

Its observed LQ efficiency is above the project's 15% utility target, but the
simultaneous bound, **14.65–16.97%**, crosses that target. The target is a study
criterion, not a universal threshold for scientific validity or an LHC requirement.
No method meets the complete quality-and-cost criterion.

## Computational cost

| Method | Scoring boundary, µs | Joint boundary, µs |
|:--|--:|--:|
| Compact autoencoder | 18.522 | 284.881 |
| Reference autoencoder | 31.846 | 295.362 |
| PCA | 6.530 | 266.302 |
| Mahalanobis | 8.691 | 269.108 |

Each value is a time per call for 32 events: the median of eight block means,
with neural seed costs averaged within each block. Measurements use single-thread
CPU execution on macOS arm64. The scoring boundary includes scores, masks and
owned outputs. The joint boundary additionally constructs and scales features
from objects already in memory; loading and HDF5 I/O are excluded.

The paired joint compact/reference median ratio is 0.963, short of the required
25% reduction. Mahalanobis costs about 5.48% less than compact by the paired
median statistic, also short of that margin. A cheaper scorer gives limited
overall benefit when common input processing accounts for substantial work.
These measurements do not independently isolate the cost of each stage.

## Interpretation

The comparison supports a negative compression result and a strong covariance
baseline. It does not establish that nonlinear methods are generally inferior:
all six autoencoders reached the 80-epoch cap, and neither convergence nor
architectural optimality was demonstrated. Selection strongly favors some lepton
multiplicities, which limits interpretation beyond this simulated population.
The results establish neither detector readiness nor physical LHC rates or
discovery significance.

See [experiment design](experiment-design.md), [evaluation methods](evaluation-methods.md)
and the [numerical tables](../results/tables/) for the supporting definitions.
