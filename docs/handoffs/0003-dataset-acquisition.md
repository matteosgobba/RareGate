# Task 0003 — Verified Dataset Acquisition and Raw Schema Audit

## Metadata

- Task number: 0003
- Task name: Verified Dataset Acquisition and Raw Schema Audit
- Project phase: initial data implementation
- Date: 2026-10-04 (Europe/Rome)
- Status: completed and validated; awaiting user commit/push
- Git branch: `main`, tracking `origin/main`
- Base commit: `182ff319e6a67cd1d88721a7c78e85cbc9d6890b`
- Environment: user-specified MacBook Pro M5; verified macOS 26.6.2 ARM64,
  Python 3.12.12, existing `.venv`; NumPy 2.5.3, PyTorch 2.14.1, pytest 9.1.1,
  Ruff 0.16.10, h5py 3.16.0/HDF5 2.0.0, hdf5plugin 7.1.0.

## Objective

Implement verified acquisition of the pinned LHCO R&D v5 particle source and
perform a bounded structural/integrity audit. Preserve the
[original specification](../prompts/0003-dataset-acquisition.md).

## Scope

In scope: repository/source inspection, streamed acquisition, checksums, local
provenance, unit tests, real download, bounded schema audit, and documentation.
Out of scope: full EDA, normalization, engineered features, processed tensors,
materialized splits, model training, plots, and systems benchmarking.

## Changes

- Inspected required design/protocol/handoff documents, README, configuration,
  existing source/tests, Git status/branch/HEAD/history, and instruction files.
  Starting tree was clean. Task 0001 is commit `0930b03`; Task 0002 is `182ff31`;
  local `origin/main` matches HEAD. Historical handoffs remain unchanged; the
  index records Task 0002's now-verified commit status.
- Cross-checked pinned metadata against the official Zenodo API before encoding
  it. Implemented acquisition and unit-tested it before real downloading.
- Installed the project with optional data dependencies and acquired the real
  2.91 GB file. Exact size and MD5 verification completed before promotion.
- Inspected HDF metadata and 32 class-agnostic rows with a reproducible audit
  script. Discovered/handled Blosc compression; recorded actual schema findings.
- Updated acquisition instructions, raw audit, current status/roadmap, and index.
  No dataset, processed arrays, or final split assignments entered Git.

## Technical Decisions

### Source and integrity

Source: [Zenodo record 6466204](https://zenodo.org/records/6466204), v5,
DOI `10.5281/zenodo.6466204`, CC BY 4.0,
`events_anomalydetection_v2.h5`. Expected/actual size: **2,908,260,409 bytes**.
Expected/actual MD5: **629789d55813be3860781b084ae7f1de**.
Actual SHA-256:
`5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6`.
Acquisition/first verification UTC: `2026-10-04T11:05:47.545875+00:00`.

[Authoritative API](https://zenodo.org/api/records/6466204) agrees with all Task
0002 values; no discrepancy found. Direct URL:
<https://zenodo.org/api/records/6466204/files/events_anomalydetection_v2.h5/content>.
Initial free disk space was approximately 249 GiB; the CLI also checked sufficient
space before downloading. Existing ignore rules cover the raw/state paths.

### Acquisition behavior

Use standard-library urllib, 1 MiB reads, 60-second socket timeout, exact byte
count plus streamed publisher MD5 and independent SHA-256. Download to an
exclusive sibling `.part`; verify before same-directory atomic promotion.
HTTP errors, timeouts, ordinary interruptions, and invalid downloaded bytes fail
without accepting a final artifact; owned failed partials are cleaned. A crash
or forced kill may leave a stale `.part`; another invocation refuses to clobber
it. Confirm no active download, remove the stale partial deliberately, then retry.
Range resume/automatic retry is not implemented; retries restart from zero.

Existing valid artifacts are rehashed and reused without HTTP. Invalid existing
artifacts fail unless `--replace-invalid` is supplied; after successful replacement
verification, previous bytes remain in a uniquely named `.invalid-*` sibling.
Failed download/verification leaves the existing artifact intact. Symlinks and
non-file destinations are refused. Run one acquisition per destination.

Default portable data root is discovered from cwd ancestors or the installed
editable source checkout; `--data-dir` supplies a root outside a checkout.
Static publisher facts live in Python source. Actual local state is an ignored
JSON manifest with basename-relative file identity and UTC timestamps. Unchanged
verified-state reruns preserve manifest bytes/mtime. A valid external file with
missing state gets a null acquisition timestamp rather than an invented date.

### Raw schema and safeguards

Actual root group `/df` contains a pandas fixed-format frame: axis0/block0_items
`(2101,)` int64, axis1 `(1100000,)` int64, block0_values `(1100000,2101)` float64.
Numeric chunk shape `(62,2101)`, Blosc filter 32001; 18,488,800,000 uncompressed
numeric bytes. h5py slices avoid whole-DataFrame memory use. Column metadata is
verified 0..2100. Source documentation/official parsing example define 700
`(pT,eta,phi)` triplets plus the label at 2100; units follow documented GeV/radian
conventions, not a self-describing raw header. No object type/charge fields exist.

The fixed 32-row sample had zero NaNs, infinities, negative pT, empty rows,
unexpected labels, nonzero padding angles, or valid slots after padding. It
showed label values 0/1, 16,890 padded slots, multiplicities 74..301 (mean
172.1875), and sampled row-index/ordinal agreement. These are bounded structural
findings only; no full population quality, class counts, or physics comparisons.
See [the complete raw report](../raw-data-audit.md) for methods and limitations.

The report formalizes integrity-only raw access and requires duplicate grouping
and deterministic membership before training-background statistical EDA.
Task 0002's seed 1729, expected background 70/15/15 fractions, separate background
validation roles, and test-only signals remain intended policies, not materialized
splits. No validation anomalies are introduced. Exact hashing is prepared as a
future bounded-memory pass over canonical float64 particles, excluding labels/
IDs and encoding count as uint64 little-endian; no full duplicate pass ran here.

## Files

- Modified [main README](../../README.md), [data README](../../data/README.md),
  [project configuration](../../pyproject.toml), and [handoff index](README.md).
- Created [package initializer](../../src/latenttrigger/data/__init__.py),
  [source metadata](../../src/latenttrigger/data/metadata.py),
  [acquisition module](../../src/latenttrigger/data/acquisition.py),
  [acquisition tests](../../tests/test_acquisition.py), and
  [bounded audit script](../../scripts/audit_raw_data.py).
- Created [raw audit](../raw-data-audit.md), [prompt](../prompts/0003-dataset-acquisition.md),
  and this handoff. Twelve intended version-controlled text files in total.
- Local ignored files only: the HDF artifact, its acquisition manifest, and
  `raw-schema-audit.json` under `data/raw/lhco/6466204/`. No leftover partials.

## Dependencies

Only added optional `data` dependencies in pyproject.toml:
`h5py>=3.12,<4`, `hdf5plugin>=7.1,<8`. Both installed as macOS ARM64 wheels.
h5py alone can inspect metadata but the real source's Blosc filter blocked its
first content read. The plugin registers that decoder and resolved the failure;
[maintainer documentation](https://hdf5plugin.readthedocs.io/en/stable/usage.html)
and actual filter metadata justify the additional dependency.
No requests, pandas, PyTables, or future data/ML stack was added. Core dependency
ranges, Python support, CI, device utilities, and .gitignore remain unchanged.
Acquisition tests/CLI require no optional HDF packages or network access in CI.

## Validation

Executed from the checkout on 2026-10-04:

| Command / check | Actual outcome |
| --- | --- |
| `.venv/bin/python -m pip --no-cache-dir install -e '.[dev,data]'` | Editable install passed, including the final Blosc dependency. |
| `.venv/bin/python -m pip --no-cache-dir check` | No broken requirements. |
| `.venv/bin/python -c 'import latenttrigger; print(latenttrigger.__version__)'` | Import passed; version 0.1.0. |
| `.venv/bin/python -m pytest tests/test_acquisition.py` | 28 acquisition tests passed, no real downloads. Initial 21 passed before downloading; later cases cover additional safety. |
| `.venv/bin/python -m pytest` | 32 passed: 28 acquisition plus 4 existing foundation tests. |
| `.venv/bin/python -m ruff check .` | All checks passed. |
| `.venv/bin/python -m ruff format --check .` | Passed; 23 files already formatted at final code check. |
| `.venv/bin/python scripts/smoke_test.py` | CPU sandbox diagnostic passed, result 16.0. |
| Same smoke command with native GPU access | MPS available; tensor mps:0, result 16.0, passed. |
| `.venv/bin/python -u -m latenttrigger.data.acquisition` with network escalation | Real file downloaded; exact size/MD5 matched; verified promotion completed. |
| `.venv/bin/python -u scripts/audit_raw_data.py` | Reverified existing source; HDF metadata/content readable; bounded quality checks passed. |
| Audit replay through Python subprocess | Passed; source identity included, same schema/findings, acquisition manifest bytes/mtime unchanged, no partial files. |
| Git status, tracked/untracked diff review, `git diff --check` | Only intended text changes; no data or staged files; whitespace check passed. |
| One-off documentation/artifact audit and `git check-ignore` | Relative links resolve; raw file, partials, manifests/audit JSON, backups, caches remain ignored; no large/generated binary or credentials among changes. |

No hosted GitHub Actions run or Python 3.11 execution was performed; configured
CI is not claimed as a newly observed success. Local validation used Python 3.12.

## Results

The actual corrected dataset was acquired, checksum-verified, and bounded-audited.
The CLI can reproduce/revalidate acquisition, and controlled tests cover invalid,
partial, HTTP, timeout, existing-file, manifest, space, and destination behavior.
The raw audit and operational embargo provide a concrete Task 0004 starting
point. No preprocessing/model functionality or benchmark result was produced.

## Issues / Limitations

- The web tool could not retrieve the JSON API; direct official HTTPS succeeded.
- Plain h5py initially could not decode Blosc; resolved with the optional plugin.
- Only 32 class-agnostic rows were content-audited, plus small column metadata.
  Full nonfinite/padding incidence, row-index uniqueness, exact duplicate counts,
  and class populations were not scanned. Units are source-supported conventions
  with no unit attribute in the raw file; mass/charge/type information is absent.
- Maximum raw capacity 700 is not a chosen sequence limit. No model L, precision
  tolerance, full multiplicity quantiles, or dev-subset coverage was determined.
- Interrupted retries restart from zero; forced kills require stale-partial
  cleanup. Invalid backups consume disk space until deliberately removed.

## Rejected Alternatives

Rejected old raw files/floating versions, existence-only checks, unverified final
promotion, silent invalid-file overwrites, full-file RAM loading, requests for
simple HTTPS, pandas/PyTables just to read this numeric block, resumable-download
frameworks, and arbitrary final splits/EDA before integrity grouping.
Added the compression plugin only after actual source evidence required it.

## Reproducibility

Activate the project environment; install `.[dev,data]`; run
`python -m latenttrigger.data.acquisition`, then
`python scripts/audit_raw_data.py`. See [data instructions](../../data/README.md).
Static metadata and local verified state are separate; manifests contain no
machine-specific absolute paths and unchanged revalidation preserves timestamps.
The audit uses a fixed 32-row ordinal rule and reports reader versions. Keep all
local data/state ignored; commit source, tests, prompt/handoff, and documentation
together. Base commit above identifies prior code; implementation is uncommitted
at handoff time. Prompt requested intent and handoff factual outcomes are distinct.

## Follow-up

**Task 0004 — Training-Background EDA and Schema Validation.** Begin with bounded
full-file integrity/duplicate grouping and deterministic membership/access; then
restrict statistical EDA to training background. Resolve full quality counts,
training multiplicity/tails, source-index behavior, precision tolerances,
dev-subset coverage, and reader/chunk/L policies. No models yet.

## Git

Nothing staged, committed, or pushed by Codex. Base remains
`182ff319e6a67cd1d88721a7c78e85cbc9d6890b`; no Task 0003 commit hash exists.
Suggested message: `feat: add verified LHCO dataset acquisition`.
`main` already tracks `origin/main`; use normal `git push` after selective
staging/review of the twelve task files. Never stage local raw/state files.
