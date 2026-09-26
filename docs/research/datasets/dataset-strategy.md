# Dataset Strategy

Status: Accepted ([ADR-003](../../decisions/ADR-003-dataset-strategy.md), 2026-09-26) · Last updated: 2026-09-26

## 0. Verified status (2026-09-26)

**Official PS 26170 dataset was not identified from authoritative sources.**
Verdict: **OFFICIAL DATASET NOT FOUND** — see [official-dataset-verification.md](official-dataset-verification.md).

| | Category | Status | Details |
|---|---|---|---|
| **A** | Official PS dataset | **Not found.** Official PS entry's Dataset Link is empty; R0 says evaluation uses "hidden ground-truth values" held by the evaluators. | [official-dataset-verification.md](official-dataset-verification.md) |
| **B** | External validation datasets | IGBT (~240 MB) **downloaded, verified (SHA-256), extracted and inspected** — secondary use only (6 devices, runs of hours at ≈300 °C). MOSFET (~7.85 GB) **downloaded, verified, extracted and inspected** — primary external source for forecasting methodology (42 tests, 0.38–23.45 h each, no labels). Neither has lots or burn-in checkpoints → methodology checks only, **cannot** validate the PS solution | [external-datasets.md](external-datasets.md), [external-dataset-compatibility.md](external-dataset-compatibility.md) |
| **C** | Synthetic PS-shaped dataset | Not generated (phase rule). Now the **only** route to evaluate Module A and lot-relative behaviour before evaluator data is seen. Must follow R0: Module B inputs Value_0h + Value_24h, target Value_168h; parameters may include currents **and** propagation delays | §3 below |

Previous statement → new evidence → corrected conclusion:
"None located (R3 §8)" → official PS entry retrieved, Dataset Link empty →
confirmed from the authoritative source, not only from R3.

Implication `[EI]`: because official scoring uses hidden data (R0), our
synthetic results cannot predict the official score. They can only compare our
own variants under stated assumptions. Robustness to unseen distributions
(robustness experiments R-01, R-02) matters more.

## 1. Three categories — never mixed, never relabelled

| Category | What it is | Status | May be called |
|---|---|---|---|
| **1. Official SIH/PS data** | Data released by SIH / the PS owner for PS 26170 | **None — verified from R0** (Dataset Link empty). Check again when PS portal updates. | "Official PS data" |
| **2. External public data** | Third-party datasets (e.g. NASA PCoE MOSFET, IGBT) | IGBT and MOSFET downloaded, verified and inspected (2026-09-26) | "External public data (NASA …)". Never "SIH data", never "ISRO data" |
| **3. Synthetic PS-shaped data** | Data we generate to mimic the PS structure | **Not generated** (not allowed in current phase) | "Synthetic data". Never "real", "hardware", "field" |

Every table, plot, metric and slide must carry its category.

## 2. Role of each category

| Question | Official | External | Synthetic |
|---|---|---|---|
| Does the method work on the real PS problem? | Yes (only source that can answer) | No | No |
| Lot-relative detection (Module A) | Yes | **No** — no lot structure | Yes, controlled |
| 0h+24h → 168h prediction (Module B) | Yes | Partially — must be resampled to 4 checkpoints; different device physics | Yes, but circular risk |
| Realism of degradation shapes | Yes | Yes | Only as good as the generator |
| Known ground truth per scenario | Maybe | Run-to-failure endpoint | Yes |
| Stress-testing (small lots, contamination, MAD = 0, missing data) | Limited | Limited | **Yes — main use** |

## 3. Synthetic data design

Moved (2026-09-26) and expanded in [synthetic-data-design.md](synthetic-data-design.md)
(scenario families incl. held-out families, anti-circularity rules, review checklist).

## 4. External data usage plan

- Use NASA data to test **prediction** components (E4) on real degradation
  shapes: sample each run at times mapped to 0/24/96/168h-equivalent points
  (mapping method to be documented; it is an assumption).
- Do not use NASA data to evaluate lot-relative detection (no lots).
- Record licence/usage terms before use.
- Do **not** download automatically; download is a manual, logged step.

## 5. When official data arrives

1. Place untouched in `data/raw/official/` and record hash.
2. Build data dictionary from the actual file (do not assume schema).
3. Confirm/refute assumptions A-01 … A-14.
4. Re-run experiments on official data; official results take precedence.

## 6. Open issues

- Official data availability (U-02).
- ~~NASA licence terms~~ recorded 2026-09-26 in [external-datasets.md](external-datasets.md).
- Mapping of NASA time axes to PS checkpoints (assumption to be designed in P1).
- ~~Team acceptance of this strategy~~ accepted 2026-09-26 — [ADR-003](../../decisions/ADR-003-dataset-strategy.md).
