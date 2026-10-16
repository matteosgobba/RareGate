# LatentTrigger — Task0060: Whole-project Scientific Audit, Necessary Repairs, and a Decisive Experiment Protocol

You are continuing **LatentTrigger**. Perform **Task0060 only**.

## The user's revised objective takes precedence

The user explicitly rejects closing the project with documentation alone. They want the whole project reviewed, important unfinished/incorrect parts fixed and worthwhile tests rerun, followed by **a few substantial tasks that pursue a scientifically valid, experimentally useful conclusion**.

Task0059 remains an accurate historical v1 snapshot. Its recommendation to stop is superseded by this new mandate; it is not a permanent prohibition on scientific development. Preserve historical results, exposed populations, failures and consumed allowances. Do not reclassify old pilots or silently edit frozen protocols/models to manufacture acceptance.

This task must deliver **an actual project audit with necessary focused repairs and fresh validation**, plus one feasible experimental protocol. Do not deliver only a literature survey, a list of future audits or another broad infrastructure foundation. The intended next stages are Task0061 preparation/training/freeze and Task0062 final evaluation/robustness/cost/conclusion. Do not launch them here. Avoid creating additional numbered microtasks for each routine fix.

## 1. Establish current state and an honest review boundary

Read applicable instructions, `docs/development.md`, README, living memory and handoff index; inspect HEAD/branch/upstream/index and unrelated changes. Planning inspection on **2026-10-16 Europe/Rome** found clean `main` tracking `origin/main`, empty index, HEAD **`4a61c74b764afdd2f7aa4eb4c6c4598a48c53336`**, Task0059 committed, memory1.54. Recheck; do not invent push/CI outcomes.

Save this actual prompt at `docs/prompts/0060-project-scientific-audit-and-experiment.md` and an initial Italian handoff at `docs/handoffs/0060-project-scientific-audit-and-experiment.md` before substantive work. Update living current-state language to reflect the user's resumed scientific objective while retaining Task0059 as a historical snapshot. Preserve unrelated changes and historical source artifacts.

Inventory the entire source/test/script/config/CI/documentation structure. The planning inventory found253 source Python files/~75051lines,80 test Python files/~34937lines and1340 statically named test functions, plus29 scripts/~6601lines. These are scope estimates, not completed review or collected-test counts. Every subsystem must receive a review disposition; explain files not examined and claims not recertified. Reading selected hot paths does not justify claiming a line-by-line audit of everything.

A preliminary check at the planning HEAD freshly ran `test_evaluation.py`, `test_splitting.py`, `test_inspection.py`, `test_features.py`, `test_pca.py`, `test_autoencoder.py` together: **98 passed in3.46s** with generated fixtures, no project cache writes or original event/model payload access. It included positive toy model/training work. This is a useful starting observation, not full-suite acceptance or coverage for your changed final source. Reproduce relevant checks after repairs.

## 2. Audit scientific validity end to end

Trace each principal scientific conclusion through config, input lineage, implementation, numerical convention, actual acceptance record and current report. Inspect code and tests, not only handoffs. At minimum cover:

- **Data/provenance:** source versions/units/labels/physical interpretation; eligibility/quarantine; exact-content duplicates and label conflicts; source ordering; train/selection/calibration/test separation; overlap checks and their detection limits; exposure ledger; whether split/fit operations access prohibited populations.
- **Representation:** all-particle versus truncated/jet views; padding/masks, particle ordering, phi wrapping, precision/casts; hand-computable aggregate physics; scalers fitted only on training; transformations, selection and inverse-transform claims. Check appropriate permutation/padding/rotation/beam-reflection properties independently, stating which are physics assumptions and which are required identities.
- **Models/training:** PCA rank selection, reconstruction/objective, AE capacity and bottleneck, loss reduction/event weighting/tails, optimizer/seed/order behavior, early stopping and best-state restoration, serialization/reload, score direction/dtype and use of calibration. Do not claim causality from unmatched PCA6/AE3.
- **Evaluation/statistics:** achievable tied ROC points versus frozen deployment thresholds; achieved FPR rather than target labels; calibration uncertainty; finite-tail counts; paired differences on shared events; multiple models/points/topologies and seed variation. Three seeds do not triple independent sample size. Verify AP/prevalence and uncertainty claims, zero-count behavior, and the distinction between ranking and useful operating performance.
- **Computational evidence:** comparable timer boundaries, input/cache/history, actual batch size and repetitions; sample dependence; direct measurements versus sums; synthetic billing/occupancy support, survivor bias and adverse cases. No synthetic queue total may become a physical rate or independent sample count.
- **Software/resources/reproducibility:** loaders, source/payload gates, reporting/error propagation, supervisor/session/case ownership, cleanup, cache/bytecode writes, environment/CI reproducibility and test isolation. Separate an inference/parity defect from a tooling accounting defect and from an unsupported deployment claim.

Review particle, ONNX/MPS and streaming branches too, classifying each as valid/defective/incomplete/deferred/not needed for the chosen experiment. Whole-project review does not require finishing every abandoned branch. Fix a branch when it affects the intended scientific conclusion or reliable execution; otherwise state the excluded claim and why completion would not advance this experiment.

Use independent oracles, small exact examples, property/metamorphic checks and relevant integration tests. Do not call a test independent if it simply copies the production calculation. A passed test is not evidence of signal usefulness. An unverified historical statement must stay unverified.

## 3. Correct important defects and establish final-source test evidence

Maintain an actionable finding register: ID, severity, affected file/function/line, evidence/reproducer, scientific or engineering consequence, correction, validation, historical results affected and residual uncertainty. Distinguish confirmed defects, design limitations and hypotheses. Do not label PCA's unfavorable AUC a bug merely because it is unfavorable.

Fix confirmed critical/high-impact correctness defects and narrowly related test problems in this task. Add meaningful regressions for them. Also address the known prospective tooling-cache exposure in the workflow used here: disable or explicitly contain caches/bytecode/temp outputs from the start. Do not delete/reset old caches or retrospectively validate Task0058. Preserve compatibility unless a versioned scientific correction is necessary. If a fix changes score/feature/training semantics, version it and identify the results that need recomputation in0061/0062; never silently replace historical numbers.

Audit test collection and side effects first. Run a broad current-source **safe scientific/portable suite in a clean process**, covering relevant modules together to expose shared-state/harness bugs. Then run only the focused generated native/integration paths needed for changed startup/session/cleanup code. Permit artificial arrays/models, toy fits, local generated files and bounded own subprocesses; report their work positively. Use a new audit-owned root and scope, never reset consumed historical runs or impersonate their permits.

Plan finite test groups with practical time/storage/process bounds before heavy generated work. Use existing environments, normal shared Mac use and cache-disabled commands; avoid automatic dependency upgrades, old complete native/model matrices, global host surveys, app closure/reboots and unbounded favorable-scheduling retries. Isolate known costly/native tests from the safe suite and explain exclusions. Count unique expectations, actual invocations, failures and final clean coverage separately. Final acceptance must include one coherent relevant-suite result on the final bundle; selected passing reruns cannot masquerade as a single clean run. Repair harness-state contamination when it affects that result.

This task does **not** authorize original event-array/model/scientific-score payload reads, real fits/inference, raw custody hashing, old operational replay, data acquisition or a new P4. Curated scalar/aggregate/report/config metadata and source code may be inspected. If a historical result requires real recomputation, specify the exact versioned check for the next experimental task; do not sneak it into a test. Synthetic work and primary-source web research are allowed.

## 4. Diagnose why the existing scientific result is insufficient

Use Task0033 diagnostics, Task0034/0036 and Task0049/0059 as evidence, without treating their old scope as the only permissible future question. Exposed samples remain exposed. Do not flip PCA orientation or tune thresholds on the historical test to improve the headline.

The planning review made post-hoc descriptive arithmetic from the eight published AE operating rows: `epsilon_S/epsilon_B` and nominal `epsilon_S/sqrt(epsilon_B)`. At all four published cuts, the latter is below1 for each topology; at the strictest cut the enrichment is approximately0.7264/0.4410. Check those calculations against curated counts if used. They are not a new curve maximum, discovered significance, independent confirmation or proof that every possible threshold fails. They explain why AUC alone cannot support a useful selector.

Task0034's matched ReLU/identity question and strict precision requirements remain frozen historical design. A new question may use a different, justified representation, endpoint, sample-size target and resource contract. Document prospective changes and their rationale before new results; never relax criteria after seeing the new test. Do not spend this task trying to satisfy an old precision condition that is unnecessary for the new decision.

## 5. Choose one feasible scientific experiment

Preferred candidate question:

> At the same measured background acceptance, how much detection efficiency on signals excluded from training can a compact selector retain relative to a more capable reference and simple baselines, and what measured CPU cost does it require?

Assess whether this or one clearly better question can yield an actionable result under the user's resources. Select **one primary question and one data route**, not a menu of ten future studies. Define scientific validity, practical utility and novelty separately. Do not promise a positive neural-network result; a simpler selector dominating the AE is an actionable finding if independently supported.

Consider a small matrix such as compactAE, referenceAE, dimension-controlledPCA and regularizedMahalanobis on a common declared representation. At most two neural architectures×three seeds (six neural fits) is a useful planning ceiling; analytical baselines are separate fits. An encoder/score ablation may replace an arm if better motivated. No open architecture/hyperparameter/feature/score search, best-seed selection or particle attention branch merely to obtain an impressive metric. Final choices follow the audit and feasibility, not a predetermined winning method.

### Data route to examine

The planning review found a concrete alternative to the blocked full-event LHCO confirmation route: **ADC2021**, with trigger-motivated object inputs and public signal benchmarks. It is a new representation/population study, not validation of the original eight-feature LHCO frozen model. The documented lepton preselection limits any generalization to an unfiltered collision stream.

Primary sources, accessed2026-10-16:

- Authors' challenge: https://mpp-hep.github.io/ADC2021/
- Data descriptor: https://www.nature.com/articles/s41597-022-01187-8
- Training background: https://zenodo.org/records/5046428 — listed646.4MB, `background_for_training.h5`, MD5 `08cb4801229f9d480567f8d3f5cac134`.
- A→4l: https://zenodo.org/records/7152590 — listed5.4MB, MD5 `8735ed96a96c39dd13fde7d5f7c85967`.
- LQ→bτ: https://zenodo.org/records/7152599 — listed28.6MB, MD5 `ecd9750e5c51aef54918689eec1e7415`.

These are metadata leads, not accepted local payloads/counts or necessarily a claim about the latest version. Verify version history/bugfixes, schemas, licenses, exact byte/checksum metadata, generation/selection provenance and count evidence. Do not download event files here. Preserve a future final evaluation partition; reading public documentation is not blind challenge participation.

Compare with one LHCO route, including new compact jet features if justified: https://zenodo.org/records/18983506 publishes new signal archives and substructure features, but archives are multi-GB and original full-event compatibility was unresolved. Existing exposed LHCO data may support declared development, not new untouched confirmation. A jet representation would be versioned rather than described as an exact substitute for full-event aggregates. Choose the smaller, interpretable and verifiable route if it answers the question; do not change datasets because one produces a more favorable score.

Consult primary literature where needed: AE limitations https://arxiv.org/abs/2104.09051 ; significance-improvement/sculpting context https://doi.org/10.1103/PhysRevD.107.114012 ; competitive tabular methods in a distinct weakly-supervised setting https://arxiv.org/abs/2309.13111 . Do not claim their results transfer numerically to this experiment.

## 6. Freeze a statistically defensible and executable protocol

Produce a protocol sufficiently concrete for0061/0062, including:

- Scientific estimand and claim scope; input object/feature/mask/units, preprocessing fit only on training, and any symmetry/bias checks.
- Finite sources/versions, provenance and expected download/expanded sizes; metadata acceptance and later payload validation; content-grouped train/selection/calibration/final-test roles, duplicate/overlap audit, exposure rules and forbidden feedback. Distinguish statistical holdout, generation independence, new-process transfer and true blindness.
- Exact candidate/score definitions, bottleneck controls, reference, seeds, training/early-stop/calibration rules, allowed finite development and freeze point. Signals/final-test outcomes cannot guide model or checkpoint choices.
- Primary endpoint based on signal efficiency at calibrated background operating points; achieved FPR and uncertainty, paired differences and seed/topology treatment. AUC/AP are secondary. NominalSIC may be reported with its background-dominated approximation and no discovery-significance claim. Handle calibration uncertainty and multiple comparisons; no zero-background infinite improvement.
- A practical superiority/noninferiority margin and computational advantage chosen before results, plus power/precision calculations using attainable counts and scenario effects. Consider1e-2/1e-3 background acceptance if supported, rather than demanding an arbitrarily unattainable1e-4 absolute halfwidth. Explicitly distinguish proposed targets from scientifically mandatory conditions. Do not choose the easiest target after unblinding.
- Measured CPU boundary, runtime/threads, actual batch shapes, ordering/repetitions/parity and resource observations for the selected candidates. Keep algorithm-only versus feature/preprocessing costs distinct; no need to rebuild physical streaming or complete an ONNX/MPS branch to answer the CPU question.
- Practical new data/fit/evaluation/time/storage/RSS budgets suitable for the shared16GB Mac. Derive new scope instead of importing unrelated historical32MiB diagnostic or old admission limits as universal laws. No background services, broad downloads or indefinite polling. Safety, source validity, experimental correctness and tooling bookkeeping should have explicit separate outcomes.
- Positive, negative and inconclusive decision rules; all results reported; what failure means, what corrections can occur before freeze and when final evaluation must stop. A validity failure cannot be repaired by silently rerunning the same exposed test.

The protocol may be marked ready only if the data route and execution are substantively feasible and critical scientific/software issues are resolved. Do not certify ready by writing a boolean or requiring future unspecified research to make it runnable. If an essential fact remains unavailable, give the precise fallback/narrowed claim and the concrete blocker; do not fabricate sample counts or independent confirmation.

## 7. Deliver audit, fixes and a three-task route

Deliver focused code/test/workflow corrections plus:

- `docs/project-scientific-audit.md` — English audit, scope/coverage, confirmed findings, scientific impact, actual repairs/tests, residual limitations and the selected experimental direction.
- `results/tables/final/task0060-scientific-audit-findings.csv` and `task0060-scientific-audit-summary.json` — actionable findings, subsystem dispositions, exact test/source evidence, historical results affected and readiness/blockers.
- `docs/decisive-scientific-experiment.md` and `configs/research/decisive_scientific_experiment_v2.json` — concrete preregistered design, data route, finite matrix, statistical justification, budgets and separate future execution requirements.
- Actual prompt, detailed Italian handoff, relevant README/index/living-memory updates. Explain why the resumed goal supersedes the closure recommendation without rewriting the historical snapshot.

Task0061 should perform controlled acquisition/preparation and finite development/training, then freeze models/score/thresholds with final outcomes still protected. Task0062 should perform the predeclared final evaluation, robustness and coherent CPU cost comparison and reach the experimentally supported conclusion. Absorb routine necessary fixes within these substantial tasks. No default proliferation of side tasks and no final report presented as a substitute for the experiment.

Use `completed_project_scientific_audit_and_experiment_protocol` only after the actual audit, required repairs, final relevant test coverage and feasible protocol are complete. Otherwise report exact partial scope and blockers. Historical operational readiness remains false; no old pilot is reaccepted and no new experimental P4 is exercised in0060. Preserve original exposure, failures and positive activity; later changes get explicit versions/corrections.

Final Italian response must explain the important findings and corrections, fresh test outcomes/exclusions, why the chosen experiment can be useful, its feasibility and exact next two tasks. Do not reduce the answer to a test count. Finish with exact **manual Git review, selective staging, staged review, Conventional Commit and push commands last** for actual branch/upstream. Exclude ignored event/model/fixture/cache/diagnostic artifacts and unrelated work. Do not stage, commit, push or start another task.

Proceed with **Task0060 whole-project audit, necessary repairs and one decisive experiment protocol**.
