# Research Synthesis — PS 26170

Status: Draft · Last updated: 2026-09-26

Synthesis of R1–R4 (see [claim-register.md](claim-register.md) for sources and
the classification of every individual claim). Labels: `[SF]` source fact ·
`[PA]` prior art · `[EI]` engineering interpretation · `[PR]` proposal ·
`[AS]` assumption · `[UV]` unverified · `[GAP]` gap · `[NC]` do not claim.

> ~~**Read this first.** The official PS 26170 text is not in the repository and
> none of the sources quotes it in full. Everything under "PS" below is known
> second-hand through R2 and R3. Obtaining the official text is blocker B-01.~~
>
> **Updated 2026-09-26 — official PS text obtained (R0):**
> [ps-analysis/official-ps-26170.md](ps-analysis/official-ps-26170.md). Part I
> below was written from R2/R3 and is kept; the verified corrections are in
> **Part 0**, which overrides Part I where they differ.

## Part 0 — Verified against the official PS (R0)

| Topic | Earlier synthesis | Verified (R0) |
|---|---|---|
| Module B inputs | 0h+24h (R3) vs 0/24/96h (R2), unresolved | **Value_0h + Value_24h → Value_168h** |
| Early rejection | Safety slope, undefined | Predicted 168h drift rate > "calculated safety slope"; **calculation not specified** |
| Checkpoints | 0/24/96/168h (R2) | "intervals **like** 0h, 24h, 96h, and 168h" — examples |
| Parameters | Unknown / IDDQ (R2) | e.g. Iddq, leakage currents, **propagation delays** |
| Temperature | 125 °C (R2) | "e.g., 125°C" — example |
| Lot example | 50 µA / 10 µA (R2) | lot average 10 µA, part **45 µA**, datasheet max 50 µA |
| FN | Catastrophic / "zero FN" (R2) | "catastrophic, penalizing teams that let bad parts escape" |
| Evaluation | Various proposals | **Anomaly Detection Score** (formula not given), **MAE on Value_168h vs hidden ground truth**, **Explainability** |
| Dataset | None found (R3) | Official entry's Dataset Link is **empty**; evaluators hold hidden ground truth — [OFFICIAL DATASET NOT FOUND](datasets/official-dataset-verification.md) |
| Standards | AEC-Q001, JEDEC, ISO/AS9100 (R2) | **None named** in the PS |
| PASS/REVIEW/REJECT, uncertainty | Proposals | Not in the PS — remain proposals |

Consequences `[EI]`:

- The T96 prediction path in the architecture is **not** Module B. If kept, it
  is an extension and must be reported separately.
- MAE on Value_168h is an official scoring metric → E4 must report MAE as its
  primary prediction metric.
- The safety-slope and drift-rate definitions are now **our** documented design
  decisions (not blocked on the PS text), and they should be confirmed with
  organisers if possible.
- Parameters may have different units and drift directions (currents vs
  delays); the schema and limit checks must not assume µA or an upper-only limit.

---

## Part I — Established findings

### 1. PS objective

- `[SF]` (R2, R3) Detect burn-in components that are abnormal even though they
  pass absolute (datasheet) limits, and predict their future (168h) state early.
- `[SF]` (R3) Two modules:
  - **Module A** — dynamic, population/lot-relative anomaly detection.
  - **Module B** — early prediction of `Value_168h` from `Value_0h` and
    `Value_24h`, with early rejection when predicted drift exceeds a safety slope.
- `[SF]` (R2, R3) False negatives are catastrophic; explainability is evaluated.

### 2. The actual engineering problem

`[EI]` The task is not "classify bad components". It is:

> Identify components that currently **pass** specification but whose
> behaviour is **inconsistent with their peers** and/or whose **early trajectory
> indicates future degradation**, from **very few measurements**, while keeping
> **escapes (false negatives) near zero** and the **manual review load
> manageable**, and explain every decision quantitatively.

Three facts make this harder than generic anomaly detection:

1. **Lot-to-lot variation** `[EI]` — "normal" differs between lots, so a single
   global threshold is either too loose (misses outliers in tight lots) or too
   tight (floods review in high lots).
2. **Sparse time** `[SF]` (R2) — 4 checkpoints (0/24/96/168h), 2 of which
   (0h, 24h) may be all that is available for the early prediction `[SF]` (R3).
3. **Asymmetric cost** `[SF]` — a missed latent defect is far worse than a
   false alarm, but false alarms consume engineer time.

### 3. Why static screening can miss failures

`[EI]` A fixed limit tests only "is the value above X now?". It ignores:
where the value sits within its lot (a part at 35 on a limit of 50 passes even
if its lot sits near 8 — illustrative numbers from R2), how fast it is moving,
and whether the movement is accelerating. The latent-defect concept (`[EI]`,
D-01) is exactly a part whose *current* value is acceptable but whose
*behaviour* is not.

### 4. Input requirements (known and unknown)

| Input | Status |
|---|---|
| Per-component values at 0h, 24h, 96h, 168h | `[SF]` (R2), names `[UV]` |
| Component ID, Lot ID | `[SF]` implied by lot-relative requirement; field names `[UV]` |
| Wafer ID, device family, temperature | `[PR]` (R2 §H, R3 §9) — not established as PS inputs |
| Spec limits (min/max) | `[SF]` implied by "absolute limit"; one- vs two-sided `[GAP]` |
| Number of parameters per component | `[GAP]` — single parameter vs multiple unknown |
| Failure labels | `[GAP]` — definition and availability unknown |
| Safety slope value | `[GAP]` |

### 5. Temporal structure

- `[SF]` (R2) 4 checkpoints, unequally spaced (24h, 72h, 72h gaps).
- `[EI]` Unequal spacing matters: raw differences between checkpoints are not
  comparable slopes; divide by elapsed time.
- `[EI]` With 0h+24h only, a trajectory has one increment — enough for level and
  one drift rate; **not** enough for curvature. Curvature/acceleration needs 96h.
- `[EI]` This forces two decision checkpoints to be considered: **T24** (earliest
  PS-mandated prediction) and **T96** (more information, later decision).

### 6. Lot-relative behaviour

- `[PA]` (verified 2026-09-26, S-01) Dynamic Part Average Testing sets limits per lot/wafer: median ± 6·IQR/1.35.
- `[SF]` Robust z-score with MAD is a standard robust outlier statistic (D-07).
- `[EI]` Lot-relative scoring should apply to **both the level and the drift**:
  a part can have a normal 0h value and an abnormal 0→24h increment.
- `[EI]` Known failure modes: MAD = 0 (quantised measurements), small lots,
  contaminated lots (many defects), bimodal lots (mixed wafers). R2 flags
  bimodality (M-07).
- `[PR]` (R2) Also compare against historical device-family distribution to
  detect a bad lot. Requires cross-lot history — availability `[GAP]`.

### 7. Anomaly detection

- `[EI]` Candidate detectors, simplest first: spec limit → robust z (level) →
  robust z (drift) → multivariate robust distance → Isolation Forest (as a
  comparator, not a default).
- `[EI]` (M-01) Autoencoders/LSTMs are poorly matched to 4 points.

### 8. Trajectory analysis

- `[EI]` Features available at T24: Δ₂₄ = v24 − v0, relative drift Δ₂₄/|v0|,
  lot-relative z of Δ₂₄.
- `[EI]` Features available at T96: segment slopes s₁ = (v24 − v0)/24,
  s₂ = (v96 − v24)/72, slope change s₂ − s₁ (or ratio), lot-relative z of each.
- `[EI]` (M-02) Per-component power-law fitting y₀ + A·tⁿ is not identifiable at
  T24 and has zero residual degrees of freedom at T96. The physics idea is
  usable only with population-level shape (e.g. fitting the exponent per lot or
  device family and scoring deviations).

### 9. 168h prediction

- `[SF]` (R3) Mandatory: predict `Value_168h` from `Value_0h`, `Value_24h`.
- `[EI]` Required baselines: persistence (ŷ = v24), linear extrapolation,
  lot-median-increment model, linear regression on (v0, v24).
- `[EI]` (M-05) Tree ensembles do not extrapolate — the highest-risk parts are
  exactly the ones with extreme values. Any tree model must be compared on the
  tail, not only on average error.

### 10. Uncertainty

- `[PA]` (D-16) Split conformal prediction: finite-sample **marginal** coverage
  under exchangeability.
- `[EI]` Lot structure breaks exchangeability across lots; calibration should be
  done with held-out **lots**, and coverage reported per lot.
- `[EI]` Simplest viable approach: empirical residual quantiles from calibration
  lots (which is split conformal with absolute residual score). Adaptive widths
  (e.g. conformalised quantile regression) only if fixed widths prove too wide
  or unevenly covering.

### 11. False-negative handling

- `[EI]` Handle through: (a) conservative thresholds chosen on validation data
  at a target recall; (b) a REVIEW state for uncertain/suspicious cases;
  (c) fail-safe REVIEW on missing/invalid data.
- `[NC]` "Zero false negatives" as a claim. Only "zero observed escapes on
  dataset X under conditions Y" if measured.

### 12. Explainability

- `[SF]` Explicitly evaluated (R3).
- `[EI]` Because every proposed layer is a transparent statistic or simple
  model, explanations can be the actual decision evidence (values, lot median,
  robust z, slopes, predicted value, interval, fired rule) rather than post-hoc
  attribution (SHAP) of a black box.
- `[PR]` (R2) Trajectory map: component path, lot envelope, spec limit, predicted
  168h interval.

### 13. Human review

- `[PA]` (D-15) Three-way decisions / reject option.
- `[EI]` REVIEW is a queue with a cost; review rate is a first-class metric.

---

## Part II — Proposed design (not established)

`[PR]` Architecture (provisional, see [ADR-001](../decisions/ADR-001-initial-architecture.md)):

Data quality gate → absolute spec check → lot-relative scoring (level + drift)
(incl. trajectory features) → 168h prediction → prediction interval (conditional) → ordered
decision rules → PASS/REVIEW/REJECT → evidence-based explanation. (Revised 2026-09-26, ADR-001 Rev. 1.)

Two operating checkpoints `[PR]`: **T24** (0h+24h available; Module B early
decision) and **T96** (0h/24h/96h). 168h is used only as ground truth for
prediction and as the final screening point.

Candidate methods and prior art are expanded in
[prior-art/literature-review.md](prior-art/literature-review.md) and
[../architecture/](../architecture/system-architecture.md).

## Part III — Dataset strategy (summary)

Three strictly separated categories (see [datasets/dataset-strategy.md](datasets/dataset-strategy.md)):

1. Official SIH/PS data — **none located** `[SF]` (R3).
2. External public — NASA MOSFET, NASA IGBT (verified, downloaded, inspected) — useful for
   degradation-prediction realism, **not** lot-structured, **not** SIH data.
3. Synthetic PS-shaped — required for the lot + 4-checkpoint structure; must be
   generated from documented assumptions and never presented as real.

## Part IV — Evaluation strategy (summary)

Grouped-by-lot splits; untouched final test lots; metrics per
[experiments/evaluation-protocol.md](experiments/evaluation-protocol.md);
6-step ablation per [experiments/ablation-plan.md](experiments/ablation-plan.md).
All results: **TBD — experiment not yet executed.**

## Part V — Risks

Moved (2026-09-26) to the single register [drawbacks-and-risks.md](drawbacks-and-risks.md).

## Part VI — Limitations of the research base

- R2's citations cannot be resolved (no bibliography).
- R1 contains no domain content.
- R2 contains unmeasured results that must not be reused (X-01…X-07).
- ~~No prior-art paper was opened; no dataset was inspected.~~ Updated
  2026-09-26: NASA datasets inspected; prior art partly verified
  ([prior-art/literature-review.md](prior-art/literature-review.md), sources S-01…S-17).
  Remaining UV items are listed there.

## Part VII — Open questions

Resolved: Module B inputs (0h + 24h, R0). Open questions are now tracked as
GAP-01…GAP-10 in [drawbacks-and-risks.md](drawbacks-and-risks.md) Part A.

## Part VIII — Verified prior-art update (2026-09-26)

- `[PA]` S-01: DPAT = median ± 6·IQR/1.35 per lot (AEC-Q001 Rev-D). Confirms D-06 correction.
- `[PA]` S-02/S-03: ESCC burn-in screening uses per-parameter drift limits
  relative to the 0h value, alongside absolute limits — the closest verified
  analogue of the PS safety slope (ADR-002).
- `[PA]` S-06: per-device pre/post burn-in comparison for outliers is patented (AMD, 2011).
- `[PA]` S-04/S-05: ML for burn-in exists at batch level before burn-in and at
  lot level from process data — neither uses sparse in-burn-in parametric trajectories.
- `[EI]` Consequence: lot-relative drift screening is **not** a differentiator
  (§6 above "lot-relative scoring should apply to both level and drift" remains
  a sound design choice, not a novelty). See [prior-art/novelty-boundaries.md](prior-art/novelty-boundaries.md).
