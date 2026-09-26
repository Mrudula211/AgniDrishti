"""Self-contained HTML screening report (prototype, P7). Shows only computed pipeline outputs.

No external scripts or fonts; charts are inline SVG. Every page shows the data category.
"""

from __future__ import annotations

import html
import math
from typing import Any

import pandas as pd

from agnidrish.explain import explain_row

CSS = """
:root{--bg:#f7f8fa;--card:#fff;--ink:#1c2430;--muted:#5b6675;--line:#d9dee5;--pass:#1f7a4d;--review:#a86400;--reject:#b3261e;--accent:#1d4f91;--band:#e6ecf5}
@media (prefers-color-scheme:dark){:root{--bg:#12161c;--card:#1b2129;--ink:#e6e9ee;--muted:#9aa4b2;--line:#2c3440;--pass:#4cc38a;--review:#f0a53a;--reject:#f2665c;--accent:#7fb0ff;--band:#243044}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 64px}h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:32px 0 10px}
.banner{background:var(--reject);color:#fff;padding:8px 16px;font-weight:600;text-align:center}
.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}.tile b{font-size:26px;display:block}
.PASS{color:var(--pass)}.REVIEW{color:var(--review)}.REJECT{color:var(--reject)}
table{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:14px}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left}th{background:var(--band)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:12px 0;display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:16px}
.card h3{margin:0 0 8px;font-size:16px}.card ul{margin:0;padding-left:18px}.card li{margin:3px 0}
@media (max-width:760px){.card{grid-template-columns:1fr}}svg text{fill:var(--muted);font-size:11px}
.wrap{overflow-x:auto}
"""


def _esc(x: Any) -> str:
    return html.escape(str(x))


def trajectory_svg(row: pd.Series, show_actual: bool) -> str:
    """0 h and 24 h measured, lot band at 24 h, spec limit, safety-slope line, predicted 168 h with interval."""
    w, h, pad = 360, 220, 36
    xs = {0: 0.0, 24: 24.0, 168: 168.0}
    pts = [row["value_0h"], row["value_24h"]]
    extra = [row.get("pred_168h"), row.get("pi_low"), row.get("pi_high"), row.get("spec_max"), row.get("spec_min"),
             row.get("lot_median_level", float("nan")) + 3 * row.get("lot_scale_level", float("nan")),
             row.get("lot_median_level", float("nan")) - 3 * row.get("lot_scale_level", float("nan"))]
    slope = row.get("safety_slope_per_h")
    if slope is not None and not pd.isna(slope):
        extra.append(row["value_0h"] + slope * 168.0)
    if show_actual:
        extra.append(row.get("value_168h"))
    vals = [float(v) for v in pts + extra if v is not None and not pd.isna(v) and math.isfinite(float(v))]
    if not vals:
        return ""
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    lo, hi = lo - 0.08 * span, hi + 0.08 * span

    def X(t: float) -> float:
        return pad + (t / 168.0) * (w - 2 * pad)

    def Y(v: float) -> float:
        return h - pad + (-(v - lo) / (hi - lo)) * (h - 2 * pad)

    parts = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="trajectory chart">',
             f'<line x1="{pad}" y1="{h - pad}" x2="{w - pad}" y2="{h - pad}" stroke="currentColor" opacity=".3"/>']
    for t in (0, 24, 96, 168):
        parts.append(f'<text x="{X(t):.1f}" y="{h - pad + 16}" text-anchor="middle">{t} h</text>')
    for v in (lo + 0.08 * span, hi - 0.08 * span):
        parts.append(f'<text x="4" y="{Y(v) + 4:.1f}">{v:.3g}</text>')
    med, sc = row.get("lot_median_level"), row.get("lot_scale_level")
    if med is not None and not pd.isna(med) and sc is not None and not pd.isna(sc):
        y1, y2 = Y(med + 3 * sc), Y(med - 3 * sc)
        parts.append(f'<rect x="{X(24) - 10:.1f}" y="{y1:.1f}" width="20" height="{max(y2 - y1, 1):.1f}" fill="var(--band)"><title>lot median ± 3 robust sigma at 24 h</title></rect>')
    for key, label in (("spec_max", "limit"), ("spec_min", "limit")):
        v = row.get(key)
        if v is not None and not pd.isna(v) and lo <= v <= hi:
            parts.append(f'<line x1="{pad}" x2="{w - pad}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--reject)" stroke-dasharray="5 4"/>'
                         f'<text x="{w - pad}" y="{Y(v) - 4:.1f}" text-anchor="end">{label} {v:.3g}</text>')
    if slope is not None and not pd.isna(slope):
        parts.append(f'<line x1="{X(0):.1f}" y1="{Y(row["value_0h"]):.1f}" x2="{X(168):.1f}" y2="{Y(row["value_0h"] + slope * 168):.1f}" '
                     f'stroke="var(--review)" stroke-dasharray="2 3"><title>safety slope from the 0 h value</title></line>')
    pred = row.get("pred_168h")
    if pred is not None and not pd.isna(pred):
        parts.append(f'<line x1="{X(24):.1f}" y1="{Y(row["value_24h"]):.1f}" x2="{X(168):.1f}" y2="{Y(pred):.1f}" stroke="var(--accent)" stroke-dasharray="6 4"/>')
        if row.get("pi_low") is not None and not pd.isna(row.get("pi_low")):
            parts.append(f'<line x1="{X(168):.1f}" x2="{X(168):.1f}" y1="{Y(row["pi_low"]):.1f}" y2="{Y(row["pi_high"]):.1f}" stroke="var(--accent)" stroke-width="3"><title>prediction interval</title></line>')
        parts.append(f'<circle cx="{X(168):.1f}" cy="{Y(pred):.1f}" r="4" fill="var(--card)" stroke="var(--accent)" stroke-width="2"><title>predicted 168 h</title></circle>')
    parts.append(f'<polyline points="{X(0):.1f},{Y(row["value_0h"]):.1f} {X(24):.1f},{Y(row["value_24h"]):.1f}" fill="none" stroke="var(--ink)" stroke-width="2"/>')
    for t, key in ((0, "value_0h"), (24, "value_24h")):
        parts.append(f'<circle cx="{X(t):.1f}" cy="{Y(row[key]):.1f}" r="4" fill="var(--ink)"/>')
    if show_actual and not pd.isna(row.get("value_168h", float("nan"))):
        parts.append(f'<rect x="{X(168) - 4:.1f}" y="{Y(row["value_168h"]) - 4:.1f}" width="8" height="8" fill="none" stroke="var(--pass)" stroke-width="2"><title>actual 168 h (revealed after the decision; evaluation only)</title></rect>')
    parts.append("</svg>")
    return "".join(parts)


def card(row: pd.Series, coverage: float | None, category: str, show_actual: bool, note: str = "") -> str:
    ex = explain_row(row, coverage, category)
    items = "".join(f"<li>{_esc(line)}</li>" for line in ex["lines"])
    if show_actual and "value_168h" in row and not pd.isna(row["value_168h"]):
        items += f"<li class='muted'>Actual 168 h (revealed later, evaluation only): {row['value_168h']:.4g} {_esc(row.get('unit', ''))}</li>"
    note_html = f"<p class='muted'>{_esc(note)}</p>" if note else ""
    return (f"<div class='card'><div><h3 class='{_esc(row['decision'])}'>{_esc(ex['headline'])}</h3>{note_html}<ul>{items}</ul></div>"
            f"<div>{trajectory_svg(row, show_actual)}</div></div>")


def render_report(
    screened: pd.DataFrame,
    *,
    title: str,
    category: str,
    coverage: float | None,
    pipeline_note: str,
    show_actual: bool = False,
    featured: list[tuple[pd.Series, str]] | None = None,
    evidence_html: str = "",
    max_cards: int = 60,
) -> str:
    counts = screened["decision"].value_counts()
    tiles = "".join(
        f"<div class='tile'><span class='muted'>{d}</span><b class='{d}'>{int(counts.get(d, 0))}</b>"
        f"<span class='muted'>{counts.get(d, 0) / max(len(screened), 1):.1%} of rows</span></div>"
        for d in ("PASS", "REVIEW", "REJECT")
    )
    lots = screened.groupby(["lot_id", "parameter"])["decision"].value_counts().unstack(fill_value=0)
    lot_rows = "".join(
        f"<tr><td>{_esc(l)}</td><td>{_esc(p)}</td>" + "".join(f"<td>{int(r.get(d, 0))}</td>" for d in ("PASS", "REVIEW", "REJECT")) + "</tr>"
        for (l, p), r in lots.iterrows()
    )
    flagged = screened[screened["decision"] != "PASS"].copy()
    order = {"REJECT": 0, "REVIEW": 1}
    flagged["_o"] = flagged["decision"].map(order)
    flagged = flagged.sort_values(["_o", "lot_id", "component_id", "parameter"])
    cards = "".join(card(r, coverage, category, show_actual) for _, r in flagged.head(max_cards).iterrows())
    more = f"<p class='muted'>{len(flagged) - max_cards} more flagged rows are in the decisions CSV.</p>" if len(flagged) > max_cards else ""
    feat = ""
    if featured is not None:
        feat = "<h2>Featured examples (selected by a documented rule, not hand-made)</h2>" + (
            "".join(card(r, coverage, category, show_actual, note) for r, note in featured)
            if featured else "<p>No row met the featured-example rule in this data.</p>"
        )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgniDrishti screening report</title><style>{CSS}</style></head><body>
<div class="banner">DATA CATEGORY: {_esc(category.upper())} — {'not official SIH/ISRO data' if category != 'official' else 'official data'}</div>
<main><h1>{_esc(title)}</h1><p class="muted">{_esc(pipeline_note)}</p>
<div class="grid">{tiles}</div>
{feat}
{evidence_html}
<h2>Decisions by lot and parameter</h2><div class="wrap"><table><tr><th>Lot</th><th>Parameter</th><th>PASS</th><th>REVIEW</th><th>REJECT</th></tr>{lot_rows}</table></div>
<h2>Flagged rows — evidence cards</h2>{cards}{more}
<p class="muted">Robust z is a distance in robust-sigma units, not a probability. The prediction interval targets marginal coverage across parts and is not a probability of failure. REVIEW means an engineer decides.</p>
</main></body></html>"""
