"""SI-prefix unit conversion for measurement values (ADR-007). No physics, only prefix scaling.

Two units convert when they share a base unit and differ only in SI prefix
(``nA`` -> ``uA``: x 1e-3). Anything else is not converted; the caller must
treat the value as unusable rather than guess.
"""

from __future__ import annotations

PREFIXES: dict[str, float] = {"f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "": 1.0, "k": 1e3, "M": 1e6, "G": 1e9}
BASES: frozenset[str] = frozenset({"A", "V", "s", "Ohm", "W", "Hz", "F", "H", "S", "C", "%", "dB", "degC"})
_SPELLINGS: dict[str, str] = {"µ": "u", "μ": "u", "Ω": "Ohm", "ohm": "Ohm", "ohms": "Ohm", "sec": "s", "°C": "degC"}


def normalise(unit: str) -> str:
    """Canonical spelling: 'µA' -> 'uA', 'kΩ' -> 'kOhm'. Case is kept (m and M differ)."""
    u = str(unit).strip()
    for old, new in _SPELLINGS.items():
        u = u.replace(old, new)
    return u


def split_unit(unit: str) -> tuple[float, str] | None:
    """(prefix factor, base) or None when the unit is not a known base with an optional SI prefix."""
    u = normalise(unit)
    if u in BASES:
        return 1.0, u
    if len(u) > 1 and u[0] in PREFIXES and u[1:] in BASES:
        return PREFIXES[u[0]], u[1:]
    return None


def conversion_factor(from_unit: str, to_unit: str) -> float | None:
    """Multiply values in ``from_unit`` by this to express them in ``to_unit``; None if not convertible."""
    if normalise(from_unit) == normalise(to_unit):
        return 1.0
    a, b = split_unit(from_unit), split_unit(to_unit)
    if a is None or b is None or a[1] != b[1]:
        return None
    return a[0] / b[0]
