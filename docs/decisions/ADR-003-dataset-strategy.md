# ADR-003 — Dataset Strategy

Status: Accepted · Date: 2026-09-26 · Confirmed by user (Decision 4, option 1)

## Context

No official PS 26170 dataset exists; evaluators hold hidden ground truth (R0;
[official-dataset-verification.md](../research/datasets/official-dataset-verification.md)).
Two external NASA datasets are downloaded and inspected
([external-datasets.md](../research/datasets/external-datasets.md)); neither has lots,
burn-in checkpoints or labels.

## Options considered

| # | Option | Rejected / chosen because |
|---|---|---|
| 1 | Three separate tracks: synthetic (primary) + NASA MOSFET (prediction methodology) + NASA IGBT (qualitative) + ask organisers | **Chosen** — only synthetic data can exercise lots; only NASA data contains real degradation |
| 2 | Synthetic only | Rejected — no check against real degradation shapes |
| 3 | Wait for organisers | Rejected — blocks all experiments for an unknown time |

## Decision

| Track | Category label | Used for | Not used for |
|---|---|---|---|
| Synthetic PS-shaped | **Synthetic** | Primary evaluation of Module A, Module B, safety-slope rule, decision rules, robustness (E1–E6, R-01–R-03) | Any claim about real ISRO performance |
| NASA MOSFET Thermal Overstress | **External — NASA PCoE** | Prediction-methodology robustness only (R-04), split by test | Module A; any PS-score claim; relabelling as Value_0h/24h/168h |
| NASA IGBT Accelerated Aging | **External — NASA Open Data** | Qualitative cross-device sanity checks only | Any metric presented as evidence |
| Official | **Official** | Everything, if and when released — takes precedence | — |

Rules:

1. Tracks are never pooled; every result states its category.
2. Synthetic data is generated **only after** the design review in
   [synthetic-data-design.md](../research/datasets/synthetic-data-design.md) §6 is signed off.
3. Any NASA → early/late-value mapping is defined in a documented experiment before use.
4. The team contacts the organisers (sih@aicte-india.org) for sample data and for the
   safety-slope, drift-rate and Anomaly Detection Score definitions; replies are
   recorded in the relevant docs and may supersede ADR-002.

## Consequences

- Results demonstrate behaviour under stated assumptions, not real-world performance.
- Robustness experiments (held-out scenario families, parameter sweeps) carry more
  weight than any single synthetic metric.
- B-02 (no official dataset) is closed as an accepted strategy; GAP-04 remains an
  accepted limitation.
