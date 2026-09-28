import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from app.server import Settings, create_app  # noqa: E402


@pytest.fixture()
def client(tmp_path, pipeline_path):
    return TestClient(create_app(Settings(pipeline_path, tmp_path / "runs", None, 5 * 1024 * 1024)))


@pytest.fixture()
def upload(test_lots):
    return test_lots.to_csv(index=False).encode()


def screen(client, body, category="synthetic"):
    return client.post(f"/api/screen?category={category}&source=lots.csv", content=body, headers={"Content-Type": "text/csv"})


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


def test_bad_requests_are_rejected_not_passed(client, upload):
    assert screen(client, b"not,a\n1,2\n").status_code == 400  # required columns missing
    assert screen(client, upload, category="official").status_code == 400  # file says synthetic
    assert client.post("/api/screen", content=upload).status_code == 422  # category is mandatory
    assert client.get("/api/runs/..%2F..%2Fsecrets").status_code == 404
    assert client.get("/api/runs/20260101-000000_abc/files/decisions.csv").status_code == 404


def test_upload_limit(tmp_path, pipeline_path, upload):
    small = TestClient(create_app(Settings(pipeline_path, tmp_path / "runs", None, 1024)))
    assert screen(small, upload).status_code == 413
