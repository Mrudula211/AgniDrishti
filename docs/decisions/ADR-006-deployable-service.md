# ADR-006 — Deployable Screening Service and Site Calibration

Status: Accepted · Date: 2026-09-28 · Requested by the team ("complete working prototype … deployable as in a real environment")

## Context

P7 produced a CLI and a static demo page. A burn-in line needs more than that: QA
inspectors upload lot files from the tester, see decisions with evidence, record their
own decision, and auditors must be able to reconstruct any decision later
(FR-12, FR-13, FR-14, NFR-04). The frozen v1 pipeline was fitted on SYNTHETIC data
for two parameters (iddq, tpd); a real site has its own parameters, units and lots,
so it needs a documented way to fit its own pipeline without changing the method.

CLAUDE.md §0 and requirements §3 excluded a web server, deployment and a database.
The team request above lifts the first two for P7. A database stays excluded.

## Options

| # | Option | Outcome |
|---|---|---|
| 1 | FastAPI + uvicorn service, static self-contained UI, file-based run records | **Chosen** — validated request handling and an OpenAPI description; runs offline; no new state store |
| 2 | Streamlit dashboard | Rejected — no stable API for tester or MES integration; state tied to UI sessions |
| 3 | Standard-library `http.server` | Rejected — no request validation, not intended for production use |
| 4 | Add a database for runs and overrides | Rejected for now — immutable run directories plus an append-only override log meet FR-12/13 and NFR-04 with less to operate |

## Decision

1. **Service** (`app/server.py`, `app/static/index.html`): upload CSV → screen → recorded run.
   Endpoints are in the service docstring and at `/docs`. The UI loads nothing from the internet (NFR-12).
2. **One code path**: the CLI (`scripts/screen_lot.py`) and the API both call
   `agnidrish.service`; decisions are computed only by the existing `pipeline.screen`.
3. **Run record** (FR-12, NFR-04): each run is a new directory holding a copy of the input, a copy of the
   pipeline, decisions, lot summary, HTML report and `audit.json` (hashes, category, code version,
   warnings, elapsed time). `/replay` recomputes the run and compares the decisions.
4. **Engineer override** (FR-13): appended to `overrides.jsonl`; the pipeline decision is never changed.
5. **Site calibration** (FR-20, `agnidrish.fit`, `scripts/fit_pipeline.py`): re-runs the
   pre-registered E1–E6 development procedure on the site's historical lots (with measured
   `value_168h`). Site configs set only parameters, directions, Δ_allow and split fractions;
   methods are read from `configs/experiments/pipeline_v1.yaml`.
6. **Fail-safe input handling**: later checkpoints and evaluation-only columns are removed before
   screening; parameters the pipeline was not fitted for go to REVIEW (R0) with a warning;
   unreadable input is rejected (HTTP 400), never screened.
7. **Packaging**: native Python install (virtual environment + `scripts/serve.py`), run as a Windows
   scheduled task / service or a Linux systemd unit. No container: the team chose not to use Docker
   (2026-09-28), and a native process needs nothing beyond Python. The install contains no data;
   the site points the service at its fitted `pipeline.json`.

Not in scope: authentication and TLS (put the service behind the site's reverse proxy or
single sign-on), a database, multi-checkpoint (96 h / 168 h) decision modes, which are not validated.

## Consequences

- Fitting on the synthetic development data reproduces the recorded v1 E6 pipeline exactly, and the
  service reproduces all 2,368 recorded test-lot decisions (deployment.md §5).
- A site pipeline's reported numbers are development numbers until it is evaluated once on lots
  not used for fitting (deployment.md §4).
- One Δ_allow applies to all parameters (PipelineSpec limitation); directions must be `up` or `down`.
