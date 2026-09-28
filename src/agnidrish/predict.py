"""Layer L4 — Module B: predict value_168h from value_0h and value_24h (FR-07).

Simple baselines only (CLAUDE §3–§4). Fitting reads value_168h of TRAINING rows;
prediction reads only value_0h and value_24h, per parameter. Units = parameter unit.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

MODELS: tuple[str, ...] = ("persistence", "linear_extrapolation", "population_increment", "linear_regression")
T0, T24, T168 = 0.0, 24.0, 168.0


@dataclass(frozen=True)
class Predictor:
    name: str
    params: dict[str, list[float]] = field(default_factory=dict)  # per parameter

    def to_dict(self) -> dict:
        return {"name": self.name, "params": self.params}


def fit_predictor(name: str, train: pd.DataFrame) -> Predictor:
    """Fit on training rows with value_0h, value_24h and value_168h all present."""
    if name not in MODELS:
        raise ValueError(f"unknown predictor {name!r}")
    ok = train[["value_0h", "value_24h", "value_168h"]].notna().all(axis=1)
    rows = train[ok]
    params: dict[str, list[float]] = {}
    for parameter, g in rows.groupby("parameter"):
        if name == "population_increment":
            params[parameter] = [float((g["value_168h"] - g["value_24h"]).median())]
        elif name == "linear_regression":
            x = np.column_stack([np.ones(len(g)), g["value_0h"], g["value_24h"]])
            coef, *_ = np.linalg.lstsq(x, g["value_168h"].to_numpy(), rcond=None)
            params[parameter] = [float(c) for c in coef]
    return Predictor(name, params)


def predict(model: Predictor, table: pd.DataFrame) -> pd.Series:
    """Predicted value_168h; NaN if an input is missing or the parameter was not fitted."""
    v0, v24 = table["value_0h"], table["value_24h"]
    match model.name:
        case "persistence":
            pred = v24.copy()
        case "linear_extrapolation":
            pred = v24 + (v24 - v0) * (T168 - T24) / (T24 - T0)
        case "population_increment":
            inc = table["parameter"].map({p: c[0] for p, c in model.params.items()})
            pred = v24 + inc
        case "linear_regression":
            coef = {p: c for p, c in model.params.items()}
            a = table["parameter"].map({p: c[0] for p, c in coef.items()})
            b = table["parameter"].map({p: c[1] for p, c in coef.items()})
            c = table["parameter"].map({p: c[2] for p, c in coef.items()})
            pred = a + b * v0 + c * v24
        case _:
            raise ValueError(f"unknown predictor {model.name!r}")
    return pred.rename("pred_168h")


def predictor_from_dict(data: dict) -> Predictor:
    return Predictor(data["name"], {k: list(v) for k, v in data.get("params", {}).items()})


def predict_by_parameter(models: dict[str, Predictor], table: pd.DataFrame) -> pd.Series:
    """Apply one predictor per parameter (MAE is compared per parameter because units differ)."""
    pred = pd.Series(np.nan, index=table.index, name="pred_168h")
    for parameter, model in models.items():
        rows = table["parameter"] == parameter
        pred[rows] = predict(model, table[rows])
    return pred
