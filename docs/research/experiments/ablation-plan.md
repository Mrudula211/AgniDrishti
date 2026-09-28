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

**−L4/−L5 recorded 2026-09-28** (development result, validation lots only, SYNTHETIC; the test split is spent).
This is the decision path for a parameter without a fitted forecast (ADR-007, FR-24), so every site fit now reports it.
Run: `artifacts/models/pipeline/20260928-134603_4c2bad5/fit_metrics.json` (`no_forecast_validation`), same data and
thresholds as the E6 development run.

| Configuration (validation, 55 positives) | Recall | Precision | FPR | Escape rate | Review rate | False rejection |
|---|---|---|---|---|---|---|
| E6 full rules | 0.782 | 0.090 | 0.195 | 0.218 | 0.200 | 0.0072 |
| E6 − L4 − L5 (no forecast) | 0.782 | 0.090 | 0.195 | 0.218 | 0.203 | 0.0068 |

Consistent with F3/F4: on this data the forecast adds no detection; removing it moves a few rows between REVIEW and
REJECT. Remaining leave-one-out variants (−L2 level, −L2 drift, −R4): TBD — experiment not yet executed.

## 3. Result table — v1 (recorded runs)

Data category: **synthetic** (development v1, DS-04) · Checkpoint: T24 · Label:
`label_safety_slope`, Δ_allow = 0.15 relative (ADR-002/004) · REVIEW counted as flagged.
Final test lots, evaluated once with frozen specs: `artifacts/metrics/E1-E6_test/20260926-144448_c8ca99b` (from development run
`artifacts/metrics/E1-E6_validation/20260926-144425_c8ca99b`, commit `c8ca99b`). Positives: **30** (test) — rates are imprecise.
Run directories are git-ignored; regenerate with `python scripts/run_experiments.py`
then `--final <dev run>` at the same commit.

| Step | Recall | Precision | FPR | PR-AUC | Escape rate | Review rate | False rejection | Auto-cleared | Recall vs scenario truth |
|---|---|---|---|---|---|---|---|---|---|
| 1 Static (E1) | 0.133 | 0.125 | 0.012 | 0.147 | 0.867 | 0.012 | 0.000 | 0.986 | 0.055 |
| 2 + Lot level (E2) | 0.133 | 0.085 | 0.018 | 0.168 | 0.867 | 0.019 | 0.000 | 0.980 | 0.127 |
| 3 + Lot drift (E3) | 0.667 | 0.213 | 0.032 | 0.296 | 0.333 | 0.035 | 0.003 | 0.960 | 0.309 |
| 4 + 168h pred. (E4) | 0.667 | 0.213 | 0.032 | — | 0.333 | 0.033 | 0.003 | 0.960 | 0.309 |
| 5 + Interval (E5) | 0.667 | 0.213 | 0.032 | — | 0.333 | 0.034 | 0.003 | 0.960 | 0.309 |
| 6 Full rules (E6) | 0.800 | 0.092 | 0.101 | — | 0.200 | 0.104 | 0.003 | 0.890 | 0.527 |

Module B prediction (E4, validation MAE; units differ so never pooled): population
increment chosen for both parameters — iddq 0.297 µA vs persistence 0.338 µA; tpd
0.0472 ns vs 0.0496 ns. Interval coverage (target 0.90): validation 0.886 (per lot
0.668–0.980), test 0.887. MAE on the hidden SIH data: TBD — cannot be measured.

## 4. Decision rule for keeping a layer

Keep layer L if, on held-out lots, adding it improves the primary trade-off
(escape rate at a fixed review-rate budget, or review rate at a fixed escape
target) beyond the bootstrap uncertainty, **or** it is required for safety (L0)
or explainability (L7). Otherwise remove it and record the decision in an ADR.

## 5. Findings v1 (synthetic data only — not evidence about ISRO hardware)

| # | Finding | Evidence |
|---|---|---|
| F1 | Lot-relative **drift** scoring (E3) gives the largest gain: recall 0.133 → 0.667 at FPR 0.032 (test) | Table above |
| F2 | Lot-relative **level** at the AEC-Q001 threshold (E2) adds nothing on the drift-based primary label but raises scenario-truth recall 0.055 → 0.127: it catches stable lot outliers (Module A), which the primary label cannot see (ADR-004 note) | E2 row, both label views |
| F3 | The 168 h predictor beats persistence on MAE and tail MAE, but its early-reject rule caught nothing E3 missed (E4 = E3) | E4 row; dev summary |
| F4 | Interval coverage is near target overall but varies by lot (0.668–0.980 on validation), as expected when lots break exchangeability (S-11); it did not change detection (E5 = E4) | E5 row; dev metrics |
| F5 | R* = 0.95 was **not reached** (validation 0.782 at 20 % review; test 0.800 at 10.4 % review). All 6 test escapes are late-developing shapes (sigmoid ×3, sudden shift, accelerating, slow linear) — invisible at 24 h by design | Test decisions |
| F6 | All 6 test false REJECTs are healthy rows with a single 24 h glitch: with two points a spike looks like a real jump (rules R2/R4 fire) | Test decisions |
| F7 | On validation, E1 recall (0.473) was mostly quality-gate REVIEWs of a small and a quantised lot; recall on rows not gated was 0.094 | Dev summary, "not gated" column |

Recommendations (**pending team decision**, not applied):
1. Keep L4 for the Module B output (MAE is an official metric) but claim no detection gain from it.
2. Keep L5 as reported uncertainty in explanations only; claim no detection gain.
3. Consider making R2/R4 REVIEW instead of REJECT at T24 (glitch-driven false rejections, F6).
4. The v1 test split has now been used; any rule change needs a **new pre-registered
   config and fresh evaluation data** (new generator seed), never re-use of these test lots.

