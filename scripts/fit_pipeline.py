"""Fit a deployable pipeline on a site's historical burn-in lots (FR-20, ADR-006, ADR-007).

    python scripts/fit_pipeline.py --input history.csv --category official --site configs/sites/<site>.yaml
    python scripts/fit_pipeline.py --input export.csv --profile history_profile.yaml --site ... --category official

The export is read through the site's input profile (any supported layout); historical rows
need 0 h, 24 h and 168 h readings. Parameters with a degradation direction in the site registry
get a 168 h forecast; the rest are reported as screened without one. The fit re-runs the
pre-registered E1-E6 development procedure (agnidrish.fit). Output (never overwritten):
artifacts/models/pipeline/<YYYYMMDD-HHMMSS>_<sha>/{pipeline.json, fit_metrics.json, fit_summary.md}.
Deploy with scripts/serve.py --pipeline <that pipeline.json>.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from agnidrish.experiments import to_jsonable
from agnidrish.fit import fit_config, fit_pipeline
from agnidrish.ingest import InputProfile, normalize
from agnidrish.service import code_version, pipeline_document, read_csv_bytes
from agnidrish.site import load_site

REPO_ROOT = Path(__file__).resolve().parents[1]
log = logging.getLogger("fit_pipeline")


def fmt(x: Any, digits: int = 3) -> str:
    return "—" if x is None or (isinstance(x, float) and x != x) else (f"{x:.{digits}g}" if isinstance(x, float) else str(x))


def _stage_line(stage: dict[str, Any]) -> str:
    det, ops = stage["primary_label"], stage["operational"]
    return (f"Positives {det['n_positive']} · recall {fmt(det['recall'])} · precision {fmt(det['precision'])} · FPR {fmt(det['fpr'])} · "
            f"escape rate {fmt(ops['defect_escape_rate'])} · review rate {fmt(ops['review_rate'])} · "
            f"false rejection {fmt(ops['false_rejection_rate'])} · auto-cleared {fmt(ops['auto_cleared'])}")


def summary(res: dict[str, Any], meta: dict[str, Any]) -> str:
    e6 = res["stages"]["E6"]
    lines = [
        "# Site pipeline fit",
        "",
        f"Data category: **{meta['data_category'].upper()}** · input `{meta['input']}` (sha256 `{meta['input_sha256'][:16]}…`) · "
        f"code `{meta['code_version']}` · methods `{meta['methods_from']}`",
        "",
        f"Lots per split: {res['split_lots']} · rows: {res['split_rows']}",
        "",
        "## Module B predictors (validation lots, per parameter; units differ so MAE is never pooled)",
        "",
        "| Predictor | Parameter | MAE | RMSE | Tail MAE | Chosen |",
        "|---|---|---|---|---|---|",
    ]
    for m, v in res["predictor_comparison"].items():
        for p, r in v["per_parameter"].items():
            chosen = "yes" if res["chosen_predictors"].get(p) == m else ""
            lines.append(f"| {m} | {p} | {fmt(r['mae'], 4)} | {fmt(r['rmse'], 4)} | {fmt(r['tail_mae'], 4)} | {chosen} |")
    cov = res["coverage_validation"]
    op = res["operating_point"]
    lines += [
        "",
        f"Conformal half-widths (parameter units): {res['halfwidths']}",
        f"Interval coverage on validation lots (target {1 - meta['alpha']:.2f}): overall {fmt(cov['overall']['coverage'])}; "
        f"per-lot min {fmt(min(cov['per_lot_coverage'].values()))}, max {fmt(max(cov['per_lot_coverage'].values()))}",
        f"Operating point (ADR-005): z_review = {op['z_review']}; target recall {meta['target_recall']} reached: **{op['reached_target']}**",
        "",
        "## Full pipeline on validation lots (proxy label; REVIEW counted as flagged)",
        "",
        _stage_line(e6),
        "",
        "## Same rules without the 168 h forecast (how a parameter without a forecast model is decided)",
        "",
        _stage_line(res["no_forecast_validation"]),
        f"Parameters screened without a forecast (no direction in the registry): {res['not_forecast'] or 'none'}",
        "",
        "These are development numbers (the threshold was chosen on these lots). Before relying on the pipeline,",
        "evaluate it once on lots that were not used here (docs/architecture/deployment.md §4).",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True, help="historical export with 0 h, 24 h and 168 h readings")
    ap.add_argument("--category", required=True, choices=["official", "external", "synthetic"])
    ap.add_argument("--site", required=True, help="site config, e.g. configs/sites/synthetic_demo.yaml")
    ap.add_argument("--profile", help="YAML/JSON input profile overriding the site's `input` section for this file")
    ap.add_argument("--version", default="unversioned", help="dataset version label")
    args = ap.parse_args()

    site_path = REPO_ROOT / args.site
    site = load_site(site_path, REPO_ROOT)
    cfg = fit_config(site, REPO_ROOT)
    input_path = Path(args.input) if Path(args.input).is_absolute() else REPO_ROOT / args.input
    data = input_path.read_bytes()
    raw = read_csv_bytes(data)
    if "data_category" in raw.columns and set(raw["data_category"].dropna()) != {args.category}:
        raise SystemExit(f"--category {args.category} disagrees with the file's data_category {sorted(set(raw['data_category'].dropna()))}")
    profile = InputProfile.from_dict(yaml.safe_load((REPO_ROOT / args.profile).read_text(encoding="utf-8")) if args.profile else site.input)
    # A `split` column (pre-assigned whole-lot splits) is honoured; otherwise lots are split by the site seed.
    table, report = normalize(raw, profile, site, data_category=args.category, dataset_version=args.version, keep=("split",))
    for w in report.warnings:
        log.warning(w)

    res = fit_pipeline(table, cfg)
    commit = code_version(REPO_ROOT)
    meta = {
        "fitted_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_category": args.category,
        "input": input_path.name,
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "site": site.name,
        "site_config": site_path.relative_to(REPO_ROOT).as_posix(),
        "not_forecast": res["not_forecast"],
        "methods_from": cfg["methods_from"],
        "code_version": commit,
        "alpha": cfg["uncertainty"]["alpha"],
        "target_recall": cfg["operating_point"]["target_recall"],
        "split_lots": res["split_lots"],
        "chosen_predictors": res["chosen_predictors"],
        "operating_point_reached": res["operating_point"]["reached_target"],
        "validation_recall": res["stages"]["E6"]["primary_label"]["recall"],
        "validation_review_rate": res["stages"]["E6"]["operational"]["review_rate"],
    }
    out = REPO_ROOT / "artifacts" / "models" / "pipeline" / f"{datetime.now(timezone.utc):%Y%m%d-%H%M%S}_{commit}"
    out.mkdir(parents=True, exist_ok=False)
    (out / "pipeline.json").write_text(json.dumps(to_jsonable(pipeline_document(res["specs"]["E6"], meta)), indent=2), encoding="utf-8")
    metrics = {k: v for k, v in res.items() if k != "specs"} | {"meta": meta}
    (out / "fit_metrics.json").write_text(json.dumps(to_jsonable(metrics), indent=2), encoding="utf-8")
    (out / "fit_summary.md").write_text(summary(res, meta), encoding="utf-8")
    log.info("wrote %s", (out / "pipeline.json").relative_to(REPO_ROOT))
    sys.stdout.reconfigure(encoding="utf-8")  # the summaries contain →, Δ, ×; legacy Windows consoles default to cp1252
    print((out / "fit_summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
