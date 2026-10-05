# Data policy and acquisition

Datasets are not committed to Git. All data files and subdirectories here remain
ignored; this README is the only version-controlled file in `data/`. Never
force-add datasets, processed arrays, local manifests, or evaluation labels.

Task 0002 selects **LHC Olympics 2020 R&D, Zenodo v5**, DOI
[10.5281/zenodo.6466204](https://doi.org/10.5281/zenodo.6466204), specifically
`events_anomalydetection_v2.h5`. This corrected particle file is the initial
source. Later three-prong signal and black boxes are reserved for frozen-model
evaluation. Dataset terms are CC BY 4.0; preserve attribution independently of
the software's MIT license. Full rationale and the contract are in
[the data design](../docs/data-design.md).

## Implemented acquisition

From the checkout with the project environment active:

```bash
python -m latenttrigger.data.acquisition
python -m latenttrigger.data.acquisition --verify-only
```

The first command downloads only when needed. Both commands stream-verify the
expected **2,908,260,409 bytes** and publisher MD5
`629789d55813be3860781b084ae7f1de`, and compute SHA-256. File existence alone is
never accepted. Source metadata is pinned in `latenttrigger.data.metadata` and
was cross-checked against the official Zenodo API in Task 0003.

The default data root is found from the checkout or editable package location,
including when run from a subdirectory. Outside a checkout, use
`--data-dir /path/to/local-data`; this root contains `raw/`, not the HDF file
itself. No machine-specific path is encoded in package source or manifests.

```text
data/
├── README.md
├── raw/lhco/6466204/
│   ├── events_anomalydetection_v2.h5
│   └── events_anomalydetection_v2.h5.manifest.json
└── processed/lhco-rd-v1/schema-v1/     # Implemented dev/full ragged stores
```

Static publisher metadata is version controlled in Python source. The local
JSON manifest records verified size/MD5/SHA-256 and acquisition/verification UTC
timestamps beside the artifact, under ignored data. A verified-file rerun does
not rewrite unchanged manifest timestamps. If a valid externally supplied file
has no manifest, its acquisition timestamp is unknown (`null`).

## Failure and replacement policy

Downloads use 1 MiB streamed reads, a 60-second socket timeout, and an exclusive
`.h5.part` sibling. Verification precedes atomic promotion. HTTP/timeout,
interruption, size, and checksum failures remove this invocation's partial bytes
and return failure. Rerun the acquisition command to retry from the beginning;
range resume and automatic retry are deliberately not implemented.

An invalid existing artifact fails clearly and remains intact. Explicitly use:

```bash
python -m latenttrigger.data.acquisition --replace-invalid
```

After a replacement passes verification, old bytes are retained in a sibling
`.h5.invalid-<unique-id>` file. Remove that backup deliberately when no longer
needed. Failed download/verification leaves the original untouched. Symlink
artifacts and non-file destinations are refused.

A crash or forced process kill can leave `.h5.part`. Another invocation refuses
to overwrite it. First confirm no acquisition is running, then remove only the
stale partial and retry. Run only one acquisition per destination. The program
checks free space for the new artifact plus 64 MiB headroom; retained backups
continue to use disk space. Never force-add any of these local files to Git.

## Bounded audit and future preparation

Install the optional HDF dependencies for auditing; acquisition itself uses only
the Python standard library:

```bash
python -m pip install -e ".[dev,data]"
```

The data extra contains h5py and hdf5plugin. The verified source uses Blosc
compression, which requires importing hdf5plugin to register the decoder before
reading numeric content. Plain h5py can read schema metadata but cannot decode
this artifact without that filter.

Run the implemented integrity-only audit from the checkout:

```bash
python scripts/audit_raw_data.py
```

It re-verifies the source, inspects HDF metadata and 32 fixed row ordinals, and
writes ignored `raw-schema-audit.json` beside the acquisition manifest. It does
not perform physics EDA, create splits, or produce processed model inputs. The
Task 0003 local download passed its exact size/MD5 checks and this bounded audit.

Task 0003 acquisition/audit results and the test embargo are recorded in
[the raw-data audit](../docs/raw-data-audit.md). Assign parent splits and duplicate
groups before creating the convenience subset. Train and validate on background
only; keep final test populations and reserved anomalies outside development
exploration. Implemented processed storage is described below.

## Implemented analysis and membership

Task 0004 scans the complete verified file in 992-row chunks, hashes exact
canonical content, assigns duplicate groups atomically with seed 1729, and then
computes statistics exclusively on unique training background. Task 0005 implements
the frozen preprocessing contract. Avoid older R&D files or mixing them with v2 rows.

```bash
python -m pip install -e ".[dev,data,analysis]"
python scripts/analyze_training_data.py
# Reverify raw integrity and saved indices, then regenerate training EDA:
python scripts/analyze_training_data.py --reuse-scan
# Only integrity/hash scan and membership, without feature EDA or plots:
python scripts/analyze_training_data.py --scan-only
```

The script resolves the checkout from its own location, so it can be invoked by
path from another working directory. Matplotlib is an optional analysis dependency;
the downloader and synthetic CI tests do not require it. All scans are bounded.
Allow about 3.2 GB additional free scratch storage plus 111 MB for membership;
temporary feature streams are removed after successful statistics. Failed runs
may leave ignored scratch files that a rerun rewrites. Run one analysis at a time.

```text
data/analysis/lhco-rd-v1/                 # Entirely ignored local artifacts
├── split-manifest.json                  # Source, seed, versions, counts, hashes
├── train_background.npy                 # Raw row ordinals, not copied events
├── validation_background.npy            # Union of two disjoint roles
├── validation_selection_background.npy
├── validation_calibration_background.npy
├── test_background.npy
├── test_signal.npy
├── dev_train_background.npy             # 6,999 indices
├── dev_validation_selection_background.npy # 747 indices
├── dev_validation_calibration_background.npy # 748 indices
├── group_*.npy, row_group.npy            # Atomic groups, representatives, aliases
├── event_fingerprints.npy, labels.npy, eligible.npy, multiplicities.npy
└── eda-performance.json                 # Engineering timings/RSS, not benchmarks
```

Exact representative counts: train 699,957; validation 149,572 (74,749 selection,
74,823 calibration); test background 150,471; test signal 100,000. No duplicates
or integrity violations were found. The development subset is floor(1%) of
groups independently within the three allowed background roles, 8,494 total;
it has no test membership and is never the final benchmark. Group/split arrays
are checksum-checked before reuse, with reconstructed membership and embargo
validation. No 2.9 GB raw-file copies are created.

Only the small [JSON statistics/configuration](../configs/data/lhco_rnd_v5.json)
and three deliberately curated PNGs under `results/figures/final/` are intended
for Git. Numeric source metadata and split policies are pinned; local UTC
timestamps/manifests/logs/caches remain ignored. See
[the measured EDA](../docs/training-data-eda.md) and
[the frozen preprocessing contract](../docs/preprocessing-contract.md).
All scaler fitting and preprocessing decisions use training background only.
Final test populations remain held out; do not browse their physics distributions
while developing models.

## Implemented deterministic preprocessing

The command consumes the already-frozen configuration and verified Task 0004
membership. It never refits scalers, downloads missing data or generates new
splits. If membership is missing, reproduce only the scan/group/split stage with
`python scripts/analyze_training_data.py --scan-only`; do not overwrite the fitted
configuration by rerunning EDA. Install the existing `data` extra as above.

```bash
python -m latenttrigger.data.acquisition --verify-only
python -m latenttrigger.data.preprocessing --scope dev
python -m latenttrigger.data.preprocessing --scope dev --chunk-rows 496 \
  --output data/processed/lhco-rd-v1/schema-v1/dev-repeat
python scripts/validate_preprocessing.py \
  --repeat data/processed/lhco-rd-v1/schema-v1/dev-repeat
python -m latenttrigger.data.preprocessing --scope full
python -m latenttrigger.data.preprocessing --verify data/processed/lhco-rd-v1/schema-v1/full
```

Scope is mandatory. Default output is ignored
`data/processed/lhco-rd-v1/schema-v1/{dev,full}/`. Each store has primitive NPY
ragged physical FP32 particles, offsets, slots/IDs/multiplicities, full-event
physical aggregates, standardized baseline features, separate labels, split/dev
membership and fingerprints, plus a configuration snapshot and JSON manifest.
All particles are retained; bounded model views apply Nmax384 with masks on demand.
See [pipeline documentation](../docs/preprocessing-pipeline.md) for the reader/API,
schema, independent verifier, test-access opt-in and replacement policy.

Both real dev and full stores were generated and checksum-verified in Task 0005.
Dev contains 8,494 events / 1,549,328 particles (23.1 MB); full contains 1,100,000
events / 195,918,046 particles (2.91 GB). These are local data artifacts, not
version-controlled outputs or model results. Reserve about 3.44 GB additional
free space for a fresh full build including staging safety margin; old stores
and explicit replacement backups continue to consume storage.

An existing compatible valid store is verified and reused. Corrupt/incomplete
output fails; explicitly add `--rebuild` to rebuild, retaining prior bytes in a
`.previous-<unique-id>` sibling after successful replacement. An interrupted
build cannot be treated as complete. Confirm no builder runs before deliberately
removing any stale lock/partial directory. Never force-add local generated files.
