"""Shared fixtures: SYNTHETIC development data and one pipeline fitted on it (session scope, built once)."""

import json
from pathlib import Path

import pytest

from agnidrish.experiments import to_jsonable
from agnidrish.fit import fit_pipeline, load_fit_config
from agnidrish.service import load_pipeline, pipeline_document
from agnidrish.synthetic.config import load_config
from agnidrish.synthetic.generator import generate

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def synthetic_data():
    return generate(load_config(REPO_ROOT / "configs" / "synthetic" / "development_v1.yaml"))


@pytest.fixture(scope="session")
def fit_config():
    return load_fit_config(REPO_ROOT / "configs" / "deployment" / "fit_synthetic_demo.yaml", REPO_ROOT)


@pytest.fixture(scope="session")
def fitted(synthetic_data, fit_config):
    return fit_pipeline(synthetic_data, fit_config)


@pytest.fixture(scope="session")
def pipeline_path(fitted, tmp_path_factory):
    path = tmp_path_factory.mktemp("pipeline") / "pipeline.json"
    doc = pipeline_document(fitted["specs"]["E6"], {"data_category": "synthetic", "alpha": 0.10})
    path.write_text(json.dumps(to_jsonable(doc)), encoding="utf-8")
    return path


@pytest.fixture(scope="session")
def pipeline(pipeline_path):
    return load_pipeline(pipeline_path)


@pytest.fixture(scope="session")
def test_lots(synthetic_data):
    """Held-out synthetic lots as a site would upload them (evaluation columns are still present on purpose)."""
    return synthetic_data[synthetic_data["split"] == "test"].reset_index(drop=True)
