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
└── processed/                         # Future; not implemented
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
[the raw-data audit](../docs/raw-data-audit.md). Preprocessing commands do not
exist yet. The planned processed layout remains:

```text
data/processed/lhco-rd-v1/
├── manifest.json                     # Source hashes, config, splits, versions
├── full/                             # Ragged arrays and separate eval labels
└── lhco-rd-dev-v1/                    # 1% of eligible background train/val groups
```

Assign parent splits and duplicate groups before creating the convenience
subset. Train and validate on background only; keep final test populations and
reserved anomalies outside development exploration. Proposed processed storage
is primitive NumPy NPY arrays with ragged offsets and a JSON manifest. Padding,
masks, scalers, and model-specific views will be derived later.

Task 0002's expected split ratios are intended policy, not materialized splits.
Task 0004 must establish duplicate groups and membership before statistical EDA
on training background. Avoid older raw R&D files and do not mix them with
corrected v2 feature rows.
