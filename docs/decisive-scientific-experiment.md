# Decisive scientific experiment v2

Task0060, 2026-10-16 Europe/Rome. This is the prospective specification for
**Task0061 preparation/training/freeze and Task0062 evaluation/robustness/CPU/conclusion**.
Neither task is launched here. The executable choices and numerical planning values
are in [the v2 sidecar](../configs/research/decisive_scientific_experiment_v2.json).
This document supersedes the *recommendation to stop*, not Task0059's historical
results, exposure ledger, frozen v1 contracts or failed/consumed operational pilots.

## Question, estimand and useful outcome

On ADC2021's lepton-prefiltered simulated population, can a compact background-only
selector retain **90% of the reference's detection efficiency**, while reducing
directly measured joint CPU cost by **25%**, at a common calibrated background
acceptance? The primary point is **0.01**, on **both A→4l and LQ→bτ**; 0.001 is a
predeclared secondary point. These points cannot exchange roles after results.

For arm c and signal topology s, the scientific estimand is the mean, across the
three declared training seeds, of P(score_c > population background quantile
1−α | s). Analytical arms have one deterministic fit. The six neural models are
**not an ensemble**. Each has its own background-only threshold. Report deployment
efficiency at each frozen empirical calibration threshold separately from inference
about the common population quantile. Finite calibration does not give exactly
equal measured FPRs: the rate-comparability checks below are necessary for an
approximately common-rate claim. Do not describe target labels as achieved rates.

Validity means accepted source/schema/content grouping, separated roles, no outcome
feedback, correct scores and honest conditional uncertainty. Utility means the
predeclared efficiency, retention and measured CPU margins, not AUC alone. The
contribution is an independently held-out, interpretable quality/cost comparison
within this project. It is not a new architecture, a state-of-the-art claim,
validation of the old LHCO model, FPGA deployment, or an unfiltered LHC stream.

## One route and finite metadata

The [authors' challenge](https://mpp-hep.github.io/ADC2021/) provides bounded object
inputs. We use three public benchmark files, not the blackbox. Direct Zenodo JSON
metadata and version-list endpoints were retrieved on 2026-10-16; all three list
v2 as latest, one older version, CC BY 4.0, and the nonspecific note “Several bug
fixes in dataset definition”. The exact fixes are not itemized in these records.
Pin the stated records; never mix older files or silently follow a newer release.

| Role | Version record | Exact file bytes | Publisher MD5 | Descriptor count, not local acceptance |
|---|---|---:|---|---:|
| Background | [5046428 v2](https://zenodo.org/records/5046428) | 646391984 | `08cb4801229f9d480567f8d3f5cac134` | 4000000 |
| A→4l | [7152590 v2](https://zenodo.org/records/7152590) | 5421265 | `8735ed96a96c39dd13fde7d5f7c85967` | 55969 |
| LQ→bτ | [7152599 v2](https://zenodo.org/records/7152599) | 28613508 | `ecd9750e5c51aef54918689eec1e7415` | 340544 |

Filenames, concept/older record IDs and metadata URLs are in the sidecar.
Download total is **680426757 B**. No event file was requested in Task0060.
Counts come from Table 1 of the
[published descriptor](https://www.nature.com/articles/s41597-022-01187-8.pdf),
not inspected v2 payloads. Generation uses PYTHIA 8.240, DELPHES 3.3.2 with a
Phase-II CMS card and mean pileup 20. The mixture is W/Z/tt/QCD, not individually
labeled SM subprocesses. The documented filter requires an electron above 23 GeV
with |eta|<3 or a muon above 23 GeV with |eta|<2.1. The claimed population stays
conditional on that filter and simulation; detector response and generation
independence are not experimentally certified here.

The competing [LHCO record 18983506](https://zenodo.org/records/18983506) offers
jet/substructure information but its XtoYYprime archive alone is about 4.9 GB;
the record totals about 39.9 GB. Task0036's full-event coverage, overflow and
expanded-member questions remain unresolved. A compact jet study would be a
different representation, not an exact full-event substitute. Exposed LHCO samples
cannot supply fresh confirmation. ADC is selected for bounded size, explicit object
schema and an answerable quality/cost question, before any new scores are seen.

## Payload acceptance and protected roles in Task0061

First verify exact byte lengths and publisher MD5; record local SHA256 and the
retrieved metadata identities. Read HDF headers before allocations. `Particles`
must be [N,19,4], float32 or float64, with pT in GeV, eta, phi in radians, type ID;
slot groups are MET 0, electrons 1–4, muons 5–8, jets 9–18. Types are 1/2/3/4,
padding 0. Parse names/classes metadata; the descriptor itself uses both
`Particles_Classes` and `Particle_Classes` spellings. Accept either spelling only
when the actual decoded mapping agrees; never infer an unfamiliar schema by position.

Scan chunks of at most 8192 rows. Require finite values, nonnegative MET pT and
zero MET eta, positive pT for present visible objects, exact all-zero type-0 slots,
prefix padding within each class and descending within-class pT. Check the declared
lepton filter and object cuts (electron/muon >3 GeV, jets >15 GeV and their eta
limits) with only a 1e-5 GeV boundary rounding allowance. Report all exceptions;
no more than 1% of rows may be quarantined. A contradictory class/unit mapping,
insufficient eligible unique groups or any cross-label conflict stops before fits.
Published counts are expectations: record actual counts and do not invent a match.

Fingerprint exact *provided object content*, including class and MET, in a new
`adc-exact-content-v2` domain: normalize signed zero, wrap out-of-range phi in FP64,
remove type-0 padding, sort triplets within class, encode class/count and coordinates
in little-endian FP64, then SHA256. Keep the lowest source-row representative.
Deduplicate before assigning roles, across all three files; quarantine conflicts
and stop. This detects exact canonical-content overlap, not near duplicates,
shared generator ancestry, detector-level equivalence or undocumented correlated
generation. A source row ordinal is not a physics event ID.

Order background groups by SHA256 of UTF-8
`adc-split-v2|1729|fingerprint_hex` (then fingerprint for collision tie handling).
Allocate exactly the first 200000 to training, next 50000 to selection, next
1000000 to calibration, next 1000000 to final background. Remaining groups stay
unused and sealed. Independently hash-order each signal source and reserve exactly
40000 unique groups per topology for final evaluation; no signal development set.
The published sizes leave room above these minimums; realized eligibility remains
a payload check, not future open-ended research. If a minimum fails, stop and
report source/sample insufficiency; do not choose an easier point or favorable route.

Prepare **physically separate role files** and content-bound manifests. Do not
reuse v1 `ProcessedStore`: its constructor verifies/scans all roles before its
per-read gate. The training process's allowlist contains only training and selection
files. Calibration gets a distinct phase after all model/checkpoint choices freeze.
Final background/signal features may be structurally prepared and sealed but cannot
be summarized, scored, plotted or used to choose anything before the complete freeze.
Record acquisition, structural/hash and preparation exposure positively. This is
a statistical holdout of event groups, not true blindness or independent generation;
new signal processes are excluded from training. Public documentation is already known.

## Declared representation: adc-invariant-aggregates-v2

Use every **provided** visible object, with type-ID masks; a genuine MET value of
zero is permitted. The provider's 4e/4mu/10jet caps remain truncation. No full-event
particle, charge, constituent mass or inverse-transformation claim follows.

The ordered 12 channels are:

1. log1p(MET/1 GeV).
2. Electron, muon and jet counts, three channels.
3. log1p of each class's scalar pT sum /1 GeV, three channels.
4. log1p of each class's maximum pT /1 GeV, three channels.
5. Visible transverse-vector magnitude divided by visible scalar pT sum, excluding MET.
6. log1p of the massless invariant mass of **all provided electrons and muons** /1 GeV.

For the last quantity use the independent pair formula
`m² = Σ(i<j) 2 pTi pTj [cosh(eta_i−eta_j)−cos(phi_i−phi_j)]`.
Empty/singleton lepton sets have zero mass; empty classes have zero sum/max/count;
a zero visible denominator gives zero balance. Accumulate in FP64. Fit per-channel
mean and population standard deviation on **training alone**; require std>1e-12,
do not clip, standardize in FP64 then cast once to FP32. Never fit scalers on an
all-role concatenation, and never claim an exact inverse of rounded features.

Permutation within class, added zero padding, global azimuth rotation and beam
reflection are mathematical identities of these aggregates (within declared
numerical error). Physical rotation/reflection symmetries of a detector's acceptance
are assumptions, not identities of collision data. This choice intentionally drops
signed eta and absolute phi; it is a new interpretable view, not a repair or feature
search on historical test scores. Acceptance sculpting can still occur through pT,
multiplicity and mass.

## Finite models, training and freeze

| Arm | Layers or fit | Bottleneck | Parameters / policy |
|---|---|---:|---|
| compactAE | 12→8→3→8→12 | 3 | 271 |
| referenceAE | 12→32→16→3→16→32→12 | 3 | 1999 |
| PCA3 | Centered training-only FP64 full SVD | 3 | Fixed first 3 axes, no whitening/rank search |
| regularizedMahalanobis | Training mean/covariance, ddof0 | — | Creg=.9C+.1 trace(C)/12 I; Cholesky solve |

Task0061 implements these as new 12-input models/scorers with artifact schema2
under `decisive-v2-adc/<arm>/<seed>` (analytical arms use `fit`). Do not relax the
old 8-input `CompactAutoencoder`/PCA artifact contracts to load them. Every new
scaler, fit, checkpoint, score and threshold is recomputed in Task0061; every new
quality/robustness/cost result is computed in Task0062, never substituted into v1.

Both AEs use ReLU in hidden layers, linear latent/output, explicit CPU FP32
factories, default Linear initialization under isolated CPU seeds 1729/1730/1731.
There are at most **six neural fits and two analytical fits**. The reference is
more capable by architecture, not guaranteed to win. PCA controls latent dimension;
Mahalanobis tests whether ordinary covariance geometry suffices. No attention,
hyperparameter grid, score ablation, best seed, weight averaging or ensemble is allowed.

In seed order fit compact then reference. Adam lr=.001, betas(.9,.999), eps=1e-8,
weight_decay=0, AMSGrad/foreach/fused/maximize/capturable/differentiable/decoupled
weight decay false. Pin the installed implementation and resolved options; do not
upgrade dependencies. One CPU thread, zero loader workers, batch 2048 with complete
tails, maximum 80 epochs, patience 8, min_delta=0. Minimize equal-event/channel MSE;
report epochs weighted by event counts. A local sampler generator advances across
epochs; the same seed's actual permutation stream must match across architectures.
No extra random draw may be introduced just to audit the order.

Each fit selects its own strict background-selection loss minimum (ties earliest),
clones/restores its own best state and verifies parameter/reload identity. A cap is
reported as a cap, not proof of convergence. Nonfinite loss, missing restoration,
time/RSS failure or incomplete fit makes the full matrix inconclusive; no replacement
fit silently spends a seventh allowance. Generated implementation checks may precede
fits; they do not authorize additional real pilots or search.

AE scores are FP32 reconstruction followed by **FP64 subtraction and SSE**, higher
anomalous. PCA uses FP64 residual SSE on the same FP32 standardized inputs;
Mahalanobis uses the nonnegative FP64 quadratic form. No score orientation reversal.
Canonical scoring is **B32**, final tail padded to 32 with zeros, retaining actual
rows only. Calibration and final scoring use the same code/shape. Score calibration
only after all eight fitted streams and preprocessing freeze. For each α use the
`higher` quantile and strict `>`; freeze thresholds and the uncertainty bracket below.

Freeze source/config/runtime/build/threads, role manifests, preprocessing, every
checkpoint/model/seed, order histories, stopping reasons, serialization tests,
calibration thresholds/rank brackets and CPU schedule. Task0061 ends there, with
all final outcomes protected. Task0062 records unblinding intent before any final
score read/write. Final outcomes cannot influence a correction, model, feature,
checkpoint, seed or operating-point choice.

## Statistics and predeclared decision family

Report all 8 streams, 4 arms, 2 topologies and 2 rates, including tails/failures.
Sample unit is a unique content group. A seed average uses the same events, with
N=40000, **not 120000**. Seed ranges and all individual counts remain visible;
inference is conditional on these finite seeds and approximately independent
generated event groups, not generalization to every training seed or simulation.

Allocate familywise error .05 as follows: .01 calibration, .01 final background,
.03 signal comparisons. No bootstrap over seeds and no threshold search is needed.

- **Calibration:** for each of 16 stream/rate combinations, sort N=1000000 scores.
  For q=1−α and d=.01/16, use one-based ranks
  L=BinomialPPF(d/2,N,q), U=BinomialPPF(1−d/2,N,q)+1.
  Endpoints outside 1..N are −/+infinity. This brackets the population quantile
  conservatively, including atoms; log ties and any unattainable rate.
- **Final background:** report actual strict accepted/total and Wilson 95% as
  descriptive intervals, plus simultaneous Clopper–Pearson intervals with total
  error .01 over the 16 combinations. Average the three seed interval endpoints
  for a neural arm; do not pretend their counts are independent.
- **Signal:** for each event first average indicators across its three seeds.
  For lower comparison bounds evaluate candidate at its *upper* calibration
  bracket and reference at its *lower* bracket; reverse for upper bounds. These
  brackets are for uncertainty propagation, never replacement deployment cuts.
  Use sample variance ddof1 of the paired per-event values. The fixed family is
  24 unordered arm-pair differences (6 pairs×2 topologies×2 rates), 4 compact−.9ref
  noninferiority quantities, and 16 arm efficiencies: **44 two-sided bounds**.
  For each side use
  `h = sqrt(2 s² log(4*44/.03)/N) + 7 R log(4*44/.03)/(3(N−1))`,
  with range R=2 for differences, 1.9 for NI, 1 for efficiency. Clip to support.
  This is the scaled [empirical Bernstein bound, Theorem 4](https://arxiv.org/pdf/0907.3740),
  union-bounded over 88 one-sided functions. It preserves event pairing, shared
  calibration and seed dependence without multiplying sample size.

The simultaneous inference assumes independent event groups conditional on fitted
models. Exact deduplication is not proof of that assumption; unsupported generator
correlations limit uncertainty claims. Statistical holdout, same-generator validity,
new-process transfer and true blindness are separate claims.

Rate comparability at the primary point requires every arm's mean FPR interval
inside α(1±.10), and each compared pair's interval difference inside ±.10α.
Use the difference interval [Lc−Ur,Uc−Lr]. At the secondary point tolerance is .30α,
declared now because its simultaneous finite-tail uncertainty is larger. Failure
gives no common-rate claim at that point. There is no silently randomized tie policy
or final-background recalibration. A fixed attainable ROC comparison may additionally
be reported as descriptive ranking evidence; it is not a deployment threshold.

The practical primary criterion is NI lower bound >0 for compact−.9ref on **both**
topologies, compact signal-efficiency lower bound ≥.15 on both, rate comparability,
and the joint CPU advantage below. At 0.001 the secondary utility target is .05.
These are proposed project decision targets, not universal requirements of science.
For simple-selector dominance require its simultaneous efficiency-difference lower
bound over compact >.01 on both primary topologies, primary utility/rate comparability,
and the same CPU advantage rule. Report other mixed tradeoffs without declaring a
universal winner. AUC and AP are secondary; AP states its artificial mixture prevalence.
Nominal SIC=epsilonS/sqrt(epsilonB) is only a background-dominated approximation:
no luminosity, nuisance model, discovery significance or physical trigger rate follows.
Zero background has a finite exact upper bound; SIC/rejection are unresolved, not infinity.

## Precision and power before results

Each calibration/final-background set has 1000000 groups, yielding expected tails
10000 and 1000. Normal 95% FPR halfwidths conditional on a threshold are approximately
.0001950 and .00006195; including two equal independent calibration/test sources
gives .0002758 and .00008761 as planning approximations. Simultaneous quantile ranks
are [989658,990340] and [998890,999107]. Exact final intervals, not these approximations,
control claims. We do not demand Task0034's unrelated 1e-4 absolute signal precision.

At 40000 signal groups, the worst-case unadjusted 95% efficiency halfwidth is .00490.
For NI paired variance .10, the conservative signal-bound halfwidth is about .00755;
for variance .02, .00391. Thus a reference efficiency .20 and compact .19 gives NI
excess .01; a normal approximation to the *declared conservative rule* gives about
94% conditional power. A .05/.05 pair with variance .02 gives excess .005 and
about 94% conditional power. A .05/.0475 pair has excess only .0025 and is poorly
resolved by that rule. Exact-bound/normal planning numbers are in the sidecar.
The sidecar's `conditional_normal_power` is the conventional z-rule comparison;
`conservative_rule_normal_power` approximates the actual declared bound rule.
Neither incorporates calibration uncertainty. These scenarios assume the specified paired variances and fixed thresholds;
calibration slope/atoms can reduce power further. No guaranteed positive result,
or power based on observed future discordance, is claimed. Larger effects, a clear
negative result or demonstrable simple-method dominance remain answerable.

## CPU cost, robustness and resources

Use the existing CPU runtime, one effective Torch/BLAS thread and zero loader
workers, pinning exact versions/build and queried thread control. Fresh owned worker,
one active worker at a time, no MPS/ONNX dependency, global host survey, idle-Mac
gate, background service or favorable-scheduling retry. No HDF/decompression/custody
work is inside the timers. Report two **directly measured** boundaries:

1. Owned contiguous standardized FP32 input → public score + two strict masks +
   owned outputs (algorithm only).
2. Provided in-memory object array → aggregates → frozen scaling → that same
   public score/masks/owned outputs (joint feature/preprocessing/algorithm).

Measure all eight streams at actual B1/B32/B512, 8 repetitions, 32 warmups and 128
timed calls per cell. Rotate fixed stream order by repetition index 0..7; use the
same hash-ordered 4096 development-background rows and schedule for every stream.
Record actual/padded shapes and tails, perf_counter_ns pairs, CPU time, own RSS and
all durations. No timer subtraction, best repetition or component sum. Shared rows
and serial timings are dependent; distributions describe this workload and host.
Primary cost is joint **B32**: compact/reference median paired-block ratio ≤.75 and
at least 7/8 block ratios ≤.80, averaging seed costs before arm comparison. This is
a practical reproducibility rule, not a p-value or universal latency bound.

Before timing, native reload and repeated B32 outputs must be bitwise equal.
Cross-shape B1/B512 reconstruction/score checks on the same 4096 development rows
use |difference|≤1e-5+2e-5 max(1,|reference|); count all decision mismatches.
A failing secondary shape is unqualified and excluded from performance claims;
it cannot alter canonical B32 science or relax its own tolerances. Failure of B32
reload/repeat/decisions stops the cost claim. Old 8-feature arithmetic bounds do
not automatically apply to a 12-feature, deeper network.

Predeclare rotation by .7 radians and beam reflection on 512 hash-first development
events and, only in Task0062, 512 final-background events. Check aggregate/standardized
features with atol/rtol 1e-5 after FP32, score tolerance as above, report all margin
and decision changes. A material required-identity failure is a validity stop;
within-bound near-threshold flips are reported numerical sensitivity. Profile final
background acceptance in MET bins [0,30,60,120,∞], lepton counts [1,2,≥3] and jet
counts [0,1,2,≥3], with denominators and small-cell suppression below 20. These are
descriptive bias/sculpting checks; missing per-process labels preclude SM-component
efficiencies. No subgroup metric selects a new model or cut.

The raw HDF arrays would occupy 1336539952 B at FP32 or 2673079904 B at FP64 using
published counts; dtype, chunking and auxiliary metadata are checked later. There
is no archive expansion. Read chunks, never load the entire HDF as in the authors'
unbounded example. Role feature matrices need about 112 MB at the selected counts;
fingerprints/index/sort scratch and scores are separately budgeted.

The whole new study gets **8 GiB storage**, **4 GiB own-worker RSS**, one active
worker, no background services. Allocate 45 minutes total acquisition, ≤20 minutes
per file and ≤6 transfer requests (at most one bounded transient retry per source,
no source substitution); wire cap 1 GiB. Preparation cap 30 minutes, each of six
neural fits 20 minutes, Task0061 total 4 hours. Task0062 total 2 hours, CPU measurement
20 minutes, cleanup reserve 10 seconds. These are ceilings, not measured durations.
Bound arrays before allocation and observe own resources externally. Stop on wall,
RSS or storage caps; retain partial receipts and consumed work. Do not apply old
32 MiB diagnostic limits or particle allowances as universal constraints.

Disable bytecode and pytest/Ruff caches; contain matplotlib/XDG/temp output under
the new owned root before imports. No old cache is deleted or retroactively charged.
Track **safety, source validity, experimental correctness and tooling accounting**
as separate outcomes. A bookkeeping gap is not automatically a changed score, but
it prevents claiming complete operational accounting. Cache hygiene never reaccepts
Task0058.

## Decisions, corrections and exact next stages

A positive compact result requires every primary gate above. A negative valid
result includes upper bounds excluding NI/utility, or no measured cost advantage.
Simple-selector dominance is actionable under its declared gates. Mixed efficiencies,
overlapping intervals, incomparable FPRs, missing fits/costs or inadequate unique
counts are inconclusive, with all arm/seed/topology outcomes published. Statistical
failure is not a software bug. No final cut is chosen to maximize SIC or rescue AUC.

Before freeze, correct implementation defects using generated fixtures, preserving
versioned code and all real activity; no extra fit/search is created. A final validity
failure stops evaluation and preserves exposure. Do not silently fix and rerun the
same exposed final population; a changed scientific procedure needs an explicit
prospective amendment and an appropriate still-protected population. Unused rows
are not an automatic retry allowance.

**Readiness:** source metadata, finite counts with margin, array sizes, algorithms,
endpoints, inference rules and bounded execution are substantively specified. The
protocol is ready for controlled Task0061 preparation, conditional on its explicit
ordinary payload/schema/unique-count checks. There is no essential unspecified
literature search, full-event adapter or native streaming prerequisite. This is not
local payload acceptance, an operational token or proof that all criteria will pass.
If v2 fails those checks, the narrowed deliverable is a source-validity/sample-size
failure with no scientific selector conclusion; no favorable dataset fallback is allowed.

Task0061 implements this small ADC adapter/role-separated pipeline, acquires only
these files, validates custody/content, prepares protected roles, performs finite
background-only training/selection/calibration and freezes the complete bundle.
Task0062 executes once against protected outcomes, performs the fixed robustness,
uncertainty and direct CPU comparison and reaches the supported positive, negative
or inconclusive conclusion. Routine fixes belong inside these two substantial tasks.

The motivation is consistent with [AE limitations](https://arxiv.org/abs/2104.09051),
[background-sculpting concerns](https://doi.org/10.1103/PhysRevD.107.114012) and the
value of [simple tabular competitors in a different weakly supervised setting](https://arxiv.org/abs/2309.13111).
Their reported performance does not transfer numerically to this study.
