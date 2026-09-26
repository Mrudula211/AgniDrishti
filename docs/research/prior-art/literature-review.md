# Literature Review and Source Registry

Status: Draft · Last updated: 2026-09-26

Supersedes the earlier unverified version of this file (which listed items
"as reported by R2/R3"). Sources below carry IDs `S-xx`, used across the docs.

**Verification levels**

| Level | Meaning |
|---|---|
| **V-FULL** | Primary document opened and the relevant text read |
| **V-ABS** | Official record / abstract / claims read; full text not accessed |
| **V-BIB** | Bibliographic record confirmed (Crossref / publisher); content from general knowledge of the work, not re-read this session |
| **UV** | Not verified; do not cite in the presentation |

Search snippets are never treated as sources.

## 1. Verified sources

### Standards and specifications

| ID | Source | Type | Relevant contribution | Proves | Does NOT prove | PPT? | Level |
|---|---|---|---|---|---|---|---|
| S-01 | AEC Component Technical Committee, *AEC-Q001 Rev-D: Guidelines for Part Average Testing*, 9 Dec 2011. http://www.aecouncil.com/Documents/AEC_Q001_Rev_D.pdf | Industry guideline | §2.4 Robust Mean = median (Q2); Robust Sigma = (Q3 − Q1)/1.35 ("inexact for sample sizes less than 20"). §3.1.2 Dynamic PAT limits = Robust Mean ± 6 Robust Sigma, from the current lot/wafer of parts that passed static limits | Lot-relative screening with robust statistics is established automotive practice; the exact AEC formula | Anything about burn-in drift or prediction (not covered); that MAD is the AEC statistic (it is not) | Yes | V-FULL |
| S-02 | European Space Agency, *ESCC Generic Specification No. 9000 (Integrated Circuits)*, Issue 10, Feb 2018. https://escies.org/download/specdraftapppub?id=3659 | Space component specification | §6.2.2 parameter drift failure = change during burn-in larger than Δ in the detail spec; §8.15–8.16 burn-in per MIL-STD-883 TM 1015, "Drift shall be related to the initial measurement"; §6.4.1.1 lot fails if drift + limit failures exceed 5 % (PDA) | Space-grade screening already uses per-component drift-from-0h limits and lot-level failure fractions | Any prediction of later values; any lot-relative statistic | Yes | V-FULL |
| S-03 | ESA, *ESCC Detail Specification No. 9202/045* (CMOS 4049UB), Issue 6, Aug 2020. https://escies.org/escc-specs/published/9202045.pdf | Detail specification | §2.4 drift values: IDD ±75 nA (absolute) with absolute max 500 nA; IOL/IOH ±15 % (relative); VTH ±0.3 V | Drift limits are per parameter, absolute or relative, and coexist with absolute limits | Values for any PS 26170 component | Yes, as an example of practice | V-FULL |

### Burn-in prior art (papers)

| ID | Source | Data | Relevant contribution | Proves | Does NOT prove | PPT? | Level |
|---|---|---|---|---|---|---|---|
| S-04 | I. Ahmed, P. Baraldi, E. Zio, H. Lewitschnig, "A data-driven modelling framework for predicting the quality of semiconductor devices to support burn-in decisions", *Computers & Industrial Engineering* 204, 111115 (2025). doi:10.1016/j.cie.2025.111115 | Synthetic case study + real production data (per abstract) | Predicts quality of a **production batch before burn-in** (PAA + PCA features, Clopper-Pearson, probabilistic SVR, Bayesian optimisation) to plan how many devices / which tests go to burn-in | ML with uncertainty for burn-in decisions is published | Per-component prediction during burn-in; lot-relative outliers | Yes (as prior art) | V-ABS (full text: HTTP 403) |
| S-05 | L. Langenberg, R. Pätzold, A. Khalid, "Process Data Analysis for Improved Burn-In Strategies Based on Complementary AI Models", *ESREL 2023*. https://rpsonline.com.sg/proceedings/esrel2023/html/P620.html | Real APC (process-control) meta/logistics data; known BI defects | Lot-specific health factor h from fab process data; binary classifier + LSTM autoencoder; aims to reduce BI time / sample size | Lot-level AI health assessment for burn-in is published | Use of burn-in parametric measurements or per-component trajectories (it uses process data, "not the raw sensor data") | Yes (as prior art) | V-ABS |
| S-09 | B. Aydinkarahaliloglu et al., "Predicting early failure of quantum cascade lasers during accelerated burn-in testing using machine learning", *Scientific Reports* 12 (2022). doi:10.1038/s41598-022-13303-0 | 9 lasers, one wafer; measurements every minute + LIV every ≈2.5 h | RBF-SVM on in-burn-in features predicts premature failure early | Per-device early failure prediction from in-burn-in measurements is published | Anything for sparse checkpoints, lots, uncertainty or abstention (none used); generalisation (n = 9) | Yes (as prior art; its numbers are its own) | V-FULL (PMC) |

### Patents (not legal advice; status as shown by Google Patents on 2026-09-26)

| ID | Patent | Contribution | Relevance | Level |
|---|---|---|---|---|
| S-06 | US 8,010,310 B2, AMD, "Method and apparatus for identifying outliers following burn-in testing", priority 2007-07-27, granted 2011-08-30, shown "Active", expiry 2029-11-02 | Claim 1: retrieve pre- and post-burn-in data per device, compare, "identifying the device as an outlier device based on the comparison". Examples: static IDD shifts; second acceptance criteria | **Per-device burn-in drift comparison for outlier identification is patented prior art.** Uses deterministic criteria; no prediction, no intermediate checkpoints, no uncertainty | V-ABS |
| S-07 | US 6,230,293 B1, Lucent, "…differential Iddq screening in lieu of burn-in", 2001, expired | ΔIddq (two supply voltages) outliers to replace burn-in | Delta-measurement outlier screening is old art | V-ABS |
| S-08 | US 6,968,287 B2, Texas Instruments, "System and method for predicting burn-in conditions", 2005 | Predicts burn-in **temperature** from IDDQ baselines | Context only (not screening) | V-ABS |

### Statistics and decision theory

| ID | Source | Relevance | Level |
|---|---|---|---|
| S-10 | J. Lei, M. G'Sell, A. Rinaldo, R. J. Tibshirani, L. Wasserman, "Distribution-Free Predictive Inference for Regression", *JASA* 113(523):1094–1111 (2018). doi:10.1080/01621459.2017.1307116 | Split conformal regression intervals; finite-sample **marginal** coverage under exchangeability | V-BIB |
| S-11 | R. Dunn, L. Wasserman, A. Ramdas, "Distribution-Free Prediction Sets for Two-Layer Hierarchical Models", *JASA* 118(544):2491–2502 (2023). doi:10.1080/01621459.2022.2060112 | Exchangeability fails when observations come in groups from different distributions; proposes CDF pooling / subsampling. **Directly relevant: components grouped in lots** | V-ABS |
| S-12 | R. F. Barber, E. J. Candès, A. Ramdas, R. J. Tibshirani, "Conformal prediction beyond exchangeability", *Ann. Statist.* 51(2):816–845 (2023). doi:10.1214/23-AOS2276 | Coverage loss bounded under distribution drift; weighted conformal | V-BIB |
| S-13 | C. K. Chow, "On optimum recognition error and reject tradeoff", *IEEE Trans. Inf. Theory* 16(1):41–46 (1970). doi:10.1109/TIT.1970.1054406 | Reject option (abstain) — basis for REVIEW | V-BIB |
| S-14 | Y. Yao, "Three-way decisions with probabilistic rough sets", *Information Sciences* 180(3):341–353 (2010). doi:10.1016/j.ins.2009.09.021 | Accept / reject / defer decisions | V-BIB |
| S-15 | C. J. Lu, W. O. Meeker, "Using Degradation Measures to Estimate a Time-to-Failure Distribution", *Technometrics* 35(2):161–174 (1993). doi:10.1080/00401706.1993.10485038 | Random-effects degradation paths: borrow strength across units when each has few measurements | V-BIB |

### SIH official documents

| ID | Source | Level |
|---|---|---|
| S-16 | *SIH 2026 Guidelines* (PDF, 26 pp.), https://sih.gov.in/letters/2026/SIH%202026%20Guidelines.pdf, retrieved 2026-09-26, SHA-256 `5dcbab76e01805d2e6577f217d97b22e26313ae7d40b369237b12b587c3a7fd7` | V-FULL |
| S-17 | *SIH 2026 Idea Presentation Format* (PPTX), https://sih.gov.in/letters/2026/SIH2026-IDEA-Presentation-Format.pptx, retrieved 2026-09-26, SHA-256 `ce3e5deebec2741f3383cb2dd21269cad8d9930f7c747c9903d7d4b27db14de6` | V-FULL |

Not stored in the repository (size / not project data); hashes allow re-verification.

### Datasets

NASA PCoE MOSFET and NASA IGBT: verified — see
[../datasets/external-datasets.md](../datasets/external-datasets.md).

## 2. Not verified (do not cite yet)

| Item | Why listed | Status |
|---|---|---|
| W. Kuo, Y. Kuo, "Facing the headaches of early failures: a state-of-the-art review of burn-in decisions", Proc. IEEE (1983) | Classic burn-in review | UV (Crossref rate-limited) |
| Liu, Ting, Zhou, "Isolation Forest", ICDM 2008 | Comparator E2b | UV |
| Romano, Patterson, Candès, "Conformalized quantile regression", NeurIPS 2019 | Option U2 | UV |
| "Adaptive burn-in time decision system based on pattern recognition…", Expert Syst. Appl. (ScienceDirect S095741740700396X) | Lot-level adaptive burn-in time | UV (403) |
| "New Method of Screening Out Outlier; Expanded PAT During Package Level Test", IEEE doc. 8057864 | PAT beyond wafer sort | UV |
| US 2003/0151422 A1 "Method for burn-in testing"; US 5,204,618 "Monitored burn-in system" | Burn-in prediction / early termination | UV (snippets only) |
| MIL-STD-883 TM 1015, MIL-PRF-38535 | Burn-in method referenced by S-02 | UV (not opened) |
| Public SIH26170 team repositories (e.g. AETHER-SIH26170, BurnQ-SIH-170) | Observed competitor pattern (snippet describes a "healthy 95th-percentile safety slope") | Not opened; never evidence; see sih-presentation-research.md |

## 3. Findings by topic

1. **Lot-relative screening** `[PA]` S-01: established; the AEC formula is
   median ± 6·IQR/1.35, not MAD. Our MAD variant is a design choice.
2. **Burn-in drift screening** `[PA]` S-02, S-03, S-06, S-07: comparing each
   part's burn-in change against an allowance (ESCC) or flagging drift outliers
   (AMD patent) is established. It is **not** a differentiator.
3. **ML for burn-in** `[PA]` S-04, S-05, S-09: exists at batch level before
   burn-in (S-04), at lot level from process data (S-05), and per device with
   dense data (S-09).
4. **Grouped-data uncertainty** `[PA]` S-10–S-12: marginal coverage under
   exchangeability; lots violate it (S-11), so calibration must be lot-aware.
5. **Abstention** `[PA]` S-13, S-14.
6. **Sparse degradation** `[PA]` S-15: random-effects models pool across units.
7. **Not found** `[GAP]`: a published or patented method that predicts a
   late burn-in value from two early sparse checkpoints, compares the predicted
   drift with an allowance, attaches a lot-aware prediction interval, and
   abstains to review. **Not established by available research** — the search
   was limited (below) and absence of evidence is not evidence of novelty.

## 4. Search log (2026-09-26)

| Query / action | Outcome |
|---|---|
| Title search for S-04; Crossref query | Record + abstract found (S-04) |
| Fetch ESREL 2023 P620 | S-05 abstract |
| "burn-in parametric drift outlier detection lot delta part average testing" | PAT vendor pages; patents 7129735, 7494829, 8126681 (not opened) |
| "patent predicting burn-in failure from early parametric measurements … early termination" | S-09; US 2003/0151422, US 5,204,618 (snippets) |
| "patent delta part average testing drift … pre burn-in post burn-in" | S-06, S-07 |
| "burn-in semiconductor drift outlier lot early prediction prediction interval OR conformal" | Only SIH team repos and old patents; no paper combining the elements |
| "ESCC 9000 burn-in drift values" → full texts downloaded | S-02, S-03 |
| AEC-Q001 Rev-D PDF downloaded | S-01 |
| Conformal / decision / degradation references via Crossref | S-10–S-15 |
| SIH portal → guidelines + template downloaded | S-16, S-17 |

Not searched yet (next pass): IEEE Xplore / Google Scholar full-text search for
"burn-in" + "prediction interval"; Indian patent database; ISRO/URSC
component-screening documents; MIL-PRF-38535 PDA / delta rules.
