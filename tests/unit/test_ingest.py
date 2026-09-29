from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from agnidrish.ingest import InputProfile, normalize, suggest_profile
from agnidrish.pipeline import FORECAST_NO_MODEL, screen
from agnidrish.quality import FlagCode
from agnidrish.schema import SchemaError
from agnidrish.site import SiteConfig, SiteConfigError, load_site
from agnidrish.units import conversion_factor

REPO_ROOT = Path(__file__).resolve().parents[2]
# Illustrative values only (arbitrary numbers), not measurements.
N = 24
V0 = [10.0 + 0.1 * (i % 6) for i in range(N)]
V24 = [v + 0.2 + 0.03 * (i % 5) for i, v in enumerate(V0)]
SITE = SiteConfig.from_dict({
    "site": "test",
    "parameters": {"ileak": {"aliases": ["I_LEAK"], "unit": "uA", "spec_max": 30.0, "direction": "up"}},
})


def canonical_rows():
    return pd.DataFrame({"component_id": [f"C{i}" for i in range(N)], "lot_id": "L1", "parameter": "ileak",
                         "unit": "uA", "value_0h": V0, "value_24h": V24})


def ingest(raw, profile=None, site=SITE):
    return normalize(raw, InputProfile.from_dict(profile), site, data_category="synthetic", dataset_version="t")


def test_three_layouts_give_the_same_canonical_table():
    a, _ = ingest(canonical_rows())
    long = pd.DataFrame({
        "SerialNo": [f"C{i}" for i in range(N)] * 2, "LotNo": "L1", "TestName": "I_LEAK", "Units": "uA",
        "ReadPoint": ["0h"] * N + ["T23.5"] * N, "Result": V0 + V24,  # 23.5 h snaps to the 24 h checkpoint
    }).sample(frac=1.0, random_state=0)
    b, rep_b = ingest(long, {"layout": "row_per_measurement", "columns": {
        "component_id": "SerialNo", "lot_id": "LotNo", "parameter": "TestName", "unit": "Units", "hour": "ReadPoint", "value": "Result"}})
    wide = pd.DataFrame({"DUT": [f"C{i}" for i in range(N)], "Lot": "L1", "ILEAK_0h": V0, "ILEAK 24 hrs": V24})
    c, _ = ingest(wide, {"layout": "row_per_component", "columns": {"component_id": "DUT", "lot_id": "Lot"}})
    cols = ["component_id", "lot_id", "parameter", "unit", "value_0h", "value_24h", "spec_min", "spec_max", "spec_source"]
    for other in (b, c):
        got = other[cols].sort_values("component_id").reset_index(drop=True)
        pd.testing.assert_frame_equal(got, a[cols].sort_values("component_id").reset_index(drop=True), check_dtype=False)
    assert rep_b.aliased_parameters == {"I_LEAK": "ileak"}
    assert set(a["spec_source"]) == {"registry"} and a["spec_max"].eq(30.0).all()


def test_suggestions_recognise_each_layout_and_a_missing_header():
    long = pd.DataFrame({"Serial Number": ["1"], "Lot No": ["L"], "Test Name": ["x"], "Read Point": ["24"], "Reading": ["1"]})
    s = suggest_profile(long)
    assert s["profile"]["layout"] == "row_per_measurement" and not s["missing_roles"]
    assert s["profile"]["columns"]["component_id"] == "Serial Number"
    wide = pd.DataFrame({"DUT": ["1"], "Batch": ["L"], "Iddq_0h": ["1"], "Iddq_24h": ["1"], "Tpd_T0": ["1"], "Tpd_T24": ["1"]})
    s = suggest_profile(wide)
    assert s["profile"]["layout"] == "row_per_component"
    assert set(s["profile"]["measurement_columns"]) == {"Iddq", "Tpd"}
    per_param = canonical_rows().assign(true_value_0h=0.0)  # ground-truth columns are never proposed
    s = suggest_profile(per_param)
    assert s["profile"]["layout"] == "row_per_parameter" and s["profile"]["hour_columns"] == {0: "value_0h", 24: "value_24h"}
    headerless = pd.DataFrame(columns=["1.009408E+0", "3.634864E-10"])
    assert suggest_profile(headerless)["headerless"]
    with pytest.raises(SchemaError, match="no header row"):
        ingest(pd.DataFrame([[1.0, 2.0]], columns=["1.009408E+0", "3.634864E-10"]), {"layout": "row_per_measurement"})


def test_units_are_converted_and_unconvertible_readings_go_to_review():
    assert conversion_factor("nA", "µA") == pytest.approx(1e-3)
    assert conversion_factor("mV", "uA") is None
    raw = canonical_rows().assign(unit="nA", value_0h=[v * 1000 for v in V0], value_24h=[v * 1000 for v in V24], spec_max=30000.0)
    t, rep = ingest(raw)
    assert t["unit"].eq("uA").all() and t["value_0h"].tolist() == pytest.approx(V0)
    assert t["spec_max"].tolist() == pytest.approx([30.0] * N) and set(t["spec_source"]) == {"file"}  # converted with the values
    bad, rep = ingest(canonical_rows().assign(unit=["V"] + ["uA"] * (N - 1)))
    assert bad.loc[0, "ingest_flags"] == "UNIT_NOT_CONVERTIBLE" and np.isnan(bad.loc[0, "value_0h"])
    assert rep.unit_not_convertible == 2


def test_duplicate_readings_follow_the_configured_policy():
    raw = pd.concat([canonical_rows(), canonical_rows().head(1).assign(value_24h=99.0)], ignore_index=True)
    t, rep = ingest(raw)  # default: review
    assert rep.duplicates == 4 and "DUPLICATE_MEASUREMENT" in t.loc[0, "ingest_flags"] and np.isnan(t.loc[0, "value_24h"])
    last, _ = ingest(raw, {"duplicates": "last"})
    assert last.loc[0, "value_24h"] == 99.0 and last.loc[0, "ingest_flags"] == ""


def test_limit_sources_follow_precedence_and_record_provenance():
    site = SiteConfig.from_dict({
        "parameters": {"ileak": {"unit": "uA", "spec_max": 30.0}, "vth": {"unit": "V", "no_limit": True}},
        "limits": {"sources": ["manual", "file", "table", "registry"], "table_rows": [
            {"parameter": "ileak", "device_family": None, "unit": "nA", "spec_min": None, "spec_max": 20000.0},
            {"parameter": "ileak", "device_family": "FAM-B", "unit": None, "spec_min": None, "spec_max": 10.0}]},
    })
    raw = canonical_rows().assign(device_family=["FAM-A"] * 12 + ["FAM-B"] * 12)
    raw = pd.concat([raw, canonical_rows().assign(parameter="vth", unit="V"), canonical_rows().assign(parameter="new", unit="s")])
    t, rep = ingest(raw, None, site)
    il = t[t["parameter"] == "ileak"]
    assert il["spec_source"].eq("table").all()
    assert il["spec_max"].tolist() == pytest.approx([20.0] * 12 + [10.0] * 12)  # nA converted; family row overrides generic
    assert t.loc[t["parameter"] == "vth", "spec_source"].eq("declared_none").all()
    assert t.loc[t["parameter"] == "new", "spec_source"].eq("none").all() and any("'new'" in w for w in rep.warnings)
    manual, _ = ingest(raw, {"manual_limits": {"new": {"spec_max": 5.0}}}, site)
    assert manual.loc[manual["parameter"] == "new", "spec_source"].eq("manual").all()


def test_readings_away_from_checkpoints_are_ignored_and_reported():
    long = pd.DataFrame({"component_id": ["C1"] * 3, "lot_id": "L1", "parameter": "ileak", "hour": [0, 24, 48], "value": [1.0, 2.0, 3.0]})
    t, rep = ingest(long, {"layout": "row_per_measurement"})
    assert t.loc[0, "value_24h"] == 2.0 and rep.ignored_hours == {"48.0": 1}


def test_new_parameter_uses_lot_rules_not_blanket_review(pipeline, site):
    v24 = list(V24)
    v24[3] = V0[3] + 5.0  # one drifting part
    raw = canonical_rows().assign(parameter="vgs_th", unit="V", spec_min=0.0, spec_max=50.0, value_24h=v24)
    table, _ = normalize(raw, InputProfile(), site, data_category="synthetic", dataset_version="t")
    result = screen(table, pipeline.spec)
    assert result["forecast_status"].eq(FORECAST_NO_MODEL).all()
    assert result.loc[3, "decision"] != "PASS" and "R0" not in result.loc[3, "fired_rules"]
    assert (result["decision"] == "PASS").sum() >= N - 3  # the rest of the lot is cleared, not sent to REVIEW


def test_gate_blocks_missing_limits_but_respects_a_declared_none(pipeline):
    site = SiteConfig.from_dict({"parameters": {"vth": {"unit": "V", "no_limit": True}}})
    none_declared, _ = normalize(canonical_rows().assign(parameter="vth", unit="V"), InputProfile(), site,
                                 data_category="synthetic", dataset_version="t")
    unknown, _ = normalize(canonical_rows().assign(parameter="xyz", unit="V"), InputProfile(), site,
                           data_category="synthetic", dataset_version="t")
    assert not screen(none_declared, pipeline.spec)["gate_codes"].str.contains(FlagCode.NO_SPEC_LIMIT).any()
    r = screen(unknown, pipeline.spec)
    assert r["decision"].eq("REVIEW").all() and r["gate_codes"].str.contains(FlagCode.NO_SPEC_LIMIT).all()


def test_site_configs_in_the_repository_load(tmp_path):
    for path in (REPO_ROOT / "configs" / "sites").glob("*.yaml"):
        site = load_site(path, REPO_ROOT)
        InputProfile.from_dict(site.input)
    with pytest.raises(SiteConfigError, match="alias"):
        SiteConfig.from_dict({"parameters": {"a": {"aliases": ["X"]}, "b": {"aliases": ["x"]}}})
