# Problem Statement Analysis — PS 26170

Status: Draft · Last updated: 2026-09-26

SIH 2026 — PS 26170 — *AI-Driven Anomaly Detection in Component Burn-In & Screening*

> ~~**Provenance warning.** The official PS text is not in this repository.
> Requirements below are extracted from R2 and R3 paraphrases.~~
>
> **Updated 2026-09-26:** the official PS text (R0) has been obtained and
> preserved — [official-ps-26170.md](official-ps-26170.md). §1 below is the
> original second-hand extraction, kept as a record; **§1a is authoritative**.
> §10 records every difference.

## 1a. Official requirements (R0) — authoritative

| ID | Official requirement | Maps to earlier PSR |
|---|---|---|
| OPS-01 | Predictive ML model analysing time-series parametric data (e.g. Iddq, leakage currents, propagation delays; intervals like 0h/24h/96h/168h) to detect anomalous components | PSR-01 |
| OPS-02 | Module A — "Dynamic" outlier detection beyond static limits; lot example 10 µA avg / 45 µA part / 50 µA max | PSR-02, PSR-07 |
| OPS-03 | Module B — regression: inputs Value_0h, Value_24h → output Value_168h | PSR-03 |
| OPS-04 | Early-rejection flag when predicted 168h drift rate exceeds a calculated safety slope | PSR-04 |
| OPS-05 | False negatives catastrophic, penalised (Anomaly Detection Score) | PSR-05 |
| OPS-06 | Drift Prediction Accuracy = MAE of predicted Value_168h vs hidden ground truth | — (new) |
| OPS-07 | Explainability: justify classification to a QA inspector | PSR-06 |

Not specified by R0: safety-slope calculation, drift-rate formula, Anomaly
Detection Score formula, schema beyond three named fields, label format,
Module A checkpoint, scale, output format. See
[official-ps-26170.md](official-ps-26170.md) §5.

## 1. Extracted PS requirements

Only items that R2/R3 attribute to the PS itself are listed here. Proposals
from the reports are **not** requirements.

| ID | Requirement (as reported) | Source | Confidence |
|---|---|---|---|
| PSR-01 | Handle burn-in parametric data measured at sparse checkpoints (0h, 24h, 96h, 168h). | R2 P1 | Medium (single source for the exact checkpoints; consistent with R3 field names) |
| PSR-02 | **Module A** — detect components that are anomalous relative to their lot/population ("dynamic" detection), not only by absolute limit. | R2 P1, R3 §1 | High (both sources) |
| PSR-03 | **Module B** — predict `Value_168h` early from `Value_0h` and `Value_24h`. | R3 §1 | Medium (R2 differs, C-01) |
| PSR-04 | Early rejection when predicted drift exceeds a safety slope. | R3 §1 | Medium; threshold undefined |
| PSR-05 | False negatives are catastrophic — detection must be biased against misses. | R2 P1, R3 §11 | High |
| PSR-06 | Outputs must be explainable (evaluated explicitly). | R2 P1, R3 §1 | High |
| PSR-07 | Absolute (datasheet) limits alone are insufficient; the example given contrasts a 50 µA limit with a 10 µA lot average. | R2 P5 | Medium; numbers illustrative |

Not established as PS requirements (appear only as report proposals):
uncertainty estimation, PASS/REVIEW/REJECT, trajectory maps, risk index, audit
log, edge deployment, wafer-level analysis, 125 °C temperature (R2 only),
scalability targets. These are **design responses**, listed in the
[requirements specification](../../requirements/requirements-specification.md)
with their own justification.

## 2. What the problem is

A burn-in process stresses every component and measures one or more electrical
parameters at a few checkpoints. Today, acceptance is decided by comparing each
measurement to a fixed specification limit. The PS asks for a system that also
recognises **abnormal behaviour that stays inside the limit** — abnormal compared
with the lot it came from, or abnormal in how it changes over time — and that
predicts the end-of-burn-in (168h) state early enough to act on it.

## 3. Why the problem exists `[EI]`

- Manufacturing variation means lots differ; a fixed limit must be wide enough
  to accept every legitimate lot, so it is loose for most of them.
- Latent defects (D-01) degrade under stress. At early checkpoints their value
  may be normal in absolute terms; the signal is relative position and change.
- Burn-in time is expensive; waiting until 168h to see the outcome delays
  decisions and occupies capacity.

## 4. Why conventional screening can miss failures `[EI]`

| Case | Absolute check | What is missed |
|---|---|---|
| High relative to lot, below limit | PASS | Peer abnormality |
| Normal level, abnormally fast drift | PASS | Temporal abnormality |
| Drift accelerating between 24h and 96h | PASS until it crosses | Trend |
| High absolute value but stable and consistent with a high lot | PASS (correct) | — (the system must *not* flag this; R3 §9) |

The last row matters: a good solution reduces misses **without** flagging every
high-but-healthy part.

## 5. Latent / hidden degradation in the PS context `[EI]`

A component is treated as having latent degradation when its early behaviour
(relative level, drift, or drift change) is consistent with progression toward
a specification or safety-slope violation, even though no violation has
occurred yet. **In the available data, only measured behaviour is observable.**
True latent failure (in the field) is not observable, so every label is a proxy
(see assumption A-06).

## 6. Roles of each concept

| Concept | Role in the PS | Label |
|---|---|---|
| Burn-in | Stress that accelerates latent defects so they become measurable | `[EI]` |
| Lot-to-lot variation | Reason a global threshold is insufficient; defines "normal" per lot | `[SF]`/`[EI]` |
| Temporal behaviour | Drift and its change carry the degradation signal | `[SF]`/`[EI]` |
| Anomaly detection | Module A: peer-relative abnormality | `[SF]` |
| 168h prediction | Module B: early estimate of the end state for early decisions | `[SF]` |
| Uncertainty | Not stated in PS; needed because a point prediction from 2 points is unreliable and FN is catastrophic | `[EI]`/`[PR]` |
| False negatives | Dominant cost; drives thresholds and the REVIEW path | `[SF]` |
| Explainability | Evaluated; engineers must verify each decision | `[SF]` |

## 7. Operational requirements (inferred) `[EI]`

- Batch processing per lot (lot statistics need the whole lot at a checkpoint).
- Decisions at defined checkpoints, reproducible from logged inputs.
- Review workload must be measurable and bounded.
- Engineers must be able to override and the override must be recorded.

## 8. Expected inputs and outputs

**Inputs** — see research synthesis §4; canonical schema in
[../datasets/data-dictionary.md](../datasets/data-dictionary.md).

**Outputs (proposed)** per component per checkpoint: absolute-spec status,
lot-relative scores, trajectory features, predicted 168h value with interval,
decision (PASS/REVIEW/REJECT), fired rule(s), explanation text, audit record.

## 9. Constraints, assumptions, unknowns

See [assumptions-and-constraints.md](assumptions-and-constraints.md).

## 10. Differences between §1 (second-hand) and R0 (official)

Full detail: [discrepancy-log.md](discrepancy-log.md) §Resolutions.

| PSR | Previous (§1) | Official text says (R0) | Change required |
|---|---|---|---|
| PSR-01 | Checkpoints 0/24/96/168h, medium confidence | "intervals **like** 0h, 24h, 96h, and 168h" — examples; parameters e.g. Iddq, leakage currents, **propagation delays** | Treat checkpoints as examples; support multiple parameter types and units |
| PSR-02 | Dynamic lot-relative detection | Confirmed ("'Dynamic' outlier detection", lot example) | None |
| PSR-03 | 0h+24h → 168h, medium confidence (conflict with R2) | Confirmed: "takes Value_0h and Value_24h as inputs and forecasts Value_168h" | Module B = 0h+24h only; T96 predictor is not Module B |
| PSR-04 | Safety slope, threshold undefined | "a **calculated** safety slope" — method not given | Safety-slope calculation is a documented design decision |
| PSR-05 | FN catastrophic | Confirmed; "penalizing teams that let bad parts escape" | None |
| PSR-06 | Explainability evaluated | Confirmed; "justify its classification to a QA inspector" | None |
| PSR-07 | 50 µA vs 10 µA example | 10 µA lot average, **45 µA** part, 50 µA datasheet max | Use the official numbers when citing the example |
| — (new) | — | MAE on Value_168h vs hidden ground truth is the drift metric | Added as OPS-06; MAE is the primary Module B metric |
| — | "Not established as PS requirements" list (§1) | R0 confirms: uncertainty, PASS/REVIEW/REJECT, trajectory map, risk index, audit log, edge deployment, wafer analysis are **not** in the PS | No change — they stay design proposals |
| — | 125 °C (R2 only) | "e.g., 125°C" | Example only |
