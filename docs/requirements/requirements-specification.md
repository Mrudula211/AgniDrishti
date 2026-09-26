# Requirements Specification — AgniDrishti

Status: Draft · Last updated: 2026-09-26

Requirements for the **future** system. Nothing here is implemented.
Each requirement cites its origin:

- **PSR-xx** — PS requirement (as reported; see [problem-statement-analysis.md](../research/ps-analysis/problem-statement-analysis.md))
- **EI** — engineering necessity derived from a PS requirement
- **PR** — design proposal; must be justified by an experiment before it is kept

Priority: **M** must (PS-mandated or needed for any valid result) · **S** should · **C** could.

## 1. Functional requirements

| ID | Requirement | Origin | Pri. | Verified by |
|---|---|---|---|---|
| FR-01 | Ingest a lot measurement table and map raw column names to the canonical schema ([data-dictionary](../research/datasets/data-dictionary.md)). Reject files that cannot be mapped. | EI | M | Unit + integration test — **unit tests implemented (P1)**: `src/agnidrish/schema.py`, `tests/unit/test_schema.py` |
| FR-02 | **Data quality gate**: check schema, units, duplicates, missing checkpoints, non-physical values, lot size below minimum, zero/near-zero lot dispersion (MAD = 0), suspected multi-modal lots. Each issue produces a named flag. Components with blocking issues go to REVIEW, never PASS. | EI (PSR-05) | M | Unit tests per check — **partly implemented (P1)**: `src/agnidrish/quality.py`; units and multi-modality checks pending ([data-pipeline.md](../architecture/data-pipeline.md) §3) |
| FR-03 | **Absolute specification check** at each available checkpoint (supports lower, upper or two-sided limits). | PSR-07 | M | Unit test; E1 |
| FR-04 | **Lot-relative level score**: robust z-score of the value versus its lot at the same checkpoint. | PSR-02 | M | Unit test; E2 |
| FR-05 | **Lot-relative drift score**: robust z-score of the component's drift versus the drift of its lot over the same interval. | PSR-02, EI | M | Unit test; E3 |
| FR-06 | **Trajectory (drift) features**, computed inside the L2 layer (ADR-001 Rev. 1), at each decision checkpoint using only data available at that checkpoint (T24: level, Δ, relative Δ; T96: + segment slopes, slope change). | PSR-01, EI | M | Unit + leakage tests; E3 |
| FR-07 | **168h prediction (Module B)**: regression from `value_0h`, `value_24h` to `value_168h` — confirmed by the official PS (R0, OPS-03; [discrepancy-log](../research/ps-analysis/discrepancy-log.md) DL-01 resolved). Primary metric MAE (OPS-06). A T96 predictor, if built, is an extension outside Module B and reported separately. | PSR-03 / OPS-03 | M | E4 |
| FR-08 | **Prediction interval** for the 168h prediction with a stated target coverage. | EI (PSR-05) | S | E5 |
| FR-09 | **Safety-slope rule** ([ADR-002](../decisions/ADR-002-safety-slope-and-drift-rate.md), accepted): flag for early rejection when the predicted drift rate (Ŷ₁₆₈ − V₀)/168 h exceeds Δ_allow/168 h (per-parameter drift allowance, absolute or relative, from config; no default), or when Ŷ₁₆₈ crosses the datasheet limit. | PSR-04 / OPS-04 | M | Unit test; E4 |
| FR-16 | **Binary output**: emit a binary anomaly / early-rejection flag per component in addition to PASS/REVIEW/REJECT; REVIEW → flag mapping configurable (see [anomaly-detection-score.md](../research/ps-analysis/anomaly-detection-score.md) §5). | EI (OPS-05, GAP-10) | M | Unit test |
| FR-10 | **Decision**: assign PASS / REVIEW / REJECT by documented, configurable rules. Missing or invalid inputs → REVIEW. | PR (PSR-05) | S | Unit tests per rule; E6 |
| FR-11 | **Explanation**: for every component with REVIEW or REJECT (and on request for PASS), produce the quantitative evidence and the rule(s) that fired. | PSR-06 | M | Unit test on templates; review by team |
| FR-12 | **Audit record** for every decision: input values, lot statistics used, config version, model version, outputs, rule(s) fired, timestamp. | EI (PSR-06) | S | Integration test |
| FR-13 | **Engineer override** of a decision, stored alongside the original decision. | PR | C | — (P7) |
| FR-14 | **Lot summary**: lot statistics, lot-level flags, decision counts, review rate. | EI | S | Integration test |
| FR-15 | **Evaluation harness**: compute the metrics in the [evaluation protocol](../research/experiments/evaluation-protocol.md) from predictions and labels, per data category. | EI | M | Unit tests vs hand-computed metrics |

## 2. Non-functional requirements

| ID | Quality | Requirement | Measure | Target |
|---|---|---|---|---|
| NFR-01 | Safety / reliability | Fail-safe: any error, missing input or degenerate statistic results in REVIEW, never silent PASS. | Fault-injection tests | 100% of injected faults → REVIEW |
| NFR-02 | Explainability | Every non-PASS decision is traceable to named rules and numeric evidence; no decision relies solely on an opaque score. | Review of outputs | All decisions |
| NFR-03 | Reproducibility | Same data + config + seed → identical outputs. | Re-run comparison | Bit-identical decisions |
| NFR-04 | Auditability | Decision records sufficient to reconstruct the decision offline. | Replay test | All decisions |
| NFR-05 | Data integrity | Raw data never modified; derived data regenerable; data category (official/external/synthetic) carried through to every output. | Tests + review | — |
| NFR-06 | Leakage prevention | Features at checkpoint T use only data measured at ≤ T; splits grouped by lot. | Automated leakage tests | Zero violations |
| NFR-07 | Performance | Batch processing latency per lot. | Benchmark | TBD — experiment not yet executed |
| NFR-08 | Scalability | Throughput for large lots / many lots. | Benchmark | TBD — experiment not yet executed |
| NFR-09 | Maintainability | Small modules, typed, tested; each pipeline layer independently testable and removable (for ablation). | Code review | — |
| NFR-10 | Portability | No absolute paths; runs from repository root on Windows and Linux. | CI on both (later) | — |
| NFR-11 | Configurability | All thresholds, limits, safety slope, coverage targets in `configs/`. | Review | No magic numbers |
| NFR-12 | Security | Can run fully offline; no data leaves the machine. | Design review | — |
| NFR-13 | Honesty of outputs | Uncertainty and risk outputs use correct terminology ([glossary](../glossary.md)); no probability is shown unless calibrated. | Review | — |

## 3. Out of scope for now

Frontend, dashboard, API server, database, authentication, deployment, deep
sequence models, digital-twin framing, RUL estimation. May be reconsidered after
P6 with a documented reason.
