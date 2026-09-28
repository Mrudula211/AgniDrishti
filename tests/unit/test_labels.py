import numpy as np
import pandas as pd
import pytest

from agnidrish.labels import Allowance, label_safety_slope, label_spec_168h

# Illustrative values only (arbitrary units).


def table(v0, v168, spec_min=np.nan, spec_max=50.0, parameter="p"):
    return pd.DataFrame(
        {"parameter": parameter, "value_0h": v0, "value_168h": v168, "spec_min": spec_min, "spec_max": spec_max}
    )


def test_spec_label_respects_each_side_and_missing_values():
    t = table([10.0, 10.0, 10.0, 10.0], [51.0, 49.0, 2.0, np.nan], spec_min=[np.nan, np.nan, 3.0, np.nan])
    assert label_spec_168h(t).tolist() == [True, False, True, pd.NA]


@pytest.mark.parametrize(
    ("allowance", "expected"),
    [(Allowance("absolute", 1.0), True), (Allowance("absolute", 2.0), False),
     (Allowance("relative", 0.1), True), (Allowance("relative", 0.2), False)],
)
def test_safety_slope_label_absolute_and_relative(allowance, expected):
    t = table([10.0], [11.5])  # change 1.5 units over 168 h
    assert label_safety_slope(t, {"p": allowance}, {"p": "up"}).tolist() == [expected]


def test_direction_controls_which_drift_counts():
    t = table([10.0, 10.0], [8.0, 12.0])
    one = {"p": Allowance("absolute", 1.0)}
    assert label_safety_slope(t, one, {"p": "up"}).tolist() == [False, True]
    assert label_safety_slope(t, one, {"p": "down"}).tolist() == [True, False]
    assert label_safety_slope(t, one, {"p": "both"}).tolist() == [True, True]


def test_spec_violation_is_a_backstop():
    t = table([49.5], [50.5])  # small drift, but outside the limit
    assert label_safety_slope(t, {"p": Allowance("absolute", 5.0)}, {"p": "up"}).tolist() == [True]


def test_missing_values_give_na_and_missing_config_is_an_error():
    t = table([np.nan], [12.0])
    assert label_safety_slope(t, {"p": Allowance("absolute", 1.0)}, {"p": "up"}).isna().all()
    with pytest.raises(ValueError, match="required"):
        label_safety_slope(t, {}, {"p": "up"})
