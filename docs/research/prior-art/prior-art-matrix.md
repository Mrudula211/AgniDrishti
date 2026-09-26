# Prior-Art Matrix

Status: Draft · Last updated: 2026-09-26

Source IDs and verification levels: [literature-review.md](literature-review.md).
Rows were searched adversarially (looking for work that already does what we
propose). "—" = not applicable; "Not reported" = not in the part we read.

| Source | Year | Domain | Data | Inputs | Temporal structure | Lot-aware? | Anomaly detection? | Prediction? | Uncertainty? | Decision / review? | Explainability? | Key limitation (vs PS) | Overlap with AgniDrishti | Possible differentiation | Citation status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S-01 AEC-Q001 Rev-D (DPAT) | 2011 | Automotive IC test | Production test data | One test value per part | Single insertion | **Yes** (current lot/wafer) | Yes (outside median ± 6·IQR/1.35) | No | No | Reject outliers | Transparent limits | No drift, no burn-in, no prediction | Module A level scoring | Apply to drift between checkpoints (but see S-06) | V-FULL, citable |
| S-02/S-03 ESCC 9000 / 9202/045 | 2018 / 2020 | Space ICs | Burn-in measurements | Parameter at 0h and end of burn-in | 2 points, measured | Lot fail if > 5 % fail (PDA) | Drift > Δ ⇒ failure | No | No | Reject / lot reject | Transparent limits | Measured end drift only; no early prediction; no peer comparison | Drift-from-0h rule; ESCC-style Δ is our SS-G candidate | **Predict** the end drift at 24h | V-FULL, citable |
| S-06 US 8,010,310 (AMD) | 2011 | CPU burn-in | Pre-/post-BI tester data | Per-device parameters (e.g. static IDD) | Pre vs post | Not reported | **Yes** (outlier from pre/post comparison) | No | No | Second acceptance criteria | Not reported | After burn-in only | Comparing burn-in change per device to find outliers | Early (24h) prediction; interval; review | V-ABS, citable as patent |
| S-07 US 6,230,293 (Lucent) | 2001 | IC test | ΔIddq | Iddq at two voltages | Not temporal | Distribution of sample | Yes | Predicts post-BI failures (screen) | No | Screen | — | Not burn-in trajectories | Delta-outlier idea | — | V-ABS |
| S-04 Ahmed et al., C&IE | 2025 | Semiconductor burn-in planning | Synthetic + real production | Production/test time series (PAA, PCA) | Pre-burn-in | Batch-level quality | No (quality estimation) | Yes (batch quality) | **Yes** (probabilistic SVR, Clopper-Pearson) | Burn-in planning | Not reported | Batch before burn-in, not per component during burn-in | ML + uncertainty for burn-in decisions | Per-component, in-burn-in, sparse checkpoints | V-ABS |
| S-05 Langenberg et al., ESREL | 2023 | Semiconductor burn-in | Real APC process meta/logistics data | Process data, not sensor data | Process history | **Yes** (lot health factor) | Via LSTM-AE loss | Early-failure correlation | Not reported | Reduce BI time/sample | Not reported | No parametric burn-in data | Lot-level health | Uses burn-in parametric trajectories | V-ABS |
| S-09 Aydinkarahaliloglu et al., Sci. Rep. | 2022 | QCL burn-in | 9 lasers, dense | 28 LIV features | Dense (every minute) | No | Classification | Early failure | No | No | No | n = 9; dense data | Early failure from in-burn-in data | Sparse checkpoints; lots; intervals | V-FULL |
| S-10/S-11 Conformal (incl. hierarchical) | 2018 / 2023 | Statistics | — | Any regressor | — | S-11: groups | — | Wraps predictor | **Yes**, marginal | — | Interval | General method | Our L5 | PS-specific application only | V-BIB / V-ABS |
| S-13/S-14 Reject option / three-way | 1970 / 2010 | Decision theory | — | Scores | — | — | — | — | Uses confidence | **Yes** | Rule-based | General | REVIEW state | Application only | V-BIB |
| S-15 Lu & Meeker | 1993 | Reliability | Degradation paths | Repeated measures | Few per unit | Random effects (not lots) | No | Time-to-failure | Yes (model-based) | No | Model | Needs a path model | E4b option | — | V-BIB |
| NASA MOSFET / IGBT data + studies | 2009–2011 | Power device ageing | Lab overstress | Dense electrical signals | Dense, hours | No | No | Prognostics (reported) | GP (reported, not verified) | No | — | Not burn-in, no lots | R-04 methodology only | — | Dataset verified |
| **AgniDrishti (proposed)** | — | PS 26170 | **No official data** | Value_0h, Value_24h (+ lot) | Sparse checkpoints | Level + drift | Proposed | 0h+24h → 168h | Proposed (lot-aware interval) | PASS / REVIEW / REJECT (proposed) | Evidence card (proposed) | Unvalidated | — | — | — |

## Reading `[EI]`

1. Every column individually has prior art. Two that we previously treated as
   possible differentiators are **established**: drift-from-0h limits in burn-in
   (S-02/S-03) and per-device burn-in drift outliers (S-06).
2. The remaining candidate differentiation is narrow: **predicting** the
   end-of-burn-in drift from two early sparse checkpoints, judging it against a
   drift allowance with a lot-aware prediction interval, and abstaining to
   REVIEW. Whether that combination is published is **not established by
   available research** (limited search; see literature-review §4).
3. Patent S-06 is listed as active. This is not a legal analysis; it matters
   only in that we must never say "we are the first to compare burn-in drift".
