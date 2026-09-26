# Synthetic Data Design (for review — nothing generated)

Status: Draft — **requires design review before any generator is implemented** · Last updated: 2026-09-26

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
| Q1 | Who defines held-out families 19–20? | A team member not writing detectors |
| Q2 | Level distributions | Log-normal for current-like; normal for delay-like (assumptions) |
| Q3 | Drift allowance Δ used to label | ADR-002 accepted: Δ_allow swept over a pre-registered grid |
| Q4 | Lot sizes / number of lots | Swept; minimum set by split needs (train/val/cal/test lots) |
| Q5 | Should NASA-derived shapes inform any family? | Only qualitatively, documented, not fitted |

## 6. Review checklist (must be signed off before implementation)

- [ ] Every family has a written mechanism and stated assumptions
- [ ] Held-out families sealed with hash
- [ ] Sweep grids fixed before any detector result is seen
- [ ] Label rules fixed and linked to ADR-002
- [ ] Reviewer name and date recorded here
