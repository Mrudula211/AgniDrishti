# Explainability (Provisional)

Status: Proposed · Last updated: 2026-09-26

Layer L7: engineer-readable explanation and audit record (PSR-06).

| Item | Content |
|---|---|
| Purpose | Let a QA engineer verify every decision from the numbers that produced it |
| Inputs | L6 `decision`, `fired_rules`, `evidence`; lot statistics; config version |
| Outputs | Explanation text (templated), evidence table, trajectory map (P6), audit record (JSON) |
| Assumptions | Engineers prefer quantitative, rule-based explanations (R2 P10, `[UV]`) |
| Candidate methods | Deterministic templates filled from evidence; trajectory map |
| Alternatives | SHAP / post-hoc attribution — only if a black-box model survives E4b, and then as a supplement |
| Risks | Explanations drifting from actual logic (if hand-written separately); jargon; implying false certainty |
| Validation | Unit tests: every rule has a template; every number in text equals the evidence value; qualitative review by team |
| Expected evidence | Example explanations generated from real runs for each decision type |

## 1. Questions every explanation answers

| Question | Evidence field(s) |
|---|---|
| Why was it flagged? | `fired_rules` |
| How abnormal relative to its lot? | `value_t`, lot median, lot robust scale, `z_level_t` |
| What happened to its trajectory? | `slope_0_24`, `slope_24_96`, `slope_change`, `z_drift_t` |
| Predicted future state? | `pred_168h`, predicted slope, spec limit, safety slope |
| How uncertain? | `pi_low`, `pi_high`, target coverage |
| Why this decision? | rule text + thresholds from config |

## 2. Template shape (illustrative format — no real values)

```
Component <id> · Lot <lot> · Checkpoint T24 · Decision: REVIEW
Data category: <official|external|synthetic>

- Absolute spec: <value> <unit> vs limit <limit> → within limit
- Lot position: <z_level> robust-z above lot median <median> (scale <scale>)
- Drift 0→24h: <slope>/h, <z_drift> robust-z above lot drift
- Predicted 168h: <pred> <unit>; <coverage>% prediction interval [<low>, <high>]
- Rule fired: R3 — upper end of interval exceeds spec limit
- Config: <config_id> · Model: <model_id>
```

## 3. Trajectory map (P6)

X: checkpoint hours (0, 24, 96, 168). Y: parameter value.
Lot envelope (median ± k·robust scale per checkpoint, k from config), spec limit
line, component observed points (only those available at the checkpoint),
predicted 168h point with interval. Title shows data category.

## 4. Wording rules

- "prediction interval", never "confidence that it fails".
- "robust z", never "sigma probability".
- No anthropomorphism ("the AI thinks").
- Explicitly say when REVIEW is due to missing/invalid data.
