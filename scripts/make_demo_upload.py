"""Write the demo upload file: held-out SYNTHETIC test lots as a tester would export them at 24 h.

    python scripts/make_demo_upload.py

Reads the pre-registered development dataset (hash-checked), keeps only the test split
and the canonical columns available at 24 h (no 96 h / 168 h values, no ground truth), and writes
data/synthetic/development/synthetic_development_v1_test_lots_24h_upload.csv.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd
import yaml

from agnidrish.schema import CANONICAL_ORDER, Checkpoint, model_input_columns

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "data" / "synthetic" / "development" / "synthetic_development_v1_test_lots_24h_upload.csv"


def main() -> int:
    cfg = yaml.safe_load((REPO_ROOT / "configs" / "experiments" / "pipeline_v1.yaml").read_text(encoding="utf-8"))
    path = REPO_ROOT / cfg["dataset"]["path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != cfg["dataset"]["sha256"]:
        raise SystemExit("dataset hash differs from the pre-registered one; regenerate with scripts/generate_synthetic.py")
    table = pd.read_csv(path)
    test = table[table["split"] == cfg["dataset"]["final_split"]]
    keep = [c for c in (*CANONICAL_ORDER, "nominal_value") if c in model_input_columns(list(test.columns), Checkpoint.T24)]
    test[keep].to_csv(OUT, index=False)
    print(f"wrote {OUT.relative_to(REPO_ROOT)}: {len(test)} rows, {test['lot_id'].nunique()} lots, columns {keep}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
