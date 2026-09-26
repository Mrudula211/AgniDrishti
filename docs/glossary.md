# Glossary and Terminology Rules

Status: Draft · Last updated: 2026-09-26

| Term | Meaning in this project | Do not confuse with |
|---|---|---|
| Burn-in | Stress applied to every component to precipitate early-life failures, with measurements at checkpoints | Life test / HTOL (sample-based qualification) |
| Checkpoint (T0, T24, T96, T168) | Nominal measurement time in hours | — |
| Decision checkpoint | Time at which the pipeline runs using only data measured so far | — |
| Latent defect (proxy) | A component whose early behaviour indicates progression toward a spec or safety-slope violation. In our data, always defined by a proxy label | Confirmed field failure (unobservable here) |
| Lot | Set of components manufactured together and measured together | Device family |
| Robust z-score | (x − median) / (1.4826 · MAD) within a reference group. A distance in robust-σ units | A probability; a p-value |
| MAD | Median absolute deviation from the median | Mean absolute deviation |
| DPAT-style | Lot-relative limits inspired by Dynamic Part Average Testing. AEC-Q001 Rev-D (S-01) defines Dynamic PAT limits as median ± 6·(IQR/1.35) of the current lot | "AEC-Q001 compliant" |
| Drift / slope | Change in value per hour between checkpoints | Raw difference |
| Drift rate (Module B) | "Predicted 168h drift rate" (R0). Formula not given by the PS; **our definition** (ADR-002): (Ŷ₁₆₈ − V₀)/168 h, in parameter units per hour | A PS-defined formula |
| Safety slope | Threshold on the predicted drift rate that triggers early rejection. The PS says "calculated" but gives no method; **our definition** (ADR-002): Δ_allow/168 h from a per-parameter drift allowance, plus a datasheet-limit backstop | Spec limit; a PS-given constant |
| Drift allowance (Δ) | Maximum permitted change from the 0h value during burn-in, per parameter, as used in ESCC specifications (S-02/S-03) | Spec limit |
| Point prediction | Single estimate of `value_168h` | — |
| Prediction interval (PI) | Interval intended to contain a **new observation** (the true `value_168h`) with a target frequency across components | Confidence interval |
| Confidence interval | Interval for an unknown **parameter** (e.g. a mean or a metric) | Prediction interval |
| Coverage | Fraction of cases where the true value falls inside the PI. Conformal methods target **marginal** coverage under exchangeability | Per-component certainty |
| Calibrated probability | A score whose stated value matches observed frequency on held-out data | Any number between 0 and 1 |
| Risk score | Ordering quantity for triage. Not a probability unless calibrated | Probability of failure |
| Recall | TP / (TP + FN) | Accuracy |
| False-negative rate | FN / (TP + FN) = 1 − recall | False-positive rate |
| Defect escape rate | Positives decided PASS / all positives | FNR (differs when REVIEW exists) |
| Review rate | Fraction of components sent to REVIEW | — |
| Leakage | Any use of information not available at decision time, or of test data during fitting | — |
| Data category | official / external / synthetic | — |

## Forbidden phrasings

| Do not write | Write instead |
|---|---|
| "95% probability it will fail" | "The 95% prediction interval's upper end exceeds the limit" |
| "95% confidence bounds" (for conformal output) | "95% prediction interval" |
| "3σ event, so 99.7% abnormal" | "3.0 robust-z above the lot median" |
| "Zero false negatives" | "No escapes observed among N positives on dataset X (category Y)" — only if measured |
| "Guaranteed coverage" | "Target marginal coverage of 1 − α, empirically X on held-out lots" |
