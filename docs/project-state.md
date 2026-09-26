# Project State

Status: Draft (living summary) · Last updated: 2026-09-26

Short state summary only. Details live in the linked documents.

| Item | State |
|---|---|
| **Current phase** | **P1 — Data foundation** (authorised 2026-09-26, Decision 8). Scope: schema (FR-01), quality gate (FR-02), synthetic generator (FR-17), E0 audit (FR-18), proxy labels (FR-19). Experiments E1–E6 still gated (CLAUDE §0). |
| **Current objective** | Close open design decisions (one at a time) so that implementation requirements and experiments can be finalised. |
| **PS facts** | [official-ps-26170.md](research/ps-analysis/official-ps-26170.md) (R0). Module A lot-relative outliers; Module B Value_0h + Value_24h → Value_168h; early reject if predicted 168h drift rate > "calculated safety slope"; FN catastrophic; MAE on hidden Value_168h; explainability. |
| **Known data** | Official: none (verified). External: NASA MOSFET + IGBT downloaded, hashed, inspected — methodology use only. Synthetic: development v1 generated and E0-audited (DS-04). |
| **Data gaps** | Schema, labels, lot sizes, parameters, units — GAP-04…07 |
| **Research status** | Prior art partly verified (S-01…S-17) — [literature-review.md](research/prior-art/literature-review.md). Key finding: DPAT (AEC-Q001), ESCC burn-in drift limits and a burn-in drift-outlier patent (US 8,010,310) already exist → novelty is narrow. |
| **Architecture status** | Provisional (ADR-001, Proposed) with **Revision 1 confirmed 2026-09-26**: 7 layers (L3 merged into L2), ordered decision rules with no fused score, L5 conditional, binary flag always output. |
| **Open decisions** | ~~1. Safety slope + drift rate~~ **Decided 2026-09-26** ([ADR-002](decisions/ADR-002-safety-slope-and-drift-rate.md), option 1). ~~2. Idea-PDF scope~~ **Decided 2026-09-26**: draft idea deck now (proposal only, no numbers). ~~3. Architecture simplification~~ **Decided 2026-09-26** (ADR-001 Rev. 1). ~~4. Dataset strategy~~ **Decided 2026-09-26** ([ADR-003](decisions/ADR-003-dataset-strategy.md)). ~~5. Synthetic design~~ **Approved 2026-09-26**; held-out families sealed (SHA-256 commitment, synthetic-data-design §7). ~~6. Primary proxy label~~ **Decided 2026-09-26** ([ADR-004](decisions/ADR-004-primary-proxy-label.md)). ~~7. Operating point~~ **Decided 2026-09-26** ([ADR-005](decisions/ADR-005-operating-point.md)). ~~8. Authorise P1~~ **Authorised 2026-09-26** (narrow scope). |
| **Blockers** | None for P1. Experiments E1–E6 still need success bounds and R* pre-registered (ADR-005). |
| **Implementation status** | PR #1 (`p1-data-foundation`): schema (FR-01) + quality gate (FR-02). Branch `p1-synthetic-data` (stacked on it, not pushed): synthetic generator (FR-17), E0 audit (FR-18), proxy labels (FR-19); 66 unit tests. No model, prediction or decision code. |
| **Experiment status** | E0 audit passed on synthetic development v1 (dataset statistics only, DS-04). E1–E6, R-01–R-04: TBD — experiment not yet executed. |
| **Presentation status** | Idea round (**due 30 Sep 2026**): draft built — [idea-submission-content.md](presentation/idea-submission-content.md) + filled official template [sih2026-idea-agnidrishti.pptx](presentation/sih2026-idea-agnidrishti.pptx). Team must fill Team ID / name, review, export PDF, upload. Finale deck: plan only. |
| **Next action** | Review `p1-synthetic-data`; then pre-register E1 success bounds and R* (ADR-005) before E1 (static baseline). |
| **Waiting for user** | Review of the synthetic dataset and branch; whether to push / open a PR; idea deck upload by 30 Sep. |
| **Team docs** | [problem](team-understanding/problem-in-simple-language.md) · [how it works](team-understanding/how-agnidrishti-works.md) · [data & labels](team-understanding/data-and-labels.md) · [decision flow](team-understanding/decision-flow.md) · [known / unknown](team-understanding/what-we-know-and-dont-know.md) |
| **Risk register** | [drawbacks-and-risks.md](research/drawbacks-and-risks.md) |
