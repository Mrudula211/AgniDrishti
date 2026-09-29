"""Run experiments E1-E6 (cumulative ablation) and record them in a new run directory.

Development (validation lots; fits on train / calibration):
    python scripts/run_experiments.py
Final, once, on the frozen test lots with a development run's frozen specs:
    python scripts/run_experiments.py --final artifacts/metrics/E1-E6_validation/<run>

Run directories: artifacts/metrics/<E1-E6_validation|E1-E6_test>/<YYYYMMDD-HHMMSS>_<sha>/
(never overwritten). Requires the package installed or PYTHONPATH=src.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from agnidrish.experiments import STAGES, develop, primary_label, run_stages, to_jsonable
from agnidrish.metrics import interval_metrics
from agnidrish.pipeline import PipelineSpec, screen
from agnidrish.predict import predict_by_parameter

REPO_ROOT = Path(__file__).resolve().parents[1]
log = logging.getLogger("run_experiments")
TRACKED = ("src", "configs", "scripts", "pyproject.toml")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout.strip()


def new_run_dir(experiment_id: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = REPO_ROOT / "artifacts" / "metrics" / experiment_id / f"{stamp}_{git('rev-parse', '--short', 'HEAD')}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def load_data(cfg: dict[str, Any]) -> pd.DataFrame:
    path = REPO_ROOT / cfg["dataset"]["path"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != cfg["dataset"]["sha256"]:
        raise SystemExit(f"dataset hash mismatch: {digest} != pre-registered {cfg['dataset']['sha256']}")
    return pd.read_csv(path)


def fmt(x: Any, digits: int = 3) -> str:
    return "—" if x is None or (isinstance(x, float) and x != x) else (f"{x:.{digits}f}" if isinstance(x, float) else str(x))


def stage_table(stages: dict[str, Any]) -> list[str]:
    head = "| Stage | Positives | Recall | Precision | FPR | PR-AUC | Escape rate | Review rate | False rejection | Auto-cleared | Recall (not gated) | Recall (scenario truth) |"
    lines = [head, "|" + "---|" * 12]
    for s, v in stages.items():
        p, o = v["primary_label"], v["operational"]
        lines.append(
            f"| {s} | {p['n_positive']} | {fmt(p['recall'])} | {fmt(p['precision'])} | {fmt(p['fpr'])} | {fmt(p.get('pr_auc'))} "
            f"| {fmt(o['defect_escape_rate'])} | {fmt(o['review_rate'])} | {fmt(o['false_rejection_rate'])} | {fmt(o['auto_cleared'])} "
            f"| {fmt(v['primary_label_ungated']['recall'])} | {fmt(v.get('scenario_truth', {}).get('recall'))} |"
        )
    return lines


def criteria(res: dict[str, Any], cfg: dict[str, Any]) -> list[str]:
    """Evaluate the pre-registered success criteria mechanically (text in the config)."""
    st = res["stages"]
    rec = {s: st[s]["primary_label"]["recall"] for s in STAGES}
    fpr = {s: st[s]["primary_label"]["fpr"] for s in STAGES}
    drift_rate = {s: _family_rate(st[s], "drift") for s in ("E2", "E3")}
    comp = res["predictor_comparison"]
    e4a = all(
        comp[m]["per_parameter"][p]["mae"] < comp["persistence"]["per_parameter"][p]["mae"]
        and comp[m]["per_parameter"][p]["tail_mae"] <= comp["persistence"]["per_parameter"][p]["tail_mae"]
        for p, m in res["chosen_predictors"].items()
    )
    cov = res["coverage_validation"]["overall"]["coverage"]
    op = res["operating_point"]
    rows = [
        ("E2", rec["E2"] > rec["E1"] and fpr["E2"] - fpr["E1"] <= 0.05, f"recall {fmt(rec['E1'])}→{fmt(rec['E2'])}, FPR Δ {fmt(fpr['E2'] - fpr['E1'])}"),
        ("E3", drift_rate["E3"] > drift_rate["E2"] and fpr["E3"] - fpr["E2"] <= 0.05,
         f"mean flag rate on anomalous drift families {fmt(drift_rate['E2'])}→{fmt(drift_rate['E3'])}, FPR Δ {fmt(fpr['E3'] - fpr['E2'])}"),
        ("E4 (a)", e4a, "chosen predictor beats persistence on MAE and tail MAE per parameter"),
        ("E4 (b)", rec["E4"] > rec["E3"], f"recall {fmt(rec['E3'])}→{fmt(rec['E4'])}"),
        ("E5", abs(cov - (1 - cfg["uncertainty"]["alpha"])) <= 0.05, f"coverage {fmt(cov)} vs target {1 - cfg['uncertainty']['alpha']:.2f}"),
        ("E6", op["reached_target"], f"R* {cfg['operating_point']['target_recall']} reached: {op['reached_target']}; recall {fmt(rec['E6'])}, review rate {fmt(st['E6']['operational']['review_rate'])}"),
    ]
    return ["| Criterion | Met | Evidence |", "|---|---|---|"] + [f"| {n} | {'yes' if ok else '**no**'} | {e} |" for n, ok, e in rows]


def _family_rate(stage: dict[str, Any], kind: str) -> float:
    from agnidrish.synthetic.families import FAMILY_KINDS, Kind

    rates = [r for f, r in stage["flag_rate_by_family"].items() if FAMILY_KINDS.get(f) == Kind(kind)]
    return sum(rates) / len(rates) if rates else float("nan")


def write_summary(path: Path, title: str, res: dict[str, Any], cfg: dict[str, Any], extra: list[str]) -> None:
    lines = [f"# {title}", "", "Data category: **SYNTHETIC** (development v1). Not official SIH/ISRO data.", ""]
    lines += extra
    lines += ["## Cumulative ablation (primary label: label_safety_slope, Δ_allow 0.15 relative; REVIEW counted as flagged)", ""]
    lines += stage_table(res["stages"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def development(cfg: dict[str, Any], cfg_path: Path) -> Path:
    table = load_data(cfg)
    res = develop(table, cfg)
    run = new_run_dir("E1-E6_validation")
    (run / "stage_specs.json").write_text(json.dumps(to_jsonable(res["specs"]), indent=2), encoding="utf-8")
    (run / "frozen_pipeline.json").write_text(json.dumps(to_jsonable(res["specs"]["E6"]), indent=2), encoding="utf-8")
    meta = {"config": cfg_path.relative_to(REPO_ROOT).as_posix(), "git_commit": git("rev-parse", "HEAD"),
            "git_dirty": bool(git("status", "--porcelain", "--", *TRACKED)), "split": "validation"}
    out = {k: v for k, v in res.items() if k != "specs"} | {"meta": meta}
    (run / "metrics.json").write_text(json.dumps(to_jsonable(out), indent=2), encoding="utf-8")
    comp = res["predictor_comparison"]
    extra = ["## Pre-registered success criteria", ""] + criteria(res, cfg) + ["", "## E4 predictors (validation, per parameter; units differ so MAE is not pooled)", "",
             "| Predictor | Parameter | MAE | RMSE | Tail MAE |", "|---|---|---|---|---|"]
    for m, v in comp.items():
        for p, r in v["per_parameter"].items():
            extra.append(f"| {m} | {p} | {fmt(r['mae'], 4)} | {fmt(r['rmse'], 4)} | {fmt(r['tail_mae'], 4)} |")
    cov = res["coverage_validation"]
    extra += ["", f"Chosen: {res['chosen_predictors']}. Conformal half-widths: {res['halfwidths']}.",
              f"E5 coverage (target {1 - cfg['uncertainty']['alpha']:.2f}): overall {fmt(cov['overall']['coverage'])}; "
              f"per parameter { {p: fmt(v['coverage']) for p, v in cov['per_parameter'].items()} }; "
              f"per-lot min {fmt(min(cov['per_lot_coverage'].values()))}, max {fmt(max(cov['per_lot_coverage'].values()))}.",
              f"E6 operating point (ADR-005): z_review = {res['operating_point']['z_review']}, R* reached: {res['operating_point']['reached_target']}.", ""]
    write_summary(run / "summary.md", "E1–E6 development run (validation lots)", res, cfg, extra)
    return run


def final(cfg: dict[str, Any], dev_run: Path) -> Path:
    if git("status", "--porcelain", "--", *TRACKED):
        raise SystemExit("final evaluation requires committed code and config (src, configs, scripts)")
    table = load_data(cfg)
    specs = {s: PipelineSpec.from_dict(d) for s, d in json.loads((dev_run / "stage_specs.json").read_text(encoding="utf-8")).items()}
    test_rows = table["split"] == cfg["dataset"]["final_split"]
    label = primary_label(table, cfg)
    stages = run_stages(table, test_rows, specs, label)
    e6 = specs["E6"]
    test = table[test_rows]
    pred = predict_by_parameter(e6.predictors, test)
    hw = test["parameter"].map(e6.halfwidths)
    coverage = interval_metrics(test["value_168h"], pred - hw, pred + hw)
    run = new_run_dir("E1-E6_test")
    decisions = test.join(screen(table, e6)[test_rows])
    decisions.to_csv(run / "test_decisions.csv", index=False)
    (run / "frozen_pipeline.json").write_text(json.dumps(to_jsonable(e6), indent=2), encoding="utf-8")
    meta = {"dev_run": dev_run.relative_to(REPO_ROOT).as_posix(), "git_commit": git("rev-parse", "HEAD"), "split": "test"}
    out = {"stages": stages, "coverage_test": coverage, "label_positives_test": int(label[test_rows].sum()), "meta": meta}
    (run / "metrics.json").write_text(json.dumps(to_jsonable(out), indent=2), encoding="utf-8")
    extra = [f"Frozen specs from development run `{meta['dev_run']}` — nothing was refit or retuned on test lots.", "",
             f"E5 interval coverage on test (target {1 - cfg['uncertainty']['alpha']:.2f}): {fmt(coverage['coverage'])} "
             f"(n = {coverage['n']}, mean width by parameter differs in units).", ""]
    write_summary(run / "summary.md", "E1–E6 FINAL evaluation (test lots, evaluated once)", {"stages": stages}, cfg, extra)
    return run


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default="configs/experiments/pipeline_v1.yaml")
    parser.add_argument("--final", metavar="DEV_RUN_DIR", help="evaluate the frozen specs of this development run on test lots")
    args = parser.parse_args()
    cfg_path = (REPO_ROOT / args.config).resolve()
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    run = final(cfg, (REPO_ROOT / args.final).resolve()) if args.final else development(cfg, cfg_path)
    log.info("recorded %s", run.relative_to(REPO_ROOT))
    sys.stdout.reconfigure(encoding="utf-8")  # the summaries contain →, Δ, ×; legacy Windows consoles default to cp1252
    print((run / "summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
