# Decision Engine (Provisional)

Status: Proposed · Last updated: 2026-09-26

Layer L6: risk fusion and PASS / REVIEW / REJECT.

| Item | Content |
|---|---|
| Purpose | Turn evidence from L0–L5 into an operational decision that is biased against escapes and routes uncertainty to humans (PSR-04, PSR-05) |
| Inputs | L0 flags; L1 spec status/margin; L2 z-scores; L3 features; L4 prediction; L5 interval; config thresholds |
| Outputs | `decision`, `fired_rules` (ordered list), `evidence` (dict of the numbers used) |
| Assumptions | A-10 (REVIEW is handled by a human); A-11 (early REJECT is meaningful) |
| Candidate methods | **D1** ordered, documented rule set (below). **D2 (conditional)** cost-sensitive threshold on a single fused score, thresholds chosen on validation lots |
| Alternatives | Learned classifier producing a "risk probability" — rejected until real labels exist (M-08); weighted CRI sum — only as a ranking aid, not as a probability |
| Risks | Thresholds tuned to synthetic generator; review flood; rule interactions hard to reason about |
| Validation | Unit test for every rule and for rule order; E6 recall-vs-review-rate curve on held-out lots |
| Expected evidence | Escape rate and review rate at chosen operating point vs E5. TBD — experiment not yet executed |

## 1. Provisional rule set (D1)

Evaluated in order; the first matching group determines the decision, but **all**
matching rules are recorded as evidence. All thresholds are config values —
none are chosen yet.

| Order | Rule | Decision |
|---|---|---|
| R0 | Blocking data-quality flag (component or lot) | REVIEW |
| R1 | Absolute spec violated at current checkpoint | REJECT |
| R2 | Predicted drift exceeds safety slope **and** lower end of prediction interval also exceeds it | REJECT |
| R3 | Predicted drift exceeds safety slope, **or** upper end of interval exceeds spec / safety slope | REVIEW |

Drift rate and safety slope in R2/R3 follow [ADR-002](../decisions/ADR-002-safety-slope-and-drift-rate.md) §11:
drift = (Ŷ₁₆₈ − V₀)/168 h; slope = Δ_allow/168 h; datasheet-limit crossing of
Ŷ₁₆₈ (or of the interval end) counts as exceeding. Interval ends map through
the same formula.
| R4 | `z_level_t` ≥ `z_level_reject` and `z_drift_t` ≥ `z_drift_reject` (both extreme) | REJECT *(candidate — keep only if E6 supports it)* |
| R5 | `z_level_t` ≥ `z_level_review` or `z_drift_t` ≥ `z_drift_review` | REVIEW |
| R6 | None of the above | PASS |

Notes:

- Order is fixed in config and covered by tests.
- R2 uses the interval so that REJECT requires the evidence to be strong even
  at the optimistic end; R3 uses the pessimistic end so that doubt goes to REVIEW.
- Without L5 (ablation E4), R2/R3 collapse to point-prediction comparisons.

## 2. Operating point

Thresholds are chosen on **validation lots** to meet a target recall (or escape
rate), then the resulting review rate is reported. Because acceptable review
rate is unknown (U-13), we report the full recall–review-rate curve and one or
two operating points, not a single tuned number.

## 3. Things the decision engine must never do

- Output PASS when any input is missing or invalid.
- Display a percentage as "probability of failure" unless calibrated on
  held-out real labels.
- Hide which rule fired.
