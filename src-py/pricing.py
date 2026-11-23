"""Discount and tax rules."""
from decimal import Decimal

from currency import to_money

#: Supported discount codes (upper case) mapped to the fraction taken off.
DISCOUNT_CODES = {
    "WELCOME10": Decimal("0.10"),
    "HALFOFF": Decimal("0.50"),
}

#: Supported tax regions (upper case) mapped to their tax rate.
TAX_RATES = {
    "DE": Decimal("0.19"),
    "FR": Decimal("0.20"),
    "US": Decimal("0.00"),
}


def apply_discount(subtotal, code: str | None = None) -> Decimal:
    """Return the subtotal after applying a discount code (case-insensitive).

    Args:
        subtotal: The amount to discount.
        code: A key of `DISCOUNT_CODES`, in any case. If empty or None, no
            discount is applied.

    Returns:
        The discounted amount, rounded to cents.

    Raises:
        ValueError: If `code` is not a known discount code.
    """
    subtotal = to_money(subtotal)
    if not code:
        return subtotal
    rate = DISCOUNT_CODES.get(code.upper())
    if rate is None:
        raise ValueError(f"Unknown discount code: {code}")
    return to_money(subtotal * (1 - rate))


def compute_tax(amount, region: str) -> Decimal:
    """Return the tax owed on `amount` for the given region.

    Args:
        amount: The taxable amount.
        region: A key of `TAX_RATES`, in any case.

    Returns:
        The tax amount (not the gross total), rounded to cents.

    Raises:
        ValueError: If `region` is not supported.
    """
    rate = TAX_RATES.get(region.upper())
    if rate is None:
        raise ValueError(f"Unsupported region: {region}")
    return to_money(to_money(amount) * rate)
