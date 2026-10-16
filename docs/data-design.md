# Data foundation and dataset design

Task 0002, 2026-10-04. **Status: design decided; pipeline not implemented.**
No event-data file has been downloaded or inspected. Source facts below were
verified from primary documentation and small metadata responses. Split rules,
schemas, transforms, and benchmark boundaries are RareGate design decisions,
not claims about implemented features or measured results.

> How much anomaly-detection performance can be retained when machine-learning
> models are optimized for real-time LHC event selection under strict
> computational constraints?

## 1. Primary dataset and exact components

Select **LHC Olympics 2020 (LHCO), R&D dataset, Zenodo record v5**,
DOI [10.5281/zenodo.6466204](https://doi.org/10.5281/zenodo.6466204).
Use `events_anomalydetection_v2.h5` as the particle-level source for initial
development and the primary evaluation. Pin this version DOI, not a floating
`latest` URL or an older R&D raw file.

The [v5 correction notice](https://zenodo.org/records/6466204) explains that older
raw events did not match the v2 QCD generation threshold and published features.
The corrected file uses a 500 GeV generator-level threshold to reduce artificial
trigger sculpting. Mixing old particles with v2 features would invalidate joins.

The [R&D record](https://zenodo.org/records/4536377) describes 1,000,000 QCD events
and 100,000 two-prong signal events from a heavy resonance decaying through two
intermediate particles. It uses Pythia8 and Delphes 3.4.1, without pileup or
multiple parton interactions. The resonance/intermediate masses are 3.5 TeV,
500 GeV, and 100 GeV. The selection is a fat-jet trigger; see the
[challenge documentation](https://lhco2020.github.io/homepage/) for the anti-kT
R=1, jet pT > 1.2 TeV and |eta| < 2.5 requirements. These are jet requirements,
not a 1.2 TeV cut on each particle.

Access is public. Zenodo's [v5 API metadata](https://zenodo.org/api/records/6466204)
specifies **CC BY 4.0**; retain attribution and DOI in future manifests and
publications. The repository's MIT license does not relicense the dataset.
The benchmark paper is [Kasieczka et al., arXiv:2101.08320](https://arxiv.org/abs/2101.08320),
journal DOI [10.1088/1361-6633/ac36b9](https://doi.org/10.1088/1361-6633/ac36b9).

The following are publisher metadata, not locally computed hashes or sizes:

| Component in pinned record | Bytes | Published MD5 | RareGate role |
| --- | ---: | --- | --- |
| `events_anomalydetection_v2.h5` | 2,908,260,409 | `629789d55813be3860781b084ae7f1de` | Initial particle source; split background and reserve signal for testing. |
| `events_anomalydetection_v2.features.h5` | 74,315,238 | `271cf5e71fc756b2a8d2b32730689bdb` | Optional later cross-check; not the primary model input. |
| `events_anomalydetection_Z_XY_qqq.h5` | 235,488,994 | `54e123a86143b668f9cb76905152a124` | Additional three-prong signal; reserve for later frozen-model evaluation. |

Sizes/checksums come from the [pinned API record](https://zenodo.org/api/records/6466204).
Initial source download is approximately **2.91 GB decimal**, not the size of its
expanded arrays. Future acquisition can use the record's individual HTTPS file
link or API `files[].links.self`; validate expected bytes/MD5 and compute SHA-256.
No downloader or download command is implemented in this task.

The raw R&D schema is a shuffled table with 700 zero-padded `(pT, eta, phi)`
triplets followed by a truth label, nominal shape `(1,100,000, 2101)`. Label 0 is
background and 1 is signal; particle charge/type is absent. Published jet-feature
rows are intended to align with the corresponding corrected raw file; verify
alignment after acquisition rather than assuming it from row count alone.
[R&D schema and feature documentation](https://zenodo.org/records/4536377)

Reserve **all three black boxes** and their separately supplied background MC
for a later domain-shift/blinded-protocol task, not initial fitting or tuning.
The [black-box record v6, DOI 10.5281/zenodo.4536624](https://zenodo.org/records/4536624)
has one million events per box, 2100 particle columns, and files of approximately
2.6, 2.2, and 3.5 GB. It warns of simulation differences. BB1/BB3 answer keys are
now public; therefore future work can enforce an internal evaluation embargo but
must not claim the original challenge's genuine blindness. This task read
metadata about key availability, not the keys or event-level answers.

## 2. Candidate comparison

These alternatives differ in data level and analysis scope; LHCO and Dark
Machines are distinct benchmarks, not interchangeable releases of one dataset.

**Dark Machines, Unsupervised-Hackathon**,
[DOI 10.5281/zenodo.3961917](https://zenodo.org/records/3961917), is the credible
compact alternative. Its open CC BY 4.0 tar archive is 2,084,311,040 bytes;
the generation archive [10.5281/zenodo.3685861](https://zenodo.org/records/3685861)
is about 31.2 GB and should not be confused with the hackathon subset.
[API license/size verification](https://zenodo.org/api/records/3961917)

The [original Dark Machines paper, section 2](https://arxiv.org/html/2105.14027v3)
describes 13 TeV fast simulation, typed reconstructed objects and event-level
missing transverse quantities in variable-length CSV rows. Object fields are
energy, pT, eta, phi; energy/pT use MeV. Process IDs/weights are metadata, not safe
model inputs. Background counts in channels 1/2a/2b/3 are 214,185 / 20,005 /
340,268 / 8,544,111, with separate signals. The full generation exceeds a billion
events; that is not the hackathon count. Multiple channels, selections, units,
and process mixtures need careful harmonization. Its public labeled subset is
appropriate for background-only learning; the separate secret benchmark requires
its own evaluation arrangement. Paper DOI:
[10.21468/SciPostPhys.12.1.043](https://doi.org/10.21468/SciPostPhys.12.1.043).

**CMS JetHT Run2016H NanoAOD**,
[record 30558, DOI 10.7483/OPENDATA.CMS.8ALJ.MQSO](https://opendata.cern.ch/record/30558),
provides real, trigger-selected 13 TeV collision events: 124,050,331 events,
72 files, 145.3 GiB, publicly available under CC0. HTTPS/XRootD access is offered.
Certified run/luminosity selections must be applied. It has no per-event
BSM truth labels; a detection-quality benchmark would additionally need matched
simulation, injections, or a separately justified known-process proxy.

[NanoAOD documentation](https://opendata.web.cern.ch/docs/cms-getting-started-nanoaod)
confirms standard ROOT TTrees can be read with Python `uproot`/`awkward` without
requiring CMSSW or a container. Standard NanoAOD omits the full Particle Flow
candidate collection; higher-level object sets remain available. The
[record's variable list](https://opendata.cern.ch/eos/opendata/cms/dataset-semantics/NanoAOD/30558/JetHT_doc.html)
lists jets, fat jets, leptons, MET, and trigger fields. A future analysis must
handle overlapping objects, trigger selections, calibration, and data/simulation
differences. CMS realism is valuable but does not make this a ready labeled
anomaly benchmark.

The following assessments are project judgments based on those facts:

| Criterion | LHCO R&D / later black boxes | Dark Machines hackathon | CMS JetHT NanoAOD |
| --- | --- | --- | --- |
| Scientific relevance | Explicit multijet anomaly challenge; narrow simulated topology. | Broader SM/BSM processes and selected channels. | Real detector data; anomaly ground truth needs additional design. |
| Trigger relevance | Preselected independent events support a synthetic stream. | Object-selected events support a synthetic stream. | Already-triggered collision events; preserves experimental selection effects. |
| Representation | Particle triplets support low-level sets; no type/charge. | Typed high-level object sets, fewer objects. | High-level objects; no full PF collection in standard NanoAOD. |
| Unsupervised suitability | Truth identifies pure background; signals can be embargoed. | Background mixtures plus separate signal files. | No guaranteed pure labeled background or anomaly sample. |
| Scale | Million-event background; enough distinct events to develop streaming tests. | Millions across channels; full archive much larger. | Very large, but extra realism increases workload. |
| Local feasibility | One ~2.91 GB source; bounded processed subset and chunked conversion needed. | ~2.08 GB archive feasible; channel parsing adds scope. | Selected files feasible; full 145.3 GiB release is unnecessary locally. |
| Reproducibility | Pinned corrected DOI, metadata/checksums, documented simulation. | Pinned DOIs; must record channel/process/selection choices. | DOI plus certified runs, corrections, and analysis configuration. |
| Model compatibility | Shared particles can derive aggregate baseline/AE and set views. | Good for compact object models; different low-level question. | Models possible after a detector-analysis contract is established. |
| Hardware benchmarking | Canonical tensors can be preloaded and reused. | CSV must first become deterministic tensors. | ROOT analysis must first become deterministic tensors. |

**Decision rationale:** choose LHCO R&D for a manageable, labeled particle-level
starting point with a shared source for every model family. Dark Machines remains
a strong later cross-benchmark, especially for compact typed-object workloads,
but adds multi-channel design now. CMS remains a later realism check; its absence
of anomaly labels and analysis obligations distract from the initial ML/systems
comparison. Do not use black boxes as the initial tuning population.

LHCO's lack of pileup/MPI, limited signal families, preselection, massless
approximation, and source particle ceiling restrict conclusions. It does not
validate operation at an LHC trigger stage, real event rates, detector readout,
or discovery significance. The original challenge's resonance-search protocol
differs from our labeled event-score evaluation; results must state this.

## 3. Formal ML task

For event e, define the unordered collection

\[
X_e=\{x_{ei}\}_{i=1}^{N_e},\qquad
x_{ei}=(p_{T,ei},\eta_{ei},\phi_{ei}),\quad N_e\leq700.
\]

Here N_e counts stored valid particles after removing padding, not partons, jets,
or all particles that might have existed before the source ceiling. Treat each
event as one arrival in a future synthetic stream; its row number is not a time.
The label y_e in {0,1} is metadata kept separate from inputs.

Let P_B denote selected simulated QCD events and P_S the selected two-prong
resonance sample. Fit a score a_theta(X), larger for more anomalous events, with

\[
\theta^*=\arg\min_\theta
\mathbb E_{X\sim P_B^{\rm train}}[\mathcal L_\theta(X)].
\]

The loss will depend on the later baseline/model. No signal participates in
fitting, normalization, early stopping, or hyperparameter selection. Test on
held-out background versus the two-prong signal; separately evaluate the
three-prong sample only after freezing a model in its later evaluation task.
These are held-out examples/topologies, not proof of sensitivity to every unseen
physics model. Pure-background training is an idealized initial protocol.

Report future score quality with ROC AUC and signal acceptance at predeclared
background acceptance alpha. Set the deployment-like threshold using validation
background, then report achieved test-background acceptance and test-signal
acceptance, with finite-sample uncertainty. Alpha=10^-3 is an initial evaluation
target, not a measured result: approximately 150,000 test-background events would
give only about 150 expected tail events there, and about 15 at 10^-4. Do not
claim precise extreme-rejection performance from insufficient test statistics.
Signal/background ratios used for PR metrics or a synthetic stream must be stated;
the released sample's class ratio is not a physical collision rate.

## 4. Deterministic population and split contract

Protocol name: `lhco-rd-v1`; seed: **1729**. The organizers provide R&D data for
development and black boxes for the challenge, not a prescribed 70/15/15 R&D
partition. Retain those roles; the following partition is RareGate's own.

1. Audit source schema/labels and create duplicate groups before selecting any
   subset or fitting statistics. Preserve source row ordinals. A duplicate
   fingerprint excludes label, split, source ID, and learned statistics. Remove
   verified padding, wrap angles to [-pi, pi), canonicalize signed zero, sort
   triplets lexicographically, and hash their count plus little-endian float64
   values with SHA-256 before any float32 rounding. Do not round to deduplicate.
   Verify the source precision supports this encoding in the schema audit.
2. Group exact repeated payloads, including across supplemental files. Keep one
   representative selected by sorted source-ID/row order and record all aliases.
   Quarantine groups with conflicting truth labels. Flag potential near-duplicates
   for a documented integrity audit; do not silently erase similar physical
   events. Disjoint row IDs alone are not proof of disjoint event content.
3. For each retained background group g, compute SHA-256 of the UTF-8 string
   `lhco-rd-v1|1729|bg-split|` followed by its lowercase fingerprint hex. Interpret
   the first eight digest bytes as an unsigned big-endian integer k and use
   u=k/2^64. Assign train for u<0.70, validation for 0.70<=u<0.85, and test otherwise.
   This avoids reliance on Python's randomized `hash()` or file traversal order.
4. Split validation background in half using an independent `val-role` hash domain
   with the same seed/group fingerprint: u<0.5 for model selection/early stopping,
   otherwise threshold calibration. Freeze assignments in a local manifest.
5. Allocate **all two-prong signal** to `test-signal-2prong`, and all supplemental
   three-prong signal to `reserved-signal-3prong`. Neither becomes validation data.

Background fractions are expected **70% train / 15% validation / 15% test**;
nominal counts before integrity exclusions are 700,000 / 150,000 / 150,000.
Hash assignment is deterministic but not guaranteed to yield those exact counts.
Record actual counts and duplicate exclusions. This is population-separated by
truth class, not a stratified random shuffle of a signal-contaminated mixture.
No kinematic stratification is imposed initially: random background assignment
preserves its distribution in expectation. Compare train/validation distributions
without inspecting final-test physics distributions during model development.

## 5. Leakage and embargo rules

| Population | Permitted learned quantities / use | Forbidden use |
| --- | --- | --- |
| Training background | Transform/scaler statistics, baseline/model fitting, training-only multiplicity decision, later quantization calibration. | Signal-dependent weights, synthetic label features. |
| Selection-validation background | Background loss for early stopping; validate predefined numerical/retention criteria. | Refitting scalers, optimizing ROC/AUC on signal. |
| Calibration-validation background | Set score thresholds for predeclared acceptance targets after model selection. | Choosing the winning model by its test-signal performance. |
| Test background and two-prong signal | Evaluate once protocol, views, hyperparameters, and thresholds are frozen. | EDA to tune features/cuts/truncation, training statistics, hyperparameter selection. |
| Three-prong / black boxes | Reserved later evaluation of frozen models/protocols. | Training, normalization, tuning against answer keys or published solutions. |

An integrity-only custodian/pass may read structural metadata, labels for
allocation, and hashes to prove disjointness; it must not feed test distributions
or scores back into model design. Physically motivated fixed transforms are
specified before reading test content. Fit normalization only on valid training
objects/events, excluding padding and signal. Save and reuse fitted statistics.
No full-dataset scaler, test-informed clipping, or signal contamination is allowed.

Freeze comparison configurations and the intended model list before releasing
final labels to the evaluation code. If test results motivate another design,
report the previous exposure and use a new predeclared evaluation population;
rerunning the same exposed set cannot restore its status as an untouched test.
Investigations of signal contamination belong to a separate future experiment.

## 6. Features and shared representations

Canonical content retains physical `(pT, eta, phi)` and valid multiplicity.
Model inputs exclude truth labels, row IDs, fingerprints, filenames, split names,
and signal topology. There is no measured type/charge category to encode; do not
invent particle IDs. Future typed-object datasets would require a new schema.

| Selected raw field | Meaning / units / range | Intended handling |
| --- | --- | --- |
| pT | Transverse momentum; canonical unit GeV in natural units. Valid particles have pT>0; zero marks padding. No individual-particle upper bound or empirical quantiles verified. | `log1p(pT / 1 GeV)` in learned object views; training-valid-object mean/std scaling. Retain physical pT for derived features. |
| eta | Pseudorapidity `-log(tan(theta/2))`; dimensionless, signed, not periodic. Detector acceptance bounds and actual tails require audit. | Training-valid-object mean/std scaling; no invented eta cut. |
| phi | Azimuth; radians, periodic modulo 2pi. Canonical interval [-pi, pi). | Wrap with a fixed rule; input `sin(phi), cos(phi)` in [-1,1], without independent learned scaling. Never standardize the discontinuous raw angle as a line. |
| truth bit | 0/1 background/signal, dimensionless categorical evaluation metadata. | Separate label array; never pass to a model or scaler. |

GeV is the intended Delphes-compatible convention, not a locally inspected HDF
header. Confirm file units against the generation configuration/numerical scales
before release. The official examples show the triplet layout; this task has not
audited raw dtypes, actual padding, or ranges. Any unit conversion must be fixed,
recorded, and applied identically to every population.

Proposed model-specific views, all derived from the same particles and event IDs:

- **Statistical baseline:** an eight-dimensional event vector
  `(N, S, pT_max, R, eta_mean, eta_rms, C, M)`.
  Here S=sum(pT), R=|sum(pT*(cos(phi),sin(phi)))|/S,
  eta_mean=sum(pT*eta)/S, eta_rms=sqrt(sum(pT*(eta-eta_mean)^2)/S),
  and C=sum(pT^2)/S^2. R and C are dimensionless; M is the invariant mass of
  the sum of massless four-vectors with E=pT*cosh(eta), pz=pT*sinh(eta).
  Momentum/mass use GeV; N is a count. For valid events S>0, R is in [0,1]
  up to numerical tolerance, C is in [1/N,1], and eta_rms/M are nonnegative.
  M requires finite-value/precision checks; a materially negative mass-squared
  is an error, not a value to silently clamp. Only numerical roundoff within a
  documented tolerance may be clamped. Empty/corrupt events are quarantined.
- **Compact autoencoder:** initially use the same eight aggregates to isolate
  modeling differences from information differences. Apply log1p to N, S,
  pT_max, and M using declared count/GeV units; scale all aggregate channels
  with background-training statistics. A later ordered-object AE is a separate
  view/experiment and must disclose its information and latency cost.
- **Particle/set architecture:** use N-by-4 channels
  `(scaled_log_pT, scaled_eta, sin(phi), cos(phi))`, with padding/masks at batching.
  Normalization weights valid training particles equally; record this choice.
  Preserve the physical event scale through pT inputs; do not quietly normalize
  every event to unit sum and discard scale. No absolute-index positional
  embedding is planned for a permutation-invariant set model.

Aggregate features here need no jet clustering. Published jet/substructure
features are an optional later reference; adopting them changes both available
information and preprocessing cost and needs a separate documented comparison.
All families share population, splits, quality rules, and evaluation thresholds.
Comparisons across different views measure both representation and model effects;
do not attribute every improvement solely to architecture.

## 7. Multiplicity, ordering, masks, and latency

Verify zero-padding convention and retain valid particles with pT>0; nonfinite or
negative pT and inconsistent zero triplets require explicit quarantine/reporting.
Canonical records remain ragged and preserve every stored particle. **700 is a
source storage ceiling, not an empirically chosen model sequence length.**

Sort model views by descending pT, then eta, wrapped phi, and original slot for
ties. Sorting is a reproducibility convention; a masked set model should remain
invariant to jointly permuting objects and masks. Mask=True denotes a real
particle. Pad after transforms with zero tensors; masks must exclude padding
from attention, pooling, loss, and scaler fitting. Zero-valued physical eta/phi
is not itself evidence of padding.

Defer the model maximum length L to training-background EDA. Default to no
additional truncation if feasible. If a smaller L is necessary, examine training
multiplicity quantiles, lost-particle fractions, and lost scalar-pT fractions
when retaining the largest-pT particles. Predeclare tolerances and hardware
budget, choose the smallest L satisfying them, and confirm only on background
selection-validation data. Freeze L before signal/test inspection. Later report
class-dependent truncation effects as evaluation findings, not tuning signals.
Record n_original, n_kept, and lost scalar-pT fraction for truncated views.

Dynamic batch padding minimizes work but makes latency multiplicity-dependent;
fixed L makes workloads explicit and predictable but wastes work on padding.
Benchmark both only with declared shapes/multiplicity distributions and consistent
masks. Do not hide truncation or padding changes inside an optimized runtime.

## 8. Canonical schema and storage direction

Conceptual per-event contract (`schema_version: lhco-event-v1`, not implemented):

```text
event_id: <version DOI>/<source filename>/<zero-based source row ordinal>
duplicate_group_id: SHA-256 of canonical raw particle payload
objects:
    physical_features: float32 [N, 3]  # pT_GeV, eta, phi_rad
    n_objects: integer                # every stored valid particle
event_features: float32 [8]            # specified physical aggregates
label: uint8                          # evaluation-only, separate storage
metadata:
    source_file_id, source_row, split, validation_role, manifest_id
```

Float32 is the intended canonical payload after a float64 computation/precision
audit; preserve original files and pre-rounding fingerprints. No lossless
precision claim is made yet. A derived padded view adds `[L, F]` features and a
boolean `[L]` mask without altering the canonical source. Its view/configuration
and scaler identifiers must travel with every model/runtime artifact.

| Format | Suitability for this contract | Decision |
| --- | --- | --- |
| Parquet / nested Arrow | Portable ragged tables and compression; conversion to dense model tensors and a new dependency. | Defer; useful later if analysis interoperability requires it. |
| HDF5 | Natural input format, compression and chunking; raw pandas layout may need pandas/PyTables. | Keep original unchanged; inspect layout before choosing reader dependencies. |
| Compressed NPZ | Convenient small archives; compression prevents direct mmap of array payloads. | Not the default processed/benchmark store. |
| Uncompressed NPY arrays + JSON manifest | Existing NumPy dependency, primitive dtypes, memory mapping; ragged offsets avoid global padding. | Intended initial processed format. |

Use separate NPY arrays: `objects [sum(N),3]`, `offsets [events+1]` (int64),
`event_features [events,8]`, source-file IDs, source-row ordinals, split/role codes,
and fingerprint bytes. Keep labels in a separate evaluation array. A JSON
dictionary maps source IDs and split codes; event IDs derive from it and row
ordinals, avoiding pickled object arrays. Load with `allow_pickle=False` and
`mmap_mode='r'` where appropriate. This is an intended layout, not a new loader.

File/shard sizes, raw reader, and final float32 error tolerances need bounded EDA.
Memory mapping controls resident memory, not disk footprint: at the source
ceiling, 1.1 million events times 700 times 3 float32 values is **9.24 GB** of
particle payload before other arrays. This is a calculated upper-bound layout
budget, not observed multiplicity or measured storage. Raw-file decompression
and DataFrame overhead can be larger; convert in bounded chunks later.

## 9. Initial local development subset

Name: **`lhco-rd-dev-v1`**, a convenience subset, never the final benchmark.
Construct after integrity grouping and parent split assignment. Within each
eligible background role (train, selection-validation, calibration-validation),
rank groups by the independent SHA-256 domain `lhco-rd-v1|1729|dev-subset|` plus
fingerprint; retain the first floor(0.01 * group_count) groups. Keep roles fixed.
No final-test background, two-prong signal, or reserved signals enter this subset.

One percent of nominal eligible background is approximately 8,500 events. That
fraction is motivated by the million-event scale and source ceiling: a 10,000
event payload at 700 particles would occupy 84 MB for three float32 channels,
or 112 MB for four input channels, before metadata/overhead. These are arithmetic
budgets, not measured M5 memory. Random hash ranking avoids choosing a biased
file prefix and preserves distributions in expectation. Check train/validation
subset coverage of multiplicity and kinematic tails; if inadequate, revise the
fraction/budget explicitly and issue a new subset manifest/version.

Keep deterministic synthetic edge-case fixtures distinct from physical random
subsets. Use only dev-training data for dev scaler fits; final experiments fit
on the full designated background-training population. Development metrics are
debugging outcomes and must never be substituted for final evaluation results.

## 10. Provenance manifest

Plan a small JSON manifest per acquisition/processed release, stored locally
under `data/`; no metadata database. Required fields:

- Dataset title, pinned DOI/record/version, license/attribution, component URLs,
  publisher byte counts and expected checksum algorithm/value.
- Actual download UTC date, actual bytes, locally verified MD5 and SHA-256.
- Source schema/units/dtypes and source-file ID dictionary; original-row mapping.
- Preprocessing/schema version, complete configuration and its hash, scaler
  statistics and training-population identity, transforms, feature names/units.
- Duplicate/padding/nonfinite policies, actual audit/exclusion counts, event-ID
  and fingerprint rules; disjointness check outcomes.
- Split protocol/seed/domain strings, actual counts, validation roles, embargo
  state, and subset fraction/ranking rule/parent manifest.
- Code commit and dirty-state flag, Python/library versions, created UTC date,
  processed shard sizes/hashes/dtypes/shapes and configuration IDs.

Do not fill actual-download or actual-hash fields with publisher metadata.
Training code should receive only its designated arrays; label-aware evaluation
reads labels after the freeze. Reproducible membership manifests stay local as
data artifacts; intentionally curated small configuration/provenance summaries
may later be version controlled through a documented exception.

## 11. ML evaluation versus systems measurement

Scientific evaluation follows frozen preprocessing, populations, and thresholds.
Report data-quality/selection effects, score quality, and uncertainty. An
end-to-end pipeline measurement may include decoding, feature derivation, and
loading when its boundary is stated explicitly.

Inference-only benchmarking must preload processed batches, materialize arrays
and fault in mmap pages, prepare masks, and warm up the runtime before timing.
Measure model execution on ready inputs; synchronize asynchronous accelerators
at the declared boundary. Disk/network I/O, data download, preprocessing,
first-use compilation, and page faults are outside steady-state inference
latency. Measure host/device transfers separately or label a transfer-inclusive
boundary. State batch size, L/shapes, multiplicity, dtype, device, runtime, and
memory definition. Repeated cached inputs are systems workloads, not additional
independent events for statistical confidence.

\[
T_{\rm inference}\ne T_{\rm download/read/preprocess}.
\]

## 12. Unverified facts and immediate follow-up

Network research succeeded, including official API licenses and file metadata.
Some web-tool endpoints failed; official metadata requests succeeded via Python
HTTPS. The Dark Machines attachment PDF was rate-limited and was not read; the
original paper supplied the format/count facts. No archive contents, event files,
or black-box keys were downloaded, so none of their contents were independently
validated. Source metadata is not a local checksum verification.

Defer HDF key/table layout and chunked-read support, dtype/units/padding audit,
duplicate/near-duplicate incidence, valid multiplicity/tails, L, empirical subset
coverage, float32 tolerances, and processed shard sizing. Generator cards are
listed in the record but were not read in this task.

**Immediate next task (0003): verified acquisition and bounded schema/EDA audit
of the pinned R&D v2 source.** Record provenance, establish split/embargo before
physics exploration, inspect training-background multiplicity/numerical behavior,
and determine the reader, dev-subset budget, and L decision. Do not start model
training or a production preprocessing pipeline in that audit.
