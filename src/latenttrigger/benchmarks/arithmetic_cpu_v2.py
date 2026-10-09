"""Auditable outward AE bounds under checked finite IEEE arithmetic assumptions."""

import ctypes

import numpy as np
import torch

U32, U64 = 2.0**-24, 2.0**-53
LOW, HIGH = 2.0**-40, 2.0**40
DIMENSIONS = (8, 6, 3, 6)
SSE_OPERATION_CEILING = 32  # 8 subtractions + 8 squares + <=8 reduction additions.


class ArithmeticFailure(ValueError):
    def __init__(self, message, evidence=None):
        super().__init__(message)
        self.evidence = evidence or {}


def round_mode():
    library = ctypes.CDLL(None)
    function = library.fegetround
    function.argtypes, function.restype = [], ctypes.c_int
    value = function()
    if value != 0:
        raise ArithmeticFailure("Supported FE_TONEAREST(0) required.")
    return value


def supported(values):
    values = np.asarray(values)
    magnitude = np.abs(values.astype(np.float64))
    if not np.isfinite(magnitude).all() or np.any(
        (magnitude != 0) & ((magnitude < LOW) | (magnitude > HIGH))
    ):
        raise ArithmeticFailure("Nonfinite or unsupported nonzero exponent band.")


def _nonnegative(values):
    value = np.asarray(values, dtype=np.float64)
    if not np.isfinite(value).all() or np.any(value < 0):
        raise ArithmeticFailure("Finite nonnegative bound operands required.")
    return value


def _outward(value, *, zero_exact):
    value = _nonnegative(value)
    if np.any((value > 0) & (value < np.finfo(np.float64).tiny)):
        raise ArithmeticFailure("Subnormal bound intermediate unsupported.")
    if np.any((value == 0) & ~zero_exact):
        raise ArithmeticFailure("Bound operation underflowed to zero.")
    raised = np.nextafter(value, np.inf)
    result = np.where(zero_exact, 0.0, raised)
    if not np.isfinite(result).all():
        raise ArithmeticFailure("Outward bound overflow; never unlimited permission.")
    return result


def add_up(left, right):
    left, right = _nonnegative(left), _nonnegative(right)
    with np.errstate(over="ignore", under="ignore"):
        return _outward(left + right, zero_exact=(left == 0) & (right == 0))


def mul_up(left, right):
    left, right = _nonnegative(left), _nonnegative(right)
    with np.errstate(over="ignore", under="ignore"):
        return _outward(left * right, zero_exact=(left == 0) | (right == 0))


def sub_down(left, right):
    left, right = _nonnegative(left), _nonnegative(right)
    if np.any(left < right):
        raise ArithmeticFailure("Nonnegative denominator difference required.")
    value = left - right
    if np.any((value > 0) & (value < np.finfo(np.float64).tiny)):
        raise ArithmeticFailure("Subnormal denominator difference unsupported.")
    result = np.where(left == right, 0.0, np.nextafter(value, -np.inf))
    if np.any((result > 0) & (result < np.finfo(np.float64).tiny)) or np.any(
        result < 0
    ):
        raise ArithmeticFailure("Outward denominator underflow unsupported.")
    return result


def div_up(numerator, denominator):
    numerator, denominator = _nonnegative(numerator), _nonnegative(denominator)
    if np.any(denominator <= 0):
        raise ArithmeticFailure("Strictly positive bound denominator required.")
    with np.errstate(over="ignore", under="ignore"):
        return _outward(numerator / denominator, zero_exact=numerator == 0)


def abs_difference_up(left, right):
    left, right = np.asarray(left, np.float64), np.asarray(right, np.float64)
    if not np.isfinite(left).all() or not np.isfinite(right).all():
        raise ArithmeticFailure("Nonfinite compared outputs.")
    with np.errstate(over="ignore", under="ignore"):
        return _outward(np.abs(left - right), zero_exact=left == right)


def dot_up(inputs, weights):
    """Each scalar product and addition rounded outward; never a BLAS dot."""
    inputs, weights = _nonnegative(inputs), _nonnegative(weights)
    if inputs.ndim != 2 or weights.ndim != 2 or inputs.shape[1] != weights.shape[1]:
        raise ArithmeticFailure("Outward dot dimension mismatch.")
    total = np.zeros((len(inputs), len(weights)), np.float64)
    for column in range(inputs.shape[1]):
        total = add_up(total, mul_up(inputs[:, column, None], weights[None, :, column]))
    return total


def sum_up(values):
    values = _nonnegative(values)
    if values.ndim != 2:
        raise ArithmeticFailure("Rowwise outward sum requires matrix.")
    total = np.zeros(len(values), np.float64)
    for column in range(values.shape[1]):
        total = add_up(total, values[:, column])
    return total


def gamma(m, u):
    if type(m) is not int or not 0 < m <= 32 or u not in (U32, U64):
        raise ArithmeticFailure("Unsupported gamma count/unit roundoff.")
    numerator = mul_up(float(m), u)
    return div_up(numerator, sub_down(1.0, numerator))


def magnitude(inputs, weight, bias):
    supported(inputs)
    supported(weight)
    supported(bias)
    return add_up(dot_up(np.abs(inputs), np.abs(weight)), np.abs(bias))


def affine_envelope(previous_error, previous64, weight, bias):
    n = weight.shape[1]
    if n not in DIMENSIONS:
        raise ArithmeticFailure("Unsupported frozen affine dimension.")
    g32, g64 = gamma(2 * n + 2, U32), gamma(2 * n + 2, U64)
    propagated = mul_up(add_up(1.0, g32), dot_up(previous_error, np.abs(weight)))
    rounding = mul_up(add_up(g32, g64), magnitude(previous64, weight, bias))
    return add_up(propagated, rounding)


def local_affine_bound(inputs32, weight, bias):
    n = weight.shape[1]
    return mul_up(
        add_up(gamma(2 * n + 2, U32), gamma(2 * n + 2, U64)),
        magnitude(inputs32, weight, bias),
    )


def assert_bound(actual, reference, bound, name):
    bound = _nonnegative(bound)
    error_upper = abs_difference_up(actual, reference)
    if error_upper.shape != bound.shape:
        raise ArithmeticFailure("Acceptance bound/output shape mismatch.")
    bad = error_upper > bound
    error = np.abs(np.asarray(actual, np.float64) - np.asarray(reference, np.float64))
    ratio = np.divide(
        error_upper, bound, out=np.zeros_like(error_upper), where=bound > 0
    )
    record = {
        "comparison": name,
        "elements": int(error.size),
        "max_absolute_error": float(error.max(initial=0)),
        "max_bound": float(bound.max(initial=0)),
        "max_error_over_bound": None
        if np.any((bound == 0) & (error_upper > 0))
        else float(ratio.max(initial=0)),
        "nonzero_error_at_zero_bound": int(
            np.count_nonzero((bound == 0) & (error_upper > 0))
        ),
        "violations": int(bad.sum()),
        "passed": not bool(bad.any()),
    }
    if bad.any():
        index = tuple(int(v) for v in np.argwhere(bad)[0])
        record["first_failure"] = {
            "index": list(index),
            "actual": float(actual[index]),
            "reference": float(reference[index]),
            "error_upper": float(error_upper[index]),
            "bound": float(bound[index]),
        }
        raise ArithmeticFailure("Arithmetic-aware gate failed: " + name, record)
    return record


def sse_difference_bound(
    inputs, reconstruction_reference, pair_bound, score, reference_score
):
    supported(inputs)
    supported(reconstruction_reference)
    residual = inputs.astype(np.float64) - reconstruction_reference.astype(np.float64)
    if not np.isfinite(residual).all():
        raise ArithmeticFailure("Nonfinite residual.")
    # Exact real residual R is bounded from computed rho by |rho|/(1-u64).
    residual_upper = div_up(np.abs(residual), sub_down(1.0, U64))
    q = add_up(
        mul_up(2.0, sum_up(mul_up(residual_upper, pair_bound))),
        sum_up(mul_up(pair_bound, pair_bound)),
    )
    g = gamma(SSE_OPERATION_CEILING, U64)
    # |Scomputed-Texact| <= g*Texact <= g/(1-g)*Scomputed.
    evaluation = mul_up(div_up(g, sub_down(1.0, g)), add_up(score, reference_score))
    return add_up(q, evaluation), q, evaluation


def trace(model, values, audit, *, double=False):
    captures = {}
    handles = []
    try:
        for name, module in model.named_modules():
            if isinstance(module, (torch.nn.Linear, torch.nn.ReLU)):

                def hook(module, args, output, name=name):
                    captures[name] = (
                        args[0].detach().numpy().copy(),
                        output.detach().numpy().copy(),
                    )

                handles.append(module.register_forward_hook(hook))
        audit[
            "diagnostic_fp64_full_forward_presentations"
            if double
            else "numerical_forward_input_presentations"
        ] += len(values)
        with torch.inference_mode():
            x = torch.from_numpy(values)
            output = model.decoder(model.encoder(x)) if double else model(x)
        return output.numpy().copy(), captures
    finally:
        for handle in handles:
            handle.remove()


def global_envelope(model, traces64, values):
    previous = values.astype(np.float64)
    error = np.zeros_like(previous)
    dimensions = []
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            weight = module.weight.detach().numpy().astype(np.float64)
            bias = module.bias.detach().numpy().astype(np.float64)
            dimensions.append(weight.shape[1])
            error = affine_envelope(error, previous, weight, bias)
            previous = traces64[name][1]
            supported(previous)
        elif isinstance(module, torch.nn.ReLU):
            # Exact max(0,z), 1-Lipschitz; the previous envelope is unchanged.
            previous = traces64[name][1]
            supported(previous)
    if tuple(dimensions) != DIMENSIONS:
        raise ArithmeticFailure("Frozen affine topology/dimensions changed.")
    return error


def local_checks(model64, traces32, audit):
    records = []
    for name, module in model64.named_modules():
        if not isinstance(module, torch.nn.Linear):
            continue
        inputs, actual = traces32[name]
        supported(inputs)
        supported(actual)
        weight = module.weight.detach().numpy()
        bias = module.bias.detach().numpy()
        audit["diagnostic_fp64_local_affine_row_presentations"] += len(inputs)
        with torch.inference_mode():
            reference = module(torch.from_numpy(inputs.astype(np.float64))).numpy()
        supported(reference)
        bound = local_affine_bound(inputs.astype(np.float64), weight, bias)
        records.append(assert_bound(actual, reference, bound, "local_affine/" + name))
    return records
