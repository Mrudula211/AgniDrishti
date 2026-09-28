# Deployment and Operation

Status: Draft · Last updated: 2026-09-28 · Decision: [ADR-006](../decisions/ADR-006-deployable-service.md)

How to run AgniDrishti as a screening service at a burn-in line. Everything is
offline: no data leaves the machine (NFR-12).

## 1. Components

```
tester export (CSV) ──► POST /api/screen ──► agnidrish.service ──► pipeline.screen (L0–L7)
                                               │
                                               └─► runs/<run_id>/ input.csv · pipeline.json · decisions.csv
                                                                  lot_summary.csv · report.html · audit.json
                                                                  overrides.jsonl (engineer decisions, append-only)
QA inspector ◄── web UI (/)  ·  API description (/docs)  ·  health (/api/health)
```

| Endpoint | Purpose |
|---|---|
| `GET /` | QA-inspector UI: upload, decisions, lot table, evidence cards, engineer decisions |
| `POST /api/screen?category=…&source=…&version=…` | Body = CSV (`text/csv`). Screens and records a run |
| `GET /api/runs`, `GET /api/runs/{id}` | Recorded runs and their decisions |
| `GET /api/runs/{id}/rows/{row}` | Evidence card: explanation lines, rules, trajectory chart |
| `POST /api/runs/{id}/overrides` | `{row, decision, engineer, reason}` → engineer decision (FR-13) |
| `GET /api/runs/{id}/replay` | Recompute from stored input + pipeline; `identical: true/false` (NFR-04) |
| `GET /api/runs/{id}/files/{name}` | `decisions.csv`, `lot_summary.csv`, `report.html`, `audit.json`, `overrides.jsonl` |
| `GET /api/pipeline`, `GET /api/health` | Frozen settings and provenance; liveness |

## 2. Input format

Any tester export: one row per reading, per component and parameter, or per component. The site
config (`configs/sites/<site>.yaml`) describes the usual format, parameter registry and where
specification limits come from; the web UI detects the format of an unseen file and lets the engineer
confirm the mapping before screening. Full reference: [data-ingestion.md](data-ingestion.md).
Screen **whole lots**: the lot-relative statistics use every component of the lot in the file, and lots
below 20 components go to REVIEW.

## 3. Fit a site pipeline (once per site / product, and after process changes)

1. Collect historical burn-in lots with 0 h, 24 h **and** 168 h readings, in the site's export format.
2. In the site config, give every parameter that should get a 168 h forecast a `direction` (`up`/`down`),
   and set `calibration.allowance` Δ_allow (a reliability decision for the site, ADR-002). Parameters without a
   direction are screened without a forecast.
3. Run:
   ```
   python scripts/fit_pipeline.py --input history.csv --category official --site configs/sites/<site>.yaml
   ```
   Output: `artifacts/models/pipeline/<run>/pipeline.json`, `fit_metrics.json`, `fit_summary.md`
   (Module B MAE per predictor, interval coverage, operating point, validation recall and review rate, and the
   same rules without the forecast).

## 4. Before relying on a site pipeline

The fit summary reports development numbers (thresholds were chosen on those lots). Hold back some
later lots, screen them once with the frozen pipeline, compare with their measured 168 h outcome
using `agnidrish.metrics`, and record the result. Refit only with a new, dated site config;
never re-tune on the lots used for that check (CLAUDE §7).

## 5. Run

Native install. No Docker is needed; the same commands work on Windows and Linux with Python 3.11+:
```
python -m venv .venv
.venv\Scripts\activate            # Linux: source .venv/bin/activate
pip install -e ".[serve]"
python scripts/serve.py --site configs/sites/<site>.yaml --pipeline artifacts/models/pipeline/<run>/pipeline.json --host 0.0.0.0 --port 8000 --runs-dir <backed-up dir>
```
Open `http://<host>:8000/`. Use `--host 127.0.0.1` (default) for a single workstation, and `0.0.0.0` to
serve the line's network (allow the port in the host firewall). `--pipeline latest` picks the newest
fitted pipeline, which is convenient for demos; name the file explicitly in production.

Keep it running after logout or reboot:

- **Windows:** Task Scheduler → *Create Task* → trigger *At startup*, "Run whether user is logged on or not";
  action: program `<repo>\.venv\Scripts\python.exe`, arguments `scripts\serve.py --site <site.yaml> --pipeline <file> --host 0.0.0.0`,
  start in `<repo>`. A service wrapper (e.g. NSSM) works the same way.
- **Linux (systemd):** a unit with `WorkingDirectory=<repo>`,
  `ExecStart=<repo>/.venv/bin/python scripts/serve.py --site <site.yaml> --pipeline <file> --host 0.0.0.0 --runs-dir /var/lib/agnidrishti/runs`,
  `Restart=on-failure`, run as a dedicated non-root user.

`scripts/serve.py` sets the variables below; they can also be set directly when running
`uvicorn app.server:app_from_env --factory`.

| Variable | Default | Meaning |
|---|---|---|
| `AGNIDRISH_PIPELINE` | — (required) | Frozen pipeline JSON; the service refuses to start without it |
| `AGNIDRISH_RUNS_DIR` | `artifacts/screening` | Run records (back this directory up; it is the audit trail) |
| `AGNIDRISH_SITE` | — (required) | Site config: input format, parameter registry, limit sources ([data-ingestion.md](data-ingestion.md)) |
| `AGNIDRISH_MAX_UPLOAD_MB` | 50 | Upload limit (HTTP 413 above it) |

Security: the service has no authentication or TLS. Put it behind the site's reverse proxy /
single sign-on on the internal network. Run records contain measurement data. Protect them like the tester data.

## 6. Verified so far (SYNTHETIC data only)

| Check | Result | Evidence |
|---|---|---|
| Site fit on synthetic development data reproduces the recorded v1 E6 pipeline | identical spec | `scripts/fit_pipeline.py` run of 2026-09-26 vs `artifacts/metrics/E1-E6_validation/20260926-144425_c8ca99b/frozen_pipeline.json` |
| Service decisions on the 10 held-out test lots (2,368 rows) vs recorded final run | 2,368 / 2,368 identical decisions and fired rules | in-process API check 2026-09-28 vs `artifacts/metrics/E1-E6_test/20260926-144448_c8ca99b/test_decisions.csv` |
| Replay of that run | identical | `/api/runs/20260928-094007_d5a1a07/replay` (temporary runs dir) |
| Screening time for that upload | 554 ms for 2,368 rows / 10 lots, one measurement on the development laptop | `audit.json` `elapsed_ms`; not a benchmark — NFR-07/08: TBD — experiment not yet executed |
| After the ADR-007 ingest redesign: site-config fit reproduces the recorded E6 pipeline; service reproduces all 2,368 recorded decisions and fired rules; replay identical | all identical | check of 2026-09-28 with `artifacts/models/pipeline/20260928-134603_4c2bad5` |
| Same held-out lots exported in a different format (one row per reading, other column names, `;` delimiter, text hours) | identical decisions to the canonical upload | `tests/integration/test_api.py::test_foreign_export_is_inspected_mapped_and_screened` |
| Automated tests | ingest, fit, service and API tests in `tests/` (111) | `python -m pytest` |

Detection performance on synthetic lots is in [ablation-plan.md](../research/experiments/ablation-plan.md) §3–§5
(recall 0.800 at 10.4 % review on test; R* = 0.95 not reached). Nothing here is evidence about ISRO hardware.
