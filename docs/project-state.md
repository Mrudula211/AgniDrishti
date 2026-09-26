# Project State

Status: Draft (living summary) · Last updated: 2026-09-26

Short state summary only. Details live in the linked documents.

| Item | State |
|---|---|
| **Current phase** | P0 — Research + Architecture + Documentation. No implementation (CLAUDE §0). |
| **Current objective** | Close open design decisions (one at a time) so that implementation requirements and experiments can be finalised. |
| **PS facts** | [official-ps-26170.md](research/ps-analysis/official-ps-26170.md) (R0). Module A lot-relative outliers; Module B Value_0h + Value_24h → Value_168h; early reject if predicted 168h drift rate > "calculated safety slope"; FN catastrophic; MAE on hidden Value_168h; explainability. |
| **Known data** | Official: none (verified). External: NASA MOSFET + IGBT downloaded, hashed, inspected — methodology use only. Synthetic: not generated. |
| **Data gaps** | Schema, labels, lot sizes, parameters, units — GAP-04…07 |
| **Research status** | Prior art partly verified (S-01…S-17) — [literature-review.md](research/prior-art/literature-review.md). Key finding: DPAT (AEC-Q001), ESCC burn-in drift limits and a burn-in drift-outlier patent (US 8,010,310) already exist → novelty is narrow. |
| **Architecture status** | Provisional (ADR-001, Proposed). Re-evaluation proposes merging L2-drift + L3 and no fused risk score — [system-architecture.md](architecture/system-architecture.md) §7, pending confirmation. |
| **Open decisions** | ~~1. Safety slope + drift rate~~ **Decided 2026-09-26** ([ADR-002](decisions/ADR-002-safety-slope-and-drift-rate.md), option 1). 2. Idea-PDF scope for 30 Sep ← **asked now**. 3. Architecture simplification. 4. Dataset strategy acceptance. 5. Synthetic design review. 6. Primary proxy label. 7. Review-rate budget. |
| **Blockers** | No git repository (reproducibility rules need commit hashes); synthetic design unreviewed. |
| **Experiment status** | E0–E6, R-01–R-04 planned; **none executed**. All metrics: TBD — experiment not yet executed. |
| **Presentation status** | Idea round: official 6-slide PDF template, **due 30 Sep 2026** — content mapping in [sih-presentation-research.md](presentation/sih-presentation-research.md) §4; not built. Finale deck: plan only. |
| **Next action** | Get Decision 2; then architecture simplification (Decision 3). |
| **Waiting for user** | Decision 2 — idea-PDF scope for the 30 Sep 2026 submission. |
| **Team docs** | [problem](team-understanding/problem-in-simple-language.md) · [how it works](team-understanding/how-agnidrishti-works.md) · [data & labels](team-understanding/data-and-labels.md) · [decision flow](team-understanding/decision-flow.md) · [known / unknown](team-understanding/what-we-know-and-dont-know.md) |
| **Risk register** | [drawbacks-and-risks.md](research/drawbacks-and-risks.md) |
