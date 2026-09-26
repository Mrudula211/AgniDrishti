# Requirements Traceability

Status: Draft · Last updated: 2026-09-26

Chain: **PS Requirement → Engineering Interpretation → Proposed Implementation →
Experiment → Metric → Evidence Required**.

Every major feature shown in the final presentation must appear in this table.
A feature with no PS requirement row must be justified as supporting one (see
§2) or dropped. "Evidence status" stays **TBD** until a recorded run exists.

## 1. PS requirements

**Updated 2026-09-26:** requirements are now verified against the official PS
text (R0, [official-ps-26170.md](official-ps-26170.md)). OPS IDs are the
official requirements; the PSR IDs used below map to them as follows:
PSR-01→OPS-01, PSR-02/07→OPS-02, PSR-03→OPS-03, PSR-04→OPS-04,
PSR-05→OPS-05, PSR-06→OPS-07; OPS-06 (MAE) is new — see its row.

| PS Req. | Engineering interpretation | Proposed implementation | Experiment | Metric | Evidence required | Evidence status |
|---|---|---|---|---|---|---|
| PSR-07 Absolute limits are insufficient | A baseline is needed to show what static screening misses | FR-03 absolute spec check | E1 | Recall, FNR, FPR on latent-defect proxy labels | E1 run showing which labelled cases pass the static check | TBD — experiment not yet executed |
| PSR-02 Module A: lot-relative anomaly | "Normal" is lot-specific; score position within lot | FR-04 robust z (level), FR-02 lot checks | E2 | Recall, precision, F1, PR-AUC, FPR; per-lot variation of FPR | E2 vs E1 delta; sensitivity to lot size and lot contamination | TBD — experiment not yet executed |
| PSR-02 + PSR-01 Temporal abnormality | Drift relative to lot carries signal not visible in level | FR-05 lot-relative drift, FR-06 trajectory features | E3 | Same as E2; recall on "normal level, abnormal drift" scenario | E3 vs E2 delta, per scenario | TBD — experiment not yet executed |
| PSR-03 Module B: 0h+24h → 168h (confirmed by R0) | Early point prediction from 2 points; baselines first | FR-07 (persistence, lot-increment, linear) | E4 | MAE, RMSE, tail error (error on top-k% true 168h values) | Best simple model vs persistence baseline on held-out lots | TBD — experiment not yet executed |
| OPS-06 Drift Prediction Accuracy (official metric) | Module B is scored by MAE on Value_168h against hidden ground truth; MAE is the primary Module B metric | FR-07, FR-15 | E4 | **MAE** (primary, official); RMSE, tail error (internal) | MAE on held-out lots vs persistence baseline, data category stated | TBD — experiment not yet executed |
| PSR-04 Early reject on safety slope ("calculated safety slope", R0) | Convert predicted Value_168h into a drift rate and compare to the safety slope; **both the drift-rate formula and the slope calculation are unspecified by R0 and are our documented design choices** ([ADR-002](../../decisions/ADR-002-safety-slope-and-drift-rate.md), accepted 2026-09-26) | FR-09 safety-slope rule | E4 | Recall/precision of "exceeds safety slope" vs drift computed from true Value_168h | Confusion matrix at T24; sensitivity to the slope-calculation choice | TBD — experiment not yet executed |
| PSR-05 FN catastrophic | Bias toward recall; abstain when unsure | FR-08 interval, FR-10 REVIEW, NFR-01 fail-safe | E5, E6 | FNR, defect escape rate, review rate, auto-cleared %, interval coverage | Recall–review-rate curve; escape rate at chosen operating point | TBD — experiment not yet executed |
| PSR-06 Explainability | Evidence must be the actual decision inputs | FR-11 explanation, FR-12 audit record | E6 (+ qualitative review) | Completeness of evidence fields; reviewer comprehension (qualitative) | Sample explanations for each decision type, generated from real runs | TBD — experiment not yet executed |
| PSR-01 Sparse checkpoints | No dense-sequence models; checkpoint-specific features | FR-06 | E3/E4 | — | Documented feature availability matrix + leakage tests passing | TBD |
| OPS-05 Anomaly Detection Score (formula unknown) | Hidden scoring likely needs a binary flag per component | FR-16 binary output | E6 | Recall/FNR under both REVIEW mappings | Both mappings reported | TBD — experiment not yet executed |

## 2. Supporting (non-PS) features and their justification

| Feature | Supports | Kept only if | Experiment |
|---|---|---|---|
| Data quality gate | PSR-05 (no silent PASS) | Always (safety) | Fault-injection tests |
| Prediction interval | PSR-04, PSR-05 | Coverage close to target on held-out lots **and** E5 changes decisions usefully | E5 |
| Risk fusion / PASS-REVIEW-REJECT | PSR-05 | E6 improves escape rate at acceptable review rate vs E5 simple rules | E6 |
| Trajectory map (visual) | PSR-06 | Generated from real run outputs | — |
| Advanced predictor (GBM / hierarchical) | PSR-03 | Beats simple baselines on held-out lots incl. tail | E4b (conditional) |
| Isolation Forest comparator | PSR-02 | Comparator only | E2b (conditional) |

## 3. Presentation claims → evidence

| Planned claim | Required evidence | Status |
|---|---|---|
| "Static screening misses latent-defect cases on our evaluation data" | E1 results, data category stated | TBD — experiment not yet executed |
| "Lot-relative analysis improves recall at comparable FPR" | E2 vs E1 | TBD — experiment not yet executed |
| "Trajectory features add detection of normal-level drifting parts" | E3 per-scenario | TBD — experiment not yet executed |
| "168h can be estimated at 24h with error X" | E4 | TBD — experiment not yet executed |
| "Uncertainty-aware REVIEW reduces escapes at review rate Y" | E5/E6 | TBD — experiment not yet executed |
