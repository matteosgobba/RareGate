"""Shared-event integer moments and conditional bounds; no significance API."""

import math
from fractions import Fraction
from statistics import NormalDist

from latenttrigger.research.controlled_activation import protocol as p

ELIGIBILITY = (
    "source_accepted",
    "models_complete",
    "pairing_accepted",
    "thresholds_frozen",
    "lifecycle_accepted",
    "iid_justified",
)


class Patterns:
    """Bit0=N1729,bit1=L1729,...; Python integer counts cannot overflow."""

    def __init__(self, counts=None, *, order=p.ORDER, denominator=None):
        p.require(tuple(order) == p.ORDER, "Fixed six-candidate order")
        self.counts = [0] * 64 if counts is None else list(counts)
        p.require(
            len(self.counts) == 64
            and all(type(x) is int and x >= 0 for x in self.counts),
            "64 exact nonnegative integer counts",
        )
        if denominator is not None:
            p.require(
                type(denominator) is int and denominator == sum(self.counts),
                "Source event denominator",
            )

    @property
    def n(self):
        p.require(
            len(self.counts) == 64
            and all(type(x) is int and x >= 0 for x in self.counts),
            "Aggregate mutated to invalid counts",
        )
        return sum(self.counts)

    def add(self, decisions, *, order=p.ORDER):
        p.require(
            tuple(order) == p.ORDER and len(decisions) == 6,
            "Complete ordered candidates",
        )
        columns = [list(column) for column in decisions]
        p.require(len({len(v) for v in columns}) == 1, "Equal chunk coverage")
        # Accept actual Python/NumPy booleans only; integer 0/1 is not a decision.
        for row in zip(*columns, strict=True):
            p.require(
                all(
                    type(v) is bool
                    or (type(v).__module__ == "numpy" and type(v).__name__ == "bool")
                    or (type(v).__module__ == "numpy" and type(v).__name__ == "bool_")
                    for v in row
                ),
                "Boolean decisions",
            )
            pattern = sum(int(v) << j for j, v in enumerate(row))
            self.counts[pattern] += 1
        return self

    def merge(self, other):
        p.require(type(other) is Patterns, "Same aggregate schema")
        self.counts = [a + b for a, b in zip(self.counts, other.counts, strict=True)]
        return self

    def moments(self):
        p.require(self.n > 0, "Empty aggregate")
        sums = [
            sum(c * ((pat >> j) & 1) for pat, c in enumerate(self.counts))
            for j in range(6)
        ]

        def k(pat):
            return sum(
                ((pat >> (2 * j)) & 1) - ((pat >> (2 * j + 1)) & 1) for j in range(3)
            )

        first = sum(c * k(pat) for pat, c in enumerate(self.counts))
        second = sum(c * k(pat) ** 2 for pat, c in enumerate(self.counts))
        variance = (
            Fraction(self.n * second - first * first, 9 * self.n * (self.n - 1))
            if self.n >= 2
            else None
        )
        return dict(
            n=self.n,
            mean=float(Fraction(first, 3 * self.n)),
            variance=float(variance) if variance is not None else None,
            rational_first_moment=[first, 3 * self.n],
            rational_variance=[variance.numerator, variance.denominator]
            if variance is not None
            else None,
            accepted=sums,
            rates=[float(Fraction(x, self.n)) for x in sums],
            seed_contrasts=[
                float(Fraction(sums[2 * j] - sums[2 * j + 1], self.n)) for j in range(3)
            ],
        )


def eb(mean, variance, n, *, delta, lower, upper):
    p.require(
        type(n) is int
        and n >= 0
        and all(math.isfinite(v) for v in (mean, delta, lower, upper))
        and lower < upper
        and lower <= mean <= upper
        and 0 < delta < 1,
        "Bounded mean arguments",
    )
    if n < 2:
        return dict(
            defined=False,
            reason="N_less_than_two",
            mean=mean,
            halfwidth=None,
            lower=None,
            upper=None,
        )
    p.require(
        variance is not None
        and math.isfinite(variance)
        and variance >= 0
        and type(variance) in (int, float)
        and variance <= (upper - lower) ** 2 * float(Fraction(n, n - 1)) / 4,
        "Unbiased bounded variance",
    )
    log = math.log(4 / delta)
    # Avoid float(n) overflow; ratios are computed exactly before conversion.
    h = (
        math.sqrt(float(Fraction(1, n)) * 2 * variance * log)
        + float(Fraction(1, n - 1)) * 7 * (upper - lower) * log / 3
    )
    p.require(math.isfinite(h) and h > 0, "Undefined finite-precision bound")
    return dict(
        defined=True,
        mean=mean,
        variance=variance,
        n=n,
        delta=delta,
        halfwidth=h,
        lower=max(lower, mean - h),
        upper=min(upper, mean + h),
        precision="unclipped_halfwidth",
    )


def rate_interval(count, n, delta):
    p.require(
        type(count) is int and type(n) is int and 0 <= count <= n and n > 0,
        "Rate counts",
    )
    variance = float(Fraction(count * (n - count), n * (n - 1))) if n >= 2 else None
    return eb(float(Fraction(count, n)), variance, n, delta=delta, lower=0.0, upper=1.0)


def wilson(count, n):
    p.require(
        type(count) is int and type(n) is int and 0 <= count <= n and n > 0,
        "Conditional rate counts",
    )
    rate, inv = float(Fraction(count, n)), float(Fraction(1, n))
    z = NormalDist().inv_cdf(0.975)
    center = (rate + z * z * inv / 2) / (1 + z * z * inv)
    half = (
        z
        * math.sqrt(rate * (1 - rate) * inv + z * z * inv * inv / 4)
        / (1 + z * z * inv)
    )
    return dict(
        wilson_95=[max(0.0, center - half), min(1.0, center + half)],
        zero_rate_upper_95=-math.expm1(math.log(0.05) * inv) if count == 0 else None,
        scope="individual conditional descriptive; not comparison/multiplicity test",
    )


def analyze(background, signal):
    p.require(
        type(background) is Patterns and type(signal) is Patterns,
        "Aggregate inputs only",
    )
    b, s = background.moments(), signal.moments()
    return dict(
        background=b,
        signal=s,
        signal_contrast=eb(
            s["mean"], s["variance"], s["n"], delta=0.025, lower=-1.0, upper=1.0
        ),
        background_contrast=eb(
            b["mean"], b["variance"], b["n"], delta=0.0125, lower=-1.0, upper=1.0
        ),
        background_rates=[rate_interval(c, b["n"], 0.0125 / 6) for c in b["accepted"]],
        signal_rates_descriptive=[wilson(c, s["n"]) for c in s["accepted"]],
        background_rates_descriptive=[wilson(c, b["n"]) for c in b["accepted"]],
        conditional_uncertainty=True,
        family_error_budget=0.05,
    )


def evaluate_gates(signal_interval, background_interval, background_rates, eligibility):
    """Explicit flags, fixed precedence; synthetic counts never confer source acceptance."""
    p.require(
        type(eligibility) is dict
        and set(eligibility) == set(ELIGIBILITY)
        and all(type(v) is bool for v in eligibility.values()),
        "Complete Boolean eligibility",
    )
    p.require(
        type(background_rates) is list and len(background_rates) == 6,
        "Six FPR intervals",
    )
    reasons = [k for k, v in eligibility.items() if not v]
    intervals = [signal_interval, background_interval, *background_rates]
    for i in intervals:
        p.require(type(i) is dict and type(i.get("defined")) is bool, "Interval schema")
        if i["defined"]:
            p.require(
                all(
                    type(i.get(k)) in (int, float) and math.isfinite(i[k])
                    for k in ("mean", "halfwidth", "lower", "upper")
                )
                and i["halfwidth"] >= 0
                and i["lower"] <= i["mean"] <= i["upper"],
                "Finite consistent interval",
            )
            tolerance = 8 * math.ulp(
                max(abs(i[k]) for k in ("mean", "lower", "upper", "halfwidth"))
            )
            p.require(
                max(i["mean"] - i["lower"], i["upper"] - i["mean"])
                <= i["halfwidth"] + tolerance,
                "Displayed interval exceeds unclipped halfwidth",
            )
    defined = all(i["defined"] for i in intervals)
    precision = (
        defined
        and signal_interval["halfwidth"] <= 0.0001
        and background_interval["halfwidth"] <= 0.0001
        and all(i["halfwidth"] <= 0.0002 for i in background_rates)
    )
    rate_stability = defined and all(
        i["lower"] >= 0.00075 and i["upper"] <= 0.00125 for i in background_rates
    )
    background_gate = defined and background_interval["upper"] <= 0.0001
    valid = not reasons
    if not defined:
        reasons.append("undefined_interval")
    if not precision:
        reasons.append("precision_failure")
    if not rate_stability:
        reasons.append("background_rate_stability_failure")
    if not background_gate:
        reasons.append("background_difference_failure")
    common = valid and defined and precision and rate_stability and background_gate
    flags = dict(
        nonlinear_advantage=common and signal_interval["lower"] > 0.0002,
        linear_advantage=common
        and signal_interval["upper"] < -0.0002
        and background_interval["lower"] >= -0.0001,
        practical_equivalence=common
        and signal_interval["lower"] >= -0.0002
        and signal_interval["upper"] <= 0.0002,
        no_practical_nonlinear_advantage=common and signal_interval["upper"] < 0.0002,
    )
    # Stronger labels precede overlapping negative/equivalence descriptions.
    label = (
        "nonlinear_advantage"
        if flags["nonlinear_advantage"]
        else "linear_advantage"
        if flags["linear_advantage"]
        else "practical_equivalence"
        if flags["practical_equivalence"]
        else "no_practical_nonlinear_advantage"
        if flags["no_practical_nonlinear_advantage"]
        else "background_stability_failure"
        if valid and defined and precision and not (rate_stability and background_gate)
        else "inconclusive"
    )
    return dict(
        label=label,
        actual_confirmation_claim=False,
        scope="conditional arithmetic predicates only; synthetic software never accepts sources or authorizes confirmation",
        claim_permitted=common and label != "inconclusive",
        flags=flags,
        gates=dict(
            eligibility=valid,
            defined=defined,
            precision=precision,
            rate_stability=rate_stability,
            background_difference=background_gate,
        ),
        reasons=reasons,
        precedence=[
            "nonlinear_advantage",
            "linear_advantage",
            "practical_equivalence",
            "no_practical_nonlinear_advantage",
            "background_stability_failure",
            "inconclusive",
        ],
    )


def decide(background, signal, eligibility):
    p.require(
        type(background) is Patterns and type(signal) is Patterns,
        "Aggregate inputs only",
    )
    if not background.n or not signal.n:
        undefined = dict(
            defined=False,
            reason="N_less_than_two",
            mean=None,
            halfwidth=None,
            lower=None,
            upper=None,
        )
        return evaluate_gates(
            undefined, undefined, [undefined.copy() for _ in range(6)], eligibility
        )
    result = analyze(background, signal)
    return evaluate_gates(
        result["signal_contrast"],
        result["background_contrast"],
        result["background_rates"],
        eligibility,
    )


def planning_minimum(variance, *, delta=0.025, target=0.0001):
    p.require(
        math.isfinite(variance)
        and 0 <= variance <= 1
        and math.isfinite(target)
        and target > 0,
        "Synthetic planning arguments",
    )
    low, high = 2, 100_000_000
    while low < high:
        mid = (low + high) // 2
        h = eb(0.0, variance, mid, delta=delta, lower=-1.0, upper=1.0)["halfwidth"]
        if h <= target:
            high = mid
        else:
            low = mid + 1
    p.require(
        eb(0.0, variance, low, delta=delta, lower=-1.0, upper=1.0)["halfwidth"]
        <= target,
        "Insufficient planning cap",
    )
    return low
