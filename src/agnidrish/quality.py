"""Data-quality gate, layer L0 (FR-02, NFR-01).

Every flag is blocking: a flagged component, or every component of a flagged
(lot, parameter) group, must be decided REVIEW, never PASS. The gate reads only
the measurement columns available at the checkpoint (schema.available_value_columns).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

import numpy as np
import pandas as pd

from agnidrish.schema import (
    SPEC_COLUMNS,
    Checkpoint,
    SchemaError,
    available_value_columns,
    required_columns,
)

FLAG_COLUMNS: tuple[str, ...] = ("level", "row", "lot_id", "parameter", "component_id", "code", "detail")
GROUP_KEYS: list[str] = ["lot_id", "parameter"]


class FlagCode(StrEnum):
    MISSING_IDENTIFIER = "MISSING_IDENTIFIER"
    DUPLICATE_COMPONENT = "DUPLICATE_COMPONENT"
    MISSING_VALUE = "MISSING_VALUE"
    NON_NUMERIC = "NON_NUMERIC"
    NON_FINITE = "NON_FINITE"
    OUT_OF_PHYSICAL_RANGE = "OUT_OF_PHYSICAL_RANGE"
    NO_SPEC_LIMIT = "NO_SPEC_LIMIT"
    INVALID_SPEC_LIMITS = "INVALID_SPEC_LIMITS"
    LOT_TOO_SMALL = "LOT_TOO_SMALL"
    LOW_LEVEL_DISPERSION = "LOW_LEVEL_DISPERSION"
    LOW_DRIFT_DISPERSION = "LOW_DRIFT_DISPERSION"


@dataclass(frozen=True)
class QualityConfig:
    """Thresholds for the quality gate; values belong in configs/, not in code.

    Attributes:
        min_lot_size: minimum number of valid components per (lot, parameter)
            for lot-relative statistics.
        scale_floor: per parameter, in that parameter's unit. A lot whose raw
            MAD (median absolute deviation, not scaled by 1.4826) of a level,
            or of a between-checkpoint difference, is <= this floor is flagged:
            robust z-scores would divide by ~0. Every parameter in the data
            must have an entry.
        physical_bounds: optional per-parameter (low, high) plausibility
            bounds in the parameter's unit; None means unbounded on that side.
    """

    min_lot_size: int
    scale_floor: Mapping[str, float]
    physical_bounds: Mapping[str, tuple[float | None, float | None]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.min_lot_size < 1:
            raise ValueError(f"min_lot_size must be >= 1, got {self.min_lot_size}")
        negative = sorted(p for p, v in self.scale_floor.items() if v < 0)
        if negative:
            raise ValueError(f"scale_floor must be >= 0; negative for {negative}")


def run_quality_gate(table: pd.DataFrame, checkpoint: Checkpoint, config: QualityConfig) -> pd.DataFrame:
    """Return one row per quality issue found at ``checkpoint``.

    Columns: ``level`` ("component" or "lot"), ``row`` (index label of the
    flagged row; NA for lot flags), ``lot_id``, ``parameter``, ``component_id``
    (NA for lot flags), ``code`` (FlagCode), ``detail``.

    Raises:
        SchemaError: a column required at ``checkpoint`` is missing.
        ValueError: a parameter in the data has no ``scale_floor`` entry.
    """
    missing = [c for c in required_columns(checkpoint) if c not in table.columns]
    if missing:
        raise SchemaError(f"columns required at {checkpoint.name} are missing: {missing}")
    parameters = set(table["parameter"].dropna())
    no_floor = sorted(parameters - set(config.scale_floor))
    if no_floor:
        raise ValueError(f"scale_floor has no entry for parameters: {no_floor}")

    value_cols = available_value_columns(checkpoint)
    records: list[dict[str, object]] = []
    invalid = pd.Series(False, index=table.index)

    def flag_rows(mask: pd.Series, code: FlagCode, detail: str) -> None:
        for row in table.index[mask]:
            records.append(
                {
                    "level": "component",
                    "row": row,
                    "lot_id": table.at[row, "lot_id"],
                    "parameter": table.at[row, "parameter"],
                    "component_id": table.at[row, "component_id"],
                    "code": code,
                    "detail": detail,
                }
            )
        invalid.loc[mask] = True

    for col in ("component_id", "lot_id", "parameter"):
        flag_rows(table[col].isna(), FlagCode.MISSING_IDENTIFIER, col)

    ids_present = table[["component_id", "lot_id", "parameter"]].notna().all(axis=1)
    duplicated = table.duplicated(["lot_id", "parameter", "component_id"], keep=False) & ids_present
    flag_rows(duplicated, FlagCode.DUPLICATE_COMPONENT, "same component_id twice in lot and parameter")

    numeric: dict[str, pd.Series] = {}
    for col in value_cols + SPEC_COLUMNS:
        raw = table[col]
        values = pd.to_numeric(raw, errors="coerce").astype(float)
        absent = raw.isna()
        non_numeric = values.isna() & ~absent
        non_finite = pd.Series(np.isinf(values.to_numpy()), index=table.index)
        if col in value_cols:
            flag_rows(absent, FlagCode.MISSING_VALUE, col)
        flag_rows(non_numeric, FlagCode.NON_NUMERIC, col)
        flag_rows(non_finite, FlagCode.NON_FINITE, col)
        numeric[col] = values.where(~non_finite)

    spec_min, spec_max = numeric["spec_min"], numeric["spec_max"]
    flag_rows(table["spec_min"].isna() & table["spec_max"].isna(), FlagCode.NO_SPEC_LIMIT, "spec_min and spec_max")
    flag_rows(spec_min > spec_max, FlagCode.INVALID_SPEC_LIMITS, "spec_min > spec_max")

    for parameter, (low, high) in config.physical_bounds.items():
        of_parameter = table["parameter"] == parameter
        for col in value_cols:
            outside = pd.Series(False, index=table.index)
            if low is not None:
                outside |= numeric[col] < low
            if high is not None:
                outside |= numeric[col] > high
            flag_rows(of_parameter & outside, FlagCode.OUT_OF_PHYSICAL_RANGE, f"{col} outside [{low}, {high}]")

    valid = pd.DataFrame(numeric, index=table.index).loc[~invalid, list(value_cols)]
    valid[GROUP_KEYS] = table.loc[~invalid, GROUP_KEYS]
    for (lot_id, parameter), group in valid.groupby(GROUP_KEYS, sort=True):
        records.extend(_lot_flags(lot_id, parameter, group, value_cols, config))

    return pd.DataFrame.from_records(records, columns=list(FLAG_COLUMNS))


def _lot_flags(
    lot_id: object,
    parameter: object,
    group: pd.DataFrame,
    value_cols: tuple[str, ...],
    config: QualityConfig,
) -> list[dict[str, object]]:
    def lot_flag(code: FlagCode, detail: str) -> dict[str, object]:
        return {
            "level": "lot",
            "row": pd.NA,
            "lot_id": lot_id,
            "parameter": parameter,
            "component_id": pd.NA,
            "code": code,
            "detail": detail,
        }

    n = len(group)
    if n < config.min_lot_size:
        return [lot_flag(FlagCode.LOT_TOO_SMALL, f"{n} valid components < min_lot_size {config.min_lot_size}")]

    floor = config.scale_floor[str(parameter)]
    flags = []
    for col in value_cols:
        mad = _mad(group[col])
        if mad <= floor:
            flags.append(lot_flag(FlagCode.LOW_LEVEL_DISPERSION, f"MAD({col}) = {mad:g} <= floor {floor:g}"))
    for earlier, later in zip(value_cols, value_cols[1:]):
        mad = _mad(group[later] - group[earlier])
        if mad <= floor:
            flags.append(
                lot_flag(FlagCode.LOW_DRIFT_DISPERSION, f"MAD({later} - {earlier}) = {mad:g} <= floor {floor:g}")
            )
    return flags


def _mad(values: pd.Series) -> float:
    """Raw median absolute deviation from the median (no 1.4826 scaling)."""
    return float((values - values.median()).abs().median())


def review_mask(table: pd.DataFrame, flags: pd.DataFrame) -> pd.Series:
    """True for rows that must be decided REVIEW because of a quality flag."""
    component_rows = flags.loc[flags["level"] == "component", "row"]
    flagged = table.index.isin(component_rows)
    lot_keys = flags.loc[flags["level"] == "lot", GROUP_KEYS]
    if not lot_keys.empty:
        in_flagged_lot = pd.MultiIndex.from_frame(table[GROUP_KEYS]).isin(pd.MultiIndex.from_frame(lot_keys))
        flagged = flagged | in_flagged_lot
    return pd.Series(flagged, index=table.index, name="review_required")
