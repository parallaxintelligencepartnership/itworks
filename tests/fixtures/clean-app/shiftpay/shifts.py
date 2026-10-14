"""Shifts as pairs of timezone-aware datetimes."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, tzinfo
from typing import List
from zoneinfo import ZoneInfo

_ONE_MINUTE = timedelta(minutes=1)


def _is_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


@dataclass(frozen=True, eq=False)
class Shift:
    """A half-open interval [start, end) between two aware datetimes.

    Equality and hashing are by UTC instants, so the two occurrences of a
    repeated wall-clock hour are different and a UTC shift equals the same
    instants in any zone. If either datetime is naive the shift compares by
    its raw fields (it can never equal an aware shift).
    """

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.start, datetime):
            raise TypeError("start must be a datetime")
        if not isinstance(self.end, datetime):
            raise TypeError("end must be a datetime")

    def _key(self):
        if _is_aware(self.start) and _is_aware(self.end):
            return (
                "utc",
                self.start.astimezone(timezone.utc),
                self.end.astimezone(timezone.utc),
            )
        return ("raw", self.start, self.end)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shift):
            return NotImplemented
        return self._key() == other._key()

    def __hash__(self) -> int:
        return hash(self._key())

    def duration_minutes(self) -> int:
        """Elapsed (absolute) minutes between start and end, as an int.

        Raises ValueError for naive datetimes, end before start, or a
        duration that is not a whole number of minutes.
        """
        _validate(self)
        delta = self.end.astimezone(timezone.utc) - self.start.astimezone(timezone.utc)
        if delta % _ONE_MINUTE != timedelta(0):
            raise ValueError("shift duration must be a whole number of minutes")
        return delta // _ONE_MINUTE


def _validate(shift: Shift) -> None:
    if not isinstance(shift, Shift):
        raise TypeError("shift must be a Shift")
    if not _is_aware(shift.start) or not _is_aware(shift.end):
        raise ValueError("shift start and end must be timezone-aware")
    # Compare as UTC instants: same-tzinfo comparison would use wall time.
    if shift.end.astimezone(timezone.utc) < shift.start.astimezone(timezone.utc):
        raise ValueError("shift end must not be before start")


def _local_midnight_utc(day, tz: ZoneInfo) -> datetime:
    return datetime(day.year, day.month, day.day, tzinfo=tz).astimezone(timezone.utc)


def split_at_midnight(shift: Shift, tz: tzinfo) -> List[Shift]:
    """Split a shift on local-day boundaries in ``tz``.

    Returns one shift if it does not cross a local midnight (a shift ending
    exactly at midnight does not cross it), otherwise two shifts whose
    boundary is that midnight. Results are expressed in ``tz``. Raises
    ValueError if the shift would need more than two pieces, or if the
    local-day arithmetic runs past the datetime range (year 9999).
    """
    _validate(shift)
    if not isinstance(tz, ZoneInfo):
        raise TypeError("tz must be a zoneinfo.ZoneInfo")
    start = shift.start.astimezone(timezone.utc)
    end = shift.end.astimezone(timezone.utc)
    try:
        return _split(start, end, tz)
    except OverflowError:
        raise ValueError("shift is too close to the datetime range limit") from None


def _split(start: datetime, end: datetime, tz: ZoneInfo) -> List[Shift]:
    first_day = start.astimezone(tz).date()
    boundary = _local_midnight_utc(first_day + timedelta(days=1), tz)
    start_local = start.astimezone(tz)
    end_local = end.astimezone(tz)
    if end <= boundary:
        return [Shift(start_local, end_local)]
    limit = _local_midnight_utc(first_day + timedelta(days=2), tz)
    if end > limit:
        raise ValueError("shift spans more than two local days")
    boundary_local = boundary.astimezone(tz)
    return [Shift(start_local, boundary_local), Shift(boundary_local, end_local)]
