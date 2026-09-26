# Data Pipeline (Provisional)

Status: Proposed · Last updated: 2026-09-26

Covers ingestion, data zones, L0 (data quality gate) and L1 (absolute spec check).

## 1. Data zones and flow

```
data/raw/{official,...}   (immutable, hashed)
data/external/<dataset>/  (as downloaded, manual step)
data/synthetic/           (generated from config + seed)
        │  mapping to canonical schema (data-dictionary.md)
        ▼
data/interim/             (canonical, validated, flags attached)
        │  split assignment (by lot), feature computation per checkpoint
        ▼
data/processed/           (experiment-ready tables, one per dataset version)
```

Every derived file records: source file hash, config, commit, data category.

## 2. Ingestion and schema mapping

| Item | Content |
|---|---|
| Purpose | Convert any source into the canonical schema without changing values |
| Inputs | Raw file + mapping config |
| Outputs | Canonical table + mapping log |
| Assumptions | A-04, A-08 |
| Candidate methods | Explicit column mapping in config; unit normalisation only when unit is known |
| Alternatives | Auto-detection of columns — rejected (hidden assumptions) |
| Risks | Silent unit mismatch; mis-mapped checkpoint columns |
| Validation | Unit tests with small fixtures; round-trip value checks |
| Expected evidence | Mapping log for every dataset in `data-dictionary.md` §5 |

## 3. L0 — Data Quality Gate

| Item | Content |
|---|---|
| Purpose | Stop invalid data from producing confident decisions (NFR-01) |
| Inputs | Canonical lot table at checkpoint T |
| Outputs | Per-component flags; per-lot flags; `blocking` boolean |
| Assumptions | A-05 (min lot size), A-07 (majority healthy), U-09, U-10 |
| Candidate checks | Required columns present; numeric & finite; duplicate `component_id` within lot; missing checkpoint values; non-physical values (e.g. negative where impossible — per parameter config); lot size < `min_lot_size`; MAD ≈ 0 or too few distinct values; suspected multi-modality (simple: gap/histogram rule or wafer split; GMM only if needed); single-point glitch (v24 far off a line through v0 and v96 — T96 only) |
| Alternatives | Imputation of missing values — **rejected for decisions** (imputed value could produce PASS); allowed only for exploratory analysis |
| Risks | Over-flagging → review flood; thresholds are guesses until E0 |
| Validation | Fault-injection unit tests; flag rates on synthetic scenarios with known faults |
| Expected evidence | Per-check detection on injected faults; flag rate on clean data (TBD — experiment not yet executed) |

Rule: blocking component flag → decision REVIEW with reason; blocking lot flag
→ all components in the lot REVIEW + lot-level alert.

### Implementation status (P1, 2026-09-26) — `src/agnidrish/quality.py`

All implemented flags are blocking. Lot checks run per (lot, parameter) on valid
rows only, and only on the columns available at the checkpoint.

| Check | Flag | Status |
|---|---|---|
| Required columns present | `SchemaError` | Implemented |
| Missing identifier (component / lot / parameter) | `MISSING_IDENTIFIER` | Implemented |
| Duplicate `component_id` within lot + parameter | `DUPLICATE_COMPONENT` | Implemented |
| Missing checkpoint value | `MISSING_VALUE` | Implemented |
| Non-numeric / non-finite value or limit | `NON_NUMERIC`, `NON_FINITE` | Implemented |
| Non-physical value (per-parameter bounds, optional) | `OUT_OF_PHYSICAL_RANGE` | Implemented |
| No spec limit on either side; spec_min > spec_max | `NO_SPEC_LIMIT`, `INVALID_SPEC_LIMITS` | Implemented |
| Lot smaller than `min_lot_size` (valid rows) | `LOT_TOO_SMALL` | Implemented |
| Lot MAD of a level ≤ per-parameter floor | `LOW_LEVEL_DISPERSION` | Implemented |
| Lot MAD of a between-checkpoint difference ≤ floor | `LOW_DRIFT_DISPERSION` | Implemented |
| Units consistent within a parameter | — | **Not implemented** — needs a unit convention decision |
| Suspected multi-modal lot | — | **Not implemented** — rule and threshold need design + E2 bimodal-lot evidence |
| Single-point glitch | — | **Not implemented** — T96 extension only |

Thresholds (`min_lot_size`, per-parameter `scale_floor`, `physical_bounds`) have no
defaults in code; they will live in `configs/data/` when the first script (E0) uses them.

## 4. L1 — Absolute Specification Check

| Item | Content |
|---|---|
| Purpose | Reproduce conventional screening; the baseline every other layer is compared to |
| Inputs | v_t, spec_min, spec_max |
| Outputs | `spec_pass_t` (bool), `spec_margin_t` |
| Assumptions | A-12 (upper limit relevant); limits supplied per device family |
| Candidate methods | Direct comparison; optional guard-band as config |
| Alternatives | — |
| Risks | Missing limits → cannot evaluate → REVIEW |
| Validation | Unit tests on boundary values (equal to limit, just above/below) |
| Expected evidence | E1 results: TBD — experiment not yet executed |

## 5. Split assignment (for experiments)

Defined in [evaluation-protocol.md](../research/experiments/evaluation-protocol.md):
group by `lot_id`; train / validation / calibration / test lots disjoint; test
lots frozen before any modelling.
