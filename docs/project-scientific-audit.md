# Whole-project scientific audit — Task0060

2026-10-16 Europe/Rome. The resumed objective is a defensible experimental
quality/cost conclusion, not documentation-only closure. Task0059 remains an
accurate historical v1 snapshot; its recommendation to stop is superseded by the
user's new mandate. No frozen protocol/model artifact, historical result, exposure,
failure or consumed allowance has been rewritten. Operational readiness remains
false. Task0061 and Task0062 are specified, not started.

## Boundary and evidence inventory

Actual starting state: clean `main`, tracking `origin/main`, empty index,
HEAD `4a61c74b764afdd2f7aa4eb4c6c4598a48c53336`, Task0059 committed, memory1.54.
No push, remote freshness or hosted CI outcome was inferred or checked. No unrelated
changes existed at entry. The original prompt and initial Italian handoff were
saved before substantive work. Living memory now records resumed scientific work.

The tracked baseline inventory reproduces **253 source Python files / 75051 lines,
80 test Python files / 34937 lines / 1340 statically named test functions,
29 scripts / 6601 lines**, plus 51 configs, 190 documentation files and one CI
workflow. Static functions are not parametrized collected cases. The file-level
[review inventory](../results/tables/final/task0060-source-review.csv) records each
path, source identity, size, structural scan and review level. Default
`structural_only` means its implementation was **not individually examined**.
`targeted_code_review` means selected relevant code/guards/tests were examined,
not line-by-line certification. Every subsystem below has a disposition, including
branches excluded from the chosen experiment. No source coverage percentage or
claim to have read all 75051 lines is made.

Principal paths were followed from data/config through implementation, relevant
tests and accepted curated records. Historical operational/scientific payloads,
original models, score arrays, event hashes, old native runs and raw custody were
not reopened. Source/config/report text and small aggregate CSVs were inspected.
No new event acquisition, real fit/inference, P4 or historical acceptance replay occurred.
Generated arrays, toy fitting/optimizer updates, public model scoring, calibration,
HDF fixtures, actual own-process file/mapping operations and bounded children are
positive new test work. They do not establish signal usefulness.

## Subsystem dispositions

| Subsystem | Code/config/test evidence examined | Disposition and excluded claim |
|---|---|---|
| Source acquisition and provenance | `data/metadata.py`, `acquisition.py`, `analysis.py`, three-prong schema/protocol guards; LHCO config and source-feasibility report; mocked transport tests | Valid bounded publisher identity/transport policy within old scopes; no fresh raw custody or actual schema recertification. New ADC metadata verified separately. |
| Eligibility, grouping and splits | `inspection.py`, `splitting.py`, `eda.py`, preprocessing/processed store, inspection/splitting/preprocessing tests | Exact-content grouping excludes truth from fingerprints, keeps source-low representative, quarantines label conflicts and hashes groups into roles. Exact canonical equality is not near-duplicate or generator-independence detection. Structural inspection may see all labels; statistical fitting still selects training only. |
| Feature preparation/readers | `features.py`, `inspection.aggregate_observations`, `preprocessing.py`, `processed.py`, frozen feature contract and generated tests | Full-event eight aggregates use all retained source particles; object view caps at384 with explicit masks/retained fractions. Source sorting precedes FP32 cast. Valid identities tested; v1 whole-store verification is unsuitable for a payload-isolated v2 holdout (F05). |
| PCA and tabular AE | `models/pca.py`, `autoencoder.py`, `background.py`, training AE/background/convergence; model configs and tests | Valid supported SVD/reconstruction and selection/calibration separation; ambient dtype defect fixed (F01). PCA6/AE3 is an unmatched empirical comparison, not causal evidence. |
| Particle model/training | `particle_set.py`, relevant training/mask/serialization code and `test_particle_set.py`; historical resource reports | Corresponding-particle local2/global8 model is permutation equivariant, not arbitrary-set matching or a single global bottleneck3. CPU/masked angular objective has generated tests; canonical model/calibration/usefulness incomplete.192 real diagnostic steps remain consumed. Deferred; finishing it would not answer this small tabular CPU question. |
| Metrics/calibration/evaluation gates | `metrics.py`, `thresholds.py`, `run.py`, guarded/local-three-prong audits and source restrictions, evaluation tests/configs | Achievable tied ROC and strict deployment cuts are distinct; score orientation is preserved. Wilson intervals and zero-count upper limits are conditional; old reports do not give joint calibration/model-selection uncertainty. New protocol supplies that layer. |
| Diagnostics/research activation | diagnostics analysis/reader ledger, controlled-activation model/order helpers, Task0033 aggregates and Task0034/0036 design | Valid exploratory descriptions and synthetic software evidence within scope. No causal feature importance, completed matched real experiment or independent confirmation. Old design remains frozen; v2 asks a different question. |
| Native CPU/parity/timing | benchmark core, arithmetic/AE parity, prepared/raw selection/provider boundaries, timer/statistical reporting, configs and Task0049/0059 reports | Six accepted historical boundaries remain distinct. Changed source is not requalified against their old hashes. No sum/subtraction supplies a direct joint time; no historical vectors or full model/native matrices rerun for acceptance. |
| ONNX export/ORT | export graph/protocol/numerics and CPU reporting plus portable tests | Conditional numerical/export evidence; Task0025 parent deadline failure remains failed/consumed. No accepted ORT speedup inferred from a completed child body. Not needed for the native CPU experiment; physical export/runtime matrix excluded. |
| MPS/device | CPU/MPS transfer/numerics/protocol and device tests | Software simulation/transfer policy reviewed; hardware availability and physical device conclusions not recertified. No fallback is accepted as MPS timing. Deferred/not needed for CPU estimand. |
| Synthetic trigger/occupancy replay | FIFO integer engine, refined assignment/source checks, selection support code and curated conclusions | Valid model-based accounting within explicit assumptions; sparse support, lookup billing, adverse cases and completion-conditioned latency retained. Large historical replay fixture matrices excluded from final audit suite; their scientific/physical claims not recertified. |
| Streaming/startup/session/cleanup | records/quota, transport, supervision, CPU runtime, HDF consumer gates, session contexts/controllers and pure tests | Separate generated/P4 capabilities, eager session journal and resource ownership reviewed. Mapping-close ownership defect fixed (F02); test harness roots/state fixed (F03). Whole pilots remain unaccepted. No new physical stream or old permit. |
| Resource supervisors | source inventory; selected particle sampling/collector/readiness policies and synthetic tests | Historical admissions/limits remain scoped; no global host survey/readiness or particle allowance reset. Most supervisor implementation files receive structural/test disposition only, not individual recertification. |
| Scripts/configuration/CI/docs | all path/AST/config inventory, entrypoint side-effect scan, pyproject/CI/development/README/memory/index and principal reports | New cache-contained audit runner; legacy entrypoints not operationally invoked. Dependency ranges and Linux CI config are not an environment lock or hosted pass. Historical handoffs and nonselected reports are inventoried, not reaudited as independent experiments. |

## Scientific chain and independent checks

**Data:** `LHCO_RD` pins R&D v5, exact filename/byte/MD5. `scan_and_split` validates
the 1100000×2101 FP64 schema, padding/finite/label eligibility, fingerprints sorted
FP64 triplets without labels, detects exact-content conflicting labels and retains
one representative. `assign_groups` implements integer hash cutoffs (70/15/15,
validation split into selection/calibration); source-ordered representative indices
and hash-ranked development subsets have distinct roles. `verify_split_artifacts`
recomputes memberships before training-only EDA. These are source-level checks;
current original integrity, duplicate counts and event lineage are not recertified.

Training EDA selects training rows before statistics even when HDF decompression
touches mixed chunks; object scalers weight particles and aggregate scalers weight
events, ddof0 in FP64. `ProcessedStore.verify_store`, however, hashes/opens/scans
combined role payloads before a caller requests a role. Therefore `allow_test=False`
guards model reads, not all underlying byte access. This is an important access
boundary limitation, **not evidence that test features entered historical fitting**.
V2 specifies physically separate role files and a train/selection-only process.
All original scientific test exposures stay permanently YES/YES/YES.

**Representation:** source phi is wrapped before canonical FP32 storage, sorted by
pT with eta/phi/source-slot tie breaks before rounding. Aggregates accumulate in
FP64 from canonical physical values; the object model view retains the original
source order after cast rather than resorting rounded ties. Zero padding does not
define a transformed-feature mask: a valid transformed pT of zero remains valid.
The eight aggregate definitions include massless-constituent mass, normalized
vector pT balance and signed weighted eta mean. Truncated/object and jet views
are not exact substitutes for full-event aggregates. Log/standardization plus
FP32 casts do not give lossless inverses or recover discarded particles.

New hand-computable checks use two back-to-back 5 GeV vectors (mass10, balance0,
concentration1/2) and a pairwise Lorentz-product mass oracle independent of the
production summed-four-vector calculation. Six particle permutations and added
padding preserve fingerprints/canonical physical values/aggregates. Four azimuth
rotations preserve the aggregate vector; beam reflection changes the sign of
weighted eta mean and preserves the other components. Signed eta is covariant,
**not invariant**; an AE score is not automatically reflection symmetric. These
are mathematical identities; detector symmetry is a physics assumption. Existing
particle mask/gradient/permutation tests exercise a different equivariant model.

**Models/training:** PCA fits centered FP64 full SVD and chooses the smallest rank
meeting the fixed explained-variance target; full rank is rejected. A diagonal
covariance example independently requires rank5 at target.8 and residual scores
25/16/9 on the discarded axes. The unfavorable historical PCA AUC is not a defect
and is not flipped. The old AE has155 parameters, 8→6→3→6→8, ReLU hidden layers,
linear bottleneck/output, equal-event/channel MSE, deterministic local shuffle,
Adam, own background-selection stopping and cloned best-state restoration.
Tail-weighted epoch reporting is checked using four zero events and a final
100-MSE event: epoch MSE20, not a mean of batch means. SGD's per-batch updates are
not a proof of uniform optimization influence of every event or global convergence.

Calibration is requested only after restore/export/reload in `run_background`;
FP32 reconstructions are converted to FP64 **before** subtraction and SSE reduction.
Model reload/score direction/schema/seed/order tests use artificial data. F01 fixes
ambient default dtype without changing supported historical FP32 initialization,
parameters, feature/score definitions or thresholds. No accepted numerical values
are replaced and no historical recomputation is implied. Any future new features,
architectures, fits and calibration are explicitly v2 and require Task0061/0062.

**Statistics:** a four-score tied example enumerates pairwise AUC7/8 and AP5/6
independently of sklearn; zero-FPR attainable ROC accepts only the highest signal.
The exact zero-count upper limit is checked by `(1−upper)^10=.05`, and rejection
stays unresolved. AP's historical prevalence is100000/(100000+150471), not a
physical event rate. Wilson intervals condition on frozen thresholds/models;
shared background, two topologies, four cuts, multiple candidates and seeds prevent
independent replication or a single unadjusted-significance claim. Three seeds
never triple event counts. The new protocol predeclares paired group-level bounds,
quantile uncertainty, multiple-comparison allocation and observed-rate checks.

**Computational chain:** source inspection confirms separate preloaded forward,
score/decision, prepared service, selected-read/feature and directly measured joint
boundaries. Old raw timing uses a384-row selection within a1024-row development
prefix, repeated windows and prior custody/cache history. Neither nominal B nor
HDF chunk geometry is actual m, measured disk I/O or cold cache. Task0047 observes32
of169 occupancies;137 missing remain. Task0048's lookup simulations transport
dependent historical durations under explicit policies: repeated scenarios/queue
presentations do not become independent events, physical rates or universal service
bounds. Completion-conditioned latency hides dropped events unless the full
overflow/late/pending accounting is retained. Adverse/control billing/previous-anchor
deficits in Task0049/0059 remain part of the conclusion. These source/report checks
do not remeasure or reaccept the original campaigns.

## Confirmed repairs and finding register

The [actionable CSV](../results/tables/final/task0060-scientific-audit-findings.csv)
contains IDs, kind/severity, file/function/line, reproducer, consequence, correction,
validation, historical impact and residual uncertainty. Confirmed defects are
separate from design limitations and hypotheses.

- **F01:** `CompactAutoencoder` inherited ambient Torch dtype/device. With the same
  seed and a FP64 default it produced FP64 parameters, violating its FP32 input/
  artifact contract and changing initialization. Explicit CPU FP32 factories fix
  it; the regression compares the full state with the supported historical stream
  and preserves the caller's default. Pre-fix:1failed/14passed in the new oracle group.
- **F02:** `Store.close` closed/forgot the fd after failed mmap close, and emergency
  cleanup removed both mapping/descriptor ownership despite BufferError. Real
  exported memoryviews reproduce both defects (2 failing cases before repair).
  Failed mappings/fds now remain registered for a subsequent bounded retirement;
  an additional pre-syscall fd-close failure also retains its registration instead
  of removing it in a finally block (one failing reproducer before correction);
  unrelated fds still close. Generated OS mmap/EBADF checks and a fresh bounded
  child verify successful retirement after the view is released. This fixes
  ownership accounting; it supplies no historical inference/parity acceptance.
- **F03:** tests depended on original model/Task0057/0058 roots, consumed unit slots,
  old source pins, and injected I/O failures surviving into fixture teardown.
  Convergence tests now use generated155-parameter documents. Streaming tests use
  new mock repositories/current-source bindings in **test copies**, preserve frozen
  configs, retire injected failures before cleanup and restore global quota state.
  A generated late-registration counterexample replaces a historical receipt read.
  One stale error regex and a source-free import assertion incorrectly extended to
  later gated adapters are repaired narrowly. This makes coherent grouped testing
  possible without operational activation or historical permits.
- **F04:** prospective tooling cache exposure is addressed by `-B`,
  `PYTHONDONTWRITEBYTECODE=1`, disabled pytest cache/plugin autoload, Ruff `--no-cache`,
  and owned XDG/matplotlib/temp directories **before imports**. A Python open audit
  rejects original `data`/`artifacts` opens and checkout writes during tests. This
  supplements source review; it is not an OS-level proof over native-library I/O.
  Generated HDF paths are owned fixtures. No old cache is reset, inspected for growth
  or retroactively reserved; Task0058 stays storage-partial.

The remaining register entries constrain claim scope: whole-store access, old
utility/calibration uncertainty, unmatched capacity, representation/symmetry,
timing comparability, synthetic support/survivor bias, incomplete particle/ORT/MPS,
dependency/CI reproducibility and pending ADC payload acceptance. None is concealed
by a software test pass. The signed-eta mechanism remains a hypothesis, not a
confirmed physics bug.

## Fresh validation, failures and exclusions

The planning98passed observation is historical. All six files are included again
in the final coherent group. Full test collection initially found3920 parametrized
cases, not1340; the first collection mistakenly excluded a native-named test that
actually uses stubs. Source review restored it in the final portable selection.

The first broad process stopped at observed1GiB after70.155s; it emitted2016 pass,
35 error and8 failure markers, but lacked a final report and exact completed-stage
accounting. The second broad process also hit1GiB (78.173s), retaining incremental
stage evidence. These are incomplete, **not acceptance runs**, and include some
old complete generated service/model fixture work before the final selection was
narrowed. That activity is positive artificial work and is not repeated for an old
matrix acceptance. Three intervening focused groups retain239pass/16fail,
48pass/30setup-errors and79pass; fixture construction mistakes during this repair
are retained, not presented as prior green coverage. The pre-fix numerical and
cleanup reproducers are separate actual invocations. A subsequent coherent
`portable-3` passed3001+13subtests before final source inspection found the additional
fd-close error path; its1failed/19deselected reproducer and correction are retained.
That older pass is not substituted for final-source coverage.

**Final source:** one complete `portable-4` process passes **3002 tests plus13 nested
subtests**, **938 deselected**, with zero failures/errors,141.22s pytest and
143.560983458s externally observed. It writes2133133980B at the last observed peak
under2GiB. Source/config/test bundle is
`9bc0812296844381510ffc3e211d3d18bc355d0af9a90c84f4ae43e0fd234fba`; all417 bundle files still
match after validation. The98 expectations in the six planning files pass together
inside this group. Whole-repository no-cache lint/format also pass. This is65 test
modules on one final bundle, not a sum of favorable reruns.

Final test/source/dependency identifiers, counts, commands, durations, per-module
coverage and all attempt accounting are in the
[summary](../results/tables/final/task0060-scientific-audit-summary.json).
The finite final group has180s wall /2GiB observed output ceilings in a new root;
the change from1GiB responds prospectively to the fixture footprint, not a scientific
criterion relaxation. The monitor is periodic and can observe a write overshoot;
it is explicitly **not** a pre-growth all-writes guarantee. Every attempt retains
its own root. No historical root or consumed allowance is reused.

The final selection excludes complete historical decision/payload/partial/targeted
service matrices and large repeated joint/occupancy/refined source-bundle fixture
modules, plus prepared-service/development-raw full fixtures. The exact ten module
names and deselected parametrized cases are recorded, not relabeled as passed.
Source dispositions still cover these subsystems, with pure guards tested elsewhere.
No full historical native/model/physical/ONNX/MPS matrix runs. Only the new small
mapping/descriptor integration and bounded own child are required by the changed
cleanup code; startup/thread/P4/session algorithms are not changed or requalified.
No hosted CI, coverage-tool result or signal usefulness follows from these checks.

## Why the v1 science is insufficient and the selected next experiment

Task0033's accepted score quantiles show higher signal medians coexisting with
background p99.9 exceeding signal p99.9. Signed-eta rank associations are descriptive;
they do not establish a mechanism. Task0034's matched activation proposal controls
parameters but remains a frozen historical design. Task0036's independent full-event
route remains unresolved. Tasks0049/0059 consolidate moderate AE AUC (~.660/.586),
conditional CPU evidence and explicitly partial streaming integration, not usefulness.

Task0060 checks post-hoc arithmetic from the eight **published count rows** in
Task0032's calibrated utility CSV. At the four original cuts nominal SIC is
.740465/.615418/.339017/.020169 for two-prong and
.524261/.466991/.273640/.012245 for three-prong; every value is below1.
Strict-cut enrichment is .7264117/.4410357 from56/34 of100000 against116/150471.
All eight numerator/denominator rows and calculations remain in the new summary.
This is descriptive arithmetic, not a new curve maximum, significance, independent
confirmation or proof that every possible threshold fails. It explains why AUC
cannot support a useful-selector headline. No orientation/cut is retuned.

The [v2 protocol](decisive-scientific-experiment.md) selects ADC2021, one new
12-aggregate object representation, a271-parameter compact AE and1999-parameter
reference with common bottleneck3, PCA3 and fixed-shrinkage Mahalanobis. It tests
efficiency retention and directly measured CPU cost, with protected outcomes,
finite6-neural/2-analytical fits, practical primary0.01/secondary0.001 rates and
explicit calibration/multiplicity uncertainty. It can establish compact retention,
a simple-method advantage, a valid negative result or a precisely identified
inconclusive outcome. It promises no favorable neural result.

Metadata substantively support a680426757 B route, published4million background
and55969/340544 signal counts, a small bounded feature/fit matrix and4GiB worker
RSS on the shared16GB Mac. Counts/dtype/content are not locally accepted yet;
Task0061 has concrete header/custody/group/minimum-count checks, not unspecified
future feasibility research. If they fail, stop with the narrowed source/sample
failure, not a replacement dataset chosen for better scores. Readiness means ready
for that controlled preparation; operational readiness, payload acceptance and
new P4 remain false. Task0061 ends at a full freeze; Task0062 alone unblinds,
measures robustness/cost and reaches the experimentally supported conclusion.
