# Idea-Round Submission Content (SIH 2026, PS 26170)

Status: Draft for team review · Last updated: 2026-09-26 · Deadline: **30 Sep 2026**

Source text for the portal fields and the 6-slide official template (S-17).
Rules applied: no performance numbers (no experiment has run); proposals
labelled; originality wording per [novelty-boundaries.md](../research/prior-art/novelty-boundaries.md);
the only numbers are the PS's own 10 / 45 / 50 µA illustration and cited
formulas. Fill `[…]` placeholders before export.

---

## Portal fields

**Idea title**

AgniDrishti — Lot-relative, drift-predictive and uncertainty-aware burn-in screening

**Idea description**

Static pass/fail limits let latent defects escape: a part can sit inside its
datasheet limit while being abnormal for its lot or drifting abnormally.
AgniDrishti is a proposed screening pipeline for burn-in parametric data. For
each lot at each checkpoint it (1) checks data quality, (2) applies the
datasheet limit, (3) scores every part against its own lot on both level and
drift using robust statistics (Module A), (4) predicts Value_168h from
Value_0h and Value_24h (Module B), (5) compares the predicted drift rate with
a safety slope derived from a per-parameter drift allowance, (6) attaches a
prediction interval calibrated on held-out lots, and (7) returns PASS /
REVIEW / REJECT with the exact numbers and rule behind each decision.
Uncertain or suspicious parts go to engineer REVIEW instead of being passed.
Methods are deliberately simple and transparent because each part has only a
few measurements; complex models are added only if they beat simple baselines
on held-out lots. Evaluation uses lot-grouped splits, leakage tests and an
ablation study on clearly labelled synthetic and public NASA data.

---

## Slide 1 — Title page

- Problem Statement ID – 26170
- Problem Statement Title – AI-Driven Anomaly Detection in Component Burn-In & Screening
- Theme – Smart Automation
- PS Category – Software
- Team ID – [TEAM ID]
- Team Name – [TEAM NAME]

## Slide 2 — Idea title / Proposed solution

**AgniDrishti: from static pass/fail to lot-relative, drift-predictive screening**

Problem (PS example): lot average 10 µA · part at 45 µA · datasheet max 50 µA → static test says PASS.

Proposed solution, per lot, per checkpoint:
- **Data-quality gate** — missing / invalid data → REVIEW, never PASS
- **Datasheet limit** — the conventional check, kept as baseline
- **Module A: lot-relative score** — how far a part's value *and* its 0→24h drift are from its lot (robust statistics)
- **Module B: 168h prediction** — Value_0h + Value_24h → predicted Value_168h
- **Early-rejection rule** — predicted drift rate vs a calculated safety slope
- **Prediction interval** — how uncertain the 168h prediction is
- **Decision** — PASS / REVIEW / REJECT + a quantitative explanation for the QA inspector

How it addresses the PS:
- Module A and Module B implemented as specified
- False negatives: doubt goes to REVIEW; a binary flag counts REVIEW as flagged
- Explainability: every decision shows its values, lot statistics, prediction, interval and the rule that fired

Innovation and uniqueness (proposed integration):
- Builds on proven screening practice — lot-relative limits (AEC-Q001 Dynamic PAT) and burn-in drift limits (ESCC 9000)
- Adds what they lack: **predicting end-of-burn-in drift at 24h**, judged against a drift allowance and the lot, with a **lot-aware prediction interval** and a **REVIEW** path
- Transparent by design: explanations are the actual decision evidence, not a post-hoc attribution

## Slide 3 — Technical approach

Technologies (proposed): Python 3.11 · NumPy · pandas · pytest · version-controlled YAML configs · lightweight demo UI (chosen later) · runs offline, batch per lot.

Methodology (flow chart):

```
Lot data at 24h → Quality gate → Datasheet limit → Lot score (level + drift)
   → Predict Value_168h → Drift rate vs safety slope → Prediction interval
   → Rules → PASS / REVIEW / REJECT → Evidence card
```

Key definitions (our documented choices where the PS is silent):
- Lot score: robust z = (x − lot median) / robust spread; baseline = AEC-Q001 Dynamic PAT (median ± 6·IQR/1.35); MAD variant compared
- Drift rate: r = (Ŷ₁₆₈ − V₀) / 168 h
- Safety slope: s = Δ_allow / 168 h (per-parameter drift allowance, ESCC-style) + datasheet-limit backstop; Δ is configurable and its effect is tested
- 168h predictor, simplest first: persistence → linear extrapolation → lot-median increment → linear regression; advanced models only if they beat these on held-out lots
- Uncertainty: split conformal prediction interval, calibrated on held-out lots, coverage reported per lot

Validation plan:
- Splits by lot; untouched final test lots; automated leakage tests (no 96h/168h value used at 24h)
- 6-step ablation: static → + lot → + drift → + 168h prediction → + uncertainty → full rules; a layer that adds nothing is removed
- Data: synthetic PS-shaped data (held-out scenario families, parameter sweeps) + public NASA ageing data for prediction methodology — always labelled, never presented as ISRO data
- Why not LSTM/Transformer: 2–4 measurements per part — too few for sequence models, and harder to explain

## Slide 4 — Feasibility and viability

Feasibility:
- Light statistical methods; no GPU; designed to run offline on site
- Every threshold in configuration; every decision reproducible and auditable
- Development path: data validation → baseline → lot score → prediction → uncertainty → decisions → explanations

| Challenge / risk | Strategy |
|---|---|
| No official dataset (hidden ground truth) | Synthetic PS-shaped data with held-out scenarios + NASA public data; ready to re-run on official data |
| Safety slope / Anomaly Score not defined in PS | Documented, configurable definitions; sensitivity analysis; clarification sought from organisers |
| Only 2 measurements at 24h | Simple, stable predictors; honest prediction intervals; REVIEW when unsure |
| Small, contaminated or mixed lots | Quality checks → REVIEW; drift allowance that does not depend on the lot |
| A whole lot degrading | Absolute drift allowance + datasheet backstop, not only lot comparison |
| Data leakage / optimistic results | Lot-grouped splits, frozen test lots, automated leakage tests |
| Too many REVIEWs | Report the full catch-rate vs review-rate trade-off; operating point chosen with users |

## Slide 5 — Impact and benefits

Target users: component screening / QA engineers and reliability engineers for space-grade electronics.

Intended benefits (to be quantified by our experiments):
- Fewer latent defects escaping into flight hardware
- Early visibility at 24h of parts heading for excessive drift
- Consistent, explainable, auditable decisions a QA inspector can verify
- Engineers focus on the REVIEW queue instead of all parts
- Better use of burn-in capacity and fewer late-stage failures and rework (economic)
- Runs on-premises; no data leaves the facility

Future progression: calibration on real ISRO burn-in data · multiple parameters per part · cross-lot history · integration with test-equipment data logs.

## Slide 6 — Research and references

- SIH 2026 PS 26170 (official text), sih.gov.in/sih2026PS
- AEC-Q001 Rev-D, Guidelines for Part Average Testing, AEC, 2011
- ESCC Generic Specification 9000, Issue 10, ESA, 2018; ESCC Detail Spec. 9202/045, Issue 6, 2020
- I. Ahmed et al., "A data-driven modelling framework for predicting the quality of semiconductor devices to support burn-in decisions", Comput. Ind. Eng. 204, 111115, 2025
- L. Langenberg et al., "Process Data Analysis for Improved Burn-In Strategies Based on Complementary AI Models", ESREL 2023
- US 8,010,310 B2, "Method and apparatus for identifying outliers following burn-in testing", 2011
- J. Lei et al., "Distribution-Free Predictive Inference for Regression", JASA 113, 2018
- R. Dunn, L. Wasserman, A. Ramdas, "Distribution-Free Prediction Sets for Two-Layer Hierarchical Models", JASA 118, 2023
- C. K. Chow, "On optimum recognition error and reject tradeoff", IEEE Trans. Inf. Theory 16, 1970
- C. J. Lu, W. O. Meeker, "Using Degradation Measures to Estimate a Time-to-Failure Distribution", Technometrics 35, 1993
- NASA PCoE: MOSFET Thermal Overstress Aging (Celaya et al.); IGBT Accelerated Aging (Celaya, Wysocki, Goebel, 2009)

---

## Integrity check (done 2026-09-26)

- [x] No performance number, percentage improvement or dataset size
- [x] No "first / novel / compliant / physics-informed / guaranteed / zero FN"
- [x] Module B = Value_0h + Value_24h → Value_168h (R0)
- [x] Safety slope / drift rate stated as our choice (ADR-002)
- [x] Data categories named; NASA not presented as ISRO data
- [x] All references verified (literature-review S-xx), none UV
