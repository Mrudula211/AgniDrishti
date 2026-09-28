"""Screening service core shared by the CLI and the web API (P7; FR-12, FR-13, FR-14, NFR-04).

One screening run = input validation -> frozen pipeline -> decisions, lot summary,
evidence report and an audit record, written to a new run directory that is never
modified afterwards except for the append-only engineer-override log.
"""

from __future__ import annotations

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
from agnidrish.pipeline import PipelineSpec, screen
from agnidrish.report import render_report, trajectory_svg
from agnidrish.schema import (
    DATA_CATEGORIES,
    EVALUATION_ONLY_COLUMNS,
    VALUE_COLUMNS,
    Checkpoint,
    SchemaError,
    available_value_columns,
    required_columns,
    to_canonical,
)

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


def read_csv_bytes(data: bytes) -> pd.DataFrame:
    """Parse an uploaded CSV. Identifiers stay strings so '007' is not turned into 7."""
    try:
        table = pd.read_csv(io.BytesIO(data), dtype={c: str for c in ("component_id", "lot_id", "wafer_id", "parameter", "unit")})
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as err:
        raise SchemaError(f"input is not a readable CSV: {err}") from err
    if table.empty:
        raise SchemaError("input CSV has no rows")
    return table


def prepare_input(
    raw: pd.DataFrame,
    pipeline: LoadedPipeline,
    category: str,
    *,
    mapping: dict[str, str] | None = None,
    version: str = "unversioned",
) -> tuple[pd.DataFrame, list[str]]:
    """Canonical table safe to screen at the pipeline's checkpoint, plus human-readable warnings.

    Later checkpoints and evaluation-only columns are removed before screening,
    so an upload that happens to contain value_168h cannot influence a 24 h decision.

    Raises:
        SchemaError: unknown category, unmappable input, missing required column,
            or a data_category column that disagrees with ``category``.
    """
    if category not in DATA_CATEGORIES:
        raise SchemaError(f"category must be one of {sorted(DATA_CATEGORIES)}, got {category!r}")
    checkpoint = Checkpoint[pipeline.spec.checkpoint]
    warnings: list[str] = []
    if mapping:
        table = to_canonical(raw, mapping, checkpoint=checkpoint, data_category=category, dataset_version=version)
    else:
        table = raw.copy()
        if "data_category" in table.columns:
            found = sorted(set(table["data_category"].dropna().astype(str)))
            if found != [category]:
                raise SchemaError(f"category {category!r} disagrees with the file's data_category {found}")
        else:
            table["data_category"] = category
        if "dataset_version" not in table.columns:
            table["dataset_version"] = version
        missing = [c for c in required_columns(checkpoint) if c not in table.columns]
        if missing:
            found = [str(c) for c in raw.columns[:8]]
            raise SchemaError(
                f"columns required at {checkpoint.name} are missing: {missing}. The file's first columns are {found}. "
                "Expected a burn-in lot table: one row per component per parameter with its lot and the 0 h and 24 h "
                "measurements (a header row is required), or a server-side column mapping for the tester's own format."
            )

    later = [c for c in VALUE_COLUMNS.values() if c not in available_value_columns(checkpoint) and c in table.columns]
    hidden = sorted(c for c in table.columns if c in EVALUATION_ONLY_COLUMNS)
    if later or hidden:
        warnings.append(f"ignored columns not available at {checkpoint.name} or evaluation-only: {later + hidden}")
    table = table.drop(columns=later + hidden).reset_index(drop=True)

    unknown = sorted(set(table["parameter"].dropna()) - set(pipeline.spec.predictors))
    if pipeline.spec.predictors and unknown:
        warnings.append(
            f"parameters {unknown} are not calibrated in this pipeline — their rows go to REVIEW (R0, missing evidence); "
            "fit a site pipeline that includes them (scripts/fit_pipeline.py)"
        )
    return table, warnings


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
    mapping: dict[str, str] | None = None,
    version: str = "unversioned",
) -> Path:
    """Write the run directory (FR-12, NFR-04): input copy, pipeline copy, decisions, lot summary, report, audit."""
    run = _new_run_dir(root, commit)
    (run / "input.csv").write_bytes(input_bytes)
    (run / "pipeline.json").write_text(json.dumps(pipeline.document, indent=2), encoding="utf-8")
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
        "mapping": mapping,
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
    table = pd.read_csv(run / "decisions.csv", dtype={c: str for c in ("component_id", "lot_id", "wafer_id", "parameter", "unit", "gate_codes", "fired_rules")})
    table["gate_codes"] = table["gate_codes"].fillna("")
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
    raw = read_csv_bytes((run / "input.csv").read_bytes())
    table, _ = prepare_input(raw, pipeline, audit["data_category"], mapping=audit.get("mapping"),
                             version=audit.get("dataset_version", "unversioned"))
    again = screen_table(table, pipeline)
    recorded = load_decisions(run)
    return again["decision"].tolist() == recorded["decision"].tolist() and again["fired_rules"].tolist() == recorded["fired_rules"].tolist()
