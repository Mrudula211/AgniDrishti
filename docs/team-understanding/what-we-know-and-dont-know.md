# What We Know and What We Don't

Status: Draft · Last updated: 2026-09-26

Label key: **Official** = PS text · **Verified** = primary source we opened ·
**Proposal** = our design choice · **Assumption** = believed, not checked ·
**Unknown** = nobody has told us · **To validate** = needs an experiment.

## Official (from the PS text)

- Module A: lot-relative ("Dynamic") outlier detection.
- Module B: Value_0h + Value_24h → predict Value_168h. **Not 96h.**
- Early rejection if predicted 168h drift rate > "calculated safety slope".
- Missing a bad part is catastrophic; MAE on hidden 168h values; explainability.
- 0/24/96/168h, 125 °C, Iddq/leakage/delay are **examples**, not fixed facts.
- No dataset is published. No standard (AEC, JEDEC, ESCC) is named.

## Verified elsewhere

- Automotive DPAT (AEC-Q001): lot limits = median ± 6 × (IQR/1.35).
- European space specs (ESCC 9000): burn-in drift from the 0h value must stay
  within a per-parameter allowance; lots fail if > 5 % of parts fail.
- A 2011 AMD patent flags parts by comparing pre- and post-burn-in data.
- Published ML for burn-in exists (batch-level before burn-in, 2025; lot health
  from process data, 2023; laser early-failure from dense data, 2022).
- SIH 2026 idea round: 6-slide PDF, fixed template, due **30 Sep 2026**.

## Proposals (ours — may change)

Robust lot statistics; safety slope = per-parameter drift allowance ÷ 168 h
plus datasheet-limit backstop (decided 2026-09-26, ADR-002; allowance value not yet set);
simple 168h predictor; prediction interval; PASS/REVIEW/REJECT; evidence-card
explanations; synthetic + NASA data strategy.

## Assumptions

Lot IDs exist; most parts in a lot are healthy; one parameter at a time;
output is advisory; measurement times are nominal.
Full list: [assumptions-and-constraints.md](../research/ps-analysis/assumptions-and-constraints.md).

## Unknown

How the safety slope, drift rate and Anomaly Detection Score are calculated;
what "defective" means in hidden labels; schema; lot sizes; acceptable review
load; whether early rejection physically removes a part.
Register: [drawbacks-and-risks.md](../research/drawbacks-and-risks.md) Part A.

## To be validated by experiment (all TBD — experiment not yet executed)

Does lot comparison beat the static limit? Does drift help? Does a simple
predictor beat "168h = 24h"? Is the interval's coverage close to target on new
lots? Does REVIEW reduce escapes at an acceptable review rate?
Plan: [experiment-plan.md](../research/experiments/experiment-plan.md).
