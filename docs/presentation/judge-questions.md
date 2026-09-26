# Anticipated Judge Questions

Status: Draft · Last updated: 2026-09-26

Answer outlines. Items marked **[needs evidence]** cannot be answered with
numbers until the experiment is recorded.

| # | Question | Answer outline | Backing |
|---|---|---|---|
| Q1 | Why not an LSTM / Transformer for a time-series problem? | ≤ 4 points per component: nothing for recurrence/attention to exploit, many parameters vs few observations, weak explainability. Our features capture level, drift and drift change directly. We would reconsider with dense data and a measured baseline gap. | M-01; E3/E4 **[needs evidence]** |
| Q2 | Is this novel? | Individual methods are established (burn-in ML, DPAT lot limits, ESCC drift limits, a patent on pre/post burn-in outliers, conformal, reject option). We propose a PS-specific integration — predicting end-of-burn-in drift at 24h with a lot-aware interval and a review path — and show, by ablation, what each part contributes. | novelty-boundaries.md, prior-art-matrix.md |
| Q3 | What data did you use? | Official data if provided; otherwise synthetic PS-shaped data (clearly labelled) plus NASA external data for prediction realism. Never presented as ISRO hardware data. | dataset-strategy.md |
| Q4 | Isn't synthetic evaluation circular? | Generator designed before detector tuning, held-out scenario family, parameter sweeps. Real validation still required — stated as a limitation. | Dataset strategy §3; R-01/R-02 **[needs evidence]** |
| Q5 | What does your 95% interval mean? | A prediction interval targeting 95% marginal coverage of the true 168h value across components, measured X% on held-out lots. Not a probability of failure. | glossary; E5 **[needs evidence]** |
| Q6 | Can you guarantee zero false negatives? | No. We report escape rate with its uncertainty and number of positives, at a stated review rate. REVIEW and fail-safe rules bias toward catching. | E6 **[needs evidence]** |
| Q7 | How many components go to REVIEW? | Review rate at the chosen operating point, plus the full recall–review curve. | E6 **[needs evidence]** |
| Q8 | What if a lot is bimodal or mostly defective? | Data-quality gate flags suspected multi-modality and low dispersion; whole lot → REVIEW. Robust statistics tolerate a minority of defects, not a majority — stated limitation. | data-pipeline.md; E2 sensitivity **[needs evidence]** |
| Q9 | How do you prevent data leakage? | Lot-grouped splits, frozen test lots, checkpoint feature availability matrix, automated tests. | evaluation-protocol.md |
| Q10 | Why MAD and not the AEC-Q001 method? | AEC-Q001 Rev-D uses median ± 6·IQR/1.35 (verified, S-01); we use that as the baseline and compare MAD. We call it DPAT-style, not compliant. | ml-pipeline.md L2; S-01 |
| Q11 | Why predict 168h from only 24h? | Official PS requirement (R0: "takes Value_0h and Value_24h as inputs"). A 96h checkpoint may be studied as a separately reported extension, never as Module B. | R0; E4 **[needs evidence]** |
| Q16 | How is your safety slope calculated? | The PS does not define it, so this is our documented choice (ADR-002): drift rate = (predicted 168h − 0h)/168 h; safety slope = per-parameter drift allowance ÷ 168 h, in the style of ESCC space-component drift limits, plus a datasheet-limit backstop; sensitivity to the allowance reported. | ADR-002 (accepted); E4 **[needs evidence]** |
| Q12 | Is this physics-informed? | Not claimed. Features are degradation-shaped (drift, drift change); per-component physical curve fitting is not identifiable from 2–3 points. | M-02 |
| Q13 | How fast / scalable is it? | Only measured numbers: latency per lot on stated hardware. | NFR-07/08 **[needs evidence]** |
| Q14 | How would ISRO deploy it? | Proposed: offline batch per lot at each checkpoint, audit log, engineer override. Not deployed. | requirements; P7 |
| Q15 | What happens if a measurement is missing? | Fail-safe REVIEW, never PASS; explanation states the reason. | NFR-01, R0 |
