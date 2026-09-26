# ADR-005 — Operating Point and Review-Rate Policy

Status: Accepted · Date: 2026-09-26 · Confirmed by user (Decision 7, option 1)

## Context

Decision thresholds trade defect escapes against REVIEW workload and false
rejections. R0 states that false negatives are catastrophic; no acceptable
review rate is known (GAP-08).

## Options

| # | Policy | Outcome |
|---|---|---|
| 1 | Recall-first target + full curve | **Chosen** — matches the PS's asymmetric cost; workload reported, not hidden |
| 2 | Review-budget-first | Rejected — QA capacity unknown; a cap could force escapes |
| 3 | Curve only, no operating point | Rejected — leaves no single setting for evaluation or demo |

## Decision

1. **Pre-registration.** Before E6 is run, the team records in this ADR a target
   recall R* on the primary label (`label_safety_slope`, ADR-004), counting REVIEW as
   flagged. R* is a design choice, not a result. **R*: not yet set.**
2. **Selection.** Thresholds are chosen on **validation lots only** as the setting with
   the lowest review rate that reaches R*; ties broken by lower false-rejection rate.
   If no setting reaches R*, report that and the highest recall achieved — the target is
   not silently lowered.
3. **Reporting.** Every E5/E6 result shows the full recall–review-rate curve on held-out
   test lots, plus at the selected point: recall (with number of positives), defect escape
   rate, review rate, false-rejection rate, auto-cleared %, and the Δ_allow used.
4. **No retuning on test lots.** Test-lot results at the selected point are final for that run.
5. **Binary flag.** For any binary output (FR-16), REVIEW maps to "flagged" by default.

## Consequences

- decision-engine §2 and evaluation-protocol follow this policy.
- If ISRO / organisers give a review-capacity constraint, add it as a second constraint
  and supersede this ADR.
