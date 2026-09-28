# Synthetic Data Design

Status: Accepted (design approved by user 2026-09-26, Decision 5; held-out families sealed and sweep grids pre-registered 2026-09-26) · Last updated: 2026-09-26

Supersedes dataset-strategy.md §3 (moved here). Category: **Synthetic** — never
"real", "hardware", "ISRO" or "SIH" data.

## 1. Purpose and limits

| Can answer | Cannot answer |
|---|---|
| Does a method behave as intended under controlled, stated conditions? | How it performs on ISRO components or the hidden evaluation |
| Where does it break (small lots, MAD = 0, bad lots, glitches)? | Real defect prevalence, real drift shapes |
| Do layers add value **relative to each other** under the same assumptions? | Absolute performance |

## 2. Structure (constrained by R0)

- Lots of components; each component has one or more parameters.
- Checkpoints 0h, 24h, 96h, 168h (R0 examples); 96h is generated but is not a
  Module B input.
- A datasheet limit per parameter (one- or two-sided, configurable).
- Parameter families mimicking the R0 examples: a current-like parameter
  (positive, right-skewed, rises with degradation) and a delay-like parameter
  (can shift either way). Units are "arbitrary units" unless an assumption is
  written down; the R0 10 / 45 / 50 µA example is an illustration, not a
  distribution to copy.

## 3. Scenario families

Each component gets exactly one `scenario` tag. Families marked **H** are
held out: never used while designing or tuning any detector; used only in R-01.

| # | Family | Mechanism (assumption) | Purpose |
|---|---|---|---|
| 1 | Healthy stable | Level from lot distribution; small noise | Baseline FPR |
| 2 | Healthy drift | Whole lot drifts slowly, component follows lot | Lot-relative must not flag |
| 3 | High-but-stable | High level consistent with a high lot, no drift | Must not flag (R3 §9) |
| 4 | Lot shift | Lot mean offset vs other lots | Cross-lot robustness |
| 5 | Lot contamination | 10–40 % (swept) degrading parts in one lot | Masking of robust stats |
| 6 | Bimodal lot | Two sub-populations (e.g. wafers) | False flags |
| 7 | Small lot | n swept down to very small | Scale instability |
| 8 | MAD ≈ 0 | Quantised measurements | Degenerate scale |
| 9 | Measurement noise | Noise level swept | Separability |
| 10 | Glitch | Single-checkpoint spike, trajectory otherwise normal | Must not reject on one point |
| 11 | Missing checkpoint | Value absent | Must → REVIEW |
| 12 | Gradual degradation | Monotone drift, several shapes | Core latent defect |
| 13 | Accelerating degradation | Slow early, fast late | Hard at T24 by design |
| 14 | Non-power-law degradation | e.g. logistic / saturating / step-then-linear | Shape not assumed by any detector |
| 15 | Sudden change | Jump between 96h and 168h | Undetectable at T24 — report, don't hide |
| 16 | Wrong-direction drift | Parameter degrades opposite to configured direction | Direction handling |
| 17 | Parameter-specific behaviour | Different shapes for current-like vs delay-like | Multi-parameter |
| 18 | Heteroscedastic noise | Noise ∝ level | Interval adaptivity |
| 19 **H** | Unseen family A | Defined and sealed by a person not tuning detectors | Anti-circularity |
| 20 **H** | Unseen family B | As above, different mechanism | Anti-circularity |

## 4. Anti-circularity rules (from C-11, CLAUDE §5/§6)

1. No detector or safety-slope rule may be written from the generator's
   equations. Example of what is forbidden: generate defects as t^1.5 and
   detect "exponent > 1".
2. Degradation shapes include families no method was designed around (14, 19, 20).
3. Families 19–20 are specified in a sealed config (hash recorded in the
   experiment log) before any detector code exists, and opened only for R-01.
4. Every result is reported over a **parameter sweep** (noise, prevalence,
   onset time, lot offset, lot size, contamination), not at one setting.
5. Prevalence is a parameter, never a claim about real defect rates.
6. Labels are computed by explicit rules on the generated values and stored
   separately (`label_spec_168h`, `label_safety_slope`, `scenario`);
   they are never features.
7. Seeds, config and commit recorded; filenames contain `synthetic`.

## 5. Open design questions (for the review)

| # | Question | Options |
|---|---|---|
| Q1 | Who defines held-out families 19–20? | **Decided and done:** written outside the repository by the team, not by Claude; only the SHA-256 commitment is in the repo (§7) |
| Q2 | Level distributions | Log-normal for current-like; normal for delay-like (assumptions) |
| Q3 | Drift allowance Δ used to label | ADR-002 accepted: Δ_allow swept over a pre-registered grid |
| Q4 | Lot sizes / number of lots | Swept; minimum set by split needs (train/val/cal/test lots) |
| Q5 | Should NASA-derived shapes inform any family? | Only qualitatively, documented, not fitted |

## 6. Review checklist

- [x] Design approved — by the user, 2026-09-26 (Decision 5)
- [x] Families 1–18 have a written mechanism and stated assumptions (§3); detailed distributions are written into the generator config in P1
- [x] Held-out families 19–20 written and sealed outside the repository (§7) — 2026-09-26
- [x] Sweep grids fixed before any generator or detector code exists (§8) — 2026-09-26
- [x] Label rules fixed and linked to ADR-002 (`label_spec_168h`, `label_safety_slope`)

## 7. Sealing procedure for held-out families 19–20

1. The owner writes both families (mechanism, parameters, prevalence) in a config
   file kept **outside the repository** and not shared with anyone writing detectors (including Claude).
2. The owner records the file's SHA-256 and the date in the table below.
3. The file is handed over only when R-01 runs; its hash is checked first, and the
   run log records the match.
4. If the families are ever seen by a detector author before R-01, record that here;
   R-01 then no longer counts as a held-out test.

| Owner | Date sealed | SHA-256 | Opened for R-01 |
|---|---|---|---|
| Team (kept outside the repository; not Claude) | 2026-09-26 | `1a7de27638222f0dad35c492080577e6abedfc23b2466f66227ee6cff6482f74` | No |

Integrity rules for everyone working in this repository (including Claude): do not
access, search for, infer or recreate the held-out specification; do not create
families 19 or 20; development family names never use the numbers 19 or 20.

## 8. Pre-registered sweep grids (fixed 2026-09-26, before any generator code)

These grids are fixed **before** the generator exists and before any detector
result is seen. They may be extended later only with a dated note; values are
never removed after results are known.

### 8.1 Drift allowance Δ_allow (ADR-002 sensitivity; used to compute `label_safety_slope`)

| Kind | Grid | Basis |
|---|---|---|
| Relative (fraction of \|V₀\|) | 0.02, 0.05, 0.10, 0.15, 0.20, 0.30 | Brackets the ±15 % relative drift values used in ESCC detail specifications (S-03) |
| Absolute, current-like parameter (µA, assumed unit) | 0.25, 0.5, 1, 2, 4 | Geometric grid; assumption |
| Absolute, delay-like parameter (ns, assumed unit) | 0.025, 0.05, 0.1, 0.2, 0.4 | Geometric grid; assumption |

### 8.2 Generator sweeps (robustness experiment R-02; one factor at a time from the base config)

| Factor | Grid (multiplier or value) |
|---|---|
| Measurement-noise multiplier | 0.5, 1, 2, 4 |
| Anomaly-prevalence multiplier (non-contaminated lots) | 0.5, 1, 2 |
| Contaminated-lot anomaly fraction | 0.10, 0.20, 0.30, 0.40 |
| Components per lot | 6, 12, 25, 50, 100 |
| Lot-to-lot offset SD multiplier | 0.5, 1, 2 |
| Late-drift onset window (h) | 30–60, 60–100, 100–140 |
| Seeds per setting | base seed, base + 1, base + 2 |

The base configuration is `configs/synthetic/development_v1.yaml`.

## 9. Implementation v1 (generator 1.1.0, 2026-09-26)

Category: **SYNTHETIC methodology-validation data** — not official SIH/ISRO data, and it
does not reproduce the hidden SIH evaluation. Families, anomaly labels, severity,
safety-slope settings and splits below are **our experimental definitions**.

Code: `src/agnidrish/synthetic/` (config, families, generator), `src/agnidrish/audit.py`
(E0), `src/agnidrish/labels.py` (ADR-002/004 labels). Config:
`configs/synthetic/development_v1.yaml`. Command:
`python scripts/generate_synthetic.py` (package installed or `PYTHONPATH=src`).
Dataset record (hashes, commit): [data-sources.md](data-sources.md) DS-04.

### 9.1 Contract decisions (where the task brief and repository rules differed)

| Brief asked for | Implemented | Reason |
|---|---|---|
| `src/data_generation/`, `src/data_validation/`, `tests/data_*` | `src/agnidrish/synthetic/`, `src/agnidrish/audit.py`, `tests/unit/` | CLAUDE §17–§18, §24 |
| `Value_0h`, `parameter_id`, lower/upper limit | `value_0h`, `parameter`, `spec_min`/`spec_max` | Canonical schema (CLAUDE §17, FR-01) |
| 0 h, 24 h, 168 h | + 96 h | §2 of this design; 96 h is never a Module B input |
| train / validation / test | train / validation / calibration / test | evaluation-protocol §2 |
| `docs/synthetic-data-generation.md` | this section | No duplicate documents (CLAUDE §22) |
| raw / interim / processed / manifests folders | `data/synthetic/development/` (CSV + manifest) | Only what is used; no processing step exists yet |
| Family numbers | Family **names** only | Numbers 19–20 belong to the sealed held-out families |

### 9.2 Generative model (component *c*, lot *l*, parameter *p*; t in hours, t_end = 168)

- Lot mean: m_l = N_p · (f_s + o_l), o_l ~ N(0, σ_lot) truncated at ±3 SD; f_s = `high_mean_factor` in `high_mean` lots, else 1.
- Baseline: b_c = m_l + e_c, e_c ~ N(0, σ_comp·N_p) truncated at ±3.5 SD; bimodal lots add ±½·`bimodal_separation_sd`·σ_comp·N_p by wafer.
- Healthy drift: g_l·H(t) + δ_c·s_f·H_f(t) — lot-common g_l ~ N(μ_drift·m_s·N_p, σ_ldrift·N_p) (m_s = `lot_drift_multiplier`), component δ_c ~ N(0, σ_cdrift·N_p) truncated at ±4 SD; H(t) saturating exponential (τ = `healthy_shape_tau_h`); s_f and H_f set by the family.
- True value: x(t) = b_c + L + healthy drift + A·f(t) — L is the family's constant level offset, A·f(t) its extra drift (f(0) = 0, f(t_end) = 1).
- Measured value: y(t) = x(t) + ε(t), ε ~ N(0, σ_meas·k_f); σ_meas = `meas_sd_frac`·|x(t)| (proportional, current-like) or ·N_p (additive, delay-like); k_f = family noise multiplier. Quantised lots round y to `quantisation_step`.

### 9.3 Development families

| Family | Kind | Deviation from healthy behaviour |
|---|---|---|
| healthy_stable | healthy | Component drift scaled by 0.3 |
| healthy_random_drift | healthy | Component drift with a linear instead of saturating shape |
| healthy_decelerating | healthy | Default saturating burn-in drift |
| healthy_component_offset | healthy | Level offset ±(1.5–2.5)·σ_comp (tail of normal variation) |
| healthy_noisy | healthy | Measurement noise ×4 |
| degradation_linear | drift | A·t/t_end |
| degradation_accelerating | drift | A·(t/t_end)^p, p ∈ [1.3, 1.8] |
| degradation_decelerating | drift | A·(t/t_end)^p, p ∈ [0.35, 0.7] |
| degradation_noisy | drift | Linear, noise ×4 |
| drift_early | drift | Saturating, τ ∈ [6, 15] h (most change before 24 h) |
| drift_late | drift | Zero until onset ∈ [30, 120] h, then linear (invisible at 24 h by design) |
| degradation_sigmoid | drift | Logistic, centre ∈ [40, 130] h, width ∈ [8, 25] h |
| degradation_saturating | drift | Saturating, τ ∈ [30, 80] h |
| shift_sudden | drift | Step at t ∈ [100, 160] h (visible only at 168 h) |
| degradation_wrong_direction | drift | Linear, opposite to the configured degradation direction |
| level_outlier | level | Stable offset (4–20)·σ_comp from its lot, within spec (the PS "45 µA in a 10 µA lot" case) |
| approaching_spec | spec | Linear drift covering 85–97 % of the distance to the limit by 168 h |
| crossing_spec | spec | Linear drift covering 105–150 % of the distance to the limit |
| spec_violation_at_0h | level | Baseline placed (1–5)·σ_comp beyond the limit at 0 h |

Anomaly status (`is_anomaly`) is **the family**, not a threshold on a value: anomalous
rows exist well inside spec, and healthy rows exist near the limit.

### 9.4 Severity (our definition)

Severity k is a deviation divided by a documented reference variation, never a single
absolute threshold:

- Drift families: k = |A| / σ_Δ, with σ_Δ = √((σ_cdrift·N_p)² + 2·(σ_meas·N_p)²) — the
  healthy within-lot SD of the 0 → 168 h change (lot-common drift excluded). k is drawn
  by band — mild [3, 6), moderate [6, 15), severe [15, 40] — with weights 0.4 / 0.4 / 0.2.
- Level families: k = |L| / (σ_comp·N_p).
- Spec families: k = |A| / σ_Δ after A is set from the distance to the limit (can be large).

Bands: `minimal` < 3 ≤ `mild` < 6 ≤ `moderate` < 15 ≤ `severe`; healthy rows have none.

### 9.5 Lot scenarios (54 lots)

| Scenario | Lots | Size | Anomaly fraction per parameter | Purpose |
|---|---|---|---|---|
| normal | 12 | 80–150 | 0 | FPR baseline |
| few_anomalies | 16 | 80–150 | 2–6 % | Typical screening |
| contaminated | 6 | 80–150 | 15–30 % | Masking of robust statistics |
| high_mean | 6 | 80–150 | 0–5 % (no level outliers) | Harmless offset; healthy parts near the limit |
| lot_drift | 4 | 80–150 | 0–5 % | Harmless lot-wide drift ×4 (the bad-lot tension, ADR-002) |
| bimodal | 4 | 80–150 | 0–5 % | Two wafers 3·σ_comp apart |
| small | 4 | 6–12 | 0–15 % | Scale instability |
| quantised | 2 | 80–150 | 0–5 % | MAD ≈ 0 |

### 9.6 Injected data faults (`data_fault`)

`missing_value` (0.5 % of rows; one checkpoint removed; any row), `glitch` (0.5 % of
healthy rows; ±8·σ_comp spike at 24 h only), `quantised` (all rows of quantised lots).
Faults are measurement problems, not defects: a glitched row stays healthy.

### 9.7 Splits

Whole lots go to train / validation / calibration / test (50 / 20 / 15 / 15 %),
stratified by lot scenario with largest-remainder rounding. Rounding ties go to test,
then validation, calibration, train, so scenarios with few lots still reach the frozen
test split. No component, lot or wafer appears in two splits (audit-enforced). The
split draw uses its own seed stream, independent of the data draws.

### 9.8 Columns and leakage

Canonical columns (FR-01) plus `nominal_value` (datasheet typical value; allowed as an
input). Evaluation-only (`schema.EVALUATION_ONLY_COLUMNS`, excluded by
`model_input_columns`): `true_value_*`, `is_anomaly`, `severity`, `severity_band`,
`behaviour_family`, `lot_scenario`, `anomaly_amplitude`, `level_offset`, `noise_sd`,
`data_fault`, `split` and all `label_*`. `label_safety_slope` is **not** stored: it is
computed on demand for any Δ_allow from the measured values (`labels.py`), which is what
makes the §8.1 sensitivity analysis possible.

### 9.9 E0 audit invariants (fail loudly)

Schema and numeric types; single provenance; no missing identifiers; unique
(component, parameter); each component in one lot; spec limits present, ordered and
constant per parameter; valid split values, no lot or component in two splits, no empty
split; family names from the development registry and none resembling held-out names;
every configured family present; `is_anomaly` agrees with the family; severity and band
consistent; lot counts and sizes per scenario; anomaly counts within the configured
fraction; zero anomalies in normal lots; healthy rows within spec at every checkpoint
(true values); measured values within tolerance of true values (allowing for quantisation
and glitches); missing values only in `missing_value` rows, exactly one each; glitches
only on healthy rows; at least one example of every specification scenario A–E, healthy
near-spec and starts-outside-spec. Reproducibility: the script regenerates in memory and
compares, then re-reads the written CSV and audits it again.

### 9.10 Assumptions and limitations

- All distributions, shapes, magnitudes and fractions are assumptions (the config says
  so); prevalence is a parameter, not a real defect rate.
- Units (µA, ns) are labels for schema testing; the limits (30 µA; 3.8–7.0 ns) are invented.
- A component's parameters degrade independently; there is no correlated multi-parameter failure.
- Healthy near-spec parts are rare (5 rows in v1) — enough to exist, too few to evaluate
  separately.
- Calibration has only 6 lots — per-lot coverage estimates (E5) will be noisy.
- The quantised scenario (2 lots) has no test lot.
- During development the high-mean factor of the current-like parameter was raised from
  2.2 to 2.3 because the audit found no healthy near-spec example; this met a design
  requirement and involved no detector (none exists).
- A first generation (generator 1.0.0) gave the test split no bimodal, lot-drift, small or
  quantised lot. It was never used, was deleted, and is reproducible from commit `09db46e`.
