# Decision Engine (Provisional)

Status: Proposed · Last updated: 2026-09-26

Layer L6: ordered decision rules and PASS / REVIEW / REJECT (+ binary flag). No fused risk score (ADR-001 Revision 1).

| Item | Content |
|---|---|
| Purpose | Turn evidence from L0–L5 into an operational decision that is biased against escapes and routes uncertainty to humans (PSR-04, PSR-05) |
| Inputs | L0 flags; L1 spec status/margin; L2 z-scores and drift features; L4 prediction; L5 interval; config thresholds |
| Outputs | `decision`, `binary_flag` (FR-16; REVIEW mapping configurable), `fired_rules` (ordered list), `evidence` (dict of the numbers used) |
| Assumptions | A-10 (REVIEW is handled by a human); A-11 (early REJECT is meaningful) |
| Candidate methods | **D1** ordered, documented rule set (below), thresholds chosen on validation lots. ~~D2 fused-score threshold~~ — dropped by ADR-001 Revision 1 |
| Alternatives | Learned classifier producing a "risk probability" — rejected until real labels exist (M-08); weighted CRI / fused score — **rejected as a decision input** (ADR-001 Rev. 1); at most a ranking aid, never a probability |
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

Policy: [ADR-005](../decisions/ADR-005-operating-point.md) (accepted). Thresholds are chosen on **validation lots** to meet a pre-registered target recall R*
(REVIEW counted as flagged), then the resulting review rate is reported. Because acceptable review
rate is unknown (U-13), we always report the full recall–review-rate curve next to the selected point.

## 3. Things the decision engine must never do

- Output PASS when any input is missing or invalid.
- Display a percentage as "probability of failure" unless calibrated on
  held-out real labels.
- Hide which rule fired.
