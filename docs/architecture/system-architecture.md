# System Architecture (Provisional)

Status: Proposed · Last updated: 2026-09-26 · Decision: [ADR-001](../decisions/ADR-001-initial-architecture.md)

> Layer set revised 2026-09-26 (ADR-001 Revision 1): L3 merged into L2, no fused risk score, 7 layers.
>
> **Provisional.** Nothing here is implemented or validated. Each layer after
> the absolute specification check stays in the design only if the ablation
> ([ablation-plan.md](../research/experiments/ablation-plan.md)) shows it adds value.

## 1. Pipeline

```
Burn-in data (one lot, one checkpoint)
        │
        ▼
[L0] Data Quality Gate ──────────── blocking issue ──► REVIEW (fail-safe)
        │
        ▼
[L1] Absolute Specification Check ── violation ──────► REJECT candidate
        │
        ▼
[L2] Lot-Relative Analysis of level AND drift  (robust z; checkpoint-specific drift features)
        │
        ▼
[L4] 168h Prediction  (point estimate)
        │
        ▼
[L5] Uncertainty Estimation  (prediction interval) — conditional on E5
        │
        ▼
[L6] Decision Rules  (ordered, documented; incl. safety-slope rule; no fused score)
        │
        ▼
     PASS / REVIEW / REJECT  + binary flag
        │
        ▼
[L7] Engineer-Readable Explanation + Audit Record
```

## 2. Decision checkpoints

The same pipeline runs at each checkpoint with only the data available then.

| Checkpoint | Available values | Layers active | Purpose |
|---|---|---|---|
| **T24** | v0, v24 | L0–L2, L4–L7 (L2 drift = one increment) | **Module B** (official: Value_0h + Value_24h → Value_168h) and early reject (OPS-03, OPS-04) |
| **T96** | v0, v24, v96 | L0–L2, L4–L7 (L2 drift adds slope change) | Optional extension, **not** Module B; kept only if it adds value and is reported separately |
| **T168** | all | L0–L2 (drift descriptive) | Final Module A screening; ground truth for L4/L5 evaluation |

Module B inputs resolved by the official PS text (R0) — [discrepancy-log](../research/ps-analysis/discrepancy-log.md) DL-01.

## 3. Module index

| Layer | Document | PS link |
|---|---|---|
| L0 Data quality gate | [data-pipeline.md](data-pipeline.md) | PSR-05 |
| L1 Absolute spec check | [data-pipeline.md](data-pipeline.md) | PSR-07 |
| L2 Lot-relative analysis (level + drift) | [ml-pipeline.md](ml-pipeline.md) | PSR-01, PSR-02, OPS-04 |
| ~~L3~~ | Retired — merged into L2 (ADR-001 Rev. 1) | — |
| L4 168h prediction | [ml-pipeline.md](ml-pipeline.md) | PSR-03 |
| L5 Uncertainty (conditional) | [ml-pipeline.md](ml-pipeline.md) | PSR-04, PSR-05 |
| L6 Decision rules | [decision-engine.md](decision-engine.md) | PSR-04, PSR-05 |
| L7 Explanation + audit | [explainability.md](explainability.md) | PSR-06 |

## 4. Design principles

1. **Each layer is independently removable** — required for ablation.
2. **Transparent before opaque** — every layer's output is a named, numeric
   quantity an engineer can recompute.
3. **Fail-safe** — any missing/invalid input or degenerate statistic → REVIEW.
4. **Checkpoint discipline** — features at T use only data measured at ≤ T.
5. **Configuration, not constants** — all thresholds in `configs/`.
6. **Batch per lot** — lot statistics require the whole lot at a checkpoint.

## 5. Planned code layout (created only when each layer is implemented)

```
src/agnidrish/
    data/        L0 schema mapping, validation (P1)
    features/    L2 lot-relative level + drift scores (P3)
    models/      L4 predictors, L5 intervals (P4–P5)
    decision/    L1 spec check, L6 rules (P2, P5)
    evaluation/  metrics, splits, leakage checks (P1–P2)
    utils/       only if a genuinely shared helper appears
```

No directory is created until its first tested function exists.

## 6. What is deliberately not in the architecture

| Excluded | Reason | Reconsider when |
|---|---|---|
| LSTM / Transformer / autoencoder | ≤ 4 points per component (M-01) | Dense data appears and simple models are shown insufficient |
| Per-component power-law fit | Not identifiable at T24; zero dof at T96 (M-02) | Population-level shape model shows value in E4b |
| Learned risk index (CRI) as probability | No real labels to calibrate (M-08) | Real labels available |
| Digital twin / RUL | No time-to-failure data (N-05, N-06) | — |
| GMM lot-modality check | Simpler checks first (M-07) | Simple checks fail on bimodal synthetic lots |
| Web app / API / DB | Current phase (P0) | P7 |

## 7. Re-evaluation (2026-09-26, after verified prior-art pass)

Against R0, verified sources (S-xx, [literature-review](../research/prior-art/literature-review.md)),
sparse data, unknown safety slope / score. "Value measured?" is TBD for every
layer — no experiment has run.

| Layer | PS requirement | Problem solved | Evidence for it | Data needed | Key assumption | Could fail when | Evaluated by | Removable? | Verdict `[PR]` |
|---|---|---|---|---|---|---|---|---|---|
| L0 Quality gate | None directly; supports OPS-05 | Silent PASS on bad input | Engineering necessity | Any | Checks are cheap | Over-flagging | Fault injection | No (safety) | **Keep** |
| L1 Spec check | OPS-02 (static limits are the reference) | Baseline | R0; S-02 absolute limits | Limits | Limits supplied | Limits missing → REVIEW | E1 | No (baseline) | **Keep** |
| L2 Lot level | **OPS-02 Module A** | Peer-abnormal parts | S-01 DPAT is established practice | lot_id | Majority healthy | Small / contaminated / bimodal lots | E2 | No (PS) | **Keep.** Baseline = AEC-Q001 formula (median ± k·IQR/1.35, S-01) with MAD as variant — AEC formula now verified |
| L2 drift + L3 trajectory | OPS-01 ("drift over time"), OPS-04 | Normal-level, abnormal-drift parts | S-02/S-06 (drift screening exists) | v0, v24 | Drift informative at 24h | Late-onset defects | E3 | Partly | **Merge.** At T24 L3 has one increment — the same quantity L2-drift scores. Treat as one "drift" layer; slope-change only in the T96 extension |
| L4 168h prediction | **OPS-03, OPS-06** | Module B target | R0 mandatory | v0, v24, training lots | Relationship transfers across lots | 7× extrapolation, tail | E4 (MAE + tail) | No (PS) | **Keep**, simplest models first; MAE and flagging may need different handling (D-13) |
| Safety-slope rule | **OPS-04** | Early rejection | S-02/S-03 analogue | Δ allowance | ADR-002 | Wrong Δ | E4(b) | No (PS) | **Keep**, defined in ADR-002 (accepted: Δ-allowance slope + limit backstop) |
| L5 Interval | Not in PS | Uncertainty for REVIEW (OPS-05) | S-10; S-11 warns lots break exchangeability | Calibration lots | Enough lots | Lot shift; few lots | E5 per-lot coverage | **Yes** | **Conditional** — keep only if E5 coverage holds per lot and it changes decisions usefully |
| L6 Decision rules | OPS-04/05/07 require a flag + justified classification; three-way not required | Route doubt to humans | S-13/S-14 | — | REVIEW handled by people | Review flood | E6 curves | Three-way part yes | **Keep ordered rules; drop any weighted "risk fusion" score.** Must also emit a binary flag (anomaly-detection-score.md §5) |
| L7 Explanation | **OPS-07** | QA can verify | R0 | Evidence fields | Templates match logic | Drift between text and logic | Template tests | No (PS) | **Keep** |

Net change: 8 layers → 7 (L2-drift and L3 merged); "risk fusion" replaced by
"decision rules" with no fused score. **Confirmed by user 2026-09-26** —
ADR-001 Revision 1.
