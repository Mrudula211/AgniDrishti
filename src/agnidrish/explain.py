"""Layer L7 — engineer-readable explanation built only from the decision evidence (FR-11).

Wording follows the glossary: robust z is a distance, the interval is a
prediction interval with target marginal coverage, never a failure probability.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

RULE_TEXT: dict[str, str] = {
    "R0": "data-quality problem or missing evidence — an engineer must review (never auto-PASS)",
    "R1": "a measured value is outside the datasheet limit now",
    "R2": "predicted 168 h drift exceeds the safety slope even at the optimistic end of the prediction interval",
    "R3": "predicted 168 h drift (point or pessimistic end of the interval) exceeds the safety slope or the limit",
    "R4": "both level and drift are extreme relative to the lot",
    "R5": "level or drift is unusual relative to the lot",
    "R6": "no rule fired",
}


def _num(x: Any, digits: int = 4) -> str:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return "n/a"
    return "n/a" if math.isnan(v) else f"{v:.{digits}g}"


def explain_row(row: pd.Series, coverage: float | None, data_category: str) -> dict[str, Any]:
    """Return {'headline', 'lines', 'rules'} for one screened row (``row`` = table + screen output)."""
    unit = row.get("unit", "")
    rules = str(row["fired_rules"]).split(";")
    lines = [
        f"Data category: {data_category.upper()}",
        f"Measured: 0 h = {_num(row['value_0h'])} {unit}; 24 h = {_num(row['value_24h'])} {unit}; "
        f"limits [{_num(row['spec_min'])}, {_num(row['spec_max'])}] {unit} → "
        + ("outside the datasheet limit" if row["spec_now"] else "within the datasheet limit"),
        f"Lot position at 24 h: {_num(row['z_level'], 3)} robust-z from the lot median "
        f"{_num(row['lot_median_level'])} {unit} (robust scale {_num(row['lot_scale_level'])} {unit})",
        f"Drift 0→24 h: {_num(row['drift'])} {unit}, {_num(row['z_drift'], 3)} robust-z from the lot's median drift "
        f"{_num(row['lot_median_drift'])} {unit}",
    ]
    if "pred_168h" in row and not pd.isna(row.get("pred_168h")):
        lines.append(
            f"Predicted 168 h: {_num(row['pred_168h'])} {unit}; predicted drift rate "
            f"{_num(row['pred_drift_rate_per_h'], 3)} {unit}/h vs safety slope {_num(row['safety_slope_per_h'], 3)} {unit}/h"
        )
        if "pi_low" in row and not pd.isna(row.get("pi_low")):
            cov = f"{coverage:.0%} " if coverage is not None else ""
            lines.append(
                f"{cov}prediction interval (target marginal coverage, not a failure probability): "
                f"[{_num(row['pi_low'])}, {_num(row['pi_high'])}] {unit}"
            )
    if row.get("gate_codes"):
        lines.append(f"Quality flags: {row['gate_codes']}")
    lines.append("Rules fired: " + "; ".join(f"{r} — {RULE_TEXT.get(r, r)}" for r in rules))
    headline = (
        f"{row['component_id']} · lot {row['lot_id']} · {row['parameter']} → {row['decision']} "
        f"(first rule {rules[0]})"
    )
    return {"headline": headline, "lines": lines, "rules": rules}
