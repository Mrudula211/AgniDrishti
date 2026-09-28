# Data Sources

Status: Draft · Last updated: 2026-09-26

One entry per dataset. "Unknown" means not established by the available
research; fill in only from the primary source or from inspecting the files.
~~Nothing has been downloaded.~~ Updated 2026-09-26: DS-02 and DS-03 downloaded (Phase 3); DS-01 does not exist; DS-04 v1 generated (synthetic).

**Update 2026-09-26:** DS-01 verified as not published (official PS entry).
DS-02 and DS-03 source pages verified (description, citation, terms, archive
sizes); full external-dataset records are in [external-datasets.md](external-datasets.md),
which supersedes the "Unknown" fields below where they differ.

---

## DS-01 — Official SIH 2026 PS 26170 data

| Field | Value |
|---|---|
| Verification status (2026-09-26) | **OFFICIAL DATASET NOT FOUND** — [official-dataset-verification.md](official-dataset-verification.md) |
| Category | Official SIH/PS |
| Source | SIH 2026 portal / PS owner (ISRO, Department of Space) |
| Access | **Not available.** ~~No official dataset found in public PS material (R3 §8)~~ → verified: the official PS entry's Dataset Link is **empty** (R0). Evaluators hold "hidden ground-truth values" (R0) that are not published. |
| License / usage | Not applicable (no dataset) |
| Variables | R0 names `Value_0h`, `Value_24h`, `Value_168h`; example parameters Iddq, leakage currents, propagation delays. Other fields unknown. |
| Units | Unknown (R0 example uses µA for leakage current; propagation delays would use time units) |
| Temporal resolution | R0: "intervals like 0h, 24h, 96h, and 168h" (examples) |
| Component identifiers | Unknown |
| Lot identifiers | Unknown (required for Module A) |
| Labels | Unknown |
| Missing data | Unknown |
| Limitations | Unknown |
| Intended use | Primary evaluation of all modules |

---

## DS-02 — NASA PCoE: MOSFET Thermal Overstress Aging

| Field | Value |
|---|---|
| Category | External public |
| Source | NASA Ames Prognostics Center of Excellence data repository (per R3) |
| Access | Repository: https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/ · Direct ZIP (per R3): https://phm-datasets.s3.amazonaws.com/NASA/13.+MOSFET+Thermal+Overstress+Aging.zip · Mirror: https://data.phmsociety.org/nasa/ |
| License / usage | ~~Unknown~~ → verified 2026-09-26: PCoE repository asks publications to acknowledge the repository and data donors; data used at own risk. Cite: Celaya, Saxena, Saha, Goebel, "MOSFET Thermal Overstress Aging Data Set", NASA Prognostics Data Repository. Archive size ~7.85 GB (HTTP HEAD). |
| Variables | Inspected: steady-state supply voltage, package temperature, drain-source voltage, drain current, flange temperature; transient waveforms; controller state (external-datasets.md EXT-01) |
| Units | Not stated in files; ranges consistent with °C, V, A |
| Temporal resolution | Dense (≈0.4 s); 0.38–23.45 h per test |
| Component identifiers | File names only (`Test_<N>_run_<M>`); test ↔ device mapping undocumented |
| Lot identifiers | None — **no lot structure** |
| Labels | None in files |
| Missing data | Unreliable flange-temperature channel; one set-up-error file |
| Limitations | Different device type and stress regime; few units; no lots; dense time axis must be resampled; not SIH data |
| Intended use | Realism check for 168h-style prediction (E4), not Module A |
| Downloaded? | ~~No — not reasonable for this phase~~ → Phase 3 (2026-09-26, team request): **downloaded** to `data/external/nasa-mosfet-thermal-overstress/` (7,849,865,909 B, SHA-256 `3b9b5e90…c2f8`), extracted (106 MAT files), inspected. See external-datasets.md EXT-01 and external-dataset-compatibility.md |

---

## DS-03 — NASA: IGBT Accelerated Aging

| Field | Value |
|---|---|
| Category | External public |
| Source | NASA Open Data Portal (per R3) |
| Access | https://data.nasa.gov/dataset/insulated-gate-bipolar-transistor-igbt-accelerated-aging |
| License / usage | ~~Unknown~~ → verified 2026-09-26: NASA Open Data catalogue "other-license-specified" (usa.gov/government-works) + PCoE acknowledgement request. Six devices confirmed. Archive ~240 MB. |
| Variables | Inspected: gate/collector voltages and currents, temperatures, transient waveforms, controller state; SMU I-V for unaged parts (external-datasets.md EXT-02) |
| Units | Not stated in files |
| Temporal resolution | Dense (50 ms – 0.2 s); runs 0.3–4.2 h |
| Component identifiers | Six devices (NASA catalogue); identity from folder names only |
| Lot identifiers | None |
| Labels | None in files |
| Missing data | Device runs split across files with undocumented gaps |
| Limitations | Six devices only; not burn-in; no lots; not SIH data |
| Intended use | Cross-device robustness check for prediction (optional) |
| Downloaded? | ~~No — limited usefulness~~ → Phase 3 (2026-09-26, team request): **downloaded** to `data/external/nasa-igbt-accelerated-aging/` (240,502,381 B, SHA-256 `5cd05410…b997`), extracted, inspected. Secondary use only. See external-datasets.md EXT-02 and external-dataset-compatibility.md |

---

## DS-04 — AgniDrishti synthetic PS-shaped dataset

| Field | Value |
|---|---|
| Category | Synthetic |
| Source | Generated by this project: `scripts/generate_synthetic.py` with `configs/synthetic/development_v1.yaml` ([synthetic-data-design.md](synthetic-data-design.md) §9) |
| Access | Generated locally (git-ignored): `data/synthetic/development/synthetic_development_v1_seed20260926.csv` + `.manifest.json` |
| Version record (v1) | Generator 1.1.0 · seed 20260926 · commit `8ffb75a71b4e9257f4c9b62e59a5fc1522bf9c94` · config SHA-256 `9541202579acf3e5a4b83910580b1478d8213f2524a07874d4d1f23d262ac060` · file SHA-256 `7a170d89efb3ea8a7b90ae3639f5a4b8e760c8167391f3872e457de20491cde0` · regenerated in a fresh process: byte-identical |
| License / usage | Project-internal |
| Variables | Canonical schema in [data-dictionary.md](data-dictionary.md) |
| Units | Arbitrary units unless a unit is explicitly assumed and documented |
| Temporal resolution | 0h, 24h, 96h, 168h (nominal) |
| Component identifiers | Generated: 5990 components (`SYN-Lnnn-Cnnnn`), 2 parameters each (11980 rows) |
| Lot identifiers | Generated: 54 lots (`SYN-Lnnn`), 8 lot scenarios; wafer IDs in bimodal lots |
| Labels | Scenario truth (`is_anomaly`, `severity`, `behaviour_family`); proxy labels computed on demand (`labels.py`, ADR-004) — all our definitions, not official |
| Missing data | Injected deliberately: 57 rows with one checkpoint missing; 53 glitch rows; 2 quantised lots |
| Limitations | Reflects our assumptions only; cannot validate real-world performance; circularity risk (see [synthetic-data-design.md](synthetic-data-design.md)) |
| Intended use | Controlled stress tests, ablation, demo (always labelled synthetic) |
| Derived files | `synthetic_development_v1_test_lots_24h_upload.csv` (2026-09-28): the 10 test-split lots, canonical columns available at 24 h only (no 96/168 h values, no ground truth) — demo upload for the screening service; regenerate with `scripts/make_demo_upload.py` |
