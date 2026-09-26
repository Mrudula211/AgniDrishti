"""AgniDrishti prototype: screen a lot file at 24 h and write decisions + an HTML evidence report.

Usage (from the repository root, package installed or PYTHONPATH=src):
    python scripts/screen_lot.py --input lots.csv --pipeline <run>/frozen_pipeline.json --category synthetic
    python scripts/screen_lot.py --input raw.csv --mapping mapping.yaml --category official --version v1 ...

The input must be canonical (FR-01) or be mapped with --mapping (raw -> canonical YAML).
Output: artifacts/screening/<YYYYMMDD-HHMMSS>_<sha>/{decisions.csv, report.html}.
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

from agnidrish.pipeline import PipelineSpec, screen
from agnidrish.report import render_report
from agnidrish.schema import Checkpoint, to_canonical

REPO_ROOT = Path(__file__).resolve().parents[1]
log = logging.getLogger("screen_lot")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True)
    ap.add_argument("--pipeline", required=True, help="frozen_pipeline.json from a recorded run")
    ap.add_argument("--category", required=True, choices=["official", "external", "synthetic"])
    ap.add_argument("--mapping", help="YAML raw->canonical column mapping (omit for canonical input)")
    ap.add_argument("--version", default="unversioned", help="dataset version label when --mapping is used")
    ap.add_argument("--coverage", type=float, default=0.90, help="target coverage of the pipeline's interval")
    args = ap.parse_args()

    raw = pd.read_csv(REPO_ROOT / args.input if not Path(args.input).is_absolute() else args.input)
    spec = PipelineSpec.from_dict(json.loads(Path(args.pipeline).read_text(encoding="utf-8")))
    if args.mapping:
        mapping = yaml.safe_load(Path(args.mapping).read_text(encoding="utf-8"))
        table = to_canonical(raw, mapping, checkpoint=Checkpoint[spec.checkpoint], data_category=args.category, dataset_version=args.version)
    else:
        table = raw
        if "data_category" in table.columns and set(table["data_category"]) != {args.category}:
            raise SystemExit(f"--category {args.category} disagrees with the file's data_category {sorted(set(table['data_category']))}")
    # Decisions at 24 h must never see later measurements.
    table = table.drop(columns=[c for c in ("value_96h", "value_168h") if c in table.columns])

    result = table.join(screen(table, spec))
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
    out = REPO_ROOT / "artifacts" / "screening" / f"{datetime.now(timezone.utc):%Y%m%d-%H%M%S}_{sha}"
    out.mkdir(parents=True, exist_ok=False)
    result.to_csv(out / "decisions.csv", index=False)
    note = f"Checkpoint {spec.checkpoint}; pipeline {Path(args.pipeline).as_posix()}; input {args.input}."
    (out / "report.html").write_text(
        render_report(result, title="AgniDrishti — 24 h screening report", category=args.category,
                      coverage=args.coverage if spec.halfwidths else None, pipeline_note=note),
        encoding="utf-8",
    )
    log.info("wrote %s", (out / "report.html").relative_to(REPO_ROOT))
    log.info("decisions: %s", result["decision"].value_counts().to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
