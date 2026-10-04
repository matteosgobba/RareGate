# Task 0003 — Original user specification

Recorded 2026-10-04 from the original user message in the task conversation.
The specification below is preserved as supplied; its instructions describe
requested work, not evidence that the work has been completed.

<!-- BEGIN ORIGINAL USER SPECIFICATION -->

LatentTrigger — Task 0003: Verified Dataset Acquisition and Raw Schema Audit

You are continuing development of LatentTrigger.

Tasks 0001 and 0002 are complete and committed.

Task 0002 selected the LHC Olympics 2020 R&D dataset, Zenodo v5, with the corrected:

events_anomalydetection_v2.h5

as the primary initial dataset.

The project data design is documented in:

* docs/data-design.md
* data/README.md
* docs/handoffs/0002-data-foundation.md

Read those documents before making any implementation decision.

This task is the first data implementation task.

Its purpose is to build a safe, reproducible, verifiable acquisition layer and perform a bounded raw-schema audit of the actual downloaded dataset.

This task must NOT become the full exploratory data analysis or preprocessing phase.

⸻

0. Mandatory repository inspection

Before modifying anything:

* inspect the repository;
* inspect docs/development.md;
* inspect docs/data-design.md;
* inspect data/README.md;
* inspect Task 0002 handoff;
* inspect pyproject.toml;
* inspect .gitignore;
* inspect current Git status;
* identify the current branch;
* identify the current HEAD/base commit;
* verify Tasks 0001 and 0002 are committed;
* verify the working tree is clean or identify unrelated changes.

Do not overwrite or stage unrelated work.

Follow the permanent LatentTrigger handoff protocol.

⸻

1. Task records

This is:

Task 0003 — Verified Dataset Acquisition and Raw Schema Audit

Create:

docs/prompts/0003-dataset-acquisition.md
docs/handoffs/0003-dataset-acquisition.md

Add Task 0003 to:

docs/handoffs/README.md

The prompt record must preserve this task specification.

The handoff must document what actually happened.

⸻

2. Primary objective

Implement a reproducible acquisition mechanism for the pinned LHC Olympics R&D dataset and verify that the downloaded artifact is exactly the expected source.

The acquisition layer must answer:

1. Where does the file come from?
2. Which exact dataset/version is used?
3. Which exact file is expected?
4. How large should it be?
5. What checksum is expected?
6. Where is it stored locally?
7. How do we verify it?
8. What happens if the download is interrupted?
9. What happens if an existing file is corrupted?
10. Can acquisition be skipped safely when the verified file already exists?

The dataset itself must remain outside Git.

⸻

3. Source of truth

Use the authoritative source information established in Task 0002.

The expected dataset is:

LHC Olympics 2020 R&D dataset — Zenodo v5

and specifically:

events_anomalydetection_v2.h5

Before hardcoding metadata, verify it against the authoritative Zenodo record if network access is available.

Record in code/configuration or a small manifest, as appropriate:

* dataset name;
* dataset version;
* Zenodo record identifier / DOI;
* filename;
* authoritative download URL;
* expected file size;
* expected checksum and checksum algorithm;
* any relevant source metadata.

Do not invent values.

If Task 0002 contains authoritative values, cross-check them.

If a discrepancy exists between Task 0002 and the current authoritative source, stop and investigate it rather than silently choosing one.

Document any discrepancy in the handoff.

⸻

4. Acquisition architecture

Implement a small, maintainable data-acquisition module under an appropriate location such as:

src/latenttrigger/data/
    __init__.py
    acquisition.py

or another clean equivalent.

Avoid creating a generic framework for arbitrary datasets.

We currently need one robust dataset acquisition path.

The implementation should separate where practical:

* dataset metadata;
* download;
* integrity verification;
* local-path handling.

Keep the API simple.

A future developer should be able to understand the entire acquisition flow quickly.

⸻

5. Command-line entry point

Provide a convenient command for acquisition.

Prefer a project CLI/module invocation such as:

python -m latenttrigger.data.acquisition

or a well-justified equivalent.

The command should clearly report:

* selected dataset;
* destination;
* whether download is required;
* verification status;
* final result.

Do not require notebook execution.

⸻

6. Local data layout

Follow the existing data policy.

The raw source should live under a structure conceptually similar to:

data/
└── raw/
    └── lhco2020/
        └── events_anomalydetection_v2.h5

Choose the exact directory naming based on existing Task 0002 documentation.

Avoid unnecessarily deep paths.

The acquisition code must resolve the project/data path robustly.

Do not depend on the user’s absolute path:

/Users/matteosgobba/...

The repository must remain portable.

⸻

7. Git safety

Verify that downloaded data is ignored by Git.

After acquisition, git status must not list the HDF5 dataset.

Add or adjust .gitignore only if required.

Do not use broad ignore rules that would prevent intended documentation or curated small artifacts from being tracked.

⸻

8. Download behavior

The downloader should be robust enough for a large scientific artifact.

Implement appropriate behavior for:

* streamed download rather than loading the entire response into RAM;
* sensible chunking;
* temporary/partial file;
* atomic promotion to the final filename only after successful completion and verification;
* cleanup or safe handling of failed partial downloads;
* HTTP errors;
* timeouts;
* existing verified file;
* existing invalid file.

Do not silently overwrite a corrupted or unexpected file without informing the user.

If practical, support resume/retry behavior, but do not overengineer it if the source does not support reliable resumable downloads.

Correctness and clarity matter more than elaborate download management.

⸻

9. Integrity verification

This is mandatory.

Implement checksum verification using the authoritative checksum algorithm/value associated with the pinned source.

The verification should be independently callable where practical.

Expected behavior:

Missing file

Download → verify → accept.

Existing valid file

Verify → report valid → do not redownload.

Existing invalid file

Report checksum mismatch clearly and require an explicit safe action or replace it using a documented policy.

Newly downloaded invalid file

Do not promote it as the valid raw dataset.

Fail loudly.

Never treat file existence alone as proof of validity.

⸻

10. Dataset manifest / provenance

Task 0002 designed a provenance mechanism.

Implement the minimal acquisition-level portion now.

Create a small machine-readable manifest or metadata record containing appropriate fields such as:

dataset
version
source
doi
record_id
filename
expected_checksum
checksum_algorithm
verified_checksum
file_size
acquisition_timestamp

Do not create a database.

The manifest must not contain machine-specific absolute paths if that harms portability.

Be careful with acquisition timestamps and reproducibility: metadata that changes on every verification run should not cause unnecessary Git changes.

Decide whether the runtime manifest belongs under ignored local data or whether a static source manifest belongs in repository configuration.

Prefer separating:

static source metadata

from

local acquisition state

if that produces cleaner reproducibility.

Document the decision.

⸻

11. Dependencies

Add only dependencies justified by this task.

Before adding an HTTP dependency, inspect whether the Python standard library is sufficient.

Before adding HDF5 support, determine what library will be needed for the bounded schema audit.

h5py is acceptable if appropriate.

Do not add pandas merely for convenience unless actually justified.

Do not add future ML/data-stack dependencies prematurely.

Any dependency change must be documented in:

* pyproject.toml;
* Task 0003 handoff.

⸻

12. Unit tests for acquisition

Tests must NOT download the real multi-GB dataset.

Create unit tests using temporary directories and mocked/local responses as appropriate.

Test meaningful behavior including:

* checksum success;
* checksum failure;
* existing valid file;
* invalid file behavior;
* partial-download safety;
* destination handling;
* manifest/metadata correctness where applicable.

Tests must remain fast and suitable for GitHub Actions.

Do not make CI dependent on Zenodo availability.

⸻

13. Real dataset acquisition

After unit-testing the acquisition layer, use it to acquire the actual pinned R&D dataset on the development machine if network access and local storage permit.

Before starting the large download:

* determine expected size;
* ensure the destination is ignored by Git;
* inspect available disk space if possible;
* ensure sufficient free space exists.

If the environment cannot perform the real download, do not pretend that it did.

In that case:

* fully test the acquisition mechanism with controlled test artifacts;
* document the exact command the user must execute locally;
* mark real-file verification as pending.

If the real download is possible, perform it and verify its checksum.

⸻

14. Raw schema audit

Only after the actual dataset is successfully verified, perform a bounded raw schema audit.

This is NOT full EDA.

The goal is to replace assumptions from Task 0002 with facts about the actual file.

Inspect:

* HDF5 groups/datasets;
* array names;
* shapes;
* dtypes;
* total number of rows/events;
* event representation;
* number of columns/features;
* label location;
* particle/object layout;
* padding conventions, if any;
* sentinel values, if any;
* immediately observable metadata.

Do not scan the entire dataset unnecessarily if schema information can be obtained from HDF5 metadata.

Use small bounded samples when content inspection is necessary.

⸻

15. Verify feature semantics

Task 0002 contains assumptions about particle features.

Compare the actual file representation against authoritative documentation.

Determine, as far as authoritative evidence allows:

* which columns correspond to particle/object features;
* feature order;
* units;
* particle/object type encoding;
* event label encoding;
* whether zero-padding or another convention is already present;
* maximum raw object count if encoded in the file.

Do not infer physical semantics solely from numerical values when documentation exists.

If any feature meaning or unit remains uncertain, record it explicitly.

⸻

16. Bounded data-quality audit

Perform only checks required to validate the raw source and prepare Task 0004.

On bounded samples or metadata where appropriate, investigate:

* NaNs;
* infinities;
* obviously malformed rows;
* label values;
* zero/padding behavior;
* approximate object multiplicity behavior;
* exact duplicate detection strategy feasibility.

Do NOT perform:

* full distribution plotting;
* final multiplicity analysis;
* feature normalization design;
* truncation threshold selection;
* signal/background physics comparison;
* correlation analysis;
* model-oriented feature engineering.

Those belong to Task 0004.

⸻

17. Test embargo

Task 0002 established the principle that the final test set must remain held out.

Task 0003 must formalize operational safeguards before EDA.

Define and document a policy such as:

* schema/integrity checks may inspect the full raw file only where labels/distributions are not used for model decisions;
* statistical EDA used for preprocessing/model decisions must be restricted to training background;
* validation anomalies may later be used only for explicitly defined model-selection/calibration purposes;
* final test anomalies must not be explored for iterative model decisions.

Do not yet create arbitrary final splits before verifying the raw data and duplicate situation.

If Task 0002 already specifies expected split ratios, preserve them as intended policy but distinguish them from actually materialized splits.

⸻

18. Duplicate strategy preparation

Do not necessarily run an expensive all-pairs or full-file duplicate analysis in this task.

Instead:

* inspect whether exact duplicate detection is computationally feasible;
* define a deterministic hashing strategy for events;
* identify what representation should be hashed;
* estimate what Task 0004 needs to execute to prevent duplicate leakage across splits.

If exact duplicate detection is cheap enough and naturally belongs here, it may be performed, but document the computational method.

Do not implement fuzzy/near-duplicate detection unless evidence shows it is necessary.

⸻

19. Acquisition/schema report

Create:

docs/raw-data-audit.md

This document should contain:

Source

Exact pinned source/version/file.

Integrity

Expected and verified checksum information.

Local acquisition

Portable description of where the file is stored.

Raw schema

Actual HDF5 layout, shapes and dtypes.

Feature interpretation

Verified feature/label meanings.

Data-quality observations

Only bounded observations made in this task.

Test embargo

Rules governing future EDA.

Open questions for EDA

Explicit list of decisions Task 0004 must resolve.

Do not fill it with generic HEP background.

Make it an engineering/scientific record.

⸻

20. Update data documentation

Update:

data/README.md

with the actual implemented acquisition command.

It should now be possible for another developer to understand:

1. what dataset is required;
2. how to download it;
3. how integrity is checked;
4. where it will be stored;
5. why it is not committed.

Clearly distinguish implemented commands from future preprocessing commands.

⸻

21. Update main README minimally

Update the main README only where necessary to indicate:

* acquisition support is implemented;
* whether the R&D dataset has been locally verified;
* raw schema audit status;
* next project stage.

Do not turn the main README into a development log.

Link to the relevant detailed docs.

⸻

22. Do not implement preprocessing yet

This task must NOT:

* normalize features;
* transform phi;
* compute final event aggregates;
* create model tensors;
* pad/truncate final sequences;
* choose final sequence length;
* materialize train/validation/test splits;
* train any model;
* perform full EDA;
* generate final physics plots;
* implement PCA;
* implement an autoencoder;
* implement a Transformer;
* implement benchmarking;
* implement ONNX/CoreML;
* implement the trigger simulator.

Those decisions depend on Task 0004.

⸻

23. Validation

Before completion, run all appropriate validation.

At minimum:

package installation / dependency consistency
package import
Ruff lint
Ruff formatting check
pytest
existing smoke test
new acquisition unit tests

If the actual dataset was downloaded:

* verify checksum;
* verify file size;
* verify HDF5 readability;
* run bounded schema audit;
* verify raw data does not appear in Git status.

Also:

* inspect Git diff;
* run a whitespace/error check on the diff;
* verify documentation links;
* ensure no large dataset or generated binary is staged;
* ensure no credentials/tokens were written anywhere.

Record actual results.

⸻

24. Definition of done

Task 0003 is complete when:

* Task 0003 prompt exists;
* Task 0003 handoff exists;
* handoff index is updated;
* acquisition code exists;
* pinned source metadata is encoded reproducibly;
* checksum verification exists;
* safe existing/corrupted/partial-file behavior exists;
* acquisition unit tests pass;
* data/README.md documents the real workflow;
* docs/raw-data-audit.md exists;
* real dataset integrity/schema has been verified if environment permits;
* otherwise real acquisition is explicitly marked pending;
* test-embargo rules are documented;
* Task 0004 open questions are clearly identified;
* all existing tests remain passing;
* no dataset has entered Git.

⸻

25. Mandatory Task 0003 handoff

Before finishing, update:

docs/handoffs/0003-dataset-acquisition.md

with the actual state.

It must include:

* base commit;
* environment;
* authoritative source used;
* exact dataset metadata;
* implementation summary;
* dependency changes;
* whether the real dataset was downloaded;
* expected and actual size/checksum where verified;
* actual raw schema findings;
* test results;
* issues encountered;
* rejected implementation alternatives;
* unresolved questions;
* next recommended task.

Do not claim the real dataset was verified unless checksum verification actually completed.

Update:

docs/handoffs/README.md

without modifying historical Task 0001/0002 records except for objective factual corrections if absolutely necessary.

⸻

26. Final response format

Return:

1. What was implemented

2. Acquisition result

State clearly whether the real R&D dataset was actually downloaded and checksum-verified.

3. Raw schema findings

Summarize only actual verified findings.

4. Integrity and provenance

5. Test embargo / leakage safeguards

6. Validation results

Include actual pytest count and other checks.

7. Files changed

8. Issues / deferred decisions

9. Recommended next task

The expected next task is:

Task 0004 — Training-Background EDA and Schema Validation

but adjust only if Task 0003 uncovers a blocker.

10. Git commit and push commands

This section is mandatory and MUST be last.

Do NOT commit or push automatically.

Provide exact commands to:

git status
git diff
git add <only Task 0003 files>
git status
git diff --cached
git diff --cached --check
git commit -m "<specific conventional commit>"
git push

Selectively stage only intended Task 0003 source, tests and documentation.

Never stage the downloaded dataset, partial downloads, local manifests that should remain local, credentials, caches, or unrelated files.

Use a commit message appropriate to the actual implementation. If acquisition and audit are successfully implemented, a likely message is:

feat: add verified LHCO dataset acquisition

Determine the current branch/upstream rather than assuming where practical.

⸻

Proceed with Task 0003 only.

<!-- END ORIGINAL USER SPECIFICATION -->
