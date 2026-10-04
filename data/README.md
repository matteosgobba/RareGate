# Data policy

Datasets are not committed to Git. All data files and subdirectories here are
ignored; this README is the only version-controlled file in `data/`.

- `data/raw/` will contain downloaded source data.
- `data/processed/` will contain derived or preprocessed data.
- Future scripts will provide reproducible download and preparation procedures,
  including the source and any applicable access or licensing requirements.

Dataset selection belongs to the next data-design phase. Phase 0.1 does not
select or download an LHC dataset. Create the local data directories when needed.
Never force-add datasets to Git.
