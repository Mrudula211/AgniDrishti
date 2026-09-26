# Project State

Status: Draft (living summary) · Last updated: 2026-09-26

Short state summary only. Details live in the linked documents.

| Item | State |
|---|---|
| **Current phase** | **Prototype built (P2–P7, 2026-09-26)** on branch `p1-synthetic-data`; evaluated on synthetic data only. Next phase (P8 presentation / v2 rules) needs a team decision. |
| **Current objective** | Review the prototype and findings; decide ablation-plan §5 recommendations. |
| **PS facts** | [official-ps-26170.md](research/ps-analysis/official-ps-26170.md) (R0). Module A lot-relative outliers; Module B Value_0h + Value_24h → Value_168h; early reject if predicted 168h drift rate > "calculated safety slope"; FN catastrophic; MAE on hidden Value_168h; explainability. |
| **Known data** | Official: none (verified). External: NASA MOSFET + IGBT downloaded, hashed, inspected — methodology use only. Synthetic: development v1 generated and E0-audited (DS-04). |
| **Data gaps** | Schema, labels, lot sizes, parameters, units — GAP-04…07 |
| **Research status** | Prior art partly verified (S-01…S-17) — [literature-review.md](research/prior-art/literature-review.md). Key finding: DPAT (AEC-Q001), ESCC burn-in drift limits and a burn-in drift-outlier patent (US 8,010,310) already exist → novelty is narrow. |
| **Architecture status** | Provisional (ADR-001, Proposed) with **Revision 1 confirmed 2026-09-26**: 7 layers (L3 merged into L2), ordered decision rules with no fused score, L5 conditional, binary flag always output. |
| **Open decisions** | ~~1. Safety slope + drift rate~~ **Decided 2026-09-26** ([ADR-002](decisions/ADR-002-safety-slope-and-drift-rate.md), option 1). ~~2. Idea-PDF scope~~ **Decided 2026-09-26**: draft idea deck now (proposal only, no numbers). ~~3. Architecture simplification~~ **Decided 2026-09-26** (ADR-001 Rev. 1). ~~4. Dataset strategy~~ **Decided 2026-09-26** ([ADR-003](decisions/ADR-003-dataset-strategy.md)). ~~5. Synthetic design~~ **Approved 2026-09-26**; held-out families sealed (SHA-256 commitment, synthetic-data-design §7). ~~6. Primary proxy label~~ **Decided 2026-09-26** ([ADR-004](decisions/ADR-004-primary-proxy-label.md)). ~~7. Operating point~~ **Decided 2026-09-26** ([ADR-005](decisions/ADR-005-operating-point.md)). ~~8. Authorise P1~~ **Authorised 2026-09-26** (narrow scope). |
| **Blockers** | None. The v1 test split is spent: any rule change needs a new pre-registered config and fresh data (new seed). |
| **Implementation status** | All layers L0–L7 implemented (FR-01–FR-19, FR-03–FR-11); prototype CLI `scripts/screen_lot.py`, demo `scripts/build_demo.py`; 95 unit tests. Branch `p1-synthetic-data`, not pushed. |
| **Experiment status** | E0 passed. E1–E6 recorded (validation + one final test run) — ablation-plan §3–§5: lot-relative drift gives the main gain; R* = 0.95 not reached (test recall 0.800 at 10.4 % review). R-01–R-04: TBD — experiment not yet executed. |
| **Presentation status** | Idea round (**due 30 Sep 2026**): draft built — [idea-submission-content.md](presentation/idea-submission-content.md) + filled official template [sih2026-idea-agnidrishti.pptx](presentation/sih2026-idea-agnidrishti.pptx). Team must fill Team ID / name, review, export PDF, upload. Finale deck: plan only. |
| **Next action** | Team review of demo + findings; decide §5 recommendations; then finale deck from recorded runs (CLAUDE §27). |
| **Waiting for user** | Push / PR decision; decisions on ablation-plan §5; idea deck upload by 30 Sep. |
| **Team docs** | [problem](team-understanding/problem-in-simple-language.md) · [how it works](team-understanding/how-agnidrishti-works.md) · [data & labels](team-understanding/data-and-labels.md) · [decision flow](team-understanding/decision-flow.md) · [known / unknown](team-understanding/what-we-know-and-dont-know.md) |
| **Risk register** | [drawbacks-and-risks.md](research/drawbacks-and-risks.md) |
