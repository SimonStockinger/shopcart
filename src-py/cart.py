"""Shopping cart model.

A `Cart` holds `LineItem`s keyed by SKU and computes subtotals and totals
using the discount and tax rules from `pricing`.
"""
from dataclasses import dataclass, field
from decimal import Decimal

from currency import to_money
from pricing import apply_discount, compute_tax


@dataclass
class LineItem:
    """A single product entry in a cart.

    Attributes:
        sku: Stock keeping unit identifying the product.
        unit_price: Price of one unit, rounded to cents.
        quantity: Number of units (always positive).
    """

    sku: str
    unit_price: Decimal
    quantity: int

    @property
    def line_total(self) -> Decimal:
        """Return `unit_price * quantity`, rounded to cents."""
        return to_money(self.unit_price * self.quantity)


@dataclass
class Cart:
    """A shopping cart.

    Attributes:
        items: Line items keyed by SKU. Each SKU appears at most once.
    """

    items: dict[str, LineItem] = field(default_factory=dict)

    def add_item(self, sku: str, unit_price, quantity: int = 1) -> None:
        """Add `quantity` units of a product to the cart.

        If the SKU is already in the cart, its quantity is increased and the
        originally stored unit price is kept.

        Args:
            sku: Product identifier.
            unit_price: Price per unit (int, float, str or Decimal).
            quantity: Number of units to add. Defaults to 1.

        Raises:
            ValueError: If `quantity` is not positive.
        """
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if sku in self.items:
            self.items[sku].quantity += quantity
        else:
            self.items[sku] = LineItem(sku, to_money(unit_price), quantity)

    def remove_item(self, sku: str, quantity: int | None = None) -> None:
        """Remove units of a product from the cart.

        Args:
            sku: Product identifier.
            quantity: Number of units to remove. If omitted, or if it is at
                least the quantity in the cart, the whole line item is removed.

        Raises:
            KeyError: If `sku` is not in the cart.
        """
        if sku not in self.items:
            raise KeyError(sku)
        if quantity is None or quantity >= self.items[sku].quantity:
            del self.items[sku]
        else:
            self.items[sku].quantity -= quantity

    def subtotal(self) -> Decimal:
        """Return the sum of all line totals, before discount and tax."""
        return to_money(sum((i.line_total for i in self.items.values()), Decimal("0")))

    def total(self, region: str, discount_code: str | None = None) -> Decimal:
        """Return the final amount to pay.

        The discount is applied to the subtotal first; tax is then computed on
        the discounted amount and added.

        Args:
            region: Tax region code (case-insensitive), e.g. "DE".
            discount_code: Optional discount code (case-insensitive).

        Raises:
            ValueError: If the region or discount code is unknown.
        """
        discounted = apply_discount(self.subtotal(), discount_code)
        return to_money(discounted + compute_tax(discounted, region))
