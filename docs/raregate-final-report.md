# RareGate: final scientific report

16 October 2026, Europe/Rome · Task0063 · Final review of accepted evidence

## Research answer and contribution

Compact neural reconstruction did not satisfy RareGate's declared quality/cost compression objective. On the ADC2021 representation, the compact autoencoder failed to retain 90% of the reference autoencoder's signal efficiency on both tested topologies and missed the required reduction in directly measured joint CPU cost. The negative conclusion is supported by simultaneous bounds excluding retention, rather than merely by a failure to obtain significance.

The comparison also establishes a useful positive result: regularized Mahalanobis scoring is a strong practical comparator for these features. It improves primary efficiency over compactAE on both signals and over referenceAE on LQ→bτ. Its A→4l difference from referenceAE remains unresolved. Its LQ empirical-cut efficiency, **15.8375%**, is above the project's 15% utility target; the simultaneous population-quantile bound **[14.649002%, 16.972217%]** crosses that target. This uncertainty does not invalidate the comparison or demonstrate efficiency below 15%.

The contribution is an auditable comparison of detection quality and measured computational cost, with a negative compression result and a supported covariance-baseline result. It establishes neither a new algorithm nor state-of-the-art performance. The practical recommendation is to use Mahalanobis as the baseline/reference choice for this representation and measured workload, while retaining the compound gate's negative outcome and operational readiness **false**. RareGate is an independent project without official CERN or experiment affiliation.

This report synthesizes the unchanged [prospective protocol](decisive-scientific-experiment.md), [preparation record](decisive-adc-preparation-training.md) and [final experimental report](decisive-adc-results.md). Task0063 checks their aggregate consistency; it does not independently replicate their experiment.

## Data, protected roles and representation

The selected route uses the public ADC2021 v2 benchmark background, A→4l and LQ→bτ files. The [challenge](https://mpp-hep.github.io/ADC2021/), [data descriptor](https://www.nature.com/articles/s41597-022-01187-8) and pinned Zenodo records [5046428](https://zenodo.org/records/5046428), [7152590](https://zenodo.org/records/7152590) and [7152599](https://zenodo.org/records/7152599) provide the source descriptions, historically verified in Task0060. They describe PYTHIA/DELPHES simulation with a lepton prefilter. Those descriptions are distinct from this project's measured payload counts and do not establish actual mixture proportions or generation independence.

Task0061 accepted 680,426,757 bytes in three transfers. Actual background contained **13,451,915 rows / 13,449,154 exact content groups**, rather than the descriptor's nominal four million rows. There were 55,969 A and 340,544 LQ groups, zero quarantines and zero cross-label conflicts; 2,761 exact background duplicates were removed before partitioning. Exact canonical-content grouping prevents identical provided objects from crossing roles. It cannot detect all near duplicates, shared generator ancestry or correlated generation.

| Role | Unique groups | Permitted purpose in the experiment |
|---|---:|---|
| Background training | 200,000 | Scaler and model fitting |
| Background selection | 50,000 | Each AE's own checkpoint selection |
| Background calibration | 1,000,000 | Frozen cuts and quantile brackets |
| Final background | 1,000,000 | Achieved acceptance and final comparisons |
| Final A / final LQ | 40,000 each | Signal evaluation only |
| Development | 4,096, within training | Parity and CPU workload; no additional independent sample |

Roles were stored separately and fitting was restricted to training/selection. Final structural preparation was documented exposure, while outcome feedback was protected until freeze. This is a statistical holdout, conditional on the grouping and simulation assumptions, rather than true blindness. The unused population remains sealed and confers no retry allowance.

The new `adc-invariant-aggregates-v2` view has twelve channels: log MET; electron, muon and jet counts; each class's log scalar-pT sum and log maximum pT; visible transverse-vector balance; and log massless invariant mass of all provided leptons. Accumulation and training-only means/population standard deviations use FP64, followed by one FP32 cast. The inputs are the publisher's provided MET/4-electron/4-muon/10-jet slots. These caps and the electron-or-muon preselection limit transfer to full events or unfiltered collisions. Discarding signed eta and absolute phi supplies mathematical rotation/reflection identities, without removing selection sculpting.

## Models, prospective decisions and uncertainty

| Arm | Fixed design | Fits |
|---|---|---:|
| compactAE | 12→8→3→8→12; 271 parameters | 3 seeds |
| referenceAE | 12→32→16→3→16→32→12; 1,999 parameters | 3 seeds |
| PCA3 | Centered FP64 SVD, three retained axes | 1 |
| Mahalanobis | Training covariance with 0.1 isotropic shrinkage; Cholesky solve | 1 |

Both AEs used the same declared three seeds, paired shuffle histories, background-only MSE training and own selection minima. All six reached the **80-epoch cap**; selected epochs in compact/reference order were 80/80, 80/78 and 80/79. The study therefore concerns these fixed-budget selected fits. It establishes neither convergence nor optimal networks, and cannot settle the performance of all nonlinear approaches. PCA's common bottleneck controls one design difference; architecture, optimization and score geometry still differ, preventing a causal claim about nonlinearity.

AE reconstruction SSE uses FP64 subtraction after FP32 reconstruction; PCA uses residual SSE and Mahalanobis a nonnegative quadratic score. Higher scores are anomalous. After all fits froze, each stream received its own background calibration cut using the `higher` quantile and strict `>`, at primary background target 0.01 and secondary 0.001. The six neural streams are separate models, with no ensemble or favorable-seed selection.

The prospective compact criterion required: positive lower bounds for compact−0.9reference on **both** primary signals; compact efficiency lower bounds at least 15% on both; comparable achieved background rates; and joint B32 CPU median ratio at most 0.75 with at least seven of eight paired blocks at most 0.80. Simple-selector dominance additionally required a lower improvement over compact exceeding one percentage point on both topologies, its utility/rate checks and the same CPU rule.

**15% was a prospective project utility target.** The protocol does not derive it from an actual LHC trigger budget, luminosity/nuisance model or deployment cost function. Its application-specific justification is limited. Keeping it unchanged preserves the declared decision; crossing it does not define the boundary of scientific validity. No replacement target or new confirmatory claim is introduced here.

The frozen family allocates total error 0.05 as 0.01 calibration, 0.01 final background and 0.03 signal inference. Sixteen calibration brackets propagate population-background-quantile uncertainty. Final-background simultaneous Clopper–Pearson intervals accompany descriptive Wilson intervals. Signal inference contains 24 unordered arm differences, four noninferiority quantities and sixteen efficiencies: **44 two-sided bounds**. The empirical Bernstein expression uses paired endpoint means and ddof1 variances, with support widths 2, 1.9 and 1, following the protocol's [method reference](https://arxiv.org/abs/0907.3740).

For neural arms, indicators are averaged across seeds within each event before inference. The signal sample size remains **40,000**, rather than 120,000. The bounds condition on these fitted models, finite seeds and approximately independent event groups; deduplication does not prove that last assumption. Lower comparison bounds use the candidate's upper calibration endpoint and the comparator's lower endpoint; upper bounds reverse those endpoints. Bracket endpoints never become new deployment cuts.

## Primary scientific results

A single final context evaluated 1,000,000 background and 40,000 groups per signal across eight streams: **8,640,000 score presentations / 270,000 B32 calls**, with no final padding. Repeated streams, calibration, CPU calls and symmetry transformations do not enlarge the independent event population.

The following points use frozen empirical cuts; brackets are simultaneous efficiency bounds at the **population background quantile**, including calibration uncertainty. Efficiencies are percentages.

| Arm | A→4l point [bound] | LQ→bτ point [bound] |
|---|---:|---:|
| compactAE | 37.3342 [35.6553, 39.0218] | 6.8967 [6.1783, 7.6306] |
| referenceAE | 50.5283 [49.2335, 51.8072] | 10.6250 [9.7367, 11.4864] |
| PCA3 | 22.7175 [21.2887, 24.1704] | 11.9050 [10.8848, 12.9682] |
| Mahalanobis | 50.1325 [48.7729, 51.4571] | 15.8375 [14.649002, 16.972217] |

[Operating-point counts](../results/tables/final/task0062-adc-signal-operating-points.csv) retain all seeds and both cuts. Primary compact accepted counts are 15,874/14,010/14,917 on A and 3,119/2,814/2,343 on LQ; reference counts are 20,061/20,780/19,793 and 4,060/4,483/4,207. Every denominator is 40,000. Seed variation is visible evidence about these fits, without generalization to arbitrary training seeds.

The [paired bounds](../results/tables/final/task0062-adc-paired-inference.csv) for compact−0.9reference are **[−0.097949, −0.064946] on A** and **[−0.035947, −0.017094] on LQ**. Both upper bounds are negative: 90% retention is excluded on both signals. Empirical-cut efficiency ratios are descriptively 73.89% and 64.91%; these are not inferred ratio intervals.

Every arm supports the primary 15% utility target on A. On LQ, compact, reference and PCA upper bounds are below 15%, excluding their target. Mahalanobis is **unresolved**, with the target inside its interval. Its lower-bound gap is approximately **0.351 percentage points**; that is a gap in the evidence required by the rule, not a measured efficiency deficit. The empirical-cut point and population-quantile bound answer related but different questions.

Mahalanobis-minus-compact paired lower improvements are **11.004 percentage points on A and 7.611 on LQ**, exceeding the declared one-point quality margin. Mahalanobis-minus-reference on LQ is supported at **[3.954, 6.456] percentage points**. On A, reference-minus-Mahalanobis **[−0.567, 1.386] percentage points** leaves the difference unresolved; it does not prove equivalence. PCA is worse than compact on A and better on LQ. These positive and mixed comparisons remain useful even though full simple-selector dominance is unestablished.

Measured mean primary background acceptances are 0.009961667/0.009985667/0.009896/0.009953 for compact/reference/PCA/Mahalanobis. All arm intervals lie within [0.009, 0.011], and all six pair difference intervals within ±0.001. Secondary checks also pass their declared wider relative tolerance. Comparability within tolerance does not mean exact equality. The [background table](../results/tables/final/task0062-adc-background-acceptance.csv) separates sixteen stream rows from eight arm summaries; shared background and duplicated analytical views are not replications.

![Primary efficiency, fraction scale; dots and seed crosses at empirical cuts, vertical population-quantile bounds](../results/figures/final/task0062-adc-primary-efficiency.png)

The three reused figures were visually inspected in Task0063. Their fractions, µs/call labels and eight-block ratios agree with the aggregates; the tables make narrow intervals easier to inspect.

## Secondary evidence and selection profiles

The secondary point remains secondary. Values below are percentages with the same simultaneous bound interpretation.

| Arm | A at target 0.001 | LQ at target 0.001 |
|---|---:|---:|
| compactAE | 13.8592 [12.3518, 15.3267] | 0.9667 [0.6641, 1.3017] |
| referenceAE | 22.7617 [20.9465, 24.5720] | 1.5958 [1.1969, 2.0211] |
| PCA3 | 4.7925 [3.7268, 5.9344] | 2.0750 [1.5604, 2.6149] |
| Mahalanobis | 21.5225 [19.8153, 23.4787] | 2.6625 [2.0587, 3.2922] |

All LQ upper bounds exclude the secondary 5% target; PCA's A target is unresolved. Secondary compact retention is excluded on A and unresolved on LQ, whose NI bound is [−0.009676, 0.000190]. There is no secondary rescue of the primary verdict.

Ranking also depends on the metric. LQ reference AUC spans 0.797–0.819 across seeds, exceeding Mahalanobis's 0.784, despite Mahalanobis's stronger primary-cut efficiency. AUC therefore cannot substitute for the operating-point question. Complete AUC/AP and attainable ROC summaries remain in the [experimental summary](../results/tables/final/task0062-adc-evaluation-summary.json), `/ranking_secondary`. AP uses constructed prevalence **1/26**. Nominal SIC uses efficiency divided by the square root of achieved background acceptance; it is a descriptive approximation, without luminosity, nuisance parameters or discovery significance. No SIC-optimized cut or new uncertainty calculation is supplied.

All sixteen fixed rotation/reflection outcomes pass on 512 final-background groups, with zero scaled-feature/score differences and decision flips. The qualified 24 stream/shape cells include B1/B32/B512, with exact B32 reload/repeat and no decision changes. These tests support numerical identities, not detector acceptance symmetry.

The [280-row robustness table](../results/tables/final/task0062-adc-robustness.csv) contains sixteen identities and 264 stream/arm profile views. Each MET, lepton and jet partition totals one million groups; every bin has at least twenty. At the primary cut, reference/Mahalanobis accept **92.3622%/94.5827%** of 3,858 groups with at least three leptons, versus **0.0748%/0.1612%** of 907,622 single-lepton groups. Strong multiplicity selection is visible. It is compatible with strong A→4l discrimination, without proving a causal mechanism or decorrelation. Missing subprocess labels prevent actual SM-component efficiencies.

## Direct computational result

One fixed CPU matrix measured eight streams, three batch sizes, two boundaries and eight blocks: **384 cells, 49,152 timed calls and 12,288 warmups** on the same 4,096 training-development groups. Historical runtime receipts record macOS arm64, Python 3.12.12, NumPy 2.5.3 and Torch 2.14.1, with one effective Torch/BLAS thread. Task0063 did not probe or requalify that runtime.

| Arm | Score + masks + owned outputs, B32 µs/call | In-memory objects → aggregates/scaling → score/masks/outputs, B32 µs/call |
|---|---:|---:|
| compactAE | 18.522 | 284.881 |
| referenceAE | 31.846 | 295.362 |
| PCA3 | 6.530 | 266.302 |
| Mahalanobis | 8.691 | 269.108 |

These are medians of eight block means after averaging neural seed costs within blocks. Gather/indexing, loading and HDF/custody work are outside the timers. The two boundaries were measured directly; their difference is not an independently measured causal feature-stage cost.

| Paired joint B32 comparison | Median ratio | Blocks ≤0.80 | Required margin |
|---|---:|---:|---|
| compact/reference | 0.962989814 | 0/8 | Not met |
| PCA/compact | 0.925877925 | 1/8 | Not met |
| Mahalanobis/compact | 0.945206261 | 1/8 | Not met |

Mahalanobis has about **5.48% lower measured joint cost** by the paired median statistic. That useful observation falls short of the required 25% reduction and seven-of-eight rule. Compact also has a median below one but misses the margin; its adverse eighth ratio **1.205526537** remains included. The gate was not a runtime resource cap, and failing it does not mean being uniformly slower. Every ratio was reconstructed from the [stream/block means](../results/tables/final/task0062-adc-cpu-costs.csv), rather than by dividing displayed medians.

A cheap scorer has limited impact when common processing is substantial. This interpretation is consistent with the measured boundaries and the source path `boundary → data.features → data.transform → models.public_score`, with mask/output work shared. The experiment did not separately identify causal overhead components. No timing subtraction, algorithm-only substitution, physical event throughput or production-tail guarantee follows.

![Quality versus direct joint B32 cost](../results/figures/final/task0062-adc-quality-cost.png)

![All paired primary CPU blocks, including block eight](../results/figures/final/task0062-adc-paired-cost-ratios.png)

## Earlier work and remaining scope

The [v1 snapshot](v1-research-conclusions.md) remains historical evidence on a different LHCO population and eight-feature representation: AE AUC about 0.660/0.586, with strictest cuts retaining 56/34 of 100,000 signals against 116 of 150,471 shared background. Permanent test exposure remains YES/YES/YES. ADC provides a new conditional comparison; it does not independently confirm the old LHCO model or resolve Task0034's frozen matched design and Task0036's unresolved acquisition route.

Six accepted historical CPU boundaries and synthetic queue studies remain scoped to their populations, timings and assumptions. Only 32 of 169 occupancies were measured; modeled queue presentations and survivor-conditioned latency do not become physical rates. Task0052 remains partial/negative. Task0056 PCA and Task0058 AE component parity are positive, with both whole pilots unaccepted. Task0058's **24,124 cache bytes** are recorded file lengths with unknown growth, rather than measured growth or cap exhaustion. Particle work remains 192/192 consumed diagnostic steps without canonical completion. Task0024 ONNX export/equivalence acceptance does not accept the failed Task0025 benchmark; current MPS remains unverified.

The [sixteen audit dispositions](../results/tables/final/task0063-final-review-summary.json) distinguish recorded software fixes, issues addressed by ADC's design/evidence, residual assumptions and excluded branches. The old 3,002-test audit and 204-test evaluator receipts apply to their recorded bundles; neither suite ran in Task0063. Completing this scientific project requires no completion of particle, MPS/ONNX or streaming branches. Operational readiness remains false.

## Reproducibility and final recommendation

| Conclusion | Curated evidence | Task0063 recheck |
|---|---|---|
| Source/roles/fits | Task0061 report and summary | Metadata/aggregate consistency; no payload custody |
| Primary/secondary quality and uncertainty | Background, operating-point and paired CSVs | Counts/seed means, 44-family coverage, all 88 Bernstein endpoints, binomial endpoint/rank identities, rate and decision rules |
| Direct cost | 408-row CPU CSV and summary | Complete cell scopes, seed-before-ratio arithmetic, all eight blocks and medians |
| Identities/selection | Robustness CSV, parity summary, three figures | Sixteen outcomes, 24 cells, profile partitions/means and visual labels |
| Historical status | Audit and v1 reports/receipts | Bounded document reconciliation and sixteen explicit dispositions |

The [claim map](../results/tables/final/task0063-final-claims.csv) gives paths, selectors and hashes; the [review summary](../results/tables/final/task0063-final-review-summary.json) records sources, actual checks, limits and preservation. Sixteen immutable anchors matched before and after review. A display-only rounding inconsistency in Task0062's English/Italian tables is disclosed there: exact PCA A 22.7175% and Mahalanobis LQ 15.8375% resolve the last displayed digit without changing historical files or conclusions. No material numerical contradiction was found.

Aggregate checking cannot reconstruct event pairing/variance from raw observations, prove generation independence, or replicate model execution and timing. Those require original payloads, frozen environment and a separately authorized full rerun addressing a distinct question; consumed scoring/CPU entrypoints are not routine verification commands. No acquisition, model loading, inference, fitting, calibration, timing or replay occurred in Task0063.

Use Mahalanobis as the practical baseline/reference for these features and workload. Preserve the negative preregistered compact-compression verdict, the positive paired comparisons, unresolved absolute LQ target and unmet CPU margin as separate conclusions. The current research cycle is closed; future science or deployment needs a distinct question and separate mandate.
