import unittest

from cart import Cart
from receipt import render_receipt


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.cart = Cart()
        self.cart.add_item("bread", "2.25")
        self.cart.add_item("apple", "0.50", 4)

    def test_receipt_without_discount(self):
        # 4.25 subtotal -> 19% tax 0.81 (half-up) -> total 5.06
        expected = "\n".join([
            "apple      x4   2.00 EUR",
            "bread      x1   2.25 EUR",
            "Subtotal       4.25 EUR",
            "Tax (DE)       0.81 EUR",
            "Total          5.06 EUR",
        ])
        self.assertEqual(render_receipt(self.cart, "DE"), expected)

    def test_receipt_with_discount(self):
        # 4.25 -> 10% off = 3.83 (half-up), discount 0.42 -> 19% tax 0.73 -> total 4.56
        expected = "\n".join([
            "apple      x4   2.00 EUR",
            "bread      x1   2.25 EUR",
            "Subtotal       4.25 EUR",
            "Discount       -0.42 EUR",
            "Tax (DE)       0.73 EUR",
            "Total          4.56 EUR",
        ])
        self.assertEqual(render_receipt(self.cart, "DE", "WELCOME10"), expected)

    def test_items_sorted_by_sku(self):
        lines = render_receipt(self.cart, "US").splitlines()
        self.assertTrue(lines[0].startswith("apple"))
        self.assertTrue(lines[1].startswith("bread"))

    def test_region_label_uppercased(self):
        self.assertIn("Tax (FR)", render_receipt(self.cart, "fr"))

    def test_no_discount_line_without_code(self):
        self.assertNotIn("Discount", render_receipt(self.cart, "DE"))

    def test_empty_cart(self):
        expected = "\n".join([
            "Subtotal       0.00 EUR",
            "Tax (US)       0.00 EUR",
            "Total          0.00 EUR",
        ])
        self.assertEqual(render_receipt(Cart(), "US"), expected)

    def test_unknown_discount_code(self):
        with self.assertRaises(ValueError):
            render_receipt(self.cart, "DE", "BOGUS")

    def test_unsupported_region(self):
        with self.assertRaises(ValueError):
            render_receipt(self.cart, "XX")
