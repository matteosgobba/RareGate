# LatentTrigger — Task 0027: Frozen Scientific Synthesis and Quality/Cost Frontier

Original user specification, received 2026-10-11 (Europe/Rome).

You are continuing **LatentTrigger**. Perform **Task0027 only**.

Task0026’s authorized scientific evaluation is complete, accepted and consumed. Task0022 supplies the accepted native CPU inference benchmark.

Produce an integrated scientific synthesis and a clearly scoped quality/cost comparison using those existing accepted results.

This task authorizes offline analysis of curated results, deterministic arithmetic, documentation and static figure generation. No new model execution or population access is needed.

No fitting, optimizer updates, recalibration, threshold/candidate selection, held-out replay, export, runtime benchmark, MPS check or particle execution is authorized.

Both held-out populations are already exposed. Preserve that status permanently.

## 1. Inspect live state and preserve the Task0026 continuation

Read applicable instructions, `docs/development.md`, `docs/project-memory.md`, the evaluation protocol and Task0022–0026 reports, summaries and relevant handoffs.

Planning inspection found:

```text
branch: main
upstream: origin/main
HEAD:
e69d80ed802492be3db965d0ab69ce3e1a50395d
```

At inspection, Task0026 Phase B had eleven intentional uncommitted files: six modified files and five untracked files. The index was empty.

Verify actual live state. The user may have committed that continuation before this task starts.

If it remains uncommitted:

- Record its exact pre-existing state.
- Preserve its accepted contents and evidence.
- Distinguish Task0027 additions from Task0026 work.
- Explain overlapping README/memory/index changes in the final Git delivery.
- Do not silently reset, stage or fold the previous continuation into this task.

Do not invent a Phase B commit or infer a successful push/hosted CI run.

Save:

```text
docs/prompts/0027-frozen-scientific-synthesis.md
docs/handoffs/0027-frozen-scientific-synthesis.md
```

Preserve old scientific artifacts, executable/protocol bytes, acceptances, receipts and historical records. Synced `sources/` remain read-only.

## 2. Establish a small, explicit evidence registry

Primary scientific sources:

```text
docs/guarded-pca-ae-evaluation.md
results/tables/final/task0026-guarded-pca-ae-evaluation-summary.json
results/tables/final/task0026-pca-ae-scientific-comparison.csv
results/tables/final/task0026-pca-ae-calibrated-operating-points.csv
results/tables/final/task0026-pca-ae-empirical-operating-points.csv
results/figures/final/task0026-pca-ae-roc-pr.png
```

Primary cost sources:

```text
docs/frozen-cpu-benchmark-v2.md
results/tables/final/task0022-frozen-cpu-benchmark-v2-summary.json
results/tables/final/task0022-frozen-cpu-benchmark-v2-cells.csv
```

Verify accepted status, candidate identities, score definitions, calibration provenance and agreement between curated JSON/CSV/report values.

Record source file-byte hashes separately from canonical scientific hashes.

Small existing metadata and receipts may be inspected when necessary to resolve provenance. Do not reopen:

- Raw or processed numerical arrays.
- Prepared benchmark inputs.
- Saved per-event scores.
- ROC/PR numerical curve archives.
- Model population readers.

Do not instantiate models or call scoring/evaluation functions. Existing aggregate results are sufficient.

Keep dependencies unchanged. Use the installed environment for offline rendering only.

## 3. Preserve the scientific findings exactly

The accepted native candidates are:

```text
PCA-v1:
six retained components
centered, non-whitened FP64 reconstruction

Compact AE v2:
8 → 6 → 3 → 6 → 8
155 FP32 parameters
canonical native CPU reconstruction and FP64 SSE
```

Both preserve higher-score-is-more-anomalous orientation and strict `score > threshold`.

Scientific reference values:

```text
PCA ROC-AUC:
0.4684886579473786

PCA AP:
0.36437915494963025

AE ROC-AUC:
0.6600638025267328

AE AP:
0.5474272683246686

Test background:
150471

Test signal:
100000

Evaluated signal prevalence:
0.3992478171125599
```

Explain AP’s dependence on the evaluated mixture. That prevalence is not a physical LHC signal rate.

PCA’s AUC below 0.5 is reported under its frozen orientation. Do not invert its score or compute an alternative model result after observing the test.

AE has better observed ranking and more accepted signal at all four frozen thresholds for the declared candidates and signal sample. Do not turn that into universal neural superiority.

The retained dimensions differ, six versus three. Neither residual magnitude nor this comparison isolates the causal effect of nonlinearity.

## 4. Make operating-point utility visible

Retain all four calibrated target FPRs:

```text
0.1, 0.05, 0.01, 0.001
```

For each candidate/threshold, show:

- Original frozen threshold.
- Nominal calibration target.
- Achieved test-background FPR.
- Accepted background count and denominator.
- Signal efficiency, accepted count and denominator.
- Existing Wilson intervals.
- Existing finite rejection.

Use the separate empirical operating-point table only as descriptive ROC evidence. Do not promote its cutoffs to deployable thresholds.

Explicitly explain the strict-tail observation:

```text
At calibration target FPR 0.001:

PCA:
124 background accepted
2 signal accepted

AE:
116 background accepted
56 signal accepted
```

AE’s observed signal efficiency is `0.00056`, while its background FPR is approximately `0.0007709127`.

Its better result than PCA does not establish signal enrichment at this operating point.

For interpretation, this task may derive the following arithmetic descriptions from existing counts at all four original operating points:

```text
relative acceptance =
signal efficiency / background FPR

selected signal fraction =
accepted signal / (accepted signal + accepted background)
```

Label these as **post-evaluation descriptive arithmetic from accepted aggregate counts**, not newly preregistered Task0026 metrics or an additional experiment.

Show all four operating points; do not search for a new cutoff or select a winning threshold.

At the strict AE point:

```text
relative acceptance ≈ 0.7264
selected signal fraction = 56 / 172 ≈ 32.5581%
initial evaluated prevalence ≈ 39.9248%
```

Explain that these observed values indicate no enrichment in that selected slice of the evaluated mixture. Do not claim a statistical significance result, physical purity or transport of these rates to actual LHC populations.

Preserve the original uncertainty scope. Wilson intervals are conditional rate summaries; they do not include calibration, model or simulation uncertainty. Do not construct an unsupported interval for a ratio or model difference.

Avoid headline multiplicative tail gains based on PCA’s two accepted signals.

## 5. Build a scoped quality/cost comparison

Join candidate scientific identities from Task0026 to the same native model identities in Task0022.

Use Task0022’s public adapter/decision scope as the primary cost comparison on prepared features. Include all five accepted batch sizes:

```text
1, 8, 32, 128, 1024
```

Keep exactly ten candidate/batch rows in the main frontier table.

Preserve statistical definitions:

- Median of the three worker p50 values.
- All three worker medians/means or explicit links to them.
- Pooled mean from all 600 invocations.
- Throughput = batch size / pooled mean batch duration.
- Batch latency versus amortized time per event.
- Explicit nanosecond/microsecond/event-per-second units.

Do not average reciprocal invocation times or call the reciprocal of a median the accepted pooled throughput.

Useful reference values:

```text
Adapter B1 median of worker p50s:
PCA: 8.125 µs
AE: 24.708 µs

Adapter B1024:
PCA median of worker p50s: 44.4585 µs
AE median of worker p50s: 85.5 µs

B1024 throughput from pooled means:
PCA: 22324738.539122738 events/s
AE: 11871388.805257171 events/s
```

Retain the effects of outliers and repetition variability. Do not filter the historical AE observations to improve its cost.

Explain the cross-task scope:

- Scientific quality was evaluated using canonical batch 4096 and complete tails.
- CPU costs were measured separately on 1024 prepared dev-training rows.
- Cost batches are 1–1024.
- Scientific metrics are the canonical reference result, not independently measured held-out quality for every cost batch.
- Input loading, raw event processing and preprocessing are outside the adapter benchmark.

Task0026’s 31.095 s campaign includes custody, audit, metrics and reporting. Do not convert it into a new inference benchmark.

Task0025’s ratios remain provisional and must not enter accepted cost coordinates.

Discuss dominance only within a stated metric, batch and scope. With two candidates, this is a sampled tradeoff, not a continuous or universal Pareto frontier.

Do not claim hardware-trigger throughput, end-to-end latency or production suitability.

## 6. Produce an integrated scientific report

Create:

```text
docs/scientific-synthesis.md
results/tables/final/task0027-frozen-scientific-synthesis-summary.json
results/tables/final/task0027-quality-cost-frontier.csv
results/tables/final/task0027-operating-point-interpretation.csv
```

The report should be understandable without reading the task history.

Include:

1. A concise abstract.
2. Research question and scope of the initial study.
3. Dataset, duplicate-safe populations and preprocessing.
4. Background-only model development and independent calibration.
5. Frozen candidate identities, capacity and score semantics.
6. Accepted scientific results.
7. Calibrated utility versus global ranking.
8. Accepted CPU quality/cost tradeoffs.
9. Numerical/runtime evidence and its limits.
10. Exposure, reproducibility and artifact provenance.
11. Supported conclusions and open questions.

Keep detailed execution chronology in the handoff or linked task reports.

Separate:

- Accepted findings.
- Descriptive arithmetic derived in Task0027.
- Plausible explanations.
- Untested hypotheses.
- Planned extensions.
- Failed or unavailable branches.

Do not invent a mechanism explaining PCA’s weak signal ranking or AE’s strict-tail behavior. Possible representation/bottleneck/score explanations remain hypotheses without new diagnostics.

The supported conclusion is a moderate observed AE advantage for these frozen aggregate models and this signal, with higher native CPU cost and weak strict-tail utility.

## 7. Create compact static scientific figures

Use standard plotting tools and existing aggregate tables.

Create:

```text
results/figures/final/task0027-quality-cost-frontier.png
results/figures/final/task0027-calibrated-operating-points.png
```

Suggested primary quality/cost panels:

- ROC-AUC versus adapter B1 median latency.
- ROC-AUC versus adapter B1024 pooled throughput.

Use two labeled candidate points per panel. Explain the different batch/statistical cost scopes and canonical scientific reference.

The operating-point figure should show all eight frozen calibrated points, achieved FPR versus signal efficiency, the existing intervals and a `TPR = FPR` reference.

Use axes that make the low-FPR region readable. Distinguish fractions from percentages and nominal targets from achieved rates.

Do not interpolate a new ROC curve between four calibrated points. Reuse the accepted Task0026 ROC/PR figure unchanged when discussing the full curves.

Do not create statistical error bars for AUC/AP or derived enrichment quantities when they were not computed under the accepted protocol.

Visually inspect the figures for readable labels, units, intervals, legends and captions.

## 8. Make derivation reproducible without new scientific execution

The curated summary must identify:

- Task0022 and Task0026 source artifacts and file hashes.
- Candidate scientific/config/calibration identities.
- Accepted versus failed campaign status.
- Scientific and cost scopes.
- Exact formulas and unit conversions used here.
- New population/scoring/custody/optimizer counts: zero.
- Existing test exposure: YES/YES.
- Limitations and unmeasured claims.

A small deterministic offline helper may be added if it improves regeneration and validation. It must read only approved curated aggregates and write derived tables/figures.

Do not change model/evaluation/runtime modules or dependencies.

If new helper code is added, distinguish its validation from historical scientific source acceptance. Preserving the original 130 file bytes does not mean the old acceptance covers new analysis code.

Do not add another execution controller, grant system or resource-recovery framework to this synthesis task.

## 9. Perform proportionate validation

Verify:

- Source statuses and identities.
- Exactly two candidates and the correct ten adapter cost groups.
- Complete four-threshold rows per model.
- Count/denominator arithmetic and fraction/percent conversions.
- Derived acceptance ratios and selected fractions.
- Correct cost aggregation/statistical labels.
- CSV/JSON/report/figure agreement.
- Preservation of prior scientific artifacts and exposure state.
- Relative links, whitespace and Git exclusions.

Small synthetic fixtures are appropriate for any reusable helper’s meaningful failure cases, such as missing rows, incompatible identities or invalid units.

Documentation and deterministic table/figure work do not require rerunning the entire 1259-test suite. Report historical acceptance honestly. Run lint/format and relevant checks for any new code.

No hosted CI success is implied.

## 10. Reconcile current project state

Update README, living memory and the chronological handoff index.

Increment memory from the verified current revision, expected 1.20.

Mark the initial native PCA/AE scientific comparison and its integrated synthesis as completed according to actual outcomes.

Keep open or limited:

- Scientific generalization to other signals/populations.
- Strict-tail utility.
- Feature-level bias diagnostics not measured here.
- Capacity-controlled comparisons.
- MPS physical validation and paired measurement.
- Accepted ONNX performance comparison.
- CoreML, reduced precision and streaming studies.
- Particle canonical training, still deferred with 192/192 consumed.

These extensions are separate research or engineering choices, not automatic prerequisites for reporting the completed initial study.

Future model development informed by these results requires an explicit methodological decision and independent evaluation protocol/population. Do not describe the exposed test as fresh or treat it as a tuning set.

Do not automatically launch a Task0028. Identify one justified follow-up and explain its purpose and required evidence/authorization.

## 11. Deliver an informative Italian final response

Write approximately 600–1000 words excluding Git commands.

Explain:

- What was synthesized and which accepted artifacts supplied it.
- Main scientific findings and the modest AE advantage.
- The strict-tail observation, including comparison with achieved background acceptance.
- Quality/cost tradeoff with correctly labeled CPU statistics.
- Why residual magnitude and unequal capacity limit interpretation.
- What this initial study establishes.
- What remains unmeasured or insufficient.
- Validation, provenance and one concrete next step.

Link the report, curated tables/summary and figures.

Report:

```yaml
test_background model/evaluation accessed: YES
test_signal model/evaluation accessed: YES
new_test_population_requests_in_Task0027: 0
new_model_scoring_in_Task0027: 0
```

Explain that YES records the existing Task0026 exposure, not new access in Task0027.

Optimizer updates remain zero. Particle remains 192/192 consumed and deferred. Task0025 remains failed/consumed with provisional ratios.

Finish with manual Git commands for the actual branch/upstream. List intentional files explicitly, review unstaged/staged changes and whitespace, use an outcome-appropriate Conventional Commit and verified upstream push.

Preserve and distinguish any uncommitted Task0026 continuation, including overlapping documentation changes.

Do not stage, commit or push automatically. Exclude raw data, score/curve arrays, logs, manifests, acceptances and operational receipts.
