# Idea-Round Submission Content (SIH 2026, PS 26170)

Status: Draft for team review · Last updated: 2026-09-29 (Rev. 7 — sixth audit: no “silent PASS” wording, baseline labelled “at 24 h”, Module B described as the model actually chosen (population increment beat regression), MAE marked validation lots, persistence defined, 8 of 14 REJECTs correct, one Δallow per site; earlier revisions in git history) · Deadline: **30 Sep 2026**

Source text for the portal fields and the 6-slide official template (S-17).
Rev. 2 (2026-09-26) carried no numbers because no experiment had run. The prototype
and the E1–E6 runs now exist, so Rev. 3 shows recorded results. **Every number on
a slide is listed in the provenance table below**; a number not in that table must
not appear on a slide (CLAUDE §5, §27). All results are on **synthetic** data and
every slide that shows one says so.

Deck: [sih2026-idea-agnidrishti.pptx](sih2026-idea-agnidrishti.pptx) ·
exported PDF: [sih2026-idea-agnidrishti.pdf](sih2026-idea-agnidrishti.pdf)
(6 slides; template headings and idea-detail pointers kept verbatim). Speaker
notes carry the talk track, but the portal takes the PDF only, so nothing a
judge needs lives only in the notes.

Before upload:
1. Replace "(to be assigned on the SIH portal)" on slide 1 with the Team ID once assigned.
2. The repository is public (checked 2026-09-29, HTTP 200); slides 4 and 6 link to
   `github.com/Mrudula211/AgniDrishti/tree/p1-synthetic-data`. Re-test it logged out before upload.
3. Export to PDF and re-check all six pages.

Story: **in spec is not the same as healthy — decide at hour 24, and never let
doubt become a PASS.**

---

## Portal fields

**Idea title**

AgniDrishti — catch the drifting in-spec part at hour 24 of burn-in

**Idea description**

Static pass/fail limits let latent defects escape: a part can sit inside its
datasheet limit while being abnormal for its lot or drifting toward failure.
AgniDrishti screens burn-in parametric data at the 24 h checkpoint. For each lot
it checks data quality, applies the datasheet limit, scores every part against
its own lot on level and 0→24 h drift with robust statistics (Module A),
forecasts Value_168h from Value_0h and Value_24h with a calibrated 90 % range
(Module B), and applies ordered rules including a safety-slope rule. It returns
PASS / REVIEW / REJECT with the numbers and the rule that fired; bad data, or a
range that could reach the limit, goes to an engineer instead of being passed.
A working prototype (web service, CLI, audit record with replay, 111 automated
tests) is built. On held-out synthetic test lots it flagged 24 of 30 drifting
rows at hour 24 (95 % CI 0.63–0.91) versus 4 of 30 for datasheet limits alone,
sending 10.4 % of rows to engineer review. These are synthetic results, not ISRO results; ISRO
performance will be measured on ISRO data. Code: github.com/Mrudula211/AgniDrishti/tree/p1-synthetic-data

---

## Slide content (Rev. 3)

1. **Title** — tagline "Catch the drifting in-spec part at hour 24, not 168."
2. **In spec is not the same as healthy** — one-paragraph explanation; hero chart
   of one real test-lot row (SYN-L026-C0010, Iddq) with its 137 lot peers, the
   30 µA limit, and the 96 h / 168 h values revealed after the decision;
   screenshot of the prototype's evidence card for the same row; Module A / B /
   decision lines; four "caught at 24 h" tiles (E1, E2, E3, E6); differentiator
   "Doubt is never a PASS".
3. **Technical approach** — headline "Every layer must beat a simpler baseline on
   unseen lots — or it is removed"; one-line stack + what is learned from lots;
   8-stage architecture, all marked built; rules R0–R6 with decisions;
   definitions of robust z, drift rate, safety slope; REVIEW + REJECT = flagged;
   E1–E6 test table; forecast MAE vs persistence; honest finding; why no LSTM.
4. **Feasibility** — 8-row risk table (incl. hidden ground truth, circular
   validation, measured escapes and false rejects); live-service screenshot;
   technical / operational / financial cards; built-and-verified box + code link.
5. **Impact** — "Decide at hour 24 — with evidence"; conventional vs AgniDrishti
   lane with measured decision shares; the engineer's 24 h moment; reliability /
   chamber-time / trust cards; gated roadmap.
6. **References** — unchanged selection, NASA data marked "planned, not yet run",
   ESCC 9202/045 explained; own-evidence band (code, tests, pre-registration,
   sealed held-out families).

Removed after the audits: the Isolation Forest / gradient-boosted-tree
comparators (never implemented — pyproject has no scikit-learn), "official-data-ready
pipeline" (replaced by the built column mapping), "organiser clarification" (the team
decided not to contact organisers), the conceptual mock-up and sketch, the label legend.

## Number provenance (every number on a slide)

Data category for all rows: **synthetic** (development v1, DS-04), unless stated.

| Number (slide) | Value | Source |
|---|---|---|
| Hero row (2) | 0 h 8.955, 24 h 12.34, 96 h 22.3, 168 h 32.0 µA; limit 30 µA; lot median 9.9 µA; 137 peers; drift 42.7 robust σ; forecast 12.45 µA, 90 % range 12.14–12.76; drift rate at the optimistic end 0.0190 vs slope 0.0080 µA/h (2.4×, the end R2 uses; point 0.0208 = 2.6×); REJECT, rules R2;R3;R5 | `artifacts/metrics/E1-E6_test/20260926-144448_c8ca99b/test_decisions.csv`, row SYN-L026-C0010 / iddq |
| Caught at 24 h (2, 5) | 4 / 4 / 20 / 24 of 30 | same run, recall 0.133 / 0.133 / 0.667 / 0.800 × 30 positives (summary.md) |
| E1–E6 table (3) | recall, precision, review rate, false rejection | same run, summary.md |
| Recall CI (2, 3) | 0.63–0.91 | Wilson 95 % interval for 24 / 30, computed 2026-09-29 |
| REJECT quality (4) | 6 of 14 REJECTs false (8 true) | `test_decisions.csv` vs primary label (label_safety_slope, Δallow 0.15), computed 2026-09-29 |
| Focus / enrichment (5) | 261 flagged rows (11.0 %) hold 24 of 30; 9.2 % vs 1.27 % base rate, ≈ 7× | same computation |
| Part-parameter definition (3, 5) | 2,368 part-parameters = 1,184 parts × 2 parameters, 10 lots | `test_decisions.csv` |
| Drift ratio (2) | 3.38 µA vs lot median drift 0.116 µA ≈ 29× | same row |
| tpd MAE (3) | 0.0472 vs 0.0496 ns (persistence), validation lots | ablation-plan §3 |
| Review share (2, 3, 5) | 10.4 %; PASS 89.0 %, REJECT 0.6 % | same run; reproduced by service run `20260929-035534_1f5d29a` (2107 / 247 / 14 of 2,368 rows) |
| Forecast MAE (3) | Iddq 0.297 vs 0.338 µA; tpd 0.047 vs 0.050 ns | validation lots, [ablation-plan.md](../research/experiments/ablation-plan.md) §3 |
| Coverage (3) | 0.887 on test (target 0.90) | test summary.md |
| Escapes / false rejects (4) | 6 of 30; all 6 false rejects | ablation-plan.md §5 F5, F6 |
| Scale (4) | 2,368 / 23,680 / 118,400 rows: 0.35 / 2.6 / 14.2 s (median of 3) | service runs 2026-09-29 `20260929-0420..`–`-0421..` on the frozen pipeline; test lots copied 10× / 50× with new lot IDs; one PC. Audit records in the local runs directory (not committed) |
| Replay (4) | identical decisions | `GET /api/runs/20260929-035534_1f5d29a/replay` → `identical: true` |
| Tests (4, 6) | 111 | `pytest` at commit `1f5d29a`, 111 passed (2026-09-29) |
| Thresholds (3) | z 2.5 / 6, Δallow 15 %, IQR/1.35, 90 % | `configs/experiments/pipeline_v1.yaml`, ADR-002, ADR-005 |
| Chamber time (5) | 144 of 168 h (86 %) | arithmetic from the PS timeline (168 − 24); labelled "not a measured saving" |
| Sealed families (4, 6) | 26 Sep 2026, SHA-256 1a7de276… | [synthetic-data-design.md](../research/datasets/synthetic-data-design.md) §7 |
| ESCC 9202/045 (6) | IDD ±75 nA; IOL ±15 % | literature-review.md S-03 |

The hero chart and screenshots were produced on 2026-09-29 from the runs above
(chart: matplotlib from `test_decisions.csv`, showing the 24 h forecast and its range
as the pipeline produced them; screenshots: the screening service on
`frozen_pipeline.json` of run `20260926-144425_c8ca99b`, cropped, with the replay check run). They are not stored in the
repository; regenerate them from those runs if the deck is rebuilt.

## Claim checks

- [x] Every slide number is in the provenance table; synthetic label on every result
- [x] No "first / novel / compliant / physics-informed / guaranteed / zero FN"; DPAT named as our baseline
- [x] Limits shown on the slides: recall target 0.95 not met, 6 escapes, glitch false rejects, forecast adds no detection
- [x] Prediction interval described as coverage, never as a failure probability
- [x] NASA data marked external, planned, not yet run
- [x] PDF exported via PowerPoint and all six pages inspected (no overlap or overflow)
- [ ] Team ID filled in (team action)
- [x] Repository public (HTTP 200, 2026-09-29); DOIs resolve via doi.org
