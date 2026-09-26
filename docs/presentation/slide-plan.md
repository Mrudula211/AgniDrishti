# Slide Plan

Status: Draft · Last updated: 2026-09-26

**Scope: Grand Finale deck** (after experiments). The idea-submission round is
limited by the official template to **6 slides incl. title, PDF only** (S-17) —
see [sih-presentation-research.md](sih-presentation-research.md). This plan does
not apply to that round.

Target ~12 slides + Q&A backup. Research-paper detail (formulas, conformal
theory) goes to backup slides, not the main flow.

| # | Slide | Visual | Source of content | Blocked by |
|---|---|---|---|---|
| 1 | AgniDrishti — PS 26170 | Title | — | — |
| 2 | The hidden failure problem | One trajectory below the limit but far from its lot (labelled synthetic) | Synthetic dataset v1 | P1 |
| 3 | Why static screening misses it | E1 result: cases passing static check | E1 | E1 |
| 4 | Core insight | Spec + peers + trajectory + uncertainty | Story beat 3 | — |
| 5 | Architecture (proposed) | 7-layer pipeline (ADR-001 Rev. 1), T24 (Module B) + optional T96 | system-architecture.md | — |
| 6 | Lot-relative analysis | Lot distribution + component position | E2 | E2 |
| 7 | Trajectory + 168h prediction | Trajectory map with predicted 168h point | E3, E4 | E4 |
| 8 | Uncertainty + REVIEW | Interval crossing limit → REVIEW | E5 | E5 |
| 9 | Evidence: ablation | Ablation table / recall-vs-review curve | ablation-plan.md | E6 |
| 10 | End-to-end case | Evidence card for one component | demo-flow.md | E6, P6 |
| 11 | Deployment & workflow (proposed) | Batch per lot, audit log, engineer override | requirements FR-12/13 | — |
| 12 | Limitations & future work | Honest list | assumptions-and-constraints.md | — |
| B1 | Why not LSTM / Transformer? | Points per component vs parameters | M-01 | — |
| B2 | Robust z formula, MAD vs IQR | Formula | ml-pipeline.md | — |
| B3 | Leakage prevention & splits | Lot-grouped split diagram | evaluation-protocol.md | — |
| B4 | Prediction interval meaning | Coverage plot | E5 | E5 |
| B5 | Prior art & positioning | Prior-art matrix | prior-art-matrix.md | Remaining UV items (literature-review §2) |
| B6 | Dataset categories | Official / external / synthetic table | dataset-strategy.md | — |

Every data slide footer: `Data: <category> · Run: <experiment/run id>`.
