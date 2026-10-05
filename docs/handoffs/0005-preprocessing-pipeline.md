# Task 0005 — Deterministic Preprocessing Pipeline

## Metadata

- Task/phase: 0005, production data preprocessing
- Date: 2026-10-05 (Europe/Rome)
- Status: completed locally; awaiting user review, commit/push
- Branch/upstream: main / origin/main
- Base: `cd3d24a11792e6dd8911185e12233a2930ae6ec4`
- Environment: macOS 26.6.2 ARM64, user-specified M5, 16 GiB RAM,
  Python 3.12.12, NumPy 2.5.3, h5py 3.16.0, hdf5plugin 7.1.0,
  PyTorch 2.14.1, pytest 9.1.1, Ruff 0.16.10.

## Objective / Scope

Implement the frozen Task 0004 contract: verified existing membership, all-particle
ragged physical records, fixed transformations/scalers, full-event aggregates,
on-demand model views, guarded reading, versioned provenance and verification.
Validate dev twice before full. No refitting, model training, test-signal physics
EDA, baseline fitting, deployment or inference benchmark was performed.

## Inspection

Starting tree was clean. Tasks 0001–0004 are committed; Task 0004 is HEAD cd3d24a.
Development protocol, contract, EDA, configuration, Task 0004 handoff, data policy
and acquisition/inspection/analysis/splitting code were reviewed. All 20 local
Task 0004 array artifacts and deterministic group-safe membership were verified;
no split was replaced. Initial disk free: 264,627,941,376 bytes. Historical
handoffs, configuration and existing source modules were not edited.

## Source / Integrity

LHCO R&D v5, Zenodo record 6466204, DOI
[10.5281/zenodo.6466204](https://doi.org/10.5281/zenodo.6466204), corrected
`events_anomalydetection_v2.h5`, ignored `data/raw/lhco/6466204/`.
Source metadata is inherited from Task 0003's publisher verification; no source
was redownloaded or changed. Locally reverified before dev/full and during reuse:

- Size: **2,908,260,409 bytes**.
- MD5: **629789d55813be3860781b084ae7f1de**.
- SHA-256: **5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6**.
- Exact unmodified config SHA-256:
  `2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68`.
- Stable split identity SHA-256:
  `74a97d8956a4b75d5710d456bc207fdfa9d27569256bafe7b8e72a7891468fea`.
- Input split-manifest bytes SHA-256 (including local Task 0004 metadata):
  `a94af59fa842ca24816c38170b3cf58698748a85cd865d65b6e3fa4f615bdc43`.

## Changes / Files

Created `src/latenttrigger/data/features.py`, `preprocessing.py`, `processed.py`;
`tests/test_features.py`, `tests/test_preprocessing.py` (30 additional tests);
`scripts/validate_preprocessing.py`; `docs/preprocessing-pipeline.md`; Task 0005
prompt and this handoff. Updated `.github/workflows/ci.yml`, `README.md`,
`data/README.md`, and handoff index (Task 0004 commit verified; Task 0005 added).
No dependency/config/old handoff/raw source changes.

## Technical Decisions

Schema 1 under ignored `data/processed/lhco-rd-v1/schema-v1/{dev,full}`. Eleven
primitive little-endian NPY arrays plus exact configuration and JSON manifest:
all physical FP32 particles, original slots, ragged offsets, ordinal IDs,
multiplicity, physical float64 aggregates, standardized FP32 baseline features,
separate truth/role/dev metadata and exact group fingerprints. All particles
retained; original slots never enter model features. No pickle/object arrays.

Normalize signed zero; wrap only out-of-range source phi in float64. Sort source
float64 by descending pT, ascending eta, wrapped phi, original slot before casting.
Views preserve that order rather than re-sorting rounded ties. Object channels
are standardized log1p(pT/1GeV), standardized eta, sin/cos wrapped phi, using
frozen exact means/stds and float64 arithmetic with final FP32 cast. No fitting API.
Default Nmax384, leading prefix, zero padding after transformation, mask True=real;
explicit alternative Nmax1–700. Return original/retained N and retained-pT fraction.

Eight full-event aggregates compute from all canonical particles with float64
accumulation before truncation: multiplicity, scalar_pt, max_pt, pt_balance,
weighted_eta_mean, weighted_eta_std, pt_concentration, massless_event_mass.
Log channels 0/1/2/7 then apply frozen event scalers. Physical plus standardized
aggregate arrays cost 105.6 MB full and preserve bias interpretation.

Inputs/source hashes, membership counts and every chunk's raw content fingerprint,
label and multiplicity are checked. Bounded HDF reads (default 992 rows) and
incremental memmaps avoid the 18.49 GB full decompressed source. Scientific content
identity includes stable input/config/split semantics and all artifact hashes.
UTC, chunk size, environment, timings/RSS, base/dirty code hashes are separate
build metadata; manifests contain no absolute paths. Raw acquisition metadata
remains linked by source hashes. No deviation from the frozen contract was needed.

Exclusive sibling lock; disk estimate plus max(512 MiB,10%) margin; sibling staging;
verify before promotion. Valid compatible output reuses bytes. Explicit rebuild
preserves prior output until replacement passes, then retains a recoverable
`.previous-<unique-id>` backup. Ordinary failure cleans only owned staging; hard
kill may leave locks/partial, which require deliberate recovery.

## Dependencies

No additions; pyproject unchanged. Existing NumPy and optional data extra suffice.
CI now installs `[dev,data]` for small Blosc HDF integration fixtures, independent
of network datasets/GPU. No analysis/Matplotlib dependency is needed for production.
The first editable-install attempt with no build isolation failed because Hatchling
was absent; normal isolated pip installation then passed. This build-only backend
requirement did not change project dependencies.

## Results / Generated Artifacts

| Store | Events | Particles | Total bytes including metadata | Scientific SHA-256 |
| --- | ---: | ---: | ---: | --- |
| dev | 8,494 | 1,549,328 | 23,055,615 | `2eb34e5b811c12ae5c47afba1ecdb6322feb7c7774b6c9ec5331abe78b3c9a2a` |
| dev-repeat | 8,494 | 1,549,328 | 23,055,615 | same as dev |
| full | 1,100,000 | 195,918,046 | 2,906,852,158 | `d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2` |

All 11 arrays/config files match byte-for-byte/hash/dtype/shape between independent
dev builds with chunks 992 vs496. Build metadata differs, scientific identity
matches. All dev model features, masks, aggregates, slot/order and truncation
metadata match. Dev roles remain 6,999 train /747 selection /748 calibration,
no test events. Exactly **27** dev events truncate at Nmax384; all canonical
particles remain stored.

Full counts: **699,957** train background; **74,749** selection-validation
background; **74,823** calibration-validation background; **150,471** test
background; **100,000** test signal. Full IDs equal every source ordinal
0–1,099,999. Full/dev canonical and model views match for all 8,494 common allowed
background events. Truth is used only for membership integrity. No test-signal
physics distribution/model performance was explored. Generated stores, snapshots,
local reports/logs, split arrays and raw source remain ignored; no figures/new
fitted JSON were needed.

## Numerical Validation

Dev and full raw float64→float32 round-trip absolute/relative errors are zero
in all three channels. No dev phi needs wrapping; exactly two full source angles
do. Maximum subsequent wrapped FP32 angular error: **6.357301884918343e-8 rad**.
Zero padding remains exactly zero. No real event changes order in the rounded-sort
diagnostic; adversarial synthetic tests nonetheless prove source-before-cast order.

Six independent scalar-math spot checks on dev background:

| Source ordinal | Role | N |
| ---: | --- | ---: |
| 131 | train | 168 |
| 94565 | train | 456 |
| 790 | selection validation | 228 |
| 352116 | selection validation | 376 |
| 768 | calibration validation | 200 |
| 98598 | calibration validation | 408 |

Source reconstruction/slot order match exactly. Independent `math.fsum` aggregate
arithmetic differs by at most **1.8189894035458565e-12**. Standardized baseline and
object FP32 results match exactly. These checks also pass against full storage.
Synthetic tests cover each aggregate, tie keys, signed zero, angular boundary,
large pT, alternate Nmax, and 383/384/385/700 truncation boundaries.

## Performance / Resource Observations

| Operation | Chunk events | Write/hash seconds | Verification seconds | Peak lifetime RSS |
| --- | ---: | ---: | ---: | ---: |
| dev | 992 | 4.754 | 0.086 | 312,262,656 bytes (298 MiB) |
| dev-repeat | 496 | 5.277 | 0.087 | 264,683,520 bytes (252 MiB) |
| full | 992 | 143.771 | 6.366 | 2,615,328,768 bytes (2.44 GiB) |

Times exclude raw checksum/input-membership verification; these are engineering
observations, not inference benchmarks. Full estimate: 2,906,909,467 bytes plus
536,870,912 safety margin, with 262,085,070,848 free before staging. No raw deletion.
Independent full verification/dev semantic script also passed: 6.19 s and
2,818,883,584 bytes lifetime RSS. Mmap caching contributes resident output pages;
full decompressed source is never loaded.

## Validation

Actual commands used `.venv/bin/python` / `.venv/bin/ruff`:

```bash
python -m pip install --no-deps -e ".[dev,data,analysis]"
python -m pip check
python -c "import latenttrigger; print(latenttrigger.__version__)"
ruff check .
ruff format --check .
python -m pytest
python -m latenttrigger.data.acquisition --verify-only
python -m latenttrigger.data.preprocessing --scope dev
python -m latenttrigger.data.preprocessing --scope dev --chunk-rows 496 \
  --output data/processed/lhco-rd-v1/schema-v1/dev-repeat
python scripts/validate_preprocessing.py \
  --repeat data/processed/lhco-rd-v1/schema-v1/dev-repeat
python -m latenttrigger.data.preprocessing --scope full
python -m latenttrigger.data.preprocessing --verify data/processed/lhco-rd-v1/schema-v1/full
python scripts/validate_preprocessing.py --store data/processed/lhco-rd-v1/schema-v1/full \
  --report data/task0005-full-validation.json
python -m latenttrigger.data.preprocessing --scope dev
python scripts/smoke_test.py
git diff --check
```

Editable install passed; pip check reports no broken requirements; import **0.1.0**.
Ruff lint/format pass. Full pytest suite **84 passed** (54 existing +30 new).
CPU smoke passed with MPS availability patched false; native MPS smoke outside
sandbox passed with MPS available; both result16. Raw integrity/dev/full verification
passed; CLI rerun verified reuse without build. Dev finite outputs, exact count/
multiplicity/identity, masks/zero padding/truncation and absent labels passed.
Full independent verification and full/dev consistency passed. Tests prove corrupt
store refusal/rebuild, interrupted-build safety, disk-budget refusal, dtype/metadata
checks and test embargo. Final review passed: 72 relative links in 19 Markdown
files; all 62 inspected raw/processed/split files ignored; environments, caches,
logs, reports and partials ignored; all 13 task files remain trackable. Nine new
files are small and whitespace-clean. No credential/key patterns were found in
the 13 task files. Tracked diff/whitespace inspection passed; historical handoffs
and frozen config are unchanged. Git index is untouched; no binaries/data staged.
Hosted CI has not yet run.

## Issues / Limitations / Rejected Alternatives

No resource blocker remains. Production requires compatible frozen config/Task 0004
artifacts and the existing Blosc decoder. Reader verification costs seconds for
full; keep one verified reader open for repeated batches. Verification hashes are
corruption checks, not authenticated signatures. Cross-platform transcendental
last-bit identity is not claimed: same-environment builds match bytes; record
versions and validate numeric tolerances in other environments. No automatic resume
or stale-lock/backup deletion. First validation script run found record_id is an
integer; portable path conversion was corrected and both dev/full reruns passed.

Rejected: full source loading, persistent 6.76 GB padded tensors, transformed-only
canonical particles, extra storage/CLI dependencies, fitting new scalers, and
sorting rounded values. These limits do not alter the frozen scientific policy.

## Reproducibility / Follow-up

See [pipeline documentation](../preprocessing-pipeline.md) for exact commands,
schema and split/label guards. Ignored manifests contain all hashes/snapshots and
base/dirty source-module hashes, without inventing a future commit.
Next: **Task 0006 — Statistical Baseline and Evaluation Framework** using train
background for fitting and distinct selection/calibration roles. Final test remains
embargoed until model/operating-point policy freezes. No model exists yet.

## Git

No stage/commit/push performed. Base remains cd3d24a; no resulting commit exists.
Suggested: `feat: add deterministic LHCO preprocessing pipeline`. Prompt,
handoff/index, implementation/tests and documentation belong in one reviewed
commit; generated raw/processed/split/temporary data do not.
