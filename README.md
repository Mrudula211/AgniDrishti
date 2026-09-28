# AgniDrishti

**SIH 2026 — Problem Statement 26170: AI-Driven Anomaly Detection in Component Burn-In & Screening**

> **Status: deployable prototype (P2–P7 built 2026-09-26; screening service 2026-09-28) — evaluated on SYNTHETIC data only.**
> Pipeline: quality gate → datasheet limit → lot-relative level/drift → 168 h prediction → prediction interval →
> ordered PASS/REVIEW/REJECT rules → evidence card. No official PS dataset exists; nothing here is ISRO hardware data.

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
data/                     raw / external / synthetic / interim / processed (git-ignored)
notebooks/                Exploration (empty)
src/                      Package src/agnidrish/ (pipeline layers L0–L7, fit, service)
tests/                    unit + integration tests
configs/                  Experiment, synthetic-data and deployment configs
scripts/                  Generate, experiment, fit, screen, demo workflows
artifacts/                models / metrics / plots / predictions (git-ignored)
app/                      Screening web service + QA-inspector UI (ADR-006)
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
| Datasets | Official: none exists. External: NASA MOSFET + IGBT downloaded, checksummed and inspected — [external-datasets.md](docs/research/datasets/external-datasets.md), [compatibility](docs/research/datasets/external-dataset-compatibility.md). Synthetic: development v1 generated and E0-audited |
| Architecture | Provisional |
| Experiments | E0–E6 recorded on synthetic data — [ablation-plan.md](docs/research/experiments/ablation-plan.md) §3–§5 |

## Development phases

P0 research → P1 data foundation → P2 baseline → P3 lot + trajectory
→ P4 168h prediction → P5 uncertainty + decision → P6 explainability → P7 demo + service (all done)
→ **P8 presentation (next, needs team decision)**. Details: [docs/roadmap/implementation-plan.md](docs/roadmap/implementation-plan.md).

## How to contribute

1. Read [CLAUDE.md](CLAUDE.md).
2. Pick a requirement (FR/NFR) and its experiment; do not add unplanned features.
3. Small change → tests → recorded experiment → docs update.
4. Fill in the PR checklist (no fabricated numbers, data category stated, leakage considered).

## Development setup

Python 3.11+. Dependencies and their reasons are in `pyproject.toml`.

```
pip install -e ".[dev,serve]"
python -m pytest
python scripts/generate_synthetic.py   # SYNTHETIC development data + E0 audit
python scripts/run_experiments.py      # E1–E6 on validation lots -> artifacts/metrics/E1-E6_validation/<run>
python scripts/run_experiments.py --final artifacts/metrics/E1-E6_validation/<run>   # once, test lots
python scripts/build_demo.py artifacts/metrics/E1-E6_test/<run>                      # demo page
```

## Prototype — screening service

Full runbook: [docs/architecture/deployment.md](docs/architecture/deployment.md) · decision: [ADR-006](docs/decisions/ADR-006-deployable-service.md).

```
# 1. Fit a pipeline (here: the synthetic demo site; a real site uses its historical lots with 168 h values)
python scripts/fit_pipeline.py --input data/synthetic/development/synthetic_development_v1_seed20260926.csv        --category synthetic --config configs/deployment/fit_synthetic_demo.yaml
# 2. Demo upload file: held-out synthetic test lots as exported at 24 h
python scripts/make_demo_upload.py
# 3. Serve the UI + API on http://localhost:8000 (native, Windows or Linux, no Docker)
python scripts/serve.py --pipeline latest
# or batch, same code path:
python scripts/screen_lot.py --input lots.csv --category synthetic --pipeline artifacts/models/pipeline/<run>/pipeline.json
```

Every run is recorded under `artifacts/screening/<run>/` (input and pipeline copies, decisions, lot summary,
HTML report, `audit.json`, engineer overrides) and can be replayed to check that decisions are reproduced.

Input: canonical columns (`component_id, lot_id, parameter, unit, value_0h, value_24h,
spec_min, spec_max, …`) or a raw file plus `--mapping mapping.yaml`. Later checkpoints are
dropped before screening. Results so far are on **synthetic** data only:
[ablation-plan.md](docs/research/experiments/ablation-plan.md) §3–§5.

## Important limitations

- No official dataset is published; official scoring uses hidden ground truth we cannot see.
- The PS does not specify how the safety slope, the drift rate or the Anomaly Detection Score are calculated.
- Prior-art verification is partial; items marked UV in the literature review must not be cited.
- Planned evaluation relies on synthetic and external (NASA) data until official data exists;
  such results will not demonstrate real-world performance on ISRO hardware.
- Labels for "latent defect" will be proxies (spec or safety-slope violation), not field failures.
