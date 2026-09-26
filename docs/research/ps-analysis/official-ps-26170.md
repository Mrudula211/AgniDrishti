# Official Problem Statement — SIH 2026 PS 26170

Status: Accepted (verified source) · Last updated: 2026-09-26

Source ID used in all docs: **R0** (official PS text).

## 1. Provenance

| Field | Value |
|---|---|
| Authority | Smart India Hackathon official portal (`sih.gov.in`) |
| Page URL | https://sih.gov.in/sih2026PS |
| Location on page | Table row S.No. 170; modal `#ViewProblemStatement26170` |
| Retrieved | 2026-09-26 06:22 UTC (HTTP 200, 2,808,140 bytes, via `curl`) |
| SHA-256 of full page as retrieved | `b431363ccb83156ca4dfb346c44f1b2a6db6399777b41eea76feab14ab40f128` (full page not stored — it lists all 2026 PSs) |
| Preserved copy | [official-ps-26170-sih-portal-extract.html](official-ps-26170-sih-portal-extract.html) — the unmodified HTML of the SIH26170 table row (page lines 23810–23933) |
| SHA-256 of preserved extract | `f28311b73ea7dcc11bfe31f7465adc84139b754c7d3468db32e468d0d685b318` (9,155 bytes) |
| Encoding note | The portal serves mis-encoded characters (e.g. `Â°C`, `ÂµA`, `â€”`). The extract preserves the bytes exactly; the transcription below restores `°`, `µ`, `—` for readability. No other change. |

Secondary aggregator sites (e.g. sihbuddy.in, GitHub PS mirrors) were **not** used as the source.

## 2. Listing metadata (verbatim from the portal)

| Field | Value |
|---|---|
| Problem Statement ID | 26170 (listed as `SIH26170`) |
| Problem Statement Title | AI-Driven Anomaly Detection in Component Burn-In & Screening |
| Organization | Indian Space Research Organisation(ISRO) |
| Department | Department of Space / Indian Space Research Organisation |
| Category | Software |
| Theme | Smart Automation |
| Youtube Link | (empty) |
| Dataset Link | **(empty)** |
| Contact info | (empty) |
| Submitted Idea(s) Count | 31/500 (at retrieval time) |
| Deadline | 30 September 2026 |

## 3. Description (verbatim transcription)

> Background In high-reliability sectors (like space) electronic components undergo rigorous environmental stress screening (ESS), including Burn-In testing (operating components at elevated temperatures, e.g., 125°C for extended periods).
>
> Traditional screening relies on static parametric pass/fail limits. However, 'latent defects'—components that pass the absolute limits but exhibit subtle, anomalous drift over time—often escape into final payloads, leading to catastrophic field failures.
>
> Description Development of a predictive machine learning model that analyzes time-series parametric data (e.g., standby current Iddq, leakage currents, or propagation delays measured at intervals like 0h, 24h, 96h, and 168h to detect anomalous components.
>
> Expected Solution Module A: The outlier detection system Static limits catch obvious failures. Participants need to develop a 'Dynamic' outlier detection system. If a lot has an average leakage current of 10µA, a part showing 45 µA is a massive anomaly, even if the absolute datasheet maximum limit is 50 µA.
>
> Module B: Time-Series Drift Predictor Build a predictive regression model that takes Value_0h and Value_24h as inputs and forecasts Value_168h. If the predicted 168h drift rate exceeds a calculated safety slope, the system flags the component for early rejection.
>
> **Evaluation Metrics:**
>
> • Anomaly Detection Score: a False Negative (missing a defective part) is catastrophic, penalizing teams that let bad parts escape.
> • Drift Prediction Accuracy : The mean absolute error between the predicted Value_168h and the actual hidden ground-truth values.
> • Explainability : Can the model justify its classification to a QA inspector, or is it a complete black box?

(The unclosed parenthesis after "(e.g., standby current Iddq" is in the original.)

## 4. Structured extraction

Only what the text states. Words like "e.g." and "like" mark examples, not fixed requirements.

### 4.1 Requirements

| ID | Official requirement | Quote anchor |
|---|---|---|
| OPS-01 | A predictive ML model that analyses time-series parametric data to detect anomalous components. | "Development of a predictive machine learning model…" |
| OPS-02 | **Module A** — a "Dynamic" outlier detection system that goes beyond static limits; lot-relative (lot average 10 µA → part at 45 µA is anomalous although below a 50 µA datasheet maximum). | "Module A: The outlier detection system…" |
| OPS-03 | **Module B** — a predictive regression model with inputs **`Value_0h` and `Value_24h`** and output **`Value_168h`**. | "takes Value_0h and Value_24h as inputs and forecasts Value_168h" |
| OPS-04 | **Early rejection** — flag a component when the **predicted 168h drift rate exceeds a calculated safety slope**. | "If the predicted 168h drift rate exceeds a calculated safety slope…" |
| OPS-05 | False negatives (missed defective parts) are catastrophic and penalised. | Evaluation: Anomaly Detection Score |
| OPS-06 | Module B accuracy is judged by **MAE** of predicted `Value_168h` against **hidden ground-truth** values. | Evaluation: Drift Prediction Accuracy |
| OPS-07 | The model must be able to **justify its classification to a QA inspector** (not a black box). | Evaluation: Explainability |

### 4.2 Inputs

- Time-series parametric data; example parameters: standby current Iddq, leakage currents, propagation delays.
- Example measurement intervals: 0h, 24h, 96h, 168h.
- Named fields: `Value_0h`, `Value_24h`, `Value_168h`.
- Lot membership (implied by "If a lot has an average…").
- Absolute datasheet limits (implied by "absolute datasheet maximum limit").

### 4.3 Outputs

- Anomalous / outlier components (Module A).
- Predicted `Value_168h` (Module B).
- Early-rejection flag when predicted drift rate exceeds the safety slope (Module B).
- A justification of each classification (Explainability).

### 4.4 Stated context / constraints

- High-reliability (space) setting; ESS / burn-in at elevated temperature, **e.g.** 125 °C.
- Latent defects pass absolute limits but drift anomalously.
- Evaluation uses hidden ground truth (for `Value_168h`).

### 4.5 Evaluation criteria (stated)

1. Anomaly Detection Score — FN catastrophic / penalised. **Formula not given.**
2. Drift Prediction Accuracy — MAE on `Value_168h`.
3. Explainability — qualitative.

### 4.6 Dataset information

- **No dataset link** on the official entry (field empty).
- "Hidden ground-truth values" indicates the evaluators hold data that is not published.

## 5. Not specified by the official text

| Item | Consequence |
|---|---|
| How the "safety slope" is calculated, its value or units | Must be designed, documented and justified by the team; stays a config parameter |
| How "drift rate" is defined (e.g. (Value_168h − Value_0h)/168 h, or relative) | Design decision to document |
| Anomaly Detection Score formula / weighting | Report a full set of detection metrics |
| Exact checkpoints in evaluation data (text says "like 0h, 24h, 96h, and 168h") | Schema must tolerate this |
| Number of parameters per component; which parameters | Schema must support multiple parameter types |
| Whether spec limits are one- or two-sided (propagation delay, leakage) | Support both |
| Lot sizes, wafer / device-family identifiers | — |
| Label format for "defective part" | — |
| At which checkpoint Module A runs | — |
| Required output format (binary vs other), UI, deployment | PASS/REVIEW/REJECT remains our proposal |
| Data volume / scale | — |
| Any standard (AEC-Q001, JEDEC, etc.) | **No standard is named** in the PS |
