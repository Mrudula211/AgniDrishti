# Data Ingestion and Site Configuration

Status: Draft · Last updated: 2026-09-28 · Decision: [ADR-007](../decisions/ADR-007-dataset-agnostic-ingestion.md)

How a new organisation connects its own burn-in data to AgniDrishti without changing code.

## 1. Layers

| Layer | Module | Knows about |
|---|---|---|
| Site configuration | `agnidrish.site`, `configs/sites/<site>.yaml` | the organisation: tester format, parameters, units, limits, calibration |
| Adapter / normaliser | `agnidrish.ingest`, `agnidrish.units` | export layouts, column names, hours, units, duplicates, limit sources |
| Canonical schema | `agnidrish.schema`, [data-dictionary](../research/datasets/data-dictionary.md) | the contract: one row per lot · component · parameter, `value_0h … value_168h`, `spec_min/max` |
| Detection, forecast, decision, explanation | `quality`, `spec`, `lot`, `predict`, `uncertainty`, `decision`, `explain` | canonical columns only |

Changing the data source changes only the first two rows.

## 2. Onboarding a new site

1. Copy `configs/sites/site_template.yaml` to `configs/sites/<site>.yaml`.
2. **Input**: set `layout` and map `columns` (role → column name in your export). Or upload a sample file in the web UI:
   it detects the layout and columns, you correct them, then *Save mapping* gives the `input` section as JSON.
3. **Parameters**: list each parameter with `unit`, datasheet limits (`spec_min`/`spec_max`, one side may be omitted) or
   `no_limit: true`, the tester `aliases`, and `direction` (`up`/`down`) if a 168 h forecast should be fitted.
4. **Limits**: order `limits.sources`; optionally point `limits.table` at a CSV (`parameter, spec_min, spec_max`,
   optional `device_family`, `unit`), e.g. exported nightly from a PLM or specification database.
5. **Calibrate** (optional, needs historical lots with 168 h readings):
   `python scripts/fit_pipeline.py --input history.csv --site configs/sites/<site>.yaml --category official`.
   Without calibration, use any pipeline: parameters it has no forecast model for are screened by the lot-relative
   and datasheet rules and reported as such.
6. **Run**: `python scripts/serve.py --site configs/sites/<site>.yaml --pipeline <pipeline.json>` ([deployment.md](deployment.md)).

## 3. Input layouts

| Layout | Example columns | Required roles |
|---|---|---|
| `row_per_parameter` | `Serial, Lot, Param, Units, Val_T0, Val_T24, USL` | component_id, lot_id, parameter + checkpoint columns (`hour_columns`, or detected from names such as `value_24h`) |
| `row_per_measurement` | `Serial, Lot, Test, ReadPoint, Result, Units` | component_id, lot_id, parameter, hour, value |
| `row_per_component` | `DUT, Lot, IDDQ_0h, IDDQ_24h, TPD_T0, TPD_T24` | component_id, lot_id + `<parameter>_<hour>h` / `<parameter>_T<hour>` columns (`measurement_columns`, or detected) |

Optional roles: `unit, spec_min, spec_max, wafer_id, device_family, temperature_c, nominal_value`.
Files: any delimited text (comma, semicolon, tab or pipe, detected), UTF-8 with or without byte-order mark, or Latin-1.
A header row is required.

## 4. What the normaliser does, and what it refuses to guess

| Situation | Behaviour | Row outcome |
|---|---|---|
| Reading at 23.5 h, tolerance 2 h | counted as the 24 h checkpoint | normal |
| Reading at 48 h | ignored, counted in the ingest report and warnings | — |
| Parameter `I_DDQ`, registry alias of `iddq` | renamed to `iddq` | normal |
| Unit `nA`, registry unit `uA` | value and file limits × 1e-3 | normal |
| Unit `V`, registry unit `uA` | value blanked, `UNIT_NOT_CONVERTIBLE` | REVIEW |
| Two units in one lot, no registry unit | `MIXED_UNITS` lot flag | REVIEW (lot) |
| Same component, parameter and checkpoint twice | policy `review`: blanked, `DUPLICATE_MEASUREMENT`; or first/last/mean | REVIEW / normal |
| Text or ±inf in a reading | blanked, `NON_NUMERIC` | REVIEW |
| No limit from any source | `spec_source = none`, `NO_SPEC_LIMIT` | REVIEW |
| Registry `no_limit: true` | `spec_source = declared_none` | normal (no datasheet check) |
| Parameter without a fitted 168 h model | `forecast_status = no validated model…`; rules R0, R1, R4, R5 | normal, explained |

## 5. Specification-limit sources

Sources are tried in the configured order; the first that gives a limit for a row supplies **both** sides, so a
deliberately one-sided limit is never completed from another source. `spec_source` is written to every row, shown
in the UI and on the evidence card.

| Source | Where it comes from |
|---|---|
| `manual` | entered by an engineer in the upload's mapping step (recorded in the run's audit record) |
| `file` | `spec_min` / `spec_max` columns of the export |
| `table` | site limits table; a row with `device_family` overrides the generic row for that family; its `unit` is converted |
| `registry` | `parameters.<name>.spec_min/spec_max` or `no_limit` in the site config |

## 6. Limits

- Canonical checkpoints are 0/24/96/168 h because Module B is defined on them (R0).
- One drift allowance Δ_allow per site; per-parameter allowances are not implemented.
- No direct database connection (CLAUDE §0); export limits to the table CSV.
- The rules without the forecast have development evidence on synthetic data only; each site fit reports them on the
  site's own validation lots.
