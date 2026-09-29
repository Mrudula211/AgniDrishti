# ADR-007 — Dataset-Agnostic Ingestion and Site Configuration

Status: Accepted · Date: 2026-09-28 · Requested by the team ("must work with real-world burn-in data from different testing environments … without redesigning the system")

## Context

The pipeline was built and evaluated on our SYNTHETIC development data, whose files already use
the canonical schema. An inspection on 2026-09-28 found the core layers (quality gate statistics,
datasheet check, lot-relative scores, Module B predictors, conformal interval, decision rules,
explanations) contain no dataset-specific names. They read canonical columns only. The coupling is at the
edges:

| # | Where | Coupling |
|---|---|---|
| C1 | `service.prepare_input`, `schema.to_canonical` | One input layout only (one row per component and parameter, checkpoint columns); mapping could only rename columns |
| C2 | same | The checkpoint hour had to be encoded in a column name; readings logged at 23.5 h or in an "hours" column were unusable |
| C3 | `schema.required_columns`, quality gate | Specification limits had to be columns of the measurement file, else every row went to REVIEW |
| C4 | — (FR-02 "units pending") | No unit handling; nA and µA readings in one lot would share lot statistics |
| C5 | — | Parameter names had to match exactly (`IDDQ` ≠ `iddq`) |
| C6 | `pipeline.screen` / `decide` | A parameter without a fitted 168 h predictor had "missing evidence", so every row went to REVIEW, although Module A needs no fitting |
| C7 | `configs/deployment/*.yaml`, `AGNIDRISH_MAPPING` | Site knowledge (directions, mapping) scattered; no single place a new organisation fills in |
| C8 | `read_csv_bytes` | Comma-only CSV; a byte-order mark corrupted the first header |

## Decision

Separate the system into

```
raw export ─► ingest profile (layout adapter) ─► canonical schema ─► detection / forecasting ─► decision rules ─► explanation
                    ▲                                   ▲
      site config: input profile,         spec-limit sources (file / manual / table / registry)
      parameter registry, aliases, units
```

1. **Site configuration** (`agnidrish.site`, `configs/sites/<site>.yaml`, template `site_template.yaml`):
   input profile, parameter registry (name, tester aliases, unit, datasheet limits or an explicit
   `no_limit`, degradation direction), limit-source precedence and optional limits table (e.g. an export from
   a PLM/metadata system), calibration settings. One file per organisation / product line.
2. **Ingest layer** (`agnidrish.ingest`), the only code that knows about export formats:
   - three layout adapters: `row_per_parameter`, `row_per_measurement`, `row_per_component`, plus
     automatic detection (`suggest_profile`) that an engineer confirms in the UI;
   - checkpoint snapping: readings within ± `hour_tolerance_h` of 0/24/96/168 h are used, others are ignored and reported;
   - parameter aliases (case/punctuation-insensitive) → registry names; unregistered names pass through;
   - SI-prefix unit conversion to the registry unit (`agnidrish.units`); unconvertible readings are blanked and flagged;
   - duplicate-reading policy (`review` default, or first/last/mean);
   - specification limits resolved per row from the configured sources in order, with `spec_source` provenance.
   Problems never become guesses: the reading is blanked and the row carries an `ingest_flags` code that the
   quality gate turns into REVIEW (NFR-01).
3. **Quality gate** gains `DUPLICATE_MEASUREMENT`, `UNIT_NOT_CONVERTIBLE`, `MIXED_UNITS` (FR-02 unit check), and treats
   a registry `no_limit` declaration as "no limit applies" instead of "limit missing".
4. **Per-parameter forecast availability** (C6): rows of a parameter the pipeline has no fitted predictor for are decided
   by the same ordered rules with Module B switched off (R0, R1, R4, R5); `forecast_status` records this and the
   explanation states it. Module B is never extrapolated to a parameter it was not fitted on.
5. **Calibration** reads directions from the registry; parameters without a direction are not forecast but do not block the fit.
   Each fit also reports the rules without the forecast on its validation lots (leave-one-out −L4/−L5, ablation-plan §2),
   so a site sees how its un-forecast parameters are being decided.
6. **Audit**: each run stores the site config it used (`site.json`) and the input profile, so replay stays exact.
7. `schema.to_canonical` (rename-only) is removed: the `row_per_parameter` adapter with a `columns` map covers it.

## Consequences

- A new organisation fills in one YAML file (or maps columns once in the UI and saves the profile); no code changes for a
  new tester format, parameter set, unit scale, limit source or lot structure within the canonical checkpoints.
- The canonical checkpoints stay 0/24/96/168 h because Module B is defined on them (R0); other read-points are reported, not used.
- The "no forecast" decision path has only development evidence on SYNTHETIC data (validation lots). Its detection
  performance on real parameters is unknown until a site evaluates it: TBD — experiment not yet executed.
- Not built: direct database connectors (a limits table exported from any system is the supported interface; CLAUDE §0
  still excludes a database), Excel parsing (export to delimited text), per-parameter drift allowance (one Δ_allow per site).
