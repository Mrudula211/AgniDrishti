"""E0 data audit: dataset invariants and statistics. Fails loudly on any violated invariant.

``run_audit`` applies generic checks to any canonical table; with a synthetic
``GeneratorConfig`` it also checks the generator's documented invariants
(synthetic-data-design.md §9).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from agnidrish.labels import Allowance, label_safety_slope, label_spec_168h
from agnidrish.schema import DATA_CATEGORIES, SPEC_COLUMNS, VALUE_COLUMNS, Checkpoint, required_columns
from agnidrish.synthetic.config import SPLITS, GeneratorConfig
from agnidrish.synthetic.families import ANOMALOUS_FAMILIES, FAMILY_KINDS, Kind, severity_band

FORBIDDEN_FAMILY_MARKERS = ("19", "20", "heldout", "held_out", "hidden")


class AuditError(AssertionError):
    """One or more dataset invariants are violated."""

    def __init__(self, violations: list[str], report: dict[str, Any]):
        self.violations = violations
        self.report = report
        super().__init__("E0 audit failed:\n- " + "\n- ".join(violations))


def run_audit(table: pd.DataFrame, config: GeneratorConfig | None = None) -> dict[str, Any]:
    """Return audit statistics; raise AuditError listing every violated invariant."""
    violations: list[str] = []
    report: dict[str, Any] = {}
    _check_generic(table, violations, report)
    if config is not None and not violations:
        _check_synthetic(table, config, violations, report)
    if violations:
        raise AuditError(violations, report)
    return report


def _check_generic(table: pd.DataFrame, violations: list[str], report: dict[str, Any]) -> None:
    missing_cols = [c for c in required_columns(Checkpoint.T24) if c not in table.columns]
    if missing_cols:
        violations.append(f"schema: missing required columns {missing_cols}")
        return
    value_cols = [c for c in VALUE_COLUMNS.values() if c in table.columns]
    for col in value_cols + list(SPEC_COLUMNS):
        if not pd.api.types.is_numeric_dtype(table[col]):
            violations.append(f"schema: {col} is not numeric")

    categories = set(table["data_category"].unique())
    if len(categories) != 1 or not categories <= DATA_CATEGORIES:
        violations.append(f"provenance: data_category must be one valid value, got {sorted(categories)}")
    if table["dataset_version"].nunique() != 1:
        violations.append("provenance: dataset_version must be a single value")

    for col in ("component_id", "lot_id", "parameter"):
        if table[col].isna().any():
            violations.append(f"identifiers: {col} has missing values")
    dup = table.duplicated(["component_id", "parameter"]).sum()
    if dup:
        violations.append(f"duplicates: {dup} duplicate (component_id, parameter) rows")
    lots_per_component = table.groupby("component_id")["lot_id"].nunique()
    if (lots_per_component > 1).any():
        violations.append(f"duplicates: {int((lots_per_component > 1).sum())} component_ids appear in more than one lot")

    both_missing = table["spec_min"].isna() & table["spec_max"].isna()
    if both_missing.any():
        violations.append(f"spec: {int(both_missing.sum())} rows have no spec limit")
    inverted = (table["spec_min"] >= table["spec_max"]).sum()
    if inverted:
        violations.append(f"spec: {inverted} rows have spec_min >= spec_max")
    per_param = table.groupby("parameter")[list(SPEC_COLUMNS)].nunique(dropna=False)
    if (per_param > 1).any().any():
        violations.append("spec: datasheet limits differ within a parameter")

    if "split" in table.columns:
        unknown = set(table["split"].unique()) - set(SPLITS)
        if unknown:
            violations.append(f"split: unknown values {sorted(map(str, unknown))}")
        for key in ("lot_id", "component_id"):
            leaking = int((table.groupby(key)["split"].nunique() > 1).sum())
            if leaking:
                violations.append(f"split leakage: {leaking} {key}s appear in more than one split")
        absent = set(SPLITS) - set(table["split"].unique())
        if absent:
            violations.append(f"split: empty splits {sorted(absent)}")
        report["splits"] = {
            s: {
                "lots": int(g["lot_id"].nunique()),
                "components": int(g["component_id"].nunique()),
                "rows": int(len(g)),
                **({"anomalous_rows": int(g["is_anomaly"].sum())} if "is_anomaly" in g else {}),
            }
            for s, g in table.groupby("split", sort=False)
        }

    sizes = table.groupby("lot_id")["component_id"].nunique()
    report.update(
        rows=int(len(table)),
        lots=int(table["lot_id"].nunique()),
        components=int(table["component_id"].nunique()),
        parameters=sorted(table["parameter"].unique().tolist()),
        lot_size={"min": int(sizes.min()), "median": float(sizes.median()), "max": int(sizes.max())},
        missing_values={c: int(table[c].isna().sum()) for c in value_cols},
    )


def _within_spec(values: pd.DataFrame, table: pd.DataFrame) -> pd.Series:
    above = values.gt(table["spec_max"], axis=0).any(axis=1)
    below = values.lt(table["spec_min"], axis=0).any(axis=1)
    return ~(above | below)


def _near_limit(value: pd.Series, table: pd.DataFrame, band: float) -> pd.Series:
    nominal = table["nominal_value"]
    near_upper = value >= table["spec_max"] - band * (table["spec_max"] - nominal).abs()
    near_lower = value <= table["spec_min"] + band * (nominal - table["spec_min"]).abs()
    return near_upper.fillna(False) | near_lower.fillna(False)


def spec_scenarios(table: pd.DataFrame, near_band: float) -> dict[str, int]:
    """Counts of the specification scenarios A-E, from TRUE (noise-free) values."""
    true_cols = [f"true_{c}" for c in VALUE_COLUMNS.values() if f"true_{c}" in table.columns]
    true = table[true_cols]
    within = _within_spec(true, table)
    start_in = _within_spec(true[[true_cols[0]]], table)
    end_in = _within_spec(true[[true_cols[-1]]], table)
    start_near = _near_limit(table[true_cols[0]], table, near_band)
    end_near = _near_limit(table[true_cols[-1]], table, near_band)
    max_near = pd.concat([_near_limit(table[c], table, near_band) for c in true_cols], axis=1).any(axis=1)
    kind = table["behaviour_family"].map(FAMILY_KINDS)
    anomalous = table["is_anomaly"].astype(bool)
    return {
        "A_healthy_within_spec": int((~anomalous & within).sum()),
        "healthy_near_spec": int((~anomalous & within & max_near).sum()),
        "B_anomalous_trajectory_within_spec": int((anomalous & within & kind.isin([Kind.DRIFT, Kind.SPEC])).sum()),
        "C_approaching_limit": int((anomalous & within & end_near & ~start_near).sum()),
        "D_crossing_limit": int((start_in & ~end_in).sum()),
        "E_lot_relative_abnormal_within_spec": int(((table["behaviour_family"] == "level_outlier") & within).sum()),
        "starts_outside_spec": int((~start_in).sum()),
    }


def _check_synthetic(table: pd.DataFrame, config: GeneratorConfig, violations: list[str], report: dict[str, Any]) -> None:
    raw = config.raw
    if set(table["data_category"]) != {"synthetic"}:
        violations.append("provenance: synthetic dataset must have data_category 'synthetic'")
    if set(table["dataset_version"]) != {config.dataset_version}:
        violations.append(f"provenance: dataset_version must be {config.dataset_version}")

    value_cols = [VALUE_COLUMNS[h] for h in config.checkpoints]
    true_cols = [f"true_{c}" for c in value_cols]
    absent = [c for c in value_cols + true_cols if c not in table.columns]
    if absent:
        violations.append(f"timestamps: checkpoint columns missing {absent}")
        return

    families = set(table["behaviour_family"].unique())
    configured = {f for f, w in {**raw["healthy_family_weights"], **raw["anomalous_family_weights"]}.items() if w > 0}
    if not families <= set(FAMILY_KINDS):
        violations.append(f"families: unknown families {sorted(families - set(FAMILY_KINDS))}")
    forbidden = [f for f in families if any(m in f.lower() for m in FORBIDDEN_FAMILY_MARKERS)]
    if forbidden:
        violations.append(f"families: held-out-like family names present {forbidden}")
    never_seen = configured - families
    if never_seen:
        violations.append(f"families: configured families never generated {sorted(never_seen)}")

    expected_anomaly = table["behaviour_family"].isin(ANOMALOUS_FAMILIES)
    if (table["is_anomaly"].astype(bool) != expected_anomaly).any():
        violations.append("anomaly: is_anomaly disagrees with the family registry")

    healthy = ~table["is_anomaly"].astype(bool)
    if table.loc[healthy, "severity"].notna().any() or (table.loc[healthy, "severity_band"] != "none").any():
        violations.append("severity: healthy rows must have no severity")
    sev = table.loc[~healthy, "severity"]
    if not (np.isfinite(sev) & (sev > 0)).all():
        violations.append("severity: anomalous rows need a finite positive severity")
    bands = table.loc[~healthy, "severity"].map(lambda k: severity_band(k, raw["severity"]["band_edges"]))
    if (bands != table.loc[~healthy, "severity_band"]).any():
        violations.append("severity: severity_band inconsistent with severity")

    lots = table.groupby("lot_id").agg(scenario=("lot_scenario", "first"), size=("component_id", "nunique"))
    for scenario, spec in raw["lot_scenarios"].items():
        in_scenario = lots[lots["scenario"] == scenario]
        if len(in_scenario) != spec["n_lots"]:
            violations.append(f"lots: {scenario} has {len(in_scenario)} lots, expected {spec['n_lots']}")
        lo, hi = spec["size"]
        if not in_scenario["size"].between(lo, hi).all():
            violations.append(f"lots: {scenario} lot size outside [{lo}, {hi}]")
    counts = table.groupby(["lot_id", "parameter"]).agg(
        scenario=("lot_scenario", "first"), n=("component_id", "nunique"), anomalies=("is_anomaly", "sum")
    )
    for (lot_id, parameter), row in counts.iterrows():
        flo, fhi = raw["lot_scenarios"][row["scenario"]]["anomaly_fraction"]
        if not round(flo * row["n"]) <= row["anomalies"] <= round(fhi * row["n"]):
            violations.append(f"anomaly: {lot_id}/{parameter} has {row['anomalies']} anomalies, outside configured fraction")
    if counts.loc[counts["scenario"] == "normal", "anomalies"].sum() != 0:
        violations.append("anomaly: normal lots must contain no anomalies")

    true = table[true_cols]
    healthy_outside = int((healthy & ~_within_spec(true, table)).sum())
    if healthy_outside:
        violations.append(f"spec: {healthy_outside} healthy rows leave the spec window (true values)")

    tol_sd = raw["audit"]["value_tolerance_sd"]
    steps = table["parameter"].map({p.name: p.quantisation_step for p in config.parameters})
    comp_sd = table["parameter"].map({p.name: p.comp_sd for p in config.parameters})
    quant = np.where(table["lot_scenario"] == "quantised", steps / 2.0, 0.0)
    fault = table["data_fault"]
    for col, tcol in zip(value_cols, true_cols):
        dev = (table[col] - table[tcol]).abs()
        allowed = tol_sd * table["noise_sd"] + quant
        if col == "value_24h":
            allowed = allowed + np.where(fault == "glitch", raw["faults"]["glitch_size_sd"] * comp_sd, 0.0)
        bad = (dev > allowed) & table[col].notna()
        if bad.any():
            violations.append(f"values: {int(bad.sum())} rows where {col} is inconsistent with {tcol}")
    if table.loc[fault == "glitch", "is_anomaly"].astype(bool).any():
        violations.append("faults: glitches must only be injected into healthy rows")
    n_missing = table[value_cols].isna().sum(axis=1)
    if ((n_missing > 0) != (fault == "missing_value")).any() or (n_missing > 1).any():
        violations.append("values: missing values must occur exactly once, only in rows marked missing_value")
    if table[true_cols].isna().any().any():
        violations.append("values: true values must never be missing")

    scenarios = spec_scenarios(table, raw["audit"]["near_spec_band"])
    empty = [k for k, v in scenarios.items() if v == 0]
    if empty:
        violations.append(f"spec scenarios: no examples of {empty}")

    report.update(
        dataset_version=config.dataset_version,
        seed=config.seed,
        lot_scenarios=lots["scenario"].value_counts().sort_index().to_dict(),
        families=table["behaviour_family"].value_counts().sort_index().to_dict(),
        anomalous_rows=int(table["is_anomaly"].sum()),
        normal_rows=int(healthy.sum()),
        components_with_any_anomaly=int(table.groupby("component_id")["is_anomaly"].any().sum()),
        severity_bands=table["severity_band"].value_counts().sort_index().to_dict(),
        severity_quantiles={
            q: float(sev.quantile(q)) for q in (0.0, 0.25, 0.5, 0.75, 1.0)
        },
        data_faults=fault.value_counts().sort_index().to_dict(),
        spec_scenarios=scenarios,
        label_prevalence=_label_prevalence(table, config),
    )


def _label_prevalence(table: pd.DataFrame, config: GeneratorConfig) -> dict[str, Any]:
    """Share of rows with label_spec_168h / label_safety_slope across the pre-registered Δ grid."""
    grid = config.raw["allowance_grid"]
    direction = {p.name: "up" if p.direction > 0 else "down" for p in config.parameters}
    out: dict[str, Any] = {"label_spec_168h": float(label_spec_168h(table).mean())}
    for r in grid["relative"]:
        allowance = {p.name: Allowance("relative", r) for p in config.parameters}
        out[f"label_safety_slope@relative={r}"] = float(label_safety_slope(table, allowance, direction).mean())
    for i in range(len(next(iter(grid["absolute"].values())))):
        allowance = {p: Allowance("absolute", values[i]) for p, values in grid["absolute"].items()}
        key = ",".join(f"{p}={values[i]}" for p, values in grid["absolute"].items())
        out[f"label_safety_slope@absolute[{key}]"] = float(label_safety_slope(table, allowance, direction).mean())
    return out


def check_reproducible(table: pd.DataFrame, config: GeneratorConfig) -> None:
    """Regenerate from ``config`` and raise AuditError unless the result is identical."""
    from agnidrish.synthetic.generator import generate

    again = generate(config)
    if not again.equals(table):
        raise AuditError(["reproducibility: regenerating with the same config and seed gave a different dataset"], {})
