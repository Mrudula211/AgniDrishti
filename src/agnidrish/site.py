"""Site configuration: everything that differs between organisations, in one file (ADR-007).

A site config (``configs/sites/<site>.yaml``) holds
- ``input``: how the tester export is laid out (an ingest profile, see ``agnidrish.ingest``);
- ``parameters``: the parameter registry — canonical name, aliases used by testers, unit,
  datasheet limits (or an explicit "no limit"), degradation direction;
- ``limits``: the precedence of specification-limit sources and an optional limits table
  (e.g. an export from a PLM / metadata system: parameter[, device_family], spec_min, spec_max[, unit]);
- ``calibration``: drift allowance and split settings used by ``agnidrish.fit``.

The detection, forecasting and decision layers never read this file; they only see the
canonical table produced from it. ``SiteConfig.to_dict`` is self-contained (the limits
table is inlined) so a run directory can store the exact configuration it used.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

LIMIT_SOURCES: tuple[str, ...] = ("manual", "file", "table", "registry")
DIRECTIONS: frozenset[str] = frozenset({"up", "down"})


class SiteConfigError(ValueError):
    """The site configuration is invalid."""


def _limit(value: Any) -> float:
    return float("nan") if value is None or (isinstance(value, float) and math.isnan(value)) else float(value)


@dataclass(frozen=True)
class ParameterConfig:
    """One registry entry. Limits are in ``unit``; NaN means no limit on that side."""

    name: str
    unit: str | None = None
    spec_min: float = float("nan")
    spec_max: float = float("nan")
    no_limit: bool = False  # engineering declaration: no datasheet limit applies to this parameter
    direction: str | None = None  # degradation direction, needed only to fit Module B
    aliases: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.direction is not None and self.direction not in DIRECTIONS:
            raise SiteConfigError(f"parameter {self.name}: direction must be 'up' or 'down', got {self.direction!r}")
        if self.no_limit and not (math.isnan(self.spec_min) and math.isnan(self.spec_max)):
            raise SiteConfigError(f"parameter {self.name}: no_limit contradicts spec_min/spec_max")
        if self.spec_min > self.spec_max:
            raise SiteConfigError(f"parameter {self.name}: spec_min > spec_max")

    @property
    def has_limit(self) -> bool:
        return not (math.isnan(self.spec_min) and math.isnan(self.spec_max))

    @staticmethod
    def from_dict(name: str, d: dict[str, Any]) -> ParameterConfig:
        unknown = set(d) - {"unit", "spec_min", "spec_max", "no_limit", "direction", "aliases"}
        if unknown:
            raise SiteConfigError(f"parameter {name}: unknown keys {sorted(unknown)}")
        return ParameterConfig(
            name=name,
            unit=d.get("unit"),
            spec_min=_limit(d.get("spec_min")),
            spec_max=_limit(d.get("spec_max")),
            no_limit=bool(d.get("no_limit", False)),
            direction=d.get("direction"),
            aliases=tuple(str(a) for a in d.get("aliases", ())),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit": self.unit,
            "spec_min": None if math.isnan(self.spec_min) else self.spec_min,
            "spec_max": None if math.isnan(self.spec_max) else self.spec_max,
            "no_limit": self.no_limit,
            "direction": self.direction,
            "aliases": list(self.aliases),
        }


@dataclass(frozen=True)
class SiteConfig:
    name: str
    input: dict[str, Any] = field(default_factory=dict)
    parameters: dict[str, ParameterConfig] = field(default_factory=dict)
    limit_sources: tuple[str, ...] = LIMIT_SOURCES
    limits_table: tuple[dict[str, Any], ...] = ()
    calibration: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        bad = [s for s in self.limit_sources if s not in LIMIT_SOURCES]
        if bad or len(set(self.limit_sources)) != len(self.limit_sources):
            raise SiteConfigError(f"limits.sources must be distinct values from {LIMIT_SOURCES}, got {list(self.limit_sources)}")
        seen: dict[str, str] = {}
        for p in self.parameters.values():
            for alias in (p.name, *p.aliases):
                key = alias_key(alias)
                if seen.get(key, p.name) != p.name:
                    raise SiteConfigError(f"alias {alias!r} is used by both {seen[key]} and {p.name}")
                seen[key] = p.name

    @staticmethod
    def from_dict(d: dict[str, Any]) -> SiteConfig:
        limits = d.get("limits") or {}
        return SiteConfig(
            name=str(d.get("site", "unnamed-site")),
            input=dict(d.get("input") or {}),
            parameters={str(n): ParameterConfig.from_dict(str(n), v or {}) for n, v in (d.get("parameters") or {}).items()},
            limit_sources=tuple(limits.get("sources", LIMIT_SOURCES)),
            limits_table=tuple(dict(r) for r in limits.get("table_rows", ())),
            calibration=dict(d.get("calibration") or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "site": self.name,
            "input": self.input,
            "parameters": {n: p.to_dict() for n, p in self.parameters.items()},
            "limits": {"sources": list(self.limit_sources), "table_rows": [dict(r) for r in self.limits_table]},
            "calibration": self.calibration,
        }

    def alias_map(self) -> dict[str, str]:
        """alias_key(tester name) -> registry name, for every registered name and alias."""
        return {alias_key(a): p.name for p in self.parameters.values() for a in (p.name, *p.aliases)}


def alias_key(name: str) -> str:
    """'I_DDQ', 'iddq', 'IDDQ ' -> 'iddq'."""
    return "".join(ch for ch in str(name).lower() if ch.isalnum())


def load_limits_table(path: Path) -> list[dict[str, Any]]:
    """Read a limits CSV: parameter, spec_min, spec_max, optional device_family and unit."""
    table = pd.read_csv(path, dtype={"parameter": str, "device_family": str, "unit": str}, encoding="utf-8-sig")
    missing = {"parameter", "spec_min", "spec_max"} - set(table.columns)
    if missing:
        raise SiteConfigError(f"limits table {path.name} lacks columns {sorted(missing)}")
    rows = []
    for r in table.to_dict(orient="records"):
        rows.append({
            "parameter": str(r["parameter"]).strip(),
            "device_family": None if pd.isna(r.get("device_family")) else str(r["device_family"]).strip(),
            "unit": None if pd.isna(r.get("unit")) else str(r["unit"]).strip(),
            "spec_min": None if pd.isna(r["spec_min"]) else float(r["spec_min"]),
            "spec_max": None if pd.isna(r["spec_max"]) else float(r["spec_max"]),
        })
    return rows


def load_site(path: Path, repo_root: Path) -> SiteConfig:
    """Load ``configs/sites/<site>.yaml``; a ``limits.table`` path (repo-relative) is read and inlined."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    limits = dict(raw.get("limits") or {})
    table = limits.pop("table", None)
    if table:
        table_path = Path(table) if Path(table).is_absolute() else repo_root / table
        limits["table_rows"] = load_limits_table(table_path)
    raw["limits"] = limits
    return SiteConfig.from_dict(raw)
