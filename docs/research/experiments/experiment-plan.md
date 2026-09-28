# Experiment Plan

Status: Draft · Last updated: 2026-09-26

No experiment has been executed. Every result field reads
**TBD — experiment not yet executed.** Success criteria are written before any
result is seen and must not be edited afterwards (add a dated note instead).

Common protocol: [evaluation-protocol.md](evaluation-protocol.md).

## Pre-registration (2026-09-26 — fixed before any detector, predictor or decision code)

Config: `configs/experiments/pipeline_v1.yaml` (authoritative values). Summary:

| Item | Value | Basis |
|---|---|---|
| Data | Synthetic development v1 (DS-04, SHA-256 `7a170d89…1cde0`) | ADR-003 |
| Development evaluation | validation lots; models fit on train lots, conformal on calibration lots | evaluation-protocol §2 |
| Final evaluation | test lots, once, after the pipeline is frozen | CLAUDE §7 |
| Decision checkpoint | T24 (Value_0h + Value_24h) | R0 Module B |
| Primary label | `label_safety_slope`, Δ_allow = 0.15 relative | ADR-002, ADR-004 |
| Quality gate | min lot size 20; scale floor 0.1 % of nominal | S-01 (IQR/1.35 inexact below 20) |
| Lot-relative scale / reject threshold | IQR/1.35; \|z\| ≥ 6 | AEC-Q001 Rev-D Dynamic PAT (S-01) |
| REVIEW z threshold | chosen on validation from {2, 2.5, 3, 3.5, 4, 5, 6} | ADR-005 |
| Predictors | persistence, linear extrapolation, population increment, linear regression; pick lowest validation MAE | R0 (MAE official) |
| Interval | split conformal, α = 0.10 | S-10 |
| R* | 0.95, REVIEW counted as flagged | ADR-005 |
| Success criteria | per experiment below and in the config | — |
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
| Result — synthetic development v1 (category: **synthetic**) | Audit **passed** 2026-09-26 (`src/agnidrish/audit.py`); statistics in the git-ignored manifest `data/synthetic/development/synthetic_development_v1_seed20260926.manifest.json`; version record in data-sources.md DS-04. Dataset statistics only — no method was evaluated. |
| Result — official / external data | TBD — experiment not yet executed |

## E1 — Static specification screening

| Field | Content |
|---|---|
| Hypothesis | Absolute limits miss a material share of proxy-labelled latent-defect cases |
| Layers | L0 + L1 |
| Checkpoints | T24, T96, T168 |
| Metrics | Recall, precision, F1, FNR, FPR, review/reject rate; per scenario (synthetic) |
| Success criterion | Not a pass/fail experiment — establishes the baseline |
| Result | Recorded (synthetic v1, test): recall 0.133, FPR 0.012 on the primary label (30 positives). Baseline only. Runs: `artifacts/metrics/E1-E6_validation/20260926-144425_c8ca99b` (validation), `artifacts/metrics/E1-E6_test/20260926-144448_c8ca99b` (test). |

## E2 — Static + lot statistics

| Field | Content |
|---|---|
| Hypothesis | Lot-relative level scoring detects below-limit outliers missed by E1 at acceptable FPR |
| Layers | L0 + L1 + L2 (level only) |
| Variants | MAD-based vs IQR-based robust scale; classical z (to show robustness effect); E2b Isolation Forest comparator (conditional) |
| Sensitivity | Lot size, contamination fraction, lot offset size, bimodal lots, measurement resolution |
| Metrics | As E1 + PR-AUC (score-based) + per-lot FPR spread |
| Success criterion | Recall on the primary label above E1 with FPR increase ≤ 0.05 (pre-registered) |
| Result | Recorded: criterion **not met** (recall unchanged 0.133; scenario-truth recall 0.055 → 0.127). See ablation-plan §5 F2. Runs: `artifacts/metrics/E1-E6_validation/20260926-144425_c8ca99b` (validation), `artifacts/metrics/E1-E6_test/20260926-144448_c8ca99b` (test). |

## E3 — Static + lot + trajectory

| Field | Content |
|---|---|
| Hypothesis | Lot-relative drift features detect "normal-level, abnormal-drift" parts missed by E2 |
| Layers | L0–L2 (level + drift) |
| Checkpoints | T24 (single increment) and T96 (+ slope change) separately |
| Metrics | As E2, reported per scenario |
| Success criterion | Recall on drift families above E2 with FPR increase ≤ 0.05 over E2 (pre-registered) |
| Result | Recorded: criterion met — recall 0.667, FPR 0.032 (test). F1. Runs: `artifacts/metrics/E1-E6_validation/20260926-144425_c8ca99b` (validation), `artifacts/metrics/E1-E6_test/20260926-144448_c8ca99b` (test). |

## E4 — + 168h prediction

| Field | Content |
|---|---|
| Hypothesis (a) | A simple model predicts `value_168h` at T24 better than persistence |
| Hypothesis (b) | Adding predicted-drift vs safety-slope rule improves early detection over E3 |
| Layers | L0–L4 (+ R1/R2/R3 rules using point prediction) |
| Models | B0 persistence, B1 linear extrapolation, B2 lot-median increment, B3 linear regression; E4b (conditional) GBM / hierarchical model |
| Metrics | MAE, RMSE, tail error (top-decile true v168), safety-slope confusion matrix, detection metrics as E3, hours of burn-in potentially saved (reported with assumption A-11) |
| Leakage checks | Feature availability matrix enforced; lot-grouped splits |
| Success criterion | (a) chosen model MAE below B0 on validation and tail MAE not worse than B0; (b) recall gain over E3 (pre-registered) |
| Result | Recorded: (a) met — population increment beats persistence on MAE and tail MAE per parameter; (b) **not met** — no recall gain over E3. F3. Runs: `artifacts/metrics/E1-E6_validation/20260926-144425_c8ca99b` (validation), `artifacts/metrics/E1-E6_test/20260926-144448_c8ca99b` (test). |

## E5 — + uncertainty

| Field | Content |
|---|---|
| Hypothesis | Prediction intervals achieve near-target coverage on held-out lots and, used in R2/R3, reduce escapes at a bounded review-rate increase |
| Layers | L0–L5 |
| Methods | U1 split conformal (lot-level calibration); U2/U3 conditional |
| Metrics | Coverage (overall, per lot, per scenario), interval width, then detection + operational metrics |
| Success criterion | Coverage within 0.05 of the 0.90 target overall on validation (pre-registered); escape-rate reduction vs E4 |
| Result | Recorded: criterion met — coverage 0.886 (validation), 0.887 (test) vs 0.90; per-lot 0.668–0.980. No detection change. F4. Runs: `artifacts/metrics/E1-E6_validation/20260926-144425_c8ca99b` (validation), `artifacts/metrics/E1-E6_test/20260926-144448_c8ca99b` (test). |

## E6 — Full decision rules

| Field | Content |
|---|---|
| Hypothesis | The full rule set gives the best escape-rate / review-rate trade-off of all variants |
| Layers | L0–L2, L4–L6 (+ L7 explanations generated) |
| Metrics | Defect escape rate, false rejection rate, review rate, auto-cleared %, recall–review-rate curve, latency per lot |
| Success criterion | Reaches R* = 0.95 on validation at a lower review rate than E5's interval rules alone; otherwise simplify (pre-registered) |
| Result | Recorded: **R* = 0.95 not reached** — recall 0.800 at review rate 0.104 (test; z_review = 2.5 chosen on validation). F5, F6. Runs: `artifacts/metrics/E1-E6_validation/20260926-144425_c8ca99b` (validation), `artifacts/metrics/E1-E6_test/20260926-144448_c8ca99b` (test). |

## Robustness experiments (after E6)

| ID | Stress | Result |
|---|---|---|
| R-01 | Held-out synthetic scenario family (anti-circularity) | TBD — experiment not yet executed |
| R-02 | Generator parameter sweep (noise, prevalence, onset, lot offset) | TBD — experiment not yet executed |
| R-03 | Missing checkpoints / glitches | TBD — experiment not yet executed |
| R-04 | Prediction models on NASA external data (resampled) | TBD — experiment not yet executed |
