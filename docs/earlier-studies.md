# Earlier studies and engineering context

The ADC comparison is the main scientific result. Other parts of the repository
examine related questions on LHC Olympics data and in CPU/streaming experiments.
Their conclusions apply to their own representations and workloads.

## LHC Olympics baselines

The LHCO analysis uses the corrected R&D particle dataset with separate
background development/calibration roles and two signal topologies. Its
aggregate representation has eight features, unlike the ADC twelve-feature view.
PCA and compact reconstruction models provide useful implementation baselines,
but neural ROC AUC is moderate, approximately 0.660 and 0.586 across the two
signals. At the strictest calibrated cuts the autoencoder retains 56 and 34
signals out of 100,000, against 116 of 150,471 shared background events.

These results do not establish strong rare-anomaly usefulness. The evaluated
populations are exposed, so further exploration on them is descriptive rather
than new independent confirmation. The later ADC experiment neither confirms
the same fitted LHCO model nor resolves differences between the populations.

## CPU and queue behavior

CPU studies compare multiple processing boundaries and batch occupancies.
A cheap model can have little effect on total service time when raw access,
feature construction and output handling dominate. Measurements at a particular
boundary should not be substituted for a broader pipeline cost.

Synthetic queue simulations examine batching, occupancy, admission and backlog
under explicit assumptions. Their offered loads and survivor-conditioned latency
are model outputs, not physical detector rates or production-tail guarantees.
Only part of the occupancy space was directly measured.

## Streaming and alternative models

Bounded streaming prototypes demonstrate numerical agreement for individual PCA
and autoencoder integrations, but overall pilots retain resource-accounting and
acceptance limitations. Particle-set models remain an exploratory implementation
without completed canonical training or a supported scientific conclusion.
ONNX export parity is distinct from a successful runtime benchmark; a current
MPS performance result is not established.

These branches illustrate engineering constraints without extending the ADC
quality claims. The [scientific report](scientific-report.md) and
[evaluation methods](evaluation-methods.md) state the supported conclusions.
