# Frozen CPU/MPS v1 numerical admission policy

Task0023 introduces an isolated, prospective operation-level engineering policy.
It does not revise [CPU v2](arithmetic-cpu-v2-policy.md) or certify a Metal kernel.
The policy applies only to the frozen155-parameter FP32 AE, two-dimensional
contiguous inputs, the fixed five batch shapes, the pinned PyTorch build, and the
fixed synthetic/real domains checked by the new worker.

## Device semantics and supported assumptions

The installed PyTorch2.14.1 Python MPS APIs delegate synchronization and tensor /
driver accounting to primary native bindings. Build support and availability are
separate facts ([backend documentation](https://docs.pytorch.org/docs/2.14/notes/mps.html)).
The [matching Linear implementation](https://github.com/pytorch/pytorch/blob/v2.14.1/aten/src/ATen/native/mps/operations/Linear.mm)
checks MPS operands and their types and passes the weight's mapped data type into
MPSNDArray matrix multiplication or MPSGraph multiplication and bias addition.
Normal selection is retained; the implementation does not select a native kernel.
Internal accumulation/order details remain unknown. FP32 output dtype alone is
not proof of the following error model.

Admission assumes ordinary binary32 multiply/add or fused multiply-add, a bounded
reduction tree for n products plus bias, no reduced-precision intermediates, no
fast approximations, and exact max(0,z) for ReLU. A conservative m=2n+2 accounts
for n products, reduction, bias and one extra rounding; fusion or a higher-precision
accumulator does not worsen this model. The dimensions8,6,3,6 are model facts,
not parameters selected from observed errors. The same recurrence is algebraically
applicable to these operations on either processor, conditional on their semantics.

This is a supported operation-level contract, not an assertion that all Apple
kernels universally implement a known IEEE accumulation tree. The fixed study and
every real verification independently test actual device affine outputs using
identical captured FP32 layer inputs against CPU FP64 affine diagnostics. All
stored inputs, parameters, activations and diagnostic outputs must be finite;
nonzero values lie within [2^-40,2^40], excluding subnormal/overflow domains.
Reduced-precision errors, unsupported operators, fallback, nondeterminism,
out-of-domain values, local violations or absent device/accounting proof refuse
admission. Passing finite samples supports this scoped engineering assumption;
it does not prove it outside these samples or across other builds/hardware.

`PYTORCH_ENABLE_MPS_FALLBACK=0` and `PYTORCH_MPS_FAST_MATH=0` precede imports.
The [fallback source](https://github.com/pytorch/pytorch/blob/v2.14.1/aten/src/ATen/mps/MPSFallback.mm)
selects error fallback for unset/0; its two unconditional special cases do not
belong to this AE's Linear/ReLU/transfer operations. The
[shader compilation source](https://github.com/pytorch/pytorch/blob/v2.14.1/aten/src/ATen/native/mps/OperationUtils.mm)
interprets0 as safe/precise math. These settings are checked in every process;
there is no public getter for every internal math option. Allocator watermarks,
operator preference and profiling overrides are refused, rather than changed.
See [environment documentation](https://docs.pytorch.org/docs/2.14/mps_environment_variables.html).
No AMP, compilation, quantization, custom operator, CPU fallback or policy search.

## Outward bounds and independent checks

Reuse only the unchanged validated outward primitives of CPU v2: u32=2^-24,
u64=2^-53, gamma(m,u)=m*u/(1-m*u), upward nextafter at each nonnegative FP64
primitive, downward denominators, explicit zero and normality checks. CPU FP64
round-to-nearest is verified. They execute outside measured pairs on CPU.

For the fixed CPU FP64 diagnostic h64 and each affine layer:

```
E0=0
M=|W| |h64|+|b|
E=(1+gamma32) |W| Eprevious+(gamma32+gamma64) M
ReLU is 1-Lipschitz; E is unchanged through it
```

Local device checks use `(gamma32+gamma64)(|W||actual_FP32_input|+|b|)`.
Each CPU and MPS reconstruction must separately satisfy E against h64; their
cross-device/shape discrepancy must satisfy ECPU+EMPS (2E for this policy).
Observed maxima never determine or inflate E. CPU v2's separate per-shape
acceptance remains unchanged; this new route performs its own local checks.

For reconstruction discrepancy bound D and CPU reference residual rho, use
outward R=|computed_rho|/(1-u64), Q=2 sum(R D)+sum(D^2), plus outward
`gamma(32,u64)/(1-gamma(32,u64))*(Sactual+Sreference)` for CPU SSE evaluation.
Both input and returned FP32 reconstruction are cast before subtraction, squaring
and sum. Same-shape separated/public scores use atol=rtol=1e-12, and byte equality
is recorded. Stable relative errors use `abs(error)/max(abs(reference),float64.tiny)`;
zero error reports0, zero bound with positive error is a refusal.

At every shape/window, repeat device reconstruction bit-for-bit, check cached
actual-shape reconstruction, all four strict `score > threshold` decisions versus
the CPU1024 reference with zero mismatches, and all finite outputs/bounds.
Before/after timing, each processor's reference, diagnostic, envelope, input,
FP32 parameter round trip and CPU FP64 thresholds must retain their hashes.
Cross-device byte equality is recorded if obtained, never required.
Diagnostic hooks are removed before warm-up. Synthetic fixtures prove software
behavior only; actual device proof requires the one authorized physical study.

## Execution and accounting

[Synchronization](https://docs.pytorch.org/docs/2.14/generated/torch.mps.synchronize.html)
waits for completion. Reconstruction pre-sync is outside the pair; forward and
completion sync are inside, with no output transfer. CPU postprocessing has
actual-shape reconstructions already on CPU. Public adapter timing retains its
input transfer, forward, output transfer, CPU SSE/decisions and completion sync.
Diagnostic copies and bound evaluation stay outside all pairs.

[Tensor accounting](https://docs.pytorch.org/docs/2.14/generated/torch.mps.current_allocated_memory.html)
excludes allocator cache; [driver accounting](https://docs.pytorch.org/docs/2.14/generated/torch.mps.driver_allocated_memory.html)
includes cache and framework allocations. They are sampled independently of host
accounting, with256MiB/512MiB caps. Metrics overlap on unified memory and are not
summed. CPU device accounting is not applicable. Unknown kernel/Metal version,
GPU cores and thermal facts remain unknown unless directly obtained.
