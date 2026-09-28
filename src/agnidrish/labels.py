"""Proxy labels for a "defective part" (ADR-002, ADR-004). Evaluation only — never features.

Both labels use the MEASURED 0 h and 168 h values. They are our experimental
definitions, not official SIH/ISRO labels. A label is <NA> when a value it
needs is missing.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import pandas as pd

T_END_H = 168.0


@dataclass(frozen=True)
class Allowance:
    """Drift allowance Δ_allow (ADR-002 SS-G): ``absolute`` in parameter units, or ``relative`` as a fraction of |V0|."""

    kind: str
    value: float

    def __post_init__(self) -> None:
        if self.kind not in ("absolute", "relative"):
            raise ValueError(f"allowance kind must be absolute or relative, got {self.kind!r}")
        if self.value < 0:
            raise ValueError("allowance must be >= 0")


def label_spec_168h(table: pd.DataFrame) -> pd.Series:
    """True when value_168h lies outside [spec_min, spec_max]; a NaN limit means no limit on that side."""
    v168 = table["value_168h"]
    outside = (v168 > table["spec_max"]).fillna(False) | (v168 < table["spec_min"]).fillna(False)
    return outside.astype("boolean").mask(v168.isna())


def label_safety_slope(
    table: pd.DataFrame,
    allowance: Mapping[str, Allowance],
    direction: Mapping[str, str],
) -> pd.Series:
    """ADR-002 §11: drift rate (V168 - V0)/168 h exceeds Δ_allow/168 h, or V168 is outside spec.

    ``direction`` per parameter: "up", "down" (signed drift in that direction)
    or "both" (absolute drift).
    """
    missing = sorted(set(table["parameter"]) - set(allowance) | set(table["parameter"]) - set(direction))
    if missing:
        raise ValueError(f"allowance and direction are required for parameters: {missing}")
    v0, v168 = table["value_0h"], table["value_168h"]
    change = v168 - v0
    sign = table["parameter"].map({p: {"up": 1.0, "down": -1.0, "both": 0.0}[d] for p, d in direction.items()})
    drift = (change * sign).where(sign != 0.0, change.abs())
    kind = table["parameter"].map({p: a.kind for p, a in allowance.items()})
    value = table["parameter"].map({p: a.value for p, a in allowance.items()})
    delta = value.where(kind == "absolute", value * v0.abs())
    exceeded = (drift / T_END_H > delta / T_END_H) | label_spec_168h(table).fillna(False).astype(bool)
    return exceeded.astype("boolean").mask(v0.isna() | v168.isna())
