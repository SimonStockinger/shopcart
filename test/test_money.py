import unittest
from decimal import Decimal

from currency import format_money, to_money


class MoneyTests(unittest.TestCase):
    def test_rounds_half_up(self):
        self.assertEqual(to_money("2.675"), Decimal("2.68"))

    def test_float_input(self):
        self.assertEqual(to_money(0.1 + 0.2), Decimal("0.30"))

    def test_format(self):
        self.assertEqual(format_money(5), "5.00 EUR")
        self.assertEqual(format_money("3.5", "USD"), "3.50 USD")
