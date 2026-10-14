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


class EqualityTests(unittest.TestCase):
    def test_fold_shifts_unequal(self):
        a = Shift(ny(2026, 11, 1, 1, 0), ny(2026, 11, 1, 1, 45))
        b = Shift(
            datetime(2026, 11, 1, 1, 0, tzinfo=NY, fold=1),
            datetime(2026, 11, 1, 1, 45, tzinfo=NY, fold=1),
        )
        self.assertNotEqual(a, b)
        self.assertEqual(len({a, b}), 2)

    def test_split_manufactured_fold_pair_unequal(self):
        a = split_at_midnight(
            Shift(datetime(2026, 11, 1, 5, tzinfo=UTC), datetime(2026, 11, 1, 5, 45, tzinfo=UTC)), NY)
        b = split_at_midnight(
            Shift(datetime(2026, 11, 1, 6, tzinfo=UTC), datetime(2026, 11, 1, 6, 45, tzinfo=UTC)), NY)
        self.assertNotEqual(a[0], b[0])
        self.assertEqual(len({a[0], b[0]}), 2)

    def test_same_instants_equal_across_zones(self):
        a = Shift(datetime(2026, 6, 1, 13, tzinfo=UTC), datetime(2026, 6, 1, 14, tzinfo=UTC))
        b = Shift(ny(2026, 6, 1, 9), ny(2026, 6, 1, 10))
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_not_equal_to_other_types(self):
        self.assertNotEqual(Shift(ny(2026, 6, 1, 9), ny(2026, 6, 1, 10)), (1, 2))

    def test_naive_compares_by_fields(self):
        n1 = Shift(datetime(2026, 6, 1, 9), datetime(2026, 6, 1, 10))
        n2 = Shift(datetime(2026, 6, 1, 9), datetime(2026, 6, 1, 10))
        self.assertEqual(n1, n2)
        self.assertEqual(hash(n1), hash(n2))
        self.assertNotEqual(n1, Shift(ny(2026, 6, 1, 9), ny(2026, 6, 1, 10)))


class EdgeTests(unittest.TestCase):
    def test_utc_entered_piece_start_equals_shift_start(self):
        s = Shift(datetime(2026, 11, 1, 5, 30, tzinfo=UTC), datetime(2026, 11, 1, 10, tzinfo=UTC))
        pieces = split_at_midnight(s, NY)
        self.assertEqual(pieces[0].start.astimezone(UTC), s.start)

    def test_year_9999_raises_value_error(self):
        s = Shift(datetime(9999, 12, 30, 12, tzinfo=UTC), datetime(9999, 12, 31, 2, tzinfo=UTC))
        with self.assertRaises(ValueError):
            split_at_midnight(s, ZoneInfo("Asia/Tokyo"))

    def test_ambiguous_wall_time_uses_fold_elapsed_time(self):
        start = ny(2026, 10, 31, 22)
        self.assertEqual(Shift(start, ny(2026, 11, 1, 1, 30)).duration_minutes(), 210)
        end = datetime(2026, 11, 1, 1, 30, tzinfo=NY, fold=1)
        self.assertEqual(Shift(start, end).duration_minutes(), 270)

    def test_nonexistent_wall_time_uses_fold_elapsed_time(self):
        start = ny(2026, 3, 8, 1)
        self.assertEqual(Shift(start, ny(2026, 3, 8, 2, 30)).duration_minutes(), 90)
        end = datetime(2026, 3, 8, 2, 30, tzinfo=NY, fold=1)
        self.assertEqual(Shift(start, end).duration_minutes(), 30)

    def test_split_fall_back_night_boundary_and_tz(self):
        s = Shift(ny(2026, 10, 31, 22), ny(2026, 11, 1, 6))
        pieces = split_at_midnight(s, NY)
        self.assertEqual(len(pieces), 2)
        boundary = datetime(2026, 11, 1, 4, tzinfo=UTC)
        self.assertEqual(pieces[0].end.astimezone(UTC), boundary)
        self.assertEqual(pieces[1].start.astimezone(UTC), boundary)
        self.assertEqual(pieces[0].start.astimezone(UTC), s.start.astimezone(UTC))
        self.assertEqual(pieces[1].end.astimezone(UTC), s.end.astimezone(UTC))
        for p in pieces:
            self.assertIs(p.start.tzinfo, NY)
            self.assertIs(p.end.tzinfo, NY)

    def test_first_piece_inside_repeated_hour_has_fold_1(self):
        s = Shift(datetime(2026, 11, 1, 6, tzinfo=UTC), datetime(2026, 11, 1, 7, tzinfo=UTC))
        pieces = split_at_midnight(s, NY)
        self.assertEqual(len(pieces), 1)
        self.assertEqual(pieces[0].start.fold, 1)
        self.assertEqual(pieces[0].start.astimezone(UTC), s.start)
        self.assertEqual(pieces[0].duration_minutes(), 60)

    def test_split_one_end_naive_rejected(self):
        for s in (
            Shift(datetime(2026, 6, 1, 9), ny(2026, 6, 1, 10)),
            Shift(ny(2026, 6, 1, 9), datetime(2026, 6, 1, 10)),
        ):
            with self.assertRaises(ValueError):
                split_at_midnight(s, NY)

    def test_one_microsecond_remainder_rejected(self):
        s = Shift(ny(2026, 6, 1, 9), ny(2026, 6, 1, 10) + timedelta(microseconds=1))
        with self.assertRaises(ValueError):
            s.duration_minutes()


if __name__ == "__main__":
    unittest.main()
