# Assumptions, Unknowns and Constraints

Status: Draft · Last updated: 2026-09-26

Every assumption here is a working hypothesis, not a fact. Each has an owner
action to confirm or reject it. When one is resolved, record the resolution
and date; do not delete the row.

## 1. Assumptions

| ID | Category | Assumption | Why we need it | How to verify | Status |
|---|---|---|---|---|---|
| A-01 | Temporal | Checkpoints are 0h, 24h, 96h, 168h for every component. | Feature definitions | Official PS / data | Open — R0 gives these only as examples ("intervals like"); Module B needs 0h, 24h, 168h |
| A-02 | Temporal | Checkpoint times are nominal and equal across components (no per-component timestamps). | Slopes use nominal Δt | Data inspection | Open |
| A-03 | Temporal | ~~The mandatory early prediction uses only 0h + 24h (T24).~~ Withdrawn 2026-09-26: Module B inputs are unresolved (R3: 0h+24h; R2: 0h/24h/96h). Both T24 and T96 paths are kept; neither is assumed to be the PS requirement. | Avoid designing around an unconfirmed input set | Official PS — see discrepancy-log DL-01 | **Resolved 2026-09-26 (R0):** Module B inputs are Value_0h and Value_24h. Any T96 model is an extension outside Module B. |
| A-04 | Dataset | A lot identifier exists, and lots are measured together at each checkpoint. | Lot-relative scoring | Data inspection | Open |
| A-05 | Dataset | Each lot has enough components for robust statistics (minimum TBD, set by experiment). | MAD stability | Data inspection + E2 sensitivity | Open |
| A-06 | Labelling | "Failure" labels are **proxies**: violation of the spec limit at 168h, or of the safety slope. True field failure is unobservable. | Defines metrics | Official PS / data | Decided as working proxy 2026-09-26 — ADR-004 (primary `label_safety_slope`) |
| A-07 | Labelling | Most components in a lot are healthy (defects are rare). | Robust statistics assume a majority of normal parts | Data inspection | Open |
| A-08 | Dataset | Parameters are continuous electrical measurements with known units. | Feature maths | Data inspection | Open |
| A-09 | Dataset | Initially one parameter per component; multiple parameters handled later. | Scope control | Official PS / data | Open |
| A-10 | Operational | Output is advisory to QA engineers; final decision is human for REVIEW. | Decision design | Official PS / organisers | Open |
| A-11 | Operational | Early removal from burn-in (REJECT before 168h) is operationally meaningful. | Justifies Module B early reject | Organisers | Open |
| A-12 | Dataset | Upper spec limit is the relevant side (value rising = degradation). | Direction of risk | Official PS / data; support two-sided anyway | Open |
| A-13 | Temporal | Measurement noise is small relative to defect drift. | Separability | Data (repeatability) | Open |
| A-14 | Dataset | Burn-in conditions (temperature, bias) are constant within a lot. | Lot comparability | Data / PS | Open |

## 2. Unknowns (not established by the available research)

| ID | Unknown | Impact |
|---|---|---|
| U-01 | ~~Official PS text~~ **Resolved 2026-09-26 (R0)** | — |
| U-02 | Whether data will be provided by organisers, and when | Dataset strategy |
| U-03 | Schema, units, number of parameters | Data dictionary |
| U-04 | Whether lot / wafer / device-family IDs exist | Module A design |
| U-05 | Lot sizes and number of lots | Statistics, split design, evaluation power |
| U-06 | Label definition and prevalence | Metrics, thresholds |
| U-07 | Safety slope value, units, and which interval it applies to (R0: "calculated", method not given) — candidates in ADR-002 | Module B decision rule |
| U-08 | Spec limits: one-sided / two-sided, per device family? | Absolute check |
| U-09 | Missing checkpoints / retests / dropped parts handling | Data quality gate |
| U-10 | Measurement resolution (quantisation → MAD = 0 risk) | Robust z stability |
| U-11 | Evaluation by organisers — partly resolved by R0 (hidden ground truth; MAE on Value_168h; Anomaly Detection Score formula unknown) | Optimisation target |
| U-12 | Required deliverable format (demo, report, API) | Scope |
| U-13 | Acceptable review rate for QA | Operating point |
| U-14 | Burn-in temperature and bias conditions | Context only |
| U-15 | Whether historical lots are available for device-family baselines | Cross-lot checks |
| U-16 | Whether 168h itself is a decision point to be screened (Module A at 168h) | Scope of Module A |

## 3. Constraints

| ID | Constraint | Source |
|---|---|---|
| K-01 | Very few time points per component (R0 examples: 4; Module B uses 2). | R0 |
| K-02 | Defects are rare → class imbalance. | R2 (implicit), `[EI]` |
| K-03 | False negatives weigh far more than false positives. | R0 |
| K-04 | Explainability is required. | R0 |
| K-05 | No official dataset currently available. | R0 (verified) |
| K-06 | Hackathon timeline and team capacity. | Project |
| K-07 | No fabricated results, data or claims. | CLAUDE.md |
| K-08 | Early prediction may use only information available at the checkpoint. | Leakage rule |

## 4. Risks caused by missing information

Moved (2026-09-26) to the single risk register:
[../drawbacks-and-risks.md](../drawbacks-and-risks.md) (Part A: PS gaps GAP-01…10; Part B: drawbacks D-01…D-25).
