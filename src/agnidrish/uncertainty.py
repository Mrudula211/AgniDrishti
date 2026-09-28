"""Layer L5 — split-conformal prediction intervals for value_168h (FR-08).

Half-width per parameter from absolute residuals on CALIBRATION lots. Coverage
target is marginal (1 - alpha) under exchangeability — not a per-component
guarantee, and not a probability of failure (glossary). Lots break
exchangeability (S-11), so coverage is always reported per lot as well.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def conformal_halfwidth(true: pd.Series, pred: pd.Series, alpha: float) -> float:
    """The ceil((n+1)(1-alpha))-th smallest absolute residual; +inf if n is too small."""
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    ok = true.notna() & pred.notna()
    residuals = np.sort(np.abs((true[ok] - pred[ok]).to_numpy(dtype=float)))
    n = len(residuals)
    k = math.ceil((n + 1) * (1.0 - alpha))
    return float("inf") if k > n or n == 0 else float(residuals[k - 1])


def fit_halfwidths(calibration: pd.DataFrame, pred: pd.Series, alpha: float) -> dict[str, float]:
    """Per-parameter half-width (parameter units) from calibration rows."""
    return {
        str(p): conformal_halfwidth(g["value_168h"], pred.loc[g.index], alpha)
        for p, g in calibration.groupby("parameter")
    }


def interval(table: pd.DataFrame, pred: pd.Series, halfwidths: dict[str, float]) -> pd.DataFrame:
    hw = table["parameter"].map(halfwidths)
    return pd.DataFrame({"pi_low": pred - hw, "pi_high": pred + hw}, index=table.index)
