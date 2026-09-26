# Implementation Plan

Status: Draft · Last updated: 2026-09-26

**P1 authorised 2026-09-26** (narrow scope — CLAUDE.md §0). Research phase P0 closed.
Each step is one small, reviewable change: requirement → minimal code → test →
experiment → record → document.

## Blockers (resolve or explicitly accept before P1)

| ID | Blocker | Action | Owner |
|---|---|---|---|
| B-01 | ~~Official PS 26170 text not in hand~~ | **Closed 2026-09-26** — official text obtained and preserved ([official-ps-26170.md](../research/ps-analysis/official-ps-26170.md)) | — |
| B-02 | No official dataset | **Verified 2026-09-26: OFFICIAL DATASET NOT FOUND** (Dataset Link empty; evaluators hold hidden ground truth). **Strategy accepted 2026-09-26 — [ADR-003](../decisions/ADR-003-dataset-strategy.md)**; team to ask organisers for sample data | Team |
| B-03 | ~~Module B inputs ambiguous (C-01)~~ | **Closed 2026-09-26** — R0: Value_0h + Value_24h | — |
| B-04 | Safety slope undefined (GAP-01) | **Closed 2026-09-26** — [ADR-002](../decisions/ADR-002-safety-slope-and-drift-rate.md) accepted (Δ_allow value still unset; swept) | Team |
| B-07 | Anomaly Detection Score formula not given (GAP-03) | [anomaly-detection-score.md](../research/ps-analysis/anomaly-detection-score.md); ask organisers | Team |
| B-08 | Drift-rate formula not given (GAP-02) | **Closed 2026-09-26** — ADR-002 | Team |
| B-05 | Prior-art items unverified | **Partly done 2026-09-26** (S-01…S-17); remaining UV items in literature-review §2 | Team |
| B-06 | Operating constraint on review rate unknown (GAP-08) | **Closed 2026-09-26** — [ADR-005](../decisions/ADR-005-operating-point.md) recall-first policy; R* to be pre-registered before E6 | Team |
| B-09 | Synthetic generator design | **Design approved 2026-09-26**; remaining: name owner and seal families 19–20 ([synthetic-data-design.md](../research/datasets/synthetic-data-design.md) §7) | Team |
| B-10 | ~~No git repository~~ | **Closed** — repository exists with remote `origin` (GitHub); work on branches per CLAUDE §26 | — |

All gaps and risks: [drawbacks-and-risks.md](../research/drawbacks-and-risks.md). Current state: [project-state.md](../project-state.md).

## Phases

| Phase | Deliverable | First concrete step | Exit criterion |
|---|---|---|---|
| P1 | Environment + data foundation | `pyproject.toml` (minimal deps: numpy, pandas, pytest); canonical schema + validation (FR-01, FR-02) with tests; synthetic generator **design review** then generator; E0 audit | Leakage + validation tests pass; synthetic dataset v1 documented in data-sources |
| P2 | Baseline | L1 + metrics harness (FR-15) + lot-grouped split; E1 | E1 recorded |
| P3 | Lot + drift | L2 (level + drift); E2, E3 | E2, E3 recorded; keep/remove decisions |
| P4 | 168h prediction | B0–B3; safety-slope rule; E4 (+ E4b only if justified) | E4 recorded |
| P5 | Uncertainty + decision | U1; rule engine; E5, E6 | E5, E6 recorded; ADR-001 → Accepted or revised |
| P6 | Explainability | Templates, audit record, trajectory map | Every rule has tested explanation |
| P7 | Demo app | Minimal UI over recorded runs (tech choice via ADR) | Demo uses only recorded outputs, category shown |
| P8 | Presentation | Slides from recorded evidence | Every number linked to a run |

## Recommended next step

~~Resolve B-01 (obtain the official PS text)~~ (done 2026-09-26). ~~Confirm
ADR-002~~ (done 2026-09-26), ~~accept the dataset strategy (B-02)~~ (done 2026-09-26), ~~review the synthetic
design~~ (approved 2026-09-26; families 19–20 still to be sealed, B-09), ~~initialise git~~ (B-10 closed), then — only after explicit authorisation
(CLAUDE §0) — start P1 with the
canonical schema and data-quality checks — the smallest code that every later
experiment depends on, and where leakage tests are first written.
