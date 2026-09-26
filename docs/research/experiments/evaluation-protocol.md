# Evaluation Protocol

Status: Draft · Last updated: 2026-09-26

## 1. Units of evaluation

- Detection/decision metrics: per component per checkpoint (T24, T96, T168 reported separately).
- Prediction metrics: per component, target `value_168h`.
- Positive class: proxy latent-defect label (A-06) — which label is used is stated in every result.

## 2. Splits and leakage control

| Rule | Detail |
|---|---|
| Group by lot | Train / validation / calibration / test sets contain **disjoint lots** (grouped K-fold for development). |
| Frozen test lots | Test lots selected once, by seed, before any modelling; not looked at until final evaluation. |
| Calibration lots | Separate from train and test (for L5 conformal calibration and threshold selection where needed). |
| Component uniqueness | A `component_id` appears in exactly one split; duplicates removed before splitting (checked by test). |
| Temporal availability | At checkpoint T, features use only values measured at ≤ T (feature availability matrix in data-dictionary §4). |
| Target isolation | `value_168h` and all labels never enter feature computation for T24/T96. |
| Fit-on-train only | Any learned parameter (regression coefficients, lot-increment medians, thresholds, interval quantiles) is fitted on training/calibration lots only. |
| Lot statistics | Median/MAD of the component's own lot at the same checkpoint are allowed (available operationally); peers' labels/future values are not. |
| Synthetic scenario hold-out | At least one scenario family unseen in development, used only in R-01. |

Leakage checks become automated tests in P1/P2.

## 3. Metrics

### 3.1 Detection (anomaly / screening)

Recall, precision, F1, PR-AUC (for score-based detectors), false-negative rate
(= 1 − recall), false-positive rate. REVIEW is counted two ways and both are
reported: (a) REVIEW treated as flagged (catches) — for escape analysis;
(b) REVIEW treated separately — for workload.

Accuracy is not reported as a headline metric (rare positives).

### 3.2 Prediction

MAE, RMSE, median absolute error, tail error (MAE on components with true
v168 in the top decile of their lot, and on positives), error by scenario,
signed bias. Error of predicted drift slope vs safety slope as a
confusion matrix.

### 3.3 Uncertainty

Empirical coverage of prediction intervals (overall, per lot, per scenario),
mean and median interval width, coverage–width trade-off across α.
Calibration (reliability diagram / ECE) only if a probability output is produced.

### 3.4 Operational

| Metric | Definition |
|---|---|
| Defect escape rate | Positives decided PASS / all positives |
| False rejection rate | Negatives decided REJECT / all negatives |
| Review rate | REVIEW / all components |
| Automatically cleared % | PASS / all components |
| Latency | Wall-clock time per lot on a stated machine (P2 onward) |

## 4. Uncertainty in the metrics

Report confidence intervals for metrics (e.g. bootstrap over lots) because
positives are rare and lots are the unit of variation. With few positives,
state the count of positives next to every recall value.

## 5. Reporting

Each run writes `artifacts/metrics/<experiment>/<run>/` with: config, dataset
version and category, split seed and lot lists, metrics JSON, commit hash.
Tables in docs link to those files. No number enters documentation or slides
without such a link.
