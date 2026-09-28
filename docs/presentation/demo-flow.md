# Demo Flow (planned)

Status: Draft · Last updated: 2026-09-26

The demo walks one component through every layer. **Built 2026-09-26:** `scripts/build_demo.py` over the recorded final test run; featured rows follow the rule below plus a contrast row and one missed defect.
All values shown in the demo must come from a recorded pipeline run. The
screen must show the data category at all times.

## Flow

| Step | What the viewer sees | Layer | Source |
|---|---|---|---|
| 1 | Load one lot (file name contains `synthetic` unless official) | Ingestion | Recorded dataset |
| 2 | Data-quality summary; any blocked components already in REVIEW | L0 | Run output |
| 3 | Static screening result: the featured component PASSES the limit | L1 | Run output |
| 4 | Lot view: the component's position vs lot median (robust z) | L2 | Run output |
| 5 | Trajectory: 0h→24h drift vs lot drift | L2 (drift) | Run output |
| 6 | Predicted 168h value | L4 | Run output |
| 7 | Prediction interval; its upper end vs limit / safety slope | L5 | Run output |
| 8 | Decision: REVIEW (or whatever the run produced) with fired rule | L6 | Run output |
| 9 | Evidence card + trajectory map | L7 | Run output |
| 10 | Contrast: a high-but-stable component consistent with a high lot → PASS | L2–L6 | Run output |

Step 10 matters: it shows the system does not simply flag every high value.

## Selecting the featured component

Chosen from the **test** lots after the final run, by a documented rule (e.g.
"a positive that static screening passes and the full system catches"). If no
such component exists in the results, the demo says so — the case is not
constructed by hand.

## R2's "C-42" example

R2 describes C-42 at 35 µA, lot average 8 µA, limit 50 µA, "95% probability of
breaching", "early REJECT saving 72h". These numbers are illustrative and the
"95% probability" wording is incorrect (N-04). Do not reuse them.
