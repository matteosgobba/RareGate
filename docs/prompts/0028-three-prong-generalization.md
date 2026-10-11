# LatentTrigger — Task 0028: Frozen Three-Prong Generalization Protocol and Guarded Foundation

You are continuing **LatentTrigger**. Perform **Task0028 only**.

The initial native scientific study and Task0027 synthesis are complete.

Prepare a prospective extension asking:

**How do the same frozen native PCA-v1 and compact-autoencoder-v2 respond to the reserved LHCO three-prong signal, using the accepted Task0026 background score reference and original calibrated thresholds?**

This is a signal-topology generalization study with a reused, already-exposed background reference. It is not a fully independent signal/background benchmark or a background domain-shift test.

This prompt authorizes Phase A:

1. Primary-source metadata research.
2. Protocol and compatibility design.
3. Implementation of the guarded extension.
4. Self-contained synthetic validation.
5. A concrete source-bound execution plan and readiness package.

**No real three-prong payload download, numerical opening, preprocessing or scoring is authorized by this prompt.**

Complete Phase A before requesting explicit authorization for a conditional bounded Phase B.

No fitting, optimizer updates, recalibration, candidate/threshold selection, new export, runtime benchmark, MPS check or particle execution.

## 1. Inspect actual state and preserve the completed study

Read applicable instructions, development protocol, living memory, data design, preprocessing/evaluation contracts and Task0026–0027 reports, summaries and handoffs.

Planning inspection found:

```text
branch: main
upstream: origin/main
working tree/index: clean

Task0027 commit:
c6f07da41c0053844d0ee5670651619f4e83660a

Task0026 Phase B commit:
839f8cd68a87c776d84afa2e189e157536258b2d
```

Verify live state, full commit identities and numbering. Preserve unrelated work.

Save:

```text
docs/prompts/0028-three-prong-generalization.md
docs/handoffs/0028-three-prong-generalization.md
```

Preserve original models, scalers, calibration, scientific outputs, protocols, acceptances, receipts and executable behavior.

Task0026 remains accepted and consumed; both original test populations remain exposed.

Task0025 remains failed/consumed with provisional speedups. Particle remains 192/192 consumed and locally deferred.

Synced `sources/` remain read-only.

## 2. Pin the new signal source from primary evidence

Primary source:

https://zenodo.org/records/6466204

Reserved particle-level file:

```text
events_anomalydetection_Z_XY_qqq.h5
```

The publisher describes a separate 100000-event three-prong signal sample. Do not infer physics from the filename alone.

Historical Task0002 metadata records:

```text
version DOI: 10.5281/zenodo.6466204
expected bytes: 235488994
published MD5: 54e123a86143b668f9cb76905152a124
```

Recheck official metadata, checksum, version-specific download URL, attribution/license and relevant generator/detector documentation. Small metadata and configuration-card requests are authorized.

Distinguish:

- Publisher-declared facts.
- Previously verified metadata.
- Freshly verified metadata.
- Payload facts that remain unverified until authorized custody.

If an API is unavailable, use primary record documentation and preserved evidence honestly. Do not invent a fresh API verification or a locally computed payload SHA256.

No binary payload, remote HDF preview, high-level feature file, black-box data or answer-key download during Phase A.

Use the particle file because the frozen eight aggregates cannot be replaced by the published jet-feature representation.

Determine and preregister supported HDF/table encodings from documentation and existing reader capabilities. Do not silently assume that the signal-only file has the original mixture’s appended-label column.

Document unresolved layout details and bounded custody rejection behavior.

## 3. Freeze the scientific scope

Candidates remain:

```text
PCA-v1:
six components
native centered/non-whitened FP64 reconstruction

Compact AE v2:
8 → 6 → 3 → 6 → 8
155 FP32 parameters
native CPU FP32 reconstruction
```

Bind the existing model/config/calibration scientific and file-byte identities.

Preserve eight-channel FP64 reconstruction SSE, casting before subtraction, higher anomalous, and all original strict `score > threshold` decisions.

Use the exact original feature formulas, feature order, physical normalization and training-derived scalers.

Compute aggregates from all valid physical particles before any particle-view truncation. No fitted statistics, clipping, new feature, jet clustering, score inversion or precision change.

The new signal is evaluation-only. It supplies no tuning/development subset.

Do not choose between PCA and AE or select an operating threshold in response to the new results.

## 4. Bind the reused background reference

Use only the accepted Task0026 score arrays:

```text
results/evaluation/task0026-frozen-pca-ae/final/PCA/test_background-scores.npy
results/evaluation/task0026-frozen-pca-ae/final/AE/test_background-scores.npy
```

Bind each to its accepted candidate, calibration, source ordering, population count, evaluation output, audit and parent-acceptance lineage.

Expected background count per candidate: 150471.

During Phase A, small metadata, file size, bounded NPY-header checks and byte-integrity verification are permitted. Do not numerically load or analyze the score arrays.

Phase B authorization must explicitly cover their numerical reuse.

Do not reopen the original raw/processed population or run a model on the original background again.

Do not reconstruct an empirical background distribution from summary quantiles or substitute synthetic background values.

If required arrays or accepted lineage are missing or inconsistent, report the blocker. No background re-scoring fallback.

The reference retains existing exposure and finite-sample limitations. Its FPR is not a fresh independent background measurement. Comparisons with the earlier study share this reference and must not be described as statistically independent.

## 5. Design explicit compatibility and overlap gates

The original artifacts correctly bind their original training/config/store provenance.

A new signal artifact must have its own source and scientific identity. Do not pretend it is the original processed store or alter training provenance to pass a validator.

Implement an isolated compatibility contract binding:

- Original frozen model/training provenance.
- Original transform/scaler identity.
- New signal source identity.
- Exact feature definitions/order/dtype.
- Custody, overlap and preparation results.
- Reused accepted background-score identities.

Keep original `run_final` and validators unchanged. Do not disable validation or use an unchecked fast reader.

Preregister an integrity-only overlap audit against the original full R&D fingerprint registry. This future read must be explicitly covered by Phase B authorization.

Reuse the original canonical exact-content fingerprint algorithm, excluding labels and row IDs. Verify both within-source uniqueness and overlap with all original R&D roles.

For this first extension, refuse scientific evaluation if exact duplicates, overlap or incompatible identity are found. Preserve the failed custody evidence; do not silently select a favorable subset.

A separate file, DOI or generator description does not prove event independence. Exact-content checking does not prove absence of approximate duplicates.

Labels, source IDs and fingerprints remain metadata, never model inputs. If labels are present, verify the declared signal role. If absent, record the publisher-provided class provenance and its limits.

## 6. Implement a minimal guarded extension

Reuse existing scientific functions and validated supervision primitives where appropriate.

Implement isolated orchestration for:

1. Authorized acquisition and raw integrity.
2. Streaming custody, overlap audit and frozen feature preparation.
3. PCA signal scoring and cached-background reuse.
4. AE signal scoring and cached-background reuse.
5. Consolidation/reporting.

Keep the controller stdlib-only and use one numerical worker at a time.

Reserve a distinct fixed namespace, for example:

```text
results/evaluation/task0028-three-prong/
```

Use a distinct raw/preparation namespace. Do not alter original data or Task0026 outputs.

Require current source/protocol/dependency identities, durable phase/access records, exclusive reservation, parent-enforced deadlines and normal exit/reaping.

A body receipt remains `body_complete_awaiting_exit`; only the parent accepts the stage after normal termination.

No success promotion after timeout, forced termination or an incomplete gate. A failed stage prevents subsequent scoring. No alternate dataset, retry, resume or enlarged limit after a reserved failure.

Keep existing dependencies unchanged. Avoid importing ONNX/MPS for this native study.

## 7. Preregister finite Phase B limits

Create a strict protocol, for example:

```text
configs/evaluation/frozen_three_prong_v1.json
```

For this prospective short study, preregister:

```text
numeric-worker observed lifetime RSS ceiling: 6 GiB
native reservation ceiling: 512 MiB
stdlib controller RSS ceiling: 128 MiB

acquisition and raw integrity: ≤ 300 s
custody/overlap/feature preparation: ≤ 180 s
each native candidate: ≤ 120 s
consolidation: ≤ 30 s
whole study: ≤ 900 s
termination/kill/reap grace: ≤ 2 s inside stage deadlines
```

Document phase scope and accounting. Download/decompression/preprocessing costs remain separate from model scoring.

Use streaming/chunked raw processing and bounded temporary arrays. Do not require loading the full expanded HDF table into memory.

Global available RAM is contextual; no idle-host wait or floor. WARN is advisory, CRITICAL blocks, unavailable pressure is disclosed, invalid primary accounting blocks.

Record sampling intent, terminal coverage gaps and practical enforcement limits. RSS/native overlap. These limits are prospective, not proof of actual future requirements.

## 8. Preserve the metric contract

Reuse evaluation-v1 conventions:

- ROC-AUC with supplied orientation.
- AP with actual class counts/prevalence.
- Original calibrated thresholds at targets 0.1/0.05/0.01/0.001.
- Achieved background FPR and new signal efficiency/counts.
- Existing conditional rate intervals and finite-sample conventions.
- Attainable descriptive fixed-FPR/fixed-TPR points.
- Clearly labeled descriptive relative acceptance and selected signal fraction.

Do not recalibrate on the reused background or new signal. Empirical ROC cutoffs remain descriptive.

Do not claim significance or uncertainty for model differences/ratios without an explicitly justified prospective method. AUC/AP remain descriptive under the existing convention.

For the documented 100000 signal events, preserve B4096:

```text
24 full batches + final batch1696
25 score batches per candidate

Expected complete new scoring:
50 batches
200000 signal presentations
100000 unique new signal events
```

Two accepted background arrays are reused numerically. There are zero new original-background model population requests or forward calls.

Published counts become confirmed only after custody passes. Record actual counts and any failure without fabricating completeness.

## 9. Validate Phase A without operational numerical inputs

Use synthetic HDF, fingerprint, feature, score and model fixtures.

Meaningful tests must cover:

- Source/version/checksum/size mismatch.
- Supported and refused HDF encodings.
- Padding, units, physical normalization and label separation.
- Exact frozen scaler/feature compatibility.
- Duplicate and cross-role overlap rejection.
- Wrong cached-background identity/count/dtype/hash.
- Scoring orientation, FP64-before-subtraction and strict ties.
- Batch4096 and tail1696.
- Metric equivalence to unchanged helpers.
- Durable pre-read/progress audit and in-flight interruption.
- Reservation, failed-stage propagation and consumed refusal.
- Body-complete worker that hangs instead of exiting.
- Resource/deadline failure, cleanup and reaping.

Use actual installed native libraries on toy fixtures. Do not open operational signal, fingerprint or score arrays through tests.

Run relevant full/portable validation, lint/format and dependency checks appropriate to the new orchestration. Report actual counts; neither the old1259 suite nor Task0027’s12 tests automatically covers new code.

Preserve historical source files while giving new code its own acceptance. Do not call an old consumed controller to validate the new extension.

## 10. Make authorization the final Phase A step

After implementation, synthetic validation and source acceptance, produce a reviewable plan containing:

- Exact three-prong source/version/file/checksum/size.
- Candidate/transform/calibration identities.
- Reused background score identities.
- Original fingerprint-registry integrity reference.
- Compatibility/overlap rules.
- Metrics, counts, limits and fixed outputs.
- Exact guarded execution command.
- Exposure and failure behavior.

Then ask for explicit human authorization covering:

1. One bounded acquisition of the pinned signal payload.
2. Integrity-only raw/overlap inspection, including original fingerprints.
3. Frozen feature preparation.
4. One signal evaluation per frozen candidate.
5. Numerical reuse of the two accepted background score arrays.
6. No subsequent test-guided fitting, recalibration or candidate/threshold selection.

Do not ask while the package is still incomplete. If a required prerequisite is unresolved, finish unaffected work and state the concrete blocker.

No consent record or Phase B execution before actual human approval. A locally created file, CLI flag or readiness result is not human consent.

Authorization is conditional on all custody/compatibility gates passing. An interrupted access must still be disclosed.

## 11. Produce honest documentation and current-state records

Create:

```text
docs/three-prong-generalization.md
results/tables/final/task0028-three-prong-generalization-summary.json
```

Before Phase B, report implementation/readiness and authorization pending. No new scientific scores, metrics or figures exist.

Update README, memory and index. Increment from the verified current memory revision, expected1.21.

Keep the completed initial study intact. The new study has a new signal and a reused exposed background reference; it does not establish fresh background generalization.

Historical original test exposure remains YES/YES. Record new-signal status separately and distinguish raw custody, preparation, model scoring and cached-score reuse.

Particle remains192/192; Task0025 remains failed/consumed. No hardware branch is a prerequisite here.

## 12. Deliver detailed Italian output

Write a self-contained final response in Italian, approximately600–1000 words excluding Git.

Explain:

- What was implemented and validated.
- Verified source facts and unresolved payload facts.
- Frozen candidate/transform/threshold identities.
- Why background reuse is legitimate and what it limits.
- Overlap and compatibility gates.
- Planned access/count/resource budget.
- Readiness and authorization status.
- Actual results only if Phase B is subsequently authorized and completed.
- One concrete next action.

At Phase A completion, include:

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
new_three_prong_signal model/evaluation accessed: NO
new_original_background_forward_calls_in_Task0028: 0
new_numeric_cached_background_score_loads_in_Phase_A: 0
```

Use actual flags after authorized access. Never keep NO after new signal evaluation begins.

End successful Phase A with the concrete authorization question and explain the prospective-evaluation requirement.

Finish with actual selective manual Git commands for branch/upstream, diff/staged review, whitespace checks and outcome-appropriate Conventional Commit/push.

Do not stage, commit or push automatically. Keep payloads, fingerprints, per-event features/scores, logs, manifests, acceptances and execution receipts ignored.