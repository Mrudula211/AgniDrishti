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

## Solution (built; evaluated on synthetic data only)

```
Data quality gate → Absolute spec check → Lot-relative analysis (level + drift)
→ 168h prediction → 90 % prediction interval → Ordered decision rules
→ PASS / REVIEW / REJECT (+ binary flag) → Engineer-readable explanation
```

Simple, transparent methods first (robust statistics; four 168 h forecasters compared on validation MAE,
of which a learned population increment beat least-squares regression; split-conformal ranges); every layer was measured against a simpler baseline on held-out lots, including the layers
that did not add detection — [ablation-plan.md](docs/research/experiments/ablation-plan.md) §3–§5.
Architecture: [ADR-001](docs/decisions/ADR-001-initial-architecture.md) (Rev. 1).

**Idea-round deck:** [docs/presentation/sih2026-idea-agnidrishti.pdf](docs/presentation/sih2026-idea-agnidrishti.pdf) ·
where every number on it comes from: [idea-submission-content.md](docs/presentation/idea-submission-content.md).

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
| Safety slope / drift rate | Not defined by the PS; our definition in [ADR-002](docs/decisions/ADR-002-safety-slope-and-drift-rate.md) (accepted 2026-09-26; Δallow = 15 % of the 0 h value in `configs/experiments/pipeline_v1.yaml`) |
| Risks and PS gaps | [drawbacks-and-risks.md](docs/research/drawbacks-and-risks.md) |
| Datasets | Official: none exists. External: NASA MOSFET + IGBT downloaded, checksummed and inspected — [external-datasets.md](docs/research/datasets/external-datasets.md), [compatibility](docs/research/datasets/external-dataset-compatibility.md). Synthetic: development v1 generated and E0-audited |
| Architecture | Built (ADR-001 Rev. 1); validated on synthetic data only |
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

## Reproduce the deck's numbers

```
pip install -e ".[dev,serve]"          # without [serve], the API test module (4 tests) is skipped
python -m pytest                       # 111 passed at 1f5d29a
python scripts/generate_synthetic.py   # must print sha256 7a170d89…; run_experiments.py refuses any other file
python scripts/run_experiments.py
python scripts/run_experiments.py --final artifacts/metrics/E1-E6_validation/<run>
```

The generated file's SHA-256 (`7a170d89efb3ea8a…`, pre-registered in `configs/experiments/pipeline_v1.yaml`)
was reproduced on 2026-09-29 on Windows 11 (Python 3.12, numpy 1.26.4 / pandas 2.2.2 and numpy 2.4.6 / pandas 2.3.3)
and on Ubuntu 22.04 (Python 3.12, numpy 2.4.6 / pandas 2.3.3). The CSV stores full float precision, so a platform
whose vectorised maths rounds a last bit differently (for example another CPU architecture) produces a different
hash and the pre-registered run will not start. In that case use the exact 4 MB dataset file (attached to the
repository's GitHub release `sih-idea-v1`) instead of regenerating it; check its SHA-256 before running.

## Prototype — screening service

Runbook: [deployment.md](docs/architecture/deployment.md) · onboarding a new site / data format:
[data-ingestion.md](docs/architecture/data-ingestion.md) · decisions: [ADR-006](docs/decisions/ADR-006-deployable-service.md),
[ADR-007](docs/decisions/ADR-007-dataset-agnostic-ingestion.md).

```
# 1. Fit a pipeline (here: the synthetic demo site; a real site uses its own historical lots with 168 h readings)
python scripts/fit_pipeline.py --input data/synthetic/development/synthetic_development_v1_seed20260926.csv \
       --category synthetic --site configs/sites/synthetic_demo.yaml
# 2. Demo upload file: held-out synthetic test lots as exported at 24 h
python scripts/make_demo_upload.py
# 3. Serve the UI + API on http://localhost:8000 (native, Windows or Linux, no Docker)
python scripts/serve.py --site configs/sites/synthetic_demo.yaml --pipeline latest
# or batch, same code path:
python scripts/screen_lot.py --input export.csv --site configs/sites/synthetic_demo.yaml --category synthetic --pipeline <pipeline.json>
```

The system is not tied to one data format. A site describes its tester export, parameters, units and
specification-limit sources in one config file (`configs/sites/site_template.yaml`); the UI detects the layout of an
unseen file and lets the engineer confirm the column mapping. Parameters without a fitted 168 h forecast are still
screened by the lot-relative and datasheet rules, and every output says so.

Every run is recorded under `artifacts/screening/<run>/` (input, pipeline and site-config copies, decisions, lot
summary, HTML report, `audit.json`, engineer overrides) and can be replayed to check that decisions are reproduced.
Results so far are on **synthetic** data only: [ablation-plan.md](docs/research/experiments/ablation-plan.md) §3–§5.

## Important limitations

- No official dataset is published; official scoring uses hidden ground truth we cannot see.
- The PS does not specify how the safety slope, the drift rate or the Anomaly Detection Score are calculated.
- Prior-art verification is partial; items marked UV in the literature review must not be cited.
- Planned evaluation relies on synthetic and external (NASA) data until official data exists;
  such results will not demonstrate real-world performance on ISRO hardware.
- Labels for "latent defect" will be proxies (spec or safety-slope violation), not field failures.
