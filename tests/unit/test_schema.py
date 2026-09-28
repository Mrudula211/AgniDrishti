from agnidrish.schema import Checkpoint, available_value_columns, required_columns

# Mapping raw exports to the canonical schema is tested in test_ingest.py.


def test_available_columns_never_include_later_checkpoints():
    assert available_value_columns(Checkpoint.T24) == ("value_0h", "value_24h")
    assert available_value_columns(Checkpoint.T96) == ("value_0h", "value_24h", "value_96h")
    assert available_value_columns(Checkpoint.T168)[-1] == "value_168h"


def test_later_column_required_only_at_later_checkpoint():
    assert "value_168h" not in required_columns(Checkpoint.T24)
    assert "value_168h" in required_columns(Checkpoint.T168)
