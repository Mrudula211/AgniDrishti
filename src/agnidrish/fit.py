"""Site calibration: fit a frozen PipelineSpec on historical burn-in lots (FR-20, ADR-006).

A deployment site has its own parameters, units and lots, so the frozen v1
pipeline (fitted on SYNTHETIC data for iddq/tpd) cannot be reused as-is. This
module re-runs exactly the pre-registered development procedure of E1-E6
(``experiments.develop``) on the site's historical data:

- Module B predictor chosen per parameter by lowest validation MAE (R0 metric);
- split-conformal half-widths fitted on calibration lots;
- REVIEW z threshold chosen by the ADR-005 operating point on validation lots.

Historical rows need a measured ``value_168h``: it is the regression target and
the source of the proxy label (ADR-004). Splits are whole lots (CLAUDE §7). If
the table already has a ``split`` column it is honoured and any ``test`` rows
are dropped unread; otherwise lots are assigned deterministically from a seed.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from agnidrish.experiments import develop
from agnidrish.schema import Checkpoint, SchemaError, required_columns

log = logging.getLogger(__name__)

FIT_SPLITS: tuple[str, ...] = ("train", "calibration", "validation")
METHOD_SECTIONS: tuple[str, ...] = ("checkpoint", "quality_gate", "lot_relative", "prediction", "uncertainty", "operating_point")


def load_fit_config(path: Path, repo_root: Path) -> dict[str, Any]:
    """Site config (label, splits) merged over the method sections of the pre-registered config it names.

    Methods are never redefined per site: ``methods_from`` points at the
    pre-registered experiment config, so a deployed pipeline is fitted with the
    same procedure that E1-E6 evaluated.
    """
    site = yaml.safe_load(path.read_text(encoding="utf-8"))
    methods = yaml.safe_load((repo_root / site["methods_from"]).read_text(encoding="utf-8"))
    cfg = {k: methods[k] for k in METHOD_SECTIONS}
    cfg["label"] = site["label"]
    cfg["splits"] = site["splits"]
    cfg["methods_from"] = site["methods_from"]
    cfg["dataset"] = {
        "fit_splits": {"model": "train", "conformal": "calibration"},
        "development_split": "validation",
    }
    return cfg


def assign_lot_splits(lot_ids: pd.Series, fractions: Mapping[str, float], seed: int) -> pd.Series:
    """Map every row to train / calibration / validation by whole lot (largest-remainder rounding).

    Deterministic for a given set of lot ids and seed. Every split gets at least one lot.

    Raises:
        ValueError: fewer lots than splits, or fractions that do not cover FIT_SPLITS.
    """
    if set(fractions) != set(FIT_SPLITS):
        raise ValueError(f"split fractions must name exactly {FIT_SPLITS}, got {sorted(fractions)}")
    lots = sorted(lot_ids.dropna().unique())
    n = len(lots)
    if n < len(FIT_SPLITS):
        raise ValueError(f"need at least {len(FIT_SPLITS)} lots to fit (one per split), got {n}")
    total = sum(fractions.values())
    exact = {s: fractions[s] / total * n for s in FIT_SPLITS}
    counts = {s: max(1, int(np.floor(v))) for s, v in exact.items()}
    while sum(counts.values()) > n:  # the max(1, …) floors can overshoot on very few lots
        counts[max(counts, key=lambda s: counts[s])] -= 1
    for s in sorted(FIT_SPLITS, key=lambda s: -(exact[s] - np.floor(exact[s])))[: n - sum(counts.values())]:
        counts[s] += 1
    shuffled = [lots[i] for i in np.random.default_rng(seed).permutation(n)]
    mapping: dict[str, str] = {}
    start = 0
    for s in FIT_SPLITS:
        mapping.update({lot: s for lot in shuffled[start : start + counts[s]]})
        start += counts[s]
    return lot_ids.map(mapping)


def prepare_history(table: pd.DataFrame, cfg: Mapping[str, Any]) -> pd.DataFrame:
    """Validate historical data and attach lot-grouped splits; ``test`` rows are dropped unread.

    Raises:
        SchemaError: required columns missing, no value_168h, or a parameter without a configured direction.
    """
    checkpoint = Checkpoint[cfg["checkpoint"]]
    missing = [c for c in (*required_columns(checkpoint), "value_168h") if c not in table.columns]
    if missing:
        raise SchemaError(f"historical data lacks columns needed to fit: {missing}")
    unconfigured = sorted(set(table["parameter"]) - set(cfg["label"]["directions"]))
    if unconfigured:
        raise SchemaError(f"no degradation direction configured for parameters {unconfigured} (label.directions)")
    if "split" in table.columns:
        dropped = int((~table["split"].isin(FIT_SPLITS)).sum())
        if dropped:
            log.info("dropping %d rows whose split is not one of %s (never read)", dropped, FIT_SPLITS)
        out = table[table["split"].isin(FIT_SPLITS)].copy()
    else:
        out = table.copy()
        out["split"] = assign_lot_splits(out["lot_id"], cfg["splits"]["fractions"], cfg["splits"]["seed"])
    empty = [s for s in FIT_SPLITS if not (out["split"] == s).any()]
    if empty:
        raise SchemaError(f"no lots in split(s) {empty}")
    return out.reset_index(drop=True)


def fit_pipeline(table: pd.DataFrame, cfg: Mapping[str, Any]) -> dict[str, Any]:
    """Run the pre-registered development procedure; returns ``develop`` results plus split sizes.

    ``result["specs"]["E6"]`` is the full pipeline to freeze and deploy.
    """
    history = prepare_history(table, cfg)
    result = develop(history, dict(cfg))
    result["split_lots"] = {s: int(history.loc[history["split"] == s, "lot_id"].nunique()) for s in FIT_SPLITS}
    result["split_rows"] = {s: int((history["split"] == s).sum()) for s in FIT_SPLITS}
    return result
