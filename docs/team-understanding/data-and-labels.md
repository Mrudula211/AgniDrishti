# Data and Labels

Status: Draft · Last updated: 2026-09-26

## 1. The four kinds of data — never mix, never relabel

| Kind | What it is | Do we have it? | May be called |
|---|---|---|---|
| **Official** | Data from SIH / ISRO for PS 26170 | **No.** The PS dataset link is empty; evaluators hold hidden answers | "Official PS data" |
| **External** | Public datasets from others (NASA MOSFET, NASA IGBT) | Yes, downloaded and checked | "External NASA data" — **never** ISRO/SIH data |
| **Synthetic** | Data we will generate to mimic the PS shape | Not yet (design under review) | "Synthetic data" — never "real" |
| **Illustrative** | Example numbers in docs (e.g. 10/45/50 µA) | — | "Illustrative" — never a result |

Every chart, table and slide must say which kind it uses.

## 2. What each kind can prove

| Question | Official | NASA | Synthetic |
|---|---|---|---|
| Works on the real PS? | Yes | No | No |
| Lot comparison (Module A)? | Yes | **No** (no lots) | Yes, under our assumptions |
| 0h+24h → 168h? | Yes | Only as an analogy (runs last hours, not 168h) | Yes, but risk of fooling ourselves |

## 3. Why NASA data is only a side check

NASA devices were aged in hours at ~260–300 °C, have no lots, no datasheet
screening, and no failure labels. Useful to test whether a prediction method
behaves sensibly on real degradation; useless for proving PS performance.
Details: [external-dataset-compatibility.md](../research/datasets/external-dataset-compatibility.md).

## 4. Labels — what is a "bad part"?

The PS does not define it. So we use **proxy labels**, always named:

| Label | Meaning |
|---|---|
| `label_spec_168h` | Actual 168h value is outside the datasheet limit |
| `label_safety_slope` | Actual 0→168h drift rate exceeds the safety slope (drift allowance ÷ 168 h) or the 168h value is beyond the limit ([ADR-002](../decisions/ADR-002-safety-slope-and-drift-rate.md)) |
| `scenario` | Synthetic only: which behaviour was generated |

A proxy is not a real field failure. We never claim otherwise.

## 5. The self-deception trap (circularity)

If we generate bad parts with rule X and then detect rule X, we will look
perfect and learn nothing. Protection: held-out behaviour families, parameter
sweeps, designing data before detectors. See
[synthetic-data-design.md](../research/datasets/synthetic-data-design.md).

## 6. Leakage — the other trap

At 24h we may use only Value_0h, Value_24h and same-time lot statistics. Never
Value_96h, Value_168h, labels, or anything computed from test lots. Train and
test sets are split **by lot**.
