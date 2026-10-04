# LHCO R&D raw-data audit

Task 0003, 2026-10-04. **Status: real artifact acquired and checksum-verified;
bounded schema/content audit passed.** Findings refer to the verified local
artifact and the stated sample, not a full-file quality or physics analysis.
No preprocessing or split assignments exist.

## Source

LHC Olympics 2020 R&D, Zenodo v5, record 6466204,
DOI [10.5281/zenodo.6466204](https://doi.org/10.5281/zenodo.6466204).
Only `events_anomalydetection_v2.h5` is acquired. The
[official record](https://zenodo.org/records/6466204) describes the corrected
April 2022 particle file; the old uncorrected file and supplemental/black-box
data are excluded. [Authoritative API](https://zenodo.org/api/records/6466204).

The API cross-check agreed with Task 0002 on version, DOI, CC BY 4.0 license,
filename, byte count, and checksum. The individual download URL is
<https://zenodo.org/api/records/6466204/files/events_anomalydetection_v2.h5/content>.

## Integrity and local acquisition

Publisher expected size: **2,908,260,409 bytes**.
Publisher expected MD5: **629789d55813be3860781b084ae7f1de**.
Actual size: **2,908,260,409 bytes**, matches publisher metadata.
Actual MD5: **629789d55813be3860781b084ae7f1de**, matches publisher metadata.
Locally computed SHA-256:
`5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6`.
Acquisition/first verification completed UTC:
`2026-10-04T11:05:47.545875+00:00`, from the local manifest.

The implemented CLI downloaded the artifact in 1 MiB chunks, verified the
completed partial file, and promoted it atomically. A later audit invocation
re-verified and reused the file without HTTP access or rewriting acquisition
state. No corrupt files or leftover partials occurred in real acquisition;
failure handling was exercised with controlled unit artifacts.

Portable default location: `data/raw/lhco/6466204/`. Data, partial files,
retained invalid backups, local acquisition manifests, and audit JSON remain
ignored by Git. The implemented CLI and failure/recovery policy are documented
in [data/README.md](../data/README.md).

## Raw schema

The root contains only group `/df`. This is a pandas **fixed-format frame**,
not a PyTables appendable table or a top-level dense `/table` dataset.

| HDF dataset | Shape | Stored dtype | Chunk shape | Role |
| --- | --- | --- | --- | --- |
| `/df/axis0` | `(2101,)` | int64 | `(8192,)` | DataFrame column labels, verified 0 through 2100. |
| `/df/axis1` | `(1100000,)` | int64 | `(8192,)` | Stored DataFrame row index; sampled values match row ordinals. |
| `/df/block0_items` | `(2101,)` | int64 | `(8192,)` | Numeric-block columns, verified 0 through 2100. |
| `/df/block0_values` | `(1100000, 2101)` | float64 | `(62, 2101)` | Event rows including particle features and truth bit. |

All four datasets use Blosc, HDF filter ID **32001**. Numeric-array filter
parameters are `(2, 2, 8, 1042096, 5, 1)`; axis-array parameters are
`(2, 2, 8, 65536, 5, 1)`. Stored attributes include
`PYTABLES_FORMAT_VERSION="2.1"`, `pandas_type="frame"`,
`pandas_version="0.15.2"`, `nblocks=1`, `ndim=2`, and transposed markers.
These are file attributes, not versions of libraries installed locally.
No physical unit/type metadata is stored in the inspected attributes/column names.

**Reader finding:** h5py alone read metadata but failed its first one-row content
read because Blosc was unavailable. Optional `data` dependencies now include
`h5py>=3.12,<4` and `hdf5plugin>=7.1,<8`; importing hdf5plugin registers the
decoder, as documented by [the plugin maintainer](https://hdf5plugin.readthedocs.io/en/stable/usage.html).
Content reads then succeeded with native macOS ARM64 wheels. No pandas/PyTables
dependency is needed for bounded slicing of this particular fixed-format block.

The numeric block is **18,488,800,000 uncompressed bytes** (18.49 GB decimal),
derived from actual shape/dtype; a whole-file DataFrame read risks substantial
memory overhead. A 62-row chunk is 1,042,096 uncompressed bytes. Future iteration
should read contiguous bounded slices, preferably aligned to chunk multiples.
Metadata gives event/column counts without scanning all rows.

## Feature interpretation

The official Zenodo description defines 700 padded `(pT, eta, phi)` triplets
and a final truth bit; no particle type or charge. The
[official parsing repository](https://github.com/lhcolympics2020/parsingscripts)
contains `LHCOlympics2020_pyjetexample.ipynb`, which reads the truth bit at column
2100 and triplets at columns `3*j`, `3*j+1`, `3*j+2`, accepting pT>0.
It passes momenta directly to pyjet and labels jet momentum/mass plots in GeV.
This provides source-based unit evidence, rather than inferring units from
numeric magnitudes. The [Delphes unit documentation](https://delphes.github.io/workbook/root-tree-description/)
also specifies GeV for momentum. Eta is dimensionless; phi is an azimuthal angle
in radians. Actual numeric storage/column mapping agrees with that representation.
No notebook cells or jet clustering were executed.

For zero-based particle slot j in 0..699, columns `3*j`, `3*j+1`, `3*j+2` are
pT [GeV], eta [dimensionless], phi [radians]. Column 2100 is the float64 truth
bit: 0 background, 1 signal. GeV/radian interpretation is based on the source
documentation/example and Delphes conventions, not a self-describing unit header.
There are no categorical particle IDs/types/charges to encode. The fixed storage
ceiling is 700; it is not an empirical maximum or selected model length.

## Bounded data-quality observations

Executed `python scripts/audit_raw_data.py` in the installed project environment.
The script fixes **32 equally spaced row ordinals** using
`np.linspace(0, 1099999, 32, dtype=np.int64)`, including both endpoints. No
selection by label or kinematics occurred. Its sample payload is 537,856 bytes;
HDF decoding reads whole compressed chunks (up to about 33 MB uncompressed for
these dispersed numeric-row chunks), not the entire 18.49 GB array.

- Zero NaNs, infinities, negative pT slots, empty rows, or unexpected truth values
  among the 32 sampled rows.
- Observed truth values `{0.0, 1.0}`; no full-file class counts computed.
- 16,890 zero-pT slots; every sampled zero-pT slot has eta=phi=0.
  Padding is a suffix in each sampled row; no valid particle follows padding.
- Valid-particle counts are 74..301, mean 172.1875, **in this sample only**.
  These are structural capacity observations, not population quantiles or L
  selection evidence. No signal/background multiplicity comparison was made.
- No sampled valid-particle phi lies outside [-pi, pi]. No other sentinel was
  observed; absence of other sentinels/full-file anomalies remains unproven.
- Sampled stored indexes agree with ordinals; full index uniqueness not checked.

Structural sample results are not full-dataset quality guarantees or
representative physics/multiplicity measurements, and cannot set model choices.
The full reusable findings JSON is local/ignored beside the raw artifact; this
document retains only curated structural findings, not event values or outputs.

Reader environment: Python 3.12.12, NumPy 2.5.3, h5py 3.16.0, HDF5 2.0.0,
hdf5plugin 7.1.0 on macOS ARM64.

## Operational test embargo

1. Raw bytes may be read for file hashes and HDF schema/integrity checks. A bounded
   class-agnostic sample may inspect finite values, truth encoding, padding, and
   malformed rows. Do not use it to tune features/cuts or compare signal/background.
2. Treat all statistical exploration as blocked until duplicate grouping and
   deterministic membership are established. Task 0002's seed 1729 and expected
   background 70/15/15 ratios remain intended policy, not existing assignments.
3. A future integrity pass may access labels for allocation and duplicate-conflict
   detection, but must expose only audit counts/membership to analysis. Create
   explicit training-background access; retain source ordinals and group aliases.
4. EDA for scalers, feature decisions, numerical thresholds, or sequence length
   uses training background only. Background selection-validation checks only
   predeclared criteria; separate calibration-validation sets thresholds later.
5. Preserve Task 0002's stronger initial rule: **no validation anomalies**. All
   two-prong signals are test-only; three-prong/black boxes remain reserved.
   Changing this requires an explicit new protocol, not interpreting labels as
   permission to tune. Never explore final-test physics for iterative decisions.
6. Freeze preprocessing/model comparison protocols before evaluation access.
   Record exposure if test results prompt changes; reusing an exposed population
   cannot restore it to an untouched test. No raw/sample event values belong in
   public reports, and labels/IDs/hashes are not model features.

## Exact duplicate preparation

Task 0004 should execute the canonical raw-particle SHA-256 strategy in
[data-design.md](data-design.md#4-deterministic-population-and-split-contract):
exclude labels/source IDs/splits; remove verified zero padding; canonicalize
signed zero and periodic angle representation; lexicographically sort valid
triplets; encode count and little-endian float64 values before float32 rounding.
These are integrity canonicalizations for a future pass, not model transforms
implemented here. Source float64 supports the pre-rounding encoding. Specify the
particle count as an unsigned 64-bit little-endian integer, then sorted triplets
as contiguous C-order little-endian float64 bytes. Preserve already-canonical
angles; only out-of-interval angles need future periodic canonicalization.
Version that numerical rule before implementation. Quarantine conflicting labels
and retain aliases.

Use a chunked single pass plus digest grouping/sorting, not all-pairs comparison.
For 1.1 million events, 32-byte digests require 35.2 MB; int64 source ordinals
8.8 MB and uint8 labels 1.1 MB before sorting/metadata overhead. Those are
calculated budgets, not measured throughput or actual duplicate incidence.
Python dictionaries/hex strings add substantial overhead; compact arrays or
bounded shard sorting are sufficient directions. Full duplicate detection and
fuzzy matching are not implemented or run by Task 0003.

The actual float64 block can be streamed in roughly 1,000-row slices (16.81 MB
numeric payload before working copies), without loading the whole matrix.
Per-event sorting costs O(N log N), N<=700; digest grouping can sort the compact
index. Runtime and duplicate incidence are not measured here. Thus exact hashing
is feasible as a bounded-memory linear file pass plus sorting in Task 0004;
all-pairs event comparison is unnecessary. The 32-row audit does not establish
that the dataset is duplicate-free.

## Open questions for Task 0004

- Full integrity/padding/nonfinite incidence and source-index consistency.
- Exact duplicate groups, conflicts, aliases, and deterministic membership.
- Training-only multiplicity/tails and empirical dev-subset coverage.
- Float32 precision tolerances and raw-reader/chunk/shard choices.
- Training-only numerical behavior needed to confirm the proposed feature policy.
- Sequence-length retention/hardware budget; no L is selected here.

**Next: Task 0004 — Training-Background EDA and Schema Validation.** Establish
integrity grouping/access before EDA; preprocessing/model implementation remains
a later task.
