"""Screening service core shared by the CLI and the web API (P7; FR-12, FR-13, FR-14, NFR-04).

One screening run = input validation -> frozen pipeline -> decisions, lot summary,
evidence report and an audit record, written to a new run directory that is never
modified afterwards except for the append-only engineer-override log.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from agnidrish.decision import PASS, REJECT, REVIEW
from agnidrish.explain import RULE_TEXT, explain_row
from agnidrish.ingest import InputProfile, IngestReport, normalize
from agnidrish.pipeline import PipelineSpec, screen
from agnidrish.report import render_report, trajectory_svg
from agnidrish.schema import VALUE_COLUMNS, Checkpoint, SchemaError, available_value_columns
from agnidrish.site import SiteConfig

PIPELINE_FORMAT = "agnidrish-pipeline/1"
RUN_ID_PATTERN = re.compile(r"^\d{8}-\d{6}_[0-9A-Za-z]+(?:_\d+)?$")
DECISIONS = (PASS, REVIEW, REJECT)
ROW_KEY = ("lot_id", "component_id", "parameter")


@dataclass(frozen=True)
class LoadedPipeline:
    spec: PipelineSpec
    meta: dict[str, Any]
    sha256: str
    document: dict[str, Any]

    @property
    def coverage(self) -> float | None:
        """Target marginal coverage of the interval, or None if the pipeline has no interval."""
        alpha = self.meta.get("alpha")
        return None if not self.spec.halfwidths else (1.0 - alpha if alpha is not None else 0.90)


def code_version(repo_root: Path) -> str:
    """Git short SHA of the running code; AGNIDRISH_BUILD_COMMIT in containers without git; else 'unknown'."""
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo_root, capture_output=True, text=True, timeout=5)
        if sha.returncode == 0 and sha.stdout.strip():
            return sha.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return os.environ.get("AGNIDRISH_BUILD_COMMIT", "unknown")


def pipeline_document(spec: PipelineSpec, meta: dict[str, Any]) -> dict[str, Any]:
    return {"format": PIPELINE_FORMAT, "spec": spec.to_dict(), "meta": meta}


def load_pipeline(path: Path) -> LoadedPipeline:
    """Load a frozen pipeline: a ``pipeline.json`` from fit_pipeline.py, or a bare ``frozen_pipeline.json`` spec."""
    raw = path.read_bytes()
    doc = json.loads(raw)
    if doc.get("format") == PIPELINE_FORMAT:
        spec_dict, meta = doc["spec"], dict(doc.get("meta", {}))
    else:
        spec_dict, meta = doc, {"note": "bare spec from an experiment run; no fit metadata"}
    return LoadedPipeline(PipelineSpec.from_dict(spec_dict), meta, hashlib.sha256(raw).hexdigest(), doc)


def decode_text(data: bytes) -> str:
    """UTF-8 (with or without byte-order mark), else Latin-1, which many tester exports use."""
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def read_csv_bytes(data: bytes) -> pd.DataFrame:
    """Parse a delimited text export (comma, semicolon, tab or pipe; detected). Every cell is read as text.

    Text keeps identifiers such as '007' intact; the ingest layer converts measurements to numbers.
    """
    text = decode_text(data)
    try:
        sep = csv.Sniffer().sniff(text[:65536], delimiters=",;\t|").delimiter
    except csv.Error:
        sep = ","
    try:
        table = pd.read_csv(io.StringIO(text), sep=sep, dtype=str, skipinitialspace=True)
    except (pd.errors.ParserError, pd.errors.EmptyDataError) as err:
        raise SchemaError(f"input is not a readable delimited text file: {err}") from err
    if table.empty:
        raise SchemaError("input file has no data rows")
    table.columns = [str(c).strip() for c in table.columns]
    return table


def prepare_input(
    raw: pd.DataFrame,
    pipeline: LoadedPipeline,
    site: SiteConfig,
    category: str,
    *,
    profile: InputProfile | None = None,
    version: str = "unversioned",
) -> tuple[pd.DataFrame, list[str], IngestReport]:
    """Raw export -> canonical table safe to screen at the pipeline's checkpoint, warnings, ingest report.

    ``profile`` overrides the site's input profile for this upload. Later checkpoints are
    removed before screening, so an export that also contains 168 h readings cannot
    influence a 24 h decision; evaluation-only columns never enter.

    Raises:
        SchemaError: unknown category, an export the profile cannot map, or a data_category
            column that disagrees with ``category``.
    """
    if "data_category" in raw.columns:
        found = sorted(set(raw["data_category"].dropna().astype(str)))
        if found and found != [category]:
            raise SchemaError(f"category {category!r} disagrees with the file's data_category {found}")
    profile = profile or InputProfile.from_dict(site.input)
    table, report = normalize(raw, profile, site, data_category=category, dataset_version=version)
    checkpoint = Checkpoint[pipeline.spec.checkpoint]
    warnings = list(report.warnings)

    later = [c for c in VALUE_COLUMNS.values() if c not in available_value_columns(checkpoint) and c in table.columns]
    with_data = [c for c in later if table[c].notna().any()]
    if with_data:
        warnings.append(f"readings after {checkpoint.name} were ignored for this decision: {with_data}")
    table = table.drop(columns=later)

    no_model = sorted(set(table["parameter"].dropna()) - set(pipeline.spec.predictors))
    if pipeline.spec.decision.use_prediction and no_model:
        warnings.append(
            f"no validated 168 h forecasting model for {no_model} in this pipeline: screened with the quality gate, "
            "datasheet limit and lot-relative rules only (fit a site pipeline on historical lots to add a forecast)"
        )
    if report.unregistered_parameters:
        warnings.append(f"parameters not in the site registry (unit and limits taken from the file only): {report.unregistered_parameters}")
    return table, warnings, report


def screen_table(table: pd.DataFrame, pipeline: LoadedPipeline) -> pd.DataFrame:
    return table.join(screen(table, pipeline.spec))


def lot_summary(result: pd.DataFrame) -> pd.DataFrame:
    """FR-14: per (lot, parameter) size, decision counts, review rate, lot statistics and lot-level flags."""
    rows = []
    for (lot, parameter), g in result.groupby(["lot_id", "parameter"], sort=True):
        counts = g["decision"].value_counts()
        codes = sorted({c for s in g["gate_codes"].fillna("") for c in str(s).split(";") if c})
        rows.append({
            "lot_id": lot,
            "parameter": parameter,
            "unit": g["unit"].iloc[0] if "unit" in g else "",
            "n": len(g),
            **{d: int(counts.get(d, 0)) for d in DECISIONS},
            "review_rate": round(counts.get(REVIEW, 0) / len(g), 4),
            "lot_median_level": g["lot_median_level"].iloc[0],
            "lot_scale_level": g["lot_scale_level"].iloc[0],
            "lot_median_drift": g["lot_median_drift"].iloc[0],
            "lot_scale_drift": g["lot_scale_drift"].iloc[0],
            "quality_flags": ";".join(codes),
        })
    return pd.DataFrame(rows)


def _new_run_dir(root: Path, commit: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    for n in range(1, 1000):
        path = root / (f"{stamp}_{commit}" if n == 1 else f"{stamp}_{commit}_{n}")
        try:
            path.mkdir(parents=True, exist_ok=False)
            return path
        except FileExistsError:
            continue
    raise RuntimeError("could not allocate a run directory")


def record_run(
    root: Path,
    *,
    input_bytes: bytes,
    source_name: str,
    result: pd.DataFrame,
    pipeline: LoadedPipeline,
    category: str,
    warnings: list[str],
    commit: str,
    elapsed_ms: float,
    site: SiteConfig,
    profile: InputProfile,
    ingest: IngestReport,
    version: str = "unversioned",
) -> Path:
    """Write the run directory (FR-12, NFR-04): input, pipeline and site-config copies, decisions,
    lot summary, report and audit record — enough to recompute every decision offline."""
    run = _new_run_dir(root, commit)
    (run / "input.csv").write_bytes(input_bytes)
    (run / "pipeline.json").write_text(json.dumps(pipeline.document, indent=2), encoding="utf-8")
    (run / "site.json").write_text(json.dumps(site.to_dict(), indent=2, default=str), encoding="utf-8")
    result.to_csv(run / "decisions.csv", index=False)
    lot_summary(result).to_csv(run / "lot_summary.csv", index=False)
    note = f"Checkpoint {pipeline.spec.checkpoint}; pipeline sha256 {pipeline.sha256[:12]}; input {source_name}; run {run.name}."
    (run / "report.html").write_text(
        render_report(result, title="AgniDrishti — screening report", category=category,
                      coverage=pipeline.coverage, pipeline_note=note),
        encoding="utf-8",
    )
    counts = result["decision"].value_counts()
    audit = {
        "run_id": run.name,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_name": source_name,
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "pipeline_sha256": pipeline.sha256,
        "pipeline_meta": pipeline.meta,
        "checkpoint": pipeline.spec.checkpoint,
        "data_category": category,
        "site": site.name,
        "input_profile": profile.to_dict(),
        "ingest": ingest.to_dict(),
        "dataset_version": version,
        "code_version": commit,
        "rows": int(len(result)),
        "lots": int(result["lot_id"].nunique()),
        "decisions": {d: int(counts.get(d, 0)) for d in DECISIONS},
        "warnings": warnings,
        "elapsed_ms": round(elapsed_ms, 1),
    }
    (run / "audit.json").write_text(json.dumps(audit, indent=2, default=str), encoding="utf-8")
    return run


def run_dir(root: Path, run_id: str) -> Path:
    """Resolve a run id to its directory; rejects anything that is not a run id (no path traversal)."""
    if not RUN_ID_PATTERN.match(run_id) or not (root / run_id / "audit.json").is_file():
        raise FileNotFoundError(run_id)
    return root / run_id


def list_runs(root: Path, limit: int = 50) -> list[dict[str, Any]]:
    if not root.is_dir():
        return []
    runs = sorted((p for p in root.iterdir() if RUN_ID_PATTERN.match(p.name) and (p / "audit.json").is_file()), reverse=True)
    return [json.loads((p / "audit.json").read_text(encoding="utf-8")) for p in runs[:limit]]


def load_decisions(run: Path) -> pd.DataFrame:
    text_columns = ("component_id", "lot_id", "wafer_id", "device_family", "parameter", "unit", "gate_codes", "fired_rules",
                    "forecast_status", "spec_source", "ingest_flags")
    table = pd.read_csv(run / "decisions.csv", dtype={c: str for c in text_columns})
    for c in ("gate_codes", "ingest_flags"):
        if c in table.columns:
            table[c] = table[c].fillna("")
    return table


def explain(run: Path, index: int) -> dict[str, Any]:
    """Evidence card for one row of a recorded run: explanation lines, rule texts and trajectory SVG."""
    table = load_decisions(run)
    if not 0 <= index < len(table):
        raise IndexError(index)
    audit = json.loads((run / "audit.json").read_text(encoding="utf-8"))
    pipeline = load_pipeline(run / "pipeline.json")
    row = table.iloc[index]
    ex = explain_row(row, pipeline.coverage, audit["data_category"])
    return {**ex, "rule_text": {r: RULE_TEXT.get(r, r) for r in ex["rules"]}, "svg": trajectory_svg(row, show_actual=False)}


def add_override(run: Path, *, row: int, decision: str, engineer: str, reason: str) -> dict[str, Any]:
    """FR-13: append an engineer decision; the recorded pipeline decision is never changed.

    Raises:
        ValueError: unknown decision, empty engineer or reason, or row out of range.
    """
    if decision not in DECISIONS:
        raise ValueError(f"decision must be one of {DECISIONS}")
    if not engineer.strip() or not reason.strip():
        raise ValueError("engineer and reason are required")
    table = load_decisions(run)
    if not 0 <= row < len(table):
        raise ValueError(f"row {row} is not in this run")
    r = table.iloc[row]
    entry = {
        "row": row,
        **{k: str(r[k]) for k in ROW_KEY},
        "pipeline_decision": str(r["decision"]),
        "engineer_decision": decision,
        "engineer": engineer.strip(),
        "reason": reason.strip(),
        "recorded_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with (run / "overrides.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def read_overrides(run: Path) -> list[dict[str, Any]]:
    path = run / "overrides.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def replay(run: Path) -> bool:
    """NFR-04: re-screen the stored input with the stored pipeline; True if every decision is identical."""
    audit = json.loads((run / "audit.json").read_text(encoding="utf-8"))
    pipeline = load_pipeline(run / "pipeline.json")
    site = SiteConfig.from_dict(json.loads((run / "site.json").read_text(encoding="utf-8")))
    raw = read_csv_bytes((run / "input.csv").read_bytes())
    table, _, _ = prepare_input(raw, pipeline, site, audit["data_category"], profile=InputProfile.from_dict(audit["input_profile"]),
                                version=audit.get("dataset_version", "unversioned"))
    again = screen_table(table, pipeline)
    recorded = load_decisions(run)
    return again["decision"].tolist() == recorded["decision"].tolist() and again["fired_rules"].tolist() == recorded["fired_rules"].tolist()
