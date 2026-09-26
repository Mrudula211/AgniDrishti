import numpy as np
import pandas as pd

from agnidrish.report import render_report


def screened_rows():
    base = {
        "lot_id": "L1", "parameter": "iddq", "unit": "uA", "value_0h": 10.0, "value_24h": 12.5,
        "spec_min": np.nan, "spec_max": 30.0, "spec_now": False, "z_level": 4.2, "lot_median_level": 10.0,
        "lot_scale_level": 0.5, "drift": 2.5, "z_drift": 7.5, "lot_median_drift": 0.2, "lot_scale_drift": 0.1,
        "gate_codes": "", "pred_168h": 14.0, "pred_drift_rate_per_h": 0.024, "safety_slope_per_h": 0.009,
        "pi_low": 13.5, "pi_high": 14.5,
    }
    return pd.DataFrame([
        {**base, "component_id": "<script>alert(1)</script>", "decision": "REVIEW", "fired_rules": "R3;R5"},
        {**base, "component_id": "C2", "decision": "PASS", "fired_rules": "R6"},
    ])


def test_report_shows_category_counts_and_escapes_html():
    page = render_report(screened_rows(), title="t", category="synthetic", coverage=0.9, pipeline_note="n")
    assert "DATA CATEGORY: SYNTHETIC" in page and "not official SIH/ISRO data" in page
    assert "<script>alert(1)</script>" not in page and "&lt;script&gt;" in page
    assert "12.5" in page and "R3" in page


def test_actual_168h_only_shown_in_evaluation_mode():
    rows = screened_rows().assign(value_168h=31.98)
    assert "31.98" not in render_report(rows, title="t", category="synthetic", coverage=0.9, pipeline_note="n")
    assert "31.98" in render_report(rows, title="t", category="synthetic", coverage=0.9, pipeline_note="n", show_actual=True)
