# Project State

Status: Draft (living summary) · Last updated: 2026-09-26

Short state summary only. Details live in the linked documents.

| Item | State |
|---|---|
| **Current phase** | **P1 — Data foundation** (authorised 2026-09-26, Decision 8). Scope: pyproject, canonical schema (FR-01), data-quality gate (FR-02), tests. Generator and experiments still gated (CLAUDE §0). |
| **Current objective** | Close open design decisions (one at a time) so that implementation requirements and experiments can be finalised. |
| **PS facts** | [official-ps-26170.md](research/ps-analysis/official-ps-26170.md) (R0). Module A lot-relative outliers; Module B Value_0h + Value_24h → Value_168h; early reject if predicted 168h drift rate > "calculated safety slope"; FN catastrophic; MAE on hidden Value_168h; explainability. |
| **Known data** | Official: none (verified). External: NASA MOSFET + IGBT downloaded, hashed, inspected — methodology use only. Synthetic: not generated. |
| **Data gaps** | Schema, labels, lot sizes, parameters, units — GAP-04…07 |
| **Research status** | Prior art partly verified (S-01…S-17) — [literature-review.md](research/prior-art/literature-review.md). Key finding: DPAT (AEC-Q001), ESCC burn-in drift limits and a burn-in drift-outlier patent (US 8,010,310) already exist → novelty is narrow. |
| **Architecture status** | Provisional (ADR-001, Proposed) with **Revision 1 confirmed 2026-09-26**: 7 layers (L3 merged into L2), ordered decision rules with no fused score, L5 conditional, binary flag always output. |
| **Open decisions** | ~~1. Safety slope + drift rate~~ **Decided 2026-09-26** ([ADR-002](decisions/ADR-002-safety-slope-and-drift-rate.md), option 1). ~~2. Idea-PDF scope~~ **Decided 2026-09-26**: draft idea deck now (proposal only, no numbers). ~~3. Architecture simplification~~ **Decided 2026-09-26** (ADR-001 Rev. 1). ~~4. Dataset strategy~~ **Decided 2026-09-26** ([ADR-003](decisions/ADR-003-dataset-strategy.md)). ~~5. Synthetic design~~ **Approved 2026-09-26** (held-out owner TBD). ~~6. Primary proxy label~~ **Decided 2026-09-26** ([ADR-004](decisions/ADR-004-primary-proxy-label.md)). ~~7. Operating point~~ **Decided 2026-09-26** ([ADR-005](decisions/ADR-005-operating-point.md)). ~~8. Authorise P1~~ **Authorised 2026-09-26** (narrow scope). |
| **Blockers** | Held-out synthetic families 19–20 not yet sealed (owner TBD). |
| **Implementation status** | P1 in progress on branch `p1-data-foundation`: canonical schema + mapping (FR-01) and data-quality gate (FR-02, units / multi-modality checks pending) with 28 unit tests incl. checkpoint-leakage tests. No model, prediction or decision code. |
| **Experiment status** | E0–E6, R-01–R-04 planned; **none executed**. All metrics: TBD — experiment not yet executed. |
| **Presentation status** | Idea round (**due 30 Sep 2026**): draft built — [idea-submission-content.md](presentation/idea-submission-content.md) + filled official template [sih2026-idea-agnidrishti.pptx](presentation/sih2026-idea-agnidrishti.pptx). Team must fill Team ID / name, review, export PDF, upload. Finale deck: plan only. |
| **Next action** | Review/merge `p1-data-foundation`; team: idea deck, name held-out-family owner. Then E0 config + next P1 step. |
| **Waiting for user** | Review of branch `p1-data-foundation` (not pushed); idea deck; held-out owner name; choice of next work track. |
| **Team docs** | [problem](team-understanding/problem-in-simple-language.md) · [how it works](team-understanding/how-agnidrishti-works.md) · [data & labels](team-understanding/data-and-labels.md) · [decision flow](team-understanding/decision-flow.md) · [known / unknown](team-understanding/what-we-know-and-dont-know.md) |
| **Risk register** | [drawbacks-and-risks.md](research/drawbacks-and-risks.md) |
