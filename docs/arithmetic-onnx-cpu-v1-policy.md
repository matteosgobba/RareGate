# Frozen AE ONNX CPU v1 equivalence policy

Task0024 adopts an isolated prospective **operation-level engineering contract**
for the audited155-parameter FP32 `8→6→3→6→8` reconstruction graph. It does not
revise CPUv2, MPS criteria, canonical model/score/calibration or scientific training.

## Exported operations and CPU provider assumptions

The [ONNX Gemm specification](https://onnx.ai/onnx/operators/onnx__Gemm.html)
defines matrix multiplication plus bias, including explicit transpose/alpha/beta
semantics. [MatMul](https://onnx.ai/onnx/operators/onnx__MatMul.html) plus Add and
parameter Transpose can represent the identical affine stages. Audit requires
four affine stages with exact original FP32 weights/biases (155scalars), two
ReLUs, width8 and dynamic batch; no reduced precision, unexpected constants,
custom invoked operators, scaler, score or external weights. Identity/layout
nodes must have exact explicit mappings. The actual graph is acceptance evidence.

[ONNX Runtime session APIs](https://onnxruntime.ai/docs/api/python/api_summary.html)
allow CPU-only provider, sequential execution, intra/inter-op1, optimization
disabled and fallback disabled; effective values/providers are checked. Available
CoreML/Azure providers do not mean selection. Installed runtime/build/API identities
are recorded. Specific MLAS/Accelerate kernel trees remain unknown. CPU execution
and FP32 outputs alone are not a proof of internal accumulation semantics.

The supported assumption is ordinary binary32 products/additions or FMA, bounded
reduction trees, no reduced precision, no fast approximations, and exact max(0,z)
ReLU. Fusion or wider accumulation does not worsen the bound. Nonzero stored
inputs, parameters, actual affine inputs/outputs and diagnostic activations must
lie within [2^-40,2^40], avoiding underflow/overflow lattice domains. Exact normal
FP32 parameters are promoted to CPU FP64 diagnostics. CPU FE_TONEAREST is checked.
No clipping, runtime tuning, observed-error multiplier or tolerance/opset search.

The proof is conditional on this scoped operation contract. It is supported by
actual graph/parameter/provider evidence, rational software tests, fixed synthetic
families and **mandatory local checks on each actual runtime affine input**;
it is not a universal native-kernel or unseen-input certificate. Missing support,
nonfinite/out-of-domain values, parameter mutation or nondeterminism fail closed.

## Outward propagation and independent gates

Reuse unchanged validated CPUv2 outward primitives only, with nextafter upward
at each nonnegative FP64 product/add/division, downward positive denominators,
explicit zeros and refusal of nonfinite/subnormal bound intermediates. Per-term
outward dot/sum replaces a BLAS result with one final ulp. u32=2^-24,u64=2^-53,
gamma(m,u)=m*u/(1-m*u); for n=8,6,3,6 choose m=2n+2 (products/reduction/bias plus
one extra rounding). The operation count follows the audited affine topology.

For fixed rounded FP64 diagnostic activations h64 and exact promoted weights:

```
E0=0
M=|W||h64|+|b|
Enext=(1+gamma32)|W|Eprevious+(gamma32+gamma64)M
ReLU is 1-Lipschitz; E is unchanged
```

Every PyTorch/ORT shape separately satisfies E against the same diagnostic.
Pair reconstruction bound D=Etorch+Eort=2E includes rounding of both FP32 paths
and the rounded FP64 diagnostic reference. Local affine bounds use actual captured
FP32 inputs: `(gamma32+gamma64)(|W||input32|+|b|)`, not idealized upstream inputs.
The diagnostic FP64 network is neither exact real arithmetic nor a new model.

An ignored diagnostic ONNX copy exposes intermediate outputs; the primary artifact
remains immutable. Its final output must be byte-identical to the primary session
for each same-shape invocation before intermediate tensors are used. Exact ReLU
is independently checked. Additional diagnostic outputs may affect internal
execution; measured final agreement supports these samples, not all kernel details.

Canonical score stays external on CPU: convert **both** FP32 input/reconstruction
to FP64 before subtraction, square and sum eight residuals. For reference residual
rho computed in FP64, outward R=|rho|/(1-u64) and Q=2sum(RD)+sum(D²), plus outward
`gamma(32,u64)/(1-gamma(32,u64))*(computed_Sort+computed_Storch)` bounds score drift.
The32-operation ceiling includes both evaluations, not a decimal fitted epsilon.

Independent required gates: finite/supported values and bounds; exact initializer /
source/input/threshold/export identities; byte-exact same-runtime same-shape
repeatability; separated/runtime-adapter SSE atol=rtol=1e-12 (record exact bytes);
cross-runtime reconstruction/SSE propagated bounds; zero strict `score > threshold`
mismatches against the canonical PyTorch1024 reference at all four frozen thresholds.
Cross-runtime byte equality is recorded if obtained and is not required.
Relative errors use `abs(error)/max(1,abs(reference))` solely as a stable descriptive
statistic; bound admission never uses that denominator.

Fixed synthetic families from Task0021 and every window of batch1/8/32/128/1024
precede any real array opening. Real verification covers1193windows/5120row-window
presentations and1024unique reused rows. Supported numerical/decision failures
are retained and aggregated across the complete grid; critical integrity/resource /
nonfinite failures stop. No failed family admits real work, and no failed real
comparison becomes accepted. Initial/final full references, hashes, parameters,
thresholds and immutable primary export are rechecked. No speed measurements.

## Export semantics and source consultation

Installed [PyTorch2.14 export API](https://docs.pytorch.org/docs/2.14/onnx.html)
is verified: single explicit `torch.export.export(strict=False)` capture using a
synthetic `[8,8]` example and dynamic batch1…1024; then modern `dynamo=True`,
opset18, included weights, no external data, `optimize=False`. No removed
`fallback` option or legacy retry. Decomposition, lowering and constant folding
may still happen; optimize=False does not claim to disable constant folding.
The graph audit, not requested flags alone, decides admissibility.
