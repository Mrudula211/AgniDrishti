"""AgniDrishti screening web service (P7, ADR-006, ADR-007): HTTP API + QA-inspector web UI.

Run from the repository root (package installed with the ``serve`` extra):
    python scripts/serve.py --site configs/sites/<site>.yaml --pipeline <path>/pipeline.json

Settings (environment variables; scripts/serve.py sets them from its arguments):
    AGNIDRISH_PIPELINE        frozen pipeline JSON (required; the service refuses to start without it)
    AGNIDRISH_SITE            site config YAML: input layout, parameter registry, limit sources (required)
    AGNIDRISH_RUNS_DIR        where screening runs are recorded (default artifacts/screening)
    AGNIDRISH_MAX_UPLOAD_MB   upload size limit (default 50)

No database: every run is an immutable directory (audit record, input, pipeline and site-config
copies); engineer overrides are an append-only JSONL file in that directory. No outbound network calls.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from agnidrish import service
from agnidrish.explain import LIMIT_SOURCE_TEXT, RULE_TEXT
from agnidrish.ingest import LAYOUTS, REQUIRED_ROLES, ROLES, InputProfile, normalize, suggest_profile
from agnidrish.schema import DATA_CATEGORIES, SchemaError
from agnidrish.site import SiteConfig, SiteConfigError, load_site

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC = Path(__file__).resolve().parent / "static"
RUN_FILES = {"decisions.csv", "lot_summary.csv", "report.html", "audit.json", "overrides.jsonl", "site.json"}
ROW_FIELDS = (
    "component_id", "lot_id", "parameter", "unit", "value_0h", "value_24h", "spec_min", "spec_max", "spec_source",
    "decision", "fired_rules", "binary_flag", "gate_codes", "z_level", "z_drift", "forecast_status", "pred_168h", "pi_low", "pi_high",
)
MAX_PROFILE_CHARS = 20000
log = logging.getLogger("agnidrish.server")


@dataclass(frozen=True)
class Settings:
    pipeline_path: Path
    site_path: Path
    runs_dir: Path
    max_upload_bytes: int

    @staticmethod
    def from_env() -> Settings:
        missing = [v for v in ("AGNIDRISH_PIPELINE", "AGNIDRISH_SITE") if not os.environ.get(v)]
        if missing:
            raise RuntimeError(f"{missing} not set: use scripts/serve.py --site … --pipeline … (docs/architecture/deployment.md)")
        return Settings(
            pipeline_path=_resolve(os.environ["AGNIDRISH_PIPELINE"]),
            site_path=_resolve(os.environ["AGNIDRISH_SITE"]),
            runs_dir=_resolve(os.environ.get("AGNIDRISH_RUNS_DIR", "artifacts/screening")),
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


def _profile(text: str | None, site: SiteConfig) -> InputProfile:
    """Per-upload profile (JSON in the query string) or the site default."""
    if not text:
        return InputProfile.from_dict(site.input)
    if len(text) > MAX_PROFILE_CHARS:
        raise HTTPException(413, "input profile too large")
    try:
        return InputProfile.from_dict(json.loads(text))
    except (json.JSONDecodeError, TypeError, ValueError) as err:
        raise HTTPException(400, f"invalid input profile: {err}") from None


def create_app(settings: Settings) -> FastAPI:
    pipeline = service.load_pipeline(settings.pipeline_path)
    site = load_site(settings.site_path, REPO_ROOT)
    InputProfile.from_dict(site.input)  # fail at start-up, not at the first upload
    commit = service.code_version(REPO_ROOT)
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    app = FastAPI(title="AgniDrishti screening service", version="0.2.0",
                  description="Burn-in screening (SIH 2026 PS 26170): lot-relative outliers, 168 h forecast, ordered PASS/REVIEW/REJECT rules.")

    def get_run(run_id: str) -> Path:
        try:
            return service.run_dir(settings.runs_dir, run_id)
        except FileNotFoundError:
            raise HTTPException(404, f"unknown run {run_id!r}") from None

    async def read_body(request: Request) -> bytes:
        body = await request.body()
        if len(body) > settings.max_upload_bytes:
            raise HTTPException(413, f"upload larger than {settings.max_upload_bytes // (1024 * 1024)} MB")
        return body

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index() -> HTMLResponse:
        return HTMLResponse((STATIC / "index.html").read_text(encoding="utf-8"))

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "site": site.name, "checkpoint": pipeline.spec.checkpoint,
                "pipeline_sha256": pipeline.sha256, "code_version": commit}

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
            "categories": sorted(DATA_CATEGORIES),
        }

    @app.get("/api/site")
    def site_info() -> dict[str, Any]:
        return {**site.to_dict(), "layouts": LAYOUTS, "roles": ROLES, "required_roles": REQUIRED_ROLES,
                "limit_source_text": LIMIT_SOURCE_TEXT, "forecast_parameters": sorted(pipeline.spec.predictors)}

    @app.post("/api/inspect")
    async def inspect(request: Request) -> dict[str, Any]:
        """Look at an unseen export (body = file) and suggest an input profile for an engineer to confirm."""
        try:
            raw = service.read_csv_bytes(await read_body(request))
        except SchemaError as err:
            raise HTTPException(400, str(err)) from None
        suggestion = suggest_profile(raw)
        suggestion["preview"] = json.loads(raw.head(8).to_json(orient="records"))
        suggestion["rows"] = len(raw)
        try:  # does the site's configured profile already fit this file?
            normalize(raw.head(500), InputProfile.from_dict(site.input), site, data_category="synthetic", dataset_version="inspect")
            suggestion["site_profile_error"] = None
        except (SchemaError, ValueError) as err:
            suggestion["site_profile_error"] = str(err)
        suggestion["site_profile"] = InputProfile.from_dict(site.input).to_dict()
        return suggestion

    @app.post("/api/screen")
    async def screen(
        request: Request,
        category: str = Query(..., description="official | external | synthetic"),
        source: str = Query("upload.csv", max_length=200, description="original file name, for the audit record"),
        version: str = Query("unversioned", max_length=100),
        profile: str | None = Query(None, description="JSON input profile; omit to use the site's"),
    ) -> dict[str, Any]:
        """Screen an export (request body). Returns the recorded run."""
        body = await read_body(request)
        chosen = _profile(profile, site)
        start = time.perf_counter()
        try:
            table, warnings, report = service.prepare_input(service.read_csv_bytes(body), pipeline, site, category,
                                                            profile=chosen, version=version)
            result = service.screen_table(table, pipeline)
        except (SchemaError, SiteConfigError, ValueError) as err:
            raise HTTPException(400, str(err)) from None
        elapsed = (time.perf_counter() - start) * 1000.0
        run = service.record_run(settings.runs_dir, input_bytes=body, source_name=Path(source).name, result=result,
                                 pipeline=pipeline, category=category, warnings=warnings, commit=commit, elapsed_ms=elapsed,
                                 site=site, profile=chosen, ingest=report, version=version)
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
        """NFR-04: recompute the run from its stored input, pipeline and site config and compare decisions."""
        return {"run_id": run_id, "identical": service.replay(get_run(run_id))}

    @app.get("/api/runs/{run_id}/files/{name}")
    def run_file(run_id: str, name: str) -> FileResponse:
        run = get_run(run_id)
        if name not in RUN_FILES or not (run / name).is_file():
            raise HTTPException(404, f"no file {name!r} in run")
        return FileResponse(run / name, filename=f"{run_id}_{name}" if name != "report.html" else None)

    return app


def app_from_env() -> FastAPI:
    """Factory for ``uvicorn --factory``: settings from the environment, fail fast on a missing pipeline or site config."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    return create_app(Settings.from_env())
