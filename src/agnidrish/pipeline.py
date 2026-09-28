"""End-to-end screening at one checkpoint: L0 gate -> L1 spec -> L2 lot scores ->
L4 prediction + safety-slope test -> L5 interval -> L6 decision.

A ``PipelineSpec`` is frozen from development results (experiments on
validation lots) and then applied unchanged to test lots or new data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np
import pandas as pd

from agnidrish.decision import DecisionConfig, decide, exceeds_safety_slope
from agnidrish.lot import level_and_drift_scores, scale_floor_from_nominal
from agnidrish.predict import Predictor, predict_by_parameter, predictor_from_dict
from agnidrish.quality import QualityConfig, review_mask, run_quality_gate
from agnidrish.schema import Checkpoint, available_value_columns
from agnidrish.spec import spec_violation
from agnidrish.uncertainty import interval


@dataclass
class PipelineSpec:
    checkpoint: str
    min_lot_size: int
    scale_floor_fraction: float
    scale_method: str
    allowance_kind: str
    allowance_value: float
    directions: dict[str, str]
    decision: DecisionConfig
    predictors: dict[str, Predictor] = field(default_factory=dict)  # per parameter
    halfwidths: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # The safety-slope test and the optimistic/pessimistic interval ends need a signed direction.
        bad = sorted(p for p, d in self.directions.items() if d not in ("up", "down"))
        if bad:
            raise ValueError(f"pipeline directions must be 'up' or 'down'; got {[(p, self.directions[p]) for p in bad]}")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["predictors"] = {p: m.to_dict() for p, m in self.predictors.items()}
        return d

    @staticmethod
    def from_dict(d: dict) -> PipelineSpec:
        return PipelineSpec(
            checkpoint=d["checkpoint"],
            min_lot_size=d["min_lot_size"],
            scale_floor_fraction=d["scale_floor_fraction"],
            scale_method=d["scale_method"],
            allowance_kind=d["allowance_kind"],
            allowance_value=d["allowance_value"],
            directions=dict(d["directions"]),
            decision=DecisionConfig(**d["decision"]),
            predictors={p: predictor_from_dict(m) for p, m in d.get("predictors", {}).items()},
            halfwidths={k: float(v) for k, v in d.get("halfwidths", {}).items()},
        )


def gate_codes(table: pd.DataFrame, flags: pd.DataFrame) -> pd.Series:
    """Per-row ';'-joined quality-flag codes (component and lot level)."""
    codes = pd.Series("", index=table.index, dtype=object)
    comp = flags[flags["level"] == "component"]
    for row, g in comp.groupby("row"):
        codes[row] = ";".join(sorted(set(map(str, g["code"]))))
    lot = flags[flags["level"] == "lot"]
    for (lot_id, parameter), g in lot.groupby(["lot_id", "parameter"]):
        hit = (table["lot_id"] == lot_id) & (table["parameter"] == parameter)
        lot_code = ";".join(sorted(set(map(str, g["code"]))))
        codes[hit] = [";".join(filter(None, (c, lot_code))) for c in codes[hit]]
    return codes


def evidence(table: pd.DataFrame, spec: PipelineSpec) -> pd.DataFrame:
    """All per-row evidence used by the decision rules and the explanations."""
    checkpoint = Checkpoint[spec.checkpoint]
    floors = scale_floor_from_nominal(table, spec.scale_floor_fraction)
    gate_config = QualityConfig(min_lot_size=spec.min_lot_size, scale_floor=floors)
    flags = run_quality_gate(table, checkpoint, gate_config)
    out = pd.DataFrame(index=table.index)
    out["gate_flag"] = review_mask(table, flags)
    out["gate_codes"] = gate_codes(table, flags)
    out["spec_now"] = spec_violation(table, available_value_columns(checkpoint))
    out = out.join(level_and_drift_scores(table, checkpoint, spec.scale_method, floors))

    if spec.predictors:
        pred = predict_by_parameter(spec.predictors, table)
        out["pred_168h"] = pred
        direction = table["parameter"].map({p: 1.0 if d == "up" else -1.0 for p, d in spec.directions.items()})
        relative = spec.allowance_kind == "relative"
        rel = pd.Series(relative, index=table.index)
        allow = pd.Series(spec.allowance_value, index=table.index)

        def exceeds(value: pd.Series) -> pd.Series:
            return exceeds_safety_slope(table["value_0h"], value, allow, rel, direction, table["spec_min"], table["spec_max"])

        out["pred_drift_rate_per_h"] = (pred - table["value_0h"]) / 168.0
        out["safety_slope_per_h"] = np.where(relative, spec.allowance_value * table["value_0h"].abs(), spec.allowance_value) / 168.0
        out["exceed_point"] = exceeds(pred)
        if spec.halfwidths:
            pi = interval(table, pred, spec.halfwidths)
            out = out.join(pi)
            optimistic = pi["pi_low"].where(direction > 0, pi["pi_high"])
            pessimistic = pi["pi_high"].where(direction > 0, pi["pi_low"])
            out["exceed_optimistic"] = exceeds(optimistic)
            out["exceed_pessimistic"] = exceeds(pessimistic)
    return out


def screen(table: pd.DataFrame, spec: PipelineSpec) -> pd.DataFrame:
    """Evidence plus ``decision``, ``fired_rules`` and ``binary_flag`` for every row."""
    ev = evidence(table, spec)
    return ev.join(decide(ev, spec.decision))
