"""Start the AgniDrishti screening service natively (no Docker), on Windows or Linux.

    python scripts/serve.py --pipeline artifacts/models/pipeline/<run>/pipeline.json
    python scripts/serve.py --pipeline latest --host 0.0.0.0 --port 8000 --runs-dir D:/agni/runs

``--pipeline latest`` picks the newest fitted pipeline under artifacts/models/pipeline/ (demo
convenience; a production install should name the file explicitly). Settings are passed to
app.server through the same AGNIDRISH_* environment variables documented there.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
log = logging.getLogger("serve")


def resolve_pipeline(value: str) -> Path:
    if value != "latest":
        path = Path(value) if Path(value).is_absolute() else REPO_ROOT / value
    else:
        found = sorted((REPO_ROOT / "artifacts" / "models" / "pipeline").glob("*/pipeline.json"))
        if not found:
            raise SystemExit("no fitted pipeline found; run scripts/fit_pipeline.py first")
        path = found[-1]
    if not path.is_file():
        raise SystemExit(f"pipeline file not found: {path}")
    return path


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pipeline", required=True, help="pipeline.json path, or 'latest'")
    ap.add_argument("--host", default="127.0.0.1", help="0.0.0.0 to accept connections from other machines")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--runs-dir", help="where runs are recorded (default artifacts/screening)")
    ap.add_argument("--mapping", help="YAML raw->canonical column mapping for the tester export")
    ap.add_argument("--max-upload-mb", type=float)
    args = ap.parse_args()

    pipeline = resolve_pipeline(args.pipeline)
    os.environ["AGNIDRISH_PIPELINE"] = str(pipeline)
    for flag, var in ((args.runs_dir, "AGNIDRISH_RUNS_DIR"), (args.mapping, "AGNIDRISH_MAPPING"), (args.max_upload_mb, "AGNIDRISH_MAX_UPLOAD_MB")):
        if flag is not None:
            os.environ[var] = str(flag)
    for p in (REPO_ROOT, REPO_ROOT / "src"):  # works from a checkout without `pip install -e .`
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    import uvicorn

    log.info("pipeline %s", pipeline.relative_to(REPO_ROOT) if pipeline.is_relative_to(REPO_ROOT) else pipeline)
    log.info("open http://%s:%d/", "localhost" if args.host in ("127.0.0.1", "0.0.0.0") else args.host, args.port)
    uvicorn.run("app.server:app_from_env", factory=True, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
