# External Dataset Compatibility with PS 26170

Status: Draft · Last updated: 2026-09-26

> External NASA datasets are used for methodology development and independent
> research validation. They cannot reproduce the official SIH hidden-data
> evaluation because the official PS dataset is not publicly available.

Reference task (official PS, R0): Module B regression **Value_0h + Value_24h →
Value_168h**, scored by MAE against hidden ground truth; Module A lot-relative
("Dynamic") outlier detection; early rejection on a calculated safety slope;
explainability. Provenance of both datasets: [external-datasets.md](external-datasets.md).

No preprocessing has been done. Raw files are untouched, and no external column
has been renamed to `Value_0h` / `Value_24h` / `Value_168h`. Any later mapping
of an external dataset onto a PS-like "early → future" task must be defined in
a separate, documented experiment (mapping, assumptions, information lost) and
must never make the external data look as if it natively had the PS schema.

---

## EXT-01 — NASA MOSFET Thermal Overstress Aging

Based on read-only inspection of all 106 extracted files (2026-09-26). An
earlier version of this section marked every answer TBD while the download was
running; those answers are now filled from the files.

| # | Question | Answer | Label |
|---|---|---|---|
| 1 | Unit of observation | One **run** (one `.mat` file) of a numbered **test**; inside it, steady-state records every ≈0.4 s plus intermittent transient waveforms and controller-state records. | `[SF]` |
| 2 | Component/device identifier | Only the file name (`Test_<N>_run_<M>`). No device-ID field. Whether test N = one physical device is **not documented**. | `[SF]` / `[GAP]` |
| 3 | Measurements available | Steady state: supply voltage, package temperature, drain-source voltage, drain current, flange temperature (unreliable: values down to ≈ −2279.7). Transients: gate-signal, gate-source and drain-source voltages, drain current. Controller: temperature set points, gate/supply voltage, frequency, duty cycle, gate state. Units not stated. | `[SF]` |
| 4 | Timestamps / checkpoints | Continuous timestamps (MATLAB datenum), **no checkpoints**. Per test 0.38–23.45 h recorded (median 3.61 h), split into 1–7 runs over up to 5.5 calendar days. | `[SF]` |
| 5 | Degradation indicator | None stored. Must be derived from drain-source voltage and drain current (e.g. an on-state voltage/current ratio) — a documented, future experiment. The set-point changes within runs mean temperature must be controlled for, so as not to mistake a thermal effect for degradation. | `[EI]` |
| 6 | Early observation window constructible? | **Yes, with caveats**, on cumulative stress time within one test (e.g. the first k hours). Only tests with enough recorded hours qualify (e.g. the six 7-run tests have ≈10–13 h; test 34 has ≈23 h). Gaps between runs and changing set points must be handled explicitly. | `[EI]` |
| 7 | Future target constructible? | **Yes** — the derived indicator at a later cumulative time in the same test. Horizon limited to hours (≤ ≈23 h), not 168 h. | `[EI]` |
| 8 | Early → future forecasting analogous to Module B? | **Yes, as a methodology analogue only**: "value at early time(s) → value at a later time", on real degradation-like data, split by **test** (never by row). The number of usable tests is small (order of 10 with multi-hour, consistent protocols — exact count to be fixed in the experiment definition). It is not Value_0h/24h → Value_168h and must not be relabelled as such. | `[EI]` |
| 9 | Trajectory / drift metric evaluable? | **Yes** — dense series allow slope / drift of a derived indicator per test. | `[EI]` |
| 10 | Uncertainty estimation evaluable? | **Only weakly.** Interval coverage can be computed, but with ≈10 usable tests the coverage estimate itself is very uncertain; any result must report the number of tests and not be generalised. | `[EI]` |
| 11 | Failure / degradation detection evaluable? | **Not directly.** No failure labels; "run-to-failure" is NASA's description, but failure times are not marked. Deriving event labels (e.g. from abrupt current changes) would be our construction, must be documented, and could not be validated against ground truth. | `[GAP]` |
| 12 | PS parts that cannot be evaluated | Lot-relative / "Dynamic" outlier detection (no lots or peers — Module A); the 0/24/96/168 h structure and 168 h horizon; burn-in conditions (heterogeneous overstress protocols up to ≈259 °C); PS parameters (no Iddq, leakage current or propagation delay — drain-source quantities only); spec limits and spec-violation labels; the safety-slope rule on real defect outcomes; the official Anomaly Detection Score and hidden-data MAE; explainability on PS-like decisions. | `[EI]` |

**Verdict for EXT-01:** the most useful external source for *forecasting
methodology* (early → later value on real device degradation, split by test).
It cannot evaluate Module A, cannot reproduce the PS time scale, and supports
only small-sample conclusions.

---

## EXT-02 — NASA IGBT Accelerated Aging

Based on read-only inspection of the extracted files and the bundled paper
(Sonnenfeld, Goebel, Celaya).

| # | Question | Answer | Label |
|---|---|---|---|
| 1 | Unit of observation | One **ageing run of one device**, stored as one or more `.mat` files; inside each file, time-stamped samples (steady-state ≈0.2 s; transient waveforms every ≈23 s; DC run 50 ms). Separately, single-time SMU characterisation files for unaged parts. | `[SF]` |
| 2 | Component/device identifier | No identifier field. Identity comes only from folder/file names (`Device 2`–`Device 5`, the A17 file name, the DC-run timestamp name) and from `N.txt` part numbers in the SMU folders. | `[SF]` |
| 3 | Measurements | Gate / collector voltages and currents, supply and node voltages, heat-sink / package / internal / ambient temperatures, transient gate-emitter and collector-emitter waveforms, PWM controller state. SMU: I-V sweeps (breakdown, leakage, turn-on); units not stated. | `[SF]` |
| 4 | Timestamps / checkpoints | Continuous timestamps; **no checkpoints**. Run lengths: 0.33–0.93 h (Device 2–5 files), 2.86 h (A17), 4.19 h (DC). | `[SF]` |
| 5 | Degradation indicator | Not stored as a variable. Per the paper: collector-emitter turn-off transient peak voltage (≈15 % decrease towards failure, one device) and latch-up (average current ≈4 A → ≈10 A). Deriving it requires waveform processing — a future, documented experiment. | `[SF]` paper; `[EI]` derivation needed |
| 6 | Early observation window constructible? | **Technically yes**, on a relative time axis within a run (e.g. the first fraction of a run). Any mapping to "0h/24h" is an analogy, not a PS equivalent. Device 2–5 runs are split across files with undocumented gaps, which complicates a continuous window. | `[EI]` |
| 7 | Future target constructible? | **Technically yes** — a later-time value of a derived indicator in the same run. Whether runs end at failure is not labelled. | `[EI]` / `[GAP]` |
| 8 | Early → future forecasting analogous to Module B? | **Only as a qualitative structural analogy.** With 6 devices under three different protocols there is no meaningful held-out evaluation: an MAE computed here would describe 1–6 runs, not a method's generalisation. | `[EI]` |
| 9 | Trajectory / drift metric evaluable? | **Yes, descriptively** — dense time series allow drift / slope of a derived indicator per run. Not comparable across devices without normalisation assumptions. | `[EI]` |
| 10 | Uncertainty estimation evaluable? | **No, not meaningfully.** Interval coverage needs many independent units for calibration and testing; 6 devices cannot support it. | `[EI]` |
| 11 | Failure / degradation detection evaluable? | **Weakly at most.** No failure labels; the paper describes the failure signature (latch-up). Any event labels would have to be derived and documented — never fabricated. | `[GAP]` |
| 12 | PS parts that cannot be evaluated | Lot-relative / "Dynamic" outlier detection (no lots, no peers); the 0/24/96/168 h structure and 168 h horizon (runs last hours); burn-in-like stress (≈300 °C overstress versus R0's example "e.g., 125°C for extended periods"); PS parameters (no Iddq or propagation delay over ageing; leakage only for unaged parts); spec limits and spec-violation labels; the safety-slope rule; the official Anomaly Detection Score and hidden-data MAE; explainability to a QA inspector on PS-like decisions. | `[EI]` |

**Verdict for EXT-02:** usable only for secondary, qualitative checks — whether
a forecasting or trajectory method behaves sensibly on a different device family
and stress regime. It is not a benchmark and supports no statistical claims.

---

## What no external dataset can evaluate

These remain impossible to evaluate without the official SIH data:

1. Performance on the **official hidden ground truth** (MAE on Value_168h).
2. The official **Anomaly Detection Score** (its formula is not published).
3. **Lot-relative** ("Dynamic") outlier detection on real lots.
4. The actual PS **parameters, units and checkpoints** under real burn-in conditions.
5. Calibration of the **safety slope** against real defective / non-defective parts.
6. Real **defect prevalence** and the real false-negative / false-positive trade-off.

These gaps are covered only partially, and under stated assumptions, by the
future synthetic PS-shaped dataset (separate phase), which must avoid circular
generator / detector design (claim-register C-11).

## Data-mixing rule

EXT-01, EXT-02 and future synthetic data stay **separate evaluation sources**.
Any combination requires a documented experiment stating: why, which variables
are compatible, what normalisation is needed, what is assumed, what information
is lost, and why the combination does not produce misleading results.
