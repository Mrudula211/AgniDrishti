# Claim Register

Status: Draft · Last updated: 2026-09-26

Every important claim found in the research sources, classified. This is the
reference for what the team may state as fact, what is a design choice, and
what must never appear in the presentation.

## Sources

| ID | File / origin | Nature | Reliability notes |
|---|---|---|---|
| R0 | Official PS text, SIH portal https://sih.gov.in/sih2026PS (retrieved 2026-09-26) — [ps-analysis/official-ps-26170.md](ps-analysis/official-ps-26170.md) | **Authoritative** PS statement | Added 2026-09-26. Preserved extract + SHA-256 recorded. Takes precedence over R1–R4. |
| R1 | `Comprehensive Guide to Deep Web Research.pdf` (9 pp.) | Generic research-methodology guide (ChatGPT-generated, per its header) | Contains no PS 26170 content. Its bracketed citations (e.g. 【68†L170-L178】) are tool artefacts and cannot be resolved. Useful only as process guidance. |
| R2 | `Deep Research Report.pdf` (13 pp.) | PS-specific technical blueprint, names the solution "AstraGuard" | Cites [1]–[18] but contains **no reference list**; its citations cannot be checked. Contains unmeasured numbers and several statistical overclaims (below). |
| R3 | `SIH_26170_Comprehensive_Research_Report.pdf` (6 pp.) | PS-specific research + prior-art report | Most conservative. Gives URLs for prior work and datasets. Explicitly corrects R2's novelty framing. |
| R4 | Assessment text pasted into Claude Code chat, 2026-09-26 | Critique of R1–R3 | Opinion/assessment; cites SIH college SPOC guidelines PDF for evaluation criteria. |

~~**Critical gap:** none of R1–R4 contains the verbatim, official PS 26170 text.
All PS "facts" below are second-hand paraphrases. `[GAP-01]`~~
**Corrected 2026-09-26:** GAP-01 closed — official text obtained (R0). Sections
1–6 below are the original classification of R1–R4 and are kept unchanged as a
record; **§7 records what R0 confirmed, corrected or left open**, and overrides
§1–§6 where they conflict.

**Verification status:** The official PS (R0), the NASA PCoE repository page
and the NASA IGBT catalogue page were opened on 2026-09-26. In a later pass the
same day, D-05, D-06, D-11, D-12, D-15–D-17 were verified against primary
sources (see §8). D-04 (JEDEC JESD22-A108) remains unverified.

Labels: `[SF]` source-supported fact · `[PA]` prior-art finding · `[EI]` engineering
interpretation · `[PR]` proposal · `[AS]` assumption · `[UV]` unverified claim ·
`[GAP]` research gap · `[NC]` do not claim.

---

## 1. Problem-statement content (as reported)

| # | Claim | Source | Label | Notes |
|---|---|---|---|---|
| PS-01 | Static (absolute-limit) screening can miss a component that stays below its datasheet limit while drifting abnormally relative to its lot. | R3 §1, R2 Part 1/5 | `[SF]` (second-hand) | Both PS-specific reports agree. Core premise. |
| PS-02 | Module A: dynamic, population/lot-relative anomaly detection. | R3 §1, R2 Part 1 | `[SF]` (second-hand) | Agreed by R2 and R3. |
| PS-03 | Module B: early prediction of `Value_168h` from `Value_0h` and `Value_24h`. | R3 §1 | `[SF]` (second-hand) | **Conflicts with R2**, which describes predicting "168h drift rates" and builds features from 0h/24h/96h. See C-01. |
| PS-04 | Early rejection when predicted drift exceeds a "safety slope". | R3 §1 | `[SF]` (second-hand) | The safety slope's value, units and definition are not given. `[GAP-04]` |
| PS-05 | Explainability is explicitly evaluated. | R3 §1; R2 Part 1 ("explainable outputs to QA inspectors") | `[SF]` (second-hand) | Evaluation form/criteria unknown. |
| PS-06 | False negatives are treated as catastrophic. | R2 Part 1 (quotes "False Negative = Catastrophic"); R3 §11 | `[SF]` (second-hand) | R2 escalates this to "prioritize zero false negatives"; that stronger wording is R2's interpretation, not established as PS text. |
| PS-07 | Measurements are taken at 0h, 24h, 96h, 168h. | R2 Part 1/4 | `[SF]` (single source) | R3 names 0h/24h/96h/168h fields in its synthetic design, consistent. |
| PS-08 | Burn-in / ESS at 125 °C. | R2 Part 1 | `[UV]` | Single source, no citation. |
| PS-09 | PS gives the example of a 50 µA absolute limit where the lot average is 10 µA. | R2 Part 5 ("The problem explicitly states…") | `[UV]` | Single source. Treat the numbers as illustrative. |
| PS-10 | No official dataset was found in the public PS material. | R3 §8 | `[SF]` (as of R3's search) | May change if organisers release data. |
| PS-11 | Column naming `Value_0h … Value_168h`. | R3 §1/§9 | `[UV]` | Suggests PS uses these names; not confirmed. |

## 2. Domain and prior-art claims

| # | Claim | Source | Label | Notes |
|---|---|---|---|---|
| D-01 | Latent defects causing infant mortality can pass initial test and be accelerated by burn-in stress. | R2 Part 1 | `[EI]` | Standard reliability-engineering understanding (bathtub curve); not cited in R2. Acceptable as background, phrased generally. |
| D-02 | IDDQ drift can indicate dielectric weakening (e.g. TDDB). | R2 Part 1 | `[UV]` | Plausible mechanism; the PS parameter(s) are not known to be IDDQ. |
| D-03 | "A component drifting 10→45 µA will fail in orbit; one stable at 48 µA is perfectly healthy." | R2 Part 1 | `[UV]` `[NC]` | Illustrative assertion stated as certainty. Do not repeat as fact. |
| D-04 | 125 °C burn-in corresponds to HTOL per JEDEC JESD22-A108. | R2 Part 1 | `[UV]` | JESD22-A108 is a life-test standard; burn-in (100% screening) and HTOL (sample qualification) are different activities. R2 conflates them. |
| D-05 | Part Average Testing (PAT) / Dynamic PAT is codified in AEC-Q001; DPAT sets per-lot/per-wafer limits. | R2 Part 2 | `[PA]` (unverified) | Widely known automotive practice; verify against AEC-Q001 text. |
| D-06 | Robust Z / MAD is "standard in AEC-Q001". | R2 Part 3 | `[UV]` | To verify: AEC-Q001 is commonly described as using a robust mean/sigma based on median and inter-quartile range, not MAD. Do not state MAD = AEC-Q001 method. |
| D-07 | Robust z = (x − median) / (1.4826 · MAD); 1.4826 makes MAD consistent with σ under normality. | R2 Part 5 | `[SF]` | Standard statistics. |
| D-08 | Arrhenius acceleration factor formula. | R2 Part 7 | `[SF]` | Standard formula. **Limited use here**: needs a use temperature and activation energy; with a single burn-in temperature it cannot be fitted from PS data. |
| D-09 | Many degradation parameters follow ΔP(t) = A·tⁿ. | R2 Part 7 | `[PA]` (unverified) | Common empirical model (e.g. NBTI/HCI literature). Applicability to PS parameters unknown. |
| D-10 | Healthy parts stabilise (log-like); defective parts accelerate (n > 1). | R2 Part 4/7 | `[UV]` | Useful hypothesis, must be tested. "n > 1 ⇒ physically anomalous" is not established. |
| D-11 | 2025 Computers & Industrial Engineering paper: data-driven burn-in quality prediction (PAA, PCA, Clopper-Pearson, probabilistic SVR, Bayesian optimisation), synthetic + real data. | R3 §5/§7 | `[PA]` (unverified) | URL given in R3. Verify before citing. |
| D-12 | ESREL 2023: lot-specific health factor for burn-in + binary classifier + LSTM autoencoder. | R3 §5/§7 | `[PA]` (unverified) | URL given in R3. Verify before citing. |
| D-13 | NASA MOSFET thermal-overstress run-to-failure data; GP and model-based prognostics studied on it. | R3 §7/§8 | `[PA]` (unverified) | External data; not SIH data. |
| D-14 | NASA IGBT accelerated ageing data, six devices, multiple electrical variables. | R3 §7/§8 | `[PA]` (unverified) | External data; not SIH data. |
| D-15 | Three-way decision theory / classification with reject option exist as formal frameworks. | R2 Part 9 | `[PA]` | Well-established literature (Yao's three-way decisions; Chow's reject option). Citations to be added. |
| D-16 | Split conformal prediction yields intervals with finite-sample marginal coverage under exchangeability. | R2 Part 8 | `[PA]` | Correct **only** with the exchangeability condition and "marginal" qualifier. See C-06. |
| D-17 | SIH evaluation factors include novelty, complexity, clarity, feasibility, practicability, sustainability, impact, UX, future progression. | R4 (cites SIH SPOC guidelines PDF) | `[PA]` (unverified) | Historic guidance; SIH 2026 criteria to be confirmed. |
| D-18 | A documented SIH 2024 winning solution combined OSRM + HMM + trajectory analysis. | R3 §6 | `[UV]` | No link given for the winning implementation. |

## 3. Method claims

| # | Claim | Source | Label | Notes |
|---|---|---|---|---|
| M-01 | Deep sequence models (LSTM/Transformer) are poorly suited to 4 time points. | R2 Part 3/4/24 | `[EI]` | Sound reasoning (few steps, overfitting, no benefit from recurrence). Still an argument, not a measured result. |
| M-02 | Per-component fit of y = y₀ + A·tⁿ can classify acceleration. | R2 Part 7 | `[EI]` — **identifiability problem** | 3 parameters. With 0h+24h (Module B input) only 2 points: under-determined. With 0h/24h/96h: exactly determined, zero residual degrees of freedom, no noise tolerance. Needs population priors or fixed exponent. See C-08. |
| M-03 | Hierarchical Bayesian model can borrow strength from lot curves. | R2 Part 4 | `[PR]` | Reasonable, but R2 later substitutes "Bayesian Ridge", which is not hierarchical. |
| M-04 | GP is "computationally expensive for millions of parts". | R2 Part 3 | `[UV]` | A per-component GP on ≤4 points is cheap; a population GP is not. Ambiguous. |
| M-05 | XGBoost cannot extrapolate beyond training target range. | R2 Part 33 | `[EI]` | Correct property of tree ensembles; relevant to predicting unusually high 168h values. |
| M-06 | MAD lot-relative scoring "naturally immunizes against covariate shift". | R2 Part 21 | `[UV]` `[NC]` | Only removes per-lot location/scale shifts, and fails when a large fraction of the lot is defective, when MAD ≈ 0, or with small lots. |
| M-07 | Bimodal lots break MAD; check with GMM first. | R2 Part 33 | `[EI]` / `[PR]` | Valid concern. GMM is one option; simpler checks (e.g. wafer grouping, dip test) should be compared. |
| M-08 | CRI = α·Z + β·dV/dt + γ·Ŷ/limit, Platt-scaled, so "CRI 0.90 = 90% probability of latent failure". | R2 Part 17 | `[PR]` + `[NC]` | Calibration on synthetic labels calibrates to the generator, not to real latent failure. Do not claim probabilistic meaning without held-out calibration on real labels. |
| M-09 | Conformal gives "mathematically guaranteed coverage even for small/sparse datasets". | R2 Part 8 | `[UV]` `[NC]` | Guarantee is marginal, assumes exchangeability (violated by lot shift unless calibration is by lot/group), and small calibration sets give high-variance coverage. |
| M-10 | "Expected Calibration Error" as regression metric. | R2 Part 22 | `[EI]` — misapplied | ECE is a classification-probability metric. For regression intervals use coverage and width; ECE applies only if a calibrated risk probability is produced. |
| M-11 | "Recall at fixed 5% FPR" as the primary metric. | R2 Part 22 | `[PR]` | A valid operating-point metric; tension with "zero false negatives" framing. Operating point must be chosen with the team (see evaluation protocol). |

## 4. Results-like statements (none are measured)

| # | Statement | Source | Label |
|---|---|---|---|
| X-01 | Static limits catch 20% of latent defects; +MAD 65%; +drift prediction 92%; +conformal zero catastrophic FN. | R2 Part 22–23 | `[NC]` — no experiment exists |
| X-02 | "Eliminated catastrophic false negatives while keeping the manual review queue under 8%." | R2 Part 30 | `[NC]` — no experiment exists |
| X-03 | Competitor tiers: 60% generic ML, 25% deep learning, 10% statistical, top 2–3 physics-informed. | R2 Part 13 | `[NC]` — speculation presented as figures |
| X-04 | "70–80% of teams will build a Streamlit + Isolation Forest/LSTM." | R2 Part 35 | `[NC]` |
| X-05 | "Saving 72 hours of burn-in" per early reject. | R2 Part 19 | `[UV]` — depends on the decision checkpoint (96h → 72h saved; 24h → 144h) and on whether early removal is operationally allowed. |
| X-06 | Illustrative FN sequence "17% → 9% → 4% → 1%". | R4 §5 | `[NC]` — explicitly illustrative in R4 |
| X-07 | Explanation example "3.2σ, 99th percentile, n = 1.4, 46 µA, bound 51 µA" for C-1047. | R2 Part 10 | Illustrative format only; `[NC]` as a result |

## 5. Positioning / claims to avoid

| # | Claim | Source | Label | Replacement |
|---|---|---|---|---|
| N-01 | "Highly defensible, novel engineering implementation." | R2 Part 14 | `[NC]` | "Proposed PS-specific integration" (R3 §5) |
| N-02 | "AEC-Q001 DPAT compliant." | R2 Part 32 | `[NC]` | "Informed by lot-relative (DPAT-style) screening practice" |
| N-03 | "95% Confidence Bounds" for conformal output. | R2 Part 28/32 | `[NC]` | "95% prediction interval (target marginal coverage)" |
| N-04 | "95% probability of breaching the 50 µA limit." | R2 Part 19/30 | `[NC]` | "The upper end of the prediction interval crosses the limit." |
| N-05 | "Physics-informed digital twin." | R2 Part 6/30 | `[NC]` unless physics is encoded and validated | "Trajectory model with a degradation-shaped feature set" |
| N-06 | "Remaining Useful Life / Probability of Survival index." | R2 Part 6 | `[NC]` | Requires time-to-failure data, not available. |
| N-07 | "ISO 9001 / AS9100 traceability ensured." | R2 Part 27 | `[NC]` | "Decision audit log designed to support traceability." |
| N-08 | First / novel use of AI, lot analysis, uncertainty, LSTM for burn-in; patent-pending. | R3 §13 | `[NC]` | — |

## 6. Contradictions between sources

| ID | Topic | R2 | R3 / R4 | Resolution in this repo |
|---|---|---|---|---|
| C-01 | Module B inputs | 0h/24h/96h features; velocity uses 96h and 24h | 0h + 24h → 168h | **Resolved 2026-09-26 by R0:** Module B inputs are Value_0h + Value_24h (R3 correct). T96 path is an optional extension outside Module B. See §7 and `ps-analysis/discrepancy-log.md` DL-01. |
| C-02 | Novelty | "novel" | "not proven novel" | Follow R3. |
| C-03 | Ablation numbers | Gives numbers | R3/R4: must be measured | No numbers until measured. |
| C-04 | Uncertainty wording | "confidence bounds", "95% probability" | R4: prediction interval | Use prediction-interval language. |
| C-05 | CRI meaning | Probability | R4: risk score | Risk score; probability only if calibrated on held-out real labels. |
| C-06 | Conformal guarantees | Unqualified guarantee | — | Marginal, exchangeability, group-aware calibration. |
| C-07 | Metrics | ECE + Recall@5%FPR | R3: recall, precision, F1, PR-AUC, FNR, MAE/RMSE, coverage, operational | Use R3 set + interval width; ECE only for calibrated probabilities. |
| C-08 | Physics model | Per-component power-law fit | — | Not identifiable from 2–3 points; use population-level fits or fixed-shape features. |
| C-09 | Project name | AstraGuard | AgniDrishti (this repo) | AgniDrishti. |
| C-10 | Pipeline order | Trajectory map before decision (Part 35E) | Decision then explanation (R3 §3) | Explanation is generated from the decision evidence; order is R3's. |
| C-11 | Synthetic-data circularity | Generate defects as t^1.5, detect via n > 1 | R3: do not fabricate physics | Generator must not be tuned to the detector; add scenarios the detector was not designed for. See dataset strategy. |

## 7. Verification update — official PS text (R0), 2026-09-26

Format: **Previous claim → New evidence → Corrected conclusion.** Details and
verbatim quotes: [ps-analysis/discrepancy-log.md](ps-analysis/discrepancy-log.md) §Resolutions.

### 7.1 PS-content claims

| # | Previous classification | New evidence (R0) | Corrected conclusion | New label |
|---|---|---|---|---|
| PS-01 | `[SF]` second-hand | R0 Background: latent defects "pass the absolute limits but exhibit subtle, anomalous drift over time" | Confirmed | `[SF]` R0 |
| PS-02 | `[SF]` second-hand | R0 Module A: "'Dynamic' outlier detection system", lot example | Confirmed | `[SF]` R0 |
| PS-03 | `[SF]` second-hand, conflicts with R2 | R0: "takes Value_0h and Value_24h as inputs and forecasts Value_168h" | Confirmed; R2's 96h-based early prediction is **not** Module B | `[SF]` R0 |
| PS-04 | `[SF]` second-hand, threshold undefined | R0: "predicted 168h drift rate exceeds a **calculated** safety slope" | Confirmed; calculation method **not specified** | `[SF]` R0 + `[GAP]` method |
| PS-05 | `[SF]` second-hand | R0 Evaluation: "Explainability : Can the model justify its classification to a QA inspector…" | Confirmed | `[SF]` R0 |
| PS-06 | `[SF]` second-hand; R2 "zero FN" | R0: "a False Negative … is catastrophic, penalizing teams that let bad parts escape" | Confirmed as "catastrophic"; "zero FN" is **not** PS wording | `[SF]` R0 |
| PS-07 | `[SF]` single source | R0: "measured at intervals **like** 0h, 24h, 96h, and 168h" | Confirmed as **example** intervals | `[SF]` R0 (examples) |
| PS-08 | `[UV]` 125 °C | R0: "e.g., 125°C" | Confirmed as **example** only | `[SF]` R0 (example) |
| PS-09 | `[UV]` 50 µA / 10 µA | R0: lot average 10 µA, part 45 µA, datasheet max 50 µA | Confirmed with the missing 45 µA value | `[SF]` R0 (illustration) |
| PS-10 | `[SF]` as of R3 | R0 Dataset Link field empty | Confirmed: no published official dataset | `[SF]` R0 |
| PS-11 | `[UV]` Value_* naming | R0 uses `Value_0h`, `Value_24h`, `Value_168h` | Confirmed for these three names; `Value_96h` not named | `[SF]` R0 |

### 7.2 New facts from R0 not in any earlier source

| # | Fact | Label |
|---|---|---|
| PS-12 | Module B accuracy is scored by **MAE** between predicted Value_168h and **hidden ground-truth** values. | `[SF]` R0 |
| PS-13 | Example parameters include **propagation delays** in addition to Iddq and leakage currents. | `[SF]` R0 |
| PS-14 | Organisation: ISRO; Department: Department of Space / ISRO; Category: Software; Theme: Smart Automation; submission deadline 30 September 2026. | `[SF]` R0 |
| PS-15 | Three official evaluation criteria: Anomaly Detection Score, Drift Prediction Accuracy (MAE), Explainability. Anomaly Detection Score formula not given. | `[SF]` R0 + `[GAP]` formula |
| PS-16 | The PS names **no** standard (AEC-Q001, JEDEC, ISO 9001, AS9100). | `[SF]` R0 |

### 7.3 Earlier claims affected

| # | Previous | Corrected conclusion |
|---|---|---|
| D-04 | `[UV]` 125 °C HTOL per JESD22-A108 | Temperature is only an example in R0; the JEDEC link remains `[UV]` and is not a PS statement. |
| M-10 | ECE misapplied | R0 confirms MAE as the drift metric; ECE/Recall@5%FPR are not PS metrics. |
| M-11 | Recall@5%FPR proposed as primary | Not a PS metric. May be reported as one operating point, never as "the" metric. |
| X-05 | "Saving 72 hours" `[UV]` | R0 inputs are 0h + 24h; the 72 h figure assumed a 96h decision and is **not** supported. Stays `[NC]` until measured with a documented assumption. |
| C-01 | Unresolved | **Resolved by R0** in favour of 0h + 24h. |
| C-07 | Metrics disagreement | R0 defines MAE + Anomaly Detection Score + Explainability; our wider metric set remains for internal evaluation. |
| DS-01 | "No official dataset located" (R3) | Confirmed by the official entry's empty Dataset Link — [datasets/official-dataset-verification.md](datasets/official-dataset-verification.md). |
| D-13, D-14 | NASA datasets `[PA]` unverified | Repository/catalogue pages verified 2026-09-26 (description, citation, terms, sizes) — [datasets/external-datasets.md](datasets/external-datasets.md). Still external, not SIH data. |

## 8. Verification update — primary external sources, 2026-09-26

Sources S-01…S-17: [prior-art/literature-review.md](prior-art/literature-review.md).

| # | Previous | New evidence | Corrected conclusion | New label |
|---|---|---|---|---|
| D-05 | DPAT codified in AEC-Q001 `[PA]` unverified | S-01 §3.1.2: Dynamic PAT limits = Robust Mean ± 6 Robust Sigma from current lot/wafer | Confirmed | `[PA]` S-01 (V-FULL) |
| D-06 | "MAD standard in AEC-Q001" `[UV]` | S-01 §2.4: Robust Mean = median; Robust Sigma = (Q3 − Q1)/1.35 | **R2 wrong.** AEC uses IQR, not MAD | `[NC]` for R2 wording; `[SF]` S-01 for the formula |
| D-11 | C&IE 2025 `[PA]` unverified | S-04 Crossref + abstract: Ahmed, Baraldi, Zio, Lewitschnig; CIE 204:111115; predicts **batch quality before burn-in** | Confirmed; scope narrower than R3 implied (not in-burn-in, not per component) | `[PA]` S-04 (V-ABS) |
| D-12 | ESREL 2023 `[PA]` unverified | S-05 abstract: lot health factor from **APC process data**, "not the raw sensor data" | Confirmed; uses process data, not burn-in measurements | `[PA]` S-05 (V-ABS) |
| D-15 | Reject option / three-way `[PA]` | S-13 Chow 1970; S-14 Yao 2010 (Crossref) | Citations added | `[PA]` (V-BIB) |
| D-16 | Split conformal marginal coverage `[PA]` | S-10 Lei et al. 2018; S-11 Dunn et al. 2023 (groups break exchangeability) | Confirmed; lot structure needs group-aware calibration | `[PA]` |
| D-17 | SIH evaluation factors `[PA]` unverified (historic) | S-16 SIH 2026 Guidelines p. 13 lists the same factors | Confirmed for 2026 | `[SF]` S-16 |
| D-19 | — (new) | S-02/S-03 ESCC: burn-in drift failure = change from 0h larger than per-parameter Δ | Drift-from-0h limits are established space practice | `[PA]` S-02 (V-FULL) |
| D-20 | — (new) | S-06 US 8,010,310 claim 1: pre/post burn-in comparison → outlier device | Per-device burn-in drift outliers are patented prior art | `[PA]` S-06 (V-ABS) |
| D-21 | — (new) | S-17: idea PPT max 6 slides incl. title, PDF only, fixed template | Idea-round format is fixed | `[SF]` S-17 |
| N-09 | — (new) | S-02, S-06 | Do not claim lot-relative or per-device **burn-in drift screening** as new | `[NC]` |
| N-10 | — (new) | S-02 | Do not claim "ESCC compliant" | `[NC]` |
