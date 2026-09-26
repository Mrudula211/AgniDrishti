# The Problem in Simple Language

Status: Draft · Last updated: 2026-09-26

For teammates new to reliability engineering. Precise sources are linked at the end.

## 1. What is burn-in?

Satellites cannot be repaired. So every electronic part going into a payload is
"stress-tested" first: it is run hot (the PS gives **125 °C as an example**) for
days. Weak parts tend to show themselves early under stress. During this test,
an electrical property of each part is measured a few times — the PS gives
**0h, 24h, 96h and 168h** as example times (168h = 7 days).

Examples of the measured property (from the PS): standby current (**Iddq**),
**leakage current**, **propagation delay**.

## 2. What does the factory do today?

Each part has a datasheet limit, e.g. "leakage must be below 50 µA". If a
measurement is above the limit → reject. Otherwise → pass. This is
**static pass/fail**.

## 3. Why is that not enough?

The PS's own example (illustrative numbers from the PS):

```
  Datasheet limit ............................ 50 µA
  Average part in this lot ................... 10 µA
  Our suspicious part ........................ 45 µA   ← passes the limit!
```

45 µA is legal, but it is 4.5× its siblings. Something is probably wrong with
it. A part like this — inside the limit but behaving strangely, often slowly
drifting — is a **latent defect**. It can pass screening and fail in orbit.

## 4. What is a lot?

A **lot** is a batch of parts made together (same wafer run, same process). Parts
in one lot should look alike. Lots differ from each other, so "normal" is
different for each lot.

## 5. What does the PS ask for?

| Part | Plain meaning |
|---|---|
| **Module A** — "Dynamic" outlier detection | Compare each part with **its own lot**, not only with the fixed limit |
| **Module B** — drift predictor | Using only the **0h and 24h** measurements, **predict the 168h value**. If the predicted drift is too fast ("exceeds a calculated safety slope"), flag the part for early rejection |
| Evaluation | (1) an Anomaly Detection Score where **missing a bad part is catastrophic**; (2) prediction error (**MAE**) on the 168h value against hidden answers; (3) can a QA inspector understand **why** a part was flagged |

## 6. Why 0h + 24h → 168h?

If we can tell on day 1 what will happen on day 7, engineers can act early.
But predicting 7 days out from 2 points is hard — so the prediction must come
with an honest statement of how uncertain it is.

## 7. What makes this hard?

- Only 2 measurements are available at decision time.
- Bad parts are rare, and missing one is very costly.
- There is **no official data** — the evaluators keep the real data hidden.
- The PS does not say how the "safety slope", the "drift rate" or the
  "Anomaly Detection Score" are calculated.

Sources: [official PS text](../research/ps-analysis/official-ps-26170.md) ·
[what we know and don't](what-we-know-and-dont-know.md).
