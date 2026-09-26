# PS Gaps, Drawbacks and Risks (Open-Decision Register)

Status: Draft · Last updated: 2026-09-26

Authoritative register of (A) what the official PS leaves undefined and (B) the
weaknesses of our approach. Replaces the risk tables formerly in
research-synthesis Part V and assumptions-and-constraints §4.

Status values: **Open** · **Proposal pending confirmation** · **Decided (ADR-x)** · **Accepted limitation**.

---

## Part A — PS gaps (GAP-01 … GAP-10)

### GAP-01 Safety-slope calculation unspecified

| Field | Content |
|---|---|
| Problem | R0: "a calculated safety slope" — no method, value or units |
| Why it matters | Defines Module B early rejection and its label |
| Evidence | R0; ESCC drift limits (S-02/S-03) as closest practice |
| Current assumption | ADR-002: Δ_allow/168 h + datasheet-limit backstop |
| Possible solutions | SS-A…SS-G in [ADR-002](../decisions/ADR-002-safety-slope-and-drift-rate.md) |
| Advantages | See ADR-002 §7 |
| Disadvantages | See ADR-002 §7 |
| Experiment required | E4 slope-candidate comparison + Δ sweep (ADR-002 §8) |
| Decision required | Choose candidate (Decision 1) |
| Current status | **Decided (ADR-002)** 2026-09-26 — SS-G + SS-D; Δ_allow unset (swept); organiser confirmation still desirable |

### GAP-02 Drift-rate formula unspecified

| Field | Content |
|---|---|
| Problem | "predicted 168h drift rate" — window, absolute/relative, units undefined |
| Why it matters | Same rule as GAP-01; units must match the slope |
| Evidence | R0; ESCC "drift related to the initial measurement" |
| Current assumption | ADR-002: (Ŷ₁₆₈ − V₀)/168 h |
| Possible solutions | DR-1…DR-4 (ADR-002 §5) |
| Advantages / Disadvantages | ADR-002 §5 |
| Experiment required | Part of E4 |
| Decision required | Together with GAP-01 |
| Current status | **Decided (ADR-002)** 2026-09-26 — DR-1 |

### GAP-03 Anomaly Detection Score formula unspecified

| Field | Content |
|---|---|
| Problem | Only "FN catastrophic, penalised" is stated |
| Why it matters | Cannot optimise for or predict the official score |
| Evidence | [anomaly-detection-score.md](ps-analysis/anomaly-detection-score.md) |
| Current assumption | Recall/FNR dominates; FP cost unknown |
| Possible solutions | Report full metric set; conservative operating point; ask organisers |
| Advantages | Honest; covers plausible formulas |
| Disadvantages | No single target to tune |
| Experiment required | E6 recall–review curves |
| Decision required | Operating-point policy (later decision) |
| Current status | Open |

### GAP-04 Official dataset unavailable

| Field | Content |
|---|---|
| Problem | Dataset Link empty; hidden ground truth |
| Why it matters | No real validation possible |
| Evidence | [official-dataset-verification.md](datasets/official-dataset-verification.md) |
| Current assumption | Synthetic (Module A/B) + NASA external (prediction methodology) |
| Possible solutions | Synthetic per [synthetic-data-design.md](datasets/synthetic-data-design.md); ask organisers for sample data |
| Advantages | Controlled scenarios |
| Disadvantages | Circularity; no real performance claim |
| Experiment required | R-01, R-02 |
| Decision required | — |
| Current status | **Decided (ADR-003)** 2026-09-26 — accepted limitation; organisers not contacted (ADR-003 amendment) |

### GAP-05 Failure-label definition unknown

| Field | Content |
|---|---|
| Problem | "defective part" not defined |
| Why it matters | Every detection metric depends on it |
| Evidence | R0 |
| Current assumption | Proxy labels (A-06): spec violation at 168h; drift allowance exceeded at 168h |
| Possible solutions | Report per label type; scenario tags on synthetic data |
| Advantages | Transparent |
| Disadvantages | Proxies may differ from evaluator labels |
| Experiment required | All E1–E6 per label |
| Decision required | — |
| Current status | **Decided (ADR-004)** 2026-09-26 — primary `label_safety_slope`; organiser definition still desirable |

### GAP-06 Number / type of parameters unknown

| Field | Content |
|---|---|
| Problem | Examples: Iddq, leakage currents, propagation delays |
| Why it matters | Units, degradation direction, one/two-sided limits |
| Evidence | R0 |
| Current assumption | One parameter per row; direction configured per parameter (A-09, A-12) |
| Possible solutions | Long-format schema; per-parameter config |
| Advantages | Handles any count |
| Disadvantages | Multivariate interactions ignored initially |
| Experiment required | Synthetic multi-parameter scenario |
| Decision required | No (schema proposal) |
| Current status | Open |

### GAP-07 Lot / component / wafer schema unknown

| Field | Content |
|---|---|
| Problem | Only Value_0h/24h/168h named; lot implied |
| Why it matters | Module A needs lot IDs |
| Evidence | R0 |
| Current assumption | `lot_id` exists (A-04) |
| Possible solutions | Mapping layer; if no lot ID, fall back to whole-dataset peer group and state limitation |
| Advantages | Robust to schema |
| Disadvantages | Fallback weakens Module A |
| Experiment required | E0 on any real data |
| Decision required | No |
| Current status | Open |

### GAP-08 Operating review-rate constraint unknown

| Field | Content |
|---|---|
| Problem | Acceptable REVIEW volume unknown (U-13) |
| Why it matters | Sets operating point |
| Evidence | None |
| Current assumption | None |
| Possible solutions | Recall-first target R* + full curve ([ADR-005](../decisions/ADR-005-operating-point.md)) |
| Advantages | No hidden tuning |
| Disadvantages | No single headline number |
| Experiment required | E6 |
| Decision required | R* value before E6 |
| Current status | **Decided (ADR-005)** 2026-09-26 — recall-first with full curve; R* to be pre-registered |

### GAP-09 Meaning of "early rejection" operationally

| Field | Content |
|---|---|
| Problem | Is the part removed from burn-in at 24h, or only flagged? |
| Why it matters | Claims about time saved; whether REJECT or REVIEW is appropriate at 24h |
| Evidence | R0 says "flags the component for early rejection" |
| Current assumption | Output is a flag / recommendation (A-10, A-11) |
| Possible solutions | Present as decision support; no "hours saved" claim |
| Advantages | Safe |
| Disadvantages | Weaker impact story |
| Experiment required | None |
| Decision required | No |
| Current status | Accepted limitation |

### GAP-10 Hidden evaluation behaviour unknown

| Field | Content |
|---|---|
| Problem | Format, checkpoint, module scored, binary/multi-class all unknown |
| Why it matters | Output format mismatch could zero a score |
| Evidence | R0, S-16, S-17 |
| Current assumption | Per-component Value_168h prediction + binary flag + explanation |
| Possible solutions | Produce all three; binary mapping of REVIEW configurable |
| Advantages | Covers likely formats |
| Disadvantages | — |
| Experiment required | None |
| Decision required | No |
| Current status | Accepted risk — organisers not contacted (ADR-003 amendment) |

---

## Part B — Drawbacks and risks of our approach

Compact form; all rows use the required fields. "Exp." = experiment required.

| # | Problem | Why it matters | Evidence | Current assumption | Possible solutions | Advantages | Disadvantages | Exp. | Decision | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| D-01 | Hidden ground truth | Our numbers cannot predict the official score | R0 | Synthetic/external only | Robustness experiments; clear labelling | Honest | Weak evidence | R-01/02 | No | Accepted limitation |
| D-02 | Sparse observations (2 points at T24) | No curvature; prediction weak | R0 | Linear-type predictors | Population/lot increment models; hierarchical priors (S-15) | Stable | Cannot capture late acceleration | E4 | No | Open |
| D-03 | Small lots | Robust scale unstable (AEC notes 1.35 inexact n < 20) | S-01 | min lot size config | Pool with historical lots; REVIEW | Safe | Review load | E2 sens. | Later | Open |
| D-04 | MAD = 0 / quantised data | Division by ~0 | glossary | Scale floor | Resolution floor; IQR fallback | Robust | Floor is a parameter | Unit tests, E2 | No | Open |
| D-05 | Contaminated lot | Outliers masked | M-06 | Majority healthy (A-07) | Lot-level flag; fixed drift allowance (SS-G) independent of lot | Catches bad lots | — | E2 sens. | No | Open |
| D-06 | Bimodal lot | False flags | M-07 | — | Gap/histogram check; wafer grouping | Simple | Needs wafer ID | E2 sens. | No | Open |
| D-07 | Bad-lot problem (whole lot drifts) | Lot-relative methods see it as normal | EI | — | Absolute drift allowance + spec backstop | Covers it | Needs Δ | ADR-002 §8 step 5 | With ADR-002 | Open |
| D-08 | Cross-lot shift | Model trained on some lots fails on others | S-11 | Lot-grouped splits | Lot-relative features; group-aware calibration | — | — | E4/E5 | No | Open |
| D-09 | Temporal leakage | Inflated results | CLAUDE §7 | Availability matrix | Automated tests | — | — | Tests | No | Open |
| D-10 | Synthetic circularity | Inflated results | C-11 | Design rules | [synthetic-data-design.md](datasets/synthetic-data-design.md) held-out families sealed by a non-detector author | — | Cost | R-01 | Design approved 2026-09-26 | Open until families 19–20 sealed |
| D-11 | External-domain mismatch (NASA) | Misleading transfer | external-dataset-compatibility | Methodology only | Keep separate | — | Small n | R-04 | No | Accepted limitation |
| D-12 | Extrapolation 24h → 168h (7×) | Large errors on high-risk tail; trees cannot extrapolate (M-05) | EI | Simple models first | Tail error metric; PI | — | — | E4 | No | Open |
| D-13 | MAE vs FN tension | MAE rewards average accuracy; FN depends on the tail | R0 | Report both | Separate point predictor (MAE) and flag rule (interval-aware) | Both served | Two numbers to explain | E4/E5 | No | Open |
| D-14 | Uncertainty under lot shift | Coverage fails per lot | S-11, S-12 | Lot-level calibration | Report per-lot coverage; hierarchical conformal (S-11) | — | Needs many lots | E5 | Later | Open |
| D-15 | Review burden | Useless if everything → REVIEW | EI | — | Report curve; recall-first operating point (ADR-005) | — | — | E6 | Decided (ADR-005) | Open until E6 |
| D-16 | False rejection of good parts | Cost, yield | EI | — | Report FRR | — | — | E6 | No | Open |
| D-17 | Explainability quality | Evaluated by R0 | R0 | Rule-based evidence | Templates; QA-reader test | Faithful | Not SHAP-style visuals | E6 qual. | No | Open |
| D-18 | Parameter directionality | Delays/currents may degrade either way | R0 | Direction per parameter config | Two-sided rules | — | Config burden | Unit tests | No | Open |
| D-19 | Multiple parameters | Joint abnormality ignored | GAP-06 | One-at-a-time | Later: robust multivariate distance | Simple | Misses joint cases | Later | Later | Open |
| D-20 | Missing data | Silent PASS risk | NFR-01 | → REVIEW | Fail-safe | Safe | Review load | R-03 | No | Open |
| D-21 | Operational adoption | QA may not trust it | EI | Advisory only | Audit trail; override | — | — | — | No | Open |
| D-22 | Scalability | Unmeasured | — | Batch per lot, O(n) stats | Measure | — | — | NFR-07/08 | No | TBD — experiment not yet executed |
| D-23 | Reproducibility | Required | CLAUDE §8 | Config + seed + commit | Git repository with remote; branch per change (CLAUDE §26) | — | — | — | — | Resolved (git in place) |
| D-24 | Prior art overlaps core ideas | Weak novelty story | S-02, S-06 | Proposal wording | [novelty-boundaries.md](prior-art/novelty-boundaries.md) | Credible | Less "novel" | — | No | Accepted limitation |
| D-25 | Idea-submission deadline (30 Sep 2026) before any experiment | Idea PDF can contain no results | S-16, S-17 | — | Idea PDF states proposals + experiment plan only | Honest | — | — | Decided 2026-09-26 | Draft built (docs/presentation/idea-submission-content.md); team review + upload pending |
