import unittest
from fractions import Fraction
from math import floor

from shiftpay import gross_pay, overtime_split


class GrossPayTests(unittest.TestCase):
    def test_whole_hour(self):
        self.assertEqual(gross_pay(60, 1500), 1500)

    def test_zero_minutes(self):
        self.assertEqual(gross_pay(0, 1500), 0)

    def test_zero_rate(self):
        self.assertEqual(gross_pay(600, 0), 0)

    def test_exact_half_cent_rounds_up(self):
        self.assertEqual(gross_pay(1, 30), 1)  # 0.5 cent
        self.assertEqual(gross_pay(3, 10), 1)  # 0.5 cent
        self.assertEqual(gross_pay(3, 30), 2)  # 1.5 cents

    def test_below_half_cent_rounds_down(self):
        self.assertEqual(gross_pay(1, 29), 0)  # 0.483 cent
        self.assertEqual(gross_pay(7, 10), 1)  # 1.166 cents

    def test_above_half_cent_rounds_up(self):
        self.assertEqual(gross_pay(1, 31), 1)  # 0.516 cent
        self.assertEqual(gross_pay(5, 1000), 83)  # 83.33 -> 83
        self.assertEqual(gross_pay(10, 1000), 167)  # 166.67 -> 167

    def test_large_values_are_exact(self):
        self.assertEqual(gross_pay(10**12, 10**6), 16666666666666667)  # 1e18/60 = ...666.67

    def test_negative_minutes(self):
        with self.assertRaises(ValueError):
            gross_pay(-1, 1500)

    def test_negative_rate(self):
        with self.assertRaises(ValueError):
            gross_pay(60, -1)

    def test_float_rejected(self):
        with self.assertRaises(TypeError):
            gross_pay(60.0, 1500)
        with self.assertRaises(TypeError):
            gross_pay(60, 15.0)

    def test_bool_rejected(self):
        with self.assertRaises(TypeError):
            gross_pay(True, 1500)
        with self.assertRaises(TypeError):
            gross_pay(60, False)

    def test_none_and_str_rejected(self):
        with self.assertRaises(TypeError):
            gross_pay(None, 1500)
        with self.assertRaises(TypeError):
            gross_pay(60, "1500")


class OvertimeSplitTests(unittest.TestCase):
    def test_below_threshold(self):
        self.assertEqual(overtime_split(2399), (2399, 0))

    def test_at_threshold(self):
        self.assertEqual(overtime_split(2400), (2400, 0))

    def test_one_over_threshold(self):
        self.assertEqual(overtime_split(2401), (2400, 1))

    def test_zero_minutes(self):
        self.assertEqual(overtime_split(0), (0, 0))

    def test_custom_threshold(self):
        self.assertEqual(overtime_split(500, 480), (480, 20))

    def test_zero_threshold(self):
        self.assertEqual(overtime_split(10, 0), (0, 10))

    def test_negative_minutes(self):
        with self.assertRaises(ValueError):
            overtime_split(-1)

    def test_negative_threshold(self):
        with self.assertRaises(ValueError):
            overtime_split(10, -1)

    def test_wrong_types(self):
        with self.assertRaises(TypeError):
            overtime_split(10.0)
        with self.assertRaises(TypeError):
            overtime_split(10, 2400.0)
        with self.assertRaises(TypeError):
            overtime_split(True)
        with self.assertRaises(TypeError):
            overtime_split("10")


class SweepTests(unittest.TestCase):
    def test_gross_pay_matches_exact_reference(self):
        for m in range(600):
            for r in range(400):
                want = floor(Fraction(m * r, 60) + Fraction(1, 2))
                self.assertEqual(gross_pay(m, r), want, (m, r))

    def test_overtime_split_invariants(self):
        for t in (0, 1, 60, 2400):
            for m in range(0, 5001):
                regular, overtime = overtime_split(m, t)
                self.assertEqual(regular + overtime, m, (m, t))
                self.assertLessEqual(regular, t, (m, t))
                self.assertEqual(regular, min(m, t), (m, t))
        for m in (0, 2399, 2400, 2401, 10000, 20000):
            regular, overtime = overtime_split(m)
            self.assertEqual(regular + overtime, m)
            self.assertLessEqual(regular, 2400)


if __name__ == "__main__":
    unittest.main()
