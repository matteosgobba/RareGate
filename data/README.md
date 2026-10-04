# Data policy and planned layout

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

The following is a **planned local layout**, not existing data or tooling:

```text
data/
├── README.md
├── raw/lhco/6466204/                  # Original source + acquisition manifest
└── processed/lhco-rd-v1/
    ├── manifest.json                 # Source hashes, config, splits, versions
    ├── full/                         # Ragged arrays and separate eval labels
    └── lhco-rd-dev-v1/                # 1% of eligible background train/val groups
```

Assign parent splits and duplicate groups before creating the convenience
subset. Train and validate on background only; keep final test populations and
reserved anomalies outside development exploration. Proposed processed storage
is primitive NumPy NPY arrays with ragged offsets and a JSON manifest. Padding,
masks, scalers, and model-specific views will be derived later.

No dataset was downloaded in Task 0002. Download/preparation scripts and commands
do not exist yet. The next acquisition/audit task must verify the pinned source
bytes/checksum, record actual SHA-256 and provenance, establish the split/embargo,
and inspect schema/multiplicity before a preprocessing implementation. Individual
HTTPS download links are available on the pinned Zenodo record; avoid older raw
R&D files and do not mix them with corrected v2 feature rows.
