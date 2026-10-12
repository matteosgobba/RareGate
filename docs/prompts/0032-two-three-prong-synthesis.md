# LatentTrigger — Task0032: Frozen Two-/Three-Prong Synthesis and Quality/Cost Decision Brief

## Objective

Produce the integrated scientific synthesis of the accepted two-prong and three-prong evaluations, together with the accepted native CPU cost evidence.

Explain what has been established, where utility is limited, and which methodological decisions are necessary before further development.

This is an offline task using curated accepted aggregates, documents and existing figures only. It authorizes implementation of a small reproducible synthesis helper, focused synthetic validation, documentation and static scientific figures.

It authorizes zero population access, numerical score/curve loading, model execution, fitting, recalibration, downloading or new benchmark/evaluation campaigns.

Complete the authorized work without asking for additional general confirmation.

## 1. Inspect the current repository and preserve history

Read applicable instructions, `docs/development.md`, living memory, and the relevant Task0022, Task0026, Task0027 and Task0031 reports, summaries and curated tables.

Verify branch, HEAD, upstream, index and worktree.

The planning chat observed:

- Clean local `main` tracking `origin/main`.
- Latest commit `bf6a5c3`, “complete frozen local three-prong scientific study”.
- Memory revision 1.26.

Reconfirm current state. Preserve unrelated changes if any.

Save this actual prompt and create the initial handoff:

- `docs/prompts/0032-two-three-prong-synthesis.md`
- `docs/handoffs/0032-two-three-prong-synthesis.md`

Keep historical source, reports, summaries, tables, figures and operational evidence unchanged. In particular, do not retrofit Task0027 with the later three-prong results.

Use new Task0032 outputs and a separately named synthesis helper.

## 2. Restrict inputs to accepted curated evidence

Define and record a finite input allowlist with file-byte SHA256 identities.

Use the maintained curated sources needed from:

- Task0026 accepted two-prong evaluation summary, scientific comparison, calibrated and empirical operating-point CSVs.
- Task0031 accepted three-prong summary and corresponding curated CSVs, including its two-versus-three-prong comparison.
- Task0022 accepted CPU benchmark summary and timing-cell CSV.
- Task0027 historical synthesis for context and consistency checks.
- Relevant maintained reports and accepted PNG figures.

Do not follow paths from those summaries into operational namespaces.

Do not open:

- Raw HDF5 payloads.
- Processed or prepared numerical arrays.
- Fingerprint arrays.
- Original or newly generated per-event scores.
- Numerical curve archives.
- Model artifacts for execution.
- Campaign controllers, population readers or acquisition routes.

Compare identities recorded in curated summaries. Do not instantiate candidates or rerun custody.

The helper should have an explicit input boundary, rather than relying solely on a narrative claim of “offline”.

## 3. Validate cross-task compatibility

Before deriving outputs, establish from accepted aggregates that both signal evaluations share:

- The same frozen candidate identities.
- The same feature order, transform/scaler and score definition.
- Native canonical CPU behavior.
- FP64 SSE with casts before subtraction.
- Higher score means more anomalous.
- Strict `score > threshold`.
- The same four original calibrated thresholds.
- The same exposed Task0026 background score reference and population.

Verify accepted campaign statuses and complete candidate/threshold coverage.

Expected scientific coverage:

- Two candidates.
- Two signal topologies.
- Four global-quality rows.
- Sixteen calibrated operating points.
- Eight cross-topology candidate/threshold comparisons.
- Four descriptive FPR targets and three descriptive TPR targets per candidate and topology.

Both evaluated mixtures have 100000 signal and 150471 background events, with prevalence:

`100000 / 250471 = 0.3992478171125599`

Validate counts, rates, intervals, thresholds and JSON/CSV agreement. Reject missing, duplicate, inconsistent or unaccepted inputs rather than filling gaps.

Background accepted counts must agree across topologies:

- PCA: `14922, 7362, 1416, 124`.
- AE: `14793, 7357, 1424, 116`.

These are shared measurements. Do not count them as independent FPR replications.

## 4. Consolidate global quality and calibrated utility

Report original accepted values for:

- ROC-AUC.
- Average Precision.
- Population sizes and evaluated prevalence.
- Every frozen calibrated threshold.
- Background and signal accepted counts.
- Achieved FPR and signal efficiency.
- Existing conditional Wilson intervals and rejection factors.

Preserve the distinction between nominal calibration targets and achieved test FPR.

Use these accepted global values as cross-checks:

| Candidate | Two-prong AUC | Three-prong AUC | Two-prong AP | Three-prong AP |
|---|---:|---:|---:|---:|
| PCA-v1 | 0.4684886579473786 | 0.4629531325637498 | 0.36437915494963025 | 0.36022029761655994 |
| Compact AE v2 | 0.6600638025267328 | 0.5858771149922577 | 0.5474272683246686 | 0.479971651666809 |

Describe observed changes without treating them as statistically established differences or causal topology effects.

PCA remains below 0.5 under its frozen orientation. Do not invert its scores or reinterpret the study as having tested an inverted candidate.

Average Precision depends on the evaluated mixture. Its constant-score reference is that mixture’s signal prevalence, not a physical LHC signal rate.

## 5. Label all newly derived arithmetic honestly

From accepted aggregate counts, derive descriptive quantities where useful:

- Three-prong minus two-prong AUC and AP.
- Signal-efficiency changes in percentage points.
- Three-prong/two-prong efficiency ratios.
- Relative acceptance: TPR divided by achieved FPR.
- Selected signal fraction.
- Whether observed selection enriches the evaluated mixture.

Identify Task0032 calculations as post-evaluation descriptive arithmetic. Do not falsely label them as preregistered Task0026 metrics.

Use null for undefined ratios. Keep counts beside rates and ratios.

Avoid multiplicative headlines based on PCA’s one or two accepted strict-tail signal events.

The strict-tail checks must reproduce:

- Two-prong AE: 56 signal, 116 background; selected signal fraction `56/172`.
- Three-prong AE: 34 signal, 116 background; selected signal fraction `34/150`.
- Initial evaluated signal fraction: `100000/250471`.

Both strict-tail selected fractions are below the initial mixture prevalence.

The first three AE calibrated points show descriptive enrichment for both topologies. Preserve all four points; do not select a winning threshold.

Copy accepted Wilson intervals without inventing intervals for ratios, differences, AUC or AP. Do not add hypothesis tests, significance scans, subgroup analyses or optimal cuts.

## 6. Integrate CPU cost with precise scope

Use accepted Task0022 native CPU results only.

Preserve its original statistical definitions and units, including:

- Five batches: 1, 8, 32, 128 and 1024.
- Three workers per model.
- Ten candidate/batch adapter cost groups.
- Original latency summaries and pooled throughput definitions.
- Material variability and outliers already recorded.

Cross-check the B1 adapter median of the three worker p50 values:

- PCA: 8.125 microseconds.
- AE: 24.708 microseconds.

Clearly distinguish:

- Historical cost measured on preloaded prepared development features.
- Scientific quality evaluated canonically at batch 4096.
- Raw loading, preprocessing, transport, supervision and reporting.
- Physical event-arrival rates and actual trigger constraints.

If joining quality with each historical cost batch, include explicit fields for `quality_reference_batch=4096` and the actual cost batch. Repeated quality values in those rows are references to one accepted measurement, not quality independently measured at every batch.

Do not calculate AUC/latency “utility scores”, combine heterogeneous scopes into one ranking, or infer a deployment optimum.

Task0025 speed ratios remain provisional and unaccepted. Task0030 transfer duration and Task0031 campaign duration are not inference benchmarks.

## 7. Create readable static scientific figures

Use standard plotting tools and only accepted aggregates.

Produce up to three useful new figures, for example:

1. Paired AUC/AP comparison across candidates and topologies.
2. Signal efficiencies at all four frozen thresholds for both topologies.
3. A clearly scoped quality/cost comparison using an explicitly identified historical adapter batch.

Include denominators, units, topology labels and the shared-background caveat.

For calibrated operating-point plots:

- Use achieved FPR when it is the horizontal variable.
- Label any connecting lines as visual guides between calibrated points.
- Do not present four points as a reconstructed full ROC.
- Show strict-tail counts in accompanying tables.
- Explain logarithmic axes if used.

Reuse or link the accepted full ROC/PR PNGs unchanged. Do not reopen numerical curves or regenerate full curves from per-event arrays.

Visually inspect the generated figures for labels, clipping, legends, units and misleading scales.

## 8. Write the integrated scientific report

Create:

`docs/two-three-prong-synthesis.md`

The report should explain the research question, evidence, results and limits in connected prose, with tables where comparisons are easier to assess.

State the supported conclusion:

The frozen AE has higher observed ranking and signal acceptance than the frozen PCA on both declared signals, at higher scoped native CPU cost. Its advantage and absolute signal efficiency are weaker on the three-prong sample. Strict-tail utility is weak for both signals.

Keep these limits visible:

- Background is shared, previously exposed evidence.
- Exact fingerprint disjointness does not prove full statistical or simulation independence.
- Preselected simulated populations do not establish physical LHC rates or trigger performance.
- Six PCA dimensions versus three AE latent dimensions do not isolate nonlinearity.
- Residual magnitudes do not directly rank discrimination.
- Conditional rate intervals exclude calibration, model and simulation uncertainty.
- No significance result or mechanism explaining the topology difference was established.
- All evaluated signal/background samples retain their exposure status.

Distinguish hypotheses about representation, bottleneck capacity or score tails from measured explanations. No feature-level diagnostic was performed in this task.

Include a short plain-language explanation of what the study has achieved and what remains open.

## 9. Produce a concrete methodological decision brief

Finish the report with a concise decision matrix separating:

- Closing and preserving the current frozen baseline study.
- An explicitly exploratory diagnostic of the exposed samples.
- New model/representation development.
- Independent background or signal generalization.
- End-to-end deployment and hardware validation.

For each plausible extension, state:

- The question it would answer.
- What current evidence supports.
- Necessary new data or authorization.
- Evaluation-independence requirements.
- Compute/runtime prerequisites.
- The acceptance criterion that must be defined prospectively.

Exposed samples may inform an explicitly declared exploratory analysis. They cannot become untouched confirmation samples again.

Any new development informed by these outcomes must disclose that influence and define independent evaluation before confirmation. Do not propose reshuffling the same exposed samples as a way to obtain a fresh test.

Particle execution remains deferred with 192/192 consumed disposable updates. A future particle study needs a new feasibility/budget decision, not an assumed reset.

Recommend the next decision without silently launching another experiment or claiming that further model development is already authorized.

Mark the frozen two-/three-prong baseline study as completed within its declared scope. Keep broader scientific generalization and physical deployment objectives open.

## 10. Reproducible helper and proportionate validation

Suggested helper:

`scripts/synthesize_signal_topologies.py`

Keep it small and separate from the historical Task0027 helper. It should read only pinned curated inputs and produce only Task0032 outputs.

Add focused synthetic tests where needed for:

- Accepted-status and identity compatibility.
- Complete candidate/topology/threshold coverage.
- Shared-background consistency.
- Counts, fractions, percentage-point changes and undefined ratios.
- Correct quality/cost scope fields.
- Input-boundary enforcement.
- Missing, altered or inconsistent sources.
- Preservation of original thresholds and historical files.

Run checks appropriate to this helper and required repository checks. Do not rerun operational campaigns or claim historical test counts as fresh validation.

A complete regression-suite rerun is not required merely for documentation and aggregate synthesis unless repository rules or an actual implementation concern justify it. State exactly what ran.

Verify output JSON/CSV agreement, arithmetic, source/output hashes, relative links, figure rendering, exclusions and whitespace.

Dependencies and historical source files remain unchanged.

## 11. Deliverables and final response

Produce:

- Task0032 prompt and handoff.
- `docs/two-three-prong-synthesis.md`
- The separate synthesis helper and focused tests, if implemented.
- `results/tables/final/task0032-two-three-prong-synthesis-summary.json`
- Integrated global-quality table.
- Sixteen-point calibrated-utility table.
- Eight-row cross-topology descriptive comparison.
- Scoped quality/cost table.
- The new scientific figures.

Record source file-byte hashes separately from scientific identities. Keep a clear provenance chain to accepted Task0022, Task0026 and Task0031 evidence.

Update README, handoff index and living memory from the verified current revision. Preserve historical documents.

The final Italian response should be approximately 600–1000 words excluding Git. Explain:

- What was consolidated and generated.
- The main quality and threshold findings.
- Descriptive topology changes.
- CPU cost and its precise boundaries.
- Scientific limitations and open objectives.
- Validation actually performed.
- The recommended methodological decision.

State:

original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
new_population_accesses_in_Task0032: 0
new_score_or_curve_array_loads_in_Task0032: 0
new_model_scoring_in_Task0032: 0
new_fingerprint_numeric_loads_in_Task0032: 0
optimizer_updates_in_Task0032: 0
downloads_in_Task0032: 0

The YES values preserve historical exposure; they do not mean new accesses occurred here.

Do not launch Task0033 automatically.

Finish with manual Git review, selective staging, Conventional Commit and push commands for the verified actual branch/upstream. Do not stage, commit or push.
