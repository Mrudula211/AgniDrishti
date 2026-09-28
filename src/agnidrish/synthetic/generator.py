"""Deterministic generator for SYNTHETIC, PS-shaped burn-in lots (development families only).

Output: one row per component per parameter in the canonical schema, plus
evaluation-only ground-truth columns (schema.EVALUATION_ONLY_COLUMNS).
Model and definitions: docs/research/datasets/synthetic-data-design.md §9.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd

from agnidrish.schema import VALUE_COLUMNS
from agnidrish.synthetic.config import SPLITS, GeneratorConfig, ParameterSpec
from agnidrish.synthetic.families import RowContext, Shape, sample_behaviour, severity_band

GENERATOR_VERSION = "1.1.0"
# Rounding ties give lots to the frozen test split first, so hard scenarios with
# few lots are still represented in final evaluation.
TIE_PRIORITY: tuple[str, ...] = ("test", "validation", "calibration", "train")


def truncated_normal(rng: np.random.Generator, sd: float, bound_sd: float, size: int | None = None) -> Any:
    """Normal(0, sd) truncated to +/- bound_sd * sd by resampling."""
    n = 1 if size is None else size
    out = rng.normal(0.0, sd, n)
    bad = np.abs(out) > bound_sd * sd
    while bad.any():
        out[bad] = rng.normal(0.0, sd, int(bad.sum()))
        bad = np.abs(out) > bound_sd * sd
    return float(out[0]) if size is None else out


def generate(config: GeneratorConfig) -> pd.DataFrame:
    """Generate the full synthetic dataset for ``config`` (same config + seed -> identical frame)."""
    raw = config.raw
    lots = [
        (scenario, spec)
        for scenario, spec in raw["lot_scenarios"].items()
        for _ in range(spec["n_lots"])
    ]
    streams = np.random.SeedSequence(config.seed).spawn(len(lots) + 1)
    frames = [
        _generate_lot(f"SYN-L{i + 1:03d}", scenario, spec, config, np.random.default_rng(stream))
        for i, ((scenario, spec), stream) in enumerate(zip(lots, streams[:-1]))
    ]
    table = pd.concat(frames, ignore_index=True)
    lot_split = assign_splits(
        table.groupby("lot_id", sort=True)["lot_scenario"].first(),
        raw["splits"]["fractions"],
        np.random.default_rng(streams[-1]),
    )
    table["split"] = table["lot_id"].map(lot_split)
    return table.sort_values(["lot_id", "component_id", "parameter"], ignore_index=True)


def assign_splits(
    lot_scenario: pd.Series,
    fractions: Mapping[str, float],
    rng: np.random.Generator,
) -> dict[str, str]:
    """Assign whole lots to splits, stratified by lot scenario (largest-remainder rounding)."""
    assignment: dict[str, str] = {}
    for scenario in sorted(lot_scenario.unique()):
        lot_ids = sorted(lot_scenario.index[lot_scenario == scenario])
        n = len(lot_ids)
        exact = {s: fractions[s] * n for s in SPLITS}
        counts = {s: int(np.floor(v)) for s, v in exact.items()}
        by_remainder = sorted(SPLITS, key=lambda s: (-(exact[s] - counts[s]), TIE_PRIORITY.index(s)))
        for s in by_remainder[: n - sum(counts.values())]:
            counts[s] += 1
        shuffled = [lot_ids[i] for i in rng.permutation(n)]
        start = 0
        for s in SPLITS:
            for lot_id in shuffled[start : start + counts[s]]:
                assignment[lot_id] = s
            start += counts[s]
    return assignment


def _weighted_choice(rng: np.random.Generator, weights: Mapping[str, float], exclude: set[str]) -> str:
    names = sorted(n for n in weights if n not in exclude and weights[n] > 0)
    w = np.array([weights[n] for n in names], dtype=float)
    return names[int(rng.choice(len(names), p=w / w.sum()))]


def _generate_lot(
    lot_id: str,
    scenario: str,
    spec: Mapping[str, Any],
    config: GeneratorConfig,
    rng: np.random.Generator,
) -> pd.DataFrame:
    raw = config.raw
    trunc = raw["truncation_sd"]
    hours = np.array(config.checkpoints, dtype=float)
    t_end = float(hours[-1])
    n = int(rng.integers(spec["size"][0], spec["size"][1] + 1))
    wafers = np.where(np.arange(n) < n // 2, "W1", "W2") if scenario == "bimodal" else np.full(n, "W1")
    excluded = set(spec.get("excluded_families", []))

    rows: list[dict[str, Any]] = []
    for p in config.parameters:
        rows.extend(_generate_parameter(lot_id, scenario, spec, p, n, wafers, excluded, config, rng, hours, t_end, trunc))
    return pd.DataFrame(rows)


def _generate_parameter(
    lot_id: str,
    scenario: str,
    spec: Mapping[str, Any],
    p: ParameterSpec,
    n: int,
    wafers: np.ndarray,
    excluded: set[str],
    config: GeneratorConfig,
    rng: np.random.Generator,
    hours: np.ndarray,
    t_end: float,
    trunc: Mapping[str, float],
) -> list[dict[str, Any]]:
    raw = config.raw
    level_factor = p.high_mean_factor if scenario == "high_mean" else 1.0
    lot_mean = p.nominal * (level_factor + truncated_normal(rng, p.lot_sd_frac, trunc["lot_offset"]))
    drift_mult = spec.get("lot_drift_multiplier", 1.0)
    lot_drift = p.nominal * rng.normal(p.lot_drift_mean_frac * drift_mult, p.lot_drift_sd_frac)

    offsets = truncated_normal(rng, p.comp_sd, trunc["component"], n)
    if scenario == "bimodal":
        offsets = offsets + np.where(wafers == "W1", -0.5, 0.5) * spec["bimodal_separation_sd"] * p.comp_sd
    comp_drift = truncated_normal(rng, p.comp_drift_sd_frac * p.nominal, trunc["component_drift"], n)

    fraction = rng.uniform(*spec["anomaly_fraction"])
    n_anom = int(round(fraction * n))
    anomalous = set(rng.choice(n, size=n_anom, replace=False).tolist()) if n_anom else set()

    healthy_shape_default = Shape("exp", raw["healthy_shape_tau_h"])
    faults = raw["faults"]
    rows = []
    for i in range(n):
        baseline = lot_mean + offsets[i]
        healthy_end = baseline + lot_drift + comp_drift[i]
        weights = raw["anomalous_family_weights"] if i in anomalous else raw["healthy_family_weights"]
        family = _weighted_choice(rng, weights, excluded)
        ctx = RowContext(
            direction=p.direction,
            comp_sd=p.comp_sd,
            drift_reference_sd=p.drift_reference_sd,
            limit=p.degradation_limit,
            baseline=baseline,
            healthy_end=healthy_end,
            healthy_tau_h=raw["healthy_shape_tau_h"],
        )
        b = sample_behaviour(family, rng, ctx, raw["family_params"], raw["severity"])
        healthy_part = (
            lot_drift * healthy_shape_default(hours, t_end)
            + comp_drift[i] * b.component_drift_scale * b.healthy_shape(hours, t_end)
        )
        true = baseline + b.level_offset + healthy_part + b.amplitude * b.shape(hours, t_end)

        noise_sd = p.meas_sd_frac * (np.abs(true) if p.meas_model == "proportional" else p.nominal) * b.meas_multiplier
        measured = true + rng.normal(0.0, 1.0, len(hours)) * noise_sd

        fault = "none"
        if scenario == "quantised":
            measured = np.round(measured / p.quantisation_step) * p.quantisation_step
            fault = "quantised"
        if not b.is_anomaly and rng.random() < faults["glitch_rate"]:
            idx = list(config.checkpoints).index(24)
            measured[idx] += (1.0 if rng.random() < 0.5 else -1.0) * faults["glitch_size_sd"] * p.comp_sd
            fault = "glitch"
        if rng.random() < faults["missing_value_rate"]:
            measured[int(rng.integers(len(hours)))] = np.nan
            fault = "missing_value"

        row: dict[str, Any] = {
            "component_id": f"{lot_id}-C{i + 1:04d}",
            "lot_id": lot_id,
            "wafer_id": f"{lot_id}-{wafers[i]}",
            "device_family": raw["device_family"],
            "parameter": p.name,
            "unit": p.unit,
        }
        for h, m, tv in zip(config.checkpoints, measured, true):
            row[VALUE_COLUMNS[h]] = float(m)
            row[f"true_{VALUE_COLUMNS[h]}"] = float(tv)
        row.update(
            spec_min=p.spec_min,
            spec_max=p.spec_max,
            data_category="synthetic",
            dataset_version=config.dataset_version,
            nominal_value=p.nominal,
            lot_scenario=scenario,
            behaviour_family=family,
            is_anomaly=b.is_anomaly,
            severity=b.severity,
            severity_band=severity_band(b.severity, raw["severity"]["band_edges"]),
            anomaly_amplitude=b.amplitude,
            level_offset=b.level_offset,
            noise_sd=float(np.max(noise_sd)),
            data_fault=fault,
        )
        rows.append(row)
    return rows
