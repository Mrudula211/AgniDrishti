"""AgniDrishti batch screening: screen a tester export at 24 h and record the run.

Usage (from the repository root, package installed or PYTHONPATH=src):
    python scripts/screen_lot.py --input export.csv --site configs/sites/<site>.yaml \
        --pipeline <path>/pipeline.json --category official [--profile profile.yaml] [--version v3]

The site config says how the export is laid out and where specification limits come from
(ADR-007); --profile overrides the site's input profile for this file. Same code path as
the web service (agnidrish.service). Output: artifacts/screening/<YYYYMMDD-HHMMSS>_<sha>/
{input.csv, pipeline.json, site.json, decisions.csv, lot_summary.csv, report.html, audit.json}.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import yaml

from agnidrish.ingest import InputProfile
from agnidrish.service import code_version, load_pipeline, prepare_input, read_csv_bytes, record_run, screen_table
from agnidrish.site import load_site

REPO_ROOT = Path(__file__).resolve().parents[1]
log = logging.getLogger("screen_lot")


def repo_path(p: str) -> Path:
    return Path(p) if Path(p).is_absolute() else REPO_ROOT / p


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True)
    ap.add_argument("--site", required=True, help="site config, e.g. configs/sites/synthetic_demo.yaml")
    ap.add_argument("--pipeline", required=True, help="pipeline.json from fit_pipeline.py, or frozen_pipeline.json from a recorded run")
    ap.add_argument("--category", required=True, choices=["official", "external", "synthetic"])
    ap.add_argument("--profile", help="YAML/JSON input profile overriding the site's `input` section")
    ap.add_argument("--version", default="unversioned", help="dataset version label")
    args = ap.parse_args()

    input_path = repo_path(args.input)
    data = input_path.read_bytes()
    site = load_site(repo_path(args.site), REPO_ROOT)
    pipeline = load_pipeline(repo_path(args.pipeline))
    profile = InputProfile.from_dict(yaml.safe_load(repo_path(args.profile).read_text(encoding="utf-8"))) if args.profile else None
    start = time.perf_counter()
    table, warnings, report = prepare_input(read_csv_bytes(data), pipeline, site, args.category, profile=profile, version=args.version)
    result = screen_table(table, pipeline)
    elapsed = (time.perf_counter() - start) * 1000.0
    for w in warnings:
        log.warning(w)
    run = record_run(REPO_ROOT / "artifacts" / "screening", input_bytes=data, source_name=input_path.name, result=result,
                     pipeline=pipeline, category=args.category, warnings=warnings, commit=code_version(REPO_ROOT),
                     elapsed_ms=elapsed, site=site, profile=profile or InputProfile.from_dict(site.input), ingest=report,
                     version=args.version)
    log.info("wrote %s", (run / "report.html").relative_to(REPO_ROOT))
    log.info("decisions: %s", result["decision"].value_counts().to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
