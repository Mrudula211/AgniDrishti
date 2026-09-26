# Idea-Round Submission Content (SIH 2026, PS 26170)

Status: Draft for team review · Last updated: 2026-09-26 (Rev. 2 — diagram-first redesign) · Deadline: **30 Sep 2026**

Source text for the portal fields and the 6-slide official template (S-17).
Rules applied: no performance numbers (no experiment has run); proposals
labelled; originality wording per [novelty-boundaries.md](../research/prior-art/novelty-boundaries.md);
no numbers appear on the slides. The PS's own 10 / 45 / 50 µA illustration
(R0, verbatim) is kept only in the slide 2 speaker notes, attributed to the PS.

Deck: [sih2026-idea-agnidrishti.pptx](sih2026-idea-agnidrishti.pptx) ·
exported PDF: [sih2026-idea-agnidrishti.pdf](sih2026-idea-agnidrishti.pdf)
(6 slides; template headings and idea-detail pointers kept verbatim, as S-17
requires). Formulas and talk track are in each slide's speaker notes.
Before upload: replace `[TEAM ID]` on slide 1, then File → Export → PDF (the
portal accepts PDF only) and re-check all six pages.
If this text changes, update the deck to match (this file is the source of truth).

Story: **static screening → trajectory-aware screening.** One message per slide.

---

## Portal fields

**Idea title**

AgniDrishti — Lot-relative, drift-predictive and uncertainty-aware burn-in screening

**Idea description**

Static pass/fail limits let latent defects escape: a part can sit inside its
datasheet limit while being abnormal for its lot or drifting abnormally.
AgniDrishti is a proposed screening pipeline for burn-in parametric data. For
each lot at each checkpoint it (1) checks data quality, (2) applies the
datasheet limit, (3) scores every part against its own lot on both level and
drift using robust statistics (Module A), (4) predicts Value_168h from
Value_0h and Value_24h (Module B), (5) compares the predicted drift rate with
a safety slope derived from a per-parameter drift allowance, (6) attaches a
prediction interval calibrated on held-out lots, and (7) returns PASS /
REVIEW / REJECT with the exact numbers and rule behind each decision.
Uncertain or suspicious parts go to engineer REVIEW instead of being passed.
Methods are deliberately simple and transparent because each part has only a
few measurements; complex models are added only if they beat simple baselines
on held-out lots. Evaluation uses lot-grouped splits, leakage tests and an
ablation study on clearly labelled synthetic and public NASA data.

---

## Slide 1 — Title page (hierarchy only)

AgniDrishti · *Static screening → trajectory-aware burn-in screening* ·
PS ID 26170 · official PS title · Theme Smart Automation · Category Software ·
Team ID `[TEAM ID]` · Team Name Regnum Carya.

## Slide 2 — AgniDrishti / Proposed solution

Message: *static screening misses in-spec parts that are abnormal or drifting.*

- **Gap** — Conventional asks "Is it outside its specification NOW?":
  current value → datasheet limit → PASS/FAIL. Blind spot: a part can pass the
  absolute limit yet be abnormal for its lot or drifting (R0 latent defect).
- **AgniDrishti also asks** — abnormal vs lot peers? drifting abnormally? where
  at 168h? how uncertain? should an engineer review it?
- **Pipeline** — burn-in measurements → quality gate → absolute spec check →
  lot-relative health (**PS Module A**) → trajectory/drift → **0h + 24h → 168h
  forecast** → prediction uncertainty → PASS/REVIEW/REJECT (ordered rules incl.
  safety slope) → engineer evidence card. Banner: **PS MODULE B: Value_0h +
  Value_24h → Value_168h**.
- **How it addresses the problem** — one-line PS map (Module A → lot health ·
  Module B → forecast · doubt → REVIEW · explain → card); conceptual evidence
  card (no values: spec PASS · lot ABNORMAL · trajectory DEGRADING · ‹point
  forecast› · ‹prediction interval› · decision REVIEW · rule fired); and a
  unitless **trajectory sketch labelled "sketch · not data"**: lot band, dashed
  datasheet limit, part in spec at 0h/24h but leaving its lot, dashed forecast
  to 168h whose interval reaches the limit → REVIEW, never a silent PASS
  (decision-engine rules R3/R5).
- **Innovation and uniqueness** — "Combines static specification screening,
  lot-relative behaviour, early trajectory analysis, 168h forecasting,
  uncertainty and explainable review in one screening workflow." Individual
  techniques are established; the differentiation is the PS-specific
  integration and workflow. AEC-Q001 / ESCC 9000 are research foundations, no
  compliance claimed.

## Slide 3 — Technical approach

Message: *a simple, layered, testable pipeline; every layer must earn its place.*

- Technologies: Python 3.11+ · pandas · NumPy · pytest · robust stats
  (median · IQR · MAD) · least-squares regression · versioned YAML config ·
  offline, CPU-first. In use now:
  schema + data-quality gate (unit-tested); further libraries only if a
  baseline needs them.
- Architecture (two rows): burn-in data (CSV lot tables) → quality gate → absolute spec →
  Module A → trajectory/drift ↵ Module B (0h + 24h → 168h) → prediction
  interval → risk/decision engine → PASS/REVIEW/REJECT (+ binary flag) →
  evidence + audit record (FR-11, FR-12).
- Four blocks: lot anomaly detection (robust distance; Isolation Forest as ML
  comparator) · **ML forecasting ladder** (persistence → linear → regression
  on (v0, v24) → gradient-boosted trees; a model stays only if it lowers MAE
  on held-out lots) · uncertainty (a range, not one number) · explainability.
  Ladder and comparators are those planned in ml-pipeline.md (B0–B4, E2b).
- Validation strip: lot-grouped splits, frozen test lots, automated leakage
  tests, 6-step ablation. "All formulas are proposed engineering definitions
  where the PS is silent." Formulas (ADR-002, ml-pipeline) are in the notes.

## Slide 4 — Feasibility and viability

Message: *every known risk has a concrete mitigation; the build is incremental and started.*

| Challenge / risk | Strategy |
|---|---|
| Official dataset unavailable | Controlled synthetic PS-shaped data (always labelled) + external public aging data — methodology validation only + official-data-ready pipeline |
| Only Value_0h and Value_24h at decision time | Simple, stable predictors + prediction interval + REVIEW path |
| Lot contamination / mixed populations | Data-quality checks + robust (median-based) statistics |
| Whole lot may degrade together | Absolute safety backstop in addition to lot-relative analysis |
| Safety slope / Anomaly Score not defined in the PS | Configurable engineering definition + sensitivity analysis + organiser clarification |
| Data leakage / optimistic results | Lot-grouped splits + frozen test lots + no future features (automated tests) |
| Deployment in controlled facilities | Offline, CPU-first architecture; measurement data stays on site |

Feasibility cards: **technical** (robust stats + least-squares regression on
small lot tables, no GPU) · **operational** (reads checkpoints, returns
PASS/REVIEW/REJECT, engineer override — FR-13) · **financial** (open-source
stack, standard CPU workstation, no licence or cloud cost) · **auditable**
(versioned config, reproducible decision record) · **already started** (schema
+ quality gate, unit-tested).
Build path: Data (in progress, P1) → Baseline → Lot → Drift → Prediction →
Uncertainty → Decision → Explanation.

## Slide 5 — Impact and benefits

Message: *same burn-in; risk is visible at 24h and attention goes where the evidence points.*

- Users: component screening / QA and reliability engineers, space-grade electronics.
- Conventional: burn-in → wait → final screening → PASS/FAIL.
- AgniDrishti: burn-in → 24h data → early risk assessment → prioritise REVIEW
  cases → 168h forecast → evidence-backed decision; engineer stays in the loop.
- Pillars: **Reliability** (earlier visibility, aimed at fewer latent
  escapes) · **Efficiency** (attention on suspicious parts, better use of
  burn-in capacity) · **Trust** (auditable, explainable, human-in-the-loop,
  on-premises).
- Future: Phase 1 prototype on controlled synthetic + public data → Phase 2
  calibrate on representative ISRO data → Phase 3 multiple parameters +
  cross-lot history → Phase 4 test-equipment log integration.
- "Quantitative gains will be measured after representative-data validation.
  No results or impact figures are claimed at the idea stage."

## Slide 6 — Research and references

Grouped and labelled: **Official** (PS 26170; SIH 2026 Guidelines + Idea
Presentation Format) · **Reliability foundations — research, no compliance
claimed** (AEC-Q001 Rev-D; ESCC 9000 Issue 10; ESCC 9202/045 Issue 6) ·
**Prior art — research** (Ahmed et al. 2025; Langenberg et al. ESREL 2023;
US 8,010,310 B2) · **Method — research** (Lei et al. 2018; Dunn, Wasserman,
Ramdas 2023; Lu & Meeker 1993; Chow 1970) · **Data — external public dataset,
not SIH/ISRO data** (NASA PCoE MOSFET Thermal Overstress Aging; IGBT
Accelerated Aging; methodology validation only). Full citations: literature-review.md.

---

## Claim-classification gate (Rev. 2, 2026-09-26)

Every on-slide statement falls into one of these classes. Nothing is left
unclassified.

| Class | Statements (slide) | Basis |
|---|---|---|
| OFFICIAL PS | Static limits miss latent defects that drift (2); Module A dynamic lot-relative outliers (2, 3); Module B Value_0h + Value_24h → Value_168h and safety-slope early rejection (2, 3); false negatives catastrophic (2); justify decisions to a QA inspector (2); no official dataset published (4, 6) | R0; official-dataset-verification.md |
| ESTABLISHED RESEARCH | Robust median-based statistics; prediction intervals / conformal calibration; reject option; degradation modelling; AEC-Q001 lot-relative limits; ESCC 9000 drift limits (2, 3, 6) | S-01…S-15 |
| PROPOSED | ML comparators (Isolation Forest, gradient-boosted trees) adopted only if they beat the baseline (3); nine-stage pipeline; REVIEW state; missing data → REVIEW; ordered rules (no fused score); simplest-first forecasting; lot-grouped validation and ablation; offline CPU-first deployment; four future phases; "combines … in one workflow" differentiation (2–5) | ADR-001 Rev. 1, ADR-002…ADR-005 |
| ASSUMPTION | Official data will follow the PS checkpoint structure; burn-in procedure itself is unchanged; benefits are intended outcomes (4, 5; notes) | assumptions-and-constraints.md |
| UNKNOWN / OPEN | Safety-slope and Anomaly Detection Score formulas; all performance figures — **TBD — experiment not yet executed** (3, 4, 5) | GAP-01/02; experiment-plan.md |
| FACT (repo) | Canonical schema + data-quality gate implemented and unit-tested (3, 4) | `src/agnidrish/`, `tests/unit/` |

Checks done:

- [x] No performance number, percentage, cost/time saving or dataset size on any slide
- [x] No "first / novel / unique / compliant / physics-informed / guaranteed / zero FN"
- [x] Module B = Value_0h + Value_24h → Value_168h shown prominently (slides 2, 3)
- [x] Formulas stated as our proposed definitions; kept in speaker notes (ADR-002)
- [x] Evidence card and trajectory sketch labelled conceptual / not data; no values or units in either
- [x] NASA data labelled "external public dataset · not SIH/ISRO data · methodology validation only"
- [x] AEC-Q001 / ESCC described as research foundations, no compliance
- [x] PDF exported and all six pages inspected visually (no overlap, no overflow)
- [ ] `[TEAM ID]` filled in (team action)

Judge 60-second test: (1) what is wrong with static screening → slide 2 gap
panel; (2) what AgniDrishti does → slide 2 pipeline / slide 3 architecture;
(3) 0h + 24h → 168h handled correctly → Module B banner + forecasting and
uncertainty blocks; (4) feasibility despite data limits → slide 4 matrix;
(5) what the engineer receives → evidence card (slide 2).
