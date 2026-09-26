import numpy as np
import pandas as pd
import pytest

from agnidrish.metrics import (
    average_precision,
    detection_metrics,
    interval_metrics,
    operational_metrics,
    regression_metrics,
    tail_mae,
)


def test_detection_metrics_hand_computed_and_skip_unlabelled():
    label = pd.Series([True, True, False, False, False, pd.NA], dtype="boolean")
    flag = pd.Series([True, False, True, False, False, True])
    m = detection_metrics(label, flag)
    assert (m["tp"], m["fn"], m["fp"], m["tn"], m["n_unlabelled"]) == (1, 1, 1, 2, 1)
    assert m["recall"] == 0.5 and m["precision"] == 0.5 and m["fpr"] == pytest.approx(1 / 3)


def test_undefined_ratios_are_nan():
    m = detection_metrics(pd.Series([False, False]), pd.Series([False, False]))
    assert np.isnan(m["recall"]) and np.isnan(m["precision"])


def test_average_precision_hand_computed():
    # ranked labels: T, F, T  -> precisions at hits 1/1 and 2/3 -> AP = (1 + 2/3) / 2
    ap = average_precision(pd.Series([True, False, True]), pd.Series([0.9, 0.8, 0.1]))
    assert ap == pytest.approx((1 + 2 / 3) / 2)
    assert average_precision(pd.Series([True, False]), pd.Series([np.nan, 1.0])) == pytest.approx(0.5)


def test_regression_and_tail_mae():
    true = pd.Series([1.0, 2.0, 10.0, 20.0])
    pred = pd.Series([2.0, 2.0, 12.0, 20.0])
    r = regression_metrics(true, pred)
    assert r["mae"] == pytest.approx(0.75) and r["rmse"] == pytest.approx(np.sqrt(5 / 4))
    groups = pd.Series(["a", "a", "b", "b"])
    assert tail_mae(true, pred, groups, 0.9) == pytest.approx(0.0)  # tails: 2.0 (err 0) and 20.0 (err 0)


def test_interval_and_operational_metrics():
    cov = interval_metrics(pd.Series([1.0, 5.0]), pd.Series([0.0, 0.0]), pd.Series([2.0, 2.0]))
    assert cov["coverage"] == 0.5 and cov["mean_width"] == 2.0
    label = pd.Series([True, True, False, False])
    dec = pd.Series(["PASS", "REJECT", "REJECT", "REVIEW"])
    ops = operational_metrics(label, dec)
    assert ops["defect_escape_rate"] == 0.5 and ops["false_rejection_rate"] == 0.5
    assert ops["review_rate"] == 0.25 and ops["auto_cleared"] == 0.25
