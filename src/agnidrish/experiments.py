"""Experiments E1-E6 as a cumulative ablation (experiment-plan.md, ablation-plan.md).

All development choices (predictor per parameter, conformal half-widths,
REVIEW z threshold) are made on train / calibration / validation lots only and
frozen into a PipelineSpec; the test split is evaluated once with that spec.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import numpy as np
import pandas as pd

from agnidrish.decision import DecisionConfig, decide
from agnidrish.labels import Allowance, label_safety_slope, label_spec_168h
from agnidrish.metrics import (
    average_precision,
    detection_metrics,
    interval_metrics,
    operational_metrics,
    regression_metrics,
    tail_mae,
)
from agnidrish.pipeline import PipelineSpec, evidence
from agnidrish.predict import MODELS, fit_predictor, predict, predict_by_parameter
from agnidrish.spec import spec_exceedance
from agnidrish.uncertainty import fit_halfwidths

STAGES: tuple[str, ...] = ("E1", "E2", "E3", "E4", "E5", "E6")


def primary_label(table: pd.DataFrame, cfg: dict[str, Any]) -> pd.Series:
    lab = cfg["label"]
    allowance = {p: Allowance(lab["allowance"]["kind"], lab["allowance"]["value"]) for p in lab["directions"]}
    return label_safety_slope(table, allowance, lab["directions"])


def stage_decision_config(stage: str, z_reject: float, z_review_e6: float) -> DecisionConfig:
    """Cumulative layers: E1 static; E2 + lot level; E3 + lot drift; E4 + prediction; E5 + interval; E6 + tuned REVIEW z."""
    n = STAGES.index(stage)
    return DecisionConfig(
        use_lot_level=n >= 1,
        use_lot_drift=n >= 2,
        use_prediction=n >= 3,
        use_interval=n >= 4,
        z_review=z_review_e6 if stage == "E6" else z_reject,
        z_reject=z_reject,
    )


def base_spec(cfg: dict[str, Any]) -> PipelineSpec:
    lab, gate, lot = cfg["label"], cfg["quality_gate"], cfg["lot_relative"]
    return PipelineSpec(
        checkpoint=cfg["checkpoint"],
        min_lot_size=gate["min_lot_size"],
        scale_floor_fraction=gate["scale_floor_fraction_of_nominal"],
        scale_method=lot["scale"],
        allowance_kind=lab["allowance"]["kind"],
        allowance_value=lab["allowance"]["value"],
        directions=dict(lab["directions"]),
        decision=DecisionConfig(z_review=lot["reject_z"], z_reject=lot["reject_z"]),
    )


def compare_predictors(train: pd.DataFrame, evaluation: pd.DataFrame, tail_q: float) -> dict[str, Any]:
    """E4: every baseline, per parameter (units differ, so MAE is never pooled)."""
    out: dict[str, Any] = {}
    groups = evaluation["lot_id"] + "/" + evaluation["parameter"]
    for name in MODELS:
        model = fit_predictor(name, train)
        pred = predict(model, evaluation)
        per_param = {}
        for p, rows in evaluation.groupby("parameter").groups.items():
            reg = regression_metrics(evaluation.loc[rows, "value_168h"], pred.loc[rows])
            reg["tail_mae"] = tail_mae(evaluation.loc[rows, "value_168h"], pred.loc[rows], groups.loc[rows], tail_q)
            per_param[p] = reg
        out[name] = {"model": model.to_dict(), "per_parameter": per_param}
    return out


def select_predictors(comparison: dict[str, Any]) -> dict[str, str]:
    """Lowest validation MAE per parameter (pre-registered rule, applied per parameter)."""
    params = next(iter(comparison.values()))["per_parameter"].keys()
    return {p: min(comparison, key=lambda m: comparison[m]["per_parameter"][p]["mae"]) for p in params}


def select_operating_point(label: pd.Series, decisions: dict[float, pd.DataFrame], target_recall: float) -> dict[str, Any]:
    """ADR-005: lowest review rate reaching R* (REVIEW flagged); ties -> lower false-rejection rate.

    If no setting reaches R*, the highest-recall setting is returned with reached=False.
    """
    rows = []
    for z, d in decisions.items():
        det = detection_metrics(label, d["binary_flag"])
        ops = operational_metrics(label, d["decision"])
        rows.append({"z_review": z, "recall": det["recall"], "review_rate": ops["review_rate"],
                     "false_rejection_rate": ops["false_rejection_rate"]})
    curve = pd.DataFrame(rows)
    ok = curve[curve["recall"] >= target_recall]
    if ok.empty:
        best = curve.sort_values(["recall", "review_rate"], ascending=[False, True]).iloc[0]
        reached = False
    else:
        best = ok.sort_values(["review_rate", "false_rejection_rate"]).iloc[0]
        reached = True
    return {"z_review": float(best["z_review"]), "reached_target": reached, "curve": curve.to_dict(orient="records")}


def stage_score(stage: str, table: pd.DataFrame, ev: pd.DataFrame) -> pd.Series | None:
    """Ranking score for PR-AUC (score-based detectors E1-E3 only)."""
    if stage == "E1":
        return pd.concat([spec_exceedance(table, table["value_0h"]), spec_exceedance(table, table["value_24h"])], axis=1).max(axis=1)
    if stage == "E2":
        return ev["z_level"].abs()
    if stage == "E3":
        return ev[["z_level", "z_drift"]].abs().max(axis=1)
    return None


def evaluate(table: pd.DataFrame, label: pd.Series, result: pd.DataFrame, score: pd.Series | None) -> dict[str, Any]:
    truth = table["is_anomaly"].astype("boolean") if "is_anomaly" in table.columns else None
    out: dict[str, Any] = {
        "primary_label": detection_metrics(label, result["binary_flag"]),
        "operational": operational_metrics(label, result["decision"]),
        "decisions": result["decision"].value_counts().to_dict(),
        # Diagnostic: rows not sent to REVIEW by the quality gate, so layer effects are not masked by L0.
        "primary_label_ungated": detection_metrics(label[~result["gate_flag"]], result.loc[~result["gate_flag"], "binary_flag"]),
    }
    if score is not None:
        out["primary_label"]["pr_auc"] = average_precision(label, score)
    if truth is not None:
        out["scenario_truth"] = detection_metrics(truth, result["binary_flag"])
        out["flag_rate_by_family"] = (
            result["binary_flag"].groupby(table["behaviour_family"]).mean().round(4).to_dict()
        )
    return out


def run_stages(
    table: pd.DataFrame,
    eval_rows: pd.Series,
    spec_by_stage: dict[str, PipelineSpec],
    label: pd.Series,
) -> dict[str, Any]:
    """Evaluate each stage's frozen spec on ``eval_rows`` (evidence computed on whole lots)."""
    results = {}
    for stage, spec in spec_by_stage.items():
        ev = evidence(table, spec)
        res = ev.join(decide(ev, spec.decision))
        sub = eval_rows
        results[stage] = evaluate(table[sub], label[sub], res[sub], None if (s := stage_score(stage, table, ev)) is None else s[sub])
    return results


def develop(table: pd.DataFrame, cfg: dict[str, Any]) -> dict[str, Any]:
    """Fit on train/calibration, choose on validation, return per-stage specs and all development results."""
    split = table["split"]
    train, cal = table[split == cfg["dataset"]["fit_splits"]["model"]], table[split == cfg["dataset"]["fit_splits"]["conformal"]]
    val_rows = split == cfg["dataset"]["development_split"]
    label = primary_label(table, cfg)
    z_rej = cfg["lot_relative"]["reject_z"]

    comparison = compare_predictors(train, table[val_rows], cfg["prediction"]["tail_quantile"])
    chosen = select_predictors(comparison)
    predictors = {p: fit_predictor(name, train) for p, name in chosen.items()}
    halfwidths = fit_halfwidths(cal, predict_by_parameter(predictors, cal), cfg["uncertainty"]["alpha"])

    base = base_spec(cfg)
    specs = {}
    for stage in STAGES[:5]:
        specs[stage] = replace(
            base,
            decision=stage_decision_config(stage, z_rej, z_rej),
            predictors=predictors if STAGES.index(stage) >= 3 else {},
            halfwidths=halfwidths if STAGES.index(stage) >= 4 else {},
        )

    # E6: choose the REVIEW z threshold on validation (ADR-005).
    e5_ev = evidence(table, specs["E5"])
    candidates = {
        z: decide(e5_ev, stage_decision_config("E6", z_rej, z))[val_rows]
        for z in cfg["lot_relative"]["review_z_grid"]
    }
    op = select_operating_point(label[val_rows], candidates, cfg["operating_point"]["target_recall"])
    specs["E6"] = replace(specs["E5"], decision=stage_decision_config("E6", z_rej, op["z_review"]))

    pred_val = predict_by_parameter(predictors, table[val_rows])
    pi_low = pred_val - table.loc[val_rows, "parameter"].map(halfwidths)
    pi_high = pred_val + table.loc[val_rows, "parameter"].map(halfwidths)
    val = table[val_rows]
    coverage = {
        "overall": interval_metrics(val["value_168h"], pi_low, pi_high),
        "per_parameter": {
            p: interval_metrics(val.loc[r, "value_168h"], pi_low[r], pi_high[r]) for p, r in val.groupby("parameter").groups.items()
        },
        "per_lot_coverage": _per_group_coverage(val, pi_low, pi_high, "lot_id"),
    }
    if "lot_scenario" in val.columns:  # synthetic ground truth; absent in real historical data
        coverage["per_scenario_coverage"] = _per_group_coverage(val, pi_low, pi_high, "lot_scenario")
    return {
        "specs": specs,
        "predictor_comparison": comparison,
        "chosen_predictors": chosen,
        "halfwidths": halfwidths,
        "operating_point": op,
        "coverage_validation": coverage,
        "stages": run_stages(table, val_rows, specs, label),
        "label_positives": {s: int(label[split == s].sum()) for s in split.unique()},
        "label_spec_168h_positives_validation": int(label_spec_168h(val).sum()),
    }


def _per_group_coverage(table: pd.DataFrame, low: pd.Series, high: pd.Series, key: str) -> dict[str, float]:
    inside = (table["value_168h"] >= low) & (table["value_168h"] <= high)
    ok = table["value_168h"].notna() & low.notna()
    return {str(k): round(float(v), 4) for k, v in inside[ok].groupby(table.loc[ok, key]).mean().items()}


def to_jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, PipelineSpec):
        return obj.to_dict()
    if isinstance(obj, (np.floating, float)):
        return None if not np.isfinite(obj) else float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj
