# Compact particle/set baseline — Task 0009 design v1

**Designed; implementation, training, restoration, reproduction and calibration
pending.** This report freezes one initial design, `particle-set-design-v1`, not
a trained baseline. The [JSON specification](../configs/models/particle_set_baseline_design_v1.json)
has `status: design_only`; existing model/training runners do not support it.
The [budget CSV](../results/tables/final/task0009-particle-set-design-budget.csv)
contains analytic estimates. No real population was read or scored in Task 0009.
See the [handoff](handoffs/0009-particle-set-baseline-design.md) for inspection and
actual validation, and [living memory](project-memory.md) for project direction.

## Evidence and decision boundary

The operational Git checkout is `/Users/matteosgobba/Documents/GitHub/RareGate`,
not a synced ChatGPT project mirror. Base/HEAD is
`06450773e75a4d670c771d154714e0cb4d4d9557`, `main` tracks `origin/main`; the local
tracking ref equals HEAD. This does not verify remote push or hosted CI success.
Only user-authored, untracked `docs/project-memory.md` existed initially; its
content was preserved and updated in place. No applicable `AGENTS.md` was found.
The supplied prompt and initial handoff preceded substantive design work.

Task 0008 report, handoff, configuration, curated history/results and canonical
artifact agree: AE v2 is `8 → 6 → 3 → 6 → 8`, 155 parameters, best 381, stop 396,
restored selection MSE `0.21447598731176187`. Small-file verification checked
scientific hashes, exact FP32 parameter representation/count, the configuration's
sole max-epoch difference, all first 200 history rows and the independent CPU
repeat artifact. The repeat record reports exact parameters/results and zero
test accesses. These checks confirm recorded evidence; no training was repeated.
PCA and both AE generations remain intact. Raw source/store hashing and full
verification were not rerun. Only configuration/manifest metadata were read.

## Bounded comparison: three complete proposed adaptations

[Deep Sets](https://arxiv.org/html/1703.06114v3) supplies shared element transforms
and symmetric reductions, and discusses invariant/equivariant constructions.
Our masked mean and local decoder have their own symmetry proof below; we claim
no universal approximation theorem for eight pooled values and variable
multiplicity. [Energy Flow Networks / Particle Flow Networks](https://arxiv.org/abs/1810.05165)
demonstrates collider representations using particle transforms and pooling.
Its supervised jet studies do not establish an LHCO unsupervised score; this
design does not implement the EFN energy-weighted IRC-safe construction.

[Set Transformer](https://arxiv.org/abs/1810.00825) motivates attention for element
interactions, including inducing-point reductions of attention cost. Candidate C
below is a small attention adaptation, not a reproduction of that architecture.
[Achlioptas et al.](https://arxiv.org/html/1707.02392v3) studies point-cloud
autoencoders and reconstruction distances, including limitations of Chamfer
coverage. Its geometry/results do not establish physics performance here. All
widths, objectives, budgets and choices below are project proposals, chosen
without published signal rankings or any new background/calibration inspection.

All candidates use the frozen four channels, `Nmax=384`, nonempty mask and
observed retained count `n`. Biases are enabled; unspecified additions are absent.
The distance `d` is the weighted residual defined in the selected loss section.

| Candidate | Concrete network and information | Objective, score and symmetry | Budget at B=1, n=Nmax=384 | Decision / reconsideration |
| --- | --- | --- | --- | --- |
| A: pooled event-only AE | Shared 4→16 ReLU→8 ReLU; masked mean gives g∈R⁸. Shared decoder [g,q_j] of width 9→16 ReLU→4 linear. Fixed output query q_j=j/383, j=0…383; no learned query parameters. Generate 384 outputs, first n valid. | Symmetric Chamfer: ½[(1/n)Σ_i min_j d(x_i,y_j)+(1/n)Σ_j min_i d(x_i,y_j)], valid i,j only. Train equal-event mean; same scalar score. Encoder/score invariant; generated output order fixed, not input-equivariant. n is supplied, not reconstructed. | 444 parameters, 1,776 FP32 bytes; 153,600 dense MAC/event. Largest network activation [B,384,16]. Scoring 147,456 distances/event, about 14 arithmetic operations/pair plus min/reductions; [B,384,384] FP64 distance matrix 1,179,648 bytes/event (36 MiB at B=32). A [B,384,384,4] FP64 broadcast is another 4,718,592 bytes/event (144 MiB at B=32). | Reject initial design: tiny event capacity plus arbitrary valid-query prefix, coverage/multiplicity blindness and quadratic score. Reconsider only if fixed event compression becomes necessary and a new correspondence/resource contract is justified. |
| **B: local bottleneck + pooled context AE (selected)** | Shared 4→16 ReLU→8 ReLU; local 8→2 linear; g=masked mean of 8 features; shared [local,g] 10→16 ReLU→4 linear. Distinct particles receive their own two-value code. | Corresponding-particle d, masked mean /n; equal-event training. Output/local code equivariant; g and score invariant. Local code is an intended information path. No matching, generated queries, raw-feature skips or count head. | **478 parameters; 1,912 FP32 bytes; 165,888 dense MAC/event.** Largest activation [B,384,16], 24,576 bytes/event. Scoring 15n scalar arithmetic operations/event under stated convention; no pairwise tensor. | Select for complete correspondence, transparent partial compression and linear full-detector cost. Limit: distributed code 2n+8, weak count sensitivity, global interactions only through 8 learned means. |
| C: one-head attention + local AE | Start B's 4→16→8 encoder. Q,K,V,O each biased 8→8; A=softmax(QKᵀ/√8), valid keys only; h'=h+O(AV), padded rows zero. Then B's local2/mean8/decoder. One head, no dropout, positional input or normalization layers. | Same corresponding-particle objective/score as B. Attention equivariant with consistent masks. Same local capacity/bypass limitations; direct pair interactions before compression. Residual stays inside encoder, cannot directly reach decoder. | 766 parameters, 3,064 bytes; 2,623,488 MAC/event = B+256n+16n². Logits and probabilities each [B,1,384,384] FP32: 589,824 bytes/event, 18 MiB at B=32 each; backward saves additional tensors. Score remains linear. | Reject initial design: about 15.8× B's MAC and quadratic attention for interactions not yet justified. It fits 16 GiB analytically but has greater CPU/softmax/export cost. Reconsider through a new design decision if later evidence identifies an interaction limitation worth this cost. |

A does not use slot-wise MSE. Its queries generate distinct outputs and are
independent of input slots; changing input order does not change q. At equal
distance, minimum value is well-defined; a future implementation would select
the first output/input index for an argmin subgradient and record tie-dependent
gradients. Unequal n/k could use denominators n and k separately, but A specifies
k=n and supplies that count. Duplicated outputs can share a nearest neighbor:
matching does not enforce bijection or independently reconstruct multiplicity.
All collapsed outputs incur coverage loss on a diverse input, but wrong duplicate
frequencies with identical support can have zero Chamfer loss. Exact distance
chunking can keep running minima in both directions and preserve values; training
would also need exact argmin/gradient handling. Assignment would remove some
frequency ambiguity at the cost of a solver (e.g. existing SciPy), an n² cost
matrix and typically cubic assignment work; it is not the selected approach.

All three can fit bounded batches in 16 GiB on analytic tensor sizes. This does
not establish training wall time. A and C add operations beyond small dense
layers; neither deserves that complexity for the first particle baseline.
B's reconstruction can be collapsed or over-generalizing after training; no
architecture guarantees detection sensitivity. Reconstruction of nonconstant
targets discourages a constant predictor, but optimization success remains a
future question. Latent rescaling can be compensated by decoder weights without
changing residuals, so latent norms are not anomaly scores. No latent penalty,
auxiliary head, normalization layer, augmentation or regularizer is added.

## Frozen input and model-input contract v1

Reuse [preprocessing contract v1](preprocessing-contract.md),
[pipeline](preprocessing-pipeline.md), and
[exact configuration](../configs/data/lhco_rnd_v5.json). Inputs:
`X: FP32 [B,384,4]`, `M: bool [B,384]`, B≥1. True means real retained particle.
The ordered channels are:

| Channel | Exact frozen transformation, float64 then one FP32 cast |
| --- | --- |
| 0 | `(log1p(pT/1 GeV) - 1.7563971656024226) / 1.1860427476562252` |
| 1 | `(eta - (-2.3446856614008353e-05)) / 1.4824139450954399` |
| 2 | `sin(wrapped phi)` |
| 3 | `cos(wrapped phi)` |

Read these values at implementation time from the hashed configuration; the
JSON stores its exact object-view snapshot for compatibility, not a fitting API.
Source SHA-256 `5da8fda2ca78edf8fa5acc0af92fcb6a2d464ba7bf0fd75e3944a169b88cecc6`;
preprocessing file-byte SHA-256
`2c11e6a995fd677ac88a4830243bfb7944532e3ef1aa83d1b6389ab9ca802e68`;
split scientific SHA-256
`74a97d8956a4b75d5710d456bc207fdfa9d27569256bafe7b8e72a7891468fea`;
full processed scientific SHA-256
`d12574e90e9ba9dff71e4e796f5004e704bce5d824db98c545a96d2df08e12d2`.
Dev identity remains separately specified in the JSON.

Keep leading min(N_original,384) particles in frozen source-before-cast order:
descending pT, ascending eta, wrapped phi, original slot for ties. Do not re-sort
rounded values. The canonical ragged store retains every physical particle.
Transform retained particles first, then zero-pad. No feature clipping, event
rotation, scale removal, refit, input positions or original-slot embeddings.
The retained count n=ΣM enters only reduction denominators and output validity;
it is not concatenated to a learned layer. Original multiplicity, retained-pT
fraction, physical aggregates and IDs stay in diagnostic/provenance metadata.
Labels, fingerprints and split names never enter model tensors.

## Selected ordered architecture

All Linear operations share weights over particles; weight layout [out,in],
FP32. ReLU is max(0,t), not in-place. Layer order also fixes initialization and
serialized parameter order: weight then bias for e1, e2, local, d1, d2.

| Order / operation | Input → output | Activation / bias | Trainable parameters |
| --- | --- | --- | ---: |
| 0 sanitize with `where(M[...,None],X,0)` | [B,384,4] → X₀ [B,384,4] | None / none | 0 |
| 1 e1 Linear 4→16 | X₀ → a [B,384,16] | ReLU / yes | 4×16+16=80 |
| 2 e2 Linear 16→8 | a → h [B,384,8] | ReLU / yes; padded rows zero after activation | 16×8+8=136 |
| 3 local Linear 8→2 | h → ℓ [B,384,2] | Linear / yes; padded rows zero | 8×2+2=18 |
| 4 masked mean | h → g [B,8] | None; Σ valid h / n | 0 |
| 5 broadcast g, concatenate `[ℓ,g]` | [B,384,2] + [B,384,8] → c [B,384,10] | None / none | 0 |
| 6 d1 Linear 10→16 | c → v [B,384,16] | ReLU / yes | 10×16+16=176 |
| 7 d2 Linear 16→4 | v → Y_raw [B,384,4] | Linear / yes | 16×4+4=68 |
| 8 output mask | Y_raw → Y [B,384,4] | `where(M[...,None],Y_raw,0)` | 0 |
| Total | Output channels have the same order as input | Five biased Linear layers | **478** |

Pooling is `g_b=(1/n_b)Σ_{i:M_bi}h_bi`, n_b∈[1,384]. Accumulate h in FP64 on CPU,
divide in FP64, then cast g once to FP32 for decoding. This avoids large FP32
sum-order differences while keeping dense operators FP32. The FP64 cast/reduce
is part of the initial reference; export support is unverified. No learned
global projection is needed. The global eight values express learned distribution
moments; local two values retain compressed individual particle information.

```text
validate public prefix-mask batch, exact shape/dtype, finite values, n>=1
X0 = where(M, X, 0)                         # channel broadcast of M
a = relu(e1(X0))
h = where(M, relu(e2(a)), 0)
local = where(M, local_linear(h), 0)
g64 = sum_i(float64(h_i)) / int64(sum_i(M_i))
g = float32(g64)
c_i = concatenate(local_i, broadcast(g))    # local first, global second
Y = where(M, d2(relu(d1(c))), 0)
return Y, local, g                         # no matching or generated queries
score(X,M) = residual_mean64(X,Y,M)         # canonical score defined below
```

The public inference contract accepts X,M and returns Y with the same mask,
optionally ℓ and g as diagnostics. `score(X,M)` returns one CPU FP64 value per
event, [B], finite and nonnegative, larger anomalous. No optional output chooses
an alternative score. Dense execution may compute excluded rows; masking removes
their influence and gradients. Gathering valid rows is only an engineering
optimization after equivalence tests, not a change in the loss or input contract.

### Information paths and compression claim

Each target reaches its reconstruction through ℓ_i (2 values) and through its
contribution to g (8 shared values). There is no X_i or h_i decoder skip, count
feature, slot feature, learned query or cross-layer cache accessible to d1.
Distinct outputs follow distinct local codes; equal local codes in the same
event produce equal outputs, an intended compression limitation.

The total real-valued code is **2n+8**, plus the validity/count metadata. At n=384
it is 776 floats versus 1,536 input floats, 50.520833% of channel storage. Input
angular pairs lie on a circle, so the input has about 3n physical degrees of
freedom; 776 versus 1,152 at full cardinality is not 2× physical compression.
At n≤8, 2n+8≥3n; at n≤4 it is even ≥4n. One-particle events can pass essentially
all target information through g. This is a distributed particle autoencoder,
not an event-only eight-value compression. It may reconstruct anomalies too
well; future final evaluation must establish usefulness. No finite-width
continuous-code argument proves that it cannot memorize the finite training set.

The model learns correlations among pT, eta and angular direction within each
particle and learned nonlinear averages of that joint distribution, conditioning
each particle reconstruction on event context. The eight aggregates constrain
only particular global summaries and do not determine this distribution. For
example, globally rotating an event leaves all eight existing aggregates
unchanged but changes its sin/cos particle channels and potentially this score.
That establishes representational information beyond aggregates, not desirable
rotation sensitivity. No claim of rotation invariance, jet-level pair geometry,
IRC safety or signal benefit is made; pair relations are mediated only by g.

## Correspondence, objective and the single canonical score

For each valid particle with input x and reconstruction y, define

\[
d(x,y)=\frac{(x_0-y_0)^2+(x_1-y_1)^2+
\tfrac12(x_2-y_2)^2+\tfrac12(x_3-y_3)^2}{3}.
\]

Channel weights are exactly `[1,1,0.5,0.5]`; denominator 3 is their sum. The
angular pair receives one combined weight rather than two full scalar weights;
this is a fixed modeling choice, not fitted background variance or a physics
metric. Standardized log pT and eta retain their frozen scales. Every retained
particle has equal residual weight, including soft constituents; no pT weighting.

Both input and output cardinalities are n with **the same M**. Reconstruction
correspondence is i→i: y_i is decoded from ℓ_i and shared g. Permuting X,M gives
permuted ℓ,Y, unchanged g, and the same sum of corresponding residuals. This
justifies aligned MSE without rank reconstruction, nearest-neighbor matching,
assignment or canonicalization inside the network. There are no two directed
matching losses; the same valid pairs define both input/output exclusions.

The one canonical score and mathematical event training objective are

\[
s(X_b)=L_b=\frac1{n_b}\sum_{i:M_{bi}}d(X_{bi},Y_{bi}),\qquad
L_{batch}=\frac1B\sum_b L_b.
\]

Optimization uses FP32 network weights/forward, FP64 pooling as above, then
FP64 residual subtraction, squares, weighted sums and means; autograd casts
gradients back through the FP32 forward to FP32 parameters. No AMP. Selection
and inference use exactly the same forward and FP64 residual reductions on CPU.
For each epoch, history aggregates the individual L_b in FP64 over actual
events, divided by the population count, never the number of batches or total
particles. Tail batches use their actual B; each event contributes once to
history. Optimizer updates use each batch's equal-event mean, as standard
minibatch optimization. This does not accidentally reweight the history by
tail-batch size. No terms other than d exist: count penalty weight 0, angular
penalty weight 0, latent penalty weight 0, weight decay 0.

Angular outputs are **unconstrained**. No normalization, atan2, linear phi
residual, zero-norm division or auxiliary circle penalty is used. For unit
predictions the angular contribution before /3 is `1-cos(Δphi)`, continuous
across ±pi. For a prediction of norm r, it is
`0.5*(1+r²-2r*cos(Δphi))`; radial errors already contribute. At r=0 it is 0.5,
independent of direction and finite. A conditional mean may lie inside the
circle; this is a limitation of squared reconstruction, not a physical particle
generator. Input circle tolerance below accounts only for FP32 rounding.

A mean /n avoids a mechanically growing score as more retained particles are
added with the same residual distribution. It can dilute a rare bad particle
in a large event. A sum, max, pT-weighted score or later multiplicity correction
would be a different scientific contract. Replicating every valid particle by
the same factor leaves learned mean context and score unchanged (subject to
384 capacity and roundoff). Changing only some duplicate frequencies changes
context/residual weighting, so frequency information can matter; counts are not
independently reconstructed. Original count beyond 384 and removed particles
are invisible. Truncation and original/retained multiplicities are diagnostics.

Scoring needs X,M and reconstructed Y, per-particle subtraction/squares and
masked reduction. It needs no distance matrix or solver. Reject nonfinite
outputs, loss, gradients or score; do not replace them with zero, infinity or
clipped tails. Extremely large finite FP32 inputs that overflow the FP32 network
are errors. A canonical score is finite for successfully validated finite
forward/reduction results, not a guarantee for every conceivable FP32 magnitude.
PCA/AE SSE definitions remain unchanged; raw magnitudes are incomparable across
these objectives. Lower background loss cannot establish better discrimination.

## Mask, symmetry and future edge-case tests

These are **future implementation acceptance criteria**, not executed neural tests.

| Case | Required behavior / future check |
| --- | --- |
| Valid-particle permutations | At public boundary shuffle only first n entries (prefix remains valid); g and s invariant, ℓ and Y equivariant. Check forward, residuals and input gradients after inverse permutation. |
| General mask permutation | Internal set-kernel boundary may accept holes; consistently permute X,M there to demonstrate mathematical property. Public reader/adapter still rejects a non-prefix mask. No reader contract relaxation. |
| Padding changes | Any finite replacement of excluded X values, including very large finite values, is sanitized before e1. Valid Y,g,s unchanged; padded Y and ℓ exactly zero; padding input gradients exactly zero. Biases on excluded rows do not affect valid losses/pooling. |
| n=1 and n=384 | Both accepted; actual denominator 1 or 384. Document weaker n=1 compression. No assumed minimum observed training count in kernel. |
| Empty / all-padding / B=0 | Reject before divide or optimizer work, consistent with nonempty-event contract. |
| Shapes / dtypes | Require X FP32 [B,384,4], M boolean [B,384], matching B and device, B≥1. Reject integer masks, FP64 implicit cast, wrong width/count, inconsistent shapes and unsupported device. |
| Nonfinite | Reject NaN/inf anywhere in X, including padding, and nonfinite weights/intermediates. Padding invariance is stated for finite changes. Fail visibly; no event dropping. |
| Angular input | Valid sin/cos pairs require abs(sin²+cos²−1)≤2e−6 in FP64. No such requirement on padding or predicted pairs. Do not project or clip inputs. |
| Truncation / pT ties | Loader preserves stored leading prefix, source-before-cast tie order, all-particle diagnostics. Kernel has no rank identities; permuting an already retained set preserves score. Dropped-set changes can change it. Fully equal triplets are indistinguishable; original-slot tie does not supply a learned feature. |
| Repeated particles | Equal x within the same context yields equal ℓ,Y; corresponding residuals repeated in the mean. No argmin/assignment degeneracy. Uniform replication preserves mean if capacity permits; unequal repetition need not. |
| Phi seam | Compare ±(pi−epsilon); angular contribution is `(2/3)*sin²(epsilon)` for otherwise identical unit pairs. Zero-norm and off-circle predictions remain finite under explicit formula. |

Predeclared same-CPU synthetic symmetry tolerances for well-scaled features
(`abs(X_valid)≤10`, abs(weights)≤1) are `atol=1e−6, rtol=1e−5` for FP32 g/ℓ/Y and
`atol=1e−8, rtol=1e−6` for FP64 scores. Pure FP64 formula/reduction checks use
`atol=1e−12, rtol=1e−12`. Padded outputs/gradients require exact zero. Arbitrary
overflow-scale inputs are rejection tests, not parity tests. FP64 pool reduction
order and its FP32 cast still prevent promising bitwise permutation equality.
Any unexplained tolerance failure blocks training; no silent tolerance relaxation.

## Analytic budgets and implementation resource contract

Convention: one dense multiply-accumulate is one MAC (roughly two scalar FLOPs),
including multiplication/addition inside Linear only; exclude biases, ReLU,
casts, pooling, data preparation and validation. Dense reference evaluates all
384 rows. Per event:

```text
MAC = Nmax*(4*16 + 16*8 + 8*2 + 10*16 + 16*4)
    = 432*Nmax = 165888 at 384
parameters = (4+1)*16+(16+1)*8+(8+1)*2+(10+1)*16+(16+1)*4
           = 478; parameter bytes = 4*478 = 1912
```

There are additionally 46Nmax bias additions, 40Nmax ReLU comparisons and
masking; context pooling has about 8n additions/divisions plus count reduction.
Scoring d costs 4 subtractions+4 squares+2 half multiplications+3 additions+
1 divide per particle =14n operations; sum/mean adds n−1 additions+1 divide:
**15n**, 5,760 at n=384. Mask/count/finite checks and casts are separate. No n²
tensor exists for selected forward or score. A packed valid-only implementation
can replace Nmax by n in dense work after parity; current budgets assume padding.
With local width l and pooled width g=h, dense MAC is
`Nmax*(4*16+16*h+h*l+(l+g)*16+16*4)`, linear in Nmax and these widths.
Storage and per-batch compute scale linearly in B; residual cost scales with n.

| Quantity at Nmax=384 | B=1 | B=32 (training/scoring) | Assumption |
| --- | ---: | ---: | --- |
| FP32 input / reconstruction bytes, each | 6,144 | 196,608 | 4BNmax×4 |
| Boolean mask bytes | 384 | 12,288 | 1 byte/element |
| Local latent bytes | 3,072 | 98,304 | 2BNmax×4; valid-code capacity is 2n |
| Global FP32 context bytes | 32 | 1,024 | 8B×4 |
| Largest network tensor bytes | 24,576 | 786,432 | [B,384,16], 0.0234375 / 0.75 MiB |
| Concatenated decoder input bytes | 15,360 | 491,520 | [B,384,10] materialized; broadcast g itself a view |
| Dense Linear forward MAC | 165,888 | 5,308,416 | 432BNmax |
| Score arithmetic ops at n=384 | 5,760 | 184,320 | 15Bn, excludes checks/casts |
| FP64 residual, each of residual/square buffers | 12,288 | 393,216 | [B,384,4]×8 |
| FP64 event scores bytes | 8 | 256 | [B]×8 |
| Training tensor inventory estimate bytes | 129,840 | 3,857,280 | Formula below; 0.123825 / 3.678589 MiB |
| 4× working tensor planning envelope bytes | 519,360 | 15,429,120 | Inventory ×4; 0.495300 / 14.714355 MiB |

The training inventory is an approximate allocation inventory, not measured
autograd peak: seven FP32 arrays X₀,a,h,ℓ,c,v,Y total `240BNmax` bytes;
FP64 residual and square buffers `64BNmax`, per-particle d `8BNmax`, boolean mask
`BNmax`, pooled context/count/score `48B`, and 9,600 fixed bytes. Fixed bytes
include FP32 parameters, gradients and two Adam moments (4×1,912=7,648), ten
FP32 Adam step scalars (40), one per parameter tensor, and one best-weight snapshot (1,912). Pool casts,
preactivation/ReLU saves, reduction temporaries, activation gradients, input
copy, Python, allocator, BLAS workspace, reader pages and optimizer bookkeeping
are omitted; some listed buffers may alias or be unnecessary. Formula
`313BNmax+48B+9600` is a planning estimate, not an implementation guarantee.
The 4× envelope explicitly allows several copies; only measured gate results
can establish peak RSS. FP64 pool conversion [B,384,8] is 24,576 / 786,432 bytes,
the same bytes as the largest FP32 hidden tensor, covered by envelope headroom.

CPU training backward is estimated at approximately two additional dense
forward passes. Full train+selection epoch therefore has about
`3*699957*165888 + 74749*165888 = 360743362560` MAC before view loading, reductions
and optimizer overhead. This is ~0.361 trillion MAC/cycle, substantially larger
than the aggregate AE; its historical seconds cannot forecast this workload.
Canonical batches: train 21,874 with tail 21; selection 2,336 with tail 29.

On the 16 GiB development machine require measured working tensors/workspace
≤512 MiB and **process peak RSS ≤6 GiB**, including verification/mmap pages.
Reserve at least 4 GiB for OS/other apps and 6 GiB for headroom/page-cache/runtime
variation. Gate on free available memory ≥8 GiB before launch; stop if process
RSS exceeds 6 GiB or system available memory falls below 4 GiB. These are chosen
safety ceilings, not observed usage. Stream at most 32 padded events; no padded
population cache, no full-particle tensor or persistent reconstruction arrays.
Allowed source IDs/shuffle indices and compact FP64 score vectors may be held
in memory (all three background score vectors together 6,796,232 bytes).

Likely portable operators: Linear, ReLU, where, concatenate, broadcast, sum and
division with a nonempty denominator. Fixed [384,4] simplifies shape routing.
FP64 pooling/scoring, boolean masks and reduction semantics need backend audits;
later FPGA reductions/division and FP64 costs may be obstacles. No export library
was installed, export created, backend support demonstrated or latency measured.
Any lower-precision reduction is a separately identified future runtime variant.
No trigger-readiness, hardware speedup or physical rate follows from this budget.

## Future training, convergence and resource gate (preregistered v1)

**Task 0009 authorizes none of these executions.** Initial choices are fixed
without search; 32 events means 12,288 padded particles/update, keeping many
small operations bounded, while 200 epochs caps a materially larger CPU job.
Eight context and two local coordinates balance distribution context with
limited per-particle capacity. They do not imitate the aggregate AE's latent3.

| Setting | Fixed initial contract |
| --- | --- |
| Seeds / initialization | Python, NumPy, PyTorch 1729. Separate CPU shuffle generator seeded 1729 once per run. Construct e1,e2,local,d1,d2 in that order; each weight and bias uniform U(−1/√fan_in,+1/√fan_in), PyTorch Linear default, FP32. No reseeding between epochs/layers. |
| Optimizer | Adam lr=0.001, betas=(0.9,0.999), eps=1e−8, weight_decay=0, amsgrad=False, maximize=False, foreach=False, fused=False, capturable=False, differentiable=False, decoupled_weight_decay=False (if version supports the option; otherwise ordinary Adam weight_decay=0). No schedule, clipping, accumulation or warmup. zero_grad(set_to_none=True). Record exact runtime version/options. |
| Batches / order | Batch32, workers0, no pinning/prefetch pool, drop_last=False. Uniform permutation of every train event once/epoch, without replacement; start from allowed IDs in source-ordinal order. Selection/score batches32 in source-ordinal order. Tail uses actual size. Shuffle uses a dedicated generator advanced across epochs, never a data- or loss-dependent shuffle. |
| Precision / device | CPU only; network/parameters FP32, pool FP64→FP32, loss/selection/score FP64; FP32 parameter gradients/Adam state. No AMP/MPS fallback. One intra-op and one inter-op thread in a fresh canonical subprocess, deterministic algorithms True (warn_only=False); record thread and BLAS environment. Restore caller RNG/settings or use isolated process. |
| Populations / event weighting | Full 699,957 train background for fitting; full 74,749 selection background for stopping. L_batch equal mean of L_b; history equal event mean. Calibration absent from optimizer/stopping APIs. No labels. |
| Checkpoint selection | After each complete epoch score full selection using the canonical FP64 score; select mean s. Strict improvement `metric < best - 0.0`; min_delta=0; exact ties retain earliest best and increment bad_epochs. First finite epoch becomes best. Patience20 consecutive failures; maximum200 epochs. Clone complete best FP32 state on each improvement. |
| Stop / restoration | Patience wins if reached at epoch200; otherwise cap gives **convergence unresolved**. Restore best, serialize, compare parameter bytes and independently reload/re-score selection. Require exact same-environment per-event score bytes/mean and best record under same batching/thread policy. Failure blocks freeze/calibration. |
| Reproduction / provenance | Independent fresh CPU rerun from initialization, same seed/order/config/store; require exact history, selected epoch/stop, parameter bytes, scientific identities and score-byte hashes. Investigate mismatch; no tolerance relaxation for canonical same-environment reproduction. Record environment, base/dirty code hashes, access, result/file hashes and resource limits separately. |

Before any full run in a future authorized implementation task, gates are:

1. **Synthetic correctness:** the mask/symmetry/gradient/cardinality/objective,
   guard, parameter-order, persistence and stopping tests below all pass.
2. **Bounded dev/resource gate:** separate disposable model, only first 1,024
   source-ordered `train_background` IDs within frozen dev subset, batch32,
   at most three complete passes /96 optimizer steps and one forward scoring
   pass on those same 1,024. No selection, calibration, tests or signals read.
   Fresh-process whole gate ≤300 s, working memory ≤512 MiB, RSS ≤6 GiB.
   Separately record loading, updates and no-grad forward times and RSS.
   Conservative predicted full train+selection cycle is
   `2*(699957*t_train_pass/1024 + 74749*t_score_pass/1024) ≤180 s`, using the
   maximum of the three train-pass times and including batch view preparation.
   Factor2 supplies headroom for locality/scale effects; this is a feasibility
   estimate, not latency evidence. No required loss decrease on this tiny sample
   is used to select architecture or hyperparameters. Nonfinite operations fail.
3. **Authorized canonical training:** a future task may start only after those
   gates and compatibility checks pass. Initial full epoch cycle must actually
   finish ≤180 s; every later cycle has a 180 s ceiling (interrupt if exceeded).
   Per-run fitting+selection wall ceiling 10 h, max200 epochs. Separate restore/
   reproduction/freeze/postfreeze background stage ≤1 h per run, ≤22 h total for
   two complete canonical repetitions; maintain memory ceilings throughout.
4. **Restoration/reproduction → freeze → calibration:** required in that order.
   Gate failure blocks every dependent stage. Resource/epoch ceiling without
   patience leaves convergence unresolved; retain failure metadata and history,
   do not publish a finalized baseline or access calibration. A new bounded,
   versioned decision must precede horizon/batch/device/model changes.

No automatic fallback device, batch adjustment, partial-population canonical
fit, resume, hyperparameter search or silent extension. The design is resource
plausible analytically, but full CPU feasibility is explicitly unverified.

## Future calibration and descriptive background diagnostics

After restoration, exact reproduction and freeze, use
`validation_calibration_background` (74,823), existing
[evaluation protocol](evaluation-protocol.md): targets 0.1,0.05,0.01,0.001;
`higher` quantile; accept iff score>threshold. Check frozen thresholds on
selection (74,749); do not retune on selection or test. Reuse `score_summary`,
`ks_distance`, `calibrate_thresholds`, `background_operating_point` for counts,
linear summary quantiles, min/max/tails, mean/ddof0 std, ECDF KS distances,
accepted totals, resolutions, absolute/signed relative FPR deviations, Wilson95
and zero-acceptance exact one-sided bound. No AUC/AP/signal efficiency now.

Predeclare descriptive score and acceptance profiles versus retained count,
original count, truncation flag/retained-pT fraction, full-event scalar pT,
maximum pT and existing massless event mass. For continuous variables use ten
equal-count bins whose edges come only from postfreeze training diagnostics
(linear quantiles); keep tied edges merged, overflow tails retained and report
empty/merged bins. Multiplicity also uses these train-defined bins; truncated
flag is two groups. Transfer those edges unchanged to the other backgrounds;
show counts, mean/median/p99/max score and frozen-threshold rates/intervals.
These are descriptive dependencies, not bias-removing transformations.

Selection participated in early stopping and is not an untouched model-validation
sample. Calibration is untouched by model selection until freeze, then used for
threshold estimation; it is not an independent threshold-validation sample.
No additional untouched background population is created. Report that limitation
and finite calibration tail support (~75 events at target1e−3). None of these
postfreeze diagnostics may choose dimensions, loss weights, score components or
normalization in the same run. Any changed model needs a separate versioned
protocol and disclosure of previously inspected populations. Preserve tails.
No thresholds, distributions or diagnostics were computed in Task 0009.

## Minimal Task 0010 implementation specification and acceptance

Proposed next **Task 0010 — Compact Particle/Set Baseline Implementation and
Background Validation**, subject to the live index and resource gate. It is not
executed automatically. No framework rewrite or dependency change is needed.

- `models/particle_set.py`: design-version validator, input validator, ordered
  five-layer module, `encode(X,M)->(local,g)`, `reconstruct(X,M)->Y`,
  `event_loss(X,Y,M)->[B]` with differentiable FP64 reductions,
  `score(X,M)->float64[B]`, artifact/load compatibility checks. Existing runners
  must reject design-only JSON; a separately versioned executable config records
  its relation to this design after implementation approval.
- `training/particle_set.py`: bounded train/selection iterators and existing
  `EarlyStopping` semantics (patience20), deterministic context/fresh subprocess,
  FP64 event history, resource checks, best restoration and independent reload.
  No calibration argument to the fit API.
- `models/particle_background.py`: particle loading, access audit, staged outputs,
  sequential streamed scoring and common evaluation functions after freeze.
  Reuse established `BACKGROUND_ROLES`, permissions and provenance functions;
  do not call `load_background_features` and call its aggregates particles.
- Reader routing: keep one verified `ProcessedStore` open (its constructor
  verifies fully; do this once in the future run). Before opening/reading, loader
  rejects every forbidden/unknown population and truth option; fitting gate
  additionally allows train only. Record request purpose/representation/count
  before reads and update counts after each batch, preserving failed audits.
  Obtain allowed source IDs once. Sequential score/dev views can use guarded
  `iter_batches` or `read_ids`; each returns an `EventBatch`, then
  `model_view(nmax=384)`, then owned X,M tensor batch. Exclude metadata at the
  model boundary; retain it only for audits/diagnostics.
- Canonical shuffle: minimally extend processed batch iteration with an optional
  verified permutation of split-relative positions, validating membership and
  `_positions`/truth guard **once** before batch particle reads and using existing
  bounded `_batch` logic. This is a future interface; it is not supported today.
  Require every permitted position exactly once/epoch, integer permutation,
  batch≤32 and tail retained. Calling current `read_ids` for each shuffled batch
  remains correct but repeats a full split-mask calculation per call; include
  that cost if used. Never weaken guards or use unaudited direct memmap slicing.
- Meaningful synthetic tests: numeric d and batch/population mean; equivariance,
  invariance and padding gradients; shape/dtype/empty/nonfinite/circle failures;
  n1/n384/ties/truncation/seam/repeats; analytic count and layer/parameter order;
  hostile population refusal before store construction/read; calibration absent
  before freeze, full coverage/shuffle/tail; controlled loss sequences for strict
  tie/patience/cap/restoration; corrupt parameter/config/identity/load rejection;
  resource failure blocks training/calibration. Real views enter only dev gate.

Future artifact is a new model type/version, transparent JSON with exact FP32
values in ordered `e1.weight,e1.bias,e2.weight,e2.bias,local.weight,local.bias,
d1.weight,d1.bias,d2.weight,d2.bias` and shapes `[16,4],[16],[8,16],[8],[2,8],[2],
[16,10],[16],[4,16],[4]`. Scientific content includes full architecture,
model-input/design/executable-config versions, channel order, masks/pooling,
cardinality/correspondence/angular/loss/score semantics and precision, all ordered
parameters, source/config/processed/split identities, canonical-full versus dev
scope, training configuration, selected state/history identity, fitting/selection
counts and stop rule/outcome. Hash canonical JSON using existing `content_hash`;
a design hash contains no trained weights and is not a model hash. Calibration
results bind the frozen model/config/store and score contract separately.
Build UTC, paths, engineering chunking/timings and peak RSS stay outside scientific
identity; deterministic training batch/order/seed remain inside it.

Validate scientific hashes, FP32 roundtrip/finite values, exact names/order/shapes,
478 count, versions, source/schema/channels/scalers/Nmax, split identity/counts,
scope and training success before accepting a model. Refuse mismatches rather
than casting/refitting or silently migrating. Models/checkpoints/score arrays,
logs and large outputs remain ignored local data; a new tiny curated model path
requires an explicit narrow artifact-policy decision in Task 0010. No exception
was added now. Final test gate remains separately authorized and does not gain
particle support in this design task.

## Design validation actually performed

Standalone synthetic scalar/array arithmetic only; no trainable network or loop.
The checked JSON supplies widths/weights/protocol and exact frozen scalers.
Analytic layer shapes/counts, both budget batches/units, per-epoch/tail arithmetic
and report/JSON/CSV agreement were checked. Hand cases include:

| Case (valid angular inputs; unspecified channels identical) | Expected s |
| --- | ---: |
| One particle, exact reconstruction | 0 |
| One particle, only standardized pT residual 1 | 1/3 |
| Two particles, pT residuals 1 and 0 | 1/6 |
| Same two, additional finite padded values | 1/6 |
| One particle, unit opposite angular directions | 2/3 |
| One particle, predicted angular pair (0,0) | 1/6 |
| One particle, predicted angular pair twice the target | 1/6 |
| Seam phi=±(pi−0.001) | `(2/3)*sin²(0.001)` ≈6.6666644444447e−7 |
| Reorder corresponding valid x,y pairs | Same s and mean h |
| Uniformly replicate valid pairs within capacity | Same s and mean h |
| Events with n1 score1/3 and n2 score1/6 | Batch/event mean1/4, not pooled-particle mean2/9 |

Formula checks also reject zero n and demonstrate full384 exact reconstruction.
They prove arithmetic consequences, not neural implementation behavior. Actual
gradient exclusion, initialization/shuffle, overflow rejection, runtime parity,
restoration and resource behavior remain future tests. Preregistration fields,
relative documentation links, current-state wording, intended-file scope,
historical preservation and whitespace were reviewed; outcomes recorded in the
handoff. Full pytest/training/store checks were not warranted or rerun.

## Access audit and limitations

Task 0009 real model/evaluation requests: train=0, selection=0, calibration=0,
test_background=0, test_signal=0. No reader instantiated, no raw/NPY particle or
label array opened, no model forward/fit/score performed. Existing reports,
small artifacts, config and manifest JSON establish the design inputs; synthetic
arithmetic establishes formulas. No signal-derived selection or new calibration.

```text
test_background model/evaluation accessed: NO
test_signal model/evaluation accessed: NO
```

The retained-set truncation, equal-particle mean dilution, unconstrained angular
outputs, absent independent multiplicity reconstruction, limited pooled context,
local bypass capacity and small-n compression remain explicit limitations.
CPU feasibility/convergence and anomaly sensitivity are unknown. The next gate
must test implementation correctness and resources before canonical training;
neither a design-only specification nor a favorable analytic budget authorizes
Task 0010 execution or test access.
