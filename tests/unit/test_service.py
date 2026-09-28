import json

import pandas as pd
import pytest

from agnidrish import service
from agnidrish.schema import SchemaError


def record(tmp_path, pipeline, lots):
    data = lots.to_csv(index=False).encode()
    table, warnings = service.prepare_input(service.read_csv_bytes(data), pipeline, "synthetic")
    result = service.screen_table(table, pipeline)
    run = service.record_run(tmp_path, input_bytes=data, source_name="lots.csv", result=result, pipeline=pipeline,
                             category="synthetic", warnings=warnings, commit="test", elapsed_ms=1.0)
    return run, result


def test_later_checkpoints_and_ground_truth_never_reach_the_decision(pipeline, test_lots):
    table, warnings = service.prepare_input(test_lots, pipeline, "synthetic")
    assert not {"value_96h", "value_168h", "is_anomaly", "split", "true_value_24h"} & set(table.columns)
    assert any("value_168h" in w for w in warnings)
    tampered = test_lots.assign(value_168h=1e6, value_96h=1e6, is_anomaly=True)
    t2, _ = service.prepare_input(tampered, pipeline, "synthetic")
    pd.testing.assert_series_equal(service.screen_table(table, pipeline)["decision"], service.screen_table(t2, pipeline)["decision"])


def test_input_errors_are_explicit(pipeline, test_lots):
    with pytest.raises(SchemaError, match="value_24h"):
        service.prepare_input(test_lots.drop(columns=["value_24h"]), pipeline, "synthetic")
    with pytest.raises(SchemaError, match="disagrees"):
        service.prepare_input(test_lots, pipeline, "official")
    with pytest.raises(SchemaError, match="readable CSV|no rows"):
        service.read_csv_bytes(b"")


def test_uncalibrated_parameter_goes_to_review_with_a_warning(pipeline, test_lots):
    lots = test_lots.assign(parameter=test_lots["parameter"].replace({"tpd": "ileak"}))
    table, warnings = service.prepare_input(lots, pipeline, "synthetic")
    result = service.screen_table(table, pipeline)
    new = result["parameter"] == "ileak"
    assert (result.loc[new, "decision"] == "REVIEW").all()
    assert result.loc[new, "fired_rules"].str.startswith("R0").all()
    assert any("ileak" in w for w in warnings)


def test_run_record_replays_and_overrides_are_append_only(tmp_path, pipeline, test_lots):
    run, result = record(tmp_path, pipeline, test_lots)
    audit = json.loads((run / "audit.json").read_text())
    assert audit["rows"] == len(result) and audit["pipeline_sha256"] == pipeline.sha256
    assert sum(audit["decisions"].values()) == len(result)
    assert service.replay(run)
    before = (run / "decisions.csv").read_bytes()
    row = int(result.index[result["decision"] == "REJECT"][0])
    entry = service.add_override(run, row=row, decision="REVIEW", engineer="QA-1", reason="retest requested")
    assert entry["pipeline_decision"] == "REJECT" and entry["engineer_decision"] == "REVIEW"
    assert (run / "decisions.csv").read_bytes() == before
    assert len(service.read_overrides(run)) == 1
    with pytest.raises(ValueError):
        service.add_override(run, row=row, decision="MAYBE", engineer="QA-1", reason="x")
    with pytest.raises(ValueError):
        service.add_override(run, row=len(result), decision="PASS", engineer="QA-1", reason="x")
    with pytest.raises(ValueError):
        service.add_override(run, row=row, decision="PASS", engineer=" ", reason="x")


def test_explanation_and_lot_summary_match_the_decisions(tmp_path, pipeline, test_lots):
    run, result = record(tmp_path, pipeline, test_lots)
    row = int(result.index[result["decision"] != "PASS"][0])
    card = service.explain(run, row)
    assert result.loc[row, "decision"] in card["headline"] and card["svg"].startswith("<svg")
    summary = service.lot_summary(result)
    assert summary[["PASS", "REVIEW", "REJECT"]].to_numpy().sum() == len(result)


def test_run_ids_cannot_escape_the_runs_directory(tmp_path):
    for bad in ("../etc", "..", "20260101-000000_abc/../../x", "x"):
        with pytest.raises(FileNotFoundError):
            service.run_dir(tmp_path, bad)
