# LatentTrigger — Task0061: Controlled ADC Acquisition, Role-separated Preparation, Finite Training and Complete Freeze

You are continuing **LatentTrigger**. Perform **Task0061 only**.

## Objective and conditional scientific execution scope

Implement and execute the preparation/training half of the **Task0060 preregistered ADC2021 experiment**. Acquire the three pinned files, validate their actual content, construct protected roles, fit the declared six neural/two analytical models, calibrate on background only and freeze everything needed for Task0062. This is one substantial experimental task, not another series of infrastructure microtasks.

**This actual user-issued Task0061 prompt authorizes the bounded ADC acquisition, structural preparation, original ADC training/selection/calibration and freeze described below**, conditional on source acceptance, meaningful generated implementation checks and resource enforcement. It does not reopen old LHCO/P4/particle allowances or authorize Task0062 evaluation. Do not score, summarize or plot final signal/background outcomes, select a model using them, perform the real CPU comparison or launch another task.

The question and all primary criteria remain frozen: at primary background target **0.01**, compactAE must retain90% of reference efficiency, satisfy the declared utility/rate-comparability gates on **both** A→4l and LQ→bτ, and later reduce directly measured joint CPU cost by25%. The0.001 point stays secondary. No result is assessed against those gates here. ADC is a lepton-prefiltered simulation study with a new12-feature representation, not confirmation of the old LHCO model or detector readiness.

## 1. Verify and preserve the real baseline

Read applicable instructions, `docs/development.md`, README, memory, handoff index, Task0060 audit/handoff and the full preregistered protocol/sidecar. Planning inspection on **2026-10-16 Europe/Rome** found clean `main` tracking `origin/main`, empty index, HEAD **`d02e6a5f114e1979a5a5b5e8f11c84aba02eed41`**; Task0060 is committed and memory is **1.55**. Recheck; do not invent a push, remote freshness or hosted CI pass.

Save this actual prompt at `docs/prompts/0061-adc-preparation-training-freeze.md` and an initial Italian handoff at `docs/handoffs/0061-adc-preparation-training-freeze.md` before substantive work. Preserve unrelated changes and historical artifacts.

Verify these immutable Task0060 anchors:

| File | Bytes | SHA256 |
| --- | ---: | --- |
| `docs/project-scientific-audit.md` |23048|`fe6e1876feb84550da4f014e46c8c228ac2a6bd48041d028792af7c70abf2663`|
| `docs/decisive-scientific-experiment.md` |25564|`b7cc15255702ee41aede21119be4eec1832e314703306d032d98574c1073b5c6`|
| `configs/research/decisive_scientific_experiment_v2.json` |20058|`3b49269a948fd98f335df54ae84502de8bc102a9d7f73358f378ebf86ca2191d`|
| `results/tables/final/task0060-scientific-audit-summary.json` |53666|`453b2476f01f15d7242031d88baa03d174257c6ec51f6e90e40e4e4fef2ef88f`|

The historical final audit bundle `9bc0812296844381510ffc3e211d3d18bc355d0af9a90c84f4ae43e0fd234fba` passed3002tests+13subtests with938deselected. This is evidence about that bundle, not automatic qualification of your new12-input implementation. Preserve the FP32-constructor and retained-cleanup-ownership repairs. Do not restore contaminated fixtures or use an old accepted receipt as a current pass.

## 2. Implement a small versioned ADC path and validate it before real work

Use a dedicated v2 ADC module/adapter and new artifact schema2. Keep the old8-input AE/PCA contracts, original models, score semantics and historical files unchanged. Do not monkeypatch global architecture/feature constants or route final roles through v1 `ProcessedStore`, whose constructor scans all roles.

Provide an inactive-on-import/help entrypoint, for example `scripts/prepare_decisive_adc_experiment.py`, with explicit phases and a new source-bound owner/attempt ledger. A Task0061 execution config may reference the immutable protocol and authorize only this scope; do not edit Task0060's historical `execution_authorized_in_0060:false` to create permission. Bind allowed sources/roles, paths, budgets, code/config/test/prompt identity and future-stage denial before activation.

Before acquisition, exercise tiny generated HDF fixtures and artificial models through the **same** schema/gather/feature/role/training/artifact/calibration path. Test metadata spelling/mapping, malformed shapes/classes/padding/order/nonfinite inputs, quarantine and duplicate/conflict rules, deterministic partitioning, training-only scalers, protected-role denial, model counts, explicit CPU FP32 factories, sampler pairing/tails, selected-state restore, public B32 scoring/padding, exact serialization/reload, strict tied quantiles and uncertainty-rank indexing. Use independent hand-computable feature/linear-algebra/statistical oracles; do not merely duplicate implementation expressions.

Test the complete generated orchestration with small counts that cannot be accepted as real execution permits. Generated contexts stay separately typed/scoped; original files cannot be reached by fixture fallback. Check normal and interrupted reporting/cleanup without consuming real fit slots. Count toy numerical/model/optimizer work separately.

Implement and test outcome-independent statistical helpers and the deterministic future CPU/input schedule now where needed for a complete freeze. Use artificial scores only for final-evaluation helper checks. Any future unblinding/evaluation command remains disabled without a fresh Task0062 scope. No real timing matrix or final quality run is needed to validate these helpers.

Run one coherent relevant test group on the final implementation before real acquisition/fits, including existing scientific-core and affected audit regressions. Broaden to the audited portable suite if shared-code changes justify it; do not repeatedly rerun costly historical matrices. Fix routine implementation/harness errors within this task. Freeze relevant behavioral code/config/test/prompt identities before real work; later source corrections require explicit dependency/validity accounting, not earlier-source passes.

## 3. Enforce a finite new study, with recoverable accounting

Use one new owned study layout with known raw/prepared/private artifact/diagnostic paths. Model artifacts belong under **`artifacts/models/decisive-v2-adc/<arm>/<seed>`**, analytical models under `<arm>/fit`. Declare concrete role and ledger paths before creating them. Reject aliases, unintended overwrite and ambiguous ownership. Preserve partials and completed stages.

The **whole Task0061/0062 study storage cap is8GiB**, with **4GiB own-worker RSS**, one active worker and no background services. Budget retained sources, role matrices, fingerprints/index/sort scratch, feature/score buffers, all six checkpoints/optimizer work, histories, source snapshots, test fixtures, failures, temporaries, receipts, curated copies and Task0062's future scores/timing outputs. Do not reset the storage total per phase. Bound arrays/chunks before allocation; observe own wall/RSS/storage externally with bounded cleanup. Disclose sampling/enforcement limitations rather than claim an OS-wide all-write proof.

Task0061 total≤**4hours**; acquisition≤45minutes total and≤20minutes per file inclusive of its attempts; preparation≤30minutes; each neural fit≤20minutes; cleanup reserve10seconds. Record task/campaign/phase starts and inclusive elapsed time, including relevant validation, imports, reporting, finalization/exit/reaping. No timer resets that conceal cumulative work. Use normal shared-Mac operation; no host survey, global idle/RAM gate, app closure, reboot or dependency upgrade.

Before imports disable bytecode and pytest/Ruff caches and contain XDG/matplotlib/temp outputs. Reuse existing installed libraries; pin resolved Python/NumPy/SciPy/Torch/sklearn/HDF versions/build/BLAS and one effective CPU thread, zero loader workers. No MPS/ONNX probe or fallback. Keep safety, source validity, scientific correctness and tooling accounting as distinct outcomes; none is silently waived.

Persist exclusive stage/fit intent **before** work, progress, completion/failure and actual resource counts. At most six real neural fit attempts and two real analytical fit attempts; a failed/interrupted fit remains incomplete and consumes its allowance. No seventh fit, replacement seed or continuation after a failed fit. Completed immutable stages may be verified and reused without rerunning them. After rate limit/tool disconnect, first inspect your owned process and ledger/artifact identities: a missing chat response is not evidence that a fit failed or permission to repeat it. Do not relaunch an active worker or invent zero work from an incomplete receipt.

## 4. Acquire exactly the three preregistered sources

Use the pinned version records and exact filenames, not a latest-version resolver, blackbox, substitute signal or extra source:

| Role /record | Filename | Bytes | Publisher MD5 |
| --- | --- | ---: | --- |
|background /5046428 v2|`background_for_training.h5`|646391984|`08cb4801229f9d480567f8d3f5cac134`|
|A→4l /7152590 v2|`Ato4l_lepFilter_13TeV_filtered.h5`|5421265|`8735ed96a96c39dd13fde7d5f7c85967`|
|LQ→bτ /7152599 v2|`leptoquark_LOWMASS_lepFilter_13TeV_filtered.h5`|28613508|`ecd9750e5c51aef54918689eec1e7415`|

Their metadata/version/file URLs are in the frozen sidecar. Reuse/verify Task0060 metadata provenance and retrieve only bounded necessary record/file metadata. Expected accepted bytes total **680426757**; event-transfer wire cap **1GiB**,≤**6event-transfer requests**, at most one bounded transient retry per source. Record requests/redirects/partial bytes separately from metadata retrieval and unique accepted bytes. Any retry must fit the remaining per-file/total time and wire allowance. No generic automatic retry stack or retry after a checksum/schema contradiction. Existing matching files may be reused only after full verification and provenance accounting.

Download to owned partial files, verify exact length and MD5, compute local SHA256 and atomically accept. Record actual bytes even on failure. Do not overwrite a mismatching existing file or treat a partial prefix as accepted. A source failure stops before fits; no favorable dataset fallback. No event payload is acquired merely to inspect a different source's possible performance.

## 5. Validate actual content, group it, and construct sealed roles

Follow the exact protocol/schema and document source-defined acceptance constants before payload decisions. Inspect headers before allocations; `Particles` must be numeric FP32/FP64[N,19,4]. Parse the actual classes/names metadata, allowing the two declared class-key spellings only when decoded meaning agrees. No guessed axis/unit/type mapping. Check links/storage/dimensions/metadata lengths so reads stay inside the accepted files.

Scan chunks≤**8192rows**. Enforce the declared MET/4electron/4muon/10jet slots, type IDs, finite coordinates, legitimate zero MET, positive visible pT, all-zero type0 padding, sorted class prefixes, lepton preselection/object cuts and the specified1e-5GeV boundary allowance. Keep rule-specific per-source and total structural counts and enforce the declared≤1% quarantine ceiling. Record any necessary denominator implementation detail before the first payload scan, never after observing invalid rows. A contradictory mapping, cross-label conflict or insufficient eligible unique groups stops before fitting. Published counts4000000/55969/340544 are expectations; record realized counts rather than forcing equality.

Canonical content grouping is exactly `adc-exact-content-v2`: normalized signed zero, FP64 phi wrapping, type0 removal, per-class lexicographic sorting and little-endian FP64 class/count/coordinates, SHA256, lowest source-row representative. Deduplicate across all three sources before assigning roles; make source/topology labels and conflict handling explicit and consistent with the protocol. Do not silently assign an ambiguous cross-source group to a convenient role. Exact content checks are not near-duplicate or generator-independence proof.

Sort background groups by SHA256 of UTF-8 **`adc-split-v2|1729|fingerprint_hex`**, then fingerprint for ties. Allocate consecutive roles:

| Role | Unique background groups |
| --- | ---: |
|training|200000|
|selection|50000|
|calibration|1000000|
|final background|1000000|

Independently hash-order each signal source; reserve exactly **40000unique groups per topology**, all for final evaluation. The2250000background/40000signal minima cannot be reduced. Remaining groups stay unused/sealed, not a retry or exploration pool.

Create **physically separate role files** and role-bound manifests. Fit scalers on training only, then structurally prepare final files without exposing their outcome summaries. Restrict the training worker to training/selection payloads; calibration is a later distinct phase. The trainer must not open/hash original all-role files, calibration, final background or signal files. Generated negative I/O tests must exercise these boundaries. Explain the actual enforcement and its limitations; a Python audit hook is not an OS security sandbox.

Record structural ingestion/hashing/feature preparation positively as ADC access. Do not produce final/signal feature distributions, means, losses, scores, plots, efficiencies, correlations or example events before freeze. Counts, rule failures, shape/dtype and integrity hashes are structural evidence. Freeze membership and sealed payload hashes; no model-based exclusion, role reshuffle or outcome-driven quarantine. Curated outputs contain aggregate counts/hashes, not real event/group ID lists or arrays.

## 6. Prepare exactly the12 frozen features

Implement **`adc-invariant-aggregates-v2`**, in the sidecar's order: log1pMET; three class counts; three log1pscalar-pT sums; three log1pmaximum-pT values; visible transverse balance excluding MET; log1p massless all-lepton mass. Use all **provided** visible objects and type masks, not unrecorded full-event particles. Publisher caps remain truncation.

Accumulate FP64; use the declared lepton pair-mass formula, empty/singleton conventions and zero-denominator convention. Fit FP64 training means/population standard deviations, require std>1e-12, standardize without clipping and cast once to FP32. Preserve scaler/hash identity across all roles. New representations cannot masquerade as the old eight aggregates or an exact inverse.

Freeze the development objects/features used later by the CPU and symmetry schedule: use a precisely identified hash-ordered training-only4096-group subset, with its first512 for development symmetry checks, and record that choice before scoring. It must be the same provided-object schedule for all eight streams. The512 final-background robustness rows are identified by the frozen rule but remain unopened for evaluation until0062. No CPU performance claim or final robustness outcome is produced here.

## 7. Execute the finite models in order

Fit exactly:

- compactAE **12→8→3→8→12**,271parameters;
- referenceAE **12→32→16→3→16→32→12**,1999parameters;
- fixed-rank **PCA3**, training-centered FP64 full SVD, no whitening/rank search;
- regularizedMahalanobis, training FP64 mean/covariance ddof0, **Creg=.9C+.1trace(C)/12 I**, Cholesky solve rather than explicit inverse.

Neural order is seed1729compact→reference,1730compact→reference,1731compact→reference, then PCA3 and Mahalanobis. Explicit CPU FP32 Linear factories, ReLU hidden layers and linear bottleneck/output. Isolate initialization RNG state; use a separate local sampler generator with the same seed and advancing per-epoch state across architectures. Hash the actual sampler stream including tails without extra random draws; compare common-epoch order hashes. Equal seed does not mean equal initialization tensors for different architectures.

Adam options are frozen in the sidecar: lr.001, betas(.9,.999), eps1e-8, no weight decay/AMSGrad/foreach/fused/maximize/capturable/differentiable/decoupled weight decay. Verify installed support/resolved options; no silent default substitution. One CPU thread, no loader workers, batch2048 with all tails,≤80epochs, patience8, min_delta0. Equal-event/channel MSE; event-weighted epoch summaries. Each model selects/restores its own strict background-selection minimum; ties keep earliest. Reaching80epochs is not convergence proof.

Record all attempts, histories, stopping reasons, parameter/state hashes, selected epoch and restored-selection/reload checks. Count actual batches/epochs/updates/rows and incomplete in-flight work; do not infer completion from a missing exception. No best-seed selection, averaging weights, ensemble, hyperparameter search or signal-guided adjustment. All six neural streams remain separate.

Finish and bind all eight fitted models plus preprocessing before calibration. A numerical/identity/resource failure cannot be rescued by dropping an arm or spending another fit. Preserve the partial matrix and exact reason.

## 8. Calibrate and freeze, keeping final outcomes protected

Use the same canonical public scoring path for calibration and later final evaluation: **B32**, zero-padding only the final incomplete batch and retaining actual rows. AE forward is FP32, subtraction/SSE FP64; PCA residual SSE FP64; Mahalanobis nonnegative FP64 quadratic score. Higher is anomalous for every stream. Verify exact B32 serialization/reload/repeat on development fixtures/rows, retained output ownership and the padded-tail convention. Calibration cannot choose a new checkpoint, score or representation.

After the calibration cuts are frozen, perform the predeclared .7radian rotation and beam-reflection checks on the fixed512training-development events, using protocol feature/scaled-feature atol/rtol1e-5 and score allowance1e-5+2e-5max(1,abs(reference)). Record all score margins/decision changes and positive development inference work. A material required-identity failure blocks the complete freeze; within-bound near-cutoff flips remain reported sensitivity. Do not use these checks to select a model or tolerance. The separate512final-background checks remain Task0062 work.

Score **only the1000000calibration groups**, once per frozen stream, in declared order. Fit strict `score > threshold` at `higher` quantiles for α.01/.001. Retain own private calibration score/rank evidence as budgeted; report counts/ties without interpreting them as final FPR. Eight streams imply8000000calibration score rows and250000B32 public calls for one complete pass, plus separately declared development/reload checks. Do not mix these with unique events or training forward counts.

Compute the exact preregistered population-quantile rank brackets using the fixed .01/16 family allocation and one-based indexing. The planning brackets are [989658,990340] and [998890,999107] at N1000000. Independently test indexing/ties/sentinels; store endpoint score values, ranks, conventions and source identities. Those brackets propagate uncertainty in0062; they are not replacement deployment cuts. No final-background recalibration, randomized ties or empirical margin relaxation.

Do not calculate signal efficiencies, final-background acceptance, AUC/AP/SIC, NI, dominance, bias profiles or a final selection decision. Ensure no final score files are created. Structural final preparation is not true blindness; record exposure precisely and preserve the no-outcome-feedback boundary.

Write an immutable **complete freeze manifest** binding protocol/prompt, code/config/tests, exact runtime/build/thread evidence, all source/role/preprocessing identities,8model/checkpoint identities, actual histories/order/stopping records,16deployment threshold/rank-bracket pairs, canonical score shape/tail rules, sealed final roles, deterministic CPU schedule and robustness/statistical specification. Include a Task0062 preflight recipe that checks only these identities and records unblinding intent before any future final scoring. Freeze evaluator-relevant implementation choices using generated evidence, with no actual Task0062 activation.

## 9. Deliver a ready package, not a premature scientific conclusion

Create focused implementation/tests and:

- `configs/research/decisive_adc_preparation_v2.json` — Task0061 execution/role/budget/source binding, referencing the immutable0060 protocol.
- `docs/decisive-adc-preparation-training.md` — English source acceptance, role separation, actual model/calibration/freeze work, reproducibility, failures and remaining0062 work.
- `results/tables/final/task0061-adc-source-and-role-custody.csv`, `task0061-adc-model-freeze.csv`, `task0061-adc-calibration.csv` and `task0061-adc-preparation-summary.json` — actual provenance/counts, all8fits, per-stream cuts/brackets and scope-qualified validation/resource outcomes.
- The content-bound **private** complete freeze manifest and artifacts at explicit ignored paths. Curate only small metadata; no original events, feature/score arrays, optimizer/checkpoint tensors or downloaded files in Git.
- Actual prompt, detailed Italian handoff and README/index/living-memory updates from the verified revision.

Use **`completed_adc_preparation_training_and_freeze`** only after source/group/role validity, necessary final-source implementation checks, all six neural/two analytical fits, calibration and complete immutable freeze pass. Record `ready_for_Task0062:true`, `final_evaluation_performed:false`, `Task0062_started:false`, scientific usefulness not yet evaluated and general operational readiness false. Otherwise report a precise partial/source-invalid/incomplete-matrix outcome; no claim that a prepared model is experimentally useful.

The final Italian response must show actual source/unique-role counts and structural exposure; all model epochs/stopping/checkpoints; calibration/freeze identities; generated versus original work; consumed attempts/resources; failures and limitations. Explain that0062 alone will assess the preregistered efficiency/retention/common-rate/cost gates. Preserve all prior scientific exposures and failed/consumed pilots, Task0059 snapshot and Task0060 corrections. Finish with exact **manual Git review, selective staging, staged review, Conventional Commit and push commands last** for actual branch/upstream. Do not stage, commit, push, unblind or launch Task0062.

Proceed with **Task0061 controlled ADC preparation, finite training/calibration and complete freeze only**.
