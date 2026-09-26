# Ablation Plan

Status: Draft · Last updated: 2026-09-26

Purpose: show whether each layer adds measurable value. A layer that does not
improve the evidence is removed or simplified, not kept for presentation value.

## 1. Cumulative ablation (primary)

| Step | Configuration | Layers | Experiment |
|---|---|---|---|
| 1 | Static specification | L0, L1 | E1 |
| 2 | + lot statistics | + L2 (level) | E2 |
| 3 | + drift (trajectory) | + L2 (drift) | E3 |
| 4 | + 168h prediction | + L4, rules on point prediction | E4 |
| 5 | + uncertainty | + L5, interval-based rules | E5 |
| 6 | Full decision rules | + full L6 rule set | E6 |

## 2. Leave-one-out ablation (secondary)

From the full system (step 6), remove one layer at a time: −L2 level, −L2 drift,
−L4, −L5, −R4 (joint-extreme reject rule). Shows interactions the
cumulative order can hide.

## 3. Result table (to be filled from recorded runs only)

Data category: ______ · Checkpoint: ______ · Label: ______ · Positives: ______

| Step | Recall | Precision | F1 | PR-AUC | FNR | FPR | Escape rate | Review rate | Auto-cleared % | MAE (168h) | PI coverage | PI width |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 Static | TBD | TBD | TBD | — | TBD | TBD | TBD | TBD | TBD | — | — | — |
| 2 + Lot | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | — | — | — |
| 3 + Trajectory | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | — | — | — |
| 4 + 168h pred. | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | — | — |
| 5 + Uncertainty | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 6 Full | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

TBD — experiment not yet executed.

## 4. Decision rule for keeping a layer

Keep layer L if, on held-out lots, adding it improves the primary trade-off
(escape rate at a fixed review-rate budget, or review rate at a fixed escape
target) beyond the bootstrap uncertainty, **or** it is required for safety (L0)
or explainability (L7). Otherwise remove it and record the decision in an ADR.
