import numpy as np
import pandas as pd
import pytest

from agnidrish.lot import level_and_drift_scores, lot_robust_z, robust_scale
from agnidrish.predict import fit_predictor, predict, predict_by_parameter
from agnidrish.schema import Checkpoint
from agnidrish.spec import spec_exceedance, spec_violation
from agnidrish.uncertainty import conformal_halfwidth

# Illustrative values only (arbitrary units).


def frame(v0, v24, v168=None, lot="L1", parameter="p", spec_min=np.nan, spec_max=50.0):
    n = len(v0)
    return pd.DataFrame({
        "component_id": [f"C{i}" for i in range(n)], "lot_id": lot, "parameter": parameter,
        "value_0h": v0, "value_24h": v24, "value_168h": v168 if v168 is not None else [np.nan] * n,
        "spec_min": spec_min, "spec_max": spec_max,
    })


def test_spec_violation_one_and_two_sided():
    t = frame([10.0, 10.0, 60.0], [51.0, 10.0, 10.0], spec_min=[np.nan, 11.0, np.nan])
    assert spec_violation(t, ["value_0h", "value_24h"]).tolist() == [True, True, True]
    assert spec_violation(t, ["value_24h"]).tolist() == [True, True, False]
    assert spec_exceedance(t, t["value_24h"]).iloc[0] == pytest.approx(1 / 50)


def test_robust_scales_hand_computed():
    v = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    assert robust_scale(v, "iqr") == pytest.approx((4.0 - 2.0) / 1.35)
    assert robust_scale(v, "mad") == pytest.approx(1.4826 * 1.0)


def test_robust_z_and_degenerate_lot_gives_nan():
    t = frame([0.0] * 5, [1.0, 2.0, 3.0, 4.0, 5.0])
    z = lot_robust_z(t, t["value_24h"], "iqr", {"p": 0.01})
    # median 3, IQR 2 -> scale 2/1.35; z = (v - 3) * 1.35 / 2
    assert z["z"].tolist() == pytest.approx([-1.35, -0.675, 0.0, 0.675, 1.35])
    flat = frame([0.0] * 5, [3.0, 3.0, 3.0, 3.0, 9.0])
    assert lot_robust_z(flat, flat["value_24h"], "iqr", {"p": 0.01})["z"].isna().all()


def test_level_and_drift_use_only_checkpoint_columns():
    t = frame([1.0, 2.0, 3.0, 4.0, 5.0], [1.5, 2.5, 3.5, 4.5, 9.0], v168=[0.0] * 5)
    s = level_and_drift_scores(t, Checkpoint.T24, "iqr", {"p": 0.01})
    assert s["drift"].tolist() == [0.5, 0.5, 0.5, 0.5, 4.0]
    t2 = t.assign(value_168h=[999.0] * 5)
    pd.testing.assert_frame_equal(s, level_and_drift_scores(t2, Checkpoint.T24, "iqr", {"p": 0.01}))


def test_predictors_hand_computed():
    train = frame([10.0, 20.0], [11.0, 22.0], v168=[13.0, 26.0])
    new = frame([10.0], [12.0])
    assert predict(fit_predictor("persistence", train), new).iloc[0] == 12.0
    assert predict(fit_predictor("linear_extrapolation", train), new).iloc[0] == pytest.approx(12.0 + 2.0 * 6)
    inc = fit_predictor("population_increment", train)  # median(v168 - v24) = median(2, 4) = 3
    assert predict(inc, new).iloc[0] == pytest.approx(15.0)


def test_prediction_never_reads_value_168h():
    train = frame([10.0, 20.0, 30.0], [11.0, 23.0, 31.0], v168=[13.0, 29.0, 35.0])
    model = fit_predictor("linear_regression", train)
    a = predict_by_parameter({"p": model}, train)
    b = predict_by_parameter({"p": model}, train.assign(value_168h=np.nan))
    pd.testing.assert_series_equal(a, b)


def test_conformal_halfwidth_rank():
    true = pd.Series(np.arange(1.0, 10.0))  # 9 calibration rows
    pred = pd.Series(np.zeros(9))
    # alpha 0.2 -> k = ceil(10 * 0.8) = 8 -> 8th smallest |residual| = 8
    assert conformal_halfwidth(true, pred, 0.2) == 8.0
    assert conformal_halfwidth(true.iloc[:3], pred.iloc[:3], 0.1) == float("inf")
