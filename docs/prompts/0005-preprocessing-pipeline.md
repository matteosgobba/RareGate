# Task 0005 prompt record

Original user specification from the supplied text attachment; only terminal
blank lines are normalized.

---

# LatentTrigger — Task 0005: Deterministic Preprocessing Pipeline

You are continuing development of **LatentTrigger**.

Tasks 0001–0004 are complete and committed.

Task 0004 completed the full structural scan, duplicate analysis, deterministic split assignment, training-background EDA and preprocessing design.

The preprocessing policy is now frozen in:

- `docs/preprocessing-contract.md`
- `docs/training-data-eda.md`
- `configs/data/lhco_rnd_v5.json`
- `docs/handoffs/0004-training-background-eda.md`

Read those files carefully before writing code.

**Do not redesign the preprocessing policy in this task.**

If implementation reveals a contradiction or impossible requirement, document it explicitly rather than silently changing the contract.

This is:

**Task 0005 — Deterministic Preprocessing Pipeline**

The goal is to turn the frozen Task 0004 preprocessing contract into a reproducible, tested, memory-bounded production data pipeline.

No model training belongs in this task.

---

# 0. Mandatory repository inspection

Before modifying anything:

- inspect Git status;
- identify current branch and HEAD/base commit;
- verify Tasks 0001–0004 are committed;
- inspect `docs/development.md`;
- inspect `docs/preprocessing-contract.md`;
- inspect `docs/training-data-eda.md`;
- inspect `configs/data/lhco_rnd_v5.json`;
- inspect Task 0004 handoff;
- inspect existing data/analysis/splitting modules;
- inspect local split/index artifacts produced by Task 0004;
- reverify that the raw source is available;
- inspect available disk space;
- inspect currently installed dependencies.

Do not modify unrelated work.

Follow the permanent prompt/handoff protocol.

---

# 1. Task records

Create:

```text
docs/prompts/0005-preprocessing-pipeline.md
docs/handoffs/0005-preprocessing-pipeline.md
```

Update:

`docs/handoffs/README.md`

Preserve all earlier task records.

---

# 2. Frozen preprocessing contract

Task 0004 established the following decisions.

The implementation must use the authoritative exact definitions and fitted statistics from `docs/preprocessing-contract.md` and `configs/data/lhco_rnd_v5.json`, not values copied from this prompt.

At a high level:

### Particle inputs

Raw particle features:

```text
pT
eta
phi
```

Model-facing features:

```text
standardized log1p(pT / 1 GeV)
standardized eta
sin(wrapped phi)
cos(wrapped phi)
```

### Precision

Model/canonical numeric processing should use the Task 0004 FP32 policy.

### Ordering

Particles use the frozen deterministic ordering:

1. descending pT;
2. tie-break by eta;
3. wrapped phi;
4. original slot.

### Set/sequence view

Initial:

`Nmax = 384`

with zero padding after transformation.

Mask semantics:

`True` = real retained particle.

### Compact event representation

Eight frozen aggregate features:

- multiplicity;
- scalar pT;
- maximum pT;
- transverse balance;
- pT-weighted eta mean;
- pT-weighted eta standard deviation;
- pT concentration;
- massless event mass.

Use the **exact definitions in the preprocessing contract**.

Do not reinterpret these formulas.

---

# 3. Architecture goal

Implement a clean pipeline conceptually separating:

```text
verified raw HDF5
        ↓
canonical physical events
        ↓
deterministic preprocessing
        ↓
processed canonical store
        ↓
model-specific views
```

Do not make the padded `[384, F]` representation the only persistent source of truth.

The processed representation should preserve enough information that future tasks can:

- derive compact baseline features;
- derive padded particle/set inputs;
- experiment with another `Nmax`;
- perform bias analysis;
- reproduce transformations;
- benchmark inference without rereading or decompressing the original HDF5 file.

---

# 4. Canonical processed representation

Design and implement a compact canonical representation that preserves **all valid particles**, not only the first 384.

Prefer primitive NumPy-compatible arrays as established by earlier tasks.

A strong default design is conceptually:

```text
particles.npy
offsets.npy
event_features.npy
labels.npy
event_ids.npy
split information
manifest.json
```

where:

- particle records are stored contiguously;
- event offsets identify each event's slice;
- no zero-padding is required in the canonical store;
- all valid physical particles are retained.

However, inspect the existing preprocessing contract and repository design before finalizing exact filenames/layout.

The canonical store should avoid Python object arrays.

Avoid formats requiring unnecessary heavy dependencies.

---

# 5. Raw physical versus transformed particle storage

Make an explicit design decision about whether the canonical particle store contains:

### Option A
physical FP32:

```text
pT, eta, wrapped_phi
```

with model transformations computed when model views are generated,

or:

### Option B
model-transformed features:

```text
scaled_log_pT, scaled_eta, sin_phi, cos_phi
```

If practical, prefer a design that preserves physical interpretability without forcing rereads from the 2.9 GB raw HDF5 source.

It is acceptable to persist both a compact physical representation and derived small metadata if justified.

Do not duplicate multi-gigabyte arrays without a clear reason.

Document the storage trade-off and decision in the handoff.

---

# 6. Memory-bounded processing

The source contains 1.1 million events and roughly 127+ million physical particles.

Do NOT load the entire raw HDF5 array into memory.

The preprocessing pipeline must operate in bounded chunks.

Requirements:

- chunked HDF5 reads;
- vectorized operations where practical;
- bounded peak RAM;
- no Python list containing every event's particle array;
- incremental output writing.

Use memory-mapped `.npy`, open memmaps, shards, or another simple robust mechanism.

If using sharding, make shard boundaries deterministic.

Record:

- processing chunk size;
- output layout;
- observed peak memory where practical;
- total runtime.

The pipeline must remain usable on the current 16 GiB Apple Silicon development machine.

---

# 7. Split source of truth

Do NOT recalculate splits differently.

Use the deterministic Task 0004 split membership/provenance artifacts.

The known populations are:

```text
training background               699,957
selection-validation background    74,749
calibration-validation background  74,823
test background                   150,471
test signal                       100,000
```

The development subset contains:

`8,494 background events`

Verify these counts against local artifacts before processing.

If they do not match, stop with a clear error rather than silently regenerating them.

---

# 8. Split semantics

Preserve the existing roles exactly.

At minimum distinguish:

```text
train_background
validation_selection_background
validation_calibration_background
test_background
test_signal
dev
```

Do not merge validation populations just for implementation convenience.

The full processed store may contain labels and split metadata, but later APIs must make it difficult to accidentally consume `test_signal` during model development.

Document how the representation preserves the test embargo.

---

# 9. Transformation implementation

Implement reusable, pure or near-pure functions for the frozen transformations.

At minimum cover:

### pT

Apply the exact Task 0004 transformation and scaling parameters.

### eta

Apply the exact Task 0004 centering/scaling.

### phi

- normalize/wrap according to the contract;
- generate sine;
- generate cosine.

### padding

For model views only:

- transformed padding values must be zero;
- padding mask must be `False`;
- real retained particles must have mask `True`.

### ordering

Apply the exact deterministic particle ordering before truncation.

### truncation

For the default set view:

- retain at most 384 particles;
- preserve the highest-priority particles according to the frozen ordering.

Do not silently truncate canonical physical storage.

---

# 10. Numerical edge cases

Handle explicitly:

- `pT = 0` where physically permitted;
- phi slightly above `pi` due to floating-point representation;
- negative-zero representations;
- extremely large pT;
- events with fewer than 384 particles;
- events with exactly 384;
- events with more than 384;
- deterministic tie ordering.

Do not let floating-point quirks make sorting nondeterministic across runs.

---

# 11. Float64 → float32 regression check

Task 0004 reported that the observed raw training values converted to FP32 without measurable change.

This is plausible if the source values were originally generated/quantized with FP32-compatible precision, but do **not** rely on that statement blindly.

Add an explicit regression/analysis check.

On representative and boundary-relevant source values, measure:

- maximum absolute conversion error;
- maximum or robust relative error;
- whether zero remains exactly zero;
- whether conversion changes particle ordering in any tested case;
- whether converted phi values remain correctly wrapped.

If the claim of exact conversion remains true, document why the evidence supports it.

If non-zero differences are found, document them accurately.

Do not change the FP32 policy unless the finding materially invalidates Task 0004.

---

# 12. Aggregate feature implementation

Implement the exact eight event-level aggregate features frozen in Task 0004.

Requirements:

- derive them from **all valid event particles**, before `Nmax=384` truncation unless the contract explicitly states otherwise;
- use deterministic numerical operations;
- exclude padding;
- preserve documented units/transform semantics;
- do not use the truth label;
- do not expose split identity as a feature.

The implementation should return features in one permanently defined order.

Store the feature names/order in a machine-readable source of truth.

---

# 13. Baseline feature scaling

Inspect the preprocessing contract.

If Task 0004 already froze scaling/statistics for aggregate features, implement them exactly.

If only raw aggregate definitions were frozen and aggregate scaling was explicitly deferred, do NOT invent scaling in this task.

Instead:

- persist raw aggregate features;
- document scaling as a later baseline-training responsibility.

Do not silently fit statistics using validation or test data.

---

# 14. Model-view builder

Implement a reusable mechanism that converts canonical events into the initial particle model view.

Expected conceptual output for a batch/event:

```text
features: [Nmax, 4] float32
mask:     [Nmax] bool
```

with channel order explicitly frozen and documented.

For batches:

```text
features: [B, Nmax, 4]
mask:     [B, Nmax]
```

The builder must support:

- default `Nmax=384`;
- optionally another explicit `Nmax` for future controlled experiments without changing canonical storage;
- deterministic ordering/truncation;
- correct zero padding.

Do not introduce PyTorch dependency into the data representation if NumPy is sufficient.

Conversion to `torch.Tensor` can occur in future dataset/loaders.

---

# 15. Storage layout

Create a clear processed-data hierarchy, for example:

```text
data/
└── processed/
    └── lhco-rnd-v5/
        └── <schema-version>/
            ├── ...
            └── manifest.json
```

Use the repository's existing naming conventions where applicable.

The processed output must remain ignored by Git.

The layout must support schema/version evolution.

Do not use machine-specific absolute paths in manifests.

---

# 16. Schema versioning

Introduce an explicit processed-data schema version.

For example conceptually:

`schema_version = 1`

The manifest should identify:

- dataset;
- source version;
- source checksum;
- preprocessing schema version;
- preprocessing config identity/hash;
- split provenance identity;
- feature order;
- dtypes;
- shapes/counts;
- `Nmax` default;
- canonical storage semantics;
- creation software/project version;
- relevant transformation parameters.

Do not encode transient local state unnecessarily.

---

# 17. Output integrity

Processed files are future scientific inputs.

Add integrity metadata.

For generated arrays/files, record appropriate:

- shape;
- dtype;
- byte size;
- checksum/hash where practical.

Provide a verification command/API that can check an existing processed store without regenerating it.

A corrupted or incomplete processed store must not be silently accepted.

Use a temporary output location and atomic/finalization strategy where practical so an interrupted preprocessing run is not mistaken for a valid complete dataset.

---

# 18. Pipeline CLI

Provide a clear CLI/module interface.

A reasonable conceptual interface is:

```bash
python -m latenttrigger.data.preprocessing --scope dev
```

and:

```bash
python -m latenttrigger.data.preprocessing --scope full
```

plus an integrity mode such as:

```bash
python -m latenttrigger.data.preprocessing --verify
```

Exact syntax may differ if a cleaner interface exists.

Requirements:

- default behavior must be safe;
- scope must be explicit where expensive work is involved;
- output destination must be reported;
- existing valid output should be reusable;
- invalid output should fail clearly;
- force/rebuild behavior must be explicit;
- progress should be visible for long full runs.

Do not introduce an external CLI framework unless justified.

`argparse` is sufficient.

---

# 19. Development-first execution

Before running full preprocessing:

1. implement and unit-test the pipeline;
2. run it on the deterministic 8,494-event dev subset;
3. verify all dev outputs;
4. inspect memory/storage behavior;
5. rerun the dev pipeline independently and confirm deterministic output.

Only after the dev pipeline is validated should you attempt the full dataset.

---

# 20. Deterministic output test

For the dev subset, run preprocessing twice into separate temporary/output locations.

Verify, where deterministic metadata allows:

- array shapes identical;
- array dtypes identical;
- array contents byte-identical;
- checksums identical;
- aggregate features identical;
- masks identical;
- ordering identical.

Timestamp-like metadata may differ if intentionally recorded, but such fields must not affect scientific content hashes.

Clearly separate:

```text
scientific content identity
```

from:

```text
local acquisition/build metadata
```

---

# 21. Full preprocessing execution

After the dev run succeeds, estimate required disk space before processing the full dataset.

Account for:

- canonical particle storage;
- event offsets;
- aggregate features;
- labels;
- split metadata;
- temporary files;
- safety margin.

Check actual free disk space.

If sufficient space is available, run full preprocessing.

If not sufficient:

- do not risk filling the disk;
- leave the full run pending;
- report exact estimated space requirement;
- retain a fully validated dev pipeline.

Do not delete the verified raw dataset automatically to create space.

---

# 22. Do not materialize wasteful full padded arrays by default

Do not automatically persist:

```text
1,100,000 × 384 × 4
```

padded feature tensors unless measurements show a compelling reason.

The canonical store should be storage-efficient.

The model view should normally be derived:

- on demand;
- by batches;
- or later through explicit benchmark caches.

This allows future controlled experiments with different `Nmax` values without rebuilding the canonical store.

If you choose a different approach, justify the disk/performance trade-off quantitatively.

---

# 23. Loader/read API

Provide a lightweight read interface for the processed canonical store.

It should allow future code to request deterministic event ranges or selected row indices and obtain:

- physical/canonical particles;
- event aggregate features;
- labels where allowed;
- relevant event metadata.

Also provide the model-view conversion path.

Keep it framework-agnostic if practical.

Do NOT yet implement the final PyTorch training `Dataset`/`DataLoader` abstraction unless it is unavoidable.

That can be added when the first model is implemented.

---

# 24. Test-embargo safeguards

The pipeline must not weaken the embargo established in Tasks 0002–0004.

Consider providing explicit access methods/scopes so normal development naturally targets:

```text
train
validation
dev
```

rather than `test_signal`.

Do not hide the data cryptographically; the goal is methodological protection.

But avoid APIs that casually concatenate every split for model development.

Labels must not be included among model features.

Document the safeguard.

---

# 25. Tests

Add strong unit and integration tests using synthetic/small fixtures.

At minimum test:

### Transformations

- pT transform;
- eta transform;
- phi wrapping;
- sin/cos encoding;
- FP32 behavior.

### Ordering

- descending pT;
- eta tie-break;
- wrapped-phi tie-break;
- original-slot final tie-break.

### Model view

- zero padding;
- mask semantics;
- exact 384 boundary;
- truncation;
- alternate `Nmax`.

### Aggregates

Test every aggregate against hand-computable synthetic examples.

### Canonical storage

- offsets;
- event reconstruction;
- dtypes;
- schema metadata.

### Determinism

- same input/config → identical scientific output.

### Integrity

- valid manifest/store accepted;
- modified/corrupted file detected;
- incomplete output rejected.

### Splits

- correct use of existing split memberships;
- labels/features not conflated;
- test embargo semantics preserved.

Do not use the full real dataset in CI.

---

# 26. Real-data validation

On the real dev subset, verify at minimum:

- event count = 8,494;
- no event disappears unexpectedly;
- no extra event appears;
- raw multiplicities can be reconstructed;
- canonical offsets are monotonic and valid;
- aggregate features are finite;
- transformed particle features are finite;
- masks match retained multiplicities;
- padding is zero;
- truncation count matches Task 0004 expectations for the same events;
- no labels are transformed into features.

On the full dataset, if processed:

- verify all expected population counts;
- verify source/split provenance;
- verify event and particle counts;
- verify integrity hashes.

---

# 27. Semantic spot checks

Perform a small number of explicit event-level spot checks.

For selected deterministic event IDs:

1. read raw HDF5 particles;
2. independently identify valid particles;
3. inspect ordering;
4. inspect transformations;
5. inspect aggregates;
6. inspect canonical reconstruction;
7. inspect padded model view.

Document enough information to establish correctness without dumping large event records into Git.

---

# 28. Processed-data documentation

Create:

`docs/preprocessing-pipeline.md`

Cover:

## Input

Raw verified source and split artifacts.

## Canonical representation

What is stored and why.

## Transformations

Reference frozen contract.

## Storage layout

Files, dtypes, shapes/semantics.

## Model view

How `[N,4]` / `[384,4]` representations are derived.

## Aggregate features

Exact ordered list/reference.

## Determinism

How reproducibility is guaranteed.

## Integrity

How processed stores are verified.

## Test embargo

How split semantics are preserved.

## Commands

Exact dev/full/verify commands.

## Resource requirements

Observed dev/full runtime, memory and disk if available.

Do not duplicate the entire Task 0004 EDA report.

---

# 29. Update data/README.md

Update it with implemented preprocessing commands.

A new developer should understand:

```text
acquire raw data
→ verify raw data
→ reproduce split metadata if required
→ preprocess dev/full
→ verify processed store
```

Clearly distinguish tracked source/config from ignored generated artifacts.

---

# 30. Update main README minimally

Reflect:

- verified acquisition;
- completed EDA;
- implemented deterministic preprocessing;
- whether full processed data has been materialized;
- next stage.

Do not claim that baseline/model training exists yet.

Link to:

- preprocessing contract;
- preprocessing pipeline documentation.

---

# 31. Dependency discipline

Do not add dependencies unless required.

This task should likely be implementable with existing:

- Python;
- NumPy;
- h5py/hdf5plugin.

Do not add:

- pandas;
- PyTorch data utilities;
- Dask;
- Ray;
- Arrow;
- Polars;
- TensorFlow

merely to implement the preprocessing pipeline.

If a dependency is added, justify it explicitly.

---

# 32. Scope exclusions

Do NOT:

- train PCA;
- fit an autoencoder;
- implement a Transformer;
- inspect final test signal performance;
- perform hyperparameter tuning;
- implement PyTorch training loops;
- implement ML experiment tracking;
- implement ONNX;
- implement CoreML;
- implement TensorRT;
- implement quantization;
- implement inference benchmarks;
- implement the trigger simulator;
- add FPGA/hls4ml;
- add Docker unless an actual blocker requires it;
- build a frontend/dashboard.

This task is exclusively data engineering and preprocessing.

---

# 33. Validation

Before completion run:

- editable install / dependency consistency;
- package import;
- Ruff lint;
- Ruff formatting check;
- full pytest suite;
- CPU smoke test;
- MPS smoke test;
- raw checksum verification;
- dev preprocessing;
- second independent dev preprocessing for determinism;
- dev processed-store verification;
- full preprocessing if safe/feasible;
- full processed-store verification if generated;
- documentation-link validation;
- Git exclusion check;
- `git diff --check`;
- final Git diff inspection.

Record actual outcomes only.

---

# 34. Definition of done

Task 0005 is complete only when:

- Task 0005 prompt exists;
- Task 0005 handoff exists;
- handoff index is updated;
- frozen transformations are implemented;
- canonical processed format exists;
- canonical store preserves all valid particles;
- aggregate features are implemented;
- model-view generation is implemented;
- deterministic ordering/truncation/padding/masks work;
- processed-data manifest/schema version exists;
- integrity verification exists;
- dev subset preprocessing completes;
- independent dev rerun is scientifically deterministic;
- full preprocessing is either completed safely or explicitly deferred for a concrete resource reason;
- processed-data documentation exists;
- reusable logic has meaningful tests;
- existing tests remain passing;
- generated large artifacts remain outside Git.

---

# 35. Mandatory Task 0005 handoff

Before finishing, update:

`docs/handoffs/0005-preprocessing-pipeline.md`

Include actual:

- base commit;
- environment;
- schema version;
- pipeline architecture;
- output layout;
- transformation implementation;
- aggregate feature implementation;
- dev output counts/sizes;
- full output counts/sizes if generated;
- source/config hashes;
- determinism results;
- float64 → float32 regression results;
- runtime;
- memory;
- disk consumption;
- tests;
- issues;
- rejected alternatives;
- deviations from Task 0004 contract, if any;
- next recommended task.

Update the handoff index.

Do not rewrite old handoffs.

---

# 36. Final response format

Return:

## 1. What was implemented

## 2. Processed-data architecture

Explain canonical store and model-specific views.

## 3. Transformation implementation

Confirm actual implementation of:

- pT;
- eta;
- phi;
- FP32;
- ordering;
- truncation;
- padding/mask;
- aggregates.

## 4. Dev preprocessing result

Include:

- events;
- particles;
- output size;
- runtime;
- memory where available;
- determinism result.

## 5. Full preprocessing result

Clearly state whether full preprocessing was completed.

If yes, provide:

- event counts;
- particle count;
- total disk footprint;
- runtime;
- integrity verification.

If no, explain the exact blocker.

## 6. Numerical validation

Include FP32 regression and semantic spot checks.

## 7. Test results

Include actual total pytest count and other checks.

## 8. Files changed

Separate:

- tracked source/docs/tests;
- ignored generated local artifacts.

## 9. Issues / deferred decisions

## 10. Recommended next task

Expected next task:

**Task 0006 — Statistical Baseline and Evaluation Framework**

The next phase should introduce the first actual anomaly-detection baseline only after this preprocessing pipeline is complete.

## 11. Git commit and push commands

This section is mandatory and MUST be last.

Do NOT commit or push automatically.

Provide exact commands for:

```bash
git status
git diff

git add <only intended Task 0005 tracked files>

git status
git diff --cached
git diff --cached --check

git commit -m "<specific conventional commit>"
git push
```

Selectively stage only Task 0005 code, tests, configuration and documentation.

Never stage:

- raw dataset;
- processed multi-GB arrays;
- split/index artifacts intended to remain local;
- temporary preprocessing directories;
- caches;
- logs;
- credentials;
- unrelated files.

Use an appropriate Conventional Commit message.

If the pipeline is successfully implemented, a likely message is:

`feat: add deterministic LHCO preprocessing pipeline`

but adjust it to match the actual work.

Proceed with **Task 0005 only**.
