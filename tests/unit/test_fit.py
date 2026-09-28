import numpy as np
import pandas as pd
import pytest

from agnidrish.decision import DecisionConfig
from agnidrish.fit import assign_lot_splits, fit_pipeline, prepare_history
from agnidrish.pipeline import PipelineSpec
from agnidrish.schema import SchemaError


def test_lot_splits_are_whole_lots_deterministic_and_never_empty():
    lots = pd.Series([f"L{i % 7}" for i in range(70)])
    fractions = {"train": 0.6, "calibration": 0.2, "validation": 0.2}
    a = assign_lot_splits(lots, fractions, seed=1)
    assert a.groupby(lots).nunique().max() == 1  # a lot never spans two splits
    assert set(a) == {"train", "calibration", "validation"}
    pd.testing.assert_series_equal(a, assign_lot_splits(lots, fractions, seed=1))
    three = assign_lot_splits(pd.Series(["A", "B", "C"]), fractions, seed=1)
    assert sorted(three) == ["calibration", "train", "validation"]
    with pytest.raises(ValueError, match="at least 3 lots"):
        assign_lot_splits(pd.Series(["A", "B"]), fractions, seed=1)


def test_fit_never_reads_the_test_split(synthetic_data, fit_config, fitted):
    tampered = synthetic_data.copy()
    test = tampered["split"] == "test"
    tampered.loc[test, ["value_24h", "value_168h"]] *= 50.0
    again = fit_pipeline(tampered, fit_config)
    assert again["specs"]["E6"].to_dict() == fitted["specs"]["E6"].to_dict()
    assert "test" not in again["split_lots"]


def test_fit_requires_168h_and_a_direction_for_every_parameter(synthetic_data, fit_config):
    with pytest.raises(SchemaError, match="value_168h"):
        prepare_history(synthetic_data.drop(columns=["value_168h"]), fit_config)
    extra = synthetic_data.assign(parameter=np.where(synthetic_data["parameter"] == "tpd", "vth", synthetic_data["parameter"]))
    with pytest.raises(SchemaError, match="vth"):
        prepare_history(extra, fit_config)


def test_pipeline_rejects_unsigned_direction():
    with pytest.raises(ValueError, match="'up' or 'down'"):
        PipelineSpec("T24", 20, 0.001, "iqr", "relative", 0.15, {"p": "both"}, DecisionConfig())
