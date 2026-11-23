import unittest
from decimal import Decimal

from cart import Cart


class CartTests(unittest.TestCase):
    def setUp(self):
        self.cart = Cart()
        self.cart.add_item("apple", "0.50", 4)
        self.cart.add_item("bread", "2.25")

    def test_subtotal(self):
        self.assertEqual(self.cart.subtotal(), Decimal("4.25"))

    def test_add_same_sku_merges(self):
        self.cart.add_item("apple", "0.50", 2)
        self.assertEqual(self.cart.items["apple"].quantity, 6)

    def test_remove_partial_and_full(self):
        self.cart.remove_item("apple", 1)
        self.assertEqual(self.cart.items["apple"].quantity, 3)
        self.cart.remove_item("apple")
        self.assertNotIn("apple", self.cart.items)

    def test_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.cart.add_item("x", "1.00", 0)

    def test_total_with_discount_and_tax(self):
        # 4.25 -> 50% off = 2.13 (half-up) -> +19% tax 0.40 = 2.53
        self.assertEqual(self.cart.total("DE", "HALFOFF"), Decimal("2.53"))