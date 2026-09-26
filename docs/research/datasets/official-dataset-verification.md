# Official Dataset Verification — PS 26170

Status: Accepted · Last updated: 2026-09-26

## Verdict

**OFFICIAL DATASET NOT FOUND**

Official PS 26170 dataset was not identified from authoritative sources.

## Evidence

| # | Check | Result |
|---|---|---|
| 1 | Official PS entry on `https://sih.gov.in/sih2026PS` (modal `#ViewProblemStatement26170`), field **Dataset Link** | **Empty.** Retrieved 2026-09-26 06:22 UTC; preserved in [../ps-analysis/official-ps-26170-sih-portal-extract.html](../ps-analysis/official-ps-26170-sih-portal-extract.html) |
| 2 | Do other PSs on the same official page carry dataset links? | Yes — 4 distinct dataset URLs appear across the page (e.g. mospi.gov.in, copernicus.eu, a Google Drive file). So the field is used for other PSs and is empty for 26170. |
| 3 | Official PS entry, YouTube and Contact fields | Empty — no attachment or contact channel for data |
| 4 | `https://www.sih.gov.in/dataset/` (referenced in commented-out HTML of the entry) | HTTP 403 ("Redirecting…"); no accessible content |
| 5 | Official PS text | Mentions "the actual **hidden** ground-truth values" for Module B evaluation → evaluators hold data that is **not published**. No download is referenced. |
| 6 | Web searches (2026-09-26): "SIH 26170 dataset", "SIH26170 dataset", "AI-Driven Anomaly Detection in Component Burn-In dataset Value_0h Value_24h Value_168h", "ISRO SIH 2026 burn-in screening official dataset hidden ground truth Value_168h" | Only third-party results: team GitHub repositories, PS aggregator sites (sihbuddy.in, Kaggle PS-list datasets), `sih.gov.in/dataset/Data_set.pdf` titled "SIH 2024 Data Set Link" (a different year). None is an official PS 26170 dataset. Several team repositories themselves state that no official dataset was provided and that they use synthetic data — corroborating only, not authoritative. |

## Authenticity questions (required fields)

| Question | Answer |
|---|---|
| Who published it? | No official dataset exists to attribute |
| Official source? | None — PS entry has an empty dataset field |
| Explicitly associated with PS 26170? | No dataset is |
| Linked from the official PS source? | No |
| Official dataset description? | None |
| License / access condition? | Not applicable |
| Files provided? | None |
| Variables? | Official text names only `Value_0h`, `Value_24h`, `Value_168h` and example parameters (Iddq, leakage currents, propagation delays) |
| Temporal measurements? | Official text: "intervals like 0h, 24h, 96h, and 168h" |
| Labels? | Not specified; "defective part" and "hidden ground-truth values" referenced in evaluation |
| Matches PS requirements? | Not applicable |

## Actions taken

- Nothing was downloaded into `data/raw/`.
- No `data/raw/README.md` or `official-dataset.md` was created, because they
  are defined for a verified official dataset only.

## Re-check triggers

Re-run this verification if: the PS entry's Dataset Link changes; organisers
publish data for later rounds; an official communication references data.
Recommended: re-fetch the official page after the 30 September 2026 deadline and
before each later round.
