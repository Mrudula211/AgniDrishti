# Presentation Story

Status: Draft · Last updated: 2026-09-26

This is the narrative plan for the **finale** deck. **No slide may be built with numbers until the
corresponding experiment is recorded.** Every evidence beat below is TBD.
The idea-round PDF (6 slides, fixed template, due 30 Sep 2026) is planned in
[sih-presentation-research.md](sih-presentation-research.md) §4.

## Core message

> Static limits ask "is it out of spec now?". AgniDrishti (proposed) also asks
> "is it abnormal for its lot?", "is it moving abnormally?", "where will it be
> at 168h, and how sure are we?" — and sends doubt to an engineer instead of
> guessing.

## Narrative beats

| # | Beat | Content | Evidence needed | Status |
|---|---|---|---|---|
| 1 | Hidden failure problem | A component can pass its limit and still be abnormal | PS text (R0 10/45/50 µA example) | Ready (R0) |
| 2 | Why static screening misses it | Four cases table (problem-statement-analysis §4) | E1 on stated data | TBD — experiment not yet executed |
| 3 | Core insight | Compare against spec **and** peers **and** trajectory | — | — |
| 4 | Architecture | 7-layer pipeline (ADR-001 Rev. 1), marked "proposed" until E6 | ADR-001 | Proposed |
| 5 | Lot-relative intelligence | Robust z of level and drift | E2 | TBD — experiment not yet executed |
| 6 | Trajectory intelligence | Checkpoint slopes; why not LSTM on 4 points | E3; M-01 argument | TBD — experiment not yet executed |
| 7 | 168h prediction | 0h+24h → 168h; simple models first | E4 | TBD — experiment not yet executed |
| 8 | Uncertainty | Prediction interval, correct wording | E5 coverage | TBD — experiment not yet executed |
| 9 | PASS / REVIEW / REJECT | Rules; fail-safe; review budget | E6 curve | TBD — experiment not yet executed |
| 10 | Explainability | Evidence card + trajectory map from a real run | Generated output | TBD |
| 11 | Experimental evidence | Ablation table, data category on the slide | Ablation plan table | TBD — experiment not yet executed |
| 12 | End-to-end example | One component through all layers (demo-flow.md), labelled synthetic unless official | Recorded run | TBD |
| 13 | Deployment | Offline batch per lot, audit log — **proposed** | P7 | Proposed |
| 14 | Limitations | Data category, proxy labels, unverified PS details, no field validation | — | Ready to write |
| 15 | Future work | Official data, multi-parameter, cross-lot history, advanced models if justified | — | Ready to write |

## Tone rules

- "Proposed" / "on our synthetic evaluation data" wherever true.
- No competitor-bashing statistics (X-03, X-04 are speculation).
- No domain jargon used as decoration (DPAT, Arrhenius) unless it is actually used.
