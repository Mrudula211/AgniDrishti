import numpy as np
import pandas as pd
import pytest

from agnidrish.decision import DecisionConfig, decide, exceeds_safety_slope
from agnidrish.experiments import select_operating_point
from agnidrish.explain import explain_row

FULL = DecisionConfig(use_lot_level=True, use_lot_drift=True, use_prediction=True, use_interval=True,
                      z_review=3.0, z_reject=6.0)


def ev(**over):
    base = dict(gate_flag=False, spec_now=False, z_level=0.0, z_drift=0.0,
                exceed_point=False, exceed_optimistic=False, exceed_pessimistic=False)
    base.update(over)
    return pd.DataFrame([base])


@pytest.mark.parametrize(
    ("evidence", "decision", "first_rule"),
    [
        (ev(), "PASS", "R6"),
        (ev(gate_flag=True, spec_now=True), "REVIEW", "R0"),
        (ev(spec_now=True), "REJECT", "R1"),
        (ev(exceed_point=True, exceed_optimistic=True), "REJECT", "R2"),
        (ev(exceed_point=True), "REVIEW", "R3"),
        (ev(exceed_pessimistic=True), "REVIEW", "R3"),
        (ev(z_level=7.0, z_drift=-7.0), "REJECT", "R4"),
        (ev(z_level=7.0), "REVIEW", "R5"),
        (ev(z_drift=-3.0), "REVIEW", "R5"),
        (ev(z_level=np.nan), "REVIEW", "R0"),
    ],
)
def test_each_rule(evidence, decision, first_rule):
    out = decide(evidence, FULL).iloc[0]
    assert out["decision"] == decision
    assert out["fired_rules"].split(";")[0] == first_rule
    assert out["binary_flag"] == (decision != "PASS")


def test_switched_off_layers_are_ignored():
    e = ev(z_level=9.0, z_drift=9.0, exceed_point=True)
    assert decide(e, DecisionConfig()).iloc[0]["decision"] == "PASS"
    no_interval = DecisionConfig(use_prediction=True)
    assert decide(ev(exceed_point=True), no_interval).iloc[0]["decision"] == "REJECT"


def test_missing_prediction_forces_review_only_when_prediction_is_used():
    e = ev(exceed_point=pd.NA)
    assert decide(e, DecisionConfig(use_prediction=True)).iloc[0]["decision"] == "REVIEW"
    assert decide(e, DecisionConfig()).iloc[0]["decision"] == "PASS"


def test_safety_slope_exceedance():
    v0 = pd.Series([10.0, 10.0, 10.0, np.nan])
    pred = pd.Series([11.4, 11.6, 8.0, 12.0])
    one = pd.Series([0.15] * 4)
    rel = pd.Series([True] * 4)
    up = pd.Series([1.0] * 4)
    lim = pd.Series([np.nan] * 4), pd.Series([50.0] * 4)
    out = exceeds_safety_slope(v0, pred, one, rel, up, *lim)
    assert out.tolist() == [False, True, False, pd.NA]


def test_operating_point_selection_follows_adr005():
    label = pd.Series([True, True, False, False])

    def d(flags, decisions):
        return pd.DataFrame({"binary_flag": flags, "decision": decisions})

    candidates = {
        3.0: d([True, False, False, False], ["REVIEW", "PASS", "PASS", "PASS"]),
        2.0: d([True, True, True, False], ["REVIEW", "REVIEW", "REVIEW", "PASS"]),
        2.5: d([True, True, False, False], ["REVIEW", "REVIEW", "PASS", "PASS"]),
    }
    op = select_operating_point(label, candidates, 1.0)
    assert op["reached_target"] and op["z_review"] == 2.5
    op = select_operating_point(label, {3.0: candidates[3.0]}, 1.0)
    assert not op["reached_target"] and op["z_review"] == 3.0


def test_explanation_reports_the_evidence_numbers():
    row = pd.Series({
        "component_id": "C1", "lot_id": "L1", "parameter": "iddq", "unit": "uA",
        "value_0h": 10.0, "value_24h": 12.5, "spec_min": np.nan, "spec_max": 30.0, "spec_now": False,
        "z_level": 4.25, "lot_median_level": 10.1, "lot_scale_level": 0.5,
        "drift": 2.5, "z_drift": 7.5, "lot_median_drift": 0.2, "gate_codes": "",
        "pred_168h": 14.0, "pred_drift_rate_per_h": 0.0238, "safety_slope_per_h": 0.00893,
        "pi_low": 13.5, "pi_high": 14.5, "decision": "REVIEW", "fired_rules": "R3;R5",
    })
    card = explain_row(row, 0.9, "synthetic")
    text = "\n".join(card["lines"])
    for number in ("12.5", "4.25", "7.5", "14", "13.5", "14.5", "SYNTHETIC", "R3", "R5"):
        assert number in text
    assert "probability of failure" not in text.replace("not a failure probability", "")
    assert card["headline"].endswith("REVIEW (first rule R3)")
