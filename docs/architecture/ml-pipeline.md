# ML Pipeline (Provisional)

Status: Proposed · Last updated: 2026-09-26

Layers L2, L4, L5 (L3 merged into L2 — ADR-001 Revision 1). "ML" is used loosely: most layers are robust statistics or simple
regression by design. Advanced methods appear only as conditional extensions.

---

## L2 — Lot-Relative Analysis

| Item | Content |
|---|---|
| Purpose | Module A: measure how abnormal a component is relative to its lot (PSR-02) |
| Inputs | Lot table at checkpoint T (values and drifts available at T) |
| Outputs | `z_level_t`, `z_drift_t`, drift features (below), lot median, lot robust scale |
| Assumptions | A-04, A-05, A-07 |
| Candidate methods | Robust z with median and 1.4826·MAD; the same on drift; one-sided (upper) and two-sided variants |
| Alternatives | AEC-Q001 Rev-D DPAT formula: median ± 6·(IQR/1.35) (verified, S-01) — proposed as the E2 **baseline** variant; classical z (to show why robust matters); Isolation Forest (comparator, E2b); robust Mahalanobis on (level, drift) |
| Risks | MAD = 0 (quantised data); small lots → noisy scale; contaminated lots mask outliers; bimodal lots → false flags |
| Validation | Unit tests vs hand-computed values; E2 sensitivity to lot size, contamination, bimodality |
| Expected evidence | E2 vs E1: recall/FPR delta, per-lot FPR spread. TBD — experiment not yet executed |

Design note `[EI]`: also compute the lot-scale floor (minimum scale from
measurement resolution, config) to avoid division by ~0.

---

## L2 (drift part) — Drift / Trajectory Features

Formerly layer L3; merged into L2 on 2026-09-26 (ADR-001 Revision 1). Content unchanged.

| Item | Content |
|---|---|
| Purpose | Capture temporal abnormality with checkpoint-appropriate features (PSR-01) |
| Inputs | Values available at T; lot statistics from L2 |
| Outputs | T24: `delta_24`, `rel_delta_24`, `slope_0_24`, `z_drift_24`. T96: + `slope_24_96`, `slope_change`, `z_drift_96` |
| Assumptions | A-01, A-02 (nominal times), A-13 |
| Candidate methods | Finite differences divided by elapsed time; lot-relative z of each |
| Alternatives | Population-level shape model (fit a shared exponent per lot/family, score deviation) — E4b; per-component power law — rejected at T24/T96 (M-02) |
| Risks | Noise amplification in differences; single-point glitches; relative drift unstable near v0 ≈ 0 |
| Validation | Unit tests with unequal spacing; leakage tests (no v96 at T24, no v168 before T168) |
| Expected evidence | E3 per-scenario recall gain on "normal level, abnormal drift". TBD — experiment not yet executed |

Sparse-series rule: no recurrent / attention / convolutional sequence model.
To propose one, document: why appropriate, which baseline limitation it
addresses, required data volume, validation method, expected benefit.

---

## L4 — 168h Prediction

| Item | Content |
|---|---|
| Purpose | Module B: estimate `value_168h` early (PSR-03) and derive predicted drift for the safety-slope rule (PSR-04) |
| Inputs | Module B: T24 features only (`value_0h`, `value_24h`) — official PS (R0), DL-01 resolved. Optional T96 extension is outside Module B |
| Outputs | `pred_168h` (official target, scored by MAE); `pred_slope_0_168` derived for the safety-slope rule (drift-rate formula is our design choice, DL-06/DL-08) |
| Assumptions | Relationship learned on training lots transfers to new lots |
| Candidate methods (in order) | **B0** persistence: ŷ = v24. **B1** linear extrapolation: ŷ = v24 + slope_0_24·144. **B2** lot-median increment: ŷ = v24 + median ratio/increment learned on training lots. **B3** linear regression on (v0, v24) (and lot-relative terms). **B4 (conditional)** gradient-boosted trees; hierarchical / mixed-effects degradation model; GP with population prior |
| Alternatives | Direct classification of "will exceed safety slope" without regression — compare in E4 |
| Risks | B1 over-extrapolates stabilising parts; trees cannot extrapolate beyond training range (M-05) — worst for exactly the high-risk parts; distribution shift across lots |
| Validation | Grouped-by-lot CV; MAE, RMSE, tail error; residual plots by scenario |
| Expected evidence | Best simple model vs B0 on held-out lots. B4 kept only if it beats B3 on tail error. TBD — experiment not yet executed |

---

## L5 — Uncertainty Estimation

| Item | Content |
|---|---|
| Purpose | Quantify how far the true 168h value may be from the prediction, to support REVIEW (PSR-05) |
| Inputs | L4 model; calibration lots (disjoint from train and test) |
| Outputs | `pi_low`, `pi_high` at target coverage 1 − α (config) |
| Assumptions | Calibration and test lots exchangeable (approximately) |
| Candidate methods | **U1** split conformal with absolute residuals (equivalent to empirical residual quantile), calibration by lot. **U2 (conditional)** conformalised quantile regression (adaptive width). **U3 (conditional)** group-conditional (per device family) conformal |
| Alternatives | Model-based intervals (Bayesian linear / GP) — valid only if model is correct; compare coverage |
| Risks | Coverage fails under lot shift; intervals too wide to be useful; small calibration set → unstable quantile |
| Validation | Empirical coverage overall, per lot, per scenario; mean/median width |
| Expected evidence | Coverage near target on held-out lots; width that still allows PASS for most healthy parts. TBD — experiment not yet executed |

Terminology: output is a **prediction interval with target marginal coverage**,
not a confidence interval and not a failure probability (see glossary).
