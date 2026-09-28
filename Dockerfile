# AgniDrishti screening service (ADR-006). Build from the repository root:
#   docker build --build-arg BUILD_COMMIT=$(git rev-parse --short HEAD) -t agnidrishti:0.1.0 .
#   docker run -p 8000:8000 -v <dir with pipeline.json>:/srv/agnidrishti/pipeline:ro \
#              -v agnidrishti-runs:/var/lib/agnidrishti/runs agnidrishti:0.1.0
# The image contains no data and no pipeline: a site mounts its own fitted pipeline.json.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /srv/agnidrishti

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install ".[serve]"

COPY app ./app
COPY configs ./configs
COPY scripts ./scripts

ARG BUILD_COMMIT=unknown
ENV AGNIDRISH_BUILD_COMMIT=${BUILD_COMMIT} \
    AGNIDRISH_PIPELINE=/srv/agnidrishti/pipeline/pipeline.json \
    AGNIDRISH_RUNS_DIR=/var/lib/agnidrishti/runs

RUN useradd --system --uid 10001 agni && mkdir -p /var/lib/agnidrishti/runs && chown agni /var/lib/agnidrishti/runs
USER agni
VOLUME ["/var/lib/agnidrishti/runs"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)"

CMD ["uvicorn", "app.server:app_from_env", "--factory", "--host", "0.0.0.0", "--port", "8000"]
