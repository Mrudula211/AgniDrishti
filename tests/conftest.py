"""Shared fixtures: SYNTHETIC development data, the demo site config, and one pipeline fitted on them (built once)."""

import json
from pathlib import Path

import pytest

from agnidrish.experiments import to_jsonable
from agnidrish.fit import fit_config as build_fit_config
from agnidrish.fit import fit_pipeline
from agnidrish.service import load_pipeline, pipeline_document
from agnidrish.site import load_site
from agnidrish.synthetic.config import load_config
from agnidrish.synthetic.generator import generate

REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_PATH = REPO_ROOT / "configs" / "sites" / "synthetic_demo.yaml"


@pytest.fixture(scope="session")
def synthetic_data():
    return generate(load_config(REPO_ROOT / "configs" / "synthetic" / "development_v1.yaml"))


@pytest.fixture(scope="session")
def site_path():
    return SITE_PATH


@pytest.fixture(scope="session")
def site():
    return load_site(SITE_PATH, REPO_ROOT)


@pytest.fixture(scope="session")
def fit_config(site):
    return build_fit_config(site, REPO_ROOT)


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
