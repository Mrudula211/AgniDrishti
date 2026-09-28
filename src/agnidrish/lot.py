"""Layer L2 — lot-relative robust scores of level and drift (Module A; FR-04, FR-05).

Statistics use only same-checkpoint peers in the same (lot, parameter) group —
allowed by CLAUDE §7; no peer labels or later values are read.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd

from agnidrish.schema import Checkpoint, available_value_columns

GROUP_KEYS = ["lot_id", "parameter"]


def robust_scale(values: pd.Series, method: str) -> float:
    """Robust sigma in the values' unit: ``iqr`` = (Q3 - Q1)/1.35 (AEC-Q001), ``mad`` = 1.4826·MAD."""
    v = values.dropna()
    if v.empty:
        return float("nan")
    if method == "iqr":
        return float((v.quantile(0.75) - v.quantile(0.25)) / 1.35)
    if method == "mad":
        return float(1.4826 * (v - v.median()).abs().median())
    raise ValueError(f"unknown robust scale method {method!r}")


def lot_robust_z(
    table: pd.DataFrame,
    values: pd.Series,
    method: str,
    scale_floor: Mapping[str, float],
) -> pd.DataFrame:
    """Robust z = (value - lot median) / lot robust scale, per (lot, parameter).

    Returns columns ``z``, ``median``, ``scale``. ``z`` is NaN when the value is
    missing or the lot scale is <= the parameter's floor (degenerate lot).
    """
    frame = table[GROUP_KEYS].assign(v=values)
    grouped = frame.groupby(GROUP_KEYS)["v"]
    median = grouped.transform("median")
    scale = grouped.transform(lambda s: robust_scale(s, method))
    floor = table["parameter"].map(scale_floor)
    usable = scale > floor
    z = ((values - median) / scale).where(usable & values.notna())
    return pd.DataFrame({"z": z, "median": median, "scale": scale}, index=table.index)


def level_and_drift_scores(
    table: pd.DataFrame,
    checkpoint: Checkpoint,
    method: str,
    scale_floor: Mapping[str, float],
) -> pd.DataFrame:
    """Level = latest value available at ``checkpoint``; drift = latest minus previous checkpoint.

    Returns ``z_level``, ``z_drift``, the level and drift values, and lot medians/scales.
    """
    cols = available_value_columns(checkpoint)
    level = table[cols[-1]]
    drift = table[cols[-1]] - table[cols[-2]]
    lz = lot_robust_z(table, level, method, scale_floor)
    dz = lot_robust_z(table, drift, method, scale_floor)
    return pd.DataFrame(
        {
            "level": level,
            "z_level": lz["z"],
            "lot_median_level": lz["median"],
            "lot_scale_level": lz["scale"],
            "drift": drift,
            "z_drift": dz["z"],
            "lot_median_drift": dz["median"],
            "lot_scale_drift": dz["scale"],
        },
        index=table.index,
    )


def scale_floor_from_nominal(table: pd.DataFrame, fraction: float) -> dict[str, float]:
    """Per-parameter scale floor = fraction · |typical value| (nominal_value if present, else median of value_0h)."""
    source = table["nominal_value"] if "nominal_value" in table.columns else table["value_0h"]
    typical = source.groupby(table["parameter"]).median().abs()
    return {p: float(fraction * v) for p, v in typical.items() if np.isfinite(v)}
