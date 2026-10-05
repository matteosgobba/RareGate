# Development handoff index

Maintain this chronological index in every operational task. A completed task
may still await the user's commit/push; this distinction belongs in its status.
See the [development protocol](../development.md).

| Task | Title | Phase | Status | Description | Handoff |
| --- | --- | --- | --- | --- | --- |
| 0001 | Project Initialization | 0.1 | Completed; committed; local `origin/main` matches | Python package, CPU/MPS diagnostic, tests, tooling, CI, and policies; historical record recovered in Task 0002. | [0001](0001-project-initialization.md) |
| 0002 | Data Foundation and Dataset Design | Data design | Completed; commit `182ff31` verified in Task 0003 | Prompt/handoff protocol, pinned LHCO R&D selection, split/leakage and representation/provenance design. | [0002](0002-data-foundation.md) |
| 0003 | Verified Dataset Acquisition and Raw Schema Audit | Data implementation | Completed; commit `bdc8da0` verified in Task 0004 | Implemented acquisition; real R&D file size/MD5 verified; Blosc-aware bounded raw audit and operational test embargo. | [0003](0003-dataset-acquisition.md) |
| 0004 | Training-Background EDA and Schema Validation | Data analysis/design | Completed; commit `cd3d24a` verified in Task 0005 | Full integrity/duplicate scan, reproducible group-safe splits, training-only EDA, curated figures and frozen preprocessing contract. | [0004](0004-training-background-eda.md) |
| 0005 | Deterministic Preprocessing Pipeline | Data engineering | Completed; commit `cb079ec` verified in Task 0006 | Frozen transformations, verified dev/full ragged stores, reproducibility checks, guarded reading and model views; 84 tests pass. | [0005](0005-preprocessing-pipeline.md) |
| 0006 | PCA Baseline and Evaluation Framework | Baseline modeling | Completed; commit `56a7409` verified in Task 0007 | Six-component train-only PCA, reproducible background calibration/validation, audited future metrics; real tests remain embargoed; 120 tests pass. | [0006](0006-pca-baseline.md) |
| 0007 | Compact Autoencoder Baseline | Neural baseline | Completed locally; awaiting user commit/push | Frozen 155-parameter CPU AE, identical independent rerun, background calibration, MPS compatibility; 148 tests pass; real tests embargoed. | [0007](0007-compact-autoencoder.md) |
