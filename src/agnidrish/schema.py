"""Canonical burn-in measurement schema (FR-01): the contract between data adapters and the pipeline.

Schema source of truth: docs/research/datasets/data-dictionary.md.
One row per component per parameter; values stay in the parameter's own unit.
Raw exports are converted to this schema by ``agnidrish.ingest`` (ADR-007).
"""

from __future__ import annotations

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


# Ground truth, labels and experiment bookkeeping: evaluation only, never model inputs.
EVALUATION_ONLY_COLUMNS: frozenset[str] = frozenset(
    {
        "split",
        "lot_scenario",
        "behaviour_family",
        "is_anomaly",
        "severity",
        "severity_band",
        "anomaly_amplitude",
        "level_offset",
        "noise_sd",
        "data_fault",
        "scenario",
        "label_spec_168h",
        "label_safety_slope",
        "label_latent",
    }
    | {f"true_{col}" for col in VALUE_COLUMNS.values()}
)


class SchemaError(ValueError):
    """A table cannot be mapped to, or does not satisfy, the canonical schema."""


def model_input_columns(columns: list[str] | pd.Index, checkpoint: "Checkpoint") -> list[str]:
    """Columns that may be used as inputs at ``checkpoint``.

    Excludes evaluation-only columns and every measurement taken after
    ``checkpoint`` (e.g. value_168h at T24).
    """
    later = set(VALUE_COLUMNS.values()) - set(available_value_columns(checkpoint))
    return [c for c in columns if c not in EVALUATION_ONLY_COLUMNS and c not in later]


def available_value_columns(checkpoint: Checkpoint) -> tuple[str, ...]:
    """Measurement columns observable at ``checkpoint``.

    This is the leakage boundary (data-dictionary §4): anything computed at a
    checkpoint may read only these columns, never a later measurement.
    """
    return tuple(col for hour, col in VALUE_COLUMNS.items() if hour <= checkpoint.value)


def required_columns(checkpoint: Checkpoint) -> tuple[str, ...]:
    """Columns a canonical table must contain to be processed at ``checkpoint``."""
    return ID_COLUMNS + available_value_columns(checkpoint) + SPEC_COLUMNS + PROVENANCE_COLUMNS


