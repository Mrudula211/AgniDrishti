"""Layer L6 — ordered decision rules (decision-engine.md §1, ADR-001 Rev. 1). No fused score.

Rules are evaluated in order; the first matching rule sets the decision, and
every matching rule is recorded. Rules for layers that are switched off are
skipped (ablation). Missing evidence for an active rule forces REVIEW.

R0  quality-gate flag, or missing evidence for an active rule   -> REVIEW
R1  measured value outside the datasheet limit now              -> REJECT
R2  predicted drift exceeds the safety slope even at the
    optimistic end of the interval (point if no interval)       -> REJECT
R3  point prediction or pessimistic end exceeds                 -> REVIEW
R4  |z_level| and |z_drift| both >= z_reject                    -> REJECT
R5  |z_level| or |z_drift| >= z_review                          -> REVIEW
R6  none of the above                                           -> PASS
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

PASS, REVIEW, REJECT = "PASS", "REVIEW", "REJECT"


@dataclass(frozen=True)
class DecisionConfig:
    use_lot_level: bool = False
    use_lot_drift: bool = False
    use_prediction: bool = False
    use_interval: bool = False
    z_review: float = 6.0
    z_reject: float = 6.0


def decide(evidence: pd.DataFrame, config: DecisionConfig) -> pd.DataFrame:
    """Return ``decision``, ``fired_rules`` (";"-joined) and ``binary_flag`` (REVIEW counts as flagged).

    Required evidence columns: ``gate_flag``, ``spec_now``; plus ``z_level`` /
    ``z_drift`` if the lot layers are on; ``exceed_point`` if prediction is on;
    ``exceed_optimistic`` / ``exceed_pessimistic`` if the interval is on.
    """
    idx = evidence.index
    z_cols = [c for c, on in (("z_level", config.use_lot_level), ("z_drift", config.use_lot_drift)) if on]
    pred_cols = ["exceed_point"] if config.use_prediction else []
    if config.use_prediction and config.use_interval:
        pred_cols += ["exceed_optimistic", "exceed_pessimistic"]

    missing_evidence = evidence[z_cols + pred_cols].isna().any(axis=1) if z_cols or pred_cols else pd.Series(False, index=idx)
    rules: dict[str, pd.Series] = {
        "R0": evidence["gate_flag"].astype(bool) | missing_evidence,
        "R1": evidence["spec_now"].astype(bool),
    }
    false = pd.Series(False, index=idx)
    if config.use_prediction:
        point = evidence["exceed_point"].astype("boolean").fillna(False).astype(bool)
        if config.use_interval:
            optimistic = evidence["exceed_optimistic"].astype("boolean").fillna(False).astype(bool)
            pessimistic = evidence["exceed_pessimistic"].astype("boolean").fillna(False).astype(bool)
            rules["R2"] = point & optimistic
            rules["R3"] = point | pessimistic
        else:
            rules["R2"] = point
            rules["R3"] = false
    if z_cols:
        z = evidence[z_cols].abs()
        rules["R4"] = (z >= config.z_reject).all(axis=1) if len(z_cols) == 2 else false
        rules["R5"] = (z >= config.z_review).any(axis=1)

    outcome = {"R0": REVIEW, "R1": REJECT, "R2": REJECT, "R3": REVIEW, "R4": REJECT, "R5": REVIEW}
    decision = pd.Series(PASS, index=idx, dtype=object)
    decided = pd.Series(False, index=idx)
    for name in ("R0", "R1", "R2", "R3", "R4", "R5"):
        if name in rules:
            hit = rules[name] & ~decided
            decision[hit] = outcome[name]
            decided |= rules[name]
    fired = pd.Series(
        [";".join(n for n in rules if bool(rules[n].iloc[i])) or "R6" for i in range(len(idx))],
        index=idx,
    )
    return pd.DataFrame({"decision": decision, "fired_rules": fired, "binary_flag": decision != PASS})


def exceeds_safety_slope(
    value_0h: pd.Series,
    predicted_168h: pd.Series,
    allowance_value: pd.Series,
    allowance_relative: pd.Series,
    direction: pd.Series,
    spec_min: pd.Series,
    spec_max: pd.Series,
    t_end_h: float = 168.0,
) -> pd.Series:
    """ADR-002 §11 early-rejection test on a (predicted) 168 h value.

    Drift rate (Ŷ - V0)/t_end, signed by ``direction`` (+1 up, -1 down), exceeds
    Δ/t_end, where Δ = allowance_value (absolute) or allowance_value·|V0|
    (relative); or Ŷ lies outside the datasheet limits. <NA> if an input is missing.
    """
    delta = np.where(allowance_relative, allowance_value * value_0h.abs(), allowance_value)
    rate = (predicted_168h - value_0h) * direction / t_end_h
    outside = (predicted_168h > spec_max).fillna(False) | (predicted_168h < spec_min).fillna(False)
    result = (rate > delta / t_end_h) | outside
    return result.astype("boolean").mask(value_0h.isna() | predicted_168h.isna())
