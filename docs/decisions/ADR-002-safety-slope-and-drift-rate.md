# ADR-002 — Safety Slope and Drift-Rate Definition

Status: Accepted · Date: 2026-09-26 · **DECISION STATUS: CONFIRMED BY USER 2026-09-26 — option (1): DR-1 + SS-G with SS-D backstop** (see §11)

Sources: R0 (official PS), S-02/S-03 (ESCC), S-01 (AEC-Q001) — see
[literature-review.md](../research/prior-art/literature-review.md) §1.
Related gaps: GAP-01, GAP-02 in [drawbacks-and-risks.md](../research/drawbacks-and-risks.md).

## 1. Problem

Module B must flag a component for early rejection when "the predicted 168h
drift rate exceeds a calculated safety slope" (R0). Neither quantity is defined.
Until both are fixed, the early-rejection rule, its proxy label
(`label_safety_slope`), experiment E4(b) and the explanation text are undefined.

## 2. Official PS wording (R0, verbatim)

> "Build a predictive regression model that takes Value_0h and Value_24h as
> inputs and forecasts Value_168h. If the predicted 168h drift rate exceeds a
> calculated safety slope, the system flags the component for early rejection."

## 3. What is unspecified

| Item | Unspecified |
|---|---|
| Drift rate | Window (0→168h? 24→168h? instantaneous at 168h?), absolute vs relative, units |
| Safety slope | Formula, inputs, value, units, per-parameter or global, per-lot or fixed, one- or two-sided |
| "calculated" | From what: datasheet limit? lot data? engineering Δ? |
| Direction | Parameters such as propagation delay may degrade in either direction |

## 4. Primary-source evidence found (2026-09-26)

| # | Evidence | Label |
|---|---|---|
| E-1 | ESCC 9000 Issue 10 §6.2.2: "A component shall be counted as a parameter drift failure if the changes during High Temperature Reverse Bias Burn-in or during Power Burn-in are larger than the drift values (Δ) specified." §8.15/8.16: "Drift shall be related to the initial measurement." | `[SF]` S-02 |
| E-2 | ESCC 9202/045 Issue 6 §2.4 (CMOS 4049UB): quiescent current IDD drift limit ±75 nA **and** absolute limit 500 nA max; output currents drift ±15 % (relative); threshold voltages ±0.3 V. Both drift and absolute limits "shall not be exceeded". | `[SF]` S-03 |
| E-3 | AEC-Q001 Rev-D defines lot-relative limits (median ± 6·IQR/1.35) for single test insertions; it defines no drift or slope limit. | `[SF]` S-01 |
| E-4 | No source found that defines a "safety slope" for burn-in by that name. | `[GAP]` |

`[EI]` Space-component practice (E-1, E-2) already screens burn-in by **drift from
the 0h value against a per-parameter allowance**, alongside the absolute limit.
This is the closest verified analogue to the PS's rule. The PS's addition is
that the drift is **predicted** at 24h instead of measured at the end.

## 5. Drift-rate candidates

| ID | Definition | Units | Notes |
|---|---|---|---|
| DR-1 | r̂ = (Ŷ₁₆₈ − V₀) / 168 h | parameter unit / h | Literal "168h drift rate"; matches ESCC "drift related to initial measurement" |
| DR-2 | r̂ = (Ŷ₁₆₈ − V₀) / (168 h · \|V₀\|) | 1/h (or %/h) | Relative; unstable when V₀ ≈ 0 |
| DR-3 | r̂ = (Ŷ₁₆₈ − V₂₄) / 144 h | unit / h | Future-segment slope; ignores 0→24h change already seen |
| DR-4 | Instantaneous slope at 168h | unit / h | Needs a curve shape; not identifiable from two points (M-02). Rejected |

`[EI]` Under DR-1, "r̂ > s" is algebraically identical to "predicted 168h change
Ŷ₁₆₈ − V₀ > 168·s". The slope phrasing and a predicted-Δ phrasing are the same
rule; the slope form is kept only because it is the PS's wording.

## 6. Safety-slope candidates

| ID | Name | Formula (illustrative symbols) | Inputs | "Calculated" from |
|---|---|---|---|---|
| SS-A | Simple fixed slope | s = constant | config | Nothing (not really "calculated") |
| SS-B | Normalised slope | s = p · \|V₀\| / 168 | V₀, p (fraction) | Component's own 0h value |
| SS-C | Lot-relative slope | s = median(r_lot) + k · robust_scale(r_lot) | current-lot drift rates at 24h | Current lot |
| SS-D | Spec-margin slope | s_i = (L − V₀,i) / 168 | datasheet limit L, V₀ | Datasheet limit + 0h value |
| SS-E | Empirical (training) slope | s = q-quantile of drift rates of non-defective training components | labelled training lots | Historical data |
| SS-F | Robust percentile of healthy population | as SS-E but robust / per device family | historical lots | Historical data |
| SS-G | Engineering drift allowance (ESCC-style) | s = Δ_allow / 168, Δ_allow absolute or relative (%·V₀) per parameter | per-parameter Δ from config/detail spec | Engineering specification (E-1, E-2) |

## 7. Assessment

| ID | Advantages | Disadvantages / failure modes | Sensitivity |
|---|---|---|---|
| SS-A | Trivial, explainable | Arbitrary; one number for all parameters/units | Entire reject set moves with one number |
| SS-B | Scale-free across parameters | Breaks at V₀ ≈ 0; relative drift may not be what matters physically | High for small V₀ |
| SS-C | Adapts per lot; needs no labels | **Duplicates Module A**; a lot that degrades as a whole looks normal (bad-lot problem); depends on lot size and contamination; not a fixed engineering limit | High for small / contaminated lots |
| SS-D | Uses only the datasheet limit the PS mentions; per-component; clearly "calculated" | Equivalent to "predicted Value_168h exceeds the limit" — **cannot flag in-spec latent drift**, which is the PS's core concern | Low; inherits prediction error near the limit |
| SS-E | Data-driven | Needs real labels (unavailable, GAP-05); on synthetic data it learns the generator (circularity) | High to labels and prevalence |
| SS-F | Robust version of SS-E | Same data problem; needs historical lots (U-15) | As SS-E |
| SS-G | Grounded in verified space-screening practice; independent of lot composition; per-parameter units; directly explainable to a QA inspector | Δ values for PS parameters are **not known** — must be configured, and on synthetic data are our assumption | Result depends on Δ; must be swept |

## 8. Validation experiment (part of E4 — defined, not run)

1. For each candidate pair (DR-x, SS-y) compute the early-rejection flag at T24
   from Ŷ₁₆₈ and the "true" flag from actual V₁₆₈ (same formula).
2. Report confusion matrix, recall, FPR, and flag rate per scenario, on
   held-out lots, per data category.
3. Sweep Δ_allow (SS-G), k (SS-C) and q (SS-E) over pre-registered grids;
   report curves, not one tuned point.
4. Report agreement between candidates (which components each flags).
5. Bad-lot scenario (whole lot drifts) reported separately — expected to
   separate SS-C from SS-G.

Result: TBD — experiment not yet executed.

## 9. Recommendation (proposal only — not adopted)

`[PR]`

- **Drift rate: DR-1** (absolute, 0→168h, per hour; one-sided in the
  configured degradation direction, two-sided if configured). Report DR-2 as
  a secondary view where V₀ is well away from zero.
- **Safety slope: SS-G** (per-parameter drift allowance Δ_allow / 168h,
  absolute or relative per parameter, from `configs/`), **combined with SS-D**
  as a backstop (predicted limit crossing). Flag if either is exceeded.
- **SS-C** evaluated only as a comparator in E4, because it overlaps Module A
  and fails on bad lots.
- Δ_allow has **no default chosen by us**; synthetic experiments sweep it.
- Ask the organisers (sih@aicte-india.org) how the safety slope and drift rate
  are defined in the hidden evaluation (GAP-01/02/10).

Why: SS-G is the only candidate supported by a verified screening
specification, is independent of lot composition (unlike SS-C), catches in-spec
drift (unlike SS-D), and needs no labels (unlike SS-E/F).

## 10. Decision status (history)

Options put to the team on 2026-09-26: (1) SS-G + SS-D with DR-1
(recommended); (2) SS-C (lot-relative) with DR-1; (3) research further.

## 11. Decision

**Option (1) confirmed by the user, 2026-09-26.**

| Item | Decision |
|---|---|
| Drift rate | **DR-1**: r̂ = (Ŷ₁₆₈ − V₀) / 168 h, in parameter units per hour. Signed in the parameter's configured degradation direction; two-sided if configured. DR-2 (relative) may be reported as a secondary view only |
| Safety slope | **SS-G**: s = Δ_allow / 168 h, where Δ_allow is a per-parameter drift allowance in `configs/`, either absolute (units) or relative (fraction of \|V₀\|) |
| Backstop | **SS-D**: flag if Ŷ₁₆₈ crosses the datasheet limit |
| Early-rejection flag | r̂ > s **or** Ŷ₁₆₈ beyond the datasheet limit. How the prediction interval turns this into REJECT vs REVIEW is decided with the decision engine (E5/E6), not here |
| Δ_allow value | **No default chosen.** Synthetic experiments sweep a pre-registered grid; official values only if organisers or a detail specification provide them |
| Comparator | SS-C (lot-relative slope) evaluated in E4 as a comparator only |
| Proxy label | `label_safety_slope`: actual (V₁₆₈ − V₀)/168 h > s, or V₁₆₈ beyond the datasheet limit — same formulas, using measured V₁₆₈ |
| Wording | "drift allowance in the style of ESCC space-component drift limits"; never "ESCC compliant" |

Still open (not blocking): confirm with organisers how they compute the drift
rate and safety slope in the hidden evaluation (GAP-01/02/10). If they reply
with a different definition, supersede this ADR.

Note 2026-09-26: the team decided not to contact the organisers (ADR-003 amendment), so this definition stands unless official data or text later defines the slope.

Consequences: FR-09, data-dictionary `label_safety_slope`, glossary,
decision-engine R2/R3 and GAP-01/02 updated on 2026-09-26.
