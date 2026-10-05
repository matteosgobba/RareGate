# Task 0004 — Training-Background EDA and Schema Validation

## Metadata

- Task: 0004 — Training-Background EDA and Schema Validation
- Phase: data analysis/preprocessing design
- Date: 2026-10-04–2026-10-05 (Europe/Rome); primary scans measured October 4,
  provenance rerun and final documentation/validation completed October 5.
- Status: completed and validated; awaiting user commit/push
- Branch: `main`, tracking `origin/main`
- Base commit: `bdc8da00195c131a5fc3f73281f6bb2090f3b5c5`
- Environment: macOS 26.6.2 ARM64, Python 3.12.12, user-specified MacBook Pro M5;
  16 GiB RAM verified via sysctl, approximately 247 GiB free disk at inspection.
  NumPy 2.5.3, PyTorch 2.14.1, h5py 3.16.0, HDF5 2.0.0,
  hdf5plugin 7.1.0, Matplotlib 3.11.2, pytest 9.1.1, Ruff 0.16.10.
- Resulting commit: none; Codex did not stage, commit or push.

## Objective

Establish exact structural/duplicate facts and reproducible membership before
training-background EDA, then freeze the Task 0005 preprocessing contract.

## Scope

In scope: bounded full scan, exact-content hashing/grouping, deterministic split
and development indices, training-background moments/quantiles/histograms,
precision and ordering checks, aggregate statistics, curated EDA figures,
configuration, tests and development records.

Out of scope: production preprocessing/model tensors, full signal/test physics
EDA, model training/tuning, inference benchmarks, deployment/runtime conversion,
quantization and simulation. Ephemeral aggregate/transform observations were
computed to evaluate/freeze scalers; no production feature matrix was saved.

## Inspection and Changes

The starting working tree was clean. Tasks 0001–0003 were committed at
`0930b03`, `182ff31`, `bdc8da0`; local `origin/main` matched HEAD. Required
protocol/design/audit/handoff/source files, configuration, tests, data exclusion,
RAM and storage were inspected. Historical handoffs were not modified. The index
now confirms Task 0003's real commit and includes Task 0004.

Saved the exact Task 0004 user specification from this chat's local record;
no reconstructed prompt or unrelated conversation text was substituted.
Only terminal blank lines were normalized for Git whitespace checks.
Implemented NumPy-only inspection/group/split helpers, optional real-file
orchestration/EDA, an executable analysis script, and 22 new synthetic tests.
The documentation and machine-readable configuration describe implemented
analysis separately from the production pipeline planned for Task 0005.

## Files

Created:

- `src/latenttrigger/data/inspection.py`
- `src/latenttrigger/data/splitting.py`
- `src/latenttrigger/data/analysis.py`
- `src/latenttrigger/data/eda.py`
- `scripts/analyze_training_data.py`
- `tests/test_inspection.py`
- `tests/test_splitting.py`
- `tests/test_eda.py`
- `configs/data/lhco_rnd_v5.json`
- `docs/training-data-eda.md`
- `docs/preprocessing-contract.md`
- `docs/prompts/0004-training-background-eda.md`
- `docs/handoffs/0004-training-background-eda.md`
- `results/figures/final/task0004-multiplicity.png`
- `results/figures/final/task0004-momentum.png`
- `results/figures/final/task0004-angles.png`

Modified: `README.md`, `data/README.md`, `docs/handoffs/README.md`,
`pyproject.toml`. No acquisition/device/source metadata, CI, ignore rules or
historical handoff changes were needed. Raw source bytes were not modified.

## Source and Integrity

Authoritative source remains [LHCO R&D Zenodo v5, record 6466204](https://doi.org/10.5281/zenodo.6466204),
corrected `events_anomalydetection_v2.h5`, publisher metadata cross-checked in
Task 0003 and encoded in `latenttrigger.data.metadata`. This task reused the
existing real download and independently stream-verified integrity repeatedly:

- Size: expected and actual **2,908,260,409 bytes**.
- MD5: expected and actual **629789d55813be3860781b084ae7f1de**.
- SHA-256: **5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6**.
- HDF `/df/block0_values`: `(1,100,000,2101)`, float64; 700 triplets plus truth.
- Local source: `data/raw/lhco/6466204/`, ignored by Git.

Every row was scanned in 992-row chunks (16 source HDF chunks,
16,673,536 bytes raw per chunk), with vectorized checks/sorting and a digest per
event. Full-file population: **1,000,000 background + 100,000 signal**.
Unexpected labels, NaN events, infinite events, negative-pT events, malformed
padding, non-trailing padding, empty events and row-axis mismatches: **all zero**.
Padding is exactly `(0,0,0)`; zero pT with nonzero angle is malformed. A nonzero
triplet after the first padding triplet is non-trailing. Multiplicities were
computed for every row, global structural range **22–560**, no event at 700.
Exceeding 700 slots is impossible in this validated fixed-width representation.
No event was discarded or quarantined in this real dataset.

## Duplicate and Split Results

SHA-256 identity excludes truth/split/source ordinal. Remove padding, normalize
signed zero, wrap only out-of-range phi, lexicographically sort triplets, encode
uint64 little-endian count followed by float64 little-endian content. No fuzzy
matching. Labels remain available separately to detect conflicting identities.

**1,100,000 unique groups; 0 duplicated groups; 0 events in duplicate groups;
largest group size 1; 0 conflicting-label groups.** Future duplicate aliases
share atomic membership; lowest raw ordinal is the retained representative.
Conflicts/structural violations are recorded and block EDA rather than silently
altering the benchmark.

Protocol `lhco-rd-v1`, seed **1729**, exact domain strings and integer threshold
algorithm are documented in [the EDA report](../training-data-eda.md). Whole
groups use background hash fractions 70/15/15, independent 50/50 validation roles;
signals all go to final test. Exact counts:

| Split | Events |
| --- | ---: |
| Train background | 699,957 |
| Selection-validation background | 74,749 |
| Calibration-validation background | 74,823 |
| Validation background union | 149,572 |
| Test background | 150,471 |
| Test signal | 100,000 |

Group-level train/validation, train/test and validation/test intersections are
empty. Background-only train and both validation roles have **zero signals**.
Saved group codes are regenerated from fingerprints/seed and compared before
reuse; persisted indices and dev membership are reconstructed and checked.
Independent complete scans reproduced all 20 NPY arrays **byte for byte**.

Dev `lhco-rd-dev-v1` ranks the `dev-subset` domain separately per allowed
background role and retains floor(1%) of groups: **6,999 train + 747 selection
+ 748 calibration = 8,494**. No final test, signal or duplicate aliases.
It is a pipeline convenience sample, never the final reported ML benchmark.

## Training-background EDA / Technical Decisions

Statistics use only the 699,957 frozen training-background representatives;
127,379,949 valid particles. Full raw chunks can be decompressed for access, but
selection precedes every statistical operation. No test or validation physical
feature distribution or signal-performance information entered a decision.

- Multiplicity: min 22, max 560, mean **181.982535**, population std **61.020073**,
  median **177**, p90 **263**, p95 **291**, p99 **344**, p99.5 **365**,
  p99.9 **408.044**.
- pT [GeV]: min 0.0114435, max **3138.889893**, mean **15.935601**, std **52.263314**,
  median **3.170982**, p99 **240.926450**, p99.9 **686.919154**. Long tail supports
  **log1p(pT/1 GeV), then training-particle population standardization**; no clipping.
  Log mean/std **1.7563971656024226 / 1.1860427476562252**.
- Eta: **[-5,4.999999523]**, mean **-0.000023446856614008353**,
  std **1.4824139450954399**; center/scale using those training moments.
- Phi: **[-3.1415925026,3.1415927410]**. Two particles have float32(pi), just
  above mathematical pi by 8.74e-8 rad. Wrap out-of-range angles in float64;
  use **sin(phi), cos(phi)** without standardization to avoid a false seam.
- All training raw physical values round-trip FP64->FP32->FP64 with exactly
  **zero max absolute/relative error** per channel. Padding stays exact zero;
  labels 0/1 are exact uint8. Derived transforms are not claimed lossless.
  **Float32 canonical/model inputs**; float64 calculations/fitting, no FP16.
- Every training event has an adjacent raw pT increase. Source order is not
  descending. Sort descending source pT, tie by eta, wrapped phi, original slot,
  before casting/truncation; retain original slot solely as provenance.
- Sequence rule was recorded before EDA: smallest candidate with >=99% full-event
  coverage and <=0.1% event-mean scalar-pT loss. **Nmax=384**; truncates **1,740
  events (0.2485867%)**, mean **26.76494** removed if truncated, worst **176**;
  mean lost scalar pT **0.00111784%**, worst-event loss **5.11464%**. 320 fails
  coverage; 256 truncates 11.7822%. Full canonical particles remain untruncated.
- Four exact object channels: standardized log pT, standardized eta, sin phi,
  cos phi. Pad transformed features with zeros; boolean True=real retained
  object, False=padding. Scalers exclude padding and are fitted before truncation.
- Retain eight aggregates in order: N, scalar pT, max pT, relative transverse
  balance, pT-weighted eta mean, pT-weighted eta std, pT concentration, massless
  event mass. All finite/nonconstant; log1p channels 0/1/2/7 then event-weighted
  train-only standardization. Full-particle physical definitions, units and
  numeric mass-roundoff tolerance are in [the contract](../preprocessing-contract.md).
- Future bias monitoring: N, scalar pT, max pT, massless event mass and retained
  pT fraction. No test-signal scoring or physics comparison was attempted.

These extend/freeze Task 0002 proposals. Initial 384-slot view supersedes its
provisional no-additional-truncation default, with measured retention and intact
physical records. No model memory/latency guarantee is inferred from shape.
Independent complete reruns reproduced training statistics, scalers and decisions
exactly. The JSON, not these rounded summaries, is Task 0005's numeric authority.

## Dependencies and Generated Artifacts

Only direct addition: optional `analysis` extra, **matplotlib>=3.9,<4** for
requested figures (installed 3.11.2). Standard library/NumPy handle the reusable
logic; h5py/hdf5plugin remain existing `data` extras. No pandas, new storage,
ML/runtime or future-stack dependencies. CI configuration is unchanged;
synthetic tests import optional readers/plotters only when explicitly called.

Ignored local analysis directory contains 20 primitive NPY arrays,
**110,167,088 bytes total**, and a JSON source/algorithm/seed/environment/code/hash
manifest. No raw-event copy. Local timestamps, timings, comparison snapshots,
logs, plotting cache and label arrays stay ignored. About **3,101,916,024 bytes**
of scratch feature streams supported exact mapped quantiles and were removed
on success. Exact histograms use 65,536-value mapped slices.

Tracked: **88,463-byte** configuration/statistics JSON (small scalar/histogram data),
three deliberately curated small PNGs (seven training-only panels), source,
tests and documentation. Figures were visually reviewed: labels/units/context
are readable and no test population or fabricated result is plotted.

## Performance / Resource Observations

Representative full run: checksums **4.01 s**, structural checks plus hashing
**43.38 s**, grouping/splits/persistence **1.92 s**, training-feature/aggregate scan
**30.14 s**, exact mapped quantiles/histograms **22.21 s**. Process-lifetime peak
RSS before plotting **1,380,237,312 bytes (1.285 GiB)**. Independent complete rerun:
checksums **3.96 s**, scan/hash **44.39 s**, group/splits **1.89 s**, training scan
**29.85 s**, quantiles **22.40 s**, peak **1,089,404,928 bytes (1.015 GiB)**.
These include normal concurrent system activity; they are engineering observations,
not inference/model-performance benchmarks. Final October 5 provenance rerun also passed: scan/hash
47.70 s, training scan
31.29 s, quantiles 25.48 s,
peak RSS 1,064,353,792 bytes (0.991 GiB).
No complete 18.49 GB raw matrix was loaded into RAM. Default chunk size is explicit and reproducible; changing it
can change the last bits of floating moment accumulation, not split membership.

## Validation

Actual successful commands/checks:

```bash
python -m pip install --no-cache-dir -e ".[dev,data,analysis]"
python -m pip --no-cache-dir check
python -c "import latenttrigger; print(latenttrigger.__version__)"
python -m ruff check .
python -m ruff format --check .
python -m pytest
python -m latenttrigger.data.acquisition --verify-only
python scripts/analyze_training_data.py --scan-only
python scripts/analyze_training_data.py
python scripts/analyze_training_data.py --reuse-scan
```

- Editable installation succeeded; dependency check: **no broken requirements**.
- Package import returned **0.1.0**. Ruff lint/format checks passed.
- Full pytest: **54 passed** (32 existing + 22 new); no real data/network in tests.
- CPU smoke via runpy with MPS availability patched False: computation **16.0**,
  passed. Existing normal script inside sandbox also passed CPU fallback.
- Existing `python scripts/smoke_test.py` with native Metal access: **MPS True**,
  device **mps:0**, computation **16.0**, passed.
- Full real source checksums/size/HDF readability, full structural scan,
  duplicate/group/split validation and training EDA succeeded.
- Independent complete rerun and byte-hash/config comparison passed. Final source/CLI
  hashes match the configuration and actual dirty state; all numeric results
  and 20 saved arrays still reproduce after the provenance correction.
- Reuse invocation from `/private/tmp` also passed and reproduced numeric EDA,
  proving path resolution does not depend on the caller's working directory.
- All 64 relative documentation paths/anchors checked; curated figures visually inspected.
- Git ignore checks passed for raw, partial, split, label, manifest, venv and cache
  paths. Every intended change <1 MB; credential-pattern scan clean.
- Tracked diff and all new source/docs/config/tests inspected; diff whitespace
  check passed. Git status contains only the intended 20 Task 0004 files;
  index remains empty, historical handoffs/source foundation unchanged.
  New text files also passed `git diff --no-index --check /dev/null <file>`.

Hosted GitHub Actions was not run here; local checks are actual results, not a
claim that hosted CI has already passed.

## Issues / Limitations

Sandbox sysctl was denied; native read-only sysctl verified RAM. PyPI was
unreachable in the sandbox; authorized native pip installation succeeded.
Sandbox MPS reports unavailable; native Metal diagnostic succeeded. Initial
Matplotlib font-cache warnings were resolved by directing caches into ignored
local analysis data. No remaining acquisition/integrity blocker or unresolved
external feature fact was identified beyond the dataset limitations already
recorded in Task 0002/0003.
Final provenance review replaced a hard-coded uncommitted-state description with
the actual source/script dirty flag, and included the CLI source hash. Future
reruns after commit therefore record their real Git state.

FP32 exactness applies to measured raw training values, not arbitrary future
sources or newly computed transforms. Hash collisions remain a negligible
cryptographic assumption. Interrupted analysis can leave scratch/partial local
artifacts; rerun recreates files and checksum verification rejects corruption.
Run one analysis per checkout at a time. Sequence choice is initial retention
policy; its model quality/latency trade-off is intentionally not evaluated here.

## Rejected Alternatives

- Full pandas/HDF table load: 18.49 GB payload exceeds installed RAM.
- Python per-particle scans/all-pairs duplicates: vectorized checks/sort and
  collision-resistant SHA-256 grouping suffice; only digest calls are per event.
- Truth in identity or row-wise random splitting: hide label conflicts or allow
  duplicate leakage. Whole groups and separate truth avoid both.
- Full-source normalization, signal-informed selection or test EDA: violate embargo.
- Raw standardized pT / raw phi: measured long tail / physical angular seam.
- Arbitrary 64–320 default or destructive truncation: coverage fails or physical
  records are lost. Full 700 view costs more input/potential attention storage;
  384 meets predeclared training retention, while all canonical particles survive.
- FP16 canonical storage or extra features/framework/storage dependencies: outside
  this task. Compact eight-aggregate information choice remains explicit.
- Random dev sample/full data copies/committed index arrays: rank deterministically
  within allowed groups and persist ignored lightweight provenance/indices.

## Reproducibility and Follow-up

[Exact prompt](../prompts/0004-training-background-eda.md),
[measured EDA](../training-data-eda.md),
[frozen contract](../preprocessing-contract.md), and
[numeric configuration](../../configs/data/lhco_rnd_v5.json) document the state.
The full analysis script reproduces the integrity/group/split/EDA artifacts.
`--reuse-scan` rechecks source and local file hashes and reproduces group/dev
assignment before training-only EDA; it does not trust existence alone.

Next: **Task 0005 — Deterministic Preprocessing Pipeline**, implementing the
contract with ragged NumPy storage, train-fitted scaler reuse, masked views,
aggregate formulas, manifests and synthetic numerical/leakage tests. Do not
redesign features/splits or examine test signals while implementing it.

## Git

Current branch `main` has upstream `origin/main`. All Task 0004 changes remain
unstaged. Suggested commit: `feat: add deterministic LHCO data analysis and splits`.
Use selective files from the inventory above; raw/split arrays/local manifests,
caches and logs must never be staged. No resulting commit exists yet.
