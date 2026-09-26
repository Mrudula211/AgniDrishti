import math

import pandas as pd
import pytest

from agnidrish.schema import Checkpoint, SchemaError, available_value_columns, to_canonical

RAW = pd.DataFrame(
    {
        "Component_ID": ["C1", "C2"],
        "Lot_ID": ["L1", "L1"],
        "Param": ["iddq", "iddq"],
        "Unit": ["uA", "uA"],
        "Value_0h": [10.0, 10.25],
        "Value_24h": [10.5, 10.75],
        "Value_168h": [12.0, 11.0],
        "Spec_Max": [50.0, 50.0],
        "Operator": ["x", "y"],
    }
)
MAPPING = {
    "Component_ID": "component_id",
    "Lot_ID": "lot_id",
    "Param": "parameter",
    "Unit": "unit",
    "Value_0h": "value_0h",
    "Value_24h": "value_24h",
    "Value_168h": "value_168h",
    "Spec_Max": "spec_max",
}


def canonical(raw=RAW, mapping=MAPPING, checkpoint=Checkpoint.T24, category="synthetic"):
    return to_canonical(raw, mapping, checkpoint=checkpoint, data_category=category, dataset_version="v1")


def test_available_columns_never_include_later_checkpoints():
    assert available_value_columns(Checkpoint.T24) == ("value_0h", "value_24h")
    assert available_value_columns(Checkpoint.T96) == ("value_0h", "value_24h", "value_96h")
    assert available_value_columns(Checkpoint.T168)[-1] == "value_168h"


def test_mapping_renames_without_changing_values():
    table = canonical()
    assert table["value_0h"].tolist() == [10.0, 10.25]
    assert table["value_168h"].tolist() == [12.0, 11.0]
    assert table["component_id"].tolist() == ["C1", "C2"]


def test_unmapped_columns_dropped_and_provenance_added():
    table = canonical()
    assert "Operator" not in table.columns
    assert set(table["data_category"]) == {"synthetic"}
    assert set(table["dataset_version"]) == {"v1"}


def test_absent_spec_side_added_as_nan():
    table = canonical()
    assert all(math.isnan(v) for v in table["spec_min"])
    assert table["spec_max"].tolist() == [50.0, 50.0]


@pytest.mark.parametrize(
    "mapping",
    [
        {**MAPPING, "Operator": "operator"},  # unknown canonical target
        {**MAPPING, "Operator": "value_0h"},  # two raw columns -> one target
        {**MAPPING, "Missing": "wafer_id"},  # raw column absent
        {**MAPPING, "Operator": "data_category"},  # provenance must not come from raw
    ],
)
def test_bad_mappings_rejected(mapping):
    with pytest.raises(SchemaError):
        canonical(mapping=mapping)


def test_invalid_data_category_rejected():
    with pytest.raises(SchemaError):
        canonical(category="isro")


def test_missing_checkpoint_column_rejected():
    mapping = {k: v for k, v in MAPPING.items() if v != "value_24h"}
    with pytest.raises(SchemaError):
        canonical(mapping=mapping)


def test_later_column_required_only_at_later_checkpoint():
    mapping = {k: v for k, v in MAPPING.items() if v != "value_168h"}
    canonical(mapping=mapping, checkpoint=Checkpoint.T24)
    with pytest.raises(SchemaError):
        canonical(mapping=mapping, checkpoint=Checkpoint.T168)
