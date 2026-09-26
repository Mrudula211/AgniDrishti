import numpy as np
import pandas as pd
import pytest

from agnidrish.quality import FlagCode, QualityConfig, review_mask, run_quality_gate
from agnidrish.schema import Checkpoint, SchemaError

# Illustrative test values only (arbitrary units), not measurements.
# Binary-exact values so MAD comparisons at the floor are exact:
# MAD(V0) = 0.25, MAD(DRIFT) = 0.0625, MAD(V0 + DRIFT) = 0.5625.
V0 = [10.0, 10.5, 9.75, 10.25, 11.0]
DRIFT = [0.125, 0.375, 0.25, 0.5, 0.3125]
CONFIG = QualityConfig(min_lot_size=5, scale_floor={"iddq": 0.01, "tpd": 0.01})


def lot(lot_id="L1", parameter="iddq", v0=V0, drift=DRIFT, spec_min=np.nan, spec_max=50.0):
    n = len(v0)
    return pd.DataFrame(
        {
            "component_id": [f"{lot_id}-C{i}" for i in range(n)],
            "lot_id": lot_id,
            "parameter": parameter,
            "unit": "au",
            "value_0h": list(v0),
            "value_24h": [a + d for a, d in zip(v0, drift)],
            "value_96h": np.nan,
            "value_168h": np.nan,
            "spec_min": spec_min,
            "spec_max": spec_max,
            "data_category": "synthetic",
            "dataset_version": "test",
        }
    )


def gate(table, checkpoint=Checkpoint.T24, config=CONFIG):
    return run_quality_gate(table, checkpoint, config)


def codes(flags):
    return sorted(flags["code"])


def test_clean_lot_has_no_flags():
    table = lot()
    flags = gate(table)
    assert flags.empty
    assert not review_mask(table, flags).any()


def test_missing_value_flags_only_that_component():
    table = lot()
    table.loc[2, "value_24h"] = np.nan
    table = pd.concat([table, lot().assign(component_id=lambda d: d.component_id + "x")], ignore_index=True)
    flags = gate(table)
    assert codes(flags[flags.level == "component"]) == [FlagCode.MISSING_VALUE]
    assert review_mask(table, flags).tolist() == [i == 2 for i in range(len(table))]


def test_non_numeric_and_non_finite_values_flagged():
    table = lot().astype({"value_0h": object})
    table.loc[0, "value_0h"] = "N/A"
    table.loc[1, "value_24h"] = np.inf
    flags = gate(table)
    component = flags[flags.level == "component"]
    assert set(zip(component.row, component.code)) == {(0, FlagCode.NON_NUMERIC), (1, FlagCode.NON_FINITE)}


def test_future_columns_are_never_read_at_t24():
    table = lot()
    table["value_96h"] = "garbage"
    table["value_168h"] = [np.inf, np.nan, -1e9, "x", None]
    with_future = gate(table)
    without_future = gate(table.drop(columns=["value_96h", "value_168h"]))
    pd.testing.assert_frame_equal(with_future, without_future)
    assert with_future.empty


def test_duplicate_component_flags_both_rows():
    table = lot()
    table.loc[4, "component_id"] = table.loc[3, "component_id"]
    flags = gate(table)
    assert sorted(flags.loc[flags.code == FlagCode.DUPLICATE_COMPONENT, "row"]) == [3, 4]


def test_missing_identifier_flagged():
    table = lot()
    table.loc[0, "lot_id"] = None
    flags = gate(table)
    assert (flags.loc[flags.row == 0, "code"] == FlagCode.MISSING_IDENTIFIER).any()


def test_small_lot_sends_whole_lot_to_review_but_not_other_lots():
    small = lot(lot_id="S", v0=V0[:3], drift=DRIFT[:3])
    table = pd.concat([small, lot(lot_id="L1")], ignore_index=True)
    flags = gate(table)
    assert codes(flags) == [FlagCode.LOT_TOO_SMALL]
    assert review_mask(table, flags).tolist() == [True] * 3 + [False] * 5


def test_lot_size_counts_only_valid_components():
    table = lot()
    table.loc[0, "value_0h"] = np.nan
    flags = gate(table)
    assert FlagCode.LOT_TOO_SMALL in set(flags.code)
    assert review_mask(table, flags).all()


def test_zero_level_dispersion_flagged():
    table = lot(v0=[10.0, 10.0, 10.0, 10.0, 12.0])
    flags = gate(table)
    assert FlagCode.LOW_LEVEL_DISPERSION in set(flags.code)
    assert "value_0h" in flags.loc[flags.code == FlagCode.LOW_LEVEL_DISPERSION, "detail"].iloc[0]


def test_dispersion_floor_boundary_is_inclusive():
    at_floor = QualityConfig(min_lot_size=5, scale_floor={"iddq": 0.25})
    below_floor = QualityConfig(min_lot_size=5, scale_floor={"iddq": 0.2499})
    assert FlagCode.LOW_LEVEL_DISPERSION in set(gate(lot(), config=at_floor).code)
    assert FlagCode.LOW_LEVEL_DISPERSION not in set(gate(lot(), config=below_floor).code)


def test_identical_drift_flagged_even_when_levels_vary():
    table = lot(drift=[0.5] * 5)
    assert codes(gate(table)) == [FlagCode.LOW_DRIFT_DISPERSION]


def test_groups_are_per_parameter():
    table = pd.concat([lot(parameter="iddq"), lot(parameter="tpd", drift=[0.5] * 5)], ignore_index=True)
    table["component_id"] = [f"C{i}" for i in range(5)] * 2
    mask = review_mask(table, gate(table))
    assert mask.tolist() == [False] * 5 + [True] * 5


def test_spec_limits():
    no_limit = lot(spec_min=np.nan, spec_max=np.nan)
    assert set(gate(no_limit).code) == {FlagCode.NO_SPEC_LIMIT}
    lower_only = lot(spec_min=1.0, spec_max=np.nan)
    assert gate(lower_only).empty
    inverted = lot(spec_min=60.0, spec_max=50.0)
    assert set(gate(inverted).code) == {FlagCode.INVALID_SPEC_LIMITS}


def test_physical_bounds_apply_only_to_their_parameter():
    config = QualityConfig(min_lot_size=5, scale_floor={"iddq": 0.01, "tpd": 0.01}, physical_bounds={"iddq": (0.0, None)})
    negative = [-1.0, 10.5, 9.75, 10.25, 11.0]
    flags = gate(lot(v0=negative), config=config)
    assert set(flags.loc[flags.level == "component", "code"]) == {FlagCode.OUT_OF_PHYSICAL_RANGE}
    assert gate(lot(parameter="tpd", v0=negative), config=config).empty


def test_missing_scale_floor_is_an_error():
    with pytest.raises(ValueError, match="scale_floor"):
        gate(lot(parameter="leakage"))


def test_missing_required_column_is_an_error():
    with pytest.raises(SchemaError):
        gate(lot().drop(columns=["value_24h"]))


def test_invalid_config_rejected():
    with pytest.raises(ValueError):
        QualityConfig(min_lot_size=0, scale_floor={})
    with pytest.raises(ValueError):
        QualityConfig(min_lot_size=5, scale_floor={"iddq": -1.0})
