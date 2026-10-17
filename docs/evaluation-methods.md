# Evaluation methods

RareGate evaluates detection quality at specified background acceptance and
measures computational cost at explicit processing boundaries. A high ranking
score alone does not establish useful rare-event selection or fast execution.

## Calibration and operating points

All anomaly scores are oriented so that larger values are more anomalous.
For each fitted model, the calibration background fixes a higher empirical
quantile, and selection uses `score > threshold`. The primary target background
acceptance is 0.01, with 0.001 as a secondary point. Final background data measure
the achieved acceptance rather than assuming that it equals the target.

Signal efficiency is the fraction of signal events retained. Neural efficiencies
average the indicators from three independently fitted seeds within each event;
the sample size is still 40,000 per signal, not 120,000. These averages describe
the selected fits, not an ensemble detector or arbitrary future training seeds.

## Uncertainty and comparisons

The final ADC comparison uses a simultaneous error budget of 0.05: 0.01 for
calibration, 0.01 for final background and 0.03 for signal inference. Sixteen
calibration brackets represent uncertainty in the population background quantile.
Simultaneous Clopper–Pearson intervals quantify final-background acceptance;
Wilson intervals are also available as descriptive summaries.

The signal family contains 44 two-sided bounds: 24 pairwise differences, four
compact-versus-90%-reference quantities and sixteen efficiencies, covering both
signals and operating points. Variance-sensitive empirical Bernstein bounds use
paired event quantities and sample variances with one degree-of-freedom correction.
Calibration uncertainty is propagated by evaluating opposite bracket endpoints
for the candidate and comparator. Bracket endpoints are not replacement cuts.

A point at the frozen empirical cut and a bound for efficiency at the population
background quantile answer related but different questions. In particular,
Mahalanobis's observed LQ efficiency can exceed 15% while its population-quantile
bound still crosses that target. An unresolved comparison does not prove equality.
Bounds condition on the fitted models, finite seeds and approximately independent
event groups; exact deduplication does not establish generator independence.

## Additional diagnostics

ROC AUC summarizes ranking across cuts; average precision depends on prevalence.
The final ADC AP calculation uses a constructed prevalence of 1/26. These metrics
cannot replace efficiency at the calibrated operating point. Nominal signal
efficiency divided by the square root of background acceptance is descriptive,
without a luminosity or nuisance model; it is not discovery significance.

Fixed rotations/reflections and batch/reload checks test numerical behavior.
Profiles across MET, lepton and jet multiplicities show how selection changes
the background population. Strong profile differences are selection effects,
not evidence of decorrelation or a causal explanation of discrimination.

## Timing

Report time per call with its batch size, runtime, thread setting and exact
boundary. The joint boundary includes in-memory object aggregation, scaling,
scoring, masks and owned outputs, while file loading and HDF5 I/O are excluded.
Eight paired blocks control comparisons; neural seed costs are averaged before
ratios and medians are formed. Direct boundary measurements do not identify
causal stage costs by subtraction or imply physical event throughput.

See the [experiment design](experiment-design.md) for decision margins and the
[scientific report](scientific-report.md) for the measured outcomes.
