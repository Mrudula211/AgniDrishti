# ADR-001 — Initial (Provisional) Architecture

Status: Proposed · Date: 2026-09-26

## Context

PS 26170 (as reported by R2/R3) asks for lot-relative anomaly detection
(Module A) and early 168h prediction from 0h + 24h with early rejection on a
safety slope (Module B), with catastrophic false negatives and explicit
explainability. Data is expected at 4 checkpoints per component. No official
dataset or PS text is in hand. Three research reports exist (R1 methodology,
R2 aggressive blueprint, R3 conservative correction) plus an assessment (R4).

**Update 2026-09-26 (context only; decision unchanged):** the official PS text
(R0) is now in hand and confirms Module B = 0h + 24h → 168h; no official
dataset exists. Validation item 1 below is satisfied. A layer-by-layer
re-evaluation after the prior-art pass proposed merging L2-drift with L3 and
dropping a fused risk score — confirmed as Revision 1 below — see
[system-architecture.md](../architecture/system-architecture.md) §7 (pending team confirmation).

## Problem

Choose an architecture that (a) satisfies the PS literally, (b) can be
defended technically in front of expert judges, (c) can be built and validated
incrementally within a hackathon timeline, and (d) avoids unsupported claims.

## Candidate approaches

| | Approach | Summary |
|---|---|---|
| A | Direct PS (R3 "Approach A") | Anomaly detector (z-score / Isolation Forest) + 168h regressor (XGBoost/LSTM); binary output |
| B | Layered reliability screening (R3 "Approach B", R2 "AstraGuard" without overclaims) | Quality gate → spec → lot-relative (level + drift) → trajectory → 168h prediction → interval → rules → PASS/REVIEW/REJECT → explanation |
| C | Deep sequence / autoencoder | LSTM/Transformer/AE over the 4-point sequence |
| D | Physics-informed per-component curve fit | Fit y₀ + A·tⁿ per component, classify by n |

## Selected provisional approach

**B, built incrementally with A's simple components as its first baselines.**
Each layer is kept only if the ablation shows value.

## Reasons

- B maps every layer to a PS requirement (traceability table), A leaves
  uncertainty and review unaddressed.
- B's layers are transparent statistics → explanations are the actual evidence (PSR-06).
- REVIEW state directly addresses asymmetric FN cost (PSR-05).
- C is poorly matched to ≤ 4 points (M-01) and weak on explainability.
- D is not identifiable at T24 (2 points, 3 parameters) and has no residual
  degrees of freedom at T96 (M-02).

## Alternatives retained as conditional experiments

- Isolation Forest comparator (E2b); GBM / hierarchical degradation model
  (E4b); conformalised quantile regression (E5); population-level shape model;
  GMM lot-modality check.

## Consequences

- Positive: incremental delivery; each step produces evidence; simple
  dependencies; easy to explain.
- Negative: may look less "advanced" than deep-learning solutions — mitigated
  by evidence and by the sparse-data argument.
- Negative: more layers → more thresholds → risk of overfitting to synthetic
  data; mitigated by lot-grouped splits, frozen test lots, held-out scenarios.
- Two checkpoints (T24, T96) double the evaluation effort.

## Validation still required

1. ~~Official PS text confirms Module A/B definitions and inputs (C-01).~~ Done 2026-09-26 (R0).
2. E1–E6 on synthetic data; R-01/R-02 robustness.
3. E4 on external NASA data (prediction only).
4. Any official data: all experiments repeated.
5. Prior-art searches before any originality statement (partly done 2026-09-26: [literature-review.md](../research/prior-art/literature-review.md)).

This ADR moves to **Accepted** only after E6 has been run and each retained
layer is justified by recorded evidence.

## Revision 1 — 2026-09-26 (confirmed by user, Decision 3)

Basis: layer re-evaluation in [system-architecture.md](../architecture/system-architecture.md) §7.

| Change | Reason |
|---|---|
| **L3 retired; drift / trajectory features merged into L2** ("lot-relative analysis of level and drift"). Layer IDs L0, L1, L2, L4–L7 are kept unchanged so experiment and requirement references stay stable. | At T24 there is one increment (0h→24h); a separate trajectory layer computed the same quantity L2-drift scores. Slope change at T96 stays available inside L2 for the optional T96 extension |
| **No fused risk score.** L6 is an ordered, documented rule set ("decision rules"); a weighted score may be used only as a ranking aid, never as a decision input or probability | A fused score adds an unexplainable number; ordered rules are directly explainable (OPS-07) |
| **L5 (prediction interval) is conditional** — kept only if E5 shows near-target per-lot coverage and a useful change in decisions | Not a PS requirement; lot structure threatens coverage (S-11) |
| **Binary output always emitted** alongside PASS/REVIEW/REJECT (FR-16) | Hidden scoring likely needs a flag (anomaly-detection-score.md §5) |

Resulting pipeline (7 layers):
Data-quality gate (L0) → Datasheet limit (L1) → Lot-relative level + drift (L2)
→ 168h prediction (L4) → [conditional] Prediction interval (L5) → Decision rules
incl. safety-slope rule (L6) → Explanation + audit (L7).

Status of this ADR stays **Proposed** until E6 evidence exists.
