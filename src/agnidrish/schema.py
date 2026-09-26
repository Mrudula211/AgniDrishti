"""Canonical burn-in measurement schema and raw-to-canonical column mapping (FR-01).

Schema source of truth: docs/research/datasets/data-dictionary.md.
One row per component per parameter; values stay in the parameter's own unit.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum

import pandas as pd


class Checkpoint(Enum):
    """Decision checkpoint, in nominal burn-in hours."""

    T24 = 24
    T96 = 96
    T168 = 168


VALUE_COLUMNS: dict[int, str] = {
    0: "value_0h",
    24: "value_24h",
    96: "value_96h",
    168: "value_168h",
}
ID_COLUMNS: tuple[str, ...] = ("component_id", "lot_id", "parameter", "unit")
SPEC_COLUMNS: tuple[str, ...] = ("spec_min", "spec_max")
PROVENANCE_COLUMNS: tuple[str, ...] = ("data_category", "dataset_version")
OPTIONAL_COLUMNS: tuple[str, ...] = ("wafer_id", "device_family", "temperature_c")

CANONICAL_ORDER: tuple[str, ...] = (
    ID_COLUMNS[:2]
    + ("wafer_id", "device_family")
    + ID_COLUMNS[2:]
    + ("temperature_c",)
    + tuple(VALUE_COLUMNS.values())
    + SPEC_COLUMNS
    + PROVENANCE_COLUMNS
)
DATA_CATEGORIES: frozenset[str] = frozenset({"official", "external", "synthetic"})


class SchemaError(ValueError):
    """A table cannot be mapped to, or does not satisfy, the canonical schema."""


def available_value_columns(checkpoint: Checkpoint) -> tuple[str, ...]:
    """Measurement columns observable at ``checkpoint``.

    This is the leakage boundary (data-dictionary §4): anything computed at a
    checkpoint may read only these columns, never a later measurement.
    """
    return tuple(col for hour, col in VALUE_COLUMNS.items() if hour <= checkpoint.value)


def required_columns(checkpoint: Checkpoint) -> tuple[str, ...]:
    """Columns a canonical table must contain to be processed at ``checkpoint``."""
    return ID_COLUMNS + available_value_columns(checkpoint) + SPEC_COLUMNS + PROVENANCE_COLUMNS


def to_canonical(
    raw: pd.DataFrame,
    mapping: Mapping[str, str],
    *,
    checkpoint: Checkpoint,
    data_category: str,
    dataset_version: str,
) -> pd.DataFrame:
    """Rename ``raw`` columns to canonical names without changing any value.

    ``mapping`` is raw name -> canonical name. Raw columns not in ``mapping``
    are dropped. A spec-limit column absent after mapping is added as all-NaN,
    meaning "no limit on that side"; whether a usable limit exists is checked by
    the quality gate. Provenance columns are set from the arguments and may not
    be mapped from raw data.

    Raises:
        SchemaError: invalid category or version, bad mapping, or a column
            required at ``checkpoint`` is missing after mapping.
    """
    if data_category not in DATA_CATEGORIES:
        raise SchemaError(f"data_category must be one of {sorted(DATA_CATEGORIES)}, got {data_category!r}")
    if not dataset_version.strip():
        raise SchemaError("dataset_version must be non-empty")

    allowed_targets = set(CANONICAL_ORDER) - set(PROVENANCE_COLUMNS)
    unknown = sorted(set(mapping.values()) - allowed_targets)
    if unknown:
        raise SchemaError(f"mapping targets are not mappable canonical columns: {unknown}")
    targets = list(mapping.values())
    duplicated = sorted({t for t in targets if targets.count(t) > 1})
    if duplicated:
        raise SchemaError(f"several raw columns map to the same canonical column: {duplicated}")
    absent = sorted(set(mapping) - set(raw.columns))
    if absent:
        raise SchemaError(f"mapped raw columns not found in the data: {absent}")

    table = raw.loc[:, list(mapping)].rename(columns=dict(mapping))
    for col in SPEC_COLUMNS:
        if col not in table.columns:
            table[col] = float("nan")
    table["data_category"] = data_category
    table["dataset_version"] = dataset_version

    missing = [c for c in required_columns(checkpoint) if c not in table.columns]
    if missing:
        raise SchemaError(f"columns required at {checkpoint.name} are missing after mapping: {missing}")

    return table.loc[:, [c for c in CANONICAL_ORDER if c in table.columns]]
