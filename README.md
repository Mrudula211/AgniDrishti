# AgniDrishti

**SIH 2026 — Problem Statement 26170: AI-Driven Anomaly Detection in Component Burn-In & Screening**

> **Status: research and architecture phase. No part of the system is implemented.**
> No synthetic dataset has been generated and no official PS dataset exists. Two **external** NASA datasets
> (MOSFET, IGBT) have been downloaded for methodology research only. No experiment has been run.
> All metrics in this repository read "TBD — experiment not yet executed."

## Problem

During burn-in, components are measured at a few checkpoints (reported as 0h,
24h, 96h, 168h) and accepted against fixed specification limits. A component can
stay inside its limit while being abnormal for its lot or drifting abnormally —
a possible latent defect. The PS (as reported in our research sources) asks for
lot-relative anomaly detection (Module A) and early prediction of the 168h value
from 0h and 24h with early rejection on a safety slope (Module B), where false
negatives are catastrophic and explanations are evaluated.

The official PS text (SIH portal, retrieved 2026-09-26) is preserved in
[docs/research/ps-analysis/official-ps-26170.md](docs/research/ps-analysis/official-ps-26170.md).
Module B takes `Value_0h` and `Value_24h` and forecasts `Value_168h`; its
prediction accuracy is scored by MAE against hidden ground-truth values.
**No official dataset is published for this PS**
([verification](docs/research/datasets/official-dataset-verification.md)).

**Start here:** [docs/project-state.md](docs/project-state.md) (current state,
open decisions) and the plain-language team guides in
[docs/team-understanding/](docs/team-understanding/problem-in-simple-language.md).

## Proposed solution (provisional)

```
Data quality gate → Absolute spec check → Lot-relative analysis (level + drift)
→ 168h prediction → Prediction interval (if it earns its place) → Ordered decision rules
→ PASS / REVIEW / REJECT (+ binary flag) → Engineer-readable explanation
```

Simple, transparent methods first (robust statistics, simple regression);
advanced models only if an experiment shows they help. See
[ADR-001](docs/decisions/ADR-001-initial-architecture.md).

## Repository structure

```
CLAUDE.md                 Engineering & research governance (read first)
*.pdf                     Original research sources R1–R3 (do not modify)
docs/
  research/               Synthesis, claim register, PS analysis, prior art,
                          datasets, experiments
  requirements/           Functional and non-functional requirements
  architecture/           System, data, ML, decision, explainability design
  decisions/              Architecture decision records
  presentation/           SIH format research, story, slide plan, demo flow, judge Q&A
  roadmap/                Implementation plan and blockers
  team-understanding/     Plain-language guides for teammates
  project-state.md        Current state summary
  glossary.md             Terminology rules
data/                     raw / external / synthetic / interim / processed (empty)
notebooks/                Exploration (empty)
src/                      Future package src/agnidrish/ (not created yet)
tests/                    unit / integration / fixtures (empty)
configs/                  Configuration (empty)
scripts/                  Command-line workflows (empty)
artifacts/                models / metrics / plots / predictions (git-ignored)
app/                      Demo application (phase P7)
.github/                  PR template
```

## Research status

| Area | Status |
|---|---|
| PS understanding | Verified against the official PS text; open points in [discrepancy-log.md](docs/research/ps-analysis/discrepancy-log.md) |
| Official dataset | Not found (verified) |
| Claim classification | [claim-register.md](docs/research/claim-register.md) |
| Prior art | Partly verified against primary sources (AEC-Q001, ESCC 9000, C&IE 2025, ESREL 2023, US 8,010,310, conformal literature) — [literature-review.md](docs/research/prior-art/literature-review.md). Lot-relative and burn-in drift screening are established prior art |
| Safety slope / drift rate | Not defined by the PS; our definition in [ADR-002](docs/decisions/ADR-002-safety-slope-and-drift-rate.md) (accepted 2026-09-26; allowance value not yet set) |
| Risks and PS gaps | [drawbacks-and-risks.md](docs/research/drawbacks-and-risks.md) |
| Datasets | Official: none exists. External: NASA MOSFET + IGBT downloaded, checksummed and inspected — [external-datasets.md](docs/research/datasets/external-datasets.md), [compatibility](docs/research/datasets/external-dataset-compatibility.md). Synthetic: not generated |
| Architecture | Provisional |
| Experiments | Planned (E0–E6), none executed |

## Development phases

P0 research (current) → P1 data foundation → P2 baseline → P3 lot + trajectory
→ P4 168h prediction → P5 uncertainty + decision → P6 explainability → P7 demo
→ P8 presentation. Details: [docs/roadmap/implementation-plan.md](docs/roadmap/implementation-plan.md).

## How to contribute

1. Read [CLAUDE.md](CLAUDE.md).
2. Pick a requirement (FR/NFR) and its experiment; do not add unplanned features.
3. Small change → tests → recorded experiment → docs update.
4. Fill in the PR checklist (no fabricated numbers, data category stated, leakage considered).

Python environment and dependencies will be defined in `pyproject.toml` at the
start of P1.

## Important limitations

- No official dataset is published; official scoring uses hidden ground truth we cannot see.
- The PS does not specify how the safety slope, the drift rate or the Anomaly Detection Score are calculated.
- Prior-art verification is partial; items marked UV in the literature review must not be cited.
- Planned evaluation relies on synthetic and external (NASA) data until official data exists;
  such results will not demonstrate real-world performance on ISRO hardware.
- Labels for "latent defect" will be proxies (spec or safety-slope violation), not field failures.
