# Novelty Boundaries

Status: Draft · Last updated: 2026-09-26

What we may and may not say about originality. Evidence: [prior-art-matrix.md](prior-art-matrix.md).

## 1. Not novel (do not claim) `[NC]`

- AI / ML for burn-in decisions (S-04 C&IE 2025; S-09 Sci. Rep. 2022).
- Lot-level / lot-specific analysis for burn-in (S-05 ESREL 2023) and
  lot-relative outlier limits (S-01 AEC-Q001 Dynamic PAT).
- **Screening on burn-in drift from the 0h value** (S-02/S-03 ESCC drift values).
- **Flagging devices as outliers from their pre- vs post-burn-in change** (S-06, US 8,010,310).
- Robust (median/MAD, median/IQR) outlier detection.
- Degradation forecasting, prognostics, random-effects degradation models (S-15).
- Uncertainty quantification, conformal prediction (S-10–S-12).
- Reject option / three-way decisions (S-13, S-14).
- LSTM / Transformer / autoencoder use.
- "First AI system for burn-in", "first latent-defect detector", "patent-pending",
  "AEC-Q001 compliant", "ESCC compliant", "physics-informed digital twin".

## 2. Differentiation we may state (as proposal)

> "A proposed, PS-specific screening framework that predicts the 168h value from
> the 0h and 24h checkpoints, compares the predicted drift with a drift allowance
> (in the style of space-component drift limits) and with the component's lot,
> attaches a lot-aware prediction interval, and routes uncertain cases to
> engineer review with quantitative evidence."

Allowed words: *proposed framework*, *proposed integration*, *PS-specific
implementation*, *engineering differentiation*, *informed by DPAT-style
lot-relative screening and ESCC-style drift limits*.

## 3. Differentiation we may state only after evidence

| Statement | Needs |
|---|---|
| "Predicting at 24h recovers most of the end-of-burn-in drift rejections" | E4 safety-slope confusion matrix vs measured-168h rule, held-out lots |
| "Lot-relative drift scoring catches cases a fixed drift allowance misses" (or vice versa) | E3/E4 per scenario |
| "Uncertainty-aware REVIEW reduces escapes at a bounded review rate" | E5/E6 recall vs review-rate curve |

## 4. Unknown

Whether the exact combination in §2 is published or patented. Search so far
(literature-review §4) did not find it; that is **not** evidence of novelty.
Until a fuller IEEE/Scholar/patent search is done, say nothing about originality.
