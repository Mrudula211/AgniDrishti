# Requirements Specification — AgniDrishti

Status: Draft · Last updated: 2026-09-29

Requirements for the system. Implementation status is stated per requirement (FR-01–FR-25 built as of 2026-09-29; evidence on synthetic data only).
Each requirement cites its origin:

- **PSR-xx** — PS requirement (as reported; see [problem-statement-analysis.md](../research/ps-analysis/problem-statement-analysis.md))
- **EI** — engineering necessity derived from a PS requirement
- **PR** — design proposal; must be justified by an experiment before it is kept

Priority: **M** must (PS-mandated or needed for any valid result) · **S** should · **C** could.

## 1. Functional requirements

| ID | Requirement | Origin | Pri. | Verified by |
|---|---|---|---|---|
| FR-01 | Ingest a lot measurement table and map raw column names to the canonical schema ([data-dictionary](../research/datasets/data-dictionary.md)). Reject files that cannot be mapped. | EI | M | Unit + integration test — **unit tests implemented (P1)**: `src/agnidrish/schema.py`, `tests/unit/test_schema.py` |
| FR-02 | **Data quality gate**: check schema, units, duplicates, missing checkpoints, non-physical values, lot size below minimum, zero/near-zero lot dispersion (MAD = 0), suspected multi-modal lots. Each issue produces a named flag. Components with blocking issues go to REVIEW, never PASS. | EI (PSR-05) | M | Unit tests per check — **partly implemented (P1)**: `src/agnidrish/quality.py`; unit checks added 2026-09-28 (MIXED_UNITS, UNIT_NOT_CONVERTIBLE via FR-22); multi-modality check pending ([data-pipeline.md](../architecture/data-pipeline.md) §3) |
| FR-03 | **Absolute specification check** at each available checkpoint (supports lower, upper or two-sided limits). | PSR-07 | M | Unit test; E1 |
| FR-04 | **Lot-relative level score**: robust z-score of the value versus its lot at the same checkpoint. | PSR-02 | M | Unit test; E2 |
| FR-05 | **Lot-relative drift score**: robust z-score of the component's drift versus the drift of its lot over the same interval. | PSR-02, EI | M | Unit test; E3 |
| FR-06 | **Trajectory (drift) features**, computed inside the L2 layer (ADR-001 Rev. 1), at each decision checkpoint using only data available at that checkpoint (T24: level, Δ, relative Δ; T96: + segment slopes, slope change). | PSR-01, EI | M | Unit + leakage tests; E3 |
| FR-07 | **168h prediction (Module B)**: regression from `value_0h`, `value_24h` to `value_168h` — confirmed by the official PS (R0, OPS-03; [discrepancy-log](../research/ps-analysis/discrepancy-log.md) DL-01 resolved). Primary metric MAE (OPS-06). A T96 predictor, if built, is an extension outside Module B and reported separately. | PSR-03 / OPS-03 | M | E4 |
| FR-08 | **Prediction interval** for the 168h prediction with a stated target coverage. | EI (PSR-05) | S | E5 |
| FR-09 | **Safety-slope rule** ([ADR-002](../decisions/ADR-002-safety-slope-and-drift-rate.md), accepted): flag for early rejection when the predicted drift rate (Ŷ₁₆₈ − V₀)/168 h exceeds Δ_allow/168 h (per-parameter drift allowance, absolute or relative, from config; no default), or when Ŷ₁₆₈ crosses the datasheet limit. | PSR-04 / OPS-04 | M | Unit test; E4 |
| FR-16 | **Binary output**: emit a binary anomaly / early-rejection flag per component in addition to PASS/REVIEW/REJECT; REVIEW → flag mapping configurable (see [anomaly-detection-score.md](../research/ps-analysis/anomaly-detection-score.md) §5). | EI (OPS-05, GAP-10) | M | Unit test |
| FR-17 | **Synthetic data generator** (SYNTHETIC category only): deterministic from config + seed; lots, components, parameters, checkpoints 0/24/96/168 h, datasheet limits; development behaviour families with ground truth (family, anomaly status, severity, true values) stored as evaluation-only columns; lot-grouped splits. Never generates held-out families 19–20. | EI (ADR-003) | M | Unit tests; E0 audit — `src/agnidrish/synthetic/` |
| FR-18 | **E0 data audit**: fail loudly on violated dataset invariants (schema, provenance, duplicates, spec limits, split leakage, family/anomaly/severity consistency, value-vs-truth consistency, spec scenarios, lot sizes) and report statistics; reproducibility check by regeneration. | EI (CLAUDE §7, §8) | M | Unit tests with injected violations — `src/agnidrish/audit.py` |
| FR-19 | **Proxy labels** `label_spec_168h` and `label_safety_slope` (ADR-002 §11, ADR-004) for any drift allowance, absolute or relative, and any degradation direction; evaluation only. | ADR-002, ADR-004 | M | Unit tests vs hand-computed cases — `src/agnidrish/labels.py` |
| FR-10 | **Decision**: assign PASS / REVIEW / REJECT by documented, configurable rules. Missing or invalid inputs → REVIEW. | PR (PSR-05) | S | Unit tests per rule; E6 |
| FR-11 | **Explanation**: for every component with REVIEW or REJECT (and on request for PASS), produce the quantitative evidence and the rule(s) that fired. | PSR-06 | M | Unit test on templates; review by team |
| FR-12 | **Audit record** for every decision: input values, lot statistics used, config version, model version, outputs, rule(s) fired, timestamp. | EI (PSR-06) | S | Integration test — **implemented 2026-09-28**: `agnidrish.service.record_run` (`audit.json` + input and pipeline copies), `tests/unit/test_service.py` |
| FR-13 | **Engineer override** of a decision, stored alongside the original decision. | PR | C | **Implemented 2026-09-28**: append-only `overrides.jsonl`, pipeline decision unchanged — `agnidrish.service.add_override`, API `POST /api/runs/{id}/overrides` |
| FR-14 | **Lot summary**: lot statistics, lot-level flags, decision counts, review rate. | EI | S | Integration test — **implemented 2026-09-28**: `agnidrish.service.lot_summary` |
| FR-20 | **Site calibration**: fit a frozen pipeline on a site's historical lots (with measured `value_168h`) by re-running the pre-registered E1–E6 development procedure; lot-grouped splits; a `test` split is never read. | EI (ADR-006) | S | Unit tests — `agnidrish.fit`, `scripts/fit_pipeline.py`, `tests/unit/test_fit.py` |
| FR-21 | **Screening service**: HTTP API + web UI for upload, decisions, evidence cards, overrides, replay; later checkpoints and evaluation-only columns removed before screening. | EI (ADR-006) | S | Integration tests — `app/server.py`, `tests/integration/test_api.py` |
| FR-22 | **Data adapter / normaliser**: map tester exports in three layouts (row per reading, per component and parameter, per component) to the canonical schema via a site input profile; checkpoint snapping with tolerance, parameter aliases, SI-prefix unit conversion, duplicate-reading policy; layout detection for engineer confirmation. Unusable readings are flagged, never guessed. Supersedes the rename-only mapping of FR-01. | EI (ADR-007) | M | Unit tests — `agnidrish.ingest`, `agnidrish.units`, `tests/unit/test_ingest.py`; API test with a foreign export |
| FR-23 | **Specification-limit sources**: limits from the measurement file, an engineer's per-upload entry, a site limits table (optionally per device family, with unit) or the parameter registry, in configured precedence, with per-row provenance (`spec_source`); an explicit "no limit applies" declaration. | EI (ADR-007) | M | Unit tests — `tests/unit/test_ingest.py` |
| FR-24 | **Per-parameter forecast availability**: a parameter without a fitted 168 h predictor is decided by the quality gate, datasheet and lot-relative rules (Module B off), and the output states it (`forecast_status`). | EI (ADR-007) | M | Unit tests; development evidence: leave-one-out −L4/−L5 on validation lots (ablation-plan §2) |
| FR-25 | **Site configuration**: one file per organisation holding input profile, parameter registry (aliases, unit, limits, direction), limit sources and calibration settings; stored with every run. | EI (ADR-007) | M | Unit test loads every config in `configs/sites/` |
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

Database, authentication (the service runs behind the site's proxy / single sign-on), deep
sequence models, digital-twin framing, RUL estimation, multi-checkpoint (96 h / 168 h) decision
modes. Frontend, API server and deployment moved into scope 2026-09-28 (ADR-006).
