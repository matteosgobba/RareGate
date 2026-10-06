# LatentTrigger - Living Project Memory

> **Purpose:** This is the maintained, project-wide memory of LatentTrigger. It preserves the project's intent, scientific contracts, architectural decisions, rationale, current canonical state, and future direction. Read it at the start of a new implementation or planning session, and update it as part of every task that changes project state or understanding.
>
> **This is not a task handoff.** Handoffs record what happened during individual tasks. This file explains what the project is, why it is being built this way, what remains to be established, and how the accumulated evidence should guide the next task. It complements the existing handoff system without replacing or duplicating it.

## Document control

| Field | Current value |
| --- | --- |
| Intended repository path | `docs/project-memory.md` |
| Memory revision | 1.3 |
| Last factual verification | 2026-10-06, Europe/Rome |
| Last completed implementation task | 0010 - Particle/Set implementation and synthetic validation; canonical baseline pending |
| Latest completed task | 0011 - Bounded recovery routing/readiness completed; readiness still blocked; canonical particle baseline pending |
| Verified repository branch | `main` |
| Verified HEAD / Task 0010–0011 base (both tasks uncommitted) | `96ef5aa86dea798966fa8d0e5cb38582ea84d70c` |
| Current compact neural baseline | `compact-autoencoder-v2` |
| Particle model state | Implemented and synthetically tested; real dev/training/restoration/reproduction/freeze/calibration pending |
| Next dependency | User-controlled host preparation, then bounded preflight/conditional Task 0011 recovery; separate versioned engineering-policy review if original readiness cannot be met |
| Real test evaluation exposure | None recorded through Task 0011; both test populations remain embargoed |

The HEAD above identifies the implementation snapshot used to establish this memory. It is not a claimed commit for this document. Recheck Git and the latest project files before starting new work. Do not infer a push or hosted CI result from a local commit or a configured workflow.

The earlier planning conversation stopped at Task 0007 and described Task 0008 as pending. Local repository inspection established that Task 0008 had subsequently been completed and committed. This memory therefore incorporates that result while preserving the historical v1 baseline.

## Contents

1. [Start here: current project state](#1-start-here-current-project-state)
2. [Vision, motivation, and research question](#2-vision-motivation-and-research-question)
3. [Objectives and definition of success](#3-objectives-and-definition-of-success)
4. [Scope and non-scope](#4-scope-and-non-scope)
5. [Overall architecture and repository structure](#5-overall-architecture-and-repository-structure)
6. [Development platform, stack, and resource constraints](#6-development-platform-stack-and-resource-constraints)
7. [Dataset identity, schema, and acquisition decisions](#7-dataset-identity-schema-and-acquisition-decisions)
8. [Frozen population protocol and test embargo](#8-frozen-population-protocol-and-test-embargo)
9. [Frozen preprocessing and feature contracts](#9-frozen-preprocessing-and-feature-contracts)
10. [Implemented foundation and evidence](#10-implemented-foundation-and-evidence)
11. [Canonical model registry and measured results](#11-canonical-model-registry-and-measured-results)
12. [Evaluation, calibration, and uncertainty](#12-evaluation-calibration-and-uncertainty)
13. [Hardware inference and deployment methodology](#13-hardware-inference-and-deployment-methodology)
14. [Reproducibility and artifact governance](#14-reproducibility-and-artifact-governance)
15. [Decision register: choices and rationale](#15-decision-register-choices-and-rationale)
16. [Roadmap, milestones, and next-task definitions](#16-roadmap-milestones-and-next-task-definitions)
17. [Observations, risks, and open questions](#17-observations-risks-and-open-questions)
18. [Development workflow and mandatory Git delivery](#18-development-workflow-and-mandatory-git-delivery)
19. [How to maintain this living memory](#19-how-to-maintain-this-living-memory)
20. [Instructions to future ChatGPT/Codex sessions](#20-instructions-to-future-chatgptcodex-sessions)
21. [References and memory revision history](#21-references-and-memory-revision-history)

## 1. Start here: current project state

**Project:** LatentTrigger - *Hardware-Aware Machine Learning for Real-Time LHC Event Selection*.

**Core objective:** Investigate how much anomaly-detection performance can be retained when models are constrained by inference latency, throughput, memory, and deployment practicality.

**What exists:** A verified LHCO source, deterministic duplicate-safe population assignment, frozen preprocessing, verified ragged processed stores, a PCA reconstruction baseline, a compact autoencoder, background-only evaluation and calibration, reproducible CPU training, MPS compatibility checks, and an audited gate for a future final test evaluation.

**Canonical models:** PCA with six retained components; compact AE v2 with architecture `8 -> 6 -> 3 -> 6 -> 8`, 155 parameters, best epoch 381, stopped at epoch 396 under the unchanged patience rule. AE v1 is retained as historical evidence, not the current compact AE.

**Particle/set design:** Task 0009 selects a 478-parameter equivariant particle autoencoder with local dimension 2 per retained particle and eight masked-mean context values. Corresponding-particle reconstruction avoids set matching; its total code is 2n+8, not an event-only eight-value compression. Task 0010 implements and synthetically validates this unchanged design. Its launch failed at 3.694794 GiB versus the frozen 8 GiB minimum before any real read/update. Task 0011 adds source-bound preflight and one fixed lineage-bound recovery route, with 296 synthetic tests. All three readiness samples failed at 2.9495–3.0176 GiB; no new attempt was reserved. Dev feasibility, canonical convergence, reproduction, freeze and calibration remain pending. See [the design](particle-set-baseline-design.md), [implementation/gated outcome](particle-set-baseline.md) and [recovery readiness](particle-set-resource-recovery.md).

**What does not yet exist:** Real signal-discrimination results; a trained/frozen particle/set-aware baseline; controlled inference benchmarks; ONNX/CoreML exports; a quantization study; a trigger simulator; NVIDIA/TensorRT or FPGA measurements.

**Scientific boundary:** All real model development has used background only. No real `test_background` or `test_signal` model/evaluation population request is recorded through Task 0011. Whole-file integrity checks and frozen preprocessing are separate permitted custody operations.

**Next:** User-controlled host preparation followed by the prepared three-sample preflight/conditional recovery commands. Task 0011 authorizes one recovery attempt, still unused; every original limit remains. Do not fish for passing samples, reset ledgers or relax the free+inactive ≥8 GiB launch metric. If ordinary preparation cannot meet it, a separate versioned engineering-policy review is needed. The 96-step dev allowance is unused. CPU throughput/convergence remain unmeasured; benchmark work waits for the baseline gates. Do not repeat AE convergence without new integrity evidence.

### How to interpret the statements in this file

- **Frozen:** An established contract to reuse. Changes require an explicit, versioned methodological decision.
- **Implemented / measured:** Supported by source, artifacts, task reports, or actual execution evidence.
- **Planned / proposed:** Future work, not an implemented feature or an achieved result.
- **Open:** A question that the existing evidence does not answer.

Current user instructions and applicable repository instructions govern execution. This memory provides continuity; it is not blanket authorization to unblind tests, change frozen protocols, commit, push, or perform unrelated work.

## 2. Vision, motivation, and research question

### 2.1 The project idea

Event selection is a setting where scientific usefulness and computational practicality must be considered together. A model that is accurate but cannot meet the intended processing budget is not sufficient. A model that is fast but discards useful anomaly information is also insufficient.

LatentTrigger studies this tradeoff using a controlled progression:

1. Build trustworthy scientific data and evaluation foundations.
2. Establish transparent aggregate-level baselines.
3. Investigate whether particle-level structure justifies additional complexity.
4. Measure inference cost under explicit hardware and runtime conditions.
5. Explore export, reduced precision, and streaming behavior.
6. Evaluate frozen candidates on the held-out test and report both scientific and systems outcomes.

The intended contribution is a defensible experimental study and a maintainable research implementation. The project does not depend on obtaining a positive result for every model or optimization. A carefully controlled finding that a simpler model is preferable, or that an optimization provides no useful gain, is a valid outcome.

### 2.2 CERN / openlab motivation

The project connects high-energy-physics data, machine learning, software engineering, and heterogeneous computing. This direction is relevant to the computing themes described by [CERN openlab](https://openlab.web.cern.ch/our-rd-directions/): AI, emerging technologies, efficient computing infrastructure, and collaboration between scientific computing and industry.

The personal motivation includes building a credible research and engineering portfolio relevant to CERN/openlab opportunities. The portfolio should demonstrate methodological discipline, readable software, reproducible experiments, measured tradeoffs, and the ability to explain limitations. This is a project judgment about relevance, not an official assessment of competitiveness or admission prospects.

**LatentTrigger is an independent project. It is not an official CERN, ATLAS, CMS, or CERN openlab project, and does not imply affiliation or endorsement.**

### 2.3 Main research question

> How much anomaly-detection performance can be retained when machine-learning models are optimized for real-time LHC event selection under strict computational constraints?

Supporting questions include:

- What information is lost when an event is reduced to eight aggregates?
- Does a compact nonlinear model offer a useful tradeoff relative to PCA?
- Does particle/set structure justify its additional compute and memory cost?
- How do runtime, batch size, precision, export constraints, and hardware change that tradeoff?
- How stable are background-calibrated decisions across populations and numerical implementations?
- What biases do scores introduce with respect to event scale, mass proxies, multiplicity, and truncation?
- What happens to queueing, latency, and acceptance when a model is placed in a synthetic event stream?

These questions are not all currently answered. In particular, lower background reconstruction loss is not evidence of better signal discrimination.

## 3. Objectives and definition of success

| Objective | Required outcome | Current state |
| --- | --- | --- |
| Reliable data foundation | Pinned source, verified integrity, reproducible population membership, frozen transformations | Achieved for the primary LHCO dataset |
| Transparent baselines | Linear and compact nonlinear models using a shared input/evaluation contract | PCA and compact AE implemented; AE convergence closure completed |
| Richer event representation | A justified, compact, mask-aware particle/set baseline | Design/implementation complete; Task 0011 readiness still blocked; no recovery attempt or real particle training |
| Scientific evaluation | Frozen-candidate discrimination metrics, calibrated operating points, uncertainties, and bias analysis | Framework exists; real final test evaluation is pending |
| Hardware study | Repeatable latency, throughput, and memory measurements with clear timing boundaries | Pending |
| Deployment study | Verified exports and reduced-precision variants where useful | Pending |
| Trigger-like systems study | Reproducible synthetic arrival/queue/acceptance scenarios | Pending |
| Final research deliverable | Quality-versus-cost comparison, clear claims, reproducibility package, limitations, and conclusions | Pending |

The final result should describe a quality/cost frontier rather than declare one model universally best. Any latency budget, throughput target, acceptable numerical deviation, or quality-retention requirement must be established in the relevant task before observing results. No numerical deployment target has yet been validated.

The project is successful when its conclusions are supported by evidence and another session or researcher can understand and reproduce the decisions. It does not require proving detector readiness, discovering new physics, or making the AE outperform PCA.

## 4. Scope and non-scope

### 4.1 Primary scope

- Corrected LHCO R&D particle data as the initial shared scientific source.
- Pure-background unsupervised fitting and background-only development.
- Aggregate reconstruction baselines, followed by compact particle/set-aware models.
- Common score orientation, population roles, calibration, metrics, and uncertainty conventions.
- Scientific bias and representation-loss analysis.
- Apple Silicon CPU/MPS inference as the initial hardware study.
- Controlled ONNX/ONNX Runtime and CoreML export/inference experiments.
- Precision reduction and quantization, where supported and justified.
- A synthetic trigger-like event-stream simulator.
- Conditional NVIDIA/TensorRT work and optional FPGA/hls4ml exploration.
- An explicitly authorized, frozen-candidate final test evaluation.

### 4.2 Non-scope and prohibited shortcuts

- No official experiment trigger implementation, DAQ integration, detector commissioning, or claim of operational readiness.
- No physical LHC arrival-rate inference from the released dataset's row count or class mixture.
- No discovery claim or discovery significance derived from event-score classification alone.
- No signal-driven model, preprocessing, sequence-length, epoch, or threshold selection under the current protocol.
- No test-guided iteration followed by describing the same population as untouched.
- No validation anomalies without a separate explicit protocol change and suitable reserved evaluation.
- No automatic choice of a Transformer merely because the input is a set.
- No CUDA/TensorRT assumption on the local Mac; NVIDIA work requires a separate supported environment.
- No full raw DataFrame loading on the 16 GiB development machine.
- No large data/checkpoint/export files added to Git by default.
- No expansion into unrelated applications, dashboards, tracking frameworks, or infrastructure without a concrete need.

Additional datasets, signal contamination studies, black-box studies, and real detector data are later extensions, not implicit changes to the initial benchmark.

## 5. Overall architecture and repository structure

### 5.1 Scientific and deployment pipeline

```text
Pinned and verified raw HDF5
    -> structural integrity and exact-content grouping
    -> deterministic frozen population membership
    -> canonical physical ragged event store
        -> standardized eight-aggregate view
            -> PCA / compact AE
        -> particle/set view [384, 4] + mask
            -> implemented compact particle/set AE (canonical baseline pending)
    -> finite anomaly score, larger = more anomalous
    -> frozen background-calibrated thresholds
    -> inference runtime / precision variant
    -> future synthetic streaming selection
    -> separately authorized final test evaluation
```

The canonical physical store preserves all valid source particles. Model views are derived from it; the padded representation is not the persistent source of truth. Labels and provenance remain outside model features.

Keep the following boundaries visible:

- Data custody and integrity versus model/evaluation population access.
- Frozen physical/preprocessing semantics versus model-specific representation choices.
- Model fitting/selection versus threshold calibration.
- Training resource observations versus controlled inference benchmarks.
- Model-only inference versus transfers, preprocessing, scoring, decision, and end-to-end latency.
- Scientific identities versus local build/run metadata.

### 5.2 Repository organization

```text
latent-trigger/
  .github/workflows/ci.yml
  configs/
    data/lhco_rnd_v5.json
    models/pca_baseline.json
    models/compact_autoencoder.json
    models/compact_autoencoder_v2.json
    models/particle_set_baseline_design_v1.json  # historical design-only specification
    models/compact_particle_set_autoencoder_v1.json  # exact executable mapping
  src/latenttrigger/
    data/          acquisition, inspection, splitting, features,
                   preprocessing, processed-store reading, analysis
    models/        PCA, compact AE, background loading, reporting
    training/      AE training and convergence closure
    evaluation/    metrics, thresholds, final evaluation gate
    utils/         device selection
  scripts/         acquisition audit, EDA, preprocessing checks, smoke tests
  tests/
  docs/
    project-memory.md       maintained project-wide state and direction
    development.md          task workflow
    *-contract.md           frozen scientific semantics
    *-protocol.md           evaluation and access rules
    model/data reports     detailed evidence and reproduction
    prompts/                task specifications
    handoffs/               historical task records and index
  artifacts/models/
    compact-autoencoder-v1/model.json
    compact-autoencoder-v2/model.json
  results/
    tables/final/           intentionally curated small results
    figures/final/          intentionally curated figures
    benchmarks/            future benchmark outputs/policy
  notebooks/exploration/
  data/                     local raw/analysis/processed/baseline outputs
  README.md
  pyproject.toml
  LICENSE
  .gitignore
```

Relative links in this memory are intended to resolve from `docs/` in the operational repository. The local repository used for verification was `/Users/matteosgobba/Documents/GitHub/latent-trigger`; that path is a local locator, not part of portable scientific provenance.

## 6. Development platform, stack, and resource constraints

### 6.1 Platform

- User-specified MacBook Pro M5.
- Recorded/verified task environment: macOS 26.6.2, ARM64, 16 GiB RAM.
- CPU is the canonical compact AE training device.
- MPS availability is queried, not assumed. The generic device helper prefers MPS when available and otherwise CPU; model configuration explicitly fixes canonical training to CPU.
- A sandbox may expose CPU fallback even when native MPS works. Distinguish those execution contexts.

CPU/GPU core counts, power mode, thermal behavior, and detailed hardware configuration must be captured for future benchmarks. They are not established by the current memory.

### 6.2 Stack

| Layer | Established choice |
| --- | --- |
| Python | Primary 3.12; supported range `>=3.11,<3.13` |
| Environment/build | `venv`, `pip`, editable installation, Hatchling, `src` package layout |
| Package | `latenttrigger`, version 0.1.0 at this snapshot |
| Numeric/data | NumPy; h5py and hdf5plugin in the optional data extra |
| Modeling | scikit-learn PCA/metrics; PyTorch aggregate AE and implemented particle/set AE |
| Analysis | Matplotlib in the optional analysis extra |
| Quality | pytest, Ruff lint/format |
| CI | CPU checks configured for Python 3.11 and 3.12 |
| Future runtime work | ONNX Runtime, CoreML/coremltools, NVIDIA/TensorRT, optional hls4ml |

Historical experiment versions: Python 3.12.12; PyTorch 2.14.1; NumPy 2.5.3; scikit-learn 1.9.1; SciPy 1.18.1; h5py 3.16.0/HDF5 2.0.0; hdf5plugin 7.1.0; Matplotlib 3.11.2; pytest 9.1.1; Ruff 0.16.10.

Dependency ranges are not an experiment lockfile. Record exact versions in each run. Cross-version/device bitwise identity is not guaranteed.

### 6.3 Resource implications

The raw numeric payload is 18,488,800,000 uncompressed bytes, exceeding installed RAM before overhead. Use bounded contiguous HDF slices, memory mapping, and batch processing. The established default processing chunk is 992 events, equal to 16 HDF chunks.

Do not persist a full `[1,100,000,384,4]` tensor by default: the FP32 features alone would require 6,758,400,000 bytes. A single event's four-channel particle input uses 6,144 bytes, excluding mask, activations, and runtime overhead. Unified memory does not remove copies, synchronization costs, or capacity limits.

Task 0009 selected design has 1,912 FP32 parameter bytes, 165,888 dense forward MAC/event at 384 particles and no quadratic score. Batch32 has a 0.75 MiB largest network tensor; an allocation inventory is about 3.68 MiB and a 4× working-tensor planning envelope about 14.71 MiB, excluding runtime/store overhead. These are analytic estimates, not measured RSS or latency. Preregistered ceilings, enforced by Task 0010, are 512 MiB working tensors/workspace, 6 GiB process RSS (including verification/mmap), at least 8 GiB available at launch and stop below 4 GiB available. Stream at most 32 padded events; never cache the padded population. CPU feasibility must pass the dev gate before full training. Task 0010 measured synthetic batch32/full384 temporary tensor allocation at 5,228,448 bytes (4.986 MiB) with two Adam steps; this is not real-run peak memory or latency. The real launch attempt stopped at 3,967,254,528 available bytes (3.694794 GiB), before any store/view read. Launch RSS 356,663,296 bytes and native heap reservation 184,205,312 bytes are startup observations only. Available memory uses Darwin free+inactive pages; real stages also monitor native malloc arena reservation, RSS, memory floor and deadlines. No resource limit was relaxed. Task 0011 rechecked in a fresh CPU worker: page size16,384 bytes, available2.9495/2.9671/3.0176 GiB, all below launch and continuing floors; peak RSS≤357,498,880 bytes and native reserved≤184,205,312 bytes passed their ceilings. Readiness is not a real attempt. Installed RAM16 GiB and memory-pressure free39% are distinct contextual measurements; compressed pages/cumulative swap counters are not added to availability. Current swap/current RSS queries were permission-restricted. New recovery plan/ledger/output remain absent; all real-stage evidence is still pending.

Check actual disk availability before expensive work; account for raw data, processed stores, temporary streams, repeated runs, caches, and a safety margin. Never delete verified raw data automatically to free space.

## 7. Dataset identity, schema, and acquisition decisions

### 7.1 Exact primary source

| Field | Frozen value |
| --- | --- |
| Dataset | LHC Olympics 2020 R&D |
| Version | Zenodo v5 |
| Record | 6466204 |
| Version DOI | [10.5281/zenodo.6466204](https://doi.org/10.5281/zenodo.6466204) |
| Primary filename | `events_anomalydetection_v2.h5` |
| Exact size | 2,908,260,409 bytes |
| Published and verified MD5 | `629789d55813be3860781b084ae7f1de` |
| Locally computed SHA-256 | `5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6` |
| Historical acquisition/first verification UTC | `2026-10-04T11:05:47.545875+00:00` |
| License | CC BY 4.0; retain dataset attribution |
| Default local raw directory | `data/raw/lhco/6466204/` |

Size, MD5, and SHA-256 were rechecked against local file bytes on 2026-10-06 when establishing the project memory. This was an integrity-only read, not test scoring. The software's MIT license does not relicense the dataset.

**Why the corrected v5 source matters:** The April 2022 correction aligned raw events with the v2 QCD generator threshold, `PhaseSpace:pTHatMin = 500`, and the published v2 feature file. Do not substitute the older `events_anomalydetection.h5`, use a floating latest URL, or mix older particles with corrected feature rows. See the [official correction notice](https://zenodo.org/records/6466204).

### 7.2 Physics context and interpretation

The primary file contains 1,000,000 QCD events and 100,000 two-prong signal events, shuffled together. The signal is `W' -> XY`, with `X -> qq` and `Y -> qq`; masses are 3.5 TeV, 500 GeV, and 100 GeV. Generation uses Pythia8 and Delphes 3.4.1 without pileup or multiple parton interactions.

The benchmark is already selected using a fat-jet trigger. The official challenge documents an anti-kT `R=1` jet with `pT > 1.2 TeV` and `|eta| < 2.5`. This is a jet requirement, not a per-particle cut.

These are simulated, preselected events. Rows are not timestamps; the class ratio is not a collision-rate model; reconstructed massless constituents do not represent detector readout or every stage of the real LHC trigger chain.

### 7.3 Actual HDF schema

| Object | Shape/dtype | Meaning |
| --- | --- | --- |
| `/df/block0_values` | `[1,100,000,2101]`, float64 | Numeric event rows |
| `/df/axis0` and `/df/block0_items` | `[2101]`, int64 | Column labels 0 through 2100 |
| `/df/axis1` | `[1,100,000]`, int64 | Stored row index, verified against ordinals |
| Particle slot `j`, `0 <= j < 700` | Columns `3j`, `3j+1`, `3j+2` | `pT [GeV]`, `eta`, `phi [rad]` |
| Column 2100 | float64 truth bit | 0 background, 1 signal; separate metadata |

The root contains a pandas fixed-format frame under `/df`, not an assumed dense `/table` dataset. Numeric HDF chunks are `[62,2101]`; one uncompressed numeric chunk is 1,042,096 bytes. All four datasets use Blosc filter 32001. Importing hdf5plugin registers the required decoder; plain h5py initially could inspect metadata but could not decode event content.

Real particles have `pT > 0`. Padding is an exact `(0,0,0)` trailing suffix. There are no particle type, charge, mass, or jet-assignment channels. Unit interpretation is source-supported, not supplied by a self-describing unit header.

### 7.4 Integrity evidence

Task 0003's bounded audit inspected 32 evenly spaced, class-agnostic rows. It found 16,890 padded slots, multiplicities 74-301 with mean 172.1875, and no sampled structural violations. This was a bounded finding, not a full-file quality guarantee.

Task 0004 then scanned the complete source before model-oriented EDA:

- 1,100,000 eligible events: 1,000,000 background and 100,000 signal.
- Zero unexpected truth values, NaNs, infinities, negative-pT events, malformed padding, non-trailing padding, empty events, or row-axis mismatches.
- Full structural multiplicity range: 22-560; zero events filled all 700 source slots.
- 1,100,000 unique exact-content groups; zero duplicated groups, participating duplicate rows, or conflicting-label groups; largest group size 1.

Do not generalize exact duplicate findings to approximate duplicates or other datasets.

### 7.5 Reserved sources

The v2 high-level jet-feature file is an optional later cross-check, not the primary input. The supplemental three-prong signal and LHCO black boxes are reserved for separate frozen-model evaluation/domain-shift protocols. Public black-box answer keys prevent claiming original challenge blindness.

Dark Machines was considered as a later cross-benchmark; CMS JetHT NanoAOD as a possible later realism study. Neither is part of the current implemented pipeline. Adding them requires new schema, selection, label, and evaluation decisions.

## 8. Frozen population protocol and test embargo

### 8.1 Exact populations

Protocol identifier: `lhco-rd-v1`. Seed: **1729**.

| Population | Exact count | Permitted role |
| --- | ---: | --- |
| `train_background` | 699,957 | EDA, fitted preprocessing, model fitting, future quantization calibration |
| `validation_selection_background` | 74,749 | Preregistered background model selection/early stopping and diagnostics |
| `validation_calibration_background` | 74,823 | Threshold calibration after selected model restoration and freeze |
| `test_background` | 150,471 | Future explicitly authorized frozen-candidate final evaluation |
| `test_signal` | 100,000 | Same final evaluation; never development |
| Total validation background | 149,572 | Two disjoint roles; do not merge them for convenience |
| Development subset | 8,494 | Pipeline/model implementation diagnostics, not final reported ML results |

Development subset composition: 6,999 training background, 747 selection background, 748 calibration background. No test events and no signal.

### 8.2 How membership is established

Exact-content grouping precedes split/subset selection and fitted statistics. Remove verified padding, normalize signed zero, wrap only out-of-interval phi, lexicographically sort physical triplets, and hash:

```text
uint64 little-endian particle count
    || contiguous little-endian float64 triplets
```

Labels, source ordinals, split names, and learned statistics are excluded. Do not round values to deduplicate. Future aliases share group membership; conflicting labels quarantine the group and block statistical analysis.

For each eligible background fingerprint, hash the exact UTF-8 prefix:

```text
lhco-rd-v1|1729|bg-split|<lowercase fingerprint hex>
```

Interpret the first eight digest bytes as a big-endian unsigned integer and derive `u = k / 2^64`: train below 0.70, validation from 0.70 to below 0.85, test otherwise. The independent `val-role` hash domain divides validation at 0.5. Use the implementation's exact integer cutoffs.

The fractions are hash probabilities, not exact quotas. Reuse saved membership and verified split provenance for every model. Do not resplit per experiment.

The `lhco-rd-dev-v1` subset ranks allowed groups using `dev-subset`, selecting `floor(role_count/100)` separately for each allowed background role. It is a convenience subset, not guaranteed kinematic stratification.

### 8.3 Embargo rules

**There is no anomaly validation population in the current protocol.** All primary two-prong signal is test-only.

During development, do not compute real test reconstruction loss, anomaly scores, ROC-AUC, AP, signal efficiencies, test-background FPR, signal latent distributions, or test physics distributions to guide choices. Test information must not select features, architecture, `Nmax`, scalers, training endpoint, runtime variants, or thresholds.

Allowed custody operations include raw/file hashing, structural schema/label-role consistency, duplicate/split integrity, and applying an already-frozen preprocessing function to construct the full store. Those operations must not feed test physics distributions or scores back into development.

The standard background loader permits only train, selection, and calibration backgrounds. The processed reader has explicit test and truth guards. A separate final evaluation module requires opt-in and frozen identities. Availability of an API or CLI is not authorization to run it on real test populations.

Any partial or interrupted model/evaluation test access is exposure. Repeated test-guided development cannot restore the population's untouched status. Disclose exposure and establish a new evaluation protocol/population if subsequent design is motivated by test results.

## 9. Frozen preprocessing and feature contracts

The exact numeric source of truth is [configs/data/lhco_rnd_v5.json](../configs/data/lhco_rnd_v5.json), supported by the [preprocessing contract](preprocessing-contract.md). Read the configuration; do not refit statistics or copy rounded report values.

### 9.1 Canonical physical records

- Store all valid particles as FP32 `[N,3]`, channel order `[pt_GeV, eta, phi_rad]`.
- No truncation, padding, logs, standardization, or sine/cosine replacement in the physical canonical record.
- Normalize signed zero; wrap out-of-range phi in float64 using `((phi + pi) mod (2*pi)) - pi`; preserve in-range values exactly.
- Before casting, sort original source float64 values by descending pT, ascending eta, ascending wrapped phi, then ascending original slot.
- Preserve original slots as uint16 provenance, not model channels.
- Event identity is `(source SHA-256, raw row ordinal)`; the exact-content fingerprint is separate provenance.

### 9.2 Particle/set view

Input shape: `[384,4]` FP32 and `[384]` boolean mask; batches `[B,384,4]` and `[B,384]`.

| Channel | Frozen transform |
| --- | --- |
| 0 `standardized_log1p_pt` | `(log1p(pT / 1 GeV) - 1.7563971656024226) / 1.1860427476562252` |
| 1 `standardized_eta` | `(eta - (-2.3446856614008353e-05)) / 1.4824139450954399` |
| 2 `sin_phi` | `sin(wrapped_phi)` |
| 3 `cos_phi` | `cos(wrapped_phi)` |

Object scalers were fitted in float64 on all **127,379,949 valid training-background particles**, before truncation, with equal particle weights and population standard deviation (`ddof=0`). Compute model transformations in float64 from canonical physical values, then cast once to FP32.

No clipping, winsorization, per-event rotation, event-scale removal, or learned angular standardization is part of the contract.

### 9.3 `Nmax`, ordering, padding, and mask

**Default `Nmax=384`.** Retain the leading `min(N,384)` particles in the frozen order. Preserve every particle in the canonical store.

The preregistered choice was the smallest candidate with at least 99% complete-event coverage and event-mean lost scalar-pT fraction no larger than 0.1%. Training-background evidence:

- 1,740 truncated events, or 0.248587%.
- Complete-event coverage 99.7514%.
- Mean scalar-pT loss over all training events 0.001118%; worst event loss 5.1146%.
- Truncated events lose an average 26.765 particles; worst removed count 176.
- `Nmax=320` meets momentum retention but fails complete-event coverage.

Transform real retained particles first, then pad with exactly `[0,0,0,0]`. Transforming a zero physical padding triplet would incorrectly produce `cos(phi)=1` and nonzero standardized values.

**Mask `True` means real retained particle; `False` means padding.** True entries form a prefix. Apply mask in pooling, attention, losses, and statistics. Record original/retained multiplicity and retained scalar-pT fraction separately. No original-slot channels or position embeddings in the initial permutation-symmetric set view.

Alternative `Nmax` values require controlled, versioned experiments, never test-signal tuning.

### 9.4 Eight aggregate features

Compute from **all canonical physical particles before truncation**, accumulating float64. Define:

```text
S = sum_i pT_i
Qx = sum_i pT_i * cos(phi_i)
Qy = sum_i pT_i * sin(phi_i)
mu_eta = sum_i pT_i * eta_i / S
E = sum_i pT_i * cosh(eta_i)
Pz = sum_i pT_i * sinh(eta_i)
```

| Index / channel | Physical definition | Transform before standardization |
| --- | --- | --- |
| 0 `multiplicity` | `N` | `log1p(N)` |
| 1 `scalar_pt` | `S [GeV]` | `log1p(S / 1 GeV)` |
| 2 `max_pt` | `max_i pT_i [GeV]` | `log1p(max_pt / 1 GeV)` |
| 3 `pt_balance` | `sqrt(Qx^2 + Qy^2) / S` | Identity |
| 4 `weighted_eta_mean` | `mu_eta` | Identity |
| 5 `weighted_eta_std` | `sqrt(sum_i pT_i * (eta_i-mu_eta)^2 / S)` | Identity |
| 6 `pt_concentration` | `sum_i pT_i^2 / S^2` | Identity |
| 7 `massless_event_mass` | `sqrt(E^2-Qx^2-Qy^2-Pz^2) [GeV]` | `log1p(M / 1 GeV)` |

Guard `S > 0`. Clamp a negative mass-squared only when its magnitude is within `64 * float64_eps * (E^2+Qx^2+Qy^2+Pz^2)`; materially negative values are errors. This is a visible massless event-mass proxy, not the published dijet mass. `pt_balance` is not detector-provided MET.

Every transformed aggregate is standardized using the frozen training-event mean and population std, with equal event weights. Output `[8]` FP32, in the permanent channel order above.

| Index | Exact transformed-feature mean | Exact population std |
| --- | ---: | ---: |
| 0 | 5.151002678640802 | 0.3506400659339444 |
| 1 | 7.963434750020592 | 0.13328049741910378 |
| 2 | 6.063241479784076 | 0.4747007020377456 |
| 3 | 0.02557015572051737 | 0.020723012003953097 |
| 4 | -0.0003911654144766292 | 0.42205163321441674 |
| 5 | 0.7250460126255276 | 0.24966927987490806 |
| 6 | 0.06391752754240078 | 0.03801299101213741 |
| 7 | 8.332576043011052 | 0.21947880024539493 |

Do not include truth, row ID, split, fingerprint, source identity, or original slot among features.

### 9.5 Processed storage

Local ignored root: `data/processed/lhco-rd-v1/schema-v1/{dev,dev-repeat,full}`.

| File | Dtype / shape | Role |
| --- | --- | --- |
| `particles.npy` | float32 `[P,3]` | All physical sorted particles |
| `original_slots.npy` | uint16 `[P]` | Source-slot provenance |
| `offsets.npy` | int64 `[E+1]` | Ragged event slices |
| `event_ids.npy` | int64 `[E]` | Source ordinals |
| `multiplicities.npy` | uint16 `[E]` | Full particle counts |
| `event_aggregates.npy` | float64 `[E,8]` | Physical full-event summaries |
| `event_features.npy` | float32 `[E,8]` | Standardized aggregate model input |
| `labels.npy` | uint8 `[E]` | Separate evaluation truth |
| `split_codes.npy` | uint8 `[E]` | Frozen roles |
| `development.npy` | bool `[E]` | Dev membership |
| `fingerprints.npy` | 32-byte void `[E]` | Exact-content identity |
| `configuration.json` | JSON | Exact configuration snapshot |
| `manifest.json` | JSON | Integrity/scientific identity plus separate build record |

## 10. Implemented foundation and evidence

This table preserves the project-level outcome of each task. Detailed chronology, commands, changed files, and task-time failures belong to the existing handoffs.

| Task | Verified local commit | Durable outcome | Recorded passing pytest count |
| --- | --- | --- | ---: |
| 0001 Project Initialization | `0930b03` | Package/tooling/CPU CI; CPU/MPS device diagnostic, result 16.0; repository policies | 4 |
| 0002 Data Foundation and Dataset Design | `182ff31` | Dataset selection, population/embargo and representation design; permanent prompt/handoff protocol | 4 |
| 0003 Verified Dataset Acquisition and Raw Schema Audit | `bdc8da0` | Real source acquired and hashed; streamed atomic downloader; Blosc-aware bounded schema audit | 32 |
| 0004 Training-Background EDA and Schema Validation | `cd3d24a` | Complete integrity/exact grouping, saved splits, train-only EDA; frozen scalers/order/Nmax | 54 |
| 0005 Deterministic Preprocessing Pipeline | `cb079ec` | Verified ragged dev/full stores, views, manifests, reproducibility and access safeguards | 84 |
| 0006 PCA Baseline and Evaluation Framework | `56a7409` | Frozen PCA, background diagnostics/calibration, common metrics, future audited final gate | 120 |
| 0007 Compact Autoencoder Baseline | `64bb817` | Frozen AE v1, deterministic full CPU repeat, background calibration, MPS compatibility | 148 |
| 0008 Compact Autoencoder Convergence Closure | `0645077` | Exact v1 prefix; unchanged-rule early stopping; canonical AE v2, exact independent repeat | 167 |
| 0009 Particle-Level / Set-Aware Neural Baseline Design | `96ef5aa`, verified in Task 0010 | One complete design, loss/score/budgets and future gates; zero real population requests | No suite rerun; synthetic formula/document checks |
| 0010 Compact Particle/Set Baseline Implementation and Background Validation | Uncommitted prerequisite verified in Task 0011; base `96ef5aa` | Exact implementation; original launch-memory failure and both source acceptances preserved | 247 |
| 0011 Bounded Particle/Set Resource-Gate Recovery and Background Validation | Uncommitted; base `96ef5aa`; initial Task 0010 blobs snapshotted separately | Narrow recovery routing complete; three failed read-only samples; zero new attempt/read/update | 296 |

These counts and experiment outcomes are recorded historical evidence. Creating this memory did not rerun the full training or test suite. A configured CI job is not a verified hosted CI success.

### 10.1 Training-background data observations

- 699,957 training events, 127,379,949 valid particles.
- Multiplicity min/max 22/560; mean 181.982535; population std 61.020073; median 177.
- Multiplicity p90/p95/p99/p99.5/p99.9: 263 / 291 / 344 / 365 / 408.044.
- Raw training pT min/max/median: 0.011443535 / 3138.8899 / 3.1709824 GeV; mean 15.935601 GeV, std 52.263314 GeV.
- All 699,957 training events contain at least one pT increase in raw slot order. Source order is not descending pT.
- All raw training particle values round-trip float64 -> float32 -> float64 exactly. This does not imply exactness of newly computed logs, wrapping, or aggregates.

### 10.2 Processed-store results

| Store | Events | Particles | Total bytes including metadata |
| --- | ---: | ---: | ---: |
| Dev | 8,494 | 1,549,328 | 23,055,615 |
| Independent dev repeat | 8,494 | 1,549,328 | 23,055,615 |
| Full | 1,100,000 | 195,918,046 | 2,906,852,158 |

Independent dev builds with chunks 992 and 496 reproduce all 11 arrays and configuration bytes, dtypes, shapes, scientific hashes, views, masks, and truncation metadata. Exactly 27 dev events truncate in the model view. Full/dev content matches on all 8,494 common allowed background events. Full event IDs cover ordinals 0 through 1,099,999.

Full raw cast error was zero in all three channels. Two source phi values required wrapping; the subsequent maximum FP32 angular error was `6.357301884918343e-8 rad`. Real rounded-sort diagnostics found no ordering change; source-before-cast ordering remains required and synthetic adversarial tests cover it. Six independent scalar-math spot checks showed aggregate differences no larger than `1.8189894035458565e-12`; standardized FP32 results matched exactly.

### 10.3 Engineering observations, not inference benchmarks

Task 0005 recorded:

| Build | Chunk events | Write/hash seconds | Verification seconds | Lifetime peak RSS |
| --- | ---: | ---: | ---: | --- |
| Dev | 992 | 4.754 | 0.086 | 298 MiB |
| Dev repeat | 496 | 5.277 | 0.087 | 252 MiB |
| Full | 992 | 143.771 | 6.366 | 2.44 GiB |

These exclude raw/input verification; mmap pages contribute to RSS. EDA temporary streams peaked at 3,101,916,024 bytes. Resource observations establish local feasibility, not trigger latency or controlled device performance.

## 11. Canonical model registry and measured results

### 11.1 Model roles

| Model | Role | Input / compression | Artifact |
| --- | --- | --- | --- |
| PCA reconstruction v1 | Frozen linear baseline | Eight aggregates; six retained axes | Local ignored `data/baselines/pca-v1/model.json`; curated results tracked |
| Compact AE v1 | Historical Task 0007 baseline, preserved | Eight aggregates; latent dimension three | [v1 model](../artifacts/models/compact-autoencoder-v1/model.json) |
| Compact AE v2 | Current canonical compact AE | Same architecture/input; later background-selected epoch | [v2 model](../artifacts/models/compact-autoencoder-v2/model.json) |
| Particle/set model | Implemented/tested; Task 0011 preflight still blocked; recovery allowance unused | Existing particle view plus mask; distributed local2 + mean8 code | [Executable configuration](../configs/models/compact_particle_set_autoencoder_v1.json), [report](particle-set-baseline.md); no frozen trained artifact/hash |

Implemented PCA/AE reconstruction scores remain SSE, larger means more anomalous. The implemented particle score instead uses a masked mean of weighted corresponding-particle residuals (defined below); raw scales are not directly comparable. Raw scores are not normalized for plotting; `ln(1+s)` is only a display transform where used in reports.

### 11.2 PCA baseline

Fit scikit-learn PCA using deterministic full SVD, float64 fitting, internal mean centering, no whitening, and no randomized solver on 699,957 training-background events. Select the smallest `k` reaching at least 95% cumulative **training** variance. No validation/signal-based retuning of `k`.

- Selected `k=6`.
- Retained variance 97.870086%.
- Five components retain 92.824643%.
- Variance-ratio spectrum, rounded for readability: 0.321932423 / 0.225297891 / 0.143915339 / 0.125000234 / 0.112100547 / 0.050454430 / 0.014317469 / 0.006981666.

```text
x_hat = mu + W.T @ W @ (x - mu)
score = sum_j (x_j - x_hat_j)^2
```

PCA saves 88 fitted numeric values: eight means, all eight axes, eight variances, eight variance ratios. Inference with six axes needs 56 coefficients including mean. Reported historical JSON size: 9,253 bytes. The mean residual agrees with discarded covariance eigenvalues times `(N-1)/N` to approximately `7e-16`.

Two independent real CPU runs reproduced parameters, scientific identities, score bytes, summaries, thresholds, tables, and figures exactly. This is local reproducibility, not guaranteed cross-platform BLAS identity.

**Background score summary** (numeric values copied from the curated CSV).

| Statistic | Training background | Selection background | Calibration background |
| --- | ---: | ---: | ---: |
| Events | 699957 | 74749 | 74823 |
| Mean SSE | 0.1703930829078328 | 0.17224552267031595 | 0.17282825364807736 |
| Population std | 0.3264928275983368 | 0.33077439810622167 | 0.3370284958137342 |
| Minimum | 6.229852392536156e-08 | 1.393933666930995e-06 | 2.716535882116778e-06 |
| Median | 0.09292943414097307 | 0.09344209250212934 | 0.09375141510825061 |
| p90 | 0.3466508725381213 | 0.3479482193778987 | 0.34967140578815487 |
| p95 | 0.5592304760861656 | 0.5627889007032169 | 0.5642050265377994 |
| p99 | 1.3908934004212525 | 1.4278172120604116 | 1.4231736552552572 |
| p99.9 | 4.011884664834042 | 4.005847266759414 | 4.118285218225896 |
| Maximum | 19.732761907767095 | 13.790413217924574 | 14.88682560350527 |

**Frozen calibration and independent selection check.** Calibration total 74,823; selection total 74,749. All decisions use strict `score > threshold`.

| Target FPR | SSE threshold | Calibration accepted | Calibration FPR | Selection accepted | Selection FPR |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.1 | 0.3496768162794852 | 7482 | 0.0999959905376689 | 7425 | 0.09933243254090356 |
| 0.05 | 0.5642097175249418 | 3741 | 0.04999799526883445 | 3729 | 0.04988695500943156 |
| 0.01 | 1.4232146905138892 | 748 | 0.00999692607887949 | 754 | 0.01008709146610657 |
| 0.001 | 4.1356483360291865 | 74 | 0.000989000708338345 | 71 | 0.0009498454828827141 |

**ECDF stability:** `train_vs_selection_ks` = 0.00446978684512106; `train_vs_calibration_ks` = 0.005223804426272655; `selection_vs_calibration_ks` = 0.00233090873155567.

At target FPR `1e-3`, the selection Wilson 95% interval is [0.0007531787855375236, 0.0011978033574092997]. Interpret relative tail deviations together with accepted counts and finite-sample uncertainty.

Detailed evidence: [pca-baseline.md](pca-baseline.md), [score summary](../results/tables/final/task0006-pca-background-summary.csv), [threshold results](../results/tables/final/task0006-pca-thresholds.csv), and [scientific JSON](../results/tables/final/task0006-pca-background-results.json).

### 11.3 Compact AE v1: historical result

Architecture: **`8 -> 6 -> 3 -> 6 -> 8`**, biased Linear layers; ReLU after the first encoder and first decoder layer; linear latent and output. Layer parameter counts 54+21+24+56 = **155**; raw FP32 parameter payload 620 bytes. No BatchNorm, dropout, residual blocks, or stochastic latent variables.

Frozen Task 0007 training choices:

- CPU canonical device; default PyTorch Linear initialization.
- Adam with default settings except learning rate 0.001.
- Batch size 4,096; deterministic shuffled batches, zero workers, no dropped tail.
- Seed 1729 for Python/NumPy/PyTorch and a separate shuffle generator.
- Deterministic algorithms; one intra-op CPU thread; observed inter-op setting 10.
- Channel-mean reconstruction MSE; equal event weights.
- Selection-background loss chooses epoch; patience 15, `min_delta=0`, strict improvement.
- Maximum 200 epochs.
- Calibration first loaded after best-state restoration and JSON export.

| Historical v1 result | Exact recorded value |
| --- | --- |
| Best epoch / executed epochs | 200 / 200 |
| Stop reason | `max_epochs`; zero consecutive non-improvements at stop |
| Best-epoch online training MSE | 0.22106828705179374 |
| Restored training MSE | 0.22100737705508344 |
| Best/restored selection MSE | 0.22261241728016284 |
| Canonical CPU training time | Approximately 31.18 seconds |
| Frozen JSON size | 11,945 bytes |

Forward/training arithmetic is FP32; score residual subtraction and SSE accumulation are CPU float64. Online training loss differs from restored-model loss because weights change within each epoch.

An independent full CPU rerun reproduced parameters, best epoch, scores, thresholds, summaries, tables, and figures exactly. A bounded latent check on the first 4,096 training-background events found finite values and no latent dimension with std at or below `1e-6`; it did not establish anomaly separation.

MPS compatibility used a separately initialized model for five Adam steps on 256 dev-training events, with finite forward/backward/scoring and loss approximately 0.999993265 -> 0.993118167. It exported no model and did not change canonical CPU weights. This is compatibility evidence, not a GPU benchmark.

**Background score summary** (numeric values copied from the curated CSV).

| Statistic | Training background | Selection background | Calibration background |
| --- | ---: | ---: | ---: |
| Events | 699957 | 74749 | 74823 |
| Mean SSE | 1.7680590277287618 | 1.7808993585556105 | 1.772382559767443 |
| Population std | 1.7509019423485825 | 1.7712287676678398 | 1.7475908900988042 |
| Minimum | 0.003588227986996817 | 0.016227133069896114 | 0.010355208376892137 |
| Median | 1.2739098618037987 | 1.27688273999012 | 1.2707276563316627 |
| p90 | 3.5868977539147466 | 3.61893284860893 | 3.6136349957311795 |
| p95 | 4.82906305560913 | 4.8702253578436006 | 4.862806190313804 |
| p99 | 8.589193778026782 | 8.708859649389234 | 8.637979526308955 |
| p99.9 | 16.557594381446762 | 16.29073783445919 | 16.501406212993558 |
| Maximum | 60.359542744402596 | 46.17539573286683 | 35.97693648552873 |

**Frozen calibration and independent selection check.** Calibration total 74,823; selection total 74,749. All decisions use strict `score > threshold`.

| Target FPR | SSE threshold | Calibration accepted | Calibration FPR | Selection accepted | Selection FPR |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.1 | 3.613707299930235 | 7482 | 0.0999959905376689 | 7498 | 0.1003090342345717 |
| 0.05 | 4.862834912896428 | 3741 | 0.04999799526883445 | 3751 | 0.05018127332807128 |
| 0.01 | 8.638938683116985 | 748 | 0.00999692607887949 | 772 | 0.010327897363175426 |
| 0.001 | 16.547151319930283 | 74 | 0.000989000708338345 | 73 | 0.0009766016936681428 |

**ECDF stability:** `train_vs_selection_ks` = 0.003388391473781671; `train_vs_calibration_ks` = 0.003285154347487884; `selection_vs_calibration_ks` = 0.004888069666493078.

At target FPR `1e-3`, the selection Wilson 95% interval is [0.0007768684401031215, 0.0012276233744754283]. Interpret relative tail deviations together with accepted counts and finite-sample uncertainty.

Detailed evidence: [compact-autoencoder.md](compact-autoencoder.md), [score summary](../results/tables/final/task0007-autoencoder-background-summary.csv), [threshold results](../results/tables/final/task0007-autoencoder-thresholds.csv), and [scientific JSON](../results/tables/final/task0007-autoencoder-results.json).

### 11.4 Why Task 0008 was necessary

V1's best epoch equaled the 200-epoch ceiling, with training still improving. The ceiling, rather than the stopping rule, determined the endpoint. Convergence was therefore unresolved, and introducing a richer neural architecture first would have left an avoidable methodological weakness in the compact baseline.

Task 0008 changed only `max_epochs: 200 -> 1000`, in a separate preserved v2 configuration. Architecture, optimizer, learning rate, batch size, initialization, seed/shuffle, deterministic CPU path, patience, `min_delta`, loss, populations, and preprocessing stayed unchanged. It retrained from scratch rather than resuming v1.

Mandatory prefix validation compared epochs 1-200 training/selection losses and best-state progression, plus exact FP32 parameter bytes at epoch 200. A mismatch would abort before interpreting later training or accessing calibration.

The planned cap-failure rule was also explicit: if the 1,000-epoch ceiling still determined the endpoint, report convergence unresolved and require a new methodological decision. Do not silently extend again or change optimizer/learning-rate policy within the closure task.

### 11.5 AE v2: current canonical result

Both independent extensions reproduced the historical first 200 epochs/progression and epoch-200 parameter bytes exactly.

| Current v2 result | Exact recorded value |
| --- | --- |
| Best epoch | 381 |
| Executed/stopping epoch | 396 |
| Stop reason | `patience`, 15 consecutive selection non-improvements |
| Best-epoch online training MSE | 0.21318465057790426 |
| Restored training MSE | 0.21305374425537163 |
| Best/restored selection MSE | 0.21447598731176187 |
| Last-epoch selection MSE, not selected | 0.2146456583262472 |
| Selection MSE improvement relative to v1 | Approximately 0.0081364299684, or 3.654976% |
| First / repeat extension training time | Approximately 59.700 / 59.063 seconds |
| Frozen JSON size | 11,941 bytes |
| Architecture / parameter count | Unchanged; 155 parameters |
| Interchange schema | `artifact_version=1`, despite model generation v2 |

**`compact-autoencoder-v2` supersedes v1 as the canonical compact AE.** The decision used exact prefix reproduction, continued training, strictly improved permitted selection loss, and an intact protocol/embargo. No signal information was used. Preserve v1 configuration, artifact, history, results, and task records.

Convergence closure means reaching the preregistered selection-patience endpoint. It does not prove a global optimum, a stationary training objective, an optimal architecture, or useful anomaly discrimination.

The independent v2 repeat reproduced all 396 epochs, selected weights, score-byte hashes, calibration, summaries, tables, and figure. Task 0008 kept scores in memory and saved their byte hashes; it wrote no per-event score arrays or checkpoints.

**Background score summary** (numeric values copied from the curated CSV).

| Statistic | Training background | Selection background | Calibration background |
| --- | ---: | ---: | ---: |
| Events | 699957 | 74749 | 74823 |
| Mean SSE | 1.7044299494344979 | 1.715807899924844 | 1.7158543992416249 |
| Population std | 1.6910402847301644 | 1.7099464304119902 | 1.7025519418076287 |
| Minimum | 0.005736122334827163 | 0.004962340965368073 | 0.012284028003597458 |
| Median | 1.2366082661770676 | 1.2410126407231847 | 1.2331580252857184 |
| p90 | 3.448114682422827 | 3.478031649472065 | 3.478330842943409 |
| p95 | 4.624700508292133 | 4.656520761689697 | 4.681018670431604 |
| p99 | 8.234200550503136 | 8.329682543754172 | 8.32375940704894 |
| p99.9 | 16.177322559458133 | 16.02839949271337 | 16.438957022844345 |
| Maximum | 70.74881844526628 | 43.981107267994176 | 40.728911220593275 |

**Frozen calibration and independent selection check.** Calibration total 74,823; selection total 74,749. All decisions use strict `score > threshold`.

| Target FPR | SSE threshold | Calibration accepted | Calibration FPR | Selection accepted | Selection FPR |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.1 | 3.478338537407165 | 7482 | 0.0999959905376689 | 7475 | 0.10000133781053927 |
| 0.05 | 4.681070974717348 | 3741 | 0.04999799526883445 | 3698 | 0.04947223374225742 |
| 0.01 | 8.324174660133213 | 748 | 0.00999692607887949 | 749 | 0.010020200939143 |
| 0.001 | 16.642218868621573 | 74 | 0.000989000708338345 | 64 | 0.0008561987451337141 |

**ECDF stability:** `train_vs_selection_ks` = 0.0034533996621334273; `train_vs_calibration_ks` = 0.004705428147432911; `selection_vs_calibration_ks` = 0.0047360563555980395.

At target FPR `1e-3`, the selection Wilson 95% interval is [0.0006706163426728948, 0.0010930819495628859]. Interpret relative tail deviations together with accepted counts and finite-sample uncertainty.

Detailed evidence: [autoencoder-convergence.md](autoencoder-convergence.md), [score summary](../results/tables/final/task0008-autoencoder-background-summary.csv), [threshold results](../results/tables/final/task0008-autoencoder-thresholds.csv), and [scientific JSON](../results/tables/final/task0008-autoencoder-convergence-summary.json).

### 11.6 What the model comparison currently means

PCA retains six dimensions while the AE retains three. Training mean SSE is approximately 0.170393083 for PCA, 1.768059028 for v1, and 1.704429949 for v2. Different compression capacities prevent interpreting these losses as a controlled comparison of linearity versus nonlinearity or as a signal-performance ranking.

Both model families show stable background transfer within finite-sample uncertainty. That establishes functioning score/calibration pipelines. It does not establish sensitivity to signal. No real AUC, AP, signal efficiency, or final test-background operating rate exists yet.

### 11.7 Particle/set design, implementation and readiness (Tasks 0009–0011; no real particle training)

Five biased shared Linear layers: encoder 4→16 ReLU→8 ReLU; local 8→2 linear; global g is the masked mean of the eight encoder values; decoder concatenates [local2,g8] and applies 10→16 ReLU→4 linear. Total 80+136+18+176+68=478 parameters. No raw-feature or hidden skips, input positions, output queries, auxiliary heads or normalization layers. Pooling is FP64 then cast to FP32; dense forward is FP32. Local/output arrays permute with particles; g and score are invariant mathematically, with declared numerical tolerances.

Exact per-particle distance is `d=(r0²+r1²+0.5*r2²+0.5*r3²)/3`. Training and canonical score are `s=L_event=sum_valid(d)/n_retained`, with FP64 subtraction/reduction and equal-event batch/epoch weighting. Correspondence follows each particle's own local code; no nearest-neighbor or assignment solver. Angular outputs are unconstrained sin/cos values; seam continuity and off-circle residuals follow the formula, with no angle normalization or added penalty.

Capacity is 2n+8 real values plus validity metadata (776 floats at n384). Target information intentionally travels through each local2 and through mean8; small-n events can bypass strong compression through context. Equal-particle means can dilute rare residuals and are blind to uniform replication within capacity. Count is supplied by the mask, not independently reconstructed; original multiplicity and retained-pT fraction remain diagnostics. Truncation and absent particle labels constrain the physics information. Learned joint particle features use information absent from the fixed aggregates, but eight pooled means do not capture arbitrary pair relations. No rotation/IRC-safety or anomaly-performance claim.

Preregistered CPU training: seed1729, default Linear initialization in fixed layer order, explicit ordinary Adam options/lr0.001, batch32, workers0, shuffled complete train population/no dropped tail, one intra-op/inter-op thread, deterministic algorithms, no AMP/schedule/fallback. Full selection mean canonical score chooses strict improvements (ties retain earliest); min_delta0, patience20, max200 epochs, best-state restoration and exact independent reload/CPU reproduction before freeze/calibration. Resource or epoch cap without patience means convergence unresolved, requiring a new versioned decision.

The future dev gate uses only first1,024 frozen dev-training IDs, at most three passes/96 steps plus one same-sample score pass, ≤300s; conservative full-cycle extrapolation must be ≤180s. Canonical cycles have a 180s ceiling, each fit+selection run ≤10h and postfit stages ≤1h; two complete repetitions ≤22h. The design alone authorizes no execution; Task 0010 explicitly authorized conditional stages. Its launch gate failed before any real read/update, and no later stage was reached. See [full contracts and acceptance gates](particle-set-baseline-design.md), [budget](../results/tables/final/task0009-particle-set-design-budget.csv), [implementation outcome](particle-set-baseline.md) and [Task 0010 handoff](handoffs/0010-particle-set-baseline.md). Task 0011 preserves this failure and both original/final source acceptance records, renews acceptance after narrow orchestration/probe changes, and records failed stable readiness without consuming the one newly authorized real attempt. See [recovery contracts and evidence](particle-set-resource-recovery.md).

## 12. Evaluation, calibration, and uncertainty

Protocol: `latenttrigger-evaluation-v1`; see [evaluation-protocol.md](evaluation-protocol.md).

### 12.1 Threshold contract

For target FPR `alpha` in `{0.1, 0.05, 0.01, 0.001}`, use calibration-background scores only:

```text
tau_alpha = sorted_scores[ceil((N - 1) * (1 - alpha))]
accept iff score > tau_alpha
```

This is NumPy `quantile(..., method="higher")`, with a strict `>` decision, including ties. It is conservative for empirical calibration acceptance, not a guarantee of population or independent selection acceptance.

Do not jitter ties, interpolate thresholds, or refit them using selection/test. Check frozen thresholds on selection background as a diagnostic. Calibration does not choose the winning model.

Summary quantiles use linear interpolation; calibration quantiles use higher. Preserve that distinction.

### 12.2 Metrics and reporting conventions

| Metric | Convention |
| --- | --- |
| ROC-AUC | Empirical rank-based area, score orientation as supplied; no silent flip |
| Average Precision | Recall-increment-weighted precision, not trapezoidal PR area; report prevalence/class counts |
| Signal efficiency / TPR | Accepted signal / total signal |
| Background efficiency / FPR | Accepted background / total background |
| Rejection | `1/FPR` when nonzero; zero observations require null rejection plus uncertainty, not infinity |
| TPR at fixed FPR | Largest attainable empirical TPR with achieved FPR <= target; no interpolation over unattainable tie jumps |
| FPR at fixed TPR | Highest-threshold empirical point reaching TPR target, initially 0.5/0.8/0.9 |
| Rate uncertainty | Counts, totals, empirical resolution `1/N`, and 95% Wilson binomial intervals |
| Zero-background acceptance | One-sided exact 95% upper bound `1 - 0.05^(1/N)` under the sampling assumption |

Descriptive final ROC operating points are not substitutes for deployable calibration-frozen thresholds. The implementation preserves strict-`>` semantics for ROC cutoffs and handles accept-none/accept-all explicitly.

Calibration contains approximately 74.823 expected tail events at FPR `1e-3`; test background approximately 150.471 at `1e-3` and 15.0471 at `1e-4`. Do not extrapolate extreme rejection beyond empirical support. Binomial intervals do not cover simulation, model-selection, or calibration uncertainty.

Background summaries include count, mean, population std, min, median, p90/p95/p99/p99.9, and max. Compare ECDFs with KS distance descriptively; do not tune against diagnostic p-values. Monitor score/acceptance against multiplicity, scalar pT, maximum pT, massless event mass, and retained pT fraction.

### 12.3 Final unblinding gate

Before the first real final-evaluation request, an explicitly authorized task must freeze candidate models/runtime variants, configurations, preprocessing/store/split identities, score semantics, calibration thresholds, metrics, uncertainty, and reporting plan.

The separate final CLI requires `--allow-test` and explicit frozen inputs. Before each test population request, create/preserve `test-unblinding.json` with UTC, code/base/dirty hashes, model/config/data/calibration identities, planned metrics, and access counts. Keep failed/interrupted records; save final output hashes and completion status. Disclose the exposure and candidate list in the corresponding task record and update this memory's exposure status.

If test results motivate a new design, disclose it and establish a new protocol/population. Do not describe the already-exposed test as untouched again.

## 13. Hardware inference and deployment methodology

**Status:** Planned. Recorded training/scoring times and lifetime RSS are engineering observations, not controlled inference benchmarks.

### 13.1 Required benchmark design

- Declare model-only and end-to-end timing boundaries separately.
- Measure batch-1 latency and a preregistered batch sweep for throughput.
- Include warm-up, independent repeats, and latency distribution statistics such as p50/p95/p99.
- Synchronize asynchronous device execution around timed regions; do not measure dispatch alone.
- Separate raw I/O/decompression, view construction, transfers, forward, canonical score calculation, and threshold decision.
- Preload appropriate tensors for model-only timing.
- Record device/core configuration, OS/runtime/library versions, threads, precision, batch, power mode, concurrent load, and thermal conditions where observable.
- Report memory with scope and method; lifetime RSS after verification is not isolated model memory.
- Establish numerical/decision equivalence tolerances before interpreting runtime variants.
- Use synthetic/dev/allowed-background inputs during development; hardware timing does not require test unblinding.

GPU execution is not presumed faster for a tiny AE. Small-model overhead, batch size, synchronization, and memory traffic may dominate. That is a measurement question.

### 13.2 Apple Silicon, ONNX, and CoreML

Start with reference CPU and MPS inference, then controlled ONNX/ONNX Runtime and CoreML paths. Verify actual operator support, shape policy, execution provider/compute units, and fallback. A configured accelerator provider is not proof that the entire graph executes there.

Preserve preprocessing, score orientation, and decision semantics. Export parity must cover reconstruction, each model's canonical score, and threshold decisions on controlled inputs. Unsupported operations or numerical changes require documented decisions, not silent retraining or altered scoring.

### 13.3 Quantization and reduced precision

Distinguish FP16 computation from integer quantization, weights-only from activation quantization, and numerical compression from measured speed/memory benefit. Fit any learned quantization ranges using training background under a recorded policy. Track variant identity, background score/acceptance changes, and calibration provenance.

If an optimized representation changes numerical scores materially, define/freeze the permitted variant calibration before final unblinding. Do not refit thresholds on test. Quantization is useful only when its measured tradeoff justifies it; preserving FP32 is an acceptable conclusion.

### 13.4 NVIDIA/TensorRT and FPGA/hls4ml

NVIDIA work uses separate supported hardware/runtime and records engine/device/compiler versions and numerical equivalence. Transfer-inclusive and forward-only scopes remain distinct.

FPGA is optional. Begin with a compatible compact model, explicit fixed-point policy, synthesis/resource analysis, and recorded toolchain assumptions. Report LUT/FF/DSP/BRAM, latency, and initiation interval where available. Without a board test, distinguish synthesis estimates from measured deployment performance. Toolchain/hardware availability must not block the core scientific report indefinitely.

### 13.5 Trigger-like simulator

The simulator should model explicitly chosen arrivals, service time, batching/queue policy, acceptance thresholds, capacity, drops, and total latency. Scenarios must be repeatable and state whether service times are measured or assumed. Dataset row order is not physical event timing; dataset signal prevalence is not an arrival-rate estimate.

Simulator design/load tests can use synthetic and allowed-background events. Any real held-out signal efficiency belongs to final frozen evaluation. No claim of a real trigger rate or deadline follows from a synthetic stream.

## 14. Reproducibility and artifact governance

### 14.1 Required provenance

Each scientific experiment must identify:

- Source DOI/version/file size/checksums and integrity result.
- Frozen population protocol, membership/split identity, scope, and counts.
- Preprocessing configuration and feature order/dtypes.
- Model configuration, architecture, selected state, score definition, and artifact identity.
- Calibration inputs, thresholds, decision convention, and result identities.
- Software/hardware environment, seed/RNG/shuffle/determinism/thread settings.
- Actual/base code commit and dirty-source hashes where applicable.
- Output shapes, dtypes, sizes, and checksums.
- Population-access audit and any test exposure.

Keep timestamps, host/output paths, chunk size, elapsed time, and resource observations separate from scientific content identity where the established scheme does so.

### 14.2 Frozen identity registry

| Identity | SHA-256 |
| --- | --- |
| Raw source bytes | `5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6` |
| Preprocessing configuration file bytes | `2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68` |
| Split scientific identity | `74a97d8956a4b75d5710d456bc207fdfa9d27569256bafe7b8e72a7891468fea` |
| Processed full scientific identity | `d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2` |
| Processed dev scientific identity | `2eb34e5b811c12ae5c47afba1ecdb6322feb7c7774b6c9ec5331abe78b3c9a2a` |
| PCA model scientific identity | `d09f96bb7b1536e8da147458f3b0bf50a120bdf6cfc4c247b37970f4f51bf42f` |
| PCA results scientific identity | `285a254847424870b5bee08e5a218733dcbe553ff7a4d00ec5c9493288600ccb` |
| AE v1 model scientific identity | `30dadcdc20fa788d5442e031f44694346d2ac152c9b647b77e17351558a1610e` |
| AE v1 results scientific identity | `490f8cf757ea2f2ab46dc7cee58c8d1b5b40b29cb06b799df7d8361987c222cd` |
| AE v2 model scientific identity | `6a7044ae199cf6609d096377d7bca782b0ae2a0398ad870a4f63cb874a46777b` |
| AE v2 results scientific identity | `324d7363b3e2d2ec96f57cc88790af99895097a35c91efe4839c3cead25c7d33` |

Model/results scientific hashes are computed from canonical JSON of the scientific section using the established implementation; they are not necessarily hashes of the complete file bytes. The preprocessing identity above is a **file-byte** hash. Do not interchange these definitions. Hashes provide integrity identities, not authenticated signatures.

### 14.3 Reproduction claims and storage policy

Independent local repetitions established exact scientific outputs for EDA/splits, dev preprocessing, PCA, AE v1, and AE v2. This does not guarantee bitwise identity on another operating system, BLAS implementation, PyTorch version, or device. Validate a new environment explicitly, using justified preregistered tolerances where exact identity is unavailable. Investigate unexplained mismatches.

Keep raw/processed data, split/label arrays, large outputs, logs, caches, environments, score arrays, checkpoints, and export artifacts ignored unless an explicit curation policy allows a specific small output. The tracked tiny AE JSON exceptions are exact-path exceptions, not a general permission to commit models.

Verify before accepting existing stores. Use staging/verification/finalization to prevent interrupted outputs from appearing complete. Rebuild/replacement must be explicit. Preserve historical model artifacts and task records.

## 15. Decision register: choices and rationale

This register captures enduring project reasoning. Add or supersede decisions here when a task changes the direction; leave implementation chronology in handoffs.

| Decision | Rationale | Status / reconsideration rule |
| --- | --- | --- |
| Start with corrected LHCO R&D v5 | Public, manageable, labeled particle benchmark supports shared model inputs and a clean held-out study | Frozen for the initial benchmark; new sources need a new contract |
| Pure-background training and validation | Isolate unsupervised behavior and prevent signal-based selection | Frozen; contamination/supervised studies are separate experiments |
| Separate selection and calibration backgrounds | Prevent thresholds from influencing model selection and avoid conflating development roles | Frozen |
| Exact-content grouping before splitting | Row-disjoint splits alone do not prevent duplicate leakage | Frozen; fuzzy deduplication is not implemented |
| Keep all physical particles in ragged storage | Preserve interpretability and future views without raw rereads or permanent truncation | Frozen schema 1 |
| Use log1p pT, standardized eta, periodic phi | Handle long positive pT tails, signed nonperiodic eta, and angular continuity | Frozen training-derived contract |
| FP32 physical/model representation | Local source precision supports it; compatible with compact deployment work | Frozen; new precision studies are separate variants |
| Deterministic pT ordering and `Nmax=384` | A reproducible retained prefix meeting declared event/pT retention criteria | Frozen default; alternatives require controlled evidence |
| Begin PCA and AE on the same eight aggregates | Establish simple baselines before adding particle information | Implemented; compression differs, so nonlinearity is not isolated |
| Compact 155-parameter AE | Keep a transparent, practical first neural model without aggressive search | Implemented; no automatic architecture expansion |
| Canonical CPU training, separate MPS smoke | Strengthen local determinism and separate model evidence from device compatibility | Implemented; future inference is measured independently |
| Close convergence before richer models | V1's endpoint was an arbitrary epoch cap | Resolved by unchanged-rule Task 0008; v2 canonical |
| Add particle/set information with local bottleneck and pooled context | Complete equivariant correspondence avoids matching while limiting each local path; 478 parameters and linear forward/score | Design/code unchanged; Task 0011 host readiness still blocked, model feasibility/convergence unknown |
| Bound resource recovery without resetting history | Stable read-only samples precede one lineage-bound exclusive attempt; actual worker rechecks memory | Task 0011 route/tests complete; three failed samples, no reservation or data access |
| Reject pooled event-only Chamfer AE initially | Strict event compression needs output generation and costly matching; Chamfer can miss duplicate frequencies | Reconsider if fixed event-only compression becomes a concrete requirement under a new correspondence/resource contract |
| Reject compact attention initially | One-head candidate costs about 15.8× selected MAC and quadratic activations without demonstrated interaction need | Reconsider only through a new design decision justified by a specific interaction limitation |
| Calibrate on BG and hold out test until candidate freeze | Protect an interpretable final scientific comparison | Frozen |
| Delay runtime/quantization claims until measurements | Smaller files or accelerator availability do not establish useful speedup | Planned measurement gates |
| Use selective, user-executed Git delivery | Keep scientific work reviewable and protect unrelated/local artifacts | Standing workflow requirement |

## 16. Roadmap, milestones, and next-task definitions

The roadmap is dependency-driven. Dates, speedups, and physical trigger budgets are not promised. Future task numbers beyond the next task are provisional and must be reconciled with the live task index.

### 16.1 Milestones

| Milestone | Deliverable and exit criterion | Current status |
| --- | --- | --- |
| Data foundation and aggregate baselines | Verified source/store/config, disjoint populations, reproducible PCA/AE | Completed, Tasks 0001-0007 |
| AE convergence closure | Exact v1 prefix; fixed-rule endpoint; documented canonical supersession | Completed, Task 0008 |
| Particle/set-aware baseline | Justified compact design, correct mask/permutation/loss/score semantics, background-only training/calibration | Task 0009 design/Task 0010 implementation complete; Task 0011 readiness still blocked, canonical stages pending |
| Apple Silicon inference | Repeatable CPU/MPS batch-1 and throughput study, timing/memory scopes and hardware manifest | Planned |
| ONNX / CoreML | Export/operator/provider audit and numerical/decision parity | Planned |
| Precision reduction / quantization | Training-only calibration; measured cost benefit and background stability within declared policy | Planned |
| Trigger simulator | Repeatable arrival/service/queue/acceptance/drop/latency scenarios with explicit assumptions | Planned |
| NVIDIA / TensorRT | Comparable workload on documented supported hardware, engine provenance and transfer-aware timing | Conditional |
| FPGA / hls4ml | Compatible fixed-point model and synthesis/resource/latency evidence; board measurements if available | Optional |
| Final test unblinding | Explicit authorized task; frozen candidate list and thresholds; audited real test metrics | Planned; embargo remains active |
| Final reporting | Quality/cost frontier, bias/uncertainty, reproducibility package, limitations and conclusions | Planned |

NVIDIA and FPGA branches need not block the main report if resources are unavailable. Report unexecuted branches honestly. Final unblinding must not occur merely because another milestone completes.

### 16.2 Next dependency after Task 0011 readiness work

**Manual host preparation → bounded readiness → conditional existing workflow.**

Task 0011's three samples all failed ≥8 GiB launch and ≥4 GiB continuing availability. Its read-only check completed in 5.059 s and reserved no attempt. The original Task 0010 failure, original/final acceptance and zero consumption remain intact; both tasks are still uncommitted locally and need separate reviewed commits using the initial prerequisite snapshots. Remote push and hosted CI are unverified.

The [recovery report](particle-set-resource-recovery.md) gives exact preparation/preflight/run commands. The user chooses which unnecessary workloads to close. A fresh three-sample check must pass every original ceiling, then the fixed recovery worker independently rechecks launch memory. One explicitly authorized Task 0011 real attempt remains; it does not add dev/model-selection allowance. No force, output-directory retry or ledger reset. The sequence remains synthetic acceptance → stable preflight → real dev/resource → conditional full fit/selection → restoration/exact reproduction → freeze → calibration. Failure blocks dependent stages.

If ordinary preparation cannot meet the conservative free+inactive requirement, propose a separate versioned engineering-policy review, supported by bounded process/reader accounting rather than the tiny synthetic tensor footprint. Do not relax the metric here or automatically consume a task number. Current evidence cannot justify changing architecture, device, batch, threads, horizon or objective. **Apple Silicon Inference Benchmark Protocol and Foundation** is recommended only after all particle baseline gates complete.

### 16.3 Proposed tasks after design

- **Particle/set readiness dependency:** Task 0011 routing is implemented; manual host preparation and a passing bounded preflight must precede the single authorized recovery. If the original threshold cannot be met, request a separate versioned engineering-policy review. No new task number is consumed automatically.
- **Apple Silicon inference foundation:** Benchmark PCA, canonical compact AE v2, and the set model when available, with declared synchronized timing and memory scopes.
- **ONNX/CoreML export and equivalence:** Export frozen candidates, audit operator/shape/provider behavior, and validate reconstruction/score/decision parity before speed claims.
- **Reduced-precision study:** Compare supported precision variants using training-only calibration and preregistered tolerances; freeze variant thresholds before final test.
- **Streaming study:** Establish repeatable simulator assumptions and load scenarios, then evaluate queueing/capacity/latency and acceptance.
- **Conditional deployment branches:** NVIDIA/TensorRT and optional FPGA/hls4ml as resources permit.
- **Final freeze/unblinding/report:** Audit prerequisites, authorize test access explicitly, evaluate all declared candidates, report scientific and systems conclusions.

Do not treat these bullets as already executed tasks or fixed task numbers. Choose the next bounded task from the live state, dependency order, unresolved evidence, and user direction.

## 17. Observations, risks, and open questions

### 17.1 Observations that should influence future work

- The data foundation is already substantial. Rebuilding or refitting it without cause adds risk rather than progress.
- Background split score differences are small for current baselines, but finite tails remain statistically limited.
- V2 improved permitted selection reconstruction loss by about 3.65%, resolving the cap concern under the fixed stopping rule. It has not established better anomaly detection.
- V2's maximum training SSE increased while mean/most quantiles decreased. Per-event error need not improve monotonically; do not clip inconvenient tails.
- PCA's lower residual and AE's smaller latent dimension reflect different retained capacity. Avoid a premature narrative of neural superiority or failure.
- A tiny AE can be dominated by runtime overhead. Accelerator speedup is a question to test, not a starting assumption.
- Particle structure is implemented synthetically; real resource feasibility and background convergence remain prerequisites to scientific comparisons. The launch failure concerns current available host memory, not evidence for a richer model or device change.
- An externally readable memory must preserve both general intent and current specifics. Handoffs alone are insufficient for strategic continuity, while this memory alone is insufficient for exact implementation auditing.

### 17.2 Main risks and controls

| Risk | Required control |
| --- | --- |
| Leakage or accidental test access | Guarded readers, explicit scope, access audits, separate unblinding task |
| Reconstruction treated as detection quality | Separate development loss from final signal metrics |
| Background score sculpting | Acceptance/score diagnostics against event scale, mass proxy, multiplicity, and truncation |
| Finite tail statistics | Counts, resolution, intervals; no unsupported extreme-rejection extrapolation |
| Mask/cardinality/ordering mistakes | Hand-computable synthetic cases, permutation/padding tests, explicit score semantics |
| Unjustified richer architectures | Compact baseline first; preregistered scope and resource rationale |
| Export or quantization drift | Variant provenance and preregistered numerical/decision checks; no test recalibration |
| Misleading hardware comparisons | Synchronization, warm-up/repeats, matched workloads, actual provider and timing boundaries |
| Platform/version drift | Exact environment records and explicit reproduction/parity checks |
| Storage/RAM pressure | Chunking/mmap, output estimates, free-space checks, deliberate rebuild policy |
| Narrow simulation interpretation | State preselection, no pileup/MPI, limited topology, and detector/physics limits |
| Task scope expansion | One bounded question/deliverable; explicit new decisions when gates fail |
| Stale project memory | Update this file with every relevant task; verify live state at session start |

### 17.3 Open scientific and engineering questions

- Do current reconstruction scores discriminate the held-out signal usefully at calibrated low FPR? Unknown until final evaluation.
- How much particle-level information is necessary for a meaningful quality/cost improvement?
- The initial set objective is now fixed: corresponding-particle weighted mean, avoiding matching costs. Will its local capacity, rare-particle dilution, count blindness or limited mean context undermine discrimination? Unknown until the appropriate frozen evaluation.
- Can user-controlled host preparation reach the frozen 8 GiB launch requirement? Task 0011 measured three failed samples at 2.9495–3.0176 GiB over 5.010 s. The conservative free+inactive metric differs from macOS pressure; no recovery attempt or real dev budget was consumed. A different accounting policy would require a separate versioned decision.
- Can the CPU implementation meet the factor2/180s epoch and 6 GiB RSS gates, then converge under patience20 within200 epochs? Synthetic allocations/correctness pass; real throughput and convergence are unmeasured.
- What is the actual latency/throughput/memory frontier on the specific Mac configuration?
- Do ONNX/CoreML provide a useful benefit for these model sizes and shapes?
- What precision changes preserve decisions and improve measured cost?
- Which streaming arrival/service assumptions are informative without pretending to reproduce detector operation?
- Will NVIDIA/FPGA access be available, and which deployment branch is worth its engineering cost?
- How robust are conclusions to different signals, simulation shifts, pileup, or real-data selections? These require later protocols, not extrapolation from the current benchmark.

Task 0011 completes narrow preflight/recovery engineering and 296 synthetic checks. Stable readiness still fails the unchanged launch/floor thresholds; no recovery reservation exists. Real reader footprint, dev throughput, canonical convergence, exact reproduction, freeze/calibration and signal usefulness remain unverified; no trained particle hash or performance result exists.

## 18. Development workflow and mandatory Git delivery

The existing task system remains authoritative: [development.md](development.md), [prompts/](prompts/), and [handoffs/README.md](handoffs/README.md).

Every operational task must inspect instructions and repository state, preserve unrelated work, save its specification, implement/research within scope, run relevant validation, document factual outcomes, update its handoff/index, and review the diff.

**Updating this memory is an additional project-level responsibility.** It does not replace a handoff, require inventing another handoff for the memory itself, or turn the memory into an append-only dump of task summaries. Include its relevant update in the same reviewed task change.

### Mandatory clause for every future Codex task prompt

> Read `docs/project-memory.md` before planning the task. Update it before completion wherever this task changes canonical state, project understanding, decisions/rationale, roadmap, risks, open questions, or the recommended next step. Preserve the distinction between implemented evidence and future proposals. Keep detailed execution records in the existing task handoff. At the end, provide exact Git commands for status/diff, selective staging of the intended task files, staged review and whitespace checking, a suitable Conventional Commit, and push for the actual branch/upstream. Do not automatically stage, commit, or push; leave those actions to the user unless explicitly instructed otherwise.

The final Git delivery must replace placeholders with the actual reviewed task file list, commit message, and branch/upstream. Its structure is:

```bash
git status --short --branch
git diff
git add <explicit intended task files, including project-memory.md if changed>
git diff --cached
git diff --cached --check
git commit -m "<appropriate Conventional Commit message>"
git push
```

For a branch without upstream, provide the appropriate explicit push command. Do not invent a resulting commit hash. Avoid broad staging that includes unrelated work or ignored scientific artifacts. Do not claim checks that were not run.

## 19. How to maintain this living memory

### 19.1 Update responsibility

Codex should maintain this file during every relevant task, using the verified outcome. The file's presence does not itself guarantee that every tool/session discovers it: future task prompts must include the mandatory read/update clause above, and a repository entry-point instruction or documentation link should direct sessions here when the user installs it.

An editorial memory update does not consume the next implementation task number or imply that the next planned model task is complete.

For automatic discovery in repository-based Codex sessions, add the following clause to the repository's existing root `AGENTS.md` (or create that entry point if the user chooses to install it). Preserve any existing repository instructions:

```markdown
## LatentTrigger project memory

Read docs/project-memory.md at the start of every task. Verify its current-state
claims against the relevant repository files before implementation. Treat it as
the maintained project-wide explanation of objectives, scientific contracts,
architecture, decisions/rationale, roadmap, risks, and next steps.

Before completing a task, update the affected parts of docs/project-memory.md
with verified durable outcomes and current canonical state. Keep detailed task
chronology in the existing handoff system; do not turn the memory into a second
handoff log. Follow its maintenance rules and preserve the test embargo. Always
provide concrete final manual Git commands; do not automatically stage, commit,
or push unless the user explicitly instructs otherwise.
```

This clause routes sessions to the memory; it does not supersede current user instructions or automatically authorize scientific protocol changes. A README link can aid human discovery but is not a substitute for an instruction to read and maintain the file.

### 19.2 Update procedure at task completion

1. Reconcile actual outcomes with the task specification and evidence. Separate completed, partially completed, failed, and deferred work.
2. Update document control and the start-here state: verified date/base/HEAD, latest completed task, canonical artifacts, embargo/exposure, and next recommended task.
3. Update affected objectives, architecture, measured results, milestone status, and next-task definitions in place.
4. Add or explicitly supersede enduring decisions with rationale, evidence, and the condition under which they could be reconsidered.
5. Resolve or revise open questions and risks. Preserve material limitations even when a result is positive.
6. Update the identity registry only from verified artifacts. Clearly distinguish scientific hashes from file-byte hashes.
7. Add a short revision-history entry and links to detailed reports/handoffs. Do not paste raw logs, all changed files, per-epoch histories, or per-event arrays here.
8. Check internal/relative links, numerical consistency, status terminology, and alignment with the handoff/index. Include the changed memory file in the task's proposed selective Git commands.

If a task leaves project-level state and understanding unchanged, record that the memory was reviewed and required no factual update in the task handoff/final result; avoid meaningless churn. If a task exposes test data, update exposure immediately, including failed or interrupted runs, rather than waiting for a successful completion.

### 19.3 Avoiding stale facts and duplicated sources of truth

- Configurations and artifacts remain the exact machine-readable sources; this file explains their purpose and records key identities/results.
- Handoffs remain historical evidence, not rewritten accounts of later state.
- Keep historical model generations when canonical state changes; explicitly record supersession.
- Replace outdated current-state text rather than leave conflicting assertions in different sections.
- Mark proposals as proposals and unmeasured performance as unmeasured.
- Do not invent dates, counts, hashes, commits, hardware availability, or results.
- If sources conflict, verify them and document the resolution. For example, a task-time handoff can say "awaiting commit" while later Git history establishes that the user subsequently committed it.
- If a planning chat has only this file and no repository access, it must treat current state as the document's verified snapshot and ask for missing evidence only when needed for the next decision.

### 19.4 What to send to a new Work planning chat

This file should be sufficient to explain the project and request a focused next Codex prompt. Send the latest version, state any new user priorities/constraints, and include the latest handoff or narrow configuration/report only when the next prompt needs implementation details absent here.

The planning chat should derive the next task from objectives, dependency order, verified state, unresolved questions, and scope boundaries. It must not issue another completed task, infer that a proposal was implemented, or turn hardware work into implicit test unblinding.

## 20. Instructions to future ChatGPT/Codex sessions

### 20.1 Binding operating rules

1. Read this memory, then verify current repository instructions/state and the relevant exact contracts before implementation.
2. Preserve the pure-background development protocol and real test embargo. This memory does not authorize unblinding.
3. Reuse frozen source, split membership, feature semantics/order, scalers, FP32 representation, ordering, `Nmax=384`, and mask/padding policy unless a new explicit versioned decision changes them.
4. Fit using training background; select using selection background; calibrate thresholds after restoration/freeze on calibration background. Never use signal/test performance to choose those quantities.
5. Treat compact AE v2 as canonical at this snapshot. Preserve v1 and PCA; do not silently overwrite history.
6. Distinguish reconstruction/generalization evidence from anomaly-discrimination evidence, compatibility from performance, local exact repeats from cross-platform guarantees, and measured runtime from hypothetical trigger capability.
7. Use one bounded, sequentially numbered task; keep existing prompt/handoff/index records and update this living memory as an additional responsibility.
8. Keep large/local artifacts out of Git. Preserve unrelated user work and read-only synced reference sources.
9. Report actual checks and limitations. Unknown remains unknown; pending checks remain pending.
10. Always provide concrete final manual Git commands. Do not stage, commit, or push automatically.
11. Treat any real model/evaluation test access as exposure. Preserve failed access records and update this memory immediately.
12. Do not assume a Transformer, a hardware speedup, or signal superiority. Let explicit questions and evidence determine the next step.

### 20.2 Initial checklist

- [ ] Locate the operational repository and distinguish it from any ChatGPT project mirror.
- [ ] Read applicable repository instructions and inspect Git status, branch/upstream, HEAD/base, and recent commits.
- [ ] Check this file's date and current state against the latest README/handoff/index and artifacts.
- [ ] Identify the next actual task number and whether the requested work is implementation, methodological design, measurement, or planning.
- [ ] Read [development.md](development.md), [evaluation-protocol.md](evaluation-protocol.md), [preprocessing-contract.md](preprocessing-contract.md), and relevant reports/configurations.
- [ ] Verify source/store/config/split/model provenance needed by the task; do not reflexively regenerate or refit frozen inputs.
- [ ] Confirm expected population counts and that the work plan avoids test model/evaluation access.
- [ ] Check resource and environment requirements before expensive runs.
- [ ] Define the task's bounded deliverable, acceptance criteria, and non-scope.
- [ ] Include the memory read/update and final manual Git clauses in a generated Codex prompt.

### 20.3 Reusable request for a new Work planning chat

```text
We are continuing LatentTrigger. Use the attached/current docs/project-memory.md
as the project-wide living memory. It is separate from task handoffs.

First identify the verified current state, completed work, frozen scientific
contracts, unresolved questions, and next dependency. If repository access is
available, reconcile the memory with current files; otherwise state that the
document is the latest provided snapshot and do not invent newer results.

Generate a concrete, bounded Codex prompt for the next appropriate task. Preserve
background-only development and the real test embargo. Require inspection of the
relevant exact contracts/configurations and existing prompt/handoff workflow.
Require an in-place update to docs/project-memory.md for project-level outcomes,
decisions/rationale, roadmap, risks, and the next step. Require final exact manual
Git review/staging/commit/push commands, with no automatic staging/commit/push.

Do not repeat a completed task or assume that a proposed model/runtime exists.
My current priority or requested task is: [state the new objective, if any].
```

### 20.4 Reusable start instruction for an implementation session

```text
Read docs/project-memory.md and the current repository instructions first.
Verify Git, the latest task index/handoff, exact relevant contracts/configurations,
canonical artifact identities, and test-embargo status before making changes.
Execute only the requested task within its stated scope. Update the living memory
with durable project outcomes and reasoning, while leaving execution chronology
in the task handoff. Report actual validation and provide concrete manual Git
commands. Do not automatically stage, commit, push, or unblind real test data.
```

## 21. References and memory revision history

### 21.1 Local sources of truth

- [Project overview](../README.md) and [package/dependency configuration](../pyproject.toml).
- [Development protocol](development.md) and [handoff index](handoffs/README.md).
- [Data design](data-design.md), [raw audit](raw-data-audit.md), [training EDA](training-data-eda.md).
- [Preprocessing contract](preprocessing-contract.md), [pipeline](preprocessing-pipeline.md), [frozen configuration](../configs/data/lhco_rnd_v5.json).
- [Evaluation protocol](evaluation-protocol.md).
- [PCA report](pca-baseline.md) and [configuration](../configs/models/pca_baseline.json).
- [Historical compact AE report](compact-autoencoder.md), [v1 configuration](../configs/models/compact_autoencoder.json), and [v1 artifact](../artifacts/models/compact-autoencoder-v1/model.json).
- [AE convergence report](autoencoder-convergence.md), [v2 configuration](../configs/models/compact_autoencoder_v2.json), and [v2 artifact](../artifacts/models/compact-autoencoder-v2/model.json).
- [Task 0006 scientific results](../results/tables/final/task0006-pca-background-results.json).
- [Task 0007 scientific results](../results/tables/final/task0007-autoencoder-results.json).
- [Task 0008 scientific results](../results/tables/final/task0008-autoencoder-convergence-summary.json).
- [Task 0008 handoff](handoffs/0008-autoencoder-convergence.md) for detailed closure evidence.
- [Particle/set design](particle-set-baseline-design.md), [design-only JSON](../configs/models/particle_set_baseline_design_v1.json), [analytic budget](../results/tables/final/task0009-particle-set-design-budget.csv) and [Task 0009 handoff](handoffs/0009-particle-set-baseline-design.md).
- [Particle/set implementation](particle-set-baseline.md), [executable JSON](../configs/models/compact_particle_set_autoencoder_v1.json), [gate/resource evidence](../results/tables/final/task0010-particle-set-gate-summary.json) and [Task 0010 handoff](handoffs/0010-particle-set-baseline.md).
- [Bounded resource recovery](particle-set-resource-recovery.md), [readiness summary](../results/tables/final/task0011-particle-set-recovery-summary.json) and [Task 0011 handoff](handoffs/0011-particle-set-resource-recovery.md).

### 21.2 External references

- [Zenodo LHCO R&D v5](https://zenodo.org/records/6466204), [version DOI](https://doi.org/10.5281/zenodo.6466204), and [API metadata](https://zenodo.org/api/records/6466204).
- [Original R&D schema description](https://zenodo.org/records/4536377) and [official LHCO challenge website](https://lhco2020.github.io/homepage/).
- [The LHC Olympics 2020 benchmark paper, arXiv:2101.08320](https://arxiv.org/abs/2101.08320).
- [CERN openlab R&D directions](https://openlab.web.cern.ch/our-rd-directions/).
- [ONNX Runtime CoreML execution provider](https://onnxruntime.ai/docs/execution-providers/CoreML-ExecutionProvider.html).
- [Apple Core ML optimization guide](https://apple.github.io/coremltools/docs-guides/source/opt-overview.html).
- [NVIDIA TensorRT documentation](https://docs.nvidia.com/deeplearning/tensorrt/latest/index.html).
- [hls4ml introduction](https://fastmachinelearning.org/hls4ml/intro/introduction.html).

Runtime documentation and compatibility must be rechecked when the corresponding deployment task begins. External context explains motivation/capabilities; local artifacts and reports establish project results.

### 21.3 Memory revision history

| Revision / date | Durable change | Evidence basis |
| --- | --- | --- |
| 1.0 / 2026-10-06 | Established an English, maintained project-wide memory distinct from task handoffs; incorporated Tasks 0001-0008, canonical v2, frozen scientific contracts, rationale, roadmap, update rules, and session bootstrap instructions | Repository snapshot `0645077`, exact configurations/artifacts/curated results, scientific reports and historical handoffs |
| 1.1 / 2026-10-06 | Selected local2/mean8 particle reconstruction design over event-only Chamfer and attention; froze score, capacity limits, CPU resource/convergence gates and proposed Task 0010; no implementation/training/calibration or new population access | Task 0009 design-only specification, analytic budgets/synthetic formulas and rechecked Task 0008 small-file evidence |
| 1.2 / 2026-10-06 | Exact particle design implemented with 247 synthetic tests and measured temporary allocations; 8 GiB launch gate failed at 3.694794 GiB before real reads, leaving canonical stages pending; next bounded decision addresses host resources without scientific drift | Task 0010 implementation/report/curated gate summary; base `96ef5aa`; zero real population requests |
| 1.3 / 2026-10-06 | Added one lineage-bound recovery route and stable read-only readiness; 296 synthetic tests pass but three samples fail unchanged memory thresholds, leaving all real particle stages pending and recovery allowance unused; separate prerequisite snapshots preserve uncommitted Task 0010 | Task 0011 report/readiness summary; zero new real attempts/reads/updates; original scientific/resource identities unchanged |

Keep future entries short and focused on project-level changes. Update current-state sections in place; the revision table is not a second task log.
