# Requirements Traceability

Status: Draft · Last updated: 2026-09-29

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
| PSR-07 Absolute limits are insufficient | A baseline is needed to show what static screening misses | FR-03 absolute spec check | E1 | Recall, FNR, FPR on latent-defect proxy labels | E1 run showing which labelled cases pass the static check | Recorded (SYNTHETIC, test lots, 30 positives): static screening recall 0.133, escape rate 0.867 — [ablation-plan.md](../experiments/ablation-plan.md) §3 step 1 |
| PSR-02 Module A: lot-relative anomaly | "Normal" is lot-specific; score position within lot | FR-04 robust z (level), FR-02 lot checks | E2 | Recall, precision, F1, PR-AUC, FPR; per-lot variation of FPR | E2 vs E1 delta; sensitivity to lot size and lot contamination | Recorded: level alone leaves recall at 0.133 on the drift-based primary label; scenario-truth recall 0.055 → 0.127 (F2) — [ablation-plan.md](../experiments/ablation-plan.md) §3 |
| PSR-02 + PSR-01 Temporal abnormality | Drift relative to lot carries signal not visible in level | FR-05 lot-relative drift, FR-06 trajectory features | E3 | Same as E2; recall on "normal level, abnormal drift" scenario | E3 vs E2 delta, per scenario | Recorded: recall 0.133 → 0.667 at FPR 0.032 (F1) — [ablation-plan.md](../experiments/ablation-plan.md) §3 |
| PSR-03 Module B: 0h+24h → 168h (confirmed by R0) | Early point prediction from 2 points; baselines first | FR-07 (persistence, lot-increment, linear) | E4 | MAE, RMSE, tail error (error on top-k% true 168h values) | Best simple model vs persistence baseline on held-out lots | Recorded (validation lots): population-increment beats persistence on MAE (iddq 0.297 vs 0.338 µA; tpd 0.0472 vs 0.0496 ns) — [ablation-plan.md](../experiments/ablation-plan.md) §3 |
| OPS-06 Drift Prediction Accuracy (official metric) | Module B is scored by MAE on Value_168h against hidden ground truth; MAE is the primary Module B metric | FR-07, FR-15 | E4 | **MAE** (primary, official); RMSE, tail error (internal) | MAE on held-out lots vs persistence baseline, data category stated | Recorded on synthetic validation lots (previous row); MAE on the hidden SIH data: TBD — experiment not yet executed (cannot be measured by us) |
| PSR-04 Early reject on safety slope ("calculated safety slope", R0) | Convert predicted Value_168h into a drift rate and compare to the safety slope; **both the drift-rate formula and the slope calculation are unspecified by R0 and are our documented design choices** ([ADR-002](../../decisions/ADR-002-safety-slope-and-drift-rate.md), accepted 2026-09-26) | FR-09 safety-slope rule | E4 | Recall/precision of "exceeds safety slope" vs drift computed from true Value_168h | Confusion matrix at T24; sensitivity to the slope-calculation choice | Recorded: the safety-slope rule caught nothing that E3 had missed (F3) — [ablation-plan.md](../experiments/ablation-plan.md) §5 |
| PSR-05 FN catastrophic | Bias toward recall; abstain when unsure | FR-08 interval, FR-10 REVIEW, NFR-01 fail-safe | E5, E6 | FNR, defect escape rate, review rate, auto-cleared %, interval coverage | Recall–review-rate curve; escape rate at chosen operating point | Recorded: R* = 0.95 not reached; test recall 0.800 at 10.4 % review, escape rate 0.200 (F5) — [ablation-plan.md](../experiments/ablation-plan.md) §3, §5 |
| PSR-06 Explainability | Evidence must be the actual decision inputs | FR-11 explanation, FR-12 audit record | E6 (+ qualitative review) | Completeness of evidence fields; reviewer comprehension (qualitative) | Sample explanations for each decision type, generated from real runs | Recorded: evidence cards are generated from real runs (`tests/unit/test_decision.py`, `tests/unit/test_service.py`); reviewer comprehension (qualitative): TBD — experiment not yet executed |
| PSR-01 Sparse checkpoints | No dense-sequence models; checkpoint-specific features | FR-06 | E3/E4 | — | Documented feature availability matrix + leakage tests passing | Leakage tests pass (`tests/unit/test_layers.py`, `tests/unit/test_service.py`, `tests/unit/test_fit.py`); feature availability matrix in the data dictionary |
| OPS-05 Anomaly Detection Score (formula unknown) | Hidden scoring likely needs a binary flag per component | FR-16 binary output | E6 | Recall/FNR under both REVIEW mappings | Both mappings reported | Recorded with REVIEW counted as flagged (ADR-005); the alternative mapping (REVIEW not flagged) is not reported: TBD — experiment not yet executed |

## 2. Supporting (non-PS) features and their justification

| Feature | Supports | Kept only if | Experiment |
|---|---|---|---|
| Data quality gate | PSR-05 (no silent PASS) | Always (safety) | Fault-injection tests |
| Prediction interval | PSR-04, PSR-05 | Coverage close to target on held-out lots **and** E5 changes decisions usefully | E5 |
| Decision rules / PASS-REVIEW-REJECT (no fused score, ADR-001 Rev. 1) | PSR-05 | E6 improves escape rate at acceptable review rate vs E5 simple rules | E6 |
| Trajectory map (visual) | PSR-06 | Generated from real run outputs | — |
| Advanced predictor (GBM / hierarchical) | PSR-03 | Beats simple baselines on held-out lots incl. tail | E4b (conditional) |
| Isolation Forest comparator | PSR-02 | Comparator only | E2b (conditional) |

## 3. Presentation claims → evidence

| Planned claim | Required evidence | Status |
|---|---|---|
| "Static screening misses latent-defect cases on our evaluation data" | E1 results, data category stated | Supported on SYNTHETIC data: 0.867 of positives escape static screening (test, 30 positives) |
| "Lot-relative analysis improves recall at comparable FPR" | E2 vs E1 | Drift: yes (0.133 → 0.667, FPR 0.012 → 0.032). Level alone: no gain on the primary label (0.133 → 0.133) |
| "Trajectory features add detection of normal-level drifting parts" | E3 per-scenario | Supported on SYNTHETIC data by lot-relative drift (E3); no separate trajectory-shape model was built |
| "168h can be estimated at 24h with error X" | E4 | MAE 0.297 µA (iddq) and 0.0472 ns (tpd) on SYNTHETIC validation lots; not a claim about real hardware |
| "Uncertainty-aware REVIEW reduces escapes at review rate Y" | E5/E6 | Not supported for the interval (E5 = E4 on detection); the tuned REVIEW threshold (E6) gives recall 0.800 at 10.4 % review, R* = 0.95 not reached |
