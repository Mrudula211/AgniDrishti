# Data Dictionary (canonical schema — provisional)

Status: Draft · Last updated: 2026-09-26

This is the **target internal schema**, designed from R2 §H and R3 §9. It is not
the official PS schema (unknown). When real data arrives, map its columns to
these names in one place and record the mapping below.

## 1. Measurement table (one row per component per parameter)

| Column | Type | Unit | Required | Available at | Description | Source of field |
|---|---|---|---|---|---|---|
| `component_id` | string | — | Yes | — | Unique component identifier | R2, R3 |
| `lot_id` | string | — | Yes (Module A) | — | Manufacturing lot | R2, R3 |
| `wafer_id` | string | — | No | — | Wafer within lot | R2 (proposal) |
| `device_family` | string | — | No | — | Part type / family | R2, R3 (proposal) |
| `parameter` | string | — | Yes | — | Measured parameter name (e.g. leakage current) | `[AS]` A-09 |
| `unit` | string | — | Yes | — | Unit of the parameter values | `[AS]` |
| `temperature_c` | float | °C | No | — | Burn-in temperature | R3 (proposal) |
| `value_0h` | float | `unit` | Yes | T0 | Measurement at 0h | R2, R3 |
| `value_24h` | float | `unit` | Yes | T24 | Measurement at 24h | R2, R3 |
| `value_96h` | float | `unit` | Yes* | T96 | Measurement at 96h | R2, R3 |
| `value_168h` | float | `unit` | Yes* | T168 | Measurement at 168h. **Target for Module B. Never a feature before T168.** | R2, R3 |
| `spec_min` | float | `unit` | No | — | Lower spec limit (if any) | R3 |
| `spec_max` | float | `unit` | No | — | Upper spec limit (if any) | R2, R3 |
| `data_category` | enum | — | Yes | — | `official` / `external` / `synthetic` | CLAUDE.md |
| `dataset_version` | string | — | Yes | — | Version / hash of the source file | CLAUDE.md |

\* Required for training/evaluation; may be absent at inference time for
earlier checkpoints.

## 2. Label columns (evaluation only — never features)

| Column | Type | Definition | Status |
|---|---|---|---|
| `label_spec_168h` | bool | `value_168h` outside [`spec_min`, `spec_max`] | **Secondary** proxy ([ADR-004](../../decisions/ADR-004-primary-proxy-label.md)) |
| `label_safety_slope` | bool | (`value_168h` − `value_0h`)/168 h > Δ_allow/168 h, or `value_168h` beyond the datasheet limit — [ADR-002](../../decisions/ADR-002-safety-slope-and-drift-rate.md) §11 | **Primary** proxy ([ADR-004](../../decisions/ADR-004-primary-proxy-label.md)); formula accepted, Δ_allow swept (no default) |
| `label_latent` | bool | Official failure label, if provided | Unknown |
| `scenario` | string | Synthetic scenario tag | Synthetic data only |

## 3. Derived features (defined here, computed later)

| Feature | Formula | Available at | Notes |
|---|---|---|---|
| `delta_24` | v24 − v0 | T24 | — |
| `rel_delta_24` | (v24 − v0) / \|v0\| | T24 | Undefined when v0 ≈ 0 → flag |
| `slope_0_24` | (v24 − v0) / 24 | T24 | per hour |
| `slope_24_96` | (v96 − v24) / 72 | T96 | per hour; unequal spacing handled |
| `slope_change` | slope_24_96 − slope_0_24 | T96 | curvature proxy |
| `z_level_t` | (v_t − median_lot(v_t)) / (1.4826 · MAD_lot(v_t)) | T | per checkpoint t; MAD = 0 → flag |
| `z_drift_t` | robust z of the drift within lot | T | — |
| `spec_margin_t` | (spec_max − v_t) / (spec_max − median_lot(v_t)) or absolute margin | T | exact form decided in E1/E2 |

## 4. Feature availability matrix (leakage control)

| Feature group | T24 | T96 | T168 |
|---|---|---|---|
| v0, v24 and derived | ✔ | ✔ | ✔ |
| v96 and derived | ✘ | ✔ | ✔ |
| v168 | ✘ | ✘ | ✔ (target / final screening only) |
| Labels | ✘ | ✘ | ✘ (evaluation only) |

## 5. Raw → canonical mapping log

| Dataset | Raw column | Canonical column | Transformation |
|---|---|---|---|
| — | TBD — no dataset inspected yet | — | — |
