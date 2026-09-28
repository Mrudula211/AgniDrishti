"""AgniDrishti screening web service (P7, ADR-006): HTTP API + QA-inspector web UI.

Run from the repository root (package installed with the ``serve`` extra):
    AGNIDRISH_PIPELINE=<path>/pipeline.json uvicorn app.server:app_from_env --factory --host 0.0.0.0 --port 8000

Settings (environment variables):
    AGNIDRISH_PIPELINE        frozen pipeline JSON (required; the service refuses to start without it)
    AGNIDRISH_RUNS_DIR        where screening runs are recorded (default artifacts/screening)
    AGNIDRISH_MAPPING         optional YAML raw->canonical column mapping for the site's tester export
    AGNIDRISH_MAX_UPLOAD_MB   upload size limit (default 50)

No database: every run is an immutable directory (audit record, input and pipeline copies);
engineer overrides are an append-only JSONL file in that directory. No outbound network calls.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from agnidrish import service
from agnidrish.explain import RULE_TEXT
from agnidrish.schema import DATA_CATEGORIES, SchemaError

REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC = Path(__file__).resolve().parent / "static"
RUN_FILES = {"decisions.csv", "lot_summary.csv", "report.html", "audit.json", "overrides.jsonl"}
ROW_FIELDS = (
    "component_id", "lot_id", "parameter", "unit", "value_0h", "value_24h", "spec_min", "spec_max",
    "decision", "fired_rules", "binary_flag", "gate_codes", "z_level", "z_drift", "pred_168h", "pi_low", "pi_high",
)
log = logging.getLogger("agnidrish.server")


@dataclass(frozen=True)
class Settings:
    pipeline_path: Path
    runs_dir: Path
    mapping: dict[str, str] | None
    max_upload_bytes: int

    @staticmethod
    def from_env() -> Settings:
        pipeline = os.environ.get("AGNIDRISH_PIPELINE")
        if not pipeline:
            raise RuntimeError("AGNIDRISH_PIPELINE is not set: point it at a frozen pipeline.json (docs/architecture/deployment.md)")
        mapping_path = os.environ.get("AGNIDRISH_MAPPING")
        return Settings(
            pipeline_path=_resolve(pipeline),
            runs_dir=_resolve(os.environ.get("AGNIDRISH_RUNS_DIR", "artifacts/screening")),
            mapping=yaml.safe_load(_resolve(mapping_path).read_text(encoding="utf-8")) if mapping_path else None,
            max_upload_bytes=int(float(os.environ.get("AGNIDRISH_MAX_UPLOAD_MB", "50")) * 1024 * 1024),
        )


def _resolve(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else REPO_ROOT / p


class OverrideIn(BaseModel):
    row: int = Field(ge=0)
    decision: str
    engineer: str = Field(min_length=1, max_length=120)
    reason: str = Field(min_length=1, max_length=2000)


def _records(frame: Any) -> list[dict[str, Any]]:
    """DataFrame -> JSON-safe records (NaN -> null)."""
    return json.loads(frame.to_json(orient="records"))


def _run_payload(run: Path) -> dict[str, Any]:
    table = service.load_decisions(run)
    rows = table[[c for c in ROW_FIELDS if c in table.columns]].copy()
    rows.insert(0, "row", range(len(rows)))
    return {
        "audit": json.loads((run / "audit.json").read_text(encoding="utf-8")),
        "lots": _records(service.lot_summary(table)),
        "rows": _records(rows),
        "overrides": service.read_overrides(run),
    }


def create_app(settings: Settings) -> FastAPI:
    pipeline = service.load_pipeline(settings.pipeline_path)
    commit = service.code_version(REPO_ROOT)
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    app = FastAPI(title="AgniDrishti screening service", version="0.1.0",
                  description="Burn-in screening (SIH 2026 PS 26170): lot-relative outliers, 168 h prediction, ordered PASS/REVIEW/REJECT rules.")

    def get_run(run_id: str) -> Path:
        try:
            return service.run_dir(settings.runs_dir, run_id)
        except FileNotFoundError:
            raise HTTPException(404, f"unknown run {run_id!r}") from None

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index() -> HTMLResponse:
        return HTMLResponse((STATIC / "index.html").read_text(encoding="utf-8"))

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "checkpoint": pipeline.spec.checkpoint, "pipeline_sha256": pipeline.sha256, "code_version": commit}

    @app.get("/api/pipeline")
    def pipeline_info() -> dict[str, Any]:
        spec = pipeline.spec
        return {
            "sha256": pipeline.sha256,
            "meta": pipeline.meta,
            "spec": spec.to_dict(),
            "parameters": sorted(spec.predictors),
            "coverage": pipeline.coverage,
            "rules": RULE_TEXT,
            "mapping_configured": settings.mapping is not None,
            "categories": sorted(DATA_CATEGORIES),
        }

    @app.post("/api/screen")
    async def screen(
        request: Request,
        category: str = Query(..., description="official | external | synthetic"),
        source: str = Query("upload.csv", max_length=200, description="original file name, for the audit record"),
        version: str = Query("unversioned", max_length=100),
    ) -> dict[str, Any]:
        """Screen a CSV (request body, text/csv). Returns the recorded run."""
        body = await request.body()
        if len(body) > settings.max_upload_bytes:
            raise HTTPException(413, f"upload larger than {settings.max_upload_bytes // (1024 * 1024)} MB")
        start = time.perf_counter()
        try:
            table, warnings = service.prepare_input(service.read_csv_bytes(body), pipeline, category,
                                                    mapping=settings.mapping, version=version)
            result = service.screen_table(table, pipeline)
        except (SchemaError, ValueError) as err:
            raise HTTPException(400, str(err)) from None
        elapsed = (time.perf_counter() - start) * 1000.0
        run = service.record_run(settings.runs_dir, input_bytes=body, source_name=Path(source).name, result=result,
                                 pipeline=pipeline, category=category, warnings=warnings, commit=commit,
                                 elapsed_ms=elapsed, mapping=settings.mapping, version=version)
        log.info("run %s: %d rows, %s", run.name, len(result), result["decision"].value_counts().to_dict())
        return _run_payload(run)

    @app.get("/api/runs")
    def runs(limit: int = Query(50, ge=1, le=500)) -> list[dict[str, Any]]:
        return service.list_runs(settings.runs_dir, limit)

    @app.get("/api/runs/{run_id}")
    def run_detail(run_id: str) -> dict[str, Any]:
        return _run_payload(get_run(run_id))

    @app.get("/api/runs/{run_id}/rows/{row}")
    def row_detail(run_id: str, row: int) -> dict[str, Any]:
        run = get_run(run_id)
        try:
            card = service.explain(run, row)
        except IndexError:
            raise HTTPException(404, f"row {row} not in run") from None
        card["overrides"] = [o for o in service.read_overrides(run) if o["row"] == row]
        return card

    @app.post("/api/runs/{run_id}/overrides")
    def override(run_id: str, body: OverrideIn) -> dict[str, Any]:
        try:
            return service.add_override(get_run(run_id), row=body.row, decision=body.decision,
                                        engineer=body.engineer, reason=body.reason)
        except ValueError as err:
            raise HTTPException(400, str(err)) from None

    @app.get("/api/runs/{run_id}/replay")
    def replay(run_id: str) -> dict[str, Any]:
        """NFR-04: recompute the run from its stored input and pipeline and compare decisions."""
        return {"run_id": run_id, "identical": service.replay(get_run(run_id))}

    @app.get("/api/runs/{run_id}/files/{name}")
    def run_file(run_id: str, name: str) -> FileResponse:
        run = get_run(run_id)
        if name not in RUN_FILES or not (run / name).is_file():
            raise HTTPException(404, f"no file {name!r} in run")
        return FileResponse(run / name, filename=f"{run_id}_{name}" if name != "report.html" else None)

    return app


def app_from_env() -> FastAPI:
    """Factory for ``uvicorn --factory``: settings from the environment, fail fast if the pipeline is missing."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    return create_app(Settings.from_env())
