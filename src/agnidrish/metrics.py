"""Evaluation metrics (FR-15). Rows whose label is <NA> are excluded and counted.

Undefined ratios (e.g. recall with no positives) are NaN, never 0 or 1.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def _ratio(num: float, den: float) -> float:
    return float(num) / den if den else float("nan")


def detection_metrics(label: pd.Series, flagged: pd.Series) -> dict[str, float]:
    """Recall, precision, F1, FNR, FPR for boolean ``flagged`` against ``label``."""
    known = label.notna()
    y = label[known].astype(bool).to_numpy()
    f = flagged[known].astype(bool).to_numpy()
    tp = int((y & f).sum())
    fp = int((~y & f).sum())
    fn = int((y & ~f).sum())
    tn = int((~y & ~f).sum())
    recall = _ratio(tp, tp + fn)
    precision = _ratio(tp, tp + fp)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else float("nan")
    return {
        "n": tp + fp + fn + tn,
        "n_positive": tp + fn,
        "n_unlabelled": int((~known).sum()),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "fnr": _ratio(fn, tp + fn),
        "fpr": _ratio(fp, fp + tn),
    }


def average_precision(label: pd.Series, score: pd.Series) -> float:
    """Area under the precision-recall curve as step-wise average precision.

    Rows ranked by descending score (stable order for ties); rows with a missing
    label are dropped; a missing or non-finite score ranks last.
    """
    known = label.notna()
    y = label[known].astype(bool).to_numpy()
    s = pd.to_numeric(score[known], errors="coerce").to_numpy(dtype=float)
    s = np.where(np.isfinite(s), s, -np.inf)
    if not y.any():
        return float("nan")
    order = np.argsort(-s, kind="stable")
    hits = y[order]
    precision_at_k = np.cumsum(hits) / np.arange(1, len(hits) + 1)
    return float(precision_at_k[hits].sum() / hits.sum())


def regression_metrics(true: pd.Series, pred: pd.Series) -> dict[str, float]:
    """MAE and RMSE over rows where both values are present (units of the target)."""
    ok = true.notna() & pred.notna()
    err = (pred[ok] - true[ok]).to_numpy(dtype=float)
    if len(err) == 0:
        return {"n": 0, "mae": float("nan"), "rmse": float("nan")}
    return {"n": int(len(err)), "mae": float(np.abs(err).mean()), "rmse": float(math.sqrt((err**2).mean()))}


def tail_mae(true: pd.Series, pred: pd.Series, groups: pd.Series, quantile: float) -> float:
    """MAE on rows whose true value is at or above the ``quantile`` of its group."""
    ok = true.notna() & pred.notna()
    threshold = true[ok].groupby(groups[ok]).transform(lambda v: v.quantile(quantile))
    tail = (true[ok] >= threshold).reindex(true.index, fill_value=False)
    return regression_metrics(true[tail], pred[tail])["mae"]


def interval_metrics(true: pd.Series, low: pd.Series, high: pd.Series) -> dict[str, float]:
    """Empirical coverage and width of prediction intervals (units of the target)."""
    ok = true.notna() & low.notna() & high.notna()
    inside = (true[ok] >= low[ok]) & (true[ok] <= high[ok])
    width = (high[ok] - low[ok])
    return {
        "n": int(ok.sum()),
        "coverage": float(inside.mean()) if ok.any() else float("nan"),
        "mean_width": float(width.mean()) if ok.any() else float("nan"),
        "median_width": float(width.median()) if ok.any() else float("nan"),
    }


def operational_metrics(label: pd.Series, decision: pd.Series) -> dict[str, float]:
    """Escape rate, false rejection rate, review rate, auto-cleared share (evaluation-protocol §3.4)."""
    known = label.notna()
    y = label[known].astype(bool)
    d = decision[known]
    return {
        "defect_escape_rate": _ratio(((d == "PASS") & y).sum(), y.sum()),
        "false_rejection_rate": _ratio(((d == "REJECT") & ~y).sum(), (~y).sum()),
        "review_rate": _ratio((decision == "REVIEW").sum(), len(decision)),
        "auto_cleared": _ratio((decision == "PASS").sum(), len(decision)),
        "reject_rate": _ratio((decision == "REJECT").sum(), len(decision)),
    }
