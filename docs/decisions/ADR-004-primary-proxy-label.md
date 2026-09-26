# ADR-004 — Primary Proxy Label for "Defective Part"

Status: Accepted · Date: 2026-09-26 · Confirmed by user (Decision 6, option 1)

## Context

R0 evaluates detection by an Anomaly Detection Score in which "missing a
defective part" is catastrophic, but does not define "defective" (GAP-05).
Every recall, FNR and escape-rate number depends on the label used.

## Options

| # | Primary label | Outcome |
|---|---|---|
| 1 | `label_safety_slope` | **Chosen** |
| 2 | Synthetic scenario truth | Rejected as primary — unavailable for NASA / official data, so results would not be comparable across data tracks |
| 3 | `label_spec_168h` | Rejected as primary — misses in-spec excessive drift, the PS's core concern |

## Decision

| Role | Label | Definition | Data |
|---|---|---|---|
| **Primary** | `label_safety_slope` | (V₁₆₈ − V₀)/168 h > Δ_allow/168 h, **or** V₁₆₈ beyond the datasheet limit ([ADR-002](ADR-002-safety-slope-and-drift-rate.md) §11), using the **measured** V₁₆₈ | Any data with V₀, V₁₆₈, limit and Δ_allow |
| Secondary | `label_spec_168h` | V₁₆₈ outside [spec_min, spec_max] | Any data with limits |
| Synthetic only, reported separately | Scenario truth | Component generated from a defect family ([synthetic-data-design.md](../research/datasets/synthetic-data-design.md) §3) | Synthetic |

Notes:

- `label_spec_168h` ⊆ `label_safety_slope` by construction (the limit backstop is part of the primary label).
- Scenario truth is the only label under which a **stable lot outlier** (Module A case,
  e.g. the PS's 45 µA part that does not drift) counts as positive; Module A is therefore
  also reported against scenario truth on synthetic data.
- Because the primary label depends on Δ_allow, which is swept (ADR-002), every
  detection result states the Δ_allow value used.
- Labels are evaluation-only and never features (CLAUDE §7).

## Consequences

- evaluation-protocol §1 names the label for every result; GAP-05 moves to "decided (proxy)".
- If organisers define "defective" differently, this ADR is superseded and results re-reported.
