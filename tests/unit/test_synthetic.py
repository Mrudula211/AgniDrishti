from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from agnidrish.schema import CANONICAL_ORDER, EVALUATION_ONLY_COLUMNS, Checkpoint, model_input_columns
from agnidrish.synthetic.config import SPLITS, ConfigError, from_dict, load_config
from agnidrish.synthetic.families import ANOMALOUS_FAMILIES, FAMILY_KINDS, Kind, Shape
from agnidrish.synthetic.generator import assign_splits, generate

CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "synthetic" / "development_v1.yaml"


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def data(config):
    return generate(config)


@pytest.mark.parametrize(
    "shape",
    [Shape("linear"), Shape("power", 1.5), Shape("power", 0.5), Shape("exp", 12.0), Shape("late", 60.0),
     Shape("sigmoid", 80.0, 15.0), Shape("step", 120.0)],
)
def test_shapes_are_normalised(shape):
    values = shape(np.array([0.0, 168.0]), 168.0)
    assert values[0] == pytest.approx(0.0)
    assert values[1] == pytest.approx(1.0)


def test_late_and_step_shapes_are_invisible_before_onset():
    t = np.array([0.0, 24.0, 96.0])
    assert Shape("late", 100.0)(t, 168.0).tolist() == [0.0, 0.0, 0.0]
    assert Shape("step", 100.0)(t, 168.0).tolist() == [0.0, 0.0, 0.0]


def test_no_held_out_family_is_defined():
    for name in FAMILY_KINDS:
        assert not any(marker in name for marker in ("19", "20", "heldout", "hidden"))


def test_same_seed_reproduces_and_different_seed_differs(config, data):
    pd.testing.assert_frame_equal(generate(config), data)
    other = generate(config.with_seed(config.seed + 1))
    assert not other[["value_0h", "value_168h"]].equals(data[["value_0h", "value_168h"]])


def test_every_non_schema_column_is_classified(data):
    extra = set(data.columns) - set(CANONICAL_ORDER)
    unclassified = extra - EVALUATION_ONLY_COLUMNS - {"nominal_value"}
    assert unclassified == set()


def test_model_inputs_at_t24_exclude_labels_and_future_values(data):
    inputs = set(model_input_columns(data.columns, Checkpoint.T24))
    for forbidden in ("value_96h", "value_168h", "true_value_0h", "is_anomaly", "severity",
                      "behaviour_family", "split", "lot_scenario", "data_fault"):
        assert forbidden not in inputs
    assert {"value_0h", "value_24h", "spec_max", "lot_id"} <= inputs


def test_splits_are_whole_lots_stratified_by_scenario():
    lots = pd.Series(["a"] * 10 + ["b"] * 3, index=[f"L{i:02d}" for i in range(13)])
    fractions = {"train": 0.5, "validation": 0.2, "calibration": 0.15, "test": 0.15}
    first = assign_splits(lots, fractions, np.random.default_rng(1))
    assert first == assign_splits(lots, fractions, np.random.default_rng(1))
    assert set(first) == set(lots.index) and set(first.values()) <= set(SPLITS)
    in_a = [first[lot] for lot in lots.index[lots == "a"]]
    assert {s: in_a.count(s) for s in SPLITS} == {"train": 5, "validation": 2, "calibration": 1, "test": 2}


def test_small_scenarios_still_reach_the_test_split():
    lots = pd.Series(["rare"] * 4, index=["L1", "L2", "L3", "L4"])
    fractions = {"train": 0.5, "validation": 0.2, "calibration": 0.15, "test": 0.15}
    assert "test" in assign_splits(lots, fractions, np.random.default_rng(0)).values()


def test_drift_severity_is_amplitude_over_reference_variation(config, data):
    ref = {p.name: p.drift_reference_sd for p in config.parameters}
    drift = data[data["behaviour_family"].map(FAMILY_KINDS) == Kind.DRIFT]
    expected = drift["anomaly_amplitude"].abs() / drift["parameter"].map(ref)
    np.testing.assert_allclose(drift["severity"], expected)


def test_level_outlier_offset_matches_severity(config, data):
    comp_sd = {p.name: p.comp_sd for p in config.parameters}
    rows = data[data["behaviour_family"] == "level_outlier"]
    np.testing.assert_allclose(rows["level_offset"].abs(), rows["severity"] * rows["parameter"].map(comp_sd))


def test_spec_families_do_what_their_names_say(data):
    crossing = data[data["behaviour_family"] == "crossing_spec"]
    assert (crossing["true_value_168h"] > crossing["spec_max"]).all()
    assert (crossing["true_value_0h"] <= crossing["spec_max"]).all()
    approaching = data[data["behaviour_family"] == "approaching_spec"]
    assert (approaching["true_value_168h"] <= approaching["spec_max"]).all()
    at_0h = data[data["behaviour_family"] == "spec_violation_at_0h"]
    assert (at_0h["true_value_0h"] > at_0h["spec_max"]).all()


def test_anomaly_status_follows_family_not_value(data):
    assert (data["is_anomaly"] == data["behaviour_family"].isin(ANOMALOUS_FAMILIES)).all()
    anomalous_in_spec = data["is_anomaly"] & (data["true_value_168h"] <= data["spec_max"])
    assert anomalous_in_spec.any()


def test_invalid_configs_rejected(config):
    bad_split = {**config.raw, "splits": {"fractions": {"train": 0.9, "test": 0.1}}}
    with pytest.raises(ConfigError, match="split"):
        from_dict(bad_split)
    bad_family = {**config.raw, "anomalous_family_weights": {"family_19": 1.0}}
    with pytest.raises(ConfigError, match="anomalous_family_weights"):
        from_dict(bad_family)
    no_limit = {**config.raw, "parameters": {"iddq": {**config.raw["parameters"]["iddq"], "spec_max": None}}}
    with pytest.raises(ConfigError, match="spec limit"):
        from_dict(no_limit)
