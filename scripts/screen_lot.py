"""AgniDrishti prototype: screen a lot file at 24 h and write decisions + an HTML evidence report.

Usage (from the repository root, package installed or PYTHONPATH=src):
    python scripts/screen_lot.py --input lots.csv --pipeline <path>/pipeline.json --category synthetic
    python scripts/screen_lot.py --input raw.csv --mapping mapping.yaml --category official --version v1 ...

The input must be canonical (FR-01) or be mapped with --mapping (raw -> canonical YAML).
Same code path as the web service (agnidrish.service). Output:
artifacts/screening/<YYYYMMDD-HHMMSS>_<sha>/{input.csv, pipeline.json, decisions.csv,
lot_summary.csv, report.html, audit.json}.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import yaml

from agnidrish.service import code_version, load_pipeline, prepare_input, read_csv_bytes, record_run, screen_table

REPO_ROOT = Path(__file__).resolve().parents[1]
log = logging.getLogger("screen_lot")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True)
    ap.add_argument("--pipeline", required=True, help="pipeline.json from fit_pipeline.py, or frozen_pipeline.json from a recorded run")
    ap.add_argument("--category", required=True, choices=["official", "external", "synthetic"])
    ap.add_argument("--mapping", help="YAML raw->canonical column mapping (omit for canonical input)")
    ap.add_argument("--version", default="unversioned", help="dataset version label when --mapping is used")
    args = ap.parse_args()

    input_path = Path(args.input) if Path(args.input).is_absolute() else REPO_ROOT / args.input
    data = input_path.read_bytes()
    pipeline = load_pipeline(Path(args.pipeline))
    mapping = yaml.safe_load(Path(args.mapping).read_text(encoding="utf-8")) if args.mapping else None
    start = time.perf_counter()
    table, warnings = prepare_input(read_csv_bytes(data), pipeline, args.category, mapping=mapping, version=args.version)
    result = screen_table(table, pipeline)
    elapsed = (time.perf_counter() - start) * 1000.0
    for w in warnings:
        log.warning(w)
    run = record_run(REPO_ROOT / "artifacts" / "screening", input_bytes=data, source_name=input_path.name, result=result,
                     pipeline=pipeline, category=args.category, warnings=warnings, commit=code_version(REPO_ROOT),
                     elapsed_ms=elapsed, mapping=mapping, version=args.version)
    log.info("wrote %s", (run / "report.html").relative_to(REPO_ROOT))
    log.info("decisions: %s", result["decision"].value_counts().to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
