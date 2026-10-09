# Arithmetic CPU v2 — derivation and supported assumptions

This Task0022 engineering policy changes numerical acceptance only. Frozen PCA/AE
weights, input/scaler/features, eager operators, precision, strict calibrated
thresholds and timing scopes remain unchanged. It does not pass historical v1.
The policy source is [arithmetic_cpu_v2.py](../src/latenttrigger/benchmarks/arithmetic_cpu_v2.py).
This document and executable policy are frozen before any real campaign.

## Standard model and scope

Use `fl(z)=z(1+delta)`, `|delta|<=u`, round-to-nearest IEEE binary32/binary64,
without overflow/underflow in the numerical operations covered. A product of at
most m rounding factors differs from1 by at most `gamma_m=m*u/(1-m*u)`.
This standard model and summation error analysis are described by
[Higham, The Accuracy of Floating Point Summation, 1993, sections1–3](https://nhigham.com/wp-content/uploads/2023/10/high93s.pdf).
Ordering and cancellation affect computed sums; a worst-case bound is not a
measurement of error. [PyTorch numerical accuracy](https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html)
also distinguishes batched and sliced arithmetic. Specific native kernel/order
attribution remains unverified. The runtime/build is pinned, effective threads
queried, FE_TONEAREST(0) checked on the supported Darwin/CPU implementation, and
local affine checks are mandatory. This is not a universal backend certificate.

`u32=2^-24`, `u64=2^-53`. Frozen affine input dimensions are8,6,3,6. Set
`m=2*n+2`: n products, at most n accumulation/bias additions, and two additional
rounding sites cover alpha/beta-style affine output handling. FMA/fewer rounding
sites do not require a larger bound. Arbitrary extended accumulation trees,
low precision products, approximate operators and different build/settings are
outside the bound's assumptions. Local comparisons test those assumptions on
every frozen sample row; they cannot prove a backend implementation universally.

A checked support band excludes underflow/overflow rather than silently ignoring
it: every nonzero stored input/parameter, actual affine input/output and FP64
reference activation must have magnitude in `[2^-40,2^40]`; zero is permitted.
For FP32 operands in this band their exact significands lie on a lattice no
finer than2^-63. Exact products/partial sums lie on a lattice no finer than2^-126,
the minimum normal FP32 magnitude. Each product is at most2^80; no affine sum
of at most8 products plus bias reaches FP32 overflow (upper magnitude<2^84).
Zeros from cancellation are exact zeros; nonzero exact partial sums cannot be
subnormal. The FP64 reference path has much wider exponent room: its smallest
possible product lattice spacing here is2^-155, far above2^-1022. Checked
intermediate activations permit the argument to be applied at every layer.
Violations of this scope stop acceptance; inputs are not clipped or altered.

The outward policy arithmetic is FP64 and nonnegative. Each primitive rejects
nonfinite/overflow, subnormal intermediates and a nonzero operation rounded to
zero. Exact-zero add/product cases retain zero. Positive products/sums in this
bounded scope, gamma/envelopes/Q and allowances stay normal or exactly zero;
unsupported tiny bound intermediates are refused. No flush-to-zero setting is
changed. Bound inputs beyond the supported band do not receive an absolute
underflow allowance or automatic exception.

## Outward evaluation

Nonnegative addition/multiplication/division performs one elementwise FP64
operation then `nextafter(result,+infinity)`; a downward denominator difference
uses one subtraction then `nextafter(result,-infinity)`. Magnitudes of finite
stored floats are exact. Gamma uses an upward numerator and downward positive
`1-numerator` denominator. Every n-term dot/sum uses separately upward products
and upward accumulation after each term; **no BLAS dot** is used for bounds.
The gamma factor, `1+gamma`, sums, recurrence products and pair factor2 each use
these primitives. A final nextafter following a multistep dot would be insufficient.
Observed differences use outward absolute subtraction. Tests independently use
exact rational fixtures for primitives, gamma, complete recurrence and SSE.

## Reconstruction and local affine bounds

Let `h64` be the fixed computed FP64 diagnostic path using exact stored FP32
parameter values promoted to FP64. It is rounded arithmetic, not exact truth or
a new canonical model. For an affine layer, let
`M=|W|*|h64_previous|+|b|` and let E bound the difference between the FP32 and
computed FP64 incoming activations. Ordinary rounding bounds give:

- Input perturbation: `|W|*E`.
- FP32 affine rounding: `gamma32*(M+|W|*E)`.
- Fixed FP64 affine rounding: `gamma64*M`.

Thus starting `E0=0`,
`E_next=(1+gamma32)*|W|*E+(gamma32+gamma64)*M`.
All terms are evaluated outward. ReLU is `max(0,z)`, is1-Lipschitz and needs no
amplification; it propagates E unchanged, even if a sign changes. Check the
actual FP32 full1024 and every actual-B reconstruction against `h64` with E,
then their difference with the common pair envelope `D=2*E_output`.

Local affine checks compare each actual FP32 affine output with FP64 evaluation
on its **identical stored FP32 layer inputs**. Here E0=0 locally, so the bound is
`(gamma32+gamma64)*(|W|*|actual_input32|+|b|)`. Actual-B layer traces are concatenated
in bounded memory, then local FP64 diagnostics are evaluated as1024 rows. The
FP64 path's own rounding is covered by gamma64 regardless of its batch shape.
Every row/channel is checked; no subset or favorable-run selection. Tracing and
local FP64 work are outside timings, with hooks removed after each forward.

## Canonical FP64 SSE

FP32 input/reconstruction casts to FP64 are exact. Let real residual `r=x-y_ref`
and reconstruction difference d satisfy `|d|<=D`. Exact algebra gives
`S_actual_exact-S_ref_exact=-2*r*d+sum(d^2)` and therefore
`Q=2*sum(|r|*D)+sum(D^2)` bounds its magnitude.

The canonical computed residual `rho=fl64(x-y_ref)` is not assumed exact:
`|rho-r|<=u64*|r|`, hence `|r|<=|rho|/(1-u64)`. Evaluate that magnitude bound
and all products/reductions of Q outward. Checked FP32 operand lattice/bands
exclude residual and square underflow; all positive squares/sums stay normal.

For an eight-channel score there are8 subtractions,8 squares and at most8
reduction additions (including a zero initializer): at most24 rounding sites.
Each residual rounding enters its squared term twice, but any root-to-term
factor path is at most `2+1+8=11`, also below32. `gamma_32(u64)` is a fixed,
conservative operation-count ceiling covering both total operations and squared
residual factor paths, not a fitted epsilon/error multiplier. Nonnegative sums
permit an error bound relative to exact score T:
`|S_computed-T|<=g*T`, where `g=gamma_32(u64)<1`.
Converting exact to observed scale, `T<=S_computed/(1-g)`, so
`|S_computed-T|<=g/(1-g)*S_computed`.

The final across-shape score envelope is outward
`Q + g/(1-g)*(S_computed_actual+S_computed_reference)`.
Both evaluation errors and Q evaluation are included. Zero scores give zero
score-scale allowance; exact-zero operations do not manufacture slack. Public
canonical SSE stays untouched; this bound verifies, never replaces, its output.

## Independent gates

Finite values/bounds, supported arithmetic scope and local affine checks are
mandatory. Same-shape separated/public SSE retains `atol=rtol=1e-12`, with
byte-exact repeated reconstruction/score and full-reference pre/post hashes on
the identical supported runtime. All four frozen strict `score>threshold`
decisions must agree on every1024row/grid pre/post timing, independently of a
passing envelope; ties remain rejected. PCA retains1e-12/1e-12 reconstruction/
score checks and never receives the AE envelope. Parameter/input/threshold
mutation vetoes completion. A failure is preserved, not retoleranced or replayed.

Conservatism must be reported as observed-error/envelope ratios separately from
actual error maxima. Sample decision agreement does not establish universal
runtime equivalence, calibration FPR, test acceptance, discrimination or speedup.
