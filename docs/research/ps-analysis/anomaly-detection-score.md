# Anomaly Detection Score — What Is Known

Status: Draft · Last updated: 2026-09-26 · Gap: GAP-03 ([drawbacks-and-risks.md](../drawbacks-and-risks.md))

## 1. Official definition

**None published.** The complete official text (R0) is:

> "Anomaly Detection Score: a False Negative (missing a defective part) is
> catastrophic, penalizing teams that let bad parts escape."

## 2. Observed description (what the sentence does and does not say)

| Says `[SF]` R0 | Does not say `[GAP]` |
|---|---|
| A score exists and is used for evaluation | Formula, weighting, range |
| False negatives are penalised ("catastrophic") | How strongly; whether FP is penalised at all |
| Unit = "defective part" | How "defective" is labelled in the hidden data (GAP-05) |
| — | Whether the score is on Module A outputs, Module B early-rejection flags, or both |
| — | Whether outputs must be binary; how a third state (REVIEW) would be scored |
| — | At which checkpoint the score is computed |

## 3. Where we looked (2026-09-26)

| Place | Result |
|---|---|
| Official PS entry (R0) incl. YouTube / Dataset / Contact fields | Only the sentence above; other fields empty |
| SIH 2026 Guidelines PDF (S-16) | General idea-selection criteria only; no PS-specific scoring |
| SIH 2026 idea template (S-17) | No scoring information |
| sih.gov.in FAQ page | No PS-specific scoring |
| Web search | No official clarification found |

Not established by the available research. The only official channel found is
the SIH support address (sih@aicte-india.org); the PS contact field is empty.

## 4. Our internal evaluation metrics (not the official score)

Because the formula is unknown, we report the full set in
[evaluation-protocol.md](../experiments/evaluation-protocol.md): recall, FNR,
precision, FPR, F1, PR-AUC, defect escape rate, review rate. `[PR]` A
recall-weighted summary (e.g. F-beta with beta > 1) may be reported as **our**
proxy, always labelled "internal proxy — not the official Anomaly Detection Score".

## 5. Consequences for design `[EI]`

- Any submission to a hidden evaluation will likely need a **binary** flag per
  component. REVIEW must map to a binary value; given "FN is catastrophic",
  the conservative mapping is REVIEW → flagged. This must be a documented
  config option, and both mappings reported internally.
- Operating points are chosen for low FNR; the cost in FPR/review load is
  reported, not hidden.

## 6. Unknowns / actions

1. ~~Ask organisers~~ — not pursued (team decision 2026-09-26, ADR-003 amendment); our internal metrics and binary mapping stand in.
2. Re-check the PS entry after 30 Sep 2026 and before later rounds.
