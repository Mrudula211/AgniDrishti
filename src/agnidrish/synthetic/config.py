"""Load and validate the synthetic generator configuration (configs/synthetic/*.yaml)."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from agnidrish.schema import VALUE_COLUMNS
from agnidrish.synthetic.families import ANOMALOUS_FAMILIES, FAMILY_KINDS, HEALTHY_FAMILIES

SPLITS: tuple[str, ...] = ("train", "validation", "calibration", "test")


class ConfigError(ValueError):
    """The generator configuration is invalid."""


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    unit: str
    nominal: float
    spec_min: float  # NaN = no lower limit
    spec_max: float  # NaN = no upper limit
    direction: int  # +1 up, -1 down
    lot_sd_frac: float
    comp_sd_frac: float
    comp_drift_sd_frac: float
    lot_drift_mean_frac: float
    lot_drift_sd_frac: float
    meas_sd_frac: float
    meas_model: str
    high_mean_factor: float
    quantisation_step: float

    @property
    def comp_sd(self) -> float:
        return self.comp_sd_frac * self.nominal

    @property
    def drift_reference_sd(self) -> float:
        """Healthy within-lot SD of the 0 h -> last-checkpoint change, at nominal level."""
        comp_drift = self.comp_drift_sd_frac * self.nominal
        meas = self.meas_sd_frac * self.nominal
        return math.sqrt(comp_drift**2 + 2.0 * meas**2)

    @property
    def degradation_limit(self) -> float:
        return self.spec_max if self.direction > 0 else self.spec_min


@dataclass(frozen=True)
class GeneratorConfig:
    raw: dict[str, Any]
    parameters: tuple[ParameterSpec, ...]

    @property
    def seed(self) -> int:
        return int(self.raw["seed"])

    @property
    def checkpoints(self) -> tuple[int, ...]:
        return tuple(self.raw["checkpoints_h"])

    @property
    def dataset_version(self) -> str:
        return f"{self.raw['dataset_name']}_{self.raw['version']}_seed{self.seed}"

    def sha256(self) -> str:
        canonical = json.dumps(self.raw, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def with_seed(self, seed: int) -> GeneratorConfig:
        return from_dict({**self.raw, "seed": seed})


def load_config(path: Path) -> GeneratorConfig:
    with Path(path).open(encoding="utf-8") as fh:
        return from_dict(yaml.safe_load(fh))


def _limit(value: float | None) -> float:
    return float("nan") if value is None else float(value)


def from_dict(raw: dict[str, Any]) -> GeneratorConfig:
    errors: list[str] = []
    checkpoints = raw.get("checkpoints_h", [])
    if list(checkpoints) != sorted(set(checkpoints)) or not checkpoints or checkpoints[0] != 0:
        errors.append("checkpoints_h must be strictly increasing and start at 0")
    if any(h not in VALUE_COLUMNS for h in checkpoints):
        errors.append(f"checkpoints_h must be canonical checkpoints {sorted(VALUE_COLUMNS)}")

    params = []
    for name, p in raw.get("parameters", {}).items():
        spec = ParameterSpec(
            name=name,
            unit=p["unit"],
            nominal=float(p["nominal"]),
            spec_min=_limit(p["spec_min"]),
            spec_max=_limit(p["spec_max"]),
            direction={"up": 1, "down": -1}.get(p["direction"], 0),
            lot_sd_frac=p["lot_sd_frac"],
            comp_sd_frac=p["comp_sd_frac"],
            comp_drift_sd_frac=p["comp_drift_sd_frac"],
            lot_drift_mean_frac=p["lot_drift_mean_frac"],
            lot_drift_sd_frac=p["lot_drift_sd_frac"],
            meas_sd_frac=p["meas_sd_frac"],
            meas_model=p["meas_model"],
            high_mean_factor=p["high_mean_factor"],
            quantisation_step=p["quantisation_step"],
        )
        if spec.direction == 0:
            errors.append(f"{name}: direction must be 'up' or 'down'")
        if math.isnan(spec.degradation_limit):
            errors.append(f"{name}: needs a spec limit in its degradation direction")
        if not (math.isnan(spec.spec_min) or math.isnan(spec.spec_max)) and spec.spec_min >= spec.spec_max:
            errors.append(f"{name}: spec_min must be < spec_max")
        if spec.meas_model not in ("additive", "proportional"):
            errors.append(f"{name}: meas_model must be additive or proportional")
        params.append(spec)
    if not params:
        errors.append("at least one parameter is required")

    healthy = set(raw.get("healthy_family_weights", {}))
    anomalous = set(raw.get("anomalous_family_weights", {}))
    if not healthy or not healthy <= HEALTHY_FAMILIES:
        errors.append(f"healthy_family_weights must be non-empty and within {sorted(HEALTHY_FAMILIES)}")
    if not anomalous or not anomalous <= ANOMALOUS_FAMILIES:
        errors.append(f"anomalous_family_weights must be non-empty and within {sorted(ANOMALOUS_FAMILIES)}")

    for name, sc in raw.get("lot_scenarios", {}).items():
        lo, hi = sc["size"]
        if not 1 <= lo <= hi:
            errors.append(f"lot scenario {name}: size range invalid")
        flo, fhi = sc["anomaly_fraction"]
        if not 0.0 <= flo <= fhi <= 1.0:
            errors.append(f"lot scenario {name}: anomaly_fraction range invalid")
        unknown = set(sc.get("excluded_families", [])) - set(FAMILY_KINDS)
        if unknown:
            errors.append(f"lot scenario {name}: unknown excluded families {sorted(unknown)}")

    fractions = raw.get("splits", {}).get("fractions", {})
    if set(fractions) != set(SPLITS) or not math.isclose(sum(fractions.values()), 1.0):
        errors.append(f"split fractions must cover {SPLITS} and sum to 1")

    if errors:
        raise ConfigError("; ".join(errors))
    return GeneratorConfig(raw=raw, parameters=tuple(params))
