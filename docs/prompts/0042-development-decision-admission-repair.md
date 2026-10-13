# LatentTrigger — Task0042: Synthetic Acceptance and Launch-Admission Repair

You are continuing **LatentTrigger**. Perform **Task0042 only**.

## Objective and authorization

Repair the software contract between the raw-to-decision validation producer and controller admission consumer, and make failed admission/freezing stop the launch path programmatically. Validate the complete emitted-record → admission → synthetic freeze → synthetic dispatch sequence.

This prompt authorizes versioned software repairs, generated-fixture tests and bounded native synthetic integration. **Task0042 is software-only. It authorizes no operational raw-to-decision attempt**, including no real prerequisite invocation, raw hash, HDF metadata opening, operational membership/golden load, real feature construction, frozen operational model instantiation or actual service timing.

Task0041 remains `failed_prerequisites_no_retry`, consumed, with zero operational numerical work. Its validation checks passed, but its issued record was not controller-admissible. Preserve that distinction. A repaired source and successful synthetic admission do not renew its allowance or grant a replacement campaign. Do not launch Task0043.

## 1. Verify current state and preserve the original failure

Read applicable instructions, `docs/development.md`, living memory, Task0041's actual prompt/config/report/summary/handoff, validation driver, admission protocol, native controller and related tests. Inspect the actual validation/diagnosis/workflow/prerequisite-marker metadata and relevant Task0038/0040 contracts; do not load event/model numerical sources.

Final planning inspection on 2026-10-13 Europe/Rome found clean `main` tracking `origin/main`, HEAD `a7ee0a23f92003a430a2570a233d08042f986e71`, empty index and committed Task0041; memory 1.36. Earlier planning found its 21 paths uncommitted at `8b6310d...`; that remains Task0041's historical base. Recheck actual Git and preserve unrelated work and historical base descriptions.

Save the actual prompt and initial handoff before substantive repair:

- `docs/prompts/0042-development-decision-admission-repair.md`
- `docs/handoffs/0042-development-decision-admission-repair.md`

Before editing affected live files, preserve a reproducible ignored snapshot/manifest of their original bytes, the complete issued Task0041 source map, and the original failure evidence. Resolve every original source-map entry against preserved bytes or a verified committed original version. Do not rely only on an unstaged diff to recover untracked files. Snapshot source/metadata only; do not copy event datasets or installed native libraries.

Original immutable evidence includes:

- `data/task0041-validation/a09896d5ef3f4c81b150f50b075b58f3/software-acceptance.json`, SHA256 `a86c964e9b6a4355c97c231c0617dda0ef5158ac529d5e7fe1c62bb2f5b08c4c`.
- The failed directory `results/benchmarks/task0041-development-raw-decisions/58ad326c2f574505874d47b69ae32e02`.
- The root `prerequisite-attempt.json`, SHA256 `e12e95bf539b0ba1fbd4e4fec0d5f2b2aa5cc333abdcb219db784e2c9e8898c0`.
- Original synthetic plans/receipts/logs, failed diagnosis and workflow; header-only measured CSV and curated Task0041 summary/report/handoff/prompt/config.

Keep these bytes and their original interpretation. Do not edit the issued record to make it pass, create an operational `attempt.json`/plan, remove/rename/reset the marker, rerun the Task0041 actual CLI or overwrite its documentation. Explain the correction in new Task0042 documents and living memory. This new task expressly permits the narrow live-source repairs below after preserving the failed version; it does not retroactively change Task0041.

## 2. Repair the demonstrated contract defects narrowly

The verified producer in `scripts/validate_development_raw_decisions.py` emits:

`software_accepted_synthetic_development_raw_decision`

The consumer in `development_decision_protocol.acceptance` requires:

`software_accepted_synthetic_development_decision`

Use one authoritative typed status/schema contract with the canonical producer value `software_accepted_synthetic_development_raw_decision`. Both record construction and acceptance verification must use it. Reject the mismatched shorter spelling, unknown states, malformed records and wrong record roles; no alias list, prefix matching or permissive fallback.

Planning also verified `development_decision_native.run` writes `plan["task"] = "0040"`; the preserved final Task0041 synthetic plan contains that value. Correct new chain plans to derive and check the task identity from their bound protocol/config. Test consistency among task, kind, prompt/config, plan, grant and receipt at the relevant admission boundaries. When exercising the Task0041 measurement protocol on fixtures, its protocol task is 0041; the repair study/validation owner is 0042. Record those roles explicitly rather than relabeling preserved plans or calling a repair fixture run an operational Task0042 measurement.

Limit live changes to the shared contract, validation producer, admission consumer/native launch path and necessary focused tests, plus additive Task0042 validation/harness/report files. Preserve raw membership selection, feature arithmetic, model/threshold registry, CPU arithmetic/thread/cache policies, timer boundaries, matrix/budgets and resource caps. No optimization, new candidate or broad controller rewrite.

A shared constant alone is insufficient: the serialized record, scope/path checks, evidence identities and actual consumer predicates must agree. Keep checks for final source/dependencies/native build/config/prompt, required successful validation checks, log/receipt identities and safe owned paths. Distinguish software-validation success, controller-compatible contract admission, a valid freeze, execution authorization and parent acceptance.

## 3. Make admission and freezing control downstream launch

Implement a small checked orchestration path in which failed record validation or freezing returns failure before downstream controller dispatch. The next operation must depend on a successful immutable admission/freeze result, not on the caller noticing an earlier command's exit code.

No independent manual command sequence may treat a failed precheck as permission to continue. Test the actual coordinator/control-flow branch used by the launcher, including absent or partially written freeze artifacts, stale source/prompt/build bindings, changed plan bytes after freeze, and task/scope mismatches. A caller-supplied Boolean or arbitrary path is not an execution permit.

For software-only failure tests, use generated roots and observable leaf spies for controller launch, reservation, raw custody, sleep assertion, worker dispatch and numerical access. Assert those downstream effects are absent after failed admission/freezing, and that no accepted freeze/plan is published. Positive fixture tests must reach the intended synthetic dispatch exactly once; negative tests must not mask the predicate by mocking acceptance/freezing to unconditional success.

Keep the controller's independent final checks, one-attempt rules and normal-exit/reaping requirements. A good earlier check must not bypass changed identities or a consumed allowance later. Task0042 admission proof is scoped to synthetic/contract testing and cannot admit operational payloads. Do not interpret a record's generic `synthetic_only` validation flag as a new operational authorization.

Tests of historical consumed-marker refusal must use copied/generated marker bytes in a temporary fixture root, not invoke the actual controller against the project or write into the original failed namespace.

## 4. Verify the real producer-to-consumer roundtrip

Factor record construction/verification only as much as needed so the validation driver and controller share the same strict production contract. Keep production namespace checks; supply explicit bounded fixture contexts in tests rather than disabling them or broadly admitting arbitrary roots/paths. A new Task0042 validation namespace must not become a general bypass for the consumed Task0041 actual route.

The regression must serialize a record through the actual producer code, read it back through the actual admission verifier and scope wrapper, and compare the independently specified canonical status/task/scope and all bindings. Do not handwrite a separately matching toy record or merely assert equality of two constants. Exercise the outer path/role checks as well as the field validator in an artifact-free generated context.

Required cases include:

- The original producer spelling succeeds under the repaired contract with correct current fixture bindings; the original consumer spelling is rejected.
- A producer/consumer roundtrip after actual file serialization, without replacing either component with a stub.
- Wrong task/kind/scope and the observed 0040-plan/0041-protocol mismatch fail before dispatch.
- Missing/failed checks, modified logs/native receipt, changed source/dependency/native-build/config/prompt identities, unsafe/symlinked paths and malformed records are rejected.
- Failed freeze, missing freeze, interrupted publication or changed frozen bytes do not reach controller/worker launch.
- A valid fixture admission/freezing path reaches only the synthetic executor; duplicate launch and copied consumed-marker cases are refused.
- The original Task0041 record remains preserved and is not rewritten/reissued as current acceptance; repair changes invalidate its current-source bindings. Do not call its old actual namespace to demonstrate this.

Run the complete admission roundtrip on the final driver-emitted software record before the driver declares overall success. Preserve the immutable record and bind the verification result to its exact SHA256 in a sidecar/final repair receipt. Avoid circular receipt hashes or adding a check to a record after it has been consumed. If the roundtrip fails, report failed validation even if the earlier suites passed; do not publish a usable repair acceptance.

## 5. Fresh synthetic validation and bounded native evidence

Use a separate `data/task0042-validation/` namespace, actual Task0042 prompt binding and owned ignored fixture/harness output. Add a validation entrypoint such as `scripts/validate_development_decision_admission.py`; the new repair study must be unmistakably software-only. Preserve original Task0041 validators/receipts as historical evidence while documenting any authorized changes to their live code.

Run targeted contract/orchestration tests, full and portable artifact-free suites, lint/format/dependency checks, and a bounded native synthetic integration covering corrected task/status/plan/grant identities, emitted-record admission, freeze/dispatch gating and the existing chain lifecycle. Use generated raw/membership/golden/model/threshold fixtures exclusively. Verify that the full fixed synthetic chain still conserves its planned 840 read/construction calls and 984 services; treat these as fixture results, not new operational measurements.

Preserve existing native limits during fixture runs: 60 s prerequisites, 180 s per numerical worker through exit/reaping, 60 s reporting, cleanup 2 s inside worker caps, reserved 720 s/whole 780 s; worker RSS 1 GiB/native 512 MiB/controller 128 MiB/owned arrays 64 MiB/journal 16 MiB/log 1 MiB/owned output 128 MiB. No operational raw-custody stage is exercised. Temporary owned idle-sleep assertions for native fixture workers must be verified/released/reaped/confirmed absent; display sleep remains allowed and persistent settings unchanged.

Use fresh final-source/config/prompt/test/package/native-build acceptance. The old 2417 tests/251 bindings/41 native identities and successful Task0041 fixture integrations do not prove the repaired admission path. Record actual new coverage and identities, native invocations/failures/repairs, timing/resources/pressure/gaps and normal exits. Synthetic repairs before final validation are allowed and versioned; preserve failed attempts. No package installation/update or scientific source lookup.

All real event/membership/golden/model numerical access, raw hashing and real HDF openings remain zero. Read-only original source/validation/failure metadata and installed-package/build byte identities are separately accounted for. Synthetic model forwards/fixture reconstruction and historical toy optimizer tests are actual work: do not claim global-zero model/optimizer activity.

## 6. Deliver the repair evidence and remaining decision

Produce:

- `docs/development-decision-admission-repair.md`.
- Actual Task0042 prompt and detailed handoff.
- Narrow repair code/tests and separate validation driver/harness.
- `results/tables/final/task0042-development-decision-admission-summary.json`.

No real timing-cell CSV or cost figure is needed. Explain the original status mismatch, missing integration coverage, the agent's prior continuation after failed freeze, and the additionally verified task-identity defect. State exactly which predicates and launch branches were exercised and their limits; do not present a unit spy as a native process-exit test.

Keep Task0041's failed state, consumed marker, empty measured CSV and zero operational counts unchanged. Snapshot/manifest evidence must permit inspection of original versus repaired source. Task0040 remains the last accepted raw boundary; no accepted joint raw-to-decision sequence exists for replay. Correcting admission establishes software compatibility, not real-data feature/score/decision parity or timing/resource feasibility.

Update README, handoff index and relevant living-memory sections from verified revision 1.36. Preserve Task0036 `unresolved_no_acquisition`, unchanged Task0034 scientific gates, exposure YES/YES/YES, previous acceptances/failures and deferred particle model.

The self-contained Italian handoff should include repair outcome, actual roundtrip and failed-freeze results, new validation/native evidence, historical preservation, numerical-access scope and the next decision. Use a final status such as `software_accepted_synthetic_admission_repair` only when final current-source checks, emitted-record admission and synthetic lifecycle all succeed; this is not an operational measurement status. Include:

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
Task0041_status_preserved: failed_prerequisites_no_retry
Task0041_failure_evidence_and_marker_preserved: ACTUAL_STATUS
producer_record_to_consumer_admission: ACTUAL_STATUS
task_prompt_plan_grant_identity_consistency: ACTUAL_STATUS
failed_freeze_downstream_controller_worker_dispatches: ACTUAL_COUNTS
native_synthetic_invocations_outcomes: ACTUAL_COUNTS_AND_STATUSES
new_operational_controller_invocations_reservations_workers: [0, 0, 0]
new_operational_membership_golden_raw_HDF_numeric_loads: 0
new_raw_byte_hash_passes_and_real_HDF_metadata_opens: [0, 0]
new_operational_feature_model_forward_reconstruction_decision_calls: 0
new_heldout_signal_selection_calibration_accesses: 0
new_operational_optimizer_scaler_calibration_scientific_fingerprint_work: 0
downloads: 0
replacement_operational_execution_authorized: false
Task0042_status: ACTUAL_STATUS
```

The next decision, after successful repair, is a separate explicit authorization for a new raw-to-decision campaign with a new namespace/current-source acceptance/freeze and one new allowance. Do not create that campaign, generate its live grants, reset Task0041 or launch Task0043 automatically.

## 7. Manual Git delivery

Finish with actual Git review, selective staging, staged review, Conventional Commit and push commands for verified branch/upstream. Do not stage, commit or push.

Task0041 is committed in the verified planning snapshot. Review only the narrow Task0042 repair diff and new artifacts against that preserved original commit. Do not misdescribe repaired working files as the original failing source; show the verified snapshot/base and exact repair diff. Do not require an automatic commit, alter unrelated work or stage ignored snapshots/records/fixtures.

Proceed with **Task0042 only**, software-only.
