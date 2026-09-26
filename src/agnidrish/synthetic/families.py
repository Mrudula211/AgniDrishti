"""Development behaviour families for SYNTHETIC data (our definitions, not official labels).

Held-out families 19-20 are deliberately absent: they are sealed outside the
repository (synthetic-data-design.md §7) and must not be recreated here.

Each family decides, for one (component, parameter) row, how its true
trajectory deviates from healthy lot behaviour. Shapes are normalised so that
f(0) = 0 and f(t_end) = 1: an amplitude A means "A extra units by t_end".
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

import numpy as np


class Kind(StrEnum):
    HEALTHY = "healthy"
    DRIFT = "drift"  # anomalous extra drift A * f(t)
    LEVEL = "level"  # anomalous constant offset relative to the lot
    SPEC = "spec"  # anomalous, sized relative to the datasheet limit


FAMILY_KINDS: dict[str, Kind] = {
    "healthy_stable": Kind.HEALTHY,
    "healthy_random_drift": Kind.HEALTHY,
    "healthy_decelerating": Kind.HEALTHY,
    "healthy_component_offset": Kind.HEALTHY,
    "healthy_noisy": Kind.HEALTHY,
    "degradation_linear": Kind.DRIFT,
    "degradation_accelerating": Kind.DRIFT,
    "degradation_decelerating": Kind.DRIFT,
    "degradation_noisy": Kind.DRIFT,
    "drift_early": Kind.DRIFT,
    "drift_late": Kind.DRIFT,
    "degradation_sigmoid": Kind.DRIFT,
    "degradation_saturating": Kind.DRIFT,
    "shift_sudden": Kind.DRIFT,
    "degradation_wrong_direction": Kind.DRIFT,
    "level_outlier": Kind.LEVEL,
    "approaching_spec": Kind.SPEC,
    "crossing_spec": Kind.SPEC,
    "spec_violation_at_0h": Kind.LEVEL,
}
HEALTHY_FAMILIES = frozenset(f for f, k in FAMILY_KINDS.items() if k is Kind.HEALTHY)
ANOMALOUS_FAMILIES = frozenset(FAMILY_KINDS) - HEALTHY_FAMILIES


@dataclass(frozen=True)
class Shape:
    """Normalised time shape; ``kind`` in {zero, linear, power, exp, late, sigmoid, step}."""

    kind: str
    a: float = 0.0
    b: float = 0.0

    def __call__(self, t: np.ndarray, t_end: float) -> np.ndarray:
        t = np.asarray(t, dtype=float)
        x = t / t_end
        match self.kind:
            case "zero":
                return np.zeros_like(t)
            case "linear":
                return x
            case "power":
                return x**self.a
            case "exp":
                return (1.0 - np.exp(-t / self.a)) / (1.0 - np.exp(-t_end / self.a))
            case "late":
                return np.clip((t - self.a) / (t_end - self.a), 0.0, None)
            case "sigmoid":
                def s(u: np.ndarray | float) -> np.ndarray:
                    return 1.0 / (1.0 + np.exp(-(np.asarray(u) - self.a) / self.b))
                return (s(t) - s(0.0)) / (s(t_end) - s(0.0))
            case "step":
                return (t >= self.a).astype(float)
        raise ValueError(f"unknown shape kind {self.kind!r}")


@dataclass(frozen=True)
class Behaviour:
    """Sampled deviation of one row from healthy lot behaviour (all in parameter units)."""

    family: str
    is_anomaly: bool
    level_offset: float  # constant added at every checkpoint
    amplitude: float  # signed extra change by t_end
    shape: Shape
    component_drift_scale: float  # multiplies the component's healthy drift
    healthy_shape: Shape
    meas_multiplier: float
    severity: float  # NaN for healthy rows


@dataclass(frozen=True)
class RowContext:
    """Quantities a family needs; all absolute, in parameter units."""

    direction: int  # +1 degradation raises the value, -1 lowers it
    comp_sd: float
    drift_reference_sd: float  # healthy within-lot SD of the 0 -> t_end change
    limit: float  # datasheet limit in the degradation direction
    baseline: float  # true value at 0 h before any family offset
    healthy_end: float  # true value at t_end under healthy behaviour
    healthy_tau_h: float


def uniform(rng: np.random.Generator, bounds: tuple[float, float] | list[float]) -> float:
    return float(rng.uniform(bounds[0], bounds[1]))


def sample_drift_k(rng: np.random.Generator, severity: Mapping) -> float:
    """Sample k by band weight, then uniformly inside the band."""
    edges = severity["band_edges"]
    lo_hi = {
        "mild": (edges["mild"], edges["moderate"]),
        "moderate": (edges["moderate"], edges["severe"]),
        "severe": (edges["severe"], severity["drift_k"][1]),
    }
    names = list(severity["band_weights"])
    weights = np.array([severity["band_weights"][n] for n in names], dtype=float)
    band = names[int(rng.choice(len(names), p=weights / weights.sum()))]
    return uniform(rng, lo_hi[band])


def severity_band(k: float, band_edges: Mapping[str, float]) -> str:
    if np.isnan(k):
        return "none"
    if k >= band_edges["severe"]:
        return "severe"
    if k >= band_edges["moderate"]:
        return "moderate"
    if k >= band_edges["mild"]:
        return "mild"
    return "minimal"


def sample_behaviour(
    family: str,
    rng: np.random.Generator,
    ctx: RowContext,
    params: Mapping,
    severity: Mapping,
) -> Behaviour:
    """Draw the behaviour of one row. Severity definition: synthetic-data-design.md §9.4."""
    if family not in FAMILY_KINDS:
        raise ValueError(f"unknown development family {family!r}")
    exp_healthy = Shape("exp", ctx.healthy_tau_h)
    base = dict(
        family=family,
        is_anomaly=family in ANOMALOUS_FAMILIES,
        level_offset=0.0,
        amplitude=0.0,
        shape=Shape("zero"),
        component_drift_scale=1.0,
        healthy_shape=exp_healthy,
        meas_multiplier=1.0,
        severity=float("nan"),
    )
    s = ctx.direction

    match family:
        case "healthy_stable":
            base["component_drift_scale"] = params["healthy_stable_drift_scale"]
        case "healthy_random_drift":
            base["healthy_shape"] = Shape("linear")
        case "healthy_decelerating":
            pass
        case "healthy_component_offset":
            sign = 1.0 if rng.random() < 0.5 else -1.0
            base["level_offset"] = sign * uniform(rng, params["healthy_component_offset_sd"]) * ctx.comp_sd
        case "healthy_noisy":
            base["meas_multiplier"] = params["noisy_meas_multiplier"]
        case "level_outlier":
            k = uniform(rng, params["level_outlier_sd"])
            base.update(level_offset=s * k * ctx.comp_sd, severity=k)
        case "spec_violation_at_0h":
            target = ctx.limit + s * uniform(rng, params["at_0h_excess_sd"]) * ctx.comp_sd
            offset = target - ctx.baseline
            base.update(level_offset=offset, severity=abs(offset) / ctx.comp_sd)
        case "approaching_spec" | "crossing_spec":
            key = "approaching_fraction" if family == "approaching_spec" else "crossing_fraction"
            amplitude = uniform(rng, params[key]) * (ctx.limit - ctx.healthy_end)
            base.update(amplitude=amplitude, shape=Shape("linear"), severity=abs(amplitude) / ctx.drift_reference_sd)
        case _:  # drift families
            k = sample_drift_k(rng, severity)
            shape, sign = _drift_shape(family, rng, params, ctx)
            base.update(amplitude=sign * s * k * ctx.drift_reference_sd, shape=shape, severity=k)
            if family == "degradation_noisy":
                base["meas_multiplier"] = params["noisy_meas_multiplier"]
    return Behaviour(**base)


def _drift_shape(family: str, rng: np.random.Generator, params: Mapping, ctx: RowContext) -> tuple[Shape, float]:
    match family:
        case "degradation_linear" | "degradation_noisy":
            return Shape("linear"), 1.0
        case "degradation_wrong_direction":
            return Shape("linear"), -1.0
        case "degradation_accelerating":
            return Shape("power", uniform(rng, params["accelerating_power"])), 1.0
        case "degradation_decelerating":
            return Shape("power", uniform(rng, params["decelerating_power"])), 1.0
        case "drift_early":
            return Shape("exp", uniform(rng, params["early_tau_h"])), 1.0
        case "drift_late":
            return Shape("late", uniform(rng, params["late_onset_h"])), 1.0
        case "degradation_sigmoid":
            return Shape("sigmoid", uniform(rng, params["sigmoid_center_h"]), uniform(rng, params["sigmoid_width_h"])), 1.0
        case "degradation_saturating":
            return Shape("exp", uniform(rng, params["saturating_tau_h"])), 1.0
        case "shift_sudden":
            return Shape("step", uniform(rng, params["sudden_shift_time_h"])), 1.0
    raise ValueError(f"{family!r} is not a drift family")
