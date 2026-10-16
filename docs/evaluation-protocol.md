# RareGate evaluation protocol — version 1

Protocol identifier: `latenttrigger-evaluation-v1`, established in Task 0006.
This is the common score-evaluation contract for PCA and future models.
The [data design](data-design.md) and [preprocessing contract](preprocessing-contract.md)
remain authoritative for source/split/feature semantics.

## Score convention and populations

Every score is a finite scalar; **larger means more anomalous**. Normalize a
future reversed orientation before evaluation and document that mapping. Metrics
do not silently flip scores. Truth is separate metadata, never an input feature.

| Saved population | Count | Permitted use |
| --- | ---: | --- |
| train_background | 699,957 | Fit preprocessing/model parameters using background only |
| validation_selection_background | 74,749 | Preregistered background model diagnostics/selection; no scaler fitting |
| validation_calibration_background | 74,823 | After model freezes, background threshold calibration; no model tuning |
| test_background | 150,471 | Future explicitly authorized frozen-candidate final evaluation |
| test_signal | 100,000 | Same future final evaluation; never model development |
| dev subset | 8,494 | Pipeline/synthetic implementation diagnostics, not final ML results |

Task 0006 requests only the first three populations. Full-store hashing and
structural integrity checks remain permitted custody operations; they must not
expose test scores, physics distributions or performance to development. A raw
byte read for integrity is distinct from a model population read.

## Model selection and freezing

Choose objectives, representation, hyperparameters and comparison candidates
before test unblinding. Use only training/background selection information under
an explicitly recorded selection rule. PCA chooses the smallest k reaching
95% cumulative **training** explained variance; selection scores do not retune k.
Calibration scores do not choose a model. Test AUC/signal efficiency must never
select features, k, sequence length, scalers, early stopping or model candidates.
Future autoencoder/Transformer tasks must record their background selection rule.

Freeze each model/config artifact and background-calibrated operating thresholds
before final evaluation. Repeated test-guided development turns the test set into
validation. If a final result motivates a new design, disclose exposure and
establish a new evaluation protocol/population; the same test cannot be reblinded.
Task 0006 does not unblind tests or claim anomaly-discrimination performance.

## Background threshold calibration

For alpha in `{0.1,0.05,0.01,0.001}`, use only calibration-background scores.
For sorted scores `s_(0),...,s_(N-1)`, freeze:

\[
\tau_\alpha=s_{\lceil(N-1)(1-\alpha)\rceil},\qquad
\text{accept event iff }s>\tau_\alpha.
\]

This is NumPy `quantile(...,1-alpha,method="higher")`, with **strict >**, including
ties. It is conservative for calibration empirical acceptance (<=alpha); it does
not guarantee population or independent-validation acceptance. No jitter, random
tie breaking, interpolation or test-background threshold refit. Record threshold,
calibration accepted/total/rate and expected tail size `N*alpha`.
[NumPy quantile convention](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html)

Check the frozen threshold independently on selection background. Report accepted
counts, realized FPR, absolute deviation `abs(realized-alpha)` and signed relative
deviation `(realized-alpha)/alpha`. This is a stability diagnostic, not authority
to tune thresholds against selection or test. Calibration summaries/plots are
descriptive and must not feed back into component/feature selection.

## Future signal-aware metrics

The reusable functions consume background/signal scores or strictly validated
binary labels (0=background,1=signal) and finite score arrays. Reject empty,
nonfinite, multidimensional, invalid-label or single-class inputs.

- **ROC-AUC:** empirical rank-based area from scikit-learn; ties receive the
  library's standard treatment. It assesses orientation as supplied.
- **Average precision (AP):** scikit-learn's recall-increment weighted precision,
  not trapezoidal PR area. AP depends on sample class prevalence: always report
  background/signal counts and prevalence. The released mixture is not an LHC rate.
- **Signal efficiency/TPR:** accepted signal / total signal.
- **Background efficiency/FPR:** accepted background / total background.
- **Rejection:** `1/FPR` when background acceptance is nonzero. For zero observed
  acceptance return null rejection with zero count/sample size and an upper bound;
  never advertise infinite rejection.
- **TPR at fixed FPR:** from the complete empirical ROC, choose the largest
  attainable TPR with achieved FPR <= requested target. On tied optimal TPR use
  the first/highest-threshold point (lowest background acceptance). Targets:
  0.1,0.05,0.01,0.001. Do not interpolate between unattainable tie jumps.
- **FPR/rejection at fixed TPR:** choose the first/highest-threshold ROC point
  with TPR >= target, initially 0.5,0.8,0.9. Report achieved TPR/FPR and counts.

Empirical ROC metrics are **descriptive final benchmark points**. They do not
replace deployable thresholds frozen on calibration background. ROC's `>=cutoff`
point is encoded under the universal strict-`>` rule using the immediately lower
float64 cutoff; the initial accept-none point has null threshold and explicit
`accept_none` kind. Calibrated thresholds always use their original strict-`>`
values. An extreme lowest-finite cutoff whose lower float overflows to negative
infinity uses explicit `accept_all`, not a misleading accept-none marker.
Report achieved rates, not targets alone.
[ROC implementation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html),
[AP implementation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)

## Finite-sample limitations

Every operating point returns accepted count, total, rate and empirical resolution
`1/N`. Provide a 95% Wilson binomial interval for rates. Zero observed background
acceptance additionally yields the one-sided exact 95% population upper bound
`1-0.05^(1/N)` under independent Bernoulli sampling. This is uncertainty information,
not observed rejection or proof of zero population FPR. Duplicate-safe source
events support the initial sampling approximation, not detector/physics guarantees.

About 150k test background events imply ~150 expected false positives at 1e-3,
~15 at 1e-4; do not extrapolate rejection below empirical support. Flag calibration
targets below `1/N` and report expected tail counts. No tail fit/extrapolation is
introduced. Intervals describe sample fluctuations under the stated assumption;
they do not include simulation uncertainty, model selection or calibration error.

## Background diagnostics

For each permitted background population record count, mean, population std
(ddof0), min, median, p90/p95/p99/p99.9 and max. Summary quantiles use linear
interpolation, distinct from conservative calibration quantiles. Compare ECDFs
with two-sample KS distance (including ties), without chasing significance
p-values. Report tails and relative quantile differences descriptively. Do not
clip tails or change model policy post hoc merely to improve a diagnostic.

## Final benchmark gate and unblinding record

The background CLI contains no test-access flag. `load_background_features`
rejects every role outside the three allowed backgrounds before asking the reader.
Future final evaluation is a separate module, requires `--allow-test`, verifies
the model/calibration/config/processed identities and uses the existing reader's
`allow_test=True,include_labels=True` guards. It is tested only on synthetic
fixtures in Task 0006. **Do not run it on real data during model development.**

When a future task explicitly authorizes final evaluation, create a new output
directory and write `test-unblinding.json` **before each test population request**.
Record UTC, actual code commit/base/dirty hashes, frozen model/config/data and
calibration identities, planned metrics and access counts. Preserve failed-run
records. Store final metric output/hash and mark completion. These are local
manifests; the future handoff must publicly disclose the exposure and selected
candidate list. An interrupted or partial unblinding is still exposure.

The future CLI requires explicit model, frozen background-results, store, output
and opt-in arguments; it has no automatic final-evaluation step in training.

## Reporting requirements

Report source DOI/checksum, processed/config/split identities, feature order,
model/selection rule and frozen artifact hash, software environment, populations
used, calibrated thresholds/counts, metric conventions and finite-sample limits.
Separate scientific output hashes from timestamps/timing/host metadata. Curated
small tables/figures may enter Git; score arrays, models and run manifests stay
local unless explicitly curated. State clearly when no test metrics exist.
