# Discrepancy Log

Status: Draft · Last updated: 2026-09-26

Contradictions between the research sources about PS 26170. None may be
resolved by team or assistant judgement — only by the authoritative evidence
named in each entry.

**Update 2026-09-26:** the official PS text was obtained from the SIH portal
(source `R0`, [official-ps-26170.md](official-ps-26170.md)). Entries were
resolved **only** where R0 states the answer; where R0 is silent the entry is
marked "NOT SPECIFIED IN OFFICIAL PS TEXT". See §Resolutions at the end.
The per-entry "Current status" rows in §A–§H are the **pre-verification record**
and are kept unchanged as history; the Summary table below is authoritative.

Sources: `R0` official PS text (SIH portal) · `R1` Comprehensive Guide to Deep
Web Research.pdf · `R2` Deep Research Report.pdf · `R3`
SIH_26170_Comprehensive_Research_Report.pdf · `R4` research assessment pasted
into chat (2026-09-26). See [../claim-register.md](../claim-register.md).

R1 contains no PS 26170 content and therefore appears in no entry.

## Status values

| Status | Meaning |
|---|---|
| **BLOCKED — REQUIRES OFFICIAL PS TEXT** | The disagreement is about what PS 26170 says or requires. Only the official PS text (or an official PS attachment/dataset) can resolve it. |
| **UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS)** | The disagreement is about an external fact (a standard, a statistical property, prior art). The official PS text would not settle it; the named primary source would. |
| **RESOLVED (R0)** | The official PS text states the answer; quote recorded in §Resolutions. |
| **PARTIALLY RESOLVED (R0)** | R0 settles part of the question; the remainder is not specified by R0. |
| **NOT SPECIFIED IN OFFICIAL PS TEXT** | R0 is silent. No longer blocked on the PS text; it is an open design decision that must be made explicitly, documented as **our** choice (never as a PS requirement), and — where it affects scoring — ideally confirmed with organisers. |

## Summary

| ID | Topic | Status |
|---|---|---|
| DL-01 | Module B input checkpoints (0h+24h vs 0h/24h/96h) | **RESOLVED (R0)** — 0h + 24h |
| DL-02 | Decision time for early action (24h vs 96h) | **PARTIALLY RESOLVED (R0)** |
| DL-03 | Measurement checkpoints available in the data | **PARTIALLY RESOLVED (R0)** |
| DL-04 | Measured parameter(s) | **RESOLVED (R0)** — examples only |
| DL-05 | Burn-in stress conditions (125 °C) | **RESOLVED (R0)** — example only |
| DL-06 | Prediction target (168h value vs 168h drift rate) | **RESOLVED (R0)** |
| DL-07 | Early-reject criterion (safety slope vs limit crossing vs acceleration) | **RESOLVED (R0)** — safety slope |
| DL-08 | Definition and value of the safety / degradation slope | **NOT SPECIFIED IN OFFICIAL PS TEXT** |
| DL-09 | Reference population for "lot-relative" | **PARTIALLY RESOLVED (R0)** |
| DL-10 | Checkpoint at which Module A operates | **NOT SPECIFIED IN OFFICIAL PS TEXT** |
| DL-11 | False-negative requirement wording (catastrophic vs zero FN) | **RESOLVED (R0)** — "catastrophic" |
| DL-12 | Evaluation metrics / primary metric | **PARTIALLY RESOLVED (R0)** |
| DL-13 | Existence of an official dataset / hidden test set | **RESOLVED (R0)** — no published dataset; hidden ground truth held by evaluators |
| DL-14 | Dataset schema (fields) | **PARTIALLY RESOLVED (R0)** |
| DL-15 | Failure labels | **NOT SPECIFIED IN OFFICIAL PS TEXT** |
| DL-16 | Illustrative example values in the PS | **RESOLVED (R0)** |
| DL-17 | Scale requirement | **NOT SPECIFIED IN OFFICIAL PS TEXT** |
| DL-18 | Required output form (binary vs three-way) | **PARTIALLY RESOLVED (R0)** |
| DL-19 | AEC-Q001 compliance / MAD as the AEC-Q001 statistic | UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS) |
| DL-20 | Burn-in equated with HTOL (JESD22-A108) | UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS) |
| DL-21 | ISO 9001 / AS9100 traceability claim | UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS) |
| DL-22 | Novelty of the proposed combination | UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS) |
| DL-23 | Meaning of uncertainty output (probability vs prediction interval) | UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS) |
| DL-24 | Conformal coverage guarantee under sparse / lot-shifted data | UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS) |
| DL-25 | Risk index as calibrated probability | UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS) |

---

## A. Module B inputs and timing

### DL-01 — Module B input checkpoints

| Field | Content |
|---|---|
| Claim A | Module B predicts `Value_168h` **from `Value_0h` and `Value_24h`**. |
| Source A | R3 §1 ("early prediction of Value_168h from Value_0h and Value_24h"). |
| Claim B | Early prediction uses **0h, 24h and 96h**: "From 3 early points (0, 24, 96), we can extract … velocity … acceleration"; velocity defined as (X₉₆ₕ − X₂₄ₕ)/(96 − 24); architecture input "Data (0h, 24h, 96h)"; trajectory map shows actual path 0–96h. |
| Source B | R2 Part 4, Part 18, Part 35 E and F.2. |
| Also | R4 traceability table lists "0h/24h information → trajectory features" and "168h prediction" without stating whether 96h is an input. |
| Why it matters | Determines which features are legal at the prediction time (leakage boundary), whether curvature/acceleration can be used at all, the identifiability of any curve fit, and how much burn-in time an early decision saves. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Existing lean in repo docs (not a resolution) | claim-register C-01, assumption A-03 and FR-07 priority "M (T24)" were written treating 0h+24h as the mandatory minimum. These are provisional wording only and are re-pointed to this entry. The architecture keeps both T24 and T96 paths so that neither is removed before resolution. |
| Authoritative evidence required | Official PS 26170 text (Module B description), or an official dataset / sample file whose documented inputs define it. |
| Implementation consequence | Feature availability matrix, leakage tests, E4 design, the safety-slope rule, and presentation slide 7 all depend on this. No Module B code may assume either answer until resolved. |

### DL-02 — Decision time for early action

| Field | Content |
|---|---|
| Claim A | Early prediction / rejection happens after **24h** (inputs 0h + 24h). |
| Source A | R3 §1. |
| Claim B | Component is flagged "on **Day 4**" (≈ 96h) and early reject "saves **72 hours**" (168 − 96). |
| Source B | R2 Part 19 step 5, Part 30 (pitch 90–130 s). |
| Why it matters | Defines when the pipeline runs, what "early" means, and any claim about burn-in time saved. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text stating when early rejection is expected. |
| Implementation consequence | Decision checkpoint configuration; any "hours saved" metric (claim X-05) must not be reported until resolved. |

## B. Expected measurements

### DL-03 — Measurement checkpoints available in the data

| Field | Content |
|---|---|
| Claim A | Data is measured at **0h, 24h, 96h, 168h**. |
| Source A | R2 Part 1, Part 4; R3 §9 and R4 §10 list `Value_96h` in the proposed (synthetic) schema. |
| Claim B | R3 §1's description of the PS mentions only `Value_0h`, `Value_24h`, `Value_168h`; whether 96h is part of the PS data is not stated there. |
| Source B | R3 §1. |
| Why it matters | If 96h is absent from official data, the T96 path, slope-change features and R2's velocity definition cannot exist. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text or official data file listing the checkpoints. |
| Implementation consequence | Canonical schema (`value_96h` currently "Required*"), synthetic generator design, data-quality checks for missing checkpoints. |

### DL-04 — Measured parameter(s)

| Field | Content |
|---|---|
| Claim A | The parameter is **IDDQ / quiescent supply current / leakage current** in µA (fields `Iddq_0h … Iddq_168h`). |
| Source A | R2 Part 1, Part 5, Part 18 (Y-axis "Leakage Current"), Part 35 H. |
| Claim B | A generic parameter `Value_*`, no parameter named. |
| Source B | R3 §1, §9. |
| Why it matters | Parameter physics (direction of degradation, one- vs two-sided limit, noise, units) and whether multiple parameters per component exist. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text or official data dictionary. |
| Implementation consequence | Assumptions A-08, A-09, A-12; spec check direction; units in all outputs. |

### DL-05 — Burn-in stress conditions

| Field | Content |
|---|---|
| Claim A | Burn-in / ESS at **125 °C**. |
| Source A | R2 Part 1. |
| Claim B | No temperature stated; `Temperature` appears only as a proposed field. |
| Source B | R3 §9; R4 §10. |
| Why it matters | Context for degradation assumptions; relevance of Arrhenius (claim D-08); whether temperature varies between lots. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text or dataset metadata. |
| Implementation consequence | Whether `temperature_c` is a schema field or a constant; synthetic generator assumptions. |

## C. Prediction target

### DL-06 — Prediction target

| Field | Content |
|---|---|
| Claim A | Target is the **168h value** (`Value_168h`). |
| Source A | R3 §1; R2 Part 15 Layer 3 ("predicting the 168h value"); R2 Part 35 G. |
| Claim B | Module B predicts "**168h drift rates**". |
| Source B | R2 Part 1 (explicit requirements). |
| Also | R2 Part 6 proposes a "Remaining Useful Life" / "Probability of Survival" index — a third, different target. |
| Why it matters | Regression target, error metrics (value vs rate units) and how the safety slope is compared. R2 is internally inconsistent. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text for Module B output. |
| Implementation consequence | L4 output definition, E4 metrics, FR-07/FR-09 wording. |

## D. Safety / degradation slope

### DL-07 — Early-reject criterion

| Field | Content |
|---|---|
| Claim A | Early rejection when **predicted drift exceeds a safety slope**. |
| Source A | R3 §1. |
| Claim B | Risk is HIGH / REVIEW when the **upper prediction bound crosses the absolute safety threshold (spec limit)**; REJECT when "**physics-based drift acceleration** predicts catastrophic violation" (fitted exponent n > 1). |
| Source B | R2 Part 8, Part 9, Part 7. |
| Claim C | "Projected trajectory approaches/exceeds the **safety boundary**." |
| Source C | R4 §6. |
| Why it matters | Three different decision variables (a rate, a level, a curve shape). They produce different rejected sets and different explanations. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text defining the early-rejection condition. |
| Implementation consequence | Decision rules R2/R3 in decision-engine.md are provisional; FR-09; label `label_safety_slope`. |

### DL-08 — Definition and value of the safety slope

| Field | Content |
|---|---|
| Claim A | A "safety slope" exists as a PS parameter. |
| Source A | R3 §1. |
| Claim B | No safety slope mentioned; only the absolute limit (example 50 µA) and acceleration. |
| Source B | R2 (entire report). |
| Unstated in all sources | Numeric value, units (per hour? relative %?), interval over which it applies (0→168h? 0→24h?), whether it is per device family. |
| Why it matters | Without it, the Module B reject rule and its proxy label are undefined. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text or dataset documentation giving the slope definition. |
| Implementation consequence | Unknown U-07; must remain a config parameter with no default value chosen by us. |

## E. Module A scope

### DL-09 — Reference population for "lot-relative"

| Field | Content |
|---|---|
| Claim A | Compare against the **current lot** and also **historical device-family distributions**; DPAT per **wafer or lot**. |
| Source A | R2 Part 2, Part 5. |
| Claim B | "**Population/lot-relative**"; "relevant lot or peer group". |
| Source B | R3 §1, §4. |
| Why it matters | Grouping key for robust statistics; whether historical data is needed. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text and identifiers present in official data. |
| Implementation consequence | Required identifiers (`lot_id`, `wafer_id`, `device_family`); U-04, U-15. |

### DL-10 — Checkpoint at which Module A operates

| Field | Content |
|---|---|
| Claim A | Layer 1 flags **0h** spatial outliers. |
| Source A | R2 Part 15 Layer 1. |
| Claim B | Module A is dynamic, lot-relative detection with no checkpoint restriction; the core example is a component "drifting" relative to its lot (implies multiple checkpoints). |
| Source B | R3 §1. |
| Why it matters | Whether Module A is a static per-checkpoint screen, a drift screen, or both. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text for Module A. |
| Implementation consequence | Scope of L2 and FR-04/FR-05; experiment E2/E3 checkpoints. |

## F. False negatives and evaluation criteria

### DL-11 — False-negative requirement wording

| Field | Content |
|---|---|
| Claim A | "The model must **prioritize zero false negatives**." |
| Source A | R2 Part 1. |
| Claim B | "The PS explicitly treats false negatives as **catastrophic**"; thresholds should reflect asymmetric consequences and preserve human review. |
| Source B | R3 §11; R4 §9 warns against claiming zero FN. |
| Why it matters | "Zero FN" as a target vs "catastrophic cost" as a weighting lead to different operating points and different claims. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS wording on false negatives. |
| Implementation consequence | Operating-point selection in E6; presentation wording (claim X-01/X-02 already barred). |

### DL-12 — Evaluation metrics / primary metric

| Field | Content |
|---|---|
| Claim A | Primary metric **Recall at fixed 5% FPR**; **ECE** and **prediction-interval coverage**; "do not evaluate purely on F1"; optimising accuracy or F1 "will fail". |
| Source A | R2 Part 1, Part 22, Part 35 J&K. |
| Claim B | Recall, precision, **F1**, PR-AUC, FNR; MAE, RMSE; interval coverage/calibration; defect escape rate, false rejection rate, review rate, % automatically cleared. |
| Source B | R3 §11; R4 §12. |
| Claim C | SIH-level judging factors: novelty, complexity, clarity, feasibility, practicability, sustainability, impact, UX, future progression. |
| Source C | R4 §5 (citing historic SIH SPOC guidelines). |
| Why it matters | Whether the PS or organisers define a scoring metric; what the system is optimised and presented against. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** (and official SIH 2026 evaluation guidelines for Claim C) |
| Authoritative evidence required | Official PS text; official SIH 2026 evaluation criteria. |
| Implementation consequence | evaluation-protocol.md reports all metrics until a primary metric is defined by an official source. |

## G. Dataset assumptions

### DL-13 — Existence of an official dataset / hidden test set

| Field | Content |
|---|---|
| Claim A | "The current public PS material … **does not provide an official dataset**." |
| Source A | R3 §8; repeated in R4 §10. |
| Claim B | Refers to "**the hidden test set**" having a different mean (30 µA vs 10 µA) and a demo upload of `burn_in_lot_884.csv` from ATE — implying organiser-held data. |
| Source B | R2 Part 21, Part 19. |
| Why it matters | Determines whether evaluation on official data is possible and whether a hidden test exists to prepare for. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS page / attachments, or official organiser communication. |
| Implementation consequence | Dataset strategy; robustness priorities (distribution shift). |

### DL-14 — Dataset schema

| Field | Content |
|---|---|
| Claim A | `Component_ID, Lot_ID, Wafer_ID, Device_Family, Iddq_0h, Iddq_24h, Iddq_96h, Iddq_168h, Spec_Max` (no spec min, no temperature, no label). |
| Source A | R2 Part 35 H. |
| Claim B | `Component_ID, Lot_ID, Device_Family, Temperature, Value_0h, Value_24h, Value_96h, Value_168h, Spec_Min, Spec_Max, Failure_Label` (no wafer). |
| Source B | R3 §9 (explicitly a proposed synthetic schema). |
| Claim C | `Component_ID, Lot_ID, Wafer_ID, Device_Family, Temperature, Value_0h…Value_168h, Spec_Max, Failure_Label`. |
| Source C | R4 §10. |
| Why it matters | All three are proposals; none is established as the PS schema. Field presence changes Module A grouping, spec check (one- vs two-sided) and supervision. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text or official data file. |
| Implementation consequence | data-dictionary.md remains a provisional target schema. |

### DL-15 — Failure labels

| Field | Content |
|---|---|
| Claim A | A `Failure_Label` field exists. |
| Source A | R3 §9; R4 §10 (both in proposed synthetic schemas). |
| Claim B | No label field; evaluation described via latent-defect detection on synthetic data. |
| Source B | R2 Part 35 H, Part 20. |
| Why it matters | Supervised vs unsupervised framing; definition of positives for every detection metric. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text or official data. |
| Implementation consequence | Assumption A-06 (proxy labels) remains; no label may be fabricated. |

### DL-16 — Illustrative example values attributed to the PS

| Field | Content |
|---|---|
| Claim A | "The problem **explicitly states** that absolute limits (50 µA) are insufficient if the lot average is 10 µA." |
| Source A | R2 Part 5. |
| Claim B | Demo example: lot average **8 µA**, component at **35 µA**, limit 50 µA. |
| Source B | R2 Part 19; repeated in R4 §7. |
| Also | R3 does not quote any PS numeric example. |
| Why it matters | Whether any numbers are PS-given (and usable in synthetic design) or invented illustrations. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text. |
| Implementation consequence | Until resolved, these numbers are illustrative only and cannot parameterise the synthetic generator as "PS values". |

### DL-17 — Scale requirement

| Field | Content |
|---|---|
| Claim A | Must "scale to **thousands** of components"; GP "expensive for **millions** of parts". |
| Source A | R2 Part 1, Part 3. |
| Claim B | No scale stated; scalability listed as a gap needing demonstration. |
| Source B | R3 (silent); R4 §13. |
| Why it matters | Performance NFR targets. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS text. |
| Implementation consequence | NFR-07/NFR-08 targets remain TBD. |

### DL-18 — Required output form

| Field | Content |
|---|---|
| Claim A | Output is **PASS / REVIEW / REJECT** (three-way decision), described as required by the FN constraint ("requires abandoning binary classification"). |
| Source A | R2 Part 9. |
| Claim B | Three-way decision is a **recommended design**, not a PS requirement; PS asks for anomaly detection and early rejection. |
| Source B | R3 §4 (listed under "Proposed differentiation"). |
| Why it matters | Whether REVIEW is a requirement or our design choice — affects traceability and whether a binary output must also be produced. |
| Current status | **BLOCKED — REQUIRES OFFICIAL PS TEXT** |
| Authoritative evidence required | Official PS output requirements. |
| Implementation consequence | FR-10 stays marked PR (proposal); a binary view may be needed. |

## H. Standards, compliance and claim accuracy

### DL-19 — AEC-Q001 compliance / MAD as the AEC-Q001 statistic

| Field | Content |
|---|---|
| Claim A | PAT is "codified in AEC-Q001"; robust Z/MAD is "standard in AEC-Q001"; solution is "Robust MAD (**AEC-Q001 DPAT compliant**)"; architecture "rooted in JEDEC/AEC-Q001 screening physics". |
| Source A | R2 Part 2, Part 3, Part 32, Final Answer. |
| Claim B | Do not claim AEC-Q001 compliance unless demonstrated; say "inspired by / informed by lot-relative screening principles". |
| Source B | R4 §9. R3 does not mention AEC-Q001. |
| Why it matters | A compliance or equivalence claim that is wrong is easily challenged by domain judges. |
| Current status | **UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS)** |
| Authoritative evidence required | AEC-Q001 document text (robust mean/sigma definition, scope). If the PS itself names a standard, the official PS text as well. |
| Implementation consequence | L2 compares MAD- and IQR-based scale; wording "DPAT-style" only. |

### DL-20 — Burn-in equated with HTOL (JESD22-A108)

| Field | Content |
|---|---|
| Claim A | 125 °C burn-in is "High-Temperature Operating Life or HTOL as per JEDEC JESD22-A108". |
| Source A | R2 Part 1. |
| Claim B | No source supports the equivalence; R3/R4 do not cite JEDEC. |
| Source B | R3, R4 (silent). |
| Why it matters | Mis-citing a standard; burn-in screening and life-test qualification differ in purpose. |
| Current status | **UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS)** |
| Authoritative evidence required | JESD22-A108 text; a burn-in standard/reference (e.g. the applicable screening specification named by the PS, if any). |
| Implementation consequence | Documentation wording only. |

### DL-21 — ISO 9001 / AS9100 traceability claim

| Field | Content |
|---|---|
| Claim A | Audit JSON "ensures traceability for ISO 9001/AS9100 compliance". |
| Source A | R2 Part 27. |
| Claim B | No compliance claims without demonstration. |
| Source B | R4 §9 (general principle); R3 §13. |
| Why it matters | Unsupported compliance claim. |
| Current status | **UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS)** |
| Authoritative evidence required | Relevant standard clauses and an actual conformity assessment. |
| Implementation consequence | FR-12 described as "designed to support traceability" only. |

### DL-22 — Novelty of the proposed combination

| Field | Content |
|---|---|
| Claim A | "This specific fusion … is a highly defensible, **novel** engineering implementation." |
| Source A | R2 Part 14. |
| Claim B | Not justified as novel; prior work exists (C&IE 2025, ESREL 2023); call it a proposed framework until a literature and patent search. |
| Source B | R3 §5, §13; R4 §3. |
| Why it matters | Credibility with judges. |
| Current status | **UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS)** |
| Authoritative evidence required | Literature and patent search L-01…L-05. |
| Implementation consequence | novelty-boundaries.md wording applies. |

### DL-23 — Meaning of the uncertainty output

| Field | Content |
|---|---|
| Claim A | "Conformal prediction cone shows a **95% probability of breaching** the 50 µA limit"; "**95% Confidence Bounds**". |
| Source A | R2 Part 19, Part 28, Part 30, Part 32. |
| Claim B | Conformal prediction gives prediction intervals with coverage properties, not a per-component failure probability. |
| Source B | R4 §9. |
| Why it matters | Statistical misstatement. |
| Current status | **UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS)** |
| Authoritative evidence required | Primary conformal-prediction literature (e.g. Vovk et al.; Lei et al. 2018). |
| Implementation consequence | glossary.md wording rules apply to all outputs. |

### DL-24 — Conformal coverage guarantee under sparse / lot-shifted data

| Field | Content |
|---|---|
| Claim A | Conformal gives "mathematically guaranteed coverage intervals **even for small/sparse datasets**"; MAD "naturally immunizes the model against covariate shift". |
| Source A | R2 Part 8, Part 21. |
| Claim B | (No source disputes it directly; R4 speaks of "coverage guarantees".) Repo analysis M-06/M-09 flags the exchangeability condition. |
| Source B | R4 §9; claim-register M-06, M-09. |
| Why it matters | Over-stated guarantees; lot shift may break exchangeability. |
| Current status | **UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS)** |
| Authoritative evidence required | Primary conformal literature on exchangeability and group/covariate shift; empirical E5 coverage per lot. |
| Implementation consequence | E5 reports coverage per lot; no "guaranteed" wording. |

### DL-25 — Risk index as calibrated probability

| Field | Content |
|---|---|
| Claim A | CRI Platt-calibrated on synthetic data "so that a CRI of 0.90 **literally translates to a 90% probability**" of latent failure. |
| Source A | R2 Part 17. |
| Claim B | Present CRI as "a calibrated risk score designed to support risk-based triage" until validated. |
| Source B | R4 §9. |
| Why it matters | Calibration to synthetic labels does not establish real-world probability. |
| Current status | **UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS)** |
| Authoritative evidence required | Held-out calibration measurement on real labelled data. |
| Implementation consequence | No probability output in the decision engine (decision-engine.md §3). |

---

## Resolutions (2026-09-26, evidence: R0)

Format: **Previous claim → New evidence (R0 quote) → Corrected conclusion.**
R0 = [official-ps-26170.md](official-ps-26170.md), retrieved from https://sih.gov.in/sih2026PS on 2026-09-26.

| ID | Previous claim(s) | New evidence (R0, verbatim) | Corrected conclusion | Remaining open |
|---|---|---|---|---|
| DL-01 | R3: 0h+24h. R2: 0h/24h/96h. | "Build a predictive regression model that takes **Value_0h and Value_24h as inputs** and forecasts Value_168h." | **R3 is correct.** Module B inputs are `Value_0h`, `Value_24h`. R2's use of 96h (velocity X₉₆−X₂₄, "Data (0h, 24h, 96h)") does **not** describe Module B. | Any T96 model would be an extension **outside** Module B and must never be reported as Module B. |
| DL-02 | R3: early action after 24h. R2: "Day 4", "saves 72 hours". | Inputs are Value_0h and Value_24h; "the system flags the component for early rejection". No decision time is stated. | R0 fixes the inputs, so a Module B decision can be made once 24h is measured. R2's "Day 4 / 72 hours" is **not** supported by R0. | Exact decision time and whether removal from burn-in is operationally allowed: not specified. Any "hours saved" figure stays barred. |
| DL-03 | R2: data at 0/24/96/168h. R3 §1: only 0/24/168 mentioned. | "measured at intervals **like** 0h, 24h, 96h, and 168h" | All four checkpoints are named, **as examples** ("like"). 96h is mentioned as a measurement interval but is not a Module B input. | Exact checkpoints in evaluator data: not specified. Schema must tolerate other intervals. |
| DL-04 | R2: IDDQ only (µA). R3: generic `Value_*`. | "(e.g., standby current Iddq, leakage currents, or propagation delays" | Parameters are given **as examples**: Iddq, leakage currents, **propagation delays** (not mentioned by R2/R3). Both reports were incomplete. | Number of parameters per component, units, limit direction: not specified. Propagation delay implies non-current units and possibly different drift direction. |
| DL-05 | R2: ESS at 125 °C (as fact). | "operating components at elevated temperatures, **e.g., 125°C** for extended periods" | 125 °C is an **example**, not a stated test condition. R2 over-stated it. | — |
| DL-06 | R3: target Value_168h. R2 P1: "168h drift rates". R2 P6: RUL. | "forecasts **Value_168h**"; "If the **predicted 168h drift rate** exceeds…"; MAE "between the predicted **Value_168h** and the actual hidden ground-truth values" | Regression target is **Value_168h** (scored by MAE). The **drift rate** is derived from the prediction for the rejection rule. RUL / survival index is **not** in the PS. | Formula for "168h drift rate": not specified (see DL-08). |
| DL-07 | R3: safety slope. R2: upper bound crossing spec limit; acceleration n > 1. R4: safety boundary. | "If the predicted 168h drift rate exceeds a calculated safety slope, the system flags the component for early rejection." | Early-rejection criterion is **predicted drift rate vs safety slope** (R3 correct). R2's limit-crossing and acceleration criteria are **our possible additions**, not PS requirements. | — |
| DL-08 | R3: safety slope exists, undefined. R2: none. | "a **calculated** safety slope" — no value, units or method. | The slope is required but **how it is calculated is not specified**. It must be designed and justified by the team and documented as our method. | NOT SPECIFIED — design decision (e.g. derived from datasheet limit and burn-in duration, or from lot statistics); consider asking organisers. |
| DL-09 | R2: current lot + historical device family; wafer. R3: population/lot or peer group. | "Participants need to develop a 'Dynamic' outlier detection system. If a **lot** has an average leakage current of 10µA, a part showing 45 µA is a massive anomaly…" | Reference population named by R0 is the **lot**. Wafer and device-family references are **not** in the PS. R0's example uses the lot **average**; it does not prescribe a statistic. | Definition of "Dynamic"; whether cross-lot history exists: not specified. |
| DL-10 | R2: Module A at 0h. R3: unrestricted. | Module A text gives no checkpoint. Latent defects "exhibit subtle, anomalous **drift over time**". | Not specified. The Background describes drift over time, which supports but does not require multi-checkpoint detection. | NOT SPECIFIED — design decision. |
| DL-11 | R2: "prioritize zero false negatives". R3: "catastrophic". | "a False Negative (missing a defective part) is **catastrophic**, penalizing teams that let bad parts escape." | R3's wording is correct. "Zero false negatives" is **not** a PS requirement. | Size of the penalty: not specified (DL-12). |
| DL-12 | R2: Recall@5%FPR, ECE, PIC; not F1. R3: recall, precision, F1, PR-AUC, FNR, MAE, RMSE, coverage, operational. R4: + SIH judging factors. | Evaluation Metrics: "Anomaly Detection Score" (FN catastrophic); "Drift Prediction Accuracy : The **mean absolute error** between the predicted Value_168h and the actual hidden ground-truth values"; "Explainability". | Official evaluation = (1) Anomaly Detection Score, (2) **MAE** on Value_168h, (3) Explainability. MAE is confirmed (R3). R2's Recall@5%FPR and ECE are **not** PS metrics. | Anomaly Detection Score formula: NOT SPECIFIED. SIH 2026 general judging criteria (R4) not verified in this session. |
| DL-13 | R3/R4: no official dataset. R2: "hidden test set", ATE upload. | Dataset Link field **empty**; "actual **hidden** ground-truth values". | No published official dataset (see [../datasets/official-dataset-verification.md](../datasets/official-dataset-verification.md)). Evaluators hold hidden ground truth. R2's "hidden test set" idea is consistent with R0; its "mean of 30 µA" example is **not** in R0. | Whether/when evaluators release data: unknown. |
| DL-14 | R2 / R3 / R4: three different proposed schemas. | Only `Value_0h`, `Value_24h`, `Value_168h` are named; "lot"; "absolute datasheet maximum limit". | Official schema is **not published**. Named fields: Value_0h, Value_24h, Value_168h. Lot and datasheet max limit are implied. All other fields in R2/R3/R4 are proposals. | Remaining fields: NOT SPECIFIED. |
| DL-15 | R3/R4: Failure_Label. R2: none. | "missing a **defective part**" (evaluation). | Evaluation uses some notion of defective parts; **label format and definition are not specified**. | NOT SPECIFIED. |
| DL-16 | R2 P5: "PS explicitly states 50 µA vs lot average 10 µA". R2 P19 / R4: 8 µA lot, 35 µA part. | "lot has an average leakage current of **10µA**, a part showing **45 µA** is a massive anomaly, even if the absolute datasheet maximum limit is **50 µA**." | Official example is **10 / 45 / 50 µA**. R2 P5 was essentially right (omitted 45 µA). The 8 µA / 35 µA "C-42" demo values are **not** from the PS. | Official numbers are an illustration, not a data specification. |
| DL-17 | R2: thousands/millions. | No scale stated. | Not specified. | NOT SPECIFIED. |
| DL-18 | R2: three-way decision required. R3: proposal. | Module A detects outliers; Module B "flags the component for early rejection"; Explainability: "justify its **classification**". | PS asks for detection, early-rejection flagging and justified classification. **PASS/REVIEW/REJECT is not a PS requirement** (R3 correct); it remains our proposal and must map onto a flag/classification output. | Required output format: not specified. |
| DL-19–DL-25 | (standards, novelty, statistics) | R0 names **no standard** (no AEC-Q001, JEDEC, ISO, AS9100) and makes no statement about novelty or uncertainty. | Unchanged: UNRESOLVED — REQUIRES PRIMARY SOURCE (non-PS). R0 confirms no compliance requirement exists in the PS. | As before. |

## Resolution procedure

1. Obtain the official PS 26170 text; save it under `docs/research/ps-analysis/`. *(Done 2026-09-26.)*
2. For each BLOCKED entry, quote the exact official sentence(s) in the entry,
   set status RESOLVED with date, and record: *Previous claim → New evidence →
   Corrected conclusion*.
3. Propagate to: claim-register, problem-statement-analysis (discrepancy
   table), assumptions-and-constraints, requirements-specification,
   requirements-traceability, data-dictionary, affected architecture docs.
4. Do not delete resolved entries.
