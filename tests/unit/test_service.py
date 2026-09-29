import json

import pandas as pd
import pytest

from agnidrish import service
from agnidrish.ingest import InputProfile
from agnidrish.schema import SchemaError


def record(tmp_path, pipeline, site, lots):
    data = lots.to_csv(index=False).encode()
    table, warnings, report = service.prepare_input(service.read_csv_bytes(data), pipeline, site, "synthetic")
    result = service.screen_table(table, pipeline)
    run = service.record_run(tmp_path, input_bytes=data, source_name="lots.csv", result=result, pipeline=pipeline,
                             category="synthetic", warnings=warnings, commit="test", elapsed_ms=1.0,
                             site=site, profile=InputProfile.from_dict(site.input), ingest=report)
    return run, result


def test_later_checkpoints_and_ground_truth_never_reach_the_decision(pipeline, site, test_lots):
    table, warnings, _ = service.prepare_input(test_lots, pipeline, site, "synthetic")
    assert not {"value_96h", "value_168h", "is_anomaly", "split", "true_value_24h"} & set(table.columns)
    assert any("value_168h" in w for w in warnings)
    tampered = test_lots.assign(value_168h=1e6, value_96h=1e6, is_anomaly=True)
    t2, _, _ = service.prepare_input(tampered, pipeline, site, "synthetic")
    pd.testing.assert_series_equal(service.screen_table(table, pipeline)["decision"], service.screen_table(t2, pipeline)["decision"])


def test_input_errors_are_explicit(pipeline, site, test_lots):
    with pytest.raises(SchemaError, match="no column"):
        service.prepare_input(test_lots.drop(columns=["lot_id"]), pipeline, site, "synthetic")
    with pytest.raises(SchemaError, match="disagrees"):
        service.prepare_input(test_lots, pipeline, site, "official")
    with pytest.raises(SchemaError, match="no data rows|readable"):
        service.read_csv_bytes(b"a,b\n")


def test_delimiters_and_byte_order_mark_are_handled():
    table = service.read_csv_bytes("﻿component_id;lot_id;value\n007;L1;1,5\n".encode("utf-8"))
    assert list(table.columns) == ["component_id", "lot_id", "value"] and table.loc[0, "component_id"] == "007"


def test_uncalibrated_parameter_is_screened_by_lot_rules_and_reported(pipeline, site, test_lots):
    lots = test_lots.assign(parameter=test_lots["parameter"].replace({"tpd": "ileak"}))
    table, warnings, _ = service.prepare_input(lots, pipeline, site, "synthetic")
    result = service.screen_table(table, pipeline)
    new = result["parameter"] == "ileak"
    assert result.loc[new, "forecast_status"].str.startswith("no validated model").all()
    assert (result.loc[new, "decision"] == "PASS").mean() > 0.5  # not a blanket REVIEW
    assert any("forecasting model" in w and "ileak" in w for w in warnings)


def test_run_record_replays_and_overrides_are_append_only(tmp_path, pipeline, site, test_lots):
    run, result = record(tmp_path, pipeline, site, test_lots)
    audit = json.loads((run / "audit.json").read_text())
    assert audit["rows"] == len(result) and audit["pipeline_sha256"] == pipeline.sha256 and audit["site"] == site.name
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


def test_explanation_and_lot_summary_match_the_decisions(tmp_path, pipeline, site, test_lots):
    run, result = record(tmp_path, pipeline, site, test_lots)
    row = int(result.index[result["decision"] != "PASS"][0])
    card = service.explain(run, row)
    assert result.loc[row, "decision"] in card["headline"] and card["svg"].startswith("<svg")
    assert any(line.startswith("Limit source") for line in card["lines"])
    summary = service.lot_summary(result)
    assert summary[["PASS", "REVIEW", "REJECT"]].to_numpy().sum() == len(result)


def test_run_ids_cannot_escape_the_runs_directory(tmp_path):
    for bad in ("../etc", "..", "20260101-000000_abc/../../x", "x"):
        with pytest.raises(FileNotFoundError):
            service.run_dir(tmp_path, bad)
