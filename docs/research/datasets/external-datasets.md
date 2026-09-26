# External Datasets

Status: Draft · Last updated: 2026-09-26

> **External NASA datasets are used for methodology development and independent
> research validation. They cannot reproduce the official SIH hidden-data
> evaluation because the official PS dataset is not publicly available.**

These datasets are **not** SIH, ISRO or PS 26170 data. No official-PS accuracy,
SIH benchmark performance, expected SIH score or hidden-test performance may be
claimed from them. Each dataset is an **independent** evaluation source; they
are not combined with each other or with synthetic data unless a documented
experiment justifies it.

This document supersedes the pre-download version of the same file (which
recorded only catalogue information and a "do not download yet" decision). The
download was then explicitly requested by the team (Phase 3, 2026-09-26).

## Summary

| Dataset | Authority | Category label | Devices | Stress | Data type | Intended use | Limitations |
|---|---|---|---:|---|---|---|---|
| NASA MOSFET Thermal Overstress Aging | NASA Ames PCoE | **EXTERNAL — NASA PCoE** | Not established from files (42 numbered tests + 1 ramp-up file; test ↔ device mapping undocumented) | Thermal overstress (package temperature up to ≈259 °C; controller settings vary between tests) | Run-to-failure per NASA; dense time series (0.4 s), 106 runs, 0.38–23.45 h per test | Primary external dataset for forecasting / prognostics methodology | Not SIH burn-in; no lots; no failure labels; heterogeneous protocols; hours, not 168 h |
| NASA IGBT Accelerated Aging | NASA Open Data / PCoE | **EXTERNAL — NASA Open Data — IGBT** | 6 (NASA catalogue) | Thermal overstress (≈300 °C package temperature observed) | Accelerated ageing, dense time series, runs of minutes–hours | Secondary robustness / cross-device sanity checks only | Very small sample (6); runs last 0.3–4.2 h; no labels file; no lots |

---

## EXT-01 — NASA PCoE: MOSFET Thermal Overstress Aging

**Label: EXTERNAL — NASA PCoE**

| Field | Value |
|---|---|
| Official source | NASA Ames Prognostics Center of Excellence (PCoE) Data Set Repository — https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/ |
| Direct download URL | https://phm-datasets.s3.amazonaws.com/NASA/13.+MOSFET+Thermal+Overstress+Aging.zip (linked from the PCoE repository page) |
| Local path | `data/external/nasa-mosfet-thermal-overstress/` |
| Original filename | `13. MOSFET Thermal Overstress Aging.zip` (S3 object name with `+` decoded as space) |
| File size | 7,849,865,909 bytes (HTTP `Content-Length`); server last-modified 2022-09-18 |
| Download date | 2026-09-26; started ≈06:33 UTC, one connection reset (curl exit 56) resumed from the partial file, completed **07:33:51 UTC**. Written to `…zip.part` and renamed to the original filename only after the size matched exactly. |
| File size (downloaded) | 7,849,865,909 bytes — identical to `Content-Length` |
| SHA-256 | `3b9b5e90cf72e867ccab94c9ea3b8a7a54290e6517a7134d685da462ed4fc2f8` |
| Integrity | `unzip -t`: "No errors detected" (CRC check also confirms the resumed transfer joined correctly) |
| Archive structure | Folder `13. MOSFET Thermal Overstress Aging/` containing nested archive `MOSFET_Thermal_Overstress_Aging_v0.zip` (7,847,858,146 bytes; SHA-256 `82c9a8492a928ebde18d7f8a18cdd9bbdb58cbac820cea355feb4bcfb44e14b7`; dated 2022-09-17) |
| Extraction status | Nested archive extracted to `extracted/` (106 files, ≈7.5 GB). The intermediate nested ZIP was written to a temporary folder outside the repository and deleted after extraction (reproducible from the original; hash above). Original archive untouched. |
| Extracted directory structure | `extracted/MOSFET_Thermal_Overstress_Aging_v0/` — flat folder of 106 MATLAB 5.0 `.mat` files: `Test_<N>_run_<M>.mat` for N = 1…42 (1–7 runs per test), `test_rampup.mat`, and `Test_13_run_1 1 (error setting up this run).mat` (name marks a failed set-up). No README or documentation file is included. |
| License / usage | PCoE repository: publications "are requested to acknowledge both the assistance received by using this repository and the donators of the data"; data used "at their own risk". |
| Citation (requested by NASA) | J. R. Celaya, A. Saxena, S. Saha, and K. Goebel, "MOSFET Thermal Overstress Aging Data Set", NASA Prognostics Data Repository |
| Description (NASA, verbatim) | "Run-to-failure experiments on Power MOSFETs under thermal overstress." |
| Number of devices | **Not established.** The files contain 42 numbered tests (+ `test_rampup`). Whether each test is one physical device (and runs of a test are successive stress sessions of that device) is **not documented** in the archive; the repository's reference document is "Currently offline". `[GAP]` |
| Measured variables (all 106 files, same layout) | `measurement.steadyState[].timeDomain`: `supplyVoltage`, `packageTemperature`, `drainSourceVoltage`, `drainCurrent`, `flangeTemperature` (+ `date`, `timeEpoch`, `nanosec_time`). `measurement.transient[].timeDomain`: `dt`, `gateSignalVoltage`, `gateSourceVoltage`, `drainSourceVoltage`, `drainCurrent` (waveforms of 500 / 1000 / 5000 points; dt 0.2–2 µs; 2 files with empty/degenerate transients). `measurement.pwmTempControllerState[]`: `lowTemp`, `highTemp`, `shutdownTemp`, `gateVoltage`, `supplyVoltage`, `switchingFrequency`, `dutyCycle`, `gateState`. `[SF]` (files) |
| Units | Not stated in the files. Value ranges are consistent with °C, V, A. `[GAP]` |
| Temporal resolution | Steady-state records every ≈0.4 s (1,906,566 records in total); transient captures intermittently. Timestamps are MATLAB datenums (≈734187 → 17 Feb 2010) with matching date strings; recordings span Feb–Sep 2010. `[SF]` |
| Run / test durations | Per run 0.003–8.0 h. Per test (sum of runs) 0.38–23.45 h, median 3.61 h; runs of one test spread over up to 5.5 calendar days with undocumented gaps. Runs per test: 1 run (20 tests), 2 (11), 3 (2), 4 (1), 5 (1), 6 (1), 7 (6). `[SF]` (computed from timestamps) |
| Stress conditions | Package temperature maxima 29–259 °C per file. Controller settings **differ between tests**: high-temperature set points step through values such as 40→100→150→200→(210–280) within runs; shutdown temperatures 120–330; supply voltage 1–8 V; gate voltage 0–10 V. Heterogeneous protocol. `[SF]` |
| Data quality observations | `flangeTemperature` contains physically implausible values (minimum ≈ −2279.7), so that sensor channel is unreliable in at least some files. One file is explicitly named as a set-up error. Some runs last seconds to minutes. `[SF]` |
| Failure / degradation labels | **No label field or file.** NASA's description says "run-to-failure", but which runs end in failure, and when, is not marked. `[GAP]` |
| Degradation indicator | Not stored as a variable. Candidate indicators must be **derived** from stored `drainSourceVoltage` / `drainCurrent` (e.g. an on-state voltage-to-current ratio) under a documented experiment; the choice is not established by documentation in the archive. `[EI]` |
| Limitations | Not burn-in screening; no lots or peer groups; no spec limits; no labels; heterogeneous stress protocols; device identity undocumented; tests last hours (max ≈23 h), not 168 h; power MOSFET under overstress ≠ PS components; one unreliable channel |
| Intended use in AgniDrishti | Primary external source for degradation-trajectory analysis and early-window → later-value forecasting **methodology** (E4 / R-04), restricted to tests with enough recorded time and a consistent protocol, defined in a documented experiment. See [external-dataset-compatibility.md](external-dataset-compatibility.md). |

## EXT-02 — NASA Open Data: IGBT Accelerated Aging

**Label: EXTERNAL — NASA Open Data — IGBT**

### Provenance

| Field | Value |
|---|---|
| Official source | NASA Open Data Portal — https://data.nasa.gov/dataset/insulated-gate-bipolar-transistor-igbt-accelerated-aging (publisher: PCoE; maintainer: Christopher Teubert; issued 2022-11-22; modified 2025-05-29). Also listed on the PCoE repository page. |
| Direct download URL | https://phm-datasets.s3.amazonaws.com/NASA/8.+IGBT+Accelerated+Aging.zip |
| Download date | 2026-09-26, completed 06:48:44 UTC (`curl`, HTTP 200) |
| Local path | `data/external/nasa-igbt-accelerated-aging/` |
| Original filename | `8. IGBT Accelerated Aging.zip` (unmodified) |
| File size | 240,502,381 bytes (matches `Content-Length`); server last-modified 2022-09-18 |
| SHA-256 | `5cd05410e0670f78fbb9b62e9784cd65638eac435c8dac6b738076395781b997` |
| Integrity | `unzip -t`: "No errors detected" |
| Archive structure | Folder `8. IGBT Accelerated Aging/` containing nested archive `IGBTAgingData_04022009.zip` (240,501,751 bytes; SHA-256 `77cc930c68d7674e694b4aa4f33b94e854bb66b147deb170d0131662f176c2e0`). The nested file name matches the resource listed in the NASA catalogue. |
| Extraction status | Nested archive extracted to `extracted/`. The intermediate nested ZIP is **not** kept as a separate file (it is reproducible byte-for-byte from the original archive; its hash is recorded above). Original archive untouched. |
| Extracted contents | `extracted/IGBTAgingData_04022009/` — 199 files, ≈246 MB |
| License / usage | Catalogue: "other-license-specified", referencing https://www.usa.gov/government-works; PCoE acknowledgement request applies. |
| Citation (requested by NASA) | J. Celaya, Phil Wysocki, and K. Goebel (2009), "IGBT Accelerated Aging Data Set", NASA Prognostics Data Repository |
| Bundled reference | `Sonnenfeld_Goebel_Celaya.pdf` — G. Sonnenfeld, K. Goebel, J. Celaya, "An Agile Accelerated Aging, Characterization and Scenario Simulation System for Gate Controlled Power Transistors" |

### Extracted directory structure

```
extracted/IGBTAgingData_04022009/
├── Sonnenfeld_Goebel_Celaya.pdf
└── Data/
    ├── Thermal Overstress Aging with DC at gate/
    │   └── 20080429T135531.mat                                 (11.1 MB)
    ├── Thermal Overstress Aging with Square Signal at gate/
    │   └── april22nd-23rdIgbtIRCG40BC30kd-A17.mat              (87.7 MB)
    ├── Thermal Overstress Aging with Square Signal at gate and SMU data/
    │   ├── Aging Data/
    │   │   ├── Device 2/  Device2  1.mat, Device2b  1.mat, Device2check  1.mat
    │   │   ├── Device 3/  Device3  1.mat, Device3b  1.mat, Device3check  1.mat
    │   │   ├── Device 4/  Device4  1.mat, Device4b  1.mat
    │   │   └── Device 5/  Device5  1.mat, Device5check  1.mat
    │   └── SMU Parameter Characterization/  Part 1 … Part 5/
    │         (N.txt, Breakdown.csv, LeakageIV.csv, Turn On.csv)
    └── SMU Data for new devices/
        ├── IGBT-IRG4BC30K/     20 "Part" folders (same 4 files each)
        └── MOSFET-IRF520Npbf/  20 "Part" folders (same 4 files each)
```

All `.mat` files are MATLAB 5.0 format (readable with `scipy.io.loadmat`).

### Content (from read-only inspection, 2026-09-26)

| Item | Finding | Label |
|---|---|---|
| Number of devices | 6, per NASA catalogue ("one device aged with DC gate bias and the rest aged with a squared signal gate bias"). Files show 6 aged-run groups: 1 DC-gate run, 1 square-signal run (A17), Devices 2–5. The one-to-one mapping of these groups to the catalogue's 6 devices is our reading of the folder names. | `[SF]` count; `[EI]` mapping |
| DC-gate run variables | `GATE_VOLTAGE`, `COLLECTOR_VOLTAGE`, `GATE_CURRENT`, `COLLECTOR_CURRENT`, `HEAT_SINK_TEMP`, `PACKAGE_TEMP`, `TIME` (301,680 samples each) plus scalar last-sample fields | `[SF]` (file) |
| Square-signal runs, structure | `measurement` struct with `pwmTempControllerState` (lowTemp, highTemp, shutdownTemp, gateVoltage, supplyVoltage, switchingFrequency, dutyCycle, gateState), `steadyState.timeDomain` (supplyVoltage, node1Voltage, node2Voltage, collectorEmitterCurrent, heatSinkTemperature, packageTemperature, internalTemperature, ambientTemperature), `transient.timeDomain` (dt, gateSignalVoltage, gateEmitterVoltage, collectorEmitterVoltage, collectorEmitterCurrentSignal); the A17 file also has a `report` text field | `[SF]` (file) |
| Units | Not stated in the files. Paper context indicates °C, V, A. | `[GAP]` |
| Time base | Epoch seconds ≈3.29–3.31 × 10⁹, consistent with a 1904-based (LabVIEW) epoch → dates in 2008, matching the `date` strings in the files | `[EI]` |
| Run durations | DC run 4.19 h; A17 run 2.86 h (22 Apr 2008 21:10 → 23 Apr 00:01); Device 2–5 files 0.33–0.93 h each; "check" files < 1 min | `[SF]` (computed from timestamps) |
| Sampling | DC run 50 ms; steady-state ≈0.2 s; transient waveforms of 125,000 points at 8 ns, captured every ≈23 s | `[SF]` |
| Temperatures observed | Package temperature up to ≈305 °C (DC run) and ≈297 °C (square-signal runs). Paper: set point ≈330 °C | `[SF]` |
| SMU CSVs | Two numeric columns, no header, units not stated. "New devices" folders characterise 20 unaged IGBT IRG4BC30K and 20 unaged MOSFET IRF520Npbf parts at a single time point. `N.txt` holds part ID, test type, device type, operator, date/time. | `[SF]` structure; `[GAP]` units/column meaning |
| Failure labels | No label field or file. Paper: IGBTs "either fail very early, within the first several minutes of testing, or survived from 1 to 4 hours before loss of gate control or thermal runaway"; failure shown as latch-up (average on-state current ≈4 A → ≈10 A). Whether each file ends at failure is **not established**. | `[SF]` paper; `[GAP]` per-run labels |
| Degradation indicator | Paper: collector-emitter **turn-off transient peak voltage** decreased ≈15 % from initial to near failure (single IGBT, Fig. 10); authors attribute it most likely to package thermal-impedance degradation. It is not a stored variable; it would have to be derived from transient waveforms. | `[SF]` paper |

### Limitations

- Only 6 aged devices, with three different protocols (DC gate, square gate, square gate with SMU) → no statistically meaningful held-out evaluation.
- Timescale of minutes to hours at ≈300 °C; this is acute thermal overstress, not burn-in (R0 example: e.g. 125 °C for extended periods, checkpoints like 0/24/96/168 h).
- No lots, no peer groups, no spec limits, no failure labels.
- Parameters differ from the PS examples (no Iddq or propagation delay; leakage I-V exists only for unaged parts).
- Device 2–5 data is split across several files per device ("", "b", "check"); ordering and gaps between files are not documented.

### Intended use in AgniDrishti

Secondary only: a cross-device sanity check of whether a forecasting method
behaves sensibly on another device family, and a demonstration that the
methodology is not tuned to a single dataset. Not a benchmark; no strong
generalisation claims.

---

## Not downloaded (by rule)

Team GitHub repositories, SIH aggregator sites, Kaggle PS-list datasets and any
source without authoritative provenance.
