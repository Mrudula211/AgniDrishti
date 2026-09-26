# Decision Flow: PASS / REVIEW / REJECT

Status: Draft · Last updated: 2026-09-26

**Proposal.** The PS asks for anomaly flags, an early-rejection flag and a
justified classification; it does **not** require three outcomes. Thresholds
are not chosen yet. Technical rules: [decision-engine.md](../architecture/decision-engine.md).

## 1. The three outcomes

| Outcome | Meaning | Who acts |
|---|---|---|
| **PASS** | Enough evidence the part is fine | Continues normally |
| **REVIEW** | Suspicious or uncertain, or data is missing/broken | A QA engineer decides |
| **REJECT** | Strong evidence of a problem | Removed / flagged for rejection |

## 2. Why REVIEW exists

Missing a bad part is "catastrophic" (PS). With only 2 measurements the
prediction can be wrong. Forcing a yes/no on uncertain parts either lets bad
parts escape or rejects good ones. REVIEW sends doubt to a person. Its cost is
engineer time, so the **review rate is measured and reported**.

If the evaluators need a yes/no, REVIEW is counted as "flagged" (the safer
choice) — a documented setting.

## 3. Flow (rules checked in order; all matching rules are recorded)

```
Data missing or broken? ───────────────────────── yes → REVIEW
        │ no
Outside datasheet limit now? ──────────────────── yes → REJECT
        │ no
Predicted drift beyond allowance,
  even at the optimistic end of the range? ────── yes → REJECT
        │ no
Predicted drift beyond allowance at the point
  estimate or pessimistic end of the range? ───── yes → REVIEW
        │ no
Far from its lot (level or drift)? ────────────── yes → REVIEW
        │ no
                                                      PASS
```

## 4. Key terms without jargon

| Term | Plain meaning | Common mistake |
|---|---|---|
| **Drift** | How much the value changed since 0h, per hour | Using raw change without dividing by time |
| **Safety slope** | The fastest acceptable drift. The PS says it is "calculated" but not how. **Our choice** ([ADR-002](../decisions/ADR-002-safety-slope-and-drift-rate.md)): a per-parameter drift allowance ÷ 168 h, like the drift limits in European space-component specs, plus "predicted 168h value over the datasheet limit" | Saying the PS defines it |
| **Robust z** | "How many normal-spreads away from the lot's middle value" | Calling it a probability |
| **Prediction interval** | A range that should contain the true 168h value for about, say, 90 % of parts overall | Saying "90 % chance this part fails" — **wrong** |
| **Anomaly score** | A number that ranks how unusual a part is | Treating it as a probability |

## 5. Why a prediction interval is not a failure probability

The interval is about **where the 168h value will be**, averaged over many
parts. It says nothing directly about one part failing in orbit, and "90 %"
holds across parts, not for each individual part. So we say "the upper end of
the range crosses the allowance", never "90 % likely to fail".
