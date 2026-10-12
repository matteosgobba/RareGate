# LatentTrigger — Task0034: Controlled Follow-up Design and Independent-Confirmation Protocol

You are continuing **LatentTrigger**. Perform **Task0034 only**.

## Objective and authorization

Turn Task0033's exploratory observations into one concrete, bounded follow-up design. Specify the controlled model comparison, the independent data needed to evaluate it, the prospective analysis, and a feasible implementation brief.

This task authorizes documentation, primary-source metadata research, inspection of existing small curated artifacts and configuration/source text, and synthetic-only planning calculations or checks when useful. Complete that work without requesting another general confirmation.

It authorizes **zero operational numerical population access, stored score-array loads, model instantiation/forwards, reconstruction, fitting, calibration, acquisition of event payloads, fingerprint-array loads, or scientific evaluation**. The future experiment described below is a design requirement, not a granted execution budget.

Task0032 remains the completed frozen baseline. Task0033 remains accepted, exploratory, and result-informed. Preserve their outcomes and permanent exposure. Do not launch Task0035.

## 1. Reconcile the actual state

Read applicable instructions, `docs/development.md`, living memory, Task0032's decision brief, Task0033's report/handoff/curated summary, and the relevant original preprocessing, evaluation, compact-AE training and particle-deferral contracts.

The planning chat verified on 2026-10-12, Europe/Rome:

- Clean local `main` tracking `origin/main`, with empty index.
- HEAD `c9f9bc5317f575ff2e29566214db20609745fcc1`: committed Task0033.
- Living-memory revision 1.28.
- All three evaluated populations permanently exposed.

Recheck those facts. Preserve unrelated changes. Record the actual prompt and an initial handoff before substantive work:

- `docs/prompts/0034-controlled-follow-up-protocol.md`
- `docs/handoffs/0034-controlled-follow-up-protocol.md`

The memory's recorded Task0033 base `a671b98` is historical task-time information. Reconcile the later commit in the new handoff rather than silently rewriting historical records.

Do not rerun accepted or failed campaigns, reset allowances, regenerate missing historical artifacts, change historical model/calibration/source identities, or edit synced `sources/` material. Particle characterization remains 192/192 consumed and canonical training deferred. Task0025's failed process-exit supervision remains a failed performance campaign.

## 2. Convert evidence into one testable question

Use existing curated aggregates to document the motivation:

- PCA and AE currently have unequal latent dimensions: six versus three.
- AE signal medians exceed background, but background p99.9 exceeds both signal p99.9 values.
- At the strictest original thresholds, AE accepts 116/150471 background, 56/100000 two-prong, and 34/100000 three-prong events.
- Signed eta associations coexist with centered eta marginals; these do not establish a symmetry defect or causal mechanism.

Do not recompute these quantities or promote correlations to feature importance.

The primary future question is:

> Under a fixed background-only training procedure, how does replacing the two ReLU activations with identity activations change independently measured strict-tail signal acceptance and background acceptance, at the same input representation, bottleneck dimension, layer structure and parameter count?

The task must produce a usable protocol even if the answer will be negative or inconclusive. It must not promise that removing activations, increasing capacity, or changing representation will repair the tails.

Treat signed-eta symmetry, residual attribution and richer particle representations as deferred hypotheses. Do not add ablations, feature removal, perturbations, extra anomaly scores, subgroup searches or architectures to this first comparison.

## 3. Specify the minimal controlled comparison

Design two future arms:

| Arm | Structure | Activations | Bottleneck | Parameters |
| --- | --- | --- | ---: | ---: |
| Nonlinear aggregate AE | 8 → 6 → 3 → 6 → 8 | ReLU at the two existing hidden locations | 3 | 155 |
| Linear aggregate AE | 8 → 6 → 3 → 6 → 8 | Identity at those same locations | 3 | 155 |

Retain biased layers, linear latent/output layers, the eight frozen standardized FP32 inputs, equal event weights, the reconstruction objective, and the finite nonnegative FP64 SSE score with higher meaning more anomalous. Do not refit scalers or approximately invert rounded inputs.

Use three prespecified paired seeds, `1729`, `1730`, `1731`, for at most six future fits. Pair initial parameter tensors and training-row permutations within each seed; record the implementation requirements for reproducible pairing. Use the existing background-only optimizer, batch and early-stopping recipe as the starting contract, verifying its exact configuration rather than copying rounded historical descriptions. Both arms use the same selection rule and restore their own selected state. Different stopping epochs are permitted outcomes of that fixed procedure.

All prespecified seeds and both arms must be reported. Do not select the best seed, average model weights, create an ensemble score, or use signal results to choose a checkpoint. These six fits are proposed future scope, not authorization to run them now.

The historical AE v2 and PCA-six remain frozen reference models. Specify an optional fixed PCA-three diagnostic control based on the leading three accepted training components if the existing artifact supports this unambiguously. Otherwise describe its prerequisites; do not inspect numerical component arrays or refit PCA here. PCA-three versus PCA-six addresses rank/compression under the linear model; neither is a parameter-matched substitute for the two-arm comparison.

Be precise about interpretation: equal bottleneck and parameter counts control specific differences, not all notions of expressivity. The activation contrast includes its interaction with optimization and background-only checkpoint selection. It does not isolate a causal physics mechanism, prove global optimization of the linear AE, or establish whether eight aggregates lose useful particle information.

## 4. Establish an independent-confirmation data route

Research only primary publisher metadata, papers and text generation/detector cards. Do not fetch event files, answer-key rows, feature matrices, binary archives or per-event examples. Record URLs, retrieval dates, verified facts, and unavailable metadata. Keep the source shortlist small.

Start with these leads; verify them rather than treating their inclusion as source acceptance:

1. [Official LHCO black-box/background record](https://zenodo.org/records/4536624). Its separately supplied background and labeled black-box options require assessment of simulation differences, signal definitions and achievable tail resolution. Public keys cannot support a claim of original challenge blindness.
2. [Extra LHCO background lead](https://zenodo.org/records/8370758). The [additional-signal publisher](https://zenodo.org/records/18983506) links this record as extra background. The planning chat could not inspect its own record because the web request returned HTTP429; exact file metadata and selection coverage remain unverified.
3. [Additional Signal Models for LHCO2020 R&D](https://zenodo.org/records/18983506). Distinguish its newly generated signal samples from its derived features for existing R&D events. Its generation chain differs from the original release; a similarly named topology does not establish a controlled replication of the original two-/three-prong contrast.

For each plausible route record:

- Version DOI/record, publisher, license, exact proposed files, available sizes/checksums and generation lineage.
- Coordinates, units, labels, layout, padding, full-event versus selected-jet constituent coverage, and compatibility with the frozen eight-feature construction.
- Generator/detector configuration, process/mass/decay definitions, preselection and any restricted phase-space coverage.
- Declared population counts and evidence for separate generation; unknowns stay unknown.
- Prior project exposure and possible overlap with every original training, selection, calibration and evaluated population.
- Storage, acquisition and preparation implications for the shared 16GiB Mac.

A new filename, DOI, feature representation, exact-content disjointness, or reshuffle alone does not establish independent generation. Existing R&D feature files remain the same exposed events. Fresh background paired with old exposed signals supports new background-rate evidence, not an independent signal comparison.

Define the future duplicate/overlap audit and identity requirements without opening raw events or fingerprints. Separate event disjointness, independent generation and transport to another simulated domain.

Recommend one route based on scientific compatibility and feasibility, never its published model performance. Distinguish three possible claims: fresh-background stability, independent discrimination on new signals, and replication of the original topology difference. Do not assert the third without an appropriate matched independent signal pair.

If available public metadata cannot establish a suitable route, deliver the complete conditional protocol with exact missing prerequisites. Do not invent an accepted source or begin an event generator. Specify whether the next useful task can implement synthetic/background-only software while confirmation remains pending.

## 5. Separate development, calibration and confirmation

Specify a prospective research sidecar rather than mutating evaluation-v1 or the original preprocessing/model JSONs.

The original 699957 training-background and 74749 selection-background roles may be proposed for future background-only fitting and checkpoint selection. The 74823 calibration-background role may be proposed for one calibration per frozen new model. Their use is not authorized in Task0034, and no confirmation signal may enter any of these decisions.

Historical candidates keep their historical thresholds. Every new frozen arm/seed gets its own background-calibrated thresholds using the established `higher` quantile and strict `score > threshold`; applying old AE thresholds to a new model is not valid calibration. No confirmation-background threshold adjustment is permitted.

Define embargoed confirmation membership, transformations and source acceptance before numerical preparation; freeze candidate checkpoints and thresholds before any confirmation scoring. If a route requires separate domain calibration, make that an explicit, disjoint prospective role and change the stated estimand accordingly.

Keep exposed samples as historical exploratory context. This first follow-up protocol must not use them for signal-guided model selection or repeat evaluation merely to show improvement. Design choices are openly motivated by Task0026/0031/0033 results; independent confirmation does not erase that history.

## 6. Preregister outcomes, uncertainty and sample sufficiency

Use calibration target `alpha=0.001` as the primary operating point because strict-tail weakness motivates this study. Retain `0.01`, `0.05`, `0.1` as secondary reported points, with no post-result choice of the most favorable threshold.

Specify primary estimands for each eligible independent signal population: the paired nonlinear-minus-linear TPR contrast at each model's own frozen primary threshold, together with realized confirmation-background FPR. Define the equal-weight summary across the three fixed seed pairs and retain all seed-specific results. Repeated predictions on the same events do not triple the independent sample size.

Define the prospective uncertainty method for paired acceptance differences, dependence across seeds/models on shared events, and the separate conditional rate intervals. Distinguish uncertainty conditional on frozen models/thresholds from calibration, training and simulation uncertainty. Do not infer improvement from overlapping/nonoverlapping individual Wilson intervals alone. Statistical-method development is a design/synthetic task here, not permission for operational resampling or significance computation.

Set explicit, justified numerical decision criteria before future execution: background-rate tolerance, practically relevant signal-acceptance difference, interval precision and treatment of inconclusive outcomes. Distinguish descriptive evidence from a confirmatory improvement claim. If several signals or contrasts are confirmatory, address multiplicity or reduce the primary claim; reporting all results is mandatory.

Use declared source counts and synthetic/binomial planning arithmetic to assess whether the strict tail has useful resolution. `N*alpha` is a planning expectation, not an observed accepted count. Do not assume signal acceptance equals alpha or use historical TPR as a guaranteed future yield. Show sensitivity to plausible rates; record insufficient sample size honestly. No tail extrapolation, discovery significance, physical trigger rate or deployment purity claim.

## 7. Produce a feasible future execution brief

Specify the smallest implementation task that realizes this design. Include fixed phase order, role allowlists, maximum candidate/seed counts, per-phase access accounting, checkpoint restoration, current-source synthetic acceptance, freeze/authorization points, durable attempt state, normal exit/reaping and parent acceptance.

Derive numeric process/storage/time ceilings from relevant existing aggregate-training evidence. Distinguish measurements from projections and unavailable evidence. A short synthetic implementation task can be ready while a training or confirmation campaign is not. Do not reuse Task0033's diagnostic timing as a training-time estimate or the particle-dev budget as an aggregate-training allowance.

Carry forward continuous-clock deadlines, temporary verified idle-sleep assertions for future bounded campaigns, display-sleep permission, process-specific resource ceilings, WARN advisory/CRITICAL veto, invalid-primary-accounting veto, disclosed unavailable pressure and explicit assertion release. Global available RAM remains context; no idle-Mac window, app closure, repeated readiness polling or monitor-optimization project.

Keep acquisition, background development and independent confirmation as distinct authorization scopes. An unready confirmation source must not silently authorize another data campaign. Avoid copying whole processed stores, broad reader construction, new dependencies, controllers or infrastructure in this design task.

## 8. Deliver and validate the design

Create:

- `docs/controlled-follow-up-protocol.md`
- `configs/research/controlled_follow_up_v1.json`
- `results/tables/final/task0034-confirmation-source-registry.csv`
- `results/tables/final/task0034-controlled-follow-up-summary.json`
- Task0034 prompt and handoff.

The sidecar must clearly be `design_only`, not an execution plan, source acceptance, model freeze or authorization token. Include provenance of motivating aggregates, hypotheses, controlled/deferred factors, arms/seeds, populations, proposed metrics/criteria, source unknowns, resource assumptions and separate readiness states for implementation, training, and confirmation.

Use JSON/link/coverage/consistency checks and targeted synthetic calculations where necessary. No full operational suite rerun is required for documentation alone. If adding a small planning helper, test its meaningful behavior with synthetic inputs, enforce its input boundary and run the relevant lint/format checks. Do not claim Task0033's 1728-test acceptance covers new code. No scientific plots, heatmap repairs or operational-array reads are needed here.

Update README, chronological index and living memory from the verified revision. Explain the selected controlled question, independent-source feasibility and concrete next implementation step without launching it.

The final Italian handoff should explain the evidence, what the comparison controls and leaves unresolved, source suitability, planned decision criteria/sample resolution, readiness/blockers and a concrete Task0035 brief. Include actual counters:

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
new_operational_population_requests_in_Task0034: 0
new_feature_rows_read_in_Task0034: 0
new_stored_score_array_loads_in_Task0034: 0
new_membership_or_fingerprint_numeric_loads_in_Task0034: 0
new_model_forward_calls_in_Task0034: 0
new_reconstruction_computations_in_Task0034: 0
new_calibration_or_scientific_evaluations_in_Task0034: 0
optimizer_updates_in_Task0034: 0
event_payload_downloads_in_Task0034: 0
```

YES preserves historical exposure. Disclose actual metadata requests and any synthetic calculations separately; they are not event-payload downloads or scientific measurements.

Finish with exact Git review, selective staging, staged review, Conventional Commit and push commands for the verified branch/upstream. Do not stage, commit or push. Curate only the intended design artifacts and any justified small helper/tests; preserve operational arrays, receipts, ledgers, acceptances and historical reports.

Proceed with **Task0034 only**.
