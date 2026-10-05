# Deterministic LHCO preprocessing — schema 1

Task 0005 implements the [frozen contract](preprocessing-contract.md) and uses
[the exact Task 0004 configuration](../configs/data/lhco_rnd_v5.json) without
refitting. No model has been trained. Acquisition, splitting, preprocessing and
evaluation remain separate steps.

## Verified inputs

Only the corrected LHCO R&D v5 file from Zenodo record 6466204 is accepted:
`events_anomalydetection_v2.h5`, 2,908,260,409 bytes, publisher MD5
`629789d55813be3860781b084ae7f1de`, SHA-256
`5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6`.
The source and all Task 0004 split artifacts are verified before building.
The CLI does not download missing data or silently regenerate membership.

Source: `/df/block0_values`, float64 `[1100000,2101]`; first 2100 columns are
700 `(pT,eta,phi)` triplets, final column is truth. Reads are bounded to 992
selected rows by default, about 16.7 MB of numeric source data per chunk.
Contiguous IDs use HDF slicing; sparse dev membership uses sorted fancy indexing.
Hashes, labels and multiplicities are compared with Task 0004 for each chunk.
Malformed, empty, nonfinite or inconsistent events block finalization rather
than disappearing silently. Exact groups use the original lowest-ordinal
representatives; the Task 0004 manifest preserves aliases (none in this source).

## Canonical representation and model views

The canonical particle record contains **all real physical FP32 particles** in
channel order `[pt_GeV, eta, phi_rad]`, with no padding or truncation. Ragged
offsets allow reconstruction and alternative sequence-length experiments without
decompressing raw HDF again. Arrays are primitive little-endian NPY files with
no pickle/object arrays. Incremental writes use NumPy
[open_memmap](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.open_memmap.html).
The bounded sparse reads follow
[h5py's documented fancy-indexing constraints](https://docs.h5py.org/en/stable/high/dataset.html#fancy-indexing).

Signed zeros are normalized. Phi outside `[-pi,pi)` is wrapped in float64;
in-range source values are preserved. Full-event sorting uses **source float64**:
descending pT, ascending eta, ascending wrapped phi, ascending original slot.
Only then are physical values cast to FP32. On-demand views preserve this order;
re-sorting rounded ties would violate the contract.

The default model view is FP32 `[B,384,4]`:

1. `(log1p(pT / 1 GeV) - pt_mean) / pt_std`;
2. `(eta - eta_mean) / eta_std`;
3. `sin(wrapped phi)`;
4. `cos(wrapped phi)`.

Transforms compute in float64 from canonical physical values, with one final
FP32 cast. Exact scalers come from the verified configuration snapshot; no
fitting API exists. A rounded FP32 phi can lie just outside the mathematical
interval, so angular evaluation wraps again, preserving periodic semantics.

Retain the first `min(N,Nmax)` particles, with explicit alternative integer
Nmax in `[1,700]`. Transform real retained particles first, then pad with exactly
four zeros. Boolean mask **True = real retained particle**, False = padding;
True entries form a prefix. Return original and retained multiplicities and
retained scalar-pT fraction separately. No IDs, truth, slots or split metadata
enter model channels. A full `[1100000,384,4]` array alone would use 6.76 GB;
it is not persisted.

## Aggregates

Eight channels, permanently ordered: `multiplicity`, `scalar_pt`, `max_pt`,
`pt_balance`, `weighted_eta_mean`, `weighted_eta_std`, `pt_concentration`,
`massless_event_mass`. See the contract for exact formulas, units and mass²
roundoff rule. Compute from **all canonical physical particles before truncation**
with float64 accumulation. Store physical float64 quantities for interpretation
and bias checks, plus the small standardized FP32 baseline view. Log1p applies
only to channels 0, 1, 2 and 7 before frozen event-level standardization.
Persisting both eight-channel arrays costs 105.6 MB for the full source, rather
than duplicating the particle store or materializing padded model tensors.

## Local layout

Everything below this generated directory is ignored by Git:

```text
data/processed/lhco-rd-v1/schema-v1/
├── dev/                         # 8,494 fixed allowed-background representatives
├── dev-repeat/                  # Independent reproducibility check
└── full/                        # All 1,100,000 frozen representatives
```

Each finalized store contains:

| File | dtype / shape | Meaning |
| --- | --- | --- |
| `particles.npy` | float32 `[P,3]` | All sorted physical particles |
| `original_slots.npy` | uint16 `[P]` | Source-slot provenance, never a feature |
| `offsets.npy` | int64 `[E+1]` | Start/end into particle records |
| `event_ids.npy` | int64 `[E]` | Increasing source row ordinals |
| `multiplicities.npy` | uint16 `[E]` | Original particle counts |
| `event_aggregates.npy` | float64 `[E,8]` | Full physical aggregates |
| `event_features.npy` | float32 `[E,8]` | Frozen standardized baseline view |
| `labels.npy` | uint8 `[E]` | Separate evaluation truth, 0/1 |
| `split_codes.npy` | uint8 `[E]` | Frozen role codes 1–5 |
| `development.npy` | bool `[E]` | Fixed dev membership flag |
| `fingerprints.npy` | 32-byte void `[E]` | Task 0004 exact-content group identity |
| `configuration.json` | JSON | Exact unmodified fitted/configuration snapshot |
| `manifest.json` | JSON | Schema, scientific identity and separate build record |

Identity of an event is `(source SHA-256, raw ordinal)`; the fingerprint is
separate content identity. Physical arrays are never evaluation labels.

## Provenance, determinism and integrity

The manifest's scientific section records pinned source/size/MD5/SHA-256,
configuration hash, stable split identity/hash (seed, protocol, group-hash
version, dev policy, counts and all input array hashes), channels, default Nmax,
all output sizes/dtypes/shapes/SHA-256 hashes. Its canonical-JSON SHA-256 excludes
timestamps, chunk size, output path and host environment. Independent runs with
identical scientific outputs therefore have the same identity.

A separate build section records UTC creation, project/code version, dirty
source state and source-module hashes, runtime versions, input split-manifest
hash, chunk size, technical precision diagnostics, write/hash and verification
timings, and process-lifetime peak RSS. No absolute machine paths are recorded.
Local acquisition timestamps remain beside the raw file; raw content hashes
provide the stable link. Exact configuration bytes are copied, never rewritten.

Verification hashes every file and checks the complete schema, finite physical
values, offsets/multiplicity, pT ordering, unique slots/group fingerprints,
source ordinals, expected population/dev counts, label-role integrity, and
recalculated standardized aggregate values. Hashes detect byte corruption;
they are not authenticated signatures. Verification can run independently of
the raw file and network. It does not refit statistics or explore test physics.

Builders reserve an exclusive sibling lock and write a sibling `.partial`
directory. They estimate new output plus `max(512 MiB,10%)` headroom and verify
everything before promoting the directory. Existing verified compatible output
is reused; invalid/incomplete/incompatible output requires explicit `--rebuild`.
Successful replacement retains the old directory as `NAME.previous-<unique-id>`.
If replacement fails, the original remains recoverable; promotion failure rolls
it back. Ordinary failure removes only this invocation's staging directory.
A hard kill can leave a lock/partial: confirm no builder is running before
deliberately removing those siblings. Never accept a partial directory as a
store. No automatic resume or backup deletion is implemented.

## Reader and test embargo

`ProcessedStore` fully verifies on open, maps arrays read-only and returns owned,
bounded NumPy batches. Closing it releases its mappings; returned batches remain
usable. A maximum of 4,096 events per batch limits accidental large reads.
Use one explicit primary split; the two validation roles stay separate.

```python
from pathlib import Path
from latenttrigger.data.processed import ProcessedStore

with ProcessedStore(Path("data/processed/lhco-rd-v1/schema-v1/full")) as store:
    batch = store.read("train_background", slice(0, 32), dev_only=True)
    physical, baseline = batch.particles, batch.event_features
    view = batch.model_view()  # [B,384,4], bool [B,384]
    shorter = batch.model_view(nmax=256)  # Explicit future controlled experiment
    assert batch.labels is None
```

`read_ids(split, integer_source_ids)` resolves selected raw ordinals;
`event_ids(split)` and `iter_batches(split,batch_size=256)` support deterministic
selection without Python event-object lists. Requests outside the chosen split
fail. Test reads require **allow_test=True**. Truth additionally requires
**include_labels=True** and an explicit test split; the ordinary reader does
not map labels into batches. These are methodological safeguards, not encryption.
Full preprocessing applies an already-frozen function to test events; only
technical integrity/precision checks inspect them. No test distributions,
signal-informed tuning or test model performance were used in Task 0005.

## Commands and reproduction

From an editable checkout, with dependencies and Task 0004 membership available:

```bash
python -m pip install -e ".[dev,data]"
python -m latenttrigger.data.acquisition --verify-only
# If membership is missing, reproduce Task 0004's integrity/group/split stage:
python scripts/analyze_training_data.py --scan-only
python -m latenttrigger.data.preprocessing --scope dev
python -m latenttrigger.data.preprocessing --scope dev --chunk-rows 496 \
  --output data/processed/lhco-rd-v1/schema-v1/dev-repeat
python scripts/validate_preprocessing.py \
  --repeat data/processed/lhco-rd-v1/schema-v1/dev-repeat
python -m latenttrigger.data.preprocessing --scope full
python -m latenttrigger.data.preprocessing --verify data/processed/lhco-rd-v1/schema-v1/full
```

Do not rerun fitting/EDA to replace the tracked frozen configuration.
Outside a checkout use explicit `--data-dir`, `--config` and optionally `--output`.
No-argument preprocessing fails with usage; an expensive scope must be chosen.
`--rebuild` deliberately replaces a selected output only after successful
verification. `scripts/validate_preprocessing.py --store .../full` verifies the
full store but restricts semantic spot checks and model views to dev background.
It writes a small ignored report under data; it is a real-data validation script,
not a CI dependency or a new EDA stage.

## Measured execution

On macOS ARM64/Python 3.12.12 with 16 GiB RAM, the 992-row dev build retains
8,494 events and 1,549,328 particles. Output is 23,055,615 bytes. Writing plus
hashing took 4.75 s, output verification 0.086 s, lifetime peak RSS 298 MiB.
A second independent 496-row build took 5.28 s plus 0.087 s verification, peak
252 MiB, and all 11 NPY files/configuration/scientific hashes were identical.
Model features, masks, provenance/order and truncation metadata also matched
for every dev event. Exactly 27 dev events truncate at Nmax384.

The full build retains 1,100,000 events / 195,918,046 particles, consuming
2,906,852,158 bytes including metadata. Writing/hashing took 143.77 s,
verification 6.37 s, peak lifetime RSS 2.44 GiB; 992-row chunks were used.
Its scientific identity is
`d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2`.
All frozen population counts, file hashes and source/split identities passed.
The full raw cast error is zero in all three channels; two phi values require
wrapping, with maximum subsequent FP32 angular error 6.3573e-8 rad. Zero padding
remains exact; no events would change order from an extra rounded-value sort.

These timings exclude input/raw integrity verification and are engineering
observations, not inference benchmarks. Details are recorded in
the [Task 0005 handoff](handoffs/0005-preprocessing-pipeline.md).

Dev raw source values round-trip to FP32 without error; no boundary wrap was
needed there. Six deterministic raw-event spot checks, including 456- and
408-particle events, matched source ordering/slots/physical arrays exactly.
Independent scalar-math aggregate calculations differ by at most 1.82e-12;
their standardized FP32 baseline and model-channel results matched exactly.
Synthetic tests exercise rounded ordering ties, signed zero, angular boundaries,
large pT, each aggregate, 383/384/385/700 boundaries and alternate Nmax.
