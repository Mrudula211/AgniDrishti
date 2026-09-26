# Synthetic Data Design

Status: Accepted (design approved by user 2026-09-26, Decision 5; held-out families sealed and sweep grids pre-registered 2026-09-26) · Last updated: 2026-09-26

Supersedes dataset-strategy.md §3 (moved here). Category: **Synthetic** — never
"real", "hardware", "ISRO" or "SIH" data.

## 1. Purpose and limits

| Can answer | Cannot answer |
|---|---|
| Does a method behave as intended under controlled, stated conditions? | How it performs on ISRO components or the hidden evaluation |
| Where does it break (small lots, MAD = 0, bad lots, glitches)? | Real defect prevalence, real drift shapes |
| Do layers add value **relative to each other** under the same assumptions? | Absolute performance |

## 2. Structure (constrained by R0)

- Lots of components; each component has one or more parameters.
- Checkpoints 0h, 24h, 96h, 168h (R0 examples); 96h is generated but is not a
  Module B input.
- A datasheet limit per parameter (one- or two-sided, configurable).
- Parameter families mimicking the R0 examples: a current-like parameter
  (positive, right-skewed, rises with degradation) and a delay-like parameter
  (can shift either way). Units are "arbitrary units" unless an assumption is
  written down; the R0 10 / 45 / 50 µA example is an illustration, not a
  distribution to copy.

## 3. Scenario families

Each component gets exactly one `scenario` tag. Families marked **H** are
held out: never used while designing or tuning any detector; used only in R-01.

| # | Family | Mechanism (assumption) | Purpose |
|---|---|---|---|
| 1 | Healthy stable | Level from lot distribution; small noise | Baseline FPR |
| 2 | Healthy drift | Whole lot drifts slowly, component follows lot | Lot-relative must not flag |
| 3 | High-but-stable | High level consistent with a high lot, no drift | Must not flag (R3 §9) |
| 4 | Lot shift | Lot mean offset vs other lots | Cross-lot robustness |
| 5 | Lot contamination | 10–40 % (swept) degrading parts in one lot | Masking of robust stats |
| 6 | Bimodal lot | Two sub-populations (e.g. wafers) | False flags |
| 7 | Small lot | n swept down to very small | Scale instability |
| 8 | MAD ≈ 0 | Quantised measurements | Degenerate scale |
| 9 | Measurement noise | Noise level swept | Separability |
| 10 | Glitch | Single-checkpoint spike, trajectory otherwise normal | Must not reject on one point |
| 11 | Missing checkpoint | Value absent | Must → REVIEW |
| 12 | Gradual degradation | Monotone drift, several shapes | Core latent defect |
| 13 | Accelerating degradation | Slow early, fast late | Hard at T24 by design |
| 14 | Non-power-law degradation | e.g. logistic / saturating / step-then-linear | Shape not assumed by any detector |
| 15 | Sudden change | Jump between 96h and 168h | Undetectable at T24 — report, don't hide |
| 16 | Wrong-direction drift | Parameter degrades opposite to configured direction | Direction handling |
| 17 | Parameter-specific behaviour | Different shapes for current-like vs delay-like | Multi-parameter |
| 18 | Heteroscedastic noise | Noise ∝ level | Interval adaptivity |
| 19 **H** | Unseen family A | Defined and sealed by a person not tuning detectors | Anti-circularity |
| 20 **H** | Unseen family B | As above, different mechanism | Anti-circularity |

## 4. Anti-circularity rules (from C-11, CLAUDE §5/§6)

1. No detector or safety-slope rule may be written from the generator's
   equations. Example of what is forbidden: generate defects as t^1.5 and
   detect "exponent > 1".
2. Degradation shapes include families no method was designed around (14, 19, 20).
3. Families 19–20 are specified in a sealed config (hash recorded in the
   experiment log) before any detector code exists, and opened only for R-01.
4. Every result is reported over a **parameter sweep** (noise, prevalence,
   onset time, lot offset, lot size, contamination), not at one setting.
5. Prevalence is a parameter, never a claim about real defect rates.
6. Labels are computed by explicit rules on the generated values and stored
   separately (`label_spec_168h`, `label_safety_slope`, `scenario`);
   they are never features.
7. Seeds, config and commit recorded; filenames contain `synthetic`.

## 5. Open design questions (for the review)

| # | Question | Options |
|---|---|---|
| Q1 | Who defines held-out families 19–20? | **Decided and done:** written outside the repository by the team, not by Claude; only the SHA-256 commitment is in the repo (§7) |
| Q2 | Level distributions | Log-normal for current-like; normal for delay-like (assumptions) |
| Q3 | Drift allowance Δ used to label | ADR-002 accepted: Δ_allow swept over a pre-registered grid |
| Q4 | Lot sizes / number of lots | Swept; minimum set by split needs (train/val/cal/test lots) |
| Q5 | Should NASA-derived shapes inform any family? | Only qualitatively, documented, not fitted |

## 6. Review checklist

- [x] Design approved — by the user, 2026-09-26 (Decision 5)
- [x] Families 1–18 have a written mechanism and stated assumptions (§3); detailed distributions are written into the generator config in P1
- [x] Held-out families 19–20 written and sealed outside the repository (§7) — 2026-09-26
- [x] Sweep grids fixed before any generator or detector code exists (§8) — 2026-09-26
- [x] Label rules fixed and linked to ADR-002 (`label_spec_168h`, `label_safety_slope`)

## 7. Sealing procedure for held-out families 19–20

1. The owner writes both families (mechanism, parameters, prevalence) in a config
   file kept **outside the repository** and not shared with anyone writing detectors (including Claude).
2. The owner records the file's SHA-256 and the date in the table below.
3. The file is handed over only when R-01 runs; its hash is checked first, and the
   run log records the match.
4. If the families are ever seen by a detector author before R-01, record that here;
   R-01 then no longer counts as a held-out test.

| Owner | Date sealed | SHA-256 | Opened for R-01 |
|---|---|---|---|
| Team (kept outside the repository; not Claude) | 2026-09-26 | `1a7de27638222f0dad35c492080577e6abedfc23b2466f66227ee6cff6482f74` | No |

Integrity rules for everyone working in this repository (including Claude): do not
access, search for, infer or recreate the held-out specification; do not create
families 19 or 20; development family names never use the numbers 19 or 20.

## 8. Pre-registered sweep grids (fixed 2026-09-26, before any generator code)

These grids are fixed **before** the generator exists and before any detector
result is seen. They may be extended later only with a dated note; values are
never removed after results are known.

### 8.1 Drift allowance Δ_allow (ADR-002 sensitivity; used to compute `label_safety_slope`)

| Kind | Grid | Basis |
|---|---|---|
| Relative (fraction of \|V₀\|) | 0.02, 0.05, 0.10, 0.15, 0.20, 0.30 | Brackets the ±15 % relative drift values used in ESCC detail specifications (S-03) |
| Absolute, current-like parameter (µA, assumed unit) | 0.25, 0.5, 1, 2, 4 | Geometric grid; assumption |
| Absolute, delay-like parameter (ns, assumed unit) | 0.025, 0.05, 0.1, 0.2, 0.4 | Geometric grid; assumption |

### 8.2 Generator sweeps (robustness experiment R-02; one factor at a time from the base config)

| Factor | Grid (multiplier or value) |
|---|---|
| Measurement-noise multiplier | 0.5, 1, 2, 4 |
| Anomaly-prevalence multiplier (non-contaminated lots) | 0.5, 1, 2 |
| Contaminated-lot anomaly fraction | 0.10, 0.20, 0.30, 0.40 |
| Components per lot | 6, 12, 25, 50, 100 |
| Lot-to-lot offset SD multiplier | 0.5, 1, 2 |
| Late-drift onset window (h) | 30–60, 60–100, 100–140 |
| Seeds per setting | base seed, base + 1, base + 2 |

The base configuration is `configs/synthetic/development_v1.yaml`.
