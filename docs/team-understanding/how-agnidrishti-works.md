# How AgniDrishti Is Meant to Work (Proposed)

Status: Draft · Last updated: 2026-09-26

**Nothing here is built or tested yet.** Every step is a proposal that must earn
its place in experiments. Technical version: [system architecture](../architecture/system-architecture.md).

## 1. The idea in one picture

```
 Measurements of one lot at 24h (Value_0h, Value_24h for every part)
        │
  1. Is the data OK?              missing / broken → REVIEW (never PASS)
        │
  2. Inside datasheet limit?      outside → REJECT
        │
  3. Normal for its lot?          how far from lot's typical value and typical drift
        │
  4. Predict Value_168h           simple model first
        │
  5. How sure is the prediction?  a range ("prediction interval"), not one number
        │
  6. Apply written rules          → PASS / REVIEW / REJECT
        │
  7. Explain with numbers         which rule fired, and the values behind it
```

## 2. Each step in plain words

| Step | What it does | Why |
|---|---|---|
| 1 Data check | Catches missing values, duplicates, tiny lots, all-identical values | A broken input must not become a confident PASS |
| 2 Datasheet limit | Today's method | The baseline everything else must beat |
| 3 Lot comparison (Module A) | Measures distance from the lot's middle value, in units of the lot's normal spread ("robust z") | 45 µA in a 10 µA lot is abnormal even under 50 µA |
| 4 Prediction (Module B) | Estimates the 168h value from 0h and 24h | Required by the PS; scored by MAE |
| 5 Uncertainty | Gives a range the true 168h value is expected to fall in, for a target share of parts | With 2 points we might be wrong; better to know how wrong |
| 6 Rules | e.g. "predicted drift clearly too fast → REJECT; maybe too fast → REVIEW" | Doubt goes to a human instead of a coin flip |
| 7 Explanation | "Value_24h is X above the lot median (Y robust-z); predicted 168h is Z; range crosses the drift allowance → REVIEW (rule R3)" | The PS evaluates explainability |

## 3. What we deliberately do NOT use

- **No LSTM / Transformer / deep learning.** A part has 2–4 numbers; these
  models need long sequences and lots of data, and are hard to explain.
- **No per-part curve fitting** (e.g. y = y₀ + A·tⁿ): 3 unknowns cannot be
  found from 2 points.
- **No "probability of failure"** unless it is calibrated on real labels — we have none.

## 4. What already exists elsewhere (be honest in pitches)

Lot-relative limits (automotive DPAT), burn-in drift limits (European space
specs), and flagging parts by their burn-in change (a 2011 patent) all exist.
What we propose is the **combination for this PS**: predict at 24h, compare to
a drift allowance and the lot, show uncertainty, and send doubt to review.
Details: [novelty boundaries](../research/prior-art/novelty-boundaries.md).
