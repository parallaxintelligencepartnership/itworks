import unittest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from shiftpay import Shift, split_at_midnight

NY = ZoneInfo("America/New_York")
UTC = timezone.utc


def ny(*args):
    return datetime(*args, tzinfo=NY)


class DurationTests(unittest.TestCase):
    def test_simple(self):
        s = Shift(ny(2026, 6, 1, 9), ny(2026, 6, 1, 17, 30))
        self.assertEqual(s.duration_minutes(), 510)

    def test_zero_length(self):
        s = Shift(ny(2026, 6, 1, 9), ny(2026, 6, 1, 9))
        self.assertEqual(s.duration_minutes(), 0)

    def test_mixed_zones_use_instants(self):
        s = Shift(datetime(2026, 6, 1, 13, tzinfo=UTC), ny(2026, 6, 1, 10))
        self.assertEqual(s.duration_minutes(), 60)

    def test_naive_start_rejected(self):
        s = Shift(datetime(2026, 6, 1, 9), ny(2026, 6, 1, 10))
        with self.assertRaises(ValueError):
            s.duration_minutes()

    def test_naive_end_rejected(self):
        s = Shift(ny(2026, 6, 1, 9), datetime(2026, 6, 1, 10))
        with self.assertRaises(ValueError):
            s.duration_minutes()

    def test_end_before_start_rejected(self):
        s = Shift(ny(2026, 6, 1, 10), ny(2026, 6, 1, 9))
        with self.assertRaises(ValueError):
            s.duration_minutes()

    def test_sub_minute_rejected(self):
        s = Shift(ny(2026, 6, 1, 9), ny(2026, 6, 1, 9, 0, 30))
        with self.assertRaises(ValueError):
            s.duration_minutes()

    def test_non_datetime_rejected(self):
        with self.assertRaises(TypeError):
            Shift("2026-06-01", ny(2026, 6, 1, 9))
        with self.assertRaises(TypeError):
            Shift(ny(2026, 6, 1, 9), None)

    def test_spring_forward_day_is_23_hours(self):
        s = Shift(ny(2026, 3, 8), ny(2026, 3, 9))
        self.assertEqual(s.duration_minutes(), 23 * 60)

    def test_spring_forward_overnight(self):
        s = Shift(ny(2026, 3, 8, 1), ny(2026, 3, 8, 4))  # 02:00-03:00 skipped
        self.assertEqual(s.duration_minutes(), 120)

    def test_fall_back_day_is_25_hours(self):
        s = Shift(ny(2026, 11, 1), ny(2026, 11, 2))
        self.assertEqual(s.duration_minutes(), 25 * 60)

    def test_fall_back_repeated_hour(self):
        first = datetime(2026, 11, 1, 1, 30, tzinfo=NY, fold=0)
        second = datetime(2026, 11, 1, 1, 30, tzinfo=NY, fold=1)
        self.assertEqual(Shift(first, second).duration_minutes(), 60)


class SplitTests(unittest.TestCase):
    def assertInstants(self, parts, expected):
        got = [(p.start.astimezone(UTC), p.end.astimezone(UTC)) for p in parts]
        want = [(a.astimezone(UTC), b.astimezone(UTC)) for a, b in expected]
        self.assertEqual(got, want)

    def test_within_one_day(self):
        s = Shift(ny(2026, 6, 1, 9), ny(2026, 6, 1, 17))
        parts = split_at_midnight(s, NY)
        self.assertEqual(len(parts), 1)
        self.assertInstants(parts, [(s.start, s.end)])

    def test_crossing_midnight(self):
        s = Shift(ny(2026, 6, 1, 22), ny(2026, 6, 2, 6))
        parts = split_at_midnight(s, NY)
        self.assertInstants(
            parts,
            [(ny(2026, 6, 1, 22), ny(2026, 6, 2)), (ny(2026, 6, 2), ny(2026, 6, 2, 6))],
        )
        self.assertEqual([p.duration_minutes() for p in parts], [120, 360])

    def test_ends_exactly_at_midnight(self):
        s = Shift(ny(2026, 6, 1, 22), ny(2026, 6, 2))
        self.assertEqual(len(split_at_midnight(s, NY)), 1)

    def test_starts_exactly_at_midnight(self):
        s = Shift(ny(2026, 6, 2), ny(2026, 6, 2, 8))
        self.assertEqual(len(split_at_midnight(s, NY)), 1)

    def test_one_minute_past_midnight(self):
        s = Shift(ny(2026, 6, 1, 23, 59), ny(2026, 6, 2, 0, 1))
        parts = split_at_midnight(s, NY)
        self.assertEqual([p.duration_minutes() for p in parts], [1, 1])

    def test_full_local_day(self):
        s = Shift(ny(2026, 6, 1), ny(2026, 6, 2))
        self.assertEqual(len(split_at_midnight(s, NY)), 1)

    def test_zero_length_at_midnight(self):
        s = Shift(ny(2026, 6, 2), ny(2026, 6, 2))
        parts = split_at_midnight(s, NY)
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0].duration_minutes(), 0)

    def test_zero_length_midday(self):
        s = Shift(ny(2026, 6, 2, 12), ny(2026, 6, 2, 12))
        self.assertEqual(len(split_at_midnight(s, NY)), 1)

    def test_input_in_utc_split_in_local_time(self):
        # 03:00Z-09:00Z on 2026-06-02 is 23:00 EDT 06-01 to 05:00 EDT 06-02.
        s = Shift(datetime(2026, 6, 2, 3, tzinfo=UTC), datetime(2026, 6, 2, 9, tzinfo=UTC))
        parts = split_at_midnight(s, NY)
        self.assertEqual([p.duration_minutes() for p in parts], [60, 300])

    def test_results_expressed_in_tz(self):
        s = Shift(ny(2026, 6, 1, 22), ny(2026, 6, 2, 6))
        for p in split_at_midnight(s, NY):
            self.assertEqual(p.start.utcoffset(), timedelta(hours=-4))

    def test_spring_forward_overnight(self):
        s = Shift(ny(2026, 3, 7, 22), ny(2026, 3, 8, 6))
        parts = split_at_midnight(s, NY)
        self.assertEqual([p.duration_minutes() for p in parts], [120, 300])
        self.assertEqual(sum(p.duration_minutes() for p in parts), s.duration_minutes())

    def test_spring_forward_full_day_not_split(self):
        s = Shift(ny(2026, 3, 8), ny(2026, 3, 9))
        parts = split_at_midnight(s, NY)
        self.assertEqual([p.duration_minutes() for p in parts], [23 * 60])

    def test_fall_back_overnight(self):
        s = Shift(ny(2026, 10, 31, 22), ny(2026, 11, 1, 6))
        parts = split_at_midnight(s, NY)
        self.assertEqual([p.duration_minutes() for p in parts], [120, 420])
        self.assertEqual(sum(p.duration_minutes() for p in parts), s.duration_minutes())

    def test_fall_back_full_day_not_split(self):
        s = Shift(ny(2026, 11, 1), ny(2026, 11, 2))
        parts = split_at_midnight(s, NY)
        self.assertEqual([p.duration_minutes() for p in parts], [25 * 60])

    def test_fall_back_next_midnight(self):
        s = Shift(ny(2026, 11, 1, 20), ny(2026, 11, 2, 2))
        parts = split_at_midnight(s, NY)
        # 20:00 EST is 01:00Z+... EST day ends at 05:00Z on 11-02
        self.assertEqual([p.duration_minutes() for p in parts], [240, 120])

    def test_spans_three_local_days_rejected(self):
        s = Shift(ny(2026, 6, 1, 12), ny(2026, 6, 3, 12))
        with self.assertRaises(ValueError):
            split_at_midnight(s, NY)

    def test_exactly_two_full_days_after_start_midnight_ok(self):
        s = Shift(ny(2026, 6, 1, 12), ny(2026, 6, 3))
        self.assertEqual(len(split_at_midnight(s, NY)), 2)

    def test_naive_rejected(self):
        s = Shift(datetime(2026, 6, 1, 9), datetime(2026, 6, 1, 10))
        with self.assertRaises(ValueError):
            split_at_midnight(s, NY)

    def test_end_before_start_rejected(self):
        s = Shift(ny(2026, 6, 1, 10), ny(2026, 6, 1, 9))
        with self.assertRaises(ValueError):
            split_at_midnight(s, NY)

    def test_bad_shift_type(self):
        with self.assertRaises(TypeError):
            split_at_midnight((1, 2), NY)

    def test_bad_tz_type(self):
        s = Shift(ny(2026, 6, 1, 9), ny(2026, 6, 1, 10))
        with self.assertRaises(TypeError):
            split_at_midnight(s, "America/New_York")
        with self.assertRaises(TypeError):
            split_at_midnight(s, UTC)


if __name__ == "__main__":
    unittest.main()
