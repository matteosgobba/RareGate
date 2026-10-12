# LatentTrigger — Task0033: Exploratory Frozen-Feature and Score-Tail Diagnostics

## Objective and authorization

Investigate the exposed baseline samples through a bounded descriptive analysis of existing frozen model-input features and accepted score arrays.

The purpose is to identify observable associations that may help formulate future hypotheses about weak strict-tail utility and the two-/three-prong performance difference.

This prompt explicitly authorizes, after successful software validation and plan freezing:

- Read-only numerical access to the specified existing feature and membership arrays.
- Read-only numerical loading of six accepted score arrays.
- Fixed descriptive feature/score summaries, associations and original-threshold tail diagnostics.
- One bounded diagnostic session and its aggregate reporting.

It authorizes zero model forwards, reconstruction recomputation, fitting, optimizer updates, recalibration, score inversion, candidate/threshold selection, downloads or independent confirmatory evaluation.

Complete implementation, validation and the one conditional diagnostic session without requesting another general confirmation. Record this actual prompt as prospective authorization bound to the finalized source, acceptance and plan.

All samples are already exposed. These diagnostics are exploratory and result-informed. They must not be presented as untouched confirmation or as proof of a causal mechanism.

## 1. Inspect and preserve the completed baseline

Read applicable instructions, `docs/development.md`, living memory, Task0032’s decision brief and relevant Task0026/Task0031 provenance.

Verify Git state. The planning chat observed:

- Clean local `main` tracking `origin/main`.
- Latest commit `a671b98`.
- Memory revision 1.27.

Reconfirm actual state and preserve unrelated changes.

Save this prompt and create the initial handoff:

- `docs/prompts/0033-exploratory-feature-score-diagnostics.md`
- `docs/handoffs/0033-exploratory-feature-score-diagnostics.md`

Preserve completed scientific reports, accepted arrays, source, parameters, transformations, thresholds and historical outcomes.

Task0032 remains the completed frozen baseline synthesis. Task0033 adds exploratory evidence; it does not replace or reopen consumed evaluation campaigns.

## 2. Define a narrow input boundary

Use three populations:

1. Original test background: 150471 events.
2. Original two-prong test signal: 100000 events.
3. Accepted three-prong signal: 100000 events.

### Original feature and membership files

Under:

`data/processed/lhco-rd-v1/schema-v1/full/`

Allow:

- `manifest.json`
- `configuration.json`
- `event_features.npy`
- `split_codes.npy`
- `event_ids.npy`
- `labels.npy`

Verify the manifest scientific identity and each required file’s recorded size, dtype, shape and SHA256.

Original feature-array identity:

- Shape `[1100000,8]`, dtype `<f4`.
- Size `35200128` bytes.
- SHA256 `213d94d939141a7c0c8eb48641a3f6ecb185b9346d5f9cf2c2bedb15cab53015`

Determine original test memberships from frozen split codes:

- Code 4: test background.
- Code 5: test signal.

Validate counts, labels and source ordering against accepted provenance. Select test positions before accessing feature values. Do not numerically analyze training, selection or calibration features.

Whole-file hashing is byte custody; distinguish it from numerical population access.

Avoid `ProcessedStore` or another broad validator if its construction opens/scans particles, fingerprints or unrelated populations. Implement a narrow manifest-bound adapter and test its scope.

### Three-prong features

Use:

`data/task0031-three-prong/prepared/event_features.npy`

- Shape `[100000,8]`, dtype `<f4`.
- SHA256 `3059ff96b75268839d6e55e8aca1bb3fe019dab3cb19d4cbbb1dabe9cafb7f93`

Bind its prepared manifest, scientific identity and accepted Task0031 preparation lineage. Preserve the complete accepted source order.

Do not load the three-prong fingerprint array.

### Accepted score arrays

Use only:

- Task0026 PCA `test_background-scores.npy`
- Task0026 PCA `test_signal-scores.npy`
- Task0026 AE `test_background-scores.npy`
- Task0026 AE `test_signal-scores.npy`
- Task0031 PCA `three-prong-scores.npy`
- Task0031 AE `three-prong-scores.npy`

Their directories are:

`results/evaluation/task0026-frozen-pca-ae/final/{PCA,AE}/`

and:

`results/evaluation/task0031-three-prong/{PCA,AE}/`

Pin their hashes from accepted parent/receipt lineage. Cross-check:

| Array | SHA256 |
|---|---|
| PCA background | `7e8762a1b675c637ed1533eab1b96686bc7ffd364666aea022a0f6e48766987d` |
| PCA two-prong | `93917e81ec79b489594899f8fcf5a00b60f3a84d17d550d6e31a9d8130249712` |
| AE background | `65711ecda105801c07855d9f6d8e4d5fa9264daac993b8ed10e362166c5efee3` |
| AE two-prong | `a2bc271d313d818ef82e596c115cfad8864c4a27892ea09595602e76828873a7` |
| PCA three-prong | `5b818a3a0157a1752b0a3194b25f6392e55e7785e4b04341733cc87fc3fa6148` |
| AE three-prong | `5f8d58a5e8aa15c337f9e5a0314bcb829ed9244617b8a82e4922119dcf63dff2` |

Note that Task0026 receipts use basename output keys, while later receipts may use repository-relative paths. Resolve keys explicitly; do not treat a missing lookup as an absent identity.

Require finite, nonnegative FP64 scores and exact population lengths.

Reject missing, altered, symlinked or ambiguous sources before numerical analysis. Do not regenerate missing arrays.

## 3. Verify row alignment

Establish that accepted score order matches the corresponding feature order:

- Original role-selected rows retain the accepted ascending source order.
- Source IDs and labels agree with frozen membership.
- Task0026 evaluation/ledger provenance agrees with the original store identity.
- Three-prong features and scores share the accepted prepared identity and complete source order.

Length equality alone is insufficient.

If alignment cannot be established from existing accepted artifacts and fixed membership, stop before diagnostic computation. Do not rerun scoring to manufacture alignment evidence.

## 4. Fix the exploratory questions before execution

Answer only these questions:

1. How do the eight frozen input-feature distributions differ between background, two-prong and three-prong samples?
2. How do accepted score distributions differ within each candidate?
3. Which input features are monotonically associated with each candidate’s existing scores within each population?
4. What feature profiles occur in the slices selected by the four original calibrated thresholds?

These are descriptive associations. They do not isolate a feature’s causal effect, attribute reconstruction-error channels, or establish why a model behaves as observed.

Do not introduce feature ablations, perturbations, alternative anomaly scores, clustering, subgroup searches or new operating thresholds.

Ambiguous or uninformative findings are valid outcomes.

## 5. Preregister the descriptive computations

### Feature marginals

For each population and each of eight features, report:

- Count.
- Mean and population standard deviation.
- Minimum and maximum.
- Linear quantiles at probabilities:
  `0.001, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 0.999`.

Expected coverage: 24 population/feature rows.

Use existing frozen standardized FP32 inputs, with FP64 accumulation for descriptions. Do not restandardize, refit transformations or reconstruct physical quantities by approximately inverting rounded features.

Label axes and tables as frozen standardized inputs. Log-transformed channels must be identified; do not label standardized values as GeV or radians.

### Score marginals

Use the same descriptive statistics for six candidate/population combinations.

Cross-check overlapping statistics against accepted historical summaries. Do not rank discrimination by comparing the absolute score magnitude of PCA with AE.

Do not recompute AUC/AP or full ROC/PR curves.

### Feature–score associations

Compute one Spearman coefficient per candidate/population/feature:

- Two candidates × three populations × eight features = 48 rows.
- Average ranks for ties.
- Finite inputs only.
- Null with an explicit reason for constant or otherwise undefined variables.

Use ranks and correlation arithmetic without calculating p-values or hypothesis-test results. Do not invoke a statistical API that computes significance and then merely hides it.

Reuse ranked features within the worker. Associations are not feature importance or residual attribution.

### Original-threshold tail profiles

Apply only the four existing thresholds per candidate, with strict `score > threshold`.

Expected coverage:

- 24 candidate/population/threshold count rows.
- 192 corresponding feature-profile rows.

For every slice, report the denominator, accepted count and fraction. Verify exact agreement with Task0032’s accepted counts.

For slices with at least 20 events, report each feature’s mean, median, p25 and p75.

For fewer than 20 events, retain counts but suppress per-feature summaries with reason `small_tail_descriptive_summary_suppressed`. Do not publish singleton-event feature values or build comparisons around them.

This rule is a Task0033 descriptive reporting convention, not a statistical confidence guarantee.

No threshold searches, significance calculations, confidence intervals for associations or new tail-optimization criteria.

## 6. Load each population and score array once

Expected logical numerical access:

- Three feature-population requests.
- 350471 feature rows in total.
- Six accepted score-array loads.
- 700942 score values in total.
- Zero model forwards.

Read original membership metadata separately and account for it explicitly. Do not hide full membership scans inside feature counts.

Load each population’s features once and reuse them for both candidates and all descriptive calculations. Load each score array once.

The plotting worker should consume owned aggregate tables only, without reopening population or score arrays.

Distinguish file hashing, array headers, membership metadata, feature rows, scores and repeated in-memory calculations in the access ledger.

## 7. Bounded implementation and execution

Suggested protocol:

`configs/diagnostics/exposed_feature_score_v1.json`

Distinct operational namespace:

`results/diagnostics/task0033-exposed-feature-score/`

Use separate preparation/analysis/reporting helpers as needed. Do not modify historical controllers or analytical helpers.

Prefer one numerical analysis worker followed by one aggregate-only plotting/reporting worker.

Use Task0030 continuous-clock and scoped idle-system-sleep assertion mechanisms where appropriate. Inspect reused helpers for hard-coded paths and clock assumptions.

Fixed continuous limits:

| Scope | Maximum |
|---|---:|
| Prerequisites before reservation | 60 s |
| Numerical analysis worker | 120 s |
| Aggregate figures/reporting worker | 60 s |
| Parent finalization | 15 s |
| Reserved session | 240 s |
| Cleanup inside each worker ceiling | 2 s |
| Worker RSS | 1 GiB |
| Native reservation | 512 MiB |
| Controller RSS | 128 MiB |
| Guard journal per worker | 64 MiB |

Enforce the narrower Task0033 RSS ceiling explicitly; do not assume a reused guard’s historical 6 GiB limit implements it.

Retain WARN advisory, CRITICAL veto, invalid-primary-accounting veto and disclosed unavailable pressure. Global available RAM is contextual.

Define storage, log and access-journal bounds before execution. Do not copy entire source stores or create per-event diagnostic exports.

Establish and verify the temporary sleep assertion, permit display sleep and confirm release. No persistent power-setting changes.

Accept workers only after normal exit, reaping, source/output identity checks and continuous deadline/resource checks. Disclose monitoring gaps and overshoot.

One reserved diagnostic session only. On failure, preserve partial artifacts and stop without retry, reset, broader access or implementation changes.

## 8. Validate before operational numerical access

Use synthetic feature, membership and score fixtures.

Cover:

- Input allowlist and narrow-reader behavior.
- Wrong roles, labels, counts, ordering or lineage.
- Same-length but misaligned arrays.
- Altered files and ambiguous receipt keys.
- Complete finite inputs and score constraints.
- Exact strict-threshold decisions and ties.
- Quantile conventions and population standard deviation.
- Spearman ties, constant inputs and absence of significance computation.
- Small-tail suppression.
- Single numerical load per allowed array/population.
- Reporting from aggregate outputs only.
- Deadline advancement through simulated suspension.
- Assertion failure/loss/release.
- Body-complete versus parent-accepted lifecycle.
- Preservation of all historical inputs.

Run appropriate full and portable checks because this adds an operational numerical reader and guarded workers. Include lint, formatting, dependencies and bounded native synthetic integration.

Use a fresh current-source acceptance; historical scientific and Task0032 helper tests do not cover new diagnostic code.

Freeze the protocol, source/dependency map, input identities and execution plan after validation. Bind this actual prompt as prospective authorization.

Then execute the one authorized session. No further general confirmation is required.

Do not instantiate operational candidates, access numerical samples during synthetic validation, or change the frozen plan after reservation.

## 9. Aggregate outputs and scientific interpretation

Produce:

- `docs/exploratory-feature-score-diagnostics.md`
- Task0033 prompt and handoff.
- A curated Task0033 summary with provenance, access, lifecycle and limits.
- Feature marginal table.
- Score marginal table.
- Feature–score association table.
- Frozen-threshold tail-count table.
- Tail-feature profile table.

Use standard scientific plotting tools. Limit new figures to a few readable views, such as:

- Population feature medians/IQRs.
- Candidate-specific score quantile profiles with original thresholds.
- Feature–score association heatmaps.

Show counts, standardized units, topology and candidate labels. Explain any display clipping or log axes. Do not imply full distributions from a few quantiles.

Visually inspect all figures.

The report must separate:

- Observed descriptions.
- Plausible interpretations.
- Unresolved mechanisms.
- Future hypotheses requiring independent confirmation.

Do not claim that correlations explain causally the topology difference, that a favorable feature should now be selected, or that weak tails have been repaired.

End with a short hypothesis/decision table: observation, possible interpretation, alternative explanation, and a future test that would distinguish them. Do not launch that test.

## 10. Detailed final handoff

Update README, chronological index and living memory from the verified current revision.

Preserve the completed baseline and permanent exposure status. These samples cannot be reblinded. Any subsequent result-informed development must disclose its exploratory basis and define independent confirmation.

The final Italian response should be approximately 600–1000 words excluding Git. Explain:

- Questions addressed and actual outcome.
- Allowed inputs and alignment evidence.
- Actual feature/score/membership accesses.
- Main marginal, association and tail observations.
- Small-tail suppressions and ambiguous findings.
- What remains a hypothesis.
- Validation, continuous durations, resources and assertion release.
- A concrete supported next decision.

State actual counts, including:

original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
exploratory_diagnostic_session: ACTUAL_STATUS
feature_population_requests: ACTUAL_COUNT
feature_rows_read: ACTUAL_COUNT
stored_score_array_loads: ACTUAL_COUNT
stored_score_values_read: ACTUAL_COUNT
new_model_forward_calls: 0
new_reconstruction_computations: 0
new_AUC_AP_or_significance_computations: 0
new_fingerprint_numeric_loads: 0
optimizer_updates: 0
downloads: 0

Do not claim zero numerical access: this task explicitly authorizes new diagnostic reads of exposed samples.

Keep per-event arrays, membership extracts, logs, ledgers, receipts, acceptances and operational artifacts excluded from Git. Commit only intentionally curated aggregates and figures through manual commands.

Finish with Git review, selective staging, Conventional Commit and push commands for the verified actual branch/upstream. Do not stage, commit or push. Do not launch Task0034 automatically.
