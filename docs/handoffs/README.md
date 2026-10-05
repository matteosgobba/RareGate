# Development handoff index

Maintain this chronological index in every operational task. A completed task
may still await the user's commit/push; this distinction belongs in its status.
See the [development protocol](../development.md).

| Task | Title | Phase | Status | Description | Handoff |
| --- | --- | --- | --- | --- | --- |
| 0001 | Project Initialization | 0.1 | Completed; committed; local `origin/main` matches | Python package, CPU/MPS diagnostic, tests, tooling, CI, and policies; historical record recovered in Task 0002. | [0001](0001-project-initialization.md) |
| 0002 | Data Foundation and Dataset Design | Data design | Completed; commit `182ff31` verified in Task 0003 | Prompt/handoff protocol, pinned LHCO R&D selection, split/leakage and representation/provenance design. | [0002](0002-data-foundation.md) |
| 0003 | Verified Dataset Acquisition and Raw Schema Audit | Data implementation | Completed; commit `bdc8da0` verified in Task 0004 | Implemented acquisition; real R&D file size/MD5 verified; Blosc-aware bounded raw audit and operational test embargo. | [0003](0003-dataset-acquisition.md) |
| 0004 | Training-Background EDA and Schema Validation | Data analysis/design | Completed and validated; awaiting user commit/push | Full integrity/duplicate scan, reproducible group-safe splits, training-only EDA, curated figures and frozen preprocessing contract. | [0004](0004-training-background-eda.md) |
