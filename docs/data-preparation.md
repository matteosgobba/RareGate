# Data and preparation

The main study uses public ADC2021 simulated collision events: Standard Model
background and the benchmark signals A → 4ℓ and LQ → bτ. The
[challenge](https://mpp-hep.github.io/ADC2021/) and
[data descriptor](https://doi.org/10.1038/s41597-022-01187-8) describe the
PYTHIA/DELPHES simulation and lepton prefilter. The selected publisher records are
[background](https://zenodo.org/records/5046428),
[A → 4ℓ](https://zenodo.org/records/7152590) and
[LQ → bτ](https://zenodo.org/records/7152599). Their CC BY 4.0 attribution terms
are separate from the software license.

## Validation and partitioning

HDF5 inputs contain `Particles` arrays shaped `[N, 19, 4]`, with transverse
momentum, pseudorapidity, azimuth and object class. Slots provide MET, up to four
electrons, four muons and ten jets. Validation checks schema and class metadata,
finite coordinates, padding, object cuts and preselection consistency before
forming canonical-content groups.

The accepted background contains 13,451,915 rows and 13,449,154 exact groups:
2,761 exact duplicates are removed before partitioning. The signal files contain
55,969 A groups and 340,544 LQ groups. These measured counts, particularly the
background count, differ from nominal counts in the source description.

| Role | Background groups | Purpose |
|:--|--:|:--|
| Training | 200,000 | Fit preprocessing and models |
| Selection | 50,000 | Select each neural checkpoint |
| Calibration | 1,000,000 | Fix score cuts and quantile brackets |
| Final evaluation | 1,000,000 | Measure achieved background acceptance |

Each signal contributes 40,000 groups to final evaluation. CPU and parity work
uses 4,096 development groups drawn from training; these are not an additional
independent sample. Exact grouping prevents identical provided objects from
crossing roles, but cannot rule out near duplicates, shared generator ancestry
or other event correlations.

## Event representation

The twelve channels are log MET; electron, muon and jet counts; each class's log
scalar transverse-momentum sum and log maximum transverse momentum; visible
transverse-vector balance; and log massless invariant mass of all provided
leptons. Sums and feature accumulation use FP64. Training-only population means
and standard deviations standardize the features before one FP32 cast.

The aggregates discard absolute azimuth and signed pseudorapidity. Rotation and
reflection checks verify the intended numerical identities; they do not establish
symmetries of detector acceptance or remove selection sculpting. Object caps and
the lepton prefilter restrict transfer to full events or unfiltered collisions.

## Working with the data

Keep original files, processed arrays and fitted model weights outside Git.
Preserve source record/version, checksums, grouping and split definitions with
any derived analysis. Fit transformations only on training background, use
selection data for model choices, and calibrate cuts after models are fixed.
Do not use signal outcomes to revise preprocessing or thresholds.

The separate LHCO representation and verified download interface are described
in the [usage guide](usage-guide.md). Results from the two datasets should not be
treated as independent confirmation of the same fitted model.
