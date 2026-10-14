"""Integer-only pay arithmetic. Money is whole cents."""

from typing import Tuple


def _require_int(name: str, value: object) -> int:
    # bool is an int subclass; reject it explicitly.
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int")
    if value < 0:
        raise ValueError(f"{name} must not be negative")
    return value


def gross_pay(minutes: int, rate_cents_per_hour: int) -> int:
    """Pay in cents for ``minutes`` at ``rate_cents_per_hour``, half up.

    Exact value is minutes * rate / 60; exactly half a cent rounds up.
    """
    minutes = _require_int("minutes", minutes)
    rate = _require_int("rate_cents_per_hour", rate_cents_per_hour)
    # floor(n/60 + 1/2) == (2n + 60) // 120 for integer n >= 0
    return (2 * minutes * rate + 60) // 120


def overtime_split(minutes: int, threshold_minutes: int = 2400) -> Tuple[int, int]:
    """Return (regular, overtime) minutes; overtime is minutes above threshold."""
    minutes = _require_int("minutes", minutes)
    threshold = _require_int("threshold_minutes", threshold_minutes)
    regular = min(minutes, threshold)
    return regular, minutes - regular
