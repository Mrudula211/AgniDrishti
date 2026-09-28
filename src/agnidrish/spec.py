"""Layer L1 — absolute datasheet-limit check (FR-03). A NaN limit means no limit on that side."""

from __future__ import annotations

import pandas as pd


def outside_spec(table: pd.DataFrame, value: pd.Series) -> pd.Series:
    """True where ``value`` lies outside [spec_min, spec_max]; missing values give False (L0 handles them)."""
    above = (value > table["spec_max"]).fillna(False)
    below = (value < table["spec_min"]).fillna(False)
    return (above | below).astype(bool)


def spec_violation(table: pd.DataFrame, columns: list[str] | tuple[str, ...]) -> pd.Series:
    """True where any of the measured ``columns`` is outside the datasheet limits."""
    result = pd.Series(False, index=table.index)
    for col in columns:
        result |= outside_spec(table, table[col])
    return result


def spec_exceedance(table: pd.DataFrame, value: pd.Series) -> pd.Series:
    """Signed exceedance relative to the limit: > 0 outside spec, < 0 inside (unitless ranking score).

    For each side with a limit L: (value - L) / |L| above, (L - value) / |L| below;
    the larger of the two is returned.
    """
    upper = (value - table["spec_max"]) / table["spec_max"].abs()
    lower = (table["spec_min"] - value) / table["spec_min"].abs()
    return pd.concat([upper, lower], axis=1).max(axis=1, skipna=True)
