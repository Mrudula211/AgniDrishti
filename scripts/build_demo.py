"""Build the demo page from a recorded FINAL test run (demo-flow.md). Synthetic data, evaluation mode.

    python scripts/build_demo.py artifacts/metrics/E1-E6_test/<run>

Featured rows are chosen by fixed rules from the test lots — never hand-made:
  1. caught: primary-label positive that static screening (E1) passes and the full system (E6) flags;
     largest |z_drift| first.
  2. correctly passed: healthy row in a high-mean lot, E6 PASS, highest 24 h value.
  3. missed: primary-label positive that E6 passes (an escape); largest actual 0->168 h change first.
Writes artifacts/demo/<YYYYMMDD-HHMMSS>_<sha>/index.html.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

from agnidrish.experiments import primary_label
from agnidrish.pipeline import PipelineSpec, screen
from agnidrish.report import render_report

REPO_ROOT = Path(__file__).resolve().parents[1]


def fmt(x: object) -> str:
    return "—" if x is None else (f"{x:.3f}" if isinstance(x, float) else str(x))


def evidence_table(final: dict, final_run: str, dev_run: str) -> str:
    rows = "".join(
        f"<tr><td>{s}</td><td>{fmt(v['primary_label']['recall'])}</td><td>{fmt(v['primary_label']['fpr'])}</td>"
        f"<td>{fmt(v['operational']['defect_escape_rate'])}</td><td>{fmt(v['operational']['review_rate'])}</td>"
        f"<td>{fmt(v['operational']['false_rejection_rate'])}</td><td>{fmt(v['scenario_truth']['recall'])}</td></tr>"
        for s, v in final["stages"].items()
    )
    n_pos = final["label_positives_test"]
    return f"""<h2>Evidence: cumulative ablation on held-out test lots (evaluated once)</h2>
<p class="muted">Primary label: measured 0→168 h drift above 15 % of the 0 h value, or 168 h value outside the limit (ADR-002/004) —
our proxy, not an official label. {n_pos} positive rows, so rates are imprecise. REVIEW counts as flagged.
E1 static limits · E2 + lot level · E3 + lot drift · E4 + 168 h prediction · E5 + prediction interval · E6 + tuned REVIEW threshold.
Runs: <code>{final_run}</code> (test) from <code>{dev_run}</code> (development).</p>
<div class="wrap"><table><tr><th>Stage</th><th>Recall</th><th>FPR</th><th>Escape rate</th><th>Review rate</th><th>False rejection</th><th>Recall vs scenario truth</th></tr>{rows}</table></div>
<p class="muted">Findings: lot-relative drift (E3) gives the largest gain; the 168 h prediction and the interval (E4, E5) did not change detection on this data;
the pre-registered target recall 0.95 was not reached. Interval coverage on test: {fmt(final['coverage_test']['coverage'])} (target 0.90).</p>"""


def main() -> int:
    final_run = Path(sys.argv[1]).resolve()
    final = json.loads((final_run / "metrics.json").read_text(encoding="utf-8"))
    dev_run = REPO_ROOT / final["meta"]["dev_run"]
    specs = {s: PipelineSpec.from_dict(d) for s, d in json.loads((dev_run / "stage_specs.json").read_text(encoding="utf-8")).items()}
    cfg = yaml.safe_load((REPO_ROOT / "configs/experiments/pipeline_v1.yaml").read_text(encoding="utf-8"))
    table = pd.read_csv(REPO_ROOT / cfg["dataset"]["path"])
    test = table[table["split"] == "test"]

    visible = test.drop(columns=["value_96h", "value_168h"])  # decisions never see later values
    e6 = screen(visible, specs["E6"])
    e1 = screen(visible, specs["E1"])
    rows = test.join(e6)
    label = primary_label(test, cfg).fillna(False).astype(bool)

    featured = []
    caught = rows[label & (e1["decision"] == "PASS") & (e6["decision"] != "PASS")]
    if not caught.empty:
        r = caught.loc[caught["z_drift"].abs().idxmax()]
        featured.append((r, f"Caught: passes the static limit check (E1) but is flagged by the full system (E6). Generator family: {r['behaviour_family']}."))
    ok = rows[~rows["is_anomaly"] & (rows["lot_scenario"] == "high_mean") & (e6["decision"] == "PASS")]
    if not ok.empty:
        r = ok.loc[ok["value_24h"].idxmax()]
        featured.append((r, "Correctly passed: high value, but consistent with its (high-mean) lot and not drifting abnormally."))
    missed = rows[label & (e6["decision"] == "PASS")]
    if not missed.empty:
        r = missed.loc[(missed["value_168h"] - missed["value_0h"]).abs().idxmax()]
        featured.append((r, f"Missed (escape): nothing at 24 h gave it away. Generator family: {r['behaviour_family']}."))

    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
    out = REPO_ROOT / "artifacts" / "demo" / f"{datetime.now(timezone.utc):%Y%m%d-%H%M%S}_{sha}"
    out.mkdir(parents=True, exist_ok=False)
    rel = lambda p: p.relative_to(REPO_ROOT).as_posix()  # noqa: E731
    page = render_report(
        rows,
        title="AgniDrishti — prototype demo (24 h screening of held-out test lots)",
        category="synthetic",
        coverage=0.90,
        pipeline_note="Frozen pipeline from the development run; decisions use only 0 h and 24 h values. "
        "Squares at 168 h show the actual value, revealed after the decision for evaluation only.",
        show_actual=True,
        featured=featured,
        evidence_html=evidence_table(final, rel(final_run), rel(dev_run)),
        max_cards=40,
    )
    (out / "index.html").write_text(page, encoding="utf-8")
    print(rel(out / "index.html"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
