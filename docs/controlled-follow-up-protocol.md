# Controlled activation follow-up and independent-confirmation protocol

Task0034, 2026-10-12 Europe/Rome. **Design only; conditional confirmation route.**
The actual starting state was clean `main`, empty index, tracking `origin/main`,
HEAD `c9f9bc5317f575ff2e29566214db20609745fcc1` (committed Task0033), memory1.28.
The memory's `a671b98` Task0033 base is historical task-time information, not the
current HEAD. The [actual prompt](prompts/0034-controlled-follow-up-protocol.md)
authorizes this design and metadata research, with zero operational numerical
access. The [sidecar](../configs/research/controlled_follow_up_v1.json) is explicitly
`design_only`: it is neither an execution plan, source acceptance, model freeze
nor authorization token. [Curated summary](../results/tables/final/task0034-controlled-follow-up-summary.json)
and [handoff](handoffs/0034-controlled-follow-up-protocol.md) bind the evidence and
checks. Task0035 has not started.

## Evidence and the single question

[Task0032](two-three-prong-synthesis.md) remains the completed frozen baseline;
[Task0033](exploratory-feature-score-diagnostics.md) remains accepted exploratory,
result-informed evidence. The following values are copied from its curated
[score marginals](../results/tables/final/task0033-score-marginals.csv),
[associations](../results/tables/final/task0033-feature-score-associations.csv) and
[tail counts](../results/tables/final/task0033-tail-counts.csv), without recomputation.

| AE population | Score median | Score p99.9 | Strictest original accepted/denominator |
|---|---:|---:|---:|
| Original test background | 1.237087 | 15.720911 | 116/150471 |
| Original two-prong signal | 2.008749 | 15.001871 | 56/100000 |
| Accepted three-prong signal | 1.576639 | 14.419351 | 34/100000 |

Higher signal medians coexist with background p99.9 above both signal p99.9
values. Signed eta associations coexist with centered marginal eta distributions;
they establish neither a symmetry defect nor a physics mechanism. PCA retains
six dimensions while the AE bottleneck has three, so the historical comparison
does not control compression rank. No correlation is promoted to feature importance.

The future primary question is: **Under a fixed background-only training
procedure, how does replacing the two ReLU activations with identity activations
change independently measured strict-tail signal acceptance and background
acceptance, at the same input representation, bottleneck dimension, layer
structure and parameter count?** A negative or inconclusive answer is useful.
Removing activations is not promised to repair the tails.

## Two arms and reproducible pairing

| Arm | Biased layer structure | Existing two hidden activation locations | Bottleneck | Parameters |
|---|---|---|---:|---:|
| Nonlinear aggregate AE | 8 → 6 → 3 → 6 → 8 | ReLU / ReLU | 3 | 155 |
| Linear aggregate AE | 8 → 6 → 3 → 6 → 8 | Identity / Identity | 3 | 155 |

Latent and output layers remain linear. The input is the same eight frozen
standardized FP32 aggregates: multiplicity, scalar pT, maximum pT, pT balance,
pT-weighted eta mean/spread, pT concentration and massless event mass. Retain
the accepted log transforms, scalers, feature order, equal event weights and
MSE reconstruction objective. There is no scaler refit, approximate inverse of
rounded inputs, particle representation, perturbation, feature removal, subgroup,
additional score or architecture in this comparison.

The exact starting recipe comes from
[AE v2 JSON](../configs/models/compact_autoencoder_v2.json),
[training source](../src/latenttrigger/training/autoencoder.py),
[background loader](../src/latenttrigger/training/background.py) and
[convergence contract](autoencoder-convergence.md): CPU, one native thread,
zero loader workers, deterministic algorithms, Adam learning rate0.001,
batch4096 including complete tails, maximum1000 epochs, patience15,
`min_delta=0`. Adam defaults verified in installed source text are
betas(0.9,0.999), epsilon1e-8, weight decay0, AMSGrad/maximize/capturable/
differentiable/decoupled-weight-decay false, foreach/fused unset. Pin exact future
runtime/build and resolved options; default changes must not pass silently.
Task0034 checked installed Adam source text and distribution metadata only:
Python3.12.12/Torch2.14.1; the source byte hash is in the sidecar. No Torch import
or model instantiation was needed.

Use exactly three paired seeds **1729,1730,1731**, at most six fits, in seed order
with nonlinear then linear. The historical JSON's seed1729 is the base recipe;
replace it by the prespecified seed for each pair. Create one default-PyTorch-
Linear FP32 weight/bias tensor document per seed, with fixed named layer order,
shapes and byte hashes; copy those same tensors into both arms before optimization.
Record Python/NumPy/Torch seeding and independent initialization/loader RNG streams.

The historical `RandomSampler` and `DataLoader` share one local CPU generator:
loader base-seed consumption is part of the recipe, and its state advances across
epochs. Reset that local generator to the same seed for each arm. Instrument the
actual sampler stream, without an extra RNG draw, and hash each complete epoch
permutation including its tail. Require equal initialization and permutation
hashes for every common epoch. Do not persist per-event permutation exports or
replace this recipe with an invented reseeding rule.

Each arm independently selects on background selection loss using strict
`loss < best_loss - 0`; ties retain the earliest checkpoint, fifteen consecutive
nonimprovements stop the fit. Restore and verify that arm's own selected state.
Different stopping epochs, or reaching the fixed1000 cap, are valid outcomes;
the cap does not establish convergence. Report all six fits and all seed-specific
results. No best-seed selection, weight averaging, ensemble score or signal-guided
checkpoint decision is permitted.

Forward arithmetic stays FP32; convert both inputs and reconstructions to FP64
**before** subtraction, then sum eight squared residuals. Require finite,
nonnegative FP64 SSE; higher means more anomalous. Equal dimensions and parameter
counts control specific differences, not every definition of expressivity. The
activation contrast includes interaction with optimization and background-only
checkpoint selection. It proves neither global optimization of the linear AE,
a causal physics mechanism, nor whether the aggregates discard particle information.

Historical AE v2 and PCA-six are frozen descriptive references with their original
thresholds. An optional **PCA-three** control is disabled by default. Existing
[PCA source](../src/latenttrigger/models/pca.py) stores all eight ordered full-SVD,
centered, nonwhitened axes and reconstructs `components[:k]`, supporting a derivative
from the first three accepted training axes and the same center. No numerical
component values were inspected here. Future byte/scientific identity, ordered
shape/finite/orthonormal verification, a separate derivative identity and its own
background calibration are prerequisites. No PCA refit. PCA-three versus PCA-six
addresses linear rank/compression; neither substitutes for the parameter-matched
activation comparison. Eight confirmation candidates are proposed by default,
nine maximum with this explicitly enabled control.

## Primary metadata research and conditional source choice

Retrieved2026-10-12 Europe/Rome. The
[source registry](../results/tables/final/task0034-confirmation-source-registry.csv)
has sixteen file-metadata rows across three version records, exact publisher
sizes/checksums/URLs, layout, lineage, exposure, proposed claims and missing facts.
All three publishers are Zenodo and all licenses are CC-BY4.0. Publisher checksums
are MD5 custody facts, not local SHA256 acceptance. **Zero sources accepted.**
No event file, key row, matrix, archive or per-event example was fetched.

| Route | Verified facts | Suitability and blockers |
|---|---|---|
| [Official LHCO v6, DOI10.5281/zenodo.4536624](https://zenodo.org/records/4536624) | Separate Pythia background file:1M events,2697677287bytes, MD5`f9ebde2e7739465902234ae73ec045e8`. BB1/2/3 each1M full reconstructed events; pT/eta/phi triplets,700-particle zero padding,2100 columns; public keys for BB1/3. | Standalone background independence from original R&D is unestablished. BB1 has834 signals; BB3 has1200 dijet+2000 trijet signals; insufficient for the prescribed precision. Changed masses/simulation and public keys prevent original challenge blindness or original topology replication. |
| [Extra QCD v2, DOI10.5281/zenodo.8370758](https://zenodo.org/records/8370758) |612858 events, SR only mJJ3.3–3.7TeV. `events_anomalydetection_qcd_extra_inneronly_4vecs_and_features.h5`:2665142971bytes, MD5`eecb8e30ef4efaa91e9530600370b54c`;2114 columns:2100 **px,py,pz** particle triplets plus14 jet fields. Publisher explicitly describes all event particles and original R&D simulation settings. | Preferred conditional background route. Cartesian units/dtype/precision, exact SR endpoints, generation run/seed provenance and overlap remain unverified. All-background label0 is a source role, not an appended truth column. The smaller14-feature-only file cannot construct the frozen eight inputs. |
| [Additional models, DOI10.5281/zenodo.18983506](https://zenodo.org/records/18983506) | Displayed v1; API version field absent. New signal generation is distinguished from derived EFP files of old R&D events. Conditional primary `XtoYYprime.tar.gz`:4924678720bytes, MD5`c75e84491ff7dc3695bb0986d31211c7`. MG5_aMC@NLO3.6.2 LO→Pythia8.313→Delphes3.5.0; parent3500GeV, daughters100/500GeV,2+2 topology, narrow hadronic decays. | Preferred conditional **single new signal**, based on structural compatibility and smallest model archive, not published performance. `events.h5` describes up to700 reconstructed **jet constituents**,2101 columns including label; full-event coverage is ambiguous. Raw Delphes ROOT is included but branch/export/toolchain compatibility and extracted sizes are unknown. Raw/selected signal count is undeclared. |

The [LHCO paper](https://arxiv.org/html/2101.08320) describes original R&D
Pythia8.219/Delphes3.4.1 and BB generator/tune/detector changes. BB1 uses masses
3823/732/378GeV and modified tracking/resolutions; BB2 is background-only Herwig++;
BB3's4200GeV graviton and2217GeV radion generate different dijet/trijet processes.
Those are not matched replicas of the original boosted two-/three-prong pair.
The uploaded BB1/BB2 detector cards have identical MD5 despite the paper's stated
differences; this metadata discrepancy is unresolved. The BB1 Delphes text card
was inspected; standalone Pythia card retrieval failed/timed out, so their exact
contents are not independently verified here.

The [additional-model paper](https://arxiv.org/html/2604.20965v1) describes the
new generation chain, default tune/R&D detector card, MPI off and analysis SR.
Its roughly20000 SR test signals are an analysis subset, not a declared source
total. The other new models (2+4,6+6,5+5) are not in the first experiment; there
is no post-result substitution. Derived `LHCO_2-prong_efps.h5` and
`LHCO_3-prong_efps.h5` still represent the permanently exposed original events.
Derived extra-background EFPs are the same extra QCD events, not another generation.
A new DOI, filename, representation, reshuffle or disjoint exact byte content
alone establishes no generation independence.

**Recommendation:** retain extra QCD plus newly generated XtoYYprime as a
conditional, signal-region transported-domain route. It can support fresh-
background stability and independent discrimination on that new signal only
after acceptance. It cannot establish replication of the original topology
difference; none of these records supplies the required matched independently
generated two-/three-prong pair. Fresh background with old exposed signals would
support new background-rate evidence only.

Before acquisition/preparation, require publisher-declared raw/selected counts,
generation seeds/run IDs and process/card hashes, explicit units/layout/dtype/
padding/overflow, full-event particle coverage, exact SR membership and jet
four-vector provenance, and bounded archive member/extraction sizes. Prefer a
publisher-supported full-event export; do not silently introduce a new ROOT
dependency or substitute selected-jet constituents. The future Cartesian adapter
must preserve the frozen [preprocessing contract](preprocessing-contract.md):
physical sort/wrap/cast conventions, massless all-particle aggregates, accepted
logs/scalers and FP32 outputs. Never invert rounded derived features.

Future separately authorized audit must bind exact source version/file size/
publisher checksum/local SHA256, labels/IDs/source order, within-source uniqueness,
and overlap with **every original1100000 training/selection/calibration/test row
and accepted100000 three-prong row**. Audit event IDs/run lineage plus canonical
particle fingerprints where representations permit. Cartesian conversion or
rounding can defeat exact-content matching: explain detection limits and require
generation evidence independently. Unexpected overlaps/invalid rows reject the
source; no result-dependent deletion or deduplication. No raw events or fingerprints
were opened to design this audit.

## Roles, embargo and calibration

This is a research sidecar; original evaluation-v1, preprocessing/model JSONs,
historical controllers, thresholds, accepted reports and synced `sources/` stay
unchanged. Proposed future original roles are699957 training-background,
74749 selection-background and74823 calibration-background. **Their reuse is
not authorized in Task0034.** No confirmation signal enters training, selection,
transformation choice, checkpoint selection or calibration.

Every restored/frozen new arm/seed receives exactly one original-background
calibration with NumPy `higher` quantile, index`ceil((N−1)*(1−alpha))` and strict
`score > threshold`. Primary alpha0.001; secondary0.01,0.05,0.1. Six new models
produce24 thresholds; optional PCA-three adds four. Old AE thresholds on a new
model are invalid calibration. References retain historical thresholds. Ties are
rejected. No confirmation-background adjustment of thresholds is allowed.

Freeze source eligibility, transformation, labels and SR rule **before numerical
payload audit**; seal accepted source identities and realized membership before
feature preparation. Use all eligible extra-background rows and all eligible
new-signal rows under the fixed SR rule, in complete source order, with no
score-dependent subset. Freeze all candidate checkpoints and thresholds before
any confirmation feature access/scoring. Maintain a separate durable embargo/
access ledger; label revelation follows checkpoint/threshold freeze. Public labels
do not make the original challenge blind. Original exposed test samples remain
historical exploratory context and are not rescored to show improvement.
The prospective new-signal rule is label1, anti-kT R1 leading-jet pT>1200GeV,
and **3300<mJJ<3700GeV**, using accepted publisher jet four-vectors or exact
membership. QCD label0 and its entire declared SR membership must agree with
this rule. Ambiguous units/endpoints/labels block source acceptance. Preparation
streams at most992raw rows per chunk; scoring uses4096row batches/complete tails,
without whole-event-table materialization or a new jet-clustering dependency.

The estimand is SR-conditional transport using original-background calibrated
thresholds. A need for domain calibration is a blocker, not permission to use
confirmation background. A separate disjoint domain-calibration role and a changed
estimand would require a prospective amendment before any confirmation scoring.
Design choices openly use Task0026/0031/0033 results; independent confirmation
does not erase that exploratory history or reblind any sample.

## Prospective outcomes and conditional uncertainty

Only XtoYYprime is the primary confirmatory signal, subject to eligibility and
sample sufficiency. At each model's own frozen alpha0.001 threshold, report
nonlinear-minus-linear paired TPR for each seed and their equal-weight mean
`Delta_S = (TPR_N,1729−TPR_L,1729 + TPR_N,1730−TPR_L,1730 + TPR_N,1731−TPR_L,1731)/3`.
Also report all six realized confirmation-background FPRs and their paired mean
contrast. All seeds, denominators, accepted counts, rates, secondary points and
frozen-reference results are mandatory; secondary comparisons are descriptive.
No AUC/AP, full curve, best threshold, ensemble or best-seed claim is needed.

For each independent source event define
`D_i = sum_s(A_N,s(i)−A_L,s(i))/3`, bounded[-1,1]. Record the64 six-bit primary
acceptance-pattern counts; these suffice for mean and unbiased sample variance
of D while preserving dependence across seeds/models on the same events.
Repeated predictions do **not** turn N events into3N independent observations.
No independence assumption across seeds/models or per-event bootstrap export.

Use the bounded-mean empirical Bernstein inequality of
[Maurer and Pontil,2009, theorem4](https://arxiv.org/pdf/0907.3740), with affine
scaling and a two-tail union bound. For N≥2 and range width R,

`h = sqrt(2*V*ln(4/delta)/N) + 7*R*ln(4/delta)/(3*(N−1))`,

where V is unbiased sample variance. Clip interval endpoints to the possible
mean range; precision gates use the **unclipped h**, preventing clipping from
artificially satisfying them. R=2 for paired D, R=1 for binary rates. Constant/zero-discordance
observations still have a positive width; N<2 is undefined and inconclusive.
Family error budget0.05 is allocated0.025 to the one signal contrast,0.0125 to
the background paired contrast and0.0125/6 to each of six background rate
bounds. Union coverage needs no independence among these statistics. Additional
signals would require a new prospective multiplicity allocation; they cannot
be added to the confirmatory family after viewing results.

Report separate individual Wilson95% intervals for conditional per-model rates,
and exact one-sided95% zero-rate upper bounds where applicable. Individual
Wilson overlap/nonoverlap is not the comparison test or a simultaneous claim.
Inference is conditional on frozen models/thresholds and independently generated,
i.i.d. events. Calibration, training-seed population and simulation uncertainty
are not included; three fixed seeds describe those models, not all optimizer
initializations. If generation dependence invalidates i.i.d. assumptions, retain
descriptions and withhold the confirmatory claim pending a prospective method.

| Prespecified gate | Numeric decision |
|---|---|
| Background stability | Every one of six simultaneous FPR intervals lies wholly in[0.00075,0.00125]; paired mean nonlinear-minus-linear FPR upper bound≤0.0001. |
| Precision | Signal-contrast halfwidth≤0.0001; paired-background halfwidth≤0.0001; each background-rate halfwidth≤0.0002. |
| Practical signal advantage | Primary Delta_S lower bound>0.0002, together with all source, lifecycle, background and precision gates. |
| Negative/inconclusive | With gates and precision satisfied, upper Delta_S<0.0002 excludes the specified practical nonlinear advantage. Upper<−0.0002 plus background paired lower≥−0.0001 supports the symmetric linear advantage. Interval wholly inside±0.0002 supports practical equivalence. Otherwise report inconclusive; a failed background gate is explicitly a stability failure. |

These are benchmark choices:25% tolerance around target FPR, maximum incremental
background0.1alpha, absolute signal improvement20 events/100000, and precision
half that practical difference. They are not physical trigger-rate or purity
requirements. All results are reported even when a gate fails. A missing model,
failed lifecycle/source gate, incomplete six-fit set or insufficient precision
precludes improvement claims; no retuning, retry or favorable-point selection.

## Planning resolution, not scientific measurement

The sidecar contains35 N/rate sensitivity cases (rates0.0001,0.0005,0.001,0.005,0.01),
28 paired-variance cases and five minimum-N solves. `N*alpha` below is a background
planning expectation, not an observed count. Signal acceptance is unknown.

| N | Expected background count at alpha0.001 | One-event resolution | Expected signal counts at hypothetical rates0.0001 /0.001 /0.01 |
|---:|---:|---:|---:|
|834|0.834|0.001199|0.0834 /0.834 /8.34|
|2000|2|0.0005|0.2 /2 /20|
|20000|20|0.00005|2 /20 /200|
|100000|100|0.00001|10 /100 /1000|
|612858|612.858|0.000001632|61.2858 /612.858 /6128.58|
|1000000|1000|0.000001|100 /1000 /10000|

For example, binomial planning SE at N20000,p0.001 is0.0002235; the normal95%
halfwidth approximation0.000438 is a planning approximation, not an observed
interval. At612858,p0.001 the proposed simultaneous background EB halfwidth is
about0.0001858, below its precision cap at this assumed variance; source, actual
rate and calibration gates can still fail. Original calibration has expected
tail74.823 and event resolution1/74823; it is not infinitely precise.

For paired signal precision, let q bound V(D), without assuming seed independence.
Planning minimum N for h≤0.0001 at delta0.025 is:

| Assumed variance upper q | Required new independent signal events |
|---:|---:|
|0.0002|579973|
|0.001|1450034|
|0.002|2481145|
|0.01|10618749|

These are conservative variance scenarios, not power or yield guarantees.
Even at zero observed variance the bound needs at least236843 events;
at20000 its additive halfwidth floor is0.0011843. Thus the black-box signals and
the paper's20000-signal analysis subset cannot meet this protocol's precision.
The proposed additional-signal raw/selected count is unknown: **confirmation
readiness is blocked**, not assumed from a similarly named topology. Counts beyond
the prospective4M signal cap or storage bound require another source/resource
decision before acquisition. No extrapolation into an unobserved tail, discovery
significance, physical trigger rate or deployment-purity claim.

## Smallest future implementation and bounded campaign brief

**Task0035 proposal, synthetic only:** add the minimal separate research
schema/factory and adapters to existing utilities, without changing historical
validators. Implement the two activation arms, named initialization copying,
actual loader-permutation proofs, own-best-state restore, exact FP64 SSE/
`higher`/strict decisions, shared-event pattern arithmetic and bounded mean
intervals. Synthetic tests must cover pairing/divergent stops, ties, seed
dependence, zero/constant cases, interval scaling, multiplicity, role/source
allowlists and lifecycle failure. Use current-source synthetic acceptance and
one bounded native synthetic integration, with continuous suspension, assertion
failure/loss/release, normal exit/reaping and parent acceptance. No real source,
fitting, scoring or acquisition is needed to make this software reviewable.
The old1728-test Task0033 acceptance does not cover new research code.
Propose one native synthetic worker≤60s, whole≤120s including≤15s finalization,
cleanup2s inside the worker cap,1GiB RSS/512MiB native/128MiB parent,64MiB journal /
1MiB log/128MiB total storage and at most two synthetic optimizer steps per
arm/seed. These are implementation-test caps, not training-time estimates or an
execution grant. Portable lifecycle tests use simulated clocks/assertions.

The future phase order is: software acceptance → freeze source/dependency map
and background-only plan → separate authorization → durable attempt reservation
→ three paired initializations → six sequential fit/restore workers → six own
calibrations (seventh only for enabled PCA-three) → checkpoint/threshold freeze
→ aggregate background report and parent acceptance. Confirmation is a separate
source/acquisition/overlap/embargo/plan/authorization campaign, followed by fixed
preparation → one numerical worker with up to nine sequential candidate phases
→ aggregate-only analysis → parent
acceptance. A body-complete receipt is not acceptance: normal exit, reap,
source/output identities, resource/deadline checks and final publication checks
must all pass. Failed attempts retain partial evidence, consume their scope and
stop; no automatic retry, reset or historical campaign replay.
Retain only each arm's current best checkpoint and the fixed initialization
documents, with atomic replacement; log epoch/permutation/state hashes instead
of accumulating checkpoint tensors or row lists. Reserve storage globally before
dispatch and enforce it across worker journals, parent ledger and owned outputs.

Numeric ceilings are **proposals**, derived from the relevant curated evidence,
not current measurements or authorization:

| Future scope | Proposed ceilings and basis |
|---|---|
| Six-fit background development |60s prerequisites,60s initialization,900s/fit,120s/calibration (6default/7max),60s freeze,120s report,15s finalization; whole6600s. Max phase sum6555s leaves45s. |
| Training projection |Task0008 measured396epochs,59.700382250/59.063456375s training,66.846885583/66.036752583s core; `4*max(training)/396*1000 =603.034s/fit`. Factor4/linear scaling are assumptions; identity-arm/guarded costs unmeasured. |
| Fit resources/storage |3GiB worker RSS,512MiB native reservation,128MiB controller,1GiB reporting;1GiB development storage;64MiB guard journal and1MiB text log per worker. Task0008 peaks2051489792/2553315328bytes were legacy broad-store RSS, not native reservation. New narrow-reader/native feasibility must pass acceptance. |
| Conditional confirmation envelope |60s prerequisites; two sources each600s audit plus600s preparation;600s/candidate (9max) within one5400s numerical scoring worker;120s aggregates;15s finalization; whole8400s (phase sum7995s). Signal cap4M, background612858. No campaign is ready/granted. |
| Confirmation projection |Task0031 accepted parent preparation13.821576s and max PCA/AE dispatch2.452941s at100000events. Assumed2× preparation scaling to4Mraw rows gives1105.726s/source for audit+prepare; assumed4× scoring at4612858total rows gives452.603s/candidate. Different formats/audits/guards and ownership costs remain unknown. |
| Acquisition/storage prerequisites |Selected raw files total7589821691bytes (~7.59GB decimal). Provisional16GiB working-storage cap,20GiB free-disk admission,7GiB selected archive extraction. Expanded ROOT/HDF members and actual counts are unknown and can invalidate this envelope. Transport deadline/request budget is unassigned and must be separately specified/authorized before acquisition. |

Cleanup2s is **inside** every worker ceiling; operate before cap minus cleanup.
Reuse Task0030's continuous clock and scoped temporary owned idle-system-sleep
assertion, verify it before reservation/during stages and verify release on all
exits; permit display sleep, change no persistent power settings. Explicitly
enforce process-specific RSS/native/controller ceilings, guard journal and log
bounds. WARN is advisory, CRITICAL and invalid primary accounting veto; unavailable
pressure and monitoring gaps/overshoot are disclosed. Global available RAM is
context only. No idle-Mac window, app closure, readiness polling or monitor project.
No training allowance is inferred from Task0033 timing or the consumed particle
budget. Particle192/192 canonical deferral and Task0025's failed process-exit
supervision remain unchanged.

Proposed development accounting: six workers each read train+selection once,
12 feature-population requests/4648236 rows; six calibration requests/448938
rows,24 thresholds. Each worker's three original membership arrays total3.3M
metadata records:19.8M for fits and19.8M for default calibrations. Optional PCA-three
adds one request/74823 rows/3.3M metadata records/four thresholds. Maximum training
updates1026000 (171batches×1000epochs×6); maximum repeated train/selection
presentations4652884236 includes one post-restore pass per role/fit. These are
ceilings, not actual accesses. Hash/header custody, membership, feature loads,
in-memory epoch presentations, score computations, overlap/fingerprint work and
aggregate reporting require distinct ledger entries. Narrow role adapters must
avoid broad `ProcessedStore` construction or whole-store copying.

The confirmation numerical worker should load its two prepared feature populations
once and retain owned bounded arrays for all8default/9maximum candidates; the
stdlib128MiB parent owns metadata only (at the population cap, FP32 feature buffers
alone total147611456bytes). Each600s candidate phase and the5400s worker deadline
are checked continuously; normal worker exit/reap precedes acceptance of all
candidate outputs. The longer numerical worker has an explicit512MiB guard-journal
cap; other workers retain64MiB. Neither ceiling is a claim that the future trace
will fit: current-source bounded serialization/storage acceptance is required.
Accumulate six primary acceptance bits in owned buffers and emit only64pattern
counts, then discard event buffers; aggregate reporting reopens no arrays.
Separately account
`N_BG+N_SIG` feature rows and `M*(N_BG+N_SIG)` forward presentations, complete
batch tails, source metadata/audit passes and any local owned-buffer rereads.
No old stored scores, event exports, ensemble score or copied full processed
store. Reporting consumes owned aggregates only. Implementing, acquiring,
background development and independent confirmation require separate scopes;
an unready source grants none of the others.

## Task0034 actual access and validation

Nineteen logical web URL open/click attempts plus five bounded publisher HTTP
GET attempts were made; six additional text-find operations used retrieved pages.
Sixteen URL/GET responses succeeded, eight failed (including429/unavailable web
API/card responses and two timed-out Pythia text cards). Three accepted publisher
JSON bodies total30856bytes; primary paper/site/Delphes-card text was inspected.
Physical web/cache request count is unavailable. These are metadata/text requests,
not event-payload downloads. API metadata resolved the extra-background record
after the web429. Missing card/version/count facts remain marked unknown.

Temporary boundary-limited authoring/check scripts use only allowlisted curated
tables, configuration/source text, publisher JSON and hypothetical arithmetic.
Nineteen synthetic assertions,35 rate scenarios,28 variance scenarios and five
minimum-N solves check parameter count, variance/range/dependence, positive
zero-variance width, family budget, minimum solutions, roles and projections.
CSV full-grid authoring/roundtrip, JSON/link/coverage/consistency, byte-preservation
and Git checks are recorded in the handoff. No new tracked helper/dependency,
controller, scientific plot, heatmap repair or operational suite rerun.

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
new_operational_population_requests_in_Task0034: 0
new_feature_rows_read_in_Task0034: 0
new_stored_score_array_loads_in_Task0034: 0
new_membership_or_fingerprint_numeric_loads_in_Task0034: 0
new_model_forward_calls_in_Task0034: 0
new_reconstruction_computations_in_Task0034: 0
new_calibration_or_scientific_evaluations_in_Task0034: 0
optimizer_updates_in_Task0034: 0
event_payload_downloads_in_Task0034: 0
```

The YES values preserve historical permanent exposure. The concrete next decision
is whether to authorize **Task0035 synthetic-only implementation** of this
comparison and uncertainty arithmetic. Training awaits new software acceptance
and its own plan/authorization; confirmation additionally awaits independent,
full-event, sufficiently large source evidence. None has been launched.
