# Experiment Plan

Status: Draft · Last updated: 2026-09-26

No experiment has been executed. Every result field reads
**TBD — experiment not yet executed.** Success criteria are written before any
result is seen and must not be edited afterwards (add a dated note instead).

Common protocol: [evaluation-protocol.md](evaluation-protocol.md).
Ablation view: [ablation-plan.md](ablation-plan.md).

Each experiment is run separately per data category (official / external /
synthetic) and results are never pooled across categories.

---

## E0 — Data audit (prerequisite)

| Field | Content |
|---|---|
| Question | What does the data actually contain? Do assumptions A-01…A-14 hold? |
| Data | Whatever dataset is being introduced |
| Method | Schema, units, missingness, lot sizes, value resolution (MAD = 0 risk), distributions per checkpoint, label prevalence |
| Output | Updated data dictionary + assumption statuses |
| Result | TBD — experiment not yet executed |

## E1 — Static specification screening

| Field | Content |
|---|---|
| Hypothesis | Absolute limits miss a material share of proxy-labelled latent-defect cases |
| Layers | L0 + L1 |
| Checkpoints | T24, T96, T168 |
| Metrics | Recall, precision, F1, FNR, FPR, review/reject rate; per scenario (synthetic) |
| Success criterion | Not a pass/fail experiment — establishes the baseline |
| Result | TBD — experiment not yet executed |

## E2 — Static + lot statistics

| Field | Content |
|---|---|
| Hypothesis | Lot-relative level scoring detects below-limit outliers missed by E1 at acceptable FPR |
| Layers | L0 + L1 + L2 (level only) |
| Variants | MAD-based vs IQR-based robust scale; classical z (to show robustness effect); E2b Isolation Forest comparator (conditional) |
| Sensitivity | Lot size, contamination fraction, lot offset size, bimodal lots, measurement resolution |
| Metrics | As E1 + PR-AUC (score-based) + per-lot FPR spread |
| Success criterion | Recall improves over E1 on held-out lots with FPR increase judged acceptable by the team (bound to be set before running) |
| Result | TBD — experiment not yet executed |

## E3 — Static + lot + trajectory

| Field | Content |
|---|---|
| Hypothesis | Lot-relative drift features detect "normal-level, abnormal-drift" parts missed by E2 |
| Layers | L0–L3 |
| Checkpoints | T24 (single increment) and T96 (+ slope change) separately |
| Metrics | As E2, reported per scenario |
| Success criterion | Recall gain on drift scenarios without loss on others beyond noise (bounded before running) |
| Result | TBD — experiment not yet executed |

## E4 — + 168h prediction

| Field | Content |
|---|---|
| Hypothesis (a) | A simple model predicts `value_168h` at T24 better than persistence |
| Hypothesis (b) | Adding predicted-drift vs safety-slope rule improves early detection over E3 |
| Layers | L0–L4 (+ R1/R2/R3 rules using point prediction) |
| Models | B0 persistence, B1 linear extrapolation, B2 lot-median increment, B3 linear regression; E4b (conditional) GBM / hierarchical model |
| Metrics | MAE, RMSE, tail error (top-decile true v168), safety-slope confusion matrix, detection metrics as E3, hours of burn-in potentially saved (reported with assumption A-11) |
| Leakage checks | Feature availability matrix enforced; lot-grouped splits |
| Success criterion | (a) chosen model beats B0 on held-out lots including the tail; (b) recall gain over E3 |
| Result | TBD — experiment not yet executed |

## E5 — + uncertainty

| Field | Content |
|---|---|
| Hypothesis | Prediction intervals achieve near-target coverage on held-out lots and, used in R2/R3, reduce escapes at a bounded review-rate increase |
| Layers | L0–L5 |
| Methods | U1 split conformal (lot-level calibration); U2/U3 conditional |
| Metrics | Coverage (overall, per lot, per scenario), interval width, then detection + operational metrics |
| Success criterion | Coverage within a tolerance of target (tolerance set before running); escape-rate reduction vs E4 |
| Result | TBD — experiment not yet executed |

## E6 — Full risk decision framework

| Field | Content |
|---|---|
| Hypothesis | The full rule set gives the best escape-rate / review-rate trade-off of all variants |
| Layers | L0–L6 (+ L7 explanations generated) |
| Metrics | Defect escape rate, false rejection rate, review rate, auto-cleared %, recall–review-rate curve, latency per lot |
| Success criterion | Dominates or matches E5 on the curve; otherwise simplify |
| Result | TBD — experiment not yet executed |

## Robustness experiments (after E6)

| ID | Stress | Result |
|---|---|---|
| R-01 | Held-out synthetic scenario family (anti-circularity) | TBD — experiment not yet executed |
| R-02 | Generator parameter sweep (noise, prevalence, onset, lot offset) | TBD — experiment not yet executed |
| R-03 | Missing checkpoints / glitches | TBD — experiment not yet executed |
| R-04 | Prediction models on NASA external data (resampled) | TBD — experiment not yet executed |
