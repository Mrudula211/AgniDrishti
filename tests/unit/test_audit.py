from pathlib import Path

import numpy as np
import pytest

from agnidrish.audit import AuditError, check_reproducible, run_audit
from agnidrish.synthetic.config import load_config
from agnidrish.synthetic.generator import generate

CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "synthetic" / "development_v1.yaml"


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="module")
def data(config):
    return generate(config)


def violations(table, config):
    with pytest.raises(AuditError) as err:
        run_audit(table, config)
    return "\n".join(err.value.violations)


def test_generated_dataset_passes_and_reports(data, config):
    report = run_audit(data, config)
    assert report["lots"] == sum(s["n_lots"] for s in config.raw["lot_scenarios"].values())
    assert set(report["splits"]) == {"train", "validation", "calibration", "test"}
    assert all(v > 0 for v in report["spec_scenarios"].values())


def test_lot_split_across_partitions_is_leakage(data, config):
    bad = data.copy()
    lot = bad["lot_id"].iloc[0]
    rows = bad.index[bad["lot_id"] == lot]
    bad.loc[rows[:3], "split"] = "test" if bad.loc[rows[0], "split"] != "test" else "train"
    assert "split leakage" in violations(bad, config)


def test_duplicate_row_detected(data, config):
    bad = data.copy()
    bad.loc[1, ["component_id", "parameter"]] = bad.loc[0, ["component_id", "parameter"]].values
    assert "duplicates" in violations(bad, config)


def test_healthy_row_outside_spec_detected(data, config):
    bad = data.copy()
    i = bad.index[~bad["is_anomaly"] & (bad["data_fault"] == "none")][0]
    bad.loc[i, ["true_value_168h", "value_168h"]] = bad.loc[i, "spec_max"] + 1.0
    assert "healthy rows leave the spec window" in violations(bad, config)


def test_unflagged_missing_value_detected(data, config):
    bad = data.copy()
    i = bad.index[bad["data_fault"] == "none"][0]
    bad.loc[i, "value_24h"] = np.nan
    assert "missing values must occur exactly once" in violations(bad, config)


def test_measured_value_inconsistent_with_truth_detected(data, config):
    bad = data.copy()
    i = bad.index[bad["data_fault"] == "none"][0]
    bad.loc[i, "value_96h"] = bad.loc[i, "true_value_96h"] + 100 * bad.loc[i, "noise_sd"]
    assert "value_96h is inconsistent" in violations(bad, config)


def test_inverted_spec_limits_detected(data, config):
    bad = data.copy()
    tpd = bad["parameter"] == "tpd"
    bad.loc[tpd, "spec_min"] = bad.loc[tpd, "spec_max"] + 1.0
    assert "spec_min >= spec_max" in violations(bad, config)


def test_anomaly_label_disagreeing_with_family_detected(data, config):
    bad = data.copy()
    bad.loc[bad.index[0], "is_anomaly"] = not bool(bad.loc[bad.index[0], "is_anomaly"])
    assert "is_anomaly disagrees" in violations(bad, config)


def test_glitch_on_anomalous_row_detected(data, config):
    bad = data.copy()
    i = bad.index[bad["is_anomaly"] & (bad["data_fault"] == "none")][0]
    bad.loc[i, "data_fault"] = "glitch"
    assert "glitches must only be injected into healthy rows" in violations(bad, config)


def test_held_out_like_family_name_rejected(data, config):
    bad = data.copy()
    bad.loc[bad["behaviour_family"] == "shift_sudden", "behaviour_family"] = "family_19"
    assert "held-out-like family names" in violations(bad, config)


def test_reproducibility_check_detects_changed_data(data, config):
    check_reproducible(data, config)
    bad = data.copy()
    bad.loc[0, "value_0h"] += 1e-9
    with pytest.raises(AuditError, match="reproducibility"):
        check_reproducible(bad, config)
