import unittest
from decimal import Decimal

from pricing import apply_discount, compute_tax


class DiscountTests(unittest.TestCase):
    def test_no_code(self):
        self.assertEqual(apply_discount("100"), Decimal("100.00"))

    def test_code_case_insensitive(self):
        self.assertEqual(apply_discount("100", "welcome10"), Decimal("90.00"))

    def test_unknown_code(self):
        with self.assertRaises(ValueError):
            apply_discount("100", "BOGUS")


class TaxTests(unittest.TestCase):
    def test_germany(self):
        self.assertEqual(compute_tax("100", "DE"), Decimal("19.00"))

    def test_lowercase_region(self):
        self.assertEqual(compute_tax("10", "fr"), Decimal("2.00"))

    def test_unsupported_region(self):
        with self.assertRaises(ValueError):
            compute_tax("10", "XX")
