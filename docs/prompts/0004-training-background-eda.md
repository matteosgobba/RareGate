# Task 0004 prompt record

Exact user task specification recovered from this task’s local conversation record.
The specification text below is preserved; terminal blank lines are normalized.

---

LatentTrigger — Task 0004: Training-Background EDA and Schema Validation

You are continuing development of LatentTrigger.

Tasks 0001–0003 are complete and committed.

Task 0003 successfully downloaded and verified the real LHC Olympics 2020 R&D dataset:

events_anomalydetection_v2.h5

Pinned source:

LHC Olympics 2020 R&D — Zenodo v5

Verified raw-file facts include:

* file size: 2,908,260,409 bytes;
* MD5: 629789d55813be3860781b084ae7f1de;
* HDF dataset: /df/block0_values;
* shape: (1,100,000, 2101);
* dtype: float64;
* 700 (pT, eta, phi) triplets;
* truth label at column 2100;
* trailing zero-triplet padding observed;
* decompressed numeric payload approximately 18.49 GB.

Read before modifying anything:

* docs/development.md
* docs/data-design.md
* docs/raw-data-audit.md
* docs/handoffs/0003-dataset-acquisition.md
* data/README.md
* relevant acquisition/data source code.

This task is Task 0004 — Training-Background EDA and Schema Validation.

The purpose is to inspect the real dataset rigorously enough to freeze the preprocessing contract for Task 0005.

Do NOT implement the production preprocessing pipeline or train models yet.

⸻

0. Mandatory repository inspection

Before modifying files:

* inspect Git status;
* identify current branch and HEAD/base commit;
* confirm Tasks 0001–0003 are committed;
* inspect the existing data modules;
* verify the raw dataset remains available and checksum-valid;
* inspect available RAM/storage where practical;
* inspect current dependencies;
* ensure no unrelated work is modified.

Follow the permanent LatentTrigger development/handoff protocol.

⸻

1. Task records

Create:

docs/prompts/0004-training-background-eda.md
docs/handoffs/0004-training-background-eda.md

Update:

docs/handoffs/README.md

Preserve historical task records.

⸻

2. Core methodological rule

This task must preserve the test embargo defined previously.

The order of operations matters:

raw verified dataset
        ↓
structural / integrity scan
        ↓
exact duplicate grouping
        ↓
deterministic split assignment
        ↓
training-background selection
        ↓
statistical EDA
        ↓
preprocessing decisions

Do not inspect final-test signal distributions to make preprocessing/model decisions.

Structural checks required to establish data integrity may inspect the complete raw file, but statistical model-oriented EDA must be restricted appropriately.

Document the exact boundary.

⸻

3. Memory constraint

The raw HDF dataset represents approximately 18.49 GB of uncompressed numeric data.

Do NOT load the entire (1,100,000, 2101) float64 array into RAM.

Design all full-file scans to operate in bounded chunks.

The code should remain practical on an Apple Silicon MacBook Pro M5.

Prefer deterministic, vectorized chunk processing.

Avoid per-event Python loops across 1.1 million events where a vectorized/chunked method is practical.

Record:

* chunk size;
* approximate peak memory where measurable;
* wall-clock time for important full scans.

Do not optimize prematurely, but avoid obviously wasteful designs.

⸻

4. Implement an EDA/integrity analysis layer

Create a small reusable analysis module under an appropriate package path, for example:

src/latenttrigger/data/
    inspection.py
    splitting.py

or another clean structure.

Also provide an executable analysis script such as:

scripts/analyze_training_data.py

Separate reusable logic from one-off reporting code.

Do not build a large generic analytics framework.

⸻

5. Full-file structural integrity scan

Perform a chunked full-file scan to establish actual dataset properties.

At minimum determine exact counts for:

* total events;
* background events;
* signal events;
* unexpected label values;
* events containing NaN;
* events containing infinity;
* events containing negative pT;
* malformed padding;
* non-trailing padding;
* completely empty events;
* events exceeding the expected 700 object slots, if meaningful;
* any other clear structural violations.

Define malformed padding precisely.

For example, if zero triplets denote padding, verify whether a non-zero particle ever appears after the first padding triplet.

Do not silently discard malformed events.

Report them.

⸻

6. Particle multiplicity

Compute exact particle/object multiplicity for every event in a chunk-safe way.

For the complete dataset, structural summaries may include label-independent/global integrity information.

For model/preprocessing decisions, compute detailed statistics on training background only after split assignment.

For training background report at least:

* minimum;
* maximum;
* mean;
* standard deviation;
* median;
* p90;
* p95;
* p99;
* p99.5 if useful;
* p99.9 if useful.

Also produce a histogram or ECDF suitable for deciding future sequence length.

Do not choose sequence length before obtaining these values.

⸻

7. Exact duplicate detection

Task 0002 requires duplicate-aware splitting.

Implement a deterministic exact-event hashing strategy.

The hash should represent the raw event content relevant to duplicate identity.

Important considerations:

* do not use Python’s randomized built-in hash();
* hashing must be deterministic across runs/machines;
* do not accidentally include split assignment in the hash;
* decide explicitly whether the truth label is part of duplicate identity;
* preserve enough information to detect the dangerous case where identical event content appears with inconsistent labels.

Use a cryptographic or otherwise collision-resistant deterministic digest suitable for exact duplicate grouping.

Perform full-dataset duplicate grouping if computationally practical.

Report:

* number of unique event-content groups;
* number of duplicated groups;
* total events participating in duplicate groups;
* largest duplicate-group size;
* whether any identical event content occurs with conflicting labels.

Do not perform fuzzy or approximate duplicate detection.

⸻

8. Split assignment

Once duplicate groups are known, materialize deterministic split membership.

The intended policy from Task 0002 is approximately:

* 70% background train;
* 15% background validation;
* 15% background test;
* seed 1729.

But do not split individual rows if that could place duplicates across splits.

Assign duplicate groups atomically.

Preserve ratios as closely as practical.

Document the exact deterministic algorithm.

Important:

* background training must contain background only;
* background validation must contain background only;
* background test must remain held out;
* signals must not enter background training;
* signal test membership must be deterministic;
* do not use final-test signal performance to tune preprocessing.

If a dedicated anomaly-validation/calibration subset is scientifically required later, define its role carefully rather than leaking final-test anomalies.

⸻

9. Persist split membership reproducibly

Do not duplicate the 2.9 GB raw dataset just to create splits.

Persist lightweight deterministic split metadata.

Possible approaches include:

* row-index arrays;
* compact NumPy arrays;
* another justified lightweight representation.

The resulting artifact should make it possible to reconstruct:

train_background
validation_background
test_background
test_signal

without rerunning expensive duplicate detection.

Include appropriate provenance:

* source checksum;
* seed;
* split algorithm/version;
* counts;
* creation metadata;
* relevant code version if practical.

Large/generated split artifacts should remain ignored unless they are small and intentionally suitable for version control.

Decide deliberately and document the choice.

⸻

10. Development subset

Materialize or define the deterministic development subset designed in Task 0002.

It should derive only from allowed training/validation background data.

Task 0002 proposed approximately 1%.

Now that actual counts are known, choose and document exact semantics.

The dev subset must be:

* deterministic;
* reproducible;
* representative enough for pipeline development;
* clearly marked as NOT the final benchmark;
* free of test events;
* duplicate-safe.

Prefer storing indices rather than copying raw events.

⸻

11. Training-background feature EDA

Only after split membership is frozen, perform model-relevant statistical EDA on the training background.

For each raw physical feature:

[
p_T,\eta,\phi
]

compute appropriate statistics.

For pT, include:

* min;
* max;
* mean;
* median;
* relevant quantiles;
* distribution shape;
* heavy-tail behavior;
* frequency of zeros among valid particles, if any.

For eta:

* range;
* center;
* spread;
* relevant quantiles;
* unusual/extreme values.

For phi:

* actual numerical range;
* distribution;
* verify angular convention;
* verify boundary behavior around -\pi / +\pi or the dataset’s actual convention.

Do not include padding values in physical feature statistics.

⸻

12. Phi representation decision

Task 0002 correctly flagged phi as periodic.

Based on actual training-background data and physical semantics, determine the intended representation for model inputs.

Explicitly evaluate the standard angular encoding:

[
\sin(\phi), \cos(\phi)
]

versus raw phi.

The goal is to avoid an artificial discontinuity at the angular boundary.

Make a concrete recommendation for Task 0005 and explain it.

Do not transform the production dataset yet.

⸻

13. pT transformation decision

Inspect the actual pT distribution.

Determine whether future preprocessing should use:

* raw pT;
* standardized pT;
* log1p(pT) followed by scaling;
* another justified transformation.

The decision must come from training-background statistics, not generic ML habit.

If extreme values materially influence scaling, document them.

Do not implement production normalization yet.

⸻

14. Eta transformation decision

Determine the intended treatment of eta.

Consider:

* whether centering/scaling is useful;
* observed range;
* outliers;
* physical interpretation.

Again, derive scaling parameters only from training background.

⸻

15. Precision decision

The raw dataset is float64.

Future inference benchmarking should not blindly preserve float64 if the models will use FP32/FP16.

Evaluate whether the canonical processed representation should default to:

float32

for model inputs.

Quantify the numerical error introduced by float64 → float32 conversion on a representative training-background sample.

At minimum inspect:

* maximum absolute error;
* relevant relative error measure;
* whether zero padding remains exactly zero;
* whether label/integer-like semantics are unaffected.

Do not introduce FP16 as canonical storage at this stage.

Make a documented decision.

⸻

16. Sequence-length decision

Using the actual training-background multiplicity distribution, choose the intended initial maximum particle count:

[
N_{\max}
]

for padded/set-based models.

The choice must balance:

* event coverage;
* truncation rate;
* compute;
* memory;
* future latency.

Report, for candidate values where useful:

Nmax
fraction of training events truncated
mean particles removed when truncated
worst-case particles removed

Consider hardware-friendly candidate lengths where scientifically reasonable, e.g. powers/multiples such as:

64
96
128
160
192
256

but do not force one of these if the data strongly suggests otherwise.

Choose one initial default and document why.

Also preserve the ability to benchmark sequence length itself later.

⸻

17. Ordering policy

Determine how particles should be ordered before truncation/padding.

If the raw dataset already follows a meaningful order, verify it rather than assuming.

Potentially relevant choices include:

* original dataset order;
* descending pT;
* another physically justified ordering.

For set/attention models, ordering may be mathematically less important, but truncation makes ordering highly consequential.

Make a concrete recommendation for Task 0005.

⸻

18. Baseline event-level features

Task 0002 proposed eight aggregate event-level features for simple baselines/compact autoencoders.

Review this design using actual training-background data.

Do not yet build the production feature matrix.

Specify the final intended aggregate feature set.

Features should be:

* physically interpretable;
* computable from canonical particle records;
* compact;
* free from obvious leakage;
* suitable for PCA/simple AE baseline.

For each aggregate, document:

* definition;
* motivation;
* units;
* expected preprocessing.

Avoid arbitrary feature proliferation.

⸻

19. Bias-analysis variables

Identify variables that must later be used to determine whether anomaly score is merely learning trivial event properties.

At minimum consider:

[
N_{\text{particles}}
]

and event-level momentum/energy-scale proxies supported by the dataset.

Define a small set of future bias-analysis variables.

Do not inspect test-signal anomaly behavior now.

⸻

20. Statistical plots

Generate a concise set of EDA figures based only on permitted data.

Useful plots likely include:

1. training-background multiplicity distribution;
2. multiplicity ECDF;
3. pT distribution;
4. log1p(pT) distribution if relevant;
5. eta distribution;
6. phi distribution;
7. candidate Nmax coverage/truncation curve.

Do not create dozens of redundant plots.

Figures should have:

* meaningful titles;
* axis labels;
* units where known;
* data-source/split context.

Do not use styling merely for decoration.

Follow existing results policy regarding generated versus curated figures.

If selected EDA figures are useful as permanent scientific documentation, intentionally curate only those.

⸻

21. EDA report

Create:

docs/training-data-eda.md

It should be the authoritative report for Task 0004.

Suggested structure:

Dataset population

Integrity scan

Duplicate analysis

Split construction

Development subset

Training-background multiplicity

Raw feature distributions

Angular representation

Numerical precision

Sequence-length decision

Particle ordering

Baseline aggregate features

Bias-analysis variables

Frozen preprocessing decisions

Remaining questions

Include actual measured values.

Distinguish facts from decisions.

⸻

22. Preprocessing contract

Create:

docs/preprocessing-contract.md

This is particularly important.

At the end of Task 0004, freeze the input contract that Task 0005 will implement.

Define precisely:

Canonical particle representation

For example conceptually:

particles: [N, F]
mask: [N]

but use the actual selected feature schema.

Feature order

Specify exact channel order.

Phi handling

Raw or sin/cos, based on analysis.

pT handling

Exact intended transform.

Eta handling

Exact intended transform.

Scaling

Which statistics are fitted on training background only.

Precision

Expected canonical dtype.

Ordering

Exact rule.

Padding

Exact padding value.

Truncation

Exact initial Nmax.

Mask semantics

Define True/False or 1/0 meaning explicitly.

Baseline aggregate representation

Exact ordered feature list.

Labels

How labels are represented and when they are exposed.

Splits

Which split may be used for which purpose.

This contract should make Task 0005 mostly an implementation task rather than another design task.

⸻

23. Reproducibility artifact

Store the actual fitted/derived EDA statistics needed for Task 0005 in a small machine-readable artifact.

For example:

configs/data/lhco_rnd_v5.json

or an equally appropriate location/format.

It may contain values such as:

* source checksum;
* split seed;
* event counts;
* selected Nmax;
* feature transform choices;
* training-background scaling statistics;
* aggregate feature definitions/version;
* schema version.

Do not manually duplicate values across multiple files if code can read a single source of truth.

Do not put large arrays in Git.

If some statistics should instead be generated locally from split artifacts, document why.

⸻

24. Performance observations

Because this project ultimately studies systems performance, record the runtime characteristics of the EDA itself where useful.

For expensive operations report approximately:

* wall-clock duration;
* peak/resident memory if readily measurable;
* chunk size.

This is not yet a formal hardware benchmark.

Do not publish these numbers as model-performance results.

They are engineering observations.

⸻

25. Tests

Add meaningful unit tests for reusable logic introduced in this task.

Tests should use synthetic/small fixtures, not the 2.9 GB dataset.

Test at least as applicable:

* multiplicity computation;
* padding validation;
* deterministic event hashing;
* duplicate grouping;
* duplicate-safe split assignment;
* deterministic split reproduction;
* split disjointness;
* background-only train/validation;
* dev subset determinism;
* feature-statistics exclusion of padding;
* precision conversion logic if implemented as reusable analysis utility.

CI must remain independent of the real dataset.

⸻

26. Main README and data README

Update them minimally.

The main README should reflect that:

* verified acquisition exists;
* raw-data audit exists;
* training-background EDA/split design is complete once this task succeeds;
* preprocessing is still the next phase.

data/README.md should document generated split/index artifacts and how to reproduce them if applicable.

Do not turn either README into the full EDA report.

Link to detailed documentation.

⸻

27. Scope exclusions

Do NOT:

* implement the final preprocessing pipeline;
* create production model tensors;
* train PCA;
* train an autoencoder;
* train a Transformer;
* inspect final-test signal performance;
* optimize model hyperparameters;
* implement inference benchmarks;
* add ONNX;
* add CoreML;
* add quantization;
* add TensorRT;
* add hls4ml;
* implement the trigger simulator;
* add a dashboard;
* add experiment tracking unless genuinely required for this task.

⸻

28. Validation

Before completion, run:

* package/dependency consistency checks;
* package import;
* Ruff lint;
* Ruff formatting check;
* full pytest suite;
* CPU smoke test;
* MPS smoke test;
* real raw-file checksum verification;
* full structural scan;
* duplicate/split validation;
* EDA generation;
* documentation-link validation;
* Git ignore verification;
* Git diff inspection;
* git diff --check.

Verify specifically:

[
Train \cap Validation = \varnothing
]

[
Train \cap Test = \varnothing
]

[
Validation \cap Test = \varnothing
]

at the duplicate-group level, not merely row-index level.

Verify that no signal event is present in background training or background validation.

Verify that no final-test signal distribution was used for preprocessing decisions.

⸻

29. Definition of done

Task 0004 is complete only when:

* Task 0004 prompt/handoff exist;
* handoff index is updated;
* full structural integrity scan is complete;
* exact duplicate analysis is complete or a concrete blocker is documented;
* deterministic duplicate-safe split membership exists;
* development subset exists/has deterministic membership;
* training-background EDA is complete;
* raw feature statistics are known;
* phi representation is decided;
* pT transformation is decided;
* eta treatment is decided;
* float32 policy is decided;
* sequence length is decided;
* particle ordering is decided;
* baseline aggregate features are finalized;
* bias-analysis variables are identified;
* preprocessing contract is written;
* machine-readable configuration/statistics exist;
* reusable analysis logic has tests;
* existing tests still pass;
* raw/generated large artifacts remain outside Git.

⸻

30. Mandatory handoff

Before finishing, update:

docs/handoffs/0004-training-background-eda.md

with actual facts.

Include:

* base commit;
* environment;
* raw checksum status;
* scan method/chunk size;
* integrity results;
* duplicate results;
* exact split counts;
* dev subset definition/count;
* EDA statistics;
* decisions and rationale;
* generated artifacts;
* runtime/memory observations;
* tests;
* issues;
* rejected alternatives;
* deferred decisions;
* next recommended task.

Update the handoff index.

Do not rewrite historical handoffs.

⸻

31. Final response format

Return:

1. What was implemented

2. Dataset integrity findings

Include actual full-scan findings.

3. Duplicate and split results

Include exact counts.

4. Training-background EDA

Include the most important measured statistics.

5. Frozen preprocessing decisions

Clearly state:

* pT;
* eta;
* phi;
* dtype;
* ordering;
* Nmax;
* padding;
* mask;
* aggregate features.

6. Generated artifacts

Explain what is tracked versus ignored.

7. Validation results

Include actual test count and real-data checks.

8. Performance / resource observations

9. Issues / deferred decisions

10. Recommended next task

Expected:

Task 0005 — Deterministic Preprocessing Pipeline

unless Task 0004 reveals a blocker.

11. Git commit and push commands

This section is mandatory and MUST be last.

Do NOT commit or push automatically.

Provide exact commands to:

git status
git diff
git add <only intended Task 0004 files>
git status
git diff --cached
git diff --cached --check
git commit -m "<specific conventional commit>"
git push

Selectively stage only intended source, tests, configuration, curated small figures and documentation.

Never stage:

* raw HDF5 data;
* large generated arrays;
* split artifacts intended to remain local;
* caches;
* temporary files;
* credentials;
* unrelated work.

Use an appropriate Conventional Commit message, likely:

feat: add deterministic LHCO data analysis and splits

but adjust it to reflect the actual completed work.

Proceed with Task 0004 only.
