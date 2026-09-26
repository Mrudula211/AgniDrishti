# data/

Data files are git-ignored. Only this README and `.gitkeep` files are committed.
Every dataset must be documented in `docs/research/datasets/data-sources.md`.

| Folder | Contents | Rules |
|---|---|---|
| `raw/` | Original data (official PS data goes in `raw/official/`) | Never modified or overwritten; record file hash |
| `external/` | Third-party public datasets (e.g. NASA PCoE) | Downloaded manually, as-is; licence recorded; never called SIH/ISRO data |
| `synthetic/` | Generated PS-shaped data | Reproducible from config + seed + commit; filename contains `synthetic`; never called real |
| `interim/` | Canonical-schema, validated tables | Regenerable by script |
| `processed/` | Experiment-ready tables | Regenerable by script; versioned |

Current contents (2026-09-26):

- `external/nasa-igbt-accelerated-aging/` — **EXTERNAL — NASA Open Data — IGBT**: original archive + `extracted/`.
- `external/nasa-mosfet-thermal-overstress/` — **EXTERNAL — NASA PCoE**: original archive + `extracted/`.

Provenance, checksums and limitations: `docs/research/datasets/external-datasets.md`. No official PS data exists; `raw/` is empty by design.
