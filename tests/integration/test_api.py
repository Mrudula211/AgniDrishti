import json

import pandas as pd
import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from app.server import Settings, create_app  # noqa: E402


@pytest.fixture()
def client(tmp_path, pipeline_path, site_path):
    return TestClient(create_app(Settings(pipeline_path, site_path, tmp_path / "runs", 5 * 1024 * 1024)))


@pytest.fixture()
def upload(test_lots):
    return test_lots.to_csv(index=False).encode()


def screen(client, body, category="synthetic", profile=None):
    params = {"category": category, "source": "lots.csv"}
    if profile is not None:
        params["profile"] = json.dumps(profile)
    return client.post("/api/screen", params=params, content=body, headers={"Content-Type": "text/csv"})


def test_screen_explain_override_replay(client, upload, test_lots):
    assert client.get("/api/health").json()["status"] == "ok"
    assert "AgniDrishti" in client.get("/").text
    r = screen(client, upload)
    assert r.status_code == 200, r.text
    run = r.json()
    run_id = run["audit"]["run_id"]
    assert len(run["rows"]) == len(test_lots) and sum(run["audit"]["decisions"].values()) == len(test_lots)
    flagged = next(x["row"] for x in run["rows"] if x["decision"] == "REJECT")
    card = client.get(f"/api/runs/{run_id}/rows/{flagged}").json()
    assert card["svg"].startswith("<svg") and any("Rules fired" in line for line in card["lines"])
    o = client.post(f"/api/runs/{run_id}/overrides", json={"row": flagged, "decision": "REVIEW", "engineer": "QA-1", "reason": "retest"})
    assert o.status_code == 200 and o.json()["pipeline_decision"] == "REJECT"
    assert len(client.get(f"/api/runs/{run_id}").json()["overrides"]) == 1
    assert client.get(f"/api/runs/{run_id}/replay").json()["identical"] is True
    assert client.get(f"/api/runs/{run_id}/files/decisions.csv").status_code == 200
    assert [x["run_id"] for x in client.get("/api/runs").json()] == [run_id]


def test_foreign_export_is_inspected_mapped_and_screened(client, test_lots):
    # The same held-out lots, exported by a different tester: one row per reading, other column names, hours as text.
    rows = []
    for _, r in test_lots.iterrows():
        for hour, col in (("0 h", "value_0h"), ("24 h", "value_24h")):
            rows.append({"Serial": r["component_id"], "Batch": r["lot_id"], "Test": r["parameter"].upper(),
                         "Units": r["unit"], "Read Point": hour, "Reading": r[col], "USL": r["spec_max"], "LSL": r["spec_min"]})
    body = pd.DataFrame(rows).to_csv(index=False, sep=";").encode()
    suggestion = client.post("/api/inspect", content=body).json()
    assert suggestion["profile"]["layout"] == "row_per_measurement" and not suggestion["missing_roles"]
    foreign = screen(client, body, profile=suggestion["profile"])
    # nominal_value is not in the foreign export, so leave it out of the native one too (it sets the degenerate-lot floor).
    native = screen(client, test_lots.drop(columns=["nominal_value"]).to_csv(index=False).encode())
    assert foreign.status_code == 200, foreign.text
    key = lambda x: (x["lot_id"], x["component_id"], x["parameter"])  # noqa: E731
    a = {key(x): (x["decision"], x["fired_rules"]) for x in foreign.json()["rows"]}
    b = {key(x): (x["decision"], x["fired_rules"]) for x in native.json()["rows"]}
    assert a == b  # same readings, same decisions, whatever the export format


def test_bad_requests_are_rejected_not_passed(client, upload):
    assert screen(client, b"not,a\n1,2\n").status_code == 400  # required columns missing
    assert screen(client, upload, category="official").status_code == 400  # file says synthetic
    assert client.post("/api/screen", content=upload).status_code == 422  # category is mandatory
    assert screen(client, upload, profile={"layout": "nonsense"}).status_code == 400
    assert client.get("/api/runs/..%2F..%2Fsecrets").status_code == 404
    assert client.get("/api/runs/20260101-000000_abc/files/decisions.csv").status_code == 404


def test_upload_limit(tmp_path, pipeline_path, site_path, upload):
    small = TestClient(create_app(Settings(pipeline_path, site_path, tmp_path / "runs", 1024)))
    assert screen(small, upload).status_code == 413
