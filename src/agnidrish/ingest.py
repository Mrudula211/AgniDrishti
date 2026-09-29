"""Data adapter / normaliser: raw tester export -> canonical measurement table (FR-01, FR-22, ADR-007).

    raw export ──► layout adapter ──► measurements (one row per component · parameter · hour)
               ──► hour snapping, parameter aliases, unit conversion, duplicate policy
               ──► pivot to canonical (one row per component · parameter, value_<h>h columns)
               ──► specification limits from configured sources (with per-row provenance)

Supported layouts (``profile["layout"]``):

- ``row_per_parameter``   one row per component and parameter, one column per checkpoint
                          (e.g. ``value_0h, value_24h``; our canonical files use this layout)
- ``row_per_measurement`` one row per reading: component, lot, parameter, hour, value
- ``row_per_component``   one row per component, one column per parameter and checkpoint
                          (e.g. ``Iddq_0h, Iddq_24h, Tpd_0h, …``)

Nothing downstream depends on the layout. Problems that make a reading unusable are never
guessed away: the reading is blanked and the row carries an ``ingest_flags`` code, which the
quality gate turns into REVIEW.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from agnidrish.schema import DATA_CATEGORIES, EVALUATION_ONLY_COLUMNS, VALUE_COLUMNS, SchemaError
from agnidrish.site import SiteConfig, alias_key
from agnidrish.units import conversion_factor, normalise

LAYOUTS: tuple[str, ...] = ("row_per_parameter", "row_per_measurement", "row_per_component")
ID_ROLES: tuple[str, ...] = ("component_id", "lot_id")
ATTRIBUTE_ROLES: tuple[str, ...] = ("wafer_id", "device_family", "temperature_c", "nominal_value")
ROLES: tuple[str, ...] = ID_ROLES + ("parameter", "unit", "hour", "value", "spec_min", "spec_max") + ATTRIBUTE_ROLES
REQUIRED_ROLES: dict[str, tuple[str, ...]] = {
    "row_per_parameter": ("component_id", "lot_id", "parameter"),
    "row_per_measurement": ("component_id", "lot_id", "parameter", "hour", "value"),
    "row_per_component": ("component_id", "lot_id"),
}
DUPLICATE_POLICIES: tuple[str, ...] = ("review", "first", "last", "mean")
CHECKPOINT_HOURS: tuple[int, ...] = tuple(VALUE_COLUMNS)
# "<parameter>_24h", "Iddq 24 hrs", "IDDQ@168h" … and "<parameter>_T24".
HOUR_COLUMN_PATTERNS: tuple[str, ...] = (
    r"^(?P<parameter>.*?[A-Za-z0-9])[\s_@\-]*(?P<hour>\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours)$",
    r"^(?P<parameter>.*?[A-Za-z0-9])[\s_@\-]+[Tt](?P<hour>\d+(?:\.\d+)?)$",
)
SYNONYMS: dict[str, tuple[str, ...]] = {  # compared after alias_key(): lower-case, letters and digits only
    "component_id": ("componentid", "component", "compid", "serial", "serialno", "serialnumber", "sn", "deviceid",
                     "dut", "dutid", "partid", "partserial", "chipid", "dieid", "unitid", "uid"),
    "lot_id": ("lotid", "lot", "lotno", "lotnumber", "batch", "batchid", "batchno"),
    "wafer_id": ("waferid", "wafer", "waferno"),
    "device_family": ("devicefamily", "family", "parttype", "product", "partnumber", "device"),
    "parameter": ("parameter", "param", "parametername", "test", "testname", "measurement"),
    "unit": ("unit", "units", "uom"),
    "hour": ("hour", "hours", "timeh", "time", "readpoint", "checkpoint", "burninhours", "burninhour",
             "stresshours", "stresstime", "duration"),
    "value": ("value", "reading", "result", "measuredvalue", "meas", "val"),
    "spec_min": ("specmin", "lsl", "lowerlimit", "lowerspec", "minlimit", "lolimit", "lowlimit", "speclow", "ll"),
    "spec_max": ("specmax", "usl", "upperlimit", "upperspec", "maxlimit", "hilimit", "highlimit", "spechigh", "ul"),
    "temperature_c": ("temperaturec", "temperature", "temp", "tempc"),
    "nominal_value": ("nominalvalue", "nominal", "typical", "typ"),
}


class IngestFlag:
    """Codes written to ``ingest_flags``; the quality gate maps them to blocking component flags."""

    DUPLICATE_MEASUREMENT = "DUPLICATE_MEASUREMENT"
    UNIT_NOT_CONVERTIBLE = "UNIT_NOT_CONVERTIBLE"
    MIXED_UNITS = "MIXED_UNITS"
    NON_NUMERIC = "NON_NUMERIC"


@dataclass(frozen=True)
class InputProfile:
    """How one tester export is laid out. Column names not given default to the canonical names."""

    layout: str = "row_per_parameter"
    columns: dict[str, str] = field(default_factory=dict)  # role -> raw column
    hour_columns: dict[float, str] = field(default_factory=dict)  # row_per_parameter: hour -> raw column
    measurement_columns: dict[str, dict[float, str]] = field(default_factory=dict)  # row_per_component
    column_pattern: str | None = None  # regex with groups (?P<parameter>) and (?P<hour>)
    hour_tolerance_h: float = 2.0
    duplicates: str = "review"
    manual_limits: dict[str, dict[str, Any]] = field(default_factory=dict)  # parameter -> {spec_min, spec_max, unit}

    def __post_init__(self) -> None:
        if self.layout not in LAYOUTS:
            raise SchemaError(f"layout must be one of {LAYOUTS}, got {self.layout!r}")
        if self.duplicates not in DUPLICATE_POLICIES:
            raise SchemaError(f"duplicates must be one of {DUPLICATE_POLICIES}, got {self.duplicates!r}")
        bad = sorted(set(self.columns) - set(ROLES))
        if bad:
            raise SchemaError(f"unknown column roles {bad}; roles are {ROLES}")
        if self.hour_tolerance_h < 0:
            raise SchemaError("hour_tolerance_h must be >= 0")
        if self.column_pattern is not None:
            groups = re.compile(self.column_pattern).groupindex
            if not {"parameter", "hour"} <= set(groups):
                raise SchemaError("column_pattern needs named groups (?P<parameter>…) and (?P<hour>…)")

    @staticmethod
    def from_dict(d: Mapping[str, Any] | None) -> InputProfile:
        d = dict(d or {})
        unknown = set(d) - {"layout", "columns", "hour_columns", "measurement_columns", "column_pattern",
                            "hour_tolerance_h", "duplicates", "manual_limits"}
        if unknown:
            raise SchemaError(f"unknown input profile keys {sorted(unknown)}")
        return InputProfile(
            layout=d.get("layout", "row_per_parameter"),
            columns={str(k): str(v) for k, v in (d.get("columns") or {}).items() if v},
            hour_columns={float(h): str(c) for h, c in (d.get("hour_columns") or {}).items()},
            measurement_columns={str(p): {float(h): str(c) for h, c in cols.items()}
                                 for p, cols in (d.get("measurement_columns") or {}).items()},
            column_pattern=d.get("column_pattern"),
            hour_tolerance_h=float(d.get("hour_tolerance_h", 2.0)),
            duplicates=d.get("duplicates", "review"),
            manual_limits={str(p): dict(v) for p, v in (d.get("manual_limits") or {}).items()},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "layout": self.layout,
            "columns": self.columns,
            "hour_columns": {_hour_key(h): c for h, c in self.hour_columns.items()},
            "measurement_columns": {p: {_hour_key(h): c for h, c in cols.items()} for p, cols in self.measurement_columns.items()},
            "column_pattern": self.column_pattern,
            "hour_tolerance_h": self.hour_tolerance_h,
            "duplicates": self.duplicates,
            "manual_limits": self.manual_limits,
        }


@dataclass
class IngestReport:
    layout: str
    rows_in: int
    measurements: int = 0
    rows_out: int = 0
    ignored_hours: dict[str, int] = field(default_factory=dict)
    duplicates: int = 0
    non_numeric: int = 0
    unit_conversions: dict[str, str] = field(default_factory=dict)
    unit_not_convertible: int = 0
    aliased_parameters: dict[str, str] = field(default_factory=dict)
    unregistered_parameters: list[str] = field(default_factory=list)
    limit_sources: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def _hour_key(h: float) -> int | float:
    return int(h) if float(h).is_integer() else h


# ---------------------------------------------------------------- column detection


def match_hour_column(name: str, pattern: str | None = None) -> tuple[str, float] | None:
    """(parameter part, hour) if ``name`` looks like a per-checkpoint column, e.g. 'Iddq_24h' -> ('Iddq', 24.0)."""
    for p in (pattern,) if pattern else HOUR_COLUMN_PATTERNS:
        m = re.match(p, str(name).strip(), flags=re.IGNORECASE)
        if m:
            return m.group("parameter").strip(" _-@"), float(m.group("hour"))
    return None


def guess_roles(columns: Iterable[str]) -> dict[str, str]:
    """Role -> column by known synonyms (each column used once, first synonym wins)."""
    keyed = {alias_key(c): c for c in columns}
    used: set[str] = set()
    roles: dict[str, str] = {}
    for role, names in SYNONYMS.items():
        for name in (alias_key(role), *names):
            col = keyed.get(name)
            if col is not None and col not in used:
                roles[role] = col
                used.add(col)
                break
    return roles


def looks_headerless(columns: Iterable[str]) -> bool:
    """True when every header parses as a number — the file has no header row."""
    def is_num(s: str) -> bool:
        try:
            float(str(s).replace("E", "e"))
            return True
        except ValueError:
            return False
    cols = list(columns)
    return bool(cols) and all(is_num(c) for c in cols)


def suggest_profile(raw: pd.DataFrame, max_distinct: int = 200) -> dict[str, Any]:
    """Best-guess profile for an unseen export plus what was detected, for an engineer to confirm."""
    columns = [str(c) for c in raw.columns if c not in EVALUATION_ONLY_COLUMNS]
    if looks_headerless(columns):
        return {"headerless": True, "profile": None, "columns": columns,
                "message": "the first line holds numbers, not column names — add a header row"}
    roles = guess_roles(columns)
    hour_cols = {c: m for c in columns if c not in roles.values() and (m := match_hour_column(c))}
    groups: dict[str, dict[float, str]] = {}
    for col, (param, hour) in hour_cols.items():
        groups.setdefault(param, {})[hour] = col
    if {"hour", "value", "parameter"} <= set(roles):
        layout = "row_per_measurement"
    elif "parameter" in roles and groups:
        layout = "row_per_parameter"
    elif groups:
        layout = "row_per_component"
        roles.pop("parameter", None)
    else:
        layout = "row_per_measurement" if {"hour", "value"} <= set(roles) else "row_per_parameter"
    profile: dict[str, Any] = {"layout": layout, "columns": roles}
    if layout == "row_per_parameter" and groups:
        profile["hour_columns"] = {_hour_key(h): c for h, c in _pick_group(groups).items()}
    if layout == "row_per_component":
        profile["measurement_columns"] = {p: {_hour_key(h): c for h, c in hc.items()} for p, hc in groups.items()}
    distinct = {c: sorted(map(str, raw[c].dropna().unique()))[:max_distinct]
                for c in columns if raw[c].nunique(dropna=True) <= max_distinct}
    missing = [r for r in REQUIRED_ROLES[layout] if r not in roles]
    return {"headerless": False, "profile": profile, "columns": columns, "distinct": distinct,
            "missing_roles": missing, "hour_column_groups": {p: sorted(h) for p, h in groups.items()}}


def _pick_group(groups: dict[str, dict[float, str]]) -> dict[float, str]:
    """In row_per_parameter files the checkpoint columns share one prefix; prefer 'value', else the fullest group."""
    if "value" in {alias_key(g) for g in groups}:
        return next(v for g, v in groups.items() if alias_key(g) == "value")
    return max(groups.values(), key=len)


# ---------------------------------------------------------------- layout adapters -> measurements


def _column(raw: pd.DataFrame, profile: InputProfile, role: str) -> str | None:
    col = profile.columns.get(role, role)
    return col if col in raw.columns else None


def _require(raw: pd.DataFrame, profile: InputProfile) -> dict[str, str]:
    cols = {r: c for r in ROLES if (c := _column(raw, profile, r)) is not None}
    missing = [r for r in REQUIRED_ROLES[profile.layout] if r not in cols]
    if missing:
        hint = " (the file has no header row)" if looks_headerless(raw.columns) else ""
        raise SchemaError(
            f"layout {profile.layout}: no column for {missing}{hint}. File columns: {[str(c) for c in raw.columns[:12]]}. "
            "Map them in the input profile (columns: {role: column name})."
        )
    return cols


def _measurements(raw: pd.DataFrame, profile: InputProfile) -> pd.DataFrame:
    """Long form: one row per reading with canonical role names plus 'hour' and 'value'."""
    cols = _require(raw, profile)
    carried = [r for r in ("component_id", "lot_id", "parameter", "unit", "spec_min", "spec_max", *ATTRIBUTE_ROLES) if r in cols]
    base = pd.DataFrame({r: raw[cols[r]] for r in carried}, index=raw.index)
    base["_row"] = np.arange(len(raw))
    if profile.layout == "row_per_measurement":
        return base.assign(hour=parse_hours(raw[cols["hour"]]), value=raw[cols["value"]].to_numpy())
    if profile.layout == "row_per_parameter":
        hour_columns = profile.hour_columns or _detect_hour_columns(raw, cols, profile.column_pattern)
        return _melt(base, raw, {None: hour_columns})
    measurement_columns = profile.measurement_columns or _detect_measurement_columns(raw, cols, profile.column_pattern)
    return _melt(base, raw, measurement_columns)


def _detect_hour_columns(raw: pd.DataFrame, cols: dict[str, str], pattern: str | None) -> dict[float, str]:
    groups: dict[str, dict[float, str]] = {}
    for c in raw.columns:
        if c in cols.values() or c in EVALUATION_ONLY_COLUMNS:
            continue
        if m := match_hour_column(c, pattern):
            groups.setdefault(m[0], {})[m[1]] = str(c)
    if not groups:
        raise SchemaError("no checkpoint columns found (e.g. value_0h, value_24h); set hour_columns in the input profile")
    return _pick_group(groups)


def _detect_measurement_columns(raw: pd.DataFrame, cols: dict[str, str], pattern: str | None) -> dict[str, dict[float, str]]:
    groups: dict[str, dict[float, str]] = {}
    for c in raw.columns:
        if c in cols.values() or c in EVALUATION_ONLY_COLUMNS:
            continue
        if m := match_hour_column(c, pattern):
            groups.setdefault(m[0], {})[m[1]] = str(c)
    if not groups:
        raise SchemaError("no <parameter>_<hour>h columns found; set measurement_columns in the input profile")
    return groups


def _melt(base: pd.DataFrame, raw: pd.DataFrame, columns: Mapping[str | None, Mapping[float, str]]) -> pd.DataFrame:
    parts = []
    for parameter, hours in columns.items():
        for hour, col in hours.items():
            if col not in raw.columns:
                raise SchemaError(f"column {col!r} named in the input profile is not in the file")
            part = base.assign(hour=float(hour), value=raw[col].to_numpy())
            if parameter is not None:
                part["parameter"] = parameter
            parts.append(part)
    return pd.concat(parts, ignore_index=True)


def parse_hours(values: pd.Series) -> pd.Series:
    """Numeric hours from '24', '24h', 'T24', '24 hrs'; NaN when no number is present."""
    numeric = pd.to_numeric(values, errors="coerce")
    text = values.astype(str).str.extract(r"(\d+(?:\.\d+)?)", expand=False)
    return numeric.fillna(pd.to_numeric(text, errors="coerce")).astype(float)


# ---------------------------------------------------------------- normalise


def normalize(
    raw: pd.DataFrame,
    profile: InputProfile,
    site: SiteConfig,
    *,
    data_category: str,
    dataset_version: str,
    keep: tuple[str, ...] = (),
) -> tuple[pd.DataFrame, IngestReport]:
    """Canonical table (one row per lot · component · parameter) and a report of every change made.

    ``keep`` names extra raw columns carried through unchanged (e.g. ``split`` when fitting).

    Raises:
        SchemaError: invalid category, a required column role is missing, or the profile names absent columns.
    """
    if data_category not in DATA_CATEGORIES:
        raise SchemaError(f"data_category must be one of {sorted(DATA_CATEGORIES)}, got {data_category!r}")
    report = IngestReport(layout=profile.layout, rows_in=len(raw))
    m = _measurements(raw.drop(columns=[c for c in raw.columns if c in EVALUATION_ONLY_COLUMNS and c not in keep]), profile)
    for k in keep:
        if k in raw.columns:
            m[k] = raw[k].to_numpy()[m["_row"].to_numpy()]
    for r in ("component_id", "lot_id", "parameter", "wafer_id", "device_family", "unit"):
        if r in m.columns:
            m[r] = m[r].where(m[r].isna(), m[r].astype(str).str.strip()).replace("", np.nan).astype(object)
    m["_flags"] = ""

    _snap_hours(m, profile.hour_tolerance_h, report)
    if m.empty:
        raise SchemaError(f"no readings at the checkpoints {list(CHECKPOINT_HOURS)} h (±{profile.hour_tolerance_h:g} h)")
    _alias_parameters(m, site, report)
    _numeric_values(m, report)
    _convert_units(m, site, report)
    table = _pivot(m, profile.duplicates, report, keep)
    _resolve_limits(table, profile, site, report)
    table["data_category"] = data_category
    table["dataset_version"] = dataset_version
    report.rows_out = len(table)
    report.measurements = len(m)
    return table, report


def _snap_hours(m: pd.DataFrame, tolerance: float, report: IngestReport) -> None:
    targets = np.array(CHECKPOINT_HOURS, dtype=float)
    hours = m["hour"].to_numpy(dtype=float)
    dist = np.abs(hours[:, None] - targets[None, :])
    dist = np.where(np.isnan(dist), np.inf, dist)  # unparseable hour -> never matches
    nearest = dist.argmin(axis=1)
    ok = dist.min(axis=1, initial=np.inf) <= tolerance
    dropped = m.loc[~ok, "hour"]
    if len(dropped):
        counts = dropped.astype(str).value_counts().to_dict()
        report.ignored_hours = {str(k): int(v) for k, v in counts.items()}
        report.warnings.append(
            f"{len(dropped)} readings at hours not within ±{tolerance:g} h of a checkpoint {list(CHECKPOINT_HOURS)} were ignored: "
            f"{dict(list(report.ignored_hours.items())[:6])}"
        )
    m.drop(index=m.index[~ok], inplace=True)
    m["checkpoint"] = targets[nearest[ok]].astype(int)


def _alias_parameters(m: pd.DataFrame, site: SiteConfig, report: IngestReport) -> None:
    aliases = site.alias_map()
    raw_names = m["parameter"]
    mapped = raw_names.map(lambda n: aliases.get(alias_key(n), n) if isinstance(n, str) else n)
    changed = raw_names.notna() & (mapped != raw_names)
    report.aliased_parameters = dict(sorted(set(zip(raw_names[changed], mapped[changed]))))
    m["parameter"] = mapped
    report.unregistered_parameters = sorted(set(mapped.dropna()) - set(site.parameters))


def _numeric_values(m: pd.DataFrame, report: IngestReport) -> None:
    for col in ("value", "spec_min", "spec_max", "temperature_c", "nominal_value"):
        if col not in m.columns:
            continue
        if m[col].dtype == object:  # blank cells in text exports are missing, not "non-numeric"
            m[col] = m[col].replace(r"^\s*$", np.nan, regex=True)
        numeric = pd.to_numeric(m[col], errors="coerce").astype(float)
        bad = m[col].notna() & ~np.isfinite(numeric)  # text, or ±inf
        if col == "value" and bad.any():
            report.non_numeric = int(bad.sum())
            _flag(m, bad, IngestFlag.NON_NUMERIC)
        m[col] = numeric.where(np.isfinite(numeric))


def _convert_units(m: pd.DataFrame, site: SiteConfig, report: IngestReport) -> None:
    """Express every reading (and file limits) in the registry unit of its parameter."""
    target = m["parameter"].map({n: p.unit for n, p in site.parameters.items() if p.unit})
    if "unit" not in m.columns:
        m["unit"] = target
        return
    m["unit"] = m["unit"].fillna(target)
    todo = target.notna() & m["unit"].notna() & (m["unit"].map(normalise) != target.map(normalise, na_action="ignore"))
    for (src, dst), idx in m[todo].groupby(["unit", target[todo]]).groups.items():
        factor = conversion_factor(src, dst)
        if factor is None:
            report.unit_not_convertible += len(idx)
            m.loc[idx, "value"] = np.nan
            _flag(m, m.index.isin(idx), IngestFlag.UNIT_NOT_CONVERTIBLE)
            continue
        for col in ("value", "spec_min", "spec_max", "nominal_value"):
            if col in m.columns:
                m.loc[idx, col] = m.loc[idx, col] * factor
        m.loc[idx, "unit"] = dst
        report.unit_conversions[f"{src}→{dst}"] = f"×{factor:g}"
    if report.unit_not_convertible:
        report.warnings.append(f"{report.unit_not_convertible} readings have a unit that cannot be converted to the registry unit; they go to REVIEW")


def _pivot(m: pd.DataFrame, policy: str, report: IngestReport, keep: tuple[str, ...]) -> pd.DataFrame:
    keys = ["lot_id", "component_id", "parameter"]
    ids = m[keys].astype(object).where(m[keys].notna(), "\x00missing")
    codes, _ = pd.MultiIndex.from_frame(ids).factorize()
    m["_k"] = codes
    counts = m.groupby(["_k", "checkpoint"])["value"].transform("size")
    dup = counts > 1
    report.duplicates = int(dup.sum())
    if dup.any():
        if policy == "review":
            m.loc[dup, "value"] = np.nan
            _flag(m, dup, IngestFlag.DUPLICATE_MEASUREMENT)
            report.warnings.append(f"{report.duplicates} readings share a component, parameter and checkpoint; those rows go to REVIEW (policy 'review')")
        else:
            report.warnings.append(f"{report.duplicates} repeated readings resolved with policy '{policy}'")
    # first/last/mean skip blanks, so 'first' means the first valid reading in file order.
    agg = {"review": "first", "first": "first", "last": "last", "mean": "mean"}[policy]
    values = m.groupby(["_k", "checkpoint"])["value"].agg(agg).unstack("checkpoint")
    values = values.reindex(index=range(codes.max() + 1), columns=list(CHECKPOINT_HOURS))
    values.columns = [VALUE_COLUMNS[h] for h in CHECKPOINT_HOURS]

    attrs = [c for c in (*keys, "unit", "spec_min", "spec_max", *ATTRIBUTE_ROLES, *keep) if c in m.columns]
    first = m.groupby("_k")[attrs].first()
    units = m.groupby("_k")["unit"].nunique()
    flags = m.groupby("_k")["_flags"].agg(lambda s: ";".join(sorted({f for v in s for f in v.split(";") if f})))
    mixed = units > 1
    if mixed.any():
        flags[mixed] = [";".join(filter(None, (f, IngestFlag.MIXED_UNITS))) for f in flags[mixed]]
        values.loc[mixed[mixed].index] = np.nan
    table = first.join(values).assign(ingest_flags=flags)
    for col in ("spec_min", "spec_max"):
        if col not in table.columns:
            table[col] = np.nan
    return table.reset_index(drop=True)


def _flag(m: pd.DataFrame, mask: pd.Series | np.ndarray, code: str) -> None:
    mask = np.asarray(mask, dtype=bool)
    m.loc[mask, "_flags"] = [";".join(filter(None, (f, code))) for f in m.loc[mask, "_flags"]]


# ---------------------------------------------------------------- specification limits


def _resolve_limits(table: pd.DataFrame, profile: InputProfile, site: SiteConfig, report: IngestReport) -> None:
    """Fill spec_min/spec_max from the first source (site order) that gives a limit; record ``spec_source``.

    A row takes both sides from one source, so a deliberately one-sided limit is never
    completed from another source. ``declared_none`` = the registry says no limit applies.
    """
    n = len(table)
    lo, hi = np.full(n, np.nan), np.full(n, np.nan)
    source = np.full(n, "none", dtype=object)
    done = np.zeros(n, dtype=bool)
    unit = table["unit"]
    file_lo, file_hi = table["spec_min"].to_numpy(float), table["spec_max"].to_numpy(float)
    for name in site.limit_sources:
        cand_lo, cand_hi, declared_none = _candidates(name, table, profile, site, unit, file_lo, file_hi)
        has = ~(np.isnan(cand_lo) & np.isnan(cand_hi)) | declared_none
        take = has & ~done
        lo[take], hi[take] = cand_lo[take], cand_hi[take]
        source[take] = np.where(declared_none[take], "declared_none", name)
        done |= take
    table["spec_min"], table["spec_max"], table["spec_source"] = lo, hi, source
    report.limit_sources = {str(k): int(v) for k, v in pd.Series(source).value_counts().items()}
    missing = sorted(set(table.loc[source == "none", "parameter"].dropna()))
    if missing:
        report.warnings.append(
            f"no specification limit from any configured source for parameters {missing}; their rows go to REVIEW "
            "(add limits to the site registry or limits table, enter them for this upload, or declare no_limit)"
        )


def _candidates(name, table, profile, site, unit, file_lo, file_hi):
    n = len(table)
    lo, hi, none = np.full(n, np.nan), np.full(n, np.nan), np.zeros(n, dtype=bool)
    params = table["parameter"]
    if name == "file":
        return file_lo, file_hi, none
    if name == "registry":
        for p, cfg in site.parameters.items():
            rows = (params == p).to_numpy()
            if cfg.no_limit:
                none |= rows
            lo[rows], hi[rows] = cfg.spec_min, cfg.spec_max
        return lo, hi, none
    if name == "manual":
        entries = [dict(r, parameter=p, device_family=None) for p, r in profile.manual_limits.items()]
    else:  # table
        entries = [dict(r) for r in site.limits_table]
    family = table["device_family"] if "device_family" in table.columns else pd.Series(np.nan, index=table.index)
    aliases = site.alias_map()
    # Generic rows first, family-specific rows second so they override.
    for r in sorted(entries, key=lambda r: r.get("device_family") is not None):
        rows = params == aliases.get(alias_key(r["parameter"]), r["parameter"])
        if r.get("device_family") is not None:
            rows &= family == r["device_family"]
        rows = rows.to_numpy()
        factor = np.ones(n)
        if r.get("unit"):
            f = unit.map(lambda u: conversion_factor(r["unit"], u) if isinstance(u, str) else None)
            ok = f.notna().to_numpy()
            rows &= ok  # limits in a unit that cannot be converted are not applied
            factor = f.fillna(1.0).to_numpy(float)
        lo[rows] = _limit(r.get("spec_min")) * factor[rows]
        hi[rows] = _limit(r.get("spec_max")) * factor[rows]
    return lo, hi, none


def _limit(v: Any) -> float:
    return float("nan") if v is None or v == "" or (isinstance(v, float) and math.isnan(v)) else float(v)
